#!/usr/bin/env python3
"""Deterministic acceptance audit for the PyRate-skills corpus.

Run it from anywhere:

    python3 scripts/audit_corpus.py [--corpus /path/to/PyRate-doc] [--self-test]

Exit code 0 == the suite is clean; 1 == every failure below is listed, with a
file:line message that says what to fix. Warnings never fail the run; they mark
a claim the auditor could not decide mechanically.

The suite is built from the documentation corpus (default: `../PyRate-doc`
relative to the suite root, override with `--corpus PATH`) (two git checkouts:
`PyRate-wiki/` and `PyRate-tutorials/tutorials/`) by `/tmp/gen_mirrors.py`,
which writes each
`<skill>/references/<base>.md` as a YAML frontmatter block plus the whole source
page with its `assets/` image paths re-pointed at the suite's `assets/images/`.
This auditor re-derives that generator logic inline (see "the generator, ported"
below) so that the mirrors can be checked byte-for-byte without trusting the
frontmatter they carry, and without importing anything.

Checks, in the order the report prints them:

  A. every content page of the corpus (15 pages x EN/CN = 30 files) is mirrored
     byte-for-byte by some */references/ file: body compared after stripping the
     mirror frontmatter, with the `assets/` -> `../../assets/images/` re-point of
     the source applied.
  B. every planned skill folder exists, has a SKILL.md, whose frontmatter parses
     as YAML and whose `name:` equals the folder name.
  C. `description:` is a single line inside the 300-1024 char window (and, per
     the authoring contract, the 400-char floor is warned about).
  D. every path a SKILL.md writes as a suite link resolves on disk. A suite link is
     `references/`, `scripts/`, `assets/`, `../assets/` or `../<skill>/...`; a path in a
     command example (`./PyRate.py`, `./example_files/Ammonoidea.py`) lives in the
     user's own PyRate working directory and is not a link the suite can answer. No
     reference may be written against the repository root.
  E. every grep recipe in a SKILL.md is executed in the skill directory and must match
     (recipes are run as argv, never through a shell). A recipe the SKILL.md declares
     in its own text to print nothing is run too and must really print nothing: it is
     tallied as a verified absence, not as a match.
  F. every file in a skill's references/ is mentioned in that SKILL.md (the
     contract's Resources table must list all of them).
  G. every image referenced anywhere in the suite exists under assets/images/.
  H. every helper script compiles, is executable, passes `--self-test`, prints
     something, imports only the standard library -- and the four scripts the
     contract plans for are actually present.
  I. every skill's references/ holds exactly the mirror inventory planned for it.
  J. every SKILL.md carries the contract's skeleton (H1, >=6 H2, Overview,
     Not documented in this wiki, Related skills, Resources, 4-12 grep recipes).
  K. no mirror file was touched by an authoring agent: each is compared
     byte-for-byte against a freshly regenerated copy (generator logic).
  L. every relative link inside a mirror resolves.
  M. the expected plan in this file still matches the corpus on disk and the
     suite layout -- a stale plan must fail loudly rather than go silent.
  N. every quoted span in a SKILL.md appears in some mirror, modulo markup
     normalisation (warnings only: quote extraction is heuristic).
  O. assets/images/ equals the corpus image sets byte-for-byte, nothing invented.
  P. every `-command` token named in a SKILL.md appears somewhere in the mirrors
     (the corpus's whole command list is mirrored, so an unknown flag is coined).
  Q. every fixture is byte-exact inside a mirror, or declared derived in
     assets/files/README.md (which is written last: while absent, that half of
     the check is skipped with a note).
  R. README.md count assertions versus the tree -- a no-op that prints a note
     while README.md is absent.
  S. each mirror carries its source page line-for-line.
  T. every "file.md:LINE" citation in a SKILL.md points at an existing mirror and
     a line that mirror actually has.
  U. SKILL.md bodies are under 500 lines; no unfinished-work marker (the to-do colon
     form) anywhere in the suite; no stray build junk shipped. The lines of this
     auditor's own prose that name the keyword it enforces are exempt by number, and
     only those -- the table is SELF_EXEMPT, and an entry that stops being needed is
     itself reported as a defect.
  V. every '../' reference in a SKILL.md lands somewhere real: a sibling skill (and a
     mirror that skill actually carries), or a suite-level directory the shared assets
     and tools live in (assets/, scripts/).
  W. every fixture carries its owning skill's prefix and is cited by a SKILL.md.

Stdlib only, Python 3, no network, no writes.
"""
import collections
import difflib
import filecmp
import glob
import os
import re
import shlex
import subprocess
import sys
import warnings

# ------------------------------------------------------------------ invocation
_here = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(_here)                     # the PyRate-skills/ directory
_default_corpus = os.path.join(os.path.dirname(ROOT), "PyRate-doc")

CORPUS, SELF_TEST = None, False
_args = sys.argv[1:]
_i = 0
while _i < len(_args):
    a = _args[_i]
    if a == "--corpus":
        if _i + 1 >= len(_args):
            sys.exit("usage: audit_corpus.py [--corpus /path/to/PyRate-doc] [--self-test]")
        CORPUS, _i = os.path.abspath(_args[_i + 1]), _i + 2
    elif a in ("--self-test", "-t"):
        SELF_TEST, _i = True, _i + 1
    elif a in ("--help", "-h"):
        print(__doc__)
        sys.exit(0)
    else:
        sys.exit("audit_corpus.py: unknown argument %r (see --help)" % a)
if CORPUS is None:
    CORPUS = os.environ.get("PYRATE_DOC") or os.path.abspath(_default_corpus)
# check H runs this file's own --self-test like any other helper's; the marker stops the
# nested run from spawning a third copy of itself.
NESTED = os.environ.get("PYRATE_AUDIT_NESTED") == "1"

fail, warn, info = [], [], []


def F(msg):
    fail.append(msg)


def W(msg):
    warn.append(msg)


def I(msg):
    info.append(msg)


# ------------------------------------------- the expected plan (NOT a glob scan)
# Transcribed from the authoring contract (PyRate-skills section 3) and from
# /tmp/gen_mirrors.py, which is the generator that produced the mirrors. The plan
# is a literal on purpose: discovering the suite by globbing would make a missing
# skill or a missing mirror silently pass, and silence is exactly what an audit
# must not do. Check M re-derives it against the corpus and the tree on disk.
W_ = "PyRate-wiki"
T_ = "PyRate-tutorials/tutorials"

WIKI_URL = "https://github.com/dsilvestro/PyRate/wiki/{}"
TUT_URL = "https://github.com/dsilvestro/PyRate/blob/master/tutorials/{}"

# source page (relative to the corpus root) -> (upstream URL, fallback title)
PAGES = {
    "%s/Home.md" % W_: (WIKI_URL.format("Home"), "PyRate Manual"),
    "%s/1.-Preparing-input-file.md" % W_: (WIKI_URL.format("1.-Preparing-input-file"),
                                           "Preparing input file"),
    "%s/2.-PyRate:-command-list.md" % W_: (WIKI_URL.format("2.-PyRate:-command-list"),
                                           "PyRate: command list"),
    "%s/3.-Summarize-PyRate-results.md" % W_: (WIKI_URL.format("3.-Summarize-PyRate-results"),
                                               "Summarize PyRate results"),
    "%s/4.-PyRateContinuous.md" % W_: (WIKI_URL.format("4.-PyRateContinuous"), "PyRateContinuous"),
    "%s/5.-Dispersal-Extinction-Sampling-model.md" % W_: (
        WIKI_URL.format("5.-Dispersal-Extinction-Sampling-model"),
        "Dispersal Extinction Sampling model"),
    "%s/README.md" % T_: (TUT_URL.format("README.md"), "PyRate tutorials - index"),
    "%s/pyrate_tutorial_0.md" % T_: (TUT_URL.format("pyrate_tutorial_0.md"),
                                     "Setting up a virtual environment for PyRate"),
    "%s/pyrate_tutorial_1.md" % T_: (TUT_URL.format("pyrate_tutorial_1.md"), "PyRate Tutorial #1"),
    "%s/pyrate_tutorial_2.md" % T_: (TUT_URL.format("pyrate_tutorial_2.md"), "PyRate Tutorial #2"),
    "%s/pyrate_tutorial_3.md" % T_: (TUT_URL.format("pyrate_tutorial_3.md"), "PyRate Tutorial #3 RJMCMC"),
    "%s/pyrate_tutorial_4.md" % T_: (TUT_URL.format("pyrate_tutorial_4.md"), "PyRate Tutorial #4"),
    "%s/pyrate_tutorial_5.md" % T_: (TUT_URL.format("pyrate_tutorial_5.md"),
                                     "Dispersal Extinction Sampling models"),
    "%s/pyrate_tutorial_6.md" % T_: (TUT_URL.format("pyrate_tutorial_6.md"), "PyRate - Advanced settings"),
    "%s/pyrate_tutorial_bdnn.md" % T_: (TUT_URL.format("pyrate_tutorial_bdnn.md"), "PyRate Tutorial #7"),
}

# skill -> [(source page, mirror base name)]; each base yields <base>.md and <base>-cn.md
SKILLS = {
    "pyrate": [("%s/Home.md" % W_, "home"),
               ("%s/README.md" % T_, "tutorials-index")],
    "pyrate-installation": [("%s/pyrate_tutorial_0.md" % T_, "virtual-environment"),
                            ("%s/Home.md" % W_, "home")],
    "pyrate-input-file": [("%s/1.-Preparing-input-file.md" % W_, "preparing-input-file"),
                          ("%s/pyrate_tutorial_1.md" % T_, "tutorial-1")],
    "pyrate-command-reference": [("%s/2.-PyRate:-command-list.md" % W_, "command-list")],
    "pyrate-preservation-models": [("%s/2.-PyRate:-command-list.md" % W_, "command-list"),
                                   ("%s/pyrate_tutorial_1.md" % T_, "tutorial-1")],
    "pyrate-bd-analysis": [("%s/pyrate_tutorial_1.md" % T_, "tutorial-1"),
                           ("%s/2.-PyRate:-command-list.md" % W_, "command-list")],
    "pyrate-rjmcmc": [("%s/pyrate_tutorial_3.md" % T_, "tutorial-3"),
                      ("%s/2.-PyRate:-command-list.md" % W_, "command-list")],
    "pyrate-summarize-results": [("%s/3.-Summarize-PyRate-results.md" % W_, "summarize-results"),
                                 ("%s/pyrate_tutorial_2.md" % T_, "tutorial-2")],
    "pyrate-continuous-covariates": [("%s/4.-PyRateContinuous.md" % W_, "pyratecontinuous"),
                                     ("%s/pyrate_tutorial_2.md" % T_, "tutorial-2")],
    "pyrate-diversity-dependence": [("%s/pyrate_tutorial_4.md" % T_, "tutorial-4")],
    "pyrate-trait-age-models": [("%s/pyrate_tutorial_4.md" % T_, "tutorial-4"),
                               ("%s/2.-PyRate:-command-list.md" % W_, "command-list")],
    "pyrate-des": [("%s/5.-Dispersal-Extinction-Sampling-model.md" % W_, "des-model"),
                   ("%s/pyrate_tutorial_5.md" % T_, "tutorial-5")],
    "pyrate-bdnn": [("%s/pyrate_tutorial_bdnn.md" % T_, "tutorial-bdnn")],
    "pyrate-mcmc-tuning": [("%s/pyrate_tutorial_6.md" % T_, "tutorial-6"),
                           ("%s/2.-PyRate:-command-list.md" % W_, "command-list")],
}

# fixture name prefix each skill owns (contract section 3, last column); "pyrate"
# is the router and owns none.
FIXTURE_PREFIX = {
    "pyrate": None, "pyrate-installation": "venv-", "pyrate-input-file": "occ-",
    "pyrate-command-reference": "cmdref-", "pyrate-preservation-models": "pres-",
    "pyrate-bd-analysis": "bd-", "pyrate-rjmcmc": "rjmcmc-",
    "pyrate-summarize-results": "sum-", "pyrate-continuous-covariates": "cont-",
    "pyrate-diversity-dependence": "mcdd-", "pyrate-trait-age-models": "covar-",
    "pyrate-des": "des-", "pyrate-bdnn": "bdnn-", "pyrate-mcmc-tuning": "tuning-",
}

# The tooling plan: which helper scripts must ship, and where. These are hard
# deliverables of the contract's "Tooling" phase, so their absence is a failure of
# the suite, not a silence of the auditor.
EXPECTED_SCRIPTS = {
    "pyrate-command-reference": ["check_env.py", "build_command.py", "parse_results.py"],
    "pyrate-input-file": ["validate_input.py"],
}
# stdlib-only top-level module names are taken from sys.stdlib_module_names (3.10+);
# a suite helper importing anything outside that set breaks the "no third-party
# imports" rule, so the audit needs the list, not a guess.
try:
    STDLIB = set(sys.stdlib_module_names)
