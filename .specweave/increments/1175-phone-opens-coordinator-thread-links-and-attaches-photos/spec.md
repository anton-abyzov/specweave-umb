# Phone opens coordinator thread links and attaches photos

## Problem

Two reports from the owner on the iPhone app (`apps/ios`), November 2, 2026.

1. "Every time I try to click on one of those threads inside of the orchestrator window on a mobile phone, I get this error." No screenshot reached us. Code reading points at `AppModel.threadLink` (`apps/ios/SWCKit/Sources/SWCSync/IncrementProgress.swift:83`): it only accepts threads in the model's lists, and `ShellSummaries.isTopLevel` removes subagent threads from those lists. A coordinator's workers are delegated tasks with `relationshipToParent: subagent`, so every link to one fails with "This thread is not available on this machine...". Must be confirmed by reproduction. The desktop resolver (`apps/web/src/studio/studioThreadLinks.ts`, `StudioThreadLink.tsx`) also handles forms the phone does not: the ID as written (`%3A` pasted raw), bare links to a worker on another machine, and titles.

2. "On a mobile phone, I don't see a way to attach images... from my photos." `ComposerBar` has an attach button, but `ChatView` never passes `onAttach`, the engine send path takes text only, and transcript rows drop `attachments`, so the phone can neither send nor show an image.

## Scope

In: every `studio://thread/` form opens the right thread from any chat, including worker, archived and other-machine threads; a clear message when it really cannot open. Attach from Photos and camera in the coordinator, Aide and thread composers; HEIC handled; images show in the transcript; works on any route the phone uses (LAN, Tailscale, Connect).

Out: attaching non-image files; a desktop or server change (the existing upload contract is used); App Store submission.

## Acceptance Criteria

- [x] AC-01: A canonical link to a worker (subagent) thread in a coordinator chat opens that thread instead of showing an error, with a real server.
- [x] AC-02: Every link form resolves like desktop: encoded once, ID as written with `%3A`, `<environment>/<thread>` on another paired machine, a bare link to a worker on another paired machine, an archived thread, and a title only one thread has (including a title with a slash or a space).
- [x] AC-03: A link that cannot open says why: unpaired machine, still loading, or not available (the server leaves deleted threads out of its lists, so this message also names deletion; a thread row marked deleted says so outright). A named machine whose list has not loaded opens the chat and its own connection state instead of an error.
- [x] AC-04: The composer in coordinator, Aide and thread chats shows an attach control on small and Duo screens, and offers the system Photos picker, plus the camera where the device has one.
- [x] AC-05: A picked image (HEIC included) is converted to a JPEG under the server's 10 MiB limit with metadata removed, uploaded through `attachments.createUploadUrl`, and sent as a normal attachment on `message.dispatch` and `projects.coordinatorSend`, including an image with no text.
- [x] AC-06: Sent and received images show in the transcript, with a preview while sending; a failed send keeps the draft text and images.
- [x] AC-07: Upload uses the machine's own route, so a thread on another machine or over Connect takes the same path as a local one. The camera usage string covers photos.

## Approach

Thread links: `MarkdownThreadLink.Route` gains ID candidates and allows a space inside an ID. A new `ThreadLinkResolver` in SWCSync ports the desktop rules over a machine's full thread list. `AppEngine.threadLink` lets `LiveEngine` read the shell snapshot (subagents and archived included) instead of the filtered model lists. `ChatView` calls it.

Attachments: the coordinator accepts only pending uploads (`ProjectCoordinatorAttachments.validate`), so `assets.persistChatAttachments` cannot serve both paths. Use `attachments.createUploadUrl` and POST to `route.httpBase`, the same as Expo and web. The token in the URL is the credential. `PhotoAttachmentEncoder` (ImageIO) downsizes to 2048 px and writes JPEG, dropping EXIF and GPS. `PhotosPicker` runs out of process and needs no photo library permission, so no `NSPhotoLibraryUsageDescription` is declared. Display goes through `assets.createUrl`.

Rejected: base64 over the socket, because the coordinator refuses it. Sending HEIC as is, because providers accept only PNG, JPEG, GIF and WebP.

Risk: Connect cannot be driven from the simulator without an account sign-in; check the route on the cabled Duo if reachable, otherwise report it as not proven.

## Verification

Merged as `e305a1b9eb` (PR 1212). `swift test`: 529 passed. `LiveCoordinatorLinkTests` passed on two isolated real servers in the simulator, November 2, 2026. Attach and link fixture tests passed on iPhone 17 Pro and Duo simulators. Evidence is in `reports/`.

Not proven by a run: AC-07 over Connect, because the simulator has no account sign-in; it is met by code, since uploads use the same `MachineConnection` route as every other call. The cabled Duo was reachable but locked, so no real-device run happened (`reports/duo-device-locked.log`). The camera path was not exercised.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Images only, no arbitrary files → the report is about photos (reversible).
- D-02 2048 px JPEG → keeps uploads small on cellular and readable to the model (reversible).
### Open
- none

## Tasks

### T-01 Resolve every thread link form
- AC: AC-01, AC-02, AC-03 | Files: apps/ios/SWCKit/Sources/Weave/Markdown/MarkdownThreadLink.swift, apps/ios/SWCKit/Sources/SWCSync/ThreadLinkResolver.swift, apps/ios/SWCKit/Sources/SWCSync/IncrementProgress.swift, apps/ios/SWCKit/Sources/SWCSync/AppModel.swift, apps/ios/SWCKit/Sources/SWCSync/LiveEngine.swift, apps/ios/SWCKit/Sources/SWCSync/FixtureEngine.swift, apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatView.swift, apps/ios/SWCKit/Tests/SWCSyncTests/ThreadLinkResolverTests.swift | Test: cd apps/ios/SWCKit && swift test --filter 'ThreadLink|WeaveBehavior'

### T-02 Encode and send photos
- AC: AC-05, AC-07 | Files: apps/ios/SWCKit/Sources/SWCSync/PhotoAttachmentEncoder.swift, apps/ios/SWCKit/Sources/SWCSync/LiveEngine+Sessions.swift, apps/ios/SWCKit/Sources/SWCSync/AppModel.swift, apps/ios/SWCKit/Sources/SWCWire/Rpc.swift, apps/ios/SWCKit/Sources/SWCTransport/MachineHTTP.swift, apps/ios/project.yml, apps/ios/SWCKit/Tests/SWCSyncTests/PhotoAttachmentTests.swift | Test: cd apps/ios/SWCKit && swift test --filter PhotoAttachment

### T-03 Attach control and images in the transcript
- AC: AC-04, AC-06 | Files: apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatView.swift, apps/ios/SWCKit/Sources/SWCFeatures/Chat/TranscriptRowView.swift, apps/ios/SWCKit/Sources/Weave/Components/ComposerBar.swift, apps/ios/SWCKit/Sources/SWCSync/TranscriptMapper.swift, apps/ios/UITests/MobileReadabilityUITests.swift | Test: cd apps/ios && make sim-test ONLY=SpecWithCodeUITests/MobileReadabilityUITests

### T-04 Prove on a real server in the simulator
- AC: AC-01, AC-02, AC-04, AC-05, AC-06 | Files: reports only | Test: simulator screenshots saved to files

### T-05 Verify and close 1175
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07 | Files: none | Test: specweave verify 1175-phone-opens-coordinator-thread-links-and-attaches-photos
