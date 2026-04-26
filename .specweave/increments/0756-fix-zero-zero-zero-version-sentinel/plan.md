# Plan — 0756

## Approach

The cleanest, lowest-risk fix is to teach `resolveSkillVersion`'s `pick()` filter to reject `"0.0.0"` as a sentinel placeholder. `0.0.0` is technically valid SemVer but in this codebase it's only ever produced by the studio's own placeholder for `/check-updates` — no real skill is ever published at `0.0.0`. Treating it as "absent" lets the priority chain fall through to `pluginVersion` or the `"1.0.0"` default.

A second small fix updates `StudioContext.tsx:405`'s remaining hardcoded `"0.0.0"` fallback to `"1.0.0"` for consistency.

## Files

- `src/eval-ui/src/version-resolver.ts` — `pick()` rejects `"0.0.0"`.
- `src/eval-ui/src/version-resolver.test.ts` — add coverage for `"0.0.0"` sentinel handling.
- `src/eval-ui/src/StudioContext.tsx:405` — fallback `"0.0.0"` → `"1.0.0"`.

## Verification

1. **Unit**: `npx vitest run src/eval-ui/src/version-resolver.test.ts` (RED then GREEN).
2. **Smoke**: build vskill, launch `vskill studio`, navigate to the codex plugin section, capture screenshot. None of the 3 codex skills shows `v0.0.0`.
3. **DB**: re-run `scripts/check-zero-versions.ts` — counts remain 0.

## Risk

- A skill that legitimately publishes `0.0.0` (e.g. an alpha) would now display the fallback instead of the real version. Mitigation: the contract has always defaulted new skills to `1.0.0` (incr 0728); no published skill in the DB is at `0.0.0`. If one ever appears it would be a sentinel/test row.
