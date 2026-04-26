# Implementation Plan: vskill-platform — skill page must always render

## Overview

Tiny, surgical bug fix in **two catch blocks** of `repositories/anton-abyzov/vskill-platform/src/lib/data.ts`. The page render contract at `src/app/skills/[owner]/[repo]/[skill]/page.tsx:152-163` is **unchanged** — it already treats a `null` return from the fallback queries as "not blocked / not rejected" and falls through to `notFound()`. We just stop the two outlier functions from rethrowing.

## Design

### Components touched

| File | Change | Why |
|------|--------|-----|
| `src/lib/data.ts` | Replace `throw err` with `return null` in `getBlocklistEntryBySkillName` (line 296-301) and `getRejectedSubmissionBySkillName` (line 352-357) catch blocks | Align with `getSkillByLegacySlug` (line 251-254). Stop the canonical skill page from crashing on a transient DB hiccup during the 404-fallback path. |
| `src/lib/__tests__/data-failsoft.test.ts` (new) | Vitest tests for the four AC scenarios + warn-spy assertions | TDD red→green for the change. |
| `tests/e2e/skill-not-found.spec.ts` (new) | Playwright smoke test on a non-existent skill URL | AC-US1-05 e2e regression. |

### Data flow (unchanged)

```
GET /skills/<owner>/<repo>/<skill>
  └─ page.tsx
       ├─ getSkillByNameCached(decoded)
       │     ├─ hit  → render skill detail
       │     └─ null → fallback chain ↓
       ├─ getBlocklistEntryBySkillName(decoded)        ← FIX #1: return null on throw
       │     ├─ entry → render <BlockedSkillView>
       │     └─ null  → fallback continues ↓
       ├─ getRejectedSubmissionBySkillName(decoded)    ← FIX #2: return null on throw
       │     ├─ entry → render <RejectedSkillView>
       │     └─ null  → notFound()                     ← always reachable now
       └─ notFound()
```

### Code shape (target)

Both functions converge on this catch-block pattern (mirrors `getSkillByLegacySlug` at data.ts:250-256):

```ts
} catch (err) {
  if (typeof window === "undefined") {
    console.warn("[<fnName>] DB error:", err instanceof Error ? err.message : err);
  }
  return null;
}
```

Concretely:
- **`getBlocklistEntryBySkillName`** (data.ts:296-301): replace the trailing `throw err;` with `return null;` (the `console.warn` line is already in place).
- **`getRejectedSubmissionBySkillName`** (data.ts:352-357): same change.

That is the entire production code diff. ~4 lines net.

## Rationale

### Why fail-soft in the data layer (not a try/catch in the page)

1. **Convention consistency** — `getSkillByLegacySlug` already does exactly this. The two outliers are accidental, not principled.
2. **Single-call-site reasoning** — every consumer of `getBlocklistEntryBySkillName` / `getRejectedSubmissionBySkillName` lives in the page render path (`page.tsx`, `generateMetadata`). All call sites already handle a `null` return; none handles a thrown error meaningfully.
3. **Smaller diff, fewer reviewers** — page-level try/catch would add 8+ lines of nesting in a 530-line server component. Catch-block flip is 2 × 1-line changes.
4. **Belt-and-suspenders is unnecessary** — once the data layer fails soft, no caller can crash from a fallback DB error. Wrapping at the page level just adds noise.

### Why NOT also change `getSkillByName`

The primary lookup is semantically different. If the primary D1 query fails, the system genuinely doesn't know whether the skill exists — showing "could not be loaded / Retry" is the correct UX and the current `error.tsx` boundary handles it. Returning `null` from the primary would silently disguise outages as 404s, which is worse for incident response.

### Why a console.warn (not a structured logger)

Existing codebase pattern. `wrangler tail` already pretty-prints `console.warn` lines. Adding a structured logger here is YAGNI and out of scope for a 4-line bug fix.

### Risk assessment

- **Failure mode if fix is wrong**: real blocklisted skills temporarily miss their `<BlockedSkillView>` during a DB hiccup and show 404 instead. Acceptable: the skill is already excluded from the active Skill table, so it never renders as "safe." Operators see the warn line and investigate.
- **Failure mode if fix is right but DB is permanently down**: every skill page shows 404 (because `getSkillByName` itself throws → error boundary; same as today). No regression.
- **Test coverage**: Vitest unit tests cover all four success-and-failure permutations of the two functions; Playwright covers the negative-case page render contract.

