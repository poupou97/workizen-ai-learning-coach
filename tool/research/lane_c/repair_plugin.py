#!/usr/bin/env python3
"""LANE C (round 5) — a plugin for Lane A1's DETECT → REPAIR → VALIDATE → RESTORE framework
(`tool/corpus/repair/`), registered from Lane C's own package exactly as the framework asks.
Nothing under `tool/corpus/` is edited.

It exists to answer two questions the Founder asked about LS&ĐL 5 Bài 8 with EVIDENCE:

  Q1  the block carrying all seven dated events is withheld for `agree_tones` — but the PRIMARY stack is
      right and the VERIFIER is wrong («Bạch Đằng» vs «Bạch Đăng»). Can it be restored WITHOUT loosening
      the guard?
  Q2  the block carrying «Âu Lạc (179 TCN)» is withheld for `agree_text` at similarity 70 — but the text is
      verbatim and the verifier simply merged two columns. Can that be told apart from a real disagreement?

Three repairers, each fail-closed, none of which may validate itself:

  `lanec.tone-corroboration-v1`  (layer D generator) — the guard fired because the two stacks disagree on a
      tone. If an INDEPENDENT signal corroborates the PRIMARY's form (the same context-scoped form is
      attested elsewhere in the book's trusted text; the human print read agrees), propose the primary
      value UNCHANGED. This is a repair of the DISPOSITION, not of the text: nothing is rewritten.
  `lanec.tone-majority-v1`  (layer D generator) — the primary's form is the minority for its context and a
      dominant majority exists ⇒ propose that majority. This is a real text change and needs an independent
      signal, because the same signal proposed «Đăng Khoa» → «Đặng Khoa», which is WRONG.
  `lanec.column-linearisation-v1`  (layer B generator) — `agree_text` fired, but every token of the primary
      appears, in order, inside the verifier's whole-page token stream. That is a reading-order artefact of
      the verifier, not a text disagreement ⇒ propose the primary value unchanged.

Validator `lanec.history-text-validator-v1`: one objection rejects; otherwise the candidate must have
support from a layer OTHER than its generator's (`independent_support(exclude_layers=…)`), else
`insufficient`. Insufficient is never a soft yes.

    python3 tool/research/lane_c/repair_plugin.py [--out DIR] [--copy-md PATH]

Import is soft: without `tool/corpus/repair/` (Lane A1's branch not merged) the module still imports and
`available()` is False, so tests skip instead of going green on nothing. Set `WAL_REPAIR_PATH` to point at
a checkout of the framework.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
MAIN = '/Users/alexnguyen/projects/workizen-ai-learning-coach'
BOOK = '05-sgk-lich-su-va-dia-li-5'
LESSON = 8
RUN = f'{MAIN}/poc-out/round5/lane-c/tc2-lsdl5/v1'
R5 = f'{RUN}/root/poc-out/trusted-corpus/tc-v2/tc2-r5'
XYCUT = (f'{MAIN}/poc-out/round4/lane-c/tc2-lsdl5/v1/root/poc-out/trusted-corpus/tc-v2/tc2-p1'
         f'/bakeoff/raw/current-xycut')
LEDGER = f'{REPO}/docs/research/lane-c/data/lsdl5-bai8-verbatim-ledger.json'

sys.path.insert(0, HERE)
import tone_repair_probe as tp  # noqa: E402

FC_TONE = 'vi_tone_disagreement'
FC_TEXT = 'text_agreement_linearisation'
VALIDATOR_ID = 'lanec.history-text-validator-v1'

_extra = os.environ.get('WAL_REPAIR_PATH')
for _p in ([_extra] if _extra else []) + [f'{REPO}/tool/corpus']:
    if _p and os.path.isdir(os.path.join(_p, 'repair')):
        sys.path.insert(0, _p)
        break
try:                                        # noqa: SIM105
    from repair import engine, ledger as ledger_mod, model, registry
except Exception:                           # pragma: no cover - framework not present
    engine = ledger_mod = model = registry = None


def available():
    return model is not None


def load(p):
    with open(p, encoding='utf-8') as fh:
        return json.load(fh)


def short(block_id):
    parts = (block_id or '').split(':')
    return ':'.join(parts[1:]) if len(parts) >= 4 else (block_id or '')


# ---------------------------------------------------------------- signals (pure, testable without the framework)
def corpus_signal(observed, proposed, evidence, key):
    """Layer D — is the proposed form the attested majority for this context in the book's trusted text?"""
    counts = evidence.get(key) or Counter()
    n_prop, n_obs = counts.get(proposed.lower(), 0), counts.get(observed.lower(), 0)
    total = sum(counts.values())
    if not total:
        return 'abstains', 0.0, dict(reason='context never seen in trusted text')
    if n_prop > n_obs:
        return 'supports', n_prop / (n_prop + n_obs + 1), dict(proposed=n_prop, observed=n_obs, key=list(key))
    if n_obs > n_prop:
        return 'objects', n_obs / (n_prop + n_obs + 1), dict(proposed=n_prop, observed=n_obs, key=list(key))
    return 'abstains', 0.0, dict(proposed=n_prop, observed=n_obs, key=list(key))


