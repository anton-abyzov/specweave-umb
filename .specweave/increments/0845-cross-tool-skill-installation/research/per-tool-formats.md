# Per-Tool Skill Format Research (Phase 1)

**Date**: 2026-05-11
**Method**: Web research via Explore subagent (WebSearch + WebFetch) against 2026 docs.
**Purpose**: Catalog every agentic tool's skill/rules/instructions format, install path, and activation mechanism so vskill can build the right install adapter for each.

## Summary table

| Tool | Local install? | Path | Format | Frontmatter? | Activation | Notes |
|------|----------------|------|--------|--------------|------------|-------|
| **Codex CLI** | Yes — CLI native | `~/.codex/skills/<name>/SKILL.md` (global) or `$CODEX_HOME/skills/`. Also `~/.codex/AGENTS.md` | SKILL.md + YAML frontmatter | `name`, `description` required; optional `when_to_use`, `allowed-tools`, `model` | Auto-scan at session start; metadata only loaded; full body on match. Also `/skills` slash-cmd | **Drop-in compatible with Claude Code skill layout.** Restart Codex to reload. `[[skills.config]]` in `~/.codex/config.toml` to disable |
| **Antigravity** | Yes — IDE native | Global: `~/.gemini/antigravity/skills/`; Workspace: `.agents/skills/<name>/SKILL.md` (also legacy `.agent/skills/`). Rules: `~/.gemini/GEMINI.md` (AG-only) or `~/.gemini/AGENTS.md` (cross-tool); workspace `.agents/rules/` | SKILL.md + YAML frontmatter | `name`, `description` | Auto-scan frontmatter on session start; full body loaded on match | v1.20.3 (Mar 5, 2026) added AGENTS.md support. GEMINI.md > AGENTS.md priority |
| **Cursor** | Yes | Project: `.cursor/rules/*.mdc`. User-global: Settings → Rules (no canonical filesystem path, stored in app config) | `.mdc` (markdown + YAML) | `description`, `globs`, `alwaysApply` | `alwaysApply:true` always; `globs` on matching files; `description` for agent-requested | Legacy `.cursorrules` still works but deprecated. Keep alwaysApply rules <200 words |
| **Gemini CLI** | Yes — CLI native | Global: `~/.gemini/skills/` (alias `~/.agents/skills/`); Project: `.gemini/skills/` (alias `.agents/skills/`). Context: `GEMINI.md` | SKILL.md + YAML frontmatter | `name`, `description` (description critical — triggers selection) | Auto-scan; frontmatter only at startup; full body on activation. Max 1 dir deep | `gemini extensions install` auto-places skills under `~/.gemini/extensions/<ext>/skills/` |
| **ChatGPT** | **No** — cloud-only | N/A | Plain text paste into Custom Instructions (1,500 char limit) or Custom GPT system prompt (longer) or Project Instructions | None | Manual paste via web UI | **Tier 3** — vskill adapter outputs a clipboard-ready bundle with paste instructions. No filesystem hook |
| **Windsurf** | Yes | Project: `.windsurfrules` (file) or `.windsurf/rules/*.md` (dir). Global: Settings → Cascade → Custom Instructions. Memories: `~/.codeium/windsurf/memories/` (auto-generated, don't write here) | Plain markdown; `.md` files concatenated in `.windsurf/rules/` | None canonical | Always-on in system context | Per-team conventions go in `.windsurfrules` (committed). Personal prefs in global settings |
| **Aider** | Yes (limited) | `~/.aider.conf.yml` (global) + `~/.aider.conventions.md` (convention via absolute path). Project: `.aider.conf.yml`, `CONVENTIONS.md` | YAML (config) + plain markdown (conventions) | None | `read: [CONVENTIONS.md]` in conf file loads it as read-only context | No skill directory; everything is convention files. Model-agnostic by design |
| **OpenCode** | Yes — CLI native | Global rules: `~/.config/opencode/AGENTS.md`. Project: `AGENTS.md` in root. Skills: `.opencode/skills/<name>/SKILL.md`. Also reads `.claude/skills/` and `.agents/skills/` walking up to git root. Commands: `.opencode/commands/<name>.md` | SKILL.md + YAML frontmatter; commands are plain markdown with `$ARGUMENTS` | `name`, `description` | Auto-discover walking up to git root; multi-source compatible | **Reads `.claude/skills/` natively — Claude Code skills work unchanged** |
| **OpenClaw** | Yes — CLI native | `~/.openclaw/skills/` (global), `.openclaw/skills/` (project). Manifest: `~/.openclaw/openclaw.json` | Identical to Claude Code SKILL.md | `name`, `description` | Auto-scan; restart session to reload | **Layout + format identical to Claude Code** |
| **Continue.dev** | Yes | `~/.continue/config.yaml` (global), `.continue/config.json` (project). Rules: `.continue/rules/`. Slash commands defined in config | YAML/JSON config; rules as plain markdown | None | Modal — Agent, Chat, Edit modes all consume rules | No SKILL.md ecosystem; closer to "named prompts + rules" model |
| **GitHub Copilot** | Yes (limited) | `.github/copilot-instructions.md` (repo). Path-scoped: `.github/instructions/NAME.instructions.md`. Also reads `AGENTS.md`. Prompt files in VS Code only | Plain markdown; `.instructions.md` uses `applyTo:` frontmatter | `applyTo: "glob"` on instructions files | Applies to Chat, JetBrains, GH.com chat, cloud agent, Copilot CLI — **NOT inline ghost-text** | Priority: personal > path-scoped > copilot-instructions > AGENTS.md > org |
| **Junie (JetBrains)** | Yes | `.junie/AGENTS.md` (default), `.junie/rules/*.md` (concatenated), legacy `.junie/guidelines.md`. Custom path via `JUNIE_GUIDELINES_FILENAME` env | Plain markdown | None | Always-loaded as project context | Configurable path in Settings → Tools → Junie |
| **Kiro (AWS)** | Yes | Global: `~/.kiro/steering/*.md`. Workspace: `.kiro/steering/*.md` | Plain markdown ("steering files"); convention names `product.md`, `tech.md`, `structure.md` | None | Smart conditional loading (2026 update); workspace overrides global | 17 hooks enforce checks. Spec-driven IDE — similar mental model to SpecWeave |
| **Trae (ByteDance)** | Yes (limited) | `.trae/` directory in project; supports `TRAE.md`-style rule files. MCP-based for tools | Plain markdown rules + MCP config | None | Custom agents via `.trae/` | Less mature ecosystem; standardize via committed `.trae/` repo |
| **bolt.new / v0 / Devin / Replit Agent / Lovable** | **No** — cloud-only | N/A | v0: Project Settings → Knowledge (paste). Bolt: artifact_instructions inline. Devin: per-session prompt. Replit: project description | None | Manual paste in web UI | **Tier 3/4.** vskill outputs clipboard-ready blob with per-tool paste instructions |

## Tier classification

**Tier 1 — Drop-in (write SKILL.md, tool picks it up unchanged)**:
- Claude Code
- Codex CLI (`~/.codex/skills/`)
- OpenClaw (`~/.openclaw/skills/` — byte-identical to Claude Code)
- OpenCode (reads `.claude/skills/` natively + own `.opencode/skills/`)
- Antigravity (`.agents/skills/` workspace, `~/.gemini/antigravity/skills/` global)
- Gemini CLI (`~/.gemini/skills/`)

These six share the **SKILL.md + YAML frontmatter (`name`, `description`)** convention. A single source-of-truth skill file installs to all with only path rewriting. No transformer needed — reuse existing `installSymlink` / `installCopy` flow.

**Tier 2 — File works, format conversion needed**:
- **Cursor** — SKILL.md → `.mdc` with `description`/`globs`/`alwaysApply` frontmatter; map `description`→`description`, add `alwaysApply:false`, empty `globs:""`
- **Windsurf** — Split SKILL.md into `.windsurf/rules/<name>.md`, strip YAML frontmatter (plain markdown)
- **GitHub Copilot** — Per-skill `.github/instructions/<name>.instructions.md` with `applyTo: "**"` frontmatter
- **Junie** — `.junie/rules/<name>.md`, strip frontmatter
- **Kiro** — `.kiro/steering/<name>.md`, strip frontmatter
- **Continue.dev** — `.continue/rules/<name>.md`, strip frontmatter
- **Aider** — `~/.aider/conventions/<name>.md` + append entry to `~/.aider.conf.yml` `read:` list (use backup-write pattern)
- **Trae** — `.trae/<name>.md`, strip frontmatter

**Tier 3 — Clipboard/export only (no filesystem)**:
- ChatGPT Custom Instructions (1500 char limit)
- ChatGPT Custom GPT (system prompt)
- ChatGPT Project Instructions
- v0 (Project Settings → Knowledge)
- bolt.new (first-message paste)
- Lovable / Same.dev

Adapter output: blob + 1-paragraph paste instructions + link to tool's settings URL.

**Tier 4 — No install surface (link-to-docs only)**:
- Devin (per-session only; no persistent custom instructions surface as of May 2026)
- Replit Agent (project-level description only; no skill import)

Already gated by `isRemoteOnly: true` in vskill registry. Render with "REMOTE" badge in cloud-only section.

## Key implementation notes

1. **Tier 1 is the big unlock** — six tools share the SKILL.md format. The adapter just needs path resolution + a restart hint per tool.
2. **AGENTS.md is the emerging cross-tool standard** — Codex, OpenCode, Antigravity, Junie, Copilot all read it. vskill could optionally compile a top-level skill catalog into `AGENTS.md` as a fallback (future work, not this increment).
3. **The Antigravity gap the user flagged**: install to `~/.gemini/antigravity/skills/<name>/SKILL.md` (global) or `.agents/skills/<name>/SKILL.md` (workspace). Frontmatter requires `name` + `description`. ~1-day adapter.
4. **ChatGPT adapter is paste-only** — design the UX around copy-to-clipboard with a "How to install" sub-flow per surface (custom GPT vs Project vs Custom Instructions). No filesystem at all.
5. **Cursor MDC conversion**: SKILL.md → `.mdc` is mechanical — wrap the body, rewrite frontmatter to `description`/`globs:""`/`alwaysApply:false` (agent-requested mode mirrors Claude Code's auto-trigger semantics best).

## Sources

- [Codex AGENTS.md (OpenAI Developers)](https://developers.openai.com/codex/guides/agents-md)
- [Codex Agent Skills (OpenAI Developers)](https://developers.openai.com/codex/skills)
- [The Codex CLI Customisation Stack](https://codex.danielvaughan.com/2026/04/12/codex-cli-customisation-stack-unified-system/)
- [Antigravity Rules Guide (AGENTS.md & Examples)](https://antigravity.codes/blog/user-rules)
- [Antigravity Skills Documentation](https://antigravity.google/docs/skills)
- [Cursor Rules Documentation](https://docs.cursor.com/context/rules)
- [Cursor Rules: Complete .mdc Guide (2026)](https://www.vibecodingacademy.ai/blog/cursor-rules-complete-guide)
- [Gemini CLI Agent Skills](https://geminicli.com/docs/cli/skills/)
- [Gemini CLI Creating Skills](https://geminicli.com/docs/cli/creating-skills/)
- [ChatGPT Custom Instructions (OpenAI Help)](https://help.openai.com/en/articles/8096356-chatgpt-custom-instructions)
- [Windsurf Cascade Memories](https://docs.windsurf.com/windsurf/cascade/memories)
- [.windsurfrules Complete Guide (2026)](https://thepromptshelf.dev/blog/windsurfrules-complete-guide-2026/)
- [Aider YAML config](https://aider.chat/docs/config/aider_conf.html)
- [Aider Specifying coding conventions](https://aider.chat/docs/usage/conventions.html)
- [OpenCode Rules](https://opencode.ai/docs/rules/)
- [OpenCode Agent Skills](https://opencode.ai/docs/skills/)
- [OpenClaw Skills Directory (Agensi)](https://www.agensi.io/learn/openclaw-skills-directory-path)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [Continue.dev Customization Overview](https://docs.continue.dev/customize/overview)
- [Continue.dev Slash Commands](https://docs.continue.dev/customize/slash-commands)
- [GitHub Copilot Repository Custom Instructions](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)
- [Junie Guidelines and Memory](https://junie.jetbrains.com/docs/guidelines-and-memory.html)
- [Junie Customize Guidelines](https://www.jetbrains.com/help/junie/customize-guidelines.html)
- [Kiro Steering Documentation](https://kiro.dev/docs/steering/)
- [TRAE IDE Rules](https://docs.trae.ai/ide/rules?_lang=en)
- [System prompts & models of AI tools (Bolt/v0/Devin/Replit leak archive)](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools)
