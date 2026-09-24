# 理论推导：命题、证明与方差交叉点解析

本文旨在建立一个条件明确、数学自洽的分层随机框架，清晰界定**“当期传播强度的测量误差”**与**“基础趋势的估计误差”**，推导**方差交叉点 $m_\times$**，并在更新过程与多步预测中给出条件均方误差的准确展开式。

---

## 1. 基准分支模型与符号定义

设时间以代（Generation）或固定离散观测期 $t$ 推进。
- 上一传播代真实感染者集合规模为 $n$（风险集）。
- 第 $i$ 名感染者在当期产生的继发感染数为 $X_{i,t}$。
- 当期实现的传播强度为 $R_t$。在给定 $R_t$ 的条件下，个体继发感染数服从过离散负二项分支分布：
  $$\mathbb{E}[X_{i,t} \mid R_t] = R_t, \qquad \operatorname{Var}(X_{i,t} \mid R_t) = R_t + \frac{R_t^2}{k}, \quad (i = 1, \dots, n)$$
  其中 $k > 0$ 为个体传播离散度参数（$k \to \infty$ 时退化为泊松分布，$k$ 越小代表超传播异质性越强）。
- 当期真实新发感染总数为 $I_t = \sum_{i=1}^n X_{i,t}$。
- 观测过程：每个真实感染者以概率 $\rho \in (0, 1]$ 独立被监测系统捕获，当期报告病例数为 $C_t$：
  $$C_t \mid I_t \sim \operatorname{Binomial}(I_t, \rho)$$
- 当 $n$ 与 $\rho$ 已知时，定义当期传播强度的矩估计量为：
  $$\widehat{R}_t = \frac{C_t}{\rho n}$$

---

## 2. 核心命题与严格证明

### 命题 1（传播与观测复合方差引理）
在上述基准模型下，估计量 $\widehat{R}_t$ 关于当期实现的传播强度 $R_t$ 是条件严格无偏的，其条件方差为：
$$\operatorname{Var}(\widehat{R}_t \mid n, R_t) = \frac{R_t}{\rho n} + \frac{R_t^2}{k n}$$

**证明**：
首先验证无偏性。由全期望定律（Law of Iterated Expectations）：
$$\mathbb{E}[C_t \mid n, R_t] = \mathbb{E}\big[\mathbb{E}[C_t \mid I_t] \mid n, R_t\big] = \mathbb{E}[\rho I_t \mid n, R_t] = \rho \sum_{i=1}^n \mathbb{E}[X_{i,t} \mid R_t] = \rho n R_t$$
因此：
$$\mathbb{E}[\widehat{R}_t \mid n, R_t] = \frac{\mathbb{E}[C_t \mid n, R_t]}{\rho n} = \frac{\rho n R_t}{\rho n} = R_t$$

接着计算条件方差。由全方差公式（Law of Total Variance）：
$$\operatorname{Var}(C_t \mid n, R_t) = \mathbb{E}\big[\operatorname{Var}(C_t \mid I_t) \mid n, R_t\big] + \operatorname{Var}\big(\mathbb{E}[C_t \mid I_t] \mid n, R_t\big)$$

分别计算两项：
1. 二项抽样方差的条件期望：
   $$\operatorname{Var}(C_t \mid I_t) = I_t \rho (1 - \rho)$$
   $$\mathbb{E}\big[\operatorname{Var}(C_t \mid I_t) \mid n, R_t\big] = \rho (1 - \rho) \mathbb{E}[I_t \mid n, R_t] = \rho (1 - \rho) n R_t$$
2. 均值抽样波动的方差：
   $$\mathbb{E}[C_t \mid I_t] = \rho I_t$$
   $$\operatorname{Var}(\rho I_t \mid n, R_t) = \rho^2 \operatorname{Var}(I_t \mid n, R_t) = \rho^2 \sum_{i=1}^n \operatorname{Var}(X_{i,t} \mid R_t) = \rho^2 n \left(R_t + \frac{R_t^2}{k}\right)$$

