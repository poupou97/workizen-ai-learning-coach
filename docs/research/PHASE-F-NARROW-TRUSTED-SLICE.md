# PHASE F — THE NARROW TRUSTED SLICE: WHAT REACHED WHICH STAGE

Founder order 47 §PHASE F · branch `phase-f/narrow-trusted-slice`, based on `main` @ `5d77cb1` ·
**No threshold was activated. Nothing was served. No device was touched. `trusted = 0` and
`eligible for teaching = 0` are unchanged.** No SGK page, crop, reading or served string appears in
this document or in anything this work committed.

> **Selection rule: `docs/research/PHASE-F-SELECTION-RULE.md`, commit `aadaa137129f53c0`,
> committed 2026-09-06 before the harness that decides the outcome existed.**
> Verify the order: `git log --oneline --reverse phase-f/narrow-trusted-slice` — the rule is the
> first commit on the branch, the gate is the second.

---

## 0 · The one-paragraph answer

**The smallest real learning slice this repository can build reaches VALIDATION and stops there,
and what stops it is a clause, not a number.** Of 236 candidate units enumerated over both gold
sets, 95 are learning slices — a unit a child acts on — and exactly **two** clear SOURCE,
STRUCTURE, RECOGNITION, ROLE and VALIDATION: a section heading plus one question, character-exact
against gold, correctly roled, served by the unchanged pipeline gate with no guard raised, on
`06-sgk-ngu-van-6-tap-mot` printed page 20 and `09-sgk-ngu-van-9-tap-mot` printed page 66. **Both
are then refused by every frozen trust candidate**, and the refusal is structural: C1, C2 and C4
refuse the question role outright (`role_not_interactive` / `role_not_teaching_shaped`), and C3 —
the question surface — refuses the heading for not being a question and refuses the question itself
because the role layer's lexicon method returns 0.78 and 0.85 where C3 requires 0.90. **No
threshold setting rescues either unit; a pinned test proves that raising role confidence to 0.99
does not change the verdict.** And both units sit in books the delivery pipeline has never
processed: **there is no TSL, no lesson boundary and no `LessonDocument` for Ngữ văn 6 or Ngữ văn 9
anywhere in `poc-out`** — the slice that measures best has no path to a child, and the two books
that do have a path (KHTN 6 Bài 17, LS&ĐL 5 Bài 8) fail earlier. **WHAT CAN A CHILD USE NOW THAT
THEY COULD NOT BEFORE? NOTHING.** The RESEARCH STOP CONDITION therefore applies and
`NARROW-SLICE-BLOCKER-REPORT.md` is the deliverable beside this one.

---

## 1 · What was attempted, and why it could not be cherry-picked

The order forbids knowing the answer and then adjusting the threshold. The construction that makes
that impossible is not a promise, it is a design: **the harness does not choose a slice.** It
enumerates every candidate unit on every gold page of both gold sets, applies one bar to all of
them, and reports all of them — passes and failures alike, with the failing stage named.

| | |
|---|---|
| pages rebuilt | **58** — 54 (`tc_gold`) + 4 (`tc_gold_bai17`) |
| gold learning rows | **696** |
| candidate units | **236** — 221 on the 54-page plane, 15 on the Bài 17 plane |
| scopes enumerated | LESSON · PAGE · SECTION (§2 of the rule) |
| units that are learning slices (G3) | **95** — the other 141 hold no block a child acts on |

**The bar is the rule's, unchanged.** Seven stages, `S1 SOURCE → S7 ARTIFACT`, and two words the
harness cannot print at any measurement: **TRUSTED** and **CERTIFIED**. The strongest verdict
available to it is `QUALIFIES_GATE_CLOSED`, and §S6(b) of the rule says why that is the ceiling.

### The scope that turned out to be empty, measured rather than assumed

The rule required the LESSON scope to be enumerated even though discovery predicted it was empty,
**because an emptiness that is assumed is indistinguishable from one that was never looked for.**

| | |
|---|---|
| lessons touched by a gold page | **46** |
| **fully covered by gold pages** | **0** |
| partially covered | 18 |
| no authoritative page span declared anywhere in `poc-out` | 27 |
| **page span CONTESTED — the corpus states it two incompatible ways** | **1** |

