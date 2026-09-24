# Accord — Phase 0: Foundation (F1–F3) — Implementation Plan

> **How to use this plan:** work it task-by-task; each task ends with **build → run → assert →
> commit**. Steps use `- [ ]` checkboxes. **Planning-only repo:** this plan gives the approach,
> schema, the Databricks Assistant prompt to generate from, and the verify step — **you write and
> own the code** (FE Bar integrity). Reference the design in
> [`../specs/2026-09-24-accord-3way-match-design.md`](../specs/2026-09-24-accord-3way-match-design.md).
>
> **Skills to load when building this phase:** `databricks-core` (auth/profile/CLI) → then
> `databricks-unity-catalog` (F1), `databricks-synthetic-data-gen` **or**
> `fe-databricks-tools:databricks-data-generation` (F2), `databricks-dabs` (bundle wiring).

**Goal:** Stand up the governed home for Accord and generate a **realistic, fully synthetic**
dataset of Purchase Orders, Goods Receipts, and Invoices whose discrepancies are **seeded and
labeled** — so the 3-way match (Phase 1) has something to catch and the ML model (Phase 2) has
honest ground truth.

**Architecture:** UC catalog + medallion schemas + a landing volume. A data generator produces
linked PO/GR/Invoice line items for N suppliers over a date range, deliberately injecting a known
mix of exceptions (price variance, overbill, missing receipt, no PO, duplicate, vendor/UOM
mismatch). Feeds are written to the landing volume as files, mimicking ERP/EDI extracts, ready for
Auto Loader in Phase 1.

**Tech stack:** Unity Catalog, Volumes, Delta; Python (Polars + Mimesis / Faker or `dbldatagen`);
serverless notebooks; DAB.

## Global constraints

- **Fully synthetic, customer-safe.** No real vendors, SKUs, or bank data. Any remit-to / bank-like
  field is fake and flagged as the future UC-mask target. (FE Bar scanner blocks secrets.)
- **Parameterized, portable.** Every notebook reads `dbutils.widgets.get("catalog")` and
  `get("schema_suffix")`. **No hardcoded catalog/host/profile literals.**
- **Profile:** operator-chosen; pass `--profile <name>`. **Never auto-select.**
- **Serverless** compute unless stated.
- **Seed the RNG** so regeneration is reproducible and the disposition mix is stable.
- **Naming** per spec §4: catalog `febar_accord_dev`, schemas `landing_dev`/`bronze_dev`/…,
  volume `/Volumes/${catalog}/landing${suffix}/feeds/`.

---

## Task F1: Unity Catalog setup

**Scenarios:** governed home for all Accord objects; the Product-domain governance story starts here.

**Files:**
- Create: `foundation/src/00_uc_setup.py` (notebook)
- Create: `foundation/resources/foundation.job.yml` (DAB job to run foundation end-to-end)

**Interfaces:**
- Produces: catalog `${catalog}`; schemas `landing${suffix}`, `bronze${suffix}`, `silver${suffix}`,
  `gold${suffix}`, `ml${suffix}`; volume `landing${suffix}` with dirs `feeds/po`, `feeds/gr`,
  `feeds/invoice`; baseline grants.

**Approach:**
- [ ] `CREATE CATALOG IF NOT EXISTS` + the five schemas + the managed volume.
- [ ] Create the `feeds/{po,gr,invoice}` directories in the volume.
- [ ] Grants: a read-only analyst group on `gold`; note the vendor-remit column as the future
      **column-mask** demo (implement the mask in Phase 1/governance walkthrough).

**Databricks Assistant prompt (generate, then review & own):**
```
Write a Databricks notebook that sets up Unity Catalog for a project. Read widgets "catalog"
(default febar_accord_dev) and "schema_suffix" (default _dev). Create the catalog if not exists,
then schemas landing<suffix>, bronze<suffix>, silver<suffix>, gold<suffix>, ml<suffix>. Create a
managed volume named landing<suffix> and, using dbutils.fs.mkdirs, create subdirectories
feeds/po, feeds/gr, feeds/invoice under the volume. Print each object created. Idempotent.
```

**Verify:**
```sql
SHOW SCHEMAS IN febar_accord_dev;              -- expect landing_dev, bronze_dev, silver_dev, gold_dev, ml_dev
LIST '/Volumes/febar_accord_dev/landing_dev/feeds';  -- expect po/ gr/ invoice/
```

---

## Task F2: Synthetic PO/GR/Invoice generator (seeded, labeled discrepancies)

**Scenarios:** the dataset that makes the match meaningful and gives ML honest labels.

**Files:**
- Create: `foundation/src/10_generate_documents.py` (notebook)

**Interfaces:**
- Produces (in `landing${suffix}` as Delta staging, before file export in F3): `po_line`,
  `gr_line`, `invoice_line`, `vendor_master`, and a `line_truth` table (the seeded disposition +
  reason per invoice line = ground truth).

**Data design:**
- **Suppliers/vendors:** ~25 fragrance-house vendors in `vendor_master` (vendor_id, name, address,
  email, remit_to, payment_terms). Names/addresses synthetic (Mimesis/Faker).
