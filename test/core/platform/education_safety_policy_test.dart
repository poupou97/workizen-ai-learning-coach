/// WAL-110 — safety policy là CODE có test, không phải bảng tài liệu.
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/platform/education_safety_policy.dart';

void main() {
  test('capability CHƯA audit ⇒ disable (fail closed), không null', () {
    expect(decisionFor('capability-la-hoac-moi'), CapabilityDecision.disable);
  });

  test('các REJECT phản-triết-lý bị khoá: chat generic, ads, leaderboard, '
      'analytics, hub-learning-state', () {
    for (final id in [
      'chat-generic',
      'ads',
      'leaderboard',
      'arcade-gamification',
      'growth-engagement',
      'analytics',
      'hub-learning-state',
    ]) {
      expect(decisionFor(id), CapabilityDecision.disable, reason: id);
    }
  });

  test('tiền/quyền là parentGated — PAYMENT ≠ LEARNING TRUTH', () {
    for (final id in ['subscription', 'auth', 'backup-restore', 'ai-usage']) {
      expect(decisionFor(id), CapabilityDecision.parentGated, reason: id);
    }
  });

  test('⭐ pubspec KHÔNG chứa SDK ads/analytics/tracking nào — quét thật',
      () {
    final pubspec = File('pubspec.yaml').readAsStringSync();
    for (final dep in forbiddenDependencies) {
      expect(pubspec.contains(dep), isFalse,
          reason: '$dep xuất hiện trong pubspec — vi phạm '
              'Analytics/Ads ≠ child telemetry (Founder Gate WAL-125)');
    }
    // và cả firebase_core — SAM chưa qua child-privacy pass F42.
    expect(pubspec.contains('firebase'), isFalse,
        reason: 'firebase chưa qua F42 child privacy pass');
  });

  test('không feature «chat» generic nào trong lib/features (F34)', () {
    final dirs = Directory('lib/features')
        .listSync()
        .whereType<Directory>()
        .map((d) => d.path.split(Platform.pathSeparator).last)
        .toList();
    expect(dirs.where((d) => d.contains('chat')), isEmpty,
        reason: 'tutor = TutorSession + cage + guard, không phải chat generic');
  });
}
