# Narration and captions for every silent site video

## Problem
Six videos on spec-weave.com played with no sound (the /code tour said "[No sound]" in its first caption). Anton asked for sound and captions on every site video.

## Scope
The SpecWithCode tour, the agent result walkthrough and the four studio-projects walkthroughs. Not in scope: `ship-while-you-sleep.mp4` and `code-run-20261015.mp4`, which no page shows.

## Acceptance Criteria
- [ ] AC-01: Every video shown on spec-weave.com has a narrated audio track at -16 LUFS, captions that match the spoken words, and is marked narrated in the catalogue.

## Approach
`video/narration/narrate.mjs` in the specweave repo voices each line with ElevenLabs "Anton Abyzov best voice" (eleven_v4) in its window, writes WebVTT from the character alignment, and copies the picture. Burned-in sentences are narrated word for word. Shipped in anton-abyzov/specweave#2102.

## Tasks
### T-01 Narrate the six silent site videos and publish
- AC: AC-01 | Files: docs-site/static/video, docs-site/static/img/studio, docs-site/src/data/tutorials.json, video/narration | Test: bash -c 'for u in video/studio-tutorial.mp4 img/studio/agent-driven-demo.mp4 video/studio-projects/projects-and-threads.mp4 video/studio-projects/plans-and-routines.mp4 video/studio-projects/memory-and-usage.mp4 video/studio-projects/personal-and-connections.mp4; do curl -s "https://spec-weave.com/$u" -o /tmp/sw-live.mp4 && ffprobe -v error -select_streams a -show_entries stream=codec_name -of csv=p=0 /tmp/sw-live.mp4 | grep -q aac || exit 1; done; rm -f /tmp/sw-live.mp4'
