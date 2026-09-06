# Per-round archive registry — identities of record

**Why this file exists.** On 2026-09-06 four of the five per-round Desktop archives
**disappeared** — rounds 4, 5, 6-v1 and 6-v2 — while `~/Desktop/wal-evidence/` beside them was
untouched. They were not in the Trash, not offloaded to iCloud (the container is an empty 2021
leftover, Desktop is a local directory, no `.icloud` stubs), and not anywhere else under the home
directory. **I cannot attribute a cause and will not speculate about one.**

Two were rebuilt because their build inputs happened to still exist in a **session-scoped
scratchpad that is wiped when the session rolls**. That is luck, not a process.

**A rebuild restores the contents, not the identity.** A regenerated ZIP is never byte-identical —
the manifest records build time and commit — so its hash cannot match what was published. Without
this registry, a later reader comparing a rebuilt archive against a hash quoted in an old report
would see a mismatch and reasonably conclude tampering.

**The ZIPs themselves cannot live in git**: they contain verbatim SGK page images, which are
INTERNAL / RESEARCH ONLY under D4, and they are large. This registry holds their *identities* so
that a loss costs the bytes and not the provenance.

| Round | Filename | Original sha256 | Files | Bytes | Status |
|---|---|---|---|---|---|
| 4 | `ROUND4-REPORT` ×2 (pre-format) | `bf0d27a9…` | — | — | **LOST, NOT RECOVERABLE.** Source of record is in git and inside the round-5 archive |
| 5 | `HOC-CUNG-SAM-ROUND-05-2026-09-06.zip` | **`30f2912cd165c5b9bf67ea32ab427c92a97282714356effe657e748eb8a77a4c`** | 117 | 11,607,777 | **LOST → REBUILT** as `90b5acb8068b45d657418ad56a60d624e841c8f842e7d59ba0be767acc6ca979` (118 files, 11,609,135 B) |
| 6 v1 | `HOC-CUNG-SAM-ROUND-06-2026-09-06.zip` | **`a2e7495ca5467049d9d9efebfeb32cd031bafbf7f256142647e60696e07bedf5`** | 82 | 2,159,003 | **LOST, not rebuilt** — v2 already documents the error v1 recorded |
| 6 v2 | `HOC-CUNG-SAM-ROUND-06-2026-09-06-v2.zip` | **`7d0bea5d28058d4161bda37653f0fa874c8953ae0f8173b9898de6b05f1b51e2`** | 82 | 2,160,729 | **LOST → REBUILT** as `5894c19cb88d9cc1449fb0e35e2c2f58574e05d30c9b537a4bae6dd62875b79d` (83 files, 2,162,078 B) |
| 7 | `HOC-CUNG-SAM-ROUND-07-2026-09-06.zip` | **`1a8db62260807943542d62a0974a1607b4d16a5da2efe3618f436141af33d595`** | 73 | 6,248,822 | **ORIGINAL, intact** |

Every rebuild carries `manifests/REGENERATION-NOTE.md` naming the original's size and hash.

## Founder decision needed

**Per-round Desktop archives are the archive of record (permanent rule, Part VII) and they are
not backed up.** Two of five survived, by luck. Options:

1. **Durable location** — keep archives outside `~/Desktop` in a backed-up or versioned store.
2. **Registry only** — accept that ZIPs may be lost, and treat this file as the identity of
   record. Cheap; loses the evidence bodies.
3. **Both** — this registry regardless, plus a durable store.

Until decided, **this registry is committed on every round close**, so a lost archive costs its
bytes and not its identity.