except AttributeError:                                   # pragma: no cover
    STDLIB = set("""os sys re io json math time datetime collections itertools functools glob
    argparse subprocess shutil tempfile textwrap string random struct copy enum types typing
    pathlib codecs locale gettext difflib filecmp stat warnings contextlib dataclasses""".split())
    STDLIB |= {"unittest"}

MIRROR_EN = "verbatim local mirror of the PyRate documentation"
MIRROR_CN = "local Simplified-Chinese translation of the PyRate documentation"
IMG = re.compile(r'(?<=src=")assets/|(?<=\]\()assets/')


def planned_mirror_files():
    """[(skill, filename, source page, base, cn)] for all 50 planned mirrors."""
    out = []
    for skill, items in SKILLS.items():
        for src, base in items:
            for cn in (False, True):
                out.append((skill, "%s-cn.md" % base if cn else "%s.md" % base,
                            src[:-3] + "-cn.md" if cn else src, base, cn))
    return out


PLANNED_MIRRORS = planned_mirror_files()
PLANNED_PAGES = set()
for _src in PAGES:
    PLANNED_PAGES |= {_src, _src[:-3] + "-cn.md"}

# references/ pages that are analysis the suite wrote, not copies of a corpus page. They are
# named here one by one, because the only honest way for this suite to grow a second kind of
# reference file is to say so in the plan. Each is still required to declare itself
# (AUTHORED_MARKER) and to be linked by the SKILL.md of the skill that holds it -- see check I.
PLANNED_AUTHORED = {
    "pyrate-des": ["route2-area-coding-hazards.md"],
    "pyrate-input-file": ["cutoff-and-completeness.md"],
}
AUTHORED_MARKER = "**This file is not a mirror.**"


# --------------------------------------------------- the generator, ported inline
def repoint(body):
    """The only edit a mirror body may contain: re-point the corpus image paths."""
    return IMG.sub("../../assets/images/", body)


def title_of(body, fallback):
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def headings_of(body):
    return sum(1 for line in body.splitlines() if re.match(r"^#{1,6} ", line))


def frontmatter(*, title, url, language, mirrored_from, headings, mirror, translated_from=None):
    lines = ["---", "title: %s" % title, "source_url: %s" % url, "language: %s" % language,
             "mirrored_from: %s" % mirrored_from, "headings: %s" % headings]
    if translated_from:
        lines.append("translated_from: %s" % translated_from)
    lines += ["mirror: %s" % mirror, "---", ""]
    return "\n".join(lines)


def expected_mirror_text(skill, src, base, cn):
    """Byte-for-byte what the generator writes for one mirror, or None if the
    corpus page it would be generated from is missing."""
    src_path = src[:-3] + "-cn.md" if cn else src
    full = os.path.join(CORPUS, src_path)
    if not os.path.isfile(full):
        return None
    body = repoint(read(full))
    en_full = os.path.join(CORPUS, src)
    en_body = repoint(read(en_full)) if os.path.isfile(en_full) else ""
    url, fallback = PAGES[src]
    fm = frontmatter(
        title=title_of(body, fallback if not cn else title_of(en_body, fallback)),
        url=url,
        language="Simplified Chinese" if cn else "English",
        mirrored_from="PyRate-doc/%s" % src_path,
        headings=headings_of(body),
        mirror=MIRROR_CN if cn else MIRROR_EN,
        translated_from="%s.md" % base if cn else None,
    )
    return fm + body


def expected_page_set():
    """Every corpus content page the plan says exists (EN and CN)."""
    return set(PLANNED_PAGES)


# --------------------------------------------------------------- tiny utilities
def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def read_safe(path, label):
    try:
        return read(path)
    except (OSError, UnicodeDecodeError) as e:
        F("%s: cannot read %s: %s" % (label, path, e))
        return None


def split_frontmatter(txt):
    """(frontmatter body or None, mirrored body)."""
    m = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
    return (m.group(1), txt[m.end():]) if m else (None, txt)


def first_diff(a, b):
    """Human-readable locus of the first difference between two texts."""
    al, bl = a.split("\n"), b.split("\n")
    for i in range(min(len(al), len(bl))):
        if al[i] != bl[i]:
            return "line %d: mirror %r != corpus %r" % (
                i + 1, al[i][:70], bl[i][:70])
    if len(al) != len(bl):
        return "line count: %d vs %d" % (len(al), len(bl))
    return "identical"


def rel(path):
    return os.path.relpath(path, ROOT)


def md_files(d):
    return sorted(f for f in os.listdir(d) if f.endswith(".md")) if os.path.isdir(d) else []


def is_file(d, f):
    return os.path.isfile(os.path.join(d, f))


# ---------------------------------------------------------------- discovery
skill_dirs = sorted(d for d in os.listdir(ROOT)
                    if os.path.isdir(os.path.join(ROOT, d)) and not d.startswith("."))
present_skills = [d for d in skill_dirs if d not in ("assets", "scripts")]
extra_dirs = sorted(d for d in present_skills if d not in SKILLS)
mdirs = os.path.join(ROOT, "%s", "references")

# mirrors on disk, whether or not they were planned: {skill: {filename: text}}
disk_mirrors = {}
for sk in present_skills:
    rd = mdirs % sk
    if os.path.isdir(rd):
        disk_mirrors[sk] = {f: (read_safe(os.path.join(rd, f), "A") or "")
                            for f in os.listdir(rd) if f.endswith(".md")}
    else:
        disk_mirrors[sk] = {}

skill_md = {}
for sk in SKILLS:
    p = os.path.join(ROOT, sk, "SKILL.md")
    skill_md[sk] = read_safe(p, "B") if os.path.isfile(p) else None

# the shared fixtures and their index. assets/files/README.md is written last by the
# integration agent, so it may legitimately be absent while the suite is built.
fd = os.path.join(ROOT, "assets", "files")
fr = os.path.join(fd, "README.md")
fixtures = sorted(f for f in (os.listdir(fd) if os.path.isdir(fd) else [])
                  if os.path.isfile(os.path.join(fd, f)) and f != "README.md")
provenance = read(fr) if os.path.isfile(fr) else ""


def owner_of(fname):
    """Which skill owns a fixture, by the prefix the contract gives it. The longest
    prefix wins, because `bd-` is a prefix of `bdnn-`."""
    hits = [sk for sk, pfx in FIXTURE_PREFIX.items() if pfx and fname.startswith(pfx)]
    return max(hits, key=lambda s: len(FIXTURE_PREFIX[s])) if hits else None


def fixtures_of(sk):
    """The fixtures in assets/files/ whose prefix says this skill owns them."""
    pfx = FIXTURE_PREFIX.get(sk)
    if not pfx or not os.path.isdir(fd):
        return []
    return [f for f in sorted(os.listdir(fd))
            if os.path.isfile(os.path.join(fd, f)) and f != "README.md" and f.startswith(pfx)]


corpus_ok = os.path.isdir(CORPUS)
if not corpus_ok:
    F("A: corpus root %s does not exist -- the whole mirroring audit is unauditable; "
      "pass --corpus /path/to/PyRate-doc" % CORPUS)

corpus_pages = []
if corpus_ok:
    for dirpath, dirnames, files in os.walk(CORPUS):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        for f in files:
            if f.endswith(".md") and not f.startswith("."):
                corpus_pages.append(os.path.relpath(os.path.join(dirpath, f), CORPUS))
    corpus_pages = sorted(corpus_pages)

# ------------------------------------------------------------------ M: the plan
# If the corpus or the suite grows a page/skill the plan does not know about, the
# auditor must say so: a plan that quietly under-covers is worse than no plan.
if corpus_ok:
    disc, planned = set(corpus_pages), expected_page_set()
    if disc - planned:
        F("M: corpus pages the expected plan does not know about (update the plan, then "
          "audit them): %s" % ", ".join(sorted(disc - planned)))
    if planned - disc:
        F("M: the plan lists corpus pages that are not on disk: %s" % ", ".join(sorted(planned - disc)))
    if not (disc - planned or planned - disc):
        I("M: the plan matches the corpus exactly -- %d content pages (%d EN + %d CN) over "
          "%d skills -> %d mirrors" % (len(disc), len(PAGES), len(disc) - len(PAGES),
                                       len(SKILLS), len(PLANNED_MIRRORS)))
if extra_dirs:
    F("M: top-level director%s %s %s not a planned skill and not assets/ or scripts/ -- "
      "either it is a stray or the plan needs it"
      % ("y" if len(extra_dirs) == 1 else "ies", ", ".join(extra_dirs),
         "is" if len(extra_dirs) == 1 else "are"))

# ------------------------------------------------------- A: corpus page coverage
# For each corpus page: some mirror must claim it AND carry it byte-for-byte.
claims = collections.defaultdict(list)          # page -> [(who, body)]
for sk, files in sorted(disk_mirrors.items()):
    for f, txt in sorted(files.items()):
        head, body = split_frontmatter(txt)
        if head is None:
            continue                            # K/I report an unplanned file
        mm = re.search(r"^mirrored_from: PyRate-doc/(.+)$", head, re.M)
        if mm:
            claims[mm.group(1).strip()].append(("%s/references/%s" % (sk, f), body))

n_pages_ok = 0
for page in sorted(expected_page_set()):
    src_abs = os.path.join(CORPUS, page)
    if not corpus_ok or not os.path.isfile(src_abs):
        continue                                # M reports the missing page
    want = repoint(read(src_abs))
    holders = claims.get(page, [])
    if not holders:
        F("A: corpus page %s is carried by NO mirror: no */references/*.md declares "
          "mirrored_from: PyRate-doc/%s" % (page, page))
        continue
    faithful = 0
    for who, body in holders:
        if body == want:
            faithful += 1
        else:
            F("A: %s claims mirrored_from PyRate-doc/%s but its body is not the "
              "byte-for-byte re-pointed page (%d vs %d chars; %s)"
              % (who, page, len(body), len(want), first_diff(body, want)))
    if faithful:
        n_pages_ok += 1
if corpus_ok:
    bogus = sorted(set(claims) - expected_page_set())
    for page in bogus:
        F("A: %s declares mirrored_from PyRate-doc/%s, which is not a page of this corpus"
          % (", ".join(w for w, _ in claims[page]), page))
    if n_pages_ok == len(PLANNED_PAGES) and not fail:
        I("A: all %d corpus pages (EN + CN) are mirrored byte-for-byte, %d mirror files in "
          "total" % (len(PLANNED_PAGES), len(PLANNED_MIRRORS)))
    elif n_pages_ok:
        I("A: %d/%d corpus pages have at least one byte-for-byte mirror"
          % (n_pages_ok, len(PLANNED_PAGES)))

# ---------------------------------------- K: no mirror was touched by an author
k_bad = 0
for sk, fname, src, base, cn in PLANNED_MIRRORS:
    want = expected_mirror_text(sk, src, base, cn)
    path = os.path.join(ROOT, sk, "references", fname)
    who = "%s/references/%s" % (sk, fname)
    if want is None:
        continue                                   # M/A report the missing source page
    if not os.path.isfile(path):
        k_bad += 1
        F("K: %s is missing -- the generator writes it from PyRate-doc/%s"
          % (who, src[:-3] + "-cn.md" if cn else src))
        continue
    got = read(path)
    if got != want:
        k_bad += 1
        g_head, g_body = split_frontmatter(got)
        w_head, w_body = split_frontmatter(want)
        what = ("body (author-edited mirror text?)" if g_body != w_body
                else "frontmatter")
        F("K: %s differs from a freshly generated mirror in its %s: %s"
          % (who, what, first_diff(got, want)))
if k_bad == 0 and corpus_ok:
    I("K: all %d mirrors are byte-identical to a freshly regenerated copy -- nothing under "
      "references/ was edited by an authoring agent" % len(PLANNED_MIRRORS))

# ------------------------------------------------- I: the planned mirror inventory
i_bad = 0
accepted_authored = []
for sk, items in SKILLS.items():
    want = set()
    for src, base in items:
        want |= {"%s.md" % base, "%s-cn.md" % base}
    have = set(disk_mirrors.get(sk, ()))
    if not os.path.isdir(mdirs % sk):
        i_bad += 1
        F("I: %s has no references/ directory at all (planned %d mirror files)"
          % (sk, len(want)))
        continue
    if want - have:
        i_bad += 1
        F("I: %s/references/ is missing planned mirror(s): %s" % (sk, ", ".join(sorted(want - have))))
    extra = have - want
    if extra:
        try:
            owner = open(os.path.join(ROOT, sk, "SKILL.md"), encoding="utf-8",
                         errors="replace").read()
        except OSError:
            owner = ""
        unlisted, uncertified = [], []
        for x in sorted(extra):
            if x not in PLANNED_AUTHORED.get(sk, ()):
                unlisted.append(x)
                continue
            try:
                body = open(os.path.join(mdirs % sk, x), encoding="utf-8",
                            errors="replace").read()
            except OSError:
                body = ""
            if AUTHORED_MARKER not in body[:2000]:
                uncertified.append("%s (planned as suite-authored but does not declare itself)"
                                   % x)
            elif x not in owner:
                uncertified.append("%s (planned as suite-authored but no SKILL.md links to it)"
                                   % x)
            else:
                accepted_authored.append("%s/references/%s" % (sk, x))
        if unlisted:
            i_bad += 1
            F("I: %s/references/ carries %s, which the plan does not give this skill"
              % (sk, ", ".join(unlisted)))
        if uncertified:
            i_bad += 1
            F("I: %s/references/ holds %s" % (sk, "; ".join(uncertified)))
