/// TRACK B — `LessonDocument`: MỘT bài học, một tài liệu, ba View đọc chung.
///
/// Hình chiếu theo bài của SDM (12-STRUCTURED-LESSON-HYPOTHESIS §3) ở mức
/// tối thiểu mà ba View cần. Bất biến (giữ bằng test):
/// - Mọi block có `sourceRef` + `trust`; không có thì không parse được.
/// - `WithheldBlock` KHÔNG CÓ trường chữ — bị giữ lại là bị giữ lại, không
///   View nào lôi được chữ ra (bất biến #3 của TC-11).
/// - `evidencePolicy` chỉ là `none`.
/// - `fromJson` fail-closed: JSON lệch ⇒ `null`, không tài liệu nửa vời.
library;

import 'content_trust.dart';
import 'semantic_data.dart';
import 'tutor_script.dart';

/// Nguồn của MỘT phần tử: sách + trang PDF + trang in + khung `[x, y, w, h]`
/// chuẩn hoá theo trang (quy ước SDM, TC-11 §2).
class SourceRef {
  const SourceRef({
    required this.book,
    required this.pagePdf,
    required this.bbox,
    this.pagePrinted,
    this.blockId,
    this.extraction,
    this.ocrConf,
  }) : assert(bbox.length == 4, 'khung phải đủ 4 số');

  final String book;
  final int pagePdf;

  /// Trang IN — thứ nói với trẻ. `null` ⇒ UI không bịa số trang.
  final int? pagePrinted;
  final List<double> bbox;
  final String? blockId;
  final String? extraction;
  final double? ocrConf;

  static SourceRef? fromJson(Object? v) {
    if (v is! Map) return null;
    final book = v['book'], pg = v['pagePdf'];
    final bbox = [
      for (final x in (v['bbox'] as List? ?? const []))
        if (x is num) x.toDouble(),
    ];
    if (book is! String || pg is! num || bbox.length != 4) return null;
    return SourceRef(
      book: book,
      pagePdf: pg.toInt(),
      pagePrinted: (v['pagePrinted'] as num?)?.toInt(),
      bbox: bbox,
      blockId: v['blockId'] as String?,
      extraction: v['extraction'] as String?,
      ocrConf: (v['ocrConf'] as num?)?.toDouble(),
    );
  }

  Map<String, Object?> toJson() => {
    'book': book,
    'pagePdf': pagePdf,
    if (pagePrinted != null) 'pagePrinted': pagePrinted,
    'bbox': bbox,
    if (blockId != null) 'blockId': blockId,
    if (extraction != null) 'extraction': extraction,
    if (ocrConf != null) 'ocrConf': ocrConf,
  };
}

enum ActivityKind {
  objective,
  instruction,
  sidebar,
  stageLabel;

  static ActivityKind? parse(Object? v) {
    for (final k in values) {
      if (k.name == v) return k;
    }
    return null;
  }
}

sealed class LessonBlock {
  const LessonBlock({
    required this.id,
    required this.sourceRef,
    required this.trust,
    this.roleConfidence,
  });

  final String id;
  final SourceRef sourceRef;
  final ContentTrust trust;

  /// Độ tin của VAI TRÒ (khác độ tin của chữ) — TC-07: câu hỏi tự gán nhãn
  /// chưa đủ tin để làm đề; UI chỉ dùng để vẽ, không để chấm.
  final double? roleConfidence;

  Map<String, Object?> toJson();

  Map<String, Object?> _base(String type) => {
    'type': type,
    'id': id,
    'sourceRef': sourceRef.toJson(),
    'trust': trust.name,
    if (roleConfidence != null) 'roleConfidence': roleConfidence,
  };

