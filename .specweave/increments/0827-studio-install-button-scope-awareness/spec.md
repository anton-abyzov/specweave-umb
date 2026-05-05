---
increment: 0827-studio-install-button-scope-awareness
title: "Studio install button: scope clarity + installed-state awareness"
type: feature
priority: P1
status: planned
created: 2026-05-05
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio install button: scope clarity + installed-state awareness

## Overview

The Find Skills palette → SkillDetailPanel today shows three install scope buttons (`Project | User | Global`) regardless of whether the skill is already installed at any of those scopes. Live verification this session: after `npx vskill install gitroomhq/postiz-agent/postiz --scope user -y` succeeded, the panel still rendered all three buttons as if the skill were brand new.

Two related problems in one feature:

1. **Ambiguous scope labels.** "Global" is unclear — users don't know whether it means "all project-level folders like .agents/.pi/.cursor" or "every detected agent tool on the machine". The vskill CLI's `--global` flag actually fans out only to *detected* tools (CLI binary present OR `globalSkillsDir` exists) — never to all 53 agents in the registry. The behavior is correct; the label and tooltip are not.
2. **No installed-state awareness.** A button that triggers a re-install of an already-present skill with no warning is confusing. The user wants the panel to show "Installed ✓" with version + agent-tool list when a scope is already populated.

This increment ships a two-button picker (Project / User), driven by a new server-side endpoint that reports per-scope install state, with tooltips that transparently list the agent-tool destinations each scope will touch.

## User Stories

### US-001: Two-scope picker with transparent destinations (P1)
**Project**: vskill

**As a** developer using the vskill studio Find Skills palette
**I want** the install scope picker to expose only two clearly-labeled buttons (Project, User) with tooltips listing exactly which agent-tool folders each will touch on my machine
**So that** I never have to guess what "Global" means, and I can trust the button to fan out only to tools I actually use

