/// ⭐⭐⭐ F1 — ConceptSummary: tóm tắt bằng chứng **không công bố vượt bằng chứng**.
///
/// Founder decision (2026-09-01) BÁC câu hỏi *"Concept mastery = min hay mean?"*
/// như một khung sai. Câu hỏi thay thế:
///
///   *"Hệ thống nên TÓM TẮT bằng chứng qua các SkillCase thế nào mà không
///    claim thứ nó chưa từng quan sát?"*
///
/// Trả lời: một con số không làm được việc đó, vì ba trục sau **độc lập**:
///
///   MASTERY ước lượng cao  ≠  COVERAGE đủ  ≠  CONFIDENCE cao
///
/// - `min`/`mean` đều trộn ba trục vào một vô hướng rồi mất hai trục.
/// - `mean` giấu ca hỏng sau ca vững (đã bác từ ADR-001).
/// - `min` giấu ca CHƯA GẶP — và biến "đã phủ hết" với "còn ca chưa hỏi"
///   thành cùng một kết luận (đã bác bằng falsification F1, ADR-003).
///
/// Kiến trúc: mọi giá trị ở đây **suy ra được từ log thô** (`EvidenceLog` +
/// policy, xem `evidence_weighting.dart`) — đổi luật tổng hợp là tính lại,
/// không migration. `ConceptMastery.stateAt`/`derived` cũ hạ cấp thành
/// heuristic xếp hạng NỘI BỘ; **mọi claim hướng phụ huynh đi qua tệp này**.
library;

import 'mastery.dart';

/// ⭐ Trục COVERAGE — đã quan sát bao nhiêu phần của khái niệm.
///
/// "Quan sát" nghĩa là có **bằng chứng độc lập** (`evidenceCount > 0`). Một ca
/// chỉ luyện với gợi ý là ca CHƯA quan sát — nếu không, F3 lại chui vào F1
/// bằng cửa sau: hệ thống can thiệp đủ nhiều thì coverage tự "đầy".
class Coverage {
  const Coverage({required this.observedCases, required this.unobservedCases});

  /// Cả hai danh sách **đã sort theo id** — tất định (doctrine F4).
  final List<String> observedCases;
  final List<String> unobservedCases;

  int get knownCaseCount => observedCases.length + unobservedCases.length;

  /// `null` khi không biết ca nào tồn tại — không giả vờ 0% hay 100%.
  double? get fraction => knownCaseCount == 0
      ? null
      : observedCases.length / knownCaseCount;

  bool get isComplete => knownCaseCount > 0 && unobservedCases.isEmpty;
}

/// ⭐ Trục CONFIDENCE — tin được bằng chứng ĐÃ CÓ tới đâu.
///
/// Cố ý KHÔNG chứa coverage: gộp vào là ba trục sập lại còn hai, đúng thứ
/// Decision 1 cấm. Coverage đứng riêng; claim gate dùng cả hai.
///
/// Tổng hợp bằng **min** — một mắt xích yếu (quá ít, quá cũ, quá mâu thuẫn)
/// phải kéo cả chuỗi xuống; lấy trung bình sẽ để "nhiều bằng chứng" che "toàn
/// bằng chứng cũ" — chính kiểu lỗi `mean` đã bị bác ở ADR-001. Đây là lựa
/// chọn suy từ nhất quán với bằng chứng cũ, không phải hằng số mới.
class ConfidenceFactors {
  const ConfidenceFactors({
    required this.volume,
    required this.consistency,
    required this.recency,
  });

  /// Đủ SỐ LƯỢNG bằng chứng độc lập chưa (min trên các ca đã quan sát).
  final double volume;

