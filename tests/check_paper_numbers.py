"""
Automated consistency and regression verification suite.
Validates numbers reported in paper/main.tex against simulations/empirical_stats.json,
checks bibliography 1:1 DOI alignment between DOCX and references.bib,
and enforces text and mathematical hygiene across all deliverable documents.
"""
import json
import os
import re
import sys
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def p(*args):
    return os.path.join(ROOT, *args)

def check_all():
    errors = []
    print(f"Running consistency suite from ROOT: {ROOT}")
    
    # 1. Load empirical_stats.json
    stats_path = p('simulations', 'empirical_stats.json')
    with open(stats_path, 'r', encoding='utf-8') as f:
        stats = json.load(f)
        
    ci_joint = stats['stage_scale_audit']['ols_joint_interaction_ci']
    ci_lower = round(ci_joint[0], 2)
    ci_upper = round(ci_joint[1], 2)
    print(f"[OK] JSON stage interaction CI: [{ci_joint[0]:.4f}, {ci_joint[1]:.4f}] -> formatted [{ci_lower:.2f}, {ci_upper:.2f}]")
    if ci_lower != -2.33 or ci_upper != 0.59:
        errors.append(f"Interaction CI rounded to 2 decimals expected [-2.33, 0.59], got [{ci_lower}, {ci_upper}]")
        
    iv_mean_g = stats['stage_scale_audit']['iv_subsample_mean_g']
    if round(iv_mean_g, 4) != 1.6266:
        errors.append(f"iv_subsample_mean_g expected 1.6266, got {iv_mean_g}")
    else:
        print(f"[OK] iv_subsample_mean_g matches: {iv_mean_g:.4f}")

    # Check FGLS main fit numbers
    a_fit = stats['early']['affine']['a']
    b_fit = stats['early']['affine']['b']
    mx_fit = stats['early']['affine']['m_x']
    if round(a_fit, 4) != 0.0991 or round(b_fit, 4) != 2.2434 or round(mx_fit, 1) != 22.6:
        errors.append(f"Main fit numbers unexpected: a={a_fit}, b={b_fit}, m_x={mx_fit}")
    else:
        print(f"[OK] Main FGLS affine fit: a={a_fit:.4f}, b={b_fit:.4f}, m_x={mx_fit:.1f}")

    # 2. Check paper/main.tex
    tex_path = p('paper', 'main.tex')
    with open(tex_path, 'r', encoding='utf-8') as f:
        tex = f.read()
        
    required_tex_snippets = [
        "[-2.33, 0.59]",
        "14.7 \\sim 24.4",
        "46.5 \\sim 77.1",
        "21.6 \\sim 59.4",
        "1.3921",
        "[0.43, 2.41]",
        "0.0014",
        "[0.01, 3.47]",
        "0.025",
        "88.9\\%",
        "若由内部一阶条件求出的规模超出可行上界",
        "althouse2015enhancing"
    ]
    for snip in required_tex_snippets:
        if snip not in tex:
            errors.append(f"paper/main.tex missing required snippet: '{snip}'")
        else:
            print(f"[OK] paper/main.tex contains '{snip}'")
            
    banned_tex_phrases = [
        "[-2.2702, 0.6261]",
        "14.5 \\sim 24.5",
        "45.8 \\sim 77.5",
        "强稳健性对照",
        "这种相容性表明两者在数量级上具有理论机制的一致性"
    ]
    for phrase in banned_tex_phrases:
        if phrase in tex:
            errors.append(f"paper/main.tex contains banned phrase: '{phrase}'")
        else:
            print(f"[OK] paper/main.tex free of '{phrase}'")

    # 3. Check theory/propositions_and_proofs.md
    theory_path = p('theory', 'propositions_and_proofs.md')
    with open(theory_path, 'rb') as f:
        raw_theory = f.read()
    bad_bytes = [b for b in raw_theory if 0 <= b <= 8 or b == 11 or b == 12 or 14 <= b <= 31]
    if bad_bytes:
        errors.append(f"theory/propositions_and_proofs.md contains {len(bad_bytes)} non-printing control bytes")
    else:
        print("[OK] theory/propositions_and_proofs.md is clean of non-printing control bytes")

    theory_text = raw_theory.decode('utf-8')
    if "若由内部一阶条件求出的规模超出可行上界" not in theory_text:
        errors.append("theory/propositions_and_proofs.md missing Corollary 1 corner solution clause")
    else:
        print("[OK] theory/propositions_and_proofs.md contains Corollary 1 corner solution")

    # 4. Check paper/references.bib
    bib_path = p('paper', 'references.bib')
    with open(bib_path, 'r', encoding='utf-8') as f:
        bib_text = f.read()
    if "Time series analysis via mechanistic models: inference on imperfectly observed populations" in bib_text:
        errors.append("references.bib still has subtitle in Breto et al. entry")
    else:
        print("[OK] references.bib has corrected Breto et al. title")

    # Extract all DOIs from references.bib
    bib_dois = re.findall(r'doi\s*=\s*\{([^}]+)\}', bib_text, re.I)
    print(f"[OK] Extracted {len(bib_dois)} DOIs from references.bib")

    # 5. Check paper/main_docx.docx
    docx_path = p('paper', 'main_docx.docx')
    if os.path.exists(docx_path):
        try:
            with zipfile.ZipFile(docx_path, 'r') as zf:
                xml_content = zf.read('word/document.xml').decode('utf-8')
                
            banned_docx = [
                "证实了规模效应的强稳健性",
                "极显著排除零点",
                "强稳健性对照",
                "[-2.2702, 0.6261]",
                "信度比等于0.5的理论锚点",
                "在数理结构上恰对应单期信度比",
                "表4证实",
                "证明所谓“样本量失效”"
            ]
            for phrase in banned_docx:
                if phrase in xml_content:
                    errors.append(f"main_docx.docx contains banned phrase: '{phrase}'")
                else:
                    print(f"[OK] main_docx.docx free of '{phrase}'")
                    
            if "[-2.33, 0.59]" not in xml_content:
                errors.append("main_docx.docx missing formatted interaction CI [-2.33, 0.59]")
            else:
                print("[OK] main_docx.docx contains [-2.33, 0.59]")
                
            # Verify that every DOI from references.bib appears in document.xml
            missing_dois = []
            for d in bib_dois:
                if d.strip() not in xml_content:
                    missing_dois.append(d)
            if missing_dois:
                errors.append(f"main_docx.docx missing {len(missing_dois)} DOIs from references.bib: {missing_dois[:3]}...")
            else:
                print(f"[OK] All {len(bib_dois)} DOIs from references.bib present in main_docx.docx")

        except Exception as e:
            errors.append(f"Error checking main_docx.docx: {e}")
    else:
        print("[NOTICE] main_docx.docx not found; will be checked after build.")

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
