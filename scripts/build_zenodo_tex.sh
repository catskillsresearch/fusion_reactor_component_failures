#!/usr/bin/env bash
# Generate zenodo.tex and Mermaid figures from arxiv.md (no arXiv categories).
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/build_arxiv_tex.py --target zenodo "$@"
