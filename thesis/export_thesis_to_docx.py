
def set_font_eastasia(run, font_name):
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    rFonts.set(qn('w:eastAsia'), font_name)
# -*- coding: utf-8 -*-
"""
Export 85-page Master Thesis to Word DOCX format
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def export_docx():
    doc = docx.Document()
    
    # Page setup: A4
    for section in doc.sections:
        section.top_margin = Inches(1.18)    # 3.0 cm
        section.bottom_margin = Inches(0.98) # 2.5 cm
        section.left_margin = Inches(1.18)   # 3.0 cm
        section.right_margin = Inches(0.98)  # 2.5 cm
        
    # Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    normal_style.paragraph_format.line_spacing = 1.35
    normal_style.paragraph_format.space_after = Pt(2)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t = p_title.add_run("硕 士 学 位 论 文\n\n疫情监测中的病例规模收益边界：\n估计目标、环境随机性与外部验证\n")
    r_t.font.size = Pt(22)
    r_t.font.bold = True
    r_t.font.color.rgb = RGBColor(15, 23, 42)
    set_font_eastasia(r_t, '黑体')
    
    p_en = doc.add_paragraph()
    p_en.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_en = p_en.add_run("Boundaries of Surveillance Scale Returns in Epidemic Monitoring:\nEstimation Targets, Environmental Stochasticity, and External Validation\n\n")
    r_en.font.size = Pt(13)
    r_en.font.italic = True
    r_en.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_page_break()

    # Chapters to include
    tex_files = [
        ("第一章 绪论", "D:/trae/thesis_master/chapters/ch1_introduction.tex"),
        ("第二章 动力学建模与观测机制", "D:/trae/thesis_master/chapters/ch2_micro_mechanism.tex"),
        ("第三章 统计推断与运筹优化理论", "D:/trae/thesis_master/chapters/ch3_asymptotic_theory.tex"),
        ("第四章 蒙特卡洛数值模拟与机制检验", "D:/trae/thesis_master/chapters/ch4_numerical_simulations.tex"),
        ("第五章 全美流感住院大数据实证分析", "D:/trae/thesis_master/chapters/ch5_empirical_nhsn.tex"),
        ("第六章 跨模型与跨病种外部扩展验证", "D:/trae/thesis_master/chapters/ch6_external_validation.tex"),
        ("第七章 监测资源优化策略与研究展望", "D:/trae/thesis_master/chapters/ch7_resource_optimization.tex"),
        ("附录 A 数学命题保姆级代数推导补充", "D:/trae/thesis_master/appendix/app_proofs.tex"),
        ("附录 B 核心模拟与计量回归 Python 源码清单", "D:/trae/thesis_master/appendix/app_codes.tex"),
    ]

    import re

    for ch_title, file_path in tex_files:
        if not os.path.exists(file_path): continue
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        p_ch = doc.add_paragraph()
        p_ch.paragraph_format.space_before = Pt(18)
        p_ch.paragraph_format.space_after = Pt(12)
        r_ch = p_ch.add_run(ch_title)
        r_ch.font.size = Pt(18)
        r_ch.font.bold = True
        r_ch.font.color.rgb = RGBColor(30, 58, 138)
        set_font_eastasia(r_ch, '黑体')

        in_lst = False
        for line in lines:
            text = line.strip()
            if not text: continue
            if text.startswith(r'\chapter') or text.startswith(r'\begin{document}') or text.startswith(r'\end{document}'):
                continue
            if text.startswith(r'\begin{lstlisting}'):
                in_lst = True
                continue
            if text.startswith(r'\end{lstlisting}'):
                in_lst = False
                continue
                
            if in_lst:
                p_code = doc.add_paragraph()
                p_code.paragraph_format.left_indent = Inches(0.2)
                p_code.paragraph_format.line_spacing = 1.0
                r_c = p_code.add_run(text)
                r_c.font.name = 'Consolas'
                r_c.font.size = Pt(9.5)
                r_c.font.color.rgb = RGBColor(30, 41, 59)
                continue

            # Heading 1 (\section)
            if text.startswith(r'\section{'):
                m = re.search(r'\\section\{([^}]+)\}', text)
                if m:
                    h1 = doc.add_paragraph()
                    h1.paragraph_format.space_before = Pt(14)
                    h1.paragraph_format.space_after = Pt(6)
                    r_h1 = h1.add_run(m.group(1))
                    r_h1.font.size = Pt(15)
                    r_h1.font.bold = True
                    r_h1.font.color.rgb = RGBColor(15, 23, 42)
                    set_font_eastasia(r_h1, '黑体')
                continue

            # Heading 2 (\subsection)
            if text.startswith(r'\subsection{'):
                m = re.search(r'\\subsection\{([^}]+)\}', text)
                if m:
                    h2 = doc.add_paragraph()
                    h2.paragraph_format.space_before = Pt(10)
                    h2.paragraph_format.space_after = Pt(4)
                    r_h2 = h2.add_run(m.group(1))
                    r_h2.font.size = Pt(13)
                    r_h2.font.bold = True
                    r_h2.font.color.rgb = RGBColor(30, 41, 59)
                    set_font_eastasia(r_h2, '黑体')
                continue

            # Clean simple LaTeX tags
            clean_text = text
            clean_text = re.sub(r'\\cite[pt]?\{[^}]+\}', '[文献]', clean_text)
            clean_text = re.sub(r'\\ref\{[^}]+\}', '[图表]', clean_text)
            clean_text = re.sub(r'\\eqref\{[^}]+\}', '[公式]', clean_text)
            clean_text = re.sub(r'\\textbf\{([^}]+)\}', r'\1', clean_text)
            clean_text = re.sub(r'\\textit\{([^}]+)\}', r'\1', clean_text)
            clean_text = re.sub(r'\\emph\{([^}]+)\}', r'\1', clean_text)
            clean_text = clean_text.replace(r'\%', '%').replace(r'\&', '&').replace(r'\_', '_').replace(r'\dots', '...')
            
            if clean_text.startswith(r'\begin') or clean_text.startswith(r'\end') or clean_text.startswith(r'\caption') or clean_text.startswith(r'\label'):
                continue

            # Regular paragraph
            p = doc.add_paragraph()
            p.paragraph_format.first_line_indent = Inches(0.3)
            r = p.add_run(clean_text)
            r.font.size = Pt(12)
            
        doc.add_page_break()

    out_docx = "D:/trae/thesis_master/硕士学位大论文_定稿_85页.docx"
    doc.save(out_docx)
    print("Exported DOCX successfully to:", out_docx)
    
    out_root = "D:/trae/硕士学位大论文_定稿_85页.docx"
    doc.save(out_root)
    print("Exported root DOCX successfully to:", out_root)

if __name__ == '__main__':
    export_docx()
