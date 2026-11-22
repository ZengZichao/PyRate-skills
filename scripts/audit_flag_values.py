#!/usr/bin/env python3
"""Check that the numeric arguments in the suite's worked examples are the numbers the
documentation actually uses.

Why: every other gate compares the suite against the mirrors (text fidelity). Nothing compared
the *example parameters* - the `-n`, `-b`, `-s` values an agent will copy into a real analysis.
An invented value can be silently catastrophic rather than merely unsourced: PyRateContinuous
defines `-b` as a number of SAMPLES ("the number of samples excluded is set with the command
`-b`", 4.-PyRateContinuous.md:7) while the command list defines it as ITERATIONS
(command-list.md:69), so an example pairing `-n 1000000 -s 1000` (1 000 logged samples) with
`-b 200000` discards the entire chain under one definition and 20% of it under the other.
The documentation corpus is the only authority for these numbers, so anything else must either
match the corpus or say out loud that it is illustrative.

    python3 scripts/audit_flag_values.py                 # audit the suite next to this script
    python3 scripts/audit_flag_values.py --corpus DIR    # against a different corpus
    python3 scripts/audit_flag_values.py --self-test     # prove the gate detects planted values

Exit 0 only if every numeric example parameter is corpus-attested, marked illustrative on its
own line, or at least arithmetically survivable.
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile

SUITE_DEFAULT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS_DEFAULT = os.path.join(os.path.dirname(SUITE_DEFAULT), "PyRate-doc")

NUM = r"\d+(?:\.\d+)?"
FLAG_VALUE = re.compile(r"(?<![\w-])-([A-Za-z][A-Za-z0-9_]*)[= ](?=%s)(%s)(?![\d.])" % (NUM, NUM))
FENCE = re.compile(r"^```(?:sh|bash|console|text)?\s*(.*?)^```", re.S | re.M)
# A value the author marks as arbitrary is honest, so long as the mark is on the same line as
# the command - a disclaimer three paragraphs away will not survive a copy-paste.
ILLUSTRATIVE = re.compile(r"illustrativ|arbitrary|placeholder|not from the docs|any number|"
                          r"pick a value|your own|adjust to|e\.g\. with", re.I)
def md_files(root, only_skill_md=False):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git")]
        if only_skill_md and "SKILL.md" not in filenames:
            continue
        for f in sorted(filenames):
            if f == "SKILL.md" if only_skill_md else f.endswith(".md"):
                p = os.path.join(dirpath, f)
                if "references" in dirpath.split(os.sep) and only_skill_md:
                    continue
                yield p


def values_by_flag(root):
    """flag -> set of numeric strings the documentation uses for it."""
    out = {}
    for path in md_files(root):
        with open(path, encoding="utf-8", errors="replace") as fh:
            for m in FLAG_VALUE.finditer(fh.read()):
                out.setdefault(m.group(1), set()).add(m.group(2))
    return out


def commands_in(text):
    """Yield (lineno, command) for every shell invocation of a PyRate program inside a fenced
    block. Prose, table cells and commented-out echoes are skipped on purpose: a hazard table
    that discusses `-nT 0` is not an example an agent will copy, and judging it would bury the
    findings that matter in noise. Continuation lines are joined so that `-n`, `-s` and `-b`
    written on three lines are still read as one chain."""
    out = []
    for block in FENCE.finditer(text):
        base = text.count("\n", 0, block.start()) + 1
        logical, start, buf = [], None, []
        for offset, raw in enumerate(block.group(1).splitlines(), start=base + 1):
            if not raw.strip() or raw.lstrip().startswith("#"):
                continue
            buf.append(raw.rstrip("\\").rstrip())
            if raw.rstrip().endswith("\\"):
                if start is None:
                    start = offset
                continue
            out.append((start or offset, " ".join(buf)))
            start, buf = None, []
        if buf:
            out.append((start, " ".join(buf)))
    return [(n, c) for n, c in out if re.search(r"PyRate\w*\.py", c)]


def audit(suite, corpus):
    doc = values_by_flag(corpus)
    fails, infos, judged = [], [], 0
    b_values = doc.get("b", set())
    for path in md_files(suite, only_skill_md=True):
        rel = os.path.relpath(path, suite).replace(os.sep, "/")
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        for lineno, cmd in commands_in(text):
            marks = ILLUSTRATIVE.search(cmd)
            seen = set()
            for m in FLAG_VALUE.finditer(cmd):
                flag, val = m.group(1), m.group(2)
                if (flag, val) in seen:
                    continue
                seen.add((flag, val))
                if flag not in doc:
                    continue
                judged += 1
                if val in doc[flag] or marks:
                    continue
                # Only -b is failure-worthy: the two documentation pages disagree about whether
                # it counts samples or iterations, so an invented -b is the one value that can
                # silently void a run. Other knobs are free choice -> reported, not failed.
                if flag == "b":
                    fails.append("%s:%d :: `-b %s` appears in no example in the documentation "
                                 "(it uses: %s), and -b's unit is contested between "
                                 "4.-PyRateContinuous.md:7 (samples) and command-list.md:69 "
                                 "(iterations)" % (rel, lineno, val,
                                                   ", ".join(sorted(b_values, key=float))))
                else:
                    infos.append("%s:%d :: -%s %s is not a value the documentation uses (it "
                                 "uses: %s)" % (rel, lineno, flag, val,
                                                ", ".join(sorted(doc[flag], key=float)[:8])))
            n = re.search(r"(?<![\w-])-n (?=\d)(\d+)(?!\d)", cmd)
            s = re.search(r"(?<![\w-])-s (?=\d)(\d+)(?!\d)", cmd)
            b = re.search(r"(?<![\w-])-b (?=\d)(\d+)(?!\d)", cmd)
            if n and s and b and int(s.group(1)) and not marks:
                samples = int(n.group(1)) // int(s.group(1))
                if int(b.group(1)) > samples:
                    fails.append("%s:%d :: `-b %s` exceeds the %d samples this chain logs "
                                 "(-n %s / -s %s); on the Continuous page's reading of -b "
                                 "(samples) it discards the entire run"
                                 % (rel, lineno, b.group(1), samples, n.group(1), s.group(1)))
    print("%d flag/value pair(s) in PyRate example commands judged against the documentation"
          % judged)
    for f in infos:
        print("INFO  %s" % f)
    for f in fails:
        print("FAIL  %s" % f)
    print("\n%d unattested -b value(s) or dead chain(s), %d informational value(s)"
          % (len(fails), len(infos)))
    print("RESULT: %s" % ("PASS" if not fails else "FAIL (%d)" % len(fails)))
    return 1 if fails else 0


def self_test():
    """The gate must flag an invented value and a dead chain, and must leave a
    corpus-attested value and a marked-illustrative value alone."""
    tmp = tempfile.mkdtemp(prefix="audit_flag_values_selftest_")
    ok = True
    try:
        corpus = os.path.join(tmp, "doc")
        suite = os.path.join(tmp, "skills", "S")
        os.makedirs(corpus)
        os.makedirs(suite)
        with open(os.path.join(corpus, "p.md"), "w") as fh:
            fh.write("`PyRate.py -n 1000001 -s 1000 -b 100`\n")
        with open(os.path.join(corpus, "q.md"), "w") as fh:
            fh.write("`python PyRate.py -n 1000001 -s 1000`\n")
        cases = [
            ("invented -b must be flagged", "PyRate.py -b 777777", True),
            ("dead chain must be flagged", "PyRate.py -n 1000001 -s 1000 -b 999999", True),
            ("corpus value must pass", "PyRate.py -n 1000001 -s 1000 -b 100", False),
            ("marked illustrative must pass", "PyRate.py -b 777777  # illustrative", False),
            ("prose must not be judged", "| hazard | `-b 777777` discards everything |", False),
            ("non-PyRate command must not be judged", "Rscript plot.R -b 777777", False),
            ("continuation lines count as one chain",
             "PyRate.py -n 1000001 -s 1000 \\\n  -b 999999", True),
        ]
        for label, cmd, want_fail in cases:
            body = ("```sh\n%s\n```\n" % cmd) if cmd.startswith(("PyRate", "Rscript")) \
                else cmd + "\n"
            with open(os.path.join(suite, "SKILL.md"), "w") as fh:
                fh.write("---\nname: S\n---\n\n" + body)
            out = subprocess.run([sys.executable, os.path.abspath(__file__),
                                  "--suite", suite, "--corpus", corpus],
                                 capture_output=True, text=True)
            got_fail = out.returncode != 0
            if got_fail != want_fail:
                print("self-test: %s -> exit %d (%s), wanted %s\n%s"
                      % (label, out.returncode, "FAIL" if got_fail else "PASS",
                         "FAIL" if want_fail else "PASS", out.stdout.strip()[:400]))
                ok = False
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    if not ok:
        print("audit_flag_values.py self-test: FAILED")
        return 1
    print("audit_flag_values.py self-test: OK (invented value and dead chain flagged; "
          "corpus value and marked-illustrative value left alone)")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite")
    ap.add_argument("--corpus")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        sys.exit(self_test())
    sys.exit(audit(os.path.abspath(a.suite or SUITE_DEFAULT),
                   os.path.abspath(a.corpus or CORPUS_DEFAULT)))