def _slip_matches_occurrence(slip, prev_token):
    """A ledger slip may name the LEFT CONTEXT of the occurrence it refers to («Bạch —» for «Đằng»), because
    one spelling can occur twice in a block with two different truths («Theo Đăng Khoa … sông Bạch Đằng»).
    No context recorded ⇒ the slip applies to every occurrence."""
    ctx = (slip.get('context') or '').replace('—', ' ').split()
    if not ctx:
        return True
    return any(tp.strip_tone(w) == tp.strip_tone(prev_token) for w in ctx)


def human_signal(block_id, text, cands, verbatim):
    """Layer E — the human read of the printed page, checked PER OCCURRENCE and for COMPLETENESS.

    `cands` are the span-scoped candidates the generator produced (empty ⇒ a no-op/disposition repair).
    The signal objects when (a) a proposal touches a token the print does not show as a slip AT THAT
    OCCURRENCE, (b) a proposal disagrees with what the print says, or (c) the repair leaves a slip the
    print DOES show uncovered — a half-repaired block is still not verbatim and must not be served.
    """
    entry = verbatim.get(short(block_id))
    if entry is None:
        return 'abstains', 0.0, dict(reason='print not read for this block')
    slips = entry.get('slips') or []
    if not cands:                                 # no-op repair: does the print say the primary is right?
        if entry['verdict'] in ('verbatim', 'verbatim_glyph'):
            return 'supports', 1.0, dict(verdict=entry['verdict'])
        return 'objects', 1.0, dict(verdict=entry['verdict'],
                                    slips=[f"{s['pipeline']}→{s['printed']}" for s in slips])
    sp = tp.spans(text)
    covered, confirmed = set(), []
    for c in cands:
        i = c['index']
        prev = sp[i - 1][2] if 0 < i < len(sp) else '^'
        match = next((k for k, s in enumerate(slips)
                      if s['pipeline'] == c['observed'] and _slip_matches_occurrence(s, prev)), None)
        if match is None:
            return 'objects', 1.0, dict(reason=f'the print shows no slip at this «{c["observed"]}» (after «{prev}»)',
                                        verdict=entry['verdict'])
        if slips[match]['printed'].lower() != c['proposed'].lower():
            return 'objects', 1.0, dict(reason=f'the print reads «{slips[match]["printed"]}», not «{c["proposed"]}»')
        covered.add(match)
        confirmed.append(f"{c['observed']}→{c['proposed']}")
    missing = [f"{s['pipeline']}→{s['printed']}" for k, s in enumerate(slips) if k not in covered]
    if missing:
        return 'objects', 1.0, dict(reason='the repair leaves the block non-verbatim', uncovered=missing,
                                    confirmed=confirmed)
    return 'supports', 1.0, dict(verdict=entry['verdict'], confirmed=confirmed)


def tokens_in_order(needle_tokens, haystack_tokens):
    """Layer B — is the primary's token sequence a SUBSEQUENCE of the verifier's whole-page stream?
    True ⇒ the verifier holds every word, in order, and the low similarity is a linearisation artefact
    (two columns merged) rather than a text disagreement."""
    it = iter(haystack_tokens)
    return all(any(h == n for h in it) for n in needle_tokens)


