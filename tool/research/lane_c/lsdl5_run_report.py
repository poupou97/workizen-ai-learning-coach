#!/usr/bin/env python3
"""LANE C (round 4, §7 Golden Slice #2 gate) — report on the bounded TC-v2 run over LS&ĐL 5.

Reads (read-only) the versioned sandbox run under
  poc-out/round4/lane-c/tc2-lsdl5/<ver>/root/poc-out/trusted-corpus/tc-v2/tc2-p1/
(manifest, attach, sdm, lessons) plus the gold pages (tool/corpus/tc_gold) and the Lane C second
review (docs/research/lane-c/data/lsdl5-bai8-second-review.json), and writes
  <run>/report/run-report.json  +  <run>/report/run-report.md   (D4: anchors only, no page text)

Gate steps covered: 1 (run numbers), 2 (second review vs pipeline vs gold), 3 (header-vs-TOC for
all 28 lessons + a wide-regex probe of the missed headers), bridge determinism.
Nothing in tool/corpus is modified; the pipeline is imported only to hash two bridge runs.

    python3 tool/research/lane_c/lsdl5_run_report.py [--ver v1] [--copy-md docs/research/lane-c/data/lsdl5-run-report.md]
"""
import argparse
import glob
import json
import os
import re
import statistics
import sys
import unicodedata
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
MAIN = '/Users/alexnguyen/projects/workizen-ai-learning-coach'
BOOK = '05-sgk-lich-su-va-dia-li-5'
LESSON = 8
WIDE_HDR = re.compile(r'^\s*(B[ÀÁẢẠÃ]I|B[àáảạã]i)\s+(\d{1,2})\b')   # the pipeline regex lacks Ã/ã (BÃI = OCR tone slip)
FURNITURE = {'page_number', 'running_head', 'figure', 'empty', 'figure_text'}
ROLE_EQUIV = {'heading': {'heading', 'stage_label'}, 'stage_label': {'stage_label', 'heading'}}


def run_dir(ver):
    return f'{MAIN}/poc-out/round4/lane-c/tc2-lsdl5/{ver}'


def pipe_dir(ver):
    return f'{run_dir(ver)}/root/poc-out/trusted-corpus/tc-v2/tc2-p1'


def norm(s):
    s = unicodedata.normalize('NFD', (s or '').replace('đ', 'd').replace('Đ', 'D'))
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower()
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


def words(s, n):
    return ' '.join(norm(s).split()[:n])


def levenshtein(a, b):
    if a == b:
        return 0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def load_sdm(ver, page):
    p = f'{pipe_dir(ver)}/sdm/{BOOK}/p{page:03d}.sdm.json'
    return json.load(open(p)) if os.path.exists(p) else None


def match_block(anchor, sdm_blocks, used, my_role=None):
    """First SDM block (reading order) whose diacritics-insensitive text contains the anchor's first
    three words; for short label anchors (≤ 4 words) a fragment of the label also matches. Figure
    text / empty cells are candidates only when the reviewed block is itself a label or a table
    (a map label must never «match» a body paragraph)."""
    key = words(anchor, 3)
    if not key or anchor.startswith('['):
        return None
    short = len(norm(anchor).split()) <= 4
    allow_fig = my_role in ('box_label', 'table', 'figure_label')
    for ob in sdm_blocks:
        role = ob['role']['value']
        if ob['id'] in used or role == 'figure' or (role in ('figure_text', 'empty') and not allow_fig):
            continue
        t = norm(ob['text'] or '')
        if not t:
            continue
        if key in t or (short and len(t.split()) <= 4 and t in norm(anchor)):
            used.add(ob['id'])
            return ob
    return None


def order_inversions(pairs):
    """pairs: list of (my_order, sdm_order). Count pairs (i<j) whose SDM order is reversed."""
    inv = tot = 0
    for i in range(len(pairs)):
        for j in range(i + 1, len(pairs)):
            tot += 1
            if (pairs[i][0] - pairs[j][0]) * (pairs[i][1] - pairs[j][1]) < 0:
                inv += 1
    return inv, tot


