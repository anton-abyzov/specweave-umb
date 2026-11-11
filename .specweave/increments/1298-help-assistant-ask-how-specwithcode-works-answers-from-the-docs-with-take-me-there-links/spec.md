# Help assistant: ask how SpecWithCode works, answers from the docs with Take me there links

## Problem

On November 11, 2026 Anton could not work out how to connect his phone to a new machine. Connect was not obvious on the desktop, the web or the iPhone. His ask: "a kind of a chatbot where we could ask about all those features of SpecWithCode ... 'Where could we find something in settings?' or 'What is the best way to connect?'"

The answer existed (`repositories/anton-abyzov/specweave/docs-site/docs/studio/connect.md:46-50`: Settings > Machines > Your phones). Nothing in the product leads to it:

- **Search finds rows, not answers.** Settings search and the command palette share a catalog of about 300 rows with row anchors (`apps/web/src/components/settings/settingsSearch.ts:206`, used at `CommandPalette.tsx:2966`). "pair phone" finds a row. "how do I connect my phone" gets no steps, no order and no word on which device to do it on. "Your phones", the card the guide points at, is not a catalog row at all.
- **The app links to no guide.** The desktop Help menu has only "Check for Updates..." (`apps/desktop/src/window/DesktopApplicationMenu.ts:290-296`). The whole UI holds one docs link, to a GitHub file (`StudioFleetConnections.tsx:1215`). The repository has 45 user guides in `docs/user/`, 30 in `docs/studio/` and a detailed `CHANGELOG.md`; none is bundled or searchable in the app.
- **The docs site is thin.** 14 SpecWithCode pages, keyword search only, no Full access page, no SpecWithCode release notes, a hand-written `llms.txt`.
- **A stuck person cannot ask an agent.** Percy and coordinators know the product only as far as the model guesses, cannot point at a screen (chat routes only `studio://thread/` links, `apps/web/src/components/ChatMarkdown.tsx:3370-3398`), and need a signed-in provider. Built-in text generation fails quietly without one (`apps/server/src/serverSettings.ts:1083-1112`). First run is when help is needed most.
- **The phone cannot link into itself.** iOS deep links cover pairing and threads only (`apps/ios/SWCKit/Sources/SWCFeatures/Navigation/Router.swift:8-19,478-489`), and an unpaired phone has no server to ask.

## Scope

In, three phases:

1. **App (desktop and web): a help pack, Help, and Take me there.** One build-time pack made from the guides, the settings catalog and the release notes. Ask from the command palette or a Help panel. Answers link to the exact row. The same pack serves Percy and every agent through one tool.
2. **Hosted answers and the docs site.** A small answer endpoint on the Connect relay for people with no provider signed in, and an Ask box on spec-weave.com backed by the same pack. Docs gaps the test set finds are written.
3. **Phones.** Help on iOS and Android, working before a machine is paired.

Out: a named bot persona or a second assistant; answers about the person's own code, threads or project memory; Help taking actions (it points, the person clicks); opening a row on another machine from the phone; voice; live web search; translating the guides (answers follow the question's language, the pack is English in this increment); moving `docs/user` onto the docs site wholesale.

### Where it lives, and why

| Surface | Decision | Why |
|---|---|---|
| In the app (palette and Help panel) | First | The failure happened in the app. Only the app can open the exact row, and only it knows this machine's state ("Connect is already on here"). |
| Percy, coordinators, workers | Same pack through one tool | Reuses the assistant people already talk to. No parallel bot. Percy alone is not enough: it needs setup and a provider. |
| spec-weave.com docs | Second, same pack | Anton's words were "site idea" (possibly dictation for "side idea"). The site helps before install and costs little once the pack exists, but it cannot see the app or open a screen unless the app is installed. |
| iPhone and Android | Third | Needs new routes in both apps and the hosted endpoint, since an unpaired phone has no machine to ask. |

## Acceptance Criteria

### Phase 1: help pack, Help and Take me there (desktop and web)

