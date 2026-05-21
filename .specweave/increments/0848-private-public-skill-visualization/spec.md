# 0848 — Smart Public/Private Skill Visualization

## Problem

Users connect public AND private GitHub repos. In Skill Studio (desktop) and the web cabinet, skills from both repo types render with no clear visual separation. The 0826 PrivateBadge exists for org-level views, but inside the main Sidebar, MarketplaceDrawer, and account list, private-repo skills look identical to public-repo ones.

## User stories

### US-001 — As a Skill Studio user, I can tell at a glance which sidebar rows came from private repos

**AC-US1-01** Every SkillRow in the Sidebar AVAILABLE/AUTHORING sections renders a small amber lock chip when the skill's source repo is private.
**AC-US1-02** Public-repo and unknown-source skills render with no privacy chip (current behavior).
**AC-US1-03** The chip has `data-testid="skill-row-private-chip"` and `aria-label` that mentions "private repo" for screen readers.
**AC-US1-04** Hovering the chip shows a tooltip "From private repo: owner/name".

### US-002 — Within a Sidebar section, private and public skills are visually grouped

**AC-US2-01** When AVAILABLE > Project contains a mix of private and public skills, sub-headers "🔒 Private repos (N)" and "🌐 Public repos (N)" partition the rows.
**AC-US2-02** When a section contains only one visibility class, no sub-header is shown.
**AC-US2-03** Sub-headers are collapsible and remember state in localStorage scoped to `vskill-sidebar-{agent}-section-{name}-private-collapsed`.

### US-003 — Account skills tab tiles emphasize the private/public split

**AC-US3-01** /account/skills tiles use distinct amber tint on the Private side and a neutral surface on the Public side.
**AC-US3-02** Each tile shows a lock or globe icon next to its label.

### US-004 — Public surfaces hint that private skills exist

**AC-US4-01** /skills (public catalog) shows a one-line banner "You have N private skills →" for signed-in users with private skills.
**AC-US4-02** /publishers/[name] shows a footer "+ N private skills not listed publicly" when the viewer is the publisher and has private skills.

### US-005 — MarketplaceDrawer separates user-private plugins from public marketplace

**AC-US5-01** When the user has private-repo plugins, they render in a top "Your private plugins" section with amber tint above the public marketplaces.

## Out of scope

- Server-side schema changes (no DB migration).
- New API endpoints — all data comes from existing `repoUrl` field + connected-repos API.
