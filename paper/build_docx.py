# -*- coding: utf-8 -*-
"""按《论文初稿(修改5).docx》的学报模板，把流感监测论文重写为 docx。

通过生成 officecli batch JSON 一次写入：标题/摘要/关键词/0引言/…/6结论/参考文献，
公式用 OMML（officecli equation），表用 table，图用 figures/ 下的 PNG。
"""
import json, os

import os
BASE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(BASE, '..', 'figures')
OUT = os.path.join(BASE, 'main_docx.docx')

cmds = []

def p(text, style=None, size=None, bold=None, align=None, before=None, after=None,
      first=None, italic=None, pagebreak=None):
    props = {'text': text}
    if style: props['style'] = style
    if size: props['size'] = size
    if bold is not None: props['bold'] = bold
    if align: props['align'] = align
    if before: props['spaceBefore'] = before
    if after: props['spaceAfter'] = after
    if first: props['firstLineIndent'] = first
    if italic is not None: props['italic'] = italic
    if pagebreak: props['pageBreakBefore'] = True
    cmds.append({'command': 'add', 'parent': '/body', 'type': 'paragraph', 'props': props})

def h1(t):   # 一级标题：0引言 / 1研究回顾 / ...
    p(t, style='Heading1', size='16pt', bold=True, before='13pt', after='13pt')
def h2(t):
    p(t, style='Heading2', size='14pt', bold=True, before='12pt', after='6pt')

def body(t):
    p(t, size='10.5pt', first='420', after='0pt', line=None) if False else \
    p(t, size='10.5pt', first='420')

def eq(latex):
    cmds.append({'command': 'add', 'parent': '/body', 'type': 'equation',
                 'props': {'formula': latex}})

def fig(png, cap, width='5.9in'):
    cmds.append({'command': 'add', 'parent': '/body', 'type': 'paragraph',
                 'props': {'align': 'center'}})
    cmds.append({'command': 'add',
                 'parent': '/body/p[last()]', 'type': 'picture',
                 'props': {'src': os.path.join(FIG, png), 'width': width,
                           'alt': cap}})
    p(cap, size='9pt', bold=True, align='center', before='3pt', after='10pt')

def table(headers, rows, cap):
    p(cap, size='9pt', bold=True, align='center', before='8pt', after='3pt')
    cmds.append({'command': 'add', 'parent': '/body', 'type': 'table',
                 'props': {'rows': len(rows) + 1, 'cols': len(headers),
                           'width': '100%'}})
    cmds.append({'command': 'set', 'path': '/body/tbl[last()]/tr[1]',
                 'props': dict([('header', 'true')] +
                               [('c%d' % (i + 1), h) for i, h in enumerate(headers)])})
    for r, row in enumerate(rows, start=2):
        cmds.append({'command': 'set', 'path': '/body/tbl[last()]/tr[%d]' % r,
                     'props': dict([('c%d' % (i + 1), v) for i, v in enumerate(row)])})

# ============ 标题区 ============
p('病例规模不再是主要推断瓶颈的边界：估计目标、监测杠杆与流感住院实证',
  style='Title', size='16pt', bold=True, align='center', after='12pt')
p('摘要：准确识别疫情增长并预测短期病例负担是传染病预警的核心任务。直观上病例数越多测量精度越高，但在个体超传播、监测漏报与周际环境扰动并存时，“样本量”与“信息量”不能简单等同。既有信息下界的标度律建立在当期再生数R_t一类估计目标上；本文证明更换估计目标后标度律随之改变，据此将“病例规模何时不再是主要推断瓶颈”作为监测设计问题严格推导。主要结果：（i）矩估计量R̂_t=C_t/(ρn)为条件MLE，方差达到Fisher信息逆，随m=ρn单调收敛于零；（ii）推断跨期基础水平R̄时方差受环境底板v_R制约，导出环境项与规模项相等的平滑交叉点m_×；（iii）提高ρ仅消除漏报抽稀方差，唯有扩大基数n使各项方差同时衰减，拉长观测期数以O(1/T)削减环境方差；（iv）给出负二项单调似然比的精确增长判定检验与离散功效。实证方面，利用CDC NHSN 2020—2026年16218个州周流感住院数据：仿射FGLS拟合得规模相关方差项b=2.2434（95%CI[1.50,3.02]）、环境底板a=0.0991、经验交叉点22.6例/周；误差预算分解将平均误差定量为与规模无关份额39%–55%（回顾口径54.6%）、规模份额45%–61%（随基准口径移动），样本中已实现的大规模观测（D_t≥250）误差约为全体平均的六成；达峰期总体误差约89%来自平稳基准的常数偏差（各规模箱占比59.5%–94.8%不等）；统一损失尺度后达峰期内部规模项仍显著为正（b=7.93），但点估计低于初期（共同分母口径1.85对2.24）且阶段差异未达统计显著（交互项95%CI含零）——失效的是平稳性假定而非病例规模；时变交叉点在流感季（中位数19.7—20.4）与非流感季（46.9—47.9）间系统性分离。上述量化参照为监测资源在规模与协变量之间的配置比较提供了量级判断。',
  size='10.5pt', first='420', after='6pt')
p('关键词：疫情增长判定；分支过程；超传播；漏报；环境随机性；监测设计；短期预测；流感住院实证',
  size='10.5pt', after='12pt')

