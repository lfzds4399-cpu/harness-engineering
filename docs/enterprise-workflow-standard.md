# Enterprise Workflow Standard

> Scope：Laolin's `D:\作品` software, harness, content and automation projects。
> Status：baseline v0.1，created 2026-05-16。
> Principle：one-person company speed，enterprise-grade traceability。

## 1. Operating Model

Every project is classified before work starts。

| Type | Examples | Required Standard |
|---|---|---|
| Product app | 福木源，TetraGG，四面体电竞 | product workflow + tests + deploy checklist |
| API service | 交易系统，token-中转站 | service workflow + health + secrets + rollback |
| Harness pipeline | methods_harness，traffic-harness，aigc工作流 | harness workflow + validators + state |
| Daemon watcher | power-watchdog-harness | daemon workflow + install / uninstall + state |
| Library / tool | ai-council，_voice2cc | library workflow + tests + README |
| Docs / governance | harness-engineering，_legal | docs workflow + review checklist |

If a project does not fit one row，write the type decision in its `CLAUDE.md` or `AGENTS.md` before implementation。

## 2. Delivery Lifecycle

### 2.1 Intake

Before code changes：

- identify project path；
- read project `CLAUDE.md` / `AGENTS.md`；
- read language rule if applicable；
- state success criteria；
- identify verification command；
- identify whether changes may affect secrets，money，production，legal or user data。

### 2.2 Plan

Use a short plan when the task has more than one step。

Plan format：

```text
1. Change：...
   Verify：...
2. Change：...
   Verify：...
```

Do not create large plans for tiny edits。

### 2.3 Implement

Rules：

- smallest diff that satisfies the request；
- no unrelated cleanup；
- no shared `_lib` unless the same code has already proven necessary in multiple projects；
- new abstractions require a concrete repeated pain；
- write files under `D:\作品` unless explicitly directed otherwise。

### 2.4 Verify

Every code change needs a verification line。

Preferred order：

1. targeted unit test；
2. project smoke test；
3. lint / type check；
4. manual UI check with browser screenshot for frontend；
5. explicit statement if verification is unavailable。

### 2.5 Handoff

End every substantial task with：

- changed files；
- verification run；
- remaining risk；
- next decision for Laolin。

Use the wording “等劳林审” for handoff，not “已完成”。

## 3. Git Standard

### 3.1 Branches

- default branch：`main` for new repositories；
- existing `master` projects may stay on `master` until there is a planned rename；
- feature branch format：`type/topic-YYYYqN`，example `docs/enterprise-workflow-2026q2`。

### 3.2 Commits

Commit shape：

```text
type(scope): English summary

中文说明：...
验证：...
```

Allowed types：

- `feat`
- `fix`
- `docs`
- `test`
- `refactor`
- `chore`
- `perf`
- `security`

### 3.3 Dirty Worktree Rule

Before edits：

- run `git status --short` in the target repo；
- do not revert files changed by the user；
- if dirty files overlap the task，read them and work with them；
- if dirty files are unrelated，ignore them。

## 4. Project Governance Files

Every active code project should have：

- `README.md`：what it is，how to run，how to verify；
- `CLAUDE.md` or `AGENTS.md`：project-specific agent context；
- `.gitignore`：secrets，logs，generated artifacts；
- dependency manifest：`pyproject.toml` / `package.json` / `requirements.txt`；
- test directory or explicit reason why no tests exist。

For private operational projects，`CLAUDE.md` may contain local paths and workflow notes。
For public repos，keep private references out of committed docs。

## 5. Harness Standard

Harness projects must first be classified：

| Harness Type | Required Entry |
|---|---|
| Pipeline | `status`，`doctor`，`run`，`audit` |
| Daemon watcher | `status`，`doctor`，`run --once`，`run --watch`，`install`，`uninstall` |
| API service | `serve`，`status`，`doctor`，`/health` |
| RAG index | `build`，`query`，`reindex`，`audit` |
| Education content | `build`，`verify`，`audit` |

Common requirements：

- quiet logging；
- captured subprocess output for agent-driven commands；
- state persistence；
- at least two validators for generated artifacts；
- deterministic audit command；
- cost tracking for external API calls。

Exception：

Library and interactive tool projects may borrow logging，config and tests without adopting full harness structure。

## 6. Quality Gates

### 6.1 Standard Gate

Required before handoff：

- `git diff --check` passes；
- relevant tests pass；
- no secret-like strings added；
- generated files are intentional；
- docs match actual commands。

### 6.2 Frontend Gate

Required before frontend handoff：

- dev server runs；
- user-facing URL opens；
- desktop and mobile screenshot checked；
- text does not overlap；
- no blank canvas or broken primary asset。

### 6.3 Service Gate

Required before service handoff：

- health check exists or explicit reason；
- env vars documented；
- secrets are not committed；
- startup command documented；
- rollback or stop command documented。

### 6.4 Harness Gate

Required before harness handoff：

- `status` can explain state；
- `doctor` catches missing dependencies；
- `audit` can run without regenerating artifacts；
- validator failure is visible and actionable；
- long-running stages do not flood stdout。

## 7. Security Standard

Never commit：

- API keys；
- private SSH keys；
- `.env` with live secrets；
- OAuth tokens；
- browser cookies；
- service account JSON。

Required patterns：

- use `secrets/.env` for local secrets；
- add `secrets/` to `.gitignore`；
- keep public examples in `.env.example`；
- block `git --no-verify` unless Laolin explicitly authorizes a one-off emergency。

## 8. Memory and Knowledge

Claude Code memory is useful but stale by default。

Rules：

- verify memory against code before asserting current state；
- project status belongs in `_meta-harness` or project docs，not global rules；
- long-lived lessons belong in global rules or `harness-engineering`；
- one-off debugging notes stay in session logs。

## 9. Agent Usage

Use subagents for parallel sidecar work，not for the immediate blocking step。

Good uses：

- independent codebase discovery；
- separate review dimensions；
- disjoint implementation areas；
- verification while local implementation continues。

Bad uses：

- delegating the next blocking action；
- asking multiple agents the same question；
- broad vague research without a concrete output。

## 10. Claude Code / Codex Parity

Claude Code and Codex should share：

- same project routing；
- same safety red lines；
- same default D drive workspace rule；
- same harness engineering standard；
- same output style；
- same verification discipline。

Implementation rule：

- update `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md` together when changing global behavior；
- update `D:\作品\AGENTS.md` and `D:\作品\CLAUDE.md` together when changing project-root behavior。

## 11. Review Cadence

Weekly：

- inspect dirty repos；
- inspect projects without `CLAUDE.md` / `AGENTS.md`；
- inspect harnesses missing validators or state；
- inspect hooks that fail silently；
- update `_meta-harness` if project status changed。

Monthly：

- archive stale projects；
- prune global rules；
- verify active project list；
- run secret scan on public repos；
- review C drive footprint。
