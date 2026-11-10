"""Render training-log excerpts as console-style PNG images for the report.

Usage: python make_log_screenshots.py
Reads exp3_results/exp3_log.txt and writes exp3_results/exp3_log_*.png.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path("exp3_results")
LOG = OUT / "exp3_log.txt"

BG = (12, 12, 12)
FG = (204, 204, 204)
ACCENT = (120, 220, 120)  # green for section banners
FONT_PATH = "C:/Windows/Fonts/msyh.ttc"  # Microsoft YaHei (covers CJK)
FONT_SIZE = 20
LINE_GAP = 6
PADDING = 24
WIDTH = 1180


def render(lines: list[str], save_path: Path, highlight: bool = False) -> None:
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    line_h = FONT_SIZE + LINE_GAP
    height = PADDING * 2 + line_h * len(lines)
    img = Image.new("RGB", (WIDTH, height), BG)
    draw = ImageDraw.Draw(img)
    y = PADDING
    for line in lines:
        color = ACCENT if (highlight and line.startswith("=====")) else FG
        draw.text((PADDING, y), line, fill=color, font=font)
        y += line_h
    img.save(save_path)
    print(f"saved {save_path}")


def slice_between(lines: list[str], start_marker: str, end_marker: str) -> list[str]:
    start = next(i for i, l in enumerate(lines) if start_marker in l)
    end = next((i for i, l in enumerate(lines[start:], start) if end_marker in l),
               len(lines))
    return lines[start:end]


def main() -> None:
    lines = LOG.read_text(encoding="utf-8").splitlines()

    render(lines[:11], OUT / "exp3_log_env.png", highlight=True)

    baseline = slice_between(lines, "===== 实验 baseline", "===== 实验 bs32")
    render(baseline, OUT / "exp3_log_baseline.png", highlight=True)

    final = slice_between(lines, "===== 实验 final", "===== 实验汇总")
    if len(final) > 46:  # keep head + tail so it fits on one image
        final = final[:32] + ["    ......(中间轮次省略)......"] + final[-14:]
    render(final, OUT / "exp3_log_final.png", highlight=True)

    summary_start = next(i for i, l in enumerate(lines) if "实验汇总" in l)
    summary = lines[summary_start:]
    if len(summary) > 44:
        summary = summary[:30] + ["    ......"] + summary[-14:]
    render(summary, OUT / "exp3_log_summary.png", highlight=True)


if __name__ == "__main__":
    main()
