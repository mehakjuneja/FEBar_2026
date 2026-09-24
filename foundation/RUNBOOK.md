# foundation/ — RUNBOOK

**Phase 0.** UC setup + synthetic PO/GR/Invoice data (with seeded, labeled discrepancies) + landing
feeds. Plan: [`../docs/superpowers/plans/2026-09-24-phase0-foundation.md`](../docs/superpowers/plans/2026-09-24-phase0-foundation.md)

| Object | File | Purpose |
|---|---|---|
| F1 | `src/00_uc_setup.py` | catalog, schemas, landing volume, grants |
| F2 | `src/10_generate_documents.py` | synthetic vendors/SKUs/PO/GR/Invoice + `line_truth` labels |
| F3 | `src/20_write_feeds.py` | export feeds to the volume (po/gr CSV, invoice JSON) |

**Skills:** databricks-core → databricks-unity-catalog, databricks-synthetic-data-gen (or
fe-databricks-tools:databricks-data-generation), databricks-dabs.

**Run:** `databricks bundle run foundation_job -t dev --profile <name>`

**Verify:** `line_truth` disposition mix ≈ 70% MATCH_OK; feeds present under
`/Volumes/febar_accord_dev/landing_dev/feeds/`. See the plan's Verify blocks.