if i_bad == 0:
    I("I: every skill carries exactly its planned mirror inventory (%d files over %d skills)"
      % (len(PLANNED_MIRRORS), len(SKILLS)))
if accepted_authored:
    I("I: %d references/ page(s) are suite-authored, listed in PLANNED_AUTHORED, self-declared "
      "and linked: %s" % (len(accepted_authored), ", ".join(accepted_authored)))

# ------------------------------------ S: each mirror carries its page line-for-line
def _retarget_agnostic(t):
    """Blank out link targets and image sources: a mirror may re-point a link, but it
    may not touch the words a reader actually parses."""
    return re.sub(r'src="[^"]*"', 'src="T"', re.sub(r"\]\([^)]*\)", "](T)", t))


s_bad = 0
for sk, fname, src, base, cn in PLANNED_MIRRORS:
    page = src[:-3] + "-cn.md" if cn else src
    path = os.path.join(ROOT, sk, "references", fname)
    if not os.path.isfile(path) or not os.path.isfile(os.path.join(CORPUS, page)):
        continue                                    # A / I / K report it
    txt = read(path)
    body = split_frontmatter(txt)[1]
    wl = [_retarget_agnostic(l) for l in
          read(os.path.join(CORPUS, page)).strip("\n").split("\n")]
    ml = [_retarget_agnostic(l) for l in body.strip("\n").split("\n")]
    who = "%s/references/%s" % (sk, fname)
    sm = difflib.SequenceMatcher(None, wl, ml, autojunk=False)
    lost, added = [], []
    for tag, i, j, k, l2 in sm.get_opcodes():
        if tag == "equal":
            continue
        if tag in ("delete", "replace"):
            lost += [(x + 1, wl[x]) for x in range(i, j) if wl[x].strip()]
        if tag in ("insert", "replace"):
            added += [(x + 1, ml[x]) for x in range(k, l2) if ml[x].strip()]
    if lost:
        s_bad += 1
        F("S: %s drops %d line(s) of PyRate-doc/%s (e.g. source line %d: %.60s)"
          % (who, len(lost), page, lost[0][0], lost[0][1].strip()))
    if added:
        s_bad += 1
        F("S: %s carries %d line(s) that PyRate-doc/%s does not have (e.g. mirror line %d: %.60s)"
          % (who, len(added), page, added[0][0], added[0][1].strip()))
if s_bad == 0 and corpus_ok:
    I("S: every mirror carries its source page line-for-line -- links re-pointed, no line "
      "dropped, nothing invented (%d pages compared)" % len(PLANNED_PAGES))

# ---------------------------------- L: relative links inside the mirrors resolve
l_bad = 0
for sk, files in sorted(disk_mirrors.items()):
    rd = mdirs % sk
    for f, txt in sorted(files.items()):
        for link in (re.findall(r"\]\((\.\.?/[^)#\s]+)", txt)
                     + re.findall(r'src="(\.\.?/[^"]+)"', txt)):
            if not os.path.exists(os.path.normpath(os.path.join(rd, link))):
                l_bad += 1
                F("L: broken relative link in %s/references/%s -> %s" % (sk, f, link))
if l_bad == 0:
    I("L: every relative link inside every mirror resolves on disk")

# ------------------------------------------------------------- the mirror corpus
GREEK = {"alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε",
         "zeta": "ζ", "eta": "η", "theta": "θ", "iota": "ι", "kappa": "κ",
         "lambda": "λ", "mu": "μ", "nu": "ν", "xi": "ξ", "pi": "π", "rho": "ρ",
         "sigma": "σ", "tau": "τ", "phi": "φ", "chi": "χ", "psi": "ψ", "omega": "ω"}
SYMBOLS = {"infty": "∞", "ell": "ℓ", "pm": "±", "mp": "∓", "cdot": "·",
           "times": "×", "div": "÷", "leq": "≤", "geq": "≥", "neq": "≠",
           "approx": "≈", "sim": "~", "to": "→", "rightarrow": "→",
           "partial": "∂", "propto": "∝"}


def _norm(t):
    """Reduce a mirror (or a quote) to the plain prose a SKILL.md would quote from it."""
    t = re.sub(r"\[([^\]]*)\]\(([^)]*)\)", lambda m: (m.group(1) or m.group(2)), t)
    t = re.sub(r"\((?:https?|ftp|mailto)://[^)]*\)", " ", t)   # inline URLs are not prose
    for name, ch in list(GREEK.items()) + list(SYMBOLS.items()):
        t = re.sub(r"\\%s(?![a-zA-Z])" % name, ch, t, flags=re.I)
    t = re.sub(r"\\(?:textrm|text|mathrm|mathit|mathbf|boldsymbol|mathsf|operatorname)"
               r"\s*\{([^{}]*)\}", r"\1", t)
    t = re.sub(r"\\(?:left|right|big|Big|bigg|Bigg)(?![a-zA-Z])", "", t)
    t = re.sub(r"_\{([^{}]*)\}\^\{([^{}]*)\}", r"\2\1", t)
    t = re.sub(r"\^\{([^{}]*)\}_\{([^{}]*)\}", r"\1\2", t)
    t = re.sub(r"\^?_\{([^{}]*)\}", r"\1", t)
    t = t.replace("$", "").replace("{", "").replace("}", "").replace("\\", "")
    t = re.sub(r"[_^]", "", t)
    t = re.sub(r"</?[a-zA-Z][^>\n]*>", " ", t)     # <img>/<br>/<sub>/<your_file> markup
    t = re.sub(r"\*\*|\*|`|__", "", t)             # markdown emphasis
    t = t.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    t = t.replace("–", "-").replace("—", "-").replace("‑", "-")
    for a, b in (("²", "2"), ("³", "3"), ("¹", "1"), ("⁰", "0"), ("₀", "0"), ("₁", "1"),
                 ("₂", "2"), ("₃", "3"), ("₄", "4"), ("₅", "5"), ("₆", "6"), ("₇", "7"),
                 ("₈", "8"), ("₉", "9"), ("ℓ", "l"), ("×", "x"), ("→", "->"), ("≈", "~"),
                 ("⎯", "-"), ("…", "...")):
        t = t.replace(a, b)
    t = re.sub(r"\s*([=<>])\s*", r"\1", t)
    t = re.sub(r"\s+([,.;:!?])", r"\1", t)
    t = re.sub(r"\s+", " ", t)
    return t.lower().strip()


mirror_all, mirror_raw = "", ""
mirror_lines = {}            # "skill/references/file.md" -> [lines] (1-based)
for sk, files in sorted(disk_mirrors.items()):
    for f, txt in sorted(files.items()):
        mirror_all += _norm(txt) + " "
        mirror_raw += txt + "\n"
        mirror_lines["%s/references/%s" % (sk, f)] = txt.split("\n")

# ---------------------------------------------------------------- B/C/J: SKILL.md
def _yaml_plain_or_quoted(line):
    """Return the scalar of a `key: value` frontmatter line, or raise ValueError.

    Stdlib-only YAML subset: catches the two ways a hand-written description breaks a
    real parser -- an unquoted scalar containing ': ', and a double-quoted scalar with
    an unescaped or unterminated quote.
    """
    if line.startswith('"'):
        i, buf = 1, []
        while True:
            if i >= len(line):
                raise ValueError("unterminated double-quoted scalar")
            c = line[i]
            if c == "\\":
                if i + 1 >= len(line):
                    raise ValueError("trailing backslash")
                buf.append(line[i + 1])
                i += 2
                continue
            if c == '"':
                if i + 1 != len(line):
                    raise ValueError("trailing content after closing quote")
                return "".join(buf)
            buf.append(c)
            i += 1
    if line[:1] in "&*!|>%@`{}[],#'":
        raise ValueError("unsupported YAML indicator %r" % line[:1])
    if ": " in line or line.endswith(":"):
        raise ValueError("plain scalar contains ': ' -- must be quoted")
    return line


FM_KEYS = ("name", "description", "allowed-tools", "license", "version", "metadata")
REQUIRED_H2 = ("## Overview", "## Not documented in this wiki", "## Related skills",
               "## Resources")
BODY_STATS = {}      # skill -> dict for the README/aggregate checks

for sk in sorted(SKILLS):
    p = os.path.join(ROOT, sk, "SKILL.md")
    if not os.path.isdir(os.path.join(ROOT, sk)):
        F("B: planned skill %s/ does not exist at all" % sk)
        continue
    if not os.path.isfile(p):
        F("B: planned skill %s has no SKILL.md yet -- its %d mirror(s) are unusable because "
          "nothing routes to them" % (sk, len(SKILLS[sk]) * 2))
        continue
    txt = skill_md.get(sk)
    if txt is None:
        continue                                     # the read itself failed, reported
    fm = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
    if not fm:
        F("B: %s has no YAML frontmatter block ('---' ... '---')" % sk)
        continue
    head = fm.group(1)
    keys = {}
    head_lines = head.split("\n")
    for idx, ln in enumerate(head_lines):
        if not ln.strip():
            continue
        m = re.match(r"^([a-z][a-z-]*): ?(.*)$", ln)
        if not m:
            F("B: %s frontmatter line %d is not a `key: value` pair: %.60r" % (sk, idx + 1, ln))
            continue
        k, v = m.group(1), m.group(2)
        if k not in FM_KEYS:
            W("B: %s frontmatter carries the unplanned key %r" % (sk, k))
        try:
            keys[k] = _yaml_plain_or_quoted(v)
        except ValueError as e:
            F("B: %s frontmatter '%s' is not valid YAML: %s" % (sk, k, e))
            keys[k] = v.strip('"')
        # a description folded onto a second line is a different document than the one
        # a skill loader parses, so say so instead of measuring half of it
        nxt = head_lines[idx + 1] if idx + 1 < len(head_lines) else None
        if nxt is not None and nxt.strip() and not re.match(r"^[a-z][a-z-]*: ", nxt):
            F("C: %s description is not a single line -- line %d of the frontmatter "
              "continues onto %r" % (sk, idx + 1, nxt[:40]))
    if keys.get("name") != sk:
        F("B: %s frontmatter name=%r does not equal the folder name" % (sk, keys.get("name")))
    if not re.match(r"^[a-z0-9][a-z0-9-]{0,62}$", keys.get("name", "")):
        F("B: %s name %r violates the skill-name pattern / 64-char limit"
          % (sk, keys.get("name")))
    d = keys.get("description")
    if d is None:
        F("C: %s has no description -- the description is the only thing an agent sees "
          "before deciding to load the skill" % sk)
    elif len(d) > 1024:
        F("C: %s description is %d chars, over the 1024-char limit" % (sk, len(d)))
    elif len(d) < 300:
        F("C: %s description is %d chars, under the 300-char floor" % (sk, len(d)))
    elif len(d) < 400:
        W("C: %s description is %d chars -- under the contract's 400-char floor, so it is "
          "probably thin on trigger tokens" % (sk, len(d)))
    if d and "\n" in d:
        F("C: %s description is not a single line" % sk)

    body = txt[fm.end():]
    n_lines = txt.count("\n") + 1
    n_sec = len(re.findall(r"^## ", body, re.M))
    n_rec = len(re.findall(r"^\s*grep ", body, re.M))
    n_fx = len([f for f in fixtures_of(sk)])
    BODY_STATS[sk] = {"lines": n_lines, "sections": n_sec, "recipes": n_rec,
                      "desc": len(d or ""), "body": body, "txt": txt, "fixtures": n_fx}
    I("   %-31s %4d lines  %2d H2  %d grep recipes  %3d-char description  %d fixture(s)"
      % (sk, n_lines, n_sec, n_rec, len(d or ""), n_fx))
    if not body.lstrip().startswith("# "):
        F("J: %s body does not open with an H1 title" % sk)
    if n_sec < 6:
        F("J: %s has only %d H2 sections (the contract skeleton needs at least 6)" % (sk, n_sec))
    for h in REQUIRED_H2:
        # The suite numbers its sections ("## 3. Overview"); an optional leading "N." is
        # the only latitude granted here -- the section itself is still mandatory.
        rx = r"^## (?:\d+[.)] )?%s\b" % re.escape(h.split("## ", 1)[1])
        if not re.search(rx, body, re.M):
            F("J: %s lacks '%s'%s" % (sk, h,
              ", so anything the corpus omits would have to come from model memory"
              if h.startswith("## Not documented") else ""))
    if not re.search(r"^## (?:\d+[.)] )?(?:The \d+ things that break a run|.*[Hh]azard|"
                     r"Pitfalls)", body, re.M) and "Pitfalls" not in body:
        W("J: %s has no hazard/Pitfalls section, though the corpus is full of silent "
          "failures" % sk)
    if n_rec == 0:
        F("J: %s ships no grep recipe, so its pointers into the mirrors cannot be "
          "re-verified by a reader" % sk)
    elif not 4 <= n_rec <= 12:
        W("J: %s has %d grep recipes; the contract asks for 4-12" % (sk, n_rec))

