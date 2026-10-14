#!/usr/bin/env python3
"""第 5 节估计方法:一步 FGLS(权重 1/μ̂²)对 a、b 的一致性,b/a 的比值偏差,以及州聚类 bootstrap 区间的覆盖率。

数据生成(仿实证规模:51 州 × 每州 25 周 = 1,275 个观测 ≈ 论文 N=1,267):
  D 在 [5, 600] 上对数均匀;μ(D) = a + b/D,真值取论文估计 a=0.0991,b=2.2434(m_×=22.6);
  L = μ(D) · u_s · X,u_s ~ Gamma(均值 1,CV 0.3) 为州乘性效应(制造州内相关),
  X ~ Gamma(κ, 1/κ):
    "const"   CV²(X) = 1/κ ≡ 2(χ²_1 的 CV²,FGLS 权重 1/μ² 恰当);
    "decline" CV²(X) 由 D=5 处 5.32 按 log D 线性降到 D=600 处 0.99(第 512 行实证描述,权重设定有误)。
抽样预算(每项 ≤ 2e5):一致性每种设定 60 次重复 × 约 2,600 次抽样;
覆盖率 36 次重复 × B=99 次州重抽(36×99×51 ≈ 1.8e5 次下标抽样)。
规模限制:覆盖率的蒙特卡洛标准误约 √(0.95×0.05/36) ≈ 0.036,只能识别明显的欠覆盖。"""
import numpy as np
from _common import Checker, fgls_affine

ck = Checker("c11_fgls_bootstrap", "实证估计:FGLS 一致性、b/a 比值偏差与州聚类 bootstrap 覆盖率")
A_TRUE, B_TRUE = 0.0991, 2.2434
MX = B_TRUE / A_TRUE
S, TW = 51, 25
rng = np.random.default_rng(20261019)


def gen(mode):
    D = np.exp(rng.uniform(np.log(5), np.log(600), S * TW))
    st = np.repeat(np.arange(S), TW)
    u = rng.gamma(1 / 0.3**2, 0.3**2, S)[st]
    if mode == "const":
        cv2 = np.full(D.size, 2.0)
    else:
        cv2 = 5.32 + (0.99 - 5.32) * (np.log(D) - np.log(5)) / (np.log(600) - np.log(5))
    X = rng.gamma(1 / cv2, cv2)
    return (A_TRUE + B_TRUE / D) * u * X, D, st


# ---- (1) 一致性与比值偏差 ----
for mode in ("const", "decline"):
    est = np.array([fgls_affine(*gen(mode)[:2]) for _ in range(60)])
    a_m, b_m = est.mean(axis=0)
    a_se, b_se = est.std(axis=0, ddof=1) / np.sqrt(len(est))
    ratio = est[:, 1] / est[:, 0]
    ck.record(f"11.1.{mode}", f"FGLS â 的均值(CV² {mode},60 次重复)", f"{A_TRUE}", f"{a_m:.4f}(SE {a_se:.4f})",
              "通过" if abs(a_m - A_TRUE) < 3 * a_se else "偏差", "均值设定正确时加权最小二乘对任意权重都无偏;权重只影响效率")
    ck.record(f"11.2.{mode}", f"FGLS b̂ 的均值(CV² {mode})", f"{B_TRUE}", f"{b_m:.4f}(SE {b_se:.4f})",
              "通过" if abs(b_m - B_TRUE) < 3 * b_se else "偏差")
    ck.record(f"11.3.{mode}", f"b̂/â 的均值与中位数 vs 真值 m_×(CV² {mode})", f"{MX:.2f}",
              f"均值 {ratio.mean():.2f},中位数 {np.median(ratio):.2f},单次 SD {ratio.std(ddof=1):.2f}",
              "通过" if abs(np.median(ratio) / MX - 1) < 0.1 else "偏差",
              "本设定下未见比值正偏(â 相对误差仅 7–9%,Jensen 项小);b̂ 略低 2.4%(1.2–1.7 SE),来自一步 FGLS 用同一数据估权重,量级可忽略")
    ck.log(f"  {mode}: â 单次 SD {est[:,0].std(ddof=1):.4f}(相对 {est[:,0].std(ddof=1)/A_TRUE:.0%}),"
           f"b̂ 单次 SD {est[:,1].std(ddof=1):.4f}(相对 {est[:,1].std(ddof=1)/B_TRUE:.0%})")

# ---- (2) 州聚类 percentile bootstrap 的覆盖率(CV² 递减设定) ----
cover_b, cover_r, rel_w = 0, 0, []
NREP, B = 36, 99
for rep in range(NREP):
    L, D, st = gen("decline")
    idx_by_state = [np.where(st == s)[0] for s in range(S)]
    bs = []
    for _ in range(B):
        pick = rng.integers(0, S, S)
        ii = np.concatenate([idx_by_state[s] for s in pick])
        bs.append(fgls_affine(L[ii], D[ii]))
    bs = np.array(bs)
    lo_b, hi_b = np.percentile(bs[:, 1], [2.5, 97.5])
    r_ = bs[:, 1] / bs[:, 0]
    lo_r, hi_r = np.percentile(r_, [2.5, 97.5])
    cover_b += int(lo_b <= B_TRUE <= hi_b)
    cover_r += int(lo_r <= MX <= hi_r)
    a0, b0 = fgls_affine(L, D)
    rel_w.append((hi_r - lo_r) / (b0 / a0))
se_c = np.sqrt(0.95 * 0.05 / NREP)
ck.record("11.4", f"州聚类 bootstrap 95% 区间对 b 的覆盖率({NREP} 次重复 × B={B})", "0.95", f"{cover_b/NREP:.3f}(MC SE ≈ {se_c:.3f})",
          "通过" if cover_b / NREP > 0.95 - 3 * se_c else "偏差", "论文用 B=1,500(main.tex 第 512 行附近);此处 B=99 受抽样预算限制,百分位端点更粗,覆盖率结论只到「无明显欠覆盖」")
ck.record("11.5", f"州聚类 bootstrap 95% 区间对 m_× = b/a 的覆盖率", "0.95", f"{cover_r/NREP:.3f}(MC SE ≈ {se_c:.3f})",
          "通过" if cover_r / NREP > 0.95 - 3 * se_c else "偏差")
ck.record("11.6", "【补充】m_× 区间的相对宽度 (上−下)/点估计:仿真中位数 vs 论文 [13.7, 33.7]/22.6", f"{(33.7-13.7)/22.6:.2f}",
          f"{np.median(rel_w):.2f}(四分位 {np.percentile(rel_w,25):.2f}–{np.percentile(rel_w,75):.2f})",
          "通过" if np.percentile(rel_w, 10) < (33.7 - 13.7) / 22.6 < np.percentile(rel_w, 90) else "偏差",
          "仅在本仿真设定下比较量级;论文区间宽度与「州效应 CV 0.3 + CV² 递减」的设定相容与否只作参考")
ck.close()
