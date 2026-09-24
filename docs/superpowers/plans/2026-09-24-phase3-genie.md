# Accord — Phase 3: Genie Agent (G1) — Implementation Plan

> **FE Bar HARD GATE.** A **real Databricks Genie** over the governed gold tables, where a user asks
> natural-language questions and gets **SQL-backed answers.**
> **⚠️ The app's embedded chatbot (A6) does NOT satisfy this gate** — G1 is a real Genie space over
> the data. Planning-only: approach + curation + benchmark Q&A + verify. Design:
> [`../specs/2026-09-24-accord-3way-match-design.md`](../specs/2026-09-24-accord-3way-match-design.md).
>
> **Skills to load when building:** `databricks-core` → `databricks-genie-agents` (build/curate a
> Genie space) and/or `databricks-data-discovery`, `databricks-unity-catalog` (grants + descriptions).

**Goal:** Stand up a curated Genie space, **"Accord — AP 3-Way Match,"** over the gold match tables
so an AP lead can ask questions in plain English ("how much is on hold for price variance this
month?") and get correct, SQL-backed answers — and so I can demo NL analytics next to the app.

**Architecture:** Genie space scoped to a small, well-described set of gold tables
(`invoice_match_result` + `vendor_master` + any supporting dims), enriched with instructions,
table/column descriptions, synonyms, and example SQL. A benchmark question set is the acceptance
test.

**Tech stack:** Databricks Genie, Unity Catalog (descriptions/grants), SQL warehouse.

## Global constraints

- Scope Genie to **gold** only (governed, analyst-safe); no raw/PII.
- Curate deliberately — Genie quality is mostly **table/column descriptions + example queries +
  synonyms**, not luck.
- Benchmark answers are validated against **direct SQL on gold** (ground truth).
- Profile operator-chosen; never auto-select.

---

## Task G1: Genie space over gold + curated sample Q&A

**Files:**
- Create: `genie/src/accord_genie_space.md` (space config: instructions, table scope, synonyms,
  example SQL, benchmark set) — the human-readable spec of the space.
- Create: `genie/src/benchmark_questions.sql` (the ground-truth SQL each benchmark answer must match).
- Optionally: `genie/src/accord_genie_space.geniespace.json` if exporting/versioning the space.

**Interfaces:**
- Consumes: `gold_dev.invoice_match_result`, `silver_dev.vendor_master` (+ dims).
- Produces: a live Genie space + a versioned config + benchmark set.

**Approach:**
- [ ] Add tables to the space; write a **space instruction** ("This space answers AP 3-way-match
      questions. A line is on 'hold' when disposition='HOLD'. 'Auto-approved' = AUTO_APPROVED.
      'Rejected' is an analyst decision in the audit table. 'Supplier'='vendor'. $ = invoice_amount
      or amt_at_risk.").
- [ ] Rich **column descriptions** on `invoice_match_result` (disposition, reason_code, amt_at_risk,
      price_var_pct, etc.) and `vendor_master`.
- [ ] **Synonyms:** hold=exception=blocked; supplier=vendor; auto-approved=touchless=clean match;
      reason=root cause.
- [ ] **Example SQL** for 3–4 canonical patterns (by reason, by supplier, by month, $ sums).
- [ ] Grant the analyst group read on the space's tables.

**Benchmark questions (each must return an answer matching the ground-truth SQL):**

| # | NL question | Ground-truth SQL shape |
|---|---|---|
| 1 | How many invoice lines are on hold for price variance this month? | `WHERE disposition='HOLD' AND reason_code='PRICE_VAR' AND month(invoice_date)=…` count |
| 2 | Which suppliers have the highest exception rate? | `HOLD/total` grouped by vendor, ordered desc |
| 3 | What's the total $ on hold by reason? | `sum(amt_at_risk)` grouped by `reason_code` where HOLD |
| 4 | Auto-approved vs hold counts by month | count grouped by `disposition`, `month(invoice_date)` |
| 5 | Top 10 highest-$ held lines right now | `WHERE disposition='HOLD' ORDER BY amt_at_risk DESC LIMIT 10` |
| 6 | How many invoices did we receive last week? | distinct `invoice_id` where `invoice_date` in last week |
| 7 | Which vendor has the most duplicate-invoice holds? | `WHERE reason_code='DUP_INVOICE'` group by vendor |
| 8 | What share of lines auto-approved this quarter? | `AUTO_APPROVED / total` for the quarter |

**Verify:**
- [ ] Ask each benchmark question in Genie; confirm the returned number **matches** running the
      corresponding SQL in `benchmark_questions.sql` on gold.
- [ ] Confirm Genie shows the generated SQL (explainability) and uses the synonyms correctly.
- [ ] ≥ 7/8 correct on first pass; fix descriptions/examples for any miss and re-ask.

---

## Self-Review

- G1 is a **standalone gate** — verified independently of the app. The app's "Ask Accord" (A6) can
  embed this space, but the gate is the space itself answering the benchmark set.
- Genie accuracy is a curation outcome: if a question misses, the fix is a better column description,
  a synonym, or an example query — log which fix resolved which miss (good technical-roleplay detail).
- Keep the benchmark SQL in-repo so re-verification after a data refresh is one command.

**Exit criteria:** benchmark set ≥ 7/8 correct, SQL visible, synonyms working → G1 ✅. Then Phase 4.
