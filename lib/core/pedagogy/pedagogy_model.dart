/// WAL-128 — PEDAGOGY MODEL v0: TeachingAct + AssistanceRung + Intent.
///
/// Phân tầng theo WAL-67 (falsified M:N, khớp VanLehn):
///   outer  LearningGoal   — decide() hiện tại (KHÔNG đổi enum LearningAction)
///   inner  TeachingAct    — nước đi TRONG bài, tầng NÀY
///   domain TeachingMethod — tham số TUỲ CHỌN của act ([PlannedAct.methodId])
///
/// Bất biến §32 (giữ bằng test + mutation):
/// - EVIDENCE KHÔNG ĐỔI NGHĨA: [SupportLevel] 4 nấc là từ vựng CỦA EVIDENCE,
///   bất biến qua replay. Act/Rung là từ vựng CỦA PEDAGOGY — map XUỐNG
///   SupportLevel khi ghi evidence, không bao giờ ngược lại.
/// - Mapping BẢO THỦ: nghi ngờ thì ghi mức hỗ trợ CAO hơn — «đúng sau PROMPT»
///   không được lẻn thành độc lập.
library;

import '../student/mastery.dart';

const String pedagogyModelVersion = 'pedagogy-model-v0';

/// §21 — thẩm quyền của một mảnh pedagogy. KHÔNG gắn tất cả là «Theo SGK».
enum PedagogyAuthority {
  /// SGV/SGK nói thẳng (trích được trang).
  sourceExplicit,

  /// Nguồn DẠY QUA ví dụ/hoạt động — không phát biểu quy tắc.
  sourceDemonstrated,

  /// SAM suy ra từ dữ liệu nguồn bằng luật tất định.
  samInferred,

  /// Văn liệu học thuật/nghiên cứu ngoài (Wood, Sweller, AutoTutor…).
  externalResearch,

  /// Giả thuyết đang thử — chưa có chỗ dựa; phải đo rồi mới lên hạng.
  experimental,
}

/// Intent sư phạm — TAXONOMY ĐO TỪ CORPUS (WAL-127 §4), không chép danh sách
/// 18 mục lý thuyết: 8 loại VN xuất hiện thật + 2 loại EN. Mở rộng khi corpus
/// hoặc validation (PED-D) chứng minh thiếu — không thêm trước.
enum PedagogicalIntent {
  activate, // Khởi động (ACTIVATE→DISCOVER là chuỗi phổ biến nhất: 45 bài)
  discover, // Khám phá / Hình thành kiến thức
  practice, // Luyện tập
  apply, // Vận dụng
  game, // Trò chơi (Tiểu học dày)
  consolidate, // Củng cố (TV1: 76 lần)
  reflect, // Nhìn lại/suy ngẫm — MỚI 1 hit trong sample, giữ vì GDPT yêu cầu
  review, // Ôn tập/Fun corner (EN)
}

/// 17 act ứng viên → 15 act sau merge của đối chiếu văn liệu (WAL-67 §1).
/// Mỗi act một dòng prior art trong TEACHINGACT-TAXONOMY-RESEARCH.md.
enum TeachingAct {
  observeWait, // im lặng có tên (wait-time, contingent tutoring)
  pumpRecall, // AutoTutor pump/prompt — «còn gì nữa?», mớm từ
  diagnosticProbe, // hỏi vì THÔNG TIN (model tracing)
  smallHint, // AutoTutor hint / OATutor ladder
  strategicHint, // nấc sâu hơn của cùng thang
  contrastCases, // WAL đi trước văn liệu — đã có test ở decide()
  explainConcept, // assertion — nước đi CUỐI chu trình, không phải đầu
  demonstrateStep, // modeling (cognitive apprenticeship)
  workedExample, // worked-example effect (Sweller)
  askExplanation, // self-explanation (Chi) — trẻ giảng lại
  askVerification, // CV 5588: kiểm chứng kết quả AI — chỗ dựa pháp quy
  reflect, // reflection
  stepBack, // fading — RÚT LUI là nước đi, không phải vắng mặt
  revealStep, // bottom-out một bước
  revealAnswer, // lời giải trọn vẹn — SupportLevel.fullSolution
}

/// Act ↔ mức hỗ trợ GHI VÀO EVIDENCE khi act được thực thi.
/// Bảo thủ: act đưa NỘI DUNG (mớm từ, gợi ý, so ca) đều ≥ hint.
SupportLevel supportLevelOf(TeachingAct act) => switch (act) {
      // Không đưa nội dung — trẻ vẫn tự làm.
      TeachingAct.observeWait ||
      TeachingAct.diagnosticProbe ||
      TeachingAct.askExplanation ||
      TeachingAct.askVerification ||
      TeachingAct.reflect ||
      TeachingAct.stepBack =>
        SupportLevel.none,
      // Đưa nội dung định hướng.
      TeachingAct.pumpRecall ||
      TeachingAct.smallHint ||
      TeachingAct.strategicHint ||
      TeachingAct.contrastCases =>
        SupportLevel.hint,
      // Làm mẫu / giảng — một phần lời giải lộ ra.
      TeachingAct.explainConcept ||
      TeachingAct.demonstrateStep ||
      TeachingAct.workedExample ||
      TeachingAct.revealStep =>
        SupportLevel.workedStep,
      TeachingAct.revealAnswer => SupportLevel.fullSolution,
    };

/// §17 — thang assistance chuẩn hoá 7 nấc (từ vựng pedagogy/blueprint).
enum AssistanceRung {
  independent,
  prompt,
  smallHint,
  strategicHint,
  partialScaffold,
  demonstration,
  workedSolution,
}

/// Rung → SupportLevel (evidence). ĐƠN ĐIỆU TĂNG — mutation-guarded: đảo một
/// nấc là «đúng sau demonstration» lẻn xuống hint.
SupportLevel rungToSupport(AssistanceRung r) => switch (r) {
      AssistanceRung.independent => SupportLevel.none,
      AssistanceRung.prompt ||
      AssistanceRung.smallHint ||
      AssistanceRung.strategicHint =>
        SupportLevel.hint,
      AssistanceRung.partialScaffold ||
      AssistanceRung.demonstration =>
        SupportLevel.workedStep,
      AssistanceRung.workedSolution => SupportLevel.fullSolution,
    };

/// Một nước đi ĐÃ LÊN KẾ HOẠCH: act + method tuỳ chọn (WAL-67 §2 — act
/// không cần method; method không sở hữu act).
class PlannedAct {
  const PlannedAct(this.act, {this.methodId});
  final TeachingAct act;
  final String? methodId;
}
