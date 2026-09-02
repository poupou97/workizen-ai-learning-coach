library;

import 'dart:convert';
import 'dart:io';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/core/tutor/output_guard.dart';

const facts = DerivedFacts(
    commonDenominator: 20,
    answerForms: ['19/20'],
    intermediateForms: ['15/20', '4/20']);

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

void main() {
  final files = Directory('poc-out/shadow/runs')
      .listSync()
      .whereType<File>()
      .toList()
    ..sort((a, b) => a.path.compareTo(b.path));
  var blocked = 0, total = 0;
  final bySid = <String, int>{};
  for (final f in files) {
    final rec = jsonDecode(f.readAsStringSync()) as Map<String, dynamic>;
    String text;
    try {
      text = (jsonDecode(rec['raw'] as String)
          as Map<String, dynamic>)['result'] as String;
    } catch (_) {
      continue;
    }
    final sid = rec['scenario'] as String;
    final v = validateTutorOutput(
      text: text,
      maxAllowed: levelOf[sid]!,
      facts: facts,
      examMode: sid == 's05-exam-mode',
      // s07: trẻ tự nêu «19/20 đúng không?» — echo không phải reveal
      childStatedFacts:
          sid == 's07-praise' ? const ['19/20', '20'] : const [],
    );
    total++;
    if (!v.allowed) {
      blocked++;
      bySid[sid] = (bySid[sid] ?? 0) + 1;
      stdout.writeln('BLOCK $sid#${rec['run']}: ${v.blockedReasons}');
    }
  }
  stdout.writeln('GUARD: chặn $blocked/$total transcript; theo scenario: $bySid');
}
