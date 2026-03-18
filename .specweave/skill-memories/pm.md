# Pm Memory

<!-- Project-specific learnings for this skill -->

## Learnings

- **2026-03-18**: Enable interview process during increment creation for SpecWeave projects (5+ questions minimum, count determined by context)
- **2026-03-18**: Call /sw:grill before completing features/increments to validate quality and fix revealed issues
- **2026-03-18**: Validate spec.md against existing architecture patterns before writing user stories - check for parallel/duplicate systems that indicate overengineering
- **2026-03-18**: Always use EnterPlanMode BEFORE calling /sw:increment to research codebase and present approach for approval. Correct sequence: EnterPlanMode → plan & approve → /sw:increment → /sw:do → /sw:done. Exception: /sw:team-lead (with careful consideration).
- **2026-03-18**: When running /sw:done, execute all steps autonomously without pausing for confirmation - proceed through all gates and syncs in one pass
- **2026-03-18**: Enforce testing at 3 lifecycle stages: Design (BDD plans via /sw:increment (via the sw-planner agent)), Implementation (TDD cycle with mandatory test validation after each task), Closing (full suite + E2E + coverage validation in /sw:done)
- **2026-03-18**: When /sw:plan generates task visualizations, use DAG (Dependency Graph) format showing task blocking relationships and parallel lanes rather than flat checklists or grouped lists for critical path visibility
- **2026-03-18**: sw:team-merge does not call TeamDelete — stale team state persists in ~/.claude/teams/ and ~/.claude/tasks/ after merge, blocking creation of new teams in the same session. Must manually call TeamDelete before starting subsequent teams.
- **2026-03-18**: Always invoke /sw:increment for every implementation request—perceived simplicity is not an opt-out. Only explicit user direction overrides this requirement. Hook 'SKILL FIRST: sw:increment' is a blocking precondition.
- **2026-03-18**: When designing skills that require agents to compute derived values (like next increment IDs), expose the deterministic logic as a CLI command instead of expecting agents to parse complex output and manually compute. Prevents LLM miscalculation and collision errors.
