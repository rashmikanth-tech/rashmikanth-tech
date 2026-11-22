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
SLOT = 0.9            # seconds per move

# Language orbs: (label, colour, glyph colour, glyph). Glyphs are simple marks drawn here, not the official logos.
ORBS = [
    ("Flutter", "#02569B", "#54C5F8", "flutter"),
    ("Java", "#E76F00", "#ffffff", "java"),
    ("Dart", "#0175C2", "#7FD6F7", "dart"),
    ("Go", "#00ADD8", "#ffffff", "Go"),
    ("Python", "#3776AB", "#FFD43B", "py"),
    ("TypeScript", "#3178C6", "#ffffff", "TS"),
    ("PHP", "#777BB4", "#ffffff", "php"),
    ("JavaScript", "#F7DF1E", "#1a1a1a", "JS"),
]
# Where each orb gets cut, and how: a flying "leap" slash or a thrown "star".
CUTS = [(200, 125, "leap"), (340, 160, "leap"), (470, 105, "star"), (575, 140, "leap"),
        (700, 150, "leap"), (610, 120, "star"), (420, 100, "leap"), (250, 145, "leap")]
T = SLOT * len(ORBS) + 0.1  # one full loop


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




def kf(name, frames, loop=True):
    """@keyframes from (time, css) pairs. loop: 0% and 100% take the last frame's value so the cycle joins up."""
    frames = sorted(frames, key=lambda f: f[0])
    out = [("0%", frames[-1][1] if loop else frames[0][1])]
    out += [(pct(t), c) for t, c in frames]
    out.append(("100%", frames[-1][1]))
    return f"@keyframes {name} {{ " + " ".join(f"{p} {{ {c} }}" for p, c in out) + " }"


def plan():
    """The ninja's moves: ground x before each slot, direction, landing x. The start spot is the last landing, so it loops."""
    g0 = 120
    for _ in range(3):
        g, moves = g0, []
        for (cx, cy, kind) in CUTS:
            d = 1 if cx >= g else -1
            land = g if kind == "star" else max(60, min(W - 60, cx + d * 60))
            moves.append((g, d, land))
            g = land
        g0 = g
    return moves


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


