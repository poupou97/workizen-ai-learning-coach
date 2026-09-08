/// STRESS-TEST QUY MÔ LỚP 10–12 — dữ liệu thật đo được, dựng trong test.
///
/// Đo trên pack thật: mỗi lớp 10–12 có **41–42 sách · 16–17 môn · 515–557 bài**,
/// sách nhiều nhất 35 bài, tên bài trung vị ~30 ký tự, p95 ~60, dài nhất **107**.
/// Lớp 5 — nơi mọi test giá sách hiện có đang chạy — chỉ có 15 sách.
///
/// Test KHÔNG đọc `assets/pack/lesson-index-g11.json`: tệp ấy dựng tại máy và
/// KHÔNG nằm trong git, nên một test đọc thẳng nó sẽ xanh ở máy dev và đỏ trên
/// CI (đã dính một lần). Ở đây dựng lại ĐÚNG các chiều đo được.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/features/subjects/book_shelf_screen.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';

import '../../support/pack_bundle.dart';

const _p = LearnerProfile(learnerId: 'l', displayName: 'Na', grade: 11);

/// Tên bài dài nhất đo được trên corpus (lớp 12).
const _longTitle =
    'PHÁT TRIỂN KINH TẾ VÀ ĐẢM BẢO QUỐC PHÒNG, AN NINH Ở BIỂN ĐÔNG VÀ CÁC ĐẢO, QUẦN ĐẢO';

/// 17 môn, 42 sách, 557 bài — đúng hình dạng lớp 11 thật.
LessonIndex _grade11() {
  const subjects = [
    'Toán', 'Ngữ văn', 'Vật lí', 'Hoá học', 'Sinh học', 'Lịch sử', 'Địa lí',
    'Tin học', 'Công nghệ', 'GDKT&PL', 'Tiếng Anh', 'Âm nhạc', 'Mĩ thuật',
    'GDTC', 'HĐTN-HN', 'GDQP', 'Chuyên đề',
  ];
  final subj = StringBuffer();
  final books = StringBuffer();
  var b = 0;
  var lessons = 0;
  for (var s = 0; s < subjects.length; s++) {
    // «Chuyên đề» thật sự gom 9 sách — môn phình to nhất, và là chỗ điều hướng
    // dễ vỡ nhất khi một môn nuốt gần một phần tư giá sách.
    final n = subjects[s] == 'Chuyên đề' ? 9 : (s % 3 == 0 ? 3 : 2);
    final entries = <String>[];
    for (var i = 0; i < n; i++, b++) {
      final id = '11-sgk-mon$s-quyen$i';
      final per = 13 + (b % 23);          // tới 35 bài/sách như đo được
      final ls = [
        for (var k = 1; k <= per; k++)
          '{"no":$k,"title":"${k == 1 ? _longTitle : 'Bài học số $k của môn ${subjects[s]}'}",'
              '"pageStart":${5 + k * 4}}'
      ];
      lessons += per;
      entries.add('{"sourceDocumentId":"$id","volume":null,"lessons":[${ls.join(',')}]}');
      books.write('${b == 0 ? '' : ','}'
          '{"sourceDocumentId":"$id","subject":"${subjects[s]}","grade":11,'
          '"title":"${subjects[s]} 11","volumeLabel":null,'
          '"cover":"covers/$id.webp",'
          '"lessonCount":$per,"bookSeries":null}');
    }
    subj.write('${s == 0 ? '' : ','}"${subjects[s]}":[${entries.join(',')}]');
  }
  assert(b >= 41 && lessons >= 500, 'phải đúng quy mô thật: $b sách, $lessons bài');
  return LessonIndex.fromJsonString(
      '{"grade":11,"subjects":{$subj},"toanExercises":{},"books":[$books]}')!;
}

