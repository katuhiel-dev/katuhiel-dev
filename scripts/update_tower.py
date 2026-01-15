from __future__ import annotations
import csv
from datetime import date, datetime, timedelta
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA = REPO_ROOT / "data" / "drinks.csv"
FLAVORS_DIR = REPO_ROOT / "assets" / "flavors"
TOWER_OUT = REPO_ROOT / "assets" / "tower_week.png"
TOTAL_BADGE = REPO_ROOT / "assets" / "total_count.svg"

FLAVOR_TO_FILE = {
    "original": "monster.png",
    "ultra-zero": "ultra-zero.png",
    "electric-blue": "electric-blue.png",
    "sunrise": "sunrise.png",
    "ultra-black": "ultra-black.png",
    "rosa": "rosa.png",
    "paradise": "paradise.png",
}

def week_start(d: date) -> date:
    return d - timedelta(days=d.weekday())  # Monday start

def load_rows() -> list[dict]:
    if not DATA.exists():
        return []
    with DATA.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def load_this_week(rows: list[dict]) -> list[str]:
    today = date.today()
    start = week_start(today)
    out: list[str] = []

    for row in rows:
        try:
            d = datetime.strptime(row["date"], "%Y-%m-%d").date()
        except Exception:
            continue
        if start <= d <= today:
            out.append(row["flavor"].strip())
    return out

def write_total_badge(count: int) -> None:
    label = "Total"
    value = str(count)

    label_w = 52
    value_w = max(28, 10 + 8 * len(value))
    w = label_w + value_w
    h = 20

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" role="img" aria-label="{label}: {value}">
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="{w}" height="{h}" rx="4" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="{label_w}" height="{h}" fill="#555"/>
    <rect x="{label_w}" width="{value_w}" height="{h}" fill="#ff69b4"/>
    <rect width="{w}" height="{h}" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle"
     font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
    <text x="{label_w/2}" y="14">{label}</text>
    <text x="{label_w + value_w/2}" y="14">{value}</text>
  </g>
</svg>"""

    TOTAL_BADGE.parent.mkdir(parents=True, exist_ok=True)
    TOTAL_BADGE.write_text(svg, encoding="utf-8")

def generate_tower(this_week: list[str]) -> None:
    target_h = 70  # tower size: 40 tiny, 70 nice, 110 big

    if not this_week:
        img = Image.new("RGBA", (520, target_h + 30), (0, 0, 0, 0))
        TOWER_OUT.parent.mkdir(parents=True, exist_ok=True)
        img.save(TOWER_OUT)
        return

    sample_key = next((k for k in this_week if k in FLAVOR_TO_FILE), "original")
    sample_path = FLAVORS_DIR / FLAVOR_TO_FILE[sample_key]
    base = Image.open(sample_path).convert("RGBA")

    scale = target_h / base.height
    target_w = int(base.width * scale)

    def load_can(key: str) -> Image.Image:
        fname = FLAVOR_TO_FILE.get(key, FLAVOR_TO_FILE["original"])
        im = Image.open(FLAVORS_DIR / fname).convert("RGBA")
        return im.resize((target_w, target_h), Image.NEAREST)

    cans = [load_can(k) for k in this_week]

    gap = 10
    per_row = 10
    rows = (len(cans) + per_row - 1) // per_row

    width = per_row * target_w + (per_row - 1) * gap
    height = rows * target_h + (rows - 1) * gap

    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    for idx, c in enumerate(cans):
        r = idx // per_row
        col = idx % per_row
        x = col * (target_w + gap)
        y = r * (target_h + gap)
        canvas.alpha_composite(c, (x, y))

    TOWER_OUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(TOWER_OUT)

def main() -> None:
    rows = load_rows()
    this_week = load_this_week(rows)
    write_total_badge(len(rows))
    generate_tower(this_week)

if __name__ == "__main__":
    main()
