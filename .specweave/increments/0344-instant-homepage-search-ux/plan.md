# Plan — 0344-instant-homepage-search-ux

## Implementation Order

1. **T-001**: Create skeleton components in `src/app/components/home/HomeSkeleton.tsx`
2. **T-002-T-005**: Extract async server components (HeroStats, MarketDashboard, TrendingSkills, CategoryNav)
3. **T-006**: Add `React.cache()` wrapper for `getPlatformStats`
4. **T-007**: Restructure `page.tsx` — remove async, add Suspense boundaries, reduce ISR to 60s
5. **T-008**: Create `HeroSearchInput` client component
6. **T-009**: Modify `SearchPalette` to handle pre-filled query from openSearch event
7. **T-010**: Add compound indexes to Prisma schema
8. **T-011**: Build + test verification

## Key Files

| File | Action |
|------|--------|
| `src/app/page.tsx` | MODIFY — restructure with Suspense |
| `src/app/components/home/HomeSkeleton.tsx` | CREATE — skeleton fallbacks |
| `src/app/components/home/HeroStats.tsx` | CREATE — async stats component |
| `src/app/components/home/MarketDashboard.tsx` | CREATE — async dashboard component |
| `src/app/components/home/TrendingSkills.tsx` | CREATE — async trending component |
| `src/app/components/home/CategoryNav.tsx` | CREATE — async category pills |
| `src/app/components/home/HeroSearchInput.tsx` | CREATE — client search input |
| `src/app/components/SearchPalette.tsx` | MODIFY — handle detail.query |
| `src/lib/cron/stats-refresh.ts` | MODIFY — add getCachedPlatformStats |
| `prisma/schema.prisma` | MODIFY — add compound indexes |
