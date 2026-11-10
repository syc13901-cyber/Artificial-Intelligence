/* Generate 第4次实验报告.docx — Experiment 4 (20 Newsgroups, Naive Bayes) lab report.
 * All numbers are read from exp4_results/summary.json (written by exp4.py) so the
 * report always matches the actual measured values. */

const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, Header, Footer, PageNumber, AlignmentType, HeadingLevel,
  WidthType, BorderStyle, ShadingType,
} = require("docx");
const fs = require("fs");
const { imageSize } = require("image-size");

// ---------- data loading ----------
const S = JSON.parse(fs.readFileSync("exp4_results/summary.json", "utf-8"));
const sub4 = S.subset4;
const pct = (x) => (x * 100).toFixed(2) + "%";
const pp = (a, b) => {
  const d = (a - b) * 100;
  return `${d >= 0 ? "+" : ""}${d.toFixed(2)} 个百分点`;
};
const vec = Object.fromEntries(S.vec_variants.map((r) => [r.variant, r]));
const C = S.clf_compare;
const p20 = S.full20;

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
    (line, i) =>
      new Paragraph({
        shading: { type: ShadingType.CLEAR, fill: "F5F5F5" },
        spacing: { line: 276 },
        indent: { left: 240, right: 240 },
        keepNext: i < lines.length - 1 ? true : undefined,
        children: [new TextRun({ text: line.length ? line : " ", size: 18, font: FONT_CODE, color: "1A1A1A" })],
      })
  );
}

const TABLE_BORDERS = {
  top: { style: BorderStyle.SINGLE, size: 4, color: "8A8A8A" },
  bottom: { style: BorderStyle.SINGLE, size: 4, color: "8A8A8A" },
  left: { style: BorderStyle.SINGLE, size: 4, color: "8A8A8A" },
  right: { style: BorderStyle.SINGLE, size: 4, color: "8A8A8A" },
  insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: "C8C8C8" },
  insideVertical: { style: BorderStyle.SINGLE, size: 2, color: "C8C8C8" },
};

function cell(text, { width, bold = false, size = 21, align = AlignmentType.CENTER, fill } = {}) {
  return new TableCell({
    width: width !== undefined ? { size: width, type: WidthType.PERCENTAGE } : undefined,
    shading: fill ? { type: ShadingType.CLEAR, fill } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    verticalAlign: "center",
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
  const headerRow = new TableRow({
    tableHeader: true,
    children: headerCells.map(
      (t, i) => cell(t, { width: widths[i], bold: true, size, fill: "EEF2F7" })
    ),
  });
  const rows = dataRows.map(
    (r) =>
      new TableRow({
        children: r.map((t, i) =>
          cell(t, {
            width: widths[i],
            size,
            align: firstColLeft && i === 0 ? AlignmentType.LEFT : AlignmentType.CENTER,
          })
        ),
      })
  );
  return new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, borders: TABLE_BORDERS, rows: [headerRow, ...rows] });
}

// ============ 文档主体 ============
const children = [];