- [ ] AC-01: `pnpm help:pack` builds one versioned `help-pack.json` from `docs/user/**`, `docs/studio/**`, the settings catalog (id, title, section, anchor, search terms, platform flags), per-setting help text and the last 20 releases of `CHANGELOG.md`. It ships inside the server build and is written to the release artifacts. Nobody edits it by hand; there is no FAQ file.
- [ ] AC-02: The pack build fails when a guide or release note names a settings path (`Settings > X > Y`) whose section or row is not in the catalog, or links a destination that does not exist. A new **Your phones** catalog row exists and anchors the card.
- [ ] AC-03: `help.search` returns ranked guide passages and settings rows from the pack with no model and no network. The command palette shows them under **Settings** (as today) and a new **Guides** group.
- [ ] AC-04: Help opens from: an **Ask Help: <question>** row at the top of the command palette when the query reads as a question or has no strong match; a **Help** button in the sidebar footer and in Settings; **Help > Ask SpecWithCode...** in the desktop menu; and an **Ask Help** row when Settings search finds nothing.
- [ ] AC-05: An answer has at most six numbered steps, each labelled with the device it happens on ("On this Mac", "On your iPhone"), **Take me there** buttons, and the guides it came from. Take me there opens the row with the existing highlight, keeps the machine and project scope, and leaves Help open.
- [ ] AC-06: Every button and guide link in an answer is a pack id that the app resolves. The model returns ids in a fixed schema; an id not in this build's pack is dropped, never rendered as a link.
- [ ] AC-07: Answers are written by this machine's text generation model on the person's own provider (the first ready provider when the chosen one is not ready). The footer names the provider and model.
- [ ] AC-08: With no ready provider, no network or a failed model call, Help shows the closest matches from search, each with Take me there or Read the guide. It never shows an empty or error-only panel.
- [ ] AC-09: A `studio://settings/<section>#<row>` or `studio://help/<guide>#<heading>` link in any chat renders as a Take me there or guide chip, and a target that no longer exists renders as a muted "no longer exists" chip. A read-only `studio_help_search` tool returns passages and these links. Percy's and the coordinator's instructions say to use it for questions about SpecWithCode.
- [ ] AC-10: The prompt holds only the question, the retrieved pack passages and an allowlist of state facts: platform, app version, Connect signed in and on, machine count, phone count, ready provider names, default permission mode. A test asserts it holds no project or thread names, paths, messages, memory, account emails or tokens. Help turns are not written to any thread or project memory and clear when the panel closes.
- [ ] AC-11: The state facts shape the answer: with Connect already on, "how do I connect my phone" skips turning it on and starts at Your phones.

### Phase 2: hosted answers and the docs site (after D-04)

- [ ] AC-12: The relay answers `POST /v1/help/ask` (question up to 500 characters, app version, platform, locale, state facts) with the same answer schema, using the pack published for that version. Limits: 30 a day per installation, 10 a minute per address, and a monthly spend cap after which it returns a "budget" refusal. It stores and logs no question text, only counts.
- [ ] AC-13: The app uses the hosted answer only when no provider is ready and **Hosted help** (Settings > Data & privacy, on by default) is on. The footer says "Written by SpecWithCode Help" and lists exactly what was sent, with **Turn off**. A refusal or timeout falls back to AC-08.
- [ ] AC-14: spec-weave.com has an Ask box on the SpecWithCode docs pages and `/code`. Answers cite docs pages; a settings destination shows **Open in SpecWithCode**, which opens that row in the installed desktop app.
- [ ] AC-15: Every answerable question in the test set has at least one source passage. The gaps found on November 11 are written: Full access, connecting a phone, text generation model, worktree storage, notifications, archive, load balancing, Google account, skills in the slash menu. The site gets a SpecWithCode release notes page and generated `llms.txt` and `llms-full.txt`, all from the pack.

### Phase 3: phones

- [ ] AC-16: iOS and Android show **Help** in global settings and on the welcome and pairing screens. The pack ships inside each app, so search works unpaired and offline. Answers come from the connected machine, else the hosted endpoint, else search.
- [ ] AC-17: A step for the phone gets a button that opens that screen (sign in, scan a code, machines, a global settings section). A step for the computer is labelled "On your computer" with the path and has no button.

