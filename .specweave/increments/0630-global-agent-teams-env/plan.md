# Implementation Plan: Enable agent teams env var in global Claude settings

## Overview

Add `enableAgentTeamsEnvVar(os.homedir())` call alongside the existing project-level call in both `team.ts` and `init.ts`. The function is already idempotent and safe — no new logic needed.

## Files to Modify

| File | Change |
|------|--------|
| `src/cli/commands/team.ts` | Add `import * as os from 'os'`; add `enableAgentTeamsEnvVar(os.homedir())` after line 90 |
| `src/cli/commands/init.ts` | Add `enableAgentTeamsEnvVar(os.homedir())` after line 522 (inside existing try/catch) |
| `tests/unit/cli/commands/team.test.ts` | Add test: function called with both project and homedir |
| `tests/unit/cli/helpers/init/claude-settings-env.test.ts` | Add test: works with simulated home directory |

## Testing Strategy

TDD RED→GREEN: Write failing tests first, then add the 2 implementation lines.
