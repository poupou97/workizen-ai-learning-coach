# 13 · REMAINING ROADMAP

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**
>
> **THIS IS A FORECAST, NOT A PROMISE.** Round 6 is **DONE**. Rounds 7–8 are **PROPOSED**. Rounds
> 9–10 are **TBD** — themes, not plans. No date is attached to anything.

---

## THE ROUND TABLE — as the coordinator proposed it

| Round | Status | Theme | North Star | Exit condition |
|---|---|---|---|---|
| **6** | **DONE** | Delivery + Recognition | Verified accuracy reaches the learner | **4 PASS · 1 truthful zero** |
| **7** | **PROPOSED** | Trust threshold | Trusted content reaches the learner | `eligible > 0` **with measured false trust** |
| **8** | **PROPOSED** | Scale the validated pipeline | Beyond Golden slices | **Generalisation proven on a holdout** |
| 9 | **TBD** | Semantic / visual generalisation | One grammar, many lessons | **Census-justified** renderer families |
| 10 | **TBD** | Pedagogy / evidence breadth | Learning that is measured | Based on **the measured bottleneck** |

**Two properties of that table are worth naming.** Every exit condition is a **measurement**, not a
deliverable — and rounds 9 and 10 name *what would justify them* rather than what they will contain.
**A roadmap whose later rounds are honest about being undecided is the only kind that survives a
round like this one.**

---

## ROUND 7 — **PROPOSED** · the threshold round

Detail in `12-NEXT-ROUND-PLAN.md`. **Dependency: a Founder decision. Nothing else.**

The evidence obliging it, in one line each:

- **`eligible for teaching` = 0, `SOURCE TRUST` = 0/97, `PEDAGOGY REALITY` 7/17** — all four blocked
  on the same gate.
- **Six validated repairs sit withheld on the flagship lesson**, including the block carrying all
  seven dated events *(PROVEN)*.
- **A3 built the trade-off curve in round 5 and deliberately chose no point on it** — the instrument
  is waiting.

## ROUND 8 — **PROPOSED** · scale the validated pipeline

| Candidate | The round-6 evidence that argues for it |
|---|---|
| **Prove R13 conservation over the whole corpus** | Measured on **29 ledgers / 1,878 regions**; explicitly **HYPOTHESIS** beyond that. *Every published rate depends on conservation holding everywhere.* |
| **Prove recognition beyond the measured slices** | Holdout digit recall **0.181** vs DEV **0.500**. And **two holdouts returned ~0 because the population was wrong** — a scale round must fix the population, not the recogniser. |
| **A token splitter for the SEGMENTATION class** | **196 of 548 (36 %)** of unreadable regions had the ink recognised and glued elsewhere. *Cheap, deterministic, no recogniser at all* — and round 5's framing hid it entirely. |
| **Wire `ink-accounted-v1` into the consensus rule** | Round 5 **already built** the check that catches a dropped printed minus; this lane does not run it. **Wiring an existing validator is the cheapest fix available and it is not done.** |
| **An in-corpus template recogniser for `Ω`** | **0 of 22 at every scale.** The corpus prints thousands of correct Ω glyphs **in the same books.** |
| **The 63 TOC-less books** | They contribute **zero rows**. *«3,679 was never all SGK lessons.»* Same failure family as R13: a whole book leaving the denominator with no record. |
| **`NO_SOURCE_AT_ALL` — 1,384 lessons (42.7 %)**, carried from round 5 | E1's verdict stands: *«no grammar change moves this — it is a source-pipeline problem wearing a semantics costume.»* |

## ROUNDS 9–10 — **TBD** (themes only)

- **Semantic / visual generalisation.** Gate: **census-justified renderer families.** Round 6's
  census says the honest next candidate is **LABELED_FIGURE** (`figure_dependent` **632 blocks,
  0.291** of withheld, against 3,864 figures) — *and that this is step 2 of FORMS BEFORE RULES, not
  a licence to build.*
- **Pedagogy / evidence breadth.** `PEDAGOGY REALITY` has been **7/17 for three rounds** and
  `EVIDENCE REALITY` **0 of 0**. **SAM has a script on exactly 1 of 238 lessons.**
