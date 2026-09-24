# -*- coding: utf-8 -*-
"""
Simulation Suite 3: Renewal Process Growth Statistic and Ex-ante Forecasting Error
1. Evaluates ex-post proxy growth statistic error: (G_{t+1} - R_bar)^2
   where G_{t+1} = C_{t+1} / D_t with D_t = sum_s w_s C_{t+1-s} (evaluating only on active history D_t > 0).
2. Evaluates ex-ante one-step case forecasting relative error:
   hat{C}_{t+1|t} = R_bar * D_t
   RelMSE = E[ ((C_{t+1} - hat{C}_{t+1|t}) / hat{C}_{t+1|t})^2 | D_t > 0 ] = E[ (G_{t+1} - R_bar)^2 / R_bar^2 | D_t > 0 ]
3. Compares with the idealized reference benchmarks:
   V_growth(m) = v_R + A/m
   RelMSE_bench(m) = (v_R + A/m) / R_bar^2
4. Evaluates diminishing marginal benefit per doubling of cases:
   Analytical: 1 / [2 * (1 + m / m_times)]
   Empirical: (RelMSE(m) - RelMSE(2m)) / RelMSE(m) (identical for growth statistic and forecasting)
5. Outputs publication-quality Figure 3.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_FIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'figures')
os.makedirs(OUTPUT_FIG_DIR, exist_ok=True)

def run_renewal_forecasting_experiments():
    R_bar = 1.15
    v_R = 0.04
    k = 0.35
    rho = 0.25
    
    A = R_bar + rho * (R_bar**2 + v_R) / k # 2.1232
    m_times = A / v_R # 53.08
    
    w = np.array([0.45, 0.35, 0.15, 0.05])
    S = len(w)
    
    gamma_k = (R_bar**2) / v_R
    gamma_theta = v_R / R_bar
    
    target_m_grid = np.array([6, 12, 25, 50, 100, 200, 400, 800])
    reps = 150
    rng = np.random.default_rng(20260925)
    
    results = []
    
    for tm in target_m_grid:
        target_Lambda = tm / rho
        growth_errs = []
        zero_hist_count = 0
        total_eval_weeks = 0
        
        for rep in range(reps):
            T = 30
            I = np.zeros(T)
            C = np.zeros(T)
            
            # Initial conditions
            I[:S] = target_Lambda
            for s in range(S):
                C[s] = rng.binomial(int(I[s]), rho)
                
            for t in range(S, T):
                R_t = rng.gamma(gamma_k, gamma_theta)
                lam_true = np.sum(w * I[t-S:t][::-1])
                
                p_nb = k / (k + R_t)
                I_t = rng.negative_binomial(lam_true * k, p_nb)
                I[t] = max(1, I_t)
                
                C_t = rng.binomial(int(I[t]), rho)
                C[t] = C_t
                
                hist_pressure = np.sum(w * C[t-S:t][::-1])
                total_eval_weeks += 1
                
                if hist_pressure <= 0:
                    zero_hist_count += 1
                    continue
                    
                # 1. Ex-post normalized growth statistic: G_{t+1} = C_{t+1} / D_t
                g_stat = C_t / hist_pressure
                growth_errs.append((g_stat - R_bar)**2)
                
        # 无数据依赖截尾：保留全部活跃周（D_t>0）观测，与正文披露口径一致
        mean_growth = np.mean(growth_errs)
        se_growth = np.std(growth_errs) / np.sqrt(len(growth_errs))
        
        # Point-by-point algebraic identity: rel_forecast_err = growth_err / R_bar^2
        mean_forecast = mean_growth / (R_bar**2)
        se_forecast = se_growth / (R_bar**2)
        
        results.append({
            "target_m": tm,
            "total_weeks": total_eval_weeks,
            "zero_count": zero_hist_count,
            "effective_weeks": total_eval_weeks - zero_hist_count,
            "zero_prop": zero_hist_count / total_eval_weeks,
            "growth_mse": mean_growth,
            "growth_se": se_growth,
            "forecast_rel_mse": mean_forecast,
            "forecast_se": se_forecast,
            "growth_bench": v_R + A / tm,
            "forecast_bench": (v_R + A / tm) / (R_bar**2)
        })
        
    df_res = pd.DataFrame(results)
    return df_res, m_times, v_R, A, R_bar

def plot_fig3_forecasting(df_res, m_times, v_R, A, R_bar):
    fig, axes = plt.subplots(1, 3, figsize=(17, 4.6), dpi=300)
    
    m_dense = np.logspace(0.6, 3.1, 150)
    growth_bench_dense = v_R + A / m_dense
    forecast_bench_dense = growth_bench_dense / (R_bar**2)
    
    # Panel (a): Ex-post growth statistic error vs Reference Benchmark
    ax = axes[0]
    ax.loglog(m_dense, growth_bench_dense, 'r-', lw=2.2, label=r"Single-Gen Ref: $v_R + \frac{A}{m}$")
    ax.axhline(v_R, color='gray', linestyle=':', lw=1.5, label=rf"Environmental Floor $v_R = {v_R}$")
    ax.axvline(m_times, color='darkgreen', linestyle='-.', lw=1.8, label=rf"Crossover $m_\times = {m_times:.1f}$")
    
    ax.errorbar(df_res["target_m"], df_res["growth_mse"], yerr=df_res["growth_se"]*1.96,
                fmt='o', color='black', ecolor='gray', elinewidth=1.5, capsize=3.5,
                markersize=5.5, label=r"Renewal Sim ($\mathbb{E}[(G_{t+1}-\bar{R})^2 \mid D_t>0]$)")
    
    ax.set_xlabel(r"Expected Weekly Report Scale $m = \rho \Lambda_t$ (Log Scale)", fontsize=10.5)
    ax.set_ylabel(r"Growth Statistic Error / Reference (Log Scale)", fontsize=10.5)
    ax.set_title(r"(a) Ex-post Growth Statistic Error vs Reference", fontsize=11.5, fontweight='bold')
    ax.grid(True, which="both", ls=":", alpha=0.5)
    ax.legend(fontsize=7.5, loc='lower left')
    
    # Panel (b): Ex-ante case forecasting Relative MSE vs Scaled Reference
    ax = axes[1]
    ax.loglog(m_dense, forecast_bench_dense, 'purple', lw=2.2, label=r"Scaled Ref: $\frac{v_R + A/m}{\bar{R}^2}$")
    ax.axhline(v_R / (R_bar**2), color='gray', linestyle=':', lw=1.5, label=rf"Asymptotic Floor $\frac{{v_R}}{{\bar{{R}}^2}} = {v_R/(R_bar**2):.4f}$")
    ax.axvline(m_times, color='darkgreen', linestyle='-.', lw=1.8, label=rf"Crossover $m_\times = {m_times:.1f}$")
    
    ax.errorbar(df_res["target_m"], df_res["forecast_rel_mse"], yerr=df_res["forecast_se"]*1.96,
                fmt='s', color='navy', ecolor='gray', elinewidth=1.5, capsize=3.5,
                markersize=5.5, label=r"Renewal Sim (Ex-ante RelMSE)")
    
    ax.set_xlabel(r"Expected Weekly Report Scale $m = \rho \Lambda_t$ (Log Scale)", fontsize=10.5)
    ax.set_ylabel(r"Ex-ante Case Forecast RelMSE (Log Scale)", fontsize=10.5)
    ax.set_title(r"(b) Ex-ante Case Forecast RelMSE vs Scaled Reference", fontsize=11.5, fontweight='bold')
    ax.grid(True, which="both", ls=":", alpha=0.5)
    ax.legend(fontsize=7.5, loc='lower left')
    
    # Panel (c): Diminishing marginal benefit per doubling of case scale
    ax = axes[2]
    analytical_doubling = 100.0 / (2.0 * (1.0 + m_dense / m_times))
    
    # Empirical doubling gains (algebraically identical for both metrics!)
    emp_m = df_res["target_m"].values
    emp_growth = df_res["growth_mse"].values
    
    emp_doubling_m = []
    emp_doubling_gain = []
    
    for i in range(len(emp_m) - 1):
        if np.isclose(emp_m[i+1] / emp_m[i], 2.0, atol=0.1):
            emp_doubling_m.append(np.sqrt(emp_m[i] * emp_m[i+1]))
            emp_doubling_gain.append((emp_growth[i] - emp_growth[i+1]) / emp_growth[i] * 100.0)
            
    ax.plot(m_dense, analytical_doubling, 'navy', lw=2.2, label=r"Analytical: $\frac{1}{2(1 + m/m_\times)}$")
    ax.plot(emp_doubling_m, emp_doubling_gain, 'ro--', lw=1.8, markersize=6,
            label=r"Renewal Sim (Empirical Doubling Gain)")
    
    ax.axvline(m_times, color='darkgreen', linestyle='-.', lw=1.8, label=rf"$m_\times = {m_times:.1f}$ (25.0%)")
    ax.axhline(25.0, color='gray', linestyle=':', lw=1.2)
    
    # Annotations
    ax.scatter([10, m_times, 200], [100.0/(2*(1+10/m_times)), 25.0, 100.0/(2*(1+200/m_times))],
               color='crimson', zorder=5)
    ax.annotate(r"$m=10$ (42.1%)", xy=(10, 42.1), xytext=(11, 46),
                fontsize=8, fontweight='bold', color='navy')
    ax.annotate(r"$m_\times=53.1$ (25.0%)", xy=(m_times, 25.0), xytext=(m_times*1.1, 28),
                fontsize=8, fontweight='bold', color='darkgreen')
    ax.annotate(r"$m=200$ (10.5%)", xy=(200, 10.5), xytext=(110, 14),
                fontsize=8, fontweight='bold', color='purple')
    
    ax.set_xscale('log')
    ax.set_ylim(0, 58)
    ax.set_xlabel(r"Reported Case Scale $m$ (Log Scale)", fontsize=10.5)
    ax.set_ylabel(r"Relative Error Reduction (%) per Doubling", fontsize=10.5)
    ax.set_title(r"(c) Diminishing Benefit per Case Doubling", fontsize=11.5, fontweight='bold')
    ax.grid(True, ls=":", alpha=0.5)
    ax.legend(fontsize=7.5, loc='upper right')
    
    plt.tight_layout()
    pdf_path = os.path.join(OUTPUT_FIG_DIR, "fig3_forecasting_saturation_crossover.pdf")
    png_path = os.path.join(OUTPUT_FIG_DIR, "fig3_forecasting_saturation_crossover.png")
    plt.savefig(pdf_path, bbox_inches='tight')
    plt.savefig(png_path, bbox_inches='tight')
    plt.close()
    print(f"Generated clean Figure 3 at {pdf_path}")

if __name__ == "__main__":
    df_res, m_times, v_R, A, R_bar = run_renewal_forecasting_experiments()
    print(df_res[["target_m", "total_weeks", "zero_count", "effective_weeks", "zero_prop", "growth_mse", "forecast_rel_mse"]])
    plot_fig3_forecasting(df_res, m_times, v_R, A, R_bar)
