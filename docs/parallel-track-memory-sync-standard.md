# Parallel Track Memory Sync Standard

> Scope：long-running parallel work across Claude Code，Codex，subagents and project repos。
> Status：baseline v0.1，created 2026-05-16。

## 1. Goal

Enable multiple work tracks to run in parallel while staying coordinated through explicit state，not through implicit chat memory。

The system must answer at any time：

- what tracks exist；
- who owns each track；
- what changed；
- what is blocked；
- what needs review；
- what memory was updated；
- what source of truth wins when records disagree。

## 2. Track Model

Each long-running effort gets a track id。

Format：

```text
TRACK-YYYYQn-short-name
```

Example：

```text
TRACK-2026Q2-token-router
TRACK-2026Q2-fumuyuan-prod
TRACK-2026Q2-harness-standard
```

Each track has：

- objective；
- repo path；
- owner；
- current state；
- next action；
- verification；
- memory targets；
- last sync timestamp。

## 3. Source of Truth

| Information | Source of Truth |
|---|---|
| Current cross-project status | `D:/作品/_meta-harness` |
| Track runbook | project `CLAUDE.md` / `AGENTS.md` |
| Enterprise workflow | `D:/作品/harness-engineering/docs/enterprise-workflow-standard.md` |
| Parallel sync protocol | this file |
| Long-lived lessons | Claude memory `feedback/` or `infra/` |
| Secrets index | Claude memory `accounts/MASTER-INDEX.md` |
| Code truth | actual repository files and git |

When sources disagree：

1. code and git win over memory；
2. project docs win over global docs；
3. `_meta-harness` wins for cross-project status；
4. memory is treated as an index，not truth。

## 4. Sync Points

### 4.1 Start of Work

Before starting a track：

- read project rules；
- read relevant memory index；
- read current git status；
- record success criteria；
- record verification command；
- record sync target。

### 4.2 During Work

After any material change：

- update local track notes or project doc；
- keep git diff scoped；
- do not rely on conversation context alone；
- if a subagent is used，give it a bounded ownership scope and output contract。

### 4.3 End of Work

Every handoff must include：

- changed files；
- verification；
- remaining risk；
- memory updated；
- next decision；
- whether `_meta-harness` needs a status update。

## 5. Realtime Memory Sync

Realtime means “after each meaningful state change”，not every token。

Sync these immediately：

- new permanent workflow rule；
- secret/account index location，not the secret value；
- project status that changes roadmap or priority；
- production incident；
- deployment endpoint；
- repeated failure pattern；
- user preference that should affect future work。

Do not sync：

- transient shell output；
- one-off debugging attempts；
- speculative ideas；
- unverified claims；
- large logs；
- generated artifacts。

## 6. Claude Code and Codex Coordination

Claude Code and Codex share the same workspace policy：

- all projects under `D:/作品`；
- global behavior mirrored between `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`；
- enterprise workflow standard stored in `harness-engineering`；
- long-lived memory indexed under Claude memory and referenced by Codex。

When Codex learns a durable rule：

1. write it into the project doc or `harness-engineering`；
2. add a Claude memory index if it should be visible to Claude Code；
3. update `~/.codex/AGENTS.md` only if it changes global behavior。

When Claude Code learns a durable rule：

1. write it into Claude memory；
2. if Codex must follow it，mirror it into `~/.codex/AGENTS.md` or `harness-engineering`；
3. verify both files remain UTF-8 readable。

## 7. Multi-Agent Coordination

Use multiple agents only when work can be split into disjoint scopes。

Each agent assignment must include：

- track id；
- repo path；
- owned files or modules；
- what not to touch；
- expected output；
- verification required；
- memory update requirement。

Do not ask multiple agents the same broad question unless doing adversarial review。

## 8. Conflict Handling

Conflict types：

- two tracks touching the same file；
- memory contradicts code；
- project doc contradicts global doc；
- dirty worktree contains user changes；
- agent result is incomplete or stale。

Resolution order：

1. stop edits in the conflicting area；
2. inspect git status and diff；
3. identify owner；
4. preserve user changes；
5. merge only the minimal necessary change；
6. record the decision in the track handoff。

## 9. Cadence

Recommended cadence：

- realtime：sync durable state after meaningful changes；
- daily：brief `_meta-harness` status sweep for active tracks；
- weekly：review dirty repos，missing project docs and stalled tracks；
- monthly：archive stale projects and prune global rules。

## 10. Minimal Track Record Template

```markdown
# TRACK-YYYYQn-name

Objective：
Repo：
Owner：
Status：active | blocked | review | paused | archived
Last sync：

Current state：
Next action：
Verification：
Memory updated：
Risks：
Decision needed：
```

## 11. Gate

A parallel track is healthy only if：

- it has a track id；
- it has a source-of-truth file；
- it has a next action；
- it has a verification command；
- it has no unowned conflict；
- its durable memory is synced。
