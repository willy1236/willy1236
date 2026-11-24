"""Generate the profile README artwork into assets/.

Usage: python scripts/gen_svg.py assets
"""
import math, random, sys, os

OUT = sys.argv[1]
SERIF = "'Noto Serif TC','Source Han Serif TC','Songti TC','PMingLiU',serif"
MONO = "'JetBrains Mono','SFMono-Regular',Consolas,'Liberation Mono',monospace"
INK0, INK1 = "#0a0e13", "#121b25"
FG, SUB, DIM = "#e8edf2", "#a9b8c6", "#7a8da1"
GOLD, MIST = "#f0d38a", "#9fb3c8"


def ridge(w, base, amp, seed, step=6, rough=0.35):
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 6.28) for _ in range(4)]
    fr = [rnd.uniform(0.6, 1.4) for _ in range(4)]
    pts, n = [], 0.0
    for x in range(0, w + step, step):
        n = n * 0.85 + rnd.uniform(-1, 1) * rough
        t = x / w
        y = (math.sin(t * 6.28 * 1.1 * fr[0] + ph[0]) * 0.55
             + math.sin(t * 6.28 * 2.7 * fr[1] + ph[1]) * 0.28
             + math.sin(t * 6.28 * 6.3 * fr[2] + ph[2]) * 0.12
             + math.sin(t * 6.28 * 13 * fr[3] + ph[3]) * 0.05 + n * 0.1)
        pts.append((x, base - y * amp))
    return pts


def path(pts, h):
    d = f"M0,{h} L" + " L".join(f"{x:.0f},{y:.1f}" for x, y in pts) + f" L{pts[-1][0]},{h} Z"
    return d


def y_at(pts, x):
    return min(pts, key=lambda p: abs(p[0] - x))[1]


STYLE = f"""<style>
.t{{font-family:{SERIF};fill:{FG}}}
.m{{font-family:{MONO};fill:{SUB};letter-spacing:.32em}}
.d{{font-family:{MONO};fill:{DIM};letter-spacing:.24em}}
.drift{{animation:drift 48s ease-in-out infinite alternate}}
.drift2{{animation:drift 64s ease-in-out infinite alternate-reverse}}
.tw{{animation:tw 3.6s ease-in-out infinite}}
.trail{{stroke-dasharray:2 7;animation:march 6s linear infinite}}
@keyframes drift{{from{{transform:translateX(-60px)}}to{{transform:translateX(60px)}}}}
@keyframes tw{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}
@keyframes march{{to{{stroke-dashoffset:-90}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>"""

DEFS = f"""<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{INK0}"/><stop offset="1" stop-color="{INK1}"/></linearGradient>
<radialGradient id="glow"><stop offset="0" stop-color="{GOLD}" stop-opacity=".55"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></radialGradient>
<filter id="mist" filterUnits="userSpaceOnUse" x="-300" y="-300" width="1800" height="1100">
<feTurbulence type="fractalNoise" baseFrequency="0.006 0.035" numOctaves="3" seed="7"/>
<feDisplacementMap in="SourceGraphic" scale="70"/><feGaussianBlur stdDeviation="14"/></filter>
<linearGradient id="wisp"><stop offset="0" stop-color="{MIST}" stop-opacity="0"/><stop offset=".5" stop-color="{MIST}"/><stop offset="1" stop-color="{MIST}" stop-opacity="0"/></linearGradient>
<linearGradient id="fadeL" gradientUnits="userSpaceOnUse" x1="470" y1="0" x2="780" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff"/></linearGradient>
<mask id="fade" maskUnits="userSpaceOnUse" x="0" y="0" width="1200" height="460"><rect width="1200" height="460" fill="url(#fadeL)"/></mask>
<filter id="soft" filterUnits="userSpaceOnUse" x="-300" y="-300" width="1800" height="1100"><feGaussianBlur stdDeviation="2.2"/></filter>
<clipPath id="card"><rect width="100%" height="100%" rx="14"/></clipPath>
</defs>"""


def star(x, y, s=1.0):
    r = 7 * s
    return (f'<g transform="translate({x},{y})"><circle r="{38*s}" fill="url(#glow)" class="tw"/>'
            f'<path d="M0,-{r*2.4} L{r*0.32},-{r*0.32} L{r*2.4},0 L{r*0.32},{r*0.32} L0,{r*2.4} L-{r*0.32},{r*0.32} L-{r*2.4},0 L-{r*0.32},-{r*0.32} Z" fill="{GOLD}"/></g>')


