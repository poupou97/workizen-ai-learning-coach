/// WAL-109 — PIN + activeLearner: last-wins, sống qua đĩa.
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/file_store.dart';
import 'package:learning_coach/core/store/learner_store.dart';

void main() {
  test('PIN: chưa đặt = null; đặt rồi đổi = bản sau thắng', () async {
    final s = JsonlLearnerStore();
    expect(await s.parentPin(), isNull);
    await s.saveParentPin('1234');
    await s.saveParentPin('9999');
    expect(await s.parentPin(), '9999');
  });

  test('activeLearner: sống qua «restart» file store', () async {
    final tmp = await Directory.systemTemp.createTemp('sam-gate');
    try {
      final f = File('${tmp.path}/store.jsonl');
      final s1 = await FileLearnerStore.open(f);
      await s1.saveActiveLearner('l-b');
      await s1.saveParentPin('2468');
      final s2 = await FileLearnerStore.open(f);
      expect(await s2.activeLearnerId(), 'l-b');
      expect(await s2.parentPin(), '2468');
    } finally {
      await tmp.delete(recursive: true);
    }
  });
}
