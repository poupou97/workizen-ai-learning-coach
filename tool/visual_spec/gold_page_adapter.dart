/// ⭐ LANE E2 (round 5) — cầu ĐỌC-MỘT-CHIỀU: trang GOLD (người chú giải bằng
/// tay) → `LessonDocument`, để chạy bộ biên dịch VisualSpec trên NHIỀU MÔN.
///
/// `tool/corpus/tc_gold/*.json` là 54 trang do NGƯỜI chú giải: vai trò từng
/// khối, bbox, thứ tự đọc, trang in. Đây là dữ liệu NHIỀU MÔN NHẤT đang được
/// commit trong repo (10 môn) — nên nó là nền để chứng minh §19 mà một bản
/// clone sạch cũng chạy lại được (`poc-out/` bị gitignore).
///
/// Cầu này KHÔNG sửa gì, KHÔNG sinh nội dung mới, và KHÔNG phải một tầng của
/// sản phẩm: nó chỉ đổi hình dạng dữ liệu đã có. Độ tin đặt là
/// `fixtureFromTrustedCorpus` — chữ đúng là chữ sách nhưng CHƯA qua cổng TC.
library;

import 'dart:convert';
import 'dart:io';

import 'package:learning_coach/core/lesson_model/content_trust.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';

/// Vai trò gold → loại block. Vai trò lạ ⇒ `null` ⇒ BỎ khối (fail-closed),
/// không nhét bừa vào `paragraph`.
LessonBlock? _blockOf(
  Map<String, Object?> raw,
  String book,
  int pagePdf,
  int? pagePrinted,
) {
  final id = raw['id'];
  final role = raw['role'];
  final text = (raw['text'] as String?)?.trim() ?? '';
  final bboxRaw = raw['bbox'];
  if (id is! String || role is! String) return null;
  final bbox = [
    for (final x in (bboxRaw as List? ?? const []))
      if (x is num) x.toDouble(),
  ];
  if (bbox.length != 4) return null;
  final ref = SourceRef(
    book: book,
    pagePdf: pagePdf,
    pagePrinted: pagePrinted,
    bbox: bbox,
    blockId: '$book:p$pagePdf:gold:$id',
    extraction: 'gold-annotation',
  );
  final blockId = '$book:p$pagePdf:gold:$id';
  const trust = ContentTrust.fixtureFromTrustedCorpus;
  if (text.isEmpty) {
    // Khối rỗng trong gold = vùng có mặt nhưng không chép chữ ⇒ GIỮ LẠI thật.
    return WithheldBlock(
      id: blockId,
      sourceRef: ref,
      trust: ContentTrust.withheld,
      reasons: const ['gold_no_text'],
      sourceRole: role,
    );
  }
  return switch (role) {
    'heading' => HeadingBlock(
      id: blockId,
      sourceRef: ref,
      trust: trust,
      text: text,
      sourceRole: role,
    ),
    'body' || 'footnote' || 'speech_bubble' || 'rule' => ParagraphBlock(
      id: blockId,
      sourceRef: ref,
      trust: trust,
      text: text,
      sourceRole: role,
    ),
    'caption' || 'figure_label' => CaptionBlock(
      id: blockId,
      sourceRef: ref,
      trust: trust,
      text: text,
      sourceRole: role,
    ),
    'question' || 'option' || 'answer' => QuestionBlock(
      id: blockId,
      sourceRef: ref,
      trust: trust,
      text: text,
      sourceRole: role,
    ),
    'objective' => ActivityBlock(
      id: blockId,
      sourceRef: ref,
      trust: trust,
      text: text,
      kind: ActivityKind.objective,
      sourceRole: role,
    ),
    'activity' || 'instruction' => ActivityBlock(
      id: blockId,
      sourceRef: ref,
      trust: trust,
      text: text,
      kind: ActivityKind.instruction,
      sourceRole: role,
    ),
    'sidebar' => ActivityBlock(
      id: blockId,
      sourceRef: ref,
      trust: trust,
      text: text,
      kind: ActivityKind.sidebar,
      sourceRole: role,
    ),
    'attribution' => SourceRefBlock(
      id: blockId,
      sourceRef: ref,
      trust: trust,
      text: text,
    ),
    // `table` / `formula` / `diagram` KHÔNG có chữ đọc được thành ô ⇒ giữ lại
    // thật thay vì dựng lại (round 4: 16 biểu thức Toán dựng lại đều sai).
    'table' || 'formula' || 'diagram' => WithheldBlock(
      id: blockId,
      sourceRef: ref,
      trust: ContentTrust.withheld,
      reasons: ['gold_structured_region:$role'],
      sourceRole: role,
    ),
    // page_number / running_head / answer_slot: đồ trang trí, không phải bài.
    _ => null,
  };
}

