# Verify — 0883-deploy-bounded-cli-scan-fixes

PASS · 2026-09-22T05:37:30.519Z · commands from explicit

## Commands

### `cd /tmp/specweave-0881-root && npm run lint:skills && npm run lint:docs-refs && node scripts/e2e/bounded-scans.mjs` → exit 0 (3s)

```

> specweave@2.3.0 lint:skills
> node scripts/lint-skills.mjs

lint-skills: 46 files clean

> specweave@2.3.0 lint:docs-refs
> node scripts/lint-docs-refs.mjs

docs-refs: OK — 155 pages, 12 skills, 82 CLI commands.
PASS living-docs: exit 1, 68 ms
PASS gc: exit 1, 46 ms
PASS dashboard --no-browser: exit 1, 45 ms
PASS lsp setup --dry-run: exit 1, 62 ms
PASS lsp search foo: exit 1, 62 ms
PASS lsp refs missing.ts foo: exit 1, 65 ms
PASS lsp def missing.ts foo: exit 1, 62 ms
PASS lsp hover missing.ts foo: exit 1, 61 ms
PASS lsp symbols missing.ts: exit 1, 62 ms
PASS lsp warmup: exit 1, 62 ms
PASS lsp status: exit 1, 60 ms
PASS lsp warmup --quiet: exit 1, 58 ms
PASS gc --json: exit 1, 44 ms
PASS save --dry-run --no-push: exit 1, 58 ms
PASS symlink escape and discovery depth: counted = scanned = 16
PASS lsp setup --dry-run --min-files 1: exit 0, 56 ms
PASS gc --json: exit 0, 42 ms
PASS save --dry-run --no-push: exit 0, 121 ms
PASS save --dry-run --no-push: exit 0, 235 ms
BLACKBOX: PASS
```

## Acceptance criteria

4/4 checked

| AC | Done | Text |
|---|---|---|
| AC-01 | x | Both fix PRs merged with exact-head protection; respect branch policy and the authorized release process. |
| AC-02 | x | Version 2.2.4 contains stable 2.2.3 and both fix branches; combined build, unit tests, lint, and packaged CLI regressions pass. |
| AC-03 | x | npm latest and GitHub release resolve to coordinated stable 2.3.0; downloaded registry artifact passes bounded-scan and refresh-plugins regressions. |
| AC-04 | x | Source and scoped evidence pushed; merge SHAs, publication receipts, and remaining external check status recorded. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | codex@antons-macbook-m4max | cd repositories/anton-abyzov/0883-release && npm run build … |  |
| T-02 | done | codex@antons-macbook-m4max | node .specweave/increments/0883-deploy-bounded-cli-scan-fix… |  |

2/2 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
