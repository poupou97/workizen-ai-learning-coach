library;

import 'dart:convert';
import 'dart:io';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/core/tutor/output_guard.dart';

const facts = DerivedFacts(
  commonDenominator: 20,
  answerForms: ['19/20'],
  intermediateForms: ['15/20', '4/20'],
);

const levelOf = {
  's01-first-hint': SupportLevel.hint,
  's02-worked-step': SupportLevel.workedStep,
  's03-reveal-blocked': SupportLevel.hint,
  's04-full-solution': SupportLevel.fullSolution,
  's05-exam-mode': SupportLevel.none,
  's06-bcnn-request': SupportLevel.hint,
  's07-praise': SupportLevel.none,
  's08-provenance': SupportLevel.hint,
  's09-unexpected': SupportLevel.hint,
  's10-cross-turn': SupportLevel.workedStep,
};

/// ⭐⭐ WAL-223 S10 — «GUARD: chặn 0/0 transcript» RỒI EXIT 0.
///
/// Hai lối để sự vắng mặt đội lốt thành công ở đây:
///   1. thư mục run rỗng (hoặc không tồn tại) ⇒ in 0/0 rồi thoát êm;
///   2. `catch (_) { continue; }` vứt transcript không parse được mà KHÔNG
///      tăng bất kỳ bộ đếm nào — một lô hỏng hoàn toàn trông y hệt một lô sạch.
///
/// Nay cả hai đều được ĐẾM và NÓI RA, và 0 transcript hợp lệ là exit ≠ 0.
void main() {
  final dir = Directory('poc-out/shadow/runs');
  if (!dir.existsSync()) {
    stdout.writeln(
      'GUARD: KHÔNG XÁC MINH ĐƯỢC — không có ${dir.path}. '
      'Chưa chạy thì không phải là đạt.',
    );
    exitCode = 2;
    return;
  }
  final files = dir.listSync().whereType<File>().toList()
    ..sort((a, b) => a.path.compareTo(b.path));
  var blocked = 0, total = 0, unreadable = 0;
  final bySid = <String, int>{};
  for (final f in files) {
    final rec = jsonDecode(f.readAsStringSync()) as Map<String, dynamic>;
    String text;
    try {
      text =
          (jsonDecode(rec['raw'] as String) as Map<String, dynamic>)['result']
              as String;
    } catch (_) {
      // Đếm, đừng nuốt: transcript hỏng là một sự kiện, không phải số không.
      unreadable++;
      stdout.writeln('UNREADABLE ${f.path}');
      continue;
    }
    final sid = rec['scenario'] as String;
    final v = validateTutorOutput(
      text: text,
      maxAllowed: levelOf[sid]!,
      facts: facts,
      examMode: sid == 's05-exam-mode',
      // s07: trẻ tự nêu «19/20 đúng không?» — echo không phải reveal
      childStatedFacts: sid == 's07-praise' ? const ['19/20', '20'] : const [],
    );
    total++;
    if (!v.allowed) {
      blocked++;
      bySid[sid] = (bySid[sid] ?? 0) + 1;
      stdout.writeln('BLOCK $sid#${rec['run']}: ${v.blockedReasons}');
    }
  }
  stdout.writeln(
    'GUARD: chặn $blocked/$total transcript; theo scenario: $bySid'
    '${unreadable > 0 ? "; $unreadable transcript KHÔNG ĐỌC ĐƯỢC" : ""}',
  );
  if (total == 0) {
    stdout.writeln(
      'GUARD: KHÔNG XÁC MINH ĐƯỢC — 0 transcript hợp lệ trong '
      '${files.length} tệp. «chặn 0/0» không chứng minh guard hoạt động.',
    );
    exitCode = 2;
    return;
  }
  if (unreadable > 0) {
    stdout.writeln(
      'GUARD: $unreadable/${files.length} tệp không parse được — '
      'kết quả trên chỉ nói về $total tệp còn lại, không nói về cả lô.',
    );
    exitCode = 1;
  }
}
