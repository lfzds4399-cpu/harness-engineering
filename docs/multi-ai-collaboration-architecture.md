# Multi-AI Collaboration Architecture

> Scope：Claude Code + Codex + subagents working on `D:\作品` projects。
> Status：baseline v0.1，created 2026-05-16。

## 1. Principle

Use multiple AI systems as separate roles，not as duplicate hands editing the same files。

Default split：

- Claude Code：primary implementation and long-running project execution。
- Codex：independent review，workflow governance，environment audit，standards and second-opinion checks。
- Subagents：bounded sidecar tasks with explicit ownership。

The shared truth is files and git，not chat memory。

## 2. Role Matrix

| Role | Primary Tool | Best At | Avoid |
|---|---|---|---|
| Executor | Claude Code | project-local implementation，deployment，long sessions，plugin-heavy workflows | broad governance without writing source-of-truth docs |
| Auditor | Codex | cross-project review，configuration audit，standards，risk checks，second-opinion code review | racing Claude Code on the same files |
| Specialist | Subagent | bounded file ownership，parallel review，isolated implementation slice | vague open-ended work |
| Source of truth | Git + docs | actual state | relying on memory as truth |

## 3. Track Protocol

Every long-running effort uses a track id：

```text
TRACK-YYYYQn-short-name
```

Each track records：

- objective；
- repo path；
- owner；
- status；
- current files owned；
- next action；
- verification；
- memory updated；
- last sync。

## 4. Collaboration Patterns

### 4.1 Implementation + Audit

Use when shipping features or fixes。

Flow：

1. Claude Code implements scoped changes。
2. Claude Code verifies locally。
3. Codex independently reviews diff，tests，rules and risk。
4. Durable findings go into project docs or memory。

### 4.2 Governance + Execution

Use when creating standards，processes or cross-project rules。

Flow：

1. Codex writes or updates standard docs。
2. Claude Code applies standards to project implementation。
3. Both systems reference the same standard file。

### 4.3 Parallel Slices

Use only when file ownership is disjoint。

Each slice must define：

- files owned；
- files forbidden；
- expected output；
- verification command；
- merge owner。

### 4.4 Adversarial Review

Use for high-risk tasks：money，production，legal，accounts，security，public release。

Flow：

1. Executor writes proposal or patch。
2. Auditor tries to find failure modes。
3. Executor fixes confirmed issues。
4. Final handoff lists residual risk。

## 5. Conflict Rules

If two AIs touch the same area：

1. stop further edits；
2. inspect `git status --short` and diff；
3. identify file owner；
4. preserve user changes；
5. merge the smallest safe change；
6. record the conflict in handoff。

Never resolve by reverting unknown changes。

## 6. Memory Sync

Write durable facts only。

Sync immediately：

- new workflow rule；
- repeated failure pattern；
- project status that changes roadmap；
- deployment endpoint；
- production incident；
- account index location，not secret value；
- user preference。

Do not sync：

- temporary shell output；
- speculation；
- large logs；
- unverified claims；
- one-off debug attempts。

## 7. Source-of-Truth Map

| Need | File / System |
|---|---|
| Enterprise workflow | `D:/作品/harness-engineering/docs/enterprise-workflow-standard.md` |
| Parallel track sync | `D:/作品/harness-engineering/docs/parallel-track-memory-sync-standard.md` |
| Multi-AI collaboration | this file |
| Agent and skill routing | `D:/作品/harness-engineering/docs/agent-skill-routing-standard.md` |
| Coordination bus | `D:/作品/_meta-harness/multi_ai/` |
| Cross-project status | `D:/作品/_meta-harness` |
| Claude Code long memory | `C:/Users/ssh07/.claude/projects/C--Users-ssh07/memory/` |
| Codex global rules | `C:/Users/ssh07/.codex/AGENTS.md` |
| Claude global rules | `C:/Users/ssh07/.claude/CLAUDE.md` |
| Project truth | project files + git |

## 8. Handoff Format

Every multi-AI handoff includes：

```text
Track：
Role：
Changed files：
Verification：
Memory synced：
Risks：
Next owner：
Next action：
```

## 9. Default Operating Rule

Claude Code ships the mainline。
Codex audits and governs。
Both write durable state into shared files。
Neither treats memory as truth without checking code and git。

## 10. Automation Layer

Claude Code writes lightweight coordination events through：

```text
C:/Users/ssh07/.claude/hooks/multi_ai_sync.py
```

Events append to：

```text
D:/作品/_meta-harness/multi_ai/events.jsonl
```

Codex should inspect this bus before multi-AI coordination work。
This is automatic coordination，not direct IPC。
## 11. Claude Code Codex Bridge Plugin

Local plugin source:
```text
D:/作品/harness-engineering/codex-cc-marketplace/plugins/codex-cc-bridge
```

Installed in Claude Code as:
```text
codex-cc-bridge@laurin-local
```

Commands:
- `/codex-handoff` writes a standard handoff packet into `D:/作品/_meta-harness/multi_ai/handoffs/`.
- `/codex-review` runs `codex review --uncommitted` and writes the output into `D:/作品/_meta-harness/multi_ai/codex_reviews/`.

Rule: `/codex-review` is read-only. Claude Code must not automatically apply Codex findings without Laurin approval.
