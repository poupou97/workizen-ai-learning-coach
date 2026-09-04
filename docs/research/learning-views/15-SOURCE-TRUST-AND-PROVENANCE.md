# 15 — Source Trust and Provenance across Views (§12)

> **Reconciled with TC-v1 (2026-09-05).** `TC-nn` = `docs/research/trusted-corpus/nn-….md`. Changes: §1 OCR row; §2 mapped onto SDM trust (T1 split into text vs role); §3 new rows; §4 fourth break; §6 fourth test; §7 applied.

**Trust rule (Founder):** prettier Views must not weaken source trust. TRACE ≠ EVIDENCE ·
RETRIEVED ≠ PERMITTED · BROWSABLE ≠ LEARNABLE · OCR TEXT ≠ TRUSTED SOURCE. Uncertain structured
source ⇒ FAIL CLOSED or show uncertainty/source fallback. Trust > visual richness.

Corpus-dependent rows were PENDING TRUSTED-CORPUS FINDINGS at writing; reconciled below.

## 1. The four inequalities, where each is enforced today, and what each View adds

| Inequality | Enforced today (OBSERVED-IN-CODE) | What Views must add |
|---|---|---|
| **TRACE ≠ EVIDENCE** | `validateCandidateEvidence` returns `null` on `lookup`; Reader's READ gate emits nothing; Convergence §1 defines TRACE | Mode 1 and Mode 2 display emit TRACE only; a View switch never mints; markers shown in Mode 1/2 come from evidence but never create it |
| **RETRIEVED ≠ PERMITTED** | `TutorScope = APPLICABLE ∩ ALLOWED`; pedagogical filter proven load-bearing (WAL-81: leak 5 → 0); `explainTeaching` fails closed | Mode 3 realisations use only the lesson document's `DerivedFacts`; Mode 2 renders only typed data from *this* lesson (no cross-lesson relations unless `citableAsDependency`) |
| **BROWSABLE ≠ LEARNABLE** | C-013: Browsable 843→3,679, Learnable +0; lesson row says «chưa có việc» | a lesson with a document but no activity shows Mode 1 (and Mode 2 if typed data) but Mode 3 says «SAM chưa dạy được bài này» — never a generated session |
| **OCR TEXT ≠ TRUSTED SOURCE** | `blocks[].trusted`, `layout.trusted`, Q1–Q8 gate, "no manual annotation, no LLM generation anywhere in the chain" (WAL-206). **TC-v1:** that trust is page/region-gated — it withholds 76 % of blocks on hard pages and 12 % of what it keeps is wrong (TC-08 §1); block-level trust is the agreement cascade + deterministic guards of TC-10 (not built) | Mode 1 renders non-TRUSTED blocks as page-region images; Mode 2 refuses untrusted nodes; Mode 3 never quotes an untrusted block; **no View treats a `question` label as a question until the role layer measures ≥ 0.95** (TC-07) |

## 2. Trust levels a View may act on (proposed vocabulary, HYPOTHESIS — mapped onto the SDM)

