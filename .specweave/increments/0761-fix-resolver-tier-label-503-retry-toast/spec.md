---
status: completed
---
# 0761 — Fix studio resolver, tier-label, 503 retry, update-bell toast

## Context

While viewing `vskill / greet-anton` at `localhost:3162/#/skills/vskill/greet-anton` four user-visible defects were observed:

1. **Wrong upstream repo on Versions tab.** On-disk `repositories/anton-abyzov/vskill/skills/greet-anton/SKILL.md` is at `1.0.1`. The Versions tab shows `1.0.3 (CERTIFIED)` latest and `1.0.2 (installed)` — but those are versions of a **different** GitHub repo, `anton-abyzov/greet-anton/greet-anton` (the standalone repo). Clicking *"Update to 1.0.3"* would overwrite the in-repo skill with content from a foreign upstream. Confirmed:
   - `https://verified-skill.com/api/v1/skills/anton-abyzov/vskill/greet-anton/versions` → `1.0.1` only.
   - `https://verified-skill.com/api/v1/skills/anton-abyzov/greet-anton/greet-anton/versions` → `1.0.3, 1.0.2`.
   - The local studio at `http://localhost:3162/api/skills/vskill/greet-anton/versions` proxies to the **second** path.

2. **Tier-label nomenclature drift.** `VersionHistoryPanel.tsx:376` renders raw `{v.certTier}` (`CERTIFIED`). Elsewhere in the studio, `TierBadge.tsx` maps `CERTIFIED → "Trusted Publisher"` / `VERIFIED → "Security-Scanned"` / `TAINTED → "Tainted"`. The version timeline must use the same vocabulary so the studio reads as one app.

3. **Transient 503 from `/api/v1/skills/check-updates`.** Direct probe of the platform endpoint returns 200 reliably; the studio occasionally sees 503 (CF cold-start / transient). The frontend already handles it gracefully (`if (!res.ok) return []`) but does not retry — every blip is a red row in the network tab. Add a single 250ms-backoff retry for 502/503/504.

4. **UpdateBell toast wording for multi-location skills.** `UpdateBell.tsx:159-169` fires *"Skill installed under {agent} — switch to {agent} to view details"* whenever the click target isn't found in the current sidebar's skills list. When `greet-anton` has copies under multiple agents (verified: 6 on-disk copies including `vskill/.claude/skills/greet-anton`), the wording is misleading — the user is already viewing a valid copy. Differentiate informational ("Also installed under …") from actionable ("switch to …").

## User Stories

### US-001: Versions tab shows the correct upstream repo

**As** the studio user viewing `vskill / greet-anton` (which lives in `anton-abyzov/vskill`),
**I want** the Versions tab to fetch versions from `anton-abyzov/vskill/greet-anton`,
**So that** I do not see versions from an unrelated `anton-abyzov/greet-anton/greet-anton` repo and do not accidentally overwrite my skill with content from a foreign upstream.

**Acceptance Criteria**:
- [x] **AC-US1-01**: The eval-server resolver, when given a bare skill name AND a source-tree skill at `<root>/skills/<skill>/SKILL.md`, resolves to `{owner}/{repo}/{skill}` derived from the **enclosing repo's git remote** (e.g. `anton-abyzov/vskill/greet-anton`) — NOT a same-named standalone repo even when the lockfile points there.
- [x] **AC-US1-02**: When no source-tree skill, no lockfile entry, and no `<root>/plugins/*/skills/<skill>` match, the resolver falls back to the bare skill name (existing contract).
- [x] **AC-US1-03**: **Source-tree beats lockfile.** A `<root>/skills/<skill>/SKILL.md` is the canonical author copy; lockfile entries point at downstream installs that may live in a different upstream repo. Without this precedence the Versions tab proxies to the wrong repo and an "Update" button could overwrite the source skill with content from a foreign upstream.
- [x] **AC-US1-04**: Existing `<root>/plugins/<plugin>/skills/<skill>/` discovery path is preserved unchanged (with the same git-remote fallback) for skills with no source-tree entry and no lockfile entry.
- [x] **AC-US1-05**: The hot path (`resolverCache` hit) is unchanged — the new probe runs only on the cache-miss branch.

### US-002: Version timeline uses trust-tier nomenclature

**As** the studio user reading the Versions tab,
**I want** the same trust-tier vocabulary I see in find-palette and skill detail (`Trusted Publisher`, `Security-Scanned`, `Tainted`),
**So that** the studio reads as one app rather than two.

**Acceptance Criteria**:
- [x] **AC-US2-01**: `VersionHistoryPanel` renders `formatTierLabel(certTier)` (`CERTIFIED → "Trusted Publisher"`, `VERIFIED → "Security-Scanned"`, `TAINTED → "Tainted"`) instead of the raw `certTier` enum.
- [x] **AC-US2-02**: Unknown / missing tiers fall back to the raw value so the panel never breaks on a new tier the platform introduces.
- [x] **AC-US2-03**: Existing local-only single-version branch (`LOCAL` badge) is unchanged.
- [x] **AC-US2-04**: Existing CERT_COLORS palette is unchanged — only the text changes.

### US-003: check-updates recovers from transient 5xx invisibly

**As** the studio user idling with the bell open,
**I want** transient platform blips to resolve themselves rather than flooding the network tab with red rows,
**So that** my dev experience is quiet and the bell stays useful.

**Acceptance Criteria**:
- [x] **AC-US3-01**: `api.checkSkillUpdates` retries once after 250ms when the first response is 502 / 503 / 504. A second 5xx returns `[]` (existing graceful-degrade contract).
- [x] **AC-US3-02**: 4xx responses are NOT retried (still return `[]` immediately) — they are deterministic, retrying wastes load.
- [x] **AC-US3-03**: Network failures (thrown errors) are NOT retried — the existing catch path is unchanged.
- [x] **AC-US3-04**: The retry path applies to `resolveInstalledSkillIds` as well (same endpoint, same failure mode).
- [x] **AC-US3-05**: Successful first responses pass through unchanged with no extra fetch.

### US-004: UpdateBell toast distinguishes "also under other" from "only under other"

**As** the studio user clicking an update from the bell,
**I want** the toast to tell me whether I am already in a valid view of the skill,
**So that** I do not get told to "switch to Codex CLI" when the skill is also installed under Claude Code (the agent I am already in).

**Acceptance Criteria**:
- [x] **AC-US4-01**: If the click target's `installLocations` includes the **current agent** (per `studio.state.agentId` / `agentLabel`), the toast reads *"Also installed under {other-agent}"* (or *"Also installed under {N} other locations"* when the count of *other* agents is ≥ 2) — informational, no "switch to" verb.
- [x] **AC-US4-02**: If the click target's `installLocations` does NOT include the current agent, the existing message *"Skill installed under {agent} — switch to {agent} to view details"* is preserved.
- [x] **AC-US4-03**: If `installLocations` is empty / undefined, no toast fires (existing behaviour).
- [x] **AC-US4-04**: The toast only fires when no row in the current sidebar matches the click target (existing trigger condition is preserved).

## Out of scope

- Splitting the click handler into a smaller hook (refactor — keep the diff minimal).
- Migrating `VersionHistoryPanel` to the full `<TierBadge />` component (icon + colour). Label parity is the user-visible nomenclature ask; visual unification is deferred.
- Backend dedup of `anton-abyzov/vskill/greet-anton` vs `anton-abyzov/greet-anton/greet-anton` registrations on the platform. The studio fix above renders the correct one regardless.
