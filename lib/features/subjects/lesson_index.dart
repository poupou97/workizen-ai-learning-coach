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

/// WAL-144 — đề bài VIẾT thật từ units TV («Viết…», «Dựa vào… viết»).
/// ⭐ Cố ý CHỈ có đề — không trường nào chứa bài mẫu (REVEAL gate của Compose
/// đúng theo cấu trúc dữ liệu, cùng họ LearningActivity.composeChecklist).
class TvWriting {
  const TvWriting(
      {required this.book, required this.lesson, required this.prompt,
      this.page});
  final String book;
  final int lesson;
  final int? page;
  final String prompt;
}

/// WAL-144 #KHTN — khối THÍ NGHIỆM thật từ SGK Khoa học (Chuẩn bị/Tiến hành
/// VERBATIM — không viết lại lời sách; thiếu bước ⇒ không thành object).
class KhoaExperiment {
  const KhoaExperiment(
      {required this.book,
      required this.title,
      required this.chuanBi,
      required this.tienHanh,
      this.subject = 'Khoa học',
      this.page,
      this.lesson,
      this.duDoan,
      this.quanSat});

  /// Môn của khối (Khoa học / Vật lí / Hoá học…) — tile môn nào hiện khối
  /// môn đó, không trộn.
  final String subject;
  final String book;
  final int? page;
  final int? lesson;
  final String title;
  final String chuanBi;
  final List<String> tienHanh;

  /// Câu «Dự đoán…» in trong sách — có nó thì surface phải PREDICT-gate.
  final String? duDoan;
  final String? quanSat;
}

/// WAL-144 #28 — BẢN ĐỒ SGK đã crop (SOURCE_ASSET, human-curation, WAL-43:
/// localResearchOnly — PNG gitignored, bundle local). Câu hỏi VERBATIM.
class DiaMap {
  const DiaMap(
      {required this.subject,
      required this.book,
      required this.asset,
      required this.caption,
      required this.questions,
      required this.pagePdf,
      required this.bboxFrac,
      required this.extractionVersion,
      this.page});
  final String subject;
  final String book;
  final int? page; // trang IN
  final String asset; // tên file trong assets/pack/
  final String caption; // caption in trong sách
  final List<String> questions;

  /// WAL-133 — provenance của CROP: thiếu thì không dựng được `SourceAsset`,
  /// và khi ấy KHÔNG được nói với trẻ «đây là hình trong sách».
  final int pagePdf;
  final List<double> bboxFrac;
  final String extractionVersion;
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
      this.tvWritings = const [],
      this.suSources = const [],
      this.khoaExperiments = const [],
      this.diaMaps = const []});

  final int grade;
  final Map<String, List<BookLessons>> subjects;
  final Map<int, List<CorpusExercise>> toanExercises;
  final List<TvReading> tvReadings;
  final List<TvWriting> tvWritings;
  final List<SuSource> suSources;
  final List<KhoaExperiment> khoaExperiments;
  final List<DiaMap> diaMaps;

  List<CorpusExercise> exercisesForToan(int lessonNo) =>
      toanExercises[lessonNo] ?? const [];

  List<TvReading> readingsForTv(String book, int lessonNo) => [
        for (final r in tvReadings)
          if (r.book == book && r.lesson == lessonNo) r
      ];

  List<TvWriting> writingsForTv(String book, int lessonNo) => [
        for (final w in tvWritings)
          if (w.book == book && w.lesson == lessonNo) w
      ];

  List<SuSource> suSourcesFor(int lessonNo) =>
      [for (final s in suSources) if (s.lesson == lessonNo) s];

  List<DiaMap> mapsForSubject(String subject) =>
      [for (final m in diaMaps) if (m.subject == subject) m];

  List<KhoaExperiment> experimentsForSubject(String subject) =>
      [for (final e in khoaExperiments) if (e.subject == subject) e];

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
    final tw = <TvWriting>[];
    final wj = j['tvWritings'];
    if (wj is List) {
      for (final w in wj.whereType<Map>()) {
        if (w['prompt'] is! String || w['lesson'] is! num) continue;
        tw.add(TvWriting(
            book: '${w['book']}',
            lesson: (w['lesson'] as num).toInt(),
            page: (w['page'] as num?)?.toInt(),
            prompt: w['prompt'] as String));
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
    final ke = <KhoaExperiment>[];
    final kj = j['khoaExperiments'];
    if (kj is List) {
      for (final e in kj.whereType<Map>()) {
        final steps = [
          for (final t in (e['tienHanh'] as List? ?? const []))
            if (t is String) t
        ];
        // thiếu bước tiến hành hoặc title ⇒ KHÔNG phải thí nghiệm dùng được.
        if (e['title'] is! String || steps.isEmpty) continue;
        ke.add(KhoaExperiment(
            subject: '${e['subject'] ?? 'Khoa học'}',
            book: '${e['book']}',
            page: (e['page'] as num?)?.toInt(),
            lesson: (e['lesson'] as num?)?.toInt(),
            title: e['title'] as String,
            chuanBi: '${e['chuanBi'] ?? ''}',
            tienHanh: steps,
            duDoan: e['duDoan'] as String?,
            quanSat: e['quanSat'] as String?));
      }
    }
    final dm = <DiaMap>[];
    final mj = j['diaMaps'];
    if (mj is List) {
      for (final m in mj.whereType<Map>()) {
        final qs = [
          for (final q in (m['questions'] as List? ?? const []))
            if (q is String) q
        ];
        // thiếu asset/caption/câu hỏi ⇒ không phải bản đồ dùng được.
        if (m['asset'] is! String || m['caption'] is! String || qs.isEmpty) {
          continue;
        }
        // ⭐ WAL-133: thiếu provenance crop ⇒ BỎ. Không cắt lại/kiểm chứng
        // được thì không có quyền trình bày như hình trong sách.
        final bbox = [
          for (final v in (m['bboxFrac'] as List? ?? const []))
            if (v is num) v.toDouble()
        ];
        if (m['pagePdf'] is! num ||
            bbox.length != 4 ||
            m['extractionVersion'] is! String) {
          continue;
        }
        dm.add(DiaMap(
            subject: '${m['subject'] ?? 'LS&ĐL'}',
            book: '${m['book']}',
            page: (m['page'] as num?)?.toInt(),
            asset: m['asset'] as String,
            caption: m['caption'] as String,
            questions: qs,
            pagePdf: (m['pagePdf'] as num).toInt(),
            bboxFrac: bbox,
            extractionVersion: m['extractionVersion'] as String));
      }
    }
    return LessonIndex(
        grade: grade,
        subjects: subjects,
        toanExercises: ex,
        tvReadings: tv,
        tvWritings: tw,
        suSources: su,
        khoaExperiments: ke,
        diaMaps: dm);
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
