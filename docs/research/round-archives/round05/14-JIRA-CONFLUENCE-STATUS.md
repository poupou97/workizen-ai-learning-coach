# 14 · JIRA AND CONFLUENCE STATUS

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

Raw evidence: `evidence/jira-confluence-status.txt`.
Configuration of record: `.workforce.json` at the repository root —
`cloudId: workizen.atlassian.net · jiraProject: WAL · confluenceSpace: WAL`.

---

## 1. THE HEADLINE — round 5 is not in either tracker

**Status: NOT TRACKED. Label: PROVEN — queried live by the archive builder on 2026-09-06.**

| Tracker | Query | Result |
|---|---|---|
| **Jira WAL** | `project = WAL AND updated >= "2026-09-05" ORDER BY updated DESC` | **6 issues touched — none of them a round-5 issue.** Newest update anywhere in the project: **2026-09-05T16:29 (+0700)**, which is *before six of the ten round-5 PRs existed*. |
| **Confluence WAL** | `space = WAL AND type = page ORDER BY lastmodified DESC` | **20 pages (00–19). Newest last-modified: 2026-09-02.** **No page created or updated for round 3, round 4 or round 5.** |

**No Jira issue was created, transitioned or commented for any of the nine round-5 lanes. No
Confluence page records round 5.**

## 2. WHAT JIRA DOES SHOW

| Key | Type | Status | Last updated | Summary |
|---|---|---|---|---|
| WAL-209 | Task | **Done** | 2026-09-05 16:29 | [P0] TC-v2 Science Slice — Source → SDM → block trust → Role Layer → guards → attachment → Trusted Structured Lesson |
| WAL-210 | Task | **Done** | 2026-09-05 16:29 | [P0] B-lane after pre-autonomy checkpoint — gates before growth |
| WAL-195 | Epic | Ideas | 2026-09-05 10:40 | [ARCH] Education Data Architecture & Learning Graph Research |
| WAL-206 | Story | **QA** | 2026-09-05 02:14 | [P0] Layout-aware K-12 extraction — reading order, columns, block roles from OCR geometry |
| WAL-207 | Task | **QA** | 2026-09-05 02:14 | [P0 Research] Learning Views concept & reference research |
| WAL-208 | Task | **Done** | 2026-09-05 02:14 | [RESEARCH] Trusted-Corpus Feasibility Study (TC-v1) |

**These are round-3/round-4-era tickets.** WAL-209 and WAL-210 were closed on 2026-09-05, the day
round 5 opened. **Two issues sit in `QA` (WAL-206, WAL-207) and have not moved since 2026-09-05
02:14** — they are the closest thing to open round-5-adjacent work in the tracker, and neither was
touched by any round-5 lane.

## 3. WHAT CONFLUENCE DOES SHOW

Space **WAL** holds the 20-page backfill created by the Founder on 2026-09-01/02
(`00 — Start Here` … `19 — Coverage Dashboard`), exactly as `.workforce.json` records:
*"backfill 10 Epic + 34 issue + 16 trang Confluence (00–15) hoàn tất cùng ngày"*.

**Pages most affected by round-5 findings, and now stale:**

| Page | Last modified | Why it is now stale |
|---|---|---|
| **15 — Current Status** | 2026-09-02 | Predates rounds 3, 4 and 5 entirely |
| **19 — Coverage Dashboard** | 2026-09-02 | Every coverage figure on it uses a denominator **R13 has shown to be wrong**, and a lesson count (`3,679`) that E1 has challenged (3,240 distinct keys) |
| **03 — Educational Knowledge Model** | 2026-09-01 | E1 refuted three planned per-subject graph subsystems and reduced the core to 6 primitives · 6 relations |
| **11 — UI/UX & Design System** | 2026-09-02 | Predates the workspace A/B/C study and the Founder's selection of option B |

## 4. HOW ROUND 5 WAS ACTUALLY TRACKED

**By git branches, pull requests and committed markdown reports.** That is not a criticism — it is
what happened, and the evidence trail is strong:

| Artefact | Where | Quality |
|---|---|---|
| Lane ownership + scope boundaries | `docs/research/ROUND5-PLAN.md` | committed before the round |
| Per-lane deliverables | 9 branches, 9 PRs, all CI-green | **PROVEN** — heads and CI re-verified |
| Per-lane reports | ~20 committed markdown documents (all in `reports/`) | verified by the coordinator against the repo |
| Consolidated Founder report | `ROUND5-CONSOLIDATED-REPORT-2026-09-06.md`, 1,034 lines | every number re-checked before being written down |
| Device evidence | `docs/design/track-b-evidence/round5/` + manifest | **PROVEN** — 36/36 hashes recomputed |
| Round closure | the composition check + this archive | |

**The tracker is the only weak link, and it is weak in a specific way:** a person who reads only
Jira and Confluence today would believe the project's last activity was **2026-09-05**, would not
know that R13 exists, and would still be quoting the coverage dashboard's denominators.

## 5. THE RISK THIS CREATES

The workspace root `CLAUDE.md` records the precedent explicitly: a founder question stayed listed
as open for **over two months** after it was closed, code cited that stale listing as a reason not
to build, and **a decision was ratified on the expired premise**. *"Stale doctrine blocks as hard
as a real gate, and no test catches it."*

**Confluence page `19 — Coverage Dashboard` is now in exactly that position.** It publishes
coverage figures computed on a denominator that R13 has invalidated and a lesson count E1 has
challenged. Nothing in CI will ever notice.

## 6. RECOMMENDATION — Founder decision, not taken here

Three options, stated without choosing:

1. **Backfill the trackers per round.** One Jira epic per round with one issue per lane, and one
   Confluence page per round mirroring the consolidated report. Cost: real, recurring.
2. **Declare git + PRs + these per-round archives the system of record**, and mark Jira/Confluence
   explicitly as *historical, not current* — including a banner on `15 — Current Status` and
   `19 — Coverage Dashboard`. Cost: low. Honest.
3. **Backfill only the stale-and-load-bearing pages** — `15 — Current Status` and
   `19 — Coverage Dashboard` — and leave the rest as a dated snapshot.

**The archive builder's view:** option 2 with the two banners from option 3. The evidence trail in
git is stronger than anything the tracker holds; the danger is not the absence of tickets but the
**presence of confidently wrong numbers** on a dashboard nobody has retracted.

**No tracker was modified by this archive task.** Creating or editing Jira issues and Confluence
pages is inside the round-6 autonomous list, but this task's scope is the archive — so the state
above is **reported, not changed**.
