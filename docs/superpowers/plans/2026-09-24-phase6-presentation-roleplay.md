# Accord — Phase 6: Presentation & AI Roleplay (R1–R3) — Implementation Plan

> The **second scored half** of the FE Bar. After submitting the build, you present to **two AI
> customer personas** (business + technical) for ~20–30 min, scored on **demo setup, value
> communication, reading the room, professionalism** (Domain 4). If you pass the build but not the
> roleplay, only the roleplay carries over to retake. Planning-only: outline + prep + Q&A bank.
> Design defense material: spec [§10 decision log](../specs/2026-09-24-accord-3way-match-design.md).
>
> **Skills to load when building:** `fe-workflows:humanize` (make the narrative sound like me),
> `fe-google-tools:google-slides` or `markdown-to-pdf` (export the deck to the submitted PDF).

**Goal:** A deck + rehearsed narrative that lands the value in the customer's terms and lets me
**defend every design decision** to both a business and a technical stakeholder.

## Global constraints

- The deck is submitted as a **PDF** (attach the file, not a link).
- Lead with **outcomes and $**, not features. Features serve the story.
- The **live app is the demo spine**: Summary → Reconciliation (filter + bulk approve) → Exceptions
  → Line detail (AI recommendation + root cause) → Ask Accord (Genie).
- Every claim must be defensible from the spec decision log — no hand-waving.

---

## Task R1: Presentation deck (submitted PDF)

**Files:** `docs/presentation/accord_deck_outline.md` → export to `docs/presentation/accord_deck.pdf`.

**Slide-by-slide outline (narrative arc):**
1. **Title** — Accord: automated 3-way match + AI-assisted invoice reconciliation for Maison Lumière.
2. **The problem** — manual 3-way match in AP: slow, high-touch, leaks money (duplicates, price creep,
   billing for un-received goods), audit exposure. (Industry framing.)
3. **The stakes ($)** — exception cycle time, % touchless, $ leakage — order-of-magnitude for a
   prestige-fragrance retailer.
4. **The idea** — ingest PO + GR + Invoice, match them, recommend Approve/Hold with a root cause,
   let analysts clear the rest fast.
5. **Live demo** — the app spine (5 clicks): summary → filter to a supplier/month → bulk-approve
   clean-ish holds → open a price-variance line → show AI recommendation + root cause → ask Genie a
   question.
6. **How it works** — the architecture diagram (feeds → Lakeflow → gold match → model/serving →
   Genie → app), one slide.
7. **The AI** — the model (Approve/Hold + confidence), grounded root-cause narrative (X1), and why
   it's trustworthy (rules + ML + human-in-the-loop).
8. **Governance & trust** — Unity Catalog lineage, synthetic data, masking of vendor bank/remit,
   audit trail.
9. **Value recap** — outcomes mapped to metrics; what a 6-week POC would measure.
10. **Ask / next steps** — the POC proposal.

**Verify:** deck exports to PDF; a peer can follow the arc without narration; every slide maps to a
rubric domain (Industry 2–3, Product 6–8, Build+AI 4–7, Customer Skills throughout).

---

## Task R2: Business-stakeholder roleplay prep (Controller / VP Finance / AP Director)

**Files:** `docs/presentation/roleplay_business.md`.

**Approach:**
- [ ] Open with outcomes: **touchless-match rate ↑, exception cycle time ↓, recovered $ from
      overbilling/duplicates, analyst capacity freed, DPO / early-pay-discount capture.**
