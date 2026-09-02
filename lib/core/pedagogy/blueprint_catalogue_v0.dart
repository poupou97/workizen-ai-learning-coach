/// WAL-129 — CATALOGUE v0: 8 blueprint mẫu, 5 subject family, TỪ NGUỒN THẬT.
///
/// Mỗi blueprint trỏ về đúng (SGV, trang, bài) đã mine (WAL-127/129);
/// sequence lấy từ pattern ĐO ĐƯỢC của family/bài đó — KHÔNG một khuôn chung
/// (F2/F3). Trường nguồn không nói (phút, misconception) thì để trống.
library;

import '../student/learning_evidence.dart';
import 'learning_blueprint.dart';
import 'pedagogical_pattern.dart';
import 'pedagogy_model.dart';

/// ⭐ Blueprint đầu tiên — DRIVE ĐƯỢC TutorSession thật của WAL-108.
/// Nguồn: 05-sgv-toan-5 p36 (Bài 6, 2 tiết): «Khởi động → hình thức phù hợp
/// → Củng cố»; Khám phá/Hình thành kiến thức mới; Vận dụng; Tiết 2 Luyện tập.
const blueprintQuyDongB6 = LearningExperienceBlueprint(
  blueprintId: 'bp:toan5:b6:quy-dong-khac-mau',
  subject: 'Toán',
  grade: 5,
  lessonId: 'toan5-t1-bai6',
  conceptIds: ['quy-dong'],
  skillCaseIds: ['denominator-non-divisible', 'denominator-divisible'],
  methodIds: ['common-denom-by-product', 'common-denom-take-larger'],
  sequence: [
    PatternStep(intent: PedagogicalIntent.activate, allowedActs: [
      TeachingAct.pumpRecall, // gợi lại ca chia-hết lớp 4
      TeachingAct.contrastCases,
    ]),
    PatternStep(intent: PedagogicalIntent.discover, allowedActs: [
      TeachingAct.diagnosticProbe,
      TeachingAct.demonstrateStep, // SGV dạy qua ví dụ (sourceDemonstrated)
      TeachingAct.askExplanation,
    ]),
    PatternStep(intent: PedagogicalIntent.practice, allowedActs: [
      TeachingAct.observeWait, // trẻ THỬ TRƯỚC — WAL-86
      TeachingAct.smallHint,
      TeachingAct.strategicHint,
      TeachingAct.stepBack, // YOUR_TURN
    ]),
    PatternStep(intent: PedagogicalIntent.apply, allowedActs: [
      TeachingAct.workedExample,
      TeachingAct.askVerification,
    ]),
    PatternStep(intent: PedagogicalIntent.consolidate, allowedActs: [
      TeachingAct.reflect,
      TeachingAct.revealStep,
      TeachingAct.revealAnswer, // chỉ sau tự thử — REVEAL gate của session
    ]),
  ],
  assistanceCap: AssistanceRung.workedSolution, // practice tự học: thang đủ
  evidenceRequired: [EvidenceKind.independentAttempt],
  transferRequired: true, // WAL-103: cùng-template không đủ tuyên mastery
  source: PedagogySource(
    authority: PedagogyAuthority.sourceExplicit,
    extractionMethod: 'sgv-pedagogy-v1',
    sourceDocumentId: '05-sgv-toan-5',
    page: 36,
    lesson: 6,
  ),
);

/// Toán 6 — số nguyên, bỏ ngoặc dấu trừ; có misconception nguồn cảnh báo.
const blueprintSoNguyenB15 = LearningExperienceBlueprint(
  blueprintId: 'bp:toan6:b15:bo-ngoac-so-nguyen',
  subject: 'Toán',
  grade: 6,
  lessonId: 'toan6-b15',
  conceptIds: ['so-nguyen-cong-tru'],
  skillCaseIds: ['bo-ngoac-dau-tru'],
  methodIds: [],
  sequence: [
    // Pattern THCS đo được p22: PRACTICE(5p)→APPLY(5p)→DISCOVER(7p)→…
    PatternStep(
        intent: PedagogicalIntent.practice,
        minutes: 5,
        allowedActs: [TeachingAct.observeWait, TeachingAct.smallHint]),
    PatternStep(
        intent: PedagogicalIntent.discover,
        minutes: 7,
        allowedActs: [TeachingAct.diagnosticProbe, TeachingAct.contrastCases]),
    PatternStep(
        intent: PedagogicalIntent.apply,
        minutes: 5,
        allowedActs: [TeachingAct.askVerification]),
  ],
  assistanceCap: AssistanceRung.demonstration,
  evidenceRequired: [EvidenceKind.independentAttempt],
  misconceptionIds: ['mis:toan6:bo-ngoac-dau-tru'],
  source: PedagogySource(
    authority: PedagogyAuthority.sourceExplicit,
    extractionMethod: 'sgv-pedagogy-v1',
    sourceDocumentId: '06-sgv-toan-6',
    page: 84,
    lesson: 15,
  ),
);

