# Windows CI observation

PR #995, head 914455629b6a134d019e1cec4a7f9d8d07c52bd5. Job https://github.com/anton-abyzov/specwithcode-dev/actions/runs/40817085570/job/123261188656 failed two unchanged fleetSkills.test.ts launcher tests; 158 files / 2442 tests passed. Production fleetSkills.ts and its tests are unchanged by #995. Active PR #991 owns the Windows PATH/PATHEXT/npm launcher repair. This is recorded as an outstanding Windows platform defect, not a passing Windows run. Required PR gates and the canonical macOS release suite are checked separately.

```text
2026-10-29T04:44:27.8795844Z  FAIL  src/fleet/fleetSkills.test.ts > the live fleet skill worker > finds vskill on PATH, runs it without a shell in the project and reads its lock
2026-10-29T04:44:27.8798101Z  FAIL  src/fleet/fleetSkills.test.ts > the live fleet skill worker > drops the pin in the project's own lock, not a parent SpecWeave project's lock
2026-10-29T04:44:27.8801459Z StudioFleetSkillError: vskill is not installed on this machine (looked on PATH, ~/.local/bin, /opt/homebrew/bin, /usr/local/bin and npm's global bin). Install it with npm i -g vskill there.
2026-10-29T04:44:27.8827467Z  Test Files  1 failed | 158 passed | 5 skipped (164)
2026-10-29T04:44:27.8829060Z       Tests  2 failed | 2442 passed | 34 skipped (2478)
2026-10-29T04:44:28.0398445Z ##[error]StudioFleetSkillError: vskill is not installed on this machine (looked on PATH, ~/.local/bin, /opt/homebrew/bin, /usr/local/bin and npm's global bin). Install it with npm i -g vskill there.
2026-10-29T04:44:28.0581672Z ##[error]StudioFleetSkillError: vskill is not installed on this machine (looked on PATH, ~/.local/bin, /opt/homebrew/bin, /usr/local/bin and npm's global bin). Install it with npm i -g vskill there.
```

## Shard 1

Unchanged Windows path/placement tests also failed; these files are not modified by #995.

```text
2026-10-29T04:48:48.8400632Z  FAIL  src/worktreesDirectory.test.ts > resolves modes without moving or reinterpreting saved legacy roots
2026-10-29T04:48:48.8431567Z  Test Files  1 failed | 160 passed (161)
2026-10-29T04:48:48.8432072Z       Tests  1 failed | 2274 passed | 35 skipped (2310)
```

## Shard 3

Unchanged Windows path/placement tests also failed; these files are not modified by #995.

```text
2026-10-29T04:48:39.4774120Z  FAIL  src/handoff/handoffPlacement.test.ts > reuses a registered checkout across storage changes without touching retained edits
2026-10-29T04:48:39.4795682Z  Test Files  1 failed | 161 passed | 1 skipped (163)
2026-10-29T04:48:39.4797691Z       Tests  1 failed | 2224 passed | 13 skipped (2238)
```

## Shard 2

The project skills version suite also hits the same pre-existing Windows executable discovery failure (vskill-missing). One added drift test shares that harness; it never reaches its drift assertion on Windows. PR #991 already includes ProjectSkillsActions/Common/Rpc and portable fixture repairs. Keep that active owner lane intact. macOS focused tests and full canonical release tests pass; Windows compatibility is not claimed complete here.

