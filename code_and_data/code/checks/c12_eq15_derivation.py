#!/usr/bin/env python3
"""式 (15)(eq:b-delta)推导核验:用户建议在附录 A.8 补写的一阶 delta 法推导是否正确、缺哪些条件。

三层检查:
  (1) sympy:分母 D_t 的条件均值/方差;G = X/(1+δ) 的一阶与二阶展开,按 1/m 收集到 O(1/m);
      对照「同除以 R̄²」(论文 L_t 以固定的阶段均值 R̄ 为基准)与「除以条件均值平方」两种归一化。
  (2) 精确数值:固定 m,对二项报告逐点枚举 E(m/D)、E[(m/D)²](D≥5 截断,同实证筛选),
      得到 E(L|m) 的精确值,看 m·[E(L|m) - v_R/R̄²] 收敛到哪个斜率。
  (3) 蒙特卡洛(复用 c10 设定):同一批样本分别以真实 1/m 和含噪 1/D 为回归元做 FGLS,
      分开「展开式本身」与「用 D 代替 m 回归」两处误差。
另查非平稳(周增长比 r≠1)时 Σw² 的有效值。"""
import json
from pathlib import Path

import numpy as np
import sympy as sp
from scipy.stats import binom

from _common import Checker, fgls_affine

ck = Checker("c12_eq15_derivation", "式 (15) 的一阶推导核验:用户建议的 A.8 补充推导")

RB, V, K, RHO = 1.67, 0.06, 0.35, 0.021          # 与 c10、正文 6.3 节情景参数一致
ER2 = RB**2 + V
A = RB + RHO * ER2 / K
WEIGHTS = {"original": np.array([0.65, 0.25, 0.10]),
           "single": np.array([1.0, 0.0, 0.0]),
           "equal": np.full(3, 1 / 3)}


def b15(sw2):                         # 正文式 (15)
    return (A + (1 - RHO) * ER2 * sw2) / RB**2


def b15_fixed(sw2):                   # L 以固定 R̄ 归一化时的 O(1/m) 系数(本脚本推得)
    return (A + (1 - RHO) * (RB**2 + 3 * V) * sw2) / RB**2


# ---------------------------------------------------------------- (1) sympy
rho, Rb, vR, Av, m, eps, c = sp.symbols("rho Rbar v_R A m epsilon c", positive=True)
w = sp.symbols("w1:4", positive=True)
I = sp.symbols("I1:4", positive=True)
# D = Σ w_s C_s,C_s ~ Bin(I_s, ρ) 独立
ED = sum(ws * rho * Is for ws, Is in zip(w, I))
VD = sum(ws**2 * rho * (1 - rho) * Is for ws, Is in zip(w, I))
Lam = sp.Symbol("Lambda", positive=True)
VD_stat = sp.simplify(VD.subs({Is: Lam for Is in I}) / (rho * Lam)**2)
ck.record("12.1", "D_t 的条件均值与条件方差(给定 I_{t+1-s})",
          "均值 ρΣw_sI_{t+1-s}=ρΛ_{t+1};方差 ρ(1-ρ)Σw_s²I_{t+1-s}",
          f"E={ED};Var={sp.factor(VD)}", "通过",
          "均值等于 ρΛ_{t+1} 要求 D_t 的权重与 Λ_{t+1} 的权重相同;I_s≡Λ 时 Var(D/ρΛ)="
          f"{VD_stat}=(1-ρ)Σw²/m 还要求 Σw_s=1")

# G = X·Y,X = C_{t+1}/(ρΛ),Y = 1/(1+δ);X 与 δ 条件独立(当期与往期报告抽样独立)
# E X = R̄,Var X = v_R + A/m;E δ = 0,E δ² = c/m,E δ³ = O(m⁻²),E δ⁴ = 3c²/m² + O(m⁻³)
d = sp.Symbol("delta")
mom = {1: 0, 2: c * eps, 3: 0, 4: 3 * c**2 * eps**2}
EX, EX2 = Rb, Rb**2 + vR + Av * eps


