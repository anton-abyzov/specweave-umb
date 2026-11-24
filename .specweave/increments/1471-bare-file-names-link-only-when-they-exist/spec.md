# Bare file names in chat link only when the file exists

## Problem

A chat reply that writes a bare file name in inline code (`llms.txt`, `README.md`, `app.ts:12`) shows it as a file chip before anyone checks the file exists. When it does not exist, clicking the chip shows the toast "llms.txt was not found. Looked in: /Users/anton/Projects/github/specweave-umb/llms.txt". Seen on M5 on November 24, 2026 in the project coordinator: the reply meant the web convention `llms.txt`, a file nobody had made.

Cause: `settleInlineCodeFileLink` (`apps/web/src/markdown-links.ts`) gives a bare name a workspace search, `useExistingFileLinks` marks it `unresolved` when nothing is found, and `MarkdownCode` in `ChatMarkdown.tsx` renders a chip for any meta, settled or not. The inline fallback `resolveInlineCodeFileLinkMeta` in `MarkdownCode` never asks the host at all.

## Scope

In: inline code that names a bare file (no `/` or `\` in what was written, optionally with `:line`), and a bare `:12` that follows one. Out: paths with a `/`, `~/` or drive letter (they keep their chip and the not-found notice, since they name a place), authored Markdown links, fenced path lists (they already mark missing files), the threads' Files list (already drops files the host lacks).

## Acceptance Criteria

- [ ] AC-01: A bare file name in inline code that the thread's machine does not have renders as plain code, not a chip; clicking it shows no toast.
- [ ] AC-02: A bare file name the host has (in the workspace root, a folder the message names, or found uniquely by search) still renders as a chip that opens the file, with `file:line` keeping its line.
- [ ] AC-03: Until the host answers, a bare name renders as plain code; a name already confirmed on that machine renders as a chip on the next mount without a code-to-chip flash; a name that was missing is checked again, so a file created later starts linking.
- [ ] AC-04: Paths containing `/` keep today's behaviour, including the not-found notice for a missing one.
- [ ] AC-05: A remote thread checks the name on its own machine (the thread's environment), never on the viewer's.

## Approach

1. `markdown-links.ts`: mark a bare-name meta with `requiresHost: true` in `settleInlineCodeFileLink`, carry it onto a following `:12` span, and export `confirmedFileLink(meta)` that returns null for a `requiresHost` meta the host has not found. Export `isBareFileNameSpan` for the inline fallback.
2. `useExistingFileLinks.ts`: host-check every `requiresHost` meta; keep a module cache per environment and link of settled results, seed from it on mount, and re-check entries that were missing. A found file drops `requiresHost` through `fileLinkMetaAtPath`.
3. `ChatMarkdown.tsx`: filter the settled inline map through `confirmedFileLink` before `viewerLinks` and `MarkdownCode` read it; the inline fallback skips bare names.
4. Tests: render `ChatMarkdown` with the host listing mocked (`ChatMarkdown.bare-names.test.tsx`); pure tests in `markdown-links` for the flag.

Rejected: linkify only paths with a `/`. It would break the `README.md` and `CoordinatorConversation.tsx` chips that already resolve correctly through the host.

Remote threads already resolve on their own machine: `environmentId` comes from `threadRef.environmentId`, and `projectEnvironment.listEntries` runs there. With no environment the bare name stays code.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Unconfirmed bare names render as plain code while the host answers → default (reversible), the cache hides the delay on later mounts.
- D-02 A bare `name.ts:12` follows the same rule as `name.ts` → default.
### Open
- none

## Review

Adversarial review on Gemini 4 Neon, else GPT-6.2 Sol, never Grok.

## Tasks

### T-01 Bare names link only once the host confirms them
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/markdown-links.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/useExistingFileLinks.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/ChatMarkdown.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/ChatMarkdown.bare-names.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/markdown-links.bare-names.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run --passWithNoTests --project unit src/components/ChatMarkdown src/markdown-links src/components/chat/useExistingFileLinks src/threadArtifacts

### T-02 PR, adversarial review, merge and release request
- AC: AC-01 | Files: .specweave/increments/1471-bare-file-names-link-only-when-they-exist/reports/ | Test: PR checks green, review findings answered, request-release.sh run
