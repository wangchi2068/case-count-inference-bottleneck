#!/usr/bin/env python3
"""第 5 节实证数值与 simulations/empirical_stats.json 的算术一致性(只读 JSON,不运行仓库脚本)。
另做理论映射:a、b 与情景区间隐含值 v_R/R̄²、A/R̄² 的比较(issues I-14)。"""
import itertools
import json
from pathlib import Path
import numpy as np
from _common import Checker

ck = Checker("c09_empirical", "实证:仿射拟合、份额分解、阶段偏差与外部验证的算术一致性")
ROOT = Path(__file__).resolve().parents[2]          # 本包根目录
d = json.load(open(ROOT / "data/empirical_stats.json", encoding="utf-8"))
E, P = d["early"], d["peak"]

def chk(cid, target, paper, val, tol, note=""):
    ck.record(cid, target, paper, f"{val:.4f}", "通过" if abs(val - paper) <= tol else "不通过", note)

# ---- 仿射拟合与 b/a ----
chk("9.1", "初期 m_×^emp = b/a(第 512 行 22.6)", 22.6, E["affine"]["b"] / E["affine"]["a"], 0.05)
chk("9.2", "剔除 1% 后 b/a(第 512 行 10.6)", 10.6, E["affine_trim1pct"]["b"] / E["affine_trim1pct"]["a"], 0.05)
chk("9.3", "十分位拟合 b/a(第 512 行 22.6)", 22.6, E["decile"]["b"] / E["decile"]["a"], 0.05)
lw = d["lag_weights_sensitivity"]
for key, paper in [("original", 22.65), ("equal_3w", 12.64), ("single_1w", 45.96)]:
    chk(f"9.4.{key}", f"滞后权重 {key} 的 b/a(表 tab:lag_weights_robustness)", paper, lw[key]["b"] / lw[key]["a"], 0.006)
ro = d["rolling_origin"]
for key, paper in [("expanding_all", 22.5), ("pool_26w", 42.7), ("state_expanding", 38.9)]:
    chk(f"9.5.{key}", f"事前滚动 {key} 的 b/a(第 551 行)", paper, ro[key]["b"] / ro[key]["a"], 0.05)
fl = d["extended_validation_flusight"]["primary_states_exante"]
chk("9.6", "FluSight 外部验证 b/a", 60.28, fl["b"] / fl["a"], 0.01)
cv = d["extended_validation_covid19"]["sensitivity_table"][0]
chk("9.7", "欧洲 COVID-19 纯事前口径 b/a", 124.66, cv["b"] / cv["a"], 0.01)
chk("9.8", "达峰期条件拟合 b/a", 119.2, P["affine_cond"]["b"] / P["affine_cond"]["a"], 0.05)

# ---- 分箱与降幅 ----
tb = {r["bin"]: r for r in E["table"]}
drop = 1 - tb["[20, 50)"]["mean"] / tb["[5, 20)"]["mean"]
chk("9.9", "[5,20)→[20,50) RelMSE 降幅(第 511 行 51.3%)", 0.513, drop, 0.0005)
nb = sum(r["N"] for r in E["table"])
ck.record("9.10", "分箱样本量之和 = 初期 N", E["N"], nb, "通过" if nb == E["N"] else "不通过")
wmean = sum(r["N"] * r["mean"] for r in E["table"]) / nb
chk("9.11", "分箱加权平均 RelMSE = 总平均 0.181", 0.181, wmean, 0.0005)
chk("9.12", "(sd/R̄_early)² ≈ 总平均 RelMSE(ddof 差异)", E["error_budget"]["total_mean_relmse"], (E["sd"] / E["R_bar"])**2, 0.002)

# ---- 误差预算份额(I-18) ----
eb = E["error_budget"]
chk("9.13", "a 份额 = a/总平均(第 554 行 54.6%)", 0.546, E["affine"]["a"] / eb["total_mean_relmse"], 0.0006)
chk("9.14", "b/D 份额(第 554 行 45.1%)", 0.451, eb["scale_share"], 0.0006)
s_a = eb["env_floor_share"] / (eb["env_floor_share"] + eb["scale_share"])
ck.record("9.15", "第 551 行「回顾口径 54.8%/45.2%」= 去掉模型外残差后重新归一的份额", "54.8%/45.2%",
          f"{100*s_a:.1f}%/{100*(1-s_a):.1f}%", "偏差",
          "同一规格在第 551 行与第 554 行用了两种归一化(54.8/45.2 vs 54.6/45.1),正文未说明(issues I-18)")
inv_mean = eb["scale_share"] * eb["total_mean_relmse"] / E["affine"]["b"]
ck.record("9.16", "【补充】由 b/D 份额反推样本 E[1/D] 与调和平均规模", "论文未给", f"E[1/D]={inv_mean:.4f},调和平均 D≈{1/inv_mean:.1f}",
          "通过", "调和平均≈27 例/周,与 m_×^emp=22.6 同量级 ⇒ 份额约各半是 m_× 定义的直接推论")
