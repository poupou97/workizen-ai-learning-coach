# Structural spot-checks re-run by the archive builder — round 6

The round-6 consolidated report states that its coordinator verified every number first-hand. This
file records the **archive builder** verifying a second time, independently, on **2026-09-06**,
against `origin` and against the artefacts on the Founder's Desktop.

A claim is **PROVEN** here only where the command shown produced the stated result.

---

## 1. GATE C, verified on the artefact itself — **PROVEN**

The Golden #1 fixture (`~/Desktop/wal-evidence/round6-artefacts/fixtures-real/lesson-05-sgk-lich-su-va-dia-li-5-b8.json`,
archived in `evidence/round6-artefacts/`) was parsed directly:

```
sha256(bytes) = a904d0052aa9ff7d0516d99539ac7009d90b1868990a39f6b84da8d7dca91a91
```

**Matches the device MANIFEST's declared fixture hash exactly.** So the file archived here is the
file that was on the phone.

| measured | value |
|---|---|
| blocks | **52** |
| block types | paragraph 18 · **withheld 17** · activity 6 · heading 4 · question 3 · caption 3 · sourceRef 1 |
| trust | `trustedStructuredLesson` 35 · `withheld` 17 |
| `semantic` | **0** |
| `tutorSteps` | **0** (absent) |
| title | **«Đấu tranh giành độc lập thời kì Bắc thuộc»** |

34 served *content* blocks + 1 `sourceRef` = the 35 non-withheld entries, reconciling exactly with
WS-C's «34 served / 17 withheld».

**The Founder's sharp case, `p039:000`, read straight out of the file:**

```
id          05-sgk-lich-su-va-dia-li-5:p039:tc2-p1:000
type        withheld          trust  withheld
reasons     ["agree_tones"]   status WITHHELD
textLen     272               ← and there is NO `text` key on the block
repair.disposition   VALIDATED_REPAIR
repair.method        lanec.tone-corroboration-v1
repair.validatorId   lanec.history-text-validator-v1  (v1)
repair.verdict       validated
repair.changed       false
repair.servable      false
repair.caps          []
```

**Across the whole document:** 6 blocks carry a repair · **6 of 6** disposition `VALIDATED_REPAIR` ·
**6 of 6** `servable: false` · **6 of 6** on type `withheld` · **0** carry a `text` field · **0**
carry any of the forbidden value keys (`proposedValue / text / value / latex / textProjection /
candidate / originalObservations / structuredValue`).

The repair record's complete key set is
`caps · changed · disposition · failureClass · method · repairId · repairVersion · servable ·
structuredKind · supportingLayers · validatorId · validatorVersion · verdict` — **no field that
could carry a proposed value.**

**This is GATE C proved from the artefact rather than from a report: a `ValidatedRepair` crossed
into the LessonDocument, and it did not become trusted.**

**And it independently confirms WS-D's device finding (b):** the *data* says «thời kì **B**ắc
thuộc» with a capital B; the *screen* (frame `round6-04-read-peek.png`) shows «thời kì **b**ắc
thuộc». **The lowercasing is a display-layer defect, not a data defect.**

## 2. `CONNECT ≠ TRUST` enforced in code, not by discipline — **PROVEN**

```
$ git show origin/ws-c/round6-repair-integration:tool/corpus/repair/validated.py | grep -n disposition
167:    disposition = Disposition.VALIDATED_REPAIR          ← a CLASS ATTRIBUTE, not a field
227:    if entry.stage == 'restore' or entry.disposition == Disposition.TRUSTED:   → raises
231:    if entry.disposition != Disposition.VALIDATED_REPAIR:                      → raises
265:    if d.get('disposition') != Disposition.VALIDATED_REPAIR:                   → from_json raises
```

There is no argument, flag or setter that produces `TRUSTED`, and serialisation cannot launder one.

```
$ git show origin/ws-c/…:lib/core/lesson_model/lesson_document.dart | grep -n repair
236:  if (j['repair'] != null) return null;                  ← on a non-withheld block
263:  if (j['repair'] != null && j['type'] != 'withheld') return null;
608:  final ValidatedRepairRef? repair;                      ← the field exists only on WithheldBlock
```

A served block has nowhere to put a repair, and a document that tries is rejected whole.

## 3. The bridge's new carrier reason — **PROVEN**

```
$ git show origin/ws-c/…:tool/corpus/tsl_to_lesson_document.py | grep -n KNOWN_UNCARRIED
112:  KNOWN_UNCARRIED_ROLES = {'formula': 'no_carrier:formula'}
306:  if role in KNOWN_UNCARRIED_ROLES: → withheld_block(..., [KNOWN_UNCARRIED_ROLES[role]], ...)
309:  else: → withheld_block(..., [f'unknown_role:{role}'], ...)
```

`no_carrier:formula` replaces the false `unknown_role:formula`. Round 5's archive recorded
«`ROLE_MAP` has 11 keys, `formula` appears 0 times» — that hole is now **named**, though still not
**servable**.

## 4. The conservation check really fails — **PROVEN (code path)**

```
$ git show origin/ws-a/round6-accounting:tool/corpus/accounting/ledger.py | grep -n 'return 1\|sys.exit'
248:        return 1        ← audit --strict returns non-zero on any UNACCOUNTED region
272:    sys.exit(main())
```

*(The archive builder did **not** execute `ledger.py audit`: it needs the gitignored `poc-out/`
artefacts. The exit path is verified; the 138 → 0 result is **MEASURED by WS-A**, not re-PROVEN
here.)*

## 5. Branch heads and PR state — **PROVEN**

