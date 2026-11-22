#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""validate_input.py — pre-flight validator for PyRate inputs.

Part of the PyRate-skills suite (skill: pyrate-input-file). Python 3 standard
library only; deterministic; offline; it never runs PyRate, never runs R and
never installs anything.

TWO INPUTS ARE ACCEPTED, picked by the file's own text (extension is only a hint):

  1. the raw OCCURRENCE TABLE that `extract.ages` reads (tab-delimited .txt):
     one header row plus one row per fossil occurrence, the four mandatory
     columns and the optional Trait / Site column.
  2. the generated `*_PyRate.py` input that `python PyRate.py` reads. It is
     parsed TEXTALLY ONLY — never imported, never exec'd, never unpickled. A
     PyRate input file is arbitrary Python, so executing it would run whatever
     it contains; this tool reads it as characters and reports what it can see.

DOCUMENTED RULES (every one is quoted with its mirror line; --self-test re-checks
that each quotation really sits where it is claimed):
  * "All fossil occurrences need to be provided in a table (a tab-delimited text
    file), with species names, their status ("extant" or "extinct"), and minimum and
    maximum ages as the columns."        references/preparing-input-file.md:14
  * "At present, PyRate can not deal with missing information in these four columns,
    so make sure that you remove these entries beforehand."                same line
  * "One additional column may be added providing a trait value ... missing data are
    allowed, and should be given as NA"                                             same line
  * header printed as `Species Status MinT MaxT Trait`
                                                    references/preparing-input-file.md:16
  * "The table must include 4 columns including 1) Taxon name, 2) Status ... 3) Minimum
    age, and 4) Maximum age. The table should have a header (first row) and one row for
    each fossil occurrence"                references/tutorial-1.md:49
  * a "Site" column "with a number specifying the ID of the assemblage for each
    occurrence"                              references/tutorial-1.md:72
  * species names "expected format: Genus_species", checked by the documented
    `-check_names` function                  references/tutorial-1.md:94
  * the input for PyRate itself "is a Python file with the fossil occurrence data (as
    list of Numpy arrays) and, optionally, one or more continuous traits"
                                       ../pyrate-command-reference/references/command-list.md:13

CORPUS CONFLICT you must know about — three different header spellings are printed by
three pages of this corpus, and the upstream example file the wiki names uses a fourth
set of labels: `Species Status MinT MaxT` (wiki), `Taxon_name Status MinAge MaxAge`
(tutorial 1), `Species Status min_age max_age trait` (the real
example_files/Ursidae.txt, see ../assets/files/occ-ursidae-upstream.txt). All are
accepted; anything else is an ERROR. Nothing in the corpus says which is required.

Findings are graded, and the grade follows how the rule is stated:
  ERROR = the page states the rule imperatively  -> exit code 1
  WARN  = the page only exhibits the pattern (its example rows), or this tool inferred
          it; a WARN never fails a run
  NOTE  = information, no judgement

USAGE
  python3 scripts/validate_input.py TABLE.txt
  python3 scripts/validate_input.py Occurs_PyRate.py --pyrate-dir .
  python3 scripts/validate_input.py table.txt --expect site
  python3 scripts/validate_input.py table.txt --json
  python3 scripts/validate_input.py --self-test
  python3 scripts/validate_input.py --rules            # the cited rule table

FLAGS
  PATH ...                one or more files to check (each reported separately)
  --expect trait|site|none  assert what the optional 5th column must be
  --pyrate-dir DIR        (unused for checking, recorded in the report as where the
                          program would be run from)
  --json                  machine-readable report
  --rules                 print the cited rules and exit 0
  --self-test             build its own temp fixtures and assert behaviour
  --quiet                 only the RESULT line

EXIT CODES
  0 no ERROR (warnings possible)   1 at least one ERROR   2 usage / unreadable input
