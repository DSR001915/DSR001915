"""Generate animated HUD/circuit SVGs for the GitHub profile README.

Theme taken from the reference video: pure black, cyan circuit traces with
travelling light pulses, a CPU chip inside rotating rings, hexagon badges and
small orange "loading" accents. Everything is self-contained SVG + CSS so it
animates inside GitHub's <img> rendering (no JS, no external requests).
"""
import base64
import math
import os
import random

OUT = r"E:/DSR001915_Profile/assets"
os.makedirs(OUT, exist_ok=True)

BG = "#02070a"
GRID = "#0a1c22"
DIM = "#0f3a44"
MID = "#1d6f7d"
CYAN = "#2ee6ff"
SOFT = "#4ea4af"
BRIGHT = "#c9fcff"
ORANGE = "#ff8a1c"
GREEN = "#3dff9a"
MONO = "Consolas, 'Cascadia Code', 'Courier New', monospace"
SANS = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"

BASE_STYLE = f"""
  .mono {{ font-family: {MONO}; }}
  .sans {{ font-family: {SANS}; }}
  .pulse {{ fill: none; stroke: {CYAN}; stroke-width: 2; stroke-linecap: round;
           stroke-dasharray: 26 900; animation: run 3.2s linear infinite; filter: url(#glow); }}
  .trace {{ fill: none; stroke: {DIM}; stroke-width: 1.4; }}
  .node {{ fill: {BG}; stroke: {SOFT}; stroke-width: 1.4; }}
  .spin {{ transform-box: fill-box; transform-origin: center; animation: spin 14s linear infinite; }}
  .spin-r {{ transform-box: fill-box; transform-origin: center; animation: spin 9s linear infinite reverse; }}
  .spin-s {{ transform-box: fill-box; transform-origin: center; animation: spin 30s linear infinite; }}
  .blink {{ animation: blink 1.1s steps(1) infinite; }}
  .breathe {{ animation: breathe 2.6s ease-in-out infinite; }}
  .boot {{ opacity: 0; animation: boot .7s ease-out forwards; }}
  @keyframes run {{ from {{ stroke-dashoffset: 926; }} to {{ stroke-dashoffset: 0; }} }}
  @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  @keyframes breathe {{ 50% {{ opacity: .35; }} }}
  @keyframes boot {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: none; }} }}
"""

DEFS = f"""
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="2.4" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="glow-sm" x="-20%" y="-50%" width="140%" height="200%">
    <feGaussianBlur stdDeviation="1.1" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="glow-lg" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="6" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <pattern id="grid" width="22" height="22" patternUnits="userSpaceOnUse">
    <path d="M22 0H0V22" fill="none" stroke="{GRID}" stroke-width="1"/>
  </pattern>
  <pattern id="hazard" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <rect width="5" height="10" fill="{ORANGE}"/>
  </pattern>
  <linearGradient id="name-grad" x1="0" x2="1">
    <stop offset="0" stop-color="{BRIGHT}"/>
    <stop offset=".5" stop-color="{CYAN}"/>
    <stop offset="1" stop-color="{SOFT}"/>
  </linearGradient>
  <linearGradient id="scan" x1="0" x2="0" y1="0" y2="1">
    <stop offset="0" stop-color="{CYAN}" stop-opacity="0"/>
    <stop offset=".85" stop-color="{CYAN}" stop-opacity=".18"/>
    <stop offset="1" stop-color="{CYAN}" stop-opacity=".55"/>
  </linearGradient>
"""


def svg(w, h, body, extra_style="", title=""):
    title = title.replace("&", "&amp;")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{title}">\n'
        f"<title>{title}</title>\n<defs>{DEFS}</defs>\n"
        f"<style>{BASE_STYLE}{extra_style}</style>\n{body}\n</svg>\n"
    )


def trace(points, delay=0.0, dur=3.2, pulse=True):
    d = "M" + " L".join(f"{x},{y}" for x, y in points)
    out = f'<path class="trace" d="{d}"/>'
    if pulse:
        out += f'<path class="pulse" d="{d}" style="animation-delay:{delay:.2f}s;animation-duration:{dur:.2f}s"/>'
    x, y = points[-1]
    out += f'<circle class="node" cx="{x}" cy="{y}" r="3.2"/>'
    return out


