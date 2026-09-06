/// ⭐⭐ F3 — Trọng số bằng chứng: **suy ra từ mô hình, không đặt hằng số tuỳ tiện**.
///
/// Founder decision (2026-09-01): *"Investigate evidence weighting rather than
/// hard-code arbitrary scientific constants without justification."*
///
/// Kết quả điều tra — khung **tỷ số hợp lý** (likelihood ratio), lấy thẳng từ
/// chính BKT chứ không thêm gì:
///
///   Mọi quan sát chỉ có giá trị chẩn đoán ở mức nó PHÂN BIỆT được người-biết
///   với người-chưa-biết:  P(quan sát | biết)  vs  P(quan sát | chưa biết).
///
/// Từ đó **mọi "trọng số" trong tệp này rơi ra từ toán, không phải đặt tay**:
///
/// - Lời giải đã hiện trên màn hình ⇒ ai cũng chép đúng được
///   ⇒ P(đúng|biết) = P(đúng|chưa biết) ⇒ tỷ số = 1 ⇒ **hậu nghiệm = tiên
///   nghiệm**. Không cần hằng số "chiết khấu 30%" nào — con số đó sẽ là bịa.
/// - Gợi ý mức nhẹ: ta KHÔNG đo được gợi ý tiết lộ bao nhiêu ⇒ khai báo
///   **không định lượng được** và xử như tỷ số 1 (fail closed về bằng chứng),
///   nhưng số hạng `learn` vẫn áp — có dạy + có tự thử thì có cơ hội học.
/// - `fullSolution`/chép mẫu: `learn` KHÔNG áp. `learn` trong BKT là xác suất
///   chuyển trạng thái **trên một cơ hội luyện tập có tự thử** (định nghĩa
///   chuẩn của "opportunity" trong văn liệu BKT). Chép lại không phải tự thử.
///   Cho `learn` ở đây là mở lại đúng vòng lặp tự xác nhận F3 bằng cửa sau.
/// - Trắc nghiệm 4 lựa chọn: `guess ≥ 0.25` **theo cấu trúc đề** — hằng số này
///   có justification hình thức, không phải tinh chỉnh.
///
/// Luật thay được: mọi suy diễn đi qua [EvidenceWeightingPolicy]; log thô giữ
/// nguyên ([EvidenceLog]) nên đổi policy ⇒ `replayMastery` lại từ đầu, không
/// mất gì và không cần migration.
library;

import 'learning_evidence.dart';
import 'mastery.dart';

/// P(quan sát thấy câu trả lời này | trạng thái tri thức).
///
/// Đây KHÔNG phải một "trọng số chỉnh tay" — nó là cặp likelihood của BKT, và
/// là **chỗ duy nhất** được phép mã hoá "bằng chứng này đáng tin tới đâu".
class ObservationLikelihood {
  const ObservationLikelihood({
    required this.pCorrectGivenKnown,
    required this.pCorrectGivenUnknown,
  })  : assert(pCorrectGivenKnown >= 0 && pCorrectGivenKnown <= 1),
        assert(pCorrectGivenUnknown >= 0 && pCorrectGivenUnknown <= 1);

  final double pCorrectGivenKnown;
  final double pCorrectGivenUnknown;

  /// Tỷ số = 1 ⇒ quan sát không nói gì ⇒ hậu nghiệm = tiên nghiệm. **Suy ra
  /// từ Bayes**, không phải một nhánh if đặc biệt.
  bool get isInformative => pCorrectGivenKnown != pCorrectGivenUnknown;
}

/// Một sự kiện được diễn giải thành gì. Kết quả của policy — tách khỏi sự kiện
/// thô để log không bao giờ chứa diễn giải.
class EvidenceUpdate {
  const EvidenceUpdate({
    required this.likelihood,
    required this.appliesLearning,
    required this.countsAsIndependent,
  });

  /// `null` = sự kiện không phải câu trả lời chấm được ⇒ belief đứng yên.
  final ObservationLikelihood? likelihood;

  /// Số hạng chuyển trạng thái `learn` có áp không (= có một *cơ hội luyện
  /// tập có tự thử* theo nghĩa BKT không).
  final bool appliesLearning;

  /// Có vào `evidenceCount` — tức có được dùng cho **claim với phụ huynh**.
  final bool countsAsIndependent;

  static const noOp = EvidenceUpdate(
      likelihood: null, appliesLearning: false, countsAsIndependent: false);
}

