/// ⭐⭐⭐ F3 — LearningEvidence: **sự kiện thô**, giữ nguyên, không diễn giải sẵn.
///
/// Lỗ hổng F3 (ADR-003) được vá lần đầu bằng `SupportLevel` truyền vào lúc cập
/// nhật. Cách đó sửa được TRIỆU CHỨNG mà không sửa được NGUYÊN NHÂN: belief là
/// thứ duy nhất được lưu, nên một khi luật quy công thay đổi thì **không tính
/// lại được** — bằng chứng cũ đã bị nghiền thành một con số.
///
/// Founder decision (2026-09-01): *"Preserve raw events. Derived mastery must
/// remain recomputable."* ⇒ tệp này là **nguồn sự thật**; `CaseMastery` hạ xuống
/// thành **giá trị suy ra**, và luật suy ra là thứ **thay thế được**.
///
/// Vì sao quan trọng hơn một refactor: vòng lặp tự xác nhận
///
///   can thiệp → đúng sau gợi ý → ghi công mastery → hệ thống tự tin hơn →
///   thôi can thiệp → trẻ sai → can thiệp lại…
///
/// chỉ chặn được nếu ta còn phân biệt được *"đúng"* nào là do đứa trẻ và
/// *"đúng"* nào là do hệ thống. Một cờ boolean `correct` **không mang** phân
/// biệt đó, và không có tham số `slip`/`guess` nào khôi phục lại được.
library;

import '../pedagogy/pedagogy_model.dart' show TeachingAct;
import 'mastery.dart';

/// ⭐ Bảy loại sự kiện Founder liệt kê. Cố ý **không** gộp.
///
/// Gộp là chỗ mất thông tin: `postHintSuccess` và `independentAttempt` cùng cho
/// `correct == true`, nhưng nói hai điều khác hẳn nhau về đứa trẻ.
enum EvidenceKind {
  /// Trẻ tự làm, chưa có hỗ trợ nào trên màn hình. **Bằng chứng đầy đủ.**
  independentAttempt,

  /// Trẻ **chủ động xin** gợi ý. Bản thân nó là bằng chứng — về siêu nhận thức
  /// (biết mình chưa biết), không phải về kiến thức. Không đổi belief.
  hintRequested,

  /// Hệ thống **chủ động** hiện gợi ý (trẻ không xin). Khác `hintRequested`:
  /// một đằng trẻ tự đánh giá là bí, một đằng hệ thống đoán hộ. Nếu gộp, ta
  /// mất khả năng đo xem hệ thống có can thiệp quá sớm không.
  hintShown,

  /// Trả lời **trong khi** đang có hỗ trợ hiển thị.
  guidedAttempt,

  /// Đúng, **sau khi** đã xem gợi ý. KHÔNG phải bằng chứng tự làm được.
  postHintSuccess,

  /// Trẻ **tự phát hiện và tự sửa** cái sai của mình, không cần hỗ trợ mới.
  /// ⭐ Đây là bằng chứng MẠNH — mạnh hơn đúng-ngay-lần-đầu ở khía cạnh giám
  /// sát lời giải — và mô hình cũ không có chỗ nào biểu diễn nó.
  selfCorrection,

  /// Đáp án chốt của cả bài. Là **kết quả**, không phải một lần thử; giữ riêng
  /// để không đếm hai lần cùng một lần làm.
  finalCorrectness,
}

/// Dạng câu trả lời — quyết định `guess` **theo cấu trúc**, không phải theo cảm
/// tính. pyBKT gọi là `multigs`.
enum ResponseFormat {
  freeResponse,
  multipleChoice4,

  /// Không biết dạng ⇒ phải fail closed ở tầng trên, không tự chọn tham số.
  unknown,
}

