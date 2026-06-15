#!/usr/bin/env bash
# Generate arxiv.tex and Mermaid figure PNGs from arxiv.md only.
# For tex + PDF + submit zip, run: ./scripts/rebuild_arxiv.sh
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/build_arxiv_tex.py
