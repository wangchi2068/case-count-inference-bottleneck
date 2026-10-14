"""学位论文第二至四章新增的数据图。

只用新稿已有的参数定义(示例参数 R̄=1.15、v_R=0.04、k=0.35、ρ=0.25;推论 1 的
c0=100、c1=1、𝓑=600;AR(1) 系数 0.5/0.8),不改数据口径。图写到 thesis/figures,
图中数字写到 thesis/derived/thesis_figures.json,供正文引用。
"""
from __future__ import annotations

import json
import math

import numpy as np
from scipy import stats

import figstyle as fs

THESIS = fs.WORK / "thesis"
fs.FIG_DIR = THESIS / "figures"
OUT = THESIS / "derived"
OUT.mkdir(parents=True, exist_ok=True)

R_BAR, V_R, K, RHO = 1.15, 0.04, 0.35, 0.25
A = R_BAR + RHO * (R_BAR**2 + V_R) / K
M_X = A / V_R

log = fs.logger("thesis_figures")
fs.apply_style()
import matplotlib.pyplot as plt  # noqa: E402

rec: dict = {"params": {"R_bar": R_BAR, "v_R": V_R, "k": K, "rho": RHO,
                        "A": round(A, 5), "m_cross": round(M_X, 3)}}


# ---------- 图 2-1 负二项后代分布与传播集中度 ----------
def top_share(k: float, p: np.ndarray) -> np.ndarray:
    """个体再生数 ν~Gamma(k, R/k) 时,最具传染力的前 p 比例个体贡献的期望传播份额。
    份额 = P(ν>q_p) 在 ν 的尺寸偏倚分布 Gamma(k+1, R/k) 下的概率,与 R 无关。"""
    q = stats.gamma.ppf(1 - p, a=k)
    return stats.gamma.sf(q, a=k + 1)


ks = [0.1, 0.35, 1.0]
colors = [fs.ACCENT, fs.THEORY, fs.CROSS]
fig, axes = plt.subplots(1, 2, figsize=fs.WIDE)
x = np.arange(0, 9)
ax = axes[0]
pmf_rec = {}
for k, c in zip(ks, colors):
    pk = stats.nbinom.pmf(x, k, k / (k + R_BAR))
    ax.plot(x, pk, "o-", color=c, label=f"$k={k:g}$")
    pmf_rec[str(k)] = {"p0": round(float(pk[0]), 4),
                       "ratio_to_poisson_at_8": round(float(pk[8] / stats.poisson.pmf(8, R_BAR)), 1)}
pp = stats.poisson.pmf(x, R_BAR)
ax.plot(x, pp, "s--", color=fs.FLOOR, label="泊松")
pmf_rec["poisson"] = {"p0": round(float(pp[0]), 4)}
ax.set_yscale("log")
ax.set_ylim(1e-4, 1.2)
ax.set_ylabel("概率")
fs.panel_xlabel(ax, "a", "继发感染数")
ax.legend(loc="upper right")

ax = axes[1]
p = np.linspace(1e-4, 1, 400)
share_rec = {}
for k, c in zip(ks, colors):
    ax.plot(p, top_share(k, p), color=c, label=f"$k={k:g}$")
    share_rec[str(k)] = round(float(top_share(k, np.array([0.2]))[0]), 4)
ax.plot([0, 1], [0, 1], "--", color=fs.FLOOR, label="同质")
ax.axvline(0.2, color=fs.C["lightgrey"], lw=0.8, zorder=0)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1.02)
ax.set_ylabel("贡献的传播份额")
fs.panel_xlabel(ax, "b", "按传染力排序的感染者比例")
ax.legend(loc="lower right")
fs.fix_mixed(fig)
fig.tight_layout()
fs.save(fig, "fig_2_1_offspring", log)
rec["fig_2_1"] = {"R": R_BAR, "pmf": pmf_rec, "top20_share": share_rec}


# ---------- 图 3-4 报告率与覆盖面的边际效果之比 ----------
def lever_ratio(rho, k, rbar=R_BAR, vr=V_R):
    return 1 + rho * (rbar**2 + vr) / (k * rbar)


