# Implementation Plan: Enforce SKILL.md validation for internal/crawler submissions

## Overview

Add a lightweight `skillMdVerified` boolean flag to the enqueue-submissions contract. The endpoint filters out items without the flag. The queue-processor (Hetzner) already validates SKILL.md before enqueue — it just needs to attest this by setting the flag.

## Changes by File

### 1. `src/app/api/v1/internal/enqueue-submissions/route.ts`
- Add `skillMdVerified?: boolean` to `EnqueueItem` interface
- After field validation, filter items where `skillMdVerified !== true`
- Add `skippedNoSkillMd` to response for observability

### 2. `crawl-worker/sources/queue-processor.js`
- Add `skillMdVerified: true` to valid items pushed to `validItems` array (line 213)

## Risk Assessment
- **Low risk**: Additive change — items that already set the flag work; items that don't are filtered
- Queue-processor must be redeployed to Hetzner VMs after this change
- processSubmission still validates as defense-in-depth
