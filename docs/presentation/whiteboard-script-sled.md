# Platform Whiteboard — Delivery Script (SLED / Public Sector)

> **What this is:** your spoken narration for the **FY27 Field Onboarding Platform Whiteboard** —
> draw the whole Databricks story live, no slides, from a blank canvas (~10 min). Modeled on Tom
> Molyneux's bootcamp exemplar, tailored to **State & Local / Higher Ed**, with **Accord** (your
> FE Bar build) as the concrete proof beat.
>
> **How to use it:** `[DRAW: …]` = what to put on the board; **colors** match your
> `accord-whiteboard.md` palette — **red = problems/4 Cs**, **green = solution bands**,
> **blue = value story**. Lines in plain text are what you *say* (~150 wpm). Timings are cumulative.
> Hit every **bold messaging term** — that's rubric line #1.
>
> **Rubric this serves:** (1) messaging, (2) product knowledge, (3) business value/TCO,
> (4) a customer story that unlocks a use case, (5) presentation skills.

---

## 0 · Frame + promise · [0:00–0:35]

> *[DRAW: nothing yet — start on a clean canvas. Draw the stacked-diamond Databricks logo, top-center, in red.]*

"Welcome. Databricks is the **data and AI company**, and our mission is to **democratize data and
AI** — put it in the hands of everyone in an organization, not just a specialist team. Every
architectural choice we've made traces back to that.

I'm going to **draw** this instead of clicking through slides — because I want you to leave with a
picture you can redraw in front of your own agency or campus leadership."

---

## 1 · Business value first — the 3 phases · [0:35–1:50]

> *[DRAW: start the BLUE column down the right side. Header "Data + AI" with sparkles. Then number
> them 1-2-3 as you say them.]*

"Why does a public-sector leader care? Because AI is reshaping how institutions run — and it happens
in **three phases.**

**One — 10x workforce productivity.** *[DRAW: '1 · 10x' + person/laptop icon]* Every caseworker,
analyst, and administrator gets AI coworkers — personal agents, coding assistants. People stop
*hunting* for data and start *making decisions*.

**Two — automate the business processes.** *[DRAW: '2 · AUTOMATE' + gear/workflow]* Departmental
agents, document intelligence, workflow automation. This is where you take **OpEx** out — the
backlogs, the manual review queues, the paperwork.

**Three — re-imagine the mission.** *[DRAW: '3 · RE-IMAGINE' + trophy/$]* One-to-one citizen and
student experiences, self-healing systems. This is **better outcomes** and doing more with a flat
budget.

Costs down, outcomes up, faster time-to-value. *[DRAW: underline the blue column]* That's the case —
and the race is on to get there."

---

## 2 · Make it concrete — the Accord proof · [1:50–3:05]

> *[DRAW: a boxed proof point under the blue column — "ACCORD · 3-way match", a little "~72%" and a
> "$ at risk" doodle.]*

"Let me make that concrete with something **I built.** It's called **Accord** — an AI-assisted
**invoice three-way match**. Every purchase order, goods receipt, and invoice has to agree before a
dollar goes out the door. I built the whole thing end to end on the platform: a pipeline that runs
the match, a machine-learning model that scores each exception, and an app where an analyst clears
them.

The result: about **72% of invoice lines matched cleanly and never needed a human** — that's
**Phase 2, automation**, OpEx straight out. The model ranked the rest by **dollars at risk**, so the
analyst's day starts on the biggest exposure, not the top of an alphabetical list — that's
**Phase 1, productivity.** And the path from there is agents that *resolve* the disputes themselves —
**Phase 3**.

Now — picture that exact process in a **state agency's accounts payable** or a **university
procurement office**: hundreds of thousands of invoices a year, under audit, with improper-payment
and transparency pressure. Swap fragrances for lab equipment and construction POs and it's the *same
problem*. That's the point — this platform runs *your* mission-critical processes, not a toy."

