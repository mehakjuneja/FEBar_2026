# Accord — Cleanup

Tear down Accord's workspace footprint when done (or to rebuild fresh). Operator supplies
`--profile <name>`; **never auto-select**. Order matters (dependents first).

```bash
PROFILE=<name>     # your workspace profile
CATALOG=febar_accord_dev

# 1. App
databricks apps delete accord-ap-workbench --profile $PROFILE

# 2. Serving endpoint + UC model
databricks serving-endpoints delete accord-holdrecommender --profile $PROFILE
# (delete the UC model version(s) via Catalog Explorer or SDK: ${CATALOG}.ml_dev.accord_holdrecommender)

# 3. Genie space — delete in the UI (Genie > space > settings)

# 4. Dashboard (if D1 built) — delete in the UI or via API

# 5. Pipeline + jobs (via the bundle)
databricks bundle destroy -t dev --profile $PROFILE

# 6. Data (catalog) — LAST, and only if you really mean it
# databricks catalogs delete $CATALOG --force --profile $PROFILE
```

**Notes**
- `bundle destroy` removes pipeline/job/app resources defined in the DAB but not the catalog data or
  the Genie space (delete those explicitly).
- Lakebase instance (if used for the decision/audit store, D-7) — delete separately.
- Keep the repo + `line_truth`/synthetic generator so you can regenerate everything reproducibly.
