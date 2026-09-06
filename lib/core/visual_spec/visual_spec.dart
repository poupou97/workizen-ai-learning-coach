/// ⭐ LANE E2 (round 5) — `VisualSpec`: BIỂU DIỄN TRUNG GIAN giữa tầng NGỮ
/// NGHĨA và tầng HÌNH ẢNH.
///
/// Ý định Founder: *«Không thiết kế 3.679 visualization — thiết kế một NGÔN
/// NGỮ để 3.679 bài có thể được biên dịch thành visualization.»*
///
///     SOURCE TRUTH  ≠  SEMANTIC INTERPRETATION  ≠  VISUAL REPRESENTATION
///
/// Ba ràng buộc kiểu (trình biên dịch giữ hộ, không phải văn xuôi):
///
/// 1. **Renderer chỉ đọc `VisualSpec`.** `VisualSpec` KHÔNG mang `book`,
///    `lessonNo`, hay bất kỳ khoá nhận dạng bài nào mà renderer đọc được ⇒
///    `if (lesson == …)` không viết ra được, vì renderer không có gì để so.
/// 2. **Không phần tử nào trẻ nhìn thấy mà thiếu nguồn.** Mọi nhãn (`label`)
///    đi kèm `ProvenanceRef`; thiếu ⇒ `fromJson` trả `null` cho CẢ spec
///    (fail-closed), không có «vẽ tạm rồi bổ nguồn sau».
/// 3. **Mũi tên KHÔNG phải sự thật nguồn.** Mỗi cạnh khai `InferenceStatus`:
///    sách nói thẳng · luật tất định suy từ block đã tin · SAM nối (suy diễn).
///    Trạng thái này BẮT BUỘC hiện ra chữ trẻ đọc được — xem `childNote`.
///
/// `family` là CHUỖI MỞ, không phải enum: thêm một họ hình = đăng ký một
/// renderer, không phải sửa một `sealed class` và bốn `switch` vét cạn.
///
/// ⭐ **KHÔNG CÓ HÀM DỰNG TỪ MỘT DẠNG TRÌNH BÀY** (tiền lệ làn A2, PR #84:
/// `MathExpression` có `from_json` nhưng CỐ Ý không có `from_latex`).
/// Ở đây cũng vậy: không có `VisualSpec.fromSvg`, `.fromMarkdown`,
/// `.fromMermaid`, `.fromLatex`, `.fromRendered…`. Một chuỗi để VẼ không được
/// phép quay ngược thành CẤU TRÚC — đó đúng là cái lỗ để nội dung chưa kiểm
/// định rửa mình thành «sơ đồ tin được». `VisualSpec` chỉ dựng được từ:
/// (a) `fromJson` của artefact đã dựng sẵn, hoặc (b) bộ biên dịch chạy trên
/// cấu trúc ngữ nghĩa đã có nguồn. Ràng buộc này do
/// `test/core/visual_spec/no_presentation_constructor_test.dart` quét mã giữ.
///
/// **Phiên bản TÁCH khỏi pack bài học.** `LessonDocument.fromJson` là một
/// union kín: một loại block lạ làm hỏng CẢ tài liệu, không phải một block.
/// `VisualSpec` cố ý nằm trong artefact RIÊNG: một họ hình mới mà app cũ
/// chưa biết chỉ làm mất HÌNH («SAM chưa biết vẽ kiểu đó»), không làm mất
/// BÀI. Không có loại block mới nào được thêm vào pack cho làn này.
library;

import '../lesson_model/content_trust.dart';

/// Một phần tử của spec được sinh ra thế nào — quyết định CHỮ nói với trẻ.
enum InferenceStatus {
  /// Sách viết thẳng câu này; nhãn là NGUYÊN VĂN của block nguồn.
  stated,

  /// Luật TẤT ĐỊNH chạy trên các block đã tin (thứ tự đánh số, năm in trong
  /// ngoặc, hàng của bảng…). Không thêm tri thức, chỉ xếp lại.
  derivedDeterministic,

  /// SAM NỐI hai ý mà sách không viết thẳng thành một câu. Luôn phải hiện
  /// khác đi (nét đứt) và nói ra bằng lời trẻ.
  inferred,

