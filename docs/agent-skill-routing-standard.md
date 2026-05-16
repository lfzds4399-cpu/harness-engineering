# Agent and Skill Routing Standard

> Scope：Claude Code，Codex，and project agents under `D:/作品`。
> Status：baseline v0.1，created 2026-05-16。

## 1. Rule

Use agents and skills as routing aids，not as automatic context stuffing。

Default policy：
- Read the project rules first。
- Use the smallest relevant skill set。
- Use subagents only for bounded sidecar work with explicit file ownership。
- Do not load large skill trees unless the task names that domain。

## 2. Default Agent Routing

| Situation | Primary agent |
|---|---|
| Architecture，ownership，review strategy | `ccgs-lead-programmer` |
| Cross-project planning，track control，handoff | `ccgs-producer` |
| Security，secrets，auth，production risk | `ccgs-security-engineer` |
| CI，deployment，release，environment | `ccgs-devops-engineer` / `ccgs-release-manager` |
| Performance，memory，runtime bottlenecks | `ccgs-performance-analyst` |
| Python implementation | `voltagent-python-pro` / `voltagent-fastapi-developer` |
| TypeScript / Next.js implementation | `voltagent-typescript-pro` / `voltagent-nextjs-developer` |
| Data pipelines，ETL，analytics | `voltagent-data-engineer` / `ccgs-analytics-engineer` |
| Database schema，query performance | `voltagent-database-administrator` |
| ML infrastructure，training，model ops | `voltagent-mlops-engineer` |
| UI / UX product workflow | `ccgs-ux-designer` / `ccgs-ui-programmer` |
| Game / 3D / engine work | relevant `ccgs-*` engine specialist only |

## 3. Default Skill Routing

| Situation | Skill family |
|---|---|
| Harness，pipeline，daemon，service，RAG，render | `harness-engineering` |
| Multi-AI coordination | `agent-teams:*`，`conductor:*` |
| Code review and PR review | `code-review`，`github-code-review`，`github-pr-workflow` |
| Claude memory and CLAUDE.md maintenance | `claude-md-management:*`，`claude-mem:*` |
| Security，secrets，threat modeling | `security-scanning:*`，`developer-essentials:error-handling-patterns` |
| Python project work | `python-development:*`，`api-scaffolding:fastapi-templates` |
| Next.js / TypeScript | `frontend-mobile-development:nextjs-app-router-patterns`，`javascript-typescript:*` |
| UI，accessibility，design systems | `frontend-design`，`ui-design:*`，`accessibility-compliance:*` |
| CI / deploy / cloud | `cicd-automation:*`，`cloud-infrastructure:*`，`kubernetes-operations:*` |
| RAG / LLM application | `llm-application-dev:*` |
| Trading systems | `claude-trading-skills:*`，`agiprolabs-trading-skills:*` |
| AIGC video，cinematic workflow | `higgsfield:*`，`aigc` project rules |
| Documents，slides，spreadsheets | `documents:documents` plus Codex document tools |

## 4. Mandatory Review Triggers

Run `/codex-review` or ask Codex for a second review when a task touches：
- production。
- secrets，API keys，accounts，billing，payments。
- legal，finance，tax，visa。
- deployment，CI，hooks，settings，CLAUDE.md，AGENTS.md。
- cross-project standards。
- security-sensitive auth or permission logic。
- irreversible data migration or deletion。

## 5. Subagent Ownership

Every subagent task must include：
- owner。
- files owned。
- files forbidden。
- expected output。
- verification command。
- merge owner。

Do not run two agents on the same file set unless one is explicitly read-only review。

## 6. Context Budget Rule

Do not add every useful agent or skill to the active prompt。

Use this order：
1. Project `CLAUDE.md` / `AGENTS.md`。
2. This routing standard。
3. One or two relevant skills。
4. A bounded agent only when parallelism or specialty is useful。

The goal is better routing，not larger context。
