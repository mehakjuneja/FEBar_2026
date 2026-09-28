# Databricks notebook source
# MAGIC %md
# MAGIC # M4 — Batch scoring (Accord)
# MAGIC
# MAGIC Loads the champion model and scores every invoice line, writing `ml.invoice_scored`
# MAGIC (hold_probability + predicted_hold at the recall-favoring threshold). This table powers the
# MAGIC app's queue ranking (`amt_at_risk × hold_probability`) and the exceptions/summary views.
# MAGIC The real-time serving endpoint returns the class decision on the line an analyst opens.

# COMMAND ----------
dbutils.widgets.text("catalog", "accord_febar_catalog", "Catalog")
dbutils.widgets.text("schema_suffix", "", "Schema suffix")
dbutils.widgets.text("threshold", "0.35", "Hold decision threshold (D-3)")
CATALOG = dbutils.widgets.get("catalog"); SUFFIX = dbutils.widgets.get("schema_suffix")
ML = f"{CATALOG}.ml{SUFFIX}"
THR = float(dbutils.widgets.get("threshold"))

import mlflow, pandas as pd
from pyspark.sql import functions as F
mlflow.set_registry_uri("databricks-uc")

FEATURES = ["price_var_pct","qty_var","qty_ordered_var","receipt_lag_days","days_since_po",
            "invoice_amount","dup_count","has_po","has_gr","remit_match","uom_match","vendor_exc_rate"]

# COMMAND ----------
# MAGIC %md ## Load champion model + score all lines (predict_proba for confidence)

# COMMAND ----------
model = mlflow.sklearn.load_model(f"models:/{ML}.accord_holdrecommender@champion")
pdf = spark.table(f"{ML}.features_labeled").toPandas()
pdf["hold_probability"] = model.predict_proba(pdf[FEATURES])[:, 1]
pdf["predicted_hold"] = (pdf["hold_probability"] >= THR).astype(int)

out = spark.createDataFrame(pdf[["invoice_id","inv_line_no","hold_probability","predicted_hold"]]) \
    .withColumn("hold_probability", F.round("hold_probability", 4)) \
    .withColumn("scored_at", F.current_timestamp())
out.write.mode("overwrite").option("overwriteSchema","true").saveAsTable(f"{ML}.invoice_scored")
print(f"scored {out.count()} lines -> {ML}.invoice_scored")

# COMMAND ----------
# MAGIC %md ## Verify — distribution
# COMMAND ----------
display(spark.sql(f"""
  SELECT predicted_hold, count(*) n, round(avg(hold_probability),3) avg_p,
         round(min(hold_probability),3) min_p, round(max(hold_probability),3) max_p
  FROM {ML}.invoice_scored GROUP BY predicted_hold ORDER BY predicted_hold
"""))
