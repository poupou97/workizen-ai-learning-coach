/// ⭐ Mastery — đo theo **SkillCase**, mastery của Concept là giá trị **suy ra**.
///
/// Xem `docs/decisions/ADR-001-mastery-per-skillcase.md`.
///
/// Luật cập nhật là BKT chuẩn. Toàn bộ engine của OATutor (Berkeley CAHL) là 14 dòng —
/// ta không cần phụ thuộc nào, và **không thể** dùng pyBKT ở runtime: nó là Python,
/// còn Workizen chạy trên điện thoại. pyBKT vẫn hữu ích **ngoại tuyến** để khớp tham
/// số, khi nào có dữ liệu học sinh thật.
library;

/// Bốn tham số BKT. Đặt tay theo tiên nghiệm; khớp bằng dữ liệu sau.
class BktParams {
  const BktParams({
    required this.prior,
    required this.learn,
    required this.slip,
    required this.guess,
  });

  final double prior;
  final double learn;

  /// Biết mà vẫn sai.
  final double slip;

  /// Không biết mà đoán trúng.
  ///
  /// ⚠️ **Phải đặt theo DẠNG BÀI, không dùng một hằng số chung.** Trắc nghiệm bốn lựa
  /// chọn có `guess ≈ 0.25` **theo cấu trúc**; tự luận gần 0. Dùng chung một số là đọc
  /// sai bằng chứng một cách hệ thống. pyBKT gọi đây là `multigs` — không cần tự nghĩ.
  final double guess;

  static const freeResponse =
      BktParams(prior: 0.2, learn: 0.15, slip: 0.1, guess: 0.05);
  static const multipleChoice4 =
      BktParams(prior: 0.2, learn: 0.15, slip: 0.1, guess: 0.25);
}

/// Luật cập nhật BKT — hậu nghiệm Bayes rồi cộng xác suất học được.
double bktUpdate(double pMastery, bool correct, BktParams p) {
  final num = correct ? pMastery * (1 - p.slip) : pMastery * p.slip;
  final other = correct
      ? (1 - pMastery) * p.guess
      : (1 - pMastery) * (1 - p.guess);
  final posterior = num / (num + other);
  return posterior + (1 - posterior) * p.learn;
}

class CaseMastery {
  const CaseMastery({
    required this.skillCaseId,
    required this.pMastery,
    required this.evidenceCount,
  });

  final String skillCaseId;
  final double pMastery;
  final int evidenceCount;

  /// ⭐ Chưa gặp **KHÁC** làm sai. Một ca chưa có bằng chứng phải là *chưa biết*, không
  /// phải *bằng 0* — nếu không, mọi học sinh mới đều trông như đang hỏng mọi thứ.
  bool get hasEvidence => evidenceCount > 0;

  CaseMastery observe(bool correct, BktParams p) => CaseMastery(
        skillCaseId: skillCaseId,
        pMastery: bktUpdate(pMastery, correct, p),
        evidenceCount: evidenceCount + 1,
      );

  static CaseMastery initial(String id, BktParams p) =>
      CaseMastery(skillCaseId: id, pMastery: p.prior, evidenceCount: 0);
}

enum MasteryState { unknown, learning, needsPractice, mastered }

class ConceptMastery {
  const ConceptMastery({required this.conceptId, required this.cases});

  final String conceptId;
  final Map<String, CaseMastery> cases;

  /// ⭐ Suy ra bằng **min** các ca CÓ bằng chứng. `null` = chưa biết gì.
  ///
  /// Vì sao `min` chứ không phải `mean`: `mean` giấu một ca hỏng sau một ca vững — đúng
  /// thứ ta đang cố phát hiện. *"Em ấy vững nhất ở mức của ca yếu nhất"* là phát biểu
  /// an toàn cho một đứa trẻ.
  /// ⚠️ Đây là **giả thuyết**, chưa có dữ liệu thực nghiệm chọn nó. Xem ADR-001.
  double? get derived {
    final seen = cases.values.where((c) => c.hasEvidence).map((c) => c.pMastery);
    return seen.isEmpty ? null : seen.reduce((a, b) => a < b ? a : b);
  }

  MasteryState stateAt({double masteredAt = 0.85, double practiceBelow = 0.6}) {
    final d = derived;
    if (d == null) return MasteryState.unknown;
    if (d >= masteredAt) return MasteryState.mastered;
    return d < practiceBelow ? MasteryState.needsPractice : MasteryState.learning;
  }

  /// ⭐⭐ Ca nào vững, ca nào chưa — thứ mà mastery mức Concept **không thể** nói.
  ///
  /// Đây là bằng chứng để kết luận `caseTransitionGap`: có ít nhất một ca vững VÀ ít
  /// nhất một ca yếu/chưa gặp. Không có nó thì `caseTransitionGap` chỉ là một cái tên.
  ({List<String> strong, List<String> weak, List<String> unseen}) caseBreakdown({
    double strongAt = 0.85,
  }) {
    final strong = <String>[], weak = <String>[], unseen = <String>[];
    for (final c in cases.values) {
      if (!c.hasEvidence) {
        unseen.add(c.skillCaseId);
      } else if (c.pMastery >= strongAt) {
        strong.add(c.skillCaseId);
      } else {
        weak.add(c.skillCaseId);
      }
    }
    return (strong: strong, weak: weak, unseen: unseen);
  }
}
