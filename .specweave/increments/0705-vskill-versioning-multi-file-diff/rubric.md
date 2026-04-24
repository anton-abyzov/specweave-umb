---
increment: 0705-vskill-versioning-multi-file-diff
title: "Fix vskill versioning pipeline + GitHub-backed multi-file diff"
generated: "2026-04-24T18:45:00.000Z"
source: auto-generated
---

# Quality Contract

Per-increment quality bar for closure gates. All items below are required to pass before `sw:done` accepts this increment.

## Coverage

- Unit test coverage on modified files ≥ 90%.
- Integration test coverage on new code paths (upsertSubmission requeue branch, admin-rescan skip-on-unchanged branch, githubCompare, /versions/compare route, vskill diff command) ≥ 90%.
- E2E coverage: at least one E2E scenario (T-018 republish-smoke) passes in staging.

## Correctness Gates

- **No regressions** in existing submission flow: first-time publishes still create a SkillVersion with correct fields (existing tests continue to pass).
- **Republish**: resubmitting an identical skill (same `contentHash`) returns `{kind:"verified"}` without creating a duplicate row.
- **Republish with changes**: resubmitting with different `contentHash` creates a new SkillVersion row with all of (`content`, `contentHash`, `gitSha`, `manifest`, `treeHash`) populated.
- **Admin rescan**: no new SkillVersion row when content is unchanged; new row with ALL fields populated when content changes.
- **Compare endpoint**: returns `source:"github"` when both versions have valid gitSha on a GitHub repo; returns `source:"local-content"` otherwise; NEVER returns 5xx.
- **CLI diff**: returns exit 0 on success, 1 on API error; works in non-TTY (piped) without control sequences.

## Data Integrity

- Backfill script with `--dry-run` produces an actions log that is human-reviewable (one action per row).
- Backfill with `--apply` is idempotent: running it twice produces the same end state as running it once.
- After full rollout, `SELECT COUNT(*) FROM SkillVersion WHERE content='' AND gitSha!=''` = 0.
- After full rollout, `SELECT COUNT(*) FROM SkillVersion WHERE content='' AND contentHash=''` ≤ the pre-backfill count (no new ghosts created).

## Cross-Platform

- `vskill diff` runs successfully on `windows-latest` CI matrix, verified by T-016.
- No usage of `which`, `&&`, `~`, `2>/dev/null`, `lsof`, `chmod`, or symlinks in the new `diff` command.
- No OS-specific path separators hardcoded.

## Security

- `GITHUB_TOKEN` (when present) is never written to logs.
- `from`/`to` query params validated against `/^[0-9a-f]{7,40}$/` before forwarding to GitHub.
- `skillPath` used as a filter prefix rejects `..` segments and absolute paths.
- `/versions/compare` endpoint does not require auth (matches existing `/versions` surface) but CANNOT leak non-skillPath files from the parent repo (filter is applied server-side).

## Performance

- Compare endpoint p95 latency ≤ 1.5 seconds cold / ≤ 50ms cached (KV hit).
- Large patches (>1MB total) are truncated with a "View on GitHub" notice rather than blocking the page.
- Backfill script processes ≥ 50 rows/minute against a staging Neon instance.

## Failure Modes

- GitHub 429 → compare endpoint returns `source:"local-content"` with no error surfaced to user.
- GitHub 404 (repo/SHA gone) → compare endpoint returns `source:"local-content"`.
- KV unavailable → compare endpoint skips cache, still succeeds.
- SkillVersion row with null gitSha → compare endpoint uses LCS fallback.
- Queue send failure in upsertSubmission requeue branch → returns 5xx with a clean error (not a Prisma leak).

## Documentation

- READMEs for both vskill-platform and vskill CLI updated with:
  - `vskill diff` usage block (all flags, Windows compatibility note).
  - Compare endpoint shape + `source` semantics.
  - Link to the live scout golden test case (commit range + screenshot).

## Review Gates

- [!] `sw:code-reviewer` must pass with 0 critical/high/medium findings on modified files. — RECOVERY-2 2026-04-24: all 6 findings patched + regression tests added (F-CR-001 through F-CR-007, excl. F-CR-004 reclassified from flagged→clean). Re-review 2026-04-24 FAILED: 1 HIGH + 3 MEDIUM + 1 LOW remaining (F-CR-2A backfill treeHash algorithm divergence, F-CR-2B manifest size unit mismatch, F-CR-2C publishSkill empty-contentHash fallback, F-CR-2D compare KV cache schema validation, F-CR-2E asymmetric baseSha/headSha sourcing). See reports/code-review-report.json. RECOVERY-3 2026-04-24: F-CR-2A/B/C/D fixed with TDD regression tests (commits 2ef19ec, 533abce, efedad5, b59d27d). F-CR-2E accepted as known debt — see Known Debt section below.
- `sw:grill` report must have zero blocking issues.
- `sw:judge-llm` WAIVED only if consent denied (per workflow default).
- User manually verifies (manual gate): (a) compare page for `anton-abyzov/vskill/scout` shows 4 files after a seeded republish, (b) `vskill diff` prints expected output on a Mac terminal.

## Known Debt

- **F-CR-2E — asymmetric baseSha/headSha sourcing** (LOW, cosmetic). In `src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/compare/route.ts:193-200`, `baseSha` is read from GitHub's compare echo (`compare.base_commit?.sha ?? fromRow.gitSha`) while `headSha` is read from our own DB row (`toRow.gitSha`). The two sources can be equal in the happy path but would diverge in edge cases (force-push, detached SHA). No functional impact on dedup/diff logic — both values still feed into the response as display fields only, and downstream consumers (UI, `vskill diff`) treat them as opaque identifiers. Tracked for a future polish pass; recovery-3 accepted as debt rather than expand scope.
