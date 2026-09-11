import 'dart:convert';
import 'dart:io';

import 'package:flutter/services.dart' show rootBundle;
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/features/lesson_workspace/tutor_view.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/runtime_plan.dart';

/// ⭐ ĐƯỜNG SẢN PHẨM, không phải unit test của `resolveBinding`.
///
/// `planForDoc` là đúng hàm màn «Học với SAM» gọi. Nếu ngữ nghĩa suy từ nguồn
/// có thật thì ở ĐÂY `plan.isBound` phải thành `true`, và dòng chữ trẻ đọc
/// phải thôi nói «chưa ràng buộc».
void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  final have =
      File('assets/fixtures/real/lesson-11-sgk-hoa-hoc-11-b13.json').existsSync();
  const why = 'assets/fixtures/real/ chưa sinh trên máy này (gitignore)';

  Future<LessonDocument> doc(String b, int l) async => LessonDocument.fromJson(
      (jsonDecode(await rootBundle
              .loadString('assets/fixtures/real/lesson-$b-b$l.json')) as Map)
          .cast<String, Object?>())!;

  test('⭐ bài CÓ quy tắc in ⇒ plan ĐÃ RÀNG BUỘC trên đường sản phẩm', () async {
    if (!have) return markTestSkipped(why);
    final d = await doc('11-sgk-hoa-hoc-11', 13);
    expect(d.curriculum, isNotNull, reason: 'tài liệu thiếu khối curriculum');
    final plan = planForDoc(d);
    expect(plan, isNotNull);
    expect(plan!.isBound, isTrue,
        reason: 'vẫn chưa ràng buộc: ${plan.planRefusals}');
  });

  test('⭐ chữ trẻ đọc PHẢI đổi theo runtime, không hard-code', () async {
    if (!have) return markTestSkipped(why);
    final bound = planForDoc(await doc('11-sgk-hoa-hoc-11', 13));
    final unbound = planForDoc(await doc('10-sgk-lich-su-10', 9));
    expect(TutorView.runtimeLineShort(bound), isNot(contains('chưa ràng buộc')),
        reason: 'bài đã ràng buộc mà client vẫn nói chưa — chữ cũ còn sót');
    expect(TutorView.runtimeLineShort(unbound), contains('chưa ràng buộc'),
        reason: 'bài CHƯA ràng buộc mà client im lặng — mất cảnh báo đúng');
  });

  test('⭐ bài KHÔNG có quy tắc in ⇒ KHÔNG ràng buộc, fail closed', () async {
    if (!have) return markTestSkipped(why);
    final d = await doc('10-sgk-lich-su-10', 9);
    expect(d.curriculum, isNull);
    expect(planForDoc(d)!.isBound, isFalse);
  });
}