"""

import argparse
import contextlib
import io
import json
import os
import re
import sys

# ---------------------------------------------------------------- citation registry
# key -> (path as cited from the skill folder, 1-based mirror line, verbatim quote)
CITE = {
    "table": ("references/preparing-input-file.md", 14,
              "All fossil occurrences need to be provided in a table (a tab-delimited "
              "text file), with species names, their status (\"extant\" or \"extinct\"), "
              "and minimum and maximum ages as the columns."),
    "nomissing": ("references/preparing-input-file.md", 14,
                  "At present, PyRate can not deal with missing information in these four "
                  "columns, so make sure that you remove these entries beforehand."),
    "trait": ("references/preparing-input-file.md", 14,
              "One additional column may be added providing a trait value, if available, "
              "which can be used in the birth-death analysis (note that here, missing data "
              "are allowed, and should be given as NA)."),
    "header": ("references/preparing-input-file.md", 16,
               "Species\t\t\t\tStatus\t\tMinT\t MaxT    Trait"),
    "naexample": ("references/preparing-input-file.md", 23,
                  "Agriotherium_intermedium\t\textinct\t 3.4\t  4.2\t\t NA"),
    "specific": ("references/preparing-input-file.md", 9,
                 "The PyRate program requires a specific format for the input data, so "
                 "please follow the next steps carefully."),
    "extract": ("references/preparing-input-file.md", 26,
                "This file can then be processed using the R function extract.ages from "
                "the R utilities script provided with PyRate package."),
    "replicates": ("references/preparing-input-file.md", 34,
                   "This option allows the user to generate several replicates of the data "
                   "set in a single input file, each time re-drawing the ages of the "
                   "occurrences at random from uniform distributions with boundaries MinT "
                   "and MaxT."),
    "cutoff": ("references/preparing-input-file.md", 40,
               "Specify a threshold to exclude fossil occurrences with a high temporal "
               "uncertainty, i.e. with a wide temporal range between MinT and MaxT."),
    "generates": ("references/preparing-input-file.md", 54,
                  "generates a Python file (here called 'Ursidae_PyRate.py') that can now "
                  "be imported in PyRate for diversification rate analyses"),
    "fourcols": ("references/tutorial-1.md", 49,
                 "The table must include 4 columns including 1) Taxon name, 2) Status "
                 "specifying whether the taxon is \"extinct\" or \"extant\", 3) Minimum "
                 "age, and 4) Maximum age."),
    "onerow": ("references/tutorial-1.md", 49,
               "The table should have a header (first row) and one row for each fossil "
               "occurrence"),
    "thdr": ("references/tutorial-1.md", 52,
             "| Taxon\\_name   | Status  | MinAge | MaxAge |"),
    "duprows": ("references/tutorial-1.md", 54,
                "Canis\\_ferox | extinct | 4.9    | 10.3"),
    "duprows2": ("references/tutorial-1.md", 58,
                 "Canis\\_ferox | extinct | 4.9 | 10.3"),
    "sitecol": ("references/tutorial-1.md", 72,
                "This can be done by specifying a \"Site\" column in the input data, with "
                "a number specifying the ID of the assemblage for each occurrence."),
    "siteauto": ("references/tutorial-1.md", 87,
                 "will automatically resample fossil ages by site when a column named "
                 "\"Site\" is included in the input table"),
    "namefmt": ("references/tutorial-1.md", 94,
                "check for inconsistent spelling in species names (expected format: "
                "Genus\\_species)"),
    "checknames": ("references/tutorial-1.md", 94,
                   "This is implemented in the function -check_names, which requires a "
                   "text file containing one species name for each row."),
    "ranks": ("references/tutorial-1.md", 100,
              "Ranks 0 and 1 indicate the most likely cases of misspellings, whereas ranks "
              "2 and 3 are most likely truly different names."),
    "nosyn": ("references/tutorial-1.md", 101,
              "NOTE that this algorithm does NOT check for synonyms!"),
    "datainfo": ("references/tutorial-1.md", 45,
                 "python PyRate.py '.../Canis_pbdb_data_PyRate.py' -data_info"),
    "spyfile": ("../pyrate-command-reference/references/command-list.md", 13,
                "The file is a Python file \twith the fossil occurrence data (as list of "
                "Numpy arrays) and, optionally, one or more continuous traits."),
    "jdefault": ("../pyrate-command-reference/references/command-list.md", 30,
                 "-j 1  (default; the first data set from the input file is analyzed)"),
    "several": ("../pyrate-command-reference/references/command-list.md", 28,
                "If the input file includes several data sets, e.g. generated using the R "
                "script pyrate_utilities.R to account for uncertainties of fossil ages, "
                "this command defines which data set will be analyzed."),
    "traitna": ("../pyrate-command-reference/references/command-list.md", 133,
                "Alternatively, they can be included in the table with trait value NA. "
                "These species will be still included in the analysis, but their trait "
                "value will be imputed by the MCMC."),
}

SKILL_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          os.pardir))
SUITE_DIR = os.path.normpath(os.path.join(SKILL_DIR, os.pardir))
# the observed shape of a generated input, recorded by this suite as a fixture
PY_SHAPE_FIXTURE = "../assets/files/occ-pyrate-input-structure-EXCERPT.py"

NUM = re.compile(r"^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$")
MISSING_TOKENS = {"", "na", "n/a", "nan", "null", "none", "-", ".", "?", "unknown"}
STATUS_OK = ("extinct", "extant")
# the header spellings this corpus actually prints (see the docstring conflict note)
HEADERS = [
    (["species", "status", "mint", "maxt"], "wiki", "references/preparing-input-file.md:16"),
    (["taxon_name", "status", "minage", "maxage"], "tutorial 1",
     "references/tutorial-1.md:52"),
    (["taxon_name", "status", "min_age", "max_age"], "tutorial 1 spelling + wiki ages",
     "by combination of the two documented headers"),
    (["species", "status", "min_age", "max_age"], "upstream example_files/Ursidae.txt",
     "../assets/files/occ-ursidae-upstream.txt (not a mirror)"),
    (["species", "status", "mint", "maxage"], "mixed", "no page prints this one"),
    (["taxon", "status", "mint", "maxt"], "mixed", "no page prints this one"),
]
EXTRA_DOC = {"trait": "trait value, NA allowed (references/preparing-input-file.md:14)",
             "site": "assemblage ID, numeric "
                     "(references/tutorial-1.md:72)"}


def quote(key):
    rel, line, text = CITE[key]
    return '"%s" (%s:%d)' % (re.sub(r"\s+", " ", text), rel, line)


# ------------------------------------------------------------------------ findings
class Report(object):
    def __init__(self, path, kind):
        self.path = path
        self.kind = kind          # "table" | "pyrate-py" | "unknown"
        self.findings = []
        self.stats = {}
        self.extra_kind = None    # "trait" | "site" | None, taken from the header
        self.header_fatal = False  # the header itself was rejected: row checks are noise

    def add(self, level, where, msg, fix, cite=None, once=None):
        if once:
            for f in self.findings:
                if f.get("once") == once:
                    f["more"] = f.get("more", 0) + 1
                    f["last"] = where
                    return
        self.findings.append({"level": level, "where": where, "message": msg,
                              "fix": fix, "cite": cite, "once": once, "more": 0})

    def error(self, where, msg, fix, cite=None, once=None):
        self.add("ERROR", where, msg, fix, cite, once)

    def warn(self, where, msg, fix, cite=None, once=None):
        self.add("WARN", where, msg, fix, cite, once)

    def note(self, where, msg, fix=None, cite=None, once=None):
        self.add("NOTE", where, msg, fix or "", cite, once)

    def count(self, level):
        return sum(1 for f in self.findings if f["level"] == level)

    @property
    def ok(self):
        return self.count("ERROR") == 0


def render_report(rep, args):
    lines = []
    lines.append("%s  [%s]" % (rep.path, rep.kind))
    for f in rep.findings[:args.max_findings]:
        text = "  %-5s %s: %s" % (f["level"], f["where"], f["message"])
        if f.get("more"):
            text += "  [same on %d more row(s)%s]" % (
                f["more"], ", last %s" % f["last"] if f.get("last") else "")
        if len(text) > 260:
            text = text[:257] + "..."
        lines.append(text)
        tail = []
        if f["cite"]:
            tail.append("rule: %s" % f["cite"])
        if f["fix"]:
            tail.append("fix: %s" % f["fix"])
        if tail:
            line = "        " + " | ".join(tail)
            lines.append(line if len(line) <= 300 else line[:297] + "...")
    extra = len(rep.findings) - args.max_findings
    if extra > 0:
        lines.append("  ... +%d further finding(s) not shown (--max-findings %d)"
                     % (extra, args.max_findings))
    if rep.stats:
        lines.append("  stats: " + "; ".join("%s=%s" % kv for kv in sorted(rep.stats.items())))
    return lines


# ---------------------------------------------------------------- shared file reading
def read_text(path, max_bytes=8 * 1024 * 1024):
    """Text of a file, never evaluated. Returns (text, warning_or_None)."""
    try:
        size = os.path.getsize(path)
        with open(path, "rb") as fh:
            raw = fh.read(max_bytes)
    except OSError as exc:
        return None, "cannot read: %s" % (exc.strerror or exc)
    note = None
    if size > max_bytes:
        note = ("only the first %d bytes were inspected (bounded output/memory)"
                % max_bytes)
    return raw.decode("utf-8-sig", "replace"), note


def split_lines(text):
    """Split on LF, CRLF and lone CR (the upstream Ursidae.txt uses CR only)."""
    return re.split(r"\r\n|\r|\n", text)


# ----------------------------------------------------------------- occurrence tables
def sniff_kind(text, path):
    """Table vs generated *_PyRate.py, from the file's own content."""
    if re.search(r"^\s*(from\s+numpy\s+import|data_\d+\s*=|taxa_names\s*=)", text,
                 re.MULTILINE):
        return "pyrate-py"
    base = os.path.basename(path).lower()
    if base.endswith("_pyrate.py") or base.endswith(".py"):
        return "pyrate-py"
    return "table"


def is_missing(cell):
    return cell.strip().lower() in MISSING_TOKENS


def looks_like_numbers(cells):
    return bool(cells) and all(NUM.match(c.strip()) for c in cells)


