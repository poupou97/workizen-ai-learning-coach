/// TRACK B — DỮ LIỆU NGỮ NGHĨA CÓ KIỂU cho Mode 2 «Trực quan».
///
/// Hợp đồng UI đón «typed semantic data → renderer» (05-VISUAL-LEARNING §1):
/// renderer là hàm thuần trên dữ liệu có kiểu, KHÔNG có đường «bài → LLM →
/// hình». Bốn hình dạng của Founder đều có kiểu ở đây; một bài chỉ mang hình
/// dạng nào dữ liệu của nó chống đỡ được (Bài 17: Process + Comparison; KHÔNG
/// có ConceptMap/Timeline — UI không hiện tab cho thứ không có).
///
/// Mỗi nút/hàng/bước mang `sourceBlockId` — không có nguồn thì không vẽ.
library;

import 'content_trust.dart';

sealed class SemanticData {
  const SemanticData({
    required this.id,
    required this.title,
    required this.trust,
    required this.derivation,
  });

  final String id;
  final String title;
  final ContentTrust trust;

  /// LUẬT sinh ra dữ liệu này (vd `tsl-enumerated-steps-v1`) — để kiểm lại
  /// được và để đếm «suy tất định từ block tin được» tách khỏi «viết tay».
  final String derivation;

  /// Tên hình dạng cho tab con của Mode 2.
  String get shapeLabel;

  Map<String, Object?> toJson();

  static SemanticData? fromJson(Map<String, Object?> j) {
    final trust = ContentTrust.parse(j['trust']);
    final id = j['id'], title = j['title'], derivation = j['derivation'];
    if (trust == null || id is! String || title is! String) return null;
    if (derivation is! String) return null;
    switch (j['type']) {
      case 'process':
        final steps = <ProcessStep>[];
        for (final s in (j['steps'] as List? ?? const []).whereType<Map>()) {
          final st = ProcessStep.fromJson(s.cast<String, Object?>());
          if (st == null) return null; // một bước hỏng ⇒ cả sơ đồ không dùng
          steps.add(st);
        }
        if (steps.isEmpty) return null;
        return ProcessSemantic(
          id: id,
          title: title,
          trust: trust,
          derivation: derivation,
          steps: steps,
        );
      case 'comparison':
        final entities = <ComparisonEntity>[];
        for (final e in (j['entities'] as List? ?? const []).whereType<Map>()) {
          final name = e['name'], src = e['sourceBlockId'];
          if (name is! String || src is! String) return null;
          entities.add(ComparisonEntity(name: name, sourceBlockId: src));
        }
        final dims = <ComparisonDimension>[];
        for (final d
            in (j['dimensions'] as List? ?? const []).whereType<Map>()) {
          final name = d['name'];
          final values = (d['values'] as List? ?? const [])
              .map((v) => v is String ? v : null)
              .toList();
          if (name is! String || values.length != entities.length) return null;
          dims.add(ComparisonDimension(name: name, values: values));
        }
        if (entities.isEmpty || dims.isEmpty) return null;
        return ComparisonSemantic(
          id: id,
          title: title,
          trust: trust,
          derivation: derivation,
          entities: entities,
          dimensions: dims,
        );
      case 'conceptMap':
        final rels = <ConceptRelation>[];
        for (final r
            in (j['relations'] as List? ?? const []).whereType<Map>()) {
          final a = r['a'], rel = r['relation'], b = r['b'];
          final src = r['sourceBlockId'];
          if (a is! String || rel is! String || b is! String) return null;
          if (src is! String) return null;
          rels.add(
            ConceptRelation(a: a, relation: rel, b: b, sourceBlockId: src),
          );
        }
        if (rels.isEmpty) return null;
        return ConceptMapSemantic(
          id: id,
          title: title,
          trust: trust,
          derivation: derivation,
          relations: rels,
        );
      case 'timeline':
        final evs = <TimelineEvent>[];
        for (final e in (j['events'] as List? ?? const []).whereType<Map>()) {
          final when = e['when'], t = e['title'], src = e['sourceBlockId'];
          if (when is! String || t is! String || src is! String) return null;
          evs.add(
            TimelineEvent(
              when: when,
              title: t,
              text: e['text'] as String?,
              sourceBlockId: src,
            ),
          );
        }
        if (evs.isEmpty) return null;
        return TimelineSemantic(
          id: id,
          title: title,
          trust: trust,
          derivation: derivation,
          events: evs,
        );
      default:
        return null;
    }
  }

  Map<String, Object?> _base(String type) => {
    'type': type,
    'id': id,
    'title': title,
    'trust': trust.name,
    'derivation': derivation,
  };
}

