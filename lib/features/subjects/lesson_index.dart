/// WAL-136 — LessonIndex: mục lục MÔN×BÀI từ DỮ LIỆU THẬT (curriculum-structure
/// 7.626 bài + exercise-case-map), đóng gói assets/pack/lesson-index-g`N`.json
/// (đi cùng chính sách pack: local build, KHÔNG commit — WAL-43).
///
/// Fail-closed: thiếu asset ⇒ trả null — UI nói «chưa có dữ liệu», không bịa.
library;

import 'dart:convert';

import '../../core/assets/learning_asset.dart';

import 'package:flutter/services.dart' show rootBundle;

class LessonRef {
  const LessonRef({required this.no, this.title, this.pageStart});
  final int no;

  /// `null` = title miner chưa bắt được tên (29% coverage) — hiển thị «Bài N»,
  /// KHÔNG bịa tên.
  final String? title;
  final int? pageStart;
}

/// Bỏ bản ghi TRÙNG HỆT (cùng số, cùng tên, cùng trang in) trong một cuốn.
///
/// Đo trên pack lớp 5: 7/251 bản ghi như vậy ở GDTC, LS&ĐL, Tin học — trẻ thấy
/// «Bài 1» hai dòng liền nhau, không dòng nào nói thêm điều gì. Bỏ một bản ghi
/// KHÔNG mất thông tin nào vì hai bản ghi giống nhau từng trường.
///
/// ⭐ Cố ý KHÔNG gộp theo số bài: GDTC đánh số LẠI theo từng chủ đề nên có 5
/// bài mang số 1, mỗi bài một tên và một trang khác nhau — đó là cấu trúc THẬT
/// của cuốn sách, không phải lỗi. Gộp theo số là xoá bài của trẻ.
List<LessonRef> _dedupeLessons(List<LessonRef> ls) {
  final seen = <String>{};
  return [
    for (final l in ls)
      if (seen.add('${l.no}|${l.title}|${l.pageStart}')) l,
  ];
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
  const TvQuestion({required this.prompt, this.page, this.options = const []});
  final String prompt;
  final int? page;

  /// WAL-204 — lựa chọn A/B/C/D do pattern router tách từ SGK. Cố ý KHÔNG có
  /// trường đáp án: có options mà không có chìa khoá ⇒ Reader chạy chế độ chọn
  /// KHÔNG chấm (correct=null). Chấm chỉ khi một bước sau nối được SGV.
  final List<String> options;
}

class TvReading {
  const TvReading(
      {required this.book,
      required this.lesson,
      required this.passage,
      required this.questions,
      this.page,
      this.source});
  final String book;
  final int lesson;
  final int? page; // trang IN của đoạn văn

  /// WAL-210 — nguồn TRÍCH XUẤT của bài đọc như builder ghi (`null` = miner
  /// mặc định; `pattern-router-*` = thử nghiệm WAL-204/206). Chỉ để guard +
  /// audit, không để hiển thị.
  final String? source;

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
      this.page, this.source});
  final String book;
  final int lesson;
  final int? page;
  final String prompt;

  /// WAL-210 — như [TvReading.source].
  final String? source;
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

/// ⭐ WAL-210 (audit B.6 §4 + top-gap #3 «no build provenance») — PROVENANCE
/// CỦA CHÍNH PACK: builder nào, commit nào, cờ nào, có phải bản thử nghiệm.
///
/// Hợp đồng chia sẻ với lane Python (`tool/ui/build_lesson_index.py` ghi vào
/// `assets/pack/lesson-index-g{N}.json`, khoá đỉnh `"buildProvenance"`):
/// `{"schema": 1, "builderVersion", "gitSha", "builtAt": ISO-8601, "grade",
///   "flags": {"PATTERN_ROUTER": "0|1", "UNITS_SOURCE", "ROUTE_EXPLAIN": "0|1"},
///   "experimental": bool, "attachmentRule": "capped-toc-v1",
///   "contentHash": sha256(pack không có field này),
///   "packVersion": "grade-builtAtCompact-sha8"}` (vd `g6-20260905T1200-abcdef12`).
///
/// Fail-closed: thiếu/khuyết/sai kiểu bất kỳ trường BẮT BUỘC nào (`schema`,
/// `packVersion`, `experimental`) ⇒ `null` — pack cũ vẫn dùng được, chỉ
/// KHÔNG có version để đóng lên evidence (emitter rơi về hằng cũ) và KHÔNG
/// được coi là bản thử nghiệm.
class BuildProvenance {
  const BuildProvenance({
    required this.schema,
    required this.packVersion,
    required this.experimental,
    this.builderVersion,
    this.gitSha,
    this.builtAt,
    this.grade,
    this.flags = const {},
    this.attachmentRule,
    this.contentHash,
  });

