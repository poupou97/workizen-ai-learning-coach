/// WAL-87 — Fading simulation: ±1 (Wood) vs 4 policy đối chứng.
///
/// CHẠY TRÊN KERNEL THẬT: sự kiện phát ra là LearningEvent đúng taxonomy,
/// ước lượng là replayMastery + ConservativeBktPolicy — không chép lại số học.
///
/// ⚠️ GIẢ ĐỊNH KHAI BÁO (không phải sự thật đo được):
/// ảnh hưởng của mức hỗ trợ lên (a) xác suất HỌC và (b) xác suất TRẢ LỜI ĐÚNG
/// khi chưa biết. Vì là giả định, quét 3 kịch bản × 3 tốc độ học — nếu kết
/// luận đổi theo kịch bản thì phải BÁO ĐÚNG NHƯ VẬY.
///
/// Chạy: dart run tool/sim/fading_sim.dart > poc-out/sim/fading-sim-out.txt
// ignore_for_file: avoid_print — tool CLI, print là giao diện.
library;

import 'dart:convert';
import 'dart:io';
import 'dart:math';

import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/evidence_weighting.dart';
import 'package:learning_coach/core/student/mastery.dart';

// ---------- học sinh mô phỏng ----------

/// P(trả lời đúng | CHƯA biết, mức hỗ trợ). full≈0.95: chép lời giải vừa đọc.
const answerBoost = {
  SupportLevel.none: 0.10,
  SupportLevel.hint: 0.25,
  SupportLevel.workedStep: 0.50,
  SupportLevel.fullSolution: 0.95,
};

/// Ba KỊCH BẢN về ảnh hưởng của hỗ trợ lên P(học) — hệ số nhân trên pLearn.
const learnScenarios = {
  // VanLehn assistance dilemma: gợi ý đúng lúc giúp học; xem trọn lời giải
  // thì học thụ động, kém hơn tự vật lộn có dẫn dắt.
  'help-helps': {
    SupportLevel.none: 1.0,
    SupportLevel.hint: 1.5,
    SupportLevel.workedStep: 2.0,
    SupportLevel.fullSolution: 1.2,
  },
  // Hỗ trợ không ảnh hưởng gì tới học — chỉ ảnh hưởng trả lời.
  'help-neutral': {
    SupportLevel.none: 1.0,
    SupportLevel.hint: 1.0,
    SupportLevel.workedStep: 1.0,
    SupportLevel.fullSolution: 1.0,
  },
  // ⭐ Kịch bản mà giả thuyết Wood THỰC SỰ sống trong đó (ZPD): vật lộn
  // không dẫn dắt dạy được RẤT ÍT; hỗ trợ đúng nấc giữ trẻ trong vùng học được.
  'zpd-flail-futile': {
    SupportLevel.none: 0.25,
    SupportLevel.hint: 1.5,
    SupportLevel.workedStep: 2.0,
    SupportLevel.fullSolution: 1.2,
  },
  // Cực đoan bất lợi cho hỗ trợ: lời giải trọn vẹn làm HẠI việc học.
  'full-hurts': {
    SupportLevel.none: 1.0,
    SupportLevel.hint: 1.3,
    SupportLevel.workedStep: 1.5,
    SupportLevel.fullSolution: 0.4,
  },
};

class SimStudent {
  SimStudent(this.pLearn, this.boost, this.rng);
  final double pLearn;
  final Map<SupportLevel, double> boost;
  final Random rng;
  bool known = false;
  static const slip = 0.10;

  bool answer(SupportLevel s) => known
      ? rng.nextDouble() > slip
      : rng.nextDouble() < answerBoost[s]!;

  /// Cơ hội học sau MỖI lần chạm bài (kể cả trả lời sai — vật lộn cũng là học).
  void maybeLearn(SupportLevel s) {
    if (!known && rng.nextDouble() < (pLearn * boost[s]!).clamp(0.0, 1.0)) {
      known = true;
    }
  }
}

// ---------- 5 policy ----------

typedef Policy = SupportLevel Function(SupportLevel current, bool? lastCorrect);

final policies = <String, Policy>{
  // GIẢ THUYẾT (Wood contingent): sai → +1 nấc, đúng → −1 nấc.
  'wood-±1': (cur, last) {
    if (last == null) return SupportLevel.none;
    final i = SupportLevel.values.indexOf(cur);
    return SupportLevel.values[
        (last ? i - 1 : i + 1).clamp(0, SupportLevel.values.length - 1)];
  },
  // Phản mẫu Photomath: sai một lần → xem trọn lời giải, mãi mãi.
  'jump-to-full': (cur, last) =>
      (last == false || cur == SupportLevel.fullSolution)
          ? SupportLevel.fullSolution
          : SupportLevel.none,
  'never-help': (cur, last) => SupportLevel.none,
  'fixed-hint': (cur, last) => SupportLevel.hint,
  'random': (cur, last) => SupportLevel
      .values[_sharedRng.nextInt(SupportLevel.values.length)],
};
final _sharedRng = Random(20260901);

// ---------- một phiên học ----------

class EpisodeResult {
  int attemptsToKnown = -1; // -1 = chưa học được trong budget
  int timeToIndependence = -1; // lần thử đầu của chuỗi 3 đúng-độc-lập liên tiếp
  int independentEvents = 0, totalAnswerEvents = 0;
  double posterior = 0;
  bool claimedOld = false; // gate V1: pM≥0.85 + ≥2 độc lập (kernel trước ADR-007)
  bool claimedNew = false; // gate ADR-007: cần 2 + supported~/4 độc lập
  bool trueKnown = false;
}

