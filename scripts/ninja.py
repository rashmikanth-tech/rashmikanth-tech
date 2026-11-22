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
SLOT = 1.6            # seconds per slice
PEAK_Y = 150          # orb height when sliced

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
XS = [110 + i * 93 for i in range(len(ORBS))]
T = SLOT * len(ORBS)  # one full loop


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


def build(total, year):
    css, body = [], []
    # ---- language orbs: rise, get sliced at the peak, two halves fall apart with a splash
    for i, ((name, col, fg, kind), x) in enumerate(zip(ORBS, XS)):
        t0 = i * SLOT          # launch
        tc = t0 + 0.72         # cut
        t1 = t0 + 1.55         # gone
        css.append(f"""
@keyframes rise{i} {{
  0% {{ transform: translate({x}px,{H + 40}px); opacity:0 }}
  {pct(t0 - 0.01)} {{ transform: translate({x}px,{H + 40}px); opacity:0 }}
  {pct(t0)} {{ transform: translate({x}px,{H + 40}px); opacity:1; animation-timing-function: cubic-bezier(.2,.7,.3,1) }}
  {pct(tc)} {{ transform: translate({x}px,{PEAK_Y}px); opacity:1; animation-timing-function: cubic-bezier(.5,0,.9,.6) }}
  {pct(t1)} {{ transform: translate({x}px,{H + 30}px); opacity:1 }}
  {pct(t1 + 0.01)}, 100% {{ transform: translate({x}px,{H + 30}px); opacity:0 }}
}}
@keyframes halfa{i} {{ 0%, {pct(tc)} {{ transform: translate(0,0) rotate(0) }} {pct(t1)}, 100% {{ transform: translate(-52px,-6px) rotate(-75deg) }} }}
@keyframes halfb{i} {{ 0%, {pct(tc)} {{ transform: translate(0,0) rotate(0) }} {pct(t1)}, 100% {{ transform: translate(52px,10px) rotate(85deg) }} }}
@keyframes cut{i} {{ 0%, {pct(tc - 0.06)} {{ opacity:0; stroke-dashoffset:90 }} {pct(tc)} {{ opacity:1; stroke-dashoffset:0 }} {pct(tc + 0.22)}, 100% {{ opacity:0; stroke-dashoffset:-90 }} }}
@keyframes burst{i} {{ 0%, {pct(tc)} {{ transform: scale(.2); opacity:0 }} {pct(tc + 0.02)} {{ opacity:.95 }} {pct(tc + 0.45)}, 100% {{ transform: scale(1.5); opacity:0 }} }}
@keyframes pop{i} {{ 0%, {pct(tc)} {{ transform: translate({x}px,{PEAK_Y - 30}px); opacity:0 }} {pct(tc + 0.05)} {{ opacity:1 }}
  {pct(tc + 0.75)}, 100% {{ transform: translate({x}px,{PEAK_Y - 62}px); opacity:0 }} }}
.r{i} {{ animation: rise{i} {T}s linear infinite }}
.a{i} {{ animation: halfa{i} {T}s ease-in infinite }}
.b{i} {{ animation: halfb{i} {T}s ease-in infinite }}
.c{i} {{ animation: cut{i} {T}s linear infinite }}
.s{i} {{ animation: burst{i} {T}s ease-out infinite }}
.p{i} {{ animation: pop{i} {T}s ease-out infinite }}""")
        orb = (f'<circle r="25" fill="{col}"/><circle r="25" fill="url(#shine)"/>{glyph(kind, fg)}')
        dots = "".join(f'<circle cx="{dx}" cy="{dy}" r="{r}" fill="{col}"/>' for dx, dy, r in
                       [(-30, -8, 4), (28, -14, 3.5), (-14, 26, 3), (20, 22, 4.5), (2, -32, 3), (-34, 18, 2.5), (36, 10, 2.5)])
        body.append(f'''
  <g class="r{i}">
    <g class="s{i}">{dots}</g>
    <g class="a{i}"><g clip-path="url(#topcut)">{orb}</g></g>
    <g class="b{i}"><g clip-path="url(#botcut)">{orb}</g></g>
    <line class="c{i}" x1="-42" y1="30" x2="42" y2="-30" stroke="#ffffff" stroke-width="3.5" stroke-linecap="round" stroke-dasharray="90 90" filter="url(#glow)"/>
  </g>
  <text class="p{i}" text-anchor="middle" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-weight="800" font-size="15" fill="{fg if col != '#F7DF1E' else col}" stroke="#0b1020" stroke-width="3" paint-order="stroke">{name} +1</text>''')

    # ---- the ninja: dash under each orb, leap, slash at the cut, land
    pos, sword = [f"0% {{ transform: translate({XS[0] - 70}px,{GROUND}px) }}"], []
    for i, x in enumerate(XS):
        t0 = i * SLOT
        tc = t0 + 0.72
        pos += [f"{pct(t0 + 0.18)} {{ transform: translate({x - 70}px,{GROUND}px) scaleY(.86); animation-timing-function: cubic-bezier(.2,.8,.4,1) }}",
                f"{pct(tc - 0.02)} {{ transform: translate({x - 44}px,{PEAK_Y + 52}px) rotate(-8deg); animation-timing-function: linear }}",
                f"{pct(tc + 0.14)} {{ transform: translate({x - 22}px,{PEAK_Y + 46}px) rotate(14deg); animation-timing-function: cubic-bezier(.5,0,.9,.5) }}",
                f"{pct(t0 + 1.25)} {{ transform: translate({x + 4}px,{GROUND}px) scaleY(.88) }}"]
        nxt = XS[i + 1] - 70 if i + 1 < len(XS) else XS[0] - 70
        if i + 1 == len(XS):  # back to the start, out of sight behind a smoke puff
            pos += [f"{pct(t0 + 1.4)} {{ transform: translate({x + 30}px,{GROUND}px); opacity:1 }}",
                    f"{pct(t0 + 1.5)} {{ transform: translate({x + 30}px,{GROUND}px); opacity:0 }}",
                    f"{pct(t0 + 1.51)} {{ transform: translate({nxt}px,{GROUND}px); opacity:0 }}",
                    f"100% {{ transform: translate({nxt}px,{GROUND}px); opacity:1 }}"]
        else:
            pos.append(f"{pct(t0 + SLOT)} {{ transform: translate({nxt}px,{GROUND}px) }}")
        sword += [f"{pct(tc - 0.16)} {{ transform: rotate(-150deg) }}", f"{pct(tc - 0.03)} {{ transform: rotate(-160deg) }}",
                  f"{pct(tc + 0.07)} {{ transform: rotate(35deg) }}", f"{pct(t0 + 1.3)} {{ transform: rotate(-35deg) }}"]
    css.append("@keyframes ninja {\n  " + "\n  ".join(pos) + "\n}")
    css.append("@keyframes sword {\n  0% { transform: rotate(-35deg) }\n  " + "\n  ".join(sword) + "\n  100% { transform: rotate(-35deg) }\n}")
    css.append(f""".ninja {{ animation: ninja {T}s infinite }}
.sword {{ animation: sword {T}s ease-in-out infinite; transform-origin: 0 0 }}
@keyframes tail {{ 0%,100% {{ d: path("M-6,-46 q-14,-6 -26,4 q-8,6 -18,2") }} 50% {{ d: path("M-6,-46 q-14,4 -26,-4 q-10,-6 -18,4") }} }}
.tail {{ animation: tail .45s ease-in-out infinite }}
@keyframes twinkle {{ 0%,100% {{ opacity:.25 }} 50% {{ opacity:1 }} }}
.star {{ animation: twinkle 3s ease-in-out infinite }}
@media (prefers-reduced-motion: reduce) {{ * {{ animation-duration: 0s !important }} }}""")

    stars = "".join(f'<circle class="star" cx="{(i * 137) % W}" cy="{18 + (i * 53) % 120}" r="{1 + (i % 3) * .5}" fill="#cfe8ff" style="animation-delay:{(i % 7) * .4}s"/>'
                    for i in range(34))
    ninja = '''
  <g class="ninja">
    <ellipse cx="0" cy="2" rx="18" ry="4" fill="#000" opacity=".35"/>
    <path d="M-7,-18 L-11,0 M6,-18 L11,0" stroke="#111827" stroke-width="7" stroke-linecap="round"/>
    <path d="M-12,-40 q12,-8 24,0 l-2,24 q-10,4 -20,0 Z" fill="#111827"/>
    <path d="M-12,-26 h24" stroke="#EA580C" stroke-width="4"/>
    <circle cx="0" cy="-52" r="13" fill="#111827"/>
    <rect x="-11" y="-56" width="22" height="7" rx="3.5" fill="#f2d2b6"/>
    <circle cx="-4" cy="-52.5" r="1.7" fill="#111"/><circle cx="5" cy="-52.5" r="1.7" fill="#111"/>
    <path d="M-13,-60 h26" stroke="#E11D48" stroke-width="4"/>
    <path class="tail" d="M-6,-46 q-14,-6 -26,4 q-8,6 -18,2" stroke="#E11D48" stroke-width="3.5" fill="none" stroke-linecap="round" transform="translate(-6,-14)"/>
    <g transform="translate(9,-34)"><g class="sword">
      <path d="M0,0 L10,0" stroke="#111827" stroke-width="7" stroke-linecap="round"/>
      <rect x="8" y="-4" width="3" height="8" fill="#FBBF24"/>
      <path d="M11,-1.6 L58,-1.6 L63,0 L58,1.6 L11,1.6 Z" fill="#e5edf7" stroke="#9fb3c8" stroke-width=".6"/>
    </g></g>
  </g>'''
    total_s, year_s = f"{total:,}", f"{year:,}"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="A ninja slicing programming languages. {total_s} contributions in total, {year_s} this year.">