  final int schema;

  /// Chuỗi đóng lên `LearningEvent.knowledgeVersion` của đường Scale.
  final String packVersion;

  /// `true` = pack dựng với cờ thử nghiệm (vd pattern router) — nội dung
  /// router chỉ được hiện khi pack TỰ khai điều này (item F, PR-C).
  final bool experimental;
  final String? builderVersion;
  final String? gitSha;
  final DateTime? builtAt;
  final int? grade;
  final Map<String, String> flags;
  final String? attachmentRule;
  final String? contentHash;

  static BuildProvenance? fromJson(Object? j) {
    if (j is! Map) return null;
    final schema = j['schema'], version = j['packVersion'],
        experimental = j['experimental'];
    if (schema is! int || version is! String || version.trim().isEmpty ||
        experimental is! bool) {
      return null;
    }
    final flags = <String, String>{};
    final fj = j['flags'];
    if (fj is Map) {
      fj.forEach((k, v) {
        if (v != null) flags['$k'] = '$v';
      });
    }
    final built = j['builtAt'];
    return BuildProvenance(
      schema: schema,
      packVersion: version,
      experimental: experimental,
      builderVersion: j['builderVersion'] as String?,
      gitSha: j['gitSha'] as String?,
      builtAt: built is String ? DateTime.tryParse(built) : null,
      grade: (j['grade'] as num?)?.toInt(),
      flags: flags,
      attachmentRule: j['attachmentRule'] as String?,
      contentHash: j['contentHash'] as String?,
    );
  }
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
      this.page,
      this.lesson});
  final String subject;
  final String book;
  final int? page; // trang IN

  /// WAL-210 — số bài IN mà bản đồ thuộc về; pack hôm nay chưa ghi (`null`)
  /// ⇒ sự kiện Map không có `lessonNo` và KHÔNG hiện trên Learning Map —
  /// không đoán từ trang.
  final int? lesson;
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

/// WAL-133 — hình SGK đã crop, mang ĐỦ provenance để dựng `SourceAsset`.
/// Thiếu một mảnh nào là tầng parse loại thẳng — không có object nửa vời.
class IndexedSourceAsset {
  const IndexedSourceAsset(
      {required this.subject,
      required this.assetType,
      required this.asset,
      required this.sourceDocumentId,
      required this.pagePdf,
      required this.bboxFrac,
      required this.extractionVersion,
      this.pagePrinted,
      this.printedCaption,
      this.samGloss,
      this.lesson});

  final String subject;

  /// MAP / FIGURE / EXPERIMENT / PORTRAIT… — dùng để xếp chỗ, không để claim.
  final String assetType;
  final String asset;
  final String sourceDocumentId;
  final int pagePdf;
  final int? pagePrinted;
  final List<double> bboxFrac;
  final String extractionVersion;
  final String? printedCaption;
  final String? samGloss;
  final int? lesson;

  SourceAsset toAsset() => SourceAsset(
        path: 'assets/pack/$asset',
        sourceDocumentId: sourceDocumentId,
        pagePdf: pagePdf,
        pagePrinted: pagePrinted,
        bboxFrac: bboxFrac,
        extractionVersion: extractionVersion,
        printedCaption: printedCaption,
        samGloss: samGloss,
      );
}

/// ⭐ WAL-167 — MỘT CUỐN SÁCH có thật, kèm bìa thật.
///
/// Trẻ nhận ra sách bằng BÌA trước khi đọc được tên môn. Bìa là trang 1 của
/// PDF nên trích được tự động cho cả 531 cuốn — khác hẳn hình trong ruột sách
/// (phải có người chấm khung cắt).
///
/// `title` dựng từ TRƯỜNG CÓ THẬT trong registry (môn + lớp), KHÔNG đọc chữ
/// trên bìa: OCR bìa sai một chữ là gọi sai tên sách của trẻ.
class BookRef {
  /// Thư mục bìa, tính từ `assets/pack/`. Phải TRÙNG một dòng trong
  /// `pubspec.yaml`: Flutter khai báo asset theo THƯ MỤC và **không đệ quy**,
  /// nên bìa để ngoài thư mục đã khai báo là ảnh không bao giờ dựng được trên
  /// máy thật — dù file nằm sờ sờ trên đĩa (WAL-167 n89).
  static const String coverDir = 'covers/';

