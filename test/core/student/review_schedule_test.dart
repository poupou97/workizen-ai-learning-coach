/// ⭐ F5 — lịch ôn tách khỏi ước lượng tri thức (Founder: không sập sớm).
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/core/student/review_schedule.dart';

void main() {
  const p = BktParams.freeResponse;
  final t0 = DateTime(2026, 9, 1);

  CaseMastery drill(int n, {DateTime? at}) {
    var c = CaseMastery.initial('ca', p);
    for (var i = 0; i < n; i++) {
      c = c.observeWithSupport(true, p, at: at ?? t0);
    }
    return c;
  }

  test('⭐⭐ BẤT BIẾN TÁCH: thời gian trôi KHÔNG đổi pMastery, chỉ đổi lịch ôn',
      () {
    final c = drill(3);
    final soon = reviewStateOf(c, t0.add(const Duration(days: 1)));
    final later = reviewStateOf(c, t0.add(const Duration(days: 400)));
    expect(soon.urgency, ReviewUrgency.fresh);
    expect(later.urgency, ReviewUrgency.overdue);
    expect(c.pMastery, drill(3).pMastery,
        reason: '⭐⭐ ước lượng tri thức và lịch ôn là HAI câu hỏi — Founder '
            'cấm sập vào nhau khi chưa có dữ liệu chọn mô hình quên');
  });

  test('⭐ khoảng ôn GIÃN NỞ theo bằng chứng — hình dạng SM-2/FSRS', () {
    final one = reviewStateOf(drill(1), t0).nextReviewAt!;
    final three = reviewStateOf(drill(3), t0).nextReviewAt!;
    expect(three.isAfter(one),
        isTrue, reason: 'nhiều bằng chứng hơn ⇒ nhớ lâu hơn ⇒ ôn thưa hơn');
    expect(one, t0.add(const Duration(days: 7)),
        reason: 'một bằng chứng ⇒ khoảng nền 7 ngày (nhịp tuần học)');
  });

  test('⭐ khoảng ôn có TRẦN — không khoảng nào vượt một học kỳ', () {
    final many = reviewStateOf(drill(50), t0).nextReviewAt!;
    expect(many.difference(t0).inDays, lessThanOrEqualTo(112),
        reason: '7×2⁴ = 112 ngày: không ca nào "vững vĩnh viễn" đến mức '
            'không bao giờ gặp lại');
  });

  test('chưa có bằng chứng ⇒ KHÔNG CÓ GÌ ĐỂ ÔN — khác với "tới hạn ôn"', () {
    final s = reviewStateOf(CaseMastery.initial('ca', p), t0);
    expect(s.urgency, ReviewUrgency.nothingToReview);
    expect(s.nextReviewAt, isNull,
        reason: 'gửi bài "ôn" cho thứ chưa từng học là chẩn sai can thiệp — '
            'ca này cần HỌC/ĐO, không phải review');
  });

  test('tới hạn rồi quá hạn — ba mức theo thời gian, tất định', () {
    final c = drill(1); // due = t0 + 7d, overdue = t0 + 14d
    expect(reviewStateOf(c, t0.add(const Duration(days: 6))).urgency,
        ReviewUrgency.fresh);
    expect(reviewStateOf(c, t0.add(const Duration(days: 8))).urgency,
        ReviewUrgency.reviewDue);
    expect(reviewStateOf(c, t0.add(const Duration(days: 15))).urgency,
        ReviewUrgency.overdue);
  });
}
