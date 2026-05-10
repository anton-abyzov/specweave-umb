# Implementation Plan: vskill — Private-repo Install Support

## Design

### One-line summary

Replace every `https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}`
fetch in the install pipeline with a single `fetchRepoContent(owner, repo,
path, branch)` helper that uses
`GET https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}`
with `Accept: application/vnd.github.raw`. Layer enterprise-grade auth, error
differentiation, and audit/provenance fields on top.

### Component map

```
src/lib/github-fetch.ts
├── createGitHubFetch(opts)                  (existing, unchanged)
├── githubFetch(url, init)                   (existing, unchanged)
├── ALLOWED_HOSTS                            (existing, unchanged — already permits api.github.com)
├── fetchRepoContent(owner, repo, path,      (NEW — the centerpiece)
│     branch?, opts?) -> Promise<{
│       content: string, sha: string,
│       size: number, encoding: "utf8"
│     }>
├── fetchRepoMeta(owner, repo)               (NEW — visibility + default_branch)
│     -> Promise<{ private: boolean,
│                  defaultBranch: string,
│                  fullName: string }>
└── tokenFingerprint(token)                  (NEW — sha256(token).slice(0,12))

src/lib/auth-resolver.ts                     (NEW — small, ~60 lines)
└── resolveToken(): { token: string|null,
                      source: "env-app"|"env-pat"|"keychain"|"none" }
                                              precedence: env-app > env-pat > keychain

src/lib/install-audit.ts                     (NEW — ~80 lines)
├── recordInstall(entry: AuditEntry)         appends to ~/.vskill/installed-skills.json
├── interface AuditEntry { repo, branch,
│     commit_sha, marketplace_hash,
│     token_fingerprint_hash, installed_at,
│     actor }
└── (uses proper-lockfile already in deps)

src/commands/add.ts
├── installAllRepoPlugins()                  (CHANGE — use fetchRepoContent + fetchRepoMeta + audit)
├── installRepoPlugin()                      (CHANGE — same)
└── classifyFetchError()                     (NEW — maps API responses to exit codes 2/3/4/5)

docs/private-repos.md                        (NEW — worked example doc)

tests/unit/private-repo-install.test.ts      (NEW — mocked-fetch unit tests)
tests/integration/private-repo-install.test.ts (NEW — gated by VSKILL_E2E=1)
```

### Data flow (after fix)

```
vskill install --repo OWNER/REPO --all
        │
        ▼
[resolveToken]  env VSKILL_GITHUB_APP_TOKEN > env VSKILL_GITHUB_TOKEN > keychain
        │
        ▼
[fetchRepoMeta]  GET /repos/OWNER/REPO  →  { private, defaultBranch }
        │
   private && no token? ───► exit 2 (auth-required, US-AC2-01)
        │
        ▼
[fetchRepoContent]  GET /repos/OWNER/REPO/contents/.claude-plugin/marketplace.json
        │
   404 + private + token? ───► exit 3 (auth-insufficient, US-AC2-02)
   404 + path-missing?    ───► list .claude-plugin/, exit 4 (US-AC2-03)
        │
        ▼
[parse manifest, install plugins]  (existing logic unchanged)
        │
        ▼
[recordInstall]  append AuditEntry to ~/.vskill/installed-skills.json
```

### Auth precedence (US-003)

1. `process.env.VSKILL_GITHUB_APP_TOKEN` — used as-is, treated as installation token.
2. `process.env.VSKILL_GITHUB_TOKEN` — used as-is, treated as user PAT/OAuth.
3. Keychain (`getDefaultKeychain().getGitHubToken()`) — existing path.
4. None — install proceeds only if `fetchRepoMeta` returns `private: false`.

`tokenFingerprint(token) = sha256(token).slice(0, 12)`. Stored in audit log; never the raw token.

### Error matrix (US-002)

| HTTP | repo private | token? | Exit | Message |
|------|-------------|--------|------|---------|
| 404 on `/repos/{o}/{r}` | unknown | none | 2 | "Repository not found or private. Run `vskill auth login`." |
| 404 on `/repos/{o}/{r}` | unknown | yes | 3 | "Token cannot read OWNER/REPO. SSO? Re-auth?" |
| 200 on `/repos/{o}/{r}`, 404 on contents | yes | none | 2 | "Private — login first" |
| 200 on `/repos/{o}/{r}`, 404 on contents | yes/no | yes | 4 | "Manifest missing. Found: <ls .claude-plugin/>" |
| 403 on contents | yes | yes | 3 | "Token lacks Contents: Read scope. SSO header: …" |
| 5xx | * | * | 5 | "GitHub API unhealthy. Retry later." (after existing retry exhausted) |

