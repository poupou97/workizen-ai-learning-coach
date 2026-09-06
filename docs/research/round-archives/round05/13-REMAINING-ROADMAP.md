# 13 · REMAINING ROADMAP

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**
>
> **THIS IS A FORECAST, NOT A PROMISE.** Only round 6 is committed. Rounds 7–8 are **PROPOSED**
> and each item names the round-5 evidence that argues for it. Rounds 9–10 are **TBD** — areas,
> not plans. Nothing below creates an obligation, and no date is attached to anything beyond
> round 6.

---

## ROUND 6 — **COMMITTED**

*(Committed in the repository: `docs/research/ROUND6-PLAN.md`, commit `1a75d24`, 2026-09-06.
Full text in `reports/`; summary in `12-NEXT-ROUND-PLAN.md`.)*

**North Star: MAKE VERIFIED ACCURACY REACH THE LEARNER.**

| WS | Scope | Gate |
|---|---|---|
| **A · TRUTH ACCOUNTING** | R13 conservation + canonical lesson identity | **GATE A** — zero unexplained silent loss on Golden + holdout |
| **B · RECOGNITION** | failure census, then bounded recognition candidates on the 274/336 fractions | **GATE B** — ≥1 previously unrecoverable OCR failure class materially improves at recognition level |
| **C · REPAIR → PRODUCT** | `ValidatedRepair` crosses the production-shaped pipeline. **CONNECT ≠ TRUST** | **GATE C** |
| **D · GOLDEN DELIVERY** | 3–5 real lessons end to end on a real device; Workspace **option B** | **GATE D** (≥1 lesson honestly eligible for teaching, a truthful zero acceptable) + **GATE E** (device consumes validated data, fully traceable) |

---

## ROUND 7 — **PROPOSED** (not committed; each item names its evidence)

| Candidate | Why the round-5 evidence argues for it | Evidence anchor |
|---|---|---|
| **A trust threshold decision, with the curve in hand** | A3 built the instrument and produced the trade-off curve, deliberately choosing no point. `trusted` computes to **0 by construction** until a point is chosen. This has been the **single biggest blocker since round 4** and is a Founder act, not a lane's. | A3 / PR #80; Source Trust 0/97 flat for two rounds |
| **A semantic-yield gate** | 4 of 28 LS&ĐL lessons **lost** a visual family and none gained, while the newer pipeline had *more* trusted blocks. **Accuracy work can silently destroy semantic yield and nothing gates for it.** | E1 *(MEASURED)* |
| **Close defect 8 on the lesson path** | A1 measures 7 → 0 on the gold set; Lane D measures **9 → 9** and **13 → 13** where a child reads. The class is closed where one lane looks and open where the other does. | D + A1, both PARTIAL |
| **Resolve R15 and re-derive the pack build on a reproducible attach** | 950 of 6,176 page verdicts differ, 896 unexplained; the pack build depends on attach provenance. **Not assigned to any round-6 workstream.** | D / PR #82 |
| **Answer Q-ROLE-1/2/3, then recompute role rates under SPEC v1** | Applying the spec **raises** the measured role rate; any before/after comparison must be recomputed under it, not compared across it. Role is the one class that moved the wrong way this round (0.116 → 0.151). | A3 §9 |
| **The subjects with no TSL at all** | **Ngữ văn / Tiếng Việt — the subjects where verse matters — have never been measured**, because no TSL exists for them. | E1 census |
| **NO_SOURCE_AT_ALL: 1,384 lessons (42.7 %)** | E1's own verdict: *"No grammar change moves this. It is a source-pipeline problem wearing a semantics costume."* This is the largest single exception cluster in the corpus. | E1 census |

## ROUND 8 — **PROPOSED** (not committed)

