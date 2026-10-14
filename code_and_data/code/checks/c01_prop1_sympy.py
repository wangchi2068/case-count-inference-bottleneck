#!/usr/bin/env python3
"""命题 1 的符号验证:Poisson–Gamma 表示、PGF 卷积与二项抽稀、均值方差、得分函数、MLE、Fisher 信息、CRLB 达到条件。"""
import sympy as sp
from _common import Checker

ck = Checker("c01_prop1_sympy", "命题 1:负二项抽稀封闭性、Fisher 信息与 CRLB(sympy)")
n, k, rho, R, s, nu, C = sp.symbols("n k rho R s nu C", positive=True)

# 1) Poisson–Gamma 混合 = NB(k, p=k/(k+R)):X|nu ~ Poisson(R nu), nu ~ Gamma(shape k, rate k)
gamma_pdf = k**k / sp.gamma(k) * nu**(k - 1) * sp.exp(-k * nu)
u = sp.symbols("u", positive=True)  # u = 1 - s ∈ (0,1],避免 sympy 对 s-1 取极坐标分支
pgf_mix = sp.integrate(sp.exp(-R * nu * u) * gamma_pdf, (nu, 0, sp.oo), conds="none")
p = k / (k + R)
pgf_nb = (p / (1 - (1 - p) * s))**k
d1 = sp.simplify(pgf_mix - pgf_nb.subs(s, 1 - u))
vals = [abs(float(d1.subs({k: kv, R: Rv, u: uv}).evalf())) for kv, Rv, uv in
        [(0.35, 1.15, 0.7), (2.0, 0.8, 0.5), (0.1, 3.0, 0.1)]]
ck.record("1.1", "Poisson–Gamma 混合的 PGF = NB(k,k/(k+R)) 的 PGF", 0, f"符号差 {d1};数值最大差 {max(vals):.1e}",
          "通过" if d1 == 0 or max(vals) < 1e-12 else "不通过", "E[exp(-Rνu)] = (1+Ru/k)^(-k),u=1-s")

# 2) 个体 NB 的均值方差(由 PGF)
G = pgf_nb
mean_X = sp.simplify(sp.diff(G, s).subs(s, 1))
var_X = sp.simplify((sp.diff(G, s, 2) + sp.diff(G, s) - sp.diff(G, s)**2).subs(s, 1))
ck.record("1.2", "E[X|R], Var(X|R)(式 eq:nb_branching)", "R, R+R^2/k", f"{mean_X}, {sp.simplify(var_X)}",
          "通过" if sp.simplify(mean_X - R) == 0 and sp.simplify(var_X - (R + R**2 / k)) == 0 else "不通过")

# 3) n 个独立同分布 NB 求和:PGF 相乘 -> NB(nk, p);再二项抽稀 s -> 1-rho+rho s
G_I = G**n
G_C = G_I.subs(s, 1 - rho + rho * s)
p_star = k / (k + rho * R)
target = (p_star / (1 - (1 - p_star) * s))**(n * k)
base_ratio = sp.simplify((p / (1 - (1 - p) * (1 - rho + rho * s))) / (p_star / (1 - (1 - p_star) * s)))
ck.record("1.3", "G_C(s)=G_I(1-ρ+ρs) 化为 (p*/(1-(1-p*)s))^{nk}", 1, base_ratio,
          "通过" if base_ratio == 1 else "不通过", "两底数之比化简为 1 即同分布")
p_star_paper = sp.simplify(p / (p + rho * (1 - p)))
ck.record("1.4", "附录 p* = p/(p+ρ(1-p)) = k/(k+ρR)", sp.simplify(p_star), p_star_paper,
          "通过" if sp.simplify(p_star_paper - p_star) == 0 else "不通过")

