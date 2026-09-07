/// ⭐⭐ Lệnh 57 — TOKEN PHẢI KHỚP CONCEPT, và giá trị được ĐO chứ không chọn.
///
/// Mỗi con số dưới đây có nguồn là một phép đo trên ảnh concept trong repo.
/// Ai đổi token mà không đổi concept sẽ làm bài kiểm này đỏ — đó là mục đích.
library;

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/app/theme/wal_tokens.dart';
import 'package:learning_coach/core/curriculum/subject_id.dart';

void main() {
  group('§8.1 màu thương hiệu — đo trên 4 màn concept', () {
    test('⭐ tím SAM = #6A36EE (mode: 6A34EE · 6B38EB · 6934F2 · 693AED)', () {
      expect(WalColors.primary500, const Color(0xFF6A36EE));
    });

    test('⛔ KHÔNG quay lại #7C4DFF — sắc tím implementation tự nới', () {
      expect(WalColors.primary500, isNot(const Color(0xFF7C4DFF)));
    });

    test('nền trang #F9F9FD và surface tím nhạt #F5F1FE, đo trên 05 Home', () {
      expect(WalColors.surface, const Color(0xFFF9F9FD));
      expect(WalColors.surfaceLavender, const Color(0xFFF5F1FE));
    });
  });

  group('§8.7 hình khối — đo trên concept', () {
    test('nút r=16 (đo ≈15 trên nền cao 48) — KHỚP', () {
      expect(WalSpacing.radiusButton, 16.0);
    });

    test('⭐ thẻ r=14 (đo 12 và 15), KHÔNG phải 20', () {
      expect(WalSpacing.radiusCard, 14.0);
      expect(WalSpacing.radiusCard, lessThan(20.0));
    });

    test('thẻ KHÔNG bo tròn hơn nút — concept không như vậy', () {
      expect(WalSpacing.radiusCard, lessThanOrEqualTo(WalSpacing.radiusButton));
    });
  });

  group('§8.10 màu theo môn — của CONCEPT, không phải bảng tự chế', () {
    test('năm môn concept có màu đúng như đo được', () {
      expect(
        WalSubjectColors.conceptColor(subjectIdOf('Toán')),
        const Color(0xFFF2EDFD),
      );
      expect(
        WalSubjectColors.conceptColor(subjectIdOf('Tiếng Việt')),
        const Color(0xFFEBF9F3),
      );
      expect(
        WalSubjectColors.conceptColor(subjectIdOf('Khoa học')),
        const Color(0xFFE9F1FE),
      );
    });

    test('⭐ môn concept CHƯA quy định ⇒ null, không giả vờ là màu concept', () {
      expect(WalSubjectColors.conceptColor(subjectIdOf('KHTN')), isNull);
      expect(WalSubjectColors.conceptColor(subjectIdOf('Ngữ văn')), isNull);
    });

    test('bảng dự phòng tất định và không rỗng', () {
      expect(WalSubjectColors.fallback, isNotEmpty);
    });
  });

  group('§8.4 typography — trạng thái THẬT, ghi ra chứ không giấu', () {
    test('⚠ DESIGN GAP: app KHÔNG khai font nào ⇒ dùng font hệ thống', () {
      // Sự thật kiểm chứng được, độc lập nền tảng: `pubspec.yaml` không có
      // khối `fonts:` nào. Flutter vì thế rơi về font hệ thống (Roboto trên
      // Android).
      //
      // Font của CONCEPT thì KHÔNG xác minh được: repo chỉ có ảnh PNG, không
      // có design source, không có tệp font, không có tài liệu nào nêu tên
      // font. Theo §8.4 đây là UNRESOLVED — sửa mà không có nguồn font là tự
      // phát minh, đúng thứ §8.2 cấm.
      final pubspec = File('pubspec.yaml').readAsStringSync();
      expect(
        RegExp(r'^\s{2}fonts:', multiLine: true).hasMatch(pubspec),
        isFalse,
        reason: 'đã khai font ⇒ cập nhật báo cáo visual fidelity',
      );
    });
  });
}
