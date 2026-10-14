#!/usr/bin/env python3
"""推论 1:成本约束下的最优单期规模 m*;一阶/二阶条件、角点解、整数搜索、论文数值、AR(1) 修正。"""
import itertools
import numpy as np
import sympy as sp
from _common import Checker, rel

ck = Checker("c05_cor1", "推论 1:成本约束下的最优监测规模 m*")
m, c0, c1, A, v, Bc, r = sp.symbols("m c0 c1 A v_R Bcal r", positive=True)

T = Bc / (c0 + c1 * m)
f = v / T + A / (T * m)                      # = (c0 + c1 m)(v + A/m)/𝓑
f_exp = sp.expand(sp.simplify(f))
ck.record("5.1", "代入 T=𝓑/(c0+c1m) 后 f(m) = [c0v_R + c0A/m + c1v_Rm + c1A]/𝓑", 0,
          sp.simplify(f - (c0 * v + c0 * A / m + c1 * v * m + c1 * A) / Bc),
          "通过" if sp.simplify(f - (c0 * v + c0 * A / m + c1 * v * m + c1 * A) / Bc) == 0 else "不通过")
f1 = sp.simplify(sp.diff(f, m))
ck.record("5.2", "f'(m) = (c1v_R - c0A/m²)/𝓑", 0, sp.simplify(f1 - (c1 * v - c0 * A / m**2) / Bc),
          "通过" if sp.simplify(f1 - (c1 * v - c0 * A / m**2) / Bc) == 0 else "不通过")
f2 = sp.simplify(sp.diff(f, m, 2))
ck.record("5.3", "f''(m) = 2c0A/(𝓑m³) > 0(第 277 行)", 2 * c0 * A / (Bc * m**3), f2,
          "通过" if sp.simplify(f2 - 2 * c0 * A / (Bc * m**3)) == 0 else "不通过")
sol = sp.solve(sp.Eq(f1, 0), m)
ck.record("5.4", "f'(m)=0 的唯一正根 m* = √(c0A/(c1v_R))(式 eq:optimal_scale)", sp.sqrt(c0 * A / (c1 * v)), sol,
          "通过" if len(sol) == 1 and sp.simplify(sol[0] - sp.sqrt(c0 * A / (c1 * v))) == 0 else "不通过")
# 几何平均表述:m* = √((c0/c1)·m_×)
ck.record("5.5", "m* 是成本比 c0/c1 与 m_× 的几何平均(第 283 行)", "√((c0/c1)·m_×)", "恒等", "通过")
# 预算形式:c0=0 时 f 关于 m 单调增 → m*→0
ck.record("5.6", "c0=0 时 f'(m) = c1v_R/𝓑 > 0,最优 m→0(第 279 行)", "c1v_R/𝓑", sp.simplify(f1.subs(c0, 0)),
          "通过" if sp.simplify(f1.subs(c0, 0) - c1 * v / Bc) == 0 else "不通过")

# ---- 数值:论文情景 ----
Rb = 1.67
grid = {"k": (0.2, 0.5), "rho": (0.0056, 0.021), "v": (0.04, 0.08)}
mx_vals = []
for kk, rr, vv in itertools.product(grid["k"], grid["rho"], grid["v"]):
    Av = Rb + rr * (Rb**2 + vv) / kk
    mx_vals.append(Av / vv)
mx_lo, mx_hi = min(mx_vals), max(mx_vals)
ck.record("5.7", "情景区间(R̄=1.67,k∈[0.2,0.5],ρ∈[0.0056,0.021],v_R∈[0.04,0.08])的 m_× 角点范围(第 515 行 21.3–49.3)",
          "21.3–49.3", f"{mx_lo:.2f}–{mx_hi:.2f}", "偏差" if abs(mx_hi - 49.3) > 0.05 else "通过",
          "上端用一致参数得 49.18;论文 49.3 需在 A 里取 v_R=0.08、分母取 0.04(两处 v_R 不一致),差异可忽略但应修正口径")
# 49.3 的来源复现
Ahi_v08 = Rb + 0.021 * (Rb**2 + 0.08) / 0.2
ck.record("5.8", "复现 49.3:A(v=0.08)/0.04", 49.3, f"{Ahi_v08/0.04:.2f}", "通过" if abs(Ahi_v08 / 0.04 - 49.3) < 0.05 else "不通过",
          "说明 49.3 来自不一致的 v_R 取值")
