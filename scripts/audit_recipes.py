#!/usr/bin/env python3
"""Execute every grep recipe in every SKILL.md and compare reality with the text.

    python3 scripts/audit_recipes.py [--suite-root]     # audit a suite root (default: this one)
    python3 scripts/audit_recipes.py --self-test        # prove each verdict class is detected
    python3 scripts/audit_recipes.py --help

--suite-root exists for negative testing only: self_test() points it at temp fixtures,
and an unrecognised second argument is refused rather than silently taken as a root.

shell=True is deliberate: reproducing what a reader experiences requires real shell
semantics (quoting, pipes, '#' comments). It is safe only because the commands come
from this suite's own SKILL.md files - never from user or corpus input. The '>' filter
that stops the sweep writing files is load-bearing; do not remove or widen it, and do
not reuse this sweep on untrusted markdown.

Each recipe runs with cwd set to the skill directory that declares it, because that is
what makes ../assets/... and ../<sibling>/references/... resolve the way the reader's
will. Running from the suite root instead reports hundreds of bogus failures.

WHAT IT FAILS ON - only claims that are exactly checkable:
  * a recipe that errors (exit >= 2) or times out, unless it is a post-run inspection
    step whose file only the block's own PyRate run creates (reported as INFO, counted);
  * a recipe whose SAME-LINE comment asserts a count ("# 27 command lines", "= 0 hits",
    "# 31") that the real output contradicts - the drift this catches is a doc that
    promises a number the mirrors no longer contain;
  * a recipe whose same-line comment says it matches nothing, but which does match.
WHAT IT ONLY REPORTS (INFO): an empty result with no same-line annotation. "This proves
an absence" and "this is dead" look identical to a machine; a human or agent has to read
the sentence. They are listed, never hidden, and never counted as a failure.
"""

import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # the suite root
_ARGS = [a for a in sys.argv[1:] if a not in ("--self-test", "-t")]
if _ARGS and _ARGS[0] in ("--help", "-h"):
    print(__doc__)
    sys.exit(0)
if len(_ARGS) > 1:
    sys.exit("usage: audit_recipes.py [--suite-root] [--self-test] [--help]")
if _ARGS:                            # an alternate suite root, for negative testing
    ROOT = os.path.abspath(_ARGS[0])
BLOCKS = re.compile(r"^```(?:sh|bash|console)?\s*\n(.*?)^```", re.S | re.M)

# A same-line comment stating a number: "# 27 command lines", "= 0 hits", "# 31;", "# 8 sections"
CLAIM_COUNT = re.compile(r"^(?:=\s*)?(\d+)(?!\s*:)|\b(\d+)\s*(?:hits|matches|lines|sections|"
                         r"headings|occurrences|rows|statements|command lines|files|calls)\b")
# A same-line comment asserting a line number the output should contain: "# 135: ..."
CLAIM_LINE = re.compile(r"^=?\s*(\d+)\s*:")

# A same-line comment stating emptiness.
CLAIM_EMPTY = re.compile(r"\b0 hits\b|prints nothing|prints 0\b|returns 0\b|returns `?0\b|"
                         r"no (?:match|output|hit)s?\b|not on this page|does not occur", re.I)

# Files a real PyRate run produces: grepping one is a post-run step, impossible at rest.
RUN_STEMS = ("_mcmc.log", "_sum.txt", "_se_est.txt", "_se_ext.txt", "_marginal_rates.log",
             "_marginal_likelihood.txt", "_sp_rates.log", "_ex_rates.log", "_RTTplot.pdf",
             "_RTTplot.r")
RUN_LINE = re.compile(r"python3?\s+(\./)?PyRate")


def skills():
    for d in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, d, "SKILL.md")
        if os.path.isdir(os.path.join(ROOT, d)) and os.path.isfile(p):
            yield d, p