```text
2026-10-29T04:52:05.7497291Z  FAIL  src/project/ProjectSkillsActions.test.ts > ProjectSkillsActions with a stand-in vskill > lists versions and reads outdated even though it exits 1
2026-10-29T04:52:05.7499955Z  FAIL  src/project/ProjectSkillsActions.test.ts > ProjectSkillsActions with a stand-in vskill > previews an install without running it, then installs and reads the lock back
2026-10-29T04:52:05.7514296Z  FAIL  src/project/ProjectSkillsActions.test.ts > ProjectSkillsActions with a stand-in vskill > updates to latest and drops the pin the install sets when there was none
2026-10-29T04:52:05.7517025Z  FAIL  src/project/ProjectSkillsActions.test.ts > ProjectSkillsActions with a stand-in vskill > refuses registry drift and missing preview before updating latest
2026-10-29T04:52:05.7519662Z  FAIL  src/project/ProjectSkillsActions.test.ts > ProjectSkillsActions with a stand-in vskill > keeps the pin on update when the skill was pinned before
2026-10-29T04:52:05.7522456Z  FAIL  src/project/ProjectSkillsActions.test.ts > ProjectSkillsActions with a stand-in vskill > refuses a pin that would change another project's lock, and installs in the lock's folder
2026-10-29T04:52:05.7525297Z  FAIL  src/project/ProjectSkillsActions.test.ts > ProjectSkillsActions with a stand-in vskill > refuses writes for a user skill recorded only in the older ~/vskill.lock
2026-10-29T04:52:05.7532626Z  FAIL  src/project/ProjectSkillsActions.test.ts > ProjectSkillsActions with a stand-in vskill > installs with pin: false and drops the pin, as Undo of an unpinned change does
2026-10-29T04:52:05.7535464Z  FAIL  src/project/ProjectSkillsActions.test.ts > ProjectSkillsActions with a stand-in vskill > pins project locks only and installs user locks with --global from HOME
2026-10-29T04:52:05.7566668Z  FAIL  src/project/ProjectSkillsActions.test.ts > ProjectSkillsActions with a stand-in vskill > refuses a version the registry does not list and a lock that changed
2026-10-29T04:52:05.7596821Z  FAIL  src/project/ProjectSkillsActions.test.ts > ProjectSkillsActions with a stand-in vskill > checks pin and unpin against the lock, not vskill's word
2026-10-29T04:52:05.7626430Z  FAIL  src/project/ProjectSkillsActions.test.ts > ProjectSkillsActions with a stand-in vskill > reports a failed run with its exit code and the end of its output
2026-10-29T04:52:05.7654539Z  FAIL  src/project/ProjectSkillsActions.test.ts > ProjectSkillsActions with a stand-in vskill > checks the lock inside the queue, so a second apply of one preview is stale
2026-10-29T04:52:05.7678357Z  Test Files  1 failed | 162 passed | 3 skipped (166)
2026-10-29T04:52:05.7679861Z       Tests  13 failed | 2048 passed | 58 skipped (2119)
```

## Shard 5

One unchanged ClaudeSettingsWrite.test.ts assertion expects POSIX mode 0600 but Windows reports 0666; 161 files / 2159 tests passed. The write/hash assertions passed before the mode assertion. This is a Windows fixture limitation, not proof of Windows ACL enforcement; no permission assertion was weakened.

Job: https://github.com/anton-abyzov/specwithcode-dev/actions/runs/40817085570/job/123261188787

## Windows web

The complete Windows web run also fails unchanged RightPanelTabs fixtures and worker startup; the Linux web shards and macOS release web suite passed.

