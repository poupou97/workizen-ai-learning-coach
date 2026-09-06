# 14 · JIRA AND CONFLUENCE STATUS

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

Raw evidence: `evidence/jira-confluence-status.txt`. Configuration of record: `.workforce.json`
(archived at `manifests/workforce-config.json`) — `jiraProject: WAL · confluenceSpace: WAL`.

---

## 1. THE HEADLINE — three consecutive rounds now have no tracker artefact

**Status: NOT TRACKED. Label: PROVEN — queried live on 2026-09-06.**

| Tracker | Result |
|---|---|
| **Jira WAL** — `project = WAL AND updated >= "2026-09-06"` | **0 issues.** No WAL issue was created, transitioned or commented on the day round 7 ran. |
| **Jira WAL** — newest activity of any kind | **2026-09-05T16:29 (+0700)** — unchanged since the round-5 archive |
| **Confluence WAL** | **Newest page last-modified 2026-09-02.** 20 pages (`00 — Start Here` … `19 — Coverage Dashboard`). **No page for rounds 3, 4, 5, 6 or 7.** |

**Rounds 5, 6 and 7 have each closed with nothing in either tracker.** The gap between the tracker
and reality is now **three rounds and roughly 170 commits wide.**

## 2. HOW ROUND 7 WAS ACTUALLY TRACKED

**By git branches, pull requests, committed markdown — and, new this round, by hashed artefacts.**

| Artefact | Quality |
|---|---|
| Plan **and five acceptance gates**, committed `1e31512` **before any work** | **PROVEN** — predates every workstream PR |
| Four branches, four PRs, all CI-green | **PROVEN** — heads and CI re-verified |
| Six workstream documents, ~1,970 lines | in `reports/` |
| Consolidated Founder report, 283 lines | every number verified by the coordinator |
| **`ROUND7-HISTORICAL-CORRECTIONS.md` (C1–C5)** | corrections recorded **beside** round 6's report, which is **unchanged** |
| **The frozen calibration chain** — `LEDGER.jsonl` + four payloads | **the strongest tracking artefact this project has produced: an append-only hash chain that refuses at write time** |
| The debt triage — **30 rows, nothing dropped** | in `reports/ws-r-round6-debt/` |

**A reader consulting only Jira and Confluence today would believe the project's last activity was
2026-09-05.** They would not know that a trust gate exists, that it is frozen, that calibration has
been measured insufficient, or that 22 imprint blocks reach children.

## 3. THE PAGES THAT ARE NOW ACTIVELY WRONG

Not merely stale — **wrong in a way a reader cannot detect from the page**:

| Page | Last modified | Why it is now wrong |
|---|---|---|
| **19 — Coverage Dashboard** | 2026-09-02 | Its denominators predate the R13 accounting fix **and** round 7's finding that **3,679 / 3,240 / 3,650 / 3,381 are one leaf population under four grouping keys** — a **definition** question, not a data conflict. |
| **15 — Current Status** | 2026-09-02 | Predates rounds 3–7. |
| **03 — Educational Knowledge Model** | 2026-09-01 | Predates the repair/disposition layer, the trust gate and the structured-gap findings. |
| **11 — UI/UX & Design System** | 2026-09-02 | Predates Workspace Option B shipping, and the title-casing rule. |

**This is the hazard the workspace root `CLAUDE.md` warns about**, and round 7 supplies a fresh
instance of the same species in code: **a metric that could not distinguish «not applicable» from
«not asked»**, and **a gate green because the thing it guards was absent**. *A page can be green
for the same reason.*

**`19 — Coverage Dashboard` is in exactly that position, and nothing in CI will ever notice.**

## 4. RECOMMENDATION — Founder decision, not taken here

Three options, unchanged from the round-5 and round-6 archives and now one round more urgent:

1. **Backfill per round** — one Jira epic per round, one issue per workstream, one Confluence page
   mirroring the consolidated report. Cost: real and recurring.
2. **Declare git + PRs + these per-round archives the system of record**, and mark Jira/Confluence
   **historical, not current** — with a banner on `15 — Current Status` and `19 — Coverage
   Dashboard`. **Cost: low. Honest.**
3. **Backfill only the two stale-and-load-bearing pages** and leave the rest as a dated snapshot.

**The archive builder's view is unchanged across three archives: option 2, with the two banners from
option 3.** The evidence trail in git is now **stronger than it has ever been** — round 7 added a
hash chain that refuses at write time. **The danger is not the absence of tickets; it is the presence
of confidently wrong numbers on a dashboard nobody has retracted.**

**No tracker was modified by this archive task.** Jira and Confluence edits are inside the
autonomous list, but this task's scope is the archive — so the state above is **reported, not
changed.**
