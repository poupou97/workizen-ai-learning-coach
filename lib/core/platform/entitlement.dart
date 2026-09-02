/// WAL-119 — ENTITLEMENT: ROLE × AGE × SUBSCRIPTION × CAPABILITY × SAFETY
/// → quyền dùng MỘT feature. MỘT resolver — không rải `if premium` khắp UI.
///
/// Bất biến (giữ bằng test + cấu trúc):
/// - ⭐ PAYMENT ≠ LEARNING TRUTH: tầng học tập (lib/core/student|adaptive|
///   curriculum|tutor) KHÔNG BIẾT subscription tồn tại — test quét import/chuỗi.
/// - ⭐ NEVER-MONETIZE: hint/answer/assessment/mastery/evidence/child-data/
///   streak KHÔNG BAO GIỜ phụ thuộc tier — resolver từ chối cả việc HỎI
///   (đó là lỗi lập trình, không phải câu hỏi kinh doanh).
/// - Consent/privacy/safety/export-delete: FREE vô điều kiện (không paywall
///   quyền của cha mẹ đối với dữ liệu con mình).
/// - Premium bán INSIGHT + COACHING + CONVENIENCE — không bán learning loop.
library;

const String entitlementPolicyVersion = 'entitlement-v1';

enum AppRole { student, parent, teacher }

enum SubscriptionTier { basicFree, premiumFamily }

/// Feature NGƯỜI LỚN/hệ thống — không phải capability học tập của trẻ.
enum ParentFeature {
  // ---- BASIC (FREE vô điều kiện — quyền, không phải quà) ----
  createSwitchLearner,
  consentPrivacy,
  safetyControls,
  exportDelete,
  basicStatus, // tình-hình-cơ-bản claim-gated (đã có WAL-109)
  // ---- PREMIUM candidates: INSIGHT ----
  dailyBrief,
  weeklyInsight,
  independentVsAssisted,
  weakestSkillCase,
  assessmentInsight,
  multiWeekTrend,
  // ---- PREMIUM candidates: COACHING ----
  tonightHelp, // «Tối nay tôi nên giúp con điều gì?»
  parentCoach,
  reviewPlan,
  proactiveRecommendation,
  // ---- PREMIUM candidates: CONVENIENCE ----
  multiChildOverview,
  cloudBackupSync,
  adFreeFamily,
}

const Set<ParentFeature> _basicFree = {
  ParentFeature.createSwitchLearner,
  ParentFeature.consentPrivacy,
  ParentFeature.safetyControls,
  ParentFeature.exportDelete,
  ParentFeature.basicStatus,
};

/// ⭐ Capability học tập KHÔNG BAO GIỜ đi qua entitlement thương mại.
/// Resolver ném [ArgumentError] nếu bị hỏi — «hỏi» đã là bug.
const Set<String> neverMonetize = {
  'hint',
  'answer',
  'assessment',
  'mastery',
  'evidence',
  'child-data',
  'streak',
  'dependence-mechanics',
};

class Entitlement {
  const Entitlement._(this.allowed, this.reason);
  const Entitlement.granted(String why) : this._(true, why);
  const Entitlement.denied(String why) : this._(false, why);
  final bool allowed;
  final String reason; // đọc được — UI nói thật vì sao
}

/// RESOLVER duy nhất. [pinVerified] = đã qua PIN khu bố mẹ (WAL-109).
Entitlement resolveEntitlement({
  required ParentFeature feature,
  required AppRole role,
  required SubscriptionTier tier,
  required bool pinVerified,
}) {
  // ROLE trước: feature phụ huynh không dành cho learner đang học.
  if (role == AppRole.student) {
    return const Entitlement.denied('ROLE: khu bố mẹ — không dành cho con');
  }
  // SAFETY: mọi feature phụ huynh nằm sau PIN (parentGated — WAL-110).
  if (!pinVerified) {
    return const Entitlement.denied('SAFETY: cần PIN khu bố mẹ');
  }
  // BASIC = quyền, FREE vô điều kiện — kể cả tier nào.
  if (_basicFree.contains(feature)) {
    return const Entitlement.granted('BASIC: quyền của phụ huynh — miễn phí');
  }
  // PREMIUM candidates — theo family-unit tier.
  return tier == SubscriptionTier.premiumFamily
      ? const Entitlement.granted('PREMIUM: gói gia đình')
      : const Entitlement.denied(
          'PREMIUM: thuộc gói gia đình — learning của con KHÔNG bị khoá');
}

/// Chặn từ GỐC việc hỏi entitlement cho capability học tập.
Never refuseLearningCapability(String capabilityId) {
  assert(neverMonetize.contains(capabilityId));
  throw ArgumentError(
      'NEVER-MONETIZE: "$capabilityId" là learning truth — không có câu hỏi '
      'entitlement thương mại nào hợp lệ ở đây (PAYMENT ≠ LEARNING TRUTH).');
}
