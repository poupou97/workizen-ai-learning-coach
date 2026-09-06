#!/usr/bin/env python3
"""Lane E1 · P0.1 — TSL -> SemanticGraphCandidate, by deterministic rules only.

One extractor, many subjects. Every rule here is subject-agnostic: it reads roles,
heading nesting, enumerators, connectives and figure references that the SGK prints in
every book. Nothing here knows what "tách chất" or "Bắc thuộc" means, and there is no
per-subject branch — that is the reuse claim this file exists to make falsifiable.

EVERY relation carries its OWN claim, grounded in the text that ASSERTS the relation.
A `causes` edge whose two endpoints are grounded but whose connective is not, is not
emitted. That is §5 enforced in code rather than in prose.

No LLM is called anywhere in this module.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ontology as onto  # noqa: E402
from graph import (SemanticClaim, SemanticGraph, SemanticNode,  # noqa: E402
                   SemanticRelation, SourceGrounding)

# --- enumerators the SGK actually prints (measured on the TSL layer) ------------
ENUM_RX = [
    ('bullet',  re.compile(r'^\s*([·•▪–-])\s+')),
    ('num_dot', re.compile(r'^\s*(\d{1,2})\s*[.)]\s+')),
    ('alpha',   re.compile(r'^\s*([a-hA-H])\s*[.)]\s+')),
    ('buoc',    re.compile(r'^\s*(?:bước|Bước|BƯỚC)\s+(\d{1,2})\s*[:.]?\s*')),
]
STAGE_SEQ_RX = re.compile(r'^\s*(?:chuẩn\s+bị|tiến\s+hành|thực\s+hiện|quan\s+sát|'
                          r'nhận\s+xét|kết\s+luận|thảo\s+luận)', re.I)

# ⭐ AN ENUMERATION IS NOT A PROCEDURE.
# Measured on KHTN 6 Bai 17: treating every run of >=2 same-marked siblings as a
# process produced 7 "procedures", of which the first two were the lesson's OBJECTIVES
# ("· Trình bày được…") and a pair of numbered QUESTIONS. Both are ordered on the page
# and neither is a process. So ordinal succession (`next`) and procedurality are
# separated: the enumerator asserts ORDER, the governing stage label / heading asserts
# PROCEDURE. Only a run with a procedural governor yields `Step` primitives; the rest
# yield `Statement`s that are still `next`-linked and feed no visual family.
# ⭐ The governor test runs on a DIACRITIC-STRIPPED string, and that is not a
# convenience. Measured on this very lesson: the block that governs Bai 17's filtering
# procedure reads «Chuẩn bị: … Tiền hành:» — OCR turned «Tiến hành» into «Tiền hành»
# (round 4 names this exact slip as one of the four that survive because BOTH OCR
# stacks make it). Matching the accented form only, one tone slip deletes the sole
# signal that a bulleted run is a procedure, and the lesson silently loses its whole
# PROCESS family. Comparing without tones is a general repair for that class, not a
# special case for one typo.
_DIA = str.maketrans(
    'àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ'
    'ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ',
    'a' * 17 + 'e' * 11 + 'i' * 5 + 'o' * 17 + 'u' * 11 + 'y' * 5 + 'd'
    + 'A' * 17 + 'E' * 11 + 'I' * 5 + 'O' * 17 + 'U' * 11 + 'Y' * 5 + 'D')


def strip_tones(text):
    return (text or '').translate(_DIA).lower()


PROCEDURAL_CTX_RX = re.compile(
    r'(?:tien\s+hanh|thuc\s+hien|cach\s+(?:lam|tien\s+hanh)|cac\s+buoc|quy\s+trinh|'
    r'thi\s+nghiem|thuc\s+hanh|chuan\s+bi|trinh\s+tu|huong\s+dan|thao\s+tac)')
NON_PROCEDURAL_CTX_RX = re.compile(
    r'(?:muc\s+tieu|em\s+se|luyen\s+tap|van\s+dung|cau\s+hoi|khoi\s+dong|'
    r'em\s+da\s+hoc|ghi\s+nho|tim\s+hieu\s+them)')

# A causal connective must sit INSIDE one block, with text on both sides of it.
# re.I matters: a sentence-initial connective is capitalised ("Vì … nên …"), and the
# first version silently found nothing on exactly those sentences.
# `_CB` anchors a cause clause at a real clause boundary. Without it `.{6,90}?` starts
# wherever the regex engine finds it cheapest, and the extracted cause began mid-word —
# "h 17.1, hạt phù sa …" out of "Hình 17.1, hạt phù sa …". A cause that starts mid-word
# is not a quotation of the book, whatever its span says.
_CB = r'(?:^|(?<=[.;:!?])\s|(?<=,)\s)'
CAUSAL_RX = [
    ('vi_nen',     re.compile(r'(?<![\wÀ-ỹ])vì\s+(?P<c>[^.;:!?]{4,90}?)\s+nên\s+'
                              r'(?P<e>[^.;:!?]{4,120})', re.I)),
    ('do_nen',     re.compile(r'(?<![\wÀ-ỹ])do\s+(?P<c>[^.;:!?]{4,90}?)\s+nên\s+'
                              r'(?P<e>[^.;:!?]{4,120})', re.I)),
    ('dan_den',    re.compile(_CB + r'(?P<c>[^.;:!?]{6,90}?)\s+(?:dẫn\s+đến|dẫn\s+tới|'
                              r'gây\s+ra|làm\s+cho)\s+(?P<e>[^.;:!?]{4,120})', re.I)),
    ('nho_do',     re.compile(_CB + r'(?P<c>[^.;:!?]{6,90}?)\s*[,]?\s+'
                              r'(?:nhờ\s+đó|vì\s+vậy|do\s+đó)\s+'
                              r'(?P<e>[^.;:!?]{4,120})', re.I)),
]
DEFN_RX = None  # built below, after UPPER is defined
CONTRAST_RX = [
    ('khac_nhau', re.compile(r'(?:khác\s+nhau|điểm\s+khác|sự\s+khác\s+biệt|phân\s+biệt|'
                             r'so\s+sánh)\s+(?:giữa\s+)?(?P<a>[^.;?]{2,80})')),
]
FIG_REF_RX = re.compile(r'(?:hình|Hình|HÌNH)\s+(\d{1,2}(?:[.,]\d{1,2})?)')
FIG_LABEL_RX = re.compile(r'^\s*(?:hình|Hình|HÌNH)\s+(\d{1,2}(?:[.,]\d{1,2})?)\s*[.:]?\s*$')
YEAR_RX = re.compile(r'(?<![\d])(?:năm\s+)?(\d{3,4})(?:\s*[-–—]\s*(\d{3,4}))?'
                     r'(\s*(?:TCN|tcn|trước\s+Công\s+nguyên))?')
# Inside a parenthesis the context is already narrow, so a 1-2 digit year counts —
# Vietnamese history needs it ("Hai Bà Trưng (40 - 43)"). The guard against matching
# "(hình 2)" is that the WHOLE parenthesis must look like a date expression.
WHEN_DATE_RX = re.compile(r'^(?:năm|ngày|tháng|thế\s+k[iỉíỷỳ]|tcn|trước\s+công\s+nguyên|'
                          r'[\d\s\-–—/.,]|[IVXivx])+$', re.I)
WHEN_HAS_DIGIT_RX = re.compile(r'\d')
# ⚠️ `[A-ZÀ-Ỹ]` LOOKS like "an uppercase Vietnamese letter" and is not. As a RANGE it
# spans U+00C0..U+1EF8, which contains every lowercase accented Vietnamese letter too
# (á U+00E1, ă U+0103, ủ U+1EE7 …). The first version used it and produced event titles
# like 'ăm' (from "năm") and 'ủa Ngô Quyền' (from "của") — a mid-word start that reads as
# a real name in the output. So the class is built from Unicode case, not from a range.
_VN_UPPER = ''.join(chr(c) for c in list(range(0x41, 0x5B)) + list(range(0xC0, 0x1F00))
                    if chr(c).isupper() and chr(c).isalpha())
_VN_LETTER = r'\w'          # Python 3 \w is already Unicode-aware for Vietnamese
UPPER = '[' + re.escape(_VN_UPPER) + ']'

# A capitalised run may itself contain a hyphen ("Lý Bí - Triệu Quang Phục"), and a
# `when` may be a single bare year ("(248)"). Both were missed by a stricter first
# version; the miss was found by comparing against Lane C's hand-checked 7/7 on this
# very lesson, which is why that comparison is part of the test suite.
DATED_EVENT_RX = re.compile(
    r'(?P<title>' + UPPER + _VN_LETTER + r'*(?:\s*[-–—]?\s*' + UPPER + _VN_LETTER +
    r'*){0,5})\s*\((?P<when>[^()]{2,44})\)')

DEFN_RX = [
    ('goi_la', re.compile(r'(?P<t>[^.;:]{2,60}?)\s+(?:được\s+)?gọi\s+là\s+(?P<d>[^.;]{2,90})')),
    ('la_def', re.compile(r'^(?P<t>' + UPPER + r'[^.;:]{2,60}?)\s+là\s+(?P<d>[^.;]{6,140})')),
]

# roles whose text the source itself marks as procedural / structural
PROCEDURAL_ROLES = ('instruction', 'activity', 'stage_label')


def _g(block, span=None, quote=None):
    return SourceGrounding.from_tsl_block(block, span=span, quote=quote)


def _nid(prefix, *parts):
    """A node id that is unique WITHIN a lesson and says nothing about WHICH lesson.

    ⭐ It used to embed `graph.book` and `graph.lesson`, so a renderer could parse
    `step:06-sgk-khoa-hoc-tu-nhien-6|17|0|0#n1` and branch on the lesson — the exact door
    Lane E2 closed by making lesson identity untypable on its side. The graph object
    already knows which lesson it is; its nodes do not need to repeat it, and the
    identity a reader legitimately needs is on the lineage artefact.
    """
    return prefix + ':' + '|'.join(str(p) for p in parts)


# ---------------------------------------------------------------------------
# rule 1 — e1-ordered-steps-v1 : Step nodes + `next`
#   The `next` relation is grounded in the ENUMERATORS, because the enumerator is what
#   the page prints to assert the order. Grounding it in the step texts would be the
#   §5 mistake: two grounded steps do not make a grounded ordering.
# ---------------------------------------------------------------------------
def _is_procedural(governor, items):
    """Does the SOURCE mark this run as a procedure, or merely as a list?"""
    gov = strip_tones(governor or '')
    if NON_PROCEDURAL_CTX_RX.search(gov):
        return False
    if PROCEDURAL_CTX_RX.search(gov):
        return True
    # no governor signal: fall back to the items themselves — a procedure's items are
    # instructions, and the pipeline already role-tags those.
    roles = {b['role'] for b, _ in items}
    return bool(roles & {'instruction', 'activity'})


def rule_ordered_steps(les, graph):
    rule = 'e1-ordered-steps-v1'
    runs, cur, cur_kind, gov = [], [], None, ''
    for b in les['blocks']:
        # A governor is whatever the page prints to introduce what follows. On Bai 17
        # that is an `instruction` block («Chuẩn bị: … Tiến hành:»), NOT the section
        # heading («Lọc nước từ hỗn hợp nước lẫn đất») — reading only headings found no
        # procedure at all in a lesson that plainly contains two.
        is_governor = (b['role'] in ('heading', 'stage_label', 'instruction')
                       or PROCEDURAL_CTX_RX.search(strip_tones(b['text'] or ''))
                       is not None)
        if is_governor:
            if len(cur) >= 2:
                runs.append((cur_kind, cur, gov))
            cur, cur_kind = [], None
            gov = b['text'] or ''
            continue
        kind = None
        for name, rx in ENUM_RX:
            m = rx.match(b['text'] or '')
            if m:
                kind = (name, m)
                break
        if kind is None and STAGE_SEQ_RX.match(b['text'] or ''):
            kind = ('stage', STAGE_SEQ_RX.match(b['text']))
        if kind is None:
            continue
        if cur_kind is None or kind[0] == cur_kind:
            cur_kind = kind[0]
            cur.append((b, kind[1]))
        else:
            if len(cur) >= 2:
                runs.append((cur_kind, cur, gov))
            cur, cur_kind = [(b, kind[1])], kind[0]
    if len(cur) >= 2:
        runs.append((cur_kind, cur, gov))

    made = 0
    for ri, (kind, items, governor) in enumerate(runs):
        procedural = _is_procedural(governor, items)
        primitive = 'Step' if procedural else 'Statement'
        node_ids = []
        for i, (b, m) in enumerate(items):
            nid = _nid('step' if procedural else 'item', ri, i)
            claim = SemanticClaim(
                kind='node', subject=nid,
                assertion=('%s %d of a printed enumeration (%s) under "%s"'
                           % ('step' if procedural else 'item', i + 1, kind,
                              (governor or '?')[:40])),
                # the book DEMONSTRATES the procedure by printing marked items; it does
                # not STATE "this is step 1 of a process".
                support='sourceDemonstrated', derivation=rule,
                grounding=[_g(b, quote=b['text'][:160])],
                confidence=0.7 if procedural else 0.5)
            graph.add_node(SemanticNode(nid, primitive, b['text'], claims=[claim],
                                        order=i + 1, enumerator=kind,
                                        governor=(governor or None)[:60] if governor else None))
            node_ids.append(nid)
        for i in range(len(node_ids) - 1):
            b, m = items[i]
            span = (m.start(), m.end()) if m.end() > m.start() else None
            rc = SemanticClaim(
                kind='relation', subject={'from': node_ids[i], 'rel': 'next',
                                          'to': node_ids[i + 1]},
                assertion=('the page marks these items in order with "%s" enumerators'
                           ' (procedural context: %s)' % (kind, procedural)),
                # a deterministic rule over the printed marker, not a book sentence
                support='systemDerived', derivation=rule,
                grounding=[_g(b, span=span, quote=(b['text'] or '')[m.start():m.end()])],
                confidence=0.75)
            graph.add_relation(SemanticRelation('next', node_ids[i], node_ids[i + 1], rc))
        made += 1
    return made


# ---------------------------------------------------------------------------
# rule 2 — e1-heading-partonomy-v1 : Entity nodes from the printed heading nesting
#   Support is systemDerived: the book prints the nesting, it never says "A has part B".
# ---------------------------------------------------------------------------
def rule_heading_partonomy(les, graph):
    rule = 'e1-heading-partonomy-v1'
    seen, made = {}, 0
    for b in les['blocks']:
        if b['role'] != 'heading':
            continue
        path = [h for h in (b['heading_path'] or []) if h and h.strip()]
        if not path:
            continue
        prev = None
        for depth, h in enumerate(path):
            nid = _nid('ent', depth, h[:48])
            if nid not in seen:
                claim = SemanticClaim(
                    kind='node', subject=nid,
                    assertion='a section the book prints as a heading at depth %d' % depth,
                    support='sourceStated', derivation=rule,
                    grounding=[_g(b, quote=h[:120])], confidence=0.9)
                graph.add_node(SemanticNode(nid, 'Entity', h, claims=[claim], depth=depth))
                seen[nid] = True
            if prev is not None and prev != nid:
                rc = SemanticClaim(
                    kind='relation', subject={'from': prev, 'rel': 'hasPart', 'to': nid},
                    assertion='the page nests this heading under the previous one',
                    support='systemDerived', derivation=rule,
                    grounding=[_g(b, quote=' > '.join(path[:depth + 1])[:160])],
                    confidence=0.8)
                try:
                    graph.add_relation(SemanticRelation('hasPart', prev, nid, rc))
                    made += 1
                except Exception:
                    pass
            prev = nid
    return made


# ---------------------------------------------------------------------------
# rule 3 — e1-prose-dated-events-v1 : Event + atTime
#   Prior art audited, not duplicated: Lane C's `prose-dated-events-v1`
#   (tool/research/lane_c/history_rules.py, docs/research/lane-c/05-GOLDEN-SLICE-2-GATE.md)
#   measured 7/7 on LS&DL 5 Bai 8. This is the same SHAPE lifted into the core so it is
#   not a History rule; it is the core TIMELINE rule that History happens to exercise.
# ---------------------------------------------------------------------------
def rule_dated_events(les, graph):
    rule = 'e1-prose-dated-events-v1'
    made = 0
    for b in les['blocks']:
        if b['role'] in ('heading',):
            continue
        text = b['text'] or ''
        for m in DATED_EVENT_RX.finditer(text):
            when, title = m.group('when').strip(), m.group('title').strip()
            if not (WHEN_HAS_DIGIT_RX.search(when) and WHEN_DATE_RX.match(when)):
                continue
            nid = _nid('evt', title[:40], when[:20])
            if nid in graph.nodes:
                continue
            claim = SemanticClaim(
                kind='node', subject=nid,
                assertion='the book names this event with a parenthesised date',
                support='sourceStated', derivation=rule,
                grounding=[_g(b, span=(m.start(), m.end()), quote=m.group(0))],
                confidence=0.85)
            graph.add_node(SemanticNode(nid, 'Event', title, claims=[claim], when=when))
            ac = SemanticClaim(
                kind='relation', subject={'from': nid, 'rel': 'atTime', 'to': when},
                assertion='the date is printed in parentheses immediately after the name',
                support='sourceStated', derivation=rule,
                grounding=[_g(b, span=(m.start('when'), m.end('when')), quote=when)],
                confidence=0.85)
            graph.add_claim(ac)
            graph.nodes[nid].attrs['atTimeClaim'] = ac.id
            made += 1
    return made


# ---------------------------------------------------------------------------
# rule 4 — e1-figure-reference-v1 : Figure nodes + refersToFigure
# ---------------------------------------------------------------------------
def rule_figure_reference(les, graph):
    rule = 'e1-figure-reference-v1'
    made = 0
    fig_nodes = {}
    # figure LABEL blocks ("Hình 17.1") are the anchors the prose refers to
    for b in les['blocks']:
        m = FIG_LABEL_RX.match((b['text'] or '').strip())
        if not m:
            continue
        num = m.group(1)
        nid = _nid('fig', num)
        if nid in fig_nodes:
            continue
        claim = SemanticClaim(
            kind='node', subject=nid,
            assertion='the page prints a figure label',
            support='sourceStated', derivation=rule,
            grounding=[_g(b, quote=b['text'][:60])], confidence=0.9)
        graph.add_node(SemanticNode(nid, 'Figure', b['text'].strip(), claims=[claim],
                                    figureNumber=num))
        fig_nodes[nid] = num
    for b in les['blocks']:
        if FIG_LABEL_RX.match((b['text'] or '').strip()):
            continue
        for m in FIG_REF_RX.finditer(b['text'] or ''):
            nid = _nid('fig', m.group(1))
            if nid not in fig_nodes:
                continue
            src = _nid('stmt', b['id'])
            if src not in graph.nodes:
                sc = SemanticClaim(
                    kind='node', subject=src,
                    assertion='a trusted text block of this lesson',
                    support='sourceStated', derivation=rule,
                    grounding=[_g(b, quote=(b['text'] or '')[:160])], confidence=0.9)
                graph.add_node(SemanticNode(src, 'Statement', (b['text'] or '')[:120],
                                            claims=[sc], role=b['role']))
            rc = SemanticClaim(
                kind='relation', subject={'from': src, 'rel': 'depicts', 'to': nid},
                assertion='this text names the figure explicitly',
                support='sourceStated', derivation=rule,
                grounding=[_g(b, span=(m.start(), m.end()), quote=m.group(0))],
                confidence=0.85)
            try:
                graph.add_relation(SemanticRelation('depicts', src, nid, rc))
                made += 1
            except Exception:
                pass
    return made


# ---------------------------------------------------------------------------
# rule 5 — e1-causal-connective-v1 : `causes`, grounded in the CONNECTIVE
# ---------------------------------------------------------------------------
def rule_causal(les, graph):
    rule = 'e1-causal-connective-v1'
    made = 0
    for b in les['blocks']:
        text = b['text'] or ''
        for name, rx in CAUSAL_RX:
            m = rx.search(text)
            if not m:
                continue
            cause, effect = m.group('c').strip(), m.group('e').strip()
            if len(cause) < 4 or len(effect) < 4:
                continue
            cid = _nid('stmt', b['id'], 'c')
            eid = _nid('stmt', b['id'], 'e')
            for nid, txt, sp in ((cid, cause, (m.start('c'), m.end('c'))),
                                 (eid, effect, (m.start('e'), m.end('e')))):
                if nid in graph.nodes:
                    continue
                sc = SemanticClaim(
                    kind='node', subject=nid, assertion='a clause the book prints',
                    support='sourceStated', derivation=rule,
                    grounding=[_g(b, span=sp, quote=txt[:160])], confidence=0.8)
                graph.add_node(SemanticNode(nid, 'Statement', txt[:120], claims=[sc]))
            # the connective span is the evidence FOR THE RELATION
            conn_start = m.end('c')
            conn_end = m.start('e')
            if conn_end <= conn_start:
                conn_start, conn_end = m.start(), m.end()
            rc = SemanticClaim(
                kind='relation', subject={'from': cid, 'rel': 'causes', 'to': eid},
                assertion='the book joins these two clauses with a causal connective (%s)' % name,
                support='sourceStated', derivation=rule,
                grounding=[_g(b, span=(conn_start, conn_end),
                              quote=text[conn_start:conn_end])], confidence=0.7)
            try:
                graph.add_relation(SemanticRelation('causes', cid, eid, rc))
                made += 1
            except Exception:
                pass
            break
    return made


# ---------------------------------------------------------------------------
# rule 6 — e1-definition-v1 : Entity + hasProperty (a stated definition)
# ---------------------------------------------------------------------------
def rule_definition(les, graph):
    rule = 'e1-definition-v1'
    made = 0
    for b in les['blocks']:
        if b['role'] not in ('body', 'sidebar', 'caption'):
            continue
        text = b['text'] or ''
        for name, rx in DEFN_RX:
            m = rx.search(text)
            if not m:
                continue
            term, defn = m.group('t').strip(), m.group('d').strip()
            if len(term) < 2 or len(defn) < 6:
                continue
            tid = _nid('ent', 'def', term[:40])
            did = _nid('stmt', b['id'], 'd')
            if tid not in graph.nodes:
                tc = SemanticClaim(
                    kind='node', subject=tid, assertion='a term the book names',
                    support='sourceStated', derivation=rule,
                    grounding=[_g(b, span=(m.start('t'), m.end('t')), quote=term)],
                    confidence=0.65)
                graph.add_node(SemanticNode(tid, 'Entity', term, claims=[tc]))
            if did not in graph.nodes:
                dc = SemanticClaim(
                    kind='node', subject=did, assertion='the definition clause as printed',
                    support='sourceStated', derivation=rule,
                    grounding=[_g(b, span=(m.start('d'), m.end('d')), quote=defn[:160])],
                    confidence=0.65)
                graph.add_node(SemanticNode(did, 'Statement', defn[:120], claims=[dc]))
            rc = SemanticClaim(
                kind='relation', subject={'from': tid, 'rel': 'hasProperty', 'to': did},
                assertion='the book links term and definition with "%s"' % name,
                support='sourceStated', derivation=rule,
                grounding=[_g(b, span=(m.start(), m.end()), quote=m.group(0)[:180])],
                confidence=0.6)
            try:
                graph.add_relation(SemanticRelation('hasProperty', tid, did, rc))
                made += 1
            except Exception:
                pass
            break
    return made


RULES = [
    ('e1-ordered-steps-v1', rule_ordered_steps),
    ('e1-heading-partonomy-v1', rule_heading_partonomy),
    ('e1-prose-dated-events-v1', rule_dated_events),
    ('e1-figure-reference-v1', rule_figure_reference),
    ('e1-causal-connective-v1', rule_causal),
    ('e1-definition-v1', rule_definition),
]


def extract(les, subject=None, grade=None):
    """TSL lesson (corpus_io.load_tsl shape) -> SemanticGraph candidate."""
    g = SemanticGraph(les['book'], les['lesson'], les['title'], subject=subject,
                      grade=grade, pipeline=les.get('pipeline') or 'tc2')
    fired = {}
    for name, fn in RULES:
        try:
            fired[name] = fn(les, g)
        except Exception as e:      # a rule must never take the lesson down with it
            fired[name] = 'ERROR: %s' % e
            g.notes.append('rule %s failed: %s' % (name, e))
    g.notes.append({'rulesFired': fired})
    # withheld regions are recorded as an explicit hole, never silently skipped
    if les.get('withheld'):
        g.notes.append({'withheldRegions': len(les['withheld']),
                        'meaning': 'source text exists but may not be read; any claim '
                                   'depending on it is absent, not wrong'})
    return g


def families_present(graph):
    """Which visual families this graph could feed, from its own contents only."""
    rels = {}
    for r in graph.relations:
        rels[r.relation] = rels.get(r.relation, 0) + 1
    prims = {}
    for n in graph.nodes.values():
        prims[n.primitive] = prims.get(n.primitive, 0) + 1
    fams = set()
    if rels.get('next', 0) >= 1 and prims.get('Step', 0) >= 2:
        fams.add('PROCESS')
    if prims.get('Event', 0) >= 2:
        fams.add('TIMELINE')
    if rels.get('hasPart', 0) >= 2:
        fams.add('HIERARCHY')
    if rels.get('depicts', 0) >= 1:
        fams.add('LABELED_FIGURE')
    if rels.get('causes', 0) >= 1:
        fams.add('CAUSAL')
    if rels.get('hasProperty', 0) >= 1:
        fams.add('DEFINITION')
    typed = sum(rels.get(k, 0) for k in ('isA', 'hasPart', 'hasProperty', 'causes',
                                         'contrastsWith'))
    if typed >= 2 and len(graph.nodes) >= 3:
        fams.add('CONCEPT_MAP')
    return sorted(fams), prims, rels
