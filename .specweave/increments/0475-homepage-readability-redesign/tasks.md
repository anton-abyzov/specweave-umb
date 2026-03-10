---
increment: 0475-homepage-readability-redesign
title: "Homepage Readability Redesign"
generated_by: sw:test-aware-planner
by_user_story:
  US-001: [T-001]
  US-002: [T-002]
  US-003: [T-003]
  US-004: [T-004]
  US-005: [T-005, T-006]
---

# Tasks: Homepage Readability Redesign

## User Story: US-001 - Readable Hero Agent Badges

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 1 total, 0 completed

### T-001: Increase hero badge font size, height, padding, and icon size

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [ ] pending

**Test Plan**:
- **Given** the homepage is rendered at any viewport width
- **When** a visitor views the hero section agent badges
- **Then** badges render at `0.75rem` font, `26px` height, `0.25rem 0.5rem` padding, `14x14` icons, with text color `rgba(230,237,243,0.7)` unchanged

**Test Cases**:
1. **Unit**: `src/app/page.test.tsx`
   - testHeroBadgeFontSize(): Confirms `fontSize: "0.75rem"` on hero badge spans
   - testHeroBadgeHeight(): Confirms `height: "26px"` on hero badge spans
   - testHeroBadgePadding(): Confirms `padding: "0.25rem 0.5rem"` on hero badge spans
   - testHeroBadgeIconSize(): Confirms `width={14}` and `height={14}` on badge `<img>` elements
   - testHeroBadgeTextColor(): Confirms `color: "rgba(230,237,243,0.7)"` unchanged on badge spans
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/app/page.tsx`
2. Locate the hero `FEATURED_AGENTS` badge `<span>` elements (lines 63-96 per plan)
3. Change `fontSize` from `"0.625rem"` to `"0.75rem"`
4. Change `height` from `"20px"` to `"26px"`
5. Change `padding` from `"0.125rem 0.3125rem"` to `"0.25rem 0.5rem"`
6. Change badge `<img>` `width` and `height` attributes from `11` to `14`
7. Leave `color: "rgba(230,237,243,0.7)"` and border formula (`accentColor + "40"`) unchanged
8. Run `npx vitest run src/app/page.test.tsx`

---

## User Story: US-002 - Value Proposition Above Video

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Tasks**: 1 total, 0 completed

### T-002: Reorder children slot above video in HomepageDemoHero

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [ ] pending

**Test Plan**:
- **Given** `HomepageDemoHero` receives a `children` prop with heading and stats content
- **When** the component renders
- **Then** the children wrapper node appears before the video container node in the DOM, `marginTop` is removed from the children wrapper, and the server/client boundary is unchanged

**Test Cases**:
1. **Unit**: `src/app/components/homepage/HomepageDemoHero.test.tsx`
   - testChildrenRenderBeforeVideo(): Queries rendered DOM; asserts children wrapper node index is less than video container node index
   - testChildrenWrapperMargin(): Confirms `marginTop` is absent and `marginBottom: "1.25rem"` is present on the children wrapper
   - testServerClientBoundaryUnchanged(): Confirms `"use client"` directive present; children accepted as `ReactNode` prop (no prop-type change)
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/app/components/homepage/HomepageDemoHero.tsx`
2. Locate the `{children && ...}` wrapper block — currently rendered after the video container
3. Move the entire `{children && ...}` block to appear before the video container `<div>`
4. Remove `marginTop: "1.25rem"` from the children wrapper style
5. Add `marginBottom: "1.25rem"` to the children wrapper style
6. Run `npx vitest run src/app/components/homepage/HomepageDemoHero.test.tsx`

---

## User Story: US-003 - Standalone Flaws Stat Callout

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Tasks**: 1 total, 0 completed

### T-003: Extract flaws stat into a distinct callout block in page.tsx

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [ ] pending

**Test Plan**:
- **Given** the homepage server component renders
- **When** a visitor views the area between the description paragraph and the "Works with" row
- **Then** a standalone callout block with amber left border, `0.8125rem` mono text, and a working `/audits` link is visible; the description `<p>` no longer contains the "36.82%" span

