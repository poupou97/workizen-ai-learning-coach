#!/usr/bin/env python3
"""Round 5 · measuring a text repair against the gold text - precision, recall and **false correction**.

The gold pages carry human-verified verbatim text for 679 of their 759 blocks. That is the truth this lane
is scored against, and the three numbers are defined here once so that nothing can quietly redefine them:

* **detection recall** - of the in-scope wrong tokens (a token whose gold and observed readings differ only
  in diacritics, i.e. the class this lane attacks), how many did the repairer *change to the gold form*.
* **repair precision** - of the tokens the repairer changed, how many now equal the gold form.
* **false-correction rate** - of the tokens the repairer changed, how many were **already correct** and are
  now wrong. This is the number the Founder called the one that matters most, and it is deliberately not
  folded into precision: a repair that turns a right word into a different wrong word and a repair that
  turns a wrong word into a different wrong word are not the same crime.

Tone *placement* (hoá/hóa, thuỷ/thủy) is normalised on both sides, exactly as `tc_score` does, so the two
valid Vietnamese orthographies are never counted as an error or as a repair.
"""
from __future__ import annotations

import difflib
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tc_score      # noqa: E402

from .vi import syllable   # noqa: E402

TOKEN = re.compile(r'[0-9A-Za-zÀ-ỹĂăÂâĐđÊêÔôƠơƯư]+')


def place(tok):
    return tc_score.norm_tone_placement(unicodedata.normalize('NFC', tok or '')).lower()


def toks(text):
    return TOKEN.findall(unicodedata.normalize('NFC', text or ''))


def _skel(t):
    return syllable.strip_quality(t).lower()


def align_tokens(gold_text, cand_text):
    """[(gold_tok, cand_tok)] over the region the two texts share. Aligned on the ASCII skeleton so a
    diacritic difference is *inside* an aligned pair rather than a mismatch, and a one-letter vowel
    substitution («phẫu»/«phễu») is aligned too."""
    g, c = toks(gold_text), toks(cand_text)
    gk, ck = [_skel(t) for t in g], [_skel(t) for t in c]
    out = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, gk, ck, autojunk=False).get_opcodes():
        if tag == 'equal':
            out += [(g[i1 + k], c[j1 + k]) for k in range(i2 - i1)]
        elif tag == 'replace' and (i2 - i1) == (j2 - j1):
            for k in range(i2 - i1):
                a, b = gk[i1 + k], ck[j1 + k]
                if len(a) == len(b) and sum(1 for x, y in zip(a, b) if x != y) == 1:
                    out.append((g[i1 + k], c[j1 + k]))
    return out


def in_scope_errors(gold_text, observed_text):
    """Aligned pairs where the observed reading differs from the gold only in diacritics/vowel quality -
    the class this lane attacks. Returns [(gold, observed, edit_kind)]."""
    out = []
    for gt, ot in align_tokens(gold_text, observed_text):
        if place(gt) == place(ot):
            continue
        k = syllable.edit_kind(ot, gt)
        if k in ('tone', 'quality'):
            out.append((gt, ot, k))
    return out


def block_clean(gold_text, cand_text, min_cover=0.8):
    """True when the candidate carries no diacritic error against the gold over an aligned region covering
    at least `min_cover` of the gold's tokens. This is the display-fidelity test used for restore precision
    and for the false-withheld count."""
    g = toks(gold_text)
    if not g:
        return None
    pairs = align_tokens(gold_text, cand_text)
    if len(pairs) < min_cover * len(g):
        return None                                  # not comparable: the block is spliced/split, not a spelling case
    return all(place(a) == place(b) for a, b in pairs)


class RepairScore:
    """Accumulates the three numbers plus their supporting counts."""

    def __init__(self):
        self.in_scope = 0          # wrong tokens of the class, present in the observation
        self.detected = 0          # …the repairer produced a candidate touching that token
        self.repaired_right = 0    # …and the new form equals the gold
        self.changed = 0           # tokens the repairer changed
        self.changed_right = 0
        self.false_correction = 0  # changed a token that was ALREADY correct into a wrong one
        self.changed_wrong_to_wrong = 0
        self.rows = []

    def add_block(self, gold_text, observed_text, repaired_text, block_id=None):
        if not gold_text:
            return
        errs = in_scope_errors(gold_text, observed_text)
        self.in_scope += len(errs)
        gold_by_obs = {}
        for gt, ot in align_tokens(gold_text, observed_text):
            gold_by_obs.setdefault(place(ot), []).append(gt)
        obs, rep = toks(observed_text), toks(repaired_text)
        if len(obs) != len(rep):
            return                                    # a repair never changes the token count; nothing to score
        gold_pairs = align_tokens(gold_text, observed_text)
        gold_for = {}
        oi = 0
        for gt, ot in gold_pairs:
            while oi < len(obs) and place(obs[oi]) != place(ot):
                oi += 1
            if oi < len(obs):
                gold_for[oi] = gt
                oi += 1
        for i, (o, r) in enumerate(zip(obs, rep)):
            if place(o) == place(r):
                continue
            self.changed += 1
            g = gold_for.get(i)
            if g is None:
                self.rows.append(dict(block=block_id, observed=o, repaired=r, gold=None, verdict='unknown'))
                continue
            was_right = place(o) == place(g)
            now_right = place(r) == place(g)
            if now_right:
                self.changed_right += 1
                self.repaired_right += 1
                verdict = 'repaired'
            elif was_right:
                self.false_correction += 1
                verdict = 'false_correction'
            else:
                self.changed_wrong_to_wrong += 1
                verdict = 'still_wrong'
            self.rows.append(dict(block=block_id, observed=o, repaired=r, gold=g, verdict=verdict))

    def summary(self):
        return dict(
            in_scope_errors=self.in_scope,
            tokens_changed=self.changed,
            repaired_to_gold=self.changed_right,
            false_corrections=self.false_correction,
            changed_wrong_to_wrong=self.changed_wrong_to_wrong,
            unknown_gold=sum(1 for r in self.rows if r['verdict'] == 'unknown'),
            repair_precision=(round(self.changed_right / self.changed, 4) if self.changed else None),
            false_correction_rate=(round(self.false_correction / self.changed, 4) if self.changed else None),
            detection_recall=(round(self.repaired_right / self.in_scope, 4) if self.in_scope else None),
        )


def wilson(k, n, z=1.96):
    if not n:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return (round((c - h) / d, 4), round((c + h) / d, 4))
