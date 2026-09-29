# 理论推导：命题、证明与方差交叉点解析（全推导底稿）

本文建立一个分层随机推断框架，严格区分**“当期传播参数 $R_t$ 的测量误差”**与**“跨期基础水平 $\bar{R}$ 的估计误差”**，推导方差占比交叉点 $m_\times$、监测杠杆非对称性与跨期预算权衡，并给出精确增长判定检验与单步预测方差分解。本底稿与论文正文命题 1–6 严格 1:1 对齐。

---

## 1. 基准模型与符号定义

设时间以代（Generation）或离散周 $t$ 推进。
- 上一传播代真实感染者集合规模为 $n$（风险集）。
- 第 $i$ 名感染者在当期产生的继发感染数为 $X_{i,t}$。
- 当期实现的传播强度为 $R_t$。在给定 $R_t$ 条件下，个体继发感染数服从过离散负二项分支分布：
  $$\mathbb{E}[X_{i,t} \mid R_t] = R_t, \qquad \operatorname{Var}(X_{i,t} \mid R_t) = R_t + \frac{R_t^2}{k}, \quad (i = 1, \dots, n)$$
  其中 $k > 0$ 为个体传播离散度参数（$k \to \infty$ 退化为泊松分布，$k$ 越小代表超传播异质性越强）。
- 当期真实新发感染总数为 $I_t = \sum_{i=1}^n X_{i,t}$。
- 观测过程：每个真实感染者以概率 $\rho \in (0, 1]$ 独立被监测系统捕获，当期报告病例数为 $C_t$：
  $$C_t \mid I_t \sim \operatorname{Binomial}(I_t, \rho)$$
- 当 $n$ 与 $\rho$ 已知时，矩估计量为：
  $$\widehat{R}_t = \frac{C_t}{\rho n}$$

---

## 2. 命题 1（当期传播参数的条件似然、Fisher 信息与方差）

在个体继发感染条件独立且服从负二项模型、二项报告率 $\rho$ 固定的基准条件下，当真实风险集 $n$ 与报告率 $\rho$ 已知时：
1. 报告病例数 $C_t$ 在给定 $(n, R_t)$ 下的边缘分布严格服从负二项分布：
   $$C_t \mid n, R_t \sim \operatorname{NB}\!\left(\text{均值} = \rho n R_t, \; \text{形状参数} = nk, \; p^* = \frac{k}{k + \rho R_t}\right)$$
2. 矩估计量 $\widehat{R}_t = \frac{C_t}{\rho n}$ 恰为该条件似然模型下 $R_t$ 的极大似然估计量（MLE）；当观测值 $C_t = 0$ 时，$\widehat{R}_t = 0$ 位于非负参数空间的边界；
3. 在内部参数点 $R_t \in (0, \infty)$ 上，关于 $R_t$ 的 Fisher 信息量为：
   $$\mathcal{I}(R_t \mid n) = \frac{n}{\frac{R_t}{\rho} + \frac{R_t^2}{k}}$$
4. 估计量 $\widehat{R}_t$ 的条件方差严格达到 Cramér–Rao 下界：
   $$\operatorname{Var}\!\left(\frac{C_t}{\rho n} \;\middle|\; n, R_t\right) = \mathcal{I}(R_t \mid n)^{-1} = \frac{R_t}{\rho n} + \frac{R_t^2}{k n}$$

### 证明
由负二项分布的概率生成函数（PGF），若个体继发感染数 $X_{i,t} \sim \operatorname{NB}(k, p)$，其中 $p = \frac{k}{k + R_t}$，则 $I_t = \sum_{i=1}^n X_{i,t} \sim \operatorname{NB}(nk, p)$，其 PGF 为：
$$G_{I_t}(s) = \left(\frac{p}{1 - (1-p)s}\right)^{nk}$$
在二项抽样 $C_t \mid I_t \sim \operatorname{Binomial}(I_t, \rho)$ 下，复合分布的 PGF 为：
$$G_{C_t}(s) = G_{I_t}(1 - \rho + \rho s) = \left(\frac{p}{1 - (1-p)(1 - \rho + \rho s)}\right)^{nk} = \left(\frac{p^*}{1 - (1-p^*)s}\right)^{nk}$$
其中：
$$p^* = \frac{p}{p + \rho(1-p)} = \frac{\frac{k}{k+R_t}}{\frac{k}{k+R_t} + \rho \frac{R_t}{k+R_t}} = \frac{k}{k + \rho R_t}$$
这证明了 $C_t \mid n, R_t \sim \operatorname{NB}(nk, p^*)$，条件均值为 $\rho n R_t$。

