#!/usr/bin/env python3
"""Render ```mermaid fenced blocks in arxiv.md to PNG files under figures/."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "arxiv.md"
FIGURES = ROOT / "figures"

MERMAID_RE = re.compile(
    r"^```mermaid\s*\n(.*?)^```\s*$",
    re.MULTILINE | re.DOTALL,
)

DEFAULT_NAMES = [
    "tfr-runaway-electron",
    "tftr-motor-generator",
    "jet-reactor-bounce",
    "jt60u-mg-rotor",
    "tore-supra-quench",
    "jt60sa-hv-arc",
]


def mermaid_cli() -> list[str]:
    if subprocess.run(["which", "mmdc"], capture_output=True).returncode == 0:
        return ["mmdc"]
    return ["npx", "--yes", "@mermaid-js/mermaid-cli"]


def render_one(mmd_body: str, out_png: Path) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".mmd", delete=False, encoding="utf-8") as tmp:
        tmp.write(mmd_body.rstrip() + "\n")
        tmp_path = Path(tmp.name)
    env = None
    for candidate in (
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium-browser",
        "/snap/bin/chromium",
    ):
        if Path(candidate).is_file():
            env = {**os.environ, "PUPPETEER_EXECUTABLE_PATH": candidate}
            break
    try:
        cmd = [
            *mermaid_cli(),
            "-i",
            str(tmp_path),
            "-o",
            str(out_png),
            "-b",
            "white",
            "-w",
            "1200",
            "-H",
            "800",
            "--scale",
            "2",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if proc.returncode != 0:
            print(proc.stderr or proc.stdout, file=sys.stderr)
            raise RuntimeError(f"mermaid-cli failed for {out_png.name}")
    finally:
        tmp_path.unlink(missing_ok=True)


def replace_mermaid_blocks(text: str) -> tuple[str, list[str]]:
    names = list(DEFAULT_NAMES)
    rendered: list[str] = []
    idx = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal idx
        body = match.group(1)
        if idx < len(names):
            stem = names[idx]
        else:
            stem = f"mermaid-{idx + 1:03d}"
        idx += 1
        rel = f"figures/{stem}.png"
        render_one(body, ROOT / rel)
        rendered.append(rel)
        caption = stem.replace("-", " ").title()
        return f"\n\n![{caption}]({rel})\n\n"

    return MERMAID_RE.sub(repl, text), rendered


def main() -> int:
    if not SRC.is_file():
        print(f"error: missing {SRC}", file=sys.stderr)
        return 1
    raw = SRC.read_text(encoding="utf-8")
    converted, paths = replace_mermaid_blocks(raw)
    if not paths:
        print("no mermaid blocks found")
        return 0
    for path in paths:
        print(f"  rendered {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
