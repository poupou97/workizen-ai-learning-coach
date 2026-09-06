/// LANE E2 (round 5) — `VisualSpec` fail-closed + composition + artefact.
///
/// Bất biến được test giữ hộ, không phải văn xuôi giữ:
/// - phần tử nhìn thấy KHÔNG có nguồn ⇒ cả spec bị từ chối;
/// - nút `withheld` KHÔNG được mang chữ, nút có chữ KHÔNG được khai withheld;
/// - cạnh trỏ vào nút không tồn tại ⇒ từ chối (hình SAI, không phải hình thiếu);
/// - một spec hỏng ⇒ CẢ artefact bị từ chối (nửa artefact là thứ nguy hiểm nhất).
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/visual_spec/visual_spec.dart';
import 'package:learning_coach/core/visual_spec/visual_spec_artifact.dart';

Map<String, Object?> _prov([String rule = 'r-v1']) => {
  'blockIds': ['blk-1'],
  'derivationRule': rule,
  'trust': 'trustedStructuredLesson',
};

Map<String, Object?> _node(String id, {Object? label = 'chữ sách'}) => {
  'id': id,
  if (label != null) 'label': label,
  'status': 'stated',
  'provenance': _prov(),
};

Map<String, Object?> _section({
  List<Map<String, Object?>>? nodes,
  List<Map<String, Object?>>? edges,
  String id = 'sec-1',
}) => {
  'id': id,
  'family': 'process',
  'title': 'Tách chất',
  'titleProvenance': _prov(),
  'trust': 'trustedStructuredLesson',
  'nodes': nodes ?? [_node('a'), _node('b')],
  if (edges != null) 'edges': edges,
};

Map<String, Object?> _spec({Map<String, Object?>? primary, List? secondary}) => {
  'specVersion': VisualSpec.currentVersion,
  'primary': primary ?? _section(),
  if (secondary != null) 'secondary': secondary,
};

