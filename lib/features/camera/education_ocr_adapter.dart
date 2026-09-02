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
String? extractFractionExpression(List<String> lines) {
  final re = RegExp(r'(\d{1,3})\s*/\s*(\d{1,3})\s*([+\-−])\s*(\d{1,3})\s*/\s*(\d{1,3})');
  final found = <String>{};
  for (final line in lines) {
    for (final m in re.allMatches(line)) {
      final op = m.group(3) == '−' ? '-' : m.group(3)!;
      found.add('${m.group(1)}/${m.group(2)} $op ${m.group(4)}/${m.group(5)}');
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
