#!/usr/bin/env python3
"""Round 5 · Vietnamese orthography: what a syllable may look like, and what a mis-read one may have been.

Two jobs, deliberately separated because they carry very different risk:

* **legality** - deterministic, zero data, zero licence: a Vietnamese syllable carries **at most one tone
  mark**, the tone mark sits on a vowel, and the onset is one of the 28 initial consonant spellings. This
  is phonology, not statistics, and it is what catches the «thủỷ» class (two hooks in one syllable) that no
  amount of OCR agreement can catch.
* **candidate generation** - the set of forms an observed token *might* have been: its six tone variants,
  and one-position substitutions inside a vowel-quality family (a/ă/â, e/ê, o/ô/ơ, u/ư, i/y, plus the
  â↔ê pair Apple Vision actually confuses: «phẫu» for «phễu»). Generation is cheap and wide; deciding is
  the lexicon's and the validator's job, never this module's.

Nothing here decides anything. `is_legal` returning False is a *detection*; it is never a repair.
"""
from __future__ import annotations

import re
import unicodedata

TONE_MARKS = {'̀': 'grave', '́': 'acute', '̃': 'tilde', '̉': 'hook', '̣': 'dot'}
TONES = ('', '̀', '́', '̃', '̉', '̣')   # '' = ngang (level)
QUALITY_MARKS = {'̂', '̆', '̛'}                    # circumflex, breve, horn
VOWELS = set('aăâeêioôơuưy')

#: the 28 initial consonant spellings of Vietnamese (plus the empty onset), longest first.
ONSETS = ('ngh', 'ng', 'nh', 'ch', 'gh', 'gi', 'kh', 'ph', 'qu', 'th', 'tr',
          'b', 'c', 'd', 'đ', 'g', 'h', 'k', 'l', 'm', 'n', 'p', 'r', 's', 't', 'v', 'x')

#: vowel-quality families for candidate generation. â↔ê and e↔â are included because the corpus's own
#: failure («phẫu» for «phễu», measured in round 4 §3) is exactly that substitution.
QUALITY_FAMILY = {
    'a': 'aăâ', 'ă': 'aăâ', 'â': 'aăâê',
    'e': 'eêâ', 'ê': 'eêâ',
    'o': 'oôơ', 'ô': 'oôơ', 'ơ': 'oôơ',
    'u': 'uư', 'ư': 'uư',
    'i': 'iy', 'y': 'iy',
}

WORD = re.compile(r'^[A-Za-zÀ-ỹĂăÂâĐđÊêÔôƠơƯư]+$')


def nfc(s):
    return unicodedata.normalize('NFC', s or '')


def nfd(s):
    return unicodedata.normalize('NFD', s or '')


def tone_count(token):
    """How many TONE marks the token carries. >1 is illegal in Vietnamese, full stop."""
    return sum(1 for c in nfd(token) if c in TONE_MARKS)


def tone_of(token):
    for c in nfd(token):
        if c in TONE_MARKS:
            return c
    return ''


def strip_tone(token):
    return nfc(''.join(c for c in nfd(token) if c not in TONE_MARKS))


def strip_quality(token):
    """Remove tone AND quality marks, and fold đ→d: the ASCII skeleton used to compare two readings."""
    d = nfd(token.replace('đ', 'd').replace('Đ', 'D'))
    return ''.join(c for c in d if unicodedata.category(c) != 'Mn')


def onset_of(token):
    t = strip_tone(token).lower()
    for o in ONSETS:
        if t.startswith(o):
            # «gi» and «qu» are onsets only when a vowel follows; «gia» yes, «gi» alone no
            if o in ('gi', 'qu') and len(t) == len(o):
                continue
            return o
    return ''


def _tone_position_legal(token):
    """The tone mark must sit on a vowel letter (Apple Vision sometimes puts one on a consonant)."""
    for ch in nfd(token):
        pass
    base = None
    for ch in nfd(token):
        if unicodedata.category(ch) != 'Mn':
            base = ch
        elif ch in TONE_MARKS:
            if base is None or base.lower() not in VOWELS:
                return False
    return True


def has_vowel(token):
    return any(c.lower() in VOWELS for c in strip_tone(token))


def legality(token):
    """→ (ok, reasons[]). Deterministic; no corpus, no lexicon, no threshold."""
    reasons = []
    t = nfc(token)
    if not t or not WORD.match(t):
        return True, []                      # not a Vietnamese word token: layer A abstains, it does not object
    if tone_count(t) > 1:
        reasons.append('double_tone')
    if not _tone_position_legal(t):
        reasons.append('tone_on_consonant')
    if not has_vowel(t):
        if len(t) > 1 or t.lower() not in ('a', 'e', 'i', 'o', 'u', 'y'):
            reasons.append('no_vowel')
    if len(t) > 1 and not has_vowel(t):
        pass
    else:
        rest = strip_tone(t).lower()
        o = onset_of(t)
        if not o and rest and rest[0] not in VOWELS:
            reasons.append('illegal_onset')
    return (not reasons), reasons


