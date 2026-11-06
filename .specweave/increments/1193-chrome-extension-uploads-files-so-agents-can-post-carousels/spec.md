# Chrome extension uploads files so agents can post carousels

## Problem

The user asked that the Chrome extension support "Meta News" and suspected a missed carousel. An audit on November 3, 2026 found no site restriction: `chrome_*` already reads and clicks on Instagram, Facebook and Threads, and Muse threads already get the tools. The gap is uploads. `chrome_*` has no way to give a page a file, so an agent cannot attach an image to any post, and a multi-image carousel is impossible. `preview_upload` exists only for the app's own preview browser.

## Scope

In: a `chrome_upload` tool for one or many files, extension 1.0.5 whose store text and privacy policy disclose uploads, and the upload kit. Out: pages that open a picker with no `input[type=file]` in the DOM, uploads to Chrome on another machine, and publishing anything to a social account.

## Acceptance Criteria

- [x] AC-01: `chrome_upload` with absolute paths sets those files, in order, on the page's file input, by ref, by selector or by finding the page's only upload input, and fires input and change events.
- [x] AC-02: Several files on a single-file input, a missing path, a directory, more than 20 files, more than 100 MiB in total and a page with no file input each fail with a clear error, before the page gets anything.
- [x] AC-03: `chrome_upload` refuses Chrome on another machine, both from the calling side and through `chrome_peer`, so another machine can never read local files here.
- [x] AC-04: Extension version 1.0.5 builds, and its summary, store description and privacy policy disclose attached files, and the store metadata names no AI products (the privacy policy may, per the October 16, 2026 review).
- [x] AC-05: A three-image carousel reaches the Instagram composer's slide preview with nothing posted. Evidence: the same in-page method was run live on November 3, 2026.

## Approach

`pageScripts.ts` gets the upload scripts and `chromeTools.ts` reads the files and streams them as base64 chunks through `Runtime.evaluate`, then builds `File` objects and a `DataTransfer` in the page. `DOM.setFileInputFiles` is rejected: Chrome allows it for an extension only when the user turns on "Allow access to file URLs". No extension code or permission changes, so 1.0.5 carries only the disclosure.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 "Meta News" reads as Facebook, Instagram and Threads, per the coordinator's note. It may be dictation for Meta's Muse; Muse threads already get `chrome_*`, verified November 2, 2026, so nothing is lost either way (reversible).
- D-02 Paths follow `preview_upload`: any absolute path on this machine (reversible).
### Open
- none

## Tasks

### T-01 chrome_upload tool
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/browserExtension.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/browserExtension/pageScripts.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/browserExtension/chromeTools.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/browserExtension/chromeTools.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/mcp/toolkits/chrome/tools.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/mcp/toolkits/chrome/handlers.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/mcp/toolkits/chrome/handlers.test.ts, repositories/anton-abyzov/specwithcode-dev/packages/shared/src/studioMcpToolPresentation.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/provider/StudioOrchestrationInstructions.ts | Test: cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode-dev/worktrees/chrome-pair-first/apps/server && pnpm exec vp test run src/browserExtension src/mcp/toolkits/chrome

### T-02 Extension 1.0.5 and store text
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/apps/chrome-extension/manifest.json, repositories/anton-abyzov/specwithcode-dev/apps/chrome-extension/package.json, repositories/anton-abyzov/specwithcode-dev/apps/chrome-extension/store/SUBMISSION.md, repositories/anton-abyzov/specwithcode-dev/apps/chrome-extension/store/privacy-policy.md, repositories/anton-abyzov/specwithcode-dev/apps/server/src/browserExtension/extensionVersion.generated.ts | Test: cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode-dev/worktrees/chrome-pair-first && node apps/chrome-extension/scripts/build.mjs --check

### T-03 Live carousel proof
- AC: AC-05 | Files: none | Test: manual, Instagram composer shows three slides and nothing is posted

### T-04 Verify and close 1193
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: none | Test: specweave verify 1193