其对数似然函数为：
$$\ln L(R_t) = \text{const} - (nk + C_t) \ln(k + \rho R_t) + C_t \ln R_t$$
对 $R_t$ 求导并令得分为零：
$$\frac{\partial \ln L}{\partial R_t} = -\frac{\rho(nk + C_t)}{k + \rho R_t} + \frac{C_t}{R_t} = \frac{k(C_t - \rho n R_t)}{R_t(k + \rho R_t)} = 0 \implies \widehat{R}_t^{\text{MLE}} = \frac{C_t}{\rho n}$$
计算得分函数的方差以求 Fisher 信息量：
$$\mathcal{I}(R_t \mid n) = \operatorname{Var}\left(\frac{\partial \ln L}{\partial R_t}\right) = \frac{k^2 \operatorname{Var}(C_t \mid n, R_t)}{R_t^2(k + \rho R_t)^2}$$
代入负二项方差 $\operatorname{Var}(C_t \mid n, R_t) = \rho n R_t + \frac{\rho^2 n R_t^2}{k} = \frac{\rho n R_t(k + \rho R_t)}{k}$：
$$\mathcal{I}(R_t \mid n) = \frac{k^2 \cdot \frac{\rho n R_t(k + \rho R_t)}{k}}{R_t^2(k + \rho R_t)^2} = \frac{k \rho n R_t}{R_t^2(k + \rho R_t)} = \frac{n}{\frac{R_t}{\rho} + \frac{R_t^2}{k}}$$
其倒数恰为 $\operatorname{Var}(\widehat{R}_t \mid n, R_t) = \frac{R_t}{\rho n} + \frac{R_t^2}{kn}$，严格达到 Cramér–Rao 下界。 $\blacksquare$

---

## 3. 命题 2（跨期基础水平的单期边际方差）与定义 1（方差交叉点）

在条件矩假设 $\mathbb{E}[R_t \mid n] = \bar{R}, \operatorname{Var}(R_t \mid n) = v_R > 0$ 下，若使用单期估计量 $\frac{C_t}{\rho n}$ 估计跨期基础水平 $\bar{R}$，其给定风险集 $n$ 的条件边际方差为：
$$\operatorname{Var}\!\left(\frac{C_t}{\rho n} \;\middle|\; n\right) = v_R + \frac{\bar{R}}{\rho n} + \frac{\bar{R}^2 + v_R}{k n}$$

### 证明
应用全方差公式以 $\bar{R}$ 为目标分解：
$$\operatorname{Var}\!\left(\frac{C_t}{\rho n} \;\middle|\; n\right) = \operatorname{Var}\left(\mathbb{E}\left[\frac{C_t}{\rho n} \;\middle|\; n, R_t\right] \;\middle|\; n\right) + \mathbb{E}\left[\operatorname{Var}\left(\frac{C_t}{\rho n} \;\middle|\; n, R_t\right) \;\middle|\; n\right]$$
由命题 1，第一项为 $\operatorname{Var}(R_t \mid n) = v_R$。第二项为：
$$\mathbb{E}\left[\frac{R_t}{\rho n} + \frac{R_t^2}{k n} \;\middle|\; n\right] = \frac{\mathbb{E}[R_t \mid n]}{\rho n} + \frac{\mathbb{E}[R_t^2 \mid n]}{k n}$$
利用条件二阶矩关系 $\mathbb{E}[R_t^2 \mid n] = \operatorname{Var}(R_t \mid n) + (\mathbb{E}[R_t \mid n])^2 = v_R + \bar{R}^2$，相加即得：
$$\operatorname{Var}\!\left(\frac{C_t}{\rho n} \;\middle|\; n\right) = v_R + \frac{\bar{R}}{\rho n} + \frac{\bar{R}^2 + v_R}{k n} \quad \blacksquare$$