**Test Cases**:
1. **Unit**: `src/app/page.test.tsx`
   - testFlawsStatNotInParagraph(): Confirms "36.82%" text is NOT a descendant of the description `<p>` element
   - testFlawsCalloutBlockExists(): Confirms a callout `<div>` element exists between the description `<p>` and the "Works with" row
   - testFlawsCalloutBorderLeft(): Confirms `borderLeft: "2px solid rgba(245,158,11,0.4)"` on callout div
   - testFlawsCalloutFontSize(): Confirms `fontSize: "0.8125rem"` and `color: "rgba(230,237,243,0.6)"` on callout div
   - testFlawsAuditsLinkHref(): Confirms "Scan results" `<a>` element has `href="/audits"`
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/app/page.tsx`
2. Locate the description `<p>` containing the inline `<span>` with "36.82% have flaws" (lines 49-57 per plan)
3. Remove the inline `<span>` from inside the `<p>` tag
4. After the closing `</p>`, insert a new `<div>` callout with inline styles:
   - `borderLeft: "2px solid rgba(245,158,11,0.4)"`
   - `paddingLeft: "0.625rem"`, `marginTop: "0.5rem"`
   - `fontSize: "0.8125rem"`, `color: "rgba(230,237,243,0.6)"`, monospace `fontFamily`
   - Inner content: `<span>36.82%</span> have flaws · <a href="/audits">Scan results</a>`
5. Run `npx vitest run src/app/page.test.tsx`

---

## User Story: US-004 - Enlarged Bottom Works-With Badges

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05
**Tasks**: 1 total, 0 completed

### T-004: Increase bottom Works-With badge sizes for featured and non-featured variants

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05
**Status**: [ ] pending

**Test Plan**:
- **Given** the homepage renders the bottom "Works with" section
- **When** a visitor views featured and non-featured agent badges
- **Then** featured badges show `0.8125rem` font / `28px` height / `16x16` icon / `6px` dot / `0.25rem 0.5625rem` padding, and non-featured show `0.75rem` / `24px` / `14x14` / `5px` dot / `0.1875rem 0.4375rem` padding

**Test Cases**:
1. **Unit**: `src/app/page.test.tsx`
   - testFeaturedBadgeFontSize(): Confirms `fontSize: "0.8125rem"` on featured bottom badges
   - testFeaturedBadgeHeight(): Confirms `height: "28px"` on featured bottom badges
   - testFeaturedBadgeIconSize(): Confirms `width={16}` and `height={16}` on featured badge `<img>` elements
   - testFeaturedBadgeDot(): Confirms featured dot element is `6px` wide/tall
   - testFeaturedBadgePadding(): Confirms `padding: "0.25rem 0.5625rem"` on featured badges
   - testNonFeaturedBadgeFontSize(): Confirms `fontSize: "0.75rem"` on non-featured bottom badges
   - testNonFeaturedBadgeHeight(): Confirms `height: "24px"` on non-featured bottom badges
   - testNonFeaturedBadgeIconSize(): Confirms `width={14}` and `height={14}` on non-featured badge `<img>` elements
   - testNonFeaturedBadgeDot(): Confirms non-featured dot element is `5px` wide/tall
   - testNonFeaturedBadgePadding(): Confirms `padding: "0.1875rem 0.4375rem"` on non-featured badges
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/app/page.tsx`
2. Locate the bottom "Works with" section badge elements (lines 244-283 per plan)
3. Update featured badge inline styles: `fontSize` → `"0.8125rem"`, `height` → `"28px"`, `padding` → `"0.25rem 0.5625rem"`, img `width`/`height` → `16`, dot `width`/`height` → `6`
4. Update non-featured badge inline styles: `fontSize` → `"0.75rem"`, `height` → `"24px"`, `padding` → `"0.1875rem 0.4375rem"`, img `width`/`height` → `14`, dot `width`/`height` → `5`
5. Run `npx vitest run src/app/page.test.tsx`

---

## User Story: US-005 - CLI Copy Button in Video Overlay

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05, AC-US5-06
**Tasks**: 2 total, 0 completed

### T-005: Add video-copy-btn CSS rules to globals.css

**User Story**: US-005
**Satisfies ACs**: AC-US5-06
**Status**: [ ] pending

