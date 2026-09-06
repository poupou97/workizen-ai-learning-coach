# ACCURACY RECOVERY — architecture audit (Lane A4, round 5, 2026-09-06)

**READY FOR FOUNDER REVIEW — nothing merged.** Base `integration/round5-2026-09-06` + Lane A1's
`a1/round5-repair-framework`. This document answers the Founder's ACCURACY RECOVERY addendum question by
question, **against the repo as it stands after A1 and Lane C landed**, and states the *minimum* to add.
Results and numbers are in `ACCURACY-RECOVERY-RESULT.md`; this is the audit that decided what to build.

Classification: **EXISTS AND USED** · **EXISTS BUT NOT WIRED** · **PARTIAL** · **RESEARCH ONLY** · **MISSING**.

---

## The chain the Founder asked for

```
SOURCE → OCR/parser observations → deterministic validation → specialised domain validation
       → cross-corpus consistency → LLM semantic review → external authoritative verification
       → human correction → validated correction → versioned Trusted Corpus
```

with a **router** choosing which links a given block traverses. Audited link by link below.

---

## 1 · Multi-path DETECT → VERIFY → REPAIR → RESTORE — **EXISTS AND USED** (A1 owns it)

`tool/corpus/repair/{engine,registry,model,ledger}.py`. The engine runs registered repairers, collects
`RepairCandidate`s, submits each to registered validators (unanimity among non-abstainers; `insufficient`
is never a soft yes), and writes an append-only ledger. `Observation` is a frozen dataclass with a
`_FrozenDict` provenance, so *«never overwrite a source observation»* is enforced by the type system
rather than by prose.

**What A4 added:** nothing structural. Four new signal families registered into that registry
(`crosscorpus`, `enumerator`, `furniture`, `llm`, `external`) plus two token/block providers. A4 wrote no
engine, no ledger and no second registry — that was the standing order and it held.

**Minimum still to add:** nothing.

---

## 2 · Cross-corpus consistency — was **MISSING**, now **RESEARCH ONLY (measured)**

**Before:** nothing read the corpus as a corpus. Lane C had a *narrow* form — `lanec.tone-majority-v1`,
book-scoped, token-level, tone-marks-only — measured at precision 0.889 / recall 0.533 /
**false-correction 0.111**, whose single false correction rewrote a person's name.

**Now:** `tool/corpus/verify/index.py` + `crosscorpus.py`. A read-only index over **62,729 OCR pages /
531 books / 94,787 distinct surface forms**, with a diacritic-variant map and a corpus-measured
**proper-noun prior**; plus a query-driven context scan that returns exact n-gram counts *and real
occurrences* as evidence.

Three things the audit forced, each from a measured failure rather than from taste:

| finding | consequence |
|---|---|
| the corpus writes `đầu` 30,232× and `đấu` 5,627×, so a **token-frequency** majority rewrites the correct «cuộc đấu tranh» | the unit of evidence is the **n-gram in its context**, never the syllable. Three of the six POC cases are invisible to unigram frequency. |
| treating a punctuation-separated pair as context read «đồi mồi,...), phải» as the bigram `mồi phải` | evidence is never read across a comma; and the corpus index counts bigrams **across line breaks**, because a block's text joins lines |
| «đã phất cờ» and «về hưởng ứng» are rare *left* bigrams and very common *right* ones | **contradicting evidence vetoes**: if any context of the observed token is well attested, the text is a phrase the corpus knows |

Those three changes together cut clean-text proposals from 18 to 6 per 480 rows and the injected
false-correction rate from 0.109 to 0.063.

**Minimum still to add:** a persistent bigram index over the ambiguous-key subset (the current context
scan is one corpus pass per batch, ~2 min — fine for research, not for a pipeline stage).

---

## 3 · LLM as a verifier — was **MISSING**, now **RESEARCH ONLY (measured, and the verdict is split)**

**Before:** an offline harness pattern existed and was proven (`tool/shadow/run_shadow.py` calls
`claude -p … --output-format json`; `eval_shadow.py`, `guard_check.dart`), and the app had no network and
no LLM. Nothing pointed a model at the corpus.

