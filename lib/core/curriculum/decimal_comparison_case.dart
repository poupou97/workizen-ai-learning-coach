/// ⭐⭐ Khái niệm #2 — `so-sanh-so-thap-phan`: SkillCase đo từ corpus, lần hai.
///
/// SGK Toán 5 KNTT, Bài 11 tr.39 phát biểu quy tắc so sánh như **ba trường
/// hợp tường minh** (nguyên văn):
///   ① "Nếu phần nguyên của hai số đó KHÁC nhau…"        → so phần nguyên
///   ② "Nếu phần nguyên của hai số đó BẰNG nhau thì so sánh phần thập phân,
///      lần lượt từ hàng phần mười, hàng phần trăm…"      → so từng hàng
///   ③ "Nếu phần nguyên và phần thập phân … bằng nhau thì hai số đó bằng nhau."
/// Tr.38 còn gắn nhãn ví dụ theo ca: "3,5 > 2,75 (phần nguyên có 3 > 2)" ·
/// "2,75 > 2,29 (phần nguyên bằng nhau, hàng phần mười có 7 > 2)".
///
/// ⭐ Ca thứ tư nằm ở MỤC SAU (tr.40 "Số thập phân bằng nhau"): so sánh khi
/// hai phần thập phân KHÁC ĐỘ DÀI (76,3 vs 76,30) đòi luật "viết thêm/bỏ chữ
/// số 0 ở tận cùng" — dạy TÁCH RIÊNG, sau quy tắc ba ca. Một học sinh vững
/// ①② vẫn có thể vướng ca này ⇒ đúng cấu trúc `caseTransitionGap`.
///
/// ⭐⭐ Phát hiện cấu trúc MỚI so với `quy-dong`: ranh giới ca không chỉ nằm
/// GIỮA CÁC LỚP (lớp 4/lớp 5) — nó còn nằm GIỮA CÁC MỤC trong cùng một cụm
/// bài. `introducedGrade` không đủ nhỏ; định vị ca cần tới mục/trang
/// (`ConceptExposure.lessonId/pageStart` đã chứa được — không đổi schema).
library;

/// Phân tích tất định một bài so sánh hai số thập phân (dạng chữ "37,29").
class DecimalComparisonAnalysis {
  const DecimalComparisonAnalysis._({
    required this.intA,
    required this.intB,
    required this.fracA,
    required this.fracB,
  });

  final int intA;
  final int intB;

  /// Chuỗi chữ số thập phân ĐÚNG NHƯ BỀ MẶT ĐỀ BÀI — không chuẩn hoá.
  /// Ca là thuộc tính của BỀ MẶT bài toán: "0,70 vs 0,7" cần luật số-0 để
  /// NHÌN RA bằng nhau, dù giá trị bằng nhau. Chuẩn hoá trước là xoá mất ca.
  final String fracA;
  final String fracB;

  /// ① tr.39 — phần nguyên khác nhau.
  bool get integerPartDiffers => intA != intB;

  /// ② tr.39 — phần nguyên bằng, một hàng thập phân trong đoạn chung khác.
  bool get fractionDigitDiffers {
    if (integerPartDiffers) return false;
    final n = fracA.length < fracB.length ? fracA.length : fracB.length;
    for (var i = 0; i < n; i++) {
      if (fracA[i] != fracB[i]) return true;
    }
    return false;
  }

  /// ④ tr.40 — đoạn chung bằng nhau nhưng ĐỘ DÀI khác: quyết định được phải
  /// dùng luật số-0-tận-cùng (kể cả khi phần thừa toàn 0 — chính là lúc cần
  /// luật nhất).
  bool get unequalDecimalLength =>
      !integerPartDiffers &&
      !fractionDigitDiffers &&
      fracA.length != fracB.length;

  /// ③ tr.39 — mọi phần bằng nhau trên bề mặt.
  bool get allPartsEqual =>
      !integerPartDiffers && !fractionDigitDiffers && !unequalDecimalLength;

  /// SkillCase id theo chương trình. Bốn ca vét cạn, loại trừ nhau.
  String get skillCase => integerPartDiffers
      ? 'integer-part-differs'
      : fractionDigitDiffers
          ? 'fraction-digit-differs'
          : unequalDecimalLength
              ? 'unequal-decimal-length'
              : 'all-parts-equal';
}

/// Cổng vào duy nhất — malformed ⇒ `null`, fail closed (doctrine F2).
///
/// Nhận dạng viết SGK Việt Nam: dấu PHẨY thập phân ("37,29"). Cho phép số
/// không có phần thập phân ("38"). Mọi thứ khác (rỗng, hai dấu phẩy, ký tự
/// lạ, dấu chấm kiểu Anh-Mỹ) ⇒ không đoán.
DecimalComparisonAnalysis? analyzeDecimalComparison(String a, String b) {
  final pa = _parse(a), pb = _parse(b);
  if (pa == null || pb == null) return null;
  return DecimalComparisonAnalysis._(
      intA: pa.$1, intB: pb.$1, fracA: pa.$2, fracB: pb.$2);
}

(int, String)? _parse(String s) {
  final t = s.trim();
  if (t.isEmpty) return null;
  final parts = t.split(',');
  if (parts.length > 2) return null;
  final intPart = int.tryParse(parts[0]);
  if (intPart == null || intPart < 0) return null;
  final frac = parts.length == 2 ? parts[1] : '';
  if (parts.length == 2 && frac.isEmpty) return null;
  if (!RegExp(r'^\d*$').hasMatch(frac)) return null;
  return (intPart, frac);
}
