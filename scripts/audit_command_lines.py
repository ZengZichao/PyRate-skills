#!/usr/bin/env python3
r"""Command-line gate: every flag the documentation tells a user to type must be one the
suite's own tooling can account for.

WHY THIS EXISTS
  `pyrate-command-reference/scripts/build_command.py` parses the accepted PyRate
  command set out of the mirror `references/command-list.md` (plus a cited extensions
  table) and refuses anything else. The mirrors and the SKILL.md files, on the other
  hand, carry command lines copied from the corpus. Nothing until now compared the
  two: a documented `-hsp 0` could sit in a mirror for months while the builder
  rejected it as an unknown command -- i.e. the skill tells the user to run a command
  that the skill's own tooling calls invalid. This gate is that comparison, done from
  the outside: it never reads the builder's source, it asks the builder what it
  accepts (`build_command.py --list`) and then reads what the documentation says.

SCOPE OF THE BUILDER -- READ THIS BEFORE TRUSTING A NUMBER BELOW
  The builder describes exactly one program: PyRate.py. Its accepted set is parsed
  from `references/command-list.md`, which is the mirror of the wiki page
  "2. PyRate: command list", plus EXTENSIONS cited from other pages; `--list` prints
  "Commands parsed from .../command-list.md (50 core)" and nothing about any other
  program. That limitation is MEASURED, not assumed: `builder_scope()` runs the builder
  and `scope_lines()` prints what it found, on every run, so this prose is never more
  current than the block above the counts. Measured on the tree this gate ships with:

    * `build_command.py --list` reports a grammar for PyRate.py only (109 flags).
    * `build_command.py --program NAME` renames the program token in the emitted line;
      it never switches grammar. The probe
        python3 pyrate-command-reference/scripts/build_command.py \
            --program PyRateContinuous.py -d x.txt -m 1 -c temp.txt
      exits 4, i.e. the two flags the Continuous page documents (`-m`, `-c` -- read it
      at pyrate-continuous-covariates/references/pyratecontinuous.md:31 and :34) are not
      accepted for it. As first measured, `--program PyRateContinuous.py` was accepted
      and printed `COMMAND: python PyRateContinuous.py ...` for a line whose grammar had
      just been checked against PyRate.py's page; the builder now refuses a `--program`
      value it has no grammar for and names, in the refusal, the mirror where each other
      program's own options are documented. Either way the gate's arithmetic is the same,
      and `scope_lines()` prints which of the two the builder does today.
    * whether `--help` mentions `--program` is measured too, because a limitation a
      reader cannot find in the usage text is a limitation they will trip over.
  Consequence, and the reason this gate used to print 213 false failures: a documented
  `PyRateContinuous.py`, `PyRateMCDD.py`, `PyRateMBD.py`, `PyRateDES.py` or
  `PyRateDES2.py` line CANNOT be judged against `--list`. Doing so charges each of those
  programs' own flags (`-m`, `-c`, `-DD`, `-TdD`, `-qtimes`, `-varE`, `-traitD`,
  `-fossil`, `-recent`, `-filename`, ...) to a grammar that never claimed to cover them.
  Redesigning the builder is out of scope here (another agent owns it); what this gate
  does instead is classify by program token and be exact about what it verified:

    PyRate.py lines            -> judged against `--list`. A flag `--list` does not
                                  report is a HARD failure (UNKNOWN-FLAG), exactly as
                                  before: the builder refuses that documented line.
    the other five programs    -> the builder has no grammar to appeal to, so the flag
                                  is judged against THAT PROGRAM'S OWN DOCUMENTATION in
                                  the mirrors (see HOW A FLAG IS JUDGED OUT OF SCOPE).
                                  Every one of these is counted and printed as
                                  OUT OF BUILDER SCOPE -- never dropped, never folded
                                  into the "accepted by the builder" number, and the
                                  RESULT line states both counts.

  What out-of-builder-scope does NOT mean: it is not a pass. The builder cannot assemble
  those lines today, so the suite ships documentation that its own tool will not build.
  Until the builder grows per-program grammars, the honest reading of an
  out-of-builder-scope count is "the gate could not verify this against a grammar", and
  the block prints that number first, before any verdict.

HOW A FLAG IS JUDGED OUT OF SCOPE
  `program_docs()` harvests, from the mirrors only (never from a SKILL.md, which is the
  derived text and the thing being checked), what each program's own documentation
  shows it taking:
    "usage"      a flag on a documented command line whose program token is that program
                 -- the mirror shows the program run with it;
    "definition" a flag the mirrors DEFINE (`##### \`-c\``, `* \`-traitD\` is ...`) in a
                 heading whose title names the program, or within
                 DEF_WINDOW lines of the program's name, or in a page whose frontmatter
                 `title:` / `mirrored_from:` is that program's own page.
    "prose"      a flag NAMED in prose -- an inline code span whose whole text is exactly
                 one flag token (`using the flags `-n` and `-s`, respectively`,
                 pyrate-continuous-covariates/references/tutorial-2.md:110; `the number of
                 iteration (as specified by the flag `-n`)`, same file :151). This is the
                 third shape the corpus uses to tell a reader "this program takes this
                 option", and a gate that reads only the first two calls it a coined flag:
                 every `-n`/`-s` on a documented PyRateContinuous.py line was reported HARD
                 while Continuous' own mirror named both. It shares the scope rule with
                 "definition" -- both go through `page_programs()`, one code path -- so a
                 prose mention counts for the program named in its window or in its page
                 frontmatter and for no other program, and unquoted prose stays no evidence
                 at all. Requiring the whole span to be one flag token keeps an example with
                 a value (`-wd path_to_target_directory`,
                 pyrate-bd-analysis/references/command-list.md:25) out of the
                 harvest, so the added source adds no flag that the mirrors do not also name.
  A flag on a `PyRateDES.py` line that appears nowhere in the DES documentation is a
  HARD failure (UNDOCUMENTED-FLAG): that is a coined flag, and the per-program split is
  what makes it fail -- `-qtimes` is documented for PyRateDES.py and not for
  PyRateMBD.py, so a MBD line carrying it is charged, not excused. Widening the evidence
  to prose does not widen that: `-wd` is named for PyRate.py
  (pyrate-bd-analysis/references/command-list.md:22, a flag heading) and defined for
  PyRateDES.py (pyrate-des/references/tutorial-5.md:69, `* `-wd` is the path to the
  generated inpute file(s).`), and no page of the continuous skill names it anywhere, so a
  PyRateContinuous.py line carrying `-wd` stays HARD -- asserted both ways in --self-test.

WHAT COUNTS AS A COMMAND LINE
  A run of tokens that starts at one of the six documented programs --
  PyRate.py, PyRateContinuous.py, PyRateMCDD.py, PyRateDES.py, PyRateMBD.py,
  PyRateDES2.py -- and carries at least one flag. Such a run is taken from
    * fenced code blocks (``` ... ```), where a line ending in `\` continues on the
      next line, and
    * inline backtick spans of prose, which is how the mirrors quote a command inside
      a sentence.
  A bare mention (`PyRateDES2.py` in a table cell, with no flag after it) is counted
  as a mention, not a command line, and contributes no flags. Prose that is not inside
  backticks is never parsed as a command, so a sentence that lists option names with
  commas is not mistaken for a run line.
  The two roles of a backtick span are harvested apart and never borrow each other's
  authority: a span becomes a COMMAND line only when it names a program (command_lines),
  while a span that is nothing but a flag name (`-n`) becomes DOCUMENTATION of that flag
  for the program whose page says it (program_docs, kind "prose") -- it is never run, and a
  command line is never excused by a sentence that merely lists options.
  Arguments are read up to the first shell operator (`|`, `&&`, `;`, `>` ...) or the
  first `#` comment, so a flag belonging to `tee`, or a trailing mirror citation, is
  not charged to PyRate.

WHAT IS FLAGGED
  HARD - UNKNOWN-FLAG: a flag on a documented PyRate.py line that `--list` does not
  report, i.e. the builder refuses a command the documentation tells the user to type.
  HARD - UNDOCUMENTED-FLAG: a flag on a documented line of another program that no
  mirror documents for that program (coined, or borrowed from a sibling program).
  HARD - no command line found at all, an empty accepted set, or a builder that will not
  answer: a scan that verified nothing must never be able to print PASS.
  COUNTED AND PRINTED, NOT HARD - out-of-builder-scope flags that the program's own
  documentation does show.

This gate holds no exemption table and no flag list of its own: the accepted set is
whatever the builder prints today, and the out-of-scope set is whatever the mirrors
document today, so it gets stricter, never looser, as the tooling and the documentation
are completed. An exemption here would hide exactly the defect it is meant to find.

Usage: python3 scripts/audit_command_lines.py [--verbose]
       python3 scripts/audit_command_lines.py --self-test
Exit 0 = every documented flag is either accepted by the builder (PyRate.py lines) or
documented for its own program in a mirror (the other five), with both numbers printed.
"""

