# 15 — Source Trust and Provenance across Views (§12)

**Trust rule (Founder):** prettier Views must not weaken source trust. TRACE ≠ EVIDENCE ·
RETRIEVED ≠ PERMITTED · BROWSABLE ≠ LEARNABLE · OCR TEXT ≠ TRUSTED SOURCE. Uncertain structured
source ⇒ FAIL CLOSED or show uncertainty/source fallback. Trust > visual richness.

Corpus-dependent rows are PENDING TRUSTED-CORPUS FINDINGS (no bundle existed at writing).

## 1. The four inequalities, where each is enforced today, and what each View adds

| Inequality | Enforced today (OBSERVED-IN-CODE) | What Views must add |
|---|---|---|
| **TRACE ≠ EVIDENCE** | `validateCandidateEvidence` returns `null` on `lookup`; Reader's READ gate emits nothing; Convergence §1 defines TRACE | Mode 1 and Mode 2 display emit TRACE only; a View switch never mints; markers shown in Mode 1/2 come from evidence but never create it |
| **RETRIEVED ≠ PERMITTED** | `TutorScope = APPLICABLE ∩ ALLOWED`; pedagogical filter proven load-bearing (WAL-81: leak 5 → 0); `explainTeaching` fails closed | Mode 3 realisations use only the lesson document's `DerivedFacts`; Mode 2 renders only typed data from *this* lesson (no cross-lesson relations unless `citableAsDependency`) |
| **BROWSABLE ≠ LEARNABLE** | C-013: Browsable 843→3,679, Learnable +0; lesson row says «chưa có việc» | a lesson with a document but no activity shows Mode 1 (and Mode 2 if typed data) but Mode 3 says «SAM chưa dạy được bài này» — never a generated session |
| **OCR TEXT ≠ TRUSTED SOURCE** | `blocks[].trusted`, `layout.trusted`, Q1–Q8 gate, "no manual annotation, no LLM generation anywhere in the chain" (WAL-206) | Mode 1 renders untrusted blocks as page-region images; Mode 2 refuses untrusted nodes; Mode 3 never quotes an untrusted block |

## 2. Trust levels a View may act on (proposed vocabulary, HYPOTHESIS)

| Level | Meaning | Source of the flag | Mode 1 | Mode 2 | Mode 3 |
|---|---|---|---|---|---|
| **T0 page image** | the scan itself | raster | show (anchor) | «xem vùng trang» | «xem lại trong sách» |
| **T1 trusted block** | layout `trusted=true`, page `trusted=true`, passes gate | WAL-206 | render as text with provenance | eligible as node/label | quotable; `DerivedFacts` |
| **T2 untrusted block** | page/region untrusted, tableLike, marginal cut, overlap | WAL-206 | image region + label «SAM chưa đọc chắc» | not eligible | not quotable |
| **T3 typed datum** | extracted deterministically with `sourceRef`, gold-validated | extractor + gold set (e.g. `tienHanh[]`) | — | render | scope/facts |
| **T4 curated** | human-verified (`SourceAsset`, VERIFIED stories, `samGloss`) | curation | render with label | render | quotable with its own label («SAM diễn giải») |
| **T5 keyed** | SGV answer key linked deterministically | WAL-192 pattern | inline check may grade | interaction may grade | `feedbackFor` may say đúng/sai |
| **X inferred** | `llmInferred`/`systemDerived` relations, generated summaries | — | never as book text | never as node | only as «cách của SAM» with the fallback wording |

Rule of thumb for the child-facing line: **only T1/T3/T4/T5 content may carry «Theo SGK …, trang N»**;
T2/X carry «SAM chưa chắc…» or «Đây là cách của SAM…» (`sourceLineForChildOf`, the only wording function).

## 3. Fail-closed matrix (what happens when something is missing)

| Missing | Mode 1 | Mode 2 | Mode 3 |
|---|---|---|---|
| lesson boundary (`pageStart null`) | show book TOC; «SAM chưa tìm được trang bài này» | absent | absent |
| all blocks untrusted | page images only | absent | Surface-level only if an activity exists |
| typed data | — | tab absent (no empty canvas) | — |
| activity | — | — | «SAM chưa dạy được bài này» |
| key | inline question ungraded (`correct=null`) | interaction ungraded | probe/short answer ungraded; SAM says so |
| blueprint / binding | — | — | Surface policy (`reader-v1`, `experiment-v1`) |
| provenance on a datum | do not render | do not render | do not quote |
| licence for page images (OQ8) | fragments only + «xem sách giấy» | — | — |

## 4. Provenance chain and the three ways it breaks

`Book → Chapter → Lesson → Source Page → Block/BBox → Structured Content → Learning View`

1. **Silent conversion** (Markdown, reflow without trust marks): broken by the intermediate —
   rejected in `04`.
2. **Generated content with cosmetic anchors** (DeepTutor snippet anchors; OpenMAIC HTML): broken
   at "Structured Content" — rejected in `05`/`11`.
3. **Presentation that outruns confidence** (large headings from low-`ocrConf` blocks; a clean
   diagram from a partially trusted page): the SAM-specific risk (WAL-193 class — legibility gate
   gap). Mitigations: (a) headings below an `ocrConf` threshold render from the page region, not
   text; (b) Mode 2 shows a per-diagram trust footer («Sơ đồ dựng từ 4 bước in ở trang 5»);
   (c) device walk before any ship.

## 5. What each View may *say* (voice rules, reusing existing guards)

- The book's words and SAM's words stay typographically separate in all Views (Convergence §2 item 7;
  `SourceReader` three-claim precedent).
- No View shows percentages, scores, or "understood" claims to the child; markers are evidence-
  backed states (`learningMapStateFor`), phrased per `DESIGN-SYSTEM-DIRECTION.md` §3.
- SAM praise only on evidence events; "🎉" is not a Mode 3 default.
- Any LLM wording passes `validateRealization`/`validateTutorOutput` (citation fabrication,
  future-knowledge, method-permission guards) — unchanged.

## 6. "Trust > visual richness" — three tests a design must pass before it ships

1. **Can the child get to the page?** From any block, node, or SAM line, one tap reaches the source
   page region (T0).
2. **Can the praise/claim be wrong?** Every «đúng rồi», every marker, every «theo sách» traces to a
   T5 key, an evidence event, or a T1/T3/T4 datum.
3. **Does uncertainty look uncertain?** An untrusted region must be visibly different (image, label,
   `admit-uncertainty` chip) — a design that makes T2 look like T1 fails.

## 7. Reconciliation checklist — when the Trusted Corpus bundle lands

- [ ] Map the study's trust/confidence vocabulary onto T0–T5 (or replace T0–T5 with it).
- [ ] Update §3 rows for tables/figures/formulas per the study's verdicts.
- [ ] If the study defines per-subject fidelity, add a per-subject "Mode 1 allowed / page-only" list.
- [ ] Confirm the page-image licensing position (OQ8) — it changes T0's availability.
