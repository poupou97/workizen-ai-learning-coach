#!/usr/bin/env python3
"""Build an immutable, standalone per-round retrospective archive (a ZIP on the Founder's Desktop).

Why this exists
---------------
A round's evidence is spread across a repository, GitHub, a device-evidence directory and a set of
gitignored artefact trees. A Founder cannot read that. This tool assembles one self-contained ZIP
that can be opened years later with no repository, no network and no tooling.

Three rules the tool enforces rather than trusts:

1. **Never overwrite an archive.** A previous round's ZIP is immutable evidence. If the target name
   exists, the tool writes ``-v2`` (then ``-v3`` …) and says so.
2. **No zero-byte required document.** Every required report must exist and be non-empty, or the
   build fails. An empty file in an archive is worse than a missing one, because it reads as
   "nothing happened" rather than "this was not captured".
3. **The manifest is generated from the bytes that are actually staged**, never hand-written, and
   it is then re-verified against the finished ZIP.

Large or licence-restricted data (an SGK corpus, derived OCR trees) is **never** copied. The spec
records path, size and reason in ``excluded``, and the round's own docs carry the reproduction
instructions.

Usage
-----
    python3 tool/reporting/build_round_archive.py \
        --spec /path/to/round05-content/archive-spec.json \
        --repo /path/to/repo \
        --out ~/Desktop

    # check what would happen without writing anything
    python3 tool/reporting/build_round_archive.py --spec ... --dry-run

The spec (``wal-round-archive-spec-v1``) lives beside the round's authored documents. See
``tool/reporting/README.md`` for the field-by-field description and for how to reuse this for the
next round.

Exit codes: 0 built and verified · 1 build/verification failure · 2 bad invocation.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

SCHEMA = "wal-round-archive-spec-v1"
BUF = 1024 * 1024


# --------------------------------------------------------------------------- helpers
def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(BUF)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def human(n: int) -> str:
    x = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if x < 1024 or unit == "GB":
            return f"{x:.1f} {unit}" if unit != "B" else f"{int(x)} B"
        x /= 1024
    return f"{x:.1f} GB"


def git(repo: str, *args: str) -> str:
    try:
        return subprocess.run(
            ["git", *args], cwd=repo, capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:
        return "UNAVAILABLE"


def repo_name(repo: str) -> str:
    """Name the repository by its origin remote, not by the checkout directory.

    A worktree directory is named after the task, not the project, so the directory basename
    would misidentify an archive built from one.
    """
    url = git(repo, "remote", "get-url", "origin")
    if url and url != "UNAVAILABLE":
        return os.path.basename(url.rstrip("/")).removesuffix(".git")
    return os.path.basename(os.path.abspath(repo))


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


# --------------------------------------------------------------------------- staging
def stage_content(content_dir: str, root: str) -> None:
    """Copy the round's authored documents and any pre-built evidence subdirectories."""
    for name in sorted(os.listdir(content_dir)):
        if name in ("archive-spec.json",) or name.startswith("."):
            continue
        src = os.path.join(content_dir, name)
        dst = os.path.join(root, name)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            os.makedirs(os.path.dirname(dst) or root, exist_ok=True)
            shutil.copy2(src, dst)


def stage_copies(spec: dict, repo: str, root: str) -> tuple[list[str], list[str]]:
    """Apply the spec's copy operations. Returns (copied, missing_optional)."""
    copied: list[str] = []
    missing: list[str] = []
    for op in spec.get("copy", []):
        src_pat = op["src"]
        dest_rel = op["dest"]
        abs_pat = src_pat if os.path.isabs(src_pat) else os.path.join(repo, src_pat)
        matches = sorted(glob.glob(abs_pat))
        if not matches:
            if op.get("optional"):
                missing.append(src_pat)
                continue
            fail(f"required source not found: {src_pat}")
        dest_dir = os.path.join(root, dest_rel)
        os.makedirs(dest_dir, exist_ok=True)
        for m in matches:
            if os.path.isdir(m):
                shutil.copytree(m, os.path.join(dest_dir, os.path.basename(m)), dirs_exist_ok=True)
                copied.append(m)
                continue
            name = op.get("rename") if (op.get("rename") and len(matches) == 1) else os.path.basename(m)
            shutil.copy2(m, os.path.join(dest_dir, name))
            copied.append(os.path.join(dest_rel, name))
    return copied, missing


def walk_files(root: str) -> list[str]:
    out = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if fn == ".DS_Store":
                continue
            out.append(os.path.relpath(os.path.join(dirpath, fn), root))
    return sorted(out)


