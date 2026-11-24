# Documentation test baseline audit

**12 of the release-head 15 failures reproduce on published v2.0.3. Exactly 3 are new navigation/footer contract mismatches.** This is a baseline comparison, not a green test result.

| Snapshot | Passed | Failed | Skipped | Files passed / failed |
|---|---:|---:|---:|---:|
| v2.0.3 (`bb154f48964ad80150d09330af1cb05a7b59c220`) | 188 | 12 | 0 | 32 / 7 |
| Release head (`59fd2c4d5`) | 185 | 15 | 0 | 30 / 9 |

Both snapshots contain 200 tests in 39 files. The isolated baseline worktree is `/tmp/specweave-0877-docs-baseline`. It uses exactly the same root and docs-site dependency directories as the release worktree: Node 22.20.0, Vitest 4.0.18, jsdom 28.1.0, React 19.2.0. No source files, test assertions, skips, or thresholds were edited. No browser was launched. The baseline checkout is clean; only ignored dependency symlinks were added.

Replay from its `docs-site` directory:

```sh
PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never npm test -- --reporter=default --reporter=json --outputFile.json=<reports>/docs-v2.0.3-baseline-tests.json
```

## Confirmed pre-existing failures

| Test file | Failures | Observed cause |
|---|---:|---|
| `src/__tests__/docusaurus-config.test.ts` | 2 | Tests require `onBrokenLinks: 'throw'`; baseline already sets `'warn'`. The redesign did not introduce this configuration. |
| `src/__tests__/remotion-theme.test.ts` | 1 | Expected individual `// --sw-*` token comments are absent. Numeric/color-value tests pass. |
| `src/components/sections/__tests__/HeroSection.test.tsx` | 2 | Tests expect “Ship Features” and “Claude Code Native”; the baseline component has different headline/badges. |
| `src/components/sections/__tests__/HowItWorksSection.test.tsx` | 2 | Tests expect an earlier section title and step copy. |
| `src/components/sections/__tests__/IntegrationsSection.test.tsx` | 2 | SVG imports are URL/data strings in Vitest but component code treats them as React components; rendering throws `InvalidCharacterError`. |
| `src/components/sections/__tests__/TrustedBySection.test.tsx` | 2 | Same SVG import/render mismatch prevents rendering. |
| `src/components/ui/Icon/__tests__/Icon.test.tsx` | 1 | Test expects an image with alt text; implementation uses an imported SVG component and the test mock supplies a tag string. |

All seven failing test files are byte-identical between baseline and release head. Their section/Icon/Remotion implementations and the docs package manifest, lockfile, Vitest config, and test setup are also unchanged. Docusaurus configuration changed elsewhere, but its `onBrokenLinks: 'warn'` and `onBrokenMarkdownLinks: 'warn'` lines are unchanged. Restoring a strict broken-link build gate is separate follow-up work, not a baseline regression.

## New failures requiring current contracts

- `sidebars.test.ts`: “includes Docs and Learn nav items” and “includes Enterprise and Blog nav items”. Product/Integrations/Docs/Verified Skills replaced the prior primary navigation. Verify the intended current destinations and labels when updating the contract.
- `Footer.test.tsx`: “renders social icon links”. The current accessible social link is GitHub Issues rather than Discussions. Preserve assertions for a real accessible support link and its intended destination.

The 12 baseline failures are a subset of the 15 release-head failures, with no other differences. This audit does not repair or dismiss baseline failures; it identifies their provenance. It compares the specified release head before any subsequent strict-link or navigation test fixes.

Evidence: `docs-v2.0.3-baseline-tests.log`, `docs-v2.0.3-baseline-tests.json`, `docs-release-head-tests.log`; exact test-name mapping and dependency paths: `docs-baseline-audit.json`.