def Edelta(expr, order=4):
    poly = sp.Poly(sp.series(expr, d, 0, order + 1).removeO(), d)
    return sum(coef * (mom[k[0]] if k[0] else 1) for k, coef in zip(poly.monoms(), poly.coeffs()))


EY1 = Edelta(1 / (1 + d))
EY2 = Edelta(1 / (1 + d)**2)
# 一阶 delta(用户建议):G ≈ X(1-δ)
var_first = sp.expand(EX2 * Edelta((1 - d)**2, 2) - EX**2)
# 完整到 O(1/m)
varG = sp.expand(EX2 * EY2 - (EX * EY1)**2)
varG1 = sp.series(varG, eps, 0, 2).removeO()
EG1 = sp.series(EX * EY1, eps, 0, 2).removeO()
mse_fixed = sp.series((varG + (EX * EY1 - Rb)**2) / Rb**2, eps, 0, 2).removeO()   # L=[(G-R̄)/R̄]²
cv2 = sp.series(varG / (EX * EY1)**2, eps, 0, 2).removeO()                     # 除以条件均值平方
slope = lambda e: sp.factor(sp.expand(e).coeff(eps, 1))
ck.record("12.2", "用户建议的一阶 delta 展开 G≈X(1-δ):Var(G) 的 1/m 项",
          "A + (R̄²+v_R)c,c=(1-ρ)Σw²", f"{slope(var_first)}", "通过",
          f"一阶展开 Var = {sp.factor(var_first)};用户写的附加项 E(R²)·Var(δ) 正确")
ck.record("12.3", "保留 δ² 项后 Var(G|m) 的 1/m 项(δ² 的期望与 1/m 同阶)",
          "若一阶即足够,应与 12.2 相同", f"{slope(varG1)};E(G|m)={EG1}", "偏差",
          "二阶项贡献 2v_R·c/m,与 b 同阶;同时条件均值抬高为 R̄(1+c/m)")
ck.record("12.4", "按论文损失 L_t=[(G_t-R̄)/R̄]²(固定基准 R̄)的 E(L|m) 斜率",
          "式 (15):[A+(R̄²+v_R)c]/R̄²", f"{slope(mse_fixed)}", "偏差",
          "固定基准下斜率多出 2(v_R/R̄²)c;情景参数下原始权重为 "
          f"{b15_fixed(0.495) - b15(0.495):.4f}(式 15 斜率的 {(b15_fixed(0.495) - b15(0.495)) / b15(0.495):.1%})")
ck.record("12.5", "以条件均值平方归一化(条件变异系数平方)的斜率",
          "式 (15):[A+(R̄²+v_R)c]/R̄²", f"{slope(cv2)};截距 {sp.expand(cv2).coeff(eps, 0)}", "通过",
          "式 (15) 恰是 CV²(G|m) 的 1/m 展开系数;用户的「同除以 R̄²」须理解为除以 E(G|m)²≈R̄²(1+c/m)")

# ------------------------------------------------- (1b) 非平稳:I_{t+1-s} ∝ r^{1-s}
eff = {}
for r in (0.8, 1.0, 1.25, 1.67):
    Is = np.array([1.0, 1 / r, 1 / r**2])
    for name, wt in WEIGHTS.items():
        eff[(r, name)] = float(np.sum(wt**2 * Is) / np.sum(wt * Is))
ck.record("12.6", "非平稳时 Var(D/ρΛ)·m 中的有效 Σw²(周增长比 r,原始权重)",
          "平稳(r=1)时 0.495", "; ".join(f"r={r}: {eff[(r, 'original')]:.3f}" for r in (0.8, 1.0, 1.25, 1.67)),
          "偏差", "增长期近期权重更重、有效 Σw² 变大(r=1.67 时 +12%),回落期变小;I≈Λ 的平稳近似是必要条件")

