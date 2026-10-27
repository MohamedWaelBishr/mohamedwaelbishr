#!/usr/bin/env python3
"""Generate the animated SVGs used by the profile README.

No dependencies. Run from the repo root:  python3 scripts/build_assets.py

Constraints these files are written against (GitHub serves them through <img>):
  - no web fonts, scripts, foreignObject or links inside the SVG
  - CSS @keyframes and SMIL both animate; prefers-reduced-motion is honoured
  - text widths vary by OS, so reveals are whole-line or over-sized clips
"""
import math
import re
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

# ── tokens ────────────────────────────────────────────────────────────────
BG = "#0B0F17"
SURFACE = "#101725"
BORDER = "#1E293B"
TEXT = "#E6EDF3"
MUTED = "#8B97A8"
DIM = "#4B5565"
CYAN = "#22D3EE"
VIOLET = "#A78BFA"
GREEN = "#34D399"
AMBER = "#FBBF24"
PINK = "#F472B6"

MONO = "ui-monospace,'SF Mono',SFMono-Regular,Menlo,'JetBrains Mono',Consolas,'Liberation Mono',monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Helvetica,Arial,sans-serif"

BASE_CSS = f"""
.mono{{font-family:{MONO}}}
.sans{{font-family:{SANS}}}
.up{{animation:up .6s cubic-bezier(.2,.7,.2,1) both}}
.fade{{animation:fade .6s ease both}}
.blink{{animation:blink 1.1s steps(1) infinite}}
.pulse{{animation:pulse 1.8s ease-out infinite;transform-box:fill-box;transform-origin:center}}
.flow{{stroke-dasharray:4 10;animation:flow 1.2s linear infinite}}
@keyframes up{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
@keyframes fade{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes blink{{50%{{opacity:0}}}}
@keyframes pulse{{0%{{opacity:.8;transform:scale(1)}}100%{{opacity:0;transform:scale(2.6)}}}}
@keyframes flow{{to{{stroke-dashoffset:-28}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
"""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(w, h, label, body, css="", x0=0):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{x0} 0 {w} {h}" '
        f'role="img" aria-label="{esc(label)}" fill="none">\n'
        f"<title>{esc(label)}</title>\n<style>{BASE_CSS}{css}</style>\n{body}\n</svg>\n"
    )


def write(name, content):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"  {path.relative_to(OUT.parent)}  ({len(content):,} bytes)")


def type_clip(cid, x, y, h, width, begin, dur):
    """Clip that grows left→right in discrete steps: a typing reveal that never
    depends on the exact glyph width (width is deliberately over-sized)."""
    steps = 24
    vals = ";".join(f"{width * i / steps:.1f}" for i in range(steps + 1))
    return (
        f'<clipPath id="{cid}"><rect x="{x}" y="{y}" height="{h}" width="0">'
        f'<animate attributeName="width" values="{vals}" calcMode="discrete" '
        f'begin="{begin}s" dur="{dur}s" fill="freeze"/></rect></clipPath>'
    )


def chrome(w, title, y=0, r=16):
    """Window title bar with traffic lights."""
    return f"""
<path d="M{r} {y}H{w - r}a{r} {r} 0 0 1 {r} {r}V{y + 40}H0V{y + r}a{r} {r} 0 0 1 {r}-{r}z" fill="{SURFACE}"/>
<circle cx="24" cy="{y + 20}" r="6" fill="#FF5F57"/><circle cx="44" cy="{y + 20}" r="6" fill="#FEBC2E"/><circle cx="64" cy="{y + 20}" r="6" fill="#28C840"/>
<text x="{w / 2}" y="{y + 24.5}" text-anchor="middle" class="mono" font-size="12" fill="{MUTED}">{esc(title)}</text>
<line x1="0" y1="{y + 40.5}" x2="{w}" y2="{y + 40.5}" stroke="{BORDER}"/>"""


GRAD_DEFS = f"""
<linearGradient id="brand" x1="0" y1="0" x2="1" y2="0" gradientUnits="objectBoundingBox">
  <stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{CYAN}"/>
  <animateTransform attributeName="gradientTransform" type="translate" values="-1 0;0 0" dur="6s" repeatCount="indefinite"/>
</linearGradient>
<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset=".5" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>
</linearGradient>"""


