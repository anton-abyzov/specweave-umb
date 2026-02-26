# DORA Metrics Dashboard

> **Auto-generated** by SpecWeave Release Management Plugin.
> For live data, see [spec-weave.com/docs/metrics](https://spec-weave.com/docs/metrics).

## Data Sources

- **Latest Snapshot**: `.specweave/metrics/dora-latest.json`
- **Detailed Report**: `.specweave/metrics/dora-report.md`
- **History File**: `.specweave/metrics/dora-history.jsonl`
- **Update Frequency**: Twice daily at 06:00 and 18:00 UTC via GitHub Actions

## Tier Definitions

| Metric | Elite | High | Medium | Low |
|--------|-------|------|--------|-----|
| **Deployment Frequency** | >365/year | 52-365/year | 12-52/year | <12/year |
| **Lead Time for Changes** | <1 hour | 1 hour - 1 week | 1 week - 1 month | >1 month |
| **Change Failure Rate** | 0-15% | 15-30% | 30-45% | >45% |
| **Mean Time to Recovery** | <1 hour | 1 hour - 1 day | 1 day - 1 week | >1 week |

## Notes

- Metrics calculated from GitHub API data (commits, releases, issues)
- Deployment frequency counts commits to `develop` branch
- Incidents tracked via issues labeled `incident` or `production-bug`
- Rolling averages and trends computed by the release management plugin

---

*Generated automatically by SpecWeave Release Management Plugin*
