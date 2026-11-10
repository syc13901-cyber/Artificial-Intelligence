# -*- coding: utf-8 -*-
"""生成《第5次实验报告.docx》：白纸黑字、默认字体、无页眉页脚页码，
表格全部网格且无填充颜色。所有数值来自 exp5_results/exp5_log.txt 的真实运行结果。
"""

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

doc = Document()


def title(text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.bold = True


def centered(text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run(text)


def heading(text: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(text)
    r.bold = True


def sub_heading(text: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(text)
    r.bold = True


def body(text: str, bold_prefix: str = "") -> None:
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Pt(22)
    if bold_prefix:
        r = p.add_run(bold_prefix)
        r.bold = True
    p.add_run(text)


def q_title(text: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Pt(22)
    r = p.add_run(text)
    r.bold = True


def make_table(headers: list[str], rows: list[list[str]],
               widths: list[int] | None = None) -> None:
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"  # 全部网格边框，无填充颜色
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(headers):
        cell = table.rows[0].cells[j]
        cell.text = ""
        r = cell.paragraphs[0].add_run(h)
        r.bold = True
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            cell = table.rows[i].cells[j]
            cell.text = ""
            cell.paragraphs[0].add_run(val)
            if j > 0:
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if widths:
        for j, w in enumerate(widths):
            for row in table.rows:
                row.cells[j].width = Pt(w)
    doc.add_paragraph()


# ================= 标题区 =================
title("实验五　生成式 AI 与大语言模型入门实验报告")
centered("姓名：陈思妍　　学号：2023141420127")
centered("2026 年 11 月 10 日")

# ================= 一、实验概述 =================
heading("一、实验概述")
body("本实验使用 Python 调用 DeepSeek 开放平台的大语言模型 API，对同一条虚构课程通知"
     "（“机器学习实验周五18:00前提交实验报告到课程平台。”）分别用 A（开放式）与 B（JSON "
     "结构化）两种提示词各发起一次真实调用，比较输出的格式稳定性；再用 Python 的 json.loads "
     "检查输出能否直接解析为 JSON 对象，并对照原文逐项核验字段内容；记录每次调用的输入、输出 "
     "token 用量，按讲义给出的高峰价估算费用。此外完成了进阶任务：删除通知中的截止时间后，"
     "仅用 B 提示词再调用一次，检查 deadline 与 contact 是否都正确为 null。")
body("环境与配置：Windows 11（64 位）、Python 3.13.14、openai SDK 3.49.0；BASE_URL 为 "
     "https://api.deepseek.com，请求模型为 deepseek-flash，三次调用 finish_reason 均为 stop。"
     "密钥按讲义要求保存在环境变量 DEEPSEEK_API_KEY 中，代码里只通过 os.getenv 读取，"
     "不写入代码、报告或输出，打印与截图中均不含密钥。")
body("复现方法：设置环境变量后运行 python experiment5.py 即可一键完成三次调用，"
     "自动打印真实输出、token 用量、JSON 解析结果与费用估算。提交的两张真实输出截图"
     "（A 组、B 组）与进阶任务截图均来自本次实际运行。")

# ================= 二、结果记录 =================
heading("二、结果记录")
body("按讲义 5.6 节要求，将实测结果填入记录表（表 1）：")
make_table(
    ["记录项", "实测结果"],
    [
        ["服务与实际模型名",
         "DeepSeek 开放平台（BASE_URL：https://api.deepseek.com）；实际返回模型 "
         "deepseek-flash，三次调用 finish_reason 均为 stop"],
        ["A 组输出及 JSON 解析结果",
         "输出三条要点：“事项：提交机器学习实验报告”“截止时间：周五18:00前”"
         "“提交方式/地点：课程平台”；json.loads 抛出 JSONDecodeError，"
         "能直接解析为 JSON 对象：False"],
        ["B 组输出及 JSON 解析结果",
         "{\"course\":\"机器学习实验\",\"deadline\":\"周五18:00前\","
         "\"deliverable\":\"实验报告\",\"channel\":\"课程平台\",\"contact\":null}；"
         "能直接解析为 JSON 对象：True"],
        ["字段核验与两组差异",
         "B 组五个字段与原文逐项一致，contact 正确填 null（见表 2）；"
         "A 组信息内容也正确且未编造联系人，但字段名不稳定"
         "（把 channel 写成“提交方式/地点”）且无固定结构，需要额外解析"],
        ["A、B 各自的输入和输出 token 数",
         "A 组：输入 26、输出 29；B 组：输入 58、输出 31"
         "（B 的提示词更长所以输入多；两组输出相近）"],
        ["估算费用与计价依据",
         "计价依据讲义示例（两次合计 600 个未缓存输入 token + 400 个输出 token ≈ 0.0044 元，"
         "高峰价），即输入 2 元/百万 token、输出 8 元/百万 token。"
         "A 组 0.000284 元、B 组 0.000364 元，A+B 合计 0.000648 元；"
         "加进阶任务三次合计约 0.0010 元。实际费用以平台账单为准"],
    ],
    widths=[130, 330],
)

# ================= 三、结果分析 =================
heading("三、结果分析")
sub_heading("（一）A、B 两组输出对比与 JSON 可解析性")
body("A 组开放式提示词返回的是自由格式的中文要点列表：", )
make_table(
    ["", "A 组（开放式）", "B 组（JSON 结构化）"],
    [
        ["输出格式", "三条“字段名：值”要点，字段名由模型自定",
         "一个 JSON 对象，键名由提示词预先规定"],
        ["能直接 json.loads", "False（不是合法 JSON 文本）", "True（一次解析即得字典）"],
        ["字段完整性", "覆盖了事项、截止时间、提交渠道，但没有输出 contact 为空这一信息",
         "五个键齐全，缺失字段显式为 null"],
        ["输入 / 输出 token", "26 / 29", "58 / 31"],
        ["finish_reason", "stop", "stop"],
    ],
    widths=[100, 180, 180],
)
body("差异的根源在提示词：A 组只说“提取关键信息”，输出结构完全由模型自由发挥；B 组明确要求"
     "“只输出一个 JSON 对象，不加 Markdown”，并规定键名集合与“缺失字段填 null，不得推测”，"
     "因此输出恰好是可解析、键名固定的 JSON。两组输出均未被 max_tokens=200 截断"
     "（finish_reason 均为 stop）。")
sub_heading("（二）字段核验")
body("把 B 组 JSON 的每个字段与原文逐项对照（表 2），五个字段全部正确：")
make_table(
    ["字段", "原文信息", "B 组取值", "核验结果"],
    [
        ["course", "机器学习实验", "机器学习实验", "正确"],
        ["deadline", "周五18:00前", "周五18:00前", "正确"],
        ["deliverable", "实验报告", "实验报告", "正确"],
        ["channel", "课程平台", "课程平台", "正确"],
        ["contact", "原文未提供", "null", "正确（未编造）"],
    ],
    widths=[80, 120, 120, 120],
)
sub_heading("（三）token 用量与费用估算")
make_table(
    ["调用", "输入 token", "输出 token", "finish_reason", "估算费用（元）"],
    [
        ["A 组", "26", "29", "stop", "0.000284"],
        ["B 组", "58", "31", "stop", "0.000364"],
        ["进阶任务（B）", "54", "27", "stop", "0.000324"],
        ["合计", "138", "87", "—", "约 0.0010"],
    ],
    widths=[110, 90, 90, 100, 110],
)
body("计价依据：讲义示例“两次合计 600 个未缓存输入 token 和 400 个输出 token 约为 0.0044 元”"
     "对应 DeepSeek Flash 高峰价输入 2 元/百万 token（未缓存）、输出 8 元/百万 token。"
     "本实验 A+B 两次基础调用合计 0.000648 元，加进阶任务第三次调用共约 0.0010 元，"
     "成本可忽略不计；实际费用以平台账单为准。")
sub_heading("（四）哪种提示词更便于程序处理")
body("B 组明显更便于程序处理，理由有三：一是输出格式确定，json.loads 一次即可得到字典，"
     "不需要再写针对自然语言的解析规则；二是键名由提示词固定（course、deadline、deliverable、"
     "channel、contact），下游代码可以按名取值，而 A 组的字段名是模型自拟的"
     "（如“提交方式/地点”），每次调用都可能不同；三是缺失信息有明确的语义——B 组把原文没有的 "
     "contact 显式输出为 null，程序可以直接判空，而 A 组“没提到联系人”只能靠人阅读确认。"
     "代价是 B 的提示词更长，输入 token 是 A 的 2.2 倍（58 对 26），但输出长度相近，"
     "总费用差异不足 0.0001 元，用少量 token 换取稳定的机器可读结构是值得的。")

# ================= 四、进阶任务 =================
heading("四、进阶任务：删除截止时间后的鲁棒性检查")
body("把通知改为“机器学习实验请提交实验报告到课程平台。”（删除“周五18:00前”），"
     "仅用 B 提示词再调用一次，返回：{\"course\":\"机器学习实验\",\"deadline\":null,"
     "\"deliverable\":\"实验报告\",\"channel\":\"课程平台\",\"contact\":null}，"
     "能直接解析为 JSON 对象：True。检查结果：deadline 与 contact 都正确为 null，"
     "其余三个字段仍与原文一致。")
body("说明提示词中“缺失字段填 null，不得推测”的约束有效：原文删掉截止时间后，"
     "模型没有臆造出“周五”之类的默认值，而是如实输出 null。对程序而言，null 与猜测值"
     "的区别是可检测的，这正是结构化输出优于自由文本的地方。")

# ================= 五、思考题回答 =================
heading("五、思考题回答")
q_title("（1）JSON 可以解析，为什么还要检查字段内容？")
body("json.loads 只验证语法和数据类型，不验证内容是否符合事实。即使解析成功，模型仍可能"
     "遗漏字段、误读截止时间（例如把“周五18:00前”理解成“周五18:00”），甚至补出原文没有的"
     "联系人。结合本实验实测：B 组五个字段与原文逐项一致，但这依赖提示词中“不得推测”的约束——"
     "进阶任务里若去掉该约束，模型可能把已删除的截止时间补成猜测值；语法上它依然是合法 JSON，"
     "解析器不会报任何错，只有对照原文核验才能发现。所以“解析通过”只是及格线，"
     "字段级核验才是保证数据可用的最后一道关。")
q_title("（2）如何控制本实验的 API 费用？")
body("本实验用了四种手段：一是输入尽量短，通知原文只有一句话，加上提示词每次输入也只有 "
     "26～58 个 token；二是限制生成长度，max_tokens=200 把输出上限封顶（实测三组输出都只有 "
     "27～31 个 token，未触发截断）；三是控制调用次数，基础任务只调用两次，进阶任务加一次，"
     "共三次；四是用返回的 usage 核对估算，三次合计输入 138、输出 87 个 token，"
     "按高峰价估算总费用约 0.0010 元。此外还可以选用低价模型、利用输入缓存命中"
     "（本次三组缓存命中均为 0，因为输入各不相同）以及在非高峰时段调用进一步降低费用。")

doc.save("第5次实验报告.docx")
print("written 第5次实验报告.docx")
