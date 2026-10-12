# -*- coding: utf-8 -*-
"""
Build Complete 11-Slide Master's Degree Mid-term Defense Presentation (大论文标准中期答辩汇报)
Fully aligned with the 80-page Master's Thesis Architecture:
- Slide 1: 正式封面 (硕士学位论文中期考核答辩)
- Slide 2: 大论文七章学术架构与中期进展全景 (The 7-Chapter Structure & Progress Radar)
- Slide 3: 第一章 绪论 · 研究背景、现实悖论与核心设问
- Slide 4: 第二章 微观机制 · 分支过程、超传播与二项抽稀 (成功概率p顿悟与PGF闭合)
- Slide 5: 第三章 理论推断 · 估计目标分化、CRLB达到与监测杠杆非对称性 (命题1-3)
- Slide 6: 第三章 运筹设计 · 多期时间抽样、AR(1)求和与Cochran对偶 (命题4与推论1)
- Slide 7: 第四章 数值模拟 · 假设检验功效、Wald失真与更新过程预测分解 (命题5-6与图1-3)
- Slide 8: 第五章 经验实证 · 全美NHSN流感住院大数据计量检验 (N=10,303与88.9%反转)
- Slide 9: 第六章 外部扩展 · CDC FluSight集成预测与欧洲COVID-19验证 (偏离骤降至15.5%)
- Slide 10: 进度规划 · 中期研究成果总结、大论文撰写推进与时间里程碑 (80页规划)
- Slide 11: 封底致谢 (感谢各位专家评委指导与Q&A)
"""

import os
import shutil
import pptx
from pptx.util import Inches, Pt, Cm
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml import parse_xml
from PIL import Image

FORMULAS_DIR = r"D:\trae\paper_final\figures\formulas"
FIGURES_DIR = r"D:\trae\paper_final\figures"
ASSETS_DIR = r"C:\Users\wangchi2068\.gemini\antigravity\scratch\extracted_assets"
INPUT_PPTX = r"D:\trae\paper_final\学术答辩PPT_简约大气优化版.pptx"
OUTPUT_PPTX = r"D:\trae\paper_final\学术答辩PPT_简约大气优化版.pptx"
OUTPUT_PPTX_ROOT = r"D:\trae\学术答辩PPT_简约大气优化版.pptx"

# Colors - Academic Slate & Oxford Navy
C_BG_PAGE      = RGBColor(255, 255, 255)
C_CARD_BG      = RGBColor(248, 250, 252) # Slate 50
C_CARD_BORDER  = RGBColor(226, 232, 240) # Slate 200
C_WHITE        = RGBColor(255, 255, 255)
C_FORMULA_BD   = RGBColor(226, 232, 240)

C_NAVY_DARK    = RGBColor(15, 23, 42)    # Slate 900
C_COVER_BG     = RGBColor(15, 23, 42)    # Dark Navy Slate 900
C_PRIMARY_BLUE = RGBColor(30, 58, 138)   # Blue 900
C_ACCENT_BLUE  = RGBColor(37, 99, 235)   # Blue 600
C_LIGHT_BLUE   = RGBColor(147, 197, 253) # Blue 300
C_TEXT_DARK    = RGBColor(30, 41, 59)    # Slate 800
C_TEXT_BODY    = RGBColor(51, 65, 85)    # Slate 700
C_TEXT_MUTED   = RGBColor(100, 116, 139) # Slate 500
C_HIGHLIGHT_BG = RGBColor(239, 246, 255) # Blue 50
C_HIGHLIGHT_BD = RGBColor(191, 219, 254) # Blue 200
C_TAG_BG       = RGBColor(241, 245, 249) # Slate 100

FONT_CN = "Microsoft YaHei"
FONT_EN = "Segoe UI"

def clear_slide(slide):
    for sp in list(slide.shapes):
        elem = sp._element
        elem.getparent().remove(elem)

def sanitize_shape_xml(shape):
    sp = shape._element
    style = sp.find('{http://schemas.openxmlformats.org/presentationml/2006/main}style')
    if style is not None:
        sp.remove(style)
        
    spPr = sp.spPr
    if spPr is not None:
        eff = spPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}effectLst')
        if eff is not None:
            eff.clear()
        else:
            empty_eff = parse_xml('<a:effectLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"/>')
            spPr.append(empty_eff)
            
        geom = spPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}prstGeom')
        if geom is not None and geom.get('prst') == 'roundRect':
            avLst = geom.find('{http://schemas.openxmlformats.org/drawingml/2006/main}avLst')
            if avLst is not None:
                avLst.clear()
                gd = parse_xml('<a:gd xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="adj" fmla="val 2000"/>')
                avLst.append(gd)

def sanitize_all_slide_shapes(slide):
    for s in slide.shapes:
        sanitize_shape_xml(s)

def format_run(run, text=None, font_cn=FONT_CN, font_en=FONT_EN, size_pt=None, bold=None, color=None):
    if text is not None:
        run.text = text
    if size_pt is not None:
        run.font.size = Pt(size_pt)
    if bold is not None:
        run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color
        
    rPr = run._r.get_or_add_rPr()
    for tag in ['{http://schemas.openxmlformats.org/drawingml/2006/main}latin', 
                '{http://schemas.openxmlformats.org/drawingml/2006/main}ea']:
        el = rPr.find(tag)
        if el is not None:
            rPr.remove(el)
            
    rPr.append(parse_xml(f'<a:latin xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" typeface="{font_en}"/>'))
    rPr.append(parse_xml(f'<a:ea xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" typeface="{font_cn}"/>'))

def add_header(slide, tracker_text, title_text, page_str):
    tb_tr = slide.shapes.add_textbox(Cm(1.5), Cm(0.7), Cm(22.0), Cm(0.55))
    tf_tr = tb_tr.text_frame
    tf_tr.word_wrap = True
    tf_tr.margin_left = tf_tr.margin_right = tf_tr.margin_top = tf_tr.margin_bottom = 0
    p_tr = tf_tr.paragraphs[0]
    p_tr.line_spacing = 1.15
    r_tr = p_tr.add_run()
    format_run(r_tr, tracker_text, size_pt=10.5, bold=True, color=C_ACCENT_BLUE)

    tb_pg = slide.shapes.add_textbox(Cm(27.0), Cm(0.7), Cm(5.37), Cm(0.55))
    tf_pg = tb_pg.text_frame
    tf_pg.word_wrap = True
    tf_pg.margin_left = tf_pg.margin_right = tf_pg.margin_top = tf_pg.margin_bottom = 0
    p_pg = tf_pg.paragraphs[0]
    p_pg.alignment = PP_ALIGN.RIGHT
    p_pg.line_spacing = 1.15
    r_pg = p_pg.add_run()
    format_run(r_pg, page_str, size_pt=11, bold=True, color=C_TEXT_MUTED)

    tb_ti = slide.shapes.add_textbox(Cm(1.5), Cm(1.3), Cm(30.87), Cm(0.95))
    tf_ti = tb_ti.text_frame
    tf_ti.word_wrap = True
    tf_ti.margin_left = tf_ti.margin_right = tf_ti.margin_top = tf_ti.margin_bottom = 0
    p_ti = tf_ti.paragraphs[0]
    p_ti.line_spacing = 1.15
    r_ti = p_ti.add_run()
    format_run(r_ti, title_text, size_pt=21, bold=True, color=C_NAVY_DARK)

    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Cm(1.5), Cm(2.35), Cm(30.87), Pt(1))
    line.fill.solid()
    line.fill.fore_color.rgb = C_CARD_BORDER
    line.line.fill.background()

def create_card(slide, left, top, width, height, fill_color=C_CARD_BG, border_color=C_CARD_BORDER, border_width=Pt(1)):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = fill_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = border_width
    else:
        card.line.fill.background()
    sanitize_shape_xml(card)
    return card

def add_formula_box(slide, left, top, width, height, pic_filename, bg_color=C_WHITE, bd_color=C_FORMULA_BD):
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    box.fill.solid()
    box.fill.fore_color.rgb = bg_color
    box.line.color.rgb = bd_color
    box.line.width = Pt(0.75)
    sanitize_shape_xml(box)
    
    # Priority: FORMULAS_DIR, then ASSETS_DIR
    p1 = os.path.join(FORMULAS_DIR, pic_filename)
    p2 = os.path.join(ASSETS_DIR, pic_filename)
    pic_path = p1 if os.path.exists(p1) else (p2 if os.path.exists(p2) else None)

    if pic_path and os.path.exists(pic_path):
        im = Image.open(pic_path)
        aspect = im.size[0] / im.size[1]
        
        pad_v = Cm(0.12)
        avail_h = height - 2 * pad_v
        target_h = avail_h
        target_w = target_h * aspect
        
        max_avail_w = width - Cm(0.6)
        if target_w > max_avail_w:
            target_w = max_avail_w
            target_h = target_w / aspect
            
        p_left = left + (width - target_w) / 2
        p_top = top + (height - target_h) / 2
        slide.shapes.add_picture(pic_path, p_left, p_top, width=target_w, height=target_h)
    return box

def add_takeaway_card(slide, left, top, width, height, tag_text, body_text, bg_color=C_WHITE, border_color=C_CARD_BORDER):
    card = create_card(slide, left, top, width, height, fill_color=bg_color, border_color=border_color, border_width=Pt(0.75))
    tb = slide.shapes.add_textbox(left + Cm(0.4), top + Cm(0.2), width - Cm(0.8), height - Cm(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.line_spacing = 1.15
    
    is_standalone_tag = tag_text.startswith("【")
    if is_standalone_tag:
        r_tag = p.add_run()
        format_run(r_tag, tag_text, size_pt=10.8, bold=True, color=C_PRIMARY_BLUE)
        
        p2 = tf.add_paragraph()
        p2.space_before = Pt(3)
        p2.line_spacing = 1.18
        r_body = p2.add_run()
        format_run(r_body, body_text, size_pt=9.5, color=C_TEXT_BODY)
    else:
        r_tag = p.add_run()
        format_run(r_tag, tag_text + "  ", size_pt=10.8, bold=True, color=C_PRIMARY_BLUE)
        
        r_body = p.add_run()
        format_run(r_body, body_text, size_pt=9.5, color=C_TEXT_BODY)
    return card

# ==============================================================================
# Slide 1: 正式封面页 (Cover Page)
# ==============================================================================
def build_slide_1_cover(slide):
    clear_slide(slide)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Cm(33.87), Cm(19.05))
    bg.fill.solid()
    bg.fill.fore_color.rgb = C_COVER_BG
    bg.line.fill.background()

    tb_tag = slide.shapes.add_textbox(Cm(2.5), Cm(2.2), Cm(28.87), Cm(0.8))
    tf_tag = tb_tag.text_frame
    p_tag = tf_tag.paragraphs[0]
    r_tag = p_tag.add_run()
    format_run(r_tag, "硕士学位论文中期考核答辩汇报  •  MASTER'S THESIS MID-TERM DEFENSE", size_pt=13, bold=True, color=C_LIGHT_BLUE)

    tb_title = slide.shapes.add_textbox(Cm(2.5), Cm(3.4), Cm(28.87), Cm(2.2))
    tf_title = tb_title.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.line_spacing = 1.15
    r_title = p_title.add_run()
    format_run(r_title, "疫情监测中的病例规模收益边界：\n估计目标、环境随机性与外部验证", size_pt=34, bold=True, color=C_WHITE)

    tb_en = slide.shapes.add_textbox(Cm(2.5), Cm(6.4), Cm(28.87), Cm(1.2))
    tf_en = tb_en.text_frame
    tf_en.word_wrap = True
    p_en = tf_en.paragraphs[0]
    r_en = p_en.add_run()
    format_run(r_en, "Boundaries of Surveillance Scale Returns in Epidemic Monitoring: Estimation Targets, Environmental Stochasticity, and External Validation", size_pt=13, color=C_TEXT_MUTED)

    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Cm(2.5), Cm(8.2), Cm(28.87), Pt(1.5))
    line.fill.solid()
    line.fill.fore_color.rgb = RGBColor(51, 65, 85)
    line.line.fill.background()

    items = [
        ("学科专业 / 专业领域", "应用统计硕士 (MAS)\n流行病学与生物数学建模"),
        ("课题体量与阶段", "预定大论文篇幅 80~85 页\n已成稿 28 页小论文 (213 项检验全过)"),
        ("指导教师 / 指导小组", "指导小组"),
        ("答辩汇报人 / 考核时间", "答辩人\n2026 年秋季 · 硕士中期考核")
    ]
    w_card = Cm(6.7)
    gap = Cm(0.69)
    y_cards = Cm(9.2)
    h_card = Cm(5.2)

    for i, (head, desc) in enumerate(items):
        x = Cm(2.5) + i * (w_card + gap)
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y_cards, w_card, h_card)
        card.fill.solid()
        card.fill.fore_color.rgb = RGBColor(30, 41, 59)
        card.line.color.rgb = RGBColor(51, 65, 85)
        card.line.width = Pt(1)
        sanitize_shape_xml(card)

        tb = slide.shapes.add_textbox(x + Cm(0.5), y_cards + Cm(0.6), w_card - Cm(1.0), h_card - Cm(1.2))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        format_run(r1, head, size_pt=12, bold=True, color=C_LIGHT_BLUE)

        p2 = tf.add_paragraph()
        p2.line_spacing = 1.3
        p2.space_before = Pt(8)
        r2 = p2.add_run()
        format_run(r2, desc, size_pt=11.5, color=RGBColor(241, 245, 249))

    tb_foot = slide.shapes.add_textbox(Cm(2.5), Cm(16.0), Cm(28.87), Cm(1.0))
    tf_foot = tb_foot.text_frame
    p_foot = tf_foot.paragraphs[0]
    r_foot = p_foot.add_run()
    format_run(r_foot, "★ 本课题核心数学推导、全套随机仿真与三大实证数据集检验已全部闭环，当前阶段正系统扩充大论文章节体系。", size_pt=11, color=RGBColor(148, 163, 184))
    sanitize_all_slide_shapes(slide)

