#!/usr/bin/env python3
"""Audit every documentation citation that appears inside the suite's scripts/.

scripts/audit_citations.py covers the SKILL.md prose; it does not look inside the
Python helpers - yet those helpers print citations to the user as if they were
evidence ("only logged in BDMCMC analyses [summarize-results.md:20]"). A wrong line
number in a script is worse than a wrong one in prose: it is machine-generated output
and reads as authoritative.

The source is parsed with `ast`, so Python's own rules decide what a string is: implicit
concatenation across lines is already merged, and the position of a `%s` in a format
string is aligned to the argument that actually fills it. That alignment is what makes
the check exact rather than a guess based on neighbouring lines. Three styles:

  1. CONST + ":112-113"        the constant names the mirror
  2. "foo.md:20"               a literal path:line inside a string
  3. "[%s:20]" % CONST         the format argument resolves to a mirror constant

HARD (decides the exit status): the referenced mirror exists and the cited line number
is within it.

SOFT: when a citation is the only one in its string, any document text quoted in double
quotes in that string must sit on the cited line ("..." allowed as an elision). When a
string carries several citations the quote could not be attributed, so the site is
counted as LINE-ONLY instead of being guessed at.

Usage: python3 scripts/audit_script_citations.py [--verbose]
       python3 scripts/audit_script_citations.py --self-test
Exit 0 = every citation resolves to a real file and an in-range line.
"""

import ast
import glob
import os
import re
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERBOSE = '--verbose' in sys.argv

SPEC = r'(\d+(?:\s*[-–,]\s*\d+)*)'
SITE_PATH = re.compile(r'((?:\.\./)?(?:[a-z0-9-]+/)?references/[A-Za-z0-9._+-]+\.md|'
                       r'[A-Za-z0-9._+-]+\.md)(?<!  )\s*:\s*' + SPEC)
SITE_AFTER_FMT = re.compile(r'^\s*:\s*' + SPEC)
CONV = re.compile(r'%(?:\([^)]*\))?[-#0 +]*(?:\d+|\*)?(?:\.(?:\d+|\*))?[hlL]?([diouxXeEfFgGcrsa%])')
SPEC_ONLY = re.compile(r'^\s*:\s*' + SPEC + r'\s*$')
QUOTED = re.compile(r'"([^"]{20,300})"')


def parse_lines(spec):
    out = set()
    for part in spec.split(','):
        part = part.strip()
        m = re.match(r'^(\d+)\s*[-–]\s*(\d+)$', part)
        if m:
            out.update(range(int(m.group(1)), int(m.group(2)) + 1))
        elif part.isdigit():
            out.add(int(part))
    return out


def norm(s):
    s = s.replace('‘', "'").replace('’', "'").replace('“', '"').replace('”', '"')
    s = s.replace('–', '-').replace('—', '-')
    s = s.replace('\\_', '_').replace('\\*', '*').replace('\\`', '`')
    s = re.sub(r'\\(?=[\\[\]()#.+!-])', '', s)
    s = re.sub(r'\*+|`+', '', s)
    s = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', s)
    return re.sub(r'\s+', ' ', s).strip()


def mirror_index():
    idx = {}
    for p in sorted(glob.glob(os.path.join(ROOT, '*', 'references', '*.md'))):
        skill = os.path.relpath(p, ROOT).split(os.sep)[0]
        rel = os.path.relpath(p, os.path.join(ROOT, skill))
        lines = open(p, encoding='utf-8', errors='replace').read().split('\n')
        idx.setdefault(os.path.basename(p), []).append((skill, rel, lines))
    return idx


def resolve(ref, idx, own_skill):
    base = ref.split('/')[-1]
    key = ref.replace('\\', '/')
    if key.startswith('../') and key.endswith(base):
        skill = key.split('/')[1]
        cand = [c for c in idx.get(base, []) if c[0] == skill]
    elif key.startswith('references/'):
        cand = [c for c in idx.get(base, []) if c[0] == own_skill] or idx.get(base, [])
    else:
        cand = idx.get(base, [])
    seen = {}
    for c in cand:
        seen[os.path.join(ROOT, c[0], c[1])] = c[2]
    return sorted(seen.items())


