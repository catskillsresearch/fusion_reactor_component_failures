#!/usr/bin/env bash
# Full rebuild: arxiv.md → arxiv.tex, Mermaid PNGs, arxiv.pdf, dist/arxiv_submit.zip
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Generating arxiv.tex and Mermaid figures"
python3 scripts/build_arxiv_tex.py

echo "==> Compiling arxiv.pdf"
latexmk -pdf -interaction=nonstopmode arxiv.tex

echo "==> Packaging arXiv submit zip"
./scripts/package_arxiv_submit.sh --zip-only
