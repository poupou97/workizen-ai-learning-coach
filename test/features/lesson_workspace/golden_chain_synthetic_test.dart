/// ⭐⭐ WAL-218 — **BẢN MÔ PHỎNG KHÔNG CẦN CORPUS của chuỗi Golden.**
///
/// Chín khẳng định đắt nhất của repo chỉ chạy khi máy có fixture THẬT của
/// Golden #1, mà fixture ấy nằm trong `.gitignore` (Founder D4). Trên CI chúng
/// bỏ qua — và trước WAL-218 suite vẫn in «All tests passed!».
///
/// Tệp này dựng một tài liệu **hình dạng Golden** từ chính fixture MẪU đã
/// commit: một vùng bị GIỮ LẠI mang `VALIDATED_REPAIR` không phục vụ được,
/// không dòng thời gian nào dựng từ nó, không bản ghi sửa nào mang chữ. Không
/// một byte SGK nào tham gia — đầu vào là văn bản giả lập, đầu ra cũng vậy.
///
/// ⭐ **SYNTHETIC PASS ≠ GOLDEN VERIFIED.** Chín test dưới đây chứng minh
/// ĐƯỜNG MÃ vẫn giữ được bất biến; chỉ fixture thật mới chứng minh CHUỖI
/// GOLDEN — rằng chính cái tài liệu sinh ra từ sách kia đi qua được đường ấy.
/// `tool/ci/golden_chain_verdict.py` in hai con số ở hai dòng riêng và không
/// bao giờ cộng chúng lại.
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/content_trust.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/next_action.dart';
import 'package:learning_coach/core/lesson_model/repair_record.dart';
import 'package:learning_coach/core/lesson_model/semantic_data.dart';
import 'package:learning_coach/core/lesson_model/timeline_sources.dart';
import 'package:learning_coach/core/lesson_model/workspace_catalog.dart';
import 'package:learning_coach/features/lesson_workspace/lesson_workspace_screen.dart';
import 'package:learning_coach/features/lesson_workspace/smart_book_view.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/fixture_chip.dart';
import 'package:learning_coach/features/lesson_workspace/workspace_trace.dart';

import '../../support/golden_chain_ledger.dart';
import 'support.dart';

const _slot = FixtureSlot(book: '05-sgk-lich-su-va-dia-li-5', lessonNo: 8);
const _syntheticSource =
    'assets/fixtures/synthetic/lesson-05-sgk-lich-su-va-dia-li-5-b8.synthetic.json';

/// Dấu của HAI THẾ HỆ. Đường mẫu giữ `[MẪU]`; bản mô phỏng-đường-thật mang
/// `[MIRROR]`. Trộn hai dấu trong một tài liệu ⇒ catalog đã nạp nhầm đường.
const _syntheticMark = '[MẪU]';
const _mirrorMark = '[MIRROR]';

Map<String, Object?> _deepCopy(Object? j) =>
    (jsonDecode(jsonEncode(j)) as Map).cast<String, Object?>();

/// Bản ghi sửa chữa hình dạng thật: đủ trường để đọc lại quyết định, KHÔNG
/// một trường nào mang giá trị đề xuất.
Map<String, Object?> _repairFor(String blockId) => {
  'repairId': '$blockId#mirror.tone-corroboration-v1#0000000000000000',
  'disposition': 'VALIDATED_REPAIR',
  'failureClass': 'vi_tone_disagreement',
  'method': 'mirror.tone-corroboration-v1',
  'repairVersion': 'repair-v1/mirror.tone-corroboration-v1',
  'validatorId': 'mirror.text-validator-v1',
  'validatorVersion': 'v1',
  'verdict': 'validated',
  'supportingLayers': ['D', 'E'],
  'changed': false,
  'servable': false,
  'structuredKind': null,
  'caps': ['trust_gate:founder_decision_absent'],
};

