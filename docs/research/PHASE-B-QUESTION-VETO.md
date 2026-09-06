# PHASE B — THE QUESTION-PROMOTION VETO, AND WHAT ADJUDICATION DID TO ITS TARGET

Founder order 47 §PHASE B + §PHASE C · branch `phase-b/question-veto`, based on `main` @ `8dd9f3f` ·
**No threshold was activated. Nothing was served. `trusted = 0` and `eligible for teaching = 0` are
unchanged.** No SGK page, crop, reading or served string appears in this document or in anything
this work committed.

---

## 0 · The one-paragraph answer

**The adjudication moved the target before a line of the fix was written, and it moved it in the
direction that costs a row.** Of the five gold role labels behind Phase A's ROLE DISAMBIGUATION
class — never put through `ROLE-DEFINITION-SPEC-v1` §7 — four are upheld and **one is overturned**:
`10-sgk-vat-li-10` p030 `b03` is the *statement* of a worked example, and the spec's ANSWER
§exclusion says in as many words that the statement of a worked example is QUESTION. **The served
role on that row is correct. The honest baseline is 11 teaching-critical errors, not 12.** That
finding falsifies Phase A's **P2** as written — it vetoed that row, and measured over the same 54
pages its lead-in pattern also fires on a block where the same verb *governs an object*, which is a
real task. P2 is replaced by a rule keyed on the punctuation rather than the word. **P1 and P3
stand.** Measured rebuild-against-rebuild, per gold row, on the 54-page plane: **teaching-critical
11 → 7 · false trust 25 → 22 · 0 served blocks withdrawn · 0 of 66 correct questions broken.**
And the part that matters more than the number: **the teaching-critical gain is entirely in-sample
and could not be reproduced out of sample, because no labelled plane in this repository contains the
failure class.** What *did* reproduce out of sample is the role correction — **4 independent role
changes, 2 of them on held-out gold pages, 4 corrections, 0 regressions.**

---

## 1 · The adjudication, which came first

The Founder's standing rule from round 5 is **role spec before tuning**, and Phase A deferred this
deliberately. `tool/corpus/audit/ROLE-ADJUDICATION-v1.json` carries the ruling row by row with its
citation. Summary:

| row | gold label | verdict | basis (ROLE-DEFINITION-SPEC-v1) | effect |
|---|---|---|---|---|
| **#3** `07-sgk-toan-7-tap-hai` p041 `b03` | `heading` | **UPHELD** | QUESTION §exclusion — «A question-form section title (→ HEADING)»; §7 R2 | 0 |
| **#7** `09-sgk-toan-9-tap-mot` p029 `b01` | `body` | **UPHELD** | ANSWER §exclusion — a `Nhận xét` that generalises rather than answering is RULE or BODY | 0 |
| **#9** `10-sgk-vat-li-10` p030 `b03` | `body` | **OVERTURNED → `question`** | ANSWER §exclusion — «The *statement* of the worked example (its data and its question) — that is QUESTION or FORMULA». §7 **R3** scopes ANSWER to the *solution*, which on this page is a separate gold block under its own heading | **−1** |
| **#10** `10-sgk-vat-li-10` p030 `b19` | `sidebar` | **UPHELD** | SIDEBAR §semantic names this label; SIDEBAR §inclusion (geometrically inside the labelled box) | 0 |
| **#11** `10-sgk-vat-li-10` p089 `b06` | `body` | **UPHELD** | QUESTION §inclusion admits an *enumerated* item opening with a directive verb; this region carries no enumerator, no «?», no options and no lead | 0 |

**Decidability.** All five are decided on the axis that matters — is the printed unit a QUESTION —
and that is the axis every count in this report turns on. On the **fine** role the spec decides only
two of the five; three carry a residual ambiguity that moves no count because both candidates sit
in `tc_sdm.NOT_A_QUESTION`. That is stated rather than rounded away: **5/5 decided on the question
axis, 2/5 on the fine role.** Round 5 measured the spec's decidability at 0.885 on a known-hard
sample; this is a different, much smaller sample and the two must not be pooled.