将两项合并：
$$\begin{aligned}
\operatorname{Var}(C_t \mid n, R_t) &= \rho (1 - \rho) n R_t + \rho^2 n R_t + \frac{\rho^2 n R_t^2}{k} \\
&= \rho n R_t (1 - \rho + \rho) + \frac{\rho^2 n R_t^2}{k} \\
&= \rho n R_t + \frac{\rho^2 n R_t^2}{k}
\end{aligned}$$

代入估计量 $\widehat{R}_t = \frac{C_t}{\rho n}$ 的方差：
$$\operatorname{Var}(\widehat{R}_t \mid n, R_t) = \frac{1}{\rho^2 n^2} \operatorname{Var}(C_t \mid n, R_t) = \frac{\rho n R_t + \rho^2 n R_t^2 / k}{\rho^2 n^2} = \frac{R_t}{\rho n} + \frac{R_t^2}{k n}$$
证毕。 $\blacksquare$

---

### 命题 2（环境随机性与单期基础趋势估计方差）
假设单期共同环境使当期实际实现的传播强度 $R_t$ 在基础水平 $\bar{R}$ 周围波动，满足：
$$\mathbb{E}[R_t] = \bar{R}, \qquad \operatorname{Var}(R_t) = v_R > 0$$
若以单期观测估计基础传播水平 $\bar{R}$，则估计量的边际方差由三部分组成：
$$\operatorname{Var}(\widehat{R}_t \mid n) = v_R + \frac{\bar{R}}{\rho n} + \frac{\bar{R}^2 + v_R}{k n}$$

**证明**：
以 $\bar{R}$ 为目标，应用全方差公式分解：
$$\operatorname{Var}(\widehat{R}_t \mid n) = \operatorname{Var}\big(\mathbb{E}[\widehat{R}_t \mid n, R_t]\big) + \mathbb{E}\big[\operatorname{Var}(\widehat{R}_t \mid n, R_t)\big]$$

由命题 1：
1. 第一项（环境随机方差）：
   $$\mathbb{E}[\widehat{R}_t \mid n, R_t] = R_t \implies \operatorname{Var}\big(\mathbb{E}[\widehat{R}_t \mid n, R_t]\big) = \operatorname{Var}(R_t) = v_R$$
2. 第二项（样本与超传播期望方差）：
   $$\mathbb{E}\big[\operatorname{Var}(\widehat{R}_t \mid n, R_t)\big] = \mathbb{E}\left[ \frac{R_t}{\rho n} + \frac{R_t^2}{k n} \right] = \frac{\mathbb{E}[R_t]}{\rho n} + \frac{\mathbb{E}[R_t^2]}{k n}$$
   注意到二阶矩关系：
   $$\mathbb{E}[R_t^2] = \operatorname{Var}(R_t) + (\mathbb{E}[R_t])^2 = v_R + \bar{R}^2$$
   因此：
   $$\mathbb{E}\big[\operatorname{Var}(\widehat{R}_t \mid n, R_t)\big] = \frac{\bar{R}}{\rho n} + \frac{\bar{R}^2 + v_R}{k n}$$

将两部分相加，即得：
$$\operatorname{Var}(\widehat{R}_t \mid n) = v_R + \frac{\bar{R}}{\rho n} + \frac{\bar{R}^2 + v_R}{k n}$$
证毕。 $\blacksquare$

> **理论意涵对比**：
> - **式 (1) $\operatorname{Var}(\widehat{R}_t \mid n, R_t)$**：衡量的是对**已实现当期传播强度 $R_t$** 的测量误差。当样本量 $n \to \infty$ 时，该方差严格趋于 0。只要样本量不断扩大，对当期实现值的测量精度可以无限提高。
> - **式 (2) $\operatorname{Var}(\widehat{R}_t \mid n)$**：衡量的是用**单期数据估计潜在基础趋势 $\bar{R}$** 的总误差。当样本量 $n \to \infty$ 时，其极限为环境随机方差 $v_R$。无论单期病例数多大，均无法凭借单期数据消除跨周共同环境扰动。

