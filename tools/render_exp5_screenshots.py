# -*- coding: utf-8 -*-
"""把 exp5_results/exp5_log.txt 切片渲染成控制台风格 PNG，供报告插图。

用法：python render_exp5_screenshots.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path("exp5_results")
LOG = OUT / "exp5_log.txt"

BG = (12, 12, 12)
FG = (204, 204, 204)
ACCENT = (120, 220, 120)  # 分节横幅用绿色
FONT_PATH = "C:/Windows/Fonts/msyh.ttc"
FONT_SIZE = 20
LINE_GAP = 6
PADDING = 24
WIDTH = 1180
WRAP_COLS = 92  # 每行超过约 92 个字符宽度才折行（中文按 2 计）


def text_width(s: str) -> int:
    return sum(2 if ord(c) > 0x2E7F else 1 for c in s)


def wrap_line(line: str) -> list[str]:
    if text_width(line) <= WRAP_COLS:
        return [line]
    parts, cur, w = [], "", 0
    for ch in line:
        cw = 2 if ord(ch) > 0x2E7F else 1
        if w + cw > WRAP_COLS:
            parts.append(cur)
            cur, w = ch, cw
        else:
            cur += ch
            w += cw
    if cur:
        parts.append(cur)
    return parts


def render(lines: list[str], save_path: Path, max_lines: int = 46,
           keep_head: int = 1) -> None:
    if len(lines) > max_lines:
        lines = lines[:keep_head] + ["    ......"] + lines[-(max_lines - keep_head - 1):]
    flat = []
    for line in lines:
        flat.extend(wrap_line(line))
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    line_h = FONT_SIZE + LINE_GAP
    height = PADDING * 2 + line_h * len(flat)
    img = Image.new("RGB", (WIDTH, height), BG)
    draw = ImageDraw.Draw(img)
    y = PADDING
    for line in flat:
        color = ACCENT if line.startswith("=====") else FG
        draw.text((PADDING, y), line, fill=color, font=font)
        y += line_h
    img.save(save_path)
    print(f"saved {save_path} ({len(flat)} 行)")


def slice_between(lines: list[str], start_marker: str, end_marker: str) -> list[str]:
    start = next(i for i, l in enumerate(lines) if start_marker in l)
    end = next((i for i, l in enumerate(lines[start + 1:], start + 1) if end_marker in l),
               len(lines))
    return lines[start:end]


def main() -> None:
    lines = LOG.read_text(encoding="utf-8").splitlines()

    render(slice_between(lines, "===== A", "===== B"),
           OUT / "exp5_group_a.png")
    render(slice_between(lines, "===== B", "===== 进阶任务"),
           OUT / "exp5_group_b.png")
    render(slice_between(lines, "===== 进阶任务", "===== 字段核验"),
           OUT / "exp5_group_adv.png")


if __name__ == "__main__":
    main()
