#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_env.py — detect a usable PyRate runtime on this machine.

Part of the PyRate-skills suite (skill: pyrate-command-reference).
Python 3 standard library only. Deterministic, no network access, no eval/exec.

WHAT PYRATE NEEDS (corpus citations; line numbers include mirror frontmatter):
  * PyRate runs from the command line as `python PyRate.py <input> [commands]`
    (references/command-list.md:15).
  * The program files PyRate.py / PyRateContinuous.py / PyRateDES.py / PyRateMCDD.py
    ship in the PyRate package, together with the library `pyrate_lib` that must sit
    next to them (../pyrate-installation/references/virtual-environment.md:52 paths
    into pyrate_lib/fastPyRateC/, confirming adjacency; the "library pyrate_lib"
    requirement is also echoed in ../pyrate-summarize-results/references/tutorial-2.md:24).
  * `-plot` shells out to R: "The script is automatically executed by PyRate using
    the shell command `RScript`" (../pyrate-installation/references/virtual-environment.md:55).
  * Dependencies install route:
    `python -m pip install -r your_path/PyRate-master/requirements.txt`
    (../pyrate-installation/references/virtual-environment.md:44); sanity check
    `python your_path/PyRate-master/PyRate.py -v` (same file, line 49).
  * CORPUS CONFLICT about the interpreter: the classic PyRate 2014 release line
    targets Python 2.6-2.7 (suite grounding), but the mirrored venv tutorial says
    "make sure **Python (v.3.10 or higher)** is installed"
    (../pyrate-installation/references/virtual-environment.md:13). This checker
    probes BOTH a python2 candidate (python2, python2.7) and a python3 candidate
    and reports each separately instead of silently picking one reading.
  * numpy / scipy / argparse are named requirements in the suite grounding; the
    wiki command list itself never re-lists them (documented gap, not invented here).

USAGE
  python3 check_env.py [--pyrate-dir PATH ...] [--json] [--self-test]
                       [--timeout SECONDS] [--python2 PATH] [--python3 PATH]

WHAT IT PRINTS
  One `[PASS|FAIL|WARN|SKIP]` verdict line per check: python2 interpreter,
  python3 interpreter, importability of numpy/scipy/argparse on each usable
  interpreter, Rscript on PATH, the four PyRate program files, adjacent
  pyrate_lib. Then a `Remediation (single most useful fix):` line for the first
  failure, a per-failure remediation list, and a final `VERDICT:` line. With
  --json the same data is one JSON object. Output is bounded (< 60 lines).

EXIT CODES
  0 usable runtime detected, 1 not usable / --self-test failure detail on stdout,
  2 bad usage, 3 internal I/O error.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

MODULES = ("numpy", "scipy", "argparse")
PROGRAMS = ("PyRate.py", "PyRateContinuous.py", "PyRateDES.py", "PyRateMCDD.py")
VERSION_PROBE = "import sys; sys.stdout.write('PYRATE_VER %d' % sys.version_info[0])"

REMEDY = {
    "python2": ("Install a Python 2.7 interpreter or build one in a virtualenv, e.g. "
                "`conda create -n pyrate27 python=2.7` (classic PyRate 2.6-2.7 line); note "
                "the mirrored upstream venv tutorial instead targets Python >= 3.10 "
                "(../pyrate-installation/references/virtual-environment.md:13)."),
    "python3": ("Install Python 3.10+ per "
                "../pyrate-installation/references/virtual-environment.md:13 "
                "(python.org) — current upstream PyRate installs inside a venv."),
    "module": ("Activate the PyRate environment and run `python -m pip install -r "
               "your_path/PyRate-master/requirements.txt` "
               "(../pyrate-installation/references/virtual-environment.md:44)."),
    "rscript": ("Install R and put the folder containing Rscript on PATH — the -plot "
                "script 'is automatically executed by PyRate using the shell command "
                "`RScript`' (../pyrate-installation/references/virtual-environment.md:55)."),
    "programs": ("Download the PyRate package and point this checker at it, e.g. "
                 "`python3 check_env.py --pyrate-dir /path/to/PyRate-master` (invocation "
                 "form: `python PyRate.py <input file> [commands]`, "
                 "references/command-list.md:15)."),
    "pyrate_lib": ("Unpack the full PyRate distribution so that the library folder "
                   "`pyrate_lib` sits next to PyRate.py "
                   "(../pyrate-installation/references/virtual-environment.md:52)."),
}


