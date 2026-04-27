---
increment: 0795-studio-plugin-list-cli-removed
total_tasks: 5
completed_tasks: 5
---

# Tasks: Studio /api/plugins 500

All paths relative to `repositories/anton-abyzov/vskill/`.

## T-001: New `src/eval-server/plugin-discovery.ts`
**Status**: [x] completed · **Refs**: AC-US1-01..06, AC-US3-01, AC-US3-02

**Description**: Pure function `discoverInstalledPlugins({ cacheRoot, projectDir? })`. Walks `<cacheRoot>/<marketplace>/<plugin>/<version>/.claude-plugin/plugin.json`, reads `enabledPlugins` from user + project settings via existing `listEnabledPlugins()`, joins. Returns `InstalledPlugin[]`.

**Test Plan**: `src/eval-server/__tests__/plugin-discovery.test.ts` (new)
- **TC-001** Empty cache: Given `cacheRoot` does not exist → Then returns `[]`.
- **TC-002** Happy path enabled-user: Given a plugin at `<cache>/mp/myplug/1.0.0/.claude-plugin/plugin.json` and `~/.claude/settings.json` `enabledPlugins["myplug@mp"]: true` → Then returns one row `{ name: "myplug", marketplace: "mp", version: "1.0.0", scope: "user", enabled: true }`.
- **TC-003** Project scope: enabled only in project settings → row has `scope: "project", enabled: true`.
- **TC-004** Installed but disabled: present on disk but absent from any `enabledPlugins` → row has `enabled: false, scope: "user"`.
- **TC-005** Missing plugin.json: cache dir exists but no `.claude-plugin/plugin.json` → skip silently (no throw).
- **TC-006** Path-traversal rejection: marketplace name `..` (synthesized via direct dirent forgery in test) → rejected by `isInside` check.
- **TC-007** Multiple versions: two version dirs `1.0.0` and `1.0.1` → emit one row using the latest (highest mtime).

## T-002: Replace GET /api/plugins handler
**Status**: [x] completed · **Refs**: AC-US1-01, AC-US1-05, AC-US1-07

**Description**: Edit `src/eval-server/plugin-cli-routes.ts:81-92`. Replace `runClaudePlugin(["list"], …)` + `parseInstalledPlugins` with a single call to `discoverInstalledPlugins({ cacheRoot, projectDir: root })`.

**Test Plan**: extend `src/eval-server/__tests__/authoring-routes.test.ts` (or add a separate spec). Inject a temp cacheRoot via `registerPluginCliRoutes(router, root, { cacheRoot })`. Confirm GET /api/plugins returns 200 + the seeded plugins.

**Critical regression test (AC-US1-07)**: spawn the route handler with PATH set to `/dev/null-…` so any accidental `claude` invocation fails. The endpoint must still return 200 — proves we no longer shell out.

## T-003: Replace `fetchPluginList()` in `plugin-cli.ts`
**Status**: [x] completed · **Refs**: AC-US2-01..03

**Description**: Edit `src/eval-server/plugin-cli.ts:60`. The function signature can stay as `fetchPluginList(cwd?: string)` for callers' sake; internally, call `discoverInstalledPlugins({ cacheRoot: defaultCacheRoot, projectDir: cwd })`. Keep `parseInstalledPlugins` exported but unused in production.

**Test Plan**: covered by existing `plugin-cli-routes` mutation tests (enable/disable/install/uninstall) — they invoke `fetchPluginList` for post-mutation refresh; if this task regresses, those tests fail.

## T-004: Verify against TestLab/hi-anton
**Status**: [x] completed · **Refs**: success criteria

**Description**: After build, restart Studio via `preview_start vskill-studio-0795-plugin-list-fix` (add launch.json entry on a fresh port), check `preview_network` filter=failed for `/api/plugins` — must be empty. Take `preview_screenshot` for the closure record.

**Verification result**: Live test against `vskill studio --port 3230 --root /Users/antonabyzov/Projects/TestLab/hi-anton`. `GET /api/plugins` returned 200 with 2 real plugins (`codex@openai-codex`, `sw@specweave`), both correctly tagged `enabled: true, scope: "user"` from `~/.claude/settings.json`. Network tab clean (no failed requests). Two GET /api/plugins calls completed in 105ms + 1ms.

## T-005: Run full vitest + build
**Status**: [x] completed

**Description**: `npx vitest run` (no new failures vs the 7 pre-existing failures already documented in 0793). `npm run build` + `npm run build:eval-ui` clean.

**Result**: Full vitest sweep — 4825 passed, 7 pre-existing failures unrelated to this increment (TopRail/CommandPalette/useCreateSkill.flush — already failing on `main`). `npm run build` and `npm run build:eval-ui` clean.