**Test Plan**:
- **Given** `globals.css` is loaded by the application
- **When** an element with class `video-copy-btn` is rendered
- **Then** the stylesheet contains transition, hover background/border, and 480px responsive font/padding rules matching the play button style

**Test Cases**:
1. **Unit**: CSS content verification (grep/snapshot in hero component tests)
   - testVideoCopyBtnTransitionExists(): Confirms `.video-copy-btn` block contains `transition: background-color 180ms ease, border-color 180ms ease`
   - testVideoCopyBtnHoverExists(): Confirms `.video-copy-btn:hover` sets `background: rgba(0,0,0,0.8)` and `border-color: rgba(255,255,255,0.4)`
   - testVideoCopyBtnResponsiveExists(): Confirms `@media (max-width: 480px)` block sets `font-size: 0.5625rem` and `padding: 0.25rem 0.5rem` for `.video-copy-btn`
   - **Coverage Target**: 85%

**Implementation**:
1. Open `src/app/globals.css`
2. Locate the existing `.video-play-btn:hover` block
3. After that block, add:
   ```css
   .video-copy-btn {
     transition: background-color 180ms ease, border-color 180ms ease;
   }

   .video-copy-btn:hover {
     background: rgba(0, 0, 0, 0.8) !important;
     border-color: rgba(255, 255, 255, 0.4) !important;
   }

   @media (max-width: 480px) {
     .video-copy-btn {
       font-size: 0.5625rem !important;
       padding: 0.25rem 0.5rem !important;
     }
   }
   ```
4. Run `npx vitest run` to confirm no regressions

### T-006: Move CLI copy button into video overlay and remove standalone CLI row

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05
**Status**: [ ] pending

**Dependencies**: T-005 (globals.css rules must exist before className is applied)

**Test Plan**:
- **Given** `HomepageDemoHero` renders with copy-command state
- **When** a visitor views the video section
- **Then** a pill-shaped glass-morphism copy button appears bottom-left of the video overlay with the full CLI command, and the standalone CLI row and "as shown in video" label are absent from the DOM

**Test Cases**:
1. **Unit**: `src/app/components/homepage/HomepageDemoHero.test.tsx`
   - testCopyButtonInVideoOverlay(): Confirms copy button element is a descendant of the video container div
   - testCopyButtonGlassMorphism(): Confirms `background: "rgba(0,0,0,0.6)"`, `backdropFilter: "blur(4px)"`, `border: "1px solid rgba(255,255,255,0.2)"`, `borderRadius: "999px"` on button
   - testCopyButtonText(): Confirms button displays `$ npx vskill find code-review`
   - testCopyButtonPosition(): Confirms `position: "absolute"`, `bottom: "0.75rem"`, `left: "0.75rem"` on button
   - testCopyButtonClassName(): Confirms `className="video-copy-btn"` is present on button element
   - testCopyButtonCopiedState(): Simulates click event; confirms button text changes to copied indicator; after timeout resets to original text
   - testStandaloneCLIRowAbsent(): Confirms the standalone CLI copy row div is NOT present in rendered output
   - testAsShownInVideoLabelAbsent(): Confirms "as shown in video" text is NOT present anywhere in rendered output
   - **Coverage Target**: 90%

**Implementation**:
1. Confirm T-005 is complete (globals.css updated)
2. Open `src/app/components/homepage/HomepageDemoHero.tsx`
3. Remove the entire standalone CLI copy `<div>` block (plan lines 119-161) including the "as shown in video" label
4. Inside the video container `<div>`, add a pill-shaped `<button>` as sibling to the play/pause button:
   - `position: "absolute"`, `bottom: "0.75rem"`, `left: "0.75rem"`
   - `borderRadius: "999px"`, `background: "rgba(0,0,0,0.6)"`, `backdropFilter: "blur(4px)"`, `border: "1px solid rgba(255,255,255,0.2)"`
   - `fontFamily` monospace, `fontSize: "0.6875rem"`, `color: "#fff"`, `padding: "0.375rem 0.75rem"`
   - `className="video-copy-btn"`
   - Content: `$ npx vskill find code-review` with existing copy/copied state toggle logic
5. Run `npx vitest run src/app/components/homepage/HomepageDemoHero.test.tsx`
