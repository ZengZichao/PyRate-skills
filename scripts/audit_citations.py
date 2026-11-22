#!/usr/bin/env python3
"""Anti-hallucination gate for the PyRate skills suite.

Every SKILL.md line in this suite cites the local doc mirrors as
`references/<file>.md`:LINE and supports its claims with quotations. This script
checks both mechanically:

  STRUCTURE  the cited mirror exists and the cited line number is in range
  EVIDENCE   each natural-language quotation on a citing line occurs verbatim in
             the mirrored corpus (elisions marked with ... or … are matched part
             by part); a quote found in the corpus but not at the cited line is
             reported SOFT (stale pointer), a quote found nowhere is FABRICATED

A pointer may sit before its quotation (`references/x.md`:442), after it on the same line
(`(line 442)`, `(lines 440-462)`, `(:191)`, `(same:53)`, `same:69`), or in the last cell of
the table row that carries it (`| 381 |`). All of these are read, and `lines A-B` / `:A-B`
means the whole interval A..B, not just A. Reading a pointer does not soften the evidence
test: a post-position pointer is only credited to the quotation it directly follows, and a
quotation is VERBATIM only if it is verbatim inside the line or interval that pointer names.

Exit 0 requires zero FILE-MISSING, zero LINE-OOB and zero FABRICATED.

--self-test asserts this script's own parsing invariants on synthetic strings (no suite
file is read, so it passes on an empty tree and fails if a parser is edited blunt).

Usage: python3 scripts/audit_citations.py [--verbose] [--self-test]
"""
import os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERBOSE = '--verbose' in sys.argv

# The sentence a suite-authored references/ page must use about itself; audit_sources.py
# admits such a page as a second class beside a corpus mirror, so this gate has to know which
# pages are prose an agent wrote (and therefore worth citation-checking) and which are mirrors.
AUTHORED_MARKER = '**This file is not a mirror.**'

CITE = re.compile(r'(?:\.\./(?P<skill>[a-z0-9-]+)/)?references/(?P<file>[A-Za-z0-9._-]+\.md)'
                  r'`?\s*(?::\s*|lines?\s+|line\s+)?(?P<l1>\d+)?'
                  r'(?:\s*(?:,|and|-|–|to)\s*(?:lines?\s+|line\s+)?\d+)*')
QUOTE = re.compile(r'["“]([^"“”]{20,300})["”]')

DASH = r'(?:-|–|\bto\b)'
# `(line 442)`, `(lines 440-462)`, `line 126`, `(same:53)`, `same:69`, `(same file:10)`.
# A comma list contributes only its first entry: `lines 297, 352` is not one interval, and
# this gate does not guess at spellings it has not been told to read.
KW_PTR = re.compile(r'\b(?P<kw>lines?|same(?:\s+file)?)\s*:?\s*(?P<a>\d+)'
                    r'(?:\s*' + DASH + r'\s*(?P<b>\d+))?', re.I)
# bare restatements -- `(:191)`, `` `:239` ``, `and :64` -- inherit the file just cited
BARE_PTR = re.compile(r'`?:(\d+)(?:\s*' + DASH + r'\s*(\d+))?`?')
# a table row whose last cell is nothing but a number: `... | 381 |`
CELL_PTR = re.compile(r'\|\s*(?P<a>\d{1,4})\s*\|')

CURLY = {'‘': "'", '’': "'", '“': '"', '”': '"', '–': '-', '—': '-', '…': '...'}

def strip_md(s):
    """`[text](url)` -> `text`; drop images and residue."""
    s = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', s)
    s = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', s)
    return s