  /// Bằng chứng có TỰ MÂU THUẪN không: `|đúng − sai| / (đúng + sai)` tính
  /// TRONG TỪNG CA rồi lấy min. 0 khi chia đôi hoàn hảo, 1 khi đồng thuận.
  /// Không hằng số.
  ///
  /// ⭐ Vì sao TRONG TỪNG CA: một ca toàn đúng cạnh một ca toàn sai KHÔNG
  /// phải mâu thuẫn — đó chính là `caseTransitionGap`, thông tin chẩn đoán
  /// quý nhất của mô hình. Đo mâu thuẫn gộp toàn khái niệm sẽ nghiền tín
  /// hiệu đó thành nhiễu — đúng lỗi "một con số cho cả khái niệm" mà
  /// SkillCase sinh ra để tránh.
  /// ⚠️ Hạn chế đã biết: chuỗi "sai nhiều rồi đúng dần" (đang HỌC) cũng bị
  /// tính là mâu thuẫn — hướng sai này AN TOÀN (đánh giá thấp độ chắc),
  /// nhưng khi có dữ liệu thật nên thay bằng consistency có trọng số gần đây.
  final double consistency;

  /// Bằng chứng có CÒN MỚI không (min trên các ca — ca cũ nhất quyết định).
  /// Đây là "belief về ước lượng phai đi", KHÔNG phải mô hình quên F5 —
  /// Founder tách hai thứ đó, và trục này không đụng vào `pMastery`.
  final double recency;

  double get overall =>
      [volume, consistency, recency].reduce((a, b) => a < b ? a : b);
}

/// ⭐⭐ Điều DUY NHẤT được phép nói với phụ huynh về một khái niệm.
///
/// Bất biến Decision 1: một khái niệm KHÔNG BAO GIỜ thành `mastered` chỉ vì
/// các ca đã quan sát đều mạnh trong khi còn ca bắt buộc chưa quan sát.
enum ConceptClaim {
  /// Chưa có sự kiện nào. KHÁC `insufficientEvidence` — chưa hỏi ≠ hỏi rồi
  /// mà chưa rõ. Và tuyệt đối KHÔNG phải "failed".
  noEvidence,

  /// Có hoạt động nhưng bằng chứng không đỡ nổi kết luận nào: quá thưa, quá
  /// cũ, tự mâu thuẫn, hoặc CHỈ TOÀN luyện-có-hỗ-trợ. Câu trả lời hợp lệ.
  insufficientEvidence,

  /// Bằng chứng đủ tin và chỉ ra ít nhất một ca đang hỏng.
  needsWork,

  /// Đang tiến bộ — không ca nào hỏng hẳn, chưa ca nào tới mức claim vững.
  developing,

  /// ⭐ Vững MỌI CA ĐÃ QUAN SÁT — nhưng còn ca chưa quan sát nên KHÔNG được
  /// nói "vững khái niệm". Đây là chỗ `min` cũ nói dối.
  strongOnObserved,

  /// Vững + phủ hết ca đã biết + bằng chứng đủ tin. Chỉ ca này Parent Coach
  /// được dùng chữ "vững/mastered".
  mastered,
}

/// ⭐ Ngưỡng — **có tên, có lý do, thay được**. Không hằng số trôi nổi trong
/// công thức (yêu cầu Founder: no arbitrary constants without justification).
///
/// Tất cả là GIẢ THUYẾT V1, chờ dữ liệu thật để khớp lại. Lý do từng con số:
class SummaryPolicy {
  const SummaryPolicy({
    this.masteredAt = 0.85,
    this.practiceBelow = 0.6,
    this.confidenceFloor = 0.6,
    this.minIndependentPerCase = 2,
    this.supportDilutionPerCase = 4,
    this.freshWithin = const Duration(days: 30),
    this.staleAfter = const Duration(days: 180),
    this.weakestTieEpsilon = 0.05,
  });

  /// 0.85 — kế thừa `ConceptMastery.stateAt` và cùng vùng với
  /// MASTERY_THRESHOLD của OATutor. Giữ nguyên để hai tầng không cãi nhau.
  final double masteredAt;

  /// 0.6 — kế thừa `stateAt(practiceBelow)`.
  final double practiceBelow;

  /// 0.6 — cùng số với `confidenceFloor` của `remediationFor` (concept.dart):
  /// một chuẩn "đủ tin để nói ra" duy nhất trong toàn kernel.
  final double confidenceFloor;

