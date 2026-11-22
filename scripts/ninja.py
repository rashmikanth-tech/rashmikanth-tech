# Copyright (c) 2026 Rashmikanth G R (https://github.com/rashmikanth-tech)
# Code: MIT. The animation, its characters and design: CC BY 4.0, credit required. See LICENSE.
"""Draws assets/ninja.svg: a ninja fights your programming languages and a boss; the score climbs to your real contribution count.

Usage:  python scripts/ninja.py      # needs GH_TOKEN (the Action's GITHUB_TOKEN works)

- Score, this-year count and streak come from the contribution calendar, which includes private repos (the profile shows them).
- Languages and their share of the points come from assets/languages.json: bytes of code per language across your own repos.
  It is refreshed only when the token can see private repos (a STATS_TOKEN secret in the Action, or `gh auth token` locally);
  GITHUB_TOKEN sees public repos only, so with it the saved snapshot is kept.
- The fight is different every day: the date seeds the order of languages and moves.
"""
import datetime as dt
import json
import os
import random
import urllib.request

USER = "rashmikanth-tech"
W, H = 880, 320
GROUND = 262          # y of the ground line

LANG_FILE = "assets/languages.json"
NOT_CODE = {"CMake", "Roff", "Dockerfile", "Batchfile", "Inno Setup", "Mako", "Vim Snippet", "Go Template", "Hack", "Makefile",
            "Procfile", "Jupyter Notebook", "Smarty", "Twig", "EJS", "Handlebars", "Cython", "Starlark"}
RENAME = {"PLpgSQL": "SQL", "TSQL": "SQL", "Shell": "Bash"}


