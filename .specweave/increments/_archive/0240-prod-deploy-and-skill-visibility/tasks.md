# Tasks — 0240: Production Deploy & Skill Visibility

### T-001: Deploy current code to production
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given current codebase → When `npm run deploy` runs → Then verified-skill.com/skills shows 89 skills
**Notes**: Removed `export const runtime = "edge"` from SSE stream route (incompatible with OpenNext). Clean build + deploy succeeded. API confirms 89 skills.

### T-002: Add local post-push deploy hook
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given a `git push` on vskill-platform → When push completes → Then `npm run deploy` executes
**Notes**: Created `scripts/push-deploy.sh` — pushes to remote, then builds + deploys to Cloudflare if on main. Added `npm run push-deploy` script. Skips deploy for non-main branches.

### T-003: Verify KV published skills merge
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: Given a skill published via pipeline → When /skills loads → Then published skill appears as VERIFIED
**Notes**: KV namespace is empty (no community submissions yet). Code correctly merges KV published skills with seed data via `getPublishedSkillsList()` + dedup by name. try/catch handles empty KV gracefully. Merge logic verified in data.ts.

### T-004: Verify production after deploy
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given production deploy → When visiting /api/v1/stats → Then totalSkills >= 89
**Notes**: `/api/v1/stats` returns `{"totalSkills":89,"verifiedCount":89,"agentCount":39,"scanCount":89}`. `/api/v1/skills?limit=100` returns 89 skills.
