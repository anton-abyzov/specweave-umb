# Tasks — 0240: Production Deploy & Skill Visibility

### T-001: Deploy current code to production
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [ ] pending
**Test**: Given current codebase → When `npm run deploy` runs → Then verified-skill.com/skills shows 89 skills

### T-002: Add local post-push deploy hook
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [ ] pending
**Test**: Given a `git push` on vskill-platform → When push completes → Then `npm run deploy` executes

Create `repositories/anton-abyzov/vskill-platform/.git/hooks/post-push` (or a wrapper script):
- Detect if pushed branch is main
- Run `npm run deploy` (which calls `npx @opennextjs/cloudflare deploy`)
- Note: git has no native `post-push` hook — use a shell alias or wrapper script instead

Alternative: simple deploy script `scripts/push-deploy.sh`:
```sh
git push "$@" && npm run deploy
```

### T-003: Verify KV published skills merge
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [ ] pending
**Test**: Given a skill published via pipeline → When /skills loads → Then published skill appears as VERIFIED

### T-004: Verify production after deploy
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] pending
**Test**: Given production deploy → When visiting /api/v1/stats → Then totalSkills >= 89