# ============ 0 引言 ============
h1('0引言')
body('准确识别疫情由平稳或下降转为上升增长，并对随后数周的病例负担作出可靠预测，是现代传染病预警与应急响应的核心支柱。在常规统计直觉中，大样本量通常意味着高推断精度，即增加捕获病例数能够持续压制随机计数波动的相对影响。然而，在传染病监测与动力学建模的真实场景下，这一直觉往往遭遇严峻挑战：病原体传播普遍具有高度个体异质性（超传播），导致继发感染数严重过离散[1,2]；监测系统普遍存在不同程度的不完全检测与报告延迟[20,31]；更关键的是，处于同一地理辖区或时间窗口内的宿主群体共同受到气象条件、人群接触模式以及周期性社会流动等环境随机扰动[16,33]。在个体微观超传播、宏观监测漏报与中观共同环境波动交织并存的条件下，“样本量”与“信息量”不能再被简单等同。')
body('关于传染病监测数据中信息瓶颈与推断局限的研究，在既有文献中形成了数条清晰而深入的发展脉络。第一条脉络源于对传播异质性与更新过程动力学的建模探索。开创性工作揭示了个体繁殖数高度偏离泊松假设的负二项分布特征[1,3]；基于发病时间间隔分布的代际更新过程模型逐步确立了时变再生数推断的通用范式[4,5]，其中以Cori等[6]提出的瞬时更新框架及其衍生工具（如EpiEstim）成为实时疫情追踪的国际主流基准。近年来，学者们进一步针对滑动窗口选择、世代间隔不确定性及截断偏差对再生数估计的扭曲效应展开了深入的方法学讨论与评估指南[7,8,15]。')
body('第二条脉络聚焦于不完全观测、报告延迟与状态空间滤波。现实公共卫生系统难以直接捕捉真实感染发生，往往只能观测到夹杂抽稀与迟滞的医院确诊或重症入院序列[21,32]。为了从带噪监测序列中恢复潜在未观测感染压力，学者们构建了包含粒子滤波、半机制更新过程与分层时空平滑在内的状态空间推断架构[14,31]。特别地，针对显著漏报疾病的计数建模，Bracher与Held[13]提出了基于边缘矩匹配的方法，在避免高维潜变量完整似然计算的同时，系统揭示了报告率与传播强度的联合可识别性边界。')
body('第三条脉络近年来利用信息论与Fisher信息量严格解析了带噪疫情曲线所蕴含的物理信息极限。开创性文献量化了带噪发病序列中的Fisher信息量随观测期与抽样比例的演化规律[10]，进而证明了在有效再生数框架下实时检测疫情反弹存在不可逾越的根本性信息论下界[9]，并揭示了由观测噪声诱导的非对称干预延迟边界[11]。然而，必须深刻指出的是：既有信息下界文献所确立的标度律，其信息量随期望病例数近似线性增长的结论，本质上均是在当期再生数R_t这一类估计目标下建立的。本文在此与之形成正面对话：信息下界的标度律在推断目标由当期参数转换为跨期基础水平时将发生根本性改变——对当期条件参数R_t，增加病例规模的边际方差收益恒为正；而对跨周平稳的潜在基础趋势R̄，单期规模收益受制于共同环境方差底板v_R并受平滑交叉点m_×标定。换言之，“病例数何时不再是主要瓶颈”不是疫情系统的孤立物理属性，而是估计目标与观测维度的内生属性，这一目标依赖性为既有信息极限理论补充了一个关键的结构性维度。')
body('第四条脉络植根于非线性生态动力学中人口统计随机性与环境随机性的经典二分法[18,33]。群体微观的繁殖与抽稀随机性随种群或样本规模扩大而呈现大数定律衰减，但不可观测的宏观共同环境震荡在单期横截面内具有共同加性或乘性特征，无法仅凭该期样本内部的数据聚合予以消除[16,17,19]。类似地，从应用统计与计量学的视角来看，这一问题与经典测量误差模型与混合效应信度理论具有深刻的代数同构性[22,23,25]。在流行病学暴露与风险估计中，观测噪声导致的衰减偏倚与方差分配已被广泛探讨[24]。在这一语境下，本文推导的方差交叉点m_×，在数理实质上恰对应单期估计方差内部信度比（Reliability Ratio，即信号方差占总方差的比例）等于0.5的关键对称点，为理解监测精度演变提供了跨学科的统计理论锚点。')
body('第五条脉络来自于大规模真实监测网络与流感预测评估实践（如CDC FluSight挑战赛）的经验启示[29,30]。全美疾控中心长期运行的多模型前瞻性集成预测评估表明，随着监测系统覆盖面的扩张与统计模型的复杂化，前瞻预测精度的提升迅速呈现收益递减平台，集合模型的误差往往受制于超预期的季节性漂移而非单个辖区的样本规模[26,27,28]；在评估此类前瞻预测表现时，相对尺度均方误差等评分规则展现出有效平衡不同发病规模量级的稳健优势[12]。')
body('面对上述理论进展与现实经验，回答“病例规模何时不再主导推断误差”，绝不能将单代理想公式无条件推广。本文的贡献不在于单独提出新的负二项分支模型或漏报校正公式，而在于针对“病例规模何时不再主导推断误差”这一具体监测设计问题，建立一个分层随机推断框架，系统实现以下五项贡献：（1）严格区分当期环境条件下的传播参数R_t与跨期基础水平R̄，证明二者对增加病例规模的边际方差响应截然不同，解析导出单期指定估计量方差内部环境项与抽样项相等的平滑交叉点m_×（对应信度比0.5的结构位置）；（2）精确拆解监测杠杆的非对称性：提高报告率仅能消除漏报抽稀方差，唯有扩大真实基数才能使各项方差同时衰减；（3）在理想化重复采样设计与总监测输入规模预算B=T·m约束下，严格推导拉长独立观测期数T削减环境方差v_R的精确表达式与AR(1)自相关闭式；（4）给出基于负二项单调似然比的精确上尾超临界增长判定检验并证明其水平控制；在时间序列更新过程中清晰界定事后代理增长统计量与事前单步病例预测的内在代数关系与条件方差展开；（5）采用美国疾控中心国家医疗保健安全网（CDC NHSN）2020—2026年覆盖50个州及华盛顿特区周度流感住院真实数据（16,218个州周观测），在控制聚类不确定性的前提下，测得经验收益放缓平台的数量级与报告政策切换前后的离散度分化，识别出达峰期失效的是跨期平稳基准假定而非病例规模本身；进一步构建与Cori时变更新过程基线的竞争对照，开展预测偏差项分解与季节内独立两阶段最小二乘（2SLS）稳健性检验；并给出误差预算份额分解与时变经验交叉点：仿射拟合中过半误差份额落在与规模无关的拟合项上，样本中已实现的大规模观测误差约为全体平均的六成。')
body('本文结构安排如下：第1节回顾相关文献脉络；第2节建立传播与报告模型并界定两类估计目标；第3节呈现核心理论结果、交叉点与监测杠杆非对称性推导；第4节报告增长判定离散功效与更新过程预测模拟；第5节利用全美流感住院真实监测数据展开系统实证检验与反证边界分析；第6节总结全文并探讨公共卫生监测设计的决策启示。')

