# 实验 5：生成式 AI 与大模型 API 入门（DeepSeek，第五次实验，2026-11-10）

## 实验内容

用 Python 调用 DeepSeek 开放平台（`deepseek-flash` 模型），对同一条课程通知设计两种提示词并对比：

1. **A 组（开放式提示词）**：自由作答，输出自然语言；
2. **B 组（结构化提示词）**：要求输出严格 JSON（course / deadline / deliverable / channel / contact 五个字段）；
3. 用 `json.loads` 检查 JSON 可解析性，并对照原文核验每个字段；
4. 记录输入/输出 token 用量并按讲义高峰价（输入 2 元/百万、输出 8 元/百万）估算费用；
5. **进阶任务**：从通知中删除截止时间后再用 B 提示词调用，检查 deadline 与 contact 是否正确输出为 `null`。

## 关键结果（摘自 `exp5_results/exp5_log.txt`）

| 调用 | 输入/输出 token | JSON 可解析 | 核验 |
|------|----------------|-------------|------|
| A 组开放式 | 26 / 29 | 否（自然语言） | 信息正确但非结构化 |
| B 组严格 JSON | 58 / 31 | 是 | 五字段全对，contact=null |
| 进阶（删截止时间） | 54 / 27 | 是 | deadline 与 contact 均正确为 null |
| 合计 | 138 / 87 | — | 估算费用约 **0.0010 元** |

结论：结构化提示词是让大模型输出可被程序稳定消费的关键；删除信息后模型能按指令正确返回 null 而不是编造。

## 运行

密钥按讲义要求保存在环境变量中，**代码与输出中均不含密钥**：

```powershell
$env:DEEPSEEK_API_KEY = "你的密钥"
python experiment5.py
```

依赖：openai SDK（`python -m pip install openai`）

## 文件说明

| 文件 | 说明 |
|------|------|
| `experiment5.py` | 实验源码（一键复现三次调用与全部检查） |
| `exp5_results/exp5_log.txt` | 完整运行日志 |
| `exp5_results/exp5_group_a/b/adv.png` | 三次调用的控制台风格截图 |