/// ⭐ Luật diễn giải bằng chứng — **thay thế được**. `policyId` đi kèm mọi giá
/// trị suy ra để biết mastery này được tính bằng luật nào (truy vết được).
abstract class EvidenceWeightingPolicy {
  String get policyId;
  EvidenceUpdate interpret(LearningEvent e, BktParams p);
}

/// Luật V1 — bảo thủ, mọi lựa chọn ghi rõ lý do ở doc đầu tệp.
///
/// ⚠️ Là GIẢ THUYẾT có lý do, chưa phải kết quả thực nghiệm. Khi có dữ liệu học
/// sinh thật: khớp lại bằng pyBKT (offline), giữ nguyên log, thay policy.
///
/// ⭐⭐ ROUND 4: lớp này giữ NGUYÊN luật đọc-cũ (#63: sự kiện có chấm không dấu
/// vẫn đẩy belief) dưới id `conservative-bkt-v1` — vì đổi hành vi dưới cùng
/// một `policyId` là REPLAY SILENTLY REINTERPRET. Nó KHÔNG còn là mặc định:
/// [replayMastery] mặc định dùng [ValidatedOnlyBktPolicy]. Dùng lớp này
/// tường minh chỉ để ĐỐI CHIẾU/audit («mastery sẽ ra sao nếu đếm dữ liệu
/// cũ») — không cho màn hình trẻ/phụ huynh.
class ConservativeBktPolicy implements EvidenceWeightingPolicy {
  const ConservativeBktPolicy();

  /// ⭐ Round 3 (A3): `true` ⇒ chỉ sự kiện mang dấu validator ĐƯỢC ĐĂNG KÝ
  /// cấp năng lực mới đẩy belief — xem [ValidatedOnlyBktPolicy].
  bool get requireValidation => false;

  @override
  String get policyId => 'conservative-bkt-v1';

  /// `guess` theo CẤU TRÚC dạng bài. `null` = không biết dạng ⇒ fail closed.
  double? _structuralGuess(ResponseFormat f, BktParams p) => switch (f) {
        ResponseFormat.freeResponse => p.guess,
        // 1/4 là sàn cấu trúc; nếu tham số khai lớn hơn thì tin tham số.
        ResponseFormat.multipleChoice4 => p.guess > 0.25 ? p.guess : 0.25,
        ResponseFormat.unknown => null,
      };

  @override
  EvidenceUpdate interpret(LearningEvent e, BktParams p) {
    switch (e.kind) {
      case EvidenceKind.independentAttempt:
      case EvidenceKind.selfCorrection:
        // Tự làm — bằng chứng đầy đủ. `selfCorrection` KHÔNG cộng thêm điểm
        // thưởng nào: chưa có hằng số nào justify được mức thưởng, và hướng
        // sai an toàn là ĐÁNH GIÁ THẤP (doctrine F1). Ghi nhận định tính của
        // nó nằm ở chính loại sự kiện trong log.
        final guess = _structuralGuess(e.format, p);
        if (e.correct == null || guess == null) {
          // Không chấm được / không biết dạng ⇒ không claim gì. UNKNOWN không
          // bao giờ thành FAILED.
          return EvidenceUpdate.noOp;
        }
        // ⭐⭐ Round 3 (Founder A3): dấu validator LẠ / không cấp năng lực ⇒
        // không claim gì (RETRIEVED ≠ PERMITTED áp cho cả validator).
        if (e.hasRejectedValidation) return EvidenceUpdate.noOp;
        if (requireValidation && !e.hasApprovedValidation) {
          return EvidenceUpdate.noOp;
        }
        return EvidenceUpdate(
          likelihood: ObservationLikelihood(
            pCorrectGivenKnown: 1 - p.slip,
            pCorrectGivenUnknown: guess,
          ),
          appliesLearning: true,
          countsAsIndependent: true,
        );

      case EvidenceKind.guidedAttempt:
      case EvidenceKind.postHintSuccess:
        // Câu trả lời bị can thiệp nhuộm ⇒ khai báo KHÔNG ĐỊNH LƯỢNG ĐƯỢC
        // mức tiết lộ ⇒ tỷ số 1 (không claim). Có dạy + có tự thử ⇒ `learn` áp.
        return const EvidenceUpdate(
          likelihood: ObservationLikelihood(
              pCorrectGivenKnown: 1, pCorrectGivenUnknown: 1),
          appliesLearning: true,
          countsAsIndependent: false,
        );

      case EvidenceKind.hintRequested:
      case EvidenceKind.hintShown:
        // Can thiệp, không phải câu trả lời. Công `learn` gắn vào lần TỰ THỬ
        // theo sau (guidedAttempt/postHintSuccess), không gắn vào việc hiện
        // gợi ý — nếu không, chỉ cần bấm "xem gợi ý" 10 lần là mastery tăng.
        return EvidenceUpdate.noOp;

      case EvidenceKind.finalCorrectness:
        // Kết quả chốt của cả bài — TRÙNG với lần thử cuối đã ghi. Chấm cả
        // hai là đếm đôi cùng một bằng chứng. Giữ để báo cáo, không để chấm.
        return EvidenceUpdate.noOp;

      case EvidenceKind.participation:
        // ⭐⭐ D1: tự báo / hoàn thành KHÔNG CHẤM ⇒ không claim gì về năng lực,
        // không `learn`, không đếm. Cùng kết cục với independentAttempt +
        // correct == null trước đây — BKT không đổi.
        return EvidenceUpdate.noOp;
    }
  }
}

