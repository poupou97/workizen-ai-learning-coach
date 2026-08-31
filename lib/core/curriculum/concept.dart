/// ⭐ Khái niệm — **lớp không phải ranh giới cứng**.
///
/// Đo từ corpus thật (KNTT), khái niệm `quy đồng mẫu số`:
///
/// | Lớp | Bài | Điều kiện | Mẫu số chung |
/// |---|---|---|---|
/// | 4 | Bài 57, tr.62 | mẫu này **chia hết** cho mẫu kia | lấy mẫu lớn, giữ nguyên một phân số |
/// | 5 | Bài 6, tr.20 | **không chia hết** | lấy **tích** hai mẫu |
///
/// Một khái niệm, hai ca bổ sung nhau, **chia đôi qua hai lớp**. Lớp 5 còn mở
/// đầu bằng *"Hai mẫu số 5 và 2 không chia hết cho nhau"* — sách tự tham chiếu
/// ca đã dạy ở lớp 4.
///
/// ⇒ Hệ quả cho Student Model: mastery gắn vào **`quy-dong`**, KHÔNG phải
/// `grade4-quy-dong` và `grade5-quy-dong` như hai thứ khác nhau. Nhân đôi khái
/// niệm theo lớp là mất chính điều làm cho chẩn đoán xuyên lớp hoạt động — và
/// khiến một đứa trẻ đã nắm chắc ở lớp 4 bị coi là chưa biết gì ở lớp 5.
library;

class ConceptExposure {
  const ConceptExposure({
    required this.grade,
    required this.bookSeries,
    required this.lessonId,
    required this.role,
    this.pageStart,
  });

  final int grade;
  final String bookSeries;
  final String lessonId;
  final ExposureRole role;
  final int? pageStart;
}

/// Bài này **dạy** khái niệm, hay chỉ **ôn**, hay chỉ **dùng**?
///
/// Khác biệt quyết định nội dung vá lỗ nằm ở đâu. Toán 5 Bài 3 tên là
/// *"Ôn tập phân số"* và trang 12 là bài luyện tập — không dạy gì. Nếu hệ thống
/// tưởng đó là nơi dạy, nó sẽ gửi học sinh tới một trang không giải thích gì.
enum ExposureRole { introduces, reinforces, applies }

class Concept {
  const Concept({
    required this.id,
    required this.canonicalName,
    required this.exposures,
    required this.textbookTerms,
  });

  final String id;

  /// Tên của ta, dùng nội bộ. **Không** hiển thị cho trẻ.
  final String canonicalName;

  final List<ConceptExposure> exposures;

  /// ⭐ Từ SÁCH dùng, theo lớp. Đo được: Toán 5 KNTT không dùng cụm
  /// "phân số bằng nhau" (0 lần) — nó nói "rút gọn" / "phân số tối giản".
  final Map<int, Set<String>> textbookTerms;

  /// Lớp **dạy lần đầu**. `null` = chưa có bài nào trong corpus dạy nó ⇒ nếu
  /// đây là root gap thì ta **không có nội dung để vá**.
  int? get introducedGrade {
    final g = exposures
        .where((e) => e.role == ExposureRole.introduces)
        .map((e) => e.grade);
    return g.isEmpty ? null : g.reduce((a, b) => a < b ? a : b);
  }

  List<int> get reinforcedGrades => [
        for (final e in exposures)
          if (e.role == ExposureRole.reinforces) e.grade
      ];

  /// Ở lớp này, khái niệm đóng vai trò gì.
  ExposureRole? relevanceAt(int grade) {
    for (final r in ExposureRole.values) {
      if (exposures.any((e) => e.grade == grade && e.role == r)) return r;
    }
    return null;
  }

  /// ⭐ Có nội dung nguồn để **dạy** khái niệm này không.
  bool get hasTeachingSource => introducedGrade != null;
}

/// Engine phải phân biệt ba ca — §REMEDIATION STATUS.
enum RemediationStatus {
  /// Tìm ra lỗ hổng VÀ có nguồn để dạy.
  remediateAvailable,

  /// Tìm ra lỗ hổng nhưng **corpus chưa có bài dạy**. Tuyệt đối không bịa một
  /// bài giảng rồi gán cho sách. Nói thật: *"phần này thuộc chương trình lớp N"*.
  remediateKnowledgeMissing,

  /// Chưa đủ bằng chứng để chỉ ra lỗ hổng. Nói "chưa chắc" thay vì đoán bừa.
  diagnosticConfidenceLow,
}

RemediationStatus remediationFor(
  Concept? rootGap, {
  required double diagnosticConfidence,
  double confidenceFloor = 0.6,
}) {
  if (rootGap == null || diagnosticConfidence < confidenceFloor) {
    return RemediationStatus.diagnosticConfidenceLow;
  }
  return rootGap.hasTeachingSource
      ? RemediationStatus.remediateAvailable
      : RemediationStatus.remediateKnowledgeMissing;
}
