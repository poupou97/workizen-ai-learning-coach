/// WAL-132 — PRESENTATION LÀ TẦNG RIÊNG: cùng kiến thức, trình bày theo
/// subject × activity × grade-band × assistance × device.
///
/// Bất biến (giữ bằng test + đột biến):
/// - «KHÔNG chat bubble cho mọi thứ» (§8): tổ hợp không khớp ⇒ UNSUPPORTED
///   (nói thật), KHÔNG có surface chat để rơi về — enum này không có 'chat'.
/// - F5 «một Method một presentation» — SAI (đo WAL-67: 1 method chở 6 act):
///   binding phụ thuộc CẢ assistance level, không chỉ method/activity.
/// - Surface môn nào của môn đó: đọc-tư-liệu ngoài family SU ⇒ unsupported,
///   không mượn SourceReader cho môn khác chỉ vì «trông giống».
/// - Mọi binding mang [presentationPolicyVersion] — đổi policy không được
///   lặng lẽ đổi nghĩa trải nghiệm cũ (cùng họ policyId/knowledgeVersion).
library;

import '../student/mastery.dart';
import '../tutor/learning_activity.dart';

const String presentationPolicyVersion = 'presentation-v1';

/// Band tuổi — đúng quy ước đã đo ('1-2' · '3-5' · '6-9' · '10-12').
enum GradeBand {
  b1_2('1-2'),
  b3_5('3-5'),
  b6_9('6-9'),
  b10_12('10-12');

  const GradeBand(this.label);
  final String label;
}

/// `null` = lớp ngoài 1-12 — fail closed, không đoán band.
GradeBand? bandForGrade(int grade) => switch (grade) {
      >= 1 && <= 2 => GradeBand.b1_2,
      >= 3 && <= 5 => GradeBand.b3_5,
      >= 6 && <= 9 => GradeBand.b6_9,
      >= 10 && <= 12 => GradeBand.b10_12,
      _ => null,
    };

enum DeviceClass { phone, tablet }

/// Vocabulary surface ở TẦNG TRÌNH BÀY — cố ý KHÔNG có 'chat'.
enum PresentationSurface {
  mathWorkspace,
  quizSelect,
  reader,
  compose,
  sourceReader,
  unsupported,
}

enum PresentationFormat {
  symbolicStep, // Toán: bước + biểu thức
  readerProse, // văn xuôi đọc-hiểu
  draftRevision, // dàn ý → nháp → sửa
  sourceEvidence, // nguồn/diễn giải/kết luận
  choiceChips, // lựa chọn chạm
  unsupported,
}

/// Chi tiết trình bày — NƠI F5 hiện hình: cùng surface, assistance khác ⇒
/// chi tiết khác (worked-region chỉ mở từ workedStep trở lên).
class PresentationDetail {
  const PresentationDetail({
    required this.textScale,
    required this.showWorkedRegion,
    required this.twoPane,
  });

  final double textScale;
  final bool showWorkedRegion;
  final bool twoPane;
}

class PresentationBinding {
  const PresentationBinding(
      {required this.surface,
      required this.format,
      required this.detail,
      this.version = presentationPolicyVersion});

  final PresentationSurface surface;
  final PresentationFormat format;
  final PresentationDetail detail;
  final String version;

  bool get supported => surface != PresentationSurface.unsupported;
}

/// Band 1-2 đọc chữ to hơn (AGE-ADAPTIVE: band 1-2 là pass riêng) — các band
/// khác giữ 1.0 cho tới khi có đo lường riêng (không bịa hệ số).
double textScaleFor(GradeBand band) =>
    band == GradeBand.b1_2 ? 1.3 : 1.0;

/// RESOLVER duy nhất của tầng trình bày.
///
/// [sourceExcerpt] = hoạt động ĐỌC TƯ LIỆU (không phải một [ResponseKind]
/// của bài tập — verdict WAL-113 B3: không thêm kind giả để gom cho đẹp).
PresentationBinding resolvePresentation({
  required String subjectFamily, // TOAN · TV-VAN · SU · KHOA · NN · KHAC
  ResponseKind? response,
  bool sourceExcerpt = false,
  required GradeBand band,
  required SupportLevel assistance,
  DeviceClass device = DeviceClass.phone,
}) {
  final detail = PresentationDetail(
    textScale: textScaleFor(band),
    // ⭐ F5: assistance là MỘT CHIỀU của trình bày — không phải 1 method 1 hình.
    showWorkedRegion: assistance.index >= SupportLevel.workedStep.index,
    twoPane: device == DeviceClass.tablet,
  );
  PresentationBinding bind(PresentationSurface s, PresentationFormat f) =>
      PresentationBinding(surface: s, format: f, detail: detail);

  if (sourceExcerpt) {
    // Surface môn nào của môn đó — tư liệu ngoài SU không mượn SourceReader.
    return subjectFamily == 'SU'
        ? bind(PresentationSurface.sourceReader,
            PresentationFormat.sourceEvidence)
        : bind(PresentationSurface.unsupported, PresentationFormat.unsupported);
  }
  return switch (response) {
    ResponseKind.numericStep when subjectFamily == 'TOAN' => bind(
        PresentationSurface.mathWorkspace, PresentationFormat.symbolicStep),
    ResponseKind.readRespond =>
      bind(PresentationSurface.reader, PresentationFormat.readerProse),
    ResponseKind.compose =>
      bind(PresentationSurface.compose, PresentationFormat.draftRevision),
    ResponseKind.selectIdentify =>
      bind(PresentationSurface.quizSelect, PresentationFormat.choiceChips),
    // shortText / numericStep-ngoài-Toán / null ⇒ nói thật KHÔNG HỖ TRỢ —
    // tuyệt đối không rơi về một «màn chat» nào (bất biến §8).
    _ => bind(PresentationSurface.unsupported, PresentationFormat.unsupported),
  };
}