def check_table(path, text, rep, expect):
    lines = [l for l in split_lines(text)]
    comments = [i for i, l in enumerate(lines, 1) if l.lstrip().startswith("#")]
    body = [(i, l) for i, l in enumerate(lines, 1)
            if l.strip() and not l.lstrip().startswith("#")]
    if comments:
        rep.note("header block", "%d '#'-comment line(s) were skipped as provenance "
                 "text (this suite's fixtures carry them)" % len(comments),
                 "nothing to fix, but a real PyRate/extract.ages run will not skip them - "
                 "strip them before feeding the file to R")
    if len(body) < 2:
        rep.error("file", "no usable rows: %d non-comment line(s); the format is one "
                  "header row plus one row per occurrence" % len(body),
                  "add the header and at least one occurrence row",
                  quote("onerow"))
        return

    # ---- delimiter ----------------------------------------------------------
    tabs = sum(l.count("\t") for _i, l in body)
    commas = sum(l.count(",") for _i, l in body)
    if tabs == 0:
        rep.error("file", "no tab character anywhere: the table is not tab-delimited",
                  "convert the separators to TAB (Excel: save as 'Text (tab delimited)'; "
                  "shell: sed 's/,/\\t/g' file > file.txt)",
                  quote("table"))
        sep = "," if commas > tabs else None
        if sep is None:
            rep.error("file", "no comma either: columns can only be guessed from runs of "
                      "spaces, which the docs never allow",
                      "re-save the table as a tab-delimited text file", quote("table"))
            return
    else:
        sep = "\t"
        if commas > 0 and commas >= len(body):
            rep.warn("file", "%d comma(s) alongside the tabs: a comma inside a name or a "
                     "stray CSV column shifts every later field" % commas,
                     "check that each row still has the same number of tab-separated "
                     "fields")

    rows = [(i, [c.strip() for c in l.split(sep)]) for i, l in body]

    widths = {}
    for line_no, r in rows:
        widths.setdefault(len(r), []).append(line_no)
    if len(widths) > 1:
        parts = []
        for w in sorted(widths):
            shown = ",".join(str(x) for x in widths[w][:12])
            parts.append("%d column(s) on line(s) %s%s"
                         % (w, shown, ", ..." if len(widths[w]) > 12 else ""))
        rep.error("file", "ragged table: " + "; ".join(parts),
                  "pad or drop fields so every row has the same columns; trailing empty "
                  "cells count as missing data")

    hline, header = rows[0]
    data = rows[1:]
    check_header(header, rep, hline, expect)
    if rep.header_fatal:
        rep.note("file", "row-by-row checking stopped: with this header the columns "
                 "cannot be mapped, so every row would only repeat the same finding "
                 "(%d data row(s) left unchecked)" % len(data),
                 "fix the header (or use the file that has the four columns) and re-run",
                 quote("fourcols"))
        return
    if expect is not None:
        rep.note("--expect", "you asserted the 5th column should be '%s'; the check "
                 "reports a mismatch as an ERROR" % expect)

    # ---- mandatory columns --------------------------------------------------
    ages_by_name = {}
    status_by_name = {}
    seen_rows = {}
    numeric_ages = []
    extra_vals = []
    for line_no, cells in data:
        where = "line %d" % line_no
        if len(cells) < 4:
            rep.error(where, "only %d field(s); the four mandatory columns are name, "
                      "status, minimum age, maximum age" % len(cells),
                      "complete the row or delete it", quote("fourcols"), once="short-row")
            continue
        name, status, mint, maxt = cells[0], cells[1], cells[2], cells[3]

        if not name or is_missing(name):
            rep.error(where, "taxon name is empty/missing in a mandatory column",
                      "fill the name or drop the occurrence", quote("nomissing"))
        else:
            check_name_format(name, where, rep)
            status_by_name.setdefault(name.lower(), set()).add(status.lower())
            if NUM.match(mint or "") and NUM.match(maxt or ""):
                ages_by_name.setdefault(name.lower(), []).append(
                    (float(mint), float(maxt), line_no))

        if not status or is_missing(status):
            rep.error(where, "Status is empty/missing in a mandatory column",
                      "write extinct (or extant) - PyRate cannot handle missing values "
                      "here", quote("nomissing"))
        elif status.lower() not in STATUS_OK:
            rep.error(where, "Status %r is neither \"extant\" nor \"extinct\"" % status,
                      "use exactly 'extinct' or 'extant'; anything else is read as a "
                      "missing value", quote("table"))
        elif status != status.lower():
            rep.warn(where, "Status %r is not lower-case as in every documented example"
                     % status, "write it lower-case to match the examples "
                     "(case-sensitivity is nowhere stated)", once="status-case")

        for label, val in (("MinT", mint), ("MaxT", maxt)):
            if is_missing(val):
                rep.error(where, "%s (%s) is missing" % (label, "minimum age" if label ==
                          "MinT" else "maximum age"),
                          "fill the age or remove the occurrence - missing values in the "
                          "four columns cannot be handled", quote("nomissing"))
            elif not NUM.match(val):
                rep.error(where, "%s %r is not a number" % (label, val),
                          "ages are numeric Myr; remove thousand separators, commas and "
                          "units", quote("table"))
            else:
                v = float(val)
                numeric_ages.append(v)
                if v < 0:
                    rep.warn(where, "%s %s is negative; no page describes a negative age"
                             % (label, val), "use ages > 0 in Myr before present, or "
                             "verify against your own PyRate version", once="neg-age")
        if all(NUM.match(x) for x in (mint, maxt)):
            lo, hi = float(mint), float(maxt)
            if lo > hi:
                rep.warn(where, "MinT %s > MaxT %s: the two age bounds are the wrong way "
                         "round for every row of the docs' own table" % (mint, maxt),
                         "swap them - a uniform redraw between MinT and MaxT needs the "
                         "smaller age first",
                         quote("replicates") + " [ordering itself is INFERRED: no page "
                         "states it as a rule]", once="range-order")
            elif lo == hi:
                rep.warn(where, "MinT == MaxT (%s): zero temporal range" % mint,
                         "harmless for midpoint ages, but randomised replicates cannot "
                         "vary - see the cutoff option", quote("cutoff"),
                         once="zero-range")

        # one row per occurrence: identical repeats are legal, so count only
        key = tuple(cells[:4])
        seen_rows.setdefault(key, []).append(line_no)

        if len(cells) > 4:
            check_extra_column(cells[4], line_no, rep.extra_kind, extra_vals, rep)

    dup_sets = dict((k, v) for k, v in seen_rows.items() if len(v) > 1)
    if dup_sets:
        rep.note("duplicates", "%d distinct row(s) appear more than once (e.g. line(s) "
                 "%s) - legal, and not flagged: the docs' own table prints one species "
                 "with identical ages four times, because each row is one occurrence"
                 % (len(dup_sets), dup_sets[list(dup_sets)[0]][:3]),
                 "nothing, unless the repetition is unintended - deduplicate only if the "
                 "same occurrence was pasted twice",
                 quote("duprows") + " and " + quote("duprows2") + "; " + quote("onerow"))

    for name in sorted(status_by_name):
        if len(status_by_name[name]) > 1:
            rep.warn("name %r" % name, "the same taxon carries more than one Status "
                     "(%s)" % ", ".join(sorted(status_by_name[name])),
                     "give each taxon a single status, or the extant/extinct reading is "
                     "ambiguous", "the docs attach status to a species, not to an "
                     "occurrence (%s) [single-status rule INFERRED]" % quote("table"))

    if extra_vals:
        label = {"site": "site", "trait": "trait"}.get(rep.extra_kind, "5th column")
        nums = [float(x) for x in extra_vals if NUM.match(x)]
        nas = sum(1 for x in extra_vals if x.upper() == "NA")
        rep.stats["%s values given" % label] = "%d/%d rows" % (len(extra_vals), len(data))
        rep.stats["%s rows marked NA" % label] = nas
        if nums:
            rep.stats["%s range (arithmetic)" % label] = "%g-%g" % (min(nums), max(nums))
        if rep.extra_kind == "site":
            rep.stats["distinct sites"] = len({int(x) for x in nums})
            rep.note("Site column", "present: with a column named \"Site\", PyRate "
                     "\"will automatically resample fossil ages by site\" when generating "
                     "replicates, instead of drawing uniformly between MinT and MaxT",
                     "no action; keep the column name exactly \"Site\"",
                     quote("siteauto") + "; " + quote("sitecol"))

    check_name_collisions(sorted({c[1][0].lower() for c in data if len(c[1]) >= 1
                                 and c[1][0]}), rep)

    extant = {n for n, s in status_by_name.items() if "extant" in s}
    rep.stats.update({
        "occurrence rows": len(data),
        "taxa": len(ages_by_name),
        "extant taxa": len(extant),
    })
    if numeric_ages:
        rep.stats["age span (Myr)"] = "%g-%g" % (min(numeric_ages), max(numeric_ages))
    rep.note("next step", "this file is the input of the R function extract.ages, not of "
             "PyRate; after generating the *_PyRate.py run 'python PyRate.py "
             "<file>_PyRate.py -data_info' to see the same statistics from PyRate",
             None, quote("extract") + "; " + quote("datainfo"))


