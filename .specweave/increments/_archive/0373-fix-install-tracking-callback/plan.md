# Architecture: Fix install tracking callback

## Overview

Surgical bug fixes across two repos (vskill CLI + vskill-platform) to ensure `reportInstall()` fires correctly on all install paths with the right skill name, and the platform endpoint decodes URL-encoded names.

## Changes

### 1. vskill CLI — `commands/add.ts`

**installPluginDir()** (~line 677, after lockfile write):
- Add: `reportInstall(pluginName).catch(() => {});`

**installRepoPlugin()** (~line 1088, after lockfile write):
- Add: `reportInstall(pluginName).catch(() => {});`

**tryNativeClaudeInstall()** (line 189):
- Remove: `reportInstall(pluginName).catch(() => {});`
- Reason: The parent `installPluginDir` will now handle reporting. Keeping it here would double-report when native install path succeeds.

**installFromRegistry()** (line 1479):
- Change: `reportInstall(skillName)` to `reportInstall(detail.name)`
- Reason: `skillName` is user input (may be variant spelling); `detail.name` is the canonical name from the registry that matches the platform DB.

### 2. vskill-platform — `installs/route.ts`

**POST handler** (line 47):
- Change: `const { name: skillName } = await params;`
- To: `const { name: rawName } = await params; const skillName = decodeURIComponent(rawName);`
- Reason: CLI client uses `encodeURIComponent(skillName)` when building the URL. Explicit decoding ensures correctness for all special characters.

### 3. vskill-platform — `installs/__tests__/route.test.ts`

- Add test case: URL-encoded skill name (e.g., `my%40skill`) is properly decoded and matched against DB.

## Risks

- **Low**: All changes are additive (adding missing calls) or surgical (swapping variable names). No architectural changes.
- **Double-report prevention**: Removing `reportInstall` from `tryNativeClaudeInstall` while adding it to `installPluginDir` means the report happens once regardless of native-vs-extraction path.

## Testing Strategy

- Existing unit tests for the platform route must continue to pass
- New test for URL-encoded names on platform route
- CLI changes are fire-and-forget calls -- verified by code inspection (no unit test infrastructure for add.ts install paths)

## Sequence

1. Fix platform endpoint first (decodeURIComponent) -- makes the server ready
2. Add test for encoded names on platform
3. Fix CLI call sites -- add missing reportInstall, fix wrong names, remove duplicate
4. Verify all tests pass