void main() {
  test('spec hợp lệ đọc được và round-trip không mất gì', () {
    final s = VisualSpec.fromJson(_spec())!;
    expect(s.primary.nodes.length, 2);
    expect(VisualSpec.fromJson(s.toJson())!.toJson(), s.toJson());
  });

  test('FAIL CLOSED: nút thiếu nguồn ⇒ cả spec bị từ chối', () {
    final bad = _node('a')..remove('provenance');
    expect(VisualSpec.fromJson(_spec(primary: _section(nodes: [bad]))), isNull);
  });

  test('FAIL CLOSED: nguồn không có block nào ⇒ từ chối', () {
    final bad = _node('a');
    bad['provenance'] = {..._prov(), 'blockIds': <String>[]};
    expect(VisualSpec.fromJson(_spec(primary: _section(nodes: [bad]))), isNull);
  });

  test('FAIL CLOSED: nút withheld mà vẫn mang chữ ⇒ từ chối', () {
    final bad = _node('a');
    bad['status'] = 'withheld';
    expect(VisualSpec.fromJson(_spec(primary: _section(nodes: [bad]))), isNull);
  });

  test('FAIL CLOSED: nút có chữ rỗng ⇒ từ chối (không vẽ ô trống câm)', () {
    final bad = _node('a', label: '   ');
    expect(VisualSpec.fromJson(_spec(primary: _section(nodes: [bad]))), isNull);
  });

  test('nút withheld KHÔNG có chữ là hợp lệ — chỗ trống thật', () {
    final held = {
      'id': 'a',
      'status': 'withheld',
      'provenance': _prov(),
    };
    final s = VisualSpec.fromJson(
      _spec(primary: _section(nodes: [held, _node('b')])),
    );
    expect(s, isNotNull);
    expect(s!.primary.hasWithheldNode, isTrue);
  });

  test('FAIL CLOSED: cạnh trỏ vào nút không tồn tại ⇒ từ chối', () {
    final edge = {
      'fromId': 'a',
      'toId': 'khong-co',
      'kind': 'sequence',
      'status': 'derivedDeterministic',
      'provenance': _prov(),
    };
    expect(
      VisualSpec.fromJson(_spec(primary: _section(edges: [edge]))),
      isNull,
    );
  });

  test('FAIL CLOSED: phiên bản spec lạ ⇒ không đoán, trả null', () {
    final j = _spec()..['specVersion'] = 'visual-spec-v99';
    expect(VisualSpec.fromJson(j), isNull);
  });

  test('cạnh SUY DIỄN giữ được trạng thái và có lời cho trẻ', () {
    final edge = {
      'fromId': 'a',
      'toId': 'b',
      'kind': 'relatesTo',
      'status': 'inferred',
      'provenance': _prov(),
    };
    final s = VisualSpec.fromJson(_spec(primary: _section(edges: [edge])))!;
    expect(s.primary.hasInferredEdge, isTrue);
    expect(InferenceStatus.inferred.childNote, contains('SAM nối'));
    // Cạnh sách nói thẳng thì KHÔNG có chú — không làm trẻ nghi ngờ chữ sách.
    expect(InferenceStatus.stated.childNote, isNull);
  });

  test('COMPOSITION: một hình chính + nhiều hình phụ, id không được trùng', () {
    final ok = VisualSpec.fromJson(
      _spec(secondary: [_section(id: 'sec-2')]),
    );
    expect(ok!.sections.length, 2);
    expect(VisualSpec.fromJson(_spec(secondary: [_section()])), isNull);
  });

  test('LƯỚI: ô = giao của hàng và cột; KHÔNG có ô = «sách không nói»', () {
    final j = _spec(
      primary: {
        ..._section(nodes: [_node('c00'), _node('c10')]),
        'family': 'comparison',
        'groups': [
          {
            'id': 'r0',
            'label': 'Lọc',
            'axis': 'row',
            'nodeIds': ['c00'],
          },
          {
            'id': 'r1',
            'label': 'Cô cạn',
            'axis': 'row',
            'nodeIds': ['c10'],
          },
          {
            'id': 'k0',
            'label': 'Dùng để tách',
            'axis': 'column',
            'nodeIds': ['c00', 'c10'],
          },
          {
            'id': 'k1',
            'label': 'Ví dụ',
            'axis': 'column',
            'nodeIds': ['c00'],
          },
        ],
      },
    );
    final s = VisualSpec.fromJson(j)!.primary;
    expect(s.rows.length, 2);
    expect(s.columns.length, 2);
    expect(s.cellAt(s.rows[0], s.columns[0])!.id, 'c00');
    // Hàng «Cô cạn» × cột «Ví dụ»: sách không nói ⇒ không có nút.
    expect(s.cellAt(s.rows[1], s.columns[1]), isNull);
  });

  test('ARTEFACT: một spec hỏng ⇒ CẢ artefact bị từ chối', () {
    final good = {
      'artifactVersion': VisualSpecArtifact.currentVersion,
      'builtAt': '2026-09-06T00:00:00Z',
      'builder': 'test',
      'specs': {'book#1': _spec()},
    };
    expect(VisualSpecArtifact.fromJson(good), isNotNull);
    final bad = {
      ...good,
      'specs': {
        'book#1': _spec(),
        'book#2': _spec(primary: _section(nodes: [_node('a')..remove('provenance')])),
      },
    };
    expect(VisualSpecArtifact.fromJson(bad), isNull);
  });

  test('ARTEFACT: `lessonKey` sống ở tầng artefact, KHÔNG trong VisualSpec', () {
    // Nếu spec mang danh tính bài thì renderer sẽ có thứ để rẽ nhánh. Không có.
    final s = VisualSpec.fromJson(_spec())!;
    final keys = s.toJson().keys.toSet();
    for (final forbidden in ['book', 'lessonNo', 'lesson', 'slotKey']) {
      expect(keys.contains(forbidden), isFalse, reason: forbidden);
    }
  });
}
