---
increment: 0780-studio-uninstall-installed-skill
title: "Studio Uninstall Button for Installed Skills"
generated: 2026-04-26
source: hand-written
version: "1.0"
status: active
---

# Quality Contract

## Functional Correctness

- All ACs in `spec.md` map to ≥1 test in `tasks.md`.
- Server endpoint NEVER hard-deletes — always routes through OS trash.
- Path-traversal guard verified by an explicit test.
- Lockfile read+write is atomic (no partial state on crash).

## Code Quality

- No `any` in new TS.
- Reuse `trash` package (already a dep). No new shell-out commands.
- Reuse `usePendingDeletion`, `ConfirmDialog`. No new dialog primitives.
- Button copy lives in `strings.ts` (consistent with existing convention).

## Cross-Cutting

- **Performance**: O(1) lockfile op + one `trash()`. No polling added.
- **Cross-platform**: macOS / Linux / Windows via `trash` package.
- **Accessibility**: Uninstall button has descriptive `aria-label`. ConfirmDialog already a11y-clean.
- **Security**: skill-name regex + path.resolve()+startsWith() check. Hardcoded API path. No new auth surface.

## Closure Gates

- [ ] `vitest run` green for affected suites.
- [ ] `tsc --noEmit` clean.
- [ ] `sw:code-reviewer` 0 critical/high/medium.
- [ ] `sw:grill` writes report.
- [ ] `sw:judge-llm` writes report (waived if consent denied).
- [ ] Living docs synced.

## Manual Verification (User Gate)

1. Click an installed lockfile-tracked skill (e.g. greet-anton) → DetailHeader shows the Uninstall button.
2. Click Uninstall → ConfirmDialog opens with the expected copy.
3. Confirm → skill disappears from sidebar (optimistic). 10s undo banner appears.
4. Wait > 10s → check Trash; the skill folder is there. The lockfile entry is gone.
5. Re-install via `vskill install <source>` — the skill comes back.
6. Click a plugin-bundled installed skill → NO Uninstall button (correct).
7. Click a source-authored skill → existing Delete button still works (regression check).
