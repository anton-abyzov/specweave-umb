---
increment: 0483-merge-social-skills
title: "Merge social-posts into social-media-posting"
generated_by: sw:test-aware-planner
by_user_story:
  US-001: [T-001, T-002, T-003, T-004, T-005, T-006, T-007, T-009, T-010, T-011, T-012, T-013]
  US-002: [T-008]
  US-003: [T-014]
  US-004: [T-015, T-016]
---

# Tasks: Merge social-posts into social-media-posting

---

## User Story: US-001 - Merge SKILL.md Content

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 12 total, 12 completed

---

### T-001: Merge SKILL.md frontmatter (description + triggers + tags)

**User Story**: US-001
**Satisfies ACs**: AC-US4-03
**Status**: [x] completed

**Test Plan**:
- **Given** the merged SKILL.md at `social-media-posting/SKILL.md`
- **When** I read the `description` field in the frontmatter
- **Then** it contains trigger phrases from both original skills including "social media blast", "cross-post", "share on socials", "spread the word", "promote this on", "quick post", "post with video", "create social content", "repost across socials" from social-posts AND the existing phrases from social-media-posting; AND `version` is NOT present in metadata

**Test Cases**:
1. `grep -c "social media blast" ...SKILL.md` returns >= 1
2. `grep -c "cross-post" ...SKILL.md` returns >= 1
3. `grep -c "share on socials" ...SKILL.md` returns >= 1
4. `grep "version:" ...SKILL.md` returns 0 matches

**Implementation**:
1. Open `repositories/anton-abyzov/vskill/plugins/marketing/skills/social-media-posting/SKILL.md`
2. Expand the `description` field to include all trigger phrases from social-posts: "post about", "social media blast", "cross-post", "share on socials", "spread the word about", "promote this on [platform]", "quick post", "post with video", "create social content for", "repost across socials"
3. Merge `metadata.tags`: union of both tag sets — add `content-creation, copywriting, publishing, facebook` from social-posts
4. Remove `version: 1.1.0` — social-media-posting does not use a version field

---

### T-002: Insert "Before Starting" section (product context file check)

**User Story**: US-001
**Satisfies ACs**: AC-US1-02
**Status**: [x] completed

**Test Plan**:
- **Given** the merged SKILL.md
- **When** I read the "Before Starting" section
- **Then** it instructs checking for `product-marketing-context.md` in the `.claude/` directory first, project root as secondary fallback, and describes the 60/20/15/5% product integration ratio breakdown

**Test Cases**:
1. `grep -c "product-marketing-context.md" ...SKILL.md` returns >= 1
2. `grep -c "\.claude/" ...SKILL.md` returns >= 1
3. `grep -c "60%" ...SKILL.md` returns >= 1
4. YAML frontmatter remains valid: `python3 -c "import yaml; yaml.safe_load(open('SKILL.md').read().split('---')[1])"` exits 0

**Implementation**:
1. After the title/tagline and before `## Core Rules`, insert new `## Before Starting` section
2. Content adapted from social-posts lines 17-35:
   - Check `.claude/product-marketing-context.md` first; project root as secondary fallback
   - Replace "nanobanana" with "nano-banana-pro" in all text
   - Include 60/20/15/5% product integration ratio breakdown
3. Do not duplicate Core Rule #1 (approval gate already covers it)

---

### T-003: Insert Strategic Thinking phase section

**User Story**: US-001
**Satisfies ACs**: AC-US1-01
**Status**: [x] completed

**Test Plan**:
- **Given** the merged SKILL.md
- **When** I read the Strategic Thinking section
- **Then** it appears before content writing in the workflow and includes hook formulas (curiosity gaps, contrarian takes, story hooks, value hooks), psychological angles (social proof, curiosity gap, loss aversion, authority, reciprocity), copy principles, and content pillar guidance

**Test Cases**:
1. `grep -c "curiosity gap" ...SKILL.md` returns >= 1
2. `grep -c "loss aversion" ...SKILL.md` returns >= 1
3. `grep -c "content pillar" ...SKILL.md` returns >= 1
4. `grep -c "contrarian" ...SKILL.md` returns >= 1

**Implementation**:
1. After the Workflow Overview section, insert new `## Strategic Thinking Phase` section
2. Absorb content from social-posts lines 42-59:
   - Hook formula: curiosity gaps, contrarian takes, story hooks, value hooks
   - Psychological angles: social proof, curiosity gap, loss aversion, authority, reciprocity
   - Copy principles: clarity over cleverness, benefits over features, specificity, customer language
   - Content pillar: educational, behind-the-scenes, personal story, industry insight, promotional (<=5%)