- **Catalog/SKUs:** ~300 fragrance SKUs (product_no, description, uom, list_price).
- **Volume/time:** ~18 months of activity; a few thousand POs → tens of thousands of line items,
  enough for trends by week/month/year (the app's summary page needs this granularity).
- **Linkage:** each PO line → 0..n GR lines (receipts) → 1 invoice line (mostly). This linkage is
  what the match reconstructs.
- **Seeded exception mix (labeled in `line_truth`):** target roughly — 70% `MATCH_OK`
  (→ AUTO_APPROVED), then a spread across `PRICE_VAR`, `QTY_OVERBILL`, `NO_RECEIPT`, `NO_PO`,
  `DUP_INVOICE`, `VENDOR_MISMATCH`, `UOM_MISMATCH`. Vary rates **by vendor** so the exceptions page
  and vendor-history feature have signal.
- **Realism knobs:** price drift over time, seasonal launch spikes, tester/GWP zero-price units,
  occasional partial receipts.

**Databricks Assistant prompt (generate, then review & own):**
```
Write a Databricks (Python) notebook that generates a synthetic accounts-payable dataset for a
fragrance retailer, for three-way match. Read widgets catalog/schema_suffix. Set a fixed random
seed. Produce Delta tables in landing<suffix>:
- vendor_master: ~25 fake fragrance-house vendors (vendor_id, name, address, email, remit_to,
  payment_terms) using Faker/Mimesis.
- product (~300 SKUs: product_no, description, uom, list_price).
- po_line (po_id, po_line_no, vendor_id, product_no, qty_ordered, unit_price, uom, ship_to,
  po_date) across ~18 months.
- gr_line (gr_id, gr_line_no, po_id, product_no, qty_received, condition, receipt_date) linked to
  PO lines; allow partial and missing receipts.
- invoice_line (invoice_id, inv_line_no, vendor_id, po_id, product_no, qty_billed, unit_price,
  uom, tax, remit_to, invoice_date, invoice_no) mostly linked to PO lines.
- line_truth (invoice_id, inv_line_no, true_disposition in {AUTO_APPROVE, HOLD}, true_reason in the
  exception taxonomy, note): deliberately inject a labeled mix — ~70% clean, the rest spread across
  PRICE_VAR, QTY_OVERBILL, NO_RECEIPT, NO_PO, DUP_INVOICE, VENDOR_MISMATCH, UOM_MISMATCH, with
  exception rates that vary by vendor.
Print row counts per table and the disposition/reason distribution. Everything must be synthetic.
```

**Verify:**
```sql
SELECT true_reason, count(*) FROM febar_accord_dev.landing_dev.line_truth GROUP BY 1 ORDER BY 2 DESC;
-- expect ~70% MATCH_OK, the rest spread across the taxonomy; rates differ by vendor
SELECT count(DISTINCT vendor_id) FROM febar_accord_dev.landing_dev.vendor_master;  -- ~25
SELECT count(*) FROM febar_accord_dev.landing_dev.invoice_line;                    -- tens of thousands
```

---

## Task F3: Landing feeds (write files to the volume)

**Scenarios:** make the data arrive the way an ERP/EDI extract would, so Phase 1 uses `read_files`.

**Files:**
- Create: `foundation/src/20_write_feeds.py` (notebook)

**Interfaces:**
- Consumes: the Delta staging tables from F2.
- Produces: files under `/Volumes/${catalog}/landing${suffix}/feeds/{po,gr,invoice}/` —
  POs and GRs as CSV, invoices as JSON (mixed formats on purpose, to exercise the pipeline), one
  file per period (e.g., per month) so Auto Loader has multiple files to pick up.

**Databricks Assistant prompt (generate, then review & own):**
```
Write a Databricks notebook that exports the F2 staging tables to files on the landing volume:
po_line and gr_line as monthly CSV files under feeds/po and feeds/gr; invoice_line as monthly JSON
files under feeds/invoice. Partition file names by year-month. Print the files written per folder.
```

**Verify:**
```bash
databricks fs ls /Volumes/febar_accord_dev/landing_dev/feeds/invoice --profile <name>
# expect multiple monthly JSON files
```

---

## Self-Review

**Coverage (Phase 0):**

| Object | Produces | Feeds into |
|---|---|---|
| F1 | catalog + schemas + volume + grants | everything |
| F2 | linked PO/GR/Invoice + vendor_master + `line_truth` (labels) | P-series match, M-series labels |
| F3 | file feeds on the volume | P1 Auto Loader ingestion |

**Design checks:**
- `line_truth` is the **ground truth** — Phase 1's match result is later compared against it
  (match accuracy) and Phase 2 trains against it. Keep it out of the features to avoid leakage.
- Disposition mix must give the summary page real numbers (auto-approved vs hold vs — later —
  rejected) and the exceptions page a real reason breakdown.
- Exception rates **vary by vendor** so the vendor-history ML feature and the exceptions-by-supplier
  view have signal.

**Open items:**
- Volume size vs. cost — start ~tens of thousands of invoice lines; scale later if needed.
- Whether to also emit a few malformed rows to exercise `_rescued_data` in Phase 1 (nice Product
  touch) — recommend yes, a small %.

**Exit criteria:** F1–F3 all ✅ in `BUILD_TRACKER.md`; feeds visible on the volume; `line_truth`
distribution verified. Then start Phase 1.