### Three spec defects the adjudication exposed

Each is a contradiction *inside* `ROLE-DEFINITION-SPEC-v1`, found by applying it rather than reading
it. **None is resolved here** — doctrine is not settled by the agent applying it.

| id | the contradiction |
|---|---|
| **Q-ROLE-6** | HEADING §exclusion: «A line that ends in `?` (→ QUESTION)». QUESTION §exclusion: «A question-form section title (→ HEADING)». For a question-form section title these are mutually exclusive. Row #3 is adjudicated on the more specific clause. |
| **Q-ROLE-7** | The spec's normative ANSWER §exclusion makes a worked example's statement a QUESTION, while the spec's own illustrative confusion list under QUESTION cites row #9 as a `BODY → QUESTION` **error**. A normative rule and an example in the same document disagree; the rule is applied. |
| **Q-ROLE-8** | SIDEBAR §semantic lists `Em có thể` among the sidebar labels; SIDEBAR §exclusion sends «a tinted box listing what the child will be able to do» to OBJECTIVE; OBJECTIVE §exclusion routes `Em đã học` to SIDEBAR and is silent on `Em có thể`. Row #10 is decided as `sidebar`, and the question axis is unaffected either way. |

### What the adjudication did to the target

**The committed gold is unchanged.** The ruling is an **overlay** applied by the measurement harness
(`--adjudication`), never written into `tool/corpus/tc_gold/*.json`, so every published figure over
the 643-row plane still reproduces byte-identically. Correcting the gold itself is a Founder
decision and is filed as one.

| | as published | adjudicated |
|---|---|---|
| teaching-critical, served | 12 | **11** |
| — as-question | 6 | **5** |
| distinct served blocks | 11 | **10** |
| of which not pipeline errors at all (Phase A §3) | 2 | 2 |
| **honest served-error count** | 10 on 10 blocks | **9 on 9 blocks** |

---

## 2 · What shipped, and why it is not what Phase A recommended

| | rule | derived from | status |
|---|---|---|---|
| **P1** | `assign_role`: the extractor's own `section_header` / `title` label is no longer discarded because the line ends in «?». A title that is *enumerated* or that *opens with a directive verb* is still a task and is untouched. | #3 | **shipped as recommended** |
| **P2** | ~~a block opening with a worked-example or remark lead-in is not promoted to QUESTION~~ → **a leading directive verb closed by a FULL STOP does not promote to QUESTION.** A block that actually ends in «?» is untouched. | #7 | **FALSIFIED as written, replaced** |
| **P3** | `SIDEBAR_LABEL` matches the labels **as printed**: its vowel classes carried only the plain and circumflex forms. | #10 | **shipped as recommended** |

### Why P2 as written is falsified — two measurements, not an opinion

1. **It vetoed a correct question.** Its `Bài tập ví dụ|Ví dụ N` clause removes row #9, which the
   adjudication says is served correctly. On the adjudicated plane that clause is a **regression**,
   not a −1.
2. **On the same 54 pages its `Nhận xét` clause fires on a real task.** The lead-in pattern matches
   **6 blocks**; three of them are `question` today. One is `09-sgk-khoa-hoc-tu-nhien-9` p046, where
   the same verb **governs an object** — an instruction to comment on something, ending in a
   reference to a table. P2 as written demotes it to `body`. It happens to be WITHHELD, so the
   served plane never shows the damage. **That is luck, not correctness**, and it is exactly the
   shape this project has been burned by: a rule that looks clean only because its failing case is
   invisible on the plane it was scored on.

The replacement keys on the **punctuation**, because that is what actually separates the two:
`Nhận xét.` + a declarative sentence is a label opening a remark; `Nhận xét` + its object is an
instruction. Both spellings exist in this corpus. The rule is stated as a general property of the
whole directive lexicon, not as a list of remark words.

