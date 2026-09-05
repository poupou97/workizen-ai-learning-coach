#!/usr/bin/env python3
"""Round 5 · Lane A1's repairer: **Vietnamese diacritic / syllable errors**.

The class round 4 could not close: `agree_tones` withholds a block when the two stacks read a word's tones
differently (that block is *correct in one of the two readings* and is withheld anyway - false withholding),
and nothing at all fires when the two stacks make the **same** mistake («Tiền hành» for «Tiến hành»,
«Em cô thể» for «Em có thể», «phẫu» for «phễu») - false trust.

Two detectors, one repairer, and a deliberately asymmetric bar:

| detector | what it sees | what it is attacking | bar |
|---|---|---|---|
| `disagreement` | the stacks read one token differently | **false withholding** (a withheld block is already not served, so choosing wrong costs a wrong restore) | layer A decisive, plus one more layer |
| `agreed_error` | both stacks agree and the reading is still not Vietnamese here | **false trust** (the block is being served now) | much stricter: the observed collocation must be essentially unattested AND an alternative must dominate by `agree_ratio`, or the observed token must be *illegally* spelled |

A block is repaired **only if every issue in it is resolved**. One unresolved token keeps the whole block
withheld and puts it on the human queue (layer E). That is the fail-closed rule that makes the restore
numbers mean something.

Every threshold here is a **detection/arbitration threshold inside the repair framework**. None of them is a
production trust threshold, none of them relaxes a pipeline guard: a guard is answered with evidence or it
stands.
"""
from __future__ import annotations

import difflib
import re
import unicodedata
from dataclasses import dataclass

from .. import model, registry
from ..signals import consistency, layout, numeric, vi_lexicon
from ..vi import syllable

FAILURE_CLASS = 'vi_text_diacritic'
RULE_ARBITRATE = 'vi.diacritic-arbitrate-v1'
RULE_AGREED = 'vi.diacritic-agreed-error-v1'

TOKEN = re.compile(r'[0-9A-Za-zÀ-ỹĂăÂâĐđÊêÔôƠơƯư]+')
HAS_LETTER = re.compile(r'[A-Za-zÀ-ỹĂăÂâĐđÊêÔôƠơƯư]')
_ASCII = re.compile(r'^[A-Za-z]+$')
_SENT_END = re.compile(r'[.!?:;]\s*$')


def is_proper_noun(tokens, i):
    """A capitalised token that is not sentence-initial and not part of an all-caps run: «Đăng Khoa»,
    «Lý Thái Tổ», «Bạch Đằng».

    Lane C measured the failure this guards against: the corpus tone-majority signal proposed rewriting a
    person's name «Đăng Khoa» → «Đặng Khoa» - a confident wrong correction of exactly the kind the Founder
    named as the P0 failure mode. A name is not a dictionary word; the corpus's opinion about which spelling
    is commoner says nothing about which person this page is naming. Proper nouns therefore get their own,
    much stricter bar: **corpus frequency alone may never rewrite one**, and this sub-class's
    false-correction rate is reported separately.
    """
    tok = tokens[i][0]
    if not tok[:1].isupper() or tok.isupper():
        return False
    if i == 0:
        return False
    prev = tokens[i - 1][0]
    if prev.isupper() and len(prev) > 1:
        return False                      # inside an all-caps banner
    return True


@dataclass
class Config:
    """Calibrated on the 38 dev gold pages only; the 16 held-out pages never informed a number here."""
    min_uni_pages: int = vi_lexicon.MIN_UNI_PAGES
    min_uni_books: int = vi_lexicon.MIN_UNI_BOOKS
    ctx_min: int = vi_lexicon.CTX_MIN
    ctx_ratio: float = vi_lexicon.CTX_RATIO
    agree_ctx_min: int = 20            # an alternative must be this well attested before we touch a served block
    agree_ratio: float = 25.0          # …and dominate the observed reading by this much
    agree_obs_max: int = 2             # …while the observed collocation is essentially unattested
    max_issues_per_block: int = 6      # a block with more disagreements than this is a layout problem, not a spelling one
    enable_agreed_error: bool = True
    enable_quality_edits: bool = True


CONFIG = Config()
QUEUE = None            # a `signals.human.ReviewQueue`, installed by the driver
TRACE = None            # optional list; the driver appends per-token rows for contribution measurement