def _run(cmd, timeout):
    """Run argv (never via shell); return (rc, combined output text) or (None, msg)."""
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           timeout=timeout)
        return p.returncode, p.stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return None, "timed out after %ss" % timeout
    except FileNotFoundError:
        return None, "executable not found"
    except OSError:
        return None, "OS error while spawning probe"


def _which(name, env_path=None):
    return shutil.which(name, path=env_path)


def probe_interpreter(exe, timeout):
    """Return {'exe','found','major','version_note'} for a candidate interpreter."""
    out = {"exe": exe, "found": exe is not None, "major": None, "version_note": ""}
    if not exe:
        out["version_note"] = "not found on PATH"
        return out
    rc, text = _run([exe, "-c", VERSION_PROBE], timeout)
    if rc == 0 and "PYRATE_VER" in text:
        try:
            out["major"] = int(text.split("PYRATE_VER")[1].split()[0])
        except (IndexError, ValueError):
            out["version_note"] = "version probe output unparseable"
    else:
        out["version_note"] = "does not execute (-c probe failed)"
    return out


def probe_module(exe, module, timeout):
    """True/False importability of `module` under `exe`, plus last error line."""
    rc, text = _run([exe, "-c", "import %s" % module], timeout)
    if rc == 0:
        return True, "imports OK"
    detail = (text.strip().splitlines() or ["import failed"])[-1][:120]
    return False, "import failed: %s" % detail


def find_programs(search_dirs):
    """Locate PyRate program files in search_dirs and a pyrate_lib adjacent to one."""
    found = {}
    for name in PROGRAMS:
        for d in search_dirs:
            cand = os.path.join(d, name)
            if os.path.isfile(cand):
                found[name] = cand
                break
    lib_dir = None
    bases = sorted({os.path.dirname(p) for p in found.values()})
    for base in bases:
        cand = os.path.join(base, "pyrate_lib")
        if os.path.isdir(cand):
            lib_dir = cand
            break
    return found, lib_dir


