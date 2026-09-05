#!/usr/bin/env python3
"""LANE C (round 4, §7) — PROPOSED History rules over a bridged LessonDocument (deterministic, block-grounded).

Nothing here touches tool/corpus. The input is the LessonDocument JSON the bridge writes
(`tsl_to_lesson_document.py`); the output is the same document with a typed `TimelineSemantic`, a
prototype History tutor script and a `provenance.historyRules` record — every event, attribution and
prompt names the block (id · page · bbox · character span) it came from. Withheld blocks have no text
and therefore never yield an event or an attribution (fail closed).

Rules (all PROPOSED — see docs/research/lane-c/05-GOLDEN-SLICE-2-GATE.md §4):
  prose-dated-events-v1   «Name (year[ – year][ TCN])» in a trusted paragraph → TimelineEvent
                          {when = the parenthesised text verbatim, title = the capitalised run before it,
                          text = the enclosing clause verbatim, sourceBlockId, yearStart/yearEnd/era, charSpan}.
                          Narrative years («năm 544») are counted but NOT promoted to events.
  story-attribution-v1    a trusted text block «(Theo …)» (or «(…, NXB …, YYYY)») closes a story: the
                          story = the preceding paragraph blocks back to the nearest heading (cross-page);
                          withheld regions inside it are listed, never filled; NXB + year parsed, authors/title
                          NOT split (italics are lost in text — fail closed on that split).
  figure-dependent-question-v1   a question whose text says «quan sát … hình» is never a tutor prompt.
  lesson-title-v1         header-confirmed-by-TOC lesson ⇒ title from the printed TOC (trailing dots
                          stripped) when the header title is a strict suffix of it; else the header title.
  history-tutor-v1        typed TutorScript (prototype): who/when · before/after · cause/effect · source
                          awareness · the verbatim «hoàn thiện trục thời gian» ask — prompts grounded in
                          blocks; acceptable patterns derived from the extracted events; ≤ 2 hints, no hint
                          matches an acceptable pattern (answer-leak guard, self-checked).

Round 5 (§11) — v2 adds THE VERBATIM GATE. Round 4 falsified A26 («two OCR stacks agreeing means the
text is verbatim»), so a TRUSTED flag is no longer sufficient to quote a block back at a child: with
`--verbatim-ledger` every event and every attribution must come from a block an INDEPENDENT read of the
printed page verified, else it is withheld with its reason and the slips the print shows. Without the
flag the rules run v1 and reproduce the round-4 numbers exactly.

    python3 tool/research/lane_c/history_rules.py --doc <lesson-document.json> --out <dir> \
        [--toc-title "…"] [--verbatim-ledger docs/research/lane-c/data/…-verbatim-ledger.json] [--report]
"""
import argparse
import json
import os
import re
import sys

RULE_EVENTS = 'prose-dated-events-v1'
RULE_ATTR = 'story-attribution-v1'
RULE_FIGQ = 'figure-dependent-question-v1'
RULE_TITLE = 'lesson-title-v1'
RULE_TUTOR = 'history-tutor-v1'
VERSION_V1 = 'history-rules@v1'
VERSION_V2 = 'history-rules@v2'
VERSION = VERSION_V2

# ---------------------------------------------------------------- round 5: the verbatim gate
# Round 4 falsified A26: two OCR stacks agreeing (`text_sim` = 100) does NOT mean the text is verbatim
# to the print. So from v2 a rule may not emit an event or an attribution merely because its source block
# is TRUSTED — the block must also be VERBATIM-VERIFIED by a signal independent of the two stacks.
# Today that signal is a human read of the printed page recorded in a verbatim ledger
# (`docs/research/lane-c/data/lsdl5-bai8-verbatim-ledger.json`). No ledger entry ⇒ `unverified` ⇒ fail closed.
VERBATIM_OK = 'verifiedAgainstPrint'
VERBATIM_DIFFERS = 'printDiffers'
VERBATIM_UNKNOWN = 'unverified'
VERBATIM_VERDICTS = {'verbatim': VERBATIM_OK, 'verbatim_glyph': VERBATIM_OK,
                     'slip': VERBATIM_DIFFERS, 'unread': VERBATIM_UNKNOWN}

