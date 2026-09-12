#!/usr/bin/env python3
"""Build an anonymous IEEEtran PDF from the frozen Markdown manuscript."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript" / "original-paper.md"
IEEE_DIR = ROOT / "submission" / "ieee"
FIGURE_DIR = IEEE_DIR / "figures"
OUTPUT_DIR = ROOT / "output" / "pdf"
PREPARED = IEEE_DIR / "prepared-paper.md"
TEX = IEEE_DIR / "medical-world-model-ieee.tex"
PDF = IEEE_DIR / "medical-world-model-ieee.pdf"
FINAL_PDF = OUTPUT_DIR / "medical-world-model-ieee.pdf"

TITLE = (
    "Beyond One-Step Error: Free-Running Evaluation of ICU "
    "Chart-Process World Models Across Cohorts"
)
KEYWORDS = (
    "world model, clinical time series, free-running rollout, uncertainty, "
    "external validation, intensive care"
)


def run(*args: str, cwd: Path | None = None) -> None:
    subprocess.run(args, cwd=cwd, check=True)


def strip_markdown(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = text.replace("\\(", "$").replace("\\)", "$")
    return " ".join(text.split())


def latex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
    return "".join(replacements.get(char, char) for char in text)


def convert_citations(text: str) -> str:
    pattern = re.compile(r"\[([1-9][0-9]*(?:\s*[-,]\s*[1-9][0-9]*)*)\]")

    def replacement(match: re.Match[str]) -> str:
        content = match.group(1)
        numbers: list[int] = []
        for part in content.split(","):
            part = part.strip()
            if "-" in part:
                start, end = (int(value.strip()) for value in part.split("-", 1))
                numbers.extend(range(start, end + 1))
            else:
                numbers.append(int(part))
        if any(number > 99 for number in numbers):
            return match.group(0)
        return r"\cite{" + ",".join(f"b{number}" for number in numbers) + "}"

    return pattern.sub(replacement, text)


def extract_abstract(text: str) -> tuple[str, str]:
    before, rest = text.split("## Abstract", 1)
    abstract_block, body = rest.split("## 1. Introduction", 1)
    paragraphs: list[str] = []
    for label in ("Background", "Methods", "Results", "Conclusions"):
        match = re.search(
            rf"\*\*{label}:\*\*\s*(.*?)(?=\n\n\*\*|\n\n\*\*Keywords:)",
            abstract_block,
            flags=re.S,
        )
        if match:
            content = latex_escape(strip_markdown(match.group(1)))
            paragraphs.append(f"\\textit{{{label}---}} {content}")
    return "\n\n".join(paragraphs), "## 1. Introduction" + body


def move_references_to_end(text: str) -> tuple[str, str]:
    before_refs, after_marker = text.split("## References", 1)
    refs, tail = after_marker.split("## Data and Code Availability", 1)
    tail = "## Data and Code Availability" + tail
    tail = re.sub(
        r"## Funding\s+.*?(?=\n## )",
        "## Funding\n\nFunding information is withheld for anonymous review.\n\n",
        tail,
        flags=re.S,
    )
    tail = re.sub(
        r"## Declaration of Competing Interest\s+.*?(?=\n## )",
        "## Declaration of Competing Interest\n\n"
        "Competing-interest information is withheld for anonymous review.\n\n",
        tail,
        flags=re.S,
    )
    tail = re.sub(
        r"## CRediT Author Statement\s+.*?(?=\n## )",
        "",
        tail,
        flags=re.S,
    )
    return before_refs.rstrip() + "\n\n" + tail.rstrip(), refs.strip()


def references_latex(refs: str) -> str:
    entries = re.findall(r"(?m)^(\d+)\.\s+(.*)$", refs)
    lines = [r"\balance", r"\begin{thebibliography}{00}"]
    for number, entry in entries:
        clean = latex_escape(strip_markdown(entry))
        lines.append(rf"\bibitem{{b{number}}} {clean}")
    lines.append(r"\end{thebibliography}")
    return "\n".join(lines)


def replace_figures(text: str) -> str:
    pattern = re.compile(
        r"!\[(?P<alt>[^\]]*)\]\((?P<path>[^)]+)\)\s*\n\s*"
        r"\*\*(?P<label>(?:Figure|Extended Data Figure)\s+\d+\.[^*]*)\*\*"
        r"(?P<caption>.*?)(?=\n\n(?:###|##|!\[)|\Z)",
        flags=re.S,
    )
    counter = 0

    def replacement(match: re.Match[str]) -> str:
        nonlocal counter
        counter += 1
        source = (MANUSCRIPT.parent / match.group("path")).resolve()
        source = source.with_suffix(".pdf")
        target = FIGURE_DIR / f"figure-{counter}.pdf"
        shutil.copy2(source, target)
        caption = strip_markdown(match.group("label") + match.group("caption"))
        caption = re.sub(
            r"^(?:Extended Data )?Figure\s+\d+\.\s*", "", caption
        )
        return (
            "\n\n"
            r"\begin{figure*}[!t]" "\n"
            r"\centering" "\n"
            rf"\includegraphics[width=0.98\textwidth]{{figures/{target.name}}}" "\n"
            rf"\caption{{{latex_escape(caption)}}}" "\n"
            rf"\label{{fig:result-{counter}}}" "\n"
            r"\end{figure*}"
            "\n\n"
        )

    return pattern.sub(replacement, text)


def replace_main_table(text: str) -> str:
    pattern = re.compile(
        r"(?P<table>\| Model \| 1 h NMAE .*?\n"
        r"\| ---.*?(?:\n\|.*?)+)(?=\n\nBaseline values)",
        flags=re.S,
    )
    match = pattern.search(text)
    if not match:
        raise ValueError("Main result table was not found")
    lines = [
        line for line in match.group("table").splitlines()
        if line.strip() and not line.startswith("| ---")
    ]
    rows = [
        [cell.strip() for cell in line.strip().strip("|").split("|")]
        for line in lines[1:]
    ]
    latex = [
        r"\begin{table*}[!t]",
        r"\centering",
        r"\caption{Descriptive zero-shot external-test results. Neural values "
        r"are mean (across-seed standard deviation).}",
        r"\label{tab:external-results}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{lrrrrrrr}",
        r"\toprule",
        r"Model & 1 h NMAE & 12 h NMAE & 24 h NMAE & 12 h CRPS & "
        r"Empirical coverage & Mask Brier & Pressure violations/1,000 \\",
        r"\midrule",
    ]
    for row in rows:
        latex.append(" & ".join(latex_escape(cell) for cell in row) + r" \\")
    latex.extend(
        [
            r"\bottomrule",
            r"\end{tabular}%",
            r"}",
            r"\end{table*}",
        ]
    )
    return text[: match.start()] + "\n".join(latex) + text[match.end() :]


def normalize_headings(text: str) -> str:
    text = re.sub(
        r"^(#{2,3})\s+\d+(?:\.\d+)*\.?\s+",
        lambda match: match.group(1) + " ",
        text,
        flags=re.M,
    )
    lines = []
    for line in text.splitlines():
        if line.startswith("### "):
            line = "## " + line[4:]
        elif line.startswith("## "):
            line = "# " + line[3:]
        lines.append(line)
    return "\n".join(lines)


def prepare_markdown() -> tuple[str, str]:
    raw = MANUSCRIPT.read_text(encoding="utf-8")
    abstract, body = extract_abstract(raw)
    body, refs = move_references_to_end(body)
    body = replace_figures(body)
    body = replace_main_table(body)
    body = normalize_headings(body)
    body = convert_citations(body)
    body = re.sub(
        r"Development status:.*?\n\nAuthors:.*?\nCorresponding author:.*?\n\n",
        "",
        body,
        flags=re.S,
    )
    body = body.rstrip() + "\n\n" + references_latex(refs) + "\n"
    PREPARED.write_text(body, encoding="utf-8")
    return abstract, body


def main() -> int:
    IEEE_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    abstract, _ = prepare_markdown()
    run(
        "pandoc",
        str(PREPARED),
        "--from=markdown+raw_tex+tex_math_dollars+tex_math_single_backslash",
        "--to=latex",
        "--standalone",
        f"--template={IEEE_DIR / 'template.tex'}",
        f"--metadata=title:{TITLE}",
        "--metadata=abstract:IEEEABSTRACTPLACEHOLDER",
        f"--metadata=keywords:{KEYWORDS}",
        "--wrap=preserve",
        f"--output={TEX}",
        cwd=IEEE_DIR,
    )
    tex = TEX.read_text(encoding="utf-8")
    if "IEEEABSTRACTPLACEHOLDER" not in tex:
        raise ValueError("Abstract placeholder was not preserved by Pandoc")
    TEX.write_text(
        tex.replace("IEEEABSTRACTPLACEHOLDER", abstract),
        encoding="utf-8",
    )
    run(
        "tectonic",
        "--keep-logs",
        "--keep-intermediates",
        TEX.name,
        cwd=IEEE_DIR,
    )
    shutil.copy2(PDF, FINAL_PDF)
    print(FINAL_PDF)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
