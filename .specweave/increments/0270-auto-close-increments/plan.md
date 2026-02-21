# 0270 — Architecture Plan

## Summary

Three coordinated changes across the SpecWeave plugin system to enable automatic increment closure in unattended execution modes.

## Change 1: stop-auto-v5.sh — Block on All-Complete

**File**: `plugins/specweave/hooks/stop-auto-v5.sh`

**Current behavior** (section 9, lines 188-193):
When all increments are complete (IC=0), the hook calls `loud_approve` which ends the auto session. Claude receives an approve decision and stops working. The increment stays `active`.

**New behavior**:
When all increments are complete, the hook calls `block` with reason code `all_complete_needs_closure` and a systemMessage instructing Claude to run `/sw:done --auto <id>`. This keeps Claude in the auto loop so it can close the increment.

Session state files must NOT be cleaned up on this block -- they should only be cleaned after `/sw:done` succeeds (which the auto skill handles) or when the turn limit is hit.

**Key detail**: After `/sw:done` completes, all tasks remain `[x]` and the metadata status changes to `completed`. On the next stop hook invocation, the hook will see IC=0 again. To prevent an infinite block loop, we need to check if all active increments have `completed` status. If so, do a `loud_approve` to end the session. The existing code already filters out `completed` status increments in the scan loop (line 166), so once `/sw:done` changes status to `completed`, the next hook invocation will find IC=0 with no active increments and the `loud_approve` path fires naturally. No additional loop prevention needed.

## Change 2: /sw:done SKILL.md — Add --auto Flag

**File**: `plugins/specweave/skills/done/SKILL.md`

Add `--auto` to the argument-hint and document it in a new Options section. In Step 4 (Status Validation), add a conditional: if `--auto` flag is present, skip the explicit user confirmation prompt. All other gates (grill, judge-llm, Gate 0, PM gates) remain enforced.

## Change 3: /sw:auto SKILL.md — Closure Step

**File**: `plugins/specweave/skills/auto/SKILL.md`

Add a Step 3.5 (or amend Step 3) that instructs Claude: "When all tasks are complete and quality gates pass, run `/sw:done --auto <id>` for each increment in the session. If /sw:done fails, report the failure. If /sw:done succeeds, clean up session state and output `<!-- auto-complete:DONE -->`."

## Change 4: /sw:team-lead SKILL.md — Auto-Close Step

**File**: `plugins/specweave/skills/team-lead/SKILL.md`

Add an explicit step in Section 8 (Quality Gates > Orchestrator Quality Gate) between step 4 (grill) and step 5 (team-merge): "Run `/sw:done --auto <id>` for each increment in dependency order."

## Change 5: /sw:team-merge SKILL.md — Use --auto Flag

**File**: `plugins/specweave/skills/team-merge/SKILL.md`

Update Step 4 to use `/sw:done --auto <id>` instead of bare `/sw:done <id>`.

## Test Impact

- **stop-auto-v5.test.ts**: The test "should approve when all increments are completed" (line 256) needs to change expectation from `approve` to `block`. A new test should verify the block message contains `/sw:done`.
- **stop-auto-v5.test.ts**: The test "should NOT auto-close increments" (line 712) needs updating -- the hook still does not auto-close, but it now blocks instead of approving.
- All other existing tests remain valid (quick exits, staleness, work remaining, turn counter, dedup).

## Risks

- **Infinite loop risk**: Mitigated by the turn counter safety net and the natural filtering of `completed` status increments.
- **Gate failures in --auto mode**: If grill/judge-llm finds blockers, the increment stays open. The auto session will retry on next turn or hit the turn limit.
