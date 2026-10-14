"""新稿数据图 fig02–fig10（matplotlib，全部中文标签）。

数据来源：
- empirical_stats.json（旧稿实证结果，数值以它为准）;
- derived/sim_theory.json（sim_theory.py:方差 MC、检验水平/功效的精确值、更新过程模拟）;
- derived/national_weekly.csv、derived/nhsn_bins.json（prep_nhsn.py，自原始 CSV 流式重建并已对账）;
- theory/checks/results/c10_random_denominator.json（随机分母核验）。
用法：python3 make_figures.py [fig02 fig03 ...]，缺省全画。每张图的检查记录追加到 derived/fig_records.json。
"""
from __future__ import annotations

import json
import sys

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

import figstyle as fs
from figstyle import C, CROSS, EMPIRIC, FLOOR, THEORY, ACCENT, ACCENT2

log = fs.logger("make_figures")
fs.apply_style()
ST = fs.load_stats()
SIM = json.loads((fs.RESULTS / "sim_theory.json").read_text())
BINS = json.loads((fs.DERIVED / "nhsn_bins.json").read_text())
BIN_LABELS = ["5–20", "20–50", "50–100", "100–250", "250–600", "600–5000"]
BIN_SHORT = ["5–20", "20–50", "50–100", "100–250", "250–600", "≥600"]

R_BAR, V_R, K, RHO = 1.15, 0.04, 0.35, 0.25
A = R_BAR + RHO * (R_BAR**2 + V_R) / K
M_X = A / V_R


def fig02():
    """方差分解与交叉点（理论参数 R̄=1.15, v_R=0.04, k=0.35, ρ=0.25）。"""
    mc = SIM["variance_mc"]["rows"]
    m = np.geomspace(0.8, 2000, 400)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=fs.WIDE, constrained_layout=True)

    ax1.plot(m, (R_BAR + RHO * R_BAR**2 / K) / m, color=THEORY, label="目标Ⅰ：Cramér–Rao 下界")
    ax1.plot(m, V_R + A / m, color=EMPIRIC, label="目标Ⅱ：$v_R + A/m$")
    ax1.axhline(V_R, color=FLOOR, ls=":", lw=1.0, label="环境底板 $v_R$")
    ax1.plot([M_X, M_X], [1e-3, 2 * V_R], color=CROSS, ls="--", lw=1.0)   # 交叉点处 V = 2v_R
    ax1.plot(M_X, 2 * V_R, "o", color=CROSS, ms=3.5)
    ax1.text(M_X * 1.12, 1.4e-3, f"$m_\\times={M_X:.1f}$", color=CROSS, fontsize=8)
    xm = [r["m"] for r in mc]
    ax1.plot(xm, [r["var_I"] for r in mc], "o", mfc="white", mec=THEORY, ms=4,
             label="目标Ⅰ：模拟")
    ax1.plot(xm, [r["var_II"] for r in mc], "s", mfc="white", mec=EMPIRIC, ms=4,
             label="目标Ⅱ：模拟")
    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.set_xlim(0.8, 2000)
    ax1.set_ylim(1e-3, 4)
    ax1.set_ylabel("估计量方差")
    fs.panel_xlabel(ax1, "a", "期望报告病例数 $m=\\rho n$（例/期）")
    ax1.legend(loc="upper right", fontsize=7.5, handlelength=1.8)

    share = V_R / (V_R + A / m)
    halving = 1 / (2 * (1 + m / M_X))
    ax2.plot(m, 100 * share, color=EMPIRIC, label="环境项占比")
    ax2.plot(m, 100 * halving, color=THEORY, label="翻倍降幅")
    ax2.axvline(M_X, color=CROSS, ls="--", lw=1.0)
    for mm in [10, M_X, 200]:
        h = 100 / (2 * (1 + mm / M_X))
        ax2.plot(mm, h, "o", color=THEORY, ms=4)
        ax2.text(mm * 1.15, h + 1.5, f"{h:.1f}%", ha="left", va="bottom", fontsize=7.5, color=THEORY)
    ax2.text(M_X * 1.12, 92, "$m_\\times$", color=CROSS, fontsize=8)
    ax2.set_xscale("log")
    ax2.set_xlim(0.8, 2000)
    ax2.set_ylim(0, 100)
    ax2.set_ylabel("环境项占总方差 / 规模翻倍的方差降幅（%）")
    fs.panel_xlabel(ax2, "b", "期望报告病例数 $m$（例/期）")
    ax2.legend(loc="center right", fontsize=7.5)
    ratios = [r["ratio_II"] for r in mc]
    log(f"fig02: m_x={M_X:.2f}, A={A:.4f}, MC/理论（目标Ⅱ） {min(ratios):.3f}–{max(ratios):.3f}")
    return fig


