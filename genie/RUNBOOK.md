# genie/ — RUNBOOK

**Phase 3 — FE Bar HARD GATE.** A real Genie space over governed gold tables. Plan:
[`../docs/superpowers/plans/2026-09-24-phase3-genie.md`](../docs/superpowers/plans/2026-09-24-phase3-genie.md)

> ⚠️ The app's embedded chat (A6) does **not** satisfy this gate — **G1 is the real Genie space.**

| Object | File | Purpose |
|---|---|---|
| G1 | `src/accord_genie_space.md` | space config: scope, instructions, synonyms, example SQL |
| G1 | `src/benchmark_questions.sql` | ground-truth SQL each benchmark answer must match |

**Skills:** databricks-core → databricks-genie-agents (and/or databricks-data-discovery),
databricks-unity-catalog.

**Scope:** `gold_dev.invoice_match_result` + `silver_dev.vendor_master`.

**Verify:** the 8 benchmark NL questions return answers matching the SQL on gold (target ≥ 7/8); SQL
is visible; synonyms (hold=exception, supplier=vendor) work.
