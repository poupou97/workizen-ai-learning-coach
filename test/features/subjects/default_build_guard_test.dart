/// ⭐⭐ WAL-210 item F — DEFAULT-BUILD GUARD (audit top-gap #3 «no build
/// provenance»: the packs on this Mac are the WAL-206 *variant* build; any APK
/// built here ships experimental content indistinguishably from a default build).
///
/// Hai lớp:
/// 1. FIXTURE (CI luôn chạy): parser LOẠI mục `source: pattern-router*` khi
///    pack không tự khai `buildProvenance.experimental == true`; đếm được.
/// 2. FILE THẬT (skip khi máy chưa có pack): MỌI pack trên máy phải khai
///    provenance, KHÔNG experimental, và 0 mục router. Trên pack dựng TRƯỚC
///    WAL-210 test này ĐỎ — đúng ý: máy này chưa được phép làm bằng chứng
///    thiết bị cho tới khi lane Python dựng lại pack.
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';

const _book = '06-sgk-khoa-hoc-tu-nhien-6';

String _pack({String? provenance}) => '''
{"grade":6,"version":"lesson-index-v2",${provenance == null ? '' : '$provenance,'}
 "subjects":{"KHTN":[{"sourceDocumentId":"$_book","volume":null,
   "lessons":[{"no":17,"title":"Tách chất khỏi hỗn hợp","pageStart":60},
              {"no":18,"title":"Tế bào","pageStart":64}]}]},
 "tvReadings":[
   {"book":"$_book","lesson":17,"page":62,"source":"pattern-router-v2-layout",
    "passage":"Tách dầu ăn khỏi nước…","questions":[{"prompt":"2. Tại sao?","page":62}]},
   {"book":"$_book","lesson":18,"page":65,
    "passage":"Tế bào là đơn vị cơ bản…","questions":[{"prompt":"1. Tế bào là gì?","page":65}]}],
 "tvWritings":[
   {"book":"$_book","lesson":17,"page":63,"source":"pattern-router-v1","prompt":"Viết…"}],
 "khoaExperiments":[
   {"subject":"KHTN","book":"$_book","lesson":17,"page":62,"source":"pattern-router-v2-layout",
    "title":"Tách dầu ăn khỏi nước","chuanBi":"phễu chiết","tienHanh":["Rót hỗn hợp."]}]}
''';

String _prov(bool experimental) =>
    '"buildProvenance":{"schema":1,"experimental":$experimental,'
    '"packVersion":"g6-20260905T1200-abcdef12","flags":{"PATTERN_ROUTER":"${experimental ? 1 : 0}"}}';

void main() {
  group('fixture — guard theo provenance', () {
    test('⭐⭐ KHÔNG provenance ⇒ mọi mục router bị loại, đếm 3; mục mined giữ',
        () {
      final idx = LessonIndex.fromJsonString(_pack())!;
      expect(idx.buildProvenance, isNull);
      expect(idx.droppedRouterActivities, 3,
          reason: '1 bài đọc + 1 đề viết + 1 thí nghiệm mang source router');
      expect(idx.tvReadings.map((r) => r.lesson), [18],
          reason: 'bài đọc mined (không source) vẫn còn');
      expect(idx.tvWritings, isEmpty);
      expect(idx.khoaExperiments, isEmpty);
      expect(idx.activitiesFor(book: _book, lessonNo: 17), isEmpty,
          reason: '⭐⭐ Bài 17 chỉ có nội dung router ⇒ KHÔNG mở được trên bản '
              'mặc định — đây chính là cổng');
      expect(idx.activitiesFor(book: _book, lessonNo: 18), hasLength(1));
    });

    test('provenance khai experimental=false ⇒ vẫn loại (pack nói nó là bản '
        'mặc định thì không được chở nội dung thử nghiệm)', () {
      final idx = LessonIndex.fromJsonString(_pack(provenance: _prov(false)))!;
      expect(idx.buildProvenance!.experimental, isFalse);
      expect(idx.droppedRouterActivities, 3);
      expect(idx.activitiesFor(book: _book, lessonNo: 17), isEmpty);
    });

    test('⭐ provenance khai experimental=true ⇒ giữ đủ, không loại gì', () {
      final idx = LessonIndex.fromJsonString(_pack(provenance: _prov(true)))!;
      expect(idx.droppedRouterActivities, 0);
      expect(idx.tvReadings, hasLength(2));
      expect(idx.tvReadings.first.source, 'pattern-router-v2-layout',
          reason: 'source lộ ra để audit đọc được');
      expect(idx.tvWritings.single.source, 'pattern-router-v1');
      expect(idx.activitiesFor(book: _book, lessonNo: 17), hasLength(3));
    });

    test('openableLessonCount đếm BÀI (không đếm việc), theo guard', () {
      expect(LessonIndex.fromJsonString(_pack())!.openableLessonCount, 1);
      expect(
          LessonIndex.fromJsonString(_pack(provenance: _prov(true)))!
              .openableLessonCount,
          2);
    });
  });

  group('FILE THẬT — mọi pack trên máy phải là bản mặc định có provenance', () {
    for (var g = 1; g <= 12; g++) {
      test('lớp $g: buildProvenance khai, experimental=false, 0 mục router', () {
        final f = File('assets/pack/lesson-index-g$g.json');
        if (!f.existsSync()) {
          markTestSkipped('pack lớp $g chưa dựng trên máy này');
          return;
        }
        final idx = LessonIndex.fromJsonString(f.readAsStringSync());
        expect(idx, isNotNull);
        final p = idx!.buildProvenance;
        expect(p, isNotNull,
            reason: '⭐⭐ pack lớp $g không khai buildProvenance — pack dựng '
                'TRƯỚC WAL-210 hoặc builder chưa ghi (lane Python). Máy này '
                'chưa được làm bằng chứng thiết bị.');
        expect(p!.experimental, isFalse,
            reason: '⭐⭐ pack lớp $g tự khai là BẢN THỬ NGHIỆM — không được '
                'đóng vào APK mặc định');
        expect(idx.droppedRouterActivities, 0,
            reason: 'bản mặc định không được chứa mục router để guard phải loại');
        expect(
            idx.tvReadings.every(
                (r) => !(r.source?.startsWith('pattern-router') ?? false)),
            isTrue);
        expect(
            idx.tvWritings.every(
                (w) => !(w.source?.startsWith('pattern-router') ?? false)),
            isTrue);
      });
    }
  });
}
