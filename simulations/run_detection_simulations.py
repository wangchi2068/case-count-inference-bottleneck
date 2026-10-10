# -*- coding: utf-8 -*-
"""
Simulation Experiment: Single-period Outbreak Detection Power and Scale Requirements.
Tests:
1. Empirical Type I error control: Monotone Likelihood Ratio exact test vs. Wald asymptotic test.
2. Power curves and 80% detection threshold scaling m_{80%}.
3. The impact of superspreading overdispersion k on surveillance capacity requirements.
Zero-occlusion design: clean curves, no text bubbles inside plotting area, all numbers in legend/caption.
"""
import os
import numpy as np
import scipy.stats as stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_FIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'figures')
os.makedirs(OUTPUT_FIG_DIR, exist_ok=True)

def nb_rvs(n, k, rho, R, size=1):
    r = n * k
    p_star = k / (k + rho * R)
    return stats.nbinom.rvs(r, p_star, size=size)

def compute_exact_critical_value(n, k, rho, alpha=0.05):
    r = n * k
    p_star = k / (k + rho * 1.0)
    c = stats.nbinom.ppf(1.0 - alpha, r, p_star)
    while stats.nbinom.sf(c - 1, r, p_star) > alpha:
        c += 1
    while c > 0 and stats.nbinom.sf(c - 2, r, p_star) <= alpha:
        c -= 1
    return int(c)

def compute_exact_power(c_alpha, n, k, rho, delta):
    r = n * k
    p_star_alt = k / (k + rho * (1.0 + delta))
    return stats.nbinom.sf(c_alpha - 1, r, p_star_alt)

def compute_normal_approx_power(n, k, rho, delta, alpha=0.05):
    z_alpha = stats.norm.ppf(1.0 - alpha)
    V0 = 1.0 / (rho * n) + 1.0 / (k * n)
    V1 = (1.0 + delta) / (rho * n) + ((1.0 + delta)**2) / (k * n)
    z_score = (delta - z_alpha * np.sqrt(V0)) / np.sqrt(V1)
    return stats.norm.cdf(z_score)

def enumerate_m80(n_max, k, rho, delta, alpha=0.05):
    for n in range(1, n_max + 1):
        c_alpha = compute_exact_critical_value(n, k, rho, alpha)
        pow_val = compute_exact_power(c_alpha, n, k, rho, delta)
        if pow_val >= 0.80:
            return n
    return n_max

def run_detection_experiments():
    k_vals = [0.1, 0.35, 1.0]
    m_eval = [5, 10, 20, 40, 80, 150, 300, 600]
    rho = 0.25
    n_sims = 30000
    alpha = 0.05
    z_crit = stats.norm.ppf(1.0 - alpha)
    
    size_results = {k: {"m": m_eval, "empirical_exact": [], "empirical_wald": []} for k in k_vals}
    
    np.random.seed(42)
    for k in k_vals:
        for m in m_eval:
            n = int(round(m / rho))
            V0 = 1.0 / m + 1.0 / (k * n)
            c_alpha = compute_exact_critical_value(n, k, rho, alpha)
            C_samples = nb_rvs(n, k, rho, R=1.0, size=n_sims)
            
            p_exact = np.mean(C_samples >= c_alpha)
            size_results[k]["empirical_exact"].append(p_exact)
            
            R_hat = C_samples / (rho * n)
            Z_wald = (R_hat - 1.0) / np.sqrt(V0)
            p_wald = np.mean(Z_wald >= z_crit)
            size_results[k]["empirical_wald"].append(p_wald)

    n_dense = np.logspace(np.log10(16), np.log10(3200), 120)
    m_dense = n_dense * rho
    return size_results, m_dense, n_dense