  const BookRef({
    required this.sourceDocumentId,
    required this.subject,
    required this.title,
    required this.cover,
    required this.lessonCount,
    this.volumeLabel,
    this.volume,
    this.bookSeries,
    this.pageCount,
  });

  final String sourceDocumentId;
  final String subject;
  final String title;

  /// Đường dẫn trong `assets/pack/` — bìa là SOURCE_ASSET (WAL-43: không commit).
  final String cover;
  final int lessonCount;

  /// «Tập 1» — `null` khi sách không chia tập.
  final String? volumeLabel;

  /// Số tập để XẾP THỨ TỰ. Không có thì `null` — không đoán từ tên file:
  /// `tap-hai` xếp trước `tap-mot` theo bảng chữ cái là đúng chuỗi, sai sách.
  final int? volume;

  /// ⭐ Bộ sách (Kết nối tri thức / Chân trời sáng tạo / Cánh Diều).
  /// Registry chưa có trường này ⇒ hiện luôn `null`. Giữ CHIỀU DỮ LIỆU để
  /// không khoá kiến trúc vào «chỉ tồn tại một bộ sách», nhưng KHÔNG bịa giá
  /// trị và KHÔNG dựng UI chọn bộ khi chưa có nhu cầu thật (Founder Delta §3).
  final String? bookSeries;
  final int? pageCount;
}

/// ⭐ WAL-166 — MỘT VIỆC trẻ có thể làm trong một bài, **không hỏi tên môn**.
///
/// Trước đây màn Subject Home quyết định bài có mở được không bằng
/// `_isToan/_isTv/_isSu`: môn nào không nằm trong ba tên tiếng Việt đó thì dù
/// pack CÓ dữ liệu vẫn không bấm được. Đo trên pack lớp 5 thật: Khoa học có
/// 5 thí nghiệm và Tiếng Anh là môn lớn nhất corpus, cả hai đều không có
/// đường vào.
///
/// Nay câu hỏi đổi thành «bài này CÓ việc gì không», và câu trả lời đến từ
/// DỮ LIỆU. `sealed` ⇒ thêm loại việc mới là mọi chỗ tiêu thụ đỏ ngay.
sealed class LessonActivity {
  const LessonActivity();
}

final class ExerciseActivity extends LessonActivity {
  const ExerciseActivity(this.items);
  final List<CorpusExercise> items;
}

final class ReadingActivity extends LessonActivity {
  const ReadingActivity(this.reading);
  final TvReading reading;
}

final class WritingActivity extends LessonActivity {
  const WritingActivity(this.writing);
  final TvWriting writing;
}

final class SourceActivity extends LessonActivity {
  const SourceActivity(this.source);
  final SuSource source;
}

