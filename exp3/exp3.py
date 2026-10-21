"""Experiment 3: Convolutional neural network image classification on CIFAR-10.

Covers every required and optional task from the lab handout:
- Steps 1-4: data loading, CNN definition, training loop, test evaluation.
- Basic tasks: per-class accuracy and most-confused classes; hyperparameter
  comparison (batch size 32/128, learning rate 0.01/0.0001).
- Advanced tasks: data augmentation comparison, deeper CNN with parameter
  count, and a training-loss curve figure.

Run with: python exp3.py          (full training set, 2 epochs, all runs)
Optional: python exp3.py --quick  (first 2000 images, 1 epoch, fast pass)
          python exp3.py --epochs 3 --runs baseline,augment
"""

from __future__ import annotations

import argparse
import csv
import os
import platform
import random
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms

CLASSES = ("plane", "car", "bird", "cat", "deer",
           "dog", "frog", "horse", "ship", "truck")

# One entry per comparison run. The baseline matches the official tutorial
# setting (batch 64, lr 0.001, the small Net, no augmentation).
RUN_SPECS = [
    ("baseline", dict(batch_size=64, lr=0.001, deep=False, augment=False)),
    ("bs32", dict(batch_size=32, lr=0.001, deep=False, augment=False)),
    ("bs128", dict(batch_size=128, lr=0.001, deep=False, augment=False)),
    ("lr0.01", dict(batch_size=64, lr=0.01, deep=False, augment=False)),
    ("lr0.0001", dict(batch_size=64, lr=0.0001, deep=False, augment=False)),
    ("augment", dict(batch_size=64, lr=0.001, deep=False, augment=True)),
    ("deep", dict(batch_size=64, lr=0.001, deep=True, augment=False)),
    # Longer training with the best settings found above: shows the real
    # benefit of data augmentation once the model trains long enough.
    ("final", dict(batch_size=64, lr=0.01, deep=False, augment=True, epochs=10)),
    # Control group for the "final" run: same training length without
    # augmentation, so the augmentation effect is isolated.
    ("final_noaug", dict(batch_size=64, lr=0.01, deep=False, augment=False,
                         epochs=10)),
]


class Tee:
    """Copy every printed line into the log file as well as the console."""

    def __init__(self, console, logfile):
        self.console = console
        self.logfile = logfile

    def write(self, text):
        self.console.write(text)
        self.logfile.write(text)

    def flush(self):
        self.console.flush()
        self.logfile.flush()


class Net(nn.Module):
    """Small tutorial CNN: two 5x5 conv layers + three linear layers."""

    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)      # 3 input channels, 6 output, 5x5 kernel
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = torch.flatten(x, 1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)