/// Dựng tài liệu hình dạng Golden từ fixture MẪU đã commit.
///
/// * mọi block mà dòng thời gian dựng từ đó ⇒ **withheld + VALIDATED_REPAIR**,
///   mất trường chữ;
/// * `semantic` mất luôn dòng thời gian — đó là HỆ QUẢ, không phải một lựa
///   chọn trình bày: mốc chỉ được quay lại cùng một quyết định tin;
/// * `provenance` khai đủ năm trường phiên bản + kế toán sửa chữa `trusted: 0`.
///
/// `real: true` ⇒ thế hệ «đường thật» (`trustedStructuredLesson`, dấu
/// `[MIRROR]`); `real: false` ⇒ giữ nguyên thế hệ mẫu.
Map<String, Object?> mirrorJson({required bool real}) {
  final m = _deepCopy(jsonDecode(File(_syntheticSource).readAsStringSync()));

  final semantic = (m['semantic']! as List)
      .map((s) => (s as Map).cast<String, Object?>())
      .toList();
  final timeline = semantic.firstWhere((s) => s['type'] == 'timeline');
  final withheldIds = <String>{
    for (final e in (timeline['events']! as List))
      (e as Map)['sourceBlockId']! as String,
  };
  expect(withheldIds, isNotEmpty, reason: 'fixture mẫu phải có dòng thời gian');

  final blocks = <Map<String, Object?>>[];
  for (final raw in (m['blocks']! as List)) {
    final b = (raw as Map).cast<String, Object?>();
    final id = b['id']! as String;
    if (withheldIds.contains(id)) {
      blocks.add({
        'id': id,
        'type': 'withheld',
        'trust': 'withheld',
        'sourceRef': b['sourceRef'],
        'sourceRole': b['type'],
        if (b['relations'] != null) 'relations': b['relations'],
        'reason': 'agree_tones',
        'reasons': ['agree_tones'],
        'status': 'WITHHELD',
        'textLen': (b['text'] as String? ?? '').length,
        'repair': _repairFor(id),
        'disposition': 'VALIDATED_REPAIR',
      });
      continue;
    }
    if (real && b['text'] is String) {
      b['text'] = (b['text']! as String).replaceAll(_syntheticMark, _mirrorMark);
    }
    if (real) b['trust'] = 'trustedStructuredLesson';
    blocks.add(b);
  }
  m['blocks'] = blocks;
  // ⭐ dòng thời gian biến mất VÌ nguồn của nó bị giữ lại.
  m['semantic'] = [
    for (final s in semantic)
      if (s['type'] != 'timeline') s,
  ];
  // Kịch bản SAM của fixture mẫu trích đúng những block vừa bị giữ lại — một
  // kịch bản trỏ vào vùng không còn chữ là chuyện của lát cắt khác, không
  // phải bất biến tệp này ghim.
  m.remove('tutorScript');

  final p = (m['provenance']! as Map).cast<String, Object?>();
  if (real) p['trust'] = 'trustedStructuredLesson';
  p['sourceHash'] = 'mirror-sha256-not-a-real-source';
  p['pipelineVersion'] = 'mirror/sdm-v3';
  p['sdmVersion'] = 'sdm-v3';
  p['generator'] = 'test/features/lesson_workspace/'
      'golden_chain_synthetic_test.dart@golden-chain-mirror-v1';
  p['tslPath'] = '(synthetic mirror — no TSL, no corpus)';
  p['repair'] = {
    'validatedRepairs': withheldIds.length,
    'onBlocks': withheldIds.length,
    'trusted': 0,
    'capped': withheldIds.length,
    'projection': 'tsl-repair-projection-v1',
    'framework': 'repair-v1',
    'productionTrustThreshold': null,
    'note': 'VALIDATED REPAIR != TRUSTED — synthetic mirror, no corpus.',
    'sourceTslSha256': 'mirror-sha256-not-a-real-source',
    'projectedTslSha256': 'mirror-sha256-not-a-real-projection',
    'hashMethod': 'n/a (synthetic mirror)',
    'generator': p['generator'],
    'generation': 'golden-chain-mirror-v1',
  };
  m['provenance'] = p;
  return m;
}

LessonDocument mirrorDoc({bool real = true}) {
  final d = LessonDocument.fromJson(
    mirrorJson(real: real),
    assetBase: real ? FixtureSlot.realDir : FixtureSlot.syntheticDir,
  );
  expect(
    d,
    isNotNull,
    reason: 'bản mô phỏng phải PARSE ĐƯỢC bằng chính mã app này — nếu không, '
        'nó không mô phỏng đường mã nào cả',
  );
  return d!;
}