h1('1研究回顾')
body('综合上述文献，既有研究分别刻画了超传播（Lloyd-Smith等[1], Endo等[2], Kucharski等[3]）、时变再生数更新过程（Wallinga & Teunis[4], Fraser[5], Cori等[6], Thompson等[7], Gostic等[8], Steyn等[15]）、漏报与报告延迟状态空间模型（Bracher & Held[13], Bhatt等[14], Stoner等[31], Lipsitch等[20], Azmon等[32]）、Fisher信息量下界（Parag等[9,10,11]）、人口统计随机性与环境随机性二分（Rohani等[33], Rasmussen等[16], Aber等[17], Dalziel等[19], Bretó等[18]）、测量误差与信度比理论（Fuller[22], Carroll等[23], Armstrong[24], Verbeke & Molenberghs[25]）以及真实监测与FluSight预测挑战（Reich等[26], Cramer等[27], Ray等[28], Biggerstaff等[29], Jhung等[30], Bosse等[12]）各自对推断的影响。')
body('然而，“病例规模何时不再主导推断误差”这一关于监测资源配置的结构性问题——尤其是规模收益如何随估计目标（当期参数 vs. 跨期基础水平）、监测杠杆（基数n vs. 报告率ρ）以及疫情动态相位发生质变——尚未在统一的数理与实证框架下得到解答。本文的差异化定位即在于填补这一理论与经验空白。')
h1('2模型与估计目标')
h2('2.1传播与报告模型')
body('设上一传播代有n名真实感染者，第i名感染者产生的继发感染数为X_i。在给定当期环境条件下的传播参数R_t后，个体继发感染数服从过离散负二项分支分布：')
eq(r'E[X_{i,t}\mid R_t]=R_t,\quad Var(X_{i,t}\mid R_t)=R_t+\frac{R_t^2}{k}')
body('其中k>0为个体传播离散参数（k→0对应极端超传播，k→∞退化为泊松分布）。给定(n,R_t)时个体继发感染数条件独立，当期真实新发感染总数为I_t=∑X_i。观测过程采用固定报告率ρ∈(0,1]的二项抽稀模型：C_t|I_t~Binomial(I_t,ρ)。理论基准设定声明：第3节推导中n暂时设定为已知真实风险集规模，其用途是推导条件明确的理论基准，并非声称现实监测必然已知真实感染数。')
h2('2.2两种估计目标与信息集')
body('目标A（当期传播参数）：估计当期环境条件决定的个体期望继发感染水平R_t。目标B（跨期基础水平）：估计消除单周共同随机扰动后的潜在基础增长趋势R̄。单期基准设计中，当期环境满足条件矩设定E[R_t|n]=R̄，Var(R_t|n)=v_R>0。针对前瞻预测，本文区分全历史信息集F_t^I=σ(I_1,…,I_t,C_1,…,C_t)与仅报告序列信息集F_t^C=σ(C_1,…,C_t)：后者是现实监测中唯一可直接获取的信息集，由于二项漏报的存在，下一周的潜在感染压力本身具有不确定性。')