### P3, re-derived on a definition anchored in the code

Phase A reported «misses 10 of 19». Re-derived here on a definition that can be checked — *blocks on
the 54 gold pages whose whole text is a sidebar-family label, recognised by the `STAGE` lexicon* —
the number is: **14 such blocks · the old pattern matched 7 · the new pattern matches 14.** Every one
of the 7 misses is a tone-marked vowel (`thể`, `biết`, `BIẾT`); every `Em đã học`, which has no tone
in the affected class, already matched. The two counts differ because Phase A's population also
included OCR-corrupted spellings of the same labels; both support the same finding, and **this one
is stated with its definition so it can be re-derived.**

---

## 3 · Before → after, in the categories the order names

Both columns are **rebuilds**, produced by the **same harness file run from two worktrees** — one at
`origin/main`, one on this branch — so the only difference between them is the change. The BEFORE
rows produced from the pristine worktree are **byte-identical** to the BEFORE rows produced from
this worktree before the edit.

### 3.1 The served plane, 54 gold pages, 643 learning rows

| | **BEFORE** | **AFTER** | | **BEFORE** | **AFTER** |
|---|---|---|---|---|---|
| | *gold as published* | | | *adjudicated gold* | |
| served (trusted) blocks | 356 | **356** | | 356 | **356** |
| **teaching-critical rows** | **12** | **8** | | **11** | **7** |
| teaching-critical rate | 0.0337 | **0.0225** | | 0.0309 | **0.0197** |
| false trust | 26 | **23** | | 25 | **22** |
| FTR | 0.0730 | **0.0646** | | 0.0702 | **0.0618** |
| correctly-served QUESTION blocks | 65 | **65** | | 66 | **66** |
| coarse role wrong, served | 58 | **52** | | 57 | **51** |
| blocks withdrawn | — | **0** | | — | **0** |

### 3.2 By root-cause class (Phase A §4), adjudicated plane, **no double-counting**

| class | **BEFORE** | **AFTER** | what changed |
|---|---|---|---|
| **1 · BLOCK BOUNDARY / SEGMENTATION** | 1 | **1** | untouched — no rule here addresses it |
| **2 · CHARACTER / DIGIT RECOGNITION** | 4 | **4** | untouched — four rows needing four different mechanisms |
| **3 · ROLE DISAMBIGUATION** | 4 | **1** | #3, #7, #10 removed. **#11 remains and nothing here touches it** |
| **4 · COMPOSITION / GROUPING** | 0 | **0** | empty on this population, measured both times |
| **5 · PIPELINE ORDERING** | 0 | **0** | empty on this population, measured both times |
| **6 · UNKNOWN** | 0 | **0** | — |
| **NOT A PIPELINE ERROR** (measurement artefacts) | 2 | **1** | the matcher artefact #8 no longer fires `as_question`; it stays false-trusted through its `order` flag. The tokeniser artefact #12 is untouched |
| **teaching-critical total** | **11** | **7** | |

A row is counted **once**, at the layer its causal chain ends. #8 sits on the *same candidate block*
as #7 — the evaluation matcher attached two gold blocks to one served block — so the one role change
moves two rows; #8 is reported as an artefact, not as a second win.

**⚠ Do not read 0.0197 as beating round 7's ≈0.021 floor.** That floor was measured over signal
combinations chosen **without seeing the rows**; these rules were derived from the rows they remove.
The comparison is invalid in the direction that flatters this work. It also remains **5.6× above
BOUND-2's 0.0035.**

---

## 4 · In-sample and out-of-sample, separated, both stated

### 4.1 What is in-sample

