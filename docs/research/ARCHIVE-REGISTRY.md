# Per-round archive registry — identities of REVIEW SNAPSHOTS

> **Semantics corrected 2026-09-06** (Founder task order 43). This file is a **provenance /
> identity registry**, **not** a Desktop archive policy and **not** the project's source of record.
> The canonical source of record is the **repository** — see
> [`docs/governance/REPOSITORY-SOURCE-OF-RECORD.md`](../governance/REPOSITORY-SOURCE-OF-RECORD.md).
>
> Earlier text in this file called per-round Desktop archives «the archive of record». That was
> wrong under the governance clarified on 2026-09-06. **Previous Desktop ZIPs were review
> snapshots.** The wording is corrected; **no hash has been deleted and no history rewritten.**

## What this file is for

A review snapshot may be deleted by the Founder at any time after reading — that is expected. But
a ZIP that is later **rebuilt is never byte-identical**: its manifest records build time and
commit, so its hash cannot match what was published. Without a registry, a reader comparing a
rebuilt archive against a hash quoted in an old report would see a mismatch and reasonably
conclude tampering.

**So this file records identities, so that losing a review snapshot costs its bytes and not its
provenance.** It does not make the ZIPs canonical, and nothing may depend on their continued
existence.

## What happened on 2026-09-06 — recorded, not hidden

Four of the five per-round Desktop ZIPs (rounds 4, 5, 6-v1, 6-v2) disappeared while
`~/Desktop/wal-evidence/` beside them was untouched. **The Founder subsequently confirmed they
delete Desktop copies after reviewing them.** That is correct behaviour under the rule above and
**cost the project no record** — see `ROUND4-7-CANONICAL-RECORD-AUDIT.md` for the evidence that
the canonical knowledge was already in the repository.

Two were rebuilt at the time from inputs that happened to still exist in a session-scoped
scratchpad. **A rebuild restores contents, not identity.**

| Round | Filename | Original sha256 | Files | Bytes | Status |
|---|---|---|---|---|---|
| 4 | `ROUND4-REPORT` ×2 (pre-format) | `bf0d27a9…` | — | — | **LOST, NOT RECOVERABLE.** Source of record is in git and inside the round-5 archive |
| 5 | `HOC-CUNG-SAM-ROUND-05-2026-09-06.zip` | **`30f2912cd165c5b9bf67ea32ab427c92a97282714356effe657e748eb8a77a4c`** | 117 | 11,607,777 | **LOST → REBUILT** as `90b5acb8068b45d657418ad56a60d624e841c8f842e7d59ba0be767acc6ca979` (118 files, 11,609,135 B) |
| 6 v1 | `HOC-CUNG-SAM-ROUND-06-2026-09-06.zip` | **`a2e7495ca5467049d9d9efebfeb32cd031bafbf7f256142647e60696e07bedf5`** | 82 | 2,159,003 | **LOST, not rebuilt** — v2 already documents the error v1 recorded |
| 6 v2 | `HOC-CUNG-SAM-ROUND-06-2026-09-06-v2.zip` | **`7d0bea5d28058d4161bda37653f0fa874c8953ae0f8173b9898de6b05f1b51e2`** | 82 | 2,160,729 | **LOST → REBUILT** as `5894c19cb88d9cc1449fb0e35e2c2f58574e05d30c9b537a4bae6dd62875b79d` (83 files, 2,162,078 B) |
| 7 | `HOC-CUNG-SAM-ROUND-07-2026-09-06.zip` | **`1a8db62260807943542d62a0974a1607b4d16a5da2efe3618f436141af33d595`** | 73 | 6,248,822 | **ORIGINAL, intact** |

Every rebuild carries `manifests/REGENERATION-NOTE.md` naming the original's size and hash.

## Status of this registry

**No Founder decision is outstanding.** The question this file originally raised — *«where should
archives of record live?»* — was answered by task order 43: **the repository is the record, and
Desktop ZIPs are review copies.** The registry continues, in its corrected role: it is updated on
every round close so a rebuilt or missing review snapshot can always be told apart from a tampered
one.
