---
title: 新稿代码与结果
date: 2026 年 10 月 14 日
---

# 新稿代码与结果

本文件夹收录新稿《病例规模与再生数估计精度：环境波动下的收益边界及美国流感住院数据检验》第二轮修订版（`paper.pdf`，20 页）所用的研究代码、数据和结果，可以整体下载。所有脚本只用本文件夹内的相对路径，解压到任意位置都能直接运行。

LaTeX 源码和论文终稿配图不在这里，它们随论文发布在 `../paper/` 下（`main.tex`、`sections/`、`figures/`、`bibliography.bib`）。本轮逐条修改的内容见 `../新稿_第二轮修改说明.md`。

## 目录

```text
新稿_代码与结果/
├── README.md
├── paper.pdf                      当前发布版论文的副本
├── code/
│   ├── figstyle.py                出图样式、字体与路径设置（其余脚本都从这里取路径）
│   ├── prep_nhsn.py               NHSN 原始数据 → 全国周序列与分箱结果
│   ├── sim_theory.py              图 2–4 的理论量与蒙特卡洛模拟
│   ├── make_figures.py            图 2–10 的作图脚本
│   └── checks/                    理论与数值核验脚本 c01–c12，_common.py 为公用工具
├── data/
│   ├── raw/Weekly_Hospital_Respiratory_Data_Metrics_by_Jurisdiction.csv   NHSN 州级周数据（24 MB）
│   ├── empirical_stats.json       原仓库实证分析的输出（拟合、重抽区间、外部数据）
│   └── derived/
│       ├── national_weekly.csv    prep_nhsn.py 生成的全国周序列
│       └── nhsn_bins.json         prep_nhsn.py 生成的初期与峰期分箱
└── results/
    ├── sim_theory.json            sim_theory.py 的输出
    ├── fig_records.json           make_figures.py 的出图记录（尺寸、嵌入字体）
    └── checks/                    c01–c12 的核验结论，c12 另有逐项数值 c12_eq15_derivation_detail.json
```

脚本运行时会在本文件夹下新建 `figures/`（作图输出）和 `logs/`（运行日志），下载包里不预置这两个目录。

## 依赖

- Python 3.10 及以上。本包在 Python 3.11.2 下测试，所用包的版本为 numpy 2.4.6、pandas 3.0.6、scipy 1.17.1、sympy 1.13.1、matplotlib 3.11.2、fonttools 4.66.0、pypdf 6.19.0。matplotlib 至少需要 3.6，因为需要逐字形字体回退。
- 安装命令：`pip install numpy pandas scipy sympy matplotlib fonttools pypdf`。
- 字体：图中西文用 Liberation Serif，汉字用 Noto Serif CJK SC。`code/figstyle.py` 开头的 `FONT_FILES` 和 `CJK_TTC` 写的是 Debian/Ubuntu 上的默认路径，其他系统请改成本机的字体文件路径。找不到字体文件时，脚本会跳过逐字形检查，照常出图，但图中字体可能被 matplotlib 换成默认字体。
- 可选：安装 poppler-utils 后，脚本会用 `pdffonts` 核对 PDF 的嵌入字体；未安装时跳过这一项。

## 复现

以下命令都在本文件夹内执行。

```bash
cd code
python3 prep_nhsn.py              # 约 1 秒,重写 data/derived/ 下的两个文件
python3 sim_theory.py             # 约 2 秒,重写 results/sim_theory.json
python3 make_figures.py           # 画全部 9 张数据图到 figures/;只画部分图可写 python3 make_figures.py fig04 fig09
cd checks
python3 c12_eq15_derivation.py    # 约 1 秒,式 (15) 推导核验;其余 c01–c11 用法相同,每个都在 15 秒以内
```

随机种子都写在脚本里，重跑的结果与 `results/` 中的文件一致。交付前在一份副本上完整重跑过一遍，对照结果如下：

- `national_weekly.csv`、`nhsn_bins.json`、`sim_theory.json` 与原文件逐字节一致。
- 图 2、图 4、图 7、图 10 的 PNG 与论文所用图逐像素一致。
- c01、c03 至 c12 的核验结论与原文件完全一致。c02 有 3 条记录的数值误差在 1e-15 量级上略有不同，属于浮点舍入，判定不变。

`make_figures.py` 输出的文件名沿用写作时的编号，例如 `fig09_mx_forest`。论文按出现顺序重新编了号，对照见下表。

## 每张图对应的脚本与数据