# ── hero ──────────────────────────────────────────────────────────────────
def hero():
    W, H = 880, 400
    cx, cy = 706, 200
    sats = [
        ("React", 0), ("TS", 60), ("Next", 120), ("Node", 180), ("LLM", 240), ("Figma", 300),
    ]
    ring = 86
    graph = []
    for i, (label, deg) in enumerate(sats):
        a = math.radians(deg - 90)
        sx, sy = cx + ring * math.cos(a), cy + ring * math.sin(a)
        d = f"M{cx:.1f} {cy:.1f}L{sx:.1f} {sy:.1f}"
        graph.append(f'<path d="{d}" stroke="{BORDER}" stroke-width="1.5"/>')
        graph.append(f'<path d="{d}" stroke="{CYAN if i % 2 else VIOLET}" stroke-opacity=".7" stroke-width="1.5" class="flow" style="animation-delay:{-i * .2:.1f}s"/>')
        graph.append(
            f'<circle r="3" fill="{CYAN if i % 2 else VIOLET}"><animateMotion path="{d}" dur="2.4s" '
            f'begin="{i * .4:.1f}s" repeatCount="indefinite"/></circle>'
        )
        graph.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="22" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>')
        graph.append(f'<text x="{sx:.1f}" y="{sy + 4:.1f}" text-anchor="middle" class="mono" font-size="11" fill="{TEXT}">{label}</text>')

    bars = []
    for i in range(28):
        x = 600 + i * 8
        dur = 0.9 + (i * 37 % 11) / 10
        lo, hi = 4 + (i * 7 % 5), 10 + (i * 13 % 14)
        bars.append(
            f'<rect x="{x}" width="5" rx="1.5" fill="{CYAN if i % 9 else AMBER}" fill-opacity=".75">'
            f'<animate attributeName="height" values="{lo};{hi};{lo}" dur="{dur:.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="y" values="{362 - lo};{362 - hi};{362 - lo}" dur="{dur:.1f}s" repeatCount="indefinite"/></rect>'
        )

    lines = [
        ("ship real-time fintech dashboards @ Octane", 2.0, CYAN),
        ("design systems · render performance · motion", 2.7, VIOLET),
        ("build my own AI dev tooling — MCP, Claude, Raycast", 3.4, GREEN),
    ]
    clips, typed = [], []
    for i, (txt, t, col) in enumerate(lines):
        y = 238 + i * 28
        clips.append(type_clip(f"t{i}", 40, y - 16, 22, 520, t, 0.7))
        typed.append(
            f'<g clip-path="url(#t{i})"><text x="40" y="{y}" class="mono" font-size="14" fill="{TEXT}">'
            f'<tspan fill="{col}">›</tspan> {esc(txt)}</text></g>'
        )

    css = f"""
.glow{{animation:drift 14s ease-in-out infinite alternate;transform-box:view-box}}
.glow2{{animation:drift 18s ease-in-out infinite alternate-reverse;transform-box:view-box}}
@keyframes drift{{from{{transform:translate(-40px,-10px)}}to{{transform:translate(60px,30px)}}}}
"""
    body = f"""
<defs>
{GRAD_DEFS}
<clipPath id="card"><rect width="{W}" height="{H}" rx="16"/></clipPath>
<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" stroke="{BORDER}" stroke-width="1"/></pattern>
<radialGradient id="fadeR" cx=".5" cy=".4" r=".7"><stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<mask id="gridMask"><rect width="{W}" height="{H}" fill="url(#fadeR)"/></mask>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="60"/></filter>
<linearGradient id="ringG" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
{''.join(clips)}
{type_clip("t-who", 40, 70, 24, 360, 0.3, 0.6)}
</defs>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <circle class="glow" cx="220" cy="150" r="150" fill="{CYAN}" fill-opacity=".14" filter="url(#blur)"/>
  <circle class="glow2" cx="700" cy="250" r="170" fill="{VIOLET}" fill-opacity=".16" filter="url(#blur)"/>
  <rect width="{W}" height="{H}" fill="url(#grid)" mask="url(#gridMask)" opacity=".55"/>
  {chrome(W, "bishr@mansoura-eg: ~/profile — zsh")}

  <g clip-path="url(#t-who)"><text x="40" y="88" class="mono" font-size="14" fill="{TEXT}"><tspan fill="{GREEN}">➜</tspan> <tspan fill="{CYAN}">~/profile</tspan> <tspan fill="{MUTED}">git:(</tspan><tspan fill="{PINK}">main</tspan><tspan fill="{MUTED}">)</tspan> whoami</text></g>

  <text x="38" y="150" class="sans up" style="animation-delay:1s" font-size="46" font-weight="800" textLength="440" lengthAdjust="spacingAndGlyphs" fill="url(#brand)">Mohamed Wael Bishr</text>
  <text x="40" y="184" class="sans up" style="animation-delay:1.3s" font-size="18" fill="{TEXT}" fill-opacity=".88" textLength="410" lengthAdjust="spacingAndGlyphs">Senior Software Engineer <tspan fill="{DIM}">·</tspan> Frontend Architecture</text>
  <line x1="40" y1="206" x2="500" y2="206" stroke="url(#sweep)" class="fade" style="animation-delay:1.6s"/>
  {''.join(typed)}

  <text x="40" y="336" class="mono fade" style="animation-delay:4.2s" font-size="14" fill="{TEXT}"><tspan fill="{GREEN}">➜</tspan> <tspan fill="{CYAN}">~/profile</tspan> <tspan fill="{CYAN}" class="blink">▍</tspan></text>

  <g class="fade" style="animation-delay:4.4s">
    <rect x="40.5" y="352.5" width="330" height="28" rx="14" fill="{SURFACE}" stroke="{BORDER}"/>
    <circle cx="58" cy="366.5" r="4" fill="{GREEN}"/>
    <circle cx="58" cy="366.5" r="4" fill="{GREEN}" class="pulse"/>
    <text x="70" y="371" class="mono" font-size="12" fill="{TEXT}">open to interesting frontend problems</text>
  </g>

  <g class="fade" style="animation-delay:.6s">
    <rect x="572.5" y="64.5" width="268" height="314" rx="14" fill="{BG}" fill-opacity=".7" stroke="{BORDER}"/>
    <circle cx="592" cy="86" r="3.5" fill="{GREEN}"/><circle cx="592" cy="86" r="3.5" fill="{GREEN}" class="pulse"/>
    <text x="602" y="90" class="mono" font-size="11" fill="{MUTED}">runtime · live</text>
    <text x="826" y="90" text-anchor="end" class="mono" font-size="11" fill="{DIM}">v2026.10</text>
    <circle cx="{cx}" cy="{cy}" r="{ring + 30}" stroke="{BORDER}" stroke-dasharray="2 6">
      <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="40s" repeatCount="indefinite"/>
    </circle>
    {''.join(graph)}
    <circle cx="{cx}" cy="{cy}" r="30" fill="{SURFACE}" stroke="url(#ringG)" stroke-width="2"/>
    <circle cx="{cx}" cy="{cy}" r="30" stroke="{CYAN}" class="pulse" style="animation-duration:2.6s"/>
    <text x="{cx}" y="{cy + 5}" text-anchor="middle" class="mono" font-size="14" font-weight="700" fill="{TEXT}">&lt;MB/&gt;</text>
    {''.join(bars)}
    <text x="600" y="330" class="mono" font-size="10.5" fill="{DIM}">frame budget · 16.6ms</text>
  </g>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="15.5" stroke="{BORDER}"/>"""
    write("hero.svg", svg(W, H, "Mohamed Wael Bishr — Senior Software Engineer, Frontend Architecture, Mansoura, Egypt", body, css))


# ── now.ts editor ─────────────────────────────────────────────────────────
def now_editor():
    W = 880
    K, S, C, P, N = VIOLET, GREEN, DIM, TEXT, CYAN  # keyword, string, comment, plain, key

    def arr(*items):
        out = [(P, "[")]
        for i, it in enumerate(items):
            out.append((S, f'"{it}"'))
            if i < len(items) - 1:
                out.append((P, ", "))
        out.append((P, "],"))
        return out

    code = [
        [(C, "// now.ts — last updated Oct 2026")],
        [(K, "export const "), (N, "mohamed"), (P, " = {")],
        [(N, "  role:      "), (S, '"Senior Software Engineer"'), (P, ",")],
        [(N, "  shipping:  "), (S, '"real-time fintech dashboards @ Octane"'), (P, ",")],
        [(N, "  focus:     ")] + arr("Frontend Architecture", "Design Systems", "Data UI"),
        [(N, "  daily:     ")] + arr("TypeScript", "React", "Next.js", "Tailwind"),
        [(N, "  exploring: ")] + arr("LLM tooling", "MCP servers", "Render perf"),
        [(N, "  motto:     "), (S, '"Ship it, measure it, then make it beautiful."'), (P, ",")],
        [(P, "} "), (K, "as const"), (P, ";")],
        [],
        [(K, "export default "), (N, "mohamed"), (P, ".motto"), (P, ";"), (N, " ▍")],
    ]
    BLINK = ' class="blink"'
    top, lh = 74, 24
    H = top + len(code) * lh + 52
    rows = []
    for i, toks in enumerate(code):
        y = top + i * lh
        spans = "".join(
            f'<tspan fill="{col}"{BLINK if t == " ▍" else ""}>{esc(t)}</tspan>' for col, t in toks
        )
        rows.append(
            f'<g class="up" style="animation-delay:{.3 + i * .12:.2f}s">'
            f'<text x="44" y="{y}" text-anchor="end" class="mono" font-size="13" fill="{DIM}">{i + 1}</text>'
            f'<text x="64" y="{y}" class="mono" font-size="13.5" xml:space="preserve">{spans}</text></g>'
        )
    css = ""
    hl_vals = ";".join(f"{top + i * lh - 17}" for i in range(len(code)))
    body = f"""
<defs>{GRAD_DEFS}</defs>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="15.5" fill="{BG}" stroke="{BORDER}"/>
{chrome(W, "~/profile/now.ts — VS Code")}
<rect x="96" y="8" width="96" height="32" rx="6" fill="{BG}" stroke="{BORDER}"/>
<text x="112" y="29" class="mono" font-size="12" fill="{TEXT}"><tspan fill="{CYAN}">TS</tspan> now.ts</text>
<rect x="1" y="{top - 17}" width="{W - 2}" height="{lh}" fill="{CYAN}" fill-opacity=".06">
  <animate attributeName="y" values="{hl_vals}" dur="{len(code) * .12:.2f}s" begin=".3s" calcMode="discrete" fill="freeze"/>
</rect>
<line x1="56.5" y1="48" x2="56.5" y2="{H - 34}" stroke="{BORDER}"/>
{''.join(rows)}
<line x1="0" y1="{H - 28.5}" x2="{W}" y2="{H - 28.5}" stroke="{BORDER}"/>
<text x="20" y="{H - 10}" class="mono" font-size="11" fill="{MUTED}"><tspan fill="{GREEN}">✓</tspan> 0 problems   <tspan fill="{DIM}">·</tspan>   ⎇ main</text>
<text x="{W - 20}" y="{H - 10}" text-anchor="end" class="mono" font-size="11" fill="{MUTED}">Ln {len(code)}, Col 34   UTF-8   LF   TypeScript React</text>"""
    write("now.svg", svg(W, H, "now.ts — role: Senior Software Engineer; shipping real-time fintech dashboards at Octane; focus: frontend architecture, design systems, data UI", body, css))


