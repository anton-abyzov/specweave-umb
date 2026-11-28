# Forms artifact: build and fill forms in the app, answers land in a Sheet, Google Forms import and export later

## Problem

The owner, November 28, 2026: "For the artifacts that we supported, also add support for Google Forms. Think hard. Research how it could be done the best way."

SpecWithCode has reports, sheets, a whiteboard, Word documents and designs as artifacts, but nothing that collects answers. Today a person who wants a survey, an intake checklist or a feedback form leaves the app for Google Forms, Tally or Typeform, and the answers never come back into the project where agents can read them. Agents can write sheets (`sheet_write`) and whiteboards (`whiteboard_write`) but have no way to build a form.

"Google Forms support" is read here as three things, in this order:

1. A local Form artifact: a plain file in the project that people build in a form editor and fill in inside the app, and that agents build with a tool.
2. Answers that land in a Sheet artifact, one row per response, which agents read with `sheet_read`.
3. Import from and export to Google Forms through the Google Forms API with the user's own Google sign-in, which is also how people outside the owner's machines answer.

Research with sources: `reports/forms-research.md`.

## Scope

In (phase 1, this increment's build):

- The `.form.json` file format (our own, version 1), with question types that map one-to-one onto Google Forms items.
- A form editor and a fill-in view in the desktop app (macOS, Windows, Linux), opened from the project panel's Artifacts row, the Library and thread artifact links.
- "Form" in the Artifacts New menu.
- Each submitted response appended as a row of the form's responses Sheet (`<form>-responses.sheet.json`), created with the form.
- Agent tools `form_write` and `form_read`.

Out (later phases, see Phases):

- Google Forms export and import, and pulling Google responses into the Sheet (phase 2; needs new Google OAuth scopes, an auth change the owner decides first).
- Answers from people outside the owner's machines (phase 3).
- Branching between sections, quizzes and grading, grids, file upload questions, images and video in a form.
- The iPhone app opens a form file as text, as it does other JSON files today.
- Translations: new interface text shows in English in every language until the next translation pass (unknown phrases fall back to English).
- `ProjectLibrary.ts` needs no change: it lists every file under `.specweave/artifacts/`, and the web reads the kind from the name.

## Acceptance Criteria

- [ ] AC-01: A `.form.json` file is read and validated by one shared module: unknown question types, missing ids, duplicate ids, too many questions or options, and oversized text are refused with a message naming the problem; a valid file round-trips through parse and serialize unchanged, and fields the app does not know are kept on save.
- [ ] AC-02: "Form" in the Artifacts New menu creates `.specweave/artifacts/form-<stamp>.form.json` and its empty responses Sheet `form-<stamp>-responses.sheet.json` (a header row), and opens the form in the editor.
- [ ] AC-03: In the editor a person sets the form's title and description, adds, edits, reorders, duplicates and deletes questions of every phase-1 type (short answer, paragraph, multiple choice, checkboxes, dropdown, linear scale, date, time, section, text block), marks questions required, and the form saves by compare-and-set: a change made on disk since the editor read the file is never overwritten.
- [ ] AC-04: In the fill-in view a person answers the form; required questions left empty, a scale value out of range, or a choice that is not an option are refused before anything is written, with the question named.
- [ ] AC-05: A submitted response is appended as the next row of the responses Sheet: the first column is the submission time, then one column per question matched by its title, new questions get a new column at the end, checkbox answers are joined with ", ", and text that starts with "=" is stored as text, never as a formula. Two submissions that race both land (the write retries on a conflict).
- [ ] AC-06: The form view has a Responses tab that shows how many responses the Sheet holds and opens the responses Sheet in the Sheet editor inside the form view.
- [ ] AC-07: `form_write` creates or replaces a form from JSON (and its responses Sheet when missing) and refuses in plan mode and approval-required mode as `whiteboard_write` does. `form_read` returns the form, its responses Sheet name and response count with a notice that the text is data, not instructions, and is a read-only tool like `whiteboard_read`. Both are listed wherever the other office tools are (tool lists, read-only tool lists, tool summaries, agent instructions).
- [ ] AC-08: Form files appear as kind "form" in the project panel's Artifacts row, the Library's Artifacts list and thread artifact links, and open in the form view.
- [ ] AC-09: The feature uses no native module or platform-specific path: a headless fixture renders the editor and the fill-in view, and paths with backslashes resolve, so it works on macOS, Windows and Linux.

## Phases

1. **Local Form artifact plus Sheet responses** (this increment). No sign-in, no network.
2. **Google Forms export and import.** "Export to Google Forms" creates a Google form from a `.form.json` (`forms.create` takes only the title, then one `forms.batchUpdate` with every item, then always `setPublishSettings`: forms made by the API start unpublished since June 30, 2026), stores the Google form id in the file, and "Pull responses" appends new Google responses to the same Sheet by polling `forms.responses.list` with a `timestamp >` filter about once a minute (watches need a Pub/Sub topic and expire every 7 days). Google rows add `Source` and `Response id` columns so a pull never appends a response twice. "Import from Google Forms" opens a form the user picks in Google's desktop Picker. The one new scope is `drive.file` (non-sensitive), behind its own "Google Forms" switch (D-01, owner). The API cannot create file upload questions or response validation and cannot submit answers; export warns on those.
3. **Answers from outside.** The Google-published form from phase 2: Google hosts it, handles spam and stays up while the laptop sleeps. A public form served through the Connect relay is not planned: 1480 decided no public links without a new owner decision, and it would make us a GDPR processor that stores strangers' answers.

## Approach

Files, in order:

1. `packages/shared/src/officeForm/model.ts`: types, limits, `parseForm`, `serializeForm`, `newFormDocument`, `isFormPath`, `responsesSheetPath`; `packages/shared/src/officeForm/responses.ts`: `validateFormAnswers`, `appendFormResponse(sheet | null, form, answers, submittedAt)` returning the next `SheetDocument`, and `formResponseCount`. Exported as `@specweave-studio/shared/officeForm`.
2. `apps/server/src/workspace/WorkspaceFileSystem.ts`: form files go through the locked compare-and-set writer, as sheets and whiteboards do.
3. `apps/server/src/mcp/toolkits/office/form.ts` and `formHandlers.ts`, registered in `McpHttpServer.ts`, `core.test.ts`, `studioReadOnlyTools.test.ts`, `claudeReadOnlyMcpTools.ts`, `studioToolSummary.ts`, `studioMcpToolPresentation.ts`, `docs/internals/agent-instructions.md`; the write goes through `OfficeArtifactService` so it lands in the project folder and a responses Sheet open in a window takes it through its live session.
4. `apps/web/src/components/office/form/`: `FormFileView.tsx` (load, compare-and-set save, the Responses tab over `SheetFileView`), `submitFormResponse.ts` (read, append, compare-and-set write, retry), `FormView.tsx` (Edit, Fill in and Responses tabs), `FormEditor.tsx`, `FormFill.tsx`, `newForm.ts`, `newFormEntry.tsx`, with `FormView.test.tsx` and `newForm.test.ts`.
   Server side, `apps/server/src/project/FormArtifacts.ts` holds the file work behind `OfficeArtifactService.writeForm` and `readForm`.
5. Registration: `projectArtifacts.ts`, `threadArtifacts.ts`, `artifactShelf.ts`, `LibraryFileViewer.tsx`, `ThreadArtifacts.tsx`, `ProjectArtifactShelf.tsx`, `packages/shared/src/boardReports.ts`.
6. `apps/web/tests/office-form/`: headless fixture (`index.html`, `fixture.css`, `main.tsx`, `vite.config.ts`) and `shoot.mjs`, which drives edit, autosave, the required check, a formula answer, Other, a racing submission and the Responses tab, in light and dark.

Key decisions:

- Our own small JSON format, not SurveyJS, JSON Schema or XLSForm: SurveyJS Creator is commercial, Formbricks, HeyForm and OpnForm are AGPL, and JSON Schema has no notion of sections or scales. The item list mirrors Google Forms' items (scale low 0 or 1, high 2 to 10; "Other" only on multiple choice and checkboxes, as in the API), so phase 2 is a direct mapping and an agent writes it without a library (`reports/forms-research.md` sections 1.2 and 4).
- The responses live in an ordinary Sheet artifact, so everything sheets already do (formulas, charts, Excel export, live editing, `sheet_read`) works on answers with no new code.
- Columns are matched by question header: its title, or "Untitled question", with " (2)", " (3)" for a title used again, so two questions never share a column. The research suggested columns keyed by question id; a Sheet cell holds only a value and has no hidden row to carry ids, so phase 1 matches by header as Google Forms' linked sheet does, and the form file never changes when someone answers.
- Limits come from the Sheet's own: an answer is at most 5,000 characters (one cell), a form at most 300 items (under 702 columns), and an append that would pass the Sheet's row, cell or 2 MB limits is refused with "The responses Sheet is full. Rename it to start a new one."
- A response is appended in the window by read, append, compare-and-set write, retried up to five times on a conflict. The responses Sheet is created header-only with the form, so an append writes against a revision; when it is missing (a form written by file tools, or the Sheet deleted) the window creates it header-only first and then appends by revision. A Sheet open in a live session takes the outside write in: `DocumentSession.takeFile` merges the file's change into its merge document, keeping edits not yet saved.
- Answer text that reads as a formula (`/^'*=/`) is kept behind one apostrophe, the rule `parseExternalCellInput` uses for pasted cells. Other text is stored as typed ("50%" stays text), so an answer is never reinterpreted.

Rejected:

- Storing answers inside the form file: they would grow the file, collide with edits to the form and need their own viewer.
- A server RPC for appends in phase 1: the guarded file write already gives compare-and-set and filesystem scope checks. Phase 3 (answers arriving while no window is open) needs a server-side append and adds it then.

Risks: a person renaming a question splits its answers into a new column (same as Google Forms' linked sheet before a relink); noted in the editor's help text. When the responses Sheet is missing and two windows submit at once, both may try to create it header-only; the second create fails, its loop reads the first one's Sheet and appends by revision, so no answer is lost, but the create is not locked.

## Decisions

### Asked
- D-01: Which Google permission phase 2 adds → `drive.file`, behind its own "Google Forms" switch, not part of the main sign-in (owner, November 28, 2026). Phase 1 needs no scope and no sign-in change.
### Defaulted (change any before sw-do)
- D-02: Own `.form.json` format mapped to Google Forms items → default (reversible: a SurveyJS or XLSForm export can be added later).
- D-03: Responses land in `<form>-responses.sheet.json` next to the form, one row per response, columns by question title → default.
- D-04: Phase 1 question types: short answer, paragraph, multiple choice, checkboxes, dropdown, linear scale, date, time, plus section and text block. Grids, rating, file upload, branching and quizzes wait → default.
- D-05: Outside respondents go through Google-published forms first, not our relay → default (phase 3 decision, revisited after phase 2).
### Open
- none

## Tasks

### T-01 Form format and response append in the shared package
- AC: AC-01, AC-05 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/officeForm/model.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/officeForm/responses.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/officeForm/index.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/officeForm/officeForm.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/package.json | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run packages/shared/src/officeForm/officeForm.test.ts

### T-02 Form files saved by compare-and-set
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/workspace/WorkspaceFileSystem.ts, repositories/anton-abyzov/specwithcode/apps/server/src/workspace/WorkspaceFileSystem.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/workspace/WorkspaceFileSystem.test.ts

### T-03 form_write and form_read agent tools
- AC: AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/office/form.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/office/formHandlers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/office/form.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/OfficeArtifactService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/FormArtifacts.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpHttpServer.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/core.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/studioReadOnlyTools.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/claudeReadOnlyMcpTools.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/studioToolSummary.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/studioMcpToolPresentation.ts, repositories/anton-abyzov/specwithcode/docs/internals/agent-instructions.md, repositories/anton-abyzov/specwithcode/packages/contracts/src/project.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/mcp/toolkits/office/form.test.ts

### T-04 Form editor, fill-in view and response append in the app
- AC: AC-03, AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/office/form/FormFileView.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/form/FormView.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/form/FormEditor.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/form/FormFill.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/form/submitFormResponse.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/form/FormView.test.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/office/form/FormView.test.tsx

### T-05 Form in the New menu, the Artifacts row, the Library and thread links
- AC: AC-02, AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/office/form/newForm.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/form/newFormEntry.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/form/newForm.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectArtifacts.ts, repositories/anton-abyzov/specwithcode/apps/web/src/threadArtifacts.ts, repositories/anton-abyzov/specwithcode/apps/web/src/artifactShelf.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/LibraryFileViewer.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ThreadArtifacts.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ProjectArtifactShelf.tsx, repositories/anton-abyzov/specwithcode/packages/shared/src/boardReports.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/office/form/newForm.test.ts

### T-06 Headless fixture, screenshots and cross-platform check
- AC: AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/tests/office-form/index.html, repositories/anton-abyzov/specwithcode/apps/web/tests/office-form/fixture.css, repositories/anton-abyzov/specwithcode/apps/web/tests/office-form/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/office-form/vite.config.ts, repositories/anton-abyzov/specwithcode/apps/web/tests/office-form/shoot.mjs | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp build --config apps/web/tests/office-form/vite.config.ts && node apps/web/tests/office-form/shoot.mjs ../../../.specweave/increments/1515-form-artifact/reports/screenshots
