#!/usr/bin/env python3
"""第 4.2 节更新过程:式 eq:relmse_identity、式 eq:exact_renewal_decomp、翻倍降幅与图 3 文字中的数值;
按复现规格(第 421 行)做小规模更新过程仿真,检验「经验误差始终不低于单代下界」的表述。"""
import numpy as np
import sympy as sp
from _common import Checker

ck = Checker("c08_renewal", "更新过程:RelMSE 恒等式、条件偏差–方差分解与图 3 数值")

# ---- 恒等式 ----
C1, D, Rb = sp.symbols("C1 D Rbar", positive=True)
lhs = ((C1 - Rb * D) / (Rb * D))**2
rhs = (C1 / D - Rb)**2 / Rb**2
ck.record("8.1", "((C-R̄D)/(R̄D))² = (G-R̄)²/R̄²(式 eq:relmse_identity,逐观测成立)", 0, sp.simplify(lhs - rhs),
          "通过" if sp.simplify(lhs - rhs) == 0 else "不通过", "逐观测恒等 ⇒ 期望恒等;前提是两者用同一个 R̄、同一活跃周样本")
mu, sig2 = sp.symbols("mu sigma2", positive=True)
# 给定 F:E[(C/D-R̄)²|F] = Var(C|F)/D² + (μ/D-R̄)²,因 D 是 F 可测
EC2 = sig2 + mu**2
cond = sp.simplify(EC2 / D**2 - 2 * Rb * mu / D + Rb**2 - (sig2 / D**2 + (mu / D - Rb)**2))
ck.record("8.2", "D_t 为 F_t^C 可测时的条件偏差–方差分解(式 eq:exact_renewal_decomp)", 0, cond, "通过" if cond == 0 else "不通过",
          "外层再取 E[·|D_t>0] 并用塔式性质即得;对任一包含 σ(D_t) 的信息集都成立")

# ---- 图 3 文字中的数值 ----
v, A, Rbar = 0.04, 2.1232, 1.15
ref = lambda m: v + A / m
items = [("8.3", "m=6 参照值 v_R+A/6", 0.394, ref(6)),
         ("8.4", "m=6 参照相对损失 (v_R+A/6)/R̄²", 0.298, ref(6) / Rbar**2),
         ("8.5", "m=6 经验相对损失 0.718/R̄²", 0.543, 0.718 / Rbar**2),
         ("8.6", "m=6 经验/参照倍数", 1.82, (0.718 / Rbar**2) / (ref(6) / Rbar**2)),
         ("8.7", "m=12 参照值", 0.217, ref(12)),
         ("8.8", "环境底板 v_R/R̄²", 0.0302, v / Rbar**2),
         ("8.9", "首点 m=6→12 经验翻倍降幅 (0.718-0.190)/0.718", 0.735, (0.718 - 0.190) / 0.718)]
for cid, t, paper, val in items:
    dec = len(repr(paper).split(".")[1]) if "." in repr(paper) else 0
    ck.record(cid, t, paper, f"{val:.4f}", "通过" if abs(val - paper) <= 0.5 * 10**(-dec) + 1e-12 else "不通过",
              "按论文所报小数位四舍五入比较")
ck.record("8.10", "剔除率:3/3900、1/3900", "0.077%、0.026%", f"{100*3/3900:.3f}%、{100*1/3900:.3f}%",
          "通过" if abs(100 * 3 / 3900 - 0.077) < 0.0005 and abs(100 * 1 / 3900 - 0.026) < 0.0005 else "不通过")

