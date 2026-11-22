#!/usr/bin/env python3
"""Prove the bundle is portable: it must resolve every internal reference from whatever
directory it is installed into, contain no path from the machine that authored it, and have
every self-testing script still pass after being copied elsewhere.

Why this exists separately from the other gates: a skills bundle is read by an agent in some
other session, on some other machine, usually from ~/.qoder/skills/. Two failure classes are
invisible in place and fatal in use - an absolute path that only exists on the authoring
machine, and a relative reference written against the wrong anchor (`assets/...` instead of
`../assets/...` from inside a skill directory). Both look perfect in the source tree if you
never leave it.

    python3 scripts/audit_install.py                # audit the suite this script lives in
    python3 scripts/audit_install.py --root DIR     # audit DIR as the suite root
    python3 scripts/audit_install.py --self-test    # prove the gate detects planted breakage

Exit 0 only if every check passes.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

# Path-like tokens that claim to point inside the bundle. Only two forms are checked, because
# only those two are unambiguously live: an image embed, and a markdown link. Prose that
# mentions a path as an example (a code span in a licence note, a provenance header naming a
# reference file from the shared assets directory) is not a link, and treating it as one turns
# the gate into noise - which is worse than having no gate, because noise teaches people to
# ignore failures. Bare names such as PyRate.py are run-time artefacts, not bundle paths.
MD_LINK = re.compile(r"\[(?:[^\]]*)\]\(([^)\s#]+)[^)]*\)")
IMG = re.compile(r"!\[[^\]]*\]\(([^)\s#]+)[^)]*\)")
CONTENT_EXT = (".md", ".sh", ".txt", ".R", ".bat", ".r")
TOOL_EXT = (".py",)
SCAN_EXT = CONTENT_EXT + TOOL_EXT

# Only the authoring machine's own prefixes count as leaks. The corpus legitimately contains
# generic examples such as /home/user/PyRate-main/, which must survive verbatim.
SKIP_TOKEN_CHARS = ("*", "?", "$", "{", "}", "<", ">")


def leaks_to_reject(root):
    # Detect authoring-machine absolute paths that should not appear in skill
    # content or scripts.  The home directory is always checked.  Additionally,
    # if this script is running from inside a home-directory tree (the typical
    # authoring setup), the parent path components above the suite root are
    # also checked — this catches paths like /home/user/... or
    # /data/user/... that were embedded during authoring on that machine.
    out = [os.path.expanduser("~")]
    home = os.path.expanduser("~")
    if home and home != "/":
        out.append(home)
    # Also derive a machine-specific prefix from the suite root itself: the
    # first few path components (everything up to and including the user's
    # home) are the authoring-machine paths that must not leak.
    abspath = os.path.abspath(root)
    parts = abspath.split(os.sep)
    if len(parts) > 2 and parts[1] in ("home", "data", "Users", "mnt", "opt"):
        # Build the machine-specific prefix (e.g. /home/user or /data/user)
        prefix = os.sep + os.path.join(*parts[1:3])
        out.append(prefix)
    return [x for x in dict.fromkeys(out) if x and x != root]


def walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git")]
        for f in filenames:
            if f.endswith(SCAN_EXT):
                yield os.path.join(dirpath, f)


def ref_candidates(path, root):
    """Yield (lineno, rel_path, token) for every live embed/link in a Markdown file."""
    if not path.endswith(".md"):
        return
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except OSError:
        return
    rel = os.path.relpath(path, root).replace(os.sep, "/")
    for i, line in enumerate(lines, 1):
        for m in list(IMG.finditer(line)) + list(MD_LINK.finditer(line)):
            tok = m.group(1).strip().strip("<>").rstrip(".,;:")
            if not tok or tok.startswith(("http://", "https://", "mailto:", "#", "//")) or \
                    "://" in tok or any(c in tok for c in SKIP_TOKEN_CHARS):
                continue
            yield i, rel, tok


def resolve(tok, md_path, root):
    """Anchor a token the way a reader would. Inside `pyrate-des/SKILL.md`, a relative path is
    resolved from `pyrate-des/` - so a bare `assets/images/` path is broken there even though
    the same file exists under the suite root, and the correct form is `../assets/images/`.
    Falling back to the suite root would accept the wrong form and hide exactly the defect
    class this gate is for. Only a token whose first component is another skill directory is
    additionally tried from the suite root (cross-skill references)."""
    skill_dir = os.path.dirname(md_path)
    head = tok.split("/")[0]
    bases = [skill_dir]
    if head != os.path.basename(skill_dir) and os.path.isdir(os.path.join(root, head)):
        bases.append(root)
    for base in bases:
        cand = os.path.normpath(os.path.join(base, tok))
        if os.path.exists(cand):
            return True, cand
    return False, os.path.normpath(os.path.join(bases[0], tok))


def scan(root):
    """Return (missing, leaked_content, leaked_tooling).
    Content is everything an agent reads or runs out of an installed skill; it must not name
    the authoring machine. The audit_*.py gates are development tooling that legitimately
    needs the documentation corpus next to it, so a path there is reported separately rather
    than failing an otherwise installable bundle."""
    missing, leaked_content, leaked_tooling = [], [], []
    bad_prefixes = leaks_to_reject(root)
    for path in walk(root):
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        is_tool = rel.startswith("scripts/audit_")
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError as exc:
            missing.append("%s :: unreadable (%s)" % (rel, exc))
            continue
        for pre in bad_prefixes:
            for i, line in enumerate(text.splitlines(), 1):
                if pre in line:
                    hit = "%s:%d :: %s :: %s" % (rel, i, pre, line.strip()[:110])
                    (leaked_tooling if is_tool else leaked_content).append(hit)
        for i, rel_md, tok in ref_candidates(path, root):
            ok, where = resolve(tok, path, root)
            if not ok:
                missing.append("%s:%d :: %s does not resolve (tried %s)"
                               % (rel_md, i, tok, os.path.relpath(where, root)))
    return missing, leaked_content, leaked_tooling


def run_self_testing_scripts(root):
    """Every script in the bundle that advertises --self-test must pass from this location.

    Exception: audit_tutorial_runs.py requires a real PyRate source tree and a
    Python runtime with numpy/scipy installed (see its own header).  That
    environment is never available in an install copy, so running its
    --self-test there would always fail for environmental reasons unrelated to
    portability — the gate would report a defect that is not a defect.  The
    script is therefore skipped here; its --self-test is still exercised when
    the gate is run in the source tree with --tree and --env provided.
    """
    bad, ran = [], []
    for path in walk(root):
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        if not rel.endswith(".py") or "/scripts/" not in "/%s" % rel:
            continue
        # Skip the one gate that needs an external PyRate source tree.
        if os.path.basename(rel) == "audit_tutorial_runs.py":
            continue
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                if "--self-test" not in fh.read():
                    continue
        except OSError:
            continue
        # -B: a rehearsal that leaves __pycache__/*.pyc inside the copy would be creating,
        # in the installed location, the very build junk it is meant to prove absent
        # (compiled bytecode also carries the path of the machine that wrote it).
        r = subprocess.run([sys.executable, "-B", path, "--self-test"],
                           capture_output=True, text=True, timeout=600,
                           cwd=os.path.dirname(os.path.dirname(path)))
        ran.append(rel)
        if r.returncode != 0:
            tail = (r.stdout.strip().splitlines() or r.stderr.strip().splitlines())[-3:]
            bad.append("%s exited %d :: %s" % (rel, r.returncode, " / ".join(tail)))
    return bad, ran


def _report(title, findings, limit=12):
    for f in findings[:limit]:
        print("FAIL  %s" % f)
    if len(findings) > limit:
        print("FAIL  ... and %d more" % (len(findings) - limit))
    print("%s  %s: %d" % ("FAIL" if findings else "ok", title, len(findings)))
    return len(findings)


def audit(root):
    fails = 0
    missing, leaked, tool_paths = scan(root)
    print("== path portability (%s) ==" % root)
    fails += _report("authoring-path leak(s) in skill content", leaked)
    fails += _report("unresolved embed/link reference(s)", missing)
    if tool_paths:
        print("\nWARN  %d authoring path(s) inside scripts/audit_*.py tooling: the gates need "
              "the documentation corpus next to the bundle, so they cannot run from an "
              "install of the skills alone. The skills themselves are unaffected."
              % len(tool_paths))
        for f in tool_paths[:6]:
            print("WARN    %s" % f)

    # The rehearsal itself: copy the whole bundle elsewhere and re-check. Nothing in a skills
    # bundle may depend on where it was built.
    tmp = tempfile.mkdtemp(prefix="pyrate_skills_install_")
    try:
        dest = os.path.join(tmp, ".qoder", "skills", "PyRate-skills")
        shutil.copytree(root, dest,
                        ignore=shutil.ignore_patterns("__pycache__", ".git"))
        m2, l2, _t2 = scan(dest)
        print("\n== installed-location rehearsal (%s) ==" % os.path.relpath(dest, tmp))
        # Only findings that appear in the copy but not at the source are location bugs; the
        # rest were already counted above and must not be double-charged.
        only_m = [x for x in m2 if x not in missing]
        only_l = [x for x in l2 if x not in leaked]
        fails += _report("leak(s) that appear only once installed", only_l)
        fails += _report("reference(s) that break only once installed", only_m)

        gate = os.path.join(dest, "scripts", "audit_recipes.py")
        if os.path.exists(gate):
            r = subprocess.run([sys.executable, "-B", gate, dest],
                               capture_output=True, text=True,
                               timeout=1800, cwd=dest)
            print("%s  documented recipes from the copy: exit %d :: %s"
                  % ("FAIL" if r.returncode else "ok", r.returncode,
                     (r.stdout.strip().splitlines() or [""])[-1]))
            fails += 1 if r.returncode else 0
        bad, ran = run_self_testing_scripts(dest)
        for f in bad:
            print("FAIL  %s" % f)
        fails += len(bad)
        print("%s  %d self-testing script(s) run from the copy, %d failure(s)"
              % ("FAIL" if bad else "ok", len(ran), len(bad)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\nRESULT: %s" % ("PASS" if fails == 0 else "FAIL (%d)" % fails))
    return 1 if fails else 0


def self_test():
    """Break a copy in the two ways this gate exists to catch, and require both to be
    reported. A portability gate that has never been seen to fail is not evidence."""
    src = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tmp = tempfile.mkdtemp(prefix="audit_install_selftest_")
    ok = True
    try:
        root = os.path.join(tmp, "skills", "PyRate-skills")
        shutil.copytree(src, root, ignore=shutil.ignore_patterns("__pycache__", ".git"))
        base_m, base_l, _b = scan(root)
        # Assembled at run time: a literal of that shape anywhere in this file would be read
        # by the corpus auditor as a figure the suite references but does not ship.
        needle = "no-such-figure." + "png"
        victim = os.path.join(root, "pyrate-bd-analysis", "SKILL.md")
        with open(victim, "a", encoding="utf-8") as fh:
            # Use a path that leaks_to_reject() will catch on any machine:
            # the home directory is always in the reject list, so embedding
            # an absolute path under it tests the detection.
            leak_path = os.path.join(os.path.expanduser("~"), "somewhere", "PyRate.py")
            fh.write("\nRun `%s`, as the figure below "
                     "shows:\n\n![a rate plot](../assets/images/%s)\n" % (leak_path, needle))
        m, l, _ = scan(root)
        if len(l) <= len(base_l):
            print("self-test: FAILED to detect a planted authoring-machine path")
            ok = False
        if not any(needle in x for x in m):
            print("self-test: FAILED to detect a planted broken image embed")
            ok = False
        if len(m) <= len(base_m):
            print("self-test: the planted broken embed did not increase the missing set")
            ok = False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if not ok:
        print("audit_install.py self-test: FAILED - the gate does not detect what it claims")
        return 1
    print("audit_install.py self-test: OK (planted absolute-path leak and planted broken "
          "image embed both detected)")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        sys.exit(self_test())
    sys.exit(audit(os.path.abspath(a.root or
                  os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
