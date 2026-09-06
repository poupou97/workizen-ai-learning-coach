#!/usr/bin/env python3
"""Lane E1 · the DISCOVERED semantic ontology v0 — primitives, relations, families.

WHERE THIS CAME FROM. Not from the Founder's candidate list. Every cue below cites the
measured lesson count that `discover_markers.py` (cross-subject/cross-book n-gram mining)
and `probe_cues.py` produced on the units layer (denominator: 1,906 SGK lessons that have
role-tagged units). A cue with no measurement does not belong here.

    hình 84.6% · năm 49.5% · thuộc 45.8% · gồm 43.3% · khác nhau 41.7% · bảng 40.3%
    kết quả 38.9% · vì sao 36.8% · vị trí 32.9% · gọi là 32.4% · chuẩn bị 26.3%
    sau đó 26.2% · đơn vị 25.3% · sơ đồ 22.8% · so sánh 22.4% · bao gồm 21.5%
    các bước 21.0% · tại sao 20.6% · là gì 20.3% · tiến hành 19.6% · bước 1 18.4%
    do đó 16.3% · thứ tự 15.0% · phân biệt 14.7% · nguyên nhân 14.2% · dẫn đến 13.1%
    cuối cùng 12.1% · phân loại 11.2% · công thức 10.0% · giống nhau 9.7% · thế kỉ 8.8%
    bản đồ 6.1% · phương trình 5.4% · biểu đồ 5.1% · lược đồ 3.1% · trước CN 1.9%

THE HARD BOUNDARY THIS FILE ENFORCES.
    SOURCE TRUTH  ≠  SEMANTIC INTERPRETATION  ≠  VISUAL REPRESENTATION
A cue match is an INTERPRETATION. It is never source truth. Every claim this module
emits carries `inference='CUE_MATCH'` plus the block id and the character span of the
match, so a reviewer can go back to the printed page. Nothing here promotes a claim to
a graph edge; that is the job of a validation step that does not exist yet, and the
census reports the two counts separately for exactly that reason.

No LLM is called anywhere in this module.
"""
import re

# ---------------------------------------------------------------------------
# 1. PRIMITIVES — the node kinds a semantic graph would need
#    Every primitive must be justified by lessons that cannot be expressed without it.
# ---------------------------------------------------------------------------
PRIMITIVES = {
    # id             kind of thing                              justified by
    'Entity':     'a named thing: concept, object, organism, person, place, artefact',
    'Statement':  'a verbatim proposition carried from one source block (the carrier '
                  'primitive — every other primitive degrades to this when structure is lost)',
    'Step':       'an action at an ordinal position in a procedure',
    'Event':      'a happening that carries a time anchor',
    'Quantity':   'a number with a unit (and optionally a symbol)',
    'Figure':     'a source image region with bbox, optional caption, optional labels',
    'Formula':    'a VALIDATED structured expression (Lane A2 MathExpression / a chemical '
                  'reaction). Carrier only — the AST itself is A2\'s, tool/corpus/mathfix/. '
                  'Listed as a primitive because the census must be able to say "this '
                  'lesson needs one", and because today it has NO PATH: see the bridge '
                  'gap in docs/research/semantic-graph/01-AUDIT-CLASSIFICATION.md',
}

# Deliberately NOT primitives — measured as expressible by composition:
#   Property  = Entity --hasProperty--> (Statement | Quantity)
#   TimePoint = the `when` field of Event (it has no independent identity in the corpus)
#   Place     = Entity + locatedAt (no lesson was found needing a distinct Place node
#               that Entity+relation could not carry)
COMPOSED_NOT_PRIMITIVE = {
    'Property': 'Entity --hasProperty--> Statement|Quantity',
    'TimePoint': 'a field of Event, not a node',
    'Place': 'Entity reached by locatedAt',
    'Person': 'Entity (History extension adds a role tag, not a node kind)',
}

