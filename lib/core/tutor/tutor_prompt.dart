/// WAL-30 (phần tất định) — TutorPrompt: chuồng cho Generative Tutor.
///
/// HARD GATE Founder §E đã dựng (eval L1+L2, WAL-101). Phần này là nửa
/// TẤT ĐỊNH còn lại: prompt được LẮP từ TutorScope + TeachingProvenance —
/// không tay ai (kể cả LLM) chọn được nội dung ngoài chuồng, vì nội dung
/// đi vào prompt CHỈ đến từ các cấu trúc đã fail-closed:
/// - method: CHỈ từ scope.allowedMethods (APPLICABLE ∩ ALLOWED);
/// - từ vựng: CHỈ liệt kê terminology của stage; cấm dùng ngoài danh sách;
/// - nguồn: sourceLineForChild (demonstrated ≠ «Theo SGK» đã mutation-guard);
/// - thang ±1 + REVEAL gate + luật khen: chép từ hằng công khai, không tự chế.
///
/// KHÔNG gọi LLM ở đây. Việc nối model thật (chi phí + bật production) là
/// quyết định Founder; file này bảo đảm khi bật, mọi lời dạy sinh ra đều
/// đo được bằng eval L1/L2 và bị chặn cấu trúc trước khi tới trẻ.
library;

import '../curriculum/pedagogical_boundary.dart';
import 'teaching_provenance.dart';
import 'tutor_feedback.dart' show bannedAbilityPraise;

class TutorPromptRequest {
  const TutorPromptRequest({
    required this.scope,
    required this.methodId,
    required this.exerciseCase,
    required this.problemText,
    required this.grade,
  });

  final TutorScope scope;
  final String methodId;
  final String? exerciseCase;
  final String problemText;
  final int grade;
}

/// Lắp prompt. Trả `null` (fail closed) khi [explainTeaching] không cấp
/// provenance — ngoài scope thì KHÔNG CÓ prompt nào tồn tại để mà gọi model.
String? buildTutorPrompt(TutorPromptRequest r) {
  final teaching = explainTeaching(
    scope: r.scope,
    methodId: r.methodId,
    exerciseCase: r.exerciseCase,
  );
  if (teaching == null) return null;

  final m = teaching.method;
  final terms = r.scope.allowedTerminology.toList()..sort();
  final banned = bannedAbilityPraise.join(', ');

  return '''
Bạn là SAM — gia sư cú tím-vàng cho học sinh lớp ${r.grade} Việt Nam.

BÀI: ${r.problemText}
DẠNG BÀI: ${r.exerciseCase}

PHƯƠNG PHÁP DUY NHẤT ĐƯỢC DÙNG: «${m.name}».
${teaching.whyLineForChild}
NGUỒN (nói đúng nguyên văn khi trẻ hỏi "sao cô/thầy dạy khác"): ${teaching.sourceLineForChild}

TỪ VỰNG ĐƯỢC PHÉP: ${terms.join(' · ')}.
Tuyệt đối không dùng thuật ngữ toán học ngoài danh sách trên — kể cả khi
em giải thích đúng, một từ trẻ chưa gặp là dạy sai.

LUẬT HỖ TRỢ (thang ±1):
- Bắt đầu bằng câu hỏi gợi hướng, KHÔNG cho bước giải.
- Chỉ nâng đúng MỘT nấc mỗi lần trẻ vẫn bí: gợi ý → làm mẫu MỘT bước.
- KHÔNG BAO GIỜ đưa lời giải trọn vẹn khi trẻ chưa tự thử (REVEAL gate).
- Trẻ trong bài kiểm tra: không gợi ý gì hết.

LUẬT KHEN: khen nỗ lực/quá trình/chiến lược. CẤM các từ: $banned.

Trả lời NGẮN (≤2 câu), tiếng Việt, xưng "tớ" với trẻ.''';
}