  static LessonBlock? fromJson(Map<String, Object?> j) {
    final id = j['id'];
    final ref = SourceRef.fromJson(j['sourceRef']);
    final trust = ContentTrust.parse(j['trust']);
    if (id is! String || ref == null || trust == null) return null;
    final conf = (j['roleConfidence'] as num?)?.toDouble();
    String? text() => j['text'] is String ? j['text'] as String : null;
    switch (j['type']) {
      case 'heading':
        final t = text();
        if (t == null) return null;
        return HeadingBlock(
          id: id,
          sourceRef: ref,
          trust: trust,
          roleConfidence: conf,
          text: t,
          level: ((j['level'] as num?)?.toInt() ?? 1).clamp(1, 3),
        );
      case 'paragraph':
        final t = text();
        if (t == null) return null;
        return ParagraphBlock(
          id: id,
          sourceRef: ref,
          trust: trust,
          roleConfidence: conf,
          text: t,
        );
      case 'image':
        final crop = j['crop'];
        if (crop is! String || crop.isEmpty) return null;
        return ImageBlock(
          id: id,
          sourceRef: ref,
          trust: trust,
          crop: crop,
          captionBlockId: j['captionBlockId'] as String?,
          labels: (j['labels'] as num?)?.toInt() ?? 0,
          aspect: (j['aspect'] as num?)?.toDouble(),
        );
      case 'caption':
        final t = text();
        if (t == null) return null;
        return CaptionBlock(
          id: id,
          sourceRef: ref,
          trust: trust,
          roleConfidence: conf,
          text: t,
          refersFigure: j['refersFigure'] == true,
        );
      case 'table':
        final rows = <List<String>>[];
        for (final r in (j['rows'] as List? ?? const [])) {
          if (r is! List) return null;
          rows.add([for (final c in r) c is String ? c : '']);
        }
        if (rows.isEmpty) return null;
        return TableBlock(
          id: id,
          sourceRef: ref,
          trust: trust,
          roleConfidence: conf,
          rows: rows,
          safe: j['safe'] == true,
          headerRows: (j['headerRows'] as num?)?.toInt() ?? 0,
        );
      case 'question':
        final t = text();
        if (t == null) return null;
        return QuestionBlock(
          id: id,
          sourceRef: ref,
          trust: trust,
          roleConfidence: conf,
          text: t,
        );
      case 'activity':
        final t = text();
        final kind = ActivityKind.parse(j['kind']);
        if (t == null || kind == null) return null;
        return ActivityBlock(
          id: id,
          sourceRef: ref,
          trust: trust,
          roleConfidence: conf,
          kind: kind,
          text: t,
        );
      case 'withheld':
        final reason = j['reason'];
        if (reason is! String || reason.isEmpty) return null;
        // ⭐ Cố ý KHÔNG đọc `text` dù JSON có — bị giữ lại là bị giữ lại.
        return WithheldBlock(
          id: id,
          sourceRef: ref,
          trust: trust,
          reason: reason,
          crop: j['crop'] as String?,
        );
      case 'sourceRef':
        final t = text();
        if (t == null) return null;
        return SourceRefBlock(id: id, sourceRef: ref, trust: trust, text: t);
      default:
        return null;
    }
  }
}

final class HeadingBlock extends LessonBlock {
  const HeadingBlock({
    required super.id,
    required super.sourceRef,
    required super.trust,
    super.roleConfidence,
    required this.text,
    this.level = 1,
  });
  final String text;
  final int level; // 1 = tên bài/mục lớn, 2 = mục, 3 = mục con

  @override
  Map<String, Object?> toJson() => {
    ..._base('heading'),
    'text': text,
    'level': level,
  };
}

final class ParagraphBlock extends LessonBlock {
  const ParagraphBlock({
    required super.id,
    required super.sourceRef,
    required super.trust,
    super.roleConfidence,
    required this.text,
  });
  final String text;

  @override
  Map<String, Object?> toJson() => {..._base('paragraph'), 'text': text};
}

/// Vùng trang cắt từ SGK — NỘI BỘ (Founder D4). `crop` là đường dẫn tương
/// đối trong thư mục fixture; thiếu tệp ⇒ UI nói «hình trong sách, trang N».
final class ImageBlock extends LessonBlock {
  const ImageBlock({
    required super.id,
    required super.sourceRef,
    required super.trust,
    required this.crop,
    this.captionBlockId,
    this.labels = 0,
    this.aspect,
  });
  final String crop;
  final String? captionBlockId;
  final int labels;

  /// width/height của ảnh crop — để UI giữ CHỖ trước khi ảnh giải mã xong
  /// (Nokia n1 D4: neo cuộn trượt vì ảnh nở ra sau). `null` ⇒ không giữ chỗ.
  final double? aspect;

