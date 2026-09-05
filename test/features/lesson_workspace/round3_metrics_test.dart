/// ROUND 3 §7 — bốn con số đầu vào, ĐẾM BẰNG MÁY trên fixture thật (bỏ qua ở
/// máy không có fixture), in ra để báo cáo trích — không cộng, không trung
/// bình:
///   SOURCE REALITY  — phần tử nhìn thấy theo `ContentTrust`;
///   SOURCE TRUST    — phần tử qua đường sản xuất tin được (`trustedCorpus`);
///   PEDAGOGY REALITY— bước tutor runtimeGuided vs prototypeScripted (A7);
///   EVIDENCE REALITY— bước có validator được duyệt (A3) — hôm nay 0.
/// Fixture mẫu (CI) kiểm cùng bất biến: KHÔNG phần tử trustedCorpus, KHÔNG
/// validator, KHÔNG bước nào tự nhận runtime khi không có block nguồn.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/content_trust.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/pedagogy/pedagogy_runtime.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/runtime_plan.dart';

import 'support.dart';

Map<String, Object> _metrics(LessonDocument d) {
  final census = d.capabilityCensus();
  final byTrust = <ContentTrust, int>{};
  var visible = 0;
  for (final r in census) {
    byTrust[r.trust] = (byTrust[r.trust] ?? 0) + r.count;
    visible += r.count;
  }
  final plan = planForDoc(d, learnerId: 'na');
  return {
    'visibleElements': visible,
    'byTrust': {for (final e in byTrust.entries) e.key.name: e.value},
    'sourceTrust(trustedCorpus)': byTrust[ContentTrust.trustedCorpus] ?? 0,
    'tutorStepsPlanned': plan?.steps.length ?? 0,
    'runtimeGuided': plan?.runtimeGuidedCount ?? 0,
    'prototypeScripted': plan?.prototypeCount ?? 0,
    'planRefusals': plan?.planRefusals ?? const [],
    'stepsWithValidator':
        plan?.steps.where((s) => s.validator != null).length ?? 0,
    'refusalCodes': {
      for (final s in plan?.steps ?? const <PlannedStep>[])
        for (final r in s.refusals) r.split(':').first,
    }.toList()..sort(),
  };
}

void main() {
  test('fixture MẪU: 0 trustedCorpus · 0 validator · runtime 4/12', () {
    final m = _metrics(loadSyntheticDoc());
    expect(m['sourceTrust(trustedCorpus)'], 0);
    expect(m['stepsWithValidator'], 0);
    expect(m['runtimeGuided'], 4);
    expect(m['prototypeScripted'], 8);
    // ignore: avoid_print
    print('ROUND3-METRICS synthetic: $m');
  });

  test('fixture THẬT (nếu có): in bốn con số cho báo cáo; bất biến giữ', () {
    final d = loadRealDocOrSkip();
    if (d == null) return;
    final m = _metrics(d);
    expect(m['sourceTrust(trustedCorpus)'], 0,
        reason: 'chưa có đường sản xuất tin được ⇒ SOURCE TRUST = 0');
    expect(m['stepsWithValidator'], 0,
        reason: 'không validator đăng ký cho kịch bản ⇒ EVIDENCE REALITY = 0');
    expect((m['byTrust'] as Map)['fixtureSynthetic'], isNull,
        reason: 'fixture thật không chứa phần tử giả lập');
    // ignore: avoid_print
    print('ROUND3-METRICS real: $m');
  });
}
