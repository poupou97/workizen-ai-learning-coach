/// WAL-110 §6 — EDUCATION SAFETY POLICY: ranh giới Hub capability → SAM,
/// LÀ CODE chứ không phải bảng trong tài liệu.
///
/// WORKIZEN SHARED CAPABILITIES → EDUCATION SAFETY ADAPTER → SAM DOMAIN.
/// Bảng dưới là phiên bản thi hành của HUB-TO-SAM-CAPABILITY-REUSE-MATRIX
/// (31 capability, audit repo Hub thật). Đổi quyết định = đổi CODE = qua test.
///
/// 5 luật ≠ (đều có chỗ enforce cụ thể, không lời hứa):
/// - OCR ≠ LearningEvidence      → EducationOcrAdapter chỉ sinh hypothesis (WAL-108, type-enforced)
/// - Generic Chat ≠ SAM Tutor    → [CapabilityDecision.disable] + không dep/feature chat nào
/// - AI Provider ≠ authority     → realization_contract (ACT_OVER_RUNG + cage + guard)
/// - Imported Doc ≠ curriculum   → KnowledgeContentProvider.license bắt buộc khai
/// - Analytics ≠ child telemetry → [forbiddenDependencies] + test quét pubspec
library;

/// Quyết định cho MỘT capability khi vào ngữ cảnh giáo dục.
enum CapabilityDecision {
  /// Dùng nguyên — không rủi ro trẻ em riêng.
  allow,

  /// Chỉ sau ranh giới an toàn/kiểu dữ liệu riêng (vd OCR→hypothesis).
  sanitize,

  /// Theo band tuổi (vd TTS speech-rate, canvas density).
  ageGated,

  /// Chỉ trong Parent Mode sau PIN (vd subscription, backup restore).
  parentGated,

  /// KHÔNG vào SAM — phản triết lý hoặc thừa.
  disable,
}

/// Bảng thi hành — capability id khớp matrix. Thiếu id ⇒ [disable]
/// (fail closed: chưa quyết = chưa vào).
const Map<String, CapabilityDecision> educationCapabilityPolicy = {
  // Perception
  'ocr': CapabilityDecision.sanitize, // hypothesis-only, WAL-108
  'doc-scanner': CapabilityDecision.allow,
  'camera': CapabilityDecision.sanitize, // bind activeLearner + pre-capture
  'qr': CapabilityDecision.sanitize, // SCAN ≠ AUTHORIZATION (purpose/nonce)
  // Voice
  'stt': CapabilityDecision.ageGated, // child-voice policy, không cloud mặc định
  'tts': CapabilityDecision.ageGated, // speech-rate theo band
  // AI
  'ai-router': CapabilityDecision.sanitize, // routing không quyết pedagogy
  'ai-usage': CapabilityDecision.parentGated, // trẻ không thấy token
  'chat-generic': CapabilityDecision.disable, // F34 — tutor không phải chat
  'ollama-local': CapabilityDecision.sanitize,
  // Content
  'smart-canvas': CapabilityDecision.ageGated,
  'smart-tools': CapabilityDecision.ageGated, // output = learner artifact
  'doc-ingestion': CapabilityDecision.sanitize, // nhãn nguồn bắt buộc
  'library': CapabilityDecision.sanitize, // SAM knowledge ≠ user files
  // Platform
  'auth': CapabilityDecision.parentGated, // account ≠ learner
  'backup-restore': CapabilityDecision.parentGated, // không merge learner A/B
  'secure-storage': CapabilityDecision.allow,
  'subscription': CapabilityDecision.parentGated, // PAYMENT ≠ LEARNING TRUTH
  'notifications': CapabilityDecision.sanitize, // learning-only, không streak-spam
  'permissions': CapabilityDecision.allow,
  'l10n': CapabilityDecision.allow,
  'design-tokens': CapabilityDecision.allow,
  'mascot': CapabilityDecision.ageGated,
  'deep-links': CapabilityDecision.sanitize,
  'voice-ui': CapabilityDecision.ageGated, // không bypass TutorScope
  'analytics': CapabilityDecision.disable, // child privacy pass TRƯỚC (F42)
  // Phản triết lý — vĩnh viễn trừ khi Founder đổi doctrine
  'leaderboard': CapabilityDecision.disable,
  'arcade-gamification': CapabilityDecision.disable,
  'ads': CapabilityDecision.disable, // ads TRONG APP TRẺ = Founder Gate WAL-125
  'growth-engagement': CapabilityDecision.disable,
  'hub-learning-state': CapabilityDecision.disable, // tránh 2 nguồn «mastery»
};

/// Tra quyết định — id lạ trả [CapabilityDecision.disable], KHÔNG null:
/// một capability chưa audit mà lọt vào là lỗ hổng, không phải ngoại lệ.
CapabilityDecision decisionFor(String capabilityId) =>
    educationCapabilityPolicy[capabilityId] ?? CapabilityDecision.disable;

/// Dependency BỊ CẤM trong app trẻ em (enforce bằng test quét pubspec):
/// ad SDK, analytics hành vi, tracking. Thêm vào đây = qua review Founder Gate.
const List<String> forbiddenDependencies = [
  'google_mobile_ads',
  'applovin',
  'unity_ads',
  'ironsource',
  'firebase_analytics',
  'firebase_crashlytics', // crash data có thể chứa ngữ cảnh trẻ — chưa qua F42
  'amplitude',
  'mixpanel',
  'appsflyer',
  'adjust',
  'facebook_app_events',
];
