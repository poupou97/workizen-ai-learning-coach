/// WAL-128 §18 — misconception TỪ NGUỒN (SGV nói thẳng «HS hay sai…»).
///
/// TÁCH BẠCH với [ErrorHypothesis] (WAL-27 — runtime, học từ log):
/// - SourceMisconception: thẩm quyền NGUỒN, tồn tại TRƯỚC khi có learner nào;
/// - ErrorHypothesis: giả thuyết lúc chạy, proposed→confirmed qua probe.
/// Một hypothesis CÓ THỂ trích dẫn một SourceMisconception làm prior —
/// nhưng không chiều ngược: nguồn không bao giờ tự thành «đã xác nhận trên
/// trẻ này». KHÔNG có import nào từ file này sang mastery/evidence — kiểm
/// soát bằng cấu trúc, như WAL-27.
///
/// KHÔNG invent: seed dưới đây là 4 mục ĐƯỢC GIÁM TUYỂN từ 39 candidate đo
/// được (WAL-127 §5); observablePattern là DIỄN ĐẠT LẠI (paraphrase), nguyên
/// văn nằm trong poc-out (localResearchOnly — WAL-43).
library;

import 'pedagogical_pattern.dart';
import 'pedagogy_model.dart';

class SourceMisconception {
  const SourceMisconception({
    required this.id,
    required this.subject,
    required this.grade,
    required this.observablePattern,
    required this.source,
    this.skillCaseId,
    this.diagnosticProbeHint,
    this.version = pedagogyModelVersion,
  });

  final String id;
  final String subject;
  final int grade;

  /// Trẻ làm gì thì NGHI mắc lỗi này — mô tả quan sát được, không chẩn đoán.
  final String observablePattern;

  final PedagogySource source;

  /// `null` = nguồn nói theo bài, chưa map được về ca — GIỮ NGUYÊN UNKNOWN.
  final String? skillCaseId;

  /// Gợi ý probe NẾU nguồn gợi (SGV thường có). `null` = nguồn không nói.
  final String? diagnosticProbeHint;

  final String version;
}

/// Seed v0 — 4 misconception THẬT có (doc, trang, bài) từ sample WAL-127.
const sourceMisconceptionSeedV0 = [
  SourceMisconception(
    id: 'mis:toan3:chu-vi-hcn-3x-hv',
    subject: 'Toán',
    grade: 3,
    observablePattern:
        'Tính chu vi hình chữ nhật bằng 3 lần chu vi một hình vuông; '
        'lẫn chu vi với diện tích khi làm bài.',
    diagnosticProbeHint: 'Phân biệt lại chu vi và diện tích trước khi làm.',
    source: PedagogySource(
      authority: PedagogyAuthority.sourceExplicit,
      extractionMethod: 'sgv-pedagogy-v1',
      sourceDocumentId: '03-sgv-toan-3',
      page: 190,
      lesson: 3,
    ),
  ),
  SourceMisconception(
    id: 'mis:toan3:dem-canh-hinh',
    subject: 'Toán',
    grade: 3,
    observablePattern: 'Đếm sót/đếm trùng khi đếm cạnh của hình.',
    source: PedagogySource(
      authority: PedagogyAuthority.sourceExplicit,
      extractionMethod: 'sgv-pedagogy-v1',
      sourceDocumentId: '03-sgv-toan-3',
      page: 84,
      lesson: 21,
    ),
  ),
  SourceMisconception(
    id: 'mis:toan6:bo-ngoac-dau-tru',
    subject: 'Toán',
    grade: 6,
    observablePattern:
        'Sai dấu khi bỏ dấu ngoặc có dấu trừ đằng trước, nhất là với số âm; '
        'sai dấu lặp lại ở phép nhân/chia số nguyên.',
    source: PedagogySource(
      authority: PedagogyAuthority.sourceExplicit,
      extractionMethod: 'sgv-pedagogy-v1',
      sourceDocumentId: '06-sgv-toan-6',
      page: 84,
      lesson: 15,
    ),
  ),
  SourceMisconception(
    id: 'mis:tv1:phu-am-vung-mien',
    subject: 'Tiếng Việt',
    grade: 1,
    observablePattern:
        'Lẫn phụ âm theo vùng miền khi đọc/viết: l–n (Bắc), v–d (Nam), x–s.',
    source: PedagogySource(
      authority: PedagogyAuthority.sourceExplicit,
      extractionMethod: 'sgv-pedagogy-v1',
      sourceDocumentId: '01-sgv-tieng-viet-1-tap-mot',
      page: 110,
      lesson: 27,
    ),
  ),
];