/// ⭐ Một sự kiện học tập. **Bất biến, chỉ ghi thêm.**
///
/// Không có setter, không có `copyWith` đổi bản chất: log là append-only. Sửa
/// một sự kiện đã ghi là làm hỏng chính thứ khiến mastery tính lại được.
class LearningEvent {
  const LearningEvent({
    required this.eventId,
    required this.skillCaseId,
    required this.kind,
    required this.at,
    this.correct,
    this.conceptIds = const [],
    this.exerciseId,
    this.format = ResponseFormat.freeResponse,
    this.timeSpent,
    this.support,
    this.policyId,
    this.priorEventId,
    this.interventionId,
    this.knowledgeVersion,
    this.sourceDocumentId,
    this.lessonNo,
    this.act,
    this.learnerText,
  });

  final String eventId;

  /// ⭐ Đơn vị mastery (ADR-001). Sự kiện gắn vào **ca**, không phải khái niệm.
  final String skillCaseId;

  /// ⭐ F6-ready: một bài tập chạm **NHIỀU** khái niệm (Q-matrix / `cpt_seq`
  /// của EduStudio). Giữ dạng danh sách ngay từ bây giờ để không phải migrate
  /// dữ liệu học sinh thật về sau — schema là thứ đắt nhất để đổi muộn.
  final List<String> conceptIds;

  final String? exerciseId;
  final EvidenceKind kind;

  /// `null` khi sự kiện **không phải** một câu trả lời (`hintRequested`,
  /// `hintShown`). Đây là lý do nó nullable: ép về `false` là mã hoá
  /// **UNKNOWN thành FAILED** — điều Founder cấm thẳng.
  final bool? correct;

  /// ⭐ F5-ready. Mọi sự kiện có dấu thời gian ngay từ đầu, kể cả khi mô hình
  /// quên chưa được bật: không có nó thì F5 phải migrate lịch sử.
  final DateTime at;

  /// EduStudio: `cost_time` là trường hạng nhất ở **mọi** dataset KT/CD. Ghi
  /// sẵn để dữ liệu của ta dùng được với các mô hình đó về sau.
  final Duration? timeSpent;

  final ResponseFormat format;

  /// ⭐ LINEAGE (Founder Task Order 2026-09-01 §7 — gap ĐO ĐƯỢC): mức hỗ trợ
  /// ĐANG HIỂN THỊ tại thời điểm sự kiện. Thiếu trường này, «đúng sau MỘT
  /// gợi ý nhỏ» và «đúng sau khi xem TRỌN lời giải» đều chỉ là
  /// `postHintSuccess` — chỉ tái dựng được gián tiếp bằng đếm hintRequested
  /// đứng trước, và cách đó KHÔNG sống qua ghép session. `null` = sự kiện
  /// từ nguồn không biết mức hỗ trợ (dữ liệu cũ) — fail closed, không đoán 0.
  final SupportLevel? support;

  /// Phiên bản chính sách tutor đã tạo ra can thiệp quanh sự kiện này —
  /// để dữ liệu lịch sử không bị diễn giải lại theo chính sách mới
  /// (cùng bất biến REPLAY MUST NOT SILENTLY REINTERPRET).
  final String? policyId;

  /// Sự kiện TRẢ LỜI liền trước trong cùng phiên — quan hệ pre/post quanh
  /// can thiệp («sai → hint → đúng» lần được thành CHUỖI, không phải 3 điểm rời).
  final String? priorEventId;

  /// ⭐ §3 Master Order — «exact hint/intervention identity»: định danh CAN
  /// THIỆP đã hiển thị quanh sự kiện (policy/method@nấc). Thiếu nó, «gợi ý
  /// nào đã giúp con» không truy được về đúng nội dung — lineage đứt ở nấc
  /// cuối. `null` = sự kiện không gắn can thiệp (hoặc dữ liệu cũ).
  final String? interventionId;

  /// ⭐ WAL-114: PHIÊN BẢN MODEL TRI THỨC lúc sự kiện sinh ra — cặp với
  /// [policyId] (tutor policy version). Cùng bất biến REPLAY MUST NOT
  /// SILENTLY REINTERPRET: đổi model tri thức không được lặng lẽ đổi nghĩa
  /// evidence cũ. `null` = dữ liệu trước WAL-114.
  final String? knowledgeVersion;

