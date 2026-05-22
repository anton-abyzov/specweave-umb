# 0849 — Sleek Repositories cabinet + dedupe Connect CTA

## Problem

User reported (verbatim): "I cannot understand how it could connect
repositories. You first have a duplicated button to connect your
repository in the web and also in this Mac OS application."

Both the web cabinet (`/account/repos`) and the desktop AccountShell
showed TWO Connect-GitHub buttons (header + empty state) and interleaved
public/private repos in one undifferentiated list. The user wants:

1. ONE clear way to connect a repo per surface.
2. Crisp public-vs-private differentiation everywhere the user looks at
   their connected repos / skills.
3. Clear instructions on how to leverage private-repo skills end-to-end
   (Stripe → connect repo → use in Mac Studio → optionally publish).

## User stories

### US-001 — One canonical Connect CTA per surface

**AC-US1-01** `/account/repos` on the web renders exactly ONE Connect
button (the header CTA). The empty state is informational only.
**AC-US1-02** Desktop AccountShell renders exactly ONE Connect button
(the SummaryChip CTA, always visible). Empty state is informational.
**AC-US1-03** The empty-state copy directs the user to the canonical
CTA above ("Use the Connect GitHub repository button above").

### US-002 — Sectioned Public/Private repos

**AC-US2-01** Connected repos render in two sections: "Private
repositories" (amber-tinted, listed first) and "Public repositories"
(neutral). Each section has a section header with glyph, count, and
one-line subtext.
**AC-US2-02** When a bucket is empty, its section is omitted (not shown
as an empty section).
**AC-US2-03** Within each section, repos are alpha-sorted by full name.
**AC-US2-04** Desktop + web sectioning is visually + structurally
consistent so the two surfaces feel like one product.

### US-003 — Public/Private SkillsSummary tile clarity (shipped in 0848)

Already shipped — kept here as the related context for the visual
language: amber + lock for private, neutral + globe for public, matching
the cabinet sectioning.

## Out of scope

- Server-side schema changes (no DB migration).
- Desktop binary release pipeline (handled by `release-desktop.sh`).
