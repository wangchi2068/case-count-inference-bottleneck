"""学位论文第五、六章的表格数字与新增数据图。

只读取新稿已有的结果文件(empirical_stats.json、nhsn_bins.json、c10_random_denominator.json),
不改数据口径、不重新拟合。表格数字写到 thesis/derived/thesis_tables.json,
第六章新增的「各基准分箱损失」图写到 thesis/figures。
"""
from __future__ import annotations

import json

import numpy as np

import figstyle as fs

THESIS = fs.WORK / "thesis"
fs.FIG_DIR = THESIS / "figures"
OUT = THESIS / "derived"
OUT.mkdir(parents=True, exist_ok=True)

log = fs.logger("thesis_empirical")
fs.apply_style()
import matplotlib.pyplot as plt  # noqa: E402

ST = fs.load_stats()
BINS = json.loads((fs.DERIVED / "nhsn_bins.json").read_text())
BIN_SHORT = ["5–20", "20–50", "50–100", "100–250", "250–600", "≥600"]


def r(x, n=4):
    return None if x is None else round(float(x), n)


rec: dict = {}

# ---------- 表 5-1 三个填报制度期 ----------
pol = ST["policy"]
rec["tab_5_1_policy"] = {
    k: {s: r(pol[k][s]) for s in ["N", "coverage_mean", "coverage_median", "g_mean", "g_std",
                                  "g_iqr", "g_mad", "g_skew", "g_max", "g_p10", "g_p90"]}
    for k in ["period1_mandatory", "period2_voluntary", "period3_remandated"]
}
rec["tab_5_1_policy"]["sd_bound_uniform_thinning"] = r(
    pol["period1_mandatory"]["g_std"]
    * np.sqrt(pol["period1_mandatory"]["coverage_mean"] / pol["period2_voluntary"]["coverage_mean"]), 3)
rec["tab_5_1_policy"]["flu_season_only"] = pol["flu_season_only"]
rec["tab_5_1_policy"]["period1_subsegments"] = ST["period1_subsegments"]

# ---------- 表 5-2 流行初期分箱 ----------
var = {v["bin"]: v for v in ST["early"]["var_structure"]}
rec["tab_5_2_early_bins"] = [
    {"bin": t["bin"], "N": t["N"], "n_states": t["n_states"], "mean": r(t["mean"], 3),
     "median": r(t["median"], 3), "ci": [r(t["ci_lo"], 3), r(t["ci_hi"], 3)],
     "var_over_mean2": r(var[t["bin"]]["var_over_mean2"], 2)}
    for t in ST["early"]["table"]
]

# ---------- 表 5-3 仿射模型的估计与推断口径 ----------
e = ST["early"]
br = e["bootstrap_robustness"]
rec["tab_5_3_affine"] = {
    "main": {k: (r(v) if not isinstance(v, list) else [r(x) for x in v]) for k, v in e["affine"].items()},
    "trim1pct": {k: (r(v) if not isinstance(v, list) else [r(x) for x in v])
                 for k, v in e["affine_trim1pct"].items()},
    "decile": {"a": r(e["decile"]["a"]), "b": r(e["decile"]["b"]), "m_x": r(e["decile"]["m_x"], 2)},
    "ols_b": r(ST["stage_scale_audit"]["ols_sep"]["b_early"]),
    "endogenous_reestimation_b_ci": [r(x) for x in br["endogenous_reestimation"]["b_ci"]],
    "week_clustered_b_ci": [r(x) for x in br["week_clustered"]["b_ci"]],
    "week_clustered_a_ci": [r(x) for x in br["week_clustered"]["a_ci"]],
    "error_budget": {k: r(v) for k, v in e["error_budget"].items()},
    "realized_large_scale": ST["realized_large_scale"],
}

# ---------- 表 5-4 滞后权重:实证、delta 法预测与模拟 ----------
c10 = {x["id"]: x for x in json.loads((fs.CHECKS / "c10_random_denominator.json").read_text())["records"]}
lag = ST["lag_weights_sensitivity"]
rows = []
for key, cid, sw2, lagmean in [("original", "original", 0.495, 1.45), ("single_1w", "single", 1.0, 1.0),
                               ("equal_3w", "equal", 0.333, 2.0)]:
    L = lag[key]
    rows.append({"spec": key, "weights": [r(w, 3) for w in L["weights"]], "sum_w2": sw2,
                 "mean_lag_weeks": lagmean, "N": L["N"], "R_bar": r(L["R_bar"]),
                 "a": r(L["a"]), "a_ci": [r(x) for x in L["a_ci"]],
                 "b": r(L["b"]), "b_ci": [r(x) for x in L["b_ci"]],
                 "m_x": r(L["m_x"], 1), "m_x_ci": [r(x, 1) for x in L["m_x_ci"]],
                 "b_ratio_to_main": r(L["b"] / lag["original"]["b"], 2),
                 "delta_pred_b": c10[f"10.3.{cid}"]["expected"].split("(")[0],
                 "sim_b": c10[f"10.3.{cid}"]["observed"].split("(")[0],
                 "sim_a": c10[f"10.4.{cid}"]["observed"].split("(")[0]})
