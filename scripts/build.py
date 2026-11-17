#!/usr/bin/env python3
"""Build the GTM deliverables from one plan.json.

    python3 build.py <plan.json> [--out DIR] [--no-pdf] [--check-only]

Outputs (in --out, default: the plan's folder):
    <slug>_GTM_Presentation.html   Persian RTL presentation (slides mode + print-to-PDF layout)
    <slug>_GTM_Presentation.pdf    A4-landscape dark deck (needs Google Chrome; skipped otherwise)
    <slug>_GTM_Scorecard.html      evaluation dashboard (10-dimension scale, fixes, funnel, spend vs gate)

Exit code 1 when the plan has lint ERRORS (nothing is written). Warnings are printed and the build continues.
Dates in plan.json are Jalali strings "YYYY/MM/DD" (Latin or Persian digits).
"""
from __future__ import annotations

import base64
import datetime as dt
import io
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE.parent / "templates"
FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
TO_LATIN = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
MONTHS = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]

# The scale. Weights are fixed so scores stay comparable across plans (see references/scorecard.md).
DIMENSIONS = [
    (1, "شواهد و منابع", 15),
    (2, "پژوهش بازار و مقایسه", 10),
    (3, "پرسونای مشتری", 10),
    (4, "اهداف و معیارهای قابل اندازه‌گیری", 15),
    (5, "تصمیم‌ها با هزینهٔ گزینهٔ ردشده", 10),
    (6, "فرض‌ها و پرسش‌های باز", 5),
    (7, "زمان‌بندی و وابستگی‌ها", 10),
    (8, "تعریف «انجام‌شده» برای هر کار", 10),
    (9, "ریسک‌ها و حفاظ‌ها", 10),
    (10, "دروازه‌های Go / No-Go", 5),
]


# ---------------------------------------------------------------- Jalali calendar
def _div(a: int, b: int) -> int:
    return a // b


