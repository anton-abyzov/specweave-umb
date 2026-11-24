# Open linked HTML and text artifacts on phones

Related: 1268 (inline media preview; shares the `assets.createUrl` media-file path), 1273 (iPhone Artifacts in the side menu; can reuse this viewer).

## Problem

Anton, November 10, 2026: "Why are those artifact files not possible to open on iPhones or phones in general? I believe we should be able to read it. It's just like the Markdown files, right? Make sure to implement it."

Agents deliver results as files on the thread's host, for example `/Users/antonabyzov/Movies/livestreams/2026-11-10/cue-sheet.html`, linked as `[cue-sheet.html](/abs/path.html)` or written as a path in backticks. The desktop app opens these as file chips. The iPhone app cannot open them, so the workaround was publishing the page to Cloudflare Pages.

Cause: the shipped iPhone app is the native SwiftUI app in `apps/ios`. Its Markdown renderer (`apps/ios/SWCKit/Sources/Weave/Markdown/MarkdownText.swift`, `MarkdownInline.parse` and the `openURL` action) removes every link whose scheme is not `http`, `https`, `mailto` or `tel` and is not a `studio://thread` link, and the app has no file viewer. A linked host path renders as plain text and a backticked path as inline code, so the phone never asks the host for the file.

Two server gaps block a viewer even once the link is tappable:

- `assets.createUrl` for a `media-file` serves only media, audio, HTML and PDF (`hostPreviewMimeTypeFromExtension`); `.md`, `.txt` and `.json` are refused.
- HTML served from a `media-file` URL cannot load the local images it references: an absolute host path (`<img src="/Users/x/shot.png">`) resolves against the server origin, and a sibling path is refused by the exact-file token. Desktop web shows the same broken images.

## Scope

In:
- iPhone: host file links and backticked absolute paths become tappable and open an in-app viewer for `.html`, `.htm`, `.md`, `.txt`, `.json`, `.svg`, images and PDF, fetched from the thread's host through a signed asset URL (works over direct pairing and Connect).
- HTML renders in a `WKWebView` with a non-persistent data store and no script bridge, so it has no access to the app's session; the server's sandbox CSP still applies.
- Server: text artifacts served as `text/plain` (sandboxed, `nosniff`) through `media-file` URLs; local images referenced by served HTML load through their own signed URLs.
- Desktop web gets the HTML image fix through the same URLs.

Out:
- Android and the React Native app (`apps/mobile`), which already open these through `projects.readFile` and the asset WebView.
- Files on a third machine that is neither the viewer nor the thread's host.
- Editing files from the phone.

## Acceptance Criteria

- [ ] AC-01: On the iPhone app, a message linking `[cue-sheet.html](/abs/cue-sheet.html)` shows a tappable link; tapping it opens an in-app viewer that renders the HTML from the thread's host. Evidence: iPhone Duo simulator screenshots before (plain text) and after (rendered page) against a real paired server.
- [ ] AC-02: The same viewer opens `.md` (rendered Markdown), `.txt` and `.json` (monospaced, JSON pretty-printed), `.svg` and images, both from Markdown links and from backticked absolute paths.
- [ ] AC-03: `assets.createUrl` with a `media-file` resource accepts `.md`, `.markdown`, `.txt`, `.log`, `.json`, `.csv`, `.yaml`, `.yml`, `.xml`, `.toml`; the response is `text/plain; charset=utf-8` with `X-Content-Type-Options: nosniff` and a `sandbox` CSP. Protected paths stay refused.
- [ ] AC-04: HTML served from a `media-file` URL that references an absolute host image path or a sibling image gets those references rewritten to signed asset URLs, so the images load on phone and desktop web. Only image, video and audio files that the server would serve on their own are rewritten; protected and missing files are left as written.
- [ ] AC-05: The HTML viewer on iPhone uses a non-persistent `WKWebsiteDataStore`, registers no script message handlers and opens outside links in the system browser, never inside the app's session.
- [ ] AC-06: Unit tests cover the server MIME and rewrite rules, and the iOS link classification; the existing asset and Markdown tests still pass.

## Approach

