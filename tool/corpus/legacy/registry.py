#!/usr/bin/env python3
"""Round 4 · Lane D — LEGACY REGISTRY: every legacy lesson in scope, with its original source, layout
family, risk classes and the OLD artefacts (pack activities, units, sam-units rows) hashed — status PENDING.

    python3 tool/corpus/legacy/registry.py                 # → poc-out/round4/legacy/registry.json (versioned, never overwritten)
    python3 tool/corpus/legacy/registry.py --print         # summary only

Scope (Founder §8): the 113 baseline lessons (poc-out/p0-experiment/baseline-learnable.json — 111 after the
WAL-210 G2/G3 gates; the registry keeps all 113 and marks the 2 non-canonical keys) ∪ every lesson that has
rows in assets/pack/sam-units.db (the grounding store: Toán 4–5, TV5 — 2,584 rows). Denominators (D5): the
registry states N in scope beside 3,679 canonical (historical) and 3,381 ranged; it never divides by them.

Per lesson: book · lesson · title · TOC pageStart / range (printed) · pdf pages actually carrying OLD units ·
pdf offset · original PDF path + sha256 (per book) · layout family per page (K-12 census export) · TC-v1 census
features (formula / table / side_by_side / diagram / color_heavy) · risk classes · OLD artefacts with sha256 ·
status PENDING. Risk classes are DERIVED from measured page features and the round-3 audit classes, never from
the old text itself being "read": toan · two_col · formula · attachment_suspect · order_suspect · figure_caption.
Nothing here decides trust; REPROCESSED ≠ TRUSTED.
"""
import argparse
import collections
import json
import os
import re
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402

REGISTRY_VERSION = 'legacy-registry-v1'
SAM_UNITS_BOOKS = ('04-sgk-toan-4-tap-mot', '04-sgk-toan-4-tap-hai', '05-sgk-toan-5-tap-mot', '05-sgk-toan-5-tap-hai', '05-sgk-tieng-viet-5-tap-mot', '05-sgk-tieng-viet-5-tap-hai')
PACK_META_KEYS = {'grade', 'version', 'subjects', 'books', 'buildProvenance'}
FRACTION = re.compile(r'\b\d{1,3}\s*/\s*\d{1,3}\b')


# ---------------------------------------------------------------- loaders
def load_curriculum(path=common.CURRICULUM):
    docs = common.load_json(path, {}).get('documents', [])
    return {d['sourceDocumentId']: d for d in docs}


def lesson_ranges(doc):
    """{lesson number: (pageStart, pageEnd)} in PRINTED pages from the TOC; end = next start − 1 (None when unranged)."""
    ls = sorted([l for l in doc.get('lessons', []) if l.get('number') is not None], key=lambda l: l['number'])
    starts = [(l['number'], l.get('pageStart')) for l in ls]
    out = {}
    for i, (n, s) in enumerate(starts):
        nxt = next((s2 for _, s2 in starts[i + 1:] if s2 is not None), None)
        out[n] = (s, (nxt - 1) if (s is not None and nxt is not None and nxt > s) else None)
    return out


def load_baseline(path=common.BASELINE_113):
    return [(b, int(l)) for b, l in common.load_json(path, [])]


def load_units(book, units_dir=common.UNITS):
    j = common.load_json(f'{units_dir}/{book}.json')
    if not j:
        return [], None
    return j.get('units', []), j.get('offset')


def load_sam_units_rows(db_path=common.SAM_UNITS_DB):
    """{(book, lesson): [(id, role, page, sha256(text))]} — text itself is not carried (D4); the hash is."""
    out = collections.defaultdict(list)
    if not os.path.exists(db_path):
        return out
    c = sqlite3.connect(db_path)
    for uid, book, lesson, role, page, text in c.execute('select id, book, lesson, role, page, text from unit order by id'):
        out[(book, int(lesson or 0))].append(dict(id=uid, role=role, page=page, sha256=common.sha256_text(text)))
    return out


def load_packs(pack_dir=common.PACK_DIR):
    packs = {}
    for g in range(1, 13):
        p = f'{pack_dir}/lesson-index-g{g}.json'
        j = common.load_json(p)
        if j:
            packs[g] = j
    return packs


def pack_activities(packs):
    """{(book, lesson): [activity records with family, sha256 of the canonical JSON, packVersion]} — the OLD
    served activities. Dict families (toanExercises) are keyed by lesson number with the book inside each entry."""
    out = collections.defaultdict(list)
    for g, pk in packs.items():
        prov = pk.get('buildProvenance') or {}
        pv = prov.get('packVersion'); ch = prov.get('contentHash')
        for fam, val in pk.items():
            if fam in PACK_META_KEYS:
                continue
            if isinstance(val, dict):
                for k, entries in val.items():
                    for e in entries if isinstance(entries, list) else [entries]:
                        b = e.get('book'); n = e.get('lesson', k)
                        try:
                            n = int(n)
                        except (TypeError, ValueError):
                            continue
                        if b:
                            out[(b, n)].append(dict(family=fam, grade=g, page=e.get('page') or e.get('pagePdf'), sha256=common.sha256_json(e), packVersion=pv, packContentHash=ch))
            elif isinstance(val, list):
                for e in val:
                    b = e.get('book'); n = e.get('lesson')
                    if b and n is not None:
                        out[(b, int(n))].append(dict(family=fam, grade=g, page=e.get('pagePdf') or e.get('page'), sha256=common.sha256_json(e), packVersion=pv, packContentHash=ch))
    return out