# ============ 3 理论结果 ============
h1('3理论结果')
h2('3.1当期传播参数的条件似然、Fisher信息与方差')
body('命题1：在负二项分支与二项报告基准下，当n与ρ已知时：（i）报告病例数C_t|(n,R_t)严格服从均值为ρnR_t、形状参数为nk的负二项分布；（ii）矩估计量R̂_t=C_t/(ρn)恰为该条件似然下的极大似然估计；（iii）关于R_t的Fisher信息量为')
eq(r'\mathcal{I}(R_t\mid n)=\frac{n}{R_t/\rho+R_t^2/k}')
body('（iv）估计量的条件方差严格达到Cramér–Rao下界：')
eq(r'Var\left(\frac{C_t}{\rho n}\,\middle|\,n,R_t\right)=\frac{R_t}{\rho n}+\frac{R_t^2}{kn}')
body('证明思路：由概率生成函数，NB卷积二项抽稀仍是NB（参数p*=k/(k+ρR_t)）；对数似然得分方程直接解得MLE，代入NB方差即得信息量与方差。该命题表明：对当期参数，信息量∝n，规模的边际方差收益恒为正。')
h2('3.2跨期基础水平的单期边际方差与交叉点')
body('命题2：在条件矩假设下，以单期估计量C_t/(ρn)估计跨期基础水平R̄，其给定n的条件边际方差为')
eq(r'Var\left(\frac{C_t}{\rho n}\,\middle|\,n\right)=v_R+\frac{\bar{R}}{\rho n}+\frac{\bar{R}^2+v_R}{kn}')
body('由全方差公式：第一项为环境项Var(R_t|n)=v_R，第二、三项为E[R_t/(ρn)+R_t²/(kn)|n]代入E[R_t²|n]=v_R+R̄²展开即得。令m=ρn为期望报告病例数，上式可重写为v_R+A/m，其中A=R̄+ρ(R̄²+v_R)/k。定义方差占比交叉点：')
eq(r'm_\times=\frac{A}{v_R}=\frac{\bar{R}+\rho(\bar{R}^2+v_R)/k}{v_R}')
body('其含义是环境方差项与病例规模相关项相等的规模位置：m>m_×后环境方差占主导，增加病例数仅能作用于占比逐渐减小的A/m项。交叉点是平滑的收益放缓点，不是硬阈值。')
h2('3.3监测杠杆的非对称性')
body('将式(5)拆解为(n,ρ)的二元函数后可得命题3：其一，报告率杠杆存在饱和下界——当ρ→1时漏报抽稀方差(1-ρ)R̄/(ρn)→0，但计数波动R̄/n与超传播内在抽样方差(R̄²+v_R)/(kn)依然存在，估计方差严格大于环境底板v_R；其二，基数杠杆具有全域收敛性——无论ρ处于何种水平，n→∞时两项规模相关方差均严格收敛于零。直观含义：提高报告率消除的是漏报额外引入的抽稀方差；唯有扩大真实基数才能使两项方差同时衰减至环境底板。')
h2('3.4预算约束下的监测维度权衡')
body('命题4：在理想化重复采样设计（T个观测期、每期风险集n_T=B/(ρT)、总预算B=T·m）下：若各期环境扰动跨期独立，样本均值估计量的方差为v_R/T+A/B——总预算固定时拉长期数T严格单调降低方差；若环境扰动服从AR(1)自相关Cov(R_t,R_{t+s})=v_R r^{|s|}，有限期精确方差为')
eq(r'Var(\bar{\hat{R}}_T)=\frac{v_R}{T}\left[\frac{1+r}{1-r}-\frac{2r(1-r^T)}{T(1-r)^2}\right]+\frac{A}{B}')
body('大期数下可近似为有效独立期数T_eff=T(1-r)/(1+r)。当要求各期风险集为正整数且精确用尽预算时，可行设计集合为{T:B/(ρT)∈N_+}，即B/ρ的正整数因子集合。')
h2('3.5增长判定检验与预测方差分解')
body('命题5：基准模型下负二项族关于充分统计量C_t具有单调似然比，拒绝域{C_t≥c_α}的非随机化上尾检验在复合原假设H_0:R_t≤1下严格控水平α，离散临界值c_α=min{c:P_{R_t=1}(C_t≥c)≤α}；对备择R_t=1+δ，检出功效由负二项累积分布精确给出。命题6：基于报告信息集F_t^C，未来报告病例的预测方差严格分解为二项抽稀项与感染过程方差项的加权和：Var(C_{t+1}|F_t^C)=ρ(1-ρ)E[I_{t+1}|F_t^C]+ρ²Var(I_{t+1}|F_t^C)。')

# ============ 4 数值模拟 ============
h1('4数值模拟评估')
h2('4.1增长判定检验的有限样本功效')
body('在名义水平α=0.05、ρ=0.25下，针对k∈{0.1,0.35,1.0}与期望报告规模m∈[5,600]进行30000次蒙特卡洛抽样。三项发现：（1）渐近Wald检验在网格内最小规模m=5、k=0.1处经验一类错误率达最高的8.1%（30000次模拟），全低规模段系统性过检，而精确离散检验全网格严格受控；（2）k=0.35时达到80%功效所需规模由δ=0.15的517.8例降至δ=0.50的57.2例；（3）相同增长信号(δ=0.25)下，从k=1.0到k=0.1样本需求放大约3倍（142.0对415.0例）。结果如图1所示。')
fig('fig2_growth_detection_power.png', '图1 当期超临界增长判定检验功效与有限样本性质验证')
h2('4.2更新过程的预测误差与参照曲线')
body('在时间序列更新过程中（150条轨迹×26个预测起点，种子20260925），事后代理增长统计量误差与事前单步预测相对均方误差严格相差常数因子1/R̄²，但二者均不精确等于单代理想基准：更新过程额外引入报告历史代理真实感染压力的预测偏差项与随机分母的倒数二次方重加权。经验曲线在m≥25段为缩放参照曲线(v_R+A/m)/R̄²的0.75–0.98倍并渐近收敛于0.0302；m=6处为参照的1.82倍（0.543对0.298），小规模端不贴合——这是单代基准在极小规模不适用的直接证据。规模每翻倍的边际削减由单代参照的1/(2(1+m/m_×))给出——m=10时为42.1%，越过交叉点m_×=53.1（25.0%）后，m=200时仅10.5%；m<12段经验降幅系统性高于该解析式。结果如图2所示。')
fig('fig3_forecasting_saturation_crossover.png', '图2 更新过程事后增长统计量与事前单步病例预测误差对照')

