---
increment: 0437J-add-retry-logic
title: "Add retry logic to sync operations"
---

# Plan

## Approach

Add retry wrapper with exponential backoff to sync HTTP operations. Classify errors as transient (5xx, timeout, rate limit) vs non-transient (4xx auth/not-found) for immediate failure.