def load_layout_census(path=common.LAYOUT_CENSUS):
    return common.load_json(path, {})


def load_feature_census(books, path=common.FEATURE_CENSUS):
    """TC-v1 census rows for the given books only: {(book, pdf page): features}."""
    out = {}
    if not os.path.exists(path):
        return out
    want = set(books)
    with open(path, encoding='utf-8') as f:
        for line in f:
            j = json.loads(line)
            if j.get('book') in want:
                out[(j['book'], int(j['page']))] = dict(formula=bool(j.get('formula')), table=bool(j.get('table')), side_by_side=bool(j.get('side_by_side')), diagram=bool(j.get('diagram')),
                                                        color_heavy=bool(j.get('color_heavy')), figure=bool(j.get('figure')), columns=j.get('columns'))
    return out


# ---------------------------------------------------------------- derivations
def risk_classes(book, subject, pages_layout, features, units, toc_start, toc_end, unit_pages, last_lesson, has_toan_exercises):
    """Deterministic risk flags from page features + audit-measured mechanisms (never from reading the old text as truth)."""
    r = set()
    if subject == 'Toán':
        r.add('toan')
    if any(v == 'two_col' for v in pages_layout.values()):
        r.add('two_col')
    if any(f.get('side_by_side') for f in features.values()) or 'two_col' in r:
        r.add('order_suspect')
    if any(f.get('formula') for f in features.values()) or has_toan_exercises or any(FRACTION.search(u.get('text') or '') for u in units):
        r.add('formula')
    if any(f.get('diagram') or f.get('figure') for f in features.values()):
        r.add('figure_caption')
    if toc_start is None:
        r.add('attachment_suspect')            # unranged in the TOC → attached by neighbour
    if last_lesson:
        r.add('attachment_suspect')            # the audit found back covers attached to a book's last lesson
    if '-tieng-viet-5-' in book:
        r.add('attachment_suspect')            # measured +1…+3 pageStart offset in TV5
    if toc_end is not None and unit_pages and max(unit_pages) > toc_end + 1:
        r.add('attachment_suspect')            # old units extend past the TOC range (uncapped rule)
    if has_toan_exercises:
        r.add('geometry_rebuilt_expr')
    return sorted(r)


