# harness-engineering

> Notes on a recurring layout for staged automation: validators, manifest, retries, quiet logs, one CLI.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/v-0.1-orange.svg)]()

Not a library — nothing to `pip install`. An architecture re-implemented six times across six problem domains (screen capture, voice dictation, domain investing, math PDFs, multi-voter LLM voting, file cleanup), each in its own repo with its own dependencies. What follows is the part that stays the same.

Single-author project, no external adoption yet. Treat as one person's notes, not a community standard.

---

## The shape

```
cli.py     status / doctor / run / audit         single entry point
agents/    LLM calls, HTTP, scrapes              does the work
validators/  pure-function gates                 catches mistakes
pipelines/   multi-stage orchestrate             composes the above
manifest.json  stage status + counts + cost      state of the world
configs/<artifact>.yaml                          what to build
logs/pipeline_<ts>.log                           debug surface
```

Three rules everything else falls out of:

1. **Every artifact runs through ≥ 1 deterministic validator before it ships.** A wrong-sign derivative, a -48 LUFS audio track, a 401 from a paid API — caught by the validator layer, not by whoever is eyeballing the output.
2. **Subprocess calls always use `capture_output=True`.** Inherited stdout floods the LLM context window and disappears on the next tool call. `result.stderr[-800:]` on non-zero exit is structured and inspectable.
3. **One CLI, four verbs.** `status` reads the manifest, `doctor` checks keys and deps, `run` executes a stage or all, `audit` replays validators against existing artifacts.

## Why a pattern not a framework

LangChain, CrewAI, LangGraph, Inspect — mature frameworks for model-driven pipelines already exist. Once code is decorated with `@stage`, it is coupled to that framework's ideas about state, retries, and async. Migrating two years later is a rewrite. And a video harness, a math harness, and a trading harness share nothing at the dependency level (FFmpeg vs SymPy vs CCXT) — forcing them through one framework drags in transitive deps none needs.

The transferable thing is not a base class. It is the layout: agents + validators + manifest, CLI-driven, with logs that do not flood. That stays the same across six stacks. Everything else gets re-implemented in whatever the project's language already is.

## When to use it

When the project has multiple stages that need ordering (discover → score → buy → list), cross-stage state recovery (re-run stage 4 without re-running 1–2), a mix of LLM and deterministic logic, batch artifacts each with their own success/fail status, and a cost or correctness gate.

When **not** to use it: a library (no stages, just an API surface), an interactive event loop (push-to-talk hotkey, browser extension), a one-shot migration script, or an evaluation harness — eval frameworks like Inspect already do this and are better suited than a hand-rolled equivalent.

For libs and tools, the conventions (quiet logging, subprocess capture, CLI shape) can still be adopted without the full skeleton. `ai-council` and `voice2ai` below do exactly that.

## The seven things

Every full harness implements all seven. Skipping any of them is what causes the rewrite-in-month-three trajectory.

**Validators.** Two or three deterministic ones per harness, each a pure function returning `Verdict(pass|fail|warn, evidence)`. Run them all before the artifact leaves the pipeline. Examples that have paid for themselves: `ebur128` LUFS check (a -48 LUFS music track sounds fine and is unshippable), SymPy derivative check, gitleaks regex on anything about to be published, dominant-color ΔE check against an expected hex. The rule: if a human eye or ear could miss it, the validator catches it.

**Subprocesses captured.** `subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)`. The one exception is a `run.py` a human runs interactively and wants live progress for — there, inheriting stdout is fine.

**Quiet logging.** The logging setup takes `quiet: bool = False`. Default sends INFO to console and file. Quiet sends WARNING+ to console, INFO to file. Both branches log everything to `logs/pipeline_<ts>.log`. The console is for the human watching; the file is for the postmortem.

**Manifest as source of truth.** `data/<artifact>/manifest.json` tracks `stage_status`, `count`, `provider`, `updated_at`, per-stage `cost_usd`, and exposes a `summary()` that pretty-prints. Stages marked `done` get skipped on re-run unless `--force`. Partial failures become visible.

**Retries + cost.** Every external API call goes through `retry.py`: exponential backoff, max 3, 4xx surfaces immediately, 5xx retries, optional fallback chain. Every wrapped call writes USD to the manifest. If a single CLI command cannot answer "how much has been spent today", the project has already lost track.

**The four-verb CLI.** `typer` makes it trivial. Resist adding verbs — every extra one is a surface a maintainer has to remember.

