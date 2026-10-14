#!/usr/bin/env python3
"""命题 2(全方差分解)、定义 1(m_×)、命题 3(杠杆非对称)与翻倍降幅公式:sympy + 蒙特卡洛。"""
import numpy as np
import sympy as sp
from _common import Checker, rel

ck = Checker("c03_prop2_mx_prop3", "命题 2 / 定义 1 / 命题 3:方差分解、交叉点、杠杆非对称")
Rb, v, k, rho, n, m = sp.symbols("Rbar v_R k rho n m", positive=True)

# ---- 命题 2:全方差公式 ----
ER, ER2 = Rb, v + Rb**2
cond_mean_var = v                                   # Var(E[R̂|R]) = Var(R) = v_R
cond_var_mean = ER / (rho * n) + ER2 / (k * n)      # E[Var(R̂|R)]
V = sp.simplify(cond_mean_var + cond_var_mean)
V_paper = v + Rb / (rho * n) + (Rb**2 + v) / (k * n)
ck.record("3.1", "全方差公式给出式 eq:var_prop2", 0, sp.simplify(V - V_paper), "通过" if sp.simplify(V - V_paper) == 0 else "不通过")
A = Rb + rho * (Rb**2 + v) / k
ck.record("3.2", "式 eq:var_prop2 = v_R + A/m(m=ρn,A 为第 176 行)", 0, sp.simplify(V_paper - (v + A / (rho * n))),
          "通过" if sp.simplify(V_paper - (v + A / (rho * n))) == 0 else "不通过")

# ---- 定义 1 与图 1 参数 ----
pars = {Rb: 1.15, v: 0.04, k: 0.35, rho: 0.25}
A_num, mx_num = float(A.subs(pars)), float((A / v).subs(pars))
ck.record("3.3", "图 1/图 3 参数下 A 与 m_×(第 196、399 行:A=2.1232,m_×=53.1)", "2.1232; 53.1",
          f"{A_num:.4f}; {mx_num:.2f}", "通过" if abs(A_num - 2.1232) < 5e-4 and abs(mx_num - 53.1) < 0.05 else "不通过")
share_env = sp.simplify((v / (v + A / m)).subs(m, A / v))
ck.record("3.4", "m = m_× 处环境项占总方差 50%", "1/2", share_env, "通过" if share_env == sp.Rational(1, 2) else "不通过")
dbl = sp.simplify(((v + A / m) - (v + A / (2 * m))) / (v + A / m) - 1 / (2 * (1 + m / (A / v))))
ck.record("3.5", "翻倍降幅 [V(m)-V(2m)]/V(m) = 1/(2(1+m/m_×))(第 409 行)", 0, dbl, "通过" if dbl == 0 else "不通过")
for mm, paper in [(10, 42.1), (53.08, 25.0), (200, 10.5)]:
    val = 100 / (2 * (1 + mm / mx_num))
    ck.record(f"3.6.{mm}", f"翻倍降幅数值 m={mm}", f"{paper}%", f"{val:.2f}%", "通过" if abs(val - paper) < 0.06 else "不通过")
dVdm = sp.diff(v + A / m, m)
ck.record("3.7", "dV/dm = -A/m²(第 190 行)", -A / m**2, dVdm, "通过" if sp.simplify(dVdm + A / m**2) == 0 else "不通过")

# ---- 命题 3 ----
Vnr = v + Rb / (rho * n) + (Rb**2 + v) / (k * n)
dec = sp.simplify(Rb / (rho * n) - (Rb / n + (1 - rho) * Rb / (rho * n)))
ck.record("3.8", "恒等拆分 式 eq:rho_decomp", 0, dec, "通过" if dec == 0 else "不通过")
lim_rho = sp.limit(Vnr, rho, 1)
ck.record("3.9", "ρ→1 极限 式 eq:rho_limit", v + Rb / n + (Rb**2 + v) / (k * n), lim_rho,
          "通过" if sp.simplify(lim_rho - (v + Rb / n + (Rb**2 + v) / (k * n))) == 0 else "不通过")
lim_n = sp.limit(Vnr, n, sp.oo)
ck.record("3.10", "n→∞ 极限 = v_R(第 222 行)", v, lim_n, "通过" if sp.simplify(lim_n - v) == 0 else "不通过")
# 补充:同样增加一单位期望报告规模 m,两条路径的边际降幅之比
V_m_via_n = v + A / m                                     # ρ 固定,n = m/ρ
V_m_via_rho = v + Rb / m + (Rb**2 + v) / (k * n)          # n 固定,ρ = m/n
ratio = sp.simplify(sp.diff(V_m_via_n, m) / sp.diff(V_m_via_rho, m))
ck.record("3.11", "【补充】每增加一单位 m:沿 n 与沿 ρ 的边际降幅之比", "A/R̄ = 1+ρ(R̄²+v_R)/(kR̄)", ratio,
          "通过" if sp.simplify(ratio - A / Rb) == 0 else "不通过", "非对称在单位规模口径下的精确度量,见 derivations §6.4")
# 住院场景下该比值的数值(第 515 行情景区间)
vals = [float((A / Rb).subs({Rb: 1.67, rho: r_, k: k_, v: v_})) for r_ in (0.0056, 0.021) for k_ in (0.2, 0.5) for v_ in (0.04, 0.08)]
ck.record("3.12", "【补充】流感住院情景下 A/R̄ 的范围", "接近 1 则两条杠杆几乎等效", f"[{min(vals):.3f}, {max(vals):.3f}]", "偏差",
          "ρ≈1% 时命题 3 的非对称在数量上很弱,论文第 467、613、658 行把它作为实证启示时应说明")

# ---- 蒙特卡洛:命题 2 方差与交叉点份额 ----
rng = np.random.default_rng(20261013)
Rbar, vR, kk, rr = 1.15, 0.04, 0.35, 0.25
reps = 200_000
for nn in [4, 40, 212, 2000]:
    Rt = rng.gamma(shape=Rbar**2 / vR, scale=vR / Rbar, size=reps)
    # 给定 R_t 抽 C ~ NB(nk, k/(k+ρR))(分布已在 c02 用卷积独立核实)
    Cc = rng.negative_binomial(nn * kk, kk / (kk + rr * Rt))
    Rhat = Cc / (rr * nn)
    v_th = vR + (Rbar + rr * (Rbar**2 + vR) / kk) / (rr * nn)
    v_mc = Rhat.var(ddof=1)
    se = np.sqrt((np.mean((Rhat - Rhat.mean())**4) - v_mc**2) / reps)
    ck.record(f"3.mc.{nn}", f"Var(C/(ρn)|n) MC vs 式 eq:var_prop2(n={nn},m={rr*nn:g})", f"{v_th:.5f}",
              f"{v_mc:.5f}(比值 {v_mc / v_th:.4f},z={(v_mc - v_th) / se:.2f})",
              "通过" if abs((v_mc - v_th) / se) < 3 else "不通过")
    # 环境份额:Var(E[R̂|R]) / Var(R̂),MC 用 Var(R_t)/Var(R̂)
    share = Rt.var() / v_mc
    ck.record(f"3.share.{nn}", f"环境项份额 v_R/V(m={rr*nn:g}),m_×=53.1 时应≈0.5", f"{vR / v_th:.3f}", f"{share:.3f}",
              "通过" if abs(share - vR / v_th) < 0.02 else "不通过")
ck.close()
