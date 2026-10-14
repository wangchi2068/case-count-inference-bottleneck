"""从 NHSN 原始 CSV(24 MB,分块流式读取)重建图 5–7 所需的派生数据。

口径照抄旧分析脚本 run_empirical_flu_analysis.py 的 load_data/build_panel/tag_phase/tag_peak_decay
(只读不运行):51 个辖区、缺失住院数按 0、D_t = 0.65C_t + 0.25C_{t-1} + 0.10C_{t-2}、D_t >= 5 入样。
重建后先与 empirical_stats.json 逐项对账;对不上的以 JSON 为准并写入日志。
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from figstyle import DATA, DERIVED, load_stats, logger

CSV = DATA / "raw" / "Weekly_Hospital_Respiratory_Data_Metrics_by_Jurisdiction.csv"
COLS = ["Week Ending Date", "Geographic aggregation", "Total Influenza Admissions",
        "Percent Hospitals Reporting Influenza Admissions"]
W = np.array([0.65, 0.25, 0.10])
BINS = [5, 20, 50, 100, 250, 600, 5000]
LABELS = ["[5, 20)", "[20, 50)", "[50, 100)", "[100, 250)", "[250, 600)", "[600, 5000)"]
EARLY = [("2022-10-08", "2022-11-26"), ("2023-10-14", "2023-12-16"), ("2024-11-09", "2025-01-18")]
EXCLUDE = {"PR", "VI", "GU", "MP", "AS", "US"}

log = logger("prep_nhsn")


def read_stream() -> pd.DataFrame:
    parts = []
    for i, chunk in enumerate(pd.read_csv(CSV, usecols=COLS, chunksize=4000)):
        g = chunk["Geographic aggregation"].astype(str)
        parts.append(chunk[(g.str.len() == 2) & ~g.isin(EXCLUDE)])
        log(f"chunk {i}: rows={len(chunk)} kept={len(parts[-1])}")
    df = pd.concat(parts, ignore_index=True)
    df["week_end"] = pd.to_datetime(df["Week Ending Date"])
    return df.sort_values(["Geographic aggregation", "week_end"]).reset_index(drop=True)


def build_panel(df: pd.DataFrame, w=W) -> pd.DataFrame:
    rows = []
    for state, sub in df.groupby("Geographic aggregation", sort=True):
        c = sub["Total Influenza Admissions"].fillna(0).to_numpy()
        d = sub["week_end"].to_numpy()
        if len(c) < 10:
            continue
        for t in range(2, len(c) - 1):
            dt = w[0] * c[t] + w[1] * c[t - 1] + w[2] * c[t - 2]
            if dt >= 5:
                rows.append((state, pd.Timestamp(d[t]), dt, c[t + 1]))
    p = pd.DataFrame(rows, columns=["state", "week_end", "D_t", "C_next"])
    p["g"] = p["C_next"] / p["D_t"]
    return p


def main() -> None:
    st = load_stats()
    df = read_stream()
    n_sw = len(df)
    n_missing = int(df["Total Influenza Admissions"].isna().sum())
    log(f"state-weeks={n_sw} (JSON {st['n_state_weeks']}), missing admissions={n_missing}, "
        f"jurisdictions={df['Geographic aggregation'].nunique()}")

    # 全国周序列:51 个辖区直接加总(旧图 4(a) 只加总了 D_t>=5 的行,这里改为全量)
    nat = df.assign(adm=df["Total Influenza Admissions"].fillna(0)).groupby("week_end").agg(
        admissions=("adm", "sum"),
        coverage=("Percent Hospitals Reporting Influenza Admissions", "mean"),
        n_juris=("adm", "size"),
    ).reset_index()
    nat.to_csv(DERIVED / "national_weekly.csv", index=False)
    log(f"national weekly rows={len(nat)}, range {nat.week_end.min().date()}–{nat.week_end.max().date()}")

    panel = build_panel(df)
    log(f"valid panel rows={len(panel)} (JSON n_valid {st['n_valid']})")

    early_mask = np.zeros(len(panel), bool)
    for a, b in EARLY:
        early_mask |= (panel.week_end >= a) & (panel.week_end <= b)
    early = panel[early_mask].copy()
    r_early = early.g.mean()
    log(f"early N={len(early)} (JSON {st['early']['N']}), R_bar={r_early:.6f} (JSON {st['early']['R_bar']:.6f})")

    peaks = [pd.Timestamp(v) for v in st["peaks"].values()]
    pk_mask = np.zeros(len(panel), bool)
    for pk in peaks:
        pk_mask |= (panel.week_end >= pk) & (panel.week_end <= pk + pd.Timedelta(weeks=7))
    peak = panel[pk_mask].copy()
    log(f"peak N={len(peak)} (JSON {st['peak']['N']}), R_bar={peak.g.mean():.6f} (JSON {st['peak']['R_bar']:.6f})")

    out = {"early_bins": [], "peak_bins": [], "check": {}}
    early["bin"] = pd.cut(early.D_t, BINS, labels=LABELS, right=False)
    early["loss"] = ((early.g - st["early"]["R_bar"]) / st["early"]["R_bar"]) ** 2
    for lab, ref in zip(LABELS, st["early"]["table"]):
        x = early[early.bin == lab]
        rec = {"bin": lab, "N": int(len(x)), "mean_loss": float(x.loss.mean()),
               "mean_D": float(x.D_t.mean()), "median_D": float(x.D_t.median()),
               "json_N": ref["N"], "json_mean": ref["mean"]}
        out["early_bins"].append(rec)
        log(f"early {lab}: N={rec['N']} vs {ref['N']}, loss={rec['mean_loss']:.4f} vs {ref['mean']:.4f}, "
            f"meanD={rec['mean_D']:.1f}")

    rE = st["early"]["R_bar"]
    peak["bin"] = pd.cut(peak.D_t, BINS, labels=LABELS, right=False)
    for lab, ref in zip(LABELS, st["peak"]["table_stationary"]):
        x = peak[peak.bin == lab]
        total = float((((x.g - rE) / rE) ** 2).mean())
        bias = float(((x.g.mean() - rE) / rE) ** 2)
        rec = {"bin": lab, "N": int(len(x)), "total": total, "bias": bias,
               "within": total - bias, "bias_share": bias / total,
               "mean_D": float(x.D_t.mean()), "json_N": ref["N"], "json_total": ref["mean"]}
        out["peak_bins"].append(rec)
        log(f"peak {lab}: N={rec['N']} vs {ref['N']}, total={total:.4f} vs {ref['mean']:.4f}, "
            f"bias share={rec['bias_share']:.3f}")
    tot_all = float((((peak.g - rE) / rE) ** 2).mean())
    bias_all = float(((peak.g.mean() - rE) / rE) ** 2)
    log(f"peak overall bias={bias_all:.4f} (JSON {st['peak']['bias_term']:.4f}), "
        f"share={bias_all / tot_all:.4f} (JSON {st['peak']['bias_share']:.4f})")

    out["check"] = {
        "n_state_weeks": [n_sw, st["n_state_weeks"]],
        "n_missing": n_missing,
        "n_valid": [len(panel), st["n_valid"]],
        "early_N": [len(early), st["early"]["N"]],
        "peak_N": [len(peak), st["peak"]["N"]],
        "peak_bias": [bias_all, st["peak"]["bias_term"]],
        "peak_bias_share": [bias_all / tot_all, st["peak"]["bias_share"]],
    }
    (DERIVED / "nhsn_bins.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    log("done")


if __name__ == "__main__":
    main()
