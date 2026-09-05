/// ⭐⭐ WAL-210 round 3 (A-runtime) — Founder A8 NEXT BEST LEARNING ACTION:
/// một luật một test; «sang bài tiếp» CHỈ từ tự-làm-được CÓ DẤU validator;
/// không bao giờ bịa phút / phần trăm / mastery.
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/agenda/learning_agenda.dart';
import 'package:learning_coach/core/agenda/lesson_next_action.dart';
import 'package:learning_coach/core/context/learning_context.dart';
import 'package:learning_coach/core/curriculum/khtn6_bai17.dart';
import 'package:learning_coach/core/curriculum/semantic_binding.dart';
import 'package:learning_coach/core/intent/learning_intent.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/next_action.dart' show WorkspaceView;
import 'package:learning_coach/core/student/evidence_validation.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/learning_map_state.dart';
import 'package:learning_coach/core/student/student_lesson_state.dart';

const _ctx = LearningContext(
    learnerId: 'na',
    grade: 6,
    subject: 'KHTN',
    sourceDocumentId: '06-sgk-khoa-hoc-tu-nhien-6',
    lessonNo: 17,
    intent: LearningIntent.review);
const _b18 = LessonRef('06-sgk-khoa-hoc-tu-nhien-6', 18);

const _full = LessonSummary(
    lessonRef: khtn6Bai17,
    hasReadableBlocks: true,
    hasSemanticData: true,
    hasTutorScript: true,
    firstAskPrompt: 'Làm muối từ nước biển dùng cách tách chất nào?',
    nextLesson: _b18);

LearningEvent _ev(EvidenceKind k, {bool? correct, EvidenceValidation? v}) =>
    LearningEvent(
        eventId: 'e-${k.name}-$correct-${v?.validatorId}',
        skillCaseId: khtn6ChonCachTachCaseId,
        kind: k,
        correct: correct,
        at: DateTime(2026, 9, 5),
        sourceDocumentId: khtn6Bai17.sourceDocumentId,
        lessonNo: 17,
        validation: v);

LessonNextAction _act(
        {StudentLessonState? state,
        LessonSummary lesson = _full,
        Set<WorkspaceView> seen = const {},
        LearningContext ctx = _ctx}) =>
    nextBestLessonAction(
        state: state ?? StudentLessonState.unseen(khtn6Bai17),
        context: ctx,
        lesson: lesson,
        viewsSeen: seen);

