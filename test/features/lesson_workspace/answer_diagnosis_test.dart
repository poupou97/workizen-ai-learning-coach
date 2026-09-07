/// ROUND 7 · V2 — **PHẢN HỒI PHỤ THUỘC LỖI** (Founder order 49 §2).
///
/// Đây là test QUYẾT ĐỊNH của vòng này. Yêu cầu Founder nêu ra là một câu
/// phủ định — «không dùng mặc định "Chưa đúng — nhưng gần rồi" cho MỌI đáp án
/// sai» — nên phép kiểm phải so HAI đáp án sai với nhau, chứ không phải xem
/// một đáp án sai có ra chữ hay không.
///
/// A. Ba nhánh là THẬT: gần đúng · sai bản chất · chưa đủ bằng chứng.
/// B. ⭐⭐ Hai phương án sai KHÁC NHAU ⇒ hai lời KHÁC NHAU, và lời ấy là
///    NGUYÊN VĂN sách về đúng cái trẻ chọn.
/// C. Nhánh «sai bản chất» KHÔNG lộ đáp án (thử lại phải còn nghĩa).
/// D. Không có căn cứ ⇒ nói ít đi + nói thẳng «SAM không kết luận».
/// E. Tất định, và không có chữ nào của một bài cụ thể trong mã.
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/content_trust.dart';
import 'package:learning_coach/core/lesson_model/semantic_data.dart';
import 'package:learning_coach/core/lesson_model/tutor_script.dart';
import 'package:learning_coach/features/lesson_workspace/teaching/answer_diagnosis.dart';

import 'support.dart';

/// Bảng bốn cách tách — CÙNG HÌNH DẠNG dữ liệu thật của Bài 17 (bốn thực thể,
/// một chiều «Dùng để tách»), chữ đánh dấu [MẪU] để không ai nhầm là lời sách.
ComparisonSemantic _fourWays() => ComparisonSemantic(
  id: 'cmp-1',
  title: 'Các cách tách chất (mẫu)',
  trust: ContentTrust.fixtureSynthetic,
  derivation: 'synthetic-test',
  entities: const [
    ComparisonEntity(name: 'Lọc', sourceBlockId: 'b-loc'),
    ComparisonEntity(name: 'Lắng', sourceBlockId: 'b-lang'),
    ComparisonEntity(name: 'Cô cạn', sourceBlockId: 'b-cocan'),
    ComparisonEntity(name: 'Chiết', sourceBlockId: 'b-chiet'),
  ],
  dimensions: [
    ComparisonDimension(
      name: 'Dùng để tách',
      cells: const [
        ComparisonValue(
          text: '[MẪU] chất rắn không tan ra khỏi chất lỏng',
          sourceBlockId: 'b-loc',
          grounding: ValueGrounding.cellStated,
        ),
        ComparisonValue(
          text: '[MẪU] chất rắn lơ lửng nặng hơn ra khỏi chất nhẹ hơn',
          sourceBlockId: 'b-lang',
          grounding: ValueGrounding.cellStated,
        ),
        ComparisonValue(
          text: '[MẪU] chất khó bay hơi ra khỏi chất dễ bay hơi',
          sourceBlockId: 'b-cocan',
          grounding: ValueGrounding.cellStated,
        ),
        ComparisonValue(
          text: '[MẪU] hai chất lỏng không tan vào nhau',
          sourceBlockId: 'b-chiet',
          grounding: ValueGrounding.cellStated,
        ),
      ],
    ),
  ],
);

ProcessSemantic _filterProcess() => ProcessSemantic(
  id: 'proc-loc',
  title: 'Lọc nước đục (mẫu)',
  trust: ContentTrust.fixtureSynthetic,
  derivation: 'synthetic-test',
  steps: const [
    ProcessStep(order: 1, text: '· [MẪU] Khuấy đất vào cốc nước.', sourceBlockId: 'p1'),
    ProcessStep(order: 2, text: '· [MẪU] Rót qua phễu có giấy lọc.', sourceBlockId: 'p2'),
  ],
);

AskStep _mcq({
  List<String> options = const ['Lọc', 'Cô cạn', 'Chiết', 'Lắng'],
  List<String> acceptable = const [r'^cô cạn$'],
}) => AskStep(
  id: 'q1',
  prompt: '[MẪU] Làm muối từ nước biển dùng cách nào?',
  options: options,
  acceptable: acceptable,
  hints: const ['[MẪU] gợi ý 1', '[MẪU] gợi ý 2'],
  feedbackMatched: '[MẪU] khớp',
  scaffold: '[MẪU] scaffold',
  keySource: 'synthetic prototype key',
);