# ---------------------------------------------------------------- step 1: run numbers
def step1(ver):
    m = json.load(open(f'{pipe_dir(ver)}/manifest.json'))
    att = json.load(open(f'{pipe_dir(ver)}/attach/{BOOK}.json'))
    lessons = []
    for f in sorted(glob.glob(f'{pipe_dir(ver)}/lessons/{BOOK}/bai-*.tsl.json')):
        t = json.load(open(f))
        b, s = t['boundary'], t['stats']
        lessons.append(dict(lesson=t['lesson'], title=t['title'], page_start=b['page_start'], page_end=b['page_end'], pages=len(b['pages']),
                            confidence=b['confidence'], source=b['source'], header_found=b['header_found'], sourceability=t['sourceability'],
                            learning=s['learning_blocks'], trusted=s['trusted'], withheld=s['withheld'], figures=s['figures'],
                            withheld_by_reason=s['withheld_by_reason'], roles_trusted=s['roles_trusted']))
    tot = dict(lessons_with_tsl=len(lessons), learning=sum(l['learning'] for l in lessons), trusted=sum(l['trusted'] for l in lessons),
               withheld=sum(l['withheld'] for l in lessons), figures=sum(l['figures'] for l in lessons),
               withheld_by_reason=dict(sum((Counter(l['withheld_by_reason']) for l in lessons), Counter())),
               roles_trusted=dict(sum((Counter(l['roles_trusted']) for l in lessons), Counter())))
    return dict(manifest=dict(git_sha=m.get('git_sha'), versions=m.get('versions'), docling_options=m.get('docling_options'), summary=m.get('summary'),
                              docling_artifacts=m.get('docling_artifacts')),
                attach_counts=att['counts'], lessons=lessons, totals=tot)


# ---------------------------------------------------------------- step 3: header vs TOC
def step3(ver):
    att = json.load(open(f'{pipe_dir(ver)}/attach/{BOOK}.json'))
    cs = json.load(open(f'{MAIN}/poc-out/graph/curriculum-structure.json'))
    meta = next(d for d in cs['documents'] if d['sourceDocumentId'] == BOOK)
    toc = {l['number']: l for l in meta['lessons']}
    off = att['counts']['printed_offset']
    by_page = {p['page']: p for p in att['pages']}
    headers = {l['number']: l for l in att['lessons'] if l['source'] in ('header', 'both')}
    # wide-regex probe over the OCR lines (research only — the pipeline's own regex is not changed here)
    wide = {}
    for fp in sorted(glob.glob(f'{MAIN}/poc-out/graph/ocr-body/{BOOK}/p*.json')):
        page = int(re.search(r'p(\d+)\.json', fp).group(1))
        lines = [l for l in json.load(open(fp))['lines'] if l['text'].strip()]
        if not lines or by_page.get(page, {}).get('kind') in ('toc', 'front_matter'):
            continue
        med = statistics.median(l['h'] for l in lines)
        for l in lines:
            m = WIDE_HDR.match(l['text'].strip())
            if m and l['y'] < 0.35 and l['h'] >= 1.25 * med and len(l['text'].strip()) <= 60:
                wide.setdefault(int(m.group(2)), page)
                break
    rows = []
    for n in range(1, meta['lessonCount'] + 1):
        h = headers.get(n)
        ts = toc.get(n, {}).get('pageStart')
        wp = wide.get(n)
        if h:
            agree = (ts is not None and h['page_printed'] is not None and abs(ts - h['page_printed']) <= 1)
            status = 'RESOLVED_HEADER_TOC_AGREE' if agree else ('RESOLVED_HEADER_ONLY' if ts is None else 'CONFLICT_HEADER_VS_TOC')
        elif wp is not None:
            status = 'WITHHELD_HEADER_MISSED_BY_REGEX'
        elif ts is not None:
            status = 'WITHHELD_TOC_ONLY'
        else:
            status = 'WITHHELD_NEITHER'
        rows.append(dict(lesson=n, header_pdf=h['page_pdf'] if h else None, header_printed=h['page_printed'] if h else None,
                         header_conf=h['confidence'] if h else None, header_form=h.get('form') if h else None, toc_page_start=ts,
                         toc_pdf=(ts + off) if ts is not None else None, wide_regex_header_pdf=wp, status=status,
                         header_title=h['title'] if h else None, toc_title=toc.get(n, {}).get('title')))
    # pages that would move if the wide-regex headers were used (naive sequence: last header ≤ page)
    seq = sorted((p, n) for n, p in wide.items())
    moved = []
    for p in sorted(by_page):
        rec = by_page[p]
        if rec['kind'] != 'page':
            continue
        cur = None
        for hp, n in seq:
            if hp <= p:
                cur = n
        if cur is not None and rec['lesson'] != cur:
            moved.append(dict(page=p, pipeline_lesson=rec['lesson'], wide_regex_lesson=cur))
    counts = Counter(r['status'] for r in rows)
    return dict(printed_offset=off, rows=rows, status_counts=dict(counts), wide_regex_headers_found=len(wide),
                pages_misattached_under_pipeline_regex=len(moved), pages_misattached=moved,
                bai8=dict(header_pdf=headers.get(LESSON, {}).get('page_pdf'), toc_page_start=toc[LESSON]['pageStart'], next_header_pdf=headers.get(LESSON + 1, {}).get('page_pdf'),
                          pages=[p for p in sorted(by_page) if by_page[p].get('lesson') == LESSON], pipeline_title=headers.get(LESSON, {}).get('title'), toc_title=toc[LESSON]['title']))


