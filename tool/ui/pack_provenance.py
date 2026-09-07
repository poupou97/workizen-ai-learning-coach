#!/usr/bin/env python3
"""WAL-210 — pack build PROVENANCE (audit gate G5) for assets/pack/lesson-index-g<N>.json.

Why: `assets/pack` is gitignored, so a pack on disk carried no record of which
builder, which git state and which env flags produced it. The pre-autonomy
audit (02 §1, 07 #3) found the on-disk packs were the WAL-206 *experiment*
build (97 `pattern-router*` entries) — indistinguishable from a default build,
and any APK built on that Mac would have shipped them.

Every pack now carries a top-level ``buildProvenance`` (schema 1):

    {"schema": 1,
     "builderVersion": "build_lesson_index.py@<short sha of the script's last commit, or HEAD>",
     "gitSha": "<HEAD sha of the repo the builder ran from>",
     "builtAt": "<ISO-8601 UTC, e.g. 2026-09-05T10:20:30Z>",
     "grade": N,
     "flags": {"PATTERN_ROUTER": "0|1", "UNITS_SOURCE": "<value or ''>", "ROUTE_EXPLAIN": "0|1"},
     "experimental": true iff PATTERN_ROUTER=1 or any activity source starts with "pattern-router",
     "attachmentRule": "capped-toc-v2",
     "contentHash": "<sha256 hex of the canonical JSON (sort_keys, separators=(',',':'),
                      ensure_ascii=False) of the pack with buildProvenance removed>",
     "packVersion": "g<N>-<builtAt as YYYYMMDDTHHMMZ>-<gitSha[:8]>"}

Deterministic except ``builtAt`` (and therefore ``packVersion``). The Dart side
parses exactly this shape — do not rename keys.

CLI (the Python-side DEFAULT-BUILD test; exit ≠ 0 on any problem):

    python3 tool/ui/pack_provenance.py verify assets/pack/lesson-index-g6.json [more packs…]
    python3 tool/ui/pack_provenance.py show   assets/pack/lesson-index-g6.json

``verify`` fails when: provenance is missing or malformed, the content hash
does not match the file's content, ``experimental`` is true, any
``pattern-router*`` source exists, or the flags say PATTERN_ROUTER=1.
"""
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

SCHEMA = 1
# Round 4: the rule name is owned by lesson_attach, not duplicated here — a pack that
# stamps a rule it was not built with is a provenance lie (found by the round-4 review).
try:  # pragma: no cover - import shape depends on caller
    from lesson_attach import RULE as ATTACHMENT_RULE
except ImportError:
    from tool.ui.lesson_attach import RULE as ATTACHMENT_RULE
BUILDER_NAME = 'build_lesson_index.py'
ROUTER_FAMILIES = ('tvReadings', 'tvWritings')
ROUTER_PREFIX = 'pattern-router'
FLAG_NAMES = ('PATTERN_ROUTER', 'UNITS_SOURCE', 'ROUTE_EXPLAIN')


# ---------------------------------------------------------------- hashing
def canonical_json(obj):
    """The one canonical serialisation the hash is defined over."""
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def content_hash(pack):
    """sha256 hex of the canonical JSON of the pack WITHOUT buildProvenance."""
    body = {k: v for k, v in pack.items() if k != 'buildProvenance'}
    return hashlib.sha256(canonical_json(body).encode('utf-8')).hexdigest()


# ---------------------------------------------------------------- experiment detection
def router_sources(pack):
    """Every (family, index, source) whose source starts with 'pattern-router'.

    Scans EVERY activity family, not just the two the WAL-206 experiment happened
    to use: a detector that only looks where the last experiment put things finds
    only the last experiment.
    """
    out = []
    for fam in ACTIVITY_FAMILIES:
        for i, e in enumerate(_entries(pack, fam)):
            src = str((e or {}).get('source', '') or '')
            if src.startswith(ROUTER_PREFIX):
                out.append((fam, i, src))
    return out


VACUOUS = ('no activity entries in any family — "no pattern-router source" is '
           'vacuously true, so this pack cannot be certified a DEFAULT build')