### 定义 1（方差占比交叉点）
令 $m = \rho n$ 为上一代风险集对应的期望被报告人数。方差式可重写为 $v_R + A/m$，其中 $A = \bar{R} + \rho(\bar{R}^2 + v_R)/k$。定义规模项 $A/m$ 与环境项 $v_R$ 相等的期望规模为交叉点：
$$m_\times \triangleq \frac{A}{v_R} = \frac{\bar{R} + \rho(\bar{R}^2 + v_R)/k}{v_R}$$
此时单期估计方差中环境随机性占比恰为 50%（信度比为 0.5）。

---

## 4. 命题 3（监测杠杆的非对称性与超传播方差下界）

将单期方差写作 $(n, \rho)$ 的二元函数：
$$V(n, \rho) = v_R + \frac{\bar{R}}{\rho n} + \frac{\bar{R}^2 + v_R}{k n}$$
将第二项恒等拆解为计数方差与漏报抽稀方差：$\frac{\bar{R}}{\rho n} = \frac{\bar{R}}{n} + \frac{(1-\rho)\bar{R}}{\rho n}$。
1. **报告率杠杆的饱和下界：** 给定任意有限风险集 $n < \infty$，当 $\rho \to 1$ 时：
   $$\lim_{\rho \to 1} V(n, \rho) = v_R + \frac{\bar{R}}{n} + \frac{\bar{R}^2 + v_R}{k n} > v_R$$
   提高报告率只能消除抽稀方差，无法消除完全报告时的计数波动 $\frac{\bar{R}}{n}$ 与超传播内在抽样方差 $\frac{\bar{R}^2+v_R}{kn}$。
2. **样本基数杠杆的全域收敛性：** 无论报告率 $\rho \in (0, 1]$ 为何，扩大基数至极限：
   $$\lim_{n \to \infty} V(n, \rho) = v_R$$
   唯有扩大感染基数才能使两项方差同时衰减至环境底板。

### 证明
直接代入极限即得。 $\blacksquare$

---

## 5. 命题 4（预算约束下的监测设计权衡与可行性集合）

设在 $T$ 个观测期内总期望被报告风险集人数受限为 $B = T \cdot m$（每期 $m = \rho n_T$）：
1. 若各期环境扰动跨期独立，平均估计量 $\overline{\widehat{R}}_T = \frac{1}{T}\sum_{t=1}^T \widehat{R}_t$ 的方差为：
   $$\operatorname{Var}(\overline{\widehat{R}}_T \mid n_T) = \frac{v_R}{T} + \frac{A}{B}$$
   总预算 $B$ 固定时，拉长独立期数 $T$ 严格单调削减估计方差。
2. 若各期环境扰动存在一阶自回归自相关 $\operatorname{Cov}(R_t, R_{t+s} \mid n_T) = v_R r^{|s|}$（$0 \le r < 1$），则有限期 $T$ 下的精确方差为：
   $$\operatorname{Var}(\overline{\widehat{R}}_T \mid n_T) = \frac{v_R}{T}\left[\frac{1+r}{1-r} - \frac{2r(1-r^T)}{T(1-r)^2}\right] + \frac{A}{B}$$
   大期数极限下有效独立期数近似为 $T_{\operatorname{eff}}(T, r) \triangleq T \frac{1-r}{1+r}$。
3. **离散可行设计集合：** 要求各期风险集相同且为正整数（$n_T \in \mathbb{N}_+$）并精确用尽预算时，可行集合为：
   $$\mathcal{T}(B, \rho) \triangleq \left\{ T \in \mathbb{N}_+ \;:\; \frac{B}{\rho T} \in \mathbb{N}_+ \right\}$$

