# Verify — 0847-skill-install-publish-scale

PASS · 2026-10-09T12:11:20.482Z · commands from explicit

## Commands

### `python3 /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0847-skill-install-publish-scale/reports/studio-release-20261009/desktop-release/verify-delivery.py` → exit 0 (0s)

```
{
  "verifiedAt": "2026-10-09T12:11:20.473216+00:00",
  "source": "c39c49d82ae620dc98a822adc778d1a58f1c989e",
  "desktopVersion": "1.0.64",
  "cliVersion": "1.2.2",
  "installedMacCodesignAndHashes": "pass",
  "recordedPlatformHashAndSignatureProofs": [
    "darwin-aarch64",
    "linux-x86_64",
    "windows-x86_64"
  ],
  "installedRuntimeAndHeadlessUiReceipts": "pass",
  "fullPackageTests": "6330 passed, 2 skipped; retained receipt",
  "report": "/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0847-skill-install-publish-scale/reports/studio-release-20261009/desktop-release/release-verification.md"
}
```

## Acceptance criteria

42/42 met

| AC | Met | Text |
|---|---|---|
| AC-US1-01 | x | Public GitHub repositories are discovered through root `SKILL.md`, `skills/<name>/SKILL.md`, and `plugins/<plugin>/skills/<name>/SKILL.md` paths. |
| AC-US1-02 | x | Private GitHub repositories are discovered with an authenticated token path and do not fall back to unauthenticated raw URLs when a token is available. |
| AC-US1-03 | x | Private repository failures distinguish `401/403 unauthorized`, `404 missing`, rate limit, and transient network errors in CLI and desktop UI. |
| AC-US1-04 | x | `vskill install <github-ref>` and the desktop install modal produce equivalent installed files for the same skill and agent target. |
| AC-US1-05 | x | Lockfile/source metadata records enough provenance to check updates later: normalized repo URL, branch, commit SHA, skill path, and plugin name when applicable. |
| AC-US1-06 | x | Path traversal and unsafe ref strings are rejected before any filesystem write. |
| AC-US2-01 | x | Claude plugin cache discovery handles installed, enabled, disabled, user-scope, and project-scope plugins without requiring the removed `claude plugin list` command. |
| AC-US2-02 | x | Bare plugin names resolve to `name@marketplace` where required for enable, disable, uninstall, and install commands. |
| AC-US2-03 | x | Plugin-backed skills dedupe against direct GitHub and marketplace copies using stable source identity, not only display name. |
| AC-US2-04 | x | Re-running the same plugin install is idempotent: no duplicate files, duplicate lockfile entries, duplicate update subscriptions, or duplicated sidebar rows. |
| AC-US2-05 | x | Plugin install errors stream through the desktop SSE UI with actionable status and do not leave jobs stuck. |
| AC-US2-06 | x | Plugin install/uninstall tests cover at least 50 fixture skills and mixed scope installs. |
| AC-US3-01 | x | A local authored skill can be test-installed, pushed to GitHub, submitted, scanned, approved, published, and reinstalled from the registry in an automated sandbox. |
| AC-US3-02 | x | Republish detects changed SKILL.md content by canonical content hash and creates exactly one new `SkillVersion` row per new commit. |
| AC-US3-03 | x | Publishing rejects non-monotonic versions, missing versions when required, malformed semver, and changed post-scan content with clear states. |
| AC-US3-04 | x | Publishing a skill with multiple files records a stable manifest and diff summary; rerunning publish on the same commit is idempotent. |
| AC-US3-05 | x | Platform search, skill detail, versions, diff, update check, and install tracking endpoints all surface the newly published version. |
| AC-US3-06 | x (tasks) | Public and private publish sandboxes both pass, with private access using scoped GitHub credentials only. |
| AC-US4-01 | x | `SKILL.md` validation enforces required frontmatter (`name`, `description`) and preserves optional fields (`version`, `author`, `metadata`, `agents/openai.yaml`) without data loss. |
| AC-US4-02 | x | Claude/Anthropic-compatible filesystem installs preserve full `SKILL.md` content and bundled resources. |
| AC-US4-03 | x | ChatGPT/OpenAI Tier 3 export emits a complete paste-ready blob and, when `agents/openai.yaml` exists, preserves the OpenAI-facing metadata in the export path. |
| AC-US4-04 | x | Per-agent transformers for Cursor, Copilot, Aider, Windsurf, Continue, and related targets are idempotent and path-safe. |
| AC-US4-05 | x | Large skills with `scripts/`, `references/`, `assets/`, nested agent metadata, and multi-file resources install without truncation. |
| AC-US4-06 | x | Generated fixtures include a universal skill and a provider-specific skill, and both pass scanner, install, export, and update tests. |
| AC-US5-01 | x | Desktop install modal covers direct GitHub, plugin, local authored, marketplace, and clipboard-export targets. |
| AC-US5-02 | x | Desktop progress streams are replayable and finish with a truthful success/error summary. |
| AC-US5-03 | x | Desktop cannot expose GitHub, NPM, Cloudflare, database, or platform tokens to the WebView or logs. |
| AC-US5-04 | x | Desktop E2E runs on macOS using the sidecar/server path that users actually ship. |
| AC-US5-05 | x | CLI and desktop parity tests compare file outputs, lockfile metadata, source identity, and version displayed in the sidebar/detail panel. |
| AC-US5-06 | x | Missing secrets cause clear test skips, not false failures. |
| AC-US5-07 | x | Skill Studio desktop app updates surface as a clear notification in the main UI, and the Install flow downloads, installs, and offers a real restart action. |
| AC-US5-08 | x | Desktop GitHub OAuth uses the registered GitHub callback URL, bounces desktop state back to localhost, and shows a clickable/copyable authorization fallback before browser-open settles. |
| AC-US6-01 | x | Full validation runs `npm run build`, `npx vitest run`, `npx playwright test`, desktop sidecar/build checks, platform build/tests, and targeted private/public sandbox suites. |
| AC-US6-02 | x (tasks) | The release script bumps versions only after tests pass and updates package metadata consistently. |
| AC-US6-03 | x | The newly built `vskill` package is installed on the local machine and smoke-tested with public GitHub, private GitHub, plugin, and ChatGPT/OpenAI export flows. |
| AC-US6-04 | x | Any failed release candidate is followed by a fix and a new version candidate rather than reusing the same broken version. |
| AC-US6-05 | x | Reports are written only under `.specweave/increments/0847-skill-install-publish-scale/reports/` and contain no secret values. |
| AC-US6-06 | x | Desktop update notification and install/restart behavior are covered by focused automated tests before the next release. |
| AC-AUDIT-01 | x (tasks) | Verified current model IDs are selectable with provider-compatible requests and testcase round-trips preserve headings/newlines. |
| AC-AUDIT-02 | x (tasks) | Sign-out clears both platform and GitHub credentials including legacy fallbacks; fallback key files are owner-only. Optional usage telemetry requires consent and excludes search text. Tenant publication preserves authentication, owner/admin authorization and private-submission boundaries. |
| AC-AUDIT-03 | x (tasks) | Three useful authored example skills have reproducible tests, public source receipts and truthful registry queue/publication status. |
| AC-AUDIT-04 | x (tasks) | Enterprise, production queue/crawler, actual adoption and Studio integration conclusions cite fresh evidence and distinguish unsupported claims. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-001 | done | tasks.md | checkbox in tasks.md |  |
| T-002 | done | tasks.md | checkbox in tasks.md |  |
| T-003 | done | tasks.md | checkbox in tasks.md |  |
| T-004 | done | tasks.md | checkbox in tasks.md |  |
| T-005 | done | tasks.md | checkbox in tasks.md |  |
| T-006 | done | tasks.md | checkbox in tasks.md |  |
| T-007 | done | tasks.md | checkbox in tasks.md |  |
| T-008 | done | tasks.md | checkbox in tasks.md |  |
| T-009 | done | tasks.md | checkbox in tasks.md |  |
| T-010 | done | tasks.md | checkbox in tasks.md |  |
| T-011 | done | tasks.md | checkbox in tasks.md |  |
| T-012 | done | tasks.md | checkbox in tasks.md |  |
| T-013 | done | tasks.md | checkbox in tasks.md |  |
| T-014 | done | tasks.md | checkbox in tasks.md |  |
| T-015 | done | tasks.md | checkbox in tasks.md |  |
| T-016 | blocked | vskill-audit-root |  | Release blocker from May is resolved by published CLI 1.2.2… |
| T-017 | done | tasks.md | checkbox in tasks.md |  |
| T-018 | done | tasks.md | checkbox in tasks.md |  |
| T-019 | done | tasks.md | checkbox in tasks.md |  |
| T-020 | done | tasks.md | checkbox in tasks.md |  |
| T-021 | done | tasks.md | checkbox in tasks.md |  |
| T-022 | done | tasks.md | checkbox in tasks.md |  |
| T-023 | done | tasks.md | checkbox in tasks.md |  |
| T-024 | done | vskill-audit-models | cd /Users/antonabyzov/Projects/github/vskill-models-audit-2… |  |
| T-025 | done | vskill-audit-enterprise | cd /Users/antonabyzov/Projects/github/vskill-enterprise-sec… |  |
| T-026 | done | vskill-audit-root | node .specweave/increments/0847-skill-install-publish-scale… |  |
| T-027 | done | vskill-audit-root | test -s .specweave/increments/0847-skill-install-publish-sc… |  |
| T-028 | done | vskill-audit-enterprise | cd /Users/antonabyzov/Projects/github/vskill-enterprise-sec… |  |
| T-029 | done | vskill-audit-models | cd /Users/antonabyzov/Projects/github/vskill-models-audit-2… |  |
| T-030 | done | vskill-audit-models | cd /Users/antonabyzov/Projects/github/vskill-models-audit-2… |  |
| T-031 | done | vskill-audit-root | cd /Users/antonabyzov/Projects/github/vskill-studio-audit-2… |  |
| T-032 | done | vskill-audit-enterprise | cd /Users/antonabyzov/Projects/github/vskill-platform-enter… |  |
| T-033 | done | vskill-audit-enterprise | cd /Users/antonabyzov/Projects/github/vskill-platform-enter… |  |
| T-034 | done | vskill-audit-models | cd /Users/antonabyzov/Projects/github/vskill-models-audit-2… |  |
| T-035 | done | vskill-audit-enterprise | python3 /tmp/vskill-queue-health-release-verify-20261009.py… |  |
| T-036 | done | vskill-audit-models | python3 .specweave/increments/0847-skill-install-publish-sc… |  |
| T-037 | done | vskill-audit-root | cd /Users/antonabyzov/Projects/github/vskill-scanner-health… |  |
| T-038 | done | vskill-audit-root | cd /Users/antonabyzov/Projects/github/vskill-scanner-health… |  |
| T-039 | done | vskill-audit-enterprise | cd /Users/antonabyzov/Projects/github/vskill-platform-enter… |  |
| T-040 | done | vskill-audit-root | cd /Users/antonabyzov/Projects/github/vskill-scanner-health… |  |
| T-041 | done | vskill-audit-enterprise | cd /Users/antonabyzov/Projects/github/vskill-platform-enter… |  |
| T-042 | done | vskill-audit-root | cd /Users/antonabyzov/Projects/github/vskill-scanner-health… |  |
| T-043 | done | vskill-audit-root | cd /Users/antonabyzov/Projects/github/vskill-scanner-health… |  |
| T-044 | done | vskill-audit-root | cd /Users/antonabyzov/Projects/github/vskill-scanner-health… |  |
| T-045 | done | vskill-audit-enterprise | cd /Users/antonabyzov/Projects/github/vskill-platform-enter… |  |
| T-046 | done | vskill-audit-enterprise | cd /Users/antonabyzov/Projects/github/vskill-platform-enter… |  |
| T-047 | done | vskill-audit-enterprise | cd /Users/antonabyzov/Projects/github/vskill-platform-enter… |  |

46/47 done · 0 skipped · 0 claimed · 1 blocked · 0 stale · 0 open