import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILDER = os.path.join(ROOT, "pyrate-command-reference", "scripts", "build_command.py")
VERBOSE = "--verbose" in sys.argv
TIMEOUT = 300

# The six programs the corpus documents (Home.md's program table). A command line for
# anything else is not one of the tools this suite describes.
PROGRAMS = ("PyRate.py", "PyRateContinuous.py", "PyRateMCDD.py",
            "PyRateDES.py", "PyRateMBD.py", "PyRateDES2.py")
# The one program build_command.py --list actually describes. Everything else is out of
# its scope, and this gate must not charge a foreign grammar to a documented line.
BUILDER_PROGRAM = "PyRate.py"
OTHER_PROGRAMS = tuple(p for p in PROGRAMS if p != BUILDER_PROGRAM)
PROGRAM_RE = re.compile(r"^(?:\./)?(%s)$" % "|".join(re.escape(p) for p in PROGRAMS))

# A flag token: one or two hyphens, a letter, then word characters (the corpus spells
# them -mG, -A, -qtimes, -data_in_area, -constrDivdD_0). A negative number (-0.5) is a
# value, not a flag, and is deliberately not matched.
FLAG_RE = re.compile(r"^-{1,2}[A-Za-z][A-Za-z0-9_]*$")
# The command-line matcher is deliberately wider than the one that reads documentation.
# A run line can only ever contain a real option or an invented one, so anything shaped like
# a long option with internal hyphens (--no-taxa) must be put to the builder rather than
# skipped: the narrower rule quietly ignored such tokens, and an invented flag written that
# way was never checked at all. The documentation matchers keep the narrow form, because the
# mirrors are full of hyphenated tokens that are not options -- 176 occurrences of the anchor
# fragment -command-list alone -- and reading those as flags would manufacture evidence in
# both directions. No corpus command line spells an option with a hyphen (measured: 0), so
# this widens what can be refused and not what is excused.
CMD_FLAG_RE = re.compile(r"^-{1,2}[A-Za-z][A-Za-z0-9_-]*$")
TOKEN_RE = re.compile(r'"[^"\n]*"|\'[^\']*\'|[^ \t\n]+')
# a shell operator ends the PyRate part of the line
SHELL_BREAK = {"|", "||", "&&", ";", ";;", "&", ">", ">>", "<", "<<", "2>&1", ">&",
               "(", ")"}
FENCE_RE = re.compile(r"^\s*(?:```+|~~~+)")
SPAN_RE = re.compile(r"`([^`\n]+)`")
# "  -pL           arity=2      kind=float   references/command-list.md:166"
LIST_LINE_RE = re.compile(r"^\s+(-{1,2}[A-Za-z][A-Za-z0-9_]*)\s+arity=(\d+)")
# how the mirrors DEFINE a command: a heading whose whole title is the flag, or a bullet
# that opens with it -- the shape every command page and tutorial uses
DEF_HEAD_RE = re.compile(r"^\s{0,3}#{2,6}\s*`?(-{1,2}[A-Za-z][A-Za-z0-9_]*)`?\s*$")
DEF_BULLET_RE = re.compile(r"^\s*[*+-]\s+`(-{1,2}[A-Za-z][A-Za-z0-9_]*)`")
# how close a program's name has to sit to a definition -- or to a prose mention, which
# uses the same window on purpose -- for that evidence to be the program's own
DEF_WINDOW = 8


def prose_flag(span):
    """The flag an inline span NAMES, else None: only when the whole span is one flag.

    This is the third way the mirrors talk about a command, alongside a run line ("usage")
    and a heading or bullet ("definition"): a sentence whose inline code is just the option,
    as at pyrate-continuous-covariates/references/tutorial-2.md:110, "the number of MCMC
    iterations and sampling frequencies can be set using the flags `-n` and `-s`,
    respectively". A span with anything else in it (`-wd path_to_target_directory`) is an
    example line, already the business of command_of(), not a name.
    """
    t = span.strip()
    return t if FLAG_RE.match(t) else None


def tokenize(text):
    """Split a command into tokens, keeping quoted runs together."""
    return [t for t in TOKEN_RE.findall(text.replace("\\\n", " ")) if t]


def command_of(tokens):
    """(program, args, ok) for a token run; ok is False if it runs no PyRate program.

    The run starts at the first program token and ends at the first shell operator or
    comment; anything before the program (a `python` interpreter, a `$` prompt, a path)
    is skipped, and anything after the terminator is another program's business.
    """
    prog_at = None
    for i, tok in enumerate(tokens):
        if PROGRAM_RE.match(tok):
            prog_at = i
            break
    if prog_at is None:
        return None, [], False
    args = []
    for tok in tokens[prog_at + 1:]:
        if tok in SHELL_BREAK or tok.startswith("#"):
            break
        args.append(tok)
    return tokens[prog_at].split("/")[-1], args, True


def flags_of(args):
    """The flag tokens of an argument list, each with its index in the run."""
    return [(i, t) for i, t in enumerate(args) if CMD_FLAG_RE.match(t)]


def parse_listing(text):
    """{flag: arity} from the builder's own --list output; other lines are ignored."""
    accepted = {}
    for line in text.split("\n"):
        m = LIST_LINE_RE.match(line)
        if m:
            accepted[m.group(1)] = int(m.group(2))
    return accepted


