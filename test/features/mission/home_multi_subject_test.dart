/// ⭐⭐ FOUNDER ORDER 50 — «AI LEARNING HOME CHO MỘT NGÀY HỌC NHIỀU MÔN».
///
/// Bài kiểm này giữ SÁU điều, và cả sáu đều là điều Founder gọi tên:
///
/// §2 §4  HÀNG THẺ TRƯỢT NGANG có thật, thẻ chính 75–85 % viewport, thẻ kế bên
///        HÉ RA (trẻ phải thấy là có thể vuốt), và vuốt được sang thẻ 2.
/// §3     Thẻ trả lời ĐÚNG bốn câu: MÔN · BÀI · TRẠNG THÁI · VIỆC TIẾP THEO.
/// §5     MULTI-SUBJECT CONTEXT + SINGLE NEXT ACTION — cả màn ĐÚNG MỘT nút tô
///        đặc; không bao giờ năm CTA cạnh tranh.
/// §9  ⛔ KHÔNG BỊA TRẠNG THÁI HỌC. Từ vựng bị khoá; `ĐÃ HIỂU` · `70%` ·
///        `GIỎI` · `MASTERED` · sao · điểm bị cấm bằng tên trên CẢ MÀN.
/// ⛔     KHÔNG BỊA DỮ LIỆU. Môn chưa có bài thì thẻ NÓI THẲNG là chưa có, và
///        con số nó nêu là con số mục lục THẬT — không phải tiến độ.
/// §12 D  LUẬT CHỌN MỘT VIỆC là hàm THUẦN, xếp hạng những việc ĐÃ ĐƯỢC TÍNH —
///        không phải một động cơ đề xuất thứ hai.
library;

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/agenda/learning_agenda.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/next_action.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/runtime_plan.dart';
import 'package:learning_coach/features/mission/home_cards.dart';
import 'package:learning_coach/features/mission/mission_center_screen.dart';
import 'package:learning_coach/features/mission/mission_data.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';

import '../lesson_workspace/support.dart';

const _g6 = LearnerProfile(learnerId: 'l6', displayName: 'Na', grade: 6);
const _khtnBook = '06-sgk-khoa-hoc-tu-nhien-6';

/// Mục lục THU NHỎ của lớp 6 — cùng HÌNH DẠNG pack thật (nhiều môn, đa số
/// chỉ có mục lục, một môn có việc làm được).
LessonIndex _index() => LessonIndex.fromJsonString('''
{"grade":6,"subjects":{
   "KHTN":[{"sourceDocumentId":"$_khtnBook","volume":null,
     "lessons":[{"no":11,"title":"Oxygen","pageStart":40},
                {"no":17,"title":"Tách chất khỏi hỗn hợp","pageStart":60}]}],
   "Toán":[{"sourceDocumentId":"06-sgk-toan-6-tap-mot","volume":null,
     "lessons":[{"no":1,"title":"Tập hợp","pageStart":7},
                {"no":2,"title":"Cách ghi số","pageStart":11},
                {"no":3,"title":"Thứ tự","pageStart":14}]}],
   "Ngữ văn":[{"sourceDocumentId":"06-sgk-ngu-van-6-tap-mot","volume":null,
     "lessons":[{"no":1,"title":"Bài học đường đời","pageStart":12}]}],
   "Tin học":[{"sourceDocumentId":"06-sgk-tin-hoc-6","volume":null,
     "lessons":[{"no":1,"title":"Thông tin","pageStart":5},
                {"no":2,"title":"Xử lí thông tin","pageStart":9}]}]},
 "khoaExperiments":[
  {"subject":"KHTN","book":"$_khtnBook","lesson":11,"page":41,
   "title":"Oxygen","chuanBi":"que đóm","tienHanh":["Đốt."]}]}
''')!;

Future<MissionData> _data({LessonIndex? index}) => buildMissionFromStore(
  profile: _g6,
  store: JsonlLearnerStore(),
  now: DateTime(2026, 9, 6, 19),
  index: index ?? _index(),
);

List<HomeShelfSubject> _shelf([LessonIndex? idx]) {
  final i = idx ?? _index();
  return [
    for (final s in i.subjects.keys)
      HomeShelfSubject(
        subject: s,
        listedLessons: i.listedLessonCountFor(s),
        openableLessons: i.openableLessonCountFor(s),
      ),
  ];
}

