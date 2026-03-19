# Implementation Plan: Fix ADO Per-US Sync Scoping Bug

## Overview

One-line fix: add `featureId` parameter to `findExistingWorkItem()` WIQL query to scope by Feature.

## Files

| File | Change |
|------|--------|
| `plugins/specweave/lib/integrations/ado/per-us-sync.ts` | Add featureId to search query |
| `.specweave/docs/internal/specs/specweave/FS-597/us-*.md` | Remove wrong ado.id values |
