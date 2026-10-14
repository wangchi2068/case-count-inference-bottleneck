#!/usr/bin/env python3
"""命题 4:预算约束方差、AR(1) 双重求和闭式、T_eff 近似误差、离散可行集;sympy + 蒙特卡洛。"""
import numpy as np
import sympy as sp
from _common import Checker, rel

ck = Checker("c04_prop4_ar1", "命题 4:预算权衡、AR(1) 有效期数与可行期数集合")
T, r, v, A, B, s = sp.symbols("T r v_R A B s", positive=True)

# ---- (i) 独立环境:v/T + A/B,且关于 T 严格递减 ----
m = B / T
V_ind = v / T + A / (T * m)
ck.record("4.1", "全方差 + 预算 B=Tm 给出 v_R/T + A/B(式 eq:var_budget_indep)", 0, sp.simplify(V_ind - (v / T + A / B)),
          "通过" if sp.simplify(V_ind - (v / T + A / B)) == 0 else "不通过")
ck.record("4.2", "∂/∂T (v_R/T + A/B) = -v_R/T² < 0", -v / T**2, sp.diff(v / T + A / B, T),
          "通过" if sp.simplify(sp.diff(v / T + A / B, T) + v / T**2) == 0 else "不通过")

# ---- (ii) AR(1) 双重求和 ----
closed = r * T / (1 - r) - r * (1 - r**T) / (1 - r)**2          # Σ_{s=1}^{T-1}(T-s) r^s
ok = all(sp.simplify(sum((Ti - si) * r**si for si in range(1, Ti)) - closed.subs(T, Ti)) == 0 for Ti in range(1, 41))
ck.record("4.3", "Σ_{s=1}^{T-1}(T-s)r^s = rT/(1-r) - r(1-r^T)/(1-r)²(T=1..40 逐个符号核对)", "恒等", "恒等" if ok else "不等",
          "通过" if ok else "不通过")
bracket = sp.simplify((T + 2 * closed) / T - ((1 + r) / (1 - r) - 2 * r * (1 - r**T) / (T * (1 - r)**2)))
ck.record("4.4", "Tv_R + 2v_RΣ = v_R T[(1+r)/(1-r) - 2r(1-r^T)/(T(1-r)²)](附录第 751 行)", 0, bracket,
          "通过" if bracket == 0 else "不通过")
sym_sum = sp.simplify(sp.summation((T - s) * r**s, (s, 1, T - 1)) - closed)
ok45 = sym_sum == 0 or (isinstance(sym_sum, sp.Piecewise) and sym_sum.args[-1][0] == 0)
ck.record("4.5", "sympy 直接求和与闭式的差(r≠1 分支)", 0, sym_sum, "通过" if ok45 else "不通过", "Piecewise 中 r=1 分支为闭式的可去奇点,与 0≤r<1 无关")

# 精确环境项与 T_eff 近似
def env_exact(Tv, rv):
    return (1 / Tv) * ((1 + rv) / (1 - rv) - 2 * rv * (1 - rv**Tv) / (Tv * (1 - rv)**2))

def env_approx(Tv, rv):
    return (1 + rv) / ((1 - rv) * Tv)

rows = []
for Tv in (5, 10, 26, 52, 156):
    for rv in (0.3, 0.5, 0.8, 0.9):
        e, a_ = env_exact(Tv, rv), env_approx(Tv, rv)
        rows.append((Tv, rv, e, a_, a_ / e - 1, Tv * (1 - rv)))
ck.log("T  r  精确(÷v_R)  T_eff近似(÷v_R)  近似高估比例  T(1-r)")
for row in rows:
    ck.log("%4d %.1f %.5f %.5f %+.1f%% %.1f" % (row[0], row[1], row[2], row[3], 100 * row[4], row[5]))
always_over = all(rw[4] > 0 for rw in rows)
ck.record("4.6", "T_eff 近似对环境项的偏差方向", "论文未说明方向", "所有 (T,r) 下近似均高估环境项" if always_over else "方向不一",
          "偏差", "高估比例 = 2r(1-r^T)/(T(1-r)(1+r)-2r(1-r^T));r=0.8,T=26 时 +20.5%,r=0.8,T=10 时 +65.8%(见日志表)")
over = sp.simplify(((1 + r) / (1 - r)) / ((1 + r) / (1 - r) - 2 * r * (1 - r**T) / (T * (1 - r)**2)) - 1
                   - 2 * r * (1 - r**T) / (T * (1 - r) * (1 + r) - 2 * r * (1 - r**T)))
