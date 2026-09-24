# Accord — Phase 1: Lakeflow Pipeline (P1–P3) — Implementation Plan

> **FE Bar HARD GATE.** A self-built **Spark Declarative Pipeline (SDP)** doing raw → silver → gold
> with `read_files`/Auto Loader, streaming tables, and materialized views. Work task-by-task;
> **build → run → assert → commit.** Planning-only: approach + prompts + verify — **you write and
> own the code.** Design: [`../specs/2026-09-24-accord-3way-match-design.md`](../specs/2026-09-24-accord-3way-match-design.md).
>
> **Skills to load when building:** `databricks-core` → `databricks-pipelines` (SDP),
> `databricks-unity-catalog` (governance/lineage), optionally
> `databricks-spark-structured-streaming` (streaming-table semantics).

**Goal:** Turn the three landed document feeds (PO, GR, Invoice) into one governed **three-way match
result** — the table the model, Genie, and the app all consume. This is the heart of Accord.

**Architecture:** one Lakeflow SDP with three layers. **bronze** = raw landed rows per feed
(`read_files`/Auto Loader streaming tables). **silver** = conformed, typed, deduped line items +
governed `vendor_master` and `match_config`. **gold** = `invoice_match_result` (materialized view):
one row per invoice line with disposition (`AUTO_APPROVED` | `HOLD`), per-field match flags,
exception reason code(s), discrepancy features, and `amt_at_risk`.

**Tech stack:** Lakeflow SDP (streaming tables + materialized views), Auto Loader (`read_files`),
Unity Catalog, Delta, SQL/PySpark, serverless.

## Global constraints

- **Parameterized:** widgets/bundle vars `catalog`, `schema_suffix`; no hardcoded literals.
- **Profile:** operator-chosen; `--profile <name>`; never auto-select.
- **Tolerances are governed** in `match_config` (D-1: 2% price, exact qty + immaterial-$ auto-pass),
  so a demo can change them live.
- **Match logic is deterministic/rules-based** (the code) — the ML model (Phase 2) predicts
  hold-likelihood on top; keep the two separate (D-5).
- **Layer naming** per spec §4; tables scenario-scoped so nothing clobbers foundation staging.

---

## Task P1: Raw ingestion → bronze (Tracks: hard gate)

**Files:**
- Create: `pipeline/src/bronze_ingest.py` (SDP source; streaming tables)
- Create: `pipeline/resources/accord_pipeline.pipeline.yml` (the SDP definition; grows through P1–P3)

**Interfaces:**
- Consumes: `/Volumes/${catalog}/landing${suffix}/feeds/{po,gr,invoice}/` (from F3) — po/gr CSV,
  invoice JSON.
- Produces: bronze streaming tables `bronze_po_raw`, `bronze_gr_raw`, `bronze_invoice_raw` with
  `_ingested_at`, `_source_file`, `_rescued_data`.

**Approach:**
- [ ] Three streaming tables reading with `read_files` (CSV for po/gr, JSON for invoice), schema
      inference + `_rescued_data` on, `_metadata.file_path` → `_source_file`, `current_timestamp()`
      → `_ingested_at`.
- [ ] No transforms in bronze beyond light typing; keep it faithful to the source.

**Lakeflow Designer NL prompt (generate, then own):**
```
Create a Lakeflow pipeline that incrementally ingests three file feeds from a Unity Catalog volume:
1. feeds/po/*.csv  -> streaming table bronze_po_raw (CSV, header, rescue bad records)
2. feeds/gr/*.csv  -> streaming table bronze_gr_raw
3. feeds/invoice/*.json -> streaming table bronze_invoice_raw (JSON)
For each, add columns _ingested_at (current_timestamp) and _source_file (input file name), and keep
_rescued_data. Output row counts per table.
```

**Verify:**
```sql
SELECT count(*) FROM febar_accord_dev.bronze_dev.bronze_invoice_raw;  -- = invoice feed rows
SELECT count(*) FROM febar_accord_dev.bronze_dev.bronze_invoice_raw WHERE _rescued_data IS NOT NULL; -- small % (seeded malformed)
```

---

## Task P2: Bronze → silver conform (Tracks: hard gate)

**Files:**
- Create: `pipeline/src/silver_conform.py`
- Add to: `pipeline/resources/accord_pipeline.pipeline.yml`
- Create (seed): governed `match_config` (tolerances) — a small seed table/notebook.

**Interfaces:**
- Consumes: bronze tables + `vendor_master` (from foundation).
- Produces: silver materialized views `silver_po_line`, `silver_gr_line`, `silver_invoice_line`,
  plus governed `vendor_master` and `match_config`.

**Approach:**
- [ ] Type/cast keys (`po_id`, `product_no`, `qty_*`, `unit_price`, dates); enforce a light
      expectation set (`EXPECT` non-null keys → quarantine/drop, and count).
- [ ] **Dedup** invoice lines on `(vendor_id, invoice_no, inv_line_no)` (keep a `dup_seq` for the
      `DUP_INVOICE` signal in P3).
- [ ] **Normalize** vendor name/address (trim/upper/collapse whitespace; strip punctuation) and
      **UOM** (map synonyms → canonical) — enables reliable matching in P3.
- [ ] Seed `match_config`: `price_tol_pct`, `qty_tol_units`, `immaterial_amt` — governed so
      the demo can retune tolerances live.