void main() {
  test('R0 — context chưa giải ra bài / lệch bài ⇒ về mục lục (fail closed)', () {
    const noLesson = LearningContext(learnerId: 'na', grade: 6, subject: 'KHTN');
    expect(_act(ctx: noLesson).rule, 'R0');
    expect(_act(ctx: noLesson).kind, LessonNextKind.backToContents);
    final other = _act(state: StudentLessonState.unseen(_b18));
    expect(other.rule, 'R0', reason: 'state nói bài 18, context nói bài 17');
  });

  test('⭐⭐ R1 — tự làm được CÓ DẤU validator ⇒ sang bài tiếp; không biết bài '
      'tiếp ⇒ về mục lục', () {
    const v = EvidenceValidation(validatorId: 'fraction-check-v1', validatorVersion: '1');
    final st = StudentLessonState.fromEvents(
        khtn6Bai17, [_ev(EvidenceKind.independentAttempt, correct: true, v: v)]);
    expect(st.hasApprovedValidatedSuccess, isTrue);
    final a = _act(state: st);
    expect(a.rule, 'R1');
    expect(a.kind, LessonNextKind.nextLesson);
    expect(a.nextLesson, _b18);
    expect(a.label, 'Sang Bài 18');
    final noNext = _act(
        state: st,
        lesson: const LessonSummary(
            lessonRef: khtn6Bai17,
            hasReadableBlocks: true,
            hasSemanticData: false,
            hasTutorScript: false));
    expect(noNext.rule, 'R1');
    expect(noNext.kind, LessonNextKind.backToContents);
  });

  test('⭐⭐ R1 KHÔNG mở khoá từ tự báo, từ dữ liệu cũ không dấu, từ dấu lạ', () {
    final participation = StudentLessonState.fromEvents(
        khtn6Bai17, [_ev(EvidenceKind.participation)]);
    expect(participation.mapState, LearningMapState.participation);
    expect(_act(state: participation).rule, isNot('R1'));
    final legacy = StudentLessonState.fromEvents(
        khtn6Bai17, [_ev(EvidenceKind.independentAttempt, correct: true)]);
    expect(legacy.mapState, LearningMapState.engaged,
        reason: 'ROUND 4: dữ liệu cũ không dấu = historicalUnvalidated');
    expect(legacy.hasHistoricalUnvalidated, isTrue);
    expect(legacy.historicalUnvalidatedCount, 1);
    expect(legacy.standing, LessonEvidenceStanding.participatedUnverified);
    expect(legacy.hasApprovedValidatedSuccess, isFalse);
    expect(_act(state: legacy).rule, isNot('R1'));
    const rogue = EvidenceValidation(validatorId: 'llm-judge-v1', validatorVersion: '1');
    final rejected = StudentLessonState.fromEvents(
        khtn6Bai17, [_ev(EvidenceKind.independentAttempt, correct: true, v: rogue)]);
    expect(rejected.hasApprovedValidatedSuccess, isFalse);
    expect(_act(state: rejected).rule, isNot('R1'));
  });

  test('R2 — chưa Đọc ⇒ 📖 Đọc (nói thật «chưa có gì ghi lại»)', () {
    final a = _act();
    expect(a.rule, 'R2');
    expect(a.view, WorkspaceView.read);
    expect(a.reason, contains('chưa có gì ghi lại'));
    final withEvidence = _act(
        state: StudentLessonState.fromEvents(khtn6Bai17, [_ev(EvidenceKind.hintShown)]));
    expect(withEvidence.rule, 'R2');
    expect(withEvidence.reason, contains('đọc lại'));
  });

  test('R3 — đã Đọc, có SemanticData, chưa Trực quan ⇒ ✨ Trực quan', () {
    final a = _act(seen: {WorkspaceView.read});
    expect(a.rule, 'R3');
    expect(a.view, WorkspaceView.visual);
  });

  test('R3 bị bỏ qua khi bài KHÔNG có SemanticData ⇒ thẳng tới SAM', () {
    const noSemantic = LessonSummary(
        lessonRef: khtn6Bai17,
        hasReadableBlocks: true,
        hasSemanticData: false,
        hasTutorScript: true);
    final a = _act(seen: {WorkspaceView.read}, lesson: noSemantic);
    expect(a.rule, 'R4');
    expect(a.view, WorkspaceView.tutor);
  });

  test('R4 — Đọc + Trực quan xong, có kịch bản ⇒ 🦉 Học với SAM, nêu ĐÚNG câu '
      'sách hỏi', () {
    final a = _act(seen: {WorkspaceView.read, WorkspaceView.visual});
    expect(a.rule, 'R4');
    expect(a.view, WorkspaceView.tutor);
    expect(a.reason, contains('Làm muối từ nước biển'));
  });

  test('R5 — đi hết ⇒ về mục lục; tự báo ⇒ nói «đã tham gia, chưa chấm»', () {
    final all = {WorkspaceView.read, WorkspaceView.visual, WorkspaceView.tutor};
    final a = _act(seen: all);
    expect(a.rule, 'R5');
    expect(a.kind, LessonNextKind.backToContents);
    final p = _act(
        seen: all,
        state: StudentLessonState.fromEvents(khtn6Bai17, [_ev(EvidenceKind.participation)]));
    expect(p.reason, contains('chưa chấm'));
    expect(p.reason.contains('hiểu'), isFalse);
  });

  test('⭐⭐ ROUND 4 — kết cục «đã tham gia nhưng chưa được kiểm» (R5): ba dạng, '
      'không dạng nào nói «đã hiểu»/«tự làm được»; evidenceNote đi kèm MỌI luật',
      () {
    final all = {WorkspaceView.read, WorkspaceView.visual, WorkspaceView.tutor};
    // (a) dữ liệu cũ có chấm-không-dấu
    final hist = StudentLessonState.fromEvents(
        khtn6Bai17, [_ev(EvidenceKind.independentAttempt, correct: true)]);
    final a = _act(seen: all, state: hist);
    expect(a.rule, 'R5');
    expect(a.kind, LessonNextKind.backToContents);
    expect(a.standing, LessonEvidenceStanding.participatedUnverified);
    expect(a.reason, contains('ghi nhận trước hợp đồng mới'));
    expect(a.reason, contains('chưa tính là tự làm được'));
    expect(a.evidenceNote, contains('ghi nhận trước hợp đồng mới'));
    expect(a.basis, contains('historicalUnvalidated=1'));
    // (b) tự báo
    final part = StudentLessonState.fromEvents(
        khtn6Bai17, [_ev(EvidenceKind.participation)]);
    final b = _act(seen: all, state: part);
    expect(b.reason, contains('chưa chấm'));
    expect(b.evidenceNote, contains('đã tham gia'));
    expect(b.basis, contains('participation=1'));
    // (c) học cùng SAM (xin gợi ý) — chưa lần nào được kiểm
    final eng = StudentLessonState.fromEvents(
        khtn6Bai17, [_ev(EvidenceKind.hintRequested)]);
    final c = _act(seen: all, state: eng);
    expect(c.reason, contains('chưa có lần tự làm được nào được kiểm'));
    expect(c.evidenceNote, contains('chưa có lần tự làm được'));
    // (d) chưa học gì ⇒ không có note; (e) đã kiểm ⇒ R1, không note
    expect(_act(seen: all).evidenceNote, isNull);
    expect(_act(seen: all).standing, LessonEvidenceStanding.none);
    const v = EvidenceValidation(validatorId: 'fraction-check-v1', validatorVersion: '1');
    final ok = _act(
        seen: all,
        state: StudentLessonState.fromEvents(
            khtn6Bai17, [_ev(EvidenceKind.independentAttempt, correct: true, v: v)]));
    expect(ok.rule, 'R1');
    expect(ok.standing, LessonEvidenceStanding.validated);
    expect(ok.evidenceNote, isNull);
    // note cũng có ở R2 (chưa đọc) khi đã có gì ghi lại
    final r2 = _act(state: hist);
    expect(r2.rule, 'R2');
    expect(r2.evidenceNote, contains('ghi nhận trước hợp đồng mới'));
    for (final act in [a, b, c, r2]) {
      expect(act.reason.contains('hiểu'), isFalse, reason: act.reason);
      expect(act.reason.startsWith('Con đã tự làm được'), isFalse);
      expect(RegExp(r'\d+\s*(phút|%)').hasMatch(act.evidenceNote ?? ''), isFalse);
    }
  });

  test('R5 — bài rỗng (không đọc được gì) ⇒ về mục lục, nói thật', () {
    const empty = LessonSummary(
        lessonRef: khtn6Bai17,
        hasReadableBlocks: false,
        hasSemanticData: false,
        hasTutorScript: false);
    final a = _act(lesson: empty);
    expect(a.kind, LessonNextKind.backToContents);
    expect(a.reason, contains('chưa đọc được'));
  });

  test('⭐⭐ KHÔNG BAO GIỜ bịa phút / phần trăm / mastery — quét mọi luật', () {
    final reasons = <String>[];
    for (final seen in [
      <WorkspaceView>{},
      {WorkspaceView.read},
      {WorkspaceView.read, WorkspaceView.visual},
      {WorkspaceView.read, WorkspaceView.visual, WorkspaceView.tutor},
    ]) {
      for (final state in [
        StudentLessonState.unseen(khtn6Bai17),
        StudentLessonState.fromEvents(khtn6Bai17, [_ev(EvidenceKind.participation)]),
        StudentLessonState.fromEvents(khtn6Bai17, [
          _ev(EvidenceKind.independentAttempt,
              correct: true,
              v: const EvidenceValidation(
                  validatorId: 'fraction-check-v1', validatorVersion: '1'))
        ]),
      ]) {
        reasons.add(_act(seen: seen, state: state).reason);
      }
    }
    final banned = RegExp(r'\d+\s*(phút|%)|mastery|vững|thành thạo', caseSensitive: false);
    for (final r in reasons) {
      expect(banned.hasMatch(r), isFalse, reason: r);
    }
  });

  test('LessonSummary.fromDocument đọc đúng fixture mẫu Bài 17; '
      'NextBestLearningAction.forLesson uỷ quyền', () {
    final j = jsonDecode(File(
            'assets/fixtures/synthetic/lesson-06-sgk-khoa-hoc-tu-nhien-6-b17.synthetic.json')
        .readAsStringSync()) as Map;
    final d = LessonDocument.fromJson(j.cast<String, Object?>(), assetBase: 'x/')!;
    final s = LessonSummary.fromDocument(d, nextLesson: _b18);
    expect(s.lessonRef, khtn6Bai17);
    expect(s.hasReadableBlocks, isTrue);
    expect(s.hasSemanticData, isTrue);
    expect(s.hasTutorScript, isTrue);
    expect(s.firstAskPrompt, contains('Làm muối'));
    final a = NextBestLearningAction.forLesson(
        state: StudentLessonState.unseen(khtn6Bai17),
        context: _ctx,
        lesson: s,
        viewsSeen: const {});
    expect(a.rule, 'R2');
  });
}