def fig03():
    """增长检验：实际水平与 80% 功效所需规模（全部精确计算）。"""
    g = SIM["growth_test"]
    cols = {"0.1": EMPIRIC, "0.35": ACCENT, "1.0": THEORY}
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=fs.WIDE, constrained_layout=True)
    for kk, col in cols.items():
        s = g["size"][kk]
        m = np.array(s["m"])
        sel = m <= 200
        ax1.plot(m[sel], 100 * np.array(s["wald"])[sel], "o", color=col, ms=1.6, mew=0,
                 label=f"Wald 检验，$k={kk}$")
        ax1.plot(m[sel], 100 * np.array(s["exact"])[sel], "o", color=FLOOR, ms=1.2, mew=0, alpha=0.6)
    ax1.axhline(5, color=C["black"], ls="--", lw=0.9)
    ax1.plot([], [], "o", color=FLOOR, ms=2.5, label="精确检验（三种 $k$）")
    ax1.plot([], [], ls="--", color=C["black"], lw=0.9, label="名义水平 5%")
    ax1.set_xscale("log")
    ax1.set_xlim(0.9, 210)
    ax1.set_ylim(0, 14)
    ax1.set_ylabel("实际检验水平（%）")
    fs.panel_xlabel(ax1, "a", "期望报告病例数 $m$（例）")
    ax1.legend(loc="upper right", fontsize=7.5, markerscale=1.8)

    for kk, col in cols.items():
        rows = g["required"][kk]
        d = [100 * r["delta"] for r in rows]
        ax2.plot(d, [r["m_stable"] for r in rows], "o-", color=col, ms=3, label=f"$k={kk}$")
    ax2.set_yscale("log")
    ax2.set_xlim(8, 62)
    ax2.set_ylabel("所需期望报告病例数 $m$（例）")
    fs.panel_xlabel(ax2, "b", "待检出的增长幅度 $\\delta$（%）")
    ax2.legend(loc="upper right", title="功效 80%，$\\alpha=5\\%$", title_fontsize=7.5)
    for kk in cols:
        r = {round(x["delta"], 3): x for x in g["required"][kk]}
        log(f"fig03: k={kk} δ=0.25 n_first={r[0.25]['n_first']} n_stable={r[0.25]['n_stable']}")
    return fig


