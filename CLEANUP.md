# Accord — Cleanup

Tear down Accord's workspace footprint when done (or to rebuild fresh). Operator supplies
`--profile <name>`; **never auto-select**. Order matters (dependents first).

```bash
PROFILE=<name>     # your workspace profile
CATALOG=accord_febar_catalog

# 1. App
databricks apps delete accord-ap-workbench --profile $PROFILE

# 2. Serving endpoint + UC model
databricks serving-endpoints delete accord-holdrecommender --profile $PROFILE
# (delete the UC model version(s) via Catalog Explorer or SDK: ${CATALOG}.ml.accord_holdrecommender)

# 3. Genie space — delete in the UI (Genie > space > settings)

# 4. Dashboard (if D1 built) — delete in the UI or via API

# 5. Pipeline + jobs (via the bundle)
databricks bundle destroy -t dev --profile $PROFILE

# 6. Data — the accord-febar workspace uses the FEVM-provided catalog `accord_febar_catalog`
#    (owned by the FEVM deployer SP), so do NOT drop the catalog. Drop the schemas you own instead,
#    or just let the FEVM workspace TTL expire / delete the whole deployment in go/fevm.
for s in gold silver bronze ml landing; do
  databricks experimental aitools tools query "DROP SCHEMA IF EXISTS ${CATALOG}.${s} CASCADE" --profile $PROFILE
done

# Or nuke the entire workspace deployment (removes everything at once):
#   go/fevm  ->  deployment accord-febar  ->  Delete   (Resource ID 01a0d48d-c3d9-77e9-ad2e-232f6373ad1e)
```

**Notes**
- `bundle destroy` removes pipeline/job/app resources defined in the DAB but not the catalog data or
  the Genie space (delete those explicitly).
- On this shared FEVM workspace, `CREATE/DROP CATALOG` may be denied (deployer-SP owns the catalog) —
  work at the schema level, which you own.
- Lakebase instance (if used for the decision/audit store, D-7) — delete separately.
- Keep the repo + `line_truth`/synthetic generator so you can regenerate everything reproducibly.
