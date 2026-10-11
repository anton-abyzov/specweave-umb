# Consolidate agent skills across tools

## Problem

Skills on Anton's M4 and in this umbrella are duplicated, diverged and partly broken across the agents he uses (Claude Code, Codex, OpenCode, Antigravity, Grok, Cursor, Copilot, Gemini). Evidence, 2026-10-11:

- `~/.claude/skills` and `~/.agents/skills` hold two real copies of most personal skills. 21 differ. The `~/.agents` copies were produced by OpenAI's `migrate-to-codex`, which rewrote "Claude" to "Codex" (even `.claude/` to `.Codex/`), dropped `version`/`license`, and appended "## MANUAL MIGRATION REQUIRED" to 9 skills. Some `~/.agents` copies also carry newer real edits.
- `~/.agents/skills/social-media-posting-skill` declares `name: social-media-posting`, so Grok (`grok inspect --json`) loads two different skills under one name.
- `~/.config/opencode/skills`, `~/.cursor/skills`, `~/.copilot/skills`, `~/.gemini/skills` and `~/.grok/skills` hold symlinks to skills those agents already read from `~/.agents/skills` or `~/.claude/skills` (per each agent's docs), so the same skill is listed two or three times. `~/.gemini/antigravity/skills/find-skills` is a broken link.
- The Claude plugin cache `~/.claude/plugins/cache/specweave/sw/2.1.0` holds 3.0.12 content plus files 3.x no longer ships (the `qa` skill, old `lib/`), because `syncNativePluginContent` copies over the cache without deleting removed files. Claude and Grok still offer `sw:qa`.
- The umbrella's `.agents/skills` keeps `sw-qa` and `sw-team/agents/` that SpecWeave 3 no longer installs; `installProjectSkills` never removes retired `sw-*` folders.
- The umbrella gitignores `.claude/` and `.agents/`, so the `sw-*` skills that CLAUDE.md says "load in cloud sessions too" are never committed.
- vskill's agent registry is out of date with the agents' docs: Codex is mapped to `.codex/skills` (Codex reads `.agents/skills`), Antigravity to legacy `.agent/skills`, Copilot CLI project scope to `.copilot/skills` (docs: `.github/skills`), and Grok has no entry. vskill also links skills into agents that already read the shared `.agents/skills`, which creates the duplicates above.

## Scope

In: SpecWeave plugin-cache mirror and retired project-skill cleanup; vskill registry corrections, duplicate-free linking and a `vskill doctor` check/fix for skill folders; consolidating this Mac's global skills and the umbrella's project skills; committing the umbrella's `sw-*` skills.
Out: Studio's skill scanners and a Studio Skills panel (follow-up increment), the tutorials and website (follow-up increments), renaming SpecWeave Studio.

## Acceptance Criteria

- [ ] AC-01: `syncNativePluginContent` leaves each install path an exact mirror of the plugin source (files the source no longer ships are removed; Claude's own root dotfiles such as `.in_use` are kept), and refuses install paths outside `~/.claude/plugins/cache`.
- [ ] AC-02: `installProjectSkills` removes `sw-*` folders and files SpecWeave no longer ships (e.g. `sw-qa`, `sw-team/agents/`) when they are SpecWeave-owned, and leaves user folders alone.
- [ ] AC-03: vskill's registry matches the agents' current docs for Codex, Antigravity, Copilot CLI and Grok, and records which agents read the shared `.agents/skills` per scope.
- [ ] AC-04: `vskill install` does not create an agent-specific link for an agent that already reads the shared `.agents/skills` in that scope.
- [ ] AC-05: `vskill doctor` reports divergent same-name copies, broken links, redundant links, `migrate-to-codex` damage, name/folder mismatches, over-long descriptions and two folders declaring one name; `--fix` removes broken and redundant links and replaces byte-identical copies with links, never touching divergent content.
- [ ] AC-06: On the M4, every personal skill exists once as a real folder in `~/.agents/skills` with migration damage removed and genuine edits kept, `~/.claude/skills` links to it, no agent lists a skill twice, and `vskill doctor` reports no problems; a backup of the previous state exists.
- [ ] AC-07: The umbrella's project skills match what SpecWeave and `vskill.lock` install (no retired `sw-*`, no stray copies), and the `sw-*` skills are committed so cloud sessions load them.

## Approach

Canonical store is `.agents/skills` (agentskills.io client guide; read natively by Codex, OpenCode, Gemini CLI, Cursor, Copilot and Grok's user scope). Claude Code does not read it, so Claude gets a link (POSIX) or a copy (Windows fallback) in `.claude/skills`. Antigravity's global folder does not read it either, so it keeps links. Every other agent-specific link is redundant and removed.

Files, in order: `specweave/src/utils/plugin-copier.ts` (mirror), `specweave/src/core/skills/project-skills.ts` (retired cleanup); `vskill/src/agents/agents-registry.ts`, `vskill/src/installer/canonical.ts`, new `vskill/src/commands/doctor.ts`; then the M4 consolidation (merged content staged in the session scratchpad, applied after `vskill doctor` from the worktree build) and the umbrella `.gitignore`.

Rejected: picking one side wholesale for the diverged skills (loses real edits on either side); deleting `~/.claude/skills` copies without links (Claude stops seeing them); keeping per-agent copies (they diverge again).

Risks: personal skills are live for every agent on the M4. Mitigation: full tarball backup at `~/.skills-backups/agent-skills-20261011-003247.tgz` before any change, and the doctor never rewrites divergent content.

## Open questions

- none

## Tasks

### T-01 Mirror plugin content into the Claude plugin cache
- AC: AC-01 | Files: repositories/anton-abyzov/specweave/src/utils/plugin-copier.ts, repositories/anton-abyzov/specweave/tests/unit/utils/plugin-copier-sync-mirror.test.ts | Test: cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0894-specweave && npx vitest run tests/unit/utils/plugin-copier-sync-mirror.test.ts

### T-02 Remove retired sw-* project skills
- AC: AC-02 | Files: repositories/anton-abyzov/specweave/src/core/skills/project-skills.ts, repositories/anton-abyzov/specweave/tests/unit/core/skills/project-skills-retired.test.ts | Test: cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0894-specweave && npx vitest run tests/unit/core/skills/project-skills-retired.test.ts

### T-03 Correct vskill's agent registry and skip redundant links
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/vskill/src/agents/agents-registry.ts, repositories/anton-abyzov/vskill/src/agents/agents-registry.test.ts, repositories/anton-abyzov/vskill/src/installer/canonical.ts, repositories/anton-abyzov/vskill/src/installer/canonical.test.ts | Test: cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0894-vskill && npx vitest run src/agents src/installer

### T-04 vskill doctor for skill folders
- AC: AC-05 | Files: repositories/anton-abyzov/vskill/src/commands/doctor.ts, repositories/anton-abyzov/vskill/src/commands/doctor.test.ts, repositories/anton-abyzov/vskill/src/index.ts | Test: cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0894-vskill && npx vitest run src/commands/doctor.test.ts

### T-05 Consolidate the M4's global skills
- AC: AC-06 | Files: none (machine state; merge report in the session scratchpad) | Test: node /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0894-vskill/dist/index.js doctor --global

### T-06 Consolidate and commit the umbrella's project skills
- AC: AC-07 | Files: .gitignore, .claude/skills, .agents/skills | Test: cd /Users/antonabyzov/Projects/github/specweave-umb/.claude/worktrees/0894-umb && git ls-files .claude/skills .agents/skills | grep -c "sw-.*/SKILL.md" | grep -qx 22 && test ! -e /Users/antonabyzov/Projects/github/specweave-umb/.agents/skills/sw-qa && test ! -e /Users/antonabyzov/Projects/github/specweave-umb/.claude/skills/hyperframes