ck.record("4.7", "近似高估比例的闭式", 0, over, "通过" if over == 0 else "不通过")
e26, a26 = env_exact(26, 0.8), env_approx(26, 0.8)
ck.record("4.8", "「T ≫ 1/(1-r)」条件下的实际误差(T=26 周、r=0.8,T(1-r)=5.2)", "可良好近似", f"高估 {100*(a26/e26-1):.1f}%", "偏差",
          "满足 T>1/(1-r)=5 并不足以「良好近似」,建议正文给误差界或直接用精确闭式")
# 精确环境项关于 T 单调递减(r≥0)
mono = all(env_exact(Tv + 1, rv) < env_exact(Tv, rv) for rv in np.linspace(0, 0.98, 50) for Tv in range(1, 300))
ck.record("4.9", "【补充】AR(1) 精确环境项 Var(R̄_T)/v_R 关于 T 严格递减(r∈[0,0.98],T=1..300)", "递减", "递减" if mono else "存在反例",
          "通过" if mono else "不通过", "命题 4(i) 的单调性结论在 AR(1) 下仍成立")

# ---- (iii) 离散可行集 ----
def feasible(Bv, rhov, Tmax=None):
    out = []
    for Ti in range(1, int(Bv / rhov) + 2):
        q = Bv / (rhov * Ti)
        if abs(q - round(q)) < 1e-9 and round(q) >= 1:
            out.append(Ti)
    return out

f1 = feasible(30, 0.25)
divs = [d for d in range(1, 121) if 120 % d == 0]
ck.record("4.10", "B=30, ρ=0.25(B/ρ=120)时可行期数 = 120 的正因子", divs, f1, "通过" if f1 == divs else "不通过")
f2 = feasible(30, 0.7)
ck.record("4.11", "B=30, ρ=0.7(B/ρ 非整数)时可行集为空", [], f2, "通过" if f2 == [] else "不通过")
ck.record("4.12", "T ≤ ⌊B/ρ⌋ 只是必要条件:T=7 ≤ 120 但不可行", "7 ∉ 𝒯", "7 ∉ 𝒯" if 7 not in f1 else "7 ∈ 𝒯",
          "通过" if 7 not in f1 else "不通过")

# ---- 蒙特卡洛:AR(1) 高斯环境 + NB 报告 ----
rng = np.random.default_rng(20261014)
Rbar, vR, kk, rho_ = 1.15, 0.04, 0.35, 0.25
Avalue = Rbar + rho_ * (Rbar**2 + vR) / kk
Bud = 260.0
for Tv in (10, 26):
    mv = Bud / Tv
    nv = mv / rho_
    reps = 200_000 // Tv
    for rv in (0.0, 0.5, 0.8):
        eps = np.empty((reps, Tv))
        eps[:, 0] = rng.normal(0, np.sqrt(vR), reps)
        innov = rng.normal(0, np.sqrt(vR * (1 - rv**2)), (reps, Tv))
        for t in range(1, Tv):
            eps[:, t] = rv * eps[:, t - 1] + innov[:, t]
        Rt = np.clip(Rbar + eps, 1e-6, None)   # 截断概率 < 1e-8,可忽略
        Cc = rng.negative_binomial(nv * kk, kk / (kk + rho_ * Rt))
        mean_hat = (Cc / (rho_ * nv)).mean(axis=1)
        v_mc = mean_hat.var(ddof=1)
        se = v_mc * np.sqrt(2 / (reps - 1))
        v_exact = vR * env_exact(Tv, rv) + Avalue / Bud if rv > 0 else vR / Tv + Avalue / Bud
        v_appr = vR * env_approx(Tv, rv) + Avalue / Bud
        z = (v_mc - v_exact) / se
        ck.record(f"4.mc.T{Tv}.r{rv}", f"MC Var(R̄_T)(T={Tv},m={mv:.1f},r={rv},reps={reps})",
                  f"精确 {v_exact:.5f};T_eff 近似 {v_appr:.5f}",
                  f"{v_mc:.5f}(对精确 z={z:.2f};对近似 {100*(v_appr/v_mc-1):+.1f}%)",
                  "通过" if abs(z) < 3 else "不通过", "精确闭式与 MC 吻合;近似的偏差列在实测括号里")
ck.close()
