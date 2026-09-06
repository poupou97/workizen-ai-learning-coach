/// LANE E2 (round 5) — bộ biên dịch `SemanticData → VisualSpec` trên FIXTURE
/// THẬT ĐANG COMMIT, và điều nó làm mà tầng cũ không làm:
///
/// **kiểm chứng nhãn có nguyên văn trong block nguồn hay không.** Mô hình cũ
/// không có ô nào để phân biệt «sách viết câu này» với «SAM nối hai ý»; một
/// `ConceptRelation` do luật nào sinh ra cũng hiện lên giống hệt nhau.
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/content_trust.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/semantic_data.dart';
import 'package:learning_coach/core/visual_spec/semantic_to_spec.dart';
import 'package:learning_coach/core/visual_spec/visual_spec.dart';

const _khtn =
    'assets/fixtures/synthetic/lesson-06-sgk-khoa-hoc-tu-nhien-6-b17.synthetic.json';
const _history =
    'assets/fixtures/synthetic/lesson-05-sgk-lich-su-va-dia-li-5-b8.synthetic.json';

LessonDocument _doc(String path) {
  final f = File(path);
  expect(f.existsSync(), isTrue, reason: 'fixture $path phải có trong repo');
  return LessonDocument.fromJson(
    (jsonDecode(f.readAsStringSync()) as Map).cast<String, Object?>(),
  )!;
}

