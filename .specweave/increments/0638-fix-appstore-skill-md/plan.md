# Plan: Fix appstore skill security scan false positives

## Overview

Targeted bug fix in two files: narrow CT-004 regex in scanner patterns, remove nested fencing in appstore SKILL.md.

## Files to Modify

| File | Change |
|------|--------|
| `repositories/anton-abyzov/vskill/src/scanner/patterns.ts` | Narrow CT-004 pattern, add CT-004 to DOCUMENTATION_SAFE_PATTERNS |
| `repositories/anton-abyzov/vskill/plugins/mobile/skills/appstore/SKILL.md` | Remove nested ```markdown wrapper around installation instructions |
| `repositories/anton-abyzov/vskill/src/scanner/patterns.test.ts` | Add CT-004 positive/negative match tests |
| `repositories/anton-abyzov/vskill/src/scanner/tier1.test.ts` | Add CT-004 documentation-safe downgrade test |

## Risks

- Narrowing CT-004 too aggressively could miss real keychain access → mitigated by testing specific API/CLI patterns