> *Optional (stronger on rubric #4): add a real public-sector logo here — e.g. a state or university
> Databricks customer with a hard metric from go/customer — and say "and here's a real one." Ask me
> and I'll pull one.*

---

## 3 · The bridge + the agentic tidal wave · [3:05–4:00]

"So if the prize is that big — what's actually **blocking** most institutions?

Here's the backdrop. *[DRAW: switch to RED. Up the left side, a wave of little database/chart icons;
circle '2026' in red.]* An **agentic tidal wave** is hitting. And when I say *agentic*, I don't mean
chatbots and copilots — I mean systems where AI does the **work**: processing transactions, touching
core systems, running operations autonomously.

Our CEO, **Ali Ghodsi**, framed it at the Data and AI Summit: the question is no longer whether the
models are smart enough — they are. The question is whether AI can operate **inside your
organization**, at scale, with access to **your data, your processes, your context.** **2026 is the
year AI gets real inside institutions** — not a pilot here and there, but infrastructure that runs
the mission."

---

## 4 · The Four Cs — the real blockers · [4:00–6:30]

> *[DRAW: RED, left column. Number and circle each C as you go, with a quick icon.]*

"It comes down to four things. We call them the **Four Cs** — and they're *not* a product framework.
They're the four obstacles that stop AI from scaling inside a customer. Watch how often these show up
in your own accounts.

**One — Context.** *[DRAW: '1 · CONTEXT', scattered system boxes: 'SIS', 'ERP', 'email']* The models
know everything about the world and **nothing about your institution.** Your data is scattered —
student information systems, the finance ERP, HR, grants, constituent and case systems, email, a
mainframe nobody wants to touch. Connecting AI meaningfully to all of it isn't a config problem —
it's an **architecture** problem.

**Two — Control.** *[DRAW: '2 · CONTROL', people icons + 'FERPA/CJIS?' + gear-with-X]* The moment AI
touches a student record or constituent PII, the questions start. Who can access what? What are the
agents actually *doing*? Can we **audit** them? In public sector this isn't just compliance — FERPA,
CJIS, public-records law — it's **public trust.** Most organizations have zero visibility here.

**Three — Cost.** *[DRAW: '3 · COST $', a token icon + 'budget!']* This becomes a crisis fast. Token
spend spirals, agents run all night, nobody knows whose they are. Uber burned through its **entire
2026 AI budget in a single quarter.** A public institution **cannot** explain that to a legislature or
the taxpayers — your budget is fixed and it's public.

**Four — Choice.** *[DRAW: '4 · CHOICE', branching arrows + a one-way-door]* The best model today
won't be the best in **60 to 90 days.** If you've built on one vendor's proprietary stack, you've
walked through a **one-way door** — and in public procurement, that lock-in is exactly what you're
mandated to avoid.

*[DRAW: underline all four.]* Context, control, cost, choice. **Every stalled AI program I've seen is
stuck on at least one of these.**"

---

## 5 · The solution — build it bottom-up · [6:30–9:15]

> *[DRAW: switch to GREEN. Build a stack of horizontal bands in the middle, bottom to top, with a
> vertical divider on the left. Green highlighter-circle each product as you name it.]*

"So let me build how we solve this — from the **bottom up.**

**It starts with Open.** *[DRAW: bottom band 'OPEN' + '60–90 days' + one-way-door]* This has been our
philosophy since day one. The right architecture for data and AI is **open** — **open formats, open
infrastructure, open models** — not for ideology, but because it's what keeps you out of that one-way
door. Your data sits on an **open-format data lake** — we support **Delta Lake and Iceberg**, and the
two have **converged**. Any cloud, any engine, any AI can read it. You **own your data.** *That's
**Choice**, and it lives at the foundation.*

**Agentic Data.** *[DRAW: next band up, 'Agentic Data' + 'Lakeflow 100+', Lakehouse + Lakebase icons]*
Above that you need infrastructure that can actually serve **agents** — and agents behave nothing like
people. A person runs one query and reads the answer; an agent **loops, branches, runs parallel
subtasks.** Three products deliver this: **Lakeflow** for ETL — ingest, transform, orchestrate, 100-plus
connectors. **Lakehouse** for best-in-class SQL and warehousing at any scale. And **Lakebase** — a
**serverless Postgres that lives on the lake**, where an agent can spin up and **branch an entire
database in under a second** to experiment and roll back. Operational database, built for the agentic
era.