# ── how I ship pipeline ───────────────────────────────────────────────────
def pipeline():
    W, H = 880, 250
    stages = [
        ("clipboard-check", "spec", "read the real problem"),
        ("pen-tool", "design", "figma → tokens"),
        ("terminal-prompt", "build", "typed end to end"),
        ("bug-shield", "test", "unit · e2e · a11y"),
        ("rocket", "ship", "ci/cd → prod"),
        ("analytics-dashboard", "measure", "telemetry → iterate"),
    ]
    bw, gap, x0, by = 124, 20, 20, 54
    period = 7.2
    boxes = []
    for i, (glyph, name, cap) in enumerate(stages):
        x = x0 + i * (bw + gap)
        delay = period * (i + .5) / len(stages) - period * .08
        boxes.append(f"""
<g>
  <rect x="{x + .5}" y="{by + .5}" width="{bw}" height="72" rx="12" fill="{SURFACE}" stroke="{BORDER}"/>
  <rect x="{x + .5}" y="{by + .5}" width="{bw}" height="72" rx="12" stroke="{CYAN}" stroke-width="1.5" class="lit" style="animation-delay:{delay:.2f}s"/>
  {koboyo(glyph, x + 14, by + 11, 26, 24, CYAN)}
  <text x="{x + 16}" y="{by + 56}" class="sans" font-size="16" font-weight="700" fill="{TEXT}">{name}</text>
  <text x="{x + bw - 12}" y="{by + 30}" text-anchor="end" class="mono" font-size="10.5" fill="{DIM}">0{i + 1}</text>
  <text x="{x + bw / 2 + .5}" y="{by + 98}" text-anchor="middle" class="mono" font-size="11" fill="{MUTED}">{esc(cap)}</text>
</g>""")
    y_mid = by
    x_end = x0 + 5 * (bw + gap) + bw
    rail = f"M{x0 + 10} {y_mid}H{x_end - 10}"
    loop = f"M{x_end - 40} {by + 112}C{x_end - 40} {H - 44} {x0 + 40} {H - 44} {x0 + 40} {by + 112}"
    css = f"""
.lit{{opacity:0;animation:lit {period}s ease-out infinite}}
@keyframes lit{{0%{{opacity:0}}6%{{opacity:1}}22%{{opacity:0}}100%{{opacity:0}}}}
"""
    body = f"""
<defs>{GRAD_DEFS}</defs>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="15.5" fill="{BG}" stroke="{BORDER}"/>
<text x="20" y="32" class="mono" font-size="12" fill="{MUTED}"><tspan fill="{GREEN}">$</tspan> make ship <tspan fill="{DIM}"># how a feature moves through my hands</tspan></text>
<path d="{rail}" stroke="{BORDER}" stroke-width="2"/>
<path d="{rail}" stroke="{CYAN}" stroke-opacity=".5" stroke-width="2" class="flow"/>
{''.join(boxes)}
<path d="{loop}" stroke="{VIOLET}" stroke-opacity=".55" stroke-width="1.5" class="flow" style="animation-direction:reverse"/>
<text x="{W / 2}" y="{H - 14}" text-anchor="middle" class="mono" font-size="11" fill="{VIOLET}">↺ feedback loop — measure, then make it beautiful</text>
<circle r="5" fill="{CYAN}"><animateMotion path="{rail}" dur="{period}s" repeatCount="indefinite"/></circle>
<circle r="11" fill="{CYAN}" fill-opacity=".2"><animateMotion path="{rail}" dur="{period}s" repeatCount="indefinite"/></circle>"""
    write("pipeline.svg", svg(W, H, "How I ship: spec, design, build, test, ship, measure — then loop back", body, css))


# ── project cards ─────────────────────────────────────────────────────────
CW, CH = 440, 260
GUTTER = 8  # transparent space on a card's inner edge; README pairs them at 50% + 50% with no gap
# column each paired card sits in, so its outer edge lines up with the full-width sections
SIDE = {"chronoflow": "left", "teacher-toolbox": "left", "raycast-prompt-enhancer": "left"}
PX, PY, PW, PH = 20, 78, 400, 124  # preview area


def card(slug, title, tagline, icon, accent, status, chips, preview, label, css=""):
    status_col = {"live": GREEN, "private": MUTED, "oss": VIOLET}[status[0]]
    chip_svg, x = [], 20
    for c in chips:
        w = len(c) * 7.4 + 18
        chip_svg.append(
            f'<rect x="{x + .5}" y="218.5" width="{w:.0f}" height="22" rx="11" fill="{SURFACE}" stroke="{BORDER}"/>'
            f'<text x="{x + w / 2 + .5:.1f}" y="233.5" text-anchor="middle" class="mono" font-size="11" fill="{MUTED}">{esc(c)}</text>'
        )
        x += w + 6
    body = f"""
<defs>{GRAD_DEFS}
<clipPath id="pv"><rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="10"/></clipPath>
<linearGradient id="topline" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{accent}" stop-opacity="0"/><stop offset=".5" stop-color="{accent}"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/>
<animateTransform attributeName="gradientTransform" type="translate" values="-1 0;1 0" dur="4s" repeatCount="indefinite"/></linearGradient>
</defs>
<rect x=".5" y=".5" width="{CW - 1}" height="{CH - 1}" rx="15.5" fill="{BG}" stroke="{BORDER}"/>
<rect x="16" y=".5" width="{CW - 32}" height="1.5" fill="url(#topline)"/>
<rect x="20" y="20" width="40" height="40" rx="10" fill="{accent}" fill-opacity=".14" stroke="{accent}" stroke-opacity=".35"/>
{koboyo(icon, 26, 26, 28, 28, accent)}
<text x="72" y="38" class="sans" font-size="19" font-weight="700" fill="{TEXT}">{esc(title)}</text>
<text x="72" y="57" class="sans" font-size="12.5" fill="{MUTED}">{esc(tagline)}</text>
<circle cx="{CW - 20 - len(status[1]) * 7.2 - 10:.1f}" cy="34" r="3.5" fill="{status_col}"/>
<text x="{CW - 20}" y="38" text-anchor="end" class="mono" font-size="11" fill="{status_col}">{status[1]}</text>
<rect x="{PX + .5}" y="{PY + .5}" width="{PW - 1}" height="{PH - 1}" rx="10" fill="{SURFACE}" stroke="{BORDER}"/>
<g clip-path="url(#pv)">{preview}</g>
{''.join(chip_svg)}"""
    x0 = 0 if SIDE.get(slug) == "left" else -GUTTER
    write(f"cards/{slug}.svg", svg(CW + GUTTER, CH, label, body, css, x0))


