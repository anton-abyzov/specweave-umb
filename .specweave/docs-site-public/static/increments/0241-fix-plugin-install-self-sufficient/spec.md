# 0241: Fix Plugin Installation — Self-Sufficient First-Party Copier

## Problem
`specweave refresh-plugins` is broken for ALL production users. It shells out to `vskill` CLI which is not installed, not a dependency, and not resolvable outside the monorepo dev environment.

## Solution
Replace vskill shell-out with an inline `plugin-copier.ts` module that copies first-party plugins directly to `~/.claude/commands/<name>/`.

## User Stories

### US-001: Plugin refresh works without vskill
As a specweave user, I want `specweave update` and `specweave refresh-plugins` to install plugins without requiring vskill CLI.

- [x] AC-US1-01: `refresh-plugins.ts` uses inline copier instead of vskill shell-out
- [x] AC-US1-02: Error messages show actual failure reasons (not "Unknown error")
- [x] AC-US1-03: Hash-based skip works (unchanged plugins not re-copied)

### US-002: Plugin init works without vskill
As a new specweave user, I want `specweave init` to install the core plugin without requiring vskill.

- [x] AC-US2-01: `plugin-installer.ts` uses inline copier
- [x] AC-US2-02: `enablePluginsInSettings()` still called after install

### US-003: Lazy loading works without vskill
As a specweave user, I want on-demand plugin loading to work without `npx vskill`.

- [x] AC-US3-01: `user-prompt-submit.sh` uses direct copy instead of `npx vskill install`
- [x] AC-US3-02: Hook still checks vskill.lock as fast-path skip
