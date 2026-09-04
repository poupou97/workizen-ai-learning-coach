# 19 — Jira / Confluence Status

> **Reconciled with TC-v1 (2026-09-05).** WAL-208 row added; git/PR/bundle section updated; **Reconciliation ledger** and **Not reconciled in this pass** added.

## Jira (project WAL, cloud `workizen.atlassian.net`)

| Key | Summary | Role in this track | Status at writing |
|---|---|---|---|
| **WAL-207** | [P0 Research] Learning Views concept & reference research — One Trusted Lesson → Smart Book / Visual Learning / SAM Tutor | **This track's single ticket** (created 2026-09-05; labels `research`, `learning-views`, `p0`, `founder-order`). Linked *Relates* → WAL-206. Comment posted when PR #55 opened; second comment posted with the TC-v1 reconciliation PR. | Ideas (created) |
| **WAL-208** | Trusted-Corpus Feasibility Study TC-v1 (`docs/research/trusted-corpus/00…20`, PR #56) | **The evidence this package now consumes.** Verdict GO WITH SOURCE ARCHITECTURE CHANGE; every extraction-dependent claim here was reconciled against it on 2026-09-05 (ledger below; conflicts in `17` §5). | merged to `main` (PR #56) |
| WAL-206 | [P0] Layout-aware K–12 extraction — reading order, columns, block roles from OCR geometry; then re-run WAL-204 | Upstream constraint for Mode 1 (block roles, trust, content gate); its result doc is cited throughout; two of its gold numbers are superseded by TC-v1 on the hard set (`18` §5) | QA |
| WAL-205 | [BACKLOG] K–12 Activity Pattern Expansion — remaining patterns with required modality | Mode 3's measured bottleneck (Short-Answer Surface is its first item); `14` maps patterns to Views without promoting any; counts to recompute per TC-15 | Ideas |
| WAL-203 | [REGISTRY] K–12 Activity Pattern Registry — 27 corpus-derived patterns | Source of the pattern counts in `14` (old-extractor counts, TC-15) | Ideas |
| WAL-204 | [P0 EXPERIMENT] Pattern-driven scale falsification | The failure that rejects "PDF → Markdown → generic renderer" (`04` §1); TC-v1 re-measured its page (TC-02 §2) | Ideas |
| WAL-200 | [ARCH] P0 — Thin Convergence Bridge + Gold Set + Vertical Slice | `SemanticBinding` design reused in `12` | Ready |
| WAL-196 / WAL-195 | Education Data Architecture proposal / epic | Seven-plane model that Views must sit on top of (`03` F8) | Ready / Ideas |
| WAL-185 | Learning Visual Surface — Process/Flow + Map/Spatial POC | Mode 2's two PROVEN shapes | Ideas (research doc marks it shipped + Founder-reviewed) |
| WAL-30 | Generative Tutor gate | Mode 3's LLM remains shadow behind it | — |

**Search performed before creating (2026-09-04):** JQL `project = WAL AND (summary ~ "Learning View" OR summary ~
"Lesson Workspace" OR summary ~ "Smart Book" OR summary ~ "architecture" OR summary ~ "Trusted
Corpus" OR summary ~ "Feasibility")` → no Learning-Views ticket existed; no Trusted-Corpus ticket
was found at that time. WAL-208 has since landed; the *Relates* link WAL-207 ↔ WAL-208 is noted in
the reconciliation comment (link creation is not a gate; the Founder may add it).

**Not done, by rule:** no epic, no child issues, no transitions beyond creation (Founder-only gates).

## Confluence

No Confluence page was created or edited in this track (the order asked for a Jira ticket and a
PR + Desktop bundle only). If the Founder wants a Confluence mirror, `01` and `18` are the pages
to publish; `.workforce.json` in the repo root names the space (`WAL`).

## Git

- Original branch `research/learning-views-concept` (worktree), base `3f0c160` (WAL-206 merged) →
  PR **#55** (https://github.com/poupou97/workizen-ai-learning-coach/pull/55), merged.
- Reconciliation branch `research/learning-views-tc-v1-reconcile`, base `6cf832b` (WAL-208 / PR #56
  merged) → PR titled *"docs(research): WAL-207 — reconcile Learning Views with TC-v1 Trusted-Corpus
  findings"*; number and link recorded in the WAL-207 comment. CI (`flutter analyze` + `flutter test`,
  runs on every PR including docs-only by design — `.github/workflows/ci.yml`) → squash-merge only if green.
- Commit scope: `docs/research/learning-views/` only. No pack data, no ZIPs, no PDFs, no images.
  **No trusted-corpus doc was edited.**
