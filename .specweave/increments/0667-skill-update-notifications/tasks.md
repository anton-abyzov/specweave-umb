# Tasks: Skill Update Notifications & Upgrade Flow

## Domain: Studio Notifications

### T-001: Add updateNotificationDismissed state to StudioContext
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05, AC-US1-06 | **Status**: [x] completed
**Test Plan**:
- Given StudioState initial state, When state is created, Then updateNotificationDismissed is false
- Given updateNotificationDismissed is false, When DISMISS_UPDATE_NOTIFICATION is dispatched, Then updateNotificationDismissed is true
- Given updateNotificationDismissed is true, When no further action, Then it remains true for the session

### T-002: Create UpdateToast component
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06 | **Status**: [x] completed
**Test Plan**:
- Given updateCount is 0, When UpdateToast renders, Then nothing is shown
- Given updateCount is 3 and not dismissed, When UpdateToast renders, Then banner shows "3 updates available" with "View Updates" button and X button
- Given toast is visible, When 10 seconds pass, Then toast auto-dismisses via DISMISS_UPDATE_NOTIFICATION
- Given toast is visible, When X is clicked, Then toast dismisses immediately
- Given toast is visible, When "View Updates" is clicked, Then window.location.hash is set to "#/updates"
- Given toast was dismissed, When re-render, Then toast does not appear

### T-003: Render UpdateToast in App.tsx
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test Plan**:
- Given App renders with StudioProvider, When UpdateToast is inside provider, Then it has access to useStudio() context

### T-004: Add hasUpdate prop and yellow dot to TabBar Versions tab
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test Plan**:
- Given hasUpdate is true, When TabBar renders, Then versions tab shows a yellow dot indicator
- Given hasUpdate is false, When TabBar renders, Then versions tab has no dot
- Given hasUpdate is true, When dot renders, Then it uses var(--yellow) color matching other indicator dots

### T-005: Derive hasUpdate in SkillWorkspace and pass to TabBar
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [x] completed
**Test Plan**:
- Given selected skill has updateAvailable: true, When SkillWorkspace renders, Then hasUpdate is true and passed to TabBar
- Given selected skill has updateAvailable: false, When SkillWorkspace renders, Then hasUpdate is false
- Given skill is updated (updateAvailable changes), When re-render, Then hasUpdate reflects new state

## Domain: Studio Upgrade Flow

### T-006: Add "Update to Latest" button in VersionHistoryPanel
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed
**Test Plan**:
- Given installed !== latest, When VersionHistoryPanel renders, Then "Update to {latest.version}" button is visible
- Given installed === latest, When VersionHistoryPanel renders, Then no update button is shown
- Given update button clicked, When SSE starts, Then button shows "Updating..." disabled state
- Given SSE emits scanning event, When progress updates, Then button shows "Scanning..."
- Given SSE emits done event, When update completes, Then versions list revalidates and global skills refresh
- Given SSE emits error event, When update fails, Then inline error shown with "Retry" option

### T-007: Add "Manage all updates" cross-link in VersionHistoryPanel
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02 | **Status**: [x] completed
**Test Plan**:
- Given updateCount is 3, When VersionHistoryPanel renders, Then "Manage all updates (3)" link is visible
- Given updateCount is 1, When VersionHistoryPanel renders, Then no manage-all link is shown
- Given updateCount is 0, When VersionHistoryPanel renders, Then no manage-all link is shown
- Given link is clicked, When navigation triggers, Then window.location.hash is "#/updates"
