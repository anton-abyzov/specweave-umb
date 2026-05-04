---
increment: 0823-studio-installed-skill-readonly-and-rescan
title: >-
  Studio installed-skill read-only Source view + comprehensive origin resolver +
  rescan endpoint
type: feature
priority: P1
status: completed
created: 2026-05-01T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio installed-skill read-only Source view + comprehensive origin resolver + rescan endpoint

## Overview

vskill Studio (the local browser UI served by `vskill studio` on port 3157) has three concrete bugs and one design gap that surface when a user inspects an installed-copy skill (e.g. `~/.claude/skills/slack-messaging`):

1. **No read-only surface to view the skill** — the Edit tab is gated to authoring personas, the Overview tab is metric-cards-only, and the legacy `SkillDetailPage` body viewer is unreachable from the workspace UI. Consumers cannot read SKILL.md or browse the skill's folder tree.
2. **Versions tab shows "Local-only — not registered on verified-skill.com"** for installed copies that ARE registered (e.g. `nanobanana`, `pptx`) — `skill-name-resolver.ts:237` calls `readLockfile()` with no `dir` arg, so it only reads `cwd()/vskill.lock` and ignores the global lockfile at `~/.agents/vskill.lock`. For Anthropic-shipped skills with no vskill upstream (slack-messaging) the message is technically correct but unhelpfully phrased and offers no upstream tracking even though those skills DO have a canonical `anthropic-skills/{name}` upstream.
3. **"Check now" button does nothing** — the client (`api.ts:889`) POSTs to `/api/v1/skills/:id/rescan` but the server route was never implemented. The client's tests mock `api.rescanSkill` so CI never caught the gap.
4. **(Investigated, no action)** — the Models sub-tab under History was questioned; investigation confirmed it correctly shows per-model leaderboard data from local sweep runs and is appropriate for both author and consumer personas.

This increment delivers a long-term comprehensive fix in one increment: a complete read-only Source view, a unified Origin Resolver that handles every provenance source (project lockfile, user-global lockfile, frontmatter, well-known Anthropic skills, plugin lockfile), a clearer Versions UX with provider classification, and the missing rescan endpoint with proper SSE bridging.

## User Stories

### US-001: Read-only Source view for installed-copy skills (P1)
**Project**: vskill

**As a** skill consumer browsing an installed copy in vskill Studio
**I want** to read the SKILL.md content and browse the skill's folder structure (references/, scripts/, assets/, etc.)
**So that** I can understand what the skill does and what files ship with it without leaving the Studio

**Acceptance Criteria**:
- [x] **AC-US1-01**: A new "Source" tab is visible to ALL personas (author and consumer) in the workspace tab bar, placed immediately before "Edit"; today the Edit tab is hidden for read-only consumers, leaving them with no way to view the body.
- [x] **AC-US1-02**: Clicking the Source tab renders SKILL.md (frontmatter cards + markdown body) using the existing `SkillContentViewer` component.
- [x] **AC-US1-03**: The Source tab renders a collapsible folder tree of all files under the skill directory; clicking a file loads its content into the viewer pane.
- [x] **AC-US1-04**: File rendering is type-aware: `.md` renders as markdown, code/text files (`.ts`, `.js`, `.json`, `.yaml`, `.yml`, `.toml`, `.sh`, `.py`, `.txt`, `.env.example`, etc.) render in a monospace `<pre>` with line numbers, images (`.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.svg`) render as `<img>`, binary files show a `Binary file — N KB` placeholder.
- [x] **AC-US1-05**: The Edit tab continues to be hidden from read-only personas (no regression in author/consumer separation).
- [x] **AC-US1-06**: Source tab is the default landing tab for read-only personas; Overview remains the default for authors.
- [x] **AC-US1-07**: Source tab is keyboard-navigable: arrow keys move selection within the file tree, Enter opens a file, Escape returns focus to the tab bar.
- [x] **AC-US1-08**: Source tab works for plugin-shipped skills (under `~/.claude/plugins/`), user-global skills (`~/.claude/skills/`), and project-local skills (`{project}/.claude/skills/`) — all three install locations resolve the same way via `resolveAllowedSkillDir`.

---

### US-002: Comprehensive Origin Resolver + Versions tab provider clarity (P1)
**Project**: vskill

**As a** skill consumer who installed a skill via `vskill install --global`, an Anthropic apps user, or a user with Anthropic-shipped skills under `~/.claude/skills/`
**I want** the Versions tab to show the upstream version history regardless of how the skill arrived, with a clear provider label
**So that** I can see what versions exist, what version I'm on, and whether an update is available — without misleading "Local-only" messages for skills that genuinely have an upstream