# ---------------------------------------------------------------- plugin registration
def register(evidence, verbatim, page_streams):
    """Register Lane C's repairers/validator against A1's registry. Returns the ids registered."""
    if not available():
        return []

    @registry.repairer(FC_TONE, repairer_id='lanec.tone-corroboration-v1', order=10)
    def corroborate(ctx):
        """The guard fired on a tone disagreement; propose the PRIMARY value unchanged when an independent
        signal corroborates it. Repairs the disposition, never the text."""
        if 'agree_tones' not in (ctx.withhold_reasons or ()):
            return
        primary = ctx.primary()
        disputes = (ctx.extra or {}).get('tone_disagreements') or []
        if primary is None or not disputes:
            return
        sigs = []
        for p_tok, v_tok in disputes:
            key = (tp.strip_tone(_prev_token(primary.value, p_tok)), tp.strip_tone(p_tok))
            verdict, strength, detail = corpus_signal(v_tok, p_tok, evidence, key)   # is the PRIMARY's form the majority?
            sigs.append(model.Signal('D.in_corpus_majority', verdict, strength,
                                     dict(detail, token=p_tok, verifier=v_tok)))
        v, s, d = human_signal(ctx.block_id, primary.value, [], verbatim)
        sigs.append(model.Signal('E.human_print_read', v, s, d))
        yield model.RepairCandidate(
            block_id=ctx.block_id, failure_class=FC_TONE, original_observations=ctx.observations,
            proposed_value=primary.value, rule_id='lanec.tone-corroboration-v1',
            supporting_signals=tuple(sigs), confidence=0.0,
            provenance=dict(covers_reasons=('agree_tones',), kind='disposition-only: the text is unchanged'),
            detected=dict(disputes=[list(x) for x in disputes],
                          note='the two stacks disagree on a tone; the primary is the candidate'))

    @registry.repairer(FC_TONE, repairer_id='lanec.tone-majority-v1', order=20)
    def majority(ctx):
        """The primary's form is the minority for its context ⇒ propose the dominant majority. A REAL text
        change: the same signal proposes «Đăng Khoa» → «Đặng Khoa», which is wrong, so it must not validate
        itself."""
        primary = ctx.primary()
        if primary is None or not isinstance(primary.value, str):
            return
        cands = tp.candidates(primary.value, evidence, 2, 'dominant-majority', 2)
        if not cands:
            return
        text = primary.value
        toks = tp.tokens(text)
        # index-scoped, never a global replace: «sông Bạch Đăng» and «Theo Đăng Khoa» are two occurrences
        # of one spelling and the signal proposes DIFFERENT forms for them
        proposed = tp.apply_candidates(text, cands)
        mapping = {c['observed']: c['proposed'] for c in cands}
        sigs = [model.Signal('D.in_corpus_majority', 'supports',
                             min(1.0, sum(c['support'] for c in cands) / (10.0 * len(cands))),
                             dict(candidates=[{k: c[k] for k in ('observed', 'proposed', 'support', 'observedSupport')}
                                              for c in cands], tokens=len(toks)))]
        v, s, d = human_signal(ctx.block_id, text, cands, verbatim)
        sigs.append(model.Signal('E.human_print_read', v, s, d))
        yield model.RepairCandidate(
            block_id=ctx.block_id, failure_class=FC_TONE, original_observations=ctx.observations,
            proposed_value=proposed, rule_id='lanec.tone-majority-v1', supporting_signals=tuple(sigs),
            confidence=0.0, provenance=dict(covers_reasons=('agree_tones',), kind='text change'),
            detected=dict(replacements=mapping))

    @registry.repairer(FC_TEXT, repairer_id='lanec.column-linearisation-v1', order=10)
    def linearisation(ctx):
        """`agree_text` fired, but the verifier's whole-page stream contains every token of the primary in
        order ⇒ the two stacks did not disagree, they linearised two columns differently."""
        if 'agree_text' not in (ctx.withhold_reasons or ()):
            return
        primary = ctx.primary()
        page = (ctx.page or {}).get('page')
        stream = page_streams.get(page)
        if primary is None or not stream:
            return
        need = [tp.strip_tone(t) for t in tp.tokens(primary.value)]
        have = [tp.strip_tone(t) for t in stream]
        if not need or not tokens_in_order(need, have):
            return
        sigs = [model.Signal('B.layout_linearisation', 'supports', 1.0,
                             dict(primaryTokens=len(need), verifierPageTokens=len(have),
                                  check='primary tokens are a subsequence of the verifier page stream'))]
        v, s, d = human_signal(ctx.block_id, primary.value, [], verbatim)
        sigs.append(model.Signal('E.human_print_read', v, s, d))
        yield model.RepairCandidate(
            block_id=ctx.block_id, failure_class=FC_TEXT, original_observations=ctx.observations,
            proposed_value=primary.value, rule_id='lanec.column-linearisation-v1',
            supporting_signals=tuple(sigs), confidence=0.0,
            provenance=dict(covers_reasons=('agree_text',), kind='disposition-only: the text is unchanged'),
            detected=dict(note='low text_sim caused by the verifier merging two columns'))

    def _validate(candidate, ctx):
        if candidate.objections():
            return model.ValidationResult(VALIDATOR_ID, model.Verdict.REJECTED,
                                          detail=dict(objections=[s.signal_id for s in candidate.objections()]))
        gen = 'B' if candidate.rule_id.endswith('column-linearisation-v1') else 'D'
        independent = candidate.independent_support(exclude_layers=(gen,))
        if not independent:
            return model.ValidationResult(VALIDATOR_ID, model.Verdict.INSUFFICIENT,
                                          detail=dict(generatorLayer=gen, independentLayers=[]))
        return model.ValidationResult(
            VALIDATOR_ID, model.Verdict.VALIDATED,
            evidence=[dict(kind='independent signal layer', value=lyr) for lyr in independent],
            detail=dict(generatorLayer=gen, independentLayers=independent))

    registry.validator(FC_TONE, validator_id=VALIDATOR_ID)(_validate)
    registry.validator(FC_TEXT, validator_id=VALIDATOR_ID)(_validate)
    return ['lanec.tone-corroboration-v1', 'lanec.tone-majority-v1', 'lanec.column-linearisation-v1', VALIDATOR_ID]