def chip(cx, cy, s=56, rings=True, scale=1.0):
    """CPU chip with pins inside rotating HUD rings."""
    s = s * scale
    h = s / 2
    parts = []
    if rings:
        r1, r2, r3, r4 = 62 * scale, 84 * scale, 104 * scale, 116 * scale
        circ2 = 2 * math.pi * r2
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r4}" fill="none" stroke="{DIM}" stroke-width="1"/>')
        # tick ring
        ticks = "".join(
            f'<line x1="{cx + r3 * math.cos(a)}" y1="{cy + r3 * math.sin(a)}" '
            f'x2="{cx + (r3 - (8 if i % 5 == 0 else 4) * scale) * math.cos(a)}" '
            f'y2="{cy + (r3 - (8 if i % 5 == 0 else 4) * scale) * math.sin(a)}" stroke="{SOFT}" stroke-width="1"/>'
            for i, a in enumerate(math.radians(d) for d in range(0, 360, 6))
        )
        parts.append(f'<g class="spin-s">{ticks}</g>')
        parts.append(
            f'<circle class="spin-r" cx="{cx}" cy="{cy}" r="{r2}" fill="none" stroke="{CYAN}" stroke-width="{3 * scale:.1f}" '
            f'stroke-dasharray="{circ2 * .18:.1f} {circ2 * .07:.1f} {circ2 * .3:.1f} {circ2 * .45:.1f}" filter="url(#glow)" opacity=".9"/>'
        )
        parts.append(
            f'<circle class="spin" cx="{cx}" cy="{cy}" r="{r1}" fill="none" stroke="{SOFT}" stroke-width="1.5" '
            f'stroke-dasharray="4 7"/>'
        )
        parts.append(f'<circle class="breathe" cx="{cx}" cy="{cy}" r="{r1 - 10 * scale}" fill="{CYAN}" opacity=".08"/>')
    # pins
    pins = []
    n = 5
    for i in range(n):
        o = -h + (i + 1) * s / (n + 1)
        pl = 9 * scale
        pins += [
            f'<line x1="{cx + o}" y1="{cy - h}" x2="{cx + o}" y2="{cy - h - pl}"/>',
            f'<line x1="{cx + o}" y1="{cy + h}" x2="{cx + o}" y2="{cy + h + pl}"/>',
            f'<line x1="{cx - h}" y1="{cy + o}" x2="{cx - h - pl}" y2="{cy + o}"/>',
            f'<line x1="{cx + h}" y1="{cy + o}" x2="{cx + h + pl}" y2="{cy + o}"/>',
        ]
    parts.append(f'<g stroke="{CYAN}" stroke-width="{1.6 * scale:.1f}" filter="url(#glow)">{"".join(pins)}</g>')
    parts.append(
        f'<rect x="{cx - h}" y="{cy - h}" width="{s}" height="{s}" rx="{4 * scale}" fill="#041318" stroke="{CYAN}" stroke-width="2" filter="url(#glow)"/>'
    )
    parts.append(
        f'<rect x="{cx - h * .55}" y="{cy - h * .55}" width="{s * .55}" height="{s * .55}" rx="2" fill="none" stroke="{SOFT}" stroke-width="1.2"/>'
    )
    parts.append(f'<circle class="blink" cx="{cx}" cy="{cy}" r="{3 * scale}" fill="{BRIGHT}" filter="url(#glow)"/>')
    return "".join(parts)


def hexagon(cx, cy, r, label, sub="", color=CYAN, cls=""):
    pts = " ".join(
        f"{cx + r * math.cos(math.radians(60 * i - 30)):.1f},{cy + r * math.sin(math.radians(60 * i - 30)):.1f}"
        for i in range(6)
    )
    out = f'<g class="{cls}"><polygon points="{pts}" fill="#041318" stroke="{color}" stroke-width="1.6" filter="url(#glow)"/>'
    out += f'<text x="{cx}" y="{cy + (2 if not sub else -2)}" text-anchor="middle" class="mono" font-size="{r * .42:.0f}" font-weight="700" fill="{BRIGHT}">{label}</text>'
    if sub:
        out += f'<text x="{cx}" y="{cy + r * .45:.0f}" text-anchor="middle" class="mono" font-size="{r * .24:.0f}" fill="{SOFT}">{sub}</text>'
    return out + "</g>"


