# 0282: Repository Links on All Skill Surfaces

## Problem

Repository links (to the source GitHub repo) are only shown on a few skill surfaces (skill detail page, security report, admin submission detail). Other surfaces like the skills listing, trust center verified tab, blocked tab, homepage trending, and search palette lack repository links. Users need quick access to source repositories from any surface where skills are listed.

## User Stories

### US-001: As a user, I want to see a GitHub repo link on every skill listing surface so I can quickly navigate to the source code.

**Acceptance Criteria:**
- [x] AC-US1-01: Skills listing page (`/skills`) shows a repo link icon for each skill
- [x] AC-US1-02: Trust Center Verified Skills tab table includes a Repo column with clickable links
- [x] AC-US1-03: Trust Center Blocked Skills tab shows sourceUrl as a clickable repo link
- [x] AC-US1-04: Homepage trending section shows a small repo link for each skill
- [x] AC-US1-05: Search palette results include a subtle repo indicator

### US-002: As a user, I want repo links to be unobtrusive and consistent with the existing design language.

**Acceptance Criteria:**
- [x] AC-US2-01: Repo links use the same monospace font and teal accent color as existing repo links
- [x] AC-US2-02: Repo links open in a new tab with noopener noreferrer
- [x] AC-US2-03: Repo links show abbreviated format (owner/repo, stripping github.com prefix)
- [x] AC-US2-04: Repo links use click event stopPropagation where the row itself is a link/button

## Scope

- IN: Add repo links to skills listing, trust center tabs, homepage trending, search palette
- OUT: API changes (repoUrl already included in skill data), schema changes, new components
