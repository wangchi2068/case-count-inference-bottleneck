# -*- coding: utf-8 -*-
with open(r'D:\trae\paper_final\build_master_defense_presentation.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Locate line 1088: fig_w = Cm(16.5)
# and line 1122: sanitize_all_slide_shapes(slide)
start_idx = None
end_idx = None

for i in range(1050, 1130):
    if i < len(lines):
        if 'fig_w = Cm(16.5)' in lines[i]:
            start_idx = i
        if start_idx is not None and 'sanitize_all_slide_shapes(slide)' in lines[i]:
            end_idx = i
            break

print(f"start_idx: {start_idx+1}, end_idx: {end_idx+1}")

replacement = [
    '    fig_w = Cm(16.5)\n',
    '    fig_h = Cm(6.80)\n',
    '    create_card(slide, x_right + Cm(0.53), y_card + Cm(0.40), fig_w, fig_h, fill_color=C_WHITE, border_color=C_CARD_BORDER)\n',
    '    \n',
    '    pic_fig4 = os.path.join(FIGURES_DIR, "fig4_empirical_falsification.png")\n',
    '    if not os.path.exists(pic_fig4):\n',
    '        pic_fig4 = os.path.join(ASSETS_DIR, "slide_6_pic_3.png")\n',
    '    if os.path.exists(pic_fig4):\n',
    '        im = Image.open(pic_fig4)\n',
    '        aspect = im.size[0] / im.size[1]\n',
    '        pad_v = Cm(0.12)\n',
    '        pad_h = Cm(0.20)\n',
    '        avail_w = fig_w - 2 * pad_h\n',
    '        avail_h = fig_h - 2 * pad_v\n',
    '        if avail_w / avail_h > aspect:\n',
    '            target_h = avail_h\n',
    '            target_w = target_h * aspect\n',
    '        else:\n',
    '            target_w = avail_w\n',
    '            target_h = target_w / aspect\n',
    '        p_x = x_right + Cm(0.53) + (fig_w - target_w) / 2\n',
    '        p_y = y_card + Cm(0.40) + (fig_h - target_h) / 2\n',
    '        slide.shapes.add_picture(pic_fig4, p_x, p_y, width=target_w, height=target_h)\n',
    '        \n',
    '    tb_fig4_cap = slide.shapes.add_textbox(x_right + Cm(0.6), y_card + Cm(7.35), w_right - Cm(1.2), Cm(0.45))\n',
    '    tf_fig4_cap = tb_fig4_cap.text_frame\n',
    '    p_cap4 = tf_fig4_cap.paragraphs[0]\n',
    '    r_cap4 = p_cap4.add_run()\n',
    '    format_run(r_cap4, "图 4：全美流感住院实证拟合、分箱分布与机制分解", size_pt=11.2, bold=True, color=C_PRIMARY_BLUE)\n',
    '    \n',
    '    s8_tag = "【实证检验总结与大论文论证闭环】"\n',
    '    s8_body = (\n',
    '        "• 仿射拟合高度显著：FGLS 证实 1/D 衰减项客观存在 (b=2.24 极显著，p<10^-4，平衡点 22.6 例/周)\\n"\n',
    '        "• 达峰机制彻底反转：88.9% 误差由基准漂移解释，控制后规模项仍显著为正，推翻失效误读\\n"\n',
    '        "• 空间汇聚突破底板：全国 51 辖区加总方差降至 0.0348，验证弱相关空间汇聚对偶收益\\n"\n',
    '        "• 严格质量保证：实证完全经受住纯事前筛选与 213 项一致性回归检验，全链条自洽"\n',
    '    )\n',
    '    add_takeaway_card(slide, x_right + Cm(0.6), y_card + Cm(7.90), w_right - Cm(1.2), Cm(6.80),\n',
    '                      s8_tag, s8_body,\n',
    '                      bg_color=C_HIGHLIGHT_BG, border_color=C_HIGHLIGHT_BD)\n',
    '    sanitize_all_slide_shapes(slide)\n'
]

lines = lines[:start_idx] + replacement + lines[end_idx+1:]

with open(r'D:\trae\paper_final\build_master_defense_presentation.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Slide 8 successfully replaced with perfectly spaced layout!")
