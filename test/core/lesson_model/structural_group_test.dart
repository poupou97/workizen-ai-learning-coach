/// ⭐⭐ ROUND 7 (WS-S) — MỘT CẤU TRÚC BỊ CẮT XÉN TRỞ NÊN ĐẾM ĐƯỢC, VÀ KHÔNG ĐỌC ĐƯỢC.
///
/// Lỗi số 8 của vòng 5: giữ lại MỘT phương án của câu trắc nghiệm khiến câu ĐƯỢC
/// PHỤC VỤ trở nên SAI, chứ không phải ngắn đi. Vòng 5 và vòng 6 đều ghi lại rằng
/// lớp lỗi ấy **vẫn mở trên đường bài học** — đường mà một đứa trẻ thật sự đọc.
///
/// `BlockGroup` là bước làm cho nó **nhìn thấy và đếm được ở tầng mô hình**. Nó
/// KHÔNG phải bước làm cho nó phục vụ được. Mỗi test dưới đây là một cánh cửa mà
/// qua đó «biết có một thành viên bị thiếu» có thể biến thành «đọc được thành
/// viên ấy», hoặc thành «tài liệu tự khai là lành lặn». Không cửa nào mở.
library;

import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';

const _book = '07-sgk-khoa-hoc-tu-nhien-7';
const _gid = '$_book:p032:g-qo-005';

Map<String, Object?> _ref(String id) => {
  'book': _book,
  'pagePdf': 32,
  'pagePrinted': 31,
  'bbox': [0.1, 0.3, 0.7, 0.03],
  'blockId': id,
};

Map<String, Object?> _group({int members = 5, int withheld = 4, String kind = 'question_options'}) => {
  'id': _gid,
  'kind': kind,
  'members': members,
  'withheldMembers': withheld,
};

Map<String, Object?> _served(String id, {Map<String, Object?>? group}) => {
  'type': 'question',
  'id': id,
  'sourceRef': _ref(id),
  'trust': 'trustedStructuredLesson',
  'text': '[MẪU] Câu hỏi mẫu gồm các thứ:',
  'relations': {'order': 5, 'group': ?group},
};

Map<String, Object?> _withheld(String id, {Map<String, Object?>? group}) => {
  'type': 'withheld',
  'id': id,
  'sourceRef': _ref(id),
  'trust': 'withheld',
  'reasons': ['unknown_role:option'],
  'status': 'WITHHELD',
  'relations': {'order': 6, 'group': ?group},
};

Map<String, Object?> _docJson(List<Map<String, Object?>> blocks) => {
  'schema': LessonDocument.schemaV1,
  'book': _book,
  'bookTitle': 'KHTN 7',
  'subject': 'KHTN',
  'grade': 7,
  'lesson': 4,
  'title': '[MẪU] BÀI MẪU',
  'provenance': {
    'trust': 'trustedStructuredLesson',
    'book': _book,
    'pagePdfStart': 32,
    'pagePdfEnd': 32,
    'generator': 'tool/corpus/tsl_to_lesson_document.py@v1',
    'sourcePipeline': 'tc2-p1',
    'sdmVersion': 'sdm-v2',
    'distribution': 'internal-research-only (Founder D4)',
    'auditStatus': 'notAudited',
    'answerKeysIncluded': false,
  },
  'evidencePolicy': 'none',
  'licence': 'internalResearchOnly',
  'blocks': blocks,
  'semantic': <Object?>[],
  'chapters': <Object?>[],
};

/// Hình dạng thật của nhóm trắc nghiệm DUY NHẤT trong kho: một câu dẫn được phục
/// vụ và bốn phương án bị giữ lại — bị giữ lại vì app KHÔNG CÓ KIỂU, chứ không
/// phải vì chữ đáng ngờ.
LessonDocument _mutilatedDoc() => LessonDocument.fromJson(
  _docJson([
    _served('$_book:p032:tc2-p1:005', group: _group()),
    for (var i = 6; i <= 9; i++)
      _withheld('$_book:p032:tc2-p1:${i.toString().padLeft(3, '0')}', group: _group()),
  ]),
)!;

