/// WAL-119 — Entitlement resolver: role×PIN×tier; PAYMENT ≠ LEARNING TRUTH
/// giữ bằng CẤU TRÚC (quét mã) + never-monetize fail-closed.
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/platform/entitlement.dart';

Entitlement r(ParentFeature f,
        {AppRole role = AppRole.parent,
        SubscriptionTier tier = SubscriptionTier.basicFree,
        bool pin = true}) =>
    resolveEntitlement(feature: f, role: role, tier: tier, pinVerified: pin);

void main() {
  test('⭐ PAYMENT ≠ LEARNING TRUTH theo CẤU TRÚC: tầng học tập không biết '
      'subscription tồn tại', () {
    final banned = ['subscription', 'premium', 'SubscriptionTier', 'tier'];
    final hits = <String>[];
    for (final dir in ['lib/core/student', 'lib/core/adaptive',
        'lib/core/curriculum', 'lib/core/tutor', 'lib/core/pedagogy']) {
      for (final f in Directory(dir)
          .listSync(recursive: true)
          .whereType<File>()
          .where((f) => f.path.endsWith('.dart'))) {
        final src = f.readAsStringSync().toLowerCase();
        for (final b in banned) {
          if (src.contains(b.toLowerCase())) hits.add('${f.path}: $b');
        }
      }
    }
    expect(hits, isEmpty,
        reason: '⭐ đột biến đưa tier vào engine ⇒ test này đỏ — đổi gói '
            'KHÔNG THỂ đổi mastery/evidence/hint vì engine không có chỗ nhận nó');
  });

  test('⭐ NEVER-MONETIZE: hỏi entitlement cho learning capability = lỗi', () {
    for (final c in neverMonetize) {
      expect(() => refuseLearningCapability(c), throwsArgumentError,
          reason: c);
    }
    expect(neverMonetize, containsAll(
        ['hint', 'answer', 'assessment', 'mastery', 'evidence', 'streak']));
  });

  test('BASIC là QUYỀN — free vô điều kiện, tier nào cũng vậy', () {
    for (final f in [
      ParentFeature.consentPrivacy,
      ParentFeature.exportDelete,
      ParentFeature.safetyControls,
      ParentFeature.createSwitchLearner,
      ParentFeature.basicStatus,
    ]) {
      expect(r(f, tier: SubscriptionTier.basicFree).allowed, isTrue,
          reason: '⭐ đột biến paywall consent/privacy ⇒ đỏ: $f');
      expect(r(f, tier: SubscriptionTier.premiumFamily).allowed, isTrue);
    }
  });

  test('PREMIUM candidates: basic bị từ chối CÓ LÝ DO ĐỌC ĐƯỢC, premium mở', () {
    final d = r(ParentFeature.dailyBrief);
    expect(d.allowed, isFalse);
    expect(d.reason, contains('learning của con KHÔNG bị khoá'),
        reason: 'lời từ chối phải nói thật điều không bị khoá');
    expect(
        r(ParentFeature.dailyBrief, tier: SubscriptionTier.premiumFamily)
            .allowed,
        isTrue);
    expect(
        r(ParentFeature.parentCoach, tier: SubscriptionTier.premiumFamily)
            .allowed,
        isTrue);
  });

  test('ROLE + SAFETY gate: student bị chặn; parent chưa PIN bị chặn', () {
    expect(r(ParentFeature.basicStatus, role: AppRole.student).allowed, isFalse);
    expect(r(ParentFeature.dailyBrief, role: AppRole.student,
            tier: SubscriptionTier.premiumFamily).allowed, isFalse,
        reason: 'premium KHÔNG vượt được role gate');
    expect(r(ParentFeature.basicStatus, pin: false).allowed, isFalse);
    expect(r(ParentFeature.basicStatus, pin: false).reason, contains('PIN'));
  });
}
