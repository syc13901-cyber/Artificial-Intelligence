# -*- coding: utf-8 -*-
"""实验四　文本分类与朴素贝叶斯（20 Newsgroups）

一键运行：python exp4.py
全部结果输出到 exp4_results/ 目录：
  - exp4_log.txt                    完整运行日志（截图由此渲染）
  - classification_report_*.txt     分类报告文本
  - confmat_*.csv                   混淆矩阵数值表
  - exp4_confmat_*.png              混淆矩阵热力图（4 类 / 2 类 / 20 类）
  - exp4_exp_accuracy.png           各实验测试准确率对比图
  - exp4_top_confusions.png         20 类最易混淆类别对 Top10
  - summary.csv / summary.json      实验汇总（数值供报告引用）
"""

import json
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix)
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

OUT = Path("exp4_results")
OUT.mkdir(exist_ok=True)
REMOVE = ("headers", "footers", "quotes")
CATS4 = ["rec.sport.baseball", "sci.space", "comp.graphics", "talk.politics.misc"]
CATS2 = ["sci.electronics", "sci.med"]

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False


class Tee:
    """同时输出到终端与日志文件，保证报告截图与日志一致。"""

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


def new_nb(**vec_kwargs) -> Pipeline:
    """讲义标准流程：TfidfVectorizer + MultinomialNB 串成 Pipeline。"""
    return Pipeline([
        ("tfidf", TfidfVectorizer(stop_words="english", **vec_kwargs)),
        ("clf", MultinomialNB()),
    ])


def fit_eval(name: str, model: Pipeline, train, test) -> dict:
    """训练并评估，返回准确率、训练耗时、混淆矩阵等关键指标。"""
    t0 = time.perf_counter()
    model.fit(train.data, train.target)
    fit_time = time.perf_counter() - t0
    pred = model.predict(test.data)
    acc = accuracy_score(test.target, pred)
    n_feat = len(model.named_steps["tfidf"].vocabulary_)
    print(f"[{name}] 训练耗时 {fit_time:.2f}s，特征维度 {n_feat}，测试准确率 {acc:.4f}")
    return {"name": name, "model": model, "pred": pred, "acc": acc,
            "fit_time": fit_time, "n_features": n_feat}


def f1_extremes(test, pred, names: list[str]) -> tuple[dict, dict]:
    """返回分类报告中 F1 最低与最高的类别。"""
    rep = classification_report(test.target, pred, target_names=names,
                                output_dict=True, zero_division=0)
    f1 = {n: rep[n]["f1-score"] for n in names}
    lo = min(f1, key=f1.get)
    hi = max(f1, key=f1.get)
    return ({"cls": lo, "f1": f1[lo]}, {"cls": hi, "f1": f1[hi]})


def top_confusion(cm: np.ndarray, names: list[str], k: int = 10) -> list[dict]:
    """把混淆矩阵对角线清零后取混淆次数最多的 k 个类别对。"""
    off = cm.copy().astype(int)
    np.fill_diagonal(off, 0)
    idx = np.dstack(np.unravel_index(np.argsort(off, axis=None)[::-1], off.shape))[0]
    return [{"true": names[i], "pred": names[j], "count": int(off[i, j])}
            for i, j in idx[:k] if off[i, j] > 0]


def save_confmat_csv(cm: np.ndarray, names: list[str], path: Path) -> None:
    with open(path, "w", encoding="utf-8-sig") as f:
        f.write("," + ",".join(names) + "\n")
        for n, row in zip(names, cm):
            f.write(n + "," + ",".join(str(v) for v in row) + "\n")


def plot_confmat(cm: np.ndarray, names: list[str], path: Path, title: str) -> None:
    n = len(names)
    size = 7 if n <= 4 else (6 if n == 2 else 11.5)
    fig, ax = plt.subplots(figsize=(size, size * 0.82))
    im = ax.imshow(cm, cmap="Blues")
    fig.colorbar(im, ax=ax, fraction=0.046)
    ax.set_xticks(range(n), names, rotation=45 if n > 2 else 0, ha="right",
                  fontsize=8 if n > 4 else 9)
    ax.set_yticks(range(n), names, fontsize=8 if n > 4 else 9)
    ax.set_xlabel("预测类别")
    ax.set_ylabel("真实类别")
    ax.set_title(title)
    if n <= 20:
        fs = 10 if n <= 4 else 6
        thr = cm.max() / 2
        for i in range(n):
            for j in range(n):
                ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=fs,
                        color="white" if cm[i, j] > thr else "#222222")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"已保存 {path}")