def card_chronoflow():
    ox, oy = PX, PY
    nodes = [("trigger", 52, 62), ("validate", 148, 34), ("enrich", 148, 90), ("approve", 250, 62), ("audit", 346, 62)]
    edges = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4)]
    out = []
    for a, b in edges:
        x1, y1 = ox + nodes[a][1] + 34, oy + nodes[a][2]
        x2, y2 = ox + nodes[b][1] - 34, oy + nodes[b][2]
        mx = (x1 + x2) / 2
        d = f"M{x1} {y1}C{mx} {y1} {mx} {y2} {x2} {y2}"
        out.append(f'<path d="{d}" stroke="{BORDER}" stroke-width="1.5"/><path d="{d}" stroke="{AMBER}" stroke-opacity=".7" stroke-width="1.5" class="flow"/>')
    delays = [0, .5, .5, 1.0, 1.5]
    for (name, x, y), dl in zip(nodes, delays):
        X, Y = ox + x, oy + y
        out.append(
            f'<rect x="{X - 34}" y="{Y - 13}" width="68" height="26" rx="7" fill="{BG}" stroke="{BORDER}"/>'
            f'<rect x="{X - 34}" y="{Y - 13}" width="68" height="26" rx="7" fill="{AMBER}" fill-opacity=".12" stroke="{AMBER}" class="run" style="animation-delay:{dl}s"/>'
            f'<text x="{X}" y="{Y + 4}" text-anchor="middle" class="mono" font-size="10.5" fill="{TEXT}">{name}</text>'
        )
    out.append(f'<text x="{ox + 14}" y="{oy + PH - 10}" class="mono" font-size="10.5" fill="{MUTED}"><tspan fill="{GREEN}">✓</tspan> run complete · audit trail sealed</text>')
    css = ".run{opacity:0;animation:run 3.2s ease-out infinite}@keyframes run{0%{opacity:0}10%{opacity:1}45%{opacity:.25}100%{opacity:0}}"
    card("chronoflow", "ChronoFlow", "Workflow orchestration for auditable ops", "workflow", AMBER, ("private", "private"),
         ["Next.js 15", "NestJS 11", "Postgres", "Redis", "Docker"], "".join(out),
         "ChronoFlow — visual workflow builder with 40+ node types, real-time collaboration and an auditable execution engine", css)


def card_mocklyst():
    ox, oy = PX + 14, PY + 24
    lines = [
        (f'<tspan fill="{GREEN}">$</tspan> curl mocklyst.vercel.app/api/<tspan fill="{CYAN}">x7f2</tspan>/users', 0),
        (f'<tspan fill="{GREEN}">HTTP/1.1 200 OK</tspan>  <tspan fill="{DIM}">·</tspan>  <tspan fill="{AMBER}">latency 142ms</tspan>', .7),
        (f'<tspan fill="{MUTED}">[{{ </tspan><tspan fill="{CYAN}">"id"</tspan>: 1, <tspan fill="{CYAN}">"name"</tspan>: <tspan fill="{GREEN}">"Ada"</tspan>, <tspan fill="{CYAN}">"role"</tspan>: <tspan fill="{GREEN}">"admin"</tspan><tspan fill="{MUTED}"> }}, …]</tspan>', 1.2),
    ]
    out = [
        f'<text x="{ox}" y="{oy + i * 24}" class="mono ln" font-size="11.5" fill="{TEXT}" style="animation-delay:{d}s">{t}</text>'
        for i, (t, d) in enumerate(lines)
    ]
    out.append(f'<rect x="{ox}" y="{oy + 66}" width="372" height="4" rx="2" fill="{BG}"/>')
    out.append(f'<rect x="{ox}" y="{oy + 66}" width="372" height="4" rx="2" fill="{CYAN}" class="bar"/>')
    out.append(f'<text x="{ox}" y="{oy + 88}" class="mono" font-size="10.5" fill="{MUTED}">endpoint live in &lt; 30s · expires in 7d</text>')
    css = (
        ".ln{animation:ln 4.5s ease infinite both}@keyframes ln{0%{opacity:0;transform:translateX(-6px)}8%,85%{opacity:1;transform:none}100%{opacity:0}}"
        ".bar{transform-box:fill-box;transform-origin:left;animation:bar 4.5s cubic-bezier(.2,.7,.2,1) infinite}@keyframes bar{0%,15%{transform:scaleX(0)}40%,85%{transform:scaleX(1)}100%{transform:scaleX(1);opacity:0}}"
    )
    card("mocklyst", "Mocklyst", "Instant API mocking — no signup, no install", "api-gateway", CYAN, ("live", "live"),
         ["Next.js 15", "React 19", "Supabase", "Tailwind 4"], "".join(out),
         "Mocklyst — a working mock API endpoint in under 30 seconds, with schema designer, status codes, latency and analytics", css)