# ---------------------------------------------------------------------------
# 2. RELATIONS — the edge kinds
# ---------------------------------------------------------------------------
RELATIONS = {
    'next':          'Step -> Step, ordinal successor',
    'hasPart':       'Entity -> Entity, part/whole (inverse partOf)',
    'isA':           'Entity -> Entity, class membership / classification',
    'hasProperty':   'Entity -> Statement|Quantity, an attribute the source states',
    'contrastsWith': 'Entity -> Entity along a named dimension (Comparison is this '
                     'relation projected onto a grid, not a separate primitive)',
    'causes':        'Event|Entity -> Event|Entity, a stated cause/effect link',
    'atTime':        'Event -> when (verbatim time expression)',
    'depicts':       'Figure -> Entity|Statement, and its inverse refersToFigure',
    'locatedAt':     'Entity -> Entity(place)',
}

# ---------------------------------------------------------------------------
# 3. VISUAL FAMILIES — what a renderer draws. A family is a PROJECTION of
#    primitives+relations, never a new data model.
# ---------------------------------------------------------------------------
FAMILIES = {
    'PROCESS':        {'primitives': ['Step'], 'relations': ['next'],
                       'min_arity': '>=2 ordered steps'},
    'COMPARISON':     {'primitives': ['Entity'], 'relations': ['contrastsWith', 'hasProperty'],
                       'min_arity': '>=2 entities x >=1 shared dimension'},
    'HIERARCHY':      {'primitives': ['Entity'], 'relations': ['isA', 'hasPart'],
                       'min_arity': '>=1 parent with >=2 children'},
    'TIMELINE':       {'primitives': ['Event'], 'relations': ['atTime', 'next'],
                       'min_arity': '>=2 dated events'},
    'CAUSAL':         {'primitives': ['Entity', 'Event', 'Statement'], 'relations': ['causes'],
                       'min_arity': '>=1 cause -> effect pair'},
    'LABELED_FIGURE': {'primitives': ['Figure', 'Entity'], 'relations': ['depicts'],
                       'min_arity': '1 figure + >=1 label or caption'},
    'CONCEPT_MAP':    {'primitives': ['Entity'], 'relations': ['isA', 'hasPart', 'hasProperty',
                                                               'causes', 'contrastsWith'],
                       'min_arity': '>=3 entities, >=2 typed relations, not a tree'},
    'QUANTITY':       {'primitives': ['Quantity', 'Entity'], 'relations': ['hasProperty'],
                       'min_arity': '>=2 quantities sharing a dimension'},
    'SPATIAL':        {'primitives': ['Entity', 'Figure'], 'relations': ['locatedAt', 'depicts'],
                       'min_arity': 'a map/plan region + >=1 located entity'},
    'DEFINITION':     {'primitives': ['Entity', 'Statement'], 'relations': ['hasProperty'],
                       'min_arity': 'term + a stated definition'},
}

# ---------------------------------------------------------------------------
# 4. CUES — deterministic, measured, each tagged with the family it proposes.
#    Rules for a cue to live here:
#      * measured lesson coverage printed by probe_cues.py (see the header block),
#      * a word-boundary regex, never a bare substring,
#      * cues that a Vietnamese reader would call ambiguous carry `weak=True` and
#        cannot alone raise a lesson above tier B.
# ---------------------------------------------------------------------------


def _rx(*alts):
    return re.compile(r'(?<![\wÀ-ỹ])(?:%s)(?![\wÀ-ỹ])' % '|'.join(alts))


