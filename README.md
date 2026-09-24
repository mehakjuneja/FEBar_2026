# Accord — 3-Way Match Invoice Approval for Fragrance Retail

> **FE Bar 2026 submission build.** An end-to-end Databricks solution for **Maison Lumière**
> (a fictional, synthetic-data fragrance retailer): automated **three-way match** of Purchase
> Orders ↔ Goods Receipts ↔ Supplier Invoices, with an **AP analyst workbench** that recommends
> **Approve / Hold** on each invoice line and explains the **root cause** of every hold.
>
> Codename **Accord** — a perfume *accord* is a blend of notes that agree; an *accord* is also an
> agreement. When the PO, the receipt, and the invoice agree, the line pays. When they don't, Accord
> tells the analyst why.

---

## What this repo is

This is the **planning and build repository** for my [FE Bar](docs/FE_BAR_REQUIREMENTS.md)
submission. The FE Bar (go/fe-bar) is Field Engineering's AI-driven skills-validation program:
**1 Databricks certification + 1 end-to-end AI build + 1 customer-facing AI roleplay**, scored by
an AI validator across four domains (Industry, Product, Build + AI Mindset, Customer Skills).
Completion is expected by **November 30, 2026**.

Everything in `docs/` is the plan; the module folders hold the build.

## The business problem (why an AP team cares)

Accounts Payable at a retailer pays thousands of supplier invoice lines a month. Before paying,
each line should reconcile against what was **ordered** (the PO) and what was **received** (the
goods receipt). Doing this by hand is slow and leaks money — duplicate invoices, price creep above
the PO, billing for quantities never received. **Accord** ingests all three document streams,
performs the three-way match, and gives the analyst a prioritized queue with an **AI Approve/Hold
recommendation and a plain-language root cause** for every exception.

## The three parties → the three documents

| Party | Document | Key fields it asserts |
|---|---|---|
| Retailer (Maison Lumière — AP/procurement) | **Purchase Order (PO)** | vendor, product number, qty ordered, unit price, ship-to |
| Fulfillment center / 3PL | **Goods Receipt / ASN** | product number, qty received, condition, receipt date |
| 3rd-party supplier (fragrance house) | **Invoice** | vendor remit-to, product number, qty billed, unit price, tax |

The match reconciles invoice lines to PO and receipt lines on **product number, count/quantity,
unit price, vendor name / address / email, and UOM**, within configurable tolerances.

## Architecture at a glance

```
 PO feed ─┐
 GR feed ─┼─► Lakeflow SDP ─► bronze ─► silver (conformed lines) ─► gold (3-way match + features)
 INV feed ┘     (raw)                                                   │
                                                                        ├─► MLflow model (Approve/Hold + root cause) ─► Serving endpoint
                                                                        ├─► Genie space (NL Q&A over match results)
                                                                        └─► AP Analyst Workbench (Databricks App)
                                                                              ├─ review queue
                                                                              ├─ 3-way side-by-side line detail
                                                                              ├─ AI recommendation + root-cause panel  (calls serving + AI Gateway)
                                                                              ├─ approve / hold + audit log
                                                                              └─ embedded Genie
```

## Repository layout (mirrors go/sled_hands_on_workshop conventions)

| Path | What it holds |
|---|---|
| `docs/FE_BAR_REQUIREMENTS.md` | The program: rules, timeline, submission mechanics, integrity rules |
| `docs/RUBRIC.md` | The four scoring domains, Below/Meets/Exceeds, hard gates — mapped to this build |
| `docs/BUILD_TRACKER.md` | Authoritative build-object tracker + rubric coverage |
| `docs/superpowers/specs/` | The solution design spec |
| `docs/superpowers/plans/` | Dated, checkbox-driven, per-object implementation plans (one per phase) |
| `docs/runbook/` | Walkthroughs (governance, ops, demo script) |
| `docs/presentation/` | Deck outline + roleplay prep (business + technical stakeholders) |
| `foundation/` | Unity Catalog setup + synthetic PO/GR/Invoice data generation + landing feeds |
| `pipeline/` | Lakeflow Spark Declarative Pipeline: raw → bronze → silver → gold match table |
| `ml/` | Approve/Hold + root-cause model: feature engineering, training, MLflow, UC model, serving |
| `genie/` | Genie space over the governed gold tables |
| `app/` | AP Analyst Workbench (Databricks App) |
| `dashboard/` | AI/BI exceptions dashboard *(optional add)* |
| `agents/` | AI Gateway root-cause / vendor-dispute act-layer tool *(optional add)* |
| `scripts/` | Workspace setup + teardown helpers |

Each module folder carries `src/` (notebooks/code), `resources/` (DAB YAML), and a `RUNBOOK.md`.

## FE Bar mapping (the three required elements + the four scored domains)

| FE Bar requirement | Where it lives here |
|---|---|
| **Certification** (of your choice) | Data Engineer Associate — see `docs/FE_BAR_REQUIREMENTS.md` |
| **Lakeflow pipeline** (raw→silver→gold, SDP) | `pipeline/` — Phase 1 |
| **Real ML model behind a serving endpoint** | `ml/` — Phase 2 |
| **Genie agent over governed tables** | `genie/` — Phase 3 |
| End-to-end integrated app | `app/` — Phase 4 |
| Optional adds (AI/BI, act-layer via AI Gateway) | `dashboard/`, `agents/` — Phase 5 |
| Customer-facing roleplay | `docs/presentation/` — Phase 6 |

## Build phases

| Phase | Plan | Objects |
|---|---|---|
| 0 | [Foundation](docs/superpowers/plans/2026-09-24-phase0-foundation.md) | F1–F3: UC setup, synthetic data, landing feeds |
| 1 | [Lakeflow pipeline](docs/superpowers/plans/2026-09-24-phase1-pipeline.md) | P1–P3: ingest → conform → 3-way match |
| 2 | [ML model](docs/superpowers/plans/2026-09-24-phase2-ml.md) | M1–M4: features, train, register, serve |
| 3 | [Genie agent](docs/superpowers/plans/2026-09-24-phase3-genie.md) | G1: Genie over gold |
| 4 | [AP Analyst Workbench app](docs/superpowers/plans/2026-09-24-phase4-app.md) | A1–A6 |
| 5 | [Optional adds](docs/superpowers/plans/2026-09-24-phase5-optional-adds.md) | D1 dashboard, X1 act-layer |
| 6 | [Presentation & roleplay](docs/superpowers/plans/2026-09-24-phase6-presentation-roleplay.md) | R1–R3 |

## Guardrails (read before building)

- **Synthetic data only.** No real customer data, no secrets. The FE Bar scanner blocks
  submissions containing credentials. See `docs/FE_BAR_REQUIREMENTS.md` § Integrity.
- **This is my own work.** AI tools are used to scaffold, refactor, and research; the decisions,
  the code understanding, and the value story are mine, and I defend them in the roleplay.
- **Never auto-select a Databricks profile.** Pass `--profile <name>` explicitly; the target
  workspace is operator-chosen.
- **DAB targets:** `dev` and `prod` (see `databricks.yml`); catalog via bundle variable.

## Status

See [`docs/BUILD_TRACKER.md`](docs/BUILD_TRACKER.md) for live status. As of scaffold: **planning
complete, build not started.**