EpisodeResult runEpisode(Policy policy, SimStudent st, {int budget = 20}) {
  const p = BktParams.freeResponse;
  var log = EvidenceLog.empty('sim-case');
  var support = SupportLevel.none;
  bool? last;
  final r = EpisodeResult();
  var indepStreak = 0;
  var t = DateTime(2026, 9, 1);

  for (var i = 0; i < budget; i++) {
    support = policy(support, last);
    final correct = st.answer(support);
    // sự kiện đúng taxonomy — hỗ trợ do HỆ chủ động đặt ⇒ hintShown đi trước
    if (support != SupportLevel.none && log.events.isEmpty ||
        support != SupportLevel.none &&
            log.events.isNotEmpty &&
            log.events.last.kind != EvidenceKind.hintShown) {
      log = log.append(LearningEvent(
          eventId: 'e${log.events.length}',
          skillCaseId: 'sim-case',
          kind: EvidenceKind.hintShown,
          correct: null,
          at: t = t.add(const Duration(minutes: 1))));
    }
    final kind = support == SupportLevel.none
        ? EvidenceKind.independentAttempt
        : (correct ? EvidenceKind.postHintSuccess : EvidenceKind.guidedAttempt);
    log = log.append(LearningEvent(
        eventId: 'e${log.events.length}',
        skillCaseId: 'sim-case',
        kind: kind,
        correct: correct,
        at: t = t.add(const Duration(minutes: 2))));
    r.totalAnswerEvents++;
    if (kind == EvidenceKind.independentAttempt) {
      r.independentEvents++;
      indepStreak = correct ? indepStreak + 1 : 0;
      if (indepStreak >= 3 && r.timeToIndependence < 0) {
        r.timeToIndependence = i + 1;
      }
    } else {
      indepStreak = 0;
    }
    st.maybeLearn(support);
    if (st.known && r.attemptsToKnown < 0) r.attemptsToKnown = i + 1;
    last = correct;
  }

  final m = replayMastery(log, p);
  r.posterior = m.pMastery;
  r.claimedOld = m.pMastery >= 0.85 && m.evidenceCount >= 2;
  r.claimedNew = m.pMastery >= 0.85 &&
      m.evidenceCount >= 2 + m.supportedCount ~/ 4;
  r.trueKnown = st.known;
  return r;
}

// ---------- quần thể + báo cáo ----------

void main() {
  const n = 800;
  final out = <Map<String, Object>>[];
  print('WAL-87 fading sim · $n học sinh/ô · budget 20 lần thử/phiên\n');
  for (final sc in learnScenarios.entries) {
    for (final pLearn in [0.05, 0.15, 0.30]) {
      print('── kịch bản ${sc.key} · pLearn $pLearn ──');
      print('policy         học-đc  tớiĐộcLập  %evidĐộcLập  FALSE-TRUSTED  MISSED');
      for (final pol in policies.entries) {
        var known = 0, indep = 0, indepEv = 0, totEv = 0;
        var ftO = 0, clO = 0, msO = 0, ftN = 0, clN = 0, msN = 0, trueN = 0;
        for (var i = 0; i < n; i++) {
          final st =
              SimStudent(pLearn, sc.value, Random(7919 * i + pol.key.hashCode));
          final r = runEpisode(pol.value, st);
          if (r.trueKnown) trueN++;
          if (r.attemptsToKnown > 0) known++;
          if (r.timeToIndependence > 0) indep++;
          indepEv += r.independentEvents;
          totEv += r.totalAnswerEvents;
          if (r.claimedOld) { clO++; if (!r.trueKnown) ftO++; }
          if (r.trueKnown && !r.claimedOld) msO++;
          if (r.claimedNew) { clN++; if (!r.trueKnown) ftN++; }
          if (r.trueKnown && !r.claimedNew) msN++;
        }
        final ftRate = clO == 0 ? 0.0 : ftO / clO;
        final missRate = trueN == 0 ? 0.0 : msO / trueN;
        final ftRateN = clN == 0 ? 0.0 : ftN / clN;
        final missRateN = trueN == 0 ? 0.0 : msN / trueN;
        print('${pol.key.padRight(14)} '
            '${(known / n * 100).toStringAsFixed(0).padLeft(5)}%  '
            '${(indep / n * 100).toStringAsFixed(0).padLeft(8)}%  '
            '${(indepEv / totEv * 100).toStringAsFixed(0).padLeft(10)}%  '
            '${(ftRate * 100).toStringAsFixed(1).padLeft(5)}%→${(ftRateN * 100).toStringAsFixed(1)}%  '
            '${(missRate * 100).toStringAsFixed(0).padLeft(3)}%→${(missRateN * 100).toStringAsFixed(0)}%');
        out.add({
          'scenario': sc.key, 'pLearn': pLearn, 'policy': pol.key,
          'learnedRate': known / n, 'independenceRate': indep / n,
          'independentEvidenceShare': indepEv / totEv,
          'falseTrustedRateOld': ftRate, 'missedRateOld': missRate,
          'falseTrustedRateNew': ftRateN, 'missedRateNew': missRateN,
        });
      }
      print('');
    }
  }
  File('poc-out/sim/fading-sim.json')
      .writeAsStringSync(const JsonEncoder.withIndent(' ').convert(out));
  print('JSON: poc-out/sim/fading-sim.json');
}
