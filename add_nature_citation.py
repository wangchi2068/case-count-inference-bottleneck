# -*- coding: utf-8 -*-
with open(r'D:\trae\paper_final\build_master_defense_presentation.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Slide 4 section 1 title with Nature 2005 citation
old_s4_m1_title = 'format_run(r_m1, "• 第一阶段：微观传播层（负二项分支过程）", size_pt=11.2, bold=True, color=C_TEXT_DARK)'
new_s4_m1_title = 'format_run(r_m1, "• 第一阶段：微观传播层（负二项分支过程） [Lloyd-Smith et al., Nature 2005]", size_pt=10.6, bold=True, color=C_TEXT_DARK)'

if old_s4_m1_title in text:
    text = text.replace(old_s4_m1_title, new_s4_m1_title, 1)
    print("Slide 4: Added Nature 2005 citation to section 1 header!")
else:
    print("Slide 4 header pattern not found directly, checking...")

# 2. Update Slide 4 bio item
old_s4_bio = '("方差均值比（离散指数）：", "Var(Y) / E[Y] = 1 + Rt / k > 1，体现极强超离散特征。")'
new_s4_bio = '("方差均值比与超传播：", "Var(Y) / E[Y] = 1 + Rt / k > 1，Lloyd-Smith 等 (Nature 2005) 证实病原体普遍具备强过度离散。")'

if old_s4_bio in text:
    text = text.replace(old_s4_bio, new_s4_bio, 1)
    print("Slide 4: Added Nature 2005 citation to bio item!")

# 3. Update Slide 3 section 2
old_s3_bio = '1. 微观生物学超传播： 极少数个体引发绝大多数二次感染（负二项分布重尾特征与强过度离散，k ≪ 1）；'
new_s3_bio = '1. 微观生物学超传播： 极少数个体引发绝大多数二次感染 (负二项分布重尾特征，k ≪ 1, Lloyd-Smith et al., Nature 2005)；'

if old_s3_bio in text:
    text = text.replace(old_s3_bio, new_s3_bio, 1)
    print("Slide 3: Added Nature 2005 citation to motivation!")

with open(r'D:\trae\paper_final\build_master_defense_presentation.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("build_master_defense_presentation.py successfully updated with Lloyd-Smith (Nature 2005)!")