# ---------------------------------------------------------------- step 2: second review
def review_vs_pipeline(ver, review):
    out = {}
    for page_s, pg in review['pages'].items():
        page = int(page_s)
        sdm = load_sdm(ver, page)
        blocks = sdm['blocks']
        learning = [ob for ob in blocks if ob['role']['value'] not in FURNITURE and (ob['text'] or '').strip()]
        used = set()
        rows, pairs = [], []
        flex = {b for g in pg.get('flex_groups', []) for b in g}
        mine = [b for b in pg['blocks'] if b['role'] not in ('figure', 'page_number', 'table')]
        for b in mine:
            ob = match_block(b['anchor'], blocks, used, b['role'])
            accept = set(b.get('accept') or []) | ROLE_EQUIV.get(b['role'], set()) | {b['role']}
            if b['role'] == 'box_label':
                accept |= set(review['role_equivalence']['box_label'])
            row = dict(n=b['n'], my_role=b['role'], anchor=b['anchor'], found=ob is not None)
            if ob:
                row.update(sdm_id=ob['id'], sdm_order=ob['order'], sdm_role=ob['role']['value'], role_agree=ob['role']['value'] in accept,
                           trust=ob['trust']['status'], reasons=ob['trust']['reasons'],
                           anchor_verbatim=(ob['text'] or '').lstrip('·•-–—& ').startswith(b['anchor'].lstrip('–- ')))
                if str(b['n']) not in flex:
                    pairs.append((b['n'], ob['order']))
            rows.append(row)
        inv, tot = order_inversions(pairs)
        pipeline_only = [dict(order=ob['order'], role=ob['role']['value'], trust=ob['trust']['status'], first_words=' '.join((ob['text'] or '').split()[:3]))
                         for ob in learning if ob['id'] not in used]
        found = [r for r in rows if r['found']]
        out[page_s] = dict(my_learning_blocks=len(mine), found=len(found), role_agree=sum(1 for r in found if r['role_agree']),
                           trusted=sum(1 for r in found if r['trust'] == 'TRUSTED'), withheld=sum(1 for r in found if r['trust'] != 'TRUSTED'),
                           anchor_verbatim=sum(1 for r in found if r['anchor_verbatim']), order_inversions=inv, order_pairs=tot,
                           pipeline_learning_blocks=len(learning), pipeline_only_blocks=len(pipeline_only), pipeline_only=pipeline_only,
                           figures_mine=sum(1 for b in pg['blocks'] if b['role'] == 'figure'), figures_pipeline=len(sdm.get('figures', [])),
                           tables_mine=sum(1 for b in pg['blocks'] if b['role'] == 'table'), rows=rows,
                           page_features=sdm['features'])
    return out


