# Databricks notebook source
# MAGIC %md
# MAGIC # F1 — Unity Catalog setup (Accord)
# MAGIC
# MAGIC Creates the governed home for the Accord 3-way match build:
# MAGIC catalog → medallion schemas → landing `feeds` volume + feed folders → baseline grants.
# MAGIC
# MAGIC **Idempotent** — safe to re-run. Reads `catalog` / `schema_suffix` from widgets so the
# MAGIC same notebook works across workspaces (no hardcoded literals).
# MAGIC
# MAGIC Deployed home (FEVM `accord-febar` workspace): catalog `accord_febar_catalog`, no suffix.
# MAGIC See `docs/superpowers/plans/2026-09-24-phase0-foundation.md` (Task F1).

# COMMAND ----------
# MAGIC %md ## Parameters

# COMMAND ----------
dbutils.widgets.text("catalog", "accord_febar_catalog", "Catalog")
dbutils.widgets.text("schema_suffix", "", "Schema suffix (empty here; _dev in a dev/prod split)")

CATALOG = dbutils.widgets.get("catalog")
SUFFIX = dbutils.widgets.get("schema_suffix")

SCHEMAS = ["landing", "bronze", "silver", "gold", "ml"]
LANDING_SCHEMA = f"landing{SUFFIX}"
VOLUME = "feeds"  # managed volume `feeds` inside the landing schema
FEED_DIRS = ["po", "gr", "invoice"]

print(f"Catalog       : {CATALOG}")
print(f"Schema suffix : '{SUFFIX}'")
print(f"Schemas       : {[s + SUFFIX for s in SCHEMAS]}")

# COMMAND ----------
# MAGIC %md ## 1. Catalog + medallion schemas
# MAGIC On a shared FEVM metastore you don't have `CREATE CATALOG` and the catalog is pre-provisioned,
# MAGIC so we *try* to create it but tolerate `PERMISSION_DENIED` — you own the schemas within it.

# COMMAND ----------
try:
    spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
    print(f"  ✓ catalog {CATALOG} (created or already present)")
except Exception as e:
    if "PERMISSION_DENIED" in str(e) or "CREATE CATALOG" in str(e):
        print(f"  ℹ catalog {CATALOG} is pre-provisioned (no CREATE CATALOG on this metastore) — using it.")
    else:
        raise

for s in SCHEMAS:
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{s}{SUFFIX}")
    print(f"  ✓ schema {CATALOG}.{s}{SUFFIX}")

# COMMAND ----------
# MAGIC %md ## 2. Landing `feeds` volume + feed folders
# MAGIC The ERP/EDI-style feeds land here; Phase 1 (P1) picks them up with `read_files` / Auto Loader.
# MAGIC Path: `/Volumes/<catalog>/landing<suffix>/feeds/{po,gr,invoice}`.

# COMMAND ----------
spark.sql(f"CREATE VOLUME IF NOT EXISTS {CATALOG}.{LANDING_SCHEMA}.{VOLUME}")
volume_root = f"/Volumes/{CATALOG}/{LANDING_SCHEMA}/{VOLUME}"

for d in FEED_DIRS:
    path = f"{volume_root}/{d}"
    dbutils.fs.mkdirs(path)
    print(f"  ✓ {path}")

# COMMAND ----------
# MAGIC %md ## 3. Baseline grants (adjust group names to your workspace)
# MAGIC Give downstream consumers read access to `gold`. Vendor remit/bank-like columns in `silver`
# MAGIC are the natural target for a UC column mask later (Product-domain governance story) — noted,
# MAGIC not applied here.

# COMMAND ----------
# NOTE: `account users` is a convenient demo grantee in a personal FEVM workspace.
# Swap for a real analyst group in a shared/prod setting.
ANALYST_GROUP = "account users"
try:
    spark.sql(f"GRANT USE CATALOG ON CATALOG {CATALOG} TO `{ANALYST_GROUP}`")
    spark.sql(f"GRANT USE SCHEMA ON SCHEMA {CATALOG}.gold{SUFFIX} TO `{ANALYST_GROUP}`")
    spark.sql(f"GRANT SELECT ON SCHEMA {CATALOG}.gold{SUFFIX} TO `{ANALYST_GROUP}`")
    print(f"  ✓ granted read on {CATALOG}.gold{SUFFIX} to `{ANALYST_GROUP}`")
except Exception as e:
    print(f"  ⚠ grant skipped ({e}); set ANALYST_GROUP to a group you can grant to.")

# COMMAND ----------
# MAGIC %md ## 4. Verify

# COMMAND ----------
print("Schemas:")
display(spark.sql(f"SHOW SCHEMAS IN {CATALOG}"))
print("Feed folders:")
for d in FEED_DIRS:
    print(f"  {volume_root}/{d} -> {dbutils.fs.ls(f'{volume_root}/{d}')}")
print("\nF1 complete. Next: F2 (10_generate_documents.py).")
