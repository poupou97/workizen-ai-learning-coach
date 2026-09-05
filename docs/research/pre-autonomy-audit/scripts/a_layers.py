#!/usr/bin/env python3
"""Pre-autonomy audit — Layer A / S1: per-layer lesson counts, never merged.
BROWSABLE / SOURCE-ADDRESSABLE / TRUSTED / LEARNABLE / SAM-SUPPORTABLE / DEVICE-VALIDATED,
by grade x subject, with both denominators (3,679 canonical vs 3,381 ranged).
Reads only existing outputs. Writes data/layers.json + data/layers-by-grade-subject.md.
Run: python3 a_layers.py   (paths absolute)"""
import json, os, glob, collections, sqlite3
ROOT = '/Users/alexnguyen/projects/workizen-ai-learning-coach'
OUT = f'{ROOT}/poc-out/audit/pre-autonomy/data'
docs = json.load(open(f'{ROOT}/poc-out/graph/curriculum-structure.json'))['documents']
toc_fresh = {r['sourceDocumentId']: r for r in json.load(open(f'{OUT}/toc-health-fresh.json'))}

# ---- corpus facts (MEASURED here) ----
ocr_pages = {b: len(glob.glob(f'{ROOT}/poc-out/graph/ocr-body/{b}/p*.json')) for b in os.listdir(f'{ROOT}/poc-out/graph/ocr-body')}
by_doctype = collections.Counter(d['docType'] for d in docs)
sgk = [d for d in docs if d['docType'] == 'SGK']
canonical = sum(len(d.get('lessons', [])) for d in sgk)
ranged_tc = sum(1 for d in sgk for l in d.get('lessons', []) if l.get('pageStart'))              # TC definition
ranged_num = sum(1 for d in sgk for l in d.get('lessons', []) if l.get('pageStart') is not None and l.get('number') is not None)
sgk_pages = sum(ocr_pages.get(d['sourceDocumentId'], 0) for d in sgk)
sgk_with_ocr = sum(1 for d in sgk if ocr_pages.get(d['sourceDocumentId'], 0) > 0)
units_k12 = {os.path.basename(p)[:-5] for p in glob.glob(f'{ROOT}/poc-out/units-k12/*.json')}

# ---- packs on disk ----
packs = {g: json.load(open(f'{ROOT}/assets/pack/lesson-index-g{g}.json')) for g in range(1, 13)}
compiled = set(); shelf_books = set(); act_base = collections.defaultdict(set); act_router = collections.defaultdict(set)
for g, p in packs.items():
    for subj, bl in p['subjects'].items():
        for b in bl:
            for l in b['lessons']:
                compiled.add((b['sourceDocumentId'], l['no']))
    for b in p['books']:
        shelf_books.add(b['sourceDocumentId'])
    for e in p['khoaExperiments']:
        if e.get('lesson') is not None:
            act_base[(e['book'], e['lesson'])].add('EXPERIMENT')
    for e in p['suSources']:
        if e.get('lesson') is not None:
            act_base[(e['book'], e['lesson'])].add('SOURCE')
    for k, tag in (('tvReadings', 'READING'), ('tvWritings', 'WRITING')):
        for e in p[k]:
            key = (e['book'], e['lesson'])
            if str(e.get('source', '')).startswith('pattern-router'):
                act_router[key].add(tag + '@' + e['source'])
            else:
                act_base[key].add(tag)
    for les, lst in p['toanExercises'].items():
        for e in lst:
            act_base[(e['book'], int(les))].add('TOAN_EXERCISE')
    for e in p['diaMaps']:
        act_base[(e['book'], None)].add('MAP')   # diaMaps carry no lesson number

baseline = {tuple(x) for x in json.load(open(f'{ROOT}/poc-out/p0-experiment/baseline-learnable.json'))}
device_valid = {tuple(x) for x in json.load(open(f'{ROOT}/poc-out/p0-experiment/device-valid-lessons.json'))}
content_valid_variant = {tuple(x) for x in json.load(open(f'{ROOT}/poc-out/p0-experiment/content-valid-variant.json'))}
content_valid_exact = {tuple(x) for x in json.load(open(f'{ROOT}/poc-out/p0-experiment/content-valid-exact.json'))}

