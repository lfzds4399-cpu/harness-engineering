---
allowed-tools: Bash(python:*), Bash(py:*)
description: Write a Codex handoff packet into the multi-AI coordination bus
---

Write a Codex handoff packet for the current task.

Run this command exactly once:

```bash
/mnt/c/Python314/python.exe "D:/作品/harness-engineering/codex-cc-marketplace/plugins/codex-cc-bridge/scripts/codex_bridge.py" handoff --cwd "$(wslpath -w "$PWD")" --task "$ARGUMENTS"
```

Then report the generated handoff file path and do not claim Codex has already acted on it.
