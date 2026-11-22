#!/usr/bin/env python3
"""Structural conformance gate for the PyRate skills suite.

Checks the mechanical rules a skill package has to satisfy, independently of the
content auditors (audit_citations.py, audit_corpus.py, audit_coverage.py):

  * SKILL.md exists and its YAML frontmatter is delimited by `---` at line 1
  * `name` is present, hyphen-case, and equal to the folder name
  * `description` is present, single-line, and <= 1024 characters (the skill format
    hard limit - a longer one is silently truncated, so the skill stops triggering)
  * SKILL.md body is < 500 lines
  * no unfinished-work marker survives in any .md or .py of the skill: the to-do
    keyword glued to a colon, which is what a reader must never find in a shipped file
  * no extraneous README/CHANGELOG/NOTES file inside a skill folder (assets/files/ is
    excluded: that directory legitimately carries a provenance README)
  * every backticked local path in a SKILL.md resolves
  * shared assets are addressed as `../assets/...` - the suite keeps images and
    fixtures at its root, so a bare `assets/...` only resolves from the suite root and
    breaks when read from inside the skill folder
  * no build junk anywhere under the suite root: no `__pycache__/` directory, no
    compiled bytecode (`*.pyc`, `*.pyo`), no editor/OS droppings (`.DS_Store`,
    `Thumbs.db`, `*.bak`, `*.tmp`, `*.swp`, `*.orig`, `*.rej`, trailing `~`). A bundle
    is read by an agent on someone else's machine; bytecode embeds the absolute path of
    the machine that authored it, and a stray temp file is a file the suite claims to
    ship but does not explain. This sweep walks the WHOLE root - the per-skill rules
    above only look inside folders that hold a SKILL.md, so junk at the suite root
    (`scripts/__pycache__/`) used to be invisible here.

Deliberately not flagged: glob patterns (`occ-*.txt`), paths inside fenced code blocks
(shell variables), and `../../assets/...` written as it appears *inside* a
references/ mirror (which sits one level deeper, so `../../` is correct there).
The only directory pruned from the junk sweep is `.git`; `__pycache__` is NOT pruned -
that is one of the things the sweep is looking for.

Usage: python3 scripts/audit_structure.py [--verbose]
       python3 scripts/audit_structure.py --self-test
       python3 scripts/audit_structure.py --help
Exit 0 = every skill folder satisfies every rule above.
"""

import glob
import os
import re
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True          # this gate fails on build junk; it must not make any
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERBOSE = '--verbose' in sys.argv
SELF_TEST = '--self-test' in sys.argv or '-t' in sys.argv
HELP = '--help' in sys.argv or '-h' in sys.argv
DESC_MAX = 1024
BODY_MAX = 500

# The unfinished-work needle, assembled rather than written: this file is scanned by the
# very sweep it implements, so spelling the token out here would report a defect that
# does not exist (and, worse, teach an author that the way to pass is to hide the token).
# Assembled the same way it is matched, so a marker can only pass by not being there.
MARKER = "TO" + "DO" + ":"

BACKTICK = re.compile(r'`((?:\.\./|references/|scripts/|assets/)[A-Za-z0-9._/*-]+[A-Za-z0-9.*_-])`')
EXTRANEOUS = re.compile(r'^(README|CHANGELOG|INSTALL(_GUIDE)?|NOTES|HOWTO)([.-].*)?$', re.I)

# Build junk. Names are matched exactly, suffixes at the end of a basename. The list is
# deliberately short and each entry answers a real risk: bytecode (`.pyc`, `.pyo`) and the
# `__pycache__` folders that hold it carry the authoring machine's absolute path inside
# them, editor droppings (`.bak`, `.swp`, `.orig`, `.rej`, `~`) and OS droppings
# (`.DS_Store`, `Thumbs.db`) are files nobody wrote for the reader, and `.tmp` is a file
# that was never finished. `.git` is the only directory pruned from the walk, and it is
# pruned because it is a VCS checkout, not because its contents are wanted in the bundle.
JUNK_DIRS = {'__pycache__'}
JUNK_NAMES = {'.DS_Store', 'Thumbs.db', '.AppleDouble'}
JUNK_SUFFIXES = ('.pyc', '.pyo', '.tmp', '.bak', '.swp', '.swo', '.orig', '.rej', '~')