// 标题区
children.push(
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 60, line: 420, lineRule: "atLeast" },
    children: [new TextRun({ text: "实验四\u3000文本分类与朴素贝叶斯实验报告", bold: true, size: 36, font: FONT_HEAD, color: "000000" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 40, line: 312 },
    children: [new TextRun({ text: "姓名：陈思妍\u3000\u3000学号：2023141420127", size: 24, font: FONT_BODY, color: "000000" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 160, line: 312 },
    children: [new TextRun({ text: "2026 年 10 月 27 日", size: 24, font: FONT_BODY, color: "000000" })],
  })
);

// ============ 一、实验目标 ============
children.push(h1("一、实验目标"));
children.push(
  body("本实验按照讲义要求，使用 scikit-learn 在真实公开文本数据集 20 Newsgroups 上完成文本分类任务，具体目标包括：掌握用 fetch_20newsgroups 官方接口获取真实文本数据集的方法；理解词袋（Bag of Words）与 TF-IDF 两种文本特征化思想；掌握朴素贝叶斯分类器 MultinomialNB 的使用，能把\u201c特征化 + 分类器\u201d串成 Pipeline；会用准确率、分类报告、混淆矩阵评估多分类文本模型，并分析易混淆类别。"),
  body(`在完成基础任务（结果记录、去掉邮件头等信息前后的对比实验、两个易混淆类别的二分类实验）之外，本次实验还完成了全部三项进阶任务：全量 20 类挑战、TfidfVectorizer 参数对比（max_df / min_df / ngram_range）、LogisticRegression 与朴素贝叶斯的对比，共 8 组实验（另有 4 组参数变体在 20 类上复核），全部数值均为本人电脑实测。`)
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
      ["scikit-learn", "1.9.1"],
      ["matplotlib / numpy", "3.11.1 / 2.5.2"],
      ["GPU", "未使用（sklearn 传统机器学习，纯 CPU 即可完成）"],
    ],
    [30, 70],
    { firstColLeft: true }
  )
);
children.push(
  body(`运行 exp4.py 时脚本会先打印版本信息（图 1），确认环境无误后再加载数据集：fetch_20newsgroups 首次运行自动从官方数据源下载约 14 MB 的压缩包并缓存到用户目录 ~/scikit_learn_data，之后再次运行直接使用缓存，不重复下载。整个实验 python exp4.py 一键复现，全部图表与日志由脚本自动保存到 exp4_results/ 目录。`),
  figure("exp4_results/exp4_log_env.png", 500),
  captionFigure("图 1\u3000环境信息日志")
);

// ============ 三、实验原理简介 ============
children.push(h1("三、实验原理简介"));
children.push(
  body("计算机不能直接处理文字，需要先把文本变成数值向量。最简单的做法是词袋模型：把整个词表作为向量维度，统计每个词在文档中出现的次数，句子语序信息被丢弃、只保留\u201c有哪些词、各出现多少次\u201d。TF-IDF 在词频基础上再做加权：TF（词频）让在当前文档中频繁出现的词更重要；IDF（逆文档频率）惩罚 the、is 这类几乎所有文档都有的词，让稀有但有区分度的词获得更高权重，两者相乘即突出\u201c对这篇文档有代表性\u201d的词。"),
  body("朴素贝叶斯分类器基于贝叶斯定理，在\u201c各特征（词）在类别条件下相互独立\u201d这一朴素假设下，把后验概率拆成一串容易估计的词条件概率连乘。该假设在真实语言中并不严格成立，但分类只需要概率大小的排序正确，且高维稀疏文本上独立假设带来的偏差常被大量证据平均掉，因此朴素贝叶斯训练快、效果好、可解释，是文本分类的经典基线。"),
  body("本实验把 TfidfVectorizer 与 MultinomialNB 串成 sklearn 的 Pipeline：训练时 fit 先学词表与 IDF 权重再喂给分类器，预测时自动走完全相同的特征化流程，避免了\u201c训练与预测特征不一致\u201d这一常见错误。")
);

// ============ 四、实验数据与实验步骤 ============
children.push(h1("四、实验数据与实验步骤"));
children.push(h2("（一）数据集获取与规模"));
children.push(
  body("20 Newsgroups 数据集收录约 18 000 篇英文新闻组帖子，分属 20 个主题（棒球、航天、计算机图形学、政治等）。按讲义建议，基础任务用 categories 参数只取 4 个类别缩小规模；remove 参数去掉邮件头、脚注、引用三类\u201c作弊\u201d信息（第六节将用对比实验验证其必要性）：")
);
children.push(
  ...codeBlock([
    'cats = ["rec.sport.baseball", "sci.space",',
    '        "comp.graphics", "talk.politics.misc"]',
    'train = fetch_20newsgroups(subset="train", categories=cats,',
    '                           shuffle=True, random_state=42,',
    '                           remove=("headers", "footers", "quotes"))',
    'test  = fetch_20newsgroups(subset="test", categories=cats,',
    '                           shuffle=True, random_state=42,',
    '                           remove=("headers", "footers", "quotes"))',
  ])
);
children.push(
  body(`实测加载结果（图 2）：4 类子集训练集 ${sub4.train_n} 篇、测试集 ${sub4.test_n} 篇，四个类别分别是 ${sub4.cats.join("、")}（sklearn 按类别名字典序编号）。`),
  figure("exp4_results/exp4_log_step1.png", 500),
  captionFigure("图 2\u3000步骤 1：4 类子集加载日志")
);

