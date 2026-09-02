/// WAL-136 — LessonIndex: mục lục MÔN×BÀI từ DỮ LIỆU THẬT (curriculum-structure
/// 7.626 bài + exercise-case-map), đóng gói assets/pack/lesson-index-g`N`.json
/// (đi cùng chính sách pack: local build, KHÔNG commit — WAL-43).
///
/// Fail-closed: thiếu asset ⇒ trả null — UI nói «chưa có dữ liệu», không bịa.
library;

import 'dart:convert';

import 'package:flutter/services.dart' show rootBundle;

class LessonRef {
  const LessonRef({required this.no, this.title, this.pageStart});
  final int no;

  /// `null` = title miner chưa bắt được tên (29% coverage) — hiển thị «Bài N»,
  /// KHÔNG bịa tên.
  final String? title;
  final int? pageStart;
}

class BookLessons {
  const BookLessons(
      {required this.sourceDocumentId, this.volume, required this.lessons});
  final String sourceDocumentId;
  final String? volume;
  final List<LessonRef> lessons;
}

/// Bài tập THẬT từ corpus (biểu thức + trang in + ca) — qmap-v1.
class CorpusExercise {
  const CorpusExercise(
      {required this.expr, required this.book, this.skillCaseId, this.page});
  final String expr;
  final String book;
  final String? skillCaseId;
  final int? page;
}

class LessonIndex {
  const LessonIndex(
      {required this.grade,
      required this.subjects,
      required this.toanExercises});

  final int grade;
  final Map<String, List<BookLessons>> subjects;
  final Map<int, List<CorpusExercise>> toanExercises;

  List<CorpusExercise> exercisesForToan(int lessonNo) =>
      toanExercises[lessonNo] ?? const [];

  static LessonIndex? fromJsonString(String raw) {
    final Object? j;
    try {
      j = jsonDecode(raw);
    } catch (_) {
      return null;
    }
    if (j is! Map) return null;
    final grade = j['grade'];
    if (grade is! int) return null;
    final subjects = <String, List<BookLessons>>{};
    final sj = j['subjects'];
    if (sj is Map) {
      sj.forEach((k, v) {
        if (v is! List) return;
        subjects['$k'] = [
          for (final b in v.whereType<Map>())
            BookLessons(
              sourceDocumentId: '${b['sourceDocumentId']}',
              // volume có thể là int hoặc String tuỳ nguồn registry — chịu kiểu.
              volume: b['volume'] == null ? null : '${b['volume']}',
              lessons: [
                for (final l in (b['lessons'] as List? ?? const [])
                    .whereType<Map>())
                  if (l['no'] is num)
                    LessonRef(
                        no: (l['no'] as num).toInt(),
                        title: l['title'] as String?,
                        pageStart: (l['pageStart'] as num?)?.toInt()),
              ],
            )
        ];
      });
    }
    final ex = <int, List<CorpusExercise>>{};
    final ej = j['toanExercises'];
    if (ej is Map) {
      ej.forEach((k, v) {
        final no = int.tryParse('$k');
        if (no == null || v is! List) return;
        ex[no] = [
          for (final e in v.whereType<Map>())
            if (e['expr'] is String)
              CorpusExercise(
                  expr: e['expr'] as String,
                  book: '${e['book']}',
                  skillCaseId: e['skillCaseId'] as String?,
                  page: (e['page'] as num?)?.toInt()),
        ];
      });
    }
    return LessonIndex(grade: grade, subjects: subjects, toanExercises: ex);
  }

  /// `null` khi máy này chưa build asset (poc-out chưa có) — hợp lệ, nói thật.
  static Future<LessonIndex?> loadForGrade(int grade) async {
    try {
      final raw =
          await rootBundle.loadString('assets/pack/lesson-index-g$grade.json');
      return fromJsonString(raw);
    } catch (_) {
      return null;
    }
  }
}
