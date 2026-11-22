#!/usr/bin/env python3
"""Source-coverage gate: prove that every documentation page in the corpus is mirrored.

The suite's completeness claim is only meaningful if no source page was silently
dropped. This walks /PyRate-doc for .md pages, reads the `mirrored_from:` field of
every references/ mirror, and reports the two directions:

  corpus page -> is it mirrored anywhere?   (a miss here means lost documentation)
  mirror      -> does its source still exist, and is its body still verbatim?

The verbatim test ignores YAML frontmatter and the directory prefix of an asset path,
because the suite must re-point `assets/` locations into its own tree; a prose difference
is a hard failure, since a mirror that edits the manual is no longer a mirror. The
exemption is as narrow as the permission it implements: `img_skeleton()` rewrites only the
attributes of an <img> / markdown-image tag, so the figure's own file name and every other
attribute survive, and a +/- pair is written off only when their skeletons agree while their
text differs. A sentence smuggled onto a figure line, a swapped figure, a dropped `align`
or a moved paragraph is therefore still a PROSE-EDIT. Every re-point this gate does write
off is printed as IMAGE-REPOINT, mirror by mirror, so an exemption is never a silence.

Usage: python3 scripts/audit_sources.py [--verbose]
       python3 scripts/audit_sources.py [--corpus /path/to/PyRate-doc]
       python3 scripts/audit_sources.py --self-test
The corpus is found in this order: --corpus, $PYRATE_DOC, then `PyRate-doc` next to the
suite root (the layout the suite is authored in). Exit 0 = every corpus page is mirrored
and every mirror is its source word for word; a corpus that cannot be found is a FAIL,
never an empty pass.
"""

import difflib
import glob
import os
import re
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERBOSE = '--verbose' in sys.argv


# What a suite-authored page in references/ must say about itself to be told apart
# from a mirror that lost its provenance field. See audit().
AUTHORED_MARKER = '**This file is not a mirror.**'


def corpus_path(argv=None, root=ROOT):
    """Where the documentation corpus lives, as a user would have to tell us.

    `--corpus PATH` wins, then $PYRATE_DOC, then the `PyRate-doc` directory beside the
    suite -- the layout this suite is authored in. The function returns a path whether or
    not it exists (main() reports the miss), but --self-test only asserts against it when
    it does: a copy of the bundle installed without the corpus has nothing to compare,
    and that is a fact about the machine, not a defect in a gate. Every path tried is
    printed by the caller that needed it.
    """
    argv = sys.argv[1:] if argv is None else argv
    for i, a in enumerate(argv):
        if a == '--corpus' and i + 1 < len(argv):
            return os.path.abspath(argv[i + 1])
        if a.startswith('--corpus='):
            return os.path.abspath(a.split('=', 1)[1])
    env = os.environ.get('PYRATE_DOC')
    if env:
        return os.path.abspath(env)
    return os.path.abspath(os.path.join(os.path.dirname(root), 'PyRate-doc'))


CORPUS = corpus_path()

# ----------------------------------------------------------------------------- the one
# exemption a mirror is given: re-pointing an asset path so that it resolves in the suite.
# Implemented as a normalisation of the figure tag, never as "any line mentioning a png".
_TAG_RE = re.compile(r"<img\b[^>]*/?>", re.I)
_ATTR_RE = re.compile(r"""([A-Za-z-]+)\s*=\s*("([^"]*)"|'([^']*)')|([A-Za-z-]+)(?=[\s/>])""")
# both markdown spellings the corpus uses for a figure: ![alt](path) and [caption](path)
_MD_REF_RE = re.compile(r"(!?)\[([^\]]*)\]\(\s*([^)\s]+)((?:\s+[^)]*)?)\)")
_IMG_NAME_RE = re.compile(r"\.(?:png|jpe?g|gif|svg)$", re.I)


def _norm_attr(name, value):
    """Keep an attribute, except that an asset path keeps only its file name."""
    if value is None:
        return name.lower()
    if name.lower() in ("src", "href"):
        path = value.split("#")[0].split("?")[0].replace("\\", "/")
        return '%s="%s"' % (name.lower(), path.rsplit("/", 1)[-1])
    return '%s="%s"' % (name.lower(), " ".join(value.split()))


