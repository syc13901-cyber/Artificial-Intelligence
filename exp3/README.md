# 实验 3：CNN 图像分类（CIFAR-10，第三次实验，2026-10-21）

## 实验内容

用 PyTorch 在 CIFAR-10（5 万训练图 / 1 万测试图）上搭建 CNN 并系统对比：

1. 数据加载、CNN 定义与训练循环、测试集评估（基础任务）；
2. 进阶对比实验：
   - batch size：32 / 64 / 128；
   - 学习率：0.0001 / 0.001 / 0.01；
   - 数据增强（随机水平翻转 + RandomCrop）有无对比；
   - 更深的网络 `NetDeep`（156,074 参数 vs `Net` 62,006 参数）；
   - final 组合：lr=0.01 + 10 epoch。

## 关键结果（摘自 `exp3_results/summary.csv`）

| 组名 | 配置 | 测试准确率 |
|------|------|-----------|
| baseline | lr=0.001, bs=64, 2 epoch | 31.24% |
| bs32 / bs128 | 仅改 batch size | 41.52% / 17.23% |
| lr0.01 | 仅改学习率 | **53.05%** |
| lr0.0001 | 仅改学习率 | 11.34% |
| augment | 加数据增强（2 epoch） | 29.32% |
| deep | 更深网络 | 34.42% |
| **final** | lr=0.01 + 增强 + 10 epoch | **62.15%** |
| final_noaug | lr=0.01 + 10 epoch | 63.52% |

结论：学习率影响最大；短训练下数据增强反而拖慢收敛，训练充分后才能体现其收益。

## 运行

```bash
python exp3.py            # CIFAR-10 自动下载到 ./data
python exp3.py --data-root ../data   # 使用已有数据目录
```

完整日志、混淆矩阵、逐类准确率、loss 曲线输出到 `exp3_results/`。

## 依赖

torch、torchvision、matplotlib

## 文件说明

| 文件 | 说明 |
|------|------|
| `exp3.py` | 实验源码（一键复现） |
| `exp3_net.pth` / `exp3_net_final.pth` | baseline / final 训练得到的模型权重 |
| `exp3_results/summary.csv` | 全部对比组的数值汇总 |
| `exp3_results/exp3_log*.png` | 运行日志的控制台风格截图 |
| `exp3_results/loss_curves.png` 等 | loss 曲线、混淆矩阵、逐类准确率图表 |