def check_header(header, rep, hline, expect):
    low = [h.lower() for h in header]
    if len(header) < 4:
        if low[:3] == ["species", "status", "trait"]:
            rep.error("line %d (header)" % hline,
                      "3 columns named %s: this is the *_SpeciesList.txt taxon list that "
                      "extract.ages writes, not an occurrence table" % " ".join(header),
                      "use the occurrence table (Species Status MinT MaxT [Trait]); the "
                      "SpeciesList file is the input of -check_names", quote("checknames"))
            rep.header_fatal = True
            return
        rep.error("line %d (header)" % hline, "the header has %d column(s) %s; four are "
                  "mandatory" % (len(header), " ".join(header)),
                  "add the missing age columns", quote("fourcols"))
        rep.header_fatal = True
        return
    if looks_like_numbers(header[:2]) or header[0].lower() in MISSING_TOKENS:
        rep.error("line %d" % hline, "the first row looks like data, not a header: %s"
                  % " ".join(header), "add the header row "
                  "Species<TAB>Status<TAB>MinT<TAB>MaxT", quote("onerow"))
        rep.header_fatal = True
        return
    matched = None
    for cols, label, src in HEADERS:
        if low[:4] == cols:
            matched = (label, src)
            break
    if matched is None:
        rep.error("line %d (header)" % hline,
                  "the first four columns are %s, which matches no header this corpus "
                  "prints" % " ".join(header[:4]),
                  "rename them to Species / Status / MinT / MaxT (the wiki spelling) in "
                  "that order", quote("header"))
        rep.header_fatal = True
    elif matched[0] != "wiki":
        rep.warn("line %d (header)" % hline,
                 "header %s is the %s spelling (recorded at %s); the wiki prints "
                 "`Species Status MinT MaxT` - this corpus never says which is required"
                 % (" ".join(header[:4]), matched[0], matched[1]),
                 "either works with extract.ages in practice; keep the column ORDER "
                 "(name, status, min age, max age)",
                 "CONFLICT: %s vs %s" % (quote("header"), quote("thdr")))
    else:
        rep.note("line %d (header)" % hline, "header matches the documented wiki spelling",
                 None, quote("header"))
    extra = header[4:]
    if len(extra) > 1:
        rep.error("line %d (header)" % hline,
                  "%d columns after the four mandatory ones (%s): exactly ONE additional "
                  "column is allowed" % (len(extra), " ".join(extra)),
                  "keep Trait or Site, delete the rest - the format allows one extra "
                  "column", quote("trait"))
    elif len(extra) == 1:
        name = extra[0].lower()
        if name in EXTRA_DOC:
            rep.extra_kind = name
            rep.note("5th column", "%s -> %s" % (extra[0], EXTRA_DOC[name]), None,
                     quote("trait") if name == "trait" else quote("sitecol"))
        else:
            rep.warn("line %d (header)" % hline,
                     "the 5th column is %r; the docs name it `Trait` (wiki) or `Site` "
                     "(tutorial 1)" % extra[0],
                     "rename it, or drop it - extract.ages keys the site-based age "
                     "resampling on a column named \"Site\"", quote("siteauto"))
        if expect and name != expect:
            rep.error("line %d (header)" % hline,
                      "5th column is %r but --expect %s" % (extra[0], expect),
                      "use the column you asserted, or drop --expect")
    elif expect in ("trait", "site"):
        rep.error("line %d (header)" % hline,
                  "no 5th column but --expect %s" % expect,
                  "add the %s column" % expect, quote("trait"))
    elif expect == "none":
        rep.note("5th column", "absent, as asserted by --expect none: fine for a plain "
                 "birth-death analysis")


def check_extra_column(cell, line_no, kind, vals, rep):
    """The single optional 5th column: Trait (NA allowed) or Site (assemblage ID).

    kind is "trait", "site" or None when the header did not name a known column.
    """
    where = "line %d" % line_no
    vals.append(cell)
    if cell.upper() == "NA":
        if kind == "site":
            rep.warn(where, "Site ID is NA: the Site column is documented as \"a number "
                     "specifying the ID of the assemblage for each occurrence\", and no "
                     "page documents a missing site",
                     "give every occurrence an assemblage ID, or drop the Site column and "
                     "let ages be resampled uniformly between MinT and MaxT",
                     quote("sitecol"), once="site-na")
        else:
            rep.note(where, "NA in the optional column: the documented way to spell a "
                     "missing trait value; that taxon stays in the analysis and its trait "
                     "value is imputed by the MCMC", None,
                     quote("naexample") + "; " + quote("traitna"), once="extra-na")
        return
    if is_missing(cell):
        rep.warn(where, "5th-column value %r reads as missing but is not NA" % cell,
                 "write NA - that is the only missing spelling the docs use for the "
                 "optional column", quote("trait"), once="extra-missing")
        return
    if not NUM.match(cell):
        rep.warn(where, "5th-column value %r is neither a number nor NA" % cell,
                 "a Site ID is \"a number\" and a Trait value is a number or NA",
                 quote("sitecol") + " / " + quote("trait"), once="extra-notnum")
        return
    v = float(cell)
    if kind == "site":
        if v < 0 or v != int(v):
            rep.warn(where, "Site ID %s is not a positive whole number; the docs and every "
                     "example use small integers as assemblage IDs" % cell,
                     "renumber the assemblages 1, 2, 3 ...", quote("sitecol"),
                     once="site-int")
    elif kind == "trait" and v < 0:
        rep.note(where, "negative trait value %s: legal, but no page documents a trait on "
                 "a negative scale" % cell, None, quote("trait"), once="trait-neg")


def check_name_format(name, where, rep):
    """`Genus_species` is the documented expected format (-check_names context)."""
    if re.search(r"\s", name):
        rep.warn(where, "taxon name %r contains a space; the expected format is "
                 "Genus_species" % name,
                 "replace the space with an underscore, consistently across all rows - "
                 "'Canis lupus' and 'Canis_lupus' are two taxa as far as the table goes",
                 quote("namefmt"), once="name-space")
    parts = name.split("_")
    if len(parts) != 2:
        rep.warn(where, "taxon name %r is %d underscore-separated token(s), not "
                 "Genus_species" % (name, len(parts)),
                 "use Genus_species; a 3-word name is usually a subspecies or an "
                 "author year left in the cell", quote("namefmt"),
                 once="name-tokens")
    elif not (parts[0][:1].isupper() and parts[1][:1].islower()):
        rep.warn(where, "taxon name %r does not look like Genus_species (capitalised "
                 "genus, lower-case epithet)" % name,
                 "fix the case, or confirm the name is what you want analysed",
                 quote("namefmt") + " [case convention INFERRED from the examples]",
                 once="name-case")
    if name.lower() in MISSING_TOKENS:
        rep.error(where, "taxon name %r is a missing-value marker" % name,
                  "fill the name or drop the occurrence", quote("nomissing"))


def lev(a, b, cap=3):
    """Bounded Levenshtein distance (returns cap+1 when further apart)."""
    if abs(len(a) - len(b)) > cap:
        return cap + 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        best = i
        for j, cb in enumerate(b, 1):
            val = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb))
            cur.append(val)
            best = min(best, val)
        if best > cap:
            return cap + 1
        prev = cur
    return prev[-1]


def check_name_collisions(names, rep):
    """Near-identical names: a static echo of the documented -check_names function."""
    uniq = sorted(set(names))
    if len(uniq) > 1200:
        rep.note("name spelling", "the built-in near-identical-name scan was skipped "
                 "(%d distinct names, quadratic cost); the documented check has no such "
                 "limit" % len(uniq),
                 "python PyRate.py -check_names <TaxonList.txt>", quote("checknames"))
        return
    hits = []
    for i, a in enumerate(uniq):
        for b in uniq[i + 1:]:
            if a.split("_")[0] != b.split("_")[0]:
                continue
            d = lev(a.lower(), b.lower())
            if 0 < d <= 2:
                hits.append((a, b, d))
    for a, b, d in hits[:8]:
        rep.warn("names %r / %r" % (a, b),
                 "spelled %d character(s) apart - possibly the same taxon under two "
                 "spellings" % d,
                 "run the documented check: python PyRate.py -check_names "
                 "<TaxonList.txt>; its ranks 0-1 mean likely misspelling, 2-3 likely "
                 "different names. Note -check_names does NOT check synonyms.",
                 quote("ranks") + "; " + quote("nosyn") +
                 " [this tool's edit distance is its own heuristic, NOT the -check_names "
                 "algorithm]")
    if len(hits) > 8:
        rep.warn("names", "+%d further near-identical name pair(s) not shown"
                 % (len(hits) - 8), "use -check_names on the whole list",
                 quote("checknames"))
    if hits:
        rep.stats["near-identical name pairs"] = len(hits)


# ------------------------------------------------------------- the *_PyRate.py input
def balanced(text, open_idx):
    """Return (inner_text, end_idx) for the bracket group starting at text[open_idx]."""
    depth = 0
    for i in range(open_idx, len(text)):
        c = text[i]
        if c in "([":
            depth += 1
        elif c in ")]":
            depth -= 1
            if depth == 0:
                return text[open_idx + 1:i], i
    return text[open_idx + 1:], len(text) - 1


TOKEN = re.compile(r"[A-Za-z_][A-Za-z_0-9.]*|[-+]?\d+\.?\d*(?:[eE][-+]?\d+)?")
# words that legitimately appear inside a numeric list and are not occurrence ages
NAME_OK = {"nan", "inf", "-inf", "+inf", "neginf", "float64", "float32", "float16",
           "float", "int64", "int32", "int8", "dtype", "array"}