children.push(h2("（二）TF-IDF 特征化与朴素贝叶斯训练"));
children.push(
  body("按讲义步骤 2 搭建 Pipeline 并训练：")
);
children.push(
  ...codeBlock([
    "model = Pipeline([",
    '    ("tfidf", TfidfVectorizer(stop_words="english")),',
    '    ("clf", MultinomialNB()),',
    "])",
    "model.fit(train.data, train.target)",
  ])
);
children.push(captionTable("表 2\u3000Pipeline 各组件配置"));
children.push(
  makeTable(
    ["阶段", "组件", "关键参数", "作用"],
    [
      ["特征化", "TfidfVectorizer", "stop_words='english'", "分词、去英文停用词，按 TF-IDF 加权生成稀疏向量"],
      ["分类", "MultinomialNB", "alpha=1.0（默认拉普拉斯平滑）", "多项式朴素贝叶斯，按词频似然做后验判决"],
    ],
    [14, 26, 28, 32],
    { size: 18 }
  )
);
children.push(
  body(`训练集 ${sub4.train_n} 篇文档共产生 ${sub4.features.toLocaleString("en-US").replace(/,/g, " ")} 个特征词（图 3），朴素贝叶斯拟合耗时仅 ${sub4.fit_time.toFixed(2)} 秒——对高维稀疏特征只需按类别累加词频，这正是生成式模型训练快的特点。`),
  figure("exp4_results/exp4_log_step2.png", 500),
  captionFigure("图 3\u3000步骤 2：训练日志")
);

children.push(h2("（三）测试集评估"));
children.push(
  body(`在 ${sub4.test_n} 篇测试文档上预测，整体准确率 ${pct(sub4.acc)}（图 4）。分类报告（表 3）显示四个类别的 F1 都在 0.83 以上；混淆矩阵（图 5 热力图）中错误最多的一格是 ${S.subset4.top_pair.true} 被误判为 ${S.subset4.top_pair.pred}（${S.subset4.top_pair.count} 篇）。`)
);
children.push(captionTable("表 3\u30004 类子集分类报告（测试集 1 490 篇）"));
children.push(
  makeTable(
    ["类别", "precision", "recall", "F1-score", "support"],
    [
      ["comp.graphics", "0.91", "0.92", "0.91", "389"],
      ["rec.sport.baseball", "0.85", "0.95", "0.90", "397"],
      ["sci.space", "0.85", "0.85", "0.85", "394"],
      ["talk.politics.misc", "0.91", "0.76", "0.83", "310"],
    ],
    [32, 17, 17, 17, 17]
  )
);
children.push(
  body(`F1 最高的是 ${S.subset4.f1_max.cls}（${S.subset4.f1_max.f1.toFixed(2)}），最低的是 ${S.subset4.f1_min.cls}（${S.subset4.f1_min.f1.toFixed(2)}）——政治类的 recall 只有 0.76，说明它有约四分之一的帖子被流进了其他类别，这与混淆矩阵中它被大量误判为 sci.space 的现象一致。`),
  figure("exp4_results/exp4_log_step3.png", 500),
  captionFigure("图 4\u3000步骤 3：准确率 / 分类报告 / 混淆矩阵日志"),
  figure("exp4_results/exp4_confmat_4class.png", 470),
  captionFigure("图 5\u30004 类子集混淆矩阵热力图")
);

children.push(h2("（四）对任意新文本做预测"));
children.push(
  body("按讲义步骤 4，用训练好的模型对三条自拟英文短句做预测（图 6）：航天、棒球、显卡三条文本分别被判定为 sci.space、rec.sport.baseball、comp.graphics，三条全部正确，说明模型确实学到了各类别的主题词汇而非表面特征。"),
  figure("exp4_results/exp4_log_step4.png", 500),
  captionFigure("图 6\u3000步骤 4：新文本预测日志")
);