| Candidate | Why | Evidence anchor |
|---|---|---|
| **MATH_AST as a first-class corpus extension** | NEEDS_MATH_AST covers **1,096 lessons (33.8 %)** — *one extension worth 9× everything else* — and is blocked on two verified bridge defects. | E1 census |
| **A bridge carrier for validated structured nodes, plus a per-block failure mode** | `ROLE_MAP` has no `formula` *(PROVEN)*; the app union has no formula member and **fails closed on the whole document**. A validated `MathExpression` cannot reach the app today. | E1's requested change list; `09-…` §2 |
| **Rich-text / math rendering in the app** | **0 of 161** Dart files contain `RichText`, `TextSpan` or `Text.rich`; no math, markdown, LaTeX, SVG or WebView dependency. **A superscript or a fraction cannot render correctly even when the data is right.** | *(PROVEN — `evidence/structural-spot-checks.md`)* |
| **`khtn6_bai17.dart`'s 122 hardcoded `const` lines become data** | E1: versioned data + compiled artefacts + a ~10-row rule registry + a small curated overlay. Until then the golden lesson is partly hand-written. | E1 |
| **The next renderer families: HIERARCHY and LABELED_FIGURE** | E1's census makes these the **justified** next two — chosen by measured corpus frequency rather than by appetite. | E1 |
| **Scale beyond the golden lessons — only after GATE D holds** | Round 6 proves 3–5 lessons end to end. Scaling before that would repeat round 3's finding that *the currently shipped Scale content is not trustworthy for teaching*. | round-3 audit; round-5 §8.1 |

## ROUNDS 9–10 — **TBD** (areas only; no plan exists)

- **Parent surfaces.** Untouched by round 5; `Evidence Reality` is 0 of 0, so there is nothing
  honest to show a parent yet. **UNAVAILABLE:** no parent measurement exists from this round.
- **Teacher / classroom.** Standing backlog only.
- **Assessment mode** (policy distinct from tutor mode).
- **Voice / English adapter.**
- **Licensing.** Nothing in this archive may be published; a distribution decision is a
  precondition for anything public-facing.
- **Public release.** Founder gate. No round has produced content that is `eligible for teaching`.

---

## THE STANDING BACKLOG THAT PREDATES THE ROUNDS

`docs/pm/ROADMAP-POST-K12.md` (Founder master order, 2026-09-02; a mirror of Jira WAL) is the
execution roadmap that the rounds were superimposed on. It is **not superseded**, and its still-open
items are listed here so they are not lost:

| Item | State per the roadmap mirror |
|---|---|
| **WAL-30** | open — awaiting Founder |
| **WAL-84** — knowledge-pack scale | open at the 500 MB+ / battery tier. Measured to **2.7 GB / 3.82 M units on the Nokia at FTS p95 92 ms — no breakpoint to the end of the target scale**; proposed threshold 4–5 GB; FULL-vs-MODULAR became a product question |
| **WAL-33** | open — recall awaits real photographs |
| **WAL-50** — age-adaptive UX | tokens / dark / motion / density done; **consumer wiring open** |
| **WAL-121–124, 137–140, 143–146, ALA 155–158, MA 159–162** | **deferred** |
| **WAL-125** — ads for children | research complete, **STOP, submitted to the Founder** |
| Branch protection on `main` | **not enabled** — a Founder decision, recorded there |
| **Known debt** | the map badge is still bound to the hard Toán-B6 slice and must be generalised when the curriculum opens more subjects; one map fix was **never re-walked on the device** (the Nokia was unplugged when the build finished) |

*(Reproduced as a status mirror. The archive builder did not re-verify these Jira states; see
`14-JIRA-CONFLUENCE-STATUS.md` for what the trackers actually show today.)*

---

## WHAT WOULD CHANGE THIS FORECAST

| If this turns out to be true | The roadmap changes like this |
|---|---|
| **R13's silent loss is much larger than 27/394 and 55/375 at corpus scale** | Round 7 becomes accounting, not delivery. Every published rate in every round gets restated. |
| **Recognition on the crop does not materially beat the current OCR** | The 274 unreadable fractions become a **ceiling, not a bottleneck**, and the strategy shifts from repair to **coverage honesty** — serving less, saying so, and building the product around what can be read. |
| **`3,679` turns out to be a row count, not a lesson count** | Every coverage figure in every round is restated against 3,240. Round-6 WS A2 exists to answer this. |
| **The Founder declines to wire the repair path** | Rounds 7+ stop optimising repair precision — a laboratory that will never connect does not need a better validator — and the effort moves to recognition and to withholding honestly. |
| **A trust threshold is set** | `trusted` and `eligible for teaching` become non-zero for the first time, and the five product scores start measuring something they have never measured. |
