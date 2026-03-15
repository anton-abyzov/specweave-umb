# Plan: Local Plugin Installation

## Approach
Replace the `claude plugin install` pathway with direct file copy to `.claude/skills/`.

## Changes
1. `plugin-copier.ts` — Add `copyPluginSkillsToProject()` function
2. `plugin-installer.ts` — Always full install, use direct copy
3. `user-prompt-submit.sh` — Remove on-demand plugin install section
4. `llm-plugin-detector.ts` — Remove plugin install triggers
5. `init.ts` — Remove lazyMode flag
