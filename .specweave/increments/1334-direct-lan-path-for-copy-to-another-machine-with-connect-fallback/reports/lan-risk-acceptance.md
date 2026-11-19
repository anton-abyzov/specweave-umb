# LAN path: residual risk acceptance

Recorded November 19, 2026, about 10:18 a.m. EST. Anton answered the question card in the 1390 coordinator thread with "Accept all three".

The question he answered:

> The LAN path for Sync and Add passed its security design review, and the code is being built with the setting off. It can only be turned on after you accept three leftover risks. R-01: a machine you opt in learns your other machine's private IP addresses. R-02: other devices on the same network can see that a temporary encrypted connection exists and how much data it carries, but not the contents. R-03: a firewall prompt or Wi-Fi client isolation can block the LAN path; the copy then runs over Connect as it does today. Do you accept them?

| Risk | Status |
|---|---|
| R-01: an opted-in destination learns the source's offered private addresses | Accepted by Anton, November 19, 2026 |
| R-02: local observers can see a temporary TLS endpoint and how much traffic it carries | Accepted by Anton, November 19, 2026 |
| R-03: an OS firewall prompt or client isolation can prevent the LAN path; the copy then runs on Connect | Accepted by Anton, November 19, 2026 |

This meets gate 4 of S-11 and the acceptance half of AC-35 only. The setting stays off by default. It still cannot be turned on until an implementation review confirms that findings 1 to 4 are fixed in code with the real-socket tests of AC-36, and the per-OS evidence of AC-34 is recorded. The help text must still state R-01 to R-03 in plain words.

Design reviews: `.specweave/increments/1390-sync-projects-across-machines-and-hand-off-work/reports/reviews/security-review-lan-listener-4.md` (DESIGN OK) and the earlier rounds beside it.