def fig04():
    """更新过程模拟：按初始规模与按实现规模两种口径对照参照曲线。"""
    rn = SIM["renewal"]
    gr = rn["groups"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=fs.WIDE, constrained_layout=True)
    m = np.geomspace(4, 1200, 300)
    ax1.plot(m, (V_R + A / m) / R_BAR**2, color=THEORY, label="单代参照 $(v_R+A/m)/\\overline{R}^{\\,2}$")
    ax1.axhline(V_R / R_BAR**2, color=FLOOR, ls=":", lw=1.0, label="环境底板 $v_R/\\overline{R}^{\\,2}$")
    x = [g["m0"] for g in gr]
    y = np.array([g["mean"] for g in gr])
    se = np.array([g["se"] for g in gr])
    ax1.errorbar(x, y, yerr=1.96 * se, fmt="o", color=EMPIRIC, ms=4, capsize=2, lw=0.9,
                 label="更新过程模拟（95% 区间）")
    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.set_ylim(0.02, 3)
    ax1.set_ylabel("相对均方误差")
    fs.panel_xlabel(ax1, "a", "初始期望报告规模 $m_0$（例/周）")
    ax1.legend(loc="upper right", fontsize=7.5)

    b = rn["realised_bins"]
    xd = [r["mean_D"] for r in b]
    ratio = [r["ratio"] for r in b]
    err = [1.96 * r["se"] / r["mean_ref"] for r in b]
    ax2.axhline(1, color=FLOOR, ls="--", lw=0.9)
    ax2.errorbar(xd, ratio, yerr=err, fmt="s", color=EMPIRIC, ms=3.5, capsize=2, lw=0.9,
                 label="按实现规模 $D_t$ 分箱")
    big = [g for g in gr if g["m0"] >= 25]
    ax2.plot([g["m0"] for g in big], [g["ratio_init"] for g in big], "o", mfc="white",
             mec=THEORY, ms=4, label="按初始规模 $m_0$ 计（$m_0\\geq25$）")
    ax2.set_xscale("log")
    ax2.set_ylim(0.6, 1.4)
    ax2.set_ylabel("模拟误差 / 单代参照")
    fs.panel_xlabel(ax2, "b", "实现规模 $D_t$ 或初始规模 $m_0$（例/周）")
    ax2.legend(loc="lower left", fontsize=7.5)
    log("fig04: ratio_init(m0>=25) " + ", ".join(f"{g['m0']}:{g['ratio_init']:.3f}" for g in big))
    log("fig04: realised-bin ratio range "
        f"{min(ratio):.3f}–{max(ratio):.3f}; m0=6/12 ratio_init {gr[0]['ratio_init']:.2f}/{gr[1]['ratio_init']:.2f}"
        f" （SE/ref {gr[0]['se'] / gr[0]['ref_init']:.2f}/{gr[1]['se'] / gr[1]['ref_init']:.2f}，重尾）")
    return fig


def fig05():
    """全国周住院数与医院填报率。"""
    nat = pd.read_csv(fs.DERIVED / "national_weekly.csv", parse_dates=["week_end"])
    fig, ax = plt.subplots(figsize=(6.5, 2.8), constrained_layout=True)
    early = [("2022-10-08", "2022-11-26"), ("2023-10-14", "2023-12-16"), ("2024-11-09", "2025-01-18")]
    for a, b in early:
        ax.axvspan(pd.Timestamp(a), pd.Timestamp(b), color=C["green"], alpha=0.15, lw=0)
    ax.axvspan(pd.Timestamp("2024-05-01"), pd.Timestamp("2024-11-01"), color=C["lightgrey"], alpha=0.8, lw=0)
    ax.plot(nat.week_end, nat.admissions / 1000, color=EMPIRIC, lw=1.1)
    ax.set_ylabel("流感住院数（千例/周）")
    ax.set_ylim(0, None)
    ax2 = ax.twinx()
    ax2.spines["right"].set_visible(True)
    ax2.plot(nat.week_end, nat.coverage, color=THEORY, lw=0.9, ls="--")
    ax2.set_ylabel("医院填报率（%）")
    ax2.set_ylim(0, 105)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_xlabel("周末日期（年）")
    handles = [Line2D([], [], color=EMPIRIC, lw=1.1, label="51 个辖区住院数合计"),
               Line2D([], [], color=THEORY, lw=0.9, ls="--", label="平均填报率（右轴）"),
               Patch(color=C["green"], alpha=0.3, label="增长初期样本窗口"),
               Patch(color=C["lightgrey"], label="自愿填报期")]
    ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=4, fontsize=7.5)
    ax.set_ylim(0, nat.admissions.max() / 1000 * 1.08)
    log(f"fig05: weeks={len(nat)}, peak admissions={nat.admissions.max():.0f} "
        f"on {nat.loc[nat.admissions.idxmax(), 'week_end'].date()}")
    return fig