YEARS = re.compile(r'\(\s*(\d{1,4})(\s*TCN)?\s*(?:[-–—]\s*(\d{1,4}))?\s*\)')
NARRATIVE_YEAR = re.compile(r'\b[Nn]ăm\s+(\d{3,4})\b')
ATTR_THEO = re.compile(r'^\(\s*Theo\s+.+\)\s*$', re.S)
ATTR_QUOTE = re.compile(r'^\(.+?,\s*NXB\s[^)]+?,\s*\d{4}\s*\)\s*$', re.S)
PUBLISHER = re.compile(r'NXB\s+[^,)]+')
YEAR_END = re.compile(r'(\d{4})\s*\)\s*$')
FIG_Q = re.compile(r'quan sát\s+(?:các\s+)?hình', re.I)
TEXT_TYPES = ('paragraph', 'heading', 'caption', 'question', 'activity')


WORD = re.compile(r'[^\W\d_]+')


def is_cap(tok):
    """A capitalised WORD (letters only): «Trưng» yes; «TCN).» / «43),» / «của» no — punctuation ends
    the actor run, so the previous clause never bleeds into the next actor."""
    t = tok.strip('«»"\'')
    return bool(t) and WORD.fullmatch(t) is not None and t[0].isupper()


def actor_before(text, end):
    """Maximal run of capitalised tokens (joined by spaces or a dash) ending right before `end`."""
    head = text[:end].rstrip()
    toks = head.split(' ')
    run = []
    i = len(toks) - 1
    while i >= 0:
        t = toks[i]
        if t in ('-', '–', '—') and run and i > 0 and is_cap(toks[i - 1]):
            run.insert(0, t); i -= 1; continue
        if is_cap(t):
            run.insert(0, t); i -= 1; continue
        break
    if not run:
        return None, None
    actor = ' '.join(run)
    start = len(head) - len(actor)
    return actor, start


def clause_bounds(text, start, end):
    """Enclosing clause: from the previous sentence end / clause comma (after the previous ')') to the ')'."""
    left = 0
    for m in re.finditer(r'[.;]\s+|\)\s*,\s*', text[:start]):
        left = m.end()
    return left, end


class Verbatim:
    """Verdicts of an independent read of the PRINTED page, keyed by block id. `None` ⇒ no ledger given
    ⇒ v1 behaviour (the rules trust the pipeline's TRUSTED flag alone, which round 4 falsified)."""

    def __init__(self, entries=None, path=None):
        self.path = path
        self.by_block = {}
        for e in entries or []:
            self.by_block[_short(e['block'])] = e

    @classmethod
    def load(cls, path):
        if not path:
            return cls(None)
        with open(path, encoding='utf-8') as fh:
            data = json.load(fh)
        return cls(data.get('blocks') or [], path=path)

    @property
    def enabled(self):
        return bool(self.by_block)

    def status(self, block_id):
        if not self.enabled:
            return VERBATIM_UNKNOWN
        e = self.by_block.get(_short(block_id))
        return VERBATIM_VERDICTS.get((e or {}).get('verdict'), VERBATIM_UNKNOWN)

    def slips(self, block_id):
        return ((self.by_block.get(_short(block_id)) or {}).get('slips')) or []

    def ok(self, block_id):
        return self.status(block_id) == VERBATIM_OK


def _short(block_id):
    """`05-…-5:p039:tc2-p1:000` → `p039:tc2-p1:000`; already-short ids pass through."""
    parts = (block_id or '').split(':')
    return ':'.join(parts[1:]) if len(parts) >= 4 else (block_id or '')