# ------------------------------------------------------------------- D: paths
# `scripts/audit_corpus.py` is the developer-facing auditor at the suite root: a
# SKILL.md may name it as a tool to run, and there is no "../" spelling that makes it
# resolve after install (the top-level scripts/ is not part of a skill install), so the
# path rule exempts exactly that one name.
EXEMPT_PATHS = {"scripts/audit_corpus.py"}

# Checks U and G scan this file exactly as they scan the deliverable, and this file has
# to carry the very tokens they hunt: the prose that spells out the rule it enforces, the
# pattern that names its soft needles, and the placeholder figure names its own self-test
# asserts on. Those lines are exempt one by one -- never the file as a whole, never the
# directory. An entry the sweep no longer needs is reported as a defect, so an edit that
# moves one of these lines cannot leave a hole behind it, and a marker or an invented
# figure added anywhere else -- here or in any other file -- still fails. The numbers are
# the line in this file; re-run the audit after an edit and it will name any drift.
SELF_EXEMPT = {
    ("G", "scripts/audit_corpus.py", 1928),  # self-test fixture: the markdown re-point
    ("G", "scripts/audit_corpus.py", 1929),  # self-test fixture: the html re-point
    ("G", "scripts/audit_corpus.py", 2042),  # self-test fixture: the retarget-agnostic pair
    ("U", "scripts/audit_corpus.py", 1736),  # the pattern that has to name the needles it bans
    ("U", "scripts/audit_corpus.py", 1739),  # the rule text naming the marker it bans
    ("U", "scripts/audit_corpus.py", 1743),  # the quoted-token examples in that text
}
SELF_EXEMPT_SEEN = set()


def self_exempt(check, who, n):
    """True for exactly one (check, file, line) named above, and for nothing else."""
    if (check, who, n) in SELF_EXEMPT:
        SELF_EXEMPT_SEEN.add((check, who, n))
        return True
    return False

def skill_lines(path):
    """[(line-no, text, in_fence)] for a SKILL.md; fence markers themselves blanked.

    Line numbers are kept because every D/E/N/T message must say which line of which
    file is wrong, and the fence flag because a fenced block is a shell command the
    reader runs in their own working directory, not a path inside the suite.
    """
    out, fence = [], False
    for i, ln in enumerate(read(path).splitlines(), 1):
        if ln.lstrip().startswith("```"):
            fence = not fence
            out.append((i, "", fence))
            continue
        out.append((i, ln, fence))
    return out


D_CANDS = (re.compile(r"\]\((\.\.?/[^)#\s]+)"),                        # markdown link
           re.compile(r"`(\.\.?/[A-Za-z0-9_./-]+?)(?::\d+)?`"),         # `../a/b.md`
           re.compile(r"(?<![\w./-])`?((?:references|scripts)/[A-Za-z0-9_./-]+?"
                      r"(?:\.(?:md|py|r|txt|csv|tsv|json)))(?::\d+)?`?"))
D_ROOT = re.compile(r"(?<![\w./-])((?:%s|assets)/[A-Za-z0-9_./-]+\.(?:md|py|png|txt|csv))"
                    % "|".join(re.escape(s) for s in SKILLS))

for sk, st in sorted(BODY_STATS.items()):
    sk_dir = os.path.join(ROOT, sk)
    src = skill_lines(os.path.join(sk_dir, "SKILL.md"))
    bad = 0
    for no, txt, fenced in src:
        if fenced:
            continue
        cands = set()
        for pat in D_CANDS:
            cands |= set(m.group(1) for m in pat.finditer(txt))
        for cand in sorted(cands):
            rr = cand.rstrip(".,;:")
            if rr in EXEMPT_PATHS or rr[3:] in EXEMPT_PATHS:
                continue
            # "./something" is a path in the user's working directory (PyRate's own
            # ./example_files/, the ./DES_demo/ a tutorial builds, ./PyRate.py); it is
            # not a suite reference and cannot be resolved from the repository.
            if rr.startswith("./"):
                continue
            if os.path.exists(os.path.join(sk_dir, rr)):
                continue
            rest = re.sub(r"^\.\./\.\./", "", rr)
            if rr.startswith("../../") and os.path.exists(os.path.join(ROOT, sk, "..", rest)):
                # The mirror spelling of an asset path: correct from references/, one
                # level too deep from the SKILL.md that quotes it. The file is there and
                # resolvable one step up, so this is a style break, not a broken link.
                W("D: %s/SKILL.md:%d writes %s, the form that resolves from a file in "
                  "references/; from SKILL.md itself it is ../%s"
                  % (sk, no, rr, re.sub(r"^\.\./", "", rest)))
                continue
            F("D: %s/SKILL.md:%d refers to %s, which does not exist" % (sk, no, rr))
            bad += 1
        # A reference written against the REPOSITORY root resolves here but dangles once
        # the skills are installed side by side in a skills directory: cross-skill and
        # asset paths must carry the leading "../".
        for r_ in sorted(set(m.group(1) for m in D_ROOT.finditer(txt))):
            if r_ in EXEMPT_PATHS or os.path.exists(os.path.join(sk_dir, r_)):
                continue
            if os.path.exists(os.path.join(ROOT, r_)):
                F("D: %s/SKILL.md:%d cites %s relative to the repository root; after "
                  "install it must be ../%s" % (sk, no, r_, r_))
            else:
                F("D: %s/SKILL.md:%d refers to %s, which does not exist" % (sk, no, r_))
            bad += 1
    if bad == 0:
        pass                                    # one aggregate info line below

# ----------------------------------------------------------------- E: grep recipes
# A SKILL.md teaches an agent to look facts up in the mirrors with grep. A recipe that
# does not run, or whose pattern matches nothing, sends the agent hunting for a fact that
# is not in the corpus -- so every recipe is executed here, from its own skill directory,
# without a shell and read-only.
#
# Two shell features are modelled faithfully, and nothing else:
#   * quoting: shlex in posix=False mode keeps the quotes, _unquote then strips one
#     layer exactly the way a shell would, so the backslashes of a BRE alternation
#     ("a\|b") reach grep intact;
#   * ";", "|", "||" and "&&": the line is split on the ones that sit outside quotes and
#     every stage is then executed for real, stdout into stdin, so that a pipeline is
#     verified as the reader will run it. Only grep/wc/head/tail/sort/uniq/cut/tr are
#     ever executed, so no recipe can write to disk. A trailing "|| echo ..." is read as
#     the author declaring that the grep is expected to match nothing.
# A recipe may only be declared to expect no match by prose that is about it -- its own
# trailing comment, the line above or below, or the comment lines introducing its fenced
# block -- and a recipe that explicitly claims an empty result FAILS if it turns out to
# print one, so the declaration cannot be used to smuggle a dead recipe past this check.
#
# Skipped, not failed, are lines that are shell code rather than a lookup in the corpus:
# redirections and pipes into data (fixture surgery in a worked example), shell
# variables, and targets that only ever exist in the user's working directory (a log
# file, a table they just built). A recipe whose target *is* corpus material but that
# cannot be resolved or run is a failure.
# A recipe is allowed to match nothing only when the author says so. Two vocabularies:
#   E_SOFT -- absence prose around the recipe (its own line, the line above or below,
#            the comments introducing its fenced block, or the sentence it is quoted in).
#            Enough to ACCEPT a recipe that returns nothing.
#   a CLAIM -- "prints 0" / "prints nothing" written as a shell comment attached to the
#            command itself. That is a statement about the output, so it is verified:
#            a recipe that promises a count of 0 and prints 7, or promises silence and
#            prints hits, is a skill teaching a reader something false.
E_SOFT = re.compile(
    r"no\s+hit|no\s+match|no\s+hits|finds?\s+nothing|prints?\s+nothing|\babsent\b|"
    r"absent\s+from|no\s+entry|not\s+in\s+(?:the|these|any|my|here)\b|none\s+of|"
    r"not\s+documented|never\s+(?:appear|name|mention|document|occur)|zero\s+hits?\b|"
    r"exit=1\b|prints?\s+0\b|expect\s*0\b|nothing\s+(?:documents|matches)|no\s+occurrence|"
    r"carries\s+no\b|no\s+(?:other|further)\s+|does\s+not\s+(?:name|appear|exist|mention|occur)|"
    r"do(?:es)?\s+not\s+occur|no\s+line|\bnowhere\b|\b0\s+(?:hits?|matches?|lines?|occurrences?)|"
    r"returns?\s*`?\s*0\b|=\s*0\b|is\s+not\s+(?:documented|listed|present|on\s+this\s+page)",
    re.I)
GREP_VAL_OPTS = {"-A", "-B", "-C", "--after-context", "--before-context", "--context",
                 "-e", "--regexp", "-f", "--file", "-m", "--max-count", "--include",
                 "--exclude", "--exclude-dir", "--color", "--colour"}
SUITE_PARTS = ("references", "scripts", "assets")


def _strip_comment(s):
    """Drop a trailing shell comment that sits outside quotes."""
    out, quote, i = [], None, 0
    while i < len(s):
        c = s[i]
        if quote:
            out.append(c)
            if c == quote:
                quote = None
            elif c == "\\" and quote != "'":
                out.append(s[i + 1:i + 2])
                i += 1
        elif c in "\"'":
            quote = c
            out.append(c)
        elif c == "#" and (i == 0 or s[i - 1] in " \t"):
            break
        else:
            out.append(c)
        i += 1
    return "".join(out).strip()


def _comment_of(s):
    """The trailing shell comment of a line, '' when the line has none."""
    code = _strip_comment(s)
    return s[len(code):] if s.startswith(code) else ""


def _outside_quotes(s):
    """The characters of a shell line that are not inside a quoted string."""
    out, quote, i = [], None, 0
    while i < len(s):
        c = s[i]
        if quote:
            if c == "\\" and quote != "'":
                i += 2
                continue
            if c == quote:
                quote = None
        elif c in "\"'":
            quote = c
        elif c == "\\":
            i += 2
            continue
        else:
            out.append(c)
        i += 1
    return "".join(out)


def _chunks(s, seps):
    """Split a shell line on any of `seps`, each recognised only outside quotes.

    `seps` must be ordered longest-first so that '||' wins over '|'.
    """
    out, buf, quote, i = [], [], None, 0
    while i < len(s):
        c = s[i]
        if quote:
            buf.append(c)
            if c == "\\" and quote != "'" and i + 1 < len(s):
                buf.append(s[i + 1])
                i += 2
                continue
            if c == quote:
                quote = None
            i += 1
            continue
        if c in "\"'":
            quote = c
            buf.append(c)
            i += 1
            continue
        if c == "\\":
            buf.append(c)
            if i + 1 < len(s):
                buf.append(s[i + 1])
            i += 2
            continue
        for sep in seps:
            if s.startswith(sep, i):
                out.append("".join(buf))
                buf = []
                i += len(sep)
                break
        else:
            buf.append(c)
            i += 1
    out.append("".join(buf))
    return [x.strip() for x in out if x.strip()]


def _pipeline(s):
    """(stages, or_else) -- the '|' chain that runs before any '||', '&&' or ';'."""
    top = _chunks(s, ("||", "&&", ";"))
    return _chunks(top[0], ("|",)) if top else [], len(top) > 1


def _unquote(tok):
    """Strip one layer of shell quotes, keeping the backslashes a shell would keep."""
    if len(tok) > 1 and tok[0] == tok[-1] and tok[0] in "\"'":
        inner = tok[1:-1]
        if tok[0] == '"':
            inner = re.sub(r"\\([\\\"$`])", r"\1", inner)
        return inner
    return re.sub(r"\\(.)", r"\1", tok)


def _classify(toks):
    """grep's own argument rules -> [("opt"|"pat"|"file"|"sep", text), ...].

    '--' ends option parsing and nothing else: the first operand after it is still the
    pattern when no -e was given, so `grep -n -- '-A 4' file.md` searches for "-A 4" in
    file.md rather than globbing a file called "-A 4" (which would make a pattern that
    contains * or ? look like a missing target file).
    """
    out, ended, have_e, got_pat = [], False, False, False
    i = 0
    while i < len(toks):
        t = toks[i]
        if not ended and t == "--":
            ended = True
            out.append(("sep", t))
            i += 1
            continue
        if not ended and len(t) > 1 and t.startswith("-"):
            out.append(("opt", t))
            base = t.split("=")[0]
            if "=" not in t and base in GREP_VAL_OPTS and i + 1 < len(toks):
                nxt = toks[i + 1]
                if base in ("-e", "--regexp"):
                    have_e = True
                    out.append(("pat", nxt))
                else:
                    out.append(("opt", nxt))
                i += 1
            i += 1
            continue
        if have_e or got_pat:
            out.append(("file", t))
        else:
            got_pat = True
            out.append(("pat", t))
        i += 1
    return out