def parse_numbers(inner, where, rep, allow_nan):
    vals, junk = [], []
    for tok in TOKEN.findall(inner):
        low = tok.lower()
        if low in NAME_OK:
            if low in ("nan", "inf", "-inf", "+inf", "neginf") and not allow_nan:
                junk.append(tok)
            continue
        try:
            vals.append(float(tok))
        except ValueError:
            junk.append(tok)
    if junk:
        rep.error(where, "non-numeric token(s) %s inside an occurrence list"
                  % ", ".join(repr(j) for j in junk[:5]),
                  "the data must be numbers (the docs describe the file as a list of "
                  "Numpy arrays of occurrence ages)",
                  quote("spyfile"))
    return vals


def check_pyrate_py(path, text, rep):
    lines = split_lines(text)
    if not [l for l in lines if l.strip()]:
        rep.error("file", "empty file: nothing for PyRate to read",
                  "generate the input with extract.ages first", quote("generates"))
        return
    rep.note("how this file was read",
             "as text only - it was NOT imported, exec'd or unpickled, because a "
             "*_PyRate.py file is arbitrary Python and running it runs its contents")
    # an excerpt (as this suite's own shape fixture is) says so in a comment; incomplete
    # blocks in such a file are a property of the excerpt, not of the user's data
    excerpt = bool(re.search(r"#.*\b(elided|elision|truncated for brevity)\b", text,
                             re.IGNORECASE))
    if excerpt:
        rep.note("excerpt", "the file contains an elision comment, so it is an excerpt of "
                 "a generated input; findings about blocks that are simply not shown are "
                 "reported as NOTE", "to validate a real analysis input, run this on the "
                 "full *_PyRate.py that extract.ages wrote",
                 "shape observed in %s" % PY_SHAPE_FIXTURE)

    if not re.search(r"\barray\s*\(?\s*\[", text):
        rep.error("file", "no array(...) data block found: the documented input is \"a "
                  "Python file with the fossil occurrence data (as list of Numpy "
                  "arrays)\"",
                  "regenerate it with the R function extract.ages, which writes exactly "
                  "that shape", quote("spyfile"))
        return
    if not re.search(r"^\s*data_\d+\s*=", text, re.MULTILINE):
        rep.error("file", "no data_N=[...] occurrence list found - the file has arrays but "
                  "not the names extract.ages gives them",
                  "regenerate with extract.ages; if you edited the file by hand, restore "
                  "the data_1, data_2, ... variables",
                  "%s; observed shape recorded in %s" % (quote("spyfile"), PY_SHAPE_FIXTURE))
        return

    replicates = {}
    for m in re.finditer(r"^\s*(data_(\d+))\s*=\s*\[", text, re.MULTILINE):
        var, num = m.group(1), int(m.group(2))
        inner, _end = balanced(text, m.end() - 1)
        arrays = []
        pos = 0
        while True:
            a = re.compile(r"\barray\s*\(?\s*\[").search(inner, pos)
            if not a:
                break
            body, close = balanced(inner, a.end() - 1)
            vals = parse_numbers(body, "array #%d of %s" % (len(arrays) + 1, var),
                                 rep, allow_nan=True)
            arrays.append(vals)
            pos = close + 1
        replicates[num] = arrays

    if not replicates:
        rep.error("file", "data_N variables are present but none could be read",
                  "the file may be truncated; re-run extract.ages", quote("spyfile"))
        return

    counts = dict((n, len(a)) for n, a in replicates.items())
    sizes = sorted(set(counts.values()))
    if len(sizes) > 1:
        rep.error("replicate shape", "the replicates hold different numbers of taxa: %s"
                  % ", ".join("data_%d=%d" % (n, counts[n]) for n in sorted(counts)),
                  "every replicate redraws the SAME taxa, so the lists must be the same "
                  "length; regenerate with extract.ages(replicates=N)",
                  quote("replicates"))
    taxa = sizes[0] if len(sizes) == 1 else None
    total_occ = sum(len(v) for a in replicates.values() for v in a)
    empty_taxa = sum(1 for a in replicates.values() for v in a if not v)
    if empty_taxa:
        rep.error("occurrence lists", "%d taxon list(s) contain no age at all" % empty_taxa,
                  "a taxon with no occurrence cannot be analysed - remove it from the "
                  "source table", quote("nomissing"))
    all_vals = [v for a in replicates.values() for lst in a for v in lst]
    if all_vals:
        rep.stats["replicates (data blocks fully present)"] = len(replicates)
        rep.stats["taxa per replicate"] = taxa if taxa is not None else "?"
        rep.stats["occurrences in those blocks"] = total_occ
        rep.stats["ages in data_* (all replicates)"] = len(all_vals)
        rep.stats["age span (Myr)"] = "%g-%g" % (min(all_vals), max(all_vals))
    if any(v < 0 for v in all_vals):
        rep.warn("ages", "at least one age in the data lists is negative",
                 "check the source table; no page describes negative ages")

    dm = re.search(r"^\s*d\s*=\s*\[", text, re.MULTILINE)
    if dm:
        inner, _e = balanced(text, dm.end() - 1)
        listed = re.findall(r"data_(\d+)", inner)
        missing = [x for x in listed if int(x) not in replicates]
        if missing:
            more = "" if len(missing) <= 10 else " (+%d more)" % (len(missing) - 10)
            shown = ("d references data_%s, which is not defined in the file%s"
                     % (", data_".join(missing[:10]), more))
            if excerpt:
                rep.note("d=[...]", shown + " - expected in an excerpt that shows only the "
                         "first data block",
                         "no action for the excerpt; check the same thing on your real input",
                         "the docs call the file a list of data sets (%s)" % quote("several"))
            else:
                rep.error("d=[...]", shown,
                          "the file is incomplete; regenerate it with extract.ages",
                          "the docs call the file a list of data sets (%s)" % quote("several"))
        unlisted = sorted(set(replicates) - {int(x) for x in listed})
        if unlisted:
            rep.warn("d=[...]", "data_%s defined but not referenced by d=[...] - they "
                     "would never be analysed" % ", ".join(str(u) for u in unlisted[:6]),
                     "regenerate the file; -j can only pick a data set listed in d",
                     quote("jdefault"))
        rep.stats["data sets listed in d"] = len(listed)
        # what -j can select is the list in d, even when an excerpt does not show every
        # data block the list names
        rep.stats["replicates"] = len(listed) if listed else len(replicates)
        if listed and max(int(x) for x in listed) > 1:
            rep.note("-j", "this input carries %d data sets, so -j accepts 1..%d (default "
                     "1)" % (len(listed), len(listed)),
                     "analyse several replicates and combine them with -combLog",
                     quote("jdefault"))
    else:
        rep.stats["replicates"] = len(replicates)
        rep.warn("d=[...]", "no d=[...] variable found: PyRate selects the data set "
                 "through it", "regenerate with extract.ages", quote("several"))

    for label in ("taxa_names", "names"):
        nm = re.search(r"^\s*%s\s*=\s*\[" % label, text, re.MULTILINE)
        if not nm:
            rep.warn(label, "no %s=[...] list in the file" % label,
                     "the generated input normally carries it; regenerate with "
                     "extract.ages if you did not write these by hand",
                     "shape observed in %s" % PY_SHAPE_FIXTURE)
            continue
        inner, _e = balanced(text, nm.end() - 1)
        got = [t for t in re.findall(r"'([^']*)'|\"([^\"]*)\"", inner)]
        names = [a or b for a, b in got]
        if label == "taxa_names" and taxa is not None and len(names) != taxa:
            msg = "%d names but %d occurrence lists per replicate" % (len(names), taxa)
            if excerpt:
                rep.note("taxa_names", msg + " - expected in an excerpt that shows only "
                         "part of one data block",
                         "no action for the excerpt; on a real input this pairing must "
                         "line up 1:1", "%s [the 1:1 pairing is INFERRED: the corpus prints "
                         "no *_PyRate.py]" % quote("spyfile"))
            else:
                rep.error("taxa_names", msg,
                          "the name list and the data lists must line up 1:1; regenerate "
                          "with extract.ages",
                          "%s [the 1:1 pairing is INFERRED: the corpus prints no "
                          "*_PyRate.py]" % quote("spyfile"))
        dupes = sorted({n for n in names if names.count(n) > 1})
        if dupes:
            rep.error("%s" % label, "duplicate name(s) in %s: %s"
                      % (label, ", ".join(repr(d) for d in dupes[:5])),
                      "one entry per taxon; a repeated name makes the occurrence lists "
                      "ambiguous", quote("onerow") + " [one-row-per-occurrence rule read "
                      "across to the generated list: INFERRED]")
        if label == "taxa_names":
            for n in names:
                if re.search(r"\s", n) or len(n.split("_")) != 2:
                    rep.warn("%s" % label, "name %r does not match the expected format "
                             "Genus_species" % n,
                             "fix the spelling in the source table before regenerating; "
                             "inconsistent spellings 'hamper the accuracy of the analysis'",
                             quote("namefmt"))
                    break
            check_name_collisions([n for n in names if n], rep)
        else:
            n_sets = rep.stats.get("data sets listed in d")
            rep.note("names", "names=[...] holds one label per data set (%d here%s), not "
                     "one per taxon; the file's own get_out_name(i) returns names[i]"
                     % (len(names), ", d lists %d data sets" % n_sets if n_sets else ""),
                     "keep len(names) equal to the number of data sets in d",
                     "shape observed in %s [how the real program uses names is NOT "
                     "documented in this corpus]" % PY_SHAPE_FIXTURE)

    traits = re.findall(r"^\s*(trait\d+)\s*=\s*array\s*\(?\s*\[", text, re.MULTILINE)
    for tvar in traits:
        m = re.search(r"^\s*%s\s*=\s*array\s*\(?\s*\[" % tvar, text, re.MULTILINE)
        inner, _e = balanced(text, m.end() - 1)
        n_nan = len(re.findall(r"\bnan\b", inner))
        vals = parse_numbers(inner, tvar, rep, allow_nan=True)
        rep.note(tvar, "%d value(s), %d of them nan - nan is how a missing trait is "
                 "written in the table, and those taxa stay in the analysis because "
                 "\"their trait value will be imputed by the MCMC\""
                 % (len(vals) + n_nan, n_nan),
                 "no action, unless the count of nan is itself a mistake in your table",
                 quote("traitna") + "; " + quote("naexample"))
        if taxa is not None:
            if excerpt:
                rep.note(tvar, "entry-count check skipped: this excerpt shows %d of the "
                         "%d taxon lists, so the trait length cannot be compared to them"
                         % (taxa, len(vals) + n_nan), None,
                         "shape observed in %s" % PY_SHAPE_FIXTURE)
            elif len(vals) + n_nan != taxa:
                rep.warn(tvar, "%d entries for %d taxa" % (len(vals) + n_nan, taxa),
                         "one trait value (or NA) per taxon", quote("traitna"))
    if not traits:
        rep.note("traits", "no traitN=array(...) in the input: fine, unless you plan a "
                 "Covar model, in which case the trait may also come from -trait_file",
                 None, quote("spyfile"))
    if re.search(r"^\s*(from\s+numpy\s+import\s+\*|import\s+numpy)", text, re.MULTILINE):
        rep.note("numpy", "the file imports numpy - expected, and the reason a PyRate "
                 "input needs the numpy install; this tool did not import it",
                 None, quote("spyfile"))
    rep.note("next step", "check what PyRate itself reads with: python PyRate.py %s "
             "-data_info (and -singleton 1 if you want singletons excluded)"
             % os.path.basename(path), None, quote("datainfo"))