def _slips(slips):
    """«pipeline→printed» pairs for a report cell — single tokens only (D4)."""
    return '; '.join(f"{s.get('pipeline')}→{s.get('printed')}" for s in (slips or [])) or '—'


def derive_events(doc, verbatim=None, gate=True):
    verbatim = verbatim or Verbatim(None)
    events, mentions, held = [], [], []
    blocks = [b for b in doc['blocks'] if b['type'] == 'paragraph' and b.get('text')]
    for b in blocks:
        text = b['text']
        vstatus = verbatim.status(b['id'])
        for m in YEARS.finditer(text):
            actor, a_start = actor_before(text, m.start())
            if not actor:
                continue
            y0, era, y1 = int(m.group(1)), (m.group(2) or '').strip(), m.group(3)
            c0, c1 = clause_bounds(text, a_start, m.end())
            ev = dict(when=text[m.start() + 1:m.end() - 1].strip(), title=actor, text=text[c0:c1].strip(), sourceBlockId=b['id'],
                      yearStart=y0, yearEnd=int(y1) if y1 else y0, era=('TCN' if era else 'CN'), charSpan=[a_start, m.end()],
                      pagePdf=b['sourceRef']['pagePdf'], pagePrinted=b['sourceRef'].get('pagePrinted'), bbox=b['sourceRef']['bbox'],
                      trust=b['trust'], verbatimStatus=vstatus)
            if gate and verbatim.enabled and vstatus != VERBATIM_OK:
                held.append(dict(ev, withheldReason=f'source-not-verbatim-verified:{vstatus}', slips=verbatim.slips(b['id'])))
                continue
            events.append(ev)
        for m in NARRATIVE_YEAR.finditer(text):
            mentions.append(dict(year=int(m.group(1)), sourceBlockId=b['id'], charSpan=[m.start(), m.end()], reason='narrative-year-not-enumerated'))
    return events, mentions, held


def derive_attributions(doc, verbatim=None, gate=True):
    verbatim = verbatim or Verbatim(None)
    out, held = [], []
    blocks = doc['blocks']
    for i, b in enumerate(blocks):
        if b['type'] not in ('paragraph', 'caption') or not b.get('text'):
            continue
        t = b['text'].strip()
        form = 'theo' if ATTR_THEO.match(t) else ('quote' if ATTR_QUOTE.match(t) else None)
        if not form:
            continue
        story, withheld, title = [], [], None
        j = i - 1
        while j >= 0:
            p = blocks[j]
            if p['type'] == 'heading':
                title = p; break
            if p['type'] in ('activity', 'question', 'caption', 'sourceRef'):
                break
            if p['type'] == 'paragraph':
                story.insert(0, p)
            elif p['type'] == 'withheld':
                withheld.insert(0, p)
            j -= 1
        pub = PUBLISHER.search(t)
        yr = YEAR_END.search(t)
        vstatus = verbatim.status(b['id'])
        # the story is only «kể theo nguồn» if the title block is verbatim too — a slipped title
        # («LÝ BĨ …») would be quoted back at the child as if the book wrote it
        title_status = verbatim.status(title['id']) if title else VERBATIM_UNKNOWN
        span = [0, len(t)]
        rec = dict(attributionBlockId=b['id'], form=form, text=t, publisher=pub.group(0).strip() if pub else None, year=int(yr.group(1)) if yr else None,
                   titleBlockId=title['id'] if title else None, title=title['text'] if title else None, storyBlockIds=[p['id'] for p in story],
                   withheldPartIds=[w['id'] for w in withheld], withheldReasons=[w.get('reasons') for w in withheld], complete=not withheld and bool(title),
                   pagePdf=b['sourceRef']['pagePdf'], pagePrinted=b['sourceRef'].get('pagePrinted'), bbox=b['sourceRef']['bbox'], trust=b['trust'],
                   conclusionBlockId=story[-1]['id'] if story else None, charSpan=span,
                   verbatimStatus=vstatus, titleVerbatimStatus=title_status)
        if gate and verbatim.enabled and vstatus != VERBATIM_OK:
            held.append(dict(rec, withheldReason=f'source-not-verbatim-verified:{vstatus}', slips=verbatim.slips(b['id'])))
            continue
        if gate and verbatim.enabled and title is not None and title_status != VERBATIM_OK:
            rec['titleVerbatimWithheld'] = True
            rec['title'] = None            # the attribution stands; the story TITLE is not quoted
            rec['complete'] = False
        out.append(rec)
    return out, held