def norm(s):
    for k, v in CURLY.items():
        s = s.replace(k, v)
    s = strip_md(s)
    s = re.sub(r'[*_`#|]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip().lower()

def looks_prose(q):
    """Evidence quotations, not shell snippets, grep patterns or code."""
    n = norm(q)
    if '\\' in q or '{' in q or '```' in q:
        return False
    if len(n.split()) < 5:
        return False
    if not re.search(r'[a-z]{3} [a-z]{3}', n):
        return False
    if re.match(r'^(grep|python|awk|sed|ls |cd |find |sort |no match|section)', n):
        return False
    return True

def rng(a, b=None):
    """A pointer's (first, last); a lone number is its own interval."""
    a = int(a)
    b = int(b) if b not in (None, '') else a
    return (a, b) if a <= b else (b, a)


def cite_probe(m):
    """(skill, file, (first, last)) for a CITE match.

    `l1` plus a dash interval written right after it, so `x.md`:29-34 claims the range 29-34.
    A comma list (`x.md`:13, 19, 26) still contributes only its first entry -- reading the rest
    would mean inventing a spelling this gate has not been asked to accept.
    """
    off = m.span('l1')[1] - m.start()
    mm = re.match(r'\s*' + DASH + r'\s*(\d+)', m.group(0)[off:])
    return (m.group('skill'), m.group('file'), rng(m.group('l1'), mm and mm.group(1)))


def file_before(cites, pos):
    """The mirror named last before `pos` on this line, or None -- `(line N)` means "just cited"."""
    out = None
    for m in cites:
        if m.start() < pos:
            out = (m.group('skill'), m.group('file'))
    return out


def post_pointers(line, cites, qspans, prev_file):
    """{(quote_start, quote_end): (skill, file, (first, last))} for pointers written AFTER a quote.

    Attribution stays strict. A pointer takes the file named before it on its own line, falling
    back to the last file cited earlier in the document (`(line 442)` in a section that has been
    quoting one page for ten lines has no other referent, and the verbatim test still binds).
    A table cell `| 381 |` is only read at all when one single mirror is named in that row. And
    a pointer is credited to a quotation only when the two are mutual neighbours: it is the first
    pointer after the quotation and the quotation is the last one before it. Stack two quotations
    against two pointers and at most one pair forms -- the rest is reported STALE, not guessed.
    """
    toks = []
    for m in KW_PTR.finditer(line):
        f = file_before(cites, m.start()) or prev_file
        if f:
            toks.append((m.start(), m.end(), (f[0], f[1], rng(m.group('a'), m.group('b')))))
    for m in BARE_PTR.finditer(line):
        if any(s <= m.start() and m.end() <= e for s, e, _ in toks):
            continue                                   # the number already read as `same:53`
        f = file_before(cites, m.start()) or prev_file
        if f:
            toks.append((m.start(), m.end(), (f[0], f[1], rng(m.group(1), m.group(2)))))
    if line.lstrip().startswith('|'):
        named = {(m.group('skill'), m.group('file')) for m in cites}
        if len(named) == 1:
            f = named.pop()
            for m in CELL_PTR.finditer(line):
                toks.append((m.start(), m.end(), (f[0], f[1], rng(m.group('a')))))
    # a number inside a quotation is quoted text (a manual's own "(line 12)"), not a pointer
    toks = [t for t in toks if not any(s <= t[0] and t[1] <= e for s, e in qspans)]
    toks.sort()
    pairs = {}
    for st, _en, probe in toks:
        before = [q for q in qspans if q[1] <= st]
        if not before:
            continue
        q = max(before, key=lambda x: x[1])
        if min([t[0] for t in toks if t[0] >= q[1]]) != st:
            continue                                   # another pointer claims this quotation first
        pairs[q] = probe
    return pairs


def at_pointer(probe, parts, resolve):
    """Is the quotation verbatim inside the line / interval the pointer claims for it?

    A single line number keeps the window this gate has always used (the line, two above, four
    below); an interval is read as exactly the lines the pointer claims, no more. Same norm() as
    everywhere else -- no second, gentler comparison exists here.
    """
    skl, f, (a, b) = probe
    s = resolve((skl, f))
    if not s:
        return False
    w = norm(' '.join(s[max(0, a - 2):a + 4])) if a == b else norm(' '.join(s[max(0, a - 1):b]))
    return any(p in w for p in parts)


def quote_verdicts(line, cites, corpus, resolve, prev_file):
    """Classify every quotation on one suite line: VERBATIM / STALE / NEARLINE / FABRICATED.

    VERBATIM means the wording is verbatim *at a line or interval this line points at*; STALE
    means the wording is real but no pointer on the line reaches it. Pointers placed before the
    quotation are read as they always were, and the post-position pointers of post_pointers() are
    added only for the quotation they pair with.
    """
    quotes = list(QUOTE.finditer(line))
    qspans = [(m.start(), m.end()) for m in quotes]
    pre = [cite_probe(m) for m in cites if m.group('l1')]
    last_file = next(((m.group('skill'), m.group('file')) for m in reversed(cites) if m.group('l1')),
                     None)
    bare = [(m.start(), rng(m.group(1), m.group(2))) for m in BARE_PTR.finditer(line)]
    post = post_pointers(line, cites, qspans, prev_file)
    out = []
    for qm in quotes:
        q = qm.group(1)
        if not looks_prose(q):
            continue
        nq = norm(q)
        parts = [p.strip() for p in nq.split('...') if len(p.strip()) >= 10] or [nq]
        if not all(p in corpus for p in parts):
            out.append((q, 'NEARLINE' if any(t in corpus for t in nq.split(' ') if len(t) > 8)
                       else 'FABRICATED'))
            continue
        probes = list(pre)
        probes += [(last_file[0], last_file[1], rg) for st, rg in bare if st < qm.start() and last_file]
        p = post.get((qm.start(), qm.end()))
        if p:
            probes.append(p)
        out.append((q, 'VERBATIM' if any(at_pointer(pb, parts, resolve) for pb in probes)
                    else 'STALE'))
    return out


def main():
    mirrors = {}
    for p in sorted(glob.glob(os.path.join(ROOT, '*', 'references', '*.md'))):
        mirrors[p] = norm(open(p, encoding='utf-8').read())
    if not mirrors:
        print('no mirrors found under */references/*.md')
        return 1
    corpus = ' ||| '.join(mirrors.values())

    skills = [d for d in sorted(glob.glob(os.path.join(ROOT, '*')))
              if os.path.isdir(d) and os.path.exists(os.path.join(d, 'SKILL.md'))]
    missing = [os.path.basename(d) for d in sorted(glob.glob(os.path.join(ROOT, '*')))
               if os.path.isdir(d) and not os.path.exists(os.path.join(d, 'SKILL.md'))
               and os.path.basename(d) not in ('scripts', 'assets')]

    # SKILL.md is not the only suite-authored prose in the tree. A references/ page that
    # declares itself "not a mirror" carries citations and quotations of its own, and until now
    # nothing checked them: the mirrors need no citation check because audit_sources.py compares
    # them to the corpus byte for byte, but an authored page is prose an agent wrote, so it is
    # exactly the kind of file that can cite a line it never read. Each is judged from the anchor
    # directory of the skill that holds it, so `references/x.md`:51 means the same thing there as
    # it does in that skill's SKILL.md.
    docs = []
    for sk in skills:
        docs.append((os.path.basename(sk), sk, os.path.join(sk, 'SKILL.md')))
        for a in sorted(glob.glob(os.path.join(sk, 'references', '*.md'))):
            if AUTHORED_MARKER in open(a, encoding='utf-8', errors='replace').read()[:2000]:
                docs.append(('%s/references/%s' % (os.path.basename(sk), os.path.basename(a)),
                             sk, a))

    n_cites = 0
    tot = {'VERBATIM': 0, 'NEARLINE': 0, 'STALE': 0, 'FABRICATED': 0}
    miss_files = miss_lines = 0
    rows = []

    for name, sk, path in docs:
        lines = open(path, encoding='utf-8').read().split('\n')
        c = dict.fromkeys(tot, 0)
        mf = ml = 0
        nc = 0
        prev_file = None
        cache = {}

        def resolve(key, sk=sk, cache=cache):
            """The lines of a mirror named on this page, or None; each file is read once."""
            skl, f = key
            p = os.path.join(sk, 'references', f)
            if not os.path.exists(p) and skl:
                p = os.path.join(ROOT, skl, 'references', f)
            if not os.path.exists(p):
                return None
            if p not in cache:
                cache[p] = open(p, encoding='utf-8').read().split('\n')
            return cache[p]
        for lineno, line in enumerate(lines, 1):
            cites = list(CITE.finditer(line))
            if not cites:
                continue
            for m in cites:
                nc += 1
                f = m.group('file')
                cand = os.path.join(sk, 'references', f)
                if not os.path.exists(cand) and m.group('skill'):
                    cand = os.path.join(ROOT, m.group('skill'), 'references', f)
                if not os.path.exists(cand):
                    print('FILE-MISSING  %s:%d references/%s' % (name, lineno, f))
                    mf += 1
                    continue
                src = open(cand, encoding='utf-8').read().split('\n')
                if m.group('l1') and int(m.group('l1')) > len(src):
                    print('LINE-OOB      %s:%d references/%s (%d lines, cited %s)'
                          % (name, lineno, f, len(src), m.group('l1')))
                    ml += 1
            for q, verdict in quote_verdicts(line, cites, corpus, resolve, prev_file):
                if verdict == 'NEARLINE':
                    c['NEARLINE'] += 1
                    if VERBOSE:
                        print('NEAR/PARAPHRASE %s:%d %r' % (name, lineno, q[:80]))
                elif verdict == 'FABRICATED':
                    c['FABRICATED'] += 1
                    print('FABRICATED  %s:%d %r' % (name, lineno, q[:140]))
                else:
                    c[verdict] += 1
                    if verdict == 'STALE' and VERBOSE:
                        print('STALE LINE    %s:%d %r' % (name, lineno, q[:80]))
            prev_file = (cites[-1].group('skill'), cites[-1].group('file'))
        for k in tot:
            tot[k] += c[k]
        n_cites += nc
        miss_files += mf
        miss_lines += ml
        rows.append((name, nc, c['VERBATIM'], c['STALE'], c['NEARLINE'], c['FABRICATED'], mf, ml))

    print()
    print('%-30s %6s %9s %6s %8s %11s %5s %4s' %
          ('SKILL', 'cites', 'VERBATIM', 'STALE', 'PARAPHR', 'FABRICATED', 'miss', 'oob'))
    for r in rows:
        print('%-30s %6d %9d %6d %8d %11d %5d %4d' % r)
    if missing:
        print('\nSKILLS WITHOUT SKILL.md: ' + ', '.join(missing))
    print('\ncitations: %d   quotations: %d' % (n_cites, sum(tot.values())))
    print('VERBATIM at/near cited line: %d' % tot['VERBATIM'])
    print('VERBATIM elsewhere in mirror (stale pointer): %d' % tot['STALE'])
    print('PARAPHRASE (real wording, not quoted): %d' % tot['NEARLINE'])
    print('FABRICATED: %d' % tot['FABRICATED'])
    print('FILE-MISSING: %d   LINE-OOB: %d' % (miss_files, miss_lines))
    hard = tot['FABRICATED'] + miss_files + miss_lines
    print('\nRESULT: %s' % ('PASS' if hard == 0 else 'FAIL (%d hard problems)' % hard))
    return 1 if hard else 0

def self_test():
    """Prove this script's own parsers on synthetic input -- no suite files read.

    The gate is only worth anything if a citation is found where the contract writes
    one, and if a grep pattern is never mistaken for a quotation. Both are asserted
    here against strings this function carries, so the test cannot be passed by an
    empty tree, and needs nothing but the standard library.
    """
    run, bad = [0], []

    def ok(cond, msg):
        run[0] += 1
        if not cond:
            bad.append(msg)

    # the citation shape the contract mandates, in all four spellings authors use
    hits = [(m.group('skill'), m.group('file'), m.group('l1'))
            for m in CITE.finditer('see `references/command-list.md`:120 for the flag')]
    ok(hits == [(None, 'command-list.md', '120')], 'plain cite parsed: %s' % hits)
    hits = [(m.group('skill'), m.group('file'), m.group('l1'))
            for m in CITE.finditer('per ../pyrate/references/home.md:9 and :14')]
    ok(hits == [('pyrate', 'home.md', '9')], 'cross-skill cite parsed: %s' % hits)
    ok(list(CITE.finditer('the ratio 3:40 is not a cite')) == [], 'a ratio is not a cite')
    ok([(m.group('file'), m.group('l1'))
        for m in CITE.finditer('references/tutorial-1.md lines 30-31')]
       == [('tutorial-1.md', '30')], 'a wordled line range still names its mirror')

    # quotations: long enough to be evidence, and paired
    q = QUOTE.findall('the docs say "the gamma model strongly outperforms constant '
                      'rates" here and "too short" there')
    ok(q == ['the gamma model strongly outperforms constant rates'], 'quote length window: %s' % q)

    # markup folding: what a mirror prints vs what the SKILL.md quotes
    ok(norm('**Bold** `code` text with a [link](http://x) and “curly”')
       == 'bold code text with a link and "curly"', 'norm folds markup: %r'
       % norm('**Bold** `code` text with a [link](http://x) and “curly”'))
    ok(norm('plain text stays plain') == 'plain text stays plain', 'norm is stable')
    ok(strip_md('![fig](../assets/images/PyRate_logo1024.png) body [t](u) end')
       == ' body t end', 'strip_md drops images')

    # an elided quotation is matched part by part, and each part must be substantial
    parts = [p.strip() for p in norm('the first half of the claim ... the second half'
                                     ' of the claim').split('...') if len(p.strip()) >= 10]
    ok(len(parts) == 2 and all('half' in p for p in parts), 'elision splits: %s' % parts)

    # prose vs code: a grep pattern is never evidence of a quotation
    ok(looks_prose('the gamma model strongly outperforms constant rates') is True,
       'a real sentence is prose')
    for not_prose in ["grep -n 'a\\|b' references/x.md", 'one short',
                      '\\-varD|\\-DivdD|\\-traitD options', '{a: 1} dict of things here',
                      'sort the file and count the lines']:
        ok(looks_prose(not_prose) is False, 'not prose: %r' % not_prose)

    # ---------------------------------------------------------------- pointer spellings
    # Mutation tests for the pointer reader. The fixture is a synthetic mirror whose line i
    # carries a sentence that appears on no other line, so a VERBATIM can only be earned by a
    # pointer that really reaches line i -- and every test below is written so that a blunt
    # recognizer (widen the window, pair by hope, read numbers inside quotations) turns red.
    body = ['mirror line %02d explains preservation rates and fossil occurrences in its own words %02d'
            % (i, i) for i in range(1, 27)]
    body[11] = 'mirror line 12 quotes (line 3) before finishing its own words 12'
    MIRROR = '\n'.join(body)
    MLINES = MIRROR.split('\n')

    def verdict(line, prev=None):
        cites = list(CITE.finditer(line))
        return [v for _q, v in quote_verdicts(line, cites, norm(MIRROR),
                                              lambda key: MLINES if key[1] == 'm.md' else None,
                                              prev)]

    def Q(n):
        return '"%s"' % body[n - 1]

    # anchors whose own window (cited line -2 .. +4) reaches neither of the lines under test,
    # so that a VERBATIM here can only come from the pointer being tested
    FAR = 'the anchor page `references/m.md`:21 says '       # window covers lines 20-26
    NEAR = 'the anchor page `references/m.md`:2 says '       # window covers lines 1-6

    # (i) a pointer written after the quotation is a pointer
    ok(verdict(FAR + Q(3) + ' (line 3)') == ['VERBATIM'],
       'post-position (line N): %s' % verdict(FAR + Q(3) + ' (line 3)'))
    ok(verdict(FAR + Q(4) + ' (same:4)') == ['VERBATIM'], 'post-position (same:N)')
    ok(verdict(FAR + Q(5) + ' (:5)') == ['VERBATIM'], 'post-position bare (:N)')
    ok(verdict('the page says ' + Q(6) + ' (line 6)', prev=('x', 'm.md')) == ['VERBATIM'],
       'a pointer with no file on its line takes the mirror last cited before it')
    ok(verdict('the page says ' + Q(6) + ' (line 6)') == ['STALE'],
       'a line number with no mirror named on the line or before it is not read at all')
    # (ii) ... but only when the number is right: the same spelling, twenty lines off
    ok(verdict(FAR + Q(3) + ' (line 23)') == ['STALE'],
       'a (line N) twenty lines away is not evidence: %s' % verdict(FAR + Q(3) + ' (line 23)'))
    ok(verdict(FAR + Q(4) + ' (same:24)') == ['STALE'], 'a wrong same: is still stale')
    # (iii) an interval reaches its last line and stops there
    ok(verdict(NEAR + Q(20) + ' (lines 10-20)') == ['VERBATIM'], 'a range covers its end line')
    ok(verdict('per `references/m.md`:10-20 the page says ' + Q(20)) == ['VERBATIM'],
       'a range on the cite itself covers its end line')
    ok(verdict(NEAR + Q(21) + ' (lines 10-20)') == ['STALE'],
       'a range is not a window: the line after its end is stale')
    ok(verdict('per `references/m.md`:10-20 the page says ' + Q(21)) == ['STALE'],
       'a cited range does not pad past its own last line')
    ok(verdict('per `references/m.md` 10-20 the page says ' + Q(20)) == ['VERBATIM'],
       'a range written without a colon is still a range')
    ok(verdict('per `references/m.md` 10-20 the page says ' + Q(21)) == ['STALE'],
       'and it stops at its own last line')
    # (iv) two quotations and two post pointers: pairing must be unique, never assumed. Pairing
    # them in order of appearance would call both VERBATIM, which is exactly what is forbidden.
    stacked = verdict(FAR + Q(3) + ' and then ' + Q(4) + ' (line 3) (line 4)')
    ok(stacked.count('VERBATIM') <= 1, 'stacked pointers are not paired by hope: %s' % stacked)
    # one quotation, two pointers: only the first is its pointer, and the second may not rescue
    # a number that failed -- "which did he mean" is not a question the gate gets to answer
    ok(verdict(FAR + Q(3) + ' (line 23) (line 3)') == ['STALE'],
       'a quotation followed by two pointers is judged against the first only')
    ok(verdict(FAR + Q(3) + ' (line 3) while ' + Q(4) + ' (line 4)')
       == ['VERBATIM', 'VERBATIM'], 'interleaved pointers pair uniquely')
    # (v) a table cell is a pointer only when it names the right line, and only when one
    # single mirror is in the row to say what "line" means
    ok(verdict('| `references/m.md`:21 | item | ' + Q(3) + ' | 3 |') == ['VERBATIM'],
       'a table cell of the right line number is read')
    ok(verdict('| `references/m.md`:21 | item | ' + Q(3) + ' | 23 |') == ['STALE'],
       'a table cell of the wrong line number is stale')
    ok(verdict('| `references/m.md`:21 vs `references/other.md`:21 | ' + Q(3) + ' | 3 |')
       == ['STALE'], 'a row naming two mirrors does not get a cell pointer')
    twin = '| `references/m.md`:21 vs `references/other.md`:21 | ' + Q(3) + ' | 3 |'
    ok(not post_pointers(twin, list(CITE.finditer(twin)),
                         [(m.start(), m.end()) for m in QUOTE.finditer(twin)], None),
       'a row naming two mirrors produces no pointer at all')
    # a number inside a quotation is quoted text, never a pointer -- drop the filter and the
    # "(line 3)" the mirror itself prints inside quotation two reaches back and "verifies"
    # quotation one, which nothing on the line points at
    ok(verdict(FAR + Q(3) + ' and also ' + Q(12)) == ['STALE', 'STALE'],
       'a (line N) inside a quotation is not a pointer: %s'
       % verdict(FAR + Q(3) + ' and also ' + Q(12)))
    # spellings this gate deliberately does NOT read yet, pinned so the choice stays visible
    ok(verdict(NEAR + Q(24) + ' (lines 2, 24)') == ['STALE'],
       'a comma list of line numbers is not read as a pointer')
    ok(verdict(FAR + Q(9) + ' (line)') == ['STALE'], 'a keyword with no number points nowhere')
    # the two branches that are not about line numbers at all still work
    ok(verdict(FAR + '"nothing here echoes the mirror wording whatsoever"') == ['FABRICATED'],
       'an invented quotation is still FABRICATED')
    ok(verdict(FAR + '"preservation rates and something else entirely whatsoever"') == ['NEARLINE'],
       'a paraphrase made of mirror words is still NEARLINE')

    print('audit_citations.py self-test: %s (%d checks, %d failure(s))'
          % ('OK' if not bad else 'FAILED', run[0], len(bad)))
    for b in bad:
        print('  SELF-TEST FAIL: %s' % b)
    return 0 if not bad else 1


if __name__ == '__main__':
    if '--self-test' in sys.argv:
        sys.exit(self_test())
    sys.exit(main())
