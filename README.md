# 病例规模不再是主要推断瓶颈的边界：估计目标、监测杠杆与流感住院实证

本目录为该论文的干净交付版，所有脚本路径均为相对路径，可在本目录内自洽复现全部结果。

## 目录结构

```
paper_final/
├── data/        CDC NHSN 周度流感住院原始数据（24 MB CSV，50 州 + 华盛顿特区，2020-08 至 2026-09）
├── simulations/ 全部计算脚本与统计量输出
│   ├── run_theory_simulations.py            图1：理论命题蒙特卡洛验证（50,000 次，种子 20260923）
│   ├── run_detection_simulations.py         图2：增长判定检验功效（30,000 次，种子 20260924，首次穿越计算驱动）
│   ├── run_forecasting_crossover_simulations.py  图3：更新过程预测误差（150 轨迹×26 起点，种子 20260925，无截尾干净实现）
│   ├── run_empirical_flu_analysis.py        图4 + 全部实证统计量（含仿射 FGLS、cluster bootstrap、竞争基线、IV、误差预算）
│   └── empirical_stats.json                 论文第 5 节全部数字的唯一数据来源（156+ 字段全固化）
├── theory/      propositions_and_proofs.md  命题 1–6 的全推导底稿（与正文命题 1–6 严格 1:1 对齐，含全证明）
├── figures/     fig1–fig4（PDF 投稿版 + PNG 预览版，含对数轴尾部离散与精确枚举图例）
└── paper/       论文正文（LaTeX 为权威版本；docx 为按学报模板派生的交付件，修订时以 main.tex 为准）
    ├── main.tex           LaTeX 源（Tectonic 编译，xelatex 兼容）— 权威版本
    ├── main.pdf           编译产物（27 页；从 paper/ 目录执行 tectonic main.tex）
    ├── main_docx.docx     按学报模板重写的 Word 版（含 OMML 公式、原生表格、3 图）
    ├── references.bib     33 条权威参考文献（含 DOI，覆盖超传播、更新过程、Fisher信息下界、状态空间、信度比、FluSight）（含 DOI，核对 Communications Physics 450）
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

- 初期波段仿射拟合：$b = 2.2434$（95% CI $[1.5019, 3.0161]$），$a = 0.0991$，经验交叉点 22.6 例/周
- 误差预算分解：仿射拟合中与规模无关项 54.6% / 规模项 45.1%；已实现的大规模观测（$D_t \ge 250$）误差为全体平均的 57.5%（约六成，0.104 对 0.181）
- 竞争预测基准对照（表 2）：Cori 2周窗基线（均值 0.2876，中位 0.0658）、3周窗基线（均值 0.2490，中位 0.0626）远优于朴素平移基准（均值 0.6367）；分规模箱呈现一致的严格单调下降；大规模段（$D_t \ge 100$）Cori 2周窗误差降至 0.0903（略低于常数阶段均值的 0.1032）；其拟合斜率 $b = 6.0637$（$m_\times = 74.7$）
- 预测偏差项分解：总损失中纯条件方差项贡献 125.2%（$b_{\text{var}} = 3.3553$），预测偏差项贡献 70.3%（$b_{\text{bias}} = 0.3416$），交叉项 -95.6%，澄清了时序更新过程对经验规模斜率的动态重加权机制
- 季节内/波段内独立 IV：排除跨季趋势混杂，2022–23（$F=277.4, b=3.28$）、2023–24（$F=464.8, b=2.19$）、2024–25（$F=503.3, b=3.61$）、全初期汇集（$F=1147.1, b=2.85$），第一阶段 F 均大于 270 且 $b_{\text{iv}} > b_{\text{ols}} > 0$
- 达峰期：常数基准偏差占总体损失 88.9%；控制后内部规模项仍显著为正（$b = 7.9272$）；共同分母与未归一化尺度比较表明达峰期点估计不高于初期（1.85 对 2.24，交互项 CI $[-2.27, 0.63]$ 含零）
- 时变交叉点：流感季窗口中位数 20.4 vs 非流感季 46.9（251 个 26 周滚动窗口）；滞后基准口径 19.7 vs 47.9
- 份额分解（与规模无关/规模）：回顾 54.8/45.2、全历史扩张窗 54.9/45.1、26 周池 39.1/60.9、逐州 41.3/58.7（%）
- 制度子段：早期高覆盖 2020-10~2022-09（$N=2627$, SD 0.628）、法定强制 2022-10~2024-04（$N=3382$, SD 0.620）