def jalali_to_gregorian(jy: int, jm: int, jd: int) -> dt.date:
    jy += 1595
    days = -355668 + (365 * jy) + (_div(jy, 33) * 8) + _div((jy % 33) + 3, 4) + jd
    days += (jm - 1) * 31 if jm < 7 else ((jm - 7) * 30) + 186
    gy = 400 * _div(days, 146097)
    days %= 146097
    if days > 36524:
        days -= 1
        gy += 100 * _div(days, 36524)
        days %= 36524
        if days >= 365:
            days += 1
    gy += 4 * _div(days, 1461)
    days %= 1461
    if days > 365:
        gy += _div(days - 1, 365)
        days = (days - 1) % 365
    gd = days + 1
    leap = (gy % 4 == 0 and gy % 100 != 0) or gy % 400 == 0
    month_days = [0, 31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 1
    while gm <= 12 and gd > month_days[gm]:
        gd -= month_days[gm]
        gm += 1
    return dt.date(gy, gm, gd)


def gregorian_to_jalali(d: dt.date) -> tuple[int, int, int]:
    gy, gm, gd = d.year, d.month, d.day
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gy2 = gy + 1 if gm > 2 else gy
    days = 355666 + (365 * gy) + _div(gy2 + 3, 4) - _div(gy2 + 99, 100) + _div(gy2 + 399, 400) + gd + g_d_m[gm - 1]
    jy = -1595 + (33 * _div(days, 12053))
    days %= 12053
    jy += 4 * _div(days, 1461)
    days %= 1461
    if days > 365:
        jy += _div(days - 1, 365)
        days = (days - 1) % 365
    if days < 186:
        jm, jd = 1 + _div(days, 31), 1 + (days % 31)
    else:
        jm, jd = 7 + _div(days - 186, 30), 1 + ((days - 186) % 30)
    return jy, jm, jd


def parse_jalali(s: str) -> dt.date:
    m = re.fullmatch(r"\s*(\d{4})[/-](\d{1,2})[/-](\d{1,2})\s*", str(s).translate(TO_LATIN))
    if not m:
        raise ValueError(f"not a Jalali date YYYY/MM/DD: {s!r}")
    return jalali_to_gregorian(*map(int, m.groups()))


def fa(n) -> str:
    return str(n).translate(FA_DIGITS)


def jlabel(d: dt.date, with_year: bool = False) -> str:
    y, m, dd = gregorian_to_jalali(d)
    return f"{fa(dd)} {MONTHS[m - 1]}" + (f" {fa(y)}" if with_year else "")


# ---------------------------------------------------------------- lint
class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


EVIDENCE = {"verified", "assumed", "unknown", "stated"}


def lint(p: dict, r: Report) -> None:
    for key in ["meta", "hero", "proposal", "segments", "tasks", "budget", "goals", "gates", "risks",
                "decisions", "open_questions", "assumptions", "ask", "scorecard"]:
        if key not in p:
            r.err(f"missing top-level key '{key}'")
    if r.errors:
        return
    meta = p["meta"]
    for k in ["brand", "start", "end", "launch", "product_gate"]:
        if not meta.get(k):
            r.err(f"meta.{k} is required")

    # goals: the target must be derived from a funnel, not asserted
    g = p["goals"]
    for k in ["target", "target_unit", "accounts", "funnel"]:
        if k not in g:
            r.err(f"goals.{k} is required (the sales target must be backed by a funnel)")
    f = g.get("funnel", {})
    for k in ["meet", "demo", "prop", "close", "ticket"]:
        if k not in f:
            r.err(f"goals.funnel.{k} is required")
    if f.get("evidence") not in EVIDENCE:
        r.err("goals.funnel.evidence must be one of verified/assumed/unknown/stated")
    if not r.errors:
        deals = g["accounts"] * f["meet"] / 100 * f["demo"] / 100 * f["prop"] / 100 * f["close"] / 100
        projected = deals * f["ticket"]
        if g["target"] and projected < 0.6 * g["target"]:
            r.warn(f"funnel projects {projected:,.0f} vs target {g['target']:,.0f} ({projected / g['target']:.0%}) — "
                   "either the target or the funnel is wrong; say so in the plan, do not hide it")

    # tasks: owner, dates, deliverable and a testable done-criterion
    ids = set()
    for t in p["tasks"]:
        tid = t.get("id")
        if tid in ids:
            r.err(f"duplicate task id {tid}")
        ids.add(tid)
        for k in ["title", "group", "owner", "deliverable", "start", "end"]:
            if not t.get(k):
                r.err(f"task {tid}: '{k}' is required")
        if not t.get("done"):
            r.warn(f"task {tid}: no 'done' criterion (definition of done) — scale dimension 8")
        if re.search(r"تعیین (شود|نشده)|TBD|TODO", str(t.get("owner", ""))):
            r.warn(f"task {tid}: owner is not decided ('{t['owner']}')")

    # budget
    b = p["budget"]
    if "reserve" not in b:
        r.err("budget.reserve is required (0 is allowed, but it must be stated)")
    elif not b["reserve"]:
        r.warn("budget.reserve is 0 — no contingency")
    gkeys = {x["key"] for x in b.get("groups", [])}
    for it in b.get("items", []):
        if it.get("group") not in gkeys:
            r.err(f"budget item '{it.get('name')}' has group '{it.get('group')}' not in budget.groups")
        if "commit" not in it:
            r.warn(f"budget item '{it.get('name')}' has no 'commit' window (use null when the plan has no date)")

    # decisions: decide, don't hedge
    for d in p["decisions"]:
        if d.get("status") == "decided":
            for k in ["chosen", "rejected", "cost"]:
                if not d.get(k):
                    r.err(f"{d.get('id')}: a decided record needs '{k}' (what lost and what it would have bought)")
        elif not d.get("due"):
            r.err(f"{d.get('id')}: an open decision needs a 'due' date")
    for q in p["open_questions"]:
        for k in ["id", "q", "owner", "due", "blocks"]:
            if not q.get(k):
                r.err(f"open question {q.get('id', '?')}: '{k}' is required")
    for a in p["assumptions"]:
        if not a.get("impact"):
            r.warn(f"assumption '{a.get('text', '')[:30]}…' has no impact-if-wrong")

    # gates
    for gt in p["gates"]:
        for k in ["date", "title", "criteria", "approver", "on_fail"]:
            if not gt.get(k):
                r.warn(f"gate '{gt.get('title', '?')}': '{k}' missing — scale dimension 10")

    # evidence: claims and sources
    srcs = p.get("sources", [])
    if not srcs:
        r.warn("no sources — scale dimension 1 cannot score above 2")
    for s in srcs:
        if not s.get("url"):
            r.warn(f"source {s.get('id')} has no URL")
    if not p.get("research", {}).get("benchmark"):
        r.warn("no research.benchmark — scale dimension 2 cannot score above 1")

    # scorecard
    sc = p["scorecard"]
    got = {d["id"] for d in sc.get("dims", [])}
    for i, _, _ in DIMENSIONS:
        if i not in got:
            r.err(f"scorecard.dims is missing dimension {i}")
    for d in sc.get("dims", []):
        if not 0 <= d.get("score", -1) <= 5:
            r.err(f"scorecard dimension {d.get('id')}: score must be 0–5")
        if not d.get("why"):
            r.err(f"scorecard dimension {d.get('id')}: 'why' is required (evidence for the score)")

    # dates inside the window
    try:
        s0, s1 = parse_jalali(meta["start"]), parse_jalali(meta["end"])
        if s1 <= s0:
            r.err("meta.end must be after meta.start")
        for t in p["tasks"]:
            a, z = parse_jalali(t["start"]), parse_jalali(t["end"])
            if z < a:
                r.err(f"task {t['id']}: end before start")
            if a < s0 or z > s1:
                r.warn(f"task {t['id']}: outside the campaign window")
    except (ValueError, KeyError) as e:
        r.err(str(e))


# ---------------------------------------------------------------- derive
def derive(p: dict) -> dict:
    meta = p["meta"]
    s0, s1 = parse_jalali(meta["start"]), parse_jalali(meta["end"])
    n = (s1 - s0).days + 1
    idx = lambda s: (parse_jalali(s) - s0).days  # noqa: E731
    days, months = [], []
    for i in range(n):
        d = s0 + dt.timedelta(days=i)
        y, m, dd = gregorian_to_jalali(d)
        days.append({"d": fa(dd), "fri": d.weekday() == 4})
        if not months or months[-1]["m"] != m:
            months.append({"m": m, "label": f"{MONTHS[m - 1]} {fa(y)}", "s": i, "e": i})
        else:
            months[-1]["e"] = i
    for t in p["tasks"]:
        t["s"], t["e"] = idx(t["start"]), idx(t["end"])
        t["span"] = f"{jlabel(parse_jalali(t['start']))} → {jlabel(parse_jalali(t['end']))}"
        t.setdefault("due_label", jlabel(parse_jalali(t["end"])))
    for ph in p.get("phases", []):
        ph["s"], ph["e"] = idx(ph["start"]), idx(ph["end"])
    for ms in p.get("milestones", []):
        ms["d"] = idx(ms["date"])
        ms["label"] = jlabel(parse_jalali(ms["date"]))
    for gt in p["gates"]:
        gt["label"] = gt.get("label") or jlabel(parse_jalali(gt["date"]))
    gate_i = idx(meta["product_gate"])
    before = unknown = 0
    for it in p["budget"]["items"]:
        c = it.get("commit")
        if c:
            it["cs"], it["ce"] = idx(c[0]), idx(c[1])
            if it["cs"] < gate_i:
                before += it["amount"]
        else:
            unknown += it["amount"]
    total = sum(it["amount"] for it in p["budget"]["items"])
    g = p["goals"]
    f = g["funnel"]
    deals = g["accounts"] * f["meet"] / 100 * f["demo"] / 100 * f["prop"] / 100 * f["close"] / 100
    sc_now = sum(next(d["score"] for d in p["scorecard"]["dims"] if d["id"] == i) / 5 * w for i, _, w in DIMENSIONS)
    p["_d"] = {
        "days": days, "n": n, "months": months,
        "start_iso": s0.isoformat(), "launch": idx(meta["launch"]), "gate": gate_i,
        "launch_label": jlabel(parse_jalali(meta["launch"])), "gate_label": jlabel(parse_jalali(meta["product_gate"])),
        "window_label": f"{jlabel(s0)} — {jlabel(s1, True)}",
        "axis": [[i, jlabel(s0 + dt.timedelta(days=i))] for i in sorted({0, gate_i, idx(meta['launch']), n - 1})],
        "budget_total": total, "before_gate": before, "unknown_commit": unknown,
        "per_account": g["target"] / g["accounts"] if g["accounts"] else 0,
        "deals": deals, "projected": deals * f["ticket"],
        "dims": [{"id": i, "n": name, "w": w} for i, name, w in DIMENSIONS],
        "score_now": round(sc_now, 1),
    }
    return p


# ---------------------------------------------------------------- assets
def data_uri(path: Path, width: int, recolor_dark_to: tuple | None = None, recolor_grey_to: tuple | None = None) -> str:
    try:
        from PIL import Image
    except ImportError:
        mime = "image/png" if path.suffix.lower() == ".png" else "image/svg+xml" if path.suffix.lower() == ".svg" else "image/jpeg"
        return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()
    if path.suffix.lower() == ".svg":
        return "data:image/svg+xml;base64," + base64.b64encode(path.read_bytes()).decode()
    im = Image.open(path).convert("RGBA")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    if recolor_dark_to or recolor_grey_to:
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                r_, g_, b_, a_ = px[x, y]
                if not a_:
                    continue
                if recolor_dark_to and max(r_, g_, b_) < 90:
                    px[x, y] = (*recolor_dark_to, a_)
                elif recolor_grey_to and abs(r_ - g_) < 12 and abs(g_ - b_) < 12 and r_ < 140:
                    px[x, y] = (*recolor_grey_to, a_)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=90, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


def assets(p: dict, base: Path) -> dict:
    logos = p["meta"].get("logos", {})
    out = {"primary": None, "icon": None, "partner": None, "orb": None}
    spec = {
        "primary": dict(width=700, recolor_dark_to=(245, 246, 250)),   # dark wordmark → white on the dark theme
        "icon": dict(width=260),
        "partner": dict(width=760, recolor_grey_to=(214, 219, 235)),   # grey wordmark → light grey
        "orb": dict(width=560),
    }
    for k, kw in spec.items():
        v = logos.get(k)
        if v:
            path = (base / v).expanduser()
            if path.exists():
                out[k] = data_uri(path, **kw)
            else:
                print(f"  ! logo '{k}' not found: {path}")
    return out


# ---------------------------------------------------------------- render
def render(template: str, p: dict, a: dict) -> str:
    html = (TEMPLATES / template).read_text(encoding="utf-8")
    payload = json.dumps(p, ensure_ascii=False).replace("</", "<\\/")
    html = html.replace("/*__PLAN__*/null", payload).replace("/*__ASSETS__*/null", json.dumps(a))
    title = f"{p['meta']['brand']} {p['meta'].get('campaign', 'Go to Market')}"
    html = html.replace("__TITLE__", title if template.startswith("presentation") else f"{p['meta']['brand']} Plan Scorecard")
    return html


def find_chrome() -> str | None:
    for c in ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              "/Applications/Chromium.app/Contents/MacOS/Chromium",
              shutil.which("google-chrome") or "", shutil.which("chromium") or "", shutil.which("chrome") or ""]:
        if c and Path(c).exists():
            return c
    return None