**Progress that does not flood.** Anything longer than 30s emits JSON-lines on a separate file or stderr (not stdout — that is the artifact channel) behind a `--progress json|tqdm|silent` flag. LLM-driven runs default to `silent`, humans get `tqdm`, CI gets `json`.

## Migrating an existing pipeline

Do not rewrite. Add the layers in this order, one per commit:

1. Quiet logging — touches zero business logic, unblocks LLM-driven runs.
2. Manifest — enables idempotent re-runs.
3. Validators — at least two; add more as bugs ship.
4. Subprocess capture — mostly mechanical grep+replace.
5. Retries + cost tracking — API code lives in many files, do it when the rest is stable.

Run the whole pipeline after each step. Combining steps in one commit makes the cause of a regression invisible.

## Reference implementations

| Repo | What it does | Stages |
|---|---|---|
| [claude-screen-mcp](https://github.com/lfzds4399-cpu/claude-screen-mcp) | Cross-platform screen capture + OCR for AI agents | 10 tools, conventions only |
| [voice2ai](https://github.com/lfzds4399-cpu/voice2ai) | Push-to-talk dictation, Windows | Interactive — logging/config only |
| [domain-harness](https://github.com/lfzds4399-cpu/domain-harness) | Automated domain investing | 6 stages, full pattern |
| [ai-council](https://github.com/lfzds4399-cpu/ai-council) | Multi-voter LLM consensus | Library — manifest only |
| [cleanup-harness](https://github.com/lfzds4399-cpu/cleanup-harness) | Reversible disk cleanup | 4 stages, full pattern |
| methods-harness *(private)* | SymPy-verified bilingual math PDFs | 5 stages per chapter, full pattern |

The full harnesses (domain / cleanup / methods) use all seven. The other three adopt conventions only, because they are not pipeline-shaped.

## Lessons that paid for the rules

**A music track at -48 LUFS sounded fine during preview.** End users reported "audio is broken." Fix was an `ebur128` validator failing the build below -23. Canonical example for why validators must be deterministic and not "another LLM grading the first LLM."

**"It generated something" ≠ "it generated the right thing".** A documentary stage emitted Ken Burns pan-and-zoom on still frames because the video model had failed silently. The validator now checks for frame-to-frame pixel motion above a threshold.

**LLM color descriptions are not RGB.** "Zitan red" (a reddish-brown wood) rendered as `purple`. Every color spec in a prompt now needs an explicit hex code; the validator checks dominant color against expected hex within ΔE tolerance.

**Placeholder substitution must be reverse-sorted.** `_D_1` is a prefix of `_D_10`. Replacing forward turns `_D_10` into `<value-of-D_1>0`. Use `for i in reversed(range(N))`.

**A shared `_lib/` across multiple harnesses is a trap.** Bumping one project's needs broke another. The same 50 lines of `logging_setup.py` repeated six times is fine; dependency hell across six projects is not.

**Auto-audit tools lie.** Regex audits over multi-line subprocess calls produce false positives. AST audits flag genuinely-OK calls in user-facing orchestrators. Treat auto-audit output as a candidate list, never a bug list.

**Verify the API before writing docs about it.** CONTRIBUTING.md sections have shipped describing functions that did not exist. `grep -nE "^def " src/ | sort` before mentioning any function name in user-facing prose.

## Minimum skeleton

```
<project>/
├── src/<package>/
│   ├── cli.py             # typer app: status / doctor / run / audit
│   ├── manifest.py        # load/save data/<artifact>/manifest.json
│   ├── logging_setup.py   # setup(quiet: bool = False) -> Logger
│   ├── retry.py           # @retry decorator + cost-track hook
│   ├── agents/            # one file per external service
│   ├── validators/        # >= 2 pure functions returning Verdict
│   └── pipelines/         # one file per stage
├── configs/<artifact>.yaml
├── data/<artifact>/manifest.json
├── logs/pipeline_<ts>.log
└── pyproject.toml         # typer + rich + pyyaml + python-dotenv
```

No `_lib/`, no shared base classes across projects. Repeating those 50 lines of `logging_setup.py` in every harness is the point.

## Contributing

PRs welcome on more lessons, more reference implementations, translations, and clarity fixes. PRs that wrap this in a Python package will not be merged — the point is that there is not one. See [CONTRIBUTING.md](CONTRIBUTING.md). [MIT](LICENSE).