def configure(config=None, queue=None, trace=None):
    global CONFIG, QUEUE, TRACE
    if config is not None:
        CONFIG = config
    QUEUE = queue
    TRACE = trace
    return CONFIG


def nfc(s):
    return unicodedata.normalize('NFC', s or '')


def _place(tok):
    """Fold the two valid Vietnamese tone placements (hoá/hóa, thuỷ/thủy) so they are one candidate."""
    import tc_score
    return tc_score.norm_tone_placement(nfc(tok)).lower()


def tokenize(text):
    return [(m.group(0), m.start(), m.end()) for m in TOKEN.finditer(nfc(text or ''))]


def _skeleton(tok):
    return syllable.strip_quality(tok).lower()


def align(primary_tokens, verifier_tokens):
    """→ [(kind, p_index, v_index)] where kind is 'same' | 'diacritic' | 'quality'.

    Aligned on the ASCII skeleton, so «tiền»/«tiến» align (same skeleton, different diacritics) and
    «phẫu»/«phễu» align too (`replace` of equal length, one letter apart) - the base-vowel case round 4
    could not even see."""
    pk = [_skeleton(t) for t, _, _ in primary_tokens]
    vk = [_skeleton(t) for t, _, _ in verifier_tokens]
    out = []
    sm = difflib.SequenceMatcher(None, pk, vk, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            for k in range(i2 - i1):
                p, v = primary_tokens[i1 + k][0], verifier_tokens[j1 + k][0]
                out.append(('same' if _place(p) == _place(v) else 'diacritic', i1 + k, j1 + k))
        elif tag == 'replace' and (i2 - i1) == (j2 - j1):
            for k in range(i2 - i1):
                a, b = pk[i1 + k], vk[j1 + k]
                if len(a) == len(b) and sum(1 for x, y in zip(a, b) if x != y) == 1:
                    out.append(('quality', i1 + k, j1 + k))
    return out


def _dedupe(cands):
    seen, out = set(), []
    for c in cands:
        k = _place(c)
        if k in seen:
            continue
        seen.add(k); out.append(c)
    return out


def _candidate_set(observed, verifier_token, lex, book, cfg):
    """Everything the token might have been: the two readings, then attested tone/quality variants.

    A token with two tone marks is a special case: its candidate set is the **minimal de-toning** only, so a
    systematic OCR slip cannot be «repaired» into the tone-less form the same OCR produces elsewhere
    («thủỷ» → «thuy» rather than «thuỷ», measured on the dev split)."""
    doubled = syllable.detone_variants(observed)
    if doubled:
        return _dedupe([c for c in doubled if syllable.is_legal(c)] or [observed])
    base = [observed] + ([verifier_token] if verifier_token else [])
    gen = syllable.candidates(observed, include_quality=cfg.enable_quality_edits)
    if verifier_token:
        gen += syllable.candidates(verifier_token, include_quality=cfg.enable_quality_edits)
    attested = []
    for c in gen:
        if not syllable.is_legal(c):
            continue
        s = lex.unigram(c, exclude_book=book)
        if s.pages >= cfg.min_uni_pages and s.books >= cfg.min_uni_books:
            attested.append(c)
    return _dedupe([c for c in base if c] + attested)


def _neighbours(tokens, i, blocked=()):
    """The nearest word tokens left and right. A neighbour that is **itself an unresolved issue** is not a
    neighbour: on the dev split «đất cắn cổi» for «đất cằn cỗi» had each wrong token looking the other one
    up, so every collocation count was taken against corrupt context and both repairs went wrong. A corrupt
    neighbour is now treated as no evidence at all (that side is skipped), which makes the pair abstain and
    the block stay withheld - the correct fail-closed outcome."""
    blocked = set(blocked)
    left = next((tokens[k][0] for k in range(i - 1, -1, -1)
                 if HAS_LETTER.search(tokens[k][0]) and k not in blocked), None)
    right = next((tokens[k][0] for k in range(i + 1, len(tokens))
                  if HAS_LETTER.search(tokens[k][0]) and k not in blocked), None)
    if left is not None and any(k in blocked for k in range(max(0, i - 1), i)):
        left = None
    if right is not None and any(k in blocked for k in range(i + 1, min(len(tokens), i + 2))):
        right = None
    return left, right


def in_block_forms(tokens, suspect_indices):
    """{skeleton: Counter(form)} over the tokens of the block the two stacks AGREED on - the evidence
    `D.in_block` reads."""
    out = {}
    for i, (t, _s, _e) in enumerate(tokens):
        if i in suspect_indices or not HAS_LETTER.search(t) or len(t) < 2:
            continue
        out.setdefault(_skeleton(t), {}).setdefault(_place(t), []).append(t)
    return out


def resolve_token(observed, verifier_token, left, right, ctx, cfg, agreed, in_block=None,
                  proper_noun=False):
    """→ (winner | None, [Signal]). `agreed` selects the strict bar for a block that is being served;
    `proper_noun` selects the strictest bar of all."""
    lex, doc, book = ctx.lexicon, ctx.document, (ctx.page or {}).get('book')
    sigs = []
    obs_legal = vi_lexicon.syllable_signal(observed)
    # An observed reading the corpus has NEVER seen - «ỗi», 0 pages of 62,729 - is not evidence of anything.
    # It is treated exactly like an illegally spelled one: the strict «served block» bar does not apply,
    # because there is nothing to protect. ASCII-only tokens are exempt (foreign words are legitimately
    # absent from a Vietnamese corpus).
    obs_unattested = (lex is not None and not _ASCII.match(observed)
                      and not vi_lexicon.lexicon_signal(observed, lex, book).supports)
    cands = _candidate_set(observed, verifier_token, lex, book, cfg)
    # the same block's own agreed spelling of this word is always a candidate
    block_forms = (in_block or {}).get(_skeleton(observed), {})
    for forms in block_forms.values():
        cands = cands + [forms[0]]
    cands = _dedupe(cands)
    cands = [c for c in cands if syllable.is_legal(c) or c == observed]
    if obs_legal.objects:
        cands = [c for c in cands if c != observed]          # an illegally spelled reading is not a candidate
        if len(cands) == 1 and syllable.detone_variants(observed):
            # An illegal double-tone reading with exactly ONE legal minimal de-toning. Deterministic: the
            # only question left is whether that form is a Vietnamese word at all.
            only = cands[0]
            lx = vi_lexicon.lexicon_signal(only, lex, book)
            if not lx.supports:
                return None, []
            return only, [model.Signal('A.vi_syllable', model.SignalVerdict.SUPPORTS, 1.0,
                                       dict(observed=observed, proposed=only,
                                            reasons=list(obs_legal.detail.get('reasons', ())),
                                            note='the observed reading carries two tone marks; exactly one '
                                                 'legal minimal de-toning exists')),
                          lx,
                          layout.verifier_signal(only, verifier_token),
                          _page_signal(only, observed, ctx)]
    if len(cands) < 2:
        return None, [obs_legal] if obs_legal.objects else []

    # layer D, page scope: another block of the SAME page, one the pipeline trusts, prints this word.
    # It is also a candidate, so the corpus is able to object to it.
    pforms = (ctx.extra or {}).get('page_forms', {}).get(_skeleton(observed), {})
    pwinner, pcount, pobs_count = None, 0, len(pforms.get(_place(observed), ()))
    for key, forms in pforms.items():
        if key != _place(observed):
            pwinner, pcount = forms[0], len(forms)
    p_ok = bool(pwinner) and pobs_count == 0 and len(pforms) == 1
    for forms in pforms.values():
        cands = cands + [forms[0]]
    cands = _dedupe(cands)
    if obs_legal.objects:
        cands = [c for c in cands if _place(c) != _place(observed)]

    strict = agreed and not (obs_legal.objects or obs_unattested)
    ratio = cfg.agree_ratio if strict else cfg.ctx_ratio
    minimum = cfg.agree_ctx_min if strict else cfg.ctx_min
    winner, table, verdict = vi_lexicon.decide(cands, left, right, lex, book, ratio=ratio, minimum=minimum)
    dwinner, dtable, dverdict = (None, {}, {})
    if doc is not None:
        dwinner, dtable, dverdict = consistency.decide(cands, left, right, doc)

    # layer D, tightest scope: this very block already spells the word, in a spot both stacks agree on
    bwinner, bcount, bcompeting = None, 0, len(block_forms)
    if block_forms:
        for key, forms in block_forms.items():
            if key != _place(observed):
                bwinner, bcount = forms[0], len(forms)
    # layer B, deterministic: the block's role makes its text a closed set and exactly one candidate lands in it
    cwinner = None
    if ctx.role in layout.CLOSED_BY_ROLE:
        hits = [c for c in cands if layout.closed_vocabulary_signal(observed, c, ctx.role).supports]
        if len(hits) == 1:
            cwinner = hits[0]

    # a LOCAL signal (the block's own spelling, the page's own spelling, the role's closed vocabulary) may
    # break a tie the corpus and the document could not - but it may never overrule positive corpus evidence
    # FOR the observed reading. Found on the held-out split: «Đề xuất» was rewritten to «để xuất» because
    # the same page happened to print «để» elsewhere, while the corpus had «đề xuất» on 1,270 pages.
    local = (cwinner or (bwinner if bcount >= 2 and bcompeting == 1 else None) or (pwinner if p_ok else None))
    # a local winner is a *surface* form; map it onto the candidate the corpus actually scored, so the two
    # guards below are not vacuous ( «để» and «Để» are one candidate, and the corpus scored it under one key )
    by_place = {_place(c): c for c in cands}
    if local is not None:
        local = by_place.get(_place(local), local)
    if local is not None and (verdict.get(observed, {}).get('decisive')
                              or verdict.get(local, {}).get('objecting')
                              or dverdict.get(local, {}).get('objecting')
                              or max(list(verdict.get(observed, {}).get('left', 0) for _ in (0,))
                                     + [verdict.get(observed, {}).get('right', 0)]) > cfg.agree_obs_max):
        local = None
    pick = winner or dwinner or local
    if winner and dwinner and winner != dwinner:
        pick = None                                          # the corpus and the document disagree: abstain
    if proper_noun and pick is not None and _place(pick) != _place(observed):
        # A NAME. Corpus frequency is not evidence about a name, so it may not carry the repair on its own:
        # the document/page/block must print the proposed spelling itself, or the observed spelling must be
        # illegal Vietnamese. (Lane C: «Đăng Khoa» → «Đặng Khoa» is the case this refuses.)
        name_ok = bool((dwinner == pick and dverdict.get(pick, {}).get('decisive'))
                       or (p_ok and pwinner == pick)
                       or (bwinner == pick and bcount >= 2 and bcompeting == 1)
                       or obs_legal.objects)
        if not name_ok:
            return None, []
    if pick is None:
        return None, []
    if dverdict.get(pick, {}).get('objecting'):
        return None, []                                      # the book itself argues against the corpus
    if verdict.get(pick, {}).get('objecting'):
        return None, []                                      # the corpus argues against the document / the block

    if agreed:
        # A SERVED block. The bar is deliberately much higher than for arbitration, because here a mistake
        # replaces a correct word rather than choosing between two readings that are already on the table.
        obs_row = verdict.get(observed, {})
        obs_ctx = max(obs_row.get('left', 0), obs_row.get('right', 0))
        # The observed collocation must be essentially unattested in the corpus - OR the PAGE must print a
        # competing form in a block both stacks agreed on and never print the observed one. The second
        # clause exists because the corpus table is the same OCR: «chất răn» for «chất rắn» is attested on
        # enough pages to pass a frequency filter, and only the page itself says otherwise.
        if not (obs_legal.objects or obs_unattested) and obs_ctx > cfg.agree_obs_max and not p_ok:
            return None, []
        if pick == observed:
            return None, []
        # …and the document must agree, or the observed spelling must be illegal Vietnamese, or the block's
        # role must make its text a closed set. Corpus frequency ALONE never rewrites a served word: the
        # corpus table is the same OCR that produced the word.
        doc_ok = bool((dwinner == pick and dverdict.get(pick, {}).get('decisive'))
                      or (p_ok and pwinner == pick) or (bwinner == pick and bcount >= 2 and bcompeting == 1))
        closed = layout.closed_vocabulary_signal(observed, pick, ctx.role).supports
        if not (doc_ok or obs_legal.objects or obs_unattested or closed):
            return None, []

    sigs.append(vi_lexicon.syllable_signal(pick))
    sigs.append(vi_lexicon.lexicon_signal(pick, lex, book))
    sigs.append(vi_lexicon.collocation_signal(pick, verdict.get(pick), winner))
    if doc is not None:
        sigs.append(consistency.in_document_signal(pick, dverdict.get(pick), dwinner))
    sigs.append(consistency.in_block_signal(pick, observed, bcount if pick == bwinner else 0, bcompeting))
    sigs.append(consistency.in_page_signal(pick, observed, pcount if pick == pwinner else 0,
                                           pobs_count, len(pforms)))
    sigs.append(layout.closed_vocabulary_signal(observed, pick, ctx.role))
    sigs.append(layout.verifier_signal(pick, verifier_token))
    sigs.extend(registry.token_signals(observed, pick, ctx))      # Lane A4's providers, if any are registered
    if obs_legal.objects:
        sigs.append(model.Signal('A.vi_syllable', model.SignalVerdict.SUPPORTS, 1.0,
                                 dict(observed=observed, reasons=list(obs_legal.detail.get('reasons', ())),
                                      note='the observed reading is not a legal Vietnamese syllable')))
    elif obs_unattested:
        so = lex.unigram(observed, exclude_book=book)
        sigs.append(model.Signal('A.vi_lexicon', model.SignalVerdict.SUPPORTS, 0.9,
                                 dict(observed=observed, observed_pages=so.pages, observed_books=so.books,
                                      note='the observed reading is not attested anywhere in the corpus')))
    if TRACE is not None:
        TRACE.append(dict(block=ctx.block_id, observed=observed, verifier=verifier_token, winner=pick,
                          agreed=agreed, proper_noun=proper_noun, left=left, right=right,
                          corpus=verdict.get(pick), document=dverdict.get(pick),
                          corpus_observed=verdict.get(observed), document_observed=dverdict.get(observed)))
    return pick, sigs


def _page_signal(pick, observed, ctx):
    pforms = (ctx.extra or {}).get('page_forms', {}).get(_skeleton(observed), {})
    count = len(pforms.get(_place(pick), ()))
    return consistency.in_page_signal(pick, observed, count, len(pforms.get(_place(observed), ())), len(pforms))


def _rebuild(text, tokens, repairs):
    """Apply token replacements to the ORIGINAL text by span. The observation is untouched; this builds a
    new string for the candidate."""
    t = nfc(text)
    out, last = [], 0
    for i, new in sorted(repairs.items()):
        _, s, e = tokens[i]
        out.append(t[last:s]); out.append(new); last = e
    out.append(t[last:])
    return ''.join(out)


@registry.repairer(FAILURE_CLASS, repairer_id='vi.diacritic-v1')
def propose(ctx):
    cfg = CONFIG
    if ctx.lexicon is None:
        return
    primary = ctx.primary()
    if primary is None or not (primary.value or '').strip():
        return
    text = nfc(primary.value)
    verifier_obs = ctx.observation('current-xycut')
    vtext = nfc(verifier_obs.value) if verifier_obs else ''
    ptoks, vtoks = tokenize(text), tokenize(vtext)
    pairs = align(ptoks, vtoks) if vtoks else [('same', i, None) for i in range(len(ptoks))]

    trusted = ctx.disposition == model.Disposition.TRUSTED
    # ---- pass 0: which tokens are issues at all (so a neighbour that is itself suspect is not used as context)
    suspects = []
    for kind, i, j in pairs:
        tok = ptoks[i][0]
        if not HAS_LETTER.search(tok) or len(tok) < 2:
            continue
        agreed = (kind == 'same')
        if agreed and not cfg.enable_agreed_error:
            continue
        vtok = vtoks[j][0] if j is not None else None
        if agreed:
            l0, r0 = _neighbours(ptoks, i)
            if not _worth_checking(tok, l0, r0, ctx, cfg):
                continue
        suspects.append((i, tok, vtok, agreed, is_proper_noun(ptoks, i)))

    if not suspects:
        return

    # ---- passes 1..2: resolve, treating a still-unresolved suspect as NO context on that side. A token
    # resolved in pass 1 becomes usable context in pass 2, so a repaired word can help the word beside it.
    resolved, sigs_by_index = {}, {}
    tokens_now = [list(t) for t in ptoks]
    suspect_idx = {i for i, *_r in suspects}
    in_block = in_block_forms(ptoks, suspect_idx)
    for _ in range(2):
        progressed = False
        for i, tok, vtok, agreed, pn in suspects:
            if i in resolved:
                continue
            blocked = {k for k, *_r in suspects if k != i and k not in resolved}
            left, right = _neighbours(tokens_now, i, blocked)
            winner, ss = resolve_token(tok, vtok, left, right, ctx, cfg, agreed, in_block, proper_noun=pn)
            if winner is not None:
                resolved[i] = winner
                sigs_by_index[i] = ss
                tokens_now[i][0] = winner
                progressed = True
        if not progressed:
            break

    issues, repairs, sigs, unresolved = [], {}, [], []
    for i, tok, vtok, agreed, pn in suspects:
        winner = resolved.get(i)
        issues.append(dict(kind=('agreed_error' if agreed else 'disagreement'), token=tok, verifier=vtok,
                           index=i, resolved=(winner is not None), winner=winner,
                           sub_class=('proper_noun' if pn else
                                      ('invalid_syllable' if not syllable.is_legal(tok) else 'valid_syllable'))))
        if winner is None:
            unresolved.append(issues[-1])
            continue
        sigs.extend(sigs_by_index.get(i, ()))
        if _place(winner) != _place(tok):
            repairs[i] = winner
    if len(issues) > cfg.max_issues_per_block:
        _queue(ctx, 'unresolved', dict(reason='too many issues in one block', issues=issues[:8]))
        return
    if unresolved:
        _queue(ctx, QUEUE.classify(trusted, ctx.role, False) if QUEUE else 'unresolved',
               dict(issues=issues, text_head=text[:80]))
        return

    proposed = _rebuild(text, ptoks, repairs) if repairs else text
    num = numeric.numeric_signal(text, proposed)
    sigs.append(num)
    # A block is only restored if every word in it is vouched for - not merely the tokens that were flagged.
    sigs.append(vi_lexicon.sweep_signal(proposed, ctx.lexicon, (ctx.page or {}).get('book')))
    if repairs:
        sigs.append(layout.closed_vocabulary_signal(text, proposed, ctx.role))
    sigs.append(layout.ocr_confidence_signal((ctx.page or {}).get('ocr_conf')))
    sigs.extend(registry.block_signals(text, proposed, ctx))
    rule = RULE_AGREED if any(i['kind'] == 'agreed_error' for i in issues) else RULE_ARBITRATE
    covers = ('agree_tones',) if not repairs or rule == RULE_ARBITRATE else ()
    conf = min(0.99, 0.5 + 0.1 * sum(1 for s in sigs if s.supports))
    yield model.RepairCandidate(
        block_id=ctx.block_id, failure_class=FAILURE_CLASS,
        original_observations=ctx.observations, proposed_value=proposed, rule_id=rule,
        supporting_signals=tuple(sigs), confidence=conf,
        provenance=dict(covers_reasons=covers, changed=bool(repairs),
                        prior_disposition=ctx.disposition, role=ctx.role,
                        book=(ctx.page or {}).get('book'), page=(ctx.page or {}).get('page')),
        detected=dict(issues=tuple(dict(i) for i in issues), repairs={str(k): v for k, v in repairs.items()}))


def _worth_checking(tok, left, right, ctx, cfg):
    """The agreed-error pre-filter. Cheap, and deliberately narrow: an illegal spelling always qualifies;
    otherwise the token's own collocation must be essentially unattested in 62,729 pages."""
    if not syllable.is_legal(tok):
        return True
    lex, book = ctx.lexicon, (ctx.page or {}).get('book')
    if lex is None:
        return False
    l_s = lex.bigram(left, tok, exclude_book=book).pages if left else None
    r_s = lex.bigram(tok, right, exclude_book=book).pages if right else None
    seen = [x for x in (l_s, r_s) if x is not None]
    pforms = (ctx.extra or {}).get('page_forms', {}).get(_skeleton(tok), {})
    page_says_otherwise = (len(pforms) == 1 and _place(tok) not in pforms)
    if page_says_otherwise:
        return True
    if not _ASCII.match(tok) and not vi_lexicon.lexicon_signal(tok, lex, book).supports:
        return True             # the corpus has never seen this reading: always worth a second look
    if not seen:
        return False
    return max(seen) <= cfg.agree_obs_max


def _queue(ctx, kind, detail):
    if QUEUE is None:
        return
    QUEUE.add(ctx.block_id, kind if isinstance(kind, str) else 'unresolved', ctx.page or {}, ctx.role,
              detail, disposition=ctx.disposition)
