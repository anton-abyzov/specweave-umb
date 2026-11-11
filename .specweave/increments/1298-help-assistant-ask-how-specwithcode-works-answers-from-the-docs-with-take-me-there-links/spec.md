# Help assistant: ask how SpecWithCode works, answers from the docs with Take me there links

## Problem

On November 11, 2026 Anton could not work out how to connect his phone to a new machine. Connect was not obvious on the desktop, the web or the iPhone. His ask: "a kind of a chatbot where we could ask about all those features of SpecWithCode ... 'Where could we find something in settings?' or 'What is the best way to connect?'"

The answer existed (`repositories/anton-abyzov/specweave/docs-site/docs/studio/connect.md:46-50`: Settings > Machines > Your phones). Nothing in the product leads to it:

- **The coordinator does not know the product.** It is the chat people already have open, but it knows SpecWithCode only as far as its model guesses, and it cannot point at a screen: chat routes only `studio://thread/` links (`apps/web/src/components/ChatMarkdown.tsx:3370-3398`).
- **Search finds rows, not guides.** Settings search and the command palette share a catalog of about 300 rows with row anchors (`apps/web/src/components/settings/settingsSearch.ts:206`, used at `CommandPalette.tsx:2966`). "pair phone" finds a row. Nothing searches the guides, and "Your phones", the card the phone guide points at, is not a catalog row.
- **The app links to no guide.** The desktop Help menu has only "Check for Updates..." (`apps/desktop/src/window/DesktopApplicationMenu.ts:290-296`). The whole UI holds one docs link, to a GitHub file (`StudioFleetConnections.tsx:1215`). The repository has 45 user guides in `docs/user/`, 30 in `docs/studio/` and a detailed `CHANGELOG.md`; none is bundled or searchable in the app.
- **The docs site is thin.** 14 SpecWithCode pages, no Full access page, no SpecWithCode release notes, a hand-written `llms.txt`.
- **The phone cannot link into itself.** iOS deep links cover pairing and threads only (`apps/ios/SWCKit/Sources/SWCFeatures/Navigation/Router.swift:8-19,478-489`).

## Scope

In, three phases:

1. **App (desktop and web).** One build-time help pack made from the guides, the settings catalog and the release notes. Every project coordinator, Percy and any other chat answers "how do I..." from it through one tool, on the person's own provider, and every answer carries Take me there links that open the settings page or dialog, scroll to the row and highlight it. With no provider signed in, the same pack is searched in the command palette, with the same links.
2. **Docs site.** The guides the test set finds missing, SpecWithCode release notes, and settings paths that open the installed app.
3. **Phones.** The same links and the same search on iOS and Android.

Out: any model paid for by SpecWithCode, and any hosted answer endpoint (D-04); a separate help agent, panel, persona or model setting; an Ask box on the docs site; Help changing a setting for the person (it opens the place, the person clicks); answers about the person's own code, which the coordinator already gives; opening a row on another machine from the phone; translating the guides (answers follow the question's language, the pack is English in this increment).

### Where it lives, and why

| Surface | Decision | Why |
|---|---|---|
| Every project coordinator, Percy and any chat | The answer surface | Anton's decision (D-09). It is the chat already open, it runs on the person's own provider, and it costs SpecWithCode nothing. |
| Command palette and Settings search | Guide and settings search with the same links | Works with no provider signed in, offline, and at first run. No model. |
| spec-weave.com docs | Guides, release notes, links into the app | No model on the site, so no Ask box. The existing site search covers the new pages. |
| iPhone and Android | Same links in chat; bundled search | An unpaired phone has no coordinator, so it gets search. |

## Acceptance Criteria

### Phase 1: the pack, the coordinator and Take me there (desktop and web)