# ============ 5 实证 ============
h1('5实证检验：全美流感住院监测数据（2020—2026）')
h2('5.1数据源、制度分段与预处理')
body('数据来自全美各州及华盛顿特区医院向CDC NHSN上报的周度实验室确诊新发流感住院人数及各州周度医院报告覆盖率。样本跨越2020年8月至2026年9月，共16218个州周观测；D_t≥5的有效推断样本10303个。样本期内该系统经历三次制度切换：前过渡高覆盖期（2020年10月至2024年4月30日，184个有效周、N=6,009），含大流行早期高覆盖子段（N=2,627，覆盖率87.8%）与2022年10月起的法定强制子段（N=3,382，覆盖率93.7%），合计平均覆盖率91.1%（中位数92.3%）；第二阶段自愿过渡期（2024年5月1日至10月31日）覆盖率断崖式跌至54.6%（中位数45.7%）；第三阶段CMS新规重制期（2024年11月1日起）恢复至91.8%（中位数93.2%）。这一覆盖率骤降构成本文考察报告率冲击的主要制度变异来源。')
body('状态空间设定：取滞后权重向量w=(0.65,0.25,0.10)构建各州历史有效输入压力D_t=∑w_s C_{t+1-s}，增长代理为G_{t+1}=C_{t+1}/D_t。该卷积核是感染代际分布与住院报告延迟分布的离散复合。评估预测误差时采用阶段条件化基准Ĉ_{t+1|t}=R̄_phase·D_t，以在同等基准下纯化评估病例捕获规模对相对预测方差的边际贡献。')
h2('5.2检验一：流行初期波段的方差衰减与误差预算分解')
body('在三个流感季的流行初期上升波段（N=1267，平均增长率1.6706）中，按理论形式直接对原始观测估计仿射模型E[((G_{t+1}-R̄)/R̄)²|D_t]=a+b/D_t，采用一阶可行广义最小二乘（FGLS，权重1/μ̂²），标准误与置信区间由按州聚类的cluster bootstrap给出（1500次重抽）。结果：规模相关方差项b=2.2434（95%CI[1.5019,3.0161]，1500次重抽无一次b≤0）；环境底板a=0.0991（95%CI[0.0841,0.1173]）；经验交叉点m_×^emp=b/a=22.6例/周（95%CI[13.7,33.7]）。从最小规模组到[20,50)组，经验相对均方误差下降51.3%，聚类95%CI严格分离。各规模分组统计见表1。')
table(
    ['每周有效规模D_t', 'N', '相对均方误差', '中位数', '普通SEM', '州聚类SE', '州聚类95%CI'],
    [['[5,20)', '319', '0.3292', '0.0969', '0.0425', '0.0437', '[0.2435,0.4149]'],
     ['[20,50)', '297', '0.1605', '0.0596', '0.0169', '0.0189', '[0.1235,0.1974]'],
     ['[50,100)', '187', '0.1446', '0.0483', '0.0194', '0.0198', '[0.1057,0.1835]'],
     ['[100,250)', '220', '0.1118', '0.0545', '0.0110', '0.0114', '[0.0895,0.1341]'],
     ['[250,600)', '152', '0.1032', '0.0460', '0.0097', '0.0133', '[0.0771,0.1293]'],
     ['[600,5000)', '92', '0.1054', '0.0735', '0.0109', '0.0146', '[0.0769,0.1340]']],
    '表1 流行初期波段单步前瞻预测误差随周捕获规模的分组统计')
body('针对D_t与C_{t+1}共享报告噪声导致的变量误差问题，我们进一步以滞后3–5周报告序列构造的工具规模D_t^iv做两阶段最小二乘对照。在全初期波段汇集样本（有效样本N=1,051）中，第一阶段F统计量达1147.1（强工具），第二阶段b估计为2.8501（a=0.0807），高于基准OLS的1.4581。更将2SLS限定在各流感季初期波段内部独立运行：2022–23季（N=273）第一阶段F=277.4，b_iv=3.2787（OLS: 1.8865）；2023–24季（N=358）第一阶段F=464.8，b_iv=2.1867（OLS: 1.6760）；2024–25季（N=420）第一阶段F=503.3，b_iv=3.6131（OLS: 1.8295）。在每个独立季节内部，第一阶段F统计量均远超临界值（均高于270），且每个季节的2SLS规模斜率均显著为正并高于对应OLS斜率，与经典测量误差导致的衰减偏倚修正方向一致。')
body('过度离散结构Var(L)/E[L]²从[5,20)箱的5.32单调降至[600,5000)箱的0.99，与理论形状一致。')
body('预测偏差项与机制隐含斜率的分解检验：依更新过程展开式，总相对预测方差严格分解为条件方差项与预测偏差项。若以2周滑动窗口估计量作为局部期望比的经验代理，实测偏差项在全波段均值为0.1252，仿射拟合得到其斜率b_bias=0.3416；而扣除偏差项后的纯条件方差项斜率依然高达b_var=3.3553（a_var=0.1109）。这直接澄清了经验估计b=2.24高于单代静态模型参数空间隐含值（约0.6–0.8）的机制来源：在动态更新卷积与分母1/D_t²随机重加权下，时间序列更新过程固有地放大了经验规模斜率，但规模相关项的主导贡献依然来自纯条件方差，而非单纯的趋势预测偏差。')
body('与时变更新过程及时间序列基准的竞争预测性能对照：我们进一步构建了两类具备竞争性的事前预测基线：其一是基于Cori等(2013)滑动窗口更新过程的时变再生数预测（分别取1周、2周与3周滑动窗）；其二是经典时间序列朴素平移基准C_{t+1}=C_t。在流行初期波段上，各基准的事前单步相对预测均方误差见表2。结果表明：(1)全体均值上，2周窗与3周窗Cori基线的RelMSE分别为0.2876与0.2490，中位数为0.0658与0.0626，性能远优于朴素平移基准（均值0.6367，中位数0.1732）；(2)关键在于分规模表现：在所有更新过程基准中，预测误差均随每周病例规模D_t单调显著下降；(3)在大规模段（D_t≥100），2周与3周Cori基线的平均相对均方误差（约0.087–0.098）甚至略低于常数阶段均值（0.103–0.112），原因在于时变参数能更好适应局部流行波动的拐点；但在小规模段（[5,20)），滑动窗口估计R_t自身引入了显著的有限样本小计数估计方差。对2周与3周Cori基线误差进行仿射拟合，分别给出b=6.0637（m_x=74.7）与b=4.9836（m_x=65.3）。无论采用回顾性阶段基准还是事前时变更新过程基准，预测方差随规模衰减是内在的结构性特征。')
table(
    ['每周有效规模D_t', '样本数N', '阶段均值基准', 'Cori 2周窗基线', 'Cori 3周窗基线', '朴素平移基线'],
    [['[5,20)', '319', '0.3292', '0.6576', '0.5606', '1.2563'],
     ['[20,50)', '297', '0.1605', '0.2576', '0.2288', '0.5528'],
     ['[50,100)', '187', '0.1446', '0.2271', '0.1680', '0.5639'],
     ['[100,250)', '220', '0.1118', '0.0903', '0.0870', '0.3999'],
     ['[250,600)', '152', '0.1032', '0.0975', '0.0903', '0.2356'],
     ['[600,5000)', '92', '0.1054', '0.0983', '0.0982', '0.1360'],
     ['全体样本均值', '1267', '0.1813', '0.2876', '0.2490', '0.6367'],
     ['全体样本中位数', '1267', '0.0653', '0.0658', '0.0626', '0.1732']],
    '表2 不同预测基准在流行初期波段单步相对均方误差（RelMSE）的规模分箱对照')
