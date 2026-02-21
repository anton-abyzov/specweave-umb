# Spec: Fix Plugin Scope & Ban Official Plugins Auto-Install

## Problem

Two policy violations were observed in the plugin system:

1. **User-scope pollution**: sw-github and sw-jira appear under the "User" section in Claude Code's plugin panel (sourced from `~/.claude/settings.json`). All specweave domain plugins must be project-scoped only.

2. **Unauthorized marketplace**: `gitlab@claude-plugins-official` was auto-installed into the project. The rule is: **only `@specweave` plugins are allowed**. The `claude-plugins-official` marketplace must never be used for auto-installation.

## Rules (enforced by this increment)

- ONLY `@specweave` plugins — NEVER `@claude-plugins-official`
- Plugin install: always `npx vskill install` (not direct copy workaround)
- Plugin scope: ALWAYS project (`.claude/commands/`) — NEVER user (`~/.claude/commands/`)
- Detection prompt must NOT suggest gitlab, firebase, slack, linear, or any official plugins

## Root Causes

**Bug A** — `install_plugin_direct()` in `user-prompt-submit.sh` line 514 hardcodes:
```bash
local target_dir="${HOME}/.claude/commands/${plugin}"  # user scope — WRONG
```
Should be `${SW_PROJECT_ROOT}/.claude/commands/${plugin}` (project scope).

The scope guard is also broken: it uninstalls from user scope, then re-runs `install_plugin_direct` which puts it back to user scope — an infinite loop.

**Bug B** — `OFFICIAL_PLUGINS` in `llm-plugin-detector.ts` lists gitlab, firebase, slack, etc. The Haiku detection prompt instructs the LLM to suggest these. The hook auto-installs them via `claude plugin install <plugin>@claude-plugins-official`.

**Bug C** — Why vskill was broken in production: `vskill-resolver.ts` resolves vskill at `<specweave-root>/../vskill/dist/cli.js` — a monorepo-only path. Production installs don't have this sibling dir, so `npx vskill` failed → v1.0.278 replaced it with `install_plugin_direct` which introduced user-scope bug.

## Acceptance Criteria

- [ ] AC-01: `install_plugin_direct()` installs to `${SW_PROJECT_ROOT}/.claude/commands/${plugin}` (project scope)
- [ ] AC-02: `OFFICIAL_PLUGINS` constant removed from `llm-plugin-detector.ts`; `ALL_VALID_PLUGINS` contains only specweave plugins
- [ ] AC-03: Detection prompt in `buildDetectionPrompt()` contains no official plugin suggestions (no gitlab, firebase, slack, etc.)
- [ ] AC-04: Hook's `claude-plugins-official` auto-install branch removed
- [ ] AC-05: Scope guard uninstalls `*@claude-plugins-official` from both user and project settings without reinstalling
- [ ] AC-06: `~/.claude/settings.json` has sw-github and sw-jira removed from enabledPlugins
- [ ] AC-07: vskill is tried first (via node + resolved path) before falling back to direct copy
- [ ] AC-08: Tests pass; no test references official plugins as valid auto-install targets
