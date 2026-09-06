#!/usr/bin/env python3
"""Round 5 · Lane A4 — the three evaluation sets, and why there are three.

The 97-row audit is an **evaluation set, not a tuning set**, and «every improvement must be re-measured on
a holdout the lane did not look at». So this lane measures on three sets with three different kinds of
truth, and never reports one without the others:

| set | n | truth comes from | independence |
|---|---|---|---|
| **R · the five Founder POC cases** | 5 | the Founder's own defect list | regression only — 5 rows can prove a bug is fixed and can prove nothing else |
| **L · Lane C's Bài 8 verbatim ledger** | 51 blocks / 15 token slips | a **human reading the printed page** at 150 dpi | real ground truth, real OCR errors, but Lane C has published a summary of it: **semi-independent** |
| **H · the injection holdout** | 12 books this lane never opened | the uncorrupted original line | fully independent, and the only set that can measure **false correction rate on text that was already right** |

Set H is where the P0 metric lives. Detection recall can be measured on corrupted text; *false* correction
can only be measured honestly where nothing was corrupted, because there the correct answer is «propose
nothing» for every single token. A signal that flags 3 % of clean tokens would look excellent on R and L
and would be unusable.

**Index leakage matters and is handled.** The corpus index is built from the same OCR corpus these sets
are drawn from, so a book that verifies itself is not evidence. Every measurement here uses an index and a
context scan built with the evaluated books **excluded** (`held_out_books()`), and the runner reports both
index sizes so the exclusion is checkable.

**Injection model.** Corruptions are single-character diacritic edits drawn from the confusion classes the
real slips exhibit (tone-mark substitution on one vowel; vowel-quality substitution inside {a â ă},
{o ô ơ}, {e ê}, {u ư}, {i y}). The result is **not** checked against the corpus before being injected —
checking it would inject exactly what the detector looks for and turn recall into a tautology. Real OCR
produces both non-words («ỗi») and perfectly good words («hoa»), and so does this.
"""
from __future__ import annotations

import json
import os
import random
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # tool/corpus

import tc_score  # noqa: E402

from . import index as ix, paths  # noqa: E402

#: Lane C's file, owned by Lane C. This lane does NOT copy it into its own branch: it reads a snapshot
#: taken from `origin/lane-c/round5-history` into the gitignored input directory, so the evaluation is
#: reproducible without A4 committing another lane's data.
LANEC_LEDGER_SNAPSHOT = f'{paths.OUT}/inputs/lsdl5-bai8-verbatim-ledger.json'
LANEC_LEDGER = 'docs/research/lane-c/data/lsdl5-bai8-verbatim-ledger.json'
LANEC_SDM = (f'{paths.ROOT}/poc-out/round5/lane-c/tc2-lsdl5/v1/root/poc-out/trusted-corpus/tc-v2/'
             f'tc2-r5/sdm/05-sgk-lich-su-va-dia-li-5')
LANEC_BOOK = '05-sgk-lich-su-va-dia-li-5'
HOLDOUT_SEED = 20260906
HOLDOUT_BOOKS = 12


# --------------------------------------------------------------------------- R · the five POC cases
#: Founder's five, each in a sentence of the kind the book actually prints. The `correct` string is what
#: the print says; `observed` is what the OCR/parser produced. Cases C and E are the hard ones by design:
#: a *valid* Vietnamese syllable replacing another valid one, where no lexicon can decide.
POC_CASES = [
    dict(id='A', kind='stem_constant', subject='Khoa học tự nhiên', lesson='Ánh sáng',
         heading_path=['CHỦ ĐỀ 5. ÁNH SÁNG', 'Bài 40. Tốc độ ánh sáng'],
         correct='Ánh sáng truyền trong chân không với tốc độ c = 3×10⁸ m/s.',
         observed='Ánh sáng truyền trong chân không với tốc độ c = 3×10° m/s.',
         span_correct='3×10⁸', span_observed='3×10°',
         note='superscript destroyed by the parser; a physical constant becomes nonsense'),
    dict(id='B', kind='proper_noun_person', subject='Lịch sử và Địa lí', lesson='Thăng Long',
         heading_path=['CHỦ ĐỀ 3', 'Bài 9. Triều Lý và việc định đô ở Thăng Long'],
         correct='Năm 1010, Lý Thái Tổ dời đô từ Hoa Lư về Thăng Long.',
         observed='Năm 1010, Lý Thái Tô dời đô từ Hoa Lư về Thăng Long.',
         span_correct='Tổ', span_observed='Tô',
         note='proper noun; both «tổ» and «tô» are common valid words'),
    dict(id='C', kind='common_word_meaning', subject='Tiếng Việt', lesson='Bản sắc dân tộc',
         heading_path=['CHỦ ĐỀ 4', 'Bài 12. Giữ gìn bản sắc dân tộc'],
         correct='Giữ gìn bản sắc văn hoá của dân tộc là trách nhiệm của mỗi người.',
         observed='Giữ gìn bán sắc văn hoá của dân tộc là trách nhiệm của mỗi người.',
         span_correct='bản', span_observed='bán',
         note='HARD: «bán» is a valid word (to sell); the meaning inverts and no lexicon can decide'),
    dict(id='D', kind='proper_noun_state', subject='Lịch sử và Địa lí', lesson='Nhà nước',
         heading_path=['CHỦ ĐỀ 6', 'Bài 20. Nước Cộng hoà xã hội chủ nghĩa Việt Nam'],
         correct='Nước Cộng hoà xã hội chủ nghĩa Việt Nam là nhà nước của nhân dân.',
         observed='Nước Cộng hoa xã hội chủ nghĩa Việt Nam là nhà nước của nhân dân.',
         span_correct='hoà', span_observed='hoa',
         note='«hoa» is a very common word (flower); token frequency argues for the WRONG form'),
    dict(id='E', kind='common_word_nonword', subject='Tự nhiên và Xã hội', lesson='Cây cối',
         heading_path=['CHỦ ĐỀ 4. THỰC VẬT VÀ ĐỘNG VẬT', 'Bài 15. Cây xung quanh em'],
         correct='Trong vườn nhà em có cây ổi và cây xoài.',
         observed='Trong vườn nhà em có cây ỗi và cây xoài.',
         span_correct='ổi', span_observed='ỗi',
         note='HARD by the Founder\'s framing; in fact «ỗi» is unattested in all 62,729 pages'),
]