  @override
  Map<String, Object?> toJson() => {
    ..._base('image'),
    'crop': crop,
    if (captionBlockId != null) 'captionBlockId': captionBlockId,
    'labels': labels,
    if (aspect != null) 'aspect': aspect,
  };
}

final class CaptionBlock extends LessonBlock {
  const CaptionBlock({
    required super.id,
    required super.sourceRef,
    required super.trust,
    super.roleConfidence,
    required this.text,
    this.refersFigure = false,
  });
  final String text;
  final bool refersFigure;

  @override
  Map<String, Object?> toJson() => {
    ..._base('caption'),
    'text': text,
    'refersFigure': refersFigure,
  };
}

/// Bảng: chỉ vẽ thành ô khi `safe` (đường GPU/Marker, TC-07); không safe ⇒
/// UI vẽ như vùng ảnh / placeholder. Bài 17 không có bảng nào.
final class TableBlock extends LessonBlock {
  const TableBlock({
    required super.id,
    required super.sourceRef,
    required super.trust,
    super.roleConfidence,
    required this.rows,
    required this.safe,
    this.headerRows = 0,
  });
  final List<List<String>> rows;
  final bool safe;
  final int headerRows;

  @override
  Map<String, Object?> toJson() => {
    ..._base('table'),
    'rows': rows,
    'safe': safe,
    'headerRows': headerRows,
  };
}

final class QuestionBlock extends LessonBlock {
  const QuestionBlock({
    required super.id,
    required super.sourceRef,
    required super.trust,
    super.roleConfidence,
    required this.text,
  });
  final String text;

  @override
  Map<String, Object?> toJson() => {..._base('question'), 'text': text};
}

final class ActivityBlock extends LessonBlock {
  const ActivityBlock({
    required super.id,
    required super.sourceRef,
    required super.trust,
    super.roleConfidence,
    required this.kind,
    required this.text,
  });
  final ActivityKind kind;
  final String text;

  @override
  Map<String, Object?> toJson() => {
    ..._base('activity'),
    'kind': kind.name,
    'text': text,
  };
}

/// Vùng bị giữ lại — KHÔNG có trường chữ theo cấu trúc. `crop` (nếu có) là
/// ảnh vùng trang nội bộ để người lớn đối chiếu; trẻ thấy placeholder thật.
final class WithheldBlock extends LessonBlock {
  const WithheldBlock({
    required super.id,
    required super.sourceRef,
    required super.trust,
    required this.reason,
    this.crop,
  });
  final String reason;
  final String? crop;

  @override
  Map<String, Object?> toJson() => {
    ..._base('withheld'),
    'reason': reason,
    if (crop != null) 'crop': crop,
  };
}

/// Dòng nguồn cuối bài («SGK KHTN 6 · trang 60–63»).
final class SourceRefBlock extends LessonBlock {
  const SourceRefBlock({
    required super.id,
    required super.sourceRef,
    required super.trust,
    required this.text,
  });
  final String text;

  @override
  Map<String, Object?> toJson() => {..._base('sourceRef'), 'text': text};
}

/// Chương/chủ đề trong mục lục — suy từ MỤC LỤC in (OCR), có luật, có trust.
class ChapterRef {
  const ChapterRef({
    required this.label,
    required this.title,
    required this.lessonNos,
    required this.trust,
    required this.derivation,
  });
  final String label; // «Chương IV»
  final String title; // nguyên văn mục lục (OCR) — có thể mang lỗi OCR
  final List<int> lessonNos;
  final ContentTrust trust;
  final String derivation;

  bool contains(int lessonNo) => lessonNos.contains(lessonNo);

  static ChapterRef? fromJson(Object? v) {
    if (v is! Map) return null;
    final label = v['label'], title = v['title'], der = v['derivation'];
    final trust = ContentTrust.parse(v['trust']);
    final nos = [
      for (final n in (v['lessonNos'] as List? ?? const []))
        if (n is num) n.toInt(),
    ];
    if (label is! String || title is! String || der is! String) return null;
    if (trust == null) return null;
    return ChapterRef(
      label: label,
      title: title,
      lessonNos: nos,
      trust: trust,
      derivation: der,
    );
  }

  Map<String, Object?> toJson() => {
    'label': label,
    'title': title,
    'lessonNos': lessonNos,
    'trust': trust.name,
    'derivation': derivation,
  };
}

