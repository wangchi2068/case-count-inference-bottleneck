# -*- coding: utf-8 -*-
"""
精修西安科技大学应用统计硕士《中期答辩.pptx》：
1. 字体全局替换：汉字全部设为宋体 (SimSun)，英文与数字全部设为 Times New Roman (无损Schema规范修改)；
2. Slide 5 & Slide 6 补充理论亮点 (Lloyd-Smith Nature 2005 奠基引用 & Cochran 两阶段抽样闭式解同构)；
3. 为全部 12 页幻灯片写入超详细、接地气、自然口语化的大白话演讲者备注 (Speaker Notes)，可直接照着念！
"""

import os
import shutil
import pptx
from pptx.util import Inches, Pt, Cm
from pptx.oxml import parse_xml

SRC_PPTX = r"C:\Users\wangchi2068\.kimi-code\sessions\wd_trae_c14486ecff06\session_16eab20c-4f77-44fa-85dd-43ea90e9b7fc\attachments\f_147a1f7c-00cd-4a3b-b1df-0947a4ba443e-中期答辩.pptx"
OUT_PPTX_REPO = r"D:\trae\paper_final\中期答辩_精修版.pptx"
OUT_PPTX_ROOT = r"D:\trae\中期答辩_精修版.pptx"
OUT_PPTX_ORIG = r"D:\trae\中期答辩.pptx"

FONT_CN = "宋体"
FONT_EN = "Times New Roman"

def set_font_clean(run):
    """Schema-compliant font setter without XML validation errors"""
    rPr = run._r.get_or_add_rPr()
    
    # Update or add latin (English & Numbers)
    latin = rPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}latin')
    if latin is not None:
        latin.set('typeface', FONT_EN)
    else:
        rPr.append(parse_xml(f'<a:latin xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" typeface="{FONT_EN}"/>'))
        
    # Update or add ea (Chinese characters)
    ea = rPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}ea')
    if ea is not None:
        ea.set('typeface', FONT_CN)
    else:
        rPr.append(parse_xml(f'<a:ea xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" typeface="{FONT_CN}"/>'))
        
    # Also update cs (Complex Script) for consistency
    cs = rPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}cs')
    if cs is not None:
        cs.set('typeface', FONT_EN)

def set_shape_fonts(shape):
    if shape.has_text_frame:
        for p in shape.text_frame.paragraphs:
            for r in p.runs:
                set_font_clean(r)
    if shape.has_table:
        for row in shape.table.rows:
            for cell in row.cells:
                for p in cell.text_frame.paragraphs:
                    for r in p.runs:
                        set_font_clean(r)