# Assembled at runtime so audit_corpus.py check G cannot read this planted name as a
# figure the suite ships (see scripts/audit_sources.py:_FIG for the same convention).
_ART = 'figure.png' + '.tmp'


def junk_sweep(root):
    """[(kind, message)] for every piece of build junk under root, at any depth.

    Reported once per offending path. A `__pycache__` directory is reported as a whole and
    not descended into, so a folder of twenty bytecode files is one finding, not twenty-one:
    the fix is the same, and the count must not be inflated by it.
    """
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in sorted(dirnames) if d != '.git']
        for d in list(dirnames):
            if d in JUNK_DIRS:
                out.append(('BUILD-JUNK',
                            '%s (directory of compiled bytecode; delete it and run Python '
                            'with -B so it does not come back)'
                            % os.path.relpath(os.path.join(dirpath, d), root)))
                dirnames.remove(d)          # report the folder, not its contents
        for f in sorted(filenames):
            if f in JUNK_NAMES or f.endswith(JUNK_SUFFIXES):
                out.append(('BUILD-JUNK',
                            '%s (build junk; it must not ship in the bundle)'
                            % os.path.relpath(os.path.join(dirpath, f), root)))
    return out



def skills(root=ROOT):
    return sorted(os.path.basename(d.rstrip('/')) for d in glob.glob(os.path.join(root, '*'))
                  if os.path.exists(os.path.join(d, 'SKILL.md')))


def strip_fences(body):
    out, fence = [], False
    for line in body.split('\n'):
        if line.lstrip().startswith('```'):
            fence = not fence
            continue
        if not fence:
            out.append(line)
    return '\n'.join(out)


def marker_line_no(txt):
    """1-based number of the first line carrying the unfinished-work needle."""
    for i, line in enumerate(txt.split('\n'), 1):
        if MARKER in line:
            return i
    return 0