# ---- TSL (tc-v2) ----
tsl = collections.defaultdict(dict)
for f in glob.glob(f'{ROOT}/poc-out/trusted-corpus/tc-v2/tc2-p1/lessons/*/*.tsl.json'):
    d = json.load(open(f)); tsl[d['book']][d['lesson']] = d['sourceability']
tsl_count = sum(len(v) for v in tsl.values())
tsl_full = sum(1 for v in tsl.values() for s in v.values() if s == 'FULL')

# ---- baseline 113 vs on-disk pack ----
base_in_pack = {k for k in baseline if act_base.get(k)}
base_missing = sorted(baseline - base_in_pack)
router_lessons = set(act_router)
sam_supportable_units = set()
con = sqlite3.connect(f'{ROOT}/assets/pack/sam-units.db')
for book, les in con.execute('select distinct book, lesson from unit where lesson is not null'):
    sam_supportable_units.add((book, les))
n_units = con.execute('select count(*) from unit').fetchone()[0]

# ---- per grade x subject ----
rows = {}
book_meta = {d['sourceDocumentId']: d for d in sgk}
def key_of(b):
    d = book_meta.get(b)
    return (d['grade'], d['subject']) if d else None
for d in sgk:
    k = (d['grade'], d['subject']); r = rows.setdefault(k, collections.Counter()); r['books'] += 1
    r['pages_ocr'] += ocr_pages.get(d['sourceDocumentId'], 0)
    r['canonical'] += len(d.get('lessons', []))
    r['ranged'] += sum(1 for l in d.get('lessons', []) if l.get('pageStart'))
    fl = toc_fresh.get(d['sourceDocumentId'], {}).get('flags', [])
    r['toc_ok'] += fl == ['OK']; r['toc_notoc'] += ('NO_TOC' in fl or 'NO_PAGES' in fl)
    r['units_k12'] += d['sourceDocumentId'] in units_k12
    r['on_shelf'] += d['sourceDocumentId'] in shelf_books
    r['tsl'] += len(tsl.get(d['sourceDocumentId'], {}))
    r['tsl_full'] += sum(1 for s in tsl.get(d['sourceDocumentId'], {}).values() if s == 'FULL')
def bump(keys, col):
    for k in keys:
        kk = key_of(k[0])
        if kk and (k[1] is not None):
            rows[kk][col] += 1
bump(compiled, 'compiled'); bump(act_base, 'wired_base'); bump(act_router, 'wired_router'); bump(baseline, 'learnable_113')
bump(device_valid, 'device_valid'); bump(content_valid_variant, 'content_valid_variant'); bump(sam_supportable_units, 'sam_units_lessons')

cols = ['books', 'pages_ocr', 'canonical', 'ranged', 'toc_ok', 'toc_notoc', 'units_k12', 'compiled', 'on_shelf', 'sam_units_lessons', 'wired_base', 'learnable_113', 'wired_router', 'content_valid_variant', 'device_valid', 'tsl', 'tsl_full']
md = ['# Layers by grade x subject (MEASURED by scripts/a_layers.py, 2026-09-05)', '',
      f'Denominators: canonical = SGK lessons in curriculum-structure.json ({canonical:,}); ranged = with pageStart ({ranged_tc:,}). Never collapse.', '',
      'Columns: compiled = lesson listed in the on-disk lesson-index pack; sam_units_lessons = lessons with content units in assets/pack/sam-units.db (FTS grounding only, no activity); wired_base = lessons with a NON-router activity in the on-disk pack; learnable_113 = baseline-learnable.json; wired_router = lessons with a pattern-router (experiment) activity present in the on-disk pack; content_valid_variant = WAL-206 variant gate pass; device_valid = hand-walked (6, variant build); tsl = TC-v2 Trusted Structured Lessons (repaired ranges, NOT canonical).', '',
      '| grade | subject | ' + ' | '.join(cols) + ' |', '|' + '---|' * (len(cols) + 2)]