def corners(x, y, w, h, l=18, color=CYAN):
    return (
        f'<g stroke="{color}" stroke-width="2" fill="none" filter="url(#glow)">'
        f'<path d="M{x},{y + l} V{y} H{x + l}"/><path d="M{x + w - l},{y} H{x + w} V{y + l}"/>'
        f'<path d="M{x},{y + h - l} V{y + h} H{x + l}"/><path d="M{x + w - l},{y + h} H{x + w} V{y + h - l}"/></g>'
    )


def keypad(x, y, cols=4, rows=3, c=12, gap=4, lit=(1, 6)):
    out = []
    for r in range(rows):
        for k in range(cols):
            i = r * cols + k
            fill = CYAN if i in lit else "#062028"
            cls = ' class="breathe"' if i in lit else ""
            out.append(
                f'<rect{cls} x="{x + k * (c + gap)}" y="{y + r * (c + gap)}" width="{c}" height="{c}" rx="1.5" '
                f'fill="{fill}" stroke="{MID}" stroke-width=".8" style="animation-delay:{i * .17:.2f}s"/>'
            )
    return "".join(out)


def bars(x, y, n=7, w=6, gap=4, hmax=34):
    random.seed(x + y)
    out = []
    for i in range(n):
        hh = random.randint(8, hmax)
        out.append(
            f'<rect x="{x + i * (w + gap)}" y="{y - hh}" width="{w}" height="{hh}" fill="{SOFT}" opacity=".75">'
            f'<animate attributeName="height" values="{hh};{max(4, hh // 3)};{hh}" dur="{1.4 + i * .23:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="y" values="{y - hh};{y - max(4, hh // 3)};{y - hh}" dur="{1.4 + i * .23:.2f}s" repeatCount="indefinite"/></rect>'
        )
    return "".join(out)


def scanline(w, h, dur=5):
    return (
        f'<rect x="0" y="-60" width="{w}" height="60" fill="url(#scan)" opacity=".7">'
        f'<animate attributeName="y" values="-60;{h};{h}" keyTimes="0;.85;1" dur="{dur}s" repeatCount="indefinite"/></rect>'
    )