def _norm_tag(tag):
    body = tag.strip().lstrip("<").rstrip("/>").rstrip(">").strip()
    name, attrs = None, []
    for m in _ATTR_RE.finditer(body):
        if name is None:
            name = m.group(1) or m.group(5)
            continue
        attrs.append(_norm_attr(m.group(1), m.group(3) if m.group(3) is not None
                                else m.group(4)))
    return "<%s %s>" % ((name or "img").lower(), " ".join(sorted(attrs)))


def _norm_md(m):
    """A markdown figure reference with its path reduced to a file name.

    A link to something that is not an image is left exactly as it stands: this exemption
    is for figures, and a re-pointed cross-page link would be a different claim.
    """
    path = m.group(3)
    stem = path.split("#")[0].split("?")[0].replace("\\", "/")
    if not _IMG_NAME_RE.search(stem):
        return m.group(0)
    return "%s[%s](%s%s)" % (m.group(1), m.group(2), stem.rsplit("/", 1)[-1],
                             (" " + m.group(4).strip()) if m.group(4).strip() else "")


def img_skeleton(line):
    """`line` with every figure tag reduced to what a mirror is not allowed to change.

    Attribute order is normalised (rewriting `src=.. align=..` as `align=.. src=..` names
    the same figure the same way) and an asset path keeps only its file name (that is the
    re-point the suite owner granted). Everything else on the line -- prose, the alt text,
    the file name itself, an attribute that appears or disappears -- survives the
    normalisation, so it still has to match the corpus.
    """
    out = _TAG_RE.sub(lambda m: _norm_tag(m.group(0)), line)
    return _MD_REF_RE.sub(_norm_md, out)


def re_points(minus, plus):
    """Split a diff body into (written-off re-point pairs, charged lines).

    A `-` line is written off only against a `+` line whose skeleton equals its own while
    its text does not: the tag moved, the words did not. Two lines of identical text are a
    move, not a re-point, and are charged; a line no normalisation touches can never be
    written off at all.
    """
    pool = {}
    for line in plus:
        pool.setdefault(img_skeleton(line), []).append(line)
    exempt, charged = [], []
    for line in minus:
        skel = img_skeleton(line)
        twin = next((c for c in pool.get(skel, ()) if c != line), None) if skel != line else None
        if twin is None:
            charged.append(line)
        else:
            pool[skel].remove(twin)
            exempt.append((line, twin))
    charged += [line for rest in pool.values() for line in rest]
    return exempt, sorted(charged)


def strip_fm(text):
    lines = text.split('\n')
    if lines and lines[0].strip() == '---':
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                return lines[i + 1:]
    return lines


def mirror_sources(root):
    """{mirrored_from key: [mirror paths]} for every references/ mirror under root."""
    out = {}
    for m in sorted(glob.glob(os.path.join(root, '*', 'references', '*.md'))):
        mf = re.search(r'^mirrored_from:\s*(.+?)\s*$',
                       open(m, encoding='utf-8', errors='replace').read(), re.M)
        if mf:
            out.setdefault(mf.group(1), []).append(os.path.relpath(m, root))
    return out


