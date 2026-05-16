# harness-engineering · Claude Code Context

## Purpose

This repository is the source of truth for Laolin's enterprise engineering workflow pattern.
It is a pattern document, not a runtime framework.

Use it to standardize:

- agent-driven delivery workflow；
- harness project structure；
- validation gates；
- Claude Code / Codex operating rules；
- cross-project review and handoff discipline。

## Commands

```powershell
git status --short
git diff -- README.md docs CLAUDE.md
```

There is currently no package install step and no test runner in this repo.
Most changes are documentation changes and should be verified by reading the rendered markdown structure and checking git diff.

## Working Rules

- Keep this repo as docs-first governance. Do not turn it into a shared Python package unless Laolin explicitly asks.
- Prefer concise standards, checklists and gate definitions over generic essays.
- When updating standards, cite the concrete failure or operational need that motivated the rule.
- Do not rewrite unrelated parts of `README.md` while adding new standards.
- Preserve `README.md.bak` unless Laolin explicitly asks to clean backup files.

## Standard Documents

- `docs/enterprise-workflow-standard.md`：enterprise-grade operating standard for AI-agent software delivery。
- `docs/claude-code-audit-2026-05-16.md`：current Claude Code setup audit and improvement backlog。

## Verification

For documentation-only changes:

```powershell
git diff --check
git status --short
```

For changes touching hooks or scripts:

```powershell
C:\Python314\python.exe -m py_compile C:\Users\ssh07\.claude\hooks\secret-guard.py
C:\Python314\python.exe -m py_compile C:\Users\ssh07\.claude\hooks\session-journal.py
C:\Python314\python.exe -m py_compile C:\Users\ssh07\.claude\hooks\battery-prompt-injector.py
```