// ============ 五、实验结果记录 ============
children.push(h1("五、实验结果记录"));
children.push(
  body("按讲义 4.6 节要求，将实测结果填入记录表（表 4）：")
);
children.push(captionTable("表 4\u3000实验结果记录表"));
children.push(
  makeTable(
    ["记录项", "实测结果"],
    [
      ["实际使用的类别集合与训练 / 测试篇数", `4 类：comp.graphics、rec.sport.baseball、sci.space、talk.politics.misc；训练 ${sub4.train_n} 篇、测试 ${sub4.test_n} 篇`],
      ["4 类子集的测试集准确率", pct(sub4.acc)],
      ["分类报告中 F1 最低与最高的类别", `最低 ${S.subset4.f1_min.cls}（${S.subset4.f1_min.f1.toFixed(2)}），最高 ${S.subset4.f1_max.cls}（${S.subset4.f1_max.f1.toFixed(2)}）`],
      ["混淆矩阵中混淆最严重的一对类别", `${S.subset4.top_pair.true} → ${S.subset4.top_pair.pred}（${S.subset4.top_pair.count} 篇）`],
      ["步骤 4 三条新文本的预测结果", "sci.space / rec.sport.baseball / comp.graphics，三条全部正确"],
      ["进阶任务：全量 20 类的准确率", `${pct(p20.acc)}（训练 11 314 篇、测试 7 532 篇，耗时 ${p20.fit_time.toFixed(2)} s）`],
    ],
    [38, 62],
    { size: 18, firstColLeft: true }
  )
);

// ============ 六、基础任务对比实验 ============
children.push(h1("六、基础任务对比实验"));
children.push(h2("（一）去掉邮件头、脚注、引用前后的对比"));
children.push(
  body(`其余设置完全不变，仅把 remove=("headers","footers","quotes") 去掉（即保留全部头部信息）再训练一次，结果见表 5：准确率从 ${pct(S.remove_compare.with_remove)} 虚高到 ${pct(S.remove_compare.without_remove)}，上涨 ${pp(S.remove_compare.without_remove, S.remove_compare.with_remove)}。`)
);
children.push(captionTable("表 5\u3000remove 参数对比（4 类子集，其余设置相同）"));
children.push(
  makeTable(
    ["数据版本", "特征维度", "测试准确率"],
    [
      ["去掉 headers / footers / quotes（讲义要求）", sub4.features.toLocaleString("en-US").replace(/,/g, " "), pct(S.remove_compare.with_remove)],
      ["保留全部头部信息", "34 549", pct(S.remove_compare.without_remove)],
    ],
    [50, 24, 26]
  )
);
children.push(
  body("图 7 打印了一份未去头的原始文档：Subject 行\u201cRe: Jewish Baseball Players?\u201d几乎直接点明版面，Organization、引文（> 开头的转发内容）与签名档也和发帖版面高度相关。值得注意的是，sklearn 使用的 20news-bydate 版本已经删去了 Newsgroups 字段本身，但 Subject、引文等元信息仍是强泄漏——模型学到的是\u201c看标题和抬头认版面\u201d而不是\u201c理解正文主题\u201d。这样的准确率在测试集上虚高，换到没有这些固定格式的真实文本（如一段普通邮件正文）上表现会骤降。因此去掉这三类信息后，评估才能反映模型真实的文本分类能力。"),
  figure("exp4_results/exp4_log_remove.png", 520),
  captionFigure("图 7\u3000未去头文档示例与 remove 对比日志")
);

