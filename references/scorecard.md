# The readiness scale (10 dimensions, 100 points)

Adapted from the principles of github.com/iniesohidham/idea-to-blueprint for go-to-market plans:
evidence or silence · decide, don't hedge (name the loser and its price) · measurable goals ·
a definition of done per unit of work · legal questions go to a professional · quality is specified, not assumed.

Weights are fixed in `scripts/build.py` so plans stay comparable. Score each dimension 0–5 (halves allowed).
Points = score / 5 × weight. Verdict: < 60 not ready · 60–75 conditional · ≥ 75 ready for a go decision.

| # | Dimension (fa label in the dashboard) | Weight |
|---|---|---|
| 1 | Evidence & sources (شواهد و منابع) | 15 |
| 2 | Market research & benchmark (پژوهش بازار و مقایسه) | 10 |
| 3 | Customer segments / personas (پرسونای مشتری) | 10 |
| 4 | Measurable goals & funnel (اهداف و معیارهای قابل اندازه‌گیری) | 15 |
| 5 | Decisions with the rejected option's cost (تصمیم‌ها با هزینهٔ گزینهٔ ردشده) | 10 |
| 6 | Assumptions & open questions (فرض‌ها و پرسش‌های باز) | 5 |
| 7 | Timeline & dependencies (زمان‌بندی و وابستگی‌ها) | 10 |
| 8 | Definition of done per task (تعریف «انجام‌شده» برای هر کار) | 10 |
| 9 | Risks & guardrails (ریسک‌ها و حفاظ‌ها) | 10 |
| 10 | Go / No-Go gates (دروازه‌های Go / No-Go) | 5 |

## Anchors

**1 Evidence & sources**
0 claims with no source · 2 honest "proposed" labels but internal sources only · 3 key external facts tagged verified/assumed/unknown · 4 every external claim tagged, sources with URLs and dates · 5 plus every number in the plan traceable to a source or an explicit assumption.

**2 Market research & benchmark** (capped at 1 when `research.benchmark` is empty)
0 none · 1 competitors named only · 3 3–5 comparable launches with what they did and the lesson · 4 plus a positioning statement and the gap we take · 5 plus market size or demand signal with evidence.

**3 Segments / personas**
1 a list of audiences · 3 each segment has problem, access route and proof needed, and the buyer/distributor/referrer role · 4 plus decision-maker, likely objections and typical ticket size · 5 plus named target accounts per segment with owner.

**4 Measurable goals & funnel**
1 only a final target · 2 final targets for several outcomes · 3 funnel stages defined with rates · 4 target derived from the funnel with weekly leading indicators · 5 plus media/content KPIs and the instrument that measures each.

**5 Decisions**
1 many open choices, no records · 2 open choices listed with deadlines · 3 key choices decided · 4 every decided record names the rejected option and what it would have bought · 5 plus reversibility noted and no blocking decision past its due date.

**6 Assumptions & open questions**
1 implicit · 2 listed · 3 assumptions with impact-if-wrong · 4 open questions with owner, due, what they block · 5 plus the critical ones are scheduled before the commitments they block.

**7 Timeline & dependencies**
2 dates only · 3 tasks with owners and dates · 4 plus Gantt, phases and dependency chains · 5 plus every owner decided and the critical path explicit.

**8 Definition of done** (capped at 2.5 when tasks have no `done`)
1 activities only · 2.5 every task has a deliverable · 4 most tasks have a testable done-criterion · 5 all tasks.

**9 Risks & guardrails**
1 none · 3 real risks with responses and a public-claims rule · 4 plus legal/regulatory OQ, budget reserve, and the most likely external shock (price, regulation, competitor) · 5 plus a trigger and owner per risk.

**10 Gates**
1 none · 3 dated gates with qualitative criteria · 4 measurable criteria and a named approver · 5 plus an `on_fail` action and irreversible spend placed after the gate.

## Fixes
For every dimension below 4, add a fix to `scorecard.fixes`: `priority` 1 if it blocks the go decision (target unsupported, legal open, irreversible spend before the product gate, key decision open), else 2. `gain` is your estimate of the score increase per dimension when the fix is done; the dashboard caps each dimension at 5.