def gql(query):
    req = urllib.request.Request("https://api.github.com/graphql", json.dumps({"query": query}).encode(),
                                 {"Authorization": f"bearer {os.environ['GH_TOKEN']}", "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))["data"]["user"]


def stats():
    """Total contributions, this year's, current daily streak, and the per-language code mix."""
    first = int(gql(f'{{user(login:"{USER}"){{createdAt}}}}')["createdAt"][:4])
    today = dt.datetime.now(dt.timezone.utc).date()
    per_year, days = {}, {}
    for y in range(first, today.year + 1):  # the API allows at most one year per query
        c = gql(f'{{user(login:"{USER}"){{contributionsCollection(from:"{y}-01-01T00:00:00Z",to:"{y}-12-31T23:59:59Z")'
                f'{{contributionCalendar{{totalContributions weeks{{contributionDays{{date contributionCount}}}}}}}}}}}}')["contributionsCollection"]["contributionCalendar"]
        per_year[y] = c["totalContributions"]
        days.update({d["date"]: d["contributionCount"] for w in c["weeks"] for d in w["contributionDays"]})
    streak, day = 0, today
    if not days.get(day.isoformat()):  # today not started yet: count from yesterday
        day -= dt.timedelta(days=1)
    while days.get(day.isoformat()):
        streak += 1
        day -= dt.timedelta(days=1)
    return sum(per_year.values()), per_year[today.year], streak, languages()


def languages():
    """{language: (bytes, colour)} across your own non-fork repos; the saved snapshot unless this token sees private repos."""
    saved = json.load(open(LANG_FILE, encoding="utf-8")) if os.path.exists(LANG_FILE) else {}
    repos = gql(f'{{user(login:"{USER}"){{repositories(ownerAffiliations:OWNER,isFork:false,first:100){{nodes{{isPrivate '
                f'languages(first:20){{edges{{size node{{name color}}}}}}}}}}}}}}')["repositories"]["nodes"]
    if saved and not any(r["isPrivate"] for r in repos):
        return saved
    mix = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            name = RENAME.get(e["node"]["name"], e["node"]["name"])
            if name in NOT_CODE:
                continue
            size, colour = mix.get(name, (0, e["node"]["color"] or "#888888"))
            mix[name] = (size + e["size"], colour)
    mix = dict(sorted(mix.items(), key=lambda kv: -kv[1][0]))
    with open(LANG_FILE, "w", encoding="utf-8") as f:
        json.dump(mix, f, indent=1)
    return mix


BELTS = [(100, "BLACK", "#0a0a0a"), (60, "BROWN", "#7c4a1e"), (30, "BLUE", "#2563eb"), (14, "GREEN", "#16a34a"),
         (7, "ORANGE", "#ea580c"), (3, "YELLOW", "#facc15"), (0, "WHITE", "#f8fafc")]


def belt(streak):
    """Belt name and colour for a daily streak: white under 3 days ... black at 100+."""
    return next((name, col) for need, name, col in BELTS if streak >= need)


def pct(t):
    return f"{max(0.0, min(100.0, t / T * 100)):.3f}%"


def glyph(kind, fg):
    if kind == "flutter":
        return (f'<path d="M-4,-14 L6,-14 L-7,-1 L-12,-6 Z" fill="{fg}"/>'
                f'<path d="M-1,-2 L9,-2 L2,5 L9,12 L-1,12 L-8,5 Z" fill="{fg}"/>')
    if kind == "java":
        return ('<path d="M-9,-1 h15 v7 a7,7 0 0 1 -7,7 h-1 a7,7 0 0 1 -7,-7 Z" fill="#fff"/>'
                '<path d="M6,1 a4,4 0 0 1 0,7" stroke="#fff" stroke-width="2.4" fill="none"/>'
                '<path d="M-4,-5 q-3,-4 0,-8 M1,-5 q-3,-4 0,-8" stroke="#fff" stroke-width="2.2" fill="none" stroke-linecap="round"/>')
    if kind == "dart":
        return f'<path d="M-11,-3 L-3,-11 L11,-11 L11,3 L3,11 L-11,11 Z" fill="{fg}"/><path d="M-3,-11 L11,3 L11,-11 Z" fill="#ffffff" opacity=".55"/>'
    if kind == "py":
        return ('<rect x="-11" y="-11" width="13" height="13" rx="4" fill="#ffffff"/>'
                '<rect x="-2" y="-2" width="13" height="13" rx="4" fill="#FFD43B"/>'
                '<circle cx="-7" cy="-7" r="1.6" fill="#3776AB"/><circle cx="7" cy="7" r="1.6" fill="#3776AB"/>')
    size = 15 if len(kind) <= 2 else 12
    return (f'<text x="0" y="{size * 0.36:.1f}" text-anchor="middle" font-family="Segoe UI,Helvetica,Arial,sans-serif" '
            f'font-weight="800" font-size="{size}" fill="{fg}">{kind}</text>')





# Hand-drawn glyphs for languages that have one; anything else gets GitHub's colour and its initials.
# label -> (colour, glyph colour, glyph). Glyphs are simple marks drawn here, not the official logos.
LANG = {
    "Flutter": ("#02569B", "#54C5F8", "flutter"), "Java": ("#E76F00", "#ffffff", "java"),
    "Dart": ("#0175C2", "#7FD6F7", "dart"), "Kotlin": ("#7F52FF", "#ffffff", "K"),
    "Go": ("#00ADD8", "#ffffff", "Go"), "Python": ("#3776AB", "#FFD43B", "py"),
    "TypeScript": ("#3178C6", "#ffffff", "TS"), "JavaScript": ("#F7DF1E", "#1a1a1a", "JS"),
    "PHP": ("#777BB4", "#ffffff", "php"), "SQL": ("#336791", "#ffffff", "SQL"), "Swift": ("#F05138", "#ffffff", "Sw"),
    "C++": ("#00599C", "#ffffff", "C++"), "Rust": ("#CE422B", "#ffffff", "Rs"), "C#": ("#68217A", "#ffffff", "C#"),
    "Ruby": ("#CC342D", "#ffffff", "rb"), "HTML": ("#E34F26", "#ffffff", "&lt;/&gt;"), "CSS": ("#1572B6", "#ffffff", "{ }"),
    "Bash": ("#3a3a3a", "#4EAA25", "$_"), "Lua": ("#2C2D72", "#ffffff", "Lua"), "Blade": ("#f7523f", "#ffffff", "Bl"),
    "C": ("#555555", "#ffffff", "C"),
}
MAX_ORBS = 20
BOSS_SHARE = 0.15   # the boss's three hits are worth 15% of the score; languages share the rest by bytes of code


def look(name, colour):
    if name in LANG:
        return LANG[name]
    r, g, b = (int(colour[i:i + 2], 16) for i in (1, 3, 5))
    fg = "#1a1a1a" if r * .299 + g * .587 + b * .114 > 160 else "#ffffff"
    return colour, fg, "".join(w[0] for w in name.replace("-", " ").split())[:3] if " " in name or "-" in name else name[:2]


def split(total, weights):
    """Whole-number points in proportion to weights that add up exactly to total (largest remainder)."""
    raw = [total * w / sum(weights) for w in weights]
    pts = [int(x) for x in raw]
    for i in sorted(range(len(raw)), key=lambda i: pts[i] - raw[i])[:total - sum(pts)]:
        pts[i] += 1
    return pts


def setup(mix, seed):
    """Picks today's languages and moves (seeded by the date) and sets the timeline: EVENTS, TB, HITS, T."""
    global EVENTS, TB, HITS, T
    names = list(mix)[:MAX_ORBS - 1]
    if "Dart" in names:  # Dart here is Flutter apps: show both, sharing Dart's bytes
        mix = dict(mix)
        mix["Flutter"] = mix["Dart"] = (mix["Dart"][0] / 2, mix["Dart"][1])
        names.insert(names.index("Dart"), "Flutter")
    rng = random.Random(seed)
    rng.shuffle(names)
    events, g = [], 300
    while names:
        kind = "leap" if not events else rng.choices(["leap", "attack", "star", "double"], [4, 3, 2, 2])[0]
        if kind == "double" and (len(names) < 2 or not 130 < g < W - 130):
            kind = "attack"
        if kind in ("leap", "star"):
            cx = rng.randrange(150, 601)  # stays clear of the score in the top-right corner
            cy = rng.randrange(100, 161)
            events.append((kind, names.pop(), cx, cy))
            if kind == "leap":
                g = max(60, min(W - 60, cx + (60 if cx >= g else -60)))
        elif kind == "attack":
            side = 1 if g < 140 else -1 if g > W - 140 else rng.choice([-1, 1])
            events.append(("attack", names.pop(), side))
        else:
            events.append(("double", names.pop(), names.pop()))
    EVENTS = events
    TB = 0.05 + SLOT * len(EVENTS) + 0.3       # the boss arrives
    HITS = [TB + 1.75, TB + 2.5, TB + 3.2]     # dash slash, flip slash, spin finisher
    T = HITS[-1] + 2.1                         # then GAME CLEAR, then the round restarts
    return mix


# The round, move by move (built by setup()):
#   leap   (lang, cx, cy)       an orb is tossed up; the ninja flips up to it and slashes
#   star   (lang, cx, cy)       he throws a shuriken at a tossed orb
#   attack (lang, side)         an orb charges at him along the ground from side -1 (left) or 1 (right); he counter-slashes
#   double (left, right)        two orbs charge from both sides at once; he spins and cuts both
# Then the boss fight: THE BUG drops in, spits a fireball, and takes three hits.
SLOT = 0.75         # seconds per move
BX = 680            # boss x
EVENTS, TB, HITS, T = [], 0, [], 1
REACH = 46          # how far from the ninja a charging orb is cut


def kf(name, frames, loop=True, first=None):
    """@keyframes from (time, css) pairs. 0% takes `first`, else the last frame's value (loop) or the first frame's."""
    frames = sorted(frames, key=lambda f: f[0])
    start = first if first is not None else frames[-1][1] if loop else frames[0][1]
    out = [("0%", start)] + [(pct(t), c) for t, c in frames] + [("100%", frames[-1][1])]
    return f"@keyframes {name} {{ " + " ".join(f"{p} {{ {c} }}" for p, c in out) + " }"


FIGURE = '''<ellipse cx="0" cy="2" rx="18" ry="4" fill="#000" opacity=".35"/>
      <path d="M-7,-18 L-13,0 M6,-18 L13,-2" stroke="#111827" stroke-width="7" stroke-linecap="round"/>
      <path d="M-12,-40 q12,-8 24,0 l-2,24 q-10,4 -20,0 Z" fill="#111827"/>
      <path d="M-12,-26 h24" stroke="#EA580C" stroke-width="4"/>
      <circle cx="0" cy="-52" r="13" fill="#111827"/>
      <rect x="-10" y="-56" width="22" height="7" rx="3.5" fill="#f2d2b6"/>
      <path d="M-2,-54 l5,1.5 M6,-53 l5,-1.5" stroke="#111" stroke-width="2.2" stroke-linecap="round"/>
      <path d="M-13,-60 h26" stroke="#E11D48" stroke-width="4"/>
      <path class="tail" d="M-6,-46 q-14,-6 -26,4 q-8,6 -18,2" stroke="#E11D48" stroke-width="3.5" fill="none" stroke-linecap="round" transform="translate(-6,-14)"/>
      <g transform="translate(9,-34)"><g class="sword"DELAY>
        <path d="M0,0 L10,0" stroke="#111827" stroke-width="7" stroke-linecap="round"/>
        <rect x="8" y="-4" width="3" height="8" fill="#FBBF24"/>
        <path d="M11,-1.8 L64,-1.8 L70,0 L64,1.8 L11,1.8 Z" fill="#f1f5f9" stroke="#94a3b8" stroke-width=".6"/>
      </g></g>'''


BELT_PATH = '<path d="M-12,-26 h24" stroke="#EA580C" stroke-width="4"/>'


def ninja(delay, opacity, tint=""):
    """The ninja, or (with a delay and tint) one of its motion-blur afterimages."""
    dl = f' style="animation-delay:{delay}s"' if delay else ""
    fig = FIGURE.replace("DELAY", dl)
    if tint:
        fig = fig.replace("#111827", tint).replace("#f2d2b6", tint)
    return (f'<g class="pos"{dl} opacity="{opacity}"><g transform="translate(0,-34)"><g class="flip"{dl}><g transform="translate(0,34)">'
            f'<g class="face"{dl}>{fig}</g></g></g></g></g>')


def choreograph(g=None):
    """Turns EVENTS into orb flights and the ninja's keyframes. Returns (orbs, words, star throws, ninja frames).
    The ninja starts where the round ends, so the loop joins up: a first pass finds that spot."""
    if g is None:
        g = choreograph(120)[-1]
    orbs, words, stars = [], [], []
    pos, flip, face, sword = [], [], [], []
    for i, ev in enumerate(EVENTS):
        t0 = 0.05 + i * SLOT
        tc = t0 + 0.45
        how = ev[0]
        if how in ("leap", "star"):
            _, lang, cx, cy = ev
            d = 1 if cx >= g else -1
            od = -1 if i % 2 else 1
            orbs.append(dict(lang=lang, start=(cx - od * 120, H + 40), cut=(cx, cy), t0=t0, tc=tc, drift=od * 30, toss=True))
            face.append((t0, f"transform: scaleX({d})"))
        if how == "leap":
            land = max(60, min(W - 60, cx + d * 60))
            pos += [(t0 + 0.12, f"transform: translate({g}px,{GROUND}px)"),
                    (t0 + 0.19, f"transform: translate({g - d * 4}px,{GROUND + 4}px); animation-timing-function: cubic-bezier(.1,.7,.3,1)"),
                    (tc, f"transform: translate({cx - d * 36}px,{cy + 40}px); animation-timing-function: linear"),
                    (tc + 0.08, f"transform: translate({cx + d * 10}px,{cy + 28}px); animation-timing-function: cubic-bezier(.5,0,1,.5)"),
                    (t0 + 0.74, f"transform: translate({land}px,{GROUND}px)")]
            flip += [(t0 + 0.19, "transform: rotate(0deg)"), (tc - 0.05, f"transform: rotate({d * 360}deg)"),
                     (tc - 0.049, "transform: rotate(0deg)"), (tc + 0.09, f"transform: rotate({d * 25}deg)"), (t0 + 0.74, "transform: rotate(0deg)")]
            sword += [(t0 + 0.17, "transform: rotate(-35deg)"), (t0 + 0.25, "transform: rotate(-150deg)"), (tc - 0.03, "transform: rotate(-170deg)"),
                      (tc + 0.05, "transform: rotate(45deg)"), (t0 + 0.74, "transform: rotate(-35deg)")]
            g = land
            words.append((tc, None))
        elif how == "star":
            pos += [(t0 + 0.1, f"transform: translate({g}px,{GROUND}px)"), (t0 + 0.17, f"transform: translate({g}px,{GROUND - 26}px)"),
                    (t0 + 0.3, f"transform: translate({g}px,{GROUND}px)")]
            sword += [(t0 + 0.1, "transform: rotate(-35deg)"), (t0 + 0.15, "transform: rotate(-120deg)"), (t0 + 0.22, "transform: rotate(30deg)"),
                      (t0 + 0.65, "transform: rotate(-35deg)")]
            stars.append((i, g + d * 20, t0 + 0.22, cx, cy, tc, cx + (cx - g) * .6))
            words.append((tc, "SHURIKEN!"))
        elif how == "attack":
            _, lang, side = ev
            hit = g + side * REACH
            orbs.append(dict(lang=lang, start=(-40 if side < 0 else W + 40, GROUND - 38), cut=(hit, GROUND - 38), t0=t0, tc=tc,
                             drift=side * 50, toss=False))
            face.append((t0, f"transform: scaleX({side})"))
            pos += [(tc - 0.12, f"transform: translate({g}px,{GROUND}px)"), (tc, f"transform: translate({g + side * 14}px,{GROUND}px)"),
                    (t0 + 0.7, f"transform: translate({g}px,{GROUND}px)")]
            sword += [(t0 + 0.15, "transform: rotate(-35deg)"), (tc - 0.08, "transform: rotate(-160deg)"), (tc + 0.03, "transform: rotate(40deg)"),
                      (t0 + 0.7, "transform: rotate(-35deg)")]
            words.append((tc, "COUNTER!"))
        else:  # double
            _, left, right = ev
            for lang, side in ((left, -1), (right, 1)):
                orbs.append(dict(lang=lang, start=(-40 if side < 0 else W + 40, GROUND - 38), cut=(g + side * REACH, GROUND - 38),
                                 t0=t0, tc=tc, drift=side * 50, toss=False))
            pos += [(t0 + 0.2, f"transform: translate({g}px,{GROUND}px)"), (tc, f"transform: translate({g}px,{GROUND - 30}px)"),
                    (t0 + 0.72, f"transform: translate({g}px,{GROUND}px)")]
            flip += [(tc - 0.2, "transform: rotate(0deg)"), (tc + 0.12, "transform: rotate(360deg)"), (tc + 0.121, "transform: rotate(0deg)")]
            sword += [(t0 + 0.2, "transform: rotate(-35deg)"), (tc - 0.15, "transform: rotate(0deg)"), (tc + 0.12, "transform: rotate(0deg)"),
                      (t0 + 0.72, "transform: rotate(-35deg)")]
            words.append((tc, "DOUBLE KILL!"))
    # boss fight
    h1, h2, h3 = HITS
    G = GROUND

    def at(t, x, y=G):
        pos.append((t, f"transform: translate({x}px,{y}px)"))
    face.append((TB, "transform: scaleX(1)"))
    at(TB + 0.1, g); at(TB + 0.45, 260)
    at(TB + 1.12, 260); at(TB + 1.27, 260, G - 72); at(TB + 1.45, 260)          # jump the fireball
    at(h1 - 0.1, 300); at(h1, BX - 95); at(h1 + 0.25, 470)                        # dash slash
    at(h2 - 0.3, 470); at(h2, BX - 70, G - 120); at(h2 + 0.08, BX - 50, G - 110); at(h2 + 0.4, 470)
    at(h3 - 0.3, 470); at(h3, BX - 80, G - 45); at(h3 + 0.35, 450)
    tv = h3 + 0.7
    at(tv, 450); at(tv + 0.18, 450, G - 40); at(tv + 0.36, 450)                  # victory hop
    flip += [(h2 - 0.3, "transform: rotate(0deg)"), (h2 - 0.05, "transform: rotate(360deg)"), (h2 - 0.049, "transform: rotate(0deg)"),
             (h3 - 0.25, "transform: rotate(0deg)"), (h3 + 0.1, "transform: rotate(720deg)"), (h3 + 0.101, "transform: rotate(0deg)"),
             (tv, "transform: rotate(0deg)"), (tv + 0.36, "transform: rotate(-360deg)"), (tv + 0.361, "transform: rotate(0deg)")]
    sword += [(TB + 0.1, "transform: rotate(-35deg)"),
              (h1 - 0.15, "transform: rotate(-35deg)"), (h1 - 0.05, "transform: rotate(-160deg)"), (h1 + 0.04, "transform: rotate(40deg)"),
              (h2 - 0.25, "transform: rotate(-150deg)"), (h2 - 0.03, "transform: rotate(-170deg)"), (h2 + 0.05, "transform: rotate(45deg)"),
              (h3 - 0.25, "transform: rotate(0deg)"), (h3 + 0.1, "transform: rotate(0deg)"), (h3 + 0.35, "transform: rotate(-35deg)"),
              (tv, "transform: rotate(-35deg)"), (tv + 0.2, "transform: rotate(-95deg)"), (tv + 0.9, "transform: rotate(-95deg)"),
              (tv + 1.1, "transform: rotate(-35deg)")]
    words += [(h1, "HIT!"), (h2, "CRITICAL!"), (h3, "K.O.!")]
    g = 450
    return orbs, words, stars, (pos, flip, face, sword), g


def score_strip(values, times, total):
    """An arcade score: one rolling digit column per place value; leading places and the comma appear as the score grows."""
    css, parts = [], []
    places = len(str(total))
    x = 0
    for p in range(places):
        if p and p % 3 == 0:  # comma between thousands
            x -= 9
            frames = [(t + 0.12, f"opacity:{1 if v >= 10 ** p else 0}") for t, v in zip(times, values)]
            css.append(kf(f"cm{p}", frames, loop=False, first="opacity:0") + f" .cm{p}{{animation:cm{p} {T}s infinite step-end}}")
            parts.append(f'<text class="cm{p}" x="{x + 4}" y="0" text-anchor="middle">,</text>')
        x -= 20
        frames, shown = [], []
        prev = 0
        for t, v in zip(times, values):
            dgt = (v // 10 ** p) % 10
            frames += [(t, f"transform: translateY({-36 * prev}px)"), (t + 0.14, f"transform: translateY({-36 * dgt}px)")]
            shown.append((t, f"opacity:{1 if (v >= 10 ** p or p == 0) else 0}"))
            prev = dgt
        css.append(kf(f"dg{p}", frames, loop=False, first="transform: translateY(0px)") + f" .dg{p}{{animation:dg{p} {T}s infinite ease-out}}")
        if p:
            css.append(kf(f"dv{p}", shown, loop=False, first="opacity:0") + f" .dv{p}{{animation:dv{p} {T}s infinite step-end}}")
        digits = "".join(f'<text x="0" y="{36 * k}" text-anchor="middle">{k}</text>' for k in range(10))
        parts.append(f'<g class="dv{p}" transform="translate({x + 10},0)" clip-path="url(#dig)"><g class="dg{p}">{digits}</g></g>')
    return css, "".join(parts)


BOSS = '''<ellipse cx="0" cy="2" rx="74" ry="8" fill="#000" opacity=".45"/>
      <path d="M-36,-30 L-62,-14 L-70,0 M-6,-22 L-14,-6 L-18,0 M26,-26 L44,-10 L50,0 M50,-34 L74,-16 L80,0" stroke="#3b0a0a" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
      <ellipse cx="6" cy="-60" rx="66" ry="52" fill="#7f1d1d"/>
      <ellipse cx="14" cy="-66" rx="54" ry="42" fill="#b91c1c"/>
      <path d="M14,-108 L14,-26" stroke="#7f1d1d" stroke-width="3"/>
      <circle cx="-6" cy="-80" r="7" fill="#7f1d1d"/><circle cx="36" cy="-86" r="9" fill="#7f1d1d"/><circle cx="40" cy="-52" r="6" fill="#7f1d1d"/><circle cx="-8" cy="-46" r="5" fill="#7f1d1d"/>
      <path d="M-58,-78 q-12,-30 -32,-34 M-44,-80 q2,-32 -10,-46" stroke="#450a0a" stroke-width="4" fill="none" stroke-linecap="round"/>
      <circle cx="-90" cy="-112" r="5" fill="#f87171"/><circle cx="-54" cy="-126" r="5" fill="#f87171"/>
      <circle cx="-52" cy="-52" r="32" fill="#450a0a"/>
      <circle cx="-64" cy="-60" r="10" fill="#fde047"/><circle cx="-40" cy="-62" r="10" fill="#fde047"/>
      <circle cx="-68" cy="-58" r="4.5" fill="#111"/><circle cx="-44" cy="-60" r="4.5" fill="#111"/>
      <path d="M-76,-74 L-56,-68 M-28,-74 L-46,-70" stroke="#111" stroke-width="4" stroke-linecap="round"/>
      <path d="M-78,-36 q-18,4 -14,22 M-60,-28 q-10,12 0,22" stroke="#fbbf24" stroke-width="5" fill="none" stroke-linecap="round"/>
      <text x="18" y="-58" text-anchor="middle" font-family="Impact,Arial Black,sans-serif" font-size="18" fill="#fecaca" opacity=".85">BUG</text>'''


def boss(css, shake, flash):
    """THE BUG: drops in, bobs, spits a fireball, recoils from each hit, then explodes. Has an HP bar."""
    h1, h2, h3 = HITS
    a = f"{T}s infinite"
    hidden = "transform: translate(0px,-340px) scale(1); opacity:0"
    frames = [(TB - 0.001, hidden), (TB, "transform: translate(0px,-340px) scale(1); opacity:1; animation-timing-function: cubic-bezier(.5,0,1,.6)"),
              (TB + 0.35, "transform: translate(0px,0px) scale(1); opacity:1")]
    for h in HITS:
        frames += [(h, "transform: translate(0px,0px) scale(1); opacity:1"), (h + 0.05, "transform: translate(16px,0px) scale(1); opacity:1"),
                   (h + 0.2, "transform: translate(0px,0px) scale(1); opacity:1")]
    frames = [f for f in frames if f[0] < h3 + 0.02] + [(h3 + 0.02, "transform: translate(0px,0px) scale(1); opacity:1"),
                                                        (h3 + 0.3, "transform: translate(0px,0px) scale(1.35); opacity:0"), (h3 + 0.302, hidden)]
    css.append(kf("boss", frames, loop=False, first=hidden) + f" .boss{{animation:boss {a} linear}}")
    css.append(kf("bflash", [f for h in HITS for f in [(h, "opacity:0"), (h + 0.02, "opacity:.9"), (h + 0.14, "opacity:0")]], loop=False)
               + f" .bflash{{animation:bflash {a} linear}}")
    css.append("@keyframes bob { 0%,100% { transform: translateY(0) } 50% { transform: translateY(-5px) } } .bob{animation:bob .5s infinite ease-in-out}")
    css.append(kf("boom", [(h3, "transform: scale(.2); opacity:0"), (h3 + 0.03, "transform: scale(.6); opacity:1"), (h3 + 0.7, "transform: scale(2.6); opacity:0")], loop=False)
               + f" .boom{{animation:boom {a} ease-out}}")
    css.append(kf("hp", [(TB + 0.4, "opacity:0"), (TB + 0.55, "opacity:1"), (h3 + 0.3, "opacity:1"), (h3 + 0.5, "opacity:0")], loop=False)
               + f" .hp{{animation:hp {a} linear}}")
    left = [(TB, "transform: scaleX(1)")]
    for k, h in enumerate(HITS):
        left += [(h, f"transform: scaleX({1 - k / 3:.3f})"), (h + 0.15, f"transform: scaleX({1 - (k + 1) / 3:.3f})")]
    css.append(kf("hpf", left, loop=False) + f" .hpf{{animation:hpf {a} ease-out}}")
    css.append(kf("fire", [(TB + 0.949, f"transform: translate({BX - 70}px,{GROUND - 40}px); opacity:0"),
                           (TB + 0.95, f"transform: translate({BX - 70}px,{GROUND - 40}px); opacity:1"),
                           (TB + 1.6, f"transform: translate(-40px,{GROUND - 40}px); opacity:1"),
                           (TB + 1.602, f"transform: translate(-40px,{GROUND - 40}px); opacity:0")], loop=False)
               + f" .fire{{animation:fire {a} linear}}")
    blink = [(TB - 0.25, "opacity:0")] + [(TB - 0.15 + k * 0.22, f"opacity:{1 if k % 2 == 0 else .15}") for k in range(6)] + [(TB + 1.2, "opacity:0")]
    css.append(kf("warn", blink, loop=False) + f" .warn{{animation:warn {a} linear}}")
    shake += [(TB + 0.349, "transform: translate(0,0)"), (TB + 0.37, "transform: translate(0,8px)"), (TB + 0.42, "transform: translate(0,-5px)"),
              (TB + 0.48, "transform: translate(0,0)")]
    flash += [(h3 + 0.13, "opacity:0"), (h3 + 0.15, "opacity:.5"), (h3 + 0.4, "opacity:0")]
    whites = BOSS.replace('fill="#', 'fill="#ffffff" data-f="#').replace('stroke="#', 'stroke="#ffffff" data-s="#')
    boom = "".join(f'<circle cx="{40 * __import__("math").cos(k * 0.5236):.0f}" cy="{40 * __import__("math").sin(k * 0.5236):.0f}" r="{6 + k % 3 * 3}" '
                   f'fill="{["#b91c1c", "#fbbf24", "#f97316"][k % 3]}"/>' for k in range(12))
    return f'''
  <g transform="translate(0,0)"><g class="fire"><circle r="13" fill="#f97316" filter="url(#glow)"/><circle r="7" fill="#fde047"/>
    <path d="M10,-8 l20,-4 M12,0 l26,0 M10,8 l20,4" stroke="#f97316" stroke-width="3" stroke-linecap="round" opacity=".7"/></g></g>
  <g transform="translate({BX},{GROUND})">
    <g class="boss"><g class="bob">{BOSS}<g class="bflash" opacity="0">{whites}</g></g></g>
    <g transform="translate(0,-58)"><g class="boom">{boom}</g></g>
  </g>
  <g class="hp" opacity="0" transform="translate({BX - 80},{GROUND - 150})" font-family="Segoe UI,Helvetica,Arial,sans-serif">
    <text x="0" y="-6" font-size="12" font-weight="900" fill="#fca5a5" letter-spacing="1.5">BOSS · THE BUG</text>
    <rect width="160" height="10" rx="5" fill="#3b0a0a" stroke="#fca5a5" stroke-width="1"/>
    <rect class="hpf" width="160" height="10" rx="5" fill="#ef4444"/>
  </g>
  <g transform="translate({W // 2},132)"><g class="warn" opacity="0" text-anchor="middle" font-family="Impact,Segoe UI Black,Arial Black,sans-serif" font-style="italic">
    <text font-size="34" fill="#ef4444" stroke="#1f0505" stroke-width="5" paint-order="stroke">WARNING!</text>
    <text y="26" font-size="16" fill="#fecaca" stroke="#1f0505" stroke-width="4" paint-order="stroke">BOSS APPROACHING: THE BUG</text></g></g>'''


def build(total, year, streak, mix):
    orbs, words, stars, (pos, flip, face, sword), _ = choreograph()
    # points: languages share most of the score by bytes of code, the boss's hits the rest; it lands exactly on the total
    boss_pts = round(total * BOSS_SHARE)
    lang_pts = dict(zip([o["lang"] for o in orbs], split(total - boss_pts, [mix[o["lang"]][0] for o in orbs])))
    hit_pts = split(boss_pts, [1, 1, 1])
    cut_times = sorted({o["tc"] for o in orbs} | set(HITS))
    values, gain, score = [], {}, 0
    for t in cut_times:
        g = sum(lang_pts[o["lang"]] for o in orbs if o["tc"] == t) + (hit_pts[HITS.index(t)] if t in HITS else 0)
        score += g
        gain[t] = g
        values.append(score)
    css, body, shake, flash, bump = [], [], [], [], []
    for i, o in enumerate(orbs):
        col, fg, kind = look(o["lang"], mix[o["lang"]][1])
        (sx, sy), (cx, cy), t0, tc = o["start"], o["cut"], o["t0"], o["tc"]
        launch = "cubic-bezier(.15,.6,.4,1)" if o["toss"] else "cubic-bezier(.5,0,.9,.5)"
        css.append(kf(f"o{i}", [
            (t0 - 0.002, f"transform: translate({sx}px,{sy}px); opacity:0"),
            (t0, f"transform: translate({sx}px,{sy}px); opacity:1; animation-timing-function: {launch}"),
            (tc, f"transform: translate({cx}px,{cy}px); opacity:1; animation-timing-function: cubic-bezier(.6,0,1,.6)"),
            (tc + 0.4, f"transform: translate({cx + o['drift']}px,{H + 30}px); opacity:1"),
            (tc + 0.402, f"transform: translate({cx + o['drift']}px,{H + 30}px); opacity:0")], loop=False))
        css.append(kf(f"ha{i}", [(tc, "transform: translate(0,0) rotate(0)"), (tc + 0.4, "transform: translate(-60px,-14px) rotate(-120deg)")], loop=False))
        css.append(kf(f"hb{i}", [(tc, "transform: translate(0,0) rotate(0)"), (tc + 0.4, "transform: translate(60px,12px) rotate(130deg)")], loop=False))
        css.append(kf(f"sl{i}", [(tc - 0.03, "transform: scale(.3); opacity:0"), (tc + 0.03, "transform: scale(1.15); opacity:1"),
                                 (tc + 0.2, "transform: scale(1.35); opacity:0")], loop=False))
        css.append(kf(f"sp{i}", [(tc, "transform: scale(.2); opacity:0"), (tc + 0.02, "transform: scale(.6); opacity:1"),
                                 (tc + 0.3, "transform: scale(1.6); opacity:0")], loop=False))
        css.append(kf(f"pp{i}", [(tc, "transform: translate(0,0) scale(.4); opacity:0"), (tc + 0.06, "transform: translate(0,-14px) scale(1.15); opacity:1"),
                                 (tc + 0.6, "transform: translate(0,-40px) scale(1); opacity:0")], loop=False))
        a = f"{T}s infinite"
        css.append(f".o{i}{{animation:o{i} {a} linear}} .ha{i}{{animation:ha{i} {a} ease-in}} .hb{i}{{animation:hb{i} {a} ease-in}}"
                   f" .sl{i}{{animation:sl{i} {a} ease-out}} .sp{i}{{animation:sp{i} {a} ease-out}} .pp{i}{{animation:pp{i} {a} ease-out}}")
        orb = f'<circle r="25" fill="{col}"/><circle r="25" fill="url(#shine)"/>{glyph(kind, fg)}'
        if not o["toss"]:  # charging orbs get angry eyes and a speed trail
            orb = (f'<path d="M{-o["drift"] / 50 * 26},-14 l{-o["drift"] / 50 * 40},-6 M{-o["drift"] / 50 * 26},0 l{-o["drift"] / 50 * 50},0'
                   f' M{-o["drift"] / 50 * 26},14 l{-o["drift"] / 50 * 40},6" stroke="{col}" stroke-width="3" stroke-linecap="round" opacity=".6"/>' + orb)
        juice = "".join(f'<circle cx="{dx}" cy="{dy}" r="{r}" fill="{col}"/>' for dx, dy, r in
                        [(-32, -8, 4.5), (30, -16, 3.5), (-16, 28, 3), (22, 24, 5), (2, -36, 3), (-38, 18, 2.5), (40, 8, 3)])
        sparks = "".join(f'<path d="M0,-30 L0,-46" transform="rotate({k * 45 + 20})" stroke="#fde68a" stroke-width="2.5" stroke-linecap="round"/>'
                         for k in range(8))
        label_fill = col if col == "#F7DF1E" else fg if fg != "#1a1a1a" else col
        body.append(f'''
  <g class="o{i}">
    <g class="sp{i}">{juice}{sparks}</g>
    <g class="ha{i}"><g clip-path="url(#topcut)">{orb}</g></g>
    <g class="hb{i}"><g clip-path="url(#botcut)">{orb}</g></g>
    <g class="sl{i}"><path d="M-58,40 Q-10,-6 58,-40 Q4,6 -58,40 Z" fill="url(#blade)" filter="url(#glow)"/>
      <path d="M-70,50 L70,-50" stroke="#fff" stroke-width="2" stroke-linecap="round"/></g>
  </g>
  <g transform="translate({cx},{cy - 34})"><text class="pp{i}" text-anchor="middle" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-weight="900" font-size="15" fill="{label_fill}" stroke="#0b1020" stroke-width="3" paint-order="stroke">{o["lang"]} +{lang_pts[o["lang"]]:,}</text></g>''')

    for t in cut_times:
        shake += [(t - 0.001, "transform: translate(0,0)"), (t + 0.025, "transform: translate(6px,-4px)"),
                  (t + 0.055, "transform: translate(-5px,3px)"), (t + 0.085, "transform: translate(3px,-1px)"), (t + 0.12, "transform: translate(0,0)")]
        flash += [(t - 0.001, "opacity:0"), (t + 0.02, "opacity:.22"), (t + 0.12, "opacity:0")]
        bump += [(t + 0.02, "transform: scale(1)"), (t + 0.08, "transform: scale(1.18)"), (t + 0.22, "transform: scale(1)")]

    # combo words in the middle
    for k, (t, w) in enumerate(words):
        word = w or ("SLICE!" if k == 0 else f"COMBO x{sum(1 for o in orbs if o['tc'] <= t)}")
        if t in HITS:
            word += f" +{gain[t]:,}"
        css.append(kf(f"cb{k}", [(t, "transform: scale(.3) rotate(-8deg); opacity:0"), (t + 0.07, "transform: scale(1.25) rotate(3deg); opacity:1"),
                                 (t + 0.16, "transform: scale(1) rotate(0); opacity:1"), (t + 0.5, "transform: scale(1.05) rotate(0); opacity:0")], loop=False)
                   + f" .cb{k}{{animation:cb{k} {T}s infinite ease-out}}")
        body.append(f'<g transform="translate({W // 2},62)"><text class="cb{k}" text-anchor="middle" font-family="Impact,Segoe UI Black,Arial Black,sans-serif" '
                    f'font-weight="900" font-size="30" font-style="italic" fill="#fbbf24" stroke="#7c2d12" stroke-width="5" paint-order="stroke">{word}</text></g>')

    for i, sx, ts, cx, cy, tc, ex in stars:
        css.append(kf(f"st{i}", [(ts - 0.001, f"transform: translate({sx}px,{GROUND - 46}px); opacity:0"),
                                 (ts, f"transform: translate({sx}px,{GROUND - 46}px); opacity:1"),
                                 (tc, f"transform: translate({cx}px,{cy}px); opacity:1"),
                                 (tc + 0.25, f"transform: translate({ex:.0f}px,{cy - 60}px); opacity:0")], loop=False)
                   + f" .st{i}{{animation:st{i} {T}s linear infinite}}")
        body.append(f'<g class="st{i}"><g class="spin"><path d="M0,-11 L3,-3 L11,0 L3,3 L0,11 L-3,3 L-11,0 L-3,-3 Z" fill="#cbd5e1" stroke="#64748b" stroke-width=".8"/><circle r="2.2" fill="#1e293b"/></g></g>')

    body.append(boss(css, shake, flash))

    # game clear banner
    tg = cut_times[-1] + 0.45
    css.append(kf("clear", [(tg, "transform: scale(.2); opacity:0"), (tg + 0.12, "transform: scale(1.2); opacity:1"), (tg + 0.25, "transform: scale(1); opacity:1"),
                            (T - 0.15, "transform: scale(1); opacity:1"), (T - 0.02, "transform: scale(1.4); opacity:0")], loop=False)
               + f" .clear{{animation:clear {T}s infinite ease-out}}")
    total_s, year_s = f"{total:,}", f"{year:,}"
    body.append(f'''<g transform="translate({W // 2},150)"><g class="clear" font-family="Impact,Segoe UI Black,Arial Black,sans-serif" text-anchor="middle" font-style="italic">
    <text y="0" font-size="40" fill="#fbbf24" stroke="#7c2d12" stroke-width="6" paint-order="stroke">GAME CLEAR</text>
    <text y="34" font-size="20" fill="#ffffff" stroke="#0b1020" stroke-width="4" paint-order="stroke">{total_s} COMMITS SLICED</text></g></g>''')

    score_css, score = score_strip(values, cut_times, total)
    css += score_css
    css += [kf("pos", pos), kf("flip", flip), kf("face", face), kf("sword", sword), kf("shake", shake), kf("flash", flash), kf("bump", bump)]
    css.append(f""".pos {{ animation: pos {T}s infinite }}
.flip {{ animation: flip {T}s infinite linear }}
.face {{ animation: face {T}s infinite step-end }}
.sword {{ animation: sword {T}s infinite ease-out }}
.shake {{ animation: shake {T}s infinite linear }}
.flash {{ animation: flash {T}s infinite linear }}
.bump {{ animation: bump {T}s infinite ease-out }}
.spin {{ animation: spin .22s infinite linear }}
@keyframes spin {{ to {{ transform: rotate(360deg) }} }}
@keyframes tail {{ 0%,100% {{ d: path("M-6,-46 q-14,-6 -26,4 q-8,6 -18,2") }} 50% {{ d: path("M-6,-46 q-14,4 -26,-4 q-10,-6 -18,4") }} }}
.tail {{ animation: tail .3s ease-in-out infinite }}
@keyframes twinkle {{ 0%,100% {{ opacity:.25 }} 50% {{ opacity:1 }} }}
.star {{ animation: twinkle 3s ease-in-out infinite }}
@media (prefers-reduced-motion: reduce) {{ * {{ animation-duration: 0s !important }} }}""")

    belt_name, belt_col = belt(streak)
    level = total // 250 + 1
    # the belt shows the streak; a black belt gets a gold trim so it reads on the black outfit
    belt_svg = (f'<path d="M-12,-26 h24" stroke="#fbbf24" stroke-width="6"/><path d="M-12,-26 h24" stroke="{belt_col}" stroke-width="3.5"/>'
                f'<path d="M6,-26 l5,9 M6,-26 l-1,10" stroke="{belt_col}" stroke-width="2.5"/>')
    ghosts = "".join(ninja(dl, op, "#38bdf8") for dl, op in [(0.09, .14), (0.06, .22), (0.03, .35)])
    sky = "".join(f'<circle class="star" cx="{(i * 137) % W}" cy="{18 + (i * 53) % 120}" r="{1 + (i % 3) * .5}" fill="#cfe8ff" style="animation-delay:{(i % 7) * .4}s"/>'
                  for i in range(34))
    style = "\n".join(css)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="A ninja fights programming languages; the score climbs to {total_s} contributions ({year_s} this year).">
<title>{total_s} contributions, {year_s} this year</title>
<metadata>Ninja fight animation (c) 2026 Rashmikanth G R, https://github.com/rashmikanth-tech. Licensed CC BY 4.0: credit required. https://github.com/rashmikanth-tech/rashmikanth-tech/blob/main/LICENSE</metadata>
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#070b18"/><stop offset="1" stop-color="#1a2340"/></linearGradient>
  <linearGradient id="blade" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#38bdf8" stop-opacity="0"/><stop offset=".5" stop-color="#e0f2fe"/><stop offset="1" stop-color="#ffffff"/></linearGradient>
  <radialGradient id="shine" cx=".35" cy=".3" r=".75"><stop offset="0" stop-color="#fff" stop-opacity=".35"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".25"/></radialGradient>
  <clipPath id="topcut"><polygon points="-40,-40 40,-40 40,-28 -40,28"/></clipPath>
  <clipPath id="botcut"><polygon points="-40,28 40,-28 40,40 -40,40"/></clipPath>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  <clipPath id="dig"><rect x="-12" y="-28" width="24" height="34"/></clipPath>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>{style}</style>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="url(#sky)"/>
<g class="shake">
{sky}
<circle cx="300" cy="58" r="26" fill="#fef3c7" opacity=".9"/><circle cx="310" cy="52" r="26" fill="#0a0f1f"/>
<path d="M-20,{GROUND - 30} L90,{GROUND - 78} L170,{GROUND - 40} L260,{GROUND - 96} L360,{GROUND - 44} L470,{GROUND - 88} L560,{GROUND - 36} L660,{GROUND - 82} L760,{GROUND - 34} L{W + 20},{GROUND - 70} L{W + 20},{H + 20} L-20,{H + 20} Z" fill="#1b2547"/>
<rect x="-20" y="{GROUND}" width="{W + 40}" height="{H - GROUND + 20}" fill="#0e1428"/>
<path d="M-20,{GROUND} H{W + 20}" stroke="#2c5364" stroke-width="2"/>
{ghosts}
{ninja(0, 1).replace(BELT_PATH, belt_svg)}
{"".join(body)}
</g>
<rect class="flash" width="{W}" height="{H}" fill="#fff" opacity="0"/>
<text x="{W - 16}" y="{H - 12}" text-anchor="end" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="10.5" fill="#9fb3c8" opacity=".55">© Rashmikanth G R · github.com/rashmikanth-tech</text>
<g font-family="Segoe UI,Helvetica,Arial,sans-serif">
  <text x="26" y="34" font-size="12" font-weight="700" fill="#7dd3fc" letter-spacing="2">NINJA RANK</text>
  <text x="26" y="66" font-size="28" font-weight="900" fill="#ffffff">LV {level}</text>
  <rect x="{26 + len(f"LV {level}") * 17 + 10}" y="47" width="58" height="12" rx="3" fill="{belt_col}" stroke="#94a3b8" stroke-width="1"/>
  <text x="26" y="86" font-size="12" fill="#9fb3c8">{belt_name} BELT · {streak}-day streak</text>
</g>
<g font-family="Segoe UI,Helvetica,Arial,sans-serif" text-anchor="end">
  <text x="{W - 26}" y="34" font-size="12" font-weight="700" fill="#7dd3fc" letter-spacing="2">COMMITS SLICED</text>
  <g transform="translate({W - 26},68)"><g class="bump" font-size="32" font-weight="900" fill="#ffffff" style="font-variant-numeric: tabular-nums">{score}</g></g>
  <text x="{W - 26}" y="88" font-size="12" fill="#9fb3c8">{year_s} this year · private repos included</text>
</g>
</g>
</svg>
'''


if __name__ == "__main__":
    total, year, streak, mix = stats()
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    mix = setup(mix, os.environ.get("NINJA_SEED", today))
    with open("assets/ninja.svg", "w", encoding="utf-8") as f:
        f.write(build(total, year, streak, mix))
    print(f"assets/ninja.svg: {total:,} total, {year:,} this year, {streak}-day streak, {len(mix)} languages, seed {today}")
