# Plan: Fix vskill.lock in user project folders

## Overview
Add `migrateBundledToGlobalLock(projectRoot)` call at end of `installAllPlugins()`. Add `vskill.lock` to gitignore template.

## Changes
1. `plugin-installer.ts`: Import + call `migrateBundledToGlobalLock` after plugin loop, in try/catch
2. `gitignore-generator.ts`: Add `'vskill.lock'` to `GITIGNORE_ENTRIES.specweave`