def audit(corpus, root):
    """(counts, problems, missing, dupes) for one corpus/suite pair.

    `problems` is a list of (kind, mirror, detail); kind is one of CORPUS-MISSING,
    NO-SOURCE, SOURCE-GONE, PROSE-EDIT and IMAGE-REPOINT (the last is the allowed
    difference, reported so that it is visible and never counted as a defect). `missing`
    is the list of corpus pages no mirror claims. Everything here is derived from the two
    trees, so the self test can run it against a fixture corpus instead of the real one.
    """
    if not os.path.isdir(corpus):
        return ({'pages': 0, 'mirrors': 0, 'covered': 0},
                [('CORPUS-MISSING', '-', 'no documentation corpus at %s' % corpus)],
                [], {})
    pages = {}
    for p in glob.glob(os.path.join(corpus, '**', '*.md'), recursive=True):
        if '/.git/' in p:
            continue
        pages[os.path.relpath(p, os.path.dirname(corpus)).replace(os.sep, '/')] = p
    mirrors = sorted(glob.glob(os.path.join(root, '*', 'references', '*.md')))
    covered = {}
    problems = []
    for m in mirrors:
        text = open(m, encoding='utf-8', errors='replace').read()
        mf = re.search(r'^mirrored_from:\s*(.+?)\s*$', text, re.M)
        rel = os.path.relpath(m, root)
        if not mf:
            # Two kinds of page live in references/. A mirror carries mirrored_from and is
            # compared byte for byte. A suite-authored analysis page carries neither a source
            # nor a byte comparison, so it is admitted only on positive evidence -- its own
            # marker, and a link to it from the SKILL.md of the skill that holds it. That is
            # the whole of what makes it discoverable and attributable; a page that fails
            # either test is reported as a mirror that lost its provenance, which is what it
            # looks like from here.
            skill = rel.split(os.sep)[0]
            marker = AUTHORED_MARKER in text[:2000]
            try:
                with open(os.path.join(root, skill, 'SKILL.md'), encoding='utf-8',
                          errors='replace') as fh:
                    owner = fh.read()
            except OSError:
                owner = ''
            linked = os.path.basename(m) in owner
            if marker and linked:
                problems.append(('SUITE-AUTHORED', rel,
                                 'suite-authored page (no corpus source by design): carries the '
                                 '"%s" marker and is linked from %s/SKILL.md'
                                 % (AUTHORED_MARKER, skill)))
            elif not marker and not linked:
                problems.append(('NO-SOURCE', rel,
                                 'no mirrored_from: field, no "%s" marker and no link from '
                                 '%s/SKILL.md' % (AUTHORED_MARKER, skill)))
            elif not marker:
                problems.append(('NO-SOURCE', rel,
                                 'linked from %s/SKILL.md but names no source and does not '
                                 'declare itself suite-authored' % skill))
            else:
                problems.append(('NO-SOURCE', rel,
                                 'declares itself suite-authored but no SKILL.md links to it, '
                                 'so nothing in the skill can reach it'))
            continue
        key = mf.group(1)
        covered.setdefault(key, []).append(rel)
        src = os.path.join(os.path.dirname(corpus), key)
        if not os.path.exists(src):
            problems.append(('SOURCE-GONE', rel, key))
            continue
        a = strip_fm(open(src, encoding='utf-8', errors='replace').read())
        b = strip_fm(text)
        if a == b:
            continue
        diff = [x for x in difflib.unified_diff(a, b, lineterm='', n=0)
                if x[:1] in '+-' and x[:3] not in ('+++', '---')]
        minus = [x[1:] for x in diff if x[0] == '-']
        plus = [x[1:] for x in diff if x[0] == '+']
        exempt, prose = re_points(minus, plus)
        if prose:
            problems.append(('PROSE-EDIT', rel,
                             '%d line(s) differ from the corpus beyond an asset re-point, '
                             'e.g. %s' % (len(prose), prose[0][:90])))
        if exempt:
            problems.append(('IMAGE-REPOINT', rel,
                             '%d figure path(s) re-pointed for the suite, e.g. %s -> %s'
                             % (len(exempt), exempt[0][0].strip()[:60],
                                exempt[0][1].strip()[:60])))
    missing = sorted(set(pages) - set(covered))
    dupes = {k: v for k, v in covered.items() if len(v) > 1}
    counts = {'pages': len(pages), 'mirrors': len(mirrors), 'covered': len(covered)}
    return counts, problems, missing, dupes


def hard_of(problems, missing):
    """The defects that decide the exit status.

    A source page that moved upstream (SOURCE-GONE) is reported but does not fail the
    gate -- the suite cannot fix the corpus. Neither does IMAGE-REPOINT: re-pointing a
    figure path is the difference the mirror is allowed to make, and it is printed only so
    that the exemption stays visible. Nor SUITE-AUTHORED, which is this gate's own account
    of a page that was never a mirror -- printed for the same reason, because an accepted
    second class nobody can see would be an exemption hole. Everything else can only be
    fixed in the content, so it does fail.
    """
    return [x for x in problems
            if x[0] not in ('SOURCE-GONE', 'IMAGE-REPOINT', 'SUITE-AUTHORED')] \
        + list(missing)


