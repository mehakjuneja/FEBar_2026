# ml/ — RUNBOOK

**Phase 2 — FE Bar HARD GATE.** Approve/Hold recommender: MLflow → UC model → **serving endpoint**.
Plan: [`../docs/superpowers/plans/2026-09-24-phase2-ml.md`](../docs/superpowers/plans/2026-09-24-phase2-ml.md)

| Object | File | Purpose |
|---|---|---|
| M1 | `src/10_features.py` | leakage-safe feature/label view from gold + `line_truth` |
| M2 | `src/20_train.py` | train Approve/Hold (GBT) + MLflow tracking + SHAP |
| M3 | `src/30_register_serve.py` | UC-register + deploy endpoint `accord-holdrecommender` |
| M4 | `src/40_inference.py` | batch scores → gold + real-time contract for the app |

**Skills:** databricks-core → databricks-ml-training, databricks-model-serving,
databricks-mlflow-evaluation, databricks-unity-catalog.

**Rules vs ML (D-5):** rules (P3) give the exception *code*; the model gives *hold-likelihood +
confidence*. **No leakage:** `line_truth` and rule outputs are never features.

**Verify:** endpoint READY and returns a score for a sample line; metrics beat the majority-class
baseline. UC model: `${catalog}.ml${suffix}.accord_holdrecommender`.
