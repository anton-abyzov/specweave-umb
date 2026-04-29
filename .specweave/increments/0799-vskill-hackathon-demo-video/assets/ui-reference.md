# UI Reference — Real Product Screenshots

> **Authoritative reference for all hackathon-demo Remotion scenes.** When in doubt, MIRROR these. The agents' first pass drew approximations — this corrects them.

Source: `Hackathon Anthropic Skill Studio Full.mov` (4:46), keyframes extracted to `keyframes/frame_NNN.jpg` at 5-second intervals starting at 30s.

---

## SCREEN 1 — vskill Studio (LIGHT theme)

**File reference**: `keyframes/frame_001.jpg`, `frame_010.jpg`, `frame_022.jpg`, `frame_025.jpg`, `frame_048.jpg`

### Top chrome (every Studio screen)
- **Logo**: Orange/red ✷ (sparkle/asterisk) icon + "Skill Studio" text — left edge
- **Project picker**: pill button "● <project-name> ▾" with green dot, opens dropdown listing projects with paths (e.g., "vskill ACTIVE", "specweave-umb", "greet-anton", "vskill-verify", "antonabyzov", "+ Add project")
- **Right cluster** (top-right):
  - 🔍 "Find skills  ⌘K" — search trigger pill, light gray
  - **+ New Skill** — purple button (#7c3aed-ish)
  - "● Claude Code · Claude Opus 4.7" — agent + model badge with green dot
  - 🔔 notification bell with red badge "2"
  - "⌘K" key hint
- Background: white / very light gray (#fafafa)

### Left sidebar (256-280px wide)
- **Agent header**: "● Claude Code (3 · 11 · 50)" — green dot, counts of (project · personal · plugins)
- **Tip card** (dismissible): light yellow/cream — "Claude Code uses your existing session. No API key needed — vskill just runs the official claude binary on your behalf. Learn more"
- **Filter input**: "🔍 Filter skills..." with `/` keyboard hint
- **AVAILABLE (64)** — section header in caps, with caret to collapse/expand
  - **PROJECT (3)** — bookmark icon on right
    - **.CLAUDE (3)** — sub-group label in lighter caps
      - bullet items: greet-anton, obsidian-brain, scout (no version shown for project)
  - **PERSONAL (11)**
    - **CLAUDE-CODE (11)** — sub-group label
      - excalidraw-diagram-generator 1.0.0
      - excalidraw-skill 1.0.0
      - frontend-design 1.0.0
      - gws 1.0.0
      - nanobanana 1.0.0
      - obsidian-brain 1.0.0
      - pptx 1.0.0
      - slack-messaging 1.0.0
      - social-media-posting 1.0.0
      - tax-filing 1.0.0
      - webapp-testing 1.0.0
  - **PLUGINS (58)** — collapsible
    - codex (3) ⋯
      - codex-cli-runtime 1.0.0
      - codex-result-handling 1.0.0
    - sw (47) ⋯
- **AUTHORING (16)** — second section header, caret to collapse
  - **[+ NEW]** orange/coral button on the right of the AUTHORING header
  - **SKILLS (2)**
    - **VSKILL (2)** — sub-group
      - greet-anton 1.0.2 (with green dot)
      - greet-elena 1.0.0 (with bullet)
  - **PLUGINS (14)**
- Footer (bottom): subtle status row "opus  ● Ok" + small icons

### Right pane — empty / default state
- Title centered: "Select a skill to view details"
- Subtitle: "Choose a skill from the sidebar — its frontmatter, filesystem info, and benchmark status will appear here."

### Right pane — skill detail (e.g., hi-anton)
- **Breadcrumbs** (top bar of pane): `hi-anton ▾  /  SKILLS  /  hi-anton`
- **Skill header**:
  - Skill name in large bold ("hi-anton")
  - Subtitle row: "—  hi-anton" with a small icon
  - **v1.0.0** badge on top-right of pane (with subtle border)
- **Install method row**: "INSTALL METHOD  Authored" badge
- **Path row**: `/Users/anton..ts/TestLab/hi-anton/skills/hi-anton` with [Copy] button (light)
- **Tabs** (horizontal, with underline indicator on active): Overview · Edit · **Tests** · Run · Trigger · Versions

### Right pane — Tests tab (eval generation in progress)
- Empty state icon (clipboard with checkmark)
- Title: "No test cases yet"
- Subtitle: "Create test cases to start evaluating your skill"
- Two buttons: **Create Test Case** (dark/black) | **Generating...** (purple, disabled while generating)
- Below: **Progress Log (2)** expandable
  - `● 0s   Reading skill content...`
  - `● +0.0s   Generating unit test cases...`

### Right pane — Versions tab
- Empty state title: "No published versions yet"
- Body: "This skill is local-only — the version history shown here is sourced from verified-skill.com. Submit your skill to start tracking versions and share it with others."
- Centered button: **[Submit on verified-skill.com]** (dark)

### Right pane — Available Updates view
- Title: "**Available Updates (N)**"
- Right-aligned actions: "Refresh" (text link) + **[Update Selected (0)]** (gray, disabled when nothing selected)
- "Select All" sub-action
- Update row card:
  - Skill name (bold) + **patch** badge (light gray pill, lowercase)
  - Version transition: `1.0.0 → 1.0.1` in muted text below the name
  - Far right: "View Changes" link + **[Update]** button (dark/black)

### Bottom-right toast
- Light gray/white pill: "● 1 update available  [View Updates]" (purple link/button) "✕" close

---

## SCREEN 1b — Studio: Create-a-skill modal (Step 1 of 2)

**File reference**: `keyframes/frame_015.jpg`

- Modal overlay: dim background
- Modal card: white, ~520px wide, soft shadow
- Header: "**Create a skill**" left, "Step 1 of 2" right (muted text)
- Three option cards stacked vertically:
  1. **Standalone skill** — SELECTED (light pink background tint, salmon left border)
     - icon: terra-cotta document
     - subtitle (small caps): "A SINGLE SKILL IN THIS PROJECT"
     - body: "Lives at <project>/skills/<name>/SKILL.md. Works with every agent."
  2. **Add to existing plugin** — DISABLED (faded)
     - icon: gray puzzle piece
     - subtitle: "NO PLUGIN SOURCES IN THIS PROJECT YET"
     - body: "Appends a skill to an existing <plugin>/.claude-plugin/plugin.json source."
  3. **New plugin**
     - icon: terra-cotta puzzle stack
     - subtitle: "BUNDLES ONE OR MORE SKILLS FOR DISTRIBUTION"
     - body: "Scaffolds <plugin>/.claude-plugin/plugin.json and its first skill."
- Footer right: "Cancel" (text) + **[Continue →]** (dark/black button)

---

## SCREEN 1c — Studio: Create a New Skill form (Step 2, AI-Assisted)

**File reference**: `keyframes/frame_020.jpg`

- Breadcrumb top: "Skills  /  New Skill"
- Title row: "**Create a New Skill**" + small `[STANDALONE]` tag (muted)
- Subtitle: "Define your skill's metadata, content, and placement"
- Right of header, tab toggle: **AI-Assisted** (left, SELECTED, purple bg) / Manual (right, light)
- **Authoring engine** label
  - Stacked cards:
    - "VSkill skill-builder" — "not installed" muted — [Install] button right
    - "**Anthropic skill-creator**" — "installed" — SELECTED (light blue/lavender bg, blue left border)
    - "No engine — generate raw" — "always available"
- **Describe Your Skill** section:
  - Large textarea (~200px tall) with example/typed text "Before every user prompt, it should say "HI Enter"."
  - Hint below: "Cmd+Enter to generate"
- **SKILL.MD PREVIEW** panel on the right (~360px) showing:
  - YAML frontmatter:
    ```
    ---
    description: "Before every user prompt, it
    should say \"HI Enter\"."
    ---
    # /hi-anton
    You are a helpful assist...
    ```
- **Source Model** section (horizontal):
  - Header: "Source Model  [DEFAULT]"
  - Two select dropdowns: PROVIDER ("Use current Claude Code session") | MODEL ("Claude Sonnet 4.6")
  - Disclaimer: "Uses your logged-in Claude Code session — your existing CLI session handles quota. No API key needed. Overflow runs at standard API rates if extra usage is enabled in your account settings."  *(small muted text)*
  - "Enable with usage »" link
- Footer:
  - **[✨ Generate Skill]** purple button (with sparkle icon)
  - "Cancel" (text)

---

## SCREEN 2 — verifiedskill.com (DARK theme)

**File reference**: `keyframes/frame_030.jpg` (queue), `frame_032.jpg` (submission detail)

### Top nav (every page)
- Yellow/amber bar at very top: "⭐ If you find vskill useful, give it a star on GitHub →"
- Logo bar:
  - Left: "vskill ✶" wordmark (white text)
  - Right cluster: "✋ anton-abyzov", "Logout", "/", "⌘K"
- Main nav (horizontal): Skills · Studio · **Submit** (active) · Publishers · Trust · Queue · Docs · Marketplace · 〔GitHub octocat〕
- All on a near-black bg (#0a0a0a) with very thin borders

### Submit / Queue page (frame_030)
- Page header: "**— Submission Queue —**"
- 6 stat cards across the top (white text on dark, thin border):
  - **TOTAL** 112,842 (with green up-tick)
  - **ACTIVE** 94 (cyan)
  - **PUBLISHED** 107,808 (green)
  - **REJECTED** 4,934
  - **BLOCKED** 6
  - **AVG SCORE** 97.0
- Status row: "● SSE polling  [Counters refreshing...]"
- Right-aligned: "Last updated: 7:20:31 PM"
- Search: "Search by skill name, repo, or ID"
- Table:
  - Cols: # | SKILL NAME | REPO | STATE | SCORE | LAST ACTIVITY | ACTIONS
  - Row: `#1 | appstore | anton-abyzov/vskill | [Tier 1 Scanning] | -- | 2h ago`
  - State pill is small caps amber/orange-bordered
  - Many rows scrolling: tax-filing, frontend-design, tournament-manager, figma-connect, greet-anton, etc.

### Submission detail page (frame_032)
- URL bar visible: `verified-skill.com/submit/sub_ae82f0d2...`
- "<< Back to queue" link (top-left)
- Section title: "**— Submission —**"
- Key/value rows:
  - Skill: hi-anton
  - Repo: anton-abyzov/hi-anton (link)
  - Skill File: skills/hi-anton/SKILL.md (link)
  - ID: sub_ae82f0d2-4bd7-44be-a250-1c03bbe6b5e0 (monospace)
- "**Status: Published**"
- **Pipeline timeline** (vertical, with branch/tree connectors and timestamps right-aligned):
  - ├── Received  (19:20:27)
  -      submission_created
  - ├── Tier 1 Scanning  (19:21:00)
  -      Claimed by VM scanner
  - ├── Auto-Approved  (19:21:19)
  -      LLM approved. Score: 90/100
  - └── Published  (19:21:19)
  -      Skill published to verified registry
- **SCAN RESULTS** card (bordered):
  - Verdict: **PASS** (green)
  - Score: **90/100**
  - Findings: 0
  - Patterns: 52
  - 16480ms
- **FINDINGS (0)** section: "No line-level findings — this submission was rejected before/outside the scanner pipeline."
- **LLM ANALYSIS**:
  - **Intent Analysis** body
  - **Scope Alignment** body

---

## SCREEN 3 — macOS Terminal (cloud sky background)

**File reference**: `keyframes/frame_040.jpg` (initial), `frame_042.jpg` (with bug)

- macOS menubar at top: "🍎 Terminal  Shell  Edit  View  Window  Help  ... 🔔 ☀ 🔋 🔍 ☁  Sun Apr 26 10:13 PM"
- Wallpaper: realistic clouds + sky (light blue-gray)
- Terminal window:
  - Title bar: traffic lights (red/yellow/green dots) + title text "hi-anton — ✷ Claude Code — mcp-server-darwin-arm64 · claude — 129×40"
  - Two tabs visible: previous tab + active "✷ Claude Code — mcp-server-..." tab
  - Window has subtle translucency
- Body content:
  - Shell prompt: `(base) antonabyzov@Mac-1255 hi-anton % claude`
  - Welcome banner (boxed with horizontal rules):
    - Title row: "─ Claude Code v2.1.119 ─"
    - Left col: "Welcome back Anton!" + ASCII robot art (terra-cotta colored) + "Opus 4.7 (1M context) · Claude Max · anton.abyzov@gmail.com's Organization · ~/Projects/TestLab/hi-anton"
    - Right col: "Tips for getting started" / "Run /init to create a CLAUDE.md file with instructions for Claude" / "Recent activity / No recent activity"
  - Below banner: `/remote-control is active · Code in CLI or at https://claude.ai/code/session_01MqtyzhX88RTZAw9y3bQ5uE`
  - Prompt: `> ` cursor blinking
  - Status row at bottom: `▸▸ bypass permissions on (shift+tab to cycle)        ● xhigh · /effort`

### Bug-state additions (frame_042)
- User typed (highlighted block): `What is two plus two?`
- Reply (no markup, plain monospace):
  - `HI Enter`
  - `Four.`
- New `>` prompt with cursor

### Working-state (post-update, scene 11)
- User typed: `Anthropic skills are wonderful, aren't they?`
- Reply:
  - `Hi Anton.`
  - `Yes — they are.`

---

## Color tokens for mirroring (LIGHT Studio)

Add these to `scenes/hackathon/uiTokens.ts` (NEW file — do NOT modify `constants.ts`):

```ts
export const STUDIO_LIGHT = {
  bg: "#fafafa",
  surface: "#ffffff",
  border: "#e5e7eb",        // gray-200
  borderSoft: "#f3f4f6",    // gray-100
  text: "#111827",          // gray-900
  textMuted: "#6b7280",     // gray-500
  textSubtle: "#9ca3af",    // gray-400
  accentOrange: "#ea580c",  // orange-600 (logo)
  accentPurple: "#7c3aed",  // violet-600 (New Skill, AI-Assisted)
  accentDark: "#111827",    // dark buttons
  greenDot: "#22c55e",
  yellowTip: "#fef3c7",     // yellow-100 (tip card bg)
  yellowTipBorder: "#fde68a",
  pillBg: "#f3f4f6",
  pillText: "#374151",
  patchBadgeBg: "#f3f4f6",
  toastBg: "#ffffff",
  toastShadow: "0 4px 12px rgba(0,0,0,0.08)",
} as const;

export const VERIFIED_DARK = {
  bg: "#0a0a0a",
  surface: "#111111",
  border: "#262626",
  text: "#ffffff",
  textMuted: "#a3a3a3",
  pass: "#22c55e",
  fail: "#ef4444",
  link: "#60a5fa",
  amberBar: "#f59e0b",
} as const;

export const TERMINAL_BG = {
  cloudGradient: "linear-gradient(180deg, #d4def0 0%, #c8d6e8 50%, #d4def0 100%)",
  windowBg: "rgba(15, 15, 15, 0.92)",
  windowBorder: "rgba(255,255,255,0.08)",
  text: "#e5e5e5",
  prompt: "#22c55e",
  banner: "#d97757",  // terra-cotta for Claude Code branding
} as const;
```

---

## Scene-by-scene which screen + which frame to mirror

| Scene | Screen | Reference frames |
|---|---|---|
| 01 HookProblem | abstract drift visual (3 mini Studios with version pills) | combine 3 versions of frame_010 with conflicting versions |
| 02 BrandReveal | Studio LIGHT brand reveal (logo + product name) | frame_001, frame_010 |
| 03 BrowseGrid | Studio LIGHT main view: full sidebar + Cmd+K search overlay with security-scanned results | frame_005 (search), frame_001 (sidebar) |
| 04 UpdateButton | Studio LIGHT updates page + bottom toast | frame_010, frame_048 |
| 05 AuthorCreate | Step 1 modal → Step 2 form (AI-Assisted active, textarea, Generate, SKILL.MD preview) | frame_015, frame_020 |
| 06 AuthorEvals | Studio Tests tab with progress log | frame_022 |
| 07 AuthorPublish | verifiedskill.com submission detail page (DARK) — pipeline → PASS | frame_030 (queue), frame_032 (detail) |
| 08 ConsumeInstall | Studio Cmd+K search → install scope picker | frame_005, custom scope picker per transcript |
| 09 ConsumeBugSurface | Terminal with HI Enter bug | frame_042 |
| 10 AuthorFix | Studio Edit tab (SKILL.md diff) + terminal commit/push | frame_025-ish + custom |
| 11 ConsumeSyncUpdate | Studio update toast → Terminal works | frame_048 + custom terminal |
| 12 Outro | Brand finale (light, references Studio look) | abstract |

---

**KEY DIRECTIVE**: All Studio scenes must use the LIGHT theme tokens. The verifiedskill.com scene must use DARK. Terminal scene must show macOS Terminal with sky bg + Claude Code v2.1.119 banner.
