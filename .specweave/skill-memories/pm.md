# Pm Memory

<!-- Project-specific learnings for this skill -->

## Learnings

- **2026-02-27**: Enable interview process during increment creation for SpecWeave projects (5+ questions minimum, count determined by context)
- **2026-02-27**: Call /sw:grill before completing features/increments to validate quality and fix revealed issues
- **2026-02-27**: Validate spec.md against existing architecture patterns before writing user stories - check for parallel/duplicate systems that indicate overengineering
- **2026-02-27**: Always use EnterPlanMode BEFORE calling /sw:increment to research codebase and present approach for approval. Correct sequence: EnterPlanMode → plan & approve → /sw:increment → /sw:do → /sw:done. Exception: /sw:team-lead (with careful consideration).
- **2026-02-27**: When running /sw:done, execute all steps autonomously without pausing for confirmation - proceed through all gates and syncs in one pass
- **2026-02-27**: Enforce testing at 3 lifecycle stages: Design (BDD plans via /sw:test-aware-planner), Implementation (TDD cycle with mandatory test validation after each task), Closing (full suite + E2E + coverage validation in /sw:done)
