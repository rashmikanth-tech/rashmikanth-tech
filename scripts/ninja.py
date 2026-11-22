"""Draws assets/ninja.svg: a ninja jumps and slices programming-language orbs, with the real contribution count as the score.

Usage:  python scripts/ninja.py              # counts read from GitHub (needs GH_TOKEN; the Action's GITHUB_TOKEN works)
        python scripts/ninja.py 6528 6221    # or pass total and this-year counts by hand

Counts come from GitHub's contribution calendar, which includes private-repo contributions because the profile shows them.
"""
import datetime as dt
import json
import os
import sys
import urllib.request

USER = "rashmikanth-tech"
W, H = 880, 320
GROUND = 262          # y of the ground line

def counts():
    if len(sys.argv) == 3:
        return int(sys.argv[1]), int(sys.argv[2])
    token = os.environ["GH_TOKEN"]

    def q(query):
        req = urllib.request.Request("https://api.github.com/graphql", json.dumps({"query": query}).encode(),
                                     {"Authorization": f"bearer {token}", "Content-Type": "application/json"})
        return json.load(urllib.request.urlopen(req))["data"]["user"]

    first = int(q(f'{{user(login:"{USER}"){{createdAt}}}}')["createdAt"][:4])
    now = dt.datetime.now(dt.timezone.utc).year
    per_year = {}
    for y in range(first, now + 1):  # the API allows at most one year per query
        c = q(f'{{user(login:"{USER}"){{contributionsCollection(from:"{y}-01-01T00:00:00Z",to:"{y}-12-31T23:59:59Z")'
              f'{{contributionCalendar{{totalContributions}}}}}}}}')
        per_year[y] = c["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    return sum(per_year.values()), per_year[now]


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





# Language orbs: label -> (colour, glyph colour, glyph). Glyphs are simple marks drawn here, not the official logos.
LANG = {
    "Flutter": ("#02569B", "#54C5F8", "flutter"), "Java": ("#E76F00", "#ffffff", "java"),
    "Dart": ("#0175C2", "#7FD6F7", "dart"), "Kotlin": ("#7F52FF", "#ffffff", "K"),
    "Go": ("#00ADD8", "#ffffff", "Go"), "Python": ("#3776AB", "#FFD43B", "py"),
    "TypeScript": ("#3178C6", "#ffffff", "TS"), "JavaScript": ("#F7DF1E", "#1a1a1a", "JS"),
    "PHP": ("#777BB4", "#ffffff", "php"), "Node.js": ("#339933", "#ffffff", "node"),
    "SQL": ("#336791", "#ffffff", "SQL"), "Swift": ("#F05138", "#ffffff", "Sw"),
    "C++": ("#00599C", "#ffffff", "C++"), "Rust": ("#CE422B", "#ffffff", "Rs"),
}
# The round, move by move:
#   leap   (lang, cx, cy)       an orb is tossed up; the ninja flips up to it and slashes
#   star   (lang, cx, cy)       he throws a shuriken at a tossed orb
#   attack (lang, side)         an orb charges at him along the ground from side -1 (left) or 1 (right); he counter-slashes
#   double (left, right)        two orbs charge from both sides at once; he spins and cuts both
EVENTS = [
    ("leap", "Flutter", 200, 125), ("attack", "Java", 1), ("leap", "Dart", 420, 110), ("double", "Kotlin", "Go"),
    ("star", "Python", 610, 115), ("leap", "TypeScript", 700, 150), ("attack", "JavaScript", -1), ("leap", "PHP", 470, 100),
    ("double", "Node.js", "SQL"), ("star", "Swift", 240, 120), ("leap", "C++", 330, 150), ("attack", "Rust", 1),
]
SLOT = 0.8          # seconds per move
END = 1.6           # the "game clear" hold after the last hit
T = 0.05 + SLOT * len(EVENTS) + END
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
    # victory hop while the final score shows
    tv = 0.05 + SLOT * len(EVENTS) + 0.3
    pos += [(tv, f"transform: translate({g}px,{GROUND}px)"), (tv + 0.18, f"transform: translate({g}px,{GROUND - 40}px)"),
            (tv + 0.36, f"transform: translate({g}px,{GROUND}px)")]
    flip += [(tv, "transform: rotate(0deg)"), (tv + 0.36, "transform: rotate(-360deg)"), (tv + 0.361, "transform: rotate(0deg)")]
    sword += [(tv, "transform: rotate(-35deg)"), (tv + 0.2, "transform: rotate(-95deg)"), (tv + 0.9, "transform: rotate(-95deg)"),
              (tv + 1.1, "transform: rotate(-35deg)")]
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


def build(total, year):
    orbs, words, stars, (pos, flip, face, sword), _ = choreograph()
    n = len(orbs)
    cut_times = sorted({o["tc"] for o in orbs})
    # the score climbs with each orb cut and lands exactly on the real total at the last hit
    values, done = [], 0
    for t in cut_times:
        done += sum(1 for o in orbs if o["tc"] == t)
        values.append(round(total * done / n))
    gain = {}
    prev = 0
    for t, v in zip(cut_times, values):
        gain[t] = v - prev
        prev = v

    css, body, shake, flash, bump = [], [], [], [], []
    for i, o in enumerate(orbs):
        col, fg, kind = LANG[o["lang"]]
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
  <g transform="translate({cx},{cy - 34})"><text class="pp{i}" text-anchor="middle" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-weight="900" font-size="15" fill="{label_fill}" stroke="#0b1020" stroke-width="3" paint-order="stroke">{o["lang"]} +{gain[tc]:,}</text></g>''')

    for t in cut_times:
        shake += [(t - 0.001, "transform: translate(0,0)"), (t + 0.025, "transform: translate(6px,-4px)"),
                  (t + 0.055, "transform: translate(-5px,3px)"), (t + 0.085, "transform: translate(3px,-1px)"), (t + 0.12, "transform: translate(0,0)")]
        flash += [(t - 0.001, "opacity:0"), (t + 0.02, "opacity:.22"), (t + 0.12, "opacity:0")]
        bump += [(t + 0.02, "transform: scale(1)"), (t + 0.08, "transform: scale(1.18)"), (t + 0.22, "transform: scale(1)")]

    # combo words in the middle
    for k, (t, w) in enumerate(words):
        word = w or ("SLICE!" if k == 0 else f"COMBO x{sum(1 for o in orbs if o['tc'] <= t)}")
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

    ghosts = "".join(ninja(dl, op, "#38bdf8") for dl, op in [(0.09, .14), (0.06, .22), (0.03, .35)])
    sky = "".join(f'<circle class="star" cx="{(i * 137) % W}" cy="{18 + (i * 53) % 120}" r="{1 + (i % 3) * .5}" fill="#cfe8ff" style="animation-delay:{(i % 7) * .4}s"/>'
                  for i in range(34))
    style = "\n".join(css)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="A ninja fights programming languages; the score climbs to {total_s} contributions ({year_s} this year).">
<title>{total_s} contributions, {year_s} this year</title>
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
<circle cx="80" cy="66" r="30" fill="#fef3c7" opacity=".9"/><circle cx="91" cy="59" r="30" fill="#0a0f1f"/>
<path d="M-20,{GROUND - 30} L90,{GROUND - 78} L170,{GROUND - 40} L260,{GROUND - 96} L360,{GROUND - 44} L470,{GROUND - 88} L560,{GROUND - 36} L660,{GROUND - 82} L760,{GROUND - 34} L{W + 20},{GROUND - 70} L{W + 20},{H + 20} L-20,{H + 20} Z" fill="#1b2547"/>
<rect x="-20" y="{GROUND}" width="{W + 40}" height="{H - GROUND + 20}" fill="#0e1428"/>
<path d="M-20,{GROUND} H{W + 20}" stroke="#2c5364" stroke-width="2"/>
{ghosts}
{ninja(0, 1)}
{"".join(body)}
</g>
<rect class="flash" width="{W}" height="{H}" fill="#fff" opacity="0"/>
<g font-family="Segoe UI,Helvetica,Arial,sans-serif" text-anchor="end">
  <text x="{W - 26}" y="34" font-size="12" font-weight="700" fill="#7dd3fc" letter-spacing="2">COMMITS SLICED</text>
  <g transform="translate({W - 26},68)"><g class="bump" font-size="32" font-weight="900" fill="#ffffff" style="font-variant-numeric: tabular-nums">{score}</g></g>
  <text x="{W - 26}" y="88" font-size="12" fill="#9fb3c8">{year_s} this year · private repos included</text>
</g>
</g>
</svg>
'''


if __name__ == "__main__":
    total, year = counts()
    os.makedirs("assets", exist_ok=True)
    with open("assets/ninja.svg", "w", encoding="utf-8") as f:
        f.write(build(total, year))
    print(f"assets/ninja.svg: {total:,} total, {year:,} this year")