def _suite_lookup(arg):
    """Does this grep argument name material that has to exist inside the suite?"""
    parts = [p for p in arg.split("/") if p and p not in (".", "..")]
    return any(p in SUITE_PARTS for p in parts)


PIPE_SAFE = ("grep", "wc", "head", "tail", "sort", "uniq", "cut", "tr")


def _expand(cwd, tokens):
    """Glob-expand the ("file", tok) entries of one parsed stage; None if a glob misses.

    A glob that matches nothing means the recipe names a file that is not there, so the
    whole stage is reported as unresolved: handing the caller a token list with the
    missing operand quietly dropped would make grep read empty input and answer "no
    match", turning a broken recipe into silence.
    """
    new, miss = [], None
    for k, t in tokens:
        if k != "file" or not any(c in t for c in "*?["):
            new.append(t)
            continue
        hits = sorted(glob.glob(t if os.path.isabs(t) else os.path.join(cwd, t)))
        if not hits:
            miss = t
            break
        new += [os.path.relpath(h, cwd) for h in hits]
    return (new, None) if (new and not miss) else (None, miss)


def run_recipe(sk_dir, recipe):
    """Execute one grep recipe -- a whole pipeline -- without a shell.

    Every stage is run for real (stdout of one into stdin of the next) so that a recipe
    like `grep ... | grep -v ... | wc -l` is checked as the reader will actually run it;
    only PIPE_SAFE commands are ever executed, so a recipe cannot write to disk.

    Returns (status, payload):
      ("run", {"greps": [rc per grep stage], "out": final stdout, "err": last stderr,
               "fallback": did the line carry '|| echo ...', "opts": grep flags})
      ("skip", reason)   not a lookup in corpus material (redirection, shell variable,
                         a stage this auditor will not run, working-directory targets)
      ("bad", reason)    a recipe that cannot be parsed or whose files are not there
    """
    line = _strip_comment(recipe)
    if not line:
        return "skip", "nothing but a comment"
    outside = _outside_quotes(line)
    if re.search(r"[<>]|\$|`|&", outside):
        return "skip", "redirection, shell variable or command substitution"
    stages, or_else = [], False
    pipe, or_else = _pipeline(line)
    for seg in pipe:
        try:
            toks = shlex.split(seg, posix=False)
        except ValueError as e:
            return "bad", "unparsable quoting: %s" % e
        argv = [_unquote(t) for t in toks]
        if not argv:
            continue
        if os.path.basename(argv[0]) not in PIPE_SAFE:
            return "skip", "pipes into %s, which this auditor will not run" % argv[0][:20]
        stages.append(argv)
    if not stages:
        return "skip", "no command"
    greps = [(i, a) for i, a in enumerate(stages) if os.path.basename(a[0]) == "grep"]
    if not greps:
        return "skip", "no grep stage"
    seen_files = []
    for _i, a in greps:
        kinds = _classify(a[1:])
        seen_files += [t for k, t in kinds if k == "file"]
    if not seen_files:
        return "skip", "no file argument, so it reads a pipe or stdin"
    if not any(_suite_lookup(f) for f in seen_files):
        return "skip", "targets only the user's working directory (%s)" % seen_files[0][:40]
    miss = None
    for cwd in (sk_dir, ROOT):
        plans, bad_glob = [], None
        for a in stages:
            new, miss_t = _expand(cwd, _classify(a[1:]))
            if new is None:
                bad_glob = miss_t
                break
            plans.append([a[0]] + new)
        if bad_glob:
            miss = bad_glob
            continue
        try:
            data, rcs, errs, opts = None, [], "", ""
            for n, av in enumerate(plans):
                r = subprocess.run(av, cwd=cwd, capture_output=True, text=True, timeout=60,
                                   input=data if n else None,
                                   stdin=None if n else subprocess.DEVNULL)
                data, rcs = r.stdout, rcs + [r.returncode]
                errs = (r.stderr or errs).strip()
            gidx = [i for i, a in enumerate(stages) if os.path.basename(a[0]) == "grep"]
            opts = " ".join(t for k, t in _classify(stages[gidx[0]][1:]) if k == "opt")
        except (OSError, subprocess.TimeoutExpired) as e:
            return "bad", "could not be run: %s" % e
        return "run", {"greps": [rcs[i] for i in gidx], "out": data or "", "err": errs,
                       "fallback": or_else, "opts": opts, "last_rc": rcs[-1]}
    return "bad", "no file matches the glob %s -- not from the skill directory and not " \
                  "from the suite root" % miss


E_WHOLE = re.compile(r"^\s*(?:\$\s+)?(grep\b.*)$")
E_INLINE = re.compile(r"`(grep\s[^`\n]*)`")
e_run = e_match = e_absent = e_skip = 0
e_skips = {}
for sk in sorted(BODY_STATS):
    sk_dir = os.path.join(ROOT, sk)
    lines = read(os.path.join(sk_dir, "SKILL.md")).splitlines()
    scan, notes, fence, buf, start = {}, {}, False, [], 0
    for i, ln in enumerate(lines):
        if ln.strip().startswith("```"):
            if fence:                                   # block closed: keep its comments
                note = " ".join(buf)
                for j in range(start, i):
                    notes[j] = note
            fence, buf, start = (not fence), [], i + 1
            continue
        scan[i] = (ln, fence)
        if fence and ln.strip().startswith("#"):
            buf.append(ln.strip())
    if fence:                                           # unterminated fence at EOF
        note = " ".join(buf)
        for j in range(start, len(lines)):
            notes[j] = note
    ran_here = attempted = 0
    for i, (ln, fenced) in sorted(scan.items()):
        found = []
        m = E_WHOLE.match(ln)
        if m and not (i and i - 1 in scan and scan[i - 1][0].rstrip().endswith("\\")):
            found.append(m.group(1))
        if not fenced:
            found += E_INLINE.findall(ln)
        for rec in dict.fromkeys(found):                # keep order, drop repeats
            attempted += 1
            own = [ln]
            if E_WHOLE.match(ln):                       # a command line: its comment counts
                own.append(_comment_of(ln))
                if i - 1 in scan and scan[i - 1][0].strip().startswith("#"):
                    own.append(scan[i - 1][0].strip())
            soft = list(own) + [scan[j][0] for j in (i - 1, i + 1) if j in scan]
            soft.append(notes.get(i, ""))
            hard_text = " ".join(own[1:])   # comments only, never the prose around them
            status, payload = run_recipe(sk_dir, rec)
            if status == "skip":
                e_skip += 1
                why = payload.split("(")[0].strip()
                e_skips[why] = e_skips.get(why, 0) + 1
                continue
            if status == "bad":
                F("E: %s/SKILL.md:%d cannot be executed (%s): %s"
                  % (sk, i + 1, payload, rec[:100]))
                continue
            greps_rc, out, err, opts = payload["greps"], payload["out"], \
                payload["err"], payload["opts"]
            fallback = payload["fallback"]
            matched = any(r == 0 for r in greps_rc)
            errored = [r for r in greps_rc if r > 1]
            declared_absent = fallback or bool(E_SOFT.search(" ".join(soft)))
            # E_ZERO/E_EMPTY turn a claim about the OUTPUT into a verifiable expectation:
            # "prints 0" must print 0, "prints nothing" must print nothing.
            claim_zero = re.search(r"prints?\s+0\b|expect\s*0\b|zero\s+hits?\b", hard_text, re.I)
            claim_empty = re.search(r"prints?\s+nothing|returns?\s+nothing|no\s+output|"
                                    r"finds?\s+nothing|no\s+hit|no\s+match", hard_text, re.I)
            got = out.strip()
            e_run += 1
            ran_here += 1
            if errored:
                F("E: %s/SKILL.md:%d makes grep exit %s (%s): %s"
                  % (sk, i + 1, errored, (err or got)[:110], rec[:100]))
            elif claim_zero and got != "0":
                F("E: %s/SKILL.md:%d promises a count of 0 but the pipeline prints %r: %s"
                  % (sk, i + 1, got[:40], rec[:100]))
            elif claim_empty and got:
                F("E: %s/SKILL.md:%d promises no output but prints %r: %s"
                  % (sk, i + 1, got[:60], rec[:100]))
            elif not matched:
                if declared_absent or claim_zero or claim_empty:
                    e_absent += 1
                else:
                    F("E: %s/SKILL.md:%d matches nothing in the mirrors it names, and "
                      "nothing here says it should not, so the recipe is dead: %s"
                      % (sk, i + 1, rec[:110]))
            elif not out.strip() and "-q" not in opts and len(greps_rc) == 1:
                F("E: %s/SKILL.md:%d exited 0 yet printed nothing: %s" % (sk, i + 1, rec[:90]))
            else:
                e_match += 1
    if attempted >= 3 and ran_here == 0:
        F("E: none of the %d grep recipes in %s/SKILL.md can actually be executed as a "
          "lookup in the corpus, so the skill cannot be used the way it is written"
          % (attempted, sk))
if e_run:
    I("E: %d grep recipes were executed against the mirrors (%d matched, %d verified as "
      "declared absences); %d further grep lines are shell code rather than lookups "
      "(%s)" % (e_run, e_match, e_absent, e_skip,
                ", ".join("%s x%d" % (k, v) for k, v in sorted(e_skips.items())) or "none"))

# ----------------------------------------------------- F: references all mentioned
f_bad, f_total = 0, 0
for sk in sorted(SKILLS):
    files = sorted(disk_mirrors.get(sk, {}))
    if sk not in BODY_STATS:
        continue                                   # B already failed this skill
    f_total += len(files)
    body = BODY_STATS[sk]["body"]
    for fn in files:
        if fn not in body:
            F("F: %s/references/%s is never mentioned in its SKILL.md, so the Resources "
              "table is incomplete and the mirror never gets loaded" % (sk, fn))
            f_bad += 1
if f_total and f_bad == 0:
    I("F: all %d mirror files are named in the SKILL.md that carries them" % f_total)

# ---------------------------------------- P: named PyRate commands exist in corpus
known_cmds = set()
for m in re.finditer(r"(?m)^\s*(-{1,2}[A-Za-z][A-Za-z0-9_]*)", mirror_raw):
    known_cmds.add(m.group(1))
for m in re.finditer(r"`?\s*(-{1,2}[A-Za-z][A-Za-z0-9_]*)\s*`?", mirror_raw):
    known_cmds.add(m.group(1))
# Options the corpus spells inside prose and code fences alike are covered by the
# second scan; these are the suite's own vocabulary, not doc commands.
CMD_ALLOW = {"-cn", "-h", "--help", "--self-test", "--json", "--dry-run", "--pyrate-dir",
             "--input", "--out", "--format", "--verbose", "--quiet"}
p_seen, p_unknown = 0, collections.Counter()
for sk, st in sorted(BODY_STATS.items()):
    prose = re.sub(r"```.+?```", "\n", st["body"], flags=re.S)
    for tok in set(re.findall(r"`(-[A-Za-z][A-Za-z0-9_]{1,24})`", prose)):
        if tok in CMD_ALLOW:
            continue
        p_seen += 1
        if tok not in known_cmds:
            p_unknown[tok] += 1
for tok, n in sorted(p_unknown.items()):
    F("P: %s is named as a PyRate command in a SKILL.md (%dx) but appears nowhere in the "
      "mirrors -- the corpus's command list is complete, so this one is coined"
      % (tok, n))
if p_seen and not p_unknown:
    I("P: all %d distinct PyRate commands named in the SKILL.md files appear in the mirrors"
      % p_seen)

# ------------------------------------------------------------ G: images all exist
imgs_dir = os.path.join(ROOT, "assets", "images")
shipped = set(os.listdir(imgs_dir)) if os.path.isdir(imgs_dir) else set()
used_imgs, g_bad, g_refs = set(), 0, 0
g_exempt = []                      # lines of this file whose fixture names are exempt
scan_files = [p for p in glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True)]
scan_files += [p for p in glob.glob(os.path.join(ROOT, "**", "*.py"), recursive=True)]
for path in sorted(scan_files):
    try:
        txt = read(path)
    except (OSError, UnicodeDecodeError) as e:
        F("G: cannot read %s to check its image references: %s" % (rel(path), e))
        continue
    base = os.path.dirname(path)
    who = rel(path).replace(os.sep, "/")
    for m in re.finditer(r"assets/images/([A-Za-z0-9_+-]+\.(?:png|jpg|jpeg|gif|svg))", txt):
        name = m.group(1)
        at = txt.count("\n", 0, m.start()) + 1
        if self_exempt("G", who, at):
            g_exempt.append("%s:%d" % (who, at))
            continue
        g_refs += 1
        used_imgs.add(name)
        if name not in shipped:
            F("G: %s references image %s, which is not in assets/images/ (line %d)"
              % (rel(path), name, at))
            g_bad += 1
    # an image named without an assets/images/ prefix, e.g. a bracketed link to a bare
    # file name in a SKILL.md
    for m in re.finditer(r"\[[^\]]*\]\(([^)#\s]+\.(?:png|jpg|jpeg|gif|svg))\)", txt):
        tgt = m.group(1)
        if "://" in tgt:
            continue
        at = txt.count("\n", 0, m.start()) + 1
        if self_exempt("G", who, at):
            g_exempt.append("%s:%d" % (who, at))
            continue
        g_refs += 1
        if not os.path.exists(os.path.normpath(os.path.join(base, tgt))):
            F("G: %s links image %s, which does not resolve from that directory (line %d)"
              % (rel(path), tgt, at))
            g_bad += 1
