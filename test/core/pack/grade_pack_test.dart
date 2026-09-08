/// CÀI PACK HÌNH THEO LỚP.
///
/// App hỗ trợ lớp 1–12, trẻ dùng một lớp. Gói cả 12 pack (332 MB) vào APK là
/// bắt mọi máy mang 11 lớp không ai mở. Mỗi test dưới đây là một ràng buộc
/// Founder nêu khi chọn phương án cài-lúc-chạy.
library;

import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:crypto/crypto.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/pack/grade_pack.dart';

late Directory _root;
String get _src => '${_root.path}/incoming';
String get _dst => '${_root.path}/packs';

Uint8List _body([String s = 'PACK-BYTES-6']) =>
    Uint8List.fromList(utf8.encode(s));

/// Đặt một pack vào NGUỒN. `corrupt` = manifest nói một đằng, tệp một nẻo.
void _stage(int grade, {Uint8List? data, bool corrupt = false, String? version}) {
  final d = data ?? _body();
  Directory(_src).createSync(recursive: true);
  File('$_src/figures-g$grade.db').writeAsBytesSync(d);
  final real = sha256.convert(d).toString();
  File('$_src/figures-g$grade.manifest.json').writeAsStringSync(jsonEncode({
    'grade': grade,
    'file': 'figures-g$grade.db',
    'version': version ?? 'g$grade-${real.substring(0, 12)}',
    'size': d.length,
    'sha256': corrupt ? 'f' * 64 : real,
  }));
}

GradePackInstaller _installer() => GradePackInstaller(
    source: DirectoryPackSource(_src), dir: _dst);

void main() {
  setUp(() {
    _root = Directory.systemTemp.createTempSync('gradepack');
  });
  tearDown(() => _root.deleteSync(recursive: true));

  group('cài', () {
    test('cài đúng lớp được yêu cầu, KHÔNG kéo cả 12 lớp', () async {
      _stage(6);
      _stage(7);
      expect(await _installer().install(6), InstallResult.installed);
      expect(File('$_dst/figures-g6.db').existsSync(), isTrue);
      expect(File('$_dst/figures-g7.db').existsSync(), isFalse,
          reason: 'lớp không ai mở thì không được tải');
    });

    test('nguồn chưa có pack ⇒ notAvailable, KHÔNG phải lỗi', () async {
      expect(await _installer().install(6), InstallResult.notAvailable);
      expect(Directory(_dst).existsSync(), isFalse);
    });

    test('đã đúng phiên bản ⇒ không tải lại', () async {
      _stage(6);
      expect(await _installer().install(6), InstallResult.installed);
      expect(await _installer().install(6), InstallResult.alreadyInstalled);
    });

    test('nội dung đổi ⇒ phiên bản đổi ⇒ cài bản mới', () async {
      _stage(6);
      await _installer().install(6);
      _stage(6, data: _body('PACK-BYTES-6-V2'));
      expect(await _installer().install(6), InstallResult.installed);
      expect(File('$_dst/figures-g6.db').readAsStringSync(),
          'PACK-BYTES-6-V2');
    });
  });

  group('fail closed', () {
    test('băm sai ⇒ KHÔNG kích hoạt', () async {
      _stage(6, corrupt: true);
      expect(await _installer().install(6), InstallResult.verifyFailed);
      expect(File('$_dst/figures-g6.db').existsSync(), isFalse,
          reason: 'pack không kiểm được thì không được nằm ở chỗ app sẽ mở');
    });

    test('băm sai KHÔNG phá bản đang dùng', () async {
      // Bản cũ chạy tốt phải sống sót qua một lần cài hỏng.
      _stage(6);
      await _installer().install(6);
      final good = File('$_dst/figures-g6.db').readAsStringSync();
      _stage(6, data: _body('HỎNG'), corrupt: true, version: 'g6-moi');
      expect(await _installer().install(6), InstallResult.verifyFailed);
      expect(File('$_dst/figures-g6.db').readAsStringSync(), good);
      expect(await _installer().installedVersion(6), isNot('g6-moi'));
    });

    test('kích thước lệch manifest ⇒ verifyFailed (tệp cụt)', () async {
      _stage(6);
      final m = jsonDecode(
          File('$_src/figures-g6.manifest.json').readAsStringSync()) as Map;
      m['size'] = (m['size'] as int) + 10;
      File('$_src/figures-g6.manifest.json').writeAsStringSync(jsonEncode(m));
      expect(await _installer().install(6), InstallResult.verifyFailed);
    });

    test('mất tệp pack mà còn manifest ⇒ fetchFailed', () async {
      _stage(6);
      File('$_src/figures-g6.db').deleteSync();
      expect(await _installer().install(6), InstallResult.fetchFailed);
    });

    test('KHÔNG để lại nửa pack ở đường dẫn app sẽ mở', () async {
      _stage(6, corrupt: true);
      await _installer().install(6);
      final left = Directory(_dst).existsSync()
          ? Directory(_dst).listSync().map((e) => e.path).toList()
          : <String>[];
      expect(left.where((p) => p.endsWith('.part')), isEmpty);
      expect(left.where((p) => p.endsWith('figures-g6.db')), isEmpty);
    });
  });

  group('manifest', () {
    test('manifest hỏng ⇒ null, không đoán', () {
      for (final bad in [
        '{',
        '{"grade":6}',
        '{"grade":0,"file":"a.db","version":"v","size":1,"sha256":"${'a' * 64}"}',
        '{"grade":6,"file":"a.db","version":"v","size":0,"sha256":"${'a' * 64}"}',
        '{"grade":6,"file":"a.db","version":"v","size":1,"sha256":"abc"}',
      ]) {
        expect(GradePackManifest.parse(bad), isNull, reason: bad);
      }
    });

    test('tên tệp là TÊN, không phải đường dẫn', () {
      // Manifest nói `../../x` sẽ ghi ra ngoài thư mục pack.
      for (final f in ['../evil.db', 'a/b.db', '..']) {
        final raw = jsonEncode({
          'grade': 6, 'file': f, 'version': 'v', 'size': 1,
          'sha256': 'a' * 64,
        });
        expect(GradePackManifest.parse(raw), isNull, reason: f);
      }
    });

    test('manifest khai lớp khác ⇒ không cài', () async {
      _stage(6);
      final m = jsonDecode(
          File('$_src/figures-g6.manifest.json').readAsStringSync()) as Map;
      m['grade'] = 7;
      File('$_src/figures-g6.manifest.json').writeAsStringSync(jsonEncode(m));
      expect(await _installer().install(6), InstallResult.notAvailable);
    });
  });

  test('chỉ ghi trong thư mục pack — KHÔNG đụng dữ liệu học', () async {
    final learner = File('${_root.path}/learner.db')..writeAsStringSync('HỒ SƠ');
    _stage(6);
    await _installer().install(6);
    expect(learner.readAsStringSync(), 'HỒ SƠ');
    expect(Directory(_dst).listSync().map((e) => e.path.split('/').last).toSet(),
        {'figures-g6.db', 'figures-g6.installed.json'});
  });
}
