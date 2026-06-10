# Tasks: Desktop verified-skill repository link

### T-001: Add verified-skill URL support to RepoLink
**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-04
**Status**: [x] completed

**Test Plan** (BDD):
- Given `RepoLink` receives `repoUrl=https://github.com/anton-abyzov/vskill` and
  `skillName=remotion-best-practices` -> When it renders -> Then the anchor href
  is `https://verified-skill.com/skills/anton-abyzov/vskill/remotion-best-practices`.
- Given `RepoLink` receives a null, empty, malformed, or non-GitHub URL -> When it
  renders -> Then it returns null.
- Given `RepoLink` is called without `skillName` -> When it renders -> Then it
  preserves the existing GitHub repo-root href for backward compatibility.

### T-002: Wire DetailHeader to pass the skill slug
**User Story**: US-001
**Satisfies ACs**: AC-US1-02, AC-US1-03
**Status**: [x] completed

**Test Plan** (BDD):
- Given `DetailHeader` renders a skill with `repoUrl`, `skill`, and `skillPath`
  -> When the byline is inspected -> Then `repo-link` points to verified-skill.com.
- Given the same skill -> When `source-file-link` is inspected -> Then it still
  points to the GitHub `blob/HEAD/{skillPath}` URL.

### T-003: Focused verification
**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] completed

**Test Plan** (BDD):
- Given the focused eval-ui component tests -> When Vitest runs -> Then all
  modified repo-link and detail-header tests pass.
