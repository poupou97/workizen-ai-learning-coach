"""Round 6 · Workstream A — TRUTH ACCOUNTING.

`INPUT SOURCE REGIONS = SERVED + WITHHELD + EXCLUDED_WITH_REASON + defined non-learning regions`

Every source region the pipeline extracted must carry an explicit, auditable disposition. Any region
that carries none is UNACCOUNTED, and an UNACCOUNTED region is a HARD FAILURE — not a warning.
"""
