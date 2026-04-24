---
increment: 0706-vskill-cli-windows-compat
title: "Windows compatibility fixes for vskill install/update/studio"
generated: "2026-04-24T18:58:00.000Z"
source: auto-generated
---

# Quality Contract

## Coverage

- Unit test coverage on modified files ≥ 90%.
- Each of the 5 bugs has at least one platform-specific unit test with `process.platform` mocked.

## Correctness Gates

- **Zero regressions on macOS/Linux**: all existing CI jobs (ubuntu-latest, macos-latest) remain green.
- **windows-latest CI job passes** on 3 consecutive runs before merge.
- `vskill install --help`, `update --help`, `studio --help` exit 0 on Windows.
- Smoke install of a test skill on Windows detects at least one agent OR prints graceful "no agents detected" message (NOT a crash).

## Cross-Platform

- NO new uses of `which`, `&&`, `~`, `2>/dev/null`, `lsof`, POSIX `ps`, or hardcoded `/` separators in modified code.
- `symlinkSync` calls ALWAYS have an EPERM/EACCES fallback.
- `path.relative(base, target).startsWith("..")` used consistently for traversal guards.
- Windows-specific warning ("Symlinks not available...") logged exactly once per process.

## Review Gates

- [x] `sw:code-reviewer` passes with 0 critical/high/medium findings. — PASS 2026-04-24 (re-review): 0 critical, 0 high, 0 medium, 3 low, 2 info. Previous F-01 resolved in commit ad6a24a (install-smoke uses `-y` flag + exits on crash codes). See `reports/code-review-report.json`.
- [x] `sw:grill` report clean. — PASS 2026-04-24: verdict PASS, ship READY. All 17 ACs verified against code + tests (17/17 pass). 0 critical, 0 high, 2 medium (G-M1 DRY cleanup across path-traversal guards; G-M2 AC-US3 spec/impl wording drift — both non-blocking maintainability). See `reports/grill-report.json`.
- Manual gate: reviewer with access to a Windows VM confirms `vskill install scout` installs into at least one agent without errors.