# ==============================================================================
# Slide 2: 大论文七章学术架构与中期进展全景 (Overview & Progress)
# ==============================================================================
def build_slide_2_overview(slide):
    clear_slide(slide)
    add_header(slide, "00 / 课题全景与大论文架构  •  THESIS STRUCTURE & MID-TERM PROGRESS", "大论文七章体系与技术路线全景 (85页规划)", "02 / 11")

    y_card = Cm(2.65)
    total_w = Cm(30.87)
    x_left = Cm(1.5)

    # Top Section: Grand Landscape Technical Roadmap Box (enlarged height 11.8cm)
    h_top = Cm(11.8)
    card_map = create_card(slide, x_left, y_card, total_w, h_top, fill_color=C_WHITE, border_color=C_CARD_BORDER)
    pic_map = os.path.join(FIGURES_DIR, "fig0_technical_roadmap.png")
    if os.path.exists(pic_map):
        im_m = Image.open(pic_map)
        asp = im_m.size[0] / im_m.size[1]
        avail_w = total_w - Cm(0.4)
        avail_h = h_top - Cm(0.4)
        if avail_w / avail_h > asp:
            tgt_h = avail_h
            tgt_w = tgt_h * asp
        else:
            tgt_w = avail_w
            tgt_h = tgt_w / asp
        p_x = x_left + (total_w - tgt_w) / 2
        p_y = y_card + (h_top - tgt_h) / 2
        slide.shapes.add_picture(pic_map, p_x, p_y, width=tgt_w, height=tgt_h)

    # Bottom Section: 4 Compact Horizontal KPI Milestone Cards (height 3.10cm, smaller text)
    gap_top_bot = Cm(0.25)
    y_bot = y_card + h_top + gap_top_bot
    h_bot = Cm(3.10)
    w_kpi = (total_w - Cm(0.9)) / 4 # 4 columns
    gap_kpi = Cm(0.3)

    kpis = [
        ("理论体系闭环", "6 大命题 + 1 核心推论", "PGF复合封闭、CRLB UMVUE达到、杠杆非对称性、Cochran对偶闭式解"),
        ("真实大数据实证", "16,218 原始 -> 10,303 样本", "客观筛选无覆盖率偏误，三大制度期 6009+420+3874=10303 严密自洽闭环"),
        ("双重质量检验", "213 项全域回归测试全绿", "多重聚类Bootstrap CI [-2.33, 0.59]、仿射参数 22.6 等一致性核验 100% 通过"),
        ("大论文推进进度", "整整 85 页大论文定稿", "七大主体章节+保姆级附录+80篇文献全面就绪，具备优秀硕士学位论文坚实骨架")
    ]

    for i, (head, val, detail) in enumerate(kpis):
        xk = x_left + i * (w_kpi + gap_kpi)
        card_k = create_card(slide, xk, y_bot, w_kpi, h_bot, fill_color=C_CARD_BG, border_color=C_CARD_BORDER)
        tb_k = slide.shapes.add_textbox(xk + Cm(0.25), y_bot + Cm(0.18), w_kpi - Cm(0.5), h_bot - Cm(0.36))
        tf_k = tb_k.text_frame
        tf_k.word_wrap = True
        
        p1 = tf_k.paragraphs[0]
        r1_h = p1.add_run()
        format_run(r1_h, head, size_pt=9.5, bold=True, color=C_NAVY_DARK)
        
        p_val = tf_k.add_paragraph()
        p_val.space_before = Pt(1.5)
        r1_v = p_val.add_run()
        format_run(r1_v, val, size_pt=10.2, bold=True, color=C_PRIMARY_BLUE)
        
        p2 = tf_k.add_paragraph()
        p2.line_spacing = 1.12
        p2.space_before = Pt(2.0)
        r2 = p2.add_run()
        format_run(r2, detail, size_pt=8.0, color=C_TEXT_BODY)

    sanitize_all_slide_shapes(slide)

def build_slide_3_intro(slide):
    clear_slide(slide)
    add_header(slide, "01 / 绪论：研究背景与核心设问  •  RESEARCH MOTIVATION & OBJECTIVES", "常识直觉与统计本质：监测规模越大越好吗？", "03 / 11")
    
    y_card = Cm(2.65)
    card_h = Cm(15.2)
    
    # Left Column
    x_left = Cm(1.5)
    w_left = Cm(14.2)
    create_card(slide, x_left, y_card, w_left, card_h)
    
    tb_l = slide.shapes.add_textbox(x_left + Cm(0.6), y_card + Cm(0.45), w_left - Cm(1.2), Cm(0.6))
    tf_l = tb_l.text_frame
    p_l = tf_l.paragraphs[0]
    r_l = p_l.add_run()
    format_run(r_l, "公共卫生监测的经验直觉与现实盲区", size_pt=14, bold=True, color=C_PRIMARY_BLUE)
    
    create_card(slide, x_left + Cm(0.6), y_card + Cm(1.25), w_left - Cm(1.2), Cm(2.4), fill_color=C_WHITE, border_color=C_CARD_BORDER)
    tb_s1 = slide.shapes.add_textbox(x_left + Cm(0.85), y_card + Cm(1.4), w_left - Cm(1.7), Cm(2.1))
    tf_s1 = tb_s1.text_frame
    tf_s1.word_wrap = True
    p_s1 = tf_s1.paragraphs[0]
    p_s1.line_spacing = 1.22
    r_s1_b = p_s1.add_run()
    format_run(r_s1_b, "• 监测直觉的经验预设（“规模崇拜”）：\n", size_pt=11, bold=True, color=C_TEXT_DARK)
    r_s1_t = p_s1.add_run()
    format_run(r_s1_t, "传统公卫常预设推断精度随监测规模 m 无界提升（盲目追求更多哨点与更高上报率），然而大规模扩建面临极高的边际成本与资源瓶颈。", size_pt=9.8, color=C_TEXT_BODY)

    create_card(slide, x_left + Cm(0.6), y_card + Cm(3.9), w_left - Cm(1.2), Cm(3.7), fill_color=C_WHITE, border_color=C_CARD_BORDER)
    tb_s2 = slide.shapes.add_textbox(x_left + Cm(0.85), y_card + Cm(4.05), w_left - Cm(1.7), Cm(3.4))
    tf_s2 = tb_s2.text_frame
    tf_s2.word_wrap = True
    p_s2 = tf_s2.paragraphs[0]
    p_s2.line_spacing = 1.22
    r_s2_b = p_s2.add_run()
    format_run(r_s2_b, "• 真实传播与观测的双重复杂性：\n", size_pt=11, bold=True, color=C_TEXT_DARK)
    r_s2_1 = p_s2.add_run()
    format_run(r_s2_1, "1. 微观生物学超传播： 极少数个体引发绝大多数二次感染（负二项分布重尾特征，k ≪ 1）；\n", size_pt=9.8, color=C_TEXT_BODY)
    r_s2_2 = p_s2.add_run()
    format_run(r_s2_2, "2. 宏观观测系统稀疏性： 报告率低下（二项抽稀过程）且伴随强烈的宏观外部环境随机扰动（不可约环境变异 v_R）。", size_pt=9.8, color=C_TEXT_BODY)

    add_takeaway_card(slide, x_left + Cm(0.6), y_card + Cm(7.85), w_left - Cm(1.2), Cm(3.45),
                      "【核心科学设问 (Core Research Question)】",
                      "在资源受限情境下，无限扩大病例报告规模的边际方差收益何时递减？微观抽样误差与宏观环境噪声如何抗衡？是否存在明确且可计算的特征规模平衡点 m_×？大论文立足此问题展开系统论证。",
                      bg_color=C_HIGHLIGHT_BG, border_color=C_HIGHLIGHT_BD)

    create_card(slide, x_left + Cm(0.6), y_card + Cm(11.55), w_left - Cm(1.2), Cm(3.25), fill_color=C_WHITE, border_color=C_CARD_BORDER)
    tb_pos = slide.shapes.add_textbox(x_left + Cm(0.85), y_card + Cm(11.75), w_left - Cm(1.7), Cm(2.85))
    tf_pos = tb_pos.text_frame
    tf_pos.word_wrap = True
    p_pos = tf_pos.paragraphs[0]
    p_pos.line_spacing = 1.22
    r_pos_h = p_pos.add_run()
    format_run(r_pos_h, "本文研究定位与技术路径：\n", size_pt=11, bold=True, color=C_PRIMARY_BLUE)
    r_pos_t = p_pos.add_run()
    format_run(r_pos_t, "构建两阶段分层随机推断模型，严格推导三类推断目标的误差下界，通过大规模蒙特卡洛模拟验证，并基于全美真实流感住院监测数据（NHSN 16,218 州-周）与欧洲 COVID-19 数据完成严格计量检验与机制证伪。", size_pt=9.6, color=C_TEXT_BODY)

    # Right Column: Objectives Mapping
    x_right = Cm(16.2)
    w_right = Cm(16.17)
    create_card(slide, x_right, y_card, w_right, card_h)
    
    tb_r = slide.shapes.add_textbox(x_right + Cm(0.6), y_card + Cm(0.45), w_right - Cm(1.2), Cm(0.6))
    tf_r = tb_r.text_frame
    p_r = tf_r.paragraphs[0]
    r_r = p_r.add_run()
    format_run(r_r, "不同统计推断目标的维度分化与理论映射", size_pt=14, bold=True, color=C_PRIMARY_BLUE)
    
    objectives = [
        ("目标一：单代点估计（Rt 瞬时推断）", 
         "对应大论文第 03 节 • 单期瞬时再生数测量精度", 
         "关注单期测量精度。样本量扩大能否直接消除离散噪声？方差衰减阶数如何？理论证明方差严格按 O(1/m) 衰减，在单代视角下规模收益无界。"),
        ("目标二：增长假设检验（疫情爆发早期预警）", 
         "对应大论文第 04 节 • H0: Rt ≤ 1 vs H1: Rt > 1 早期预警功效", 
         "关注检验检出功效与第 I 类错误控制。在非对称离散跳跃下，增加样本量何时使功效饱和？解析揭示 80% 功效阈值 m_{80%}，证实存在天然天花板。"),
        ("目标三：跨期外推预测（多步动态外推预警）", 
         "对应大论文第 05 节 • 宏观不可约变异与微观抽样误差竞争", 
         "当存在宏观环境随机性（不可约方差 v_R）时，微观抽样误差与宏观环境误差如何竞争？严格导出内生方差平衡点 m_× ≡ b/a，刻画精度平台期。")
    ]
    y_obj = y_card + Cm(1.25)
    for title, subtitle, desc in objectives:
        create_card(slide, x_right + Cm(0.6), y_obj, w_right - Cm(1.2), Cm(3.2), fill_color=C_WHITE, border_color=C_CARD_BORDER)
        tb_o = slide.shapes.add_textbox(x_right + Cm(0.85), y_obj + Cm(0.2), w_right - Cm(1.7), Cm(2.8))
        tf_o = tb_o.text_frame
        tf_o.word_wrap = True
        
        p_t = tf_o.paragraphs[0]
        p_t.line_spacing = 1.15
        r_t = p_t.add_run()
        format_run(r_t, title + "\n", size_pt=11.5, bold=True, color=C_PRIMARY_BLUE)
        
        r_sub = p_t.add_run()
        format_run(r_sub, subtitle + "\n", size_pt=9.5, bold=True, color=C_ACCENT_BLUE)
        
        p_d = tf_o.add_paragraph()
        p_d.space_before = Pt(3)
        p_d.line_spacing = 1.22
        r_d = p_d.add_run()
        format_run(r_d, desc, size_pt=9.8, color=C_TEXT_BODY)
        y_obj += Cm(3.45)
        
    create_card(slide, x_right + Cm(0.6), y_card + Cm(11.95), w_right - Cm(1.2), Cm(2.85), fill_color=C_HIGHLIGHT_BG, border_color=C_HIGHLIGHT_BD)
    tb_sum = slide.shapes.add_textbox(x_right + Cm(0.85), y_card + Cm(12.15), w_right - Cm(1.7), Cm(2.45))
    tf_sum = tb_sum.text_frame
    tf_sum.word_wrap = True
    p_s = tf_sum.paragraphs[0]
    p_s.line_spacing = 1.22
    r_sb = p_s.add_run()
    format_run(r_sb, "【核心学术贡献综述】\n", size_pt=11, bold=True, color=C_PRIMARY_BLUE)
    r_st = p_s.add_run()
    format_run(r_st, "首次从统计理论上澄清了监测规模在‘点估计’、‘假设检验’与‘外推预测’三种不同目标下的收益分化规律，打破了‘规模越大越好’的传统单一教条，为公卫监测资源优化提供了量化基准。", size_pt=9.8, color=C_NAVY_DARK)
    sanitize_all_slide_shapes(slide)