def fig06():
    """增长初期：分箱相对均方误差与 a + b/D 拟合。"""
    tab = ST["early"]["table"]
    af = ST["early"]["affine"]
    xD = [b["mean_D"] for b in BINS["early_bins"]]
    fig, ax = plt.subplots(figsize=fs.SINGLE, constrained_layout=True)
    y = np.array([t["mean"] for t in tab])
    lo = y - np.array([t["ci_lo"] for t in tab])
    hi = np.array([t["ci_hi"] for t in tab]) - y
    d = np.geomspace(5, 3000, 300)
    ax.plot(d, af["a"] + af["b"] / d, color=THEORY,
            label=f"加权拟合 $a+b/D$（$a={af['a']:.3f}$，$b={af['b']:.2f}$）")
    ax.axhline(af["a"], color=FLOOR, ls=":", lw=1.0, label="规模无关项 $a$")
    ax.errorbar(xD, y, yerr=[lo, hi], fmt="o", color=EMPIRIC, ms=4.5, capsize=2.5, lw=1.0,
                label="分箱均值（州聚类 95% 区间）")
    mx = af["m_x"]
    ax.axvline(mx, color=CROSS, ls="--", lw=1.0)
    ax.text(mx * 1.1, 0.40, f"$b/a={mx:.1f}$", color=CROSS, fontsize=8)
    for xi, yi, lab in zip(xD, y, BIN_LABELS):
        ax.text(xi, 0.056, lab, ha="center", va="bottom", fontsize=7, color=FLOOR)
    ax.text(5.6, 0.056, "分箱：", ha="left", va="bottom", fontsize=7, color=FLOOR)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(0.05, 0.6)
    ax.set_yticks([0.05, 0.1, 0.2, 0.3, 0.4, 0.5], ["0.05", "0.1", "0.2", "0.3", "0.4", "0.5"])
    ax.yaxis.set_minor_formatter(plt.NullFormatter())
    ax.set_xlim(5, 3000)
    ax.set_ylabel("周增长比的相对均方误差")
    ax.set_xlabel("实现规模 $D_t$（加权报告住院数，例/周）")
    ax.legend(loc="upper right", fontsize=7.5)
    log(f"fig06: a={af['a']:.4f} b={af['b']:.4f} b/a={mx:.2f}, bins mean_D " +
        ", ".join(f"{v:.1f}" for v in xD))
    return fig


def fig07():
    """达峰回落期：以增长初期均值为基准的误差拆成偏差与箱内波动。"""
    pk = BINS["peak_bins"]
    early = [t["mean"] for t in ST["early"]["table"]]
    x = np.arange(len(pk))
    bias = np.array([p["bias"] for p in pk])
    within = np.array([p["within"] for p in pk])
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=fs.WIDE, constrained_layout=True,
                                   gridspec_kw={"width_ratios": [1, 1]})
    ax1.bar(x, bias, 0.62, color=ACCENT, label="均值偏移（偏差项）")
    ax1.bar(x, within, 0.62, bottom=bias, color=C["sky"], label="箱内波动")
    ax1.plot(x, early, "D", color=C["black"], ms=4, label="增长初期同一分箱")
    ax1.set_xticks(x, BIN_SHORT, fontsize=7)
    ax1.set_ylim(0, max((bias + within).max(), max(early)) * 1.3)
    ax1.set_ylabel("相对均方误差")
    fs.panel_xlabel(ax1, "a", "实现规模分箱 $D_t$（例/周）")
    ax1.legend(loc="upper right", fontsize=7.5)

    share = 100 * np.array([p["bias_share"] for p in pk])
    ax2.bar(x, share, 0.62, color=ACCENT)
    for xi, si in zip(x, share):
        ax2.text(xi, si + 1.5, f"{si:.1f}", ha="center", va="bottom", fontsize=7.5)
    ax2.text(-0.4, 104, f"全样本 {100 * ST['peak']['bias_share']:.1f}%", ha="left", va="top", fontsize=7.5)
    ax2.set_xticks(x, BIN_SHORT, fontsize=7)
    ax2.set_ylim(0, 105)
    ax2.set_ylabel("偏差项占比（%）")
    fs.panel_xlabel(ax2, "b", "实现规模分箱 $D_t$（例/周）")
    log("fig07: bias share by bin " + ", ".join(f"{s:.1f}" for s in share))
    return fig


