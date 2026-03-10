# Architect Memory

<!-- Project-specific learnings for this skill -->

## Learnings

- **2026-03-10**: When designing new adapter systems, first audit existing adapter patterns in codebase - reuse existing ProviderAdapter interfaces and infrastructure rather than creating parallel systems
- **2026-03-10**: When proposing schema changes, use ASCII table format (showing columns, types, relationships) rather than Prisma model code or prose descriptions for clearest comparison of alternatives
- **2026-03-10**: Source file editing (configs, evals.json, test definitions) should happen locally via CLI + git workflow, not through web UIs. Reserve web interfaces for read-only dashboards (results, trends), remote execution triggers, and aggregated analytics. Local workflows enable immediate testing, use of preferred editors, and proper git commit semantics for audit trails.