def detect(pyrate_dirs, env_path=None, python2_override=None, python3_override=None,
           timeout=20.0):
    """Run all checks. Returns (checks, ok, verdict, top_remediation).

    checks: list of {name, status, detail, remedy}; deterministic PATH lookups,
    os.path tests and bounded subprocess probes only.
    """
    checks = []

    def add(name, status, detail, remedy=""):
        checks.append({"name": name, "status": status, "detail": detail, "remedy": remedy})

    # 1. python2 interpreter (classic PyRate line)
    py2 = python2_override
    if py2 is not None and not os.path.exists(py2):
        py2 = None
    if py2 is None:
        py2 = _which("python2", env_path) or _which("python2.7", env_path)
    py2_info = probe_interpreter(py2, timeout)
    if py2_info["found"] and py2_info["major"] == 2:
        add("python2 interpreter", "PASS", "%s (python 2.x)" % py2_info["exe"])
    elif py2_info["found"]:
        add("python2 interpreter", "FAIL",
            "python2/python2.7 resolved to a non-2.x interpreter: %s (%s)"
            % (py2_info["exe"], py2_info["version_note"]), REMEDY["python2"])
    else:
        add("python2 interpreter", "FAIL",
            "no python2 / python2.7 found on PATH (needed by the classic PyRate 2.6-2.7 line)",
            REMEDY["python2"])

    # 2. python3 interpreter (mirrored venv tutorial targets >= 3.10)
    py3 = python3_override
    if py3 is not None and not os.path.exists(py3):
        py3 = None
    if py3 is None:
        py3 = _which("python3", env_path)
    py3_info = probe_interpreter(py3, timeout)
    py3_ok = bool(py3_info["found"] and py3_info["major"] == 3)
    if py3_ok:
        add("python3 interpreter", "PASS",
            "%s (python 3.x; docs target >= 3.10, virtual-environment.md:13)"
            % py3_info["exe"])
    else:
        add("python3 interpreter", "FAIL",
            "no usable python3 found (%s)" % py3_info["version_note"], REMEDY["python3"])

    # 3. module importability on every usable interpreter (python2 first)
    interps = []
    if py2_info["major"] == 2:
        interps.append((py2_info["exe"], "python2"))
    if py3_ok:
        interps.append((py3_info["exe"], "python3"))
    if not interps:
        for mod in MODULES:
            add("import %s" % mod, "SKIP", "no usable interpreter to probe",
                REMEDY["python2"])
    else:
        for exe, tag in interps:
            for mod in MODULES:
                ok_imp, detail = probe_module(exe, mod, timeout)
                add("import %s (%s: %s)" % (mod, tag, os.path.basename(exe)),
                    "PASS" if ok_imp else "FAIL", detail,
                    "" if ok_imp else REMEDY["module"])

    # 4. Rscript on PATH (-plot/-plot2/-ginput plotting shell out to it)
    rscript = _which("Rscript", env_path)
    if rscript:
        rc, text = _run([rscript, "--version"], timeout)
        first = (text.strip().splitlines() or [""])[0][:80]
        add("Rscript on PATH", "PASS" if rc == 0 else "WARN",
            "%s%s" % (rscript, (" — " + first) if first else ""))
    else:
        add("Rscript on PATH", "FAIL",
            "Rscript not found; plotting commands shell out to it (virtual-environment.md:55)",
            REMEDY["rscript"])

    # 5. PyRate program files + adjacent pyrate_lib
    found, lib_dir = find_programs(pyrate_dirs)
    searched = ", ".join(pyrate_dirs) if pyrate_dirs else "<no search dirs>"
    for name in PROGRAMS:
        if name in found:
            add(name, "PASS", found[name])
        elif name == "PyRate.py":
            add(name, "FAIL", "core program not found (searched: %s)" % searched,
                REMEDY["programs"])
        else:
            add(name, "WARN", "not found (searched: %s) — only needed for that program "
                "variant" % searched)
    if lib_dir:
        add("pyrate_lib adjacent", "PASS", lib_dir)
    else:
        add("pyrate_lib adjacent",
            "FAIL" if "PyRate.py" in found else "SKIP",
            "no pyrate_lib directory next to any found program" if "PyRate.py" in found
            else "PyRate.py itself was not found, so adjacency cannot be judged",
            REMEDY["pyrate_lib"])

    # Aggregate: a runtime is usable if some interpreter passes AND numpy+scipy+argparse
    # import on it. Programs (PyRate.py + pyrate_lib) missing is separately blocking.
    usable = False
    for _exe, tag in interps:
        mod_ok = all(c["status"] == "PASS" for c in checks
                     if c["name"].startswith("import ") and ("(%s:" % tag) in c["name"])
        if mod_ok:
            usable = True
    progs_ok = ("PyRate.py" in found) and bool(lib_dir)
    progs_ok = ("PyRate.py" in found) and bool(lib_dir)
    ok = usable and progs_ok
    fails = [c for c in checks if c["status"] == "FAIL"]
    top = pick_top_remediation(checks, usable, progs_ok, interps) or ""
    if not ok and not top:
        top = REMEDY["programs"] if usable else REMEDY["python2"]
    verdict = ("VERDICT: usable PyRate runtime detected" if ok
               else "VERDICT: no usable PyRate runtime detected")
    return checks, ok, verdict, top


def pick_top_remediation(checks, usable, progs_ok, interps):
    """Single most useful fix: interpreter first, then missing deps, then package files."""
    fails = [c for c in checks if c["status"] == "FAIL"]
    if not interps and not usable:
        return REMEDY["python2"]
    if not usable:
        mod_fail = next((c for c in fails if c["name"].startswith("import ")), None)
        if mod_fail:
            return mod_fail["remedy"] or REMEDY["module"]
        return REMEDY["python2"]
    if not progs_ok:
        lib_fail = next((c for c in fails if c["name"] == "pyrate_lib adjacent"), None)
        if lib_fail:
            return lib_fail["remedy"]
        return REMEDY["programs"]
    return fails[0]["remedy"] if fails else ""


def default_search_dirs(cli_dirs):
    """CLI dirs first, then $PYRATE_DIR, then cwd and ./PyRate-master; existing only."""
    dirs = list(cli_dirs)
    env_dir = os.environ.get("PYRATE_DIR")
    if env_dir:
        dirs.append(env_dir)
    dirs.append(os.getcwd())
    dirs.append(os.path.join(os.getcwd(), "PyRate-master"))
    out, seen = [], set()
    for d in dirs:
        d = os.path.abspath(d)
        if d not in seen and os.path.isdir(d):
            seen.add(d)
            out.append(d)
    return out


