/// WAL-95 — LearnerProfile: ai đang học, đang ở ĐÂU trong chương trình.
///
/// ⭐ BA BẤT BIẾN của Founder Task Order §1 nằm ngay trong kiểu:
/// 1. BIRTH YEAR ≠ CURRENT GRADE — hai trường độc lập, không hàm nào suy
///    grade từ birthYear (hai trẻ cùng tuổi có thể khác lớp).
/// 2. CURRENT GRADE ≠ MASTERY — profile KHÔNG chứa mastery; chọn lớp 5 nghĩa
///    là vị trí chương trình = lớp 5, KHÔNG phải lớp 1-4 đã vững. Mastery chỉ
///    đến từ LearningEvidence (kho khác, tính khác).
/// 3. Grade phải ĐỔI ĐƯỢC — [withGrade].
///
/// Parent ≠ learner: guardianId tách khỏi learnerId; một guardian nhiều learner
/// (domain sẵn sàng multi-child; UI ship sau — đúng challenge của lệnh).
library;

class LearnerProfile {
  const LearnerProfile({
    required this.learnerId,
    required this.displayName,
    required this.grade,
    this.guardianId,
    this.birthYear,
    this.bookSeries,
  });

  final String learnerId;
  final String displayName;

  /// VỊ TRÍ chương trình hiện tại (1..12). KHÔNG phải trình độ.
  final int grade;

  /// Người giám hộ sở hữu hồ sơ này. `null` = chưa gắn (trẻ dùng một mình).
  final String? guardianId;

  /// Tuỳ chọn, và **không bao giờ** dùng để suy ra [grade].
  final int? birthYear;

  /// Bộ sách — chỉ khai khi thực sự cần cho sư phạm (method/ca theo bộ sách).
  final String? bookSeries;

  /// Đổi lớp: chuyển lớp, ở lại, hay học vượt — đều là chuyện bình thường.
  /// KHÔNG đụng tới bằng chứng: đổi vị trí chương trình không xoá/không thêm
  /// mastery nào (bất biến 2).
  LearnerProfile withGrade(int newGrade) => LearnerProfile(
        learnerId: learnerId,
        displayName: displayName,
        grade: newGrade,
        guardianId: guardianId,
        birthYear: birthYear,
        bookSeries: bookSeries,
      );

  Map<String, Object?> toJson() => {
        'learnerId': learnerId,
        'displayName': displayName,
        'grade': grade,
        if (guardianId != null) 'guardianId': guardianId,
        if (birthYear != null) 'birthYear': birthYear,
        if (bookSeries != null) 'bookSeries': bookSeries,
      };

  static LearnerProfile? fromJson(Map<String, Object?> j) {
    final id = j['learnerId'], name = j['displayName'], g = j['grade'];
    if (id is! String || name is! String || g is! int) return null;
    if (g < 1 || g > 12) return null; // lớp ngoài 1..12 ⇒ từ chối, không kẹp
    return LearnerProfile(
      learnerId: id,
      displayName: name,
      grade: g,
      guardianId: j['guardianId'] as String?,
      birthYear: j['birthYear'] as int?,
      bookSeries: j['bookSeries'] as String?,
    );
  }
}