AskStep _open() => const AskStep(
  id: 'q2',
  prompt: '[MẪU] Vì sao phải mở khoá từ từ?',
  options: [],
  acceptable: ['dầu.*(lẫn|chảy)'],
  hints: ['[MẪU] gợi ý 1'],
  feedbackMatched: '[MẪU] khớp',
  scaffold: '[MẪU] scaffold',
  keySource: 'synthetic prototype key',
);

AnswerDiagnosis? _d(
  AskStep step,
  String answer, {
  List<SemanticData>? semantic,
  List<String> earlier = const [],
}) => diagnoseAnswer(
  step: step,
  answer: answer,
  semantic: semantic ?? [_filterProcess(), _fourWays()],
  earlierAnswers: earlier,
);

void main() {
  group('A. ba nhánh của order 49 §2 là THẬT, không phải một câu đổi chữ', () {
    test('khớp mẫu ⇒ không có chẩn đoán (phản hồi khớp là việc của runner)', () {
      expect(_d(_mcq(), 'Cô cạn'), isNull);
      expect(_d(_mcq(), '   '), isNull);
    });

    test('sai bản chất ⇒ misconception; không căn cứ ⇒ insufficient; trúng '
        'một phần ⇒ nearMiss', () {
      expect(_d(_mcq(), 'Lọc')!.kind, DiagnosisKind.misconception);
      // «Nam châm» không có trong bảng nào của bài ⇒ SAM không có gì để nói.
      expect(
        _d(_mcq(options: ['Nam châm', 'Cô cạn']), 'Nam châm')!.kind,
        DiagnosisKind.insufficient,
      );
      // Đáp án khoá ghép HAI cách; trẻ mới gọi được MỘT ⇒ gần đúng.
      final two = _mcq(
        options: const [
          'Hoà tan vào nước rồi lọc bỏ cát, sau đó cô cạn lấy muối',
          'Chỉ lọc là xong',
        ],
        acceptable: const [r'^hoà tan vào nước'],
      );
      expect(_d(two, 'Chỉ lọc là xong')!.kind, DiagnosisKind.nearMiss);
    });
  });

  group('B. ⭐⭐ HAI ĐÁP ÁN SAI ⇒ HAI LỜI KHÁC NHAU', () {
    test('ba phương án sai của một câu: ba lời khác nhau, mỗi lời mang NGUYÊN '
        'VĂN sách về ĐÚNG cái trẻ chọn', () {
      final step = _mcq();
      final wrong = ['Lọc', 'Chiết', 'Lắng'];
      final said = {for (final w in wrong) w: _d(step, w)!};

      // 1) ba lời, ba chuỗi — đây là chính yêu cầu Founder nêu.
      final texts = {for (final e in said.entries) e.value.fullText};
      expect(texts.length, 3, reason: 'ba đáp án sai không được chung một lời');

      // 2) mỗi lời NHẮC LẠI lựa chọn của trẻ…
      for (final e in said.entries) {
        expect(e.value.headline, contains('«${e.key}»'));
      }
      // 3) …và mang đúng dòng sách của cách ĐÓ, không phải của cách khác.
      final cmp = _fourWays();
      String cell(String name) => cmp
          .dimensions
          .first
          .values[cmp.entities.indexWhere((x) => x.name == name)]!;
      for (final e in said.entries) {
        expect(e.value.headline, contains(cell(e.key)));
        for (final other in wrong) {
          if (other == e.key) continue;
          expect(
            e.value.fullText,
            isNot(contains(cell(other))),
            reason: 'lời cho «${e.key}» không được mượn dòng của «$other»',
          );
        }
      }
    });

    test('⭐ liên hệ trong bài khác nhau theo lựa chọn: có sơ đồ ⇒ chỉ tới; '
        'không có ⇒ NÓI THẲNG', () {
      // «Lọc» có một quy trình mang đúng từ ấy trong tiêu đề…
      final loc = _d(_mcq(), 'Lọc')!;
      expect(loc.links.map((l) => l.semanticId), contains('proc-loc'));
      expect(loc.linksEmptyNote, isNull);
      // …«Lắng» thì không, và SAM nói ra điều đó thay vì gợi bừa.
      final lang = _d(_mcq(), 'Lắng')!;
      expect(lang.links, isEmpty);
      expect(lang.linksEmptyNote, contains('Lắng'));
      expect(lang.linksEmptyNote, contains('không dựng thêm sơ đồ'));
    });

    test('câu «gần rồi» bị Founder bác KHÔNG xuất hiện ở bất kỳ nhánh nào', () {
      final all = [
        _d(_mcq(), 'Lọc')!,
        _d(_mcq(), 'Chiết')!,
        _d(_mcq(), 'Lắng')!,
        _d(_mcq(options: ['Nam châm', 'Cô cạn']), 'Nam châm')!,
        _d(_open(), 'tại vì thế thôi')!,
        _d(_open(), 'vì nước ở dưới')!,
      ];
      // Chữ cấm: câu mặc định cũ, mọi lời chấm điểm, mọi lời chê tư chất.
      const banned = [
        'gần rồi',
        'gần đúng rồi',
        'Chưa đúng —',
        '%',
        '⭐',
        'điểm',
        'đã thạo',
        'thành thạo',
        'con hiểu rồi',
        'chưa hiểu bài',
        'kém',
        'dở',
        'giỏi',
      ];
      for (final d in all) {
        for (final b in banned) {
          expect(
            d.fullText.toLowerCase(),
            isNot(contains(b.toLowerCase())),
            reason: '«$b» trong: ${d.fullText}',
          );
        }
      }
    });
  });

  group('C. nhánh «sai bản chất» KHÔNG lộ đáp án', () {
    test('⭐ tên phương án đúng không xuất hiện trong lời phản hồi', () {
      for (final w in ['Lọc', 'Chiết', 'Lắng']) {
        final d = _d(_mcq(), w)!;
        expect(
          d.fullText.toLowerCase(),
          isNot(contains('cô cạn')),
          reason: 'lộ đáp án ngay lần sai đầu thì «thử lại» vô nghĩa',
        );
      }
    });

    test('mời THỬ LẠI bằng ĐIỀU KIỆN của chính cái trẻ chọn, không câu chung', () {
      // ⭐⭐ Trước đây dòng này là MỘT CÂU DUY NHẤT cho mọi đáp án sai («con so
      // dòng sách với câu hỏi»). Đúng, nhưng giống nhau ở mọi lựa chọn nên nó
      // vẫn là nghi thức: trẻ đã đọc lời sách rồi mà vẫn chọn sai thì lời mời
      // so lại không thêm gì. Nay nó hỏi thẳng vào ĐIỀU KIỆN của cách trẻ chọn.
      final d = _d(_mcq(), 'Chiết')!;
      expect(d.retry, isNotNull);
      expect(d.retry, contains('thứ cần tách ở câu này'));
      // Cụm điều kiện phải là chữ NGUYÊN VĂN của sách về CHÍNH cái trẻ chọn.
      expect(d.retry, contains('không tan vào nhau'));
      expect(d.sourceBlockId, 'b-chiet');
    });

    test('⭐ hai đáp án sai KHÁC NHAU ⇒ hai lời mời thử lại KHÁC NHAU', () {
      // Đây là phép kiểm chống quay lại câu chung: nếu ai đó thay bằng một
      // dòng cố định, test này đỏ ngay.
      final a = _d(_mcq(), 'Chiết')!;
      final b = _d(_mcq(), 'Lọc')!;
      expect(a.retry, isNotNull);
      expect(b.retry, isNotNull);
      expect(a.retry, isNot(b.retry),
          reason: 'lời mời thử lại phải bám điều kiện của lựa chọn, không phải '
              'một câu dùng chung');
    });

    test('⭐ lời mời thử lại KHÔNG được lộ đáp án', () {
      for (final wrong in const ['Chiết', 'Lọc', 'Lắng']) {
        final d = _d(_mcq(), wrong);
        if (d?.retry == null) continue;
        expect(d!.retry!.toLowerCase(), isNot(contains('cô cạn')), reason: wrong);
      }
    });

    test('chọn LẠI đúng cái vừa sai ⇒ SAM nói «vẫn chọn», không lặp y nguyên',
        () {
      final first = _d(_mcq(), 'Lọc')!;
      final again = _d(_mcq(), 'Lọc', earlier: const ['Lọc'])!;
      expect(first.headline, startsWith('Con chọn'));
      expect(again.headline, startsWith('Con vẫn chọn'));
      expect(again.fullText, isNot(first.fullText));
    });

    test('sách để trống ô ấy ⇒ nói VÌ SAO trống, không bịa lời sách', () {
      final blank = ComparisonSemantic(
        id: 'cmp-blank',
        title: 'Bảng thiếu ô (mẫu)',
        trust: ContentTrust.fixtureSynthetic,
        derivation: 'synthetic-test',
        entities: const [
          ComparisonEntity(name: 'Lọc', sourceBlockId: 'b1'),
          ComparisonEntity(name: 'Cô cạn', sourceBlockId: 'b2'),
        ],
        dimensions: [
          ComparisonDimension(
            name: 'Dùng để tách',
            cells: const [
              ComparisonValue(
                text: null,
                sourceBlockId: 'b1',
                grounding: ValueGrounding.cellStated,
              ),
              ComparisonValue(
                text: '[MẪU] chất khó bay hơi',
                sourceBlockId: 'b2',
                grounding: ValueGrounding.cellStated,
              ),
            ],
          ),
        ],
      );
      final d = _d(_mcq(), 'Lọc', semantic: [blank])!;
      expect(d.kind, DiagnosisKind.misconception);
      expect(d.headline, contains('để trống'));
      expect(d.headline, contains('không đoán hộ'));
    });
  });

  group('D. «chưa đủ bằng chứng» — KHÔNG suy diễn trạng thái hiểu bài', () {
    test('⭐⭐ câu tự viết không có chữ nào đối chiếu được ⇒ SAM nói KHÔNG BIẾT',
        () {
      final d = _d(_open(), 'tại vì thế thôi')!;
      expect(d.kind, DiagnosisKind.insufficient);
      expect(d.limitNote, isNotNull);
      expect(d.limitNote, contains('KHÔNG BIẾT'));
      expect(d.limitNote, contains('không đoán'));
      // và KHÔNG có câu nào kết luận trẻ hiểu / chưa hiểu
      expect(d.fullText, isNot(contains('con chưa hiểu')));
      expect(d.retry, isNotNull);
    });

    test('có chữ đối chiếu được ⇒ nearMiss KỂ RA đúng những chữ ấy, và vẫn nói '
        'rõ «chữ trùng chưa phải là hiểu»', () {
      final d = _d(_open(), 'vì hạt cát nặng hơn nước nên chìm')!;
      expect(d.kind, DiagnosisKind.nearMiss);
      expect(d.headline, contains('nước'));
      expect(d.limitNote, contains('so CHỮ, không'));
      // liên hệ trỏ về đúng sơ đồ có chứa những chữ ấy
      expect(d.links, isNotEmpty);
    });

    test('hư từ KHÔNG được tính là «đối chiếu được» — chúng có ở mọi trang', () {
      // toàn hư từ ⇒ không có chữ nào đáng kể ⇒ nhánh «chưa đủ bằng chứng»
      expect(
        _d(_open(), 'và là của để thì có không cho')!.kind,
        DiagnosisKind.insufficient,
      );
      expect(echoedWords('và là của để thì', [_fourWays()]), isEmpty);
    });

    test('MCQ không có căn cứ: SAM nói ít đi, KHÔNG kết luận', () {
      final d = _d(_mcq(options: ['Nam châm', 'Cô cạn']), 'Nam châm')!;
      expect(d.kind, DiagnosisKind.insufficient);
      expect(d.facts, isEmpty, reason: 'không có lời sách thì không có ô nào');
      expect(d.limitNote, contains('KHÔNG kết luận'));
      expect(d.headline, contains('«Nam châm»'));
    });
  });

  group('E. tất định + không danh tính bài', () {
    test('cùng đầu vào ⇒ cùng đầu ra (view dựng lại được khi vẽ)', () {
      for (final w in ['Lọc', 'Chiết', 'Nam châm']) {
        final step = _mcq(options: ['Lọc', 'Chiết', 'Nam châm', 'Cô cạn']);
        expect(_d(step, w)!.fullText, _d(step, w)!.fullText);
      }
    });

    test('so khớp tên là NGUYÊN TỪ, hai chiều', () {
      // chiều A: tên thực thể nằm trong một lựa chọn dài
      final long = _mcq(
        options: const ['Chiết bằng phễu chiết', 'Cô cạn'],
      );
      expect(_d(long, 'Chiết bằng phễu chiết')!.headline, contains('«Chiết»'));
      // chiều B: tên thực thể có hậu tố, lựa chọn là tên trần
      final suffixed = ComparisonSemantic(
        id: 'cmp-suffix',
        title: 'Bảng mẫu',
        trust: ContentTrust.fixtureSynthetic,
        derivation: 'synthetic-test',
        entities: const [
          ComparisonEntity(name: 'Lọc (mẫu)', sourceBlockId: 'b1'),
          ComparisonEntity(name: 'Cô cạn (mẫu)', sourceBlockId: 'b2'),
        ],
        dimensions: [
          ComparisonDimension(
            name: 'Dùng để tách',
            cells: const [
              ComparisonValue(
                text: '[MẪU] chất rắn không tan',
                sourceBlockId: 'b1',
                grounding: ValueGrounding.cellStated,
              ),
              ComparisonValue(
                text: '[MẪU] chất khó bay hơi',
                sourceBlockId: 'b2',
                grounding: ValueGrounding.cellStated,
              ),
            ],
          ),
        ],
      );
      expect(
        _d(_mcq(), 'Lọc', semantic: [suffixed])!.headline,
        contains('«Lọc (mẫu)»'),
      );
      // KHÔNG khớp chuỗi con: «lọc» trong «phin lọc cà phê» là một từ riêng,
      // nhưng «Lọ» thì không được khớp vào «Lọc».
      expect(
        _d(_mcq(options: ['Lọ', 'Cô cạn']), 'Lọ')!.kind,
        DiagnosisKind.insufficient,
      );
    });

    test('⭐⭐ mã của thư mục teaching/ không khoá theo danh tính bài, và không '
        'chạm LessonDocument', () {
      final dir = Directory('lib/features/lesson_workspace/teaching');
      expect(dir.existsSync(), isTrue);
      final identity = RegExp(
        r'(KHTN|LS&ĐL|Bài\s*\d+|bai-\d+|0\d-sgk-|lessonNo\s*==|slotKey'
        r'|doc\.book\s*==|\.lessonNo\b)',
      );
      var scanned = 0;
      for (final f in dir.listSync(recursive: true).whereType<File>()) {
        if (!f.path.endsWith('.dart')) continue;
        scanned++;
        expect(
          f.readAsStringSync(),
          isNot(contains('lesson_document.dart')),
          reason: '${f.path}: lời phản hồi chỉ được dựng từ dữ liệu CÓ KIỂU',
        );
        final code = f
            .readAsLinesSync()
            .where((l) => !l.trimLeft().startsWith('//'))
            .where((l) => !l.trimLeft().startsWith('///'));
        for (final line in code) {
          expect(
            identity.hasMatch(line),
            isFalse,
            reason: '${f.path} khoá theo danh tính bài: «${line.trim()}»',
          );
        }
      }
      expect(scanned, greaterThanOrEqualTo(2));
    });
  });

  group('F. FIXTURE THẬT — Bài 17, bốn phương án của câu 1', () {
    test('⭐⭐ bốn lựa chọn ⇒ BỐN lời khác nhau, mỗi lời là lời sách về đúng '
        'cách trẻ chọn (skip khi máy chưa có fixture thật)', () {
      final doc = loadRealDocOrSkip();
      if (doc == null) return;
      final q1 = doc.tutorScript!.asks.first;
      expect(q1.options.length, greaterThanOrEqualTo(4));
      final wrong = [
        for (final o in q1.options)
          if (!answerMatches(o, q1.acceptable)) o,
      ];
      expect(wrong.length, 3, reason: 'ba phương án nhiễu');
      final said = <String, AnswerDiagnosis>{};
      for (final w in wrong) {
        final d = diagnoseAnswer(
          step: q1,
          answer: w,
          semantic: doc.semantic,
        );
        expect(d, isNotNull, reason: '«$w» phải nhận được một lời');
        said[w] = d!;
      }
      expect(
        {for (final d in said.values) d.fullText}.length,
        wrong.length,
        reason: 'ĐÂY LÀ YÊU CẦU QUYẾT ĐỊNH: không hai lời nào giống nhau',
      );
      for (final e in said.entries) {
        expect(e.value.kind, DiagnosisKind.misconception);
        expect(e.value.headline, contains('«${e.key}»'));
        expect(
          e.value.fullText.toLowerCase(),
          isNot(contains('cô cạn')),
          reason: 'không lộ đáp án',
        );
      }
      // In ra để dán vào tài liệu — bảng so sánh cạnh nhau của Founder.
      for (final e in said.entries) {
        // ignore: avoid_print
        print('--- ${e.key} ---\n${e.value.fullText}\n');
      }
    });

    test('câu tự viết của bài thật: không có chữ đối chiếu được ⇒ «chưa đủ '
        'bằng chứng»', () {
      final doc = loadRealDocOrSkip();
      if (doc == null) return;
      final open = [
        for (final a in doc.tutorScript!.asks)
          if (!a.isChoice) a,
      ];
      expect(open, isNotEmpty);
      final d = diagnoseAnswer(
        step: open.first,
        answer: 'zzzz qqqq',
        semantic: doc.semantic,
      )!;
      expect(d.kind, DiagnosisKind.insufficient);
      expect(d.limitNote, contains('KHÔNG BIẾT'));
    });
  });
}