### Answer quality

- [ ] AC-18: `docs/help/eval/questions.jsonl` holds at least 60 real questions: 50 answerable, each with accepted destinations, source guides and a reference answer, and 10 that Help must decline. It starts from the 50 lines in this increment's `eval/questions.jsonl`.
- [ ] AC-19: Required on every pull request, no model: the right guide or row is in the top 5 for at least 95% of answerable questions, and every destination and source in the test set exists in the built pack.
- [ ] AC-20: `pnpm help:eval` writes a report per release for the hosted model and the default text generation model of Codex and of Claude. Bars: first Take me there is an accepted destination, 90%; rendered links valid, 100%; answer matches the reference as judged by a model from another family, 85%; out-of-scope questions declined, 9 of 10. A miss names its cause: no source, wrong row, or wrong answer.
- [ ] AC-21: Each answer has thumbs up and down. The app keeps counts only (asked, answered, search-only, Take me there used, up, down) and adds them to the daily statistics when **Product improvement and diagnostics** is on. Thumbs down offers **Send this question to SpecWithCode**; the question text leaves the machine only on that click.

## Approach

**One pack, three consumers.** `scripts/build-help-pack.ts` reads the sources and writes `help-pack.json`: guide passages split by heading, catalog rows with their `studio://settings/...` link and per-platform target, and release entries. `packages/shared/src/help/` holds the pack types, the search (BM25 over titles, headings, search terms and text; no embeddings, no index service) and link parsing, so the server, the relay worker, the docs widget and the tests share one implementation. iOS and Android bundle the same JSON.

**Take me there reuses what exists.** Web navigation is already `{to, hash: targetId, state: {settingsTargetHighlight: true}}` (`SettingsSidebarNav.tsx:239-248`). The desktop protocol already loads `studio://app/settings/...` for provider sign-in returns behind an allowlist (`packages/shared/src/providerAuthReturnUrl.ts:4-24`, `apps/desktop/src/app/DesktopClerk.ts:176-200`); the docs site's **Open in SpecWithCode** widens that handler to any catalog row. Chat links get one more branch beside `parseStudioThreadHref` in `ChatMarkdown.tsx`.

**Answering.** `apps/server/src/help/HelpService.ts`: search, take the top 8 passages and rows, add the state facts, ask for a structured answer (lead sentence, steps with device and destination id, source ids, or "not in the guides"). The server resolves ids against the pack before anything reaches the client, which is what makes AC-06 hold on any model. Local answers go through the existing text generation path (`packages/contracts/src/settings.ts:2048`, the one thread titles and commit messages use), so there is no new provider plumbing and no new setting. Help is stateless: the panel sends at most the last two turns back for a follow-up.

**The model, and who pays.**