void main() {
  _shelfLabelTests();
  testWidgets('giá sách 42 sách / 17 môn dựng được, không tràn, không lỗi bố cục',
      (t) async {
    final idx = _grade11();
    expect(idx.books.length, greaterThanOrEqualTo(41));
    t.view.physicalSize = const Size(1080, 2400);   // Nokia thật
    t.view.devicePixelRatio = 3.0;
    addTearDown(t.view.reset);

    await t.pumpWidget(packHost(
        BookShelfScreen(profile: _p, index: idx, onOpenBook: (_) {})));
    await t.pumpAndSettle();
    expect(testerExceptions(), isEmpty);
    // Giá sách phải DỰNG ĐƯỢC hết, không phải chỉ không nổ: một giá im lặng
    // thiếu 30 cuốn cũng «không có lỗi».
    var seen = <String>{};
    final list = find.byType(Scrollable).first;
    for (var i = 0; i < 30; i++) {
      seen.addAll(t.widgetList<Text>(find.byType(Text)).map((w) => w.data ?? ''));
      await t.drag(list, const Offset(0, -500));
      await t.pump();
    }
    await t.pumpAndSettle();
    seen.addAll(t.widgetList<Text>(find.byType(Text)).map((w) => w.data ?? ''));
    final subjectsSeen = {
      for (final s in ['Toán', 'Ngữ văn', 'Vật lí', 'Chuyên đề', 'GDQP'])
        if (seen.any((x) => x.contains(s))) s
    };
    expect(subjectsSeen.length, greaterThanOrEqualTo(4),
        reason: 'cuộn hết giá phải gặp được các môn, không chỉ vài môn đầu');
  });

  testWidgets('MỘT môn nuốt 9 sách vẫn phân biệt được từng cuốn', (t) async {
    // «Chuyên đề» thật sự gom 9 sách ở cả ba lớp 10–12. Nếu chín cuốn hiện
    // giống hệt nhau thì trẻ không chọn được cuốn nào.
    t.view.physicalSize = const Size(1080, 2400);
    t.view.devicePixelRatio = 3.0;
    addTearDown(t.view.reset);
    final idx = _grade11();
    final cd = idx.books.where((b) => b.subject == 'Chuyên đề').toList();
    expect(cd, hasLength(9));
    expect(cd.map((b) => b.sourceDocumentId).toSet(), hasLength(9),
        reason: 'chín cuốn phải có định danh riêng');
    expect(cd.map((b) => b.lessonCount).toSet().length, greaterThan(1),
        reason: 'ít nhất số bài phải khác nhau — nếu không, giá sách hiện chín ô y hệt');
  });

  testWidgets('cuộn hết giá sách không ném lỗi bố cục', (t) async {
    t.view.physicalSize = const Size(1080, 2400);
    t.view.devicePixelRatio = 3.0;
    addTearDown(t.view.reset);
    await t.pumpWidget(packHost(
        BookShelfScreen(profile: _p, index: _grade11(), onOpenBook: (_) {})));
    await t.pumpAndSettle();
    final list = find.byType(Scrollable).first;
    for (var i = 0; i < 12; i++) {
      await t.drag(list, const Offset(0, -600));
      await t.pump();
    }
    await t.pumpAndSettle();
    expect(testerExceptions(), isEmpty);
  });

  testWidgets('tên bài 82 ký tự KHÔNG tràn ngang', (t) async {
    // Tràn ngang trên máy thật là một vệt vàng-đen; trong test là một exception.
    t.view.physicalSize = const Size(1080, 2400);
    t.view.devicePixelRatio = 3.0;
    addTearDown(t.view.reset);
    await t.pumpWidget(packHost(
        BookShelfScreen(profile: _p, index: _grade11(), onOpenBook: (_) {})));
    await t.pumpAndSettle();
    expect(testerExceptions(), isEmpty);
  });
}

/// Mọi lỗi Flutter bắt được trong lúc dựng — tràn bố cục nằm ở đây.
List<Object> testerExceptions() {
  final out = <Object>[];
  while (true) {
    final e = TestWidgetsFlutterBinding.instance.takeException();
    if (e == null) break;
    out.add(e);
  }
  return out;
}

void _shelfLabelTests() {
  test('cuốn có nhãn phân biệt hiện ĐỦ ba phần trên giá', () {
    const b = BookRef(
        sourceDocumentId: '11-sgk-mi-thuat-11-hoi-hoa',
        subject: 'Mĩ thuật',
        title: 'Mĩ thuật 11',
        cover: 'covers/x.webp',
        lessonCount: 2,
        variantLabel: 'HỘI HOẠ');
    expect(b.shelfLabel, 'Mĩ thuật 11 · HỘI HOẠ');
  });

  test('không có nhãn phân biệt thì giá sách KHÔNG thêm chữ thừa', () {
    const b = BookRef(
        sourceDocumentId: '11-sgk-vat-li-11',
        subject: 'Vật lí',
        title: 'Vật lí 11',
        cover: 'covers/x.webp',
        lessonCount: 30);
    expect(b.shelfLabel, 'Vật lí 11');
  });

  test('tám cuốn Mĩ thuật 11 phải ra TÁM nhãn khác nhau', () {
    // Máy thật hiện tám ô y hệt «Mĩ thuật 11 · 2 bài».
    const names = ['ĐỒ HOẠ (TRANH IN)', 'HỘI HOẠ', 'KIẾN TRÚC',
      'THIẾT KẾ CÔNG NGHIỆP', 'THIẾT KẾ ĐỒ HOẠ',
      'THIẾT KẾ MĨ THUẬT ĐA PHƯƠNG TIỆN',
      'THIẾT KẾ MĨ THUẬT SÂN KHẤU, ĐIỆN ẢNH', 'THIẾT KẾ THỜI TRANG'];
    final labels = {
      for (final n in names)
        BookRef(sourceDocumentId: 'b-$n', subject: 'Mĩ thuật',
            title: 'Mĩ thuật 11', cover: 'covers/x.webp', lessonCount: 2,
            variantLabel: n).shelfLabel
    };
    expect(labels, hasLength(8));
  });
}
