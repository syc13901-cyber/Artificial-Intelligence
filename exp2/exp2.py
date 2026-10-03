from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier


OUTPUT_DIR = Path(__file__).resolve().parent / "exp2_results"
OUTPUT_DIR.mkdir(exist_ok=True)

iris = load_iris()
X, y = iris.data, iris.target

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42,stratify=y 
)
print("训练集:", X_train.shape, "测试集:", X_test.shape)

print("\n一、KNN 基础 k 值对比")
for k in [1, 3, 5, 7, 9, 11]:
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X_train, y_train)
    acc = accuracy_score(y_test, knn.predict(X_test))
    print(f"k={k:2d}  测试集准确率: {acc:.4f}")

print("\n二、决策树深度对比")
for depth in [1, 2, 3, 5, None]:
    tree = DecisionTreeClassifier(max_depth=depth, random_state=42)
    tree.fit(X_train, y_train)
    train_acc = accuracy_score(y_train, tree.predict(X_train))
    test_acc = accuracy_score(y_test, tree.predict(X_test))
    print(f"max_depth={str(depth):4s}  训练集: {train_acc:.4f}  测试集: {test_acc:.4f}")

best_knn = KNeighborsClassifier(n_neighbors=5)
best_knn.fit(X_train, y_train)
y_pred = best_knn.predict(X_test)
print("\n混淆矩阵:\n", confusion_matrix(y_test, y_pred))
print("\n分类报告:\n", classification_report(y_test, y_pred, target_names=iris.target_names))

# 扩展实验 1：StandardScaler + Pipeline 与未标准化 KNN 对比。
print("\n三、特征标准化对比")
scaling_rows = ["k,未标准化准确率,标准化准确率"]
for k in [1, 3, 5, 7, 9, 11]:
    plain_knn = KNeighborsClassifier(n_neighbors=k)
    scaled_knn = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("knn", KNeighborsClassifier(n_neighbors=k)),
        ]
    )
    plain_knn.fit(X_train, y_train)
    scaled_knn.fit(X_train, y_train)
    plain_acc = accuracy_score(y_test, plain_knn.predict(X_test))
    scaled_acc = accuracy_score(y_test, scaled_knn.predict(X_test))
    print(f"k={k:2d}  未标准化: {plain_acc:.4f}  标准化: {scaled_acc:.4f}")
    scaling_rows.append(f"{k},{plain_acc:.6f},{scaled_acc:.6f}")
(OUTPUT_DIR / "scaling_comparison.csv").write_text("\n".join(scaling_rows), encoding="utf-8")

# 扩展实验 2：5 折交叉验证，与单次划分结果进行比较。
print("\n四、5 折交叉验证")
cv_rows = ["k,单次划分准确率,5折平均准确率,5折标准差"]
for k in [1, 3, 5, 7, 9, 11]:
    single_model = KNeighborsClassifier(n_neighbors=k).fit(X_train, y_train)
    single_acc = accuracy_score(y_test, single_model.predict(X_test))
    cv_scores = cross_val_score(KNeighborsClassifier(n_neighbors=k), X, y, cv=5)
    print(
        f"k={k:2d}  单次划分: {single_acc:.4f}  "
        f"5折平均: {cv_scores.mean():.4f}  标准差: {cv_scores.std():.4f}"
    )
    cv_rows.append(f"{k},{single_acc:.6f},{cv_scores.mean():.6f},{cv_scores.std():.6f}")
(OUTPUT_DIR / "cross_validation_comparison.csv").write_text("\n".join(cv_rows), encoding="utf-8")

# 扩展实验 3：仅使用前两个特征绘制不同 k 的 KNN 决策边界。
print("\n五、决策边界图")
X_two = X[:, :2]
x_min, x_max = X_two[:, 0].min() - 0.5, X_two[:, 0].max() + 0.5
y_min, y_max = X_two[:, 1].min() - 0.5, X_two[:, 1].max() + 0.5
xx, yy = np.meshgrid(
    np.linspace(x_min, x_max, 400),
    np.linspace(y_min, y_max, 400),
)

fig, axes = plt.subplots(1, 3, figsize=(16, 4.8), constrained_layout=True)
for ax, k in zip(axes, [1, 5, 11]):
    boundary_knn = KNeighborsClassifier(n_neighbors=k).fit(X_two, y)
    grid_pred = boundary_knn.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
    ax.contourf(xx, yy, grid_pred, alpha=0.25, cmap="viridis")
    for class_id, class_name in enumerate(iris.target_names):
        mask = y == class_id
        ax.scatter(
            X_two[mask, 0],
            X_two[mask, 1],
            label=class_name,
            edgecolor="black",
            linewidth=0.35,
        )
    ax.set_title(f"KNN decision boundary (k={k})")
    ax.set_xlabel(iris.feature_names[0])
    ax.set_ylabel(iris.feature_names[1])
    ax.legend(fontsize=8)

plot_path = OUTPUT_DIR / "knn_decision_boundaries_k1_k5_k11.png"
fig.savefig(plot_path, dpi=160)
plt.close(fig)
print(f"决策边界图已保存：{plot_path}")
