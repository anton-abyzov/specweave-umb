# HTML file links open rendered in a sandboxed preview, and every file link in a reply opens its native preview

## Problem

Anton clicked the `page.html` link in a reply ("approval page draft page.html", thread "Viral series: copy to new machine"). The viewer opened it as "HTML File page.html" and showed the raw source with syntax highlighting, with Open in editor, Reveal in Finder and Open in panel in the header. He expected the page.

Evidence (screenshot of November 16, 2026, and the code on `origin/main` at `21d74227e`):

- A file link opens in one of three places (`apps/web/src/lib/openInFront.ts`, `openFileInFront`): the viewer overlay when one is already in front, the focused viewer when the window is too narrow for the side panel, or the thread's side panel.
- The overlay and the focused viewer both render `ViewerLinkedPane` > `LinkedFile` (`apps/web/src/components/chat/ViewerLinkedPane.tsx`). It knows two things: markdown, and "everything else as source". It reads every file as text first.
  - `.html` shows as source. That is the screenshot: he had `ep2-ru-master.mp4` open in the viewer, so the link opened in its place.
  - A video, image, audio file or PDF fails the text read and shows "The file is binary and cannot be displayed as text."
  - CSV, `.pptx` and office files get source or the same error.
- The other two renderers already draw each kind: the side panel (`FilePreviewPanel`) and the artifact viewer (`ThreadArtifacts.ArtifactBody`). Only the side panel has a rendered/source switch, and it stores "source" as a sticky preference, so one click on it makes every later HTML file open as source. Markdown in the side panel opens as source until the person switches it once.
- In the "N files" list (`MarkdownPathList`), the chip opens the file; the full path beside it is text that does nothing on click.
- The sandbox is weaker than the request. The server sends HTML files with `Content-Security-Policy: sandbox allow-scripts allow-forms allow-popups` (`apps/server/src/http.ts`). The page has an opaque origin, so it cannot reach the app's session. Nothing stops its scripts from loading or calling any site, opening windows, or sending its frame to another site. Checked headless on November 16, 2026: with today's header a framed page reached a listener on another origin by image, fetch, WebSocket and navigation.
- A page inside the project folder cannot load a video or audio file next to it (the folder scope leaves those types out). A page outside it (scratch, evidence) loads pictures, video and audio it names with `src`, `poster` or `srcset`.

## Scope

In: the overlay and focused viewer's file pane, the side panel's HTML and markdown defaults, the artifact viewer's HTML source switch, the files list path cell, and the server's response for HTML files shown in a frame. Web and desktop.

Out:

- Stylesheets, scripts and fonts in separate files next to an HTML page outside the project folder (a page inside it loads them today; pictures, video and audio resolve for both).
- Agent HTML renders (`html_render`, `show_visual`) and other attachments: their frame and policy do not change.
- HTML opened as its own tab or window (the integrated browser, "Open in browser", the phone apps): it stays a browser page, as today.
- Media and HTML previews for a file no thread owns (a link in a Library document): text kinds keep working, the rest say why.
- Paths with spaces in inline code, and `~/` paths in a project outside the home folder.

## Acceptance Criteria

- [ ] AC-01: An `.html` or `.htm` file link opened in the viewer overlay or the focused viewer shows the rendered page, not its source. The header says "Page" and the file name.
- [ ] AC-02: The header has one switch for an HTML file: "View source" shows the highlighted source, "Preview" goes back. A link with a line number opens the source at that line. The artifact viewer (an absolute-path link opened from the thread) has the same switch. The side panel opens every HTML file rendered: showing source there applies to the open file only and is not remembered.
- [ ] AC-03: In the overlay and the focused viewer a video plays in the native player with seeking, an audio file plays, an image is shown and can be zoomed, and a PDF opens in the PDF viewer. None of them shows a "binary" error. A CSV or TSV shows as a table, a `.pptx` as its slides, and an office document or archive as a card that opens it in its app.
- [ ] AC-04: A markdown link opens rendered in all three places. In the side panel that is the default until the person chooses source there.
- [ ] AC-05: A rendered HTML page shows the local pictures, video and audio it names: by `src`, `poster` or `srcset` for a page outside the project folder, and by relative URL for a page inside it.
- [ ] AC-06: Inside an app frame, an HTML file's scripts and markup cannot reach the app or anything but local files. Measured headless against a real server with a listener on another origin that must receive zero requests: image, script, stylesheet, font, media, `fetch`, XHR, WebSocket, beacon and form submission are refused; `window.open` returns nothing; sending its own frame, its parent or the top window to another origin is refused; `document.cookie` and `parent.document` throw.
- [ ] AC-07: A link to another site inside a rendered page opens in the browser only when the reader clicks it, through the app. Without a click nothing opens.
- [ ] AC-08: In the "N files" list, clicking the full path opens the file exactly as its chip does. A missing file's path stays plain text. Inline-code paths and list rows for `.html`, `.mp4`, `.png`, `.pdf` and `.md` each open the preview for their kind.
- [ ] AC-09: Nothing changes for an HTML file opened as its own tab or window, for attachments and agent HTML renders, or for a PDF. A server older than this change still shows the page in the frame.
- [ ] AC-10: Before and after screenshots of the `page.html` case, and one of each other kind, are in this increment's `reports/`.