void main() {
  group('BlockGroup — fail-closed, và không mang chữ', () {
    test('đọc được một nhóm hợp lệ, và CHỈ bốn con số', () {
      final g = BlockGroup.fromJson(_group());
      expect(g, isNotNull);
      expect(g!.id, _gid);
      expect(g.kind, 'question_options');
      expect(g.members, 5);
      expect(g.withheldMembers, 4);
      expect(g.hasWithheldMember, isTrue);
      expect(g.isComplete, isFalse);
      expect(g.toJson().keys.toSet(), {'id', 'kind', 'members', 'withheldMembers'});
    });

    test('⭐ mọi khai báo bất khả thi bị TỪ CHỐI, không bị làm tròn thành lành', () {
      final bad = <Map<String, Object?>>[
        {..._group(), 'id': ''},
        {..._group(), 'kind': ''},
        {..._group(), 'members': 0},
        {..._group(), 'withheldMembers': -1},
        // nhiều thành viên bị giữ lại hơn số thành viên: một nhóm nói dối về
        // chính nó, và cách hỏng an toàn là KHÔNG có nhóm nào.
        {..._group(), 'members': 2, 'withheldMembers': 3},
        {..._group()}..remove('members'),
        {..._group(), 'members': 'nhiều'},
      ];
      for (final j in bad) {
        expect(BlockGroup.fromJson(j), isNull, reason: 'nhóm bậy lọt qua: $j ⇒ đỏ');
      }
      expect(BlockGroup.fromJson(null), isNull);
      expect(BlockGroup.fromJson('question_options'), isNull);
    });

    test('⭐⭐ nhóm KHÔNG có đường nào mang chữ của thành viên bị giữ lại', () {
      // Một khoá chữ thêm vào không được trở thành một trường đọc được: kiểu
      // chỉ có bốn trường, và JSON đi ra chỉ có bốn trường.
      final g = BlockGroup.fromJson({..._group(), 'text': 'C. Kim loại và khí hiếm'});
      expect(g, isNotNull);
      expect(jsonEncode(g!.toJson()).contains('Kim loại'), isFalse);
    });
  });

  group('LessonDocument — cấu trúc bị cắt xén đếm được', () {
    test('⭐⭐ câu trắc nghiệm mất phương án ĐƯỢC ĐẾM là cấu trúc bị cắt xén', () {
      final doc = _mutilatedDoc();
      expect(doc.hasGroupMeasurement, isTrue);
      expect(doc.structuralGroups.length, 1);
      expect(doc.mutilatedGroups.map((g) => g.id), [_gid]);
      expect(doc.hasMutilatedStructure, isTrue);
      // và không có block nào ở đây đọc được: bốn phương án vẫn không có chữ
      final withheldBlocks = doc.blocks.whereType<WithheldBlock>();
      expect(withheldBlocks.length, 4);
      expect(jsonEncode(doc.toJson()).contains('Kim loại'), isFalse);
    });

    test('⭐ nhóm còn nguyên KHÔNG bị đếm là cắt xén', () {
      final doc = LessonDocument.fromJson(
        _docJson([
          _served('$_book:p032:tc2-p1:005', group: _group(members: 2, withheld: 0)),
          _served('$_book:p032:tc2-p1:006', group: _group(members: 2, withheld: 0)),
        ]),
      )!;
      expect(doc.hasGroupMeasurement, isTrue);
      expect(doc.mutilatedGroups, isEmpty);
    });

    test('⭐ nhóm bị giữ lại HOÀN TOÀN không phải cắt xén — đó chính là luật', () {
      // Không thành viên nào được phục vụ ⇒ không có gì bị dạy sai. Đây là trạng
      // thái mà luật «cả nhóm hoặc không gì cả» tạo ra, và nó phải đọc là LÀNH.
      final doc = LessonDocument.fromJson(
        _docJson([
          for (var i = 5; i <= 9; i++)
            _withheld('$_book:p032:tc2-p1:${i.toString().padLeft(3, '0')}',
                group: _group(members: 5, withheld: 5)),
        ]),
      )!;
      expect(doc.hasGroupMeasurement, isTrue);
      expect(doc.structuralGroups.length, 1);
      expect(doc.mutilatedGroups, isEmpty);
    });

    test('⭐⭐ KHÔNG ĐO khác KHÔNG CÓ: pack cũ không được đọc thành «lành lặn»', () {
      final doc = LessonDocument.fromJson(
        _docJson([
          _served('$_book:p032:tc2-p1:005'),
          _withheld('$_book:p032:tc2-p1:006'),
        ]),
      )!;
      expect(doc.hasGroupMeasurement, isFalse,
          reason: 'pack chưa mang phép đo nhóm mà tài liệu lại khai là đã đo ⇒ đỏ');
      expect(doc.mutilatedGroups, isEmpty);
      // `mutilatedGroups` rỗng ở đây KHÔNG phải phép đo. Ai đọc số 0 mà không
      // hỏi `hasGroupMeasurement` đang đọc một câu trả lời không tồn tại.
    });
  });

  group('Tuần tự hoá KHÔNG tẩy trắng xuất xứ', () {
    test('⭐⭐ đi một vòng lưu/đọc: nhóm KHÔNG BAO GIỜ lành thêm', () {
      // Vòng 5 bắt được một vòng lưu/đọc LÀM MẠNH nền tảng của nội dung. Test
      // này canh đúng thuộc tính đó cho nhóm: sau mỗi vòng, số thành viên bị giữ
      // lại không được GIẢM, và một nhóm bị cắt xén không được thành nguyên vẹn.
      var doc = _mutilatedDoc();
      final firstWithheld = doc.structuralGroups[_gid]!.withheldMembers;
      final firstMutilated = doc.mutilatedGroups.length;
      for (var round = 0; round < 3; round++) {
        final again = LessonDocument.fromJson(
          jsonDecode(jsonEncode(doc.toJson())) as Map<String, Object?>,
        );
        expect(again, isNotNull, reason: 'vòng $round: tài liệu không đọc lại được ⇒ đỏ');
        doc = again!;
        expect(doc.structuralGroups[_gid], isNotNull,
            reason: 'vòng $round: nhóm biến mất khi lưu ⇒ đỏ');
        expect(doc.structuralGroups[_gid]!.withheldMembers,
            greaterThanOrEqualTo(firstWithheld),
            reason: 'vòng $round: nhóm tự nhiên «lành» thêm ⇒ đỏ');
        expect(doc.mutilatedGroups.length, greaterThanOrEqualTo(firstMutilated),
            reason: 'vòng $round: cắt xén biến mất khi lưu ⇒ đỏ');
        expect(doc.hasGroupMeasurement, isTrue,
            reason: 'vòng $round: phép đo bị tẩy trắng thành «chưa đo» ⇒ đỏ');
      }
    });

    test('⭐⭐ không block nào bị giữ lại mọc ra chữ khi đi một vòng', () {
      final doc = _mutilatedDoc();
      final again = LessonDocument.fromJson(
        jsonDecode(jsonEncode(doc.toJson())) as Map<String, Object?>,
      )!;
      expect(again.blocks.whereType<WithheldBlock>().length, 4);
      for (final b in again.blocks) {
        if (b is WithheldBlock) {
          expect(b.trust.mayCarryText, isFalse);
        }
      }
    });
  });

  group('Mã máy của nhóm KHÔNG BAO GIỜ là lời cho trẻ', () {
    test('⭐ id và kind là chuỗi máy — test này ghim rằng chúng nằm ở xuất xứ', () {
      // `no_machine_ids_test.dart` đi khắp UI và cấm mọi mã máy hiện ra. Nhóm
      // mang chính xác cái hình dạng ấy (`07-sgk-…:p032:g-qo-005`), nên nếu một
      // ngày nào đó có widget vẽ nó thì test kia phải đỏ. Ở đây chỉ ghim rằng
      // mô hình KHÔNG cung cấp một chuỗi «lời trẻ» nào cho nhóm — không có
      // `groupLabel`, không có `kindForChild` — để không ai vô tình vẽ nó.
      final g = BlockGroup.fromJson(_group())!;
      expect(g.id.contains(':g-qo-'), isTrue);
      expect(g.kind, 'question_options');
    });
  });
}