  /// Có chỗ nhưng SAM chưa đọc được — chỗ trống thật, chỉ trang.
  withheld;

  static InferenceStatus? parse(Object? v) {
    if (v is! String) return null;
    for (final s in values) {
      if (s.name == v) return s;
    }
    return null;
  }

  /// Phần tử này có được phép mang chữ không (`withheld` thì không).
  bool get mayCarryLabel => this != withheld;

  /// Chữ TRẺ đọc — không có mã máy, không có tên luật.
  String? get childNote => switch (this) {
    stated => null, // mặc định: chữ sách, không cần chú
    derivedDeterministic => 'SAM xếp lại theo đúng thứ tự sách viết.',
    inferred => 'SAM nối hai ý này — sách không viết thẳng thành một câu.',
    withheld => 'Chỗ này SAM chưa đọc được — con xem trong sách nhé.',
  };
}

/// Loại quan hệ giữa hai nút — MỞ theo họ hình, nhưng đóng ở mức vẽ: renderer
/// chỉ cần biết vẽ mũi tên có hướng hay đường nối không hướng.
enum EdgeKind {
  /// 1 → 2 → 3 (quy trình, thuật toán, vòng đời).
  sequence,

  /// A xảy ra trước B theo thời gian.
  precedes,

  /// A gây ra / dẫn tới B.
  causes,

  /// A chứa / gồm B (phần–toàn thể, phân loại).
  contains,

  /// A và B là hai lựa chọn đặt cạnh nhau để so.
  contrasts,

  /// Quan hệ có nhãn tự do («dùng để», «sống ở»…).
  relatesTo;

  static EdgeKind? parse(Object? v) {
    if (v is! String) return null;
    for (final k in values) {
      if (k.name == v) return k;
    }
    return null;
  }

  bool get isDirected => this != contrasts && this != relatesTo;
}

/// ⭐ CHUỖI NGUỒN của MỘT phần tử nhìn thấy được.
///
/// `VisualElement → VisualSpec element → SemanticNode/Edge → SemanticClaim →
/// SourceBlock(s) → trang/bbox`.
///
/// `blockIds` là DANH SÁCH — một quan hệ thường trải trên hai block («Lọc…»
/// ở block A, «…dùng khi chất không tan» ở block B). Mô hình cũ
/// (`ConceptRelation.sourceBlockId`) chỉ giữ được một, nên nửa nguồn rơi mất.
class ProvenanceRef {
  const ProvenanceRef({
    required this.blockIds,
    required this.derivationRule,
    required this.trust,
    this.claimId,
    this.charSpan,
  });

  /// «Không nguồn thì không vẽ». KHÔNG đặt được thành `assert` trong hàm dựng
  /// `const` (Dart không tính được `length` của list literal lúc biên dịch),
  /// nên bất biến này được giữ ở HAI cửa thật sự có dữ liệu lạ đi qua:
  /// `ProvenanceRef.fromJson` (đường vào từ artefact) và
  /// `VisualSection.fromJson`. Test `visual_spec_test.dart` khoá cả hai.
  bool get isGrounded => blockIds.isNotEmpty;

  /// Các block nguồn (≥1). Mã máy — KHÔNG BAO GIỜ hiện cho trẻ.
  final List<String> blockIds;

  /// Luật đã sinh phần tử này (`tsl-enumerated-steps-v1`…). Mã máy: chỉ hiện
  /// sau nếp gấp kỹ thuật trong sheet «Nguồn & độ tin».
  final String derivationRule;

  /// Độ tin của NGUỒN phần tử này (khác độ tin của cả sơ đồ).
  final ContentTrust trust;

  /// Khẳng định ngữ nghĩa (nếu tầng semantic có id riêng cho nó).
  final String? claimId;

  /// Khoảng KÝ TỰ trong chữ của `blockIds.first` — cho phép tô đúng đoạn
  /// sách thay vì cả block. Fixture Lịch sử đã có sẵn (`charSpan`), mô hình
  /// `TimelineEvent` hôm nay VỨT ĐI; ở đây giữ lại.
  final List<int>? charSpan;

  String get primaryBlockId => blockIds.first;