def card_teacher():
    ox, oy = PX, PY
    paper = f"""
<rect x="{ox + 14}" y="{oy + 12}" width="210" height="140" rx="6" fill="#F8FAFC"/>
<text x="{ox + 28}" y="{oy + 34}" class="sans" font-size="11" font-weight="700" fill="#0F172A">Worksheet · Algebra I</text>
<text x="{ox + 28}" y="{oy + 56}" class="mono" font-size="11" fill="#334155">1.  2x + 6 = 14</text>
<text x="{ox + 28}" y="{oy + 76}" class="mono" font-size="11" fill="#334155">2.  ∫₀¹ x² dx = ⅓</text>
<rect x="{ox + 28}" y="{oy + 86}" width="180" height="22" rx="4" stroke="#94A3B8" stroke-dasharray="3 3"/>"""
    chip = f"""
<g class="drag"><rect x="{ox + 30}" y="{oy + 88}" width="176" height="18" rx="4" fill="{GREEN}" fill-opacity=".9"/>
<text x="{ox + 38}" y="{oy + 101}" class="mono" font-size="10.5" fill="#052E16">3.  multiple choice</text></g>"""
    side = f"""
<text x="{ox + 244}" y="{oy + 34}" class="mono" font-size="10.5" fill="{MUTED}">AI · generate</text>
<rect x="{ox + 244}" y="{oy + 44}" width="140" height="6" rx="3" fill="{BG}"/><rect x="{ox + 244}" y="{oy + 44}" width="140" height="6" rx="3" fill="{GREEN}" class="gen"/>
<text x="{ox + 244}" y="{oy + 78}" class="mono" font-size="10.5" fill="{MUTED}">KaTeX ✓</text>
<text x="{ox + 244}" y="{oy + 98}" class="mono" font-size="10.5" fill="{MUTED}">drag &amp; drop ✓</text>
<text x="{ox + 244}" y="{oy + 118}" class="mono" font-size="10.5" fill="{GREEN}">export .docx ↓</text>"""
    css = (
        ".drag{animation:drag 4s cubic-bezier(.3,.7,.2,1) infinite}@keyframes drag{0%{transform:translate(200px,-40px);opacity:0}15%{opacity:1}45%,85%{transform:none;opacity:1}100%{opacity:0}}"
        ".gen{transform-box:fill-box;transform-origin:left;animation:gen 4s ease infinite}@keyframes gen{0%{transform:scaleX(0)}40%,100%{transform:scaleX(1)}}"
    )
    card("teacher-toolbox", "Teacher Toolbox", "AI-generated worksheets for classrooms", "toolbox", GREEN, ("live", "live"),
         ["Next.js", "Strapi", "TanStack Query", "dnd-kit"], paper + chip + side,
         "Teacher Toolbox — AI worksheet generator with drag-and-drop builder, KaTeX math and DOCX export", css)


def card_azooz():
    cx, cy, s = PX + 80, PY + PH / 2, 30
    verts = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    edges = [(a, b) for a in range(8) for b in range(a + 1, 8) if sum(verts[a][k] != verts[b][k] for k in range(3)) == 1]
    tilt = math.radians(24)
    phase = math.radians(35)
    frames = 36

    def proj(v, th):
        x, y, z = v
        th += phase
        x, z = x * math.cos(th) + z * math.sin(th), -x * math.sin(th) + z * math.cos(th)
        y, z = y * math.cos(tilt) - z * math.sin(tilt), y * math.sin(tilt) + z * math.cos(tilt)
        k = 3.2 / (3.2 + z)  # perspective, so no frame reads as a flat square
        return cx + x * s * k, cy + y * s * k

    out = []
    for a, b in edges:
        pts = [(proj(verts[a], 2 * math.pi * f / frames), proj(verts[b], 2 * math.pi * f / frames)) for f in range(frames + 1)]
        anims = "".join(
            f'<animate attributeName="{attr}" values="{";".join(f"{p[i][j]:.1f}" for p in pts)}" dur="8s" repeatCount="indefinite"/>'
            for attr, i, j in (("x1", 0, 0), ("y1", 0, 1), ("x2", 1, 0), ("y2", 1, 1))
        )
        (x1, y1), (x2, y2) = pts[0]
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{PINK}" stroke-width="1.5" stroke-linecap="round">{anims}</line>')
    out.append(f'<ellipse cx="{cx}" cy="{cy + 50}" rx="38" ry="5" fill="{PINK}" fill-opacity=".12"/>')
    rx = PX + 170
    out.append(f"""
<text x="{rx}" y="{PY + 30}" class="mono" font-size="10.5" fill="{MUTED}">course · Motion Design</text>
<text x="{rx}" y="{PY + 52}" class="sans" font-size="14" font-weight="700" fill="{TEXT}">Module 3 · Springs &amp; easing</text>
<rect x="{rx}" y="{PY + 64}" width="210" height="6" rx="3" fill="{BG}"/>
<rect x="{rx}" y="{PY + 64}" width="210" height="6" rx="3" fill="{PINK}" class="prog"/>
<text x="{rx}" y="{PY + 92}" class="mono" font-size="10.5" fill="{MUTED}">lessons</text>
{''.join(f'<rect x="{rx + 58 + i * 16}" y="{PY + 83}" width="11" height="11" rx="3" fill="{PINK}" fill-opacity="{1 if i < 4 else .18}"/>' for i in range(8))}
<text x="{rx}" y="{PY + 112}" class="mono" font-size="10.5" fill="{DIM}">R3F scene · mixpanel funnel tracked</text>""")
    css = ".prog{transform-box:fill-box;transform-origin:left;animation:prog 5s cubic-bezier(.2,.7,.2,1) infinite}@keyframes prog{0%{transform:scaleX(.05)}60%,100%{transform:scaleX(.72)}}"
    card("azooz-lms", "Azooz LMS", "Learning management that feels like a product", "graduation-cap", PINK, ("live", "live"),
         ["Next.js", "R3F", "Framer Motion", "Mixpanel"], "".join(out),
         "Azooz LMS — course delivery and dashboards with React Three Fiber 3D scenes, Framer Motion and Mixpanel analytics", css)


def card_raycast():
    ox, oy = PX + 14, PY + 14
    out = f"""
<rect x="{ox}" y="{oy}" width="372" height="30" rx="8" fill="{BG}" stroke="{BORDER}"/>
<text x="{ox + 12}" y="{oy + 20}" class="mono" font-size="11.5" fill="{DIM}">⌘␣</text>
<text x="{ox + 44}" y="{oy + 20}" class="mono" font-size="11.5" fill="{TEXT}">fix my code pls<tspan fill="{PINK}" class="blink">▍</tspan></text>
<text x="{ox + 360}" y="{oy + 20}" text-anchor="end" class="mono" font-size="10.5" fill="#FF6363">enhance ↵</text>
<text x="{ox + 4}" y="{oy + 52}" class="mono ln" font-size="11" fill="{MUTED}" style="animation-delay:.6s"><tspan fill="#FF6363">→</tspan> Act as a senior TypeScript reviewer.</text>
<text x="{ox + 4}" y="{oy + 70}" class="mono ln" font-size="11" fill="{MUTED}" style="animation-delay:1.1s"><tspan fill="#FF6363">→</tspan> Find the bug, explain the root cause,</text>
<text x="{ox + 4}" y="{oy + 88}" class="mono ln" font-size="11" fill="{MUTED}" style="animation-delay:1.6s"><tspan fill="#FF6363">→</tspan> then propose a minimal diff + a test.</text>"""
    css = ".ln{animation:ln 4.5s ease infinite both}@keyframes ln{0%{opacity:0;transform:translateX(-6px)}8%,85%{opacity:1;transform:none}100%{opacity:0}}"
    card("raycast-prompt-enhancer", "Prompt Enhancer", "Raycast: a lazy prompt in, a good one out", "wand-sparkles", "#FF6363", ("oss", "open source"),
         ["TypeScript", "Raycast API", "LLM"], out,
         "Raycast Prompt Enhancer — a Raycast extension that rewrites weak prompts with an LLM without leaving the launcher", css)


