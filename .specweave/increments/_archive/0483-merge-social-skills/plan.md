# Plan: Merge social-posts into social-media-posting

## Overview

This is a content/documentation merge of two SKILL.md files and their eval suites. No code changes. The surviving skill (`social-media-posting`) absorbs all unique content from the deleted skill (`social-posts`), gaining strategic thinking, product context, copy file output, Veo 3.1 video generation, Chrome-open fallback, proof screenshot guidance (new), and 4 additional evals.

## Architecture Decision: Merged SKILL.md Section Order

Target: ~600 lines (448 from surviving + ~200 net new from social-posts minus ~50 overlap removal).

### Section Layout of Merged SKILL.md

```
Line  Section                              Source             Notes
----  -------                              ------             -----
1-6   Frontmatter (merged triggers)        BOTH               Merge description fields
7-11  Title + tagline                       social-media-posting  Keep existing
12-15 "Before Starting" (NEW section)       social-posts L17-35   Insert before Core Rules
16-70 Core Rules (5 rules)                  social-media-posting  Unchanged
71-85 Workflow Overview (updated)           social-media-posting  Insert CONTEXT+STRATEGY+VIDEO steps
86-120 Strategic Thinking Phase (NEW)       social-posts L42-59   Hook formulas, psych angles, copy principles
                                                                 content pillars, product integration ratios
121-145 Tool Priority (updated table)       social-media-posting  Add Chrome-open fallback column
146-195 Tool Details (xurl, discord, etc)   social-media-posting  Unchanged
196-260 Image Generation                    BOTH                 Keep Nano Banana Pro as primary,
                                                                 add direct Gemini API as documented fallback,
                                                                 add Pillow carousel compositing from social-posts
261-310 Proof Screenshots (NEW section)     NEW CONTENT          X/Twitter + Threads first-image requirement
311-375 Video Generation                    social-posts L158-272 Veo 3.1, Ken Burns, UGC script (wholesale)
376-400 Platform Posting tables             social-media-posting  Unchanged
401-430 Content Adaptation                  social-media-posting  Unchanged
431-445 Copy File Output (NEW subsection)   social-posts L72-84   Per-platform .txt files in generated-assets/copy/
446-490 TikTok Video + Timing + Scheduling  social-media-posting  Unchanged
491-505 Telegram Posting                    social-media-posting  Unchanged
506-530 Deduplication                       social-media-posting  Unchanged
531-560 Daily Engagement                    social-media-posting  Unchanged
561-580 Review & Publish (Chrome-open)      social-posts L276-298 Chrome profile open workflow merged in
581-595 Post-Publishing Checklist           social-media-posting  Unchanged
596-610 Error Handling (NEW section)        social-posts L326-336 "When Things Go Wrong" table
611-625 Daily Engagement Log                social-media-posting  Unchanged
626-640 Reference Files + Related Skills    BOTH                 Remove social-posts self-ref
```

## Content Source Mapping

### Kept As-Is from social-media-posting (bulk of document)

| Section | Lines in Current | Status |
|---------|-----------------|--------|
| Core Rules (5 rules) | 14-48 | No changes |
| xurl CLI details | 87-108 | No changes |
| Discord skill actions | 110-129 | No changes |
| Peekaboo fallback | 131-155 | No changes |
| Nano Banana Pro generation | 159-226 | Keep as primary image gen, extend |
| Platform Posting table | 233-248 | No changes |
| Content Adaptation guide | 249-262 | No changes |
| TikTok video from carousel | 264-272 | No changes |
| Optimal Timing 3-tier | 274-301 | No changes |
| Scheduled Posting | 303-327 | No changes |
| Telegram posting | 329-339 | No changes |
| Deduplication | 343-363 | No changes |
| Daily Engagement (10-thread rule) | 367-408 | No changes |
| Post-Publishing Checklist | 411-417 | No changes |
| Daily Engagement Log | 421-441 | No changes |
| Reference Files | 444-448 | Update to remove social-posts ref |

### Absorbed from social-posts (unique content)

