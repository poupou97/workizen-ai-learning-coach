# FOUNDER DECISION PACK
## Four decisions no agent may take · prepared 2026-09-06 under order 47

Short by design. Each: **QUESTION · CURRENT EVIDENCE · OPTIONS · RECOMMENDATION · CONSEQUENCE IF
DEFERRED.** None of these blocked the autonomous run — everything runnable without them was run.

---

## D1 · Which grouping key is the canonical lesson denominator?

**EVIDENCE.** Re-derived twice, independently — by WS-M from `tool/metrics`, and by me from
`assets/pack/lesson-index-g*.json` — identical to the digit. **The four "competing" numbers are one
leaf population under four grouping keys**, not four artefacts disagreeing:

| grouping key | count |
|---|---|
| leaf rows | **3,679** |
| distinct `(doc, no)` | **3,240** |
| distinct `(doc, no, pageStart, title)` | **3,650** |
| rows carrying `pageStart` | **3,381** |

`3,240` **deletes 410 real lessons** to key collision («Bài 1» printed seven times in one GDTC book,
once per chủ đề). `3,679` over-counts by 29 true duplicates. **63 of 301 SGK books contribute zero
rows**, so `3,679` was never «all SGK lessons».

**OPTIONS.** (a) `3,650` canonical, `3,381` ranged, `3,679` historical baseline · (b) keep `3,679`
and carry the +29 as known error · (c) defer, and require every metric to name its key.

**RECOMMENDATION: (a).** It is the only one that counts lessons rather than rows or collisions.

**IF DEFERRED.** No harm today — every metric already states its key, and `3,679` stays HISTORICAL
BASELINE ONLY. The cost is that coverage figures across rounds remain non-comparable.

---

## D2 · Ratify D-135 … D-138? (WAL-196)

**EVIDENCE.** Still **PROPOSED**. Knowledge-base PR #1 unmerged; **10 items in
`DECISIONS-REQUESTED.md` unanswered**. This is **the gate holding `trusted = 0` structurally** —
not an engineering limit. Round 6 built the whole chain up to it; round 7 froze a calibration
against it; this run reached VALIDATION and stopped at a clause.

**OPTIONS.** (a) ratify as proposed · (b) ratify with amendments · (c) reject and re-propose ·
(d) defer.

**RECOMMENDATION: read the four and choose (a) or (b).** I have deliberately not recommended a
substance — these are architecture decisions of yours, and an agent ratifying its own architecture
proposals is the failure mode the governance exists to prevent.

**IF DEFERRED.** `trusted = 0` and `eligible for teaching = 0` remain **structurally** unreachable.
Every future round inherits the same ceiling, and no amount of recognition or role work moves it.
**This is the single most blocking item in the project.**

---

## D3 · Activate a trust threshold, and under which bound?

**EVIDENCE.** Round 7 froze a policy and two blind populations, hashed, with **no `approval` and no
`admitted` entry** — the ordering is enforced, not asserted (an `admitted` write without approval
raises `PermissionError`). The recommendation was **C2 · PROSE under BOUND-2**, with its own
predicted outcome — a truthful zero — **sealed inside the frozen payload** so it could not be
revised after the fact.

The finding that decides it: **all teaching-critical errors reduce to two mechanisms, and neither is
visible to any signal a gate can read.** 3 of 6 digit corruptions survive **character-exact agreement
between two independent OCR stacks**. No combination bounds teaching-critical below **≈0.021**
against BOUND-2's required **0.0035** — a factor of six.

Phase F adds: the two best units in the corpus are **refused by a clause, not a number**, at every
threshold from 0.70 to 0.99.

**OPTIONS.** (a) do not activate — keep the truthful zero · (b) BOUND-4 · (c) BOUND-5, per-lesson
certification of a bounded slice.

**RECOMMENDATION: (a), and if a non-zero is required, (c) — never (b).** **BOUND-4's consequence is
45 % of lessons carrying a teaching-critical error, which is not sayable to a parent.** And (c) is
not a threshold and must never be reported as one.

**IF DEFERRED.** No product harm — this is the *safe* default and the project has held it honestly
for three rounds. The cost is only that the ceiling stays where it is.

---

## D4 · WAL-43 — SGK licensing

**EVIDENCE.** Verbatim SGK pages, text and crops are **INTERNAL / RESEARCH ONLY** under D4 and have
been held that way without exception — verified again this run: `assets/fixtures/real/` on `main`
holds two `.gitkeep` files and nothing else, asserted by a test using `git ls-files` rather than
trusting `.gitignore`. Golden #1 carries 22 SGK page crops that make the lesson honest and **cannot
be distributed**.

**OPTIONS.** (a) pursue a licence · (b) build a crop-free presentation path · (c) defer and keep
research-only.

**RECOMMENDATION: (c) for now, and start (a) before any release conversation.** **TECHNICALLY
POSSIBLE ≠ DISTRIBUTION RIGHT**, and nothing in the pipeline is close enough to release for this to
be urgent.

**IF DEFERRED.** No engineering blocked. It becomes blocking the moment anything ships.

---

## One thing that is not a decision, but you should see it

**Every piece of ground truth in this repository is model-produced.**
`FALSE-TRUST-AUDIT-PROTOCOL`'s second-annotator requirement has **never been run**. So «certified»
is unavailable to any content at any bar, and every number in every round report — including the
ones that look most rigorous — inherits that limit. **Fixing it needs a human reading pages, not an
agent.** It is the cheapest thing on this list that no amount of autonomy can do.