def build(total, year):
    css, body, shake, flash = [], [], [], []
    pos, flip, face, sword = [], [], [], []
    for i, ((name, col, fg, kind), (cx, cy, how), (g, d, land)) in enumerate(zip(ORBS, CUTS, plan())):
        t0 = 0.05 + i * SLOT
        tc = t0 + 0.5                       # the hit
        od = -1 if i % 2 else 1             # orbs fly in from alternate sides
        sx = cx - od * 120
        # orb: tossed in on an arc, cut, halves fly apart and drop
        css.append(kf(f"o{i}", [
            (t0 - 0.002, f"transform: translate({sx}px,{H + 40}px); opacity:0"),
            (t0, f"transform: translate({sx}px,{H + 40}px); opacity:1; animation-timing-function: cubic-bezier(.15,.6,.4,1)"),
            (tc, f"transform: translate({cx}px,{cy}px); opacity:1; animation-timing-function: cubic-bezier(.6,0,1,.6)"),
            (tc + 0.4, f"transform: translate({cx + od * 30}px,{H + 30}px); opacity:1"),
            (tc + 0.402, f"transform: translate({cx + od * 30}px,{H + 30}px); opacity:0")], loop=False))
        css.append(kf(f"ha{i}", [(tc, "transform: translate(0,0) rotate(0)"), (tc + 0.4, "transform: translate(-60px,-14px) rotate(-120deg)")], loop=False))
        css.append(kf(f"hb{i}", [(tc, "transform: translate(0,0) rotate(0)"), (tc + 0.4, "transform: translate(60px,12px) rotate(130deg)")], loop=False))
        css.append(kf(f"sl{i}", [(tc - 0.03, "transform: scale(.3); opacity:0"), (tc + 0.03, "transform: scale(1.15); opacity:1"),
                                 (tc + 0.2, "transform: scale(1.35); opacity:0")], loop=False))
        css.append(kf(f"sp{i}", [(tc, "transform: scale(.2); opacity:0"), (tc + 0.02, "transform: scale(.6); opacity:1"),
                                 (tc + 0.3, "transform: scale(1.6); opacity:0")], loop=False))
        css.append(kf(f"pp{i}", [(tc, "transform: translate(0,0) scale(.4); opacity:0"), (tc + 0.06, "transform: translate(0,-14px) scale(1.15); opacity:1"),
                                 (tc + 0.6, "transform: translate(0,-40px) scale(1); opacity:0")], loop=False))
        css.append(kf(f"cb{i}", [(tc, "transform: scale(.3) rotate(-8deg); opacity:0"), (tc + 0.07, "transform: scale(1.25) rotate(3deg); opacity:1"),
                                 (tc + 0.16, "transform: scale(1) rotate(0); opacity:1"), (tc + 0.55, "transform: scale(1.05) rotate(0); opacity:0")], loop=False))
        a = f"{T}s infinite"
        css.append(f".o{i}{{animation:o{i} {a} linear}} .ha{i}{{animation:ha{i} {a} ease-in}} .hb{i}{{animation:hb{i} {a} ease-in}}"
                   f" .sl{i}{{animation:sl{i} {a} ease-out}} .sp{i}{{animation:sp{i} {a} ease-out}} .pp{i}{{animation:pp{i} {a} ease-out}}"
                   f" .cb{i}{{animation:cb{i} {a} ease-out}}")
        shake += [(tc - 0.001, "transform: translate(0,0)"), (tc + 0.025, "transform: translate(6px,-4px)"),
                  (tc + 0.055, "transform: translate(-5px,3px)"), (tc + 0.085, "transform: translate(3px,-1px)"), (tc + 0.12, "transform: translate(0,0)")]
        flash += [(tc - 0.001, "opacity:0"), (tc + 0.02, "opacity:.22"), (tc + 0.12, "opacity:0")]

        orb = f'<circle r="25" fill="{col}"/><circle r="25" fill="url(#shine)"/>{glyph(kind, fg)}'
        juice = "".join(f'<circle cx="{dx}" cy="{dy}" r="{r}" fill="{col}"/>' for dx, dy, r in
                        [(-32, -8, 4.5), (30, -16, 3.5), (-16, 28, 3), (22, 24, 5), (2, -36, 3), (-38, 18, 2.5), (40, 8, 3)])
        sparks = "".join(f'<path d="M0,-30 L0,-46" transform="rotate({k * 45 + 20})" stroke="#fde68a" stroke-width="2.5" stroke-linecap="round"/>'
                         for k in range(8))
        word = "SLICE!" if i == 0 else ("SHURIKEN!" if how == "star" else f"COMBO x{i + 1}")
        label_fill = col if col == "#F7DF1E" else fg
        body.append(f'''
  <g class="o{i}">
    <g class="sp{i}">{juice}{sparks}</g>
    <g class="ha{i}"><g clip-path="url(#topcut)">{orb}</g></g>
    <g class="hb{i}"><g clip-path="url(#botcut)">{orb}</g></g>
    <g class="sl{i}"><path d="M-58,40 Q-10,-6 58,-40 Q4,6 -58,40 Z" fill="url(#blade)" filter="url(#glow)"/>
      <path d="M-70,50 L70,-50" stroke="#fff" stroke-width="2" stroke-linecap="round"/></g>
  </g>
  <g transform="translate({cx},{cy - 34})"><text class="pp{i}" text-anchor="middle" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-weight="900" font-size="15" fill="{label_fill}" stroke="#0b1020" stroke-width="3" paint-order="stroke">{name} +1</text></g>
  <g transform="translate({W // 2},62)"><text class="cb{i}" text-anchor="middle" font-family="Impact,Segoe UI Black,Arial Black,sans-serif" font-weight="900" font-size="30" font-style="italic" fill="#fbbf24" stroke="#7c2d12" stroke-width="5" paint-order="stroke" letter-spacing="1">{word}</text></g>''')

        # ninja moves for this slot
        face.append((t0, f"transform: scaleX({d})"))
        if how == "leap":
            pos += [(t0 + 0.16, f"transform: translate({g}px,{GROUND}px)"),
                    (t0 + 0.24, f"transform: translate({g - d * 4}px,{GROUND + 4}px); animation-timing-function: cubic-bezier(.1,.7,.3,1)"),
                    (tc, f"transform: translate({cx - d * 36}px,{cy + 40}px); animation-timing-function: linear"),
                    (tc + 0.09, f"transform: translate({cx + d * 10}px,{cy + 28}px); animation-timing-function: cubic-bezier(.5,0,1,.5)"),
                    (t0 + 0.8, f"transform: translate({land}px,{GROUND}px)")]
            flip += [(t0 + 0.24, "transform: rotate(0deg)"), (tc - 0.05, f"transform: rotate({d * 360}deg)"),
                     (tc - 0.049, "transform: rotate(0deg)"), (tc + 0.1, f"transform: rotate({d * 25}deg)"), (t0 + 0.8, "transform: rotate(0deg)")]
            sword += [(t0 + 0.22, "transform: rotate(-35deg)"), (t0 + 0.3, "transform: rotate(-150deg)"), (tc - 0.03, "transform: rotate(-170deg)"),
                      (tc + 0.05, "transform: rotate(45deg)"), (t0 + 0.8, "transform: rotate(-35deg)")]
        else:  # hop and throw a shuriken
            pos += [(t0 + 0.12, f"transform: translate({g}px,{GROUND}px)"), (t0 + 0.2, f"transform: translate({g}px,{GROUND - 26}px)"),
                    (t0 + 0.34, f"transform: translate({g}px,{GROUND}px)")]
            sword += [(t0 + 0.12, "transform: rotate(-35deg)"), (t0 + 0.18, "transform: rotate(-120deg)"), (t0 + 0.25, "transform: rotate(30deg)"),
                      (t0 + 0.7, "transform: rotate(-35deg)")]
            css.append(kf(f"st{i}", [(t0 + 0.249, f"transform: translate({g + d * 20}px,{GROUND - 46}px); opacity:0"),
                                     (t0 + 0.25, f"transform: translate({g + d * 20}px,{GROUND - 46}px); opacity:1"),
                                     (tc, f"transform: translate({cx}px,{cy}px); opacity:1"),
                                     (tc + 0.25, f"transform: translate({cx + (cx - g) * .6:.0f}px,{cy - 60}px); opacity:0")], loop=False))
            css.append(f".st{i}{{animation:st{i} {T}s linear infinite}}")
            body.append(f'<g class="st{i}"><g class="spin"><path d="M0,-11 L3,-3 L11,0 L3,3 L0,11 L-3,3 L-11,0 L-3,-3 Z" fill="#cbd5e1" stroke="#64748b" stroke-width=".8"/><circle r="2.2" fill="#1e293b"/></g></g>')

    css += [kf("pos", pos), kf("flip", flip), kf("face", face), kf("sword", sword), kf("shake", shake), kf("flash", flash)]
    css.append(f""".pos {{ animation: pos {T}s infinite }}
.flip {{ animation: flip {T}s infinite linear }}
.face {{ animation: face {T}s infinite step-end }}
.sword {{ animation: sword {T}s infinite ease-out }}
.shake {{ animation: shake {T}s infinite linear }}
.flash {{ animation: flash {T}s infinite linear }}
.spin {{ animation: spin .22s infinite linear }}
@keyframes spin {{ to {{ transform: rotate(360deg) }} }}
@keyframes tail {{ 0%,100% {{ d: path("M-6,-46 q-14,-6 -26,4 q-8,6 -18,2") }} 50% {{ d: path("M-6,-46 q-14,4 -26,-4 q-10,-6 -18,4") }} }}
.tail {{ animation: tail .3s ease-in-out infinite }}
@keyframes twinkle {{ 0%,100% {{ opacity:.25 }} 50% {{ opacity:1 }} }}
.star {{ animation: twinkle 3s ease-in-out infinite }}
@media (prefers-reduced-motion: reduce) {{ * {{ animation-duration: 0s !important }} }}""")

    ghosts = "".join(ninja(dl, op, "#38bdf8") for dl, op in [(0.09, .14), (0.06, .22), (0.03, .35)])
    stars = "".join(f'<circle class="star" cx="{(i * 137) % W}" cy="{18 + (i * 53) % 120}" r="{1 + (i % 3) * .5}" fill="#cfe8ff" style="animation-delay:{(i % 7) * .4}s"/>'
                    for i in range(34))
    total_s, year_s = f"{total:,}", f"{year:,}"
    style = "\n".join(css)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="A ninja fighting and slicing programming languages. {total_s} contributions in total, {year_s} this year.">
<title>{total_s} contributions, {year_s} this year</title>
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#070b18"/><stop offset="1" stop-color="#1a2340"/></linearGradient>
  <linearGradient id="blade" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#38bdf8" stop-opacity="0"/><stop offset=".5" stop-color="#e0f2fe"/><stop offset="1" stop-color="#ffffff"/></linearGradient>
  <radialGradient id="shine" cx=".35" cy=".3" r=".75"><stop offset="0" stop-color="#fff" stop-opacity=".35"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".25"/></radialGradient>
  <clipPath id="topcut"><polygon points="-40,-40 40,-40 40,-28 -40,28"/></clipPath>
  <clipPath id="botcut"><polygon points="-40,28 40,-28 40,40 -40,40"/></clipPath>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>{style}</style>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="url(#sky)"/>
<g class="shake">
{stars}
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
  <text x="{W - 26}" y="68" font-size="32" font-weight="900" fill="#ffffff">{total_s}</text>
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