| Level | Meaning | Source of the flag | SDM equivalent (TC-11) | Mode 1 | Mode 2 | Mode 3 |
|---|---|---|---|---|---|---|
| **T0 page image** | the scan itself | raster | `Page.render sha256` + `layout_features[]` | show (anchor; delivery path for math/diagram/table, TC-19 #7) | «xem vùng trang» | «xem lại trong sách» |
| **T1 trusted block (text)** | text + order agreed by two independent analyses, no guard fired | TC-10 cascade. *Today's* WAL-206 flag is **T1-legacy**: page-gated, FTR 0.119 on hard pages (TC-08 §1) — not T1 | `trust.status = TRUSTED` | render as text with provenance | eligible as node/label | quotable; `DerivedFacts` |
| **T1r trusted role** *(new after TC-v1)* | a T1 block whose role passed the role layer (question precision ≥ 0.95 measured on gold) | role layer — unbuilt (TC-07) | `role` + role confidence, no `role_conflict` | question affordance / inline check allowed | typed relations (`options_of`, `answer_of`) | may become a prompt |
| **T2 withheld / conflict** | disagreement, a guard fired (math, box-boundary, empty-block, figure-dependence, answer-leak, page-feature), or role conflict | TC-10 gates | `trust.status ∈ {WITHHELD, CONFLICT}` + `reasons[]` | image region + reason-coded label «SAM chưa đọc chắc» | not eligible | not quotable |
| **T3 typed datum** | extracted deterministically with `sourceRef`, gold-validated | extractor + gold set (e.g. `tienHanh[]`) | SDM relations (`caption_of`, `options_of`, `refers_figure`, `continues`) + `Figure`/`Table` objects | — | render | scope/facts |
| **T4 curated** | human-verified (`SourceAsset`, VERIFIED stories, `samGloss`) | curation | (outside the SDM; review-queue output can feed it, TC-10) | render with label | render | quotable with its own label («SAM diễn giải») |
| **T5 keyed** | SGV answer key linked deterministically | WAL-192 pattern → TC-14: `answer_of` by printed enumerator / table cell, enumerator present on both sides, answer-leak guard | `relations.answer_of` | inline check may grade | interaction may grade | `feedbackFor` may say đúng/sai |
| **X inferred** | `llmInferred`/`systemDerived` relations, generated summaries | — | forbidden as block content (TC-11 §6) | never as book text | never as node | only as «cách của SAM» with the fallback wording |

Rule of thumb for the child-facing line: **only T1/T3/T4/T5 content may carry «Theo SGK …, trang N»**;
T2/X carry «SAM chưa chắc…» or «Đây là cách của SAM…» (`sourceLineForChildOf`, the only wording function).
A T1 block without T1r may be *read* under «Theo SGK» but never *asked*.

## 3. Fail-closed matrix (what happens when something is missing)

| Missing | Mode 1 | Mode 2 | Mode 3 |
|---|---|---|---|
| lesson boundary (`pageStart null` / no header, TC-14 §2) | show book TOC; «SAM chưa tìm được trang bài này» | absent | absent |
| all blocks untrusted | page images only | absent | Surface-level only if an activity exists |
| block WITHHELD / CONFLICT (TC-10) | image region + reason-coded label | not eligible | not quotable |
| role conflict (QUESTION vs verifier HEADING, TC-10) | render as body text, no affordance | — | not a prompt |
| page carries formula / diagram / map / timeline / colour-heavy feature (page-feature guard, TC-18 Q16) | page image + FIGURE blocks only | tab absent unless a typed shape exists | «xem lại trong sách» |
| table on the Mac path (TC-07) | image region «Bảng trong sách» | absent | not quotable |
| typed data | — | tab absent (no empty canvas) | — |
| activity | — | — | «SAM chưa dạy được bài này» |
| key | inline question ungraded (`correct=null`) | interaction ungraded | probe/short answer ungraded; SAM says so |
| enumerator missing on either side of an SGV pair (TC-14 §1) | — | — | pairing fails closed; no key |
| blueprint / binding | — | — | Surface policy (`reader-v1`, `experiment-v1`) |
| provenance on a datum | do not render | do not render | do not quote |
| licence for page images (OQ8) | fragments only + «xem sách giấy» | — | — |

## 4. Provenance chain and the four ways it breaks

`Book → Chapter → Lesson → Source Page → Block/BBox → Structured Content → Learning View`

1. **Silent conversion** (Markdown, reflow without trust marks): broken by the intermediate —
   rejected in `04`; TC-11 §6 says the same.
2. **Generated content with cosmetic anchors** (DeepTutor snippet anchors; OpenMAIC HTML): broken
   at "Structured Content" — rejected in `05`/`11`.
3. **Presentation that outruns confidence** (large headings from low-`ocrConf` blocks; a clean
   diagram from a partially trusted page): the SAM-specific risk (WAL-193 class — legibility gate
   gap). Mitigations: (a) headings below an `ocrConf` threshold render from the page region, not
   text; (b) Mode 2 shows a per-diagram trust footer («Sơ đồ dựng từ 4 bước in ở trang 5»);
   (c) device walk before any ship.
4. **Silent agreement on a shared error** (TC-17 "single biggest residual risk"): two stacks
   flatten the same fraction or merge the same adjacent boxes, the gate says TRUSTED, and a View
   shows "200 300" as book text. Invisible to every View by construction; bounded only by
   deterministic guards (math, box-boundary, empty-block), structurally different verification
   for math/boxes (image-first or human), and continuous false-trust audit on shipped lessons
   (TC-17, TC-18 Q21–22).

## 5. What each View may *say* (voice rules, reusing existing guards)

- The book's words and SAM's words stay typographically separate in all Views (Convergence §2 item 7;
  `SourceReader` three-claim precedent).
- No View shows percentages, scores, or "understood" claims to the child; markers are evidence-
  backed states (`learningMapStateFor`), phrased per `DESIGN-SYSTEM-DIRECTION.md` §3.
- SAM praise only on evidence events; "🎉" is not a Mode 3 default.
- Any LLM wording passes `validateRealization`/`validateTutorOutput` (citation fabrication,
  future-knowledge, method-permission guards) — unchanged.

## 6. "Trust > visual richness" — four tests a design must pass before it ships

1. **Can the child get to the page?** From any block, node, or SAM line, one tap reaches the source
   page region (T0).
2. **Can the praise/claim be wrong?** Every «đúng rồi», every marker, every «theo sách» traces to a
   T5 key, an evidence event, or a T1/T3/T4 datum.
3. **Does uncertainty look uncertain?** An untrusted region must be visibly different (image, label,
   `admit-uncertainty` chip) — a design that makes T2 look like T1 fails.
4. **Can a shared error reach the child as text?** Formula, table and diagram content must be image
   regions regardless of trust status — the one class agreement cannot certify (TC-08 §4).

## 7. Reconciliation checklist — APPLIED 2026-09-05

- [x] T0–T5 mapped onto SDM `trust.status` / `reasons[]` / relations; T1 split into T1 (text) and T1r (role) per TC-07 / TC-10; today's flag named T1-legacy.
- [x] §3 rows added for WITHHELD/CONFLICT blocks, role conflict, page-feature guard, tables on the Mac path, SGV enumerator pairing.
- [ ] Per-subject "Mode 1 allowed / page-only" list: TC-v1 gives it **per layout feature** (`18` §4 answer 7) and per subject only as fully-sourceable counts (Toán 4/554, KHTN 4/145, Vật lí 1/82 — TC-18 Q17). Per-subject fidelity STILL UNMEASURED after TC-v1 (≥ 20-page per-family gold would close it, TC-19 #9).
- [ ] Page-image licensing (OQ8): not measured, not decided by TC-v1 — Founder/Legal.
