# pipeline/ — RUNBOOK

**Phase 1 — FE Bar HARD GATE.** Lakeflow SDP: raw → silver → gold three-way match. Plan:
[`../docs/superpowers/plans/2026-09-24-phase1-pipeline.md`](../docs/superpowers/plans/2026-09-24-phase1-pipeline.md)

| Object | File | Purpose |
|---|---|---|
| P1 | `src/bronze_ingest.py` | `read_files`/Auto Loader → bronze streaming tables |
| P2 | `src/silver_conform.py` | typing, dedup, vendor/UOM normalization, `match_config` |
| P3 | `src/gold_match.py` | **3-way match** → `invoice_match_result` (gold) |
| — | `resources/accord_pipeline.pipeline.yml` | the SDP definition |

**Skills:** databricks-core → databricks-pipelines, databricks-unity-catalog,
databricks-spark-structured-streaming.

**Run:** `databricks bundle run accord_pipeline -t dev --profile <name>`

**Verify:** disposition mix + reason breakdown sane; **match accuracy vs `line_truth`** (the
reconciliation query in the plan). `invoice_match_result` is the contract for ML/Genie/App.