body('口径声明：本节主分析以阶段均值为基准，属回顾性的阶段条件误差分析，目的是在受控同等基准下检验误差随规模的衰减形态。严格滚动起点核验（每个t仅用其前数据估计基准）：全部历史扩张窗得b=9.1579（聚类bootstrap 95%CI[5.8376,12.8819]，b/a=22.5）；26周滚动池得b=9.4562（CI[6.7612,12.4767]，b/a=42.7）；逐州扩张窗得b=13.2666（CI[9.1385,18.2948]，b/a=38.9）。三种事前口径下误差水平抬升（回顾性基准偏乐观），但规模项均显著为正、分箱单调下降，大规模端实际观测的误差水平稳定低于全体平均。误差预算分解：初期平均相对均方误差0.181中，与规模无关拟合项贡献54.6%，规模相关项贡献45.1%，模型外残差不足0.3%。作为对照，样本中实际处于大规模端（D_t≥250，共244个观测）的组内平均相对均方误差为0.104——与拟合截距a=0.0991一致，即经验数据中已实现的大规模观测误差约为全体平均的六成；过半误差份额落在与规模无关的拟合项上，提示环境协变量采集与多期平滑是值得进一步评估的互补路径。达峰期条件方差口径下的分解结构类似（46.7%对55.6%）。这组份额结构给本文核心问题提供了可操作的参照：规模收益真实存在，但过半误差份额与规模无关，监测资源的配置取决于当前所处份额结构。')
h2('5.3检验二：达峰期——失效的是平稳基准而非病例规模')
body('反证口径：用流行初期估计的平稳基准R̄_early=1.6706预测全部阶段。达峰与回落期（各季全国达峰周及其后7周，N=1220，平均增长率0.8075）的总误差在所有规模组恒定处于0.292—0.312，看似不再随规模下降。但分解显示：在达峰期总体样本的均值—方差分解中，基准偏移项为0.2669，占总体损失88.9%；按各箱自身均值计算的偏差占比从[5,20)箱的59.5%升至[600,5000)箱的94.8%，总体份额不代表各箱结构，"总误差不随规模下降"并不能否定规模的作用。改用达峰期自身均值作基准后，仿射拟合给出a=0.0665（95%CI[0.0467,0.0897]）、b=7.9272（95%CI[5.4239,11.2248]）：达峰期内部规模相关项显著为正。但阶段间b比较必须统一损失尺度：该b以R̄_peak=0.8075归一化，而初期以R̄_early=1.6706归一化，两者不同分母。三口径比较：未归一化损失下初期b=6.2611、达峰期b=5.1690；共同分母（R̄_early）口径下初期b=2.2434、达峰期b=1.8521；各自归一化口径（原稿）下为2.2434对7.9272——统一尺度后达峰期b点估计低于初期，共同尺度交互项-0.9183（聚类bootstrap 95%CI[-2.2702,0.6261]），阶段差异不显著——支持"未发现达峰期斜率增强"，不支持断言"达峰期低于初期"。交互项与分别拟合的点估计差（-0.3913）不同，因联合回归使用共同参数化与全样本FGLS权重并吸收阶段主效应。两者均刻画阶段斜率差，但分别拟合与联合FGLS所使用的迭代权重及估计程序不同，故点估计不必相等。原稿"达峰期规模项绝对量更高"是归一化分母差异的伪象。')
body('因此正确的反证结论是关于基准而非样本量：达峰期人群行为改变、节假日填报积压及医疗挤兑使跨期平稳基准不再适用，单期预测的首要误差来源转为基准偏移；但本文的检验不支持"达峰期病例规模不再有用"这一更强主张——控制基准偏移后达峰期内部规模项仍显著为正（b=7.9272）。同时，统一损失尺度后的三口径比较（未归一化5.17对6.26、共同分母1.85对2.24，交互项95%CI含零）表明达峰期规模项并不强于初期：规模在两阶段同样有用，未检出阶段间增强。实际含义是：达峰期需要换用非平稳状态模型或显式行为协变量，而不是停止扩大病例捕获。')
body('时变经验交叉点的探索性证据：对全部有效观测做26周滚动窗口的窗口条件化仿射拟合，251个窗口的经验交叉点中位数为36.5（IQR[14.2,61.6]），量级与分段估计一致，但离季窗口的估计极不稳定（个别窗口逾千例）；逐周滚动产生的高度重叠窗口使IQR的有效样本量小于表观窗口数，区间解读应视为保守。为考察窗口内基准与窗口误差同源的影响，改用前一窗口均值作滞后基准重估（滞后只保证时间先后，不自动保证外生性）：流感季中位数19.7对非流感季47.9，与窗口内基准下的分离（20.4对46.9）基本一致，说明该分离并非窗口内基准机械压缩的产物。稳健的定性事实是：流感季窗口的中位数（20.4）系统性低于非流感季窗口（46.9）——传播活跃期规模收益的边界更近、扩大捕获更早进入回报放缓区，为动态监测资源配置提供了直接可用的阶段信号。')
h2('5.4检验三：报告制度切换对观测噪声的冲击')
body('2024年5—10月自愿填报过渡期（N=420，平均覆盖率54.6%）中，观测增长率标准差由强制期的0.624攀升至1.823（扩张192.1%），偏度由3.29暴增至14.98，最大值达33.9；恢复强制后两者回落至0.649与2.68。但四分位距（0.638→0.594）与中位绝对离差基本不变——覆盖率下降主要放大的是分布右尾极端值，而非主体分布宽度。全样本与流感季子样本同向放大、尾部指标与主体指标明确分化，与报告率冲击放大分布右尾的机制方向相容；鉴于医院覆盖率并不等同于事件级二项报告概率、停止填报的医院可能非随机，且自愿期与夏季低发期重叠，本节对比定位为与漏报噪声机制相容的描述性证据，而非制度冲击的因果检验。')
h2('5.5检验四：空间跨区域汇聚的方差收益与边界')
body('将51个州级单位按周加总构建全美序列：流行初期波段平均周捕获规模约6662例，单步预测相对均方误差降至0.0348（中位数0.0115，N=28），低于单州平台（约0.10，约降至三分之一）。全国汇总误差较低与空间汇聚并存这一事实，与命题3"扩大基数使各项方差同时衰减"的方向相容；但本对比未单独识别环境抵消、子代波动平均与其他汇总效应的相对贡献。属地化预警所需的州级参数异质性与达峰时间差，则界定了简单汇总的适用边界。全部实证结果见图3。')
fig('fig4_empirical_falsification.png', '图3 全美CDC NHSN流感住院真实监测数据实证检验')

