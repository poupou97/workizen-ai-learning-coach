/// ⭐⭐ WAL-213 — QUAN HỆ THAY THẾ, PHÍA APP.
///
/// Vòng 7 đo: **một chữ số phục hồi được KHÔNG trở thành một block đã sửa**
/// (`10 → 10, Δ 0`), vì bộ nhận dạng **THÊM** một quan sát vào chỗ mà quan sát
/// bị phá phải bị **THAY THẾ**. Từ đó một block giữ hai đoạn chữ mâu thuẫn và
/// không có gì nói cái nào là chữ của nó.
///
/// Mỗi test dưới đây là MỘT CÁNH CỬA mà qua đó một trong hai đoạn chữ đó — hoặc
/// bản thân mâu thuẫn — có thể tới màn hình của trẻ, hoặc có thể biến mất khỏi
/// dấu vết. Không cửa nào mở.
///
/// Dữ liệu ở đây là **cấu trúc thật, không phải chữ SGK**: bản chiếu cấp block
/// theo thiết kế không mang giá trị nào của bên nào (D4), nên một test đúng
/// không cần một chữ nào của sách.
library;

import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/repair_record.dart';

const _book = '04-sgk-toan-4-tap-hai';
const _bid = '$_book:p083:tc2-p3:010';

/// Hình dạng ĐO ĐƯỢC trên Bài 61: một quan hệ giải quyết được (FULL) và một
/// quan hệ KHÔNG (PARTIAL ⇒ CONFLICT). 4 và 13 trong quần thể thật.
Map<String, Object?> supersedesJson({
  String disposition = 'SUPERSEDED',
  String coverage = 'FULL',
  bool resolved = true,
  int supersededObservations = 2,
  Map<String, Object?> extra = const {},
}) => {
  'supersessionId': '$_bid#$_book:p083:r011#71fb62460b441916',
  'disposition': disposition,
  'supersededObservations': supersededObservations,
  'supersedingEngine': 'apple-vision-crop-v1',
  'coverage': coverage,
  'agreeingScales': 2,
  'stacked': true,
  'resolved': resolved,
  'changed': true,
  'servable': false,
  ...extra,
};

Map<String, Object?> conflictJson() => supersedesJson(
  disposition: 'CONFLICT',
  coverage: 'PARTIAL',
  resolved: false,
);

Map<String, Object?> repairJson({Object? supersedes}) => {
  'repairId': '$_bid#recognition.recrop-supersede-v1#5c31cd1c',
  'disposition': 'VALIDATED_REPAIR',
  'failureClass': 'FRACTION_STRUCTURE',
  'method': 'recognition.recrop-supersede-v1',
  'repairVersion': 'repair-v1/recognition.recrop-supersede-v1',
  'validatorId': 'wal213.region-stacking-v1',
  'validatorVersion': 'v1',
  'verdict': 'validated',
  'supportingLayers': ['B', 'F'],
  'changed': true,
  'servable': false,
  'structuredKind': null,
  'caps': <String>['trust_gate:founder_decision_absent'],
  'supersedes': ?supersedes,
};

Map<String, Object?> sourceRef() => {
  'book': _book,
  'pagePdf': 83,
  'pagePrinted': 81,
  'bbox': [0.07, 0.06, 0.83, 0.08],
  'blockId': _bid,
};

Map<String, Object?> withheldBlockJson({Object? repair}) => {
  'type': 'withheld',
  'id': _bid,
  'sourceRef': sourceRef(),
  'trust': 'withheld',
  'reasons': ['unread:unreadable_region'],
  'status': 'WITHHELD',
  'repair': ?repair,
  if (repair != null) 'disposition': 'VALIDATED_REPAIR',
};