def figure_dependent_questions(doc):
    return [b['id'] for b in doc['blocks'] if b['type'] == 'question' and FIG_Q.search(b.get('text') or '')]


def section_heading_before(doc, block_id):
    last = None
    for b in doc['blocks']:
        if b['id'] == block_id:
            return last
        if b['type'] == 'heading' and re.match(r'^\d+\.\s', b.get('text') or ''):
            last = b
    return last


def lesson_title(doc, toc_title):
    prov = doc.get('provenance') or {}
    src = (prov.get('boundary') or {}).get('source')
    pipeline_title = doc.get('title') or ''
    if toc_title and src == 'both':
        clean = re.sub(r'[\s.…]+$', '', toc_title).strip()
        # diacritics-insensitive suffix test: display-font tone slips («KĨ» for «kì») are the documented OCR failure
        if not pipeline_title or _norm(clean).endswith(_norm(pipeline_title)):
            return clean, dict(rule=RULE_TITLE, source='toc', match='diacritics-insensitive-suffix', pipelineTitle=pipeline_title, tocTitle=toc_title)
        return pipeline_title, dict(rule=RULE_TITLE, source='header', pipelineTitle=pipeline_title, tocTitle=toc_title, note='header title is not a suffix of the TOC title — kept the header (fail closed)')
    return pipeline_title, dict(rule=RULE_TITLE, source='header', pipelineTitle=pipeline_title, tocTitle=toc_title)


# ---------------------------------------------------------------- tutor script (prototype, History-specific)
def _page(doc, bid):
    b = next((x for x in doc['blocks'] if x['id'] == bid), None)
    p = (b or {}).get('sourceRef', {}).get('pagePrinted') if b else None
    return f'SGK trang {p}' if p else 'SGK'


RX_SYNTAX = set('\\^$.|?*+()[]{}/')


def _rx(s):
    """Pattern for a verbatim string that is valid in BOTH Python `re` and Dart `RegExp(unicode: true)`:
    only regex syntax characters are escaped (`re.escape` would emit `\\-` / `\\ `, which JS unicode mode
    rejects); a dash accepts hyphen or en dash; whitespace is elastic. Matched case-insensitively."""
    out = []
    for ch in s.lower():
        if ch in RX_SYNTAX:
            out.append('\\' + ch)
        elif ch in '-–—':
            out.append('[-–—]')
        elif ch.isspace():
            out.append(r'\s*')
        else:
            out.append(ch)
    return ''.join(out)


def _norm(s):
    import unicodedata
    s = unicodedata.normalize('NFD', (s or '').replace('đ', 'd').replace('Đ', 'D'))
    return re.sub(r'\s+', ' ', ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower()).strip()


