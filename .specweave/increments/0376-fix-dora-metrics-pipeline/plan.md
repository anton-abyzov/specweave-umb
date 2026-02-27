# Implementation Plan: Fix DORA metrics pipeline

## Overview

Three targeted fixes: (1) CFR boundary bug in tier-classifier.ts, (2) doc/code threshold alignment in metrics.md, (3) stale goals update.

## Changes by File

### 1. `src/metrics/utils/tier-classifier.ts` -- Fix CFR boundaries
- Change `< 15` to `<= 15`, `< 30` to `<= 30`, `< 45` to `<= 45`
- This aligns with the documented "0-15%", "15-30%", "30-45%" ranges

### 2. `.specweave/docs/public/metrics.md` -- Fix doc inconsistencies
- Lead Time High: "1 day to 1 week" to "1 hour to 1 week"
- CFR High: "16-30%" to "15-30%"
- CFR Medium: "31-45%" to "30-45%"
- Update goals to reflect current performance

## Risk Assessment
- **Low risk**: Threshold changes only affect exact boundary values (15, 30, 45)
- CFR=0% currently, so no production impact on current tier classification