The three rules were derived from **three rows** (#3, #7, #10). All four teaching-critical rows the
change removes lie on the derivation plane, and one of the four (#8) is an artefact riding the same
candidate block as a derivation row. **The teaching-critical −4 is in-sample. Full stop.**

### 4.2 The out-of-sample planes, and the honest news about them

| plane | rows | served | as-question errors BEFORE | teaching-critical Δ | role Δ | withdrawn |
|---|---|---|---|---|---|---|
| **held-out gold** (16 of the 54 pages carry `held_out: true`) | 181 | 99 | **0** | **0** | **−2 (both corrections)** | 0 |
| **Bài 17 gold** (`tc_gold_bai17`, a separate gold set, 4 pages) | 53 | 44 → 43 | 2 | **0** | **−1 (a correction)** | **1** |
| **the 54-page plane, every row the rules were not derived from** (includes the held-out 16 pages) | 640 | — | — | **0** | **−3 (all corrections)** | 0 |

**The teaching-critical gain does not reproduce out of sample, and it cannot — the planes do not
contain the failure class.**

- The **held-out gold plane holds zero as-question errors before the change.** A veto measured
  there would print a flawless zero and mean nothing. This is the same trap the Phase A probe
  refuses to run into, met again on the other side.
- The **Bài 17 plane's two as-question errors are `ACTIVITY → QUESTION`** — a class none of these
  three rules addresses. The change removes neither, and that is the correct outcome, not a miss.

**What *does* reproduce is the role correction, and this is the finding to carry forward.** Seven
gold rows change role on the 54-page plane. Three are derivation rows and one shares their candidate
block. The **four independent changes are all corrections**:

| row | plane | change | gold |
|---|---|---|---|
| `04-sgk-khoa-hoc-4` p009 `b12` | **held-out** | `objective` → `sidebar` | `sidebar` ✔ |
| `07-sgk-khoa-hoc-tu-nhien-7` p096 `b13` | **held-out** | `objective` → `sidebar` | `sidebar` ✔ |
| `11-sgk-vat-li-11` p105 `b16` | 54-page, not a derivation row | `body` → `sidebar` | `sidebar` ✔ |
| `06-sgk-khoa-hoc-tu-nhien-6` p064 `b12` | **Bài 17 gold set** | `heading` → `sidebar` | `sidebar` ✔ |

**4 of 4 correct · 0 regressions.** The first of them is a block `ROLE-DEFINITION-SPEC-v1` already
names in print as one of its four measured `SIDEBAR → OBJECTIVE` errors, «TRUSTED as an objective» —
independently annotated, on a held-out page, and this change corrects it.

The Bài 17 correction costs its block: `sidebar` is not colour-exempt, so the newly-correct role is
now **WITHHELD**. That is the fail-closed direction and it is the consequence the spec already flags
with a ⚠ — the role most often printed on colour is the role least protected from the colour guard.
**Served count on that plane 44 → 43.**

### 4.3 Blast radius on an unlabelled plane — 1,124 pages

`tool/corpus/audit/phase_b_blast_radius.py`, both arms, 12 books · 1,124 pages · **28,542 blocks**:

| | |
|---|---|
| blocks whose role changes | **197 (0.69 %)**, on 100 pages, in 6 of the 12 books |
| the transitions | `→ sidebar` 178 · `→ heading` 16 · `→ body` 3 |
| **QUESTION demotions** | **31** (`question → sidebar` 18 · `→ heading` 11 · `→ body` 2) |
| **QUESTION promotions** | **0** — coarse question count 2,385 → 2,354, exactly the 31 |
| trust status changes | 35: `CONFLICT → TRUSTED` 22 · `WITHHELD → TRUSTED` 6 · **`TRUSTED → WITHHELD` 6** · `CONFLICT → WITHHELD` 1 |

All six withdrawals are `heading|caption → sidebar` on colour — the same fail-closed consequence.
**No correctness is claimed on this plane: it has no labels.** It measures reach, and the reach is
narrow and one-directional.

---

## 5 · Every headline count re-derived a second way

*«A number of the right type and the wrong quantity passes every check that is not a re-derivation.»*

| count | route 1 | route 2 | agree |
|---|---|---|---|
| served / false trust / as-question / correct questions, AFTER | per-gold-row diff of `phase_b_veto_measure.py` — **356 / 23 / 2 / 65** | `phase_a_veto_probe.py`'s own baseline, a different aggregation (`tc_score.score` page totals, not evidence rows), run on this branch — **356 / 23 / 2 / 65** | ✔ |
| teaching-critical, AFTER | `truth_teaching_critical` on served rows — **8** | union of the two underlying flags: digits **6** ∪ as-question **2**, intersection **0** — **8** | ✔ |
| BEFORE arm | rebuilt from this worktree before the edit | rebuilt from a **separate pristine worktree** at `origin/main` with the same harness file — **byte-identical JSONL** | ✔ |
| P3's label miss | Phase A: 10 of 19, broader population | code-anchored definition here: **7 of 14 correctly-printed label blocks matched by the old pattern, 14 of 14 by the new** | same finding, both definitions stated |
| distinct served blocks carrying the teaching-critical rows | 12 rows → **11** blocks BEFORE | 8 rows → **8** blocks AFTER; adjudicated 7 → **7** | ✔ |

---

## 6 · Mutation results — the guards are alive

**Seven mutants of the three rules. All seven killed.** `python3 -m unittest tool.tests.test_tc2_question_veto`

| mutant | killed by |
|---|---|
| **M1** revert P1 (restore the `not ends with "?"` clause) | `test_a_question_form_section_title_is_a_heading` |
| **M2** widen P1 (drop the directive-opening clause) | `test_a_title_that_opens_with_a_directive_verb_is_still_a_question` |
| **M3** revert P2 (drop the full-stop veto) | `test_a_remark_marker_closed_by_a_full_stop_is_not_a_question` |
| **M4** **P2 as Phase A wrote it** — veto the *word*, ignore the stop | `test_the_same_verb_governing_an_object_is_still_a_question` + 2 more |
| **M5 / M6** revert either half of P3's vowel classes | `test_every_correctly_printed_label_matches`, `test_a_correctly_printed_label_now_opens_the_box_context` |
| **M7** make `SIDEBAR_LABEL` match everything | 4 tests, including the P1 cases |

M4 is the one worth naming: **the test suite rejects the rule the audit recommended.** Each mutation
was applied to a backed-up copy of the real file, the change was asserted to have landed before the
suite ran, and the file was restored and the suite proved green again afterwards.

**Six adequacy guards on the two harnesses, each proved to exit non-zero** — *absence cannot satisfy
a positive obligation*, and *test populations must contain the failing case*:

| guard | provocation | result |
|---|---|---|
| the plane must contain all twelve Phase A rows, present **and matched** | remove one gold page | `UNVERIFIED`, exit 1, names the missing row |
| a `--require none` plane must declare its own size | omit `--min-rows` | `UNVERIFIED`, exit 1 |
| the declared size must hold | `--min-rows 999` on a 53-row plane | `UNVERIFIED`, exit 1 |
| an adjudication overlay must actually apply | overlay naming a row not in the plane | `UNVERIFIED`, exit 1 — «would leave the numbers unchanged and look like agreement» |
| D4 | `--detail` pointed inside the repository | `REFUSED`, exit 1, **no file written** |
| the blast-radius plane must be large enough | `--min-pages` above the plane | `UNVERIFIED`, exit 1 |

The D4 guard was itself wrong when first written — `startswith` on a path string made a sibling
directory `<repo>-work` look like a directory *inside* `<repo>` — and is now a resolved-path
containment test. It is recorded because it is the same class of defect as the ones this project
keeps paying for: **a check of the right shape and the wrong quantity.**

Suite: **967 → 984 tests, skips unchanged at 38, all green.**

---

## 7 · What remains unfixed

| | |
|---|---|
| **Row #11** `10-sgk-vat-li-10` p089 `b06` | The adjudication **upholds** the gold label, so this is a real pipeline error and **no rule here touches it.** An unenumerated imperative that states the aim of an experimental-design section, with no structural signal separating it from a task. §7 does not decide BODY vs ACTIVITY for it either. **Fix: still unknown.** |
| **The 6 digit rows** | Untouched, and now **6 of the 7 remaining teaching-critical errors**. Four different mechanisms are needed (Phase A §3): a stacked-fraction reader, cross-engine arbitration, something no stack here possesses, and a re-read of ink that produced no text item. |
| **The segmentation row #4** | Untouched. One row, one fix, one row's worth of value. |
| **`ACTIVITY → QUESTION`** | The Bài 17 plane's two as-question errors, and 3 more in the round-4 confusion matrix. **A class no rule here addresses**, and the only as-question class with a labelled population outside the derivation plane. This is the next question-vs-non-question work that has evidence behind it. |
| **The blind populations** | `BLIND-CORE` / `BLIND-TEACHING` still hold **no role annotation**, so they cannot measure this at all. Phase A asked for that measurement; it is not possible without an annotation pass, and saying so is the honest answer rather than substituting a proxy. |
| **A title opening with an interrogative the lexicon knows** (`Vì sao …?`) | P1 deliberately does **not** rescue it. No such row exists in the measured population, and widening the rule on no evidence would put every mislabelled `Vì sao …?` prompt at risk. Pinned by a test that states the limit. |
| **Q-ROLE-6 / 7 / 8** | Three contradictions inside `ROLE-DEFINITION-SPEC-v1`, reported and **not resolved here.** |
| **The gold correction for row #9** | An overlay, not a commit. The Founder decides whether `tool/corpus/tc_gold/10-sgk-vat-li-10-p030.json` is corrected — it moves a published truth flag. |

---

## 8 · PLANNED vs ACTUAL

| # | Planned | Status | Actual |
|---|---|---|---|
| 1 | Adjudicate the 5 gold role labels against `ROLE-DEFINITION-SPEC-v1` §7 **before** tuning | **DONE, first** | 4 upheld, **1 overturned**; target moved 12 → 11; three spec contradictions reported, none resolved |
| 2 | Implement the smallest upstream intervention | **DONE, altered** | P1 and P3 as recommended; **P2 falsified and replaced** on two measurements |
| 3 | Re-measure the real population BEFORE → AFTER in the order's categories | **DONE** | §3, both gold planes, per class, no double-counting |
| 4 | Separate in-sample from out-of-sample and state both | **DONE** | §4. In-sample −4 teaching-critical. **Out-of-sample teaching-critical gain: 0, and unmeasurable — the planes hold no instance of the class.** Out-of-sample role: 4 of 4 correct |
| 5 | Mutation-check the guards | **DONE** | 7 rule mutants killed, 6 adequacy guards proved live, one guard found broken and fixed |
| 6 | Do not double-count a root cause | **DONE** | #8 rides #7's candidate block and is reported as an artefact, not a second win |
| 7 | Re-derive every headline count a second way | **DONE** | §5, four counts, two routes each; the BEFORE arm reproduced from a separate pristine worktree |
| 8 | Falsify the fix if it does not improve out of sample | **PARTIALLY APPLIED** | The **teaching-critical claim is not carried out of sample** and is labelled in-sample everywhere it appears. The **role claim is carried**, on 4 independent rows. Nothing is polished into a pass |
| — | Measure on `BLIND-CORE` / `BLIND-TEACHING` | **NOT POSSIBLE** | Those populations carry lesson identities and no role annotation. Reported as a blocker, not worked around |
| — | Fix row #11 | **NOT STARTED** | Correctly: the adjudication says it is a real error and offers no signal to key on |

**Nothing was promoted from PARTIAL to DONE.**

---

## 9 · Claims by label

| label | claim |
|---|---|
| **PROVEN** | the BEFORE arm reproduces byte-identically from a pristine worktree; the AFTER totals agree across two independent aggregation paths; 7 of 7 rule mutants are killed and 6 of 6 adequacy guards exit non-zero; no rule in this change promotes anything to QUESTION (0 promotions in 28,542 blocks) |
| **MEASURED** | 12 → 8 / 11 → 7 teaching-critical, 26 → 23 / 25 → 22 false trust, 0 withdrawn, 0 correct questions broken on the 54-page plane; 4 of 4 out-of-sample role changes correct; 0 out-of-sample teaching-critical change; 197 of 28,542 blocks touched over 1,124 pages, 31 question demotions, 6 withdrawals; `SIDEBAR_LABEL` matched 7 of 14 correctly-printed labels before and 14 of 14 after |
| **ADJUDICATED** | four gold labels upheld and one overturned under `ROLE-DEFINITION-SPEC-v1` §7, with the clause cited per row |
| **OBSERVED** | that P2-as-written's failing case is invisible on the served plane only because the block is WITHHELD; that all six withdrawals are the colour guard meeting a newly-correct `sidebar` |
| **HYPOTHESIS** | that the role correction seen on 4 independent rows continues to hold at corpus scale; that the 31 question demotions on the unlabelled plane are mostly correct |
| **UNKNOWN** | what fixes row #11; whether the teaching-critical gain survives on any population that contains the class, because none is annotated; how many `ACTIVITY → QUESTION` errors the corpus holds |
| **FALSIFIED** | Phase A's **P2** as written — on the adjudicated plane its `Ví dụ` clause is a regression, and its `Nhận xét` clause demotes a real task on the very plane it was scored on |

---

## 10 · Files, and how to reproduce

| file | what |
|---|---|
| `tool/corpus/tc2_sdm.py` | the three rules: `SIDEBAR_LABEL`, `LEAD_VERB_STOP`, and the two clauses in `assign_role` |
| `tool/corpus/audit/ROLE-ADJUDICATION-v1.json` | the adjudication, row by row, with the overlay it proposes. **The committed gold is not modified** |
| `tool/corpus/audit/phase_b_veto_measure.py` | the per-gold-row before/after harness, its population-adequacy guard and its D4 refusal |
| `tool/corpus/audit/phase_b_blast_radius.py` | the per-block reach measurement on an unlabelled plane |
| `tool/tests/test_tc2_question_veto.py` | 17 tests; every rule carries both directions |
| `docs/research/PHASE-B-QUESTION-VETO.md` | this report |

```
# both arms, from two worktrees, same harness file
python3 tool/corpus/audit/phase_b_veto_measure.py \
    --sdm poc-out/round4/pipeline/tc2-p2/sdm-gold \
    --adjudication tool/corpus/audit/ROLE-ADJUDICATION-v1.json \
    --out <rows.jsonl> --detail <outside-the-repo.json> --label AFTER

# the out-of-sample gold set
python3 tool/corpus/audit/phase_b_veto_measure.py \
    --pages-from-gold --gold-dir tool/corpus/tc_gold_bai17 \
    --require none --min-rows 40 --out <bai17.jsonl>

# reach, 1,124 unlabelled pages
python3 tool/corpus/audit/phase_b_blast_radius.py \
    --from-raw poc-out/trusted-corpus/tc-v2/tc2-p1/bakeoff/raw --out <blast.jsonl>
```

Both harnesses exit non-zero with `UNVERIFIED` on an inadequate population. `--detail` carries the
readings, is refused inside the repository, and never enters git. The measurement inputs
(`poc-out/**`) are git-excluded by design.

---

`trusted = 0` · `eligible for teaching = 0` · **no threshold activated** ·
**the adjudication cost a row before the fix earned four, and the four are in-sample.**
