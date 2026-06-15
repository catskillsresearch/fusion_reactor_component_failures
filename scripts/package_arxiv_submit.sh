#!/usr/bin/env bash
# Build arxiv.tex and zip everything arXiv needs to compile it.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

TEX="arxiv.tex"
OUT_DIR="dist"
ZIP="${OUT_DIR}/arxiv_submit.zip"

if [[ "${1:-}" != "--zip-only" ]]; then
  echo "==> Regenerating TeX and Mermaid figure PNGs"
  ./scripts/build_arxiv_tex.sh
fi

if [[ ! -f "$TEX" ]]; then
  echo "error: missing $TEX" >&2
  exit 1
fi

shopt -s nullglob
figures=(figures/*.png)
if [[ ${#figures[@]} -eq 0 ]]; then
  echo "error: no PNG files in figures/" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"
rm -f "$ZIP"

echo "==> Writing 00README.json (mark figures as include so arXiv does not drop them)"
python3 - <<'PY'
import json
from pathlib import Path

sources = [{"filename": "arxiv.tex", "usage": "toplevel"}]
for path in sorted(Path("figures").glob("*.png")):
    sources.append({"filename": path.as_posix(), "usage": "include"})
readme = {"process": {"compiler": "pdflatex"}, "sources": sources}
Path("00README.json").write_text(json.dumps(readme, indent=2) + "\n")
print(f"  {len(sources)} sources")
PY

echo "==> Packaging"
zip -r "$ZIP" 00README.json "$TEX" "${figures[@]}"

echo "wrote $ZIP ($(du -h "$ZIP" | cut -f1))"
echo "Contents:"
zipinfo -1 "$ZIP" | sed 's/^/  /'
echo
echo "Upload $ZIP to arXiv (pdfLaTeX)."
echo
echo "On arXiv Add Files: Delete All before uploading (uploads merge, they do not replace)."
echo "On arXiv Review Files: if any figures/*.png are marked for deletion, UNCHECK them."