final class ExperimentActivity extends LessonActivity {
  const ExperimentActivity(this.experiment);
  final KhoaExperiment experiment;
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
      this.diaMaps = const [],
      this.sourceAssets = const [],
      this.books = const [],
      this.buildProvenance,
      this.droppedRouterActivities = 0});

  final int grade;

  /// WAL-210 — `null` = pack chưa khai provenance (pack cũ / chưa dựng lại).
  final BuildProvenance? buildProvenance;

  /// ⭐ WAL-210 item F — DEFAULT-BUILD GUARD: số mục có `source` bắt đầu bằng
  /// `pattern-router` đã bị LOẠI lúc parse vì pack không tự khai
  /// `buildProvenance.experimental == true`. Một APK dựng từ pack thử nghiệm
  /// trên máy dev (WAL-206 variant) không thể lặng lẽ đưa nội dung router tới
  /// trẻ — pack phải NÓI RA nó là bản thử nghiệm. Lộ ra để test đếm.
  final int droppedRouterActivities;

  /// ⭐ WAL-210 item G2 — số BÀI (sách, số bài) có ít nhất một việc trẻ làm
  /// được — con số THẬT để Home nói «Có N bài để học ở Môn học» thay vì
  /// «chưa có nội dung» với lớp chưa có chương trình sư phạm.
  int get openableLessonCount {
    final seen = <String>{};
    for (final books in subjects.values) {
      for (final b in books) {
        for (final l in b.lessons) {
          final key = '${b.sourceDocumentId}|${l.no}';
          if (seen.contains(key)) continue;
          if (activitiesFor(book: b.sourceDocumentId, lessonNo: l.no)
              .isNotEmpty) {
            seen.add(key);
          }
        }
      }
    }
    return seen.length;
  }

  /// Version để đóng lên evidence của đường Scale; `null` khi chưa khai —
  /// emitter rơi về hằng cũ, không bịa version.
  String? get packVersion => buildProvenance?.packVersion;

  final Map<String, List<BookLessons>> subjects;
  final Map<int, List<CorpusExercise>> toanExercises;
  final List<TvReading> tvReadings;
  final List<TvWriting> tvWritings;
  final List<SuSource> suSources;
  final List<KhoaExperiment> khoaExperiments;
  final List<DiaMap> diaMaps;
  final List<IndexedSourceAsset> sourceAssets;
  final List<BookRef> books;

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

  List<BookRef> booksForSubject(String subject) =>
      [for (final b in books) if (b.subject == subject) b];

  BookRef? bookById(String id) {
    for (final b in books) {
      if (b.sourceDocumentId == id) return b;
    }
    return null;
  }

  /// ⭐ WAL-166 — mọi việc gắn được vào MỘT bài của MỘT cuốn sách.
  ///
  /// Lọc theo `book` ở mọi loại — kể cả tư liệu Sử, thứ trước đây chỉ lọc
  /// theo số bài nên bài số 9 của sách khác có thể lôi nhầm tư liệu.
  List<LessonActivity> activitiesFor(
      {required String book, required int lessonNo}) {
    final ex = [
      for (final e in exercisesForToan(lessonNo))
        if (e.book == book) e
    ];
    return [
      if (ex.isNotEmpty) ExerciseActivity(ex),
      for (final r in readingsForTv(book, lessonNo)) ReadingActivity(r),
      for (final w in writingsForTv(book, lessonNo)) WritingActivity(w),
      for (final s in suSources)
        if (s.book == book && s.lesson == lessonNo) SourceActivity(s),
      for (final e in khoaExperiments)
        if (e.book == book && e.lesson == lessonNo) ExperimentActivity(e),
    ];
  }

  /// ⭐ WAL-210 round 3 (#7, Lane B yêu cầu): hình của MÔN này VÀ của SÁCH
  /// THUỘC LỚP này. Trước đây chỉ lọc theo môn ⇒ Toán 6 trưng hình Toán 5.
  /// Một hình thuộc lớp khi (a) sách của nó nằm trên giá của pack (`books`),
  /// hoặc (b) định danh sách mang tiền tố lớp `NN-` khớp `grade`. Không
  /// chứng minh được ⇒ bỏ (fail closed), không đoán.
  List<IndexedSourceAsset> sourceAssetsFor(String subject) => [
        for (final a in sourceAssets)
          if (a.subject == subject && _belongsToThisGrade(a.sourceDocumentId))
            a
      ];

  bool _belongsToThisGrade(String sourceDocumentId) {
    if (books.any((b) => b.sourceDocumentId == sourceDocumentId)) return true;
    final m = RegExp(r'^(\d{2})-').firstMatch(sourceDocumentId);
    return m != null && int.parse(m.group(1)!) == grade;
  }

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
    // WAL-210: provenance đọc TRƯỚC — guard bên dưới cần biết pack có tự khai
    // là bản thử nghiệm không. Tuỳ chọn, fail-closed: thiếu ⇒ null.
    final provenance = BuildProvenance.fromJson(j['buildProvenance']);
    final routerAllowed = provenance?.experimental == true;
    var droppedRouter = 0;
    // ⭐ item F: mục có `source` = pattern-router* chỉ đi qua khi pack tự
    // khai experimental. Không khai ⇒ loại và đếm (fail closed).
    bool guardRouter(Map e) {
      final src = e['source'];
      if (src is String && src.startsWith('pattern-router') && !routerAllowed) {
        droppedRouter++;
        return false;
      }
      return true;
    }

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
              lessons: _dedupeLessons([
                for (final l in (b['lessons'] as List? ?? const [])
                    .whereType<Map>())
                  if (l['no'] is num)
                    LessonRef(
                        no: (l['no'] as num).toInt(),
                        title: l['title'] as String?,
                        pageStart: (l['pageStart'] as num?)?.toInt()),
              ]),
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
        if (!guardRouter(r)) continue;
        tv.add(TvReading(
            book: '${r['book']}',
            lesson: (r['lesson'] as num).toInt(),
            page: (r['page'] as num?)?.toInt(),
            source: r['source'] as String?,
            passage: r['passage'] as String,
            questions: [
              for (final q
                  in (r['questions'] as List? ?? const []).whereType<Map>())
                if (q['prompt'] is String)
                  TvQuestion(
                      prompt: q['prompt'] as String,
                      page: (q['page'] as num?)?.toInt(),
                      options: [
                        for (final o in (q['options'] as List? ?? const []))
                          if (o is String && o.trim().isNotEmpty) o,
                      ]),
            ]));
      }
    }
    final tw = <TvWriting>[];
    final wj = j['tvWritings'];
    if (wj is List) {
      for (final w in wj.whereType<Map>()) {
        if (w['prompt'] is! String || w['lesson'] is! num) continue;
        if (!guardRouter(w)) continue;
        tw.add(TvWriting(
            book: '${w['book']}',
            lesson: (w['lesson'] as num).toInt(),
            page: (w['page'] as num?)?.toInt(),
            source: w['source'] as String?,
            prompt: w['prompt'] as String));
      }
    }
    final su = <SuSource>[];
    final uj = j['suSources'];
    if (uj is List) {
      for (final e in uj.whereType<Map>()) {
        // thiếu excerpt hoặc attribution ⇒ KHÔNG phải tư liệu dùng được — bỏ.
        if (e['excerpt'] is! String || e['attribution'] is! String) continue;
        if (!guardRouter(e)) continue;
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
        if (!guardRouter(e)) continue;
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
        if (!guardRouter(m)) continue;
        dm.add(DiaMap(
            subject: '${m['subject'] ?? 'LS&ĐL'}',
            book: '${m['book']}',
            page: (m['page'] as num?)?.toInt(),
            lesson: (m['lesson'] as num?)?.toInt(),
            asset: m['asset'] as String,
            caption: m['caption'] as String,
            questions: qs,
            pagePdf: (m['pagePdf'] as num).toInt(),
            bboxFrac: bbox,
            extractionVersion: m['extractionVersion'] as String));
      }
    }
    final sa = <IndexedSourceAsset>[];
    final aj = j['sourceAssets'];
    if (aj is List) {
      for (final a in aj.whereType<Map>()) {
        final bbox = [
          for (final v in (a['bboxFrac'] as List? ?? const []))
            if (v is num) v.toDouble()
        ];
        // Thiếu bất kỳ mảnh provenance nào ⇒ KHÔNG dựng được SourceAsset,
        // nên cũng không được phép nằm trong index.
        if (a['asset'] is! String ||
            a['subject'] is! String ||
            a['sourceDocumentId'] is! String ||
            a['pagePdf'] is! num ||
            a['extractionVersion'] is! String ||
            bbox.length != 4) {
          continue;
        }
        sa.add(IndexedSourceAsset(
            subject: a['subject'] as String,
            assetType: '${a['assetType'] ?? 'FIGURE'}',
            asset: a['asset'] as String,
            sourceDocumentId: a['sourceDocumentId'] as String,
            pagePdf: (a['pagePdf'] as num).toInt(),
            pagePrinted: (a['pagePrinted'] as num?)?.toInt(),
            bboxFrac: bbox,
            extractionVersion: a['extractionVersion'] as String,
            printedCaption: a['printedCaption'] as String?,
            samGloss: a['samGloss'] as String?,
            lesson: (a['lesson'] as num?)?.toInt()));
      }
    }
    final bk = <BookRef>[];
    final bj = j['books'];
    if (bj is List) {
      for (final b in bj.whereType<Map>()) {
        // Thiếu bìa hoặc thiếu định danh ⇒ KHÔNG lên giá sách (fail closed):
        // một ô trống trên giá còn tệ hơn không có giá.
        if (b['sourceDocumentId'] is! String ||
            b['subject'] is! String ||
            b['title'] is! String ||
            b['cover'] is! String) {
          continue;
        }
        // Bìa ngoài thư mục đã khai báo trong pubspec là bìa KHÔNG BAO GIỜ
        // dựng được trên máy thật ⇒ coi như không có bìa.
        if (!(b['cover'] as String).startsWith(BookRef.coverDir)) continue;
        bk.add(BookRef(
            sourceDocumentId: b['sourceDocumentId'] as String,
            subject: b['subject'] as String,
            title: b['title'] as String,
            cover: b['cover'] as String,
            lessonCount: (b['lessonCount'] as num?)?.toInt() ?? 0,
            volumeLabel: b['volumeLabel'] as String?,
            volume: switch (b['volume']) {
              final num v => v.toInt(),
              final String s => int.tryParse(s),
              _ => null,
            },
            bookSeries: b['bookSeries'] as String?,
            pageCount: (b['pageCount'] as num?)?.toInt()));
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
        diaMaps: dm,
        sourceAssets: sa,
        books: bk,
        // WAL-210: tuỳ chọn, fail-closed — thiếu ⇒ null, KHÔNG đổi gì khác
        // ngoài guard router phía trên.
        buildProvenance: provenance,
        droppedRouterActivities: droppedRouter);
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
