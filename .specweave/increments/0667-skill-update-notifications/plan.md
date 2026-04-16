# Implementation Plan: Skill Update Notifications & Upgrade Flow

## Architecture Decision

**No new architecture.** All changes extend existing patterns:
- StudioContext reducer pattern for state
- Existing SSE update flow from UpdatesPanel
- Existing tab indicator dot pattern from TabBar
- Existing design tokens (--yellow, --accent-muted, --surface-1)

## Component Design

### UpdateToast (new)
- Consumes `useStudio()` for `updateCount` and `updateNotificationDismissed`
- Fixed position (bottom-right), z-index above workspace
- Uses `animate-fade-in` pattern from UpdatesPanel toast
- Self-contained: auto-dismiss timeout via `useEffect`

### StudioContext (extend)
- Add `updateNotificationDismissed: boolean` to `StudioState`
- Add `DISMISS_UPDATE_NOTIFICATION` action
- Expose via context value

### TabBar (extend)
- Add `hasUpdate?: boolean` prop
- Extend `showDot` condition for versions tab
- Yellow dot color already handled in existing dotColor logic

### VersionHistoryPanel (extend)
- Add "Update to {version}" button (condition: `showAutoLink`)
- SSE handler following UpdatesPanel pattern
- "Manage all updates (N)" link (condition: `updateCount > 1`)
- Post-update: revalidate SWR + refreshSkills()

### SkillWorkspace (extend)
- Derive `hasUpdate` from `useStudio().state.skills`
- Pass to TabBar

## Data Flow

```
Studio load → StudioContext fetches updates → merges into skills
                                            → sets updateCount
                                            → UpdateToast renders if count > 0

Skill selected → SkillWorkspace derives hasUpdate → TabBar yellow dot

Versions tab → VersionHistoryPanel shows Update button if showAutoLink
             → Click → api.startSkillUpdate(SSE) → progress → done
             → refreshSkills() + SWR revalidate
```

## Files to Modify

| File | Type | Lines |
|------|------|-------|
| StudioContext.tsx | Extend | ~15 lines (state + action + reducer case) |
| components/UpdateToast.tsx | New | ~60 lines |
| App.tsx | Extend | ~2 lines (import + render) |
| components/TabBar.tsx | Extend | ~5 lines (prop + condition) |
| pages/workspace/SkillWorkspace.tsx | Extend | ~5 lines (derive + pass prop) |
| pages/workspace/VersionHistoryPanel.tsx | Extend | ~60 lines (button + SSE + link) |

## Risk Assessment

- **Low risk**: All changes are additive, no existing behavior modified
- **No API changes**: All endpoints already exist
- **No new dependencies**: Uses React built-ins only
- **Isolated failure**: Toast/dot are cosmetic; update button falls back to UpdatesPanel