- [ ] AC-01: `pnpm help:pack` builds one versioned `help-pack.json` from `docs/user/**`, `docs/studio/**`, the settings catalog (id, title, section, anchor, search terms, platform flags), per-setting help text and the last 20 releases of `CHANGELOG.md`. It ships inside the server build. Nobody edits it by hand; there is no FAQ file.
- [ ] AC-02: The pack build fails when a guide or release note names a settings path (`Settings > X > Y`) whose section or row is not in the catalog, or links a destination that does not exist. A new **Your phones** catalog row exists, and every destination in the test set has its own anchor instead of falling back to its section.
- [ ] AC-03: A read-only `studio_help_search` tool is available to every project coordinator, to Percy and to worker threads, on every provider that gets SpecWithCode's tools. It returns the closest guide passages, the matching settings rows with their links, and the state facts of AC-07, in at most about 1,500 tokens. The coordinator, Percy and worker instructions gain one line: for a question about SpecWithCode itself, call it and answer from it. There is no separate help agent, model or setting.
- [ ] AC-04: Asked "how do I connect my phone" or "where is Full access", a coordinator answers with short numbered steps, names the device each step happens on, puts a Take me there link on each step that has a destination, and names the guide it used. When the pack has no answer it says so and does not guess. Measured by AC-17.
- [ ] AC-05: In any chat, `studio://settings/<section>#<row>`, `studio://project-settings/<tab>#<row>`, `studio://open/<dialog>` and `studio://help/<guide>#<heading>` render as chips: **Take me there** for a place, a guide chip for a passage. A link whose target is not in this build's catalog renders as a muted "no longer exists" chip, never as a dead link.
- [ ] AC-06: Take me there opens the page for the thread's machine and project scope, opens a collapsed group if the row is inside one, scrolls the row to the middle of the view and rings it for about 2.5 seconds, on long pages too. `studio://open/` opens the allowlisted dialogs **Pair a phone**, **Add a machine** and **Join a main machine**. Arriving from a chat link, the page shows **Back to the coordinator** (or the chat's name), which returns to the thread at the same scroll position.
- [ ] AC-07: The tool's state facts are an allowlist: platform, app version, Connect signed in and on, machine count, phone count, ready provider names, default permission mode. A test asserts the tool result holds no project or thread names, paths, messages, memory, account emails or tokens. With Connect already on, the answer to "how do I connect my phone" skips turning it on.
- [ ] AC-08: With no provider signed in, offline, or outside any chat, the command palette lists matching guide passages under **Guides** beside **Settings**, with no model and no network. **Help** in the sidebar footer, **Help > Search help...** in the desktop menu and the empty state of Settings search open the palette scoped to guides and settings. Inside a project with a ready provider the palette also offers **Ask the coordinator: <question>**, which sends the question to that project's coordinator.
- [ ] AC-09: A guide result or a `studio://help/` chip opens that passage from the pack in an in-app reader. Settings paths inside it are Take me there links.
- [ ] AC-10: Help sends nothing to SpecWithCode. The pack is local, search is local, and the only model call is the chat's own turn on the person's provider. A test asserts the help tool and palette search make no network request.

### Phase 2: docs site

- [ ] AC-11: Every answerable question in the test set has at least one source passage. The gaps found on November 11 are written: text generation model, default model, worktree storage, thread notifications, dictation language, Google account, archived threads, load balancing, skills in the slash menu, plus a site page for Full access and for connecting a phone.
- [ ] AC-12: The site has a SpecWithCode release notes page and generated `llms.txt` and `llms-full.txt`, built from the pack. A settings path on a SpecWithCode docs page is an **Open in SpecWithCode** link that opens that row in the installed desktop app. The site runs no model.

### Phase 3: phones

- [ ] AC-13: On iOS and Android the same links render as chips in chat. A destination on the phone opens that screen (sign in, scan a code, machines, a global settings section). A destination on the computer shows "On your computer" with the path and has no button.
- [ ] AC-14: The pack ships inside each app. **Help** in global settings and on the welcome and pairing screens searches it unpaired and offline, with the same buttons.

### Answer quality

- [ ] AC-15: `docs/help/eval/questions.jsonl` holds at least 60 real questions: 50 answerable, each with accepted destinations, source guides and a reference answer, and 10 the coordinator must decline or hand back. It starts from the 50 lines in this increment's `eval/questions.jsonl`.
- [ ] AC-16: Required on every pull request, no model: the right guide or row is in the top 5 for at least 95% of answerable questions, and every destination and source in the test set exists in the built pack.
- [ ] AC-17: `pnpm help:eval` writes a report per release. It sends the questions to a coordinator in a fixture project on the release machine's own signed-in Codex and Claude, so it spends no API money. Bars: first Take me there is an accepted destination, 90%; rendered links valid, 100%; answer matches the reference as judged by a model from another family, 85%; out-of-scope questions not answered from the guides, 9 of 10. A miss names its cause: no source, wrong row, or wrong answer.
- [ ] AC-18: The app keeps counts only: help lookups, lookups that found no source, Take me there clicks, searches with no provider. They join the daily statistics when **Product improvement and diagnostics** is on. No question text leaves the machine.

## Approach

**One pack.** `scripts/build-help-pack.ts` reads the sources and writes `help-pack.json`: guide passages split by heading, catalog rows with their link and per-platform target, and release entries. `packages/shared/src/help/` holds the pack types, the search (BM25 over titles, headings, search terms and text; no embeddings, no index service) and link parsing, shared by the server tool, the palette, the docs build and the tests. iOS and Android bundle the same JSON.

