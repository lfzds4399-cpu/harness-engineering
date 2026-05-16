# Claude Code Audit · 2026-05-16

## Summary

Claude Code is operational and already has strong automation：

- broad plugin set；
- bypass-style permissions；
- secret guard hook；
- session journal hook；
- battery reminder hook；
- project routing in global `CLAUDE.md`；
- language-specific rules。

Main weaknesses：

- global `CLAUDE.md` was mojibake in the current shell view；
- global context mixed routing，project status，old state and workflow policy；
- some hook files contain mojibake comments and output strings；
- current permission allow list is very broad；
- project docs are uneven across `D:\作品`；
- history and memory are useful but need freshness checks before being trusted。

## Findings

### 1. Global CLAUDE.md Encoding Risk

Observed：

- `C:\Users\ssh07\.claude\CLAUDE.md` rendered as mojibake in PowerShell。
- This makes rules hard to audit and may degrade prompt quality。

Action：

- Backed up the old file to `C:\Users\ssh07\.claude\CLAUDE.md.bak-before-enterprise-workflow-2026-05-16`。
- Rewrote global `CLAUDE.md` as clean UTF-8。

### 2. Hook Health

Checked：

```powershell
C:\Python314\python.exe -m py_compile C:\Users\ssh07\.claude\hooks\secret-guard.py
C:\Python314\python.exe -m py_compile C:\Users\ssh07\.claude\hooks\session-journal.py
C:\Python314\python.exe -m py_compile C:\Users\ssh07\.claude\hooks\battery-prompt-injector.py
```

Result：

- all three compiled successfully。

Residual issue：

- hook comments and some emitted Chinese strings are mojibake。
- This is not currently a syntax blocker，but it is a maintainability problem。

Recommended next action：

- rewrite hook comments and user-facing strings as clean UTF-8 in a separate hook-cleanup pass；
- keep code logic unchanged；
- run `py_compile` after each file。

### 3. Permissions

Observed：

- `defaultMode` is `bypassPermissions`。
- many tools are allowed。
- destructive commands are denied。
- `secret-guard.py` blocks common live key patterns and `--no-verify`。

Assessment：

- This matches Laolin's high-autonomy workflow。
- The risk is acceptable only because there is a deny list and secret guard。

Recommended improvement：

- add deny patterns for recursive delete / move in PowerShell forms；
- add deny patterns for writing under `C:\Windows` and `C:\Program Files` already exists；
- add deny pattern for direct deletion of `D:\作品` roots except explicit trash scripts。

### 4. Project Context Drift

Observed：

- Several active git repos lack project-level `CLAUDE.md` or `AGENTS.md`。
- Some harness projects do not expose standard `src` / `tests` / dependency markers。

Recommended improvement：

- add lightweight project context files first；
- do not force full harness layout onto libraries or interactive tools；
- prioritize dirty active repos and public repos。

### 5. Memory Freshness

Observed：

- Claude Code memory contains valuable project status。
- Some global status tables appear old or mixed with routing。

Rule：

- memory is a point-in-time index，not truth。
- code and current repo state win over memory。

Recommended improvement：

- keep global `CLAUDE.md` routing-only；
- use `_meta-harness` for live status；
- use project `CLAUDE.md` for project-specific runbooks。

## Improvement Backlog

| Priority | Item | Target |
|---|---|---|
| P0 | Rewrite global `CLAUDE.md` clean UTF-8 | done in this pass |
| P0 | Establish enterprise workflow standard | `docs/enterprise-workflow-standard.md` |
| P1 | Add `CLAUDE.md` to `harness-engineering` | done in this pass |
| P1 | Clean hook comments and emitted text | `.claude/hooks/*.py` |
| P1 | Add PowerShell destructive command deny patterns | `.claude/settings.json` |
| P2 | Add missing project rules to active repos | `D:\作品\<project>\CLAUDE.md` |
| P2 | Audit harness projects against type-specific standard | `D:\作品\*_harness*` |
| P3 | Align Codex and Claude global rules quarterly | `.codex/AGENTS.md` and `.claude/CLAUDE.md` |

## Verification

This audit used：

- `git status --short` in `D:\作品\harness-engineering`；
- `py_compile` on three Claude Code hooks；
- direct read of `settings.json` and `settings.local.json`；
- directory-level scan of `D:\作品` projects。