# 12 页超详细、接地气、口语化演讲者备注 (Speaker Notes)
SPEAKER_NOTES = [
    # Slide 1: 封面
    """各位老师好！我是应用统计专业的硕士研究生王驰，我的指导老师是张仲华老师。今天向各位老师汇报我的硕士学位论文中期检查进展，题目是《疫情监测中的病例规模收益边界：估计目标、环境随机性与外部验证》。

开题以来，在张老师的悉心指导下，我主要围绕微观动力学分支过程、渐近统计推断界限和全美流感住院真实大数据展开研究。接下来我从研究背景、核心理论成果、实证检验和后续大论文推进计划四个方面向各位老师汇报，恳请各位评委老师批评指正。""",

    # Slide 2: 背景与动机
    """首先向老师们汇报研究背景和选题动机。这里先向各位评委老师汇报一个情况：我的原开题题目是关于新冠多维控制策略研究的，后来经过张老师深入论证与指导，考虑到当前疫情常态化监测与公卫资源配置的紧迫性，我们将研究聚焦到了更为本质的“病例规模收益边界”这一核心问题上。

为什么要做这个研究？大家平时的直觉都是“数据越多越好、测的人越多推断越准”。但疾控部门在实际监测中经常面临一个很尴尬的困境：在流感或新冠暴发高峰期，每周收上来几万个住院病例，模型对下周走势的预测依然会出现较大偏差；上面花大钱扩建哨点，预测精度很快就进入了平台期，改观非常微弱。

以往文献基于 Fisher 信息论认为信息随病例数线性增长，但这只适用于当期瞬态测量。如果误差主要来自全员共同面临的气象和环境波动，盲目扩建哨点、狂抓病例就无法换来精度。这迫使我们必须在数学上把规模收益的边界给严格算清楚。""",

    # Slide 3: 研究问题与目标
    """基于这个现实矛盾，本课题锁定的核心科学问题是：病例规模扩大时，推断精度的收益究竟在何处放缓？这个放缓是由哪些具体的随机性来源决定的？

围绕这个问题，我设定了四个环环相扣的研究目标：
第一，构建符合生物学真实性的双层随机模型，用负二项分支过程刻画超级传播，用二项抽稀刻画漏报；
第二，在数学上严格区分两类估计目标，推导当期瞬态再生数与跨期基础基准的方差结构，导出内生的特征平衡点 m_x；
第三，采集全美 CDC NHSN 长周期真实住院大数据，检验理论预测的仿射误差结构；
第四，扩展到真实多模型集成预报与欧洲跨病种数据，并推导出预算约束下的最优单期监测规模。""",

    # Slide 4: 研究方法
    """接下来汇报本课题的研究方法，屏幕中间展示的是本文的技术路线图。

我们的方法体系由三根支柱构成：
首先是模型层，我们用负二项分支过程刻画个体生殖数异质性，离散参数 k 越小超传播越强；用二项抽稀刻画样本上报率 rho。我们用概率母函数复合律严格证明了报告病例依然服从负二项分布闭包；
其次是推断层，我们严格证明了目标 A（当期瞬态参数）能够达到 Cramér-Rao 信息量下界，方差按 O(1/m) 无界衰减；而目标 B（跨期潜在基准）由于单期样本无法消除宏观共同冲击，必然留存不可约环境方差底板；
最后是检验层，我们设计了可行广义最小二乘法 FGLS 拟合仿射模型，通过 1,500 次按州聚类 Bootstrap 和分季工具变量法进行稳健性检验。""",

    # Slide 5: 关键结果一 · 理论与模拟
    """下面汇报第一个关键结果：理论推导与随机模拟验证。

屏幕左下方是两个核心理论命题：
首先在微观机理上，我们基于 Lloyd-Smith 等人 2005 年发表在 Nature 上的奠基模型，确立了个体超传播的负二项分支分布。命题 2 证明：跨期目标 B 的方差呈现仿射结构 v_R + A/m。宏观环境底板 v_R 与样本量无关，只有后项抽样误差随规模递减。两项相等的位置就是特征平衡点 m_x = A/v_R，它清晰划分出微观噪声区与宏观环境饱和区。小论文基准情景下平衡点约为 53 例；
命题 3 则证明了杠杆非对称性：单纯提高报告率 rho 到极限，方差依然无法降到 v_R；唯有扩大地理和人群基数 n，方能逼近底板。

屏幕右侧是 50,000 次蒙特卡洛随机模拟结果，仿真与解析方差比在 0.988 到 1.017 之间，证明理论完全精确；同时模拟发现，常规正态 Wald 检验在小样本强超传播下虚警率高达 8.1%，必须使用精确离散检验。""",

    # Slide 6: 关键结果二 · NHSN 实证
    """第二个关键结果来自全美 CDC NHSN 真实数据的实证检验。

我们使用了覆盖全美 50 个州及华盛顿特区整整 6 年、16,218 条周度住院记录，筛选出初期上升波段 1,267 个活跃周样本。
大家看屏幕中间的拟合结果：散点是按病例规模分箱的均方误差均值，实线是 FGLS 仿射拟合线。结果显示：规模反比斜率项 b = 2.2434，95% 置信区间完全远离零点，在 1,500 次聚类 Bootstrap 中无一次小于零，强力证实了规模反比项的存在；实测测定出流感周住院的经验平衡点 m_x 约为 22.6 例/周。

屏幕右下方反映出：当周病例数在 100 例以上时，相对误差基本走平，即便改用权威的 Cori 时变更新过程竞争基准，在 100 例以上也同样收敛到平台期。同时在运筹设计上，我们导出了最优单期规模闭式解 m* = sqrt(c0/c1 * m_x)，在数学形式上同构于经典 Cochran (1977) 两阶段抽样。""",

    # Slide 7: 关键结果三 · 误差来源与稳健性
    """第三个关键结果是误差来源的正交分解与稳健性反转。

屏幕左侧的饼图和数据展示了误差预算份额：在流行初期，约 54.6% 的误差属于与样本量无关的环境底板，规模项仅占 45.1%；在不同流感季中，规模无关份额稳定在 39% 到 55% 之间。这说明仅靠增加病例数，有一半左右的误差是根本消除不掉的。

中间部分汇报了一个重大反转发现：在疫情达峰期，以往文献认为误差横盘在 0.3 意味着样本量失效。我们用均值--方差正交分解证明，达峰期整整 88.9% 的误差来源于疫情转向带来的常数基准漂移！扣除漂移后，规模项斜率仍高达 7.9 且显著为正，推翻了“达峰期样本量无用”的传统误读。

右侧显示：分季 IV 工具变量第一阶段 F 检验高达 76 到 119，排除反向因果；欧洲新冠日度平衡点约为 124.7 例/天，验证了跨病种稳健性。""",

    # Slide 8: 已完成工作
    """接下来向老师们汇报开题以来的具体研究进展和完成情况。

如表格所示：
第 1 到 3 章的双层模型构建、命题 1 到 6 的推导和全部证明已经定稿；
第 4 章的三组蒙特卡洛仿真实验和绘图已全部完成；
第 5 章的全美流感实证拟合、达峰期分解与工具变量检验已完成约 85%，正在补充按优势亚型划分的敏感性测试；
第 6 到 7 章关于 FluSight 集成预测和欧洲新冠的数据清洗与初步拟合已就绪，最优规模的凸性证明已完成。

目前已形成约 30 页的高水平中文期刊定稿论文，大论文七章初稿也已成型。这里顺便向老师们汇报，目前大论文各章初稿经过扩充，整体篇幅已经达到整整 85 页，骨架已经非常完整。""",

    # Slide 9: 后续计划
    """这是我后续的研究工作推进计划与毕业时间表。

按照学院要求，整体按五个阶段推进：
2026 年 10 到 11 月，听取今天各位评委老师的宝贵修改意见，完善第 5 章的亚型子样本与空间自相关分析；
12 月到明年初，完成第 6 章外部验证与第 7 章资源配置章节的全文撰写，并同步修改小论文；
明年 2 到 3 月，进行全文统稿、统一符号体系、复核全部数值一致性；
2027 年 4 月形成正式送审稿，完成学术查重、评阅送审，并参加最终的学位论文答辩。""",

    # Slide 10: 讨论与局限
    """本课题在方法学上也存在一些局限性，我们在此坦诚交代并提出了应对举措：

第一是空间自相关限制：目前按州聚类主要处理了同州跨周相关，按周聚类区间为 1.47 到 3.12，后续我们将增加空间滞后模型与双向聚类；
第二是滞后权重与病毒亚型：平衡点随权重选择在 12 到 46 例之间波动，后续拟增加指数衰减权重测试，并补充各流感季优势亚型分层；
第三是成本参数设定：目前成本比 c0/c1 仅选取了 10 和 100 两种代表性情景，后续拟调研疾控实际哨点运营开销以划定真实参数区间；
第四是识别口径：截距项 a 混合了纯外生环境方差与模型平滑偏差，我们在论文中严格界定结论适用边界，强调经验拐点属于量级参照而非绝对点位识别。""",

    # Slide 11: 结论
    """最后总结本文的核心结论，主要有三点：

第一，病例规模对推断精度的收益真实存在，但在跨期推断中必然受到不可约环境方差 v_R 的约束，内生存在特征平衡点 m_x = A/v_R；
第二，全美流感住院实证测定经验拐点约为 22.6 例/周，约四至五成的误差属于与规模无关的底板；
第三，一旦越过平衡点，单纯增加病例上报已边际收益递减，延长观测周期与引入多模型前瞻集成是降低误差的主要路径；实证中 FluSight 集成预测将达峰期偏差占比成功压缩到了 15.5%。""",

    # Slide 12: 致谢与 Q&A
    """以上就是我的硕士学位论文中期考核汇报。

再次衷心感谢我的校内导师张仲华老师在选题与研究过程中的悉心指导，也诚挚感谢在座各位专家评委老师的聆听！恳请各位老师多提宝贵意见和批评指正！谢谢大家！

【评委可能提问备用小抄】：
1. 平衡点 22.6 例/周能否作为通用固定阈值？答：不能作为跨病种通用固定值，它依赖于时间粒度、报告流程和疾病 R0，应作为具体体系下的量级参照；
2. 为什么不用普通 OLS 而用 FGLS？答：真实数据残差偏度高达 8.63，小样本段方差是均值的 5.32 倍，存在严重的非齐次方差，OLS 功效受损严重，FGLS 加权在大样本下达到最佳线性无偏估计（BLUE）。"""
]