void main() {
  test('KHTN: biên dịch ra hình CHÍNH + hình PHỤ (composition)', () {
    final r = compileLesson(_doc(_khtn));
    final spec = r.spec!;
    expect(r.dropped, isEmpty);
    expect(spec.primary.family, VisualFamily.process);
    expect([for (final s in spec.secondary) s.family], [
      VisualFamily.comparison,
    ]);
    // Hình chính = hình có NHIỀU nút đọc được nhất — tất định, không «đẹp hơn».
    expect(spec.primary.nodes.where((n) => !n.isWithheld).length, 3);
  });

  test('CHUỖI NGUỒN: mọi nút → block có thật → trang + bbox', () {
    final doc = _doc(_khtn);
    final spec = compileLesson(doc).spec!;
    for (final section in spec.sections) {
      for (final n in section.nodes) {
        final b = doc.blockById(n.provenance.primaryBlockId);
        expect(b, isNotNull, reason: 'nút ${n.id} trỏ vào hư không');
        expect(b!.sourceRef.bbox.length, 4);
        expect(b.sourceRef.pagePdf, greaterThan(0));
      }
      // Tiêu đề cũng phải có nguồn — không có tiêu đề «SAM tự đặt».
      expect(section.titleProvenance.isGrounded, isTrue);
      for (final e in section.edges) {
        expect(e.provenance.isGrounded, isTrue);
      }
    }
  });

  test('§8 mọi Ô so sánh mang nguồn, và KHAI là thừa kế của hàng', () {
    final spec = compileLesson(_doc(_khtn)).spec!;
    final table = spec.secondary.single;
    expect(table.nodes, isNotEmpty);
    for (final n in table.nodes) {
      expect(n.provenance.isGrounded, isTrue);
      expect(n.provenance.derivationRule, contains('cell-inherits-row-v1'));
    }
    // Lưới dựng lại được từ hai trục.
    expect(table.rows.length, 2);
    expect(table.columns.length, 1);
    expect(table.cellAt(table.rows[0], table.columns[0]), isNotNull);
  });

  test('bước GIỮ LẠI vẫn là một nút — chỗ trống thật, không biến mất', () {
    final spec = compileLesson(_doc(_khtn)).spec!;
    final held = spec.primary.nodes.where((n) => n.isWithheld).toList();
    expect(held.length, 1);
    expect(held.single.label, isNull);
    expect(held.single.provenance.isGrounded, isTrue);
    expect(spec.primary.childSummary, contains('SAM chưa đọc được'));
  });

  test('mũi tên thứ tự KHÔNG BAO GIỜ khai là câu của sách', () {
    final spec = compileLesson(_doc(_khtn)).spec!;
    expect(spec.primary.edges, isNotEmpty);
    for (final e in spec.primary.edges) {
      expect(e.status, InferenceStatus.derivedDeterministic);
      expect(e.kind, EdgeKind.sequence);
    }
  });

  test('Lịch sử: cùng bộ biên dịch, họ hình khác, vẫn đủ nguồn', () {
    final doc = _doc(_history);
    final spec = compileLesson(doc).spec!;
    expect(spec.primary.family, VisualFamily.timeline);
    expect(spec.primary.nodes.length, 5);
    for (final n in spec.primary.nodes) {
      expect(n.badge, isNotNull, reason: 'mốc phải mang năm sách nêu');
      expect(doc.blockById(n.provenance.primaryBlockId), isNotNull);
    }
    for (final e in spec.primary.edges) {
      expect(e.kind, EdgeKind.precedes);
      expect(e.status, InferenceStatus.derivedDeterministic);
    }
  });

  test('⭐ nhãn KHÔNG có trong chữ block ⇒ `inferred`, không phải `stated`', () {
    // Đây là năng lực THẬT mà mô hình cũ không có: bộ biên dịch ĐỌC chữ của
    // block rồi mới quyết định, chứ không tin lời khai của tầng trên.
    final doc = _doc(_khtn);
    final block = doc.blocks.firstWhere((b) => LessonDocument.textOf(b) != null);
    final text = LessonDocument.textOf(block)!;

    final verbatim = ProcessSemantic(
      id: 'p',
      title: 'thử',
      trust: ContentTrust.fixtureSynthetic,
      derivation: 'test-rule-v1',
      steps: [
        ProcessStep(order: 1, sourceBlockId: block.id, text: text),
        ProcessStep(
          order: 2,
          sourceBlockId: block.id,
          text: 'SAM tự viết một câu không có trong sách',
        ),
      ],
    );
    final s = compileSection(doc, verbatim)!;
    expect(s.nodes[0].status, InferenceStatus.stated);
    expect(s.nodes[1].status, InferenceStatus.inferred);
  });

  test('so khớp KHÔNG bỏ dấu thanh — «phẫu» ≠ «phễu»', () {
    expect(normalizeForMatch('· Phẫu thuật'), 'phẫu thuật');
    expect(normalizeForMatch('Phẫu') == normalizeForMatch('Phễu'), isFalse);
  });

  test('FAIL CLOSED: hình có block nguồn không tồn tại ⇒ BỎ hình, ghi lý do',
      () {
    final doc = _doc(_khtn);
    final broken = ProcessSemantic(
      id: 'p-hong',
      title: 'thử',
      trust: ContentTrust.fixtureSynthetic,
      derivation: 'test-rule-v1',
      steps: const [
        ProcessStep(order: 1, sourceBlockId: 'khong-ton-tai', text: 'x'),
        ProcessStep(order: 2, sourceBlockId: 'khong-ton-tai-2', text: 'y'),
      ],
    );
    expect(compileSection(doc, broken), isNull);

    // Một hình hỏng KHÔNG được kéo cả bài xuống: các hình khác vẫn ra.
    final mixed = LessonDocument(
      schema: doc.schema,
      book: doc.book,
      bookTitle: doc.bookTitle,
      subject: doc.subject,
      grade: doc.grade,
      lessonNo: doc.lessonNo,
      title: doc.title,
      provenance: doc.provenance,
      blocks: doc.blocks,
      semantic: [...doc.semantic, broken],
    );
    final r = compileLesson(mixed);
    expect(r.spec, isNotNull);
    expect(r.dropped.keys, contains('p-hong'));
    expect(r.dropped['p-hong'], startsWith('missing_source_block:'));
  });

  test('độ tin của hình = độ tin YẾU NHẤT của nguồn, không lạc quan', () {
    final spec = compileLesson(_doc(_khtn)).spec!;
    expect(spec.trust, ContentTrust.fixtureSynthetic);
    expect(spec.trust.isProductionTruth, isFalse);
    expect(spec.trust.requiresFixtureChip, isTrue);
  });
}
