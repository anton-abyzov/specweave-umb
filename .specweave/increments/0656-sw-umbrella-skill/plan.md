---
increment: 0656-sw-umbrella-skill
---

# Architecture: sw:umbrella skill

## Overview

Single SKILL.md file — no TypeScript code. The skill instructs the AI to orchestrate existing CLI commands (`specweave init`, `specweave get`) and shell operations (`mkdir`, `mv`, `ln -s`).

## File Location

`repositories/anton-abyzov/specweave/plugins/specweave/skills/umbrella/SKILL.md`

## Design Decisions

- **Skill, not CLI**: AI handles interactive decisions (naming, confirmation for moves)
- **Leverages existing commands**: `specweave init` + `specweave get` do heavy lifting
- **Symlink manifest**: `.specweave/state/symlinks.json` tracks created symlinks
- **Idempotent**: Each step checks before executing
- **Destructive ops gated**: Moving repos requires user confirmation

## Dependencies

- `specweave init` — creates .specweave/, config.json, CLAUDE.md
- `specweave get` — clones + registers repos in umbrella config
- `git remote get-url origin` — detects org/repo from local repos
