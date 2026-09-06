# Where each report in this directory came from

**Round 7's workstream reports are NOT on the integration branch.** Each lives only on its own
workstream branch, because nothing was merged. They were extracted with `git show <branch>:<path>`
by the archive builder on **2026-09-06** and are byte-identical to what those branches hold.

| File in this archive | Source branch | Head at extraction | Path in the repository |
|---|---|---|---|
| `ROUND7-CONSOLIDATED-REPORT-2026-09-06.md` | `integration/round7-2026-09-06` | `74d9db6` | `docs/research/…` |
| `ROUND7-PLAN.md` | `integration/round7-2026-09-06` | `74d9db6` | `docs/research/…` |
| `ROUND7-MERGE-DEBT-REAUDIT.md` | `integration/round7-2026-09-06` | `74d9db6` | `docs/research/…` |
| `ROUND7-HISTORICAL-CORRECTIONS.md` | `integration/round7-2026-09-06` | `74d9db6` | `docs/research/…` |
| `ws-m-metric-truth/METRIC-REGISTRY-ROUND7.md` | **`ws-m/round7-metric-truth`** | **`a6cae3b`** | `docs/research/…` |
| `ws-t-trust-calibration/TRUST-CALIBRATION-ROUND7-REPORT.md` | **`ws-t/round7-trust-calibration`** | **`5e706c9`** | `docs/research/…` |
| `ws-t-trust-calibration/TRUST-CALIBRATION-POLICY-v1.md` | **`ws-t/…`** | **`5e706c9`** | `docs/research/…` |
| `ws-t-trust-calibration/TRUST-CALIBRATION-BLIND-PROTOCOL-v1.md` | **`ws-t/…`** | **`5e706c9`** | `docs/research/…` |
| `ws-s-structured-gap/STRUCTURED-GAP-ROUND7.md` | **`ws-s/round7-structured-gap`** | **`36e4c50`** | `docs/research/…` |
| `ws-r-round6-debt/ROUND6-DEBT-TRIAGE.md` | **`ws-r/round7-debt`** | **`7d37521`** | `docs/research/…` |
| `context-previous-rounds/*` | `integration/round7-2026-09-06` | `74d9db6` | `docs/research/…` |

**All four workstream heads were independently re-resolved from `origin` and matched §10.1 of the
consolidated report** — `evidence/round7-branch-heads-and-merge-debt.txt`. *(PROVEN.)*

**The frozen calibration payloads** in `metrics/frozen-calibration/` were extracted the same way,
from `ws-t/round7-trust-calibration:tool/corpus/thresholds/frozen/`. **They are the artefacts that
make GATE B provable**, and they are archived here because the branch that holds them is unmerged.

**Why this table matters.** If these branches are ever deleted, the copies here are the surviving
ones, and this table is what lets a later reader tell which generation they hold — the same
discipline round 7's own lineage gate applies to fixtures, applied to documents.

**Language note:** all round-7 workstream reports are in English. Earlier rounds' WS-D reports were
in Vietnamese and were archived untranslated; the same rule applies here — **translating a
workstream's own report would be a rewrite, not an archive.**