rec["tab_5_4_lag_weights"] = rows
rec["tab_5_4_lag_weights_scenario"] = {"R_bar": 1.67, "v_R": 0.06, "k": 0.35, "rho": 0.021, "A": 1.8409,
                                       "b_no_denominator_noise": c10["10.2"]["expected"],
                                       "b_over_a_sim": c10["10.9"]["observed"],
                                       "A_over_vR": c10["10.9"]["expected"],
                                       "overdispersed_phi_1_96": c10["10.7"]["observed"]}

# ---------- 表 5-5 达峰期分箱 ----------
pk = {p["bin"]: p for p in BINS["peak_bins"]}
evp = {x["bin"]: x for x in ST["early_vs_peak"]}
rec["tab_5_5_peak_bins"] = [
    {"bin": t["bin"], "N": t["N"], "mean": r(t["mean"], 3), "bias": r(pk[t["bin"]]["bias"], 3),
     "within": r(pk[t["bin"]]["within"], 3), "bias_share_pct": r(100 * pk[t["bin"]]["bias_share"], 1),
     "early_mean": r(evp[t["bin"]]["early"], 3), "ratio_to_early": r(evp[t["bin"]]["ratio"], 2)}
    for t in ST["peak"]["table_stationary"]
]
rec["tab_5_5_peak_summary"] = {
    "N": ST["peak"]["N"], "R_bar": r(ST["peak"]["R_bar"]), "sd": r(ST["peak"]["sd"]),
    "bias_term": r(ST["peak"]["bias_term"]), "bias_share": r(ST["peak"]["bias_share"]),
    "affine_cond": {k: (r(v) if not isinstance(v, list) else [r(x) for x in v])
                    for k, v in ST["peak"]["affine_cond"].items()},
    "error_budget_cond": {k: r(v) for k, v in ST["peak"]["error_budget_cond"].items()},
    "stage_scale_audit": ST["stage_scale_audit"],
}

# ---------- 第六章:工具变量、事前基准、时变基准、外部数据 ----------
iv = ST["seasonal_subsample_iv"]
rec["tab_6_1_iv"] = {
    s: {k: (r(v) if not isinstance(v, list) else [r(x) for x in v]) for k, v in iv[s].items()}
    for s in ["2022-23", "2023-24", "2024-25", "pooled_within_phase", "pooled_subsample_mean"]
}
ro = ST["rolling_origin"]
rec["tab_6_2_rolling_origin"] = {
    s: {"N": ro[s]["N"], "a": r(ro[s]["a"]), "b": r(ro[s]["b"]), "b_ci": [r(x) for x in ro[s]["b_ci"]],
        "m_x": r(ro[s]["b"] / ro[s]["a"], 1)}
    for s in ro
}
cb = ST["competing_baselines"]
rec["tab_6_3_baselines"] = {
    "overall": cb["overall"], "bins": cb["bins"], "common_scale": cb["common_scale"],
    "affine_cori_2w": cb["affine_cori_2w"], "affine_cori_3w": cb["affine_cori_3w"],
}
rec["national"] = ST["national"]
fl = ST["extended_validation_flusight"]
rec["tab_6_4_external"] = {
    "flusight_primary": fl["primary_states_exante"], "flusight_sensitivity": fl["sensitivity_table"],
    "flusight_phase": fl["phase_decomposition"],
    "covid19": ST["extended_validation_covid19"]["sensitivity_table"],
}

# ---------- 图 6-2 各基准在规模分箱上的损失 ----------
names = [("phase_mean", "阶段均值基准", fs.THEORY, "o"), ("cori_2w", "Cori 滑动窗（2 周）", fs.EMPIRIC, "s"),
         ("cori_3w", "Cori 滑动窗（3 周）", fs.ACCENT, "^"), ("naive", "朴素预测（下周＝本周）", fs.FLOOR, "D")]
fig, axes = plt.subplots(1, 2, figsize=fs.WIDE, constrained_layout=True, sharey=True)
x = np.arange(len(BIN_SHORT))
for ax, src, letter, title in [(axes[0], cb["bins"], "a", "按各自预测值归一化"),
                               (axes[1], cb["common_scale"]["bins"], "b", "统一按初期均值归一化")]:
    for key, lab, col, mk in names:
        ax.plot(x, [b[key] for b in src], marker=mk, color=col, label=lab, ms=4)
    ax.set_yscale("log")
    ax.set_xticks(x, BIN_SHORT, fontsize=7)
    fs.panel_xlabel(ax, letter, f"$D_t$ 分箱（例/周），{title}")
axes[0].set_ylabel("相对均方误差（对数刻度）")
axes[0].set_ylim(0.05, 2.0)
axes[1].legend(loc="upper right", fontsize=7)
fs.save(fig, "fig_6_2_baselines", log)
log("fig_6_2: phase_mean vs cori_2w vs naive by bin written")

(OUT / "thesis_tables.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1))
log(f"wrote {OUT / 'thesis_tables.json'}")