def audit(root):
    """[(skill, desc_len, body_lines, n_refs)] rows + [(skill, kind, msg)] defects.

    Includes the build-junk sweep of the whole tree, so `root` may be the suite or a
    fixture; the self test drives it against both.
    """
    fails = []
    rows = []
    # the whole-tree sweep runs first: it is the only check here that looks at the suite
    # root itself, and a bundle that ships bytecode is broken whatever the skills say
    for kind, msg in junk_sweep(root):
        fails.append((msg.split('/')[0], kind, msg))
    dirs = [os.path.basename(d.rstrip('/')) for d in glob.glob(os.path.join(root, '*'))
            if os.path.isdir(os.path.join(d, 'references')) or
            os.path.exists(os.path.join(d, 'SKILL.md'))]
    for sk in sorted(dirs):
        path = os.path.join(root, sk, 'SKILL.md')
        if not os.path.exists(path):
            fails.append((sk, 'FOLDER-WITHOUT-SKILL', sk + '/ has no SKILL.md'))
            continue
        raw = open(path, encoding='utf-8').read()
        if not raw.startswith('---\n'):
            fails.append((sk, 'FRONTMATTER', 'file does not open with --- on line 1'))
            continue
        end = raw.find('\n---\n', 3)
        if end < 0:
            fails.append((sk, 'FRONTMATTER', 'unterminated --- block'))
            continue
        fm, body = raw[3:end], raw[end + 5:]
        nm = re.search(r'^name:\s*(\S+)\s*$', fm, re.M)
        if not nm:
            fails.append((sk, 'FRONTMATTER', 'no name: field'))
        elif nm.group(1) != sk:
            fails.append((sk, 'NAME', 'name %r != folder %r' % (nm.group(1), sk)))
        elif not re.fullmatch(r'[a-z0-9-]+', nm.group(1)):
            fails.append((sk, 'NAME', '%r is not hyphen-case' % nm.group(1)))
        # the value runs to the next top-level key (or the end of the frontmatter), so a
        # description folded over several lines cannot hide behind a single-line regex
        dm = re.search(r'^description:[ \t]*(.*?)(?=^(?:[A-Za-z_][\w-]*:[ \t]?)|\Z)',
                       fm, re.M | re.S)
        dlen = 0
        if not dm or not dm.group(1).strip():
            fails.append((sk, 'DESCRIPTION', 'no description: field'))
        else:
            d = dm.group(1).strip()
            dlen = len(d)
            if '\n' in d:
                fails.append((sk, 'DESCRIPTION', 'must be a single line'))
            if dlen > DESC_MAX:
                fails.append((sk, 'DESCRIPTION',
                              '%d chars > %d (will be truncated)' % (dlen, DESC_MAX)))
        nlines = body.count('\n') + 1
        if nlines >= BODY_MAX:
            fails.append((sk, 'BODY', '%d lines >= %d' % (nlines, BODY_MAX)))
        refs = glob.glob(os.path.join(root, sk, 'references', '*.md'))
        if not refs:
            fails.append((sk, 'REFERENCES', 'no references/*.md mirror'))
        prose = strip_fences(body)
        for m in BACKTICK.finditer(prose):
            p = m.group(1)
            if '*' in p or '?' in p:
                continue
            cand = os.path.normpath(os.path.join(root, sk, p))
            if not os.path.exists(cand) and p.startswith('../../'):
                # quoted as it appears inside a references/ mirror, which sits one level
                # deeper - resolve it from there before calling it dead
                cand = os.path.normpath(os.path.join(root, sk, 'references', p))
            if not os.path.exists(cand):
                fails.append((sk, 'DEAD-PATH', '`%s` -> %s' % (p, os.path.relpath(cand, root))))
            if re.match(r'^assets/', p):
                fails.append((sk, 'ASSET-PREFIX',
                              '`%s` should be `../%s` (assets live at the suite root)' % (p, p)))
        for f in sorted(glob.glob(os.path.join(root, sk, '**', '*'), recursive=True)):
            if not os.path.isfile(f):
                continue
            b = os.path.basename(f)
            rel = os.path.relpath(f, os.path.join(root, sk))
            if EXTRANEOUS.match(b) and not rel.startswith('assets/files'):
                fails.append((sk, 'EXTRANEOUS', rel))
            if b.endswith(('.md', '.py', '.sh', '.R', '.r')):
                txt = open(f, encoding='utf-8', errors='replace').read()
                if MARKER in txt:
                    fails.append((sk, 'MARKER', '%s:%d' % (rel, marker_line_no(txt))))
        rows.append((sk, dlen, nlines, len(refs)))
    return rows, fails


def main():
    rows, fails = audit(ROOT)
    print('%-30s %5s %5s %5s' % ('skill', 'desc', 'body', 'refs'))
    for sk, dlen, nlines, nref in rows:
        print('%-30s %5d %5d %5d %s' % (sk, dlen, nlines, nref,
                                        'OK' if dlen <= DESC_MAX and nlines < BODY_MAX else '<--'))
    junk = [f for f in fails if f[1] == 'BUILD-JUNK']
    print('\n%d skills checked, %d build-junk finding(s), %d structural defect(s)'
          % (len(rows), len(junk), len(fails)))
    if fails or VERBOSE:
        for sk, kind, msg in fails:
            print('  %-14s %-20s %s' % (kind, sk, msg))
    print('\nRESULT: ' + ('PASS' if not fails else 'FAIL (%d)' % len(fails)))
    return 0 if not fails else 1


# ------------------------------------------------------------------ self test
DESC = "One line of what this demo skill does."
GOOD_SKILL = """---
name: demo-skill
description: %s
---
# Demo skill

Body says to see `references/demo-mirror.md` and to run `../assets/files/demo.txt`.
""" % DESC


def _write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(text)
    return path


