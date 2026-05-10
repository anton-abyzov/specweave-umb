# Tasks: vskill — Private-repo Install Support

Implementation order. Single-domain (vskill repo) — single-agent execution.
TDD enforcement: each task lists its **Test Plan** before it can be marked `[x]`.

## T-001: Add `fetchRepoMeta(owner, repo)` to `src/lib/github-fetch.ts`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04 | **Status**: [ ] pending

Implement helper that calls `GET https://api.github.com/repos/{owner}/{repo}`
and returns `{ private: boolean, defaultBranch: string, fullName: string }`.
Use existing `githubFetch` so the SSRF guard + retries + auth header are
inherited. On 404 throw a `RepoNotFoundError`; on 403 throw a
`RepoAccessDeniedError`; surface `X-Github-Sso` header value when present.

**Test Plan**:
- Given a public repo (mocked 200 with `private: false`)
  When `fetchRepoMeta("owner", "public-repo")` is called
  Then it returns `{ private: false, defaultBranch: "main", fullName: "owner/public-repo" }`
- Given a 404 response, Then it throws `RepoNotFoundError`
- Given a 403 with `X-Github-Sso` header, Then it throws `RepoAccessDeniedError` carrying the SSO URL

## T-002: Add `fetchRepoContent(owner, repo, path, branch?)` to `src/lib/github-fetch.ts`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-04 | **Status**: [ ] pending

Implement the centerpiece helper. Uses
`GET /repos/{o}/{r}/contents/{path}?ref={branch}` with `Accept: application/vnd.github.raw`.
Returns `{ content, sha, size }`. Falls back to `git/blobs/{sha}` when the
`contents/` endpoint returns 403 with `errors[0].code === "too_large"`. Branch
defaults to the result of `fetchRepoMeta`.

