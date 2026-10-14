#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
rm -f main.aux main.bbl main.blg main.log main.out main.toc main.lof main.lot main.pdf
xelatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
xelatex -interaction=nonstopmode -halt-on-error main.tex
xelatex -interaction=nonstopmode -halt-on-error main.tex
