# 0765 — Studio: plugin-aware skill resolver + update no-op fix

## Problem

Two related symptoms reported on `2026-04-26` for `.claude/greet-anton`:

### A. Versions tab shows the wrong upstream

`http://localhost:3162/#/skills/.claude/greet-anton` (Versions tab) shows only `1.0.1` even though the user is on `1.0.2` and the platform has `1.0.3`. Header chip shows `v1.0.2` correctly (from on-disk frontmatter). The "Update to 1.0.3" button is rendered (from `/api/skills/updates`, a different code path that uses the lockfile's source). So the data IS available — only the Versions tab disagrees.

**Root cause:** [skill-name-resolver.ts:166-185](repositories/anton-abyzov/vskill/src/eval-server/skill-name-resolver.ts:166) runs the 0761 "source-tree" probe first. For `greet-anton` it finds `<root>/skills/greet-anton/SKILL.md` (the authoring source, v1.0.1, in the vskill repo) and returns `anton-abyzov/vskill/greet-anton`. That platform record only has `1.0.1`. The lockfile entry (`source: "github:anton-abyzov/greet-anton"` → `anton-abyzov/greet-anton/greet-anton` with 1.0.1/1.0.2/1.0.3) is never consulted because the source-tree branch short-circuits.

The resolver is plugin-blind. The route `/api/skills/:plugin/:skill/versions` knows the plugin (`.claude`) is an installed-agent dir, not an authoring plugin, but doesn't pass that signal down.

### B. "Update to 1.0.3" button is a silent no-op

User clicks Update. POST `/api/skills/.claude/greet-anton/update` returns 200. Disk file unchanged, header still reads `v1.0.2`.

Reproduced by hand: `cd <vskill-root>/repositories/anton-abyzov/vskill && vskill update greet-anton` prints `greet-anton: already up to date` and returns 0.

**Root cause:** The Studio's outdated detection (`/api/skills/updates`) talks to verified-skill.com (knows about 1.0.3). The CLI's `update` command ([commands/update.ts:160-200](repositories/anton-abyzov/vskill/src/commands/update.ts:160)) fetches via `fetchFromSource` against `github:anton-abyzov/greet-anton` and falls back to the SHA equality short-circuit — content hasn't changed on GitHub, so it bails as "up to date". Two sources of truth disagree on what "latest" is, and the user's update click is silently swallowed.

## User Stories

### US-001: Versions tab uses the right upstream for installed-agent-dir plugins
**As** a Studio user viewing an installed copy under `.claude/skills/<name>/` (or `.cursor/`, `.windsurf/`, etc.)
**I want** the Versions tab to list the versions of *the upstream the install came from*
**So that** I can see all available versions and tell whether an update is real.

**Acceptance Criteria:**
- [x] AC-US1-01: When `params.plugin` starts with `.` (agent dir convention), `resolveSkillApiName(plugin, skill, root)` skips the source-tree probe and consults the lockfile first.
- [x] AC-US1-02: When `params.plugin` does NOT start with `.` (authoring plugin), the existing 0761 source-tree probe runs first (no regression for source-tree skills).
- [x] AC-US1-03: Resolver cache is keyed by `(skill, plugin)` so installed and source views of the same skill name don't overwrite each other.
- [x] AC-US1-04: For `.claude/greet-anton`, the Versions tab returns 3 rows (1.0.1, 1.0.2, 1.0.3) with `isInstalled: true` on `1.0.2`.

### US-002: Update writes the new version to disk and lockfile
**As** a Studio user clicking "Update to <latest>"
**I want** the on-disk SKILL.md and the lockfile to actually reflect the new version
**So that** the header chip and Versions tab refresh to the new version.

**Acceptance Criteria:**
- [x] AC-US2-01: When the update command resolves a `newVersion` that is greater than the current lockfile version, the SKILL.md frontmatter `version:` field is rewritten to `newVersion` even if upstream content's SHA matches the local SHA (content-identical re-publish).
- [x] AC-US2-02: After update, `/api/skills/updates` no longer reports `updateAvailable: true` for that skill.
- [x] AC-US2-03: After update, the Studio header chip reads the new version on the next refresh.

## Out of scope

- Reconciling the two "latest" sources (CLI fetches GitHub HEAD, Studio fetches verified-skill.com platform). This increment makes the platform-driven update path actually update local files; the deeper "should the CLI talk to the platform first?" question is separate.
- Changing the agent-dir set. We use `startsWith('.')` as the heuristic since every supported agent dir matches it (`.claude`, `.cursor`, `.windsurf`, `.codex`, `.openclaw`, `.agent`, `.kiro`, `.gemini`, `.github`, `.aider`, `.copilot`, `.opencode`, `.pi`).
- VS Code copilot's `.github/copilot/skills/` nested structure — handled by existing skill-resolver, not affected here.
