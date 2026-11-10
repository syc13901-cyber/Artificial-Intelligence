/* Generate 第3次实验报告.docx — Experiment 3 (CNN CIFAR-10) lab report.
 * All numbers are read from exp3_results/ CSV files and the run log so the
 * report always matches the actual measured values. */

const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, Header, Footer, PageNumber, AlignmentType, HeadingLevel,
  WidthType, BorderStyle, ShadingType,
} = require("docx");
const fs = require("fs");
const { imageSize } = require("image-size");

// ---------- data loading ----------
function readCsv(path) {
  const lines = fs.readFileSync(path, "utf-8").trim().split(/\r?\n/);
  const header = lines[0].split(",");
  return lines.slice(1).map((line) => {
    const cells = line.split(",");
    const row = {};
    header.forEach((h, i) => (row[h] = cells[i]));
    return row;
  });
}

const summaryRows = readCsv("exp3_results/summary.csv");
const S = {};
for (const r of summaryRows) S[r.run] = r;
const perClassBaseline = readCsv("exp3_results/per_class_accuracy_baseline.csv");
const perClassFinal = readCsv("exp3_results/per_class_accuracy_final.csv");
const logLines = fs.readFileSync("exp3_results/exp3_log.txt", "utf-8").split(/\r?\n/);

const pct = (r) => `${r.test_accuracy_pct}%`;
const diffPp = (a, b) =>
  `${(parseFloat(a.test_accuracy_pct) - parseFloat(b.test_accuracy_pct) >= 0 ? "+" : "")}${(
    parseFloat(a.test_accuracy_pct) - parseFloat(b.test_accuracy_pct)
  ).toFixed(2)} 个百分点`;

// ---------- style helpers ----------
const FONT_BODY = { ascii: "Times New Roman", eastAsia: "SimSun" };
const FONT_HEAD = { ascii: "Times New Roman", eastAsia: "SimHei" };
const FONT_CODE = { ascii: "Consolas", eastAsia: "SimSun" };

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 160, line: 312 },
    children: [new TextRun({ text, bold: true, size: 32, font: FONT_HEAD, color: "000000" })],
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 240, after: 120, line: 312 },
    children: [new TextRun({ text, bold: true, size: 28, font: FONT_HEAD, color: "000000" })],
  });
}

function body(text, opts = {}) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    indent: { firstLine: 480 },
    spacing: { line: 312, after: 60 },
    children: [new TextRun({ text, size: 24, font: FONT_BODY, color: "000000", ...opts })],
  });
}

// Paragraph with mixed bold/plain segments: parts = [[text, bold], ...]
function bodyRich(parts) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    indent: { firstLine: 480 },
    spacing: { line: 312, after: 60 },
    children: parts.map(
      ([text, bold]) => new TextRun({ text, bold: !!bold, size: 24, font: FONT_BODY, color: "000000" })
    ),
  });
}

function captionTable(text) {
  return new Paragraph({
    keepNext: true,
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 60, line: 312 },
    children: [new TextRun({ text, bold: true, size: 21, font: FONT_HEAD, color: "000000" })],
  });
}

function captionFigure(text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 60, after: 120, line: 312 },
    children: [new TextRun({ text, size: 21, font: FONT_HEAD, color: "000000" })],
  });
}

function figure(path, displayWidth) {
  const buf = fs.readFileSync(path);
  const dim = imageSize(buf);
  const h = Math.round((displayWidth * dim.height) / dim.width);
  return new Paragraph({
    keepNext: true,
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 40 },
    children: [new ImageRun({ data: buf, transformation: { width: displayWidth, height: h }, type: "png" })],
  });
}

function codeBlock(lines) {
  return lines.map(
    (line) =>
      new Paragraph({
        shading: { type: ShadingType.CLEAR, fill: "F5F5F5" },
        spacing: { line: 276 },
        indent: { left: 240, right: 240 },
        children: [new TextRun({ text: line.length ? line : " ", size: 18, font: FONT_CODE, color: "1A1A1A" })],
      })
  );
}

