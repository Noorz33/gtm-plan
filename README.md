# gtm-plan: a Claude Code skill for go-to-market plans

A [Claude Code](https://claude.com/claude-code) skill that writes a go-to-market, launch or campaign plan to a 10-dimension readiness scale, then delivers three files:

| File | What it is |
|---|---|
| `<SLUG>_GTM_Presentation.html` | Persian RTL presentation, dark theme. Sections: proposal, research, segments, campaign architecture, concepts, event, action plan, day-by-day Gantt, budget, gates and risks, decisions, open questions and the decision ask. It has a slides mode (press `P`) and a print layout. |
| `<SLUG>_GTM_Presentation.pdf` | A4-landscape deck with one section per page and a logo header on every page. |
| `<SLUG>_GTM_Scorecard.html` | Readiness dashboard: the score per dimension with reasons, tickable fixes with the projected score, a sales-funnel calculator, a spend-vs-product-gate timeline and open items. |

The skill writes the plan to the scale from the start; it does not score it afterwards. The sales target has to come out of a funnel. Every task needs a named owner and a testable "done" criterion. Every decision records the rejected option and what it would have bought. Every gate needs a measurable criterion, an approver and an action for when it fails. Legal questions are never answered; they are recorded as open questions for a professional.

See it before installing: [`examples/sample/output/`](examples/sample/output/) has the built files for a **fictional** plan ("Parto", a cloud warehouse app; every name, number and source is made up).

## Install

```bash
git clone https://github.com/Noorz33/gtm-plan ~/.claude/skills/gtm-plan
```

Requirements:
- Python 3.9+
- Google Chrome or Chromium, for the PDF. Without it, run with `--no-pdf`.
- Optional: `pip install pillow` to shrink and recolour logos. Without it, logos are embedded as they are.

## Use

In Claude Code, run `/gtm-plan` or just ask, for example «برنامه ورود به بازار برای … بنویس» or "write a go-to-market plan for …". Put briefs, meeting notes and logos in the working folder first. The skill runs these steps:

1. **Intake:** one batch of questions, each with a default answer.
2. **Research:** web research for 3–5 comparable launches.
3. **Decision brief:** a one-screen summary. The skill waits for your "go" before continuing.
4. **`plan.json`:** the plan, written following [`references/plan-schema.md`](references/plan-schema.md).
5. **Build, score, fix:** the linter checks the plan against the scale, and Claude checks the rendered pages and PDF visually.
6. **Deliver:** the files land next to `plan.json` and are served on localhost.

The build script also runs on its own:

```bash
python3 scripts/build.py examples/sample/plan.json --out /tmp/parto        # HTML + PDF
python3 scripts/build.py path/to/plan.json --check-only                      # lint and score only
```

## The scale

Weights are fixed so plans stay comparable:

| Dimension | Weight |
|---|---|
| Evidence | 15 |
| Market research | 10 |
| Personas | 10 |
| Measurable goals and funnel | 15 |
| Decisions | 10 |
| Assumptions and open questions | 5 |
| Timeline | 10 |
| Definition of done | 10 |
| Risks | 10 |
| Go/No-Go gates | 5 |

Each dimension is scored 0–5. The verdict is **< 60** not ready, **60–75** conditional, **≥ 75** ready for a go decision. The anchors for each score are in [`references/scorecard.md`](references/scorecard.md). The principles are adapted from [iniesohidham/idea-to-blueprint](https://github.com/iniesohidham/idea-to-blueprint).

## Layout

```
SKILL.md                 workflow Claude follows
references/              scale anchors, plan.json schema, intake questions
scripts/build.py         Jalali dates, linter, scoring, rendering, PDF
templates/               presentation and scorecard templates
examples/sample/         fictional plan.json and its built output
```

## Limits

- PDF fit: about 14 tasks, 14 budget items, 3 segments and 4 concepts. Keep card text under about 180 characters. Longer sections spill onto a second page.
- The UI and copy are in Persian. Plan text can be in any language, but the labels are Persian.

MIT licensed.
