# Accord — Guided Roleplay Script (follow along live)

> **What this is:** the doc you keep open **during** the FE Bar AI roleplay (~20–30 min). You present
> Accord to **two AI personas** — a **business stakeholder** and a **technical stakeholder** — and
> defend the value story in real time. Scored on **demo setup · value communication · reading the
> room · professionalism.** This is the live script; the *build* prep lives in
> `../superpowers/plans/2026-09-24-phase6-presentation-roleplay.md`.
>
> Values shown as `$X` / `Y%` are **illustrative** — replace with your demo's actual numbers or say
> "in a customer's numbers, this is where X shows up." Never invent a specific customer's figures.

---

## 0. Pre-flight checklist (2 min before you start)

- [ ] **Tabs open, in demo order:** App → **Summary**, **Reconciliation**, **Exceptions**, **Line detail**; the **Genie** space; the **deck** (PDF).
- [ ] Serving endpoint `accord-holdrecommender` is **READY** (so the AI panel responds live).
- [ ] Pick **one held line you know cold** to drill into (a clean `PRICE_VAR` or `QTY_OVERBILL`).
- [ ] Water, notifications off, share the right screen.
- [ ] **Positioning line memorized** (say it in the first 30s):
  > *"Accord is an AI-assisted invoice-reconciliation workbench: it runs the three-way match across
  > every PO, receipt, and invoice, auto-approves the clean lines, and hands analysts only the
  > exceptions — each with a recommendation and a plain-language reason."*
- [ ] Keep the **four scored dimensions** in the back of your mind: set up cleanly, lead with value,
  read the room, stay composed.

---

## 1. Narrative arc (20–25 min budget)

| Min | Beat | Goal |
|---|---|---|
| 0–2 | **Hook + problem** | AP pays thousands of invoice lines/mo; manual 3-way match is slow and leaks money |
| 2–4 | **What Accord is** | one integrated journey: feeds → match → score → analyst decision → audit |
| 4–14 | **Live demo** | Summary → Reconciliation (bulk approve) → Exceptions → Line detail (AI) → Ask Accord |
| 14–18 | **Value** | touchless-match rate, cycle time, recovered $, analyst capacity, clean audit |
| 18–22 | **Architecture / trust** (esp. for tech persona) | medallion + Lakeflow + UC governance + the model |
| 22–25 | **Close** | "here's what a 4-week POC proves" + the ask |

Adjust live: business persona → spend more on 0–14 and 14–18; technical persona → compress the demo, expand 18–22.

---

## 2. Live demo run-sheet (click → say → prove)

### Summary landing page
- **Click:** open Summary; toggle **week / month / year**.
- **Say:** *"This is the AP lead's morning view — how many suppliers we transact with, invoices
  received this period, and the split of invoice lines that **auto-approved** versus sit **on hold**
  versus were **rejected**, in both count and dollars. The number that matters is touchless-match
  rate — the share that never needed a human."*
- **Proves:** business framing + that the match already did the bulk of the work automatically.

### Reconciliation review page
- **Click:** filter to a **supplier** + **month**; select several held lines; **bulk approve**; show
  the per-row **AI recommendation + confidence + one-line reason**.
- **Say:** *"Analysts live here. They filter to what they own, and every held line carries a
  recommendation — Approve or Hold — with the reason. Lines the model is confident are fine, they
  clear in a batch; the judgment calls get their attention. It's ranked by dollars-at-risk times
  hold-likelihood, so the biggest exposure floats up."*
- **Proves:** the core workflow + human-in-the-loop + AI is load-bearing, not decorative.

### Exceptions page
- **Click:** group by **reason** and by **supplier**.
- **Say:** *"This is the 'why'. Holds broken down by reason — price variance, over-billing, no
  receipt, duplicates — and by vendor. When one supplier shows chronic price variance, that's a
  conversation with procurement, not just an AP fix."*
- **Proves:** root-cause visibility + turns exceptions into supplier-management insight.

### Line detail (drill-in)
- **Click:** open your rehearsed held line; show **PO vs GR vs Invoice side-by-side** with the field
  chips; open the **AI panel**.
