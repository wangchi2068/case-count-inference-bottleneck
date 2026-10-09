# -*- coding: utf-8 -*-
"""
Robust Markdown to Publication-grade LaTeX converter and Tectonic compiler.
Handles display math, inline math, complex tables, lists, and unicode symbols.
Includes LaTeX bracket-after-newline guard and longtable support.
"""
import os
import re
import sys
import subprocess

SRC = r'C:\Users\wangchi2068\.kimi-code\sessions\wd_trae_c14486ecff06\session_16eab20c-4f77-44fa-85dd-43ea90e9b7fc\attachments\f_547f35ef-5748-4abd-b675-f24a21ca0e33-deep-read.md'
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs')
os.makedirs(OUT_DIR, exist_ok=True)
TEX_PATH = os.path.join(OUT_DIR, 'deep_read.tex')
PDF_PATH = os.path.join(OUT_DIR, 'deep_read.pdf')

def parse_md_to_latex(md_text):
    unicode_reps = [
        ('≥', r'$\ge$'),
        ('≤', r'$\le$'),
        ('±', r'$\pm$'),
        ('→', r'$\to$'),
        ('≈', r'$\approx$'),
        ('≠', r'$\ne$'),
        ('×', r'$\times$'),
        ('∞', r'$\infty$'),
        ('λ', r'$\lambda$'),
        ('α', r'$\alpha$'),
        ('β', r'$\beta$'),
        ('ρ', r'$\rho$'),
        ('δ', r'$\delta$'),
        ('σ', r'$\sigma$'),
        ('π', r'$\pi$'),
        ('Λ', r'$\Lambda$'),
        ('ν', r'$\nu$'),
        ('τ', r'$\tau$'),
        ('γ', r'$\gamma$'),
        ('κ', r'$\kappa$'),
        ('μ', r'$\mu$'),
        ('′', r'$^{\prime}$'),
        ('‑', '-'),
    ]
    
    lines = md_text.splitlines()
    latex_lines = []
    
    in_math_block = False
    math_block_lines = []
    
    in_table = False
    table_lines = []
    
    in_list = False
    list_type = None # 'itemize' or 'enumerate'

    def format_inline(text):
        if not text:
            return ''
            
        # Protect inline math $...$
        math_matches = []
        def math_repl(m):
            math_matches.append(m.group(0))
            return f'TOKENMATHINLINE{len(math_matches)-1}ENDTOKEN'
        text = re.sub(r'(?<!\\)\$(.*?)(?<!\\)\$', math_repl, text)
        
        # Protect inline code `...`
        code_matches = []
        def code_repl(m):
            code_matches.append(m.group(1))
            return f'TOKENCODEINLINE{len(code_matches)-1}ENDTOKEN'
        text = re.sub(r'`([^`]+)`', code_repl, text)
        
        # Replace unicode math symbols if outside protected tokens
        for sym, rep in unicode_reps:
            text = text.replace(sym, rep)
            
        # Bold and Italic
        text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)
        text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'\\textit{\1}', text)
        
        # Escape LaTeX special chars: %, &, _, #
        text = text.replace('%', r'\%')
        text = text.replace('&', r'\&')
        text = text.replace('_', r'\_')
        text = text.replace('#', r'\#')
        text = text.replace('~', r'\textasciitilde{}')
        
        # Restore inline code
        for i, c in enumerate(code_matches):
            c_safe = c.replace('\\', r'\textbackslash{}').replace('_', r'\_').replace('%', r'\%').replace('&', r'\&')
            text = text.replace(f'TOKENCODEINLINE{i}ENDTOKEN', f'\\texttt{{{c_safe}}}')
            
        # Restore inline math
        for i, m in enumerate(math_matches):
            text = text.replace(f'TOKENMATHINLINE{i}ENDTOKEN', m)
            
        return text

    def flush_list():
        nonlocal in_list, list_type
        if in_list:
            latex_lines.append(f'\\end{{{list_type}}}')
            in_list = False
            list_type = None

    def render_table(t_lines):
        if not t_lines:
            return
        rows = []
        for l in t_lines:
            cells = [c.strip() for c in l.strip().split('|')[1:-1]]
            rows.append(cells)
        if len(rows) < 2:
            return
        header = rows[0]
        data_rows = rows[2:] if len(rows) > 2 else []
        col_count = len(header)
        if col_count == 0:
            return
            
        is_long = len(data_rows) > 15
        
        if is_long:
            # Longtable for large tables (like notation table)
            if col_count == 4:
                aligns = r'l p{5.2cm} l p{5.2cm}'
            else:
                aligns = 'l' * col_count
                
            out = []
            out.append('\\begin{center}')
            out.append('\\small')
            out.append(f'\\begin{{longtable}}{{{aligns}}}')
            out.append('\\toprule')
            header_tex = ' & '.join([f'\\textbf{{{format_inline(c)}}}' for c in header]) + r' \\'
            out.append(header_tex)
            out.append('\\midrule')
            out.append('\\endfirsthead')
            out.append('\\toprule')
            out.append(header_tex)
            out.append('\\midrule')
            out.append('\\endhead')
            out.append('\\bottomrule')
            out.append('\\endfoot')
            
            for r in data_rows:
                r = r + [''] * (col_count - len(r))
                formatted_cells = []
                for c in r[:col_count]:
                    fc = format_inline(c)
                    if fc.startswith('['):
                        fc = '{' + fc + '}'
                    formatted_cells.append(fc)
                row_tex = ' & '.join(formatted_cells) + r' \\'
                out.append(row_tex)
                
            out.append('\\end{longtable}')
            out.append('\\end{center}')
            latex_lines.extend(out)
        else:
            use_resize = col_count > 4
            aligns = 'l' * col_count
            
            out = []
            out.append('\\begin{table}[htbp]')
            out.append('\\centering')
            out.append('\\small')
            if use_resize:
                out.append('\\resizebox{\\textwidth}{!}{%')
            out.append(f'\\begin{{tabular}}{{{aligns}}}')
            out.append('\\toprule')
            header_tex = ' & '.join([f'\\textbf{{{format_inline(c)}}}' for c in header]) + r' \\'
            out.append(header_tex)
            out.append('\\midrule')
            
            for r in data_rows:
                r = r + [''] * (col_count - len(r))
                formatted_cells = []
                for c in r[:col_count]:
                    fc = format_inline(c)
                    # Protect bracket from being parsed as row spacing \\[...pt]
                    if fc.startswith('['):
                        fc = '{' + fc + '}'
                    formatted_cells.append(fc)
                row_tex = ' & '.join(formatted_cells) + r' \\'
                out.append(row_tex)
                
            out.append('\\bottomrule')
            if use_resize:
                out.append('\\end{tabular}%')
                out.append('}')
            else:
                out.append('\\end{tabular}')
            out.append('\\end{table}')
            latex_lines.extend(out)

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Single-line display math: $$...$$ with optional punctuation
        m_single_math = re.match(r'^\$\$(.*?)\$\$[，,。;；]?$', stripped)
        if m_single_math:
            flush_list()
            if in_table:
                render_table(table_lines)
                table_lines = []
                in_table = False
            math_content = m_single_math.group(1).rstrip('，,。;； ')
            latex_lines.append(f'\\[\n{math_content}\n\\]')
            i += 1
            continue
            
        # Multi-line display math start/end $$
        if stripped == '$$':
            flush_list()
            if in_table:
                render_table(table_lines)
                table_lines = []
                in_table = False
            if in_math_block:
                math_content = '\n'.join(math_block_lines)
                latex_lines.append(f'\\[\n{math_content}\n\\]')
                math_block_lines = []
                in_math_block = False
            else:
                in_math_block = True
            i += 1
            continue
            
        if in_math_block:
            math_block_lines.append(line)
            i += 1
            continue
            
        # Table rows
        if stripped.startswith('|') and stripped.endswith('|'):
            flush_list()
            in_table = True
            table_lines.append(stripped)
            i += 1
            continue
        else:
            if in_table:
                render_table(table_lines)
                table_lines = []
                in_table = False
                
        # Empty lines
        if not stripped:
            flush_list()
            latex_lines.append('')
            i += 1
            continue
            
        # Horizontal rules
        if stripped in ['---', '***', '___']:
            flush_list()
            latex_lines.append('\\vspace{0.8em}\\hrule\\vspace{0.8em}')
            i += 1
            continue
            
        # Headings
        if stripped.startswith('#'):
            flush_list()
            m = re.match(r'^(#+)\s*(.*)$', stripped)
            level = len(m.group(1))
            htext = format_inline(m.group(2))
            if level == 1:
                latex_lines.append('\\begin{center}')
                latex_lines.append(f'{{\\LARGE\\textbf{{{htext}}}}}\\\\[0.8em]')
                latex_lines.append('{\\large\\color{gray} 论文全案理论推导详解 $\\cdot$ sympy 数值核验 $\\cdot$ 技术审计意见}\\\\[1.2em]')
                latex_lines.append('\\end{center}')
                latex_lines.append('{\\hypersetup{linkcolor=black}\\tableofcontents}')
                latex_lines.append('\\vspace{1.5em}\\hrule\\vspace{1.5em}')
            elif level == 2:
                latex_lines.append(f'\\section{{{htext}}}')
            elif level == 3:
                latex_lines.append(f'\\subsection{{{htext}}}')
            elif level == 4:
                latex_lines.append(f'\\subsubsection{{{htext}}}')
            else:
                latex_lines.append(f'\\paragraph{{{htext}}}')
            i += 1
            continue
            
        # Unordered list
        m_ul = re.match(r'^[-*]\s+(.*)$', stripped)
        if m_ul:
            item_text = format_inline(m_ul.group(1))
            if not in_list or list_type != 'itemize':
                flush_list()
                in_list = True
                list_type = 'itemize'
                latex_lines.append('\\begin{itemize}[leftmargin=2em, itemsep=2pt, parsep=0pt]')
            latex_lines.append(f'\\item {item_text}')
            i += 1
            continue
            
        # Ordered list
        m_ol = re.match(r'^(\d+)\.\s+(.*)$', stripped)
        if m_ol:
            item_text = format_inline(m_ol.group(2))
            if not in_list or list_type != 'enumerate':
                flush_list()
                in_list = True
                list_type = 'enumerate'
                latex_lines.append('\\begin{enumerate}[leftmargin=2em, itemsep=2pt, parsep=0pt]')
            latex_lines.append(f'\\item {item_text}')
            i += 1
            continue
            
        # Regular text paragraph
        flush_list()
        latex_lines.append(format_inline(stripped) + '\n')
        i += 1
        
    flush_list()
    if in_table:
        render_table(table_lines)
        
    return '\n'.join(latex_lines)