/// TV lớp 1 — âm/vần: chuỗi ACTIVATE→CONSOLIDATE đo được ×20.
const blueprintTv1AmVan = LearningExperienceBlueprint(
  blueprintId: 'bp:tv1:am-van',
  subject: 'Tiếng Việt',
  grade: 1,
  lessonId: 'tv1-am-van',
  conceptIds: ['am-van'],
  skillCaseIds: ['doc-am-de-lan'],
  methodIds: [],
  sequence: [
    PatternStep(intent: PedagogicalIntent.activate, allowedActs: [
      TeachingAct.pumpRecall,
    ]),
    PatternStep(intent: PedagogicalIntent.consolidate, allowedActs: [
      TeachingAct.observeWait,
      TeachingAct.smallHint,
      TeachingAct.reflect,
    ]),
  ],
  // Band 1-2 + đọc thành tiếng: không có «lời giải» để reveal — trần thấp.
  assistanceCap: AssistanceRung.demonstration,
  evidenceRequired: [EvidenceKind.independentAttempt],
  misconceptionIds: ['mis:tv1:phu-am-vung-mien'],
  source: PedagogySource(
    authority: PedagogyAuthority.sourceExplicit,
    extractionMethod: 'sgv-pedagogy-v1',
    sourceDocumentId: '01-sgv-tieng-viet-1-tap-mot',
    page: 44,
    lesson: 5,
  ),
);

/// TV lớp 3 — đọc hiểu (Reader surface WAL-98 đã có; recognize≠explain≠apply).
const blueprintTv3DocHieu = LearningExperienceBlueprint(
  blueprintId: 'bp:tv3:doc-hieu',
  subject: 'Tiếng Việt',
  grade: 3,
  lessonId: 'tv3-doc-hieu',
  conceptIds: ['doc-hieu'],
  skillCaseIds: ['doc-hieu-tra-loi'],
  methodIds: [],
  sequence: [
    PatternStep(intent: PedagogicalIntent.activate, allowedActs: [
      TeachingAct.pumpRecall,
    ]),
    PatternStep(intent: PedagogicalIntent.practice, allowedActs: [
      TeachingAct.observeWait,
      TeachingAct.diagnosticProbe,
      TeachingAct.askExplanation, // giải thích ≠ nhận diện
    ]),
  ],
  // SAM không đọc hộ đáp án bài đọc-hiểu — trần dừng ở scaffold.
  assistanceCap: AssistanceRung.partialScaffold,
  evidenceRequired: [EvidenceKind.independentAttempt],
  source: PedagogySource(
    authority: PedagogyAuthority.sourceExplicit,
    extractionMethod: 'sgv-pedagogy-v1',
    sourceDocumentId: '03-sgv-tieng-viet-3-tap-hai',
    page: 114,
    lesson: 15,
  ),
);

/// Sử 10 — làm việc với sử liệu: DISCOVER→APPLY đo được ×5.
/// NGUỒN NÓI GÌ ≠ SAM DIỄN GIẢI ≠ HS KẾT LUẬN → acts giữ ranh giới đó.
const blueprintSu10SuLieu = LearningExperienceBlueprint(
  blueprintId: 'bp:su10:su-lieu',
  subject: 'Lịch sử',
  grade: 10,
  lessonId: 'su10-su-lieu',
  conceptIds: ['su-dung-su-lieu'],
  skillCaseIds: ['doc-su-lieu-ket-luan'],
  methodIds: [],
  sequence: [
    PatternStep(intent: PedagogicalIntent.discover, allowedActs: [
      TeachingAct.observeWait, // HS đọc nguồn trước
      TeachingAct.diagnosticProbe, // hỏi HS thấy gì TRONG nguồn
    ]),
    PatternStep(intent: PedagogicalIntent.apply, allowedActs: [
      TeachingAct.askExplanation, // HS lập luận từ evidence
      TeachingAct.askVerification, // đối chiếu nguồn khác
      TeachingAct.contrastCases,
    ]),
  ],
  // Sử: SAM không «giải hộ» kết luận — không reveal.
  assistanceCap: AssistanceRung.strategicHint,
  learnerFirst: true, // trẻ quan sát/đọc nguồn TRƯỚC
  evidenceRequired: [EvidenceKind.independentAttempt],
  source: PedagogySource(
    authority: PedagogyAuthority.sourceExplicit,
    extractionMethod: 'sgv-pedagogy-v1',
    sourceDocumentId: '10-sgv-lich-su-10',
    page: 44,
    lesson: 3,
  ),
);

