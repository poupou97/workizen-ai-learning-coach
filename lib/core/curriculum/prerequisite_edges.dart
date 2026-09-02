/// WAL-18 — Cạnh prerequisite CÓ NGUỒN: kết quả khai thác corpus thật.
///
/// KẾT LUẬN ĐO ĐƯỢC (2026-09-02, quét 4 SGK Toán 4-5 + SGV Toán 5, ~700
/// trang OCR): sách hầu như KHÔNG «nói thẳng» quan hệ tiên quyết — 7 hit
/// mẫu «đã học/đã biết/dựa vào cách», trong đó đúng MỘT quan hệ
/// concept→concept rõ ràng. Hệ quả doctrine (giữ nguyên CurriculumEdge):
/// đại đa số cạnh prerequisite sẽ mãi là suy luận (llmInferred/systemDerived,
/// KHÔNG citable-as-dependency); đường nâng nguồn chính là `sourceOrder` +
/// sourceSequence — nói «sách xếp trước» chứ không nói «sách bảo cần».
library;

import '../knowledge/provenance.dart';
import 'curriculum_edge.dart';

/// Cạnh prerequisite sourceStated ĐẦU TIÊN của SAM — sách nói thẳng:
/// SGK Toán 5 KNTT tập hai, Bài 53, tr.54: nhân vật mở bài «Mình đã biết
/// cách tính thể tích của hình hộp chữ nhật, còn thể tích [hình lập
/// phương]…» — quan hệ dựa-trên được PHÁT BIỂU trong sách, không phải ta
/// suy từ thứ tự mục lục.
const prerequisiteEdges = [
  CurriculumEdge(
    from: 'the-tich-hinh-hop-chu-nhat',
    to: 'the-tich-hinh-lap-phuong',
    kind: EdgeKind.prerequisite,
    provenance: Provenance(
      origin: KnowledgeOrigin.sourceStated,
      sourceId: '05-sgk-toan-5-tap-hai',
      extractionMethod: 'manual', // đọc tay từ OCR, đối chiếu trang gốc
      confidence: 0.9,
      bookSeries: 'KNTT',
      grade: 5,
      subject: 'Toán',
      pageStart: 54,
    ),
    evidence: 'Bài 53 mở đầu: «Mình đã biết cách tính thể tích của hình hộp '
        'chữ nhật, còn thể tích [của hình lập phương]…» — dạy LP dựa trên HHCN.',
  ),
];

/// Ứng viên CHƯA mint — ghi lại để không mất, và để không đoán:
/// SGV Toán 5 p026: dạng bài «Tính» của Bài 5 «dựa vào cách rút gọn phân
/// số» — nguồn nói thẳng nhưng ĐÍCH của cạnh không phải một concept rõ
/// (một dạng bài trong bài ôn tập). Unknown đích ⇒ không tạo cạnh.
const prerequisiteCandidatesNote =
    'sgv-toan-5 p026: rut-gon-phan-so → (dạng bài Tính, Bài 5 ôn tập) — '
    'đích chưa quy được về concept; giữ candidate, không mint.';