---

### 命题 3（方差交叉点 $m_\times$ 的解析解与比较静态分析）
令 $m = \rho n$ 为上一传播代的**期望报告病例数**。式 (2) 可表示为：
$$\operatorname{Var}(\widehat{R}_t \mid m) = v_R + \frac{A}{m}, \qquad A = \bar{R} + \frac{\rho(\bar{R}^2 + v_R)}{k}$$
当环境方差 $v_R > 0$ 时，定义**方差交叉点（Variance Crossover Point）** $m_\times$ 为“病例数相关方差项与共同环境方差项相等时的期望报告病例规模”：
$$m_\times \triangleq \frac{A}{v_R} = \frac{\bar{R}}{v_R} + \frac{\rho(\bar{R}^2 + v_R)}{k v_R}$$

其对应的期望真实感染者交叉点规模为 $n_\times = m_\times / \rho$：
$$n_\times = \frac{\bar{R}}{\rho v_R} + \frac{\bar{R}^2 + v_R}{k v_R}$$

**比较静态性质（Comparative Statics）**：
1. **个体超传播异质性 $k$ 的影响**：
   $$\frac{\partial m_\times}{\partial k} = -\frac{\rho(\bar{R}^2 + v_R)}{k^2 v_R} < 0$$
   个体过离散度越高（$k$ 越小），方差交叉点 $m_\times$ 越高。这表明在超传播严重的疾病中，需要更大的病例规模才能将计数波动压低到环境噪声水平。
2. **报告率 $\rho$ 的影响**：
   - 观测尺度下：$\frac{\partial m_\times}{\partial \rho} = \frac{\bar{R}^2 + v_R}{k v_R} > 0$。
   - 真实感染尺度下：$\frac{\partial n_\times}{\partial \rho} = -\frac{\bar{R}}{\rho^2 v_R} < 0$。
   当漏报严重（$\rho \to 0$）时，所需真实感染者基数 $n_\times$ 随 $1/\rho$ 剧烈发散。
3. **环境扰动方差 $v_R$ 的影响**：
   $$\frac{\partial m_\times}{\partial v_R} = -\frac{\bar{R}}{v_R^2} - \frac{\rho \bar{R}^2}{k v_R^2} < 0$$
   外部环境扰动越剧烈（$v_R$ 越大），交叉点 $m_\times$ 反而越小。原因在于：在高度动荡的环境中，较小的病例数就已经使测量误差低于环境波动，此时继续收集当期病例对推断基础趋势的边际改善极早饱和。

> **澄清声明**：$m_\times$ 绝非所谓“最低可用病例数”，亦非“超过后收集病例完全无用”的截断门槛。它标志着**误差控制的主导权转移**：当 $m < m_\times$ 时，扩大病例数是削减估计方差的最主要杠杆；当 $m > m_\times$ 时，环境波动成为主要误差来源，增加样本量的边际收益明显放缓。

---

### 命题 4（更新过程推广与多周前瞻预测误差条件方差恒等式）
在现实监测中，感染具有跨周代际分布。设离散感染间隔分布权重为 $\{w_s\}_{s=1}^S$（$\sum_{s=1}^S w_s = 1$），第 $t$ 周的有效感染压力定义为：
$$\Lambda_t = \sum_{s=1}^S w_s I_{t-s}$$
真实新发感染满足：
$$\mathbb{E}[I_t \mid \mathcal{F}_{t-1}, R_t] = R_t \Lambda_t$$
报告病例满足 $C_t \mid I_t, \rho_t \sim \operatorname{Binomial}(I_t, \rho_t)$。

