"""学位论文表 5-5（达峰期分箱误差分解）的 LaTeX 源与 tables/manifest.json。

数字只取自 nhsn_bins.json 的 peak_bins 与 early_bins(由 prep_nhsn.py 生成),
不手工转录。输出 thesis/tables/tab_peak_bins.tex,并记录 SHA-256。
"""
from __future__ import annotations

import hashlib
import json

import figstyle as fs

THESIS = fs.WORK / "thesis"
TABLES = THESIS / "tables"
TABLES.mkdir(parents=True, exist_ok=True)
BINS_PATH = fs.DERIVED / "nhsn_bins.json"
BINS = json.loads(BINS_PATH.read_text())

LABELS = ["$[5,20)$", "$[20,50)$", "$[50,100)$", "$[100,250)$", "$[250,600)$", "$[600,5000)$"]


def f3(x):
    return f"{x:.3f}"


peak = BINS["peak_bins"]
early = BINS["early_bins"]
assert len(peak) == len(early) == len(LABELS)
rows = []
for lab, p, e in zip(LABELS, peak, early):
    assert p["bin"] == e["bin"]
    share = 100 * p["bias_share"]
    rows.append(
        f"    {lab} & {p['N']} & {f3(p['total'])} & {f3(p['bias'])} & {f3(p['within'])}"
        f" & {share:.1f} & {f3(e['mean_loss'])} & {p['total'] / e['mean_loss']:.2f} \\\\"
    )
n_total = sum(p["N"] for p in peak)

tex = "\n".join([
    r"\begin{table}[!tbp]",
    r"  \centering",
    r"  \caption{达峰期以初期均值为基准时的分箱误差分解}",
    r"  \label{tab:peak-bins}",
    r"  \small",
    r"  \begin{tabular}{@{}lccccccc@{}}",
    r"    \toprule",
    r"    $D_t$ 分箱 & 州周数 & 总损失 & 偏差项 & 箱内波动 & 偏差占比（\%） & 初期损失 & 峰期/初期 \\",
    r"    \midrule",
    *rows,
    r"    \bottomrule",
    r"  \end{tabular}",
    "",
    r"  \vspace{4pt}",
    "  {\\small 注：峰期为各季全国峰值周及其后 7 周，共 "
    + f"{n_total:,}" + " 个州周；基准为初期均值 1.6706。}",
    r"\end{table}",
    "",
])
out = TABLES / "tab_peak_bins.tex"
out.write_text(tex, encoding="utf-8")

manifest = {
    "schema_version": 1,
    "tables": [{
        "id": "tab:peak-bins",
        "path": "tab_peak_bins.tex",
        "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
        "generator": "paper/code/thesis_tables_tex.py",
        "data_sources": ["paper/code/derived/nhsn_bins.json"],
        "display": "raw",
        "n_seeds": 1,
    }],
}
(TABLES / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
print(out, n_total)
