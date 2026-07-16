"""
Generates a Language Grid SVG.
Treemap-style grid showing language distribution.
Rose Pine Dark theme. Pure CSS animations.
"""
import os
import requests
from pathlib import Path

USERNAME = "sumitjhaa"
OUTPUT_SVG = Path("img/profile/lang_grid.svg")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
} if TOKEN else {}

RP = {
    "base": "#191724", "surface": "#1f1d2e", "overlay": "#26233a",
    "muted": "#6e6a86", "subtle": "#908caa", "text": "#e0def4",
    "love": "#eb6f92", "gold": "#f6c177", "rose": "#ebbcba",
    "pine": "#31748f", "foam": "#9ccfd8", "iris": "#c4a7e7",
    "hl_med": "#403d52",
}

LANG_COLORS = {
    "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6",
    "C++": "#f34b7d", "HTML": "#e34c26", "CSS": "#563d7c", "Shell": "#89e051",
    "Rust": "#dea584", "Go": "#00ADD8", "Java": "#b07219", "Ruby": "#701516",
    "PHP": "#4F5D95", "Swift": "#F05138", "Kotlin": "#A97BFF", "Dart": "#00B4AB",
    "Jupyter Notebooks": "#DA5B0B", "Markdown": "#083fa1", "JSON": "#292929",
}


def fetch_languages():
    """Fetch language byte counts."""
    lang_bytes = {}
    if not TOKEN:
        return lang_bytes
    page = 1
    while page <= 3:
        try:
            r = requests.get(
                f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}",
                headers=HEADERS, timeout=10,
            )
            r.raise_for_status()
            repos = r.json()
            if not repos:
                break
            for repo in repos:
                if repo.get("fork"):
                    continue
                try:
                    lr = requests.get(
                        f"https://api.github.com/repos/{USERNAME}/{repo['name']}/languages",
                        headers=HEADERS, timeout=10,
                    )
                    lr.raise_for_status()
                    for lang, b in lr.json().items():
                        lang_bytes[lang] = lang_bytes.get(lang, 0) + b
                except Exception:
                    pass
            page += 1
        except Exception:
            break
    return lang_bytes


def fallback_languages():
    return {"Python": 50000, "JavaScript": 30000, "TypeScript": 20000, "C++": 10000, "HTML": 8000, "CSS": 5000}