1. Server MIME (`packages/shared/src/filePreview.ts`, `apps/server/src/assets/AssetAccess.ts`, `apps/server/src/http.ts`): add `hostTextPreviewMimeTypeFromExtension`; `media-file` mint and resolve accept host preview or host text; text responses get `text/plain; charset=utf-8` and `default-src 'none'; sandbox`.
2. HTML rewrite (`apps/server/src/assets/HtmlLocalReferences.ts`, new; `AssetAccess.ts`; `http.ts`): when a `media-file-exact` token resolves to HTML, read it (up to 5 MB), find `src`, `poster` and `srcset` values that are absolute host paths or relative paths, mint a `media-file-exact` URL for each readable media file and substitute it. Pure rewrite function plus a minting effect.
3. iOS links (`Weave/Markdown/MarkdownText.swift`, `Weave/Markdown/HostFileLink.swift`, new): classify absolute paths and `file://` URLs as host file links, keep them tappable under an internal `swc-file:` URL, and turn backticked absolute paths with a known extension into links.
4. iOS viewer (`SWCSync/LiveEngine+Sessions.swift`, `SWCSync/AppModel.swift`, `SWCFeatures/Chat/HostFileViewer.swift`, new; `SWCFeatures/Chat/ChatView.swift`): `hostFileURL(path:threadId:on:)` mints a `media-file` URL; the viewer picks web, Markdown or text by extension.
5. Evidence: live UI test against an isolated seeded server on the iPhone Duo simulator; headless web check of the HTML image fix.

Rejected: proxying file bytes over the RPC socket (the signed HTTP URL already reaches the host over every route, Connect included); `projects.readFile` on iPhone (no cwd in the native app's model and no binary support).

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01: Text artifacts are served as `text/plain` rather than their own types, so no browser ever renders them as active content.
- D-02: HTML rewriting covers `src`, `poster` and `srcset` only. Stylesheets and scripts next to the HTML are not rewritten.
- D-03: The viewer is a sheet over the thread on iPhone, reusable by 1273's Artifacts pane.
- D-04: HTML reference rewriting signs only media inside the page's own folder tree (checked on the written and the resolved path). Absolute paths elsewhere stay as written, since a page's scripts could otherwise read any host media. Windows paths are not rewritten.

### Open
- none

## Tasks

### T-01 Serve text artifacts through media-file URLs
- AC: AC-03 | Files: packages/shared/src/filePreview.ts, apps/server/src/assets/AssetAccess.ts, apps/server/src/http.ts, apps/server/src/assets/AssetAccess.test.ts | Test: node ../../node_modules/vite-plus/bin/vp test run src/assets/AssetAccess.test.ts (from apps/server)

### T-02 Rewrite local image references in served HTML
- AC: AC-04 | Files: apps/server/src/assets/HtmlLocalReferences.ts, apps/server/src/assets/HtmlLocalReferences.test.ts, apps/server/src/assets/AssetAccess.ts, apps/server/src/http.ts | Test: node ../../node_modules/vite-plus/bin/vp test run src/assets (from apps/server)

### T-03 iPhone: tappable host file links
- AC: AC-02, AC-06 | Files: apps/ios/SWCKit/Sources/Weave/Markdown/HostFileLink.swift, apps/ios/SWCKit/Sources/Weave/Markdown/MarkdownText.swift, apps/ios/SWCKit/Tests/WeaveTests/HostFileLinkTests.swift | Test: swift test --filter HostFileLink (from apps/ios/SWCKit)

### T-04 iPhone: host file viewer
- AC: AC-01, AC-02, AC-05 | Files: apps/ios/SWCKit/Sources/SWCFeatures/Chat/HostFileViewer.swift, apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatView.swift, apps/ios/SWCKit/Sources/SWCSync/LiveEngine+Sessions.swift, apps/ios/SWCKit/Sources/SWCSync/AppModel.swift | Test: make test-core (from apps/ios)

### T-05 Evidence on the iPhone Duo simulator and headless web
- AC: AC-01, AC-04 | Files: apps/ios/UITests/LiveArtifactTests.swift | Test: live UI test against the seeded isolated server; screenshots under reports/
