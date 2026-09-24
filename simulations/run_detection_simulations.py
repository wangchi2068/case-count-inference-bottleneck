# -*- coding: utf-8 -*-
"""
Simulation Suite 2: Growth Detection Power and Finite-Sample Properties
1. Evaluates Exact Discrete Negative Binomial Power vs. Asymptotic Normal (Wald) Test.
2. Compares empirical Type I error rate under H0: R_t = 1.0.
3. Evaluates statistical power pi(n, delta) across effect size delta and overdispersion k.
4. Generates publication-quality Figure 2 with exact parameter annotations.
"""

import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

# Styling
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_FIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'figures')
os.makedirs(OUTPUT_FIG_DIR, exist_ok=True)

def nb_sf(y, r, p):
    if y <= 0:
        return 1.0
    return stats.nbinom.sf(y - 1, r, p)

def compute_exact_critical_value(n, k, rho, alpha=0.05):
    """
    Smallest integer c_alpha such that P_{R_t=1}(C_t >= c_alpha) <= alpha.
    Under R_t = 1: C_t ~ NB(r = n*k, p = k / (k + rho))
    """
    r = n * k
    p0 = k / (k + rho)
    c_cand = int(stats.nbinom.ppf(1 - alpha, r, p0))
    while nb_sf(c_cand, r, p0) > alpha:
        c_cand += 1
    while c_cand > 0 and nb_sf(c_cand - 1, r, p0) <= alpha:
        c_cand -= 1
    return c_cand

def compute_exact_power(c_alpha, n, k, rho, delta):
    """
    pi(n, delta) = P_{R_t = 1 + delta}(C_t >= c_alpha)
    Under R_t = 1 + delta: C_t ~ NB(r = n*k, p_alt = k / (k + rho * (1 + delta)))
    """
    r = n * k
    p_alt = k / (k + rho * (1.0 + delta))
    return nb_sf(c_alpha, r, p_alt)

def compute_normal_approx_power(n, k, rho, delta, alpha=0.05):
    """
    Wald test under H0: R_t = 1 with V0 = 1/(rho*n) + 1/(k*n).
    Critical value R_crit = 1 + z_{1-alpha} * sqrt(V0).
    Power = 1 - Phi( (R_crit - (1 + delta)) / sqrt(V_alt) ),
    where V_alt = (1 + delta)/(rho*n) + (1 + delta)^2 / (k*n).
    """
    z_alpha = stats.norm.ppf(1 - alpha)
    V0 = 1.0 / (rho * n) + 1.0 / (k * n)
    R_crit = 1.0 + z_alpha * np.sqrt(V0)
    
    R_alt = 1.0 + delta
    V_alt = R_alt / (rho * n) + (R_alt**2) / (k * n)
    z_alt = (R_crit - R_alt) / np.sqrt(V_alt)
    return 1.0 - stats.norm.cdf(z_alt)

def run_detection_experiments():
    rho = 0.25
    alpha = 0.05
    reps = 30000
    rng = np.random.default_rng(20260924)
    
    m_grid = np.array([5, 10, 20, 40, 80, 150, 300, 600])
    n_grid = (m_grid / rho).astype(int)
    
    k_list = [0.1, 0.35, 1.0]
    size_results = {k: {"m": m_grid, "exact_nominal": [], "empirical_exact": [], "empirical_wald": []} for k in k_list}
    
    for k in k_list:
        p0 = k / (k + rho)
        for i, n in enumerate(n_grid):
            c_alpha = compute_exact_critical_value(n, k, rho, alpha)
            exact_nom = nb_sf(c_alpha, n * k, p0)
            
            sub_rng = rng.spawn(1)[0]
            C_samples = sub_rng.negative_binomial(n * k, p0, size=reps)
            emp_exact = np.mean(C_samples >= c_alpha)
            
            # Wald test under H0: Z = (R_hat - 1) / sqrt(V0)
            R_hat = C_samples / (rho * n)
            V0 = 1.0 / (rho * n) + 1.0 / (k * n)
            wald_stat = (R_hat - 1.0) / np.sqrt(V0)
            emp_wald = np.mean(wald_stat >= stats.norm.ppf(1 - alpha))
            
            size_results[k]["exact_nominal"].append(exact_nom)
            size_results[k]["empirical_exact"].append(emp_exact)
            size_results[k]["empirical_wald"].append(emp_wald)
            
    m_dense = np.logspace(np.log10(5), np.log10(800), 120)
    n_dense = m_dense / rho
    
    return size_results, m_dense, n_dense


def enumerate_m80(n_max, k, rho, delta, alpha=0.05, target=0.80):
    """自 n=1 起以步长 1 枚举，取首次满足功效 >= target 的最小整数 n（处理 c_alpha 非单调）。"""
    for n in range(1, n_max + 1):
        c = compute_exact_critical_value(n, k, rho, alpha)
        if compute_exact_power(c, n, k, rho, delta) >= target:
            return n
    return None

