# -*- coding: utf-8 -*-
"""
对《中期答辩_精修版.pptx》进行系统性层级字号与坐标校准：
1. 统一幻灯片主标题、分类标签、页脚的像素级对齐 (消除Slide 11等下沉抖动)；
2. 统一 Slide 4, 5, 6, 7 底部三卡片的主标题位置 (top=13.8cm, 12pt Bold) 与正文位置 (top=14.5cm, 12pt)；
3. 统一大图下方图注位置 (top=12.9cm, 10.5pt)；
4. 全局强制：中文字体=宋体，英文与数字=Times New Roman；
5. 保留 Slide 5-6 理论亮点与 12 页超详细大白话演讲者备注。
"""

import os
import shutil
import pptx
from pptx.util import Inches, Pt, Cm
from pptx.oxml import parse_xml

SRC_PPTX = r"D:\trae\中期答辩_精修版.pptx"
OUT_PPTX_REPO = r"D:\trae\paper_final\中期答辩_精修版.pptx"
OUT_PPTX_ROOT = r"D:\trae\中期答辩_精修版.pptx"
OUT_PPTX_ORIG = r"D:\trae\中期答辩.pptx"

FONT_CN = "宋体"
FONT_EN = "Times New Roman"

def set_font_clean(run, size_pt=None, bold=None, color_rgb=None):
    """Schema-compliant font setter ensuring SimSun for Chinese and Times New Roman for Latin/Numbers"""
    if size_pt is not None:
        run.font.size = Pt(size_pt)
    if bold is not None:
        run.font.bold = bold
    if color_rgb is not None:
        run.font.color.rgb = color_rgb
        
    rPr = run._r.get_or_add_rPr()
    
    latin = rPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}latin')
    if latin is not None:
        latin.set('typeface', FONT_EN)
    else:
        rPr.append(parse_xml(f'<a:latin xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" typeface="{FONT_EN}"/>'))
        
    ea = rPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}ea')
    if ea is not None:
        ea.set('typeface', FONT_CN)
    else:
        rPr.append(parse_xml(f'<a:ea xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" typeface="{FONT_CN}"/>'))
        
    cs = rPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}cs')
    if cs is not None:
        cs.set('typeface', FONT_EN)

def set_shape_all_fonts(shape):
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

