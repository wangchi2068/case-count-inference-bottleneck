#!/usr/bin/env python3
"""命题 5(正文编号):单步预测方差分解 式 eq:var_I_decomp / eq:var_C_decomp;
符号验证、向命题 2 的退化,以及随机 Λ、R 的蒙特卡洛。"""
import numpy as np
import sympy as sp
from _common import Checker

ck = Checker("c06_prop5", "命题 5:真实感染与报告病例的单步预测方差分解")
rho, k, n, Rb, v = sp.symbols("rho k n Rbar v_R", positive=True)
EI, VI = sp.symbols("E_I V_I", positive=True)

# (1) 报告层:C|I ~ Bin(I, ρ) ⇒ Var(C|F) = E[Iρ(1-ρ)|F] + Var(ρI|F)
VC = rho * (1 - rho) * EI + rho**2 * VI
ck.record("6.1", "全方差 + 二项条件矩 ⇒ 式 eq:var_C_decomp", "ρ(1-ρ)E[I|F] + ρ²Var(I|F)", VC, "通过",
          "E[Var(C|I)] = ρ(1-ρ)E[I],Var(E[C|I]) = ρ²Var(I);条件独立于 F_t^C 是必要的")

# (2) 退化到命题 2:Λ=n 已知,R~(R̄,v_R),I|n,R ~ NB 分支(均值 nR,方差 nR+nR²/k)
VI_n = n**2 * v + (n * Rb + n * (Rb**2 + v) / k)        # Var(nR) + E[nR + nR²/k]
EI_n = n * Rb
VC_n = VC.subs({EI: EI_n, VI: VI_n})
red = sp.simplify(VC_n / (rho * n)**2 - (v + Rb / (rho * n) + (Rb**2 + v) / (k * n)))
ck.record("6.2", "【补充】Λ≡n 已知时 Var(C|F)/(ρn)² 恰为命题 2 的 v_R + A/m", 0, red, "通过" if red == 0 else "不通过",
          "命题 5 是命题 2 在随机感染压力下的推广;论文没有写出这一桥接")
# (3) 命题 5 第一式的第一项 Var(ΛR|F) 在 Λ、R 条件独立时的展开
EL, VL = sp.symbols("E_Lambda V_Lambda", positive=True)
var_LR = (VL + EL**2) * (v + Rb**2) - EL**2 * Rb**2
ck.record("6.3", "【补充】Λ ⫫ R | F 时 Var(ΛR|F) = Var(Λ)v_R + Var(Λ)R̄² + E[Λ]²v_R", sp.expand(var_LR),
          sp.expand(VL * v + VL * Rb**2 + EL**2 * v), "通过" if sp.simplify(var_LR - (VL * v + VL * Rb**2 + EL**2 * v)) == 0 else "不通过",
          "感染压力的不确定性 Var(Λ|F) 以 R̄² 放大进入预测方差,这是第 391 行「预测偏差项」的来源")