3. Product Integration ratios: 60% natural context, 20% pure value, 15% directly about product, 5% personal

---

### T-004: Update Workflow Overview (add CONTEXT, STRATEGY, VIDEO steps)

**User Story**: US-001
**Satisfies ACs**: AC-US1-01
**Status**: [x] completed

**Test Plan**:
- **Given** the merged SKILL.md
- **When** I read the Workflow Overview code block
- **Then** steps include CONTEXT (check product-marketing-context.md), STRATEGY (hook formula, psychological angle), and VIDEO (Veo 3.1/Ken Burns/UGC) with STRATEGY inserted after DEDUP and before CONTENT

**Test Cases**:
1. `grep -c "CONTEXT" ...SKILL.md` returns >= 1
2. `grep -c "STRATEGY" ...SKILL.md` returns >= 1
3. `grep -c "VIDEO" ...SKILL.md` returns >= 1
4. `grep -c "proof screenshots first" ...SKILL.md` returns >= 1

**Implementation**:
1. Replace the existing Workflow Overview code block with the 12-step version from plan.md:
   - 0. DEDUP, 1. CONTEXT (new), 2. STRATEGY (new), 3. ANALYZE, 4. CONTENT (save to generated-assets/copy/), 5. IMAGES (proof screenshots first for X/Threads), 6. VIDEO (new), 7. REVIEW, 8. POST (Chrome-open as last resort), 9. VERIFY, 10. ENGAGE, 11. LOG

---

### T-005: Update Tool Priority table (add Chrome-open fallback column)

**User Story**: US-001
**Satisfies ACs**: AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** the merged SKILL.md tool priority table
- **When** I read the table
- **Then** Chrome-open appears as a last-resort fallback column for all browser-based platforms (Instagram, LinkedIn, Threads, YouTube, Reddit, TikTok, dev.to, Facebook) but NOT for Telegram (API-only) and NOT as a 4th choice for Discord

**Test Cases**:
1. `grep -c "Chrome-open" ...SKILL.md` returns >= 8
2. The Telegram row does NOT contain "Chrome-open"
3. X/Twitter row shows Chrome-open as 4th (Last Resort) choice
4. Table has a 4th column header

**Implementation**:
1. Replace the existing Tool Priority Order table with a 5-column table (Platform, 1st, 2nd, 3rd, 4th Last Resort)
2. Populate per plan.md mapping:
   - X/Twitter: xurl | Puppeteer | Peekaboo | Chrome-open
   - Discord: discord skill | Webhook API | Browser automation | — (no Chrome-open)
   - Telegram: Bot API | — | — | — (API-only, no Chrome-open)
   - Instagram/LinkedIn/Threads/YouTube/Reddit/TikTok/dev.to/Facebook: Puppeteer | Peekaboo | Chrome-open | —

---

### T-006: Add direct Gemini API as image generation fallback

**User Story**: US-001
**Satisfies ACs**: AC-US1-03
**Status**: [x] completed

**Test Plan**:
- **Given** the merged SKILL.md image generation section
- **When** I read it
- **Then** the direct Gemini API Python code block appears labeled as "Fallback when nano-banana-pro skill is not installed" with model `gemini-3-pro-image-preview`

**Test Cases**:
1. `grep -c "gemini-3-pro-image-preview" ...SKILL.md` returns >= 1
2. `grep -c "GEMINI_API_KEY" ...SKILL.md` returns >= 1
3. `grep -c "Fallback" ...SKILL.md` returns >= 1

**Implementation**:
1. Under `## Image Generation with Nano Banana Pro`, after existing content, add subsection `### Fallback: Direct Gemini API (when nano-banana-pro is not installed)`
2. Insert the Python code block from social-posts lines 91-113 (direct API call pattern)
3. Keep nano-banana-pro as the primary/preferred method; direct API is clearly labeled as fallback

---

### T-007: Add Pillow carousel compositing technique

**User Story**: US-001
**Satisfies ACs**: AC-US1-03
**Status**: [x] completed

**Test Plan**:
- **Given** the merged SKILL.md Carousels subsection
- **When** I read it
- **Then** it includes the Pillow (PIL) carousel compositing technique with the Python code block for dark gradient overlay and text compositing

**Test Cases**:
1. `grep -c "from PIL import" ...SKILL.md` returns >= 1
2. `grep -c "dark gradient" ...SKILL.md` returns >= 1
3. `grep -c "Image.alpha_composite" ...SKILL.md` returns >= 1