Map<String, Object?> docJson(List<Map<String, Object?>> blocks) => {
  'schema': LessonDocument.schemaV1,
  'book': _book,
  'bookTitle': 'Toán 4 tập hai',
  'subject': 'Toán',
  'grade': 4,
  'lesson': 61,
  'title': 'BÀI 61',
  'provenance': {
    'trust': 'trustedStructuredLesson',
    'book': _book,
    'pagePdfStart': 81,
    'pagePdfEnd': 83,
    'generator': 'tool/corpus/tsl_to_lesson_document.py@v1',
    'sourcePipeline': 'tc2-p3',
    'sdmVersion': 'sdm-v3',
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

void main() {
  group('SupersessionRef — ĐẾM ĐƯỢC, KHÔNG ĐỌC ĐƯỢC', () {
    test('đọc được quan hệ đã giải quyết, và nó KHÔNG phục vụ được', () {
      final s = SupersessionRef.fromJson(supersedesJson())!;
      expect(s.disposition, RepairDisposition.superseded);
      expect(s.coverage, 'FULL');
      expect(s.resolved, isTrue);
      expect(s.supersededObservations, 2);
      expect(s.supersedingEngine, 'apple-vision-crop-v1');
      expect(s.servable, isFalse);
    });

    test('⭐ quan hệ KHÔNG giải quyết được là CONFLICT và đóng an toàn', () {
      final s = SupersessionRef.fromJson(conflictJson())!;
      expect(s.disposition, RepairDisposition.conflict);
      expect(s.coverage, 'PARTIAL');
      expect(s.resolved, isFalse);
    });

    test('⭐⭐ KHÔNG trường nào mang chữ, của bên nào', () {
      final s = SupersessionRef.fromJson(supersedesJson())!;
      // Toàn bộ khoá là một danh sách CHO PHÉP — không có chỗ cho một đoạn chữ.
      expect(s.toJson().keys.toSet(), {
        'supersessionId',
        'disposition',
        'supersededObservations',
        'supersedingEngine',
        'coverage',
        'agreeingScales',
        'stacked',
        'resolved',
        'changed',
        'servable',
      });
    });

    test('⭐⭐ mọi cửa mang giá trị đều bị đóng', () {
      for (final k in [
        'supersededValue',
        'supersedingValue',
        'supersededText',
        'superseded',
        'superseding',
        'text',
        'value',
        'proposedValue',
      ]) {
        expect(
          SupersessionRef.fromJson(supersedesJson(extra: {k: '8/14'})),
          isNull,
          reason: 'khoá $k phải làm bản ghi bị từ chối',
        );
      }
    });

    test('⭐⭐ TRUSTED và mọi disposition khác đều bị từ chối', () {
      for (final d in [
        'TRUSTED',
        'VALIDATED_REPAIR',
        'ORIGINAL_OBSERVATION',
        'HUMAN_VERIFIED',
        'khong-phai-mot-trang-thai',
      ]) {
        expect(
          SupersessionRef.fromJson(supersedesJson(disposition: d)),
          isNull,
          reason: d,
        );
      }
    });

    test('⭐ servable = true ⇒ từ chối; getter không đặt được từ JSON', () {
      expect(
        SupersessionRef.fromJson(supersedesJson(extra: {'servable': true})),
        isNull,
      );
      final s = SupersessionRef.fromJson(supersedesJson())!;
      expect(s.toJson()['servable'], isFalse);
    });

    test('⭐⭐ hình học và trạng thái phải KHỚP — không có PARTIAL đã giải quyết', () {
      expect(
        SupersessionRef.fromJson(
          supersedesJson(coverage: 'PARTIAL', resolved: true),
        ),
        isNull,
        reason: 'PARTIAL không bao giờ là đã giải quyết',
      );
      expect(
        SupersessionRef.fromJson(
          supersedesJson(disposition: 'CONFLICT', coverage: 'FULL'),
        ),
        isNull,
        reason: 'FULL + CONFLICT là hai lời nói mâu thuẫn',
      );
      expect(
        SupersessionRef.fromJson(
          supersedesJson(coverage: 'NONE', resolved: false, disposition: 'CONFLICT'),
        ),
        isNotNull,
      );
    });

    test('⭐ 0 quan sát bị thay thế KHÔNG phải một quan hệ thay thế', () {
      expect(
        SupersessionRef.fromJson(supersedesJson(supersededObservations: 0)),
        isNull,
        reason: 'không thay thế gì thì là THÊM, không phải THAY',
      );
    });

    test('vòng lưu–đọc không đổi gì', () {
      final s = SupersessionRef.fromJson(supersedesJson())!;
      final again = SupersessionRef.fromJson(s.toJson())!;
      expect(again.toJson(), s.toJson());
      expect(SupersessionRef.notStrengthened(s.toJson(), again.toJson()), isTrue);
    });

    test('⭐⭐ vòng lưu–đọc KHÔNG được làm mạnh lên', () {
      final before = SupersessionRef.fromJson(conflictJson())!.toJson();
      for (final entry in <String, Object?>{
        'disposition': 'SUPERSEDED',
        'resolved': true,
        'servable': true,
        'coverage': 'FULL',
      }.entries) {
        expect(
          SupersessionRef.notStrengthened(before, {
            ...before,
            entry.key: entry.value,
          }),
          isFalse,
          reason: entry.key,
        );
      }
    });

    test('⭐⭐ MẤT một quan sát bị thay thế là mâu thuẫn trở thành vô hình', () {
      final before = SupersessionRef.fromJson(supersedesJson())!.toJson();
      expect(
        SupersessionRef.notStrengthened(before, {
          ...before,
          'supersededObservations': 1,
        }),
        isFalse,
      );
    });

    test('KIỂM ĐỘT BIẾN: guard phải CHẤP NHẬN một vòng lưu–đọc trung thực', () {
      final before = SupersessionRef.fromJson(conflictJson())!.toJson();
      expect(
        SupersessionRef.notStrengthened(before, {...before, 'stacked': false}),
        isTrue,
        reason: 'một guard nói không với mọi thứ không chứng minh gì',
      );
    });
  });

  group('ValidatedRepairRef mang quan hệ thay thế', () {
    test('bản sửa vòng 5/6 KHÔNG có quan hệ nào — null, không phải rỗng', () {
      final r = ValidatedRepairRef.fromJson(repairJson())!;
      expect(r.supersedes, isNull);
    });

    test('bản sửa từ bộ nhận dạng MANG quan hệ, và vẫn không tin được', () {
      final r = ValidatedRepairRef.fromJson(
        repairJson(supersedes: supersedesJson()),
      )!;
      expect(r.supersedes, isNotNull);
      expect(r.supersedes!.supersededObservations, 2);
      expect(r.servable, isFalse);
      expect(r.disposition, RepairDisposition.validatedRepair);
      expect(r.cappedByTrustGate, isTrue);
    });

    test('⭐⭐ quan hệ HỎNG ⇒ TỪ CHỐI CẢ BẢN GHI, không rơi xuống «không có»', () {
      final r = ValidatedRepairRef.fromJson(
        repairJson(supersedes: supersedesJson(disposition: 'TRUSTED')),
      );
      expect(r, isNull);
    });

    test('⭐⭐ MẤT quan hệ qua vòng lưu–đọc là mất mâu thuẫn', () {
      final before = ValidatedRepairRef.fromJson(
        repairJson(supersedes: conflictJson()),
      )!.toJson();
      final after = {...before, 'supersedes': null};
      expect(ValidatedRepairRef.notStrengthened(before, after), isFalse);
      expect(ValidatedRepairRef.notStrengthened(before, before), isTrue);
    });

    test('⭐⭐ quan hệ mạnh lên bên trong bản sửa cũng bị bắt', () {
      final before = ValidatedRepairRef.fromJson(
        repairJson(supersedes: conflictJson()),
      )!.toJson();
      final after = {
        ...before,
        'supersedes': {
          ...conflictJson(),
          'disposition': 'SUPERSEDED',
          'coverage': 'FULL',
          'resolved': true,
        },
      };
      expect(ValidatedRepairRef.notStrengthened(before, after), isFalse);
    });
  });

  group('LessonDocument', () {
    test('⭐⭐ vùng bị giữ lại MANG quan hệ thay thế, vẫn KHÔNG CÓ CHỮ', () {
      final d = LessonDocument.fromJson(
        docJson([withheldBlockJson(repair: repairJson(supersedes: supersedesJson()))]),
      )!;
      final b = d.blocks.single as WithheldBlock;
      expect(b.hasValidatedRepair, isTrue);
      expect(b.repair!.supersedes!.coverage, 'FULL');
      expect(d.trustedRepairCount, 0);
      final encoded = jsonEncode(d.toJson());
      for (final door in ['supersededValue', 'supersedingValue', 'proposedValue']) {
        expect(encoded.contains(door), isFalse, reason: door);
      }
    });

    test('⭐⭐ block PHỤC VỤ mang quan hệ thay thế ⇒ TỪ CHỐI CẢ TÀI LIỆU', () {
      final served = {
        'type': 'paragraph',
        'id': _bid,
        'sourceRef': sourceRef(),
        'trust': 'trustedStructuredLesson',
        'text': 'Một dòng bất kỳ.',
        'repair': repairJson(supersedes: supersedesJson()),
      };
      expect(LessonDocument.fromJson(docJson([served])), isNull);
    });
  });
}