# 4) C 的均值方差:PGF 路线与全方差公式路线
mean_C = sp.simplify(sp.diff(target, s).subs(s, 1))
var_C = sp.simplify((sp.diff(target, s, 2) + sp.diff(target, s) - sp.diff(target, s)**2).subs(s, 1))
EI, VI = n * R, n * (R + R**2 / k)
var_C_tv = sp.simplify(rho * (1 - rho) * EI + rho**2 * VI)  # E[Var(C|I)] + Var(E[C|I])
ok = sp.simplify(mean_C - rho * n * R) == 0 and sp.simplify(var_C - var_C_tv) == 0 \
     and sp.simplify(var_C - (rho * n * R + rho**2 * n * R**2 / k)) == 0
ck.record("1.5", "E[C|n,R]=ρnR;Var(C|n,R)=ρnR+ρ²nR²/k(PGF 与全方差两条路线一致)",
          "ρnR; ρnR+ρ²nR²/k", f"{mean_C}; {sp.factor(var_C)}", "通过" if ok else "不通过")
var_hat = sp.simplify(var_C / (rho * n)**2)
ck.record("1.6", "Var(C/(ρn)|n,R)(式 eq:var_prop1)", "R/(ρn)+R²/(kn)", sp.expand(var_hat),
          "通过" if sp.simplify(var_hat - (R / (rho * n) + R**2 / (k * n))) == 0 else "不通过")

# 5) 对数似然、得分、MLE
loglik = sp.loggamma(C + n * k) - sp.loggamma(n * k) - sp.loggamma(C + 1) \
         + n * k * sp.log(p_star) + C * sp.log(1 - p_star)
score = sp.simplify(sp.diff(loglik, R))
score_paper = k * (C - rho * n * R) / (R * (k + rho * R))
ck.record("1.7", "得分函数 ∂lnL/∂R(附录第 701 行)", score_paper, sp.factor(score),
          "通过" if sp.simplify(score - score_paper) == 0 else "不通过")
loglik_paper = -(n * k + C) * sp.log(k + rho * R) + C * sp.log(R)
ck.record("1.8", "附录第 697 行的对数似然(去常数)与完整对数似然的 R 导数一致", 0,
          sp.simplify(sp.diff(loglik_paper, R) - score),
          "通过" if sp.simplify(sp.diff(loglik_paper, R) - score) == 0 else "不通过")
mle = sp.solve(sp.Eq(score, 0), R)
ck.record("1.9", "得分为零的解 = C/(ρn)", C / (rho * n), mle, "通过" if mle == [C / (rho * n)] else "不通过")

# 6) Fisher 信息:三种算法
fisher_paper = n / (R / rho + R**2 / k)
info_var = sp.simplify((k / (R * (k + rho * R)))**2 * var_C)  # Var(score),score 关于 C 线性
info_neg_hess = sp.simplify(-sp.diff(loglik, R, 2).subs(C, rho * n * R))  # -E[ℓ''],ℓ'' 对 C 线性
ok = sp.simplify(info_var - fisher_paper) == 0 and sp.simplify(info_neg_hess - fisher_paper) == 0
ck.record("1.10", "Fisher 信息 = Var(score) = -E[ℓ''] = n/(R/ρ+R²/k)(式 eq:fisher_info)", fisher_paper,
          f"{sp.factor(info_var)} ; {sp.factor(info_neg_hess)}", "通过" if ok else "不通过")
ck.record("1.11", "CRLB:1/I = Var(C/(ρn))", 0, sp.simplify(1 / fisher_paper - var_hat),
          "通过" if sp.simplify(1 / fisher_paper - var_hat) == 0 else "不通过")
# 7) CRLB 达到的充要条件:score = I(R)·(T(C) − R),T(C)=C/(ρn)
lin = sp.simplify(score - fisher_paper * (C / (rho * n) - R))
ck.record("1.12", "得分可写成 I(R)·(R̂−R)(CRLB 取等的充要条件)", 0, lin,
          "通过" if lin == 0 else "不通过", "论文证明只比较了方差,没写这一条件;derivations §3.4 补上")
# 8) 泊松极限
lim = sp.limit(fisher_paper, k, sp.oo)
ck.record("1.13", "k→∞ 时 I → ρn/R(第 151 行)", rho * n / R, lim,
          "通过" if sp.simplify(lim - rho * n / R) == 0 else "不通过")
ck.close()