class LessonProvenance {
  const LessonProvenance({
    required this.trust,
    required this.book,
    required this.pagePdfStart,
    required this.pagePdfEnd,
    required this.generator,
    required this.sourcePipeline,
    required this.distribution,
    this.pagePrintedStart,
    this.pagePrintedEnd,
    this.sdmVersion,
    this.boundaryConfidence,
    this.tslPath,
  });

  final ContentTrust trust;
  final String book;
  final int pagePdfStart, pagePdfEnd;
  final int? pagePrintedStart, pagePrintedEnd;
  final String generator;
  final String sourcePipeline;
  final String? sdmVersion;
  final double? boundaryConfidence;
  final String? tslPath;

  /// «internal-research-only (Founder D4)» — chuỗi bắt buộc có, để không ai
  /// tưởng crop trang là tài sản phát hành được.
  final String distribution;

  static LessonProvenance? fromJson(Object? v) {
    if (v is! Map) return null;
    final trust = ContentTrust.parse(v['trust']);
    final book = v['book'], s = v['pagePdfStart'], e = v['pagePdfEnd'];
    final gen = v['generator'],
        pipe = v['sourcePipeline'],
        dist = v['distribution'];
    if (trust == null || book is! String || s is! num || e is! num) return null;
    if (gen is! String || pipe is! String || dist is! String) return null;
    return LessonProvenance(
      trust: trust,
      book: book,
      pagePdfStart: s.toInt(),
      pagePdfEnd: e.toInt(),
      pagePrintedStart: (v['pagePrintedStart'] as num?)?.toInt(),
      pagePrintedEnd: (v['pagePrintedEnd'] as num?)?.toInt(),
      generator: gen,
      sourcePipeline: pipe,
      sdmVersion: v['sdmVersion'] as String?,
      boundaryConfidence: (v['boundaryConfidence'] as num?)?.toDouble(),
      tslPath: v['tslPath'] as String?,
      distribution: dist,
    );
  }

  Map<String, Object?> toJson() => {
    'trust': trust.name,
    'book': book,
    'pagePdfStart': pagePdfStart,
    'pagePdfEnd': pagePdfEnd,
    if (pagePrintedStart != null) 'pagePrintedStart': pagePrintedStart,
    if (pagePrintedEnd != null) 'pagePrintedEnd': pagePrintedEnd,
    'generator': generator,
    'sourcePipeline': sourcePipeline,
    if (sdmVersion != null) 'sdmVersion': sdmVersion,
    if (boundaryConfidence != null) 'boundaryConfidence': boundaryConfidence,
    if (tslPath != null) 'tslPath': tslPath,
    'distribution': distribution,
  };
}

/// Một dòng của «bảng điều tra năng lực thật» — máy đếm, không người ước.
class CensusRow {
  const CensusRow({
    required this.element,
    required this.trust,
    required this.count,
    required this.basis,
  });
  final String element;
  final ContentTrust trust;
  final int count;

  /// Vì sao đếm vào ô này (vd `derivation` của sơ đồ).
  final String basis;

  @override
  String toString() => '$element · ${trust.name} · $count · $basis';
}

class LessonDocument {
  const LessonDocument({
    required this.schema,
    required this.book,
    required this.bookTitle,
    required this.subject,
    required this.grade,
    required this.lessonNo,
    required this.title,
    required this.provenance,
    required this.blocks,
    this.chapter,
    this.chapters = const [],
    this.semantic = const [],
    this.tutorScript,
    this.evidencePolicy = EvidencePolicy.none,
    this.assetBase = '',
  });

  static const schemaV1 = 'wal-lesson-fixture-v1';

  final String schema;
  final String book;
  final String bookTitle;
  final String subject;
  final int grade;
  final int lessonNo;

  /// Nguyên văn tiêu đề trong sách (thường in hoa) — UI tự title-case.
  final String title;
  final ChapterRef? chapter;
  final List<ChapterRef> chapters;
  final LessonProvenance provenance;
  final EvidencePolicy evidencePolicy;
  final List<LessonBlock> blocks;
  final List<SemanticData> semantic;
  final TutorScript? tutorScript;

