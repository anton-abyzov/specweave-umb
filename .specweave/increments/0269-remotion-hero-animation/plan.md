# 0269: Plan — Remotion Hero Animation

## Approach

Create a Remotion project inside the docs-site repo. The `remotion-best-practices` skill provides patterns for text animations, springs, and sequencing. Render to MP4, embed on homepage.

## Steps

1. **Project setup**: Install Remotion deps, create `remotion/` dir with `Root.tsx`
2. **Scene 1**: Implement floating threat snippets + "36.82%" spring animation
3. **Scene 2**: Implement scanner with scan line, file card, results list, BLOCKED overlay
4. **Scene 3**: Implement three-tier badges with staggered spring entrances
5. **Scene 4**: Implement terminal window with typewriter + verified badge bounce
6. **Scene 5**: Implement wordmark slide-up, tagline, trust badges
7. **Compose**: Wire all scenes with `<Sequence>` and crossfade overlaps
8. **Preview**: Run `npx remotion preview`, iterate on timing
9. **Render**: `npx remotion render SpecWeaveHero out/hero.mp4`
10. **Integrate**: Add `<video>` tag to homepage, copy to `static/video/`

## Risks

- **Medium**: Remotion render time — mitigated by 720p resolution and 45s duration (should be <5min)
- **Medium**: Video file size — mitigated by H.264 compression, target <5MB
- **Low**: Font loading — use system fonts as fallback

## Dependencies

- `remotion-best-practices` skill (already installed)
- Increment 0268 (optional) — video section can be placed independently