def gold_vs_pipeline(ver, page):
    g = json.load(open(f'{REPO}/tool/corpus/tc_gold/{BOOK}-p{page:03d}.json'))
    sdm = load_sdm(ver, page)
    att = json.load(open(f'{pipe_dir(ver)}/attach/{BOOK}.json'))
    prec = next(p for p in att['pages'] if p['page'] == page)
    used = set()
    flex = {b for grp in g.get('flex_groups', []) for b in grp}
    rows, pairs = [], []
    for b in g['blocks']:
        if b['role'] in ('page_number', 'figure_label', 'diagram'):
            continue
        anchor = b.get('anchor') or (b.get('text') or '')
        ob = match_block(anchor, sdm['blocks'], used, b['role'])
        row = dict(id=b['id'], gold_role=b['role'], anchor=anchor, found=ob is not None)
        if ob:
            accept = ROLE_EQUIV.get(b['role'], set()) | {b['role']}
            row.update(sdm_order=ob['order'], sdm_role=ob['role']['value'], role_agree=ob['role']['value'] in accept, trust=ob['trust']['status'], reasons=ob['trust']['reasons'])
            if b.get('text'):
                row['text_exact'] = (ob['text'] or '') == b['text']
                row['char_diff'] = levenshtein(ob['text'] or '', b['text'])
                row['text_exact_dash_insensitive'] = re.sub(r'\s*[-–—]\s*', '-', ob['text'] or '') == re.sub(r'\s*[-–—]\s*', '-', b['text'])
            if b['id'] not in flex:
                pairs.append((b['order'], ob['order']))
        rows.append(row)
    inv, tot = order_inversions(pairs)
    found = [r for r in rows if r['found']]
    texted = [r for r in found if 'text_exact' in r]
    return dict(page=page, printed=g.get('printed_page'), gold_lesson=g['lesson']['number'], pipeline_lesson=prec['lesson'], pipeline_method=prec['method'],
                gold_blocks_scored=len(rows), found=len(found), role_agree=sum(1 for r in found if r['role_agree']),
                trusted=sum(1 for r in found if r['trust'] == 'TRUSTED'), text_blocks=len(texted), text_exact=sum(1 for r in texted if r['text_exact']),
                text_exact_dash_insensitive=sum(1 for r in texted if r['text_exact_dash_insensitive']), char_diff_total=sum(r['char_diff'] for r in texted),
                order_inversions=inv, order_pairs=tot, rows=rows)


# ---------------------------------------------------------------- Bài 8 detail + bridge determinism
def bai8_detail(ver):
    t = json.load(open(f'{pipe_dir(ver)}/lessons/{BOOK}/bai-{LESSON:02d}.tsl.json'))
    blocks = [dict(id=b['id'].split(':', 1)[1], page=b['page'], printed=b['page_printed'], order=b['order'], role=b['role']['value'], conf=b['role']['confidence'], method=b['role']['method'],
                   bbox=[round(v, 3) for v in b['bbox']], sim=b['provenance']['text_sim'], heading=(b['heading_path'] or ['-'])[-1][:30], first_words=' '.join(b['text'].split()[:4]))
              for b in t['blocks']]
    withheld = [dict(id=w['id'].split(':', 1)[1], page=w['page'], order=w['order'], role=w['role'], reasons=w['reasons'], status=w['status'], bbox=[round(v, 3) for v in w['bbox']], text_len=w['text_len'])
                for w in t['withheld']]
    figures = [dict(id=f['id'].split(':', 1)[1], page=f['page'], bbox=[round(v, 3) for v in f['bbox']], caption=(f['caption'] or '').split(':')[-1] or None, labels=f['labels'], area=round(f['bbox'][2] * f['bbox'][3], 4)) for f in t['figures']]
    per_page = {}
    for p in t['boundary']['pages']:
        tb = [b for b in t['blocks'] if b['page'] == p]
        wb = [w for w in t['withheld'] if w['page'] == p]
        per_page[p] = dict(trusted=len(tb), withheld=len(wb), roles_trusted=dict(Counter(b['role']['value'] for b in tb)), withheld_reasons=dict(Counter(r for w in wb for r in w['reasons'])))
    return dict(title=t['title'], boundary=t['boundary'], sourceability=t['sourceability'], stats=t['stats'], per_page=per_page, blocks=blocks, withheld=withheld, figures=figures)