def stars_field(w, h, seed, n):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        r = rnd.choice([0.6, 0.8, 1.0, 1.3])
        dl = f' class="tw" style="animation-delay:{rnd.uniform(0,3.6):.1f}s"' if i % 4 == 0 else ""
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{SUB}" opacity="{rnd.uniform(.25,.7):.2f}"{dl}/>')
    return "".join(out)


def svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">'
            f'{STYLE}{DEFS}<g clip-path="url(#card)"><rect width="{w}" height="{h}" fill="url(#sky)"/>{body}</g></svg>')


def marker(x, y, name, en, lift, anchor="middle"):
    ty = y - lift
    return (f'<line x1="{x}" y1="{y-6}" x2="{x}" y2="{ty+10}" stroke="{SUB}" stroke-width="1" opacity=".5"/>'
            f'<circle cx="{x}" cy="{y}" r="4.5" fill="{GOLD}"/><circle cx="{x}" cy="{y}" r="10" fill="none" stroke="{GOLD}" stroke-opacity=".45"/>'
            f'<text x="{x}" y="{ty-14}" class="t" font-size="22" text-anchor="{anchor}">{name}</text>'
            f'<text x="{x}" y="{ty+4}" class="d" font-size="10" text-anchor="{anchor}">{en}</text>')


def header():
    W, H = 1200, 460
    far = ridge(W, 300, 70, 11)
    mid = ridge(W, 345, 55, 23)
    near = ridge(W, 400, 30, 37)
    b = [stars_field(W, 230, 3, 70)]
    b.append(f'<path d="{path(far,H)}" fill="#1b2633"/>')
    b.append(f'<g class="drift" filter="url(#mist)" opacity=".28"><ellipse cx="600" cy="310" rx="700" ry="26" fill="{MIST}"/></g>')
    b.append(f'<path d="{path(mid,H)}" fill="#141d28"/>')
    b.append(f'<g class="drift2" filter="url(#mist)" opacity=".22"><ellipse cx="640" cy="368" rx="720" ry="22" fill="{MIST}"/></g>')
    b.append(f'<path d="{path(near,H)}" fill="#0c1218"/>')
    # places on the mid ridge
    px = [520, 790, 1040]
    py = [y_at(mid, x) for x in px]
    # city lights for 析域
    rnd = random.Random(5)
    for i in range(16):
        x = px[0] + rnd.uniform(-34, 34); y = py[0] + rnd.uniform(4, 30)
        b.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="2" height="2" fill="{GOLD}" opacity="{rnd.uniform(.4,.9):.2f}" class="tw" style="animation-delay:{rnd.uniform(0,3):.1f}s"/>')
    # trail
    pts = " ".join(f"{x},{y}" for x, y in zip(px, py))
    b.append(f'<polyline points="{pts}" fill="none" stroke="{GOLD}" stroke-opacity=".55" stroke-width="1.4" class="trail"/>')
    b.append(marker(px[0], py[0], "析域", "DOMALYZE", 92))
    b.append(marker(px[1], py[1], "墨嵐", "INK MIST", 70))
    b.append(marker(px[2], py[2], "群島", "ISLES", 96))
    b.append(star(1110, 70, 1.0))
    # title block
    b.append(f'<text x="72" y="122" class="t" font-size="58" font-weight="600" letter-spacing="6">威立</text>')
    b.append(f'<text x="75" y="156" class="m" font-size="14">WILLY1236</text>')
    b.append(f'<text x="74" y="194" class="t" font-size="17" fill="{SUB}" style="fill:{SUB}">正在努力讓程式變成夢想中的世界。</text>')
    b.append(f'<text x="76" y="436" class="d" font-size="11">SHEET 01  ·  SURVEYED 2020–2026</text>')
    b.append(f'<text x="{W-40}" y="436" class="d" font-size="11" text-anchor="end">0 ─── 1 ─── 2 YEARS</text>')
    return svg(W, H, "".join(b), "威立 willy1236：析域、墨嵐、群島的地圖")