**Databricks Assistant prompt (generate, then own):**
```
Write SDP silver transforms: from bronze_po_raw/bronze_gr_raw/bronze_invoice_raw create
materialized views silver_po_line, silver_gr_line, silver_invoice_line with proper types, non-null
key expectations, and dedup of invoice lines on (vendor_id, invoice_no, inv_line_no) preserving a
dup_seq. Add UOM normalization (map synonyms to a canonical uom) and vendor name/address
normalization (trim, upper, collapse whitespace). Also emit match_config with price_tol_pct,
qty_tol_units, immaterial_amt.
```

**Verify:**
```sql
SELECT count(*), count(DISTINCT (vendor_id, invoice_no, inv_line_no)) FROM febar_accord_dev.silver_dev.silver_invoice_line; -- equal after dedup
SELECT DISTINCT uom FROM febar_accord_dev.silver_dev.silver_invoice_line; -- canonical set only
```

---

## Task P3: Silver → gold three-way match + features (Tracks: hard gate) — the heart

**Files:**
- Create: `pipeline/src/gold_match.py`
- Add to: `pipeline/resources/accord_pipeline.pipeline.yml`

**Interfaces:**
- Consumes: silver line tables + `match_config` + `vendor_master`.
- Produces: gold materialized view **`invoice_match_result`** — one row per invoice line.

**`invoice_match_result` columns (contract for ML/Genie/App):**
- keys: `invoice_id`, `inv_line_no`, `po_id`, `product_no`, `vendor_id`, `invoice_date`
- match flags: `price_match`, `qty_match`, `vendor_match`, `uom_match`, `receipt_present`, `po_present`, `is_duplicate`
- features: `price_var_pct`, `qty_var_units`, `receipt_lag_days`, `days_since_po`, `invoice_amount`, `amt_at_risk`
- disposition: `disposition` (`AUTO_APPROVED` | `HOLD`), `reason_code` (exception taxonomy; may be a
  list for multi-exception lines), `reason_detail`
- lineage: `_computed_at`

**Approach (the match):**
- [ ] Join invoice line → PO line on `(po_id, product_no)`; LEFT so `NO_PO` surfaces as null PO.
- [ ] Join to GR line(s) on `(po_id, product_no)`; aggregate `qty_received`, earliest/last
      `receipt_date`; LEFT so `NO_RECEIPT` surfaces.
- [ ] Compute flags/features vs `match_config` tolerances; derive `reason_code` per the taxonomy
      (spec §2). `AUTO_APPROVED` iff all asserts pass (or variance immaterial); else `HOLD` with the
      first/most-severe reason (+ full list in `reason_detail`).
- [ ] `amt_at_risk` = the $ exposed by the exception (e.g., price-var × qty, or full line for
      NO_RECEIPT/DUP).

**Databricks Assistant prompt (generate, then own):**
```
Write an SDP gold transform invoice_match_result: for each silver_invoice_line, LEFT JOIN
silver_po_line on (po_id, product_no) and LEFT JOIN aggregated silver_gr_line on (po_id,
product_no). Using match_config tolerances, compute price_match (abs(inv-po)/po <=
price_tol_pct), qty_match (qty_billed <= qty_received + qty_tol_units), vendor_match (remit-to vs
vendor_master, normalized), uom_match, receipt_present, po_present, is_duplicate (dup_seq>1). Derive
features price_var_pct, qty_var_units, receipt_lag_days, days_since_po, invoice_amount, amt_at_risk.
Set disposition AUTO_APPROVED when every assert passes (or variance is immaterial), else HOLD with a
reason_code from {PRICE_VAR, QTY_OVERBILL, NO_RECEIPT, NO_PO, DUP_INVOICE, VENDOR_MISMATCH,
UOM_MISMATCH} and a reason_detail listing all failed asserts.
```

**Verify (functional + reconciliation against ground truth):**
```sql
-- disposition mix
SELECT disposition, count(*), round(sum(amt_at_risk),2) amt FROM febar_accord_dev.gold_dev.invoice_match_result GROUP BY 1;
-- reason breakdown
SELECT reason_code, count(*) FROM febar_accord_dev.gold_dev.invoice_match_result WHERE disposition='HOLD' GROUP BY 1 ORDER BY 2 DESC;
-- MATCH ACCURACY vs seeded ground truth (foundation line_truth): should agree on the large majority
SELECT (r.disposition='HOLD') AS pred_hold, (t.true_disposition='HOLD') AS true_hold, count(*)
FROM febar_accord_dev.gold_dev.invoice_match_result r
JOIN febar_accord_dev.landing_dev.line_truth t USING (invoice_id, inv_line_no)
GROUP BY 1,2;  -- inspect off-diagonal: those are the interesting edge cases (great roleplay material)
```

---

## Self-Review

| Object | Produces | Feeds |
|---|---|---|
| P1 | bronze raw streaming tables | P2 |
| P2 | conformed silver + governed config/vendor | P3 |
| P3 | `invoice_match_result` (gold) | M (features/labels), G (Genie), A (app), D (dashboard) |

**Design checks:**
- The match is **rules/deterministic**; ML sits on top (D-5) — do not let the rule outputs leak into
  the model as trivial label copies (Phase 2 M1 handles the leakage guard).
- Tolerances live in `match_config` so the technical roleplay can show governed, live-tunable logic.
- The reconciliation query above is the **match-accuracy** proof and a source of the "interesting
  edge cases" I discuss in the roleplay.

**Open items:**
- Multi-exception lines: store all in `reason_detail`, pick a severity-ordered primary `reason_code`.
- Lineage across bronze→silver→gold is the Product/governance evidence (screenshot for the deck).

**Exit criteria:** P1–P3 ✅; disposition mix + reason breakdown sane; match accuracy vs `line_truth`
verified. Then Phase 2 (ML).
