# coordinator notes (evidence for 00/01/08/09)

## git — merged rounds (main)
e5155f4 docs(research): WAL-207 — reconcile Learning Views with TC-v1 Trusted-Corpus findings (#57)
6cf832b research(corpus): TC-v1 Trusted-Corpus Feasibility Study — census, hard gold set, parser bake-off, cas
5b0bcfa docs(research): WAL-207 — Learning Views concept & reference research (One Trusted Lesson → Đọc / Trực
3f0c160 feat(corpus): WAL-206 — layout-aware K-12 extraction (XY-cut), gold set, content gate, funnel (#54)
65d21d7 feat(corpus): WAL-204 — pattern router P0 experiment (Khoa học/KHTN 4-9) + pattern registry (#53)
dcc29a8 research(corpus): Fable 5.1 independent K-12 scale review — corpus-derived taxonomy + five-bucket verd
74601c9 docs+feat(corpus): WAL-197/201 — K-12 convergence coverage census (#51)
13c0792 docs(architecture): WAL-195 — Education Data Architecture AS-IS/theory/TO-BE proposal (#50)
9ab5274 docs(research): Breadth×Depth×UX capability matrix (Founder 3-track operating model) (#49)
2bf7058 fix(stories): WAL-193 — «Bạn có biết?» PERSON title vô nghĩa khi thiếu năm sinh-mất (#48)
81bd355 docs(research): WAL-192 gate closed — automated SGK↔SGV linkage validated, low yield, deferred (#47)
9d003ae docs(research): WAL-192 — Tin học full-chain POC: format lệch giữa lớp, bounded 4-lớp (#46)

## open PRs (unmerged, READY FOR FOUNDER REVIEW)
#58 research/tc-v2-science-slice — research(corpus): TC-v2 Science Slice — Source → SDM → block trust → Role Layer 
KB #1 — PROPOSED D-135…D-138: Trusted-Corpus source architecture (SDM-as-source, block t

## packs ON DISK (assets/pack is gitignored, 2 tracked placeholders) — VERIFIED 2026-09-05 10:3x
- The on-disk packs g4–g9 are the WAL-206 *variant* build (PATTERN_ROUTER=1 UNITS_SOURCE=layout ROUTE_EXPLAIN=1): router entries g4 32/32 readings (15 lessons), g5 13/81 (8), g6 32/32 (22), g7 18/18 (9), g8 22/22 (13), g9 88/87+1 (29). A default build (no env) emits none of these.
- Consequence: any APK built from this Mac since 2026-09-04 23:xx ships experimental router content; the Nokia currently runs such a build. No build-provenance manifest ties an APK to pack build flags. (P0 gap: build provenance.)
- Grades 1–3 and 10–12 packs carry 0 readings/writings; g10 has 5 khoaExperiments only.

## Founder decisions in force (from session record, 2026-09-04/05)
- TC-v1 verdict ACCEPTED: GO WITH SOURCE ARCHITECTURE CHANGE (SDM as source; block-level trust; image-first for math/visual; trusted subset not whole corpus — filed PROPOSED, KB PR #1 unmerged)
- P0-NEXT was Science Slice (TC-v2, WAL-209, PR #58 unmerged); primary criterion = validate the chain, coverage secondary
- Short-Answer Surface DEFERRED until Role Layer trust measured (six roles); TC-v2 question precision 0.83-0.89 < 0.95
- Three Learning Views RETAINED; Views-in-LearningContext and Smart Book=lookup NOT approved; LearningSession model kept open
- Hybrid Smart Book research only; page/image crop delivery NOT approved (licensing gate); architecture must work without page images
- Denominators: 3,679 canonical vs 3,381 ranged, never collapsed; TC-v2 repaired six Science books 194→238 ranged (canonical >=3,725 proposed, not adopted)
- No full-corpus reprocess; no 27-pattern expansion; no mass Learning Views implementation
- Governance: no standing merge authority; stop at READY FOR FOUNDER REVIEW
