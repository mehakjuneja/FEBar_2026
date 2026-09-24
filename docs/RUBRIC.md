# FE Bar Rubric — mapped to the Accord build

> The FE Bar AI validator scores **both the build and the roleplay** across four domains, each rated
> **Below / Meets / Exceeds**. **You pass when all four are Meets-or-above and the hard gates are
> met.** Meets is the bar; Exceeds is upside. This file translates each domain into concrete,
> checkable must-haves for Accord, plus the Exceeds "level-up" targets — so I always know what
> "done and defensible" looks like. Detail lives in go/fe-bar-faq; this is my working copy.

## Hard gates (must be true or the build can't pass)

- [ ] **Lakeflow pipeline** — a self-built SDP doing raw → silver → gold (`read_files`, streaming
      tables, and/or materialized views) producing the governed match tables. *(Phase 1)*
- [ ] **Real ML model** — an MLflow model **behind a serving endpoint** (not a heuristic). *(Phase 2)*
- [ ] **Genie agent** — a real Databricks Genie over the governed gold tables (the app's chat does
      **not** satisfy this by itself). *(Phase 3)*
- [ ] **One integrated end-to-end journey** — feeds → match → score → analyst decision → audit,
      not disconnected demos.
- [ ] **Customer-safe** — synthetic data only; no secrets (scanner-clean).
- [ ] **Own work** — commit authorship is mine; attestation signed; decisions defensible in roleplay.

---

## Domain 1 — Industry

*Can you situate the solution in a real industry with real economics and stakeholders?*

**Meets (target):**
- [ ] Names the industry precisely: **Retail / CPG — fragrance & beauty**, and the function:
      **Accounts Payable / procure-to-pay**.
- [ ] Frames the real pain: manual 3-way match is slow and leaks money (duplicate invoices, price
      variance above PO, billing for un-received goods, maverick spend), with audit exposure.
- [ ] Quantifies value in the customer's terms: invoice-exception cycle time, % touchless match,
      recovered $ from blocked overbilling, analyst capacity, DPO/discount-capture impact.
- [ ] Uses correct domain vocabulary: PO, GR/ASN, invoice, 3-way vs 2-way match, tolerance, UOM,
      remit-to, exception/hold, GL coding, vendor master.

**Exceeds (level-up):**
- Ties to fragrance-retail specifics (seasonal launches, tester/GWP units, high-value SKUs,
  serialized/allocated fragrances) and how they stress the match.
- Contrasts against how an ERP (SAP/Coupa/Oracle) handles this today and where Databricks adds
  the AI + governance layer on top.

## Domain 2 — Product

*Do you use the right Databricks capabilities, correctly and idiomatically?*

**Meets (target):**
- [ ] **Lakeflow / Spark Declarative Pipelines** for ingestion + transformation (`read_files`,
      streaming tables, materialized views).
- [ ] **Unity Catalog** governance: catalog/schema layout, lineage across bronze→silver→gold,
      tolerances/config as governed tables, and at least one access-control or masking touch
      (vendor bank/remit data is a natural candidate).
- [ ] **MLflow + Model Serving**: tracked experiment, UC-registered model, live serving endpoint.
- [ ] **Genie** over governed tables with sample NL Q&A that returns SQL-backed answers.
- [ ] **Databricks Apps** for the analyst workbench.

**Exceeds (level-up):**
- **AI/BI dashboard** (Phase 5 D1), **AI Gateway** act-layer tool (Phase 5 X1), Lakehouse
  Monitoring on the match/feature tables, and clean DAB deployment across dev/prod targets.

## Domain 3 — Build + AI Mindset

*Is it one coherent, well-reasoned system — and did you make real decisions?*

**Meets (target):**
- [ ] End-to-end journey is wired and runs: a landed invoice flows through match → score → appears
      in the analyst queue with a recommendation + reason → decision is logged.
- [ ] **AI is load-bearing, not decorative:** the model drives the recommendation; the root-cause
      reason is generated/explained, not hardcoded.
- [ ] **Documented trade-offs** (in the spec): rules-vs-ML for the match, tolerance thresholds,
      approve/hold decision threshold and the cost of false approves vs false holds, feature
      choices, batch-vs-realtime scoring.
- [ ] Reproducible: DAB-deployable, parameterized (no hardcoded workspace literals), verifiable.

**Exceeds (level-up):**
- An **agentic** step (act-layer: draft the vendor-dispute note / propose a GL correction via AI
  Gateway), human-in-the-loop framing, feedback loop from analyst decisions back into the model,
  and explicit handling of model confidence / abstention.

## Domain 4 — Customer Skills (the roleplay)

*Can you present and defend it to a business and a technical stakeholder?* Scored on **demo setup,
value communication, reading the room, professionalism.** ~20–30 min.

**Meets (target):**
- [ ] Clean demo setup and narrative arc: problem → solution → value → ask.
- [ ] **Business stakeholder** (Controller / VP Finance / AP Director): leads with outcomes and $,
      not features; handles "why not just our ERP?" and "what's the ROI?".
- [ ] **Technical stakeholder** (Head of Data Platform / ERP-integration lead): can go deep on
      architecture, governance, model, and how it fits their stack.
- [ ] Reads the room — adjusts depth per persona; handles objections without getting defensive.

**Exceeds (level-up):**
- Crisp discovery-style framing, a confident POV on rollout/change-management for AP analysts, and
  a clear "what we'd measure in a POC" close.

See `docs/presentation/` for the deck outline and per-persona prep.

---

## Self-scoring checklist (run before each submission)

| Domain | Meets? | Evidence (file / object) | Exceeds opportunity taken? |
|---|---|---|---|
| Industry | ☐ | spec §1, deck | ☐ |
| Product | ☐ | pipeline/, ml/, genie/, app/ | ☐ D1 / X1 |
| Build + AI Mindset | ☐ | end-to-end run + spec §Decisions | ☐ act-layer |
| Customer Skills | ☐ | roleplay dry-run | ☐ |
| **Hard gates** | ☐ | BUILD_TRACKER | — |