def bridge_determinism(ver):
    os.environ['TC_ROOT'] = f'{run_dir(ver)}/root'
    sys.path.insert(0, os.path.join(REPO, 'tool', 'corpus'))
    import tsl_to_lesson_document as br  # noqa: E402  (read-only use of Lane A-pipeline's bridge)
    tsl = f'{pipe_dir(ver)}/lessons/{BOOK}/bai-{LESSON:02d}.tsl.json'
    hashes = []
    for k in ('a', 'b'):
        out = f'{run_dir(ver)}/report/determinism-{k}'
        path = br.build(tsl, out, crops=False)
        hashes.append(br.document_hash(json.load(open(path))))
    with_crops = f'{run_dir(ver)}/lesson-document/lesson-{BOOK}-b{LESSON}.json'
    doc = json.load(open(with_crops)) if os.path.exists(with_crops) else None
    return dict(no_crops_run_a=hashes[0], no_crops_run_b=hashes[1], identical=hashes[0] == hashes[1],
                with_crops_hash=br.document_hash(doc) if doc else None,
                with_crops_blocks=(dict(Counter(b['type'] for b in doc['blocks'])) if doc else None),
                with_crops_by_trust=(doc['provenance']['blockCounts']['byTrust'] if doc else None),
                semantic=[s['type'] for s in doc['semantic']] if doc else None, chapters=len(doc['chapters']) if doc else None, tutor_script=bool(doc.get('tutorScript')) if doc else None)


