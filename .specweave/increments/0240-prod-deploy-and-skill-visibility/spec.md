# 0240: Production Deploy & Skill Visibility

## Problem

Production site (verified-skill.com/skills) shows only **15 skills**, but seed-data.ts contains **89 skills**. Deployment is manual — no auto-deploy on push.

## User Stories

### US-001: All seed skills visible on production
As a visitor, I should see all 89 seed skills on /skills.

**Acceptance Criteria:**
- [ ] AC-US1-01: Production shows 89+ skills on /skills page
- [ ] AC-US1-02: Homepage shows correct total count
- [ ] AC-US1-03: All vendors represented (Anthropic 16, OpenAI 32, Google 20, Community 21)

### US-002: Submitted skills appear in registry
As a submitter, PUBLISHED skills should appear on /skills.

**Acceptance Criteria:**
- [ ] AC-US2-01: KV published skills appear in /skills listing
- [ ] AC-US2-02: KV published skills show as VERIFIED tier

### US-003: Auto-deploy on push
As a developer, pushing to main should deploy to Cloudflare automatically.

**Acceptance Criteria:**
- [ ] AC-US3-01: Local post-push git hook runs `npm run deploy` for vskill-platform
- [ ] AC-US3-02: Deploy goes directly to Cloudflare Workers (no CI cost)

## Root Cause

- No auto-deploy — `npm run deploy` is manual
- Production runs a stale build with 15 skills (original seed data)
- Code is pushed to `origin/main` but never deployed

## Approach

Use a **local git post-push hook** instead of GitHub Actions:
- Zero CI cost (deploys directly from local to Cloudflare via `wrangler deploy`)
- Runs automatically after every `git push` on the vskill-platform repo
- Cloudflare Workers free tier: 100k req/day (plenty)
- GitHub Actions is free for public repos but adds unnecessary complexity