def load(subset: str, cats=None, remove=REMOVE):
    return fetch_20newsgroups(subset=subset, categories=cats, shuffle=True,
                              random_state=42, remove=remove)


def main() -> None:
    sys.stdout = Tee(OUT / "exp4_log.txt")
    results: dict = {}

    # ---------- 0 环境信息 ----------
    banner("0 环境信息")
    import sklearn
    print("Python:", sys.version.split()[0])
    print("scikit-learn:", sklearn.__version__)
    print("matplotlib:", matplotlib.__version__)
    print("numpy:", np.__version__)
    print("设备：纯 CPU（sklearn 传统机器学习，无需 GPU）")
    results["env"] = {"python": sys.version.split()[0], "sklearn": sklearn.__version__}

    # ---------- 1 加载 4 类子集 ----------
    banner("1 加载 4 类子集（讲义推荐缩小规模）")
    train = load("train", CATS4)
    test = load("test", CATS4)
    print("训练集:", len(train.data), "测试集:", len(test.data))
    print("类别:", train.target_names)
    print("\n第一篇前 200 字符：")
    print(train.data[0][:200])
    results["subset4"] = {"cats": train.target_names, "train_n": len(train.data),
                          "test_n": len(test.data)}

    # ---------- 2 TF-IDF + 朴素贝叶斯训练 ----------
    banner("2 TF-IDF 特征化 + 朴素贝叶斯训练")
    model = new_nb()
    r4 = fit_eval("4类 baseline", model, train, test)
    results["subset4"].update({"features": r4["n_features"],
                               "fit_time": r4["fit_time"], "acc": r4["acc"]})

    # ---------- 3 评估：准确率 / 分类报告 / 混淆矩阵 ----------
    banner("3 评估：准确率 / 分类报告 / 混淆矩阵")
    pred = r4["pred"]
    names4 = test.target_names
    print("测试集准确率:", round(r4["acc"], 4))
    print("\n分类报告:")
    report4 = classification_report(test.target, pred, target_names=names4)
    print(report4)
    cm4 = confusion_matrix(test.target, pred)
    print("混淆矩阵:")
    print(cm4)
    (OUT / "classification_report_4class.txt").write_text(report4, encoding="utf-8")
    save_confmat_csv(cm4, names4, OUT / "confmat_4class.csv")
    plot_confmat(cm4, names4, OUT / "exp4_confmat_4class.png",
                 "4 类子集混淆矩阵（TF-IDF + MultinomialNB）")
    lo, hi = f1_extremes(test, pred, names4)
    pairs4 = top_confusion(cm4, names4, 1)
    print(f"\nF1 最高类别: {hi['cls']} ({hi['f1']:.2f})，F1 最低类别: {lo['cls']} ({lo['f1']:.2f})")
    print(f"混淆最严重的类别对: {pairs4[0]['true']} → {pairs4[0]['pred']} "
          f"({pairs4[0]['count']} 篇)")
    results["subset4"].update({"f1_min": lo, "f1_max": hi, "top_pair": pairs4[0],
                               "confmat": cm4.tolist()})

    # ---------- 4 对新文本做预测 ----------
    banner("4 对任意新文本做预测")
    docs = [
        "The shuttle launch was delayed due to weather conditions at the space center.",
        "He hit a home run in the ninth inning to win the game.",
        "My graphics card cannot run this 3D rendering software smoothly.",
    ]
    preds3 = []
    for d, p_ in zip(docs, model.predict(docs)):
        print("预测类别:", names4[p_], " <- ", d[:50], "...")
        preds3.append({"text": d, "pred": names4[p_]})
    results["subset4"]["predict3"] = preds3

    # ---------- 基础任务A：去掉邮件头/脚注/引用前后的对比 ----------
    banner("基础任务A remove=('headers','footers','quotes') 前后对比")
    train_raw = load("train", CATS4, remove=())
    test_raw = load("test", CATS4, remove=())
    print("未去掉邮件头时，某训练文档的开头 300 字符：")
    print(train_raw.data[0][:300])
    print("...")
    r_raw = fit_eval("4类 未去头", new_nb(), train_raw, test_raw)
    print(f"去掉 headers/footers/quotes：准确率 {r4['acc']:.4f}")
    print(f"保留 headers/footers/quotes：准确率 {r_raw['acc']:.4f}（虚高）")
    results["remove_compare"] = {"with_remove": r4["acc"],
                                 "without_remove": r_raw["acc"]}

    # ---------- 基础任务B：两个易混淆类别 ----------
    banner("基础任务B 只在 sci.electronics 与 sci.med 两类上训练")
    train2 = load("train", CATS2)
    test2 = load("test", CATS2)
    print("训练集:", len(train2.data), "测试集:", len(test2.data))
    r2 = fit_eval("2类 electronics/med", new_nb(), train2, test2)
    pred2 = r2["pred"]
    names2 = test2.target_names
    report2 = classification_report(test2.target, pred2, target_names=names2)
    print("\n分类报告:")
    print(report2)
    cm2 = confusion_matrix(test2.target, pred2)
    print("混淆矩阵:")
    print(cm2)
    save_confmat_csv(cm2, names2, OUT / "confmat_2class.csv")
    plot_confmat(cm2, names2, OUT / "exp4_confmat_2class.png",
                 "sci.electronics vs sci.med 混淆矩阵")
    results["pair2"] = {"cats": names2, "train_n": len(train2.data),
                        "test_n": len(test2.data), "acc": r2["acc"],
                        "cm": cm2.tolist()}

    # ---------- 进阶A：全量 20 类 ----------
    banner("进阶A 全量 20 类")
    train20 = load("train")
    test20 = load("test")
    names20 = train20.target_names
    print("训练集:", len(train20.data), "测试集:", len(test20.data),
          "类别数:", len(names20))
    r20 = fit_eval("20类 baseline", new_nb(), train20, test20)
    pred20 = r20["pred"]
    print("测试集准确率:", round(r20["acc"], 4))
    report20 = classification_report(test20.target, pred20, target_names=names20)
    print("\n分类报告:")
    print(report20)
    cm20 = confusion_matrix(test20.target, pred20)
    print("混淆矩阵（20×20，数值表见 confmat_20class.csv）:")
    print(cm20)
    (OUT / "classification_report_20class.txt").write_text(report20, encoding="utf-8")
    save_confmat_csv(cm20, names20, OUT / "confmat_20class.csv")
    plot_confmat(cm20, names20, OUT / "exp4_confmat_20class.png",
                 "全量 20 类混淆矩阵（TF-IDF + MultinomialNB）")
    pairs20 = top_confusion(cm20, names20, 10)
    print("\n最易混淆的类别对 Top10（真实 → 预测，次数）:")
    for p in pairs20:
        print(f"  {p['true']} → {p['pred']}: {p['count']}")
    lo20, hi20 = f1_extremes(test20, pred20, names20)
    print(f"\nF1 最高类别: {hi20['cls']} ({hi20['f1']:.2f})，"
          f"F1 最低类别: {lo20['cls']} ({lo20['f1']:.2f})")
    results["full20"] = {"train_n": len(train20.data), "test_n": len(test20.data),
                         "features": r20["n_features"], "fit_time": r20["fit_time"],
                         "acc": r20["acc"], "top_pairs": pairs20,
                         "f1_min": lo20, "f1_max": hi20}

    # ---------- 进阶B：TfidfVectorizer 参数对比 ----------
    banner("进阶B TfidfVectorizer 参数对比（max_df / min_df / ngram_range）")
    variants = [
        ("baseline", {}),
        ("max_df=0.5", {"max_df": 0.5}),
        ("min_df=2", {"min_df": 2}),
        ("ngram_range=(1,2)", {"ngram_range": (1, 2)}),
    ]
    vec_rows = []
    for label, kw in variants:
        ra = fit_eval(f"4类 {label}", new_nb(**kw), train, test)
        rb = fit_eval(f"20类 {label}", new_nb(**kw), train20, test20)
        vec_rows.append({"variant": label, "acc4": ra["acc"], "n4": ra["n_features"],
                         "time4": ra["fit_time"], "acc20": rb["acc"],
                         "n20": rb["n_features"], "time20": rb["fit_time"]})
    print("\n汇总（准确率 / 特征维度）:")
    print(f"{'变体':<18}{'4类准确率':>10}{'4类特征':>10}{'20类准确率':>11}{'20类特征':>10}")
    for row in vec_rows:
        print(f"{row['variant']:<18}{row['acc4']:>10.4f}{row['n4']:>10}"
              f"{row['acc20']:>11.4f}{row['n20']:>10}")
    results["vec_variants"] = vec_rows

    # ---------- 进阶C：LogisticRegression 对比 ----------
    banner("进阶C LogisticRegression(max_iter=1000) 与朴素贝叶斯对比")
    def new_lr() -> Pipeline:
        return Pipeline([
            ("tfidf", TfidfVectorizer(stop_words="english")),
            ("clf", LogisticRegression(max_iter=1000)),
        ])
    lr4 = fit_eval("4类 LogisticRegression", new_lr(), train, test)
    lr20 = fit_eval("20类 LogisticRegression", new_lr(), train20, test20)
    print("\n对比（准确率 / 训练耗时）:")
    print(f"4类:  MultinomialNB {r4['acc']:.4f} / {r4['fit_time']:.2f}s   "
          f"LogisticRegression {lr4['acc']:.4f} / {lr4['fit_time']:.2f}s")
    print(f"20类: MultinomialNB {r20['acc']:.4f} / {r20['fit_time']:.2f}s   "
          f"LogisticRegression {lr20['acc']:.4f} / {lr20['fit_time']:.2f}s")
    results["clf_compare"] = {
        "nb4": {"acc": r4["acc"], "time": r4["fit_time"]},
        "lr4": {"acc": lr4["acc"], "time": lr4["fit_time"]},
        "nb20": {"acc": r20["acc"], "time": r20["fit_time"]},
        "lr20": {"acc": lr20["acc"], "time": lr20["fit_time"]},
    }

    # ---------- 实验汇总 ----------
    banner("实验汇总")
    main_rows = [
        ("4类 baseline（主模型）", r4),
        ("4类 未去 headers/footers/quotes", r_raw),
        ("2类 electronics vs med", r2),
        ("20类 全量", r20),
        ("4类 LogisticRegression", lr4),
        ("20类 LogisticRegression", lr20),
    ]
    print(f"{'实验':<28}{'测试准确率':>10}{'训练耗时(s)':>12}")
    summary_rows = []
    for name, r in main_rows:
        print(f"{name:<28}{r['acc']:>10.4f}{r['fit_time']:>12.2f}")
        summary_rows.append({"实验": name, "测试准确率": round(r["acc"], 4),
                             "训练耗时s": round(r["fit_time"], 2),
                             "特征维度": r["n_features"]})
    print("\nTfidfVectorizer 参数变体（MultinomialNB）:")
    print(f"{'变体':<18}{'4类准确率':>10}{'20类准确率':>11}")
    for row in vec_rows:
        print(f"{row['variant']:<18}{row['acc4']:>10.4f}{row['acc20']:>11.4f}")
        summary_rows.append({"实验": f"4类 {row['variant']}",
                             "测试准确率": round(row["acc4"], 4),
                             "训练耗时s": round(row["time4"], 2),
                             "特征维度": row["n4"]})
        summary_rows.append({"实验": f"20类 {row['variant']}",
                             "测试准确率": round(row["acc20"], 4),
                             "训练耗时s": round(row["time20"], 2),
                             "特征维度": row["n20"]})
    with open(OUT / "summary.csv", "w", encoding="utf-8-sig") as f:
        f.write("实验,测试准确率,训练耗时s,特征维度\n")
        for row in summary_rows:
            f.write(f"{row['实验']},{row['测试准确率']},{row['训练耗时s']},{row['特征维度']}\n")

    # 各实验准确率对比图
    labels = [r[0] for r in main_rows] + [f"4类 {row['variant']}" for row in vec_rows[1:]]
    accs = [r[1]["acc"] * 100 for r in main_rows] + [row["acc4"] * 100 for row in vec_rows[1:]]
    fig, ax = plt.subplots(figsize=(9, 6.2))
    colors = ["#c0504d" if "未去" in l else "#4f81bd" for l in labels]
    bars = ax.barh(range(len(labels)), accs, color=colors)
    ax.set_yticks(range(len(labels)), labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("测试集准确率 (%)")
    ax.set_title("各实验测试准确率对比")
    ax.set_xlim(0, 100)
    for b, a in zip(bars, accs):
        ax.text(b.get_width() + 1, b.get_y() + b.get_height() / 2, f"{a:.2f}%",
                va="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "exp4_exp_accuracy.png", dpi=150)
    plt.close(fig)
    print("已保存 exp4_results/exp4_exp_accuracy.png")

    # 20 类最易混淆类别对 Top10 柱状图
    pair_labels = [f"{p['true']} → {p['pred']}" for p in pairs20]
    pair_counts = [p["count"] for p in pairs20]
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.barh(range(len(pair_labels)), pair_counts, color="#8064a2")
    ax.set_yticks(range(len(pair_labels)), pair_labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("被误分类篇数")
    ax.set_title("全量 20 类最易混淆类别对 Top10")
    for i, c in enumerate(pair_counts):
        ax.text(c + 1, i, str(c), va="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "exp4_top_confusions.png", dpi=150)
    plt.close(fig)
    print("已保存 exp4_results/exp4_top_confusions.png")

    (OUT / "summary.json").write_text(json.dumps(results, ensure_ascii=False, indent=2),
                                      encoding="utf-8")
    print("\n全部实验完成，结果见 exp4_results/ 目录。")


if __name__ == "__main__":
    main()