The contested one is **`05-sgk-lich-su-va-dia-li-5` Bài 8 — the Golden #1 lesson.** Ten TSLs (the
lane-C runs, and the chain that reaches `assets/fixtures/real/`) declare pdf pages **38, 39, 40,
41**; four TSLs from the legacy reprocessing runs (`tc2-p2`, `tc2-p3`) declare **41 alone**. Under
the legacy boundary the flagship lesson is one page long. Reading the generous span first made the
lesson report as *fully covered* off a single gold page — a false positive this report caught in
its own harness and fixed by ruling that **a contested boundary is not a boundary**. Lessons fully
covered: **0 on the strictest reading and 0 on the most generous one.**

---

## 2 · What reached which stage

The honest view is the survival curve over the 95 learning slices: how many still hold every
property up to and including each stage. It is monotone by construction.

| stage | what it demands | slices still standing |
|---|---|---|
| — | is a learning slice at all (G3) | **95** |
| **S1 · SOURCE** | every member matched a pipeline block with provenance | **39** |
| **S2 · STRUCTURE** | complete, contiguous, one-to-one, no dangling figure/table | **19** |
| **S3 · RECOGNITION** | every member character-exact against gold (`cer = 0`, `edits = 0`) | **5** |
| **S4 · ROLE** | coarse role correct, nothing served as a question that is not one | **4** |
| **S5 · VALIDATION** | served by the unchanged gate, no guard, no wrongness, no hole | **2** |
| **S6a · TRUST POLICY** | admitted by the frozen candidate C2 · PROSE | **0** |
| **S6b · TRUST GATE** | — | **not reachable by an agent.** Founder gate, and the second annotator has never been run |
| **S7 · ARTIFACT** | a `LessonDocument` the app renders | **no path exists for either surviving unit** |

### Where the 93 are lost, and to what

| loss | count | what it actually is |
|---|---|---|
| **S1 — a member the evidence layer does not model** | 50 units | The unit contains a printed block whose gold role is outside `tc_sdm.LEARNING_ROLES`, so **no evidence row exists for it and its correctness is not merely unknown, it is unrepresentable.** Across those units the roles are `figure_label` 42 · `instruction` 30 · `table` 16 · `diagram` 12 · `answer_slot` 2. `instruction` is the block that tells the child what to do. |
| **S1 — a member the matcher could not attach** | 14 units | |
| **S2 — a member depends on a figure the slice cannot contain** | 15 units | A gold figure is not a gold block, so a `refers_figure` member can never have its referent verified inside the unit. |
| **S2 — two members matched one pipeline block** | 4 units | The many-to-one matcher shape Phase A found on row #8, met again as a population property. |
| **S2 — a member carries no text in gold** | 7 units | Almost always a table printed with empty answer cells. |
| **S3 — not character-exact** | 14 units | |
| **S4 — role wrong** | 1 unit | |
| **S5 — validation** | 2 units | |
| **S6a — the trust policy** | 2 units | **The two that got furthest.** |

Note the verdict column in `units.jsonl` applies a precedence the survival curve does not: a unit
whose gold carries no text for one member is reported `UNMEASURABLE` rather than `FAIL@S3`, because
**a stage that cannot be measured did not pass.** 62 units are `UNMEASURABLE` on that rule.

### The Bài 17 plane, and the prediction that held

The rule predicted (§6.4) that the Bài 17 plane would produce no PASS at any scope, because its
gold carries **anchors and no verbatim text on any of 73 blocks**, and because
`thresholds/evidence.py::_wrongness` sets `digits_wrong = None` in that case, which
`truth_teaching_critical` then reads as False.

**Measured: 15 units, 9 of them learning slices, all 9 `UNMEASURABLE`, 0 passes.** The prediction
holds, and the consequence is worth stating plainly beyond this phase: **on the only lesson-wide
gold set this repository owns, the digit half of teaching-critical — six of the seven errors that
remain — cannot be detected at all, and reads a silent zero.** That is the shape of defect this
project has named repeatedly, sitting inside the truth layer itself.

---

## 3 · The two that reached VALIDATION, and exactly what stops them

Both are the same shape: **a section heading plus one question. Two blocks.** That is as small as
the rule permits a learning slice to be, and it is the smallest useful learner experience this
corpus can produce: *one task, with the heading that says what it is for.*