  /// Thư mục asset chứa fixture này (`assets/fixtures/real/`…) — do loader
  /// đặt; `ImageBlock.crop` nối vào đây.
  final String assetBase;

  ContentTrust get trust => provenance.trust;
  bool get isFixture => trust.requiresFixtureChip;
  String get slotKey => '$book#$lessonNo';

  /// «HỖN HỢP. TÁCH CHẤT…» → «Hỗn hợp. Tách chất…»: viết hoa đầu chuỗi và
  /// sau dấu kết câu (Nokia n1 D1: «Hỗn hợp. tách chất» — chữ thường sau «.»).
  static String titleCase(String upper) => upper.toLowerCase().replaceAllMapped(
    RegExp(r'(^\s*|[.!?]\s*)(\S)', unicode: true),
    (m) => '${m[1]}${m[2]!.toUpperCase()}',
  );

  String get lessonLabel => 'Bài $lessonNo · ${titleCase(title)}';

  /// «SGK KHTN 6 · trang 60–63» — chỉ từ trang IN; thiếu ⇒ nói thật.
  String get pageRangeLine {
    final s = provenance.pagePrintedStart, e = provenance.pagePrintedEnd;
    if (s == null || e == null) return 'SGK $bookTitle · chưa dò được trang in';
    return s == e
        ? 'SGK $bookTitle · trang $s'
        : 'SGK $bookTitle · trang $s–$e';
  }

  /// Dòng nguồn cho MỘT block («SGK KHTN 6 · trang 61»).
  String sourceLineFor(SourceRef ref) => ref.pagePrinted == null
      ? 'SGK $bookTitle · trang PDF ${ref.pagePdf} (chưa dò được trang in)'
      : 'SGK $bookTitle · trang ${ref.pagePrinted}';

  LessonBlock? blockById(String id) {
    for (final b in blocks) {
      if (b.id == id) return b;
    }
    return null;
  }

  /// Trang IN của một trang PDF — suy từ block chữ cùng trang (hình của TSL
  /// không mang trang in). Không suy được ⇒ `null`, UI nói «trang PDF N».
  int? printedPageFor(int pagePdf) {
    for (final b in blocks) {
      if (b.sourceRef.pagePdf == pagePdf && b.sourceRef.pagePrinted != null) {
        return b.sourceRef.pagePrinted;
      }
    }
    return null;
  }

  /// Dòng nguồn cho một block, ưu tiên trang in đã suy được.
  String sourceLineForBlock(LessonBlock b) {
    final printed =
        b.sourceRef.pagePrinted ?? printedPageFor(b.sourceRef.pagePdf);
    return printed == null
        ? 'SGK $bookTitle · trang PDF ${b.sourceRef.pagePdf} (chưa dò được trang in)'
        : 'SGK $bookTitle · trang $printed';
  }

  /// Chữ của một block nếu block ấy CÓ chữ (withheld/image ⇒ `null`).
  static String? textOf(LessonBlock b) => switch (b) {
    HeadingBlock(:final text) => text,
    ParagraphBlock(:final text) => text,
    CaptionBlock(:final text) => text,
    QuestionBlock(:final text) => text,
    ActivityBlock(:final text) => text,
    SourceRefBlock(:final text) => text,
    TableBlock(:final rows) => rows.map((r) => r.join(' | ')).join('\n'),
    ImageBlock() => null,
    WithheldBlock() => null,
  };

  bool get hasProcess => semantic.any((s) => s is ProcessSemantic);

