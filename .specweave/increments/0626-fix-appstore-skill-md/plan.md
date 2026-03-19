# Plan: Fix appstore SKILL.md

## Overview

Single-file edit: `repositories/anton-abyzov/vskill/.claude/skills/mobile/appstore/SKILL.md`. No code changes, no tests — this is a documentation/skill file fix. Verification via grep.

## Approach

Apply fixes in priority order (RED-LINE → HIGH → MEDIUM) using Edit tool. Global replacements for flags (`--app-id` → `--app`), targeted section edits for new content (workflows, warnings, install).

## Key Decisions

- Use `replace_all` for global flag fixes
- Replace phantom related skills with real vskill skills
- Split env var table into secrets (require protection) vs config (safe to log)
- Add variable capture patterns inline, right before first usage
