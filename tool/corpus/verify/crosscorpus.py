#!/usr/bin/env python3
"""Round 5 · Lane A4 — signal **`D.cross_corpus`**: consistency against our own SGK/SGV corpus.

Founder: *«cross-corpus verification is HIGHER PRIORITY than internet search … if «Lý Thái Tổ» appears
correctly many times and one occurrence reads «Lý Thái Tô», that is strong anomaly evidence. But frequency
≠ truth — it is a verification signal.»*

Everything in this module is built around taking that last sentence literally.

## What Lane C already measured, and what this changes

Lane C shipped a narrow form of this signal (`lanec.tone-majority-v1`, book-scoped, token-level,
tone-marks-only) and measured it against a human print read of LS&ĐL 5 Bài 8:
**precision 0.889 · recall 0.533 · false-correction rate 0.111** — and its one false correction rewrote a
**person's name**, «Đăng Khoa» → «Đặng Khoa». Three changes here, each answering one of those limits:

1. **Context, not token frequency.** Unigram frequency is not merely weak, it is *actively wrong*: the
   corpus writes `đầu` 30,232× and `đấu` 5,627×, so a majority rule "corrects" the correct «cuộc đấu
   tranh» into «cuộc đầu tranh». The unit of evidence is the **n-gram in its context** — `cuộc đấu` vs
   `cuộc đầu` — never the syllable. Three of the five Founder cases (`Cộng hoà`, `bản sắc`, `Lý Thái Tổ`)
   are *invisible* to token frequency because both variants are common, valid Vietnamese words.
2. **Corpus scope, not book scope.** 62,729 pages / 531 books, so «unattested» means unattested in the
   whole of K-12, and «attested» can require independent books rather than one repeated page.
3. **A proper-noun sub-class with a stricter bar**, and its false-correction rate reported separately.
   The prior is measured from the corpus itself (`index.key_proper_ratio`), so it works inside an ALL-CAPS
   heading where the surface tells you nothing: `đặng` 0.951 · `hán` 0.928 · `đằng` 0.468 vs `đấu` 0.015.

## What it refuses to do

* **Tone-placement variants are not errors.** `hoà`/`hòa`, `thuỷ`/`thủy` are two valid orthographies; the
  index normalises them together, so this signal *structurally cannot* propose that "correction". Lane C
  measured it as one of its 15 slips; it is a display-fidelity question, not a meaning question.
* **It never validates itself.** The repairer emits layer `D`; the validator here refuses any candidate
  whose only support is layer `D`. That is A1's `independent_support(exclude_layers=…)` contract, and it
  is the rule that saved Lane C from its proper-noun false correction.
* **It does not correct what it cannot explain.** When the observed form is unattested but no alternative
  is well enough attested, the output is an `AnomalySignal` (→ `SUSPECT`), not a guess. Detection and
  proposal are separate acts and are measured separately.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # tool/corpus

from repair import model, registry  # noqa: E402

from . import index as ix  # noqa: E402
from .trust import AnomalySignal, EvidenceRef  # noqa: E402

SIGNAL_ID = 'D.cross_corpus'
FC_TONE = 'vi_tone_disagreement'          # the class Lane C already uses — register, do not fork
RULE_STRICT = 'xcorpus.context-unattested-v1'
RULE_DOMINANT = 'xcorpus.context-dominant-v1'
VALIDATOR_ID = 'xcorpus.independent-context-v1'


# --------------------------------------------------------------------------- policy
@dataclass(frozen=True)
class Policy:
    """Every number here is a **research** parameter of a *verification* signal. None of them is a
    production trust threshold, and the lane reports a family of settings rather than one tuned point
    (Lane A3's rule, and the 97-row set is an evaluation set, not a tuning set)."""

    ngram: int = 2
    #: strict rule — the observed n-gram must be entirely unattested in 62,729 pages
    max_observed_ctx: int = 0
    min_alt_ctx: int = 8
    min_alt_books: int = 3
    #: recall rule — the observed n-gram is attested but overwhelmed
    dominant_max_observed: int = 2
    dominant_ratio: float = 25.0
    #: proper-noun sub-class (Lane C's measured failure): a name may legitimately be rare
    proper_threshold: float = 0.45
    pn_min_alt_ctx: int = 40
    pn_min_alt_books: int = 10
    pn_max_observed_unigram: int = 5
    pn_allow_dominant: bool = False       # names get the strict rule only
    #: **name-internal evidence.** Evidence about a name must come from the name, not from the function
    #: word beside it. When the context partner is itself an informatively capitalised token — «Thái» in
    #: «Lý Thái Tô» — the pair is part of the name and the bar can be the ordinary strict one at this
    #: level. When it is not — «Theo» in «(Theo Đăng Khoa, …)» — the signal must abstain, which is exactly
    #: what stops Lane C's measured false correction «Đăng Khoa» → «Đặng Khoa» from happening here.
    pn_internal_min_alt_ctx: int = 20
    pn_internal_min_alt_books: int = 3
    #: fallback when a token has no usable context at all (block of one word, first token of a fragment)
    unigram_fallback: bool = True
    unigram_max_observed: int = 0         # the form must be absent from the whole corpus
    unigram_min_dominant: int = 200
    #: a form the corpus never writes at all is an anomaly even when nothing can be proposed
    anomaly_max_unigram: int = 0
    #: **the contradicting-evidence veto.** If ANY context of the OBSERVED token is itself well attested,
    #: the observed text is a phrase the corpus knows and must not be "corrected". Measured on Lane C's
    #: Bài 8: «đã phất cờ» and «về hưởng ứng» are rare *left* bigrams and very common *right* ones, and
    #: without this veto both correct phrases were rewritten. This is the Founder's «store contradicting
    #: evidence» doing real work rather than being a field nobody reads.
    veto_observed_support: int = 3

    def label(self):
        return (f'ctx{self.ngram}/obs<={self.max_observed_ctx}/alt>={self.min_alt_ctx}'
                f'@{self.min_alt_books}bk/pn>={self.pn_min_alt_ctx}@{self.pn_min_alt_books}bk'
                f'{"/dominant" if self.dominant_ratio else ""}')


STRICT = Policy(dominant_ratio=0.0)                       # strict only, no dominant rule
DEFAULT = Policy()
RECALL = Policy(min_alt_ctx=4, min_alt_books=2, dominant_max_observed=3, dominant_ratio=12.0)


# --------------------------------------------------------------------------- finding
@dataclass(frozen=True)
class Finding:
    """One token position the cross-corpus signal has something to say about."""
    i: int
    observed: str
    proposed: str | None
    rule: str
    context: str                          # the n-gram that decided it, e.g. 'cuộc —'
    observed_ctx_count: int
    alt_ctx_count: int
    alt_ctx_books: int
    proper_ratio: float | None
    is_proper: bool
    supporting: Sequence[EvidenceRef] = ()
    contradicting: Sequence[EvidenceRef] = ()
    strength: float = 0.0
    reason: str = ''

    @property
    def proposes(self):
        return bool(self.proposed)

    def to_json(self):
        return dict(i=self.i, observed=self.observed, proposed=self.proposed, rule=self.rule,
                    context=self.context, observed_ctx_count=self.observed_ctx_count,
                    alt_ctx_count=self.alt_ctx_count, alt_ctx_books=self.alt_ctx_books,
                    proper_ratio=self.proper_ratio, is_proper=self.is_proper,
                    strength=round(self.strength, 3), reason=self.reason,
                    supporting=[e.to_json() for e in self.supporting],
                    contradicting=[e.to_json() for e in self.contradicting])


# --------------------------------------------------------------------------- verifier
class CrossCorpusVerifier:
    """Ask the corpus about every token of a text. Returns `Finding`s; never touches the text."""

    def __init__(self, idx, scan=None, policy=DEFAULT):
        self.idx = idx
        self.scan = scan
        self.policy = policy

    # ---- what the scan must be asked for, so a caller can batch one pass over 62,729 pages
    def context_keys(self, text):
        stream = ix.tokens_with_adjacency(text)
        toks = [t for t, _ in stream]
        adj = [a for _, a in stream]
        keys = set()
        for i, t in enumerate(toks):
            for f, _, _ in self.idx.variants(t):
                if i and adj[i]:
                    keys.add((ix.key_of(toks[i - 1]), ix.key_of(f)))
                if i + 1 < len(toks) and adj[i + 1]:
                    keys.add((ix.key_of(f), ix.key_of(toks[i + 1])))
        return keys

    # ---- the signal
    def analyse(self, text, where=None):
        p = self.policy
        raw = [m.group() for m in ix.TOKEN.finditer(text or '')]
        stream = ix.tokens_with_adjacency(text)
        toks = [t for t, _ in stream]
        adj = [a for _, a in stream]
        out = []
        for i, t in enumerate(toks):
            variants = [(f, c, b) for f, c, b in self.idx.variants(t) if f != t]
            if not variants:
                continue
            obs_count = self.idx.count(t)
            eff_pr, is_proper, why_proper = self._properness(raw, toks, i, obs_count)

            best, obs_support = self._best_context(toks, adj, i, t, variants)
            if best is None:
                f = self._unigram_only(i, t, obs_count, variants, eff_pr, is_proper, where)
                if f:
                    out.append(f)
                continue
            alt, side, ctx_label, obs_ctx, alt_ctx, alt_books = best

            sup, con = self._evidence(toks, adj, i, t, alt, side, obs_support)
            if obs_support >= p.veto_observed_support:
                # CONTRADICTING EVIDENCE WINS. The corpus itself writes this phrase; whatever the other
                # side of the token looks like, the observed text is not an anomaly.
                continue
            partner = i - 1 if side == 'left' else i + 1
            internal = self._informative_caps(raw, toks, partner)
            rule, ok, reason = self._decide(is_proper, obs_count, obs_ctx, alt_ctx, alt_books, internal)
            if is_proper and why_proper:
                reason = f'{reason} [{why_proper}{"; name-internal context" if internal else ""}]'
            if ok:
                out.append(Finding(i, t, alt, rule, ctx_label, obs_ctx, alt_ctx, alt_books, eff_pr,
                                   is_proper, sup, con, self._strength(obs_ctx, alt_ctx, alt_books,
                                                                       is_proper), reason))
            elif obs_ctx <= p.max_observed_ctx and obs_count <= p.anomaly_max_unigram:
                # the corpus has never written this word at all, and never in this context: an anomaly
                # worth flagging even though nothing may be proposed.
                out.append(Finding(i, t, None, 'xcorpus.anomaly-unattested-v1', ctx_label, obs_ctx,
                                   alt_ctx, alt_books, eff_pr, is_proper, sup, con, 0.6,
                                   reason or 'unattested form, no alternative well enough attested'))
        return out

    # ---- internals
    def _properness(self, raw, toks, i, obs_count):
        """(effective prior, is_proper, why).

        Two independent readings, because neither alone is enough. The **corpus prior** works inside an
        ALL-CAPS heading, where the surface says nothing (`đặng` 0.951 · `hán` 0.928 · `đấu` 0.015). The
        **surface** works for a name the corpus has no statistics for — and it is what catches Lane C's
        «(Theo Đăng Khoa, …)», where the token `đăng` has a low corpus prior (0.169) because it is also
        the common verb «đăng ký», yet *this* occurrence is unmistakably a person's name.
        """
        p = self.policy
        t = toks[i]
        pr = self.idx.proper_ratio(t)
        key_pr = self.idx.key_proper_ratio(t)
        eff_pr = pr if (pr is not None and obs_count >= 20) else key_pr
        if eff_pr is not None and eff_pr >= p.proper_threshold:
            return eff_pr, True, f'corpus prior {eff_pr}'
        if len(raw) != len(toks) or not raw[i][:1].isupper():
            return eff_pr, False, ''
        if all(w.upper() == w for w in raw):
            return eff_pr, False, ''                # ALL-CAPS: only the corpus prior can speak
        if i and raw[i - 1][:1].isupper():
            return eff_pr, True, 'capitalised beside a capitalised word'
        if i and raw[i][:1].isupper():
            return eff_pr, True, 'capitalised mid-text'
        if i + 1 < len(raw) and raw[i + 1][:1].isupper():
            return eff_pr, True, 'capitalised before a capitalised word'
        return eff_pr, False, ''

    @staticmethod
    def _informative_caps(raw, toks, j):
        """Is token `j` capitalised in a position where a capital *means* something?

        Not at index 0, not in an ALL-CAPS run, and not the first word after a sentence end — in all three
        the capital is forced by orthography and carries no information about proper-nounhood. This is the
        test that separates «Thái» in «Lý Thái Tô» (informative → the pair is part of the name, and
        name-internal evidence may be used) from «Theo» in «(Theo Đăng Khoa, …)» (block-initial → the
        pair says nothing about the name, and the signal must abstain).
        """
        if j <= 0 or j >= len(raw) or len(raw) != len(toks):
            return False
        if all(w.upper() == w for w in raw):
            return False
        return bool(raw[j][:1].isupper())

    def _best_context(self, toks, adj, i, t, variants):
        """→ (best alternative tuple, `obs_support`).

        `obs_support` is the strongest attestation of the **observed** token in any of its own contexts —
        the contradicting evidence. Both neighbours are tried for both, and only adjacency-clean pairs
        count."""
        if not self.scan:
            return None, 0
        best, obs_support = None, 0
        for side in ('left', 'right'):
            a, b = (i - 1, i) if side == 'left' else (i, i + 1)
            if a < 0 or b >= len(toks) or not adj[b]:
                continue
            obs = self.scan.count((toks[a], toks[b]))
            obs_support = max(obs_support, obs)
            for f, _, _ in variants:
                sur = (f, toks[b]) if side == 'right' else (toks[a], f)
                n = self.scan.count(sur)
                if n <= 0:
                    continue
                books = len({o['book'] for o in self.scan.occurrences(sur)})
                # `occurrences` is capped, so `books` is a floor — never an inflated independence claim
                if best is None or n > best[4]:
                    label = (f'{toks[a]} —' if side == 'left' else f'— {toks[b]}')
                    best = (f, side, label, obs, n, books)
        return best, obs_support

    def _decide(self, is_proper, obs_count, obs_ctx, alt_ctx, alt_books, name_internal=False):
        p = self.policy
        if is_proper:
            if obs_ctx > p.max_observed_ctx:
                return RULE_STRICT, False, (f'proper noun: the corpus attests the OBSERVED name in this '
                                            f'context {obs_ctx}×; a name may legitimately be rare')
            if name_internal:
                # evidence drawn from inside the name itself («Thái —»), which is the only kind that says
                # anything about a name. Still stricter than a common word, and still needs independent
                # confirmation before the engine will validate it.
                if alt_ctx >= p.pn_internal_min_alt_ctx and alt_books >= p.pn_internal_min_alt_books:
                    return RULE_STRICT, True, ('proper noun, name-internal context: the observed form is '
                                               f'unattested and «{alt_ctx}» attests the alternative')
                return RULE_STRICT, False, (f'proper noun with name-internal context below the bar '
                                            f'(alt {alt_ctx} in {alt_books} books)')
            if (alt_ctx >= p.pn_min_alt_ctx and alt_books >= min(p.pn_min_alt_books, 3)
                    and obs_count <= p.pn_max_observed_unigram):
                return RULE_STRICT, True, 'proper noun: unattested in context AND near-absent corpus-wide'
            return RULE_STRICT, False, ('proper noun, context word is not part of the name: evidence about '
                                        f'a name must come from the name (alt {alt_ctx}, '
                                        f'observed unigram {obs_count})')
        if obs_ctx <= p.max_observed_ctx and alt_ctx >= p.min_alt_ctx and alt_books >= p.min_alt_books:
            return RULE_STRICT, True, 'context unattested corpus-wide; alternative well attested'
        if (p.dominant_ratio and obs_ctx <= p.dominant_max_observed
                and alt_ctx >= max(p.min_alt_ctx, p.dominant_ratio * max(obs_ctx, 1))
                and alt_books >= p.min_alt_books):
            return RULE_DOMINANT, True, f'context {alt_ctx}:{obs_ctx} in favour of the alternative'
        return RULE_STRICT, False, f'insufficient context evidence ({alt_ctx} vs {obs_ctx})'

    def _unigram_only(self, i, t, obs_count, variants, eff_pr, is_proper, where):
        p = self.policy
        if obs_count > p.unigram_max_observed:
            return None
        dom, dc, db = variants[0]
        if is_proper or not p.unigram_fallback or dc < p.unigram_min_dominant:
            if obs_count <= p.anomaly_max_unigram:
                return Finding(i, t, None, 'xcorpus.anomaly-unattested-v1', '(no context)', 0, dc, db,
                               eff_pr, is_proper, (), (), 0.5,
                               'form unattested in 62,729 pages; no contextual evidence to propose from')
            return None
        return Finding(i, t, dom, 'xcorpus.unigram-unattested-v1', '(no context)', 0, dc, db, eff_pr,
                       is_proper, (), (), 0.55,
                       f'form unattested corpus-wide; single dominant variant «{dom}» ×{dc}')

    def _evidence(self, toks, adj, i, t, alt, side, obs_support):
        """Real occurrences, both ways. The contradicting half is collected from **both** contexts of the
        observed token, not only the side the proposal came from — that a detector *looked* for
        counter-evidence, and where, is itself part of the record."""
        sup, con = [], []
        if not self.scan:
            return (), ()
        a, b = (i - 1, i) if side == 'left' else (i, i + 1)
        alt_sur = (toks[a], alt) if side == 'left' else (alt, toks[b])
        for o in self.scan.occurrences(alt_sur)[:4]:
            sup.append(EvidenceRef(kind='corpus_occurrence', source=f"{o['book']}/{o['page']}",
                                   claim=f"the corpus writes «{' '.join(alt_sur)}» here",
                                   relation='supports', authority='corpus',
                                   detail=dict(snippet=o['snippet'])))
        for s2 in ('left', 'right'):
            c, d = (i - 1, i) if s2 == 'left' else (i, i + 1)
            if c < 0 or d >= len(toks) or not adj[d]:
                continue
            obs_sur = (toks[c], toks[d])
            for o in self.scan.occurrences(obs_sur)[:3]:
                con.append(EvidenceRef(
                    kind='corpus_occurrence', source=f"{o['book']}/{o['page']}",
                    claim=f"the corpus also writes the OBSERVED «{' '.join(obs_sur)}» here",
                    relation='contradicts', authority='corpus',
                    detail=dict(snippet=o['snippet'], observed_support=obs_support)))
        return tuple(sup), tuple(con)

    @staticmethod
    def _strength(obs_ctx, alt_ctx, alt_books, is_proper):
        """0..1 evidence weight. NOT a probability of correctness and no threshold on it is a trust gate."""
        import math
        base = min(1.0, math.log10(max(alt_ctx, 1) + 1) / 3.0)
        base *= min(1.0, 0.4 + 0.2 * min(alt_books, 3))
        if obs_ctx:
            base *= max(0.2, 1.0 - obs_ctx / 5.0)
        if is_proper:
            base *= 0.8            # a name's frequency evidence is worth less, by construction
        return round(base, 3)


# --------------------------------------------------------------------------- text application
def apply_findings(text, findings):
    """The proposed text — token substitution at the found positions, preserving the original casing and
    the original surrounding characters. Used ONLY to build a `RepairCandidate.proposed_value`; nothing in
    this package writes it anywhere."""
    if not findings:
        return text
    out, pos, ti = [], 0, 0
    repl = {f.i: f.proposed for f in findings if f.proposes}
    for m in ix.TOKEN.finditer(text):
        if ti in repl:
            out.append(text[pos:m.start()])
            out.append(_match_case(m.group(), repl[ti]))
            pos = m.end()
        ti += 1
    out.append(text[pos:])
    return ''.join(out)


def _match_case(original, proposed):
    if original.isupper():
        return proposed.upper()
    if original[:1].isupper():
        return proposed[:1].upper() + proposed[1:]
    return proposed


# --------------------------------------------------------------------------- plugins (A1's registry)
_STATE = dict(verifier=None)


def install(verifier):
    """Give the registered plugins the index/scan they need. Kept out of the registry so the plugins are
    pure functions of `(ctx)` exactly as A1's contract asks."""
    _STATE['verifier'] = verifier
    return verifier


@registry.signal(SIGNAL_ID)
def cross_corpus_signal(value, ctx):
    """`D.cross_corpus` as A1's registry sees it: a reading ABOUT a proposed value.

    `supports` when the corpus attests the proposed text in its context and does not attest the observed
    one; `objects` when the corpus attests the *observed* text (evidence against changing it); `abstains`
    when it has nothing to say — recorded, never treated as support."""
    v = _STATE['verifier']
    if v is None:
        return model.Signal(SIGNAL_ID, model.SignalVerdict.ABSTAINS, 0.0, dict(reason='no index installed'))
    observed = ctx.primary().value if ctx.primary() else ''
    if value == observed:
        # a *disposition* repair (Lane C's corroboration shape): the corpus corroborates the text as it is
        fs = v.analyse(observed, where=ctx.page)
        objecting = [f for f in fs if f.strength >= 0.5]
        if objecting:
            return model.Signal(SIGNAL_ID, model.SignalVerdict.OBJECTS,
                                max(f.strength for f in objecting),
                                dict(findings=[f.to_json() for f in objecting]))
        return model.Signal(SIGNAL_ID, model.SignalVerdict.SUPPORTS, 0.45,
                            dict(reason='no cross-corpus objection to the text as observed',
                                 tokens=len(ix.tokens_of(observed))))
    fs = v.analyse(observed, where=ctx.page)
    proposed_here = apply_findings(observed, fs)
    if proposed_here == value and fs:
        return model.Signal(SIGNAL_ID, model.SignalVerdict.SUPPORTS,
                            max(f.strength for f in fs), dict(findings=[f.to_json() for f in fs]))
    return model.Signal(SIGNAL_ID, model.SignalVerdict.ABSTAINS, 0.0,
                        dict(reason='the corpus does not attest this particular proposal'))


@registry.token_signal_provider('xcorpus.token-v1')
def token_signal(observed, proposed, ctx):
    """**The registration that matters most.** A1's repairer consults every registered token provider for
    every token it is about to change, and an `objects` reading from a provider **vetoes** the repair.

    This is where cross-corpus consistency does its highest-value work, and it is *not* the work of
    proposing: A1's Vietnamese repairer already runs at precision 1.000 / false-correction 0.000 with
    detection recall 0.040, so what it needs from A4 is not more proposals but an independent layer that
    can say «the corpus attests the alternative» (support, layer D, letting a candidate clear the
    independent-support bar) or «the corpus attests the text exactly as observed» (objection, killing a
    repair that would have been a false correction).

    Returns `None` when there is no index installed, so a run without A4's index behaves exactly as A1's
    own run did — an absent signal must never look like a supporting one.
    """
    v = _STATE['verifier']
    if v is None or not isinstance(observed, str) or not isinstance(proposed, str):
        return None
    o, pr = ix.norm_token(observed), ix.norm_token(proposed)
    if o == pr:
        return None
    text = ctx.primary().value if ctx.primary() else ''
    fs = {f.i: f for f in v.analyse(text, where=ctx.page)} if isinstance(text, str) else {}
    hit = next((f for f in fs.values() if f.observed == o), None)
    if hit is None:
        # the corpus was asked and had nothing to say about this token — recorded as an abstention, never
        # as support (A1's `SignalContribution` can only measure a layer if its silences are counted).
        return model.Signal(SIGNAL_ID, model.SignalVerdict.ABSTAINS, 0.0,
                            dict(reason='no cross-corpus finding at this token', observed=o, proposed=pr))
    if hit.proposes and hit.proposed == pr:
        return model.Signal(SIGNAL_ID, model.SignalVerdict.SUPPORTS, hit.strength,
                            dict(finding=hit.to_json(),
                                 supporting=[e.to_json() for e in hit.supporting],
                                 contradicting=[e.to_json() for e in hit.contradicting]))
    if hit.proposes and hit.proposed != pr:
        return model.Signal(SIGNAL_ID, model.SignalVerdict.OBJECTS, hit.strength,
                            dict(reason=f'the corpus attests «{hit.proposed}» here, not «{pr}»',
                                 finding=hit.to_json()))
    return model.Signal(SIGNAL_ID, model.SignalVerdict.ABSTAINS, 0.0,
                        dict(reason='cross-corpus detected an anomaly but proposes nothing',
                             finding=hit.to_json()))


@registry.block_signal_provider('xcorpus.block-v1')
def block_signal(observed_text, proposed_text, ctx):
    """Per-block reading: does the corpus attest the whole proposed text, and does it attest the observed
    text as it stands? An objection here is the «do not touch this block» vote."""
    v = _STATE['verifier']
    if v is None or not isinstance(observed_text, str):
        return None
    fs = v.analyse(observed_text, where=ctx.page)
    if not fs:
        return model.Signal(SIGNAL_ID, model.SignalVerdict.ABSTAINS, 0.0,
                            dict(reason='no cross-corpus finding anywhere in the block'))
    if isinstance(proposed_text, str) and apply_findings(observed_text, [f for f in fs if f.proposes]) == proposed_text:
        return model.Signal(SIGNAL_ID, model.SignalVerdict.SUPPORTS,
                            max(f.strength for f in fs if f.proposes) if any(f.proposes for f in fs) else 0.3,
                            dict(findings=[f.to_json() for f in fs]))
    return model.Signal(SIGNAL_ID, model.SignalVerdict.ABSTAINS, 0.0,
                        dict(reason='the corpus does not attest this particular block-level proposal',
                             findings=[f.to_json() for f in fs]))


@registry.repairer(FC_TONE, repairer_id='xcorpus.context-v1')
def propose(ctx):
    """DETECT + PROPOSE from cross-corpus context. Emits at most one candidate per block; a block whose
    findings are all anomalies emits nothing (the caller turns those into `SUSPECT` — a candidate is a
    proposal and an anomaly is not one)."""
    v = _STATE['verifier']
    if v is None or not ctx.primary():
        return
    text = ctx.primary().value
    if not isinstance(text, str):
        return
    fs = v.analyse(text, where=ctx.page)
    proposing = [f for f in fs if f.proposes]
    if not proposing:
        return
    proposed = apply_findings(text, proposing)
    if proposed == text:
        return
    sig = model.Signal(SIGNAL_ID, model.SignalVerdict.SUPPORTS,
                       max(f.strength for f in proposing),
                       dict(findings=[f.to_json() for f in proposing],
                            supporting=sum(len(f.supporting) for f in proposing),
                            contradicting=sum(len(f.contradicting) for f in proposing)))
    yield model.RepairCandidate(
        block_id=ctx.block_id, failure_class=FC_TONE, original_observations=ctx.observations,
        proposed_value=proposed, rule_id=proposing[0].rule, supporting_signals=(sig,),
        confidence=min(f.strength for f in proposing),
        provenance=dict(covers_reasons=('agree_tones', 'agree_text'), signal=SIGNAL_ID,
                        policy=v.policy.label(), corpus=v.idx.meta.get('pages'),
                        proper_noun=any(f.is_proper for f in proposing)),
        detected=dict(kind='cross-corpus context anomaly',
                      tokens=[f.to_json() for f in proposing],
                      anomalies_without_proposal=[f.to_json() for f in fs if not f.proposes]))


@registry.validator(FC_TONE, validator_id=VALIDATOR_ID)
def validate(candidate, ctx):
    """A validator that **refuses to validate its own layer**.

    This is the rule that saved Lane C from «Đăng Khoa» → «Đặng Khoa», and it is A1's
    `independent_support(exclude_layers=…)` contract used as written. A cross-corpus candidate needs
    corroboration from a layer that is not `D`; a candidate from another layer may be corroborated *by*
    `D`, which is the useful direction and the one this lane adds.
    """
    v = _STATE['verifier']
    if candidate.objections():
        return model.ValidationResult(VALIDATOR_ID, model.Verdict.REJECTED,
                                      detail=dict(reason='a signal objects to this candidate'),
                                      evidence=[dict(objection=s.to_json()) for s in candidate.objections()])
    layers = candidate.independent_support(exclude_layers=('D',))
    if not layers:
        return model.ValidationResult(
            VALIDATOR_ID, model.Verdict.INSUFFICIENT,
            detail=dict(reason='only cross-corpus support; a frequency signal may not validate itself',
                        note='Founder: frequency is a verification signal, not truth'))
    if v is not None and isinstance(candidate.proposed_value, str):
        sig = cross_corpus_signal(candidate.proposed_value, ctx)
        if sig.objects:
            return model.ValidationResult(VALIDATOR_ID, model.Verdict.REJECTED,
                                          detail=dict(reason='the corpus objects to the proposed text'))
        if sig.supports:
            return model.ValidationResult(
                VALIDATOR_ID, model.Verdict.VALIDATED,
                detail=dict(independent_layers=layers, cross_corpus=sig.to_json()),
                evidence=[dict(kind='cross_corpus', layers=layers)])
    return model.ValidationResult(VALIDATOR_ID, model.Verdict.INSUFFICIENT,
                                 detail=dict(reason='cross-corpus abstained on the proposed text'))


def anomalies_of(block_id, text, verifier, where=None, severity='unknown'):
    """The `AnomalySignal`s for a block — detection WITHOUT proposal, which A1's repairer contract has no
    slot for. These are what make a block `SUSPECT` rather than silently trusted."""
    out = []
    for f in verifier.analyse(text, where=where):
        if f.proposes:
            continue
        out.append(AnomalySignal(block_id=block_id, detector_id=f'{SIGNAL_ID}/{ix.INDEX_VERSION}',
                                 reason=f.reason, span=f.observed, observed=text,
                                 confidence=f.strength, severity=severity,
                                 context_supplied=dict(context=f.context, where=dict(where or {})),
                                 evidence=tuple(f.supporting) + tuple(f.contradicting)))
    return out