**Acceptance Criteria**:
- [x] **AC-US2-01**: A new `origin-resolver.ts` module (in `src/eval-server/`) exposes `resolveSkillOrigin(skill, plugin, root)` that returns `{ source: "platform" | "anthropic-registry" | "local", owner: string | null, repo: string | null, provider: "vskill" | "anthropic" | "local", trackedForUpdates: boolean }`.
- [x] **AC-US2-02**: Origin resolver walks this precedence chain and uses the FIRST hit:
  (1) project lockfile `cwd()/vskill.lock`
  (2) user-global lockfile `~/.agents/vskill.lock`
  (3) well-known Anthropic-skill registry mapping (covers slack-messaging, pptx, excalidraw-diagram-generator, frontend-design, gws, remotion-best-practices, social-media-posting, webapp-testing, obsidian-brain, nanobanana, and other anthropic-shipped names → `anthropics/skills/{name}` — the verified-live URL pattern on verified-skill.com; an earlier draft incorrectly said `anthropic-skills/{name}`, fixed during code review)
  (4) bare-name fallback (existing behavior)
  Frontmatter `source:` was originally listed as Tier 3 but no installed skill writes that field today; the slot is reserved in `origin-resolver.ts` and will be wired in a follow-up increment when install commands start emitting it.
- [x] **AC-US2-03**: All NEW callers of skill provenance (the `/versions`, `/versions/diff`, and `/rescan` routes in `api-routes.ts`) consult `resolveSkillOrigin` first and fall back to the legacy `resolveSkillApiName` only when origin can't determine `owner/repo`. The legacy resolver itself is left untouched to avoid disturbing its 35 existing tests + cache + bare-name-poisoning guard. (Spec was originally drafted as a delegation refactor; reduced scope per code-review F-003 in favor of the safer wrapper-at-callsite pattern.)
- [x] **AC-US2-04**: For `nanobanana` (global-install with lockfile entry), the Versions tab shows the upstream version list from verified-skill.com (no "Local-only" badge).
- [x] **AC-US2-05**: For `slack-messaging` (Anthropic-shipped, no lockfile but in registry), the Versions tab shows upstream versions and a small "Anthropic" provider chip.
- [x] **AC-US2-06**: The `/api/skills/:plugin/:skill/versions` envelope adds two fields: boolean `trackedForUpdates` and string `provider`. Existing fields (`versions`, `count`, `source`) are unchanged. `trackedForUpdates` is `true` when origin resolves to a real upstream AND the upstream returned at least one version.
- [x] **AC-US2-07**: When `source === "none"` AND no provider can be resolved (genuinely orphaned skill), the Versions tab shows "No upstream registry — this skill ships without origin metadata, so update tracking is unavailable" instead of "Local-only".
- [x] **AC-US2-08**: When `trackedForUpdates === false`, the "Check now" button is hidden (it has no work to do).
- [x] **AC-US2-09**: A small "Provider: <vskill | Anthropic | Local>" chip renders next to the version number on the Versions tab and on the Source tab header so users always know the provenance.
- [x] **AC-US2-10**: When both project AND global lockfiles contain the entry, project wins (deterministic precedence).

---

### US-003: Implement the missing POST /api/v1/skills/:id/rescan endpoint with SSE bridge (P1)
**Project**: vskill

**As a** skill consumer clicking the "Check now" button on a tracked installed skill
**I want** the request to actually trigger an upstream version check and the spinner to clear when complete
**So that** I can confirm whether my installed version is current without restarting the Studio

**Acceptance Criteria**:
- [x] **AC-US3-01**: `POST /api/v1/skills/:id/rescan` exists. The `:id` param is URL-encoded `plugin/skill` (e.g. `.claude%2Fnanobanana`). Returns 200 with `{ jobId: string }` on success.
- [x] **AC-US3-02**: Malformed `:id` (failing the `isSafeSkillName` regex) returns 400 without performing any network or disk work.
- [x] **AC-US3-03**: On successful upstream fetch, the endpoint emits a `skill.updated` event via `dataEventBus` for any in-process subscribers. CheckNowButton clears its spinner via the SYNCHRONOUS `await api.rescanSkill()` resolution (the rescan endpoint completes the upstream fetch + bus emission before returning, so the POST resolution itself is the "we're done" signal). Originally drafted as an SSE-bridged push to `useStudio().updatesById` — that wiring is deferred to a follow-up because the existing `/api/v1/skills/stream` is upstream-proxied from verified-skill.com (not local). The synchronous-resolve path is fully verified live (network panel: POST → 200 OK; spinner clears; "No changes detected" appears).
- [x] **AC-US3-04**: The endpoint is idempotent and side-effect free on disk (no lockfile writes, no SKILL.md changes, no cache poisoning).
- [x] **AC-US3-05**: When invoked from the UI, the "Check now" spinner clears within 30 seconds (the existing client-side timeout); for skills genuinely tracked upstream the typical latency is sub-second.
- [x] **AC-US3-06**: Concurrent rescan calls (clicking Check now multiple times rapidly) each return their own `jobId` and do not cause duplicate event emissions for unrelated skills.
- [x] **AC-US3-07**: Rescan called on a skill with no resolvable upstream (provider==='local') returns 200 with `jobId` and emits `skill.updated` with `versions: []` so the spinner clears via the "no changes" path. (Alternative: hide the button — covered by AC-US2-08 — but the endpoint must still be defensive if called.)