**Implementation**:
1. Under `### Carousels (Instagram/TikTok)`, after the existing slide grid content
2. Add `#### Carousel Text Compositing (Pillow)` subsection
3. Insert content from social-posts lines 127-148: steps and Python code block with PIL imports, overlay drawing loop, alpha composite

---

### T-008: Add Proof Screenshots section (X/Twitter and Threads first-image requirement)

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** the merged SKILL.md
- **When** I read the Proof Screenshots section
- **Then** it states: (1) first image for X/Twitter and Threads MUST be a proof screenshot; (2) if no proof screenshot available, ask user first; (3) abstract topics fall back to data visualization; (4) NEVER generate fake/mock terminal screenshots; (5) never block the posting workflow over absent proof; (6) guidance on creating good proof screenshots

**Test Cases**:
1. `grep -ic "proof screenshot" ...SKILL.md` returns >= 4
2. `grep -ic "NEVER.*fake\|fake.*terminal\|mock.*terminal" ...SKILL.md` returns >= 1
3. `grep -c "abstract" ...SKILL.md` returns >= 1
4. `grep -ic "never block" ...SKILL.md` returns >= 1

**Implementation**:
1. After Image Generation section and before Video Generation, insert new `## Proof Screenshots (X/Twitter and Threads)` section
2. Include all required rules:
   - First image on X/Twitter and Threads MUST be a proof screenshot (terminal output, metrics dashboard, before/after comparison, code with results, error stories)
   - If no proof screenshot: ask user to provide one first
   - Abstract topics fallback: data visualization or infographic-style AI art
   - Hard prohibition: NEVER generate mock or fake terminal screenshots
   - Non-blocking: never block the posting workflow over absence of a proof screenshot
3. Creation guide: clean terminal with visible output, cropped metrics dashboards, annotated before/after comparisons

---

### T-009: Insert Video Generation section (Veo 3.1 + Ken Burns + UGC)

**User Story**: US-001
**Satisfies ACs**: AC-US1-03
**Status**: [x] completed

**Test Plan**:
- **Given** the merged SKILL.md
- **When** I read the Video Generation section
- **Then** Veo 3.1 (Option A) is documented with model `veo-3.1-generate-preview`, full API endpoint, poll loop, ffmpeg upscale + text overlay, and crossfade concatenation; Ken Burns fallback (Option B) with ffmpeg zoompan is present; UGC script (Option C) with 4-phase structure is present

**Test Cases**:
1. `grep -c "veo-3.1-generate-preview" ...SKILL.md` returns >= 1
2. `grep -c "Ken Burns" ...SKILL.md` returns >= 1
3. `grep -c "UGC" ...SKILL.md` returns >= 1
4. `grep -c "zoompan" ...SKILL.md` returns >= 1
5. `grep -c "xfade" ...SKILL.md` returns >= 1

**Implementation**:
1. After the Proof Screenshots section, insert new `## Video Generation` section
2. Absorb content wholesale from social-posts lines 158-272:
   - Option A: Veo 3.1 (full API, polling loop, ffmpeg upscale + text, crossfade)
   - Option B: Ken Burns zoompan fallback
   - Option C: UGC filming script (hook/setup/value/CTA)
3. Preserve `durationSeconds` note (must be number not string) and download URL `&key=API_KEY` note

---

### T-010: Add per-platform copy file output subsection (all 11 platforms)

**User Story**: US-001
**Satisfies ACs**: AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** the merged SKILL.md
- **When** I read the copy output subsection
- **Then** per-platform copy files are saved to `generated-assets/copy/*.txt` for all 11 platforms including reddit.txt, devto.txt, discord.txt, telegram.txt, youtube.txt (the 5 new beyond what social-posts had)

**Test Cases**:
1. `grep -c "generated-assets/copy/" ...SKILL.md` returns >= 1
2. `grep -c "reddit.txt" ...SKILL.md` returns >= 1
3. `grep -c "discord.txt" ...SKILL.md` returns >= 1
4. `grep -c "telegram.txt" ...SKILL.md` returns >= 1
5. `grep -c "youtube.txt" ...SKILL.md` returns >= 1

**Implementation**:
1. Under `### Content Adaptation`, add new subsection `#### Copy File Output`
2. List all 11 platform files: linkedin.txt, twitter.txt (or twitter-thread.txt), instagram.txt, tiktok.txt, facebook.txt, threads.txt, reddit.txt, devto.txt, discord.txt, telegram.txt, youtube.txt, plus first-comments.txt
3. Add note: "Also show all copy in the conversation so the user can review without opening files"

