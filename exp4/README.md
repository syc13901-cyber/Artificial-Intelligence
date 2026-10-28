# 实验 4：文本分类与朴素贝叶斯（20 Newsgroups，第四次实验，2026-10-28）

## 实验内容

用 scikit-learn 官方接口获取真实文本数据集 20 Newsgroups，搭建"词袋/TF-IDF 特征化 + 分类器"的 Pipeline：

1. 4 类子集（baseball / space / graphics / politics.misc）训练 TF-IDF + MultinomialNB；
2. 2 类子集（sci.electronics / sci.med）二分类；
3. 全部 20 类的多分类；
4. **信息泄漏对比**：不去除 headers/footers/quotes 时的准确率虚高现象（原数据的 Newsgroups 头已被官方预处理移除，泄漏分析按 Subject 与引文展开）；
5. 20 类上与 LogisticRegression 对比；
6. 混淆矩阵热力图与最易混淆类别对分析。

## 关键结果

| 实验 | 测试准确率 |
|------|-----------|
| 4 类（去头） | **87.52%** |
| 4 类（未去头，含泄漏） | 94.23% |
| 2 类 | 91.76% |
| 20 类（朴素贝叶斯） | 67.79% |
| 20 类（LogisticRegression） | 69.09% |

## 运行

```bash
python exp4.py
```

首次运行自动下载 20 Newsgroups 数据集；完整日志、分类报告、混淆矩阵 CSV、汇总（summary.csv/json）与全部图表输出到 `exp4_results/`。

## 依赖

scikit-learn、matplotlib

## 文件说明

| 文件 | 说明 |
|------|------|
| `exp4.py` | 实验源码（一键复现全部实验并重新生成结果） |
| `exp4_results/exp4_confmat_*.png` | 4 类 / 2 类 / 20 类混淆矩阵热力图 |
| `exp4_results/exp4_log_*.png` | 运行日志的控制台风格截图 |
