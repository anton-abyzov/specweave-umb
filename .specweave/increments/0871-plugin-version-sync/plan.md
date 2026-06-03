# Plan: 0871 Plugin version sync

## Fix
1. **New** `scripts/build/stamp-plugin-version.cjs` — lift the exact `node -e` targets from
   `bump-version.sh` (plugin.json.version, marketplace.json.version, marketplace.json.plugins[0].version),
   read `package.json.version`, write each if different, idempotent, log changes. CLI-runnable.
2. **package.json**:
   - `"stamp:plugin-version": "node scripts/build/stamp-plugin-version.cjs"`
   - `"validate:versions": "node scripts/validation/validate-versions.cjs"`
   - `build`: append `&& npm run stamp:plugin-version` (stamps source before pack on every publish).
   - `prepublishOnly`: `"npm run rebuild && npm run validate:versions"` (rebuild stamps, validate hard-gates).
   - `version`: `"node scripts/build/auto-changelog.js && npm run stamp:plugin-version && git add CHANGELOG.md plugins/specweave/.claude-plugin/plugin.json .claude-plugin/marketplace.json"`.
3. **bump-version.sh**: replace the inline `node -e` block with `node scripts/build/stamp-plugin-version.cjs` (DRY).
4. **Guard test** `tests/unit/build/version-alignment.test.ts` — asserts package.json == marketplace.json(root+plugins[0]) == plugin.json. RED now (1.0.586 vs 1.0.589).
5. **Fix current drift**: run the stamp → 1.0.589 across plugin.json + marketplace.json.

## TDD
- RED: write the guard test → fails (plugin.json 1.0.586 ≠ package 1.0.589).
- GREEN: add stamp script, run it (→1.0.589), wire package.json + bump-version.sh.
- VERIFY: `npm run build` (stamps + builds clean), `node scripts/validation/validate-versions.cjs` exit 0, guard test green.

## Why this covers every path
`npm publish` always runs `prepublishOnly` → `rebuild` → `build` (now stamps) → `validate:versions`
(now gates). CI `release.yml` and manual both call `npm publish`, so both are covered even though
they bump via `npm version`. `version` lifecycle covers local bumps; bump-version.sh covers the
scripted release. Defense in depth.

## E2E (deferred, OTP-gated)
A republish (1.0.590) is needed to prove `refresh-plugins` produces a fresh cache with current
content — ask Anton (the build will stamp plugin.json→1.0.590 automatically).

## Files
- new `scripts/build/stamp-plugin-version.cjs`
- `package.json`, `scripts/build/bump-version.sh`
- new `tests/unit/build/version-alignment.test.ts`
- stamped: `plugins/specweave/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`