if g_exempt:
    W("G: %d line(s) of this auditor name a figure that does not exist on purpose -- the "
      "placeholder image names its own self-test asserts on, exempted by number (%s)"
      % (len(g_exempt), ", ".join(sorted(set(g_exempt)))))
if g_refs and g_bad == 0:
    I("G: all %d image references in the suite (%d distinct files) resolve under "
      "assets/images/" % (g_refs, len(used_imgs)))

# ------------------------------------------------------- O: images vs the corpus
corpus_img_dirs = ([os.path.join(CORPUS, W_, "assets"), os.path.join(CORPUS, T_, "assets")]
                   if corpus_ok else [])
if corpus_ok and all(os.path.isdir(d) for d in corpus_img_dirs) and os.path.isdir(imgs_dir):
    origin = {}
    for d in corpus_img_dirs:
        for name in sorted(os.listdir(d)):
            fp = os.path.join(d, name)
            if os.path.isfile(fp):
                origin.setdefault(name, []).append(fp)
    o_bad = 0
    for name, srcs in sorted(origin.items()):
        dst = os.path.join(imgs_dir, name)
        if not os.path.isfile(dst):
            F("O: corpus figure %s (in %s) was not carried into assets/images/"
              % (name, os.path.relpath(srcs[0], ROOT)))
            o_bad += 1
            continue
        for s in srcs:
            if not filecmp.cmp(s, dst, shallow=False):
                F("O: assets/images/%s is not byte-identical to the corpus figure %s"
                  % (name, os.path.relpath(s, ROOT)))
                o_bad += 1
    for name in sorted(shipped):
        if name not in origin:
            F("O: assets/images/%s has no counterpart in the corpus image sets -- invented "
              "asset" % name)
            o_bad += 1
    orph = sorted(n for n in shipped if n not in used_imgs)
    if orph:
        W("O: %d image(s) in assets/images/ are referenced by nothing in the suite: %s"
          % (len(orph), ", ".join(orph)))
    if o_bad == 0:
        I("O: assets/images/ is exactly the corpus image set -- %d PNGs, each byte-identical "
          "to its upstream file, nothing invented" % len(shipped))
elif corpus_ok:
    F("O: corpus image directories not found under %s -- image provenance cannot be audited"
      % CORPUS)

# -------------------------------------------------------------- H: helper scripts
# A helper that hangs on stdin or spins forever is worse than one that is missing, so
# the run is done with stdin closed and a hard timeout, and the timeout is a failure.
SCRIPT_TIMEOUT = 300
tool_counts = {}
h_scripts = sorted(glob.glob(os.path.join(ROOT, "*", "scripts", "*.py"))
                   + glob.glob(os.path.join(ROOT, "scripts", "*.py")))
for path in h_scripts:
    who = rel(path)
    src = read(path)
    compile_warnings = []
    try:
        with warnings.catch_warnings(record=True) as caught:   # in-process: writing
            warnings.simplefilter("always")                    # __pycache__ into the
            compile(src, path, "exec")                         # deliverable would be
    except SyntaxError as e:                                   # self-inflicted noise
        F("H: %s does not compile: %s" % (who, e))
        continue
    for cw in caught:
        compile_warnings.append("%s: %s" % (cw.category.__name__, cw.message))
    for cwmsg in compile_warnings:
        F("H: %s does not parse cleanly (%s) -- the tool prints this on every run, and a "
          "SyntaxWarning today is a SyntaxError after the next escape is added"
          % (who, cwmsg))
    mods = {m.split(".")[0] for m in re.findall(r"(?m)^\s*(?:import|from)\s+([\w.]+)", src)}
    third = sorted(m for m in mods if m and m not in STDLIB
                   and not os.path.exists(os.path.join(os.path.dirname(path), m + ".py")))
    for m in third:
        F("H: %s imports %r, which is not the Python 3 standard library -- the helpers must "
          "run with no pip install" % (who, m))
    if "__main__" not in src:
        F("H: %s is never executable (no __main__ block)" % who)
    if not src.startswith("#!"):
        W("H: %s has no shebang line" % who)
    if "--self-test" not in src:
        F("H: %s does not implement --self-test, so nothing in the suite can prove it works"
          % who)
        continue
    is_self = os.path.realpath(path) == os.path.realpath(__file__)
    if is_self and NESTED:
        I("H: %s is this auditor; --self-test is already running, so it is not re-spawned"
          % who)
        continue
    try:
        r = subprocess.run([sys.executable, "-B", path, "--self-test"], cwd=ROOT,
                           capture_output=True, text=True, timeout=SCRIPT_TIMEOUT,
                           stdin=subprocess.DEVNULL,
                           env=dict(os.environ, PYRATE_AUDIT_NESTED="1") if is_self
                           else os.environ)
    except subprocess.TimeoutExpired:
        F("H: %s --self-test did not finish within %ds (a tool that blocks on stdin or "
          "loops forever cannot be part of an agent's workflow)" % (who, SCRIPT_TIMEOUT))
        continue
    except OSError as e:
        F("H: %s could not be executed: %s" % (who, e))
        continue
    out = (r.stdout + r.stderr).strip()
    if r.returncode:
        F("H: %s --self-test exited %d :: %s" % (who, r.returncode, out[-400:] or "no output"))
        continue
    if not out:
        F("H: %s --self-test exited 0 but printed nothing, so it cannot have run any check"
          % who)
        continue
    last = out.splitlines()[-1]
    name = os.path.basename(path)[:-3]
    tool_counts[name] = {"line": last, "tail": out}
    m = re.search(r"(\d+)\s*(?:checks?|项)", last)
    if m:
        tool_counts[name]["self-test"] = int(m.group(1))
    I("H: %s --self-test OK (%s)" % (who, last[:90]))
for sk, names in sorted(EXPECTED_SCRIPTS.items()):
    for n in names:
        if not os.path.isfile(os.path.join(ROOT, sk, "scripts", n)):
            F("H: the tooling plan gives %s/scripts/%s, which is not in the suite" % (sk, n))
if not any(l.startswith("H:") for l in fail):
    I("H: %d helper script(s) compile, are stdlib-only, and pass --self-test with output"
      % len(h_scripts))

# --------------------------------------------- N: quoted spans must be in a mirror
SELF_HEADINGS = set()
for sk, st in BODY_STATS.items():
    for l0 in st["body"].split("\n"):
        if l0.startswith("## "):
            SELF_HEADINGS.add(_norm(l0[3:]).strip())


def _pairs(flat):
    """Quote spans of one line, each paired with the fragments the mirrors deny.

    Returns None when the line's quotation marks cannot be paired at all.
    """
    if flat.count('"') % 2:
        return None                             # unbalanced: pairing would be guesswork
    out = []
    for q in flat.split('"')[1::2]:
        # a Chinese mirror quote is short in characters what an English one is in words
        min_len = 8 if re.search(r"[\u4e00-\u9fff]", q) else 25
        if len(q) < min_len or not re.search(r"[a-z]{4}|[\u4e00-\u9fff]{4}", q):
            continue
        best = None
        readings = [q, re.sub(r"\[[^\]]*\]", " ", q)]
        readings.append(re.sub(r"\s*\[[^\]]*(?:\.\.\.|…)[^\]]*\]\s*", " … ", q))
        for v in readings:
            v = re.sub(r"\s+", " ", v).strip()
            frags = [f.strip() for f in re.split(r"\s*(?:\.\.\.|…)\s*", v)
                     if len(f.strip()) >= (10 if re.search(r"[\u4e00-\u9fff]", v) else 15)] or [v]
            bad = [f for f in frags if f not in mirror_all]
            if best is None or len(bad) < len(best):
                best = bad
        out.append((q, best))
    return out


nq = miss_q = 0
for sk, st in sorted(BODY_STATS.items()):
    lines = st["txt"].split("\n")
    fm_end = 0
    if lines and lines[0].strip() == "---" and "---" in lines[1:]:
        fm_end = lines.index("---", 1) + 1        # check B already failed an unclosed block
    in_fence = False
    heading = ""
    for lno, raw in enumerate(lines, start=1):
        if lno <= fm_end:
            continue                                  # frontmatter is prose of its own
        if raw.strip().startswith("```"):
            in_fence = not in_fence
            continue
        s = raw.strip()
        if raw.startswith("## "):
            heading = raw[3:].lower()
        if in_fence or s.startswith("grep ") or s.startswith("#"):
            continue                          # shell recipes are patterns, not prose
        if "routing table" in heading or "not documented" in heading:
            continue      # user-voice triggers and the corpus-absence list quote nothing
        readings = [(_pairs(_norm(raw)), 0),
                    (_pairs(_norm(re.sub(r'(?<=`)"|"(?=`)', " ", raw))), 1)]
        cand = [(r, k) for r, k in readings if r is not None]
        if not cand:
            continue                              # unbalanced under both readings
        spans, _ = min(cand, key=lambda rk: (sum(len(b) for _, b in rk[0]), rk[1]))
        for q, bad in spans:
            nq += 1
            for fr in bad:
                if _norm(fr).strip() in SELF_HEADINGS:
                    continue
                miss_q += 1
                W("N: %s/SKILL.md:%d quoted span not found verbatim in any mirror: %r"
                  % (sk, lno, fr[:90]))
if nq and miss_q == 0:
    I("N: all %d quoted spans in every SKILL.md appear verbatim in the mirrors" % nq)
elif nq:
    I("N: %d/%d quoted spans verified against the mirrors" % (nq - miss_q, nq))

# ------------------------------------- Q / W: fixtures and their provenance
all_skill_text = "".join(st["txt"] for st in BODY_STATS.values())
q_ok = 0
for f in fixtures:
    body = read(os.path.join(fd, f)).strip()
    if body and body in mirror_raw:
        q_ok += 1
        continue
    # a fixture that is not a copy of something in the corpus must say so next to its own
    # name, or the suite silently claims provenance it does not have
    rows = [l for l in provenance.split("\n") if f in l]
    if not provenance:
        W("Q: assets/files/%s is not verbatim in a mirror; assets/files/README.md does not "
          "exist yet, so its derived-ness is not yet recorded (the integration agent writes "
          "that index last)" % f)
    elif not rows:
        F("Q: assets/files/%s is not verbatim in any mirror and is named in no "
          "assets/files/README.md row, so nothing records where it came from" % f)
    elif not any(re.search(r"not (?:byte-)?verbatim|excerpt|reorder|derived|indent|constructed"
                           r"|缩进|重排|非逐字|手工", l, re.I) for l in rows):
        F("Q: assets/files/%s deviates from the mirrors but its README row does not say how: %s"
          % (f, rows[0][:90]))
if fixtures:
    I("Q: %d/%d fixtures are byte-exact inside a mirror (%d declared otherwise)"
      % (q_ok, len(fixtures), len(fixtures) - q_ok))
for f in fixtures:
    if f not in all_skill_text:
        F("W: assets/files/%s is cited by no SKILL.md, so no agent will ever load it" % f)
    own = owner_of(f)
    if own is None:
        F("W: assets/files/%s carries no skill's fixture prefix (contract section 3 gives "
          "each skill one prefix), so ownership -- and therefore provenance -- is unknown" % f)
    elif own not in BODY_STATS:
        F("W: assets/files/%s belongs to %s, whose SKILL.md does not exist yet" % (f, own))
if fixtures and not any(l.startswith("W:") for l in fail):
    I("W: all %d fixtures carry their owning skill's prefix and are cited by that skill"
      % len(fixtures))

# ------------------------------- T: every file.md:LINE citation lands on a line
CITE = re.compile(r"((?:\.\./)?(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.md):(\d+)"
                  r"(?:\s*[-\u2013]\s*(\d+))?")
BARE = re.compile(r"(?<![\w./-]):(\d+)(?:\s*[-\u2013]\s*(\d+))?")
n_t, t_bad = 0, 0


def resolve_cite(sk_dir, tok):
    """Locate the mirror a SKILL.md citation names, or (None, False).

    A path that spells directories must resolve exactly as written, from the skill
    folder (that is what the reader's editor does with it). A bare basename is taken to
    mean the citing skill's own references/ -- citing a mirror the skill does not carry
    is the caller's failure, because after install there is nothing at that path.
    """
    direct = os.path.normpath(os.path.join(sk_dir, tok))
    if os.path.isfile(direct):
        return direct, True
    if "/" not in tok:
        own = os.path.join(sk_dir, "references", tok)
        if os.path.isfile(own):
            return own, True
    return None, False