  /// 2 — suy từ chính mô hình: BKT khai `slip > 0`, nghĩa là MỘT lần làm có
  /// thể là trượt tay theo giả định của chính ta. Claim với phụ huynh phải
  /// sống sót ít nhất một lần trượt được mô hình thừa nhận ⇒ cần ≥ 2.
  final int minIndependentPerCase;

  /// ⭐ ADR-007 (từ số đo WAL-87): stream NẶNG HỖ TRỢ claim trên rất ít mẫu
  /// độc lập bị hiệu chuẩn kém — FALSE TRUSTED 7–13% số claim ở học sinh chậm
  /// trong mô phỏng. Cứ mỗi [supportDilutionPerCase] lần trả-lời-có-hỗ-trợ,
  /// yêu cầu bằng chứng độc lập của ca tăng thêm 1:
  /// `cần = minIndependentPerCase + supportedCount ~/ supportDilutionPerCase`.
  /// Stream thuần độc lập (supportedCount = 0) KHÔNG đổi hành vi.
  /// 4 là GIẢ THUYẾT V1 — khớp lại bằng dữ liệu thật; cơ chế mới là quyết định.
  final int supportDilutionPerCase;

  /// 30/180 ngày — placeholder có lý do (mất mát sau kỳ nghỉ hè đo được ở
  /// văn liệu ~3 tháng); sẽ do F5 thay thế bằng mô hình thời gian thật.
  final Duration freshWithin;
  final Duration staleAfter;

  /// Chênh lệch nhỏ hơn mức này giữa các ca là KHÔNG phân giải được bằng dữ
  /// liệu hiện có ⇒ không được chọn một ca "yếu nhất" duy nhất — phải nêu cả
  /// nhóm (Founder, Decision 5).
  final double weakestTieEpsilon;
}

/// Số liệu quan sát của MỘT ca — để mọi câu nói trích dẫn được đúng ca
/// (doctrine F4: truy vết tới bằng chứng, không trích số liệu gộp).
class CaseObservation {
  const CaseObservation({
    required this.pMastery,
    required this.evidenceCount,
    required this.lastEvidenceAt,
  });

  final double pMastery;
  final int evidenceCount;
  final DateTime? lastEvidenceAt;
}

/// ⭐⭐⭐ Tóm tắt bằng chứng của MỘT khái niệm — thứ Parent Coach đọc.
class ConceptSummary {
  const ConceptSummary({
    required this.conceptId,
    required this.estimatedMastery,
    required this.coverage,
    required this.confidence,
    required this.confidenceFactors,
    required this.weakestObservedCases,
    required this.unobservedCases,
    required this.evidenceCount,
    required this.supportedPracticeCount,
    required this.lastEvidenceAt,
    required this.claim,
    this.observedCaseFacts = const {},
  });

  final String conceptId;

  /// Ước lượng TRUNG TÂM — trung bình có trọng số theo lượng bằng chứng
  /// (nhiều quan sát ⇒ hậu nghiệm chụm hơn ⇒ nặng ký hơn; precision-weighting
  /// chuẩn, không hằng số mới). `null` = chưa quan sát gì.
  ///
  /// ⚠️ CHỈ là heuristic XẾP HẠNG nội bộ (chọn bài, sắp thứ tự ôn). KHÔNG
  /// BAO GIỜ hiển thị như một claim — claim là [claim], và gate của nó dùng
  /// min trên các ca chứ không dùng số này. Một câu nói với phụ huynh đòi
  /// bằng chứng mạnh hơn một heuristic xếp hạng (Founder, Decision 1).
  final double? estimatedMastery;

  final Coverage coverage;

  /// = [ConfidenceFactors.overall]. Trục thứ ba, độc lập với hai trục kia.
  final double confidence;

  /// Giữ nguyên từng thừa số để MỌI con số truy vết được (doctrine F4).
  final ConfidenceFactors confidenceFactors;

  /// Các ca yếu nhất TRONG SỐ ĐÃ QUAN SÁT. Có thể nhiều hơn một khi chênh
  /// lệch nằm trong `weakestTieEpsilon` — khi bằng chứng không phân giải
  /// được, nói cả nhóm chứ không bịa ra một thứ tự (Decision 5). Sort
  /// (pMastery tăng, id) — tất định, không phụ thuộc thứ tự chèn Map.
  final List<String> weakestObservedCases;

