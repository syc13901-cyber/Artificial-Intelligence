# tools：实验报告与截图的生成管线

本目录是完成各次实验时使用的辅助脚本，用于把 `expN_results/` 里的日志与数值汇总渲染成控制台风格截图，并生成提交给课程的 docx 实验报告。**报告本身不入库**（见根 README 与 `.gitignore`），这些脚本只说明结果图与报告是如何生产的。

| 脚本 | 用途 |
|------|------|
| `make_log_screenshots.py` | 实验 3：用 PIL 把运行日志渲染成深色控制台风格截图（中文按宽 2 折行） |
| `render_exp4_screenshots.py` | 实验 4：日志截图渲染 |
| `render_exp5_screenshots.py` | 实验 5：日志截图渲染 |
| `generate_report.js` | 实验 3 报告生成（Node `docx` 包，数值读自 exp3_results） |
| `generate_report4.js` | 实验 4 报告生成（同上，数值读自汇总文件保证与实测一致） |
| `gen_report5.py` | 实验 5 极简版报告生成（python-docx，白纸黑字无定制版式） |
| `package.json` / `package-lock.json` | Node 脚本依赖（docx、image-size），`npm install` 后运行 |