def quote_verdict(quote, cands, want):
    parts = [p.strip() for p in norm(quote).split('...') if len(p.strip()) >= 12]
    if not parts:
        return None
    for _p, lines in cands:
        for ln in sorted(want):
            if 1 <= ln <= len(lines) and all(p in norm(lines[ln - 1]) for p in parts):
                return 'VERBATIM'
    for _p, lines in cands:
        for i, text in enumerate(lines, 1):
            if i not in want and all(p in norm(text) for p in parts):
                return 'STALE:%d' % i
    return 'ABSENT'


class Counters(dict):
    def __init__(self):
        dict.__init__(self, sites=0, verbatim=0, stale=0, absent=0, line_only=0)
    def bump(self, k, n=1):
        self[k] += n


class Site(object):
    __slots__ = ('label', 'spec', 'ref', 'lineno', 'prose', 'gradeable')

    def __init__(self, label, spec, ref, lineno, prose, gradeable):
        self.label, self.spec, self.ref = label, spec, ref
        self.lineno, self.prose, self.gradeable = lineno, prose, gradeable


def physical_line(text, offset, start_lineno):
    before = text[:offset]
    line = start_lineno + before.count('\n')
    seg = before.split('\n')[-1]
    tail = text[offset:].split('\n')[0]
    return line, seg + tail


def sites_from_format(node, consts, idx, own_skill, out, unresolved):
    """Style 3: "[%s:20]" % CONST - align each %s to the argument that fills it."""
    fmt = node.left.value
    start = node.left.lineno
    right = node.right
    if isinstance(right, ast.Tuple):
        args = right.elts
    elif isinstance(right, ast.Constant):
        args = [right]
    else:
        args = [right]
    arg_names = []
    for a in args:
        try:
            arg_names.append(ast.unparse(a))
        except Exception:
            arg_names.append('')
    n_sites_in_fmt = 0
    picks = []
    k = 0
    for m in CONV.finditer(fmt):
        if m.group(1) == '%':
            continue
        idx_arg = k
        k += 1
        if m.group(1) != 's':
            continue
        after = SITE_AFTER_FMT.match(fmt[m.end():])
        if not after:
            continue
        n_sites_in_fmt += 1
        name = arg_names[idx_arg] if idx_arg < len(arg_names) else ''
        picks.append((m.start(), name, after.group(1)))
    for off, name, spec in picks:
        if name in consts:
            out.append(Site(name, spec, consts[name], start + fmt[:off].count('\n'),
                            fmt, n_sites_in_fmt == 1))
        elif re.match(r'^[A-Z_][A-Z_0-9]*$', name):
            unresolved.append(('%s:%s' % (name, spec), 'constant is not a mirror path'))
        else:
            unresolved.append((('%s:' % spec)[:28], 'argument is not a bare constant'))


def collect(src, consts, idx, own_skill):
    tree = ast.parse(src)
    out, unresolved = [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod) \
                and isinstance(node.left, ast.Constant) \
                and isinstance(node.left.value, str):
            sites_from_format(node, consts, idx, own_skill, out, unresolved)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add) \
                and isinstance(node.left, ast.Name) and node.left.id in consts \
                and isinstance(node.right, ast.Constant) \
                and isinstance(node.right.value, str):
            m = SPEC_ONLY.match(node.right.value)
            if m:
                out.append(Site(node.left.id, m.group(1), consts[node.left.id],
                                node.right.lineno, node.right.value, False))
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            found = list(SITE_PATH.finditer(node.value))
            for m in found:
                line, prose = physical_line(node.value, m.start(), node.lineno)
                out.append(Site(m.group(1), m.group(2), m.group(1), line,
                                prose if len(found) == 1 else prose, len(found) == 1))
    return out, unresolved