**Unified Governance.** *[DRAW: next band, 'Unified Gov' + a 'UC' building + 'AI Gateway']* **Slow
down here — this is the differentiator.** **Unity Catalog** is one governance layer across **every
asset** — tables, files, models, agents, tools — with access control, lineage, quality, and business
semantics. It's **open-sourced.** And the newer half — the **Unity AI Gateway** — is the one that
changes the conversation: a **single pane of glass** for *every* AI call in the organization. Full
observability into who's using what and what it costs, **budget controls** by team and agent, plus
policy, auditing, and identity. *One place to govern data and AI, one place to control AI cost —
that's **Control** and **Cost** solved at the same layer.* For public sector, that audit trail **is**
your FERPA and CJIS story.

**Agentic Work.** *[DRAW: top band, 'Agentic Work' + 'Genie Ontology', then 'Genie' + 'Agent Bricks']*
The top band — the hardest problem. Most agents answer by searching documents one at a time, at query
time: slow, expensive, and inconsistent. **Genie Ontology** works differently — it builds a
**knowledge graph of the whole organization** continuously, in the background, and ranks what matters.
Because it's **pre-built**, any agent draws on it instantly. *That's **Context** — enterprise context
for all AI.* Two things sit on top: **Genie**, the data-smart AI coworker — ask a business question
and it goes to the **governed** data, writes the query, and computes the **right number** instead of
guessing. And **Agent Bricks**, the open platform for building custom agents — any model, any
framework. If a team already uses LangChain, it works. Both run on the **same ontology and the same
governance.**"

---

## 6 · Recap — 4 problems, 4 answers · [9:15–9:45]

> *[DRAW: draw arrows linking each RED C to the GREEN layer that answers it. Then a GREEN loop around
> the whole board.]*

"Step back and look at the whole picture. *[point as you go]* **Context** — from unified open data and
Genie Ontology. **Control** — Unity Catalog and the AI Gateway. **Cost** — the Gateway's budget
controls. **Choice** — open infrastructure at the base. **Four problems, four answers, one unified
data and AI platform.** If you can draw *this*, you can have the platform conversation with any
public-sector leader, at any altitude, **without a deck.**"

---

## 7 · Close — three takeaways · [9:45–10:30]

> *[DRAW: BLUE — '→ winner!' with a trophy, next to 'context / control / cost / choice'.]*

"Three things to take with you.

**First — lead with the problem, not the product.** Your customers aren't confused about whether AI
is powerful. They're stuck on **context, control, cost, and choice.** Name those four before you name
a product and you're in a **leadership conversation**, not a feature demo.

**Second — this is a platform, not a point product.** Every band is a **land-and-expand** door. A
customer might start with a Lakehouse migration or one process like Accord — but the Four Cs open the
door to governance on Unity Catalog, cost control on the AI Gateway, and agents on Agent Bricks. Your
job is to **draw the whole picture** so they see where it goes.

**Third — open is the wedge.** When they're weighing a proprietary option, **open is your
differentiation** — their investment travels across clouds, models, and formats as the market churns
every 60 to 90 days. And the frontier models — OpenAI, Anthropic — are **native to the platform.** In
public procurement, that no-lock-in story isn't a nice-to-have, it's often the requirement.

We're the **data and AI company**, our mission is to **democratize data and AI** — and this platform
is how you help your institutions get there."

---

## Delivery notes
- **Target ~10 min.** To trim to a hard 10: shorten §3 (the tidal wave) and keep §5 tight — the Four
  Cs (§4) and the bands (§5) are the scored core; don't rush them.
- **Say the proper nouns**, not synonyms: *Unity Catalog, Unity AI Gateway, Lakeflow, Lakehouse,
  Lakebase, Delta Lake, Iceberg, Genie, Genie Ontology, Agent Bricks.*
- **Messaging checklist** (rubric #1): Unified · Simple · Context · Control · Cost · Choice · UC /
  Unified Governance · Lakebase · Open Formats. Tick each — they're all in here.
- **Customer-story note (rubric #4):** Accord is *your* synthetic build — great as a concrete,
  defensible proof. For full marks, consider adding one **real** SLED customer logo + metric in §2
  ("and here's a real one"). Ask me and I'll pull a public-sector story from go/customer.
- Pairs with `accord-whiteboard.md` (same palette) and `roleplay-guide.md` (FE Bar roleplay).
