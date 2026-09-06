/// ⭐ LANE E2 (round 5) §21 — DỰNG SẴN artefact VisualSpec, NGOÀI giờ chạy.
///
///     dart run tool/visual_spec/build_specs.dart [--out <đường dẫn>]
///
/// Không có lệnh gọi mô hình nào trong tệp này, và cũng không có trong cây
/// import của nó (`lib/core/visual_spec/**` chỉ import `lesson_model`). Đó là
/// cách «0 lệnh gọi LLM lúc chạy» được GIỮ, chứ không phải được hứa.
///
/// Hai đường vào, cùng một `VisualSpec` ra:
/// - tầng ngữ nghĩa có kiểu (`SemanticData`) → `compileLesson`
/// - tài liệu (mục đánh số) → `compileNumberedSequence`   (PROPOSED, §19)
library;

import 'dart:convert';
import 'dart:io';

import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/visual_spec/document_sequence_rule.dart';
import 'package:learning_coach/core/visual_spec/semantic_to_spec.dart';
import 'package:learning_coach/core/visual_spec/visual_spec.dart';
import 'package:learning_coach/core/visual_spec/visual_spec_artifact.dart';

import 'gold_page_adapter.dart';

const _fixtures = [
  'assets/fixtures/synthetic/lesson-06-sgk-khoa-hoc-tu-nhien-6-b17.synthetic.json',
  'assets/fixtures/synthetic/lesson-05-sgk-lich-su-va-dia-li-5-b8.synthetic.json',
  'assets/fixtures/real/lesson-06-sgk-khoa-hoc-tu-nhien-6-b17.json',
];

void main(List<String> args) {
  final outIdx = args.indexOf('--out');
  final out = outIdx >= 0 && outIdx + 1 < args.length
      ? args[outIdx + 1]
      : 'poc-out/round5/lane-e2/visual-specs.json';

  final specs = <String, VisualSpec>{};
  final bySubject = <String, Map<String, int>>{};
  final rows = <String>[];
  var lessonsSeen = 0;
  var lessonsWithSpec = 0;

  void note(String subject, String family) {
    bySubject.putIfAbsent(subject, () => {}).update(
      family,
      (n) => n + 1,
      ifAbsent: () => 1,
    );
  }

  // ── đường 1: tầng ngữ nghĩa có kiểu ──
  for (final path in _fixtures) {
    final f = File(path);
    if (!f.existsSync()) {
      rows.add('SKIP  (không có trên máy này)  $path');
      continue;
    }
    final doc = LessonDocument.fromJson(
      (jsonDecode(f.readAsStringSync()) as Map).cast<String, Object?>(),
    );
    if (doc == null) {
      rows.add('FAIL  (không parse được)      $path');
      continue;
    }
    lessonsSeen++;
    final r = compileLesson(doc);
    final spec = r.spec;
    if (spec == null) {
      rows.add('NONE  ${doc.subject} ${doc.book}  (${r.dropped})');
      continue;
    }
    lessonsWithSpec++;
    specs['${doc.book}#${doc.lessonNo}'] = spec;
    for (final s in spec.sections) {
      note(doc.subject, s.family);
    }
    rows.add(
      'SPEC  ${doc.subject.padRight(12)} ${doc.book}#${doc.lessonNo}  '
      'sections=${spec.sections.length} '
      'families=${[for (final s in spec.sections) s.family]}',
    );
  }

  // ── đường 2: tài liệu (mục đánh số) — NHIỀU MÔN, §19 ──
  // Đo TRƯỚC-LỌC để con số dương-tính-giả không biến mất khỏi báo cáo.
  var firedAll = 0;
  var firedTeacher = 0;
  for (final f in goldPageFiles()) {
    final any = goldPageToDocument(f, allowTeacherBook: true);
    if (any == null) continue;
    if (compileNumberedSequence(any) == null) continue;
    firedAll++;
    if (goldPageToDocument(f) == null) firedTeacher++;
  }

  for (final f in goldPageFiles()) {
    final doc = goldPageToDocument(f);
    if (doc == null) continue;
    lessonsSeen++;
    final section = compileNumberedSequence(doc);
    if (section == null) continue;
    lessonsWithSpec++;
    final key = '${doc.book}#p${doc.provenance.pagePdfStart}';
    specs[key] = VisualSpec(
      specVersion: VisualSpec.currentVersion,
      primary: section,
      compiledBy: numberedSectionSequenceRule,
    );
    note(doc.subject, section.family);
    rows.add(
      'SEQ   ${doc.subject.padRight(12)} $key  '
      'nodes=${section.nodes.length}  «${section.nodes.first.label}»',
    );
  }

  final artifact = VisualSpecArtifact(
    artifactVersion: VisualSpecArtifact.currentVersion,
    // Cố định để hai lần dựng cho ra BYTE Y HỆT (kiểm replay tất định).
    builtAt: '2026-09-06T00:00:00Z',
    builder: '$semanticToSpecVersion+$numberedSectionSequenceRule',
    specs: specs,
  );
  final encoded = artifact.encode();
  File(out).parent.createSync(recursive: true);
  File(out).writeAsStringSync(encoded);

  for (final r in rows) {
    stdout.writeln(r);
  }
  stdout.writeln('');
  stdout.writeln('— PHỦ THEO MÔN (họ hình × môn) —');
  final subjects = bySubject.keys.toList()..sort();
  for (final s in subjects) {
    stdout.writeln('  ${s.padRight(14)} ${bySubject[s]}');
  }
  stdout.writeln('');
  stdout.writeln('tài liệu đã đọc      : $lessonsSeen');
  stdout.writeln('tài liệu có spec     : $lessonsWithSpec');
  stdout.writeln('spec trong artefact  : ${artifact.lessonCount}');
  stdout.writeln('section trong artefact: ${artifact.sectionCount}');
  stdout.writeln('họ hình               : ${artifact.sectionsByFamily}');
  stdout.writeln('môn có ít nhất 1 spec : ${subjects.length}');
  stdout.writeln(
    'luật mục-đánh-số      : bắn $firedAll/${goldPageFiles().length} trang gold; '
    '$firedTeacher trong đó là SÁCH GIÁO VIÊN (đã lọc, không tới trẻ)',
  );
  stdout.writeln('artefact              : $out (${encoded.length} bytes)');
  stdout.writeln('lệnh gọi mô hình      : 0 (không có trong cây import)');
}