def audit_script(path, idx):
    src = open(path, encoding='utf-8', errors='replace').read()
    own_skill = os.path.relpath(path, ROOT).split(os.sep)[0]
    consts = {}
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str) \
                and node.value.value.endswith('.md'):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    consts[t.id] = node.value.value
    c = Counters()
    bad = []
    sites, unresolved = collect(src, consts, idx, own_skill)
    for s in sites:
        c.bump('sites')
        cands = resolve(s.ref, idx, own_skill)
        if not cands:
            bad.append(('FILE-MISSING', path, '%s:%s' % (s.label, s.spec), 'no such mirror'))
            continue
        want = parse_lines(s.spec)
        longest = max(len(l) for _p, l in cands)
        if not want or max(want) > longest:
            bad.append(('LINE-OOB', path, '%s:%s' % (s.label, s.spec),
                        'mirror ends at line %d' % longest))
            continue
        if not s.gradeable:
            c.bump('line_only')
            continue
        for q in QUOTED.findall(s.prose):
            v = quote_verdict(q, cands, want)
            if v is None:
                continue
            if v == 'VERBATIM':
                c.bump('verbatim')
            elif v.startswith('STALE'):
                c.bump('stale')
                bad.append(('QUOTE-STALE', path, '%s:%s' % (s.label, s.spec),
                            '"%s..." is on mirror line %s, not %s'
                            % (q[:44].replace('\n', ' '), v[6:], s.spec)))
            else:
                c.bump('absent')
                bad.append(('QUOTE-ABSENT', path, '%s:%s' % (s.label, s.spec),
                            'not found in mirror: "%s..."' % q[:52].replace('\n', ' ')))
    for cite, why in unresolved:
        bad.append(('UNRESOLVED', path, cite[:30], why))
    return c, bad, len(consts)


HARD_KINDS = ('FILE-MISSING', 'LINE-OOB', 'SYNTAX')


def sweep(root=None):
    """(totals, defects, per-script rows) over every helper under `root` (default ROOT)."""
    global ROOT
    keep = ROOT
    if root:
        ROOT = root
    try:
        idx = mirror_index()
        scripts = [s for s in sorted(glob.glob(os.path.join(ROOT, '*', 'scripts', '*.py')))
                   if '__pycache__' not in s]
        tot = Counters()
        allbad = []
        rows = []
        for s in scripts:
            try:
                c, bad, nconst = audit_script(s, idx)
            except SyntaxError as exc:
                allbad.append(('SYNTAX', s, os.path.basename(s), str(exc)))
                rows.append((s, Counters(), 0, 1))
                continue
            for k in tot:
                tot[k] += c[k]
            allbad += bad
            rows.append((s, c, nconst, len(bad)))
        return tot, allbad, rows, idx
    finally:
        ROOT = keep


def main():
    tot, allbad, rows, idx = sweep()
    for s, c, nconst, nbad in rows:
        print('%-58s %4d sites  %4d mirror consts  %3d quotes verified  '
              '%3d line-only  %d defects'
              % (os.path.relpath(s, ROOT), c['sites'], nconst, c['verbatim'],
                 c['line_only'], nbad))
    hard = [b for b in allbad if b[0] in HARD_KINDS]
    print('\nTOTAL: %d citation sites in %d scripts; %d embedded quotes verbatim-at-line, '
          '%d stale, %d absent; %d sites line-verified only (quote not attributable)'
          % (tot['sites'], len(rows), tot['verbatim'], tot['stale'], tot['absent'],
             tot['line_only']))
    kinds = {}
    for k, _p, _c, _m in allbad:
        kinds[k] = kinds.get(k, 0) + 1
    print('defects by kind: ' + (', '.join('%s=%d' % kv for kv in sorted(kinds.items()))
                                 or 'none'))
    if VERBOSE or allbad:
        for k, p, cite, msg in allbad:
            print('  %-14s %-44s %-30s %s'
                  % (k, os.path.relpath(p, ROOT), cite[:30], msg[:100].replace('\n', ' ')))
    print('\nRESULT: ' + ('PASS' if not hard else 'FAIL (%d hard defects)' % len(hard)))
    return 0 if not hard else 1


# ------------------------------------------------------------------ self test
_MIRROR_A = """# Foo mirror

the gamma model strongly outperforms constant rates
a second verbatim sentence that lives on line four of this mirror file
filler line five
filler line six
"""
_MIRROR_B = "a sentence that lives on line one of the other skill's mirror file\n"
_CONSTS = ('FOO = "references/foo.md"\n'
           'BAR = "../skill-b/references/bar.md"\n'
           'TABLE = "references/table.txt"\n\n')


def _fixture():
    """A two-skill suite in a temp directory: the mirrors the fixture scripts cite."""
    tmp = tempfile.mkdtemp(prefix='audit-script-citations-selftest-')
    for rel, text in (('skill-a/references/foo.md', _MIRROR_A),
                      ('skill-b/references/bar.md', _MIRROR_B)):
        p = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='utf-8').write(text)
    return tmp