def tutor_script(doc, events, attributions, fig_q, timeline_ask_id):
    """Typed steps grounded in blocks. Returns None when the lesson lacks ≥ 3 dated events (no script is invented)."""
    if len(events) < 3:
        return None
    first, second, third = events[0], events[1], events[2]
    steps = []
    sec = section_heading_before(doc, first['sourceBlockId'])
    steps.append(dict(type='explain', id='e1', mascot='sam-explain', sourceBlockId=first['sourceBlockId'],
                      text='Bài này kể về những cuộc đấu tranh giành độc lập trong thời kì Bắc thuộc. Sách liệt kê từng cuộc kèm năm diễn ra trong ngoặc — '
                           'con đọc đoạn sách bên dưới rồi mình thử ba câu nhé.'))
    # who / when — the first enumerated event
    w = first['when']
    steps.append(dict(type='ask', id='q1', prompt=f'Theo sách, {first["title"]} gắn với những năm nào?', promptBlockId=first['sourceBlockId'],
                      options=[first['when'], second['when'], third['when']],
                      acceptable=[r'^' + _rx(w) + r'$', r'\b' + str(first['yearStart']) + r'\b'],
                      hints=[f'Con tìm tên «{first["title"]}» trong đoạn sách — năm nằm ngay trong ngoặc sau tên.',
                             f'Đoạn đó ở {_page(doc, first["sourceBlockId"])}, ngay dòng có tên {first["title"]}.'],
                      feedbackMatched=f'Khớp với sách: {first["title"]} ({first["when"]}). Con đã đọc đúng năm trong ngoặc.',
                      scaffold=f'Sách viết «{first["title"]} ({first["when"]})» — mình cùng đọc lại dòng đó rồi đi tiếp nhé.',
                      keySource=f'{RULE_EVENTS} — block {first["sourceBlockId"]} ({_page(doc, first["sourceBlockId"])}); KHÔNG phải SGV'))
    # before / after — two events, answer from the parsed years (no year in the prompt)
    a, b = second, third
    before = a if a['yearStart'] <= b['yearStart'] else b
    steps.append(dict(type='ask', id='q2', prompt=f'Theo sách, {a["title"]} và {b["title"]} — cuộc nào diễn ra trước?', promptBlockId=a['sourceBlockId'],
                      options=[a['title'], b['title']], acceptable=[r'^' + _rx(before['title']) + r'$', _rx(before['title'])],
                      hints=['So hai năm trong ngoặc sau mỗi tên trong đoạn sách — số nhỏ hơn là sớm hơn.',
                             f'Cả hai tên nằm trong cùng đoạn ở {_page(doc, a["sourceBlockId"])}.'],
                      feedbackMatched=f'Khớp với sách: {before["title"]} ({before["when"]}) diễn ra trước.',
                      scaffold=f'Sách ghi {a["title"]} ({a["when"]}) và {b["title"]} ({b["when"]}) — năm nhỏ hơn là sớm hơn. Mình đi tiếp nhé.',
                      keySource=f'{RULE_EVENTS} — so sánh yearStart của hai sự kiện trong block {a["sourceBlockId"]}; KHÔNG phải SGV'))
    # cause / effect — the concluding sentence of the first complete story
    story = next((s for s in attributions if s['conclusionBlockId'] and s['title']), None)
    if story:
        concl = next(x for x in doc['blocks'] if x['id'] == story['conclusionBlockId'])
        key = [k for k in ('bất khuất', 'tiền đề', 'tinh thần', 'lòng yêu nước', 'trưởng thành', 'chấm dứt', 'độc lập') if k in concl['text'].lower()]
        if key:
            steps.append(dict(type='ask', id='q3', prompt=f'Theo câu chuyện «{story["title"]}», cuộc khởi nghĩa ấy đã chứng tỏ điều gì?', promptBlockId=concl['id'],
                              options=[], acceptable=[_rx(k) for k in key],
                              hints=['Con đọc câu cuối của câu chuyện — câu nói về ý nghĩa, không phải diễn biến.',
                                     f'Câu đó nằm ngay trên dòng «(Theo …)» ở {_page(doc, concl["id"])}.'],
                              feedbackMatched='SAM thấy câu trả lời của con có ý sách nêu ở câu kết. (Đây là kịch bản thử nghiệm; thầy cô mới là người xác nhận.)',
                              scaffold='Ý ở câu kết của câu chuyện — mình đọc lại câu đó rồi đi tiếp nhé.',
                              keySource=f'{RULE_ATTR} — câu kết {concl["id"]} của câu chuyện có nguồn {story["attributionBlockId"]}; KHÔNG phải SGV'))
        steps.append(dict(type='explain', id='e2', mascot='sam-explain', sourceBlockId=story['attributionBlockId'],
                          text=f'Câu chuyện «{story["title"]}» được sách kể theo một nguồn khác — dòng «(Theo …)» cuối câu chuyện cho biết nguồn ấy'
                               + (f' ({story["publisher"]}, {story["year"]})' if story.get('publisher') and story.get('year') else '')
                               + '. Khi kể lại cho bạn, con cũng nói rõ mình kể theo sách nào nhé.'))
    # the verbatim SGK ask: complete the timeline — checked by the extracted events
    ask = next((x for x in doc['blocks'] if x['id'] == timeline_ask_id), None) if timeline_ask_id else None
    if ask and ask['id'] not in fig_q:
        names = [e['title'] for e in events[1:-1]]
        steps.append(dict(type='ask', id='q4', prompt=ask['text'], promptBlockId=ask['id'], options=[],
                          acceptable=[r'(' + '|'.join(_rx(n) for n in names) + r').{0,40}\b(' + '|'.join(str(e['yearStart']) for e in events[1:-1]) + r')\b'],
                          hints=[f'Trục bắt đầu bằng {events[0]["title"]} ({events[0]["when"]}) và kết thúc bằng năm {events[-1]["yearStart"]} — con chọn các cuộc ở giữa theo thứ tự năm, ghi tên kèm năm.',
                                 f'Các cuộc đấu tranh và năm nằm trong đoạn sách ở {_page(doc, events[1]["sourceBlockId"])}.'],
                          feedbackMatched='SAM thấy con ghi đúng một cặp «tên — năm» có trong sách. Con kiểm thứ tự trên trục trong phần Trực quan nhé.',
                          scaffold='Mình mở phần Trực quan: dòng thời gian xếp sẵn các cuộc theo năm sách nêu — con chép lại vào vở rồi đi tiếp nhé.',
                          keySource=f'{RULE_EVENTS} — các cặp tên/năm từ block {events[1]["sourceBlockId"]}; kiểm thứ tự bằng TimelineValidator; KHÔNG phải SGV'))
    steps.append(dict(type='next', id='n1', label='Xem dòng thời gian trong Trực quan', target='visual', anchorBlockId=first['sourceBlockId']))
    # answer-leak self-check: no hint may match an acceptable pattern of its own step
    for s in steps:
        if s['type'] == 'ask':
            assert len(s['hints']) <= 2 and s['acceptable'] and s['keySource']
            for h in s['hints']:
                for pat in s['acceptable']:
                    assert not re.search(pat, h.lower(), re.I), f'answer leak in hint of {s["id"]}: {h!r} ~ {pat!r}'
    return dict(samMode='prototypeScripted', trust='prototype', evidencePolicy='none', steps=steps)


