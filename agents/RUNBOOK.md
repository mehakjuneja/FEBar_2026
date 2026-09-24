# agents/ — RUNBOOK  *(optional — Exceeds lever)*

**Phase 5 (optional).** AI Gateway act-layer: grounded root-cause narrative + vendor-dispute draft.
Plan: [`../docs/superpowers/plans/2026-09-24-phase5-optional-adds.md`](../docs/superpowers/plans/2026-09-24-phase5-optional-adds.md)

| Object | File | Purpose |
|---|---|---|
| X1 | `src/rootcause_tool.py` | given a held line → `{narrative, dispute_email_draft}`, called from app A5 |

**Skills:** databricks-core → databricks-ai-functions + AI Gateway guidance, databricks-model-serving.

**Grounding is the whole game:** the output must cite only the real match fields (PO vs invoice
price, qtys, reason_code) — no invented numbers. Strongest "AI Mindset" signal; directly serves the
"reason why to hold" requirement.

**Verify:** for PRICE_VAR / NO_RECEIPT / QTY_OVERBILL lines, the narrative + email reference the
correct figures and invent nothing.
