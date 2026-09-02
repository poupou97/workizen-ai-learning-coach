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

/// WAL-113 B1 — bài ĐỌC-HIỂU thật từ units TV: đoạn văn verbatim + câu hỏi.
/// ⭐ SGK KHÔNG in đáp án ⇒ cố ý KHÔNG có trường đáp án/option nào — tầng UI
/// không thể chấm dù muốn (UNKNOWN ≠ SAI đúng theo CẤU TRÚC dữ liệu).
class TvQuestion {
  const TvQuestion({required this.prompt, this.page});
  final String prompt;
  final int? page;
}

class TvReading {
  const TvReading(
      {required this.book,
      required this.lesson,
      required this.passage,
      required this.questions,
      this.page});
  final String book;
  final int lesson;
  final int? page; // trang IN của đoạn văn

  /// Nguyên văn SECTION_TEXT từ units — textbookVerbatim, không viết lại.
  final String passage;
  final List<TvQuestion> questions;
}

/// WAL-113 B2 — khối «TƯ LIỆU.» nguyên văn từ SGK Sử-Địa (ocr-body).
/// [samGloss] là DIỄN GIẢI CỦA SAM (curated, systemDerived) — UI bắt buộc dán
/// nhãn riêng, KHÔNG BAO GIỜ trình bày như lời của nguồn.
class SuSource {
  const SuSource(
      {required this.book,
      required this.excerpt,
      required this.attribution,
      this.page,
      this.lesson,
      this.lessonTitle,
      this.samGloss});
  final String book;
  final int? page;
  final int? lesson;
  final String? lessonTitle;
  final String excerpt;
  final String attribution;
  final String? samGloss;
}

class LessonIndex {
  const LessonIndex(
      {required this.grade,
      required this.subjects,
      required this.toanExercises,
      this.tvReadings = const [],
      this.suSources = const []});

  final int grade;
  final Map<String, List<BookLessons>> subjects;
  final Map<int, List<CorpusExercise>> toanExercises;
  final List<TvReading> tvReadings;
  final List<SuSource> suSources;

  List<CorpusExercise> exercisesForToan(int lessonNo) =>
      toanExercises[lessonNo] ?? const [];

  List<TvReading> readingsForTv(String book, int lessonNo) => [
        for (final r in tvReadings)
          if (r.book == book && r.lesson == lessonNo) r
      ];

  List<SuSource> suSourcesFor(int lessonNo) =>
      [for (final s in suSources) if (s.lesson == lessonNo) s];

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
    final tv = <TvReading>[];
    final tj = j['tvReadings'];
    if (tj is List) {
      for (final r in tj.whereType<Map>()) {
        if (r['passage'] is! String || r['lesson'] is! num) continue;
        tv.add(TvReading(
            book: '${r['book']}',
            lesson: (r['lesson'] as num).toInt(),
            page: (r['page'] as num?)?.toInt(),
            passage: r['passage'] as String,
            questions: [
              for (final q
                  in (r['questions'] as List? ?? const []).whereType<Map>())
                if (q['prompt'] is String)
                  TvQuestion(
                      prompt: q['prompt'] as String,
                      page: (q['page'] as num?)?.toInt()),
            ]));
      }
    }
    final su = <SuSource>[];
    final uj = j['suSources'];
    if (uj is List) {
      for (final e in uj.whereType<Map>()) {
        // thiếu excerpt hoặc attribution ⇒ KHÔNG phải tư liệu dùng được — bỏ.
        if (e['excerpt'] is! String || e['attribution'] is! String) continue;
        su.add(SuSource(
            book: '${e['book']}',
            page: (e['page'] as num?)?.toInt(),
            lesson: (e['lesson'] as num?)?.toInt(),
            lessonTitle: e['lessonTitle'] as String?,
            excerpt: e['excerpt'] as String,
            attribution: e['attribution'] as String,
            samGloss: e['samGloss'] as String?));
      }
    }
    return LessonIndex(
        grade: grade,
        subjects: subjects,
        toanExercises: ex,
        tvReadings: tv,
        suSources: su);
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
