# -*- coding: utf-8 -*-
"""实验五　生成式 AI 与大语言模型入门（DeepSeek 开放平台）

运行前在 PowerShell 中设置密钥（密钥不写进代码）：
    $env:DEEPSEEK_API_KEY = "你的密钥"
然后执行：python experiment5.py

流程：对同一条课程通知分别用 A（开放式）与 B（JSON 结构化）两种提示词各调用一次，
再按进阶任务要求删除截止时间后仅用 B 提示词调用第三次。脚本打印真实输出、
token 用量、JSON 可解析性与费用估算；密钥只从环境变量读取，不出现在任何输出里。
"""

import json
import os
import sys
from pathlib import Path

from openai import OpenAI

BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-flash"  # 讲义指定模型；若平台提示模型不存在，改为你账号可用的低价模型

OUT = Path("exp5_results")
OUT.mkdir(exist_ok=True)

# 价格（元 / 百万 token，高峰时段）。计价依据讲义 5.3 节示例：
# 两次合计 600 个未缓存输入 token + 400 个输出 token ≈ 0.0044 元
# => 输入 2 元/百万（未缓存）、输出 8 元/百万
PRICE_IN, PRICE_OUT = 2.0, 8.0


class Tee:
    """同时输出到终端与日志文件，保证截图与日志一致。"""

    def __init__(self, path: Path) -> None:
        self.file = open(path, "w", encoding="utf-8")

    def write(self, text: str) -> None:
        sys.__stdout__.write(text)
        self.file.write(text)

    def flush(self) -> None:
        sys.__stdout__.flush()
        self.file.flush()


def banner(title: str) -> None:
    print("\n===== " + title + " =====")


def usage_info(usage) -> dict:
    """从返回的 usage 对象里安全取出 token 计数字段。"""
    info = {
        "prompt": getattr(usage, "prompt_tokens", 0),
        "completion": getattr(usage, "completion_tokens", 0),
        "total": getattr(usage, "total_tokens", 0),
    }
    details = getattr(usage, "prompt_tokens_details", None)
    info["cached"] = getattr(details, "cached_tokens", 0) if details else 0
    return info


def run_call(name: str, prompt: str, notice_text: str) -> dict:
    """发送一次请求，按讲义步骤 2 的格式打印全部真实输出。"""
    result = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt + "\n通知：" + notice_text}],
        max_tokens=200,
        extra_body={"thinking": {"type": "disabled"}},
    )
    choice = result.choices[0]
    content = choice.message.content or ""
    print(f"\n{name} | {result.model} | {choice.finish_reason}")
    print(content)
    u = usage_info(result.usage)
    print(f"Token 用量：输入 {u['prompt']}（缓存命中 {u['cached']}），"
          f"输出 {u['completion']}，合计 {u['total']}")
    try:
        parsed = json.loads(content)
        print("能直接解析为 JSON 对象：", isinstance(parsed, dict))
    except json.JSONDecodeError:
        print("能直接解析为 JSON 对象：False")
        parsed = None
    cost = (u["prompt"] - u["cached"]) / 1e6 * PRICE_IN \
        + u["completion"] / 1e6 * PRICE_OUT
    print(f"本次估算费用：{cost:.6f} 元（高峰价：输入 {PRICE_IN} 元/百万、"
          f"输出 {PRICE_OUT} 元/百万）")
    if choice.finish_reason == "length":
        print("注意：finish_reason=length，输出被 max_tokens=200 截断")
    return {"model": result.model, "finish_reason": choice.finish_reason,
            "content": content, "usage": u, "parsed": parsed, "cost": cost}


def main() -> None:
    sys.stdout = Tee(OUT / "exp5_log.txt")

    # ---------- 步骤 1：配置 API 客户端 ----------
    banner("环境信息（密钥不打印）")
    import openai
    print("Python:", sys.version.split()[0])
    print("openai SDK:", openai.__version__)
    print("BASE_URL:", BASE_URL)
    print("请求模型:", MODEL)
    print("DEEPSEEK_API_KEY：已从环境变量读取（内容保密，不显示）")

    global client
    key = os.getenv("DEEPSEEK_API_KEY")
    if not key:
        raise SystemExit("请先设置 DEEPSEEK_API_KEY 环境变量")
    client = OpenAI(api_key=key, base_url=BASE_URL, timeout=30, max_retries=0)

    # ---------- 步骤 2：运行提示词对比 ----------
    notice = "机器学习实验周五18:00前提交实验报告到课程平台。"
    prompts = {
        "A": "提取这条通知的关键信息。",
        "B": (
            "只输出一个 JSON 对象，不加 Markdown。"
            "键为 course、deadline、deliverable、channel、contact。"
            "保留原文信息，缺失字段填 null，不得推测。"
        ),
    }

    results = {}
    for name, prompt in prompts.items():
        banner(f"{name} 组：{'开放式提示词' if name == 'A' else 'JSON 结构化提示词'}")
        results[name] = run_call(name, prompt, notice)

    # ---------- 进阶任务：删除截止时间，仅用 B 提示词再调用一次 ----------
    notice_adv = "机器学习实验请提交实验报告到课程平台。"  # 已删除“周五18:00前”
    banner("进阶任务：删除截止时间后仅用 B 提示词再调用一次")
    print("新通知：", notice_adv)
    results["ADV"] = run_call("ADV(B)", prompts["B"], notice_adv)

    # ---------- 步骤 3：核验结果并估算费用 ----------
    banner("字段核验与费用汇总")
    print("原文逐项核对（对照讲义步骤 3）：course=机器学习实验, deadline=周五18:00前,")
    print("deliverable=实验报告, channel=课程平台, contact=原文未提供（应为 null）")
    print()
    print("B 组实际 JSON：",
          json.dumps(results["B"]["parsed"], ensure_ascii=False)
          if results["B"]["parsed"] else "（未能解析）")
    print("进阶任务实际 JSON：",
          json.dumps(results["ADV"]["parsed"], ensure_ascii=False)
          if results["ADV"]["parsed"] else "（未能解析）")
    if results["ADV"]["parsed"]:
        p = results["ADV"]["parsed"]
        ok = p.get("deadline") is None and p.get("contact") is None
        print("进阶任务检查 deadline 与 contact 是否都为 null：",
              "是，均正确为 null" if ok else
              f"否（deadline={p.get('deadline')!r}, contact={p.get('contact')!r}）")
    total_in = sum(results[k]["usage"]["prompt"] for k in results)
    total_out = sum(results[k]["usage"]["completion"] for k in results)
    total_cost = sum(results[k]["cost"] for k in results)
    ab_cost = results["A"]["cost"] + results["B"]["cost"]
    print(f"\n基础任务 A+B 两次调用估算费用：{ab_cost:.6f} 元")
    print(f"三次调用合计：输入 {total_in} token，输出 {total_out} token，"
          f"估算总费用约 {total_cost:.4f} 元")
    print("（讲义示例：600 输入 + 400 输出 ≈ 0.0044 元，高峰价；实际以平台账单为准）")


if __name__ == "__main__":
    main()
