/// ⭐ ROUND 5 §8 (Lane E2) — HỒI QUY: không ô so sánh nào lên màn mà không
/// lần được về một block sách.
///
/// Trước sửa: `ComparisonDimension.values` là `List<String?>` trần. Một ô có
/// chữ hoàn toàn có thể hiện ra mà không có đường nào về nguồn — và không
/// test nào bắt được, vì kiểu vẫn hợp lệ.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/semantic_data.dart';

Map<String, Object?> _comparison(List<Object?> values) => {
  'type': 'comparison',
  'id': 'c1',
  'title': 'Các cách tách chất',
  'trust': 'fixtureSynthetic',
  'derivation': 'tsl-summary-methods-v1',
  'entities': [
    {'name': 'Lọc', 'sourceBlockId': 'blk-row-1'},
    {'name': 'Cô cạn', 'sourceBlockId': 'blk-row-2'},
  ],
  'dimensions': [
    {'name': 'Dùng để tách', 'values': values},
  ],
};

void main() {
  test('§8 mọi ô đều có sourceBlockId — kể cả JSON dạng CŨ (List<String?>)', () {
    final s =
        SemanticData.fromJson(_comparison(['tách hạt rắn', null]))
            as ComparisonSemantic;
    final cells = s.dimensions.single.cells;
    expect(cells.length, 2);
    for (final c in cells) {
      expect(c.sourceBlockId.isNotEmpty, isTrue, reason: 'không ô nào vô nguồn');
    }
    // Thừa kế nguồn của HÀNG — và KHAI ra là thừa kế, không giả vờ nguồn riêng.
    expect(cells[0].sourceBlockId, 'blk-row-1');
    expect(cells[1].sourceBlockId, 'blk-row-2');
    expect(cells[0].grounding, ValueGrounding.inheritedFromEntity);
    // «sách không nói» vẫn là một ô có nguồn, chỉ là không có chữ.
    expect(cells[1].text, isNull);
  });

  test('§8 ô khai nguồn RIÊNG ⇒ cellStated, không thừa kế nhầm', () {
    final s =
        SemanticData.fromJson(
              _comparison([
                {'text': 'tách hạt rắn', 'sourceBlockId': 'blk-cell-9'},
                null,
              ]),
            )
            as ComparisonSemantic;
    final cells = s.dimensions.single.cells;
    expect(cells[0].sourceBlockId, 'blk-cell-9');
    expect(cells[0].grounding, ValueGrounding.cellStated);
    expect(cells[1].grounding, ValueGrounding.inheritedFromEntity);
  });

  test('§8 fail-closed: ô có sourceBlockId RỖNG ⇒ cả bảng bị từ chối', () {
    final s = SemanticData.fromJson(
      _comparison([
        {'text': 'tách hạt rắn', 'sourceBlockId': ''},
        null,
      ]),
    );
    expect(s, isNull, reason: 'nguồn rỗng không phải nguồn');
  });

  test('§8 fail-closed: ô kiểu lạ (số) ⇒ cả bảng bị từ chối', () {
    expect(SemanticData.fromJson(_comparison([42, null])), isNull);
  });

  test('§8 số ô phải khớp số hàng — thiếu ô là bảng sai, không phải bảng thiếu',
      () {
    expect(SemanticData.fromJson(_comparison(['chỉ một ô'])), isNull);
  });

  test('tương thích ngược: `values` vẫn trả về chữ cho các View đang đọc nó',
      () {
    final s =
        SemanticData.fromJson(_comparison(['tách hạt rắn', null]))
            as ComparisonSemantic;
    expect(s.dimensions.single.values, ['tách hạt rắn', null]);
  });

  test('round-trip: đọc lại toJson giữ NGUYÊN nguồn của từng ô', () {
    final first =
        SemanticData.fromJson(
              _comparison([
                {'text': 'tách hạt rắn', 'sourceBlockId': 'blk-cell-9'},
                'bay hơi',
              ]),
            )
            as ComparisonSemantic;
    final again =
        SemanticData.fromJson(first.toJson()) as ComparisonSemantic;
    expect(again.dimensions.single.cells[0].sourceBlockId, 'blk-cell-9');
    expect(again.dimensions.single.cells[0].grounding, ValueGrounding.cellStated);
    expect(again.dimensions.single.cells[1].sourceBlockId, 'blk-row-2');
    expect(
      again.dimensions.single.cells[1].grounding,
      ValueGrounding.inheritedFromEntity,
    );
  });
}