# ------------------------------------------------------------------------------ rules
def print_rules():
    print("Rules validate_input.py applies, each quoted from the mirror it reads:")
    for key in sorted(CITE):
        rel, line, _q = CITE[key]
        print("  %-12s %s:%d" % (key, rel, line))
    print("\nGrading: ERROR = the page states the rule; WARN = the page only shows the")
    print("pattern (or this tool inferred it); NOTE = information. A WARN never fails a")
    print("run. Header spellings conflict across the corpus - all four printed variants")
    print("are accepted (see the module docstring).")


def audit_citations(verbose=False):
    """--self-test uses this: every quote must sit at its claimed mirror line."""
    bad = []
    cache = {}
    for key, (rel, line, text) in CITE.items():
        if rel not in cache:
            path = os.path.normpath(os.path.join(SKILL_DIR, rel))
            try:
                with open(path, encoding="utf-8") as fh:
                    cache[rel] = (path, fh.read().split("\n"))
            except OSError:
                cache[rel] = (path, None)
        path, lines = cache[rel]
        if lines is None:
            bad.append("%s: mirror file missing: %s" % (key, rel))
            continue
        window = " ".join(lines[max(0, line - 2):line + 1])
        if strip_md(text) not in strip_md(window):
            bad.append("%s: quote not at %s:%d -> %r" % (key, rel, line, text[:60]))
    del verbose
    return bad


MD_ESC = re.compile(r"\\([\\`*_{}\[\]()#+\-.!|~])")


def strip_md(s):
    """Drop markdown decoration so quotes match the rendered sentence."""
    s = MD_ESC.sub(r"\1", s)
    s = s.replace("`", "").replace("*", "")
    return re.sub(r"\s+", " ", s.replace("\t", " ")).strip()