/// Một bước của quy trình — NGUYÊN VĂN hoặc BỊ GIỮ LẠI (withheld), không có
/// bước nào «viết lại cho gọn».
class ProcessStep {
  const ProcessStep({
    required this.order,
    required this.sourceBlockId,
    this.text,
    this.withheldReason,
  }) : assert(
         (text == null) != (withheldReason == null),
         'bước có chữ HOẶC bị giữ lại — không cả hai, không trống cả hai',
       );

  final int order;
  final String sourceBlockId;

  /// Nguyên văn; `null` ⇔ bước này SAM chưa đọc được (`withheldReason`).
  final String? text;
  final String? withheldReason;

  bool get isWithheld => withheldReason != null;

  static ProcessStep? fromJson(Map<String, Object?> j) {
    final order = j['order'], src = j['sourceBlockId'];
    if (order is! num || src is! String) return null;
    final text = j['text'], why = j['withheldReason'];
    if (text is String && why == null) {
      return ProcessStep(order: order.toInt(), sourceBlockId: src, text: text);
    }
    if (text == null && why is String) {
      return ProcessStep(
        order: order.toInt(),
        sourceBlockId: src,
        withheldReason: why,
      );
    }
    return null;
  }

  Map<String, Object?> toJson() => {
    'order': order,
    'sourceBlockId': sourceBlockId,
    if (text != null) 'text': text,
    if (withheldReason != null) 'withheldReason': withheldReason,
  };
}

final class ProcessSemantic extends SemanticData {
  const ProcessSemantic({
    required super.id,
    required super.title,
    required super.trust,
    required super.derivation,
    required this.steps,
  });
  final List<ProcessStep> steps;

  @override
  String get shapeLabel => 'Sơ đồ quy trình';

  @override
  Map<String, Object?> toJson() => {
    ..._base('process'),
    'steps': [for (final s in steps) s.toJson()],
  };
}

class ComparisonEntity {
  const ComparisonEntity({required this.name, required this.sourceBlockId});
  final String name;
  final String sourceBlockId;
}

/// Một chiều so sánh; `values[i]` ứng với `entities[i]`, `null` = sách không
/// nói — ô để trống, không điền hộ.
class ComparisonDimension {
  const ComparisonDimension({required this.name, required this.values});
  final String name;
  final List<String?> values;
}

final class ComparisonSemantic extends SemanticData {
  const ComparisonSemantic({
    required super.id,
    required super.title,
    required super.trust,
    required super.derivation,
    required this.entities,
    required this.dimensions,
  });
  final List<ComparisonEntity> entities;
  final List<ComparisonDimension> dimensions;

  @override
  String get shapeLabel => 'Bảng so sánh';

  @override
  Map<String, Object?> toJson() => {
    ..._base('comparison'),
    'entities': [
      for (final e in entities)
        {'name': e.name, 'sourceBlockId': e.sourceBlockId},
    ],
    'dimensions': [
      for (final d in dimensions) {'name': d.name, 'values': d.values},
    ],
  };
}

class ConceptRelation {
  const ConceptRelation({
    required this.a,
    required this.relation,
    required this.b,
    required this.sourceBlockId,
  });
  final String a, relation, b, sourceBlockId;
}

final class ConceptMapSemantic extends SemanticData {
  const ConceptMapSemantic({
    required super.id,
    required super.title,
    required super.trust,
    required super.derivation,
    required this.relations,
  });
  final List<ConceptRelation> relations;

  @override
  String get shapeLabel => 'Sơ đồ khái niệm';

  @override
  Map<String, Object?> toJson() => {
    ..._base('conceptMap'),
    'relations': [
      for (final r in relations)
        {
          'a': r.a,
          'relation': r.relation,
          'b': r.b,
          'sourceBlockId': r.sourceBlockId,
        },
    ],
  };
}

class TimelineEvent {
  const TimelineEvent({
    required this.when,
    required this.title,
    required this.sourceBlockId,
    this.text,
  });
  final String when, title, sourceBlockId;
  final String? text;
}

final class TimelineSemantic extends SemanticData {
  const TimelineSemantic({
    required super.id,
    required super.title,
    required super.trust,
    required super.derivation,
    required this.events,
  });
  final List<TimelineEvent> events;

  @override
  String get shapeLabel => 'Dòng thời gian';

  @override
  Map<String, Object?> toJson() => {
    ..._base('timeline'),
    'events': [
      for (final e in events)
        {
          'when': e.when,
          'title': e.title,
          if (e.text != null) 'text': e.text,
          'sourceBlockId': e.sourceBlockId,
        },
    ],
  };
}