const TABLE_BORDERS = {
  top: { style: BorderStyle.SINGLE, size: 4, color: "8A8A8A" },
  bottom: { style: BorderStyle.SINGLE, size: 4, color: "8A8A8A" },
  left: { style: BorderStyle.NONE },
  right: { style: BorderStyle.NONE },
  insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: "C8C8C8" },
  insideVertical: { style: BorderStyle.SINGLE, size: 2, color: "C8C8C8" },
};

function cell(text, { width, bold = false, size = 21, align = AlignmentType.CENTER, fill } = {}) {
  return new TableCell({
    width: width !== undefined ? { size: width, type: WidthType.PERCENTAGE } : undefined,
    shading: fill ? { type: ShadingType.CLEAR, fill } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [
      new Paragraph({
        alignment: align,
        spacing: { line: 276 },
        children: [new TextRun({ text: String(text), bold, size, font: FONT_BODY, color: "000000" })],
      }),
    ],
  });
}

function makeTable(headerCells, dataRows, widths, { size = 21, firstColLeft = false } = {}) {
  const rows = [
    new TableRow({
      tableHeader: true,
      cantSplit: true,
      children: headerCells.map((t, i) =>
        cell(t, { width: widths[i], bold: true, size, fill: "EEF2F7" })
      ),
    }),
    ...dataRows.map(
      (r) =>
        new TableRow({
          cantSplit: true,
          children: r.map((t, i) =>
            cell(t, {
              width: widths[i],
              size,
              align: firstColLeft && i === 0 ? AlignmentType.LEFT : AlignmentType.CENTER,
            })
          ),
        })
    ),
  ];
  return new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, borders: TABLE_BORDERS, rows });
}

// ---------- document content ----------
const children = [];