CUES = {
    'PROCESS': [
        ('buoc_n',      _rx(r'bước\s+\d+', r'bước\s+thứ\s+\w+'), False),
        ('cac_buoc',    _rx(r'các\s+bước', r'quy\s+trình', r'trình\s+tự'), False),
        ('tien_hanh',   _rx(r'tiến\s+hành', r'thực\s+hiện\s+theo', r'cách\s+làm',
                            r'chuẩn\s+bị'), True),
        ('seq_adv',     _rx(r'sau\s+đó', r'tiếp\s+theo', r'cuối\s+cùng', r'trước\s+hết',
                            r'đầu\s+tiên'), True),
        ('thu_tu',      _rx(r'thứ\s+tự', r'sắp\s+xếp\s+theo'), True),
    ],
    'COMPARISON': [
        ('so_sanh',     _rx(r'so\s+sánh', r'phân\s+biệt'), False),
        ('khac_giong',  _rx(r'khác\s+nhau', r'giống\s+nhau', r'điểm\s+khác',
                            r'điểm\s+giống', r'sự\s+khác\s+biệt'), False),
        ('doi_chieu',   _rx(r'đối\s+chiếu', r'trong\s+khi\s+đó', r'ngược\s+lại'), True),
    ],
    'HIERARCHY': [
        ('phan_loai',   _rx(r'phân\s+loại', r'các\s+loại', r'gồm\s+có', r'chia\s+thành',
                            r'chia\s+làm'), False),
        ('bao_gom',     _rx(r'bao\s+gồm', r'cấu\s+tạo\s+(?:gồm|của)', r'thành\s+phần',
                            r'bộ\s+phận'), False),
        ('thuoc_nhom',  _rx(r'thuộc\s+(?:nhóm|loại|họ|ngành|lớp)'), False),
        ('gom',         _rx(r'gồm'), True),
    ],
    'TIMELINE': [
        # a bare "năm" is a false friend (it also means "five"); require a year.
        ('nam_year',    _rx(r'năm\s+\d{3,4}'), False),
        ('the_ki',      _rx(r'thế\s+kỉ\s+[IVXivx]+', r'thế\s+kỷ\s+[IVXivx]+'), False),
        ('tcn',         _rx(r'trước\s+công\s+nguyên', r'\d{2,4}\s*tcn'), False),
        ('date_dmy',    _rx(r'ngày\s+\d{1,2}\s*[-/]\s*\d{1,2}\s*[-/]\s*\d{3,4}',
                            r'ngày\s+\d{1,2}\s+tháng\s+\d{1,2}'), False),
        ('giai_doan',   _rx(r'giai\s+đoạn', r'thời\s+kì', r'thời\s+kỳ'), True),
    ],
    'CAUSAL': [
        ('nguyen_nhan', _rx(r'nguyên\s+nhân', r'hậu\s+quả', r'hệ\s+quả'), False),
        ('dan_den',     _rx(r'dẫn\s+đến', r'dẫn\s+tới', r'làm\s+cho', r'gây\s+ra',
                            r'nhờ\s+đó'), False),
        ('vi_nen',      _rx(r'vì\s+.{1,60}?\s+nên', r'do\s+.{1,60}?\s+nên'), False),
        ('tai_sao',     _rx(r'vì\s+sao', r'tại\s+sao', r'giải\s+thích\s+vì'), True),
        ('do_do',       _rx(r'do\s+đó', r'vì\s+vậy', r'cho\s+nên'), True),
    ],
    'LABELED_FIGURE': [
        ('hinh_n',      _rx(r'hình\s+\d+(?:[.,]\d+)?'), False),
        ('quan_sat_h',  _rx(r'quan\s+sát\s+hình', r'dựa\s+vào\s+hình', r'chú\s+thích'), False),
        ('so_do',       _rx(r'sơ\s+đồ'), True),
    ],
    'CONCEPT_MAP': [
        # a concept map needs typed relations; there is no single cue for it. It is
        # detected compositionally in detect_lesson(), never by a cue of its own.
    ],
    'QUANTITY': [
        ('don_vi',      _rx(r'đơn\s+vị\s+(?:đo|của)?'), False),
        ('num_unit',    re.compile(r'(?<![\wÀ-ỹ])\d+(?:[.,]\d+)?\s*'
                                   r'(?:cm|mm|dm|km|m|kg|g|mg|tấn|tạ|yến|ml|lít|l|'
                                   r'giây|phút|giờ|°c|°|%|n|j|w|v|a|mol|hz)'
                                   r'(?![\wÀ-ỹ])'), False),
        ('cong_thuc',   _rx(r'công\s+thức', r'phương\s+trình'), False),
    ],
    'SPATIAL': [
        ('ban_do',      _rx(r'bản\s+đồ', r'lược\s+đồ', r'sơ\s+đồ\s+(?:khu|vùng|đường)'), False),
        ('vi_tri_dia',  _rx(r'vị\s+trí\s+địa\s+lí', r'tiếp\s+giáp', r'phía\s+(?:bắc|nam|đông|tây)',
                            r'toạ\s+độ', r'tọa\s+độ'), False),
    ],
    'DEFINITION': [
        ('goi_la',      _rx(r'(?:được\s+)?gọi\s+là', r'còn\s+gọi\s+là'), False),
        ('la_gi',       _rx(r'là\s+gì'), False),
        ('khai_niem',   _rx(r'khái\s+niệm', r'định\s+nghĩa', r'thuật\s+ngữ'), False),
    ],
}

