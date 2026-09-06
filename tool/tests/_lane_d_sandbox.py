#!/usr/bin/env python3
"""One sandbox root shared by every Lane D test module — import this FIRST.

Why this module exists (found in round 5, by adding a second Lane D test file):
`tool/corpus/legacy/common.py` resolves `MAIN_ROOT`, `OCR`, `PDF`, `UNITS`, … from
`TC_ROOT` **at import time**. `test_legacy_lane_d.py` therefore set `TC_ROOT` to its
own tmpdir and imported `common` immediately, and its containment assertions held only
because it happened to be the first module to import `common`. Adding
`test_lane_d_packs.py` — which sorts *before* it under `unittest discover` and pulls in
`common` transitively — silently moved the real corpus paths back into `common`, and the
containment test failed. It failed loudly here, but a hermetic-sandbox guarantee that
depends on alphabetical order is not a guarantee.

Importing this module first makes the sandbox a property of the test *session* rather
than of whichever file wins the race: the interpreter caches it, so the first Lane D
module to import it creates the tmpdir and sets the environment, and every later one
gets the same root back.
"""
import atexit
import os
import shutil
import tempfile

ROOT = tempfile.mkdtemp(prefix='lane-d-tests-')
LEGACY_OUT = os.path.join(ROOT, 'legacy')
os.environ['TC_ROOT'] = ROOT
os.environ['LEGACY_OUT'] = LEGACY_OUT
atexit.register(shutil.rmtree, ROOT, True)
