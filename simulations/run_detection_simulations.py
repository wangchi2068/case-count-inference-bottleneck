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
    # Publication-grade canvas
    fig, axes = plt.subplots(1, 3, figsize=(16.5, 5.0), dpi=300)
    rho = 0.25
    alpha = 0.05
    
    # Low-saturation, high-contrast academic palette
    col_k01 = '#D73027'   # Crimson for high superspreading
    col_k035 = '#1F78B4'  # Navy for typical respiratory
    col_k10 = '#2CA25F'   # Emerald for geometric/weak
    colors_k = {0.1: col_k01, 0.35: col_k035, 1.0: col_k10}

    # ==========================================
    # Panel (a): Type I Error Control
    # ==========================================
    ax = axes[0]
    # Subtle shaded background zones for intuitive reading
    ax.fill_between([3.5, 900], 0.05, 0.125, color='#FEE0D2', alpha=0.45, zorder=0)
    ax.fill_between([3.5, 900], 0.00, 0.05, color='#E5F5E0', alpha=0.45, zorder=0)
    
    # Reference nominal level line
    ax.axhline(0.05, color='#333333', linestyle='--', lw=1.5, zorder=2, label=r"Nominal Size $\alpha = 0.05$")
    ax.text(0.035, 0.88, "Over-rejection Zone\n(Wald Test Invalid)", transform=ax.transAxes,
            color='#A50F15', fontsize=8.5, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.9), zorder=3)
    ax.text(0.035, 0.10, r"Strictly Controlled Zone ($\alpha \leq 0.05$)", transform=ax.transAxes,
            color='#006D2C', fontsize=8.5, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.9), zorder=3)
    
    for k in [0.1, 0.35, 1.0]:
        m = size_results[k]["m"]
        # Exact NB Test (Solid line + circle)
        ax.plot(m, size_results[k]["empirical_exact"], marker='o', color=colors_k[k], lw=2.0, ms=5.5,
                mec='white', mew=0.8, zorder=4, label=rf"Exact NB ($k={k}$)")
        # Asymptotic Wald (Dotted line + triangle)
        ax.plot(m, size_results[k]["empirical_wald"], marker='^', linestyle=':', color=colors_k[k], lw=1.6, ms=5.5,
                mec='white', mew=0.8, alpha=0.85, zorder=4, label=rf"Wald Approx ($k={k}$)")
        
    ax.set_xscale('log')
    ax.set_xlim(4.0, 800)
    ax.set_ylim(0.00, 0.115)
    ax.set_xlabel(r"Expected Reported Cases $m = \rho n$ (Log Scale)", fontsize=11, fontweight='bold')
    ax.set_ylabel(r"Empirical Type I Error Rate $\widehat{\alpha}$", fontsize=11, fontweight='bold')
    ax.set_title(r"(a) Type I Error Control: Exact vs. Wald", fontsize=12, fontweight='bold', pad=10)
    ax.grid(True, ls=":", color='gray', alpha=0.35)
    ax.tick_params(direction='out', length=4, width=0.8, labelsize=9.5)
    ax.legend(fontsize=7.5, loc='center right', framealpha=0.92, edgecolor='#CCCCCC', ncol=1)

    # ==========================================
    # Panel (b): Power Curves across Effect Size delta
    # ==========================================
    ax = axes[1]
    k_fixed = 0.35
    delta_palette = {
        0.50: ('#2CA25F', 'Strong Outbreak'),
        0.30: ('#756BB1', 'Moderate Outbreak'),
        0.15: ('#E6550D', 'Mild Resurgence')
    }
    
    ax.axhline(0.80, color='#666666', linestyle='--', lw=1.3, zorder=2)
    ax.text(5.5, 0.815, r"80% Power Threshold", color='#444444', fontsize=9, fontweight='bold')
    
    for delta, (col, d_name) in delta_palette.items():
        n80 = enumerate_m80(20000, k_fixed, rho, delta)
        m80 = round(n80 * rho, 1)
        
        p_ex = [compute_exact_power(compute_exact_critical_value(n, k_fixed, rho, alpha), n, k_fixed, rho, delta) for n in n_dense]
        p_nm = [compute_normal_approx_power(n, k_fixed, rho, delta, alpha) for n in n_dense]
        
        # Plot curves
        ax.plot(m_dense, p_ex, color=col, lw=2.2, zorder=3, label=rf"Exact: $\delta={delta}$ ({d_name})")
        ax.plot(m_dense, p_nm, color=col, linestyle=':', lw=1.4, alpha=0.7, zorder=3, label=rf"Wald: $\delta={delta}$")
        
        # Mark 80% threshold crossing with drop lines
        if m80:
            ax.plot(m80, 0.80, marker='o', ms=6.5, color=col, mec='white', mew=1.2, zorder=5)
            ax.vlines(m80, 0, 0.80, color=col, linestyle=':', lw=1.2, alpha=0.75, zorder=2)
            y_offset = -0.09 if delta != 0.30 else 0.05
            ax.annotate(rf"$m_{{80\%}} \approx {m80:.0f}$" + f"\n($n={n80}$)",
                        xy=(m80, 0.80), xytext=(m80 * 0.85, 0.80 + y_offset),
                        fontsize=7.8, fontweight='bold', color=col,
                        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=col, lw=0.6, alpha=0.9),
                        arrowprops=dict(arrowstyle="->", color=col, lw=0.9, shrinkB=4))
        
    ax.set_xscale('log')
    ax.set_xlim(4.0, 800)
    ax.set_ylim(0.0, 1.03)
    ax.set_xlabel(r"Expected Reported Cases $m = \rho n$ (Log Scale)", fontsize=11, fontweight='bold')
    ax.set_ylabel(r"Statistical Power $\pi(n, \delta)$", fontsize=11, fontweight='bold')
    ax.set_title(r"(b) Detection Power vs. Scale ($k=0.35, \rho=0.25$)", fontsize=12, fontweight='bold', pad=10)
    ax.grid(True, ls=":", color='gray', alpha=0.35)
    ax.tick_params(direction='out', length=4, width=0.8, labelsize=9.5)
    ax.legend(fontsize=7.2, loc='lower right', framealpha=0.92, edgecolor='#CCCCCC', ncol=1)

    # ==========================================
    # Panel (c): Impact of Overdispersion k
    # ==========================================
    ax = axes[2]
    delta_fixed = 0.25
    k_palette = {
        0.10: (col_k01, 'High Superspreading'),
        0.35: (col_k035, 'Typical Respiratory'),
        1.00: (col_k10, 'Weak/Geometric')
    }
    
    ax.axhline(0.80, color='#666666', linestyle='--', lw=1.3, zorder=2)
    ax.text(5.5, 0.815, r"80% Power Threshold", color='#444444', fontsize=9, fontweight='bold')
    
    m80_dict = {}
    for k_val, (col, k_name) in k_palette.items():
        n80 = enumerate_m80(20000, k_val, rho, delta_fixed)
        m80 = round(n80 * rho, 1)
        m80_dict[k_val] = (m80, n80)
        
        p_ex = [compute_exact_power(compute_exact_critical_value(n, k_val, rho, alpha), n, k_val, rho, delta_fixed) for n in n_dense]
        ax.plot(m_dense, p_ex, color=col, lw=2.2, zorder=3, label=rf"$k={k_val:.2f}$ ({k_name})")
        
        # Mark 80% threshold crossing with drop lines
        if m80:
            ax.plot(m80, 0.80, marker='o', ms=6.5, color=col, mec='white', mew=1.2, zorder=5)
            ax.vlines(m80, 0, 0.80, color=col, linestyle=':', lw=1.2, alpha=0.75, zorder=2)
            y_offset = -0.10 if k_val == 0.35 else (0.05 if k_val == 1.0 else -0.11)
            ax.annotate(rf"$m_{{80\%}}={m80:.0f}$" + f"\n($n={n80}$)",
                        xy=(m80, 0.80), xytext=(m80 * 0.82, 0.80 + y_offset),
                        fontsize=8.0, fontweight='bold', color=col,
                        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=col, lw=0.6, alpha=0.9),
                        arrowprops=dict(arrowstyle="->", color=col, lw=0.9, shrinkB=4))

    # Add ~2.9x expansion annotation bracket between k=1.0 and k=0.1
    m80_k10 = m80_dict[1.00][0]
    m80_k01 = m80_dict[0.10][0]
    # Move to y=0.22 to completely avoid curves
    ax.annotate("", xy=(m80_k01, 0.22), xytext=(m80_k10, 0.22),
                arrowprops=dict(arrowstyle="<->", color='#800026', lw=1.5))
    ax.text(np.sqrt(m80_k10 * m80_k01), 0.245, r"$\approx 2.9\times$ Scale Penalty",
            horizontalalignment='center', color='#800026', fontsize=8.8, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.25", fc='white', ec='#800026', lw=0.8, alpha=0.95))

    ax.set_xscale('log')
    ax.set_xlim(4.0, 800)
    ax.set_ylim(0.0, 1.03)
    ax.set_xlabel(r"Expected Reported Cases $m = \rho n$ (Log Scale)", fontsize=11, fontweight='bold')
    ax.set_ylabel(r"Statistical Power $\pi(n, \delta = 0.25)$", fontsize=11, fontweight='bold')
    ax.set_title(r"(c) Impact of Superspreading $k$ on Surveillance Capacity", fontsize=12, fontweight='bold', pad=10)
    ax.grid(True, ls=":", color='gray', alpha=0.35)
    ax.tick_params(direction='out', length=4, width=0.8, labelsize=9.5)
    ax.legend(fontsize=8.0, loc='lower right', framealpha=0.92, edgecolor='#CCCCCC')

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
