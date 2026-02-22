# 0285 — Fix vskill install nested directory bug

## Problem

Running `vskill install` from inside an agent's base directory (e.g. `~/.openclaw/`)
creates a nested path like `~/.openclaw/.openclaw/skills/remotion/` instead of
`~/.openclaw/skills/remotion/`.

Root cause: `resolveInstallBase()` blindly joins `projectRoot + localSkillsDir`. When
`projectRoot` is already the agent's base dir (e.g. `~/.openclaw/`), appending
`.openclaw/skills` creates double-nesting.

## Acceptance Criteria

- [x] AC-01: `resolveInstallBase` does NOT create nested agent dir when projectRoot ends with agent base folder
- [x] AC-02: Test proves the bug (RED before fix)
- [x] AC-03: Fix passes the test (GREEN)
- [x] AC-04: `--cwd` path also avoids nesting when cwd is inside agent dir
