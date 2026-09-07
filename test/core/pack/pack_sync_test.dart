/// ⭐⭐ VÒNG ĐỜI PACK — «xoá app data để lấy pack mới» KHÔNG phải cơ chế cập nhật.
///
/// Hai kịch bản bắt buộc: CÀI MỚI, và MÁY CŨ ĐANG GIỮ PACK CŨ → cập nhật app →
/// nhận pack mới. Cộng an toàn khi hỏng giữa chừng.
///
/// Không đụng `assets/pack/sam-stories.db` thật: tệp ấy không nằm trong git nên
/// một test đọc nó sẽ xanh ở máy dev và đỏ trên CI.
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/pack/pack_sync.dart';

late Directory _dir;
String get _db => '${_dir.path}/sam-stories.db';

PackIdLoader idOf(String id) =>
    (_) async => id;
PackBytesLoader bytesOf(String body) =>
    (_) async => Uint8List.fromList(utf8.encode(body));

void main() {
  setUp(() => _dir = Directory.systemTemp.createTempSync('pack-sync'));
  tearDown(() => _dir.deleteSync(recursive: true));

  test('CÀI MỚI — chưa có gì trên máy ⇒ chép pack và ghi danh tính', () async {
    final copied = await syncPack(
      _db,
      loadBytes: bytesOf('PACK-A'),
      loadId: idOf('v1:aaaa'),
    );
    expect(copied, isTrue);
    expect(File(_db).readAsStringSync(), 'PACK-A');
    expect(installedPackId(_db), 'v1:aaaa');
  });

  test(
    '⭐⭐ MÁY CŨ CÓ PACK CŨ ⇒ cập nhật app ⇒ NHẬN pack mới (không xoá data)',
    () async {
      // vòng 1: máy đã cài, đang giữ pack cũ
      await syncPack(
        _db,
        loadBytes: bytesOf('PACK-CU'),
        loadId: idOf('v1:aaaa'),
      );
      // một tệp dữ liệu học nằm cùng thư mục — phải SỐNG SÓT qua cập nhật
      final learner = File('${_dir.path}/learner.json')
        ..writeAsStringSync('{"na":1}');

      // vòng 2: APK mới mang pack mới
      final copied = await syncPack(
        _db,
        loadBytes: bytesOf('PACK-MOI'),
        loadId: idOf('v1:bbbb'),
      );

      expect(copied, isTrue, reason: 'pack mới KHÔNG tới được máy đã cài');
      expect(File(_db).readAsStringSync(), 'PACK-MOI');
      expect(installedPackId(_db), 'v1:bbbb');
      expect(
        learner.readAsStringSync(),
        '{"na":1}',
        reason: 'cập nhật pack đã đụng vào dữ liệu học',
      );
    },
  );

  test(
    'cùng danh tính ⇒ KHÔNG chép lại (mở app không ghi đĩa vô ích)',
    () async {
      await syncPack(
        _db,
        loadBytes: bytesOf('PACK-A'),
        loadId: idOf('v1:aaaa'),
      );
      var called = false;
      final copied = await syncPack(
        _db,
        loadId: idOf('v1:aaaa'),
        loadBytes: (k) async {
          called = true;
          return Uint8List(0);
        },
      );
      expect(copied, isFalse);
      expect(called, isFalse, reason: 'đã nạp cả pack dù không cần');
    },
  );

  test(
    '⭐ hỏng giữa chừng ⇒ pack CŨ còn nguyên, không để lại tệp cụt',
    () async {
      await syncPack(
        _db,
        loadBytes: bytesOf('PACK-CU'),
        loadId: idOf('v1:aaaa'),
      );
      await expectLater(
        syncPack(
          _db,
          loadId: idOf('v1:bbbb'),
          loadBytes: (_) async => throw const FileSystemException('đứt mạng'),
        ),
        throwsA(isA<FileSystemException>()),
      );
      // rename là điểm cam kết: chưa tới đó thì không có gì thay đổi
      expect(File(_db).readAsStringSync(), 'PACK-CU');
      expect(installedPackId(_db), 'v1:aaaa');
    },
  );

  test('thiếu sidecar (bản build cũ) ⇒ giữ pack cũ, không ghi đè mù', () async {
    await syncPack(_db, loadBytes: bytesOf('PACK-CU'), loadId: idOf('v1:aaaa'));
    final copied = await syncPack(
      _db,
      loadBytes: bytesOf('PACK-KHAC'),
      loadId: (_) async => throw Exception('không có sidecar'),
    );
    expect(copied, isFalse);
    expect(File(_db).readAsStringSync(), 'PACK-CU');
  });

  test(
    'thiếu sidecar VÀ chưa có pack ⇒ vẫn chép, nhưng không để marker nói dối',
    () async {
      final copied = await syncPack(
        _db,
        loadBytes: bytesOf('PACK-A'),
        loadId: (_) async => throw Exception('không có sidecar'),
      );
      expect(copied, isTrue);
      expect(File(_db).readAsStringSync(), 'PACK-A');
      expect(installedPackId(_db), isNull);
    },
  );

  test(
    'marker cũ không được sống sót khi pack mới không có danh tính',
    () async {
      await syncPack(
        _db,
        loadBytes: bytesOf('PACK-CU'),
        loadId: idOf('v1:aaaa'),
      );
      File(_db).deleteSync(); // giả lập máy mất tệp db nhưng còn marker
      await syncPack(
        _db,
        loadBytes: bytesOf('PACK-MOI'),
        loadId: (_) async => throw Exception('không có sidecar'),
      );
      expect(
        installedPackId(_db),
        isNull,
        reason: 'marker cũ đang nói dối về một tệp khác',
      );
    },
  );
}
