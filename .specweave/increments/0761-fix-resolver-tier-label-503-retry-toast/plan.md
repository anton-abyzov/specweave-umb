# 0761 — Plan

Four discrete fixes, all in `repositories/anton-abyzov/vskill/`. Each fix is its own US in spec.md and gets its own task block below. TDD enforced: failing test → minimal fix → green.

## F-001 (US-001): Skill-name resolver — source-tree probe

**File**: `src/eval-server/skill-name-resolver.ts`

Today `resolveSkillApiName` walks `<root>/plugins/*/skills/<skill>` only. vskill itself authors skills at `<root>/skills/<skill>` (the canonical author-side layout). When a vskill-source skill has no lockfile entry, the resolver returns the bare name and the platform proxy falls through to a same-named standalone repo.

**Change**: add a `findAuthoredSourceTreeSkillDir(root, skill)` probe that checks `<root>/skills/<skill>/SKILL.md`. Run it BEFORE `findAuthoredSkillDir` (the plugins walk) on the cache-miss / no-lockfile branch. Same git-remote → owner/repo extraction. Same isUnsafeSegment guard. Same prefix-containment guarantee.

Order in `resolveSkillApiName`:
1. cache hit
2. lockfile entry → `parseSource` (unchanged)
3. **NEW**: `<root>/skills/<skill>/SKILL.md` + git remote → `owner/repo/skill`
4. `<root>/plugins/*/skills/<skill>` + git remote → `owner/repo/skill` (unchanged)
5. bare-name fallback

## F-002 (US-002): VersionHistoryPanel uses formatTierLabel

**File**: `src/eval-ui/src/pages/workspace/VersionHistoryPanel.tsx`

Import `formatTierLabel` from `../../components/FindSkillsPalette/components/TierBadge`. Replace `{v.certTier}` (line ~376) with `{formatTierLabel(v.certTier)}`. Keep the existing `CERT_COLORS` map and badge wrapper.

## F-003 (US-003): checkSkillUpdates one-shot 5xx retry

**File**: `src/eval-ui/src/api.ts`

Wrap the `fetch(`${BASE}/api/v1/skills/check-updates`, ...)` in `checkSkillUpdates` and `resolveInstalledSkillIds` with a small helper:

```ts
async function fetchWith5xxRetry(input: RequestInfo, init?: RequestInit): Promise<Response> {
  const first = await fetch(input, init);
  if (first.status >= 502 && first.status <= 504) {
    await new Promise((r) => setTimeout(r, 250));
    return fetch(input, init);
  }
  return first;
}
```

Keep all existing catch paths and post-response handling unchanged.

## F-004 (US-004): UpdateBell toast wording for multi-location

**File**: `src/eval-ui/src/components/UpdateBell.tsx`

In the `onSelectSkill` handler, when `matched === false` and we're about to toast:
- Read the current agent's `agentId` / `agentLabel` from `useStudio` (already available indirectly — UpdateBell already reads `skills` from studio state; expose `agentId` the same way).
- If `u.installLocations` includes the current agent, render *"Also installed under {other-agent}"* (or `"Also installed under N other locations"` when `>= 2`).
- Otherwise keep the legacy *"Skill installed under {agent} — switch to {agent} to view details"*.

## Test strategy

1. F-001 — Vitest unit test on `resolveSkillApiName`. Use `tmp` dir with a fake `<root>/skills/greet-anton/SKILL.md`, fake `git config --get remote.origin.url` via the test's existing exec mock (see `skill-name-resolver.test.ts`). Assert resolved name is `<owner>/<repo>/greet-anton`. Add a precedence test (lockfile beats source-tree).
2. F-002 — Vitest UI test on `VersionHistoryPanel`. Render with two version entries; assert the badge text reads `Trusted Publisher` for `CERTIFIED`. Assert unknown tier passes through.
3. F-003 — Vitest unit test on `checkSkillUpdates`. Mock `fetch`: first call returns 503, second returns 200 with `{results:[…]}`. Assert second-call payload is forwarded. Add a 4xx-no-retry test and a success-no-retry test.
4. F-004 — Vitest UI test on `UpdateBell`. Construct an update with `installLocations` that includes the current agent + another. Assert toast text matches `"Also installed under …"`. Add a single-location-other-agent case asserting the legacy wording.

## Verification

- `npm run test --workspace=. -- src/eval-server/__tests__/skill-name-resolver.test.ts src/eval-ui/src/pages/workspace src/eval-ui/src/api.test.ts src/eval-ui/src/components/__tests__/UpdateBell` (or equivalent vitest run).
- Manual: hit `http://localhost:3162/api/skills/vskill/greet-anton/versions` after rebuild and confirm only `1.0.1` is returned.
- Manual: load Versions tab in studio; confirm badges read `Trusted Publisher`.
- Manual: open the bell with greet-anton in the list; verify toast wording when clicked from the same agent.

## Risk

- **F-001 risk**: changing resolver order. Mitigated by lockfile-first preservation and existing test coverage in `skill-name-resolver.test.ts`.
- **F-003 risk**: doubled load on the platform when 503 is sustained (not transient). Mitigated by single retry only (no exponential ladder) and the existing `[]` graceful-degrade backstop.
- Other fixes are local and isolated.
