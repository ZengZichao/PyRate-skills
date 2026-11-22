#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Machine-readable copy of the PyRate.py command list.

Every row is transcribed from the verbatim mirror
``pyrate-command-reference/references/command-list.md`` (mirror line numbers
include its 8-line YAML frontmatter, so they match ``grep -n`` output on that
file; the Simplified-Chinese twin ``command-list-cn.md`` sits one line lower
because its frontmatter has 9 lines).  Nothing here is invented: ``arity`` and
``values`` are what the mirror's own example lines print, ``default`` is the
mirror's own "(default)" note, ``None`` means the page states no default.
``--self-test`` re-verifies every row (heading line, CN line, arity) against
the on-disk mirrors and every ``KNOWN_ELSEWHERE`` citation against the file it
names; a drift between this table and the mirrors fails the test.

Sections are the eight `###` headings of the page, in the order the page
prints them.

This module is the machine-readable index that the resource tables of
``pyrate-command-reference/SKILL.md`` and ``pyrate-des/SKILL.md`` point to
("the data table behind the index"); it is standalone — run it to look a
command up or to print the index, e.g.::

    python3 pyrate_commands.py            # full index by section
    python3 pyrate_commands.py -mCov      # one command, with EN/CN lines
    python3 pyrate_commands.py --elsewhere  # flags documented off the page
    python3 pyrate_commands.py --self-test
