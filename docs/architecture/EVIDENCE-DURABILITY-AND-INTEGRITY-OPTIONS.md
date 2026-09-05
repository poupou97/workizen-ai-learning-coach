# Evidence durability & integrity — bounded research note (WAL-210 round 3, A4)

**Status: RESEARCH ONLY — PROPOSED. No storage change is made by this note or by the
round-3 A-runtime PR.** Founder A4: *"No big storage change without a Founder decision."*
What the PR does change is listed in §0; everything from §1 on is options with costs,
for the Founder to pick from (or reject).

## 0. What is true today (measured, tests named)

| Property | Today | Held by |
|---|---|---|
| Event ids unique across re-open of the same exercise | yes — `<exerciseId>@<sessionToken>#<seq>` | `test/core/store/evidence_integrity_test.dart` (#60, C1/C2) |
| `appendSession` idempotent by `sessionId` (RAM + disk) | yes — second append = `false`, no rewrite | `evidence_integrity_test.dart` (C3), `test/core/store/evidence_durability_test.dart` (round 3: re-open ×2 + retry) |
| Torn last line does not lose earlier sessions | yes — undecodable lines skipped on load; **kept verbatim on rewrite** (harmless junk line stays in the file) | `file_store_test.dart:78`, `evidence_durability_test.dart` (round 3: 2 sessions + torn 3rd + append 4th → 3 sessions after reopen) |
| Second open of the same exercise is counted | yes (no silent dedupe) | `evidence_durability_test.dart` |
| Validator stamp (A3) survives disk | yes — JSON key `validation` | `evidence_durability_test.dart` |
| Write strategy | **whole-file rewrite** on every mutation (`FileLearnerStore._flush` → `writeAsString(..., flush: true)`) | `lib/core/store/file_store.dart:29-32` |
| Crash window | the whole file, not the last line: `writeAsString` truncates then writes; a crash between truncate and flush leaves an **empty or partial file** — every earlier session is lost | audit 04 §C.2(6); no test can hold this (it needs a fault injector) |
| Tamper detection | none — a hand-edited line replays silently | audit C9 |
| Size | ~250 B/event, ~250 KB / learner / school-year (WAL-95 measurement) | — |

The two open risks are therefore: **(R1) durability** — one crash mid-flush can erase a
learner's whole history; **(R2) integrity** — nothing detects an edited/removed line, so a
parent-facing claim can be changed by editing a file.

## 1. Durability options (append-on-disk)

| # | Option | Mechanism | Crash safety | Cost | Migration |
|---|---|---|---|---|---|
| D1 | **Atomic rewrite** (write temp → fsync → rename over) | keep whole-file model; `File.writeAsString` to `store.jsonl.tmp`, then `rename` | POSIX rename is atomic: reader sees old *or* new file, never a torn one. Loses at most the **last** mutation. | ~10 lines in `FileLearnerStore._flush`; one extra file op per mutation; no format change | none — same on-disk format; old files load unchanged |
| D2 | **True append** (`FileMode.append` for sessions) | `appendSession` appends one line + `flush`; profile/timetable/pin records also append (they are already last-wins) | A crash can only tear the **line being written**; earlier lines untouched. Torn last line already tolerated by the reader. | `_flush` becomes append-only for the append-only record types; `deleteLearner` (the one non-append operation) still rewrites via D1 | none for reads; write path changes; `toJsonl()` no longer the writer |
| D3 | D1 + D2 combined | append normally, atomic rewrite only for delete | best of both | D1 + D2 | none |
| D4 | SQLite / WAL-mode DB | move learner store to `sqlite3` (already a dependency for packs) | journaled | schema + migration + native dep in the learner path (today pure Dart, tests run anywhere) | **breaking**: format change, export/delete rewrite, privacy boundary re-check (ADR-006) |

**Recommendation to put before the Founder (not adopted):** D3. It is ~40 lines, keeps the
JSONL format, keeps `JsonlLearnerStore` as the single source of rules, and removes R1
entirely except for the line in flight. D4 is not justified by size (250 KB/year).

## 2. Integrity options (tamper strategy)

| # | Option | What it detects | What it does NOT detect | Cost | Privacy/notes |
|---|---|---|---|---|---|
| I1 | **Per-line content hash** (`"h": sha256(line-without-h)`) | accidental corruption, a hand-edited line | a deleted line; a re-generated line by someone who knows the scheme | compute on write, verify on load; ~70 B/line | no key |
| I2 | **Per-line hash chain** (`h_n = sha256(h_{n-1} ‖ line_n)`) | edits **and** deletions/reorders anywhere but the tail; truncation is visible as a broken chain | tail truncation (last k lines removed) — unless the head is anchored elsewhere | as I1 + chain state; `deleteLearner` (a legitimate removal, NĐ13) must **re-chain** — the one operation that legitimately rewrites history | no key; the chain head could be shown in the parent "about" page as a fingerprint |
| I3 | **HMAC per line** with a device-held key | edits by anyone without the key | edits by the app itself / anyone with the device (the threat model here is "curious parent edits a file", not an attacker) | needs a key store (Keychain/Keystore) — new platform surface | key loss = whole history "unverified"; must define what the app says then |
| I4 | **Signed checkpoints** (periodic hash of the whole log, kept in a second file / export) | offline audit of a whole export | nothing in-app | cheap | pairs well with `exportLearner` (NĐ13 export) |

**What a detection triggers** is the real decision, not the algorithm: a line that fails
verification must be **dropped from replay and reported** ("SAM không đọc được N bản
ghi") — never repaired, never silently trusted. That rule is the same fail-closed rule the
reader already applies to undecodable JSON, so I1/I2 slot into the existing `_records`
skip path.

**Recommendation to put before the Founder (not adopted):** I2 on top of D3, with
`deleteLearner` re-chaining and a visible chain fingerprint. Cost is ~120 lines + tests;
no key management; detects every tamper except tail truncation, which D2 already makes
the only crash-shaped failure mode.

## 3. Migration path (if D3 + I2 are chosen)

1. Reader accepts lines with or without `h` (old files load unchanged) — one release.
2. Writer appends with `h`; on first open of an old file, **do not** rewrite it; start the
   chain at the first new line (chain head = hash of the last legacy line).
3. `exportLearner` includes `h`; `deleteLearner` rewrites the survivors' chain.
4. A test that a mixed legacy+chained file loads, verifies the chained suffix, and reports
   the legacy prefix as "unverified (pre-chain)" — never as "tampered".

## 4. Not in this note

Cloud sync, multi-device merge, encryption at rest (platform default on Android/iOS
covers the device-loss case), and any change to the learner data schema. Each is a
Founder decision with privacy consequences (ADR-006, NĐ13/2023).