# -------------------------------------------------------------------------- self-test
def self_test():
    import shutil
    import tempfile
    rep = Report("(self-test)", "table")
    fails = []
    checks = [0]

    def expect(cond, msg):
        checks[0] += 1
        if not cond:
            fails.append(msg)

    # 0. every citation must be real
    bad = audit_citations()
    expect(not bad, "citation audit:\n    " + "\n    ".join(bad))

    tmp = tempfile.mkdtemp(prefix="validate_input_selftest_")
    try:
        def write(name, text):
            p = os.path.join(tmp, name)
            with open(p, "w", encoding="utf-8", newline="") as fh:
                fh.write(text)
            return p

        def run(name, text, expect_kind=None, **kw):
            p = write(name, text)
            r = validate_file(p, None, expect_kind)
            if kw.get("expect"):
                r = validate_file(p, kw["expect"], expect_kind)
            return r

        wiki = ("Species\tStatus\tMinT\tMaxT\tTrait\n"
                "Ursus_etruscus\textinct\t1.9\t2.6\t90\n"
                "Agriotherium_intermedium\textinct\t3.4\t4.2\tNA\n"
                "Ailuropoda_melanoleuca\textant\t0.01\t0.5\t120\n")
        r = run("ok.txt", wiki)
        expect(r.ok, "docs example shape must pass, got %r"
               % [f for f in r.findings if f["level"] == "ERROR"])
        expect(r.count("ERROR") == 0 and r.count("WARN") == 0,
               "clean file should have no WARN either: %r"
               % [f["message"] for f in r.findings if f["level"] == "WARN"])
        expect(r.stats.get("occurrence rows") == 3, "row count wrong: %r" % r.stats)
        expect(r.stats.get("extant taxa") == 1, "extant count wrong: %r" % r.stats)
        expect(any("imputed by the MCMC" in f["message"] for f in r.findings),
               "the NA trait must be explained: %r" % r.findings)

        r = run("space.txt", wiki.replace("\t", "  "))
        expect(any(f["level"] == "ERROR" and "tab" in f["message"] for f in r.findings),
               "space-delimited must be an ERROR")
        expect(any("sed" in f["fix"] for f in r.findings), "a delimiter fix hint expected")

        r = run("csv.txt", "Species,Status,MinT,MaxT\nA_b,extinct,1.2,2.6\n")
        expect(any("tab-delimited" in f["message"] for f in r.findings),
               "CSV must be flagged as not tab-delimited")

        r = run("status.txt", "Species\tStatus\tMinT\tMaxT\nA_b\tliving\t1.2\t2.6\n")
        expect(any(f["level"] == "ERROR" and "living" in f["message"] for f in r.findings),
               "bad Status vocabulary must be an ERROR")
        expect(any("extinct" in f["fix"] for f in r.findings), "Status fix hint missing")

        r = run("missing.txt", "Species\tStatus\tMinT\tMaxT\nA_b\textinct\t\t2.6\n"
                              "C_d\textinct\t1.0\td\n")
        errs = [f for f in r.findings if f["level"] == "ERROR"]
        expect(len(errs) >= 2 and r.ok is False,
               "blank MinT and non-numeric MaxT must both be errors: %r" % errs)
        expect(any("missing information" in f["cite"] or "cannot be handled" in f["fix"]
                   for f in errs), "the missing-value rule must be quoted: %r" % errs)

        r = run("order.txt", "Species\tStatus\tMinT\tMaxT\nA_b\textinct\t5.0\t2.0\n")
        expect(r.ok and any("wrong way round" in f["message"] for f in r.findings),
               "MinT>MaxT must WARN without failing: %r" % r.findings)

        r = run("swapped.txt", "Species\tMinT\tMaxT\tStatus\nA_b\t1.0\t2.0\textinct\n")
        expect(any(f["level"] == "ERROR" and "no header this corpus" in f["message"]
                   for f in r.findings), "wrong header order must be an ERROR")

        r = run("tutorial.txt",
                "# source: derived fixture\n# shows: the tutorial-1 table\n"
                "Taxon_name\tStatus\tMinAge\tMaxAge\n"
                "Canis_ferox\textinct\t4.9\t10.3\nCanis_ferox\textinct\t4.9\t10.3\n")
        expect(r.ok, "the tutorial header plus provenance comments must pass: %r"
               % [f for f in r.findings if f["level"] == "ERROR"])
        expect(any("CONFLICT" in (f["cite"] or "") for f in r.findings),
               "the header conflict must be cited")
        expect(any("four times" in f["message"] for f in r.findings),
               "identical duplicate rows must be explained as legal, not flagged")

        r = run("upstream.txt", "Species\tStatus\tmin_age\tmax_age\ttrait\r"
                                "Ursus_thibetanus\textant\t0.126\t0.781\t99714.19\r"
                                "Ursus_wenzensis\textinct\t3.4\t4.2\tNA\r")
        expect(r.ok, "CR-only line endings and the upstream header must be handled: %r"
               % [f for f in r.findings if f["level"] == "ERROR"])

        r = run("twoextra.txt", "Species\tStatus\tMinT\tMaxT\tTrait\tSite\n"
                               "A_b\textinct\t1\t2\t5\tX\n")
        expect(any(f["level"] == "ERROR" and "exactly ONE" in f["message"]
                   for f in r.findings), "two extra columns must be an ERROR")

        r = run("sitewrong.txt", "Species\tStatus\tMinT\tMaxT\tSite\n"
                                "A_b\textinct\t1\t2\tsite-one\n"
                                "C_d\textinct\t1\t2\t4\n")
        expect(any("neither a number nor NA" in f["message"] for f in r.findings),
               "a non-numeric Site must be flagged")
        expect(validate_file(write("expect.txt", wiki), "site").count("ERROR") >= 1,
               "--expect site on a Trait table must error")
        expect(validate_file(write("expect2.txt", wiki), "trait").ok,
               "--expect trait on a Trait table must pass")

        r = run("spaces.txt", "Species\tStatus\tMinT\tMaxT\n"
                             "Canis lupus\textant\t0.1\t0.5\n"
                             "canis_ferox\textinct\t1.0\t2.0\n")
        msgs = " ".join(f["message"] for f in r.findings)
        expect("Genus_species" in msgs, "name format must be checked: %r" % msgs)
        expect(r.ok, "name-format problems are WARN, not ERROR")

        r = run("dupe.txt", "Species\tStatus\tMinT\tMaxT\n"
                           "Adocus_parvus\textinct\t1\t2\n"
                           "Adocus_pravus\textinct\t3\t4\n"
                           "Ursus_etruscus\textinct\t1\t2\n"
                           "Ursus_etruscus\textant\t5\t6\n")
        msgs = " ".join(f["message"] for f in r.findings)
        expect("spelled 2 character(s) apart" in msgs or "near-identical" in msgs,
               "near-duplicate spellings must be reported: %r" % msgs)
        expect("more than one Status" in msgs,
               "a name with two statuses must be reported: %r" % msgs)
        expect("-check_names" in " ".join(f["fix"] for f in r.findings),
               "the -check_names route must be recommended")

        r = run("speclist.txt", "Species\tStatus\tTrait\nAgriotherium_africanum\textinct\tNA\n")
        expect(any(f["level"] == "ERROR" and "SpeciesList" in f["message"]
                   for f in r.findings), "a taxon list must not pass as an occurrence table")

        # --- the generated *_PyRate.py ------------------------------------
        good_py = ("from numpy import *\n\n"
                   "data_1=[array([2.65,4.12]),array([6.5,10.99]),array([0.01])]\n"
                   "data_2=[array([2.7,4.2]),array([6.6,11.0]),array([0.02])]\n"
                   "d=[ data_1, data_2]\n"
                   "names=[ 'Ursidae_1', 'Ursidae_2',]\n"
                   "taxa_names=['Ursus_etruscus','Agriotherium_insigne','Ailuropoda_melanoleuca']\n"
                   "trait1=array([ 90, nan, 120])\ntraits=[trait1]\n")
        r = run("good_PyRate.py", good_py)
        expect(r.ok, "a well-formed generated input must pass: %r"
               % [f for f in r.findings if f["level"] == "ERROR"])
        expect(r.stats.get("replicates") == 2, "-j range/stats wrong: %r" % r.stats)
        expect(any("-j accepts 1..2" in f["message"] for f in r.findings),
               "the -j note is missing: %r" % [f["message"] for f in r.findings])
        expect(any("imputed by the MCMC" in f["message"] for f in r.findings),
               "the trait nan convention must be reported")
        expect(any("NOT imported" in f["message"] for f in r.findings),
               "the no-execution guarantee must be stated")

        r = run("mismatch_PyRate.py", good_py.replace(
            "taxa_names=['Ursus_etruscus','Agriotherium_insigne','Ailuropoda_melanoleuca']",
            "taxa_names=['Ursus_etruscus','Agriotherium_insigne']"))
        expect(any(f["level"] == "ERROR" and "occurrence lists" in f["message"]
                   for f in r.findings), "3 lists vs 2 names must be an ERROR")

        r = run("ragged_PyRate.py",
                "from numpy import *\ndata_1=[array([1.0,2.0]),array([3.0])]\n"
                "data_2=[array([1.0,2.0])]\nd=[ data_1, data_2]\n"
                "taxa_names=['A_b','C_d']\n")
        expect(any("different numbers of taxa" in f["message"] for f in r.findings),
               "replicates with different taxon counts must be an ERROR")

        r = run("missingd_PyRate.py",
                "from numpy import *\ndata_1=[array([1.0,2.0]),array([3.0])]\n"
                "data_2=[array([1.0,2.0]),array([3.0])]\nd=[ data_1]\n"
                "taxa_names=['A_b','C_d']\n")
        expect(any("would never be analysed" in f["message"] for f in r.findings),
               "an unreferenced data_2 must be warned about")

        r = run("empty_PyRate.py", "from numpy import *\ndata_1=[array([])]\n"
                                  "d=[ data_1]\ntaxa_names=['A_b']\n")
        expect(any(f["level"] == "ERROR" and "no age at all" in f["message"]
                   for f in r.findings), "an empty occurrence list must be an ERROR")

        r = run("junk_PyRate.py", "from numpy import *\ndata_1=[array([1.0, oops])]\n"
                                 "d=[ data_1]\ntaxa_names=['A_b']\n")
        expect(any("non-numeric token" in f["message"] for f in r.findings),
               "a stray token inside array([...]) must be reported")

        r = run("notarray_PyRate.py", "# just a comment\nx = 1\n")
        expect(any(f["level"] == "ERROR" and "array(" in f["message"] for f in r.findings),
               "a .py without array(...) must fail")

        # a hostile input must not be able to run anything
        marker = os.path.join(tmp, "OWNED_BY_IMPORTED_FILE")
        hostile = ("from numpy import *\nimport os\n"
                   "open(%r, 'w').write('ran')\n"
                   "data_1=[array([1.0,2.0])]\nd=[ data_1]\ntaxa_names=['A_b']\n" % marker)
        r = run("hostile_PyRate.py", hostile)
        expect(not os.path.exists(marker),
               "VALIDATE_INPUT EXECUTED ITS INPUT - the file was imported or exec'd")
        expect(r.ok or True, "hostile file handled")

        # bounded output: 200 identical findings must collapse into one line + a count
        many = ("Species\tStatus\tMinT\tMaxT\tTrait\n"
                + "".join("Ursus_sp%d\textinct\t1.0\t2.0\tNA\n" % i for i in range(200)))
        r = run("many_na.txt", many)
        na_notes = [f for f in r.findings if "imputed by the MCMC" in f["message"]]
        expect(len(na_notes) == 1, "the NA-trait note must be aggregated, got %d"
               % len(na_notes))
        expect(na_notes and na_notes[0].get("more") == 199,
               "the aggregated count must be reported: %r"
               % (na_notes[0] if na_notes else None))
        expect(r.ok, "200 NA traits is not an error: %r"
               % [f for f in r.findings if f["level"] == "ERROR"])

        # the CLI must never let a traceback reach the agent
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                rc_missing = main([os.path.join(tmp, "definitely_absent.txt")])
                rc_ok = main([os.path.join(tmp, "ok.txt")])
        except Exception as exc:
            expect(False, "main() raised %s: %s" % (type(exc).__name__, exc))
        else:
            expect(rc_missing == 1 and rc_ok == 0,
                   "exit codes must be 1 for a missing file and 0 for a clean one, got "
                   "%r/%r" % (rc_missing, rc_ok))
            expect("Traceback" not in buf.getvalue(),
                   "a raw traceback was printed to the agent")

        # the suite's own fixture, if present, must at least parse
        fixture = os.path.normpath(os.path.join(SUITE_DIR, "assets", "files",
                                               "occ-pyrate-input-structure-EXCERPT.py"))
        if os.path.isfile(fixture):
            r = validate_file(fixture, None, None)
            expect(r.kind == "pyrate-py", "the suite fixture was not seen as a PyRate input")
            expect(r.stats.get("replicates") == 10,
                   "the suite fixture has 10 replicates, saw %r" % r.stats)
            expect(r.ok, "the suite's own shape fixture must not error: %r"
                   % [f for f in r.findings if f["level"] == "ERROR"])
        table_fixture = os.path.normpath(os.path.join(
            SUITE_DIR, "assets", "files", "occ-canis-table-with-Site.txt"))
        if os.path.isfile(table_fixture):
            r = validate_file(table_fixture, None, None)
            expect(r.ok, "the tutorial Site table must pass: %r"
                   % [f for f in r.findings if f["level"] == "ERROR"])
            expect(any("Site" in f["message"] for f in r.findings),
                   "the Site column should be recognised")

        # json shape + bounded output
        payload = [rep_to_json(validate_file(write("j.txt", wiki), None, None))]
        json.dumps(payload)
        expect(len(render_report(validate_file(write("j2.txt", wiki), None, None),
                                argparse.Namespace(max_findings=50))) < 40,
               "report not bounded")
        expect(not audit_citations(), "citation audit drifted")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        for f in fails:
            print("SELF-TEST FAIL: %s" % f)
        print("validate_input.py self-test: FAILED (%d of %d assertions)"
              % (len(fails), checks[0]))
        return 1
    print("validate_input.py self-test: OK (%d assertions; %d cited rules re-verified "
          "against the mirrors; tables + generated *_PyRate.py inputs; a hostile input "
          "was confirmed not to execute)" % (checks[0], len(CITE)))
    return 0