# ------------------------------------------------------------------ banner
def banner():
    W, H = 1280, 420
    cx, cy = 1000, 210
    b = [f'<rect width="{W}" height="{H}" fill="{BG}"/>', f'<rect width="{W}" height="{H}" fill="url(#grid)" opacity=".8"/>']
    b.append(f'<circle cx="{cx}" cy="{cy}" r="230" fill="{CYAN}" opacity=".05" filter="url(#glow-lg)"/>')

    # circuit traces radiating from the chip
    tr = [
        [(cx - 40, cy - 10), (cx - 150, cy - 10), (cx - 180, cy - 40), (cx - 330, cy - 40), (cx - 360, cy - 70)],
        [(cx - 40, cy + 10), (cx - 170, cy + 10), (cx - 200, cy + 40), (cx - 300, cy + 40)],
        [(cx - 40, cy + 22), (cx - 120, cy + 22), (cx - 140, cy + 90), (cx - 260, cy + 90), (cx - 280, cy + 120)],
        [(cx + 40, cy - 10), (cx + 140, cy - 10), (cx + 170, cy - 60), (cx + 260, cy - 60)],
        [(cx + 40, cy + 10), (cx + 160, cy + 10), (cx + 190, cy + 50), (cx + 262, cy + 50)],
        [(cx + 40, cy + 22), (cx + 120, cy + 22), (cx + 140, cy + 120), (cx + 220, cy + 120)],
        [(cx - 10, cy - 40), (cx - 10, cy - 130), (cx - 60, cy - 170), (cx - 160, cy - 170)],
        [(cx + 10, cy - 40), (cx + 10, cy - 140), (cx + 60, cy - 180), (cx + 200, cy - 180)],
        [(cx - 10, cy + 40), (cx - 10, cy + 140), (cx - 70, cy + 180), (cx - 180, cy + 180)],
        [(cx + 10, cy + 40), (cx + 10, cy + 150), (cx + 70, cy + 185), (cx + 230, cy + 185)],
        [(cx - 22, cy - 40), (cx - 22, cy - 100), (cx - 90, cy - 100), (cx - 110, cy - 140)],
        [(cx + 22, cy + 40), (cx + 22, cy + 95), (cx + 100, cy + 95)],
    ]
    for i, p in enumerate(tr):
        b.append(trace(p, delay=i * .37, dur=2.6 + (i % 4) * .5))
    b.append(chip(cx, cy))

    # side HUD widgets
    b.append(f'<g class="boot" style="animation-delay:.9s">{keypad(1170, 60)}</g>')
    b.append(f'<g class="boot" style="animation-delay:1.1s">{keypad(1160, 300, cols=5, rows=2, lit=(3, 7))}</g>')
    b.append(f'<g class="boot" style="animation-delay:1.3s">{bars(705, 380)}</g>')
    b.append(hexagon(780, 92, 30, "AI", "ML", cls="boot breathe"))
    b.append(hexagon(1220, 210, 26, "OPS", "", cls="boot"))
    b.append(
        f'<g class="boot" style="animation-delay:1.5s"><circle cx="1190" cy="390" r="0"/>'
        f'<circle class="spin" cx="760" cy="300" r="20" fill="none" stroke="{SOFT}" stroke-dasharray="20 12"/>'
        f'<circle cx="760" cy="300" r="10" fill="none" stroke="{CYAN}" filter="url(#glow)"/></g>'
    )
    # orange "loading" accent from the video
    b.append(
        f'<g class="boot" style="animation-delay:1.7s">'
        f'<rect x="1112" y="30" width="6" height="64" fill="url(#hazard)"/>'
        f'<text x="1128" y="40" class="mono blink" font-size="11" fill="{ORANGE}" letter-spacing="2">BUFFERING...</text></g>'
    )

    # left text panel
    t = []
    t.append(f'<text x="64" y="86" class="mono boot" font-size="14" fill="{SOFT}" letter-spacing="3">[ SYS://PROFILE.INIT ]  USER: DSR001915</text>')
    t.append(
        f'<text x="60" y="160" class="sans boot" style="animation-delay:.3s" font-size="58" font-weight="800" '
        f'fill="url(#name-grad)" letter-spacing="2" filter="url(#glow-sm)">DEVANSH SINGH</text>'
    )
    t.append(
        f'<text x="60" y="226" class="sans boot" style="animation-delay:.5s" font-size="58" font-weight="800" '
        f'fill="url(#name-grad)" letter-spacing="2" filter="url(#glow-sm)">RAGHUVANSHI</text>'
    )
    t.append(f'<rect class="boot" style="animation-delay:.7s" x="62" y="248" width="430" height="2" fill="{CYAN}" filter="url(#glow)"/>')
    t.append(
        f'<text x="62" y="284" class="sans boot" style="animation-delay:.8s" font-size="22" font-weight="600" fill="#e6f3f7">'
        f'AI/ML &amp; DevOps Engineer  ·  Python Developer</text>'
    )
    t.append(
        f'<text x="62" y="318" class="mono boot" style="animation-delay:1s" font-size="15" fill="{CYAN}" letter-spacing="1.5">'
        f'PYTHON ▸ FASTAPI ▸ RAG ▸ ML ▸ DOCKER ▸ LINUX</text>'
    )
    # loader bar
    t.append(
        f'<g class="boot" style="animation-delay:1.2s">'
        f'<text x="62" y="360" class="mono" font-size="12" fill="{SOFT}" letter-spacing="2">LOADING MODULES</text>'
        f'<rect x="200" y="350" width="240" height="10" fill="none" stroke="{MID}"/>'
        f'<rect x="202" y="352" width="0" height="6" fill="{CYAN}" filter="url(#glow)">'
        f'<animate attributeName="width" values="0;236;236" keyTimes="0;.8;1" dur="3.5s" repeatCount="indefinite"/></rect>'
        f'<circle class="blink" cx="470" cy="355" r="5" fill="{GREEN}" filter="url(#glow)"/>'
        f'<text x="484" y="360" class="mono" font-size="12" fill="{GREEN}" letter-spacing="2">ONLINE</text></g>'
    )
    b += t
    b.append(scanline(W, H, 6))
    b.append(corners(14, 14, W - 28, H - 28, 26))
    b.append(f'<text x="{W - 30}" y="{H - 26}" text-anchor="end" class="mono" font-size="11" fill="{MID}" letter-spacing="2">NEW DELHI · IN  //  v2026.11</text>')
    return svg(W, H, "\n".join(b), title="Devansh Singh Raghuvanshi — AI/ML & DevOps Engineer")


