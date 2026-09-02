/// WAL-84 — PACK BENCH trên THIẾT BỊ THẬT (chỉ thị Founder §9).
///
/// Đo pipeline trên pack 1,87MB (2.584 unit). ⚠️ LIMITATION GHI THẬT:
/// «1,87MB chạy tốt» KHÔNG suy rộng thành «full K-12 pack chạy tốt» —
/// benchmark lại ở mốc 100MB/500MB/1GB+ khi có pack lớn.
/// Kết quả in dòng PACKBENCH| để host gom từ log.
library;

import 'dart:io';
import 'package:flutter/services.dart';
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

  testWidgets('pack bench on-device', (tester) async {
    final dir = await getApplicationDocumentsDirectory();
    final path = '${dir.path}/sam-units.db';

    // ── nạp pack từ asset (mô phỏng first-install copy) ──
    final copyMs = await timed(() async {
      final data = await rootBundle.load('assets/pack/sam-units.db');
      await File(path).writeAsBytes(data.buffer.asUint8List(), flush: true);
    });
    bench('asset_copy_1.87MB', copyMs);

    // ── COLD OPEN: open + first query ──
    final sw = Stopwatch()..start();
    var db = sqlite3.open(path);
    final openMs = sw.elapsedMicroseconds / 1000.0;
    final firstQ = await timed(() async {
      db.select('SELECT COUNT(*) FROM unit');
    });
    bench('cold_open', openMs);
    bench('cold_first_query', firstQ);
    final unitCount = db.select('SELECT COUNT(*) c FROM unit').first['c'] as int;
    bench('unit_count', unitCount, 'rows');
    db.dispose();

    // ── WARM OPEN (OS page cache) ──
    final warm = await timed(() async {
      db = sqlite3.open(path);
      db.select('SELECT COUNT(*) FROM unit');
    });
    bench('warm_open_plus_query', warm);

    // ── FTS: 20 query thật (từ vocabulary corpus) ──
    const queries = [
      'quy đồng mẫu số', 'phân số', 'số thập phân', 'nhân một số thập phân',
      'chia một số thập phân', 'thể tích', 'hình lập phương', 'diện tích',
      'so sánh', 'làm tròn', 'mẫu số chung', 'tỉ số phần trăm', 'vận tốc',
      'hình tam giác', 'đơn vị đo', 'cộng hai phân số', 'trừ', 'hỗn số',
      'biểu đồ', 'trung bình cộng',
    ];
    final ftsTimes = <double>[];
    for (final q in queries) {
      ftsTimes.add(await timed(() async {
        db.select(
            "SELECT rowid FROM unit_fts WHERE unit_fts MATCH ? LIMIT 10",
            ['"$q"']);
      }));
    }
    ftsTimes.sort();
    bench('fts_p50', ftsTimes[ftsTimes.length ~/ 2]);
    bench('fts_p95', ftsTimes[(ftsTimes.length * 0.95).floor()]);

    // ── GRAPH TRAVERSAL: scope theo stage (grade/vol/lesson) 3 tầng ──
    final gt = await timed(() async {
      for (var i = 0; i < 20; i++) {
        db.select(
            'SELECT id FROM unit WHERE (grade<5) OR (grade=5 AND vol=1 AND '
            'lesson<=?) ORDER BY grade, vol, lesson LIMIT 50', [6 + i]);
      }
    });
    bench('graph_scope_20x', gt);

    // ── MIXED: scope-filter + FTS join (đúng luồng graph-guided RAG) ──
    final mixed = await timed(() async {
      for (var i = 0; i < 20; i++) {
        db.select(
            'SELECT u.id FROM unit u JOIN unit_fts f ON u.rowid=f.rowid '
            "WHERE f.unit_fts MATCH ? AND (u.grade<5 OR (u.grade=5 AND "
            'u.vol=1 AND u.lesson<=6)) LIMIT 10',
            ['"quy đồng"']);
      }
    });
    bench('mixed_scope_fts_20x', mixed);

    // ── REPEATED RETRIEVAL 100 lần (nhiệt/cache ổn định?) ──
    final rep = await timed(() async {
      for (var i = 0; i < 100; i++) {
        db.select('SELECT text FROM unit WHERE lesson=? AND grade=5 LIMIT 5',
            [1 + (i % 30)]);
      }
    });
    bench('repeated_100x', rep);

    // ── MIGRATION: user_version bump trong transaction ──
    final mig = await timed(() async {
      db.execute('PRAGMA user_version = 18');
    });
    bench('migration_user_version', mig);

    // ── DELTA UPDATE: update+insert+delete trong 1 transaction ──
    final delta = await timed(() async {
      db.execute('BEGIN');
      db.execute("UPDATE unit SET text = text || '' WHERE rowid = 1");
      db.execute(
          "INSERT INTO unit VALUES ('bench:new','bench',5,1,99,'RULE',1,'x')");
      db.execute("DELETE FROM unit WHERE id='bench:new'");
      db.execute('COMMIT');
    });
    bench('delta_txn', delta);
    db.dispose();

    // ── CORRUPTION/RECOVERY: file cắt cụt phải FAIL SẠCH, không treo/crash ──
    final corrupt = '${dir.path}/corrupt.db';
    final bytes = await File(path).readAsBytes();
    await File(corrupt).writeAsBytes(bytes.sublist(0, bytes.length ~/ 3));
    var failedCleanly = false;
    try {
      final cdb = sqlite3.open(corrupt);
      cdb.select('SELECT COUNT(*) FROM unit');
      cdb.dispose();
    } catch (_) {
      failedCleanly = true;
    }
    bench('corruption_fails_cleanly', failedCleanly ? 1 : 0, 'bool');

    expect(unitCount, 2584);
    expect(failedCleanly, true);
  });
}