| | **UNIT A** | **UNIT B** |
|---|---|---|
| book · grade · subject | `06-sgk-ngu-van-6-tap-mot` · 6 · Ngữ văn | `09-sgk-ngu-van-9-tap-mot` · 9 · Ngữ văn |
| printed page | **20** (pdf 21) | **66** (pdf 67) |
| lesson | Bài 1 | Bài 3 |
| members | heading + question | heading + question |
| S3 · recognition | `cer 0.0`, `edits 0` on both | `cer 0.0`, `edits 0` on both |
| S4 · role | HEADING / QUESTION, both correct | HEADING / QUESTION, both correct |
| S5 · validation | both TRUSTED, **no guard raised** | both TRUSTED, **no guard raised** |
| role confidence | heading 0.88 · question **0.78** (`lexicon`) | heading 0.88 · question **0.85** (`lexicon`) |
| two-stack agreement | `text_sim 100.0`, 0 tone disagreements | **`text_sim 98.0` on the question** |

### Why each frozen trust candidate refuses them

| candidate | refuses | the clause |
|---|---|---|
| **C1 · NAVIGATION-ONLY** | the question | `role_not_teaching_shaped` — refuses `question` by name |
| **C2 · PROSE** (pre-registered) | the question | `role_not_interactive` — refuses `question` by name |
| **C3 · QUESTION SURFACE** | **both members** | `role_is_question_high_confidence` — the heading is not a question, and the question's role confidence is below 0.90 |
| **C4 · C1 + machinery that does not exist** | both, twice over | `sibling_complete` and `digit_sequence_verified` are declared `available: false` in the frozen payload |

Unit B is refused a second time, by `two_stack_exact`: its question's two OCR stacks agree at
98.0 — **while the served string is character-exact against gold.** The trust layer refuses a block
that is right, on a signal that is wrong about it. That is the over-withhold direction the round-5
97-row audit measured at 19 of 30, met here on the single best block in the corpus.

**The refusal is not a threshold.** `test_raising_role_confidence_does_not_rescue_it_under_C2` runs
the same unit at role confidence 0.70, 0.85, 0.90 and 0.99 and gets `FAIL@S6a_POLICY` every time.
The reading gate (C1/C2) excludes *what a child acts on*; the question gate (C3) excludes *what the
role layer can label*. **There is no point on any frozen curve where a complete question section is
admitted**, and finding that is worth more than any number a tuned threshold would have produced.

### And even if the gate opened: S7 has no path

| | |
|---|---|
| TSLs in `poc-out` for `06-sgk-ngu-van-6-tap-mot` | **0** |
| TSLs in `poc-out` for `09-sgk-ngu-van-9-tap-mot` | **0** |
| `LessonDocument`s for either book | **0** |
| `WorkspaceCatalog.defaultSlots` | KHTN 6 #17 · LS&ĐL 5 #8 — **neither book** |

TSLs exist for 13 books; Ngữ văn is not among them. **The slice that survives the most stages is in
a book the delivery pipeline has never processed into a lesson**, and of the five units that
reached RECOGNITION only one (`05-sgk-lich-su-va-dia-li-5` p080, Bài 18) is in a book with a
delivery path — and it fails VALIDATION on `agree_numbers` + `agree_order` with one wrong member.

Even with a path, S7's verdict for such a unit is `LOCAL ONLY`: the text is verbatim SGK, so the
artifact lands in the gitignored `assets/fixtures/real/` tree, D4 keeps it off every device but a
machine that already holds the corpus, and distribution is the separate WAL-43 licence gate.

---

## 4 · The honest end state

> ### **WHAT CAN A CHILD USE NOW THAT THEY COULD NOT BEFORE? NOTHING.**

Not one block, not one question, not one page. The pipeline can now **say, per unit, exactly where
each candidate slice dies**, which it could not before, and that is a measurement, not a delivery.
Nothing was promoted from PARTIAL to DONE. No threshold was activated. No device was walked. No D4
material entered git.

**Three separate gates stand between the best measured slice and a child, and none of them is a
number an agent may set:**

1. **The trust policy refuses the role.** Every frozen candidate refuses a question section — by
   clause, at every confidence. This is an engineering finding and it is actionable without the
   Founder; it is stated in the blocker report as the smallest next implementation.
2. **The trust gate is a Founder act**, and `FALSE-TRUST-AUDIT-PROTOCOL.md` additionally requires a
   second annotator on ≥ 10 % of rows before any bar may be called met. This repository's only
   annotator has ever been a model — the gold pages are «VLM (Claude) reading a `tc_render` grid
   image», the 484-row audit is a «single AI annotator». **Nothing in this phase may be called
   certified, and BOUND-5 per-lesson certification remains unavailable for that reason alone.**
3. **The artifact cannot leave the machine.** Verbatim SGK text is D4; distribution is WAL-43.

The order's RESEARCH STOP CONDITION applies. **No new research direction is opened by this phase.**

---

## 5 · Every headline count re-derived a second way

