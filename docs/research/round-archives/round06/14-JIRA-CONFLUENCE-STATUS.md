# 14 · JIRA AND CONFLUENCE STATUS

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

Raw evidence: `evidence/jira-confluence-status.txt`. Configuration of record: `.workforce.json` —
`cloudId: workizen.atlassian.net · jiraProject: WAL · confluenceSpace: WAL`.

---

## 1. THE HEADLINE — round 6 is not in either tracker, and neither is round 5

**Status: NOT TRACKED. Label: PROVEN — queried live on 2026-09-06.**

| Tracker | Query | Result |
|---|---|---|
| **Jira WAL** | `project = WAL AND updated >= "2026-09-06"` | **0 issues. Empty result set.** No WAL issue was created, transitioned or commented **on the day round 6 ran.** |
| **Jira WAL** (widened) | newest activity of any kind | **2026-09-05T16:29 (+0700)** — round-3/4-era tickets (WAL-209, WAL-210 closed; WAL-206, WAL-207 sitting in **QA**) |
| **Confluence WAL** | space WAL, by last-modified | **Newest page: 2026-09-02.** 20 pages (`00 — Start Here` … `19 — Coverage Dashboard`). **No page for round 3, 4, 5 or 6.** |

**Unchanged since the round-5 archive was built.** Two consecutive rounds have now closed without a
single tracker artefact.

## 2. HOW ROUND 6 WAS ACTUALLY TRACKED

**By git branches, pull requests and committed markdown** — and the evidence trail is strong:

| Artefact | Where | Quality |
|---|---|---|
| Plan **and acceptance gates**, committed **before** the work | `ROUND6-PLAN.md` @ `1a75d24` + addendum `51711c0` | **PROVEN** — predates every workstream PR |
| Per-workstream deliverables | 4 branches, 4 PRs, all CI-green | **PROVEN** — heads and CI re-verified |
| Per-workstream reports | 5 committed markdown documents, ~1,600 lines | all in `reports/` |
| Consolidated Founder report | `ROUND6-CONSOLIDATED-REPORT-2026-09-06.md`, 342 lines | every number verified by the coordinator |
| Device evidence | `~/Desktop/wal-evidence/round6-ws-d/` + manifest | **PROVEN** — 7/7 hashes recomputed |
| **The artefacts a gate depends on** | `~/Desktop/wal-evidence/round6-artefacts/` | **PROVEN** — fixture hash matches the manifest; 12/12 pack hashes match |
| Round closure | the composition check + this archive | |

**The gap between the tracker and reality is now two rounds wide.** A person reading only Jira and
Confluence today would believe the last activity was **2026-09-05**, would not know that **R13 is
closed**, that a `ValidatedRepair` has crossed into the app, or that the canonical lesson count has
been measured — **and would still be quoting the coverage dashboard's superseded denominators.**

## 3. THE PAGES THAT ARE NOW ACTIVELY WRONG

Not merely stale — **wrong in a way a reader cannot detect from the page**:

| Page | Last modified | Why it is now wrong |
|---|---|---|
| **19 — Coverage Dashboard** | 2026-09-02 | Its coverage figures use denominators **R13 has invalidated** and a lesson count round 6 has **measured differently** (`3,650`, with `3,240` shown to **delete 410 real lessons**). |
| **15 — Current Status** | 2026-09-02 | Predates rounds 3, 4, 5 **and 6**. |
| **03 — Educational Knowledge Model** | 2026-09-01 | Round 5's E1 refuted three planned per-subject graph subsystems; round 6 added the repair/disposition layer. |
| **11 — UI/UX & Design System** | 2026-09-02 | Predates the workspace A/B/C study, the Founder's choice of B, **and B shipping**. |

**This is precisely the hazard the workspace root `CLAUDE.md` warns about**: a founder question
stayed listed as open for **over two months** after it was closed, code cited that stale listing as
a reason not to build, and **a decision was ratified on the expired premise**. *"Stale doctrine
blocks as hard as a real gate, and no test catches it."*

**`19 — Coverage Dashboard` is in exactly that position, and nothing in CI will ever notice.**

## 4. RECOMMENDATION — Founder decision, not taken here

Three options, unchanged from the round-5 archive and now one round more urgent:

1. **Backfill the trackers per round.** One Jira epic per round, one issue per workstream, one
   Confluence page mirroring the consolidated report. Cost: real and recurring.
2. **Declare git + PRs + these per-round archives the system of record**, and mark Jira/Confluence
   explicitly as *historical, not current* — with a banner on `15 — Current Status` and
   `19 — Coverage Dashboard`. **Cost: low. Honest.**
3. **Backfill only the stale-and-load-bearing pages** and leave the rest as a dated snapshot.

**The archive builder's view is unchanged: option 2, with the two banners from option 3.** The
evidence trail in git is stronger than anything the tracker holds. **The danger is not the absence
of tickets — it is the presence of confidently wrong numbers on a dashboard nobody has retracted**,
and that danger has now grown by a second round.

**No tracker was modified by this archive task.** Jira and Confluence edits are inside round 6's
autonomous list, but this task's scope is the archive — so the state above is **reported, not
changed.**
