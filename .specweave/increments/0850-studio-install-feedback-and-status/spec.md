# 0850 — Skill Studio install feedback + install-state aware modal

## Problem

User-reported "Install does nothing" symptom in Skill Studio. Three root causes:

1. **Modal shows the wrong path** — `InstallTargetsModal` always renders `agent.resolvedGlobalDir` regardless of the selected scope. With the default `scope=project`, the skill writes to `<cwd>/.claude/skills/<name>` but the modal label shows `/Users/<user>/.claude/skills`, so the user looks in the wrong place and concludes nothing happened.
2. **Success state vanishes** — on `installedCount > 0` the modal auto-closes immediately (`setInstallModalOpen(false); onClose();`). No persistent confirmation, no destination path the user can copy/verify.
3. **No already-installed surfacing** — clicking Install on a skill already installed silently re-writes the same content. There is no per-agent "installed @ vX" badge, no "Update / Reinstall / Remove" affordance, and no `/api/studio/remove-skill` endpoint.

## Users

- Skill Studio users (web + desktop) installing skills from the discovery panel.

## User Stories

### US-001 — Path matches scope
**As** a user installing a skill, **I want** the modal to show the exact destination path for the selected scope **so that** I can verify the install in the right location.

**Acceptance Criteria**
- AC-US1-01 — When `scope === "project"`, each agent row shows `resolvedLocalDir` (e.g. `.claude/skills`) joined to the active project root.
- AC-US1-02 — When `scope === "user"`, each agent row shows `resolvedGlobalDir` (e.g. `/Users/.../.claude/skills`).
- AC-US1-03 — Tier 3 cloud rows keep the "Copy to clipboard" override.
- AC-US1-04 — Modal title sub-line names the scope ("Install … to project" / "… to user scope").

### US-002 — Persistent success state
**As** a user, **I want** a clearly visible success confirmation with the install path **so that** I trust the operation completed.

**Acceptance Criteria**
- AC-US2-01 — On `installedCount >= 1` the modal stays in `phase: "done"` instead of auto-closing.
- AC-US2-02 — A "Done" footer button replaces the disabled Install button and closes the modal explicitly.
- AC-US2-03 — Per-agent success rows show the absolute written path with a "Copy path" affordance.
- AC-US2-04 — Server logs every install attempt via `console.log("[install]", { skill, scope, agentIds, results })`.

### US-003 — Already-installed status
**As** a user, **I want** to see whether the skill is already installed in each tool and at what version **so that** I can choose Reinstall / Update / Remove instead of accidentally rewriting it.

**Acceptance Criteria**
- AC-US3-01 — Modal fetches `/api/studio/install-state?skill=…` on mount.
- AC-US3-02 — Each agent row that is already installed at the current target version shows a green "Installed v<X>" badge.
- AC-US3-03 — If the registry version is newer than the installed version, the badge reads "Update available v<old> → v<new>".
- AC-US3-04 — If the registry version is older than the installed version, the badge reads "Newer installed v<installed>".
- AC-US3-05 — Already-installed rows render an extra "Remove" link that hits `POST /api/studio/remove-skill { skill, agentIds, scope }` and refreshes the row to "Not installed".

### US-004 — Remove endpoint
**As** the modal, **I want** a server-side remove operation **so that** I can clean uninstall without spawning the CLI.

**Acceptance Criteria**
- AC-US4-01 — `POST /api/studio/remove-skill { skill, agentIds[], scope }` returns `{ removed: [{agentId, path}], errors: [{agentId, message}] }`.
- AC-US4-02 — Localhost-only (mirrors install-skill-routes).
- AC-US4-03 — `SAFE_NAME` + `SAFE_AGENT_ID` validation on inputs.
- AC-US4-04 — Lockfile `skills[name]` entry is dropped when no agents remain referencing it.

## Out of scope

- Per-agent destination overrides (use scope picker).
- Multi-version side-by-side installs.
- Remote uninstall via CLI spawn.
