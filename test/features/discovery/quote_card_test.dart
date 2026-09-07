/// ⭐ Lệnh 59 §P1/§P2/§P7 — thẻ trích dẫn, và ba sự thật riêng của nó.
library;

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/stories/person_portrait.dart';
import 'package:learning_coach/features/discovery/quote_card.dart';

const _quote = 'Dân ta phải biết sử ta, Cho tường gốc tích nước nhà Việt Nam';

PersonPortrait _portrait({
  PortraitUsage usage = PortraitUsage.approvedForProduct,
  String? identity = 'trang nguồn của bảo tàng',
  String asset = 'assets/mascot/sam-hello.png',
  PortraitType type = PortraitType.historicalPhoto,
}) => PersonPortrait(
  personId: 'p:x',
  personName: 'X',
  assetPath: asset,
  portraitType: type,
  usage: usage,
  sourcePageUrl: 'https://example.org/page',
  sourceName: 'Nguồn ví dụ',
  licence: 'Public domain',
  retrievedAt: '2026-09-07',
  identityCheckedAgainst: identity,
);

Future<void> _pump(WidgetTester t, Widget card) async {
  t.view.physicalSize = const Size(1080, 2000);
  t.view.devicePixelRatio = 3.0;
  addTearDown(t.view.resetPhysicalSize);
  addTearDown(t.view.resetDevicePixelRatio);
  await t.pumpWidget(MaterialApp(home: Scaffold(body: card)));
  await t.pump();
}

