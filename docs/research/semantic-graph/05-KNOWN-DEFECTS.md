# Lane E1 · known defects — found, fixed, and still open

Recorded rather than tuned away. Every fixed one has a regression test that fails without the fix.

---

## 1. Fixed, with a regression test

| # | Defect | How it showed | Fix |
|---|---|---|---|
| 1 | **`[A-ZÀ-Ỹ]` is not "an uppercase Vietnamese letter"** | As a *range* it spans U+00C0–U+1EF8, which contains every **lowercase** accented letter (á, ă, ủ…). Event titles came out as **`ăm`** (from «năm») and **`ủa Ngô Quyền`** (from «của») — mid-word fragments that read like real names in a timeline. | the class is built from Unicode case, not from a range. LS&ĐL 5 Bài 8 went 8 events with 2 fragments → **exactly 7**, matching Lane C's hand-checked 7/7. |
| 2 | **Causal connectives were case-sensitive** | every sentence-initial «Vì … nên …» matched nothing, silently | `re.I` |
| 3 | **A bare year was not a date** | `(?P<when>…{2,40}?\d{2,4}…)` needed ≥2 characters before the digits, so «(248)» was dropped | whole-parenthesis date-shape test, which also correctly refuses «(trang 41)» |
| 4 | **An enumeration was treated as a procedure** | KHTN 6 Bài 17 compiled **7 "procedures"**, of which the first two were the lesson's OBJECTIVES («· Trình bày được…» under MỤC TIÊU) and a pair of numbered QUESTIONS | order and procedurality separated: the enumerator asserts ORDER (`next` survives for lists), a **governing block** asserts PROCEDURE, and only the latter yields `Step` |
| 5 | **The governor is not the heading** | reading only headings found **zero** procedures in a lesson that plainly prints two — Bài 17's procedure is introduced by an `instruction` block while the heading reads «Lọc nước từ hỗn hợp nước lẫn đất» | governors include `instruction` blocks and any line carrying a procedural marker |
| 6 | **One tone slip deleted a whole visual family** | that governing block reads **«Tiền hành»** — OCR's «Tiến hành», one of the four slips round 4 records as surviving *because both stacks agree*. Matching the accented form only: 0 Steps, no PROCESS. | the governor test compares **tone-stripped**. 0 → 5 Steps. See `07-EXCEPTIONS-AND-STRUCTURE-GAPS.md` §3.2 — this is a **workaround, not a repair**. |
| 7 | **A cause clause started mid-word** | `.{6,90}?` starts wherever the engine finds it cheapest: the extracted cause was «h 17.1, hạt phù sa …» out of «Hình 17.1, hạt phù sa …». A cause that starts mid-word is not a quotation of the book, whatever its span says. | clause-boundary anchor |
| 8 | **Two builds of one lesson overwrote each other's output** | the build id was taken from the first path segment starting `tc2-`, and a lane work directory is called `tc2-lsdl5` — so `tc2-p1` and `tc2-r5` results silently merged, hiding the very disagreement they were kept to measure | read the build id from under `tc-v2/` |

---

## 2. Open — measured, not fixed

| # | Defect | Size | Why it is open |
|---|---|---|---|
| A | **Precision is unmeasured on a holdout.** The rules were written while looking at KHTN 6 Bài 17 and LS&ĐL 5 Bài 8. | unknown | This is the most important open item. A rule that only fits the two lessons it was written against is not a grammar. §19's `holdoutPrecision` row is deliberately blank rather than guessed. |
| B | **`e1-definition-v1` over-fires.** `^X là Y` matches any sentence whose subject is capitalised — 154 of 224 lessons (68.8 %) "have a definition", which is implausibly high. | ~154 lessons affected | Needs a real definitional test (a term that recurs, a glossary cross-check), not a syntactic one. Reported so the DEFINITION count in `06-CENSUS.md` §3.2 is read with suspicion. |
| C | **`_is_procedural` falls back to `role in {instruction, activity}`.** | unknown | The role layer is measured unreliable (κ 0.42–0.71; Lane A2 reports 4 validated math restores blocked by `empty_block` alone). Every other E1 rule deliberately reads heading nesting, enumerators and connectives — signals that survive role error. This one does not, and inherits the role layer's defects. |
| D | **The generic dated-event rule gets 7/7 on the lesson Lane C hand-checked, and 3 events on a second build of the same lesson.** | — | The difference is entirely the source build, not the rule (§3.1). But it means the 7/7 is a result about one build, not a precision measurement. |
| E | **`gap` elements are never emitted.** | 236 of 238 TSL lessons carry withheld regions | v0 compilers read only trusted blocks, so a structure with a withheld member is silently *smaller* rather than visibly *incomplete*. That is round-5 defect 8 reproduced inside this lane. The contract is written (`03-VISUALSPEC-CONTRACT.md` §3.3); the implementation is not. |
| F | **`isA` is never distinguished from `hasPart`.** | 0 `isA` edges built | «gồm» covers both class membership and part/whole in Vietnamese, and no rule separates them. Recorded in `06-CENSUS.md` §6 as *unproven*, not refuted — it may be that 5 relations suffice, not 6. |
| G | **COMPARISON, QUANTITY, SPATIAL, CONCEPT_MAP have no extractor.** | 4 of 10 families | Their EXTRACTABLE = 0 is a fact about this lane, not about the corpus. The census emits `familiesWithNoExtractor` beside the table so the zero cannot be misread. |
| H | **Sinh học (90 canonical lessons) has zero units and no TSL.** | 90 lessons | Invisible to the census. Not an E1 defect, but it means "Science is covered" is false as stated. |

---

## 3. Things deliberately NOT done

- **No rule was tuned to make a number look better.** Defects 1–7 were all found by a test or by
  reading the output, and each fix changed the measurement in whichever direction was true —
  defect 4's fix *reduced* PROCESS from 7 to 2 on Bài 17.
- **No LLM was called anywhere in this lane**, for census, classification or generation.
- **No production threshold** was proposed or implied. LEARNER_READY is 0 and stays 0 until a
  Founder gate exists.
- **`lib/**` was not touched.** Every finding about the app is an observation with a `file:line`,
  not an edit.