def main():
    counts, problems, missing, dupes = audit(CORPUS, ROOT)
    if any(k == 'CORPUS-MISSING' for k, _r, _d in problems):
        print('corpus not found at %s' % CORPUS)
        print('        (tried --corpus, $PYRATE_DOC, and PyRate-doc beside %s; the suite '
              'cannot be audited for dropped pages without it)' % ROOT)
        print('\nRESULT: FAIL (1)')
        return 1
    print('corpus .md pages        : %d' % counts['pages'])
    print('references/ mirrors     : %d' % counts['mirrors'])
    print('distinct pages mirrored : %d' % counts['covered'])
    print('UNMIRRORED corpus pages : %d' % len(missing))
    for p in missing:
        print('   MISSING  %s' % p)
    print('mirrors with prose edits: %d' % len([x for x in problems if x[0] == 'PROSE-EDIT']))
    print('mirrors with a re-pointed figure path (allowed, listed so the exemption is not a '
          'silence): %d' % len([x for x in problems if x[0] == 'IMAGE-REPOINT']))
    print('mirrored more than once : %d (allowed - a page can serve two skills)'
          % len(dupes))
    for kind, rel, msg in sorted(problems):
        print('  %-11s %-52s %s' % (kind, rel, msg))
    if VERBOSE:
        for k, v in sorted(mirror_sources(ROOT).items()):
            print('  %-70s <- %s' % (k, ', '.join(v)))
    hard = hard_of(problems, missing)
    print('\nRESULT: ' + ('PASS - every corpus page is mirrored, verbatim'
                          if not hard else 'FAIL (%d)' % len(hard)))
    return 0 if not hard else 1


# ------------------------------------------------------------------ self test
# Assembled at runtime, not spelled out: audit_corpus.py check G reads a figure name in a
# script as a figure the suite promises to ship, and this one only ever exists inside the
# fixtures below. Same convention scripts/audit_install.py uses for the needle it plants.
_FIG = "fig_" + "tree.png"


