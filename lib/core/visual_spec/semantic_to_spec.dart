/// ⭐ LANE E2 (round 5) — BỘ BIÊN DỊCH `SemanticData` → `VisualSpec`.
///
/// Chạy NGOÀI GIỜ CHẠY của app (§13): thuần Dart, không import Flutter, không
/// gọi mô hình. `tool/visual_spec/build_specs.dart` gọi hàm này để dựng
/// artefact; app chỉ nạp artefact.
///
/// Việc thật sự của bộ biên dịch — thứ mà renderer KHÔNG được phép làm:
///
/// - **Quyết định `InferenceStatus` bằng KIỂM CHỨNG, không bằng giả định.**
///   Nhãn được coi là «sách nói thẳng» chỉ khi chữ ấy CÓ THẬT trong chữ của
///   block nguồn (so sau khi chuẩn hoá khoảng trắng/dấu đầu dòng). Không tìm
///   thấy ⇒ `inferred` — vì nhãn ấy là chữ SAM viết, không phải chữ sách.
///   Đây là chỗ mô hình cũ im lặng: `ConceptRelation` hôm nay không có ô nào
///   để phân biệt «sách viết» với «SAM nối».
/// - **Mũi tên thứ tự luôn là `derivedDeterministic`.** Sách in các bước cạnh
///   nhau; mũi tên «bước 1 → bước 2» là cách SAM xếp, không phải câu sách.
/// - **Chọn hình CHÍNH tất định**: hình có nhiều nút đọc được nhất; hoà ⇒ thứ
///   tự xuất hiện trong tài liệu. Không có «hình đẹp hơn».
library;

import '../lesson_model/content_trust.dart';
import '../lesson_model/lesson_document.dart';
import '../lesson_model/semantic_data.dart';
import 'visual_spec.dart';

const String semanticToSpecVersion = 'semantic-to-spec-v1';

/// Tên họ hình — CHUỖI, khớp với khoá renderer đăng ký.
class VisualFamily {
  const VisualFamily._();
  static const process = 'process';
  static const comparison = 'comparison';
  static const conceptMap = 'conceptMap';
  static const timeline = 'timeline';
}

/// Kết quả biên dịch MỘT bài — kèm lý do những hình bị bỏ, để đo thật.
class SpecCompileResult {
  const SpecCompileResult({required this.spec, required this.dropped});

  final VisualSpec? spec;

  /// `id hình` → lý do bị bỏ (mã máy, cho báo cáo — không hiện cho trẻ).
  final Map<String, String> dropped;

  bool get isEmpty => spec == null;
}

/// Biên dịch cả một bài. `null` ⇒ bài này KHÔNG có hình nào dựng được —
/// app phải nói thật, không vẽ đại.
SpecCompileResult compileLesson(LessonDocument doc) {
  final sections = <VisualSection>[];
  final dropped = <String, String>{};
  for (final s in doc.semantic) {
    final sec = compileSection(doc, s);
    if (sec == null) {
      dropped[s.id] = _dropReason(doc, s);
    } else {
      sections.add(sec);
    }
  }
  if (sections.isEmpty) {
    return SpecCompileResult(spec: null, dropped: dropped);
  }
  // Hình CHÍNH: nhiều nút đọc được nhất; hoà ⇒ xuất hiện trước.
  var primary = 0;
  for (var i = 1; i < sections.length; i++) {
    if (_readable(sections[i]) > _readable(sections[primary])) primary = i;
  }
  return SpecCompileResult(
    spec: VisualSpec(
      specVersion: VisualSpec.currentVersion,
      primary: sections[primary],
      secondary: [
        for (var i = 0; i < sections.length; i++)
          if (i != primary) sections[i],
      ],
      compiledBy: semanticToSpecVersion,
    ),
    dropped: dropped,
  );
}

int _readable(VisualSection s) => s.nodes.where((n) => !n.isWithheld).length;

String _dropReason(LessonDocument doc, SemanticData s) {
  for (final id in _blockIdsOf(s)) {
    if (doc.blockById(id) == null) return 'missing_source_block:$id';
  }
  return 'empty_after_compile';
}

List<String> _blockIdsOf(SemanticData s) => switch (s) {
  ProcessSemantic(:final steps) => [for (final x in steps) x.sourceBlockId],
  ComparisonSemantic(:final entities) => [
    for (final x in entities) x.sourceBlockId,
  ],
  ConceptMapSemantic(:final relations) => [
    for (final x in relations) x.sourceBlockId,
  ],
  TimelineSemantic(:final events) => [for (final x in events) x.sourceBlockId],
};