def format_lines(checks, ok, verdict, top_remediation):
    """Bounded human-readable report (one line per check)."""
    lines = ["PyRate environment check (offline, deterministic, stdlib-only helper)"]
    for c in checks:
        lines.append("[%s] %-38s %s" % (c["status"], c["name"], c["detail"]))
    if top_remediation:
        lines.append("Remediation (single most useful fix): %s" % top_remediation)
    per_fail = ["  - %s: %s" % (c["name"], c["remedy"])
                for c in checks if c["status"] == "FAIL" and c["remedy"]]
    if per_fail:
        lines.append("Remediations for every failed check:")
        lines.extend(per_fail)
    lines.append(verdict + " — docs conflict note: classic PyRate targets Python 2.6-2.7 "
                 "while the mirrored venv tutorial requires >= 3.10 (see docstring).")
    return lines


# ---------------------------------------------------------------- self-test fixtures

def _mk_fake_bin(tmp, numpy_ok=True, scipy_ok=False, major=2):
    """Deterministic shell shims acting as a fake python2/python3 + Rscript."""
    bin_dir = os.path.join(tmp, "bin")
    os.makedirs(bin_dir, exist_ok=True)
    shim = (
        "#!/bin/sh\n"
        "code=\"$2\"\n"
        "case \"$code\" in\n"
        "  *PYRATE_VER*) echo \"PYRATE_VER %d\" ;;\n"
        "  *\"import numpy\"*)    [ \"%s\" = ok ] && exit 0 || exit 1 ;;\n"
        "  *\"import scipy\"*)    [ \"%s\" = ok ] && exit 0 || exit 1 ;;\n"
        "  *\"import argparse\"*) exit 0 ;;\n"
        "  *) exit 1 ;;\n"
        "esac\n"
    ) % (major, "ok" if numpy_ok else "no", "ok" if scipy_ok else "no")
    name = "python2" if major == 2 else "py2named3"
    path = os.path.join(bin_dir, name)
    with open(path, "w") as fh:
        fh.write(shim)
    os.chmod(path, 0o755)
    with open(os.path.join(bin_dir, "Rscript"), "w") as fh:
        fh.write("#!/bin/sh\necho 'R scripting front-end 4.0.0 (fake)'\nexit 0\n")
    os.chmod(os.path.join(bin_dir, "Rscript"), 0o755)
    return bin_dir, name