def _builder_run(args, cwd=None):
    """Run the builder with these arguments. Never raises: (rc, out, err) or (None, why)."""
    try:
        r = subprocess.run([sys.executable, "-B", BUILDER] + args,
                           cwd=cwd or _REAL_ROOT, capture_output=True, text=True,
                           timeout=TIMEOUT, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return None, "did not finish within %ds" % TIMEOUT
    except OSError as e:
        return None, "could not be executed (%s)" % e
    return r.returncode, r.stdout + r.stderr


def builder_accepted():
    """Ask the builder what it accepts. Raises RuntimeError if it will not say."""
    who = os.path.relpath(BUILDER, _REAL_ROOT)
    if not os.path.isfile(BUILDER):
        raise RuntimeError("command builder not found at %s" % who)
    rc, out = _builder_run(["--list"])
    if rc is None:
        raise RuntimeError("%s --list %s" % (who, out))
    if rc != 0:
        raise RuntimeError("%s --list exited %d :: %s"
                           % (who, rc, out.strip()[-300:] or "no output"))
    accepted = parse_listing(out)
    if not accepted:
        raise RuntimeError("%s --list printed no flag line, so nothing can be verified"
                           % who)
    return accepted


def builder_scope():
    """Measure what grammar the builder owns, instead of trusting a claim in this file.

    Five questions, each answered by running the builder:
      lists_pyrate_only        -- what the --list banner says it parsed;
      program_option           -- does `--program PyRate.py` work at all;
      foreign_emitted          -- does `--program PyRateContinuous.py` emit a line, or
                                  refuse it (the two shapes the limitation takes);
      grammar_follows_program  -- does it then ACCEPT a flag only the Continuous page
                                  documents (`-m`, `-c`)? That is the only case in which
                                  --list could ever judge a Continuous line;
      help_names_program       -- does `--help` tell a reader the option exists, since a
                                  limit nobody can find in the usage text is a limit
                                  readers will trip over.
    Every field is a bool or a captured line; `probe_errors` collects the runs that did
    not answer at all (a missing builder is fatal anyway, in builder_accepted()). If the
    builder ever grows a real per-program grammar, `grammar_follows_program` says so here
    and scope_lines() prints the NOTE that retires this gate's fallback -- a measured
    statement can be wrong in public, which is the only way it can also be corrected.
    """
    who = os.path.relpath(BUILDER, _REAL_ROOT)
    foreign = BUILDER_PROGRAM.replace(".py", "Continuous.py")
    facts = {"builder": who, "foreign_program": foreign, "probe_errors": []}

    def ask(args):
        rc, out = _builder_run(args)
        if rc is None:
            facts["probe_errors"].append("%s :: %s" % (" ".join(args), out))
            return None, ""
        return rc, out or ""

    def firstline(text, n=140):
        return (text.strip().split("\n") or ["(no output)"])[0][:n]

    rc, out = ask(["--list"])
    banner = next((l for l in out.split("\n") if l.strip().startswith("Commands")),
                  "(no banner line)") if rc is not None else "(builder did not answer)"
    facts["list_banner"] = banner.strip()
    facts["lists_pyrate_only"] = "command-list.md" in banner and \
        not any(p.replace(".py", "") in banner for p in OTHER_PROGRAMS)
    rc_sup, _o = ask(["--program", BUILDER_PROGRAM, "-d", "x.txt"])
    facts["program_option"] = rc_sup == 0
    rc_f, out_f = ask(["--program", foreign, "-d", "x.txt"])
    facts["foreign_emitted"] = rc_f == 0 and foreign in out_f
    facts["foreign_refused"] = rc_f not in (0, None)
    facts["foreign_message"] = firstline(out_f)
    rc_g, out_g = ask(["--program", foreign, "-d", "x.txt", "-m", "1", "-c", "temp.txt"])
    facts["grammar_follows_program"] = rc_g == 0
    facts["grammar_probe"] = (rc_g, firstline(out_g))
    rc_h, out_h = ask(["--help"])
    facts["help_names_program"] = ("--program" in out_h) if rc_h is not None else False
    facts["help_probe"] = rc_h
    return facts


def scope_lines(scope):
    """The builder-scope block as text: printed by report(), asserted by --self-test.

    Kept apart from report() so the self test can render a scope it did not measure -- for
    instance one in which the builder has grown a per-program grammar -- and check that the
    block says so, instead of trusting what the builder happens to do on this machine.
    """
    out = ["== builder scope (measured, not assumed) ==",
           "  builder                       : %s" % scope["builder"],
           "  --list banner                 : %s" % scope["list_banner"],
           "  --list describes %s only : %s"
           % (BUILDER_PROGRAM, "yes" if scope["lists_pyrate_only"] else "NO"),
           "  --program %s works       : %s"
           % (BUILDER_PROGRAM, "yes" if scope["program_option"] else "NO")]
    if scope.get("foreign_emitted"):
        out.append("  --program %s  : EMITS the line, grammar still %s's  (%s)"
                   % (scope["foreign_program"], BUILDER_PROGRAM, scope["foreign_message"]))
    elif scope.get("foreign_refused"):
        out.append("  --program %s  : REFUSED -- this tool owns no grammar for it  (%s)"
                   % (scope["foreign_program"], scope["foreign_message"]))
    else:
        out.append("  --program %s  : the probe did not answer (%s)"
                   % (scope["foreign_program"], scope.get("probe_errors")))
    out.append("  --program changes the grammar : %s%s"
               % ("YES" if scope["grammar_follows_program"] else "no",
                  "" if scope["grammar_follows_program"]
                  else "  <- refused (exit %s): %s" % scope["grammar_probe"]))
    out.append("  --help mentions --program     : %s"
               % ("yes" if scope["help_names_program"]
                  else "no -- a reader cannot find the option, or its limit, in the usage "
                       "text"))
    if scope["grammar_follows_program"]:
        out.append("  NOTE: the builder now carries a per-program grammar for %s, so this "
                   "gate's out-of-scope count under-claims: retire the fallback and judge "
                   "that program against the builder." % scope["foreign_program"])
    out.append("  => this gate judges %s against the builder and %s against their own "
               "documentation, counted out of builder scope"
               % (BUILDER_PROGRAM, ", ".join(OTHER_PROGRAMS)))
    return out



def mirror_files(root=None):
    """The mirrors: the only text this gate accepts as documentation of a command."""
    return sorted(glob.glob(os.path.join(root or ROOT, "*", "references", "*.md")))


def read(path):
    try:
        return open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return None


def named_programs(text, stems=True):
    """Which of the six programs a blob of text names (`.py` spelling optional)."""
    out = set()
    for p in PROGRAMS:
        pat = [re.escape(p)]
        if stems and p != BUILDER_PROGRAM:
            pat.append(re.escape(p[:-3]))
        if re.search(r"\b(?:%s)\b" % "|".join(pat), text):
            out.add(p)
    return out


def page_programs(lines, fm_progs, no):
    """Which programs OWN the evidence on line `no`: named within DEF_WINDOW of it, or by
    the page's frontmatter. ONE code path for every kind of documentation evidence -- a run
    line, a definition and a prose mention are scoped identically, so harvesting a third
    kind cannot quietly widen whose flag set a piece of text feeds. Note what this is NOT:
    it is not "the suite mentions this flag somewhere". A flag named only on another
    program's pages reaches no set but that program's."""
    near = "\n".join(lines[max(0, no - 1 - DEF_WINDOW):no + DEF_WINDOW])
    return named_programs(near) | fm_progs


def frontmatter_programs(lines):
    """The programs a mirror page belongs to, from its `---` frontmatter block."""
    fm_end = 0
    if lines and lines[0].strip() == "---":
        for j in range(1, len(lines)):
            if lines[j].strip() == "---":
                fm_end = j
                break
    return named_programs("\n".join(lines[:fm_end])) if fm_end else set()


def program_docs(mirrors):
    """{program: {flag: (mirror, lineno, how)}} -- each program's documented command set.

    Harvested from the mirrors only, in the three ways the corpus documents a command for a
    program -- "usage", "definition", "prose" (see HOW A FLAG IS JUDGED OUT OF SCOPE in the
    module docstring). Evidence keeps its file and line so every out-of-scope count printed
    by the report can be followed back into the documentation it came from, and so a reader
    can see WHICH kind of documentation excused a flag.
    """
    docs = dict((p, {}) for p in PROGRAMS)

    def add(prog, flag, where):
        docs[prog].setdefault(flag, where)

    for path in mirrors:
        text = read(path)
        if text is None:
            continue
        who = rel(path)
        # "usage": the mirror shows the program being run with this flag
        for lineno, _kind, run in command_lines(text):
            prog, args, ok = command_of(tokenize(run))
            if not ok:
                continue
            for _i, tok in flags_of(args):
                add(prog, tok, (who, lineno, "usage"))
        lines = text.split("\n")
        fm_progs = frontmatter_programs(lines)
        # "definition": a flag heading or bullet near the program's name, or on a page
        # whose frontmatter says the page belongs to that program
        for no, line in enumerate(lines, 1):
            m = DEF_HEAD_RE.match(line) or DEF_BULLET_RE.match(line)
            if not m:
                continue
            flag = m.group(1)
            for prog in page_programs(lines, fm_progs, no):
                add(prog, flag, (who, no, "definition"))
        # "prose": an inline span that is nothing but a flag name, in a sentence a program's
        # own page says. A line that already DEFINES the flag is left to the loop above, so
        # the stronger kind of evidence is what the report cites.
        in_fence = False
        for no, line in enumerate(lines, 1):
            if FENCE_RE.match(line):          # inside a fence it is code, not prose
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for span in SPAN_RE.findall(line):
                flag = prose_flag(span)
                if not flag:
                    continue
                for prog in page_programs(lines, fm_progs, no):
                    add(prog, flag, (who, no, "prose"))
    return docs


def md_files(root=None):
    """Every mirror and every SKILL.md, sorted: the two plans the suite ships text in."""
    root = root or ROOT
    return sorted(glob.glob(os.path.join(root, "*", "references", "*.md"))
                  + glob.glob(os.path.join(root, "*", "SKILL.md")))


def command_lines(text):
    """[(lineno, kind, run-text)] for the fenced and inline command candidates in a file.

    `kind` is "fence" for a logical line of a code block (backslash continuations
    already joined, numbered at the line the command starts on) and "span" for one
    inline backtick span. A stretch of prose with no backticks yields nothing at all,
    which is what keeps option lists out of the check.
    """
    out = []
    in_fence = False
    pending, pending_no = "", 0
    for no, raw in enumerate(text.split("\n"), 1):
        if FENCE_RE.match(raw):
            if pending:
                out.append((pending_no, "fence", pending))
            pending, pending_no = "", 0
            in_fence = not in_fence
            continue
        if in_fence:
            if pending == "":
                pending_no = no
            if raw.rstrip().endswith("\\"):
                pending = (pending + " " + raw.rstrip()[:-1]).strip()
                continue
            out.append((pending_no, "fence", (pending + " " + raw).strip()))
            pending, pending_no = "", 0
            continue
        if pending:                              # unbalanced fence: flush what we have
            out.append((pending_no, "fence", pending))
            pending, pending_no = "", 0
        for m in SPAN_RE.finditer(raw):
            out.append((no, "span", m.group(1).strip()))
    if pending:
        out.append((pending_no, "fence", pending))
    return out


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def scan(files, accepted, docs):
    """Check every documented command line: builder grammar for PyRate.py, program
    documentation for the five programs the builder does not describe."""
    stats = {"files": 0, "runs": 0, "lines": 0, "mentions": 0,
             "programs": dict((p, 0) for p in PROGRAMS),
             "in_scope": 0, "in_scope_accepted": 0,
             "oob": 0, "oob_documented": 0, "oob_undocumented": 0,
             "oob_also_in_builder": 0, "oob_programs": dict((p, 0) for p in PROGRAMS),
             "oob_flags": dict((p, {}) for p in PROGRAMS)}
    defects, notes = [], []
    for path in files:
        text = read(path)
        if text is None:
            defects.append(("UNREADABLE", rel(path), 0, "-", "cannot be read"))
            continue
        stats["files"] += 1
        for lineno, kind, run in command_lines(text):
            prog, args, ok = command_of(tokenize(run))
            if not ok:
                continue
            stats["runs"] += 1
            stats["programs"][prog] += 1
            fl = flags_of(args)
            if not fl:
                stats["mentions"] += 1
                if kind == "fence":
                    # a fenced run with input files and no option at all is legal, but
                    # it is also what a truncated copy-paste looks like
                    notes.append((rel(path), lineno, run[:70]))
                continue
            stats["lines"] += 1
            for _i, tok in fl:
                if prog == BUILDER_PROGRAM:
                    stats["in_scope"] += 1
                    if tok in accepted:
                        stats["in_scope_accepted"] += 1
                        continue
                    defects.append(
                        ("UNKNOWN-FLAG", rel(path), lineno, "%s %s" % (prog, tok),
                         "%s is not in the accepted set the builder reports for %s, so it "
                         "refuses this documented command line" % (tok, BUILDER_PROGRAM)))
                    continue
                # a program the builder does not describe: judge it against its own
                # documentation, count it out of scope, and never fold it into the
                # builder's numbers
                stats["oob"] += 1
                stats["oob_programs"][prog] += 1
                if tok in accepted:
                    stats["oob_also_in_builder"] += 1
                ev = docs.get(prog, {}).get(tok)
                if ev:
                    stats["oob_documented"] += 1
                    stats["oob_flags"][prog].setdefault(tok, ev)
                    continue
                stats["oob_undocumented"] += 1
                defects.append(
                    ("UNDOCUMENTED-FLAG", rel(path), lineno, "%s %s" % (prog, tok),
                     "%s is not documented for %s anywhere in the mirrors (its own "
                     "documentation, and the %d flag(s) the mirrors do document for it, "
                     "say otherwise), and build_command.py has no grammar for %s either"
                     % (tok, prog, len(docs.get(prog, {})), prog)))
    return stats, defects, notes


def report(stats, defects, notes, n_accepted, scope, docs):
    for line in scope_lines(scope):
        print(line)
    print("\n== counts ==")
    print("accepted flags (build_command.py --list) : %d" % n_accepted)
    print("files scanned (mirrors + SKILL.md)       : %d" % stats["files"])
    print("program runs found                       : %d" % stats["runs"])
    for p in PROGRAMS:
        print("   %-22s %4d   %s" % (p, stats["programs"][p],
                                     "in builder scope" if p == BUILDER_PROGRAM
                                     else "out of builder scope"))
    print("documented command lines (>=1 flag)      : %d" % stats["lines"])
    print("flag tokens checked                      : %d"
          % (stats["in_scope"] + stats["oob"]))
    print("  in builder scope (%s)          : %d" % (BUILDER_PROGRAM, stats["in_scope"]))
    print("     accepted by the builder             : %d" % stats["in_scope_accepted"])
    print("     refused by the builder (HARD)       : %d"
          % len([d for d in defects if d[0] == "UNKNOWN-FLAG"]))
    print("  OUT OF BUILDER SCOPE                   : %d" % stats["oob"])
    print("     documented for its own program      : %d   (NOT verified against any "
          "grammar -- the builder cannot assemble these lines today)"
          % stats["oob_documented"])
    print("     documented nowhere (HARD)           : %d" % stats["oob_undocumented"])
    print("     of the above, also in the PyRate.py : %d" % stats["oob_also_in_builder"])
    print("                                         set (coincidence of spelling, "
          "proves nothing)")
    print("runs naming no flag at all               : %d" % stats["mentions"])
    print("fallback evidence, mirrors only (flags documented per program):")
    for p in OTHER_PROGRAMS:
        print("   %-22s %3d" % (p, len(docs.get(p, {}))))
    for p in OTHER_PROGRAMS:
        flags = stats["oob_flags"][p]
        if not flags:
            continue
        print("\n  out of builder scope for %s: %d flag token(s), %d distinct"
              % (p, stats["oob_programs"][p], len(flags)))
        for tok in sorted(flags):
            who, lineno, how = flags[tok]
            print("     %-22s %s:%d (%s)" % (tok, who, lineno, how))
    distinct = sorted({d[3].split(" ", 1)[1] for d in defects if d[0] == "UNKNOWN-FLAG"})
    if distinct:
        print("\nrefused on %s lines (%d distinct): %s"
              % (BUILDER_PROGRAM, len(distinct), ", ".join(distinct)))
    for kind, who, lineno, ctx, why in defects:
        print("  %-19s %s:%d  %s\n                      %s" % (kind, who, lineno, ctx, why))
    if VERBOSE and notes:
        print("\nfenced runs carrying no flag (input file only):")
        for who, lineno, run in notes:
            print("  %s:%d  %s" % (who, lineno, run))


def main():
    try:
        accepted = builder_accepted()
    except RuntimeError as e:
        print("RESULT: FAIL (1) -- %s" % e)
        return 1
    scope = builder_scope()
    files = md_files()
    if not files:
        print("RESULT: FAIL (1) -- no mirror or SKILL.md found under %s, so the gate "
              "verified nothing" % ROOT)
        return 1
    docs = program_docs(mirror_files())
    if not any(docs[p] for p in OTHER_PROGRAMS):
        print("RESULT: FAIL (1) -- the mirrors document no command at all for any of the "
              "five programs outside the builder's scope, so their flags could not be "
              "judged; an empty documentation set must not be read as a free pass")
        return 1
    stats, defects, notes = scan(files, accepted, docs)
    if stats["runs"] == 0 or (stats["in_scope"] + stats["oob"]) == 0:
        print("RESULT: FAIL (1) -- %d files were read and not one PyRate flag was found "
              "on them; the scanner, not the corpus, is broken" % len(files))
        return 1
    report(stats, defects, notes, len(accepted), scope, docs)
    if stats["lines"] == 0:
        print("\nRESULT: FAIL (1) -- %d flag tokens were checked but no command line was "
              "identified; that is not a pass" % (stats["in_scope"] + stats["oob"]))
        return 1
    hard = len(defects)
    oob = stats["oob"]
    print("\nRESULT: " + ("PASS (%d flag(s) verified against the builder, %d judged out of "
                          "its scope against their own documentation -- see the counts above)"
                          % (stats["in_scope_accepted"], oob)
                          if not hard else
                          "FAIL (%d) -- %d refused on %s lines, %d undocumented on lines of "
                          "programs outside the builder's scope; %d further flag(s) are out "
                          "of scope but documented"
                          % (hard, len([d for d in defects if d[0] == "UNKNOWN-FLAG"]),
                             BUILDER_PROGRAM,
                             len([d for d in defects if d[0] == "UNDOCUMENTED-FLAG"]), oob)))
    return 0 if not hard else 1


# ------------------------------------------------------------------ self test
def _scan_pairs(pairs, accepted, root=None):
    """scan() over in-memory (rel-path, text) pairs, written to a temporary directory.

    Paths may name subdirectories (`skill-x/references/mirror.md`) because the mirrors and
    the SKILL.md files are different kinds of text to this gate: only a mirror is allowed
    to document a command, and only a SKILL.md is allowed to be wrong about one.
    """
    tmp = tempfile.mkdtemp(prefix="cmdlines-selftest-")
    try:
        paths = []
        for name, text in pairs:
            p = os.path.join(tmp, name)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(text)
            paths.append(p)
        global ROOT
        ROOT = tmp                          # rel() follows the scan root
        mirrors = mirror_files(tmp)
        return scan(paths, accepted, program_docs(mirrors))
    finally:
        ROOT = _REAL_ROOT


def self_test():
    """Prove the scanner answers the question it claims to answer.

    Every check here is a pair: an input that must pass and the smallest mutation of it
    that must fail. A gate that only ever sees good input cannot be trusted to recognise
    bad input, and this one prints PASS when it finds nothing -- so the negative cases
    below, and the live counts at the end, are what make the PASS mean something. The
    per-program cases are the ones that matter most: they are what stops a foreign flag
    being waved through because some other program documents it.
    """
    checks = [0]

    def ok(cond, msg):
        checks[0] += 1
        if not cond:
            print("SELF-TEST FAIL: %s" % msg)
            return False
        return True

    good = True
    # --list parsing: the exact shape the builder prints
    listing = ("Commands parsed from /x/command-list.md (4 core):\n"
               "  -d            arity=1      kind=path   references/command-list.md:17\n"
               "  -mG           arity=0      kind=flag   references/command-list.md:95\n"
               "  -pL           arity=2      kind=float  references/command-list.md:166\n"
               "  -thread       arity=2      kind=int    references/command-list.md:75\n"
               "  -not-a-flag line at a different indent   9\n"
               "no flags here\n")
    acc = parse_listing(listing)
    good &= ok(acc == {"-d": 1, "-mG": 0, "-pL": 2, "-thread": 2},
               "--list lines are read for name and arity, got %s" % acc)
    good &= ok(parse_listing("nothing at all") == {},
               "a listing with no flag line parses empty (main() turns that into a FAIL)")
    good &= ok("-not-a-flag" not in acc, "an indented sentence is not a flag")
    # tokenising and locating the command inside a line
    good &= ok(command_of(["python", "PyRate.py", "Canis_PyRate.py", "-A", "2"]) ==
               ("PyRate.py", ["Canis_PyRate.py", "-A", "2"], True), "python prefix skipped")
    good &= ok(command_of(["./PyRateMBD.py", "-d", "x.txt", "-m", "1"])[0] == "PyRateMBD.py",
               "./ prefix and the MBD program are recognised")
    good &= ok(command_of(["echo", "hello", "world"]) == (None, [], False),
               "a line that does not run a documented program is not a command line")
    good &= ok(command_of(["python", "PyRateOTHER.py", "-zz", "1"]) == (None, [], False),
               "an unknown program name is not silently treated as one of the six")
    good &= ok(command_of(["python", "PyRate.py", "-n", "1", "|", "grep", "-c", "x", "f"]) ==
               ("PyRate.py", ["-n", "1"], True),
               "the pipe ends the PyRate part, so grep's -c is not charged to PyRate")
    good &= ok(command_of(["python", "PyRate.py", "-n", "1", "#", "see", "-zz", "2"]) ==
               ("PyRate.py", ["-n", "1"], True),
               "a trailing comment is not a command, not even when it names a flag")
    good &= ok(flags_of(["-A", "4", "-0.5", "file.txt", "--mG", "-2x"]) ==
               [(0, "-A"), (4, "--mG")],
               "a negative number and a digit-first token are values, not flags")
    # the two ways a mirror carries a COMMAND (the third way it speaks of one -- naming it in
    # prose -- is case 5b below, kept apart on purpose: a name is not a run line)
    md = ("text `python PyRate.py x_PyRate.py -A 2 -mG` text\n"
          "```\n"
          "python PyRate.py x_PyRate.py \\\n"
          "    -n 1000 -s 100\n"
          "```\n"
          "a bare mention of `PyRateDES2.py` in prose\n"
          "1000, 2000, -zz, -notreal listed in plain prose with no backticks\n")
    runs = command_lines(md)
    cmds = [command_of(tokenize(r)) for _n, _k, r in runs]
    good &= ok([k for _n, k, _r in runs] == ["span", "fence", "span"],
               "one inline span, one joined fence line, one inline span, got %s"
               % [k for _n, k, _r in runs])
    good &= ok(sum(1 for p, a, o in cmds if o) == 3,
               "all three runs name a program, got %s" % cmds)
    joined = [a for p, a, o in cmds if o and "-n" in a]
    good &= ok(joined == [["x_PyRate.py", "-n", "1000", "-s", "100"]],
               "a backslash continuation is joined into one command, got %s" % joined)
    good &= ok([n for n, k, r in runs if k == "fence"] == [3],
               "the continued command is numbered at the line it starts on")
    good &= ok(all("-zz" not in r for _n, _k, r in runs),
               "an unquoted prose list of option names is never read as a command")
    # the per-program documentation harvest, on a fixture mirror of each shape
    fixture = [("skill-x/references/continuous.md",
                "---\ntitle: PyRateContinuous\nmirrored_from: PyRate-doc/x.md\n---\n"
                "##### `-c`\nA table of a variable and its times of change.\n"
                "##### `-m`\nHow the variable is correlated.\n"
                "`python PyRateContinuous.py x.txt -d x.txt -m 1 -c temp.txt`\n"
                "##### `-unused`\nDocumented, never run.\n"),
               ("skill-x/references/des.md",
                "---\ntitle: DES\nmirrored_from: PyRate-doc/y.md\n---\n"
                "Run PyRateDES.py with the two tables:\n"
                "* `-traitD` specifies the continuous trait influencing dispersal.\n"
                "`python ./PyRateDES.py -d in.txt -TdD -qtimes 2.58 5.33`\n")]
    tmp = tempfile.mkdtemp(prefix="cmdlines-docs-")
    try:
        for name, text in fixture:
            p = os.path.join(tmp, name)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w", encoding="utf-8").write(text)
        docs = program_docs(mirror_files(tmp))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    good &= ok(set(docs["PyRateContinuous.py"]) == {"-c", "-m", "-d", "-unused"},
               "the Continuous page yields its own flag set, by usage and by definition: %s"
               % sorted(docs["PyRateContinuous.py"]))
    good &= ok(set(docs["PyRateDES.py"]) == {"-traitD", "-d", "-TdD", "-qtimes"},
               "the DES page yields the DES flag set, not the Continuous one: %s"
               % sorted(docs["PyRateDES.py"]))
    good &= ok("-m" not in docs["PyRateDES.py"] and "-traitD" not in docs["PyRateContinuous.py"],
               "a flag documented for one program does not leak into another's set")
    good &= ok(docs["PyRateContinuous.py"]["-c"][1:] == (9, "usage")
               and docs["PyRateContinuous.py"]["-unused"][1:] == (10, "definition"),
               "a flag shown being run keeps the usage evidence, one only defined keeps "
               "the definition: %s" % docs["PyRateContinuous.py"])
    good &= ok({v[2] for v in docs["PyRateContinuous.py"].values()} ==
               {"usage", "definition"},
               "a line that both runs and defines a flag is recorded as the run, and usage "
               "and definition evidence are both harvested: %s"
               % docs["PyRateContinuous.py"])
    good &= ok(not docs["PyRateMBD.py"] and not docs["PyRateMCDD.py"],
               "a program no mirror documents gets an empty set, so nothing is excused "
               "for it: %s" % {p: len(v) for p, v in docs.items()})
    # NEGATIVE CASE 1: a documented PyRate.py command whose flag the builder refuses
    files_ok = [("fake-skill/references/one.md",
                 "`python PyRate.py in_PyRate.py -d in.txt -mG -pL 0.1 0.1`\n"),
                ("fake-skill/SKILL.md", "`python PyRateDES.py -d in.txt -notdocumented 1`\n")]
    stats, defects, _notes = _scan_pairs(files_ok, acc)
    good &= ok(stats["in_scope"] == 3 and stats["in_scope_accepted"] == 3,
               "the three %s flags verify against the builder, got %s"
               % (BUILDER_PROGRAM, stats))
    good &= ok(stats["oob"] == 2 and stats["oob_undocumented"] == 2,
               "a PyRateDES.py line is NOT judged by --list; both its flags are out of "
               "scope and neither is documented for DES: %s" % stats)
    good &= ok(len(defects) == 2 and all(d[0] == "UNDOCUMENTED-FLAG" for d in defects),
               "undocumented foreign-program flags are the two defects, got %s" % defects)
    good &= ok(not any(d[0] == "UNKNOWN-FLAG" for d in defects),
               "no builder-scope failure is invented for a program the builder does not "
               "describe: %s" % defects)
    # NEGATIVE CASE 2: shrinking the accepted set must break the PyRate.py content again,
    # and must NOT move the out-of-scope numbers at all
    stats2, defects2, _n2 = _scan_pairs(files_ok, {"-d": 1})
    good &= ok(stats2["in_scope"] == 3 and stats2["in_scope_accepted"] == 1 and
               len([d for d in defects2 if d[0] == "UNKNOWN-FLAG"]) == 2,
               "the same %s content fails when the builder accepts less (%d refused of %d "
               "in scope, %d verified) -- the verdict comes from --list, not from a list "
               "kept here" % (BUILDER_PROGRAM, len([d for d in defects2 if d[0] ==
                                                    "UNKNOWN-FLAG"]),
                              stats2["in_scope"], stats2["in_scope_accepted"]))
    good &= ok(stats2["oob"] == stats["oob"] and stats2["oob_undocumented"] == 2,
               "and the out-of-scope count does not move when the builder changes: %s"
               % stats2)
    # NEGATIVE CASE 3: the same foreign flag, once its program documents it, stops being
    # a defect -- and starts being counted out of builder scope instead of verified
    with_doc = files_ok + [("fake-skill/references/des.md",
                            "---\ntitle: DES\n---\n`./PyRateDES.py -d in.txt "
                            "-notdocumented 1`\n")]
    stats3, defects3, _n3 = _scan_pairs(with_doc, acc)
    # four out-of-scope tokens: the SKILL.md line and the mirror line that documents it,
    # each carrying -d and -notdocumented
    good &= ok(not defects3 and stats3["oob"] == 4 and stats3["oob_documented"] == 4,
               "a flag the DES mirrors document is out-of-scope-and-counted, never a "
               "silent accept: %s / %s" % (stats3, defects3))
    good &= ok(stats3["oob_also_in_builder"] == 2,
               "-d is in the PyRate.py set too and that is reported as the coincidence "
               "it is, not promoted to verified: %s" % stats3)
    # NEGATIVE CASE 4: a SKILL.md may not document its own commands
    skill_only = [("fake-skill/references/mbd.md",
                   "---\ntitle: MBD\n---\n`./PyRateMBD.py -d in.txt`\n"),
                  ("fake-skill/SKILL.md",
                   "`python PyRateMBD.py -d in.txt -qtimes 2.58 -madeup 1`\n")]
    stats4, defects4, _n4 = _scan_pairs(skill_only, acc)
    good &= ok(len(defects4) == 2 and
               all(d[0] == "UNDOCUMENTED-FLAG" for d in defects4),
               "a SKILL.md is the text under test, not the documentation that excuses it: "
               "%s" % defects4)
    # NEGATIVE CASE 5: a flag documented for the WRONG program still fails
    cross = [("fake-skill/references/continuous.md",
              "---\ntitle: PyRateContinuous\n---\n`python PyRateContinuous.py x.txt -m 1`\n"),
             ("fake-skill/SKILL.md", "`python PyRateContinuous.py x.txt -traitD a.txt`\n")]
    stats5, defects5, _n5 = _scan_pairs(cross, acc)
    good &= ok([d[3] for d in defects5] == ["PyRateContinuous.py -traitD"],
               "-traitD is a DES flag; on a Continuous line it is charged, not excused: %s"
               % defects5)
    good &= ok(stats5["oob"] == 2 and stats5["oob_documented"] == 1,
               "and the same line's -m is counted out of scope and documented: %s" % stats5)
    # CASE 5b: the third evidence source, and the boundary it must not cross. `-n` and `-s`
    # are named ONLY in prose on Continuous' own page -- the real shape is
    # pyrate-continuous-covariates/references/tutorial-2.md:110, "the number of MCMC
    # iterations and sampling frequencies can be set using the flags `-n` and `-s`,
    # respectively" -- so they document Continuous and no other program. `-wd` is named for
    # PyRate.py (the material at pyrate-bd-analysis/references/command-list.md:22) and defined
    # for PyRateDES.py (pyrate-des/references/tutorial-5.md:69, "* `-wd` is the path to the
    # generated inpute file(s)."), and never appears on a Continuous page: a Continuous line
    # carrying it stays HARD, though the suite as a whole documents it and though the very
    # SKILL.md under test says its name in a sentence.
    prose_case = [
        ("skill-p/references/tutorial-2.md",
         "---\ntitle: PyRate Tutorial \\#2\nmirrored_from: PyRate-doc/t2.md\n---\n"
         "`python PyRateContinuous.py -d x.txt -m 0`\n"
         "As in standard PyRate analyses the number of MCMC iterations and sampling "
         "frequencies can be set using the flags `-n` and `-s`, respectively.\n"
         "```\n"
         "`-fencedonly` is an option list pasted into a code block, not prose\n"
         "```\n"),
        ("skill-p/references/command-list.md",
         "---\ntitle: command list\n---\nPyRate.py is the main program.\n"
         "#####`-wd`\nDefine the working directory where output files are saved.\n"),
        ("skill-p/references/tutorial-5.md",
         "---\ntitle: DES tutorial\nmirrored_from: PyRate-doc/t5.md\n---\n"
         "Run PyRateDES.py on the two tables.\n"
         "* `-wd` is the path to the generated inpute file(s).\n"),
        ("skill-p/SKILL.md",
         "`python PyRateContinuous.py -d x.txt -m 0 -n 200000 -s 1000 -wd ./TI_1`\n"
         "the `-wd` above is an extrapolation, which is why this file documents nothing\n")]
    prose_docs = {}
    tmp = tempfile.mkdtemp(prefix="cmdlines-prose-")
    try:
        for name, text in prose_case:
            p = os.path.join(tmp, name)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w", encoding="utf-8").write(text)
        prose_docs = program_docs(mirror_files(tmp))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    good &= ok({f for f, v in prose_docs["PyRateContinuous.py"].items() if v[2] == "prose"}
               == {"-n", "-s"},
               "a flag a program's own page NAMES in inline code in prose is harvested, as "
               "prose evidence, for that program: %s" % prose_docs["PyRateContinuous.py"])
    good &= ok(prose_docs["PyRateContinuous.py"].get("-n", ("", -1, ""))[1:] == (6, "prose")
               and prose_docs["PyRateContinuous.py"].get("-d", ("", -1, ""))[1:] == (5, "usage"),
               "the prose evidence keeps its file and line, and a flag that is also run "
               "keeps the stronger usage evidence: %s" % prose_docs["PyRateContinuous.py"])
    good &= ok("-fencedonly" not in prose_docs["PyRateContinuous.py"],
               "a flag inside a fenced code block is code, not prose, and documents nothing: "
               "%s" % sorted(prose_docs["PyRateContinuous.py"]))
    good &= ok("-wd" in prose_docs["PyRate.py"] and "-wd" in prose_docs["PyRateDES.py"]
               and "-wd" not in prose_docs["PyRateContinuous.py"],
               "-wd is documented for the two programs whose pages name it and for no others: "
               "%s" % {p: ("-wd" in v) for p, v in prose_docs.items()})
    good &= ok("-n" not in prose_docs["PyRateDES.py"] and "-s" not in prose_docs["PyRateDES.py"],
               "Continuous' prose sentence does not feed DES' set: %s"
               % sorted(prose_docs["PyRateDES.py"]))
    good &= ok("-n" not in prose_docs["PyRate.py"],
               "nor does it feed the builder-scope program's set (which --list judges anyway)")
    # seven out-of-scope tokens on three Continuous lines: the mirror's own usage line (-d,
    # -m), the SKILL.md line (-d, -m, -n, -s, -wd); the -wd in its prose sentence is not a run
    stats8, defects8, _n8 = _scan_pairs(prose_case, acc)
    good &= ok([d[3] for d in defects8] == ["PyRateContinuous.py -wd"]
               and defects8[0][0] == "UNDOCUMENTED-FLAG",
               "the prose source excuses -n and -s and STILL charges -wd: %s" % defects8)
    good &= ok(stats8["oob"] == 7 and stats8["oob_documented"] == 6
               and stats8["oob_undocumented"] == 1,
               "and the arithmetic accounts for every one of the seven: %s" % stats8)
    stats9, defects9, _n9 = _scan_pairs(
        prose_case[:3] + [(prose_case[3][0], prose_case[3][1].replace(" -wd ./TI_1", ""))], acc)
    good &= ok(not defects9 and stats9["oob"] == 6 and stats9["oob_documented"] == 6,
               "the same line WITHOUT the foreign -wd is clean: the failure is the flag, not "
               "the fixture (%s / %s)" % (stats9, defects9))
    # NEGATIVE CASE 6: a run with no flag at all is a mention, never a verified flag
    stats6, defects6, notes6 = _scan_pairs(
        [("fake-skill/references/three.md",
          "```\npython PyRate.py in_PyRate.py\n```\n")], acc)
    good &= ok(stats6["lines"] == 0 and stats6["mentions"] == 1 and not defects6
               and len(notes6) == 1,
               "a flagless run is reported as a mention and noted, not verified: %s"
               % stats6)
    # NEGATIVE CASE 7: an empty scan is not a pass
    stats7, defects7, _n7 = _scan_pairs([("fake-skill/SKILL.md", "no commands here\n")], acc)
    good &= ok(stats7["runs"] == 0 and stats7["in_scope"] + stats7["oob"] == 0
               and not defects7,
               "a file with no command line yields zero runs, which main() refuses to "
               "call PASS")
    # The builder-scope block. Asserted as invariants of THIS file, never as a snapshot of
    # the builder's behaviour: build_command.py has another owner and changed under this
    # gate while it was being written (--program used to rename the emitted program and
    # keep the PyRate.py grammar; it now refuses a foreign program outright). A self test
    # that pinned either answer would go red on a truth, which is how self tests get
    # ignored. What must hold regardless is that the probes answered, that the block prints
    # the answer it measured, and that a builder which really did grow a per-program
    # grammar would say so instead of being quietly relied on.
    scope = builder_scope()
    good &= ok(not scope["probe_errors"],
               "every scope probe was answered; a silence would leave this gate guessing "
               "what it is allowed to judge: %s" % scope["probe_errors"])
    good &= ok(scope["lists_pyrate_only"],
               "the builder's --list banner claims one program only, which is why foreign "
               "lines need a fallback: %s" % scope["list_banner"])
    good &= ok(scope["program_option"] or not scope["foreign_emitted"],
               "if --program is not offered at all then no line is emitted under a foreign "
               "name either (program_option=%s, foreign_emitted=%s)"
               % (scope["program_option"], scope["foreign_emitted"]))
    rendered = "\n".join(scope_lines(scope))
    good &= ok(BUILDER_PROGRAM in rendered and all(p in rendered for p in OTHER_PROGRAMS),
               "the block names the one program the builder owns and every program it does "
               "not, so a reader knows which side of the line each count sits on")
    good &= ok(("REFUSED" in rendered) == bool(scope["foreign_refused"])
               and ("EMITS" in rendered) == bool(scope["foreign_emitted"]),
               "the block prints the builder's measured refusal/emission rather than a "
               "hardcoded sentence: %s" % rendered)
    good &= ok("--help mentions --program     : %s"
               % ("yes" if scope["help_names_program"] else "no") in rendered,
               "whether --help documents the option is reported from the builder, not "
               "asserted here as a permanent flaw")
    good &= ok("retire the fallback" in "\n".join(
                   scope_lines(dict(scope, grammar_follows_program=True))),
               "a builder that really does accept a foreign program's grammar makes this "
               "block announce that the out-of-scope count under-claims")
    good &= ok("did not answer" in "\n".join(
                   scope_lines(dict(scope, foreign_emitted=False, foreign_refused=False,
                                    probe_errors=["boom"]))),
               "an unanswered probe is printed as a silence, never read as a pass")
    # the gate must not be vacuous against the real suite
    real = md_files(_REAL_ROOT)
    good &= ok(len(real) > 40, "the real suite has mirrors to scan, got %d files" % len(real))
    live_acc = builder_accepted()
    good &= ok(len(live_acc) >= 50,
               "the builder reports a real flag set (%d), not an empty one" % len(live_acc))
    live_docs = program_docs(mirror_files(_REAL_ROOT))
    live_stats, live_bad, _live_notes = scan(real, live_acc, live_docs)
    good &= ok(live_stats["lines"] >= 50,
               "the suite really does document %d command lines, so the scan is not "
               "silently finding nothing" % live_stats["lines"])
    good &= ok(live_stats["in_scope_accepted"] > 0,
               "the live scan verifies %d flag uses against the builder, so PASS is "
               "reachable" % live_stats["in_scope_accepted"])
    good &= ok(live_stats["oob"] > 0 and live_stats["oob_documented"] > 0,
               "the live scan reaches the programs outside the builder's scope (%d flags, "
               "%d of them documented for their own program) instead of dropping them"
               % (live_stats["oob"], live_stats["oob_documented"]))
    good &= ok(live_stats["oob_documented"] + live_stats["oob_undocumented"]
               == live_stats["oob"],
               "every out-of-scope flag is accounted for as documented or undocumented: %s"
               % live_stats)
    good &= ok(live_stats["in_scope"] + live_stats["oob"] > 100 and
               live_stats["programs"][BUILDER_PROGRAM] > 0,
               "the live scan reaches the main program and %d flag tokens"
               % (live_stats["in_scope"] + live_stats["oob"]))
    good &= ok(len({live_stats["programs"][p] for p in PROGRAMS if live_stats["programs"][p]})
               >= 4, "at least four of the six programs appear on real command lines")
    good &= ok(all(live_stats["oob_programs"][p] == 0 or len(live_docs[p]) > 0
                   for p in OTHER_PROGRAMS),
               "every program the builder does not describe either has no flag to judge or "
               "has documentation to judge it against (sizes: %s)"
               % {p: len(live_docs[p]) for p in OTHER_PROGRAMS})
    # the prose source, judged against the REAL mirrors rather than a fixture: it must fire,
    # every citation it produces must be followable into the line that carries it, and the
    # one program pair that started this fix must sit on the right side of the boundary.
    live_prose = sorted({(p, f) for p in PROGRAMS
                         for f, v in live_docs[p].items() if v[2] == "prose"})
    good &= ok(len(live_prose) >= 5,
               "prose names options on the real mirrors too (%d program/flag pairs), so the "
               "source is not a fixture-only feature" % len(live_prose))
    misplaced = []
    for p, f in live_prose:
        who, lineno, _how = live_docs[p][f]
        cited = (read(os.path.join(_REAL_ROOT, who)) or "").split("\n")
        spans = [s.strip() for s in SPAN_RE.findall(cited[lineno - 1])] \
            if 1 <= lineno <= len(cited) else []
        if f not in spans:
            misplaced.append((p, f, who, lineno))
    good &= ok(not misplaced,
               "every prose citation points at a line of a mirror that carries an inline span "
               "which is exactly that flag, so the excuse can be checked by hand: %s"
               % misplaced[:4])
    good &= ok("-n" in live_docs["PyRateContinuous.py"]
               and "-s" in live_docs["PyRateContinuous.py"],
               "-n and -s are documented for PyRateContinuous.py, as "
               "pyrate-continuous-covariates/references/tutorial-2.md:110 and :151 say -- if "
               "this fails, either the mirrors changed or the prose source broke, and the "
               "gate is about to report the same 10 false HARD failures it used to: %s"
               % sorted(live_docs["PyRateContinuous.py"]))
    good &= ok("-wd" in live_docs[BUILDER_PROGRAM] and "-wd" in live_docs["PyRateDES.py"]
               and "-wd" not in live_docs["PyRateContinuous.py"],
               "on the real corpus as in the fixture, a flag documented only for other "
               "programs stays undocumented for Continuous: %s"
               % {p: ("-wd" in live_docs[p]) for p in PROGRAMS})
    kinds = {v[2] for p in PROGRAMS for v in live_docs[p].values()}
    good &= ok(kinds <= {"usage", "definition", "prose"},
               "every citation is labelled with one of the three documented kinds of "
               "evidence, never a fourth invented to wave a flag through: %s" % sorted(kinds))
    if live_bad:
        good &= ok(all(d[0] in ("UNKNOWN-FLAG", "UNDOCUMENTED-FLAG") for d in live_bad)
                   and live_stats["in_scope_accepted"] > len(live_bad),
                   "the live failures are refused or undocumented flags (%d) beside %d "
                   "verified uses, so the gate is failing on content and not on its own "
                   "plumbing" % (len(live_bad), live_stats["in_scope_accepted"]))
    if good:
        print("self-test: %d checks run" % checks[0])
        print("audit_command_lines.py self-test PASSED (%d checks, 0 failures)" % checks[0])
        return 0
    print("audit_command_lines.py self-test FAILED (%d checks run)" % checks[0])
    return 1


_REAL_ROOT = ROOT

if "--self-test" in sys.argv or "-t" in sys.argv:
    sys.exit(self_test())
elif "--help" in sys.argv or "-h" in sys.argv:
    print(__doc__)
    sys.exit(0)

if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        # the reader went away (`| head`); send the leftovers to the void and come back
        # as 141, the code a shell reports for a truncated pipe, so an interrupted run
        # is never mistaken for a completed one
        _devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(_devnull, sys.stdout.fileno())
        sys.exit(141)
