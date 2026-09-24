# 病例规模不再是主要推断瓶颈的边界：估计目标、监测杠杆与流感住院实证

本目录为该论文的干净交付版，所有脚本路径均为相对路径，可在本目录内自洽复现全部结果。

## 目录结构

```
paper_final/
├── data/        CDC NHSN 周度流感住院原始数据（24 MB CSV，50 州 + 华盛顿特区，2020-08 至 2026-09）
├── simulations/ 全部计算脚本与统计量输出
│   ├── run_theory_simulations.py            图1：理论命题蒙特卡洛验证（50,000 次，种子 20260924）
│   ├── run_detection_simulations.py         图2：增长判定检验功效（30,000 次，种子 20260924）
│   ├── run_forecasting_crossover_simulations.py  图3：更新过程预测误差（150 轨迹×26 起点，种子 20260925）
│   ├── run_empirical_flu_analysis.py        图4 + 全部实证统计量（含仿射 FGLS、cluster bootstrap、误差预算分解、滚动交叉点）
│   └── empirical_stats.json                 论文第 5 节全部数字的唯一数据来源
├── theory/      propositions_and_proofs.md  命题 1–6 的推导底稿
├── figures/     fig1–fig4（PDF 投稿版 + PNG 预览版）
└── paper/       论文正文（LaTeX 为权威版本；docx 为按学报模板派生的交付件，修订时以 main.tex 为准）
    ├── main.tex           LaTeX 源（Tectonic 编译，xelatex 兼容）— 权威版本
    ├── main.pdf           编译产物（20 页）
    ├── main_docx.docx     按学报模板重写的 Word 版（含 OMML 公式、原生表格、3 图）
    ├── references.bib     11 条参考文献
    └── build_docx.py      docx 生成脚本（officecli batch，可重跑）
```

## 复现步骤

```bash
cd simulations
python run_empirical_flu_analysis.py   # 约 20 s，重算 empirical_stats.json + 图4
python run_theory_simulations.py       # 图1
python run_detection_simulations.py    # 图2
python run_forecasting_crossover_simulations.py  # 图3
cd ../paper
tectonic main.tex                      # 编译 LaTeX（xelatex 亦可）
python build_docx.py                   # 需 officecli，重新生成 docx
```

依赖：Python 3.10+，numpy / scipy / pandas / matplotlib；LaTeX 编译需 Tectonic 或 XeLaTeX（中文 ctex）；docx 生成需 officecli ≥ 1.0。

## 关键结果（与 empirical_stats.json 一一对应）

- 初期波段仿射拟合：b = 2.2434（95% CI [1.50, 3.02]），a = 0.0991，经验交叉点 22.6 例/周
- 误差预算分解：环境底板 54.6% / 规模项 45.1%，扩大捕获的反事实天花板约 41%
- 达峰期：常数基准偏差占 88.9%；控制后规模项 b = 7.9272，交叉点右移至 119.2
- 时变交叉点：流感季窗口中位数 20.4 vs 非流感季 46.9（251 个 26 周滚动窗口）