**The coordinator is the help agent.** The tool lives in `apps/server/src/mcp/toolkits/help/`, beside the other `studio-code` toolkits, so it reaches every provider at once. The instruction line goes where the coordinator and Percy prompts are built (`apps/server/src/project/ProjectWorkspaceService.ts:210-226`). A tool, not a skill: skills are per harness and can be switched off per machine, the tool cannot drift. The tool result is small on purpose, because a coordinator thread can be long and a help answer should cost one ordinary turn.

**Take me there reuses what exists.** Web navigation is already `{to, hash: targetId, state: {settingsTargetHighlight: true}}` (`SettingsSidebarNav.tsx:239-248`). Chat links get one more branch beside `parseStudioThreadHref` in `ChatMarkdown.tsx`, resolved against the catalog before rendering, which is what keeps a wrong link from an agent harmless. The desktop protocol already loads `studio://app/settings/...` for provider sign-in returns behind an allowlist (`packages/shared/src/providerAuthReturnUrl.ts:4-24`, `apps/desktop/src/app/DesktopClerk.ts:176-200`); the docs site's **Open in SpecWithCode** widens that to catalog rows.

**Destinations in this increment.** Global settings rows, project settings rows and three dialogs. Controls outside Settings, such as the composer's permission picker, are described in words and linked to their default in Settings. That keeps this increment out of `ChatComposer.tsx`.

**The model, and who pays.**

| Case | Who answers | Who pays |
|---|---|---|
| A provider is signed in | The chat you asked: the project coordinator, Percy or a thread, on its own model | The person's own subscription, one ordinary turn |
| No provider, offline, first run | Nobody: guide and settings search with the same links | Nobody |

**Privacy.** The question is an ordinary chat message to a provider the person already uses. The tool reads only the pack and the allowlisted state facts. Nothing goes to SpecWithCode.

**Quality.** Retrieval is deterministic, so its gate is required CI. Coordinator answers are judged per release and reported, not required, because a provider's model can change under us. A missed question is a guide to write or a row to rename.

**Order and files.** Phase 1 needs the shared `specwithcode-dev` checkout ("help-assistant may branch"). It adds one row to `StudioSidebar.tsx` (also touched by 1269 and 1284), one line in `ProjectWorkspaceService.ts` (1269, 1276) and one row in `settingsSearch.ts` (1295); the rest is new files plus `CommandPalette.tsx` and `ChatMarkdown.tsx`. It no longer touches the composer or the relay. The onboarding worker's screens are not edited here: they can place a `studio://help/` or Take me there link, or the **Help** entry, on Connect, Machines and first run. Docs pages for AC-11 live in `repositories/anton-abyzov/specweave/docs-site`.

Rejected:

- **A hosted model paid by SpecWithCode** for people with no provider. Anton: "I don't think we need to pay anything." Those people get search.
- **A separate Help panel with its own answer call.** Anton wants it in the coordinator; one surface less to build and to keep consistent.
- **A skill instead of a tool.** Per harness and switchable; a skill can follow for outside agents.
- **Embeddings or a vector store.** About 2,000 short passages with exact UI labels; keyword search with the catalog's search terms is enough. Revisit if the retrieval gate cannot reach 95%.
- **A hand-written FAQ.** It goes stale. The pack is built from what ships.

Risks:

- A help question in a long coordinator thread costs a full coordinator turn. The capped tool result keeps the added cost small; the turn itself is the person's choice of where to ask.
- OpenCode threads on a local model run without SpecWithCode's tools, so they cannot look up help. The palette search still works there.
- An agent may answer from memory instead of calling the tool. The instruction line and the release report (AC-17) are the control; links it invents render as "no longer exists".
- The catalog imports web-only modules; the pack builder may need the static rows moved to a plain module first.
- Guides lag the UI. AC-02 catches renamed rows at build time; it cannot catch a behaviour change nobody documented.

## Decisions

### Asked
- D-04: May SpecWithCode pay for hosted answers for people with no provider signed in? → No. "I don't think we need to pay anything." (Anton, November 11, 2026). No hosted model anywhere; no provider means search results with the same links.
- D-09: Where does help live? → Inside every project coordinator, and any chat, on the person's own provider. "Maybe it could even be incorporated somehow into every coordinator of each project ... you provide details and then a clickable link, maybe to open it in a menu, configure it, and even scroll it to a specific section if this is a huge page." (Anton, November 11, 2026)

