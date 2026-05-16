# harness-engineering

> Reference notes for staged automation projects that need validators, state,
> logging, retries, and reproducible runs.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/v-0.1-orange.svg)]()

---

## 10-second skim

**What this is** — an architecture note for staged automation: `agents/` do the work, `validators/` check outputs, `manifest.json` stores run state, and one CLI with four verbs (`status / doctor / run / audit`) wraps it.

**What this isn't** — a Python package. There is nothing to `pip install`. Each project re-implements the pattern in its own repo and language. The transferable artifact is the *architecture*, not a library.

**Who it's for** — projects with ordered stages, batch artifacts, cost or correctness gates, and re-runnable state.

**Caveats up front** — single-author repo, six reference implementations all by the same author, zero external adoption at the time of writing. The pattern earned its shape from shipping bugs (see [Lessons learned](#lessons-learned-the-painful-ones)), but it has not yet been stress-tested by anyone other than me. Take it as one person's notes, not a community standard.

Jump to: [The pattern in one diagram](#tldr--the-pattern-in-one-diagram) · [Why a pattern not a framework](#why-a-pattern-and-not-a-framework) · [The 7 mandatory features](#the-7-mandatory-features) · [Reference implementations](#reference-implementations)

---

Automation projects often fail around the model rather than inside the model call. Retries, logs, costs, validation, and state recovery get reimplemented differently in each repo, which makes failures harder to inspect and reruns harder to trust.

This repo writes down the pipeline pattern that I re-implemented six times across six different problem domains (cross-platform screen capture / voice dictation / domain investing / educational PDFs / multi-voter LLM decisions / file cleanup) in a single-author setting. It is:

- **A pattern**, not a library — there's nothing to `pip install`. Every project implements the pattern independently in its own language with its own dependencies.
- **Opinionated** — there is exactly one answer the author settled on for "where does the manifest live?", "how do I shell out to a subprocess?", "what's the CLI surface look like?". The point of writing it down is to *stop relitigating these* inside one author's portfolio. Reasonable people can disagree.
- **Earned in one person's experience** — every rule below was added the day it would have prevented a bug shipping in *my* projects. The lessons section quotes the specific failure that taught each one. Whether the rule generalises beyond a single-author setting is an open question.

Use it when an automated stage produces an artifact, another step must validate it, and the run needs to be resumed or audited later.

---

## TL;DR — The pattern in one diagram

```
┌─────────────────────────────────────────────────────┐
│  cli.py     status / doctor / run / audit           │  ← single entry point
├─────────────────────────────────────────────────────┤
│  agents/    "Generate" — LLM calls, HTTP, scrapes   │  ← does the work
│  validators/  "Verify" — pure-function gates        │  ← catches mistakes
│  pipelines/   "Orchestrate" — multi-stage flow      │  ← composes the above
├─────────────────────────────────────────────────────┤
│  manifest.json    stage status + counts + cost      │  ← state of the world
│  configs/<artifact>.yaml   per-artifact config      │  ← what to build
│  logs/pipeline_<ts>.log    everything ever happened │  ← debug surface
└─────────────────────────────────────────────────────┘
```

Three rules of the pattern:

1. **Validators are mandatory** — every artifact runs through ≥ 1 deterministic gate before it ships. A wrong-sign derivative in a math lesson, a -48 LUFS music track, a 401 from a paid API — these are caught by the validator layer, not by a human who happens to be looking.
2. **Subprocesses are always captured** — `capture_output=True` everywhere. The agent's stdout is a structured tool result for the orchestrator, not a stream into the terminal.
3. **One CLI, four verbs** — `status` (read the manifest), `doctor` (check API keys / deps), `run` (execute one or all stages), `audit` (replay validators against existing artifacts).

Everything else is a consequence of these three.

---

## Before vs after (what adopting the pattern actually changes)

| Concern | Before the pattern | After the pattern |
|---|---|---|
| "Where did stage 3 fail last night?" | Scroll terminal scrollback, hope it wasn't lost | `harness status` reads `manifest.json` |
| "Re-run only the failed stages" | Comment-out code, hope the order is right | `harness run --stage 3` (idempotent; stages marked `done` skip) |
| "How much did I spend on the API this week?" | Open the provider dashboard | Sum of `cost_usd` in the manifest, one CLI call |
| "Why did the artifact look fine but break on review?" | Re-watch / re-read it yourself | A validator already caught it (or you add one, once, and never miss that class of bug again) |
| "Are my API keys configured?" | Run the pipeline and see what fails | `harness doctor` |
| Onboarding to a 4-month-old harness | Read every file | Read `manifest.json` + `cli.py` |

The pattern is deliberately plain. It is the same code a project would need anyway, put in predictable locations so the next codebase is easier to inspect.

---

## Why a *pattern* and not a framework

LangChain, CrewAI, LangGraph, AutoGen, Inspect — there are already mature frameworks for model-driven pipelines. They give you a `Pipeline` object, a `@stage` decorator, a vendored retry policy, a vendored logger.

The problem with frameworks-as-the-answer:

- **Lock-in to a programming model.** Once you `@stage` your code, you've coupled to a specific framework's ideas about state, retries, and async. Migrating to a different framework two years later is a rewrite.
- **Dependency hell on a per-project basis.** A video harness, a math harness, and a trading harness have nothing in common at the dependency level (FFmpeg vs SymPy vs CCXT). Forcing them through one framework drags in transitive deps that none of them needs.
- **Pattern recognition is the actual transferable skill.** Six harnesses, six independent codebases, six independent dependency trees, *the same architecture*. That architecture — agents + validators + manifest, CLI-driven, observable — is what stays the same when the framework underneath doesn't.

The pattern is documented here so that:

- Someone starting their seventh harness in a fresh language doesn't waste a week relitigating layout.
- A code review can say "this stage doesn't emit a manifest update, that's a violation of the pattern" without arguing about it.
- Lessons learned compound across projects instead of being trapped in any single repo's commit history.

---

## When to use this pattern (and when not to)

**Use it when** your project has:

- **Multiple stages that need ordering** — discover → score → buy → list, or extract → render → validate → publish.
- **Cross-stage state recovery** — re-running stage 4 after a stage-3 failure should not re-run stages 1–2.
- **A mix of LLM and deterministic logic** — some stages call an LLM (creative), others apply rules (verification).
- **Batch artifacts** — multiple lessons / domains / videos coming out of the same pipeline, each with their own success/fail status.
- **Cost or correctness gates** — you want a "did this artifact pass before we ship it" step that *fails the build* if not.

**Don't use it when** the project is one of these:

| You're building | Why this pattern is wrong |
|---|---|
| A library (`Council(voters)`, `Client(api_key)`) | No stages, no batch artifacts, no manifest needed. Just a clean API surface. |
| An interactive tool (push-to-talk hotkey, browser extension) | The event loop runs forever; there's no `run --stage all` semantics. Use this pattern's *logging* and *config* conventions only. |
| A single-shot script (`scripts/migrate_db.py`) | If it runs once and writes once, there's no pipeline. Just write the script. |
| An evaluation harness (Inspect-style) | Existing eval frameworks (Inspect, lm-eval) are already optimized for this — don't reinvent. |

For lib + tool projects you can still steal the **conventions** in this repo (quiet logging, subprocess capture, CLI shape) without adopting the full agents/validators/manifest skeleton.

---

## The 7 mandatory features

Every project that calls itself a "harness" must implement all seven. Skipping any one of them is what causes the rewrite-in-month-3 trajectory.

### 1. Validators that catch what humans miss

Add at least 2–3 deterministic validators per harness. A validator is a pure function: `validator(artifact) -> Verdict(pass | fail | warn, evidence)`. Run all of them before the artifact is allowed to leave the pipeline.

Examples that have paid for themselves:

- **Video / image**: vision-model verifier (Qwen-VL scores the frame), prompt linter (rule-based scan for known prompt-injection patterns), audio QA (`ebur128` LUFS check — a -48 LUFS music track sounds fine to the human ear and is unshippable).
- **Educational / math**: SymPy ground-truth check (every claimed derivative is verified against `diff(f, x)`), LaTeX render check (catches `$$...$$` syntax errors before PDF build).
- **Trading**: backtest runner (sanity P&L), risk check (per-trade and per-day cap), data freshness check.
- **Cross-cutting**: secret scanner (gitleaks regex pass on any artifact about to be published), cost tracker (per-stage USD running total, fails the build if monthly cap is exceeded).

**The rule**: if a human eye / ear could miss the bug, the validator catches it.

### 2. Subprocesses always captured

```python
subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
```

Never inherit stdout. Two reasons:

1. **Context pollution** — when the agent is itself driven by an LLM (Claude Code, Cursor, Devin), inherited stdout floods the LLM's context window with hundreds of lines per subprocess call, choking the conversation.
2. **Failure mode legibility** — `result.stderr[-800:]` on a non-zero exit is *structured* and inspectable. `print()` to terminal is gone the moment the agent moves to the next step.

The exception: **user-facing orchestrators** (`run.py` that a human runs interactively to see live progress) may inherit stdout deliberately. The rule applies to *agent-driven* calls.

### 3. Quiet logging that doesn't drown the conversation

Logging setup must support a `quiet: bool = False` parameter:

- **Default (`quiet=False`)**: console = INFO + file = INFO. For human dev.
- **Quiet (`quiet=True`)**: console = WARNING+, file = INFO. For LLM-driven runs — the console is the LLM's context window; the file is the audit trail.

Whatever you do, both branches log everything to `logs/pipeline_<ts>.log`. The console is for the human; the file is for the postmortem.

### 4. Manifest as the source of truth

`manifest.py` persists a `data/<artifact>/manifest.json` for every artifact, tracking:

- `stage_status: {discover: done, value: running, register: pending, ...}`
- `count`, `provider`, `updated_at`, per-stage `cost_usd`
- A `summary()` method that pretty-prints the table

Re-running becomes idempotent: stages marked `done` are skipped unless `--force`. Partial failures become visible: `status` shows exactly where it stopped.

### 5. API retries + cost tracking, always

Every external API call goes through `retry.py`:

- Exponential backoff, max 3
- Distinguish 4xx (don't retry, log and surface) from 5xx (retry)
- Optional provider fallback chain (`primary → fallback_a → fallback_b`)

Every retry-wrapped call writes its USD cost to the manifest. The manifest's `cost_usd` total is the source of truth — if you can't answer "how much have I spent today?" from one CLI command, you've already lost.

### 6. A four-verb CLI

```bash
<harness> status   # read manifest, pretty-print stage status
<harness> doctor   # check API keys, runtime deps, external tools on PATH
<harness> run      # run a stage (--stage N) or everything (--stage all)
<harness> audit    # replay validators against existing artifacts, no rerun
```

`typer` makes this trivial. Resist the urge to add more verbs — every additional verb is one more surface a maintainer has to remember.

### 7. Progress that doesn't flood

Any stage that runs longer than 30s (video generation, batch image, multi-step LLM chain) must emit progress via:

- JSON-lines on a separate file or stderr (not stdout — that's the artifact channel)
- A `--progress json|tqdm|silent` flag
- The LLM-driven default is `silent`; humans use `tqdm`; CI uses `json`

The agent reads the JSON to know "stage 4 is 60% done", not "stage 4 logged 'Processing batch 38 of 64' to stdout".

---

## Upgrading an existing project

If you have a working pipeline already, don't rewrite it. Migrate in five stages, one per commit, in this order:

| Stage | Add | Why first | Effort |
|---|---|---|---|
| **A** | quiet logging | Unblocks LLM-driven runs immediately; touches zero business logic | 30 min |
| **B** | manifest persistence | Enables idempotent reruns; touches stage transitions only | 1–2 h |
| **C** | validators (≥ 2) | Catches the bugs you're shipping today | 2–4 h |
| **D** | subprocess capture | Mechanical grep + replace; no business-logic change | 30 min |
| **E** | retry + cost tracking | Hardest — API code lives in many files; do last when the rest is stable | 4–8 h |

After each stage, run end-to-end and confirm nothing broke. **Never combine two stages in one commit** — it makes the cause of a regression invisible.

---

## Reference implementations

Five public projects following this pattern, all MIT (plus one private):

| Repo | Domain | Stage count | Validators |
|---|---|---|---|
| [**claude-screen-mcp**](https://github.com/lfzds4399-cpu/claude-screen-mcp) | Cross-platform screen capture + OCR for AI agents | 10 tools, single stage each | output byte cap, dHash channel assert, OCR allowlist |
| [**voice2ai**](https://github.com/lfzds4399-cpu/voice2ai) | Hands-free push-to-talk dictation (Windows) | Interactive — *uses pattern's logging/config only* | — |
| [**domain-harness**](https://github.com/lfzds4399-cpu/domain-harness) | Automated domain investing | 6 stages: `discover → value → acquire → list → negotiate → settle` | budget walls, trademark blacklist, dup check, AI Council |
| [**ai-council**](https://github.com/lfzds4399-cpu/ai-council) | Multi-voter LLM consensus framework | Library — *uses pattern's manifest only* | — |
| [**cleanup-harness**](https://github.com/lfzds4399-cpu/cleanup-harness) | Reversible disk-cleanup pipeline | 4 stages: `scan → classify → quarantine → confirm` | whitelist enforce, dry-run gate, undo log |
| **methods-harness** *(private)* | SymPy-verified bilingual math lesson pipeline | 5 stages per chapter | derivative / integral / factor / transform / trig-solve |

The full harnesses (domain / cleanup / methods) use all 7 mandatory features. claude-screen-mcp uses 5 (no pipelines, no batch artifacts — it's a per-call tool server). voice2ai and ai-council adopt only conventions because their shape isn't pipeline-like (see [When NOT to use](#when-to-use-this-pattern-and-when-not-to)).

---

## Lessons learned (the painful ones)

These are the bugs that earned each rule. Names anonymized; specifics preserved.

**L1 · Validators must catch the audible/visible gap.**
A music track at -48 LUFS sounded fine to the ear during preview. The user reported "audio is broken." The fix was an `ebur128` LUFS validator that fails the build on anything below -23. Every harness needs at least one validator that catches what humans miss.

**L2 · "It generated something" ≠ "it generated the right thing".**
A documentary stage used Ken Burns pan-and-zoom on still frames because the video model failed silently. Output looked like video. Was rejected on review. Fix: validator that checks for actual frame-to-frame pixel motion above a threshold.

**L3 · LLM color descriptions are not RGB.**
"Zitan red" (a specific reddish-brown wood color) was translated by an image model as `purple`. Fix: every color spec in a prompt must be accompanied by an explicit hex code, and the validator checks the rendered image's dominant color against the expected hex within ΔE tolerance.

**L4 · Placeholder substitution must be reverse-sorted.**
`_D_1` is a prefix of `_D_10`. Replacing in forward order corrupts `_D_10` into `<value-of-D_1>0`. Fix: `for i in reversed(range(N))`. Trivial in hindsight; surprisingly bug-prone in practice.

**L5 · CLAUDE.md / agent-instruction files have a token budget.**
A 15k-token project instruction file was being silently truncated by the LLM client at 8k. Project-specific details belong in per-directory CLAUDE.md / AGENTS.md, not the global one. Keep the global file to meta-rules, preferences, and an index pointing into specifics.

**L6 · Half-automated > manually-finished is a trap.**
"Click here at the end" tutorial steps always desync from reality. If a step can be scripted (Playwright, an API call, a shell command), script it — even when "it's easier this once to just do it by hand."

**L7 · Store credentials and IDs the moment you receive them.**
Discovering at 2 a.m. that you don't remember which TTS voice ID was the good one is a special kind of pain. Append to `accounts.md` (or equivalent) the moment you sign up or pick a voice.

**L8 · Don't trust a SKILL just because its name overlaps.**
Three skills called "trading" turned out to be a framework, a knowledge base, and a tactical playbook — none redundant. Before deleting a "duplicate," read the SKILL.md.

**L9 · Memory files have a half-life.**
A memory written 6 weeks ago about which library was current may be stale. When a memory cites a specific function or path, *verify the cite* (grep the repo, read the file) before acting on it. Update the memory if it's wrong.

**L10 · `_lib/` shared code is an over-engineering trap for single-author multi-harness portfolios.**
Six harnesses across six different domains (video / RAG / education / trading / cleanup / OCR) tried to share a `_lib/` and the result was a versioning nightmare. Independent code + shared *methodology* (i.e. this repo) won. The same 50 lines of `logging_setup.py` repeated six times is not a problem; dependency hell across six projects is.

**L11 · Auto-audit tools can lie — every flagged item needs a human pass.**
Regex audits over multi-line subprocess calls flag false positives. AST audits flag genuinely-OK calls in user-facing orchestrators (where inheriting stdout is the right call). Treat any auto-audit output as a *candidate list*, not a *bug list*.

**L12 · `git init` *before* the SKILL refactor, not after.**
Three projects refactored without a baseline commit and had to start from scratch when the refactor went sideways. First commit on any new repo is `chore: baseline initial commit` with zero business-logic changes. Then everything else.

**L13 · Not every project should adopt all 7 features.**
A library (`Council(voters)`) doesn't need a manifest. An interactive tool (push-to-talk loop) doesn't need pipelines. Only adopt the pattern when the project has stages + cross-stage state + batch artifacts. Otherwise borrow the conventions you like and leave the rest.

**L14 · Verify the real API before writing docs about it.**
Three projects shipped CONTRIBUTING.md sections describing functions that didn't exist (plausible-but-imaginary API names auto-generated by an LLM). The validator: `grep -nE "^def " src/ | sort` before mentioning any function name in user-facing prose.

---

## Anti-patterns

A short list of "if you find yourself doing this, stop":

- **No validators, ship directly.** You will ship a bug a human eye missed. Asked-and-answered six times.
- **Subprocess without `capture_output=True`.** Floods the LLM context. Floods CI logs. Hides errors.
- **Reading progress from stdout.** Stdout is the artifact channel. Progress goes to a different channel.
- **One file with `if stage == 1: ... elif stage == 2: ...`.** Stages are independent units; one file each, in a `pipelines/` or `stages/` folder.
- **A `_lib/` shared across multiple unrelated harnesses.** See L10.
- **Editing business logic during a logging / config / structure refactor.** Each commit does one thing. Always.

---

## Minimum viable harness (copy this skeleton)

The smallest layout that still earns the name "harness". Paste into a new repo, fill in the bodies, and you're conforming to the pattern:

```
<project>/
├── src/<package>/
│   ├── cli.py             # typer app: status / doctor / run / audit
│   ├── manifest.py        # load/save data/<artifact>/manifest.json
│   ├── logging_setup.py   # setup(quiet: bool = False) -> Logger
│   ├── retry.py           # @retry decorator + cost-track hook
│   ├── agents/            # one file per external service
│   ├── validators/        # >= 2 pure functions returning Verdict
│   └── pipelines/         # one file per stage; orchestrator imports them
├── configs/<artifact>.yaml
├── data/<artifact>/manifest.json   # written by the pipeline
├── logs/pipeline_<ts>.log
├── tests/
└── pyproject.toml         # typer + rich + pyyaml + python-dotenv
```

That's it. No `_lib/`. No shared base classes across projects. The same 50 lines of `logging_setup.py` repeated in every harness is the *point*, not a smell.

---

## Status

**v0.1 — pattern documented, six reference implementations (all by the author).** Future versions of this repo are docs-only additions:

- **v0.2** — ARCHITECTURE.md long-form deep-dive on each layer
- **v0.3** — WHEN.md decision tree for "pattern vs library vs script"
- **v0.4** — UPGRADE-PATH.md per-stage runnable example (a 200-line "before" repo + diff to "after" repo)
- **v1.0** — a polished public version of `audit.py` (the self-audit script) as a reference implementation

There is no plan to ship a Python package. The point is that you *don't need* one.

---

## Contributing

PRs welcome on:

- **More lessons learned** — if you've shipped a harness following this pattern and hit a bug not already in §L, send a PR.
- **More reference implementations** — open-source harnesses that follow the pattern get linked from §Reference implementations. Open an issue with your repo URL.
- **Translations** — `README.zh-CN.md` (or any other language) is wide open.
- **Typo / clarity fixes** — always welcome.

What I won't take:

- PRs that add a Python package wrapper. The point is that there isn't one.
- PRs that add "support" for specific frameworks (LangChain, CrewAI). The pattern is framework-agnostic on purpose.

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

[MIT](LICENSE). Use this pattern, fork it, internalise it — the goal is for the architecture to spread, not for the repo to collect stars.
