# -*- coding: utf-8 -*-
"""
Theoretical Simulation Suite:
1. Monte Carlo verification of Proposition 1 (Var(R_hat | n, R_t))
2. Monte Carlo verification of Proposition 2 (Var(R_hat | n) with environmental stochasticity)
3. Crossover point m_times verification and variance decomposition
4. Numerical consistency audit: m_times = 53.1
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Styling
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_FIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'figures')
os.makedirs(OUTPUT_FIG_DIR, exist_ok=True)

def simulate_branching_nb(n, R_t, k, rng, reps=1):
    p_nb = k / (k + R_t)
    n_nb = n * k
    I_t = rng.negative_binomial(n_nb, p_nb, size=reps)
    return I_t

def simulate_observation(I_t, rho, rng):
    return rng.binomial(I_t, rho)

def run_prop1_and_prop2_mc(reps=50000, seed=20260923):
    rng = np.random.default_rng(seed)
    
    R_bar = 1.15
    v_R = 0.04
    k = 0.35
    rho = 0.25
    
    n_grid = np.array([10, 25, 50, 100, 250, 500, 1000, 2500, 5000])
    
    emp_var_p1 = []
    ana_var_p1 = []
    
    emp_var_p2 = []
    ana_var_p2 = []
    
    # 1. Proposition 1: Fixed R_t = R_bar
    for n in n_grid:
        sub_rng = rng.spawn(1)[0]
        I_samples = simulate_branching_nb(n, R_bar, k, sub_rng, reps=reps)
        C_samples = simulate_observation(I_samples, rho, sub_rng)
        R_hat_p1 = C_samples / (rho * n)
        
        emp_v1 = np.var(R_hat_p1, ddof=1)
        ana_v1 = R_bar / (rho * n) + (R_bar**2) / (k * n)
        
        emp_var_p1.append(emp_v1)
        ana_var_p1.append(ana_v1)
        
    # 2. Proposition 2: Random R_t ~ Gamma(shape, scale) with mean R_bar and var v_R
    gamma_k = (R_bar**2) / v_R
    gamma_theta = v_R / R_bar
    
    for n in n_grid:
        sub_rng = rng.spawn(1)[0]
        R_t_samples = sub_rng.gamma(gamma_k, gamma_theta, size=reps)
        
        p_nb = k / (k + R_t_samples)
        n_nb = n * k
        I_samples = sub_rng.negative_binomial(n_nb, p_nb)
        C_samples = sub_rng.binomial(I_samples, rho)
        R_hat_p2 = C_samples / (rho * n)
        
        emp_v2 = np.var(R_hat_p2, ddof=1)
        ana_v2 = v_R + R_bar / (rho * n) + (R_bar**2 + v_R) / (k * n)
        
        emp_var_p2.append(emp_v2)
        ana_var_p2.append(ana_v2)
        
    df_res = pd.DataFrame({
        "n": n_grid,
        "m": n_grid * rho,
        "emp_var_p1": emp_var_p1,
        "ana_var_p1": ana_var_p1,
        "ratio_p1": np.array(emp_var_p1) / np.array(ana_var_p1),
        "emp_var_p2": emp_var_p2,
        "ana_var_p2": ana_var_p2,
        "ratio_p2": np.array(emp_var_p2) / np.array(ana_var_p2),
    })
    return df_res

def plot_simulation_results(df_res):
    R_bar = 1.15
    v_R = 0.04
    k = 0.35
    rho = 0.25
    
    A = R_bar + rho * (R_bar**2 + v_R) / k
    m_times = A / v_R  # Exactly 53.080357...
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), dpi=300)
    
    # Panel 1: Prop 1 vs Prop 2 Variance
    ax = axes[0]
    ax.loglog(df_res["m"], df_res["ana_var_p1"], 'b--', lw=2, label=r"Prop 1 ($R_t$ parameter): $\frac{R_t}{\rho n} + \frac{R_t^2}{kn}$")
    ax.loglog(df_res["m"], df_res["emp_var_p1"], 'bo', alpha=0.7, label="Prop 1 Monte Carlo")
    
    ax.loglog(df_res["m"], df_res["ana_var_p2"], 'r-', lw=2, label=r"Prop 2 ($\bar{R}$ total): $v_R + \frac{A}{m}$")
    ax.loglog(df_res["m"], df_res["emp_var_p2"], 'rs', alpha=0.7, label="Prop 2 Monte Carlo")
    
    ax.axhline(v_R, color='gray', linestyle=':', lw=1.5, label=r"Env Variance Floor $v_R = 0.04$")
    ax.axvline(m_times, color='darkgreen', linestyle='-.', lw=1.5, label=rf"Crossover $m_\times = {m_times:.1f}$")
    
    ax.set_xlabel(r"Expected Reported Cases $m = \rho n$ (Log Scale)", fontsize=11)
    ax.set_ylabel(r"Estimation Variance $\operatorname{Var}(\widehat{R}_t)$ (Log Scale)", fontsize=11)
    ax.set_title(r"(a) Variance Convergence & Floor $v_R$", fontsize=12, fontweight='bold')
    ax.grid(True, which="both", ls=":", alpha=0.5)
    ax.legend(fontsize=8, loc='lower left')
    
    # Panel 2: Ratio of Monte Carlo to Analytical
    ax = axes[1]
    ax.plot(df_res["m"], df_res["ratio_p1"], 'b-o', lw=1.8, label="Prop 1 (MC / Analytical)")
    ax.plot(df_res["m"], df_res["ratio_p2"], 'r-s', lw=1.8, label="Prop 2 (MC / Analytical)")
    ax.axhline(1.0, color='black', linestyle='--', lw=1.2)
    ax.set_xscale('log')
    ax.set_ylim(0.97, 1.03)
    ax.set_xlabel(r"Expected Reported Cases $m = \rho n$ (Log Scale)", fontsize=11)
    ax.set_ylabel("Empirical Variance / Analytical Formula", fontsize=11)
    ax.set_title("(b) Exact Finite-Sample Agreement", fontsize=12, fontweight='bold')
    ax.grid(True, ls=":", alpha=0.5)
    ax.legend(fontsize=9)
    
    # Panel 3: Variance Component Share
    ax = axes[2]
    m_dense = np.logspace(0.5, 3.5, 200)
    var_case = A / m_dense
    share_case = var_case / (var_case + v_R)
    share_env = v_R / (var_case + v_R)
    
    ax.plot(m_dense, share_case * 100, 'b-', lw=2.2, label=r"Scale-Dep. Var Share $\frac{A/m}{v_R + A/m}$")
    ax.plot(m_dense, share_env * 100, 'r-', lw=2.2, label=r"Env Var Share $\frac{v_R}{v_R + A/m}$")
    ax.axvline(m_times, color='darkgreen', linestyle='-.', lw=1.8, label=rf"Crossover $m_\times = {m_times:.1f}$ (50% / 50%)")
    ax.axhline(50, color='gray', linestyle=':', lw=1.2)
    
    ax.set_xscale('log')
    ax.set_xlabel(r"Expected Reported Cases $m = \rho n$ (Log Scale)", fontsize=11)
    ax.set_ylabel("Variance Component Percentage (%)", fontsize=11)
    ax.set_title("(c) Error Budget Transition Across $m_\times$", fontsize=12, fontweight='bold')
    ax.grid(True, ls=":", alpha=0.5)
    ax.legend(fontsize=9, loc='center right')
    
    plt.tight_layout()
    pdf_path = os.path.join(OUTPUT_FIG_DIR, "fig1_theory_simulation_verification.pdf")
    png_path = os.path.join(OUTPUT_FIG_DIR, "fig1_theory_simulation_verification.png")
    plt.savefig(pdf_path, bbox_inches='tight')
    plt.savefig(png_path, bbox_inches='tight')
    plt.close()
    print(f"Saved figure to {pdf_path}, with m_times = {m_times:.1f}")

if __name__ == "__main__":
    df_res = run_prop1_and_prop2_mc()
    plot_simulation_results(df_res)
