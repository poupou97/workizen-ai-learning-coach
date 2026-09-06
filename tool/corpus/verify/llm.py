#!/usr/bin/env python3
"""Round 5 · Lane A4 — signal **`G.llm_semantic`**: an LLM as a *verifier*, never as a source of truth.

Founder: *«LLM có thể được dùng như MỘT tín hiệu phụ … `c = 3×10° m/s` trong ngữ cảnh Vật lí có thể bị
flag và đề xuất `3×10⁸ m/s`. NHƯNG: LLM OUTPUT ≠ TRUTH.»*

Three rules, enforced in code rather than asserted in prose:

1. **The model may only emit an `AnomalySignal` or a `RepairCandidate`.** `verify()` returns those types
   and nothing else. There is no code path from a model's answer to a corpus value: the candidate goes
   into A1's engine and is validated by a signal from a *different* layer, exactly like a rule-generated
   one. `llm_validator` below refuses to validate a candidate whose only support is layer `G`.
2. **Everything the Founder listed is stored** — original observation · proposed correction · reason ·
   context supplied (verbatim, so a later reader can tell whether the model was misled by its prompt) ·
   model and version · confidence · supporting **and contradicting** evidence. The prompt asks for
   contradicting evidence explicitly, because a model that is never asked for the case against will never
   volunteer it.
3. **Offline only, and out of the app.** This reuses the proven harness pattern of
   `tool/shadow/run_shadow.py` — `claude -p … --output-format json` in a subprocess, responses cached on
   disk by prompt hash. The Flutter app has no network and no LLM and this lane adds neither; the round-5
   standing limits forbid wiring an LLM into the product, and nothing here is importable from `lib/`.

## Why detector and proposer are measured apart

A model reading `3×10° m/s` in a Physics lesson is far more reliable at saying *«that is not a physical
constant»* than at saying *«it must be 3×10⁸»*. Folding the two into one «accuracy» number hides the only
useful thing about the signal. So `verify()` returns a detection verdict and, separately, an optional
proposal, and `measure_llm.py` scores them in two different tables.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # tool/corpus

from repair import model, registry  # noqa: E402

from . import _registration as _reg  # noqa: E402
from . import paths  # noqa: E402
from .trust import AnomalySignal, EvidenceRef  # noqa: E402

SIGNAL_ID = 'G.llm_semantic'
VALIDATOR_ID = 'llm.independent-support-v1'
FC_TONE = 'vi_tone_disagreement'
DEFAULT_MODEL = 'haiku'
PROMPT_VERSION = 'a4-verify-v1'


# --------------------------------------------------------------------------- the prompt
PROMPT = """Bạn là một người soát bản in sách giáo khoa Việt Nam. Bạn KHÔNG viết lại văn bản.

Nhiệm vụ: đọc một khối văn bản do OCR tạo ra và cho biết có chỗ nào SAI so với sách in hay không.

NGỮ CẢNH ĐƯỢC CUNG CẤP
- Môn học: {subject}
- Bài / mục: {lesson}
- Đường dẫn tiêu đề: {heading}
- Vai trò của khối: {role}

KHỐI VĂN BẢN CẦN SOÁT
<<<{text}>>>

QUY TẮC BẮT BUỘC
1. Chỉ báo lỗi khi bạn có LÝ DO cụ thể (sai chính tả tiếng Việt, sai dấu thanh làm đổi nghĩa, một hằng số
   vật lí/hoá học vô nghĩa, một tên riêng lịch sử viết sai, một đơn vị đo sai).
2. «hoà» và «hòa», «thuỷ» và «thủy» là HAI CÁCH VIẾT ĐỀU ĐÚNG. Không bao giờ báo lỗi vì lí do này.
3. Nếu bạn nghi ngờ nhưng KHÔNG biết chắc chữ đúng là gì, hãy báo anomaly và để "proposed" là null.
   Đoán bừa còn tệ hơn không đoán.
4. Bạn PHẢI liệt kê cả bằng chứng NGƯỢC LẠI (contradicting): lí do khiến văn bản hiện tại có thể ĐÚNG.
5. Chỉ trả về JSON, không giải thích thêm.

ĐỊNH DẠNG JSON
{{"findings": [{{"span": "<chuỗi đúng như trong văn bản>",
                "kind": "vi_tone|vi_spelling|stem_constant|unit|proper_noun|other",
                "severity": "teaching_critical|display",
                "reason": "<vì sao sai, bằng tiếng Việt, ngắn>",
                "proposed": "<chuỗi thay thế, hoặc null nếu không chắc>",
                "confidence": 0.0,
                "supporting": ["<bằng chứng ủng hộ việc nó SAI>"],
                "contradicting": ["<bằng chứng cho thấy nó có thể ĐÚNG>"]}}]}}

