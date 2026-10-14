#!/usr/bin/env python3
"""第 5 节实证映射(issues I-13/I-14):截面蒙特卡洛检验「随机分母」能否解释 b 的放大与三种滞后权重下 b 的排序。

模型(单个观测 = 一个州-周):
  m = ρΛ 在 [5, 600] 上对数均匀(调和平均 ≈ 24,接近实证 E[1/D] 反推的 27);
  过去三周真实感染 I_s ≡ Λ(平稳),真实感染压力 Λ = Σ w_s I_s;
  R ~ Gamma(均值 R̄, 方差 v_R),I_{t+1} | Λ,R ~ NB(kΛ, 均值 ΛR)(Poisson–Gamma);
  报告 C | I 为二项 Bin(I, ρ),或方差 φ·ρI 的过离散报告;
  分母 D = Σ w_s C_s 用**报告**病例构造(实证口径),G = C_{t+1}/D,L = ((G - Ḡ)/Ḡ)²,
  一步 FGLS 拟合 L = a + b/D(权重 1/μ̂²)。
理论预测(一阶 delta 法,见 derivations.md §12.4):
  D 精确(= ρΛ)时      a → v_R/R̄²,b → A/R̄²,A = R̄ + ρ(R̄²+v_R)/k
  D 含二项噪声时      b → [A + (1-ρ)(R̄²+v_R)Σw²]/R̄²
  报告方差 φρI 时     b → [φR̄ + ρR̄ + ρ(R̄²+v_R)/k + φ(R̄²+v_R)Σw²]/R̄²
每个配置 18,000 个观测,随机抽样 ≤ 2e5 次。"""
import json
from pathlib import Path
import numpy as np
from _common import Checker, fgls_affine

ck = Checker("c10_random_denominator", "实证映射:随机分母与报告过离散对 a、b、m_× 的影响")
ROOT = Path(__file__).resolve().parents[2]
emp = json.load(open(ROOT / "data/empirical_stats.json", encoding="utf-8"))
lw = emp["lag_weights_sensitivity"]

RB, V, K, RHO = 1.67, 0.06, 0.35, 0.021          # 第 515 行情景区间的中点附近
ER2 = RB**2 + V
A = RB + RHO * ER2 / K
WEIGHTS = {"original": np.array([0.65, 0.25, 0.10]),
           "single": np.array([1.0, 0.0, 0.0]),
           "equal": np.full(3, 1 / 3)}
N, NB_ = 18_000, 6


def simulate(rng, w, mode, phi=1.0):
    m = np.exp(rng.uniform(np.log(5), np.log(600), N))
    Lam = np.round(m / RHO)
    R = rng.gamma(RB**2 / V, V / RB, N)
    I1 = rng.poisson(rng.gamma(K * Lam, R / K))

    def report(I):
        if phi == 1.0:
            return rng.binomial(I.astype(np.int64), RHO).astype(float)
        mu = RHO * I
        return rng.poisson(rng.gamma(np.maximum(mu, 1e-9) / (phi - 1), phi - 1)).astype(float)

    C1 = report(I1)
    if mode == "exact":
        D = RHO * Lam
    else:
        D = sum(ws * report(Lam) for ws in w if ws > 0)
    ok = D >= 5                                   # 实证样本的 D ≥ 5 筛选
    return C1[ok] / D[ok], D[ok]


def fit(G, D):
    Gbar = G.mean()
    L = ((G - Gbar) / Gbar)**2
    a, b = fgls_affine(L, D)
    # 批均值标准误(6 批 × 3,000)
    ab = np.array([fgls_affine(Lb, Db) for Lb, Db in zip(np.array_split(L, NB_), np.array_split(D, NB_))])
    se = ab.std(axis=0, ddof=1) / np.sqrt(NB_)
    return a, b, se[0], se[1], Gbar


def pred_b(sw2, phi=1.0, noisy=True):
    if phi == 1.0:
        return (A + ((1 - RHO) * ER2 * sw2 if noisy else 0.0)) / RB**2
    return (phi * RB + RHO * RB + RHO * ER2 / K + phi * ER2 * sw2) / RB**2


rng = np.random.default_rng(20261018)
res = {}
# ---- (1) 验证映射:D 精确时 FGLS 截距与斜率是否回到 v_R/R̄²、A/R̄² ----
G, D = simulate(rng, WEIGHTS["original"], "exact")
a, b, sa, sb, gb = fit(G, D)
ck.record("10.1", "D=ρΛ 精确时 FGLS 截距 a → v_R/R̄²", f"{V/RB**2:.4f}", f"{a:.4f}(SE {sa:.4f})",
          "通过" if abs(a - V / RB**2) < 3 * sa + 0.002 else "不通过", "验证「a 对应环境底板」的映射本身")
ck.record("10.2", "D=ρΛ 精确时 FGLS 斜率 b → A/R̄²", f"{pred_b(0, noisy=False):.4f}", f"{b:.4f}(SE {sb:.4f})",
          "通过" if abs(b - pred_b(0, noisy=False)) < 3 * sb + 0.02 else "不通过", "验证「b 对应单代抽样项」的映射本身")