def poc_cases():
    return [dict(c) for c in POC_CASES]


# --------------------------------------------------------------------------- L · Lane C's Bài 8 ledger
def lanec_bai8(repo_root=None):
    """The 51 LS&ĐL 5 Bài 8 learning blocks with a human print verdict, joined to their pipeline text.

    → [{block_id, text, trust, reasons, verdict, slips[{pipeline, printed, context}], heading_path, …}].
    `verdict` is one of verbatim · verbatim_glyph · slip; a `slip` block is one the print disagrees with.
    """
    here = os.path.abspath(__file__)
    repo_root = repo_root or os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(here))))
    for cand in (LANEC_LEDGER_SNAPSHOT, os.path.join(repo_root, LANEC_LEDGER)):
        if os.path.exists(cand):
            break
    else:
        raise FileNotFoundError(f'Lane C verbatim ledger not found; snapshot it to {LANEC_LEDGER_SNAPSHOT} '
                                f'with: git show origin/lane-c/round5-history:{LANEC_LEDGER}')
    with open(cand, encoding='utf-8') as fh:
        led = json.load(fh)
    pages = {}
    for name in sorted(os.listdir(LANEC_SDM)):
        if name.endswith('.sdm.json'):
            with open(os.path.join(LANEC_SDM, name), encoding='utf-8') as fh:
                p = json.load(fh)
            for b in p.get('blocks') or ():
                short = ':'.join(b['id'].split(':')[1:])
                pages[short] = dict(block=b, page=p)
    out = []
    for row in led['blocks']:
        got = pages.get(row['block'])
        if not got:
            continue
        b, p = got['block'], got['page']
        out.append(dict(block_id=b['id'], short=row['block'], text=b.get('text') or '',
                        text_docling=b.get('text_docling'), trust=row['trust'],
                        reasons=row.get('reasons') or b.get('trust', {}).get('reasons') or [],
                        verdict=row['verdict'], slips=row.get('slips') or [], anchor=row.get('anchor'),
                        note=row.get('note'), role=(b.get('role') or {}).get('value'),
                        heading_path=b.get('heading_path') or [], book=LANEC_BOOK,
                        page=p.get('page'), printed_page=p.get('printed_page'),
                        guards=b.get('guards') or [], ocr_conf=b.get('ocr_conf'),
                        agreement=b.get('agreement') or {}))
    return out


# --------------------------------------------------------------------------- H · the injection holdout
#: The Vietnamese vowel families an OCR stack confuses. Derived from the real slips in Lane C's ledger
#: (ầ/ấ · ĩ/ì · ẩ/ầ · í/ị · ữ/ừ · â/á · ể/ề · ả/á · ã/á) plus the Founder's five, generalised to the
#: closed classes those edits belong to. No corpus lookup goes into this map — it is a model of the
#: *scanner*, not of the language.
TONES = ['', '̀', '́', '̃', '̉', '̣']       # none, grave, acute, tilde, hook, dot
QUALITY = [set('aâă'), set('oôơ'), set('eê'), set('uư'), set('iy'), set('dđ')]