| Content Block | social-posts Lines | Insert Location | Changes Needed |
|--------------|-------------------|-----------------|----------------|
| "Before Starting" (context file check) | 17-35 | New section before Core Rules | Change "nanobanana" to "nano-banana-pro", add `.claude/` as primary lookup dir, project root as fallback |
| Strategic Thinking phase | 42-59 | New section after Workflow Overview | Wholesale import: hook formulas, psych angles, copy principles, content pillars, product integration ratios |
| Product Integration ratios | 49-58 | Inside Strategic Thinking | 60/20/15/5% breakdown |
| Per-platform copy file output | 72-84 | New subsection under Content Adaptation | Save to `generated-assets/copy/*.txt` for all 11 platforms |
| Direct Gemini API image gen | 92-114 | Add as documented fallback under Image Generation | Label as "Fallback when nano-banana-pro skill is not installed" |
| Pillow carousel compositing | 127-148 | Add under Carousels subsection | Overlay technique for text on carousel slides |
| Veo 3.1 video generation | 158-253 | New "Video Generation" section after Image Generation | Option A (Veo 3.1), Option B (Ken Burns), Option C (UGC script) -- wholesale |
| Chrome-open publish flow | 276-298 | New "Review & Publish" section | Open Chrome with profile, per-platform posting guide |
| Error handling table | 326-336 | New section before Daily Engagement Log | "When Things Go Wrong" table |
| Platform Defaults table | 309-319 | Merge into existing Platform Posting section | YouTube default=skip unless requested |
| Related Skills | 339-351 | Merge into Reference Files section | Remove "social-media-posting" and "nanobanana" entries, add remaining |

### Overlapping Content (Deduplicated)

These items exist in both skills. The social-media-posting version is kept (more complete), social-posts version discarded:

| Topic | social-media-posting | social-posts | Resolution |
|-------|---------------------|-------------|------------|
| Approval gate | Core Rule 1 (detailed) | One-liner L13 | Keep SMP version |
| Platform copy adaptation | Content Adaptation (11 platforms) | Phase 2 (6 platforms) | Keep SMP (superset) |
| Image aspect ratios table | Platform-Specific Dimensions (11 platforms) | Per-platform image specs (5 platforms) | Keep SMP (superset) |
| Carousel creation | Carousels section | Carousel creation section | Merge: keep SMP structure, add Pillow compositing from SP |
| Image generation tool | Nano Banana Pro with 3 options | "nanobanana" skill | Keep SMP's nano-banana-pro, add direct Gemini API as fallback |

### New Content (Not in Either Source)

| Section | Purpose | AC Coverage |
|---------|---------|-------------|
| Proof Screenshots for X/Twitter and Threads | First image on high-virality platforms must be proof (terminal output, metrics, before/after) not generic AI art | AC-US2-01 through AC-US2-04 |
| Proof screenshot creation guide | Clean terminal, cropped dashboards, annotated comparisons | AC-US2-04 |
| Fallback for abstract topics | Data visualization or infographic-style AI art | AC-US2-02 |
| "Never fake screenshots" rule | Explicit prohibition, never block workflow | AC-US2-03 |

## Tool Priority Table Update

Add Chrome-open as last-resort fallback column for browser-based platforms:

```
| Platform   | 1st Choice         | 2nd Choice              | 3rd Choice        | 4th (Last Resort)    |
|------------|-------------------|-------------------------|-------------------|---------------------|
| X/Twitter  | xurl CLI          | Puppeteer/browser       | Peekaboo          | Chrome-open          |
| Discord    | discord skill     | Webhook API (curl)      | Browser automation | --                   |
| Telegram   | Bot API (curl)    | --                      | --                | --                   |
| Instagram  | Puppeteer+profile | Peekaboo                | Chrome-open        | --                   |
| LinkedIn   | Puppeteer+profile | Peekaboo                | Chrome-open        | --                   |
| Threads    | Puppeteer+profile | Peekaboo                | Chrome-open        | --                   |
| YouTube    | Puppeteer+clipboard| Peekaboo               | Chrome-open        | --                   |
| Reddit     | Puppeteer (old.reddit)| Peekaboo             | Chrome-open        | --                   |
| TikTok     | Puppeteer+ffmpeg  | Peekaboo                | Chrome-open        | --                   |
| dev.to     | Puppeteer+profile | Peekaboo                | Chrome-open        | --                   |
| Facebook   | Puppeteer+profile | Peekaboo                | Chrome-open        | --                   |
```