### Defaulted (change any before sw-do)
- D-02: No persona and no new chat. The help knowledge is one tool, `studio_help_search`, with one instruction line.
- D-03: The palette offers **Ask the coordinator: <question>** only inside a project with a ready provider; everywhere else it shows search results.
- D-05: Destinations are settings rows, project settings rows and three dialogs. Composer controls are described in words.
- D-06: The retrieval gate is required CI. The coordinator answer report is written per release and does not block one.
- D-07: The pack is English in this increment; answers follow the question's language and keep UI labels as the app shows them.
- D-08: Help opens the place and never changes a setting itself.
- D-10: No Ask box on the docs site, since it would need a hosted model.

### Open
- none

## Tasks

### T-01 Pack builder, types and search
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode-dev/scripts/build-help-pack.ts, repositories/anton-abyzov/specwithcode-dev/packages/shared/src/help/, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/settingsSearch.ts, repositories/anton-abyzov/specwithcode-dev/package.json | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm help:pack && vp test run packages/shared/src/help

### T-02 Test set and the retrieval gate
- AC: AC-15, AC-16 | Files: repositories/anton-abyzov/specwithcode-dev/docs/help/eval/questions.jsonl, repositories/anton-abyzov/specwithcode-dev/packages/shared/src/help/retrievalGate.test.ts, repositories/anton-abyzov/specwithcode-dev/.github/workflows/ci.yml | Test: cd repositories/anton-abyzov/specwithcode-dev && vp test run packages/shared/src/help/retrievalGate.test.ts

### T-03 Help tool, state facts and the instruction line
- AC: AC-03, AC-04, AC-07, AC-10 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/mcp/toolkits/help/, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ProjectWorkspaceService.ts, repositories/anton-abyzov/specwithcode-dev/docs/internals/agent-instructions.md | Test: cd repositories/anton-abyzov/specwithcode-dev && vp test run apps/server/src/mcp/toolkits/help apps/server/src/project/ProjectWorkspaceService.test.ts

### T-04 Links in chat and landing on the row
- AC: AC-05, AC-06, AC-12 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/ChatMarkdown.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/help/TakeMeThere.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/SettingsSidebarNav.tsx, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/app/DesktopClerk.ts, repositories/anton-abyzov/specwithcode-dev/packages/shared/src/providerAuthReturnUrl.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/help/ | Test: cd repositories/anton-abyzov/specwithcode-dev && vp test run apps/web/tests/help (headless: click the Your phones link in a chat fixture; the Machines page opens, the row is in view and ringed)

### T-05 Guides in the palette, Help entry points and the guide reader
- AC: AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/CommandPalette.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/CommandPalette.logic.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/help/GuideReader.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/StudioSidebar.tsx, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/window/DesktopApplicationMenu.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && vp test run apps/web/src/components/CommandPalette.logic.test.ts apps/web/tests/help

### T-06 Missing guides, release notes and links on the docs site
- AC: AC-11, AC-12 | Files: repositories/anton-abyzov/specweave/docs-site/docs/studio/, repositories/anton-abyzov/specweave/docs-site/static/llms.txt, repositories/anton-abyzov/specweave/docs-site/scripts/, repositories/anton-abyzov/specwithcode-dev/docs/user/ | Test: npm --prefix repositories/anton-abyzov/specweave/docs-site run build

### T-07 Links and Help search on iOS and Android
- AC: AC-13, AC-14 | Files: repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Help/, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Navigation/Router.swift, repositories/anton-abyzov/specwithcode-dev/apps/android/ | Test: swift test (SWCKit) and ./gradlew test (Android)

### T-08 Release report and counters
- AC: AC-17, AC-18 | Files: repositories/anton-abyzov/specwithcode-dev/scripts/help-eval.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/help/HelpCounters.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm help:eval --dry-run && vp test run apps/server/src/help

### T-09 Verify and close 1298
- AC: AC-01 | Files: .specweave/increments/1298-help-assistant-ask-how-specwithcode-works-answers-from-the-docs-with-take-me-there-links/reports/ | Test: specweave verify 1298-help-assistant-ask-how-specwithcode-works-answers-from-the-docs-with-take-me-there-links

## Mockups

Headless screenshots, light and dark, in `reports/mockups/` (`mockup.html`, rendered by `shoot.mjs`). Names, versions and scores are sample data.

| Screen | File |
|---|---|
| The coordinator answers, with Take me there links | `coordinator-answers-dark.png` |
| Where Take me there lands on a long page | `take-me-there-landed-light.png` |
| A question in the command palette | `ask-in-command-palette-dark.png` |
| No provider signed in: search and the guide reader | `no-provider-search-light.png` |
| Percy answering from the same guides | `percy-uses-help-dark.png` |
| iPhone before pairing | `help-on-iphone-dark.png` |
| A docs page that opens the app | `docs-open-in-app-light.png` |
| Quality report | `quality-report-dark.png` |
