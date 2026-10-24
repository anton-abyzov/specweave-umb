# 1038 Highlight code output by language

## Problem
Activity commands are syntax colored, but React/TSX source in their Output is plain. V2ItemInspector passes only text into ToolCodePanel. Existing shared Shiki WASM highlighting must receive reliable language context without coloring mixed logs as source.

## Scope
In: language resolution, output metadata plumbing, shared code renderer fallback and byte preservation, focused regression and headless visual checks. Out: 1011 activity density/diffs, 1035 report redesign, settings redesign, releases and service restarts.

## Acceptance Criteria
- [ ] AC-01: Explicit supported language and single-source filename metadata select the correct grammar, including TSX, JSX, TypeScript, JavaScript, Python, Rust, Go, Java, C/C++, shell, JSON, YAML, TOML, HTML, CSS, SQL and Markdown.
- [ ] AC-02: Single-file read commands may supply a source extension only when unambiguous; pipelines, compound commands, search results, multiple-file output and ordinary logs remain plain unless explicit structured source blocks identify their boundaries.
- [ ] AC-03: Conservative bounded inference recognizes strongly evidenced standalone code/config; unknown or ambiguous content safely remains plain. No per-token whole-output language guessing.
- [ ] AC-04: Copy returns exact original bytes including CRLF, tabs and trailing newlines. Existing ANSI presentation, wrap, expansion and scrolling remain functional.
- [ ] AC-05: Partial streamed output renders safely without stale text or expensive repeated full-output guessing. Large output uses a documented bound and readable fallback; a 1 MiB fixture remains interactive.
- [ ] AC-06: Both light and dark themes use existing shared highlighter themes; token readability, TSX and other language colors, mixed/plain logs, streaming and large output have headless screenshots and interaction assertions.
- [ ] AC-07: Focused regression checks, relevant web production build, fresh independent review and exact PR head checks pass. Delivery distinguishes source/CI proof from installed acceptance.

## Approach
Reuse @pierre/diffs shared Shiki WASM singleton through apps/web/src/lib/syntaxHighlighting.ts and HighlightedTokens. Inspect toolOutputPresentation, V2ItemInspector, ChatMarkdown and client-runtime item-detail before choosing the narrowest metadata adapter. Resolve explicit language, then trustworthy single-source path, then bounded conservative inference. ANSI/log evidence wins over guessed source. Keep original text separate from presentation. Cap tokenization and memoize stable context; use existing incremental infrastructure where appropriate. Unsupported grammars and errors return readable plain text.

Coordinate 1011 and 1035 before overlapping files. Current thread is bound to the SpecWeave CLI repository, so obtain an app-managed worktree binding to the approved app repository before implementation; do not create an unregistered checkout or change another owner's branch.

## Decisions
### Asked
- None. Scope and headless verification supplied by the user.
### Defaulted
- Prefer false negatives to coloring mixed output as a single language.
- Reuse existing highlighter and theme mapping; no new highlighting library.
- Large uncertain output remains plain rather than blocking the UI.
### Open
- None.

## Tasks

### T-01 Resolve language from trusted context and bounded inference
- AC: AC-01, AC-02, AC-03 | Files: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/apps/web/src/lib/outputLanguage.ts, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/apps/web/src/lib/outputLanguage.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/lib/outputLanguage.test.ts

### T-02 Integrate output and shared renderers without losing bytes or responsiveness
- AC: AC-01, AC-04, AC-05 | Files: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/toolOutputPresentation.tsx, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/V2ItemInspector.tsx, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/HighlightedTokens.tsx, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/apps/web/src/lib/syntaxHighlighting.ts, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/toolOutputPresentation.test.tsx, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/apps/web/src/lib/syntaxHighlighting.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/chat/toolOutputPresentation.test.tsx apps/web/src/lib/syntaxHighlighting.test.ts

### T-03 Prove language rendering and interactions headlessly
- AC: AC-02, AC-04, AC-05, AC-06 | Files: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/apps/web/tests/output-highlighting/main.tsx, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/apps/web/tests/output-highlighting/index.html, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/apps/web/tests/output-highlighting/vite.config.ts, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/apps/web/tests/output-highlighting/verify.mjs | Test: PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never node apps/web/tests/output-highlighting/verify.mjs

### T-04 Verify and close 1038
- AC: AC-07 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1038-highlight-code-output-by-language/reports/validation.md | Test: npx --yes specweave@3.1.7 verify 1038

Task file paths describe the approved source repository and will be updated to the bound owned worktree before claiming implementation. Every browser invocation uses explicit headless: true; reports open: never. Record tasks through the ledger, obtain fresh-context review, then complete 1038. Deliver PR and retained screenshots to Complete screenshot sessions; no separate release.