# ============ 6 结论 ============
h1('6结论')
body('本文建立了一个分层推断框架，厘清了疫情监测中病例规模相关方差与环境方差的相互作用。理论上，本文区分当期参数与跨期基础水平两类估计目标，证明了当期估计量的极大似然与Fisher信息性质，导出了基础水平单期估计方差内部环境项与抽样项相等的平滑交叉点，精确拆解了监测杠杆的非对称性与单期—多期设计权衡，并建立了离散增长判定检验与单步预测方差分解。')
body('全美CDC NHSN周度流感住院数据的描述性经验分析展现了与理论相容的特征：（1）流行初期波段的仿射模型估计出显著为正的规模相关方差项（b=2.2434，95%CI[1.5019,3.0161]）与环境底板（a=0.0991），经验交叉点22.6例/周；误差预算分解显示初期平均误差中与规模无关拟合项占54.6%、规模相关项占45.1%，样本中已实现的大规模观测误差约为全体平均的六成——规模收益真实、过半份额与规模无关；（2）达峰期套用跨期平稳基准会产生占主导的常数偏差（约89%），说明失效的是平稳性假定而非数据量；控制基准偏移后规模相关方差项依然显著为正，达峰期的正确应对是引入非平稳状态模型，而非停止扩大病例捕获；滚动窗口证据进一步表明经验交叉点并非常数，流感季窗口中位数20.4系统性低于非流感季46.9；（3）自愿过渡期覆盖率骤降伴随观测增长率标准差扩张192%与偏度扩张355%，但主体离散度指标未变，且存在季节性混杂，仅作描述性证据；（4）空间汇聚在平均局部环境扰动的同时须权衡属地预警的空间异质性限制。')
body('本文的实证口径为机制导向的经验检验：D_t的测量误差通过十分位拟合予以控制，制度分期的季节性混杂通过流感季子样本予以校准；误差预算分解进一步表明，与规模无关项的份额随基准口径在39%–55%间移动（回顾口径54.6%），该项同时含环境方差与代理不确定性、不单独识别为环境项——环境协变量的价值属待检验假设。未来工作可进一步结合显式环境协变量、微观计量参数校准、误报—漏报代价不对称下的最优监测配置，以及多毒株共循环场景下动态状态滤波的实时监测理论。')

