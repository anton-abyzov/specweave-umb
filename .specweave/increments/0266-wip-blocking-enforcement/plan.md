# 0266 — Plan

## Approach

Single-file change: rewrite Step 0B in the `/sw:increment` SKILL.md from pseudocode
into a concrete, enforced blocking step with two tiers.

## File Modified

- `repositories/anton-abyzov/specweave/.cursor/skills/sw/skills/increment/SKILL.md`
  — Step 0B (lines 70–97)

## Design

### Two-Tier Gate

| Tier | Condition | Behavior |
|------|-----------|----------|
| Soft | WIP >= 1, below hardCap | Show list, stop, wait for any user reply |
| Hard | WIP >= hardCap | Escalated warning, stop, wait for any user reply |
| Skip | WIP = 0 OR type is hotfix/bug | Proceed (hotfix/bug gets brief notice) |

### Enforcement Mechanism

The gate is enforced at the AI-skill level: the SKILL.md instructions tell the model
to STOP and wait for user input. This is the same mechanism used for plan mode
approval — the model presents information and does not continue until the user replies.

### Detection Method

Bash command in SKILL.md scans `metadata.json` files for in-flight statuses.