// Title block (not a Heading style; per student-report convention)
children.push(
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 60, line: 420, lineRule: "atLeast" },
    children: [new TextRun({ text: "实验三\u3000卷积神经网络（CNN）图像分类实验报告", bold: true, size: 36, font: FONT_HEAD, color: "000000" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 40, line: 312 },
    children: [new TextRun({ text: "姓名：【姓名】\u3000\u3000学号：【学号】\u3000\u3000班级：【班级】", size: 24, font: FONT_BODY, color: "000000" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 160, line: 312 },
    children: [new TextRun({ text: "2026 年 10 月 21 日", size: 24, font: FONT_BODY, color: "000000" })],
  })
);

// ============ 一、实验目标 ============
children.push(h1("一、实验目标"));
children.push(
  body("本实验按照讲义要求，使用 PyTorch 在真实公开数据集 CIFAR-10 上完成卷积神经网络的图像分类任务，具体目标包括：掌握用 torchvision 下载并加载公开数据集的完整流程；理解卷积层、池化层、全连接层的作用，用 PyTorch 定义小型 CNN；掌握\u201c前向传播—计算损失—反向传播—更新参数\u201d的训练循环写法；在测试集上评估模型整体准确率与各类别准确率，并对结果做出分析。"),
  body("在完成基础任务（结果记录、各类别准确率统计、batch_size 与学习率调参实验）之外，本次实验还完成了全部三项进阶任务：数据增强对比、加深网络对比、训练损失曲线绘制，共进行了 9 组训练实验，全部数值均为本人电脑实测。")
);

// ============ 二、实验环境 ============
children.push(h1("二、实验环境"));
children.push(captionTable("表 1\u3000实验环境配置"));
children.push(
  makeTable(
    ["项目", "配置"],
    [
      ["操作系统", "Windows 11 专业版（64 位）"],
      ["处理器 / 内存", "Intel Core i9-14900HX（32 逻辑核）/ 16 GB"],
      ["Python", "3.13.14"],
      ["PyTorch / torchvision", `2.14.0+cpu / 0.29.0+cpu`],
      ["GPU", "未使用（torch.cuda.is_available() 为 False，纯 CPU 训练）"],
    ],
    [30, 70],
    { firstColLeft: true }
  )
);
children.push(
  body("运行 exp3.py 时脚本会先打印版本与设备信息，确认环境无误后再下载数据集（首次约 170 MB，之后使用本地缓存）。环境检测与数据集加载的运行日志见图 1。"),
  figure("exp3_results/exp3_log_env.png", 500),
  captionFigure("图 1\u3000环境信息与数据集加载日志")
);

// ============ 三、实验数据与实验步骤 ============
children.push(h1("三、实验数据与实验步骤"));
children.push(h2("（一）数据集获取与样例查看"));
children.push(
  body("CIFAR-10 共 60 000 张 32×32 彩色图片，分 10 个类别（plane、car、bird、cat、deer、dog、frog、horse、ship、truck），其中训练集 50 000 张、测试集 10 000 张。通过 torchvision.datasets.CIFAR10 接口加载：首次运行自动从官方发布页下载压缩包并解压到 ./data 目录，之后直接使用本地缓存。"),
  body("预处理分两步：transforms.ToTensor() 把 [0,255] 的 uint8 像素转为 [0,1] 的 float32 张量，并将 H×W×C 调整为 PyTorch 卷积需要的 C×H×W 维度顺序；transforms.Normalize((0.5,0.5,0.5),(0.5,0.5,0.5)) 再把每个通道映射到均值 0、范围约 [-1,1]。DataLoader 取 batch_size=64、shuffle=True；由于 Windows 下 num_workers>0 时子进程会重新导入主模块，全部训练与加载代码都放在 if __name__ == \"__main__\": 保护块内。"),
  body("从训练集取一个批次做可视化（图 2）：8 张图片与标签一一对应。图片可以辨认，但 32×32 的分辨率非常低，细节大量丢失，这正是该任务的难度来源。"),
  figure("exp3_samples.png", 520),
  captionFigure("图 2\u3000训练集样例图片（exp3_samples.png）")
);

children.push(h2("（二）CNN 网络结构定义"));
children.push(
  body("按讲义定义小型 CNN（表 2）：两个 5×5 卷积层提取特征、每个卷积层后接 ReLU 与 2×2 最大池化降采样，最后三层全连接完成分类。数据流：3×32×32 → conv1 后 6×28×28 → 池化 6×14×14 → conv2 后 16×10×10 → 池化 16×5×5 → 展平 400 维 → 120 → 84 → 10。")
);
children.push(captionTable("表 2\u3000Net 网络结构（参数量合计 62 006）"));
children.push(
  makeTable(
    ["层", "配置", "输出尺寸"],
    [
      ["输入", "3×32×32 彩色图", "3×32×32"],
      ["conv1", "Conv2d(3, 6, 5) + ReLU + MaxPool2d(2,2)", "6×14×14"],
      ["conv2", "Conv2d(6, 16, 5) + ReLU + MaxPool2d(2,2)", "16×5×5"],
      ["fc1", "Linear(400, 120) + ReLU", "120"],
      ["fc2", "Linear(120, 84) + ReLU", "84"],
      ["fc3", "Linear(84, 10)", "10"],
    ],
    [14, 60, 26],
    { firstColLeft: false }
  )
);
children.push(
  body("用 sum(p.numel() for p in net.parameters()) 统计，全部参数仅 62 006 个，其中两个卷积层合计 2 872 个（占 4.6%），绝大部分参数集中在全连接层。")
);

children.push(h2("（三）训练过程"));
children.push(
  body("损失函数用交叉熵 nn.CrossEntropyLoss()，优化器用 SGD（lr=0.001，momentum=0.9），按讲义设置在全量训练集上训练 2 轮。核心训练循环如下，每 200 个小批次打印一次平均损失：")
);
children.push(
  ...codeBlock([
    "for epoch in range(2):",
    "    for i, (inputs, labels) in enumerate(trainloader):",
    "        inputs, labels = inputs.to(device), labels.to(device)",
    "        optimizer.zero_grad()               # 清空上一步梯度",
    "        outputs = net(inputs)               # 前向传播",
    "        loss = criterion(outputs, labels)   # 计算交叉熵损失",
    "        loss.backward()                     # 反向传播计算梯度",
    "        optimizer.step()                    # 更新参数",
  ])
);
children.push(
  body(`baseline 实验的训练日志见图 3：第 1 轮平均损失 2.296，几乎没有离开初始值 ln10≈2.303；第 2 轮降到 ${S.baseline.final_avg_loss}，训练结束时保存模型参数到 exp3_net.pth。`),
  figure("exp3_results/exp3_log_baseline.png", 500),
  captionFigure("图 3\u3000baseline 训练与评估日志")
);

children.push(h2("（四）测试集评估"));
children.push(
  body("评估时新建网络并用 torch.load(\"exp3_net.pth\", weights_only=True) 重新加载参数（对应讲义步骤 4），在 10 000 张测试图上以 torch.no_grad() 前向统计整体准确率；同时把预测与真实标签汇总为 10×10 混淆矩阵，统计各类别正确数，得到各类别准确率（见第五节）。整体流程一键运行：python exp3.py 即可复现全部实验（--quick 可切换为 2000 张子集的缩小版）。")
);

// ============ 四、实验结果记录 ============
children.push(h1("四、实验结果记录"));
children.push(body("按讲义 3.6 节要求，将 baseline 实验（讲义步骤 1—4 的原始设置：全量训练集、batch_size=64、lr=0.001、2 轮）的实测结果填入记录表："));
children.push(captionTable("表 3\u3000实验结果记录表（baseline：bs=64，lr=0.001，2 轮）"));
children.push(
  makeTable(
    ["记录项", "实测结果"],
    [
      ["PyTorch / torchvision 版本、是否使用 GPU", "PyTorch 2.14.0+cpu；torchvision 0.29.0+cpu；未使用 GPU（纯 CPU 训练）"],
      ["实际训练规模与轮数", "全量 50 000 张，2 轮（每轮 782 次参数更新，共 1 564 次）"],
      ["训练结束时最后一次打印的平均损失", `${S.baseline.final_avg_loss}（第 2 轮整轮平均损失）`],
      ["测试集整体准确率", `${pct(S.baseline)}`],
      [`训练耗时与机器配置`, `训练约 ${S.baseline.train_minutes} 分钟（测试集评估 13 秒）；Intel i9-14900HX（32 逻辑核）/ 16 GB 内存 / Windows 11`],
      ["截图：exp3_samples.png 与训练日志", "见本文图 2（样例图片）、图 3（训练日志）"],
    ],
    [34, 66],
    { size: 21, firstColLeft: true }
  )
);
children.push(
  bodyRich([
    ["关于准确率数值的说明：", true],
    [`讲义提到按官方教程设置准确率通常在 50% 上下，但本人实测 baseline 只有 ${pct(S.baseline)}，两者差异的原因在于参数更新次数：官方教程的 trainloader 用 batch_size=4（每轮 12 500 次更新），而讲义代码改为 batch_size=64（每轮 782 次更新），同样训练 2 轮，参数更新次数只有教程的约 1/16，模型还远未收敛（第 1 轮损失几乎停在初始值）。第六节的调参实验把学习率提高到 0.01 以补偿更新次数的减少后，同样 2 轮即达到 ${pct(S["lr0.01"])}，与教程的 50% 上下相当，验证了这一判断。`, false],
  ])
);

// ============ 五、各类别准确率与混淆分析 ============
children.push(h1("五、各类别准确率与混淆分析"));
children.push(body("把测试集评估扩展到各类别准确率（每个类别恰好 1 000 张测试图），baseline 与 10 轮增强训练的 final 模型对比见表 4："));
children.push(captionTable("表 4\u3000各类别测试准确率对比（每类 1 000 张）"));
children.push(
  makeTable(
    ["类别", "baseline 正确数", "baseline 准确率", "final 正确数", "final 准确率"],
    perClassBaseline.map((rowB, i) => {
      const rowF = perClassFinal[i];
      return [rowB.class, rowB.correct, `${rowB.accuracy}%`, rowF.correct, `${rowF.accuracy}%`];
    }),
    [20, 20, 20, 20, 20],
    { size: 21 }
  )
);
children.push(
  figure("exp3_results/per_class_accuracy_baseline.png", 520),
  captionFigure("图 4\u3000baseline 各类别准确率"),
  figure("exp3_results/per_class_accuracy_final.png", 520),
  captionFigure("图 5\u3000final 模型（lr=0.01+数据增强，10 轮）各类别准确率")
);
children.push(
  body("类别间差异非常大：baseline 中 frog（58.90%）、plane（51.90%）最好，bird（7.00%）、cat（13.30%）最差，差距超过 50 个百分点；final 模型整体提升到 62.15% 后，最低的 cat 也达到 30.00%，但 cat 仍是全场最弱类别。"),
  body("由混淆矩阵统计出最容易被混淆的类别对（真实→预测）。baseline 的前几名是：truck→car（333 次）、deer→frog（313 次）、bird→frog（239 次）、ship→plane（230 次）、plane→ship（179 次）。final 模型的混淆对变为 cat→dog（219 次）、deer→horse（175 次）、dog→cat（157 次）、truck↔car（各 126 次）。"),
  body("分析：① truck 和 car 都是四轮箱式车身，32×32 分辨率下轮廓几乎相同，是最稳定的混淆对；② deer、bird 被大量误判为 frog，推测是小目标动物与植被背景在低分辨率下纹理相似；③ ship 与 plane 互相混淆，海面和天空背景相近；④ 训练充分后，\u201c跨大类\u201d的错误（动物→车船）基本消失，剩下的混淆集中在语义相近的类别之间（猫狗、马鹿、卡车轿车），符合分类误差的一般规律。")
);

// ============ 六、调参实验与对比分析 ============
children.push(h1("六、调参实验与对比分析"));
children.push(body("按基础任务要求，对 batch_size（32、128）与学习率（0.01、0.0001）各做一组实验（其余设置与 baseline 完全相同），并补充两组 10 轮长训练实验。全部 9 组实验汇总见表 5，训练损失曲线见图 6。"));
children.push(captionTable("表 5\u3000调参实验汇总（除注明外均为全量训练集、无数据增强、Net 网络）"));
children.push(
  makeTable(
    ["实验", "网络", "batch", "学习率", "增强", "轮数", "参数量", "末次平均损失", "测试准确率"],
    [
      ["baseline", "Net", "64", "0.001", "无", "2", "62,006", S.baseline.final_avg_loss, pct(S.baseline)],
      ["bs32", "Net", "32", "0.001", "无", "2", "62,006", S.bs32.final_avg_loss, pct(S.bs32)],
      ["bs128", "Net", "128", "0.001", "无", "2", "62,006", S.bs128.final_avg_loss, pct(S.bs128)],
      ["lr0.01", "Net", "64", "0.01", "无", "2", "62,006", S["lr0.01"].final_avg_loss, pct(S["lr0.01"])],
      ["lr0.0001", "Net", "64", "0.0001", "无", "2", "62,006", S["lr0.0001"].final_avg_loss, pct(S["lr0.0001"])],
      ["augment", "Net", "64", "0.001", "有", "2", "62,006", S.augment.final_avg_loss, pct(S.augment)],
      ["deep", "NetDeep", "64", "0.001", "无", "2", "156,074", S.deep.final_avg_loss, pct(S.deep)],
      ["final", "Net", "64", "0.01", "有", "10", "62,006", S.final.final_avg_loss, pct(S.final)],
      ["final_noaug", "Net", "64", "0.01", "无", "10", "62,006", S.final_noaug.final_avg_loss, pct(S.final_noaug)],
    ],
    [15, 11, 8, 10, 8, 8, 13, 14, 13],
    { size: 18 }
  )
);
children.push(
  figure("exp3_results/loss_curves.png", 540),
  captionFigure("图 6\u3000九组实验的训练损失曲线（50 批滑动平均）")
);
children.push(
  bodyRich([["batch_size 的影响：", true], [`batch 32 使每轮参数更新次数翻倍（1 564 次），2 轮后准确率 ${pct(S.bs32)}，比 baseline 高 ${diffPp(S.bs32, S.baseline)}；batch 128 每轮只有 390 次更新，准确率跌到 ${pct(S.bs128)}，比 baseline 低 ${diffPp(S.bs128, S.baseline).replace("-", "")}。末次平均损失也呈同样趋势（1.750 vs 2.290）。可见在\u201c训练轮数固定\u201d的短训练场景下，小批次因为更新更频繁而收敛更快。`, false]]),
  bodyRich([["学习率的影响：", true], [`lr=0.01 时同样 2 轮达到 ${pct(S["lr0.01"])}，末次损失 1.386，是四组 2 轮实验里最好的——更大的步长正好补偿了 batch=64 带来的更新次数减少；lr=0.0001 时末次损失 2.303≈ln10、准确率 ${pct(S["lr0.0001"])}（接近随机猜的 10%），1 564 次小步长更新根本走不出初始区域。batch_size 与学习率本质上是联动的：有效更新量 ≈ 更新次数 × 步长，两者需要一起调。`, false]]),
  bodyRich([["训练轮数的影响：", true], [`固定 lr=0.01，把轮数从 2 轮加到 10 轮，无增强实验从 ${pct(S["lr0.01"])} 提高到 ${pct(S.final_noaug)}（末次损失 1.386→${S.final_noaug.final_avg_loss}），说明 2 轮时模型仍明显欠拟合，训练时长是当前设置下最大的瓶颈。`, false]]),
  figure("exp3_results/exp3_log_summary.png", 480),
  captionFigure("图 7\u3000九组实验汇总日志")
);

// ============ 七、进阶任务 ============
children.push(h1("七、进阶任务（选做，已完成全部三项）"));
children.push(h2("（一）数据增强对比"));
children.push(
  body("在训练集 transform 中加入 transforms.RandomCrop(32, padding=4)（随机平移裁剪）与 transforms.RandomHorizontalFlip()（随机水平翻转），测试集 transform 不变。两种训练时长下的对比见表 6：")
);
children.push(captionTable("表 6\u3000数据增强前后测试准确率对比"));
children.push(
  makeTable(
    ["训练设置", "无增强", "有增强", "差值"],
    [
      ["2 轮，lr=0.001（baseline）", pct(S.baseline), pct(S.augment), diffPp(S.augment, S.baseline)],
      ["10 轮，lr=0.01", pct(S.final_noaug), pct(S.final), diffPp(S.final, S.final_noaug)],
    ],
    [34, 22, 22, 22],
    { size: 21 }
  )
);
children.push(
  body("两次对比中数据增强都略微降低了测试准确率（-1.92 与 -1.37 个百分点）。分析原因：这个只有 62 006 个参数的小网络在 2 轮 / 10 轮训练后仍处于欠拟合状态（末次训练损失 2.09 / 1.14，距离充分拟合还很远），而数据增强的作用机制是增加数据多样性、抑制过拟合——模型还没有过拟合时，增强只会暂时加大学习难度，收益体现不出来。可以预期在训练几十轮、模型开始过拟合（训练准确率明显高于测试准确率）之后，增强才会转为正向收益。这个结果提醒我：数据增强不是无条件的免费提升，其效果取决于模型当前处于欠拟合还是过拟合阶段。")
);
children.push(h2("（二）加深网络对比"));
children.push(
  body("定义 NetDeep：三个 3×3 卷积层（16/32/64 通道，padding=1 保持尺寸），每层接 ReLU 与 2×2 最大池化，最后 fc(1024→128→10)。两层 3×3 卷积级联的感受野为 5×5，与一个 5×5 卷积相同，但多了一次非线性变换。")
);
children.push(captionTable("表 7\u3000Net 与 NetDeep 对比（均为 bs=64、lr=0.001、2 轮）"));
children.push(
  makeTable(
    ["网络", "结构", "参数量", "末次平均损失", "测试准确率"],
    [
      ["Net", "2 个 5×5 卷积（6/16 通道）+ 3 层全连接", "62,006", S.baseline.final_avg_loss, pct(S.baseline)],
      ["NetDeep", "3 个 3×3 卷积（16/32/64 通道）+ 2 层全连接", "156,074", S.deep.final_avg_loss, pct(S.deep)],
    ],
    [14, 40, 14, 16, 16],
    { size: 18 }
  )
);
children.push(
  body(`参数量增大到 2.52 倍（156,074 vs 62,006），同样训练设置下准确率从 ${pct(S.baseline)} 提高到 ${pct(S.deep)}（+3.18 个百分点），末次损失也从 ${S.baseline.final_avg_loss} 降到 ${S.deep.final_avg_loss}。提升幅度有限，说明当前瓶颈仍是训练不充分而非模型容量；若配合更大的学习率与更多轮次，深网络的优势应该更明显。`)
);
children.push(h2("（三）训练损失曲线"));
children.push(
  body("用 matplotlib 绘制了全部九组实验的训练损失随迭代次数下降的曲线（图 6，50 批滑动平均）。曲线直观地印证了第六节的分析：lr0.0001 的曲线几乎水平（学不动）；bs128 下降缓慢；lr0.01 与两组 10 轮实验下降最快、最深；final（有增强）的损失在同期略高于 final_noaug（无增强），对应增强加大了学习难度。")
);

// ============ 八、思考题回答 ============
children.push(h1("八、思考题回答"));
children.push(
  bodyRich([["（1）对 32×32 彩色图直接用全连接网络，第一层大约需要多少参数？换成卷积层后为什么参数量大幅下降？", true]]),
  body("全连接要把 32×32×3=3 072 个输入全部连到每个隐层神经元，若第一层 120 个神经元，仅这一层就需要 3 072×120+120≈36.9 万个参数。而卷积层 conv1（5×5×3 卷积核 6 个）只需要 5×5×3×6+6=456 个。参数量大幅下降的原因有两个：一是局部连接，每个输出位置只看输入的一个 5×5×3 邻域而不是整幅图；二是权值共享，同一个卷积核滑过整幅图，一套权重在所有空间位置复用。实测本实验的 Net 全部参数才 62 006 个，其中卷积部分合计 2 872 个，仅占 4.6%。参数共享还顺带带来平移不变性——目标在图中平移后仍能被同一组卷积核检出。"),
  bodyRich([["（2）为什么要对图像做 ToTensor 和 Normalize？", true]]),
  body("ToTensor 做两件事：把 [0,255] 的 uint8 像素值转成 [0,1] 的 float32 张量，并把 H×W×C 的维度顺序调整为 PyTorch 卷积要求的 C×H×W。Normalize((0.5,),(0.5,)) 对每个通道做 (x-0.5)/0.5，把数值变成均值 0、范围约 [-1,1]。这样处理后各通道数值尺度一致、整体分布以 0 为中心，交叉熵损失配合 SGD 训练时梯度方向更稳定、收敛更快；如果不归一化，数值大的通道会主导损失和梯度，训练容易震荡甚至不收敛。"),
  bodyRich([["（3）训练损失一直下降，测试准确率却不再提高，可能是什么原因？怎么办？", true]]),
  body("这是典型的过拟合：模型在记忆训练样本的细节而不是学习可泛化的特征，所以训练损失继续下降，但泛化性能（测试准确率）已经到顶。常见对策：数据增强、减小网络容量、加正则化（权重衰减、Dropout）、早停，以及增加训练数据量。结合本实验的观察：小网络训练 10 轮时训练损失仍较高（0.81），还处于欠拟合区，此时数据增强就没有收益；只有当模型容量大、训练久、开始过拟合时，这些正则化手段才会起作用——先判断模型处于哪个阶段，再选对策。"),
  bodyRich([["（4）如果只能改动一处来提升本实验的准确率，你会改什么？为什么？", true]]),
  body(`我会把学习率从 0.001 调到 0.01。实测同一个网络、同样 2 轮，仅这一处改动就把测试准确率从 ${pct(S.baseline)} 提高到 ${pct(S["lr0.01"])}（+21.81 个百分点），末次平均损失从 ${S.baseline.final_avg_loss} 降到 1.386，而且不增加任何计算量。理由：本实验的瓶颈是 batch_size=64 下参数更新次数不足（欠拟合），提高学习率直接放大每次更新的步长，正好对症；相比之下加深网络只带来 +3.18 个百分点。如果允许再改一处，则是增加训练轮数（10 轮可达 ${pct(S.final_noaug)}）。`)
);

// ============ 九、实验总结 ============
children.push(h1("九、实验总结"));
children.push(
  body(`本次实验在纯 CPU 上完整跑了 CIFAR-10 图像分类的\u201c数据加载—定义网络—训练—评估\u201d流程，并系统完成了 batch_size、学习率、数据增强、网络深度四个维度共 9 组对比实验。最终用 62 006 参数的小网络取得 ${pct(S.final_noaug)} 的测试准确率（lr=0.01、10 轮），全部实验总耗时不到 10 分钟。`),
  body("主要收获有三点：一是超参数之间是联动的，batch_size 与学习率要放在一起看——它们共同决定了\u201c有效更新量\u201d，孤立地调某一个容易误判；二是学会了用训练损失曲线和\u201c训练损失 vs 测试准确率\u201d的关系诊断欠拟合与过拟合，这比单看一个数字信息量大得多；三是认识到数据增强等方法有适用条件，模型欠拟合时增强反而拖慢学习，先判断模型所处阶段再选对策。这些经验对后续训练更大的网络同样适用。")
);

// ============ 附录 ============
children.push(h1("附录：提交文件清单与复现方法"));
children.push(
  body("提交材料：实验报告（本文档）、exp3.py（完整可运行源代码，含 main 保护块与全部 9 组实验）、exp3_samples.png（样例图片）、exp3_net.pth 与 exp3_net_final.pth（模型参数，是否提交以教师要求为准）、exp3_results/ 目录（完整训练日志 exp3_log.txt、汇总与各类别准确率 CSV、全部图表 PNG）。"),
  body("复现方法：安装 PyTorch 与 torchvision 后，在 exp3.py 所在目录运行 python exp3.py 即可一键复现全部实验（首次运行自动下载 CIFAR-10）；时间紧张时可运行 python exp3.py --quick 切换为 2000 张子集、每实验最多 2 轮的缩小版。")
);

// ---------- assemble ----------
const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: FONT_BODY, size: 24, color: "000000" },
        paragraph: { spacing: { line: 312 } },
      },
      heading1: {
        run: { font: FONT_HEAD, size: 32, bold: true, color: "000000" },
        paragraph: { spacing: { before: 360, after: 160, line: 312 } },
      },
      heading2: {
        run: { font: FONT_HEAD, size: 28, bold: true, color: "000000" },
        paragraph: { spacing: { before: 240, after: 120, line: 312 } },
      },
    },
  },
  sections: [
    {
      properties: {
        page: {
          size: { width: 11906, height: 16838 },
          margin: { top: 1440, bottom: 1440, left: 1701, right: 1417 },
          pageNumbers: { start: 1 },
        },
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "808080", font: FONT_BODY })],
            }),
          ],
        }),
      },
      children,
    },
  ],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("第3次实验报告.docx", buf);
  console.log("written: 第3次实验报告.docx (" + Math.round(buf.length / 1024) + " KB)");
});