# ---------------------------------------------------------------- apply
def apply(doc, toc_title=None, timeline_ask_id=None, verbatim=None, gate=True):
    out = json.loads(json.dumps(doc))
    verbatim = verbatim or Verbatim(None)
    gate = gate and verbatim.enabled
    events, mentions, events_held = derive_events(out, verbatim, gate)
    attributions, attributions_held = derive_attributions(out, verbatim, gate)
    fig_q = figure_dependent_questions(out)
    title, title_der = lesson_title(out, toc_title)
    out['title'] = title
    if timeline_ask_id is None:
        timeline_ask_id = next((b['id'] for b in out['blocks'] if b['type'] == 'question' and re.search(r'trục thời gian', b.get('text') or '', re.I)), None)
    if events:
        sec = section_heading_before(out, events[0]['sourceBlockId'])
        trust = events[0]['trust']
        out.setdefault('semantic', [])
        out['semantic'] = [s for s in out['semantic'] if s.get('derivation') != RULE_EVENTS]
        out['semantic'].append(dict(type='timeline', id='timeline-1', title=(sec['text'] if sec else 'Dòng thời gian theo sách'), trust=trust, derivation=RULE_EVENTS,
                                    events=[dict(when=e['when'], title=e['title'], text=e['text'], sourceBlockId=e['sourceBlockId'],
                                                 yearStart=e['yearStart'], yearEnd=e['yearEnd'], era=e['era'], charSpan=e['charSpan'],
                                                 verbatimStatus=e['verbatimStatus']) for e in events],
                                    sources=[dict(attributionBlockId=a['attributionBlockId'], titleBlockId=a['titleBlockId'], storyBlockIds=a['storyBlockIds'],
                                                  withheldPartIds=a['withheldPartIds'], publisher=a['publisher'], year=a['year'], form=a['form'],
                                                  verbatimStatus=a['verbatimStatus'], titleVerbatimStatus=a['titleVerbatimStatus'],
                                                  derivation=RULE_ATTR) for a in attributions]))
    script = tutor_script(out, events, attributions, fig_q, timeline_ask_id)
    if script:
        out['tutorScript'] = script
    # SGK questions the script could NOT use: withheld (no text) or figure-dependent — listed, never guessed
    withheld_q = [b['id'] for b in out['blocks'] if b['type'] == 'withheld' and b.get('sourceRole') == 'question']
    out.setdefault('provenance', {})['historyRules'] = dict(
        version=VERSION if gate else VERSION_V1, rules=[RULE_EVENTS, RULE_ATTR, RULE_FIGQ, RULE_TITLE, RULE_TUTOR],
        events=len(events), narrativeYearMentionsNotEvents=len(mentions),
        attributions=len(attributions), attributionsComplete=sum(1 for a in attributions if a['complete']), figureDependentQuestions=fig_q,
        withheldQuestionsNotUsed=withheld_q, timelineAskBlockId=timeline_ask_id, titleDerivation=title_der, tutorSteps=len(script['steps']) if script else 0,
        verbatimGate=dict(enabled=bool(gate), ledger=(os.path.basename(verbatim.path) if verbatim.path else None),
                          eventsWithheld=len(events_held), attributionsWithheld=len(attributions_held),
                          blockStatus={_short(b['id']): verbatim.status(b['id']) for b in out['blocks']} if gate else {}))
    report = dict(version=VERSION if gate else VERSION_V1, events=events, narrativeYearMentions=mentions, attributions=attributions,
                  eventsWithheld=events_held, attributionsWithheld=attributions_held, verbatimGate=bool(gate),
                  figureDependentQuestions=fig_q,
                  withheldQuestionsNotUsed=withheld_q, titleDerivation=title_der, timelineAskBlockId=timeline_ask_id, tutorScript=script)
    return out, report