/// Biên dịch MỘT hình. `null` ⇒ bỏ hình này (nguồn không tra được…), KHÔNG
/// làm hỏng cả bài.
VisualSection? compileSection(LessonDocument doc, SemanticData s) {
  // Fail-closed: thiếu một block nguồn ⇒ không dựng hình này. Hình mà chạm
  // vào không mở được sách còn tệ hơn không có hình.
  for (final id in _blockIdsOf(s)) {
    if (doc.blockById(id) == null) return null;
  }
  return switch (s) {
    ProcessSemantic() => _process(doc, s),
    ComparisonSemantic() => _comparison(doc, s),
    ConceptMapSemantic() => _conceptMap(doc, s),
    TimelineSemantic() => _timeline(doc, s),
  };
}

// ── chuẩn hoá + kiểm chứng «có thật trong chữ sách» ──

/// Bỏ dấu đầu dòng, gộp khoảng trắng, hạ chữ thường. KHÔNG bỏ dấu thanh —
/// «phẫu» và «phễu» phải vẫn khác nhau (round 4 §5b).
String normalizeForMatch(String v) => v
    .toLowerCase()
    .replaceAll(RegExp(r'^[\s·•\-–—*]+'), '')
    .replaceAll(RegExp(r'\s+'), ' ')
    .trim();

/// Nhãn này có NGUYÊN VĂN trong block nguồn không?
bool isVerbatimIn(String label, LessonBlock? block) {
  if (block == null) return false;
  final text = LessonDocument.textOf(block);
  if (text == null) return false;
  final needle = normalizeForMatch(label);
  if (needle.isEmpty) return false;
  return normalizeForMatch(text).contains(needle);
}

InferenceStatus _labelStatus(String? label, LessonBlock? block) {
  if (label == null) return InferenceStatus.withheld;
  return isVerbatimIn(label, block)
      ? InferenceStatus.stated
      : InferenceStatus.inferred;
}

ProvenanceRef _ref(
  LessonDocument doc,
  List<String> blockIds,
  String rule, {
  List<int>? charSpan,
}) {
  // Độ tin của phần tử = độ tin YẾU NHẤT trong các block nguồn của nó.
  var worst = ContentTrust.trustedCorpus;
  for (final id in blockIds) {
    final b = doc.blockById(id);
    if (b == null) continue;
    if (_trustRank(b.trust) > _trustRank(worst)) worst = b.trust;
  }
  return ProvenanceRef(
    blockIds: blockIds,
    derivationRule: rule,
    trust: worst,
    charSpan: charSpan,
  );
}

int _trustRank(ContentTrust t) => switch (t) {
  ContentTrust.trustedCorpus => 0,
  ContentTrust.trustedStructuredLesson => 1,
  ContentTrust.fixtureFromTrustedCorpus => 2,
  ContentTrust.fixtureSynthetic => 3,
  ContentTrust.prototype => 4,
  ContentTrust.withheld => 5,
};

ContentTrust _sectionTrust(List<ProvenanceRef> refs, ContentTrust declared) {
  var worst = declared;
  for (final r in refs) {
    // `withheld` là trạng thái của MỘT ô, không hạ độ tin cả hình.
    if (r.trust == ContentTrust.withheld) continue;
    if (_trustRank(r.trust) > _trustRank(worst)) worst = r.trust;
  }
  return worst;
}

// ── các họ hình ──

VisualSection _process(LessonDocument doc, ProcessSemantic s) {
  final nodes = <VisualNode>[];
  final refs = <ProvenanceRef>[];
  for (final st in s.steps) {
    final block = doc.blockById(st.sourceBlockId);
    final ref = _ref(doc, [st.sourceBlockId], s.derivation);
    refs.add(ref);
    nodes.add(
      VisualNode(
        id: 'step-${st.order}',
        label: st.text,
        badge: '${st.order}',
        status: _labelStatus(st.text, block),
        provenance: ref,
      ),
    );
  }
  final edges = <VisualEdge>[
    for (var i = 0; i < nodes.length - 1; i++)
      VisualEdge(
        fromId: nodes[i].id,
        toId: nodes[i + 1].id,
        kind: EdgeKind.sequence,
        // Mũi tên là CÁCH XẾP của SAM theo thứ tự in, không phải câu sách.
        status: InferenceStatus.derivedDeterministic,
        provenance: _ref(doc, [
          ...nodes[i].provenance.blockIds,
          ...nodes[i + 1].provenance.blockIds,
        ], s.derivation),
      ),
  ];
  return VisualSection(
    id: s.id,
    family: VisualFamily.process,
    title: s.title,
    titleProvenance: _ref(
      doc,
      [for (final n in nodes) n.provenance.primaryBlockId],
      s.derivation,
    ),
    nodes: nodes,
    edges: edges,
    ordering: [for (final n in nodes) n.id],
    trust: _sectionTrust(refs, s.trust),
    childSummary: _summaryLine('${nodes.length} bước', nodes),
  );
}

