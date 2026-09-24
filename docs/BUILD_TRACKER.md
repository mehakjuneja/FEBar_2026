# Accord — Build Tracker

Authoritative status for every build object and every FE Bar hard gate + rubric domain. Update this
when an object lands: flip its status here (and check the box in its phase plan).

> **Two things this tracks:**
> 1. **Build objects** (F/P/M/G/A/D/X/R) — what I actually work on, phase by phase.
> 2. **FE Bar coverage** — the hard gates and the four scored domains the objects satisfy.

**Status legend:** ✅ Built & verified · 🟡 In progress / partial · ⬜ Planned only
**Verified means:** it ran, and I checked the output against an explicit expectation (row counts,
endpoint responds, Genie answers correctly, app renders + writes an audit row).

**Last updated:** 2026-09-24 — **Phase 0 COMPLETE & verified** in the FEVM `accord-febar` workspace
(catalog `accord_febar_catalog`). F1 UC setup; F2 generated 25 vendors / 300 SKUs / 11.7k PO /
11.2k GR / 12.3k invoice lines with ground-truth mix (MATCH_OK 71.5%, rest across the taxonomy);
F3 wrote monthly CSV/JSON feeds to the `landing.feeds` volume. Deployed via DAB job
`foundation_build`. **Next: Phase 1 (P1 ingestion).**

---

## Hard gates (must all be ✅ to pass)

| Gate | Object(s) | Status |
|---|---|---|
| Lakeflow pipeline (SDP raw→silver→gold) | P1, P2, P3 | ⬜ |
| Real ML model behind a serving endpoint | M2, M3 | ⬜ |
| Genie agent over governed tables | G1 | ⬜ |
| One integrated end-to-end journey | F→P→M→G→A | ⬜ |
| Customer-safe (synthetic, no secrets) | F2, all | ⬜ |
| Own work / attestation / defensible | all | ⬜ |
| Certification current (DE Associate) | — | 🟡 in prep |

---

## Phase 0 — Foundation

| ID | Object | Status | Verify | Notes |
|---|---|---|---|---|
| F1 | UC setup (catalog/schemas/volume/grants) | ✅ | schemas + volume + feed folders verified | `foundation/src/00_uc_setup.py` |
| F2 | Synthetic PO/GR/Invoice generator (+ seeded labeled discrepancies) | ✅ | 25 vendors, 12.3k invoice lines, MATCH_OK 71.5% | ground truth for ML |
| F3 | Landing feeds written to volume | ✅ | 18–19 monthly partitions per feed | CSV po/gr, JSON invoice |

## Phase 1 — Lakeflow pipeline *(hard gate)*

| ID | Object | Status | Verify | Notes |
|---|---|---|---|---|
| P1 | Raw ingestion → bronze (`read_files`/Auto Loader) | ⬜ | bronze row counts = feed counts | streaming tables |
| P2 | Bronze → silver conform (+ vendor_master, match_config) | ⬜ | typed/deduped counts; normalization | |
| P3 | Silver → gold **3-way match** + features (`invoice_match_result`) | ⬜ | disposition mix matches seeded truth | the heart of the build |

## Phase 2 — ML model *(hard gate)*

| ID | Object | Status | Verify | Notes |
|---|---|---|---|---|
| M1 | Feature engineering + label view | ⬜ | feature table row count; label balance | |
| M2 | Train Approve/Hold model + MLflow tracking | ⬜ | logged run; metrics beat baseline | GBT baseline |
| M3 | Register UC model + serving endpoint | ⬜ | endpoint READY; scores a test row | hard gate |
| M4 | Inference wiring (batch → gold + realtime contract) | ⬜ | gold has scores; app contract doc | |

## Phase 3 — Genie *(hard gate)*

| ID | Object | Status | Verify | Notes |
|---|---|---|---|---|
| G1 | Genie space over gold + curated sample Q&A | ⬜ | 5 sample Qs return correct SQL-backed answers | not the app chatbot |

## Phase 4 — Invoice Reconciliation Workbench (app)

| ID | Object | Status | Verify | Notes |
|---|---|---|---|---|
| A1 | App scaffold (auth, data access, serving client) | ⬜ | app deploys + loads | |
| A2 | Summary landing page (suppliers, invoices by w/m/y, dispositions $) | ⬜ | tiles match gold aggregates | |
| A3 | Reconciliation review page (filters + bulk approve/reject) | ⬜ | filter + bulk action updates state | core workflow |
| A4 | Exceptions page (what/why, grouped) | ⬜ | reason breakdown matches gold | |
| A5 | Line detail (3-way side-by-side + AI panel) | ⬜ | serving call renders rec + root cause | |
| A6 | Decision write-back + audit + embedded Genie | ⬜ | audit row written; Genie answers | |

## Phase 5 — Optional adds *(Exceeds levers)*

| ID | Object | Status | Verify | Notes |
|---|---|---|---|---|
| D1 | AI/BI exceptions dashboard | ⬜ | dashboard renders from gold | optional |
| X1 | AI Gateway act-layer (root-cause narrative + dispute draft) | ⬜ | returns grounded text for a held line | optional |

## Phase 6 — Presentation & roleplay

| ID | Object | Status | Verify | Notes |
|---|---|---|---|---|
| R1 | Presentation deck (PDF) | ⬜ | full narrative arc; exported PDF | submission artifact |
| R2 | Business-stakeholder prep | ⬜ | objection list + $ story | Controller / VP Finance |
| R3 | Technical-stakeholder prep | ⬜ | architecture + governance deep-dive | Head of Data |

---

## Rubric coverage snapshot

| Domain | Primary evidence | Meets? | Exceeds lever |
|---|---|---|---|
| Industry | spec §1–2, deck (R1) | ⬜ | fragrance-retail specifics, ERP contrast |
| Product | P*, M*, G1, A* | ⬜ | D1, X1, Lakehouse Monitoring, UC mask |
| Build + AI Mindset | end-to-end run + spec §10 decisions | ⬜ | X1 act-layer, feedback loop |
| Customer Skills | R2, R3 dry-run | ⬜ | discovery framing, POC-metrics close |

## Build sequence

`F1 → F2 → F3 → P1 → P2 → P3 → M1 → M2 → M3 → M4 → G1 → A1 → A2 → A3 → A4 → A5 → A6 → (D1, X1) → R1 → R2 → R3`

Each object: **build → run → assert → commit.** Don't advance a phase until its objects are ✅.