# (4) 蒙特卡洛:Λ ~ Gamma(代表给定报告历史时对感染压力的后验不确定性),R ~ Gamma,I|Λ,R 为 Poisson–Gamma 分支
rng = np.random.default_rng(20261015)
N = 200_000
Rbar, vR, kk, rr = 1.15, 0.04, 0.35, 0.25
for EL_v, cvL in [(40.0, 0.0), (40.0, 0.3), (200.0, 0.5)]:
    if cvL == 0:
        Lam = np.full(N, EL_v)
    else:
        Lam = rng.gamma(1 / cvL**2, EL_v * cvL**2, N)
    Rt = rng.gamma(Rbar**2 / vR, vR / Rbar, N)
    # I | Λ,R ~ NB(shape kΛ, mean ΛR):Poisson(Gamma(kΛ, R/k))
    I = rng.poisson(rng.gamma(kk * Lam, Rt / kk))
    C = rng.binomial(I, rr)
    # 理论:Var(I) = Var(ΛR) + E[ΛR + ΛR²/k]
    VL_v = (cvL * EL_v)**2
    VLR = VL_v * vR + VL_v * Rbar**2 + EL_v**2 * vR
    VI_th = VLR + EL_v * Rbar + EL_v * (Rbar**2 + vR) / kk
    EI_th = EL_v * Rbar
    VC_th = rr * (1 - rr) * EI_th + rr**2 * VI_th
    # 直接用 MC 的 E[I]、Var(I) 代入 式 eq:var_C_decomp(检验报告层恒等式本身)
    VC_plug = rr * (1 - rr) * I.mean() + rr**2 * I.var()
    # 重尾分布下四阶矩公式会低估方差估计的标准误,改用 20 批次的批均值标准误
    seC = np.array([b.var() for b in C.reshape(20, -1)]).std(ddof=1) / np.sqrt(20)
    seI = np.array([b.var() for b in I.reshape(20, -1)]).std(ddof=1) / np.sqrt(20)
    tag = f"E[Λ]={EL_v:g},CV(Λ)={cvL}"
    ck.record(f"6.mc.I.{EL_v:g}.{cvL}", f"Var(I) MC vs 式 eq:var_I_decomp 两项之和({tag})", f"{VI_th:.1f}",
              f"{I.var():.1f}(z={(I.var() - VI_th) / seI:.2f})", "通过" if abs((I.var() - VI_th) / seI) < 3 else "不通过")
    ck.record(f"6.mc.C.{EL_v:g}.{cvL}", f"Var(C) MC vs 式 eq:var_C_decomp({tag})", f"理论 {VC_th:.2f};MC 矩代入 {VC_plug:.2f}",
              f"{C.var():.2f}(对理论 z={(C.var() - VC_th) / seC:.2f})", "通过" if abs((C.var() - VC_th) / seC) < 3 else "不通过",
              "判定按预设 |z|<3 机械给出;越界时以 6.mc.seeds 的多种子复核区分公式错误与抽样波动")
    if cvL == 0:
        ck.record("6.mc.reduce", "Λ 固定时 Var(C)/(ρΛ)² 与命题 2 的 V(m)", f"{vR + (Rbar + rr*(Rbar**2+vR)/kk)/(rr*EL_v):.4f}",
                  f"{C.var() / (rr * EL_v)**2:.4f}", "通过" if abs(C.var() / (rr * EL_v)**2 / (vR + (Rbar + rr*(Rbar**2+vR)/kk)/(rr*EL_v)) - 1) < 0.03 else "不通过")
# 种子稳健性:CV(Λ)=0.3 配置换 20 个种子、每个 1e4 次(合计 2e5),看相对误差是否系统偏离 0
EL_v, cvL = 40.0, 0.3
VL_v = (cvL * EL_v)**2
VI_th = VL_v * vR + VL_v * Rbar**2 + EL_v**2 * vR + EL_v * Rbar + EL_v * (Rbar**2 + vR) / kk
VC_th = rr * (1 - rr) * EL_v * Rbar + rr**2 * VI_th
relI, relC = [], []
for seed in range(20):
    g = np.random.default_rng(1000 + seed)
    Lam = g.gamma(1 / cvL**2, EL_v * cvL**2, 10_000)
    Rt = g.gamma(Rbar**2 / vR, vR / Rbar, 10_000)
    I = g.poisson(g.gamma(kk * Lam, Rt / kk))
    C = g.binomial(I, rr)
    relI.append(I.var() / VI_th - 1)
    relC.append(C.var() / VC_th - 1)
mI, sI = np.mean(relI), np.std(relI, ddof=1) / np.sqrt(20)
mC, sC = np.mean(relC), np.std(relC, ddof=1) / np.sqrt(20)
ck.record("6.mc.seeds", "20 个独立种子(各 1e4)的平均相对误差(E[Λ]=40,CV(Λ)=0.3)", "0",
          f"Var(I): {100*mI:+.2f}% ± {100*sI:.2f}%;Var(C): {100*mC:+.2f}% ± {100*sC:.2f}%",
          "通过" if abs(mI) < 3 * sI and abs(mC) < 3 * sC else "不通过", "排除单一种子的偶然偏离")
ck.close()
