# Personal assistant is named Percy everywhere, not Aide

## Problem

The owner calls the personal assistant Percy, and their own assistant already carries that name, but the product still says Aide in the app, the phone apps, the landing page and the docs.

## Scope

In: every name a person or an agent reads in the app (apps/web, apps/server, packages), the iPhone and Android app sources, the /code landing page and docs (specweave docs-site), and a one-time rename of an assistant still carrying the old default title. Out: identifiers, file names, setting keys, command ids and released changelog entries; phone store submissions.

## Acceptance Criteria

- [ ] AC-01: The desktop and web app show Percy wherever they showed Aide, in every language; searching settings or the palette for "aide" still finds it.
- [ ] AC-02: A new assistant is created as Percy, and an assistant still titled with the old default becomes Percy once on start; a name the person chose is kept.
- [ ] AC-03: The iPhone and Android app sources say Percy.
- [ ] AC-04: The /code landing page and docs say Percy in every locale.

## Approach

Rename strings only, by hand per hit, never identifiers or stored keys. The default name constant changes in contracts; a small idempotent server start step renames a default-titled assistant through the normal rename command. Translations rename key and value together.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Spelling is "Percy": no earlier spelling exists in the repos, history or memory, and the owner's own assistant is titled Percy.
- D-02 Internal names (aideEnabled, file names, ids) stay, so settings and history keep working.
- D-03 An assistant titled exactly "Aide" is treated as never renamed and becomes Percy.
### Open
- none

## Tasks

### T-01 App, server and translations
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/project.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/assistantTerms.ts | Test: gh pr checks --required -R anton-abyzov/specwithcode feat/percy-rename

### T-02 iPhone and Android sources
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCSync/ShellSummaries.swift, repositories/anton-abyzov/specwithcode/apps/android/sync/src/main/kotlin/ShellSummaries.kt | Test: cd repositories/anton-abyzov/specwithcode/apps/ios && make test-core

### T-03 Landing page and docs
- AC: AC-04 | Files: repositories/anton-abyzov/specweave/docs-site/src/components/code/benefits/Benefits.tsx | Test: curl -s https://spec-weave.com/code/ | grep -q Percy

### T-04 Verify and close 1317
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/CHANGELOG.md | Test: bash repositories/anton-abyzov/specwithcode/scripts/release/request-release.sh --released HEAD