def _prev_token(text, token):
    toks = tp.tokens(text)
    for i, t in enumerate(toks):
        if t == token:
            return toks[i - 1] if i else '^'
    return '^'


# ---------------------------------------------------------------- run it on Bài 8
def page_stream(page):
    p = f'{XYCUT}/{BOOK}-p{page:03d}.json'
    if not os.path.exists(p):
        return []
    d = load(p)
    blocks = ((d.get('result') or {}).get('blocks')) or []
    out = []
    for b in blocks:
        out.extend(tp.tokens(b.get('text')))
    return out


def run():
    if not available():
        raise SystemExit('Lane A1 framework not on the path — set WAL_REPAIR_PATH or merge a1/round5-repair-framework')
    verbatim = {e['block']: e for e in load(LEDGER)['blocks']}
    evidence = tp.evidence('book')
    sdm_dir = f'{R5}/sdm/{BOOK}'
    pages = {}
    blocks = []
    for name in sorted(os.listdir(sdm_dir)):
        page = load(f'{sdm_dir}/{name}')
        if page['page'] not in (38, 39, 40, 41):
            continue
        pages[page['page']] = page_stream(page['page'])
        for b in page['blocks']:
            if not b.get('learning'):
                continue
            blocks.append((page, b))   # TRUSTED blocks too: A1's engine turns a detected-but-unvalidated
                                       # failure on a TRUSTED block into WITHHELD (accuracy first)
    register(evidence, verbatim, pages)
    eng = engine.RepairEngine(ledger_mod.Ledger(f'{RUN}/report/repair-ledger.jsonl',
                                                run=dict(lane='c', book=BOOK, lesson=LESSON)))
    rows = []
    for page, b in blocks:
        obs = [model.Observation(b['id'], 'docling-ocrmac', b['text'],
                                 dict(page=page['page'], bbox=b['bbox'], ocr_conf=b.get('ocr_conf')))]
        vraw = ' '.join(pages.get(page['page']) or [])
        if vraw:
            obs.append(model.Observation(b['id'], 'current-xycut', vraw,
                                         dict(page=page['page'], note='whole-page stream (the verifier keeps no block-aligned text)')))
        ctx = engine.RepairContext(
            block_id=b['id'], observations=tuple(obs),
            disposition=(model.Disposition.TRUSTED if b['trust']['status'] == 'TRUSTED'
                         else model.Disposition.WITHHELD),
            withhold_reasons=tuple(b['trust'].get('reasons') or []), role=b['role']['value'],
            page=dict(book=BOOK, page=page['page'], printed_page=page.get('printed_page')),
            extra=dict(tone_disagreements=[tuple(x) for x in ((b.get('agreement') or {}).get('tone_disagreements') or [])]))
        out = eng.run_block(ctx)
        entry = verbatim.get(short(b['id']))
        truth = (entry or {}).get('verdict')
        rows.append(dict(block=short(b['id']), role=b['role']['value'], wasTrusted=b['trust']['status'] == 'TRUSTED',
                         reasons=list(ctx.withhold_reasons), disposition=out.disposition,
                         restorable=out.restorable,
                         rules=[c.rule_id for c in out.candidates],
                         verdicts=[v.verdict for v in out.validations],
                         printVerdict=truth,
                         changesText=any(c.proposed_value != b['text'] for c in out.candidates)))
    # What the restored blocks give back to the two PROPOSED rules — measured, not asserted: the restored
    # blocks are fed to `prose-dated-events-v1` under the verbatim gate exactly as a real document would be.
    import history_rules as hr
    restored_doc = {'blocks': [
        dict(id=b['id'], type='paragraph', text=b['text'], trust='trustedStructuredLesson',
             sourceRef=dict(book=BOOK, pagePdf=page['page'], pagePrinted=page.get('printed_page'), bbox=b['bbox']))
        for page, b in blocks
        if any(r['block'] == short(b['id']) and r['restorable'] for r in rows)
    ]}
    led = hr.Verbatim([{'block': k, 'verdict': v['verdict'], 'slips': v.get('slips') or []}
                       for k, v in verbatim.items()], path=os.path.basename(LEDGER))
    ev_after, _, held_after = hr.derive_events(restored_doc, led)
    win = [r for r in rows if not r['wasTrusted']]
    tin = [r for r in rows if r['wasTrusted']]
    return dict(book=BOOK, lesson=LESSON, blocks=len(blocks), rows=rows,
                withheldIn=len(win), trustedIn=len(tin),
                restored=sum(1 for r in win if r['restorable']),
                restoredCorrectly=sum(1 for r in win if r['restorable'] and (r['changesText'] or r['printVerdict'] in ('verbatim', 'verbatim_glyph'))),
                stillWithheld=sum(1 for r in win if not r['restorable']),
                trustedRepaired=sum(1 for r in tin if r['restorable']),
                trustedDemoted=sum(1 for r in tin if r['disposition'] == 'WITHHELD'),
                eventsAfterRestore=[dict(title=e['title'], when=e['when'], block=short(e['sourceBlockId']),
                                         charSpan=e['charSpan'], verbatimStatus=e['verbatimStatus']) for e in ev_after],
                eventsHeldAfterRestore=len(held_after))