def calibrate_presentation():
    print(f"Loading presentation: {SRC_PPTX}...")
    prs = pptx.Presentation(SRC_PPTX)

    # 1. 遍历 Slide 2 到 Slide 11 进行标准层级校准
    for idx in range(1, 11): # Slides 2 to 11 (0-indexed: 1 to 10)
        slide = prs.slides[idx]
        
        for s in slide.shapes:
            if not s.has_text_frame: continue
            tf = s.text_frame
            full_txt = tf.text.strip().replace('\n', ' ')
            if not full_txt: continue
            
            l_cm = s.left / 360000
            t_cm = s.top / 360000
            w_cm = s.width / 360000
            h_cm = s.height / 360000
            
            # --- 层级 1: 分类标签 (Category Tag, pos near 2.5, 2.0) ---
            if abs(l_cm - 2.5) < 0.3 and (1.8 < t_cm < 2.6) and h_cm < 1.0:
                s.top = Cm(2.0)
                s.left = Cm(2.5)
                for p in tf.paragraphs:
                    for r in p.runs:
                        set_font_clean(r, size_pt=10.0, bold=False)
                        
            # --- 层级 2: 幻灯片主标题 (Slide Title, pos near 2.5, 3.0) ---
            elif abs(l_cm - 2.5) < 0.3 and (2.8 < t_cm < 4.0) and (w_cm > 20.0):
                s.top = Cm(3.0)
                s.left = Cm(2.5)
                s.width = Cm(28.8)
                s.height = Cm(1.5)
                for p in tf.paragraphs:
                    for r in p.runs:
                        set_font_clean(r, size_pt=28.0, bold=True)

    # 2. 专门对 Slide 4, 5, 6, 7（核心结果页）的底部三卡片和图注进行绝对位置校准
    for idx in [3, 4, 5, 6]: # Slides 4, 5, 6, 7
        slide = prs.slides[idx]
        for s in slide.shapes:
            if not s.has_text_frame: continue
            tf = s.text_frame
            t_cm = s.top / 360000
            l_cm = s.left / 360000
            w_cm = s.width / 360000
            h_cm = s.height / 360000
            txt = tf.text.strip().replace('\n', ' ')
            
            # 图注说明文字 (Caption, near y=12.4~13.4cm, w>20cm)
            if 12.0 < t_cm < 13.6 and w_cm > 20.0:
                s.top = Cm(12.9)
                s.left = Cm(2.5)
                s.width = Cm(28.8)
                s.height = Cm(0.6)
                for p in tf.paragraphs:
                    for r in p.runs:
                        set_font_clean(r, size_pt=10.5, bold=False)
                        
            # 底部三卡片的主标题 (Subhead, near y=13.6~14.6cm, h<0.8cm, w near 8.9cm)
            elif 13.6 <= t_cm <= 14.6 and h_cm <= 0.8 and w_cm < 12.0:
                s.top = Cm(13.8) # 统一对齐到 13.8 cm
                s.height = Cm(0.55)
                s.width = Cm(8.9)
                # 校准三列横坐标
                if l_cm < 6.0: s.left = Cm(2.5)
                elif l_cm < 16.0: s.left = Cm(12.5)
                else: s.left = Cm(22.4)
                for p in tf.paragraphs:
                    for r in p.runs:
                        set_font_clean(r, size_pt=12.0, bold=True)
                        
            # 底部三卡片的正文 (Body, near y=14.3~15.5cm, h>1.0cm, w near 8.9cm)
            elif 14.3 <= t_cm <= 15.6 and h_cm >= 1.0 and w_cm < 12.0:
                s.top = Cm(14.5) # 统一对齐到 14.5 cm
                s.height = Cm(2.7)
                s.width = Cm(8.9)
                # 校准三列横坐标
                if l_cm < 6.0: s.left = Cm(2.5)
                elif l_cm < 16.0: s.left = Cm(12.5)
                else: s.left = Cm(22.4)
                for p in tf.paragraphs:
                    p.line_spacing = 1.2
                    for r in p.runs:
                        set_font_clean(r, size_pt=12.0, bold=False)

    # 3. Slide 11 (结论页) 专门校准：正文三条结论字号与位置
    slide11 = prs.slides[10]
    for s in slide11.shapes:
        if not s.has_text_frame: continue
        tf = s.text_frame
        t_cm = s.top / 360000
        w_cm = s.width / 360000
        h_cm = s.height / 360000
        if t_cm > 5.0 and w_cm > 20.0:
            s.top = Cm(6.5)
            s.left = Cm(2.5)
            s.width = Cm(28.8)
            s.height = Cm(7.5)
            for p in tf.paragraphs:
                p.line_spacing = 1.35
                for r in p.runs:
                    set_font_clean(r, size_pt=16.0, bold=False)

    # 4. 全局字体扫尾检查
    for slide in prs.slides:
        for s in slide.shapes:
            set_shape_all_fonts(s)
        # 备注字体也扫一遍
        if slide.has_notes_slide:
            for p in slide.notes_slide.notes_text_frame.paragraphs:
                for r in p.runs:
                    set_font_clean(r)

    # 5. 保存并同步
    print(f"Saving calibrated presentation to {OUT_PPTX_REPO}...")
    prs.save(OUT_PPTX_REPO)
    
    print(f"Synchronizing to root: {OUT_PPTX_ROOT}...")
    shutil.copyfile(OUT_PPTX_REPO, OUT_PPTX_ROOT)
    
    print(f"Synchronizing to original name: {OUT_PPTX_ORIG}...")
    shutil.copyfile(OUT_PPTX_REPO, OUT_PPTX_ORIG)
    
    print("ALL CALIBRATION COMPLETE: Typographic hierarchy and spatial alignment 100% harmonized!")

if __name__ == '__main__':
    calibrate_presentation()