- **Say:** *"Here's the actual three-way match for one line — purchase order, goods receipt, invoice,
  field by field. The invoice billed $X at this unit price; the PO says $Y — a 6% variance above
  tolerance. The model recommends Hold at 0.94 confidence, and the top drivers are the price variance
  and this vendor's history. The analyst approves or rejects with a reason, and it's all audited."*
- **Proves:** the match is real and explainable; the model output is grounded in the fields.

### Ask Accord (Genie)
- **Click:** ask *"total dollars on hold by supplier this quarter"* and *"which vendors have the
  highest exception rate."*
- **Say:** *"And anyone can just ask — natural language over the governed tables, SQL-backed answers,
  no dashboard-building."*
- **Proves:** the Genie hard gate + self-serve analytics on the same governed data.

---

## 3. Business stakeholder — Controller / VP Finance / AP Director

**Open with value, not features:** *"Your team's goal is to pay correctly and on time without a
person touching every line. Accord raises the share that clears automatically and makes the
exceptions fast and defensible — so you catch overbilling and duplicates before they're paid, and
free analysts for the judgment work."*

**Q&A bank:**
1. **"Why not just use our ERP / SAP / Coupa?"** — *"Keep it. Accord sits on top — it's the AI +
   governance layer: an ML recommendation with a reason and a full audit trail on your own lakehouse,
   and it works across sources the ERP doesn't reconcile cleanly. It complements, not replaces."*
2. **"What's the ROI?"** — *"Three levers: recovered dollars from blocked overbilling/duplicates,
   analyst hours returned as touchless-match rises, and captured early-payment discounts from faster
   cycle time. In a POC we measure all three against your baseline."*
3. **"How accurate is it — can I trust the AI?"** — *"The analyst always decides; the model
   recommends and shows why. We tune it to favor catching bad payments over convenience, and every
   recommendation is explainable down to the fields."*
4. **"What about the analysts' jobs / change management?"** — *"It removes the tedious clean-line
   clicking, not the judgment. Their day shifts to the exceptions that actually need a human, with
   better context."*
5. **"Is our data safe?"** — *"This demo is 100% synthetic. In your environment it's your data, on
   your lakehouse, governed by Unity Catalog — including masking sensitive vendor banking fields."*
6. **"How long to stand up?"** — *"A focused POC in ~4 weeks on a slice of your invoices; the pattern
   is already built."*
7. **"What if the model's wrong?"** — *"Wrong-hold just costs a click to approve; wrong-approve is
   the expensive one, so we bias toward recall on holds. Analyst decisions feed back to improve it."*
8. **"What does a POC prove?"** — *"Touchless-match rate on your data, dollars flagged, and cycle-time
   delta — three numbers your team already tracks."*

---

## 4. Technical stakeholder — Head of Data Platform / ERP-integration lead

**Open with the shape:** *"It's one governed medallion pipeline on Databricks — feeds land, Lakeflow
conforms and matches them, a model scores each line, and an app + Genie sit on the gold table. No
data leaves the lakehouse."*

**Architecture talk track:** landing (raw file feeds) → **bronze** (Auto Loader `read_files`
streaming tables) → **silver** (conformed lines + governed `vendor_master` / `match_config`) →
**gold** `invoice_match_result` (the 3-way match, flags, `disposition`, `reason_code`, `amt_at_risk`).
The model reads gold features, registers in **Unity Catalog**, serves behind an endpoint the app
calls. Genie sits on gold. Lineage is end-to-end in UC.

**Q&A bank:**
1. **"Rules vs ML — which decides?"** — *"Rules derive the deterministic exception code; the model
   predicts hold-likelihood/confidence. That keeps 'why' explainable and stops the model just
   re-learning the rules (spec decision D-5)."*
2. **"Model details?"** — *"Gradient-boosted trees on tabular discrepancy features — price variance,
   qty variance, receipt lag, vendor exception-history, duplicate signal. SHAP for attributions.
   Threshold tuned toward hold recall because a false approve pays bad money (D-2, D-3)."*
3. **"Label leakage?"** — *"Labels come from a separate ground-truth table; the rule outputs that
   trivially equal the label are kept out of the feature set."*
