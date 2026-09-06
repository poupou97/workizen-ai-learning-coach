# `tool/reporting` — per-round retrospective archives

**One immutable ZIP per round, on the Founder's Desktop.** Written once, never overwritten,
self-contained, readable years later with no repository and no network.

This directory holds the generator. It does **not** hold the archives — those live on the
Founder's Desktop alongside `HOC-CUNG-SAM-ROUNDS-INDEX.md`, which carries one row per round.

---

## Why an archive and not just the consolidated report

A round's evidence is spread across the repository, GitHub (PR state and CI), a device-evidence
directory, and gitignored artefact trees measured in gigabytes. A consolidated report *cites* all
of that; an archive *contains* what it legally can and records the rest with path, size and
reproduction instructions. The distinction matters the first time someone asks "what actually
happened in round 5" after the branches are gone.

---

## Usage

```bash
python3 tool/reporting/build_round_archive.py \
    --spec  <round-content-dir>/archive-spec.json \
    --repo  /path/to/workizen-ai-learning-coach \
    --out   ~/Desktop

# stage and verify without writing a ZIP
python3 tool/reporting/build_round_archive.py --spec ... --dry-run

# keep the staging directory to inspect what would ship
python3 tool/reporting/build_round_archive.py --spec ... --keep-staging
```

Exit codes: **0** built and verified · **1** build or verification failure · **2** bad invocation.

Requires only the Python 3 standard library.

---

## What the tool enforces (rather than trusts)

| Rule | Behaviour |
|---|---|
| **Never overwrite an archive** | If `…-<date>.zip` exists, it writes `…-v2.zip` (then `-v3` …) and prints a NOTE. A previous round's ZIP is immutable evidence. |
| **No zero-byte required document** | The build **fails** rather than shipping an empty required report. An empty file reads as "nothing happened" instead of "not captured", which is worse than a missing one. |
| **No broken in-archive reference** | Any backticked path whose first segment is a required directory (`evidence/…`, `metrics/…`, `screenshots/…`, `reports/…`, `manifests/…`), and any reference to a numbered document, must resolve inside the archive. Conservative by design, so prose mentioning a *repository* path cannot produce noise. |
| **The manifest is generated, never written by hand** | `15-FILE-MANIFEST.md` is built from the staged bytes — one SHA-256 and byte count per file — and then **re-verified against the finished ZIP** by recomputing every hash from inside it. |
| **Missing optional sources are recorded, not dropped** | A `copy` entry marked `"optional": true` that matches nothing is listed in the manifest as **NOT CAPTURED**. |
| **Large / licence-restricted data is never copied** | The SGK corpus and its derivatives stay out. The spec's `excluded` block records what, where, how big and why; the round's own documents carry the reproduction instructions. |

Post-zip it prints, and the rounds index records: **file count · size · SHA-256 · integrity check
(`testzip`) · manifest match**.

---

## Making the next round's archive

1. **Create a content directory** (anywhere — a scratchpad is fine; it is an input, not an
   artefact):

   ```
   round06-content/
   ├── archive-spec.json          # copy examples/round05-archive-spec.json and edit
   ├── 00-START-HERE.md … 14-JIRA-CONFLUENCE-STATUS.md   # authored by hand
   ├── evidence/                  # anything you generate yourself (PR JSON, CI status, hashes)
   ├── metrics/                   # optional; the spec can also copy these from the repo
   ├── screenshots/               # optional; the spec usually copies device frames from the repo
   ├── reports/                   # optional
   └── manifests/                 # optional
   ```

   Everything in the content directory is copied into the archive as-is (except
   `archive-spec.json` and dotfiles). `15-FILE-MANIFEST.md` is **generated** — do not author it.

2. **Edit the spec.** Fields:

   | Field | Meaning |
   |---|---|
   | `schema` | must be `wal-round-archive-spec-v1` |
   | `round`, `roundLabel` | `"06"`, and a one-line title |
   | `closeDate` | the **repository-evidenced** close date — verify it from git log, PR merge/close dates and the consolidated report's own date; do not assume |
   | `closeDateEvidence` | the sentences that justify `closeDate`; reproduced in the manifest |
   | `classification` | the banner, e.g. `INTERNAL / RESEARCH ONLY - DO NOT PUBLISH …` |
   | `rootDir`, `archiveNameTemplate` | `ROUND-06`, `HOC-CUNG-SAM-ROUND-{round}-{closeDate}.zip` |
   | `requiredDocs` | the 16 numbered documents; the build fails if any is missing or empty |
   | `generatedDocs` | documents the tool writes itself (`15-FILE-MANIFEST.md`) |
   | `requiredDirs` | must exist **and be non-empty** |
   | `copy` | `[{src, dest, optional?, rename?}]`; `src` is repo-relative and may be a glob |
   | `excluded` | large/licence-restricted data: what · path · size · reason |

3. **Dry-run**, fix what it reports, then build.

4. **Add a row to `~/Desktop/HOC-CUNG-SAM-ROUNDS-INDEX.md`** — ROUND · DATE · VERDICT ·
   NORTH STAR · KEY RESULT · PRODUCT DELIVERY · ZIP NAME (with file count, size, SHA-256) ·
   MERGE STATUS · NEXT BOTTLENECK.

---

## Writing rules for the numbered documents

These are conventions the tool cannot enforce, and they are the reason the archive is worth
having:

- **Do not fabricate missing evidence.** Write **`UNAVAILABLE`** or **`NOT CAPTURED`**. That is a
  correct answer.
- **Label claims:** **PROVEN** (re-verified first-hand — a command, a hash, an API read) ·
  **MEASURED** (an instrument's number, recorded in a committed report) · **OBSERVED** (seen on a
  real device or a page render) · **INFERRED** · **HYPOTHESIS** · **UNKNOWN**.
- **Never turn PARTIAL into DONE.** Allowed statuses: DONE · PARTIAL · FAILED · FALSIFIED ·
  BLOCKED · DEFERRED · NOT STARTED.
- **Repeat the round's *original* acceptance gates and grade each one.** Do not redefine gates
  after seeing results. *(Round 5's acceptance criteria were never committed to the repository and
  had to be reconstructed — see that archive's `11-FOUNDER-ACCEPTANCE-CARD.md` §0. **Commit each
  round's acceptance gates with its plan**, as `ROUND6-PLAN.md` does.)*
- **State denominators; never pool populations; never average scores that the Founder keeps
  separate.**
- **Widget tests and emulators are not real-device evidence** — say so wherever that distinction
  applies.
- **Answer plainly: what can a child use now that they could not before?** Then answer separately
  for parent, for SAM, and for internal-research-only.

---

## Files

| File | Purpose |
|---|---|
| `build_round_archive.py` | the generator |
| `examples/round05-archive-spec.json` | the spec that built the round-5 archive; copy it as a starting point |
| `README.md` | this file |
