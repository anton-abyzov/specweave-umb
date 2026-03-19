---
increment: 0600-docs-deployment-alignment
---

# Tasks

### T-001: Fix umbrella CLAUDE.md domain reference
**User Story**: US-001 | **AC**: AC-US1-01 | **Status**: [x] completed

**Test Plan**:
- Given the umbrella CLAUDE.md
- When reading the docs URL reference
- Then it shows `spec-weave.com` not `verified-skill.com`

---

### T-002: Replace verified-skill.com/docs/ URLs in living docs
**User Story**: US-001 | **AC**: AC-US1-02, AC-US1-03 | **Status**: [x] completed

**Test Plan**:
- Given all files in `.specweave/docs/public/`
- When searching for `verified-skill.com/docs/`
- Then zero matches are found
- And `verified-skill.com` references without `/docs/` path are unchanged

---

### T-003: Investigate and fix homepage config error
**User Story**: US-002 | **AC**: AC-US2-01 | **Status**: [x] completed

**Test Plan**:
- Given the docs-site Docusaurus config
- When building and serving locally
- Then the homepage renders without config error banners

---

### T-004: Add URL redirects
**User Story**: US-002 | **AC**: AC-US2-02, AC-US2-03 | **Status**: [x] completed

**Test Plan**:
- Given the redirect configuration in docusaurus.config.ts
- When navigating to `/docs/academy/videos/005-opencode-web-calculator`
- Then it redirects to `/docs/academy/videos/opencode-web-calculator`
- And `/docs/guides/getting-started/quickstart` redirects to `/docs/getting-started`

---

### T-005: Audit sidebar and build
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-02 | **Status**: [x] completed

**Test Plan**:
- Given all sidebar entries in sidebars.ts
- When running `npm run build`
- Then build completes without broken link errors
- And all sidebar doc IDs resolve to actual files

---

### T-006: Push to deploy
**User Story**: US-003 | **AC**: AC-US3-03 | **Status**: [x] completed

**Test Plan**:
- Given all fixes are committed
- When pushing to the develop branch
- Then GitHub Actions deploy-docs workflow triggers