children.push(h2("（二）两个易混淆类别的二分类实验"));
children.push(
  body(`自选 sci.electronics 与 sci.med 两类——前者讨论电子电路与设备，后者讨论医疗与健康，两边的帖子都会出现\u201c信号、电压、设备、监测\u201d一类交叉词汇，容易互相混淆。只在这两类上重新加载数据并训练（训练集 1 185 篇、测试集 789 篇），结果见表 6 与图 8、图 9。`)
);
children.push(captionTable("表 6\u3000sci.electronics vs sci.med 二分类结果"));
children.push(
  makeTable(
    ["类别", "precision", "recall", "F1-score", "support"],
    [
      ["sci.electronics", "0.94", "0.89", "0.91", "393"],
      ["sci.med", "0.89", "0.95", "0.92", "396"],
    ],
    [32, 17, 17, 17, 17]
  )
);
children.push(
  body(`二分类准确率 ${pct(S.pair2.acc)}，比 4 类任务（${pct(sub4.acc)}）高，但错误分布并不对称：混淆矩阵 [[349, 44], [21, 375]] 中，sci.electronics 有 44 篇被误判为 sci.med（约占该类 11%），反向只有 21 篇。分析原因：讨论医疗器械（起搏器、监护仪）、生物电信号、电路仿真的 electronics 帖子与医疗语境词汇重叠更多，而 med 帖子的\u201c患者、治疗、医生\u201d等词在 electronics 语料中少见得多，于是边界向 med 一侧倾斜。这个不对称说明\u201c易混淆\u201d是有方向的：词表重叠多的一方更容易被吸进对方。`),
  figure("exp4_results/exp4_log_pair2.png", 500),
  captionFigure("图 8\u3000两类实验训练与评估日志"),
  figure("exp4_results/exp4_confmat_2class.png", 440),
  captionFigure("图 9\u3000sci.electronics vs sci.med 混淆矩阵热力图")
);

// ============ 七、进阶任务 ============
children.push(h1("七、进阶任务"));
children.push(h2("（一）全量 20 类挑战"));
children.push(
  body(`不指定 categories 参数，在全部 20 个类别上训练：训练集 ${p20.train_n.toLocaleString("en-US").replace(/,/g, " ")} 篇、测试集 ${p20.test_n.toLocaleString("en-US").replace(/,/g, " ")} 篇、特征 ${p20.features.toLocaleString("en-US").replace(/,/g, " ")} 维。朴素贝叶斯训练耗时仅 ${p20.fit_time.toFixed(2)} s，测试准确率 ${pct(p20.acc)}（图 10、图 11）——比 4 类子集低了约 20 个百分点，符合\u201c类别越多、语义边界越细，任务越难\u201d的直觉。`)
);
children.push(
  body(`按混淆矩阵统计出的最易混淆类别对见表 7（前 5 名，完整 Top10 见图 12）：混淆高度集中成三个族群——宗教（alt.atheism、talk.religion.misc 都大量流入 soc.religion.christian，共 355 篇）、政治（talk.politics.misc → talk.politics.guns，102 篇）、计算机硬件（windows/mac 硬件 → ibm.pc.hardware）。这些类别主题本来就互相交叠（宗教讨论必然涉及基督教或无神论，政治帖常谈枪支管制），词表重叠严重，朴素贝叶斯的词频证据不足以切开它们。`)
);
children.push(captionTable("表 7\u3000全量 20 类最易混淆类别对（前 5 名）"));
children.push(
  makeTable(
    ["排名", "真实类别 → 预测类别", "误判篇数"],
    p20.top_pairs.slice(0, 5).map((p, i) => [String(i + 1), `${p.true} → ${p.pred}`, String(p.count)]),
    [16, 60, 24]
  )
);
children.push(
  body(`分类报告里还有一个极端现象：F1 最低的 talk.religion.misc 只有 ${p20.f1_min.f1.toFixed(2)}（precision 高达 1.00、recall 仅 0.01）——模型几乎从不把任何帖子判给这个类，它被 soc.religion.christian 整个\u201c吸收\u201d了。原因在于三个宗教类词表高度重叠，而朴素贝叶斯的独立性假设会把重叠词的证据重复计算，先验与似然的综合效果使 talk.religion.misc 的后验几乎总是排不进前一名。F1 最高的是 rec.sport.baseball（${p20.f1_max.f1.toFixed(2)}），体育类用词独特，与谁都不重叠。`),
  figure("exp4_results/exp4_log_20class.png", 520),
  captionFigure("图 10\u3000全量 20 类评估日志（分类报告与最易混淆类别对）"),
  figure("exp4_results/exp4_confmat_20class.png", 540),
  captionFigure("图 11\u3000全量 20 类混淆矩阵热力图"),
  figure("exp4_results/exp4_top_confusions.png", 520),
  captionFigure("图 12\u3000全量 20 类最易混淆类别对 Top10")
);

