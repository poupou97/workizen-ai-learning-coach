/// WAL-50 — BandDensityScope wire: cùng widget, band khác ⇒ mascot khác SIZE.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/app/theme/band_density_scope.dart';
import 'package:learning_coach/app/theme/wal_tokens.dart';
import 'package:learning_coach/core/context/learning_context.dart';
import 'package:learning_coach/core/tutor/learning_activity.dart';
import 'package:learning_coach/features/shell/reader_screen.dart';

const _a = LearningActivity(
  activityId: 'a',
  prompt: '1. Câu hỏi?',
  response: ResponseKind.readRespond,
  conceptId: 'c',
  passage: 'Đoạn văn thật để đọc.',
);
const _ctx = LearningContext(learnerId: 'na', grade: 5);

Future<double> _chipWidth(WidgetTester t, {WalBandDensity? d}) async {
  final screen =
      ReaderScreen(key: UniqueKey(), activity: _a, learningContext: _ctx);
  await t.pumpWidget(MaterialApp(
      home: d == null
          ? screen
          : BandDensityScope(density: d, child: screen)));
  await t.pump();
  final img = t.widget<Image>(find.byType(Image).first);
  return img.width!;
}

void main() {
  testWidgets('⭐ không scope ⇒ tiểu học 56; THCS ⇒ 40; THPT ⇒ 32 — CÙNG widget',
      (t) async {
    expect(await _chipWidth(t), 56.0,
        reason: 'mặc định an toàn: to/rõ cho tiểu học');
    expect(await _chipWidth(t, d: WalBandDensity.lowerSecondary), 40.0,
        reason: '⭐ đột biến densityOf bỏ scope ⇒ test này đỏ');
    expect(await _chipWidth(t, d: WalBandDensity.upperSecondary), 32.0);
  });
}