# --------------------------------------------------------------------------- checks
def check_required(spec: dict, root: str) -> list[str]:
    """Every required doc must exist and be non-empty. Returns the problems found."""
    problems = []
    generated = set(spec.get("generatedDocs", []))
    for doc in spec["requiredDocs"]:
        if doc in generated:
            continue  # written later by write_manifest()
        p = os.path.join(root, doc)
        if not os.path.exists(p):
            problems.append(f"MISSING required document: {doc}")
        elif os.path.getsize(p) == 0:
            problems.append(f"ZERO-BYTE required document: {doc}")
    for d in spec.get("requiredDirs", []):
        p = os.path.join(root, d)
        if not os.path.isdir(p):
            problems.append(f"MISSING required directory: {d}/")
        elif not walk_files(p):
            problems.append(f"EMPTY required directory: {d}/")
    return problems


def check_references(spec: dict, root: str) -> list[str]:
    """Flag in-archive references that do not resolve.

    Two passes, both deliberately conservative so that prose mentioning a *repository* path
    cannot produce noise:

    1. the numbered documents and the required directories, referenced by bare name;
    2. any backticked path whose first segment is one of the required directories
       (e.g. ``evidence/round5-ci-status.txt``) — these are promises the archive makes about
       its own contents, so a broken one is a real defect.
    """
    problems = []
    req_dirs = list(spec.get("requiredDirs", []))
    names = set(spec["requiredDocs"]) | {d + "/" for d in req_dirs}
    present = set(walk_files(root))
    present_dirs = {p.split("/", 1)[0] + "/" for p in present if "/" in p}

    for doc in spec["requiredDocs"]:
        p = os.path.join(root, doc)
        if not os.path.exists(p):
            continue
        try:
            text = open(p, encoding="utf-8").read()
        except UnicodeDecodeError:
            continue

        for ref in names:
            if ref in text:
                if ref.endswith("/"):
                    if ref not in present_dirs:
                        problems.append(f"{doc} references {ref} which is not in the archive")
                elif ref not in present:
                    problems.append(f"{doc} references {ref} which is not in the archive")

        for chunk in text.split("`")[1::2]:
            ref = chunk.strip()
            if "/" not in ref or ref.endswith("/") or " " in ref:
                continue
            if ref.split("/", 1)[0] not in req_dirs:
                continue
            if ref not in present:
                problems.append(f"{doc} references `{ref}` which is not in the archive")
    return problems


