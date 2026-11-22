License and provenance of this skills suite
===========================================

This directory (`PyRate-skills/`) is a derived work: an agent-authored skills suite
built from the PyRate documentation corpus. It is not part of the PyRate program
itself and it ships no PyRate source code.

Upstream
--------

PyRate is written by D. Silvestro and collaborators and is hosted at
https://github.com/dsilvestro/PyRate. The corpus states, in its own words
(`PyRate-wiki/Home.md:16`, mirrored at `pyrate/references/home.md`):

    PyRate is licensed under a [AGPLv3 License]
    (https://tldrlegal.com/license/gnu-affero-general-public-license-v3-(agpl-3.0)#summary).

The full text of the GNU Affero General Public License v3 is available from
https://www.gnu.org/licenses/agpl-3.0.html. Because the documentation is
AGPLv3-licensed and this suite reproduces it verbatim, this suite is distributed
under the same license.

Sources actually used
---------------------

The suite mirrors 30 files, and nothing else was used as text:

  `PyRate-wiki/`   git remote https://github.com/dsilvestro/PyRate.wiki.git
                   HEAD abebf92d20d9200647153847bc1bece14f4fb848  (2024-09-02)
                   Home.md, 1.-Preparing-input-file.md, 2.-PyRate:-command-list.md,
                   3.-Summarize-PyRate-results.md, 4.-PyRateContinuous.md,
                   5.-Dispersal-Extinction-Sampling-model.md

  `PyRate-tutorials/tutorials/`
                   git remote https://github.com/dsilvestro/PyRate.git
                   HEAD 6b804abb4a66807f4b2bae3dbee512eab86737b6  (2026-11-11)
                   README.md, pyrate_tutorial_0..6.md, pyrate_tutorial_bdnn.md

Every mirrored page carries its own upstream URL in the YAML frontmatter of the
file under `<skill>/references/`.

The corpus is not a pristine clone: `git status` reports local changes, and they are
all of one kind. Every modified line in both checkouts replaces a remote image URL
with a local `assets/` path (18 lines in `PyRate-tutorials`, 2 in `PyRate-wiki`), and
`assets/` is itself untracked. No English sentence of the documentation was altered,
which was checked by filtering the diffs for changed lines that are not image paths -
that filter returns nothing. The 15 image files (14 unique names; `PyRate_logo1024.png`
exists in both checkouts) are the ones copied to `assets/images/`.

Attribution of the Chinese pages
--------------------------------

The corpus contains 15 English pages and 15 Simplified-Chinese pages. The `-cn`
files are **untracked in the upstream git checkouts** - `git ls-files` matches zero
`*cn.md`, and `git status` reports all 15 as local additions - so they are local
translations supplied alongside the corpus, not upstream content. Their fidelity to
the English was verified mechanically (heading sets, command-heading sets, code
flags, numeric defaults, line counts) rather than assumed. Where the English and
Chinese agree, this suite cites both; where a claim exists only in one language, the
citation says so.

What this suite adds, and its status
------------------------------------

1. `SKILL.md` files (14, English). Original prose written for this suite by
   authoring agents, every factual claim cited to a `<skill>/references/<file>.md`
   line number. `scripts/audit_citations.py` checks the citations mechanically.

2. `<skill>/references/*.md` (50 files). Verbatim mirrors of the 30 corpus pages,
   each with a YAML frontmatter block and with `assets/` image paths re-pointed at
   `../../assets/images/`. No other edit. `scripts/audit_corpus.py` re-derives the
   mirrors from the corpus and compares bytes, so drift is detected.

3. `assets/images/*.png` (14). Copied byte-for-byte from the corpus image sets.

4. `assets/files/*` (77 fixtures + `README.md`). Format and command-line examples.
   **Read `assets/files/README.md` before trusting any of them**: PyRate's upstream
   `example_files/` datasets are referenced by the documentation but are not
   included here and were never readable during authoring, so fixtures whose values
   are not printed in the documentation are labelled SYNTHETIC.

5. `scripts/*.py`. Original tooling for this suite (standard library only, no
   runtime dependency on PyRate).

No warranty
-----------

PyRate's documentation contains internal contradictions that this suite records
rather than resolves — most prominently the required Python version, where
`Home.md` states "Python 3.x is currently not supported" while
`pyrate_tutorial_0.md` requires "Python (v.3.10 or higher)". Each contradiction is
presented with both citations and labelled as documented, inferred, or unresolved.
Treat the suite as a faithful index to the documentation, not as an authority above
it, and verify behaviour against the program you actually have.