Chrome-open excluded from Telegram (API-only) and Discord (dedicated skill/webhook).

## Workflow Overview Update

Insert strategic thinking after dedup:

```
0. DEDUP     -> Read last 10 posts per platform, flag overlaps
1. CONTEXT   -> Check product-marketing-context.md, gather brand voice  [NEW]
2. STRATEGY  -> Hook formula, psychological angle, content pillars      [NEW from social-posts]
3. ANALYZE   -> Check post analytics history, recommend optimal posting time
4. CONTENT   -> Write platform-adapted copy, save to generated-assets/copy/
5. IMAGES    -> Generate 3 options per image with Nano Banana Pro (proof screenshots first for X/Threads)
6. VIDEO     -> Veo 3.1 / Ken Burns / UGC script (if video content)    [NEW from social-posts]
7. REVIEW    -> Present everything + timing recommendation, wait for approval
8. POST      -> Publish or schedule using best available tool (Chrome-open as last resort)
9. VERIFY    -> Confirm each post is live, collect URLs
10. ENGAGE   -> Find 10 threads per platform, draft replies, get approval
11. LOG      -> Write daily engagement log with all URLs
```

## Frontmatter Merge

Combined description field covering all trigger phrases from both skills:

- From social-media-posting: "post content to social media", "create social media visuals", "schedule posts", "engage with followers", "grow their audience", "reply to threads", platform names
- From social-posts: "post about", "social media blast", "cross-post", "share on socials", "spread the word", "promote this on [platform]", "quick post", "post with video", "create social content", "repost across socials"
- Tags: union of both tag sets
- Remove `version` from metadata (social-media-posting does not use it)

## Evals Merge Strategy

### Source Evals

**social-media-posting evals (IDs 1-4, kept as-is):**
1. `breaking-news-all-platforms` -- dedup, images, tool selection, multi-platform
2. `instagram-tiktok-carousel` -- carousel generation, TikTok video conversion
3. `daily-engagement-session` -- 10-thread rule, anti-spam, reply quality
4. `scheduled-posting-optimal-time` -- analytics-driven timing, native scheduling

**social-posts evals (renumbered to IDs 5-8):**
5. `topic-to-all-platforms` (was ID 1) -- context file, strategic thinking, copy files, images
6. `product-launch-post` (was ID 2) -- brand voice, milestone framing, platform adaptation
7. `no-context-file-graceful` (was ID 3) -- graceful degradation without context file
8. `repurpose-article` (was ID 4) -- article insight extraction, link placement, standalone value

### Changes to Renumbered Evals (5-8)

| Field | Old Value | New Value |
|-------|-----------|-----------|
| `skill_name` | `"social-posts"` | `"social-media-posting"` |
| Assertion referencing "nanobanana" | `"nanobanana skill"` | `"nano-banana-pro"` |
| Assertion referencing "opens-browser" | Chrome-open only | Include as one valid approach among tool priority options |

### New/Updated Assertions

**Eval 5 (topic-to-all-platforms):** Add two assertions:
- `strategic-thinking-phase`: "Explicitly performs strategic thinking (hook formula, psychological angle, content pillar) before writing copy"
- `saves-copy-files`: Already present, keep as-is -- validates `generated-assets/copy/` output

**Eval for proof screenshots:** Add assertion to eval 1 (breaking-news-all-platforms):
- `proof-screenshot-preference`: "For X/Twitter and Threads, prioritizes proof screenshots (terminal output, metrics, before/after) as the first image over generic AI art"

**Eval for Veo 3.1:** Add assertion to eval 2 (instagram-tiktok-carousel):
- `veo-video-or-fallback`: "Attempts Veo 3.1 for video generation, or falls back to Ken Burns slideshow / UGC script if unavailable"

### Final Merged evals.json Structure