def card_turbo_select():
    ox, oy = PX + 14, PY + 12
    chips, x = [], ox + 8
    for i, c in enumerate(["React", "Next.js", "Svelte"]):
        w = len(c) * 7 + 26
        chips.append(
            f'<g class="chip" style="animation-delay:{.4 + i * .6:.1f}s"><rect x="{x}" y="{oy + 6}" width="{w}" height="18" rx="9" fill="{VIOLET}" fill-opacity=".18" stroke="{VIOLET}" stroke-opacity=".5"/>'
            f'<text x="{x + 9}" y="{oy + 19}" class="mono" font-size="10.5" fill="{TEXT}">{c} <tspan fill="{MUTED}">×</tspan></text></g>'
        )
        x += w + 6
    opts = ["React", "Next.js", "Svelte", "Vue"]
    row = 18
    list_ = "".join(
        f'<text x="{ox + 14}" y="{oy + 52 + i * row}" class="mono" font-size="11" fill="{TEXT}">{o}</text>'
        f'<text x="{ox + 160}" y="{oy + 52 + i * row}" text-anchor="end" class="mono" font-size="11" fill="{VIOLET}">{"✓" if i < 3 else ""}</text>'
        for i, o in enumerate(opts)
    )
    out = f"""
<rect x="{ox}" y="{oy}" width="372" height="30" rx="8" fill="{BG}" stroke="{VIOLET}" stroke-opacity=".6"/>
{''.join(chips)}
<text x="{ox + 358}" y="{oy + 20}" text-anchor="end" class="mono" font-size="11" fill="{MUTED}">▾</text>
<rect x="{ox}" y="{oy + 36}" width="172" height="78" rx="8" fill="{BG}" stroke="{BORDER}"/>
<rect x="{ox + 4}" y="{oy + 39}" width="164" height="18" rx="5" fill="{VIOLET}" fill-opacity=".16" class="cur"/>
{list_}
<text x="{ox + 196}" y="{oy + 52}" class="mono" font-size="10.5" fill="{MUTED}">single · multi · tags</text>
<text x="{ox + 196}" y="{oy + 70}" class="mono" font-size="10.5" fill="{MUTED}">fully themeable</text>
<text x="{ox + 196}" y="{oy + 88}" class="mono" font-size="10.5" fill="{MUTED}">keyboard-first, a11y</text>
<text x="{ox + 196}" y="{oy + 108}" class="mono" font-size="10.5" fill="{VIOLET}">npm i react-turbo-select</text>"""
    css = (
        ".chip{animation:chip 4.2s cubic-bezier(.3,1.4,.5,1) infinite both}@keyframes chip{0%{opacity:0;transform:translateY(4px)}10%,85%{opacity:1;transform:none}100%{opacity:0}}"
        ".cur{animation:cur 4.2s steps(1) infinite}@keyframes cur{0%{transform:translateY(0)}14%{transform:translateY(0)}28%{transform:translateY(18px)}42%{transform:translateY(36px)}56%,100%{transform:translateY(54px)}}"
    )
    card("react-turbo-select", "react-turbo-select", "The select I kept rewriting — so I shipped it", "dropdown-menu", VIOLET, ("oss", "open source"),
         ["React", "TypeScript", "npm"], out,
         "react-turbo-select — a flexible, themeable React select with single, multi and tag modes", css)