---

### T-011: Add Review & Publish Chrome-open workflow section

**User Story**: US-001
**Satisfies ACs**: AC-US1-05, AC-US1-01
**Status**: [x] completed

**Test Plan**:
- **Given** the merged SKILL.md
- **When** I read the Review & Publish section
- **Then** it documents the Chrome-open workflow with the macOS `open -na "Google Chrome"` command template, per-platform posting guide, and a note that dedicated tools take priority

**Test Cases**:
1. `grep -c "open -na" ...SKILL.md` returns >= 1
2. `grep -c "PROFILE_DIR" ...SKILL.md` returns >= 1
3. `grep -c "COMPOSE_URL" ...SKILL.md` returns >= 1

**Implementation**:
1. After the Platform Posting section, add new `## Review & Publish` section
2. Absorb content from social-posts lines 276-298:
   - Step 1: Present everything (copy files, image paths, video path)
   - Step 2: Ask for approval
   - Step 3: Open Chrome with profile — macOS command template
   - Step 4: Per-platform guide (copy from path, attach image, first comment)
3. Label as last-resort approach — dedicated tools (xurl, discord skill, Bot API) are preferred per tool priority table

---

### T-012: Add Error Handling ("When Things Go Wrong") section

**User Story**: US-001
**Satisfies ACs**: AC-US1-01
**Status**: [x] completed

**Test Plan**:
- **Given** the merged SKILL.md
- **When** I read the error handling section
- **Then** it contains a "When Things Go Wrong" table with entries for: no GEMINI_API_KEY, image generation fails, Veo fails/times out, Veo 400 on durationSeconds, Veo download 403, browser won't open, platform down/needs re-auth, no product context file

**Test Cases**:
1. `grep -c "When Things Go Wrong" ...SKILL.md` returns >= 1
2. `grep -c "durationSeconds" ...SKILL.md` returns >= 1
3. `grep -c "403" ...SKILL.md` returns >= 1
4. `grep -c "GEMINI_API_KEY" ...SKILL.md` returns >= 2

**Implementation**:
1. Before the Daily Engagement Log section, add new `## When Things Go Wrong` section
2. Absorb the error table from social-posts lines 326-336 with all rows (8 error scenarios)
3. Format as markdown table matching existing SKILL.md style

---

### T-013: Update Related Skills (remove social-posts ref, add SP skills)

**User Story**: US-001
**Satisfies ACs**: AC-US4-04
**Status**: [x] completed

**Test Plan**:
- **Given** the merged SKILL.md
- **When** I read the Related Skills section
- **Then** `social-posts` is NOT listed, `nanobanana` (unhyphenated) is NOT listed, there is no circular self-reference to `social-media-posting`, and skills from social-posts are added: social-content, copywriting, ad-creative, marketing-psychology, copy-editing, content-strategy

**Test Cases**:
1. `grep -c "social-posts" ...SKILL.md` returns 0
2. `grep "nanobanana" ...SKILL.md` (without hyphen) returns 0 matches
3. `grep "social-media-posting" ...SKILL.md | grep -v "^name:"` returns 0
4. `grep -c "social-content" ...SKILL.md` returns >= 1
5. `grep -c "marketing-psychology" ...SKILL.md` returns >= 1

**Implementation**:
1. Replace the current `## Reference Files` section with expanded section covering both reference files and related skills
2. Keep unchanged: `references/platform-posting.md` and `references/engagement-playbook.md` entries
3. Add `## Related Skills` subsection with skills from social-posts (minus social-media-posting self-ref and minus nanobanana):
   - social-content, copywriting, ad-creative, marketing-psychology, copy-editing, content-strategy
4. Do NOT add `social-posts` (deleted) or `social-media-posting` (circular self-reference)

---

## User Story: US-002 - Add Virality and Proof Screenshot Guidance

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Tasks**: 1 total, 1 completed

*Note: T-008 above covers all AC-US2-* requirements. It is listed under US-001's implementation ordering section because it slots between T-007 and T-009 in the plan's implementation sequence.*

---

## User Story: US-003 - Merge Eval Suites

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Tasks**: 1 total, 1 completed

### T-014: Merge evals.json (renumber 5-8, update skill_name, add assertions)

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [x] completed

**Test Plan**:
- **Given** the merged evals.json at `social-media-posting/evals/evals.json`
- **When** I parse the JSON
- **Then** it contains exactly 8 eval entries with IDs 1-8; evals 5-8 have `skill_name: "social-media-posting"` and no `nanobanana` (unhyphenated) references; eval 1 has `proof-screenshot-preference` assertion; eval 2 has `veo-video-or-fallback` assertion; eval 5 has `strategic-thinking-phase` assertion

