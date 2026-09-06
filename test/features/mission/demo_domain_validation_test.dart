/// ⭐⭐ ROUND 4 · Lane B — DẤU KIỂM CHỨNG CỦA FIXTURE DEMO PHẢI DO VALIDATOR MINT.
///
/// Round 4 đặt luật đọc NGHIÊM NGẶT làm mặc định (A-runtime R4.2–R4.4): chỉ sự
/// kiện mang dấu validator ĐÃ ĐĂNG KÝ mới đẩy mastery / thành «Tự làm được».
/// Hai test Home đã bị `skip` vì domain demo không có dấu.
///
/// Cách «sửa» rẻ tiền là gõ tay `EvidenceValidation(validatorId:
/// 'fraction-check-v1', …)` vào fixture. Đó là BỊA NĂNG LỰC: không có bài nào
/// được chấm, chỉ có một chuỗi ký tự trông giống dấu. Tệp này chốt cách làm
/// thật:
///
///   ① domain demo là bài phân số THẬT + đáp án THẬT, chấm bằng chính
///     `fraction-check-v1` ⇒ dấu là kết quả của một lần chấm, không phải dữ liệu;
///   ② KHÔNG tệp nào dưới `lib/features/**` được tự dựng `EvidenceValidation(`
///     — dấu chỉ tới từ `DeterministicValidator.grade()/.validation`.
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/fraction_problem.dart';
import 'package:learning_coach/core/student/evidence_validation.dart';
import 'package:learning_coach/features/mission/mission_data.dart';

void main() {
  group('1. Domain demo đi qua ĐÚNG luật đọc nghiêm ngặt', () {
    test('⭐⭐ ca «chia hết» CÓ bằng chứng dưới BKT mặc định (đã siết)', () {
      final d = buildDemoDomain(now: DateTime(2026, 9, 1, 19));
      final divisible = d.mastery.cases['denominator-divisible']!;

      // Dưới `ValidatedOnlyBktPolicy` (mặc định round 4), sự kiện KHÔNG dấu là
      // noOp. Còn đếm được bằng chứng ⇒ dấu là thật và được duyệt.
      expect(divisible.evidenceCount, 3,
          reason: 'ba lần làm mẫu đều được fraction-check-v1 chấm và đếm');
      expect(divisible.independentCorrect, 3);
      expect(divisible.independentIncorrect, 0);
      expect(divisible.hasEvidence, isTrue);

      // Ca lớp 5 vẫn CHƯA gặp — golden scenario caseTransitionGap giữ nguyên.
      expect(d.mastery.cases['denominator-non-divisible']!.hasEvidence, isFalse);
    });

    test('⭐⭐ mỗi bài mẫu là bài phân số THẬT, ĐÚNG ca, và đáp án ĐÚNG theo '
        'số học — không có «đúng» nào được gán tay', () {
      // Cùng bộ bài mà fixture dùng. Nếu fixture đổi bài mà quên kiểm, số
      // `evidenceCount` ở test trên tụt ⇒ đổ. Ở đây chốt tính chất của bộ bài.
      const attempts = {
        '1/2 + 1/4': '6/8',
        '1/3 + 1/6': '9/18',
        '2/5 + 1/10': '25/50',
      };
      for (final e in attempts.entries) {
        final fp = FractionProblem.parse(e.key);
        expect(fp, isNotNull, reason: '${e.key} phải đọc được thành phân số');
        expect(fractionSumCase(e.key), 'denominator-divisible',
            reason: '${e.key} phải THẬT SỰ thuộc ca «một mẫu chia hết mẫu kia»');
        final graded = FractionCheckValidator(fp!).grade(e.value);
        expect(graded, isNotNull, reason: 'validator đã đăng ký ⇒ mint được');
        expect(graded!.correct, isTrue,
            reason: '${e.value} phải ĐÚNG theo số học, không phải theo khai báo');
        expect(graded.validation.validatorId, 'fraction-check-v1');
        expect(graded.validation.grantsCompetence, isTrue);
      }
    });
  });

  group('2. CẤU TRÚC — không tầng UI nào tự viết dấu', () {
    test('⭐⭐ không tệp nào dưới lib/features/** dựng `EvidenceValidation(`', () {
      final root = Directory('lib/features');
      expect(root.existsSync(), isTrue);
      final offenders = <String>[];
      for (final f in root
          .listSync(recursive: true)
          .whereType<File>()
          .where((f) => f.path.endsWith('.dart'))) {
        for (final line in f.readAsLinesSync()) {
          final code = line.trim();
          if (code.startsWith('//') || code.startsWith('///')) continue;
          if (code.contains('EvidenceValidation(')) {
            offenders.add('${f.path}: $code');
          }
        }
      }
      expect(offenders, isEmpty,
          reason: 'Dấu kiểm chứng chỉ được mint bởi DeterministicValidator '
              '(`.grade()` / `.validation`). Một `EvidenceValidation(...)` gõ '
              'tay trong features là dấu BỊA — SELF REPORT ≠ COMPETENCE.\n'
              '${offenders.join('\n')}');
    });
  });
}
