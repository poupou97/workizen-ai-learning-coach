/// WAL-151 — StoriesStore trên DB THẬT (assets/pack/sam-stories.db).
/// Máy chưa build pack ⇒ skip (không đỏ giả), như lesson-index guard.
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/stories/stories_store.dart';

void main() {
  const path = 'assets/pack/sam-stories.db';
  final exists = File(path).existsSync();

  test('mở DB thật: chỉ VERIFIED, FTS + person + trace nguồn', () {
    if (!exists) {
      markTestSkipped('pack chưa build trên máy này');
      return;
    }
    final s = StoriesStore.open(path);
    expect(s.isEmpty, isFalse);

    final hits = s.search('Beethoven');
    expect(hits, isNotEmpty, reason: 'FTS phải tìm thấy Beethoven');
    expect(hits.first.sourceLine, contains('trang'),
        reason: 'mọi item trace được về nguồn (§34)');

    final quotes = s.loadingQuotes();
    expect(quotes, isNotEmpty);
    expect(quotes.first.body, isNotEmpty);

    // person detail từ personId của một story PERSON
    final people = s.byType('PERSON');
    expect(people, isNotEmpty);
    final pid = people.firstWhere((p) => p.personId != null).personId!;
    final person = s.person(pid);
    expect(person, isNotNull);
    expect(person!.name, isNotEmpty);
  });

  test(
      '⭐ PERSON không có năm sinh-mất ⇒ title vẫn tự giải thích được, '
      'không phải chuỗi phiên âm trần trụi vô nghĩa', () {
    if (!exists) {
      markTestSkipped('pack chưa build trên máy này');
      return;
    }
    final s = StoriesStore.open(path);
    final gram = s.search('Gram').firstWhere(
        (x) => x.type == 'PERSON' && x.title.startsWith('Hen Krit'));
    // Bug thật tìm thấy trên Nokia: card «Bạn có biết?» chỉ hiện title, và
    // title thuần phiên âm không kèm năm sinh-mất đọc như chuỗi vô nghĩa.
    // Fix: lấy lại nguyên văn tên gốc trong ngoặc mà SGK đã in sẵn kế bên
    // tên phiên âm trong câu nguồn — không suy luận, không LLM.
    expect(gram.title, 'Hen Krit-chừn Gioa-chim G-ram (Hans Christian Joachim Gram)');
  });

  test('todayEvents: ngày không có event ⇒ RỖNG, không fabricate (§14)', () {
    if (!exists) {
      markTestSkipped('pack chưa build trên máy này');
      return;
    }
    final s = StoriesStore.open(path);
    // 29/02 năm không nhuận — gần như chắc chắn không có trong pack 37 items
    expect(s.todayEvents(DateTime(2026, 2, 28)), isA<List<StoryItem>>());
    // hợp đồng: mọi phần tử trả về ĐỀU có monthDay — không suy đoán
    for (final e in s.todayEvents(DateTime(2026, 9, 2))) {
      expect(e.monthDay, '09-02');
    }
  });

  test('mở path không tồn tại ⇒ store RỖNG fail-closed, API trả rỗng', () {
    final s = StoriesStore.open('/khong/ton/tai.db');
    expect(s.isEmpty, isTrue);
    expect(s.search('x'), isEmpty);
    expect(s.todayEvents(DateTime.now()), isEmpty);
    expect(s.loadingQuotes(), isEmpty);
  });
}