def _fixture(mutate=None):
    """Build a conforming mini-suite in a temp dir; `mutate(root)` breaks one rule."""
    root = tempfile.mkdtemp(prefix='audit-structure-selftest-')
    try:
        _write(root, 'demo-skill/SKILL.md', GOOD_SKILL)
        _write(root, 'demo-skill/references/demo-mirror.md', '# mirror\n\nsome text\n')
        _write(root, 'assets/files/demo.txt', 'col1\tcol2\n')
        _write(root, 'assets/files/README.md', 'provenance of the fixture\n')
        if mutate:
            mutate(root)
        return root
    except BaseException:
        shutil.rmtree(root, ignore_errors=True)
        raise


def _kinds(fails):
    return sorted({k for _s, k, _m in fails})


def self_test():
    """Every rule in audit() gets a passing input and a deliberately broken one.

    The negative half is the point: a check that never fires on a known-bad skill is not
    protecting anything, and this file's own source must stay clean of the needle it
    hunts (it is scanned by check U of audit_corpus.py, and by nothing here).
    """
    checks = [0]

    def ok(cond, msg):
        checks[0] += 1
        if not cond:
            print('SELF-TEST FAIL: %s' % msg)
            return False
        return True

    good = True

    def with_mutant(fn):
        root = _fixture(fn)
        try:
            return audit(root)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def edit(rel, old, new):
        def apply(root):
            p = os.path.join(root, rel)
            txt = open(p, encoding='utf-8').read()
            assert old in txt, 'self-test fixture lost %r in %s' % (old, rel)
            open(p, 'w', encoding='utf-8').write(txt.replace(old, new, 1))
        return apply

    def add(rel, text='x\n'):
        return lambda root: _write(root, rel, text)

    def drop(rel):
        return lambda root: os.remove(os.path.join(root, rel))

    # the clean fixture is clean, and the gate really looked at it
    root = _fixture()
    try:
        rows, fails = audit(root)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    good &= ok(len(rows) == 1 and rows[0][0] == 'demo-skill',
               'the conforming skill is found and measured, got %s' % rows)
    good &= ok(rows[0][1] == len(DESC) and rows[0][3] == 1 and 0 < rows[0][2] <= 6,
               'description length, mirror count and body length are all measured: %s' % rows)
    good &= ok(fails == [], 'a conforming skill yields no defect, got %s' % fails)

    # NEGATIVE 1: the unfinished-work needle, in a mirror and in a helper .py
    def marker_in_mirror(r):
        _write(r, 'demo-skill/references/demo-mirror.md',
               '# mirror\n\n' + MARKER + ' write the Chinese twin\n')

    rows, fails = with_mutant(marker_in_mirror)
    good &= ok([f for f in fails if f[1] == 'MARKER'] ==
               [('demo-skill', 'MARKER', 'references/demo-mirror.md:3')],
               'a real marker in a mirror is flagged with its file and line, got %s' % fails)

    def marker_in_script(r):
        _write(r, 'demo-skill/scripts/helper.py',
               'x = 1\n' + MARKER + ' finish this\n')

    rows, fails = with_mutant(marker_in_script)
    good &= ok([f for f in fails if f[1] == 'MARKER'] ==
               [('demo-skill', 'MARKER', 'scripts/helper.py:2')],
               'the needle is hunted in .py files too, got %s' % fails)
    # the word alone, or the keyword without its colon, is not a marker
    rows, fails = with_mutant(add('demo-skill/notes-x.md', 'todo later\nTODOS are fine\n'))
    good &= ok('MARKER' not in _kinds(fails),
               'a bare "todo" is not the needle, got %s' % fails)
    good &= ok(MARKER not in open(os.path.abspath(__file__), encoding='utf-8').read(),
               'this file\'s own source carries no copy of the needle it enforces')
    good &= ok(len(MARKER) == 5 and MARKER[0] == 'T' and MARKER.endswith(':'),
               'the needle is still the five-character token, however it is assembled')

    # NEGATIVE 2 and onward: at least one deliberately broken input per remaining check
    def long_description(r):
        edit('demo-skill/SKILL.md', 'description: %s' % DESC,
             'description: ' + 'x' * (DESC_MAX + 5))(r)

    def wrapped_description(r):
        edit('demo-skill/SKILL.md', 'description: %s' % DESC,
             'description: %s\n  and a second line' % DESC)(r)

    def no_description(r):
        edit('demo-skill/SKILL.md', 'description: %s\n' % DESC, '')(r)

    def unterminated_fm(r):
        edit('demo-skill/SKILL.md', '---\n# Demo skill', '\n# Demo skill')(r)

    def long_body(r):
        _write(r, 'demo-skill/SKILL.md',
               GOOD_SKILL + '\n'.join('line %d' % i for i in range(BODY_MAX)))

    def underscore_folder(r):
        os.rename(os.path.join(r, 'demo-skill'), os.path.join(r, 'Demo_Skill'))
        p = os.path.join(r, 'Demo_Skill', 'SKILL.md')
        txt = open(p, encoding='utf-8').read()
        open(p, 'w', encoding='utf-8').write(txt.replace('name: demo-skill',
                                                         'name: Demo_Skill', 1))

    cases = [
        ('FOLDER-WITHOUT-SKILL', drop('demo-skill/SKILL.md')),
        ('FRONTMATTER', edit('demo-skill/SKILL.md', '---\nname', '# no fence\nname')),
        ('FRONTMATTER', unterminated_fm),
        ('DESCRIPTION', no_description),
        ('NAME', edit('demo-skill/SKILL.md', 'name: demo-skill', 'name: other-skill')),
        ('NAME', underscore_folder),
        ('DESCRIPTION', long_description),
        ('DESCRIPTION', wrapped_description),
        ('BODY', long_body),
        ('REFERENCES', drop('demo-skill/references/demo-mirror.md')),
        ('DEAD-PATH', edit('demo-skill/SKILL.md', 'demo-mirror.md', 'no-such-mirror.md')),
        ('ASSET-PREFIX', edit('demo-skill/SKILL.md', '../assets/files/demo.txt',
                              'assets/files/demo.txt')),
        ('EXTRANEOUS', add('demo-skill/README.md', 'nobody asked for this\n')),
    ]
    for want, mut in cases:
        rows, fails = with_mutant(mut)
        good &= ok(want in _kinds(fails),
                   'a skill with a broken %s must be reported, got %s' % (want, fails))

    # NEGATIVE: build junk. Every kind the sweep claims to hunt is planted and caught,
    # including at the suite root and in a scripts/ folder -- places the per-skill rules
    # of this gate cannot see, which is the hole this sweep fills.
    junk_cases = [
        ('demo-skill/scripts/__pycache__/helper.cpython-312.pyc',
         'demo-skill/scripts/__pycache__'),
        ('scripts/__pycache__/audit_structure.cpython-312.pyc', 'scripts/__pycache__'),
        ('.DS_Store', '.DS_Store'),
        (_ART, _ART),
        ('demo-skill/references/mirror.md.bak', 'demo-skill/references/mirror.md.bak'),
        ('demo-skill/SKILL.md~', 'demo-skill/SKILL.md~'),
        ('demo-skill/scripts/helper.pyo', 'demo-skill/scripts/helper.pyo'),
    ]
    for rel_path, named in junk_cases:
        rows, fails = with_mutant(add(rel_path, 'planted junk\n'))
        hits = [f for f in fails if f[1] == 'BUILD-JUNK']
        good &= ok(len(hits) == 1 and named in hits[0][2],
                   'planted %s is reported once, naming %s, got %s' % (rel_path, named, fails))
        good &= ok(bool(fails), 'and build junk reaches the defect list that decides the '
                                'exit status (main() returns 1 whenever it is non-empty)')

    def junk_dir_empty(r):
        os.makedirs(os.path.join(r, 'pyrate-des', '__pycache__'), exist_ok=True)

    rows, fails = with_mutant(junk_dir_empty)
    good &= ok([f[2] for f in fails if f[1] == 'BUILD-JUNK'] ==
               ['pyrate-des/__pycache__ (directory of compiled bytecode; delete it and run '
                'Python with -B so it does not come back)'],
               'an __pycache__ directory is one finding even when it holds bytecode: %s'
               % fails)

    def many_pyc(r):
        for i in range(3):
            _write(r, 'demo-skill/scripts/__pycache__/helper%d.cpython-312.pyc' % i, 'x')

    rows, fails = with_mutant(many_pyc)
    good &= ok(len([f for f in fails if f[1] == 'BUILD-JUNK']) == 1,
               'three bytecode files in one folder are one finding, not four: %s' % fails)
    # a real source file whose name merely looks like the danger is left alone
    rows, fails = with_mutant(add('demo-skill/references/tmp-notes.md', 'text\n'))
    good &= ok(_kinds(fails) == [], 'a .md file about tmp is not a .tmp file: %s' % fails)
    # and the clean fixture, re-measured, is clean
    rows, fails = with_mutant(None)
    good &= ok(_kinds(fails) == [], 'the conforming fixture carries no junk: %s' % fails)

    # ...and the same measurements do not fire on the clean fixture
    rows, fails = with_mutant(None)
    good &= ok('BODY' not in _kinds(fails), 'the short body is not flagged as too long')
    # assets/files/README.md is allowed exactly where the contract puts it
    good &= ok('EXTRANEOUS' not in _kinds(fails),
               'the provenance README under assets/files/ is not extraneous')
    # a path inside a fenced block is a shell command, not a suite path
    rows, fails = with_mutant(add('demo-skill/references/extra.md',
                                  '```\ncd $HOME/nowhere\n```\n'))
    good &= ok('DEAD-PATH' not in _kinds(fails),
               'fenced shell text is not read as a path, got %s' % _kinds(fails))
    # a glob pattern is not a dead path either
    rows, fails = with_mutant(edit('demo-skill/SKILL.md', 'see `references/demo-mirror.md`',
                                   'see `references/occ-*.txt`'))
    good &= ok(_kinds(fails) == [], 'a glob is left alone, got %s' % fails)
    # a folder holding references/ but no SKILL.md is reported even without a manifest
    rows, fails = with_mutant(add('orphan-skill/references/x.md', 'text\n'))
    good &= ok('FOLDER-WITHOUT-SKILL' in _kinds(fails) and
               [f for f in fails if f[1] == 'FOLDER-WITHOUT-SKILL'][0][0] == 'orphan-skill' and
               len(rows) == 1,
               'a skill folder is discovered by its references/ dir alone, while the '
               'sound skill is still measured: fails=%s rows=%s' % (fails, rows))
    # the gate is not vacuous on the real suite: it must find the skills that are there
    real_rows, _real_fails = audit(ROOT)
    good &= ok(len(real_rows) >= 10,
               'the real suite has %d skills to check, so a PASS is earned' % len(real_rows))
    real_junk = junk_sweep(ROOT)
    good &= ok(all(os.path.exists(os.path.join(ROOT, m.split(' (')[0])) for _k, m in real_junk),
               'every build-junk finding names a path that exists, got %s' % real_junk)
    good &= ok(len(JUNK_SUFFIXES) >= 5 and '__pycache__' in JUNK_DIRS and
               '.DS_Store' in JUNK_NAMES and '.pyc' in JUNK_SUFFIXES and '.tmp' in JUNK_SUFFIXES,
               'the junk list still covers what the docstring promises: %s / %s / %s'
               % (sorted(JUNK_DIRS), sorted(JUNK_NAMES), JUNK_SUFFIXES))
    if good:
        print('self-test: %d checks run' % checks[0])
        print('audit_structure.py self-test PASSED (%d checks, 0 failures)' % checks[0])
        return 0
    print('audit_structure.py self-test FAILED (%d checks run)' % checks[0])
    return 1


if HELP:
    print(__doc__)
    sys.exit(0)

if SELF_TEST:
    sys.exit(self_test())

if __name__ == '__main__':
    sys.exit(main())
