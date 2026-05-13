# Contributing to harness-engineering

This repo is a **pattern document** — there's no code to compile or tests to pass. Contributions are still very welcome.

## What's in scope

### 1. Lessons learned (highest value)

If you've built a harness following this pattern (or a similar one) and hit a bug, **add it to the §Lessons learned section of README.md** as `L<n>`. Format:

```
**L15 · One-sentence rule that would have prevented the bug.**
Two-to-four sentences describing the specific failure mode, the fix, and a
verifier (test / assert / convention) that catches the same bug next time.
```

Anonymize specifics if needed, but keep them concrete. "We had a bug" is not useful; "stage 3 wrote to manifest before the database commit, and a crash mid-stage left manifest claiming `done` for an artifact that was never persisted" is gold.

### 2. New reference implementations

Built an open-source harness following the pattern? Open an issue with:

- Repo URL
- Domain / problem
- Stage count
- Validators implemented
- Which of the 7 mandatory features the harness does / doesn't have

After a quick review for "does this actually follow the pattern" I'll add a row to the §Reference implementations table.

### 3. Translations

`README.zh-CN.md`, `README-ja.md`, etc. — all welcome. Keep the structure 1:1 with the English version so cross-references stay valid.

### 4. Typo / clarity / dead-link fixes

Always welcome. Small PRs get fast review.

---

## What's out of scope

- **PRs adding a Python package wrapper.** The whole point is "no library." Pattern propagation, not library adoption.
- **PRs adding "support" for specific frameworks (LangChain, CrewAI, AutoGen).** The pattern is framework-agnostic — re-implementing it inside a framework defeats the purpose.
- **PRs renaming the project, restructuring the layout, or adding a logo.** These are bikeshed-y and the maintainer is happy with the current state.

---

## Style

- English, plain. No marketing voice.
- One short paragraph per idea. Markdown tables for comparisons. Code blocks for actual code.
- When in doubt, look at how existing sections are written and match that voice.

---

## License

By contributing you agree your contribution is MIT-licensed under the same terms as the rest of the repo.