# Read markdown
with open(SRC, 'r', encoding='utf-8') as f:
    raw_md = f.read()

body_tex = parse_md_to_latex(raw_md)

# Full LaTeX document
full_tex = r"""\documentclass[11pt,a4paper]{ctexart}
\usepackage[top=2.5cm,bottom=2.5cm,left=2.2cm,right=2.2cm]{geometry}
\usepackage{amsmath,amssymb,amsfonts,amsthm}
\usepackage{booktabs,tabularx,array,makecell,graphicx,longtable}
\usepackage{enumitem}
\usepackage{xcolor}
\usepackage{fancyhdr}
\usepackage{hyperref}

\hypersetup{
    colorlinks=true,
    linkcolor=blue!75!black,
    citecolor=blue!75!black,
    urlcolor=blue!75!black,
    pdfauthor={Kimi Code Deep Read},
    pdftitle={论文深读与理论推导详解}
}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\color{gray}《病例规模的推断收益边界》深读与推导详解}
\fancyhead[R]{\small\color{gray}\nouppercase{\leftmark}}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}

% Section styling
\ctexset{
    section = {
        format = \Large\bfseries\color{blue!80!black},
        beforeskip = 1.2ex plus .2ex minus .2ex,
        afterskip = 1ex plus .2ex
    },
    subsection = {
        format = \large\bfseries\color{black},
        beforeskip = 1ex plus .2ex minus .2ex,
        afterskip = 0.8ex plus .2ex
    },
    subsubsection = {
        format = \normalsize\bfseries\color{black!90},
        beforeskip = 0.8ex plus .2ex minus .2ex,
        afterskip = 0.6ex plus .2ex
    }
}

\setlength{\parindent}{2em}
\setlength{\parskip}{0.4em}

\begin{document}

""" + body_tex + r"""

\end{document}
"""

with open(TEX_PATH, 'w', encoding='utf-8') as f:
    f.write(full_tex)

print(f"LaTeX generated: {TEX_PATH} ({len(full_tex)} bytes)")
