# Independent SpecWithCode positioning and license scope

## Problem
The public product is already a standalone GitHub repository with only Anton as contributor, but README claims a blanket MIT license and UPSTREAM calls it an MIT fork. Anton requests independent positioning, no new project-wide license grant, durable instructions and matching SpecWeave templates, while preserving concurrent work and legal notices.

## Scope
In: product documentation, license metadata and packaging notices, generic template guidance, public source snapshot. Out: runtime behavior, provider identities, private history rewrites, release tags, existing stars and other owners' changes.

## Acceptance Criteria
- [ ] AC-01: Product docs present SpecWithCode independently; no blanket project MIT grant remains; exact inherited notice survives source and packaging.
- [ ] AC-02: AGENTS and CLAUDE guidance preserves independent positioning and required third-party notices; generic templates preserve the owning project's identity and licensing decisions.
- [ ] AC-03: Changes are reviewed and merged; public snapshot retains current releases, history, stars, and only actual snapshot authors; no force-push.

## Approach
Use isolated umbrella and nested worktrees based on current remote main/develop. Preserve native sessions, existing PRs and claims. GitHub readback on 2026-10-26: fork=false, parent=null, 2 stars, contributor anton-abyzov only. No reset is needed. Move the exact inherited MIT text into THIRD_PARTY_NOTICES.md; source supplies no new project-wide license. Preserve prior grants and third-party terms. Keep bundle LICENSE output for compatibility and copy the notice there. Verify and close 1080.

## Decisions
### Asked
- Anton: independent product positioning; no project-wide license; record in agent instructions and templates; coordinate concurrent work and preserve compliance.
### Defaulted (change any before sw-do)
- Preserve source and public snapshot history: resetting is unnecessary and risks concurrent work; no GitHub fork relationship or imported contributor list exists.
- Retain required third-party notices and earlier license grants; do not assert ownership of upstream work.
### Open
- none

## Tasks

### T-01 Product identity and license boundaries
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specweave-studio/README.md, repositories/anton-abyzov/specweave-studio/AGENTS.md, repositories/anton-abyzov/specweave-studio/CLAUDE.md, repositories/anton-abyzov/specweave-studio/UPSTREAM.md, repositories/anton-abyzov/specweave-studio/LICENSE, repositories/anton-abyzov/specweave-studio/THIRD_PARTY_NOTICES.md, repositories/anton-abyzov/specweave-studio/apps/server/package.json, repositories/anton-abyzov/specweave-studio/third-party-licenses.config.json, repositories/anton-abyzov/specweave-studio/scripts/studio-brand-audit.mjs, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/bundle.mjs, repositories/anton-abyzov/specweave-studio/scripts/build-desktop-artifact.ts, repositories/anton-abyzov/specweave-studio/docs/studio/naming.md, repositories/anton-abyzov/specweave-studio/docs/studio/fleet.md, repositories/anton-abyzov/specweave-studio/docs/studio/getting-started.md, repositories/anton-abyzov/specweave-studio/CHANGELOG.md, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/make_helpers.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/npm-package.mjs, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/runtime-package.mjs, repositories/anton-abyzov/specweave-studio/apps/desktop/resources/linux/com.specweave.studio.metainfo.xml, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/runtime-package.test.mjs, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/npm-package.test.mjs, repositories/anton-abyzov/specweave-studio/scripts/public-mirror/publish.mjs | Test: node repositories/anton-abyzov/specweave-studio/scripts/studio-brand-audit.mjs --source-terms-only

### T-02 Durable generic identity guidance
- AC: AC-02 | Files: AGENTS.md, CLAUDE.md, repositories/anton-abyzov/specweave/src/templates/AGENTS.md.template, repositories/anton-abyzov/specweave/src/templates/CLAUDE.md.template, repositories/anton-abyzov/specweave/docs-site/src/pages/code.tsx, repositories/anton-abyzov/specweave/docs-site/src/pages/code/download.tsx, repositories/anton-abyzov/specweave/docs-site/src/components/ecosystem/StudioSections.tsx, repositories/anton-abyzov/specweave/docs-site/static/llms.txt | Test: cd repositories/anton-abyzov/specweave && node node_modules/vitest/vitest.mjs run tests/unit/cli/helpers/init/instruction-templates.test.ts tests/unit/cli/helpers/init/instruction-file-writer.test.ts

### T-03 Review and publish source docs
- AC: AC-03 | Files: .specweave/increments/1080-independent-specwithcode/reports/ | Test: node .specweave/increments/1080-independent-specwithcode/reports/verify-publication.mjs && PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never node .specweave/increments/1080-independent-specwithcode/reports/verify-live-site.mjs --guides && git diff --check

### T-04 Preserve agent-record assertions across formatting
- AC: AC-01 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-update-agent-refresh.py | Test: python3 -B repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-update-agent-refresh.py

### T-05 Remove remaining guide-wide license claims
- AC: AC-02 | Files: repositories/anton-abyzov/specweave/docs-site/docs/guides/claude-code-vs-codex.md, repositories/anton-abyzov/specweave/docs-site/docs/guides/claude-code-usage-limit.md, repositories/anton-abyzov/specweave/docs-site/docs/guides/switch-claude-code-to-codex.md, repositories/anton-abyzov/specweave/docs-site/docs/guides/specwithcode-vs-opencode-t3-code.md | Test: npm --prefix repositories/anton-abyzov/specweave/docs-site run build

### T-06 Integrate the released version without reverting source terms
- AC: AC-01, AC-03 | Files: repositories/anton-abyzov/specweave-studio/apps/server/package.json | Test: node repositories/anton-abyzov/specweave-studio/scripts/studio-brand-audit.mjs --source-terms-only

### T-07 Integrate concurrent release notes without losing identity changes
- AC: AC-01, AC-03 | Files: repositories/anton-abyzov/specweave-studio/CHANGELOG.md | Test: node repositories/anton-abyzov/specweave-studio/scripts/studio-brand-audit.mjs --source-terms-only

### T-08 Avoid repeated shared changelog insertion conflicts
- AC: AC-03 | Files: repositories/anton-abyzov/specweave-studio/CHANGELOG.md | Test: git -C repositories/anton-abyzov/specweave-studio diff --check

### T-09 Stabilize fan-out fixture gate ownership without weakening checks
- AC: AC-03 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/mcp/OrchestratorMcpToolkit.integration.test.ts | Test: cd repositories/anton-abyzov/specweave-studio && node_modules/.bin/vp test run apps/server/src/mcp/OrchestratorMcpToolkit.integration.test.ts