"""

from __future__ import print_function

import argparse
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))
SUITE_DIR = os.path.normpath(os.path.join(SKILL_DIR, ".."))
EN_MIRROR = os.path.join(SKILL_DIR, "references", "command-list.md")
CN_MIRROR = os.path.join(SKILL_DIR, "references", "command-list-cn.md")

PAGE = "command-list.md"

# ---------------------------------------------------------------------------
# flag -> spec
#   section : heading of the wiki page the flag is printed under
#   line    : line of the `#####` heading in references/command-list.md
#   cnline  : line of the same heading in references/command-list-cn.md
#   arity   : number of values the page's own example line shows (0 = switch)
#   values  : accepted value form(s), verbatim-condensed from the page
#   default : documented default text, or None when the page states none
#   requires: flags/values that must also be present for this one to be used
#   conflicts: mutually exclusive analysis-mode values
# ---------------------------------------------------------------------------
COMMANDS = {
    "<input file>": dict(section="input files / working directory", line=12, cnline=13,
                         arity=1, values="path to the *_PyRate.py occurrence file",
                         default=None, requires=[], conflicts=[],
                         semantics="the input file itself: occurrence data as a list of Numpy arrays"),
    "-d": dict(section="input files / working directory", line=17, cnline=18,
               arity=1, values="path to a tab-separated origin/extinction table",
               default=None, requires=[], conflicts=["<input file>"],
               semantics="alternative input: given times of origin/extinction per species; "
                         "auto-sets -fixSE = null"),
    "-wd": dict(section="input files / working directory", line=22, cnline=23,
                arity=1, values="path_to_target_directory", default=None, requires=[], conflicts=[],
                semantics="working directory for all output files (else the input-file directory)"),
    "-j": dict(section="input files / working directory", line=27, cnline=28,
               arity=1, values="int (replicate / data-set number)", default="1",
               requires=[], conflicts=[],
               semantics="which data set of a multi-data-set input file is analysed"),
    "-out": dict(section="input files / working directory", line=32, cnline=33,
                 arity=1, values="tag string", default=None, requires=[], conflicts=[],
                 semantics="tag appended to the default stem name of output files"),
    "-singleton": dict(section="input files / working directory", line=37, cnline=38,
                       arity=1, values="1 | 2 | -1", default=None, requires=[], conflicts=[],
                       semantics="1 excludes taxa with 1 occurrence, 2 excludes taxa with <= 2, "
                                 "-1 excludes extant taxa"),
    "-A": dict(section="main analysis settings", line=46, cnline=47,
               arity=1, values="0 | 1 | 2 | 3", default="2", requires=[], conflicts=[],
               semantics="0 MCMC fixed shifts, 1 MCMC + TI marginal likelihood, "
                         "2 BDMCMC (default), 3 MCMC with Dirichlet Process Prior (still being tested)"),
    "-n": dict(section="main analysis settings", line=56, cnline=57,
               arity=1, values="int (generations)", default="10000000", requires=[], conflicts=[],
               semantics="number of MCMC or BDMCMC generations"),
    "-s": dict(section="main analysis settings", line=60, cnline=61,
               arity=1, values="int", default="1000", requires=[], conflicts=[],
               semantics="MCMC sampling frequency"),
    "-p": dict(section="main analysis settings", line=64, cnline=65,
               arity=1, values="int", default=None, requires=[], conflicts=[],
               semantics="MCMC print-on-screen frequency"),
    "-b": dict(section="main analysis settings", line=68, cnline=69,
               arity=1, values="int >= 1 (iterations) OR 0 < x < 1 (fraction of -n)", default="0",
               requires=[], conflicts=[],
               semantics="burn-in discarded (not logged); required to be sensible under -A 1 (TI)"),
    "-thread": dict(section="main analysis settings", line=75, cnline=76,
                    arity=2, values="int int (birth-death, NHPP)", default="0 0",
                    requires=[], conflicts=[],
                    semantics="threads for the BD likelihood and the NHPP likelihood; 0 0 = sequential"),
    "-mHPP": dict(section="preservation model", line=87, cnline=88,
                  arity=0, values="(switch)", default=None, requires=[], conflicts=["-qShift"],
                  semantics="homogeneous Poisson process instead of the default NHPP"),
    "-qShift": dict(section="preservation model", line=91, cnline=92,
                    arity=1, values="path to a file of epoch-boundary times", default=None,
                    requires=[], conflicts=["-mHPP"],
                    semantics="time-variable Poisson process (TPP): preservation constant within epochs"),
    "-mG": dict(section="preservation model", line=95, cnline=96,
                arity=0, values="(switch)", default=None, requires=[], conflicts=[],
                semantics="Gamma model of across-taxon preservation heterogeneity (alpha estimated)"),
    "-ncat": dict(section="preservation model", line=100, cnline=100,
                  arity=1, values="int", default="4", requires=["-mG"], conflicts=[],
                  semantics="number of gamma categories; only used with -mG"),
    "-fixSE": dict(section="preservation model", line=104, cnline=104,
                   arity=1, values="path to a *_mcmc.log file, or the literal word null", default=None,
                   requires=[], conflicts=[],
                   semantics="fix times of speciation/extinction from a previous analysis "
                             "(or from first/last appearances when set to null)"),
    "-mL": dict(section="birth-death constrained shifts", line=111, cnline=111,
                arity=1, values="int", default=None, requires=[], conflicts=[],
                semantics="number of speciation rates through time (shifts = values - 1)"),
    "-mM": dict(section="birth-death constrained shifts", line=115, cnline=115,
                arity=1, values="int", default=None, requires=[], conflicts=[],
                semantics="number of extinction rates through time (shifts = values - 1)"),
    "-mC": dict(section="birth-death constrained shifts", line=119, cnline=119,
                arity=0, values="(switch)", default=None,
                requires=["-mL >= 2 or -mM >= 2"], conflicts=[],
                semantics="constrain the time frames of speciation and extinction rates to be equal"),
    "-fixShift": dict(section="birth-death constrained shifts", line=123, cnline=123,
                      arity=1, values="path to a text file of shift ages", default=None,
                      requires=[], conflicts=["-mL", "-mM"],
                      semantics="fix number and ages of shifts, identical for speciation and "
                                "extinction; switches the BD priors to half-Cauchy"),
    "-trait_file": dict(section="trait-correlated rates (Covar)", line=132, cnline=132,
                        arity=1, values="path to a tab-separated Species/Trait table (NA allowed)",
                        default=None, requires=[], conflicts=[],
                        semantics="trait values supplied as a separate file instead of the input file"),
    "-mCov": dict(section="trait-correlated rates (Covar)", line=137, cnline=137,
                  arity=1, values="1 | 2 | 3 | 4 | 5", default=None, requires=["trait data"],
                  conflicts=[],
                  semantics="1 sp, 2 ex, 3 sp+ex, 4 preservation, 5 sp+ex+preservation rate correlated "
                            "with the trait"),
    "-trait": dict(section="trait-correlated rates (Covar)", line=146, cnline=146,
                   arity=1, values="int (trait number)", default="1", requires=[], conflicts=[],
                   semantics="which trait of a multi-trait input file is analysed"),
    "-logT": dict(section="trait-correlated rates (Covar)", line=150, cnline=150,
                  arity=1, values="0 | 1 | 2", default="2", requires=[], conflicts=[],
                  semantics="0 no transformation, 1 log_e, 2 log10"),
    "-N": dict(section="(hyper)prior settings", line=162, cnline=162,
               arity=1, values="int >= 0, or -1", default="-1 (gamma prior route)",
               requires=[], conflicts=["-pL", "-pM"],
               semantics="number of extant species; conditions the BD hyperprior on present diversity"),
    "-pL": dict(section="(hyper)prior settings", line=166, cnline=166,
                arity=2, values="float float (shape scale)", default="1.1 1.1", requires=["-N -1"],
                conflicts=[],
                semantics="gamma prior on the speciation rate; only when -N -1 / not specified"),
    "-pM": dict(section="(hyper)prior settings", line=170, cnline=170,
                arity=2, values="float float (shape scale)", default=None, requires=["-N -1"],
                conflicts=[],
                semantics="gamma prior on the extinction rate; the page's example line for -pM "
                          "misprints '-pL 1.1 1.1'"),
    "-cauchy": dict(section="(hyper)prior settings", line=174, cnline=174,
                    arity=2, values="float float (-1 -1 | 0 0 | x y > 0)", default="-1 -1",
                    requires=[], conflicts=[],
                    semantics="half-Cauchy hyper priors on speciation/extinction rates; "
                              "0 0 infers the scales (default with -fixShift)"),
    "-pP": dict(section="(hyper)prior settings", line=178, cnline=177,
                arity=2, values="float float (shape scale)", default="1.5 1", requires=[], conflicts=[],
                semantics="gamma prior on the preservation rate"),
    "-pS": dict(section="(hyper)prior settings", line=182, cnline=181,
                arity=1, values="float", default="2.5", requires=[], conflicts=[],
                semantics="shape of the Dirichlet prior on the relative length of the time frames"),
    "-pC": dict(section="(hyper)prior settings", line=186, cnline=185,
                arity=1, values="float >= 0", default="1", requires=["-mCov with >= 2 correlations"],
                conflicts=[],
                semantics="sd of the Normal(0, sd) prior on the correlation parameters; "
                          "0 estimates the sd from the data with a G(2,2) hyper-prior"),
    "-r": dict(section="advanced (BD)MCMC settings", line=193, cnline=192,
               arity=1, values="int (chains, cold chain included)", default=None,
               requires=["-A 0"], conflicts=[],
               semantics="number of heated chains for MC3; only with -A 0"),
    "-t": dict(section="advanced (BD)MCMC settings", line=197, cnline=196,
               arity=1, values="float", default="0.03", requires=["-r > 1"], conflicts=[],
               semantics="temperature of the MC3 heated chains; only with -r > 1"),
    "-sw": dict(section="advanced (BD)MCMC settings", line=201, cnline=200,
                arity=1, values="int", default="100", requires=["-r > 1"], conflicts=[],
                semantics="frequency of attempted chain swaps in MC3; only with -r > 1"),
    "-k": dict(section="advanced (BD)MCMC settings", line=205, cnline=204,
               arity=1, values="int", default="10", requires=["-A 1"], conflicts=[],
               semantics="number of scaling factors for TI marginal-likelihood estimation; only with -A 1"),
    "-a": dict(section="advanced (BD)MCMC settings", line=209, cnline=208,
               arity=1, values="float", default="0.3", requires=["-A 1"], conflicts=[],
               semantics="shape of the beta-distributed scaling factors in TI; only with -A 1"),
    "-M": dict(section="advanced (BD)MCMC settings", line=213, cnline=212,
               arity=1, values="int", default="25", requires=["-A 2"], conflicts=[],
               semantics="frequency of model update in BDMCMC; only with -A 2"),
    "-B": dict(section="advanced (BD)MCMC settings", line=217, cnline=216,
               arity=1, values="float", default="1", requires=["-A 2"], conflicts=[],
               semantics="birth-rate at which BDMCMC proposes new shifts = shape of the Poisson prior "
                         "on the number of rates; only with -A 2"),
    "-T": dict(section="advanced (BD)MCMC settings", line=221, cnline=220,
               arity=1, values="float", default="1", requires=["-A 2"], conflicts=[],
               semantics="time spent updating the model in BDMCMC; only with -A 2"),
    "-S": dict(section="advanced (BD)MCMC settings", line=225, cnline=224,
               arity=1, values="int", default=None, requires=["-A 2"], conflicts=[],
               semantics="generation after which BDMCMC starts updating the model; only with -A 2"),
    "-multiR": dict(section="tuning parameters", line=231, cnline=230,
                    arity=1, values="0 | 1", default="1", requires=[], conflicts=[],
                    semantics="0 sliding-window, 1 multiplier proposals for speciation/extinction rates"),
    "-tT": dict(section="tuning parameters", line=235, cnline=234,
                arity=1, values="float", default="1", requires=[], conflicts=[],
                semantics="window size of speciation/extinction time updates"),
    "-nT": dict(section="tuning parameters", line=239, cnline=238,
                arity=1, values="int >= 0", default="5", requires=[], conflicts=["-mHPP", "-qShift", "-mG"],
                semantics="max number of SE times updated at a time; 0 sets SE times to first/last "
                          "appearances AND forces the preservation model to HPP"),
    "-tQ": dict(section="tuning parameters", line=243, cnline=242,
                arity=2, values="float float (q, alpha)", default="1.2 1.2", requires=[], conflicts=[],
                semantics="window sizes of the preservation rate and of the gamma heterogeneity alpha"),
    "-tR": dict(section="tuning parameters", line=247, cnline=246,
                arity=1, values="float", default="0.05", requires=[], conflicts=[],
                semantics="window size of speciation/extinction rate updates"),
    "-tS": dict(section="tuning parameters", line=251, cnline=250,
                arity=1, values="float", default="1", requires=[], conflicts=[],
                semantics="window size of shift-time updates"),
    "-fS": dict(section="tuning parameters", line=255, cnline=254,
                arity=1, values="float", default="0.7", requires=[], conflicts=[],
                semantics="frequency of updating shift times while updating BD parameters; "
                          "auto-set to 0 when no shifts are sampled or shift times are fixed"),
    "-tC": dict(section="tuning parameters", line=259, cnline=258,
                arity=3, values="float float float (sp, ex, q)", default="0.025 0.025 0.1",
                requires=["-mCov"], conflicts=[],
                semantics="window sizes of the correlation-parameter updates"),
    "-fU": dict(section="tuning parameters", line=263, cnline=262,
                arity=3, values="float float float (preservation, BD, Covar)",
                default="0.02 0.18 0.08 under the Covar model", requires=[], conflicts=[],
                semantics="update frequencies; the remainder updates speciation/extinction times"),
    "-fR": dict(section="tuning parameters", line=267, cnline=266,
                arity=1, values="float <= 1", default="1", requires=[], conflicts=[],
                semantics="fraction of BD rates updated at a time; lower it to improve mixing "
                          "in models with many shifts"),
}

# Commands that other pages of this corpus print but that are NOT on the
# command-list page.  Values are the mirror path (relative to the skill folder)
# and the line whose example line shows the command.
KNOWN_ELSEWHERE = {
    "-fast_burnin":   ("../pyrate-mcmc-tuning/references/tutorial-6.md", 13),
    "-log_sp_q_rates": ("../pyrate-bd-analysis/references/tutorial-1.md", 151),
    "-PPmodeltest":   ("../pyrate-bd-analysis/references/tutorial-1.md", 156),
    "-edgeShift":     ("../pyrate-bd-analysis/references/tutorial-1.md", 267),
    "-min_dt":        ("../pyrate-rjmcmc/references/tutorial-3.md", 46),
    "-bound_se":      ("../pyrate-rjmcmc/references/tutorial-3.md", 142),
    "-se_gibbs":      ("../pyrate-rjmcmc/references/tutorial-3.md", 115),
    "-plotRJ":        ("../pyrate-rjmcmc/references/tutorial-3.md", 73),
    "-combLogRJ":     ("../pyrate-rjmcmc/references/tutorial-3.md", 99),
    "-combLog":       ("../pyrate-bd-analysis/references/tutorial-1.md", 227),
    "-mProb":         ("../pyrate-bd-analysis/references/tutorial-1.md", 211),
    "-plotQ":         ("../pyrate-bd-analysis/references/tutorial-1.md", 241),
    "-data_info":     ("../pyrate-summarize-results/references/summarize-results.md", 9),
    "-plot":          ("../pyrate-summarize-results/references/summarize-results.md", 39),
    "-plot2":         ("../pyrate-summarize-results/references/summarize-results.md", 45),
    "-tag":           ("../pyrate-summarize-results/references/summarize-results.md", 53),
    "-root_plot":     ("../pyrate-summarize-results/references/summarize-results.md", 58),
    "-ginput":        ("../pyrate-continuous-covariates/references/tutorial-2.md", 29),
    "-resample":      ("../pyrate-continuous-covariates/references/tutorial-2.md", 55),
    "-ltt":           ("../pyrate-continuous-covariates/references/tutorial-2.md", 68),
    "-grid_plot":     ("../pyrate-continuous-covariates/references/tutorial-2.md", 86),
    "-BDNNmodel":     ("../pyrate-bdnn/references/tutorial-bdnn.md", 55),
    # BDNN post-processing and model settings (tutorial 7), all on PyRate.py;
    # arities mirror build_command.EXTENSIONS and are verified by --self-test
    "-BDNNtimevar":   ("../pyrate-bdnn/references/tutorial-bdnn.md", 205),
    "-BDNNtimetrait": ("../pyrate-bdnn/references/tutorial-bdnn.md", 223),
    "-BDNNtimeres":   ("../pyrate-bdnn/references/tutorial-bdnn.md", 238),
    "-BDNNnodes":     ("../pyrate-bdnn/references/tutorial-bdnn.md", 381),
    "-BDNNactfun":    ("../pyrate-bdnn/references/tutorial-bdnn.md", 385),
    "-BDNNoutputfun": ("../pyrate-bdnn/references/tutorial-bdnn.md", 383),
    "-BDNNreg":       ("../pyrate-bdnn/references/tutorial-bdnn.md", 387),
    "-BDNNprecision": ("../pyrate-bdnn/references/tutorial-bdnn.md", 389),
    "-qFilter":       ("../pyrate-bdnn/references/tutorial-bdnn.md", 394),
    "-BDNN_groups":   ("../pyrate-bdnn/references/tutorial-bdnn.md", 303),
    "-BDNN_mean_shap_per_group":
                      ("../pyrate-bdnn/references/tutorial-bdnn.md", 366),
    "-BDNNpath_taxon_time_tables":
                      ("../pyrate-bdnn/references/tutorial-bdnn.md", 410),
    "-BDNNexport_taxon_time_tables":
                      ("../pyrate-bdnn/references/tutorial-bdnn.md", 425),
    "-restore_mcmc":  ("../pyrate-bdnn/references/tutorial-bdnn.md", 433),
    "-combBDNN":      ("../pyrate-bdnn/references/tutorial-bdnn.md", 453),
    "-plotBDNN":      ("../pyrate-bdnn/references/tutorial-bdnn.md", 59),
    "-plotBDNN_groups": ("../pyrate-bdnn/references/tutorial-bdnn.md", 271),
    "-plotBDNN_effects": ("../pyrate-bdnn/references/tutorial-bdnn.md", 71),
    "-plotBDNN_transf_features":
                      ("../pyrate-bdnn/references/tutorial-bdnn.md", 301),
    "-BDNN_interaction": ("../pyrate-bdnn/references/tutorial-bdnn.md", 312),
    "-BDNN_interaction_fix": ("../pyrate-bdnn/references/tutorial-bdnn.md", 334),
    "-BDNN_pred_importance": ("../pyrate-bdnn/references/tutorial-bdnn.md", 344),
    "-BDNN_pred_importance_nperm":
                      ("../pyrate-bdnn/references/tutorial-bdnn.md", 358),
    "-BDNN_pred_importance_interaction":
                      ("../pyrate-bdnn/references/tutorial-bdnn.md", 360),
    "-BDNN_pred_importance_window_size":
                      ("../pyrate-bdnn/references/tutorial-bdnn.md", 362),
    "-BDNN_nsim_expected_cv": ("../pyrate-bdnn/references/tutorial-bdnn.md", 356),
    "-min_age_plot":  ("../pyrate-bdnn/references/tutorial-bdnn.md", 305),
    # ADE / BDC (tutorial 4 of the Covar/ADE page); -var belongs to the MBD
    # program and is deliberately NOT indexed here (this table is PyRate.py only)
    "-ADE":           ("../pyrate-trait-age-models/references/tutorial-4.md", 143),
    "-filter":        ("../pyrate-trait-age-models/references/tutorial-4.md", 145),
    "-tree":          ("../pyrate-trait-age-models/references/tutorial-4.md", 158),
    "-bdc":           ("../pyrate-trait-age-models/references/tutorial-4.md", 163),
    "-eqr":           ("../pyrate-trait-age-models/references/tutorial-4.md", 163),
    "-root_age":      ("../pyrate-summarize-results/references/summarize-results.md", 61),
    "-v":             ("../pyrate-installation/references/virtual-environment.md", 49),
}

# -A value -> (mode name, extra commands this page restricts to that mode)
ANALYSIS_MODES = {
    "0": ("MCMC with a fixed number of shifts (parameter estimation)",
          ["-r"], ["-mL", "-mM", "-mC"]),
    "1": ("MCMC with thermodynamic integration (marginal likelihood)",
          ["-k", "-a"], ["-mL", "-mM", "-mC"]),
    "2": ("BDMCMC (number and placement of shifts estimated) - documented default",
          ["-M", "-B", "-T", "-S"], ["-mL", "-mM"]),
    "3": ("MCMC with a Dirichlet Process Prior in fixed time bins (page: still being tested)",
          [], []),
}

SECTIONS = [
    "input files / working directory",
    "main analysis settings",
    "preservation model",
    "birth-death constrained shifts",
    "trait-correlated rates (Covar)",
    "(hyper)prior settings",
    "advanced (BD)MCMC settings",
    "tuning parameters",
]


def is_number(tok):
    try:
        float(tok)
        return True
    except (TypeError, ValueError):
        return False


def sorted_commands():
    """All commands in page order (by mirror line number)."""
    return sorted(COMMANDS.items(), key=lambda kv: kv[1]["line"])


# --------------------------------------------------------------------- helpers

HEADING_RE = re.compile(r"^#{5}[ \t]*`?([^`]*)`?[ \t]*$")
ANY_HEADING_RE = re.compile(r"^#{3,6}[ \t]")


def read_lines(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read().splitlines()


def looks_like_value(tok):
    """Same rule build_command.py uses to tokenise mirror example lines."""
    return bool(re.fullmatch(r"-?\d+(\.\d+)?", tok)
                or re.search(r"[/_.\\]", tok)
                or len(tok) <= 2
                or tok.lower() in ("null", "inf"))


def block_example_arities(lines, start_line, flag):
    """Arities shown by `flag` example lines inside its own block of the page.

    start_line: 1-based line of the `#####` heading. Returns a set of ints
    (possibly empty when the block states no example).
    """
    out = set()
    i = start_line  # 0-based index of the line after the heading
    while i < len(lines):
        line = lines[i]
        if i > start_line - 1 and (ANY_HEADING_RE.match(line)
                                   or line.startswith("***")):
            break
        for span in re.findall(r"`([^`]*)`", line) + [line]:
            for m in re.finditer(re.escape(flag) + r"\b(.*)", span):
                toks = []
                for t in m.group(1).split(" "):
                    if not t:
                        continue
                    if not looks_like_value(t):
                        break
                    toks.append(t)
                if toks or m.group(1).strip() == "":
                    out.add(len(toks))
        i += 1
    return out


def resolve_elsewhere(rel_path):
    return os.path.normpath(os.path.join(SUITE_DIR, rel_path.split("../", 1)[1]))


# ------------------------------------------------------------------ self test

def self_test(verbose=False):
    failures = []
    checks = [0]

    def check(cond, msg):
        checks[0] += 1
        if not cond:
            failures.append(msg)

    try:
        en = read_lines(EN_MIRROR)
        cn = read_lines(CN_MIRROR)
    except (IOError, OSError) as exc:
        print("pyrate_commands.py self-test: FAIL (mirrors unreadable: %s)" % exc)
        return 1

    # 1. every COMMANDS row points at its own heading, EN and CN
    for key, spec in sorted(COMMANDS.items()):
        name = key.strip("`")
        check(0 < spec["line"] <= len(en),
              "%s: EN line %d out of range" % (key, spec["line"]))
        if 0 < spec["line"] <= len(en):
            m = HEADING_RE.match(en[spec["line"] - 1])
            check(bool(m) and m.group(1).strip() == name,
                  "%s: %s:%d is %r, not its '#####' heading"
                  % (key, PAGE, spec["line"], en[spec["line"] - 1]))
        check(0 < spec["cnline"] <= len(cn),
              "%s: CN line %d out of range" % (key, spec["cnline"]))
        if 0 < spec["cnline"] <= len(cn):
            m = HEADING_RE.match(cn[spec["cnline"] - 1])
            check(bool(m) and m.group(1).strip() == name,
                  "%s: command-list-cn.md:%d is %r, not its heading"
                  % (key, spec["cnline"], cn[spec["cnline"] - 1]))
        # arity: when the block prints an example, the row must match one of
        # the arities the examples show (empty set = page states no example,
        # e.g. -pM, whose printed example is the docs copy-paste typo)
        if key.startswith("-"):
            arities = block_example_arities(en, spec["line"], key)
            check(not arities or spec["arity"] in arities,
                  "%s: row says arity %s but the mirror's examples show %s"
                  % (key, spec["arity"], sorted(arities)))
            if spec["default"] is not None:
                block = " ".join(en[spec["line"]:spec["line"] + 12])
                check("default" in block,
                      "%s: row claims default %r but the block never says "
                      "'default'" % (key, spec["default"]))
        for other in spec["requires"] + spec["conflicts"]:
            if other in ("<input file>", "trait data"):
                continue
            check(other.startswith("-"),
                  "%s: requires/conflicts names unknown command %r" % (key, other))
            base = other.split(" ")[0]  # "-A 2", "-r > 1", "-mL >= 2 or ..." :
            check(base in COMMANDS or base in KNOWN_ELSEWHERE,
                  "%s: requires/conflicts names unknown command %r" % (key, other))
        check(spec["section"] in SECTIONS,
              "%s: section %r is not in SECTIONS" % (key, spec["section"]))

    # 2. SECTIONS are exactly the page's ### headings, in page order
    headings = [l[4:].strip() for l in en if l.startswith("### ")]
    check(len(headings) == len(SECTIONS),
          "SECTIONS lists %d sections but the page prints %d: %r"
          % (len(SECTIONS), len(headings), headings))

    # 3. every KNOWN_ELSEWHERE citation resolves: file exists, line in range,
    #    and the cited line actually contains the flag
    for flag, (rel, line) in sorted(KNOWN_ELSEWHERE.items()):
        path = resolve_elsewhere(rel)
        try:
            lines = read_lines(path)
        except (IOError, OSError):
            failures.append("%s: cited file missing: %s" % (flag, rel))
            checks[0] += 1
            continue
        checks[0] += 1
        if not 0 < line <= len(lines):
            failures.append("%s: %s:%d out of range (file has %d lines)"
                            % (flag, rel, line, len(lines)))
            continue
        check(flag in lines[line - 1],
              "%s: not on the cited line %s:%d — %r"
              % (flag, rel, line, lines[line - 1][:90]))
        check(flag not in COMMANDS,
              "%s: listed BOTH on the command-list page and elsewhere" % flag)

    # 4. ANALYSIS_MODES sanity
    check(set(ANALYSIS_MODES) == {"0", "1", "2", "3"},
          "ANALYSIS_MODES must cover -A 0..3, got %s" % sorted(ANALYSIS_MODES))
    for mode, (_n, req, conf) in ANALYSIS_MODES.items():
        for other in req + conf:
            check(other in COMMANDS,
                  "ANALYSIS_MODES[%s] names unknown command %r" % (mode, other))

    if failures:
        for f in failures:
            print("pyrate_commands.py self-test FAIL: %s" % f)
        print("pyrate_commands.py self-test: FAILED (%d checks, %d failures)"
              % (checks[0], len(failures)))
        return 1
    print("pyrate_commands.py self-test: OK (%d checks: %d command rows verified "
          "against %s and its CN twin, %d off-page citations verified)"
          % (checks[0], len(COMMANDS), PAGE, len(KNOWN_ELSEWHERE)))
    return 0


# -------------------------------------------------------------------- command

def format_row(key, spec):
    return ("%-28s section=%s | EN line %d, CN line %d | arity=%s | default=%s\n"
            "    values  : %s\n"
            "    semantics: %s\n"
            "    requires=%s conflicts=%s"
            % (key, spec["section"], spec["line"], spec["cnline"],
               spec["arity"], spec["default"], spec["values"],
               spec["semantics"], ",".join(spec["requires"]) or "-",
               ",".join(spec["conflicts"]) or "-"))


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="pyrate_commands.py",
        description="Machine-readable index of the PyRate.py command list "
                    "(transcribed from references/command-list.md). Prints the "
                    "full index, or the rows for the named commands.")
    ap.add_argument("commands", nargs="*",
                    help="command names to look up, with or without the leading -")
    ap.add_argument("--elsewhere", action="store_true",
                    help="list the commands documented off the command-list page")
    ap.add_argument("--modes", action="store_true",
                    help="list the -A analysis modes and their restricted commands")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--self-test", action="store_true",
                    help="re-verify every row and citation against the mirrors")
    ns = ap.parse_args(argv)

    if ns.self_test:
        return self_test()

    import json
    if ns.json:
        payload = {"page": PAGE, "commands": COMMANDS,
                   "known_elsewhere": KNOWN_ELSEWHERE,
                   "analysis_modes": ANALYSIS_MODES, "sections": SECTIONS}
        print(json.dumps(payload, indent=1, sort_keys=True))
        return 0
    if ns.elsewhere:
        for flag, (rel, line) in sorted(KNOWN_ELSEWHERE.items()):
            print("%-34s %s:%d" % (flag, rel, line))
        return 0
    if ns.modes:
        for mode in sorted(ANALYSIS_MODES):
            name, req, conf = ANALYSIS_MODES[mode]
            print("-A %s  %s | restricted-to: %s | off-limits: %s"
                  % (mode, name, ",".join(req) or "-", ",".join(conf) or "-"))
        return 0
    if ns.commands:
        rc = 0
        for c in ns.commands:
            key = c if c.startswith("-") or c.startswith("<") else "-" + c
            if key in COMMANDS:
                print(format_row(key, COMMANDS[key]))
            elif key in KNOWN_ELSEWHERE:
                rel, line = KNOWN_ELSEWHERE[key]
                print("%s: NOT on %s; documented at %s:%d" % (key, PAGE, rel, line))
            else:
                print("%s: no such command in this index "
                      "(run with --list-style lookup or --elsewhere)" % key)
                rc = 1
        return rc
    current = None
    for key, spec in sorted_commands():
        if spec["section"] != current:
            current = spec["section"]
            print("\n== %s ==" % current)
        print(format_row(key, spec))
    return 0


if __name__ == "__main__":
    sys.exit(main())
