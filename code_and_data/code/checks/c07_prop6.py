#!/usr/bin/env python3
"""命题 6(正文编号):精确负二项增长检验。MLR、临界值、精确水平与功效、图 2 的样本量、Wald 检验的精确水平。"""
import numpy as np
import sympy as sp
from scipy import stats
from _common import Checker

ck = Checker("c07_prop6", "命题 6:超临界增长的精确离散检验与功效")
ALPHA, RHO = 0.05, 0.25

# ---- (i) MLR 符号推导 ----
j, k, rho, n, R0, R1 = sp.symbols("j k rho n R0 R1", positive=True)
p = lambda R: k / (k + rho * R)
logLR = n * k * (sp.log(p(R1)) - sp.log(p(R0))) + j * (sp.log(1 - p(R1)) - sp.log(1 - p(R0)))
slope = sp.simplify(sp.diff(logLR, j))
target = sp.log((R1 * (k + rho * R0)) / (R0 * (k + rho * R1)))
ck.record("7.1", "log 似然比关于 j 的斜率 = log[(1-p*(R1))/(1-p*(R0))](Γ(j+nk)/j! 相消)", target, slope,
          "通过" if sp.simplify(sp.expand_log(slope - target, force=True)) == 0 else "不通过")
# R1>R0 时斜率 > 0:(1-p*) = ρR/(k+ρR) 关于 R 递增
dq = sp.simplify(sp.diff(rho * R0 / (k + rho * R0), R0))
ck.record("7.2", "1-p* = ρR/(k+ρR) 关于 R 严格递增 ⇒ MLR", "ρk/(k+ρR)² > 0", dq, "通过" if sp.simplify(dq - rho * k / (k + rho * R0)**2) == 0 else "不通过")

def crit(nv, kv, rhov=RHO, alpha=ALPHA):
    r_, p0 = nv * kv, kv / (kv + rhov)
    c = int(stats.nbinom.isf(alpha, r_, p0))     # 初值
    while c > 0 and stats.nbinom.sf(c - 2, r_, p0) <= alpha:   # Pr(C ≥ c-1) ≤ α 则继续下移
        c -= 1
    while stats.nbinom.sf(c - 1, r_, p0) > alpha:              # Pr(C ≥ c) > α 则上移
        c += 1
    return c

def power(nv, kv, delta, rhov=RHO):
    c = crit(nv, kv, rhov)
    return stats.nbinom.sf(c - 1, nv * kv, kv / (kv + rhov * (1 + delta)))

# 数值 MLR:随机抽 (n,k,R0<R1),检查似然比在 j=0..500 单调
rng = np.random.default_rng(7)
viol = 0
for _ in range(200):
    nv, kv = rng.integers(1, 500), rng.uniform(0.05, 3)
    a, b = np.sort(rng.uniform(0.2, 3, 2))
    js = np.arange(0, 500)
    lr = stats.nbinom.logpmf(js, nv * kv, kv / (kv + RHO * b)) - stats.nbinom.logpmf(js, nv * kv, kv / (kv + RHO * a))
    viol += int(np.any(np.diff(lr) <= 0))
ck.record("7.3", "数值 MLR:200 组随机 (n,k,R0<R1) 的似然比在 j=0..499 严格递增", "0 次违例", f"{viol} 次违例", "通过" if viol == 0 else "不通过")

# 尾概率关于 R 单调不减 ⇒ sup 在 R=1
nv, kv = 100, 0.35
c = crit(nv, kv)
Rs = np.linspace(0.3, 1.0, 71)
tails = stats.nbinom.sf(c - 1, nv * kv, kv / (kv + RHO * Rs))
ck.record("7.4", "Pr_R(C ≥ c_α) 在 R∈[0.3,1] 上单调不减,上确界在 R=1(n=100,k=0.35)", f"max 在 R=1:{tails[-1]:.4f}",
          f"单调={bool(np.all(np.diff(tails) >= 0))},max={tails.max():.4f}", "通过" if np.all(np.diff(tails) >= 0) else "不通过")

# ---- 精确水平 ≤ α,且通常严格小于 ----
sizes, eq_count = [], 0
for kv in (0.1, 0.35, 1.0):
    for nv in range(1, 3001):
        c = crit(nv, kv)
        sz = stats.nbinom.sf(c - 1, nv * kv, kv / (kv + RHO))
        sizes.append(sz)
        eq_count += int(abs(sz - ALPHA) < 1e-12)
ck.record("7.5", "精确检验的实际水平(k∈{0.1,0.35,1},n=1..3000)", "≤ 0.05", f"最大 {max(sizes):.5f},最小 {min(sizes):.5f},等于 α 的个数 {eq_count}",
          "通过" if max(sizes) <= ALPHA else "不通过", "第 340 行「严格低于 α」应为「不超过 α」:恒成立的是 ≤,严格 < 只在一般位置成立")
# c_α(n) 单调不减;功效关于 n 的锯齿
for kv in (0.1, 0.35):
    cs = [crit(nv, kv) for nv in range(1, 3001)]
    mono = all(np.diff(cs) >= 0)
    ck.record(f"7.6.k{kv}", f"c_α(n) 关于 n 单调不减(k={kv},n=1..3000;附录第 758 行)", "单调不减", "是" if mono else "否",
              "通过" if mono else "不通过")
pw = np.array([power(nv, 0.35, 0.3) for nv in range(400, 700)])
ndrop = int(np.sum(np.diff(pw) < 0))
ck.record("7.7", "功效 π(n,δ) 关于 n 非单调(k=0.35,δ=0.3,n=400..699)", "存在下降", f"{ndrop} 处下降", "通过" if ndrop > 0 else "不通过",
          "故最小样本量需逐点枚举(附录第 758 行)")