  /// ⭐ REAL CAPABILITY RATIO — máy đếm theo `ContentTrust` của từng phần tử
  /// nhìn thấy trên màn. Không gộp, không ước.
  List<CensusRow> capabilityCensus() {
    final rows = <CensusRow>[];
    void add(String element, ContentTrust t, int n, String basis) {
      if (n > 0) {
        rows.add(CensusRow(element: element, trust: t, count: n, basis: basis));
      }
    }

    final byTrust = <String, Map<ContentTrust, int>>{};
    for (final b in blocks) {
      final kind = switch (b) {
        HeadingBlock() => 'block.heading',
        ParagraphBlock() => 'block.paragraph',
        ImageBlock() => 'block.image(sourceCrop)',
        CaptionBlock() => 'block.caption',
        TableBlock() => 'block.table',
        QuestionBlock() => 'block.question',
        ActivityBlock() => 'block.activity',
        WithheldBlock() => 'block.withheld',
        SourceRefBlock() => 'block.sourceRef',
      };
      byTrust
          .putIfAbsent(kind, () => {})
          .update(b.trust, (n) => n + 1, ifAbsent: () => 1);
    }
    for (final e in byTrust.entries) {
      for (final t in e.value.entries) {
        add(
          e.key,
          t.key,
          t.value,
          'provenance.sourcePipeline=${provenance.sourcePipeline}',
        );
      }
    }
    for (final s in semantic) {
      final n = switch (s) {
        ProcessSemantic(:final steps) => steps.length,
        ComparisonSemantic(:final entities) => entities.length,
        ConceptMapSemantic(:final relations) => relations.length,
        TimelineSemantic(:final events) => events.length,
      };
      add('semantic.${s.shapeLabel}', s.trust, n, 'derivation=${s.derivation}');
    }
    final ts = tutorScript;
    if (ts != null) {
      add(
        'tutor.steps',
        ts.trust,
        ts.steps.length,
        'samMode=${ts.samMode.name}; khoá đáp án = prototype, không SGV',
      );
    }
    for (final c in chapters) {
      add('chapter', c.trust, 1, 'derivation=${c.derivation}');
    }
    add(
      'evidence.writes',
      ContentTrust.prototype,
      0,
      'evidencePolicy=${evidencePolicy.name}',
    );
    return rows;
  }

  static LessonDocument? fromJson(
    Map<String, Object?> j, {
    String assetBase = '',
  }) {
    if (j['schema'] != schemaV1) return null;
    final book = j['book'], bt = j['bookTitle'], subj = j['subject'];
    final grade = j['grade'], no = j['lesson'], title = j['title'];
    if (book is! String || bt is! String || subj is! String) return null;
    if (grade is! num || no is! num || title is! String) return null;
    final prov = LessonProvenance.fromJson(j['provenance']);
    final policy = EvidencePolicy.parse(j['evidencePolicy']);
    if (prov == null || policy == null || prov.book != book) return null;
    final blocks = <LessonBlock>[];
    for (final b in (j['blocks'] as List? ?? const []).whereType<Map>()) {
      final blk = LessonBlock.fromJson(b.cast<String, Object?>());
      if (blk == null) return null; // một block hỏng ⇒ không tài liệu nửa vời
      blocks.add(blk);
    }
    if (blocks.isEmpty) return null;
    final semantic = <SemanticData>[];
    for (final s in (j['semantic'] as List? ?? const []).whereType<Map>()) {
      final sd = SemanticData.fromJson(s.cast<String, Object?>());
      if (sd == null) return null;
      semantic.add(sd);
    }
    final chapters = <ChapterRef>[];
    for (final c in (j['chapters'] as List? ?? const [])) {
      final cr = ChapterRef.fromJson(c);
      if (cr == null) return null;
      chapters.add(cr);
    }
    TutorScript? script;
    if (j['tutorScript'] is Map) {
      script = TutorScript.fromJson(
        (j['tutorScript'] as Map).cast<String, Object?>(),
      );
      if (script == null) return null;
    }
    return LessonDocument(
      schema: schemaV1,
      book: book,
      bookTitle: bt,
      subject: subj,
      grade: grade.toInt(),
      lessonNo: no.toInt(),
      title: title,
      chapter: ChapterRef.fromJson(j['chapter']),
      chapters: chapters,
      provenance: prov,
      evidencePolicy: policy,
      blocks: blocks,
      semantic: semantic,
      tutorScript: script,
      assetBase: assetBase,
    );
  }

  Map<String, Object?> toJson() => {
    'schema': schema,
    'book': book,
    'bookTitle': bookTitle,
    'subject': subject,
    'grade': grade,
    'lesson': lessonNo,
    'title': title,
    if (chapter != null) 'chapter': chapter!.toJson(),
    'chapters': [for (final c in chapters) c.toJson()],
    'provenance': provenance.toJson(),
    'evidencePolicy': evidencePolicy.name,
    'blocks': [for (final b in blocks) b.toJson()],
    'semantic': [for (final s in semantic) s.toJson()],
    if (tutorScript != null) 'tutorScript': tutorScript!.toJson(),
  };
}
