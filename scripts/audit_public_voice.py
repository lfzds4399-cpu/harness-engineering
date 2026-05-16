"""Audit public-facing repository text for hype and AI-slop signals.

The script is intentionally simple: it scans Markdown and package metadata for
phrases that make a small public repo look generated, over-marketed, or
unverified. Findings are prompts for human review, not automatic failures.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

TEXT_GLOBS = (
    "README*.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "docs/*.md",
    "package.json",
    "pyproject.toml",
)

SKIP_PARTS = {
    ".git",
    ".venv",
    "node_modules",
    "dist",
    "build",
    ".pytest_cache",
    "__pycache__",
}

RULES: list[tuple[str, re.Pattern[str]]] = [
    ("star_cta", re.compile(r"star the repo|⭐|moves the needle", re.I)),
    ("emoji_marketing", re.compile(r"[🚀✨🔥🧠🤖🎯📦🌐🧪🪟]")),
    ("hype_words", re.compile(r"\b(magic|battle-tested|production-ready|just works|game[- ]changer)\b", re.I)),
    ("unsupported_scale_claim", re.compile(r"\b(validated across|6\+ projects|10\+ apps|16 P0|3 specialized agents)\b", re.I)),
    ("cross_project_promo", re.compile(r"\b(sibling projects|same opinionated taste|other small, single-author)\b", re.I)),
    ("personal_origin_story", re.compile(r"\b(killing my thumbs|I built this because|I use it every day|largely dictated)\b", re.I)),
    ("vague_ai_label", re.compile(r"\b(AI-agent|agentic|vibe|vibecoded|slop)\b", re.I)),
]


def iter_files(root: Path) -> list[Path]:
    files: set[Path] = set()
    for pattern in TEXT_GLOBS:
        files.update(root.glob(pattern))
    return sorted(p for p in files if p.is_file() and not (set(p.parts) & SKIP_PARTS))


def scan_file(path: Path, root: Path) -> list[dict[str, object]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")

    findings: list[dict[str, object]] = []
    for line_no, line in enumerate(text.splitlines(), 1):
        for rule_name, pattern in RULES:
            if pattern.search(line):
                findings.append(
                    {
                        "file": str(path.relative_to(root)),
                        "line": line_no,
                        "rule": rule_name,
                        "text": line.strip()[:240],
                    }
                )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("roots", nargs="+", type=Path)
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = parser.parse_args()

    all_findings: list[dict[str, object]] = []
    for root in args.roots:
        root = root.resolve()
        for path in iter_files(root):
            all_findings.extend(scan_file(path, root))

    if args.json:
        print(json.dumps(all_findings, ensure_ascii=False, indent=2))
    else:
        for finding in all_findings:
            print(
                f"{finding['file']}:{finding['line']} "
                f"[{finding['rule']}] {finding['text']}"
            )

    return 1 if all_findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
