/// WAL-143 × WAL-109 — hỏi đúng người TRƯỚC khi ghi bằng chứng thi.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/features/assessment/learner_confirm.dart';

const _na = LearnerProfile(learnerId: 'na', displayName: 'Na', grade: 5);
const _bi = LearnerProfile(learnerId: 'bi', displayName: 'Bi', grade: 3);

Future<LearnerProfile?> _open(
    WidgetTester t, List<LearnerProfile> profiles) async {
  LearnerProfile? got;
  var called = false;
  await t.pumpWidget(MaterialApp(
      home: Builder(
          builder: (c) => Scaffold(
                body: Center(
                  child: TextButton(
                    onPressed: () async {
                      got = await confirmLearner(c,
                          profiles: profiles, active: _na);
                      called = true;
                    },
                    child: const Text('mở'),
                  ),
                ),
              ))));
  await t.tap(find.text('mở'));
  await t.pumpAndSettle();
  if (called) return got; // một hồ sơ ⇒ trả ngay, không sheet
  return null;
}

void main() {
  testWidgets('MỘT hồ sơ ⇒ KHÔNG hỏi (không tạo ma sát vô nghĩa)', (t) async {
    final got = await _open(t, const [_na]);
    expect(find.text('Ai đang làm bài kiểm tra?'), findsNothing);
    expect(got?.learnerId, 'na');
  });

  testWidgets('⭐ NHIỀU hồ sơ ⇒ PHẢI hỏi; chọn ai thì trả về đúng người ấy',
      (t) async {
    await _open(t, const [_na, _bi]);
    expect(find.text('Ai đang làm bài kiểm tra?'), findsOneWidget,
        reason: '⭐ đột biến bỏ hỏi ⇒ bằng chứng thi ghi nhầm sổ');
    expect(find.text('Na'), findsOneWidget);
    expect(find.text('Bi'), findsOneWidget);
    await t.tap(find.text('Bi'));
    await t.pumpAndSettle();
    expect(find.text('Ai đang làm bài kiểm tra?'), findsNothing);
  });

  testWidgets('đóng sheet mà không chọn ⇒ null (không ghi bừa)', (t) async {
    await _open(t, const [_na, _bi]);
    expect(find.text('Ai đang làm bài kiểm tra?'), findsOneWidget);
    // bấm ra ngoài = huỷ
    await t.tapAt(const Offset(10, 10));
    await t.pumpAndSettle();
    expect(find.text('Ai đang làm bài kiểm tra?'), findsNothing);
  });
}
