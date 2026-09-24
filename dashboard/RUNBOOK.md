# dashboard/ — RUNBOOK  *(optional — Exceeds lever)*

**Phase 5 (optional).** AI/BI exceptions dashboard over gold. Plan:
[`../docs/superpowers/plans/2026-09-24-phase5-optional-adds.md`](../docs/superpowers/plans/2026-09-24-phase5-optional-adds.md)

| Object | File | Purpose |
|---|---|---|
| D1 | `src/accord_exceptions.lvdash.json` | holds by reason/supplier, aging, $-at-risk, touchless rate, trend |
| D1 | `resources/accord_dashboard.dashboard.yml` | DAB dashboard resource |

**Skills:** databricks-core → databricks-aibi-dashboards.

**Not required to pass** — high visual payoff for the R1 deck. **Verify:** auto-approve rate +
$-at-risk match the gold SQL; filters (supplier/period/reason) work.