*«A number of the right type and the wrong quantity passes every check that is not a re-derivation.»*

| count | route 1 | route 2 | agree |
|---|---|---|---|
| units qualifying | `summary.qualifies_gate_closed` = **[]** | recomputed from `units.jsonl`: units with `acts_on` and all six stages true — **[]** | ✔ |
| units through S5 | `summary.through_S5` — **2**, named | recomputed from `units.jsonl` by the first five stages — the **same two ids** | ✔ |
| learning slices | harness `learn` filter — **95** | `units.jsonl` rows with non-empty `acts_on` — **95** | ✔ |
| the 54-page plane | rebuilt here — served **356** · false trust **23** · teaching-critical **8** · digits **6** · as-question **2** | the arm `PHASE-B-QUESTION-VETO` §3.1 published for `main` — identical. **Guard G4 refuses to run if they differ.** | ✔ |
| teaching-critical, 54-page | `truth_teaching_critical` on served rows — **8** | union of the two underlying flags (digits 6 ∪ as-question 2, intersection 0) — **8**. **Also a live guard.** | ✔ |
| lessons fully covered | strictest reading (canonical `tc2-p1` spans only) — **0** | most generous reading (every TSL anywhere in `poc-out`, contested boundaries excluded) — **0** | ✔ |

**One bug of exactly this class was caught by the re-derivation and is recorded in the code.** The
first version of the harness partitioned the two planes on the gold `gold_set` field. That field is
**absent on 38 of the 54 pages and reads `tc-v2` on the other 16**, so the partition silently
dropped a third of the plane and the guard printed **7** teaching-critical rows where the plane
holds **8**. A count of the right type and the wrong quantity, inside the guard whose job is to
prove the population contains the failing cases. The plane is now the directory, and G4 pins the
totals against Phase B's published arm so the same class of error cannot return silently.

---

## 6 · The gate is neither vacuous nor unreachable — both proved

A zero means nothing unless the gate that produced it could have printed something else.

**REACHABILITY — 21 corpus-free tests, `tool/tests/test_phase_f_slice_gate.py`.**
`test_a_perfect_unit_qualifies` constructs the unit the bar describes — a heading plus an
**activity**, which `GOLD_ROLE_MAP` sends to `BODY` and which C2 therefore does not refuse by role
— and asserts the harness prints `QUALIFIES_GATE_CLOSED`. **The verdict is reachable.** The corpus
zero is a fact about the corpus, not about the bar.

**NON-VACUITY — one test per stage.** Each breaks exactly one property of that same perfect unit
and asserts the verdict names that stage: an unmatched member → `FAIL@S1`; two members on one block
→ `FAIL@S2`; one edit → `FAIL@S3`; a wrong coarse role, and a non-question served as a question →
`FAIL@S4`; a withheld member, a guard reason, a teaching-critical member → `FAIL@S5`; a two-stack
disagreement → `FAIL@S6a`. A member with no gold text → `UNMEASURABLE`, never a pass.

**THE GUARDS — six provocations, every one exits non-zero.**

| provocation | result |
|---|---|
| `--detail` pointed inside the repository | `REFUSED (G5)`, exit 1, **and no file is written** |
| the plane is smaller than declared (`--min-pages 999`) | `UNVERIFIED`, exit 1 |
| the 54-page plane emptied | `UNVERIFIED (G2)`, exit 1 — «a bar never shown a failing case has not been tested» |
| the published arm G4 pins is edited by one block | `UNVERIFIED (G4)`, exit 1 |
| **the bar mutated to pass everything** | `UNVERIFIED (G2)`, exit 1, **naming the units holding a known failing row that qualified** |
| the failing rows filtered out of the plane | `UNVERIFIED (G2)`, exit 1 — «the failing case this bar must reject is not where it was left» |

Each mutation was applied to a backed-up copy of the real file, asserted to have landed on disk
before the run, and the file was restored and byte-compared afterwards.

Suite: **984 → 1005 tests, skips unchanged at 29, all green.**

---

## 7 · PLANNED vs ACTUAL