# The families the DEFAULT-build claim is actually made OVER. ROUTER_FAMILIES is
# a strict subset: a KHTN pack legitimately carries no tvReadings at all, so the
# denominator must be every family, never the router ones alone.
#
# ⚠ THIS LIST WAS WRONG ONCE, IN THIS TICKET. The first cut listed only the
# three the router touches and reported 11 of 12 real packs as empty — a false
# RED, which is every bit as dishonest as the false green being fixed. The two
# sets below are exhaustive over the packs on disk, and `unknown_families()`
# makes any future key LOUD instead of silently mis-scored either way.
ACTIVITY_FAMILIES = (
    'toanExercises', 'tvReadings', 'tvWritings',
    'suSources', 'khoaExperiments', 'diaMaps',
)
NON_ACTIVITY_KEYS = (
    'grade', 'version', 'subjects', 'sourceAssets', 'books', 'buildProvenance',
)


def _entries(pack, fam):
    """Activity entries of one family, whatever container it uses.

    ⚠ CONTAINER SHAPE. `toanExercises` is a DICT keyed by lesson number, not a
    list: `len()` of it counts LESSONS, not exercises. Counting the wrong thing
    here has already broken twice — flatten the inner lists.
    """
    v = pack.get(fam)
    if isinstance(v, dict):
        for entries in v.values():
            yield from (entries or [])
    elif isinstance(v, list):
        yield from v


def unknown_families(pack):
    """Top-level keys this gate cannot classify — neither activity nor metadata.

    A gate that silently ignores a key it has never seen is how a denominator
    goes stale without anyone noticing. Make it a problem instead.
    """
    known = set(ACTIVITY_FAMILIES) | set(NON_ACTIVITY_KEYS)
    return sorted(k for k in pack if k not in known)


def activity_population(pack):
    """How many activity ENTRIES the pack carries — the denominator of the claim.

    WAL-223 S4: `router_sources()` returning [] means "no experiment sources
    found". Over an empty pack that is not evidence of anything, yet it read as
    a pass. Absence cannot satisfy a positive obligation, so the claim now
    carries its own denominator.
    """
    return sum(1 for fam in ACTIVITY_FAMILIES for _ in _entries(pack, fam))


def read_flags(env=None):
    """Normalise the three build flags from the environment into the manifest shape."""
    env = os.environ if env is None else env
    return {
        'PATTERN_ROUTER': '1' if env.get('PATTERN_ROUTER') == '1' else '0',
        'UNITS_SOURCE': env.get('UNITS_SOURCE', '') or '',
        'ROUTE_EXPLAIN': '1' if env.get('ROUTE_EXPLAIN') == '1' else '0',
    }


def is_experimental(pack, flags):
    return flags.get('PATTERN_ROUTER') == '1' or bool(router_sources(pack))