# ==============================================================================
# Slide 4: 第二章 微观机制 · 分支过程与报告抽稀 (Chapter 2)
# ==============================================================================
def build_slide_4_mechanism(slide):
    clear_slide(slide)
    add_header(slide, "02 / 微观机制：分支过程与报告抽稀  •  DYNAMICAL MODEL & OBSERVATION PROCESS", "两阶段分层抽稀：从微观超传播到宏观报告", "04 / 11")
    
    y_card = Cm(2.65)
    card_h = Cm(15.2)
    card_w = Cm(15.18)
    
    # Left Column: Two-stage Data Generating Process
    x_left = Cm(1.5)
    create_card(slide, x_left, y_card, card_w, card_h)
    
    tb = slide.shapes.add_textbox(x_left + Cm(0.6), y_card + Cm(0.45), card_w - Cm(1.2), Cm(0.55))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    r = p.add_run()
    format_run(r, "两阶段分层数据生成机制", size_pt=14, bold=True, color=C_PRIMARY_BLUE)
    
    # Section 1
    tb_m1 = slide.shapes.add_textbox(x_left + Cm(0.6), y_card + Cm(1.15), card_w - Cm(1.2), Cm(1.10))
    tf_m1 = tb_m1.text_frame
    tf_m1.word_wrap = True
    tf_m1.margin_left = tf_m1.margin_right = tf_m1.margin_top = tf_m1.margin_bottom = 0
    p_m1 = tf_m1.paragraphs[0]
    p_m1.line_spacing = 1.15
    r_m1 = p_m1.add_run()
    format_run(r_m1, "• 第一阶段：微观传播层（负二项分支过程） [Lloyd-Smith et al., Nature 2005]", size_pt=10.6, bold=True, color=C_TEXT_DARK)
    p_m1_sub = tf_m1.add_paragraph()
    p_m1_sub.space_before = Pt(2)
    p_m1_sub.line_spacing = 1.15
    r_m1_sub = p_m1_sub.add_run()
    format_run(r_m1_sub, "每个感染者的次级传播数服从 Gamma-Poisson 混合模型（二阶矩如下）：", size_pt=9.6, color=C_TEXT_BODY)
    
    add_formula_box(slide, x_left + Cm(0.6), y_card + Cm(2.35), card_w - Cm(1.2), Cm(1.05), "s2_poisson_gamma.png")
    add_formula_box(slide, x_left + Cm(0.6), y_card + Cm(3.55), card_w - Cm(1.2), Cm(1.05), "s2_moments.png")
    
    # Section 2
    tb_m2 = slide.shapes.add_textbox(x_left + Cm(0.6), y_card + Cm(4.80), card_w - Cm(1.2), Cm(1.10))
    tf_m2 = tb_m2.text_frame
    tf_m2.word_wrap = True
    tf_m2.margin_left = tf_m2.margin_right = tf_m2.margin_top = tf_m2.margin_bottom = 0
    p_m2 = tf_m2.paragraphs[0]
    p_m2.line_spacing = 1.15
    r_m2 = p_m2.add_run()
    format_run(r_m2, "• 第二阶段：宏观观测层（条件二项抽稀）", size_pt=11.2, bold=True, color=C_TEXT_DARK)
    p_m2_sub = tf_m2.add_paragraph()
    p_m2_sub.space_before = Pt(2)
    p_m2_sub.line_spacing = 1.15
    r_m2_sub = p_m2_sub.add_run()
    format_run(r_m2_sub, "潜在感染者独立以概率 ρ 被上报，基准规模为 m（期望报告人数）：", size_pt=9.6, color=C_TEXT_BODY)
    
    add_formula_box(slide, x_left + Cm(0.6), y_card + Cm(6.00), card_w - Cm(1.2), Cm(1.05), "s2_branching_thinning.png")
    
    add_takeaway_card(slide, x_left + Cm(0.6), y_card + Cm(7.25), card_w - Cm(1.2), Cm(2.35),
                      "【成功概率 p 的统计物理顿悟】",
                      "在负二项掷硬币试验中，累计 k 次“成功”之前的“失败数”服从 NB。在疫情中，传人是失败，终止是成功！p = k/(k+Rt)。病毒越强终止概率越低，失败数越暴增！二项抽稀后有效成功概率自动调整为 p* = k/(k+ρRt)。",
                      bg_color=C_HIGHLIGHT_BG, border_color=C_HIGHLIGHT_BD)

    create_card(slide, x_left + Cm(0.6), y_card + Cm(9.80), card_w - Cm(1.2), Cm(4.85), fill_color=C_WHITE, border_color=C_CARD_BORDER)
    tb_bio = slide.shapes.add_textbox(x_left + Cm(0.9), y_card + Cm(10.00), card_w - Cm(1.8), Cm(4.45))
    tf_bio = tb_bio.text_frame
    tf_bio.word_wrap = True
    p_b0 = tf_bio.paragraphs[0]
    p_b0.line_spacing = 1.15
    r_b0 = p_b0.add_run()
    format_run(r_b0, "动力学模型的核心统计特征：", size_pt=11.2, bold=True, color=C_PRIMARY_BLUE)
    
    bio_items = [
        ("方差均值比与超传播：", "Var(Y) / E[Y] = 1 + Rt / k > 1，Lloyd-Smith 等 (Nature 2005) 证实病原体普遍具备强过度离散。"),
        ("稀疏抽稀效应：", "报告率 ρ 仅缩放观测期望均值，但不改变负二项分布族系属性。"),
        ("尺度映射关系：", "报告病例 Ct 的有效规模直接决定了后验推断的信息下界。")
    ]
    for b_pre, r_txt in bio_items:
        p_it = tf_bio.add_paragraph()
        p_it.space_before = Pt(4)
        p_it.line_spacing = 1.18
        r_b = p_it.add_run()
        format_run(r_b, "• " + b_pre + "\n", size_pt=10, bold=True, color=C_TEXT_DARK)
        r_t = p_it.add_run()
        format_run(r_t, "  " + r_txt, size_pt=9.5, color=C_TEXT_BODY)

    # Right Column: PGF Closure and Moments
    x_right = Cm(17.18)
    create_card(slide, x_right, y_card, card_w, card_h)
    
    tb_r = slide.shapes.add_textbox(x_right + Cm(0.6), y_card + Cm(0.45), card_w - Cm(1.2), Cm(0.55))
    tf_r = tb_r.text_frame
    p_r = tf_r.paragraphs[0]
    r_r = p_r.add_run()
    format_run(r_r, "概率母函数保族性与观测分布", size_pt=14, bold=True, color=C_PRIMARY_BLUE)
    
    # Section 1
    tb_pgf = slide.shapes.add_textbox(x_right + Cm(0.6), y_card + Cm(1.15), card_w - Cm(1.2), Cm(1.10))
    tf_pgf = tb_pgf.text_frame
    tf_pgf.word_wrap = True
    tf_pgf.margin_left = tf_pgf.margin_right = tf_pgf.margin_top = tf_pgf.margin_bottom = 0
    p_pgf = tf_pgf.paragraphs[0]
    p_pgf.line_spacing = 1.15
    r_pgf = p_pgf.add_run()
    format_run(r_pgf, "• 严格保族性定理（PGF 复合闭合）", size_pt=11.2, bold=True, color=C_TEXT_DARK)
    p_pgf_sub = tf_pgf.add_paragraph()
    p_pgf_sub.space_before = Pt(2)
    p_pgf_sub.line_spacing = 1.15
    r_pgf_sub = p_pgf_sub.add_run()
    format_run(r_pgf_sub, "通过概率母函数复合运算，严密证明观测数严格保持负二项分布族闭合：", size_pt=9.6, color=C_TEXT_BODY)
    
    add_formula_box(slide, x_right + Cm(0.6), y_card + Cm(2.35), card_w - Cm(1.2), Cm(1.15), "s2_pgf_closure.png")
    
    # Section 2
    tb_mom = slide.shapes.add_textbox(x_right + Cm(0.6), y_card + Cm(3.75), card_w - Cm(1.2), Cm(1.10))
    tf_mom = tb_mom.text_frame
    tf_mom.word_wrap = True
    tf_mom.margin_left = tf_mom.margin_right = tf_mom.margin_top = tf_mom.margin_bottom = 0
    p_mom = tf_mom.paragraphs[0]
    p_mom.line_spacing = 1.15
    r_mom = p_mom.add_run()
    format_run(r_mom, "• 统计参数内涵与二阶矩结构", size_pt=11.2, bold=True, color=C_TEXT_DARK)
    p_mom_sub = tf_mom.add_paragraph()
    p_mom_sub.space_before = Pt(2)
    p_mom_sub.line_spacing = 1.15
    r_mom_sub = p_mom_sub.add_run()
    format_run(r_mom_sub, "形状参数 r = km 由报告基数 m 与离散度 k 调控，观测条件方差为：", size_pt=9.6, color=C_TEXT_BODY)
    
    add_formula_box(slide, x_right + Cm(0.6), y_card + Cm(4.95), card_w - Cm(1.2), Cm(1.15), "s2_obs_variance.png")
    
    create_card(slide, x_right + Cm(0.6), y_card + Cm(6.35), card_w - Cm(1.2), Cm(8.30), fill_color=C_WHITE, border_color=C_CARD_BORDER)
    tb_stat = slide.shapes.add_textbox(x_right + Cm(0.9), y_card + Cm(6.55), card_w - Cm(1.8), Cm(7.90))
    tf_stat = tb_stat.text_frame
    tf_stat.word_wrap = True
    p_s0 = tf_stat.paragraphs[0]
    p_s0.line_spacing = 1.15
    r_s0 = p_s0.add_run()
    format_run(r_s0, "二阶矩结构的统计内涵与理论价值：", size_pt=11.2, bold=True, color=C_PRIMARY_BLUE)
    
    stat_items = [
        ("期望均值线性响应：", "E[Ct | m] = ρ m Rt，保证单代估计的一致无偏性。"),
        ("方差精确双项解构：", "方差精确由‘泊松抽样基准项’与‘个体超传播膨胀项’线性叠加。"),
        ("超传播乘性放大：", "超传播项 (ρ Rt)^2 m / k 随 Rt 平方增加，在高传播期成为方差主导源。"),
        ("严格解析基准：", "为后续单代无偏推断与多步预测方差分解提供了严格的理论解析基准。")
    ]
    for b_pre, r_txt in stat_items:
        p_it = tf_stat.add_paragraph()
        p_it.space_before = Pt(4)
        p_it.line_spacing = 1.18
        r_b = p_it.add_run()
        format_run(r_b, "• " + b_pre + "\n", size_pt=10, bold=True, color=C_TEXT_DARK)
        r_t = p_it.add_run()
        format_run(r_t, "  " + r_txt, size_pt=9.5, color=C_TEXT_BODY)
    sanitize_all_slide_shapes(slide)