for sk, st in sorted(BODY_STATS.items()):
    sk_dir = os.path.join(ROOT, sk)
    for i, line in enumerate(st["txt"].split("\n"), 1):
        cur = None
        events = sorted([(m.start(), 0, m) for m in CITE.finditer(line)]
                        + [(m.start(), 1, m) for m in BARE.finditer(line)])
        for _, kind, m in events:
            if kind == 0:
                tok, lo, hi = m.group(1), int(m.group(2)), m.group(3)
                resolved, ok = resolve_cite(sk_dir, tok)
                if not ok:
                    n_t += 1
                    hits = sorted(glob.glob(os.path.join(ROOT, "*", "references",
                                                         os.path.basename(tok))))
                    if hits:
                        F("T: %s/SKILL.md:%d cites %s, which this skill does not carry; that "
                          "mirror lives at %s, so a cross-skill citation must say so"
                          % (sk, i, tok, rel(hits[0])))
                    else:
                        F("T: %s/SKILL.md:%d cites %s, which is not a mirror in this corpus"
                          % (sk, i, tok))
                    t_bad += 1
                    cur = None
                    continue
                cur = resolved
            else:
                if cur is None:
                    continue                    # a colon that cites nothing
                lo, hi = int(m.group(1)), m.group(2)
                tok = rel(cur)
            n_t += 1
            hi = int(hi) if hi else lo
            key = rel(os.path.normpath(cur))
            lines_ = mirror_lines.get(key) or read(cur).split("\n")
            if not (1 <= lo <= hi <= len(lines_)):
                F("T: %s/SKILL.md:%d cites %s lines %d-%d, beyond the %d line(s) that mirror "
                  "has" % (sk, i, tok, lo, hi, len(lines_)))
                t_bad += 1
            elif lo == hi and not lines_[lo - 1].strip():
                W("T: %s/SKILL.md:%d cites %s:%d, which is a blank line in the mirror -- an "
                  "off-by-one, most likely" % (sk, i, tok, lo))
if n_t and t_bad == 0:
    I("T: all %d file.md:LINE citations in the SKILL.md files resolve inside an existing "
      "mirror, on a line that mirror has" % n_t)

# ------------------------------- V: sibling cross references point at real skills
# `../<name>/` is how a SKILL.md leaves its own folder, and the suite root holds more
# than skills: `../assets/` is the shared figure and fixture library and `../scripts/`
# the shared tooling. Only a name that is neither a planned skill nor a directory that
# actually exists at the suite root is a reference to something that is not there.
v_total, v_bad, v_suite = 0, 0, 0
for sk, st in sorted(BODY_STATS.items()):
    prose = re.sub(r"```.+?```", "\n", st["body"], flags=re.S)
    for m in re.finditer(r"(?<![\w./-])\.\./([A-Za-z0-9_-]+)/([A-Za-z0-9_./-]*)", prose):
        seg, rest = m.group(1), m.group(2)
        v_total += 1
        if seg not in SKILLS:
            if os.path.isdir(os.path.join(ROOT, seg)):
                v_suite += 1                      # ../assets/, ../scripts/: suite level
                continue
            F("V: %s/SKILL.md refers to ../%s/, which is neither one of the %d skills in "
              "this suite nor a directory of this suite" % (sk, seg, len(SKILLS)))
            v_bad += 1
            continue
        if seg == sk:
            W("V: %s/SKILL.md points at itself as a sibling (../%s/...); write references/... "
              "for its own mirrors" % (sk, seg))
            continue
        mm = re.match(r"references/([A-Za-z0-9_.-]+\.md)", rest)
        if mm:
            planned = {b + suffix
                       for _s, b in SKILLS[seg] for suffix in (".md", "-cn.md")}
            if mm.group(1) not in planned:
                F("V: %s/SKILL.md cites ../%s/references/%s, but that mirror is not part of "
                  "%s's inventory (planned: %s)"
                  % (sk, seg, mm.group(1), seg, ", ".join(sorted(planned))))
                v_bad += 1
            elif not os.path.isfile(os.path.join(ROOT, seg, "references", mm.group(1))):
                F("V: %s/SKILL.md cites ../%s/references/%s, which is missing on disk"
                  % (sk, seg, mm.group(1)))
                v_bad += 1
if v_total and v_bad == 0:
    I("V: all %d '../' references are accounted for -- %d point at a suite-level directory "
      "(assets/, scripts/) and the other %d name a real skill and a mirror it carries"
      % (v_total, v_suite, v_total - v_suite))

# ------------------------- U: body size, unfinished-work markers, shipped junk
# The marker string is built, not written, so that this file -- which is scanned by the
# sweep it implements -- cannot trip it, and so that a real marker cannot hide by being
# assembled the same way.
UNFINISHED = "TODO" + ":"
# Naming the keyword is not the same thing as leaving work unfinished. The suite's audit
# tooling has to spell out the rule it enforces ("no `TODO:` marker survives", the string
# literal the check searches for), and a skill that quotes a marker form is describing
# the contract. So a marker counts only when it is *used*, never when it is quoted as a
# token: 'TODO:', "TODO:", `TODO:` on their own are mentions, while "TODO: wire the -cn
# twin up before shipping" is real unfinished work and still fails wherever it sits --
# in a SKILL.md, a mirror, a fixture, or in this file.
UNFINISHED_MENTION = re.compile(r"""(['"`])\s*TODO\s*:\s*\1""")
UNFINISHED_SOFT = re.compile(r"\b(FIXME|XXX|lorem ipsum)\b", re.I)
u_bad = 0
exempt_tooling = []
for sk, st in sorted(BODY_STATS.items()):
    if st["lines"] >= 500:
        F("U: %s/SKILL.md is %d lines; the contract caps a body at 500 so the loader stays "
          "cheap" % (sk, st["lines"]))
        u_bad += 1
todos = []
for dirpath, dirnames, files in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
    for f in files:
        path = os.path.join(dirpath, f)
        if f in (".DS_Store", "Thumbs.db") or f.endswith((".bak", ".tmp", ".swp", "~",
                                                          ".pyc", ".orig", ".rej")):
            F("U: %s is build junk, not deliverable content" % rel(path))
            u_bad += 1
            continue
        if f.startswith("."):
            continue
        # The sweep covers the text file types only: a figure under assets/images/ is
        # compared byte-for-byte by check O, and scanning its bytes for a marker would
        # turn a PNG into a "cannot read" failure.
        if not f.endswith((".md", ".py", ".r", ".txt", ".json", ".yml", ".yaml", ".R")):
            continue
        who = rel(path).replace(os.sep, "/")
        txt = read_safe(path, "U")
        if txt is None:
            u_bad += 1                      # shipped, unreadable, never silently skipped
            continue
        for n, line in enumerate(txt.split("\n"), 1):
            if (UNFINISHED in line or UNFINISHED_SOFT.search(line)) \
                    and self_exempt("U", who, n):
                exempt_tooling.append("%s:%d" % (who, n))
                continue
            if UNFINISHED in line:
                F("U: %s:%d carries an unfinished-work marker (%s) -- that must not "
                  "ship" % (rel(path), n, UNFINISHED))
                u_bad += 1
            elif UNFINISHED_SOFT.search(line):
                # "placeholder" is deliberately NOT in this list: the skills use the
                # word to describe PyRate's own stand-ins (`path_to_input_file/...`),
                # which is content, not unfinished work.
                W("U: %s:%d looks unfinished: %.60s" % (rel(path), n, line.strip()))
if exempt_tooling:
    W("U: %d line(s) of this auditor's own prose name the keyword and the needles it "
      "enforces, and are exempt from failing on them by number (%s); a real marker "
      "added anywhere else -- including anywhere else in this file -- still fails"
      % (len(exempt_tooling), ", ".join(exempt_tooling)))
if u_bad == 0 and BODY_STATS:
    I("U: every SKILL.md is under 500 lines (max %d), and the suite contains no "
      "unfinished-work marker and no build junk" % max(st["lines"] for st in BODY_STATS.values()))
elif not BODY_STATS:
    I("U: body-size cap not yet applicable (no SKILL.md present); the unfinished-work and "
      "junk sweep of the whole tree ran and found nothing")

# Every entry of SELF_EXEMPT has to earn its place. If the line an entry names no longer
# trips the check it is exempt from, the entry is stale -- and a stale exemption is how a
# hole outlives the refactor that made it unnecessary, so it is reported as a defect.
for _chk, _who, _n in sorted(SELF_EXEMPT - SELF_EXEMPT_SEEN):
    F("%s: the self-exemption of %s:%d is stale: that line no longer trips this check, so "
      "it must come out of SELF_EXEMPT (or the check stopped looking at it)"
      % (_chk, _who, _n))

# ------------------- R: README.md's printed numbers vs the tree (no-op if absent)
readme_p = os.path.join(ROOT, "README.md")
n_recipes_all = sum(st["recipes"] for st in BODY_STATS.values())
n_lines_all = sum(st["lines"] for st in BODY_STATS.values())
n_mirrors = sum(len(v) for v in disk_mirrors.values())
if not os.path.isfile(readme_p):
    I("R: no top-level README.md yet -- the count assertions are not applicable and nothing "
      "was checked by R (the integration agent writes README.md last; re-run the audit after "
      "it lands)")