- **Parent surfaces.** Untouched in rounds 5 and 6. **UNAVAILABLE:** no parent measurement exists.
- **Licensing.** **NOT STARTED.** SGK verbatim remains INTERNAL/RESEARCH ONLY, and a distribution
  decision is a precondition for anything public-facing.
- **Performance / release quality.** **NOT STARTED.**

---

## MAJOR PRODUCT GATES — the honest status board

*(From §15 of the consolidated report. This is the table to read if you read only one.)*

| Gate | Status |
|---|---|
| SOURCE ACCURACY | **PARTIAL** |
| RECOGNITION | **POC** |
| TRUSTED CORPUS | **RESEARCH** — blocked on the threshold |
| STRUCTURED LEARNING CONTENT | **PARTIAL** — carried, **not servable** |
| SEMANTIC GENERALIZATION | **RESEARCH** |
| VISUAL LEARNING | **POC** — **2 of 4 families have zero real data** |
| PEDAGOGY | **RESEARCH** |
| EVIDENCE | **RESEARCH** |
| **DEVICE UX** | **PRODUCT-INTEGRATED** — the only one |
| PRIVACY | **PARTIAL** |
| LICENSING | **NOT STARTED** — SGK verbatim remains INTERNAL/RESEARCH ONLY |
| PERFORMANCE · RELEASE QUALITY | **NOT STARTED** |

**One gate is product-integrated. Everything else is POC, RESEARCH, PARTIAL or NOT STARTED.** After
six rounds, *that* is the shape of the project, and it is worth looking at directly.

---

## THE STANDING BACKLOG THAT PREDATES THE ROUNDS

`docs/pm/ROADMAP-POST-K12.md` (Founder master order, 2026-09-02; a mirror of Jira WAL) is **not
superseded**. Its still-open items, unchanged since the round-5 archive:

| Item | State |
|---|---|
| **WAL-30** | open — awaiting Founder |
| **WAL-84** — knowledge-pack scale | open at the 500 MB+ / battery tier. Measured to **2.7 GB / 3.82 M units on the Nokia at FTS p95 92 ms — no breakpoint to the end of the target scale**; proposed threshold 4–5 GB |
| **WAL-33** | open — recall awaits real photographs |
| **WAL-50** — age-adaptive UX | tokens/dark/motion/density done; **consumer wiring open** |
| WAL-121–124, 137–140, 143–146, ALA 155–158, MA 159–162 | **deferred** |
| **WAL-125** — ads for children | research complete, **STOP, submitted to the Founder** |
| Branch protection on `main` | **not enabled** — a Founder decision |
| **Known debt** | the map badge is still bound to the hard Toán-B6 slice; one map fix was **never re-walked on the device** |

*(A status mirror. The archive builder did not re-verify these Jira states — see
`14-JIRA-CONFLUENCE-STATUS.md` for what the trackers actually show today.)*

---

## WHAT WOULD CHANGE THIS FORECAST

| If this turns out to be true | The roadmap changes like this |
|---|---|
| **The Founder sets a threshold and the blind audit shows unacceptable false trust** | Round 7 reports a **second truthful zero**, and the project's centre of gravity moves back to recognition and accuracy — *with the crucial difference that it would then be a measured refusal rather than an absent decision.* |
| **The Founder declines to set a threshold** | `eligible for teaching` stays 0 **permanently**, and the honest product becomes *a reader of real book text with honest gaps* rather than a tutor. That is a legitimate product — but it should be **chosen**, not arrived at. |
| **R13 conservation does not hold at corpus scale** | Round 7 becomes accounting again, and every published rate is restated a second time. |
| **Recognition does not generalise past 0.181** | The recognition lever is **a slice tool, not a corpus tool** — and coverage honesty (serving less, saying so) becomes the strategy rather than repair. |
| **The canonical count settles far from 3,650** | Every coverage figure in every round is restated against the new denominator. |
| **The merge debt is not cleared** | Round 8's base is a composition of a composition of a composition, **and no APK on this machine will carry any correction from rounds 4–8.** |
