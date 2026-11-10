# 人工智能课程实验

本仓库收录《人工智能》课程的 5 次实验作业，按完成时间顺序排列。仓库只包含**实验代码与运行结果**，不含提交给课程的实验报告文档。

| 实验 | 主题 | 关键技术 | 关键结果 | 完成日期 |
|------|------|----------|----------|----------|
| [实验 1](exp1/) | NumPy 与 PIL 图像处理基础 | 数组操作、广播、向量化；灰度/翻转/盒模糊 | — | 2026-09-26 |
| [实验 2](exp2/) | Iris 数据集分类 | KNN、决策树、5 折交叉验证 | KNN k=5 准确率 0.9778 | 2026-10-03 |
| [实验 3](exp3/) | CNN 图像分类 | PyTorch CNN、数据增强、超参对比 | CIFAR-10 测试集 62.15%（10 epoch） | 2026-10-21 |
| [实验 4](exp4/) | 文本分类与朴素贝叶斯 | TF-IDF + MultinomialNB Pipeline | 4 类 87.52% / 20 类 67.79% | 2026-10-28 |
| [实验 5](exp5/) | 大模型 API 与提示词工程 | DeepSeek API、开放式 vs 结构化 JSON 提示词 | B 组五字段全对，三次调用约 0.0010 元 | 2026-11-10 |

## 目录结构

```
├── exp1/    第一次实验：NumPy 与 PIL 图像处理基础
├── exp2/    第二次实验：Iris 的 KNN 与决策树分类
├── exp3/    第三次实验：CNN 图像分类（CIFAR-10）
├── exp4/    第四次实验：20 Newsgroups 文本分类（朴素贝叶斯）
├── exp5/    第五次实验：DeepSeek API 提示词对比
├── tools/   辅助脚本（实验报告与日志截图的生成管线，报告本身不入库）
└── expN/expN_results/  各实验的运行日志、数值汇总与图表
```

## 环境要求

- Python 3.10+
- 依赖按实验不同：`numpy`、`matplotlib`、`pillow`（exp1）；`scikit-learn`（exp2/exp4）；`torch` + `torchvision`（exp3）；`openai` SDK（exp5）
- 数据集（Iris、CIFAR-10、20 Newsgroups）均由脚本自动下载，无需手动准备

## 运行方式

```bash
# 实验 1（需同目录下有素材图 illit_concept_26(1).jpg）
cd exp1 && python exp1.py

# 实验 2（结果自动输出到 exp2_results/）
cd exp2 && python exp2.py

# 实验 3（CIFAR-10 自动下载到 ./data，可用 --data-root 指定已有目录）
cd exp3 && python exp3.py

# 实验 4（20 Newsgroups 首次运行自动下载）
cd exp4 && python exp4.py

# 实验 5（密钥只从环境变量读取，不写入代码）
cd exp5
$env:DEEPSEEK_API_KEY = "你的密钥"
python experiment5.py
```

## 说明

- 各实验的实测数值（准确率、token 用量等）见对应 `expN_results/` 下的 CSV/JSON/日志文件，README 中的数字均取自这些文件。
- 实验 3 的训练好的模型权重（`exp3_net.pth`、`exp3_net_final.pth`）随仓库保留，可直接加载复现评估。
- `tools/` 中的脚本用于生成提交给课程的 docx 报告和日志截图，属于个人作业管线，仅供了解结果图是如何生成的。