STRONG_CUES = {fam: {name for name, _, weak in cues if not weak} for fam, cues in CUES.items()}

# ---------------------------------------------------------------------------
# 5. DOMAIN EXTENSIONS — hypotheses to be proved or refused by the census.
#    An extension is only "necessary" if lessons exist that a CORE family cannot
#    express *and* the extension names a node/edge the core lacks.
# ---------------------------------------------------------------------------
EXTENSIONS = {
    'MATH_AST':      {'adds': ['Expression', 'Operator'], 'cue_family': 'QUANTITY',
                      'test': 'lessons whose teaching object is an expression, not a sentence'},
    'PHYS_QUANTITY': {'adds': ['Unit', 'Symbol'], 'cue_family': 'QUANTITY',
                      'test': 'lessons that state a quantity with a unit and a symbol'},
    'CHEM_REACTION': {'adds': ['Species', 'Reaction'], 'cue_family': 'QUANTITY',
                      'test': 'lessons containing a chemical formula or an arrow reaction'},
    'HIST_EVENT':    {'adds': ['role tag on Entity: person/dynasty'], 'cue_family': 'TIMELINE',
                      'test': 'lessons with >=2 dated events (Event already core)'},
    'GEO_SPATIAL':   {'adds': ['Region', 'boundary'], 'cue_family': 'SPATIAL',
                      'test': 'lessons whose object is a map region'},
    'SCI_PROCESS':   {'adds': ['Observation', 'Hypothesis'], 'cue_family': 'PROCESS',
                      'test': 'lessons with a prepare/do/observe/conclude arc'},
    'LIT_TEXT':      {'adds': ['Character', 'Theme', 'Attribution', 'Line', 'Stanza'],
                      'cue_family': None,
                      'test': 'lessons whose object is a literary text with speakers/verse'},
}

CHEM_RX = re.compile(r'(?:[A-Z][a-z]?\d*){2,}\s*(?:->|→|\+)|\b(?:H2O|CO2|O2|NaCl|H2SO4|CaCO3)\b')
MATH_EXPR_RX = re.compile(r'\d+\s*[/:×x*+\-=]\s*\d+|\b[a-z]\s*=\s*[-\d]|\bx\s*[+\-]\s*\d')
UNIT_SYMBOL_RX = re.compile(r'\b(?:kí\s+hiệu|ký\s+hiệu)\b|\([A-Za-zΩμ°]{1,3}\)')
VERSE_RX = re.compile(r'(?:khổ\s+thơ|bài\s+thơ|dòng\s+thơ|câu\s+thơ|vần|nhịp)')
DIALOG_RX = re.compile(r'^\s*[-–—]\s*[A-ZÀ-Ỹ]|nhân\s+vật|lời\s+thoại|đối\s+thoại')


def cue_hits(text_norm, family):
    """[(cue_name, start, end, weak)] for one normalised text and one family."""
    out = []
    for name, rx, weak in CUES.get(family, ()):
        for m in rx.finditer(text_norm):
            out.append((name, m.start(), m.end(), weak))
    return out