def recipes(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    for block in BLOCKS.findall(text):
        lines = block.split("\n")
        runs = bool(RUN_LINE.search(block))
        for line in lines:
            s = line.strip()
            if s.startswith("grep") and ">" not in s:
                yield s, runs


def split_comment(cmd):
    """Return (command, trailing '#' comment) at top level of the line.

    A '#' inside quotes is part of a pattern (grep -n '^### '), so walk the line with
    quoting in mind instead of splitting on the first '#'.
    """
    out = []
    q = None
    i = 0
    while i < len(cmd):
        c = cmd[i]
        if q:
            out.append(c)
            if c == q and (i == 0 or cmd[i - 1] != "\\"):
                q = None
        elif c in "\"'":
            q = c
            out.append(c)
        elif c == "#" and (i == 0 or cmd[i - 1] in " \t"):
            return "".join(out).strip(), cmd[i + 1:].strip()
        else:
            out.append(c)
        i += 1
    return "".join(out).strip(), ""


def claimed_number(comment):
    m = CLAIM_COUNT.search(comment)
    if not m:
        return None
    return int(m.group(1) or m.group(2))


def main():
    ran = fails = infos = 0
    checked_claims = 0
    for skill, path in skills():
        for cmd, block_runs in recipes(path):
            real, comment = split_comment(cmd)
            if not real:
                continue
            ran += 1
            try:
                r = subprocess.run(real, shell=True, cwd=os.path.join(ROOT, skill),
                                   capture_output=True, timeout=120)
            except subprocess.TimeoutExpired:
                print("[TIMEOUT] %s :: %s" % (skill, real))
                fails += 1
                continue
            out = r.stdout.decode("utf-8", "replace").strip()
            err = r.stderr.decode("utf-8", "replace").strip()
            lines = [x for x in out.split("\n") if x.strip()]
            # count of results: -c / -rl / wc -l style output is one number, else one hit a line
            count = int(lines[0]) if len(lines) == 1 and lines[0].strip().isdigit() else len(lines)
            says_empty = bool(CLAIM_EMPTY.search(comment))
            want_line = CLAIM_LINE.match(comment)
            want_line = int(want_line.group(1)) if want_line else None
            says = claimed_number(comment)
            if want_line is not None:
                says = None   # "# 135:" is a line number, not a count

            if r.returncode == 2 and block_runs and any(st in real for st in RUN_STEMS) \
                    and "No such file" in err:
                infos += 1
                print("[INFO post-run step: needs the PyRate run earlier in this block] %s :: %s"
                      % (skill, real))
                continue
            if r.returncode not in (0, 1):
                print("[EXIT %d] %s :: %s\n    %s" % (r.returncode, skill, real, err[:160]))
                fails += 1
                continue
            if says_empty or says is not None or want_line is not None:
                checked_claims += 1
            if want_line is not None and not any(
                    x.startswith("%d:" % want_line) or re.search(r":%d:" % want_line, x)
                    for x in lines):
                print("[WRONG-LINE: comment says it prints line %d, output is %s] %s :: %s"
                      % (want_line, lines[:3], skill, real))
                fails += 1
                continue
            if says_empty and count > 0:
                print("[STALE-ANNOTATION: says it matches nothing, matched %d] %s :: %s"
                      % (count, skill, real))
                fails += 1
                continue
            if says is not None and not says_empty and count != says:
                print("[WRONG-COUNT: comment says %d, output has %d] %s :: %s"
                      % (says, count, skill, real))
                fails += 1
                continue
            if count == 0 and not says_empty and comment == "":
                infos += 1
                print("[INFO empty, no same-line annotation - read the sentence] %s :: %s"
                      % (skill, real))
    print("\n%d recipe(s) executed from %d skill(s); %d carried an exactly checkable "
      "same-line claim (count or asserted emptiness); %d anomaly(ies), %d INFO"
          % (ran, len(list(skills())), checked_claims, fails, infos))
    print("RESULT: %s" % ("PASS" if fails == 0 else "FAIL (%d)" % fails))
    return 1 if fails else 0


def _write_suite(root, body):
    os.makedirs(os.path.join(root, "sk", "references"))
    with open(os.path.join(root, "sk", "references", "x.md"), "w") as fh:
        fh.write("alpha here\nbeta there\ngamma here\n")
    with open(os.path.join(root, "sk", "SKILL.md"), "w") as fh:
        fh.write(body)


# x.md is 3 lines: 1:alpha here / 2:beta there / 3:gamma here.
DEFECTIVE = r"""# t

```sh
grep -n "alpha\|gamma" references/x.md  # 27 hits
grep -n alpha references/x.md  # no hits - the page does not use this word
grep -n beta references/x.md  # 1 hit
grep -n "alpha references/x.md
grep -n gamma references/x.md  # 777:
grep -n zzz references/x.md
```
"""

CLEAN = r"""# t

```sh
grep -n "alpha\|gamma" references/x.md  # 2 hits
grep -n beta references/x.md  # 2:
grep -n zzz references/x.md  # no hits
```
"""


def self_test():
    """Prove the gate still detects what it claims to detect. A recipe gate whose PASS is
    never challenged is indistinguishable from a gate that checks nothing, so this plants
    one defect of every verdict class it can emit and requires each one to be caught, then
    requires a fixture with correct annotations to pass.
    """
    import shutil
    import tempfile
    bads = [
        ("WRONG-COUNT", "a comment whose number disagrees with the output"),
        ("STALE-ANNOTATION", "a comment asserting emptiness for a pattern that matches"),
        ("WRONG-LINE", "a comment asserting a line number the output does not contain"),
        ("EXIT 2", "a recipe the shell cannot run"),
    ]
    ok = True
    tmp = tempfile.mkdtemp(prefix="audit_recipes_selftest_")
    try:
        defect_root = os.path.join(tmp, "bad")
        _write_suite(defect_root, DEFECTIVE)
        r = subprocess.run([sys.executable, os.path.abspath(__file__), defect_root],
                           capture_output=True, text=True)
        for token, why in bads:
            if "[%s" % token not in r.stdout:
                print("self-test: FAILED to detect %s (%s)" % (token, why))
                ok = False
        if r.returncode == 0:
            print("self-test: defective fixture exited 0 - the gate does not fail on "
                  "planted anomalies")
            ok = False
        if "[INFO" not in r.stdout:
            print("self-test: defective fixture produced no INFO line, so the unannotated-"
                  "empty listing is not exercised")
            ok = False
        if "[WRONG-COUNT: comment says 1" in r.stdout:
            print("self-test: a CORRECT count claim ('# 1 hit' on a 1-match grep) was "
                  "reported as an anomaly - the gate cries wolf")
            ok = False

        clean_root = os.path.join(tmp, "good")
        _write_suite(clean_root, CLEAN)
        c = subprocess.run([sys.executable, os.path.abspath(__file__), clean_root],
                           capture_output=True, text=True)
        if c.returncode != 0 or "RESULT: PASS" not in c.stdout:
            print("self-test: clean fixture did not PASS:\n%s" % (c.stdout or c.stderr))
            ok = False
        if "2 carried" not in c.stdout and "3 carried" not in c.stdout:
            print("self-test: clean fixture did not exercise the count/line/emptiness "
                  "claim paths at all (nothing was checked, so PASS means nothing): %s"
                  % c.stdout.strip().splitlines()[-2:])
            ok = False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if not ok:
        print("audit_recipes.py self-test: FAILED - the gate is not verifying what it claims")
        return 1
    print("audit_recipes.py self-test: OK (4 planted defect classes detected, correct "
          "annotations not flagged, clean fixture passes)")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    sys.exit(main())
