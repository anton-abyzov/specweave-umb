# 1135 Audit GitHub Actions costs and alerts

## Problem
Anton reports an approximately $500 GitHub charge without a verified period or project breakdown. Actions spend notifications must arrive at each additional $50, remain in Inbox, and be categorized.

## Scope
In: authenticated personal and accessible organization billing records, invoices and payment status, previous and current periods, project/workflow/runner/storage/retry attribution, quantified savings proposals, threshold alerts and Gmail categorization.
Out: changing CI workflows, disabling required checks, spending caps, purchases, credential rotation, other service monitors, or release ownership changes.

## Acceptance Criteria
- [ ] AC-01: Evidence identifies accessible billing accounts, exact usage and invoice periods, paid versus accrued amounts, credits and current forecast; inaccessible evidence remains explicitly unknown.
- [ ] AC-02: Projects and cost drivers are ranked from billed evidence; estimates are separately labeled and savings preserve required test and release protections.
- [ ] AC-03: Notifications use verified anton.abyzov@gmail.com, cross $50/$100/$150 and every additional $50, reset by billing period, deduplicate and catch up missed crossings without imposing a spending stop.
- [ ] AC-04: Existing monitors and Gmail labels/filters are inventoried; alerts retain Inbox and receive Billing/GitHub Actions; configuration and clearly marked test delivery are read back.
- [ ] AC-05: Changes receive appropriate checks and fresh-context review; unavailable external permissions and unverified delivery remain open gates.

## Approach
First collect read-only evidence under this increment's reports directory. Verify GitHub identity, organization membership, current official billing documentation and API access. Reconcile invoices with net Actions usage, discounts and credits rather than multiplying raw minutes. Inspect cost-leading workflows without editing them. Prefer native alert-only budgets if exact thresholds are supported; otherwise implement a small durable monitor only after billing API and sender availability are established. Monitor state must identify account, billing period and successfully delivered threshold; uncertain sends require reconciliation. No alert scheduler will be enabled without a working data source and sender. Configuration evidence and validation go under reports; any monitor source and tests go under monitoring after approach refinement from real APIs.

## Decisions
### Asked
- D-01: Gmail access is not authorized for this project. User enabled Gmail; live read access verified. Label/filter/sender capability remains unavailable through native project tools.
### Defaulted
- D-02: Alert metric is net accrued Actions charges after included usage/discounts, before tax, aggregated across verified billing accounts; gross and forecast remain separate.
- D-03: Keep CI untouched; recommendations only until current owners coordinate changes.
- D-04: GitHub authenticated account email verifies anton.abyzov@gmail.com; do not use the mistyped gmai.com address.
### Open
- Exact billing periods, billing API access and permitted delivery mechanism require evidence.

## Tasks

### T-01 Verify billing identity, invoices and periods
- AC: AC-01 | Files: reports/billing-evidence.json, reports/audit.md | Test: reconcile authenticated API and invoice totals with captured source identifiers

### T-02 Attribute costs and quantify safe savings
- AC: AC-02 | Files: reports/cost-breakdown.json, reports/audit.md | Test: reconcile project totals against net billed Actions totals; distinguish estimated workflow allocation

### T-03 Configure threshold alerts and inbox categorization
- AC: AC-03, AC-04 | Files: monitoring/, reports/alert-configuration.json | Test: verify native configuration or monitor period reset, deduplication, gap catchup and clearly marked delivery readback

### T-04 Verify and close 1135
- AC: AC-05 | Files: reports/review.md, reports/verification.md | Test: specweave verify 1135 followed by fresh-context review and specweave complete 1135 only when all gates pass
