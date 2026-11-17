---
name: gtm-plan
description: "Build a go-to-market / launch / campaign plan (برنامه ورود به بازار، کمپین Go to Market، طرح رونمایی، پروپوزال کمپین، اکشن‌پلن و گانت) that is written to pass a 10-dimension readiness scale from the start, then deliver it as a Persian RTL presentation HTML (slides mode, Gantt, action plan, budget, gates, decisions), an A4-landscape PDF deck, and a scorecard dashboard served on localhost. Use whenever the user brings a product/token/service launch, a GTM or campaign plan, a brief, meeting notes or a draft plan and wants it planned, structured, evaluated or presented — e.g. «برنامه ورود به بازار برام بنویس»، «این طرح کمپین رو آماده کن»، «پروپوزال و گانت کمپین»، «طرح رو ارزیابی کن و فایل نهایی رو بده». Also use to re-score or update an existing plan.json."
---

# GTM plan → scored presentation, PDF and scorecard

The output is always the same three files, built by `scripts/build.py` from one `plan.json`:

| File | What it is |
|---|---|
| `<SLUG>_GTM_Presentation.html` | Persian RTL, dark theme, brand logos; sections: cover, proposal, research, segments, campaign architecture, concepts, event, action plan, day-by-day Gantt, budget, gates & risks, decisions/open questions/assumptions, decision ask. Has slides mode (key P) and a print layout. |
| `<SLUG>_GTM_Presentation.pdf` | A4-landscape dark deck, one section per page, logo header on every page. |
| `<SLUG>_GTM_Scorecard.html` | The 10-dimension scale, per-dimension reasons, tickable fixes with projected score, sales-funnel calculator, budget-commitment vs product-gate timeline, open items table. |

The point of this skill is that the plan is **written to the scale**, not scored after the fact. The scale is in `references/scorecard.md`; read it before writing anything. Never inflate a score: an honest 55 with a fix list is worth more than a flattering 80.

## Workflow

Talk to the user in Persian (or their language). Machine fields in `plan.json` (keys, IDs, dates) stay in the schema's format.

### 0. Gather (do not skip)
1. Read every file the user points at or that sits in the working folder: drafts, briefs, meeting notes (`.md`, `.pdf`, `.docx`, transcripts), previous `plan.json`, logo images. Logos: a dark-wordmark brand logo (`primary`), its square symbol (`icon`, crop it from the wordmark if needed), an optional "Powered by" partner wordmark (`partner`) and an optional round/organic symbol used as a faded corner background (`orb`).
2. Ask ONE batch of questions from `references/intake.md`, each with a default; skip anything the material already answers. Say «اگر جوابی ندارید، "پیش‌فرض" بنویسید». Wait for the answers.

### 1. Research (web on)
- Benchmark 3–5 comparable launches or competitors in the same market (for Iran: local platforms, exchanges, media). Each becomes a `research.benchmark` card with an evidence label and a source `S-nn`.
- Legal / regulatory / licensing questions are **never answered** — each becomes a critical `OQ-nn` for a professional, with an owner and a due date *before* the first public claim or media commitment.
- Media prices, partner commitments, conversion rates: verify or mark `assumed` / `unknown`. Never invent a number, a source or a partner's agreement.
- Post a one-line progress note every few searches.

### 2. Decision brief (checkpoint — wait for «go»)
One screen in Persian: how you read the goal; segments; the sales target and the funnel that produces it (show the arithmetic); launch date and product gate; budget total, reserve and how much is committed before the product gate; the open decisions you will record as DR with a recommended option; critical open questions; the epics/phases and task count. End with: «اگر درست است "برو" بنویسید، یا هر خط را اصلاح کنید.»

### 3. Write `plan.json`
Follow `references/plan-schema.md` exactly; `examples/sample/plan.json` is a complete, valid (fictional) example. Rules that make the scale pass:
- **Goal = funnel.** `goals.target` must come from `accounts × meet × demo × prop × close × ticket`. If the user's target does not follow from realistic rates, keep their target but say so on the proposal page and in the scorecard — do not hide the gap.
- **Every task** has owner (a name, not «تعیین شود»), start/end (Jalali), deliverable, and a testable `done` («≥۲۰ حساب با هر ۴ فیلد کامل»), plus dependency.
- **Every decision** is either `decided` with `chosen`, `rejected` and `cost` (what the rejected option would have bought), or `open` with options, what it blocks and a due date.
- **Every gate** has measurable `criteria`, a named `approver`, and `on_fail` (stop / postpone / change scenario).
- **Budget**: each item has a `commit` window (or `null` if truly unknown), and `reserve` is stated (recommend one; say it is an assumption).
- **Assumptions** carry `impact` if wrong. **Sources** carry URLs where they exist.
- Headline/lead copy: concrete, no hype words; claims about the product only if the plan's claims rule allows them.

### 4. Build, score, fix
```bash
python3 ~/.claude/skills/gtm-plan/scripts/build.py <folder>/plan.json --out <folder>
```
- Fix every `ERROR`. Each `WARN` either gets fixed or becomes an honest lower score + a fix in `scorecard.fixes`.
- Score each dimension with the anchors in `references/scorecard.md`; `why` cites what in the plan earned the score. Fixes carry an estimated `gain` per dimension (judgement — say so).
- Rebuild until clean. Then **look** at the result: screenshot the presentation and scorecard with headless Chrome and rasterize the PDF (`pdftoppm -r 40`), check for overflow, clipped labels, sections spilling onto extra PDF pages, and fix (shorten copy, fewer items) before delivery.

### 5. Deliver
- Files land next to `plan.json` (the user's project folder unless they name another).
- Serve the folder on localhost so the user can open both pages: `python3 -m http.server <free port> --bind 127.0.0.1` (run in background, check the port is free first), then `open` the presentation URL.
- Wrap-up in Persian, 6–10 lines: the three file paths and the localhost URLs; the score and verdict; the 2–3 weakest dimensions; the open questions that block the launch; what you assumed. Do not re-summarise the whole plan.

## Updating an existing plan
Edit `plan.json` (statuses, decided DRs, new tasks, new scores), rebuild, re-check the PDF. Keep IDs stable; a dropped task or decision keeps its ID retired, never reused.

## Guardrails
- Financial products, tokens, payments, investment claims: the claims rule and the legal OQ are mandatory, and the product gate must precede irreversible media/gift/venue commitments or the scorecard says so.
- Never publish the files anywhere without the user asking; they contain budgets and names.
- People are referred to by the names the user gave; do not guess roles or pronouns.