  static ProvenanceRef? fromJson(Object? v) {
    if (v is! Map) return null;
    final ids = [
      for (final x in (v['blockIds'] as List? ?? const []))
        if (x is String && x.isNotEmpty) x,
    ];
    final rule = v['derivationRule'];
    final trust = ContentTrust.parse(v['trust']);
    if (ids.isEmpty || rule is! String || trust == null) return null;
    final span = v['charSpan'];
    List<int>? cs;
    if (span is List) {
      final n = [
        for (final x in span)
          if (x is num) x.toInt(),
      ];
      if (n.length != 2 || n[0] < 0 || n[1] < n[0]) return null;
      cs = n;
    } else if (span != null) {
      return null;
    }
    return ProvenanceRef(
      blockIds: ids,
      derivationRule: rule,
      trust: trust,
      claimId: v['claimId'] as String?,
      charSpan: cs,
    );
  }

  Map<String, Object?> toJson() => {
    'blockIds': blockIds,
    'derivationRule': derivationRule,
    'trust': trust.name,
    if (claimId != null) 'claimId': claimId,
    if (charSpan != null) 'charSpan': charSpan,
  };
}

/// Một nút trên hình — hộp, mốc, hàng bảng, khái niệm.
class VisualNode {
  const VisualNode({
    required this.id,
    required this.status,
    required this.provenance,
    this.label,
    this.detail,
    this.badge,
    this.confidence,
  });

  /// Mã máy trong spec — KHÔNG hiện cho trẻ (test quét).
  final String id;

  /// Chữ chính. `null` ⇔ `status == withheld`.
  final String? label;

  /// Câu phụ (nguyên văn hoặc rỗng).
  final String? detail;

  /// Nhãn nhỏ đứng trước nhãn chính («40 – 43», «Bước 2») — chữ sách.
  final String? badge;

  final InferenceStatus status;
  final ProvenanceRef provenance;

  /// 0..1 nếu tầng semantic có đo; `null` ⇒ không đo (KHÔNG mặc định 1.0).
  final double? confidence;

  bool get isWithheld => status == InferenceStatus.withheld;

  static VisualNode? fromJson(Object? v) {
    if (v is! Map) return null;
    final id = v['id'];
    final status = InferenceStatus.parse(v['status']);
    final prov = ProvenanceRef.fromJson(v['provenance']);
    if (id is! String || id.isEmpty || status == null || prov == null) {
      return null;
    }
    final label = v['label'];
    // Fail-closed: có chữ ⇔ KHÔNG withheld. Không có nút vừa giữ lại vừa nói.
    if (status.mayCarryLabel) {
      if (label is! String || label.trim().isEmpty) return null;
    } else if (label != null) {
      return null;
    }
    final conf = v['confidence'];
    if (conf != null && (conf is! num || conf < 0 || conf > 1)) return null;
    return VisualNode(
      id: id,
      label: label as String?,
      detail: v['detail'] as String?,
      badge: v['badge'] as String?,
      status: status,
      provenance: prov,
      confidence: (conf as num?)?.toDouble(),
    );
  }

  Map<String, Object?> toJson() => {
    'id': id,
    if (label != null) 'label': label,
    if (detail != null) 'detail': detail,
    if (badge != null) 'badge': badge,
    'status': status.name,
    'provenance': provenance.toJson(),
    if (confidence != null) 'confidence': confidence,
  };
}

/// Một cạnh — mũi tên, nan hoa, nối mốc.
class VisualEdge {
  const VisualEdge({
    required this.fromId,
    required this.toId,
    required this.kind,
    required this.status,
    required this.provenance,
    this.label,
  });

  final String fromId, toId;

  /// Nhãn quan hệ («dùng để», «gây ra»); `null` ⇒ chỉ vẽ đường.
  final String? label;
  final EdgeKind kind;
  final InferenceStatus status;
  final ProvenanceRef provenance;

  /// Cạnh SUY DIỄN ⇒ vẽ nét đứt + hiện `childNote`. Không có đường nào để
  /// một cạnh suy diễn trông giống cạnh sách nói thẳng.
  bool get isInferred => status == InferenceStatus.inferred;