VisualSection _comparison(LessonDocument doc, ComparisonSemantic s) {
  // Lưới: HÀNG = một cách sách nêu · CỘT = một chiều so sánh · Ô = giá trị.
  // KHÔNG có ô ⇒ **sách không nói** (khác «SAM chưa đọc được»).
  final nodes = <VisualNode>[];
  final refs = <ProvenanceRef>[];
  final rowIds = <int, List<String>>{};
  final colIds = <int, List<String>>{};
  for (var i = 0; i < s.entities.length; i++) {
    rowIds[i] = [];
    for (var j = 0; j < s.dimensions.length; j++) {
      colIds.putIfAbsent(j, () => []);
      final cell = s.dimensions[j].cells[i];
      final value = cell.text;
      if (value == null) continue; // sách không nói ⇒ không có nút
      // ⭐ §8: nguồn của Ô, không phải nguồn của hàng mượn tạm. Ô thừa kế
      // nguồn hàng vẫn ghi rõ luật thừa kế để đếm được hai mức riêng.
      final srcId = cell.sourceBlockId;
      final ref = _ref(
        doc,
        [srcId],
        cell.grounding == ValueGrounding.cellStated
            ? s.derivation
            : '${s.derivation}+cell-inherits-row-v1',
      );
      refs.add(ref);
      final id = 'cell-$i-$j';
      nodes.add(
        VisualNode(
          id: id,
          label: value,
          status: _labelStatus(value, doc.blockById(srcId)),
          provenance: ref,
        ),
      );
      rowIds[i]!.add(id);
      colIds[j]!.add(id);
    }
  }
  final groups = <VisualGroup>[
    for (var i = 0; i < s.entities.length; i++)
      if (rowIds[i]!.isNotEmpty)
        VisualGroup(
          id: 'row-$i',
          label: s.entities[i].name,
          nodeIds: rowIds[i]!,
          axis: GroupAxis.row,
          provenance: _ref(doc, [
            s.entities[i].sourceBlockId,
          ], s.derivation),
        ),
    for (var j = 0; j < s.dimensions.length; j++)
      if (colIds[j]!.isNotEmpty)
        VisualGroup(
          id: 'col-$j',
          label: s.dimensions[j].name,
          nodeIds: colIds[j]!,
          axis: GroupAxis.column,
        ),
  ];
  return VisualSection(
    id: s.id,
    family: VisualFamily.comparison,
    title: s.title,
    titleProvenance: _ref(
      doc,
      [for (final e in s.entities) e.sourceBlockId],
      s.derivation,
    ),
    nodes: nodes,
    groups: groups,
    trust: _sectionTrust(refs, s.trust),
    childSummary: _summaryLine('${s.entities.length} cách', nodes),
  );
}