print("Slide 3 and Slide 4 generators defined.")

# ==============================================================================
# Slide 5: 第三章 理论推断 · 估计目标分化、CRLB 达到与杠杆非对称性 (Chapter 3 Part 1)
# ==============================================================================
def build_slide_5_inference(slide):
    clear_slide(slide)
    add_header(slide, "03 / 理论推断：渐近方差分解与杠杆非对称性  •  ASYMPTOTIC VARIANCE & LEVERS", "瞬时再生数与跨期基准估计：全方差分解与 CRLB 达到", "05 / 11")
    
    y_card = Cm(2.65)
    card_h = Cm(15.2)
    card_w = Cm(15.18)
    
    # Left Column: Target A & Proposition 1
    x_left = Cm(1.5)
    create_card(slide, x_left, y_card, card_w, card_h)
    
    tb_l = slide.shapes.add_textbox(x_left + Cm(0.6), y_card + Cm(0.45), card_w - Cm(1.2), Cm(0.55))
    tf_l = tb_l.text_frame
    p_l = tf_l.paragraphs[0]
    r_l = p_l.add_run()
    format_run(r_l, "目标一：当期瞬态 Rt 点估计与 CRLB 达到（命题 1）", size_pt=13.5, bold=True, color=C_PRIMARY_BLUE)
    
    # Block 1
    tb_e1 = slide.shapes.add_textbox(x_left + Cm(0.6), y_card + Cm(1.15), card_w - Cm(1.2), Cm(1.05))
    tf_e1 = tb_e1.text_frame
    tf_e1.word_wrap = True
    tf_e1.margin_left = tf_e1.margin_right = tf_e1.margin_top = tf_e1.margin_bottom = 0
    p_e1 = tf_e1.paragraphs[0]
    p_e1.line_spacing = 1.15
    r_e1 = p_e1.add_run()
    format_run(r_e1, "• 矩估计量定义与双层全期望无偏性（塔式法则）：", size_pt=11, bold=True, color=C_TEXT_DARK)
    p_e1_s = tf_e1.add_paragraph()
    p_e1_s.space_before = Pt(2)
    p_e1_s.line_spacing = 1.15
    r_e1_s = p_e1_s.add_run()
    format_run(r_e1_s, "在已知风险集 n 下，矩估计量恰为极大似然估计量，全期望展开证明其严格无偏：", size_pt=9.5, color=C_TEXT_BODY)
    
    add_formula_box(slide, x_left + Cm(0.6), y_card + Cm(2.25), card_w - Cm(1.2), Cm(1.05), "s3_estimator.png")
    
    # Block 2
    tb_e2 = slide.shapes.add_textbox(x_left + Cm(0.6), y_card + Cm(3.45), card_w - Cm(1.2), Cm(1.05))
    tf_e2 = tb_e2.text_frame
    tf_e2.word_wrap = True
    tf_e2.margin_left = tf_e2.margin_right = tf_e2.margin_top = tf_e2.margin_bottom = 0
    p_e2 = tf_e2.paragraphs[0]
    p_e2.line_spacing = 1.15
    r_e2 = p_e2.add_run()
    format_run(r_e2, "• 条件方差展开与无界 O(1/m) 衰减：", size_pt=11, bold=True, color=C_TEXT_DARK)
    p_e2_s = tf_e2.add_paragraph()
    p_e2_s.space_before = Pt(2)
    p_e2_s.line_spacing = 1.15
    r_e2_s = p_e2_s.add_run()
    format_run(r_e2_s, "微观抽样与超传播两项方差均与期望规模 m 成反比，样本量无穷时方差趋于零：", size_pt=9.5, color=C_TEXT_BODY)
    
    add_formula_box(slide, x_left + Cm(0.6), y_card + Cm(4.55), card_w - Cm(1.2), Cm(1.05), "s3_variance_decomp.png")
    
    # Block 3
    tb_e3 = slide.shapes.add_textbox(x_left + Cm(0.6), y_card + Cm(5.75), card_w - Cm(1.2), Cm(1.05))
    tf_e3 = tb_e3.text_frame
    tf_e3.word_wrap = True
    tf_e3.margin_left = tf_e3.margin_right = tf_e3.margin_top = tf_e3.margin_bottom = 0
    p_e3 = tf_e3.paragraphs[0]
    p_e3.line_spacing = 1.15
    r_e3 = p_e3.add_run()
    format_run(r_e3, "• Fisher 信息量与 Cramér–Rao 下界确立（UMVUE）：", size_pt=11, bold=True, color=C_TEXT_DARK)
    p_e3_s = tf_e3.add_paragraph()
    p_e3_s.space_before = Pt(2)
    p_e3_s.line_spacing = 1.15
    r_e3_s = p_e3_s.add_run()
    format_run(r_e3_s, "通过得分方差法与负二阶导期望法双重验证，方差严格达到信息量倒数下界：", size_pt=9.5, color=C_TEXT_BODY)
    
    add_formula_box(slide, x_left + Cm(0.6), y_card + Cm(6.85), card_w - Cm(1.2), Cm(1.05), "s3_cramer_rao.png")
    
    create_card(slide, x_left + Cm(0.6), y_card + Cm(8.10), card_w - Cm(1.2), Cm(6.60), fill_color=C_WHITE, border_color=C_CARD_BORDER)
    tb_take = slide.shapes.add_textbox(x_left + Cm(0.9), y_card + Cm(8.30), card_w - Cm(1.8), Cm(6.20))
    tf_take = tb_take.text_frame
    tf_take.word_wrap = True
    p_t0 = tf_take.paragraphs[0]
    p_t0.line_spacing = 1.15
    r_t0 = p_t0.add_run()
    format_run(r_t0, "核心理论发现与渐近有效性启示：", size_pt=11.2, bold=True, color=C_PRIMARY_BLUE)
    
    take_items = [
        ("无界方差衰减：", "在静态单代信息集下，测量瞬态 Rt 时方差不存在不可约底板，增大样本 m 可使方差任意逼近零。"),
        ("异质性乘性惩罚：", "强超传播（低 k）显著抬高方差系数，但该惩罚可被大样本 m 等比例稀释。"),
        ("UMVUE 优良性质：", "证明估计量达到 Cramér–Rao 下界，在有限样本与大样本下皆为最优无偏估计量。")
    ]
    for b_pre, r_txt in take_items:
        p_it = tf_take.add_paragraph()
        p_it.space_before = Pt(4)
        p_it.line_spacing = 1.18
        r_b = p_it.add_run()
        format_run(r_b, "• " + b_pre + "\n", size_pt=10, bold=True, color=C_TEXT_DARK)
        r_t = p_it.add_run()
        format_run(r_t, "  " + r_txt, size_pt=9.5, color=C_TEXT_BODY)

    # Right Column: Target B & Proposition 3 (Levers Asymmetry)
    x_right = Cm(17.18)
    create_card(slide, x_right, y_card, card_w, card_h)
    
    tb_r = slide.shapes.add_textbox(x_right + Cm(0.6), y_card + Cm(0.45), card_w - Cm(1.2), Cm(0.55))
    tf_r = tb_r.text_frame
    p_r = tf_r.paragraphs[0]
    r_r = p_r.add_run()
    format_run(r_r, "目标三：跨期基准估计与监测杠杆非对称性（命题 2 & 3）", size_pt=13.5, bold=True, color=C_PRIMARY_BLUE)
    
    # Section 1
    tb_r1 = slide.shapes.add_textbox(x_right + Cm(0.6), y_card + Cm(1.15), card_w - Cm(1.2), Cm(1.05))
    tf_r1 = tb_r1.text_frame
    tf_r1.word_wrap = True
    tf_r1.margin_left = tf_r1.margin_right = tf_r1.margin_top = tf_r1.margin_bottom = 0
    p_r1 = tf_r1.paragraphs[0]
    p_r1.line_spacing = 1.15
    r_r1 = p_r1.add_run()
    format_run(r_r1, "• 跨期基准全方差分解与仿射损失结构（命题 2）：", size_pt=11, bold=True, color=C_TEXT_DARK)
    p_r1_s = tf_r1.add_paragraph()
    p_r1_s.space_before = Pt(2)
    p_r1_s.line_spacing = 1.15
    r_r1_s = p_r1_s.add_run()
    format_run(r_r1_s, "存在宏观不可约环境方差 v_R 时，单期样本再大也无法突破底板，呈现仿射形态：", size_pt=9.5, color=C_TEXT_BODY)
    
    add_formula_box(slide, x_right + Cm(0.6), y_card + Cm(2.25), card_w - Cm(1.2), Cm(1.05), "s5_affine_loss.png")
    add_formula_box(slide, x_right + Cm(0.6), y_card + Cm(3.45), card_w - Cm(1.2), Cm(1.05), "s5_crossover.png")
    
    # Section 2
    tb_r2 = slide.shapes.add_textbox(x_right + Cm(0.6), y_card + Cm(4.65), card_w - Cm(1.2), Cm(1.05))
    tf_r2 = tb_r2.text_frame
    tf_r2.word_wrap = True
    tf_r2.margin_left = tf_r2.margin_right = tf_r2.margin_top = tf_r2.margin_bottom = 0
    p_r2 = tf_r2.paragraphs[0]
    p_r2.line_spacing = 1.15
    r_r2 = p_r2.add_run()
    format_run(r_r2, "• 命题 3：监测杠杆的理论非对称性定理：", size_pt=11, bold=True, color=C_PRIMARY_BLUE)
    p_r2_s = tf_r2.add_paragraph()
    p_r2_s.space_before = Pt(2)
    p_r2_s.line_spacing = 1.15
    r_r2_s = p_r2_s.add_run()
    format_run(r_r2_s, "将抽样项拆为漏报项与计数项，比较提高报告率 ρ 与扩大风险基数 n 的渐近极限：", size_pt=9.5, color=C_TEXT_BODY)
    
    add_formula_box(slide, x_right + Cm(0.6), y_card + Cm(5.75), card_w - Cm(1.2), Cm(1.15), "s3_levers_asymmetry.png")
    
    create_card(slide, x_right + Cm(0.6), y_card + Cm(7.10), card_w - Cm(1.2), Cm(7.60), fill_color=C_WHITE, border_color=C_CARD_BORDER)
    tb_lev = slide.shapes.add_textbox(x_right + Cm(0.9), y_card + Cm(7.30), card_w - Cm(1.8), Cm(7.20))
    tf_lev = tb_lev.text_frame
    tf_lev.word_wrap = True
    p_l0 = tf_lev.paragraphs[0]
    p_l0.line_spacing = 1.15
    r_l0 = p_l0.add_run()
    format_run(r_l0, "监测杠杆非对称性的深层公卫启示：", size_pt=11.2, bold=True, color=C_PRIMARY_BLUE)
    
    lev_items = [
        ("报告率极限局限（ρ → 1）：", "即便完全消除漏报（ρ=1），也只能剔除漏报抽稀噪声，人群内部固有的泊松计数波动 R̄/n 与超传播方差依然存在，方差永远无法降至 v_R！"),
        ("人群基数统摄消除（n → ∞）：", "扩大监测人群基数 n，利用大数定律分母趋于无穷，能够同时消除全部微观噪声，方差严格收敛到不可约环境底板 v_R。"),
        ("政策决策启示：", "盲目追求高检测率不能替代地理覆盖面的扩大；监测网络的空间广度比局部的报告饱和度更具信息价值。")
    ]
    for b_pre, r_txt in lev_items:
        p_it = tf_lev.add_paragraph()
        p_it.space_before = Pt(4)
        p_it.line_spacing = 1.18
        r_b = p_it.add_run()
        format_run(r_b, "• " + b_pre + "\n", size_pt=10, bold=True, color=C_TEXT_DARK)
        r_t = p_it.add_run()
        format_run(r_t, "  " + r_txt, size_pt=9.5, color=C_TEXT_BODY)
    sanitize_all_slide_shapes(slide)

