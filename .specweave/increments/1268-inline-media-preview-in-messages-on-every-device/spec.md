# Inline media preview in messages on every device

Linked to 1264, which made the artifact shelf show deliverables and not task logs.

## Problem

Anton's report from November 9, 2026: "Images are not displayed on iPhone Duo, at least, maybe on other phones as well ... in the thread or coordinator, I think I never saw an image displayed, though it's working fine on the desktop application."

The iOS image renderer has been in the source since `b71edc5054` (SpecWithCode 1.0.5, October 12, 2026). Every shipped iOS build should therefore contain it, but nobody has confirmed it renders on a device. The suspects are:

- the native selectable-markdown path's `renderImage` (`apps/mobile/modules/studio-markdown-text`);
- the `filesystem:read` gate in `apps/mobile/src/state/assets.ts:39`;
- asset GETs over the Connect `studio_relay` endpoint, which is not proven (`apps/server/src/cloud/linkChecks.test.ts:57`).

Anton asked for this on November 9, 2026. Coordinators, Aide and workers usually report media as a local path in backticks. On an iPhone, or on any machine other than the thread's host, he sees only a path chip and no picture of the work.

The plumbing already exists. These citations are on `origin/main`:

- **Inline images on both clients.** A Markdown image with an absolute path, `![x](/abs/shot.png)`, already renders inline on web (`apps/web/src/components/ChatMarkdown.tsx:3628`) and on iOS (`apps/mobile/src/features/threads/ThreadFeed.tsx:2403`).
- **How the bytes are fetched.** The image loads from an HMAC-signed `/api/assets` URL that the thread's own server mints (`apps/server/src/assets/AssetAccess.ts:506`). On iPhone it travels over the Connect tunnel, so no raw path is involved.
- **Paths in backticks never become pictures.** A path written in backticks or as a link is only a tappable chip that opens the file viewer.
- **Images are sent at full size.** The server has no resizer, so a 5 MB screenshot downloads whole just to show a thumbnail.
- **The guidance is weak.** It says "Embed images and videos with Markdown and absolute file paths" (`apps/server/src/provider/RuntimeInstructions.ts:239`) but sets no expectation of one representative image. Pi does not receive that line at all.

## Scope

In:

- An agent guidance default: one representative image or video per result, embedded as a Markdown image.
- A fallback on web and iOS: when a message names image or video paths but embeds none, the first one shows as an inline thumbnail that opens the full file.
- A server thumbnail variant of the signed asset URL, downscaled and cached in a capped directory.
- Tests.
- Headless web screenshots.
- An iOS simulator screenshot.

Out:

- Files that live only on a third machine, neither the thread's host nor the viewer's.
- Video poster frames. Video keeps `preload=metadata`.
- Copying media into attachments, so nothing is duplicated.

## Acceptance Criteria

- [ ] AC-01: On an iPhone running the current App Store or TestFlight build (iPhone Duo first), a thread message and a coordinator message each show (a) a Markdown image with an absolute path on the thread's host, (b) an image the agent attached, and (c) an http(s) image. They show inline, through the thread's server or Connect, never as "Image unavailable" or blank. Evidence: a screenshot of each case on the device or the matching simulator build. If any case fails, the root cause is fixed and the screenshot is retaken.
- [ ] AC-02: The runtime guidance asks every role (worker, coordinator, Aide), and Pi too, to embed one representative image or video from its work as `![caption](/absolute/path)` and to list the other files as paths. The existing length test still passes.
- [ ] AC-03: On web, an assistant message that names an image or video path in a chip or link, and embeds no media of its own, shows exactly one inline thumbnail of the first such file. The path chip stays, and tapping the thumbnail opens the full file in the expanded viewer.
- [ ] AC-04: AC-03 also holds on iOS, through the same signed asset URL and over Connect.
- [ ] AC-05: `assets.createUrl` accepts `variant: "thumb"` for image `media-file` resources. The server serves a JPEG or WebP at most 640 px wide, at most 256 KB for a typical screenshot. It caches thumbs under the app's cache directory, keyed by realpath, mtime and size, with a 200 MB LRU cap. Where no resizer is available, it serves the original file.
- [ ] AC-06: Evidence covers before and after for web (headless fixture) and iOS (simulator screenshot). The before shot shows a chip with no picture; the after shot shows the thumbnail with its chip.

