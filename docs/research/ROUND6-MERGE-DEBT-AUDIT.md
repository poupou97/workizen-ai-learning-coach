# Round 6 · Part II — MERGE DEBT AUDIT

**Recommendation: B — MERGE #79.** It subsumes #73 entirely, and its only delta over
#73 is documentation. **DO NOT MERGE executed — this is a recommendation, not an action.**

---

## 1. The structure of the debt is linear, not divergent

This is the finding that decides the answer, and it was not obvious from the PR list.

| Relationship | Result |
|---|---|
| `origin/main` → #73 (round 4) | **73 commits** |
| `origin/main` → #79 (round 5) | **89 commits** |
| #73 → #79 | **16 commits** |
| **Is #73 an ancestor of #79?** | **YES — #79 already contains all of #73** |
| **Is `main` an ancestor of #79?** | **YES — no divergence; `mergeable: MERGEABLE`, state `CLEAN`, CI `SUCCESS`** |
| #79 → round-6 base | 114 commits (the nine round-5 lane branches) |

**And the delta #73 → #79 is documentation only.** All 16 commits touch **3 files, all
under `docs/research/`** — zero code, zero tests, zero assets:

```
docs(round5): lane plan and ownership · the 97-row audit as an evaluation set
docs(round5): consolidated Founder report (×12 incremental commits)
```

**Therefore merging #79 carries exactly the code risk of merging #73 — which the Founder
has already ACCEPTED — plus a report.**

**Critically: #79 does NOT contain round 5's lane code.** PRs #80–#88 target #79 but were
never merged into it. A1's repair framework is 6 commits ahead of #79; the same is true
of the other eight. So merging #79 ships **round-4 code (accepted) + round-5
documentation**, and **none** of round 5's unreviewed lane work. That is the lowest-risk
way to clear the debt that exists.

---

## 2. Component classification

| Class | Components | Where they live now |
|---|---|---|
| **SAFE FOUNDATION** | LessonDocument model + fail-closed parser (`lib/core/lesson_model/**`) · Learning Views, Smart Book, workspace at round-4 state (`lib/features/**`) · tc2 SDM, role layer, guards at round-4 state · the `pack_provenance` fix that made `verify` honestly FAIL on stale packs (`a281ea5`) · 38 test files under `test/core` and `test/features` | **#73 ⊂ #79** |
| **ROUND 6 REQUIRED** | A1 repair framework (`tool/corpus/repair/**`) → WS-C · A2 mathfix (`tool/corpus/mathfix/**`) → WS-B · Lane D `silent_loss.py` + legacy tooling → WS-A · A4 verify signals + router → WS-C · E1 semantic foundation, E2 VisualSpec, Lane B renderers → WS-D | **round-5 lane branches only** — currently reachable solely through the round-6 base |
| **NEEDS R13 FIX** | `tc2_sdm.py` role layer, specifically the `empty_block` path at `:276-277` — WS-A is changing it this round · every legacy served-share metric and scoreboard, which WS-A will recalculate · anything downstream of the corrected denominators | **round-5 lane branches** — merging these now would merge code that is about to change |
| **OBSOLETED** | **None.** Round 5 added to round 4; it did not supersede it. | — |
| **CAN WAIT** | E2 VisualSpec renderer families (bounded, not expanded in round 6) · Lane C History rules (`PROPOSED`, History-only, and **falsified as a general rule** — 3 events across 28 lessons) · A3 role-definition spec (documentation; the taxonomy is settled but no tuning follows it yet) | round-5 lane branches |

---

## 3. The four options

| Option | Assessment |
|---|---|
| **A — MERGE #73** | **Pointless.** #73 is a strict ancestor of #79. Merging it accomplishes nothing that merging #79 does not, and leaves the round-5 report stranded. |
| **B — MERGE #79** | **RECOMMENDED.** Delivers everything in #73 plus documentation only. Risk is identical to #73, which is already accepted. Clean, mergeable, CI green, `main` is an ancestor. |
| **C — SELECTIVE MERGE** | **Not justified, and actively harmful here.** Selective merge is for divergent history; this history is linear. Cherry-picking would fork the lineage and destroy the property that makes B safe. |
| **D — HOLD** | **The status quo, and it is the worst of the four.** See §5. |

**Order and risk if B is taken:** merge #79 into `main` as a single merge; **#73 then
closes automatically as subsumed** (or close it manually noting «subsumed by #79»). No
rebase, no conflict resolution, no test re-run needed beyond the green CI already on #79.
The nine round-5 lane PRs (#80–#88) **stay open and unmerged**, retargeted from #79 to
`main` or left as-is — they are unreviewed, and three of them touch code WS-A is
currently changing.

**One consequence that must be stated so it is not mistaken for delivery:** packs under
`assets/pack/` are gitignored build artefacts. **Merging #79 changes no APK.** A build on
this Mac still carries the old packs until they are rebuilt there. Merging clears
governance debt; it does not deliver anything to a child.

---

## 4. Why this matters beyond tidiness

Round 4 was **ACCEPTED by the Founder** and is still unmerged. Acceptance and merge have
decoupled. The practical cost is now visible and compounding:

- Round 6's base (`integration/round6-2026-09-06`) is a **synthetic composition branch**
  that exists only because nothing merges — 114 commits of lane work reachable from
  nowhere else.
- If round 6 also does not merge, round 7's base becomes **a composition of a
  composition**. Each round adds a layer whose only integration evidence is a throw-away
  worktree.
- No APK on this machine carries any correction from rounds 4, 5 or 6.

**Option D is not neutral.** It is the choice that makes every subsequent round's base
more synthetic than the last.

---

## 5. Recommendation, stated once

**Merge #79. Close #73 as subsumed. Hold #80–#88.**

If the Founder prefers to keep integration branches permanently unmerged, that is a
legitimate choice — but then it should be stated as policy, and integration branches
should stop being treated as a delivery path. The current state, where a round is
accepted but not merged and the next round quietly composes on top, is the one
combination that carries the cost of both options and the benefit of neither.

**Nothing was merged in producing this audit.**
