"""讲义《小论文理论详解与建议》的计算型插图。

全部数值由论文公式直接计算(参数取论文图 1 与第 515 行情景),不依赖仿真。
字体:本机无 Times New Roman / 宋体,拉丁字符用度量兼容的 Liberation Serif,
中文用 Noto Serif CJK SC(宋体风格);数学符号用 STIX(Times 风格)。
运行:python3 make_figs.py(在本目录内)。
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

OUT = Path(__file__).resolve().parent

plt.rcParams.update({
    "font.family": ["Liberation Serif", "Noto Serif CJK SC"],
    "mathtext.fontset": "stix",
    "font.size": 9,
    "axes.labelsize": 9,
    "axes.titlesize": 9.5,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": 0.6,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linewidth": 0.4,
    "lines.linewidth": 1.4,
    "axes.unicode_minus": False,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "pdf.fonttype": 42,
})

BLUE, GREEN, RED, TEAL, GREY = "#0F4D92", "#5BAF5B", "#B64342", "#42949E", "#767676"

# 论文图 1 参数
RBAR, VR, K, RHO = 1.15, 0.04, 0.35, 0.25
A = RBAR + RHO * (RBAR**2 + VR) / K
MX = A / VR


def save(fig, name):
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png", dpi=200)
    plt.close(fig)


def fig_variance_scale():
    m = np.logspace(0, 3.3, 400)
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.9), constrained_layout=True)

    ax = axes[0]
    ax.loglog(m, VR + A / m, color=BLUE, label="总方差")
    ax.loglog(m, A / m, color=RED, ls="--", lw=1.1, label="规模项 A/m")
    ax.loglog(m, np.full_like(m, VR), color=GREEN, ls="-.", lw=1.1, label="环境方差下限")
    ax.axvline(MX, color=GREY, lw=0.8, ls=":")
    ax.plot([MX], [2 * VR], "o", color=BLUE, ms=4)
    ax.annotate(f"$m_\\times={MX:.1f}$", xy=(MX, 2 * VR), xytext=(MX * 2.2, 0.35),
                fontsize=8, arrowprops=dict(arrowstyle="-", color=GREY, lw=0.6))
    ax.set_xlabel("(a) 期望报告规模 m = ρn(例/期)")
    ax.set_ylabel("目标 B 的估计方差")
    ax.set_ylim(0.01, 3)
    ax.legend(loc="upper right", frameon=False)

    ax = axes[1]
    share_env = 100 * m / (m + MX)
    share_scale = 100 - share_env
    halving = 100 / (2 * (1 + m / MX))
    ax.semilogx(m, share_scale, color=RED, ls="--", lw=1.1, label="规模项占比")
    ax.semilogx(m, share_env, color=GREEN, ls="-.", lw=1.1, label="环境项占比")
    ax.semilogx(m, halving, color=BLUE, label="规模翻倍带来的方差降幅")
    ax.axvline(MX, color=GREY, lw=0.8, ls=":")
    for mm, off in ((10, (4, 5)), (MX, (-34, -12)), (200, (-8, -13))):
        y = 100 / (2 * (1 + mm / MX))
        ax.plot([mm], [y], "o", color=BLUE, ms=3.5)
        ax.annotate(f"{y:.1f}%", xy=(mm, y), xytext=off, textcoords="offset points", fontsize=8)
    ax.set_xlabel("(b) 期望报告规模 m(例/期)")
    ax.set_ylabel("百分比(%)")
    ax.set_ylim(0, 105)
    ax.legend(loc="lower center", frameon=False, bbox_to_anchor=(0.5, 1.0), ncol=2)
    save(fig, "fig_variance_scale")


def fig_budget():
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.9), constrained_layout=True)
    ax = axes[0]
    m = np.logspace(0, 3.2, 400)
    for ratio, color, off in ((10, TEAL, (-46, 12)), (100, BLUE, (6, 12))):
        f = (ratio + m) * (VR + A / m)
        mstar = np.sqrt(ratio * MX)
        fmin = (np.sqrt(ratio * VR) + np.sqrt(A)) ** 2
        ax.semilogx(m, f / fmin, color=color, label=f"$c_0/c_1={ratio}$")
        ax.plot([mstar], [1.0], "o", color=color, ms=4)
        ax.annotate(f"$m^*={mstar:.1f}$", xy=(mstar, 1.0), xytext=off,
                    textcoords="offset points", fontsize=8, color=color)
    ax.set_ylim(0.9, 3.0)
    ax.set_xlim(2, 1600)
    ax.set_xlabel("(a) 单期期望报告规模 m(例/期)")
    ax.set_ylabel("相对最小值的方差倍数")
    ax.legend(loc="upper center", frameon=False)

    ax = axes[1]
    c0, c1, budget = 100.0, 1.0, 600.0
    Ts = np.arange(1, 6)
    ms = budget / Ts / c1 - c0 / c1
    var = (VR + A / ms) / Ts
    bars = ax.bar(Ts, var, color=[BLUE if t == 3 else "#B4C0E4" for t in Ts],
                  edgecolor="black", linewidth=0.5, width=0.6)
    for t, v, mm in zip(Ts, var, ms):
        ax.text(t, v + 0.0012, f"{v:.5f}", ha="center", va="bottom", fontsize=7.5)
        ax.text(t, 0.0015, f"m={mm:.0f}", ha="center", va="bottom", fontsize=7.5,
                color="white" if t == 3 else "black")
    cont = (np.sqrt(c0 * VR) + np.sqrt(c1 * A)) ** 2 / budget
    ax.axhline(cont, color=RED, ls="--", lw=0.9)
    ax.text(5.45, cont + 0.0008, "连续松弛下界", fontsize=7.5, color=RED, ha="right", va="bottom")
    ax.set_xticks(Ts)
    ax.set_xlabel("(b) 期数 T(c0 = 100,c1 = 1,预算 600)")
    ax.set_ylabel("跨期均值估计量的方差")
    ax.set_ylim(0, 0.052)
    ax.grid(axis="x", visible=False)
    save(fig, "fig_budget")


def fig_ar1():
    fig, ax = plt.subplots(figsize=(4.6, 2.9), constrained_layout=True)
    T = np.arange(8, 81)
    for r, color in ((0.3, TEAL), (0.5, BLUE), (0.8, RED)):
        exact = T * (1 + r) / (1 - r) - 2 * r * (1 - r**T) / (1 - r) ** 2
        approx = T * (1 + r) / (1 - r)
        ax.plot(T, 100 * (approx / exact - 1), color=color, label=f"$r={r}$")
    for t0 in (10, 26):
        r = 0.8
        e = t0 * (1 + r) / (1 - r) - 2 * r * (1 - r**t0) / (1 - r) ** 2
        y = 100 * (t0 * (1 + r) / (1 - r) / e - 1)
        ax.plot([t0], [y], "o", color=RED, ms=3.5)
        ax.annotate(f"{y:.1f}%", xy=(t0, y), xytext=(6, 4), textcoords="offset points", fontsize=8)
    ax.set_xlabel("观测期数 T")
    ax.set_ylabel("近似对环境项的高估幅度(%)")
    ax.set_ylim(0, 100)
    ax.legend(frameon=False, loc="upper right")
    save(fig, "fig_ar1_teff")


def crit(n, k, rho=RHO, alpha=0.05):
    return int(stats.nbinom.isf(alpha, n * k, k / (k + rho))) + 1


def power(n, k, delta, rho=RHO):
    c = crit(n, k, rho)
    return stats.nbinom.sf(c - 1, n * k, k / (k + rho * (1 + delta)))


def fig_power():
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.8), constrained_layout=True)
    k, delta = 0.35, 0.30
    ns = np.arange(450, 700)
    pw = np.array([power(n, k, delta) for n in ns])
    lv = np.array([stats.nbinom.sf(crit(n, k) - 1, n * k, k / (k + RHO)) for n in ns])
    ax = axes[0]
    ax.plot(ns, pw, color=BLUE, lw=0.9)
    ax.axhline(0.8, color=RED, ls="--", lw=0.8)
    first = next(n for n in range(1, 4000) if power(n, k, delta) >= 0.8)
    stable = first
    for n in range(first, first + 2000):
        if power(n, k, delta) < 0.8:
            stable = n + 1
    ax.axvline(first, color=GREY, ls=":", lw=0.8)
    ax.axvline(stable, color=GREY, ls="-.", lw=0.8)
    lo, hi = pw.min() - 0.01, pw.max() + 0.01
    ax.text(first - 4, lo + 0.008, f"首次 {first}", fontsize=7.5, ha="right")
    ax.text(stable + 4, lo + 0.008, f"稳定 {stable}", fontsize=7.5, ha="left")
    ax.set_ylim(lo, hi)
    ax.set_xlabel("(a) 上一代感染者数 n")
    ax.set_ylabel("精确检验功效")
    ax = axes[1]
    ax.plot(ns, lv, color=TEAL, lw=0.9)
    ax.axhline(0.05, color=RED, ls="--", lw=0.8)
    ax.set_ylim(min(0.040, lv.min() - 0.001), 0.0515)
    ax.set_xlabel("(b) 上一代感染者数 n")
    ax.set_ylabel("实际检验水平")
    save(fig, "fig_power_sawtooth")
    return first, stable


if __name__ == "__main__":
    print(f"A={A:.5f}  m_x={MX:.2f}")
    fig_variance_scale()
    fig_budget()
    fig_ar1()
    print("power first/stable:", fig_power())
