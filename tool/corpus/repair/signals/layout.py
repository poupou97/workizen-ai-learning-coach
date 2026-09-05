#!/usr/bin/env python3
"""Third signal **layer B** - source / layout / context constraints.

What the page itself constrains, independently of any lexicon:

* `B.verifier_reading` - the *other* stack's reading of this token. The two stacks share Apple Vision, so
  their **agreement** is worth little (round 4's falsified A26); but where they **disagree** the two readings
  are genuinely two different observations of the same ink, and the fact that a proposal equals one of them
  is source evidence, not lexical evidence.
* `B.closed_vocabulary` - a block whose role makes its text a closed set. An SGK stage label is one of
  «KHỞI ĐỘNG · KHÁM PHÁ · LUYỆN TẬP · VẬN DỤNG · THỰC HÀNH · MỤC TIÊU · EM CÓ BIẾT · GHI NHỚ …»; a caption
  label is «Hình/Bảng/Sơ đồ N». A token one edit from the closed entry, in a block of that role, is
  constrained by the layout, not guessed from frequency. (This is what makes «Quyện tập» → «Luyện tập»
  a deterministic repair rather than a statistical one.)
* `B.ocr_confidence` - Apple Vision's own confidence on the OCR line under the token. High confidence on a
  block *objects* to rewriting it; low confidence supports a repair.

Layer B abstains loudly and often: it is a constraint layer, not a generator.
"""
from __future__ import annotations

import re
import unicodedata

from .. import model, registry

#: closed vocabularies keyed by the pipeline role they constrain.
STAGE_WORDS = ('KHỞI ĐỘNG', 'KHÁM PHÁ', 'LUYỆN TẬP', 'VẬN DỤNG', 'THỰC HÀNH', 'MỤC TIÊU',
               'EM ĐÃ HỌC', 'EM CÓ THỂ', 'EM CÓ BIẾT', 'GHI NHỚ', 'LƯU Ý', 'CHÚ Ý', 'MỞ RỘNG',
               'KẾT NỐI', 'HOẠT ĐỘNG', 'CÂU HỎI VÀ BÀI TẬP', 'BÀI TẬP', 'TỰ ĐÁNH GIÁ',
               'TÌM HIỂU', 'THẢO LUẬN', 'ĐỌC HIỂU', 'VIẾT', 'NÓI VÀ NGHE', 'ÔN TẬP')
CAPTION_HEADS = ('HÌNH', 'BẢNG', 'SƠ ĐỒ', 'BIỂU ĐỒ', 'LƯỢC ĐỒ', 'TRANH', 'ẢNH')
CLOSED_BY_ROLE = {'stage_label': STAGE_WORDS, 'heading': STAGE_WORDS,
                  'caption': CAPTION_HEADS, 'sidebar': STAGE_WORDS}

OCR_CONF_HIGH = 0.98
OCR_CONF_LOW = 0.85


def _fold(s):
    d = unicodedata.normalize('NFD', (s or '').replace('đ', 'd').replace('Đ', 'D'))
    return re.sub(r'\s+', ' ', ''.join(c for c in d if unicodedata.category(c) != 'Mn')).strip().upper()


@registry.signal('B.verifier_reading')
def verifier_signal(candidate_token, verifier_token):
    """The proposal equals what the other stack read: source evidence from a genuinely different reading."""
    if not verifier_token:
        return model.Signal('B.verifier_reading', model.SignalVerdict.ABSTAINS, 0.0, dict())
    if unicodedata.normalize('NFC', candidate_token).lower() == unicodedata.normalize('NFC', verifier_token).lower():
        return model.Signal('B.verifier_reading', model.SignalVerdict.SUPPORTS, 0.6,
                            dict(verifier_token=verifier_token,
                                 note='the two stacks share Apple Vision; where they DISAGREE the two '
                                      'readings are two observations, and this proposal is one of them'))
    return model.Signal('B.verifier_reading', model.SignalVerdict.ABSTAINS, 0.0,
                        dict(verifier_token=verifier_token))


@registry.signal('B.closed_vocabulary')
def closed_vocabulary_signal(observed_text, proposed_text, role):
    """The block's role makes its text a closed set, and the proposal lands in it while the observation
    did not. Deterministic; no frequency involved."""
    vocab = CLOSED_BY_ROLE.get(role or '')
    if not vocab:
        return model.Signal('B.closed_vocabulary', model.SignalVerdict.ABSTAINS, 0.0, dict(role=role))
    obs_f, pro_f = _fold(observed_text), _fold(proposed_text)
    hit_obs = any(obs_f.startswith(v) or obs_f == v for v in vocab)
    hit_pro = any(pro_f.startswith(v) or pro_f == v for v in vocab)
    if hit_pro and not hit_obs:
        return model.Signal('B.closed_vocabulary', model.SignalVerdict.SUPPORTS, 1.0,
                            dict(role=role, matched=next(v for v in vocab if pro_f.startswith(v) or pro_f == v)))
    if hit_obs and not hit_pro:
        return model.Signal('B.closed_vocabulary', model.SignalVerdict.OBJECTS, 1.0,
                            dict(role=role, observed_is_in_vocabulary=True))
    return model.Signal('B.closed_vocabulary', model.SignalVerdict.ABSTAINS, 0.0, dict(role=role))


@registry.signal('B.ocr_confidence')
def ocr_confidence_signal(ocr_conf):
    """Apple Vision's line confidence under the block. Nothing to say on most K-12 pages (it returns 1.0
    almost everywhere) - which is itself a measured result and is why this sub-signal abstains so often."""
    if ocr_conf is None:
        return model.Signal('B.ocr_confidence', model.SignalVerdict.ABSTAINS, 0.0, dict())
    if ocr_conf <= OCR_CONF_LOW:
        return model.Signal('B.ocr_confidence', model.SignalVerdict.SUPPORTS, 0.4,
                            dict(ocr_conf=ocr_conf, note='low-confidence lines: a mis-read is plausible'))
    if ocr_conf >= OCR_CONF_HIGH:
        return model.Signal('B.ocr_confidence', model.SignalVerdict.ABSTAINS, 0.0,
                            dict(ocr_conf=ocr_conf, note='confident - but Apple Vision reports 1.0 on the '
                                                         'display-font blocks it gets wrong, so this is not '
                                                         'evidence against a repair'))
    return model.Signal('B.ocr_confidence', model.SignalVerdict.ABSTAINS, 0.0, dict(ocr_conf=ocr_conf))
