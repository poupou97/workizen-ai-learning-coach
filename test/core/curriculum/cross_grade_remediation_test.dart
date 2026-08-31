/// ⭐⭐ CHUỖI XUYÊN LỚP — dữ liệu đo từ corpus KNTT thật, không bịa.
///
/// Lớp 4 Bài 57 "Quy đồng mẫu số các phân số" (tr.62) — DẠY, ca chia hết
/// Lớp 5 Bài 3  "Ôn tập phân số"        (tr.11) — ÔN
/// Lớp 5 Bài 6  "Cộng, trừ ... khác mẫu số" (tr.20) — DÙNG, ca không chia hết
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/concept.dart';

void main() {
  const quyDong = Concept(
    id: 'quy-dong',
    canonicalName: 'Quy đồng mẫu số',
    textbookTerms: {
      4: {'quy đồng mẫu số', 'mẫu số chung'},
      5: {'quy đồng mẫu số', 'mẫu số chung'},
    },
    exposures: [
      ConceptExposure(
          grade: 4, bookSeries: 'kntt', lessonId: 'toan4-t2-bai57',
          role: ExposureRole.introduces, pageStart: 62),
      ConceptExposure(
          grade: 5, bookSeries: 'kntt', lessonId: 'toan5-t1-bai3',
          role: ExposureRole.reinforces, pageStart: 11),
      ConceptExposure(
          grade: 5, bookSeries: 'kntt', lessonId: 'toan5-t1-bai6',
          role: ExposureRole.applies, pageStart: 20),
    ],
  );

  // Khái niệm CHƯA có bài dạy nào trong corpus hiện tại.
  const bcnn = Concept(
      id: 'bcnn', canonicalName: 'Bội chung nhỏ nhất',
      exposures: [], textbookTerms: {});

  test('⭐⭐ khái niệm được DẠY ở lớp 4, chỉ ÔN và DÙNG ở lớp 5', () {
    expect(quyDong.introducedGrade, 4,
        reason: '⭐ Nội dung vá lỗ nằm ở LỚP 4. Học sinh lớp 5 hỏng quy đồng thì '
            'gửi em ấy về Toán 5 Bài 3 là gửi tới một trang ÔN TẬP — trang 12 '
            'là bài luyện tập, không giải thích gì.');
    expect(quyDong.reinforcedGrades, [5]);
    expect(quyDong.relevanceAt(4), ExposureRole.introduces);
    expect(quyDong.relevanceAt(5), ExposureRole.reinforces);
  });

  test('⭐ mastery gắn vào KHÁI NIỆM, không nhân đôi theo lớp', () {
    // Một id duy nhất phục vụ cả hai lớp.
    expect(quyDong.id, 'quy-dong');
    expect(quyDong.exposures.map((e) => e.grade).toSet(), {4, 5},
        reason: '⭐ Nếu tách thành `grade4-quy-dong` và `grade5-quy-dong` thì một '
            'đứa trẻ đã nắm chắc ở lớp 4 sẽ bị coi là chưa biết gì ở lớp 5 — và '
            'chẩn đoán xuyên lớp mất luôn ý nghĩa.');
  });

  test('⭐⭐ root gap CÓ nguồn dạy ⇒ REMEDIATE_AVAILABLE', () {
    expect(remediationFor(quyDong, diagnosticConfidence: 0.9),
        RemediationStatus.remediateAvailable);
  });

  test('⭐⭐ root gap KHÔNG có nguồn ⇒ KNOWLEDGE_MISSING, KHÔNG được bịa bài', () {
    expect(bcnn.hasTeachingSource, isFalse);
    expect(remediationFor(bcnn, diagnosticConfidence: 0.95),
        RemediationStatus.remediateKnowledgeMissing,
        reason: '⭐ Chẩn đoán chắc chắn 0.95 mà vẫn KHÔNG được dựng bài giảng '
            'gán cho sách. Confidence cao nói ta ĐÚNG về lỗ hổng — nó không cho '
            'ta nội dung để dạy. Trộn hai thứ là lúc AI bắt đầu bịa SGK.');
  });

  test('⭐ chẩn đoán yếu ⇒ CONFIDENCE_LOW, đứng trước cả câu hỏi có nguồn hay không',
      () {
    expect(remediationFor(quyDong, diagnosticConfidence: 0.4),
        RemediationStatus.diagnosticConfidenceLow,
        reason: 'có nguồn dạy không phải lý do để tin vào một chẩn đoán yếu');
    expect(remediationFor(null, diagnosticConfidence: 0.99),
        RemediationStatus.diagnosticConfidenceLow);
  });

  test('⭐ từ vựng của sách tra được theo LỚP', () {
    expect(quyDong.textbookTerms[4], contains('mẫu số chung'));
    expect(quyDong.canonicalName, isNot('quy đồng mẫu số'),
        reason: 'tên nội bộ tách khỏi từ sách dùng — hiển thị cho trẻ phải lấy '
            'từ textbookTerms theo đúng lớp em ấy đang học');
  });
}