# ---------------------------------------------------------------- markdown
def md_report(r):
    L = []
    s1, s3, rv, det, b8 = r['step1'], r['step3'], r['step2'], r['bridge'], r['bai8']
    ms = s1['manifest']['summary']
    L.append(f"# LS&ĐL 5 — bounded TC-v2 run report (Lane C, round 4, run `{r['ver']}`)\n")
    L.append(f"Pipeline code unchanged (`tc2-p1`/`sdm-v2` at git `{(s1['manifest']['git_sha'] or '')[:7]}`; docling {s1['manifest']['versions'].get('docling')}, ocrmac {s1['manifest']['versions'].get('ocrmac')}); "
             f"sandbox root `poc-out/round4/lane-c/tc2-lsdl5/{r['ver']}/root` (inputs symlinked from the main checkout, outputs only there).\n")
    L.append(f"**Step 1 — run:** {ms['pages']} pages, docling ok {ms['docling_ok']} / error {ms['docling_error']}, xycut ok {ms['xycut_ok']}; "
             f"docling median {ms['docling_sec_median']} s, p90 {ms['docling_sec_p90']} s, total {ms['docling_sec_total']} s. "
             f"Attachment: canonical {s1['attach_counts']['canonical_lesson_count']}, TOC-ranged {s1['attach_counts']['toc_ranged']}, headers detected {s1['attach_counts']['header_detected']} "
             f"(TOC-confirmed {s1['attach_counts']['header_confirmed_by_toc']}, header-only {s1['attach_counts']['header_only']}), repaired-ranged {s1['attach_counts']['repaired_ranged']}, "
             f"pages with a lesson {s1['attach_counts']['pages_with_lesson']} / {s1['attach_counts']['pages']}. TSL: {s1['totals']['lessons_with_tsl']} lessons, learning blocks {s1['totals']['learning']} = trusted {s1['totals']['trusted']} + withheld {s1['totals']['withheld']}; figures {s1['totals']['figures']}; withheld by reason {s1['totals']['withheld_by_reason']}.\n")
    L.append('| Bài | PDF pages | n | conf | source | learning | trusted | withheld | figs | title (pipeline) |\n|---|---|---|---|---|---|---|---|---|---|')
    for l in s1['lessons']:
        L.append(f"| {l['lesson']} | {l['page_start']}–{l['page_end']} | {l['pages']} | {l['confidence']} | {l['source']} | {l['learning']} | {l['trusted']} | {l['withheld']} | {l['figures']} | {l['title']} |")
    L.append(f"\n**Bài 8 (TSL):** title `{b8['title']}` · boundary {b8['boundary']['page_start']}–{b8['boundary']['page_end']} conf {b8['boundary']['confidence']} source {b8['boundary']['source']} header_found {b8['boundary']['header_found']} · sourceability {b8['sourceability']} · "
             f"learning {b8['stats']['learning_blocks']} = trusted {b8['stats']['trusted']} + withheld {b8['stats']['withheld']} · withheld by reason {b8['stats']['withheld_by_reason']} · roles trusted {b8['stats']['roles_trusted']} · figures {b8['stats']['figures']}.\n")
    L.append('| PDF page | trusted | withheld | trusted roles | withheld reasons |\n|---|---|---|---|---|')
    for p, v in b8['per_page'].items():
        L.append(f"| {p} | {v['trusted']} | {v['withheld']} | {v['roles_trusted']} | {v['withheld_reasons']} |")
    L.append('\n| block | page | order | role | conf | method | bbox | heading | first words |\n|---|---|---|---|---|---|---|---|---|')
    for b in b8['blocks']:
        L.append(f"| {b['id']} | {b['page']} | {b['order']} | {b['role']} | {b['conf']:.2f} | {b['method']} | {b['bbox']} | {b['heading']} | {b['first_words']} |")
    L.append('\n| withheld | page | order | role | reasons | status | bbox | chars |\n|---|---|---|---|---|---|---|---|')
    for w in b8['withheld']:
        L.append(f"| {w['id']} | {w['page']} | {w['order']} | {w['role']} | {','.join(w['reasons'])} | {w['status']} | {w['bbox']} | {w['text_len']} |")
    L.append('\n| figure | page | bbox | area | caption block | labels |\n|---|---|---|---|---|---|')
    for f in b8['figures']:
        L.append(f"| {f['id']} | {f['page']} | {f['bbox']} | {f['area']} | {f['caption'] or '—'} | {f['labels']} |")
    L.append(f"\n**Bridge:** two no-crops runs identical = {det['identical']} (`{det['no_crops_run_a'][:12]}…`); with-crops document `{(det['with_crops_hash'] or '')[:12]}…` blocks {det['with_crops_blocks']} byTrust {det['with_crops_by_trust']} semantic {det['semantic']} chapters {det['chapters']} tutorScript {det['tutor_script']}.\n")
    L.append('## Step 2 — second review (Lane C reading the renders) vs pipeline, per Bài 8 page\n')
    L.append('| PDF page | my learning blocks | found by pipeline | role agree | trusted | withheld | anchor verbatim | order inversions / pairs | pipeline learning blocks | pipeline-only | figures mine / pipeline | page features |\n|---|---|---|---|---|---|---|---|---|---|---|---|')
    for p, v in rv['pages'].items():
        feats = [k for k, x in v['page_features'].items() if x]
        L.append(f"| {p} | {v['my_learning_blocks']} | {v['found']} | {v['role_agree']} | {v['trusted']} | {v['withheld']} | {v['anchor_verbatim']} | {v['order_inversions']} / {v['order_pairs']} | {v['pipeline_learning_blocks']} | {v['pipeline_only_blocks']} | {v['figures_mine']} / {v['figures_pipeline']} | {', '.join(feats)} |")
    tot = rv['totals']
    L.append(f"\nTotals over the 4 pages: my learning blocks {tot['my_learning_blocks']}, found {tot['found']}, role agree {tot['role_agree']}, trusted {tot['trusted']}, withheld {tot['withheld']}, anchor-verbatim {tot['anchor_verbatim']}, order inversions {tot['order_inversions']} / {tot['order_pairs']} pairs, pipeline-only fragments {tot['pipeline_only_blocks']}.\n")
    L.append('Role disagreements (my role → pipeline role):\n')
    for p, v in rv['pages'].items():
        for row in v['rows']:
            if row['found'] and not row['role_agree']:
                L.append(f"- p{p} #{row['n']} «{row['anchor']}»: {row['my_role']} → {row['sdm_role']} ({row['trust']}{', ' + ','.join(row['reasons']) if row['reasons'] else ''})")
            elif not row['found']:
                L.append(f"- p{p} #{row['n']} «{row['anchor']}»: {row['my_role']} → NOT FOUND as a text block")
    L.append('\n### Gold pages (second reviewer) — gold vs pipeline vs Lane C\n')
    L.append('| page | printed | gold lesson | pipeline lesson (method) | Lane C lesson | gold blocks scored | found | role agree | trusted | text blocks | exact | exact (dash-insensitive) | char diffs | order inv / pairs |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for gp, rev_key in ((rv['gold_p041'], 'gold_p041_review'), (rv['gold_p080'], 'gold_p080_review')):
        mine = r['review'][rev_key]['lesson_number_reviewed']
        L.append(f"| {gp['page']} | {gp['printed']} | {gp['gold_lesson']} | {gp['pipeline_lesson']} ({gp['pipeline_method']}) | {mine} | {gp['gold_blocks_scored']} | {gp['found']} | {gp['role_agree']} | {gp['trusted']} | {gp['text_blocks']} | {gp['text_exact']} | {gp['text_exact_dash_insensitive']} | {gp['char_diff_total']} | {gp['order_inversions']} / {gp['order_pairs']} |")
    for gp in (rv['gold_p041'], rv['gold_p080']):
        for row in gp['rows']:
            if row['found'] and (not row['role_agree'] or row.get('text_exact') is False):
                L.append(f"- p{gp['page']} {row['id']} «{row['anchor']}»: gold {row['gold_role']} → pipeline {row['sdm_role']} ({row['trust']}); text exact {row.get('text_exact')}, char diff {row.get('char_diff')}")
            elif not row['found']:
                L.append(f"- p{gp['page']} {row['id']} «{row['anchor']}»: gold {row['gold_role']} → NOT FOUND as a text block")
    L.append(f"\nGold agreement (Lane C vs gold annotator): p041 {len(r['review']['gold_p041_review']['blocks_agree'])} / 11 blocks agree, lesson number {r['review']['gold_p041_review']['lesson_number_gold']} → {r['review']['gold_p041_review']['lesson_number_reviewed']}; "
             f"p080 {len(r['review']['gold_p080_review']['blocks_agree'])} / 9 blocks agree, lesson number {r['review']['gold_p080_review']['lesson_number_gold']} → {r['review']['gold_p080_review']['lesson_number_reviewed']}.\n")
    L.append('## Step 3 — header vs TOC, all 28 lessons\n')
    L.append(f"Status counts: {s3['status_counts']}; wide-regex probe (adds `Ã/ã` to the pipeline's `B[ÀÁẢẠ]I` header regex) finds {s3['wide_regex_headers_found']} / 28 headers; "
             f"pages attached to the wrong lesson under the pipeline regex: {s3['pages_misattached_under_pipeline_regex']} / {s1['attach_counts']['pages']}.\n")
    L.append('| Bài | header PDF (printed) | conf | form | TOC printed → PDF | wide-regex header PDF | status | header title | TOC title |\n|---|---|---|---|---|---|---|---|---|')
    for row in s3['rows']:
        hp = f"{row['header_pdf']} ({row['header_printed']})" if row['header_pdf'] else '—'
        tp = f"{row['toc_page_start']} → {row['toc_pdf']}" if row['toc_page_start'] is not None else '—'
        L.append(f"| {row['lesson']} | {hp} | {row['header_conf'] if row['header_conf'] is not None else '—'} | {row['header_form'] or '—'} | {tp} | {row['wide_regex_header_pdf'] or '—'} | {row['status']} | {row['header_title'] or '—'} | {row['toc_title'] or '—'} |")
    L.append(f"\nBài 8: header PDF {s3['bai8']['header_pdf']} (TOC printed {s3['bai8']['toc_page_start']}), next header PDF {s3['bai8']['next_header_pdf']}, pages {s3['bai8']['pages']}; pipeline title `{s3['bai8']['pipeline_title']}` vs TOC title `{s3['bai8']['toc_title']}`.\n")
    return '\n'.join(L) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ver', default='v1')
    ap.add_argument('--copy-md', default=None)
    a = ap.parse_args()
    review = json.load(open(f'{REPO}/docs/research/lane-c/data/lsdl5-bai8-second-review.json'))
    pages = review_vs_pipeline(a.ver, review)
    keys = ('my_learning_blocks', 'found', 'role_agree', 'trusted', 'withheld', 'anchor_verbatim', 'order_inversions', 'order_pairs', 'pipeline_learning_blocks', 'pipeline_only_blocks')
    totals = {k: sum(v[k] for v in pages.values()) for k in keys}
    r = dict(ver=a.ver, step1=step1(a.ver), step3=step3(a.ver), bai8=bai8_detail(a.ver),
             step2=dict(pages=pages, totals=totals, gold_p041=gold_vs_pipeline(a.ver, 41), gold_p080=gold_vs_pipeline(a.ver, 80)),
             bridge=bridge_determinism(a.ver), review=dict(gold_p041_review=review['gold_p041_review'], gold_p080_review=review['gold_p080_review']))
    out = f'{run_dir(a.ver)}/report'
    os.makedirs(out, exist_ok=True)
    json.dump(r, open(f'{out}/run-report.json', 'w'), ensure_ascii=False, indent=1)
    md = md_report(r)
    open(f'{out}/run-report.md', 'w').write(md)
    if a.copy_md:
        open(os.path.join(REPO, a.copy_md), 'w').write(md)
    print(md)


if __name__ == '__main__':
    main()