class NetDeep(nn.Module):
    """Advanced-task CNN: three 3x3 conv layers with 16/32/64 channels."""

    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.conv3 = nn.Conv2d(32, 64, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 4 * 4, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))  # 32x32 -> 16x16
        x = self.pool(F.relu(self.conv2(x)))  # 16x16 -> 8x8
        x = self.pool(F.relu(self.conv3(x)))  # 8x8 -> 4x4
        x = torch.flatten(x, 1)
        x = F.relu(self.fc1(x))
        return self.fc2(x)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick", action="store_true",
                        help="Fast mode: first 2000 training images, 1 epoch.")
    parser.add_argument("--epochs", type=int, default=None,
                        help="Override the number of training epochs.")
    parser.add_argument("--runs", default="all",
                        help="Comma-separated run names, or 'all'. "
                             "Choices: " + ",".join(name for name, _ in RUN_SPECS))
    parser.add_argument("--output-dir", type=Path, default=Path("exp3_results"),
                        help="Directory for CSV, PNG, and log outputs.")
    parser.add_argument("--data-root", type=Path, default=Path("./data"))
    parser.add_argument("--num-workers", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def make_loader(dataset, batch_size, shuffle, num_workers, seed):
    generator = torch.Generator().manual_seed(seed)
    return torch.utils.data.DataLoader(
        dataset, batch_size=batch_size, shuffle=shuffle,
        num_workers=num_workers, persistent_workers=num_workers > 0,
        generator=generator)


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def train_model(net, trainloader, epochs, lr, device):
    """Train and return (per-batch losses, last printed average loss, minutes)."""
    net.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(net.parameters(), lr=lr, momentum=0.9)
    batch_losses = []
    last_printed_avg = float("nan")
    start = time.perf_counter()
    for epoch in range(epochs):
        running_loss = 0.0
        for i, (inputs, labels) in enumerate(trainloader):
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = net(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            batch_losses.append(loss.item())
            if i % 200 == 199:  # print every 200 mini-batches
                last_printed_avg = running_loss / 200
                print(f"[第{epoch + 1}轮, 第{i + 1:4d}批] 平均损失: {last_printed_avg:.3f}")
                running_loss = 0.0
        # End-of-epoch summary (also gives a value when a run has < 200 batches).
        epoch_loss = float(np.mean(batch_losses[-(i + 1):]))
        print(f"[第{epoch + 1}轮结束] 本轮平均损失: {epoch_loss:.3f}")
        last_printed_avg = epoch_loss
    minutes = (time.perf_counter() - start) / 60
    return batch_losses, last_printed_avg, minutes


def evaluate(net, testloader, device):
    """Return (overall accuracy, per-class correct, per-class total, confusion)."""
    net.eval()
    correct, total = 0, 0
    class_correct = [0] * len(CLASSES)
    class_total = [0] * len(CLASSES)
    confusion = torch.zeros(len(CLASSES), len(CLASSES), dtype=torch.int64)
    with torch.no_grad():
        for images, labels in testloader:
            images, labels = images.to(device), labels.to(device)
            outputs = net(images)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            for label, pred in zip(labels.tolist(), predicted.tolist()):
                class_total[label] += 1
                class_correct[label] += int(label == pred)
                confusion[label, pred] += 1
    return correct / total, class_correct, class_total, confusion


def show_batch(loader, save_path: Path) -> None:
    """Step 1: save a grid of 8 training images."""
    images, labels = next(iter(loader))
    grid = torchvision.utils.make_grid(images[:8])
    grid = grid / 2 + 0.5  # un-normalize for display
    plt.figure(figsize=(10, 3))
    plt.imshow(np.transpose(grid.numpy(), (1, 2, 0)))
    plt.title(" ".join(CLASSES[labels[j]] for j in range(8)))
    plt.axis("off")
    plt.savefig(save_path, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"已保存 {save_path}")


def smooth(values, window=50):
    if len(values) < window:
        return values
    kernel = np.ones(window) / window
    return np.convolve(values, kernel, mode="valid")


def main() -> None:
    args = parse_args()
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        # Keep the console's native encoding; just never crash on odd glyphs.
        sys.stdout.reconfigure(errors="replace")
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    log_path = out / "exp3_log.txt"
    log_file = open(log_path, "w", encoding="utf-8", buffering=1)
    sys.stdout = Tee(sys.__stdout__, log_file)

    # ---- 3.2/3.3 environment report and dataset download ----
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cpu_id = os.environ.get("PROCESSOR_IDENTIFIER", platform.processor())
    print("PyTorch:", torch.__version__)
    print("torchvision:", torchvision.__version__)
    print("CUDA 可用:", torch.cuda.is_available())
    print("使用设备:", device)
    print(f"机器配置: {cpu_id}, {os.cpu_count()} 逻辑核")

    epochs = args.epochs if args.epochs is not None else (1 if args.quick else 2)
    train_limit = 2000 if args.quick else None

    plain_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ])
    augment_transform = transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ])
    trainset = torchvision.datasets.CIFAR10(
        root=str(args.data_root), train=True, download=True, transform=plain_transform)
    trainset_aug = torchvision.datasets.CIFAR10(
        root=str(args.data_root), train=True, download=True, transform=augment_transform)
    testset = torchvision.datasets.CIFAR10(
        root=str(args.data_root), train=False, download=True, transform=plain_transform)

    print("训练集大小:", len(trainset))   # 50000
    print("测试集大小:", len(testset))    # 10000
    print("类别:", trainset.classes)
    print(f"本次训练规模: {'前2000张子集' if train_limit else '全量50000张'}, 训练{epochs}轮")

    # ---- Step 1: look at a batch of samples ----
    sample_loader = make_loader(trainset, 64, True, args.num_workers, args.seed)
    show_batch(sample_loader, Path("exp3_samples.png"))
    del sample_loader

    if train_limit is not None:
        trainset = torch.utils.data.Subset(trainset, range(train_limit))
        trainset_aug = torch.utils.data.Subset(trainset_aug, range(train_limit))
    testloader = make_loader(testset, 64, False, args.num_workers, args.seed)

    selected = ([name for name, _ in RUN_SPECS] if args.runs == "all"
                else [s.strip() for s in args.runs.split(",")])
    specs = dict(RUN_SPECS)
    for name in selected:
        if name not in specs:
            raise SystemExit(f"未知实验名: {name}，可选: {list(specs)}")

    results = []
    for name in selected:
        cfg = specs[name]
        run_epochs = cfg.get("epochs", epochs)
        if args.quick:
            run_epochs = min(run_epochs, 2)
        print(f"\n===== 实验 {name}: batch_size={cfg['batch_size']}, "
              f"lr={cfg['lr']}, {'NetDeep' if cfg['deep'] else 'Net'}, "
              f"{'有数据增强' if cfg['augment'] else '无数据增强'}, "
              f"训练{run_epochs}轮 =====")
        set_seed(args.seed)  # same weight init and shuffle order for fair comparison
        net = NetDeep() if cfg["deep"] else Net()
        n_params = sum(p.numel() for p in net.parameters())
        print(f"参数量: {n_params:,}")
        dataset = trainset_aug if cfg["augment"] else trainset
        trainloader = make_loader(dataset, cfg["batch_size"], True,
                                  args.num_workers, args.seed)
        batch_losses, last_avg_loss, minutes = train_model(
            net, trainloader, run_epochs, cfg["lr"], device)
        del trainloader

        if name == "baseline":
            # Step 3 output: save the trained weights; Step 4 reloads them.
            torch.save(net.state_dict(), "exp3_net.pth")
            print("已保存 exp3_net.pth")
            net = (NetDeep() if cfg["deep"] else Net)().to(device)
            net.load_state_dict(
                torch.load("exp3_net.pth", weights_only=True, map_location=device))
            print("已从 exp3_net.pth 重新加载模型用于评估")
        if name == "final":
            torch.save(net.state_dict(), "exp3_net_final.pth")
            print("已保存 exp3_net_final.pth")

        t0 = time.perf_counter()
        accuracy, class_correct, class_total, confusion = evaluate(net, testloader, device)
        eval_seconds = time.perf_counter() - t0
        print(f"测试集整体准确率: {100 * accuracy:.2f}%  (评估耗时 {eval_seconds:.0f}s)")
        for j, cls in enumerate(CLASSES):
            print(f"  类别 {cls:6s} 准确率: {100 * class_correct[j] / class_total[j]:6.2f}%")

        results.append(dict(
            name=name, batch_size=cfg["batch_size"], lr=cfg["lr"],
            model="NetDeep" if cfg["deep"] else "Net",
            augment=cfg["augment"], params=n_params, epochs=run_epochs,
            train_images=len(dataset),
            final_avg_loss=last_avg_loss, train_minutes=minutes,
            test_accuracy=accuracy, class_correct=class_correct,
            class_total=class_total, confusion=confusion,
            batch_losses=batch_losses))

        if name in ("baseline", "final"):
            with open(out / f"per_class_accuracy_{name}.csv", "w",
                      newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["class", "correct", "total", "accuracy"])
                for j, cls in enumerate(CLASSES):
                    writer.writerow([cls, class_correct[j], class_total[j],
                                     f"{100 * class_correct[j] / class_total[j]:.2f}"])
            with open(out / f"confusion_matrix_{name}.csv", "w",
                      newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["true\\pred", *CLASSES])
                for j, cls in enumerate(CLASSES):
                    writer.writerow([cls, *confusion[j].tolist()])

    # ---- figures ----
    plt.figure(figsize=(9, 5))
    for r in results:
        label = f"{r['name']} (bs{r['batch_size']}, lr{r['lr']}, {r['epochs']}ep"
        if r["augment"]:
            label += ", aug"
        label += ")"
        plt.plot(smooth(r["batch_losses"]), label=label)
    plt.xlabel("iteration")
    plt.ylabel("training loss (50-batch moving average)")
    plt.title("Training loss curves")
    plt.legend(fontsize=8)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(out / "loss_curves.png", dpi=150)
    plt.close()
    print(f"\n已保存 {out / 'loss_curves.png'}")

    for key in ("baseline", "final"):
        run = next((r for r in results if r["name"] == key), None)
        if run is None:
            continue
        accs = [100 * c / t for c, t in
                zip(run["class_correct"], run["class_total"])]
        plt.figure(figsize=(9, 4))
        plt.bar(CLASSES, accs, color="#5b8db8")
        plt.axhline(100 * run["test_accuracy"], color="#c0504d",
                    linestyle="--", label=f"overall {100 * run['test_accuracy']:.1f}%")
        plt.ylabel("accuracy (%)")
        plt.title(f"Per-class test accuracy ({key})")
        plt.legend()
        plt.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.savefig(out / f"per_class_accuracy_{key}.png", dpi=150)
        plt.close()
        print(f"已保存 {out / f'per_class_accuracy_{key}.png'}")

    # ---- summary table ----
    with open(out / "summary.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["run", "model", "batch_size", "lr", "augment", "params",
                         "epochs", "train_images", "final_avg_loss",
                         "train_minutes", "test_accuracy_pct"])
        for r in results:
            writer.writerow([r["name"], r["model"], r["batch_size"], r["lr"],
                             r["augment"], r["params"], r["epochs"], r["train_images"],
                             f"{r['final_avg_loss']:.3f}", f"{r['train_minutes']:.1f}",
                             f"{100 * r['test_accuracy']:.2f}"])

    print("\n===== 实验汇总 =====")
    print(f"{'run':10s} {'model':8s} {'bs':>4s} {'lr':>8s} {'轮数':>4s} {'参数量':>10s} "
          f"{'末次平均损失':>10s} {'训练分钟':>8s} {'测试准确率':>9s}")
    for r in results:
        print(f"{r['name']:10s} {r['model']:8s} {r['batch_size']:4d} {r['lr']:8.4f} "
              f"{r['epochs']:4d} {r['params']:10,d} {r['final_avg_loss']:10.3f} "
              f"{r['train_minutes']:8.1f} {100 * r['test_accuracy']:8.2f}%")

    for key in ("baseline", "final"):
        run = next((r for r in results if r["name"] == key), None)
        if run is None:
            continue
        conf = run["confusion"]
        pairs = [(int(conf[t, p]), CLASSES[t], CLASSES[p])
                 for t in range(len(CLASSES)) for p in range(len(CLASSES)) if t != p]
        pairs.sort(reverse=True)
        print(f"\n{key} 最容易混淆的类别对（真实→预测，按误判次数排序，前8）:")
        for count, true_cls, pred_cls in pairs[:8]:
            print(f"  {true_cls:6s} -> {pred_cls:6s}  {count:4d} 次")

    print(f"\n所有输出已写入 {out.resolve()}")
    print("根目录附加文件: exp3_samples.png, exp3_net.pth, exp3_net_final.pth")


if __name__ == "__main__":
    main()