for (g, s), r in sorted(rows.items()):
    md.append(f'| {g} | {s} | ' + ' | '.join(str(r.get(c, 0)) for c in cols) + ' |')
tot = collections.Counter()
for r in rows.values():
    tot.update(r)
md.append('| **all** | | ' + ' | '.join(str(tot.get(c, 0)) for c in cols) + ' |')
open(f'{OUT}/layers-by-grade-subject.md', 'w').write('\n'.join(md) + '\n')

act_any = {k for k in list(act_base) + list(act_router) if k[1] is not None}
out = dict(
    generated='2026-09-05', script='poc-out/audit/pre-autonomy/scripts/a_layers.py',
    corpus=dict(documents=len(docs), by_doctype=dict(by_doctype), ocr_pages_total=sum(ocr_pages.values()), ocr_books=len(ocr_pages),
                sgk_documents=len(sgk), sgk_with_ocr=sgk_with_ocr, sgk_pages=sgk_pages, units_k12_books=len(units_k12)),
    denominators=dict(canonical=canonical, ranged_tc_definition=ranged_tc, ranged_number_and_pageStart=ranged_num),
    layers=dict(
        BROWSABLE=dict(definition='SGK lesson listed in a compiled on-disk lesson-index pack (book has OCR text; lesson row exists)', count=len(compiled), denominator='canonical 3,679', books_on_shelf=len(shelf_books)),
        SOURCE_ADDRESSABLE=dict(definition='SGK lesson with a pageStart in curriculum-structure.json', count=ranged_tc, denominator='canonical 3,679'),
        SAM_SUPPORTABLE_units=dict(definition='lesson with >=1 content unit in assets/pack/sam-units.db (FTS grounding only; NOT an activity)', count=len(sam_supportable_units), units=n_units, books=sorted({b for b, _ in sam_supportable_units})),
        SAM_SUPPORTABLE_activity=dict(definition='lesson with >=1 Surface-consumable activity in on-disk pack, any source (router included)', count=len(act_any)),
        LEARNABLE_baseline=dict(definition='baseline-learnable.json (113 proven, WAL-204/206 regression oracle)', count=len(baseline), still_wired_non_router_in_pack=len(base_in_pack), missing_from_pack=base_missing),
        LEARNABLE_router_present_on_disk=dict(definition='lessons whose ONLY wiring is a pattern-router activity present in the on-disk pack (experiment build ROUTE_EXPLAIN=1, NOT default)', count=len(router_lessons - {k for k in act_base if k[1] is not None}), router_lessons_total=len(router_lessons), router_entries=sum(len(v) for v in act_router.values())),
        CONTENT_VALID_variant=dict(count=len(content_valid_variant), new_vs_baseline=len(content_valid_variant - baseline)),
        CONTENT_VALID_exact=dict(count=len(content_valid_exact), new_vs_baseline=len(content_valid_exact - baseline)),
        TRUSTED_TSL=dict(definition='TC-v2 Trusted Structured Lesson documents (six Science books, repaired ranges)', count=tsl_count, full=tsl_full, partial=tsl_count - tsl_full, per_book={b: len(v) for b, v in sorted(tsl.items())}, denominator='238 repaired ranged (six books); six-book canonical 207; six-book old ranged 194'),
        DEVICE_VALIDATED=dict(definition='hand-walked on Nokia, WAL-206 variant build (device-valid-lessons.json)', count=len(device_valid), lessons=sorted(device_valid), in_baseline=len(device_valid & baseline)),
    ),
    by_grade_subject={f'{g}|{s}': dict(r) for (g, s), r in sorted(rows.items())},
)
json.dump(out, open(f'{OUT}/layers.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in out.items() if k != 'by_grade_subject'}, ensure_ascii=False, indent=1))