### Why `Accept: application/vnd.github.raw` (not the JSON contents response)

- One round-trip instead of fetch-JSON-then-base64-decode.
- Identical behavior to today's raw-host fetch (UTF-8 string body).
- Falls back to JSON form (`Accept: application/vnd.github.object` returns base64-encoded `content` field) for files >1 MB; `vnd.github.raw` returns 403 in that case with `errors[0].code === "too_large"` and we route to `git/blobs/{sha}` with `vnd.github.raw`.
- 1 MB ceiling applies to `contents/` only — `git/blobs/` has a 100 MB ceiling, more than enough for any plausible skill artifact.

### Backward compatibility

- ALLOWED_HOSTS keeps `raw.githubusercontent.com` so existing public-only call sites (if any) continue to work.
- `installSkillsFromGithub` (URL-based install path, e.g. `vskill install https://github.com/.../skill.md`) is **out of scope** for this increment — that already works for public skills and a follow-up increment can migrate it.
- The visibility check (`fetchRepoMeta`) is a single extra API call but **replaces** the existing `getDefaultBranch` call (which also hit `/repos/{o}/{r}`), so net new = 0 calls.

## Rationale

### Why not just append `?token=` to the raw URL?

- `raw.githubusercontent.com` only accepts the **temporary** asset-upload token (issued by `Get release asset` API). PATs and OAuth tokens are not valid there. Documented at https://docs.github.com/en/rest/repos/contents#about-the-rest-api-for-repository-contents.
- Even if it worked, putting tokens in URLs leaks them into proxy logs and shell history — a security regression.

### Why not `git clone --depth 1`?

- Adds `git` as a hard runtime dep (already a soft dep but install-time fragile on Windows / corporate proxies).
- ~10× slower for a single 4 KB manifest fetch.
- Doesn't compose with our existing per-file fetch pattern.

### Why a new `auth-resolver.ts` module?

- Token precedence (App > PAT > keychain) is going to grow (Codespaces secrets, GitHub Actions OIDC, etc.). Co-locating the rules in one tested module beats sprinkling `process.env.X || keychain()` calls.
- Easy to mock in unit tests.

### Why audit fields in `installed-skills.json`?

- SOC2 CC7.2 (system monitoring) and ISO-27001 A.12.4 (logging) want install-time provenance.
- Existing file already lists installed skills — we're extending its schema, not adding a new artifact.
- `marketplace_hash` lets a security team detect post-install drift (skill author force-pushes a malicious update to `main` after the install).
- `token_fingerprint_hash` lets the team correlate "who installed what" without storing the token.

### Why expose `VSKILL_GITHUB_APP_TOKEN` separately from `VSKILL_GITHUB_TOKEN`?

- GitHub App installation tokens are short-lived (1 h max) and scoped to specific repos — substantially safer for CI than long-lived PATs.
- The Authorization header format is identical (`Bearer <token>`), so the implementation cost is zero — but exposing two env vars makes the intent explicit and lets us tag the audit-log `actor` field as `github-app` instead of the bot user's login.

### Why bypass strict interview?

- The PM dimension (user stories, ACs) and the architect dimension (component map, error matrix, security threat model) are both grounded in a live repro from the active session and a direct reading of `src/commands/add.ts` and `src/lib/github-fetch.ts`. All six interview categories are covered in the bypass `interview-0844-*.json` state file.

## ADRs touched

- `architecture/adr/` — propose new ADR `ADR-vskill-private-repo-fetch-strategy.md` with the
  decision summary above. Created during implementation by `sw:tdd-green` task T-008.

## Out-of-scope follow-ups (NOT in this increment)

- Migrate `vskill install <github-url>` (single-skill URL form) to api.github.com.
- GitHub Enterprise Server `GITHUB_API_URL` env-var support.
- Codespaces / GitHub Actions OIDC integration (no static token at all).
- A `vskill audit` subcommand to render `installed-skills.json` as a human-readable table.
