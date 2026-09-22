# SpecWeave 2.3.0 stable delivery

Published and installed from npm on 2026-09-22. Release: https://github.com/anton-abyzov/specweave/releases/tag/v2.3.0. Source PR #1953 merged as 8be01b24e23f18c1a87036e7f6e8ab0d4c98cce3; the npm gitHead matches this exact commit. The merged tree matches the independently reviewed and tested candidate. Umbrella evidence: https://github.com/anton-abyzov/specweave-umb/pull/93.

## Delivered
Portable projects now work for software, research, content and operations, including folders without Git. Goals, context, work assignments, artifact references and routine definitions produce fresh briefs for Codex, Claude Code and generic tools. Existing intent/ledger evidence remains authoritative. Hosts own actual agent execution, connector permissions and schedules; stored routines are not active schedules. This additive minor release requires no breaking data migration.

Dashboard and website consume the same brand tokens. Local fonts use the exact IBM Plex Sans and Newsreader 450 faces, with bundled licenses. Responsive controls, populated chart totals, helper text, panels and primary actions were verified against the live website. The public guide is live: https://spec-weave.com/docs/guides/portable-projects.

Also includes the sibling bounded-filesystem fixes from PR #1950/#1951/#1954 and a reproduced fix preventing update --check from installing plugins.

## Installation
The normal shell resolves SpecWeave at /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/specweave; --version returns 2.3.0. npm installed the public registry artifact. All 12 native Codex skills match the installed package, the Claude core plugin is refreshed to 2.3.0, and existing AGENTS.md, CLAUDE.md, project config and hub hashes remain unchanged. See stable-install-receipt.json, stable-native-refresh.json and stable-plugin-refresh.log.

## Validation
- Local and CI standard unit suites: 16,858 passed, 159 existing skips, 751 passing files.
- Full local coverage: 69.57% lines, 61.96% branches, 71.47% functions, 68.99% statements; all exceed the 60% unit gate. New feature coverage: 95.61% lines, 86.44% branches.
- Source build, dashboard TypeScript, skills/docs lint, 17 smoke checks, ledger lifecycle and clean package installation passed.
- Documentation build with the actual CI README import and all 685 candidate links passed; production deployment and guide readback passed.
- Installed-package CLI and headless browser project workflows, native skill installation/preservation, desktop/tablet/mobile and eight adjacent dashboard routes passed. Independent global no-project/symlink/no-write checks passed.
- Independent code and visual reviews have no remaining findings.

## Recorded limitations
The existing nonblocking LSP-versus-grep timing assertion failed in CI, including a retry (49.36 ms versus 45.81 ms threshold); 88 other E2E tests passed. The test and CI policy were not weakened. The optional Claude review runner also failed at startup; independent reviews passed. Two local fast-profile attempts hit the existing 5-second Git-fixture limits; the unchanged standard release suite passed with its existing 10-second profile. Raw receipts retain these failures alongside the passing release checks.