def render(rep):
    L = ['# Lane C on Lane A1\'s repair framework — LS&ĐL 5 Bài 8 (round 5)', '',
         f"All {rep['blocks']} learning blocks of the lesson went through the engine: "
         f"{rep['withheldIn']} withheld, {rep['trustedIn']} already trusted.", '',
         f"**Withheld in:** restorable after DETECT → REPAIR → VALIDATE = **{rep['restored']}** "
         f"(the print confirms every one of them: **{rep['restoredCorrectly']}**); still withheld "
         f"**{rep['stillWithheld']}**.", '',
         f"**Trusted in:** **{rep['trustedDemoted']}** demoted to WITHHELD by the engine's accuracy-first rule "
         f"(a failure detected on a trusted block that nothing validated), **{rep['trustedRepaired']}** "
         f"repaired and revalidated.", '',
         f"**What the restored blocks give back to `prose-dated-events-v1` (verbatim gate ON): "
         f"{len(rep['eventsAfterRestore'])} events** — "
         + (', '.join(f"{e['title']} ({e['when']})" for e in rep['eventsAfterRestore']) or 'none') + '.', '',
         '| block | role | came in as | withheld for | candidates | validator verdicts | disposition | restorable | changes the text? | the print says |',
         '|---|---|---|---|---|---|---|---|---|---|']
    for r in rep['rows']:
        L.append(f"| {r['block']} | {r['role']} | {'TRUSTED' if r['wasTrusted'] else 'WITHHELD'} | "
                 f"{', '.join(r['reasons']) or '—'} | {', '.join(r['rules']) or '—'} | "
                 f"{', '.join(r['verdicts']) or '—'} | {r['disposition']} | {r['restorable']} | "
                 f"{'yes' if r['changesText'] else 'no'} | {r['printVerdict'] or '—'} |")
    return '\n'.join(L) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=f'{RUN}/report')
    ap.add_argument('--copy-md', default=None)
    a = ap.parse_args()
    rep = run()
    os.makedirs(a.out, exist_ok=True)
    with open(f'{a.out}/repair-plugin.json', 'w', encoding='utf-8') as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=2)
    md = render(rep)
    with open(f'{a.out}/repair-plugin.md', 'w', encoding='utf-8') as fh:
        fh.write(md)
    if a.copy_md:
        with open(a.copy_md, 'w', encoding='utf-8') as fh:
            fh.write(md)
    print(f'{a.out}/repair-plugin.md')
    print(f"  blocks {rep['blocks']} ({rep['withheldIn']} withheld in, {rep['trustedIn']} trusted in)")
    print(f"  restorable {rep['restored']} (print-confirmed {rep['restoredCorrectly']}) · still withheld {rep['stillWithheld']}")
    print(f"  trusted demoted {rep['trustedDemoted']} · trusted repaired {rep['trustedRepaired']}")


if __name__ == '__main__':
    main()