def is_legal(token):
    return legality(token)[0]


# ---------------------------------------------------------------- candidate generation
def _with_tone(base_token, tone):
    """Put `tone` on the token's tone-bearing vowel, keeping the token's own tone position."""
    d = list(nfd(base_token))
    # find the index of the existing tone mark's base, or the conventional bearer
    out = []
    placed = False
    # position: reuse the original token's tone slot when it had one
    orig = nfd(base_token)
    slot = None
    for i, ch in enumerate(orig):
        if ch in TONE_MARKS:
            slot = i
            break
    stripped = [c for c in orig if c not in TONE_MARKS]
    if slot is None:
        # conventional placement: last vowel of the nucleus (good enough - a generated candidate that is
        # spelled unconventionally simply will not be attested, so it dies at the lexicon)
        idxs = [i for i, c in enumerate(stripped) if unicodedata.category(c) != 'Mn' and c.lower() in VOWELS]
        if not idxs:
            return None
        slot = idxs[-1] + 1
        while slot < len(stripped) and unicodedata.category(stripped[slot]) == 'Mn':
            slot += 1
    else:
        # `slot` indexes into orig; recompute against stripped
        pre = sum(1 for c in orig[:slot] if c not in TONE_MARKS)
        slot = pre
    if not tone:
        return nfc(''.join(stripped))
    out = stripped[:slot] + [tone] + stripped[slot:]
    return nfc(''.join(out))


def tone_variants(token):
    """The six tone readings of a token (the tone is the only thing that changes)."""
    base = strip_tone(token)
    out = []
    for t in TONES:
        v = _with_tone(token, t)
        if v:
            out.append(v)
    seen = set(); res = []
    for v in out:
        if v not in seen:
            seen.add(v); res.append(v)
    if base not in seen:
        res.append(base)
    return res


def quality_variants(token):
    """One-position substitutions inside a vowel-quality family, each then re-toned. Bounded: at most one
    vowel letter changes, so «phẫu» reaches «phễu» but not «phiếu»."""
    t = nfc(token)
    stripped = strip_tone(t)
    tone = tone_of(t)
    out = []
    for i, ch in enumerate(stripped):
        fam = QUALITY_FAMILY.get(ch.lower())
        if not fam:
            continue
        for alt in fam:
            if alt == ch.lower():
                continue
            alt = alt.upper() if ch.isupper() else alt
            cand_base = stripped[:i] + alt + stripped[i + 1:]
            for tv in TONES:
                v = _with_tone(_with_tone(cand_base, '') or cand_base, tv)
                if v:
                    out.append(v)
    seen = set(); res = []
    for v in out:
        if v not in seen and v != t:
            seen.add(v); res.append(v)
    return res


def detone_variants(token):
    """For a token carrying MORE THAN ONE tone mark - «thủỷ», «lượng̣» - the forms obtained by deleting
    exactly one of them. This is the *minimal legal repair* of an illegal spelling and is deterministic:
    it never invents a tone, it only removes one Apple Vision added. It matters because the general
    candidate set would also offer the tone-less form («thuy»), which the corpus - full of the same OCR
    slip - can prefer."""
    d = nfd(nfc(token))
    marks = [i for i, c in enumerate(d) if c in TONE_MARKS]
    if len(marks) < 2:
        return []
    out = []
    for i in marks:
        out.append(nfc(''.join(c for k, c in enumerate(d) if k != i)))
    seen, res = set(), []
    for v in out:
        if v not in seen:
            seen.add(v); res.append(v)
    return res


def candidates(token, include_quality=True):
    """Everything the token might have been, most conservative first: its own tone family, then a single
    vowel-quality substitution. Order matters - the repairer prefers the smallest edit that the evidence
    supports."""
    out = [v for v in tone_variants(token) if v != nfc(token)]
    if include_quality:
        out += quality_variants(token)
    seen = set(); res = []
    for v in out:
        if v not in seen:
            seen.add(v); res.append(v)
    return res


def edit_kind(observed, proposed):
    """'tone' | 'quality' | 'other' - how far the proposal is from what was observed."""
    a, b = nfc(observed), nfc(proposed)
    if a == b:
        return 'identical'
    if strip_tone(a).lower() == strip_tone(b).lower():
        return 'tone'
    if strip_quality(a).lower() == strip_quality(b).lower():
        return 'quality'
    if len(strip_quality(a)) == len(strip_quality(b)) and \
            sum(1 for x, y in zip(strip_quality(a).lower(), strip_quality(b).lower()) if x != y) == 1:
        return 'quality'
    return 'other'
