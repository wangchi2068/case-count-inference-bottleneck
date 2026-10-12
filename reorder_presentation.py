# -*- coding: utf-8 -*-
"""
Reorder Master Defense Presentation Slides:
Move "Overview & Thesis Architecture" from front (Slide 2) to summary section (Slide 9),
making the narrative flow intuitive:
Motivation -> Mechanism -> Theory -> Design -> Simulation -> Empirical -> External -> Architecture Summary -> Timeline -> Thanks
"""

filepath = r"D:\trae\paper_final\build_master_defense_presentation.py"
with open(filepath, 'r', encoding='utf-8') as f:
    text = f.read()

# Update headers and page numbers
# Slide 3 (Intro) becomes Slide 2 (page 02 / 11)
text = text.replace(
    'add_header(slide, "01 / 绪论：研究背景与核心设问  •  RESEARCH MOTIVATION & OBJECTIVES", "常识直觉与统计本质：监测规模越大越好吗？", "03 / 11")',
    'add_header(slide, "01 / 绪论：研究背景与核心设问  •  RESEARCH MOTIVATION & OBJECTIVES", "常识直觉与统计本质：监测规模越大越好吗？", "02 / 11")'
)

# Slide 4 (Mechanism) becomes Slide 3 (page 03 / 11)
text = text.replace(
    'add_header(slide, "02 / 微观机制：分支过程与报告抽稀  •  DYNAMICAL MODEL & OBSERVATION PROCESS", "两阶段分层抽稀：从微观超传播到宏观报告", "04 / 11")',
    'add_header(slide, "02 / 微观机制：分支过程与报告抽稀  •  DYNAMICAL MODEL & OBSERVATION PROCESS", "两阶段分层抽稀：从微观超传播到宏观报告", "03 / 11")'
)

# Slide 5 (Inference) becomes Slide 4 (page 04 / 11)
text = text.replace(
    'add_header(slide, "03 / 理论推断：渐近方差分解与杠杆非对称性  •  ASYMPTOTIC VARIANCE & LEVERS", "瞬时再生数与跨期基准估计：全方差分解与 CRLB 达到", "05 / 11")',
    'add_header(slide, "03 / 理论推断：渐近方差分解与杠杆非对称性  •  ASYMPTOTIC VARIANCE & LEVERS", "瞬时再生数与跨期基准估计：全方差分解与 CRLB 达到", "04 / 11")'
)

# Slide 6 (Design) becomes Slide 5 (page 05 / 11)
text = text.replace(
    'add_header(slide, "04 / 运筹设计：多期时间抽样与 Cochran 对偶  •  MULTI-PERIOD DESIGN & COCHRAN DUAL", "监测资源运筹优化：样本预算恒常性与二阶导严格凸性", "06 / 11")',
    'add_header(slide, "04 / 运筹设计：多期时间抽样与 Cochran 对偶  •  MULTI-PERIOD DESIGN & COCHRAN DUAL", "监测资源运筹优化：样本预算恒常性与二阶导严格凸性", "05 / 11")'
)

# Slide 7 (Simulation) becomes Slide 6 (page 06 / 11)
text = text.replace(
    'add_header(slide, "05 / 数值模拟：假设检验功效与更新过程预测  •  SIMULATION & HYPOTHESIS TESTING", "离散功效锯齿波、Wald 检验失真与更新过程预测偏差", "07 / 11")',
    'add_header(slide, "05 / 数值模拟：假设检验功效与更新过程预测  •  SIMULATION & HYPOTHESIS TESTING", "离散功效锯齿波、Wald 检验失真与更新过程预测偏差", "06 / 11")'
)

# Slide 8 (Empirical) becomes Slide 7 (page 07 / 11)
text = text.replace(
    'add_header(slide, "06 / 经验实证：全美流感住院大数据计量检验  •  EMPIRICAL FALSIFICATION & NHSN DATA", "全美流感住院实证：理论仿射假说的检验与反转辨析", "08 / 11")',
    'add_header(slide, "06 / 经验实证：全美流感住院大数据计量检验  •  EMPIRICAL FALSIFICATION & NHSN DATA", "全美流感住院实证：理论仿射假说的检验与反转辨析", "07 / 11")'
)

# Slide 9 (External) becomes Slide 8 (page 08 / 11)
text = text.replace(
    'add_header(slide, "07 / 外部扩展：跨预测模型与跨病种外部验证  •  EXTERNAL VALIDITY & GENERALIZABILITY", "跨模型与跨病种扩展：从 CDC FluSight 到欧洲 COVID-19", "09 / 11")',
    'add_header(slide, "07 / 外部扩展：跨预测模型与跨病种外部验证  •  EXTERNAL VALIDITY & GENERALIZABILITY", "跨模型与跨病种扩展：从 CDC FluSight 到欧洲 COVID-19", "08 / 11")'
)

