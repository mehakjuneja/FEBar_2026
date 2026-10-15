# Accord — Platform Whiteboard (draw-along)

> **What this is:** a presenter's whiteboard for the **FY27 Field Onboarding Platform Whiteboard**
> exercise, told through the **Accord** build. You tell the *Databricks platform* story (what the
> onboarding rubric scores — governance, Lakeflow, ML/serving, Genie, Apps/Lakebase) using **one
> concrete build you actually made**: AP three-way match for Maison Lumière.
>
> Follows the deck's **Tips & Tricks** (slide 28): boxes are OK, build it up as you talk, more
> arrows/symbols than words, start and end where your *story* makes sense, use C‑O‑L‑O‑R‑S.
> Pairs with `roleplay-guide.md` (the live Q&A script) — this is the drawing.

---

## The palette (deck's C-O-L-O-R-S, slide 28 tip #4)

| Marker | Hex | Use it for |
|---|---|---|
| **Ink / teal** | `#1b3139` | structure: source docs, pipeline frame, the app |
| **Orange‑red** | `#ff5f46` | the pain + **the match moment** (the hero beat) |
| **Green** | `#00a972` | value / auto‑approved / money saved |
| **Amber** | `#ffab00` | **on hold** — exceptions needing a human |
| **Dark red** | `#98102a` | **rejected** — hard fails |
| **Blue** | `#4359ff` | AI/ML: the model, serving, Genie |
| **Gov blue** | `#2272b4` | the Unity Catalog + Lakeflow foundation band |
| Board | `#f9f7f4` | off-white background |

---

## The layout (left → right story)

```
 ┌─ THE PAIN ─┐      ┌──────────── THE BUILD (one Lakeflow pipeline) ───────────┐   ┌─ THE PAYOFF ─┐

  AP analyst,                 PO ┐
  Maison Lumière       Goods Rcpt ┼─►  BRONZE  ─►  SILVER  ─►   GOLD            ─►   AUTO-APPROVE
  "which of these       Invoice ┘    raw ingest   conform     ★ 3-WAY MATCH ★         clean lines
   10k lines do          (3 docs    Auto Loader  +match_config  disposition /         (green $)
   we pay?               that must                             reason_code /
   where's the           agree)                                amt_at_risk        │  BULK-CLEAR
   leak?" ($ at risk)                                             │               │  the safe holds
      (orange-red)                                                │               │  (amber → green)
                                        ┌─────────────────────────┼───────┐       │
                                        ▼                         ▼       ▼       │  ANALYST FOCUS
                                   ★ GENIE ★              ★ ML MODEL ★   APP:     │  on real
                                   "ask the data"         Hold rec  ─►  Invoice   │  exceptions only
                                   in English             + SERVING    Recon      │  (dark red = reject)
                                   (blue)                 endpoint     Workbench  │
                                                          (blue)       Summary ·  └─► faster close,
                                                                       Review ·       less leakage,
                                                                       Exceptions     clean audit
                                                                       (ink)          (green)

  └──────────────── UNITY CATALOG governance  +  Lakeflow (self-built, serverless) ────────────────┘
                     one catalog: accord_febar_catalog · landing→bronze→silver→gold→ml   (gov blue)
```

★ = the **three FE Bar hard gates**: self-built **Lakeflow pipeline**, real **model + serving
endpoint**, real **Genie** over governed tables.

---

## Draw order (build it up as you talk)

Draw one block at a time — don't pre-draw the whole thing. Each step: **draw it → say the line.**

1. **The pain (orange-red), far left.** Draw a stick AP analyst behind a tall stack of paper.
   > *"Maison Lumière's AP team gets ~10,000 invoice lines a month. Someone has to confirm each one
   > against what we ordered and what we received before we pay. It's manual, it's slow, and that's
   > where money leaks — overbilling, duplicates, price creep."*

2. **Three source docs (ink), feeding in.** Draw PO, Goods Receipt, Invoice as three little pages
   joining into one arrow.
   > *"Three documents have to agree: the Purchase Order, the Goods Receipt, and the Invoice. That's
   > the three-way match."*

3. **The pipeline frame (gov blue band across the bottom).** Draw the long foundation band first, label
   it **Unity Catalog + Lakeflow**.
   > *"Everything sits on one governed foundation — Unity Catalog for governance, Lakeflow for the
   > pipeline. One catalog, lineage end to end, no copies."* **(platform: governance + open lakehouse)**

4. **Bronze → Silver → Gold (ink boxes on the band).** Draw three boxes left to right with arrows.
   > *"Raw feeds land in Bronze with Auto Loader, get conformed in Silver — including an editable
   > tolerance config the business owns — and..."*

