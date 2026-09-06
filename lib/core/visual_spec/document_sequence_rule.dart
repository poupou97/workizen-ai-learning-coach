/// ⭐ LANE E2 (round 5) §19 — LUẬT `numbered-section-sequence-v1` (**PROPOSED,
/// có biên**): các mục ĐÁNH SỐ của một bài, theo đúng thứ tự sách in.
///
/// Vì sao luật này tồn tại trong làn E2: để chứng minh §19 cần MỘT renderer
/// chạy trên HAI môn khác nhau, mà tầng ngữ nghĩa hôm nay chỉ sinh dữ liệu
/// cho KHTN (`tsl-enumerated-steps-v1`) và một bài Lịch sử. Luật này lấy thứ
/// đã có sẵn trong tài liệu — tiêu đề mục và con số sách IN ra — nên nó là
/// **quan sát**, không phải suy diễn nội dung.
///
/// GIỚI HẠN, nói trước khi ai hỏi:
/// - Nó KHÔNG khẳng định «phải làm theo thứ tự này». Vì thế họ hình là
///   `sequence` («sách in các phần theo thứ tự này»), KHÔNG phải `process`.
/// - Nó có DƯƠNG TÍNH GIẢ đã đo được: trong sách GIÁO VIÊN, «1. KIẾN THỨC /
///   2. KĨ NĂNG / 3. PHẨM CHẤT» là danh mục năng lực, không phải một chuỗi.
///   Số đo nằm trong `docs/research/semantic-graph/VISUAL-SPEC-GENERALISATION.md`.
/// - Nhà đúng của luật này là TẦNG NGỮ NGHĨA (làn E1/A/C), không phải tầng
///   hình. Nó ở đây để chứng minh hợp đồng renderer, KHÔNG được đăng ký vào
///   đường sinh pack sản xuất.
library;

import '../lesson_model/content_trust.dart';
import '../lesson_model/lesson_document.dart';
import 'visual_spec.dart';

const String numberedSectionSequenceRule = 'numbered-section-sequence-v1';

/// «1. Dụng cụ thí nghiệm» · «1 TRƯỚC KHI NÓI» · «2) Tìm hiểu…»
/// Bắt buộc có CHỮ sau con số ⇒ số trang / số đơn lẻ không lọt vào.
final RegExp _numberedHeading = RegExp(r'^\s*(\d{1,2})\s*[.)]?\s+(\S.*)$');

/// Một mục đánh số đã nhận ra.
class NumberedSection {
  const NumberedSection({
    required this.number,
    required this.text,
    required this.blockId,
    required this.trust,
  });
  final int number;
  final String text;
  final String blockId;
  final ContentTrust trust;
}

/// Dãy mục đánh số DÀI NHẤT bắt đầu từ 1 và tăng đều 1, theo thứ tự đọc.
///
/// Bắt đầu-từ-1-và-liền-mạch là điều kiện cố ý chặt: nó loại các trang chỉ
/// mang một mảnh của dãy (trang tiếp theo của bài) và các con số rời rạc.
List<NumberedSection> numberedRunOf(LessonDocument doc) {
  final found = <NumberedSection>[];
  for (final b in doc.blocks) {
    if (b is! HeadingBlock) continue;
    final m = _numberedHeading.firstMatch(b.text);
    if (m == null) continue;
    found.add(
      NumberedSection(
        number: int.parse(m.group(1)!),
        text: b.text.trim(),
        blockId: b.id,
        trust: b.trust,
      ),
    );
  }
  var best = <NumberedSection>[];
  var i = 0;
  while (i < found.length) {
    if (found[i].number != 1) {
      i++;
      continue;
    }
    final run = <NumberedSection>[found[i]];
    var j = i + 1;
    while (j < found.length && found[j].number == run.length + 1) {
      run.add(found[j]);
      j++;
    }
    if (run.length > best.length) best = run;
    i = j > i ? j : i + 1;
  }
  return best.length >= 2 ? best : const [];
}

/// Dựng một `VisualSection` họ `sequence`. `null` ⇒ bài này không có dãy —
/// KHÔNG có đường nào rơi xuống «vẽ tạm».
VisualSection? compileNumberedSequence(LessonDocument doc) {
  final run = numberedRunOf(doc);
  if (run.isEmpty) return null;

  ProvenanceRef refFor(List<NumberedSection> items) {
    var worst = ContentTrust.trustedCorpus;
    for (final s in items) {
      if (_rank(s.trust) > _rank(worst)) worst = s.trust;
    }
    return ProvenanceRef(
      blockIds: [for (final s in items) s.blockId],
      derivationRule: numberedSectionSequenceRule,
      trust: worst,
    );
  }

  final nodes = <VisualNode>[
    for (final s in run)
      VisualNode(
        id: 'section-${s.number}',
        label: s.text,
        badge: '${s.number}',
        // Nhãn là NGUYÊN VĂN tiêu đề của chính block ⇒ sách nói thẳng.
        status: InferenceStatus.stated,
        provenance: refFor([s]),
      ),
  ];
  final edges = <VisualEdge>[
    for (var i = 0; i < run.length - 1; i++)
      VisualEdge(
        fromId: nodes[i].id,
        toId: nodes[i + 1].id,
        kind: EdgeKind.sequence,
        // Mũi tên = THỨ TỰ IN, do SAM xếp lại. Không phải câu của sách.
        status: InferenceStatus.derivedDeterministic,
        provenance: refFor([run[i], run[i + 1]]),
      ),
  ];
  return VisualSection(
    id: 'numbered-sequence',
    family: 'sequence',
    // Tiêu đề bài là chữ sách; UI tự viết hoa lại.
    title: LessonDocument.titleCase(doc.title),
    titleProvenance: refFor(run),
    nodes: nodes,
    edges: edges,
    ordering: [for (final n in nodes) n.id],
    trust: refFor(run).trust,
    childSummary: '${run.length} phần, theo đúng thứ tự sách in.',
  );
}

int _rank(ContentTrust t) => switch (t) {
  ContentTrust.trustedCorpus => 0,
  ContentTrust.trustedStructuredLesson => 1,
  ContentTrust.fixtureFromTrustedCorpus => 2,
  ContentTrust.fixtureSynthetic => 3,
  ContentTrust.prototype => 4,
  ContentTrust.withheld => 5,
};
