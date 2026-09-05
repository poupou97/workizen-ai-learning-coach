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
    this.pipeline,
    this.agreementScore,
  }) : assert(bbox.length == 4, 'khung phải đủ 4 số');

  final String book;
  final int pagePdf;

  /// Trang IN — thứ nói với trẻ. `null` ⇒ UI không bịa số trang.
  final int? pagePrinted;
  final List<double> bbox;
  final String? blockId;
  final String? extraction;
  final double? ocrConf;

  /// Round 3 (A1): pipeline đã sinh block (`tc2-p1`); `null` ⇒ không rõ.
  final String? pipeline;

  /// Round 3 (A1): mức đồng thuận chữ giữa hai stack (TSL `text_sim`, đưa
  /// về 0..1). `null` ⇒ không đo. Chỉ để đối chiếu, không để quyết định.
  final double? agreementScore;

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
      pipeline: v['pipeline'] as String?,
      agreementScore: (v['agreementScore'] as num?)?.toDouble(),
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
    if (pipeline != null) 'pipeline': pipeline,
    if (agreementScore != null) 'agreementScore': agreementScore,
  };
}

/// Round 3 (A1) — QUAN HỆ của một block với phần còn lại của trang/bài, bắc
/// cầu nguyên trạng từ TSL (`heading_path`, `refers_figure`, `caption` của
/// figure, `order`, `enumerator_restored`). Thiếu ⇒ rỗng: đây là siêu dữ liệu
/// dẫn đường, KHÔNG phải trust — không có nó tài liệu vẫn parse.
class BlockRelations {
  const BlockRelations({
    this.headingPath = const [],
    this.refersFigure = false,
    this.captionOf,
    this.order,
    this.enumeratorRestored = false,
  });

  static const empty = BlockRelations();

  /// «Bài 17 › TÁCH CHẤT KHỎI HỖN HỢP › · Nguyên tắc tách chất».
  final List<String> headingPath;

  /// Chữ của block nhắc tới một hình («Hình 17.2…»).
  final bool refersFigure;

  /// Block là CAPTION của figure có id này (nghịch đảo `figure.caption`).
  final String? captionOf;

  /// Thứ tự đọc trong trang theo pipeline.
  final int? order;
  final bool enumeratorRestored;

  bool get isEmpty =>
      headingPath.isEmpty &&
      !refersFigure &&
      captionOf == null &&
      order == null &&
      !enumeratorRestored;

  static BlockRelations fromJson(Object? v) {
    if (v is! Map) return empty;
    return BlockRelations(
      headingPath: [
        for (final h in (v['headingPath'] as List? ?? const []))
          if (h is String) h,
      ],
      refersFigure: v['refersFigure'] == true,
      captionOf: v['captionOf'] as String?,
      order: (v['order'] as num?)?.toInt(),
      enumeratorRestored: v['enumeratorRestored'] == true,
    );
  }