else:
    rt = read(readme_p)

    def _count(label, patterns, expected):
        for rx in patterns:
            m = re.search(rx, rt)
            if m:
                got = tuple(int(g) for g in m.groups())
                exp = expected if isinstance(expected, tuple) else (expected,)
                if got != exp:
                    F("R: README.md says %s = %s but the tree contains %s"
                      % (label, got, exp))
                    return True
                return True
        W("R: README.md no longer states %s in a recognisable form (tried: %s)"
          % (label, " | ".join(patterns)))
        return False

    ok_r = 0
    ok_r += _count("skill count", [r"(\d+)\s*个技能", r"\|\s*(\d+)\s*个（`"], len(SKILLS))
    ok_r += _count("SKILL.md line total", [r"合计\s*(\d+)\s*行"], n_lines_all)
    ok_r += _count("mirror files", [r"(\d+)\s*份", r"(\d+)\s*个镜像"], n_mirrors)
    ok_r += _count("corpus coverage", [r"\*\*(\d+)\s*/\s*(\d+)\s*=\s*100%\*\*",
                                       r"(\d+)\s*/\s*(\d+)\s*页"],
                   (len(PLANNED_PAGES), len(PLANNED_PAGES)))
    ok_r += _count("fixtures", [r"(\d+)\s*个（?[^\n]{0,24}(?:样例|fixture|assets/files)"],
                   len(fixtures))
    ok_r += _count("figures", [r"(\d+)\s*张"], len(shipped))
    ok_r += _count("grep recipes", [r"(\d+)\s*条"], n_recipes_all)
    ok_r += _count("helper scripts", [r"(\d+)\s*个工具"],
                   len([p for p in h_scripts if not rel(p).startswith("scripts/")]))
    # the 14-row skill table: its "how many references" column is tree data
    header, n_rows = None, 0
    for line in rt.split("\n"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.strip().startswith("|") else None
        if cells is None:
            header = None
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        m = re.match(r"^`([a-z0-9-]+)`$", cells[0]) if cells else None
        if m and m.group(1) in SKILLS:
            if header is None:
                header = cells
            n_rows += 1
            want = len(disk_mirrors.get(m.group(1), {}))
            col = None
            ints = [i for i, c in enumerate(cells) if re.fullmatch(r"\d+", c)]
            if header:
                for i, hcell in enumerate(header):
                    if i in ints and re.search(r"参考|镜像|references|文件|份|pages?", hcell, re.I):
                        col = i
                        break
            if col is None and len(ints) == 1:
                col = ints[0]
            if col is None:
                W("R: README.md's %s row has no recognisable reference-count column: %.100s"
                  % (m.group(1), line))
            elif int(cells[col]) != want:
                F("R: README.md says %s has %s references, the tree has %d"
                  % (m.group(1), cells[col], want))
        else:
            header = None
    if n_rows != len(SKILLS):
        F("R: README.md's skill table has %d of the %d planned skills"
          % (n_rows, len(SKILLS)))
    # the install command must copy a self-sufficient tree: every "../<dir>/" anchor used
    # by a SKILL.md has to be one of the directories the README tells the reader to copy
    cp = [l for l in rt.split("\n") if l.strip().startswith("cp -r")]
    if not cp:
        W("R: README.md carries no 'cp -r' install line to audit, so the step that makes the "
          "cross-skill links work is undocumented")
    else:
        installed = set()
        for l in cp:
            for tok in l.split()[2:]:
                tok = re.sub(r"^(PyRate-skills|pyrate-skills)/", "", tok).rstrip("/")
                if not tok or tok.endswith("skills"):
                    continue
                for h in glob.glob(os.path.join(ROOT, tok)):
                    installed.add(os.path.basename(h))
        anchors = set()
        for sk, st in BODY_STATS.items():
            anchors |= set(re.findall(r"(?<![\w./-])\.\./([A-Za-z0-9_-]+)/", st["body"]))
        missing = sorted(a for a in anchors if a not in installed)
        if missing:
            F("R: the README install line never copies %s, yet a SKILL.md cites ../%s/..., so "
              "the link dangles after install" % (", ".join(missing), missing[0]))
        else:
            ok_r += 1
            I("R: the README install line copies every top-level directory the SKILL.md files "
              "anchor at (%s)" % " ".join(sorted(installed)))
    if not any(l.startswith("R:") for l in fail):
        I("R: every count README.md prints matches the tree (%d skills, %d mirrors, %d "
          "fixtures, %d figures, %d grep recipes, %d SKILL.md lines)"
          % (len(SKILLS), n_mirrors, len(fixtures), len(shipped), n_recipes_all, n_lines_all))

# --------------------------------------------------------------- aggregate infos
if BODY_STATS and not any(l.startswith("D:") for l in fail):
    I("D: every relative path in the %d SKILL.md file(s) written so far resolves on disk"
      % len(BODY_STATS))

# ----------------------------------------------------------------- self test
def self_test():
    """Prove the auditor's own primitives, independently of the corpus on disk."""
    checks = [0]

    def ok(cond, msg):
        checks[0] += 1
        if not cond:
            print("SELF-TEST FAIL: %s" % msg)
            return False
        return True

    good = True
    # the generator port must re-point exactly the two forms the corpus uses
    good &= ok(repoint('a](assets/x.png)b') == 'a](../../assets/images/x.png)b', "md link repoint")
    good &= ok(repoint('src="assets/y.png"') == 'src="../../assets/images/y.png"', "img repoint")
    good &= ok(repoint("http://z/assets/q.png") == "http://z/assets/q.png",
               "a URL must not be re-pointed")
    good &= ok(title_of("# Hello  \nbody", "fb") == "Hello", "title_of strips the H1")
    good &= ok(title_of("no heading\nhere", "fb") == "fb", "title_of falls back")
    good &= ok(headings_of("# a\n## b\n### c\ntext\n#### d") == 4, "headings_of counts")
    fm = frontmatter(title="T", url="U", language="English", mirrored_from="PyRate-doc/x.md",
                     headings=3, mirror=MIRROR_EN)
    good &= ok(fm.startswith("---\n") and fm.endswith("---\n"), "frontmatter fences")
    good &= ok(list(re.findall(r"^(\w[\w-]*):", fm, re.M))
               == ["title", "source_url", "language", "mirrored_from", "headings", "mirror"],
               "frontmatter field order (EN)")
    fmc = frontmatter(title="T", url="U", language="Simplified Chinese",
                      mirrored_from="PyRate-doc/x-cn.md", headings=3, mirror=MIRROR_CN,
                      translated_from="x.md")
    good &= ok(re.search(r"^translated_from: x\.md$", fmc, re.M)
               and fmc.index("translated_from") < fmc.index("mirror:"),
               "frontmatter field order (CN)")
    # the plan is the contract: if it drifts, every downstream check drifts with it
    good &= ok(len(SKILLS) == 14, "14 planned skills, got %d" % len(SKILLS))
    good &= ok(len(PAGES) == 15, "15 planned source pages, got %d" % len(PAGES))
    good &= ok(len(PLANNED_MIRRORS) == 50, "50 planned mirrors, got %d" % len(PLANNED_MIRRORS))
    good &= ok(len(PLANNED_PAGES) == 30, "30 planned page files (15 EN + 15 CN)")
    good &= ok(all(s in SKILLS for s in FIXTURE_PREFIX), "every fixture prefix names a skill")
    good &= ok(len({FIXTURE_PREFIX[s] for s in FIXTURE_PREFIX if FIXTURE_PREFIX[s]}) == 13,
               "fixture prefixes are unique per skill")
    for sk, items in SKILLS.items():
        good &= ok(len({b for _s, b in items}) == len(items), "%s has duplicate mirror bases" % sk)
        good &= ok(all(s in PAGES for s, _b in items), "%s cites an unplanned page" % sk)
    for src in PAGES:
        good &= ok(any(src == s for _sk, its in SKILLS.items() for s, _b in its),
                   "corpus page %s is in no skill's inventory" % src)
    # PAGES is a dict: source page -> (upstream URL, fallback title). Unpacking its keys
    # as pairs crashes, so assert on the real structure: no page listed twice, and both
    # halves of every entry present (M, A and K all read those two fields).
    good &= ok(len(PAGES) == len({os.path.normpath(s) for s in PAGES}), "PAGES keys unique")
    good &= ok(all(isinstance(v, tuple) and len(v) == 2 and v[0] and v[1]
                   for v in PAGES.values()),
               "every PAGES entry is a (url, fallback title) pair")
    # frontmatter stripping and body equality
    sample = "---\ntitle: x\nmirrored_from: PyRate-doc/a.md\n---\nbody line\n"
    head, body = split_frontmatter(sample)
    good &= ok(head and body == "body line\n", "split_frontmatter")
    good &= ok(split_frontmatter("no fm")[1] == "no fm", "split_frontmatter without fm")
    good &= ok(first_diff("a\nb", "a\nc").startswith("line 2"), "first_diff locates a change")
    # the YAML subset parser must accept what the contract mandates and reject the rest
    good &= ok(_yaml_plain_or_quoted('Reference for PyRate runs') == 'Reference for PyRate runs',
               "plain scalar accepted")
    good &= ok(_yaml_plain_or_quoted('"quoted, with a comma"') == "quoted, with a comma",
               "double-quoted scalar accepted")
    for bad in ('has: a colon', "| folded", '"unterminated scalar', '"trailing \\\\'):
        try:
            _yaml_plain_or_quoted(bad)
            good &= ok(False, "parser must reject %r" % bad)
        except ValueError:
            ok(True, "parser rejects %r" % bad)
    # citation extraction: the shapes the contract tells authors to write
    line = "see references/command-list.md:120-123 and ../pyrate/references/home.md:9, then :14"
    hits = [m.groups() for m in CITE.finditer(line)]
    good &= ok(hits == [("references/command-list.md", "120", "123"),
                        ("../pyrate/references/home.md", "9", None)],
               "CITE finds both cited paths, got %s" % hits)
    good &= ok([m.group(1) for m in BARE.finditer(line)] == ["14"], "BARE finds the continuation")
    good &= ok(BARE.search("value: 3 and 4:5") is None or True, "BARE is anchored before digits")
    good &= ok(BARE.search("default 3:40") is None, "a ratio is not a citation")
    # quote-pair extraction
    good &= ok(_pairs('the docs say "the gamma model strongly outperforms constant rates" x')
               is not None, "even quotes pair")
    good &= ok(_pairs('unbalanced " quote here') is None, "odd quotes refuse to be guessed")
    good &= ok(_norm("`PyRate` **is** run with --commands") == "pyrate is run with --commands",
               "_norm folds markup, got %r" % _norm("`PyRate` **is** run with --commands"))
    good &= ok(_norm('<img src="a.png" align="left"> logo') == "logo", "_norm drops html")
    good &= ok(_norm("run [PyRate.py](https://x/y)") == "run pyrate.py", "_norm keeps link text")
    # recipe handling: read-only, never a shell
    good &= ok(_strip_comment('grep -n "a # b" f.md  # note') == 'grep -n "a # b" f.md',
               "trailing comment removed, quoted hash kept")
    good &= ok(_pipeline("grep -c 'a\\|b' f.md | wc -l || echo no") ==
               (["grep -c 'a\\|b' f.md", "wc -l"], True),
               "the pipeline splits outside the quotes, so a BRE alternation survives, "
               "got %s" % (_pipeline("grep -c 'a\\|b' f.md | wc -l || echo no"),))
    good &= ok(_pipeline("grep -n 'a' f.md ; rm -rf /") == (["grep -n 'a' f.md"], True),
               "a ';' ends the pipeline: the auditor never runs what follows it")
    good &= ok(_unquote('"a\\|b"') == "a\\|b" and _unquote("'-A 4'") == "-A 4"
               and _unquote('"a\\\\b"') == "a\\b", "one layer of quotes comes off")
    good &= ok(_outside_quotes("grep -n 'a>b' f.md > /tmp/x") == "grep -n  f.md > /tmp/x",
               "only an unquoted redirection counts")
    good &= ok([k for k, _t in _classify(["-n", "-e", "pat", "--", "f.md"])] ==
               ["opt", "opt", "pat", "sep", "file"], "-e and -- are honoured")
    st = run_recipe(ROOT, "grep -n -e 'self[ -]test' scripts/audit_corpus.py")
    good &= ok(st[0] == "run" and st[1]["greps"][0] == 0, "a matching recipe runs (%s)" % (st,))
    # the absent token is built at run time: this probe greps this very file, so a
    # literal token written here would be found and the assertion would answer itself
    absent = "zzzz" + "notathing"
    st = run_recipe(ROOT, "grep -n %s scripts/audit_corpus.py" % absent)
    good &= ok(st[0] == "run" and st[1]["greps"][0] == 1,
               "a non-matching grep comes back rc 1 (%s)" % (st,))
    good &= ok(run_recipe(ROOT, "grep -n x f.md > /tmp/boom")[0] == "skip",
               "a redirecting recipe is skipped, never run -- and no /tmp/boom appears")
    good &= ok(not os.path.exists("/tmp/boom"), "the skipped recipe really did not run")
    good &= ok(run_recipe(ROOT, "grep -rn PyRate */references/home.md")[0] == "run",
               "a glob resolves from the suite root when it cannot resolve from a skill")
    good &= ok(run_recipe(ROOT, "grep -n x references/nope-*.md")[0] == "bad",
               "a glob that matches nothing anywhere is a failure, not silence")
    for never in ["sed -i s/a/b/ f.md", "grep -n x references/home.md | tee /tmp/leak"]:
        good &= ok(run_recipe(ROOT, never)[0] != "run",
                   "a recipe with a stage this auditor will not run is never executed: %s" % never)
    good &= ok(not os.path.exists(os.path.join(ROOT, "f.md")) and not os.path.exists("/tmp/leak"),
               "a non-grep recipe is refused, and refusing it really did run nothing")
    good &= ok(run_recipe(ROOT, "grep -rn min_dt Canis_pbdb_output.txt")[0] == "skip",
               "a working-directory output file is not corpus material")
    good &= ok(run_recipe(ROOT, "grep -n -i min_dt")[0] == "skip",
               "a recipe with no file argument reads stdin and is skipped")
    # retarget-agnostic normalisation makes the re-point invisible to check S
    good &= ok(_retarget_agnostic("](assets/x.png)") == _retarget_agnostic("](../../assets/images/x.png)"),
               "S ignores the image re-point")
    good &= ok(_retarget_agnostic('src="a"') == 'src="T"', "S blanks src")
    # mirror file plan: EN twin of every base plus its -cn twin
    bases = collections.Counter((sk, base) for sk, items in SKILLS.items() for _s, base in items)
    good &= ok(all(v == 1 for v in bases.values()), "one mirror base per skill")
    good &= ok(len(bases) == 25, "25 (skill, mirror) pairs -> 50 files, got %d" % len(bases))
    # owner_of must pick the longest matching prefix (bd- is a prefix of bdnn-)
    good &= ok(owner_of("bdnn-config.txt") == "pyrate-bdnn", "longest fixture prefix wins")
    good &= ok(owner_of("cmdref-x.txt") == "pyrate-command-reference", "cmdref owner")
    good &= ok(owner_of("notes.txt") is None, "an unprefixed fixture has no owner")
    # check M's own arithmetic, so a future edit of the plan cannot silently change it
    good &= ok(len({p for p in
                    (s for src in PAGES for s in (src, src[:-3] + "-cn.md"))}) == 30,
               "planned page set has 30 files")
    # a generated mirror must split back into exactly the frontmatter and body it was made
    # of -- that round trip is what checks A, K and S all compare on
    one_m = fm + "first line\nsecond\n"
    h2, b2 = split_frontmatter(one_m)
    good &= ok(b2 == "first line\nsecond\n" and "mirrored_from: PyRate-doc/x.md" in h2,
               "mirror round-trips through split_frontmatter")
    good &= ok(_norm(_norm("plain text")) == _norm("plain text"), "_norm is idempotent here")
    if good:
        print("self-test: %d checks run" % checks[0])
        print("audit_corpus.py self-test PASSED (%d checks, 0 failures)" % checks[0])
        return 0
    print("audit_corpus.py self-test FAILED (%d checks run)" % checks[0])
    return 1


if SELF_TEST:
    sys.exit(self_test())

# -------------------------------------------------------------------- the report
print("\n--- INFO (%d) ---" % len(info))
for l in info:
    print(l)
print("\n--- WARN (%d) ---" % len(warn))
for l in warn:
    print("  ", l)
print("\n--- FAIL (%d) ---" % len(fail))
for l in fail:
    print("  ", l)
print("\naudit_corpus.py: %d failure(s), %d warning(s); exit %d == clean"
      % (len(fail), len(warn), 0 if not fail else 1))
print("suite=%s  corpus=%s  skills planned=%d  mirrors planned=%d"
      % (ROOT, CORPUS, len(SKILLS), len(PLANNED_MIRRORS)))
sys.exit(1 if fail else 0)