```
{
  "skill_name": "social-media-posting",
  "evals": [
    { "id": 1, "name": "breaking-news-all-platforms", ... + proof-screenshot assertion },
    { "id": 2, "name": "instagram-tiktok-carousel", ... + veo assertion },
    { "id": 3, "name": "daily-engagement-session", ... unchanged },
    { "id": 4, "name": "scheduled-posting-optimal-time", ... unchanged },
    { "id": 5, "name": "topic-to-all-platforms", ... skill_name updated, nanobanana->nano-banana-pro },
    { "id": 6, "name": "product-launch-post", ... skill_name updated, nanobanana->nano-banana-pro },
    { "id": 7, "name": "no-context-file-graceful", ... skill_name updated, nanobanana->nano-banana-pro },
    { "id": 8, "name": "repurpose-article", ... skill_name updated }
  ]
}
```

## Copy File Output: Platform Mapping

Expand social-posts' 6-platform copy file set to cover all 11 platforms:

```
generated-assets/copy/
  linkedin.txt
  twitter.txt          (or twitter-thread.txt for thread content)
  instagram.txt
  tiktok.txt
  facebook.txt
  threads.txt
  reddit.txt           [NEW - not in social-posts]
  devto.txt            [NEW]
  discord.txt          [NEW]
  telegram.txt         [NEW]
  youtube.txt          [NEW]
  first-comments.txt   [from social-posts - links, hashtags for first comments]
```

## Deletion Strategy for social-posts/

After the merge is verified complete:

1. Delete the entire directory: `repositories/anton-abyzov/vskill/plugins/marketing/skills/social-posts/`
   - `SKILL.md` (351 lines -- all content absorbed)
   - `evals/evals.json` (4 evals renumbered into merged file)
   - `evals/benchmark.json` (historical, not carried over)
   - `evals/history/` (historical, not carried over)
2. Verify no remaining references to `social-posts` anywhere in the codebase
3. Update social-media-posting's "Related Skills" section to remove `social-posts` reference
4. Ensure no circular self-reference in Related Skills

Files explicitly preserved unchanged:
- `social-media-posting/references/platform-posting.md` (18,818 bytes)
- `social-media-posting/references/engagement-playbook.md` (7,746 bytes)
- `social-media-posting/evals/HOW-TO-RUN-EVALS.md`
- `social-media-posting/evals/benchmark.json` (existing benchmarks, keep)
- `social-media-posting/evals/history/` (existing history, keep)

## Implementation Order

1. **T-001**: Merge SKILL.md frontmatter (combine description + triggers + tags)
2. **T-002**: Insert "Before Starting" section (product context file check)
3. **T-003**: Insert Strategic Thinking phase (hooks, psychology, copy principles, product integration)
4. **T-004**: Update Workflow Overview (add CONTEXT, STRATEGY, VIDEO steps)
5. **T-005**: Update Tool Priority table (add Chrome-open fallback column)
6. **T-006**: Add direct Gemini API as image generation fallback
7. **T-007**: Add Pillow carousel compositing technique
8. **T-008**: Add Proof Screenshots section (new content for X/Twitter + Threads)
9. **T-009**: Insert Video Generation section (Veo 3.1 + Ken Burns + UGC)
10. **T-010**: Add per-platform copy file output subsection (all 11 platforms)
11. **T-011**: Add Review & Publish Chrome-open workflow
12. **T-012**: Add Error Handling table
13. **T-013**: Update Related Skills (remove social-posts, add remaining from SP)
14. **T-014**: Merge evals.json (renumber 5-8, update skill_name, add assertions)
15. **T-015**: Delete social-posts directory
16. **T-016**: Verify no remaining references to social-posts in codebase

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Merged SKILL.md exceeds 600 lines | Medium | Low | Trim verbose examples; the ~600 target is a guideline not a hard cap |
| Lost content from social-posts | Low | High | Content source mapping above tracks every section; verify post-merge |
| Eval assertions reference deleted skill | Low | Medium | Explicit renaming in merge plan; grep verification in T-016 |
| Chrome-open added to Telegram | Low | Medium | Spec explicitly excludes Telegram; table mapping above confirms |
