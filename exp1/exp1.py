import numpy as np

a = np.array([[1, 2, 3], [4, 5, 6]])
print("a =\n", a)
print("shape:", a.shape)
print("dtype:", a.dtype)
print("ndim:", a.ndim)

b = np.arange(0, 12)
c = np.linspace(0, 1, 5)
d = np.zeros((3, 4))
e = np.ones((2, 2), dtype=int)
rng = np.random.default_rng(42)
f = rng.random((2, 3))

print("b =", b)
print("c =", c)
print("d =\n", d)
print("e =\n", e)
print("f =\n", f)

g = np.arange(12).reshape(3, 4)
print("g =\n", g)
print("first row:", g[0])
print("last column:", g[:, -1])
print("top-left 2x2:\n", g[:2, :2])
print("every other row:\n", g[::2])

print("transpose:\n", g.T)
h = g.reshape(2, 6)
print("reshape(2, 6):\n", h)

A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])
 
print("逐元素相乘:\n", A * B)    # 对应位置相乘
print("矩阵乘法:\n", A @ B)      # 真正的矩阵乘法
 
v = np.array([10, 20])
print("广播加法:\n", A + v)      # v 被“广播”到 A 的每一行

import time
 
n = 1_000_000
x = rng.random(n)
y = rng.random(n)
 
# 方式一：Python 循环
t0 = time.perf_counter()
s1 = 0.0
for i in range(n):
    s1 += x[i] * y[i]
t1 = time.perf_counter()
 
# 方式二：NumPy 向量化
t2 = time.perf_counter()
s2 = np.dot(x, y)
t3 = time.perf_counter()
 
print("循环结果  :", s1, "耗时(秒):", round(t1 - t0, 4))
print("向量结果  :", s2, "耗时(秒):", round(t3 - t2, 4))
print("两种结果是否接近:", np.isclose(s1, s2))

import matplotlib.pyplot as plt
 
# 生成 256x256 的渐变灰度图
h_, w_ = 256, 256
xx = np.linspace(0, 255, w_)
gray = np.tile(xx, (h_, 1)).astype(np.uint8)   # 每行都是 0->255 的渐变
print("灰度图 shape:", gray.shape, "dtype:", gray.dtype)
 
# 构造彩色图：三个通道分别为渐变、反渐变、常数
img = np.zeros((h_, w_, 3), dtype=np.uint8)
img[:, :, 0] = gray                    # R 通道
img[:, :, 1] = gray[:, ::-1]           # G 通道（水平翻转）
img[:, :, 2] = 128                     # B 通道
 
fig, axes = plt.subplots(1, 2, figsize=(8, 4))
axes[0].imshow(gray, cmap="gray"); axes[0].set_title("gray")
axes[1].imshow(img);                   axes[1].set_title("rgb")
for ax in axes: ax.axis("off")
plt.tight_layout()
plt.savefig("exp1_gradient.png", dpi=120)
print("已保存 exp1_gradient.png")

# 加权平均灰度化（常用系数）
rgb = img.astype(np.float64)
gray2 = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
gray2 = gray2.astype(np.uint8)
print("转换后 shape:", gray2.shape)
 
flip_lr = img[:, ::-1, :]   # 左右翻转
flip_ud = img[::-1, :, :]   # 上下翻转
 
fig, axes = plt.subplots(1, 3, figsize=(10, 3.5))
axes[0].imshow(img);      axes[0].set_title("original")
axes[1].imshow(flip_lr);  axes[1].set_title("flip left-right")
axes[2].imshow(flip_ud);  axes[2].set_title("flip up-down")
for ax in axes: ax.axis("off")
plt.tight_layout()
plt.savefig("exp1_flip.png", dpi=120)
print("已保存 exp1_flip.png")

# task 1: indexing and slicing
arr_4x5 = np.arange(1, 21).reshape(4, 5)
print("4x5 array:\n", arr_4x5)
print("second row:", arr_4x5[1, :])
print("last two columns:\n", arr_4x5[:, -2:])
print("center 2x2 block:\n", arr_4x5[1:3, 1:3])

# task 2: elementwise multiplication vs matrix multiplication
A_23 = np.array([[1, 2, 3],
                 [4, 5, 6]])
B_32 = np.array([[1, 2],
                 [3, 4],
                 [5, 6]])

print("A shape:", A_23.shape)
print("B shape:", B_32.shape)

try:
    print("A * B:\n", A_23 * B_32)
except ValueError as exc:
    print("A * B error:", exc)

C = A_23 @ B_32
print("A @ B:\n", C)
print("A @ B shape:", C.shape)

# optional Task 2: load a real image, convert to grayscale, and flip left-right
from pathlib import Path
from PIL import Image

work_dir = Path(__file__).resolve().parent
photo_path = work_dir / "illit_concept_26(1).jpg"

with Image.open(photo_path) as photo:
    photo_rgb = np.array(photo.convert("RGB"))

photo_float = photo_rgb.astype(np.float32)
photo_gray = np.rint(
    0.299 * photo_float[:, :, 0]
    + 0.587 * photo_float[:, :, 1]
    + 0.114 * photo_float[:, :, 2]
).astype(np.uint8)

photo_flip = np.fliplr(photo_rgb).copy()

Image.fromarray(photo_gray).save(work_dir / "exp1_photo_gray.png")
Image.fromarray(photo_flip).save(work_dir / "exp1_photo_flip.png")

print("photo shape:", photo_rgb.shape)
print("grayscale shape:", photo_gray.shape, "dtype:", photo_gray.dtype)
print("saved exp1_photo_gray.png and exp1_photo_flip.png")


# optional Task 1: 3x3 mean filter using shifted slices
height, width = photo_gray.shape
padded = np.pad(photo_gray.astype(np.float32), 1, mode="edge")

blur_sum = (
    padded[0:height,     0:width]
    + padded[0:height,   1:width + 1]
    + padded[0:height,   2:width + 2]
    + padded[1:height+1, 0:width]
    + padded[1:height+1, 1:width + 1]
    + padded[1:height+1, 2:width + 2]
    + padded[2:height+2, 0:width]
    + padded[2:height+2, 1:width + 1]
    + padded[2:height+2, 2:width + 2]
)

photo_blur = np.rint(blur_sum / 9).astype(np.uint8)
Image.fromarray(photo_blur).save(work_dir / "exp1_photo_blur.png")

print("blurred shape:", photo_blur.shape, "dtype:", photo_blur.dtype)
print("saved exp1_photo_blur.png")


# optional Task 3: np.argmax example
values = np.array([12, 7, 25, 18])
max_index = np.argmax(values)

print("values:", values)
print("index of maximum:", max_index)
print("maximum value:", values[max_index])