<title>{total_s} contributions, {year_s} this year</title>
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b1020"/><stop offset="1" stop-color="#1a2340"/></linearGradient>
  <radialGradient id="shine" cx=".35" cy=".3" r=".75"><stop offset="0" stop-color="#fff" stop-opacity=".35"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".25"/></radialGradient>
  <clipPath id="topcut"><polygon points="-40,-40 40,-40 40,-28 -40,28"/></clipPath>
  <clipPath id="botcut"><polygon points="-40,28 40,-28 40,40 -40,40"/></clipPath>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>{"".join(css)}</style>
<rect width="{W}" height="{H}" rx="18" fill="url(#sky)"/>
{stars}
<circle cx="{W // 2}" cy="64" r="30" fill="#fef3c7" opacity=".9"/><circle cx="{W // 2 + 11}" cy="57" r="30" fill="#0f1527"/>
<path d="M0,{GROUND - 30} L90,{GROUND - 78} L170,{GROUND - 40} L260,{GROUND - 96} L360,{GROUND - 44} L470,{GROUND - 88} L560,{GROUND - 36} L660,{GROUND - 82} L760,{GROUND - 34} L{W},{GROUND - 70} L{W},{H} L0,{H} Z" fill="#1b2547"/>
<rect x="0" y="{GROUND}" width="{W}" height="{H - GROUND}" fill="#0e1428"/>
<path d="M0,{GROUND} H{W}" stroke="#2c5364" stroke-width="2"/>
{"".join(body)}
{ninja}
<g font-family="Segoe UI,Helvetica,Arial,sans-serif" text-anchor="end">
  <text x="{W - 26}" y="34" font-size="12" font-weight="700" fill="#7dd3fc" letter-spacing="2">COMMITS SLICED</text>
  <text x="{W - 26}" y="68" font-size="32" font-weight="900" fill="#ffffff">{total_s}</text>
  <text x="{W - 26}" y="88" font-size="12" fill="#9fb3c8">{year_s} this year · private repos included</text>
</g>
</svg>
'''


if __name__ == "__main__":
    total, year = counts()
    os.makedirs("assets", exist_ok=True)
    with open("assets/ninja.svg", "w", encoding="utf-8") as f:
        f.write(build(total, year))
    print(f"assets/ninja.svg: {total:,} total, {year:,} this year")