**Test Plan**:
- Given a small public file mock (200, body = "hello"), Then returns `{ content: "hello", sha: "...", size: 5 }`
- Given a 404 response, Then throws `FileNotFoundError`
- Given a 403 + too-large mock, Then falls back to git/blobs and returns the body
- Given malformed UTF-8, Then throws `EncodingError` (rare, but we shouldn't silently double-decode)

## T-003: Replace `raw.githubusercontent.com` URLs in `src/commands/add.ts` (line 1631 + 1708)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [ ] pending

Both `installAllRepoPlugins` and `installRepoPlugin` build manifest URLs from
`raw.githubusercontent.com`. Refactor to call `fetchRepoMeta` once, then
`fetchRepoContent(owner, repo, ".claude-plugin/marketplace.json", branch)`.
Search downstream for any other `raw.githubusercontent.com` occurrences in the
install pipeline and migrate those too (per-file fetches inside
`fetchPluginContents` if applicable).

**Test Plan**:
- Given the new code path, When the install runs against a mocked private repo,
  Then no fetch hits `raw.githubusercontent.com`
- Given a public-repo mock, Then the install still completes successfully
- Given a private-repo mock with valid token, Then `marketplace.json` is fetched and parsed

## T-004: Add `src/lib/auth-resolver.ts` with token precedence
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [ ] pending

Module exports `resolveToken(): { token: string|null, source: "env-app"|"env-pat"|"keychain"|"none" }`.
Precedence: `VSKILL_GITHUB_APP_TOKEN` > `VSKILL_GITHUB_TOKEN` > keychain.
`createGitHubFetch` is updated to use this resolver instead of going directly
to the keychain.

**Test Plan**:
- Given `VSKILL_GITHUB_APP_TOKEN=app_xxx`, Then `resolveToken()` returns `{ token: "app_xxx", source: "env-app" }`
- Given only `VSKILL_GITHUB_TOKEN=pat_yyy`, Then returns `{ source: "env-pat" }`
- Given only keychain has a token, Then returns `{ source: "keychain" }`
- Given nothing, Then returns `{ token: null, source: "none" }`

## T-005: Add `src/lib/install-audit.ts` with `recordInstall()` + lockfile
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-04 | **Status**: [ ] pending

Module appends `AuditEntry` to `~/.vskill/installed-skills.json` under a
`proper-lockfile` lock. Computes `tokenFingerprintHash = sha256(token).slice(0, 12)`.
If the file doesn't exist, creates it with mode `0600`. If the JSON is
malformed, refuses to overwrite — logs a warning and exits the audit step
without aborting the install.

**Test Plan**:
- Given a fresh home, When `recordInstall(entry)` runs, Then the file is created with mode 0600 and contains a single-element array
- Given an existing file with one entry, Then the new entry is appended
- Given a token, Then `entry.token_fingerprint_hash` is exactly the first 12 hex chars of `sha256(token)`
- Given concurrent calls, Then the lockfile serializes them and no entry is lost

## T-006: Add `classifyFetchError()` and wire exit codes 2/3/4/5 in `add.ts`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [ ] pending

Single helper that takes the error from `fetchRepoMeta` / `fetchRepoContent`
plus the resolver result and returns `{ exitCode, message }`. Wire in the
existing `process.exit()` call sites to use it. Match the exact strings in
`spec.md` AC-US2-01..04.

**Test Plan**:
- Given `RepoNotFoundError` + no token, Then exit code 2 with the auth-required message
- Given `RepoAccessDeniedError` + token, Then exit code 3 + SSO URL when X-Github-Sso present
- Given `FileNotFoundError` (manifest only), Then exit code 4 + "found: <ls>" message
- Given a 5xx after retries, Then exit code 5

## T-007: Hook audit recording into the install pipeline
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [ ] pending

After each successful plugin install in `installRepoPlugin`, call
`recordInstall({...})` with the captured fields. The `commit_sha` comes from
the `sha` field returned by `fetchRepoContent`; `marketplace_hash =
sha256(manifestContent)`; `actor = (await fetchUser()).login || "cli"`.

**Test Plan**:
- Given a successful install, Then `~/.vskill/installed-skills.json` gains one entry with all 7 fields populated
- Given the GET /user call fails, Then `actor === "cli"` (no install abort)
- Given audit module write fails, Then a warning is logged but the install does not abort

## T-008: Write `docs/private-repos.md`
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [ ] pending

Worked example doc using `anton-abyzov/anton-personal-skills` as the canary.
Six sections matching the spec ACs: create-private, marketplace.json schema,
plugin.json optional, vskill auth login, install --repo, sharing.
Two appendices: GitHub Enterprise Server (`GITHUB_API_URL`), CI/Actions
(GitHub App OIDC pattern, no PATs).

**Test Plan**:
- Given the doc exists, Then `markdownlint docs/private-repos.md` passes (links resolve, no broken anchors)
- Given a fresh user follows the doc copy-paste, Then `vskill install` succeeds against the canary

## T-009: Unit test `tests/unit/private-repo-install.test.ts`
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [ ] pending

Mock `globalThis.fetch` and assert:
- The install path issues `GET https://api.github.com/repos/...` calls.
- It does NOT issue any `raw.githubusercontent.com` calls during install.
- Token precedence in `auth-resolver.ts` is honored (parameterized table test).

**Test Plan**:
- Given each error scenario from T-006, Then the unit test exercises it and asserts the exit code
- Given the install happy-path mock, Then `recordInstall` is called once with the expected entry shape

## T-010: Integration test `tests/integration/private-repo-install.test.ts`
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02 | **Status**: [ ] pending

Live test gated by `VSKILL_E2E=1` and `VSKILL_GITHUB_TOKEN`. Spawns the CLI
against the real `anton-abyzov/anton-personal-skills` repo with `--dry-run`
and asserts the `resume-tuner` plugin appears in stdout.

**Test Plan**:
- Given `VSKILL_E2E=1` + valid token, Then test runs and passes
- Given `VSKILL_E2E` unset, Then test is skipped (no live network)
- Given a token without access, Then test asserts exit code 3 with the SSO message (sad-path coverage)

## T-011: Verify no public-repo regressions
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [ ] pending

Run the full existing test suite (`npm test`) and a manual canary install
against a known-public skills repo. Ensure no behavioral change for the
public flow.

**Test Plan**:
- Given the existing test suite, Then `npm test` is green with no new failures
- Given a public-canary install (`vskill install --repo OWNER/PUBLIC --all`), Then it completes identically to today's behavior

## T-012: Add ADR `architecture/adr/ADR-vskill-private-repo-fetch-strategy.md`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] pending

Record the "use api.github.com/contents not raw.githubusercontent.com"
decision in the umbrella ADR directory, citing the GitHub-raw-host
authentication limitation as the forcing function.

**Test Plan**:
- Given the ADR exists, Then it is linked from `plan.md` and discoverable via `specweave docs adr list`

---

## Dependency Order

```
T-001 ──┐
T-002 ──┼─► T-003 ──┐
T-004 ──┘           │
                    ├─► T-006 ──► T-009
T-005 ──────────────┤             ▲
                    └─► T-007 ────┘
                        │
                        ▼
                    T-010, T-011 (validation)
                        │
                        ▼
                    T-008, T-012 (docs)
```

Total: 12 tasks. Estimated effort: 6-9 hours of focused work for an
experienced TS dev familiar with the vskill codebase.
