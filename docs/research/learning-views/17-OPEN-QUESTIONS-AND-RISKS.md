# 17 — Open Questions and Risks

> **Reconciled with TC-v1 (2026-09-05).** `TC-nn` = `docs/research/trusted-corpus/nn-….md` (WAL-208). Changes: OQ1 closed (partly), OQ2/OQ5/OQ8 updated, OQ11 added; §2 items annotated; R5 resolved, R11–R12 added; **new §5 "Conflicts between WAL-207 and WAL-208"**.

## 1. Open questions (numbered; owner; how to close)

| # | Question | Owner | How it closes |
|---|---|---|---|
| OQ1 | Can figure/table/formula regions be derived deterministically from scanned pages, or does Mode 1 stay "text fragments + page image" for the long term? | Trusted Corpus track | **CLOSED (partly) by TC-v1.** Figures: yes, as image regions with captions (SDM `Figure`, `caption_of` 0.90–0.95 — TC-07, TC-11); tables: yes as objects **only on the GPU path** (Marker 1.00/1.00; Docling flattens cells — TC-07, TC-14); formulas: **no** — flattened by every stack, image-first (TC-09, TC-19 #7). Mode 1 stays "fragments + page image" for formula / diagram / table / elementary pages until a formula-capable path is measured on gold (TC-18 "UNCERTAIN" sub-question). Figure bbox precision STILL UNMEASURED. |
| OQ2 | Is a per-lesson document worth building before lesson boundaries are reliable (8/30 Khoa học 5 lessons lack `pageStart`; KHTN 7/8 TOC truncated)? | Founder + Trusted Corpus track | **TC-v1:** 3,381 of 3,679 lessons ranged (TC-03 §5); TOC-range attachment wrong on 10/38 hard pages, header-based fixes 6 (TC-02 §5, TC-14 §2); 25.8 % of pages continue across pages (TC-03 §2). Answer from the evidence: build the document *as a projection of block-level attachment* (`12` §3) — it is the thing that makes boundaries reliable, not something that waits for them. Sequencing is the Founder's (TC-19 #5 before #1). |
| OQ3 | Do children switch Views at all, or follow SAM's proposal? (same shape as Convergence U1 for intents) | Product | 2-week usage measurement on the 4–5 cohort; if >85% follow, collapse to proposal + «đổi cách khác» |
| OQ4 | Does a View recommendation change learning outcomes, or only navigation? | Product / learning science | no evidence either way; test after OQ3 |
| OQ5 | Which typed relationship can be extracted next with provenance — glossary terms (`Concept{term, definition}`) or numbered steps outside experiments? | Corpus | one bounded extractor + gold set, stories-pipeline style. **TC-v1:** numbered steps need the enumerator-preservation guard first (Docling drops 65 — TC-09, TC-19 #4); the typography signal for glossary terms is STILL UNMEASURED (`05` §4). |
| OQ6 | Should the two evidence-minting patterns (validator vs direct mint) converge before Views multiply the Surfaces? (Review §3 open hypothesis #3) | Architecture | decision, not research |
| OQ7 | Is a step-ordering interaction on a Process view the first *deterministically gradable* non-Toán activity? | Pedagogy | falsification slice on one KHTN 6 lesson |
| OQ8 | Page-image licensing: is showing SGK page rasters to end users allowed under `ContentLicense.localResearchOnly`? (`knowledge_content_provider.dart:15-28`) | Founder / Legal Gate | the existing legal seam decides; Mode 1's anchor depends on it. **TC-v1 assumes an answer it does not give:** it recommends image-first delivery of page crops (TC-19 #7) and records governance as unchanged (TC-17 #15). See §5 C6. |
| OQ9 | Should "Đọc" become a fourth first-class intent or remain `lookup` shown as a book? | Founder | this package recommends *remain `lookup`* to avoid re-introducing LEARNING MODE |
| OQ10 | Does the Home card fix (read Scale path) belong with this concept or with the existing Track C defect list? | PM | already logged in WAL-206 §5; independent of Views |
| OQ11 *(new)* | Which release bar applies to a Learning View, given the Founder targets (text ≥ 99.5 %, FTR < 0.1 %, 0 critical errors) were measured at 95–96 % / 6.5–12 % / 21 events on hard pages and 0 % FTR on plain prose (TC-08 §5), and 38 pages cannot certify < 1 % (TC-17 #2)? | Founder | decision: per-feature gates (prose/questions/sidebars now; math/diagram never as text) + statistical audit on shipped lessons (TC-18 Q21–22), or one corpus-wide bar. |

## 2. What the concept board assumes that the evidence does not yet support

(Board: `concept/concept-ai-first/learning-view.png`. Each item is MEASURED or OBSERVED-IN-CODE
unless marked.)

1. **The lesson exists.** "Khoa học 5 Bài 2 — Dinh dưỡng và sức khỏe" is not in the corpus; Khoa
   học 5 Bài 2 is "Ô nhiễm, xói mòn đất và bảo vệ" (`pageStart: null`). Nearest: Khoa học 4 Bài 23.
2. **Structured Book blocks Image · Table · Formula · Activity exist.** No extractor produces
   them; `layout.tableLike ⇒ untrusted`; figures exist only as 3 human-curated crops. TC-v1: Figure
   feasible as an image region; Table GPU-only; Formula never as text (TC-07, TC-11).
3. **The nutrition lesson can be read natively.** Khoa học 4 pp.84–93: 8/10 pages untrusted, 0
   units for lesson 23; OCR headings misspelled. TC-v1: on the 150-page pilot the XY-cut trusts
   50/150 pages; Docling ▸ XY-cut keeps 84.7 % of blocks (TC-13).
4. **Frame 4's "Em có biết?" box and "Bảng 2.1" render as native blocks.** Side boxes are
   `sidebar` blocks (available when trusted; label precision 0.45 — TC-07); tables are fail-closed
   image regions on the Mac path.
5. **Frame 5's mindmap ("Chất dinh dưỡng → 4 groups") comes from data.** No `ConceptRelation[]`
   exists; producing it today would require LLM inference (forbidden by §12) or hand authoring.
6. **Frame 6's "Chính xác! 🎉".** No SGV key ⇒ `correct: null`; keyed lessons: 309 by registry
   (a marker count), 2 with a proven SGK↔SGV linkage (Tin học). TC-14: pairing must move to
   `answer_of` relations; Docling's enumerator dropping (65 gold blocks) breaks it.
7. **"SAM đề xuất … ~5 phút / ~12 phút".** No duration data exists; a reason exists only when
   `proposeIntent`/`LearningAgenda` has a signal.
8. **"Đã học 3/18 bài · 17%".** Percentages for the child are on the never-build list
   (Convergence §23 item 1).
9. **Five bottom tabs incl. "Học cùng SAM" and "Tiến bộ".** Converged IA is three tabs; a SAM tab
   "advertises chat as the main activity".
10. **"Không cần mang cả PDF, tải theo sách/bài" reduces size materially.** Text does (≈10× per
    book); figure crops (0.5–4 MB each) and page rasters (≈ 330 KB per 200-dpi page, TC-16) do not —
    the saving depends on an image policy that does not exist yet (`18` Q17–18).
11. **Three Views are selectable "on entering the lesson" independent of intent.** The converged
    model binds intent first; Views inside LearningContext.
12. **A "Bảng tóm tắt / Ghi nhớ cùng SAM" summary is available.** Only if it is verbatim
    objective/glossary text with provenance; generated summaries violate OCR TEXT ≠ TRUSTED SOURCE.

## 3. Risks

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | **Prettier Views weaken trust** — a reflowed Mode 1 or a clean Mode 2 makes OCR errors and inferred structure look authoritative (§12) | High — MEASURED: 12 % of XY-cut-trusted blocks are wrong on hard pages (TC-08 §1) | Child learns a wrong fact "from the book" | per-block trust + page-image anchor; fail-closed rendering (`15`) |
| R2 | **LEARNING MODE re-enters the vocabulary** through "3 cách học" | Medium | implementation diverges into 2–3 readings (the exact failure Convergence #2 fixed) | define Views inside LearningContext (`03` §3); never call them modes in code |
| R3 | **A parallel resolver / generic renderer is built** for Mode 2 | Medium | two mapping points semantics→widget (ADR-009 warning) | extend `_activityAction`/`resolveSurface` seam; no layout engine before three shapes |
| R4 | **Deep/Scale unification by decree** via the lesson document | Medium | breaks the 113 Learnable lessons or freezes the 1-lesson Deep path | SemanticBinding stays optional/additive (WAL-200 fail-closed guarantee) |
| R5 | **Corpus findings contradict the block model** | **RESOLVED 2026-09-05** — TC-v1 superseded rather than contradicted it | `12`/`13`/`15` rewritten onto the SDM (TC-11) | applied; remaining disagreements listed in §5 |
| R6 | **Recommendation without reason** ("SAM đề xuất" shown always) | Medium | violates Convergence §23 item 12; trains children to ignore SAM | render the row only on a signal |
| R7 | **Legibility gate gap** (WAL-193 class): true content, illegible presentation (e.g. OCR heading "SỨC KHOE" rendered large) | High for Mode 1 — tone slips on decorative fonts are an OCR ceiling (TC-17 #11) | child sees gibberish "from the book" | heading confidence rule; device walk before any ship |
| R8 | **Licence** — page images to end users under `localResearchOnly` | Unknown | legal | OQ8 through the existing seam |
| R9 | **Scope creep to "three screens"** | Medium | anti-principle #5 | one segmented control on one screen; reuse Surfaces |
| R10 | **Concept drift between Mode 3 realisations and Mode 1 text** if Mode 3 uses retrieval outside the lesson document | Low with current guard | "different truths" (§2) | `validateRealization` facts must come from the same document; build-time diff |
| R11 *(new, TC-17)* | **Silent agreement on a shared error** — two stacks flatten the same fraction or merge the same boxes → TRUSTED wrong text rendered as book text | High on math/box pages (≈ 5 % residual in the best cascade, TC-08 §3) | child learns "200 300" from the book | formula/table/diagram always image regions; deterministic guards; continuous false-trust audit on shipped lessons |
| R12 *(new)* | **Prototype fragments from the XY-cut reach a child** | Medium | FTR 0.119 on hard pages (TC-08 §1) | measurement-only until the TC pipeline exists (`04` §4 item 6) |

## 4. Not risks (checked and dismissed)

- "Evidence cannot cross Views" — evidence is keyed by SkillCase/lesson, not by Surface (`03` F6).
- "Views need a graph database" — no; rejected already (Proposal §3).
- "Views need an LLM online" — no; every View here is deterministic except guarded wording in Mode 3 (shadow today).

## 5. Conflicts between WAL-207 (this package) and WAL-208 (TC-v1) — added 2026-09-05

Where the two studies disagree, neither number was averaged; each row says which wins and why,
or who must decide.

| # | Where they disagree | WAL-207 says | WAL-208 (TC-v1) says | Proposed resolution | Who decides |
|---|---|---|---|---|---|
| C1 | **Lesson denominator** | 3,679 canonical SGK lessons (`02`, `04`, `05`, `07`, `15`); `pageStart` missing on 2,033/7,626 `LessonKey` records (`12` §2); WAL-206 used 3,357 | 3,381 lessons *with a page range* of 3,679 (TC-03 §5); sourceability shares (555 = 16 %) use 3,381; TC-18 Q17 writes "≈ 555–603 lessons (15–16 %)" without fixing one denominator | Report both, never mix: "3,679 canonical / 3,381 rangeable". Sourceability shares over 3,381; product counts over 3,679. Re-derive once header-based attachment exists (TC-19 #5) — the 298 unranged lessons may gain ranges. | Measurable (re-run the census after TC-19 #5); Founder confirms which number the product thesis quotes. |
| C2 | **Role-layer precision** | Heading "0.90 role accuracy", Question "AVAILABLE with Q1–Q8 gate" (`04` §2, from the WAL-206 9-page gold) | Heading 0.81 / 0.51, Question 0.69 / 0.79, Sidebar 0.45 / 0.43 on 38 hard pages (TC-07); no parser has a QUESTION concept | TC-07 wins (larger, harder gold; the 9 WAL-206 pages are re-annotated inside it — TC-04). WAL-207 claims marked superseded (`18` §5). | Measurable — re-measure when the role layer exists (target ≥ 0.95). |
| C3 | **Trust unit** | per-block `trusted` exists (`04` §1, `12` §2, `15` §2 T1) | `trusted` is set by page/region geometry — a marginal cut loses the whole page (TC-02 §3); block-level trust = cascade agreement + guards (TC-10, not built) | Rename today's flag **T1-legacy**; T1 = SDM `trust.status = TRUSTED`. No Learning View ships on T1-legacy. | Measurable (run the cascade on the 6 WAL-206 books); no Founder decision needed. |
| C4 | **Lesson boundary method** | TOC page range + 2.5× cap + `boundary{confidence, status}` on the lesson (`12` §2) | header-based attachment per block (`heading_path`, `continues`, "no lesson", TOC repair) — 10/38 wrong by range, 6 fixed by headers (TC-02 §5, TC-14 §2, TC-19 #5) | Adopt TC's: attachment is a per-block fact with `attach_method`; the lesson's page range is *derived*. `12` §3 rewritten accordingly. | Measurable (cross-page gold, TC-19 #9). |
| C5 | **Source for a first Mode 1** | "Trusted Fragments" on the six device-valid KHTN 6 lessons from today's XY-cut output (`04` §2, `18` §6) | current pipelines are "not safe enough" (TC-18 Q1); "stop improving the XY-cut for coverage" (TC-19); reprocess only in gated slices (TC-12) | XY-cut fragments = measurement prototype only; production Mode 1 reads `TrustedLearningSource`. Sequence: TC-19 #1–#5, Science slice (KHTN 6 is inside it), then the `18` §6 measurement on both sources. | Founder (accept that Mode 1 waits for the source layer, or accept a prototype behind a research flag). |
| C6 | **Page images to learners** | undecided licence under `ContentLicense.localResearchOnly` (OQ8) | recommends image-first delivery of page crops with provenance (TC-10, TC-19 #7); governance "unchanged", crops only in bundles (TC-17 #15) | TC-v1 *assumes* what WAL-207 *asks*. Both tracks' Mode 1 anchor and TC's math/visual path are contingent on OQ8. | Founder / Legal gate. |
| C7 | **Reading-order number** | "0.99 on gold set" (`03` F2, WAL-206 gold) | XY-cut 0.976 with 34 meaning-changing inversions on hard pages; Docling 0.987, Marker 0.991 (TC-05, TC-06) | TC wins; WAL-207 figure superseded. | Measurable (done). |
| C8 | **Question / pattern counts** | "+76 lessons" for Short-Answer, "166/185 Science lessons EXPLAIN/OBSERVE" (`06`, `18`), registry counts in `05` §2 and `14` | directive units 49 → 199 on identical pages; 23/100 XY-cut "questions" are non-questions; counts are extractor artefacts (TC-15, TC-17 #13) | Keep the counts as *rankings* from the old extractor; recompute on a role-labelled SDM before any is a target. | Measurable (TC-19 #10). |
| C9 | **SGV keys** | "309 lessons keyed by registry; 2 proven linkages" (`06` §3, `13`) | pairing must move to `answer_of` by printed enumerator + table cells; Docling drops enumerators on 65 blocks; upper bound unmeasured (TC-14) | 309 = marker count, not pairing count — say so wherever quoted. SGV format census (1 day, TC-14) closes the bound. | Measurable. |
| C10 | **Confidence vocabulary and bbox** | three confidence numbers; two bbox conventions (`12` §2) | tri-state `trust{status, reasons[]}` + role confidence + `ocr_conf`; bbox `[x, y, w, h]` normalised (TC-11 §2) | Adopt SDM; convert `SourceAsset.bboxFrac` once. | Mechanical; no decision. |
| C11 | **Product thesis wording** | "ONE TRUSTED LESSON → three Views" | "a growing trusted subset, never a silently corrupted whole"; "3,679 lessons from the books" is not the product (TC-18 verdict); SDM-as-source, block trust, image-first, trusted-subset are ecosystem decisions to file as PROPOSED (TC-19 #11) | Read "One Trusted Lesson" as *the TRUSTED-block subset of a lesson, with page images for the rest*. Neither study may decide this. | Founder — record per `canonical/KNOWLEDGE_UPDATE_PROTOCOL.md`. |
| C12 | **Release bar** | inherits the Founder targets implicitly (fail-closed) | targets (text ≥ 99.5 %, FTR < 0.1 %, 0 critical) not reached on hard pages; reached only on plain prose (TC-08 §5); 38 pages cannot certify < 1 % (TC-17 #2) | Per-feature gates (prose/questions/sidebars now; math/diagram never as text) + statistical audit on shipped lessons (TC-18 Q21–22) instead of one corpus-wide bar. | Founder (OQ11). |

**Not conflicts (both studies agree):** Markdown must not be the truth (`04` §1 ↔ TC-11 §6);
no LLM composition of visuals or blocks (`05` §3 ↔ TC-11 §6, TC-10); no grading without a key
(`06` §3 ↔ TC-15 SELECT_MCQ "ungradable"); the concept-board lesson is outside the corpus; the
page image is always reachable (`04` §5 ↔ TC-19 #7); the 27 patterns are not to be implemented
from old counts (`14` ↔ TC-15).
