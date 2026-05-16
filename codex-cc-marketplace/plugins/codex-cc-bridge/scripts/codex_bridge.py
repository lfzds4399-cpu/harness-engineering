#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


BUS_ROOT = Path("D:/作品/_meta-harness/multi_ai")
HANDOFF_DIR = BUS_ROOT / "handoffs"
REVIEW_DIR = BUS_ROOT / "codex_reviews"
EVENTS_PATH = BUS_ROOT / "events.jsonl"


def now_stamp() -> str:
    return datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")


def run_capture(args: list[str], cwd: Path) -> str:
    try:
        proc = subprocess.run(
            args,
            cwd=str(cwd),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=60,
        )
    except Exception as exc:
        return f"COMMAND FAILED: {' '.join(args)}\n{exc}\n"
    out = proc.stdout.strip()
    err = proc.stderr.strip()
    body = out
    if err:
        body = f"{body}\n\nSTDERR:\n{err}" if body else f"STDERR:\n{err}"
    return body.strip() or f"exit_code={proc.returncode}"


def append_event(event_type: str, cwd: Path, task: str, artifact: Path) -> None:
    BUS_ROOT.mkdir(parents=True, exist_ok=True)
    event = {
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source": "claude-code-plugin",
        "event_type": event_type,
        "cwd": str(cwd).replace("\\", "/"),
        "task": task[:240],
        "artifact": str(artifact).replace("\\", "/"),
    }
    with EVENTS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")


def git_context(cwd: Path) -> tuple[str, str, str]:
    status = run_capture(["git", "status", "--short"], cwd)
    branch = run_capture(["git", "branch", "--show-current"], cwd)
    diff_stat = run_capture(["git", "diff", "--stat"], cwd)
    return status, branch, diff_stat


def write_handoff(task: str, cwd: Path) -> Path:
    HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
    status, branch, diff_stat = git_context(cwd)
    artifact = HANDOFF_DIR / f"{now_stamp()}-claude-to-codex.md"
    artifact.write_text(
        "\n".join(
            [
                "# Claude Code to Codex Handoff",
                "",
                f"- Track: TODO",
                f"- Role: Claude Code -> Codex",
                f"- CWD: {str(cwd).replace(chr(92), '/')}",
                f"- Branch: {branch}",
                f"- Task: {task or 'No task argument supplied.'}",
                "",
                "## Git Status",
                "",
                "```text",
                status,
                "```",
                "",
                "## Diff Stat",
                "",
                "```text",
                diff_stat,
                "```",
                "",
                "## Requested Codex Action",
                "",
                "- Review risk, missing verification, and ownership conflicts.",
                "- Do not apply changes unless Laurin explicitly asks Codex to take over.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    append_event("codex_handoff_created", cwd, task, artifact)
    return artifact


def run_codex_review(task: str, cwd: Path) -> Path:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    artifact = REVIEW_DIR / f"{now_stamp()}-codex-review.md"
    prompt = "\n".join(
        [
            "Review current uncommitted changes from a code-review stance.",
            "Do not modify files.",
            "Lead with findings. Include file and line references where possible.",
            "Focus on correctness, security, behavioral regressions, missing verification, and instruction compliance.",
            f"Extra task context: {task or 'No extra task context.'}",
        ]
    )
    codex_bin = shutil.which("codex") or "codex"
    title = (task or "Claude Code uncommitted review")[:120]
    try:
        proc = subprocess.run(
            [codex_bin, "review", "--uncommitted", "--title", title],
            cwd=str(cwd),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=900,
        )
        output = proc.stdout.strip()
        if proc.stderr.strip():
            output = f"{output}\n\nSTDERR:\n{proc.stderr.strip()}" if output else f"STDERR:\n{proc.stderr.strip()}"
        if proc.returncode != 0:
            output = f"codex review exit_code={proc.returncode}\n\n{output}"
    except Exception as exc:
        output = f"codex review failed: {exc}"
    artifact.write_text(output.strip() + "\n", encoding="utf-8")
    append_event("codex_review_created", cwd, task, artifact)
    return artifact


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["handoff", "review"])
    parser.add_argument("--task", default="")
    parser.add_argument("--cwd", default=os.getcwd())
    args = parser.parse_args()

    cwd = Path(args.cwd).resolve()
    if args.command == "handoff":
        artifact = write_handoff(args.task, cwd)
    else:
        artifact = run_codex_review(args.task, cwd)
    print(str(artifact))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