- [ ] Translate every feature into a business result; avoid Databricks jargon with this persona.
- [ ] Have a crisp POC-success definition (what we'd measure in 6 weeks).

**Anticipated objections → answers:**
- *"Why not just our ERP / Coupa / SAP for matching?"* → ERPs do rules-based 2/3-way match; Accord
  adds AI prioritization + explainable root cause + analyst-productivity workflow + governed
  analytics on top, without ripping out the ERP.
- *"What's the ROI / how fast?"* → leakage recovery + analyst hours; POC quantifies on their data.
- *"How do we trust the AI?"* → rules decide the exception; ML only prioritizes; human approves;
  full audit trail; grounded explanations (no invented numbers).
- *"Change management for analysts?"* → it augments, not replaces; bulk actions clear the easy
  backlog so analysts focus on judgment calls.

**Discovery questions to ask them:** monthly invoice/line volume, current touchless %, avg exception
cycle time, known leakage categories, audit pain points, ERP in place.

---

## Task R3: Technical-stakeholder roleplay prep (Head of Data Platform / ERP-integration lead)

**Files:** `docs/presentation/roleplay_technical.md`.

**Approach / deep-dive readiness:**
- [ ] **Architecture:** Lakeflow SDP (streaming tables + MVs), medallion, gold `invoice_match_result`
      as the contract; DAB dev/prod.
- [ ] **Governance:** UC lineage bronze→silver→gold, governed `match_config` tolerances, column mask
      on vendor remit/bank fields, audit table.
- [ ] **The model:** features (spec §6), **leakage guard** (rules outputs excluded from features,
      `line_truth` never a feature), **threshold cost-asymmetry** (false-approve pays bad money →
      tune toward Hold recall), SHAP explainability, MLflow → UC model → serving endpoint.
- [ ] **Genie** curation and why it's separate from the app chatbot.
- [ ] **Fit to their stack:** file feeds today → **Lakeflow Connect** for real SAP/Coupa; serving +
      AI Gateway governance; how it scales.

**Anticipated technical objections → answers:**
- *"Is the model just re-learning your rules?"* → rules produce the code; ML predicts hold-likelihood
  from independent features; leakage explicitly guarded; show the off-diagonal edge cases.
- *"Why SDP over plain jobs?"* → declarative, incremental, lineage + expectations for free (D-6).
- *"How does this connect to our real ERP?"* → swap file feeds for Lakeflow Connect; match logic
  unchanged.
- *"Data security / PII?"* → synthetic here; UC masking + row filters for real remit/bank data;
  no secrets in the app.

---

## Mock Q&A bank (rehearse both personas)

| # | Persona | Question | Model answer (from spec decision log) |
|---|---|---|---|
| 1 | Biz | What does "on hold" cost us today? | Analyst hours + missed discounts + late leakage; POC quantifies. |
| 2 | Biz | Can we trust bulk-approve? | Only lines the model + rules flag as low-risk; audit logs every action; reversible. |
| 3 | Biz | Where's the fast win? | Duplicate + price-variance holds — highest $ recovery, clearest rules. |
| 4 | Biz | Replace our AP team? | No — augment; clear easy backlog, focus analysts on judgment. |
| 5 | Tech | Batch or real-time scoring? | Both — batch to gold for the queue/dashboard; real-time serving call in line detail (M4). |
| 6 | Tech | Model family + why? | GBT baseline (D-2): strong tabular perf + easy SHAP; LR considered for interpretability. |
| 7 | Tech | How do you set tolerances? | Governed `match_config` (D-1), live-tunable; 2% price / exact qty default. |
| 8 | Tech | Leakage risk in the model? | line_truth + rule outputs kept out of features; verified on off-diagonal cases. |
| 9 | Tech | Why Genie separate from the app chat? | The gate requires a real Genie over governed tables; the app embeds it but isn't it. |
| 10 | Tech | Multi-currency / tax? | Out of scope for the prototype (spec §11); a named extension. |
| 11 | Biz | What's the POC ask? | 6 weeks on a data sample; measure touchless %, cycle time, $ recovered. |
| 12 | Tech | How does it deploy / promote? | DAB dev→prod targets, parameterized, CI-friendly. |
| 13 | Biz | What if the AI is wrong? | Human-in-the-loop; rules gate; audit + easy reversal; confidence shown. |
| 14 | Tech | How is root cause generated? | Rules give the code; X1 (AI Gateway) writes a grounded narrative citing only real fields. |
| 15 | Both | Why fragrance retail specifically? | Seasonal launches, testers/GWP zero-price units, high-value SKUs stress the match — realistic, relatable. |

---

## Self-Review

- The roleplay is scored on **setup, value communication, reading the room, professionalism** —
  rehearse switching register between the two personas.
- Time-box a **dry run to 25 min**; confirm the demo spine works live and degrades gracefully if a
  serving/AI call is slow.
- Every answer traces to a logged decision — keep the spec §10 table open during prep.

**Verify:** a timed dry-run (record it) hits all four Customer-Skills sub-scores; the deck PDF is
attached-ready; I can answer the full Q&A bank without notes.

**Exit criteria:** deck PDF ready; both persona preps rehearsed; Q&A bank fluent → ready to submit.
