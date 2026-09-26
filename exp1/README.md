# 实验 1：NumPy 与 PIL 图像处理基础（第一次实验，2026-09-26）

## 实验内容

`exp1.py` 一键完成三部分：

1. **NumPy 数组基础**：数组创建（`array`/`arange`/`linspace`/`zeros`/`ones`/随机）、`shape`/`dtype`/`ndim` 属性、切片与索引、转置与 `reshape`、逐元素乘法与矩阵乘法（`*` vs `@`）、广播机制，以及 100 万元素级运算的向量化 vs 纯 Python 循环耗时对比。
2. **Matplotlib 可视化**：用 `meshgrid` 生成水平渐变图并保存为 `exp1_gradient.png`；对渐变图做上下翻转得到 `exp1_flip.png`。
3. **PIL 图像处理**：读取素材照片 `illit_concept_26(1).jpg`，分别实现并保存：
   - 灰度化（亮度加权公式）→ `exp1_photo_gray.png`
   - 上下翻转 → `exp1_photo_flip.png`
   - 3×3 盒模糊（滑窗均值卷积）→ `exp1_photo_blur.png`

## 运行

```bash
python exp1.py
```

需要同目录下存在素材图 `illit_concept_26(1).jpg`；输出图片直接生成在当前目录。

## 依赖

numpy、matplotlib、pillow

## 文件说明

| 文件 | 说明 |
|------|------|
| `exp1.py` | 实验源码（一键复现） |
| `illit_concept_26(1).jpg` | 图像处理素材（原图） |
| `exp1_gradient.png` / `exp1_flip.png` | 渐变图及其翻转 |
| `exp1_photo_gray.png` / `exp1_photo_flip.png` / `exp1_photo_blur.png` | 照片的灰度化 / 翻转 / 模糊结果 |
