import 'dart:convert';
import 'dart:io';

import 'package:flutter/services.dart' show rootBundle;
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/semantic_binding.dart';
import 'package:learning_coach/core/curriculum/source_grounded_binding.dart';

/// ⭐ RUNTIME_GUIDED_READY 0 → >0 bằng NGUỒN, không bằng bịa.
///
/// Không kiểm cờ trong dữ liệu — kiểm chính `resolveBinding` có trả ra
/// phương pháp ĐƯỢC PHÉP hay không. Cờ là lời khai; `resolveBinding` là toà.
void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  final have =
      File('assets/fixtures/real/lesson-11-sgk-hoa-hoc-11-b13.json').existsSync();
  const why = 'assets/fixtures/real/ chưa sinh trên máy này (gitignore)';

  Future<Map<String, Object?>> raw(String b, int l) async =>
      (jsonDecode(await rootBundle
              .loadString('assets/fixtures/real/lesson-$b-b$l.json')) as Map)
          .cast<String, Object?>();

  ResolvedBinding resolveFrom(Map<String, Object?> j) {
    final c = SourceCurriculum.fromJson(j['curriculum'])!;
    final r = bindingFor(c,
        book: j['book'] as String,
        lessonNo: (j['lesson'] as num).toInt(),
        grade: (j['grade'] as num).toInt(),
        bookSeries: 'kntt',
        activityId: SemanticBinding.tutorScriptActivity);
    return resolveBinding(r.binding, r.curriculum);
  }

  test('⭐ bài NGOÀI Bài 17 giải được binding — có phương pháp được phép',
      () async {
    if (!have) return markTestSkipped(why);
    final j = await raw('11-sgk-hoa-hoc-11', 13);
    final rb = resolveFrom(j);
    expect(rb.refusals, isEmpty, reason: 'bị từ chối: ${rb.refusals}');
    expect(rb.scope, isNotNull);
    expect(rb.allowedMethods, isNotEmpty,
        reason: 'không phương pháp nào được phép ⇒ TutorScope rỗng');
    expect(rb.allowedMethods.first.provenance!.citableAsTextbookFact, isTrue,
        reason: 'phương pháp phải trích được về TRANG của sách');
  });

  test('⭐ điều kiện của ca là CÂU NGUYÊN VĂN trong bài, không diễn đạt lại',
      () async {
    if (!have) return markTestSkipped(why);
    final j = await raw('11-sgk-hoa-hoc-11', 13);
    final c = SourceCurriculum.fromJson(j['curriculum'])!;
    final blocks = (j['blocks'] as List).cast<Map>();
    final src = blocks.firstWhere((b) => b['id'] == c.ruleBlockId);
    expect((src['text'] as String).contains(c.condition), isTrue,
        reason: 'câu quy tắc không có nguyên văn trong khối nguồn ⇒ đã bịa');
  });

  test('⭐ thiếu trang ⇒ KHÔNG trích được như lời sách ⇒ từ chối', () async {
    if (!have) return markTestSkipped(why);
    final j = await raw('11-sgk-hoa-hoc-11', 13);
    final m = (j['curriculum'] as Map).cast<String, Object?>()
      ..remove('pagePdf');
    expect(SourceCurriculum.fromJson(m), isNull);
  });

  test('⭐ origin khác sourceStated ⇒ từ chối, không có đường nâng hạng',
      () async {
    if (!have) return markTestSkipped(why);
    final j = await raw('11-sgk-hoa-hoc-11', 13);
    final m = (j['curriculum'] as Map).cast<String, Object?>()
      ..['origin'] = 'sourceDemonstrated';
    expect(SourceCurriculum.fromJson(m), isNull);
  });

  test('⭐ TutorScope của bài A KHÔNG dùng được cho bài B', () async {
    if (!have) return markTestSkipped(why);
    final a = await raw('11-sgk-hoa-hoc-11', 13);
    final b = await raw('11-sgk-sinh-hoc-11', 2);
    final ca = SourceCurriculum.fromJson(a['curriculum'])!;
    final cb = SourceCurriculum.fromJson(b['curriculum'])!;
    final ra = bindingFor(ca,
        book: a['book'] as String,
        lessonNo: 13,
        grade: 11,
        bookSeries: 'kntt',
        activityId: SemanticBinding.tutorScriptActivity);
    final rb = bindingFor(cb,
        book: b['book'] as String,
        lessonNo: 2,
        grade: 11,
        bookSeries: 'kntt',
        activityId: SemanticBinding.tutorScriptActivity);
    // Binding của bài A + curriculum của bài B ⇒ phải TỪ CHỐI.
    final crossed = resolveBinding(ra.binding, rb.curriculum);
    expect(crossed.allowedMethods, isEmpty,
        reason: 'ngữ nghĩa bài này không được dùng cho bài khác');
  });

  test('⭐ bài KHÔNG có khối quy tắc in ⇒ không có curriculum', () async {
    if (!have) return markTestSkipped(why);
    final j = await raw('10-sgk-lich-su-10', 9);
    expect(j['curriculum'], isNull,
        reason: 'bài này không in khối quy tắc — không được dựng binding');
    final cap = ((j['provenance'] as Map)['capability'] as Map)
        .cast<String, Object?>();
    expect(cap['runtimeGuidedReady'], false);
  });

  const all = [
    ['11-sgk-sinh-hoc-11', 2],
    ['06-sgk-khoa-hoc-tu-nhien-6', 9],
    ['11-sgk-hoa-hoc-11', 13],
    ['09-sgk-cong-nghe-9-trai-nghiem-nghe-nghiep-mo-dun-trong-cay-an-qua', 1],
    ['10-sgk-dia-li-10', 5],
    ['12-sgk-chuyen-de-hoc-tap-cong-nghe-12-lam-nghiep-thuy-san', 5],
    ['10-sgk-lich-su-10', 9],
    ['07-sgk-tin-hoc-7', 13],
    ['11-sgk-sinh-hoc-11', 6],
    ['06-sgk-khoa-hoc-tu-nhien-6', 10],
    ['06-sgk-khoa-hoc-tu-nhien-6', 18],
    ['06-sgk-khoa-hoc-tu-nhien-6', 25],
    ['09-sgk-khoa-hoc-tu-nhien-9', 18],
    ['09-sgk-khoa-hoc-tu-nhien-9', 3],
    ['09-sgk-khoa-hoc-tu-nhien-9', 44],
    ['10-sgk-dia-li-10', 19],
    ['11-sgk-sinh-hoc-11', 10],
    ['11-sgk-sinh-hoc-11', 12],
    ['11-sgk-sinh-hoc-11', 13],
    ['11-sgk-sinh-hoc-11', 15],
    ['11-sgk-sinh-hoc-11', 19],
    ['11-sgk-sinh-hoc-11', 20],
    ['11-sgk-sinh-hoc-11', 27],
    ['11-sgk-sinh-hoc-11', 9],
    ['12-sgk-cong-nghe-12-lam-nghiep-thuy-san', 1],
    ['12-sgk-cong-nghe-12-lam-nghiep-thuy-san', 27],
    ['12-sgk-cong-nghe-12-lam-nghiep-thuy-san', 3],
    ['12-sgk-cong-nghe-12-lam-nghiep-thuy-san', 7],
    ['12-sgk-hoa-hoc-12', 15],
    ['12-sgk-hoa-hoc-12', 18],
    ['12-sgk-hoa-hoc-12', 21],
    ['12-sgk-hoa-hoc-12', 24],
    ['12-sgk-hoa-hoc-12', 9],
  ];

  test('⭐ MỌI bài có curriculum đều GIẢI ĐƯỢC — không bài nào khai suông',
      () async {
    if (!have) return markTestSkipped(why);
    var withCur = 0, resolved = 0;
    for (final p in all) {
      final j = await raw(p[0] as String, p[1] as int);
      final cap = ((j['provenance'] as Map)['capability'] as Map)
          .cast<String, Object?>();
      final c = SourceCurriculum.fromJson(j['curriculum']);
      // Cờ trong dữ liệu phải KHỚP với việc có ngữ nghĩa hay không.
      expect(cap['runtimeGuidedReady'], c != null,
          reason: '${p[0]} B${p[1]}: cờ không khớp dữ liệu');
      if (c == null) continue;
      withCur++;
      final rb = resolveFrom(j);
      expect(rb.allowedMethods, isNotEmpty,
          reason: '${p[0]} B${p[1]}: khai runtimeGuidedReady nhưng '
              'resolveBinding từ chối: ${rb.refusals}');
      resolved++;
    }
    expect(withCur, 18, reason: 'quần thể có quy tắc in phải là 18');
    expect(resolved, withCur, reason: 'khai bao nhiêu phải giải được bấy nhiêu');
  });
}
