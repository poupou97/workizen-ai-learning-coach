# Structural spot-checks re-run by the archive builder

**Purpose.** The round-5 consolidated report states that its coordinator re-verified certain
load-bearing claims first-hand rather than relaying a lane's summary. This file records the
archive builder re-running that verification a second time, independently, on **2026-09-06**,
against the working checkout (branch `ws-d/round6-golden-delivery`, i.e. the round-6 base which
composes all nine round-5 lane branches).

A claim is marked **PROVEN** only where the command below produced the stated result.

---

## 1. A single unrecognised block kind rejects the entire LessonDocument — **PROVEN**

```
$ sed -n '1015,1020p' lib/core/lesson_model/lesson_document.dart
    final blocks = <LessonBlock>[];
    for (final b in (j['blocks'] as List? ?? const []).whereType<Map>()) {
      final blk = LessonBlock.fromJson(b.cast<String, Object?>());
      if (blk == null) return null; // một block hỏng ⇒ không tài liệu nửa vời
      blocks.add(blk);
    }
```

Matches the report (`lesson_document.dart:1017-1018`). This is deliberate fail-closed design.
Its consequence is a forward-compatibility constraint: **a pack that emits a new block kind
blanks the lesson on an older app — packs and app must ship together.**

## 2. The TSL→LessonDocument bridge has no `formula` role — **PROVEN**

```
$ grep -c "formula" tool/corpus/tsl_to_lesson_document.py
0
```

`ROLE_MAP` holds exactly 11 keys — `heading · body · attribution · caption · question ·
objective · instruction · sidebar · stage_label · table` plus the mapping comment — and **none of
them is `formula`**. The file's own comment states the consequence: "Roles absent here are NOT
guessed: they are withheld with reason `unknown_role:<role>`".

**A validated `MathExpression` has no path from corpus to app today.**

*(Note: the report cites this file as `tool/corpus/tsl_to_lesson_document.py:71-82` and records
that Lane A2 had mis-cited it as `tool/ui/…`. The `tool/corpus/…` path is correct.)*

## 3. The app has no rich-text capability at all — **PROVEN**

```
$ grep -rl "RichText\|TextSpan\|Text.rich" lib/ | wc -l
0
$ find lib -name "*.dart" | wc -l
161
```

**0 of 161** Dart files on this checkout contain any rich-text construct. The report measured
**0 of 147** on the round-5 base; the count of Dart files has grown since, and the number of
rich-text files is still zero. **A superscript or a fraction cannot render correctly even when
the data is right.**

## 4. All nine lane branch heads — **PROVEN, 9 of 9 match**

See `round5-branch-heads.txt`. Every head recorded in §11.3 of the consolidated report was
re-resolved from `origin` and matched exactly.

## 5. All ten round-5 PRs open, CI green, none merged — **PROVEN**

See `round5-pull-requests.json` (`mergedAt: null` on all ten, `state: OPEN`) and
`round5-ci-status.txt` (`Analyze & Test = SUCCESS` on all ten).

## 6. Device evidence — 36 frames, hashes recomputed — **PROVEN**

See `device-frame-verification.txt`. All 36 frame hashes recomputed from the repository copy and
matched the manifest; the copies under `~/Desktop/wal-evidence` are byte-identical to the
repository copies; steps `PASS 28 / FAIL 0 / SKIP 0 / UNVERIFIED 0`, `downgraded 0`, 5 iterations.

## 7. R13 corrected served share — **cross-checked in a second committed document**

The consolidated report's §8.2 figures (0.632 → 0.589 evaluation, 0.613 → 0.523 holdout) are
independently present in `docs/research/DATA-ACCURACY-SCOREBOARD-LANE-D.md` lines 78–79, which
also records the silent-loss counts as `27 of 394 extracted = 0.069` (batch 2) and
`55 of 375 = 0.147` (holdout). Two committed documents agree.

---

## What was NOT re-run by the archive builder

- **The test suites were not re-executed.** The composed-round counts (623 Python / 1061 Dart /
  `flutter analyze` clean, 0 conflicts) are taken from the coordinator's throw-away-worktree run
  as recorded in §11.3. Re-running them would require rebuilding that worktree. **Status:
  MEASURED (by the coordinator), not re-PROVEN by the archive builder.**
- **No metric was recomputed from the corpus.** The ~20 GB corpus and the `poc-out/` artefacts are
  gitignored and are **not** included in this archive. See `10-OPEN-RISKS-BLOCKERS.md` §6 for
  reproduction instructions.