| # | Planned | Status | Actual |
|---|---|---|---|
| 1 | Write the selection rule **before** the evaluation | **DONE, first** | `PHASE-F-SELECTION-RULE.md` @ `aadaa137129f53c0`, the first commit on the branch; the harness is the second |
| 2 | Find the smallest real learning slice that can go end to end | **DONE — and it does not** | 236 units judged; the furthest any gets is VALIDATION |
| 3 | Prefer 1 grade × 1 subject × 1 lesson or content type | **DONE, shrunk twice** | lesson → page → **section**; the survivors are 2 blocks each |
| 4 | Do not lower the evidence bar | **HELD** | the bar is the rule's, unchanged; two stages were made *stricter* after measurement (a contested lesson boundary is not a boundary), never looser, and both changes are their own commit |
| 5 | Prove the slice cannot report success on an empty population | **DONE** | six guard provocations, all red; the bar mutated to pass everything is caught by G2 |
| 6 | Re-derive every headline count a second way | **DONE** | §5, six counts, two routes each — and one real bug caught by doing it |
| 7 | Answer the Founder's question in his words | **DONE** | §4. **NOTHING** |
| — | Reach a learner | **NOT ACHIEVED** | RESEARCH STOP CONDITION applies; `NARROW-SLICE-BLOCKER-REPORT.md` is the deliverable |
| — | Activate a threshold | **NOT DONE, correctly** | Founder gate. `policy.admits()` returns a refusal list and has no code path that writes |
| — | Walk the device | **NOT DONE, correctly** | the Founder is offline; nothing here claims hardware verification |

**Nothing was promoted from PARTIAL to DONE.**

---

## 8 · Claims by label

| label | claim |
|---|---|
| **PROVEN** | the selection rule precedes the harness in the commit graph; `QUALIFIES_GATE_CLOSED` is reachable (a synthetic perfect unit prints it) and every stage can independently refuse; all six adequacy guards exit non-zero under provocation, including a bar mutated to pass everything; raising role confidence to 0.99 does not admit a question section under C2 |
| **MEASURED** | 236 units over 58 pages / 696 gold rows; 95 learning slices; survival 39 · 19 · 5 · 4 · 2 · 0; the two surviving units' `cer 0`, roles, guards and role confidences (0.78, 0.85); C1/C2/C3/C4 refusals per unit; 0 lessons fully covered by gold on both readings; 1 contested lesson boundary; 0 TSLs for either surviving unit's book; the 54-page plane reproducing Phase B's published arm exactly |
| **OBSERVED** | that the roles the evidence layer does not model (`instruction`, `figure_label`, `table`, `diagram`, `answer_slot`) are what stops 50 of the 95 learning slices at SOURCE; that unit B's question is refused by `two_stack_exact` while being character-exact against gold |
| **INFERRED** | that the class distribution of these failures is a property of the pipeline rather than of these particular pages — the gold plane is deliberately hard and is not a sample |
| **HYPOTHESIS** | that a book with a delivery path would show the same stage distribution as Ngữ văn; nothing here measures that, because the two books that have a path fail earlier for reasons of their own |
| **UNKNOWN** | whether any unit would clear a trust policy written *for a question surface a child uses*, because no such policy exists to evaluate; whether the gold transcription itself is right, because it has never been checked by a human |
| **FALSIFIED** | nothing of the rule's four predictions. All four held: at least one unit reached S5 (two did); zero reached a child; the answer is NOTHING; the Bài 17 plane produced no pass at any scope |

---

## 9 · Files, and how to reproduce

| file | what |
|---|---|
| `docs/research/PHASE-F-SELECTION-RULE.md` | the rule, committed first (`aadaa137129f53c0`) |
| `tool/corpus/audit/phase_f_slice_gate.py` | the gate: enumerates every unit, judges all, guards its own population |
| `tool/tests/test_phase_f_slice_gate.py` | 21 corpus-free tests — reachability, per-stage non-vacuity, the two structural claims |
| `docs/research/NARROW-SLICE-BLOCKER-REPORT.md` | the RESEARCH STOP CONDITION deliverable |
| `docs/research/PHASE-F-NARROW-TRUSTED-SLICE.md` | this report |

```
python3 tool/corpus/audit/phase_f_slice_gate.py \
    --out <units.jsonl> --summary <summary.json> --detail <outside-the-repo.json>
python3 -m unittest tool.tests.test_phase_f_slice_gate -v
```

`--out` and `--summary` carry ids, roles, booleans and counts. **Every reading goes to `--detail`,
which is refused inside the repository and never enters git.** The measurement inputs
(`poc-out/**`) are git-excluded by design; on a worktree `poc-out` is a symlink, which is why the
lesson-span scan uses a recursive glob rather than a plain `find`.

---

`trusted = 0` · `eligible for teaching = 0` · **no threshold activated** · **no device** ·
**the best slice in the corpus is two blocks long, it is correct, and every gate in front of it is
closed by a clause or by a person.**