def report_md(rep, doc):
    L = [f"# History rules report — {doc['book']} Bài {doc['lesson']} ({rep['version']})\n",
         f"Title: `{doc['title']}` ← {rep['titleDerivation']}\n",
         f"## {RULE_EVENTS}: {len(rep['events'])} events (narrative «năm …» mentions counted, not promoted: {len(rep['narrativeYearMentions'])})\n",
         '| # | when | yearStart–yearEnd | era | title (actor) | block | page (printed) | bbox | char span | trust |', '|---|---|---|---|---|---|---|---|---|---|']
    for i, e in enumerate(rep['events'], 1):
        L.append(f"| {i} | {e['when']} | {e['yearStart']}–{e['yearEnd']} | {e['era']} | {e['title']} | {e['sourceBlockId'].split(':', 1)[1]} | {e['pagePdf']} ({e['pagePrinted']}) | {[round(v, 3) for v in e['bbox']]} | {e['charSpan']} | {e['trust']} |")
    L.append(f"\n## {RULE_ATTR}: {len(rep['attributions'])} attributions\n")
    L.append('| # | form | publisher | year | story title block | story blocks | withheld parts | complete | block | page (printed) | bbox |')
    L.append('|---|---|---|---|---|---|---|---|---|---|---|')
    for i, a in enumerate(rep['attributions'], 1):
        L.append(f"| {i} | {a['form']} | {a['publisher']} | {a['year']} | {(a['titleBlockId'] or '—').split(':')[-1]} | {len(a['storyBlockIds'])} | {len(a['withheldPartIds'])} {a['withheldReasons'] or ''} | {a['complete']} | {a['attributionBlockId'].split(':', 1)[1]} | {a['pagePdf']} ({a['pagePrinted']}) | {[round(v, 3) for v in a['bbox']]} |")
    if rep.get('verbatimGate'):
        held_e, held_a = rep['eventsWithheld'], rep['attributionsWithheld']
        L.append(f"\n## verbatim gate (v2): {len(held_e)} events and {len(held_a)} attributions NOT emitted\n")
        L.append('| kind | block | reason | slips the print shows |')
        L.append('|---|---|---|---|')
        for e in held_e:
            L.append(f"| event «{e['title']} ({e['when']})» | {_short(e['sourceBlockId'])} | {e['withheldReason']} | {_slips(e['slips'])} |")
        for x in held_a:
            L.append(f"| attribution {x['publisher']}, {x['year']} | {_short(x['attributionBlockId'])} | {x['withheldReason']} | {_slips(x['slips'])} |")
        L.append('')
    L.append(f"\n## {RULE_FIGQ}: {rep['figureDependentQuestions']}\n")
    ts = rep['tutorScript']
    L.append(f"## {RULE_TUTOR}: {'no script (fewer than 3 dated events)' if not ts else str(len(ts['steps'])) + ' steps'}\n")
    if ts:
        L.append('| step | type | prompt/source block | key source |\n|---|---|---|---|')
        for s in ts['steps']:
            L.append(f"| {s['id']} | {s['type']} | {(s.get('promptBlockId') or s.get('sourceBlockId') or s.get('anchorBlockId') or '—').split(':', 1)[-1]} | {s.get('keySource', '—')} |")
    return '\n'.join(L) + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--doc', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--toc-title', default=None)
    ap.add_argument('--report', action='store_true')
    ap.add_argument('--verbatim-ledger', default=None,
                    help='JSON ledger of an INDEPENDENT read of the printed page '
                         '(docs/research/lane-c/data/*-verbatim-ledger.json). With it the rules run v2: '
                         'nothing is emitted from a block that is not verbatim-verified.')
    ap.add_argument('--no-gate', action='store_true',
                    help='v1 behaviour — emit from any TRUSTED block (reproduces the round-4 numbers)')
    a = ap.parse_args(argv)
    doc = json.load(open(a.doc, encoding='utf-8'))
    verbatim = Verbatim.load(a.verbatim_ledger)
    out, rep = apply(doc, toc_title=a.toc_title, verbatim=verbatim, gate=not a.no_gate)
    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, os.path.basename(a.doc))
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print(path)
    print(f"  {rep['version']} · verbatim gate {'ON' if rep['verbatimGate'] else 'OFF'}")
    print(f"  events={len(rep['events'])} (gate withheld {len(rep['eventsWithheld'])}) "
          f"attributions={len(rep['attributions'])} (complete {sum(1 for x in rep['attributions'] if x['complete'])}, "
          f"gate withheld {len(rep['attributionsWithheld'])}) "
          f"figure-dependent questions={rep['figureDependentQuestions']} "
          f"tutorSteps={len(rep['tutorScript']['steps']) if rep['tutorScript'] else 0} title={out['title']!r}")
    if a.report:
        json.dump(rep, open(os.path.join(a.out, 'history-rules-report.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        open(os.path.join(a.out, 'history-rules-report.md'), 'w', encoding='utf-8').write(report_md(rep, out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