def fig08():
    """填报制度切换前后周增长比的离散程度。"""
    pol = ST["policy"]
    keys = ["period1_mandatory", "period2_voluntary", "period3_remandated"]
    names = ["强制填报期", "自愿填报期", "恢复强制期"]
    cols = [THEORY, EMPIRIC, CROSS]
    stats_ = [("g_std", "标准差"), ("g_iqr", "四分位距"), ("g_mad", "中位绝对偏差")]
    fig, ax = plt.subplots(figsize=fs.SINGLE, constrained_layout=True)
    x = np.arange(len(stats_))
    wd = 0.26
    for i, (k, nm, col) in enumerate(zip(keys, names, cols)):
        v = [pol[k][s] for s, _ in stats_]
        cov = pol[k]["coverage_mean"]
        ax.bar(x + (i - 1) * wd, v, wd, color=col,
               label=f"{nm}（$N={pol[k]['N']}$，填报率 {cov:.0f}%）")
        for xi, vi in zip(x + (i - 1) * wd, v):
            ax.text(xi, vi + 0.03, f"{vi:.2f}", ha="center", va="bottom", fontsize=7)
    bound = pol[keys[0]]["g_std"] * np.sqrt(pol[keys[0]]["coverage_mean"] / pol[keys[1]]["coverage_mean"])
    ax.hlines(bound, -0.45, 0.45, color=C["black"], ls="--", lw=1.0)
    ax.annotate(f"均匀漏报时标准差上界 {bound:.2f}", xy=(0.45, bound), xytext=(0.5, bound + 0.32),
                fontsize=7.5, ha="left", va="bottom", arrowprops=dict(arrowstyle="-", lw=0.6, color=C["black"]))
    ax.set_xticks(x, [n for _, n in stats_])
    ax.set_ylim(0, 2.3)
    ax.set_ylabel("周增长比的离散程度")
    ax.set_xlabel("离散度指标")
    ax.legend(loc="upper right", fontsize=7.5)
    log(f"fig08: SD bound {bound:.3f} = P1 SD × sqrt(91.1/54.6) = ×{bound / pol[keys[0]]['g_std']:.3f}; "
        f"observed ×{pol[keys[1]]['g_std'] / pol[keys[0]]['g_std']:.2f}")
    return fig