/// ⭐⭐ WAL-210 round 3 (Founder A3) — luật SIẾT: mastery CHỈ từ sự kiện mang
/// dấu validator được đăng ký (`hasApprovedValidation`). Sự kiện có chấm
/// nhưng không dấu (dữ liệu trước hợp đồng, emitter chưa đóng dấu) ⇒ noOp —
/// đọc là `historicalUnvalidated`, giữ trong lịch sử, không viết lại.
/// Là policy THAY ĐƯỢC (ADR-004): đổi luật = replay, không migration.
///
/// ⭐⭐ ROUND 4 (Founder §4): ĐÂY LÀ MẶC ĐỊNH của [replayMastery] — mọi màn
/// đọc mastery qua `masteryFromStore` (Home, Progress, Learning Map, Parent,
/// Knowledge State, Assessment result) nhận luật này mà không đổi mã gọi.
/// Hệ quả từng màn: docs/architecture/ROUND4-RUNTIME-CONTRACTS.md.
class ValidatedOnlyBktPolicy extends ConservativeBktPolicy {
  const ValidatedOnlyBktPolicy();

  @override
  bool get requireValidation => true;

  @override
  String get policyId => 'validated-only-bkt-v1';
}

/// ⭐ Luật đọc bằng chứng MẶC ĐỊNH của toàn app (ROUND 4): siết.
const EvidenceWeightingPolicy defaultEvidencePolicy = ValidatedOnlyBktPolicy();

/// ⭐⭐ Mastery là **giá trị suy ra** = replay log thô qua một policy.
///
/// Đây là điểm F3 khác về chất so với bản vá `SupportLevel`: đổi luật ⇒ tính
/// lại toàn bộ từ sự kiện gốc. Không gì bị nghiền mất.
///
/// ROUND 4: mặc định [defaultEvidencePolicy] (`validated-only-bkt-v1`).
CaseMastery replayMastery(
  EvidenceLog log,
  BktParams p, {
  EvidenceWeightingPolicy policy = defaultEvidencePolicy,
}) {
  var m = CaseMastery.initial(log.skillCaseId, p);
  for (final e in log.events) {
    m = applyEvidence(m, e, policy.interpret(e, p), p);
  }
  return m;
}

/// Áp một sự kiện đã-diễn-giải vào belief. Toàn bộ số học nằm ở
/// [bktPosterior] — hàm này chỉ nối likelihood với sổ sách đếm.
CaseMastery applyEvidence(
  CaseMastery m,
  LearningEvent e,
  EvidenceUpdate u,
  BktParams p,
) {
  var pm = m.pMastery;
  final scored = u.likelihood != null && e.correct != null;
  if (scored && u.likelihood!.isInformative) {
    pm = bktPosterior(
      pm,
      e.correct!,
      u.likelihood!.pCorrectGivenKnown,
      u.likelihood!.pCorrectGivenUnknown,
    );
  }
  if (u.appliesLearning) pm = pm + (1 - pm) * p.learn;

  final independent = scored && u.countsAsIndependent;
  final supported = e.isSystemInfluenced;
  return CaseMastery(
    skillCaseId: m.skillCaseId,
    pMastery: pm,
    evidenceCount: m.evidenceCount + (independent ? 1 : 0),
    supportedCount: m.supportedCount + (supported ? 1 : 0),
    independentCorrect:
        m.independentCorrect + (independent && e.correct! ? 1 : 0),
    independentIncorrect:
        m.independentIncorrect + (independent && !e.correct! ? 1 : 0),
    lastIndependentEvidenceAt:
        independent ? e.at : m.lastIndependentEvidenceAt,
  );
}
