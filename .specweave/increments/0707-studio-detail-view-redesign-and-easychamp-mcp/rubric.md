---
increment: 0707-studio-detail-view-redesign-and-easychamp-mcp
title: "Skill Studio detail view redesign + MCP showcase + EasyChamp MCP server"
generated: "2026-04-24"
source: main-agent
version: "1.0"
status: active
---

# Quality Contract — 0707

## Coverage Gates
| Layer | Threshold | Tool |
|-------|-----------|------|
| Unit | ≥ 90% statements | Vitest |
| Integration | ≥ 85% statements | Vitest |
| E2E | 100% of user-stories covered by at least one test | Playwright |

## Functional Gates (blocking closure)

- **G-F1**: All 9 tabs (Overview..Versions) visible in one flat tab bar on 1440×900 viewport without horizontal or vertical scroll (Playwright assertion).
- **G-F2**: `/versions`, `/benchmark/latest`, `/evals`, `/activation-history` all return 200 with the documented envelope for a fixture skill NOT inside a git repo — verified via integration test.
- **G-F3**: `google-workspace/gws` dash-slug case passes for all four endpoints (integration test).
- **G-F4**: Benchmark card opens an ℹ popover with the exact methodology sentence and inline Tests/Run navigation links (component test).
- **G-F5**: `easychamp/tournament-manager` fixture renders EasyChamp under MCP Servers in Deps tab; Copy-config button emits valid JSON matching the spec shape (E2E test).
- **G-F6**: `easychamp-mcp` built binary exchanges `ListTools` + `CallTool(generate_league)` successfully in demo mode (integration test with child process).
- **G-F7**: `EASYCHAMP_API_KEY` never appears in any log output, tool response, committed file, or README example — verified by grep sweep on test output + `git log -p` for the new repo.

## Performance Gates
- **G-P1**: Overview tab initial render ≤ 100ms on a 50-skill fixtures workspace (Playwright `performance.now()` assertion).
- **G-P2**: Each of the 4 endpoints P95 latency ≤ 50ms on an empty-envelope response (Vitest timing assertion over 100 runs).
- **G-P3**: EasyChamp MCP demo-mode tool call ≤ 200ms (Vitest timing assertion).

## Responsive Gates
- **G-R1**: Playwright viewport-resize test visits 480, 768, 1024, 1440; asserts no metric card has `scrollWidth > clientWidth`; asserts tab bar fits at ≥ 1024 without horizontal scroll.

## Security Gates
- **G-S1**: No API key string appears anywhere in the repo, tool output, or logs (automated grep check).
- **G-S2**: All external anchor tags include `rel="noopener noreferrer"` (lint rule + component test).
- **G-S3**: Copy-config JSON uses `${EASYCHAMP_API_KEY}` placeholder, never a real value (E2E assertion on clipboard content).

## Accessibility Gates
- **G-A1**: All new interactive elements (tabs, cards, popovers, links) are keyboard navigable and expose `role` + `aria-label` where appropriate (axe-core scan via Playwright).
- **G-A2**: Benchmark popover dismisses with Escape and focus returns to the trigger (component test).

## Code-Review Gates (runs via sw:code-reviewer)
- [x] **G-C1**: Zero critical/high findings before closure. _Evaluator: sw:code-reviewer — PASS (2026-04-24): 0 critical, 0 high, 0 medium, 5 low, 1 info — see reports/code-review-report.json_
- **G-C2**: `/simplify` report surfaces zero duplication/inefficiency findings.
- [x] **G-C3**: `sw:grill` report generated and passes. _Evaluator: sw:grill — PASS with NEEDS REVIEW (2026-04-24): 0 critical, 2 high (git-init gap on demo repo, spec/impl shape nuance), 0 medium — all 31 ACs pass; see reports/grill-report.json_
- [x] **G-C4**: `sw:judge-llm` approved. _Evaluator: sw:judge-llm — APPROVED (2026-04-24): in-session ultrathink (no ANTHROPIC_API_KEY → fallback per skill spec), score 91, 0 critical, 1 high (doc-wording reconciliation), 4 low — see reports/judge-llm-report.json_

## Documentation Gates
- **G-D1**: EasyChamp MCP README covers install, env, and per-tool example calls.
- **G-D2**: `specweave sync-living-docs 0707` runs without errors.

## Out of Scope (documented — do NOT cause gate failure)
- npm publish of `easychamp-mcp`.
- OAuth device-code flow (scaffolded but disabled in v0.1.0).
- Real EasyChamp backend API implementation.
- Migration of legacy consumers of `MetadataTab.tsx` (none expected).
