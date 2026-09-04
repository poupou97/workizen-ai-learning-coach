# Breadth × Depth × UX Capability Matrix

Founder operating-model directive 2026-09-04 ("BUILD SAM BOTH BROAD AND DEEP")
— three tracks run in parallel, converge regularly, no capability counts as
mature just because backend exists or UI exists. This matrix is the shared
map. Rows are capabilities with real evidence gathered this session or
earlier and confirmed still true against current code; where something
exists in code but hasn't been freshly audited, that's stated honestly
rather than assumed.

| Capability | Breadth | Depth | UX | Evidence | Bottleneck | Next leverage |
|---|---|---|---|---|---|---|
| **Experiment (Khoa học/KHTN)** | 7 grades (4,6,7,8,9,10 + Vật lí/Hoá 10) — 113 Learnable lessons concentrated here | Source-grounded: "Chuẩn bị/Tiến hành" typography *is* the pedagogy (predict-then-observe), zero free-form inference needed | `ExperimentScreen` shipped, reads real corpus | Yes — `CandidateEvidence`+`EvidenceValidator` wired and tested; WAL-189 closed the lookup-intent leak | 2 known unfixed quality gaps (generic title fallback, image-split steps); gold-set still only 8 hand-checked entries | Fix the 2 known gaps; extend gold-set validation to the newly-added grades |
| **Reading/Writing (Tiếng Việt)** | Grade 5 (TV5) proven; Ngữ văn 6-12 blocked | Dedicated `extract_units_tv.py`; `EvidenceKind` wired | `ReaderScreen`/`ComposeLiteScreen` shipped; WAL-189 fixed evidence-integrity leak on both | Yes for TV5 | Ngữ văn raw-OCR extraction FALSIFIED (sidebar-box content indistinguishable from narrative without layout/column data) | Layout-aware extraction — real future capability, not started, no BBox data available yet |
| **Source Reasoning (Lịch sử)** | Baseline only — not extended this session | `SOURCE_TEXT` provenance tagged; Trace-vs-Evidence respected (WAL-189) | `SourceReaderScreen` shipped | Yes | Breadth unmeasured this session | Grade 6-9 History source-excerpt extension — validated lead from earlier findings doc, unimplemented |
| **Source-grounded Assessment (Tin học)** | 2/9 candidate lessons confirmed (grades 6/9/11/12 subset) | SGV-answer-key-grounded, validated safe: 0/2 false trusted on deep spot-check | Not built — would reuse `ReaderScreen`'s existing `options`+`correctOption` MCQ mode | Deferred (WAL-192) — gate passed narrowly, yield too small to justify Surface/Validator cost this pass | TOC OCR gaps + multi-run ambiguity in SGK page ranges cap yield | Bounded TOC-gap repair + multi-run disambiguation could raise yield above the current 2 |
| **Problem Solving (Toán)** | Grades 4-5 only (`toanExercises`) | SGV "MỤC TIÊU" objectives extractor confirmed extendable to grades 6-12 (grep-verified marker) but never run there | Exists via Workspace/exercise flow — not freshly audited this session | Yes for 4-5 | Never extended past grade 5 | Run `extract_objectives.py` on Toán 6-12; extend `toanExercises`-equivalent pattern |
| **Discovery/Stories** ("Bạn có biết?", "Ngày này năm xưa", Danh nhân) | Cross-subject, cross-grade — 38 verified stories, 21 PERSON | Build-time human/gold-curated VERIFIED gate (§28) + runtime defensive re-check; deterministic title derivation, always source-cited | Shipped — Home discovery card + `discovery_library_screen` full browse | N/A (browse/trivia, not graded) — the real quality axis is "does the shown fact read as true and coherent," not learner Evidence | **Just found+fixed live on Nokia (WAL-193)**: verify gate checks provenance, not standalone readability — a PERSON title without birth-years read as meaningless phonetic gibberish | Sweep remaining story types (QUOTE/EVENT/INVENTION_DISCOVERY) for the same class of silent-confusion bug; consider a build-time "does title stand alone" lint |
| **Bookshelf/Navigation** | All 12 grades (C-013) | N/A — navigation layer | Shipped, mature | N/A | None critical | Low priority, already mature |
| **Parent** | Screens exist (`family_manager_screen`, `parent_area`, `parent_tonight_screen`) | Deliberately deferred per original concept plan ("sau khi P0-P1 sinh evidence thật đáng xem") | Exists in code; visual/content fidelity not verified this session | Depends on upstream Evidence (currently thin — 113/3,679 lessons Learnable) | Not audited this session | Once Experiment/Tin học breadth grows, audit whether Parent screens surface it meaningfully |
| **Camera/Problem-capture** | Cross-subject intent (`capture_screen`, `confirm_problem_screen`, OCR adapters) | Confirm-gate before Evidence, per original P0 slice plan | Exists in code; not visually audited this session | Depends on downstream Workspace activity | Unknown — not audited | Visual/functional audit pending |
| **Assessment/Review** | `assessment_screen`/`assessment_result_screen`/`learner_confirm` exist | `review_priority.dart`/adaptive challenge policy exist | Exists in code | Yes, wired | Not visually audited this session | Visual audit pending |

## Reading this matrix

**Most mature (all 3 tracks real)**: Experiment. This is the reference
pattern — real corpus, real pedagogy already encoded in source typography,
shipped Surface, tested Evidence path, WAL-190 measured a real Learnable
delta with a gold-set-first loop.

**Depth validated, Breadth intentionally small, UX not yet built**:
Source-grounded Assessment (Tin học). Correctly NOT shipped — 2 lessons
doesn't justify new Surface/Validator work yet, but the underlying
capability is proven safe, not falsified.

**UX existed, nobody had looked closely — real defect found by direct
inspection, not review**: Discovery/Stories. WAL-193 is the concrete example
of Founder's convergence rule: a capability can have shipped UI and a
passing build-time gate and still fail a real child on first use, because no
one had opened the actual running app and read what a child would read.
This is the argument for regularly walking the real product, not just
auditing backend readiness numbers.

**Not yet touched this session**: Parent, Camera, Assessment/Review exist in
code but haven't been walked on-device this pass — named here so they don't
silently fall off the map, not rated on evidence that doesn't exist yet.

## Immediate signal

Discovery/Stories is the capability that most directly demonstrates the
convergence principle right now: real content (SGK-sourced) → real
pedagogy-adjacent structure (VERIFIED gate) → real SAM experience (Home
card) → found broken by walking the real learner journey → real fix,
device-confirmed. The other Track C rows (Parent, Camera, Assessment) are
the natural next candidates for the same kind of walk-and-verify pass,
since they're the rows with the least fresh evidence in this matrix.