  static VisualEdge? fromJson(Object? v) {
    if (v is! Map) return null;
    final f = v['fromId'], t = v['toId'];
    final kind = EdgeKind.parse(v['kind']);
    final status = InferenceStatus.parse(v['status']);
    final prov = ProvenanceRef.fromJson(v['provenance']);
    if (f is! String || t is! String || f.isEmpty || t.isEmpty) return null;
    if (kind == null || status == null || prov == null) return null;
    if (status == InferenceStatus.withheld) return null; // cạnh không «trống»
    final label = v['label'];
    if (label != null && label is! String) return null;
    return VisualEdge(
      fromId: f,
      toId: t,
      label: label as String?,
      kind: kind,
      status: status,
      provenance: prov,
    );
  }

  Map<String, Object?> toJson() => {
    'fromId': fromId,
    'toId': toId,
    if (label != null) 'label': label,
    'kind': kind.name,
    'status': status.name,
    'provenance': provenance.toJson(),
  };
}

/// Vai trò của một nhóm khi vẽ. `row` × `column` dựng LƯỚI (bảng so sánh,
/// ma trận): ô = nút thuộc CẢ hàng và cột đó; KHÔNG có nút ⇒ **sách không
/// nói** (ô để trống), khác hẳn nút `withheld` = **SAM chưa đọc được**.
enum GroupAxis {
  row,
  column,
  cluster;

  static GroupAxis? parse(Object? v) {
    if (v == null) return cluster;
    if (v is! String) return null;
    for (final a in values) {
      if (a.name == v) return a;
    }
    return null;
  }
}

/// Gom nhóm các nút (cột của bảng so sánh, nhánh của cây phân loại).
class VisualGroup {
  const VisualGroup({
    required this.id,
    required this.label,
    required this.nodeIds,
    this.axis = GroupAxis.cluster,
    this.provenance,
  });

  final String id;

  /// Chữ trẻ đọc (tên chiều so sánh, tên nhánh).
  final String label;
  final List<String> nodeIds;
  final GroupAxis axis;

  /// Nhóm do luật xếp (không phải chữ sách) ⇒ `null` hợp lệ; nhưng nhóm có
  /// TÊN LẤY TỪ SÁCH thì phải có nguồn.
  final ProvenanceRef? provenance;

  static VisualGroup? fromJson(Object? v) {
    if (v is! Map) return null;
    final id = v['id'], label = v['label'];
    final ids = [
      for (final x in (v['nodeIds'] as List? ?? const []))
        if (x is String) x,
    ];
    if (id is! String || label is! String || ids.isEmpty) return null;
    final axis = GroupAxis.parse(v['axis']);
    if (axis == null) return null;
    final p = v['provenance'];
    final prov = p == null ? null : ProvenanceRef.fromJson(p);
    if (p != null && prov == null) return null;
    return VisualGroup(
      id: id,
      label: label,
      nodeIds: ids,
      axis: axis,
      provenance: prov,
    );
  }

  Map<String, Object?> toJson() => {
    'id': id,
    'label': label,
    'nodeIds': nodeIds,
    if (axis != GroupAxis.cluster) 'axis': axis.name,
    if (provenance != null) 'provenance': provenance!.toJson(),
  };
}

/// MỘT hình trong bài. Một bài có thể cần Dòng thời gian + Nhân quả + Cây
/// phân loại cùng lúc ⇒ `VisualSpec` mang MỘT `primary` và N `secondary`.
class VisualSection {
  const VisualSection({
    required this.id,
    required this.family,
    required this.title,
    required this.nodes,
    required this.trust,
    required this.titleProvenance,
    this.edges = const [],
    this.groups = const [],
    this.ordering = const [],
    this.emphasis = const [],
    this.childSummary,
  });

  final String id;

  /// Họ hình — CHUỖI MỞ (`process`, `comparison`, `timeline`, `conceptMap`,
  /// `partWhole`, `causeEffect`, `classification`…). Renderer đăng ký theo
  /// chuỗi này; họ chưa có renderer ⇒ FAIL CLOSED, không vẽ đại.
  final String family;

  /// Tiêu đề trẻ đọc — chữ sách.
  final String title;
  final ProvenanceRef titleProvenance;

  final List<VisualNode> nodes;
  final List<VisualEdge> edges;
  final List<VisualGroup> groups;