# Slide 2 (Roadmap & Architecture) becomes Slide 9 (page 09 / 11)
text = text.replace(
    'add_header(slide, "00 / 课题全景与大论文架构  •  THESIS STRUCTURE & MID-TERM PROGRESS", "大论文七章体系与技术路线全景 (85页规划)", "02 / 11")',
    'add_header(slide, "08 / 总结全景：技术路线与大论文架构全貌  •  METHODOLOGICAL ROADMAP & THESIS OVERVIEW", "端到端研究全景闭环与大论文七章体系", "09 / 11")'
)

# Slide 10 (Progress & Schedule) stays Slide 10 (page 10 / 11)
# Header title can be fine-tuned
text = text.replace(
    'add_header(slide, "08 / 进度规划：中期研究成果总结与大论文推进  •  PROGRESS & THESIS TIMELINE", "阶段性成果盘点、大论文撰写推进与时间里程碑", "10 / 11")',
    'add_header(slide, "09 / 进度规划：阶段性成果与大论文时间表  •  PROGRESS & THESIS TIMELINE", "阶段性成果盘点、大论文撰写推进与时间里程碑", "10 / 11")'
)

# Now update main() build order
old_main_order = """    print("Building Slide 1: 正式封面...")
    build_slide_1_cover(prs.slides[0])
    
    print("Building Slide 2: 大论文七章架构与中期进展全景...")
    build_slide_2_overview(prs.slides[1])
    
    print("Building Slide 3: 第一章 绪论 · 研究背景与核心设问...")
    build_slide_3_intro(prs.slides[2])
    
    print("Building Slide 4: 第二章 微观机制 · 分支过程与报告抽稀...")
    build_slide_4_mechanism(prs.slides[3])
    
    print("Building Slide 5: 第三章 理论推断 · 估计目标分化与杠杆非对称性...")
    build_slide_5_inference(prs.slides[4])
    
    print("Building Slide 6: 第三章 运筹设计 · 多期时间抽样与 Cochran 对偶...")
    build_slide_6_design(prs.slides[5])
    
    print("Building Slide 7: 第四章 数值模拟 · 假设检验功效与更新过程预测...")
    build_slide_7_simulation(prs.slides[6])
    
    print("Building Slide 8: 第五章 经验实证 · 全美 NHSN 流感住院大数据实证...")
    build_slide_8_empirical(prs.slides[7])
    
    print("Building Slide 9: 第六章 外部扩展 · CDC FluSight 与欧洲 COVID-19 验证...")
    build_slide_9_external(prs.slides[8])
    
    print("Building Slide 10: 进度规划 · 中期研究成果总结与大论文推进计划...")
    build_slide_10_progress(prs.slides[9])
    
    print("Building Slide 11: 封底致谢页...")
    build_slide_11_thanks(prs.slides[10])"""

new_main_order = """    print("Building Slide 1: 正式封面...")
    build_slide_1_cover(prs.slides[0])
    
    print("Building Slide 2: 第一章 绪论 · 研究背景与核心设问...")
    build_slide_3_intro(prs.slides[1])
    
    print("Building Slide 3: 第二章 微观机制 · 分支过程与报告抽稀...")
    build_slide_4_mechanism(prs.slides[2])
    
    print("Building Slide 4: 第三章 理论推断 · 估计目标分化与杠杆非对称性...")
    build_slide_5_inference(prs.slides[3])
    
    print("Building Slide 5: 第三章 运筹设计 · 多期时间抽样与 Cochran 对偶...")
    build_slide_6_design(prs.slides[4])
    
    print("Building Slide 6: 第四章 数值模拟 · 假设检验功效与更新过程预测...")
    build_slide_7_simulation(prs.slides[5])
    
    print("Building Slide 7: 第五章 经验实证 · 全美 NHSN 流感住院大数据实证...")
    build_slide_8_empirical(prs.slides[6])
    
    print("Building Slide 8: 第六章 外部扩展 · CDC FluSight 与欧洲 COVID-19 验证...")
    build_slide_9_external(prs.slides[7])
    
    print("Building Slide 9: 总结全景 · 课题技术路线与大论文架构全貌...")
    build_slide_2_overview(prs.slides[8])
    
    print("Building Slide 10: 进度规划 · 阶段性成果盘点与大论文推进时间表...")
    build_slide_10_progress(prs.slides[9])
    
    print("Building Slide 11: 封底致谢页...")
    build_slide_11_thanks(prs.slides[10])"""

text = text.replace(old_main_order, new_main_order, 1)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(text)

print("Reordered presentation flow successfully!")