/// Khoa học 4 — quan sát trước, kết luận sau (YCCĐ 32 mục đo được).
const blueprintKhoa4QuanSat = LearningExperienceBlueprint(
  blueprintId: 'bp:khoa4:quan-sat',
  subject: 'Khoa học',
  grade: 4,
  lessonId: 'khoa4-quan-sat',
  conceptIds: ['quan-sat-khoa-hoc'],
  skillCaseIds: ['quan-sat-ghi-nhan'],
  methodIds: [],
  sequence: [
    PatternStep(intent: PedagogicalIntent.discover, allowedActs: [
      TeachingAct.observeWait, // learner observation ≠ source fact
      TeachingAct.diagnosticProbe,
    ]),
    PatternStep(intent: PedagogicalIntent.apply, allowedActs: [
      TeachingAct.askExplanation,
      TeachingAct.askVerification,
    ]),
    PatternStep(intent: PedagogicalIntent.reflect, allowedActs: [
      TeachingAct.reflect,
    ]),
  ],
  assistanceCap: AssistanceRung.partialScaffold,
  learnerFirst: true, // trẻ quan sát/đọc nguồn TRƯỚC
  evidenceRequired: [EvidenceKind.independentAttempt],
  source: PedagogySource(
    authority: PedagogyAuthority.sourceExplicit,
    extractionMethod: 'sgv-pedagogy-v1',
    sourceDocumentId: '04-sgv-khoa-hoc-4',
    page: 7,
    lesson: 31,
  ),
);

/// Tiếng Anh 3 — LISTENING theo Goal-block Global Success (385 hoạt động nghe
/// đo được). Listening ≠ Reading-with-audio: act không lộ transcript trước.
const blueprintNn3Listening = LearningExperienceBlueprint(
  blueprintId: 'bp:nn3:listening',
  subject: 'Tiếng Anh',
  grade: 3,
  lessonId: 'nn3-listening',
  conceptIds: ['en-listening'],
  skillCaseIds: ['listen-and-tick'],
  methodIds: [],
  sequence: [
    PatternStep(intent: PedagogicalIntent.activate, allowedActs: [
      TeachingAct.pumpRecall, // Warm-up từ vựng
    ]),
    PatternStep(intent: PedagogicalIntent.practice, allowedActs: [
      TeachingAct.observeWait, // nghe lần 1 không trợ giúp
      TeachingAct.smallHint, // nghe lại đoạn — hint là REPLAY, không transcript
    ]),
    PatternStep(intent: PedagogicalIntent.review, allowedActs: [
      TeachingAct.askVerification,
    ]),
  ],
  assistanceCap: AssistanceRung.demonstration, // demo = phát lại chậm
  evidenceRequired: [EvidenceKind.independentAttempt],
  source: PedagogySource(
    authority: PedagogyAuthority.sourceExplicit,
    extractionMethod: 'sgv-pedagogy-en-v1',
    sourceDocumentId: '03-sgv-tieng-anh-3-global-success',
    page: 8,
    lesson: 1,
  ),
);

/// Toán 3 — chu vi (misconception chu-vi/diện-tích p190 gắn thẳng).
const blueprintToan3ChuVi = LearningExperienceBlueprint(
  blueprintId: 'bp:toan3:chu-vi',
  subject: 'Toán',
  grade: 3,
  lessonId: 'toan3-chu-vi',
  conceptIds: ['chu-vi'],
  skillCaseIds: ['chu-vi-hinh-chu-nhat'],
  methodIds: [],
  sequence: [
    PatternStep(intent: PedagogicalIntent.activate, allowedActs: [
      TeachingAct.contrastCases, // chu vi VS diện tích — đúng cảnh báo SGV
    ]),
    PatternStep(intent: PedagogicalIntent.discover, allowedActs: [
      TeachingAct.demonstrateStep,
      TeachingAct.askExplanation,
    ]),
    PatternStep(intent: PedagogicalIntent.practice, allowedActs: [
      TeachingAct.observeWait,
      TeachingAct.smallHint,
    ]),
  ],
  assistanceCap: AssistanceRung.workedSolution,
  evidenceRequired: [EvidenceKind.independentAttempt],
  misconceptionIds: ['mis:toan3:chu-vi-hcn-3x-hv'],
  source: PedagogySource(
    authority: PedagogyAuthority.sourceExplicit,
    extractionMethod: 'sgv-pedagogy-v1',
    sourceDocumentId: '03-sgv-toan-3',
    page: 190,
    lesson: 3,
  ),
);

/// Toàn bộ catalogue v0 — 8 blueprint, 5 family.
const blueprintCatalogueV0 = [
  blueprintQuyDongB6,
  blueprintSoNguyenB15,
  blueprintTv1AmVan,
  blueprintTv3DocHieu,
  blueprintSu10SuLieu,
  blueprintKhoa4QuanSat,
  blueprintNn3Listening,
  blueprintToan3ChuVi,
];
