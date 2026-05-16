---
allowed-tools: Bash(python:*), Bash(py:*)
description: Ask Codex CLI for a read-only second review of current uncommitted changes
---

Ask Codex CLI for a read-only second review of the current uncommitted changes.

Run this command exactly once:

```bash
/mnt/c/Python314/python.exe "D:/作品/harness-engineering/codex-cc-marketplace/plugins/codex-cc-bridge/scripts/codex_bridge.py" review --cwd "$(wslpath -w "$PWD")" --task "$ARGUMENTS"
```

Then report the generated review file path and summarize only the review result. Do not apply code changes from Codex automatically.
