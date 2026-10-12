# -*- coding: utf-8 -*-
"""
Generate Publication-Quality Large-Font Technical Roadmap / Architecture Diagram (fig0_technical_roadmap)
Outputs both PDF (vector) and PNG (300 DPI) for paper/main.tex, thesis_main.tex, and defense PPT.

Redesigned with:
- Extra-large readable fonts (11pt - 18pt, readable even when scaled down)
- Concise keywords & mathematical formulas instead of dense paragraphs
- High contrast cards and clear directional pipeline
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_large_font_roadmap():
    # Width 14.5 inch, Height 17.5 inch for optimal proportion and large font rendering
    fig_w, fig_h = 14.5, 17.5
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=300)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

    # Academic Palette
    C_LAYER_BG  = '#F8FAFC' # Slate 50
    C_LAYER_BD  = '#94A3B8' # Slate 400
    C_CARD_BG   = '#FFFFFF'
    C_CARD_BD   = '#64748B' # Slate 500
    C_NAVY      = '#0F2744' # Deep Oxford Navy
    C_BLUE_DARK = '#1E3A8A' # Blue 900
    C_BLUE_MID  = '#2563EB' # Blue 600
    C_BLUE_LT   = '#EFF6FF' # Blue 50
    C_BLUE_BD   = '#93C5FD' # Blue 300
    C_AMBER_LT  = '#FFFBEB' # Amber 50
    C_AMBER_BD  = '#FCD34D' # Amber 300
    C_GREEN_BG  = '#F0FDF4' # Emerald 50
    C_GREEN_BD  = '#86EFAC' # Emerald 300
    C_GREEN_TXT = '#14532D' # Emerald 900
    C_TEXT_DARK = '#0F172A' # Slate 900
    C_TAG_BLUE  = '#DBEAFE' # Blue 100
    C_TAG_AMBER = '#FEF3C7' # Amber 100

    def draw_box(x, y, w, h, fill_color, border_color, border_width=1.2, radius=1.4, zorder=1):
        box = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle=f"round,pad=0.25,rounding_size={radius}",
            fc=fill_color, ec=border_color, lw=border_width,
            zorder=zorder
        )
        ax.add_patch(box)
        return box

    def draw_arrow(x1, y1, x2, y2, label="", color='#2563EB', lw=2.0):
        ax.annotate(
            '', xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=18),
            zorder=5
        )
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mx, my, label, fontsize=11, fontweight='bold', color=color,
                    ha='center', va='center', bbox=dict(boxstyle="round,pad=0.3", fc='#FFFFFF', ec=color, lw=1.0),
                    zorder=6)

    # =========================================================================
    # Header Banner (Large Font)
    # =========================================================================
    draw_box(2, 93.8, 96, 5.2, C_NAVY, C_NAVY, radius=1.2)
    ax.text(50, 96.9, "全文研究技术路线与理论推断全景架构图", fontsize=18, fontweight='bold', color='#FFFFFF', ha='center', va='center')
    ax.text(50, 94.8, "End-to-End Methodological Architecture: Inputs, Branching Dynamics, Asymptotic Limits & Empirical Falsification",
            fontsize=10.5, color='#94A3B8', ha='center', va='center')

    # =========================================================================
    # Layer 1: Inputs (Large Fonts)
    # =========================================================================
    draw_box(2, 79.2, 96, 13.5, C_LAYER_BG, C_LAYER_BD, radius=1.4)
    ax.text(4, 90.8, "层级 I · 多源已知输入层 (Known Inputs & Observation Stream)", fontsize=13, fontweight='bold', color=C_BLUE_DARK, ha='left')

    w3 = 30.0
    # Input 1: Observations
    draw_box(4, 80.2, w3, 9.4, C_CARD_BG, C_CARD_BD)
    ax.text(19.0, 87.8, "① 真实观测流 (Observed)", fontsize=11.5, fontweight='bold', color=C_NAVY, ha='center')
    ax.text(5.5, 85.0, "• 周报告住院数:  C_t ∈ N\n"
                       "• 机构覆盖率:  报告率 ρ 宏观代理\n"
                       "• 历史暴露压力:  D_t = ∑ w_s C_{t+1-s}",
            fontsize=10.2, color=C_TEXT_DARK, va='top', linespacing=1.45)

    # Input 2: Parameters
    draw_box(35.0, 80.2, w3, 9.4, C_CARD_BG, C_CARD_BD)
    ax.text(50.0, 87.8, "② 生物学先验 (Parameters)", fontsize=11.5, fontweight='bold', color=C_NAVY, ha='center')
    ax.text(36.5, 85.0, "• 超传播离散度:  k (流感 0.35, COVID 0.1~0.3)\n"
                        "• 哨点报告率:  ρ ∈ [0.0056, 0.0210]\n"
                        "• 宏观环境矩:  (R_base, v_R, r)\n"
                        "• 代际时滞核:  w = (0.65, 0.25, 0.10) (10.2天)",
            fontsize=10.2, color=C_TEXT_DARK, va='top', linespacing=1.45)

    # Input 3: Constraints
    draw_box(66.0, 80.2, w3, 9.4, C_CARD_BG, C_CARD_BD)
    ax.text(81.0, 87.8, "③ 运筹与成本红线 (Budget)", fontsize=11.5, fontweight='bold', color=C_NAVY, ha='center')
    ax.text(67.5, 85.0, "• 检验水平红线:  α = 0.05\n"
                        "• 单期固定成本:  c_0 > 0 (哨点运维维持)\n"
                        "• 边际检测成本:  c_1 > 0 (单例耗材成本)\n"
                        "• 总经费约束:  B_cost = T(c_0 + c_1 m)",
            fontsize=10.2, color=C_TEXT_DARK, va='top', linespacing=1.45)

    draw_arrow(50, 79.2, 50, 75.8, label="构建两阶段分层随机生成过程")

    # =========================================================================
    # Layer 2: Mechanisms & Fluid Limit
    # =========================================================================
    draw_box(2, 61.8, 96, 13.0, C_LAYER_BG, C_LAYER_BD, radius=1.4)
    ax.text(4, 73.2, "层级 II · 微观分支机制与动力学映射 (Data-Generating Process & Fluid Limit)", fontsize=13, fontweight='bold', color=C_BLUE_DARK, ha='left')

    w2 = 45.4
    # Card 2.1: Micro mechanism
    draw_box(4, 62.8, w2, 9.2, C_CARD_BG, C_CARD_BD)
    ax.text(26.7, 70.3, "微观负二项分支与二项抽稀封闭定理", fontsize=11.5, fontweight='bold', color=C_NAVY, ha='center')
    ax.text(5.5, 68.0, "• 微观分支层:  个体传染力 ν ~ Gamma(k, R_t/k)\n"
                       "  欧拉换元积分闭式导出:  Y ~ NB(k, p),  p = k / (k + R_t)\n"
                       "  [物理顿悟] 掷硬币模型中传人是失败、终止是成功！病毒越强终止概率越低\n"
                       "• 宏观抽稀封闭:  G_C(s) = G_I(G_B(s))  ==>  C_t ~ NB(nk,  k / (k + ρ R_t))",
            fontsize=10.0, color=C_TEXT_DARK, va='top', linespacing=1.4)

    # Card 2.2: Kurtz Fluid Limit
    draw_box(50.6, 62.8, w2, 9.2, C_BLUE_LT, C_BLUE_BD)
    ax.text(73.3, 70.3, "动力学桥梁: Kurtz 密度相关流体极限大数定理", fontsize=11.5, fontweight='bold', color=C_BLUE_DARK, ha='center')
    ax.text(52.1, 68.0, "• 确定性仓室 ODE 映射: 经典 Kermack-McKendrick SIR 系统 dI/dt = (β - γ)I\n"
                       "  无病平衡点特征值 λ = γ(R_0 - 1)，在 R_0 = 1 处发生跨临界分岔\n"
                       "• 纯跳跃生灭半鞅分解: I_N(t)/N = I_N(0)/N + ∫ (βsu - γu) du + M_N(t)\n"
                       "• Kurtz (1970) 定理: 当风险集 n -> ∞ 时随机路径依概率 1 弱收敛于 ODE 均值流形\n"
                       "  [理论定位] ODE 刻画大数均值轨道；本文研究有限样本偏离轨道的方差标度律！",
            fontsize=9.8, color=C_TEXT_DARK, va='top', linespacing=1.4)

    draw_arrow(50, 61.8, 50, 58.4, label="推断目标分化 · 全方差公式正交展开")

    # =========================================================================
    # Layer 3: Asymptotic Theory (Target A vs Target B)
    # =========================================================================
    draw_box(2, 44.0, 96, 13.5, C_LAYER_BG, C_LAYER_BD, radius=1.4)
    ax.text(4, 55.8, "层级 III · 推断目标分化与渐近方差理论 (Asymptotic Variance Theory)", fontsize=13, fontweight='bold', color=C_BLUE_DARK, ha='left')

    # Target A
    draw_box(4, 45.0, 42.0, 9.6, C_CARD_BG, C_CARD_BD)
    ax.text(25.0, 53.0, "目标 A: 瞬态再生数 R_t 点估计 (命题 1)", fontsize=11.5, fontweight='bold', color=C_NAVY, ha='center')
    ax.text(5.5, 50.8, "• 矩估计即极大似然:  R_hat_t = C_t / (ρn) = C_t / m\n"
                       "• 塔式法则严格无偏:  E[ R_hat_t | n, R_t ] = R_t\n"
                       "• Fisher 信息双算法验证:  I(R_t) = k n ρ / [ R_t(k + ρ R_t) ]\n"
                       "• 严格达到 Cramér-Rao 下界 (UMVUE):  Var = I^{-1}\n"
                       "• 标度律:  Var = R_t/m + R_t^2/(km) = O(1/m)  [无界单调衰减]",
            fontsize=10.0, color=C_TEXT_DARK, va='top', linespacing=1.4)

    # Target B
    draw_box(47.2, 45.0, 50.8, 9.6, C_AMBER_LT, C_AMBER_BD)
    ax.text(72.6, 53.0, "目标 B: 跨期基础传播基准 R_base 估计 (命题 2 & 3)", fontsize=11.5, fontweight='bold', color=C_NAVY, ha='center')
    ax.text(48.7, 50.8, "• 全方差公式展开:  Var = Var(E[ R_hat_t | R_t ]) + E[ Var(R_hat_t | R_t) ]\n"
                       "• 导出仿射损失结构:  Var = v_R + A/m,  其中 A = R_base + ρ(R_base^2+v_R)/k\n"
                       "• 特征规模平衡点:  m_× ≡ A / v_R  [抽样噪声与环境噪声各占 50% 分水岭]\n"
                       "• 监测杠杆非对称性定理:  lim_{ρ->1} V(n, ρ) > v_R  [提报告率存在无法消除硬下界]\n"
                       "  反之 lim_{n->∞} V(n, ρ) = v_R  [唯有扩大实际基数利用大数定律可彻底逼近底板]",
            fontsize=10.0, color=C_TEXT_DARK, va='top', linespacing=1.4)

    draw_arrow(50, 44.0, 50, 40.6, label="运筹设计优化 · 离散检验与预测机制")

    # =========================================================================
    # Layer 4: Surveillance Design & Simulations
    # =========================================================================
    draw_box(2, 26.2, 96, 13.5, C_LAYER_BG, C_LAYER_BD, radius=1.4)
    ax.text(4, 38.0, "层级 IV · 监测运筹优化与离散机制检验 (Surveillance Design & Simulations)", fontsize=13, fontweight='bold', color=C_BLUE_DARK, ha='left')

    # Left: Surveillance Design
    draw_box(4, 27.2, 45.4, 9.6, C_CARD_BG, C_CARD_BD)
    ax.text(26.7, 35.2, "多期抽样设计与 Cochran 抽样对偶 (命题 4 & 推论 1)", fontsize=11.5, fontweight='bold', color=C_NAVY, ha='center')
    ax.text(5.5, 33.0, "• 样本预算恒常性:  总人数 B = Tm 下抽样误差恒为常数 A/B\n"
                       "  结论: 单期狂堆人数无效！唯有拉长期数 T 平滑环境波动 v_R\n"
                       "• AR(1) 错位相减求和:  S = Tr/(1-r) - r(1-r^T)/(1-r)^2  ==>  T_eff ≈ T(1-r)/(1+r)\n"
                       "• 成本约束凸优化:  二阶导 f''(m) = 2c_0 A / (B_cost m^3) > 0  [严格凸函数]\n"
                       "• 最优单期规模闭式解:  m* = sqrt( (c_0/c_1) · m_× )  [Cochran 抽样完全对偶]",
            fontsize=10.0, color=C_TEXT_DARK, va='top', linespacing=1.4)

    # Right: Testing & Renewal
    draw_box(50.6, 27.2, 45.4, 9.6, C_CARD_BG, C_CARD_BD)
    ax.text(73.3, 35.2, "爆发假设检验天花板与更新过程预测偏差 (命题 5 & 6)", fontsize=11.5, fontweight='bold', color=C_NAVY, ha='center')
    ax.text(52.1, 33.0, "• 爆发检验 H_0: R_t ≤ 1:  单调似然比一阶差分 Δ(j) > 0 严格为正\n"
                       "  Karlin-Rubin UMP 检验与临界值阶梯跳跃诱发功效锯齿波 (Sawtooth)\n"
                       "• 检验目标天然天花板:  越过 m_80% 后功效饱和，Wald 正态失真高达 8.1%\n"
                       "• 更新过程预测均方误差式 (29):  E[(G-R_base)^2] = E[σ^2/D^2] + E[(μ/D-R_base)^2]\n"
                       "  双口径厘清: 历史暴露代理必然引入非负预测偏差，实际规模误差严格高于下界",
            fontsize=10.0, color=C_TEXT_DARK, va='top', linespacing=1.4)

    draw_arrow(50, 26.2, 50, 22.8, label="真实大数据计量检验与外部场景验证")

    # =========================================================================
    # Layer 5: Empirical Evidence & Policy Matrix
    # =========================================================================
    draw_box(2, 2.0, 96, 20.0, C_LAYER_BG, C_LAYER_BD, radius=1.4)
    ax.text(4, 20.4, "层级 V · 全美流感住院实证、外部多病种扩展与决策矩阵 (Empirical Evidence & Policy Matrix)", fontsize=13, fontweight='bold', color=C_BLUE_DARK, ha='left')

    w3_e = 30.0
    # Card 5.1: NHSN Main
    draw_box(4, 8.2, w3_e, 11.2, C_CARD_BG, C_CARD_BD)
    ax.text(19.0, 18.0, "全美 NHSN 流感住院大数据主实证", fontsize=11.0, fontweight='bold', color=C_NAVY, ha='center')
    ax.text(5.5, 15.8, "• 样本漏斗与闭环:  16,218 原始记录\n"
                       "  D_t ≥ 5 滤出 N = 10,303 活跃周样本\n"
                       "  三阶段 6009 + 420 + 3874 = 10303 闭环\n"
                       "• FGLS 仿射拟合:  b = 2.2434 (CI [1.50, 3.02])\n"
                       "  1500 次聚类 BS 无一次 ≤ 0 (p < 10^-4)\n"
                       "• 经验平衡点测定:  m_× ≈ 22.6 例/周\n"
                       "• 误差预算份额:  规模项 45%，环境底板 55%",
            fontsize=9.8, color=C_TEXT_DARK, va='top', linespacing=1.4)

    # Card 5.2: Peak Reversal
    draw_box(35.0, 8.2, w3_e, 11.2, C_CARD_BG, C_CARD_BD)
    ax.text(50.0, 18.0, "达峰期 88.9% 偏差反转与空间汇聚", fontsize=11.0, fontweight='bold', color=C_NAVY, ha='center')
    ax.text(36.5, 15.8, "• 达峰期看似恒定误差 0.3 的正交分解:\n"
                       "  Total = ( (R_peak - R_early) / R_early )^2 + Var\n"
                       "  证实整整 88.9% 源于疫情转折的基准漂移！\n"
                       "  剥离后规模项仍显著正 (b = 7.93)，打破失效误读\n"
                       "• 2024 政策冲击:  覆盖率降至 54%，方差激增 192%\n"
                       "• 空间弱相关汇聚:  全国加总方差降至 0.0348",
            fontsize=9.8, color=C_TEXT_DARK, va='top', linespacing=1.4)

    # Card 5.3: External Validation
    draw_box(66.0, 8.2, w3_e, 11.2, C_CARD_BG, C_CARD_BD)
    ax.text(81.0, 18.0, "CDC FluSight 与欧洲 COVID 外验", fontsize=11.0, fontweight='bold', color=C_NAVY, ha='center')
    ax.text(67.5, 15.8, "• FluSight 官方集成预测验证 (N = 1,177):\n"
                       "  纯事前口径 b = 7.8045, m_× ≈ 60.3 例/周\n"
                       "  [核心反转] 达峰偏差由 88.9% 骤降至 15.5%！\n"
                       "  实证证实多模型集成有效校准均值漂移\n"
                       "• 欧洲 11 国 COVID-19 跨病种验证 (N = 404):\n"
                       "  纯事前日度规模 b = 33.92, m_× ≈ 124.7 例/天\n"
                       "  证实仿射递减跨病种稳健，拐点具时间尺度性",
            fontsize=9.8, color=C_TEXT_DARK, va='top', linespacing=1.4)

    # Bottom Policy Matrix Strip (Extra large text)
    draw_box(4, 2.8, 92.0, 4.6, C_GREEN_BG, C_GREEN_BD)
    ax.text(50.0, 6.1, "【公共卫生监测资源两阶段差异化配置策略矩阵】", fontsize=11.5, fontweight='bold', color=C_GREEN_TXT, ha='center')
    ax.text(50.0, 4.2, "• 流行初期 / 低发期 (m < m_×) ——「全力扩量」: 微观噪声主导，集中预算扩哨点提覆盖，以 m_80% 为刚性达标线迅速跨过平衡点\n"
                       "• 流行达峰 / 高发期 (m > m_×) ——「战略提质」: 遭遇不可约环境方差平台与基准失配，停止盲目扩充采样，转向多模型集成与协变量采集",
            fontsize=10.0, fontweight='bold', color=C_GREEN_TXT, ha='center', linespacing=1.35)

    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    
    out_pdf = "D:/trae/paper_final/figures/fig0_technical_roadmap.pdf"
    out_png = "D:/trae/paper_final/figures/fig0_technical_roadmap.png"
    plt.savefig(out_pdf, bbox_inches='tight')
    plt.savefig(out_png, bbox_inches='tight', dpi=300)
    plt.close()
    print("Rendered large-font technical roadmap successfully:")
    print("  - PDF:", out_pdf)
    print("  - PNG:", out_png)

if __name__ == '__main__':
    draw_large_font_roadmap()