HomeLessonThread _thread(
  LessonDocument d, {
  Set<WorkspaceView> opened = const {},
}) =>
    HomeLessonThread(
      doc: d,
      openedViews: opened,
      next: founderNextAction(d, seen: opened),
    );

LessonDocument _readOnly(LessonDocument d, {int grade = 5}) => LessonDocument(
      schema: d.schema,
      book: '05-sgk-lich-su-va-dia-li-5',
      bookTitle: 'LS&ĐL 5',
      subject: 'LS&ĐL',
      grade: grade,
      lessonNo: 8,
      title: 'Đấu tranh giành độc lập',
      provenance: d.provenance,
      blocks: d.blocks,
    );

Future<void> _pump(
  WidgetTester t, {
  List<HomeLessonThread> threads = const [],
  List<HomeShelfSubject>? shelf,
  MissionData? data,
  VoidCallback? onShelf,
  void Function(LessonDocument, WorkspaceView?)? onLesson,
  bool nokia = false,
}) async {
  t.view.physicalSize = nokia ? const Size(1080, 1920) : const Size(1080, 5000);
  t.view.devicePixelRatio = nokia ? 3.0 : 2.75;
  addTearDown(t.view.reset);
  await t.pumpWidget(
    fixtureHost(
      MissionCenterScreen(
        data: data ?? await _data(),
        learnerGrade: 6,
        lessonThreads: threads,
        shelfSubjects: shelf ?? _shelf(),
        onOpenSubjects: onShelf ?? () {},
        onOpenWorkspaceLesson: (d, {at}) => onLesson?.call(d, at),
      ),
    ),
  );
  await t.pumpAndSettle();
}

/// Vuốt hàng thẻ sang phải [n] lần. `PageView` chỉ DỰNG thẻ đang thấy và thẻ
/// hé bên cạnh — thẻ thứ ba thật sự CHƯA ở trên màn, nên bài kiểm phải đi tới
/// nó bằng cử chỉ, đúng như trẻ.
Future<void> _swipe(WidgetTester t, int n) async {
  for (var i = 0; i < n; i++) {
    await t.drag(
        find.byKey(MissionCenterScreen.todayRowKey), const Offset(-400, 0));
    await t.pumpAndSettle();
  }
}

