# Spec — 0312-repos-umbrella-badge

## Feature: Repos Page — Umbrella-Managed Badge

**Problem**: Sub-repos in an umbrella project show "No SpecWeave" even though they're managed through the umbrella's `.specweave/`. The "With SpecWeave" KPI undercounts.

**Solution**: Add `isUmbrellaManaged` flag to `RepoInfo`. Show "via umbrella" badge for sub-repos managed through umbrella. Update KPI to include these.

## User Stories

### US-001: Umbrella-managed badge for sub-repos
As a user viewing the Repos page, I want sub-repos in an umbrella project to show a "via umbrella" badge so I can see they're managed by SpecWeave through the umbrella project.

## Acceptance Criteria

- [ ] AC-US1-01: `scanRepositories()` sets `isUmbrellaManaged: true` on repos that lack own `.specweave/` but are under an umbrella project that has one.
- [ ] AC-US1-02: Badge shows "SpecWeave" (green) for own `.specweave/`, "via umbrella" (info/cyan) for umbrella-managed, "No SpecWeave" (gray) otherwise.
- [ ] AC-US1-03: "With SpecWeave" KPI counts repos with either `hasSpecweave === true` or `isUmbrellaManaged === true`.
