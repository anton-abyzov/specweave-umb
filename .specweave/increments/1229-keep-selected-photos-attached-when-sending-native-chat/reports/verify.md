# Verify — 1229-keep-selected-photos-attached-when-sending-native-chat

PASS · 2026-11-04T00:04:45.898Z · commands from explicit

## Commands

### `cd "/Users/antonabyzov/.specwithcode/m4/worktrees/specwithcode-dev/recent-features-followup-20261103" && test "$(git rev-parse --short=10 HEAD)" = da8cb7ede2 && swift test --package-path apps/ios/SWCKit --filter pendingPhotoBatchesFollowTheirDraftAcrossNavigation` → exit 0 (26s)

```
104 |     let palette = WeaveTintName.allCases

macro expansion #expect:1:46: warning: call to main actor-isolated static method 'identityMonogram' in a synchronous nonisolated context [#ActorIsolatedCall]
`- /Users/antonabyzov/.specwithcode/m4/worktrees/specwithcode-dev/recent-features-followup-20261103/apps/ios/SWCKit/Tests/SWCFeaturesTests/ProjectIdentityTests.swift:29:63: note: expanded code originates here
25 |   }
26 |
27 |   @Test func initialsNeverExceedTheServerLimit() {
   |              `- note: add '@MainActor' to make instance method 'initialsNeverExceedTheServerLimit()' part of global actor 'MainActor'
28 |     for name in ["sketchmate-studio", "A very long project name", "文書"] {
29 |       #expect(ProjectAvatar.identityMonogram(name).count <= 2)
   |       `- note: in expansion of macro 'expect' here
   +--- macro expansion #expect ----------------------------------------
   |1 | Testing.__checkBinaryOperation(ProjectAvatar.identityMonogram(name).count,{ $0 <= $1() },2,expression: .__fromBinaryOperation(.__fromSyntaxNode("ProjectAvatar.identityMonogram(name).count"),"<=",.__fromSyntaxNode("2")),comments: [],isRequired: false,sourceLocation: Testing.SourceLocation.__here()).__expected()
   |  |                                              `- warning: call to main actor-isolated static method 'identityMonogram' in a synchronous nonisolated context [#ActorIsolatedCall]
   +--------------------------------------------------------------------
30 |     }
31 |   }

/Users/antonabyzov/.specwithcode/m4/worktrees/specwithcode-dev/recent-features-followup-20261103/apps/ios/SWCKit/Sources/Weave/Components/ProjectAvatar.swift:116:22: note: calls to static method 'identityMonogram' from outside of its actor context are implicitly asynchronous
114 |   /// last word's first letter, else the first word's last letter. Leading
115 |   /// numbers are skipped when a word with letters follows them.
116 |   public static func identityMonogram(_ title: String) -> String {
    |                      `- note: calls to static method 'identityMonogram' from outside of its actor context are implicitly asynchronous
117 |     let normalized = title.precomposedStringWithCompatibilityMapping.trimmingCharacters(in: .whitespacesAndNewlines)
118 |     var words: [[Character]] = []

[#ActorIsolatedCall]: <https://docs.swift.org/compiler/documentation/diagnostics/actor-isolated-call>
[151/158] Compiling SWCFeaturesTests FleetFixtureTests.swift
[152/158] Compiling SWCFeaturesTests RecentChatGroupsTests.swift
[153/158] Compiling SWCFeaturesTests LinkedProjectViewTests.swift
[154/158] Compiling SWCFeaturesTests NavigationTests.swift
[155/158] Compiling SWCFeaturesTests SidebarSelectionTests.swift
[156/158] Compiling SWCFeaturesTests ConnectPhonesTests.swift
[156/158] Write Objects.LinkFileList
[157/158] Linking SWCKitPackageTests
Build complete! (22.96s)
Test Suite 'Selected tests' started at 2026-11-03 19:04:45.763.
Test Suite 'SWCKitPackageTests.xctest' started at 2026-11-03 19:04:45.765.
Test Suite 'SWCKitPackageTests.xctest' passed at 2026-11-03 19:04:45.765.
	 Executed 0 tests, with 0 failures (0 unexpected) in 0.000 (0.000) seconds
Test Suite 'Selected tests' passed at 2026-11-03 19:04:45.765.
	 Executed 0 tests, with 0 failures (0 unexpected) in 0.000 (0.002) seconds
◇ Test run started.
↳ Testing Library Version: 1501
↳ Target Platform: arm64e-apple-macos14.0
◇ Suite "Router" started.
◇ Test pendingPhotoBatchesFollowTheirDraftAcrossNavigation() started.
✔ Test pendingPhotoBatchesFollowTheirDraftAcrossNavigation() passed after 0.011 seconds.
✔ Suite "Router" passed after 0.011 seconds.
✔ Test run with 1 test in 1 suite passed after 0.012 seconds.
```

## Acceptance criteria

1/1 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x (tasks) | met | Pending photo loads and encoding block send until all batches settle. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | codex@antons-macbook-m4max | 51af816c00; exact-source slow-photo regression passed, SWCK… |  |

1/1 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