## Approach

Server (`apps/server`):

1. `apps/server/src/assets/HtmlFilePreview.ts` (new) holds what a framed HTML file needs:
   - The locked policy: `sandbox allow-scripts allow-forms; default-src 'none'; script-src 'sha256-<link script>'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; media-src 'self' data: blob:; font-src 'self' data:; connect-src 'none'; form-action 'none'; base-uri 'none'`. `'self'` is the asset server, which serves files only through signed URLs. script-src is only the hashed link script. A page script can post `ui/open-link` for a site the reader did not click, so the page's own scripts do not run. Checked headless: under `sandbox` Chromium matches `'self'` against the document's URL, so local pictures, video and audio load.
   - A wrapper page. Content policy cannot stop a page from navigating its own frame, but a parent's `frame-src` can. The wrapper is a script-free shell (one hashed relay script) with `frame-src 'self'` that frames the real page. Checked headless: the inner page loads, its navigation to another origin is refused, and so is navigating the wrapper or the top window.
   - A small link script added to the page: a trusted click on an `http(s)` link asks the app to open it (`ui/open-link`, the protocol agent renders already use) instead of navigating. The wrapper forwards only that request, not an arbitrary message from the page.
2. `apps/server/src/http.ts`: for a file HTML asset (host file or workspace file, never an attachment):
   - `?studio-frame=1`, or an `iframe` fetch destination with no parameter, returns the wrapper, which frames the same path with `?studio-frame=page`.
   - Any request that is not a top-level document load gets the locked policy. A top-level load (`Sec-Fetch-Dest: document`, no parameter) keeps today's policy. A framed page cannot reach that copy: it cannot open windows, cannot navigate the top window, and `connect-src 'none'` blocks fetching it.
   - HTML responses become `Cache-Control: private, no-store` with `Vary: Sec-Fetch-Dest`, so a browser never reuses a top-level copy in a frame.
   - Workspace HTML is read and gets the link script the way host HTML is already rewritten (5 MB limit, UTF-8; otherwise the bytes are served as they are).
3. `apps/server/src/assets/AssetAccess.ts`: the workspace folder scope also serves video and audio types.

Web (`apps/web`):

4. `components/files/BrowserDocumentFrame.tsx`: the file HTML frame drops `allow-popups`, asks for `studio-frame=1`, and answers `ui/open-link` from its own frame only while the reader is using it (the checks agent renders use).
5. `components/files/LinkedFileBody.tsx` (new): one body by kind for a linked file, using `filePreviewKind`, `hostFilePreview` and `filePreviewDelimiter`: HTML frame or source, PDF frame, video, audio, zoomable image, markdown document, table, deck, card, source. Media and documents load through a signed asset URL (`workspace-file` for a page inside the project folder so its siblings resolve, `media-file` otherwise); only text kinds read the file as text.
6. `components/chat/ViewerLinkedPane.tsx`: `LinkedFile` renders that body, the header kind follows the file kind, and the switch sits with the header actions. `components/ViewerOverlayHost.tsx`: the focused viewer's actions get the same switch.
7. `components/chat/ThreadArtifacts.tsx`: the artifact viewer gets the switch for HTML and uses the same resource choice.
8. `components/files/FilePreviewPanel.tsx`: HTML source is per open file; markdown defaults to rendered; an image outside the project folder uses `media-file`.
9. `components/chat/MarkdownPathList.tsx`: the path cell is a button that activates the row's chip.
10. New words go into all eight phrase files.

