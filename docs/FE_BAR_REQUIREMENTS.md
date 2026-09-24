# FE Bar — Program Requirements & Rules

> **Source of truth:** the FE Bar announcement email (FE Enablement, 2026-09-17, subject
> *"FE Bar Update: Submissions Open Monday September 21"*) and **go/fe-bar-faq**. This file is my
> distilled, build-oriented copy so the requirements sit next to the build. When the FAQ and this
> file disagree, the FAQ wins — re-check go/fe-bar-faq before submitting.

## What the FE Bar is

The FE Bar is Field Engineering's AI-driven skills-validation program. It replaces product-knowledge
validation with **demonstrating you can design, build, and present a real solution**. It has three
elements:

**FE Bar = 1 Databricks certification (your choice, aligned to your work) + 1 AI build + 1 AI demo roleplay.**

1. **Certification** — maintain a current Databricks certification.
2. **The build** — a working AI prototype that solves a real customer problem in a specific
   industry, as **one integrated end-to-end data journey** (not disconnected pieces).
3. **The AI demo roleplay** — after submitting the build, you present to **two AI customer
   personas** (a **business stakeholder** and a **technical stakeholder**) the way you would a real
   customer, and defend the value story in real time. ~20–30 min. Scored on demo setup, value
   communication, reading the room, and professionalism.

## Timeline & who it applies to

- **Submissions open:** September 21, 2026 (go/skillsnavigator).
- **Completion expected by:** **November 30, 2026.**
- **New hires:** 6 months from hire date. **Just finished Tech Foundations:** +1 quarter.
- **Applies to:** SAs, DSAs, SSAs (baseline competence for all, regardless of level).
- **Exempt:** those who completed Tech Specialization via the formal Portfolio Review; EMs/TPMs
  (not currently scoped); FDEs (maintain Tech Foundations for now).
- **Not applicable in:** France, the Netherlands, Korea (at this time).
- **AI Beta participants:** until end of Q4.

> **My status (Mehak):** SA/SE in ramp. The FE Bar applies. Target: submit well before Nov 30.

## Certification (my choice)

Applicable certs: **Data Engineering, Machine Learning, Gen AI, and the new Context Engineering**
certifications.

- **My pick: Databricks Certified Data Engineer Associate** — I'm already prepping for it (see my
  onboarding tracker). The DE cert now has a **shorter renewal exam** option, and there's an
  [AI prep guide](https://www.databricks.com/sites/default/files/2026-06/ai-prep-guide-any-databricks-certification.pdf).
- Certs must be recertified every 2 years; the build + roleplay likely recertify annually.

## Scoring — the four domains

Both the build and the roleplay are scored by an AI evaluator against a rubric designed by FE
Experts, across **four domains**:

1. **Industry**
2. **Product**
3. **Build + AI Mindset**
4. **Customer Skills**

Each domain is rated **Below / Meets / Exceeds**.

- **You pass when every domain is Meets or Exceeds AND the build is complete (hard gates met).**
- A strong domain does **not** offset a weak one.
- **Meets is the bar** — every must-have genuinely satisfied, work is solid.
- **Exceeds** is upside — never required to pass; it's the "level-up" growth target you get feedback
  on for every domain not yet there.
- You get detailed written feedback within minutes of each submission.

See [`RUBRIC.md`](RUBRIC.md) for the domain-by-domain breakdown mapped to the Accord build.

## What to submit (both parts required; both in Skills Navigator)

1. **The build:**
   - A **GitHub repo link** (`github.com/owner/repo`), **and**
   - a **local folder** of the build you select in the submission form (the browser reads your
     source files locally).
2. **The presentation deck** — attached as a **file** (PDF; `.txt`/`.md` also work), not a link.

## Hard gates & customer-safety

- **Synthetic or public data only.** Never real customer data.
- Before scoring, the platform **scans the repo, deck, and linked artifacts for secrets and
  credentials**. If any are found, the submission is **blocked before it's stored or scored**, and
  you're told what to scrub. → *Accord uses fully synthetic data and no hardcoded secrets.*
- **Integrity checks:** plagiarism comparison across submissions, prompt-injection / grader-
  manipulation detection, Solution Builder artifact detection, and **commit-authorship
  verification**. Flagged builds go to human review (not auto-fail).
- **Attestation** (required before scoring): the submission is your own work; it was **not**
  generated from go/solution-builder; you understand the consequences of misrepresentation.

## What counts as cheating (auto-fail risk + leadership notification)

- Submitting someone else's code/build as your own.
- **Using Solution Builder (go/solution-builder).**
- Sharing a full solution with, or reusing another FE's submission.
- A hidden human proxy; running the build for another person; a skill that bypasses the assessment.

## Using AI tools — encouraged, with a line

**Encouraged (not cheating):** brainstorming what to build; prompting scaffolding; an AI assistant
to write/refactor/debug **code you understand and can explain**; generating/cleaning the **synthetic
dataset**; drawing on prompt/pattern libraries then adapting; researching industry context; drafting
or refining the narrative/business case/deck.

**The line:** the **work, the decisions, and the narrative must be yours** — and you must be able to
defend them in the roleplay. The validator is designed to catch pure vibe-coding and requires
real trade-off decisions.

> **How I apply this to Accord:** I use AI to scaffold this plan and stub structure, research
> AP/procure-to-pay context, and generate synthetic data. **I write and own the pipeline, model,
> Genie, and app logic, and every design decision is logged in the spec so I can defend it.**

## Remediation, appeals, opt-out

- **Resubmit** as many times as needed, no waiting period; each attempt gives actionable feedback.
- **Split credit:** pass one half (build *or* roleplay) and only the other half carries over to retake.
- **Human-only review** option in Skills Navigator (skip AI scoring; expect longer turnaround).
- **Appeal:** if you didn't pass but believe you should have, request human review on the rating
  screen. Some submissions are auto-held by integrity checks until a reviewer writes up.

## Effort estimate (from the FAQ)

| Element | Rough time |
|---|---|
| Certification | 10–15 hours |
| The build | 5–10 hours |
| AI roleplay | up to 30 min per attempt |

> Accord is intentionally scoped to hit **Meets on all four domains** within the build budget, with
> clearly-flagged **Exceeds** opportunities (the optional adds) if time allows.

## Where to go / get help

- Build + roleplay: **go/skillsnavigator** (live Sep 21, 2026).
- Program info & rubric detail: **go/fe-bar-faq**.
- Questions / submission errors: **#fe-specialization** and **#skills-navigator**.
- Tracking dashboard: coming (announced in Data Drop / #fe-specialization).

## Note on AI Customer Challenge / hackathon builds (not my path, for reference)

If you reuse an **AI Customer Challenge** build (the one approved Solution Builder exception) or a
**hackathon** build, you must add **net-new individual work on top** and defend it: specifically a
self-built **Lakeflow pipeline** (raw→silver→gold via SDP), a **real ML model** (MLflow behind a
serving endpoint, replacing any placeholder heuristic), and a **real Genie** over your governed
tables (the app's chatbot does not count). Commit authorship is verified. *Accord is a fresh,
individual build, so this doesn't apply — but the same three artifacts are exactly what Accord
delivers, which is a good completeness checklist.*
