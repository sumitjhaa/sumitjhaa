"""
Generates a Weekly Activity bar chart SVG.
Shows commits per day of week (Mon-Sun).
Rose Pine Dark theme. Pure CSS animations.
"""
import os
import requests
from pathlib import Path
from datetime import datetime, timedelta

USERNAME = "sumitjhaa"
OUTPUT_DARK = Path("img/profile/weekly_activity_dark.svg")
OUTPUT_LIGHT = Path("img/profile/weekly_activity_light.svg")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
} if TOKEN else {}

RP_DARK = {
    "base": "#191724", "surface": "#1f1d2e", "overlay": "#26233a",
    "muted": "#6e6a86", "subtle": "#908caa", "text": "#e0def4",
    "love": "#eb6f92", "gold": "#f6c177", "rose": "#ebbcba",
    "pine": "#31748f", "foam": "#9ccfd8", "iris": "#c4a7e7",
    "hl_med": "#403d52",
}
RP_LIGHT = {
    "base": "#faf4ed", "surface": "#fffaf3", "overlay": "#f2e9e1",
    "muted": "#9893a5", "subtle": "#797593", "text": "#575279",
    "love": "#d7827e", "gold": "#ea9d34", "rose": "#d7827e",
    "pine": "#286983", "foam": "#56949f", "iris": "#907aa9",
    "hl_med": "#cecacd",
}

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def fetch_weekly():
    """Fetch commit counts per day of week from last 7 days."""
    counts = [0] * 7
    if not TOKEN:
        return counts
    try:
        r = requests.get(
            f"https://api.github.com/users/{USERNAME}/events/public?per_page=100",
            headers=HEADERS, timeout=10,
        )
        r.raise_for_status()
        now = datetime.now().astimezone()
        week_ago = now - timedelta(days=7)
        for event in r.json():
            if event["type"] != "PushEvent":
                continue
            dt = datetime.fromisoformat(event["created_at"].replace("Z", "+00:00"))
            if dt < week_ago:
                continue
            day_idx = dt.weekday()
            commits = len(event.get("payload", {}).get("commits", []))
            counts[day_idx] += commits
    except Exception as e:
        print(f"Fetch failed: {e}")
    return counts


def fallback_weekly():
    return [12, 8, 15, 5, 20, 3, 1]


def bar_color(pct):
    if pct > 70:
        return "#eb6f92"
    elif pct > 40:
        return "#f6c177"
    elif pct > 15:
        return "#31748f"
    else:
        return "#26233a"


def escape_xml(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def generate_svg(counts, theme, output_path):
    W = 488
    pad = 16
    bar_area_x = 48
    bar_area_w = W - bar_area_x - pad
    bar_w = bar_area_w // 7 - 6
    bar_max_h = 72
    baseline_y = pad + bar_max_h + 8
    H = baseline_y + 32 + pad

    max_val = max(counts) or 1
    total = sum(counts)

    bars_svg = []
    for i, count in enumerate(counts):
        x = bar_area_x + i * (bar_w + 6)
        h = max(2, int(bar_max_h * count / max_val)) if count > 0 else 2
        y = baseline_y - h
        pct = count / max_val * 100
        color = bar_color(pct)
        delay = round(0.2 + i * 0.08, 2)

        bars_svg.append(f"""
    <rect x="{x}" y="{baseline_y}" width="{bar_w}" height="0" rx="3" fill="{theme['hl_med']}" opacity="0.3"/>
    <rect x="{x}" y="{baseline_y}" width="{bar_w}" height="0" rx="3" fill="{color}" opacity="0.85">
      <animate attributeName="height" from="0" to="{h}" dur="0.5s"
        begin="{delay}s" fill="freeze" calcMode="spline"
        keySplines="0.25 0.1 0.25 1" keyTimes="0;1"/>
      <animate attributeName="y" from="{baseline_y}" to="{y}" dur="0.5s"
        begin="{delay}s" fill="freeze" calcMode="spline"
        keySplines="0.25 0.1 0.25 1" keyTimes="0;1"/>
    </rect>
    <text x="{x + bar_w // 2}" y="{y - 5}" text-anchor="middle" font-family="'JetBrains Mono',monospace"
          font-size="8" fill="{theme['subtle']}" opacity="0">
      {count}
      <animate attributeName="opacity" from="0" to="1" begin="{delay + 0.3}s" dur="0.2s" fill="freeze"/>
    </text>
    <text x="{x + bar_w // 2}" y="{baseline_y + 14}" text-anchor="middle" font-family="'JetBrains Mono',monospace"
          font-size="8" fill="{theme['muted']}">{DAYS[i]}</text>""")

    bars_block = "\n".join(bars_svg)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <defs>
    <linearGradient id="wkBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{theme['base']}"/>
      <stop offset="100%" stop-color="{theme['surface']}"/>
    </linearGradient>
  </defs>

  <rect width="{W}" height="{H}" rx="10" fill="url(#wkBg)" stroke="{theme['hl_med']}" stroke-width="1"/>

  {bars_block}

  <text x="{W // 2}" y="{H - 8}" text-anchor="middle" font-family="'JetBrains Mono',monospace"
        font-size="9" fill="{theme['subtle']}">{total} commits this week</text>
</svg>"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg, encoding="utf-8")
    print(f"Generated {output_path} ({len(svg)} bytes)")


def main():
    counts = fetch_weekly()
    if sum(counts) == 0:
        print("Using fallback (set GITHUB_TOKEN for real data)")
        counts = fallback_weekly()
    print(f"Weekly commits: {counts}")
    generate_svg(counts, RP_DARK, OUTPUT_DARK)
    generate_svg(counts, RP_LIGHT, OUTPUT_LIGHT)


if __name__ == "__main__":
    main()