# --------------------------------------------------------------------------- manifest
def write_manifest(spec: dict, repo: str, root: str, missing_optional: list[str]) -> str:
    files = [f for f in walk_files(root) if f != "15-FILE-MANIFEST.md"]
    rows = []
    total = 0
    for rel in files:
        p = os.path.join(root, rel)
        size = os.path.getsize(p)
        total += size
        rows.append((rel, size, sha256_file(p)))

    by_dir: dict[str, list[tuple[str, int, str]]] = {}
    for rel, size, digest in rows:
        top = rel.split("/", 1)[0] if "/" in rel else "(root)"
        by_dir.setdefault(top, []).append((rel, size, digest))

    now = _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()
    out = [
        "# 15 · FILE MANIFEST",
        "",
        "> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**",
        "",
        f"Generated by `tool/reporting/build_round_archive.py` on **{now}**.",
        "Every hash below was computed from the staged bytes and is re-verified against the",
        "finished ZIP by the same tool. `15-FILE-MANIFEST.md` itself is not listed (it cannot",
        "contain its own hash).",
        "",
        "| | |",
        "|---|---|",
        f"| Round | {spec['round']} — {spec['roundLabel']} |",
        f"| Close date | **{spec['closeDate']}** |",
        f"| Classification | {spec['classification']} |",
        f"| Files (excluding this manifest) | **{len(rows)}** |",
        f"| Total staged size | **{human(total)}** ({total:,} bytes) |",
        f"| Repository | `{repo_name(repo)}` |",
        f"| Built from commit | `{git(repo, 'rev-parse', 'HEAD')}` on branch `{git(repo, 'rev-parse', '--abbrev-ref', 'HEAD')}` |",
        "",
        "## Close-date evidence",
        "",
        spec.get("closeDateEvidence", "NOT CAPTURED"),
        "",
    ]

    if spec.get("excluded"):
        out += [
            "## Deliberately NOT included",
            "",
            "| What | Path | Size | Reason |",
            "|---|---|---|---|",
        ]
        for e in spec["excluded"]:
            out.append(f"| {e['what']} | `{e['path']}` | {e['size']} | {e['reason']} |")
        out.append("")

    if missing_optional:
        out += [
            "## Optional sources that were not present (recorded, not silently dropped)",
            "",
        ] + [f"- `{m}` — **NOT CAPTURED**" for m in missing_optional] + [""]

    out += ["## Files", ""]
    for top in sorted(by_dir):
        out += [f"### `{top}`", "", "| file | bytes | sha256 |", "|---|---|---|"]
        for rel, size, digest in by_dir[top]:
            out.append(f"| `{rel}` | {size:,} | `{digest}` |")
        out.append("")

    path = os.path.join(root, "15-FILE-MANIFEST.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    return path


def write_build_verification(spec: dict, repo: str, root: str, problems: list[str],
                             missing_optional: list[str]) -> None:
    os.makedirs(os.path.join(root, "manifests"), exist_ok=True)
    now = _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()
    files = walk_files(root)
    lines = [
        "# Build verification (pre-zip)",
        "",
        f"Generated {now} by `tool/reporting/build_round_archive.py`.",
        "",
        f"- required documents present and non-empty: **{'YES' if not problems else 'NO'}**",
        f"- required directories present and non-empty: **{'YES' if not problems else 'NO'}**",
        f"- files staged when this check ran: **{len(files)}** "
        "(`15-FILE-MANIFEST.md` and this file are written afterwards, so the finished archive "
        "holds two more — the manifest and the ZIP verification both state the final count)",
        f"- broken in-archive references: **{'none' if not problems else len(problems)}**",
        "",
    ]
    if problems:
        lines += ["## Problems", ""] + [f"- {p}" for p in problems] + [""]
    if missing_optional:
        lines += [
            "## Optional sources not present — recorded as NOT CAPTURED",
            "",
        ] + [f"- `{m}`" for m in missing_optional] + [""]
    lines += [
        "## Post-zip verification",
        "",
        "The ZIP's own integrity check (`testzip`), member-count comparison and SHA-256 are printed",
        "by the tool at build time and recorded in the rounds index",
        "(`~/Desktop/HOC-CUNG-SAM-ROUNDS-INDEX.md`). They cannot be written inside the ZIP they",
        "describe.",
        "",
    ]
    with open(os.path.join(root, "manifests", "BUILD-VERIFICATION.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# --------------------------------------------------------------------------- zip + verify
def next_free_name(out_dir: str, base: str) -> tuple[str, str | None]:
    """Never overwrite. Returns (path, note)."""
    path = os.path.join(out_dir, base + ".zip")
    if not os.path.exists(path):
        return path, None
    n = 2
    while os.path.exists(os.path.join(out_dir, f"{base}-v{n}.zip")):
        n += 1
    newp = os.path.join(out_dir, f"{base}-v{n}.zip")
    return newp, f"{base}.zip already exists and was NOT overwritten; wrote {os.path.basename(newp)}"


def build_zip(root: str, root_name: str, zip_path: str) -> None:
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for rel in walk_files(root):
            z.write(os.path.join(root, rel), os.path.join(root_name, rel))


def verify_zip(zip_path: str, root: str, root_name: str, spec: dict) -> dict:
    result: dict = {"problems": []}
    with zipfile.ZipFile(zip_path) as z:
        bad = z.testzip()
        result["opens"] = True
        result["testzip"] = "OK" if bad is None else f"CORRUPT: {bad}"
        if bad is not None:
            result["problems"].append(f"corrupt member: {bad}")
        members = [m for m in z.namelist() if not m.endswith("/")]
        result["members"] = len(members)

        staged = walk_files(root)
        result["staged"] = len(staged)
        if len(members) != len(staged):
            result["problems"].append(f"member count {len(members)} != staged count {len(staged)}")

        for doc in spec["requiredDocs"]:
            name = os.path.join(root_name, doc)
            if name not in members:
                result["problems"].append(f"required document missing from ZIP: {doc}")
            elif z.getinfo(name).file_size == 0:
                result["problems"].append(f"required document is zero-byte in ZIP: {doc}")

        # manifest vs content: recompute every hash from inside the ZIP
        man_name = os.path.join(root_name, "15-FILE-MANIFEST.md")
        listed: dict[str, str] = {}
        if man_name in members:
            for line in z.read(man_name).decode("utf-8").splitlines():
                if not line.startswith("| `") or not line.endswith("|"):
                    continue
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if len(cells) != 3:
                    continue
                rel = cells[0].strip("`")
                digest = cells[2].strip("`")
                if len(digest) == 64 and all(c in "0123456789abcdef" for c in digest):
                    listed[rel] = digest
        mismatches = 0
        for rel, digest in listed.items():
            name = os.path.join(root_name, rel)
            if name not in members:
                result["problems"].append(f"manifest lists {rel} which is not in the ZIP")
                mismatches += 1
                continue
            h = hashlib.sha256()
            with z.open(name) as fh:
                while True:
                    chunk = fh.read(BUF)
                    if not chunk:
                        break
                    h.update(chunk)
            if h.hexdigest() != digest:
                result["problems"].append(f"hash mismatch for {rel}")
                mismatches += 1
        unlisted = [m for m in members if os.path.relpath(m, root_name) not in listed
                    and os.path.relpath(m, root_name) != "15-FILE-MANIFEST.md"]
        if unlisted:
            result["problems"].append(f"{len(unlisted)} file(s) in the ZIP are absent from the manifest")
        result["manifest_entries"] = len(listed)
        result["manifest_mismatches"] = mismatches

    result["bytes"] = os.path.getsize(zip_path)
    result["sha256"] = sha256_file(zip_path)
    result["ok"] = not result["problems"]
    return result


# --------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", required=True, help="path to the round's archive-spec.json")
    ap.add_argument("--repo", default=os.getcwd(), help="repository root (default: cwd)")
    ap.add_argument("--out", default=os.path.expanduser("~/Desktop"), help="where the ZIP is written")
    ap.add_argument("--keep-staging", action="store_true", help="do not delete the staging directory")
    ap.add_argument("--dry-run", action="store_true", help="stage and verify, but write no ZIP")
    args = ap.parse_args()

    spec_path = os.path.abspath(args.spec)
    if not os.path.exists(spec_path):
        print(f"spec not found: {spec_path}", file=sys.stderr)
        return 2
    spec = json.load(open(spec_path, encoding="utf-8"))
    if spec.get("schema") != SCHEMA:
        print(f"unexpected spec schema {spec.get('schema')!r} (want {SCHEMA})", file=sys.stderr)
        return 2

    content_dir = os.path.dirname(spec_path)
    repo = os.path.abspath(args.repo)
    out_dir = os.path.abspath(os.path.expanduser(args.out))
    os.makedirs(out_dir, exist_ok=True)

    root_name = spec.get("rootDir", f"ROUND-{spec['round']}")
    staging = tempfile.mkdtemp(prefix=f"round-archive-{spec['round']}-")
    root = os.path.join(staging, root_name)
    os.makedirs(root, exist_ok=True)

    print(f"staging   : {root}")
    stage_content(content_dir, root)
    copied, missing_optional = stage_copies(spec, repo, root)
    print(f"copied    : {len(copied)} file(s) from the repository")
    if missing_optional:
        print(f"NOT CAPTURED (optional sources absent): {len(missing_optional)}")
        for m in missing_optional:
            print(f"            - {m}")

    problems = check_required(spec, root)
    problems += check_references(spec, root)
    if problems:
        for p in problems:
            print(f"  ! {p}")
        fail(f"{len(problems)} pre-zip problem(s); nothing was written")

    write_build_verification(spec, repo, root, problems, missing_optional)
    write_manifest(spec, repo, root, missing_optional)

    problems = check_required(spec, root)  # re-check now that the manifest exists
    if problems:
        for p in problems:
            print(f"  ! {p}")
        fail("required-document check failed after manifest generation")

    files = walk_files(root)
    print(f"files     : {len(files)}")

    if args.dry_run:
        print("dry-run   : no ZIP written")
        print(f"staging kept at {staging}")
        return 0

    base = spec["archiveNameTemplate"].format(round=spec["round"], closeDate=spec["closeDate"])
    base = base[:-4] if base.endswith(".zip") else base
    zip_path, note = next_free_name(out_dir, base)
    if note:
        print(f"NOTE      : {note}")
    build_zip(root, root_name, zip_path)

    v = verify_zip(zip_path, root, root_name, spec)
    print("")
    print("=== VERIFICATION ===")
    print(f"zip           : {zip_path}")
    print(f"opens         : {v['opens']}   integrity: {v['testzip']}")
    print(f"files in zip  : {v['members']} (staged {v['staged']})")
    print(f"required docs : {'all present, none zero-byte' if v['ok'] else 'SEE PROBLEMS'}")
    print(f"manifest      : {v['manifest_entries']} entries, {v['manifest_mismatches']} mismatch(es)")
    print(f"size          : {human(v['bytes'])} ({v['bytes']:,} bytes)")
    print(f"sha256        : {v['sha256']}")
    if v["problems"]:
        for p in v["problems"]:
            print(f"  ! {p}")
        print("RESULT        : FAILED")
    else:
        print("RESULT        : PASS")

    if not args.keep_staging:
        shutil.rmtree(staging, ignore_errors=True)
    else:
        print(f"staging kept at {staging}")

    return 0 if v["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