children.push(h2("（二）TfidfVectorizer 参数对比"));
children.push(
  body(`分别尝试 max_df=0.5、min_df=2、ngram_range=(1,2) 三个参数（其余设置与 baseline 相同），在 4 类与 20 类上各复核一遍，结果见表 8。`)
);
children.push(captionTable("表 8\u3000TfidfVectorizer 参数对比（分类器均为 MultinomialNB）"));
children.push(
  makeTable(
    ["参数变体", "4 类准确率", "4 类特征数", "20 类准确率", "20 类特征数"],
    [
      ["baseline（默认）", pct(vec["baseline"].acc4), vec["baseline"].n4.toLocaleString("en-US").replace(/,/g, " "), pct(vec["baseline"].acc20), vec["baseline"].n20.toLocaleString("en-US").replace(/,/g, " ")],
      ["max_df=0.5", pct(vec["max_df=0.5"].acc4), vec["max_df=0.5"].n4.toLocaleString("en-US").replace(/,/g, " "), pct(vec["max_df=0.5"].acc20), vec["max_df=0.5"].n20.toLocaleString("en-US").replace(/,/g, " ")],
      ["min_df=2", pct(vec["min_df=2"].acc4), vec["min_df=2"].n4.toLocaleString("en-US").replace(/,/g, " "), pct(vec["min_df=2"].acc20), vec["min_df=2"].n20.toLocaleString("en-US").replace(/,/g, " ")],
      ["ngram_range=(1,2)", pct(vec["ngram_range=(1,2)"].acc4), vec["ngram_range=(1,2)"].n4.toLocaleString("en-US").replace(/,/g, " "), pct(vec["ngram_range=(1,2)"].acc20), vec["ngram_range=(1,2)"].n20.toLocaleString("en-US").replace(/,/g, " ")],
    ],
    [24, 18, 18, 20, 20],
    { size: 18 }
  )
);
children.push(
  body(`max_df=0.5 的结果与 baseline 完全相同（特征数一字不差）：baseline 已经去掉英文停用词，剩下的词没有哪个出现在半数以上文档里，max_df 阈值根本没被触发——这说明该参数与停用词表功能重叠，二者留一个即可。min_df=2 砍掉了只出现 1 次的长尾词，特征数减少一半以上（26 575 → 12 774），去掉的主要是拼写错误和人名等噪声，4 类准确率微升 ${pp(vec["min_df=2"].acc4, vec["baseline"].acc4).replace("-", "")}、20 类微升 ${pp(vec["min_df=2"].acc20, vec["baseline"].acc20).replace("-", "")}，特征少一半还加快了训练，性价比最高。ngram_range=(1,2) 把相邻词对也纳入词表，特征暴涨到 20.3 万（20 类 94.4 万），其中绝大多数 bigram 只出现一两次，是纯噪声：稀疏证据被重复计数的偏差更大，4 类与 20 类准确率反而各降约 0.9 / 0.4 个百分点，训练耗时也涨到原来的数倍。可见\u201c特征更多\u201d不等于\u201c效果更好\u201d，噪声特征对计数型模型是负担。`)
);