def region(roman, name, en, note, kind, seed):
    W, H = 1200, 150
    b = []
    if kind != "isles":
        r = ridge(W, 128, 14, seed, rough=.2)
        b.append(f'<path d="{path(r,H)}" fill="#0d141b"/>')
    if kind == "city":
        rnd = random.Random(seed)
        for i in range(40):
            x = 820 + rnd.uniform(0, 300); y = 60 + rnd.uniform(0, 50)
            b.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="2.4" height="2.4" fill="{GOLD}" opacity="{rnd.uniform(.25,.9):.2f}" class="tw" style="animation-delay:{rnd.uniform(0,3.6):.1f}s"/>')
        b.append(f'<line x1="820" y1="112" x2="1120" y2="112" stroke="{SUB}" stroke-opacity=".25"/>')
    elif kind == "mist":
        g = ['<g mask="url(#fade)">']
        for base, amp, fill, sd in [(92, 34, "#1f2b39", 71), (112, 26, "#18222e", 72), (130, 16, "#111921", 73)]:
            g.append(f'<path d="{path(ridge(W, base, amp, sd, rough=.25), H)}" fill="{fill}"/>')
            rnd = random.Random(sd)
            for i in range(3):
                x = rnd.uniform(560, 1080); w = rnd.uniform(140, 300); y = base + rnd.uniform(-6, 6)
                op = rnd.uniform(.28, .5); cls = "drift" if i % 2 == 0 else "drift2"
                g.append(f'<rect class="{cls}" x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{rnd.uniform(3,6):.1f}" rx="3" fill="url(#wisp)" opacity="{op:.2f}" filter="url(#soft)"/>')
        g.append('</g>')
        b.append("".join(g))
    else:
        base = 104
        b.append(f'<rect x="0" y="{base}" width="{W}" height="{H-base}" fill="#0d141b"/>')
        b.append(f'<line x1="0" y1="{base}" x2="{W}" y2="{base}" stroke="{SUB}" stroke-opacity=".18"/>')
        rnd = random.Random(seed)
        for i in range(14):
            x = rnd.uniform(560, 1160); y = base + rnd.uniform(8, 38)
            b.append(f'<path d="M{x:.0f},{y:.0f} h{rnd.uniform(10,26):.0f}" stroke="{SUB}" stroke-opacity="{rnd.uniform(.08,.2):.2f}"/>')
        isles = [(800, 46, 12), (880, 90, 26), (1000, 60, 17), (1075, 120, 34), (1170, 40, 10)]
        for x0, w, h in isles:
            a = rnd.uniform(.38, .55)
            d = (f"M{x0},{base} C{x0+w*.2:.0f},{base-h*.25:.1f} {x0+w*(a-.12):.0f},{base-h} {x0+w*a:.0f},{base-h} "
                 f"C{x0+w*(a+.15):.0f},{base-h} {x0+w*.8:.0f},{base-h*.3:.1f} {x0+w},{base} Z")
            b.append(f'<path d="{d}" fill="#1b2633"/>')
            b.append(f'<path d="{d}" fill="#1b2633" opacity=".25" transform="translate(0,{2*base}) scale(1,-1)"/>')
        lx = 1075 + 120*.45
        b.append(f'<circle cx="{lx:.0f}" cy="{base-36}" r="2.6" fill="{GOLD}" class="tw"/>')
        b.append(f'<circle cx="{lx:.0f}" cy="{base-36}" r="16" fill="url(#glow)" class="tw"/>')
    b.append(f'<text x="48" y="58" class="d" font-size="11">{roman}</text>')
    b.append(f'<text x="46" y="104" class="t" font-size="44" font-weight="600" letter-spacing="6">{name}</text>')
    b.append(f'<text x="{46+len(name)*50+14}" y="102" class="m" font-size="13">{en}</text>')
    b.append(f'<text x="48" y="132" class="d" font-size="11">{note}</text>')
    return svg(W, H, "".join(b), f"{name} {en}")


def footer():
    W, H = 1200, 120
    b = [stars_field(W, H, 9, 30), star(600, 60, .6)]
    return svg(W, H, "".join(b), "星")


files = {
    "header.svg": header(),
    "region-domalyze.svg": region("REGION I · CAPITAL", "析域", "DOMALYZE", "EST. 2020 · DISCORD → PLATFORM", "city", 41),
    "region-inkmist.svg": region("REGION II · HIGHLANDS", "墨嵐", "INK MIST", "MEMORY · RULES · TOOLS FOR CODING AGENTS", "mist", 53),
    "region-isles.svg": region("REGION III · OUTLYING", "群島", "ISLES", "PUBLIC GOOD · FRIENDS · GAMES · EVERYDAY", "isles", 67),
    "footer.svg": footer(),
}
for n, s in files.items():
    open(os.path.join(OUT, n), "w", encoding="utf-8").write(s)
    print(n, len(s))
