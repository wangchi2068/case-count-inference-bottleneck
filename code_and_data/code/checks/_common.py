"""核验脚本公用工具:日志同时写屏幕和 logs/checks/<name>.log,结论写 results/checks/<name>.json。
每条结论记一行 record(id, 对象, 期望, 实测, 判定, 备注),summary.md 由 build_summary.py 汇总。"""
import json, sys, time
from pathlib import Path

PKG = Path(__file__).resolve().parents[2]           # 本包根目录
LOGS = PKG / "logs" / "checks"
RESULTS = PKG / "results" / "checks"
LOGS.mkdir(parents=True, exist_ok=True)
RESULTS.mkdir(parents=True, exist_ok=True)


class Checker:
    def __init__(self, name, title):
        self.name, self.title = name, title
        self.log_f = open(LOGS / f"{name}.log", "w", encoding="utf-8")
        self.records = []
        self.t0 = time.time()
        self.log(f"# {name}: {title}")

    def log(self, *a):
        s = " ".join(str(x) for x in a)
        print(s)
        self.log_f.write(s + "\n")
        self.log_f.flush()

    def record(self, cid, target, expected, observed, verdict, note=""):
        """verdict: 通过 / 不通过 / 偏差(结论成立但数值或条件与论文表述有出入)"""
        r = dict(id=cid, target=target, expected=str(expected), observed=str(observed),
                 verdict=verdict, note=note)
        self.records.append(r)
        self.log(f"[{verdict}] {cid} {target} | 期望 {expected} | 实测 {observed} {('| ' + note) if note else ''}")
        # 增量落盘,脚本中途被杀也保留已得结论
        json.dump(dict(name=self.name, title=self.title, records=self.records),
                  open(RESULTS / f"{self.name}.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)

    def close(self):
        self.log(f"耗时 {time.time() - self.t0:.1f} s")
        self.log_f.close()


def rel(a, b):
    return abs(a - b) / abs(b)


def fgls_affine(L, D):
    """论文第 512 行的一步 FGLS:先 OLS 拟合 L = a + b/D,再以 1/μ̂² 加权重拟合。返回 (a, b)。"""
    import numpy as np
    X = np.column_stack([np.ones_like(D, dtype=float), 1.0 / D])
    beta = np.linalg.lstsq(X, L, rcond=None)[0]
    mu = np.clip(X @ beta, 1e-6, None)
    wt = 1.0 / mu
    beta = np.linalg.lstsq(X * wt[:, None], L * wt, rcond=None)[0]
    return float(beta[0]), float(beta[1])