- Desktop bundle: `~/Desktop/HOC-CUNG-SAM-LEARNING-VIEWS-RESEARCH-<YYYYMMDD-HHMM>.zip` and
  `…-LATEST.zip` — the 21 markdown files of this directory, nothing else; refreshed after the merge.

## Reconciliation ledger (2026-09-05)

Evidence read: TC-01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19 and
the TC MANIFEST. Target docs edited: `00 · 01 · 03 · 04 · 05 · 06 · 12 · 13 · 15 · 17 · 18 · 19 ·
MANIFEST` (each carries a "Reconciled with TC-v1 (2026-09-05)" line).

| Measure | Count |
|---|---|
| `PENDING TRUSTED-CORPUS FINDINGS` tag lines walked | **25** (4 status lines + 21 claim locations); **0 remain** except historical mentions in `00` and status lines that now say "were tagged" |
| Claim locations fully resolved with a MEASURED (TC-nn) finding | **13** |
| Claim locations resolved in part — measured part replaced in place, remainder marked STILL UNMEASURED or pointed at the open decision | **8** |
| Distinct measurements STILL UNMEASURED after TC-v1 | **6** — (a) text fidelity per subject; (b) false trust / reading order at scale (≥ 3,000 validated blocks); (c) figure bbox precision; (d) typography/bold signal for glossary terms; (e) reader-dpi/webp raster size; (f) SGV pairing upper bound (SGV format census). 24 marks across 10 docs, each naming the closing measurement |
| Open decisions surfaced (not measurements) | **1 from the tags:** page-image licensing (OQ8). **Plus from `17` §5:** C1 denominator wording, C5 Mode 1 prototype vs source layer, C11 thesis wording, C12 release bar (OQ11) — Founder |
| Reconciliation-checklist items (`12` §6, `13` §7, `15` §7, `18` §5) | **21 → 18 applied**, 3 not tickable by this pass (2 wait on OQ8; 1 = per-subject fidelity, unmeasured) |
| A/B/C/D verdicts changed (`01`, `18` §2–3) | **0 of 11** (re-evaluation table `18` §3a) |
| `12` §2 classes changed | **5**: Question FORMALIZE → HYPOTHESIS; Activity label FORMALIZE → HYPOTHESIS; Image/Figure HYPOTHESIS → EXTEND (image region); Table HYPOTHESIS → EXTEND (GPU) / REJECT as text (Mac); Formula HYPOTHESIS → REJECT as text |
| WAL-207 MEASURED claims superseded by TC-v1 (listed, not silently edited) | **4** (`18` §5: heading 0.90, question AVAILABLE, reading order 0.99, per-block trust) + 2 reconciled as consistent |
| Conflicts WAL-207 × WAL-208 listed | **12** (`17` §5), each with a proposed resolution and decider |

## Not reconciled in this pass (time-boxed 2026-09-05)

- `02-CURRENT-LESSON-EXPERIENCE-AS-IS.md` — AS-IS file; its "3,679 canonical SGK lessons" is
  correct as a canonical count and is *not* annotated with the 3,381 ranged figure (covered by
  `17` §5 C1). No TC-v1 numbers added.
- `14-ACTIVITY-PATTERN-INTEGRATION.md` — pattern counts not annotated as old-extractor artefacts
  (covered by the caveat in `05` §2 and `17` §5 C8, TC-15).
- `16-UX-CONCEPT.md` — untouched; wireframes carry no corpus numbers. The "question" affordance in
  the Mode 1 wireframe should be re-read under `04` §4 item 2 (plain text until the role layer).
- `07-REFERENCE-REPOSITORY-COMPARISON.md` — "3,679 lessons" left as the canonical count.
- Inside TC-v1 itself: TC-18 Q17 writes "≈ 555–603 lessons (15–16 %)" while TC-01/TC-03 give
  555/3,381 — flagged in `17` §5 C1, not resolved here (trusted-corpus docs are not edited by this track).
- Jira: no *Relates* link WAL-207 ↔ WAL-208 created by this pass (noted in the comment instead).
- Confluence mirror: not created (unchanged from PR #55).

## Precedence reminder

The Trusted Corpus Feasibility Study (WAL-208; `docs/research/trusted-corpus/`,
`~/Desktop/HOC-CUNG-SAM-TRUSTED-CORPUS-FEASIBILITY-LATEST.zip`) outranks this package on every
extraction-dependent claim. Its findings have now been consumed; where the two disagree, `17` §5
says which wins or who decides — nothing was averaged.
