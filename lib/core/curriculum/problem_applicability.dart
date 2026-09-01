/// ⭐⭐ F2 — APPLICABLE_TO_PROBLEM: mô hình hoá ĐÚNG ca toán học, không phải
/// một phép chia lấy dư.
///
/// Founder decision (2026-09-01): *"`3/5 + 1/5` must not enter a
/// denominator-conversion SkillCase merely because divisibility arithmetic
/// returns true. Problem applicability must model the mathematical case
/// correctly."*
///
/// Lỗi gốc F2: `5 % 5 == 0` ⇒ ca "chia hết" ⇒ Tutor nhận phương pháp quy đồng
/// cho một bài KHÔNG CÓ bước quy đồng. Bản vá đầu thêm nhánh `d1 == d2` —
/// đúng, nhưng vẫn là if-else trên số dư. Tệp này thay bằng một PHÂN TÍCH đầy
/// đủ của cặp mẫu số, để mọi kết luận downstream truy vết được về cấu trúc
/// toán học thật, và để ca mới (coprime vs non-coprime) TÁCH ĐƯỢC về sau mà
/// không đổi schema.
library;

/// Phân tích TẤT ĐỊNH một cặp mẫu số. Mọi trường suy từ số học, không LLM.
class FractionPairAnalysis {
  const FractionPairAnalysis._({
    required this.d1,
    required this.d2,
    required this.gcd,
    required this.lcm,
    required this.product,
  });

  final int d1;
  final int d2;
  final int gcd;
  final int lcm;
  final int product;

  /// Bốn ca biên Founder liệt kê — VÉT CẠN và LOẠI TRỪ NHAU:
  /// equal → oneDividesOther → coprime → nonCoprimeNonDivisible.
  bool get equal => d1 == d2;

  /// Một mẫu chia hết cho mẫu kia (và KHÔNG bằng nhau — `equal` đã tách
  /// trước; đây chính là chỗ bản cũ trượt).
  bool get oneDividesOther => !equal && (d1 % d2 == 0 || d2 % d1 == 0);

  /// Nguyên tố cùng nhau ⇒ tích hai mẫu CHÍNH LÀ mẫu chung nhỏ nhất.
  bool get coprime => !equal && !oneDividesOther && gcd == 1;

  /// ⭐ Không chia hết cho nhau NHƯNG có ước chung (vd 4 và 6): phương pháp
  /// sách dạy ("lấy tích") vẫn ĐÚNG, nhưng tích KHÔNG phải mẫu chung nhỏ
  /// nhất (24 ≠ 12). Toán học phân biệt được hai ca này dù sách lớp 5 dạy
  /// chung một phương pháp — giữ lại phân biệt để:
  ///   ① trình chấm KHÔNG đánh sai một đứa trẻ quy đồng ra 12;
  ///   ② khi corpus lớp trên tách ca (BCNN), ca này tách theo, không đổi schema.
  bool get nonCoprimeNonDivisible =>
      !equal && !oneDividesOther && gcd > 1;

  /// Tích hai mẫu có VƯỢT mẫu chung nhỏ nhất không — cờ của ①② ở trên.
  bool get productExceedsLcm => product > lcm;

  /// ⭐ Ánh xạ về SkillCase THEO CHƯƠNG TRÌNH (KNTT, đo từ corpus):
  ///
  /// | Ca toán học            | SkillCase                     | Dạy ở |
  /// |---|---|---|
  /// | bằng nhau              | `denominator-equal`           | trước quy đồng |
  /// | chia hết               | `denominator-divisible`       | lớp 4, Bài 57 |
  /// | coprime                | `denominator-non-divisible`   | lớp 5, Bài 6 |
  /// | non-coprime non-div    | `denominator-non-divisible`   | lớp 5, Bài 6 |
  ///
  /// Hai ca cuối GỘP ở tầng SkillCase vì sách lớp 5 dạy chung một phương
  /// pháp — gộp là sự thật SƯ PHẠM (có nguồn), còn phân biệt toán học vẫn
  /// nằm nguyên trong analysis này.
  String get skillCase => equal
      ? 'denominator-equal'
      : oneDividesOther
          ? 'denominator-divisible'
          : 'denominator-non-divisible';
}

/// ⭐ Cổng vào DUY NHẤT — mọi input xấu chết ở đây, trả `null`, KHÔNG đoán.
///
/// Founder: *"Unknown remains fail closed."* `null` chảy xuống
/// `TutorScope.forProblem` thành tập phương pháp RỖNG (chốt đã có test).
FractionPairAnalysis? analyzeFractionPair(int? d1, int? d2) {
  if (d1 == null || d2 == null) return null;
  if (d1 <= 0 || d2 <= 0) return null;
  final g = _gcd(d1, d2);
  return FractionPairAnalysis._(
    d1: d1,
    d2: d2,
    gcd: g,
    lcm: d1 ~/ g * d2,
    product: d1 * d2,
  );
}

int _gcd(int a, int b) => b == 0 ? a : _gcd(b, a % b);