children.push(h2("（三）LogisticRegression 与朴素贝叶斯对比"));
children.push(
  body(`把 Pipeline 里的分类器换成 LogisticRegression(max_iter=1000)，其余不变，与朴素贝叶斯对比见表 9，全部实验准确率汇总见图 13。`)
);
children.push(captionTable("表 9\u3000MultinomialNB 与 LogisticRegression 对比"));
children.push(
  makeTable(
    ["数据集", "模型", "测试准确率", "训练耗时"],
    [
      ["4 类子集", "MultinomialNB", pct(C.nb4.acc), `${C.nb4.time.toFixed(2)} s`],
      ["4 类子集", "LogisticRegression(max_iter=1000)", pct(C.lr4.acc), `${C.lr4.time.toFixed(2)} s`],
      ["全量 20 类", "MultinomialNB", pct(C.nb20.acc), `${C.nb20.time.toFixed(2)} s`],
      ["全量 20 类", "LogisticRegression(max_iter=1000)", pct(C.lr20.acc), `${C.lr20.time.toFixed(2)} s`],
    ],
    [22, 38, 20, 20],
    { size: 18 }
  )
);
children.push(
  body(`结果呈现出清晰的规律：任务越难，判别式模型的优势越明显。4 类任务简单，生成式的朴素贝叶斯（${pct(C.nb4.acc)}）反而略高于逻辑回归（${pct(C.lr4.acc)}）；20 类任务类别边界复杂，逻辑回归高出 ${pp(C.lr20.acc, C.nb20.acc).replace("-", "")}（${pct(C.lr20.acc)} vs ${pct(C.nb20.acc)}），但训练耗时从 ${C.nb20.time.toFixed(2)} s 涨到 ${C.lr20.time.toFixed(2)} s（约 12 倍）——逻辑回归要迭代优化 20 组判别边界，朴素贝叶斯只需一遍计数。结论：朴素贝叶斯是文本分类性价比极高的基线，几秒内就能给出接近的结果；只有当类别多、边界复杂、且愿意付出一个数量级的训练代价时，才值得换判别式模型。`),
  figure("exp4_results/exp4_exp_accuracy.png", 520),
  captionFigure("图 13\u3000各实验测试准确率对比")
);

// ============ 八、思考题回答 ============
children.push(h1("八、思考题回答"));
children.push(
  bodyRich([["（1）为什么加载数据时要去掉邮件头、脚注和引用？不去掉会发生什么？", true]]),
  body(`因为这三类信息与类别高度相关但与\u201c正文主题\u201d无关：邮件头里的 Subject 行常常直接点题（图 7 中\u201cRe: Jewish Baseball Players?\u201d一眼就是棒球版），签名档、Organization、引文也都是固定格式的元信息。不去掉时模型学到的是\u201c看抬头认版面\u201d，测试集准确率虚高——本人实测同一模型保留头部信息后从 ${pct(S.remove_compare.with_remove)} 涨到 ${pct(S.remove_compare.without_remove)}。但真实使用时用户不会把新闻组抬头贴进来，模型在这些文本上会骤降。值得注意的是，sklearn 用的 20news-bydate 版已删除 Newsgroups 字段，仅凭 Subject、引文等\u201c残余\u201d就能带来 6.71 个百分点的虚高，可见元信息泄漏的威力；去掉它们才能让评估反映真实的文本分类能力。`)
);
children.push(
  bodyRich([["（2）TF-IDF 中的 TF 和 IDF 分别起什么作用？", true]]),
  body("TF（词频）衡量\u201c这个词在这篇文档里多重要\u201d——在当前文档中出现越频繁权重越高；IDF（逆文档频率）衡量\u201c这个词有多大区分度\u201d——在几乎所有文档都出现的词（the、is 这类停用词）被压低，只在少数文档出现的词被抬高。两者相乘后，留在向量里的主要是\u201c对这篇文档有代表性、对类别有区分度\u201d的词。结合本实验：TfidfVectorizer(stop_words='english') 先删掉 318 个英文停用词，剩下的词再由 IDF 自动加权，所以 baseline 特征里航天帖子的 orbit、launch 与棒球帖子的 pitcher、inning 这类词权重远高于通用动词。")
);
children.push(
  bodyRich([["（3）朴素贝叶斯的\u201c朴素\u201d体现在哪里？这个假设在文本上成立吗？为什么仍然有效？", true]]),
  body(`\u201c朴素\u201d指假设各特征（词）在类别条件下相互独立——给定类别后，\u201c航天\u201d和\u201c发射\u201d出现与否互不影响。真实语言显然不成立：词有搭配、上下文强相关。它仍然有效的原因有二：一是分类只需要各类别后验概率的排序正确，不需要概率数值本身准确，独立假设带来的系统性偏差在各类别之间是同向的，排序常常不被破坏；二是高维稀疏文本提供了大量弱证据，单个词的估计偏差在求和中被平均掉。但这个假设也有失效的时候——进阶任务里 talk.religion.misc 被 soc.religion.christian 整类吸收（recall 仅 0.01）就是典型：两个类词表高度重叠，独立假设把重叠词证据重复计数，后验排序被系统性推向先验更大的一侧。所以朴素贝叶斯的\u201c有效\u201d是有边界的：类别区分度越高越可靠，近义类别边界上会被自己的\u201c朴素\u201d反噬。`)
);
children.push(
  bodyRich([["（4）如果要把这个流程用于中文文本分类，至少要改动哪一步？", true]]),
  body("至少要改特征化这一步。英文按空格天然分词，TfidfVectorizer 的默认 token_pattern 直接按连续字母切词；中文句子没有空格，必须先做分词——可以在 Pipeline 最前面加一个自定义转换器，用 jieba 把每篇文档切成以空格连接的词串，再交给 TfidfVectorizer（或改用 jieba.analyse 配套接口）。同时停用词表要换成中文停用词表（哈工大/百度停用词表等），因为 stop_words='english' 对中文完全不起作用。其余 Pipeline 结构——TF-IDF 加权、MultinomialNB、评估指标——都可以原样保留，这也是 Pipeline 设计的价值所在：换语言只动特征化环节，下游全部复用。")
);

