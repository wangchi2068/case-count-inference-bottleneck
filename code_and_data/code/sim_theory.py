"""图 2–4 的理论量与模拟量(新写,不调用仓库原脚本)。

1. 方差蒙特卡洛:目标Ⅰ(R_t 固定)与目标Ⅱ(R_t 随环境波动)下 C_t/(ρn) 的方差,
   每个规模 20,000 次(旧稿 50,000 次;命题 1、2 是精确等式,缩小规模只影响 MC 误差)。
2. 增长检验:精确负二项检验与 Wald 检验的实际水平、精确功效、80% 功效所需规模——全部用
   负二项分布函数精确计算,不做模拟(旧稿 Wald 水平是 30,000 次模拟值)。
3. 更新过程:与旧稿同一数据生成过程(4 周核 w=(0.45,0.35,0.15,0.05)、Gamma 环境、I_t>=1 截断),
   每个初始规模 400 条轨迹 × 26 个预测起点(旧稿 150 条),同时记录每个评价点的实现规模 D_t。
结果逐段写入 derived/sim_theory.json,进度逐行写入 logs/sim_theory.log。
"""
from __future__ import annotations

import json
import time

import numpy as np
from scipy import stats

from figstyle import RESULTS, logger

log = logger("sim_theory")
R_BAR, V_R, K, RHO = 1.15, 0.04, 0.35, 0.25
A = R_BAR + RHO * (R_BAR**2 + V_R) / K
M_X = A / V_R
OUT = RESULTS / "sim_theory.json"


def dump(res):
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1))


def variance_mc(res, reps=20_000, seed=20261013):
    rng = np.random.default_rng(seed)
    g_shape, g_scale = R_BAR**2 / V_R, V_R / R_BAR
    rows = []
    for m in [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]:
        n = int(round(m / RHO))
        # 目标Ⅰ:R_t = R̄ 固定
        p1 = K / (K + RHO * R_BAR)
        c1 = rng.negative_binomial(n * K, p1, size=reps)
        v1 = float(np.var(c1 / (RHO * n), ddof=1))
        th1 = (R_BAR + RHO * R_BAR**2 / K) / m
        # 目标Ⅱ:R_t ~ Gamma(均值 R̄, 方差 v_R)
        r = rng.gamma(g_shape, g_scale, size=reps)
        c2 = rng.negative_binomial(n * K, K / (K + RHO * r))
        est2 = c2 / (RHO * n)
        v2 = float(np.mean((est2 - R_BAR) ** 2))
        th2 = V_R + A / m
        # 方差估计的 95% 区间(按 4 阶矩近似)
        se1 = float(np.sqrt((np.mean((c1 / (RHO * n) - c1.mean() / (RHO * n)) ** 4) - v1**2) / reps))
        se2 = float(np.sqrt((np.mean((est2 - R_BAR) ** 4) - v2**2) / reps))
        rows.append({"m": m, "n": n, "var_I": v1, "se_I": se1, "theory_I": th1,
                     "var_II": v2, "se_II": se2, "theory_II": th2,
                     "ratio_I": v1 / th1, "ratio_II": v2 / th2})
        log(f"[var-mc] m={m} n={n}: I {v1:.5f}/{th1:.5f}={v1/th1:.4f}; II {v2:.5f}/{th2:.5f}={v2/th2:.4f}")
    res["variance_mc"] = {"reps": reps, "seed": seed, "rows": rows,
                          "params": {"R_bar": R_BAR, "v_R": V_R, "k": K, "rho": RHO, "A": A, "m_x": M_X}}
    dump(res)


def growth_test(res, alpha=0.05):
    z = stats.norm.ppf(1 - alpha)
    out = {"alpha": alpha, "rho": RHO, "size": {}, "required": {}}
    for k in [0.1, 0.35, 1.0]:
        n = np.arange(1, 801)
        r, p0 = n * k, k / (k + RHO)
        c = stats.nbinom.ppf(1 - alpha, r, p0) + 1
        sf = stats.nbinom.sf(c - 1, r, p0)
        bump = sf > alpha                       # 浮点边界保护
        c = np.where(bump, c + 1, c)
        size_exact = stats.nbinom.sf(c - 1, r, p0)
        v0 = 1 / (RHO * n) + 1 / (k * n)
        cw = np.ceil(RHO * n * (1 + z * np.sqrt(v0)) - 1e-12)
        size_wald = stats.nbinom.sf(cw - 1, r, p0)
        out["size"][str(k)] = {"m": (RHO * n).tolist(), "exact": size_exact.tolist(),
                               "wald": size_wald.tolist()}
        i5 = int(np.where(n == 20)[0][0])
        log(f"[size] k={k}: max exact={size_exact.max():.4f}; Wald at m=5 {size_wald[i5]:.4f}; "
            f"Wald max over m<40 = {size_wald[RHO * n < 40].max():.4f}")
    nmax = 20000
    n = np.arange(1, nmax + 1)
    for k in [0.1, 0.35, 1.0]:
        r, p0 = n * k, k / (k + RHO)
        c = stats.nbinom.ppf(1 - alpha, r, p0) + 1
        c = np.where(stats.nbinom.sf(c - 1, r, p0) > alpha, c + 1, c)
        rows = []
        for d in np.round(np.arange(0.10, 0.601, 0.025), 3):
            p1 = k / (k + RHO * (1 + d))
            pw = stats.nbinom.sf(c - 1, r, p1)
            ok = pw >= 0.8
            if not ok.any():
                continue
            first = int(n[np.argmax(ok)])
            bad = np.where(~ok)[0]
            stable = int(n[bad[-1] + 1]) if len(bad) else 1
            if stable >= nmax:
                continue
            rows.append({"delta": float(d), "n_first": first, "n_stable": stable,
                         "m_first": RHO * first, "m_stable": RHO * stable})
        out["required"][str(k)] = rows
        log(f"[power] k={k}: " + "; ".join(f"δ={x['delta']}: n {x['n_first']}/{x['n_stable']}" for x in rows
                                            if x['delta'] in (0.15, 0.25, 0.3, 0.5)))
    res["growth_test"] = out
    dump(res)


