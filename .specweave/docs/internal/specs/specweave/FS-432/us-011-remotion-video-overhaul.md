---
id: US-011
feature: FS-432
title: Remotion Video Overhaul
status: complete
priority: P2
created: 2026-03-05
project: specweave
---
# US-011: Remotion Video Overhaul

**Feature**: [FS-432](./FEATURE.md)

visitor watching the demo video
**I want** a professional 1920x1080 video with updated branding, larger typography, and polished SVG icons
**So that** the video matches the redesigned site's visual quality

---

## Acceptance Criteria

- [x] **AC-US11-01**: Given the Remotion config, when inspected, then the video resolution is set to 1920x1080 (up from 1280x720)
- [x] **AC-US11-02**: Given the Remotion theme, when inspected, then colors reference the new token values (--sw-color-primary-500 equivalent hex values) and font sizes are scaled approximately 1.5x from current values
- [x] **AC-US11-03**: Given the video scenes, when rendered, then text elements use professional SVG icons from Lucide (replacing inline text elements where applicable) with richer gradient backgrounds
- [x] **AC-US11-04**: Given the rendered video, when exported, then both MP4 (H.264) and WebM (VP9) formats are produced and placed in static/video/
- [x] **AC-US11-05**: Given the remotion:render script, when executed, then it outputs both formats at 1920x1080 resolution

---

## Implementation

**Increment**: [0432-bold-website-redesign](../../../../../increments/0432-bold-website-redesign/spec.md)