def plot_fig2_detection(size_results, m_dense, n_dense):
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.6), dpi=300)
    rho = 0.25
    alpha = 0.05
    
    # Panel 1: Type I error (Size)
    ax = axes[0]
    ax.axhline(0.05, color='black', linestyle='--', lw=1.2, label=r"Nominal Level $\alpha = 0.05$")
    colors = {0.1: 'crimson', 0.35: 'navy', 1.0: 'teal'}
    
    for k in [0.1, 0.35, 1.0]:
        m = size_results[k]["m"]
        ax.plot(m, size_results[k]["empirical_exact"], marker='o', color=colors[k], lw=1.8,
                label=rf"Exact NB Test ($k={k}$)")
        ax.plot(m, size_results[k]["empirical_wald"], marker='^', linestyle=':', color=colors[k], lw=1.5, alpha=0.75,
                label=rf"Asymptotic Wald ($k={k}$)")
        
    ax.set_xscale('log')
    ax.set_ylim(0.00, 0.125)
    ax.set_xlabel(r"Expected Reported Cases $m = \rho n$ (Log Scale)", fontsize=11)
    ax.set_ylabel(r"Empirical Type I Error Rate $\widehat{\alpha}$", fontsize=11)
    ax.set_title(r"(a) Type I Error Control: Exact vs Asymptotic", fontsize=12, fontweight='bold')
    ax.grid(True, ls=":", alpha=0.5)
    ax.legend(fontsize=7.5, loc='upper right', ncol=2)
    
    # Panel 2: Power curves across delta (at fixed k = 0.35)
    ax = axes[1]
    k_fixed = 0.35
    delta_styles = {}
    for delta, (col, ls) in zip([0.15, 0.30, 0.50], [('darkorange','solid'),('purple','solid'),('forestgreen','solid')]):
        n80 = enumerate_m80(20000, k_fixed, rho, delta)
        m80 = round(n80 * rho, 1)
        delta_styles[delta] = (col, ls, rf"$\delta={delta}$ ($m_{{80\%}}={m80:.0f}$, first-crossing $n={n80}$)")
    
    for delta, (col, ls, lbl) in delta_styles.items():
        p_ex = [compute_exact_power(compute_exact_critical_value(n, k_fixed, rho, alpha), n, k_fixed, rho, delta) for n in n_dense]
        p_nm = [compute_normal_approx_power(n, k_fixed, rho, delta, alpha) for n in n_dense]
        ax.plot(m_dense, p_ex, color=col, linestyle=ls, lw=2.2, label=rf"Exact: {lbl}")
        ax.plot(m_dense, p_nm, color=col, linestyle='--', lw=1.3, alpha=0.7, label=rf"Wald Approx ($\delta={delta}$)")
        
    ax.axhline(0.80, color='gray', linestyle=':', lw=1.2, label=r"80% Power Benchmark")
    ax.set_xscale('log')
    ax.set_ylim(0.0, 1.02)
    ax.set_xlabel(r"Expected Reported Cases $m = \rho n$ (Log Scale)", fontsize=11)
    ax.set_ylabel(r"Statistical Power $\pi(n, \delta)$", fontsize=11)
    ax.set_title(r"(b) Detection Power vs Case Scale ($k=0.35, \rho=0.25$)", fontsize=12, fontweight='bold')
    ax.grid(True, ls=":", alpha=0.5)
    ax.legend(fontsize=7.5, loc='lower right', ncol=2)
    
    # Panel 3: Power curves across k (at fixed delta = 0.25)
    ax = axes[2]
    delta_fixed = 0.25
    k_styles = {}
    for k_val, col in zip([0.1, 0.35, 1.0], ['crimson', 'navy', 'teal']):
        n80 = enumerate_m80(20000, k_val, rho, delta_fixed)
        m80 = round(n80 * rho, 1)
        k_styles[k_val] = (col, rf"$k={k_val:.2f}$ ($m_{{80\%}}={m80:.0f}$, first-crossing $n={n80}$)")
    
    for k_val, (col, lbl) in k_styles.items():
        p_ex = [compute_exact_power(compute_exact_critical_value(n, k_val, rho, alpha), n, k_val, rho, delta_fixed) for n in n_dense]
        ax.plot(m_dense, p_ex, color=col, lw=2.2, label=lbl)
        
    ax.axhline(0.80, color='gray', linestyle=':', lw=1.2, label=r"80% Power Benchmark")
    ax.set_xscale('log')
    ax.set_ylim(0.0, 1.02)
    ax.set_xlabel(r"Expected Reported Cases $m = \rho n$ (Log Scale)", fontsize=11)
    ax.set_ylabel(r"Statistical Power $\pi(n, \delta = 0.25)$", fontsize=11)
    ax.set_title(r"(c) Impact of Overdispersion $k$ ($\delta=0.25, \rho=0.25$)", fontsize=12, fontweight='bold')
    ax.grid(True, ls=":", alpha=0.5)
    ax.legend(fontsize=8, loc='lower right')
    
    plt.tight_layout()
    pdf_path = os.path.join(OUTPUT_FIG_DIR, "fig2_growth_detection_power.pdf")
    png_path = os.path.join(OUTPUT_FIG_DIR, "fig2_growth_detection_power.png")
    plt.savefig(pdf_path, bbox_inches='tight')
    plt.savefig(png_path, bbox_inches='tight')
    plt.close()
    print(f"Generated Figure 2 at {pdf_path}")

if __name__ == "__main__":
    size_res, m_dense, n_dense = run_detection_experiments()
    plot_fig2_detection(size_res, m_dense, n_dense)