# ---- (2) 二项报告 + 用报告病例构造分母:三种滞后权重 ----
for name, w in WEIGHTS.items():
    G, D = simulate(rng, w, "noisy")
    a, b, sa, sb, gb = fit(G, D)
    res[name] = (a, b)
    sw2 = float(np.sum(w**2))
    ck.record(f"10.3.{name}", f"二项报告、分母含噪(权重 {name},Σw²={sw2:.3f}):b vs delta 法预测",
              f"{pred_b(sw2):.4f}(无分母噪声时 {pred_b(0, noisy=False):.4f})", f"{b:.4f}(SE {sb:.4f})",
              "通过" if abs(b - pred_b(sw2)) < 3 * sb + 0.03 else "偏差",
              "分母的二项噪声使 b 增加 (1-ρ)(R̄²+v_R)Σw²/R̄²,与 Σw² 成正比")
    ck.record(f"10.4.{name}", f"二项报告、分母含噪(权重 {name}):a 不受分母噪声影响", f"{V/RB**2:.4f}", f"{a:.4f}(SE {sa:.4f})",
              "通过" if abs(a - V / RB**2) < 3 * sa + 0.003 else "偏差", "分母噪声是 O(1/m) 项,只进斜率")
    ck.log(f"  {name}: Ḡ={gb:.4f}, b/a={b/a:.1f}(理论 A/v_R={A/V:.1f})")
    if name == "original":
        ck.record("10.9", "【补充】分母含噪时 b/a 是否仍估计 m_× = A/v_R(原始权重)", f"{A/V:.1f}", f"{b/a:.1f}", "偏差",
                  "只有斜率被放大 ⇒ b/a 高估 m_×;实证 a 也被放大,两者部分抵消,所以 22.6 与情景区间「同量级」不能当作结构验证(issues I-14)")

# ---- (3) 排序:单周 > 原始 > 等权,和实证 b 的比值对照 ----
emp_b = {"original": lw["original"]["b"], "single": lw["single_1w"]["b"], "equal": lw["equal_3w"]["b"]}
for name in ("single", "equal"):
    pr = pred_b(float(np.sum(WEIGHTS[name]**2))) / pred_b(float(np.sum(WEIGHTS["original"]**2)))
    mc = res[name][1] / res["original"][1]
    er = emp_b[name] / emp_b["original"]
    ck.record(f"10.5.{name}", f"b_{name}/b_original:delta 法 / MC / 实证(表 tab:lag_weights_robustness)",
              f"delta {pr:.3f}", f"MC {mc:.3f};实证 {er:.3f}", "通过" if abs(er - pr) < 0.15 else "偏差",
              "固定 R̄ 下的比值;实证三种权重的 R̄ 不同(1.48/1.67/1.99),只作方向与量级对照")

# ---- (4) 水平:二项分母噪声能解释多少 b 的放大;要多大的报告过离散 φ 才补足 ----
sw2o = float(np.sum(WEIGHTS["original"]**2))
b_emp = emp_b["original"]
phi_need = (b_emp * RB**2 - RHO * RB - RHO * ER2 / K) / (RB + ER2 * sw2o)
ck.record("10.6", "二项分母噪声单独能解释的 b 水平(原始权重)", f"实证 b={b_emp:.4f}",
          f"预测 {pred_b(sw2o):.4f}(实证的 {pred_b(sw2o)/b_emp:.0%});无分母噪声 {pred_b(0, noisy=False):.4f}({pred_b(0, noisy=False)/b_emp:.0%})",
          "偏差", f"剩余缺口可由报告过离散 φ≈{phi_need:.2f} 补足(报告方差 φ·ρI);这是一种可能解释,不是唯一解释")
G, D = simulate(rng, WEIGHTS["original"], "noisy", phi=round(phi_need, 2))
a, b, sa, sb, gb = fit(G, D)
ck.record("10.7", f"过离散报告 φ={phi_need:.2f}、原始权重:b MC vs 预测", f"{pred_b(sw2o, phi=round(phi_need, 2)):.4f}",
          f"{b:.4f}(SE {sb:.4f}),a={a:.4f}", "通过" if abs(b - pred_b(sw2o, phi=round(phi_need, 2))) < 3 * sb + 0.05 else "偏差",
          "一阶 delta 法在分母噪声大时高估约 5–10%(含噪回归元 1/D 的回归稀释与 D≥5 截断,同见 10.3.single);"
          "量级结论不变:φ≈2 时 b 接近实证水平,但 a 仍停在 v_R/R̄²,a 的放大需另找来源")

# ---- (5) a 的放大与平均滞后同向(只用论文数字,不做仿真) ----
lags = {"single": 1.0, "original": 1.45, "equal": 2.0}
emp_a = {"original": lw["original"]["a"], "single": lw["single_1w"]["a"], "equal": lw["equal_3w"]["a"]}
order = sorted(lags, key=lags.get)
mono = all(emp_a[order[i]] < emp_a[order[i + 1]] for i in range(2))
ck.record("10.8", "【补充】实证截距 a 随平均回溯延迟单调增大(单周 1.0 / 原始 1.45 / 等权 2.0 周)", "若 a 只是环境方差则应与权重无关",
          "; ".join(f"{n}: a={emp_a[n]:.4f}" for n in order), "通过" if mono else "偏差",
          "支持「a 混入了周增长比与世代再生数的口径偏差」:回溯越远,G 越多地吸收增长趋势的异质性(issues I-12、I-14)")
ck.close()
