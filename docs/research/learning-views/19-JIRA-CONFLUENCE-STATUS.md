# 19 — Jira / Confluence Status

## Jira (project WAL, cloud `workizen.atlassian.net`)

| Key | Summary | Role in this track | Status at writing |
|---|---|---|---|
| **WAL-207** | [P0 Research] Learning Views concept & reference research — One Trusted Lesson → Smart Book / Visual Learning / SAM Tutor | **This track's single ticket** (created 2026-09-05; labels `research`, `learning-views`, `p0`, `founder-order`). Linked *Relates* → WAL-206. Final comment posted when the PR is open. | Ideas (created) |
| WAL-206 | [P0] Layout-aware K–12 extraction — reading order, columns, block roles from OCR geometry; then re-run WAL-204 | Upstream constraint for Mode 1 (block roles, trust, content gate); its result doc is cited throughout | QA |
| WAL-205 | [BACKLOG] K–12 Activity Pattern Expansion — remaining patterns with required modality | Mode 3's measured bottleneck (Short-Answer Surface is its first item); `14` maps patterns to Views without promoting any | Ideas |
| WAL-203 | [REGISTRY] K–12 Activity Pattern Registry — 27 corpus-derived patterns | Source of the pattern counts in `14` | Ideas |
| WAL-204 | [P0 EXPERIMENT] Pattern-driven scale falsification | The failure that rejects "PDF → Markdown → generic renderer" (`04` §1) | Ideas |
| WAL-200 | [ARCH] P0 — Thin Convergence Bridge + Gold Set + Vertical Slice | `SemanticBinding` design reused in `12` | Ready |
| WAL-196 / WAL-195 | Education Data Architecture proposal / epic | Seven-plane model that Views must sit on top of (`03` F8) | Ready / Ideas |
| WAL-185 | Learning Visual Surface — Process/Flow + Map/Spatial POC | Mode 2's two PROVEN shapes | Ideas (research doc marks it shipped + Founder-reviewed) |
| WAL-30 | Generative Tutor gate | Mode 3's LLM remains shadow behind it | — |

**Search performed before creating:** JQL `project = WAL AND (summary ~ "Learning View" OR summary ~
"Lesson Workspace" OR summary ~ "Smart Book" OR summary ~ "architecture" OR summary ~ "Trusted
Corpus" OR summary ~ "Feasibility")` → no Learning-Views ticket existed; **no Trusted-Corpus
ticket was found** at search time (the parallel track had not created one), so no second link was
made. If one appears, link WAL-207 *Relates* to it.

**Not done, by rule:** no epic, no child issues, no transitions beyond creation (Founder-only gates).

## Confluence

No Confluence page was created or edited in this track (the order asked for a Jira ticket and a
PR + Desktop bundle only). If the Founder wants a Confluence mirror, `01` and `18` are the pages
to publish; `.workforce.json` in the repo root names the space.

## Git

- Branch `research/learning-views-concept` (worktree), base `3f0c160` (WAL-206 merged).
- Commit scope: `docs/research/learning-views/` only. No pack data, no ZIPs, no PDFs, no images.
- PR → `main`, CI (`flutter analyze` + `flutter test`, runs on every PR by design) → Founder merge.
- Desktop bundle: `~/Desktop/HOC-CUNG-SAM-LEARNING-VIEWS-RESEARCH-<YYYYMMDD-HHMM>.zip` and
  `…-LATEST.zip` — the same 21 markdown files, nothing else.

## Precedence reminder

The Trusted Corpus Feasibility Study (parallel track; `poc-out/trusted-corpus/`,
`~/Desktop/HOC-CUNG-SAM-TRUSTED-CORPUS-FEASIBILITY-LATEST.zip`) outranks this package on every
extraction-dependent claim. Its bundle did not exist when this package was written; apply the
reconciliation checklists in `12`, `13`, `15`, `18` when it lands, and note the outcome on WAL-207.
