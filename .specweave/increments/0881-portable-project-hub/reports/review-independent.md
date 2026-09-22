# Independent review — 0881 Portable project hub

Verdict: ship from code-review perspective — no remaining confirmed findings (0 critical, 0 high). Five reproduced findings were fixed and independently rechecked.
Reviewer context: independent subagent. Scope: diff against origin/develop, untracked dashboard UI/routes/tests, and follow-up native installer fixes. Reviewer did not edit application source.

## Resolved findings

| Severity | Location | Original failure | Independent fix verification |
|---|---|---|---|
| High | `src/cli/commands/project.ts:28` | Initialization followed a sw-project directory symlink or dangling AGENTS.md symlink and created files outside the chosen project. | Both original Node22 reproductions now reject before project or outside files are written. New regressions and existing store/CLI/routes tests pass. |
| Medium | `src/dashboard/client/src/pages/ProjectHubPage.tsx:88` | Refresh displayed the new revision but an open draft continued to send the old revision and repeatedly failed HTTP409. | Chromium headless: explicit rebase retained the draft, submitted revision2, returned HTTP200 and persisted revision3. Delayed project-list loading also exposes no editable form before project resolution. |
| High | `src/adapters/codex/adapter.ts:136` | Redirecting refresh to shared native skills silently replaced preexisting user skills without backup. | Native skills now use namespaced directories; an unnamespaced custom skill remains unchanged, and conflicting sw-project content is recoverable byte-for-byte from a backup. |
| Medium | `src/utils/plugin-copier.ts:934` | Global source hash caused native-path migration or installation in another project to report success while target skills remained absent. | An actual legacy copy seeded the global receipt; native installation then succeeded in two project roots. Unchanged native repetition skips based on actual files. |
| Medium | `src/utils/native-skill-installer.ts:66` | Executable companion scripts were written as0644 and failed direct execution with EACCES. | Source0755 installs0755; direct execution prints PASS. Permission-only drift is detected, backed up and repaired. |

## Verification

- Node22.20.0: store, CLI and project-hub route suites — 3 files, 46 tests passed.
- Node22.20.0 final native installer, Codex adapter and refresh adapter suites — 3 files, 18 tests passed.
- Independent real-filesystem migration, collision-preservation and executable companion checks ran against current source through Vite SSR. User home was not mutated.
- Browser receipts used Chromium with `headless: true`, `PWDEBUG=0`, `PLAYWRIGHT_HTML_OPEN=never`.
- Earlier package dry run included every checked new CLI, runtime, route, skill and dashboard entrypoint. That run preceded the final native helper changes and release-candidate bump.

## Remaining verification boundaries

Full build, responsive E2E, final packaged installation and release-version proof are owned by the parent task. The final helper was independently tested from source; package build/install remains a separate gate. UI manual acceptance remains required before increment closure under umbrella AGENTS.md. This review is not a claim that those release gates have completed.