| 论文图号 | 论文中的位置 | 作图函数与输出文件名 | 输入 |
|---|---|---|---|
| 图 1 | 第 1 节，研究框架 | 不由代码生成，为概念示意图 | 无 |
| 图 2 | 第 3.2 节 | `fig02` → `fig02_variance_theory` | `results/sim_theory.json` 的 `variance_mc`（10 个规模各 20,000 次，种子 20261013） |
| 图 3 | 第 4.2 节 | `fig03` → `fig03_growth_test` | `results/sim_theory.json` 的 `growth_test`（负二项分布精确计算） |
| 图 4 | 第 5.2 节 | `fig04` → `fig04_renewal_scale` | `results/sim_theory.json` 的 `renewal`（每个初始规模 400 条轨迹，种子 20261014） |
| 图 5 | 第 6.1 节 | `fig05` → `fig05_nhsn_series` | `data/derived/national_weekly.csv` |
| 图 6 | 第 6.2 节 | `fig06` → `fig06_early_scale` | `data/derived/nhsn_bins.json` 的 `early_bins`，`data/empirical_stats.json` 的 `early` |
| 图 7 | 第 6.3 节 | `fig10` → `fig10_denominator_noise` | `empirical_stats.json` 的 `lag_weights_sensitivity`，`results/checks/c10_random_denominator.json` |
| 图 8 | 第 6.4 节 | `fig07` → `fig07_peak_decomp` | `nhsn_bins.json` 的 `peak_bins`，`empirical_stats.json` 的 `early` |
| 图 9 | 第 6.4 节 | `fig08` → `fig08_reporting_policy` | `empirical_stats.json` 的 `policy` |
| 图 10 | 第 6.5 节 | `fig09` → `fig09_mx_forest` | `empirical_stats.json` 的 `early`、`peak`、`lag_weights_sensitivity`、`competing_baselines`、`rolling_origin`、`seasonal_subsample_iv`、`extended_validation_flusight`、`extended_validation_covid19` |

## 关键数字的出处

| 论文中的数字 | 位置 | 来源 |
|---|---|---|
| 流行初期 b=2.243，经验交叉点 22.6 | 第 6.2 节、图 6 | `data/empirical_stats.json` 的 `early`；算术一致性见 `results/checks/c09_empirical.json` |
| 损失离散程度 5.32 降到 0.99 | 第 6.2 节 | `data/empirical_stats.json` 的 `early.var_structure` |
| 式 (15) 预测值 1.155、1.660、0.993，模拟值 1.195、1.566、0.999 | 第 6.3 节、图 7 | `results/checks/c10_random_denominator.json`（模拟以样本均值归一化，每种权重 18,000 次） |
| 峰期损失的 88.9% 来自基准偏移 | 第 6.4 节、第 7.1 节 | `data/empirical_stats.json` 的 `peak`；`prep_nhsn.py` 运行时会复核并打印该比例 |
| 峰期自身基准下交叉点 119.2 | 第 6.4 节 | `data/empirical_stats.json` 的 `peak` |
| FluSight 交叉点 60.3，峰期偏差占比 15.5% | 第 6.5.5 节、第 7.1 节 | `data/empirical_stats.json` 的 `extended_validation_flusight`，其中 15.5% 来自 `phase_decomposition`（峰期均值偏差平方 0.0709 除以相对均方误差 0.4583） |
| 欧洲 COVID-19 交叉点 124.7 | 第 6.5.5 节 | `data/empirical_stats.json` 的 `extended_validation_covid19` |
| 附录 A.8 中的 0.021（1.8%）、0.555 和 0.461、1.223、1.159、1.155、1.972 | 附录 A.8 | `results/checks/c12_eq15_derivation.json`（检查 12.4、12.6、12.7），全部数值见 `c12_eq15_derivation_detail.json` |

## 核验脚本与论文的对应

`code/checks/` 中的脚本最初是为上一版文稿写的，脚本内部说明里的命题编号和行号沿用的是上一版。与新稿的对应如下：

| 脚本 | 新稿中的对象 |
|---|---|
| c01、c02 | 命题 1（当期再生数的有效估计）与附录 A.1、A.2 |
| c03 | 命题 2（跨期平均水平的方差）、交叉点定义、命题 3（报告率与覆盖面的不对称） |
| c04 | 命题 4（多期分配） |
| c05 | 推论 1（最优单期规模） |
| c06 | 第 5.1 节单步预测的误差分解 |
| c07 | 命题 5（精确增长检验）与图 3 |
| c08 | 第 5.2 节更新过程仿真与图 4 |
| c09 | 第 6 节实证数字与 `empirical_stats.json` 的算术一致性 |
| c10 | 第 6.3 节随机分母与式 (15)，图 7 |
| c11 | 第 6.2 节一步可行广义最小二乘的一致性与按州聚类的重抽区间 |
| c12 | 附录 A.8 式 (15) 的推导：sympy 推导、固定规模下的精确枚举和蒙特卡洛三层核验（本轮新增） |

## 本包没有重跑的部分

- `data/empirical_stats.json` 是原研究仓库中 `simulations/run_empirical_flu_analysis.py` 的输出，包括仿射拟合、1,500 次按州聚类重抽的区间、工具变量回归、FluSight 与欧洲 COVID-19 外部数据的结果。这个脚本还依赖原仓库中没有提交的外部验证中间文件，所以本包把它的输出作为输入数据收录，不重跑这一步。新代码只读取这个文件，不改动它。
- FluSight 各阶段的偏差分解（15.5% 等）只有 JSON 中的计算结果，原仓库里没有生成它的脚本。
- 图 1 是概念示意图，不由数据生成。
- 原工作区出图时还用了一个共享的重叠检查工具，检查图中文字之间、图例与参考线之间是否重叠。该工具不随本包分发，单独运行本包时这两项检查自动跳过，不影响出图结果。