Rejected:

- Reusing the artifact viewer for links inside the overlay. It replaces the viewer that is open, so Back would be lost.
- Locking by a URL parameter alone. The page could navigate to the same URL without it.
- Locking every HTML response, top-level loads included. A page in a browser tab can navigate anywhere regardless, and it would break pages people open in the integrated browser.
- `allow-popups` with a click check. The desktop app has no popup blocker in front of `window.open`.

Risks:

- Pages that load fonts, scripts or styles from other sites lose them inside the app frame, and so do a page's own scripts. That is the request; "Open in browser" shows the page as a browser does.
- DNS prefetch is not covered by content policy in Chromium. A page could leak a few bytes through host names.
- A page can still request other URLs on the app's own server as pictures or frames. Those requests carry no session (opaque origin, `SameSite=Lax` cookie) and their answers cannot be read. Unchanged from today.
- Without `Sec-Fetch-Dest` (plain `http` to a LAN address), a top-level load also gets the locked policy. Stricter, not broken.
- WebKit was not available for the headless check; the policy uses only directives WebKit supports, and the phone apps load pages top-level.

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01 Links to other sites inside a previewed page open in the browser on the reader's click, through the app, as agent HTML renders do. Reversible: remove the link script and they do nothing.
- D-02 The side panel no longer remembers "show HTML source". Markdown there defaults to rendered for anyone who never chose.
- D-03 The switch reads "View source" / "Preview" (both already translated in all eight languages).
- D-04 The frame runs only the hashed link script. The page's inline scripts, `eval` and sibling scripts do not run there: a script can forge `ui/open-link` on the reader's next click. Open in browser still runs them.
- D-05 A file with no thread keeps today's text view; media and HTML there show a short "open it from a thread" card.

### Open
- none

## Tasks

### T-01 Server locks framed HTML files to local content
- AC: AC-05, AC-06, AC-07, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/assets/HtmlFilePreview.ts, repositories/anton-abyzov/specwithcode/apps/server/src/assets/HtmlFilePreview.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/http.ts, repositories/anton-abyzov/specwithcode/apps/server/src/assets/AssetAccess.ts, repositories/anton-abyzov/specwithcode/apps/server/src/assets/AssetAccess.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/server.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/assets/HtmlFilePreview.test.ts src/assets/AssetAccess.test.ts

### T-02 File HTML frame without popups, with reader-clicked links
- AC: AC-06, AC-07, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/files/BrowserDocumentFrame.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/files/BrowserDocumentFrame.test.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run --project unit src/components/files/BrowserDocumentFrame.test.tsx

### T-03 Linked files render by kind, with the source switch
- AC: AC-01, AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/files/LinkedFileBody.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/files/LinkedFileBody.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ViewerLinkedPane.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ViewerLinkedPane.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/ViewerOverlayHost.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run --project unit src/components/files/LinkedFileBody.test.tsx src/components/chat/ViewerLinkedPane.test.tsx src/i18n/i18n.test.ts

### T-04 Artifact viewer and side panel open HTML and markdown rendered
- AC: AC-02, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ThreadArtifacts.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ThreadArtifacts.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/files/FilePreviewPanel.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/files/FilePreviewPanel.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run --project unit src/components/chat/ThreadArtifacts.test.tsx src/components/files/FilePreviewPanel.test.ts

### T-05 The files list path opens the file
- AC: AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/MarkdownPathList.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/MarkdownPathList.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/ChatMarkdown.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run --project unit src/components/chat/MarkdownPathList.test.tsx

### T-06 Headless proof: sandbox against a real server, before and after screenshots
- AC: AC-05, AC-06, AC-07, AC-08, AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/web/tests/viewer-links, repositories/anton-abyzov/specwithcode/scripts/studio-verify/html-file-sandbox.mjs | Test: cd repositories/anton-abyzov/specwithcode && node scripts/studio-verify/html-file-sandbox.mjs "$HOME/.specwithcode/m4/scratch/2026-11-16-html-preview-1368/sandbox"

### T-07 Review, merge, release
- AC: AC-09, AC-10 | Files: .specweave/increments/1368-html-file-links-open-rendered-in-a-sandboxed-preview-and-every-file-link-in-a-reply-opens-its-native-preview/reports | Test: cd repositories/anton-abyzov/specwithcode && bash scripts/release/request-release.sh --released "$(git rev-parse origin/main)"
