# Per-round archive documents — canonicalised 2026-09-06

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.** These documents identify SGK content by
> `book / pdf page / printed page / lesson / block id` and quote at most short titles and UI
> strings, per Founder decision **D4** (`docs/founder-orders/30-founder-decisions-pre-autonomy-checkpoint.md:67-80`,
> operational form in `docs/research/METRIC-DENOMINATORS.md:50-57`). **No verbatim SGK passage,
> question text, page crop or device frame is in this directory** — see «What was deliberately
> left out» below.

## Why this directory exists

Each of rounds 5, 6 and 7 was closed by building a **review ZIP** for the Founder's Desktop. The
ZIP was assembled by `tool/reporting/build_round_archive.py` from a **content directory**: the
builder reads `content_dir = os.path.dirname(spec_path)` and stages the fifteen `00-…`–`14-…`
documents found beside the spec.

**Those fifteen documents per round were written for the archive and were never in the
repository.** They existed in exactly two places: inside the ZIP, and in a session-scoped
scratchpad that is wiped when the session rolls. Four of the five ZIPs were deleted from the
Desktop after review — which is correct behaviour under
[`docs/governance/REPOSITORY-SOURCE-OF-RECORD.md`](../../governance/REPOSITORY-SOURCE-OF-RECORD.md)
— and the scratchpad had already saved two of them once, by luck rather than by process.

That made **45 documents** the exact failure the standing rule names: *information existing
nowhere but a ZIP, a Desktop or a scratchpad.* They are round reports, acceptance cards,
falsification registers, metrics tables, open-risk registers and roadmaps — every one of them on
the mandatory list in Founder task order 43 §1. They are committed here.

The audit that found them is
[`../ROUND4-7-CANONICAL-RECORD-AUDIT.md`](../ROUND4-7-CANONICAL-RECORD-AUDIT.md).

## What is here

| Path | Round | Contents |
|---|---|---|
| `round05/` | 5 | 15 archive documents · `archive-spec.json` · evidence (branch heads, CI, PR state, git log, structural spot checks, device-frame verification) · manifests (regeneration note, large-data inventory) |
| `round06/` | 6 | the same 15 + `PROVENANCE.md` · gate results · the **round-6 device evidence manifest and steps** |
| `round07/` | 7 | the same 15 + `PROVENANCE.md` + `NO-DEVICE-FRAMES-THIS-ROUND.md` · gate results · workforce config |
| `ROUNDS-INDEX.md` | 3–7 | the per-round VERDICT · NORTH STAR · KEY RESULT · PRODUCT DELIVERY · MERGE STATUS · NEXT BOTTLENECK table, previously Desktop-only |

**Round 4 has no content directory.** Its archive predates this format — two pre-format
`ROUND4-REPORT` ZIPs, recorded as `LOST, NOT RECOVERABLE` in
[`../ARCHIVE-REGISTRY.md`](../ARCHIVE-REGISTRY.md). Round 4's canonical knowledge is in
`ROUND4-CONSOLIDATED-REPORT-2026-09-06.md`, `ROUND4-PLAN.md`,
`PIPELINE-ROUND4-FAILURE-CLASS-FIXES.md`, `legacy-reprocess/ROUND4-BATCH-1-REPORT.md`, `lane-c/**`
and `docs/design/TRACK-B-ROUND4-EXPERIENCE.md` — the audit checks it category by category.

## Provenance

Recovered from the scratchpad content directories that built the ZIPs, byte-for-byte, unedited.
Nothing was summarised, corrected or tidied — including the round-5 acceptance card's own
statement that it was grading against **RECONSTRUCTED** criteria, which is a true record of what
that agent knew at the time and is superseded by
[`../ROUND5-ACCEPTANCE-CRITERIA.md`](../ROUND5-ACCEPTANCE-CRITERIA.md) and by the verbatim §16 in
`docs/founder-orders/33-master-task-order-học-cùng-sam-round-5.md`.

`round05/archive-spec.json` and `round06/archive-spec.json` are **byte-identical** to
`tool/reporting/examples/round05-archive-spec.json` and `round06-archive-spec.json` (verified by
sha256). They are kept beside their content because the builder requires the spec and the content
in one directory. `round07/archive-spec.json` had no committed copy at all on the integration
branch — the only one was on the unmerged `ws-archive/round5-retrospective`.

## What was deliberately left out, and why

**Restricted under D4 — must not enter Git:**

| Excluded | Where it was | Reason |
|---|---|---|
| `screenshots/round6-01…07-*.png` (7 device frames) | `round06-content/screenshots/` | Verbatim SGK text rendered on screen. Frames stay at `~/Desktop/wal-evidence/round6-ws-d/`; **their manifest and steps are canonicalised** at `docs/design/track-b-evidence/round6/`, carrying git sha, APK sha256, per-pack hashes, fixture provenance and per-frame sha256 |
| `evidence/round6-artefacts/`, `evidence/round7-artefacts/` (1.3 MB + 5.8 MB) | content dirs | Real lesson fixtures and lesson packs built from SGK text |

**Already in Git elsewhere — not duplicated:**

| Not copied | Already at |
|---|---|
| `metrics/frozen-calibration/` (5 files, 140 KB) | `tool/corpus/thresholds/frozen/` on `origin/ws-t/round7-trust-calibration` — **verified byte-identical** (`LEDGER.jsonl` sha256 `1427fa98…`). Unmerged, not missing |
| `metrics/golden-slices.json` | `tool/corpus/accounting/golden-slices.json` — byte-identical (sha256 `097735eb…`) |
| `reports/**` (except `PROVENANCE.md`) | copies of `docs/research/**` documents already committed |

**The ZIPs themselves** are not here and never will be: they contain the frames, fixtures and
packs above. Their identities — original and rebuilt sha256, file counts, byte sizes — are in
[`../ARCHIVE-REGISTRY.md`](../ARCHIVE-REGISTRY.md), so a lost review snapshot costs its bytes and
not its provenance.

## Rebuilding a review snapshot

```bash
python3 tool/reporting/build_round_archive.py \
    --spec docs/research/round-archives/round07/archive-spec.json \
    --repo /path/to/workizen-ai-learning-coach \
    --out  ~/Desktop
```

A rebuild will **not** be byte-identical to the original — the manifest records build time and
commit — and the excluded evidence above will be missing unless staged from its own location. A
rebuild restores contents, not identity. Build the ZIP **after** canonicalisation, never as the
close step itself.
