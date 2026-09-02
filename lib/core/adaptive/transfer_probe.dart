/// WAL-103 — TransferProbe: không tuyên mastery từ cùng-khuôn (§H P0-3).
///
/// Doctrine: chuỗi đúng trên bài CÙNG KHUÔN là bằng chứng thuộc khuôn, chưa
/// phải hiểu kỹ năng. Probe = chọn bài CÙNG CA, KHÁC BỀ MẶT. Fail closed:
/// không có bài khác-bề-mặt ⇒ `null` — claim giữ nguyên kèm sự thật «chưa
/// thử bề mặt khác», tuyệt đối không đoán.
///
/// Xem docs/research/TRANSFER-PROBE.md — taxonomy đo từ corpus, luật kích
/// hoạt hà tiện (transfer-probe là gate của CLAIM, không phải bài luyện
/// thường), và giới hạn ghi thật (surface tag do người soạn pool khai).
library;

import '../student/mastery.dart';

/// Bề mặt bài — đo được từ corpus (extract_units + rebuild_fractions).
enum SurfaceFamily { bareExpression, comparison, visualModel, wordProblem }

/// Khoảng cách transfer giữa hai family — bảng CỐ ĐỊNH, kiểm toán được.
/// wordProblem xa nhất (retrieval-practice âm tính với word-problem —
/// evidence map §Agarwal-2019 — nên far không bao giờ là bước BẮT BUỘC).
int transferDistance(SurfaceFamily from, SurfaceFamily to) {
  if (from == to) return 0; // cùng family — near transfer là khác template
  if (to == SurfaceFamily.wordProblem || from == SurfaceFamily.wordProblem) {
    return 2;
  }
  return 1;
}

/// Bài ứng viên trong pool — surface/template do NGƯỜI SOẠN POOL khai
/// (POC không tự đoán từ text bài — giới hạn ghi thật §6).
class TransferCandidate {
  const TransferCandidate({
    required this.exerciseId,
    required this.skillCaseId,
    required this.surface,
    required this.templateId,
    this.singleSkill = true,
  });

  final String exerciseId;
  final String skillCaseId;
  final SurfaceFamily surface;

  /// Khuôn bài — v1 là skeleton chuẩn hoá của expression.
  final String templateId;

  /// Bài chỉ chạm MỘT ca (luật ② của nextProbe) — ưu tiên để bằng chứng
  /// transfer không nhiễm ca khác.
  final bool singleSkill;
}

class TransferProbeRequest {
  const TransferProbeRequest({
    required this.exerciseId,
    required this.skillCaseId,
    required this.surface,
    required this.distance,
    required this.reason,
  });

  final String exerciseId;
  final String skillCaseId;
  final SurfaceFamily surface;

  /// 0 = near (cùng family khác khuôn); 1-2 = far dần.
  final int distance;

  final String reason;
}

/// Luật kích hoạt — CẢ BA phải đúng (hà tiện, không biến mọi bài thành thi):
/// ① ca sắp chạm claim mạnh; ② bằng chứng độc lập gần đây MỘT MÀU (một
/// khuôn); ③ (kiểm ở [nextTransferProbe]) có bài khác-bề-mặt để hỏi.
bool shouldTransferProbe({
  required CaseMastery mastery,
  required Set<String> recentIndependentTemplates,
  double strongAt = 0.85,
}) {
  if (!mastery.hasEvidence || mastery.pMastery < strongAt) return false; // ①
  return recentIndependentTemplates.length <= 1; // ② một màu ⇒ cần probe
}

/// Chọn probe — tất định, kiểu nextProbe:
/// cùng ca + CHƯA GẶP (khác template với mọi khuôn đã làm) → khoảng cách
/// gần trước → đơn-kỹ-năng trước → id từ điển. Không ứng viên ⇒ `null`.
TransferProbeRequest? nextTransferProbe({
  required String skillCaseId,
  required SurfaceFamily dominantSurface,
  required Set<String> seenTemplates,
  required List<TransferCandidate> pool,
}) {
  final candidates = [
    for (final c in pool)
      if (c.skillCaseId == skillCaseId && !seenTemplates.contains(c.templateId))
        c
  ];
  if (candidates.isEmpty) return null; // ③ fail closed — không đoán

  candidates.sort((a, b) {
    final da = transferDistance(dominantSurface, a.surface);
    final db = transferDistance(dominantSurface, b.surface);
    if (da != db) return da.compareTo(db); // near trước
    if (a.singleSkill != b.singleSkill) return a.singleSkill ? -1 : 1;
    return a.exerciseId.compareTo(b.exerciseId);
  });
  final pick = candidates.first;
  final d = transferDistance(dominantSurface, pick.surface);

  return TransferProbeRequest(
    exerciseId: pick.exerciseId,
    skillCaseId: skillCaseId,
    surface: pick.surface,
    distance: d,
    reason: d == 0
        ? 'Con làm tốt dạng quen rồi — thử một bài CÙNG dạng nhưng khuôn khác '
            'xem sao nhé.'
        : 'Con làm tốt dạng quen rồi — thử cùng kỹ năng đó ở kiểu bài khác '
            'để chắc là con hiểu, không chỉ thuộc.',
  );
}