  /// Thứ tự trình bày (id nút). Rỗng ⇒ theo thứ tự `nodes`.
  final List<String> ordering;

  /// Các nút cần nhấn (nút trung tâm, mốc quan trọng) — id nút.
  final List<String> emphasis;

  /// Độ tin của cả hình (thấp nhất trong các phần tử — tính khi dựng).
  final ContentTrust trust;

  /// Câu tóm tắt cho trẻ / cho trình đọc màn hình. Không có ⇒ renderer tự
  /// dựng từ dữ liệu, KHÔNG gọi mô hình.
  final String? childSummary;

  List<VisualNode> get orderedNodes {
    if (ordering.isEmpty) return nodes;
    final byId = {for (final n in nodes) n.id: n};
    final out = <VisualNode>[
      for (final id in ordering)
        if (byId[id] != null) byId[id]!,
    ];
    for (final n in nodes) {
      if (!ordering.contains(n.id)) out.add(n);
    }
    return out;
  }

  VisualNode? nodeById(String id) {
    for (final n in nodes) {
      if (n.id == id) return n;
    }
    return null;
  }

  bool get hasInferredEdge => edges.any((e) => e.isInferred);
  bool get hasWithheldNode => nodes.any((n) => n.isWithheld);

  List<VisualGroup> get rows => [
    for (final g in groups)
      if (g.axis == GroupAxis.row) g,
  ];
  List<VisualGroup> get columns => [
    for (final g in groups)
      if (g.axis == GroupAxis.column) g,
  ];

  /// Ô của lưới = nút thuộc CẢ hàng và cột. `null` ⇒ **sách không nói** —
  /// renderer để trống và nói thế, không điền hộ.
  VisualNode? cellAt(VisualGroup row, VisualGroup column) {
    for (final id in row.nodeIds) {
      if (column.nodeIds.contains(id)) return nodeById(id);
    }
    return null;
  }

  List<VisualEdge> edgesFrom(String nodeId) => [
    for (final e in edges)
      if (e.fromId == nodeId) e,
  ];

  /// Các luật sinh đã tham gia hình này — cho sheet «Nguồn & độ tin».
  Set<String> get derivationRules => {
    titleProvenance.derivationRule,
    for (final n in nodes) n.provenance.derivationRule,
    for (final e in edges) e.provenance.derivationRule,
  };

  /// Mọi block nguồn của hình này — cho census và cho sheet nguồn.
  Set<String> get sourceBlockIds => {
    ...titleProvenance.blockIds,
    for (final n in nodes) ...n.provenance.blockIds,
    for (final e in edges) ...e.provenance.blockIds,
    for (final g in groups) ...?g.provenance?.blockIds,
  };

  static VisualSection? fromJson(Object? v) {
    if (v is! Map) return null;
    final id = v['id'], family = v['family'], title = v['title'];
    final trust = ContentTrust.parse(v['trust']);
    final tp = ProvenanceRef.fromJson(v['titleProvenance']);
    if (id is! String || family is! String || family.isEmpty) return null;
    if (title is! String || title.trim().isEmpty) return null;
    if (trust == null || tp == null) return null;

    final nodes = <VisualNode>[];
    for (final n in (v['nodes'] as List? ?? const [])) {
      final node = VisualNode.fromJson(n);
      if (node == null) return null; // một nút hỏng ⇒ cả hình không dùng
      nodes.add(node);
    }
    if (nodes.isEmpty) return null;
    final ids = {for (final n in nodes) n.id};
    if (ids.length != nodes.length) return null; // id trùng ⇒ từ chối

    final edges = <VisualEdge>[];
    for (final e in (v['edges'] as List? ?? const [])) {
      final edge = VisualEdge.fromJson(e);
      // Cạnh trỏ vào nút không tồn tại = hình sai, không phải hình thiếu.
      if (edge == null) return null;
      if (!ids.contains(edge.fromId) || !ids.contains(edge.toId)) return null;
      edges.add(edge);
    }
    final groups = <VisualGroup>[];
    for (final g in (v['groups'] as List? ?? const [])) {
      final grp = VisualGroup.fromJson(g);
      if (grp == null) return null;
      if (!grp.nodeIds.every(ids.contains)) return null;
      groups.add(grp);
    }
    final ordering = [
      for (final x in (v['ordering'] as List? ?? const []))
        if (x is String) x,
    ];
    if (!ordering.every(ids.contains)) return null;
    final emphasis = [
      for (final x in (v['emphasis'] as List? ?? const []))
        if (x is String) x,
    ];
    if (!emphasis.every(ids.contains)) return null;

    return VisualSection(
      id: id,
      family: family,
      title: title,
      titleProvenance: tp,
      nodes: nodes,
      edges: edges,
      groups: groups,
      ordering: ordering,
      emphasis: emphasis,
      trust: trust,
      childSummary: v['childSummary'] as String?,
    );
  }