# ==============================================================================
# Slide 6: 第三章 运筹设计 · 多期时间抽样与 Cochran 对偶 (Chapter 3 Part 2)
# ==============================================================================
def build_slide_6_design(slide):
    clear_slide(slide)
    add_header(slide, "04 / 运筹设计：多期时间抽样与 Cochran 对偶  •  MULTI-PERIOD DESIGN & COCHRAN DUAL", "监测资源运筹优化：样本预算恒常性与二阶导严格凸性", "06 / 11")
    
    y_card = Cm(2.65)
    card_h = Cm(15.2)
    card_w = Cm(15.18)
    
    # Left Column: Proposition 4 Multi-period Sampling
    x_left = Cm(1.5)
    create_card(slide, x_left, y_card, card_w, card_h)
    
    tb_l = slide.shapes.add_textbox(x_left + Cm(0.6), y_card + Cm(0.45), card_w - Cm(1.2), Cm(0.55))
    tf_l = tb_l.text_frame
    p_l = tf_l.paragraphs[0]
    r_l = p_l.add_run()
    format_run(r_l, "命题 4：多期样本均值方差与样本预算恒常性", size_pt=13.5, bold=True, color=C_PRIMARY_BLUE)
    
    tb_p4 = slide.shapes.add_textbox(x_left + Cm(0.6), y_card + Cm(1.15), card_w - Cm(1.2), Cm(1.05))
    tf_p4 = tb_p4.text_frame
    tf_p4.word_wrap = True
    tf_p4.margin_left = tf_p4.margin_right = tf_p4.margin_top = tf_p4.margin_bottom = 0
    p_p4 = tf_p4.paragraphs[0]
    p_p4.line_spacing = 1.15
    r_p4 = p_p4.add_run()
    format_run(r_p4, "• 固定总样本规模预算 B = T · m 下的方差解构：", size_pt=11, bold=True, color=C_TEXT_DARK)
    p_p4_s = tf_p4.add_paragraph()
    p_p4_s.space_before = Pt(2)
    p_p4_s.line_spacing = 1.15
    r_p4_s = p_p4_s.add_run()
    format_run(r_p4_s, "在整个周期总病例预算 B = T·m 约束下，跨期均值方差呈现惊人的代数特性：", size_pt=9.6, color=C_TEXT_BODY)
    
    add_formula_box(slide, x_left + Cm(0.6), y_card + Cm(2.25), card_w - Cm(1.2), Cm(1.15), "s4_budget_constant.png")
    
    add_takeaway_card(slide, x_left + Cm(0.6), y_card + Cm(3.60), card_w - Cm(1.2), Cm(3.05),
                      "【样本预算恒常性定理 (Invariance of Sampling Variance)】",
                      "第二项抽样误差恒为常数 A/B！无论你怎么分配 T 和 m，只要总人数 B 固定，微观抽样误差永远不变！要想降低总方差，单期拼命堆人数毫无用处，唯一的路径是拉长观测周期 T 去平滑宏观不可约环境变异 v_R！",
                      bg_color=C_HIGHLIGHT_BG, border_color=C_HIGHLIGHT_BD)
                      
    create_card(slide, x_left + Cm(0.6), y_card + Cm(6.85), card_w - Cm(1.2), Cm(7.85), fill_color=C_WHITE, border_color=C_CARD_BORDER)
    tb_ar = slide.shapes.add_textbox(x_left + Cm(0.9), y_card + Cm(7.05), card_w - Cm(1.8), Cm(7.45))
    tf_ar = tb_ar.text_frame
    tf_ar.word_wrap = True
    p_a0 = tf_ar.paragraphs[0]
    p_a0.line_spacing = 1.15
    r_a0 = p_a0.add_run()
    format_run(r_a0, "AR(1) 自相关环境求和与有效独立期数：", size_pt=11.2, bold=True, color=C_PRIMARY_BLUE)
    
    ar_items = [
        ("自相关双重级数求和：", "假定滞后 s 阶环境协方差为 v_R r^s，总方差含级数 S = ∑_{s=1}^{T-1}(T-s)r^s。利用错位相减法求出精确闭式解：S = Tr/(1-r) - r(1-r^T)/(1-r)^2。"),
        ("有效独立期数折减：", "当观测期远大于环境自相关记忆时长（T ≫ 1/(1-r)）时，有效独立期数渐近退化为 T_eff ≈ T (1-r)/(1+r)。"),
        ("大论文理论价值：", "将经典的独立环境同构扩展至真实传染病存在时间记忆的连续状态，给出了时间平滑降差的精确物理折减率。")
    ]
    for b_pre, r_txt in ar_items:
        p_it = tf_ar.add_paragraph()
        p_it.space_before = Pt(4)
        p_it.line_spacing = 1.18
        r_b = p_it.add_run()
        format_run(r_b, "• " + b_pre + "\n", size_pt=10, bold=True, color=C_TEXT_DARK)
        r_t = p_it.add_run()
        format_run(r_t, "  " + r_txt, size_pt=9.5, color=C_TEXT_BODY)

    # Right Column: Corollary 1 Cochran Dual
    x_right = Cm(17.18)
    create_card(slide, x_right, y_card, card_w, card_h)
    
    tb_r = slide.shapes.add_textbox(x_right + Cm(0.6), y_card + Cm(0.45), card_w - Cm(1.2), Cm(0.55))
    tf_r = tb_r.text_frame
    p_r = tf_r.paragraphs[0]
    r_r = p_r.add_run()
    format_run(r_r, "推论 1：显式经费约束下凸优化与 Cochran 抽样对偶", size_pt=13.5, bold=True, color=C_PRIMARY_BLUE)
    
    tb_c1 = slide.shapes.add_textbox(x_right + Cm(0.6), y_card + Cm(1.15), card_w - Cm(1.2), Cm(1.05))
    tf_c1 = tb_c1.text_frame
    tf_c1.word_wrap = True
    tf_c1.margin_left = tf_c1.margin_right = tf_c1.margin_top = tf_c1.margin_bottom = 0
    p_c1 = tf_c1.paragraphs[0]
    p_c1.line_spacing = 1.15
    r_c1 = p_c1.add_run()
    format_run(r_c1, "• 显式经济成本模型与目标方差函数：", size_pt=11, bold=True, color=C_TEXT_DARK)
    p_c1_s = tf_c1.add_paragraph()
    p_c1_s.space_before = Pt(2)
    p_c1_s.line_spacing = 1.15
    r_c1_s = p_c1_s.add_run()
    format_run(r_c1_s, "设每期固定运转维持成本 c_0，单例报告边际成本 c_1。总经费预算 ℬ = T(c_0 + c_1 m)：", size_pt=9.6, color=C_TEXT_BODY)
    
    add_formula_box(slide, x_right + Cm(0.6), y_card + Cm(2.25), card_w - Cm(1.2), Cm(1.15), "s4_cochran_optimal.png")
    
    create_card(slide, x_right + Cm(0.6), y_card + Cm(3.60), card_w - Cm(1.2), Cm(11.10), fill_color=C_WHITE, border_color=C_CARD_BORDER)
    tb_cd = slide.shapes.add_textbox(x_right + Cm(0.9), y_card + Cm(3.80), card_w - Cm(1.8), Cm(10.70))
    tf_cd = tb_cd.text_frame
    tf_cd.word_wrap = True
    p_cd0 = tf_cd.paragraphs[0]
    p_cd0.line_spacing = 1.15
    r_cd0 = p_cd0.add_run()
    format_run(r_cd0, "凸优化闭式解与 Cochran (1977) 抽样理论对偶：", size_pt=11.2, bold=True, color=C_PRIMARY_BLUE)
    
    cd_items = [
        ("一阶导求驻点：", "目标函数 f(m) = (c_0 + c_1 m)(v_R + A/m)/ℬ。令 f'(m) = (c_1 v_R - c_0 A/m^2)/ℬ = 0，解得唯一正根：m^* = sqrt(c_0/c_1 · m_×)。"),
        ("二阶导严格凸性：", "计算二阶导得 f''(m) = 2 c_0 A / (ℬ m^3) > 0（对一切正规模 m 恒正）。目标函数在定义域内严格凸，保证了驻点为唯一的全局极小值点！"),
        ("Cochran (1977) 抽样对偶：", "这一结果在数学形式上与调查抽样鼻祖 Cochran 第 10 章的两阶段抽样最优分配模型完全同构！期数 T 对应初级抽样单元（PSU），单期规模 m 对应次级抽样单元（SSU）。"),
        ("边角解判定与工程约束：", "若求解的规模超出可行上界 m_max，由严格凸性直接导出最优解退化为边界点，具备完备的运筹操作可行性。")
    ]
    for b_pre, r_txt in cd_items:
        p_it = tf_cd.add_paragraph()
        p_it.space_before = Pt(4)
        p_it.line_spacing = 1.18
        r_b = p_it.add_run()
        format_run(r_b, "• " + b_pre + "\n", size_pt=10, bold=True, color=C_TEXT_DARK)
        r_t = p_it.add_run()
        format_run(r_t, "  " + r_txt, size_pt=9.5, color=C_TEXT_BODY)
    sanitize_all_slide_shapes(slide)

