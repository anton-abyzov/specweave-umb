# FS-533: Remove vskill plugin installation from auto-loading

## Problem
SpecWeave's UserPromptSubmit hook tries to auto-install plugins via `npx vskill install`, but domain plugins (frontend, backend, etc.) don't exist in the vskill marketplace. This causes errors like "Plugin 'frontend' not found in marketplace 'vskill'". The project has moved to direct file copy for skill installation.

## Solution
Remove all `vskill install` calls from the auto-loading pipeline. SW plugins use native `claude plugin install` (via plugin-copier.ts). Domain plugins are removed entirely since they don't exist.

## Acceptance Criteria
- [x] AC-01: No `npx vskill install` calls remain in hooks or lazy-loading code
- [x] AC-02: SW plugin installation uses native `claude plugin install` approach
- [x] AC-03: LLM detection prompt no longer suggests non-existent domain plugins
- [x] AC-04: No "Plugin not found in marketplace" errors on hook execution
- [x] AC-05: Tests pass after changes