void main() {
  group('§0 bản mô phỏng là MỘT MÔ PHỎNG — nói thẳng ra', () {
    test('không mang chữ sách: đầu vào là fixture MẪU đã commit', () {
      expect(File(_syntheticSource).existsSync(), isTrue);
      expect(_syntheticSource, contains('/synthetic/'));
      // Và nó KHÔNG thay được fixture thật: bản đăng ký nghĩa vụ trỏ chỗ khác.
      expect(goldenChainFixturePath, isNot(_syntheticSource));
      expect(goldenChainFixturePath, contains('/real/'));
    });
  });

  group('§1 CHUỖI GIAO HÀNG (mô phỏng)', () {
    test('SYN-01 ⭐⭐ ĐƯỜNG THẬT thắng ĐƯỜNG MẪU', () async {
      final catalog = WorkspaceCatalog(
        bundle: fixtureBundleWith({
          _slot.realPath: jsonEncode(mirrorJson(real: true)),
          _slot.syntheticPath: jsonEncode(mirrorJson(real: false)),
        }),
        slots: const [_slot],
      );
      await catalog.load();
      final doc = catalog.docFor(_slot.book, _slot.lessonNo);
      expect(doc, isNotNull);
      expect(doc!.provenance.trust, ContentTrust.trustedStructuredLesson);
      final texts = doc.blocks.whereType<ParagraphBlock>().map((b) => b.text);
      expect(texts, isNotEmpty);
      expect(
        texts.where((t) => t.contains(_syntheticMark)),
        isEmpty,
        reason: 'dấu của thế hệ MẪU lọt vào đường thật ⇒ đang trộn hai thế hệ',
      );
      expect(WorkspaceCatalog.isResearchSlot(doc), isTrue);
      recordGoldenChain('SYN-01', exercised: true);
    });

    test('SYN-02 ⭐ đủ NĂM TRƯỜNG PHIÊN BẢN + kế toán sửa chữa trusted = 0', () {
      final p = (mirrorJson(real: true)['provenance']! as Map)
          .cast<String, Object?>();
      for (final k in [
        'sourceHash',
        'pipelineVersion',
        'sdmVersion',
        'generator',
        'tslPath',
      ]) {
        expect((p[k] as String?)?.trim(), isNotEmpty, reason: k);
      }
      final r = (p['repair']! as Map).cast<String, Object?>();
      expect(r['projection'] ?? r['version'], isNotNull);
      expect(r['trusted'], 0);
      recordGoldenChain('SYN-02', exercised: true);
    });
  });

  group('§2 VALIDATED REPAIR ≠ TRUSTED (mô phỏng)', () {
    test('SYN-03 ⭐⭐ mọi vùng đã sửa vẫn WITHHELD và vẫn KHÔNG mang chữ', () {
      final blocks = (mirrorJson(real: true)['blocks']! as List)
          .cast<Map<Object?, Object?>>();
      final repaired = [
        for (final b in blocks)
          if (b['repair'] != null) b.cast<String, Object?>(),
      ];
      expect(repaired, isNotEmpty);
      for (final b in repaired) {
        expect(b['type'], 'withheld', reason: 'khối ${b['id']}');
        expect(b['trust'], 'withheld', reason: 'khối ${b['id']}');
        expect(b.containsKey('text'), isFalse, reason: 'khối ${b['id']}');
      }
      recordGoldenChain('SYN-03', exercised: true);
    });

    test('SYN-04 ⭐ chỗ trống CÓ LÝ DO, và mô hình app không mang chữ', () {
      final d = mirrorDoc();
      final withheld = d.blocks.whereType<WithheldBlock>().toList();
      expect(withheld, isNotEmpty);
      for (final w in withheld) {
        expect(w.reasons, isNotEmpty, reason: '${w.id}: mỗi chỗ trống nêu LÝ DO');
        expect(jsonEncode(w.toJson()).contains(_mirrorMark), isFalse);
      }
      recordGoldenChain('SYN-04', exercised: true);
    });
  });

  group('§3 TRÊN MÀN HÌNH (mô phỏng)', () {
    testWidgets('SYN-05 ⭐ ba View mở được; chip «chưa kiểm định» còn nguyên', (
      t,
    ) async {
      final d = mirrorDoc();
      t.view.physicalSize = const Size(1080, 1920);
      t.view.devicePixelRatio = 2.75;
      addTearDown(t.view.reset);
      await t.pumpWidget(
        fixtureHost(LessonWorkspaceScreen(doc: d, trace: WorkspaceTrace())),
      );
      await t.pumpAndSettle();
      expect(
        find.byType(FixtureChip),
        findsOneWidget,
        reason: 'chưa có tài liệu trustedCorpus nào — chip là bắt buộc',
      );
      for (final v in WorkspaceView.values) {
        await t.tap(find.byKey(LessonWorkspaceScreen.tabKey(v)));
        await t.pumpAndSettle();
      }
      await t.tap(find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.read)));
      await t.pumpAndSettle();
      expect(find.byType(SmartBookView), findsOneWidget);
      recordGoldenChain('SYN-05', exercised: true);
    });

    testWidgets('SYN-06 ⭐⭐ bản ghi sửa KHÔNG mang giá trị đề xuất, và từ vựng '
        'pipeline không lên màn Đọc', (t) async {
      final raw = mirrorJson(real: true);
      const textBearing = {
        'text',
        'repairedText',
        'candidate',
        'candidateText',
        'proposed',
        'proposedText',
        'value',
        'after',
        'replacement',
        'original',
        'observed',
      };
      var seen = 0;
      for (final b in (raw['blocks']! as List).cast<Map<Object?, Object?>>()) {
        final r = b['repair'];
        if (r is! Map) continue;
        seen++;
        for (final k in r.keys) {
          expect(textBearing.contains(k), isFalse, reason: '${b['id']} · $k');
        }
        expect(r['servable'], isFalse);
        expect(r['disposition'], 'VALIDATED_REPAIR');
      }
      expect(seen, greaterThan(0));

      t.view.physicalSize = const Size(1080, 1920);
      t.view.devicePixelRatio = 2.75;
      addTearDown(t.view.reset);
      await t.pumpWidget(
        fixtureHost(
          LessonWorkspaceScreen(
            doc: mirrorDoc(),
            trace: WorkspaceTrace(),
            initialView: WorkspaceView.read,
          ),
        ),
      );
      await t.pumpAndSettle();
      expect(find.byType(SmartBookView), findsOneWidget);
      final onScreen = t
          .widgetList<Text>(find.byType(Text))
          .map((w) => w.data ?? w.textSpan?.toPlainText() ?? '')
          .join('\n');
      expect(onScreen.contains('VALIDATED_REPAIR'), isFalse);
      recordGoldenChain('SYN-06', exercised: true);
    });
  });

  group('§4 HỆ QUẢ: KHÔNG dòng thời gian khi nguồn chưa được tin (mô phỏng)', () {
    test('SYN-07 ⭐⭐ block nguồn CÓ MẶT, BỊ GIỮ LẠI, mang VALIDATED_REPAIR — '
        'và không dòng thời gian nào dựng được', () {
      final d = mirrorDoc();
      final withheld = d.blocks.whereType<WithheldBlock>().toList();
      final repaired = withheld.where((w) => w.hasValidatedRepair).toList();
      expect(repaired, isNotEmpty, reason: 'block nguồn không được biến mất');
      for (final w in repaired) {
        expect(w.trust, ContentTrust.withheld);
        final r = w.repair!;
        expect(r.disposition, RepairDisposition.validatedRepair);
        expect(r.verdict, 'validated');
        expect(r.servable, isFalse);
        expect(r.cappedByTrustGate, isTrue);
      }
      expect(d.trustedRepairCount, 0);
      // ⭐ HỆ QUẢ.
      expect(
        d.semantic.whereType<TimelineSemantic>(),
        isEmpty,
        reason: 'dòng thời gian chỉ được quay lại CÙNG một quyết định tin của '
            'Founder cho block nguồn — NỐI ≠ TIN',
      );
      // và không block PHỤC VỤ nào mang dấu vết sửa chữa.
      for (final b in d.blocks) {
        if (b is WithheldBlock) continue;
        expect(b.toJson().containsKey('repair'), isFalse, reason: b.id);
      }
      recordGoldenChain('SYN-07', exercised: true);
    });

    test('SYN-08 kế toán sửa chữa của tài liệu nói thật', () {
      final raw = mirrorJson(real: true);
      final d = mirrorDoc();
      final withRepair = d.validatedRepairs;
      expect(withRepair, isNotEmpty);
      for (final b in withRepair) {
        expect(b.trust, ContentTrust.withheld);
        expect(b.repair!.servable, isFalse);
      }
      final prov = ((raw['provenance']! as Map)['repair']! as Map)
          .cast<String, Object?>();
      expect(prov['trusted'], 0, reason: 'bất biến, không phải phép đo');
      expect(prov['onBlocks'], withRepair.length);
      expect(prov['productionTrustThreshold'], isNull);
      for (final k in [
        'sourceTslSha256',
        'projectedTslSha256',
        'hashMethod',
        'generator',
        'generation',
      ]) {
        expect(prov[k], isNotNull, reason: k);
      }
      recordGoldenChain('SYN-08', exercised: true);
    });

    test('SYN-09 nguồn kể chuyện chỉ dựng từ block CÒN được phục vụ', () {
      final d = mirrorDoc();
      final src = deriveStoryAttributions(d);
      expect(src, isNotEmpty, reason: 'mô phỏng phải thật sự chạy qua luật này');
      for (final a in src) {
        final b = d.blockById(a.attributionBlockId);
        expect(b, isNotNull, reason: a.attributionBlockId);
        expect(b, isNot(isA<WithheldBlock>()), reason: a.attributionBlockId);
      }
      recordGoldenChain('SYN-09', exercised: true);
    });
  });
}
