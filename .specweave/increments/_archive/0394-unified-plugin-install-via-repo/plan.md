# Architecture Plan: Unified Plugin Installation via --repo

## Overview

This is a targeted change to a single shell script (`user-prompt-submit.sh`) and the startup health check (`startup-health-check.sh`). No new architecture is introduced -- the existing `--repo` pattern used by domain plugins is simply extended to sw-* plugins.

## Changes

### 1. Rewrite `install_plugin_via_vskill()` (user-prompt-submit.sh, lines 488-522)

**Current**: Depends on `~/.claude/plugins/marketplaces/specweave` local directory.
```bash
install_plugin_via_vskill() {
  local plugin="$1"
  local plugin_dir="${HOME}/.claude/plugins/marketplaces/specweave"
  if [[ ! -d "$plugin_dir" ]] || [[ ! -f "$plugin_dir/.claude-plugin/marketplace.json" ]]; then
    VSKILL_INSTALL_OUTPUT="marketplace directory not found at $plugin_dir"
    return 1
  fi
  npx vskill install --plugin-dir "$plugin_dir" --plugin "$plugin" --force --yes
}
```

**New**: Uses `--repo anton-abyzov/specweave` to fetch from GitHub directly.
```bash
install_plugin_via_vskill() {
  local plugin="$1"
  VSKILL_INSTALL_OUTPUT=""
  if command -v npx >/dev/null 2>&1; then
    if command -v timeout >/dev/null 2>&1; then
      VSKILL_INSTALL_OUTPUT=$(timeout 30 npx vskill install --repo anton-abyzov/specweave --plugin "$plugin" --agent claude-code --force --yes 2>&1) || true
    else
      VSKILL_INSTALL_OUTPUT=$(npx vskill install --repo anton-abyzov/specweave --plugin "$plugin" --agent claude-code --force --yes 2>&1) || true
    fi
  else
    VSKILL_INSTALL_OUTPUT="vskill not available (npx not found)"
    return 1
  fi
  if echo "$VSKILL_INSTALL_OUTPUT" | grep -qiE "(installed|Installed)"; then
    return 0
  else
    return 1
  fi
}
```

Key differences:
- Removes dependency on local marketplace directory
- Uses `--repo anton-abyzov/specweave` (mirrors `install_vskill_repo_plugin` pattern)
- Adds `--agent claude-code` flag for proper lockfile tracking
- Increases timeout from 15s to 30s (network fetch needs more time)
- Removes fallback to `$HOME/.claude/plugins/marketplaces/specweave/node_modules/.bin/vskill`

### 2. Route `docs` Plugin Correctly

The `docs` plugin exists in `anton-abyzov/specweave` marketplace, not `anton-abyzov/vskill`. Currently it's in `VSKILL_REPO_PLUGINS` which routes to `install_vskill_repo_plugin()` (uses `--repo anton-abyzov/vskill`). After the fix:
- Remove `docs` from `VSKILL_REPO_PLUGINS`
- The `docs` plugin should be treated as a specweave plugin (like sw-*) and installed via `install_plugin_via_vskill()` which uses `--repo anton-abyzov/specweave`
- Add `docs` to the sw-* plugin detection condition (line ~1294)

### 3. Clean Up `VSKILL_REPO_PLUGINS` List

Remove plugins that don't exist in the vskill marketplace:
- `k8s` -- not in marketplace (use `infra` for Kubernetes)
- `cost` -- not in marketplace
- `docs` -- in specweave marketplace, not vskill

### 4. Update Scope Guard (lines ~297-304)

Change the sw-* reinstallation path in the scope guard to also use `install_plugin_via_vskill()` (which will now use `--repo`). This is already the case -- the scope guard calls `install_plugin_via_vskill "$_sw_name"`, so it will automatically benefit from the function rewrite.

### 5. Update Suggest-Only Mode Message

The suggest-only message at line ~1266 still references the old `--plugin-dir` syntax. Update to:
```
npx vskill install --repo anton-abyzov/specweave --plugin <plugin> --force
```

### 6. Update Startup Health Check

`startup-health-check.sh` references `SPECWEAVE_DIR="$PLUGINS_DIR/marketplaces/specweave"`. This needs to be reviewed -- if it's only used for checking marketplace existence, remove or update the check.

## Risk Assessment

- **Low risk**: The `--repo` installation path is already battle-tested by domain plugins
- **Network dependency**: `--repo` requires GitHub access (same as domain plugins already do)
- **Timeout**: Increased to 30s to match domain plugin timeout (network fetch vs local copy)
- **Backward compatible**: Users who still have the marketplace directory won't be affected (the old path is simply replaced, not conditionally chosen)

## Files to Modify

1. `repositories/anton-abyzov/specweave/plugins/specweave/hooks/user-prompt-submit.sh` -- main changes
2. `repositories/anton-abyzov/specweave/plugins/specweave/hooks/startup-health-check.sh` -- remove stale marketplace reference
