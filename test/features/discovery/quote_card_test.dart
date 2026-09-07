/// ⭐ Lệnh 59 §P1/§P2/§P7 — thẻ trích dẫn, và ba sự thật riêng của nó.
library;

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

    test('kho chân dung RỖNG hôm nay — và tra người lạ trả null, không nổ', () {
      expect(PersonPortraits.verified, isEmpty);
      expect(PersonPortraits.forPerson('p:khong-co'), isNull);
      expect(PersonPortraits.forPerson(null), isNull);
    });
  });
}
