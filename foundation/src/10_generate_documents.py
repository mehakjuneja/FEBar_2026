# Databricks notebook source
# MAGIC %md
# MAGIC # F2 — Synthetic PO / GR / Invoice generator (Accord)
# MAGIC
# MAGIC Generates a **fully synthetic** accounts-payable dataset for *Maison Lumière* (fragrance
# MAGIC retailer) with **seeded, labeled** three-way-match discrepancies. The labels in `line_truth`
# MAGIC are the **ground truth** the Phase 1 match is scored against and the Phase 2 model trains on.
# MAGIC
# MAGIC Writes to `${catalog}.landing${suffix}`: `vendor_master`, `product`, `po_line`, `gr_line`,
# MAGIC `invoice_line`, `line_truth`. Reproducible (fixed seed). **No real data.**
# MAGIC
# MAGIC See `docs/superpowers/plans/2026-09-24-phase0-foundation.md` (Task F2).

# COMMAND ----------
# MAGIC %pip install faker
# MAGIC %restart_python

# COMMAND ----------
# MAGIC %md ## Parameters

# COMMAND ----------
dbutils.widgets.text("catalog", "accord_febar_catalog", "Catalog")
dbutils.widgets.text("schema_suffix", "", "Schema suffix")
dbutils.widgets.text("seed", "42", "Random seed")
dbutils.widgets.text("n_vendors", "25", "Vendors")
dbutils.widgets.text("n_products", "300", "SKUs")
dbutils.widgets.text("n_po_lines", "12000", "PO lines (≈ invoice lines)")

CATALOG = dbutils.widgets.get("catalog")
SUFFIX = dbutils.widgets.get("schema_suffix")
LANDING = f"{CATALOG}.landing{SUFFIX}"
SEED = int(dbutils.widgets.get("seed"))
N_VENDORS = int(dbutils.widgets.get("n_vendors"))
N_PRODUCTS = int(dbutils.widgets.get("n_products"))
N_PO_LINES = int(dbutils.widgets.get("n_po_lines"))

import random, datetime as dt
import numpy as np
import pandas as pd
from faker import Faker

random.seed(SEED); np.random.seed(SEED)
fake = Faker(); Faker.seed(SEED)
print(f"Target schema: {LANDING}  |  seed={SEED}  po_lines≈{N_PO_LINES}")

# COMMAND ----------
# MAGIC %md ## Config: tolerances + the labeled exception mix
# MAGIC Disposition/reason is decided FIRST per line, then values are constructed to realize it — so
# MAGIC `line_truth` is honest ground truth. Exception rates vary by vendor (some vendors are messy).

# COMMAND ----------
PRICE_TOL = 0.02   # 2% price variance tolerance (matches match_config default, spec D-1)

# Base mix across all lines (must sum to 1.0). ~70% clean.
BASE_MIX = {
    "MATCH_OK":        0.70,
    "PRICE_VAR":       0.09,
    "QTY_OVERBILL":    0.06,
    "NO_RECEIPT":      0.05,
    "NO_PO":           0.03,
    "DUP_INVOICE":     0.03,
    "VENDOR_MISMATCH": 0.02,
    "UOM_MISMATCH":    0.02,
}
REASONS = list(BASE_MIX.keys())
UOMS = ["EA", "BX", "CS", "ML"]

# COMMAND ----------
# MAGIC %md ## 1. vendor_master  (synthetic fragrance houses; each with an exception-propensity)

# COMMAND ----------
vendors = []
for i in range(1, N_VENDORS + 1):
    house = fake.company() + random.choice([" Parfums", " Fragrances", " Maison", " Atelier", " et Cie"])
    # per-vendor "messiness" multiplier -> some vendors generate more exceptions
    messy = float(np.clip(np.random.gamma(2.0, 0.5), 0.2, 3.0))
    vendors.append({
        "vendor_id": f"V{i:04d}",
        "vendor_name": house,
        "address": fake.address().replace("\n", ", "),
        "email": f"ap@{fake.domain_name()}",
        "remit_to": fake.iban(),               # synthetic bank-like id -> future UC column-mask target
        "payment_terms": random.choice(["NET30", "NET45", "NET60", "2/10 NET30"]),
        "messiness": round(messy, 3),
    })