void main() {
  group('§P1 — trích dẫn trông ra trích dẫn', () {
    testWidgets('có tên nguồn ghi ⇒ hiện «— Tên»', (t) async {
      await _pump(
        t,
        const QuoteCard(
          quoteText: _quote,
          sourceLine: 'SGK Lịch sử 10 · trang PDF 14',
          personName: 'Hồ Chí Minh',
        ),
      );
      expect(find.byKey(QuoteCard.cardKey), findsOneWidget);
      expect(find.textContaining(_quote), findsOneWidget);
      expect(find.text('— Hồ Chí Minh'), findsOneWidget);
      expect(find.textContaining('SGK Lịch sử 10'), findsOneWidget);
    });

    testWidgets('⭐⭐ §P1.2 — KHÔNG có tên trong nguồn ⇒ KHÔNG bịa người nói', (
      t,
    ) async {
      await _pump(
        t,
        const QuoteCard(
          quoteText: _quote,
          sourceLine: 'SGK Lịch sử 10 · trang PDF 14',
        ),
      );
      expect(find.byKey(QuoteCard.cardKey), findsOneWidget);
      expect(
        find.byKey(QuoteCard.attributionKey),
        findsNothing,
        reason: 'thẻ tự thêm một dòng attribution',
      );
      expect(find.textContaining('—'), findsNothing);
    });

    testWidgets('⭐ §P1.3 — chữ hiện NGUYÊN VĂN, chỉ bỏ dấu bao ngoài', (
      t,
    ) async {
      await _pump(
        t,
        const QuoteCard(quoteText: '«$_quote»', sourceLine: 'nguồn'),
      );
      expect(
        find.text(_quote),
        findsOneWidget,
        reason: 'chữ bị sửa hoặc dấu bao không được bỏ',
      );
    });

    test('bỏ dấu bao ngoài cho cả « », " " và “ ”', () {
      expect(QuoteCard.stripOuterQuotes('«a»'), 'a');
      expect(QuoteCard.stripOuterQuotes('"a"'), 'a');
      expect(QuoteCard.stripOuterQuotes('“a”'), 'a');
      // Dấu nháy BÊN TRONG câu thì giữ nguyên — không đụng vào chữ.
      expect(QuoteCard.stripOuterQuotes('a "b" c'), 'a "b" c');
    });

    testWidgets('không năm trong nguồn ⇒ không hiện năm', (t) async {
      await _pump(
        t,
        const QuoteCard(
          quoteText: _quote,
          sourceLine: 'nguồn',
          personName: 'Hồ Chí Minh',
        ),
      );
      expect(find.text('— Hồ Chí Minh'), findsOneWidget);
    });
  });

  group('§P2.7 — chân dung là sự thật RIÊNG', () {
    testWidgets('⭐ KHÔNG có chân dung ⇒ thẻ VẪN chạy đủ', (t) async {
      await _pump(
        t,
        const QuoteCard(
          quoteText: _quote,
          sourceLine: 'nguồn',
          personName: 'Hồ Chí Minh',
        ),
      );
      expect(find.byKey(QuoteCard.cardKey), findsOneWidget);
      expect(find.byKey(QuoteCard.portraitKey), findsNothing);
      expect(find.text('— Hồ Chí Minh'), findsOneWidget);
    });

    testWidgets('có chân dung đủ điều kiện ⇒ hiện ảnh + LOẠI ảnh + nguồn ảnh', (
      t,
    ) async {
      await _pump(
        t,
        QuoteCard(
          quoteText: _quote,
          sourceLine: 'nguồn câu',
          personName: 'Hồ Chí Minh',
          portrait: _portrait(),
        ),
      );
      expect(find.byKey(QuoteCard.portraitKey), findsOneWidget);
      expect(find.textContaining('Ảnh tư liệu'), findsOneWidget);
      expect(find.textContaining('Nguồn ví dụ'), findsOneWidget);
    });

    testWidgets('⛔ §P2.6 — tranh máy vẽ KHÔNG được gọi là ảnh tư liệu', (
      t,
    ) async {
      await _pump(
        t,
        QuoteCard(
          quoteText: _quote,
          sourceLine: 'nguồn',
          portrait: _portrait(type: PortraitType.aiGeneratedIllustration),
        ),
      );
      expect(find.textContaining('Tranh do máy vẽ'), findsOneWidget);
      expect(find.textContaining('Ảnh tư liệu'), findsNothing);
    });
  });

  group('§P2.4/§P2.5 — cổng quyền dùng và danh tính', () {
    test('chỉ APPROVED_FOR_PRODUCT mới là tài sản sản phẩm', () {
      expect(PortraitUsage.approvedForProduct.isProductionAsset, isTrue);
      for (final u in [
        PortraitUsage.internalOnly,
        PortraitUsage.unknownRights,
        PortraitUsage.rejected,
      ]) {
        expect(u.isProductionAsset, isFalse, reason: u.name);
      }
    });

    test('⭐⭐ chưa xác minh danh tính ⇒ KHÔNG hiển thị, dù quyền đã duyệt', () {
      expect(
        _portrait(identity: null).eligibleForDisplay,
        isFalse,
        reason: 'thà KHÔNG ẢNH còn hơn SAI NGƯỜI',
      );
    });

    test('⭐ quyền chưa rõ ⇒ KHÔNG tự thành tài sản sản phẩm', () {
      expect(
        _portrait(usage: PortraitUsage.unknownRights).eligibleForDisplay,
        isFalse,
      );
      expect(
        _portrait(usage: PortraitUsage.internalOnly).eligibleForDisplay,
        isFalse,
      );
    });

    test('không có tệp ⇒ không đủ điều kiện', () {
      expect(_portrait(asset: '').eligibleForDisplay, isFalse);
    });

    test('tra người chưa có chân dung ⇒ null, không nổ', () {
      expect(PersonPortraits.forPerson('p:khong-co'), isNull);
      expect(PersonPortraits.forPerson(null), isNull);
    });
  });

  // ⭐⭐ Kho `verified` không còn rỗng. Nhóm này giữ cho việc THÊM một người
  // không lách được ba bất biến của §P2 — vì lúc thêm mới là lúc dễ ẩu nhất.
  group('§P2 — kho chân dung đã xác minh', () {
    test('khoá map phải trùng personId bên trong', () {
      PersonPortraits.verified.forEach((k, v) {
        expect(v.personId, k, reason: 'khoá $k lệch personId ${v.personId}');
      });
    });

    test('⭐ mọi mục trong kho đều PHẢI đủ điều kiện hiển thị', () {
      for (final p in PersonPortraits.verified.values) {
        expect(
          p.eligibleForDisplay,
          isTrue,
          reason:
              '${p.personId} nằm trong `verified` nhưng không hiển thị được — '
              'mục chưa xong thì đừng đặt vào đây',
        );
      }
    });

    test('⭐ §P2.5 — mọi mục phải ghi ĐỐI CHIẾU DANH TÍNH cụ thể', () {
      for (final p in PersonPortraits.verified.values) {
        expect(p.identityCheckedAgainst, isNotNull, reason: p.personId);
        expect(
          p.identityCheckedAgainst!.trim().length,
          greaterThan(20),
          reason: '${p.personId}: «đã kiểm» không phải là bằng chứng',
        );
      }
    });

    test('⭐⭐ §P2.3 — sourcePageUrl KHÔNG được là trang kết quả tìm kiếm', () {
      // SEARCH RESULT != ORIGINAL SOURCE. Một URL tìm kiếm lọt vào đây nghĩa là
      // ai đó đã dừng ở bước tra cứu và gọi đó là nguồn.
      const searchHosts = [
        'google.com/search',
        'www.google.com',
        'bing.com',
        'duckduckgo.com',
        'search.',
        'images.google',
      ];
      for (final p in PersonPortraits.verified.values) {
        expect(p.sourcePageUrl, startsWith('https://'), reason: p.personId);
        for (final h in searchHosts) {
          expect(
            p.sourcePageUrl.contains(h),
            isFalse,
            reason: '${p.personId}: nguồn trỏ vào trang tìm kiếm «$h»',
          );
        }
        expect(p.licence.trim(), isNotEmpty, reason: p.personId);
      }
    });

    test('⭐ tệp ảnh phải CÓ THẬT trên đĩa và nằm trong thư mục đã khai', () {
      // Thư mục `assets/people/` được commit (ảnh phạm vi công cộng), nên đọc
      // nó trong test là an toàn cả trên CI — khác `assets/pack/*.png` vốn
      // gitignore và từng làm test xanh ở máy dev, đỏ trên CI.
      final pubspec = File('pubspec.yaml').readAsStringSync();
      for (final p in PersonPortraits.verified.values) {
        final f = File(p.assetPath);
        expect(f.existsSync(), isTrue, reason: 'thiếu tệp ${p.assetPath}');
        expect(f.lengthSync(), greaterThan(1000), reason: p.assetPath);
        final dir =
            '${p.assetPath.substring(0, p.assetPath.lastIndexOf('/'))}/';
        expect(
          pubspec.contains('- $dir'),
          isTrue,
          reason:
              '$dir chưa khai trong pubspec ⇒ ảnh nằm trên đĩa nhưng máy thật '
              'dựng ra thẻ trống (đúng vết WAL-167 với thư mục bìa)',
        );
      }
    });

    test('⭐ tỉ lệ ảnh phải khớp khung 72×88, nếu không `cover` cắt mất đầu', () {
      // Ảnh gốc là bản khắc dọc tỉ lệ 0.627. Đưa thẳng vào khung 0.818 thì
      // BoxFit.cover xén trên–dưới và mất đỉnh đầu. Đây là lý do phải cắt lại.
      for (final p in PersonPortraits.verified.values) {
        final bytes = File(p.assetPath).readAsBytesSync();
        // PNG IHDR: 8 byte chữ ký + 4 độ dài + 4 'IHDR' + 4 rộng + 4 cao.
        expect(bytes.sublist(1, 4), [
          0x50,
          0x4E,
          0x47,
        ], reason: 'không phải PNG');
        int be32(int o) =>
            (bytes[o] << 24) |
            (bytes[o + 1] << 16) |
            (bytes[o + 2] << 8) |
            bytes[o + 3];
        final w = be32(16), h = be32(20);
        expect(
          w / h,
          closeTo(72 / 88, 0.02),
          reason: '${p.personId}: $w×$h lệch tỉ lệ khung thẻ',
        );
      }
    });

    test('Thạch Lam — khớp personId của `sam-stories.db`, nhãn đúng loại', () {
      final p = PersonPortraits.forPerson('p:thạch-lam');
      expect(p, isNotNull, reason: 'khoá phải trùng cột personId trong story');
      expect(p!.personName, 'Thạch Lam');
      // Bản in ty-pô 1942 của một tấm ảnh ⇒ «Ảnh tư liệu», không phải tranh vẽ.
      expect(p.portraitType, PortraitType.historicalPhoto);
      expect(p.portraitType.label, 'Ảnh tư liệu');
      expect(p.usage, PortraitUsage.approvedForProduct);
      expect(p.sourcePageUrl, contains('gallica.bnf.fr'));
    });
  });
}
