# PHASE F — THE SELECTION RULE, WRITTEN BEFORE THE EVALUATION

Founder order 47 §PHASE F · branch `phase-f/narrow-trusted-slice`, based on `main` @ `5d77cb1`.

> «Không cherry-pick bằng cách biết trước answer rồi điều chỉnh threshold. **Selection rule phải
> được ghi TRƯỚC final evaluation** nếu việc lựa chọn có thể bias kết quả.»

**This file is committed before the harness that decides the outcome exists.** Its commit hash is
quoted in `PHASE-F-NARROW-TRUSTED-SLICE.md`. A rule written afterwards is a rationalisation; the
only thing that makes this one worth anything is that the commit graph can prove the order.

**Nothing below lowers a bar.** Where a bar in this repository already exists, it is cited and
adopted as written. Where none exists, the rule states one and says it is new.

`trusted = 0` · `eligible for teaching = 0` · no threshold is activated by this phase.

---

## 0 · Full disclosure — what I knew when I wrote this

Population discovery ran before this rule. Hiding that would make the pre-registration weaker, not
stronger, so here is everything I had measured at the moment of writing. **No candidate unit's
fidelity, role or served status had been measured. No number below was chosen to make any unit
pass or fail.**

| # | Known fact | How |
|---|---|---|
| K1 | `tool/corpus/tc_gold/` holds **54 pages** with verbatim `text` per block. | file census |
| K2 | `tool/corpus/tc_gold_bai17/` holds **4 pages** (KHTN 6 Bài 17) and **0 of its 73 blocks carry `text`** — anchors only. | file census |
| K3 | **No lesson in this repository is fully covered by gold pages.** Best coverage 0.80 (Bài 17); TSLs at 1.00: **zero**. | joined `tc2-p1` TSL boundaries against both gold sets |
| K4 | `thresholds/evidence.py::_wrongness` sets `digits_wrong = None` when a gold block has no `text`, and `truth_teaching_critical = bool(None) or as_question`. **On a text-free gold plane the digit half of teaching-critical reads a silent zero.** | code |
| K5 | `05-sgk-lich-su-va-dia-li-5` p041 is a gold page **with** text and is the last page of Bài 8 — the lesson that already has an end-to-end delivery chain (Golden #1, `assets/fixtures/real/`). | gold `lesson` field + `poc-out/round6/golden/` |
| K6 | All ground truth in this repository is **model-produced**: gold pages are «VLM (Claude) reading a `tc_render` grid image»; the round-3 audit is «single AI annotator, page-render based». | `annotator` fields; `ROUND3-CONSOLIDATED-REPORT` §6 |
| K7 | `FALSE-TRUST-AUDIT-PROTOCOL.md` requires **a second annotator on ≥ 10 % of rows before any bar is called met.** It has never been run. | that file, line 82 |
| K8 | Phase B measured **2 `ACTIVITY → QUESTION` errors** on the Bài 17 plane and **7 teaching-critical rows** on the adjudicated 54-page plane. | `PHASE-B-QUESTION-VETO.md` §4.2, §3.2 |
| K9 | `THRESHOLDS.json` does not exist, so `trusted` computes to 0 by construction; creating it is a **Founder gate** this phase must not touch. | `THRESHOLDS.example.json`, order 47 §FOUNDER GATES |
| K10 | The Bài 17 TSL claims the lesson spans pdf pages **61–65**; the gold set says the lesson ends at **p064** and «pdf 65 opens Chương V / Bài 18». The two disagree. | TSL `boundary` vs gold `lesson.note` |

---

## 1 · There is no selection among candidates — the evaluation is exhaustive

The cheapest way to make cherry-picking impossible is to **not pick**. The harness does not choose
a slice. It enumerates **every** candidate unit on **every** gold page of **both** gold sets,
applies the identical bar to all of them, and reports **all** of them — passes and failures, with
the failing stage named. The output is *the set that survives*, not a unit I liked.

## 2 · What a candidate unit is — the shrink, defined structurally

> «Ưu tiên: 1 grade × 1 subject × 1 lesson/content type × smallest useful learner experience.»

Three scopes are enumerated, largest first, and each is evaluated independently:

| scope | definition |
|---|---|
| **LESSON** | every gold page of a lesson, where the gold pages cover the lesson's whole page span. K3 says there are none; the harness still enumerates the scope so its emptiness is **measured rather than assumed**. |
| **PAGE** | every learning block on one gold page. |
| **SECTION** | a gold `heading` block plus every subsequent gold block on that page in `order`, up to but excluding the next `heading`. Furniture roles (`page_number`, `running_head`, `folio`) are never members. |

A unit smaller than a SECTION is not enumerated, and the reason is doctrine this repository already
paid for: **round 5 defect 8** — «withholding one member of a structure leaves the served remainder
*wrong*, not merely smaller … never serve a mutilated structure.» A fragment of a section is a
mutilated structure by construction.

## 3 · The bar — seven stages. Every one must hold. Declared here, unchanged afterwards.

**S1 · SOURCE.** Every member matches a pipeline block (`matched`) carrying book, pdf page, printed
page and bbox provenance.

**S2 · STRUCTURE.** (a) members are contiguous in gold `order`; (b) no member is unmatched;
(c) no two members match the **same** pipeline block — the many-to-one matcher artefact Phase A
found on row #8; (d) no member refers to a figure or table that is not itself a verified member;
(e) no member is a gold block that carries no text in gold (a table with no cells cannot be
verified and must not be served).

**S3 · RECOGNITION.** Every member's served string is **character-exact** against gold after NFC:
`cer == 0.0` **and** `edits == 0`. A unit any of whose members has no gold text is reported
**`UNMEASURABLE`** and can never be reported PASS. *(This is the stage K2 + K4 make impossible on
the Bài 17 plane; the harness must say so out loud rather than print a zero.)*

**S4 · ROLE.** For every member, coarse role equals `tc_sdm.GOLD_ROLE_MAP[gold_role]`, and
`truth_as_question` is False.

**S5 · VALIDATION.** Every member is `pipeline_trusted` under the **unchanged** pipeline gate,
carries no guard reason, has `truth_wrong == []` and `truth_teaching_critical == False`. **A unit
with one withheld member FAILS** — again defect 8: a hole in a structure is not a smaller structure.

**S6 · TRUST.** Two conditions, separated because only one of them is measurable by an agent:

* **(a) measurable** — the unit is admitted by the frozen round-7 candidate policy
  (`thresholds/frozen/TRUST-POLICY-CANDIDATES-v1.json`, candidate **C2 · PROSE**, the recommended
  one) evaluated through `policy.admits()`. This activates nothing: `admits` returns a refusal
  list and has no code path that writes.
* **(b) NOT measurable by this phase** — (i) a production trust threshold is a Founder gate
  (K9); (ii) `FALSE-TRUST-AUDIT-PROTOCOL.md` requires a second annotator on ≥ 10 % of rows before
  **any** bar may be called met, and the only annotator this repository has ever had is a model
  (K6, K7).

A unit satisfying S1–S5 and S6(a) is reported **`QUALIFIES · GATE CLOSED`**. It is never reported
PASSED, TRUSTED, or CERTIFIED. **The words «trusted» and «certified» are not available to this
phase for any unit, at any measurement, by construction.**

**S7 · ARTIFACT.** The unit can be emitted as a `LessonDocument` the app renders through the
existing bridge (`tsl_to_lesson_document.py` → `assets/fixtures/real/` → `WorkspaceCatalog`), and
nothing D4 enters git. Because a qualifying unit's text is verbatim SGK, its artifact lands in the
gitignored `real/` tree, so S7's honest verdict for such a unit is **`LOCAL ONLY`**: it exists on a
machine that has the corpus and nowhere else. Any claim that a child can use it is false while the
licence gate (WAL-43) is closed.

## 4 · Adequacy guards — absence cannot satisfy a positive obligation

The harness exits non-zero with `UNVERIFIED` unless all hold:

| id | guard |
|---|---|
| **G1** | it enumerated **> 0** candidate units. A gate over an empty population prints a flawless zero. |
| **G2** | the population **contains the failing cases and the bar fails them**: the 2 `ACTIVITY → QUESTION` rows of the Bài 17 plane and ≥ 1 Phase A teaching-critical row on the 54-page plane must each land inside an enumerated unit, and every one of those units must be classified FAIL. A bar that passes everything is not a bar. |
| **G3** | a unit with **no block a child acts on** (no member whose gold role is `question` or `activity`) is `NOT-A-LEARNING-SLICE` and can never be PASS or QUALIFY — including a unit of size 1. |
| **G4** | every headline count in the report is re-derived by a **second, different aggregation** and the two must agree. |
| **G5** | verbatim strings go only to `--detail`, which must resolve **outside** the repository (containment tested on resolved paths, not `startswith` — Phase B found that bug). |

## 5 · Tie-break, declared now

If more than one unit reaches `QUALIFIES · GATE CLOSED`, the one described first is: the unit whose
lesson already has a delivery chain in `WorkspaceCatalog.defaultSlots`; else the smallest by member
count; else the lexicographically first `book/page/unit`. **The tie-break never changes a verdict.**

## 6 · Pre-registered prediction

Recorded before the measurement, because a prediction made afterwards is a description.

1. **At least one unit reaches S5** — the pipeline can serve a small, correct, complete section.
2. **Zero units reach a state in which a child can use them**, because S6(b) and S7 are both closed
   by acts this phase is forbidden to perform.
3. Therefore the order's question — **WHAT CAN A CHILD USE NOW THAT THEY COULD NOT BEFORE?** — will
   be answered **NOTHING**.
4. **The Bài 17 plane will produce no PASS at any scope**, because K2 makes S3 unmeasurable there.

If (1) is false the blocker is upstream of trust, and `NARROW-SLICE-BLOCKER-REPORT.md` names it.
If (2) or (3) turns out false, that is news and it will be reported as news.

## 7 · What this rule may not be used for

- It may not be relaxed after seeing a result. If a stage's definition turns out to be wrong, the
  fix is a **new commit that says it changed and why**, and the old number stays in the report.
- No unit may be excluded from the report because it fails.
- No threshold value appears anywhere in this rule, because there is no threshold to set: S6(b) is
  a gate, not a number.
