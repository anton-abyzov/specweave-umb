# Combined 2.3.0 candidate

Commit 193f9f6c317ee959626b86a66291a4701daa4277 merged exact fe9db936d ancestry into the portable project release. `git merge-base --is-ancestor` passed for both original fix heads cb42dab31 and 26da1f117. Package version is 2.3.0.

Independent Node 22.20.0 run against its rebuilt dist: complete bounded-scans regression harness passed. `refresh-plugins` from a temporary bare .specweave directory returned exit 1 in 62 ms; --quiet returned exit 1 with no output in 59 ms.

```text
PASS living-docs: exit 1, 67 ms
PASS gc: exit 1, 46 ms
PASS dashboard --no-browser: exit 1, 47 ms
PASS lsp setup --dry-run: exit 1, 62 ms
PASS lsp search foo: exit 1, 62 ms
PASS lsp refs missing.ts foo: exit 1, 61 ms
PASS lsp def missing.ts foo: exit 1, 62 ms
PASS lsp hover missing.ts foo: exit 1, 62 ms
PASS lsp symbols missing.ts: exit 1, 64 ms
PASS lsp warmup: exit 1, 63 ms
PASS lsp status: exit 1, 63 ms
PASS lsp warmup --quiet: exit 1, 61 ms
PASS gc --json: exit 1, 46 ms
PASS save --dry-run --no-push: exit 1, 58 ms
PASS symlink escape and discovery depth: counted = scanned = 16
PASS lsp setup --dry-run --min-files 1: exit 0, 61 ms
PASS gc --json: exit 0, 43 ms
PASS save --dry-run --no-push: exit 0, 114 ms
PASS save --dry-run --no-push: exit 0, 244 ms
BLACKBOX: PASS
```

This is source-candidate verification. Registry download and clean installation remain pending.

The release task reported 16,856 combined unit tests passed (159 existing skips), headless UI verification, independent review, and clean package preflight. Documentation CI found a generated overview link error; cec237cb8 corrects the README guide URL and documentation workflow triggers without runtime changes. Awaiting final CI and public package.

Final candidate c8fbd8c16 adds the update dry-run fix. Independent bounded-scans harness passed again against rebuilt dist. Release task supplied the final CI coverage receipt: 751 files and 16,858 tests passed, 159 existing skips; lines 69.52%, branches 61.96%, functions 71.41%, statements 68.94%, exceeding the 60% target. Documentation and 685 links passed. Source log: /tmp/specweave-0881-ci-unit.log.