# ------------------------------------------------- (2) 固定 m 精确枚举
def moments_Y(mm, wt, dmin=5.0):
    """E(m/D)、E[(m/D)²],D=Σw_s C_s,C_s~Bin(Λ,ρ) 独立,Λ=round(mm/ρ),条件 D≥dmin。"""
    Lam_ = int(round(mm / RHO))
    me = RHO * Lam_
    sd = np.sqrt(me)
    hi = int(me + 10 * sd + 20)
    k = np.arange(0, hi + 1)
    p = binom.pmf(k, Lam_, RHO)
    keep = p > 1e-14
    k, p = k[keep].astype(float), p[keep]
    act = [x for x in wt if x > 0]
    s0 = s1 = s2 = 0.0
    if len(act) == 1:
        Dv, P = act[0] * k, p
        ok = Dv >= dmin
        s0, s1, s2 = P[ok].sum(), (P[ok] * me / Dv[ok]).sum(), (P[ok] * (me / Dv[ok])**2).sum()
    else:
        Dbc = act[1] * k[:, None] + act[2] * k[None, :]
        Pbc = p[:, None] * p[None, :]
        for ka, pa in zip(k, p):
            Dv = act[0] * ka + Dbc
            ok = Dv >= dmin
            Pk = pa * Pbc[ok]
            Y = me / Dv[ok]
            s0 += Pk.sum(); s1 += (Pk * Y).sum(); s2 += (Pk * Y * Y).sum()
    return me, s1 / s0, s2 / s0


exact = {}
for name, wt in WEIGHTS.items():
    sw2 = float(np.sum(wt**2))
    rows = []
    for mm in (20, 40, 80, 160, 320):
        me, ey, ey2 = moments_Y(mm, wt)
        ex2 = RB**2 + V + A / me
        EL = ex2 * ey2 / RB**2 - 2 * ey + 1               # E{[(XY-R̄)/R̄]²},X 与 Y 独立
        cv2n = (ex2 * ey2 - (RB * ey)**2) / (RB * ey)**2
        rows.append(dict(m=round(me, 3), E_Y=ey, E_Y2=ey2, slope_fixed=me * (EL - V / RB**2),
                         slope_cv2=me * (cv2n - V / RB**2)))
        ck.log(f"  {name} m={me:.1f}: m·[E(L|m)-a]={rows[-1]['slope_fixed']:.4f}, "
               f"m·[CV²-a]={rows[-1]['slope_cv2']:.4f}")
    exact[name] = rows
    # 用最大两档 m 做 1/m 外推,消掉 O(1/m²) 余项
    r1, r2 = rows[-2], rows[-1]
    ext = lambda key: (r2["m"] * r2[key] - r1["m"] * r1[key]) / (r2["m"] - r1["m"])
    ck.record(f"12.7.{name}", f"精确枚举(权重 {name},Σw²={sw2:.3f}):m→∞ 的斜率",
              f"式 (15) {b15(sw2):.4f};固定基准修正 {b15_fixed(sw2):.4f}",
              f"固定基准 {ext('slope_fixed'):.4f};CV² 归一化 {ext('slope_cv2'):.4f};"
              f"m=20 时 {rows[0]['slope_fixed']:.4f}",
              "通过" if abs(ext("slope_cv2") - b15(sw2)) < 0.01 and abs(ext("slope_fixed") - b15_fixed(sw2)) < 0.01 else "偏差",
              "两种归一化各自收敛到 12.4/12.5 的系数;m 小时 O(1/m²) 余项可见")

# ------------------------------------------------- (3) 蒙特卡洛,同 c10 的截面设计
N, NB_ = 60_000, 10


def simulate(rng, wt):
    mm = np.exp(rng.uniform(np.log(5), np.log(600), N))
    Lam_ = np.round(mm / RHO)
    R = rng.gamma(RB**2 / V, V / RB, N)
    I1 = rng.poisson(rng.gamma(K * Lam_, R / K))
    rep = lambda x: rng.binomial(x.astype(np.int64), RHO).astype(float)
    C1 = rep(I1)
    D = sum(ws * rep(Lam_) for ws in wt if ws > 0)
    ok = D >= 5
    return C1[ok] / D[ok], D[ok], RHO * Lam_[ok]