def self_test():
    errors = []

    tally = [0]

    def expect(cond, msg):
        tally[0] += 1
        if not cond:
            errors.append(msg)

    tmp = tempfile.mkdtemp(prefix="check_env_selftest_")
    try:
        pkg = os.path.join(tmp, "PyRate-master")
        os.makedirs(os.path.join(pkg, "pyrate_lib"))
        for prog in ("PyRate.py", "PyRateMCDD.py"):
            with open(os.path.join(pkg, prog), "w") as fh:
                fh.write("# fake program for self-test only — never executed\n")

        # Case 1: fake python2 (numpy ok, scipy missing) + fake Rscript + fake package
        bin_dir, _ = _mk_fake_bin(tmp, numpy_ok=True, scipy_ok=False, major=2)
        fake_path = bin_dir + os.pathsep + tmp  # no real python3 in this PATH
        checks, ok, verdict, top = detect([pkg], env_path=fake_path)
        by = {c["name"]: c for c in checks}
        expect(by["python2 interpreter"]["status"] == "PASS",
               "case1: fake python2 not detected")
        expect(by["import numpy (python2: python2)"]["status"] == "PASS",
               "case1: numpy PASS not recorded")
        expect(by["import scipy (python2: python2)"]["status"] == "FAIL",
               "case1: scipy FAIL not recorded")
        expect(by["import argparse (python2: python2)"]["status"] == "PASS",
               "case1: argparse PASS not recorded")
        expect(by["python3 interpreter"]["status"] == "FAIL",
               "case1: python3 should be absent from the fake PATH")
        expect(by["Rscript on PATH"]["status"] == "PASS", "case1: fake Rscript missed")
        expect(by["PyRate.py"]["status"] == "PASS", "case1: PyRate.py not found")
        expect(by["PyRateDES.py"]["status"] == "WARN", "case1: missing variant should WARN")
        expect(by["pyrate_lib adjacent"]["status"] == "PASS", "case1: pyrate_lib missed")
        expect(ok is False, "case1: runtime must be judged NOT usable while scipy fails")
        expect(top == REMEDY["module"], "case1: wrong top remediation: %r" % top)
        json.dumps({"checks": checks, "ok": ok})  # serializability
        out = format_lines(checks, ok, verdict, top)
        expect(len(out) < 60, "case1: output exceeds 60 lines")

        # Case 2: nothing at all — every detection fails, still bounded + single verdict
        empty = os.path.join(tmp, "empty")
        os.makedirs(empty, exist_ok=True)
        checks2, ok2, verdict2, top2 = detect([empty], env_path=empty)
        expect(ok2 is False, "case2: must fail")
        expect(any(c["name"].startswith("import ") and c["status"] == "SKIP"
                   for c in checks2), "case2: module checks should SKIP with no interpreter")
        expect(bool(top2), "case2: top remediation mandatory when not ok")
        expect(len(format_lines(checks2, ok2, verdict2, top2)) < 60,
               "case2: output not bounded")
        expect(all(c["status"] != "PASS" for c in checks2 if c["name"] in PROGRAMS),
               "case2: no program may PASS in an empty directory")

        # Case 3: a 'python2' that is really python 3 must be rejected for the 2.x slot
        bin3, name3 = _mk_fake_bin(os.path.join(tmp, "t3"), numpy_ok=True,
                                   scipy_ok=True, major=3)
        os.rename(os.path.join(bin3, name3), os.path.join(bin3, "python2"))
        checks3, _, _, _ = detect([pkg], env_path=bin3 + os.pathsep + tmp)
        by3 = {c["name"]: c for c in checks3}
        expect(by3["python2 interpreter"]["status"] == "FAIL",
               "case3: non-2.x binary named python2 must FAIL the python2 check")

        # Case 4: full pass through the python3 route (shim major=3, scipy ok,
        # binary legitimately named python3)
        bin4 = os.path.join(tmp, "bin4")
        os.makedirs(bin4, exist_ok=True)
        shim4 = ("#!/bin/sh\ncase \"$2\" in\n"
                 "  *PYRATE_VER*) echo 'PYRATE_VER 3' ;;\n"
                 "  *) exit 0 ;;\nesac\n")
        with open(os.path.join(bin4, "python3"), "w") as fh:
            fh.write(shim4)
        os.chmod(os.path.join(bin4, "python3"), 0o755)
        with open(os.path.join(bin4, "Rscript"), "w") as fh:
            fh.write("#!/bin/sh\nexit 0\n")
        os.chmod(os.path.join(bin4, "Rscript"), 0o755)
        checks4, ok4, verdict4, _ = detect([pkg], env_path=bin4 + os.pathsep + tmp)
        expect(ok4 is True, "case4: python3 route with all modules should be usable: %r"
               % [c for c in checks4 if c["status"] != "PASS"])
        expect(verdict4.startswith("VERDICT: usable"), "case4: wrong verdict")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if errors:
        for e in errors:
            print("SELF-TEST FAIL: %s" % e)
        return 1
    print("check_env.py self-test: OK (%d assertions on temp interpreter shims, "
          "no real interpreters required)" % tally[0])
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="check_env.py",
        description="Detect a usable PyRate runtime (offline, stdlib-only).")
    ap.add_argument("--pyrate-dir", action="append", default=[], metavar="PATH",
                    help="directory to search for PyRate.py etc. (repeatable; $PYRATE_DIR "
                         "and the current directory are searched too)")
    ap.add_argument("--json", action="store_true",
                    help="emit one JSON object instead of the text report")
    ap.add_argument("--self-test", action="store_true",
                    help="build temp fixtures and assert detection behaviour")
    ap.add_argument("--timeout", type=float, default=20.0, metavar="SECONDS",
                    help="per-subprocess probe timeout, (0, 120] (default 20)")
    ap.add_argument("--python2", metavar="PATH", help="explicit python2 interpreter path")
    ap.add_argument("--python3", metavar="PATH", help="explicit python3 interpreter path")
    try:
        args = ap.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if exc.code else 0

    if args.self_test:
        return self_test()
    if not (0 < args.timeout <= 120):
        print("error: --timeout must be in (0, 120] seconds", file=sys.stderr)
        return 2
    dirs = default_search_dirs(args.pyrate_dir)
    try:
        checks, ok, verdict, top = detect(dirs, python2_override=args.python2,
                                          python3_override=args.python3,
                                          timeout=args.timeout)
    except OSError:
        print("error: I/O failure during detection", file=sys.stderr)
        return 3
    if args.json:
        print(json.dumps({"ok": ok, "verdict": verdict, "search_dirs": dirs,
                          "checks": checks, "top_remediation": top},
                         ensure_ascii=False, indent=1))
    else:
        for line in format_lines(checks, ok, verdict, top):
            print(line)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
