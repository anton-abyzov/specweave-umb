# MD Templates

These are **instruction templates for user projects** that use SpecWeave.

## What are these files?

`CLAUDE.md` and `AGENTS.md` are AI instruction files that get generated when a user runs `specweave init` in their project. They tell AI tools (Claude Code, Cursor, Copilot, Windsurf, Aider, etc.) how to work with SpecWeave's spec-driven workflow.

- **CLAUDE.md** — Instructions for Claude Code (Anthropic's CLI). Loaded automatically into every conversation.
- **AGENTS.md** — Instructions for ALL AI tools (Cursor, Copilot, Windsurf, Aider, ChatGPT, Gemini CLI, etc.). Tool-agnostic format.

Both files are generated from templates in `repositories/anton-abyzov/specweave/src/templates/`:
- `CLAUDE.md.template` — Source template for CLAUDE.md
- `AGENTS.md.template` — Source template for AGENTS.md

## When to update these templates

Add information here when it should be included in BOTH templates (since we support all AI tools):

- New workflow rules or conventions
- Changes to the increment lifecycle (plan, do, done)
- New quality gates or validation steps
- New sync integrations (GitHub, Jira, ADO)
- Changes to auto-closure behavior, testing pipeline, or skill chaining

## Important reusable content

Any important instruction that applies to how AI should work with SpecWeave projects belongs in BOTH templates. When adding a new rule:

1. Add to `CLAUDE.md.template` (Claude Code specific format, with `<!-- SECTION -->` markers)
2. Add to `AGENTS.md.template` (tool-agnostic format, with `<!-- SECTION -->` markers)
3. Test by running `specweave init` in a test project to verify output

## Template syntax

Templates use `<!-- SECTION:name -->` / `<!-- /SECTION -->` markers. Sections marked `required` are always included. Optional sections can be toggled via `specweave init` configuration.

Placeholder variables:
- `{PROJECT_NAME}` — Replaced with the user's project name
- `{AGENTS_SECTION}` — Auto-populated agent roles
- `{SKILLS_SECTION}` — Auto-populated skill list
- `{TIMESTAMP}` — Generation timestamp