**Now:** `tool/corpus/verify/llm.py`. Same harness pattern, disk cache keyed by prompt hash, `--offline`
re-scoring. Every field the Founder listed is stored — original observation · proposed correction · reason
· **context supplied verbatim** · model and prompt version · confidence · supporting **and contradicting**
evidence (the prompt asks for the case *against* explicitly, because a model never volunteers it).

`llm_validator` returns `insufficient` for any candidate whose only support is layer `G`. That is the line
of code that makes «LLM OUTPUT ≠ TRUTH» true rather than stated.

**The measured verdict, and it is not one number:**

| | detector | proposer |
|---|---|---|
| injection holdout (n=60) | recall **0.717** — the best of any signal | precision 0.822 / FCR 0.178 |
| Lane C Bài 8 (n=51, human print truth) | recall 0.400 | precision 0.556 / **FCR 0.444** |
| **60 rows that were already correct** | flagged **26.7 %** of them | 13 proposals, **every one wrong (FCR 1.000)** |

**Minimum still to add:** nothing more, and something less — the router must consult it as a *detector*
only, which is how it is wired.

---

## 4 · External authoritative verification — was **MISSING**, now **RESEARCH ONLY (by design)**

**Now:** `tool/corpus/verify/external.py`. An evidence store whose schema cannot be skipped —
`EvidenceRef(kind='external_page', …)` **raises** without a URL and a retrieval timestamp — plus
`appropriate(kind)`, the routing rule for when reaching outside is defensible at all. There is no
`apply()` in the module and no network client: rows are recorded by a bounded lookup, never fetched by the
pipeline.

The audit's substantive finding is *when it is a trap*: the truth a Trusted Corpus needs is **what the
printed page says**, and no external source knows that. External verification can establish that
`3×10° m/s` is not a physical constant; it cannot establish that page 41 prints «Bạch Đằng». So
`H.external` is a signal about *plausibility in the world*, never about *fidelity to the source* — which
is exactly why the Founder ranked it below cross-corpus, and why the router's external consult rate on
1,200 real blocks is **0.000**.

**Minimum still to add:** a Founder decision on whether any bounded lookup budget is worth spending at
all, given that measurement.

---

## 5 · Human correction workflow — was **MISSING**, now **RESEARCH ONLY (schema + triage, no UI)**

**Now:** `tool/corpus/verify/human.py`. `CorrectionRecord` carries every field the Founder listed
(`sourceBlockId` — byte-identical to the SDM/TSL id, which A1 verified at 0 mismatches — original,
proposed, reason, reporter type, source evidence, timestamp, validation result, reviewer, corpus version,
`prior_record_id`). `triage()` is a pure function, so the policy can be argued with and tested.

The one substantive design claim: **a report without a reading of the printed page is a DETECTION, not a
correction.** `CAN_ESTABLISH` says what each reporter type can establish on its own; a learner report is
full-value detection and zero-value proposal. That is the same split the LLM turned out to have, for the
same reason, and it is why `triage()` returns `NEEDS_SOURCE` rather than `ACCEPTED` for it.

UX research note (`human.UX_NOTE`): «Báo nội dung sai» is one tap on a *block*; steps 2–4 (span, proposal,
photo) are optional; the app says «SAM sẽ kiểm tra lại với sách in» and **never «đã sửa»**; accepted
corrections are attributed to the print, never to the reporter; reports are deduplicated, **never counted
as votes** — frequency is not truth here either.

**Minimum still to add:** a production UI, which this round deliberately does not ship, and a review
capacity commitment — a queue nobody reads is worse than no queue.

---

## 6 · Trust / provenance evidence model — was **PARTIAL**, now **EXISTS AND USED**

**Before A1's second delivery:** the SDM block already carried `text` **and** `text_docling` (both stacks),
`agreement`, `guards`, `trust{status,reasons}`, `ocr_conf`, `extraction`, `colour`, `bbox`, `role`,
`heading_path`, `lesson`; the TSL carried `provenance`, `reasons`, `status`. Missing were correction
candidates, contradicting evidence, and the richer disposition set.

**A1 closed most of it while this lane was auditing.** `repair/model.py` now has
`RepairCandidate.supporting()` / `.contradicting()` as first-class views, and `Disposition` now includes
**SUSPECT · HUMAN_VERIFIED · CONFLICT** plus `ALIASES = {RAW → ORIGINAL_OBSERVATION,
CORRECTION_PROPOSED → REPAIRED_CANDIDATE}`.

