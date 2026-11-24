# Verify — 0881-portable-project-hub

PASS · 2026-09-22T05:43:22.997Z · commands from explicit

## Commands

### `node /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0881-portable-project-hub/reports/verify-stable-install.mjs` → exit 0 (1s)

```
PASS: registry latest and installed CLI 2.3.0; 12 native Codex skills; existing config, instructions and project hub preserved; bundled font licenses present
```

### `cd /tmp/specweave-0881-root && node scripts/e2e/project-hub-e2e.mjs --browser && node scripts/e2e/brand-parity.mjs` → exit 0 (8s)

```
PASS: real CLI init, preservation, stale writes, work lifecycle, artifact/routine library and three harness briefs
[LogParser] logDir=/Users/antonabyzov/.claude/projects/-var-folders-js-x0hbrvjj2rl7hsgjy5955_r40000gn-T-sw-project-e2e-Z3O939 files=0
PASS: headless desktop/tablet/mobile, profile/work/artifact/routine flows, brief, download, persistence and zero runtime errors
[LogParser] logDir=/Users/antonabyzov/.claude/projects/-var-folders-js-x0hbrvjj2rl7hsgjy5955_r40000gn-T-sw-brand-project-lbaRFX files=0
PASS: live website/dashboard colors, type, buttons and panels match; fonts load locally; desktop/tablet/mobile and eight adjacent routes pass with selected-control and primary-action assertions
```

### `node /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0881-portable-project-hub/reports/native-install-smoke.mjs && node /tmp/specweave-0881-root/scripts/e2e/bounded-scans.mjs` → exit 0 (3s)

```
Previous native skill preserved: /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sw-native-package-6wOcNu/.specweave/state/skill-backups/074e8a69-7371-43da-b68b-31a854ee4c66/sw-project
PASS: installed CLI init + refresh installs all 12 native Codex skills, preserves custom project skill and refreshes idempotently
PASS living-docs: exit 1, 86 ms
PASS gc: exit 1, 45 ms
PASS dashboard --no-browser: exit 1, 47 ms
PASS lsp setup --dry-run: exit 1, 71 ms
PASS lsp search foo: exit 1, 72 ms
PASS lsp refs missing.ts foo: exit 1, 70 ms
PASS lsp def missing.ts foo: exit 1, 68 ms
PASS lsp hover missing.ts foo: exit 1, 63 ms
PASS lsp symbols missing.ts: exit 1, 64 ms
PASS lsp warmup: exit 1, 64 ms
PASS lsp status: exit 1, 63 ms
PASS lsp warmup --quiet: exit 1, 62 ms
PASS gc --json: exit 1, 44 ms
PASS save --dry-run --no-push: exit 1, 60 ms
PASS symlink escape and discovery depth: counted = scanned = 16
PASS lsp setup --dry-run --min-files 1: exit 0, 61 ms
PASS gc --json: exit 0, 42 ms
PASS save --dry-run --no-push: exit 0, 129 ms
PASS save --dry-run --no-push: exit 0, 300 ms
BLACKBOX: PASS
```

### `cd /tmp/specweave-0881-root && npm run validate:versions && npm run lint:skills && npm run lint:docs-refs` → exit 0 (0s)

```

> specweave@2.3.0 validate:versions
> node scripts/validation/validate-versions.cjs

🔍 Validating version alignment across plugin manifests...

  ✅ package.json                                  2.3.0
  ✅ marketplace.json (root)                       2.3.0
  ✅ marketplace.json (plugins[0])                 2.3.0
  ✅ plugins/specweave/.claude-plugin/plugin.json  2.3.0

✅ All four version locations aligned at 2.3.0

> specweave@2.3.0 lint:skills
> node scripts/lint-skills.mjs

lint-skills: 46 files clean

> specweave@2.3.0 lint:docs-refs
> node scripts/lint-docs-refs.mjs

docs-refs: OK — 155 pages, 12 skills, 82 CLI commands.
```

## Acceptance criteria

9/9 checked

| AC | Done | Text |
|---|---|---|
| AC-01 | x | A non-Git folder and an existing umbrella can hold editable project name, goal and shared context without replacing existing config or instructions. |
| AC-02 | x | Worker briefs combine current shared context, an existing intent and linked artifact references; remain usable by Codex, Claude Code and generic tools; never claim a native task was launched. |
| AC-03 | x | Artifacts are associated with intent IDs; local references stay inside the project and HTTPS references are safe; reusable routines produce explicit worker briefs and accurately state scheduling status. |
| AC-04 | x | Concurrent/stale updates cannot silently overwrite project data; invalid/corrupt data fails visibly; portable output is bounded and secret-scrubbed. |
| AC-05 | x | Dashboard provides usable brief editing, work links, artifact/routine creation and copyable worker briefs on desktop/tablet/mobile with headless evidence. |
| AC-06 | x | Codex adapter installs skills in .agents/skills, preserves existing user data and documents native skills and explicit CLI fallback; new project skill is portable. |
| AC-07 | x | Regression tests, build, skill/docs lint, targeted coverage and packaged-install smoke pass; release classification and actual installed version are recorded. |
| AC-08 | x | Dashboard and website consume shared brand tokens; paper, ink, accent, surfaces, type and controls match the current public website with responsive headless comparison evidence. |
| AC-09 | x | Stable npm version is published from pushed source, installed from the registry on this machine, and passes full source and installed-package checks; implementation and umbrella evidence are pushed. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | codex-0881 | cd /tmp/specweave-0881-root && npx vitest run tests/unit/pr… |  |
| T-02 | done | codex-0881 | cd /tmp/specweave-0881-root && npx vitest run tests/unit/ad… |  |
| T-03 | done | codex-0881 | cd /tmp/specweave-0881-root && PATH=/Users/antonabyzov/.nvm… |  |
| T-04 | done | codex-0881 | cd /tmp/specweave-0881-root && PATH=/Users/antonabyzov/.nvm… |  |
| T-05 | done | codex-0881 | cd /tmp/specweave-0881-root && PATH=/Users/antonabyzov/.nvm… |  |
| T-06 | done | codex-0881 | cd /tmp/specweave-0881-root && export PATH=/Users/antonabyz… |  |
| T-07 | done | codex-0881 | cd /tmp/specweave-0881-root && export PATH=/Users/antonabyz… |  |

7/7 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
