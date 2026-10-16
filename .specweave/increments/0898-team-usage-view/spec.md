# 0898 Team usage view

## Problem

0897 (free-first pricing, approved by Anton 2026-10-12) keeps SpecWithCode free and makes companies pay for hosting, control and support. The strongest reason for a company to pay beyond hosted skills is a question no single developer's app answers: across all our engineers, which Claude, Codex and Cursor seats sit idle, which hit their limits every day, and where did work hand off because of it. Today each SpecWithCode machine knows only its own accounts' usage, and the Switch fleet view (specweave PR #2034) shows one person's Macs over SSH tunnels, not a team.

## Scope

In: an opt-in team view that aggregates per-account usage summaries from members' SpecWithCode machines: remaining 5-hour and weekly windows, limit hits per day, idle days per seat, handoffs and provider switches caused by limits; a team admin page; export as CSV; the privacy boundary below, enforced in code and stated in the UI.
Out: prompts, code, file names, thread titles or any content leaving a machine; billing or seat purchasing; SSO (0842); changing how a single machine reads usage (reuse what SpecWithCode and Switch already read).

## Acceptance Criteria

- [ ] AC-01: A member opts in per machine; nothing is sent before opt-in, and opting out stops sending and deletes that machine's history from the team view.
- [ ] AC-02: Each summary carries only: provider, account label chosen by the member, plan tier if known, window remaining, reset times, limit-hit count, handoff and provider-switch counts, machine label, timestamp. A test fails if any other field is sent.
- [ ] AC-03: The admin page lists every seat with last-30-day idle days, limit hits per day and handoffs caused by limits, sortable, with "idle 14+ days" and "hits a limit most days" filters, and exports CSV.
- [ ] AC-04: Summaries reach the team over the hosted relay (off by default) or a self-hosted endpoint; both authenticate the machine with its pairing, and transport is TLS only.
- [ ] AC-05: The view is part of the Team and Enterprise offer on /pricing only once AC-01..AC-04 pass; until then the pricing page does not mention it.

## Approach

Reuse the quota shape SpecWithCode already reads per account and the Claude `get_usage` reader from Switch (PR #2034). Each machine computes a daily summary locally and posts it; the server stores summaries only. Start with one team per Verified Skill tenant so seats and billing (0840/0841) carry over.

## Open questions

- Hosted on verified-skill.com (tenant model exists) or a SpecWithCode service? Recommended: verified-skill.com tenants.
- Include Cursor seats before a Cursor usage reader exists? Recommended: show Cursor as "usage not readable yet".

## Tasks

### T-01 Local daily usage summary with the field allowlist
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specweave-studio | Test: summary allowlist unit test

### T-02 Team endpoint storing summaries per tenant
- AC: AC-04 | Files: repositories/anton-abyzov/vskill-platform | Test: endpoint auth and schema tests

### T-03 Admin page and CSV export
- AC: AC-03 | Files: repositories/anton-abyzov/vskill-platform | Test: page renders filters and CSV from fixture data

### T-04 Pricing page mention after acceptance
- AC: AC-05 | Files: repositories/anton-abyzov/specweave/docs-site/src/pages/pricing.tsx | Test: cd repositories/anton-abyzov/specweave/docs-site && npm run build
