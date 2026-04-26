# 0766 — Tasks

### T-001: useSWR — error state + loading fix
**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed
**Test Plan**:
- Given a useSWR caller with a fetcher that rejects with `new Error("boom")`,
  When the hook re-renders after the rejection,
  Then `loading` is false, `error.message` is `"boom"`, `data` is undefined.
- Given a global `unhandledrejection` listener registered in the test,
  When the rejection happens,
  Then the listener is NOT called (no rethrow).
- Given the post-rejection state, when `revalidate()` is called and the next fetch succeeds,
  Then `error` clears, `data` carries the success payload.

### T-002: StudioContext.onSkillUpdated helper
**User Story**: US-002
**Satisfies ACs**: AC-US2-01
**Status**: [x] completed
**Test Plan**: Add to context value. Type the function `(plugin: string, skill: string) => void`. Document that calling it from anywhere triggers a full refresh.

### T-003: Wire onSkillUpdated through three callers
**User Story**: US-002
**Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [x] completed
**Test Plan**: Replace the partial invalidations in UpdateAction, VersionHistoryPanel, UpdateDropdown. Existing tests for these components still pass; add one new test per component asserting `onSkillUpdated` is called with the right `(plugin, skill)` after a successful update.

### T-004: mergeUpdatesIntoSkills defensive skip
**User Story**: US-002
**Satisfies ACs**: AC-US2-05
**Status**: [x] completed
**Test Plan**:
- Given a skill on disk at currentVersion=1.0.3 AND a polling update entry with installed=1.0.2 latest=1.0.3 (stale),
  When mergeUpdatesIntoSkills runs,
  Then the skill comes back without `updateAvailable: true` stamped on it.

### T-005: Build, test, publish vskill@0.5.136
**User Story**: shipping
**Status**: [x] completed
**Test Plan**: `npm run build && npm run build:eval-ui && npx vitest run src/eval-ui/src/hooks/__tests__ src/eval-ui/src/components/__tests__`. Bump `package.json` to `0.5.136`. `npm publish`. Wait for npm CDN, then `npx -y vskill@0.5.136 --version` returns `0.5.136`.

### T-006: E2E verification in preview studio
**User Story**: US-001 + US-002
**Status**: [x] completed
**Test Plan**: Start `npx -y vskill@0.5.136 studio --root <vskill-repo>`, restore greet-anton SKILL.md to v1.0.2 + lockfile to v1.0.2, navigate to `/#/skills/.claude/greet-anton`, click Update to 1.0.3, screenshot the page — Update button is gone, bell says "No updates available", Versions tab shows the timeline (no shimmer), `installed` badge is on 1.0.3.