# ---------------------------------------------------------------- git
def _git(args, cwd):
    try:
        r = subprocess.run(['git'] + list(args), cwd=cwd, capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    return r.stdout.strip()


def git_head_sha(script_path):
    """Full HEAD sha of the repo that contains the builder script; 'unknown' outside git."""
    return _git(['rev-parse', 'HEAD'], os.path.dirname(os.path.abspath(script_path))) or 'unknown'


def builder_version(script_path):
    """'build_lesson_index.py@<short sha of the script's last commit>' — HEAD short sha when the
    script has no commit yet; '-dirty' appended when the script has uncommitted changes, so a pack
    can never claim a version its code did not have."""
    d = os.path.dirname(os.path.abspath(script_path))
    base = os.path.basename(script_path)
    short = _git(['log', '-n', '1', '--format=%h', '--', base], d) or _git(['rev-parse', '--short', 'HEAD'], d) or 'unknown'
    dirty = _git(['status', '--porcelain', '--', base], d)
    if dirty:
        short += '-dirty'
    return f'{BUILDER_NAME}@{short}'


# ---------------------------------------------------------------- build / stamp
def build_provenance(pack, grade, flags, script_path, built_at=None):
    built_at = built_at or datetime.now(timezone.utc)
    built_at = built_at.astimezone(timezone.utc).replace(microsecond=0)
    sha = git_head_sha(script_path)
    return {
        'schema': SCHEMA,
        'builderVersion': builder_version(script_path),
        'gitSha': sha,
        'builtAt': built_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'grade': int(grade),
        'flags': {k: flags.get(k, '') for k in FLAG_NAMES},
        'experimental': bool(is_experimental(pack, flags)),
        'attachmentRule': ATTACHMENT_RULE,
        'contentHash': content_hash(pack),
        'packVersion': f'g{int(grade)}-{built_at.strftime("%Y%m%dT%H%MZ")}-{sha[:8]}',
    }


def stamp(pack, grade, flags, script_path, built_at=None):
    """Return the pack with a fresh buildProvenance (replaces any previous one)."""
    pack = {k: v for k, v in pack.items() if k != 'buildProvenance'}
    pack['buildProvenance'] = build_provenance(pack, grade, flags, script_path, built_at)
    return pack


# ---------------------------------------------------------------- verify
def verify_pack(pack, expect_grade=None, require_default=True):
    """List of problems (empty = OK). ``require_default`` adds the default-build assertions."""
    problems = []
    prov = pack.get('buildProvenance')
    if not isinstance(prov, dict):
        return ['missing buildProvenance']
    if prov.get('schema') != SCHEMA:
        problems.append(f'schema {prov.get("schema")!r} != {SCHEMA}')
    for k in ('builderVersion', 'gitSha', 'builtAt', 'grade', 'flags', 'experimental', 'attachmentRule', 'contentHash', 'packVersion'):
        if k not in prov:
            problems.append(f'missing buildProvenance.{k}')
    if problems:
        return problems
    if not isinstance(prov['flags'], dict) or set(prov['flags']) != set(FLAG_NAMES):
        problems.append(f'flags keys {sorted(prov["flags"]) if isinstance(prov["flags"], dict) else prov["flags"]!r} != {sorted(FLAG_NAMES)}')
    expected = content_hash(pack)
    if prov['contentHash'] != expected:
        problems.append(f'contentHash mismatch: manifest {prov["contentHash"][:12]}… vs content {expected[:12]}…')
    if pack.get('grade') != prov['grade']:
        problems.append(f'grade mismatch: pack {pack.get("grade")} vs manifest {prov["grade"]}')
    if expect_grade is not None and prov['grade'] != expect_grade:
        problems.append(f'grade {prov["grade"]} != expected {expect_grade}')
    if prov['attachmentRule'] != ATTACHMENT_RULE:
        problems.append(f'attachmentRule {prov["attachmentRule"]!r} != {ATTACHMENT_RULE!r}')
    sha = str(prov['gitSha'])
    if not prov['packVersion'].startswith(f'g{prov["grade"]}-') or not prov['packVersion'].endswith(sha[:8]):
        problems.append(f'packVersion {prov["packVersion"]!r} does not match grade/gitSha')
    if require_default:
        # ⭐ Mẫu số TRƯỚC, khẳng định SAU. Pack rỗng ⇒ không kết luận được gì.
        if activity_population(pack) == 0:
            problems.append(VACUOUS)
        unknown = unknown_families(pack)
        if unknown:
            problems.append(
                f'unclassified top-level key(s) {unknown} — this gate cannot tell '
                'whether they carry activities, so the denominator may be wrong; '
                'add each to ACTIVITY_FAMILIES or NON_ACTIVITY_KEYS')
        if prov['experimental'] is True:
            problems.append('experimental build (manifest says experimental=true)')
        srcs = router_sources(pack)
        if srcs:
            problems.append(f'{len(srcs)} pattern-router* activity source(s) present (e.g. {srcs[0][0]}[{srcs[0][1]}]={srcs[0][2]})')
        if prov['flags'].get('PATTERN_ROUTER') == '1':
            problems.append('built with PATTERN_ROUTER=1')
        if prov['experimental'] is False and srcs:
            problems.append('manifest says experimental=false but router sources exist')
    return problems


def grade_from_filename(path):
    import re
    m = re.search(r'lesson-index-g(\d+)\.json$', os.path.basename(path))
    return int(m.group(1)) if m else None


def verify_file(path, require_default=True):
    try:
        pack = json.load(open(path, encoding='utf-8'))
    except (OSError, ValueError) as e:
        return [f'cannot read: {e}']
    if not isinstance(pack, dict):
        return ['pack is not a JSON object']
    return verify_pack(pack, expect_grade=grade_from_filename(path), require_default=require_default)


def write_ledger(path, record):
    """Record what this run actually verified, so «never ran» stays readable.

    WAL-223 S3: the CI step skipped the gate whenever the packs were absent and
    exited 0, arguing that printing «skipped» is honest. Printing is not a
    record — nothing downstream can read a log line. A ledger can be read, and
    a run that produced none has not demonstrated anything.
    """
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(record, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write('\n')


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    ledger_path, require_verified, allow_empty = None, False, False
    rest = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--ledger' and i + 1 < len(argv):
            ledger_path = argv[i + 1]
            i += 2
        elif a == '--require-verified':
            require_verified = True
            i += 1
        elif a == '--allow-empty':
            allow_empty = True
            i += 1
        else:
            rest.append(a)
            i += 1
    argv = rest
    if not argv or argv[0] not in ('verify', 'show'):
        print(__doc__.strip().split('\n')[0])
        print('usage: pack_provenance.py verify [--ledger PATH] [--require-verified] <pack.json>…')
        print('       pack_provenance.py show <pack.json>')
        return 2
    cmd, paths = argv[0], argv[1:]
    # ⭐ «Không có pack nào» phải được KHAI BÁO, không được ngầm hiểu.
    #
    # CI hợp lệ khi truyền vào 0 pack (corpus không bao giờ vào repo), nhưng
    # người gõ nhầm `verify` cụt cũng ra đúng hình dạng ấy. Bắt caller nói rõ
    # `--allow-empty` thì hai trường hợp tách ra được, và bên nào cố tình chấp
    # nhận sự vắng mặt thì phải viết ra điều đó.
    if cmd == 'verify' and not paths and not (allow_empty or require_verified):
        print('usage: pack_provenance.py verify [--ledger PATH] [--require-verified] '
              '[--allow-empty] <pack.json>…')
        print('  refusing to treat "no packs given" as a run; pass --allow-empty '
              'if zero packs is an expected input here.')
        return 2
    if cmd == 'show':
        if not paths:
            return 2
        for p in paths:
            pack = json.load(open(p, encoding='utf-8'))
            print(p)
            print(json.dumps(pack.get('buildProvenance'), ensure_ascii=False, indent=2))
        return 0

    verified, failed, vacuous = [], [], []
    for p in paths:
        problems = verify_file(p)
        if problems:
            (vacuous if VACUOUS in problems else failed).append(p)
            print(f'FAIL {p}')
            for x in problems:
                print(f'     - {x}')
        else:
            prov = json.load(open(p, encoding='utf-8'))['buildProvenance']
            verified.append(p)
            print(f'OK   {p}  {prov["packVersion"]}  {prov["builderVersion"]}  hash {prov["contentHash"][:12]}…')

    # ⭐ Ba kết quả KHÁC NHAU, không gộp thành một dòng «đạt»:
    #   verified   — đã kiểm và đạt
    #   failed     — đã kiểm và phát hiện sai
    #   vacuous    — KHÔNG kiểm được: pack rỗng, khẳng định không có mẫu số
    # và trường hợp thứ tư: paths rỗng ⇒ chưa từng chạy.
    print(f'{len(verified)}/{len(paths)} pack(s) verified as DEFAULT builds'
          + (f'; {len(failed)} FAILED' if failed else '')
          + (f'; {len(vacuous)} UNVERIFIABLE (empty)' if vacuous else ''))
    if not paths:
        print('NOT VERIFIED: no pack was given to verify. This is not a pass — '
              'the gate did not run.')

    if ledger_path:
        write_ledger(ledger_path, {
            'tool': 'pack_provenance',
            'ran': bool(paths),
            'packsGiven': len(paths),
            'verified': sorted(verified),
            'failed': sorted(failed),
            'unverifiable': sorted(vacuous),
            'claimsDefaultBuildVerified': bool(verified) and not failed and not vacuous,
        })

    if failed or vacuous:
        return 1
    if not verified:
        # Nothing was verified. Ok as a recorded state; a hard failure for any
        # caller that CLAIMS verification happened.
        if require_verified:
            print('  --require-verified was passed but 0 pack(s) were verified.')
            return 1
        return 0
    return 0


if __name__ == '__main__':
    sys.exit(main())