  Map<String, Object?> toJson() => {
    'id': id,
    'family': family,
    'title': title,
    'titleProvenance': titleProvenance.toJson(),
    'nodes': [for (final n in nodes) n.toJson()],
    if (edges.isNotEmpty) 'edges': [for (final e in edges) e.toJson()],
    if (groups.isNotEmpty) 'groups': [for (final g in groups) g.toJson()],
    if (ordering.isNotEmpty) 'ordering': ordering,
    if (emphasis.isNotEmpty) 'emphasis': emphasis,
    'trust': trust.name,
    if (childSummary != null) 'childSummary': childSummary,
  };
}

/// TOÀN BỘ phần hình của một bài: một hình chính + các hình phụ.
///
/// Cố ý KHÔNG có `book` / `lessonNo` / `slotKey`: renderer nhận `VisualSpec`
/// nên không có gì để rẽ nhánh theo bài. Khoá tra cứu (`lessonKey`) nằm ở
/// tầng ARTEFACT (`visual_spec_artifact.dart`), ngoài tầm renderer.
class VisualSpec {
  const VisualSpec({
    required this.specVersion,
    required this.primary,
    this.secondary = const [],
    this.compiledBy = '',
  });

  static const currentVersion = 'visual-spec-v1';

  final String specVersion;
  final VisualSection primary;
  final List<VisualSection> secondary;

  /// Tên + phiên bản bộ biên dịch đã sinh spec (mã máy, cho replay).
  final String compiledBy;

  List<VisualSection> get sections => [primary, ...secondary];

  /// Độ tin thấp nhất trong toàn spec — «cả bài chỉ tin được tới mức này».
  ContentTrust get trust {
    var worst = primary.trust;
    for (final s in secondary) {
      if (_rank(s.trust) > _rank(worst)) worst = s.trust;
    }
    return worst;
  }

  /// Càng lớn càng ít tin được — thứ tự CỐ ĐỊNH, test khoá.
  static int _rank(ContentTrust t) => switch (t) {
    ContentTrust.trustedCorpus => 0,
    ContentTrust.trustedStructuredLesson => 1,
    ContentTrust.fixtureFromTrustedCorpus => 2,
    ContentTrust.fixtureSynthetic => 3,
    ContentTrust.prototype => 4,
    ContentTrust.withheld => 5,
  };

  static VisualSpec? fromJson(Object? v) {
    if (v is! Map) return null;
    final ver = v['specVersion'];
    if (ver != currentVersion) return null; // phiên bản lạ ⇒ không đoán
    final primary = VisualSection.fromJson(v['primary']);
    if (primary == null) return null;
    final secondary = <VisualSection>[];
    for (final s in (v['secondary'] as List? ?? const [])) {
      final sec = VisualSection.fromJson(s);
      if (sec == null) return null;
      secondary.add(sec);
    }
    final ids = {primary.id, for (final s in secondary) s.id};
    if (ids.length != secondary.length + 1) return null;
    return VisualSpec(
      specVersion: ver as String,
      primary: primary,
      secondary: secondary,
      compiledBy: (v['compiledBy'] as String?) ?? '',
    );
  }

  Map<String, Object?> toJson() => {
    'specVersion': specVersion,
    'primary': primary.toJson(),
    if (secondary.isNotEmpty)
      'secondary': [for (final s in secondary) s.toJson()],
    if (compiledBy.isNotEmpty) 'compiledBy': compiledBy,
  };
}