### ADR

This fix is small enough that no ADR is warranted (ADR threshold per `.specweave/docs/internal/architecture/adr/` convention is "decision affects multiple modules or future direction"). The existing `getSkillByLegacySlug` precedent IS the convention. We are not making a new decision; we are fixing a deviation from it.

## Technology Stack

- **Language/Framework**: TypeScript / Next.js 15 / Cloudflare Workers (OpenNext) — unchanged.
- **Database**: Prisma against Cloudflare D1 — unchanged.
- **Test framework**: Vitest for unit, Playwright for e2e — already in repo.
- **No new dependencies**.

## Implementation Phases

### Phase 1: TDD red — failing tests
1. Add `src/lib/__tests__/data-failsoft.test.ts` with five Vitest cases:
   - `getBlocklistEntryBySkillName` returns `null` and warns when Prisma's `findFirst` rejects.
   - `getBlocklistEntryBySkillName` returns the existing entry shape unchanged when Prisma resolves with a row.
   - `getRejectedSubmissionBySkillName` returns `null` and warns when Prisma's `findFirst` rejects.
   - `getRejectedSubmissionBySkillName` returns the existing entry shape unchanged when Prisma resolves with a row.
   - Both warn lines start with `[<functionName>] DB error:`.
2. Run `npx vitest run src/lib/__tests__/data-failsoft.test.ts` → expect failures on the throw paths.

### Phase 2: TDD green — minimal fix
3. Edit `src/lib/data.ts:296-301` and `:352-357` to replace `throw err;` with `return null;`.
4. Re-run vitest → all five cases green.

### Phase 3: E2E regression
5. Add `tests/e2e/skill-not-found.spec.ts` (Playwright) hitting `/skills/no-such-publisher-9999/no-such-repo/no-such-skill?t={Date.now()}` and asserting HTTP 200 + `Skill Not Found` in body, NOT `digest:`, `could not be loaded`, `Application error`.
6. Run `npx playwright test tests/e2e/skill-not-found.spec.ts` against local dev server (or production if `BASE_URL` env set).

### Phase 4: Closure
7. Run full vitest suite for vskill-platform: `npx vitest run` — confirm no regressions.
8. Update `tasks.md` → all `[x]`, `spec.md` → all ACs `[x]`.
9. Commit + push, deploy via existing CI.

## Testing Strategy

- **Unit (Vitest)**: mock Prisma at the module level (`vi.mock('@/lib/db', ...)` — pattern already used in `data.test.ts` if it exists, else use `vi.spyOn` on `getDb()`). Stub `findFirst` to resolve OR reject. Spy on `console.warn`.
- **E2E (Playwright)**: real browser hit on a known-non-existent URL with cache-buster. Assert visible body text matches the soft-404 contract.
- **Coverage**: target 100% line coverage for the two modified catch blocks (trivial to hit both branches).

## Technical Challenges

### Challenge 1: Vitest mock for Prisma in vskill-platform
**Solution**: Use `vi.mock('@/lib/db', () => ({ getDb: vi.fn() }))` at the top of the test file, then per-case stub `getDb()` to return an object whose `blocklistEntry.findFirst` / `submission.findFirst` rejects with `new Error('simulated D1 failure')` (rejection case) or resolves with a fixture object (happy-path case).
**Risk**: existing `data.ts` tests may already mock differently — inspect first.
**Mitigation**: read any sibling test file in `src/lib/__tests__/` before writing the new one; copy the established mocking pattern.

### Challenge 2: Playwright e2e against production vs local
**Solution**: parametrise `BASE_URL` (default `http://localhost:3000`, override to `https://verified-skill.com` via env). Test hits a guaranteed-non-existent slug (`no-such-publisher-9999/no-such-repo/no-such-skill`) which neither environment will ever have.
**Risk**: local dev server may not be running during CI.
**Mitigation**: if e2e is intended to be CI-blocking, follow the existing playwright config — likely already targets a preview deploy. Inspect `playwright.config.ts` before assuming.
