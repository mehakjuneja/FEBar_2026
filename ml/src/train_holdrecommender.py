# Databricks notebook source
# MAGIC %md
# MAGIC # M2 — Train the Approve/Hold recommender (Accord)
# MAGIC
# MAGIC Gradient-boosted trees on the leakage-guarded discrepancy features (`ml.features_labeled`),
# MAGIC label = `line_truth` ground truth. MLflow-tracked, registered to Unity Catalog, alias `@champion`.
# MAGIC Decision D-2 (GBT), D-3 (threshold tuned toward Hold **recall** — a false approve pays bad money).

# COMMAND ----------
dbutils.widgets.text("catalog", "accord_febar_catalog", "Catalog")
dbutils.widgets.text("schema_suffix", "", "Schema suffix")
CATALOG = dbutils.widgets.get("catalog")
SUFFIX = dbutils.widgets.get("schema_suffix")
ML = f"{CATALOG}.ml{SUFFIX}"
MODEL_NAME = f"{ML}.accord_holdrecommender"

import json, mlflow, numpy as np, pandas as pd
from mlflow.tracking import MlflowClient
from mlflow.models.signature import infer_signature
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (roc_auc_score, precision_recall_fscore_support,
                             accuracy_score, confusion_matrix)
from sklearn.inspection import permutation_importance

mlflow.set_registry_uri("databricks-uc")
user = spark.sql("SELECT current_user()").first()[0]
mlflow.set_experiment(f"/Users/{user}/accord/mlflow_holdrecommender")

# COMMAND ----------
# MAGIC %md ## M1 — (re)build the leakage-guarded feature/label table (idempotent)
# MAGIC Same logic as `ml/src/M1_features.sql`; kept here so the job reproduces end-to-end.

# COMMAND ----------
GOLD = f"{CATALOG}.gold{SUFFIX}"
LANDING = f"{CATALOG}.landing{SUFFIX}"
spark.sql(f"""
CREATE OR REPLACE TABLE {ML}.features_labeled AS
WITH base AS (
  SELECT g.invoice_id, g.inv_line_no, g.vendor_id,
    coalesce(g.price_var_pct,0.0) price_var_pct, coalesce(g.qty_var,0) qty_var,
    coalesce(g.qty_ordered_var,0) qty_ordered_var, coalesce(g.receipt_lag_days,-1) receipt_lag_days,
    coalesce(g.days_since_po,-1) days_since_po, g.invoice_amount, g.dup_count,
    CAST(g.has_po AS INT) has_po, CAST(g.has_gr AS INT) has_gr,
    CAST(coalesce(g.inv_remit_to = g.vendor_remit_to, false) AS INT) remit_match,
    CAST(coalesce(g.inv_uom = g.po_uom, false) AS INT) uom_match,
    CASE WHEN t.true_disposition='HOLD' THEN 1 ELSE 0 END y_hold
  FROM {GOLD}.invoice_match_result g JOIN {LANDING}.line_truth t USING (invoice_id, inv_line_no)
),
vend AS (SELECT vendor_id, sum(y_hold) v_holds, count(*) v_total FROM base GROUP BY vendor_id)
SELECT b.*, round(CASE WHEN v.v_total>1 THEN (v.v_holds-b.y_hold)/(v.v_total-1) ELSE 0.0 END,4) vendor_exc_rate
FROM base b JOIN vend v USING (vendor_id)
""")

# COMMAND ----------
# MAGIC %md ## Load features + split (stratified)

# COMMAND ----------
pdf = spark.table(f"{ML}.features_labeled").toPandas()
FEATURES = ["price_var_pct","qty_var","qty_ordered_var","receipt_lag_days","days_since_po",
            "invoice_amount","dup_count","has_po","has_gr","remit_match","uom_match","vendor_exc_rate"]
X, y = pdf[FEATURES], pdf["y_hold"].astype(int)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, stratify=y, random_state=42)
print(f"train={len(X_train)}  test={len(X_test)}  hold%={100*y.mean():.1f}")

# Baseline: majority class (predict everything AUTO_APPROVE)
majority_acc = max(y_test.mean(), 1 - y_test.mean())
print(f"majority-class baseline accuracy = {majority_acc:.4f}")

# COMMAND ----------
# MAGIC %md ## Train + log + register

# COMMAND ----------
def metrics_at(proba, thr):
    pred = (proba >= thr).astype(int)
    p, r, f1, _ = precision_recall_fscore_support(y_test, pred, average="binary", pos_label=1, zero_division=0)
    return {"threshold": thr, "accuracy": accuracy_score(y_test, pred),
            "hold_precision": p, "hold_recall": r, "hold_f1": f1}

with mlflow.start_run(run_name="holdrecommender-gbt") as run:
    model = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1,
                                           max_depth=6, random_state=42)
    model.fit(X_train, y_train)
    proba = model.predict_proba(X_test)[:, 1]

    auc = roc_auc_score(y_test, proba)
    m050 = metrics_at(proba, 0.50)                 # default
    m035 = metrics_at(proba, 0.35)                 # recall-favoring (D-3)

    mlflow.log_metric("roc_auc", auc)
    mlflow.log_metric("baseline_majority_acc", majority_acc)
    for tag, mm in [("t50", m050), ("t35", m035)]:
        for k, v in mm.items():
            mlflow.log_metric(f"{tag}_{k}", float(v))
    mlflow.log_param("model_type", "HistGradientBoostingClassifier")
    mlflow.log_param("features", ",".join(FEATURES))
    mlflow.log_param("decision_threshold", 0.35)   # app default: favor catching holds

    # permutation importance (top drivers — for the roleplay + the app's "why" panel)
    imp = permutation_importance(model, X_test, y_test, n_repeats=5, random_state=42)
    fi = sorted(zip(FEATURES, imp.importances_mean), key=lambda t: -t[1])
    mlflow.log_dict({k: float(v) for k, v in fi}, "feature_importance.json")

    signature = infer_signature(X_train, model.predict_proba(X_train)[:, 1])
    info = mlflow.sklearn.log_model(
        model, name="model", signature=signature,
        input_example=X_train.head(3), registered_model_name=MODEL_NAME)

client = MlflowClient(registry_uri="databricks-uc")
client.set_registered_model_alias(MODEL_NAME, "champion", info.registered_model_version)

print(f"AUC={auc:.4f}")
print(f"@0.50: {m050}")
print(f"@0.35: {m035}")
print("top features:", fi[:5])

# COMMAND ----------
# MAGIC %md ## Exit with structured result

# COMMAND ----------
dbutils.notebook.exit(json.dumps({
    "model": MODEL_NAME, "version": info.registered_model_version,
    "roc_auc": round(auc, 4), "baseline_majority_acc": round(majority_acc, 4),
    "hold_recall_t35": round(m035["hold_recall"], 4), "hold_f1_t35": round(m035["hold_f1"], 4),
    "top_features": [k for k, _ in fi[:5]],
}))
