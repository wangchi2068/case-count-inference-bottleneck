# -*- coding: utf-8 -*-
"""
Generate Publication-Quality Landscape Ultra-Large-Font Roadmap Diagram (fig0_technical_roadmap)
Solves the "font too small" issue fundamentally:
- Landscape ratio (18.0 x 9.8 inches) perfectly fits LaTeX textwidth without vertical squishing!
- Base font size boosted to 13pt - 24pt (LARGER than normal body text when printed/viewed)
- 4-Stage Horizontal Flow: Inputs -> Theory & Limits -> Design & Testing -> Empirical Evidence
- Bottom Banner: Clear Public Health Policy Matrix
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_landscape_ultra_large_roadmap():
    # Landscape dimension: 18.2 inches wide, 9.8 inches high
    # When embedded at width=\textwidth in LaTeX, scaling is ~0.7x, meaning 14pt renders as ~10-11pt!
    fig_w, fig_h = 18.2, 9.8
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=300)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    plt.rcParams['mathtext.fontset'] = 'cm'
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

    # Palette
    C_NAVY      = '#0F2744' # Dark Oxford Navy
    C_HEADER_BG = '#0F2744'
    C_CARD_BG   = '#FFFFFF'
    C_CARD_BD   = '#64748B' # Slate 500
    C_STAGE_BG  = '#F8FAFC' # Slate 50
    C_BLUE_DARK = '#1E3A8A' # Blue 900
    C_BLUE_LT   = '#EFF6FF' # Blue 50
    C_BLUE_BD   = '#93C5FD' # Blue 300
    C_AMBER_LT  = '#FFFBEB' # Amber 50
    C_AMBER_BD  = '#FCD34D' # Amber 300
    C_PURPLE_LT = '#FAF5FF' # Purple 50
    C_PURPLE_BD = '#D8B4FE' # Purple 300
    C_GREEN_BG  = '#F0FDF4' # Emerald 50
    C_GREEN_BD  = '#86EFAC' # Emerald 300
    C_GREEN_TXT = '#14532D' # Emerald 900
    C_TEXT_DARK = '#0F172A' # Slate 900

    def draw_box(x, y, w, h, fill_color, border_color, border_width=1.5, radius=1.6, zorder=1):
        box = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle=f"round,pad=0.25,rounding_size={radius}",
            fc=fill_color, ec=border_color, lw=border_width,
            zorder=zorder
        )
        ax.add_patch(box)
        return box

    def draw_arrow(x1, y1, x2, y2, color='#2563EB', lw=2.5):
        ax.annotate(
            '', xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=20),
            zorder=5
        )

    # =========================================================================
    # Header Banner (Ultra Large Font: 22pt / 12pt)
    # =========================================================================
    draw_box(1.5, 88.5, 97.0, 9.8, C_HEADER_BG, C_HEADER_BG, radius=1.4)
    ax.text(50, 94.2, "全文研究技术路线与端到端理论推断架构图", fontsize=22, fontweight='bold', color='#FFFFFF', ha='center', va='center')
    ax.text(50, 90.5, "End-to-End Architecture: Known Inputs  ==>  Branching Dynamics  ==>  Asymptotic Limits  ==>  Empirical Falsification",
            fontsize=12.5, color='#94A3B8', ha='center', va='center')

    # =========================================================================
    # 4 Main Horizontal Columns (Stages)
    # =========================================================================
    w_col = 22.8
    y_col = 14.5
    h_col = 71.0

    # -------------------------------------------------------------------------
    # Column 1: Stage I - Inputs & Observation
    # -------------------------------------------------------------------------
    x1 = 1.5
    draw_box(x1, y_col, w_col, h_col, C_STAGE_BG, C_CARD_BD)
    # Column Header
    draw_box(x1 + 0.6, y_col + h_col - 5.5, w_col - 1.2, 4.8, '#1E293B', '#1E293B', radius=1.0)
    ax.text(x1 + w_col/2, y_col + h_col - 3.1, "阶段 I · 多源已知输入", fontsize=15, fontweight='bold', color='#FFFFFF', ha='center', va='center')

    # Box 1.1: Data
    draw_box(x1 + 0.8, 63.2, w_col - 1.6, 15.3, C_CARD_BG, C_CARD_BD)
    ax.text(x1 + w_col/2, 75.8, "① 真实观测数据流", fontsize=13.5, fontweight='bold', color=C_BLUE_DARK, ha='center', va='center')
    ax.text(x1 + 1.8, 73.0, "• 周报告住院数:  $C_t \\in \\mathbb{N}$\n"
                            "• 机构覆盖率:  报告率 $\\rho$ 代理\n"
                            "• 历史暴露压力 (代际核 $w$ 卷积):\n"
                            "  $D_t = \\sum_s w_s C_{t+1-s}$",
            fontsize=11.0, color=C_TEXT_DARK, va='top', linespacing=1.4)

    # Box 1.2: Parameters
    draw_box(x1 + 0.8, 41.5, w_col - 1.6, 20.5, C_CARD_BG, C_CARD_BD)
    ax.text(x1 + w_col/2, 59.5, "② 生物学先验参数", fontsize=13.5, fontweight='bold', color=C_BLUE_DARK, ha='center', va='center')
    ax.text(x1 + 1.8, 56.8, "• 超传播离散度:  $k$\n"
                            "  流感 $k = 0.35$, COVID $0.1 \\sim 0.3$\n"
                            "• 哨点报告率:  $\\rho \\in [0.006, 0.021]$\n"
                            "• 宏观环境三元组:  $(R_{\\mathrm{base}}, v_R, r)$\n"
                            "  均值 $R_{\\mathrm{base}}$, 方差 $v_R$, 自相关 $r$\n"
                            "• 代际时滞分布:  $w$ (平均 10.2天)",
            fontsize=11.0, color=C_TEXT_DARK, va='top', linespacing=1.4)

    # Box 1.3: Costs
    draw_box(x1 + 0.8, 16.0, w_col - 1.6, 24.0, C_CARD_BG, C_CARD_BD)
    ax.text(x1 + w_col/2, 37.5, "③ 运筹成本与政策红线", fontsize=13.5, fontweight='bold', color=C_BLUE_DARK, ha='center', va='center')
    ax.text(x1 + 1.8, 34.5, "• 假阳性红线:  $\\alpha = 0.05$\n"
                            "• 单期固定成本:  $c_0 > 0$ (运维维持)\n"
                            "• 边际检测成本:  $c_1 > 0$ (单例耗材)\n"
                            "• 总经费预算:  $B_{\\mathrm{cost}} = T(c_0 + c_1 m)$",
            fontsize=11.0, color=C_TEXT_DARK, va='top', linespacing=1.4)

    draw_arrow(x1 + w_col + 0.2, 50.0, x1 + w_col + 1.7, 50.0)

    # -------------------------------------------------------------------------
    # Column 2: Stage II - Mechanisms & Asymptotic Theory
    # -------------------------------------------------------------------------
    x2 = 26.2
    draw_box(x2, y_col, w_col, h_col, C_STAGE_BG, C_CARD_BD)
    draw_box(x2 + 0.6, y_col + h_col - 5.5, w_col - 1.2, 4.8, C_BLUE_DARK, C_BLUE_DARK, radius=1.0)
    ax.text(x2 + w_col/2, y_col + h_col - 3.1, "阶段 II · 微观机制与理论确界", fontsize=15, fontweight='bold', color='#FFFFFF', ha='center', va='center')

    # Box 2.1: Branching & Thinning
    draw_box(x2 + 0.8, 59.0, w_col - 1.6, 19.5, C_CARD_BG, C_CARD_BD)
    ax.text(x2 + w_col/2, 75.8, "负二项分支与二项抽稀封闭", fontsize=13.5, fontweight='bold', color=C_NAVY, ha='center', va='center')
    ax.text(x2 + 1.8, 72.8, "• 换元积分:  $Y \\sim \\mathrm{NB}(k, p), \\; p = \\frac{k}{k+R_t}$\n"
                            "  [物理顿悟] 传人是失败，终止是成功！\n"
                            "• 母函数复合闭合定理: $G_C(s) = G_I(G_B(s))$\n"
                            "  $\\Rightarrow \\; C_t \\sim \\mathrm{NB}(nk, \\; \\frac{k}{k+\\rho R_t})$\n"
                            "• Kurtz 定理: $n \\to \\infty$ 弱收敛于 ODE 流形",
            fontsize=10.8, color=C_TEXT_DARK, va='top', linespacing=1.38)

    # Box 2.2: Target A
    draw_box(x2 + 0.8, 38.0, w_col - 1.6, 19.5, C_CARD_BG, C_CARD_BD)
    ax.text(x2 + w_col/2, 54.8, "目标 A: 瞬态再生数 $R_t$ (命题 1)", fontsize=13.5, fontweight='bold', color=C_BLUE_DARK, ha='center', va='center')
    ax.text(x2 + 1.8, 51.8, "• 估计量:  $\\hat{R}_t = \\frac{C_t}{m}$  (无偏 UMVUE)\n"
                            "• 严格达到 Cramér-Rao 下界: $\\mathcal{I}(R_t)^{-1}$\n"
                            "• 方差标度律:  $\\mathrm{Var} = \\mathcal{O}(1/m) \\to 0$\n"
                            "  [理论结论] 单代视角下规模收益无界",
            fontsize=11.0, color=C_TEXT_DARK, va='top', linespacing=1.4)

    # Box 2.3: Target B
    draw_box(x2 + 0.8, 16.0, w_col - 1.6, 20.5, C_AMBER_LT, C_AMBER_BD)
    ax.text(x2 + w_col/2, 33.8, "目标 B: 跨期基准 $R_{\\mathrm{base}}$ (命题 2 & 3)", fontsize=13.5, fontweight='bold', color=C_NAVY, ha='center', va='center')
    ax.text(x2 + 1.8, 30.8, "• 全方差分解:  $\\mathrm{Var}(\\bar{\\hat{R}}) = v_R + \\frac{A}{m}$\n"
                            "• 特征规模平衡点:  $m_\\times \\equiv \\frac{A}{v_R}$  (50/50 分界)\n"
                            "• 杠杆非对称性定理:  提 $\\rho$ 存在硬下界,\n"
                            "  唯有扩大基数 $n$ 利用大数定律逼近底板",
            fontsize=11.0, color=C_TEXT_DARK, va='top', linespacing=1.4)

    draw_arrow(x2 + w_col + 0.2, 50.0, x2 + w_col + 1.7, 50.0)

    # -------------------------------------------------------------------------
    # Column 3: Stage III - Surveillance Design & Testing
    # -------------------------------------------------------------------------
    x3 = 50.9
    draw_box(x3, y_col, w_col, h_col, C_STAGE_BG, C_CARD_BD)
    draw_box(x3 + 0.6, y_col + h_col - 5.5, w_col - 1.2, 4.8, '#0369A1', '#0369A1', radius=1.0)
    ax.text(x3 + w_col/2, y_col + h_col - 3.1, "阶段 III · 运筹设计与机制检验", fontsize=15, fontweight='bold', color='#FFFFFF', ha='center', va='center')

    # Box 3.1: Surveillance Design & Cochran
    draw_box(x3 + 0.8, 48.0, w_col - 1.6, 30.5, C_CARD_BG, C_CARD_BD)
    ax.text(x3 + w_col/2, 75.8, "多期运筹设计与 Cochran 抽样对偶", fontsize=13.5, fontweight='bold', color=C_NAVY, ha='center', va='center')
    ax.text(x3 + 1.8, 72.8, "• 样本预算恒常性 (命题 4):\n"
                            "  总人数 $B = Tm$ 下微观抽样误差恒为 $A/B$\n"
                            "  结论: 单期狂堆人数无效！唯有拉长期数 $T$\n"
                            "• AR(1) 错位相减求和:  $T_{\\mathrm{eff}} \\approx T \\frac{1-r}{1+r}$\n"
                            "• 成本约束凸优化 (推论 1):\n"
                            "  目标方差二阶导 $f''(m) > 0$  [严格凸函数]\n"
                            "• 最优单期规模闭式解:\n"
                            "  $m^* = \\sqrt{\\frac{c_0}{c_1} \\cdot m_\\times}$\n"
                            "  [Cochran (1977) 两阶段抽样完全同构]",
            fontsize=10.8, color=C_TEXT_DARK, va='top', linespacing=1.38)

    # Box 3.2: Testing & Renewal Forecasting
    draw_box(x3 + 0.8, 16.0, w_col - 1.6, 30.5, C_CARD_BG, C_CARD_BD)
    ax.text(x3 + w_col/2, 43.8, "爆发假设检验与更新过程预测偏差", fontsize=13.5, fontweight='bold', color=C_NAVY, ha='center', va='center')
    ax.text(x3 + 1.8, 40.8, "• 假设检验 $H_0: R_t \\leq 1$ (命题 5):\n"
                            "  单调似然比一阶差分 $\\Delta(j) > 0$ 严格成立\n"
                            "  Karlin-Rubin UMP 检验与功效锯齿波\n"
                            "• 检验目标天花板: 越过 $m_{80\\%}$ 后功效饱和\n"
                            "  Wald 检验在小规模失真高达 8.1%\n"
                            "• 更新过程预测方差分解 (命题 6 式 29):\n"
                            "  $\\mathbb{E}[(G - R_{\\mathrm{base}})^2] = \\mathbb{E}[\\frac{\\sigma^2}{D^2}] + \\mathrm{Bias}^2$\n"
                            "  其中偏差项 $\\mathrm{Bias}^2 = \\mathbb{E}[(\\frac{\\mu}{D} - R_{\\mathrm{base}})^2] \\geq 0$\n"
                            "  [双口径澄清] 历史代理必然引入非负预测偏差",
            fontsize=10.6, color=C_TEXT_DARK, va='top', linespacing=1.35)

    draw_arrow(x3 + w_col + 0.2, 50.0, x3 + w_col + 1.7, 50.0)

    # -------------------------------------------------------------------------
    # Column 4: Stage IV - Empirical Evidence & External Validation
    # -------------------------------------------------------------------------
    x4 = 75.6
    draw_box(x4, y_col, w_col, h_col, C_STAGE_BG, C_CARD_BD)
    draw_box(x4 + 0.6, y_col + h_col - 5.5, w_col - 1.2, 4.8, '#047857', '#047857', radius=1.0)
    ax.text(x4 + w_col/2, y_col + h_col - 3.1, "阶段 IV · 大数据实证与外部验证", fontsize=15, fontweight='bold', color='#FFFFFF', ha='center', va='center')

    # Box 4.1: NHSN Main & Peak Reversal
    draw_box(x4 + 0.8, 45.0, w_col - 1.6, 33.5, C_CARD_BG, C_CARD_BD)
    ax.text(x4 + w_col/2, 75.8, "全美 NHSN 流感住院大数据主实证", fontsize=13.5, fontweight='bold', color=C_NAVY, ha='center', va='center')
    ax.text(x4 + 1.8, 72.8, "• 16,218 原始记录 $\\to N = 10,303$ 活跃周样本\n"
                            "  三阶段 $6009 + 420 + 3874 = 10303$ 闭环\n"
                            "• FGLS 仿射拟合: $b = 2.243 \\; (95\\% \\ \\mathrm{CI} \\ [1.50, 3.02])$\n"
                            "  1500 次聚类 BS 证 $b > 0 \\; (p < 10^{-4})$\n"
                            "• 测定经验平衡点:  $m_\\times \\approx 22.6$ 例/周\n"
                            "• 达峰期 88.9% 震撼反转: 均值正交分解\n"
                            "  证实误差源于基准失配而非规模失效！\n"
                            "• 空间弱相关汇聚: 全国加总方差降至 0.0348",
            fontsize=10.6, color=C_TEXT_DARK, va='top', linespacing=1.38)

    # Box 4.2: External Validation
    draw_box(x4 + 0.8, 16.0, w_col - 1.6, 27.5, C_CARD_BG, C_CARD_BD)
    ax.text(x4 + w_col/2, 40.8, "CDC FluSight 与欧洲 COVID 外验", fontsize=13.5, fontweight='bold', color=C_NAVY, ha='center', va='center')
    ax.text(x4 + 1.8, 37.8, "• CDC FluSight 集成预测验证 ($N = 1,177$):\n"
                            "  纯事前口径 $b = 7.805, \\; m_\\times \\approx 60.3$ 例/周\n"
                            "  [核心反转] 达峰偏差由 88.9% 骤降至 15.5%！\n"
                            "  实证证实多模型集成有效消除均值漂移\n"
                            "• 欧洲 11 国 COVID-19 跨病种验证 ($N = 404$):\n"
                            "  纯事前日度规模 $b = 33.92, \\; m_\\times \\approx 124.7$ 例/天\n"
                            "  证实仿射递减跨病种稳健，拐点具尺度敏感性",
            fontsize=10.5, color=C_TEXT_DARK, va='top', linespacing=1.38)

    # =========================================================================
    # Bottom Banner: Public Health Policy Matrix (Spacious 3-Row Layout)
    # =========================================================================
    draw_box(1.5, 1.5, 97.0, 11.8, C_GREEN_BG, C_GREEN_BD, radius=1.4)
    ax.text(50.0, 10.4, "【公共卫生监测资源两阶段差异化优化配置策略矩阵】", fontsize=14.5, fontweight='bold', color=C_GREEN_TXT, ha='center', va='center')
    ax.text(50.0, 6.9, "• 流行初期 / 低发期 ($m < m_\\times$) ——「全力扩量」: 微观噪声占主导，集中预算扩哨点提覆盖，以 $m_{80\\%}$ 为刚性门槛，迅速跨过平衡点",
            fontsize=11.6, fontweight='bold', color=C_GREEN_TXT, ha='center', va='center')
    ax.text(50.0, 3.9, "• 流行达峰 / 高发期 ($m > m_\\times$) ——「战略提质」: 遭遇不可约环境方差平台与基准失配，停止盲目同质采样，果断转向多模型集成与协变量采集",
            fontsize=11.6, fontweight='bold', color=C_GREEN_TXT, ha='center', va='center')

    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    
    out_pdf = "D:/trae/paper_final/figures/fig0_technical_roadmap.pdf"
    out_png = "D:/trae/paper_final/figures/fig0_technical_roadmap.png"
    plt.savefig(out_pdf, bbox_inches='tight')
    plt.savefig(out_png, bbox_inches='tight', dpi=300)
    plt.close()
    print("Rendered Landscape Ultra-Large-Font technical roadmap successfully:")
    print("  - PDF:", out_pdf)
    print("  - PNG:", out_png)

if __name__ == '__main__':
    draw_landscape_ultra_large_roadmap()
