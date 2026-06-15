#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/build_arxiv_tex.py
# Optional: pdflatex arxiv.tex  (twice) or latexmk arxiv.tex