# ============ 参考文献 ============
h1('参考文献')
refs = [
    'Lloyd-Smith J O, Schreiber S J, Kopp P E, et al. Superspreading and the effect of individual variation on disease emergence. Nature, 2005, 438(7066): 355-359. DOI: 10.1038/nature04153.',
    'Endo A, Abbott S, Kucharski A J, et al. Estimating the overdispersion in COVID-19 transmission using outbreak sizes outside China. Wellcome Open Research, 2020, 5: 67. DOI: 10.12688/wellcomeopenres.15842.3.',
    'Kucharski A J, Russell T W, Diamond C, et al. Early dynamics of transmission and control of COVID-19: a mathematical modelling study. The Lancet Infectious Diseases, 2020, 20(5): 553-560. DOI: 10.1016/S1473-3099(20)30144-4.',
    'Wallinga J, Teunis P. Different epidemic curves for severe acute respiratory syndrome reveal similar impacts of control measures. American Journal of Epidemiology, 2004, 160(6): 509-516. DOI: 10.1093/aje/kwh255.',
    'Fraser C. Estimating individual and household reproduction numbers in an emerging epidemic. PLOS ONE, 2007, 2(8): e758. DOI: 10.1371/journal.pone.0000758.',
    'Cori A, Ferguson N M, Fraser C, et al. A new framework and software to estimate time-varying reproduction numbers during epidemics. American Journal of Epidemiology, 2013, 178(9): 1505-1512. DOI: 10.1093/aje/kwt133.',
    'Thompson R N, Stockwin J E, van Gaalen R D, et al. Improved inference of time-varying reproduction numbers during infectious disease outbreaks. Epidemics, 2019, 29: 100356. DOI: 10.1016/j.epidem.2019.100356.',
    'Gostic K M, McGough L, Baskerville E B, et al. Practical considerations for measuring the effective reproductive number, Rt. PLOS Computational Biology, 2020, 16(12): e1008409. DOI: 10.1371/journal.pcbi.1008409.',
    'Parag K V, Donnelly C A. Fundamental limits on inferring epidemic resurgence in real time using effective reproduction numbers. PLOS Computational Biology, 2022, 18(4): e1010004. DOI: 10.1371/journal.pcbi.1010004.',
    'Parag K V, Donnelly C A, Zarebski A E. Quantifying the information in noisy epidemic curves. Nature Computational Science, 2022, 2(9): 584-594. DOI: 10.1038/s43588-022-00313-1.',
    'Parag K V, Lambert B, Donnelly C A, Beregi S. Asymmetric limits on timely interventions from noisy epidemic data. Communications Physics, 2025, 8: 450. DOI: 10.1038/s42005-025-02358-w.',
    'Bosse N I, Abbott S, Cori A, et al. Scoring epidemiological forecasts on transformed scales. PLOS Computational Biology, 2023, 19(8): e1011393. DOI: 10.1371/journal.pcbi.1011393.',
    'Bracher J, Held L. A marginal moment matching approach for fitting endemic-epidemic models to underreported disease surveillance counts. Biometrics, 2021, 77(4): 1348-1359. DOI: 10.1111/biom.13384.',
    'Bhatt S, Ferguson N, Flaxman S, et al. Semi-mechanistic Bayesian modeling of COVID-19 with renewal processes. Journal of the Royal Statistical Society Series A: Statistics in Society, 2023, 186(4): 601-624. DOI: 10.1093/jrsssa/qnad001.',
    'Steyn N, Parag K V, Thompson R N. A primer on inference and prediction with epidemic renewal models and sequential Monte Carlo. Statistics in Medicine, 2025, 44(3): e70204. DOI: 10.1002/sim.70204.',
    'Rasmussen D A, Ratmann O, Koelle K. Inference for nonlinear epidemiological models using genealogies and time series. PLOS Computational Biology, 2011, 7(8): e1002136. DOI: 10.1371/journal.pcbi.1002136.',
    'Aber S, Di Q, Dalziel B D. Time-series modeling of epidemics in complex populations: Detecting changes in incidence volatility over time. PLOS Computational Biology, 2025, 21(2): e1012882. DOI: 10.1371/journal.pcbi.1012882.',
    'Bretó C, He D, Ionides E L, King A A. Time series analysis via mechanistic models: inference on imperfectly observed populations. The Annals of Applied Statistics, 2009, 3(1): 319-348. DOI: 10.1214/08-AOAS201.',
    'Dalziel B D, Kissler S, Gog J R, et al. Urbanization and the geography of influenza in the United States. Science, 2018, 362(6410): 75-79. DOI: 10.1126/science.aat6030.',
    'Lipsitch M, Swerdlow D L, Finelli L. Enhancing the value of public health surveillance: simple models for surveillance data. PLOS Medicine, 2015, 12(7): e1001844. DOI: 10.1371/journal.pmed.1001844.',
    'Nouvellet P, Cori A, Garske T, et al. A simple approach to measure controllability of infectious disease outbreaks. Epidemics, 2018, 22: 29-38. DOI: 10.1016/j.epidem.2017.02.012.',
    'Fuller W A. Measurement Error Models. New York: John Wiley & Sons, 1987. DOI: 10.1002/9780470316665.',
    'Carroll R J, Ruppert D, Stefanski L A, Crainiceanu C M. Measurement Error in Nonlinear Models: A Modern Approach. 2nd ed. Boca Raton: Chapman & Hall/CRC, 2006. DOI: 10.1201/9781420010138.',
    'Armstrong B G. Effect of measurement error on epidemiological studies of environmental and nutritional risks. Annals of Epidemiology, 1998, 8(6): 381-387. DOI: 10.1016/S1047-2797(97)00234-8.',
    'Verbeke G, Molenberghs G. Linear Mixed Models for Longitudinal Data. New York: Springer, 2000. DOI: 10.1007/978-1-4419-0300-6.',
    'Reich N G, McGowan C J, Yamana T K, et al. Accuracy of real-time multi-model ensemble forecasts for seasonal influenza in the U.S. PLOS Computational Biology, 2019, 15(11): e1007486. DOI: 10.1371/journal.pcbi.1007486.',
    'Cramer E Y, Ray E L, Lopez V K, et al. Evaluation of individual and ensemble probabilistic forecasts of COVID-19 mortality in the United States. Proceedings of the National Academy of Sciences, 2022, 119(15): e2113561119. DOI: 10.1073/pnas.2113561119.',
    'Ray E L, Brooks L C, Bien J, et al. Comparing trained and untrained probabilistic ensemble forecasts of COVID-19 cases and deaths in the United States. International Journal of Forecasting, 2023, 39(3): 1366-1383. DOI: 10.1016/j.ijforecast.2022.06.005.',
    'Biggerstaff M, Alper D, Dredze M, et al. Results from the second open CDC challenge to predict the 2014-2015 influenza season. Epidemics, 2018, 24: 26-37. DOI: 10.1016/j.epidem.2018.02.003.',
    'Jhung M A, Powell T, Dhara R, et al. Epidemiology of influenza-associated hospitalizations in the United States, 1993-2008. Clinical Infectious Diseases, 2012, 54(11): 1555-1562. DOI: 10.1093/cid/cis253.',
    'Stoner O, Economou T, Drummond G. Hierarchical spatio-temporal modeling for surveillance data with reporting delays and incomplete observation. Biometrics, 2023, 79(3): 2296-2308. DOI: 10.1111/biom.13788.',
    'Azmon A, Faes C, Hens N. Estimating the reproduction number from incompletely observed outbreaks: real-time monitoring and reporting delay adjustment. Epidemics, 2014, 9: 30-38. DOI: 10.1016/j.epidem.2014.09.006.',
    'Rohani P, Keeling M J, Grenfell B T. The interplay between environmental and demographic stochasticity in infectious disease dynamics. Science, 2002, 297(5583): 1010-1012. DOI: 10.1126/science.1073801.'
]


for i, r in enumerate(refs, 1):
    p('[%d] %s' % (i, r), size='9pt', after='3pt')

# ============ 页脚页码 ============
cmds.append({'command': 'add', 'parent': '/', 'type': 'footer',
             'props': {'type': 'default', 'text': '', 'align': 'center', 'size': '9pt'}})
cmds.append({'command': 'add', 'parent': '/footer[1]/p[1]', 'type': 'field',
             'props': {'fieldType': 'page'}})

with open(os.path.join(BASE, '_batch.json'), 'w', encoding='utf-8') as f:
    json.dump(cmds, f, ensure_ascii=False)
print(len(cmds), 'commands')
