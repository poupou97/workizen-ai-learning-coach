/// Hỗ trợ test Track B: nạp fixture MẪU từ đĩa (commit) và, nếu máy có, fixture
/// THẬT (gitignore) — test thật chỉ chạy khi có file, KHÔNG xanh giả.
///
/// Bundle giả phục vụ `assets/fixtures/**` + `assets/pack/**` bằng ảnh 1px
/// (cùng lý do `pack_bundle.dart`: test không được đo tủ đồ của một máy).
library;

import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show CachingAssetBundle, rootBundle;
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/workspace_catalog.dart';

const syntheticPath =
    'assets/fixtures/synthetic/lesson-06-sgk-khoa-hoc-tu-nhien-6-b17.synthetic.json';
const realPath =
    'assets/fixtures/real/lesson-06-sgk-khoa-hoc-tu-nhien-6-b17.json';

LessonDocument loadSyntheticDoc() {
  final j = jsonDecode(File(syntheticPath).readAsStringSync()) as Map;
  final d = LessonDocument.fromJson(
    j.cast<String, Object?>(),
    assetBase: FixtureSlot.syntheticDir,
  );
  if (d == null) throw StateError('fixture mẫu không parse được');
  return d;
}

/// `null` + skip khi máy này chưa sinh fixture thật.
LessonDocument? loadRealDocOrSkip() {
  final f = File(realPath);
  if (!f.existsSync()) {
    markTestSkipped('fixture thật chưa sinh trên máy này (poc-out)');
    return null;
  }
  final j = jsonDecode(f.readAsStringSync()) as Map;
  return LessonDocument.fromJson(
    j.cast<String, Object?>(),
    assetBase: FixtureSlot.realDir,
  );
}

final _onePx = base64Decode(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhf'
  'DwAChwGA60e6kgAAAABJRU5ErkJggg==',
);

class _FixtureStub extends CachingAssetBundle {
  _FixtureStub({this.json = const {}});

  /// Đường dẫn asset → nội dung JSON (chuỗi). Không có ⇒ ném như thiếu asset.
  final Map<String, String> json;

  @override
  Future<ByteData> load(String key) async {
    if (json.containsKey(key)) {
      return ByteData.view(Uint8List.fromList(utf8.encode(json[key]!)).buffer);
    }
    if (key.startsWith('assets/fixtures/') && key.endsWith('.json')) {
      throw FlutterError('Unable to load asset: "$key".');
    }
    if (key.startsWith('assets/fixtures/') || key.startsWith('assets/pack/')) {
      return ByteData.view(Uint8List.fromList(_onePx).buffer);
    }
    return rootBundle.load(key);
  }

  @override
  Future<String> loadString(String key, {bool cache = true}) async {
    if (json.containsKey(key)) return json[key]!;
    return super.loadString(key, cache: cache);
  }
}

/// Bundle chỉ có fixture MẪU (đúng trạng thái CI / clone sạch).
CachingAssetBundle syntheticOnlyBundle() =>
    _FixtureStub(json: {syntheticPath: File(syntheticPath).readAsStringSync()});

/// Bundle không có fixture nào.
CachingAssetBundle noFixtureBundle() => _FixtureStub();

Widget fixtureHost(Widget child) => DefaultAssetBundle(
  bundle: _FixtureStub(),
  child: MaterialApp(home: child),
);