`round6-branch-heads.txt`: **5 of 5** heads recorded in §10.1 of the consolidated report re-resolved
from `origin` and matched. `round6-ci-status.txt`: PRs **#89–#93 all OPEN**, `Analyze & Test =
SUCCESS`, `mergedAt: null`; round 5's **#79–#88** and round 4's **#73** all still OPEN and unmerged.

## 6. Device frames — **PROVEN**

`device-frame-verification.txt`: **7 of 7** frame hashes recomputed and matched the manifest.

## 7. The packs on the phone are the packs archived here — **PROVEN**

All **12** rebuilt pack files hash-match the `packs[]` entries in the device MANIFEST — so the pack
set archived in `evidence/round6-artefacts/packs/` is byte-for-byte the set the GATE E APK carried.

Build provenance, read from `lesson-index-g4.json`:

| | `packs-STALE-before` | `packs` (rebuilt) |
|---|---|---|
| `packVersion` | `g4-20260905T0437Z-07a24504` | `g4-20260906T0424Z-eac69ea1` |
| `builtAt` | 2026-09-05T04:37:51Z | **2026-09-06T04:24:15Z** |
| `gitSha` | `07a24504` | **`eac69ea1`** — the GATE E build commit |
| **`attachmentRule`** | **`capped-toc-v1`** | **`capped-toc-v2`** |

**The `capped-toc-v1 → v2` correction is confirmed first-hand**, and the stale copy is identifiable
as the build round 5's device walk used (its `packVersion` matches the round-5 device manifest).

## 8. The pack rebuild — **41 → 0 CONFIRMED**, and a counting error of mine corrected

**WS-D reports:** activities **248 → 207**, of which **41 `toanExercises` disappeared**
(g4 −26, g5 −15), taking the family from **41 → 0**.

**Measured by the archive builder on the two pack sets archived here — WS-D is exactly right:**

| | `packs-STALE-before` | `packs` (GATE E) | delta |
|---|---:|---:|---:|
| **`toanExercises`** | **41** (g4 **26** · g5 **15**) | **0** | **−41** |
| tvReadings | 66 | 66 | 0 |
| tvWritings | 54 | 54 | 0 |
| khoaExperiments | 46 | 46 | 0 |
| sourceAssets | 36 | 36 | 0 |
| suSources | 4 | 4 | 0 |
| diaMaps | 1 | 1 | 0 |
| **total activities** | **248** | **207** | **−41** |
| files differing by sha256 | — | — | **12 of 12** (every `buildProvenance` stamp changed) |

**It reconciles exactly: 248 − 41 = 207**, and every non-Toán family is unchanged to the item.
**PROVEN, from the bytes inside this archive.**

### The correction, recorded in the open

**My first measurement said 10, and it was wrong.** `toanExercises` is a **dict keyed by lesson
number whose values are lists of expressions** — not a flat list. I called `len()` on it, which
returns the number of **keys**, so I counted **10 lessons and reported them as 10 expressions**:

```
$ python3 -c "import json;d=json.load(open('packs-STALE-before/lesson-index-g4.json'))['toanExercises'];\
  print(type(d).__name__, 'keys', len(d), 'items', sum(len(v) for v in d.values()))"
dict keys 6 items 26          # g4 — I reported 6
                              # g5 — dict keys 4 items 15 — I reported 4
```

**The correct command, and the one to re-run:**

```
python3 - <<'EOF'
import json, glob
def items(v): return sum(len(x) for x in v.values()) if isinstance(v, dict) else len(v or [])
for d in ('packs-STALE-before', 'packs'):
    print(d, sum(items(json.load(open(p)).get('toanExercises') or {})
                 for p in glob.glob(d + '/lesson-index-g*.json')))
EOF
packs-STALE-before 41
packs 0
```

**The `10` and the `217` in my first draft are the same single error**: 217 was the sum of
*container keys* (10 lesson-keys for `toanExercises` + 207 flat entries), not of activities.
**There was never a discrepancy — only my bug.** WS-D's figures were right throughout, and the
archived backup **is** the baseline they measured against.

**And the shape corroborates round 5 independently:** Lane D recorded *«g4 26 expressions across
**6 lessons**, g5 15 across **4 lessons** — 41 in total»*. The archived backup has **exactly 6 and
4 lesson keys**. The two counts describe the same artefact from two sides.

### The provenance observation stands, and now points the other way

The stale copy identifies itself as the **2026-09-05T04:37Z** build
(`packVersion g4-20260905T0437Z-07a24504`, `attachmentRule capped-toc-v1`) — **the same build round
5's device walk used**, per the round-5 device manifest.

With the count corrected, that is no longer a caveat against the 41. **It is a finding:** the APK a
child was shown in round 5 **carried all 41 fabricated expressions**. It makes concrete what the
round-5 archive could only state in prose — *«no APK built on this Mac carries any of this round's
accuracy corrections»* — and it dates the moment they stopped shipping to round 6's GATE E build.

**What is PROVEN, and it is the part that matters to a child:** the packs that shipped in the GATE E
APK carry **zero `toanExercises`**. **The app offers no Toán exercises**, and the 41 that vanished
were the fabricated ones.

---

## What was NOT re-run by the archive builder

- **The suites were not re-executed.** Composition CI (0 conflicts · `flutter analyze` clean ·
  **748 Python** · **1084 Dart**) is **MEASURED by the coordinator** in a throw-away worktree, not
  re-PROVEN here.
- **No recognition, accounting or repair number was recomputed from the corpus.** The ~24 GB corpus
  and `poc-out/` are gitignored and excluded by policy; see `10-OPEN-RISKS-BLOCKERS.md` §6.
- **The device was not touched.** GATE E rests on WS-D's walk and its manifest.