def fig09():
    """不同口径下的经验比值 b̂/â（经验交叉点）。"""
    lag = ST["lag_weights_sensitivity"]
    ro = ST["rolling_origin"]
    iv = ST["seasonal_subsample_iv"]
    cb = ST["competing_baselines"]
    fl = ST["extended_validation_flusight"]
    cv = ST["extended_validation_covid19"]["sensitivity_table"]
    flu = {r["rule"]: r for r in fl["sensitivity_table"]}
    rows = [
        ("NHSN 流感（主口径）", None),
        ("主估计：权重 0.65/0.25/0.10", (lag["original"]["m_x"], lag["original"]["m_x_ci"])),
        ("仅当周", (lag["single_1w"]["m_x"], lag["single_1w"]["m_x_ci"])),
        ("三周等权", (lag["equal_3w"]["m_x"], lag["equal_3w"]["m_x_ci"])),
        ("剔除最大 1% 损失", (ST["early"]["affine_trim1pct"]["m_x"], ST["early"]["affine_trim1pct"]["m_x_ci"])),
        ("工具变量（分阶段合并）", (iv["pooled_within_phase"]["m_x_iv"] if isinstance(iv["pooled_within_phase"], dict)
                           else iv["pooled_within_phase"], None)),
        ("滚动原点：全历史扩展", (ro["expanding_all"]["b"] / ro["expanding_all"]["a"], None)),
        ("滚动原点：26 周池", (ro["pool_26w"]["b"] / ro["pool_26w"]["a"], None)),
        ("滚动原点：分州扩展", (ro["state_expanding"]["b"] / ro["state_expanding"]["a"], None)),
        ("基准换为 Cori（2 周）", (cb["affine_cori_2w"]["m_x"], None)),
        ("基准换为 Cori（3 周）", (cb["affine_cori_3w"]["m_x"], None)),
        ("达峰回落期（条件均值）", (ST["peak"]["affine_cond"]["m_x"], ST["peak"]["affine_cond"]["m_x_ci"])),
        ("外部数据", None),
        ("FluSight 各州，事前规则", (fl["primary_states_exante"]["m_x"], fl["primary_states_exante"]["m_x_ci"])),
        ("FluSight 全部地区，事前规则", (flu["all_locations_exante"]["m_x"], None)),
        ("FluSight 各州，回溯规则", (flu["states_retro_c5"]["m_x"], None)),
        ("FluSight 全部地区，回溯规则", (flu["all_locations_retro_c5"]["m_x"], None)),
    ]
    covid_names = {"pure_exante_history": "COVID-19，纯事前历史",
                   "growth_phase_unbounded": "COVID-19，增长期不截断",
                   "original_truncated_subset": "COVID-19，原截断子集"}
    for r in cv:
        rows.append((covid_names[r["rule"]], (r["m_x"], None)))
    fig, ax = plt.subplots(figsize=(6.5, 5.2), constrained_layout=True)
    ax.axvspan(21.28, 49.18, color=C["green"], alpha=0.15, lw=0)
    main = lag["original"]["m_x"]
    ax.axvline(main, color=EMPIRIC, ls="--", lw=0.9)
    labels, ys = [], []
    y = 0
    for name, val in rows:
        if val is None:
            labels.append(name)
            ys.append(y)
            y += 1
            continue
        est, ci = val
        col = EMPIRIC if name.startswith("主估计") else C["black"]
        if ci:
            ax.plot(ci, [y, y], color=col, lw=1.1)
            ax.plot(est, y, "o", color=col, ms=4.5)
        else:
            ax.plot(est, y, "o", mfc="white", mec=col, ms=4.5)
        ax.text(330, y, f"{est:.1f}", va="center", ha="right", fontsize=7.5)
        labels.append("    " + name)
        ys.append(y)
        log(f"fig09: {name}: {est:.2f} {ci if ci else ''}")
        y += 1
    ax.set_yticks(ys, labels)
    for t, (name, val) in zip(ax.get_yticklabels(), rows):
        if val is None:
            t.set_fontweight("bold")
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlim(5, 340)
    ax.set_xticks([5, 10, 20, 50, 100, 200], ["5", "10", "20", "50", "100", "200"])
    ax.set_xlabel("经验比值 $b/a$（例/周，对数刻度）")
    handles = [Line2D([], [], marker="o", color=C["black"], lw=1.1, label="点估计与 95% 自助区间"),
               Line2D([], [], marker="o", mfc="white", mec=C["black"], lw=0, label="仅点估计"),
               Patch(color=C["green"], alpha=0.3, label="流感情景下的理论 $m_\\times$（21.3–49.2）")]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.4, 1.0), ncol=3, fontsize=8)
    return fig


