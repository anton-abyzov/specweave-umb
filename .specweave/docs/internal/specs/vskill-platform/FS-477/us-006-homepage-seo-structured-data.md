---
id: US-006
feature: FS-477
title: "Homepage SEO Structured Data"
status: completed
priority: P1
created: 2026-03-10T00:00:00.000Z
tldr: "**As a** search engine crawler."
project: vskill-platform
---

# US-006: Homepage SEO Structured Data

**Feature**: [FS-477](./FEATURE.md)

**As a** search engine crawler
**I want** JSON-LD SearchAction structured data on the homepage
**So that** the site can appear with a sitelinks search box in search results

---

## Acceptance Criteria

- [x] **AC-US6-01**: Given the homepage HTML, when inspecting the head, then a `<script type="application/ld+json">` tag contains a WebSite schema with `potentialAction` of type `SearchAction` pointing to `/skills?q={search_term_string}`
- [x] **AC-US6-02**: Given the JSON-LD, when validated, then it conforms to schema.org WebSite + SearchAction specification

---

## Implementation

**Increment**: [0477-homepage-studio-nav-redesign](../../../../../increments/0477-homepage-studio-nav-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