### 证明
由全方差公式，给定环境序列后分支与抽样过程条件独立：
$$\operatorname{Var}(\overline{\widehat{R}}_T \mid n_T) = \frac{1}{T^2}\operatorname{Var}\left(\sum_{t=1}^T R_t \;\middle|\; n_T\right) + \frac{1}{T^2}\sum_{t=1}^T \mathbb{E}\big[\operatorname{Var}(\widehat{R}_t \mid n_T, R_t) \;\big|\; n_T\big]$$
第二项为 $\frac{A}{T(\rho n_T)} = \frac{A}{B}$（因 $\rho n_T = B/T$）。独立假设下第一项为 $v_R/T$。
若存在 AR(1) 自相关，利用平稳协方差双重求和展开：
$$\operatorname{Var}\left(\sum_{t=1}^T R_t \;\middle|\; n_T\right) = T v_R + 2 v_R \sum_{s=1}^{T-1} (T-s) r^s = v_R T \left[\frac{1+r}{1-r} - \frac{2r(1-r^T)}{T(1-r)^2}\right]$$
除以 $T^2$ 即得式 (2)。当 $T \gg 1$ 时忽略 $O(1/T^2)$ 项直接得到 $T_{\operatorname{eff}}$。正整数约束 $n_T = B/(\rho T) \in \mathbb{N}_+$ 即给出集合 $\mathcal{T}(B, \rho)$。 $\blacksquare$

### 推论 1（成本与预算约束下的最优监测规模）
设监测系统在每个观测期存在固定的系统维持成本 $c_0 > 0$，每捕获上报一个病例的边际成本为 $c_1 > 0$。在总成本预算 $C = T(c_0 + c_1 m)$ 约束下，设计者寻求期数 $T$ 与单期期望报告规模 $m$ 的最优组合以最小化跨期估计方差 $\operatorname{Var}(\overline{\widehat{R}}_T) = \frac{v_R}{T} + \frac{A}{T m}$。
代入 $T = \frac{C}{c_0 + c_1 m}$，目标函数化为：
$$\min_{m > 0} \; \mathcal{V}(m) \propto (c_0 + c_1 m)\left(v_R + \frac{A}{m}\right) = c_0 v_R + c_1 A + \frac{c_0 A}{m} + c_1 v_R m$$
对其求导并令一阶导为零：
$$\frac{\mathrm{d}\mathcal{V}}{\mathrm{d}m} = -\frac{c_0 A}{m^2} + c_1 v_R = 0 \implies m^* = \sqrt{\frac{c_0}{c_1} \cdot \frac{A}{v_R}} = \sqrt{\frac{c_0}{c_1} m_\times}$$
二阶导数 $\frac{\mathrm{d}^2\mathcal{V}}{\mathrm{d}m^2} = \frac{2 c_0 A}{m^3} > 0$ 恒正，证明 $m^*$ 为全局唯一最优规模。
**经济学与监测含义：** 最优单期报告规模恰为“固定成本与边际成本之比”与“方差交叉点 $m_\times$”的几何平均数！当且仅当固定成本与边际成本之比等于方差交叉点（$c_0/c_1 = m_\times$）时，$m^* = m_\times$。这证明了方差交叉点 $m_\times$ 并非主观约定，而是监测设计与运筹优化决策中的基本充分统计量（Sufficient Statistic），从决策论层面严格界定了标题中的“推断边界”。 $\blacksquare$

---

## 6. 命题 5（当期超临界增长判定检验与精确离散功效）

针对单侧检验假设 $H_0: R_t \le 1 \quad \text{vs} \quad H_1: R_t > 1$：
1. 负二项分布族关于充分统计量 $C_t$ 具有单调似然比（MLR）性质；采用拒绝域 $\{C_t \ge c_\alpha\}$ 的非随机化上尾检验，在复合原假设 $H_0: R_t \le 1$ 下严格控制第一类错误率低于 $\alpha$，离散临界值为：
   $$c_\alpha = \min \left\{ c \in \mathbb{N} \;:\; \Pr_{R_t = 1}(C_t \ge c) \le \alpha \right\}$$
2. 对于任意备择强度 $R_t = 1 + \delta$（$\delta > 0$），理论检出功效精确为：
   $$\pi(n, \delta) \triangleq \Pr_{R_t = 1 + \delta}(C_t \ge c_\alpha) = 1 - F_{\operatorname{NB}}\!\left(c_\alpha - 1; \; nk, \; \frac{k}{k + \rho(1+\delta)}\right)$$

