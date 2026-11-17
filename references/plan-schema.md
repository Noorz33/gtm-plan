# plan.json schema

One JSON file per plan; `examples/sample/plan.json` is a complete valid (fictional) example — copy it and replace the content.
Dates are Jalali strings `"YYYY/MM/DD"` (Latin or Persian digits). Display labels (`due`, `label`, `due_label`) are free Persian text.
Colors: `copper | cyan | blue | green | violet | amber | red` (or any CSS color). Text fields are plain text; only `hero.headline` allows `<br>` and `<em>`.
Optional sections (`research`, `architecture`, `concepts`, `event`, `dependencies`, `phases`, `milestones`, `kpis`) are omitted from the page when absent.

```jsonc
{
  "meta": {
    "brand": "Parto", "brand_fa": "پرتو", "slug": "PARTO",         // slug → output file names
    "campaign": "Go to Market", "powered_by": "Partner",             // powered_by optional
    "start": "1405/08/26", "end": "1405/10/15",                      // Gantt window
    "launch": "1405/09/30", "product_gate": "1405/09/15",
    "logos": { "primary": "logo.png", "icon": "icon.png", "partner": "partner.png", "orb": "orb.png" }  // paths relative to plan.json; all optional
  },
  "hero": { "eyebrow": "...", "headline": "از ...<br>تا <em>...</em>", "lead": "..." },
  "kpis": [ { "label": "...", "value": 8650, "unit_inline": "میلیارد", "note": "...", "icon": "money|trend|target|people|calendar", "color": "copper" } ],  // max 4
  "proposal": { "title": "...", "lead": "...",
    "cards": [ { "title": "مسئله", "text": "...", "tone": "red|cyan|copper|green" } ],   // 4 cards: problem, idea, solution, result
    "storyline": "A ← B ← C", "storyline_src": "...", "steps": [ { "title": "...", "sub": "..." } ] },
  "research": { "title": "...", "lead": "...", "positioning": "...",
    "benchmark": [ { "name": "...", "what": "...", "lesson": "...", "evidence": "[VERIFIED — S-03, 1405/08/20]" } ] },
  "segments": { "title": "...", "lead": "...",
    "items": [ { "tag": "سگمنت ۰۱ · ...", "name": "...", "color": "copper", "desc": "...", "problem": "...",
                 "decision_maker": "...", "access": "...", "objections": "...", "proof": "...", "ticket": "..." } ],
    "sequence": { "title": "...", "note": "...", "steps": [ { "title": "...", "sub": "...", "color": "cyan" } ] } },
  "architecture": { "title": "...", "lead": "...", "merge": "...",
    "tracks": [ { "name": "...", "sub": "...", "color": "cyan", "steps": ["...", "..."] } ],
    "channels": [ { "name": "Owned Media", "text": "...", "color": "green" } ] },
  "concepts": { "title": "...", "lead": "...", "items": [ { "title": "...", "text": "...", "src": "..." } ],
    "deliverables_title": "...", "deliverables": ["..."], "claims_rule": "...", "dates_note": "..." },
  "event": { "title": "...", "lead": "...", "guests": [ { "label": "...", "n": 35, "color": "copper" } ],
    "decisions": ["..."], "runsheet": [ { "label": "...", "min": 10 } ] },
  "groups": { "فروش": "green", "محتوا": "cyan" },                    // task group → color
  "tasks": [ { "id": 1, "group": "فروش", "title": "...", "owner": "a name", "deliverable": "...",
               "done": "testable criterion", "start": "1405/08/26", "end": "1405/08/28",
               "due_label": "optional custom label", "dependency": "...", "detail": "..." } ],
  "phases": [ { "title": "فاز ۱ · ...", "start": "...", "end": "...", "color": "cyan" } ],
  "milestones": [ { "date": "1405/09/15", "title": "..." } ],         // diamonds on the Gantt
  "dependencies": [ { "chain": "A ← B ← C", "text": "...", "color": "cyan" } ],   // max 3 fits the PDF
  "budget": { "unit": "میلیون تومان", "reserve": 0, "unit_costs": "...", "note": "...",
    "groups": [ { "key": "رویداد", "label": "...", "color": "copper" } ],
    "items": [ { "name": "...", "amount": 1000, "group": "رویداد", "scope": "...",
                 "commit": ["1405/08/26", "1405/09/03"] /* or null */, "commit_note": "..." } ] },
  "goals": { "target": 1000, "target_unit": "میلیارد تومان", "accounts": 30,
    "funnel": { "meet": 70, "demo": 60, "prop": 60, "close": 40, "ticket": 33,
                "evidence": "verified|assumed|unknown|stated", "note": "..." } },
  "gates": [ { "date": "1405/09/15", "label": "optional", "title": "...", "criteria": "measurable",
               "approver": "a name", "on_fail": "stop / postpone / change scenario" } ],
  "risks": [ { "title": "...", "response": "..." } ],
  "decisions": [
    { "id": "DR-01", "title": "...", "status": "decided", "chosen": "...", "rejected": "...", "cost": "what the rejected option would have bought", "owner": "..." },
    { "id": "DR-02", "title": "...", "status": "open", "options": "A · B", "blocks": "...", "due": "۳ آذر", "owner": "..." } ],
  "open_questions": [ { "id": "OQ-01", "q": "...", "owner": "...", "due": "...", "blocks": "...", "critical": true } ],
  "assumptions": [ { "text": "...", "why": "...", "impact": "what breaks if wrong" } ],
  "sources": [ { "id": "S-01", "title": "...", "url": "https://...", "date": "1405/08/20" } ],
  "ask": { "title": "...", "lead": "...", "items": [ { "title": "...", "text": "..." } ] },   // 3 or 6 items fit the grid
  "footer": "...",
  "scorecard": { "note": "...",
    "dims": [ { "id": 1, "score": 2, "why": "evidence for the score", "fix": "..." } ],       // all 10 ids
    "fixes": [ { "id": "F1", "priority": 1, "title": "...", "desc": "...", "gain": { "4": 2.5, "1": 0.5 } } ] }
}
```

## Fit limits for the PDF (one section per A4-landscape page)
- tasks ≤ 14 (action table and Gantt each fit one page) · budget items ≤ 14 · segments 3 · concepts 4 · benchmark 3 or 6 · gates ≤ 6 · risks ≤ 7.
- Keep `detail` under ~200 characters and card texts under ~180; long text pushes sections onto a second page where the repeating header overlaps content.