# ------------------------------------------------------------------ section header
def header(num, label, note):
    W, H = 1280, 74
    b = [f'<rect width="{W}" height="{H}" fill="{BG}"/>']
    b.append(hexagon(40, 37, 26, f"{num:02d}"))
    b.append(f'<text x="80" y="47" class="mono" font-size="26" font-weight="700" fill="{CYAN}" letter-spacing="3" filter="url(#glow-sm)">{label.replace("&", "&amp;")}</text>')
    tw = 80 + len(label) * 17.5 + 24
    b.append(trace([(tw, 37), (tw + 60, 37), (tw + 80, 22), (W - 260, 22), (W - 240, 37), (W - 40, 37)], dur=3.6))
    b.append(f'<text x="{W - 40}" y="62" text-anchor="end" class="mono" font-size="12" fill="{MID}" letter-spacing="2">{note}</text>')
    b.append(f'<rect class="blink" x="{tw + 8}" y="44" width="10" height="3" fill="{ORANGE}"/>')
    return svg(W, H, "\n".join(b), title=label.replace("_", " ").title())


# ------------------------------------------------------------------ divider
def divider():
    W, H = 1280, 34
    b = [f'<rect width="{W}" height="{H}" fill="{BG}"/>']
    b.append(trace([(20, 17), (560, 17), (580, 6), (700, 6), (720, 17), (1260, 17)], dur=4))
    b.append(trace([(1260, 17), (720, 17), (700, 28), (580, 28), (560, 17), (20, 17)], delay=2, dur=4))
    b.append(f'<rect x="628" y="11" width="24" height="12" rx="2" fill="#041318" stroke="{CYAN}" filter="url(#glow)"/>')
    return svg(W, H, "\n".join(b), title="divider")