def card_open_gebra():
    """Full-width featured card: copy on the left, a live sine graph on the right."""
    W, H = 880, 260
    accent = "#8B5CF6"
    gx, gy, gw, gh = 452, 20, 408, 220  # graph panel
    ox, oy = gx + gw / 2, gy + gh / 2 - 6  # graph origin
    ux, uy = 30, 26  # px per unit
    amps = [1.6, .8, 2.2, 1.6]
    xs = [i / 5 for i in range(-32, 33)]

    def wave(a):
        return "M" + "L".join(f"{ox + x * ux:.1f} {oy - a * math.sin(x) * uy:.1f}" for x in xs)

    period = 9
    d_vals = ";".join(wave(a) for a in amps)
    px = 3.6
    py_vals = ";".join(f"{oy - a * math.sin(px) * uy:.1f}" for a in amps)
    slider_x0, slider_w = gx + 150, 150
    knob_vals = ";".join(f"{slider_x0 + slider_w * (a - .5) / 2:.1f}" for a in amps)
    spline = "keySplines=\".45 0 .55 1;.45 0 .55 1;.45 0 .55 1\" calcMode=\"spline\""

    grid = []
    for i in range(-6, 7):
        x = ox + i * ux
        grid.append(f'<line x1="{x}" y1="{gy + 40}" x2="{x}" y2="{gy + gh - 40}" stroke="{BORDER}" stroke-opacity=".6"/>')
    for j in range(-2, 3):
        y = oy + j * uy
        grid.append(f'<line x1="{gx + 12}" y1="{y}" x2="{gx + gw - 12}" y2="{y}" stroke="{BORDER}" stroke-opacity=".6"/>')

    # amplitude readout: one text per value, shown in turn
    readouts = []
    n = len(amps) - 1
    for k, a in enumerate(amps[:-1]):
        vis = ";".join("1" if i == k else "0" for i in range(n)) + (";1" if k == 0 else ";0")
        readouts.append(
            f'<text x="{slider_x0 + slider_w + 14}" y="{gy + gh - 15}" class="mono" font-size="11.5" font-weight="700" fill="{TEXT}" opacity="{1 if k == 0 else 0}">{a}'
            f'<animate attributeName="opacity" values="{vis}" keyTimes="{";".join(f"{i / n:.3f}" for i in range(n + 1))}" calcMode="discrete" dur="{period}s" repeatCount="indefinite"/></text>'
        )

    tools = ["Graphing", "Geometry", "3D", "CAS", "AI worksheets"]
    chip_svg, x = [], 24
    for c in tools:
        w = len(c) * 7.4 + 18
        chip_svg.append(
            f'<rect x="{x + .5}" y="206.5" width="{w:.0f}" height="22" rx="11" fill="{SURFACE}" stroke="{BORDER}"/>'
            f'<text x="{x + w / 2 + .5:.1f}" y="221.5" text-anchor="middle" class="mono" font-size="11" fill="{MUTED}">{c}</text>'
        )
        x += w + 6

    body = f"""
<defs>{GRAD_DEFS}
<clipPath id="pv"><rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" rx="12"/></clipPath>
<linearGradient id="topline" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{accent}" stop-opacity="0"/><stop offset=".5" stop-color="{accent}"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/>
<animateTransform attributeName="gradientTransform" type="translate" values="-1 0;1 0" dur="4s" repeatCount="indefinite"/></linearGradient>
<linearGradient id="og" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{accent}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="50"/></filter>
</defs>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="15.5" fill="{BG}" stroke="{BORDER}"/>
<circle cx="200" cy="40" r="90" fill="{accent}" fill-opacity=".14" filter="url(#blur)"/>
<rect x="16" y=".5" width="{W - 32}" height="1.5" fill="url(#topline)"/>

<rect x="24" y="24" width="44" height="44" rx="11" fill="{accent}" fill-opacity=".16" stroke="{accent}" stroke-opacity=".45"/>
{koboyo("cosine-wave", 30, 30, 32, 32, accent)}
<text x="82" y="44" class="sans" font-size="24" font-weight="800" letter-spacing="-.4" fill="{TEXT}">Open <tspan fill="url(#og)">Gebra</tspan></text>
<text x="82" y="64" class="sans" font-size="13" fill="{MUTED}">An all-in-one interactive math suite</text>
<rect x="{gx - 124.5}" y="24.5" width="104" height="22" rx="11" fill="{accent}" fill-opacity=".14" stroke="{accent}" stroke-opacity=".5"/>
<circle cx="{gx - 110}" cy="35.5" r="3.5" fill="{GREEN}"/><circle cx="{gx - 110}" cy="35.5" r="3.5" fill="{GREEN}" class="pulse"/>
<text x="{gx - 101}" y="39.5" class="mono" font-size="11" fill="{TEXT}">new · live</text>

<text x="24" y="110" class="sans" font-size="15" fill="{TEXT}">Graph, construct, calculate and teach in one</text>
<text x="24" y="131" class="sans" font-size="15" fill="{TEXT}">connected workspace — <tspan fill="{accent}" font-weight="700">12 tools</tspan>, one canvas.</text>
<text x="24" y="166" class="mono" font-size="11.5" fill="{MUTED}"><tspan fill="{GREEN}">✓</tspan> no install   <tspan fill="{GREEN}">✓</tspan> no account   <tspan fill="{GREEN}">✓</tspan> classroom-ready</text>
<text x="24" y="190" class="mono" font-size="11.5" fill="{accent}">www.open-gebra.com ↗</text>
{''.join(chip_svg)}

<rect x="{gx + .5}" y="{gy + .5}" width="{gw - 1}" height="{gh - 1}" rx="12" fill="{SURFACE}" stroke="{BORDER}"/>
<g clip-path="url(#pv)">
  <text x="{gx + 16}" y="{gy + 24}" class="mono" font-size="11" fill="{MUTED}">Open Gebra / Graphing</text>
  <text x="{gx + gw - 16}" y="{gy + 24}" text-anchor="end" class="mono" font-size="11" fill="{accent}">y = a · sin(x)</text>
  {''.join(grid)}
  <line x1="{gx + 12}" y1="{oy}" x2="{gx + gw - 12}" y2="{oy}" stroke="{DIM}"/>
  <line x1="{ox}" y1="{gy + 40}" x2="{ox}" y2="{gy + gh - 40}" stroke="{DIM}"/>
  <path d="{wave(amps[0])}" stroke="{accent}" stroke-width="5" stroke-opacity=".18" stroke-linejoin="round">
    <animate attributeName="d" values="{d_vals}" dur="{period}s" repeatCount="indefinite" {spline}/></path>
  <path d="{wave(amps[0])}" stroke="url(#og)" stroke-width="2.4" stroke-linejoin="round">
    <animate attributeName="d" values="{d_vals}" dur="{period}s" repeatCount="indefinite" {spline}/></path>
  <circle cx="{ox + px * ux}" cy="{oy - amps[0] * math.sin(px) * uy:.1f}" r="5" fill="{BG}" stroke="{TEXT}" stroke-width="2">
    <animate attributeName="cy" values="{py_vals}" dur="{period}s" repeatCount="indefinite" {spline}/></circle>
  <text x="{ox + px * ux - 12}" y="{oy + 44}" text-anchor="end" class="mono" font-size="10.5" fill="{MUTED}">P = (3.6, a·sin 3.6)</text>
  <text x="{gx + 16}" y="{gy + gh - 15}" class="mono" font-size="11" fill="{MUTED}">amplitude</text>
  <rect x="{slider_x0}" y="{gy + gh - 22}" width="{slider_w}" height="4" rx="2" fill="{BORDER}"/>
  <circle cx="{slider_x0 + slider_w * .55:.1f}" cy="{gy + gh - 20}" r="7" fill="{accent}" stroke="{BG}" stroke-width="2">
    <animate attributeName="cx" values="{knob_vals}" dur="{period}s" repeatCount="indefinite" {spline}/></circle>
  {''.join(readouts)}
</g>"""
    write("cards/open-gebra.svg", svg(W, H, "Open Gebra — an all-in-one interactive math suite: graphing, geometry, 3D, CAS and AI worksheets in one workspace", body))


# ── stack ─────────────────────────────────────────────────────────────────
VENDOR = OUT / "vendor"


def koboyo(slug, x, y, w, h, color, extra=""):
    """Hand-drawn icon from koboyo.com/icons (free for commercial use, no
    attribution required), cached in assets/vendor/koboyo and inlined as a
    nested <svg> so it can take any palette colour. The files are plain
    filled paths, so they inherit the fill set here."""
    path = VENDOR / "koboyo" / f"{slug}.svg"
    if not path.exists():
        req = urllib.request.Request(f"https://koboyo.com/icons/svg/{slug}.svg", headers={"User-Agent": "profile-readme-build"})
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(urllib.request.urlopen(req, timeout=30).read())
    src = path.read_text()
    vb = re.search(r'viewBox="([^"]+)"', src).group(1)
    inner = src[src.index(">", src.index("<svg")) + 1 : src.rindex("</svg>")]
    return f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="{vb}" fill="{color}"{extra}>{inner}</svg>'


def skillicons(row, ids):
    """Skill icon strip from skillicons.dev, cached in assets/vendor so the
    build is repeatable offline and the README never depends on that host.
    Element ids are prefixed per row so nested strips cannot collide."""
    path = VENDOR / f"skillicons-{row}.svg"
    if not path.exists():
        url = f"https://skillicons.dev/icons?i={','.join(ids)}&perline={len(ids)}"
        VENDOR.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "profile-readme-build"})  # default UA gets a 403
        path.write_bytes(urllib.request.urlopen(req, timeout=30).read())
    src = path.read_text()
    vb = re.search(r'viewBox="([^"]+)"', src).group(1)
    inner = src[src.index(">", src.index("<svg")) + 1 : src.rindex("</svg>")]
    inner = re.sub(r'id="([^"]+)"', rf'id="{row}-\1"', inner)
    inner = re.sub(r"url\(#([^)]+)\)", rf"url(#{row}-\1)", inner)
    inner = re.sub(r'href="#([^"]+)"', rf'href="#{row}-\1"', inner)
    return vb, inner


