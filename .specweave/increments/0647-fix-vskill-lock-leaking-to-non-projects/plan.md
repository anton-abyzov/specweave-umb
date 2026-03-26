# Implementation Plan: Fix vskill.lock leaking to non-SpecWeave directories

## Overview

Align `copyPluginSkillsToProject()` with `installPlugin()` by using the global lockfile (`~/.specweave/plugins-lock.json`) instead of the project-level lockfile (`vskill.lock`). Add post-install migration as defense-in-depth.

## Architecture

### Current State (broken)
- `installPlugin()` → `ensureGlobalLockfile()` → `writeGlobalLockfile()` (correct)
- `copyPluginSkillsToProject()` → `ensureLockfile(projectRoot)` → `writeLockfile(lock, projectRoot)` (wrong)

### Target State
- Both paths → `ensureGlobalLockfile()` → `writeGlobalLockfile()` (consistent)
- Both paths use try/catch + in-memory fallback for environments where home is unwritable

## Changes

### 1. plugin-copier.ts (core fix)
- Line 789: `ensureLockfile(projectRoot)` → `ensureGlobalLockfile()` with try/catch
- Line 904: `writeLockfile(lock, projectRoot)` → `writeGlobalLockfile(lock)`

### 2. refresh-plugins.ts (defense-in-depth)
- After install loop (~line 332): add `migrateBundledToGlobalLock(projectRoot)` inside existing `if (isClaude)` block

### 3. Tests
- plugin-copier.test.ts: static code analysis verifying `copyPluginSkillsToProject` uses global lockfile
- plugin-copier-target-dir.test.ts: assert no `vskill.lock` writes, mock global lockfile path

## Cross-Platform
Uses `os.homedir()` (Node.js cross-platform): macOS `$HOME`, Windows `%USERPROFILE%`, fallback to in-memory lock.
