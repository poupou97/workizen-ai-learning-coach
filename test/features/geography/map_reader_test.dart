/// WAL-144 #28 — MapReader: bản đồ SGK thật + câu hỏi verbatim, không chấm.
///
/// WAL-163 (CI bắt được): bản đầu dựng thẳng `MapReaderScreen` nên `Image.asset`
/// đi tìm crop bản đồ THẬT trong `assets/pack/` — file đó là artefact LOCAL,
/// gitignore theo WAL-43. Máy tôi có ⇒ xanh; CI và mọi máy khác không có ⇒
/// «Unable to load asset» ném exception ⇒ đỏ. Test cũ đang kiểm chứng cái tủ
/// đồ của một người, không phải mã nguồn.
///
/// Sửa: tiêm bundle test trả PNG 1×1 cho mọi khoá `assets/pack/`. Hợp đồng
/// thật của màn — «xin ĐÚNG tên asset ghi trong DiaMap» — nay được assert
/// thẳng, chặt hơn cả bản cũ vốn không kiểm tên bao giờ.
library;

import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart'
    show CachingAssetBundle, rootBundle;
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/features/geography/map_reader_screen.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';

/// PNG 1×1 hợp lệ — đủ để dựng widget, KHÔNG cần crop SGK.
final _onePx = base64Decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhf'
    'DwAChwGA60e6kgAAAABJRU5ErkJggg==');

class _PackStubBundle extends CachingAssetBundle {
  @override
  Future<ByteData> load(String key) async => key.startsWith('assets/pack/')
      ? ByteData.view(Uint8List.fromList(_onePx).buffer)
      : rootBundle.load(key);
}

Widget _host(Widget child) =>
    DefaultAssetBundle(bundle: _PackStubBundle(), child: MaterialApp(home: child));

const _map = DiaMap(
  subject: 'LS&ĐL',
  book: '05-sgk-lich-su-va-dia-li-5',
  page: 10,
  asset: 'map-ls-dia-5-p012-tu-nhien-vn.png',
  caption: 'Hình 1. Bản đồ tự nhiên Việt Nam',
  questions: [
    'Kể tên và xác định trên bản đồ một số khoáng sản ở nước ta.',
    'Nêu vai trò của tài nguyên khoáng sản đối với sự phát triển kinh tế.',
  ],
);

void main() {
  testWidgets('bản đồ + caption + câu hỏi VERBATIM hiện; nguồn có trang', (t) async {
    await t.pumpWidget(_host(const MapReaderScreen(map: _map)));
    await t.pump();
    expect(find.text('BẢN ĐỒ TRONG SÁCH'), findsOneWidget);
    expect(find.text('Hình 1. Bản đồ tự nhiên Việt Nam'), findsOneWidget);
    // dòng nguồn nằm dưới fold — ListView lười: cuộn tới rồi mới assert.
    await t.scrollUntilVisible(find.textContaining('tr. 10'), 150,
        scrollable: find.byType(Scrollable).first);
    expect(find.textContaining('Kể tên và xác định trên bản đồ'), findsOneWidget);
    expect(find.textContaining('tr. 10'), findsOneWidget);
    expect(find.byType(InteractiveViewer), findsOneWidget,
        reason: 'bản đồ phải phóng to được — để soi, không để ngắm');
    // ⭐ Màn phải xin ĐÚNG tên asset ghi trong DiaMap, có tiền tố assets/pack/.
    final img = t.widget<Image>(find.descendant(
        of: find.byType(InteractiveViewer), matching: find.byType(Image)));
    expect((img.image as AssetImage).assetName,
        'assets/pack/map-ls-dia-5-p012-tu-nhien-vn.png',
        reason: '⭐ đột biến ghép sai đường dẫn asset ⇒ đỏ');
  });

  testWidgets('⭐ hoàn tất ⇒ MỘT event correct=null policy map-reader-v1', (t) async {
    List<LearningEvent> out = const [];
    await t.pumpWidget(_host(MapReaderScreen(
        map: _map,
        now: () => DateTime(2026, 9, 2, 22),
        onFinished: (e) => out = e)));
    await t.pump();
    await t.scrollUntilVisible(find.text('Con đã chỉ được trên bản đồ ✅'), 150,
        scrollable: find.byType(Scrollable).first);
    await t.tap(find.text('Con đã chỉ được trên bản đồ ✅'));
    await t.pumpAndSettle();
    expect(out.single.correct, isNull,
        reason: '⭐ đột biến chấm việc chỉ-bản-đồ ⇒ test đỏ');
    expect(out.single.policyId, 'map-reader-v1');
    expect(out.single.knowledgeVersion, isNotNull);
    expect(find.textContaining('không chấm'), findsOneWidget);
  });

  testWidgets('⭐ WAL-163: máy dựng THIẾU crop bản đồ ⇒ nói thật một câu, '
      'câu hỏi vẫn đọc được (không ô đỏ giữa bài học)', (t) async {
    await t.pumpWidget(DefaultAssetBundle(
        bundle: _MissingPackBundle(),
        child: const MaterialApp(home: MapReaderScreen(map: _map))));
    await t.pump();
    expect(find.textContaining('chưa có ảnh bản đồ'), findsOneWidget);
    expect(find.textContaining('Kể tên và xác định trên bản đồ'), findsOneWidget,
        reason: 'thiếu ảnh KHÔNG được cắt mất phần học được');
  });
}

/// Bundle giả lập máy KHÔNG có pack — mọi khoá assets/pack/ ném như thật.
class _MissingPackBundle extends CachingAssetBundle {
  @override
  Future<ByteData> load(String key) async {
    if (key.startsWith('assets/pack/')) {
      throw FlutterError('Unable to load asset: "$key".');
    }
    return rootBundle.load(key);
  }
}