```text
2026-10-29T05:00:43.4032207Z  FAIL   unit  src/components/RightPanelTabs.keyboard.test.tsx > right panel new-tab shortcut > supports arrow keys with an existing tab in sheet mode and clears the menu on close
2026-10-29T05:00:43.4066360Z  FAIL   unit  src/components/RightPanelTabs.keyboard.test.tsx > file reader close, Escape and focus (1049 AC-06) > C1/C6: shows a labeled Close with no hover, and it closes and returns focus
2026-10-29T05:00:43.4077724Z  FAIL   unit  src/components/RightPanelTabs.keyboard.test.tsx > file reader close, Escape and focus (1049 AC-06) > C3: an editor in the reader keeps Escape
2026-10-29T05:00:43.4090810Z  FAIL   unit  src/components/RightPanelTabs.keyboard.test.tsx > file reader close, Escape and focus (1049 AC-06) > C4: an open menu or a combobox showing its list keeps Escape
2026-10-29T05:00:43.4104012Z  FAIL   unit  src/components/RightPanelTabs.keyboard.test.tsx > file reader close, Escape and focus (1049 AC-06) > C5: a write in flight keeps the reader open on Escape, and the labeled Close still closes
2026-10-29T05:00:43.4118247Z  FAIL   unit  src/components/RightPanelTabs.keyboard.test.tsx > file reader close, Escape and focus (1049 AC-06) > C7: a link that left the page gets no focus, and closing does not throw
2026-10-29T05:00:43.4129044Z  FAIL   unit  src/components/RightPanelTabs.keyboard.test.tsx > file reader close, Escape and focus (1049 AC-06) > C8: a file opened from inside the panel leaves focus there, and Escape still closes it
2026-10-29T05:00:43.4197425Z  FAIL   unit  src/components/RightPanelTabs.keyboard.test.tsx > file reader close, Escape and focus (1049 AC-06) > does not take focus from a field or when a tab is only shown again
2026-10-29T05:00:43.4211355Z  FAIL   unit  src/components/RightPanelTabs.keyboard.test.tsx > file reader close, Escape and focus (1049 AC-06) > C9: a terminal or browser keeps Escape and has no labeled Close
2026-10-29T05:00:43.4222577Z  FAIL   unit  src/components/RightPanelTabs.keyboard.test.tsx > file reader close, Escape and focus (1049 AC-06) > C3: an editor whose field sits in a shadow root keeps Escape
2026-10-29T05:00:43.4233939Z  FAIL   unit  src/components/RightPanelTabs.keyboard.test.tsx > file reader close, Escape and focus (1049 AC-06) > closes on an Escape a framed page in the reader left alone, and only then
2026-10-29T05:00:43.4247583Z  FAIL   unit  src/components/RightPanelTabs.keyboard.test.tsx > file reader close, Escape and focus (1049 AC-06) > C10: a modified Escape is left alone
2026-10-29T05:00:43.4262249Z  FAIL   unit  src/components/RightPanelTabs.keyboard.test.tsx > file reader close, Escape and focus (1049 AC-06) > leaves Escape and focus to the sheet, which hands focus back itself
2026-10-29T05:00:43.4277313Z  FAIL   unit  src/components/RightPanelTabs.keyboard.test.tsx > file links open beside or in front by the room there is (1049 AC-06, D-05) > R3: the conversation would get 559 opens { rowWidth: 1099, panelWidth: 540 }
2026-10-29T05:00:43.4280246Z  FAIL   unit  src/components/RightPanelTabs.keyboard.test.tsx > file links open beside or in front by the room there is (1049 AC-06, D-05) > R4: the reader would get 479 opens { rowWidth: 1280, panelWidth: 479 }
2026-10-29T05:00:43.4284121Z  FAIL   unit  src/components/RightPanelTabs.keyboard.test.tsx > file links open beside or in front by the room there is (1049 AC-06, D-05) > R6: the panel is a sheet over the conversation opens { sheet: true }
2026-10-29T05:00:43.4287114Z  FAIL   unit  src/components/RightPanelTabs.keyboard.test.tsx > file links open beside or in front by the room there is (1049 AC-06, D-05) > R11: the panel is maximized opens { maximized: true }
2026-10-29T05:00:43.4314499Z  FAIL   unit  src/components/RightPanelTabs.keyboard.test.tsx > file links open beside or in front by the room there is (1049 AC-06, D-05) > takes the room from the conversation view once it has measured its row
2026-10-29T05:00:43.4332938Z  FAIL   unit  src/components/RightPanelTabs.keyboard.test.tsx > file links open beside or in front by the room there is (1049 AC-06, D-05) > R12: a page that has not measured itself opens the file in front
2026-10-29T05:00:43.4377910Z  FAIL   unit  src/components/RightPanelTabs.keyboard.test.tsx > file links open beside or in front by the room there is (1049 AC-06, D-05) > R13/R14: a panel already open keeps its tabs, adding the file only when it fits
2026-10-29T05:00:43.4519524Z  FAIL   unit  src/components/RightPanelTabs.keyboard.test.tsx > file links open beside or in front by the room there is (1049 AC-06, D-05) > a link Safari leaves unfocused still opens in front, with focus to return to it
2026-10-29T05:00:43.4531424Z  FAIL   unit  src/components/RightPanelTabs.keyboard.test.tsx > the focused file viewer (1049 AC-06, D-05) > shows the file with the thread beside it, and offers Open beside once both fit
2026-10-29T05:00:43.4544851Z  FAIL   unit  src/components/RightPanelTabs.keyboard.test.tsx > the focused file viewer (1049 AC-06, D-05) > keeps the link's Open in editor and Reveal
2026-10-29T05:00:43.4567264Z  FAIL   unit  src/components/RightPanelTabs.keyboard.test.tsx > the focused file viewer (1049 AC-06, D-05) > offers nothing to open in the panel, an editor or a folder for a file the host lacks
2026-10-29T05:00:43.4578066Z  FAIL   unit  src/components/RightPanelTabs.keyboard.test.tsx > the focused file viewer (1049 AC-06, D-05) > C17: Open beside moves the file into the panel, and its tab returns focus to the link
2026-10-29T05:00:43.4589207Z  FAIL   unit  src/components/RightPanelTabs.keyboard.test.tsx > the focused file viewer (1049 AC-06, D-05) > C11/C15: closing it any way (Escape, Close, a route change) returns focus to the link
2026-10-29T05:00:43.4599605Z  Test Files  1 failed | 753 passed (754)
2026-10-29T05:00:43.4600734Z       Tests  26 failed | 10024 passed (10050)
```