def fig10():
    """分母噪声与回溯窗口：b 随 Σw² 变化、a 随平均滞后变化。"""
    lag = ST["lag_weights_sensitivity"]
    c10 = {r["id"]: r for r in json.loads((fs.CHECKS / "c10_random_denominator.json").read_text())["records"]}
    sw2 = {"single_1w": 1.0, "original": 0.495, "equal_3w": 1 / 3}
    meanlag = {"single_1w": 1.0, "original": 1.45, "equal_3w": 2.0}
    names = {"single_1w": "仅当周", "original": "主权重", "equal_3w": "三周等权"}
    mc_b = {"single_1w": 1.5663, "original": 1.1946, "equal_3w": 0.9987}      # c10 记录 10.3.*
    mc_a = {"single_1w": 0.0225, "original": 0.0202, "equal_3w": 0.0214}      # c10 记录 10.4.*
    for kk, v in mc_b.items():
        assert str(v) in c10[f"10.3.{ {'single_1w': 'single', 'original': 'original', 'equal_3w': 'equal'}[kk]}"]["observed"]
    b0, b1 = 0.6601, 1.6602 - 0.6601
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=fs.WIDE, constrained_layout=True)
    s = np.linspace(0.25, 1.05, 50)
    ax1.plot(s, b0 + b1 * s, color=THEORY, label="二项分母噪声的理论预测")
    ax1.axhline(b0, color=FLOOR, ls=":", lw=1.0, label="无分母噪声时的 $b$")
    for kk in sw2:
        e = lag[kk]
        ax1.errorbar(sw2[kk], e["b"], yerr=[[e["b"] - e["b_ci"][0]], [e["b_ci"][1] - e["b"]]], fmt="o",
                     color=EMPIRIC, ms=4.5, capsize=2.5, lw=1.0)
        ax1.plot(sw2[kk], mc_b[kk], "s", mfc="white", mec=THEORY, ms=4.5)
        ax1.text(sw2[kk] + 0.03, e["b"], names[kk], va="center", ha="left", fontsize=7.5)
    handles1 = [Line2D([], [], marker="o", color=EMPIRIC, lw=1.0, label="NHSN 实证（95% 区间）"),
                Line2D([], [], marker="s", mfc="white", mec=THEORY, lw=0, label="情景模拟")]
    h, l = ax1.get_legend_handles_labels()
    ax1.legend(handles=h + handles1, loc="upper left", fontsize=7.5)
    ax1.set_xlim(0.25, 1.25)
    ax1.set_ylim(0, 5.8)
    ax1.set_ylabel("规模项系数 $b$")
    fs.panel_xlabel(ax1, "a", "滞后权重平方和 $\\Sigma w^2$")

    for kk in meanlag:
        e = lag[kk]
        ax2.errorbar(meanlag[kk], e["a"], yerr=[[e["a"] - e["a_ci"][0]], [e["a_ci"][1] - e["a"]]], fmt="o",
                     color=EMPIRIC, ms=4.5, capsize=2.5, lw=1.0)
        ax2.plot(meanlag[kk], mc_a[kk], "s", mfc="white", mec=THEORY, ms=4.5)
        ax2.text(meanlag[kk] + 0.06, e["a"], f"{names[kk]} {e['a']:.3f}", va="center", ha="left", fontsize=7.5)
    ax2.axhspan(0.014, 0.029, color=C["green"], alpha=0.15, lw=0)
    ax2.text(2.55, 0.031, "情景隐含的 $a$ 范围", va="bottom", ha="right", fontsize=7.5, color=CROSS)
    ax2.set_xlim(0.8, 2.6)
    ax2.set_xticks([1.0, 1.5, 2.0, 2.5])
    ax2.set_ylim(0, 0.2)
    ax2.set_ylabel("规模无关项 $a$")
    fs.panel_xlabel(ax2, "b", "分母的平均回溯滞后（周）")
    for kk in sw2:
        log(f"fig10: {kk}: Σw²={sw2[kk]:.3f} b_emp={lag[kk]['b']:.4f} b_pred={b0 + b1 * sw2[kk]:.4f} "
            f"b_mc={mc_b[kk]} a_emp={lag[kk]['a']:.4f} a_mc={mc_a[kk]}")
    return fig


FIGS = {
    "fig02_variance_theory": fig02, "fig03_growth_test": fig03, "fig04_renewal_scale": fig04,
    "fig05_nhsn_series": fig05, "fig06_early_scale": fig06, "fig07_peak_decomp": fig07,
    "fig08_reporting_policy": fig08, "fig09_mx_forest": fig09, "fig10_denominator_noise": fig10,
}

if __name__ == "__main__":
    want = sys.argv[1:]
    rec_path = fs.RESULTS / "fig_records.json"
    recs = json.loads(rec_path.read_text()) if rec_path.exists() else {}
    for stem, fn in FIGS.items():
        if want and not any(stem.startswith(w) for w in want):
            continue
        log(f"--- {stem}")
        recs[stem] = fs.save(fn(), stem, log)
        rec_path.write_text(json.dumps(recs, ensure_ascii=False, indent=1))