/// Đọc một trang gold thành `LessonDocument`. `null` ⇒ trang không dựng được.
///
/// ⭐ MẶC ĐỊNH BỎ SÁCH GIÁO VIÊN. Đo lần đầu cho thấy luật mục-đánh-số bắn
/// đúng 6/54 trang, nhưng **3 trong 6 là SGV** — và một trong ba («1. KIẾN
/// THỨC · 2. KĨ NĂNG · 3. PHẨM CHẤT») là danh mục năng lực của giáo viên,
/// thứ tự không mang nghĩa gì cho trẻ. Trang gold có sẵn ô `docType`, nên
/// đây là một CỬA CÓ THẬT chứ không phải phỏng đoán. Đặt
/// `allowTeacherBook: true` để đo lại con số chưa lọc.
LessonDocument? goldPageToDocument(File file, {bool allowTeacherBook = false}) {
  final j = jsonDecode(file.readAsStringSync());
  if (j is! Map) return null;
  if (!allowTeacherBook && j['docType'] != 'SGK') return null;
  final book = j['book'];
  final page = j['page'];
  final subject = j['subject'];
  final grade = j['grade'];
  if (book is! String || page is! num || subject is! String) return null;
  if (grade is! num) return null;
  final lesson = j['lesson'];
  final lessonNo = lesson is Map ? (lesson['number'] as num?)?.toInt() : null;
  final lessonTitle = lesson is Map ? lesson['title'] as String? : null;
  final printed = (j['printed_page'] as num?)?.toInt();

  final blocks = <LessonBlock>[];
  for (final raw in (j['blocks'] as List? ?? const [])) {
    if (raw is! Map) continue;
    final b = _blockOf(
      raw.cast<String, Object?>(),
      book,
      page.toInt(),
      printed,
    );
    if (b != null) blocks.add(b);
  }
  if (blocks.isEmpty) return null;

  return LessonDocument(
    schema: LessonDocument.schemaV1,
    book: book,
    bookTitle: '$subject $grade',
    subject: subject,
    grade: grade.toInt(),
    lessonNo: lessonNo ?? 0,
    title: lessonTitle ?? subject,
    provenance: LessonProvenance(
      trust: ContentTrust.fixtureFromTrustedCorpus,
      book: book,
      pagePdfStart: page.toInt(),
      pagePdfEnd: page.toInt(),
      generator: 'gold_page_adapter.dart@e2-v1',
      sourcePipeline: 'gold-annotation',
      distribution: 'internal-research-only (Founder D4)',
      pagePrintedStart: printed,
      pagePrintedEnd: printed,
    ),
    blocks: blocks,
  );
}

/// Mọi trang gold đang được commit, theo thứ tự tên tệp.
List<File> goldPageFiles([String dir = 'tool/corpus/tc_gold']) {
  final d = Directory(dir);
  if (!d.existsSync()) return const [];
  return d
      .listSync()
      .whereType<File>()
      .where((f) => f.path.endsWith('.json'))
      .toList()
    ..sort((a, b) => a.path.compareTo(b.path));
}