5. **★ THE MATCH (orange-red star on Gold) — the hero beat.** Big orange-red burst on the Gold box.
   > *"...and in Gold, the three-way match runs. Every line gets a disposition — auto-approved or
   > held — a reason code, and a dollars-at-risk number. This one table is the heart of it."*
   > **(platform: Lakeflow Declarative Pipeline — hard gate #1)**

6. **★ The model + serving (blue), branching up from Gold.** Draw a brain/box → endpoint.
   > *"Rules tell you *what* broke. A gradient-boosted model adds *how likely this is a real problem*
   > — a hold-likelihood score — served behind a real endpoint the app calls live."*
   > **(platform: ML + Model Serving — hard gate #2)**

7. **★ Genie (blue), branching up from Gold.** Draw a lamp.
   > *"And because it's all governed tables, finance can just ask in plain English — 'how many lines
   > are on hold for price variance?' — and get a trustworthy answer. That's Genie."*
   > **(platform: Genie / natural-language BI — hard gate #3)**

8. **The app (ink): Invoice Reconciliation Workbench.** Draw three stacked screens: Summary,
   Review, Exceptions.
   > *"Analysts work in one app: a Summary of the whole book, a Reconciliation page where they filter
   > and **bulk-approve** the safe holds, and an Exceptions page for what/why."* **(platform: Databricks Apps)**

9. **The payoff (green), far right — end the story here.** Draw three outcome arrows.
   > *"So the clean lines auto-approve, the safe holds clear in a batch, and analysts spend their day
   > only on the real exceptions — ranked by dollars at risk. Faster close, less leakage, and every
   > decision is audited. That's the three-way match, built on the Databricks platform, end to end."*

**C-O-L-O-R-S recap:** pain + match = orange-red; approved/value = green; hold = amber; reject =
dark red; AI (model, Genie) = blue; foundation = gov blue. Keep the ink for structure.

---

## Databricks messaging alignment (go/pitchdeck, FY27 — updated Jul 2026)

The onboarding rubric scores **how consistent your whiteboard is with current corporate + product
messaging.** Accord fits it almost perfectly — it's a live example of the **Open Data + AI Platform**
turning a department into part of the **Agentic Enterprise**. Use the exact vocabulary below.

**Umbrella line (say it once, early):**
> *"Accord is one example of the Open Data + AI Platform — data engineering, ML, BI, and the app on a
> single governed platform. It's exactly the kind of departmental process you automate on the way to
> an Agentic Enterprise."*

**The 4 C's** — go/pitchdeck frames these as *"the mandatory criteria to build a successful enterprise
AI strategy."* Land each one on a specific box:

| Pillar | Current corporate phrasing | Where it lands in Accord | Say this |
|---|---|---|---|
| **Context** | *"Connecting AI to data is difficult."* | Genie + the model sit on **governed Gold** with business semantics (`match_config`) + lineage | *"The model and Genie aren't guessing — they run on governed tables with business semantics and lineage. That's **Context**."* |
| **Control** | *"Controlling AI and data use is required."* | **Unity Catalog** governs tables + model + Genie; the app **audits every approve/reject** | *"Every table, the model, and every analyst decision is governed and audited in Unity Catalog. That's **Control**."* |
| **Cost** | *"Optimizing cost is becoming essential."* | **touchless match** removes manual labor; **serverless** removes idle infra; queue ranked by **$ at risk** | *"Auto-approving clean lines removes the manual cost, serverless removes idle infra, and we recover leaked spend. That's **Cost**."* |
| **Choice** | *"Avoiding lock-in is key for innovation."* | **open formats** (Delta + Iceberg) on your object storage; any cloud / any model | *"It's open — Delta and Iceberg on storage you own, swap clouds or models freely. That's **Choice** — zero lock-in."* |

**Product-level terms** (say the proper noun, not a generic synonym):

| Term | Current phrasing | Accord beat |
|---|---|---|
| **Unity Catalog / Unified Governance** | *"Unified data + AI governance for all assets — one catalog for tables, files, models, agents."* | the **gov-blue foundation band**: one catalog governs the data **and** the model **and** Genie |
| **Open Formats** | *"Delta + Iceberg, unified — you own your data, zero lock-in."* | the open lakehouse under the pipeline |
| **Lakehouse** | *"Open Data+AI platform; sub-second SQL."* | Bronze→Silver→Gold on the lakehouse |
| **Lakebase** | *"Serverless Postgres on open lake storage; instant branching, lower TCO."* | *(optional beat)* analyst **decisions + audit write to Lakebase** — operational + analytical on one platform |
| **Unified / Simple** | *"One platform, not stitched tools; declarative + serverless."* | whole board = one platform; **declarative Lakeflow**, serverless, one app |

**Close on the FY27 transformation arc** (go/pitchdeck's 3 phases) — it makes Accord sound strategic,
not like a one-off:
> *"This is **Phase 2 — Automate Business Processes**: a departmental workflow, AP three-way match,
> automated on the platform. Phase 3 is re-imagining it — agents that resolve the disputes themselves."*

**Pre-flight messaging checklist** (tick each before you finish — this is the rubric line):
- [ ] Said **Open Data + AI Platform** / **Agentic Enterprise** once up front
- [ ] Said **Unified** + **Simple** (one platform, declarative/serverless)
- [ ] Landed all four C's by name: **Context · Control · Cost · Choice**
- [ ] Named the products: **Unity Catalog / Unified Governance**, **Open Formats (Delta + Iceberg)**, **Lakehouse**, **Lakebase**
- [ ] Closed on **Phase 2: Automate Business Processes**

---

## Why this scores on the onboarding rubric

Every platform layer the whiteboard exercise wants is in the story, grounded in one build:

| Platform layer | Where it shows up |
|---|---|
| **Unified Governance (Unity Catalog)** | the foundation band — step 3 |
| **Lakeflow / lakehouse (open, serverless)** | Bronze→Silver→Gold pipeline — steps 4–5 |
| **AI / ML + Model Serving** | hold recommender + endpoint — step 6 |
| **Genie / agentic BI** | ask-the-data lamp — step 7 |
| **Databricks Apps** | Reconciliation Workbench — step 8 |
| **Business value / outcome** | auto-approve + recovered $ + audit — step 9 |

> *Optional Lakebase beat (if asked "where does the analyst's decision live?"):* the approve/reject
> writes + audit trail land in a serverless Postgres (Lakebase) table synced back to the lakehouse —
> operational + analytical on one platform.

---

## If you're drawing it live (iPad / real board)
- Pre-mark the **gov-blue foundation band** faintly before you start so your boxes land on it.
- Keep **orange-red for exactly two things** (pain + the match) so the eye goes to the hero beat.
- End on the **green payoff** — that's the "lead with value" the rubric rewards.
