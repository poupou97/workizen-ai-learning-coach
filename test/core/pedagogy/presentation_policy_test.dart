/// WAL-132 — PresentationPolicy resolver: subject×band×assistance → surface+
/// format. Mỗi bất biến một đột biến làm đỏ (reason).
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/pedagogy/presentation_policy.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/core/tutor/learning_activity.dart';

PresentationBinding r({
  String family = 'TOAN',
  ResponseKind? kind,
  bool src = false,
  GradeBand band = GradeBand.b3_5,
  SupportLevel a = SupportLevel.none,
  DeviceClass d = DeviceClass.phone,
}) =>
    resolvePresentation(
        subjectFamily: family,
        response: kind,
        sourceExcerpt: src,
        band: band,
        assistance: a,
        device: d);

void main() {
  test('bảng ánh xạ khớp 3 PROTOTYPE THẬT đang chạy (drift guard)', () {
    // Workspace (WAL-108) · Reader (WAL-113 B1) · SourceReader (WAL-113 B2)
    expect(r(kind: ResponseKind.numericStep).surface,
        PresentationSurface.mathWorkspace);
    expect(r(family: 'TV-VAN', kind: ResponseKind.readRespond).surface,
        PresentationSurface.reader);
    expect(r(family: 'SU', src: true).surface,
        PresentationSurface.sourceReader);
    expect(r(family: 'TV-VAN', kind: ResponseKind.compose).format,
        PresentationFormat.draftRevision);
    expect(r(kind: ResponseKind.selectIdentify).format,
        PresentationFormat.choiceChips);
    // nối với tầng activity (resolveSurface) — hai tầng không trôi khỏi nhau
    expect(resolveSurface(const LearningActivity(
            activityId: 'a', prompt: 'Đọc rồi trả lời',
            response: ResponseKind.readRespond, conceptId: 'c', passage: 'x'))
        .name, 'reader');
  });

  test('⭐ KHÔNG CHAT-BUBBLE: enum không có chat; không khớp ⇒ UNSUPPORTED',
      () {
    expect(
        PresentationSurface.values.map((v) => v.name).any(
            (n) => n.toLowerCase().contains('chat')),
        isFalse,
        reason: 'bất biến §8 nằm trong VOCABULARY — không có chỗ rơi về');
    expect(r(kind: ResponseKind.shortText).surface,
        PresentationSurface.unsupported,
        reason: '⭐ đột biến map shortText→reader ⇒ test đỏ');
    expect(r(kind: null).surface, PresentationSurface.unsupported);
    expect(r(family: 'KHOA', kind: ResponseKind.numericStep).surface,
        PresentationSurface.unsupported,
        reason: 'numericStep ngoài Toán chưa được prove — không ép');
  });

  test('⭐ F5 «một Method một presentation — SAI»: assistance đổi ⇒ chi tiết đổi',
      () {
    final none = r(kind: ResponseKind.numericStep, a: SupportLevel.none);
    final worked =
        r(kind: ResponseKind.numericStep, a: SupportLevel.workedStep);
    expect(none.surface, worked.surface, reason: 'cùng surface');
    expect(none.detail.showWorkedRegion, isFalse);
    expect(worked.detail.showWorkedRegion, isTrue,
        reason: '⭐ đột biến bỏ chiều assistance ⇒ test đỏ (F5 tái sinh)');
    expect(r(kind: ResponseKind.numericStep, a: SupportLevel.hint)
        .detail.showWorkedRegion, isFalse,
        reason: 'hint CHƯA mở worked-region — ranh giới ở workedStep');
  });

  test('band 1-2 chữ to hơn band 3-5; ngoài 1-12 ⇒ band null (fail closed)',
      () {
    expect(textScaleFor(GradeBand.b1_2),
        greaterThan(textScaleFor(GradeBand.b3_5)),
        reason: '⭐ đột biến b1_2→1.0 ⇒ test đỏ');
    expect(bandForGrade(5), GradeBand.b3_5);
    expect(bandForGrade(1), GradeBand.b1_2);
    expect(bandForGrade(12), GradeBand.b10_12);
    expect(bandForGrade(0), isNull);
    expect(bandForGrade(13), isNull);
  });

  test('surface môn nào của môn đó: tư liệu ngoài SU ⇒ unsupported', () {
    expect(r(family: 'TOAN', src: true).surface,
        PresentationSurface.unsupported,
        reason: 'không mượn SourceReader cho môn khác vì «trông giống»');
  });

  test('mọi binding mang presentationPolicyVersion', () {
    expect(r(kind: ResponseKind.numericStep).version, 'presentation-v1');
    expect(r(kind: null).version, 'presentation-v1',
        reason: 'cả binding unsupported cũng có version — truy được policy');
  });

  test('tablet ⇒ twoPane; phone ⇒ không', () {
    expect(r(kind: ResponseKind.readRespond, family: 'TV-VAN',
            d: DeviceClass.tablet).detail.twoPane, isTrue);
    expect(r(kind: ResponseKind.readRespond, family: 'TV-VAN')
        .detail.twoPane, isFalse);
  });
}