for ratio, paper in [(10, (14.6, 22.2)), (100, (46.1, 70.2))]:
    lo, hi = np.sqrt(ratio * 21.3), np.sqrt(ratio * 49.3)
    lo2, hi2 = np.sqrt(ratio * mx_lo), np.sqrt(ratio * mx_hi)
    okk = abs(lo - paper[0]) < 0.06 and abs(hi - paper[1]) < 0.06
    ck.record(f"5.9.{ratio}", f"c0/c1={ratio} 时 m* 区间(第 283 行 {paper[0]}–{paper[1]})", f"{paper[0]}–{paper[1]}",
              f"用 21.3/49.3:{lo:.2f}–{hi:.2f};用一致角点:{lo2:.2f}–{hi2:.2f}", "通过" if okk else "不通过",
              "第 283 行未注明 m_× 取自第 515 行情景;中期报告第 191 行误写为「m_× 14.6～24.4」")
ck.record("5.10", "图 1 参数(m_×=53.08)下 c0/c1=10 与 100 的 m*", "论文未给", f"{np.sqrt(530.8):.1f}; {np.sqrt(5308):.1f}", "通过",
          "补充数值,供答辩举例")

# ---- 整数离散搜索 vs 连续解 ----
Rbar, vR, k_, rho_ = 1.15, 0.04, 0.35, 0.25
Av = Rbar + rho_ * (Rbar**2 + vR) / k_
for c0v, c1v, Bv in [(10.0, 1.0, 2000.0), (100.0, 1.0, 20000.0), (100.0, 1.0, 600.0)]:
    best = None
    for Ti in range(1, int(Bv / c0v) + 1):
        mm = (Bv / Ti - c0v) / c1v            # 用尽经费
        if mm <= 0:
            continue
        val = vR / Ti + Av / (Ti * mm)
        if best is None or val < best[0]:
            best = (val, Ti, mm)
    mstar = np.sqrt(c0v / c1v * Av / vR)
    mmax = (Bv - c0v) / c1v
    m_use = min(mstar, mmax)
    T_cont = Bv / (c0v + c1v * m_use)
    ck.record(f"5.11.{int(c0v)}.{int(Bv)}", f"整数 T 枚举 vs 连续 m*(c0={c0v},c1={c1v},𝓑={Bv})",
              f"连续 m*={m_use:.2f}(T={T_cont:.2f}{',角点' if mstar > mmax else ''})",
              f"整数最优 T={best[1]},m={best[2]:.2f}", "通过" if rel(best[2], m_use) < 0.35 or abs(best[1] - T_cont) <= 1 else "不通过",
              "整数解落在连续解相邻的 T 上")
# 角点:𝓑 很小时内部解不可行
Bsmall = 40.0
mstar = np.sqrt(100 * Av / vR)
ck.record("5.12", "角点条件:c0=100,c1=1,𝓑=140 时 √(c0m_×/c1)=72.9 > (𝓑-c0)/c1=40 ⇒ m*=40,T=1", "m*=40",
          f"内部解 {mstar:.1f} > 40 ⇒ 取 40", "通过" if mstar > Bsmall else "不通过")

# ---- AR(1) 修正 ----
fA = (c0 + c1 * m) * (v * (1 + r) / (1 - r) + A / m) / Bc
solA = sp.solve(sp.Eq(sp.diff(fA, m), 0), m)
target = sp.sqrt(c0 / c1 * (A / v) * (1 - r) / (1 + r))
ck.record("5.13", "v_eff=v_R(1+r)/(1-r) 代入得 m*_AR = √(c0/c1·m_×(1-r)/(1+r))(第 280 行)", target, solA,
          "通过" if len(solA) == 1 and sp.simplify(solA[0] - target) == 0 else "不通过")
# 精确 AR(1) 目标下整数搜索:近似 m*_AR 与精确最优的差距
def env_exact(Tv, rv):
    if Tv == 1:
        return 1.0
    return (1 / Tv) * ((1 + rv) / (1 - rv) - 2 * rv * (1 - rv**Tv) / (Tv * (1 - rv)**2))
for rv in (0.5, 0.8):
    c0v, c1v, Bv = 100.0, 1.0, 20000.0
    best = min(((vR * env_exact(Ti, rv) + Av / (Ti * ((Bv / Ti - c0v) / c1v)), Ti, (Bv / Ti - c0v) / c1v)
                for Ti in range(1, int(Bv / c0v)) if (Bv / Ti - c0v) > 0))
    m_ar = np.sqrt(c0v / c1v * Av / vR * (1 - rv) / (1 + rv))
    ck.record(f"5.14.r{rv}", f"AR(1) 精确目标下整数搜索 vs m*_AR 近似(c0/c1=100,𝓑=2e4,r={rv})",
              f"m*_AR={m_ar:.1f}(T={Bv/(c0v+m_ar):.1f})", f"精确最优 T={best[1]},m={best[2]:.1f}",
              "通过" if rel(best[2], m_ar) < 0.25 else "偏差", "T 较大时近似可用;T 小时以附录闭式离散搜索为准")
ck.close()
