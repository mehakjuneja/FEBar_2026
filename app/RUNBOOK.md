# app/ — RUNBOOK

**Phase 4.** Invoice Reconciliation Workbench (Databricks App) — the integrated demo surface. Plan:
[`../docs/superpowers/plans/2026-09-24-phase4-app.md`](../docs/superpowers/plans/2026-09-24-phase4-app.md)

| Object | Page | Purpose |
|---|---|---|
| A1 | scaffold | auth, gold reads, serving client, decision/audit store |
| A2 | **Summary** | # suppliers, invoices by week/month/year, dispositions (auto-approved/hold/rejected) $ |
| A3 | **Reconciliation** | not-auto-approved queue; filters (supplier/year/month/week/reason/$); **bulk approve/reject** |
| A4 | **Exceptions** | what wasn't approved and **why**, grouped by reason & supplier |
| A5 | **Line detail** | PO/GR/Invoice side-by-side + AI recommendation + root cause |
| A6 | decisions/audit/Genie | write-back + audit trail + embedded "Ask Accord" |

**Skills:** databricks-core → fe-databricks-tools:databricks-apps (or databricks-apps /
databricks-apps-python), databricks-model-serving, databricks-lakebase (if D-7), and
fe-specialized-agents:web-devloop-tester for the local devloop.

**Decisions to make at kickoff:** D-4 framework (React+FastAPI vs Streamlit), D-7 state store
(Lakebase vs Delta).

**Verify:** summary tiles = gold aggregates; a filter narrows the queue; bulk-approve N writes N
audit rows; line detail renders a live serving recommendation. App: `accord-ap-workbench`.
