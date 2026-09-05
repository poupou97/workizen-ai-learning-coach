/// ROUND 3 B5 — mã nội bộ không lọt ra màn khi CÓ tên chắc; không chắc thì
/// giữ mã, không bịa.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/subject_id.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';
import 'package:learning_coach/features/subjects/source_gallery_screen.dart';
import 'package:learning_coach/features/subjects/subject_display.dart';
import 'package:learning_coach/features/subjects/subject_home_screen.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';

import '../../support/pack_bundle.dart';

void main() {
  test('mã môn → tên môn; mã lạ giữ nguyên (không bịa)', () {
    expect(subjectDisplayName('khtn'), 'Khoa học tự nhiên');
    expect(subjectDisplayName('dia-li'), 'Địa lí');
    expect(subjectDisplayName('toan'), 'Toán');
    expect(subjectDisplayName('mon-la-hoac'), 'mon-la-hoac');
  });

  test('mã môn sinh bởi subjectIdOf cho các môn trong pack đều có tên', () {
    for (final s in [
      'Toán',
      'Tiếng Việt',
      'Ngữ văn',
      'Tiếng Anh',
      'KHTN',
      'Khoa học',
      'Vật lí',
      'Hoá học',
      'Sinh học',
      'Lịch sử',
      'Địa lí',
      'Tin học',
      'Công nghệ',
    ]) {
      final id = subjectIdOf(s);
      expect(
        subjectDisplayName(id),
        isNot(id),
        reason: '$s → $id chưa có tên trẻ đọc',
      );
    }
  });

  test('dòng nguồn: có tên sách ⇒ «SGK Tên · trang N»; không ⇒ giữ mã', () {
    expect(
      childSourceLine(
        sourceDocumentId: '05-sgk-khoa-hoc-5',
        pagePrinted: 16,
        bookTitles: const {'05-sgk-khoa-hoc-5': 'Khoa học 5'},
      ),
      'SGK Khoa học 5 · trang 16',
    );
    expect(
      childSourceLine(sourceDocumentId: '05-sgk-khoa-hoc-5', pagePrinted: 16),
      '05-sgk-khoa-hoc-5 · trang 16',
    );
    expect(
      childSourceLine(sourceDocumentId: '05-sgk-khoa-hoc-5', pagePrinted: null),
      '05-sgk-khoa-hoc-5',
      reason: 'không có trang in ⇒ không in «trang null»',
    );
  });

  testWidgets('gallery nhận bookTitles ⇒ dòng nguồn trẻ đọc', (t) async {
    const a = IndexedSourceAsset(
      subject: 'Khoa học',
      assetType: 'EXPERIMENT',
      asset: 'khoa-5-p017-tach-muoi-hinh5.png',
      sourceDocumentId: '05-sgk-khoa-hoc-5',
      pagePdf: 17,
      pagePrinted: 16,
      bboxFrac: [0.14, 0.409, 0.93, 0.618],
      extractionVersion: 'source-crop-v1',
      printedCaption: 'Hình 5',
    );
    await t.pumpWidget(
      packHost(
        const SourceGalleryScreen(
          subject: 'Khoa học',
          assets: [a],
          bookTitles: {'05-sgk-khoa-hoc-5': 'Khoa học 5'},
        ),
      ),
    );
    await t.pump();
    expect(find.text('SGK Khoa học 5 · trang 16'), findsOneWidget);
    expect(find.textContaining('05-sgk-'), findsNothing);
  });

  group('⭐ Subject Home «Hình trong sách» không lấy hình LỚP KHÁC', () {
    const p = LearnerProfile(learnerId: 'l', displayName: 'M', grade: 6);
    LessonIndex idx({required String assetBook}) => LessonIndex.fromJsonString(
      '''
{"grade":6,"subjects":{
  "Toán":[{"sourceDocumentId":"06-sgk-toan-6-tap-mot","volume":"1",
    "lessons":[{"no":1,"title":"TẬP HỢP","pageStart":7}]}]},
 "toanExercises":{},
 "books":[{"sourceDocumentId":"06-sgk-toan-6-tap-mot","subject":"Toán",
   "grade":6,"title":"Toán 6","volumeLabel":"Tập 1","volume":1,
   "cover":"covers/t.webp","lessonCount":1}],
 "sourceAssets":[{"asset":"toan-5-p023-chia-banh-phan-so.png","subject":"Toán",
   "assetType":"FIGURE","sourceDocumentId":"$assetBook","pagePdf":23,
   "pagePrinted":22,"bboxFrac":[0.1,0.3,0.8,0.5],"extractionVersion":"v1"}]}
''',
    )!;

    testWidgets('hình của sách lớp 5 trong pack lớp 6 ⇒ tile KHÔNG hiện', (
      t,
    ) async {
      await t.pumpWidget(
        packHost(
          SubjectHomeScreen(
            profile: p,
            store: JsonlLearnerStore(),
            index: idx(assetBook: '05-sgk-toan-5-tap-mot'),
            subject: 'Toán',
          ),
        ),
      );
      await t.pump();
      expect(find.textContaining('Hình trong sách'), findsNothing);
    });

    testWidgets('hình của đúng sách lớp 6 ⇒ tile hiện, nguồn có tên sách', (
      t,
    ) async {
      await t.pumpWidget(
        packHost(
          SubjectHomeScreen(
            profile: p,
            store: JsonlLearnerStore(),
            index: idx(assetBook: '06-sgk-toan-6-tap-mot'),
            subject: 'Toán',
          ),
        ),
      );
      await t.pump();
      expect(find.textContaining('Hình trong sách'), findsOneWidget);
      await t.tap(find.textContaining('Hình trong sách'));
      await t.pumpAndSettle();
      expect(find.text('SGK Toán 6 · Tập 1 · trang 22'), findsOneWidget);
    });
  });
}