fig, ax = plt.subplots(figsize=fs.SINGLE)
rho = np.logspace(math.log10(0.003), 0, 300)
for k, c in zip(ks, colors):
    ax.plot(rho, lever_ratio(rho, k), color=c, label=f"$k={k:g}$")
ax.axvspan(0.0056, 0.021, color=fs.C["lightgrey"], alpha=0.7, lw=0, label="住院占感染比例")
ax.plot([RHO], [lever_ratio(RHO, K)], "D", color=fs.EMPIRIC, label="示例参数")
ax.set_xscale("log")
ax.set_ylim(0.8, 13.5)
ax.set_xlabel(r"报告率 $\rho$")
ax.set_ylabel(r"边际效果之比 $A/\overline{R}$")
ax.legend(loc="upper left")
fs.fix_mixed(fig)
fig.tight_layout()
fs.save(fig, "fig_3_4_levers", log)
rec["fig_3_4"] = {
    "example_ratio": round(lever_ratio(RHO, K), 4),
    "hospital_band_at_example_k": [round(lever_ratio(0.0056, K), 4), round(lever_ratio(0.021, K), 4)],
    "rho_ratio_2_at_example": round((K * R_BAR) / (R_BAR**2 + V_R), 4),
    "at_rho_1": {str(k): round(lever_ratio(1.0, k), 3) for k in ks},
}


# ---------- 图 4-1 预算分配:成本目标函数与 AR(1) 近似误差 ----------
c0, c1, budget = 100.0, 1.0, 600.0


def f_cost(m):
    return (c0 + c1 * m) * (V_R + A / m) / budget


m_star = math.sqrt(c0 / c1 * M_X)
fig, axes = plt.subplots(1, 2, figsize=fs.WIDE)
ax = axes[0]
m = np.linspace(5, 520, 600)
ax.plot(m, f_cost(m), color=fs.THEORY, label="连续松弛")
ints = []
for T in range(1, 6):
    mm = budget / T - c0
    v = (V_R + A / mm) / T
    ints.append({"T": T, "m": mm, "var": round(v, 5)})
ax.plot([d["m"] for d in ints], [d["var"] for d in ints], "o", color=fs.EMPIRIC, label="整数期数")
offs = {1: (-8, 6), 2: (4, 5), 3: (4, -12), 4: (-10, 7), 5: (5, 3)}
for d in ints:
    ax.annotate(f"$T={d['T']}$", (d["m"], d["var"]), textcoords="offset points",
                xytext=offs[d["T"]], fontsize=7.5)
ax.axvline(m_star, color=fs.CROSS, ls="--", lw=1.0, label=r"$m^*$")
ax.set_ylim(0.015, 0.05)
ax.set_ylabel("估计方差")
fs.panel_xlabel(ax, "a", "单期期望报告规模 $m$")
ax.legend(loc="upper center")

ax = axes[1]
Ts = np.arange(2, 101)
over = {}
for r, c in zip([0.5, 0.8], [fs.THEORY, fs.ACCENT]):
    exact = (1 + r) / (1 - r) - 2 * r * (1 - r**Ts) / (Ts * (1 - r) ** 2)
    ratio = (1 + r) / (1 - r) / exact - 1
    ax.plot(Ts, 100 * ratio, color=c, label=f"$r={r:g}$")
    over[str(r)] = {str(t): round(float(100 * ratio[t - 2]), 2) for t in (10, 26, 52)}
for t in (10, 26):
    v = over["0.8"][str(t)]
    ax.plot([t], [v], "o", color=fs.ACCENT)
ax.set_xscale("log")
ax.set_ylabel("近似高估环境项（%）")
fs.panel_xlabel(ax, "b", "观测期数 $T$")
ax.legend(loc="upper right")
fs.fix_mixed(fig)
fig.tight_layout()
fs.save(fig, "fig_4_1_budget", log)
rec["fig_4_1"] = {"c0": c0, "c1": c1, "budget": budget, "m_star": round(m_star, 3),
                  "f_m_star": round(f_cost(m_star), 5), "integer": ints,
                  "teff_overestimate_pct": over}

(OUT / "thesis_figures.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2))
log(json.dumps(rec, ensure_ascii=False))