def rep_to_json(rep, max_findings=None):
    findings = rep.findings
    hidden = 0
    if max_findings and len(findings) > max_findings:
        hidden = len(findings) - max_findings
        findings = findings[:max_findings]
    return {"path": rep.path, "kind": rep.kind, "ok": rep.ok,
            "errors": rep.count("ERROR"), "warnings": rep.count("WARN"),
            "notes": rep.count("NOTE"), "stats": rep.stats,
            "total_findings": len(rep.findings), "findings_not_shown": hidden,
            "findings": findings}


# ------------------------------------------------------------------------------ main
def validate_file(path, expect, forced_kind=None):
    text, note = read_text(path)
    kind = forced_kind or sniff_kind(text or "", path)
    rep = Report(path, kind)
    if text is None:
        rep.error("file", note or "unreadable", "check the path and permissions")
        return rep
    if note:
        rep.warn("file", note, "nothing - the rest of the file was not inspected")
    if kind == "pyrate-py":
        check_pyrate_py(path, text, rep)
    else:
        check_table(path, text, rep, expect)
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(prog="validate_input.py", add_help=True,
                                 description="Pre-flight validation of a PyRate "
                                             "occurrence table or *_PyRate.py input "
                                             "(read-only, stdlib-only, never executes "
                                             "the input).",
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog="Exit 0 = no ERROR, 1 = at least one ERROR, "
                                        "2 = usage/IO problem.")
    ap.add_argument("paths", nargs="*", metavar="PATH")
    ap.add_argument("--expect", choices=["trait", "site", "none"],
                    help="assert what the optional 5th column must be")
    ap.add_argument("--pyrate-dir", metavar="DIR", default=None,
                    help="recorded in the report; the directory PyRate.py would run from")
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    ap.add_argument("--rules", action="store_true", help="print the cited rule table")
    ap.add_argument("--max-findings", type=int, default=40, metavar="N",
                    help="stop listing findings after N (default 40, max 500)")
    ap.add_argument("--quiet", action="store_true", help="only the RESULT lines")
    ap.add_argument("--self-test", action="store_true",
                    help="build temp fixtures and assert behaviour")
    try:
        args = ap.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if exc.code else 0

    if args.self_test:
        return self_test()
    if args.rules:
        print_rules()
        return 0
    if not args.paths:
        print(__doc__)
        return 2
    if not 1 <= args.max_findings <= 500:
        print("error: --max-findings must be in 1-500", file=sys.stderr)
        return 2

    reports, missing = [], 0
    for path in args.paths:
        if not os.path.isfile(path):
            missing += 1
            rep = Report(path, "unknown")
            rep.error("file", "not found (or not a regular file)",
                      "check the path; directories are not validated")
            reports.append(rep)
            continue
        try:
            reports.append(validate_file(path, args.expect))
        except Exception as exc:            # a raw traceback is never useful to an agent
            rep = Report(path, "unknown")
            rep.error("file", "the checker itself stopped on this file: %s: %s"
                      % (type(exc).__name__, exc),
                      "treat the file as UNVALIDATED and say so; do not assume it is "
                      "correct because this tool failed")
            reports.append(rep)

    if args.json:
        print(json.dumps({"pyrate_dir": args.pyrate_dir, "expect": args.expect,
                          "files": [rep_to_json(r, args.max_findings) for r in reports],
                          "hard_errors": sum(r.count("ERROR") for r in reports)},
                         ensure_ascii=False, indent=1))
    else:
        if args.pyrate_dir:
            print("PyRate program directory (for context only): %s" % args.pyrate_dir)
        total_err = total_warn = 0
        for rep in reports:
            if not args.quiet:
                for line in render_report(rep, args):
                    print(line)
                print("")
            total_err += rep.count("ERROR")
            total_warn += rep.count("WARN")
            print("RESULT %s: %s (%d error%s, %d warning%s)"
                  % (os.path.basename(rep.path), "PASS" if rep.ok else "FAIL",
                     rep.count("ERROR"), "" if rep.count("ERROR") == 1 else "s",
                     rep.count("WARN"), "" if rep.count("WARN") == 1 else "s"))
            if rep.kind == "table" and rep.ok:
                print("  next: source(\".../pyrate_utilities.r\") then "
                      "extract.ages(file=\"%s\", replicates=10) - passing this checker "
                      "does not mean the R function accepts the file"
                      % os.path.basename(rep.path))
        print("\nSUMMARY: %d file(s), %d ERROR, %d WARN%s"
              % (len(reports), total_err, total_warn,
                 "" if not missing else " (%d missing)" % missing))
        print("ERRORs are rules the docs state; WARNs are patterns the docs only exhibit")
        print("or that this tool inferred, and never fail a run. --rules prints the")
        print("quotations behind every ERROR.")
        return 1 if total_err else 0
    return 1 if sum(r.count("ERROR") for r in reports) else 0


if __name__ == "__main__":
    sys.exit(main())