def _script(tmp, body, label='case', skill='skill-a'):
    """Run the whole tree with exactly one fixture helper in it, named after `label`.

    The scripts directories are wiped first: a leftover helper from the previous case
    would add its defects to this one's, and a count that drifts between cases proves
    nothing about either.
    """
    for d in glob.glob(os.path.join(tmp, '*', 'scripts')):
        shutil.rmtree(d, ignore_errors=True)
    d = os.path.join(tmp, skill, 'scripts')
    os.makedirs(d, exist_ok=True)
    name = 'fixture_%s.py' % re.sub(r'[^A-Za-z0-9]+', '_', label)
    with open(os.path.join(d, name), 'w', encoding='utf-8') as fh:
        fh.write(_CONSTS + body)
    return sweep(tmp)


def _kinds(bad):
    out = {}
    for k, _p, _c, _m in bad:
        out[k] = out.get(k, 0) + 1
    return out


def _good_script():
    """A helper that cites correctly in all three styles the auditor claims to read."""
    return ('def note():\n'
            '    line = FOO + ":4"\n'
            '    print(\'the docs say "the gamma model strongly outperforms constant '
            'rates" at foo.md:3\')\n'
            '    print(\'a style-3 citation [%s:3]\' % FOO)\n'
            '    print(\'and the cross-skill one [%s:1]\' % BAR)\n'
            '    return line\n')