vendors_pd = pd.DataFrame(vendors)
print(vendors_pd[["vendor_id", "vendor_name", "payment_terms", "messiness"]].head())

# COMMAND ----------
# MAGIC %md ## 2. product  (fragrance SKUs)

# COMMAND ----------
notes = ["Rose", "Oud", "Bergamot", "Vetiver", "Amber", "Jasmine", "Sandalwood", "Musk", "Neroli", "Iris"]
forms = ["EDP 50ml", "EDP 100ml", "EDT 50ml", "Parfum 30ml", "Tester 100ml", "Gift Set", "Travel 10ml"]
products = []
for i in range(1, N_PRODUCTS + 1):
    form = random.choice(forms)
    is_tester = "Tester" in form
    products.append({
        "product_no": f"SKU{i:05d}",
        "description": f"{random.choice(notes)} {random.choice(notes)} {form}",
        "uom": "EA" if "Set" not in form else "BX",
        "list_price": 0.0 if is_tester else round(float(np.random.uniform(28, 320)), 2),
        "is_tester": is_tester,
    })
products_pd = pd.DataFrame(products)
prod_by_no = products_pd.set_index("product_no").to_dict("index")
print(products_pd.head())

# COMMAND ----------
# MAGIC %md ## 3. Generate PO → GR → Invoice lines with a labeled disposition each

# COMMAND ----------
start = dt.date(2025, 3, 1)                 # ~18 months back from build date (2026-09)
def rand_date(base, max_days):
    return base + dt.timedelta(days=int(np.random.randint(0, max_days)))

def vendor_mix(messiness):
    """Scale non-clean reasons by vendor messiness; renormalize to 1.0."""
    m = dict(BASE_MIX)
    for r in REASONS:
        if r != "MATCH_OK":
            m[r] *= messiness
    tot = sum(m.values())
    return {r: v / tot for r, v in m.items()}

po_lines, gr_lines, invoice_lines, truth = [], [], [], []
po_counter, gr_counter, inv_counter = 0, 0, 0