def build_registry(curr=None, baseline=None, sam_rows=None, packs=None, layout=None, feature_census=None, units_loader=load_units, pdf_hash=True):
    curr = curr if curr is not None else load_curriculum()
    baseline = baseline if baseline is not None else load_baseline()
    sam_rows = sam_rows if sam_rows is not None else load_sam_units_rows()
    packs = packs if packs is not None else load_packs()
    layout = layout if layout is not None else load_layout_census()
    acts = pack_activities(packs)
    scope = collections.OrderedDict()
    for b, n in baseline:
        scope[(b, n)] = {'in_113': True, 'in_sam_units': False}
    for (b, n) in sorted(sam_rows):
        if n == 0:
            continue
        scope.setdefault((b, n), {'in_113': False, 'in_sam_units': False})['in_sam_units'] = True
    books = sorted(set(b for b, _ in scope))
    feature_census = feature_census if feature_census is not None else load_feature_census(books)
    book_meta = {}
    units_by_book = {}
    for b in books:
        d = curr.get(b, {})
        units, off = units_loader(b)
        units_by_book[b] = (units, off)
        pdf = common.pdf_path(b)
        book_meta[b] = dict(book=b, label=common.book_label(b), subject=d.get('subject') or common.subject_of(b), grade=d.get('grade'), docType=d.get('docType'),
                            canonical=bool(d), lesson_count=d.get('lessonCount'), structure_status=d.get('structureStatus'),
                            pdf=pdf, pdf_sha256=(common.sha256_file(pdf) if (pdf and pdf_hash) else None), pdf_offset=off, ocr_pages=(len([f for f in os.listdir(f'{common.OCR}/{b}') if f.endswith('.json')]) if os.path.isdir(f'{common.OCR}/{b}') else 0),
                            old_extractors=sorted(set(((u.get('provenance') or {}).get('extraction') or 'unknown') for u in units)) if units else [])
    lessons = []
    for (b, n), flags in scope.items():
        d = curr.get(b, {})
        ranges = lesson_ranges(d) if d else {}
        canonical = n in ranges
        toc_start, toc_end = ranges.get(n, (None, None))
        title = next((l.get('title') for l in d.get('lessons', []) if l.get('number') == n), None)
        units, off = units_by_book[b]
        mine = [u for u in units if u.get('lesson') == n]
        unit_pages = sorted(set(u['pagePdf'] for u in mine if u.get('pagePdf')))
        off = off if off is not None else 1
        toc_pages = list(range(toc_start + off, (toc_end if toc_end is not None else toc_start) + off + 1)) if toc_start is not None else []
        pages = sorted(set(unit_pages) | set(toc_pages))
        lay = {p: (layout.get(b) or {}).get(str(p)) for p in pages}
        feats = {p: feature_census.get((b, p), {}) for p in pages}
        last = canonical and n == max(ranges) if ranges else False
        a = acts.get((b, n), [])
        srows = sam_rows.get((b, n), [])
        rec = dict(book=b, lesson=n, title=title, subject=book_meta[b]['subject'], grade=book_meta[b]['grade'], canonical=canonical,
                   toc_page_start=toc_start, toc_page_end=toc_end, pdf_offset=off, pages_pdf=pages, unit_pages_pdf=unit_pages, last_lesson_of_book=last,
                   layout_family=dict(collections.Counter(v or 'unknown' for v in lay.values())), layout_by_page={str(k): v for k, v in lay.items()},
                   features=dict(formula=sum(1 for f in feats.values() if f.get('formula')), table=sum(1 for f in feats.values() if f.get('table')), side_by_side=sum(1 for f in feats.values() if f.get('side_by_side')),
                                 diagram=sum(1 for f in feats.values() if f.get('diagram')), color_heavy=sum(1 for f in feats.values() if f.get('color_heavy')), pages_with_features=len([f for f in feats.values() if f])),
                   risk=risk_classes(b, book_meta[b]['subject'], lay, feats, mine, toc_start, toc_end, unit_pages, last, any(x['family'] == 'toanExercises' for x in a)),
                   in_113=flags['in_113'], in_sam_units=flags['in_sam_units'],
                   old=dict(pack_activities=a, pack_activity_count=len(a), pack_families=sorted(set(x['family'] for x in a)),
                            units=[dict(id=u['id'], role=u.get('role'), page_pdf=u.get('pagePdf'), sha256=common.sha256_text(u.get('text'))) for u in mine], unit_count=len(mine),
                            units_sha256=common.sha256_json([u.get('text') for u in mine]) if mine else None,
                            sam_units_rows=len(srows), sam_units_sha256=common.sha256_json([r['sha256'] for r in srows]) if srows else None),
                   status='PENDING', batch=None)
        lessons.append(rec)
    n_scope = len(lessons)
    summary = dict(in_scope=n_scope, in_113=sum(1 for l in lessons if l['in_113']), in_sam_units=sum(1 for l in lessons if l['in_sam_units']),
                   both=sum(1 for l in lessons if l['in_113'] and l['in_sam_units']), non_canonical=sum(1 for l in lessons if not l['canonical']),
                   unranged=sum(1 for l in lessons if l['toc_page_start'] is None), by_subject=dict(collections.Counter(l['subject'] for l in lessons)),
                   by_book=dict(collections.Counter(l['book'] for l in lessons)), risk=dict(collections.Counter(r for l in lessons for r in l['risk'])),
                   old_pack_activities=sum(l['old']['pack_activity_count'] for l in lessons), old_units=sum(l['old']['unit_count'] for l in lessons), old_sam_units_rows=sum(l['old']['sam_units_rows'] for l in lessons),
                   status=dict(collections.Counter(l['status'] for l in lessons)))
    reg = dict(version=REGISTRY_VERSION, generated_by='tool/corpus/legacy/registry.py',
               denominators=dict(common.DENOMINATORS, in_scope=dict(value=n_scope, definition='legacy lessons in Lane D scope = 113 baseline ∪ lessons with sam-units rows', census='this registry')),
               scope_definition='113 baseline (poc-out/p0-experiment/baseline-learnable.json) ∪ lessons with rows in assets/pack/sam-units.db',
               pack_versions=sorted(set(x['packVersion'] for l in lessons for x in l['old']['pack_activities'] if x.get('packVersion'))),
               books=book_meta, summary=summary, lessons=lessons)
    return reg


def print_summary(reg):
    s = reg['summary']
    print(f"in scope N = {s['in_scope']} (113-baseline {s['in_113']}, sam-units {s['in_sam_units']}, both {s['both']}; non-canonical {s['non_canonical']}, unranged {s['unranged']})")
    print('denominators:', {k: v['value'] for k, v in reg['denominators'].items()})
    print('by subject:', s['by_subject']); print('by book:', s['by_book']); print('risk:', s['risk'])
    print(f"OLD artefacts: pack activities {s['old_pack_activities']}, units {s['old_units']}, sam-units rows {s['old_sam_units_rows']}; pack versions {reg['pack_versions']}")
    print('status:', s['status'])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', default=f'{common.LEGACY_OUT}/registry.json')
    ap.add_argument('--print', action='store_true')
    ap.add_argument('--no-pdf-hash', action='store_true')
    a = ap.parse_args(argv)
    reg = build_registry(pdf_hash=not a.no_pdf_hash)
    print_summary(reg)
    if not a.print:
        p = common.write_new_version(reg, a.out)
        print('→', p)
    return 0


if __name__ == '__main__':
    sys.exit(main())
