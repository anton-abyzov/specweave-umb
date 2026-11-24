# Replace brain, lock and thinking icons with crafted glyphs

## Problem

The app still shows stock brain and lock icons: the brain beside reasoning effort and on "Thinking" rows, and the padlock beside access modes ("Full access"), secret requests and private repositories. The user wants them gone everywhere and replaced with high-quality crafted images. The "Working for 3s / [brain] Thinking" row in the user's screenshot must not appear anywhere: web, desktop, Expo mobile, native iOS or marketing.

## Scope

In: every brain, brain-circuit, lock, lock-open and lock-keyhole icon, the SF Symbols "brain" and "lock", and the 🧠 and 🔒 emoji in apps/web, apps/desktop, apps/mobile, apps/ios and apps/marketing. Thinking and reasoning rows, the access-mode picker and chip, the secret request card, the private repository card, and project icon options. A source-scan test that keeps them out.

Out: provider logos (kept), copy changes beyond the labels next to replaced icons, and SpecWeave docs-site.

## Acceptance Criteria

- [ ] AC-01: No thinking or reasoning row shows a brain. The row shows the provider or model mark, muted, pulsing gently while streaming (reduced motion: no pulse), with "Thinking" / "Thought for Ns" text.
- [ ] AC-02: The effort picker never falls back to BrainIcon; a model without effort levels shows the 0-bar EffortGlyph or nothing.
- [ ] AC-03: Access modes use a crafted AccessGlyph in the EffortGlyph style (16px SVG, currentColor): a four-step circular gauge, Supervised 1/4, Auto-accept edits 2/4, Auto 3/4, Full access full. Used in the composer chip, the picker menu and settings.
- [ ] AC-04: The secret request card uses a crafted "masked field" glyph (a field outline with dots); the private repository card shows the host logo plus a "Private" text badge.
- [ ] AC-05: brain and brain-circuit are removed from project icon options; saved projects using them are remapped to a crafted equivalent on read, without a migration that rewrites user data.
- [ ] AC-06: Native iOS TranscriptRowView and ProjectAvatar, and the Expo app (AppSymbol IconBrain, thread-work-log, thread-context-divider, SecretRequestCard, threadActivity "lock"), have the same replacements.
- [ ] AC-07: A unit test scans the five app source trees and fails on BrainIcon, BrainCircuit, LockIcon, LockOpenIcon, LockKeyhole, IconBrain, IconLock, SF Symbol "brain" or "lock", and the 🧠 or 🔒 emoji.
- [ ] AC-08: Headless light and dark screenshots of the composer, access picker, a thinking row, a secret card and a private repo card; an iOS simulator screenshot of a thinking row.

## Approach

Draw new glyphs as small SVG components next to apps/web/src/components/chat/EffortGlyph.tsx (same grid, stroke and currentColor), so they read as one family. Thinking rows reuse the existing provider mark component. Known locations on origin/main fc20d56fa2: TraitsPicker.tsx lines 824 and 849; MessagesTimeline.tsx lines 4202, 4476, 5537, 5736, 5787; runtimeModeConfig.ts Lock/LockOpen; ChatComposer.tsx line 6969 (Shield, keep unless it reads as a lock); GitActionsControl.tsx line 870; SecretRequestCard.tsx; projectIconOptions.ts lines 61 and 228; apps/mobile AppSymbol.tsx, thread-work-log.tsx line 1402, ThreadFeed.tsx line 1580, threadActivity.ts lines 239 and 579; apps/ios TranscriptRowView.swift lines 83 to 99, ProjectAvatar.swift lines 127 and 134. Re-scan with git grep; the list may be incomplete.

## Decisions

### Asked

- None; the user asked for removal everywhere and high-quality images.

### Defaulted

- D-01: Thinking rows use the provider mark rather than a new "thought" symbol, so the row says who is thinking.
- D-02: The access gauge is the same glyph in every mode, filling up, so the risk level reads at a glance without a lock metaphor.
- D-03: Saved brain project icons are remapped on read, not rewritten, so user data is untouched.
- D-04: Native iOS has no provider marks and its transcript rows carry no provider, so its thinking row uses the crafted dots (the web fallback) and pulses them while streaming. Drawing provider logos on iOS is a follow-up. Expo's thinking row already shimmers across the mark while streaming and stops under Reduce Motion; that sweep stands in for a separate pulse. Delivered October 26, 2026 by PR #745 (eb090035eb, 1.0.90): iOS thread chats show the muted provider mark, breathing while streaming; coordinator chats keep the dots. Installed receipt: ~/.specwithcode/m4/evidence/0965-745-installed-1090/RECEIPT.md
- D-05: AC-01's row text stays the existing "Thinking" / "Thought". A "Thought for Ns" duration needs a completion time on reasoning entries, which web, Expo and iOS rows don't carry today; that is new data and behavior outside this icon-swap lane, so it is a follow-up. (Found by the fresh-context review of the merged diff, October 20, 2026.) Delivered October 26, 2026 by PR #745 (1.0.90): settled rows read "Thought for Ns" from the item\'s startedAt/completedAt on web, Expo and iOS; unmeasured items keep "Thought". A collapsed row with reasoning text still previews the text.

## Tasks

### T-01 Crafted glyph set
- AC: AC-03, AC-04 | Files: apps/web/src/components/chat/AccessGlyph.tsx, MaskedFieldGlyph.tsx | Test: tests for glyph steps per mode

### T-02 Web and desktop replacements
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: TraitsPicker.tsx, MessagesTimeline.tsx, runtimeModeConfig.ts, GitActionsControl.tsx, SecretRequestCard.tsx, projectIconOptions.ts | Test: component tests

### T-03 Expo mobile replacements
- AC: AC-06 | Files: apps/mobile AppSymbol.tsx, thread-work-log.tsx, thread-context-divider, SecretRequestCard, threadActivity.ts | Test: unit tests

### T-04 Native iOS replacements
- AC: AC-06 | Files: TranscriptRowView.swift, ProjectAvatar.swift | Test: swift test, simulator screenshot

### T-05 Source-scan guard
- AC: AC-07 | Files: apps/web test for banned icons across app trees | Test: the guard itself, plus a seeded failure

### T-06 Visual evidence
- AC: AC-08 | Files: screenshots under the lane's scratch folder | Test: headless Playwright light and dark

### T-07 Verify and close 0965
- AC: all | Files: none | Test: specweave verify, fresh-context review, specweave complete