4. **"How does real ERP data get in?"** — *"Today it's file feeds; in production it's Lakeflow
   Connect / federation to SAP/Coupa/Oracle. Same bronze→silver→gold contract downstream."*
5. **"Governance / sensitive data?"** — *"Unity Catalog throughout — lineage, grants, and a column
   mask on vendor remit/banking fields so AP sees what they need and no more."*
6. **"Batch or real-time scoring?"** — *"Both — batch scores gold for the queue and dashboard; the
   app calls the serving endpoint live on the line the analyst opens."*
7. **"Streaming or batch ingest?"** — *"`STREAM read_files` / Auto Loader — new feed files are picked
   up incrementally; the pipeline is serverless."*
8. **"Deployment / reproducibility?"** — *"Everything is a Databricks Asset Bundle — one `bundle
   deploy` stands up the pipeline, job, model, and app across targets. It's in Git with real commit
   history."*

---

## 5. Objection & curveball handling (stay composed)

- **"This is just OCR / a rules engine with lipstick."** — *"The match is rules; the value is the
  prioritization, the explanation, and the learning loop on top — and it's governed and auditable."*
- **"Our invoices are messier than this."** — *"Agreed — that's the point of the exceptions page and
  the confidence score; messy is exactly where the triage pays off. A POC calibrates to your mess."*
- **"What about multi-currency / tax / partial receipts?"** — *"Out of scope for this prototype
  (spec §11); partial receipts are modeled, currency/tax are a documented extension."*
- **"Who's accountable if a bad invoice gets paid?"** — *"The analyst — Accord recommends and
  records; it never auto-pays. The audit trail makes accountability clearer than today."*
- **"Why Databricks and not a point AP tool?"** — *"Because it's your data, your governance, and your
  ML — one platform, no new silo, and it extends to the next reconciliation use case."*
- **"Can you prove the AI isn't hallucinating a reason?"** — *"The reason is grounded in the actual
  matched fields shown side-by-side; the narrative is generated from those values, not free-form."*
- **If asked something you don't know:** *"Good question — I'd confirm that in the POC rather than
  guess."* (Composure scores; bluffing doesn't.)

---

## 6. Reading-the-room cues

- **Business persona leans in on $ / process** → stay in Summary + Reconciliation + Exceptions; talk
  outcomes; keep architecture to one sentence.
- **Technical persona probes the model / governance** → go to Line detail + the architecture talk
  track; name the decisions (D-2/D-3/D-5) confidently.
- **Eyes glaze / "I get it"** → stop demoing, jump to value + the POC ask.
- **Skeptical tone** → acknowledge, narrow the claim, offer to prove it in a POC. Don't over-defend.
- **Short on time** → collapse to: Summary tile → one held line in Line detail → the close.

---

## 7. One-page cheat sheet (memorize these)

- **Positioning:** *AI-assisted invoice-reconciliation workbench — runs the 3-way match, auto-approves
  clean lines, hands analysts only the exceptions with a recommendation + reason.*
- **The 3 docs:** Purchase Order ↔ Goods Receipt ↔ Invoice; match on product #, qty, price, vendor.
- **Value levers (3):** touchless-match rate ↑ · recovered $ (overbilling/dupes) · cycle time ↓ →
  analyst capacity + discount capture.
- **Dispositions:** AUTO_APPROVED · HOLD · APPROVED · REJECTED (analyst acts on HOLD, all audited).
- **Model soundbite:** *rules give the exception code, the model gives hold-likelihood; tuned so a
  false approve (paying bad money) hurts more than a false hold.*
- **Architecture soundbite:** *landing → bronze → silver → gold on Lakeflow; model + Genie + app on
  gold; all governed by Unity Catalog; deployed as one Asset Bundle.*
- **Trust soundbite:** *analyst always decides; every recommendation is explainable to the fields;
  synthetic data, no secrets.*
- **Close:** *"A 4-week POC on a slice of your invoices, measured on touchless-match rate, dollars
  flagged, and cycle-time delta."*
- **The 4 scored domains:** Industry · Product · Build + AI Mindset · Customer Skills.