def renewal(res, reps=400, seed=20261014):
    rng = np.random.default_rng(seed)
    w = np.array([0.45, 0.35, 0.15, 0.05])
    S, T = len(w), 30
    g_shape, g_scale = R_BAR**2 / V_R, V_R / R_BAR
    groups = []
    points = []
    for m0 in [6, 12, 25, 50, 100, 200, 400, 800]:
        t0 = time.time()
        lam0 = m0 / RHO
        losses, ds, zero, trunc = [], [], 0, 0
        for _ in range(reps):
            I = np.zeros(T)
            Cc = np.zeros(T)
            I[:S] = lam0
            Cc[:S] = rng.binomial(int(lam0), RHO, size=S)
            for t in range(S, T):
                rt = rng.gamma(g_shape, g_scale)
                lam = np.sum(w * I[t - S:t][::-1])
                it = rng.negative_binomial(lam * K, K / (K + rt))
                trunc += int(it < 1)
                I[t] = max(1, it)
                Cc[t] = rng.binomial(int(I[t]), RHO)
                d = np.sum(w * Cc[t - S:t][::-1])
                if d <= 0:
                    zero += 1
                    continue
                losses.append(((Cc[t] / d - R_BAR) / R_BAR) ** 2)
                ds.append(d)
        losses, ds = np.array(losses), np.array(ds)
        ref_init = (V_R + A / m0) / R_BAR**2
        ref_real = (V_R + A / ds) / R_BAR**2
        se = losses.std(ddof=1) / np.sqrt(len(losses))
        g = {"m0": m0, "N": int(len(losses)), "zero_D": zero, "mean": float(losses.mean()), "se": float(se),
             "ref_init": ref_init, "ratio_init": float(losses.mean() / ref_init),
             "mean_ref_real": float(ref_real.mean()), "ratio_real": float(losses.mean() / ref_real.mean()),
             "median_D_over_m0": float(np.median(ds) / m0),
             "trunc_share": trunc / (reps * (T - S))}
        groups.append(g)
        points.append((ds, losses))
        log(f"[renewal] m0={m0}: N={g['N']} zero={zero} mean={g['mean']:.4f} ref={ref_init:.4f} "
            f"ratio_init={g['ratio_init']:.3f} ratio_real={g['ratio_real']:.3f} "
            f"medD/m0={g['median_D_over_m0']:.2f} trunc={g['trunc_share']:.4f} ({time.time() - t0:.1f}s)")
    ds = np.concatenate([p[0] for p in points])
    ls = np.concatenate([p[1] for p in points])
    edges = np.geomspace(4, 4000, 16)
    bins = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        sel = (ds >= lo) & (ds < hi)
        if sel.sum() < 200:
            continue
        x, l = ds[sel], ls[sel]
        ref = (V_R + A / x) / R_BAR**2
        bins.append({"lo": float(lo), "hi": float(hi), "N": int(sel.sum()), "mean_D": float(x.mean()),
                     "mean": float(l.mean()), "se": float(l.std(ddof=1) / np.sqrt(sel.sum())),
                     "mean_ref": float(ref.mean()), "ratio": float(l.mean() / ref.mean())})
        log(f"[renewal-bin] D∈[{lo:.1f},{hi:.1f}): N={sel.sum()} ratio={bins[-1]['ratio']:.3f}")
    res["renewal"] = {"reps": reps, "seed": seed, "T": T, "eval_per_traj": T - S, "w": w.tolist(),
                      "groups": groups, "realised_bins": bins}
    dump(res)


if __name__ == "__main__":
    res = {}
    t0 = time.time()
    log("start")
    variance_mc(res)
    growth_test(res)
    renewal(res)
    log(f"done in {time.time() - t0:.1f}s")