**Acceptance Criteria**:
- [x] **AC-US1-01**: SkillDetailPanel renders exactly two scope radio buttons: Project and User. No "Global" button is rendered or reachable via DOM testing.
- [x] **AC-US1-02**: When the User button is selected and the user clicks the primary Install CTA, the POST `/api/studio/install-skill` body sends `scope: "user"` and the displayed copy-command renders ` --global` (matching today's CLI `--global` flag).
- [x] **AC-US1-03**: When the Project button is selected, the POST body sends `scope: "project"` and the copy-command renders ` --scope project` (unchanged from today — default scope stays project).
- [x] **AC-US1-04**: Hovering the Project button shows a tooltip listing the per-tool project-local destinations for tools detected on the machine (e.g., "Will install to: ./.claude/skills, ./.cursor/skills"). The list comes from `detectInstalledAgents()` filtered to tools whose `localDir` would be touched.
- [x] **AC-US1-05**: Hovering the User button shows a tooltip listing the per-tool user-home destinations for detected tools (e.g., "Will install to: ~/.claude/skills, ~/.cursor/skills").
- [x] **AC-US1-06**: Default selected scope on panel mount remains "project" (preserves existing UX from line 215 of SkillDetailPanel.tsx — no test regression at SkillDetailPanel.test.tsx:275/302/346/398).

---

### US-002: Per-scope install-state awareness (P1)
**Project**: vskill

**As a** developer who has already installed a skill at one scope
**I want** the panel to show "Installed ✓" with the installed version and which agent tools picked it up, and to disable the corresponding scope button
**So that** I don't accidentally re-trigger an install of something I already have, and I can see at a glance where each skill lives

**Acceptance Criteria**:
- [x] **AC-US2-01**: The eval-server exposes `GET /api/studio/install-state?skill=<publisher>/<slug>` that returns `{ skill, detectedAgentTools[], scopes: { project, user } }` per the contract in plan.md §A.
- [x] **AC-US2-02**: Endpoint marks `scopes.user.installed = true` when the row builder finds a skill row with `origin === "installed"` AND legacy `scope === "global"` AND a non-empty `sourceAgent`.
- [x] **AC-US2-03**: Endpoint marks `scopes.project.installed = true` when the row has `origin === "installed"` AND legacy `scope === "installed"` (project-local agent dir).
- [x] **AC-US2-04**: For a skill never installed, the endpoint returns `installed: false`, `installedAgentTools: []`, `version: null` for both scopes — without throwing.
- [x] **AC-US2-05**: Endpoint is localhost-only — non-loopback `req.socket.remoteAddress` returns 403 (mirrors install-skill-routes.ts:49).
- [x] **AC-US2-06**: When `installState.scopes.user.installed === true`, the User scope button renders as a disabled button with text "Installed ✓ User", `aria-disabled="true"`, and a tooltip of the form `"Installed v<version> · <agent-tool ids comma-joined>"`.
- [x] **AC-US2-07**: Same disabled-state contract applies to the Project button when `installState.scopes.project.installed === true`.
- [x] **AC-US2-08**: The primary Install CTA button (data-testid `skill-detail-install-primary`) is disabled when the *currently selected* scope reports `installed: true`, and its tooltip explains why ("Already installed at <scope> — re-run via CLI to force").
- [x] **AC-US2-09**: After a successful install (existing `studio:skill-installed` CustomEvent fires per SkillDetailPanel.tsx:454-456), the panel re-fetches `/api/studio/install-state` and updates the disabled-state of buttons without a manual reload.

---

### US-003: Increment doesn't break existing install copy/SSE pipeline (P1)
**Project**: vskill

**As a** developer relying on the existing copy-to-clipboard and SSE install-job flows
**I want** every existing test in SkillDetailPanel.test.tsx and install-skill-routes.test.ts to keep passing
**So that** this UX overhaul ships as a pure addition + relabeling, not a regression

**Acceptance Criteria**:
- [x] **AC-US3-01**: Existing assertions on the npm copy-command at lines 275/302/346/398 of SkillDetailPanel.test.tsx (default scope = project, command contains `--scope project`) continue to pass with no edits to those test cases.
- [x] **AC-US3-02**: The existing POST `/api/studio/install-skill` route in install-skill-routes.ts is unchanged — no schema, body, or status-code differences. Existing route tests pass.
- [x] **AC-US3-03**: SSE `studio:skill-installed` CustomEvent payload shape is unchanged (`{ skill, scope }` with scope still typed as `"project" | "user" | "global"` for backwards compatibility — even though the UI no longer emits "global", legacy listeners that match it still work).
- [x] **AC-US3-04**: Install-state fetch is non-blocking — if the new endpoint returns 5xx or hangs, the panel still renders the install controls (defaulting to "not installed" optimistically) and the user can still install. A console warning is logged once per session.

## Functional Requirements

### FR-001: Endpoint contract for /api/studio/install-state
Response shape per plan.md §A:
```ts
{
  skill: string,                          // requested skill, echoed back
  detectedAgentTools: Array<{
    id: string,                           // agent registry id, e.g. "claude-code"
    displayName: string,                  // human label, e.g. "Claude Code"
    localDir: string,                     // e.g. ".claude/skills" (relative)
    globalDir: string                     // e.g. "~/.claude/skills" (tilde-expandable)
  }>,
  scopes: {
    project: { installed: boolean, installedAgentTools: string[], version: string | null },
    user:    { installed: boolean, installedAgentTools: string[], version: string | null }
  }
}
```
Implementation reuses `detectInstalledAgents()` (agents-registry.ts:853) and `scanSkillsTriScope` / `enrichAndComputePrecedence` (api-routes.ts:1896-1976). Localhost-only guard.

### FR-002: Client state machine
SkillDetailPanel narrows `InstallScope` to `"project" | "user"`. `scopeFlag()` maps:
- `"project"` → ` --scope project`
- `"user"`    → ` --global`

The third (`"global"`) branch is removed. Scope picker `.map(["project", "user", "global"])` becomes `.map(["project", "user"])`.

Panel mounts → parallel fetches metadata + versions + install-state (third addition to existing line 246 Promise.all). On `studio:skill-installed` event, install-state is re-fetched.

### FR-003: Tooltip contracts
- Enabled Project tooltip: `Will install to: <comma-joined detectedAgentTools.localDir prefixed with ./>` — example: `Will install to: ./.claude/skills, ./.cursor/skills`.
- Enabled User tooltip: `Will install to: <comma-joined detectedAgentTools.globalDir>` — example: `Will install to: ~/.claude/skills, ~/.cursor/skills`.
- Disabled (installed) tooltip: `Installed v<version> · <comma-joined installedAgentTools ids>` — example: `Installed v2.0.12 · claude-code`.

## Success Criteria

- All US-001/2/3 ACs satisfied with TDD red→green→refactor evidence per task.
- Vitest suite green: `src/eval-server/__tests__/install-state-routes.test.ts` (new, ≥5 cases) + `src/eval-ui/src/components/FindSkillsPalette/__tests__/SkillDetailPanel.test.tsx` (extended ≥5 cases).
- Live verification on localhost:3114 against locally-built bundle: postiz panel shows "Installed ✓ User" disabled, Project button enabled with tooltip listing project-local destinations.
- No regression in the 24 existing SkillDetailPanel test cases or the install-skill-routes route tests.
- Coverage target ≥90% on new files (install-state-routes.ts).

## Out of Scope

- Uninstall affordance in the studio UI (CLI-only for MVP — confirmed via AskUserQuestion).
- Update-version path beyond what the existing version selector already provides (re-installing a different version by selecting it from the existing version dropdown is unaffected).
- Fixing the literal `postiz: ../../SKILL.md` description rendering bug (separate increment — host plugin loader follows readlink → string instead of resolving target).
- Fixing the 431 SSE storm caused by `csvForSubscribe = skillsCsv || trackingCsv` in `useSkillUpdates.ts` (separate increment).
- New CLI flags or behavior changes to `vskill install` — `--scope project`, `--scope user`, and `--global` semantics are unchanged. Only the studio UI's surfacing changes.
- A user-curated allow-list for which agent tools to fan out to (deferred — current `detectInstalledAgents()` heuristic is sufficient for MVP per AskUserQuestion).
- Adding new agent-tool integrations beyond the existing 53 in agents-registry.ts.

## Dependencies

- Existing `detectInstalledAgents()` from `src/agents/agents-registry.ts:853-915`.
- Existing `scanSkillsTriScope` + `enrichAndComputePrecedence` from `src/eval-server/api-routes.ts:1896-1976`.
- Existing `vskill.lock` schema with `scope?: "user" | "project"` field from `src/lockfile/types.ts:5-27`.
- Existing `studio:skill-installed` CustomEvent broadcaster at `SkillDetailPanel.tsx:454-456`.
- Existing localhost-guard helper pattern at `install-skill-routes.ts:49`.