def stack():
    W = 880
    icon_rows = [
        ("frontend", ["ts", "js", "react", "nextjs", "redux", "tailwind", "sass", "html", "css", "angular"]),
        ("backend", ["nodejs", "nestjs", "express", "postgres", "mysql", "mongodb", "redis", "supabase", "python"]),
        ("delivery", ["git", "githubactions", "docker", "jest", "vercel", "figma", "vscode", "threejs"]),
    ]
    chip_rows = [
        ("ui_motion", [("shadcn/ui", TEXT), ("Radix", TEXT), ("Framer Motion", VIOLET), ("React Native", CYAN), ("Chakra UI", GREEN)]),
        ("ai_tooling", [("Claude", "#D97757"), ("Anthropic API", TEXT), ("OpenAI API", TEXT), ("MCP servers", CYAN), ("Raycast", "#FF6363")]),
    ]
    top, step, ix = 64, 58, 196
    rows = []
    for i, (key, ids) in enumerate(icon_rows):
        y = top + i * step
        vb, inner = skillicons(key, ids)
        vw, vh = map(float, vb.split()[2:])
        h = 40
        rows.append(
            f'<g class="up" style="animation-delay:{.2 + i * .12:.2f}s">'
            f'<text x="28" y="{y + 26}" class="mono" font-size="14"><tspan fill="{CYAN}">{key}</tspan><tspan fill="{MUTED}">:</tspan></text>'
            f'<svg x="{ix}" y="{y}" width="{vw * h / vh:.1f}" height="{h}" viewBox="{vb}">{inner}</svg></g>'
        )
    for j, (key, chips) in enumerate(chip_rows):
        i = len(icon_rows) + j
        y = top + i * step
        out, x = [], ix
        for name, col in chips:
            w = len(name) * 7.8 + 34
            out.append(
                f'<rect x="{x + .5}" y="{y + 6.5}" width="{w:.0f}" height="28" rx="14" fill="{SURFACE}" stroke="{BORDER}"/>'
                f'<circle cx="{x + 15}" cy="{y + 20.5}" r="4" fill="{col}"/>'
                f'<text x="{x + 26}" y="{y + 25}" class="mono" font-size="12.5" fill="{TEXT}">{esc(name)}</text>'
            )
            x += w + 8
        rows.append(
            f'<g class="up" style="animation-delay:{.2 + i * .12:.2f}s">'
            f'<text x="28" y="{y + 26}" class="mono" font-size="14"><tspan fill="{CYAN}">{key}</tspan><tspan fill="{MUTED}">:</tspan></text>'
            f'{"".join(out)}</g>'
        )
    H = top + (len(icon_rows) + len(chip_rows)) * step + 6
    body = f"""
<defs>{GRAD_DEFS}</defs>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="15.5" fill="{BG}" stroke="{BORDER}"/>
{chrome(W, "~/profile/stack.yaml")}
<line x1="{ix - 20.5}" y1="52" x2="{ix - 20.5}" y2="{H - 14}" stroke="{BORDER}"/>
{''.join(rows)}"""
    write("stack.svg", svg(W, H, "Stack — frontend: TypeScript, JavaScript, React, Next.js, Redux, Tailwind, Sass, HTML, CSS, Angular; backend: Node.js, NestJS, Express, PostgreSQL, MySQL, MongoDB, Redis, Supabase, Python; delivery: Git, GitHub Actions, Docker, Jest, Vercel, Figma, VS Code, Three.js; UI and motion: shadcn/ui, Radix, Framer Motion, React Native, Chakra UI; AI tooling: Claude, Anthropic API, OpenAI API, MCP servers, Raycast", body))


# ── section headers (dark + light variants, transparent background) ───────
def section_headers():
    palettes = {
        "dark": dict(title="#E6EDF3", muted="#8B97A8", line="#30363D", accent=CYAN, accent2=VIOLET),
        "light": dict(title="#1F2328", muted="#59636E", line="#D1D9E0", accent="#0891B2", accent2="#7C3AED"),
    }
    sections = [
        ("about", "About", "~/about.md", "teacher-laptop"),
        ("now", "Right now", "~/now.ts", "coffee-mug"),
        ("stack", "Stack", "~/stack.yaml", "layers"),
        ("work", "Selected work", "~/projects/*", "briefcase"),
        ("ship", "How I ship", "~/Makefile", "deploy-rocket"),
        ("telemetry", "Telemetry", "~/.github/stats", "chart"),
    ]
    W, H = 880, 64
    for i, (slug, title, path, icon) in enumerate(sections, 1):
        for mode, p in palettes.items():
            css = """
.scan{animation:scan 5s cubic-bezier(.6,0,.4,1) infinite;transform-box:view-box}
@keyframes scan{from{transform:translateX(-240px)}to{transform:translateX(900px)}}
"""
            body = f"""
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{p['accent']}" stop-opacity="0"/><stop offset=".5" stop-color="{p['accent']}"/><stop offset="1" stop-color="{p['accent2']}" stop-opacity="0"/></linearGradient></defs>
{koboyo(icon, 0, 12, 34, 34, p['accent'])}
<text x="46" y="38" class="mono" font-size="14" font-weight="700" fill="{p['accent']}">{i:02d}</text>
<text x="76" y="38" class="mono" font-size="14" fill="{p['muted']}">/</text>
<text x="92" y="39" class="sans" font-size="25" font-weight="800" letter-spacing="-.4" fill="{p['title']}">{esc(title)}</text>
<text x="{W}" y="38" text-anchor="end" class="mono" font-size="13" fill="{p['muted']}">{esc(path)}</text>
<rect x="0" y="54" width="{W}" height="1" fill="{p['line']}"/>
<rect x="0" y="53.5" width="200" height="2" rx="1" fill="url(#g)" class="scan"/>"""
            write(f"headers/{slug}-{mode}.svg", svg(W, H, f"{i:02d} — {title}", body, css))


# ── footer ────────────────────────────────────────────────────────────────
def footer():
    W, H = 880, 150
    body = f"""
<defs>{GRAD_DEFS}<clipPath id="c"><rect width="{W}" height="{H}" rx="16"/></clipPath>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="50"/></filter></defs>
<g clip-path="url(#c)">
<rect width="{W}" height="{H}" fill="{BG}"/>
<circle cx="760" cy="150" r="120" fill="{VIOLET}" fill-opacity=".14" filter="url(#blur)"/>
<circle cx="120" cy="0" r="110" fill="{CYAN}" fill-opacity=".12" filter="url(#blur)"/>
<g class="float">{koboyo("handshake", 690, 30, 156, 90, VIOLET, ' fill-opacity=".85"')}</g>
<text x="32" y="46" class="mono" font-size="14" fill="{TEXT}"><tspan fill="{GREEN}">➜</tspan> <tspan fill="{CYAN}">~/profile</tspan> echo $NEXT</text>
<text x="32" y="88" class="sans up" style="animation-delay:.4s" font-size="26" font-weight="800" letter-spacing="-.5" fill="url(#brand)">Let's build something people actually use.</text>
<text x="32" y="122" class="mono fade" style="animation-delay:.9s" font-size="13" fill="{MUTED}">mohamedwaelbishr@gmail.com <tspan fill="{DIM}">·</tspan> process exited with code <tspan fill="{GREEN}">0</tspan> <tspan fill="{CYAN}" class="blink">▍</tspan></text>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="15.5" stroke="{BORDER}"/>"""
    css = ".float{animation:float 4s ease-in-out infinite alternate}@keyframes float{to{transform:translateY(-6px)}}"
    write("footer.svg", svg(W, H, "Let's build something people actually use — mohamedwaelbishr@gmail.com", body, css))


if __name__ == "__main__":
    print("building assets/")
    hero()
    now_editor()
    pipeline()
    stack()
    card_open_gebra()
    card_chronoflow()
    card_mocklyst()
    card_teacher()
    card_azooz()
    card_raycast()
    card_turbo_select()
    section_headers()
    footer()