  Map<String, Object?> toJson() => {
    if (headingPath.isNotEmpty) 'headingPath': headingPath,
    if (refersFigure) 'refersFigure': true,
    if (captionOf != null) 'captionOf': captionOf,
    if (order != null) 'order': order,
    if (enumeratorRestored) 'enumeratorRestored': true,
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
    this.sourceRole,
    this.roleMethod,
    this.relations = BlockRelations.empty,
  });

  final String id;
  final SourceRef sourceRef;
  final ContentTrust trust;

  /// Độ tin của VAI TRÒ (khác độ tin của chữ) — TC-07: câu hỏi tự gán nhãn
  /// chưa đủ tin để làm đề; UI chỉ dùng để vẽ, không để chấm.
  final double? roleConfidence;

  /// Round 3 (A1): vai trò NGUYÊN VĂN pipeline gán (`body`, `sidebar`,
  /// `stage_label`…) — giữ để kiểm vai trò được, kể cả khi mô hình tiêu thụ
  /// gộp nó vào một loại block khác. `null` ⇒ fixture cũ / mẫu.
  final String? sourceRole;

  /// Round 3 (A1): cách gán vai trò (`lexicon`, `geometry`, `native`…).
  final String? roleMethod;

  /// Round 3 (A1): quan hệ với trang/bài (heading path, hình, thứ tự).
  final BlockRelations relations;

  Map<String, Object?> toJson();

  Map<String, Object?> _base(String type) => {
    'type': type,
    'id': id,
    'sourceRef': sourceRef.toJson(),
    'trust': trust.name,
    if (roleConfidence != null) 'roleConfidence': roleConfidence,
    if (sourceRole != null) 'sourceRole': sourceRole,
    if (roleMethod != null) 'roleMethod': roleMethod,
    if (!relations.isEmpty) 'relations': relations.toJson(),
  };

  static LessonBlock? fromJson(Map<String, Object?> j) {
    final id = j['id'];
    final ref = SourceRef.fromJson(j['sourceRef']);
    final trust = ContentTrust.parse(j['trust']);
    if (id is! String || ref == null || trust == null) return null;
    // ⭐⭐ WITHHELD ≠ TRUSTED: trust `withheld` chỉ được đứng trên block
    // KHÔNG CÓ CHỮ. Block chữ mà khai `withheld` ⇒ tài liệu bị từ chối.
    if (!trust.mayCarryText && j['type'] != 'withheld') return null;
    final conf = (j['roleConfidence'] as num?)?.toDouble();
    final role = j['sourceRole'] is String ? j['sourceRole'] as String : null;
    final method = j['roleMethod'] is String ? j['roleMethod'] as String : null;
    final rel = BlockRelations.fromJson(j['relations']);
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
          sourceRole: role,
          roleMethod: method,
          relations: rel,
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
          sourceRole: role,
          roleMethod: method,
          relations: rel,
          text: t,
        );
      case 'image':
        final crop = j['crop'];
        if (crop is! String || crop.isEmpty) return null;
        return ImageBlock(
          id: id,
          sourceRef: ref,
          trust: trust,
          sourceRole: role,
          relations: rel,
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
          sourceRole: role,
          roleMethod: method,
          relations: rel,
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
          sourceRole: role,
          roleMethod: method,
          relations: rel,
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
          sourceRole: role,
          roleMethod: method,
          relations: rel,
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
          sourceRole: role,
          roleMethod: method,
          relations: rel,
          kind: kind,
          text: t,
        );
      case 'withheld':
        // `reasons[]` (cầu A1) hoặc `reason` «a,b» (fixture cũ) — không có
        // lý do nào ⇒ không block. Chuỗi rỗng trong danh sách bị bỏ.
        final reasons = [
          for (final r in (j['reasons'] as List? ?? const []))
            if (r is String && r.trim().isNotEmpty) r.trim(),
        ];
        final reason = j['reason'];
        if (reasons.isEmpty && reason is String && reason.trim().isNotEmpty) {
          reasons.addAll(
            reason.split(',').map((s) => s.trim()).where((s) => s.isNotEmpty),
          );
        }
        if (reasons.isEmpty) return null;
        final status = j['status'];
        // ⭐ Cố ý KHÔNG đọc `text` dù JSON có — bị giữ lại là bị giữ lại.
        return WithheldBlock(
          id: id,
          sourceRef: ref,
          trust: trust,
          sourceRole: role,
          relations: rel,
          reasons: reasons,
          status: status is String && status.isNotEmpty ? status : null,
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
    super.sourceRole,
    super.roleMethod,
    super.relations,
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
    super.sourceRole,
    super.roleMethod,
    super.relations,
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
    super.sourceRole,
    super.relations,
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
    super.sourceRole,
    super.roleMethod,
    super.relations,
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
    super.sourceRole,
    super.roleMethod,
    super.relations,
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
    super.sourceRole,
    super.roleMethod,
    super.relations,
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
    super.sourceRole,
    super.roleMethod,
    super.relations,
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
    super.sourceRole,
    super.relations,
    required this.reasons,
    this.status,
    this.crop,
  });

  /// Mã lý do của pipeline (`page_feature:diagram`, `math_guard`,
  /// `unknown_role:footnote`…) — nguyên trạng, không dịch, không gộp.
  final List<String> reasons;

  /// `WITHHELD` / `CONFLICT` theo TSL; `null` ⇒ fixture cũ / mẫu.
  final String? status;
  final String? crop;

  /// Dạng chuỗi «a,b» — giữ cho UI cũ (`withheld_card.dart`).
  String get reason => reasons.join(',');

  @override
  Map<String, Object?> toJson() => {
    ..._base('withheld'),
    'reason': reason,
    'reasons': reasons,
    if (status != null) 'status': status,
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

/// Round 3 (A1) — RANH GIỚI BÀI theo pipeline (TSL `boundary`): trang PDF
/// đầu/cuối, cách gắn trang vào bài và độ tin của cách gắn. Thiếu ⇒ `null`
/// (fixture cũ / mẫu); có mà thiếu trang ⇒ tài liệu bị từ chối.
class LessonBoundary {
  const LessonBoundary({
    required this.pageStart,
    required this.pageEnd,
    required this.confidence,
    this.headerFound = false,
    this.source,
    this.attachMethods = const {},
  });

  final int pageStart, pageEnd;
  final double confidence;
  final bool headerFound;

  /// `header` / `toc` / `both`.
  final String? source;

  /// «header: 1, continuation: 3…» — đếm theo cách gắn từng trang.
  final Map<String, int> attachMethods;

  static LessonBoundary? fromJson(Object? v) {
    if (v is! Map) return null;
    final s = v['pageStart'], e = v['pageEnd'], c = v['confidence'];
    if (s is! num || e is! num || c is! num) return null;
    final am = <String, int>{};
    if (v['attachMethods'] is Map) {
      for (final en in (v['attachMethods'] as Map).entries) {
        if (en.key is String && en.value is num) {
          am[en.key as String] = (en.value as num).toInt();
        }
      }
    }
    return LessonBoundary(
      pageStart: s.toInt(),
      pageEnd: e.toInt(),
      confidence: c.toDouble(),
      headerFound: v['headerFound'] == true,
      source: v['source'] as String?,
      attachMethods: am,
    );
  }

  Map<String, Object?> toJson() => {
    'pageStart': pageStart,
    'pageEnd': pageEnd,
    'confidence': confidence,
    'headerFound': headerFound,
    if (source != null) 'source': source,
    if (attachMethods.isNotEmpty) 'attachMethods': attachMethods,
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
    this.boundary,
    this.pipelineVersion,
    this.auditStatus = AuditStatus.notAudited,
    this.auditRef,
    this.sourceHash,
    this.sourceability,
    this.answerKeysIncluded,
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

  /// Round 3 (A1): ranh giới bài theo pipeline; `null` ⇒ fixture cũ / mẫu.
  final LessonBoundary? boundary;

  /// Round 3 (A1): «tc2-p1/sdm-v2» — phiên bản pipeline + mô hình.
  final String? pipelineVersion;

  /// Round 3 (A2): đã đi qua kiểm-tin-giả tới đâu (không có giá trị «đạt»).
  final AuditStatus auditStatus;

  /// Tài liệu kết quả audit mà `auditStatus` trỏ tới (đường dẫn trong repo).
  final String? auditRef;

  /// sha256 của TSL nguồn — hai lần bắc cầu cùng TSL ⇒ cùng tài liệu.
  final String? sourceHash;

  /// `FULL` / `PARTIAL` theo TSL.
  final String? sourceability;

  /// TSL khai có khoá đáp án SGV không. `true` ⇒ tài liệu BỊ TỪ CHỐI ở
  /// `LessonDocument.fromJson` (đáp án SGV không được tới trẻ). `null` ⇒
  /// fixture cũ / mẫu không khai.
  final bool? answerKeysIncluded;

  static LessonProvenance? fromJson(Object? v) {
    if (v is! Map) return null;
    final trust = ContentTrust.parse(v['trust']);
    final book = v['book'], s = v['pagePdfStart'], e = v['pagePdfEnd'];
    final gen = v['generator'],
        pipe = v['sourcePipeline'],
        dist = v['distribution'];
    if (trust == null || book is! String || s is! num || e is! num) return null;
    if (gen is! String || pipe is! String || dist is! String) return null;
    // Trust của cả tài liệu không bao giờ là `withheld`.
    if (!trust.mayCarryText) return null;
    LessonBoundary? boundary;
    if (v['boundary'] != null) {
      boundary = LessonBoundary.fromJson(v['boundary']);
      if (boundary == null) return null; // có mà hỏng ⇒ từ chối
    }
    final audit = AuditStatus.parse(v['auditStatus']);
    if (audit == null) return null;
    final ak = v['answerKeysIncluded'];
    if (ak != null && ak is! bool) return null;
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
      boundaryConfidence:
          (v['boundaryConfidence'] as num?)?.toDouble() ?? boundary?.confidence,
      tslPath: v['tslPath'] as String?,
      distribution: dist,
      boundary: boundary,
      pipelineVersion: v['pipelineVersion'] as String?,
      auditStatus: audit,
      auditRef: v['auditRef'] as String?,
      sourceHash: v['sourceHash'] as String?,
      sourceability: v['sourceability'] as String?,
      answerKeysIncluded: ak as bool?,
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
    if (boundary != null) 'boundary': boundary!.toJson(),
    if (pipelineVersion != null) 'pipelineVersion': pipelineVersion,
    'auditStatus': auditStatus.name,
    if (auditRef != null) 'auditRef': auditRef,
    if (sourceHash != null) 'sourceHash': sourceHash,
    if (sourceability != null) 'sourceability': sourceability,
    if (answerKeysIncluded != null) 'answerKeysIncluded': answerKeysIncluded,
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
    this.licence = ContentLicence.internalResearchOnly,
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

  /// Round 3 (A1): giấy phép phân phối — TÁCH khỏi trust, chỉ một giá trị.
  final ContentLicence licence;
  final List<LessonBlock> blocks;
  final List<SemanticData> semantic;
  final TutorScript? tutorScript;

  /// Thư mục asset chứa fixture này (`assets/fixtures/real/`…) — do loader
  /// đặt; `ImageBlock.crop` nối vào đây.
  final String assetBase;

  ContentTrust get trust => provenance.trust;
  bool get isFixture => trust.requiresFixtureChip;
  String get slotKey => '$book#$lessonNo';

  /// Round 3: số block NHÌN THẤY theo từng giá trị trust — máy đếm, để báo
  /// cáo «trustedStructuredLesson / withheld / …» không gộp.
  Map<ContentTrust, int> get blockCountByTrust {
    final m = <ContentTrust, int>{};
    for (final b in blocks) {
      m.update(b.trust, (n) => n + 1, ifAbsent: () => 1);
    }
    return m;
  }

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
    // ⭐ Khoá đáp án SGV không bao giờ tới trẻ qua tài liệu này.
    if (prov.answerKeysIncluded == true) return null;
    final licence = ContentLicence.parse(j['licence']);
    if (licence == null) return null;
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
      licence: licence,
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
    'licence': licence.name,
    'blocks': [for (final b in blocks) b.toJson()],
    'semantic': [for (final s in semantic) s.toJson()],
    if (tutorScript != null) 'tutorScript': tutorScript!.toJson(),
  };
}