def main():
    print(f"Loading template from {SRC_PPTX}...")
    prs = pptx.Presentation(SRC_PPTX)
    
    # 1. 遍历全部 12 页，深度替换中西文字体
    print("Applying SimSun (宋体) for Chinese and Times New Roman for Latin/Numbers across all 12 slides...")
    for idx, slide in enumerate(prs.slides):
        for s in slide.shapes:
            set_shape_fonts(s)
            
    # 2. Slide 5 补充内容：在命题 2/3 卡片处注入 Nature 2005 引用
    slide5 = prs.slides[4]
    for s in slide5.shapes:
        if s.has_text_frame:
            for p in s.text_frame.paragraphs:
                if "命题 2" in p.text and "Lloyd-Smith" not in p.text:
                    p.text = "命题 2 · 负二项超传播基础 (Lloyd-Smith et al., Nature 2005)"
                    for r in p.runs:
                        set_font_clean(r)
                        
    # 3. Slide 6 补充内容：注入最优单期规模闭式解与 Cochran 同构
    slide6 = prs.slides[5]
    for s in slide6.shapes:
        if s.has_text_frame:
            for p in s.text_frame.paragraphs:
                if "竞争基准" in p.text and "Cochran" not in p.text:
                    p.text = "竞争基准与运筹最优规模 (同构于 Cochran 1977 两阶段抽样)"
                    for r in p.runs:
                        set_font_clean(r)

    # 4. 逐页注入超详细、口语化演讲者备注 (Speaker Notes)
    print("Injecting detailed, conversational speaker notes to all 12 slides...")
    for idx, slide in enumerate(prs.slides):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = SPEAKER_NOTES[idx]
        for p in tf.paragraphs:
            for r in p.runs:
                set_font_clean(r)
                
    # 5. 保存并同步到各目标路径
    print(f"Saving refined presentation to {OUT_PPTX_REPO}...")
    prs.save(OUT_PPTX_REPO)
    
    print(f"Synchronizing to root: {OUT_PPTX_ROOT}...")
    shutil.copyfile(OUT_PPTX_REPO, OUT_PPTX_ROOT)
    
    print(f"Synchronizing to root original name: {OUT_PPTX_ORIG}...")
    shutil.copyfile(OUT_PPTX_REPO, OUT_PPTX_ORIG)
    
    print("SUCCESS: 12-slide defense presentation perfectly refined with SimSun + Times New Roman, theoretical enhancements, and full speaker notes!")

if __name__ == '__main__':
    main()