def escape_xml(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def squarify(rect, values, results):
    """Recursively divide rectangle using squarified treemap algorithm."""
    if not values:
        return

    if len(values) == 1:
        results.append((rect, values[0]))
        return

    x, y, w, h = rect
    total = sum(v for _, v in values)

    # Try splitting horizontally or vertically
    if w >= h:
        # Split vertically
        best_ratio = float('inf')
        best_split = 1
        for i in range(1, len(values)):
            left_sum = sum(v for _, v in values[:i])
            right_sum = total - left_sum
            left_w = w * left_sum / total
            right_w = w - left_w

            # Calculate aspect ratios
            left_h = h
            right_h = h

            # Check worst aspect ratio
            worst = 0
            for j in range(i):
                rw = left_w
                rh = h * values[j][1] / left_sum if left_sum > 0 else h
                ratio = max(rw / rh, rh / rw) if rh > 0 else float('inf')
                worst = max(worst, ratio)
            for j in range(i, len(values)):
                rw = right_w
                rh = h * values[j][1] / right_sum if right_sum > 0 else h
                ratio = max(rw / rh, rh / rw) if rh > 0 else float('inf')
                worst = max(worst, ratio)

            if worst < best_ratio:
                best_ratio = worst
                best_split = i

        left_sum = sum(v for _, v in values[:best_split])
        left_w = w * left_sum / total

        squarify((x, y, left_w, h), values[:best_split], results)
        squarify((x + left_w, y, w - left_w, h), values[best_split:], results)
    else:
        # Split horizontally
        best_ratio = float('inf')
        best_split = 1
        for i in range(1, len(values)):
            top_sum = sum(v for _, v in values[:i])
            bottom_sum = total - top_sum
            top_h = h * top_sum / total
            bottom_h = h - top_h

            worst = 0
            for j in range(i):
                rw = w * values[j][1] / top_sum if top_sum > 0 else w
                rh = top_h
                ratio = max(rw / rh, rh / rw) if rh > 0 else float('inf')
                worst = max(worst, ratio)
            for j in range(i, len(values)):
                rw = w * values[j][1] / bottom_sum if bottom_sum > 0 else w
                rh = bottom_h
                ratio = max(rw / rh, rh / rw) if rh > 0 else float('inf')
                worst = max(worst, ratio)

            if worst < best_ratio:
                best_ratio = worst
                best_split = i

        top_sum = sum(v for _, v in values[:best_split])
        top_h = h * top_sum / total

        squarify((x, y, w, top_h), values[:best_split], results)
        squarify((x, y + top_h, w, h - top_h), values[best_split:], results)


def generate_svg(lang_bytes):
    W = 400
    H = 250
    pad = 10
    grid_y = pad
    grid_h = H - grid_y - pad
    grid_w = W - pad * 2

    total = sum(lang_bytes.values()) or 1
    sorted_langs = sorted(lang_bytes.items(), key=lambda x: -x[1])[:8]

    # Calculate percentages
    values = [(lang, b / total) for lang, b in sorted_langs]

    # Squarify layout
    results = []
    squarify((pad, grid_y, grid_w, grid_h), values, results)

    rects_svg = []
    for i, ((x, y, w, h), (lang, pct)) in enumerate(results):
        color = LANG_COLORS.get(lang, RP["iris"])
        delay = round(0.1 + i * 0.06, 2)

        # Determine text color based on brightness
        r_val = int(color[1:3], 16)
        g_val = int(color[3:5], 16)
        b_val = int(color[5:7], 16)
        brightness = (r_val * 299 + g_val * 587 + b_val * 114) / 1000
        text_color = RP["base"] if brightness > 128 else RP["text"]

        name = escape_xml(lang)
        pct_text = f"{pct * 100:.0f}%"

        # Adjust font size based on rectangle size
        font_size = min(14, max(8, int(min(w, h) / 5)))

        rects_svg.append(f"""
    <g opacity="0" style="animation:fadeBadge 0.3s {delay}s forwards">
      <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3"
            fill="{color}" opacity="0.9"/>
      <text x="{x + w // 2}" y="{y + h // 2 - 3}" text-anchor="middle"
            font-family="'JetBrains Mono',monospace" font-size="{font_size}" fill="{text_color}" font-weight="bold">
        {name}
      </text>
      <text x="{x + w // 2}" y="{y + h // 2 + font_size}" text-anchor="middle"
            font-family="'JetBrains Mono',monospace" font-size="{font_size - 1}" fill="{text_color}" opacity="0.85">
        {pct_text}
      </text>
    </g>""")

    rects_block = "\n".join(rects_svg)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%">
  <defs>
    <linearGradient id="lgBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{RP['base']}"/>
      <stop offset="100%" stop-color="{RP['surface']}"/>
    </linearGradient>
    <style>
      @keyframes fadeBadge {{
        from {{ opacity: 0; transform: scale(0.95); }}
        to   {{ opacity: 1; transform: scale(1); }}
      }}
    </style>
  </defs>

  <rect width="{W}" height="{H}" rx="8" fill="url(#lgBg)" stroke="{RP['hl_med']}" stroke-width="1"/>

  {rects_block}
</svg>"""
    OUTPUT_SVG.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_SVG.write_text(svg, encoding="utf-8")
    print(f"Generated {OUTPUT_SVG} ({len(svg)} bytes)")
    print(f"Languages: {', '.join(f'{lang} {pct*100:.0f}%' for lang, pct in values)}")


def main():
    lang_bytes = fetch_languages()
    if not lang_bytes:
        print("Using fallback (set GITHUB_TOKEN for real data)")
        lang_bytes = fallback_languages()
    print(f"Languages: {len(lang_bytes)}")
    generate_svg(lang_bytes)


if __name__ == "__main__":
    main()