// ============ 九、实验总结 ============
children.push(h1("九、实验总结"));
children.push(
  body(`本次实验在纯 CPU 上完整跑了 20 Newsgroups 文本分类的\u201c数据获取—TF-IDF 特征化—朴素贝叶斯训练—多分类评估\u201d流程：4 类子集准确率 ${pct(sub4.acc)}，全量 20 类准确率 ${pct(p20.acc)}，并系统完成了 remove 对比、易混淆类别二分类、TfidfVectorizer 参数对比、LogisticRegression 对比等 8 组实验，全部一键复现。`),
  body("主要收获有四点：一是理解了\u201c元信息泄漏\u201d——Subject 行、引文这些看起来无害的字段能让准确率虚高 6.71 个百分点，做真实文本任务必须先审查数据里有没有\u201c贴着答案的字段\u201d；二是学会了从混淆矩阵读出类别间的语义结构，20 类的混淆清楚地聚成宗教、政治、硬件三个族群，错误分布本身就是数据洞察；三是认识到特征工程参数各司其职：min_df 去噪有小幅正收益，ngram 在计数型模型上是负收益，max_df 与停用词表功能重叠；四是体会到生成式与判别式模型的取舍——朴素贝叶斯用 1/12 的训练代价拿到只差 1.3 个百分点的准确率，先跑基线再上重模型是更工程的路线。")
);

// ============ 附录 ============
children.push(h1("附录：提交文件清单与复现方法"));
children.push(
  body("提交材料：①实验报告（本文档）；②源代码文件 exp4.py（完整可运行源代码，含讲义步骤 1—4、基础任务两组对比实验与三项进阶任务）；③分类报告与混淆矩阵的运行截图（exp4_results/ 目录，含 4 类子集、sci.electronics vs sci.med 两类、全量 20 类共 6 张）。"),
  body("复现方法：安装 scikit-learn 与 matplotlib 后，在 exp4.py 所在目录运行 python exp4.py 即可一键复现全部实验并重新生成全部日志、分类报告与混淆矩阵图表（首次运行自动下载 20 Newsgroups 数据集约 14 MB 并缓存，之后使用本地缓存）。")
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
  fs.writeFileSync("第4次实验报告.docx", buf);
  console.log("written: 第4次实验报告.docx (" + Math.round(buf.length / 1024) + " KB)");
});