# group lines into POs of 1–5 lines
remaining = N_PO_LINES
while remaining > 0:
    po_counter += 1
    po_id = f"PO{po_counter:06d}"
    v = vendors[random.randrange(N_VENDORS)]
    mix = vendor_mix(v["messiness"])
    po_date = rand_date(start, 520)
    n_lines = min(remaining, random.randint(1, 5))
    for ln in range(1, n_lines + 1):
        remaining -= 1
        prod = products[random.randrange(N_PRODUCTS)]
        product_no = prod["product_no"]
        uom = prod["uom"]
        qty = int(np.random.randint(1, 200))
        base_price = prod["list_price"] if prod["list_price"] > 0 else round(float(np.random.uniform(5, 40)), 2)
        # small legitimate price drift over time, still within tolerance
        po_price = round(base_price * float(np.random.uniform(0.99, 1.01)), 2)

        reason = np.random.choice(REASONS, p=[mix[r] for r in REASONS])

        # --- PO line (always exists unless NO_PO) ---
        has_po = reason != "NO_PO"
        if has_po:
            po_lines.append({
                "po_id": po_id, "po_line_no": ln, "vendor_id": v["vendor_id"],
                "product_no": product_no, "qty_ordered": qty, "unit_price": po_price,
                "uom": uom, "ship_to": fake.city(), "po_date": po_date,
            })

        # --- Goods receipt (skipped for NO_RECEIPT / NO_PO) ---
        qty_received = qty
        receipt_date = po_date + dt.timedelta(days=int(np.random.randint(2, 21)))
        has_gr = reason not in ("NO_RECEIPT", "NO_PO")
        if reason == "QTY_OVERBILL":
            qty_received = max(1, qty - int(np.random.randint(1, max(2, qty // 4))))
        if has_gr:
            gr_counter += 1
            gr_lines.append({
                "gr_id": f"GR{gr_counter:06d}", "gr_line_no": 1, "po_id": po_id,
                "product_no": product_no, "qty_received": qty_received,
                "condition": random.choice(["OK", "OK", "OK", "DAMAGED"]),
                "receipt_date": receipt_date,
            })

        # --- Invoice line: construct values to realize the labeled reason ---
        inv_counter += 1
        inv_id = f"INV{inv_counter:06d}"
        inv_no = f"{v['vendor_id']}-{fake.bothify('INV-#####')}"
        inv_price = po_price
        inv_qty = qty_received if has_gr else qty
        inv_uom = uom
        inv_remit = v["remit_to"]
        inv_po = po_id if has_po else f"PO{random.randint(900000, 999999):06d}"  # orphan for NO_PO

        if reason == "PRICE_VAR":
            inv_price = round(po_price * (1 + float(np.random.uniform(PRICE_TOL + 0.02, 0.25))), 2)
        elif reason == "QTY_OVERBILL":
            inv_qty = qty                       # bill the full order though less was received
        elif reason == "VENDOR_MISMATCH":
            inv_remit = fake.iban()             # remit-to that won't match the vendor master
        elif reason == "UOM_MISMATCH":
            inv_uom = random.choice([u for u in UOMS if u != uom])

        inv_date = (receipt_date if has_gr else po_date) + dt.timedelta(days=int(np.random.randint(1, 15)))
        rec = {
            "invoice_id": inv_id, "inv_line_no": 1, "vendor_id": v["vendor_id"],
            "po_id": inv_po, "product_no": product_no, "qty_billed": inv_qty,
            "unit_price": inv_price, "uom": inv_uom,
            "tax": round(inv_price * inv_qty * 0.0, 2), "remit_to": inv_remit,
            "invoice_no": inv_no, "invoice_date": inv_date,
        }
        invoice_lines.append(rec)
        truth.append({"invoice_id": inv_id, "inv_line_no": 1,
                      "true_disposition": "AUTO_APPROVE" if reason == "MATCH_OK" else "HOLD",
                      "true_reason": reason, "note": f"vendor {v['vendor_id']} messiness {v['messiness']}"})

        # --- DUP_INVOICE: emit a near-identical duplicate line, also labeled ---
        if reason == "DUP_INVOICE":
            inv_counter += 1
            dup_id = f"INV{inv_counter:06d}"
            dup = dict(rec); dup["invoice_id"] = dup_id   # same invoice_no + amount, new line id
            invoice_lines.append(dup)
            truth.append({"invoice_id": dup_id, "inv_line_no": 1, "true_disposition": "HOLD",
                          "true_reason": "DUP_INVOICE", "note": f"duplicate of {inv_id}"})

print(f"PO lines={len(po_lines)}  GR lines={len(gr_lines)}  Invoice lines={len(invoice_lines)}")

# COMMAND ----------
# MAGIC %md ## 4. Write Delta tables to landing

# COMMAND ----------
def write(pdf, name):
    (spark.createDataFrame(pdf)
        .write.mode("overwrite").option("overwriteSchema", "true")
        .saveAsTable(f"{LANDING}.{name}"))
    print(f"  ✓ {LANDING}.{name}: {len(pdf)} rows")

write(vendors_pd.drop(columns=["messiness"]), "vendor_master")
write(products_pd, "product")
write(pd.DataFrame(po_lines), "po_line")
write(pd.DataFrame(gr_lines), "gr_line")
write(pd.DataFrame(invoice_lines), "invoice_line")
write(pd.DataFrame(truth), "line_truth")

# COMMAND ----------
# MAGIC %md ## 5. Verify — disposition / reason distribution (ground truth)

# COMMAND ----------
display(spark.sql(f"""
  SELECT true_reason, count(*) AS lines,
         round(100.0 * count(*) / sum(count(*)) OVER (), 1) AS pct
  FROM {LANDING}.line_truth GROUP BY true_reason ORDER BY lines DESC
"""))
print("Expect ~70% MATCH_OK; the rest spread across the taxonomy. Next: F3 (20_write_feeds.py).")