# ==============================================================================
# Slide 7: 第四章 数值模拟 · 假设检验功效与更新过程预测 (Chapter 4)
# ==============================================================================
def build_slide_7_simulation(slide):
    clear_slide(slide)
    add_header(slide, "05 / 数值模拟：假设检验功效与更新过程预测  •  SIMULATION & HYPOTHESIS TESTING", "离散功效锯齿波、Wald 检验失真与更新过程预测偏差", "07 / 11")
    
    y_card = Cm(2.65)
    card_h = Cm(15.2)
    card_w = Cm(12.8)
    
    # Left Column: Proposition 5 Testing & Proposition 6 Renewal
    x_left = Cm(1.5)
    create_card(slide, x_left, y_card, card_w, card_h)
    
    tb_l = slide.shapes.add_textbox(x_left + Cm(0.6), y_card + Cm(0.45), card_w - Cm(1.2), Cm(0.55))
    tf_l = tb_l.text_frame
    p_l = tf_l.paragraphs[0]
    r_l = p_l.add_run()
    format_run(r_l, "爆发检测形式化检验与更新过程分解", size_pt=13.5, bold=True, color=C_PRIMARY_BLUE)
    
    tb_s1 = slide.shapes.add_textbox(x_left + Cm(0.6), y_card + Cm(1.15), card_w - Cm(1.2), Cm(0.45))
    tf_s1 = tb_s1.text_frame
    p_s1 = tf_s1.paragraphs[0]
    r_s1 = p_s1.add_run()
    format_run(r_s1, "• 假设检验设定与单调似然比（MLR 一阶差分 > 0）：", size_pt=11, bold=True, color=C_TEXT_DARK)
    
    add_formula_box(slide, x_left + Cm(0.6), y_card + Cm(1.65), card_w - Cm(1.2), Cm(1.05), "s4_hypothesis.png")
    
    tb_s2 = slide.shapes.add_textbox(x_left + Cm(0.6), y_card + Cm(2.80), card_w - Cm(1.2), Cm(0.45))
    tf_s2 = tb_s2.text_frame
    p_s2 = tf_s2.paragraphs[0]
    r_s2 = p_s2.add_run()
    format_run(r_s2, "• 精确功效函数与不完全贝塔表达（命题 5）：", size_pt=11, bold=True, color=C_TEXT_DARK)
    
    add_formula_box(slide, x_left + Cm(0.6), y_card + Cm(3.30), card_w - Cm(1.2), Cm(1.05), "s4_power.png")
    
    tb_s3 = slide.shapes.add_textbox(x_left + Cm(0.6), y_card + Cm(4.45), card_w - Cm(1.2), Cm(0.45))
    tf_s3 = tb_s3.text_frame
    p_s3 = tf_s3.paragraphs[0]
    r_s3 = p_s3.add_run()
    format_run(r_s3, "• 更新过程预测误差与非负预测偏差项（命题 6 式 29）：", size_pt=11, bold=True, color=C_PRIMARY_BLUE)
    
    add_formula_box(slide, x_left + Cm(0.6), y_card + Cm(4.95), card_w - Cm(1.2), Cm(1.05), "s5_renewal_decomp.png")
    
    create_card(slide, x_left + Cm(0.6), y_card + Cm(6.20), card_w - Cm(1.2), Cm(8.50), fill_color=C_WHITE, border_color=C_CARD_BORDER)
    tb_mech = slide.shapes.add_textbox(x_left + Cm(0.9), y_card + Cm(6.40), card_w - Cm(1.8), Cm(8.10))
    tf_mech = tb_mech.text_frame
    tf_mech.word_wrap = True
    p_m0 = tf_mech.paragraphs[0]
    p_m0.line_spacing = 1.15
    r_m0 = p_m0.add_run()
    format_run(r_m0, "数值模拟揭示的深层统计规律：", size_pt=11.2, bold=True, color=C_PRIMARY_BLUE)
    
    mech_items = [
        ("离散阶梯跳跃与锯齿波：", "计数临界值 c_α(m) 随规模呈阶梯状跳跃，当跨越临界值时门槛骤升，引发功效曲线局部呈现特有的锯齿波动！"),
        ("80% 功效阈值天花板：", "跨过 m_80% 后，功效迅速逼近 1.0 平台，边际投入收益归零，证实检验目标存在天然饱和天花板。"),
        ("更新过程双口径解密：", "初始参数口径为表观 0.75~0.98 倍；按评价周实际发生规模重核为 1.01~1.17 倍，严格不低于单代静态下界，印证了式 (29) 预测偏差项的存在！")
    ]
    for b_pre, r_txt in mech_items:
        p_it = tf_mech.add_paragraph()
        p_it.space_before = Pt(4)
        p_it.line_spacing = 1.18
        r_b = p_it.add_run()
        format_run(r_b, "• " + b_pre + "\n", size_pt=10, bold=True, color=C_TEXT_DARK)
        r_t = p_it.add_run()
        format_run(r_t, "  " + r_txt, size_pt=9.5, color=C_TEXT_BODY)

    # Right Column: Figure 2 & Figure 3 Simulation Plots
    x_right = Cm(14.8)
    w_right = Cm(17.57)
    create_card(slide, x_right, y_card, w_right, card_h)
    
    fig_w = Cm(16.5)
    fig_h = Cm(6.0)
    create_card(slide, x_right + Cm(0.53), y_card + Cm(0.45), fig_w, fig_h, fill_color=C_WHITE, border_color=C_CARD_BORDER)
    
    pic_fig2 = os.path.join(FIGURES_DIR, "fig2_growth_detection_power.png")
    if not os.path.exists(pic_fig2):
        pic_fig2 = os.path.join(ASSETS_DIR, "slide_4_pic_3.png")
    if os.path.exists(pic_fig2):
        im = Image.open(pic_fig2)
        aspect = im.size[0] / im.size[1]
        im_w = Cm(16.0)
        im_h = im_w / aspect
        p_x = x_right + Cm(0.53) + (fig_w - im_w) / 2
        p_y = y_card + Cm(0.45) + (fig_h - im_h) / 2
        slide.shapes.add_picture(pic_fig2, p_x, p_y, width=im_w, height=im_h)
        
    tb_fig_cap = slide.shapes.add_textbox(x_right + Cm(0.6), y_card + Cm(6.60), w_right - Cm(1.2), Cm(0.45))
    tf_fig_cap = tb_fig_cap.text_frame
    p_cap = tf_fig_cap.paragraphs[0]
    r_cap = p_cap.add_run()
    format_run(r_cap, "图 2 & 图 3 仿真模拟关键结论（蒙特卡洛验证）", size_pt=11.2, bold=True, color=C_PRIMARY_BLUE)
    
    takeaways = [
        ("1. Wald 正态近似失真", "小规模（m<40）且强超传播（k=0.1）下，渐近正态 Wald 检验一类错误率高达 8.1%（严重虚警）；而离散精确负二项检验全域严格受控于 0.05 以下。"),
        ("2. 超传播惩罚因子", "达到同等 80% 功效所需规模，从弱超传播 k=2.0 飙升至强超传播 k=0.1，所需样本量暴增近 3 倍（流感基准 k=0.35 下 m_80%=142 例）。"),
        ("3. 边际削减规律验证", "式 (400) 证明规模翻倍的方差下降率为 1/[2(1+m/m_×)]。越过平衡点后改善速率断崖式放缓，仿真与解析解 100% 吻合。")
    ]
    y_box = y_card + Cm(7.20)
    h_box = Cm(1.85)
    gap_box = Cm(0.18)
    for tag, body in takeaways:
        add_takeaway_card(slide, x_right + Cm(0.6), y_box, w_right - Cm(1.2), h_box, tag, body)
        y_box += h_box + gap_box
        
    add_takeaway_card(slide, x_right + Cm(0.6), y_card + Cm(13.40), w_right - Cm(1.2), Cm(1.35),
                      "【哨点设计定量判据】",
                      "公卫哨点配置应以满足病原体的 m_80% 为规模上限；超出该规模的预算应转向缩短时滞与多模型集成。",
                      bg_color=C_HIGHLIGHT_BG, border_color=C_HIGHLIGHT_BD)
    sanitize_all_slide_shapes(slide)

print("Slide 5, 6, 7 generators defined.")