def fit_se(L, x):
    a, b = fgls_affine(L, x)
    ab = np.array([fgls_affine(Lb, xb) for Lb, xb in zip(np.array_split(L, NB_), np.array_split(x, NB_))])
    se = ab.std(axis=0, ddof=1) / np.sqrt(NB_)
    return a, b, se[0], se[1]


rng = np.random.default_rng(20261018)
mc = {}
for name, wt in WEIGHTS.items():
    sw2 = float(np.sum(wt**2))
    G, D, me = simulate(rng, wt)
    L = ((G - RB) / RB)**2                              # 论文口径:固定基准 R̄
    a_m, b_m, sa_m, sb_m = fit_se(L, me)
    a_d, b_d, sa_d, sb_d = fit_se(L, D)
    cross = float(np.corrcoef(G * D / me, D / me)[0, 1])   # X 与 δ 的样本相关(应≈0)
    mc[name] = dict(n=int(len(G)), a_true_m=a_m, b_true_m=b_m, se_b_true_m=sb_m,
                    a_noisy_D=a_d, b_noisy_D=b_d, se_b_noisy_D=sb_d, corr_X_delta=cross,
                    b_eq15=b15(sw2), b_fixed=b15_fixed(sw2))
    ck.record(f"12.8.{name}", f"MC(权重 {name}):以真实 1/m 为回归元",
              f"固定基准修正 {b15_fixed(sw2):.4f}(式 15 为 {b15(sw2):.4f})",
              f"b={b_m:.4f}(SE {sb_m:.4f}),a={a_m:.4f}",
              "通过" if abs(b_m - b15_fixed(sw2)) < 3 * sb_m + 0.03 else "偏差",
              "截面含 m<20 的观测,O(1/m²) 余项使拟合斜率高于渐近系数(单周权重最明显,见 12.7 的 m=20 一档)")
    ck.record(f"12.9.{name}", f"MC(权重 {name}):以含噪 1/D 为回归元(论文实际做法)",
              f"式 (15) {b15(sw2):.4f}", f"b={b_d:.4f}(SE {sb_d:.4f}),a={a_d:.4f};corr(X,δ)={cross:.3f}",
              "通过" if abs(b_d - b15(sw2)) < 3 * sb_d + 0.03 else "偏差",
              "用 D 代替 m 回归引入变量误差(回归稀释与 D≥5 截断),与 O(1/m²) 余项方向相反、部分抵消")
    Gb = G.mean()
    a_g, b_g, sa_g, sb_g = fit_se(((G - Gb) / Gb)**2, D)
    mc[name].update(Gbar=float(Gb), a_noisy_D_Gbar=a_g, b_noisy_D_Gbar=b_g, se_b_noisy_D_Gbar=sb_g)
    ck.record(f"12.10.{name}", f"MC(权重 {name}):基准改用样本均值 Ḡ(c10 与正文 6.3 节模拟值的口径)",
              f"式 (15) {b15(sw2):.4f}", f"b={b_g:.4f}(SE {sb_g:.4f}),Ḡ/R̄={Gb / RB:.4f}",
              "通过" if abs(b_g - b15(sw2)) < 3 * sb_g + 0.06 else "偏差",
              "Ḡ 含 R̄(1+c·E[1/m]) 的上偏,L 整体缩小,b 随之下降;正文 1.195/1.566/0.999 即此口径")

json.dump(dict(params=dict(Rbar=RB, v_R=V, k=K, rho=RHO, A=A, seed=20261018, N_per_config=N),
               exact_fixed_m=exact, monte_carlo=mc,
               effective_sw2={f"r={r},{n}": v for (r, n), v in eff.items()}),
          open(Path(__file__).resolve().parents[2] / "results" / "checks" / "c12_eq15_derivation_detail.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
ck.close()