  /// Các ca CHƯA TỪNG có bằng chứng độc lập — nói thẳng ra, không giấu.
  final List<String> unobservedCases;

  /// Tổng lần trả lời TỰ LÀM trên mọi ca.
  final int evidenceCount;

  /// Tổng lần luyện CÓ HỖ TRỢ — để Coach nói được "con đang luyện với gợi ý,
  /// chưa có bằng chứng tự làm" thay vì im lặng hoặc nói dối.
  final int supportedPracticeCount;

  /// Thời điểm bằng chứng độc lập gần nhất trên toàn khái niệm.
  final DateTime? lastEvidenceAt;

  final ConceptClaim claim;

  /// Số liệu từng ca ĐÃ QUAN SÁT — nguồn cho citation của tầng phát ngôn.
  final Map<String, CaseObservation> observedCaseFacts;

  /// ⭐ Suy tóm tắt từ trạng thái các ca + danh mục ca ĐÃ BIẾT của khái niệm.
  ///
  /// [knownCaseIds] đến từ danh mục SkillCase (đo từ corpus). Ca mới phát
  /// hiện sau này ⇒ gọi lại hàm này với danh mục mới ⇒ coverage tự tụt ⇒
  /// claim tự hạ. Không có trạng thái "mastered" nào được lưu để mà quên hạ.
  static ConceptSummary of(
    ConceptMastery mastery, {
    required Set<String> knownCaseIds,
    required DateTime now,
    SummaryPolicy policy = const SummaryPolicy(),
  }) {
    // Hợp nhất: ca trong danh mục ∪ ca đã có trạng thái (phòng ca có bằng
    // chứng nhưng chưa vào danh mục — bằng chứng thật không bị vứt).
    final allIds = <String>{...knownCaseIds, ...mastery.cases.keys};
    final observed = <String, CaseMastery>{};
    var supported = 0;
    for (final id in allIds) {
      final c = mastery.cases[id];
      if (c == null) continue;
      supported += c.supportedCount;
      if (c.hasEvidence) observed[id] = c;
    }
    final unobserved = allIds.difference(observed.keys.toSet()).toList()..sort();
    final coverage = Coverage(
      observedCases: observed.keys.toList()..sort(),
      unobservedCases: unobserved,
    );

    // ── không có bằng chứng độc lập nào ────────────────────────────────────
    if (observed.isEmpty) {
      final anyActivity = supported > 0;
      return ConceptSummary(
        conceptId: mastery.conceptId,
        estimatedMastery: null,
        coverage: coverage,
        confidence: 0,
        confidenceFactors:
            const ConfidenceFactors(volume: 0, consistency: 0, recency: 0),
        weakestObservedCases: const [],
        unobservedCases: unobserved,
        evidenceCount: 0,
        supportedPracticeCount: supported,
        lastEvidenceAt: null,
        // ⭐ Toàn post-hint success vẫn là ĐÂY: luyện có hỗ trợ không phải
        // bằng chứng (F3), nên không claim nào vượt insufficientEvidence.
        claim: anyActivity
            ? ConceptClaim.insufficientEvidence
            : ConceptClaim.noEvidence,
      );
    }

    // ── ước lượng trung tâm: trung bình trọng số theo evidenceCount ────────
    var wSum = 0.0, wTotal = 0;
    var evidenceTotal = 0;
    DateTime? lastAt;
    var minObserved = 1.0;
    for (final c in observed.values) {
      wSum += c.pMastery * c.evidenceCount;
      wTotal += c.evidenceCount;
      evidenceTotal += c.evidenceCount;
      if (c.pMastery < minObserved) minObserved = c.pMastery;
      final at = c.lastIndependentEvidenceAt;
      if (at != null && (lastAt == null || at.isAfter(lastAt))) lastAt = at;
    }
    final estimated = wTotal == 0 ? null : wSum / wTotal;

    // ── confidence: min(volume, consistency, recency) — từng thừa số là
    //    min trên các ca đã quan sát (mắt xích yếu nhất quyết định) ─────────
    var volume = 1.0;
    var recency = 1.0;
    var consistency = 1.0;
    for (final c in observed.values) {
      // ADR-007: luyện-có-hỗ-trợ nhiều ⇒ cần NHIỀU bằng chứng độc lập hơn
      // mới đủ tin để claim — các mẫu độc lập thưa đang cõng cả kết luận.
      final required = policy.minIndependentPerCase +
          c.supportedCount ~/ policy.supportDilutionPerCase;
      final v = c.evidenceCount / required;
      if (v < volume) volume = v > 1 ? 1 : v;
      recency = _min(recency, _recencyScore(c.lastIndependentEvidenceAt, now, policy));
      final attempts = c.independentCorrect + c.independentIncorrect;
      if (attempts > 0) {
        consistency = _min(consistency,
            (c.independentCorrect - c.independentIncorrect).abs() / attempts);
      }
    }
    final factors = ConfidenceFactors(
        volume: volume, consistency: consistency, recency: recency);
    final confidence = factors.overall;

    // ── ca yếu nhất: cả NHÓM trong epsilon, sort tất định ──────────────────
    final weakest = observed.entries
        .where((e) =>
            e.value.pMastery <= minObserved + policy.weakestTieEpsilon)
        .map((e) => e.key)
        .toList()
      ..sort((a, b) {
        final pa = observed[a]!.pMastery, pb = observed[b]!.pMastery;
        return pa != pb ? pa.compareTo(pb) : a.compareTo(b);
      });

    // ── claim: gate bảo thủ, thứ tự cố ý ───────────────────────────────────
    final ConceptClaim claim;
    if (confidence < policy.confidenceFloor) {
      // Bằng chứng không đủ tin thì KHÔNG kết luận theo hướng nào — kể cả
      // "needsWork": báo động nhầm với phụ huynh cũng là công bố vượt
      // bằng chứng, chỉ là vượt theo hướng ngược lại.
      claim = ConceptClaim.insufficientEvidence;
    } else if (minObserved < policy.practiceBelow) {
      claim = ConceptClaim.needsWork;
    } else if (minObserved >= policy.masteredAt) {
      // Gate "vững" lượng hoá TRÊN MỌI CA — nên dùng min, và min chỉ sống ở
      // đây: làm GATE cho claim, không làm "sự thật" của mastery.
      claim = coverage.isComplete
          ? ConceptClaim.mastered
          : ConceptClaim.strongOnObserved; // ⭐ bất biến Decision 1
    } else {
      claim = ConceptClaim.developing;
    }

    return ConceptSummary(
      conceptId: mastery.conceptId,
      estimatedMastery: estimated,
      coverage: coverage,
      confidence: confidence,
      confidenceFactors: factors,
      weakestObservedCases: weakest,
      unobservedCases: unobserved,
      evidenceCount: evidenceTotal,
      supportedPracticeCount: supported,
      lastEvidenceAt: lastAt,
      claim: claim,
      observedCaseFacts: {
        for (final id in coverage.observedCases)
          id: CaseObservation(
            pMastery: observed[id]!.pMastery,
            evidenceCount: observed[id]!.evidenceCount,
            lastEvidenceAt: observed[id]!.lastIndependentEvidenceAt,
          ),
      },
    );
  }

  static double _min(double a, double b) => a < b ? a : b;

  /// 1 khi còn mới, 0 khi quá hạn, tuyến tính ở giữa. Không có timestamp =
  /// không chấm được độ mới ⇒ 0 (fail closed — bằng chứng không rõ lúc nào
  /// không được tính là "mới").
  static double _recencyScore(DateTime? at, DateTime now, SummaryPolicy p) {
    if (at == null) return 0;
    final age = now.difference(at);
    if (age <= p.freshWithin) return 1;
    if (age >= p.staleAfter) return 0;
    final span = p.staleAfter - p.freshWithin;
    return 1 - (age - p.freshWithin).inSeconds / span.inSeconds;
  }
}
