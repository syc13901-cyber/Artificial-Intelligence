# -*- coding: utf-8 -*-
"""把 exp4_results/exp4_log.txt 切片渲染成控制台风格 PNG，供报告插图。

用法：python render_exp4_screenshots.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path("exp4_results")
LOG = OUT / "exp4_log.txt"

BG = (12, 12, 12)
FG = (204, 204, 204)
ACCENT = (120, 220, 120)  # 分节横幅用绿色
FONT_PATH = "C:/Windows/Fonts/msyh.ttc"
FONT_SIZE = 20
LINE_GAP = 6
PADDING = 24
WIDTH = 1180
WRAP_COLS = 92  # 每行超过约 92 个字符宽度才折行（中文按 2 计），分类报告行保持完整


def text_width(s: str) -> int:
    return sum(2 if ord(c) > 0x2E7F else 1 for c in s)


def wrap_line(line: str) -> list[str]:
    """按显示宽度折行，避免长行超出图片宽度。"""
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


def drop_between(lines: list[str], start_marker: str, end_marker: str,
                 note: str) -> list[str]:
    """删除 [start, end) 之间的行并插入省略说明（用于超大的 20×20 矩阵打印）。"""
    s = next(i for i, l in enumerate(lines) if start_marker in l)
    e = next(i for i, l in enumerate(lines[s:], s) if end_marker in l)
    return lines[:s + 1] + [note] + lines[e:]


def main() -> None:
    lines = LOG.read_text(encoding="utf-8").splitlines()

    render(slice_between(lines, "===== 0", "===== 1"), OUT / "exp4_log_env.png")
    render(slice_between(lines, "===== 1", "===== 2"), OUT / "exp4_log_step1.png")
    render(slice_between(lines, "===== 2", "===== 3"), OUT / "exp4_log_step2.png")
    render(slice_between(lines, "===== 3", "===== 4"), OUT / "exp4_log_step3.png")
    render(slice_between(lines, "===== 4", "===== 基础任务A"), OUT / "exp4_log_step4.png")
    render(slice_between(lines, "===== 基础任务A", "===== 基础任务B"),
           OUT / "exp4_log_remove.png")
    render(slice_between(lines, "===== 基础任务B", "===== 进阶A"),
           OUT / "exp4_log_pair2.png")
    part20 = slice_between(lines, "===== 进阶A", "===== 进阶B")
    part20 = drop_between(part20, "混淆矩阵（20×20", "最易混淆",
                          "……（20×20 矩阵数值省略，完整数值见 confmat_20class.csv，热力图见图 11）……")
    render(part20, OUT / "exp4_log_20class.png", max_lines=60)
    render(slice_between(lines, "===== 进阶B", "===== 进阶C"), OUT / "exp4_log_vec.png")
    render(slice_between(lines, "===== 进阶C", "===== 实验汇总"), OUT / "exp4_log_lr.png")
    render(lines[next(i for i, l in enumerate(lines) if "实验汇总" in l):],
           OUT / "exp4_log_summary.png")


if __name__ == "__main__":
    main()