| Case | Model | Who pays | Cost |
|---|---|---|---|
| A provider is ready | That provider's text generation model (Codex GPT-6 Luna at low effort by default; Claude's Haiku) | The person's own subscription | One small request per question |
| No provider ready, or the docs site | Claude Haiku 5.5 (`claude-haiku-5-5`), low effort, structured output, on the relay | SpecWithCode | About $0.0007 a question (5,000 tokens in, 350 out at $0.10 and $0.50 per million, Anthropic's price list of November 3, 2026); $7 per 10,000 questions |
| Offline, hosted help off, over the cap | None: search results | Nobody | Free |

The relay already has anonymous, rate-limited routes with per-installation and global limiters (crash reports and site events, `infra/relay/src/worker.ts:217-240`); the help route follows that pattern and adds a spend counter with a $25 monthly cap (about 35,000 questions). This is free help, not model access: the endpoint answers only from the pack, declines everything else, and is never offered as a fallback for work. The release evaluation costs under $2 a run.

**Privacy.** Local answers stay between the person and a provider they already use. Hosted answers send the question, version, platform, locale and the state facts, and the panel says so each time. No question text is kept on the relay. Nothing about a project is ever read by Help; a person who wants help with their code asks a thread.

**Quality.** Retrieval is deterministic, so its gate is required CI. Model answers are judged per release and reported, not required, because a provider's model can change under us (D-06). The test set is the tool for keeping the guides current: a missed question is a guide to write or a row to rename.

**Order and files.** Phase 1 needs the shared `specwithcode-dev` checkout ("help-assistant may branch"). It touches `CommandPalette.tsx`, `ChatMarkdown.tsx`, `StudioSidebar.tsx` and `settingsSearch.ts`, which 1269, 1284 and 1294 also touch, so it goes after them. The onboarding worker's screens are not edited here: they get a `HelpLink` component (a preset question) to place on Connect, Machines and first run. Docs pages for AC-15 live in `repositories/anton-abyzov/specweave/docs-site` and can start now.

Rejected:

- **Percy as the help bot.** Per machine, needs setup and a provider, has personal memory and Gmail in scope. Wrong tool at first run. It gets the knowledge through the tool instead.
- **A hosted answer for everyone.** One model would be easier to evaluate, but every question would leave the machine, and the product's rule is that work stays between the person and their provider.
- **Embeddings or a vector store.** About 2,000 short passages with exact UI labels; keyword search with the catalog's search terms is enough, runs anywhere and needs no service. Revisit if the retrieval gate cannot reach 95%.
- **A hand-written FAQ.** It goes stale. The pack is built from what ships.
- **Docs site only.** It cannot see the app or open a screen.

Risks:

- The catalog imports web-only modules; the pack builder may need the static rows moved to a plain module first.
- `ws.ts` must not gain imports (TS2589); the help calls go through an existing RPC group.
- Answers on weaker local models may pick a worse row. The id check keeps links valid, the search fallback keeps Help useful, and the release report shows the gap per provider.
- Guides lag the UI. AC-02 catches renamed rows at build time; it cannot catch a behaviour change nobody documented.
- The hosted endpoint is a public model endpoint. Pack-only answers, short questions, the limits and the cap bound abuse and spend.

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01: Lives in the app first (command palette and Help panel), then the docs site with the same pack, then phones.
- D-02: It is called **Help**. No persona, no memory. Percy and coordinators answer product questions through `studio_help_search`.
- D-03: With a provider ready, answers use that provider's text generation model. No new model setting.
- D-05: Hosted help is on by default with a switch under Data & privacy; question text is never stored; thumbs-down sends a question only on an explicit click.
- D-06: The retrieval gate is required CI. The model answer report is written per release and does not block one.
- D-07: The pack is English in this increment; answers follow the question's language and keep UI labels as the app shows them.
- D-08: Help points and never acts: no tool calls, no settings changes.

### Open
- D-04: May SpecWithCode pay for hosted answers (Claude Haiku 5.5 on the relay, $25 monthly cap) for people with no provider signed in, for the docs site and for unpaired phones? Recommended: yes. Without it, those three cases get search results only, and AC-12 to AC-14 shrink to search. It is a new recurring spend and sends question text through the relay, so it is Anton's call.

## Tasks

### T-01 Pack builder, types and search
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode-dev/scripts/build-help-pack.ts, repositories/anton-abyzov/specwithcode-dev/packages/shared/src/help/, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/settingsSearch.ts, repositories/anton-abyzov/specwithcode-dev/package.json | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm help:pack && vp test run packages/shared/src/help

### T-02 Test set and the retrieval gate
- AC: AC-18, AC-19 | Files: repositories/anton-abyzov/specwithcode-dev/docs/help/eval/questions.jsonl, repositories/anton-abyzov/specwithcode-dev/packages/shared/src/help/retrievalGate.test.ts, repositories/anton-abyzov/specwithcode-dev/.github/workflows/ci.yml | Test: cd repositories/anton-abyzov/specwithcode-dev && vp test run packages/shared/src/help/retrievalGate.test.ts

### T-03 Help service: answer, id check, state facts, privacy
- AC: AC-06, AC-07, AC-08, AC-10, AC-11 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/help/HelpService.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/help/HelpService.test.ts, repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/help.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && vp test run apps/server/src/help

### T-04 Help panel, palette row and entry points
- AC: AC-03, AC-04, AC-05, AC-08 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/help/, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/CommandPalette.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/CommandPalette.logic.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/SettingsSidebarNav.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/StudioSidebar.tsx, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/window/DesktopApplicationMenu.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/help/ | Test: cd repositories/anton-abyzov/specwithcode-dev && vp test run apps/web/tests/help (headless: ask "how do I connect my phone", click Take me there, the Your phones row is highlighted)

### T-05 Links in chat and the help tool for agents
- AC: AC-09 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/ChatMarkdown.tsx, repositories/anton-abyzov/specwithcode-dev/apps/server/src/mcp/toolkits/help/, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ProjectWorkspaceService.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && vp test run apps/server/src/mcp/toolkits/help apps/web/src/components/ChatMarkdown.test.tsx

### T-06 Missing guides and generated site files
- AC: AC-15 | Files: repositories/anton-abyzov/specweave/docs-site/docs/studio/, repositories/anton-abyzov/specweave/docs-site/static/llms.txt, repositories/anton-abyzov/specweave/docs-site/scripts/ | Test: npm --prefix repositories/anton-abyzov/specweave/docs-site run build

### T-07 Hosted answer route on the relay
- AC: AC-12 | Files: repositories/anton-abyzov/specwithcode-dev/infra/relay/src/help/, repositories/anton-abyzov/specwithcode-dev/infra/relay/src/worker.ts, repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/relay.ts | Test: cd repositories/anton-abyzov/specwithcode-dev/infra/relay && vp test run src/help

### T-08 Hosted fallback in the app and its switch
- AC: AC-13 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/help/HostedHelp.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/help/, repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/settings.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && vp test run apps/server/src/help apps/web/tests/help

### T-09 Ask box on the docs site
- AC: AC-14 | Files: repositories/anton-abyzov/specweave/docs-site/src/components/AskHelp/, repositories/anton-abyzov/specweave/docs-site/src/theme/, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/app/DesktopClerk.ts, repositories/anton-abyzov/specwithcode-dev/packages/shared/src/providerAuthReturnUrl.ts | Test: npm --prefix repositories/anton-abyzov/specweave/docs-site run build (headless: ask "where is Full access" on /docs/studio/connect, the answer cites Permission modes)

### T-10 Help on iOS and Android
- AC: AC-16, AC-17 | Files: repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Help/, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Navigation/Router.swift, repositories/anton-abyzov/specwithcode-dev/apps/android/ | Test: swift test (SWCKit) and ./gradlew test (Android)

### T-11 Release report and in-app signal
- AC: AC-20, AC-21 | Files: repositories/anton-abyzov/specwithcode-dev/scripts/help-eval.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/help/, repositories/anton-abyzov/specwithcode-dev/apps/server/src/help/HelpCounters.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm help:eval --dry-run && vp test run apps/server/src/help

### T-12 Verify and close 1298
- AC: AC-01 | Files: .specweave/increments/1298-help-assistant-ask-how-specwithcode-works-answers-from-the-docs-with-take-me-there-links/reports/ | Test: specweave verify 1298-help-assistant-ask-how-specwithcode-works-answers-from-the-docs-with-take-me-there-links

## Mockups

Headless screenshots, light and dark, in `reports/mockups/` (`mockup.html`, rendered by `shoot.mjs`). Names, versions and scores are sample data.

| Screen | File |
|---|---|
| A question in the command palette | `ask-in-command-palette-dark.png` |
| The answer, docked beside the work | `help-answer-dark.png` |
| Where Take me there lands | `take-me-there-landed-light.png` |
| No provider signed in, and offline | `no-provider-and-offline-light.png` |
| iPhone before pairing | `help-on-iphone-dark.png` |
| Percy answering from the same guides | `percy-uses-help-dark.png` |
| Ask box on spec-weave.com | `docs-site-ask-light.png` |
| Quality report | `quality-report-dark.png` |