# ---- 小规模更新过程仿真(按第 421 行规格;每组 1,000 条轨迹 × 30 周 ≤ 2e5 次抽样/组) ----
rng = np.random.default_rng(20261017)
w = np.array([0.45, 0.35, 0.15, 0.05])
k, rho, T, NTRAJ = 0.35, 0.25, 30, 1000
A_ = Rbar + rho * (Rbar**2 + v) / k
rows = []
for m0 in (6, 12, 25, 50, 100, 200):
    n0 = m0 / rho
    I = np.zeros((NTRAJ, T))
    C = np.zeros((NTRAJ, T))
    I[:, :4] = rng.poisson(n0, (NTRAJ, 4))   # 启动核:4 周期望规模 n0
    I[:, :4] = np.maximum(I[:, :4], 1)
    C[:, :4] = rng.binomial(I[:, :4].astype(np.int64), rho)
    for t in range(4, T):
        Lam = (I[:, t - 4:t][:, ::-1] * w).sum(axis=1)
        Rt = rng.gamma(Rbar**2 / v, v / Rbar, NTRAJ)
        It = rng.poisson(rng.gamma(k * Lam, Rt / k))
        I[:, t] = np.maximum(It, 1)        # 论文的 max(1, I) 截断
        C[:, t] = rng.binomial(I[:, t].astype(np.int64), rho)
    G, Dv, LHS_RB = [], [], []
    for t in range(3, T - 1):              # 预测起点 t(0 起算 3..28 ⇒ 26 个)
        Dt = (C[:, t - 3:t + 1][:, ::-1] * w).sum(axis=1)
        Lam1 = (I[:, t - 3:t + 1][:, ::-1] * w).sum(axis=1)
        ok = Dt > 0
        G.append(C[ok, t + 1] / Dt[ok])
        Dv.append(Dt[ok])
        # 以潜在全信息 H_t ⊇ σ(D_t) 为条件的分解右端(不含截断的近似条件矩)
        muH = rho * Lam1[ok] * Rbar
        s2H = rho * (1 - rho) * Lam1[ok] * Rbar + rho**2 * (Lam1[ok]**2 * v + Lam1[ok] * Rbar + Lam1[ok] * (Rbar**2 + v) / k)
        LHS_RB.append(s2H / Dt[ok]**2 + (muH / Dt[ok] - Rbar)**2)
    G, Dv, RB = np.concatenate(G), np.concatenate(Dv), np.concatenate(LHS_RB)
    mse = np.mean((G - Rbar)**2)
    se = np.std((G - Rbar)**2, ddof=1) / np.sqrt(G.size)
    ratio_init = mse / ref(m0)
    ratio_real = mse / np.mean(v + A_ / Dv)      # 以实际实现规模 D_t 计的参照
    rows.append((m0, mse, ref(m0), ratio_init, ratio_real, np.median(Dv) / m0))
    se_rb = np.std(RB, ddof=1) / np.sqrt(RB.size)
    zz = (RB.mean() - mse) / np.sqrt(se**2 + se_rb**2)
    ck.record(f"8.sim.dec.{m0}", f"更新过程 m={m0}:E[(G-R̄)²] 直接估计 vs 分解右端(全信息条件)", f"{mse:.4f}(SE {se:.4f})",
              f"{RB.mean():.4f}(SE {se_rb:.4f},z={zz:.2f})", "通过" if abs(zz) < 3 else "不通过",
              "两侧都含 1/D_t²,m 小时重尾、标准误大;max(1,I) 截断使条件矩略偏")
ck.log("m0  经验MSE  参照v+A/m0  按初始m比值  按实现D比值  D中位数/m0")
for r_ in rows:
    ck.log("%4d %.4f %.4f %.3f %.3f %.2f" % r_)
init_ratios = [r_[3] for r_ in rows if r_[0] >= 25]
real_ratios = [r_[4] for r_ in rows if r_[0] >= 25]
ck.record("8.11", "m≥25:按初始 m 的经验/参照比值(论文 0.75–0.98)", "0.75–0.98", f"{min(init_ratios):.2f}–{max(init_ratios):.2f}",
          "通过" if max(init_ratios) < 1 else "偏差", "比值 < 1:按论文自己的横轴,v_R+A/m 不是下界(issues I-23)")
ck.record("8.12", "m≥25:按实现规模 D_t 的经验/参照比值(论文 1.01–1.17)", "1.01–1.17", f"{min(real_ratios):.2f}–{max(real_ratios):.2f}",
          "通过" if min(real_ratios) > 0.95 else "偏差", "≥1 是数值现象,论文第 406 行称「始终不低于单代静态下界」缺少证明;本复现仅为同规格独立仿真,非逐点复刻")
ck.record("8.13", "评价周实际规模中位数 / 初始 m(论文 1.7–2.4 倍)", "1.7–2.4", f"{min(r_[5] for r_ in rows):.2f}–{max(r_[5] for r_ in rows):.2f}",
          "通过" if 1.5 < np.median([r_[5] for r_ in rows]) < 2.6 else "偏差")
ck.close()
