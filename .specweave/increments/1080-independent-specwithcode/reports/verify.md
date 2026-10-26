# Verify — 1080-independent-specwithcode

PASS · 2026-10-26T09:49:04.178Z · commands from explicit

## Commands

### `node .specweave/increments/1080-independent-specwithcode/reports/verify-final-main.mjs && node .specweave/increments/1080-independent-specwithcode/reports/verify-publication.mjs && node .specweave/increments/1080-independent-specwithcode/reports/verify-template-package.mjs` → exit 0 (4s)

```
{"head":"952b28e51d8bda25b3e7d79cade3a78a25775770","releaseAncestor":"8200bcd798e2ebe1a961a4d0eedec5e03fd560a0","productAncestor":"76bfbac921491b8dfd0f47a7cbd4b8c52c757e7b","canonicalFixtureMerge":"1fa61350a68e680e48b292f0f2913801a9caebe0","canonicalFixtureExact":true,"version":"1.0.90","allVersionFieldsAligned":true,"serverLicense":"UNLICENSED","rootLicenseAbsent":true,"identityInstructionsPreserved":true,"inheritedNoticeExact":true}
{
  "repository": "anton-abyzov/specwithcode",
  "repositoryId": 1414999661,
  "head": "dcac53c09a08364699b9f5072282b425acafffc7",
  "version": "1.0.90",
  "fork": false,
  "detectedProjectLicense": null,
  "baselineHead": "39b0a05fdf625fd06cef5c2fbe30de87ed3da96f",
  "historyStatus": "ahead",
  "initialStars": 2,
  "stars": 2,
  "contributors": [
    "anton-abyzov"
  ],
  "independentReadme": true,
  "blanketLicenseRemoved": true,
  "inheritedNoticeExact": true
}
{"package":"specweave","version":"3.1.11","integrity":"sha512-fPvc2rrMlwKY1htRnVziB/hmp3xtnf199L/xlb4GlwCR3y64AmIbyplGCtG8PqbDYxRvwfyZ58ml7AXNLVrn6w==","agentsIdentityGuidance":true,"claudeNoticeGuidance":true,"cliExistingLicensePreserved":true}
```

### `node repositories/anton-abyzov/specweave-studio/scripts/studio-brand-audit.mjs --source-terms-only && node --test repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/runtime-package.test.mjs repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/npm-package.test.mjs && cd repositories/anton-abyzov/specweave-studio && node_modules/.bin/vp test run scripts/lib/third-party-licenses.test.ts` → exit 0 (1s)

```
  duration_ms: 49.435875
  type: 'test'
  ...
# Subtest: the npm range matches the server package's own engines
ok 4 - the npm range matches the server package's own engines
  ---
  duration_ms: 0.199792
  type: 'test'
  ...
# Subtest: runtime bundle package registers both command names on the one entry
ok 5 - runtime bundle package registers both command names on the one entry
  ---
  duration_ms: 0.75
  type: 'test'
  ...
# Subtest: runtime and desktop package the complete executable managed helper graph
ok 6 - runtime and desktop package the complete executable managed helper graph
  ---
  duration_ms: 197.036875
  type: 'test'
  ...
# Subtest: bundle verification rejects a runtime package without the specwithcode bin
ok 7 - bundle verification rejects a runtime package without the specwithcode bin
  ---
  duration_ms: 0.825833
  type: 'test'
  ...
# Subtest: bundle.mjs writes the shared runtime package and verify-bundle checks its bins
ok 8 - bundle.mjs writes the shared runtime package and verify-bundle checks its bins
  ---
  duration_ms: 0.582417
  type: 'test'
  ...
1..8
# tests 8
# suites 0
# pass 8
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 229.927708

 RUN  v5.0.1 /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-1080/repositories/anton-abyzov/specweave-studio


 Test Files  1 passed (1)
      Tests  22 passed (22)
   Start at  05:49:03
   Duration  216ms (tests 72%, transform 21%, import 3%, setup 3%, worker 1%)
```

### `git diff --check` → exit 0 (0s)

```
(no output)
```

## Acceptance criteria

3/3 met

| AC | Met | Text |
|---|---|---|
| AC-01 | x (tasks) | Product docs present SpecWithCode independently; no blanket project MIT grant remains; exact inherited notice survives source and packaging. |
| AC-02 | x (tasks) | AGENTS and CLAUDE guidance preserves independent positioning and required third-party notices; generic templates preserve the owning project's identity and licensing decisions. |
| AC-03 | x (tasks) | Changes are reviewed and merged; public snapshot retains current releases, history, stars, and only actual snapshot authors; no force-push. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | codex@antons-macbook-m4max | node repositories/anton-abyzov/specweave-studio/scripts/stu… |  |
| T-02 | done | codex@antons-macbook-m4max | cd repositories/anton-abyzov/specweave && node node_modules… |  |
| T-03 | done | codex@antons-macbook-m4max | PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PA… |  |
| T-04 | done | codex@antons-macbook-m4max | python3 -B repositories/anton-abyzov/specweave-studio/scrip… |  |
| T-05 | done | codex@antons-macbook-m4max | npm --prefix repositories/anton-abyzov/specweave/docs-site … |  |
| T-06 | done | codex@antons-macbook-m4max | node repositories/anton-abyzov/specweave-studio/scripts/stu… |  |
| T-07 | done | codex@antons-macbook-m4max | node repositories/anton-abyzov/specweave-studio/scripts/stu… |  |
| T-08 | done | codex@antons-macbook-m4max | git -C repositories/anton-abyzov/specweave-studio diff --ch… |  |
| T-09 | done | codex@antons-macbook-m4max | cd repositories/anton-abyzov/specweave-studio && PATH=/User… |  |
| T-10 | done | codex@antons-macbook-m4max | cd repositories/anton-abyzov/specweave-studio && PATH=/User… |  |
| T-11 | done | codex@antons-macbook-m4max | node .specweave/increments/1080-independent-specwithcode/re… |  |
| T-12 | done | codex@antons-macbook-m4max | PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PA… |  |

12/12 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
