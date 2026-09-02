/// WAL-84 MỐC 1GB — bench pack SIDE-LOADED (không bundle asset: 1GB vào
/// APK là sai đường phân phối — ADR-006 pack tải rời). File được đẩy vào
/// documents dir bằng adb TRƯỚC khi chạy; không có file ⇒ SKIP nói thật.
/// Pack synthetic ×5 từ mốc 105MB (nhân bản cấu trúc — đo SCALE, ghi rõ).
library;

import 'dart:io';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:path_provider/path_provider.dart';
import 'package:sqlite3/sqlite3.dart';

void bench(String name, num value, [String unit = 'ms']) {
  // ignore: avoid_print
  print('PACKBENCH|$name|$value|$unit');
}

Future<double> timed(Future<void> Function() f) async {
  final sw = Stopwatch()..start();
  await f();
  return sw.elapsedMicroseconds / 1000.0;
}

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('pack 1GB side-loaded bench', (tester) async {
    // side-load: thử documents (run-as) rồi external-files (adb push được
    // không cần run-as — plan B khi run-as hỏng trên máy này).
    final dir = await getApplicationDocumentsDirectory();
    final candidates = [
      '${dir.path}/sam-synthetic-1gb.db',
      '/storage/emulated/0/Android/data/ai.workizen.learningcoach/files/'
          'sam-synthetic-1gb.db',
    ];
    final path = candidates.firstWhere(
        (p) => File(p).existsSync(),
        orElse: () => '');
    if (path.isEmpty) {
      markTestSkipped('side-load chưa đẩy pack 1GB — bỏ qua, nói thật');
      return;
    }
    bench('1gb_file_size', File(path).lengthSync() ~/ 1048576, 'MB');
    final sw = Stopwatch()..start();
    final db = sqlite3.open(path);
    bench('1gb_cold_open', sw.elapsedMicroseconds / 1000.0);
    final count = db.select('SELECT COUNT(*) c FROM unit').first['c'] as int;
    bench('1gb_unit_count', count, 'rows');

    const queries = [
      'quy đồng mẫu số', 'phân số', 'số thập phân', 'thể tích', 'diện tích',
      'so sánh', 'mẫu số chung', 'vận tốc', 'hình tam giác', 'trung bình cộng',
    ];
    final fts = <double>[];
    for (final q in queries) {
      fts.add(await timed(() async {
        db.select('SELECT rowid FROM unit_fts WHERE unit_fts MATCH ? LIMIT 10',
            ['"$q"']);
      }));
    }
    fts.sort();
    bench('1gb_fts_p50', fts[fts.length ~/ 2]);
    bench('1gb_fts_p95', fts[(fts.length * 0.95).floor()]);

    final mixed = await timed(() async {
      for (var i = 0; i < 20; i++) {
        db.select(
            'SELECT u.id FROM unit u JOIN unit_fts f ON u.rowid=f.rowid '
            "WHERE f.unit_fts MATCH ? AND (u.grade<5 OR (u.grade=5 AND "
            'u.vol=1 AND u.lesson<=6)) LIMIT 10',
            ['"quy đồng"']);
      }
    });
    bench('1gb_mixed_20x', mixed);

    // scope ĐÃ index từ lúc sinh pack (index là một phần định dạng từ mốc 2)
    final scope = await timed(() async {
      for (var i = 0; i < 20; i++) {
        db.select(
            'SELECT id FROM unit WHERE (grade<5) OR (grade=5 AND vol=1 AND '
            'lesson<=?) ORDER BY grade, vol, lesson LIMIT 50', [6 + i]);
      }
    });
    bench('1gb_graph_scope_indexed_20x', scope);
    db.dispose();
    expect(count, greaterThan(1800000));
  });
}