def main(argv: list[str]) -> int:
    if not argv or argv[0] in {"-h", "--help"}:
        print(__doc__)
        return 0
    plan_path = Path(argv[0]).resolve()
    out = Path(argv[argv.index("--out") + 1]).resolve() if "--out" in argv else plan_path.parent
    p = json.loads(plan_path.read_text(encoding="utf-8"))
    r = Report()
    lint(p, r)
    for w in r.warnings:
        print(f"WARN  {w}")
    for e in r.errors:
        print(f"ERROR {e}")
    if r.errors:
        print(f"\nFAIL — {len(r.errors)} error(s); nothing written.")
        return 1
    derive(p)
    print(f"lint OK ({len(r.warnings)} warning(s)) · scale score {p['_d']['score_now']}/100")
    if "--check-only" in argv:
        return 0
    out.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^A-Za-z0-9]+", "_", p["meta"].get("slug") or p["meta"]["brand"]).strip("_") or "Plan"
    a = assets(p, plan_path.parent)
    pres = out / f"{slug}_GTM_Presentation.html"
    card = out / f"{slug}_GTM_Scorecard.html"
    pres.write_text(render("presentation.html", p, a), encoding="utf-8")
    card.write_text(render("scorecard.html", p, a), encoding="utf-8")
    print(f"wrote {pres}\nwrote {card}")
    if "--no-pdf" not in argv:
        chrome = find_chrome()
        if not chrome:
            print("  ! Chrome not found — PDF skipped (use the PDF button in the presentation)")
        else:
            pdf = out / f"{slug}_GTM_Presentation.pdf"
            subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                            f"--print-to-pdf={pdf}", pres.as_uri()], capture_output=True, timeout=180)
            print(f"wrote {pdf}" if pdf.exists() else "  ! PDF export failed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
