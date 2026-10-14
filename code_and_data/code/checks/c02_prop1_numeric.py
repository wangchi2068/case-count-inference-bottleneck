#!/usr/bin/env python3
"""命题 1 的数值核验:
(a) 确定性:把个体 NB(k,p) 的 pmf 做 n 次卷积、再乘二项抽稀矩阵,与 NB(nk,p*) 的 pmf 比较(不靠封闭性假设);
(b) 蒙特卡洛:逐个体抽 X_i(Poisson–Gamma 两步抽)、求和、二项抽稀,核对 Var(C/(ρn)) 与 Var(score) = I(R)。
每个配置的原始抽样次数 ≤ 2e5。"""
import numpy as np
from scipy import stats
from _common import Checker, rel

ck = Checker("c02_prop1_numeric", "命题 1:抽稀分布、方差与 Fisher 信息的数值核验")
rng = np.random.default_rng(20261012)

# (a) 确定性卷积
for (n, k, rho, R) in [(5, 0.35, 0.25, 1.15), (30, 0.1, 0.5, 1.5), (60, 2.0, 0.8, 0.8)]:
    p = k / (k + R)
    M = int(stats.nbinom.ppf(1 - 1e-13, n * k, p)) + 50  # I 的截断上界
    f1 = stats.nbinom.pmf(np.arange(M), k, p)
    fI = np.array([1.0])
    for _ in range(n):
        fI = np.convolve(fI, f1)[:M]
    # 二项抽稀:P(C=c) = Σ_I P(I) Binom(c; I, ρ)
    Igrid = np.arange(M)
    fC = np.zeros(M)
    for I, w in zip(Igrid, fI):
        if w < 1e-300:
            continue
        fC[: I + 1] += w * stats.binom.pmf(np.arange(I + 1), I, rho)
    target = stats.nbinom.pmf(np.arange(M), n * k, k / (k + rho * R))
    tv = 0.5 * np.abs(fC - target).sum()
    ck.record(f"2.a.{n}", f"卷积+抽稀 pmf vs NB(nk,p*) 总变差距离 (n={n},k={k},ρ={rho},R={R})", "≈0(数值误差级)",
              f"{tv:.2e}", "通过" if tv < 1e-8 else "不通过")

# (b) 蒙特卡洛,逐个体抽样
for (n, k, rho, R) in [(10, 0.35, 0.25, 1.15), (20, 0.1, 0.5, 1.5), (40, 2.0, 0.8, 0.8)]:
    reps = 200_000 // n
    nu = rng.gamma(shape=k, scale=1.0 / k, size=(reps, n))      # 个体传播力,均值 1、方差 1/k
    X = rng.poisson(R * nu)                                       # X_i | nu_i ~ Poisson(R nu_i)
    I = X.sum(axis=1)
    Cc = rng.binomial(I, rho)
    Rhat = Cc / (rho * n)
    v_th = R / (rho * n) + R**2 / (k * n)
    v_mc = Rhat.var(ddof=1)
    # 方差估计的 MC 标准误(用四阶矩):se(s²) ≈ sqrt((μ4 - σ⁴)/reps)
    se = np.sqrt((np.mean((Rhat - Rhat.mean())**4) - v_mc**2) / reps)
    z = (v_mc - v_th) / se
    ck.record(f"2.b.var.{n}", f"Var(C/(ρn)) MC vs 式 eq:var_prop1 (n={n},k={k},ρ={rho},R={R},reps={reps})",
              f"{v_th:.5f}", f"{v_mc:.5f}(比值 {v_mc / v_th:.4f},z={z:.2f})", "通过" if abs(z) < 3 else "不通过")
    ck.record(f"2.b.mean.{n}", "E[C/(ρn)] = R(无偏)", R, f"{Rhat.mean():.4f}",
              "通过" if abs(Rhat.mean() - R) < 4 * np.sqrt(v_th / reps) else "不通过")
    score = k * (Cc - rho * n * R) / (R * (k + rho * R))
    I_th = n / (R / rho + R**2 / k)
    ck.record(f"2.b.fisher.{n}", "Var(score) MC vs Fisher 信息 式 eq:fisher_info", f"{I_th:.4f}",
              f"{score.var():.4f}(比值 {score.var() / I_th:.4f})", "通过" if rel(score.var(), I_th) < 0.03 else "不通过")
    # 分布层面:MC 频数 vs NB(nk,p*) 卡方
    pst = k / (k + rho * R)
    cmax = int(stats.nbinom.ppf(0.995, n * k, pst))
    obs = np.bincount(np.minimum(Cc, cmax), minlength=cmax + 1)
    pm = stats.nbinom.pmf(np.arange(cmax), n * k, pst)
    exp_ = np.append(pm, 1 - pm.sum()) * reps
    keep = exp_ >= 5
    chi2 = (((obs - exp_)**2 / exp_)[keep]).sum()
    pval = stats.chi2.sf(chi2, keep.sum() - 1)
    ck.record(f"2.b.dist.{n}", "MC 的 C 分布 vs NB(nk,p*) 卡方拟合", "p > 0.001", f"χ²={chi2:.1f}, df={keep.sum()-1}, p={pval:.3f}",
              "通过" if pval > 1e-3 else "不通过")
ck.close()