VisualSection _conceptMap(LessonDocument doc, ConceptMapSemantic s) {
  final nodes = <VisualNode>[];
  final byName = <String, String>{};
  final refs = <ProvenanceRef>[];
  String nodeFor(String name, String srcId) {
    final existing = byName[name];
    if (existing != null) return existing;
    final id = 'concept-${byName.length}';
    byName[name] = id;
    final ref = _ref(doc, [srcId], s.derivation);
    refs.add(ref);
    nodes.add(
      VisualNode(
        id: id,
        label: name,
        status: _labelStatus(name, doc.blockById(srcId)),
        provenance: ref,
      ),
    );
    return id;
  }

  final edges = <VisualEdge>[];
  for (final r in s.relations) {
    final a = nodeFor(r.a, r.sourceBlockId);
    final b = nodeFor(r.b, r.sourceBlockId);
    final block = doc.blockById(r.sourceBlockId);
    // Quan hệ chỉ là «sách nói thẳng» khi CẢ BA phần đều có trong một câu
    // sách. Thiếu một phần ⇒ SAM nối ⇒ `inferred`, vẽ nét đứt + nói ra.
    final stated =
        isVerbatimIn(r.a, block) &&
        isVerbatimIn(r.b, block) &&
        isVerbatimIn(r.relation, block);
    edges.add(
      VisualEdge(
        fromId: a,
        toId: b,
        label: r.relation,
        kind: EdgeKind.relatesTo,
        status: stated
            ? InferenceStatus.stated
            : InferenceStatus.inferred,
        provenance: _ref(doc, [r.sourceBlockId], s.derivation),
      ),
    );
  }
  // Nút TRUNG TÂM tất định: khái niệm xuất hiện nhiều nhất; hoà ⇒ gặp trước.
  final degree = <String, int>{};
  for (final e in edges) {
    degree.update(e.fromId, (n) => n + 1, ifAbsent: () => 1);
    degree.update(e.toId, (n) => n + 1, ifAbsent: () => 1);
  }
  var hub = nodes.first.id;
  for (final n in nodes) {
    if ((degree[n.id] ?? 0) > (degree[hub] ?? 0)) hub = n.id;
  }
  return VisualSection(
    id: s.id,
    family: VisualFamily.conceptMap,
    title: s.title,
    titleProvenance: _ref(
      doc,
      [for (final r in s.relations) r.sourceBlockId],
      s.derivation,
    ),
    nodes: nodes,
    edges: edges,
    emphasis: [hub],
    trust: _sectionTrust(refs, s.trust),
    childSummary: _summaryLine('${edges.length} mối liên hệ', nodes),
  );
}

VisualSection _timeline(LessonDocument doc, TimelineSemantic s) {
  final nodes = <VisualNode>[];
  final refs = <ProvenanceRef>[];
  for (var i = 0; i < s.events.length; i++) {
    final e = s.events[i];
    final block = doc.blockById(e.sourceBlockId);
    final ref = _ref(doc, [e.sourceBlockId], s.derivation);
    refs.add(ref);
    nodes.add(
      VisualNode(
        id: 'event-$i',
        label: e.title,
        badge: e.when,
        // `text` chỉ giữ khi nó nói THÊM so với «tên + năm» đã hiện — quy
        // tắc chống lặp ba lần (Lane B tìm thấy trên máy thật, round 4).
        detail: _addsSomething(e) ? e.text : null,
        status: _labelStatus(e.title, block),
        provenance: ref,
      ),
    );
  }
  final edges = <VisualEdge>[
    for (var i = 0; i < nodes.length - 1; i++)
      VisualEdge(
        fromId: nodes[i].id,
        toId: nodes[i + 1].id,
        kind: EdgeKind.precedes,
        status: InferenceStatus.derivedDeterministic,
        provenance: _ref(doc, [
          ...nodes[i].provenance.blockIds,
          ...nodes[i + 1].provenance.blockIds,
        ], s.derivation),
      ),
  ];
  return VisualSection(
    id: s.id,
    family: VisualFamily.timeline,
    title: s.title,
    titleProvenance: _ref(
      doc,
      [for (final e in s.events) e.sourceBlockId],
      s.derivation,
    ),
    nodes: nodes,
    edges: edges,
    ordering: [for (final n in nodes) n.id],
    trust: _sectionTrust(refs, s.trust),
    childSummary: _summaryLine('${nodes.length} mốc', nodes),
  );
}

String _norm(String v) => v
    .toLowerCase()
    .replaceAll(RegExp(r'[^\p{L}\p{N}]+', unicode: true), ' ')
    .trim();

bool _addsSomething(TimelineEvent e) {
  final t = e.text;
  if (t == null || t.trim().isEmpty) return false;
  final body = _norm(t);
  if (body.isEmpty) return false;
  return body != _norm('${e.title} ${e.when}') && body != _norm(e.title);
}

/// Câu tóm tắt cho trẻ / trình đọc màn hình — dựng TẤT ĐỊNH từ số đếm.
String _summaryLine(String size, List<VisualNode> nodes) {
  final held = nodes.where((n) => n.isWithheld).length;
  return held == 0
      ? '$size, tất cả đều có chỗ trong sách.'
      : '$size, trong đó $held chỗ SAM chưa đọc được.';
}