def _vowel_edits(tok):
    """Every single-character diacritic edit of `tok` that yields a different string."""
    out = set()
    d = unicodedata.normalize('NFD', tok)
    chars = []
    i = 0
    while i < len(d):                                  # regroup base + combining marks
        base, i = d[i], i + 1
        marks = ''
        while i < len(d) and unicodedata.category(d[i]) == 'Mn':
            marks += d[i]
            i += 1
        chars.append((base, marks))
    for j, (base, marks) in enumerate(chars):
        tone = ''.join(m for m in marks if m in TONES)
        rest = ''.join(m for m in marks if m not in TONES)
        if base.lower() in 'aeiouy' or base.lower() in 'âăêôơư':
            for t in TONES:                            # tone substitution
                if t != tone:
                    cand = list(chars)
                    cand[j] = (base, rest + t)
                    out.add(_join(cand))
        # vowel-quality substitution: the family member REPLACES the base *and its quality marks*
        # (circumflex / breve / horn), keeping only the tone. Without that, `ổ` (o + ̂ + ̉) would gain a
        # second circumflex and produce a string no scanner ever emits.
        plain = unicodedata.normalize('NFD', base)[0].lower()
        for fam in QUALITY:
            if plain in fam:
                for alt in fam:
                    a_nfd = unicodedata.normalize('NFD', alt)
                    if a_nfd == unicodedata.normalize('NFD', base.lower()):
                        continue
                    a = alt.upper() if base.isupper() else alt
                    cand = list(chars)
                    cand[j] = (a, tone)
                    out.add(_join(cand))
    out.discard(tok)
    return sorted(x for x in out if _is_vietnamese(x))


_VN_OK = re.compile(r'^[0-9A-Za-zÀ-ỹĂăÂâĐđÊêÔôƠơƯư]+$')


def _is_vietnamese(s):
    """Reject a corruption no scanner would emit: a diacritic combination Vietnamese does not have (two
    quality marks on one vowel — NFC leaves a stray combining mark behind), or more than one tone mark in
    a syllable, which Vietnamese orthography does not permit. Keeping those in would make the injected
    corruptions *easier* to detect than the real ones and flatter every recall number below."""
    if not _VN_OK.match(s):
        return False
    nfc = unicodedata.normalize('NFC', s)
    if any(unicodedata.category(c) == 'Mn' for c in nfc):
        return False
    tones = sum(1 for c in unicodedata.normalize('NFD', s) if c in ''.join(TONES))
    return tones <= 1


def _join(chars):
    return unicodedata.normalize('NFC', ''.join(b + m for b, m in chars))


def held_out_books(ocr_root=None, n=HOLDOUT_BOOKS, seed=HOLDOUT_SEED, also_exclude=(LANEC_BOOK,)):
    """The books this lane's index must NOT contain, so that a measurement on them is a measurement.
    Deterministic given the seed, so the choice is reproducible and was not shopped for."""
    ocr_root = ocr_root or paths.OCR_BODY
    books = sorted(b for b in os.listdir(ocr_root) if os.path.isdir(os.path.join(ocr_root, b)))
    rng = random.Random(seed)
    pool = [b for b in books if b not in set(also_exclude)]
    return sorted(rng.sample(pool, n)), sorted(set(also_exclude))


def holdout_lines(books, ocr_root=None, per_book=40, min_tokens=6, seed=HOLDOUT_SEED):
    """Clean text lines from the held-out books, with enough context to be verifiable. These are the
    *uncorrupted* rows: the correct answer for every token is «propose nothing»."""
    ocr_root = ocr_root or paths.OCR_BODY
    rng = random.Random(seed + 1)
    rows = []
    for book in books:
        bdir = os.path.join(ocr_root, book)
        cand = []
        for name in sorted(os.listdir(bdir)):
            if not name.endswith('.json'):
                continue
            with open(os.path.join(bdir, name), encoding='utf-8') as fh:
                page = json.load(fh)
            for li, line in enumerate(page.get('lines') or ()):
                text = tc_score.nfc(line.get('text') or '')
                toks = ix.tokens_of(text)
                if len(toks) < min_tokens or not re.search(r'[À-ỹ]', text):
                    continue
                cand.append(dict(book=book, page=name[:-5], line=li, text=text, tokens=len(toks),
                                 conf=line.get('conf')))
        rng.shuffle(cand)
        rows.extend(cand[:per_book])
    for i, r in enumerate(rows):
        r['id'] = f"holdout:{r['book']}:{r['page']}:{r['line']:03d}"
    return rows


def inject(rows, seed=HOLDOUT_SEED, rate=1.0, min_len=2):
    """One single-character diacritic corruption per selected row. → rows with `corrupted`, `truth_i`,
    `truth_token`, `injected_token`."""
    rng = random.Random(seed + 2)
    out = []
    for r in rows:
        if rng.random() > rate:
            continue
        toks = list(ix.TOKEN.finditer(r['text']))
        pos = [k for k, m in enumerate(toks) if len(m.group()) >= min_len and _vowel_edits(m.group())]
        if not pos:
            continue
        k = rng.choice(pos)
        m = toks[k]
        edits = _vowel_edits(m.group())
        bad = rng.choice(edits)
        r2 = dict(r)
        r2['corrupted'] = r['text'][:m.start()] + bad + r['text'][m.end():]
        r2['truth_i'] = k
        r2['truth_token'] = ix.norm_token(m.group())
        r2['injected_token'] = ix.norm_token(bad)
        r2['id'] = r['id'] + '#inj'
        if r2['truth_token'] != r2['injected_token']:
            out.append(r2)
    return out