考虑前瞻预测目标 $Y_{t+h}$（如第 $t+h$ 周的最终报告病例数或住院数）。基于第 $t$ 周可用信息集 $\mathcal{F}_t$ 的条件期望预测器 $\widehat{Y}_{t+h \mid t} = \mathbb{E}[Y_{t+h} \mid \mathcal{F}_t]$，其条件均方误差严格满足恒等式：
$$\operatorname{MSE}(h \mid \mathcal{F}_t) \triangleq \mathbb{E}\big[\big(Y_{t+h} - \widehat{Y}_{t+h \mid t}\big)^2 \mid \mathcal{F}_t\big] = \operatorname{Var}(Y_{t+h} \mid \mathcal{F}_t)$$

**多步方差递归展开与非正交协方差项**：
由鞅差分解（Martingale Difference Decomposition）：
$$Y_{t+h} - \mathbb{E}[Y_{t+h} \mid \mathcal{F}_t] = \sum_{j=1}^h D_{t+j}^{(h)}$$
其中鞅差序列为：
$$D_{t+j}^{(h)} \triangleq \mathbb{E}[Y_{t+h} \mid \mathcal{F}_{t+j}] - \mathbb{E}[Y_{t+h} \mid \mathcal{F}_{t+j-1}]$$
根据鞅性质，不同时刻的创新项 $\{D_{t+j}^{(h)}\}_{j=1}^h$ 之间互不相关（条件协方差为零），因此：
$$\operatorname{Var}(Y_{t+h} \mid \mathcal{F}_t) = \sum_{j=1}^h \mathbb{E}\Big[ \operatorname{Var}\big( \mathbb{E}[Y_{t+h} \mid \mathcal{F}_{t+j}] \mid \mathcal{F}_{t+j-1} \big) \;\Big|\; \mathcal{F}_t \Big]$$

对于每一期 $t+j$ 的一步更新：
$$I_{t+j} = R_{t+j} \Lambda_{t+j} + \xi_{t+j}, \qquad \mathbb{E}[\xi_{t+j} \mid \mathcal{F}_{t+j-1}, R_{t+j}] = 0$$
$$R_{t+j} = \bar{R}_{t+j} + \eta_{t+j}, \qquad \mathbb{E}[\eta_{t+j} \mid \mathcal{F}_{t+j-1}] = 0, \quad \operatorname{Var}(\eta_{t+j}) = v_R$$
将其代入感染压力递归关系中：
$$\Lambda_{t+j} = w_1 I_{t+j-1} + \sum_{s=2}^S w_s I_{t+j-s}$$
可见：未来周的感染压力 $\Lambda_{t+j}$ 与未来传播强度 $R_{t+j-1}$ 及分支噪声 $\xi_{t+j-1}$ 存在**内生自回归耦合**。

因此，单步预测误差项展开为：
$$\begin{aligned}
\operatorname{Var}(I_{t+1} \mid \mathcal{F}_t) &= \operatorname{Var}\big((\bar{R}_{t+1} + \eta_{t+1}) \Lambda_{t+1} + \xi_{t+1} \mid \mathcal{F}_t\big) \\
&= \Lambda_{t+1}^2 \operatorname{Var}(\bar{R}_{t+1} \mid \mathcal{F}_t) + \Lambda_{t+1}^2 v_R + \mathbb{E}[\operatorname{Var}(\xi_{t+1} \mid R_{t+1}, \Lambda_{t+1}) \mid \mathcal{F}_t] \\
&\quad + 2 \Lambda_{t+1} \operatorname{Cov}\big(\bar{R}_{t+1}, \eta_{t+1} \mid \mathcal{F}_t\big)
\end{aligned}$$

> **证明结论与方法学约束**：
> 1. 只有在假定基础趋势无不确定性（$\operatorname{Var}(\bar{R}) = 0$）、环境扰动无自相关且与分支噪声严格条件独立的强假设下，单步方差才能线性相加；
> 2. 对于多步外推（$h \ge 2$），由于自回归权重 $w_s$ 将前一步的随机波动直接卷入下一步的风险集 $\Lambda_{t+j}$，各期误差呈现**乘性复合放大**，因此**无法分解为普适无交叠的“四项独立预算”**。论文必须从全条件方差式 (5) 出发，并如实保留自回归路径上的复合影响。
