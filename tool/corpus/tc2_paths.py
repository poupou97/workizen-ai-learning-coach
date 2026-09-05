#!/usr/bin/env python3
"""TC-v2 — one place for the pipeline's output root and the raw-candidate fallback chain.

Round 4 (Lane A-pipeline): every versioned pipeline run (`tc2-p2`, `tc2-p3`, …) writes ONLY under its own
root and never overwrites an older version. The default root stays where `tc2-p1` lives
(`poc-out/trusted-corpus/tc-v2/<pipeline>`); a run can be redirected with `--out <dir>` on the CLIs or
the environment variable `TC2_OUT_ROOT` (absolute path of the pipeline directory itself, e.g.
`poc-out/round4/pipeline/tc2-p2`).

Raw candidate outputs (Docling / XY-cut / naive) are deterministic per page and independent of the SDM,
role, guard and attachment code that changes between pipeline versions — so a later version REUSES the
raw files of an earlier one instead of re-running Docling (≈ 1.5 s/page). `raw_path` therefore searches,
in order: the run's own root → `tc2-p1` → the TC-v1 bake-off, and reports which one it used so the SDM
page can record it (`source.docling_raw`).
"""
import os

ROOT = os.environ.get('TC_ROOT', '/Users/alexnguyen/projects/workizen-ai-learning-coach')
DEFAULT_PIPELINE = 'tc2-p1'
_override = None


def set_out_root(path):
    """Redirect every writer/reader to `path` (the pipeline directory itself). None restores the default."""
    global _override
    _override = os.path.abspath(path) if path else None


def out_root(pipeline=DEFAULT_PIPELINE):
    if _override:
        return _override
    env = os.environ.get('TC2_OUT_ROOT')
    if env:
        return os.path.abspath(env)
    return f'{ROOT}/poc-out/trusted-corpus/tc-v2/{pipeline}'


def raw_candidates(pipeline=DEFAULT_PIPELINE):
    """(label, directory) pairs searched for a raw candidate file, most specific first."""
    own = out_root(pipeline)
    chain = [(pipeline, f'{own}/bakeoff/raw')]
    p1 = f'{ROOT}/poc-out/trusted-corpus/tc-v2/{DEFAULT_PIPELINE}/bakeoff/raw'
    if os.path.abspath(f'{own}/bakeoff/raw') != os.path.abspath(p1):
        chain.append((f'tc-v2/{DEFAULT_PIPELINE}', p1))
    chain.append(('tc-v1', f'{ROOT}/poc-out/trusted-corpus/tc-v1/bakeoff/raw'))
    return chain


def raw_path(cand, book, page, pipeline=DEFAULT_PIPELINE, allow_fallback=True):
    """→ (path, source_label) of the first existing raw file for this candidate/page, or (None, None)."""
    for label, d in raw_candidates(pipeline):
        p = f'{d}/{cand}/{book}-p{page:03d}.json'
        if os.path.exists(p):
            return p, label
        if not allow_fallback:
            break
    return None, None


def own_raw_path(cand, book, page, pipeline=DEFAULT_PIPELINE):
    """Where THIS run writes a new raw file."""
    return f'{out_root(pipeline)}/bakeoff/raw/{cand}/{book}-p{page:03d}.json'