  /// ⭐⭐ WAL-179/WAL-182 LINEAGE — sách + số bài IN mà sự kiện này thuộc về.
  /// `null` = chưa biết (dữ liệu cũ, hoặc sự kiện không gắn với một bài cụ
  /// thể) — KHÔNG suy đoán để lấp. Đây là trường "Event/Evidence này thuộc
  /// learning context nào" mà Learning Map/Parent View/Citation dùng chung —
  /// không phải field riêng chỉ phục vụ một tính năng.
  final String? sourceDocumentId;
  final int? lessonNo;

  /// Nước đi sư phạm (`TeachingAct`) đã tạo ra sự kiện này — "WHO speaks as
  /// SAM" truy được ngược về đúng act, không chỉ về policyId dạng chuỗi.
  /// `null` = sự kiện không gắn với một act cụ thể (hoặc dữ liệu cũ).
  final TeachingAct? act;

  /// Chữ trẻ viết nguyên văn (dự đoán/quan sát/giải thích/nháp…) — trước đây
  /// bị bỏ khi màn pop (vd `experiment_screen.dart`). `null` = act này không
  /// có/không cần chữ trẻ viết.
  final String? learnerText;

  /// Sự kiện này có phải một lần **trả lời** không (khác với một lần can thiệp).
  bool get isAttempt => switch (kind) {
        EvidenceKind.independentAttempt ||
        EvidenceKind.guidedAttempt ||
        EvidenceKind.postHintSuccess ||
        EvidenceKind.selfCorrection ||
        EvidenceKind.finalCorrectness =>
          true,
        EvidenceKind.hintRequested || EvidenceKind.hintShown => false,
      };

  /// ⭐⭐ Câu trả lời này có bị **chính can thiệp của hệ thống** quyết định không.
  ///
  /// Đây là câu hỏi trung tâm của F3, và nó là thuộc tính của **loại sự kiện**,
  /// không phải một tham số chỉnh tay.
  bool get isSystemInfluenced => switch (kind) {
        EvidenceKind.guidedAttempt || EvidenceKind.postHintSuccess => true,
        _ => false,
      };
}

/// ⭐⭐ Log thô của một ca. **Nguồn sự thật duy nhất.**
///
/// `CaseMastery` là hàm của log này; đổi luật quy công ⇒ chạy lại `replay`,
/// không mất gì. Đó là toàn bộ mục đích.
class EvidenceLog {
  const EvidenceLog({required this.skillCaseId, required this.events});

  const EvidenceLog.empty(this.skillCaseId) : events = const [];

  final String skillCaseId;

  /// Append-only, **theo thứ tự thời gian**. Thứ tự là dữ liệu, không phải chi
  /// tiết cài đặt: `selfCorrection` chỉ có nghĩa khi biết nó đứng SAU cái gì.
  final List<LearningEvent> events;

  EvidenceLog append(LearningEvent e) =>
      EvidenceLog(skillCaseId: skillCaseId, events: [...events, e]);

  /// Lần trả lời **tự làm** — thứ duy nhất được tính là bằng chứng độc lập.
  Iterable<LearningEvent> get independentAttempts => events.where((e) =>
      e.kind == EvidenceKind.independentAttempt ||
      e.kind == EvidenceKind.selfCorrection);

  /// Lần trả lời có hệ thống can thiệp.
  Iterable<LearningEvent> get influencedAttempts =>
      events.where((e) => e.isSystemInfluenced);

  /// Số lần hệ thống đã can thiệp (xin + tự hiện).
  int get interventionCount => events
      .where((e) =>
          e.kind == EvidenceKind.hintRequested ||
          e.kind == EvidenceKind.hintShown)
      .length;

  DateTime? get lastEventAt => events.isEmpty ? null : events.last.at;

  /// ⭐ Thời điểm bằng chứng **ĐỘC LẬP** gần nhất — không phải thời điểm chạm
  /// bài gần nhất. Một đứa trẻ xem gợi ý mỗi ngày vẫn có bằng chứng độc lập
  /// **cũ**, và Parent Coach phải nói theo cái sau.
  DateTime? get lastIndependentEvidenceAt {
    DateTime? last;
    for (final e in independentAttempts) {
      if (last == null || e.at.isAfter(last)) last = e.at;
    }
    return last;
  }
}