# ------------------------------------------------------------------ ID card with photo
def id_card(photo_path):
    W, H = 440, 520
    with open(photo_path, "rb") as f:
        img = base64.b64encode(f.read()).decode()
    cx, cy, r = 220, 205, 128
    b = [f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="{BG}" stroke="{DIM}" stroke-width="1.5"/>']
    b.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="url(#grid)" opacity=".7"/>')
    b.append(f'<text x="28" y="40" class="mono" font-size="12" fill="{SOFT}" letter-spacing="3">IDENTITY_SCAN</text>')
    b.append(f'<circle class="blink" cx="398" cy="35" r="5" fill="{GREEN}" filter="url(#glow)"/>')
    b.append(f'<text x="386" y="40" text-anchor="end" class="mono" font-size="12" fill="{GREEN}" letter-spacing="2">LIVE</text>')
    b.append(f'<clipPath id="pc"><circle cx="{cx}" cy="{cy}" r="{r - 22}"/></clipPath>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{r - 22}" fill="#06232b"/>')
    b.append(
        f'<image clip-path="url(#pc)" x="{cx - 125}" y="{cy - 112}" width="250" height="250" '
        f'href="data:image/webp;base64,{img}" xlink:href="data:image/webp;base64,{img}" preserveAspectRatio="xMidYMin slice"/>'
    )
    # scan line inside the photo
    b.append(
        f'<g clip-path="url(#pc)"><rect x="{cx - r}" y="{cy - r}" width="{2 * r}" height="34" fill="url(#scan)">'
        f'<animate attributeName="y" values="{cy - r - 34};{cy + r};{cy + r}" keyTimes="0;.8;1" dur="3.6s" repeatCount="indefinite"/></rect></g>'
    )
    circ = 2 * math.pi * (r - 8)
    b.append(
        f'<circle class="spin-r" cx="{cx}" cy="{cy}" r="{r - 8}" fill="none" stroke="{CYAN}" stroke-width="3" '
        f'stroke-dasharray="{circ * .22:.1f} {circ * .06:.1f} {circ * .4:.1f} {circ * .32:.1f}" filter="url(#glow)"/>'
    )
    b.append(f'<circle class="spin" cx="{cx}" cy="{cy}" r="{r + 4}" fill="none" stroke="{SOFT}" stroke-width="1.2" stroke-dasharray="3 6"/>')
    ticks = "".join(
        f'<line x1="{cx + (r + 14) * math.cos(math.radians(a))}" y1="{cy + (r + 14) * math.sin(math.radians(a))}" '
        f'x2="{cx + (r + 22) * math.cos(math.radians(a))}" y2="{cy + (r + 22) * math.sin(math.radians(a))}" stroke="{CYAN}" stroke-width="2"/>'
        for a in range(0, 360, 45)
    )
    b.append(f'<g class="spin-s" filter="url(#glow)">{ticks}</g>')
    rows = [
        ("NAME", "Devansh Singh Raghuvanshi"),
        ("ROLE", "AI/ML & DevOps Intern"),
        ("ORG", "NeGD, MeitY · myScheme"),
        ("BASE", "New Delhi, India"),
    ]
    y = 384
    for k, v in rows:
        b.append(f'<text x="34" y="{y}" class="mono" font-size="12" fill="{MID}" letter-spacing="2">{k}</text>')
        b.append(f'<text x="104" y="{y}" class="mono" font-size="14" fill="#e6f3f7">{v.replace("&", "&amp;")}</text>')
        y += 28
    b.append(f'<rect x="34" y="{y - 6}" width="372" height="8" fill="none" stroke="{MID}"/>')
    b.append(
        f'<rect x="36" y="{y - 4}" width="0" height="4" fill="{CYAN}" filter="url(#glow)">'
        f'<animate attributeName="width" values="0;368;368" keyTimes="0;.75;1" dur="4s" repeatCount="indefinite"/></rect>'
    )
    b.append(corners(10, 10, W - 20, H - 20, 20))
    return svg(W, H, "\n".join(b), title="Devansh Singh Raghuvanshi — identity card")


# ------------------------------------------------------------------ project card
def wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    return lines


def project_card(idx, title, tag, desc, stack, status="ONLINE"):
    W, H = 620, 280
    cut = 22
    frame = f"M{cut},2 H{W - 2} V{H - cut} L{W - cut},{H - 2} H2 V{cut} Z"
    b = [f'<path d="{frame}" fill="{BG}" stroke="{DIM}" stroke-width="1.6"/>']
    b.append(f'<path d="{frame}" fill="url(#grid)" opacity=".6"/>')
    b.append(f'<path d="M{cut},2 H{cut + 140}" stroke="{CYAN}" stroke-width="3" filter="url(#glow)"/>')
    b.append(f'<path d="M{W - cut - 140},{H - 2} H{W - cut} L{W - 2},{H - cut}" fill="none" stroke="{CYAN}" stroke-width="3" filter="url(#glow)"/>')
    b.append(f'<text x="34" y="38" class="mono" font-size="12" fill="{SOFT}" letter-spacing="3">PROJECT_{idx:02d} // {tag}</text>')
    color = GREEN if status == "LIVE" else CYAN
    b.append(f'<circle class="blink" cx="{W - 34 - len(status) * 8.4 - 16:.0f}" cy="34" r="4.5" fill="{color}" filter="url(#glow)"/>')
    b.append(f'<text x="{W - 34}" y="38" text-anchor="end" class="mono" font-size="12" fill="{color}" letter-spacing="2">{status}</text>')
    b.append(f'<text x="32" y="82" class="sans" font-size="28" font-weight="800" fill="{CYAN}" filter="url(#glow-sm)">{title}</text>')
    y = 116
    for line in wrap(desc, 58):
        b.append(f'<text x="34" y="{y}" class="sans" font-size="15" fill="#c3d6dc">{line.replace("&", "&amp;")}</text>')
        y += 22
    # chips
    x = 34
    for s in stack:
        w = 16 + len(s) * 8
        b.append(f'<rect x="{x}" y="212" width="{w}" height="26" rx="13" fill="#061d24" stroke="{MID}"/>')
        b.append(f'<text x="{x + w / 2}" y="229" text-anchor="middle" class="mono" font-size="12" fill="{BRIGHT}">{s}</text>')
        x += w + 8
    b.append(f'<text x="34" y="264" class="mono" font-size="12" fill="{SOFT}" letter-spacing="2">▸ OPEN REPOSITORY</text>')
    b.append(f'<g transform="translate({W - 64},{H - 92})">{chip(0, 0, rings=True, scale=.34)}</g>')
    return svg(W, H, "\n".join(b), title=title)


def write(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"{name:28s} {len(content.encode()) / 1024:6.1f} KB")


if __name__ == "__main__":
    write("banner.svg", banner())
    write("divider.svg", divider())
    write("id-card.svg", id_card(r"E:/portfolio-main/img/dev-cutout.webp"))
    sections = [
        (1, "ABOUT_ME", "SECTOR 01 // WHO AM I"),
        (2, "CONNECT_WITH_ME", "SECTOR 02 // UPLINK"),
        (3, "TECH_STACK", "SECTOR 03 // MODULES"),
        (4, "FEATURED_PROJECTS", "SECTOR 04 // DEPLOYMENTS"),
        (5, "EXPERIENCE_&_CERTS", "SECTOR 05 // LOG"),
        (6, "GITHUB_ANALYTICS", "SECTOR 06 // TELEMETRY"),
        (7, "TROPHIES", "SECTOR 07 // ACHIEVEMENTS"),
        (8, "CONTRIBUTION_SNAKE", "SECTOR 08 // ACTIVITY"),
    ]
    for n, label, note in sections:
        slug = label.lower().replace("_&_", "-").replace("_", "-")
        write(f"h-{slug}.svg", header(n, label, note))
    projects = [
        (1, "DocuTrust", "AI/ML · RAG",
         "Self-correcting RAG built as a LangGraph state machine: reranker-graded retrieval, inline citations, query rewrites and a disclosed web fallback, streamed live over WebSockets.",
         ["FastAPI", "LangGraph", "ChromaDB", "MongoDB", "Docker"], "OPEN SOURCE"),
        (2, "Zenith Planner", "WEB APP",
         "Offline-first study planner with calendar views, Gantt timelines, a Pomodoro focus mode and gamified streaks and badges, persisted in IndexedDB.",
         ["React", "TypeScript", "Zustand", "Tailwind"], "LIVE"),
        (3, "Churn Prediction", "MACHINE LEARNING",
         "Benchmarked a dozen classifiers, then tuned voting, bagging and stacking ensembles: 98.1% test accuracy and ROC-AUC 0.98 on 5,630 customers.",
         ["scikit-learn", "XGBoost", "LightGBM", "Pandas"], "OPEN SOURCE"),
        (4, "Pneumonia Detect", "DEEP LEARNING",
         "ResNet50 chest X-ray classifier for normal, bacterial and viral pneumonia, with class-imbalance handling, Grad-CAM heatmaps and a Gradio app.",
         ["PyTorch", "fastai", "Grad-CAM", "Gradio"], "OPEN SOURCE"),
        (5, "FaceAttend", "COMPUTER VISION",
         "Register with a webcam capture, then mark attendance by real-time face matching, entirely in the browser with an in-browser SQL database.",
         ["React", "TypeScript", "face-api.js", "AlaSQL"], "OPEN SOURCE"),
        (6, "Glass Portfolio", "WEB · CI/CD",
         "Futuristic glassmorphism portfolio with a particle network, 3D tilt cards and scroll animations, auto-deployed to Netlify and GitHub Pages.",
         ["HTML", "CSS", "JavaScript", "Actions"], "LIVE"),
    ]
    for p in projects:
        write(f"project-{p[0]}.svg", project_card(*p))
