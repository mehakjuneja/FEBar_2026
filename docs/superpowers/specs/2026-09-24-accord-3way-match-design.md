# Accord — Solution Design Spec (3-Way Match Invoice Approval)

**Date:** 2026-09-24
**Author:** Mehak Juneja
**Status:** Design locked for scaffolding; open decisions flagged inline.
**FE Bar element:** the build (paired with DE Associate cert + the AI roleplay).

> This is the single source of truth for architecture, naming, and design decisions. Every phase
> plan in `docs/superpowers/plans/` inherits the decisions here. If a plan needs to diverge, update
> this spec first.

---

## 1. Problem & industry framing

**Customer:** *Maison Lumière* — a fictional, synthetic prestige-fragrance retailer. Accounts
Payable pays thousands of supplier invoice lines a month across dozens of fragrance houses (3rd-party
suppliers) and multiple fulfillment centers.

**Problem:** Before an invoice line is paid, AP should confirm a **three-way match** — the line
agrees with what was **ordered** (PO) and what was **received** (goods receipt). Today this is
manual and rules-only in the ERP: high touch, slow cycle times, and real leakage — duplicate
invoices, unit prices creeping above the PO, and billing for quantities that were never received.
The team lacks a prioritized, explainable view of *which* lines to hold and *why*.

**Solution (Accord):** ingest the three document streams, run the three-way match in a governed
Lakeflow pipeline, score each invoice line with an ML model that recommends **Approve / Hold** and a
**root-cause reason**, and surface it all in an **AP Analyst Workbench** app where the analyst
reviews, decides, and leaves an audit trail. A Genie space answers ad-hoc questions over the results.

