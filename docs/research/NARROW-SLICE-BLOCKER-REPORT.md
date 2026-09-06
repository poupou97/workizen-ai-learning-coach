# NARROW-SLICE BLOCKER REPORT

Founder order 47 · **RESEARCH STOP CONDITION** · branch `phase-f/narrow-trusted-slice`, base
`main` @ `5d77cb1` · 2026-09-06

> «Nếu sau iteration này vẫn trusted = 0 hoặc eligible for teaching = 0 hoặc không tạo được
> learner-servable trusted slice, THÌ STOP mở research direction mới … Thay vào đó tạo
> NARROW-SLICE-BLOCKER-REPORT với: smallest attempted slice · exact blocker · minimum missing
> capability · evidence · smallest next implementation required.»

The slice did not reach a learner. This is that report. **No new research direction is opened by
it, and none should be started that does not directly unblock the slice named below.**

Measurement, method and every count: `docs/research/PHASE-F-NARROW-TRUSTED-SLICE.md`.
Selection rule, written before the evaluation: `docs/research/PHASE-F-SELECTION-RULE.md` @
`aadaa137129f53c0`.

---

## 1 · Smallest attempted slice

**A section heading plus one question. Two blocks.** The smallest unit the selection rule permits
to be called a learning slice, because anything smaller is a fragment and round 5's defect 8
established that serving a mutilated structure is itself teaching-critical.

Two units in the corpus have this shape and clear every measurable stage:

| | unit A | unit B |
|---|---|---|
| book | `06-sgk-ngu-van-6-tap-mot` | `09-sgk-ngu-van-9-tap-mot` |
| grade · subject | 6 · Ngữ văn | 9 · Ngữ văn |
| printed page | 20 | 66 |
| lesson | Bài 1 | Bài 3 |
| members | heading + question | heading + question |

Both are **character-exact against gold** (`cer 0.0`, `edits 0` on every member), **correctly
roled**, **served by the unchanged pipeline gate with no guard raised**, and free of every
structural defect the bar tests for. They are the best content this repository has.

They were not chosen. The harness enumerated **236 candidate units** across **58 gold pages** and
judged all of them by one bar; these two are what survived.

---

## 2 · Exact blocker

**Three, in the order a slice meets them. None is a number an agent may set.**

### BLOCKER 1 — the trust policy refuses the role, at every confidence

| candidate | verdict on the surviving units | refusing clause |
|---|---|---|
| C1 · NAVIGATION-ONLY | REFUSED | `role_not_teaching_shaped` — refuses `question` by name |
| **C2 · PROSE** (the recommended candidate) | **REFUSED** | `role_not_interactive` — refuses `question` by name |
| C3 · QUESTION SURFACE | REFUSED, **both members** | `role_is_question_high_confidence` — the heading is not a question; the question's role confidence is **0.78** (unit A) and **0.85** (unit B) against a required **0.90** |
| C4 · C1 + machinery that does not exist | REFUSED | `sibling_complete` and `digit_sequence_verified` are `available: false` in the frozen payload |

**This is a clause, not a threshold.** `test_raising_role_confidence_does_not_rescue_it_under_C2`
runs the same unit at 0.70, 0.85, 0.90 and 0.99 and the verdict never changes. Every frozen
candidate is either a **reading** gate that excludes what a child acts on, or a **question** gate
that no complete section can clear because a section contains its heading.

Additionally on unit B: `two_stack_exact` refuses its question at `text_sim 98.0` **while the
served string is character-exact against gold** — the trust layer refusing a block that is right.

### BLOCKER 2 — trust cannot be claimed at all, by anyone but the Founder, and not yet by them

1. `THRESHOLDS.json` does not exist, so `trusted = 0` by construction. Creating it is a **Founder
   gate** (order 47 §FOUNDER GATES).
2. `FALSE-TRUST-AUDIT-PROTOCOL.md` line 82: **«a second annotator on ≥ 10 % of rows before any bar
   is called met.»** It has never been run. Every piece of ground truth in this repository is
   model-produced — the gold pages are «VLM (Claude) reading a `tc_render` grid image», the 484-row
   audit is a «single AI annotator, page-render based». **BOUND-5 per-lesson certification, the
   one route round 7's arithmetic said was ACHIEVABLE, is unavailable for this reason alone: it
   spends human attention, and no human attention has ever been spent.**

### BLOCKER 3 — the slice has no delivery path, and could not be distributed if it had one

| | |
|---|---|
| TSLs anywhere in `poc-out` for `06-sgk-ngu-van-6-tap-mot` | **0** |
| TSLs anywhere in `poc-out` for `09-sgk-ngu-van-9-tap-mot` | **0** |
| `LessonDocument`s for either book | **0** |
| `WorkspaceCatalog.defaultSlots` | KHTN 6 #17 · LS&ĐL 5 #8 — **neither book** |

The pipeline has produced TSLs for 13 books; Ngữ văn is not one of them. **The slice that measures
best is in a book the delivery pipeline has never processed.** And even with a path, the artifact
carries verbatim SGK text, so it lands in the gitignored `assets/fixtures/real/` tree (D4) and
distribution is the separate WAL-43 licence gate — both Founder decisions.

---

## 3 · Minimum missing capability

Stated as capabilities, smallest first. **Each is the least thing that would move the slice one
stage, not a programme.**

