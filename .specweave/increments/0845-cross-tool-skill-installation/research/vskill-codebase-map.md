# vskill Codebase Map (Phase 1)

**Date**: 2026-05-11
**Method**: Two parallel Explore subagents over `repositories/anton-abyzov/vskill/src/`.
**Purpose**: Map current Studio UI + install pipeline so the cross-tool feature extends rather than rewrites.

## Tool registry — source of truth

**File**: `src/agents/agents-registry.ts:99–687`

`AgentDefinition` interface fields:
```ts
interface AgentDefinition {
  id: string;                              // "claude-code", "cursor", "devin", ...
  displayName: string;                     // "Claude Code", "Cursor", ...
  localSkillsDir: string;                  // e.g., ".claude/skills"
  globalSkillsDir: string;                 // e.g., "~/.claude/skills"
  isUniversal: boolean;                    // 8 universal, 45 non-universal
  detectInstalled: string | (() => Promise<boolean>);
  parentCompany: string;
  featureSupport: FeatureSupport;          // slashCommands, hooks, mcp, customSystemPrompt
  pluginCacheDir?: string;                 // Claude Code only
  pluginMarketplaceDir?: string;           // Claude Code only
  win32PathOverride?: string;              // Windows-specific path
  isRemoteOnly?: boolean;                  // Devin, bolt.new, v0, Replit = true
}
```

**53 entries** including: Claude Code, Cursor, Codex CLI, Gemini CLI, OpenCode, OpenClaw, Antigravity, Aider, Augment, Continue, Copilot CLI, Droid, Junie, Roo, Trae, Windsurf, Kiro, Cline, Amp, Kimi CLI, GitHub Copilot Ext, Devin (remote), bolt-new (remote), v0 (remote), Replit (remote), + 30 others.

**Detection function**: `agents-registry.ts:853 detectInstalledAgents()`
- Skips `isRemoteOnly: true` entries
- Two-tier probe: (1) `detectBinary()` via `src/utils/resolve-binary.ts`, (2) fallback to checking if `globalSkillsDir` exists

## Install pipeline

**Entry points**:
- CLI: `vskill install <skill>` → `src/commands/add.ts:addCommand()`
- HTTP: `POST /api/studio/install-skill` → `src/eval-server/install-skill-routes.ts:registerInstallSkillRoutes()` (line 50)

**Routes** (`src/eval-server/install-skill-routes.ts` and related):

| Route | Method | Purpose | Scopes |
|-------|--------|---------|--------|
| `/api/studio/install-skill` | POST | Install single skill | "project", "user", "global" |
| `/api/studio/install-skill/:id/stream` | GET | SSE progress stream | N/A |
| `/api/studio/install-engine` | POST | Install missing engine | engine names only |
| `/api/studio/install-state` | GET | Per-skill install state per scope | query `?skill=<pub>/<slug>` |
| `/api/studio/detect-engines` | GET | Report skill-builder availability | N/A |

**Security**: Localhost-only, `SAFE_NAME` regex `/^[a-zA-Z0-9._@/\-]+$/`, hardcoded command names (no shell injection).

**Install core**: `src/installer/canonical.ts:installSymlink()` (line 134) + `installCopy()` (line 227)
- Universal SKILL.md format (no tool-specific transpilation today)
- Symlinks from agent-specific dir → canonical `~/.agents/skills/<name>/`
- Per-agent field stripping: `stripClaudeFields()` (frontmatter.ts) removes Claude-specific YAML for non-Claude agents
- `COPY_FALLBACK_AGENTS = {"claude-code"}` (canonical.ts:109) — only Claude Code gets symlink-fallback-to-copy

**Format handling**: `src/installer/frontmatter.ts`
- `parseFrontmatter()`, `ensureFrontmatter()` — input validation
- `stripClaudeFields()` — removes Claude-specific YAML lines via regex for non-Claude tools
- `CLAUDE_FIELD_PATTERNS` (line 11-17) controls which fields to strip
- `getAgentCreationProfile()` (agents-registry.ts:758-789) customizes per-agent

## Frontend (eval-ui)

**Framework**: React with React Router (HashRouter)
**Source**: `src/eval-ui/src/` (550 .ts/.tsx files)
**Built output**: `dist/eval-ui/`
**Served by**: `src/eval-server/eval-server.ts:113` reads `path.resolve(__dirname, "../eval-ui")` — pre-built bundle, **NOT Vite** (per project memory `project_vskill_studio_runtime.md`)

**Right-panel components**:
- `src/eval-ui/src/components/AgentScopePicker.tsx` (lines 1-210) — 40px sticky trigger row showing `displayName · (installed · global · plugins)`
- `src/eval-ui/src/components/AgentScopePicker.Popover.tsx` — Two-pane popover (agents list, stats pane)
- Existing sections: "Detected" (active install affordance) + "Not Detected" (passive, no install button) + "REMOTE" badge for cloud-only

**Scopes in UI**:
- `project` → lockfile at `./vskill.lock`
- `user` → lockfile at `~/.agents/vskill.lock`
- `global` flag → maps to user-level install

No explicit "Install Globally" button in UI today — scope is inferred from `--global` flag in install command.

## Gotchas identified

1. **`detectInstalledAgents()` is the gate hiding install for undetected tools** — even though those tools have full `AgentDefinition` entries with valid paths. This is the bug the user is hitting with Codex.
2. **Single-agent install only** — current routes accept one agent at a time.
3. **No per-tool format adapter** — Cursor `.mdc`, Windsurf, Copilot `.instructions.md`, etc. all get raw SKILL.md (with Claude fields stripped), which works for Tier 1 but not Tier 2.
4. **Tier 3 has no surface at all** — clipboard mode doesn't exist yet.
5. **Antigravity registry entry exists** — need to verify the path matches the documented `~/.gemini/antigravity/skills/`. May need a registry fix.

## Extension surface (what changes for cross-tool install)

| Layer | Change |
|-------|--------|
| `AgentDefinition` interface | Add optional `tier`, `installMode`, `formatTransformer`, `pasteInstructionsUrl` |
| Registry rows | Populate new fields per tool; ensure Antigravity path correct |
| `canonical.ts` | When `formatTransformer` is set, call it and write transformer output instead of canonical SKILL.md |
| `multi-install.ts` (NEW) | Sequential per-agent install dispatching tier-correct path |
| `transformers/*.ts` (NEW) | 8 pure transformer modules |
| `clipboard-export.ts` (NEW) | Tier 3 blob builder |
| `install-skill-routes.ts` | Accept `agentIds[]`; SSE per-agent events |
| `export-skill-routes.ts` (NEW) | Tier 3 endpoint |
| Detection route | Add `/api/studio/supported-agents` (all non-remote-only) |
| `AgentScopePicker.Popover.tsx` | 3-section restructure (Detected / Available / Cloud) |
| `InstallTargetsModal.tsx` (NEW) | Multi-tool checkbox modal |
| `ClipboardExportDialog.tsx` (NEW) | Tier 3 paste UI |
| `dist/eval-ui/` | Rebuild via `npm run build:ui` |

## No new external dependencies

- No new npm packages required
- No new env vars (one optional: `VSKILL_ANTIGRAVITY_SKILLS_DIR` override)
- No schema changes to `vskill.lock`
- No verified-skill.com server changes
