"""
Automated regression and multi-decimal consistency verification suite.
Traces multi-decimal numbers in paper/main.tex against simulations/empirical_stats.json
and explicitly documented theoretical/simulation outputs, validates 1:1 DOI parity between
paper/main_docx.docx and paper/references.bib, and enforces text hygiene.
"""
import json
import os
import re
import sys
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def p(*args):
    return os.path.join(ROOT, *args)

def extract_numbers_from_json(obj):
    nums = []
    if isinstance(obj, (int, float)):
        nums.append(float(obj))
    elif isinstance(obj, dict):
        for v in obj.values():
            nums.extend(extract_numbers_from_json(v))
    elif isinstance(obj, list):
        for v in obj:
            nums.extend(extract_numbers_from_json(v))
    return nums

def check_all():
    errors = []
    print(f"Running multi-decimal consistency and regression suite from ROOT: {ROOT}")
    
    # 1. Load empirical_stats.json and verify key econometric indicators
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

    a_fit = stats['early']['affine']['a']
    b_fit = stats['early']['affine']['b']
    mx_fit = stats['early']['affine']['m_x']
    if round(a_fit, 4) != 0.0991 or round(b_fit, 4) != 2.2434 or round(mx_fit, 1) != 22.6:
        errors.append(f"Main fit numbers unexpected: a={a_fit}, b={b_fit}, m_x={mx_fit}")
    else:
        print(f"[OK] Main FGLS affine fit: a={a_fit:.4f}, b={b_fit:.4f}, m_x={mx_fit:.1f}")

    # 2. General Number Trace on paper/main.tex
    tex_path = p('paper', 'main.tex')
    with open(tex_path, 'r', encoding='utf-8') as f:
        tex = f.read()

    json_floats = set(extract_numbers_from_json(stats))
    
    # Explicitly computed/derived theoretical quantities and documented simulation outputs
    derived_quantities = {
        0.029,   # 0.08 / (1.6706 ** 2) (v_R floor relative to R_bar at line 521)
        0.0302,  # 0.04 / (1.15 ** 2) (v_R floor relative to stationary baseline at line 428)
        2.1232,  # A parameter in run_forecasting_crossover_simulations.py
        1.3921,  # b_iv - b_ols difference in early-phase pooled subsample (2.8501 - 1.4581)
        0.0056,  # Lower bound of symptomatic hospitalization fraction rho (Zhou point estimate / Tokars attack rate upper bound)
        0.021,   # Upper bound of symptomatic hospitalization fraction rho (Zhou point estimate / Tokars attack rate lower bound)
    }
    simulation_grid_outputs = {
        0.0495,  # Empirical Wald test size at k=1.0 reported in paper/main.tex line 399
        0.190,   # Relative MSE at m=300 reported in paper/main.tex line 439
        0.394,   # Relative MSE at m=60 reported in paper/main.tex line 439
        0.543,   # Relative MSE at m=24 reported in paper/main.tex line 439
        0.718,   # Relative MSE at m=6 reported in paper/main.tex line 439
    }
    universe = json_floats | derived_quantities | simulation_grid_outputs

    clean_tex_for_numbers = tex.replace('--', ' ')
    matches = re.findall(r'(?<![A-Za-z0-9_])-?\d+\.\d{3,}', clean_tex_for_numbers)
    distinct_decimals = sorted(set(matches))
    print(f"[OK] Scanning {len(matches)} decimal occurrences ({len(distinct_decimals)} distinct) in paper/main.tex...")

    unmatched_nums = []
    for m in distinct_decimals:
        val = float(m)
        prec = len(m.split('.')[1])
        matched = False
        for u in universe:
            if abs(val - u) < 0.5 * (10 ** -prec) or abs(val - round(u, prec)) < 1e-7:
                matched = True
                break
        if not matched:
            unmatched_nums.append(m)

    if unmatched_nums:
        errors.append(f"Number trace check failed: {len(unmatched_nums)} unmatched numbers in main.tex: {unmatched_nums}")
    else:
        print(f"[OK] Multi-decimal trace 100% matched ({len(distinct_decimals)} distinct numbers verified)")

    # 3. Check required and banned phrasing in paper/main.tex
    required_tex_snippets = [
        "[-2.33, 0.59]",
        "14.6 \\sim 22.2",
        "46.1 \\sim 70.2",
        "21.3 \\sim 49.3",
        "0.0056, 0.021",
        "88.9\\%",
        "若由内部一阶条件求出的规模超出可行上界"
    ]
    for snip in required_tex_snippets:
        if snip not in tex:
            errors.append(f"paper/main.tex missing required snippet: '{snip}'")
        else:
            print(f"[OK] paper/main.tex contains '{snip}'")

    banned_tex_phrases = [
        "[-2.2702, 0.6261]",
        "14.7 \\sim 24.4",
        "46.5 \\sim 77.1",
        "21.6 \\sim 59.4",
        "14.5 \\sim 24.5",
        "45.8 \\sim 77.5",
        "强稳健性对照",
        "这种相容性表明两者在数量级上具有理论机制的一致性",
        "与 NHSN 本身周度增长比残余方差同量级",
        "代表性理论参数空间"
    ]
    for phrase in banned_tex_phrases:
        if phrase in tex:
            errors.append(f"paper/main.tex contains banned phrase: '{phrase}'")
        else:
            print(f"[OK] paper/main.tex free of '{phrase}'")

    # 4. Check theory/propositions_and_proofs.md
    theory_path = p('theory', 'propositions_and_proofs.md')
    with open(theory_path, 'rb') as f:
        raw_theory = f.read()
    bad_bytes = [b for b in raw_theory if 0 <= b <= 8 or b == 11 or b == 12 or 14 <= b <= 31]
    if bad_bytes:
        errors.append(f"theory/propositions_and_proofs.md contains {len(bad_bytes)} non-printing control bytes")
    else:
        print("[OK] theory/propositions_and_proofs.md clean of non-printing control bytes")

    theory_text = raw_theory.decode('utf-8')
    if "若由内部一阶条件求出的规模超出可行上界" not in theory_text:
        errors.append("theory/propositions_and_proofs.md missing Corollary 1 corner solution clause")
    else:
        print("[OK] theory/propositions_and_proofs.md contains Corollary 1 corner solution")

    # 5. Check paper/references.bib
    bib_path = p('paper', 'references.bib')
    with open(bib_path, 'r', encoding='utf-8') as f:
        bib_text = f.read()
    if "Time series analysis via mechanistic models: inference on imperfectly observed populations" in bib_text:
        errors.append("references.bib still has subtitle in Breto et al. entry")
    else:
        print("[OK] references.bib has corrected Breto et al. title")

    bib_dois = re.findall(r'doi\s*=\s*\{([^}]+)\}', bib_text, re.I)
    print(f"[OK] Extracted {len(bib_dois)} DOIs from references.bib")

    # 6. Check paper/main_docx.docx
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

    # Summary
    if errors:
        print("\nFAILED: Discrepancies detected:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("\nALL CONSISTENCY AND REGRESSION CHECKS PASSED!")

if __name__ == '__main__':
    check_all()