# ---- 图 2(b)(c):首次功效 ≥ 0.8 的最小 n ----
def first_n(kv, delta, nmax=8000):
    for nv in range(1, nmax):
        if power(nv, kv, delta) >= 0.8:
            return nv
    return None

def stable_n(kv, delta, n0, span=400):
    """首次越过 0.8 之后,是否还会因锯齿跌回 0.8 以下"""
    back = [nv for nv in range(n0, n0 + span) if power(nv, kv, delta) < 0.8]
    return back

for kv, delta, paper_m in [(0.35, 0.15, 517.8), (0.35, 0.30, 142.0), (0.35, 0.50, 57.2), (1.0, 0.25, 142.0), (0.1, 0.25, 415.0)]:
    n0 = first_n(kv, delta)
    back = stable_n(kv, delta, n0)
    ck.record(f"7.8.k{kv}.d{delta}", f"图 2:k={kv},δ={delta} 时功效首次 ≥0.8 的 m=ρn", f"m={paper_m}",
              f"n={n0},m={RHO*n0:.2f};此后 400 个 n 内跌回 <0.8 的有 {len(back)} 个",
              "通过" if abs(RHO * n0 - paper_m) < 0.06 else "不通过",
              "" if not back else f"首个跌回点 n={back[0]},论文「首次满足」规则下所报 m 之后功效并不稳定 ≥0.8")
# 【补充】稳定样本量:此后(检查到 +1500)功效始终 ≥0.8 的最小 n
for kv, delta in [(0.35, 0.15), (0.35, 0.30), (0.35, 0.50), (1.0, 0.25), (0.1, 0.25)]:
    n0 = first_n(kv, delta)
    pws = np.array([power(nv, kv, delta) for nv in range(n0, n0 + 2000)])
    bad = np.where(pws < 0.8)[0]
    n_st = n0 + (bad.max() + 1 if bad.size else 0)
    ck.record(f"7.13.k{kv}.d{delta}", f"【补充】稳定达到 80% 功效的最小 n(k={kv},δ={delta})", f"首次 n={n0}",
              f"稳定 n={n_st}(m={RHO*n_st:.2f},比首次多 {100*(n_st/n0-1):.1f}%)", "通过",
              "建议图 2 同时报告「此后恒 ≥0.8」的稳定样本量")
n_k1, n_k01 = first_n(1.0, 0.25), first_n(0.1, 0.25)
ck.record("7.9", "k 从 1.0 到 0.1 时样本需求的放大倍数(图 2(c)「近 3 倍」)", "≈3", f"{n_k01/n_k1:.2f}", "通过" if 2.7 < n_k01 / n_k1 < 3.1 else "偏差")

# ---- Wald 检验的精确水平(用 NB 分布逐项求和,不需 MC) ----
z = stats.norm.ppf(1 - ALPHA)
def wald_size(m_, kv, R=1.0):
    nv = m_ / RHO
    V0 = 1 / (RHO * nv) + 1 / (kv * nv)
    thr = RHO * nv * (1 + z * np.sqrt(V0))          # 拒绝 ⇔ C ≥ thr
    cthr = int(np.ceil(thr - 1e-12))
    return stats.nbinom.sf(cthr - 1, nv * kv, kv / (kv + RHO * R))

for m_, kv, paper in [(5, 0.1, 0.081), (5, 1.0, 0.0495), (10, 1.0, 0.0691)]:
    ws = wald_size(m_, kv)
    # 30,000 次 MC 的 2σ 带
    band = 2 * np.sqrt(ws * (1 - ws) / 30000)
    ck.record(f"7.10.m{m_}.k{kv}", f"Wald 检验精确水平(m={m_},k={kv};第 358、364 行 MC 报告值 {paper})", f"{paper}",
              f"{ws:.4f}(30,000 次 MC 的 ±2σ 带 ±{band:.4f})", "通过" if abs(ws - paper) < band + 0.0005 else "偏差")
# 小 MC 复核其中一点
g = np.random.default_rng(20261016)
nv = 5 / RHO
Cs = g.negative_binomial(nv * 0.1, 0.1 / (0.1 + RHO), 200_000)
V0 = 1 / (RHO * nv) + 1 / (0.1 * nv)
emp = np.mean((Cs / (RHO * nv) - 1) / np.sqrt(V0) >= z)
ck.record("7.11", "Wald 水平 MC 复核(m=5,k=0.1,2e5 次)", f"{wald_size(5, 0.1):.4f}", f"{emp:.4f}",
          "通过" if abs(emp - wald_size(5, 0.1)) < 3 * np.sqrt(emp * (1 - emp) / 2e5) else "不通过")
# Wald 在 m<40 段过检(第 365 行「全低规模段系统性过检」)
over = [(m_, kv, wald_size(m_, kv)) for kv in (0.1, 0.35) for m_ in (5, 10, 15, 20, 25, 30, 35)]
ck.log("Wald 精确水平表 (m, k, size):", [(a, b, round(c, 4)) for a, b, c in over])
n_over = sum(1 for _, _, sz in over if sz > ALPHA)
ck.record("7.12", "k≤0.35、m<40 网格上 Wald 精确水平 > 0.05 的比例(「系统性过检」)", "全部 > 0.05", f"{n_over}/{len(over)}",
          "通过" if n_over == len(over) else "偏差", "离散性造成锯齿,个别点可能低于名义水平")
ck.close()