def self_test():
    """Prove this auditor reads all three citation styles, and proves something.

    Two failure modes are fatal for a checker of machine-generated citations: reading
    only one of the styles it claims to read, and reporting PASS because it found
    nothing to look at. The style-by-style cases below answer the first; the clean
    fixture must produce a site whose QUOTE is verified verbatim at the cited line, and
    the live run at the end must report a non-zero number of verified quotes.
    """
    checks = [0]

    def ok(cond, msg):
        checks[0] += 1
        if not cond:
            print('SELF-TEST FAIL: %s' % msg)
            return False
        return True

    good = True
    tmp = _fixture()
    try:
        # ---- the primitives, in isolation
        good &= ok(parse_lines('120-123') == {120, 121, 122, 123}, 'a range expands')
        good &= ok(parse_lines('3, 5') == {3, 5}, 'a list of lines parses')
        good &= ok(parse_lines('7') == {7}, 'a bare line parses')
        good &= ok(norm('`PyRate` **is** run [see](http://x)') == 'PyRate is run see',
                   'norm strips markup but keeps case, got %r'
                   % norm('`PyRate` **is** run [see](http://x)'))
        idx = {'foo.md': [('skill-a', 'references/foo.md', _MIRROR_A.split('\n'))]}
        cands = [('skill-a/references/foo.md', _MIRROR_A.split('\n'))]
        good &= ok(quote_verdict('the gamma model strongly outperforms constant rates',
                                 cands, {3}) == 'VERBATIM',
                   'a quote on its cited line reads as VERBATIM')
        good &= ok(quote_verdict('a second verbatim sentence that lives on line four of this '
                                 'mirror file', cands, {3}) == 'STALE:4',
                   'a quote that moved is reported with the line it moved to')
        good &= ok(quote_verdict('a sentence that exists nowhere near this suite at all',
                                 cands, {3}) == 'ABSENT',
                   'a quote that is not in the document is ABSENT')
        good &= ok(quote_verdict('tiny', cands, {3}) is None,
                   'a fragment too short to attribute is not graded')
        good &= ok(len(resolve('../skill-b/references/bar.md',
                               {'bar.md': [('skill-b', 'references/bar.md', ['x'])]},
                               'skill-a')) == 1,
                   'a ../skill/ citation resolves in the named skill only')
        good &= ok(resolve('../skill-c/references/bar.md',
                           {'bar.md': [('skill-b', 'references/bar.md', ['x'])]},
                           'skill-a') == [],
                   'a citation to a skill that does not exist resolves to nothing (and so '
                   'is reported, not guessed)')
        # ---- the three styles, on a clean fixture
        total, bad, rows, _idx = _script(tmp, _good_script(), 'clean fixture')
        good &= ok(total['sites'] == 4,
                   'all three citation styles are read (style 1, 2, 2-in-prose, 3): %s'
                   % total)
        good &= ok(total['verbatim'] == 1,
                   'the literal quote beside its citation is verified verbatim, got %s'
                   % total['verbatim'])
        good &= ok(total['line_only'] == 1,
                   'the CONST+spec form is counted as line-verified only, got %s'
                   % total['line_only'])
        good &= ok(not bad, 'a correct script yields no defect, got %s' % bad)
        # ---- NEGATIVE: one broken input per rule the auditor claims to enforce
        cases = [
            ("print('see foo.md:999 for the wording')\n", {'LINE-OOB': 1}),
            ("print('see nowhere.md:2 for the wording')\n", {'FILE-MISSING': 1}),
            ("print('out of range at %s:99' % FOO)\n", {'LINE-OOB': 1}),
            ("print('%s:99' % (FOO + 'x'))\n", {'UNRESOLVED': 1}),
            ('print(\'the docs say "a second verbatim sentence that lives on line four of '
             'this mirror file" at foo.md:3\')\n', {'QUOTE-STALE': 1}),
            ('print(\'the docs say "a sentence that exists nowhere near this suite at all '
             'and is invented here" at foo.md:3\')\n', {'QUOTE-ABSENT': 1}),
            ("print('[%s:2]' % os.path.join(FOO, 'x'))\n", {'UNRESOLVED': 1}),
            ("import os\nprint('a %s:2 here' % TABLE)\n", {'UNRESOLVED': 1}),
        ]
        for body, want in cases:
            total, bad, rows, _idx = _script(tmp, body, 'one broken citation')
            good &= ok(_kinds(bad) == want,
                       '%r must report exactly %s, got %s' % (body[:48], want, _kinds(bad)))
            good &= ok(bool([b for b in bad if b[0] in HARD_KINDS]) ==
                       bool(want.get('LINE-OOB') or want.get('FILE-MISSING')),
                       'the hard/soft split of %r is what main() exits on' % body[:40])
        # a syntax error is reported per file, not as a crash
        total, bad, rows, _idx = _script(tmp, 'def broken(:\n    pass\n', 'unparseable helper')
        good &= ok(_kinds(bad) == {'SYNTAX': 1} and len(rows) == 1,
                   'an unparseable script is a SYNTAX defect, got %s' % _kinds(bad))
        good &= ok('SYNTAX' in HARD_KINDS, 'and it fails the gate')
        # several citations in one string: the quote is not attributable, so do not guess
        total, bad, rows, _idx = _script(
            tmp, 'print(\'the docs say "the gamma model strongly outperforms constant '
                 'rates" at foo.md:3 and foo.md:4\')\n', 'several citations in one string')
        good &= ok(not bad and total['verbatim'] == 0 and total['line_only'] == 2,
                   'an ambiguous quote is graded LINE-ONLY, never VERBATIM: %s %s'
                   % (total, bad))
        # a citation whose file and line are right but whose skill prefix is wrong
        total, bad, rows, _idx = _script(
            tmp, "print('from the other skill: ../skill-b/references/foo.md:2')\n",
            'wrong skill prefix')
        good &= ok(_kinds(bad) == {'FILE-MISSING': 1},
                   'foo.md is not in skill-b, and saying so is a defect, got %s'
                   % _kinds(bad))
        total, bad, rows, _idx = _script(
            tmp, "print('from the other skill: ../skill-b/references/bar.md:1')\n",
            'right skill prefix')
        good &= ok(not bad and total['sites'] == 1,
                   'the same form with a real skill in front of it verifies, got %s' % bad)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # ---- and against the real suite: a non-zero amount of work was actually verified
    total, bad, rows, idx = sweep()
    good &= ok(len(rows) >= 5, 'the suite has %d helper scripts to read' % len(rows))
    good &= ok(len(idx) >= 10, 'the mirror index has %d documents' % len(idx))
    good &= ok(total['sites'] > 0, 'the real scripts carry %d citation sites' % total['sites'])
    good &= ok(total['verbatim'] > 0,
               'REAL RUN VERIFIES %d QUOTES VERBATIM AT THE CITED LINE -- a run of this '
               'auditor that verifies none of its citations must never pass'
               % total['verbatim'])
    good &= ok(sum(1 for b in bad if b[0] == 'UNRESOLVED') <= total['sites'],
               'unresolved citations (%d) cannot outnumber the sites found (%d)'
               % (sum(1 for b in bad if b[0] == 'UNRESOLVED'), total['sites']))
    if good:
        print('self-test: %d checks run' % checks[0])
        print('audit_script_citations.py self-test PASSED (%d checks, 0 failures)'
              % checks[0])
        return 0
    print('audit_script_citations.py self-test FAILED (%d checks run)' % checks[0])
    return 1


if '--self-test' in sys.argv or '-t' in sys.argv:
    sys.exit(self_test())

if __name__ == '__main__':
    sys.exit(main())