**Test Cases**:
1. `python3 -c "import json; data=json.load(open('evals.json')); print(len(data['evals']))"` prints `8`
2. `python3 -c "import json; data=json.load(open('evals.json')); print(data['skill_name'])"` prints `social-media-posting`
3. `python3 -c "import json; data=json.load(open('evals.json')); print([e['id'] for e in data['evals']])"` prints `[1, 2, 3, 4, 5, 6, 7, 8]`
4. `grep "nanobanana" evals.json` (without hyphen) returns 0 matches
5. Eval 1 assertions include `proof-screenshot-preference`
6. Eval 2 assertions include `veo-video-or-fallback`
7. Eval 5 assertions include `strategic-thinking-phase`

**Implementation**:
1. Read current `social-media-posting/evals/evals.json` (IDs 1-4)
2. Read `social-posts/evals/evals.json` (IDs 1-4, to become 5-8)
3. Add to eval ID 1 (breaking-news-all-platforms):
   ```json
   {"id": "proof-screenshot-preference", "text": "For X/Twitter and Threads, prioritizes proof screenshots (terminal output, metrics, before/after) as the first image over generic AI art", "type": "boolean"}
   ```
4. Add to eval ID 2 (instagram-tiktok-carousel):
   ```json
   {"id": "veo-video-or-fallback", "text": "Attempts Veo 3.1 for video generation, or falls back to Ken Burns slideshow / UGC script if unavailable", "type": "boolean"}
   ```
5. For social-posts evals (new IDs 5-8): set ID to 5/6/7/8; replace "nanobanana" with "nano-banana-pro" in all text fields; update `opens-browser` assertion text to reference Chrome-open as one valid approach among tool priority options
6. Add to eval ID 5 (topic-to-all-platforms):
   ```json
   {"id": "strategic-thinking-phase", "text": "Explicitly performs strategic thinking (hook formula, psychological angle, content pillar) before writing copy", "type": "boolean"}
   ```
7. Write merged evals.json with skill_name: "social-media-posting" and all 8 evals

---

## User Story: US-004 - Delete social-posts and Verify

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Tasks**: 2 total, 2 completed

### T-015: Delete social-posts directory

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] completed

**Test Plan**:
- **Given** T-001 through T-014 are all complete
- **When** I delete the `social-posts/` directory
- **Then** the entire directory tree is gone, AND `social-media-posting/references/platform-posting.md`, `social-media-posting/references/engagement-playbook.md`, and `social-media-posting/evals/HOW-TO-RUN-EVALS.md` remain unchanged

**Test Cases**:
1. `ls repositories/anton-abyzov/vskill/plugins/marketing/skills/social-posts/` returns "No such file or directory"
2. `ls repositories/...social-media-posting/references/platform-posting.md` exits 0
3. `ls repositories/...social-media-posting/references/engagement-playbook.md` exits 0
4. `ls repositories/...social-media-posting/evals/HOW-TO-RUN-EVALS.md` exits 0

**Implementation**:
1. Confirm all prior tasks T-001 through T-014 are marked [x]
2. Run: `rm -rf repositories/anton-abyzov/vskill/plugins/marketing/skills/social-posts/`
3. Verify reference files still exist with `ls` commands

---

### T-016: Verify no remaining references to social-posts in codebase

**User Story**: US-004
**Satisfies ACs**: AC-US4-03, AC-US4-04
**Status**: [x] completed

**Test Plan**:
- **Given** the deletion in T-015 is complete
- **When** I grep the vskill repository for "social-posts"
- **Then** zero matches are found in any tracked file, AND there is no circular self-reference to `social-media-posting` in the Related Skills section

**Test Cases**:
1. `grep -r "social-posts" repositories/anton-abyzov/vskill/plugins/marketing/` returns 0 results
2. `grep -r "social-posts" repositories/anton-abyzov/vskill/plugins/` returns 0 results
3. `grep "social-media-posting" ...social-media-posting/SKILL.md | grep -v "^name:"` returns 0 results
4. `grep -c "social media blast" ...social-media-posting/SKILL.md` returns >= 1 (final AC-US4-03 confirmation)

**Implementation**:
1. Run `grep -r "social-posts" repositories/anton-abyzov/vskill/plugins/` to find any remaining references
2. If references found in non-skill files (index.json, marketplace manifest, vskill.lock), remove or update them
3. Run self-reference check on Related Skills section
4. Fix any issues found before marking complete
