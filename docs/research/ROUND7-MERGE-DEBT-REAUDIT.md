# Round 7 §10 — MERGE DEBT RE-AUDIT against current repository state

**Verdict: the round-6 recommendation is UNCHANGED and still correct.**
**MERGE #79 · CLOSE #73 AS SUBSUMED · HOLD the remaining round-5 and round-6 PRs.**
Nothing merged in producing this.

## 1 · Re-verified, not restated

| Check | Round 6 | Now |
|---|---|---|
| Is #73 an ancestor of #79? | YES | **YES** |
| Is `main` an ancestor of #79? | YES | **YES — `main` has not moved (`61dbfdb`)** |
| Delta #73 → #79 | 16 commits, 3 files, docs only | **identical — 16 commits, 3 files, all `docs/research/`** |
| Does #79 contain round-5 lane code? | No | **No** |

So merging #79 still carries exactly the code risk of #73 — Founder-ACCEPTED — plus documentation, and ships none of the unreviewed lane work. **Option C (selective) remains actively harmful on linear history; Option A (merge #73) remains pointless.**

## 2 · What changed, and it is the Founder's §10 concern arriving

The debt is now **four stacked unmerged integration layers**:

```
main
 └─ #73  integration/round4   73 commits   ACCEPTED, unmerged
     └─ #79  integration/round5   +16 commits (docs only)
         └─ integration/round6      +119 commits  (the nine round-5 lane branches)
             └─ integration/round7    + the five round-6 workstream branches
```

**`integration/round7-2026-09-06` is 254 commits ahead of `main`.**

The round-7 base composed cleanly (0 conflicts, all five round-6 branches), and round 6's composition was verified green — `flutter analyze` clean, 748 Python, 1084 Dart. So the stack is *sound*; it is the **depth** that is the risk, not the correctness.

**This is precisely what §10 said must not happen, and it has now happened once more.** Round 7 is a composition on top of a composition on top of a composition. Each layer's only integration evidence is a throw-away worktree that no CI reproduces, and `main` still contains none of rounds 4, 5 or 6.

## 3 · The specific risks of another round at this depth

- **No CI ever builds what the Founder would merge.** Per-PR CI builds each branch against its own base; only the disposable composition builds the whole. Round 6 proved that gap is not theoretical — three stale test premises and a plugin-registry defect were invisible to per-PR CI.
- **Bisect is compromised.** A regression introduced in round 5 and surfacing in round 7 must be bisected across 254 commits containing four merge fronts.
- **Rebase cost compounds.** Round 6 already paid it once: WS-C carried WS-A's commit, `patch-id` proved a duplicate, and a rebase was required to make PR #90 reviewable.
- **`main` is now ~4 rounds stale.** Any hotfix to `main` would branch from a tree that predates silent-loss accounting, the repair framework, recognition, and the honest Bài 8 fixture.

## 4 · Recommendation, unchanged and now more urgent

**Merge #79** (risk = accepted round 4 + docs). **Close #73** as subsumed. **Hold #80–#88 and #89–#93** — they remain unreviewed, and three touch code that round 7 will change.

If the Founder prefers integration branches to stay permanently unmerged, that is a legitimate policy — but it should be **stated as policy**, and integration branches should then stop being treated as a delivery path, because at four layers they no longer function as one.

**DO NOT MERGE — Founder approval required. This document is an audit, not an action.**
