# 1197 Preserve report headings when frontmatter supplies the title

## Problem

A report with a frontmatter title loses a distinct opening H1 in the document reader.

## Scope

Preserve an opening section title when frontmatter independently names the report. Keep deduplication for a plain duplicate title and for a marked-up H1 that supplies the title itself.

## Acceptance Criteria

- [ ] AC-01 A distinct opening H1 and its content remain a section when frontmatter supplies the report title.

## Approach

Use the same scalar frontmatter title predicate as the title resolver to guard the fallback H1 removal. Cover a distinct title and a duplicate plain title in the shared report renderer suite.

## Tasks

### T-01 Preserve independent opening headings

- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode-dev/packages/shared/src/reportDocument.ts, repositories/anton-abyzov/specwithcode-dev/packages/shared/src/reportDocument.test.ts | Test: cd "repositories/anton-abyzov/specwithcode-dev/packages/shared" && node ../../node_modules/vite-plus/bin/vp test run src/reportDocument.test.ts src/threadReport.test.ts
