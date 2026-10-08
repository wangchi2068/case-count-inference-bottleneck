"""
Automated consistency checker between paper manuscript, DOCX, and empirical_stats.json.
Validates that numbers reported in paper/main.tex match simulations/empirical_stats.json,
and verifies text hygiene in DOCX and Markdown documents.
"""
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

def check_all():
    errors = []
    
    # 1. Load empirical_stats.json
    with open('simulations/empirical_stats.json', 'r', encoding='utf-8') as f:
        stats = json.load(f)
        
    # Check interaction CI
    ci_joint = stats['stage_scale_audit']['ols_joint_interaction_ci']
    ci_lower = round(ci_joint[0], 2)
    ci_upper = round(ci_joint[1], 2)
    print(f"[OK] JSON stage interaction CI: [{ci_joint[0]:.4f}, {ci_joint[1]:.4f}] -> formatted [{ci_lower:.2f}, {ci_upper:.2f}]")
    if ci_lower != -2.33 or ci_upper != 0.59:
        errors.append(f"Interaction CI rounded to 2 decimals expected [-2.33, 0.59], got [{ci_lower}, {ci_upper}]")
        
    # Check iv_subsample_mean_g
    iv_mean_g = stats['stage_scale_audit']['iv_subsample_mean_g']
    if round(iv_mean_g, 4) != 1.6266:
        errors.append(f"iv_subsample_mean_g expected 1.6266, got {iv_mean_g}")
    else:
        print(f"[OK] iv_subsample_mean_g: {iv_mean_g:.4f}")

    # 2. Check paper/main.tex
    with open('paper/main.tex', 'r', encoding='utf-8') as f:
        tex = f.read()
        
    if "[-2.33, 0.59]" not in tex:
        errors.append("paper/main.tex missing formatted interaction CI [-2.33, 0.59]")
    else:
        print("[OK] paper/main.tex contains [-2.33, 0.59]")
        
    if "[-2.2702, 0.6261]" in tex:
        errors.append("paper/main.tex still contains stale interaction CI [-2.2702, 0.6261]")
        
    if "强稳健性对照" in tex:
        errors.append("paper/main.tex still contains '强稳健性对照'")
        
    if "这种相容性表明两者在数量级上具有理论机制的一致性" in tex:
        errors.append("paper/main.tex still contains over-reading mechanism sentence")
        
    # 3. Check propositions_and_proofs.md for non-printing control characters
    with open('theory/propositions_and_proofs.md', 'rb') as f:
        raw_theory = f.read()
    bad_bytes = [b for b in raw_theory if 0 <= b <= 8 or b == 11 or b == 12 or 14 <= b <= 31]
    if bad_bytes:
        errors.append(f"theory/propositions_and_proofs.md contains {len(bad_bytes)} non-printing control bytes: {bad_bytes}")
    else:
        print("[OK] theory/propositions_and_proofs.md is clean of non-printing control bytes")

    # 4. Check paper/main_docx.docx
    try:
        with zipfile.ZipFile('paper/main_docx.docx', 'r') as zf:
            xml_content = zf.read('word/document.xml').decode('utf-8')
            
        banned_docx = [
            "证实了规模效应的强稳健性",
            "极显著排除零点",
            "强稳健性对照",
            "[-2.2702, 0.6261]",
            "信度比等于0.5的理论锚点"
        ]
        for phrase in banned_docx:
            if phrase in xml_content:
                errors.append(f"main_docx.docx still contains banned phrase: '{phrase}'")
            else:
                print(f"[OK] main_docx.docx free of '{phrase}'")
                
        if "[-2.33, 0.59]" not in xml_content:
            errors.append("main_docx.docx missing formatted interaction CI [-2.33, 0.59]")
        else:
            print("[OK] main_docx.docx contains [-2.33, 0.59]")
            
    except Exception as e:
        errors.append(f"Error checking main_docx.docx: {e}")

    # Summary
    if errors:
        print("\nFAILED: Discrepancies detected:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("\nALL CONSISTENCY AND HYGIENE CHECKS PASSED!")

if __name__ == '__main__':
    check_all()
