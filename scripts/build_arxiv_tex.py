#!/usr/bin/env python3
"""Convert arxiv.md to arxiv.tex (avg_case_mls-style pipeline with Mermaid → PNG)."""

from __future__ import annotations

import re
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from render_mermaid_figures import replace_mermaid_blocks  # noqa: E402

SRC = ROOT / "arxiv.md"
OUT = ROOT / "arxiv.tex"
PREAMBLE = SCRIPTS / "tex_preamble_arxiv.tex"

GITHUB_INLINE_MATH = re.compile(r"\$`([^`\n]+?)`\$")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
FENCE_RE = re.compile(r"^```([^\n]*)\n(.*?)^```\s*$", re.MULTILINE | re.DOTALL)
MANUAL_SECTION_NUM = re.compile(r"^(#{1,4})\s+\d+\.\s+", re.MULTILINE)
ABSTRACT_RE = re.compile(
    r"^\*\*Abstract\*\*\s*\n(.*?)(?=\n---\s*\n)",
    re.MULTILINE | re.DOTALL,
)


def ensure_blank_line_before_lists(text: str) -> str:
    """Pandoc treats '* item' as a list only after a blank line."""
    return re.sub(r"(:)\n([*+-] )", r":\n\n\2", text)


def github_math_to_tex(text: str) -> str:
    return GITHUB_INLINE_MATH.sub(r"$\1$", text)


def strip_html_comments(text: str) -> str:
    return HTML_COMMENT.sub("", text)


def strip_manual_section_numbers(text: str) -> str:
    return MANUAL_SECTION_NUM.sub(r"\1 ", text)


def extract_title_and_abstract(text: str) -> tuple[str, str, str]:
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ValueError("arxiv.md must start with a # title line")
    title = lines[0][2:].strip()
    rest = "\n".join(lines[1:]).lstrip("\n")
    abstract_match = ABSTRACT_RE.search(rest)
    if not abstract_match:
        raise ValueError("arxiv.md must contain **Abstract** before the first ---")
    abstract = abstract_match.group(1).strip()
    body = (rest[: abstract_match.start()] + rest[abstract_match.end() :]).lstrip("\n")
    body = re.sub(r"^---\s*\n", "", body, count=1)
    return title, abstract, body


def escape_latex(text: str) -> str:
    replacements = [
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicaret{}"),
    ]
    out = text
    for old, new in replacements:
        out = out.replace(old, new)
    return out


def replace_fences(text: str) -> tuple[str, dict[str, str]]:
    placeholders: dict[str, str] = {}
    code_idx = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal code_idx
        lang = match.group(1).strip().lower()
        body = match.group(2)
        if lang == "mermaid":
            return match.group(0)
        key = f"CODEINCLUDE{code_idx:03d}"
        code_idx += 1
        if lang == "math":
            placeholders[key] = f"\\[\n{body.strip()}\n\\]\n"
        else:
            placeholders[key] = (
                f"\\begin{{verbatim}}\n{body.rstrip()}\n\\end{{verbatim}}\n"
            )
        return f"\n\n{key}\n\n"

    converted = FENCE_RE.sub(repl, text)
    return converted, placeholders


def pandoc_to_latex(markdown: str) -> str:
    proc = subprocess.run(
        [
            "pandoc",
            "-f",
            "markdown+tex_math_dollars+raw_tex+smart",
            "-t",
            "latex",
            "--wrap=none",
            "--shift-heading-level-by=-1",
        ],
        input=markdown,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        raise RuntimeError("pandoc failed")
    return proc.stdout


def inject_placeholders(latex: str, placeholders: dict[str, str]) -> str:
    out = latex
    for key, value in placeholders.items():
        patterns = [
            key,
            f"\\emph{{{key}}}",
            f"\\text{{{key}}}",
            f"\\passthrough{{\\lstinline!{key}!}}",
        ]
        for pat in patterns:
            if pat in out:
                out = out.replace(pat, value)
                break
        else:
            out = out.replace(key, value)
    return out


def cleanup_pandoc_latex(latex: str) -> str:
    latex = latex.replace("\\pandocbounded{", "{")
    latex = re.sub(r"\\tightlist\n", "", latex)
    latex = re.sub(r"\\section\{\d+\.\s+", r"\\section{", latex)
    latex = re.sub(r"\\subsection\{\d+\.\s+", r"\\subsection{", latex)
    latex = re.sub(r"\\subsubsection\{\d+\.\s+", r"\\subsubsection{", latex)
    latex = re.sub(
        r"\\includegraphics\{figures/([^}]+)\}",
        r"\\begin{center}\n"
        r"\\includegraphics[width=0.5\\textwidth,height=0.5\\textheight,keepaspectratio]{figures/\1}\n"
        r"\\end{center}",
        latex,
    )
    latex = re.sub(r"\n{3,}", "\n\n", latex)
    return latex


def build_title_page(title: str, abstract: str) -> str:
    abstract_tex = escape_latex(abstract)
    return textwrap.dedent(
        f"""
        \\title{{\\textbf{{{escape_latex(title)}}}}}

        \\author[1]{{\\textbf{{Lars Warren Ericson}}}}
        \\affil[1]{{Catskills Research Company}}
        \\affil[1]{{\\texttt{{lars.ericson@catskillsresearch.com}}}}

        \\date{{\\today}}

        \\begin{{document}}

        \\maketitle

        \\begin{{center}}
          \\small
          \\textbf{{ORCID:}} 0000-0001-8299-9361 \\\\
          \\textbf{{Primary Category:}} physics.plasm-ph (Plasma Physics) \\\\
          \\textbf{{Secondary Category:}} physics.ins-det (Instrumentation and Detectors) \\\\[0.5em]
          \\textbf{{Repository:}} \\url{{https://github.com/catskillsresearch/fusion_reactor_component_failures}}
        \\end{{center}}

        \\begin{{abstract}}
        {abstract_tex}
        \\end{{abstract}}
        """
    ).strip()


def main() -> int:
    if not SRC.is_file():
        print(f"error: missing {SRC}", file=sys.stderr)
        return 1
    if not PREAMBLE.is_file():
        print(f"error: missing {PREAMBLE}", file=sys.stderr)
        return 1

    raw = SRC.read_text(encoding="utf-8")
    title, abstract, body = extract_title_and_abstract(raw)
    body, mermaid_paths = replace_mermaid_blocks(body)
    if mermaid_paths:
        print("rendered mermaid figures:")
        for path in mermaid_paths:
            print(f"  {path}")

    body = strip_html_comments(body)
    body = strip_manual_section_numbers(body)
    body = ensure_blank_line_before_lists(body)
    body = github_math_to_tex(body)
    body, placeholders = replace_fences(body)
    latex_body = pandoc_to_latex(body)
    latex_body = inject_placeholders(latex_body, placeholders)
    latex_body = cleanup_pandoc_latex(latex_body)

    preamble = PREAMBLE.read_text(encoding="utf-8")
    title_page = build_title_page(title, abstract)
    document = (
        preamble
        + "\n\n"
        + title_page
        + "\n\n"
        + latex_body
        + "\n\n\\end{document}\n"
    )
    OUT.write_text(document, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