### 证明
（i）给定 $(n, \rho, k)$，$C_t$ 服从形状参数 $nk$、成功概率 $p^*(R_t) = \frac{k}{k + \rho R_t}$ 的负二项分布。其概率质量函数为：
$$\Pr(C_t = j \mid R_t) = \frac{\Gamma(j + nk)}{j! \Gamma(nk)} (p^*)^{nk} (1 - p^*)^j$$
对任意 $R_t' > R_t$，考虑似然比：
$$\frac{\Pr(C_t = j \mid R_t')}{\Pr(C_t = j \mid R_t)} = \left(\frac{p^*(R_t')}{p^*(R_t)}\right)^{nk} \left(\frac{1 - p^*(R_t')}{1 - p^*(R_t)}\right)^j$$
由于 $p^*(R_t)$ 关于 $R_t$ 严格单调递减，故 $1 - p^*(R_t') > 1 - p^*(R_t)$，从而底数 $\frac{1 - p^*(R_t')}{1 - p^*(R_t)} > 1$。因此，似然比关于充分统计量 $j$ 严格单调递增，证明了该分布族具有单调似然比性质。
由经典的单调似然比检验理论（Karlin–Rubin 定理），上尾检验统计量 $C_t \ge c_\alpha$ 的拒绝概率 $\Pr_{R_t}(C_t \ge c_\alpha)$ 关于参数 $R_t$ 严格单调递增。因此：
$$\sup_{R_t \le 1} \Pr_{R_t}(C_t \ge c_\alpha) = \Pr_{R_t = 1}(C_t \ge c_\alpha) \le \alpha$$
上确界严格在边界点 $R_t = 1$ 取到，且由 $c_\alpha$ 的定义严格受控于 $\alpha$ 以下。
（ii）在备择假设 $R_t = 1 + \delta$ 下，直接应用累积分布补集定义即得功效公式 $\pi(n, \delta) = 1 - F_{\operatorname{NB}}(c_\alpha - 1; nk, p^*(1+\delta))$。需特别指明：离散临界值 $c_\alpha$ 随 $n$ 离散跳变，使得功效函数 $\pi(n, \delta)$ 作为 $n$ 的函数呈现阶梯锯齿状非单调性，因此求解达到目标功效的最小样本量时必须逐点枚举，不能简单二分搜索。 $\blacksquare$

---

## 7. 命题 6（真实感染与报告病例的单步预测方差分解）

基于报告信息集 $\mathcal{F}_t^C$，未来真实感染数 $I_{t+1}$ 的预测方差严格满足：
$$\operatorname{Var}(I_{t+1} \mid \mathcal{F}_t^C) = \operatorname{Var}\big(\Lambda_{t+1} R_{t+1} \;\big|\; \mathcal{F}_t^C\big) + \mathbb{E}\Big[\operatorname{Var}\big(I_{t+1} \;\big|\; \Lambda_{t+1}, R_{t+1}, \mathcal{F}_t^C\big) \;\Big|\; \mathcal{F}_t^C\Big]$$
在二项抽样观测下，未来报告病例数 $C_{t+1}$ 的预测方差严格给出为：
$$\operatorname{Var}(C_{t+1} \mid \mathcal{F}_t^C) = \rho(1 - \rho)\,\mathbb{E}[I_{t+1} \mid \mathcal{F}_t^C] + \rho^2 \operatorname{Var}(I_{t+1} \mid \mathcal{F}_t^C)$$

### 证明
对 $I_{t+1}$ 以 $(\Lambda_{t+1}, R_{t+1})$ 为条件应用全方差公式直接即得式 (1)。
对 $C_{t+1}$ 以 $I_{t+1}$ 为条件应用全方差公式：
$$\operatorname{Var}(C_{t+1} \mid \mathcal{F}_t^C) = \mathbb{E}[\operatorname{Var}(C_{t+1} \mid I_{t+1}, \mathcal{F}_t^C) \mid \mathcal{F}_t^C] + \operatorname{Var}(\mathbb{E}[C_{t+1} \mid I_{t+1}, \mathcal{F}_t^C] \mid \mathcal{F}_t^C)$$
由二项抽样条件独立假定 $C_{t+1} \mid I_{t+1} \sim \operatorname{Binomial}(I_{t+1}, \rho)$，有：
$$\operatorname{Var}(C_{t+1} \mid I_{t+1}, \mathcal{F}_t^C) = \rho(1 - \rho) I_{t+1}, \qquad \mathbb{E}[C_{t+1} \mid I_{t+1}, \mathcal{F}_t^C] = \rho I_{t+1}$$
代入即得式 (2)。 $\blacksquare$