def plot_fig2_detection(size_results, m_dense, n_dense):
    fig, axes = plt.subplots(1, 3, figsize=(16.5, 4.6), dpi=300)
    
    rho = 0.25
    alpha = 0.05
    col_k01 = '#D73027'
    col_k035 = '#1F78B4'
    col_k10 = '#2CA25F'
    colors_k = {0.1: col_k01, 0.35: col_k035, 1.0: col_k10}

    # ==========================================
    # Panel (a): Type I Error Control (Pure, no text occlusions)
    # ==========================================
    ax = axes[0]
    ax.fill_between([3.5, 900], 0.05, 0.125, color='#FEE0D2', alpha=0.45, zorder=0)
    ax.fill_between([3.5, 900], 0.00, 0.05, color='#E5F5E0', alpha=0.45, zorder=0)
    ax.axhline(0.05, color='#333333', linestyle='--', lw=1.5, zorder=2, label=r"Nominal Size $\alpha = 0.05$")
    
    for k in [0.1, 0.35, 1.0]:
        m = size_results[k]["m"]
        ax.plot(m, size_results[k]["empirical_exact"], marker='o', color=colors_k[k], lw=2.0, ms=5.0,
                mec='white', mew=0.8, zorder=4, label=rf"Exact NB ($k={k}$)")
        ax.plot(m, size_results[k]["empirical_wald"], marker='^', linestyle=':', color=colors_k[k], lw=1.6, ms=5.0,
                mec='white', mew=0.8, alpha=0.85, zorder=4, label=rf"Wald Approx ($k={k}$)")
        
    ax.set_xscale('log')
    ax.set_xlim(4.0, 800)
    ax.set_ylim(0.00, 0.115)
    ax.set_xlabel(r"Expected Reported Cases $m = \rho n$ (Log Scale)", fontsize=10.5, fontweight='bold')
    ax.set_ylabel(r"Empirical Type I Error Rate $\widehat{\alpha}$", fontsize=10.5, fontweight='bold')
    ax.set_title(r"(a) Type I Error: Exact NB vs. Wald", fontsize=11.5, fontweight='bold')
    ax.grid(True, ls=":", color='gray', alpha=0.35)
    ax.tick_params(direction='out', length=4, width=0.8, labelsize=9.5)
    ax.legend(fontsize=7.2, loc='upper right', framealpha=0.92, edgecolor='#CCCCCC', ncol=2)

    # ==========================================
    # Panel (b): Power Curves across Effect Size delta (Zero occlusion)
    # ==========================================
    ax = axes[1]
    k_fixed = 0.35
    delta_palette = {
        0.50: ('#2CA25F', 'Strong', 57),
        0.30: ('#756BB1', 'Moderate', 142),
        0.15: ('#E6550D', 'Mild', 518)
    }
    
    ax.axhline(0.80, color='#555555', linestyle='--', lw=1.2, zorder=2)
    
    for delta, (col, d_name, m80_val) in delta_palette.items():
        n80 = enumerate_m80(20000, k_fixed, rho, delta)
        m80 = round(n80 * rho, 1)
        
        p_ex = [compute_exact_power(compute_exact_critical_value(n, k_fixed, rho, alpha), n, k_fixed, rho, delta) for n in n_dense]
        p_nm = [compute_normal_approx_power(n, k_fixed, rho, delta, alpha) for n in n_dense]
        
        # Plot curves: legend directly carries the threshold value!
        ax.plot(m_dense, p_ex, color=col, lw=2.2, zorder=3, 
                label=rf"$\delta={delta}$ ({d_name}, $m_{{80\%}}={m80:.0f}$)")
        ax.plot(m_dense, p_nm, color=col, linestyle=':', lw=1.2, alpha=0.65, zorder=3)
        
        # Clean drop lines down to x-axis, no bulky text bubbles in the middle
        if m80:
            ax.plot(m80, 0.80, marker='o', ms=6.0, color=col, mec='white', mew=1.2, zorder=5)
            ax.vlines(m80, 0, 0.80, color=col, linestyle=':', lw=1.2, alpha=0.75, zorder=2)
        
    ax.set_xscale('log')
    ax.set_xlim(4.0, 800)
    ax.set_ylim(0.0, 1.03)
    ax.set_xlabel(r"Expected Reported Cases $m = \rho n$ (Log Scale)", fontsize=10.5, fontweight='bold')
    ax.set_ylabel(r"Statistical Power $\pi(n, \delta)$", fontsize=10.5, fontweight='bold')
    ax.set_title(r"(b) Detection Power vs. Scale ($k=0.35$)", fontsize=11.5, fontweight='bold')
    ax.grid(True, ls=":", color='gray', alpha=0.35)
    ax.tick_params(direction='out', length=4, width=0.8, labelsize=9.5)
    # Legend placed in clean upper left where power is low at small m
    ax.legend(fontsize=7.8, loc='upper left', framealpha=0.92, edgecolor='#CCCCCC')

    # ==========================================
    # Panel (c): Impact of Overdispersion k (Zero occlusion)
    # ==========================================
    ax = axes[2]
    delta_fixed = 0.25
    k_palette = {
        1.00: (col_k10, 'Weak Heterogeneity', 142),
        0.35: (col_k035, 'Typical Respiratory', 176),
        0.10: (col_k01, 'High Superspreading', 415)
    }
    
    ax.axhline(0.80, color='#555555', linestyle='--', lw=1.2, zorder=2)
    
    for k_val, (col, k_name, m80_val) in k_palette.items():
        n80 = enumerate_m80(20000, k_val, rho, delta_fixed)
        m80 = round(n80 * rho, 1)
        
        p_ex = [compute_exact_power(compute_exact_critical_value(n, k_val, rho, alpha), n, k_val, rho, delta_fixed) for n in n_dense]
        # Legend carries threshold m80 explicitly
        ax.plot(m_dense, p_ex, color=col, lw=2.2, zorder=3, 
                label=rf"$k={k_val:.2f}$ ({k_name}, $m_{{80\%}}={m80:.0f}$)")
        
        if m80:
            ax.plot(m80, 0.80, marker='o', ms=6.0, color=col, mec='white', mew=1.2, zorder=5)
            ax.vlines(m80, 0, 0.80, color=col, linestyle=':', lw=1.2, alpha=0.75, zorder=2)

    ax.set_xscale('log')
    ax.set_xlim(4.0, 800)
    ax.set_ylim(0.0, 1.03)
    ax.set_xlabel(r"Expected Reported Cases $m = \rho n$ (Log Scale)", fontsize=10.5, fontweight='bold')
    ax.set_ylabel(r"Statistical Power $\pi(n, \delta = 0.25)$", fontsize=10.5, fontweight='bold')
    ax.set_title(r"(c) Impact of Overdispersion $k$ ($\approx 2.9\times$ penalty)", fontsize=11.5, fontweight='bold')
    ax.grid(True, ls=":", color='gray', alpha=0.35)
    ax.tick_params(direction='out', length=4, width=0.8, labelsize=9.5)
    ax.legend(fontsize=7.8, loc='upper left', framealpha=0.92, edgecolor='#CCCCCC')

    plt.tight_layout()
    pdf_path = os.path.join(OUTPUT_FIG_DIR, "fig2_growth_detection_power.pdf")
    png_path = os.path.join(OUTPUT_FIG_DIR, "fig2_growth_detection_power.png")
    plt.savefig(pdf_path, bbox_inches='tight')
    plt.savefig(png_path, bbox_inches='tight')
    plt.close()
    print(f"Generated clean zero-occlusion Figure 2 at {pdf_path}")

if __name__ == "__main__":
    size_res, m_dense, n_dense = run_detection_experiments()
    plot_fig2_detection(size_res, m_dense, n_dense)