void main() {
  // ══ LUẬT THUẦN — kiểm được không cần dựng một widget nào ═══════════════
  group('§9 · §12 D — LUẬT THẺ LÀ HÀM THUẦN', () {
    test('⭐⭐ trạng thái suy từ ĐÚNG MỘT tín hiệu (đã mở tab), theo bảng', () {
      final d = loadSyntheticDoc(); // 3 cách học: Đọc · Trực quan · Học với SAM
      HomeCardState st(Set<WorkspaceView> o) =>
          lessonCardState(HomeLessonThread(doc: d, openedViews: o));

      expect(st(const {}), HomeCardState.chuaBatDau);
      expect(st({WorkspaceView.read}), HomeCardState.daMoDoc);
      expect(st({WorkspaceView.visual}), HomeCardState.daXemTrucQuan);
      // Ví dụ CHÍNH FOUNDER nêu ở §3: đã mở Đọc + Trực quan ⇒ «ĐANG HỌC».
      expect(
        st({WorkspaceView.read, WorkspaceView.visual}),
        HomeCardState.dangHoc,
      );
      // Mở hết ⇒ TIẾP TỤC, KHÔNG PHẢI «xong»: mở không phải hiểu.
      expect(
        st({WorkspaceView.read, WorkspaceView.visual, WorkspaceView.tutor}),
        HomeCardState.tiepTuc,
      );
    });

    test('⭐ dấu vết của bài KHÁC không bao giờ đếm vào thẻ này', () {
      // Bài chỉ có Đọc; dấu vết nói đã mở Trực quan (của một bài khác).
      final readOnly = _readOnly(loadSyntheticDoc());
      final t = HomeLessonThread(
        doc: readOnly,
        openedViews: {WorkspaceView.visual},
      );
      expect(t.openedHere, isEmpty);
      expect(lessonCardState(t), HomeCardState.chuaBatDau);
    });

    test('⛔⭐⭐ MÔN CHƯA CÓ BÀI: thẻ NÓI THẲNG, và không được gọi mục lục là '
        '«bài học được»', () {
      final none = cardForShelfSubject(const HomeShelfSubject(
          subject: 'Toán', listedLessons: 43, openableLessons: 0));
      expect(none.isRealLesson, isFalse);
      expect(none.lessonLine, isNull);
      expect(none.state, HomeCardState.chuaBatDau);
      expect(none.detailLine, contains('SAM chưa xếp sẵn bài nào ở môn này'));
      // 43 là số MỤC LỤC, không phải số bài mở làm được ⇒ câu phải nói «mục
      // lục». Đây đúng chỗ dễ nói dối nhất: gộp hai con số thành một.
      expect(none.detailLine, contains('mục lục 43 bài'));
      expect(none.nextLabel, 'Xem mục lục');

      final some = cardForShelfSubject(const HomeShelfSubject(
          subject: 'KHTN', listedLessons: 55, openableLessons: 4));
      expect(some.detailLine, contains('4 bài con mở làm được'));
      expect(some.nextLabel, 'Mở giá sách');
    });

    test('⭐⭐ thứ tự hàng: bài đúng lớp → bài lớp khác → môn giá sách theo '
        '(mở được ↓, mục lục ↓, tên môn)', () {
      final b17 = loadSyntheticDoc(); // lớp 6
      final b8 = _readOnly(b17); // lớp 5
      final row = buildHomeCards(
        // cố ý đảo: luật phải thắng thứ tự truyền vào
        threads: [_thread(b8), _thread(b17)],
        shelf: _shelf(),
        learnerGrade: 6,
      );
      final ids = row.cards.map((c) => c.id).toList();
      expect(ids.first, b17.slotKey, reason: 'bài của lớp con đứng đầu');
      expect(ids[1], b8.slotKey, reason: 'bài lớp khác vẫn trong hàng');
      // KHTN đã có bài ⇒ KHÔNG được lặp lại thành thẻ giá sách.
      expect(ids, isNot(contains('shelf:KHTN')));
      // Toán (3 mục lục) trước Tin học (2), Tin học trước Ngữ văn (1).
      expect(ids.sublist(2), ['shelf:Toán', 'shelf:Tin học', 'shelf:Ngữ văn']);
    });

    test('⭐ trần thẻ: hàng cắt ở kHomeCardLimit và NÓI RA số môn bị cắt', () {
      final shelf = [
        for (var i = 0; i < 12; i++)
          HomeShelfSubject(
              subject: 'Môn $i', listedLessons: 12 - i, openableLessons: 0),
      ];
      final row = buildHomeCards(
        threads: [_thread(loadSyntheticDoc())],
        shelf: shelf,
        learnerGrade: 6,
      );
      expect(row.cards.length, kHomeCardLimit);
      expect(row.totalSubjects, 13);
      expect(row.hiddenSubjects, 13 - kHomeCardLimit);
    });

    test('⭐⭐ CHỌN MỘT VIỆC — bậc thang, và nó chỉ XẾP HẠNG việc đã được tính',
        () {
      final b17 = loadSyntheticDoc();
      final b8 = _readOnly(b17);

      // Bậc 2 — sách đúng lớp thắng, kể cả khi bài lớp khác đứng trước VÀ
      // đang dở còn bài của lớp con thì chưa mở gì.
      final r1 = buildHomeCards(
        threads: [
          _thread(b8, opened: {WorkspaceView.read}),
          _thread(b17),
        ],
        learnerGrade: 6,
      );
      expect(r1.cards[promotedCardIndex(r1.cards)!].id, b17.slotKey);

      // Bậc 1 — thẻ rỗng-trung-thực KHÔNG BAO GIỜ được lên tầng 2: nó không
      // có việc tiếp theo nào để nêu, và bịa ra một cái là phạm §9.
      final onlyShelf =
          buildHomeCards(threads: const [], shelf: _shelf(), learnerGrade: 6);
      expect(onlyShelf.cards, isNotEmpty);
      expect(promotedCardIndex(onlyShelf.cards), isNull);

      // Bậc 1 — mạch học CHƯA nối động cơ cũng không được lên: Home không tự
      // nghĩ ra đề xuất (fail closed).
      final noEngine = buildHomeCards(
        threads: [HomeLessonThread(doc: b17)],
        learnerGrade: 6,
      );
      expect(promotedCardIndex(noEngine.cards), isNull);

      // Bậc 4 — cùng lớp, cùng loại việc ⇒ bài ĐANG DỞ thắng bài chưa mở.
      final other = LessonDocument(
        schema: b17.schema,
        book: '06-sgk-toan-6-tap-mot',
        bookTitle: 'Toán 6',
        subject: 'Toán',
        grade: 6,
        lessonNo: 1,
        title: 'Tập hợp',
        provenance: b17.provenance,
        blocks: b17.blocks,
      );
      final r2 = buildHomeCards(
        threads: [_thread(other), _thread(b17, opened: {WorkspaceView.read})],
        learnerGrade: 6,
      );
      expect(r2.cards[promotedCardIndex(r2.cards)!].id, b17.slotKey);
    });

    test('⛔⭐⭐ KHÔNG CÓ ĐỘNG CƠ THỨ HAI: `home_cards.dart` không gọi động cơ, '
        'không đọc trace — nó chỉ nhận và xếp hạng', () {
      // Chỉ soi MÃ, không soi chú thích: chú thích được phép NHẮC TÊN thứ mà
      // tệp này bị cấm dùng (đó chính là chỗ ghi lý do cấm). Cùng kỷ luật mà
      // `assist_layer.dart` phải theo (workspace_density_test §3).
      final src = File('lib/features/mission/home_cards.dart')
          .readAsLinesSync()
          .where((l) => !l.trimLeft().startsWith('///'))
          .where((l) => !l.trimLeft().startsWith('//'))
          .join('\n');
      for (final forbidden in [
        'founderNextAction',
        'nextActionFor',
        'nextBestLessonAction',
        'WorkspaceTrace',
        'LearnerStore',
      ]) {
        expect(src, isNot(contains(forbidden)),
            reason: 'home_cards chỉ được TRÌNH BÀY / XẾP HẠNG NextAction có sẵn');
      }
    });

    test('⛔⭐⭐ `CÓ THỂ LUYỆN` chưa được gán ở đâu — và đó là CHỦ Ý', () {
      // Founder cho phép nhãn này (§9), nhưng bản dựng hôm nay KHÔNG đo được
      // «sẵn sàng luyện tập»: vòng luyện tập thuộc nhánh SAM teaching. Gán nó
      // bây giờ là suy diễn. Ai bắt đầu gán phải sửa BÀI KIỂM NÀY và nói ra
      // bằng chứng của mình.
      final d = loadSyntheticDoc();
      final all = <HomeCardState>{
        for (final o in [
          <WorkspaceView>{},
          {WorkspaceView.read},
          {WorkspaceView.visual},
          {WorkspaceView.tutor},
          {WorkspaceView.read, WorkspaceView.visual},
          {WorkspaceView.read, WorkspaceView.tutor},
          {WorkspaceView.visual, WorkspaceView.tutor},
          {WorkspaceView.read, WorkspaceView.visual, WorkspaceView.tutor},
        ])
          lessonCardState(HomeLessonThread(doc: d, openedViews: o)),
        cardForShelfSubject(const HomeShelfSubject(
                subject: 'Toán', listedLessons: 1, openableLessons: 0))
            .state,
      };
      expect(all, isNot(contains(HomeCardState.coTheLuyen)));
      // …và từ vựng vẫn đúng nguyên văn Founder cho phép.
      expect(
        HomeCardState.values.map((s) => s.label).toSet(),
        {
          'ĐANG HỌC',
          'CHƯA BẮT ĐẦU',
          'ĐÃ MỞ ĐỌC',
          'ĐÃ XEM TRỰC QUAN',
          'CÓ THỂ LUYỆN',
          'TIẾP TỤC',
        },
      );
    });
  });

  group('⛔ HAI CON SỐ CHO MỘT GIÁ SÁCH — lỗi tìm ra khi đọc pack THẬT', () {
    test('⭐⭐ môn đánh số LẠI theo chủ đề (GDTC): «mục lục N bài» phải khớp '
        'con số Giá sách in ra, không được gộp theo số bài', () {
      // Pack lớp 6 thật: GDTC có 24 bản ghi mục lục nhưng chỉ 4 SỐ BÀI phân
      // biệt (sách đánh số lại theo từng chủ đề). Bản đầu của
      // `listedLessonCountFor` khử trùng theo (sách, số bài) ⇒ thẻ Home nói
      // «mục lục 4 bài» còn Giá sách ngay sau một chạm nói «24 bài». Hai con
      // số cho cùng một giá sách, trên hai màn.
      //
      // `_dedupeLessons` ở đầu `lesson_index.dart` đã viết sẵn lý do:
      // «Gộp theo số là xoá bài của trẻ.»
      final idx = LessonIndex.fromJsonString('''
{"grade":6,"subjects":{"GDTC":[{"sourceDocumentId":"06-sgk-giao-duc-the-chat-6",
  "volume":null,"lessons":[
   {"no":1,"title":"Chủ đề 1 · Bài 1","pageStart":5},
   {"no":2,"title":"Chủ đề 1 · Bài 2","pageStart":9},
   {"no":1,"title":"Chủ đề 2 · Bài 1","pageStart":21},
   {"no":2,"title":"Chủ đề 2 · Bài 2","pageStart":25},
   {"no":1,"title":"Chủ đề 3 · Bài 1","pageStart":40}]}]}}
''')!;
      expect(idx.listedLessonCountFor('GDTC'), 5,
          reason: 'gộp theo số bài là xoá bài của trẻ');
      expect(idx.openableLessonCountFor('GDTC'), 0);
      // …và bản ghi TRÙNG HỆT vẫn bị bỏ (luật cũ giữ nguyên).
      final dup = LessonIndex.fromJsonString('''
{"grade":6,"subjects":{"X":[{"sourceDocumentId":"b","volume":null,"lessons":[
   {"no":1,"title":"A","pageStart":5},
   {"no":1,"title":"A","pageStart":5}]}]}}
''')!;
      expect(dup.listedLessonCountFor('X'), 1);
    });
  });

  // ══ MÀN HÌNH ═════════════════════════════════════════════════════════════
  group('§2 · §4 — HÀNG THẺ TRƯỢT NGANG', () {
    testWidgets('⭐⭐ thẻ chính chiếm 75–85 % viewport và thẻ kế bên HÉ RA',
        (t) async {
      await _pump(t, threads: [_thread(loadSyntheticDoc())], nokia: true);
      final row = find.byKey(MissionCenterScreen.todayRowKey);
      expect(row, findsOneWidget);
      final screen = t.view.physicalSize.width / t.view.devicePixelRatio;
      final page = find.descendant(of: row, matching: find.byType(PageView));
      final first = t.getRect(
        find.byKey(MissionCenterScreen.smartCardKey(loadSyntheticDoc().slotKey)),
      );
      expect(page, findsOneWidget);
      final share = first.width / screen;
      expect(share, greaterThan(.70), reason: 'thẻ chính quá hẹp');
      expect(share, lessThan(.86), reason: 'thẻ chính ăn hết chiều ngang ⇒ '
          'trẻ không biết là có thể vuốt');
      // Còn CHỖ ở mép phải cho thẻ kế bên hé ra.
      expect(first.right, lessThan(screen - 8));
    });

    testWidgets('⭐⭐ vuốt sang thẻ 2 — và thẻ 2 là môn KHÁC, không phải cùng '
        'một bài lặp lại', (t) async {
      final b17 = loadSyntheticDoc();
      await _pump(t, threads: [_thread(b17)], nokia: true);
      // Thẻ 2 (Toán) là thẻ RỖNG-TRUNG-THỰC — nó có mặt và nói thật.
      final toan = find.byKey(MissionCenterScreen.smartCardKey('shelf:Toán'));
      expect(toan, findsOneWidget);
      await t.drag(
          find.byKey(MissionCenterScreen.todayRowKey), const Offset(-400, 0));
      await t.pumpAndSettle();
      final r = t.getRect(toan);
      final screen = t.view.physicalSize.width / t.view.devicePixelRatio;
      expect(r.left, lessThan(screen * .2),
          reason: 'sau khi vuốt, thẻ 2 phải thành thẻ chính');
      expect(
        find.descendant(
            of: toan, matching: find.text('SAM chưa xếp sẵn bài nào')),
        findsOneWidget,
      );
      expect(
        find.descendant(
            of: toan, matching: find.textContaining('mục lục 3 bài')),
        findsOneWidget,
      );
    });

    testWidgets('⭐ chạm thẻ RỖNG mở GIÁ SÁCH (việc thật duy nhất có), không '
        'mở một bài không tồn tại', (t) async {
      var shelf = 0;
      LessonDocument? lesson;
      await _pump(
        t,
        threads: [_thread(loadSyntheticDoc())],
        onShelf: () => shelf++,
        onLesson: (d, _) => lesson = d,
      );
      await _swipe(t, 1);
      await t.tap(find.byKey(MissionCenterScreen.smartCardKey('shelf:Toán')));
      await t.pumpAndSettle();
      expect(shelf, 1);
      expect(lesson, isNull);
    });

    testWidgets('⭐ chạm thẻ CÓ BÀI mở đúng bài ĐÚNG cách học động cơ nêu',
        (t) async {
      LessonDocument? doc;
      WorkspaceView? at;
      await _pump(
        t,
        threads: [_thread(loadSyntheticDoc())],
        onLesson: (d, v) {
          doc = d;
          at = v;
        },
      );
      await t.tap(find.byKey(
          MissionCenterScreen.smartCardKey(loadSyntheticDoc().slotKey)));
      await t.pumpAndSettle();
      expect(doc?.slotKey, loadSyntheticDoc().slotKey);
      expect(at, WorkspaceView.read, reason: 'R2 — chưa mở gì thì Đọc trước');
    });

    testWidgets('⭐ có môn không lọt vào hàng ⇒ màn NÓI RA, không lặng lẽ giấu',
        (t) async {
      final shelf = [
        for (var i = 0; i < 10; i++)
          HomeShelfSubject(
              subject: 'Môn $i', listedLessons: 10 - i, openableLessons: 0),
      ];
      await _pump(t, threads: [_thread(loadSyntheticDoc())], shelf: shelf);
      final line = find.byKey(MissionCenterScreen.rowOverflowKey);
      expect(line, findsOneWidget);
      expect(t.widget<Text>(line).data, contains('5 môn nữa'));
    });
  });

  group('§3 — THẺ TRẢ LỜI ĐÚNG BỐN CÂU', () {
    testWidgets('⭐⭐ MÔN · BÀI · TRẠNG THÁI · VIỆC TIẾP THEO, và ví dụ §3 của '
        'Founder hiện đúng như ông viết', (t) async {
      final d = loadSyntheticDoc();
      await _pump(t, threads: [
        _thread(d, opened: {WorkspaceView.read, WorkspaceView.visual}),
      ]);
      final card = find.byKey(MissionCenterScreen.smartCardKey(d.slotKey));
      Finder inCard(Finder f) => find.descendant(of: card, matching: f);
      expect(inCard(find.text('KHTN 6')), findsOneWidget); // MÔN
      expect(inCard(find.textContaining('Bài 17')), findsOneWidget); // BÀI
      expect(inCard(find.text('ĐANG HỌC')), findsOneWidget); // TRẠNG THÁI
      expect(inCard(find.text('Đã mở: Đọc · Trực quan')), findsOneWidget);
      expect(inCard(find.text('Tiếp theo: 🦉 Học với SAM →')),
          findsOneWidget); // VIỆC TIẾP THEO
    });

    testWidgets('⭐ thẻ KHÔNG mang chương / số trang / lời SAM / thanh tiến độ '
        '— chúng là thứ cấp (§7)', (t) async {
      final d = loadSyntheticDoc();
      await _pump(t, threads: [_thread(d)]);
      final card = find.byKey(MissionCenterScreen.smartCardKey(d.slotKey));
      expect(find.descendant(of: card, matching: find.textContaining('Chương')),
          findsNothing);
      expect(find.descendant(of: card, matching: find.textContaining('trang')),
          findsNothing);
      expect(
          find.descendant(of: card, matching: find.textContaining('đã mở 0/')),
          findsNothing);
      // …nhưng chúng VẪN CÓ MẶT ở tầng dưới — thu nhỏ, không phải xoá.
      expect(find.textContaining('Chương IV'), findsOneWidget);
      expect(find.byKey(MissionCenterScreen.progressKey), findsOneWidget);
    });
  });

  group('§7 — HERO CO LẠI, KHÔNG LẶP (lỗi tìm ra TRÊN MÁY THẬT)', () {
    testWidgets('⭐⭐ tầng 2 KHÔNG in lại nguyên tiêu đề của Smart Card ngay '
        'trên nó — nó chỉ ĐỊNH DANH bài', (t) async {
      // Máy thật lượt 1 (`01-home.png`): «KHTN 6 · Bài 17 · TÁCH CHẤT KHỎI
      // HỖN HỢP» in HAI lần trên một màn, ăn hai dòng ở tầng 2. §7: «Không
      // cần lặp… Ưu tiên: title · state · next action.»
      final d = loadSyntheticDoc();
      await _pump(t, threads: [_thread(d)]);
      final full = t
          .widgetList<Text>(find.descendant(
              of: find.byKey(MissionCenterScreen.smartCardKey(d.slotKey)),
              matching: find.byType(Text)))
          .map((w) => w.data ?? '')
          .firstWhere((s) => s.startsWith('Bài 17'));
      final tier2 = t
          .widgetList<Text>(find.descendant(
              of: find.byKey(MissionCenterScreen.samSuggestionKey),
              matching: find.byType(Text)))
          .map((w) => w.data ?? '')
          .join(' | ');
      expect(tier2, isNot(contains(full)),
          reason: 'tầng 2 lặp nguyên tiêu đề của thẻ — lỗi 01-home.png');
      expect(tier2, contains('KHTN 6 · Bài 17'));
    });

    testWidgets('⭐⭐ thẻ có thêm dòng «sách lớp N» chỉ được MỘT hàng cho dòng '
        '«đã mở gì» — chữ bị xén ngang là chữ không đọc được', (t) async {
      // Máy thật lượt 1 (`02-swipe-card2.png`): ở chiều cao thẻ cũ, dòng này
      // bị CẮT NGANG THÂN CHỮ trên thẻ LS&ĐL 5 — thẻ duy nhất có bốn dòng
      // cộng dòng sự thật về lớp.
      final b8 = _readOnly(loadSyntheticDoc());
      await _pump(t, threads: [_thread(loadSyntheticDoc()), _thread(b8)]);
      // Thẻ KHÔNG có dòng «sách lớp N» vẫn được hai hàng — đo trước khi vuốt,
      // vì `PageView` huỷ thẻ đã rời màn.
      final own = t.widget<Text>(find.descendant(
        of: find.byKey(
            MissionCenterScreen.smartCardKey(loadSyntheticDoc().slotKey)),
        matching: find.textContaining('SAM đã xếp sẵn'),
      ));
      expect(own.maxLines, 2);
      await _swipe(t, 1);
      final detail = t.widget<Text>(find.descendant(
        of: find.byKey(MissionCenterScreen.smartCardKey(b8.slotKey)),
        matching: find.textContaining('SAM đã xếp sẵn'),
      ));
      expect(detail.maxLines, 1);
      expect(detail.overflow, TextOverflow.ellipsis);
    });
  });

  group('§5 — MỘT NEXT ACTION', () {
    testWidgets('⭐⭐ cả màn ĐÚNG MỘT nút tô đặc, và nó là việc tiếp theo',
        (t) async {
      await _pump(t, threads: [_thread(loadSyntheticDoc())]);
      expect(find.byType(FilledButton), findsOneWidget);
      expect(find.byKey(MissionCenterScreen.nextActionCtaKey), findsOneWidget);
    });

    testWidgets('⭐⭐ VUỐT KHÔNG ĐỔI VIỆC SAM GỢI Ý — hàng thẻ là context '
        'switcher, không phải bộ chọn đề xuất', (t) async {
      final d = loadSyntheticDoc();
      await _pump(t, threads: [_thread(d)], nokia: true);
      String cta() => t
          .widget<Text>(find.descendant(
              of: find.byKey(MissionCenterScreen.nextActionCtaKey),
              matching: find.byType(Text)))
          .data!;
      final before = cta();
      await t.drag(
          find.byKey(MissionCenterScreen.todayRowKey), const Offset(-400, 0));
      await t.pumpAndSettle();
      expect(cta(), before);
      expect(find.byType(FilledButton), findsOneWidget);
    });

    testWidgets('⭐⭐ BẰNG CHỨNG ĐÃ CHẤM VẪN THẮNG BÀI THỬ NGHIỆM: agenda ôn '
        'tập chiếm tầng 2, bài fixture lùi về hàng thẻ', (t) async {
      // Thứ tự đã chốt từ Convergence §10 (bằng chứng → TKB → làm dở). Order
      // 50 không đụng tới nó, nên nó phải sống sót qua đợt sắp lại IA này.
      final data = await _data();
      final urgent = MissionData(
        studentName: data.studentName,
        decision: data.decision,
        reviews: data.reviews,
        unobservedCaseNames: data.unobservedCaseNames,
        upcomingSubjects: data.upcomingSubjects,
        nextActionTitle: data.nextActionTitle,
        nextActionReason: data.nextActionReason,
        scaleLessonCount: data.scaleLessonCount,
        agenda: const NextBestLearningAction(
          kind: AgendaActionKind.review,
          reason: 'Con làm được bài này nhờ SAM giúp — mình gặp lại nhé.',
        ),
      );
      await _pump(t, threads: [_thread(loadSyntheticDoc())], data: urgent);
      expect(find.byKey(MissionCenterScreen.samSuggestionKey), findsNothing);
      expect(find.text('VIỆC SAM ĐỀ XUẤT'), findsOneWidget);
      expect(find.byType(FilledButton), findsOneWidget);
      // Bài fixture KHÔNG biến mất — nó vẫn là context ở tầng 1.
      expect(
        find.byKey(
            MissionCenterScreen.smartCardKey(loadSyntheticDoc().slotKey)),
        findsOneWidget,
      );
    });
  });

  group('§9 — KHÔNG BỊA TRẠNG THÁI HỌC', () {
    testWidgets('⛔⭐⭐ CẢ MÀN không có `ĐÃ HIỂU` · `%` · `GIỎI` · `MASTERED` · '
        'sao · điểm', (t) async {
      final d = loadSyntheticDoc();
      await _pump(t, threads: [
        _thread(d, opened: {WorkspaceView.read, WorkspaceView.visual}),
        _thread(_readOnly(d)),
      ]);
      final all = t
          .widgetList<Text>(find.byType(Text))
          .map((w) => (w.data ?? '').toLowerCase())
          .join(' | ');
      for (final banned in [
        'đã hiểu',
        '%',
        'giỏi',
        'mastered',
        'đã thạo',
        'thành thạo',
        'hoàn thành bài',
        'điểm số',
        '⭐',
        '★',
      ]) {
        expect(all, isNot(contains(banned)), reason: 'Home hứa mastery: $banned');
      }
    });

    testWidgets('⛔⭐ mọi chữ trạng thái trên hàng thẻ đến TỪ TỪ VỰNG Founder',
        (t) async {
      final d = loadSyntheticDoc();
      await _pump(t, threads: [
        _thread(d, opened: {WorkspaceView.read}),
        _thread(_readOnly(d)),
      ]);
      final labels = HomeCardState.values.map((s) => s.label).toSet();
      // Mỗi thẻ phải mang ĐÚNG MỘT nhãn, và nhãn ấy phải nằm trong từ vựng.
      // Đi tới từng thẻ bằng cử chỉ — thẻ chưa dựng thì chưa ở trên màn.
      for (final (i, id) in [
        d.slotKey,
        '05-sgk-lich-su-va-dia-li-5#8',
        'shelf:Toán',
      ].indexed) {
        await _swipe(t, i == 0 ? 0 : 1);
        final card = find.byKey(MissionCenterScreen.smartCardKey(id));
        expect(card, findsOneWidget, reason: id);
        final texts = t
            .widgetList<Text>(
                find.descendant(of: card, matching: find.byType(Text)))
            .map((w) => w.data ?? '')
            .where(labels.contains)
            .toList();
        expect(texts.length, 1, reason: '$id mang ${texts.length} nhãn trạng thái');
      }
    });
  });
}