**So A4 deleted its own copy.** `verify/trust.py` no longer defines a disposition:
`verify.trust.Disposition **is** repair.model.Disposition`. Three things remain genuinely A4's, because
A1's model has no slot for them:

| type | why it cannot be expressed in A1's model |
|---|---|
| `AnomalySignal` | A1 learns of a failure only through a repairer — something that yields a `RepairCandidate`. A detector that says *«this is wrong and I do not know what it should be»* cannot speak, and that is the **majority output** of an LLM verifier and of cross-corpus on a proper noun. |
| `EvidenceRef` | `ValidationResult.evidence` is free-form dicts; external evidence has *required* fields, and «required» has to be enforced by a type or it will be skipped. |
| `TrustDecision` | a read projection joining observations + anomalies + candidates + validations + human records, with a derived disposition and an `explain()` a Founder can check by eye. |

**Minimum still to add:** nothing. A4's three types are ~250 lines and no second framework.

---

## 7 · The router — was **MISSING**, now **RESEARCH ONLY (measured)**

**Now:** `tool/corpus/verify/router.py`. `route()` is pure and free — deciding *whether* to spend must not
itself cost anything — and returns the ordered path, why each signal was chosen or skipped, and whether a
human is needed. `escalate_after()` makes the second decision, once the evidence is in.

Measured on **1,200 real SDM blocks** (`poc-out/round5/pipeline/tc2-p3/sdm`, with real roles, guards and
agreement):

| | rate |
|---|---|
| **human review rate** | **0.0900** |
| LLM consulted | 0.416 |
| cross-corpus consulted | 0.993 |
| external consulted | **0.000** |
| mean cost per block (arbitrary units, human = 500) | 58.6 |

Reported honestly: on the synthetic holdout the rate is **0.0000**, because those rows carry no role and
no guard — that number measures the *inputs*, not the router, which is why the SDM set is the denominator.

**Minimum still to add:** the structural-group input (OPTION ⊂ QUESTION) is wired as a parameter but the
group index comes from A1's `repair/groups.py`; joining them is a one-line change nobody has made yet.

---

## 8 · No naive trust ladder — **EXISTS AND USED**, and it earned its place twice

There is no rule anywhere in `verify/**` that says `LLM < Internet < Human`. Trust is computed from
**evidence quality · independence · domain · source authority · reproducibility · teaching risk**:

* every validator refuses to validate its own layer (`independent_support(exclude_layers=…)`);
* `TrustDecision.derive()` orders the rules so that **disagreement beats confidence** — two credible
  candidates proposing different values produce `CONFLICT`, never a winner;
* a human record is a source: `CorrectionRecord.as_signal()` returns `SUPPORTS` only when the reporter
  actually read the page, and `OBJECTS` (a detection) otherwise, and a page reading alone still returns
  `VALIDATING`, not `ACCEPTED`, because **humans are wrong too**;
* `HUMAN_VERIFIED` is **not** in `SERVABLE`. A4 did not widen A1's `{TRUSTED}`.

The evidence that this is not decoration: Lane C measured a human print read deciding **against** a
machine correction («Đăng Khoa» must not become «Đặng Khoa») and **for** the machine on the river name in
the same block. A ladder cannot express that; an evidence record can.

**Minimum still to add:** nothing.

---

## Corrections to the lane brief's own prior audit

| brief said | measured |
|---|---|
| trust/provenance «PARTIAL but strong… check whether A1's `repair/model.py` already adds these» | it does, and A4 accordingly deleted its duplicate `Disposition`. Only `AnomalySignal`, `EvidenceRef` and `TrustDecision` remained. |
| cross-corpus «MISSING» | true at brief time, but **Lane C had a narrow measured form** whose false correction on a proper noun is the single most useful input this lane received |
| — | **Signal F (a third OCR stack) is declined, not pending**: A1 measured that both stacks share Apple Vision and the local tesseract has no `vie` model. A4 did not re-open it. |

## What the audit changed about what got built

The audit is why this lane did **not** build: a second framework, a disposition set, an LLM rewrite path,
a network client, a production correction UI, or a third OCR stack. It is why it *did* build a
context-based cross-corpus signal rather than a frequency one, a proper-noun sub-class with its own
reported false-correction rate, and a router whose escalation rate is a number rather than a promise.