## Approach

1. **Guidance.**
   - `apps/server/src/provider/RuntimeInstructions.ts`: change the `runtime_info` media sentence and the presentation block, and update their test.
   - `apps/server/src/provider/piStudioMcpExtensionSource.ts`: add the same line for Pi.
2. **Thumb variant.**
   - `packages/contracts/src/assets.ts`: add `variant` to the input and the claims.
   - `apps/server/src/assets/AssetAccess.ts`: sign the variant into the token and serve the thumb through a new `apps/server/src/assets/AssetThumbnails.ts`.
   - The resizer is macOS `sips`, falling back to the original file elsewhere. There is no new native dependency; that is D-01.
3. **Shared pick.** `packages/client-runtime/src/markdownImages.ts` gets `firstUnembeddedMedia(markdown)`. It returns the first image or video path from chips or links, and returns null when the message already has a Markdown image.
4. **Web.** `ChatMarkdown.tsx` renders `ChatMarkdownAssetImage` with `variant: "thumb"` below the message body when the pick returns a path. A tap opens `openMarkdownMedia` with the full file.
5. **iOS.** `ThreadFeed.tsx` and `ThreadMarkdownImage.tsx` do the same.

Rejected:

- Copying media into attachments, which costs storage.
- Adding `sharp`, a native dependency that would sit in every platform build.
- A thumbnail for every path in a message, which would clutter the thread.

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01: The resizer is `sips` on macOS only. Linux and Windows hosts serve the original file until a portable resizer is chosen.
- D-02: A message gets one fallback thumbnail at most. Media the agent embeds itself always wins over the fallback.
- D-03: The thumbnail cap is 640 px and the cache cap is 200 MB.

### Open
- none

## Tasks

### T-00 Reproduce and fix image rendering on the shipped iOS build
- AC: AC-01 | Files: apps/mobile/src/features/threads/ThreadFeed.tsx, apps/mobile/src/features/threads/ThreadMarkdownImage.tsx, apps/mobile/modules/studio-markdown-text/src/NativeMarkdownBlock.tsx, apps/mobile/src/state/assets.ts | Test: simulator and device screenshots of the three cases, under the increment's reports/

### T-01 Guidance: one representative image by default
- AC: AC-02 | Files: apps/server/src/provider/RuntimeInstructions.ts, apps/server/src/provider/RuntimeInstructions.test.ts, apps/server/src/provider/piStudioMcpExtensionSource.ts | Test: npx vitest run apps/server/src/provider/RuntimeInstructions.test.ts

### T-02 Thumbnail variant of signed asset URLs
- AC: AC-05 | Files: packages/contracts/src/assets.ts, apps/server/src/assets/AssetAccess.ts, apps/server/src/assets/AssetThumbnails.ts, apps/server/src/assets/AssetThumbnails.test.ts | Test: npx vitest run apps/server/src/assets

### T-03 Web fallback thumbnail
- AC: AC-03 | Files: packages/client-runtime/src/markdownImages.ts, packages/client-runtime/src/markdownImages.test.ts, apps/web/src/components/ChatMarkdown.tsx | Test: npx vitest run packages/client-runtime/src/markdownImages.test.ts apps/web/src/components/ChatMarkdown

### T-04 iOS fallback thumbnail
- AC: AC-04 | Files: apps/mobile/src/features/threads/ThreadFeed.tsx, apps/mobile/src/features/threads/ThreadMarkdownImage.tsx | Test: npx vitest run apps/mobile/src/features/threads

### T-05 Before and after evidence
- AC: AC-06 | Files: apps/web/tests/inline-media/ | Test: node apps/web/tests/inline-media/verify.mjs
