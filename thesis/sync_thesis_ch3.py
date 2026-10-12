# -*- coding: utf-8 -*-
with open(r'D:\trae\thesis_master\chapters\ch3_asymptotic_theory.tex', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add v_R dual identity to §3.1 Target B definition
target_b = r'\Var(R_t \mid n) = v_R > 0.'
replacement_b = (
    r'\Var(R_t \mid n) = v_R > 0.' + '\n\n'
    '这一设定揭示了不可约环境方差 $v_R$ 在两类推断目标下的本质分化：对目标 A 而言，环境波动正是待测对象本身，其跨期变异不构成误差；对目标 B 而言，同一波动退化为不可消除的误差源，单期样本无论多大都无法消除全员共享的单次环境实现。'
)
if target_b in text and '待测对象本身' not in text:
    text = text.replace(target_b, replacement_b, 1)
    print("Thesis Ch3: Added v_R dual identity!")

# 2. Add note on A depending on rho in Definition 3.1
target_crossover = r'm_\times \equiv \frac{A}{v_R} = \frac{\bar{R} + \frac{\rho(\bar{R}^2 + v_R)}{k}}{v_R}. \label{eq:crossover_def}'
addition_a_note = (
    '\n\n\\noindent\\textit{注记：}标量系数 $A \\equiv \\bar{R} + \\frac{\\rho(\\bar{R}^2 + v_R)}{k}$ 自身仍显式依赖于报告率 $\\rho$。因此两个监测系统即使处于相同的 $m = \\rho n$，只要报告率 $\\rho$ 不同，$A$ 与收益拐点 $m_\\times$ 便不相同。$A$ 依赖 $\\rho$ 的方式与依赖规模 $m$ 的反比衰减完全不同，这正是后文命题~\\ref{prop:prop3} 监测杠杆非对称性的数理根源。'
)
if target_crossover in text and '自身仍显式依赖于报告率' not in text:
    text = text.replace(target_crossover, target_crossover + addition_a_note, 1)
    print("Thesis Ch3: Added note on A depending on rho!")

# 3. Compact Prop 4(ii) and move ugly formula to appendix
old_p4_thesis = r'''\item 若各期环境扰动满足一阶自回归协方差 $\Cov(R_t, R_{t+s}) = v_R r^s$（$r \in [0, 1)$），则总方差严格由下式给出：
    \begin{equation}
    \Var(\overline{\widehat{R}}_T) = \frac{v_R}{T}\left[ \frac{1+r}{1-r} - \frac{2r(1-r^T)}{T(1-r)^2} \right] + \frac{A}{B}. \label{eq:ar1_closed_form}
    \end{equation}
    当 $T \gg \frac{1}{1-r}$ 时，有效独立期数退化为 $T_{\mathrm{eff}} \approx T \frac{1-r}{1+r}$。'''

new_p4_thesis = r'''\item 若各期环境扰动满足一阶自回归协方差 $\Cov(R_t, R_{t+s}) = v_R r^s$（$r \in [0, 1)$），在观测跨度远大于自相关特征时长（$T \gg \frac{1}{1-r}$）的渐近条件下，总方差良好近似为有效独立期数折减形式：
    \begin{equation}
    \Var(\overline{\widehat{R}}_T) \approx \frac{v_R}{T_{\mathrm{eff}}} + \frac{A}{B}, \qquad T_{\mathrm{eff}} \approx T \frac{1-r}{1+r}, \label{eq:ar1_closed_form}
    \end{equation}
    有限期数下的精确双重级数求和闭式见附录~\ref{app:sec_prop4_ar1}。'''

if old_p4_thesis in text:
    text = text.replace(old_p4_thesis, new_p4_thesis, 1)
    print("Thesis Ch3: Compacted Prop 4(ii)!")

# 4. Replace profound duality with clean isomorphism in Corollary 1
text = text.replace('形成了深刻对偶', '在数学形式上完全同构')
text = text.replace('达成完美的数学对偶', '在代数形式上完全同构')

with open(r'D:\trae\thesis_master\chapters\ch3_asymptotic_theory.tex', 'w', encoding='utf-8') as f:
    f.write(text)

print("Synchronized Chapter 3 of Thesis successfully!")