rl = d["realized_large_scale"]
chk("9.17", "D≥250 组平均 RelMSE(第 554 行 0.104)", 0.104, rl["mean_loss"], 0.0005)
ck.record("9.18", "D≥250 观测数", 244, rl["N"], "通过" if rl["N"] == 244 else "不通过")
chk("9.19", "大规模组 / 全体 = 「约六成」", 0.6, rl["mean_loss"] / rl["overall_mean_loss"], 0.05)

# ---- 达峰期偏差项 ----
bias = (E["R_bar"] - P["R_bar"])**2 / E["R_bar"]**2
chk("9.20", "常数偏差项 (R̄_early-R̄_peak)²/R̄_early²", P["bias_term"], bias, 1e-6)
var_term = P["sd"]**2 / E["R_bar"]**2
share = bias / (bias + var_term)
chk("9.21", "偏差份额(第 585 行 88.9%)", 0.889, share, 0.0006)
su = d["stage_scale_audit"]
chk("9.22", "未归一 b_early = b·R̄_early²", su["unnormalized"]["b_early"], E["affine"]["b"] * E["R_bar"]**2, 1e-3)
chk("9.23", "未归一 b_peak = b_peak,cond·R̄_peak²", su["unnormalized"]["b_peak"], P["affine_cond"]["b"] * P["R_bar"]**2, 1e-3)
chk("9.24", "共同分母 b_peak = 未归一 b_peak / R̄_early²(FGLS 尺度等变)", su["fgls_sep"]["b_peak"],
    su["unnormalized"]["b_peak"] / E["R_bar"]**2, 1e-3)

# ---- 其他 ----
w = np.array([0.65, 0.25, 0.10])
chk("9.25", "平均回溯延迟 Σ s·w_s(第 441 行 1.45 周)", 1.45, float(np.dot([1, 2, 3], w)), 1e-9)
ck.record("9.26", "1.45 周换算天数(第 441 行「约 10.2 天」)", "10.2", f"{1.45*7:.2f}", "通过", "10.15 四舍五入为 10.2")
pol = d["policy"]
ratio = pol["period2_voluntary"]["g_std"] / pol["period1_mandatory"]["g_std"]
chk("9.27", "自愿期 SD 扩张(第 613 行 192.1%)", 1.921, ratio - 1, 0.0006)
bound = np.sqrt(pol["period1_mandatory"]["coverage_mean"] / pol["period2_voluntary"]["coverage_mean"])
ck.record("9.28", "【补充】若覆盖率下降只是均匀二项漏报,G 的 SD 至多放大 √(ρ1/ρ2)", f"≤ {bound:.2f} 倍", f"实测 {ratio:.2f} 倍",
          "偏差", "2.9 倍远超纯抽稀上界 1.29 倍 ⇒ 支持论文「结构性非随机扰动」解释;与命题 3 的联系只能是定性的(issues I-21)")
na = d["national"]
ck.record("9.29", "全国汇总:N 与 RelMSE(第 617 行 0.0348,N=28)", "0.0348; 28", f"{na['relmse_mean']:.4f}; {na['N_early']}",
          "通过" if abs(na["relmse_mean"] - 0.0348) < 5e-5 and na["N_early"] == 28 else "不通过", "N=28 很小,宜给区间")
cbar = (na["relmse_mean"] / E["affine"]["a"] - 1 / 51) / (1 - 1 / 51)
ck.record("9.30", "【补充】若把州级 a 全视为环境项,由 v_agg/v = c̄+(1-c̄)/J 反推 c̄", "论文未估计", f"c̄≈{cbar:.2f}", "通过",
          "粗略量级;忽略了全国序列的抽样项和州间方差不等(issues I-20)")

# ---- 理论映射:a、b 与情景区间隐含值(I-14) ----
Rb = 1.67
imp_a, imp_b, mx = [], [], []
for k, rho, v in itertools.product((0.2, 0.5), (0.0056, 0.021), (0.04, 0.08)):
    A = Rb + rho * (Rb**2 + v) / k
    imp_a.append(v / Rb**2); imp_b.append(A / Rb**2); mx.append(A / v)
ck.record("9.31", "截距 a 与情景隐含 v_R/R̄²(第 508 行称「0.0991 与 0.014–0.029 相符」)", f"{min(imp_a):.3f}–{max(imp_a):.3f}",
          f"a={E['affine']['a']:.4f},为隐含值的 {E['affine']['a']/max(imp_a):.1f}–{E['affine']['a']/min(imp_a):.1f} 倍", "不通过",
          "数量上不相符;论文同段又说 a 混入了代理偏差,应删去「相符」")
ck.record("9.32", "斜率 b 与情景隐含 A/R̄²", f"{min(imp_b):.3f}–{max(imp_b):.3f}",
          f"b={E['affine']['b']:.4f},为隐含值的 {E['affine']['b']/max(imp_b):.1f}–{E['affine']['b']/min(imp_b):.1f} 倍", "偏差",
          "b 同样被放大(随机分母等,见 c10);m_× 的「数量级相符」来自分子分母同向放大")
ck.close()
