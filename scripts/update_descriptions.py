#!/usr/bin/env python3
"""
Sync the hero description paragraphs on the landing pages with the summaries
from the corresponding LaTeX resume headers.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TARGETS = [
    {
        "tex": ROOT / "resume" / "resume_en.tex",
        "html": ROOT / "index.html",
        "label": "English",
    },
    {
        "tex": ROOT / "resume" / "resume_cn.tex",
        "html": ROOT / "index-zh.html",
        "label": "Chinese",
    },
]


def extract_description(tex_path: Path) -> str:
    text = tex_path.read_text(encoding="utf-8")
    match = re.search(r"\\begin{center}(.*?)\\rule", text, re.S)
    if not match:
        raise RuntimeError(f"Could not find header block in {tex_path}")

    block = match.group(1)
    lines = []
    for raw_line in block.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("{\\LARGE"):
            continue
        stripped = re.sub(r"\\\\(\[[^\]]*\])?", "", stripped).strip()
        if stripped:
            lines.append(stripped)

    if not lines:
        raise RuntimeError(f"No description lines detected in {tex_path}")

    return " ".join(lines)


def update_hero_description(html_path: Path, description: str) -> None:
    content = html_path.read_text(encoding="utf-8")
    pattern = re.compile(
        r'(<header class="hero">[\s\S]*?<p>\s*)([\s\S]*?)(\s*</p>)',
        re.MULTILINE,
    )
    match = pattern.search(content)
    if not match:
        raise RuntimeError(f"Hero description paragraph not found in {html_path}")

    updated = pattern.sub(
        lambda m: f"{m.group(1)}{description}{m.group(3)}",
        content,
        count=1,
    )
    html_path.write_text(updated, encoding="utf-8")


def main() -> None:
    for target in TARGETS:
        tex_path = target["tex"]
        html_path = target["html"]
        description = extract_description(tex_path)
        update_hero_description(html_path, description)
        print(f"- {target['label']}: {html_path.relative_to(ROOT)} updated.")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as err:
        sys.stderr.write(f"{err}\n")
        sys.exit(1)