**Value (business terms):** touchless-match rate ↑, invoice-exception cycle time ↓, recovered $
from blocked overbilling/duplicates, analyst capacity freed for judgment calls, and a cleaner audit
trail. *(These become the deck's headline metrics; see `docs/presentation/`.)*

## 2. The three parties → three documents → the match

| Party | Document | Grain | Key assert fields |
|---|---|---|---|
| Retailer AP/procurement | **Purchase Order (PO)** | po_id + po_line_no | vendor_id, product_no, qty_ordered, unit_price, uom, ship_to |
| Fulfillment center / 3PL | **Goods Receipt (GR/ASN)** | gr_id + gr_line_no | po_id, product_no, qty_received, condition, receipt_date |
| 3rd-party supplier | **Invoice** | invoice_id + inv_line_no | vendor_id, po_id, product_no, qty_billed, unit_price, uom, tax, remit_to |

**Match keys:** an invoice line matches on **(po_id, product_no)** to a PO line and to the
associated GR line(s). **Assert fields** compared within tolerance: `qty` (billed vs received vs
ordered), `unit_price` (billed vs PO), `vendor` (name/address/email/remit-to vs vendor master), and
`uom`.

**Exception taxonomy** (the root-cause labels the model/app explains):

| Code | Exception | Rule (illustrative; tolerances are governed config) |
|---|---|---|
| `PRICE_VAR` | Unit price variance | `abs(inv_price - po_price)/po_price > price_tol` (e.g. 2%) |
| `QTY_OVERBILL` | Billed > received | `qty_billed > qty_received + qty_tol` |
| `QTY_UNDERRECEIPT` | Received short of order | `qty_received < qty_ordered - qty_tol` (informational) |
| `NO_RECEIPT` | Invoiced, not received | no GR line for (po_id, product_no) |
| `NO_PO` | Invoiced, no PO | no PO line for the invoice line |
| `DUP_INVOICE` | Duplicate invoice | same (vendor_id, invoice_no, amount) seen before |
| `VENDOR_MISMATCH` | Vendor / remit-to mismatch | invoice remit-to ≠ vendor master (fuzzy) |
| `UOM_MISMATCH` | Unit-of-measure mismatch | inv_uom ≠ po_uom after normalization |
| `MATCH_OK` | Clean 3-way match | all asserts within tolerance |

> **Open decision D-1 (tolerances):** default price 2%, qty 0 units (exact) with a small $/line
> immaterial-variance auto-pass. Governed in a `match_config` table so a demo can change them live.

## 3. Architecture & data flow

```
foundation (synthetic)          pipeline (Lakeflow SDP)                    consumption
──────────────────────   ───────────────────────────────────────   ─────────────────────────
PO feed (files)  ─┐       raw ──► bronze ──► silver ──────► gold          ┌─ Genie space (G1)
GR feed (files)  ─┼──►   read_files   conform   3-way match + features ──►┼─ MLflow model ► Serving (M3)
INV feed (files) ─┘                                                       └─ AP Analyst Workbench app (A1–A6)
                                                                                │ calls serving (recommendation)
match_config, vendor_master (seed)                                             │ calls AI Gateway (root-cause text, X1)
                                                                               └─ writes decisions ► audit table
                                                          gold ──► AI/BI dashboard (D1, optional)
```

**Layered model:**

- **bronze** — raw landed rows per feed, minimal typing, `_ingested_at`, `_source_file`.
- **silver** — conformed line items: `po_line`, `gr_line`, `invoice_line`, plus governed
  `vendor_master` and `match_config`. Deduped, typed, standardized (vendor name/address
  normalization, UOM normalization).
- **gold** — `invoice_match_result` (one row per invoice line: match status, per-field flags,
  discrepancy features, `amt_at_risk`) and feature/label tables for ML.

## 4. Canonical naming (do not drift)

| Thing | Value |
|---|---|
| Codename | **Accord** |
| Catalog (dev / prod) | `febar_accord_dev` / `febar_accord` (via bundle var `catalog`) |
| Schemas | `landing`, `bronze`, `silver`, `gold`, `ml` (suffix `_dev` in dev, none in prod) |
| Volume (landing) | `/Volumes/${catalog}/landing${suffix}/feeds/{po,gr,invoice}/` |
| Match result table | `${catalog}.gold${suffix}.invoice_match_result` |
| UC model | `${catalog}.ml${suffix}.accord_holdrecommender` |
| Serving endpoint | `accord-holdrecommender` |
| Genie space | `Accord — AP 3-Way Match` |
| App | `accord-ap-workbench` |
| DAB targets | `dev`, `prod` |
| Profile | operator-chosen; pass `--profile <name>` — **never auto-select** |

**Notebook portability rule:** every notebook reads `dbutils.widgets.get("catalog")` and
`get("schema_suffix")`; **no hardcoded catalog/host/profile literals.** (Mirrors the reference repo.)

## 5. Build objects

| ID | Object | Phase | Notes |
|---|---|---|---|
| F1 | UC setup (catalog, schemas, volume, grants) | 0 | `foundation/src/00_uc_setup.py` |
| F2 | Synthetic PO/GR/Invoice generator (with seeded, labeled discrepancies) | 0 | drives everything; labels = ground truth for ML |
| F3 | Landing feeds (write files to the volume) | 0 | CSV/JSON to mimic ERP/EDI extracts |
| P1 | Raw ingestion (3 feeds via `read_files` / Auto Loader) → bronze | 1 | streaming tables |
| P2 | Bronze → silver conform (typing, dedup, vendor/UOM normalization, `vendor_master`, `match_config`) | 1 | |
| P3 | Silver → gold **3-way match** + discrepancy features (`invoice_match_result`) | 1 | the heart of the build |
| M1 | Feature engineering + train/serve label view from gold | 2 | features + `y_hold`, `y_reason` |
| M2 | Train Approve/Hold classifier (+ root-cause) with MLflow tracking | 2 | |
| M3 | Register UC model + deploy **serving endpoint** | 2 | hard gate |
| M4 | Inference wiring (batch scores to gold + real-time contract for the app) | 2 | |
| G1 | Genie space over gold match tables + curated sample Q&A | 3 | hard gate |
| A1 | App scaffold (auth, UC/SQL data access, serving client, config) | 4 | Databricks App |
| A2 | **Summary landing page** — # suppliers, invoices received by week/month/year, line dispositions (auto-approved / on-hold / rejected) with $ | 4 | KPI + trend view |
| A3 | **Reconciliation review page** — lines not auto-approved, **filters** (Supplier, Year, Month, Week, reason, $), **bulk approve / reject** | 4 | the core analyst workflow |
| A4 | **Exceptions page** — which lines were not approved and **why** (grouped/filterable by reason & supplier) | 4 | the "why" view |
| A5 | **Line detail** — 3-way side-by-side (PO vs GR vs Invoice, field flags) + AI recommendation, confidence, root cause (calls serving + AI Gateway) | 4 | ties ML into the app |
| A6 | Decision write-back (single + bulk) + audit log + embedded Genie ("Ask Accord") | 4 | note: embedded chat does **not** replace G1 for the gate |
| D1 | AI/BI exceptions dashboard | 5 | *optional / Exceeds* |
| X1 | AI Gateway act-layer: root-cause narrative + vendor-dispute draft | 5 | *optional / Exceeds* |
| R1 | Presentation deck | 6 | submitted as PDF |
| R2 | Business-stakeholder roleplay prep | 6 | |
| R3 | Technical-stakeholder roleplay prep | 6 | |

## 6. ML design (M-series)

- **Primary target:** binary **Approve (0) / Hold (1)** per invoice line — this is the model behind
  the serving endpoint (satisfies the hard gate).
- **Root cause:** the exception taxonomy in §2. Two viable approaches:
  - **(recommended) Rules produce the deterministic exception code(s); the ML model predicts
    Hold-likelihood + confidence**, and the app shows both ("Hold — Price variance +6% vs PO, model
    confidence 0.94"). Clean, explainable, defensible.
  - *(alt)* a **multiclass** model predicting the exception category directly — more "ML," but the
    labels are essentially rule-derived, so it risks learning the rules. Documented as a considered
    alternative (good roleplay material).
- **Features:** price variance %, qty variance, receipt presence/lag, vendor exception history rate,
  invoice amount, duplicate-signal, UOM-mismatch flag, days-since-PO, first-time-vendor flag.
- **Labels:** the synthetic generator (F2) seeds each line with a true disposition → ground truth,
  so training is honest and metrics are real.
- **Explainability:** feature attributions (e.g., SHAP) surfaced in the app so "why" is grounded.
- **Serving:** UC model → serving endpoint; app calls it per line (real-time) and P-series also
  writes batch scores to gold for the queue/dashboard.

> **Open decision D-2 (model family):** start with gradient-boosted trees (strong tabular baseline,
> easy SHAP) vs. logistic regression (max interpretability). Recommend GBT; keep LR as the
> "interpretability" talking point.
> **Open decision D-3 (false-approve vs false-hold cost):** a false *approve* pays bad money; a
> false *hold* costs analyst time and can miss discounts. Tune the threshold toward recall on Hold;
> document the cost framing for the business-stakeholder roleplay.

## 7. App design (A-series) — Invoice Reconciliation Workbench

An AP analyst uses Accord to clear the lines the 3-way match could **not** auto-approve. The app has
four pages plus a drill-in and embedded Genie:

1. **Summary (landing) page** — the daily starting point:
   - **# active suppliers**, **# invoices received** with a **week / month / year** toggle.
   - **Invoice-line dispositions**: **auto-approved** vs **on-hold** vs **rejected** (counts **and
     $**), as headline tiles + a trend over the selected period.
   - Fast read on backlog and $-at-risk before diving in.
2. **Reconciliation review page** — the core workflow: the queue of lines **not auto-approved**
   (`HOLD`), with **filters** by **Supplier, Year, Month, Week**, exception reason, and $ range.
   Multi-select + **bulk Approve / bulk Reject**, each row showing the AI recommendation + confidence
   + one-line root cause; ranked by $-at-risk × hold-likelihood.
3. **Exceptions page** — the analytical "**what wasn't approved and why**" view: held/rejected lines
   grouped and filterable by **exception reason** and **supplier**, with counts and $, so patterns
   (a vendor with chronic price variance) are obvious.
4. **Line detail (drill-in)** — PO vs GR vs Invoice **side-by-side** with per-field match/mismatch
   chips; the **AI panel** (recommendation, confidence, feature attributions, plain-language root
   cause via serving + AI Gateway); single Approve/Reject with reason code + note.
5. **Ask Accord** — embedded Genie for ad-hoc NL questions.

**Disposition state machine:** the match (P3) sets each line to **`AUTO_APPROVED`** (clean 3-way
match within tolerance) or **`HOLD`** (any exception). The analyst moves `HOLD` → **`APPROVED`**
(manual, incl. bulk) or **`REJECTED`** (incl. bulk). Every transition writes to an **audit table**
(who / when / from → to / reason code / note). **Human-in-the-loop:** the AI recommends and explains;
the analyst decides.

> **Open decision D-4 (app framework):** React+FastAPI (richer, more "product," better for bulk-select
> grids) vs Streamlit (faster to a working demo). Recommend deciding on Phase-4 time budget; Streamlit
> is a solid "Meets," React is the "Exceeds" flex. Bulk-select + filter UX is smoother in React.
> **Open decision D-7 (state store):** the audit/decision write-back needs a transactional store the
> app writes to. Options: a Delta table via SQL warehouse (simplest, UC-governed) vs **Lakebase**
> (Postgres, better for interactive row-level updates in an app). Recommend Lakebase for the
> decision/audit state, Delta/UC for the analytical tables; decide in Phase 4.

## 8. Optional adds (Phase 5 — Exceeds levers)

- **D1 — AI/BI dashboard:** holds by reason, by vendor, aging, $-at-risk, touchless-match rate.
  High visual payoff for the deck.
- **X1 — AI Gateway act-layer:** given a held line, generate a **root-cause narrative** and a draft
  **vendor-dispute email** / proposed GL correction. This is the strongest "AI Mindset" signal and
  directly serves the "reason why to hold" requirement.

## 9. Data governance & customer-safety

- **Synthetic only** (F2). No real vendors, no real bank data. Vendor "remit-to" and any bank-like
  fields are fake and are the natural target for a **UC column mask / row filter** demo (Product
  domain).
- **No secrets** in the repo. Serving/AI Gateway auth via the app's managed identity / UC secrets at
  runtime, never committed. (FE Bar scanner blocks secrets.)
- **Lineage** across bronze→silver→gold is the governance story for the technical stakeholder.

## 10. Design decisions log (defend these in the roleplay)

| # | Decision | Chosen | Alternatives considered | Why |
|---|---|---|---|---|
| D-1 | Match tolerances | 2% price / exact qty, governed table | hardcoded; per-vendor tolerances | live-tunable in demo; per-vendor is an Exceeds extension |
| D-2 | Model family | Gradient-boosted trees | logistic regression; deep net | best tabular baseline + easy SHAP; LR = interpretability talking point |
| D-3 | Decision threshold | tuned toward Hold recall | balanced F1 | false-approve pays bad money; cost-asymmetry story |
| D-4 | App framework | TBD Phase 4 (React+FastAPI vs Streamlit) | — | time-budget dependent; Streamlit=Meets, React=Exceeds |
| D-5 | Root cause | rules for code + ML for hold-likelihood | multiclass ML for category | avoids ML re-learning rules; more explainable |
| D-6 | Ingestion | `read_files`/Auto Loader streaming tables | batch `COPY INTO` | idiomatic Lakeflow SDP; satisfies gate cleanly |
| D-7 | Decision/audit state store | TBD Phase 4 (Lakebase vs Delta-via-SQL-warehouse) | — | Lakebase suits interactive row updates + bulk actions; Delta/UC for analytics |

*(Append as decisions are made during the build — this table is roleplay gold.)*

## 11. Out of scope (say so in the roleplay)

- Real ERP connectors (SAP/Coupa) — mocked via file feeds; the pattern maps to Lakeflow Connect.
- Payment execution / GL posting — Accord recommends and routes; it does not cut checks.
- Multi-currency & tax engines — single currency for the prototype; noted as an extension.