| # | missing capability | which blocker it removes | who can do it |
|---|---|---|---|
| **M1** | **A trust policy whose admissible set contains a complete question section.** Every frozen candidate refuses one, by clause. What does not exist is a policy shaped «a heading and its question, both character-exact, both correctly roled, neither figure-dependent, no member withheld» — a **unit-level** policy, where every clause today is block-level. | BLOCKER 1 | **an agent** — it is a candidate, hashed and frozen like C0–C4, and freezing a candidate activates nothing |
| **M2** | **One non-model reading of one slice.** Two blocks, one page, one person, ten minutes. Until it exists the word *certified* is unavailable for any content in this repository at any measurement. | BLOCKER 2 (half) | **a person.** Not the Founder necessarily — the protocol says «the Founder's / an independent reviewer's job» |
| **M3** | **A role signal that reaches 0.90 on a printed question.** Both surviving questions were labelled by `method: lexicon` at 0.78 and 0.85; the typography method reaches 0.88 on their headings. TC-19 #3 additionally requires QUESTION precision ≥ 0.95 (measured 0.903 at n = 72) and TC-19 #9 puts ≥ 300 gold questions in front of it. | BLOCKER 1 under C3 only | an agent, but **M1 is strictly cheaper and removes more** |
| **M4** | **A lesson boundary for one Ngữ văn lesson** — or, equivalently, a slice in a book that already has one. | BLOCKER 3 | an agent |
| **M5** | **An evidence row for the roles the truth layer does not model** (`instruction`, `table`, `figure_label`, `diagram`, `answer_slot`). They stop **50 of the 95** learning slices at SOURCE: their correctness is not unknown, it is unrepresentable. `instruction` is the block that tells the child what to do. | the largest single loss on the whole plane | an agent |
| **M6** | **Verbatim gold text for `tc_gold_bai17`.** Its 73 blocks carry anchors only, so on the only lesson-wide gold set this repository owns, RECOGNITION cannot be measured and the digit half of teaching-critical — **6 of the 7 remaining errors** — reads a silent zero. | not a slice blocker; a **measurement** blocker behind every future one | an agent |

---

## 4 · Evidence

| claim | evidence |
|---|---|
| the two units clear S1–S5 | `phase_f_slice_gate.py` over 58 pages; `summary.through_S5` and an independent recomputation from `units.jsonl` agree on the same two ids |
| every frozen candidate refuses them | `summary.through_S5_candidate_refusals`, per unit, per candidate, with the clause named |
| the refusal is not a threshold | `test_raising_role_confidence_does_not_rescue_it_under_C2` — 0.70 / 0.85 / 0.90 / 0.99, same verdict |
| the bar can pass something | `test_a_perfect_unit_qualifies` — a heading plus an activity prints `QUALIFIES_GATE_CLOSED`. **The zero is a fact about the corpus, not about the bar** |
| the bar rejects what it must | six guard provocations, all exit non-zero — including the bar mutated to pass everything, caught by G2 |
| the population is the one it cites | G4 refuses to run unless the 54-page plane rebuilds to `PHASE-B-QUESTION-VETO` §3.1's published arm: 356 / 23 / 8 / 6 / 2 |
| no lesson is fully covered by gold | 0 on the canonical spans and 0 on the most generous reading of every TSL in `poc-out`; 46 lessons touched, 18 partial, 27 with no declared span, **1 contested** |
| Ngữ văn has no delivery path | recursive scan of every `*.tsl.json` under `poc-out`: 13 books, Ngữ văn absent; `WorkspaceCatalog.defaultSlots` has two slots, neither of them |
| ground truth is model-produced | the `annotator` field on all 58 gold pages; `ROUND3-CONSOLIDATED-REPORT` §6 «single AI annotator» |

---

## 5 · Smallest next implementation required

> **ONE candidate trust policy, unit-level, frozen and evaluated — not activated.**

Concretely: add a candidate beside C0–C4 in the frozen payload whose clauses apply to a **complete
unit** rather than to a block —

```
served_only ∧ no_repair ∧ two_stack_exact ∧ order_ok ∧ no_figure_dependence
∧ unit_complete        (no member unmatched, no member withheld, no member without gold text)
∧ unit_one_to_one      (no two members on one pipeline block)
∧ unit_role_exact      (every member's coarse role correct against a role the layer can defend)
```

— hash it, freeze it, and re-run `phase_f_slice_gate.py` against it. **That is one file, one
candidate, and one re-run.** It cannot activate anything: `policy.admits()` returns a refusal list
and has no code path that writes, and `apply.py` is inert without a Founder approval artefact.

It answers the one question this phase could not: *is there a trust policy under which this
repository's best content is admissible at all, or is the answer no for every shape?* Today the
answer is unknown, because every candidate ever written refuses a question by clause and no
candidate has ever been written for a unit.

**Two things it must carry, or it is worth nothing:**

1. **A bound, declared before the evaluation**, exactly as round 7 declared BOUND-2 — and a
   prediction of the outcome recorded inside the frozen payload.
2. **The statement that admitting a unit is not certifying it.** M2 remains outstanding
   regardless: a policy is a rule about model output, and the second annotator the protocol
   requires is a person.

### What must not happen next

- **No Round 8 of research.** The order forbids it and the evidence does not need it.
- **No threshold activation**, no ratification of D-135…D-138, no licensing decision, no device.
- **No new slice hunt.** The slice is found, named, and measured to the block. What is missing is a
  policy that can admit it and a person who can vouch for it.

---

`trusted = 0` · `eligible for teaching = 0` · **no threshold activated** · **no device** ·
**WHAT CAN A CHILD USE NOW THAT THEY COULD NOT BEFORE? NOTHING.**
