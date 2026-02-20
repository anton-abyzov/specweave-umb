# Plan: App Store Connect CLI Skill

## Approach

Create a single comprehensive `SKILL.md` file in `specweave-mobile/skills/appstore/` following the exact pattern established by the `/sw:npm` skill — a detailed, mode-based playbook that agents can follow autonomously.

## Key Design Decisions

1. **CLI-first, not MCP**: Use `asc` CLI directly via Bash. MCP wrapper can come later if needed.
2. **Mode-based workflow**: Mirror npm skill's flag pattern (`--testflight`, `--submit`, `--status`, etc.)
3. **Authentication-first**: Every mode starts with auth validation (like npm's Step 0 repo discovery)
4. **App discovery**: Auto-detect app ID from project config (Xcode project, app.json, etc.) or ask user
5. **Safety**: `--dry-run` support on destructive operations, confirmation before submissions
6. **JSON output**: Leverage `asc`'s JSON-first design for agent parsing

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `plugins/specweave-mobile/skills/appstore/SKILL.md` | **CREATE** | Main skill playbook (~800-1000 lines) |
| `plugins/specweave-mobile/PLUGIN.md` | **EDIT** | Add `appstore` to skills table |

## Workflow Modes (Priority Order)

1. **Step 0: Auth & App Discovery** — Always runs first (like npm's repo discovery)
2. **`--testflight`** — Most common: upload + distribute to testers
3. **`--submit`** — App Store submission with validation
4. **`--status`** — Quick check (simplest mode)
5. **`--validate`** — Pre-submission check
6. **`--metadata`** — Update app info/screenshots
7. **`--builds`** — Build management
8. **`--signing`** — Certificate/profile management
9. **`--analytics`** — Reports and reviews
10. **Default (no flags)** — Guided workflow that asks what to do

## Risks

- `asc` CLI is unofficial and may change — document version expectations
- API key setup is a one-time hurdle — auth section must be thorough
- IPA/PKG upload requires the file to exist — skill doesn't build, only distributes
