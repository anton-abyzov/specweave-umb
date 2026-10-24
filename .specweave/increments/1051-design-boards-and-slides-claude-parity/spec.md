# 1051 Design boards and slides: Claude parity and full scenario verification

Linked to 1046 (design system workspace and project designs, PR #667), 1041 (design creation and reuse, PR #660) and 0975 (design slides, its T-07 close is still open). Stacked on `feat/1046-design-workspace`.

## Problem

Anton, October 24, 2026, scheduled for a verification push at 8:10 AM EDT. His words: "check each and every workflow, especially with the design, like in Claude. Create more scenarios for boards, like testing slides, especially with the presentation. Compare it. Create at least three slides with different flows, like creating something from scratch or importing it as well. And make sure to test two other options when you go to design and create something."

What is known on October 24, 2026 at about 3:50 AM EDT:

- **"Make something new" offers four kinds.** They are Slides, Design, Design from code and Design system (`apps/web/src/components/design/gallery/galleryModel.ts:352-375`). Besides Slides, the two other real create options are **Design** (a blank canvas) and **Design from code** (an agent designs against a project's code).
- **Slides support creation from scratch, but nothing imports a deck.**
  - Supported: slide rail and menu, layouts built from the design system, speaker notes, Present and Presenter view, and export to PDF and PowerPoint (`apps/web/src/components/design/slides/`, `apps/web/src/components/design/editor/DesignEditor.tsx:930-955`, `apps/server/src/design/export/pptx.ts`).
  - Missing: there is no PowerPoint or PDF import into slides. Today the only "import" path is an agent asked to rebuild a deck.
- **Claude is the reference, from four sources:**
  - live screenshots 01 to 35 of Anton's Claude desktop app (design systems, Settings, token sections): `/Users/antonabyzov/.specwithcode/m4/evidence/design-system-claude-compare-1046/claude/reference.md`;
  - the static spec of the Design System artifact: `/Users/antonabyzov/Projects/github/studio-research-notes/design-system-workspace-2026-10-24/claude-design-system-re.md`;
  - the Claude Design inventory (gallery, canvas, slides): `/Users/antonabyzov/Projects/github/studio-research-notes/design-workspace-2026-10-20/claude-design-inventory.md`, sections 1, 3, 4 and 6;
  - the gap list from the 1046 comparison workflow, when it finishes: `/Users/antonabyzov/.specwithcode/m4/evidence/design-system-claude-compare-1046/gaps-final.md`.

  Claude slides have a slide menu (Duplicate, Add after, Move left/right, Skip, Delete), present keys, and export to PPTX, PDF and Google Slides. How Claude imports a deck is not known from authorized evidence; the inventory lists no import entry.

## Scope

In:

- A scenario matrix covering design creation, boards and slides, run end to end, with each row compared to Claude.
- At least three real decks made through different flows: from scratch, a PowerPoint import, and agent-authored.
- PowerPoint import, the missing flow.
- Fixes for every gap the runs find in boards and slides.
- Headless evidence, review and a pull request.

Out:

- Google Slides export or import, transitions, and real-time co-editing.
- Starting a provider turn on the installed app without a separate go-ahead from Anton.
- Releasing, restarting or updating the live service. The release owner ships; installed acceptance is recorded after their release.
- 1043 and 1049 surfaces (the report viewer, Files and report polish). Those owners keep them.
- Design systems themselves. 1046 owns them, and the S rows below only reference its runs.

## Acceptance Criteria

- [ ] AC-01: Every row of the scenario matrix below is run. Each result is recorded with its steps, a pass or fail verdict, and screenshots in light and dark at 1280 px (plus 360 px for layout rows), under `/Users/antonabyzov/.specwithcode/m4/evidence/design-boards-slides-1051/`.
- [ ] AC-02: At least three actual decks exist, each made through a different flow: from scratch (SL-01), imported from PowerPoint (SL-02), and authored by an agent (SL-03). Each deck opens, presents (keys and Presenter view), and exports to PDF and PowerPoint. A python-pptx read-back of each export matches the deck's slide count and text.
- [ ] AC-03: "Import PowerPoint…" turns a `.pptx` into a slides document:
  - titles and body text become editable text, simple shapes become shapes, pictures become design assets, and notes become speaker notes;
  - anything the import cannot keep is listed for each slide;
  - `.pptm` and other macro or unknown files are refused;
  - the zip, entry and image size limits are enforced, as are the XML entity rules;
  - the import runs on the server behind a capability flag, and older servers hide the entry.
- [ ] AC-04: The two other create options pass. Design (blank canvas, C-01) and Design from code (C-02) each run from "Make something new" in the Playground and in a project. C-02 starts a bound thread with its brief; no provider turn is started unless Anton approves one.
- [ ] AC-05: Board rows B-01 to B-08 pass, or each failure becomes a gap that is fixed and run again.
- [ ] AC-06: Each row names its Claude reference (a live screenshot or a static spec row) and a verdict: match, gap fixed, local equivalent, or left out (with the reason).
- [ ] AC-07: Safety. All runs use a private server or a fixture, headless (headless:true, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never). Nothing touches statev2.sqlite, the live service is not restarted, and EasyChamp is used read-only (writes go to the copy at `/tmp/swc-1046-compare/repos/ec-uikit`).
- [ ] AC-08: Installed acceptance is recorded separately, after the release owner ships. Until then the installed app (1.0.75) gets only read-only checks, plus test content in the Playground through the design tools that agents already have.

## Scenario matrix

**Where each row runs:**
- **P:** a private server built from the branch. It is started with `/tmp/swc-1046-compare/start-server.sh <home> <port>` (providers disabled, its own home, stopped by PID) and has the EasyChamp UI Kit copy added as a project.
- **I:** the installed app. It gets read-only checks only, plus Playground content through the `design_*` tools.
- **F:** a headless fixture.

**Claude reference keys:**
- **L-nn:** a live screenshot under `/Users/antonabyzov/.specwithcode/m4/evidence/design-system-claude-compare-1046/claude/`.
- **RE-x.y:** a row of the static spec.
- **INV-n:** a section of the inventory.

### Create options ("Make something new")

| ID | Flow | Steps | Where | Claude reference | Pass when |
| --- | --- | --- | --- | --- | --- |
| C-01 | Design, blank | Playground: create with the Matchday system; add a frame, text and a rectangle; apply token colors and fonts; reload. Then repeat from the project board. | P | INV-1 "Design (New)" card, INV-3 | It saves, reloads unchanged, uses the chosen system, and the project copy lands in the repository's `.specweave/design` |
| C-02 | Design from code | From "Make something new" and from the project board: pick the project and a brief. | P | INV-1 "Design in codebase", INV-7 | A design bound to a new thread exists with the brief as the first message. With providers disabled the thread says why it cannot start; no turn is run |
| C-03 | Design system | Every New design system option (1046 rows S1 to S8). | P | L-01 to L-35, RE-13 | As in 1046 |
| C-04 | Slides | Entry into SL-01. | P | INV-6 "Slides (New)" | The dialog matches the other create dialogs (owner, system, title) |

### Boards (design canvas)

| ID | Flow | Steps | Where | Claude reference | Pass when |
| --- | --- | --- | --- | --- | --- |
| B-01 | Basics | Frames, shapes, text and images; select, move, resize, layers, undo and redo, autosave, reload. | P | INV-3 | No lost edit; the save state reads Saved |
| B-02 | Pages | Add, rename, reorder and delete pages; several frames on one page. | P | INV-4 | The order and names survive a reload |
| B-03 | Design system binding | Switch the system, use the reuse chip, insert a component from the system. | P | INV-2, RE-13.15 | Tokens re-resolve on switch; the component renders |
| B-04 | Comments and versions | Add, reply to and resolve a comment; save a named version; restore it. | P | INV-5 | The history lists the version and restore brings the content back |
| B-05 | Export | PNG, SVG and HTML of a frame; PDF of all frames. | P | INV-4 | The files open; the PDF has one page per frame |
| B-06 | Implement frame | "Implement" on a frame starts a bound thread. | P | INV-7 | The thread is created with its handoff text; no turn runs |
| B-07 | Project board | More > Design; Add from Playground; Connect to a project (1046 AC-01 to AC-03). | P | INV-9 | Scoped creates; the move keeps id, history and versions |
| B-08 | Share | The Share dialog on a Playground design and on a project design. | P | INV-5 | It states what is local and offers the local equivalent |

### Slides (presentation)

| ID | Flow | Steps | Where | Claude reference | Pass when |
| --- | --- | --- | --- | --- | --- |
| SL-01 | Deck from scratch, "Matchday launch" | New slides (Playground, Matchday system). Five slides from the layouts: title, section, title and body, two columns, quote. Add notes on each. Reorder by drag and by keyboard. Use the slide menu: Duplicate, Add after, Move, Skip, Delete. | P, then I for the read-only view | INV-6 | All actions work. Present: arrows, Space, Page Up/Down, Home/End, 1-9, F, Esc; skipped slides are left out; the Presenter view shows current, next, notes and a timer. PDF and PPTX export; the read-back matches |
| SL-02 | Deck imported from PowerPoint | Import two decks: (a) SL-01's own PPTX export, a round trip; (b) a 6-slide third-party deck made with python-pptx, with a title, bullets, a two-column layout, an image, a shape and notes. | P | not known from authorized evidence; local feature | Slide count, text, notes and images arrive; unsupported parts are listed; the result can be edited, presented and exported |
| SL-03 | Deck authored by an agent | Through `design_create` (kind slides) and `design_apply` only: a 4-slide "EasyChamp season recap" brief using the Matchday system. | P through the MCP handlers; I in the Playground through this thread's design tools, titled "Test: …" | INV-6 `/slides <brief>` | The deck opens in the editor with a working rail and notes; the export read-back matches |
| SL-04 | Project deck | New slides from the project board. Then connect an SL-01 copy from the Playground to the project. | P | INV-9 | The deck lands in the repository; slides and notes survive the move |
| SL-05 | Narrow and dark | The SL-01 editor and Present at 360 px and 768 px, light and dark, and at 200% zoom. | P | — | The rail collapses cleanly; nothing overlaps; contrast is AA |

### Design systems (from 1046, referenced here)

Rows S1 to S8 are run by the 1046 comparison workflow and recorded in `/Users/antonabyzov/.specwithcode/m4/evidence/design-system-claude-compare-1046/ours/systems.md`.

## Approach

- **Branch and worktree.** Branch `feat/1051-boards-slides` from `feat/1046-design-workspace`, in a new worktree `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-1051-boards-slides` with an offline pnpm install. Never use git stash.
- **PowerPoint import (AC-03).**
  - A new `apps/server/src/design/import/pptxImport.ts` reads the deck with the zip and XML parsers already in the tree; `pptx.ts` and `sheets.ts` show which are present.
  - Limits: 50 MB per file, 2,000 zip entries, 200 MB unpacked, 200 slides (the design page limit), 10 MB per picture (the asset store limit), and per XML part 16 MB, 500,000 elements and 256 levels. DTDs and external entities are refused.
  - It maps `p:sp` text bodies to text nodes, `a:prstGeom` shapes to shapes, and `p:pic` to assets through the existing asset store. Notes slides become speaker notes.
  - Contract: an optional `design.importDeck` RPC behind a `designDeckImport` capability, using the `createEnvironmentRpcCommand` and CLIENT_GUARDED_RPC_SCOPES pattern.
  - Web: "Import PowerPoint…" in the New slides dialog and in "Make something new" under Slides.
- **Scenario runner.** `scripts/studio-verify/design-boards-slides.mjs` drives the matrix on a private server, using the launcher and sign-in recipe in `/tmp/swc-1046-compare/README.md`. It writes `matrix.json` and screenshots, and checks PPTX read-backs with python-pptx in its own folder.
- **Gaps.** Board and slide gaps from `gaps-final.md` are fixed in this branch. Design-system gaps stay on 1046.
- **Review.** A fresh-context review is delegated to `claudeAgent` / `claude-fable-5-1`, which is in the live catalog: usage 64% observed October 24, 2026 at 3:20 AM EDT, resetting at 10:00 AM EDT. Lanes with a stronger model rule keep Opus 5.5.

## Decisions

### Asked

- D-01: Three decks through different flows, two other create options, compared with Claude (Anton, October 24, 2026).

### Defaulted

- D-02: The import flow is a deterministic PowerPoint import, because no authorized evidence shows how Claude imports. Agent rebuilding stays SL-03.
- D-03: No provider turn on the installed app. The agent-authored deck uses the design tools directly.
- D-04: The release owner ships. This increment delivers a PR and coordinates with them; it never races them.

### Open

- none

## Tasks

### T-01 Scenario matrix, Claude references and environment
- AC: AC-01, AC-06 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1051-design-boards-and-slides-claude-parity/spec.md, /Users/antonabyzov/.specwithcode/m4/evidence/design-boards-slides-1051/scenario-matrix.md | Test: matrix lists C, B, SL and S rows with Claude references

### T-02 Import PowerPoint into slides
- AC: AC-02, AC-03, AC-07 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-1051-boards-slides/apps/server/src/design/import, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-1051-boards-slides/packages/contracts/src/design.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-1051-boards-slides/apps/web/src/components/design/gallery | Test: vp test run apps/server/src/design/import apps/web/src/components/design/gallery; round trip of an exported deck

### T-03 Fix board and slide gaps from the comparison
- AC: AC-05, AC-06 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-1051-boards-slides/apps/web/src/components/design/editor, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-1051-boards-slides/apps/web/src/components/design/slides | Test: vp test run apps/web/src/components/design

### T-04 Private-server scenario runner and full run
- AC: AC-01, AC-02, AC-04, AC-05, AC-07 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-1051-boards-slides/scripts/studio-verify/design-boards-slides.mjs, /Users/antonabyzov/.specwithcode/m4/evidence/design-boards-slides-1051 | Test: runner exits 0 with every row recorded; headless true, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never

### T-05 Installed-app read-only checks and Playground test decks
- AC: AC-02, AC-08 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/design-boards-slides-1051/installed | Test: design_list shows the "Test:" decks; read-only headless views; no service restart

### T-06 Fresh-context review (claude-fable-5-1) and fixes
- AC: AC-03, AC-07 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/design-boards-slides-1051/review.md | Test: findings fixed or deferred with reasons

### T-07 PR, exact-head CI and release coordination
- AC: AC-08 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/design-boards-slides-1051 | Test: gh pr checks on the exact head; the release owner is told the PR and heads

### T-08 Close 0975 with the slides evidence
- AC: AC-02 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0975-design-slides/ledger.jsonl | Test: specweave verify 0975; review; specweave complete 0975

### T-09 Verify and close 1051
- AC: all | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1051-design-boards-and-slides-claude-parity/ledger.jsonl | Test: specweave verify 1051; fresh-context review; specweave complete 1051
