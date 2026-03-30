# Implementation Plan: Figma Connect Skill - Combined MCP + CLI

## Overview

Create a new vskill plugin skill (`figma-connect`) under a new `frontend` category. The skill combines 16 Figma MCP server tools with the Code Connect CLI into 5 workflow modes. Implementation follows TDD: evals first (failing tests), then SKILL.md iteratively until evals pass.

## Architecture

### File Structure
```
plugins/frontend/
├── .claude-plugin/
│   └── plugin.json              # Category metadata
└── skills/
    └── figma-connect/
        ├── SKILL.md             # Core skill (~480 lines)
        ├── evals/
        │   ├── evals.json       # 12 eval cases
        │   └── activation-prompts.json  # 20 prompts
        └── references/
            ├── mcp-tools-reference.md
            ├── code-connect-cli-reference.md
            └── token-format-mappings.md
```

### SKILL.md Sections (~480 lines)
1. **Frontmatter** (8 lines) — name, description, metadata
2. **Prerequisites & Dual Auth** (20 lines) — MCP OAuth + CLI token
3. **Framework Detection** (30 lines) — project file → CC label mapping
4. **Mode 1: Setup** (50 lines) — auth, install, config, rules
5. **Mode 2: Design-to-Code** (80 lines) — URL parse, screenshot, get_design_context, adapt
6. **Mode 3: CC Publish** (80 lines) — suggestions, .figma.tsx, validate, publish, verify
7. **Mode 4: Token Extraction** (60 lines) — get_variable_defs, format detection, write
8. **Mode 5: Roundtrip** (60 lines) — full lifecycle orchestration
9. **MCP vs CLI Decision Tree** (40 lines) — when to use which
10. **Error Handling** (40 lines) — error table

### Key Design Decisions

1. **MCP for READ, CLI for PUBLISH** — clear, unambiguous boundary
2. **Dual auth paths** — MCP (OAuth) and CLI (FIGMA_ACCESS_TOKEN) are independent; skill detects and guides both
3. **Reference offloading** — detailed API docs in references/ keep SKILL.md under 500 lines
4. **Framework-aware** — detects from project files, passes to both MCP and CLI
5. **New frontend category** — extensible for future design skills

## Technology Stack

- **Skill format**: SKILL.md (YAML frontmatter + markdown)
- **Eval format**: JSON (evals.json, activation-prompts.json)
- **MCP tools**: 16 Figma MCP tools (claude_ai_Figma namespace)
- **CLI**: `@figma/code-connect` v1.4.2+
- **Eval runner**: `npx vskill eval run|serve`

## Testing Strategy

TDD approach:
1. **RED**: Write evals/evals.json + activation-prompts.json first (12 cases, 20 prompts)
2. **GREEN**: Build SKILL.md iteratively, running evals after each mode addition
3. **REFACTOR**: Benchmark, analyze failures, iterate until 83%+ pass rate

Target metrics:
- Benchmark: 10/12 pass (83%)
- Activation precision: 100%
- Activation recall: 90%+