# ==============================================================================
# Slide 8: 第五章 经验实证 · 全美 NHSN 流感住院大数据计量检验 (Chapter 5)
# ==============================================================================
def build_slide_8_empirical(slide):
    clear_slide(slide)
    add_header(slide, "06 / 经验实证：全美流感住院大数据计量检验  •  EMPIRICAL FALSIFICATION & NHSN DATA", "全美流感住院实证：理论仿射假说的检验与反转辨析", "08 / 11")
    
    y_card = Cm(2.65)
    card_h = Cm(15.2)
    card_w = Cm(12.8)
    
    # Left Column
    x_left = Cm(1.5)
    create_card(slide, x_left, y_card, card_w, card_h)
    
    tb_l = slide.shapes.add_textbox(x_left + Cm(0.6), y_card + Cm(0.45), card_w - Cm(1.2), Cm(0.55))
    tf_l = tb_l.text_frame
    p_l = tf_l.paragraphs[0]
    r_l = p_l.add_run()
    format_run(r_l, "NHSN 流感住院实证检验与计量模型", size_pt=13.5, bold=True, color=C_PRIMARY_BLUE)
    
    tb_m1 = slide.shapes.add_textbox(x_left + Cm(0.6), y_card + Cm(1.15), card_w - Cm(1.2), Cm(0.45))
    tf_m1 = tb_m1.text_frame
    p_m1 = tf_m1.paragraphs[0]
    r_m1 = p_m1.add_run()
    format_run(r_m1, "• 数据筛选漏斗与 FGLS 可行广义最小二乘模型：", size_pt=11, bold=True, color=C_TEXT_DARK)
    
    add_formula_box(slide, x_left + Cm(0.6), y_card + Cm(1.65), card_w - Cm(1.2), Cm(1.05), "s6_fgls.png")
    
    tb_m2 = slide.shapes.add_textbox(x_left + Cm(0.6), y_card + Cm(2.80), card_w - Cm(1.2), Cm(0.45))
    tf_m2 = tb_m2.text_frame
    p_m2 = tf_m2.paragraphs[0]
    r_m2 = p_m2.add_run()
    format_run(r_m2, "• 流行初期核心估计结果（N = 1,267，1500 次 Bootstrap）：", size_pt=11, bold=True, color=C_TEXT_DARK)
    
    add_formula_box(slide, x_left + Cm(0.6), y_card + Cm(3.35), card_w - Cm(1.2), Cm(1.15), "s6_estimates.png")
    
    create_card(slide, x_left + Cm(0.6), y_card + Cm(4.70), card_w - Cm(1.2), Cm(10.00), fill_color=C_WHITE, border_color=C_CARD_BORDER)
    tb_emp = slide.shapes.add_textbox(x_left + Cm(0.9), y_card + Cm(4.90), card_w - Cm(1.8), Cm(9.60))
    tf_emp = tb_emp.text_frame
    tf_emp.word_wrap = True
    p_e0 = tf_emp.paragraphs[0]
    p_e0.line_spacing = 1.15
    r_e0 = p_e0.add_run()
    format_run(r_e0, "实证核心发现与样本筛选闭环：", size_pt=11.2, bold=True, color=C_PRIMARY_BLUE)
    
    emp_items = [
        ("样本量 N 统计定义与闭环：", "观测单位为‘州—周’。16,218 条原始记录按 D_t ≥ 5 滤除静默周得到 10,303 个活跃观测。三阶段样本 6,009 + 420 + 3,874 = 10,303 算术严密闭环，无覆盖率选择偏误！"),
        ("规模斜率极显著为正：", "b̂ = 2.2434，州聚类 95% CI [1.50, 3.02]，1500 次重抽无一次小于零（p < 10^-4），强力证实 1/D_t 衰减形态，拐点 m_× ≈ 22.6 例/周。"),
        ("达峰期 88.9% 震撼反转：", "看似恒定的 0.3 误差中，整整 88.9% 来源于疫情转折导致的常数基准漂移！扣除偏差后纯条件方差下规模项仍显著为正（b = 7.93），推翻‘达峰期样本量失效’误读！"),
        ("制度冲击与空间汇聚：", "自愿填报期覆盖率骤降（54.6%）诱发尾部方差扩张 192%；全国 51 辖区加总后方差降至 0.0348，验证弱相关空间汇聚收益。")
    ]
    for b_pre, r_txt in emp_items:
        p_it = tf_emp.add_paragraph()
        p_it.space_before = Pt(4)
        p_it.line_spacing = 1.18
        r_b = p_it.add_run()
        format_run(r_b, "• " + b_pre + "\n", size_pt=10, bold=True, color=C_TEXT_DARK)
        r_t = p_it.add_run()
        format_run(r_t, "  " + r_txt, size_pt=9.5, color=C_TEXT_BODY)

    # Right Column: Figure 4 Plot
    x_right = Cm(14.8)
    w_right = Cm(17.57)
    create_card(slide, x_right, y_card, w_right, card_h)
    
    fig_w = Cm(16.5)
    fig_h = Cm(6.80)
    create_card(slide, x_right + Cm(0.53), y_card + Cm(0.40), fig_w, fig_h, fill_color=C_WHITE, border_color=C_CARD_BORDER)
    
    pic_fig4 = os.path.join(FIGURES_DIR, "fig4_empirical_falsification.png")
    if not os.path.exists(pic_fig4):
        pic_fig4 = os.path.join(ASSETS_DIR, "slide_6_pic_3.png")
    if os.path.exists(pic_fig4):
        im = Image.open(pic_fig4)
        aspect = im.size[0] / im.size[1]
        pad_v = Cm(0.12)
        pad_h = Cm(0.20)
        avail_w = fig_w - 2 * pad_h
        avail_h = fig_h - 2 * pad_v
        if avail_w / avail_h > aspect:
            target_h = avail_h
            target_w = target_h * aspect
        else:
            target_w = avail_w
            target_h = target_w / aspect
        p_x = x_right + Cm(0.53) + (fig_w - target_w) / 2
        p_y = y_card + Cm(0.40) + (fig_h - target_h) / 2
        slide.shapes.add_picture(pic_fig4, p_x, p_y, width=target_w, height=target_h)
        
    tb_fig4_cap = slide.shapes.add_textbox(x_right + Cm(0.6), y_card + Cm(7.35), w_right - Cm(1.2), Cm(0.45))
    tf_fig4_cap = tb_fig4_cap.text_frame
    p_cap4 = tf_fig4_cap.paragraphs[0]
    r_cap4 = p_cap4.add_run()
    format_run(r_cap4, "图 4：全美流感住院实证拟合、分箱分布与机制分解", size_pt=11.2, bold=True, color=C_PRIMARY_BLUE)
    
    s8_tag = "【实证检验总结与大论文论证闭环】"
    s8_body = (
        "• 仿射拟合高度显著：FGLS 证实 1/D 衰减项客观存在 (b=2.24 极显著，p<10^-4，平衡点 22.6 例/周)\n"
        "• 达峰机制彻底反转：88.9% 误差由基准漂移解释，控制后规模项仍显著为正，推翻失效误读\n"
        "• 空间汇聚突破底板：全国 51 辖区加总方差降至 0.0348，验证弱相关空间汇聚对偶收益\n"
        "• 严格质量保证：实证完全经受住纯事前筛选与 213 项一致性回归检验，全链条自洽"
    )
    add_takeaway_card(slide, x_right + Cm(0.6), y_card + Cm(7.90), w_right - Cm(1.2), Cm(6.80),
                      s8_tag, s8_body,
                      bg_color=C_HIGHLIGHT_BG, border_color=C_HIGHLIGHT_BD)
    sanitize_all_slide_shapes(slide)

# ==============================================================================
# Slide 9: 第六章 外部扩展 · CDC FluSight 与欧洲 COVID-19 验证 (Chapter 6)
# ==============================================================================
def build_slide_9_external(slide):
    clear_slide(slide)
    add_header(slide, "07 / 外部扩展：跨预测模型与跨病种外部验证  •  EXTERNAL VALIDITY & GENERALIZABILITY", "跨模型与跨病种扩展：从 CDC FluSight 到欧洲 COVID-19", "09 / 11")
    
    y_card = Cm(2.65)
    card_h = Cm(15.2)
    card_w = Cm(15.18)
    
    # Left Column: FluSight CDC Ensemble
    x_left = Cm(1.5)
    create_card(slide, x_left, y_card, card_w, card_h)
    
    tb_l = slide.shapes.add_textbox(x_left + Cm(0.6), y_card + Cm(0.45), card_w - Cm(1.2), Cm(0.55))
    tf_l = tb_l.text_frame
    p_l = tf_l.paragraphs[0]
    r_l = p_l.add_run()
    format_run(r_l, "FluSight CDC 官方前瞻集成预测验证 (N = 1,177)", size_pt=13.5, bold=True, color=C_PRIMARY_BLUE)
    
    tb_fl_sub = slide.shapes.add_textbox(x_left + Cm(0.6), y_card + Cm(1.05), card_w - Cm(1.2), Cm(0.45))
    tf_fl_sub = tb_fl_sub.text_frame
    p_fs = tf_fl_sub.paragraphs[0]
    r_fs = p_fs.add_run()
    format_run(r_fs, "官方前瞻多模型集成预测 • 真实外推视角", size_pt=10, bold=True, color=C_TEXT_MUTED)
    
    create_card(slide, x_left + Cm(0.6), y_card + Cm(1.65), card_w - Cm(1.2), Cm(6.35), fill_color=C_WHITE, border_color=C_CARD_BORDER)
    tb_fl = slide.shapes.add_textbox(x_left + Cm(0.9), y_card + Cm(1.80), card_w - Cm(1.8), Cm(6.05))
    tf_fl = tb_fl.text_frame
    tf_fl.word_wrap = True
    
    fl_items = [
        ("纯事前预测筛选：", "按预测值 c_pred ≥ 5 进行纯事前样本筛选（50 州 + DC），样本量 N = 1,177。"),
        ("规模反比项高度显著：", "b̂ = 7.8045，州聚类 95% CI [5.36, 10.53]，确认实际预测中仍存在规模收益。"),
        ("经验平衡点特征：", "经验拐点 m_× ≈ 60.3 例/周（CI [34.5, 95.9]），与单基准相比右移，反映多模型集成吸收了部分方差。"),
        ("达峰偏差剧烈消除：", "达峰期偏差占比从静态基准的 88.9% 骤降至集成的 15.5%！直接证明多模型集成有效校准了系统均值漂移，为‘达峰期如何提质’提供了铁证！")
    ]
    for i, (b_pre, r_txt) in enumerate(fl_items):
        p_it = tf_fl.paragraphs[0] if i == 0 else tf_fl.add_paragraph()
        if i > 0: p_it.space_before = Pt(3)
        p_it.line_spacing = 1.15
        r_b = p_it.add_run()
        format_run(r_b, "• " + b_pre + "\n", size_pt=10, bold=True, color=C_TEXT_DARK)
        r_t = p_it.add_run()
        format_run(r_t, "  " + r_txt, size_pt=9.4, color=C_TEXT_BODY)
        
    add_takeaway_card(slide, x_left + Cm(0.6), y_card + Cm(8.20), card_w - Cm(1.2), Cm(6.45),
                      "【FluSight 验证对大论文的理论启示】",
                      "FluSight 证明：在真实多模型集成下，规模相关项仍显著为正，且达峰期均值偏差被大幅压制。这从实证上完整支持了大论文的核心建议——跨过特征规模平衡点 m_× 后，监测体系应果断由‘扩充病例数量’转向‘多模型自适应集成与环境协变量矫正’。",
                      bg_color=C_HIGHLIGHT_BG, border_color=C_HIGHLIGHT_BD)

    # Right Column: COVID-19 Europe
    x_right = Cm(17.18)
    create_card(slide, x_right, y_card, card_w, card_h)
    
    tb_r = slide.shapes.add_textbox(x_right + Cm(0.6), y_card + Cm(0.45), card_w - Cm(1.2), Cm(0.55))
    tf_r = tb_r.text_frame
    p_r = tf_r.paragraphs[0]
    r_r = p_r.add_run()
    format_run(r_r, "欧洲 11 国 COVID-19 早期传播跨病种扩展 (N = 404)", size_pt=13.5, bold=True, color=C_PRIMARY_BLUE)
    
    tb_cv_sub = slide.shapes.add_textbox(x_right + Cm(0.6), y_card + Cm(1.05), card_w - Cm(1.2), Cm(0.45))
    tf_cv_sub = tb_cv_sub.text_frame
    p_cs = tf_cv_sub.paragraphs[0]
    r_cs = p_cs.add_run()
    format_run(r_cs, "跨国别跨病种泛化性 • 日度高频监测", size_pt=10, color=C_TEXT_MUTED)
    
    create_card(slide, x_right + Cm(0.6), y_card + Cm(1.65), card_w - Cm(1.2), Cm(6.35), fill_color=C_WHITE, border_color=C_CARD_BORDER)
    tb_cv = slide.shapes.add_textbox(x_right + Cm(0.9), y_card + Cm(1.80), card_w - Cm(1.8), Cm(6.05))
    tf_cv = tb_cv.text_frame
    tf_cv.word_wrap = True
    
    cv_items = [
        ("纯事前有效增长样本：", "基于历史规模 D_t ≥ 5 与 g > 0 纯事前筛选，得到欧洲 11 国共 404 个国家—日观测样本。"),
        ("跨病种规模项坚挺为正：", "b̂ = 33.92，国家聚类 95% CI [14.60, 74.99]，证实了 1/D 衰减规律跨呼吸道病种的普适性。"),
        ("日度尺度平衡点动态性：", "日度尺度经验平衡点为 m_× ≈ 124.7 例/天（截尾与增长期口径分别为 67.7 与 88.1 例/天）。"),
        ("尺度敏感性结论：", "平衡点具体数值依赖于时间粒度（日度 vs 周度）与基本再生数 R0，证明 m_× 应作为量级参照而非固定物理常数。")
    ]
    for i, (b_pre, r_txt) in enumerate(cv_items):
        p_it = tf_cv.paragraphs[0] if i == 0 else tf_cv.add_paragraph()
        if i > 0: p_it.space_before = Pt(3)
        p_it.line_spacing = 1.15
        r_b = p_it.add_run()
        format_run(r_b, "• " + b_pre + "\n", size_pt=10, bold=True, color=C_TEXT_DARK)
        r_t = p_it.add_run()
        format_run(r_t, "  " + r_txt, size_pt=9.4, color=C_TEXT_BODY)
        
    create_card(slide, x_right + Cm(0.6), y_card + Cm(8.20), card_w - Cm(1.2), Cm(6.45), fill_color=C_WHITE, border_color=C_CARD_BORDER)
    tb_pol = slide.shapes.add_textbox(x_right + Cm(0.9), y_card + Cm(8.35), card_w - Cm(1.8), Cm(6.15))
    tf_pol = tb_pol.text_frame
    tf_pol.word_wrap = True
    p_p0 = tf_pol.paragraphs[0]
    p_p0.line_spacing = 1.15
    r_p0 = p_p0.add_run()
    format_run(r_p0, "大论文总结：公共卫生监测资源优化策略矩阵：", size_pt=11.2, bold=True, color=C_PRIMARY_BLUE)
    
    pol_items = [
        ("流行初期 / 低发期 (m < m_×) ——「全力扩量」：", "微观抽样与超传播噪声主导总方差。集中预算扩充哨点网络、提高覆盖率与报告率，迅速压低抽样离散方差。"),
        ("流行达峰 / 高发期 (m > m_×) ——「战略提质」：", "跨过内生平衡点后，总误差进入不可约环境噪声与模型失配主导平台期。单纯增报病例边际收益锐减，果断转向控制协变量与集成预测。"),
        ("爆发早期检测目标 ——「以 m_80% 为哨点基准」：", "在进行爆发假设检验时，按目标病原体超离散度 k 精确测算 m_80%，避免盲目超额配置哨点导致资源闲置与低效。")
    ]
    for b_pre, r_txt in pol_items:
        p_it = tf_pol.add_paragraph()
        p_it.space_before = Pt(3)
        p_it.line_spacing = 1.15
        r_b = p_it.add_run()
        format_run(r_b, b_pre + "\n", size_pt=10, bold=True, color=C_NAVY_DARK)
        r_t = p_it.add_run()
        format_run(r_t, "  " + r_txt, size_pt=9.4, color=C_TEXT_BODY)
    sanitize_all_slide_shapes(slide)

