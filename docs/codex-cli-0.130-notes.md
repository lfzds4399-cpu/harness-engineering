# Codex CLI 0.130 兼容笔记

> 写于 2026-05-16，福木源 session bridge fix 落地后。
> 跨项目知识：任何 codex-cc-bridge 类型工具都受 codex CLI 行为影响。

## 1. `codex review --uncommitted` 不能配 `[PROMPT]`

错的：
```bash
codex review --uncommitted -          # 试图 stdin 接 prompt
codex review --uncommitted "<task>"   # 试图 inline prompt
```

会立刻报：
```
error: the argument '--uncommitted' cannot be used with '[PROMPT]'
exit code 2
```

对的：
```bash
codex review --uncommitted --title "<task context here>"
```

`--title` 是注入 task context 的唯一通道。`--uncommitted` 自己读 working tree 的 staged + unstaged + untracked diff，不需要也不接受外部 prompt。

## 2. Windows 下 subprocess 调 codex 必须 `shutil.which`

错的：
```python
subprocess.run(["codex", "review", "--uncommitted", "--title", title])
```

会报：
```
[WinError 2] 系统找不到指定的文件
```

原因：npm 全局装的 codex 在 Windows 是 `codex.cmd` shell wrapper（不是 `codex.exe`）。`subprocess.run` 默认不带 `shell=True`，不展开 PATHEXT，找不到 `.cmd`。

对的：
```python
import shutil
codex_bin = shutil.which("codex") or "codex"
subprocess.run([codex_bin, "review", "--uncommitted", "--title", title])
```

`shutil.which` 走 PATHEXT 解析，返回真路径 `C:\Users\<user>\AppData\Roaming\npm\codex.cmd`。

## 3. `--uncommitted` 行为

- 读 staged + unstaged + untracked
- 不需要 `git add`
- 输出有 STDERR 副频道（含 model / sandbox / session id）和 STDOUT review 内容
- 1k-3k 文件的 working tree 输出 100KB+ md（含 Codex 阅读 SKILL.md / CLAUDE.md 等文件的 dump）

## 4. bridge 集成最佳实践

- 用 `capture_output=True` 避免 stderr 噪声入 review artifact
- timeout 900s（Codex 实际跑 30s-3min）
- subprocess output 用 `text=True, encoding="utf-8", errors="replace"`，避免中文路径报错

## 5. 验证流程（任何 bridge 升级后）

```bash
cd "D:/作品/<test project>"
/c/Python314/python "D:/作品/harness-engineering/codex-cc-marketplace/plugins/codex-cc-bridge/scripts/codex_bridge.py" review --cwd "$(pwd -W)" --task "smoke test"
```

确认：
- exit 0
- 生成 `D:/作品/_meta-harness/multi_ai/codex_reviews/<timestamp>-codex-review.md`
- 文件 head 不是 `codex review failed: ...`

## 参考

- bridge 源：`D:/作品/harness-engineering/codex-cc-marketplace/plugins/codex-cc-bridge/scripts/codex_bridge.py`
- review 历史：`D:/作品/_meta-harness/multi_ai/codex_reviews/`
- 福木源 session 实证：`20260516-171840` (旧 stdin -) `20260516-172020` (--uncommitted+stdin 冲突) `20260516-172215` (--title 通过)
