#!/usr/bin/env python3
"""Round 5 · Lane A4 — the external-verification POC. **Research only. Nothing is ever applied.**

    python3 tool/corpus/verify/run_external.py

This records the bounded lookups an agent actually performed on 2026-09-06, in the schema the Founder
required, and then shows what the engine does with them — which is *less* than a reader might expect, and
that is the point.

The lookups are typed in rather than fetched at runtime **on purpose**. A pipeline that reaches the
internet on its own is one configuration change away from being a production auto-rewrite path, and the
round's standing limits forbid that. What belongs in code is the *discipline*: `EvidenceRef` raises
without a URL and a retrieval timestamp, and `ExternalClaim` raises for a content class where reaching
outside is not defensible at all.

Three cases are recorded, and the third is the interesting one.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from verify import evalsets as es, external as EX, paths  # noqa: E402
from verify.trust import EvidenceRef  # noqa: E402

RETRIEVED = '2026-09-06T02:10:00+00:00'      # when the agent actually ran these searches


def claims():
    # ---- case A: a physical constant. The clearest case FOR external verification: the value is fixed by
    # international agreement, it is public, and it is checkable by anyone.
    a = EX.ExternalClaim(
        block_id='poc-A', span='3×10°', kind='stem_constant',
        question='Is «3×10° m/s» a physical constant, and what is the speed of light in vacuum?',
        proposed='3×10⁸',
        evidence=[
            EvidenceRef(kind='external_page', source='https://www.bipm.org/documents/20126/28433818/'
                                                     'working-document-ID-10850/'
                                                     '978c05bc-b4ce-adce-ba8b-8eb9bf48c509',
                        claim='The SI fixes c = 299 792 458 m/s exactly; it is one of the seven defining '
                              'constants of the SI.',
                        relation='supports', authority='official', retrieved_at=RETRIEVED,
                        detail=dict(publisher='BIPM', document='Concise summary of the SI')),
            EvidenceRef(kind='external_page', source='https://goldbook.iupac.org/terms/view/S05854',
                        claim='IUPAC Gold Book: speed of light in vacuum = 299 792 458 m s⁻¹.',
                        relation='supports', authority='reference', retrieved_at=RETRIEVED,
                        detail=dict(publisher='IUPAC')),
        ],
        note='«3×10⁸ m/s» is the value a Vietnamese school textbook prints as the rounded form. The '
             'external evidence establishes the ORDER OF MAGNITUDE, which is what makes «10°» nonsense; '
             'it does NOT establish what this page printed.')

    # ---- case B: a historical proper noun with a canonical spelling.
    b = EX.ExternalClaim(
        block_id='poc-B', span='Lý Thái Tô', kind='proper_noun_person',
        question='Is the founder of the Lý dynasty who moved the capital to Thăng Long in 1010 spelled '
                 '«Lý Thái Tổ» or «Lý Thái Tô»?',
        proposed='Lý Thái Tổ',
        evidence=[
            EvidenceRef(kind='external_page',
                        source='https://vi.wikipedia.org/wiki/Chi%E1%BA%BFu_d%E1%BB%9Di_%C4%91%C3%B4',
                        claim='«Chiếu dời đô» was issued by vua Lý Thái Tổ in the spring of 1010; the '
                              'name is written «Lý Thái Tổ» throughout.',
                        relation='supports', authority='secondary', retrieved_at=RETRIEVED,
                        detail=dict(publisher='Wikipedia tiếng Việt',
                                    caution='an encyclopaedia is secondary, not official')),
            EvidenceRef(kind='external_page',
                        source='https://vov2.vov.vn/van-hoa-giai-tri/'
                               'vua-ly-thai-to-va-quyet-dinh-doi-do-lich-su-55319.vov2',
                        claim='VOV (state broadcaster): «Vua Lý Thái Tổ» moved the capital from Hoa Lư '
                              'to Thăng Long in 1010.',
                        relation='supports', authority='official', retrieved_at=RETRIEVED,
                        detail=dict(publisher='Đài Tiếng nói Việt Nam')),
        ],
        note='Two independent hosts, one of them a state broadcaster. Note what this still does not do: '
             'it makes «Lý Thái Tô» implausible, it does not establish that page 41 of this book prints '
             '«Tổ». Cross-corpus does that better and cheaper — «thái tổ» 75× / «thái tô» 0×.')

    # ---- case D: the one that LOOKS like the best candidate for an external lookup and is not.
    # `ExternalClaim` refuses to be constructed for an orthography question, so this is caught rather
    # than argued about.
    d_refused = None
    try:
        EX.ExternalClaim(block_id='poc-D', span='Cộng hoa', kind='orthography_variant',
                         question='Is the official name «Cộng hoà» or «Cộng hòa»?')
    except ValueError as e:
        d_refused = str(e)
    return [a, b], d_refused


def main():
    made, refused = claims()
    store = EX.ExternalStore(f'{paths.OUT}/external-evidence.jsonl')
    for c in made:
        store.add(c)
    EX.install(store)

    report = dict(retrieved_at=RETRIEVED, claims=[c.to_json() for c in made],
                  refused_case_D=refused,
                  appropriateness={k: dict(zip(('appropriate', 'why'), EX.appropriate(k)))
                                   for k in EX.VERIFIABLE_KINDS + EX.SOURCE_BOUND_KINDS})
    with open(f'{paths.OUT}/external-report.json', 'w', encoding='utf-8') as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)

    print('=== EXTERNAL AUTHORITATIVE VERIFICATION (H.external) — research only ===')
    for c in made:
        print(f'\n{c.block_id} · {c.kind} · «{c.span}» → «{c.proposed}»')
        print(f'   question   : {c.question}')
        print(f'   sources    : {c.independent_sources()}')
        print(f'   authority  : {c.authorities()}')
        print(f'   confidence : {c._confidence()}  (capped at 0.75 — an external page is never proof '
              f'about a printed page)')
        for e in c.evidence:
            print(f'     [{e.relation}/{e.authority}] {e.source[:72]}')
            print(f'        retrieved {e.retrieved_at} · {e.claim[:96]}')
        print(f'   note       : {c.note}')

    print(f'\nCase D was REFUSED at construction:\n   {refused}')
    print('\nWhat the engine does with all of this: an H-layer Signal, and nothing else. '
          '`external_validator` returns `insufficient` for any candidate whose only support is layer H, '
          'and there is no apply() in the module.')


if __name__ == '__main__':
    main()
