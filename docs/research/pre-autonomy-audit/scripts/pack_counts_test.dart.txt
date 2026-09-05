// Pre-autonomy audit — Scale path reach: parse the REAL built packs
// (main checkout assets/pack/lesson-index-g*.json, gitignored) through the
// production parser `LessonIndex.fromJsonString` and count what a child can open.
// Run: flutter test poc-out/audit/pre-autonomy/scripts/pack_counts_test.dart
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/knowledge/slice_curriculum.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';

const packDir = '/Users/alexnguyen/projects/workizen-ai-learning-coach/assets/pack';

void main() {
  test('AUDIT pack counts per grade (Scale path) vs SliceCurriculum (Deep path)', () {
    var totalLessons = 0, totalOpenable = 0, totalDeep = 0;
    final rows = <String>[];
    for (var g = 1; g <= 12; g++) {
      final f = File('$packDir/lesson-index-g$g.json');
      if (!f.existsSync()) {
        rows.add('| $g | (pack missing) | | | | | |');
        continue;
      }
      final idx = LessonIndex.fromJsonString(f.readAsStringSync());
      if (idx == null) {
        rows.add('| $g | (parse failed) | | | | | |');
        continue;
      }
      var lessons = 0, openable = 0, deep = 0;
      final byKind = <String, int>{};
      for (final books in idx.subjects.values) {
        for (final b in books) {
          for (final l in b.lessons) {
            lessons++;
            final acts = idx.activitiesFor(book: b.sourceDocumentId, lessonNo: l.no);
            if (acts.isNotEmpty) openable++;
            for (final a in acts) {
              final k = a.runtimeType.toString();
              byKind[k] = (byKind[k] ?? 0) + 1;
            }
            final key = LessonKey(sourceDocumentId: b.sourceDocumentId, number: l.no, pageStart: l.pageStart);
            if (curriculumForLesson(key) != null) deep++;
          }
        }
      }
      totalLessons += lessons;
      totalOpenable += openable;
      totalDeep += deep;
      final profile = LearnerProfile(learnerId: 'x', displayName: 'x', grade: g);
      rows.add('| $g | ${idx.books.length} | ${idx.subjects.length} | $lessons | $openable | $deep (curriculaForLearner=${curriculaForLearner(profile).length}) | ${byKind.entries.map((e) => '${e.key}=${e.value}').join(', ')} |');
    }
    final out = StringBuffer()
      ..writeln('| grade | books (shelf) | subjects | lessons (TOC) | openable lessons (activitiesFor≠∅) | Deep-path lessons (curriculumForLesson) | activities by kind |')
      ..writeln('|---|---|---|---|---|---|---|');
    rows.forEach(out.writeln);
    out.writeln('| **total** | | | **$totalLessons** | **$totalOpenable** | **$totalDeep** | |');
    print(out);
    File('/Users/alexnguyen/projects/workizen-ai-learning-coach/.claude/worktrees/agent-a06286097eebb4e5f/poc-out/audit/pre-autonomy/scripts/pack_counts.out')
        .writeAsStringSync(out.toString());
  });
}