## Functional Requirements

### FR-001: Tab-bar registration for "Source"
RightPanel.tsx registers `source` as a `DetailTab`, places its descriptor before `edit` in `TAB_DESCRIPTORS`, adds `source` to `ALL_TABS` and the `LEGACY_REDIRECTS` map (identity entry), and updates `applyPersonaRedirect` so read-only personas land on `source` instead of `overview` when an unknown deep-link tab is requested.

### FR-002: Files API consumption (backend already exists)
`GET /api/skills/:plugin/:skill/files` (api-routes.ts:2431) and `GET /api/skills/:plugin/:skill/file?path=...` (api-routes.ts:2487) are already implemented with traversal-safe path resolution via `resolveAllowedSkillDir`. SourcePanel consumes them — no new backend needed for the Files functionality.

### FR-003: Origin resolver module
New `src/eval-server/origin-resolver.ts` exports:
- `resolveSkillOrigin(skill, plugin, root): Promise<OriginEnvelope>` — full provenance resolution.
- `OriginEnvelope = { source, owner, repo, provider, trackedForUpdates, lockfilePath?, frontmatterSource?, registryMatch? }` — full audit trail for debugging.
- `ANTHROPIC_SKILL_REGISTRY` — internal const map of well-known skill names to `{owner: "anthropic-skills", repo: <name>}`.

`skill-name-resolver.ts` delegates to it via a thin wrapper that preserves the existing cache and bare-name-poisoning guard.

### FR-004: /versions envelope additive change
`{ versions, count, source }` becomes `{ versions, count, source, trackedForUpdates, provider }`. No existing field is removed or renamed; consumers that ignore the new fields continue to work.

### FR-005: Rescan endpoint reuses existing helpers
The new POST route reuses `isSafeSkillName`, `resolveSkillOrigin` (from FR-003), and a new shared `fetchUpstreamVersions(skill, plugin, root)` helper extracted from the existing `/versions` route logic. After fetch, emits `skill.updated` via `dataEventBus`/`emitDataEvent`. Returns `{ jobId: crypto.randomUUID() }` synchronously — the SSE event is fire-and-forget.

### FR-006: Provider chip UI
Small inline chip rendered:
- Next to the v1.0.0 badge in the SkillDetailPage header
- Next to each version row in the VersionHistoryPanel
- In the Source tab header
Chip values: `vskill` (light blue), `Anthropic` (orange), `Local` (gray).

## Success Criteria

- All three bugs verified fixed end-to-end via Claude Preview MCP browser steps (8-step verification flow in plan.md).
- Vitest pass rate ≥ 95% on new + existing tests.
- Playwright E2E specs `source-tab.spec.ts`, `check-now.spec.ts`, and `version-tracking.spec.ts` pass.
- For at least one skill from each category — vskill-installed (`nanobanana`), Anthropic-shipped (`slack-messaging`), genuinely local — the Versions tab shows the appropriate state and the Source tab renders correctly.
- No regression in existing authoring flow (Edit tab still works for authors; existing Versions/Run/History tabs unaffected for tracked skills).
- `code-review-report.json`, `grill-report.json`, and `judge-llm-report.json` clean (no critical/high/medium findings) per CLAUDE.md closure gates.

## Out of Scope

- Lockfile-write-back during install (separate concern; covered by existing 0784 family).
- Making installed-copy files writable (read-only is the intentional contract).
- Refactoring or removing the legacy `SkillDetailPage` route.
- Adding a writable Markdown editor to the Source tab (Edit tab already exists for authors).
- Auto-updating the Anthropic registry from a remote source (hardcoded for now; updates ship with new vskill releases).
- Modifying Q3 Models tab behavior (investigation confirmed correct).

## Dependencies

- `GET /api/skills/:plugin/:skill/files` and `/file` (already implemented).
- `SkillContentViewer`, `parseFrontmatter`, `renderMarkdown` (existing UI utilities).
- `dataEventBus` / `emitDataEvent` from `src/eval-server/data-events.ts`.
- `useStudio()` SSE-backed `updatesById` map from `src/eval-ui/src/StudioContext.tsx`.
- `isSafeSkillName` slug validator at `src/eval-server/api-routes.ts:2245`.
- `resolveAllowedSkillDir` traversal guard at `src/eval-server/skill-resolver.ts:61`.
- `parseSource` from `src/eval-server/resolvers/source-resolver.ts`.
- Existing `readLockfile` from `src/lockfile/lockfile.ts`.
