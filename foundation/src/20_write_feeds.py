# Databricks notebook source
# MAGIC %md
# MAGIC # F3 — Write landing feeds (Accord)
# MAGIC
# MAGIC Exports the F2 staging tables to files on the landing volume, partitioned by month, so they
# MAGIC arrive like ERP/EDI extracts and Phase 1 (P1) can ingest them with `read_files` / Auto Loader:
# MAGIC PO + GR as **CSV**, invoices as **JSON** (mixed formats on purpose).
# MAGIC
# MAGIC Reads `${catalog}.landing${suffix}` tables; writes to
# MAGIC `/Volumes/${catalog}/landing${suffix}/feeds/{po,gr,invoice}`.
# MAGIC See `docs/superpowers/plans/2026-09-24-phase0-foundation.md` (Task F3).

# COMMAND ----------
# MAGIC %md ## Parameters

# COMMAND ----------
dbutils.widgets.text("catalog", "accord_febar_catalog", "Catalog")
dbutils.widgets.text("schema_suffix", "", "Schema suffix")

CATALOG = dbutils.widgets.get("catalog")
SUFFIX = dbutils.widgets.get("schema_suffix")
LANDING = f"{CATALOG}.landing{SUFFIX}"
FEEDS = f"/Volumes/{CATALOG}/landing{SUFFIX}/feeds"

from pyspark.sql import functions as F
print(f"Source schema: {LANDING}")
print(f"Feeds root   : {FEEDS}")

# COMMAND ----------
# MAGIC %md ## Write each source, partitioned by month
# MAGIC Partitioning by `_ym` yields multiple files (one set per month) — good for demonstrating
# MAGIC incremental Auto Loader pickup in P1.

# COMMAND ----------
def write_feed(table, date_col, fmt, subdir):
    df = spark.table(f"{LANDING}.{table}").withColumn("_ym", F.date_format(F.col(date_col), "yyyy-MM"))
    path = f"{FEEDS}/{subdir}"
    writer = df.write.mode("overwrite").partitionBy("_ym")
    if fmt == "csv":
        writer.option("header", "true").csv(path)
    else:
        writer.json(path)
    n = df.count()
    print(f"  ✓ {table} -> {path} ({fmt}, {n} rows across months)")
    return n

write_feed("po_line",      "po_date",      "csv",  "po")
write_feed("gr_line",      "receipt_date", "csv",  "gr")
write_feed("invoice_line", "invoice_date", "json", "invoice")

# COMMAND ----------
# MAGIC %md ## Verify — files landed

# COMMAND ----------
for sub in ["po", "gr", "invoice"]:
    files = dbutils.fs.ls(f"{FEEDS}/{sub}")
    months = [f.name for f in files if f.name.startswith("_ym=")]
    print(f"  {sub}: {len(months)} monthly partitions, e.g. {months[:3]}")
print("\nF3 complete. Phase 0 done — feeds are on the volume for P1 (Lakeflow ingestion).")