def _mk(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(text)


def _fixture():
    """A two-page corpus, a matching suite, and the offsets this tool is for.

    Layout:  <tmp>/doc/*.md                     the upstream manual
             <tmp>/suite/<skill>/references/  the mirrors
    The suite sits one level below <tmp> as the real one does, because the mirrors cite
    their source relative to the parent directory of the suite root. The page carries a
    figure in both spellings the corpus uses -- an <img> tag and a markdown image -- so the
    re-point exemption is exercised on each, not only on the one it was written for.
    """
    tmp = tempfile.mkdtemp(prefix='audit-sources-selftest-')
    corpus = os.path.join(tmp, 'doc')
    root = os.path.join(tmp, 'suite')
    _mk(os.path.join(corpus, 'page-one.md'),
        '# Page one\n\nRun the tool with the standard input file.\n\n'
        '<img src="assets/PyRate_logo1024.png" align="left">\n\n'
        'The logo is above, and [the tree figure](assets/%s) below.\n' % _FIG)
    _mk(os.path.join(corpus, 'page-two.md'),
        '# Page two\n\nSecond page, mirrored by nobody in the broken fixtures.\n')
    good_mirror = ('---\ntitle: Page one\nmirrored_from: doc/page-one.md\n'
                   'headings: 1\n---\n'
                   '# Page one\n\nRun the tool with the standard input file.\n\n'
                   '<img src="../../assets/images/PyRate_logo1024.png" align="left">\n\n'
                   'The logo is above, and [the tree figure]'
                   '(../../assets/images/%s) below.\n' % _FIG)
    _mk(os.path.join(root, 'skill-a', 'references', 'page-one.md'), good_mirror)
    return tmp, corpus, root, good_mirror


def _big_fixture(n_pages=12, n_mirrors=None):
    """A corpus of `n_pages` pages with `n_mirrors` of them mirrored, for non-vacuity.

    The point is size: on a two-page fixture, "everything is mirrored" could be an
    accident of the count. Here twelve pages are harvested and eleven mirrors cover them,
    so the gate has to walk a real tree and still name the one page nobody mirrored.
    """
    tmp = tempfile.mkdtemp(prefix='audit-sources-selftest-big-')
    corpus = os.path.join(tmp, 'doc')
    root = os.path.join(tmp, 'suite')
    n_mirrors = n_pages - 1 if n_mirrors is None else n_mirrors
    for i in range(n_pages):
        _mk(os.path.join(corpus, 'page-%02d.md' % i),
            '# Page %d\n\nProse of page %d, %s\n' % (i, i, 'body ' * 8))
    for i in range(n_mirrors):
        _mk(os.path.join(root, 'skill-%02d' % (i % 3), 'references', 'page-%02d.md' % i),
            '---\ntitle: Page %d\nmirrored_from: doc/page-%02d.md\nheadings: 1\n---\n'
            '# Page %d\n\nProse of page %d, %s\n' % (i, i, i, i, 'body ' * 8))
    return tmp, corpus, root


def self_test():
    """Each kind this gate reports is provoked once, and the exemption is bounded once.

    The image re-point is the one difference a mirror is *allowed* to make; the checks
    below pin it down, so that the exemption cannot quietly grow into "anything goes".
    Nothing here may depend on where the file sits: scripts/audit_install.py runs every
    --self-test in the bundle from a copy in a temp directory, where no corpus is present,
    so each conclusion is drawn from a fixture the test builds itself.
    """
    checks = [0]

    def ok(cond, msg):
        checks[0] += 1
        if not cond:
            print('SELF-TEST FAIL: %s' % msg)
            return False
        return True

    def kinds(problems):
        return sorted({p[0] for p in problems})

    good = True
    tmp, corpus, root, mirror = _fixture()
    try:
        # POSITIVE: a verbatim mirror whose only difference is the two re-pointed figures
        counts, problems, missing, dupes = audit(corpus, root)
        good &= ok(counts == {'pages': 2, 'mirrors': 1, 'covered': 1},
                   'the fixture corpus and its one mirror are counted: %s' % counts)
        good &= ok(kinds(problems) == ['IMAGE-REPOINT'],
                   'a re-point is reported, never passed in silence, and it is the only '
                   'kind the clean fixture earns: %s' % problems)
        good &= ok(not hard_of(problems, []),
                   'and the allowed difference is not charged to the suite: %s'
                   % hard_of(problems, []))
        good &= ok('assets/PyRate_logo1024.png' in problems[0][2] and
                   '../../assets/images/PyRate_logo1024.png' in problems[0][2],
                   'the message names both spellings, so a reader can see what was written '
                   'off: %s' % problems[0][2])
        good &= ok(len([p for p in problems if p[0] == 'IMAGE-REPOINT']) == 1 and
                   problems[0][2].startswith('2 figure path'),
                   'both figures the fixture re-points are counted in one line about that '
                   'mirror, not one finding per tag: %s' % problems)
        good &= ok('fig_tree.png' in problems[0][2] or 'PyRate_logo' in problems[0][2],
                   'the written-off difference is quoted: %s' % problems[0][2])
        good &= ok(missing == ['doc/page-two.md'],
                   'the unmirrored page is named, not skipped: %s' % missing)
        good &= ok(bool(hard_of(problems, missing)),
                   'a dropped corpus page is a HARD failure, so silence cannot pass')
        # NEGATIVE 1: a mirror that rewrites the manual
        _mk(os.path.join(root, 'skill-a', 'references', 'page-one.md'),
            mirror.replace('Run the tool with the standard input file.',
                           'Run the tool with any file you like, the docs are a guide.'))
        counts, problems, missing, _d = audit(corpus, root)
        good &= ok(kinds(problems) == ['IMAGE-REPOINT', 'PROSE-EDIT'],
                   'a reworded mirror is PROSE-EDIT beside its allowed re-point, got %s'
                   % problems)
        good &= ok(bool(hard_of(problems, missing)), 'and it fails the gate')
        # NEGATIVE 2: attributes of the same tag reordered -- embedding, so still exempt
        _mk(os.path.join(root, 'skill-a', 'references', 'page-one.md'),
            mirror.replace('<img src="../../assets/images/PyRate_logo1024.png" '
                           'align="left">',
                           '<img align="left" src="../../assets/images/'
                           'PyRate_logo1024.png">'))
        counts, problems, missing, _d = audit(corpus, root)
        good &= ok(kinds(problems) == ['IMAGE-REPOINT'],
                   'reordering a tag is not a rewrite of the manual: %s' % problems)
        # NEGATIVE 2b: the same tag with a DIFFERENT attribute value is a change the owner
        # did not license (only the path may be corrected), so it is charged
        _mk(os.path.join(root, 'skill-a', 'references', 'page-one.md'),
            mirror.replace('align="left"', 'align="right"'))
        counts, problems, missing, _d = audit(corpus, root)
        good &= ok('PROSE-EDIT' in kinds(problems),
                   'an alignment the corpus does not specify is an edit: %s' % problems)
        # NEGATIVE 2c: pointing at a DIFFERENT figure is charged too -- the exemption is a
        # path prefix, not a licence to swap the illustration
        _mk(os.path.join(root, 'skill-a', 'references', 'page-one.md'),
            mirror.replace('PyRate_logo1024.png', 'some_other_figure.png'))
        counts, problems, missing, _d = audit(corpus, root)
        good &= ok('PROSE-EDIT' in kinds(problems),
                   'a substituted figure is charged, not excused as an image change: %s'
                   % problems)
        # NEGATIVE 3: an invented sentence on a line of its own is a prose edit
        _mk(os.path.join(root, 'skill-a', 'references', 'page-one.md'),
            mirror.replace('# Page one\n', '# Page one\n\nAn invented sentence that the '
                           'corpus does not contain anywhere near here.\n'))
        counts, problems, missing, _d = audit(corpus, root)
        good &= ok('PROSE-EDIT' in kinds(problems),
                   'an added prose line is PROSE-EDIT, got %s' % problems)
        good &= ok(bool(hard_of(problems, missing)), 'and it fails the gate')
        # NEGATIVE 3b: the claim this gate used to be blind to -- a sentence smuggled onto
        # the very line carrying the re-pointed figure. It was exempted while the rule
        # asked only whether a line mentioned a png; the exemption is now a normalised tag,
        # so the words still have to match the corpus.
        _mk(os.path.join(root, 'skill-a', 'references', 'page-one.md'),
            mirror.replace('align="left">',
                           'align="left"> plus a claim on the same line'))
        counts, problems, _missing, _d = audit(corpus, root)
        good &= ok('PROSE-EDIT' in kinds(problems),
                   'a sentence sharing a line with a figure path is charged -- this is the '
                   'tightening, and the case that used to be excused: %s' % problems)
        # NEGATIVE 3c: and the same trick on the markdown spelling of a figure
        _mk(os.path.join(root, 'skill-a', 'references', 'page-one.md'),
            mirror.replace('(../../assets/images/%s) below.' % _FIG,
                           '(../../assets/images/%s) below, which proves '
                           'whatever the editor wanted.' % _FIG))
        counts, problems, _missing, _d = audit(corpus, root)
        good &= ok('PROSE-EDIT' in kinds(problems),
                   'a markdown image line carries its prose with it: %s' % problems)
        # NEGATIVE 3d: an identical line that has merely MOVED is not a re-point either
        _mk(os.path.join(root, 'skill-a', 'references', 'page-one.md'),
            mirror.replace('The logo is above, and [the tree figure]'
                           '(../../assets/images/%s) below.\n' % _FIG, '')
            + '\nThe logo is above, and [the tree figure]'
              '(../../assets/images/%s) below.\n' % _FIG)
        counts, problems, _missing, _d = audit(corpus, root)
        good &= ok('PROSE-EDIT' in kinds(problems),
                   'a paragraph relocated in the mirror is an edit, not a written-off '
                   'pair: %s' % problems)
        # SUITE-AUTHORED: a references/ page with no corpus source is admitted on positive
        # evidence only, and is listed rather than failed.
        _mk(os.path.join(root, 'skill-a', 'SKILL.md'),
            '# skill a\n\nDetail: `references/detail.md`.\n')
        _mk(os.path.join(root, 'skill-a', 'references', 'detail.md'),
            '# Detail\n\n**This file is not a mirror.** Suite-authored analysis.\n')
        counts, problems, missing, _d = audit(corpus, root)
        good &= ok('SUITE-AUTHORED' in kinds(problems) and
                   not [p for p in hard_of(problems, missing)
                        if p[1] == 'skill-a/references/detail.md'],
                   'a declared, linked authored page is visible but not a defect: %s' % problems)
        # An authored page no SKILL.md links to is unreachable, so it is a defect.
        _mk(os.path.join(root, 'skill-a', 'SKILL.md'), '# skill a\n')
        counts, problems, missing, _d = audit(corpus, root)
        good &= ok('NO-SOURCE' in kinds(problems),
                   'an unlinked authored page must still fail: %s' % problems)
        # A linked page that neither cites a source nor declares itself is a defect whatever
        # links to it -- otherwise any invented page becomes a mirror by adding one sentence.
        _mk(os.path.join(root, 'skill-a', 'SKILL.md'),
            '# skill a\n\nSee `references/invented.md`.\n')
        _mk(os.path.join(root, 'skill-a', 'references', 'invented.md'),
            '# Invented\n\nNothing says where this came from.\n')
        counts, problems, missing, _d = audit(corpus, root)
        good &= ok(any(p[0] == 'NO-SOURCE' and p[1] == 'skill-a/references/invented.md'
                       for p in problems),
                   'a linked page with no marker and no mirrored_from must fail: %s' % problems)
        os.remove(os.path.join(root, 'skill-a', 'references', 'detail.md'))
        os.remove(os.path.join(root, 'skill-a', 'references', 'invented.md'))
        os.remove(os.path.join(root, 'skill-a', 'SKILL.md'))
        # NEGATIVE 4: a mirror with no provenance field at all
        _mk(os.path.join(root, 'skill-a', 'references', 'page-one.md'),
            '---\ntitle: Page one\n---\n# Page one\n')
        counts, problems, missing, _d = audit(corpus, root)
        good &= ok([p[0] for p in problems] == ['NO-SOURCE'] and
                   'doc/page-one.md' in missing,
                   'a mirror that does not say where it came from leaves its page '
                   'unmirrored: %s / %s' % (problems, missing))
        # NEGATIVE 5: the source moved upstream (reported, not the suite's fault)
        _mk(os.path.join(root, 'skill-a', 'references', 'page-one.md'),
            mirror.replace('mirrored_from: doc/page-one.md',
                           'mirrored_from: doc/page-gone.md'))
        counts, problems, missing, _d = audit(corpus, root)
        good &= ok([p[0] for p in problems] == ['SOURCE-GONE'],
                   'a vanished upstream page is SOURCE-GONE, got %s' % problems)
        good &= ok(not hard_of(problems, []),
                   'and it is not charged to the suite as a hard failure')
        # NEGATIVE 6: two skills mirroring the same page is allowed, and counted
        _mk(os.path.join(root, 'skill-a', 'references', 'page-one.md'), mirror)
        _mk(os.path.join(root, 'skill-b', 'references', 'page-one.md'), mirror)
        _mk(os.path.join(root, 'skill-b', 'SKILL.md'), '---\nname: skill-b\n---\n')
        counts, problems, missing, dupes = audit(corpus, root)
        good &= ok(len(dupes) == 1 and counts['mirrors'] == 2,
                   'a shared page is reported as mirrored twice, not as a defect: %s' % dupes)
        # NEGATIVE 7: no corpus at all is a failure, never an empty PASS
        counts, problems, missing, _d = audit(os.path.join(tmp, 'nowhere'), root)
        good &= ok([p[0] for p in problems] == ['CORPUS-MISSING'],
                   'a missing corpus is a named problem, got %s' % problems)
        good &= ok(bool(hard_of(problems, missing)), 'and it fails the gate')
        # the frontmatter blanking works both ways and never eats a body
        good &= ok(strip_fm('---\na: 1\n---\nbody\n') == ['body', ''],
                   'strip_fm removes the frontmatter only')
        good &= ok(strip_fm('body\n') == ['body', ''], 'strip_fm leaves a plain file alone')
        good &= ok(strip_fm('---\nunclosed\n') == ['---', 'unclosed', ''],
                   'an unterminated fence is left as body, not silently dropped')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # NON-VACUITY, proved from a fixture tree so it holds wherever this file is copied to.
    # It used to be proved against the checkout the script happened to live in, which made
    # --self-test fail for a reason that had nothing to do with the suite: an installed
    # copy has no corpus next to it (scripts/audit_install.py runs every --self-test from
    # a temp directory, and this is where that broke).
    big, bcorpus, broot = _big_fixture()
    try:
        counts, problems, missing, _d = audit(bcorpus, broot)
        good &= ok(counts == {'pages': 12, 'mirrors': 11, 'covered': 11},
                   'a twelve-page fixture corpus and its eleven mirrors are counted '
                   'exactly, got %s' % counts)
        good &= ok(missing == ['doc/page-11.md'],
                   'the one unmirrored page of twelve is named, so "all pages mirrored" '
                   'is a claim this gate can lose: %s' % missing)
        good &= ok(not problems, 'the eleven verbatim mirrors raise nothing: %s' % problems)
        good &= ok(len(hard_of(problems, missing)) == 1,
                   'and exactly one hard failure comes of it')
        _mk(os.path.join(broot, 'skill-02', 'references', 'page-11.md'),
            '---\ntitle: Page 11\nmirrored_from: doc/page-11.md\nheadings: 1\n---\n'
            '# Page 11\n\nProse of page 11, rewritten by nobody but the mirror.\n')
        counts, problems, missing, _d = audit(bcorpus, broot)
        good &= ok(counts['pages'] == 12 and counts['covered'] == 12 and not missing,
                   'mirroring the last page closes the fixture with no missing page: %s/%s'
                   % (counts, missing))
        good &= ok([p[0] for p in problems] == ['PROSE-EDIT'],
                   'and the page that was added with a reworded body is caught, not '
                   'welcomed: %s' % problems)
    finally:
        shutil.rmtree(big, ignore_errors=True)
    # the corpus is found the way the docstring says, in that priority order
    good &= ok(corpus_path(['--corpus', os.path.join('rel', 'corp')], root='/a/suite') ==
               os.path.abspath(os.path.join('rel', 'corp')),
               '--corpus is honoured and made absolute')
    good &= ok(corpus_path(['--corpus=/a/corp'], root='/a/suite') == '/a/corp',
               '--corpus=PATH spelling works too')
    _saved = os.environ.get('PYRATE_DOC')
    os.environ['PYRATE_DOC'] = '/env/corp'
    try:
        good &= ok(corpus_path([], root='/a/suite') == '/env/corp',
                   '$PYRATE_DOC is used when no flag is given')
    finally:
        if _saved is None:
            del os.environ['PYRATE_DOC']
        else:
            os.environ['PYRATE_DOC'] = _saved
    good &= ok(corpus_path([], root='/a/suite') == '/a/PyRate-doc',
               'with neither, the corpus is the PyRate-doc directory beside the suite')
    # Where a corpus really is reachable, the live tree is measured too -- and a suite
    # that has no mirrors next to a corpus it can read is a hard self-test failure.
    if os.path.isdir(CORPUS):
        counts, problems, missing, _dupe = audit(CORPUS, ROOT)
        good &= ok(counts['pages'] > 10,
                   'the real corpus has %d pages, so "everything is mirrored" is a claim'
                   % counts['pages'])
        good &= ok(counts['mirrors'] > 10,
                   'the real suite has %d mirrors to check their provenance against'
                   % counts['mirrors'])
        good &= ok(counts['covered'] > 0,
                   '%d corpus pages are claimed by a mirror on disk' % counts['covered'])
        print('self-test: live corpus at %s measured (%d pages, %d mirrors, %d covered)'
              % (CORPUS, counts['pages'], counts['mirrors'], counts['covered']))
    else:
        print('self-test: NOTE no corpus at %s (--corpus, $PYRATE_DOC and PyRate-doc beside '
              '%s were tried), so the live-tree counts are not asserted here; the fixture '
              'proof above carries the non-vacuity claim, and audit_sources.py without '
              '--corpus still FAILs rather than pass an unread corpus' % (CORPUS, ROOT))
    if good:
        print('self-test: %d checks run' % checks[0])
        print('audit_sources.py self-test PASSED (%d checks, 0 failures)' % checks[0])
        return 0
    print('audit_sources.py self-test FAILED (%d checks run)' % checks[0])
    return 1


if '--self-test' in sys.argv or '-t' in sys.argv:
    sys.exit(self_test())

if '--help' in sys.argv or '-h' in sys.argv:
    print(__doc__)
    sys.exit(0)

_unknown, _skip = [], False
for _a in sys.argv[1:]:
    if _skip:                       # the value of --corpus is not an option
        _skip = False
        continue
    if _a == '--corpus':
        _skip = True
        continue
    if _a.startswith('--corpus=') or _a in ('--verbose', '-v'):
        continue
    _unknown.append(_a)
if _unknown:
    sys.exit('audit_sources.py: unknown argument %r (see --help)' % _unknown[0])

if __name__ == '__main__':
    sys.exit(main())
