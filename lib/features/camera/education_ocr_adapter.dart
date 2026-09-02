/// WAL-108 × WAL-110 — EDUCATION SAFETY ADAPTER cho OCR (bước 1 của boundary
/// WORKIZEN CAPABILITY → EDUCATION ADAPTER → SAM DOMAIN).
///
/// Bất biến (§6 Master Order): **OCR ≠ LearningEvidence.** Adapter chỉ được
/// sản xuất [PerceptionHypothesis] — theo KIỂU không có đường nào từ đây tới
/// evidence: hypothesis bắt buộc qua màn xác nhận (ConfirmProblemScreen,
/// WAL-64) mới thành ConfirmedProblem, rồi mới thành CanonicalProblem.
///
/// Fail closed ở chính adapter: không ghép được MỘT biểu thức duy nhất ⇒
/// `null` — tầng trên hiện ADMIT_UNCERTAINTY, không đoán hộ.
library;

import '../../core/perception/perception_provenance.dart';

abstract class EducationOcrAdapter {
  /// Ghi vào [PerceptionHypothesis.pipelineVersion] — lineage bắt buộc.
  String get pipelineVersion;

  /// `null` = không đọc được đề — hợp lệ, KHÔNG phải lỗi.
  Future<PerceptionHypothesis?> recognizeExpression(String imagePath);
}

/// Bóc «a/b ± c/d» từ các dòng OCR thô. Thuần Dart — test không cần ML Kit.
///
/// Luật fail-closed (giữ bằng test):
/// - 0 match ⇒ null;
/// - ≥2 biểu thức KHÁC NHAU trong cùng ảnh ⇒ null — trẻ chụp MỘT bài; hai
///   biểu thức nghĩa là khung hình lấy cả bài bên cạnh, tự chọn là đoán hộ;
/// - đúng một biểu thức (kể cả lặp lại nhiều dòng) ⇒ chuẩn hoá «a/b + c/d».
/// WAL-33 mitigation ① — PLAUSIBILITY số học theo khối tiểu học.
///
/// PHONE-SIM POC đo được: tăng recall mà không lọc plausibility là tăng
/// tỷ lệ «biểu thức bịa» từ OCR nhiễu. Luật KHAI RÕ (không ngưỡng ngầm):
/// - mẫu số 0 hoặc 1 ⇒ loại (phân số mẫu-1 không xuất hiện trong bài
///   cộng-trừ phân số tiểu học; «/1» thường là nhiễu gạch ngang);
/// - mẫu số > 99 ⇒ loại (ngoài phạm vi số tiểu học);
/// - tử > 3×mẫu ⇒ loại (hỗn-số-hoá bất thường — thường là dính chữ số).
/// Bị loại ⇒ KHÔNG vào tập ứng viên; nếu vì thế còn 0 ⇒ null (fail closed
/// giữ nguyên — thà hỏi lại còn hơn nhận đề sai).
bool plausibleGradeFraction(int a, int b, int c, int d) {
  bool okPair(int t, int m) => m > 1 && m <= 99 && t <= 3 * m;
  return okPair(a, b) && okPair(c, d);
}

String? extractFractionExpression(List<String> lines) {
  final re = RegExp(r'(\d{1,3})\s*/\s*(\d{1,3})\s*([+\-−])\s*(\d{1,3})\s*/\s*(\d{1,3})');
  final found = <String>{};
  for (final line in lines) {
    for (final m in re.allMatches(line)) {
      final a = int.parse(m.group(1)!), b = int.parse(m.group(2)!);
      final c = int.parse(m.group(4)!), d = int.parse(m.group(5)!);
      if (!plausibleGradeFraction(a, b, c, d)) continue; // ① loại nhiễu
      final op = m.group(3) == '−' ? '-' : m.group(3)!;
      found.add('$a/$b $op $c/$d');
    }
  }
  if (found.length != 1) return null; // 0 hoặc nhiều ⇒ chưa chắc
  return found.first;
}

/// Adapter giả cho test/dev — trả kịch bản định trước, giữ đúng contract.
class FakeEducationOcrAdapter implements EducationOcrAdapter {
  FakeEducationOcrAdapter(this._lines, {this.now});

  final List<String> _lines;
  final DateTime Function()? now;

  @override
  String get pipelineVersion => 'fake-ocr-v1+extract-v1';

  @override
  Future<PerceptionHypothesis?> recognizeExpression(String imagePath) async {
    final expr = extractFractionExpression(_lines);
    if (expr == null) return null;
    final t = (now ?? DateTime.now)();
    return PerceptionHypothesis(
      hypothesisId: 'fake-${t.microsecondsSinceEpoch}',
      rawImageRef: imagePath.split('/').last,
      expression: expr,
      pipelineVersion: pipelineVersion,
      at: t,
    );
  }
}
