/// WAL-69 — luật bốn chiều + LUẬT KHEN giữ bằng test.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/core/tutor/tutor_feedback.dart';

void main() {
  // mọi tổ hợp đầu vào có nghĩa
  final all = [
    for (final correct in [true, false])
      for (final sup in SupportLevel.values)
        for (final sc in [true, false])
          if (!sc || correct) // tự-sửa chỉ có nghĩa khi kết cục đúng
            feedbackFor(correct: correct, maxSupport: sup, selfCorrected: sc),
  ];

  test('⭐ LUẬT KHEN: không một lời khen nào chạm danh sách cấm khen-tư-chất',
      () {
    for (final f in all) {
      for (final banned in bannedAbilityPraise) {
        expect(f.praise.toLowerCase().contains(banned), isFalse,
            reason: 'khen tư chất bị cấm (Dweck + doctrine): '
                '"$banned" trong "${f.praise}"');
      }
    }
  });

  test('EVIDENCE luôn nói thật: có hỗ trợ thì evidenceNote không bao giờ '
      'là countsAsIndependent', () {
    for (final sup in SupportLevel.values.where((s) => s != SupportLevel.none)) {
      final f =
          feedbackFor(correct: true, maxSupport: sup, selfCorrected: false);
      expect(f.evidenceNote, EvidenceNote.supportedOnly);
      expect(f.evidenceLine, contains('chưa tính'),
          reason: 'phải NÓI THẲNG với trẻ, không giấu trong log');
    }
  });

  test('sai KHÔNG bị phán xét: affect ghi nhận nỗ lực, evidence ghi lần thử',
      () {
    final f = feedbackFor(
        correct: false,
        maxSupport: SupportLevel.hint,
        selfCorrected: false);
    expect(f.evidenceNote, EvidenceNote.attemptRecorded);
    expect(f.praise.toLowerCase(), isNot(contains('sai rồi')));
    expect(f.praise, contains('thử'));
  });

  test('tự sửa được nâng riêng — mạnh hơn cả đúng-ngay (doctrine selfCorrection)',
      () {
    final f = feedbackFor(
        correct: true, maxSupport: SupportLevel.none, selfCorrected: true);
    expect(f.evidenceNote, EvidenceNote.countsAsSelfCorrection);
    expect(f.praise, contains('tự sửa'));
  });

  test('bốn chiều độc lập: correctness đúng + assistance cao + evidence '
      'supported cùng tồn tại — không chiều nào nuốt chiều nào', () {
    final f = feedbackFor(
        correct: true,
        maxSupport: SupportLevel.fullSolution,
        selfCorrected: false);
    expect(f.correct, isTrue); // CORRECTNESS: đúng
    expect(f.maxSupport, SupportLevel.fullSolution); // ASSISTANCE: tối đa
    expect(f.evidenceNote, EvidenceNote.supportedOnly); // EVIDENCE: không công
    expect(f.praise, isNotEmpty); // AFFECT: vẫn ấm — không chiều nào trừng phạt
  });
}
