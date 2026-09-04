# 17 — Open Questions and Risks

## 1. Open questions (numbered; owner; how to close)

| # | Question | Owner | How it closes |
|---|---|---|---|
| OQ1 | Can figure/table/formula regions be derived deterministically from scanned pages (text-free areas, ruled lines), or does Mode 1 stay "text fragments + page image" for the long term? | Trusted Corpus track | Its `11-STRUCTURED-DOCUMENT-MODEL.md` / `18-PRODUCT-FEASIBILITY-VERDICT.md` — **PENDING TRUSTED-CORPUS FINDINGS** |
| OQ2 | Is a per-lesson document (`TrustedLessonDocument`) worth building before lesson boundaries are reliable (8/30 Khoa học 5 lessons lack `pageStart`; KHTN 7/8 TOC truncated)? | Founder + Trusted Corpus track | re-derived denominator and boundary confidence |
| OQ3 | Do children switch Views at all, or follow SAM's proposal? (same shape as Convergence U1 for intents) | Product | 2-week usage measurement on the 4–5 cohort; if >85% follow, collapse to proposal + «đổi cách khác» |
| OQ4 | Does a View recommendation change learning outcomes, or only navigation? | Product / learning science | no evidence either way; test after OQ3 |
| OQ5 | Which typed relationship can be extracted next with provenance — glossary terms (`Concept{term, definition}`) or numbered steps outside experiments? | Corpus | one bounded extractor + gold set, stories-pipeline style |
| OQ6 | Should the two evidence-minting patterns (validator vs direct mint) converge before Views multiply the Surfaces? (Review §3 open hypothesis #3) | Architecture | decision, not research |
| OQ7 | Is a step-ordering interaction on a Process view the first *deterministically gradable* non-Toán activity? | Pedagogy | falsification slice on one KHTN 6 lesson |
| OQ8 | Page-image licensing: is showing SGK page rasters to end users allowed under `ContentLicense.localResearchOnly`? (`knowledge_content_provider.dart:15-28`) | Founder / Legal Gate | the existing legal seam decides; Mode 1's anchor depends on it |
| OQ9 | Should "Đọc" become a fourth first-class intent or remain `lookup` shown as a book? | Founder | this package recommends *remain `lookup`* to avoid re-introducing LEARNING MODE |
| OQ10 | Does the Home card fix (read Scale path) belong with this concept or with the existing Track C defect list? | PM | already logged in WAL-206 §5; independent of Views |

## 2. What the concept board assumes that the evidence does not yet support

(Board: `concept/concept-ai-first/learning-view.png`. Each item is MEASURED or OBSERVED-IN-CODE
unless marked.)

1. **The lesson exists.** "Khoa học 5 Bài 2 — Dinh dưỡng và sức khỏe" is not in the corpus; Khoa
   học 5 Bài 2 is "Ô nhiễm, xói mòn đất và bảo vệ" (`pageStart: null`). Nearest: Khoa học 4 Bài 23.
2. **Structured Book blocks Image · Table · Formula · Activity exist.** No extractor produces
   them; `layout.tableLike ⇒ untrusted`; figures exist only as 3 human-curated crops.
3. **The nutrition lesson can be read natively.** Khoa học 4 pp.84–93: 8/10 pages untrusted, 0
   units for lesson 23; OCR headings misspelled.
4. **Frame 4's "Em có biết?" box and "Bảng 2.1" render as native blocks.** Side boxes are
   `sidebar` blocks (available when trusted); tables are fail-closed image regions.
5. **Frame 5's mindmap ("Chất dinh dưỡng → 4 groups") comes from data.** No `ConceptRelation[]`
   exists; producing it today would require LLM inference (forbidden by §12) or hand authoring.
6. **Frame 6's "Chính xác! 🎉".** No SGV key ⇒ `correct: null`; keyed lessons: 309 by registry,
   2 with a proven SGK↔SGV linkage (Tin học).
7. **"SAM đề xuất … ~5 phút / ~12 phút".** No duration data exists; a reason exists only when
   `proposeIntent`/`LearningAgenda` has a signal.
8. **"Đã học 3/18 bài · 17%".** Percentages for the child are on the never-build list
   (Convergence §23 item 1).
9. **Five bottom tabs incl. "Học cùng SAM" and "Tiến bộ".** Converged IA is three tabs; a SAM tab
   "advertises chat as the main activity".
10. **"Không cần mang cả PDF, tải theo sách/bài" reduces size materially.** Text does (≈10× per
    book); figure crops (0.5–4 MB each) and page rasters do not — the saving depends on an image
    policy that does not exist yet (`18` Q17–18).
11. **Three Views are selectable "on entering the lesson" independent of intent.** The converged
    model binds intent first; Views inside LearningContext.
12. **A "Bảng tóm tắt / Ghi nhớ cùng SAM" summary is available.** Only if it is verbatim
    objective/glossary text with provenance; generated summaries violate OCR TEXT ≠ TRUSTED SOURCE.

## 3. Risks

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | **Prettier Views weaken trust** — a reflowed Mode 1 or a clean Mode 2 makes OCR errors and inferred structure look authoritative (§12) | High if fragments are shown without trust marks | Child learns a wrong fact "from the book" | per-block trust + page-image anchor; fail-closed rendering (`15`) |
| R2 | **LEARNING MODE re-enters the vocabulary** through "3 cách học" | Medium | implementation diverges into 2–3 readings (the exact failure Convergence #2 fixed) | define Views inside LearningContext (`03` §3); never call them modes in code |
| R3 | **A parallel resolver / generic renderer is built** for Mode 2 | Medium | two mapping points semantics→widget (ADR-009 warning) | extend `_activityAction`/`resolveSurface` seam; no layout engine before three shapes |
| R4 | **Deep/Scale unification by decree** via the lesson document | Medium | breaks the 113 Learnable lessons or freezes the 1-lesson Deep path | SemanticBinding stays optional/additive (WAL-200 fail-closed guarantee) |
| R5 | **Corpus findings contradict the block model** | Unknown (PENDING) | `12`/`13` need rewrite | reconciliation checklists; nothing built until the study lands |
| R6 | **Recommendation without reason** ("SAM đề xuất" shown always) | Medium | violates Convergence §23 item 12; trains children to ignore SAM | render the row only on a signal |
| R7 | **Legibility gate gap** (WAL-193 class): true content, illegible presentation (e.g. OCR heading "SỨC KHOE" rendered large) | High for Mode 1 | child sees gibberish "from the book" | heading confidence rule; device walk before any ship |
| R8 | **Licence** — page images to end users under `localResearchOnly` | Unknown | legal | OQ8 through the existing seam |
| R9 | **Scope creep to "three screens"** | Medium | anti-principle #5 | one segmented control on one screen; reuse Surfaces |
| R10 | **Concept drift between Mode 3 realisations and Mode 1 text** if Mode 3 uses retrieval outside the lesson document | Low with current guard | "different truths" (§2) | `validateRealization` facts must come from the same document; build-time diff |

## 4. Not risks (checked and dismissed)

- "Evidence cannot cross Views" — evidence is keyed by SkillCase/lesson, not by Surface (`03` F6).
- "Views need a graph database" — no; rejected already (Proposal §3).
- "Views need an LLM online" — no; every View here is deterministic except guarded wording in Mode 3 (shadow today).
