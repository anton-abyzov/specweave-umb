# Plan: vskill `codex-bridge` plugin

## Architecture

Single new plugin directory in the vskill repo, with two manifest files and a single-skill payload that's deliberately strict-mode compatible across runtimes.

```
repositories/anton-abyzov/vskill/
├── .agents/plugins/marketplace.json   # NEW — Codex marketplace discovery
├── .claude-plugin/marketplace.json    # MODIFY — append 9th entry
└── plugins/codex-bridge/              # NEW
    ├── .claude-plugin/plugin.json     # for Claude Code
    ├── .codex-plugin/plugin.json      # for Codex
    ├── README.md                      # dual-target authoring guide
    └── skills/agents-md-author/
        ├── SKILL.md                   # frontmatter: name + description ONLY
        └── references/
            └── agents-md-spec.md      # lazy-loaded cross-vendor spec
```

## Decisions

- **Strict frontmatter** — `SKILL.md` has only `name` + `description`. Codex rejects extra keys; Claude accepts them. The intersection works in both. README documents this rule.
- **Two manifests, near-identical** — `.claude-plugin/plugin.json` follows existing vskill convention (mirrors `plugins/skills/.claude-plugin/plugin.json`). `.codex-plugin/plugin.json` adds `skills[]` array (Codex requires explicit skill paths) and an `interface{}` block (marketplace presentation).
- **Top-level Codex marketplace** — `.agents/plugins/marketplace.json` lists only `codex-bridge` (other 8 plugins lack `.codex-plugin/`, so listing them would produce broken Codex installs).
- **No CLI source changes** — vskill's installer (`src/installer/canonical.ts`) already symlinks to `.codex/skills/` for the `codex` agent. We rely on existing behavior.
- **Test target** — `/tmp/codex-bridge-test/` (fresh tmpdir; rm at end).

## File responsibilities

| File | Purpose | Source of truth |
|---|---|---|
| `plugins/codex-bridge/.claude-plugin/plugin.json` | Claude marketplace record | mirrors existing pattern |
| `plugins/codex-bridge/.codex-plugin/plugin.json` | Codex marketplace record | OpenAI schema |
| `plugins/codex-bridge/skills/agents-md-author/SKILL.md` | The skill (strict frontmatter) | LCD of both runtimes |
| `plugins/codex-bridge/skills/agents-md-author/references/agents-md-spec.md` | Cross-vendor spec primer | Phase 1 research |
| `plugins/codex-bridge/README.md` | Authoring guide | this plan |
| `.agents/plugins/marketplace.json` | Codex marketplace at repo root | new |
| `.claude-plugin/marketplace.json` | Claude marketplace at repo root | append 9th |

## Critical references in existing code

- `plugins/skills/.claude-plugin/plugin.json` — canonical `.claude-plugin/plugin.json` shape
- `plugins/skills/skills/scout/SKILL.md` — reference SKILL.md (we'll use stricter subset)
- `.claude-plugin/marketplace.json:8-65` — entry shape to mirror
- `src/installer/canonical.ts:91-192` — symlink + Claude field-strip (no change)
- `src/agents/agents-registry.ts` — `codex` + `cursor` agent IDs (no change)
- `src/commands/submit.ts` — publish flow (not used in this increment)

## ADRs

No new ADRs required — this is a content addition, not an architectural change to vskill itself. The dual-manifest pattern is documented in the plugin README; if it stabilizes, it can be promoted to a vskill-wide ADR in the follow-up `--target` increment.

## Verification (verbatim from approved plan)

Tests A-F run from a fresh `/tmp/codex-bridge-test/`. All six must pass for `/sw:done`.

1. **A — vskill install** dual-target: `.claude/skills/agents-md-author/SKILL.md` + `.codex/skills/agents-md-author/SKILL.md`
2. **B — codex plugin marketplace add** local path discovers `codex-bridge`
3. **C — strict frontmatter** check: only `name` + `description` keys
4. **D — schema conformance** vs OpenAI spec (kebab-case name, semver, `skills[]` paths exist)
5. **E — marketplace registry**: claude has 9 plugins, codex has 1
6. **F — cleanup** tmpdir + remove Codex marketplace

## Risks & mitigations

- **Codex CLI rejects manifest** — validate against schema before `marketplace add`; capture and fix on failure
- **vskill installer doesn't recognize plugin** — follow existing 8-plugin shape exactly
- **`.agents/` clashes with vskill flow** — placed at canonical Codex path, doesn't overlap with `.claude-plugin/`
- **Frontmatter drift over time** — Test C codified as regression check; lift to CI in follow-up

## Out of scope

- Migrating 8 existing plugins to dual-manifest
- `vskill --target codex|claude|both` flag
- verified-skill.com publishing
- `.app.json` / `hooks.json`