Nếu không có lỗi nào: {{"findings": []}}"""


# --------------------------------------------------------------------------- harness
class LLMVerifier:
    """`claude -p` in a subprocess, with an on-disk cache keyed by (prompt version, model, prompt).

    The cache is what makes the measurement reproducible and cheap to re-run: a scored row can be
    re-examined months later without paying for the call again, and a changed prompt gets a new key
    rather than silently reusing old answers.
    """

    def __init__(self, model_name=DEFAULT_MODEL, cache_dir=None, timeout=120, offline=False):
        self.model = model_name
        self.cache_dir = cache_dir or paths.LLM_CACHE
        self.timeout = timeout
        self.offline = offline          # True: only answer from cache; never spawn a subprocess
        self.stats = dict(hits=0, calls=0, errors=0, unparsable=0, seconds=0.0)
        os.makedirs(self.cache_dir, exist_ok=True)

    # ---- plumbing
    def _key(self, prompt):
        h = hashlib.sha256(f'{PROMPT_VERSION}|{self.model}|{prompt}'.encode()).hexdigest()[:24]
        return os.path.join(self.cache_dir, f'{h}.json')

    def _ask(self, prompt):
        path = self._key(prompt)
        if os.path.exists(path):
            self.stats['hits'] += 1
            with open(path, encoding='utf-8') as fh:
                return json.load(fh)
        if self.offline:
            return None
        t0 = time.time()
        try:
            r = subprocess.run(['claude', '-p', prompt, '--model', self.model,
                                '--output-format', 'json'],
                               capture_output=True, text=True, timeout=self.timeout)
        except Exception as e:
            self.stats['errors'] += 1
            return dict(error=str(e))
        rec = dict(model=self.model, prompt_version=PROMPT_VERSION, exit=r.returncode,
                   wall_seconds=round(time.time() - t0, 2), raw=r.stdout, stderr=r.stderr[-400:])
        self.stats['calls'] += 1
        self.stats['seconds'] += rec['wall_seconds']
        with open(path, 'w', encoding='utf-8') as fh:
            json.dump(rec, fh, ensure_ascii=False)
        return rec

    @staticmethod
    def _parse(rec):
        """`claude -p --output-format json` wraps the model's text in an envelope; the model's own answer
        is then JSON inside that. Both layers can fail, and a failure is recorded as a failure — never as
        «no findings», which would silently turn every parse error into a clean bill of health."""
        if not rec or rec.get('error') or rec.get('exit'):
            return None, 'call failed'
        try:
            env = json.loads(rec['raw'])
        except Exception:
            return None, 'envelope not JSON'
        text = env.get('result') if isinstance(env, dict) else None
        if not isinstance(text, str):
            return None, 'no result field'
        m = re.search(r'\{.*\}', text, re.S)
        if not m:
            return None, 'no JSON object in the answer'
        try:
            return json.loads(m.group()), None
        except Exception:
            return None, 'answer JSON malformed'

    # ---- the signal
    def verify(self, block_id, text, context=None):
        """→ (`[AnomalySignal]`, `[proposal dict]`, meta).

        Detection and proposal come back separately on purpose. A finding with `proposed: null` is an
        anomaly and nothing else; a finding with a proposal is *also* an anomaly, and the proposal is a
        candidate that still has to be validated by another layer.
        """
        ctx = dict(subject='không rõ', lesson='không rõ', heading='không rõ', role='không rõ')
        ctx.update({k: v for k, v in (context or {}).items() if v})
        prompt = PROMPT.format(text=text, subject=ctx['subject'], lesson=ctx['lesson'],
                               heading=ctx['heading'], role=ctx['role'])
        rec = self._ask(prompt)
        parsed, err = self._parse(rec)
        meta = dict(model=self.model, prompt_version=PROMPT_VERSION, cached=bool(rec and 'raw' in rec),
                    error=err)
        if parsed is None:
            if err:
                self.stats['unparsable'] += 1
            return [], [], meta
        anomalies, proposals = [], []
        for f in (parsed.get('findings') or ()):
            if not isinstance(f, dict) or not f.get('span'):
                continue
            span = str(f['span'])
            if span not in text:
                # the model quoted something that is not in the block. That is a hallucinated span and it
                # is dropped and counted, never repaired into a match.
                meta.setdefault('dropped_spans', []).append(span)
                continue
            sev = f.get('severity') if f.get('severity') in ('teaching_critical', 'display') else 'unknown'
            ev = [EvidenceRef(kind='llm_statement', source=f'{self.model}@{PROMPT_VERSION}',
                              claim=str(s), relation='supports', authority='unknown')
                  for s in (f.get('supporting') or ())[:4]]
            ev += [EvidenceRef(kind='llm_statement', source=f'{self.model}@{PROMPT_VERSION}',
                               claim=str(s), relation='contradicts', authority='unknown')
                   for s in (f.get('contradicting') or ())[:4]]
            anomalies.append(AnomalySignal(
                block_id=block_id, detector_id=f'{SIGNAL_ID}/{self.model}@{PROMPT_VERSION}',
                reason=str(f.get('reason') or '')[:400], span=span, observed=text,
                confidence=_num(f.get('confidence')), severity=sev,
                context_supplied=dict(ctx, prompt_version=PROMPT_VERSION, text_shown=text),
                evidence=ev))
            if f.get('proposed'):
                proposals.append(dict(span=span, proposed=str(f['proposed']),
                                      kind=str(f.get('kind') or 'other'), severity=sev,
                                      reason=str(f.get('reason') or '')[:400],
                                      confidence=_num(f.get('confidence')),
                                      supporting=[e.to_json() for e in ev if e.relation == 'supports'],
                                      contradicting=[e.to_json() for e in ev if e.contradicts]))
        return anomalies, proposals, meta


def _num(x):
    try:
        return max(0.0, min(1.0, float(x)))
    except Exception:
        return 0.0


# --------------------------------------------------------------------------- plugins (A1's registry)
_STATE = dict(verifier=None)


def install(verifier):
    _STATE['verifier'] = verifier
    return verifier


def llm_signal(value, ctx):
    """`G.llm_semantic` as a reading ABOUT a proposed value. Supports only when the model independently
    proposed the same replacement; objects when it proposed a *different* one (a disagreement is
    information, not noise); abstains otherwise."""
    v = _STATE['verifier']
    if v is None or not ctx.primary():
        return model.Signal(SIGNAL_ID, model.SignalVerdict.ABSTAINS, 0.0, dict(reason='no LLM installed'))
    observed = ctx.primary().value
    if not isinstance(observed, str) or not isinstance(value, str):
        return model.Signal(SIGNAL_ID, model.SignalVerdict.ABSTAINS, 0.0, dict(reason='not text'))
    anomalies, proposals, meta = v.verify(ctx.block_id, observed, _ctx_of(ctx))
    if not anomalies:
        return model.Signal(SIGNAL_ID, model.SignalVerdict.ABSTAINS, 0.0,
                            dict(reason='the model reports no anomaly', meta=meta))
    for p in proposals:
        if observed.replace(p['span'], p['proposed']) == value:
            return model.Signal(SIGNAL_ID, model.SignalVerdict.SUPPORTS, p['confidence'],
                                dict(proposal=p, meta=meta))
    if proposals:
        return model.Signal(SIGNAL_ID, model.SignalVerdict.OBJECTS,
                            max(p['confidence'] for p in proposals),
                            dict(reason='the model proposes a DIFFERENT correction', proposals=proposals,
                                 meta=meta))
    return model.Signal(SIGNAL_ID, model.SignalVerdict.ABSTAINS, 0.0,
                        dict(reason='the model flags an anomaly but proposes nothing',
                             anomalies=[a.to_json() for a in anomalies], meta=meta))


def llm_token_signal(observed, proposed, ctx):
    """Consulted by A1's repairer for every token it is about to change. An LLM reading is one vote among
    the layers here and carries no privilege — it can support, it can veto, it can abstain, and it never
    decides alone because `llm_validator` refuses layer `G` as its own corroboration."""
    v = _STATE['verifier']
    if v is None or not ctx.primary() or not isinstance(observed, str):
        return None
    text = ctx.primary().value
    if not isinstance(text, str):
        return None
    anomalies, proposals, meta = v.verify(ctx.block_id, text, _ctx_of(ctx))
    for p in proposals:
        if observed.lower() in p['span'].lower():
            if p['proposed'].lower() == str(proposed).lower() or str(proposed).lower() in p['proposed'].lower():
                return model.Signal(SIGNAL_ID, model.SignalVerdict.SUPPORTS, p['confidence'],
                                    dict(proposal=p, meta=meta))
            return model.Signal(SIGNAL_ID, model.SignalVerdict.OBJECTS, p['confidence'],
                                dict(reason='the model proposes a different token here', proposal=p))
    return model.Signal(SIGNAL_ID, model.SignalVerdict.ABSTAINS, 0.0,
                        dict(reason='the model says nothing about this token',
                             anomalies=len(anomalies), meta=meta))


def llm_validator(candidate, ctx):
    """**An LLM may never validate a repair an LLM proposed**, and it may never validate alone.

    This is the code that makes «LLM OUTPUT ≠ TRUTH» true rather than stated. A candidate whose only
    support is layer `G` returns `insufficient`, which A1's engine treats exactly like `rejected` for the
    purpose of serving anything.
    """
    if candidate.contradicting():
        return model.ValidationResult(VALIDATOR_ID, model.Verdict.REJECTED,
                                      detail=dict(reason='a signal objects to this candidate'))
    layers = candidate.independent_support(exclude_layers=('G',))
    if not layers:
        return model.ValidationResult(
            VALIDATOR_ID, model.Verdict.INSUFFICIENT,
            detail=dict(reason='only LLM support; an LLM answer is an observation, not a validation'))
    return None      # nothing to add: another validator's verdict stands


def _ctx_of(ctx):
    page = dict(ctx.page or {})
    return dict(subject=page.get('subject') or page.get('book'), lesson=page.get('lesson'),
                heading=' > '.join(page.get('heading_path') or ()) or None, role=ctx.role)


# --------------------------------------------------------------------------- registration
def register():
    """Idempotent, and callable again after `registry.reset()`."""
    return _reg.apply(
        signals={SIGNAL_ID: llm_signal},
        token_providers={'llm.token-v1': llm_token_signal},
        validators={(FC_TONE, VALIDATOR_ID): llm_validator})


register()