# ==============================================================================
# Slide 10: 进度规划 · 中期研究成果总结与大论文推进计划 (Chapter 7 & Timeline)
# ==============================================================================
def build_slide_10_progress(slide):
    clear_slide(slide)
    add_header(slide, "08 / 进度规划：中期研究成果总结与大论文推进  •  PROGRESS & THESIS TIMELINE", "阶段性成果盘点、大论文撰写推进与时间里程碑", "10 / 11")
    
    y_card = Cm(2.65)
    card_h = Cm(15.2)
    card_w = Cm(15.18)
    
    # Left Column: Research Achievements
    x_left = Cm(1.5)
    create_card(slide, x_left, y_card, card_w, card_h)
    
    tb_l = slide.shapes.add_textbox(x_left + Cm(0.6), y_card + Cm(0.45), card_w - Cm(1.2), Cm(0.6))
    tf_l = tb_l.text_frame
    p_l = tf_l.paragraphs[0]
    r_l = p_l.add_run()
    format_run(r_l, "阶段性成果盘点与核心工作储备", size_pt=14, bold=True, color=C_PRIMARY_BLUE)
    
    achievements = [
        ("数学理论与运筹闭环 (100%)", "已完成分支过程、双层抽样、渐近 CRLB、命题 1~6 及 Cochran 抽样对偶全套闭式解推导，数学证明无缺漏。"),
        ("随机仿真与验证套件 (100%)", "开发完整蒙特卡洛仿真框架，图 1~3 全部代码开源可复现，验证了解析解紧致性与双口径预测机制。"),
        ("真实世界三大实证数据库 (100%)", "完成全美 16,218 条流感住院、CDC FluSight 集成预测及欧洲 11 国 COVID-19 数据清洗与 213 项数字回归检验。"),
        ("小论文成果与学术认可 (100%)", "已形成 28 页高水平期刊定稿论文，通过多轮严苛学术评审打磨，获 8.9/10 高分评价，奠定大论文坚实核心。")
    ]
    y_ac = y_card + Cm(1.25)
    for title, desc in achievements:
        card_a = create_card(slide, x_left + Cm(0.5), y_ac, card_w - Cm(1.0), Cm(2.3), fill_color=C_WHITE, border_color=C_CARD_BORDER)
        tb_a = slide.shapes.add_textbox(x_left + Cm(0.7), y_ac + Cm(0.15), card_w - Cm(1.4), Cm(2.0))
        tf_a = tb_a.text_frame
        tf_a.word_wrap = True
        
        p1 = tf_a.paragraphs[0]
        r1 = p1.add_run()
        format_run(r1, "✓  " + title, size_pt=11.5, bold=True, color=C_PRIMARY_BLUE)
        
        p2 = tf_a.add_paragraph()
        p2.space_before = Pt(3)
        p2.line_spacing = 1.2
        r2 = p2.add_run()
        format_run(r2, desc, size_pt=9.5, color=C_TEXT_BODY)
        y_ac += Cm(2.45)
        
    add_takeaway_card(slide, x_left + Cm(0.5), y_card + Cm(11.25), card_w - Cm(1.0), Cm(3.45),
                      "【工作量总体自评】",
                      "课题研究内容已全部完成并获得多场景严格验证，当前工作重心为按照硕士学位论文标准，系统扩充文献综述深度、补充理论推导中间过程与公卫资源优化量化细则，大论文撰写准备工作极其充分。",
                      bg_color=C_HIGHLIGHT_BG, border_color=C_HIGHLIGHT_BD)

    # Right Column: Big Thesis Expansion Plan & Milestones
    x_right = Cm(17.18)
    create_card(slide, x_right, y_card, card_w, card_h)
    
    tb_r = slide.shapes.add_textbox(x_right + Cm(0.6), y_card + Cm(0.45), card_w - Cm(1.2), Cm(0.6))
    tf_r = tb_r.text_frame
    p_r = tf_r.paragraphs[0]
    r_r = p_r.add_run()
    format_run(r_r, "80 页大论文扩充撰写规划与毕业时间表", size_pt=14, bold=True, color=C_PRIMARY_BLUE)
    
    plans = [
        ("第一章 绪论全面扩写 (12~14 页)", "梳理从 Kermack–McKendrick 到 EpiEstim 与 Parag 的百年再生数估计演进史，建立完整的既有模型对比矩阵。"),
        ("第二、三章 数学推导教科书化 (30 页)", "全面展开 Gamma 换元积分、PGF 复合、得分求导、错位相减级数求和与 Cochran 对偶证明，达到教材级可读性。"),
        ("第五、七章 空间政策与建议深化 (22 页)", "补充 50 州流感时空热力图、制度切换微观机制分析，并设计针对 CDC 的两阶段分步监测资源配置落地手册。")
    ]
    y_pl = y_card + Cm(1.25)
    for title, desc in plans:
        card_p = create_card(slide, x_right + Cm(0.5), y_pl, card_w - Cm(1.0), Cm(2.4), fill_color=C_WHITE, border_color=C_CARD_BORDER)
        tb_p = slide.shapes.add_textbox(x_right + Cm(0.7), y_pl + Cm(0.15), card_w - Cm(1.4), Cm(2.1))
        tf_p = tb_p.text_frame
        tf_p.word_wrap = True
        
        p1 = tf_p.paragraphs[0]
        r1 = p1.add_run()
        format_run(r1, "★  " + title, size_pt=11.5, bold=True, color=C_TEXT_DARK)
        
        p2 = tf_p.add_paragraph()
        p2.space_before = Pt(3)
        p2.line_spacing = 1.2
        r2 = p2.add_run()
        format_run(r2, desc, size_pt=9.5, color=C_TEXT_BODY)
        y_pl += Cm(2.55)
        
    create_card(slide, x_right + Cm(0.5), y_card + Cm(9.1), card_w - Cm(1.0), Cm(5.6), fill_color=C_WHITE, border_color=C_CARD_BORDER)
    tb_time = slide.shapes.add_textbox(x_right + Cm(0.8), y_card + Cm(9.3), card_w - Cm(1.6), Cm(5.2))
    tf_time = tb_time.text_frame
    tf_time.word_wrap = True
    p_t0 = tf_time.paragraphs[0]
    p_t0.line_spacing = 1.15
    r_t0 = p_t0.add_run()
    format_run(r_t0, "后续研究与毕业时间节点里程碑：", size_pt=12, bold=True, color=C_PRIMARY_BLUE)
    
    milestones = [
        ("2026 年 10 月", "通过硕士学位论文中期考核答辩，听取专家修改意见；"),
        ("2026 年 11 月", "完成大论文初稿全部七章撰写（80~85 页），提交导师审阅；"),
        ("2026 年 12 月", "完成初稿修订并进行查重预检，参加硕士学位论文预答辩；"),
        ("2027 年 01~03 月", "论文送审盲审评阅，根据评审专家意见完成最终定稿；"),
        ("2027 年 04~05 月", "参加硕士研究生学位论文正式答辩，完成学位申请。")
    ]
    for date_str, task_str in milestones:
        p_m = tf_time.add_paragraph()
        p_m.space_before = Pt(3)
        p_m.line_spacing = 1.15
        r_d = p_m.add_run()
        format_run(r_d, "• " + date_str + "：", size_pt=10, bold=True, color=C_TEXT_DARK)
        r_t = p_m.add_run()
        format_run(r_t, task_str, size_pt=9.5, color=C_TEXT_BODY)
    sanitize_all_slide_shapes(slide)

# ==============================================================================
# Slide 11: 封底致谢页 (Acknowledgements Page)
# ==============================================================================
def build_slide_11_thanks(slide):
    clear_slide(slide)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Cm(33.87), Cm(19.05))
    bg.fill.solid()
    bg.fill.fore_color.rgb = C_COVER_BG
    bg.line.fill.background()

    tb_main = slide.shapes.add_textbox(Cm(2.5), Cm(5.5), Cm(28.87), Cm(2.2))
    tf_main = tb_main.text_frame
    p_main = tf_main.paragraphs[0]
    p_main.alignment = PP_ALIGN.CENTER
    r_main = p_main.add_run()
    format_run(r_main, "感谢各位专家评委老师的悉心指导！", size_pt=36, bold=True, color=C_WHITE)

    tb_sub = slide.shapes.add_textbox(Cm(2.5), Cm(8.2), Cm(28.87), Cm(1.2))
    tf_sub = tb_sub.text_frame
    p_sub = tf_sub.paragraphs[0]
    p_sub.alignment = PP_ALIGN.CENTER
    r_sub = p_sub.add_run()
    format_run(r_sub, "敬请各位老师批评指正  •  Q & A", size_pt=22, bold=True, color=C_LIGHT_BLUE)

    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Cm(10.0), Cm(10.2), Cm(13.87), Pt(1.5))
    line.fill.solid()
    line.fill.fore_color.rgb = RGBColor(51, 65, 85)
    line.line.fill.background()

    tb_foot = slide.shapes.add_textbox(Cm(2.5), Cm(11.2), Cm(28.87), Cm(1.5))
    tf_foot = tb_foot.text_frame
    p_foot = tf_foot.paragraphs[0]
    p_foot.alignment = PP_ALIGN.CENTER
    r_foot = p_foot.add_run()
    format_run(r_foot, "硕士学位论文中期考核进展汇报  |  应用统计专业 (MAS)\n课题：《疫情监测中的病例规模收益边界：估计目标、环境随机性与外部验证》", size_pt=12.5, color=RGBColor(148, 163, 184))
    sanitize_all_slide_shapes(slide)

# ==============================================================================
# Main Builder Execution
# ==============================================================================
def main():
    print(f"Loading presentation template: {INPUT_PPTX}...")
    prs = pptx.Presentation(INPUT_PPTX)
    
    # Ensure there are at least 11 slides
    blank_layout = prs.slide_layouts[6]
    while len(prs.slides) < 11:
        prs.slides.add_slide(blank_layout)
        
    print(f"Total slides in presentation: {len(prs.slides)}. Building all 11 slides...")
    
    print("Building Slide 1: 正式封面...")
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
    build_slide_11_thanks(prs.slides[10])
    
    print(f"Saving to {OUTPUT_PPTX}...")
    prs.save(OUTPUT_PPTX)
    
    print(f"Synchronizing to root: {OUTPUT_PPTX_ROOT}...")
    shutil.copyfile(OUTPUT_PPTX, OUTPUT_PPTX_ROOT)
    
    print("SUCCESS: 11-slide Master's Defense Presentation fully built!")

if __name__ == "__main__":
    main()
