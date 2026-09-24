# Accord — Phase 5: Optional Adds (D1, X1) — Implementation Plan

> **Optional / time-permitting.** These are **Exceeds levers**, not pass requirements — the build
> passes on Phases 0–4 + 6. Do these if the budget allows; they lift Product and Build+AI-Mindset
> from Meets toward Exceeds. Planning-only. Design:
> [`../specs/2026-09-24-accord-3way-match-design.md`](../specs/2026-09-24-accord-3way-match-design.md) §8;
> rubric [`../../RUBRIC.md`](../../RUBRIC.md).
>
> **Skills to load when building:** `databricks-core` → `databricks-aibi-dashboards` (D1);
> `databricks-ai-functions` + AI Gateway guidance + `databricks-model-serving` (X1).

**Goal:** Add a visual analytics surface (D1) and an **agentic act-layer** (X1) that generates the
grounded root-cause narrative + a vendor-dispute draft — directly serving the "reason why to hold"
requirement and the strongest "AI Mindset" signal.

## Global constraints

- **Grounded, not hallucinated.** X1 output must cite the **actual** match fields (prices, qtys,
  reason_code) from `invoice_match_result`; no invented numbers.
- Synthetic data only; no secrets; endpoints from config.
- Both consume **gold** — no new pipeline needed.

---

## Task D1: AI/BI exceptions dashboard *(optional)*

**Files:** `dashboard/src/accord_exceptions.lvdash.json`, `dashboard/resources/accord_dashboard.dashboard.yml`.

**Interfaces:** consumes `gold.invoice_match_result` (+ audit for rejected).

**Approach / widgets:**
- [ ] KPIs: touchless (auto-approve) match rate; total $ on hold; # open exceptions.
- [ ] Holds **by reason** (bar); holds **by supplier** (top N); **aging** of open holds; **$-at-risk**
      over time; disposition trend by **week/month/year**.
- [ ] Filters mirror the app (supplier, period, reason).

**Databricks Assistant / Designer prompt:**
```
Create an AI/BI dashboard over gold.invoice_match_result: KPI tiles for auto-approve rate, total
$ at risk, open exception count; bar of holds by reason_code; top-10 suppliers by exception rate;
line of $ at risk by month; a disposition trend with a week/month/year granularity control.
```

**Verify:** dashboard renders; auto-approve rate + $-at-risk match the gold SQL; filters work.

---

## Task X1: AI Gateway act-layer (root-cause narrative + vendor-dispute draft) *(optional)*

**Files:** `agents/src/rootcause_tool.py` (the tool/endpoint), `agents/resources/…` (wiring), called from app A5.

**Interfaces:** consumes one `invoice_match_result` row; returns `{narrative, dispute_email_draft}`.

**Approach:**
- [ ] Build a tool that takes a held line's structured fields and, via an AI Gateway–governed LLM
      endpoint (or `ai_query`), returns: (a) a **plain-language root-cause narrative** and (b) a
      **draft vendor-dispute email** / proposed GL correction.
- [ ] **Ground it:** pass the exact fields (po/inv price, qty ordered/received/billed, reason_code)
      and instruct the model to reference only those; template the numbers so they can't drift.
- [ ] Expose it to the app A5 panel; keep a rules-only fallback string if the endpoint is down.

**Assistant prompt (for the tool's LLM call):**
```
You are an AP assistant. Given these three-way-match facts for one invoice line: <fields>. Write (1)
a 2-3 sentence root-cause explanation of why the line is held, citing only the given numbers, and
(2) a short, professional vendor email requesting correction. Do not invent any figures.
```

**Verify:** for a `PRICE_VAR` line, the narrative states the correct PO vs invoice price and %; the
email references the right invoice/PO; no numbers appear that aren't in the input. Repeat for
`NO_RECEIPT` and `QTY_OVERBILL`.

---

## Self-Review

- D1 and X1 are **independent** of each other and of the pass criteria; either can be dropped under
  time pressure without breaking the build.
- X1 is the headline "AI Mindset / agentic" story for the roleplay — prioritize it over D1 if only
  one fits.
- Grounding discipline on X1 is the whole game: a hallucinated figure in a vendor email is a
  credibility (and, in real life, a compliance) problem — call this out proactively in the roleplay.

**Exit criteria:** whichever adds are attempted are ✅ and grounded/verified. Then Phase 6.
