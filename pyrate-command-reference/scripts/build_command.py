#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""build_command.py — assemble a validated `python PyRate.py <input> [commands]` line.

Part of the PyRate-skills suite (skill: pyrate-command-reference).
Python 3 standard library only. Deterministic, offline, never executes PyRate.

TRUTH SOURCE
  The command set is PARSED AT RUNTIME from the mirror
  <skill>/references/command-list.md: every `##### -X` heading declares a
  command; every example of the form `-X tok1 tok2` in its block gives its arity.
  Nothing about the CORE set is hardcoded that the mirror could contradict —
  if the mirror changes, the accepted flag list changes with it. The page lists
  the commands of PyRate.py, and that is the ONLY grammar this tool carries:
  --program refuses every other program of the family (see GRAMMAR SCOPE below).
  Commands documented ONLY elsewhere in the corpus (-A 4, -data_info,
  -check_names, -mProb, -plot, -plot2, -plotQ, -combLog, -tag, -ginput,
  -resample, -ltt, -grid_plot, -edgeShift, -log_sp_q_rates, -PPmodeltest, -BF,
  the BDNN family of tutorial 7, the RJMCMC family of tutorial 3, the ADE/BDC
  family of tutorial 4, -fast_burnin, -root_plot/-root_age/-min_age_plot,
  -v, -var) are carried in a cited EXTENSIONS table; every entry names its own
  <file>.md:LINE citation, every citation (file, line, verbatim quote) is
  re-verified against the on-disk mirrors by --self-test, and every arity is
  taken from a documented usage line (variadic arities carry the corpus's own
  minimum and maximum; where the corpus documents no arity the message says
  so). Pass --core-only to refuse them.

  CORPUS REPLAY. --self-test also re-assembles EVERY `python [path/]PyRate.py`
  command line found inside fenced code blocks of the suite's SKILL.md and
  references/*.md files: each line (backslash continuations joined) is
  shlex-tokenised, every flag token must be in the accepted set, and the token
  tail must assemble through build() without a usage error. A documented line
  that cannot be assembled fails the test loudly; a line may only be skipped if
  it sits in REPLAY_ALLOW with a printed reason (the allow-list itself is
  checked: an entry that matches nothing is a failure).

  Conditional-combination rules (e.g. "-ncat" is "used only when running under a
  Gamma model of preservation (i.e. with -mG)", references/command-list.md:101)
  quote the mirror verbatim (whitespace-normalised, backticks removed) and cite
  file:line in every message.

USAGE EXAMPLES
  python3 build_command.py Ursidae_PyRate.py -A 2 -mG -j 1
  python3 build_command.py canis_PyRate.py -qShift epochs_q.txt -mG -ncat 4 --dry-run
  python3 build_command.py --json Ursidae_PyRate.py -mHPP -mL 2 -mM 2 -mC
  python3 build_command.py -d Ursidae_SE.txt -ltt 1
  python3 build_command.py -mProb Canis_mcmc.log -b 200
  python3 build_command.py --list          # parsed command set + arities + citations
  python3 build_command.py --self-test

OWN OPTIONS (any other -X token is treated as a PyRate command)
  --mirror PATH      command mirror to parse (default <skill>/references/command-list.md)
  --list             print the accepted command set with arities and citations
  --core-only        refuse the commands documented outside the command list
  --json             emit one JSON object instead of the text report
  --dry-run          add the per-command validation report to the output
  --self-test        re-verify every quotation and replay every documented command line
  --python-exe EXE   launcher token written first in the assembled line (default python)
  --program NAME     program token written second in the assembled line. DEFAULT AND
                     ONLY ACCEPTED VALUE: PyRate.py (any path to it is fine, e.g.
                     --program ./PyRate.py). See GRAMMAR SCOPE below - the option is
                     not a grammar switch and any other program is refused.
  --help             print this text

GRAMMAR SCOPE (why --program refuses the other programs of the family)
  The tool carries ONE grammar: the commands parsed from references/command-list.md,
  which is the option list of PyRate.py. The sibling programs document their own
  options elsewhere, and those options are not in the accepted set - e.g.
  PyRateContinuous.py documents "-c" (a table of a variable and its times of change),
  "-m" with values -1/0/1 and "-DD", and offers only "-A 0" and "-A 1"
  (../pyrate-continuous-covariates/references/pyratecontinuous.md:31, :34-38, :28,
  :26); PyRateDES.py documents "-fossil", "-recent", "-bin_size", "-rep", "-timeline"
  (../pyrate-des/references/tutorial-5.md:63, :89). --self-test asserts that none of
  those flags is accepted here, so renaming the program could only ever produce a
  line that was validated - and silently mis-validated - against PyRate.py's page.
  Where each program's own options are documented: see PROGRAM_DOCS below; the
  refusal message prints the same table.

WHAT IT PRINTS
  [ERROR]/[WARN]/[NOTE] lines with quoted doc evidence, then (on success)
  `COMMAND: python PyRate.py <input> -A 2 ...`. --dry-run adds a per-command
  validation report. --json emits one object {command_line, errors, warnings,
  notes, mode, ...}. Nothing is executed in any mode; this tool assembles and
  validates only.

EXIT CODES
  0 valid line assembled (warnings possible), 2 validation error (rejected
  combination / bad value / missing input), 3 mirror missing or unparsable,
  4 argparse usage error (unknown flag or wrong number of values) or a --program
  whose grammar this tool does not carry (see GRAMMAR SCOPE).
"""

import argparse
import json
import os
import re
import shlex
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))
SUITE_DIR = os.path.normpath(os.path.join(SKILL_DIR, ".."))
DEFAULT_MIRROR = os.path.join(SKILL_DIR, "references", "command-list.md")
MIRROR_LABEL = "references/command-list.md"   # how citations are shown to the user

# GRAMMAR SCOPE. This tool validates the options of PyRate.py and nothing else:
# the accepted set is parsed from references/command-list.md, the page that lists
# PyRate.py's commands. --program therefore accepts PyRate.py only (in any path
# form); every other program of the family is refused with the table below, which
# names the page that documents its own options. --self-test re-checks that each
# page exists and mentions its program, and that none of the foreign flags listed
# in FOREIGN_FLAGS is accepted here.
SUPPORTED_PROGRAM = "PyRate.py"
PROGRAM_DOCS = [
    ("PyRateContinuous.py",
     "../pyrate-continuous-covariates/references/pyratecontinuous.md"),
    ("PyRateMCDD.py", "../pyrate-diversity-dependence/references/tutorial-4.md"),
    ("PyRateMBD.py", "../pyrate-diversity-dependence/references/tutorial-4.md"),
    ("PyRateDES.py", "../pyrate-des/references/tutorial-5.md"),
    ("PyRateDES2.py", "../pyrate-des/references/tutorial-5.md"),
]
# flags documented for those programs and NOT part of the PyRate.py command set
FOREIGN_FLAGS = ("c", "m", "DD", "fossil", "recent", "bin_size", "rep", "timeline")


def shown_path(path):
    """Show the default mirror under the name it is cited by, not under an install path."""
    return MIRROR_LABEL if os.path.abspath(str(path)) == DEFAULT_MIRROR else str(path)


def program_ok(name):
    """True if NAME is PyRate.py (a path to it is fine) - the only grammar carried."""
    return os.path.basename(str(name)) == SUPPORTED_PROGRAM


def program_refusal(name):
    """[ERROR] lines for a --program whose grammar this tool does not carry.

    No command line is emitted (render() prints COMMAND only when rc == 0), so a
    refusal can never be mistaken for a validated line: the tool exits 4 and prints
    the program it does support plus the pages that document the other programs'
    own options. --self-test checks all of that, including that every page named
    here exists and mentions its program.
    """
    lines = [
        "[ERROR] --program %s is refused: this tool carries the %s grammar only - the "
        "flags it accepts are parsed from %s, which lists %s's commands - so it cannot "
        "validate any other program's line. Passing --program only renames the program "
        "token, it does not switch grammars; emitting anyway would print a line checked "
        "against the wrong page."
        % (name, SUPPORTED_PROGRAM, MIRROR_LABEL, SUPPORTED_PROGRAM),
        "[ERROR] supported: --program %s (any path to it, e.g. --program ./%s)."
        % (SUPPORTED_PROGRAM, SUPPORTED_PROGRAM),
        "[ERROR] where the other programs' own options are documented:",
    ]
    for prog, rel in PROGRAM_DOCS:
        lines.append("           %-19s %s" % (prog, rel))
    return lines


KIND_INT, KIND_FLOAT, KIND_FLAG, KIND_PATH, KIND_STR = \
    "int", "float", "flag", "path", "string"

# ----------------------------------------------------------------- corpus evidence
# key -> (mirror path as cited, line, quote found there after norm() normalisation)
BD = "../pyrate-bdnn/references/tutorial-bdnn.md"
RJ = "../pyrate-rjmcmc/references/tutorial-3.md"
T4 = "../pyrate-trait-age-models/references/tutorial-4.md"
CITE = {
    "invocation":    (MIRROR_LABEL, 15,  "python PyRate.py path_to_input_file/Ursidae_PyRate.py"),
    "inputfile":     (MIRROR_LABEL, 13,  "The file is a Python file with the fossil occurrence data (as list of Numpy arrays) and, optionally, one or more continuous traits."),
    "d":             (MIRROR_LABEL, 18,  "This option automatically sets -fixSE = null"),
    "dtable":        (MIRROR_LABEL, 18,  "The table should be formatted as tab-separated text file with the first line containing column headers followed by one row for each species."),
    "dalt":          (MIRROR_LABEL, 18,  "Alternatively to the python input file with occurrence data, users can provide a table with the times of origin and extinction of each species."),
    "jdefault":      (MIRROR_LABEL, 30,  "-j 1 (default; the first data set from the input file is analyzed)"),
    "singleton":     (MIRROR_LABEL, 40,  "-singleton 1 (excludes taxa with only 1 sampled occurrence)"),
    "datainfosync":  (MIRROR_LABEL, 38,  "This information is also available when using it together with the command"),
    "Adefault":      (MIRROR_LABEL, 52,  "-A 2 (default)"),
    "A3":            (MIRROR_LABEL, 54,  "Warning: this function is currently still being tested."),
    "b":             (MIRROR_LABEL, 71,  "-b 0 (default; all samples are logged)"),
    "bfraction":     (MIRROR_LABEL, 69,  "When set to a number between 0 and 1, it is interpreted as a fraction of the total number of MCMC generations."),
    "thread":        (MIRROR_LABEL, 78,  "-thread 0 0 (default; sequential likelihood calculation)"),
    "mHPP":          (MIRROR_LABEL, 88,  "Use homogeneous Poisson process for preservation rates instead of non-homogeneous Poisson process (NHPP)"),
    "qShift":        (MIRROR_LABEL, 92,  "To use this model you need to provide a file containing the times that delimit the different epochs"),
    "mG":            (MIRROR_LABEL, 97,  "This option can be applied to the NHPP, HPP, and TPP preservation models."),
    "ncat":          (MIRROR_LABEL, 101, "This command is used only when running under a Gamma model of preservation (i.e. with -mG)."),
    "ncatdefault":   (MIRROR_LABEL, 102, "-ncat 4 (default)"),
    "fixSE":         (MIRROR_LABEL, 105, "If set to -fixSE null first and last appearances are used as fixed times of speciation and extinction."),
    "mL":            (MIRROR_LABEL, 113, "-mL 2 (set 2 speciation rates and 1 rate shift)"),
    "mM":            (MIRROR_LABEL, 117, "-mM 3 (set 3 extinction rates and 2 rate shifts)"),
    "mC":            (MIRROR_LABEL, 120, "This command is only used in birth-death models with at least one rate shift (e.g. with -mL 2 and -mM 2) and"),
    "fixShift":      (MIRROR_LABEL, 124, "This should be simply a text file with the ages at which the rate shifts should be fixed"),
    "traitfile":     (MIRROR_LABEL, 133, "The first column of the table should include the species names (identical to those used in the PyRate file), the second column provides the trait values"),
    "mCov1":         (MIRROR_LABEL, 140, "-mCov 1 correlated speciation rate"),
    "mCov3":         (MIRROR_LABEL, 142, "-mCov 3 correlated speciation and extinction rates"),
    "mCov5":         (MIRROR_LABEL, 144, "-mCov 5 correlated speciation, extinction, preservation rates"),
    "trait":         (MIRROR_LABEL, 148, "-trait 1 (default; it takes first trait)"),
    "logT":          (MIRROR_LABEL, 155, "-logT 2 trait is log10 transformed (default)"),
    "N":             (MIRROR_LABEL, 163, "If set to -N -1 or if not specified, a gamma prior will be used instead with shape and scale parameters defined by the flags -pL and -pM"),
    "pL":            (MIRROR_LABEL, 167, "This command if used only if the number of extant taxa is not specified (i.e. -N -1)."),
    "pM":            (MIRROR_LABEL, 171, "This command if used only if the number of extant taxa is not specified (i.e. -N -1)."),
    "pMtypo":        (MIRROR_LABEL, 172, "Example: -pL 1.1 1.1"),
    "cauchy":        (MIRROR_LABEL, 175, "Under -cauchy 0 0 (which is default when using"),
    "pP":            (MIRROR_LABEL, 180, "-pP 1.5 1 (default)"),
    "pC":            (MIRROR_LABEL, 187, "This option should only be used if at least 2 correlation parameters are being estimated, i.e. using [-mCov 2 or -mCov]"),
    "r":             (MIRROR_LABEL, 194, "This command is used only when running MCMC analysis for parameter estimation (i.e. with -A 0)."),
    "t":             (MIRROR_LABEL, 198, "This command is used only when running MC3 analysis (i.e. with -r >1)."),
    "sw":            (MIRROR_LABEL, 202, "This command is used only when running MC3 analysis (i.e. with -r >1)."),
    "k":             (MIRROR_LABEL, 206, "This command is used only when running TI analysis (i.e. with -A 1)."),
    "a":             (MIRROR_LABEL, 210, "This command is used only when running TI analysis (i.e. with -A 1)."),
    "M":             (MIRROR_LABEL, 214, "This command is used only when running BDMCMC analysis for parameter estimation (i.e. with -A 2)."),
    "B":             (MIRROR_LABEL, 218, "This command is used only when running BDMCMC analysis for parameter estimation (i.e. with -A 2)."),
    "T":             (MIRROR_LABEL, 222, "This command is used only when running BDMCMC analysis for parameter estimation (i.e. with -A 2)."),
    "S":             (MIRROR_LABEL, 226, "This command is used only when running BDMCMC analysis for parameter estimation (i.e. with -A 2)."),
    "multiR":        (MIRROR_LABEL, 232, "When -multiR 0 updates are done using sliding window, whereas -multiR 1 sets multiplier proposals."),
    "nT":            (MIRROR_LABEL, 240, "If set to 0, speciation/extinction times are set equal to first/last appearances and the preservation model is automatically set to HPP."),
    "fS":            (MIRROR_LABEL, 256, "The value will be automatically set to 0 when no rate shifts are being sampled or if the times of shifts are fixed"),
    "fU":            (MIRROR_LABEL, 265, "-fU 0.02 0.18 0.08 (default under Covar model;"),
    # documented outside the wiki command list:
    "data_info":     ("../pyrate-input-file/references/tutorial-1.md", 45,
                      "python PyRate.py '.../Canis_pbdb_data_PyRate.py' -data_info"),
    "check_names":   ("../pyrate-input-file/references/tutorial-1.md", 94,
                      "This is implemented in the function -check_names, which requires a text file containing one species name for each row."),
    "check_names2":  ("../pyrate-input-file/references/tutorial-1.md", 98,
                      "python PyRate.py -check_names .../PBDB_dataset_TaxonList.txt"),
    "logspq":        ("../pyrate-input-file/references/tutorial-1.md", 149,
                      "When combining a TPP model with a Gamma model you can log to a file the estimated relative preservation rate for each lineage. This is done by adding the flag -log_sp_q_rates"),
    "ppmodeltest":   ("../pyrate-input-file/references/tutorial-1.md", 154,
                      "To run the test you need to provide the input file and the file providing the times of rate shift for the TPP model and add the flag -PPmodeltest"),
    "A4":            ("../pyrate-input-file/references/tutorial-1.md", 174,
                      "using -A 4 (or omitting the flag) will set the algorithm to RJMCMC"),
    "mProb":         ("../pyrate-input-file/references/tutorial-1.md", 211,
                      "python PyRate.py -mProb .../Canis_pbdb_data_mcmc.log -b 200"),
    "plot":          ("../pyrate-input-file/references/tutorial-1.md", 218,
                      "python PyRate.py -plot .../Canis_pbdb_data_marginal_rates.log -b 200"),
    "plot2":         ("../pyrate-input-file/references/tutorial-1.md", 220,
                      "A slightly different flavor of the RTT plot can be obtained using the flag -plot2 instead of -plot."),
    "combLog":       ("../pyrate-input-file/references/tutorial-1.md", 227,
                      "PyRate.py -combLog path_to_your_log_files -tag mcmc -b 100"),
    "plotQ":         ("../pyrate-input-file/references/tutorial-1.md", 241,
                      "PyRate.py -plotQ .../Canis_pbdb_data_mcmc.log -qShift epochs.txt -b 100"),
    "plotQnote":     ("../pyrate-input-file/references/tutorial-1.md", 243,
                      "Note that the file with the times of rate shift (e.g. PyRate-master/example_files/epochs_q.txt) should be provided as well."),
    "edgeShift":     ("../pyrate-input-file/references/tutorial-1.md", 269,
                      "-edgeShift 18 2 sets fixed times of shifts at times 18 and 2"),
    "edgeShiftInf":  ("../pyrate-input-file/references/tutorial-1.md", 276,
                      "python PyRate.py <data_set> -A 4 -edgeShift inf 0"),
    "tag":           ("../pyrate-summarize-results/references/summarize-results.md", 54,
                      "Specify which files should be combined in the RTT plot."),
    "tagcomb":       ("../pyrate-summarize-results/references/summarize-results.md", 56,
                      "-plot path_to_pyrate_results -tag rhinos combine all"),
    "BF":            ("../pyrate-summarize-results/references/summarize-results.md", 69,
                      "-BF path_to_file/file_1_marginal_likelihood.txt path_to_file/file_2_marginal_likelihood.txt"),
    "ginput":        ("../pyrate-summarize-results/references/tutorial-2.md", 27,
                      "The input files for PyRateContinuous can be generated from the _mcmc.log files of a previous PyRate analysis using the command -ginput."),
    "resample":      ("../pyrate-summarize-results/references/tutorial-2.md", 52,
                      "the commands shown above can be combined with the additional flag -resample specifying how many samples should be taken"),
    "tagcomb2":      ("../pyrate-summarize-results/references/tutorial-2.md", 45,
                      "You can use the additional flag -tag can be used to identify files that should be combined"),
    "ltt":           ("../pyrate-summarize-results/references/tutorial-2.md", 66,
                      "we need to provide the ...se_ext.txt file using the -d command and use the flag -ltt followed by a number"),
    "lttex":         ("../pyrate-summarize-results/references/tutorial-2.md", 68,
                      "python PyRate.py -d Canidae_1_G_se_est.txt -ltt 1"),
    "gridplot":      ("../pyrate-summarize-results/references/tutorial-2.md", 83,
                      "you can use the command -grid_plot, which defines the size of time bins."),
    # ---- BDNN family (tutorial 7); EN mirror lines, the CN twin sits one line lower
    "BDNNmodel":     (BD, 223, "To run a BDNN analysis we need to provide the occurrence "
                      "file and use the command `-BDNNmodel 1`."),
    "BDNNmodelcmd":  (BD, 55, "-BDNNmodel 1 -trait_file ./example_files/BDNN_examples/"
                      "Carnivora/Traits.txt -BDNNtimevar ./example_files/BDNN_examples/"
                      "Carnivora/Paleotemperature.txt -mG -qShift"),
    "BDNNtimevar2":  (BD, 205, "You can use different time-series for speciation and "
                      "extinction by providing the paths to two text files using "
                      "`-BDNNtimevar`."),
    "BDNNtimetrait": (BD, 223, "Time as a predictor can be omitted by including the "
                      "setting `-BDNNtimetrait 0`, but this should be justified."),
    "BDNNtimeres":   (BD, 238, "you can use e.g. `-BDNNtimeres 0.5` to set all bins to "
                      "0.5 million years"),
    "plotBDNN":      (BD, 59, "The `-plotBDNN` command will create a PDF file with the "
                      "marginal rates through time (RTT)."),
    "plotBDNNcmd":   (BD, 61, "python ./PyRate.py -plotBDNN ./example_files/BDNN_examples/"
                      "Carnivora/pyrate_mcmc_logs/Carnivora_occs_1_G_BD1-1_BDNN_16_8TVc_"
                      "mcmc.log -b 0.5"),
    "plotBDNN_groups": (BD, 271, "-plotBDNN_groups ./example_files/BDNN_examples/Carnivora/"
                      "Advanced_examples/RTT_groups.csv"),
    "plotBDNN_effects": (BD, 71, "We can create partial dependence plots (PDP) to visualize "
                      "the influence of single predictors and all two-way interactions on "
                      "speciation and extinction rates with the `-plotBDNN_effects` command."),
    "transffeat":    (BD, 301, "`-plotBDNN_transf_features`: Tab-seperated text file with "
                      "means and standard deviation to reverse z-transformation of "
                      "continuous predictors"),
    "transffeatnote": (BD, 198, "the `-plotBDNN_transf_features` is optional and does not "
                      "change anything in the BDNN model inference."),
    "BDNN_groups":   (BD, 303, "`-BDNN_groups`: String to plot all one-hot encoded states "
                      "of a trait in the same figure."),
    "BDNN_groups_pi": (BD, 364, "Works, however, also for groups of continuous traits (but "
                      "not in combination with `-BDNN_pred_importance_interaction`)"),
    "BDNN_interaction": (BD, 312, "you can obtain a text file with the partial dependence "
                      "rates for any set of predictors with the `-BDNN_interaction` command"),
    "BDNN_interactioncmd": (BD, 316, "python ./PyRate.py -BDNN_interaction ./example_files/"
                      "BDNN_examples/Carnivora/pyrate_mcmc_logs/"
                      "Carnivora_occs_1_G_BDS_BDNN_16_8TVc_mcmc.log -plotBDNN_transf_features"),
    "BDNN_interaction_fix": (BD, 334, "We only need to add the argument "
                      "`-BDNN_interaction_fix`."),
    "BDNN_pred_importance": (BD, 344, "This is done using the `-BDNN_pred_importance` "
                      "command to load the `* mcmc.log` file."),
    "BDNN_pred_importancecmd": (BD, 347, "python PyRate.py -BDNN_pred_importance "
                      "./example_files/BDNN_examples/Carnivora/pyrate_mcmc_logs/"
                      "Carnivora_occs_1_G_BDS_BDNN_16_8TVc_mcmc.log -BDNN_groups"),
    "BDNN_pred_importance_nperm": (BD, 358, "`-BDNN_pred_importance_nperm`: Sets the number "
                      "of feature permutations (default: 100)."),
    "BDNN_pred_importance_interaction": (BD, 360, "`-BDNN_pred_importance_interaction`: Add "
                      "this argument to additionally rank two-way interaction of predictors."),
    "BDNN_pred_importance_window_size": (BD, 362, "The automatic correction can be adjusted "
                      "to something slightly larger e.g. `-BDNN_pred_importance_window_size "
                      "0.1`."),
    "BDNN_nsim_expected_cv": (BD, 356, "`-BDNN_nsim_expected_cv`: Number of constant "
                      "diversification simulations to obtain the expected variation in "
                      "species-time specific speciation and extinction rates (default: 100)."),
    "BDNN_mean_shap_per_group": (BD, 366, "`-BDNN_mean_shap_per_group`: Use the mean instead "
                      "of the sum across all states of a `-BDNN_groups` to get the overall "
                      "importance of the group."),
    "BDNNnodes":     (BD, 381, "`-BDNNnodes 16 8`: Defines the number of layers and nodes in "
                      "each layer (default: two layers of 18 and 8 nodes); 30 20 10 would "
                      "specify three layers with 30, 20, and 10 nodes."),
    "BDNNoutputfun": (BD, 383, "`-BDNNoutputfun`: Activation function of the output layer: "
                      "0) abs, 1) softPlus, 2) exp, 3) relu 4) sigmoid 5) sigmoid_rate "
                      "(default=5)"),
    "BDNNactfun":    (BD, 385, "`-BDNNactfun`: Activation function of the hidden layer(s): "
                      "0) tanh, 1) relu, 2) leaky_relu, 3) swish, 4) sigmoid (default=0)"),
    "BDNNreg":       (BD, 387, "This can be made independent by providing two values "
                      "`-BDNNreg 1.0 1.0`."),
    "BDNNprecision": (BD, 389, "`-BDNNprecision`: Sets the floating point precision of the "
                      "neural network nodes and influences the BDNN speed."),
    "BDNNprecisioncontr": (BD, 389, "Use this double precision (i.e. 16 decimal digits) "
                      "with `-BDNNprecision 1`"),
    "qFilter":       (BD, 394, "Adding `-qFilter` allows for shifts in sampling rates at the "
                      "boundaries."),
    "qFiltercmd":    (BD, 397, "-qFilter 0 -edgeShift 15.97 2.5"),
    "rootminageopt": (BD, 305, "`-root_plot` and `-min_age_plot`: Considers only taxa "
                      "originating or going extinct in this time window."),
    "rootminagecmd": (BD, 402, "-min_age_plot 2.6 -root_plot 15.9"),
    "logTplot":      (BD, 264, "Rates can be visualized on a log scale by adding `-logT 2` "
                      "and truncated with `-root_plot` and `-min_age_plot`."),
    "restore_mcmc":  (BD, 433, "you can restore the MCMC chain from the last sample using "
                      "the `-restore_mcmc` argument."),
    "restore_cmccmd": (BD, 436, "-restore_mcmc ./example_files/BDNN_examples/Carnivora/"
                      "pyrate_mcmc_logs/Carnivora_occs_1_G_BDS_BDNN_16_8TVc_mcmc.log"),
    "combBDNN":      (BD, 453, "python ./PyRate.py -combBDNN ./example_files/BDNN_examples/"
                      "Carnivora/pyrate_mcmc_logs -b 0.25"),
    "BDNNexport_taxon_time_tables": (BD, 425, "PyRate allows to export the tables containing "
                      "traits and environmental predictors from a BDNN analysis with the "
                      "`-BDNNexport_taxon_time_tables` flag."),
    "BDNNexportcmd": (BD, 427, "Time_windows.txt -BDNNexport_taxon_time_tables"),
    "BDNNpath_taxon_time_tables": (BD, 410, "If a single path is provided, the custom tables "
                      "are used as predictors for speciation and extinction rates. If two "
                      "paths are given, the first one is for the predictors of speciation "
                      "rates and the second for extinction rates."),
    "BDNNpathcmd":   (BD, 415, "-BDNNpath_taxon_time_tables ./example_files/BDNN_examples/"
                      "Carnivora/Advanced_examples/load_predictors/speciation ./example_"
                      "files/BDNN_examples/Carnivora/Advanced_examples/load_predictors/"
                      "extinction -fixShift"),
    "BDNNpathrule":  (BD, 411, "No additional `-trait_file` and `-BDNNtimevar` should be "
                      "invoked."),
    "resamplepost":  (BD, 298, "`-resample`: Number of post burnin MCMC samples (using all "
                      "by default)."),
    # ---- RJMCMC family (tutorial 3)
    "min_dt":        (RJ, 44, "To change this prior you can use the flag `-min_dt` "
                      "specifying the minimum allowed duration of a bin"),
    "min_dtcmd":     (RJ, 46, "python PyRate.py -d Canidae_1_G_se_est.txt -A 4 -min_dt 0.5"),
    "plotRJ":        (RJ, 73, "python PyRate.py -plotRJ .../path_to_log_files/ -b 200"),
    "plotRJtrunc":   (RJ, 84, "python PyRate.py -plotRJ .../path_to_log_files/ -b 200 "
                      "-root_plot 23 -min_age_plot 5.3"),
    "combLogRJ":     (RJ, 99, "python PyRate.py -combLogRJ /pyrate_mcmc_logs -b 1000 -tag "
                      "Canis"),
    "combLogRJwhere": (RJ, 101, "`-combLogRJ .../pyrate_mcmc_logs` provides the full path to "
                      "the log files"),
    "combLogRJres":  (RJ, 105, "python PyRate.py -combLogRJ .../pyrate_mcmc_logs -b 1000 "
                      "-tag Canis -resample 100"),
    "se_gibbs":      (RJ, 113, "you can use the flag `-se_gibbs` and modify the update "
                      "frequencies"),
    "se_gibbscmd":   (RJ, 115, "python PyRate.py .../Rhinocerotidae_PyRate.py -qShift "
                      ".../epochs_q.txt -se_gibbs -fU 0.35 0.6 0"),
    "bound_se":      (RJ, 144, "The bounds on origination and extinction ages can be used in "
                      "combination with Gibbs sampler e.g. using:"),
    "bound_secmd":   (RJ, 142, "python ./PyRate.py ./example_files/Ammonoidea.py -bound_se "
                      "./example_files/Ammonoidea_bound_se.txt"),
    # ---- ADE / BDC family (tutorial 4 of the Covar/ADE page)
    "ADE":           (T4, 143, "where -ADE 1 specifies that you want to run the ADE model"),
    "ADEmodels":     (T4, 143, "only homogeneous Poisson process (HPP) and time-variable "
                      "Poisson process can be used with the ADE model"),
    "ADEcmd":        (T4, 141, "python PyRate.py <your_dataset> -ADE 1 -qShift epochs.txt"),
    "filter":        (T4, 145, "you can use the command `-filter` to drop all taxa outside "
                      "a specified time range"),
    "filtercmd":     (T4, 147, "python PyRate.py <your_dataset> -ADE 1 -qShift epochs.txt "
                      "-filter 23.03 5.3"),
    "tree":          (T4, 156, "you should provide the standard PyRate input file "
                      "(occurrence data) and a tree file (NEXUS format)"),
    "treecmd":       (T4, 158, "python PyRate.py example_files/BDC_model/Feliformia.py "
                      "-tree example_files/BDC_model/Feliformia.tre"),
    "bdceqr":        (T4, 163, "The flag `-bdc` enforces **compatible speciation and "
                      "extinction rates under the BDC model**, whereas the flag `-eqr` sets "
                      "the **rates to be equal**."),
    "bdccmd":        (T4, 167, "-tree example_files/BDC_model/Feliformia.tre -fixShift "
                      "example_files/epochs.txt -bdc"),
    "var":           (T4, 71, "The flag `-var` is used to specify the path to a folder "
                      "containing all predictors."),
    "varmbd":        (T4, 68, "./PyRateMBD.py -d /example_files/Ferns_SE.txt -var "
                      "/example_files/predictors_MBDmodel -m 1"),
    # ---- misc elsewhere
    "fast_burnin":   ("../pyrate-mcmc-tuning/references/tutorial-6.md", 14,
                      "Specify number of MCMC iterations using approximate Gibbs sampler "
                      "for times of origination and extinction for faster convergence "
                      "(default: `-fast_burnin 0`)"),
    "root_age":      ("../pyrate-summarize-results/references/summarize-results.md", 61,
                      "`-plot path_to_pyrate_results -tag rhinos -root_age 23` combine all"),
    "root_plotdef":  ("../pyrate-summarize-results/references/summarize-results.md", 59,
                      "sets the maximum age in the plot. If set to 0, the age will be "
                      "determined as the minimum root age across all log files."),
    "vflag":         ("../pyrate-installation/references/virtual-environment.md", 49,
                      "python your_path/PyRate-master/PyRate.py -v"),
    "vflagwhy":      ("../pyrate-installation/references/virtual-environment.md", 47,
                      "You can check that PyRate can now be run in your virtual environment "
                      "using:"),
}


def norm(s):
    """Whitespace-normalise and strip backticks/asterisks (docs markup) from text."""
    return re.sub(r"\s+", " ", s.replace("`", "").replace("*", "")).strip()


def cite(key):
    rel, line, quote = CITE[key]
    return '"%s" (%s:%d)' % (quote, rel, line)


def fmt_arity(a):
    if isinstance(a, tuple):
        return "%d-%d" % a
    return str(a)


# Core-command metadata. `arity` is only a FALLBACK used when the mirror block has
# no parsable example (real case: -pM, whose example line is a docs copy-paste typo
# showing `-pL 1.1 1.1`, CITE["pMtypo"]); arities parsed from the mirror win.
META = {
    "d":      dict(kind=KIND_PATH, arity=1, cite="dtable"),
    "wd":     dict(kind=KIND_PATH, arity=1, cite=None),
    "j":      dict(kind=KIND_INT, arity=1, cite="jdefault", positive=True),
    "out":    dict(kind=KIND_STR, arity=1, cite=None),
    "singleton": dict(kind=KIND_INT, arity=1, cite="singleton", enum_warn={-1, 1, 2}),
    "A":      dict(kind=KIND_INT, arity=1, cite="Adefault", enum={0, 1, 2, 3}),
    "n":      dict(kind=KIND_INT, arity=1, cite=None, positive=True),
    "s":      dict(kind=KIND_INT, arity=1, cite=None, positive=True),
    "p":      dict(kind=KIND_INT, arity=1, cite=None, positive=True),
    "b":      dict(kind=KIND_FLOAT, arity=1, cite="b"),
    "thread": dict(kind=KIND_INT, arity=2, cite="thread", nonneg=True),
    "mHPP":   dict(kind=KIND_FLAG, arity=0, cite="mHPP"),
    "qShift": dict(kind=KIND_PATH, arity=1, cite="qShift"),
    "mG":     dict(kind=KIND_FLAG, arity=0, cite="mG"),
    "ncat":   dict(kind=KIND_INT, arity=1, cite="ncatdefault", positive=True),
    "fixSE":  dict(kind=KIND_PATH, arity=1, cite="fixSE", or_null=True),
    "mL":     dict(kind=KIND_INT, arity=1, cite="mL", positive=True),
    "mM":     dict(kind=KIND_INT, arity=1, cite="mM", positive=True),
    "mC":     dict(kind=KIND_FLAG, arity=0, cite="mC"),
    "fixShift": dict(kind=KIND_PATH, arity=1, cite="fixShift"),
    "trait_file": dict(kind=KIND_PATH, arity=1, cite="traitfile"),
    "mCov":   dict(kind=KIND_INT, arity=1, cite="mCov1", enum={1, 2, 3, 4, 5}),
    "trait":  dict(kind=KIND_INT, arity=1, cite="trait", positive=True),
    "logT":   dict(kind=KIND_INT, arity=1, cite="logT", enum={0, 1, 2}),
    "N":      dict(kind=KIND_INT, arity=1, cite="N"),
    "pL":     dict(kind=KIND_FLOAT, arity=2, cite="pL"),
    "pM":     dict(kind=KIND_FLOAT, arity=2, cite="pM"),
    "cauchy": dict(kind=KIND_FLOAT, arity=2, cite="cauchy"),
    "pP":     dict(kind=KIND_FLOAT, arity=2, cite="pP"),
    "pS":     dict(kind=KIND_FLOAT, arity=1, cite=None),
    "pC":     dict(kind=KIND_FLOAT, arity=1, cite="pC"),
    "r":      dict(kind=KIND_INT, arity=1, cite="r", positive=True),
    "t":      dict(kind=KIND_FLOAT, arity=1, cite="t"),
    "sw":     dict(kind=KIND_INT, arity=1, cite="sw", positive=True),
    "k":      dict(kind=KIND_INT, arity=1, cite="k", positive=True),
    "a":      dict(kind=KIND_FLOAT, arity=1, cite="a"),
    "M":      dict(kind=KIND_INT, arity=1, cite="M", positive=True),
    "B":      dict(kind=KIND_FLOAT, arity=1, cite="B"),
    "T":      dict(kind=KIND_FLOAT, arity=1, cite="T"),
    "S":      dict(kind=KIND_INT, arity=1, cite="S", positive=True),
    "multiR": dict(kind=KIND_INT, arity=1, cite="multiR", enum={0, 1}),
    "tT":     dict(kind=KIND_FLOAT, arity=1, cite=None),
    "nT":     dict(kind=KIND_INT, arity=1, cite="nT", nonneg=True),
    "tQ":     dict(kind=KIND_FLOAT, arity=2, cite=None),
    "tR":     dict(kind=KIND_FLOAT, arity=1, cite=None),
    "tS":     dict(kind=KIND_FLOAT, arity=1, cite=None),
    "fS":     dict(kind=KIND_FLOAT, arity=1, cite="fS"),
    "tC":     dict(kind=KIND_FLOAT, arity=3, cite=None),
    "fU":     dict(kind=KIND_FLOAT, arity=3, cite="fU"),
    "fR":     dict(kind=KIND_FLOAT, arity=1, cite=None),
}

# Commands documented outside command-list.md (each one carries its own citation).
EXTENSIONS = {
    "data_info":      dict(kind=KIND_FLAG, arity=0, cite="data_info"),
    "check_names":    dict(kind=KIND_PATH, arity=1, cite="check_names"),
    "mProb":          dict(kind=KIND_PATH, arity=1, cite="mProb"),
    "plot":           dict(kind=KIND_PATH, arity=1, cite="plot"),
    "plot2":          dict(kind=KIND_PATH, arity=1, cite="plot2"),
    "combLog":        dict(kind=KIND_PATH, arity=1, cite="combLog"),
    "plotQ":          dict(kind=KIND_PATH, arity=1, cite="plotQ"),
    "BF":             dict(kind=KIND_PATH, arity=2, cite="BF"),
    "ginput":         dict(kind=KIND_PATH, arity=1, cite="ginput"),
    "resample":       dict(kind=KIND_INT, arity=1, cite="resample", positive=True),
    "tag":            dict(kind=KIND_STR, arity=1, cite="tag"),
    "edgeShift":      dict(kind=KIND_FLOAT, arity=2, cite="edgeShift", or_inf=True),
    "ltt":            dict(kind=KIND_INT, arity=1, cite="ltt", enum_warn={1, 2, 3}),
    "grid_plot":      dict(kind=KIND_FLOAT, arity=1, cite="gridplot"),
    "log_sp_q_rates": dict(kind=KIND_FLAG, arity=0, cite="logspq"),
    "PPmodeltest":    dict(kind=KIND_FLAG, arity=0, cite="ppmodeltest"),
    # ---- version probe and the tutorial-3 RJMCMC family
    "v":              dict(kind=KIND_FLAG, arity=0, cite="vflag"),
    "min_dt":         dict(kind=KIND_FLOAT, arity=1, cite="min_dt", positive=True),
    "bound_se":       dict(kind=KIND_PATH, arity=1, cite="bound_se"),
    "se_gibbs":       dict(kind=KIND_FLAG, arity=0, cite="se_gibbs"),
    "plotRJ":         dict(kind=KIND_PATH, arity=1, cite="plotRJ"),
    "combLogRJ":      dict(kind=KIND_PATH, arity=1, cite="combLogRJ"),
    # ---- plot truncation / burnin helpers documented on summarising pages
    "root_plot":      dict(kind=KIND_FLOAT, arity=1, cite="root_plotdef", nonneg=True),
    "root_age":       dict(kind=KIND_FLOAT, arity=1, cite="root_age", nonneg=True),
    "min_age_plot":   dict(kind=KIND_FLOAT, arity=1, cite="rootminageopt", nonneg=True),
    "fast_burnin":    dict(kind=KIND_INT, arity=1, cite="fast_burnin", nonneg=True),
    # ---- ADE / BDC family (tutorial 4)
    "ADE":            dict(kind=KIND_INT, arity=1, cite="ADE", enum_warn={0, 1}),
    "filter":         dict(kind=KIND_FLOAT, arity=2, cite="filter"),
    "tree":           dict(kind=KIND_PATH, arity=1, cite="tree"),
    "bdc":            dict(kind=KIND_FLAG, arity=0, cite="bdceqr"),
    "eqr":            dict(kind=KIND_FLAG, arity=0, cite="bdceqr"),
    # documented for the MBD program only; accepted with a printed note
    "var":            dict(kind=KIND_PATH, arity=1, cite="var"),
    # ---- BDNN family (tutorial 7); every arity below is what the cited usage
    # line prints: (lo, hi) = the corpus shows between lo and hi values
    "BDNNmodel":      dict(kind=KIND_INT, arity=1, cite="BDNNmodel", enum_warn={1}),
    "BDNNtimevar":    dict(kind=KIND_PATH, arity=(1, 2), cite="BDNNtimevar2"),
    "BDNNtimetrait":  dict(kind=KIND_INT, arity=1, cite="BDNNtimetrait"),
    "BDNNtimeres":    dict(kind=KIND_FLOAT, arity=1, cite="BDNNtimeres", positive=True),
    "BDNNnodes":      dict(kind=KIND_INT, arity=(2, 3), cite="BDNNnodes", positive=True),
    "BDNNactfun":     dict(kind=KIND_INT, arity=1, cite="BDNNactfun", enum={0, 1, 2, 3, 4}),
    "BDNNoutputfun":  dict(kind=KIND_INT, arity=1, cite="BDNNoutputfun",
                           enum={0, 1, 2, 3, 4, 5}),
    "BDNNreg":        dict(kind=KIND_FLOAT, arity=(1, 2), cite="BDNNreg"),
    "BDNNprecision":  dict(kind=KIND_INT, arity=1, cite="BDNNprecision", enum_warn={1}),
    "qFilter":        dict(kind=KIND_INT, arity=1, cite="qFilter", nonneg=True),
    "BDNN_groups":    dict(kind=KIND_STR, arity=1, cite="BDNN_groups"),
    "BDNN_mean_shap_per_group": dict(kind=KIND_FLAG, arity=0, cite="BDNN_mean_shap_per_group"),
    "BDNNpath_taxon_time_tables": dict(kind=KIND_PATH, arity=(1, 2),
                                       cite="BDNNpath_taxon_time_tables"),
    "BDNNexport_taxon_time_tables": dict(kind=KIND_FLAG, arity=0,
                                         cite="BDNNexport_taxon_time_tables"),
    "restore_mcmc":   dict(kind=KIND_PATH, arity=1, cite="restore_mcmc"),
    "combBDNN":       dict(kind=KIND_PATH, arity=1, cite="combBDNN"),
    "plotBDNN":       dict(kind=KIND_PATH, arity=1, cite="plotBDNN"),
    "plotBDNN_groups": dict(kind=KIND_PATH, arity=1, cite="plotBDNN_groups"),
    "plotBDNN_effects": dict(kind=KIND_PATH, arity=1, cite="plotBDNN_effects"),
    "plotBDNN_transf_features": dict(kind=KIND_PATH, arity=1, cite="transffeat"),
    "BDNN_interaction": dict(kind=KIND_PATH, arity=1, cite="BDNN_interaction"),
    "BDNN_interaction_fix": dict(kind=KIND_FLAG, arity=0, cite="BDNN_interaction_fix"),
    "BDNN_pred_importance": dict(kind=KIND_PATH, arity=1, cite="BDNN_pred_importance"),
    "BDNN_pred_importance_nperm": dict(kind=KIND_INT, arity=1,
                                       cite="BDNN_pred_importance_nperm", positive=True),
    "BDNN_pred_importance_interaction": dict(kind=KIND_FLAG, arity=0,
                                             cite="BDNN_pred_importance_interaction"),
    "BDNN_pred_importance_window_size": dict(kind=KIND_FLOAT, arity=1,
                                             cite="BDNN_pred_importance_window_size",
                                             positive=True),
    "BDNN_nsim_expected_cv": dict(kind=KIND_INT, arity=1, cite="BDNN_nsim_expected_cv",
                                  nonneg=True),
}
UTILITY_CMDS = ("check_names", "mProb", "plot", "plot2", "combLog", "plotQ", "BF",
                "ginput", "v", "plotRJ", "combLogRJ", "combBDNN", "plotBDNN",
                "plotBDNN_effects", "BDNN_interaction", "BDNN_pred_importance")
# commands the docs show ALONGSIDE a utility command (companions); anything else
# together with a utility command is an undocumented combination -> error
UTILITY_ALLOWED_EXTRA = {"b", "wd", "tag", "qShift", "out",
                         "logT"}  # -plotBDNN ... -logT 2: see cite("logTplot")
# post-processing commands the corpus shows -tag / -resample attached to
TAG_HOSTS = ("plot", "plot2", "combLog", "ginput", "combLogRJ")
RESAMPLE_HOSTS = ("ginput", "combLogRJ", "plotBDNN_effects", "BDNN_interaction",
                  "BDNN_pred_importance")
# BDNN model-setting flags: the corpus documents each of them only inside a
# BDNN inference, i.e. together with -BDNNmodel (cite("BDNNmodel"))
BDNN_INFERENCE_FLAGS = ("BDNNtimevar", "BDNNtimetrait", "BDNNtimeres", "BDNNnodes",
                        "BDNNactfun", "BDNNoutputfun", "BDNNreg", "BDNNprecision",
                        "qFilter", "BDNNpath_taxon_time_tables",
                        "BDNNexport_taxon_time_tables")
# post-processing options of -BDNN_pred_importance (cite("BDNN_pred_importance"))
PRED_IMPORTANCE_OPTIONS = ("BDNN_pred_importance_nperm",
                           "BDNN_pred_importance_interaction",
                           "BDNN_pred_importance_window_size",
                           "BDNN_nsim_expected_cv", "BDNN_mean_shap_per_group")

# ------------------------------------------------------------------ mirror parsing

HEADING_RE = re.compile(r"^#{5}[ \t]*`?(-[A-Za-z][A-Za-z0-9_]*)`?[ \t]*$")
BLOCK_END_RE = re.compile(r"^(#{3,6}[ \t]|\*\*\*$)")


def looks_like_value(tok):
    """Docs write `Example: -mCov 1 correlated speciation rate` inside ONE
    backtick span; stop tokenising at the first prose word. A token counts as a
    value if it is numeric, contains a path/punctuator char, is very short
    (-cauchy x y uses 1-char placeholders) or the literal null/inf."""
    return bool(re.fullmatch(r"-?\d+(\.\d+)?", tok)
                or re.search(r"[/_.\\]", tok)
                or len(tok) <= 2
                or tok.lower() in ("null", "inf"))


def parse_mirror(path):
    """Return (order, parsed) for the command-list mirror, in document order.

    parsed[name] = {"arities": set[int], "values": set[str], "start_line": int}
    """
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    order, parsed = [], {}
    current = None
    for idx, line in enumerate(lines, 1):
        m = HEADING_RE.match(line)
        if m:
            current = m.group(1).lstrip("-")
            if current not in parsed:
                order.append(current)
                parsed[current] = {"arities": set(), "values": set(),
                                   "start_line": idx}
            continue
        if BLOCK_END_RE.match(line):
            current = None
            continue
        if current is None:
            continue
        spans = re.findall(r"`([^`]*)`", line)
        rest = re.sub(r"\([^()]*\)", " ", re.sub(r"`[^`]*`", " ", line))
        spans.append(rest)
        for span in spans:
            for mm in re.finditer(r"-%s\b(.*)" % re.escape(current), span):
                toks = []
                for t in norm(mm.group(1)).split(" "):
                    if not t:
                        continue
                    if not looks_like_value(t):
                        break
                    toks.append(t)
                parsed[current]["arities"].add(len(toks))
                parsed[current]["values"].update(toks)
    return order, parsed


def resolve_arity(name, mirror_entry, meta, notes):
    """Arity for `name`; per-command notes go into `notes` (dict name -> message)."""
    parsed = mirror_entry["arities"]
    if meta and meta.get("kind") == KIND_FLAG:
        if parsed and parsed != {0}:
            notes[name] = ("[WARN] -%s: examples at %s:%d appear to take arguments %s "
                           "but the docs describe a flag — treated as 0-arg."
                           % (name, MIRROR_LABEL, mirror_entry["start_line"],
                              sorted(parsed)))
        return 0
    if not parsed:
        if meta and "arity" in meta:
            if name == "pM":
                notes[name] = ("[NOTE] -pM: the mirror's example line is a docs "
                               "copy-paste typo — %s — so arity 2 was taken from the "
                               "parallel -pL block (%s:%d)."
                               % (cite("pMtypo"), MIRROR_LABEL, CITE["pL"][1] - 1))
            return meta["arity"]
        notes[name] = ("[WARN] -%s: no example found in the mirror; assuming 0 args "
                       "(%s:%d)." % (name, MIRROR_LABEL, mirror_entry["start_line"]))
        return 0
    if len(parsed) > 1:
        notes[name] = ("[WARN] -%s: mirror examples show inconsistent arities %s "
                       "(%s:%d); using max."
                       % (name, sorted(parsed), MIRROR_LABEL,
                          mirror_entry["start_line"]))
    return max(parsed)


# ---------------------------------------------------------------- validation core

class Ctx(object):
    def __init__(self):
        self.values = {}     # name -> True or list[str]
        self.ordered = []    # command names, canonical (mirror) order
        self.errors, self.warnings, self.notes = [], [], []

    def has(self, name):
        return name in self.values

    def val(self, name, i=0):
        v = self.values.get(name)
        if not v or v is True:
            return None
        try:
            return float(v[i])
        except (IndexError, ValueError):
            return None

    def raw(self, name):
        v = self.values.get(name)
        return None if v is True else v

    def err(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def note(self, msg):
        self.notes.append(msg)


def check_value(name, meta, tokens, ctx, core_only):
    kind = meta["kind"]
    arity = meta.get("arity")
    if isinstance(arity, tuple) and not (arity[0] <= len(tokens) <= arity[1]):
        ctx.err("[ERROR] -%s: the corpus documents %s values, got %d (%s: %s)."
                % (name, fmt_arity(arity), len(tokens),
                   CITE[meta["cite"]][0], CITE[meta["cite"]][1]))
    for tok in tokens:
        if kind in (KIND_INT, KIND_FLOAT):
            try:
                v = int(tok) if kind == KIND_INT else float(tok)
                if kind == KIND_INT and float(tok) != int(float(tok)):
                    raise ValueError
            except ValueError:
                ctx.err("[ERROR] -%s: expected %s value, got '%s' (%s)."
                        % (name, kind, tok,
                           cite(meta["cite"]) if meta.get("cite")
                           else "see %s" % MIRROR_LABEL))
                continue
            if meta.get("positive") and v <= 0:
                ctx.err("[ERROR] -%s: %s must be a positive number (%s)."
                        % (name, tok, cite(meta["cite"]) if meta.get("cite")
                           else MIRROR_LABEL))
            if meta.get("nonneg") and v < 0:
                ctx.err("[ERROR] -%s: %s must be >= 0 (%s)."
                        % (name, tok, cite(meta["cite"])))
            enum = meta.get("enum")
            if enum is not None and int(v) not in enum:
                if name == "A" and int(v) == 4 and not core_only:
                    ctx.note("[NOTE] -A 4 is NOT in %s; it is documented only in %s. "
                             "Corpus conflict: %s (command list calls -A 2 the default) "
                             "vs %s (omitting -A selects RJMCMC). Pass it explicitly."
                             % (MIRROR_LABEL, cite("A4"), cite("Adefault"), cite("A4")))
                else:
                    extra = ""
                    if name == "A" and int(v) == 4:
                        extra = (" (-A 4 exists in the tutorials but --core-only "
                                 "refuses it: %s)" % cite("A4"))
                    ctx.err("[ERROR] -%s: value %s is outside the documented set %s "
                            "(%s)%s." % (name, tok, sorted(enum),
                                         cite(meta["cite"]) or MIRROR_LABEL, extra))
            ew = meta.get("enum_warn")
            if ew is not None and int(v) not in ew:
                ctx.warn("[WARN] -%s: value %s is beyond the documented examples %s (%s)"
                         % (name, tok, sorted(ew), cite(meta["cite"])))
            if name == "b" and 0 < v < 1:
                ctx.note("[NOTE] -b %s: %s" % (tok, cite("bfraction")))
        elif kind == KIND_PATH:
            if meta.get("or_null") and tok.lower() == "null":
                continue
            if meta.get("or_inf") and tok.lower() == "inf":
                continue
            if tok.startswith("-") or not tok:
                ctx.err("[ERROR] -%s: expected a file/path value (or %s), got '%s' (%s)."
                        % (name, "'null'" if meta.get("or_null") else "a path", tok,
                           cite(meta["cite"]) if meta.get("cite") else MIRROR_LABEL))


def apply_rules(ctx, core_only):
    """Conditional-combination rules; every message quotes its mirror evidence."""
    has, val = ctx.has, ctx.val
    if has("ncat") and not has("mG"):
        ctx.err("[ERROR] -ncat without -mG: %s Fix: add -mG or drop -ncat." % cite("ncat"))
    if has("mHPP") and has("qShift"):
        ctx.err("[ERROR] -mHPP with -qShift: HPP is used 'instead of' the NHPP %s, while "
                "-qShift selects the TPP model (%s) — one preservation model at a time; "
                "only -mG is documented as compatible with all three (%s)."
                % (cite("mHPP"), cite("qShift"), cite("mG")))
    if val("nT") == 0 and has("qShift"):
        ctx.err("[ERROR] -nT 0 with -qShift: %s — HPP would be forced, contradicting "
                "-qShift's TPP model (%s)." % (cite("nT"), cite("qShift")))
    if has("d") and has("fixSE"):
        ctx.err("[ERROR] -d with -fixSE: %s (%s:%d) — the combination is not documented; "
                "drop -fixSE." % (cite("d"), MIRROR_LABEL, CITE["d"][1]))
    if has("r") and has("A") and val("A") != 0:
        ctx.err("[ERROR] -r with -A %s: %s" % (ctx.raw("A")[0], cite("r")))
    if has("r") and not has("A"):
        ctx.warn("[WARN] -r without explicit -A: %s — and the corpus contradicts itself "
                 "on the -A default (%s vs %s); pass -A 0 to be safe."
                 % (cite("r"), cite("Adefault"), cite("A4")))
    if (val("r") is None or val("r") <= 1) and (has("t") or has("sw")):
        ctx.err("[ERROR] -t/-sw require MC3 with -r > 1: %s (same wording at %s:%d)."
                % (cite("t"), MIRROR_LABEL, CITE["sw"][1]))
    for nm in ("k", "a"):
        if has(nm):
            if has("A") and val("A") != 1:
                ctx.err("[ERROR] -%s with -A %s: %s" % (nm, ctx.raw("A")[0], cite(nm)))
            elif not has("A"):
                ctx.warn("[WARN] -%s without explicit -A 1: %s" % (nm, cite(nm)))
    for nm in ("M", "B", "T", "S"):
        if has(nm):
            if has("A") and val("A") != 2:
                ctx.err("[ERROR] -%s with -A %s: %s" % (nm, ctx.raw("A")[0], cite(nm)))
            elif not has("A"):
                ctx.warn("[WARN] -%s without explicit -A 2: %s" % (nm, cite(nm)))
    for nm in ("pL", "pM"):
        if has(nm) and has("N") and val("N") != -1:
            ctx.err("[ERROR] -%s with -N %s: %s — the gamma prior flags apply only when "
                    "extant diversity is not specified (-N -1 or omitted)."
                    % (nm, ctx.raw("N")[0], cite(nm)))
    if has("mC"):
        mL, mM = val("mL"), val("mM")
        if (mL is not None and mL < 2) or (mM is not None and mM < 2):
            ctx.err("[ERROR] -mC with -mL %s / -mM %s: %s (the sentence is truncated in "
                    "the docs at %s:%d — it literally ends with 'and')."
                    % (ctx.raw("mL")[0] if mL is not None else "unset",
                       ctx.raw("mM")[0] if mM is not None else "unset",
                       cite("mC"), MIRROR_LABEL, CITE["mC"][1]))
        elif mL is None and mM is None:
            ctx.warn("[WARN] -mC without -mL/-mM >= 2: %s — the mirror documents no "
                     "default for -mL/-mM, so this cannot be verified statically "
                     "(absence of a documented default is not a default)." % cite("mC"))
    if has("pC"):
        mcov = val("mCov")
        if not has("mCov"):
            if val("pC") == 0:
                ctx.err("[ERROR] -pC 0 without -mCov: %s — with no Covar model selected "
                        "no correlation parameter is estimated at all." % cite("pC"))
            else:
                ctx.warn("[WARN] -pC without -mCov: the prior it sets applies only "
                         "'under the Covar model' (%s)." % cite("pC"))
        elif val("pC") == 0 and mcov not in (3, 5):
            ctx.err("[ERROR] -pC 0 with -mCov %s: %s — by inference from the -mCov "
                    "examples, at least 2 correlation parameters are estimated only for "
                    "-mCov 3 (%s) and -mCov 5 (%s); the doc's own example span is "
                    "garbled ('%s' is exactly what the mirror prints, %s:%d)."
                    % (ctx.raw("mCov")[0], cite("pC"), cite("mCov3"), cite("mCov5"),
                       CITE["pC"][2][-28:], MIRROR_LABEL, CITE["pC"][1]))
    if has("fS") and has("fixSE"):
        ctx.warn("[WARN] -fS with -fixSE: %s — an explicit -fS may be ignored."
                 % cite("fS"))
    if has("fixShift") and has("cauchy") and (val("cauchy", 0), val("cauchy", 1)) != (0, 0):
        ctx.note("[NOTE] -fixShift with explicit -cauchy %s: %s — fixed shifts already "
                 "default to '-cauchy 0 0'." % (" ".join(ctx.raw("cauchy")), cite("cauchy")))
    if val("A") == 3:
        ctx.warn("[WARN] -A 3: %s" % cite("A3"))
    if core_only:
        return
    if has("log_sp_q_rates") and not (has("qShift") and has("mG")):
        ctx.err("[ERROR] -log_sp_q_rates without -qShift and -mG: %s" % cite("logspq"))
    if has("PPmodeltest") and not has("qShift"):
        ctx.err("[ERROR] -PPmodeltest without -qShift: %s" % cite("ppmodeltest"))
    if has("plotQ") and not has("qShift"):
        ctx.err("[ERROR] -plotQ without -qShift: %s (%s)" % (cite("plotQnote"),
                                                             cite("plotQ")))
    if has("tag") and not any(has(c) for c in TAG_HOSTS):
        ctx.err("[ERROR] -tag without %s: %s (%s; %s; for the RJMCMC combine: %s)"
                % ("/".join("-" + c for c in TAG_HOSTS), cite("tag"), cite("tagcomb"),
                   cite("tagcomb2"), cite("combLogRJ")))
    if has("resample") and not any(has(c) for c in RESAMPLE_HOSTS):
        ctx.err("[ERROR] -resample without %s: %s (shown with -combLogRJ at %s, and "
                "listed as an optional argument of the BDNN post-processing commands "
                "at %s)."
                % ("/".join("-" + c for c in RESAMPLE_HOSTS), cite("resample"),
                   cite("combLogRJres"), cite("resamplepost")))
    if has("grid_plot") and not has("ltt"):
        ctx.err("[ERROR] -grid_plot without -ltt: %s" % cite("gridplot"))
    if has("ltt") and not has("d"):
        ctx.err("[ERROR] -ltt without -d: %s (example: %s)" % (cite("ltt"), cite("lttex")))
    if has("edgeShift"):
        if has("A") and val("A") != 4:
            ctx.err("[ERROR] -edgeShift with -A %s: boundary shifts are documented "
                    "together with the RJMCMC run (%s); see also %s"
                    % (ctx.raw("A")[0], cite("edgeShift"), cite("edgeShiftInf")))
        elif not has("A"):
            ctx.warn("[WARN] -edgeShift without explicit -A 4: usage documented as "
                     "'-A 4 -edgeShift ...' (%s); %s suggests omitting -A selects "
                     "RJMCMC too, but the corpus conflicts on the -A default (%s)."
                     % (cite("edgeShift"), cite("A4"), cite("Adefault")))
    # ---- ADE / BDC (tutorial 4)
    if has("ADE"):
        if has("mG"):
            ctx.err("[ERROR] -ADE with -mG: %s — the Gamma model is neither of the two "
                    "(see also %s for what -mG is)."
                    % (cite("ADEmodels"), cite("mG")))
        if not (has("mHPP") or has("qShift")):
            ctx.warn("[WARN] -ADE without an explicit preservation model: every usage "
                     "pairs it with the TPP or the HPP (%s; example %s)."
                     % (cite("ADEmodels"), cite("ADEcmd")))
    if has("filter") and not has("ADE"):
        ctx.err("[ERROR] -filter without -ADE: %s — documented only as the time-window "
                "command of an ADE analysis (example: %s)."
                % (cite("filter"), cite("filtercmd")))
    if has("var"):
        ctx.note("[NOTE] -var: the corpus documents this flag ONLY on a PyRateMBD.py "
                 "invocation (%s: %s), not on python PyRate.py (%s) — accepted, but "
                 "check which program you are launching."
                 % (CITE["varmbd"][0] + ":" + str(CITE["varmbd"][1]), cite("varmbd"),
                    cite("var")))
    # ---- BDNN (tutorial 7)
    if has("BDNNpath_taxon_time_tables") and (has("trait_file") or has("BDNNtimevar")):
        ctx.err("[ERROR] -BDNNpath_taxon_time_tables with %s: %s Custom tables replace "
                "them (%s: %s)."
                % (" and ".join("-" + c for c in ("trait_file", "BDNNtimevar")
                                if has(c)),
                   cite("BDNNpathrule"),
                   cite("BDNNpath_taxon_time_tables"), cite("BDNNpathcmd")))
    for nm in BDNN_INFERENCE_FLAGS:
        if has(nm) and not has("BDNNmodel"):
            if has("restore_mcmc"):
                ctx.warn("[WARN] -%s with -restore_mcmc but no -BDNNmodel: the restore "
                         "usage re-states the whole inference (%s)." % (nm, cite("restore_mcmc")))
            else:
                ctx.err("[ERROR] -%s without -BDNNmodel: %s — no usage line in the "
                        "corpus runs -%s without the BDNN model switch (first usage: %s)."
                        % (nm, cite("BDNNmodel"), nm, cite("BDNNmodelcmd")))
    if has("BDNN_interaction_fix") and not has("BDNN_interaction"):
        ctx.err("[ERROR] -BDNN_interaction_fix without -BDNN_interaction: %s — it is an "
                "addition to that command (usage: %s)."
                % (cite("BDNN_interaction_fix"), cite("BDNN_interactioncmd")))
    if has("BDNN_mean_shap_per_group") and not has("BDNN_groups"):
        ctx.err("[ERROR] -BDNN_mean_shap_per_group without -BDNN_groups: %s — it changes "
                "how the states of a group are aggregated." % cite("BDNN_mean_shap_per_group"))
    if has("BDNN_groups") and has("BDNN_pred_importance_interaction"):
        ctx.err("[ERROR] -BDNN_groups with -BDNN_pred_importance_interaction: %s (%s)."
                % (cite("BDNN_groups_pi"), cite("BDNN_pred_importance_interaction")))
    for nm in PRED_IMPORTANCE_OPTIONS:
        if has(nm) and not has("BDNN_pred_importance"):
            ctx.err("[ERROR] -%s without -BDNN_pred_importance: it is one of that "
                    "command's optional arguments (%s; usage: %s)."
                    % (nm, cite(nm), cite("BDNN_pred_importancecmd")))
    if has("plotBDNN_transf_features") and not any(
            has(c) for c in ("plotBDNN_effects", "BDNN_interaction",
                             "BDNN_pred_importance")):
        ctx.err("[ERROR] -plotBDNN_transf_features without -plotBDNN_effects/"
                "-BDNN_interaction/-BDNN_pred_importance: %s — it is a post-processing "
                "option and '%s' (%s)."
                % (cite("transffeat"), CITE["transffeatnote"][2][:48],
                   CITE["transffeatnote"][0] + ":" + str(CITE["transffeatnote"][1])))
    # utility mode: no analysis commands as companions
    util = [c for c in ctx.ordered if c in UTILITY_CMDS]
    if util:
        bad = [c for c in ctx.ordered
               if c in META and c not in UTILITY_ALLOWED_EXTRA and c != "d"]
        if bad:
            ctx.err("[ERROR] -%s with analysis command(s) %s: the corpus always shows "
                    "summarising commands on their own line (e.g. %s; only -b/-tag/"
                    "-qShift/-out/-wd and -logT are shown alongside -logT for "
                    "-plotBDNN per %s); companions shown: %s, %s."
                    % (util[0], " ".join("-" + b for b in bad), cite("mProb"),
                       cite("logTplot"), cite("plotQ"), cite("combLog")))


# ------------------------------------------------------------------- command build

def build(argv):
    pre = argparse.ArgumentParser(prog="build_command.py", add_help=False,
                                  description="Assemble a validated PyRate command "
                                  "line from typed arguments (never executes it).")
    pre.add_argument("--mirror", default=DEFAULT_MIRROR)
    pre.add_argument("--json", action="store_true")
    pre.add_argument("--dry-run", action="store_true")
    pre.add_argument("--self-test", action="store_true")
    pre.add_argument("--list", action="store_true")
    pre.add_argument("--core-only", action="store_true")
    pre.add_argument("--python-exe", default="python")
    pre.add_argument("--program", default=SUPPORTED_PROGRAM)
    pre.add_argument("--help", action="store_true")
    known, rest = pre.parse_known_args(argv)
    if known.help:
        return {"rc": 0, "help": True}
    if known.self_test:
        return {"rc": self_test(known.mirror), "selftest": True}
    if not program_ok(known.program):
        # usage error, checked before any I/O so it is reported the same way
        # wherever the tool is installed from
        return {"rc": 4, "errors": program_refusal(known.program),
                "program": known.program, "supported_program": SUPPORTED_PROGRAM,
                "json": known.json}
    try:
        order, parsed = parse_mirror(known.mirror)
    except (IOError, OSError):
        return {"rc": 3, "json": known.json,
                "errors": ["[ERROR] cannot read command mirror %s — pass "
                           "--mirror PATH." % known.mirror]}
    if not parsed:
        return {"rc": 3, "json": known.json,
                "errors": ["[ERROR] no commands parsed from %s — mirror format "
                           "unexpected." % known.mirror]}

    if known.list:
        rows = []
        for name in order:
            meta = META.get(name, {})
            rows.append("-%-12s arity=%-6s kind=%-6s %s:%d"
                        % (name, fmt_arity(meta.get("arity", "parsed")),
                           meta.get("kind", "?"),
                           MIRROR_LABEL, parsed[name]["start_line"]))
        if not known.core_only:
            for name in sorted(EXTENSIONS):
                rel, line, _q = CITE[EXTENSIONS[name]["cite"]]
                rows.append("-%-12s arity=%-6s kind=%-6s [outside the command list] %s:%d"
                            % (name, fmt_arity(EXTENSIONS[name]["arity"]),
                               EXTENSIONS[name]["kind"], rel, line))
        return {"rc": 0, "list": rows, "mirror": known.mirror, "json": known.json,
                "count_core": len(order),
                "grammar": "the options of %s only; --program refuses every other "
                           "program of the family (%s)"
                           % (SUPPORTED_PROGRAM,
                              ", ".join(p for p, _d in PROGRAM_DOCS))}

    arity_notes = {}
    nargs_map = {name: resolve_arity(name, parsed[name], META.get(name), arity_notes)
                 for name in order}

    ap = argparse.ArgumentParser(prog="build_command.py", add_help=False)
    ap.add_argument("input_files", nargs="*")
    names = list(order) + ([] if known.core_only else list(EXTENSIONS))
    for name in names:
        meta = META.get(name) or EXTENSIONS.get(name)
        n = nargs_map.get(name, meta["arity"])
        opts = {"dest": "cmd_" + name}
        if n == 0:
            opts["action"] = "store_true"
        else:
            # variadic arities (min, max) use nargs="+" and are range-checked
            # in check_value() with their citation (tuple nargs needs py>=3.9
            # AND its error output would bypass our citing messages)
            opts["nargs"] = "+" if isinstance(n, tuple) else n
            opts["metavar"] = "VAL"
        try:
            ap.add_argument("-" + name, **opts)
        except argparse.ArgumentError:
            continue  # duplicate heading in the mirror; first occurrence wins
    import contextlib
    import io
    err_buf = io.StringIO()
    try:
        with contextlib.redirect_stderr(err_buf):
            ns = ap.parse_args(rest)
    except SystemExit as exc:
        reason = (err_buf.getvalue().strip().splitlines() or ["argparse usage error"])[-1]
        return {"rc": 4, "json": known.json,
                "errors": ["[ERROR] usage error: unknown flag or wrong number of "
                           "values — %s Full set: run with --list. Only flags parsed "
                           "from %s%s are accepted — the grammar of %s; if you meant "
                           "another program of the family, --program will not help, see "
                           "the GRAMMAR SCOPE note in --help."
                           % (reason, shown_path(known.mirror),
                              "" if known.core_only else " + the cited EXTENSIONS",
                              SUPPORTED_PROGRAM)]}

    ctx = Ctx()
    positionals = list(ns.input_files)
    for name in names:
        v = getattr(ns, "cmd_" + name, None)
        if v in (None, False):
            continue
        ctx.values[name] = True if v is True else list(v)
    ctx.ordered = [n for n in order if n in ctx.values] + \
                  [n for n in EXTENSIONS if n in ctx.values]

    for name in ctx.ordered:
        meta = META.get(name) or EXTENSIONS.get(name)
        v = ctx.values[name]
        if v is not True:
            check_value(name, meta, v, ctx, known.core_only)

    inp = positionals[0] if positionals else None
    util = [c for c in ctx.ordered if c in UTILITY_CMDS]
    if len(positionals) > 1:
        ctx.err("[ERROR] multiple input files %s: the documented invocation takes ONE "
                "input (%s)." % (positionals, cite("invocation")))
    if inp is not None and util:
        ctx.err("[ERROR] -%s with a separate positional input: documented usage passes "
                "the file as -%s's own argument (%s)." % (util[0], util[0],
                                                          cite(util[0])))
    mode = "utility" if util else "analysis"
    if mode == "analysis":
        if inp is None and not ctx.has("d"):
            ctx.err("[ERROR] no input: give the PyRate input file as the first argument "
                    "(%s) or an origin/extinction table via -d (%s)."
                    % (cite("inputfile"), cite("dalt")))
        if inp is not None and ctx.has("d"):
            ctx.err("[ERROR] input file AND -d given: %s — use one data source."
                    % cite("dalt"))
        if ctx.has("data_info") and inp is None:
            ctx.err("[ERROR] -data_info needs the input file as positional argument: %s"
                    % cite("data_info"))
        if ctx.has("data_info"):
            others = [c for c in ctx.ordered if c not in ("data_info", "singleton", "j",
                                                          "out", "wd")]
            if others:
                ctx.warn("[WARN] -data_info plus analysis command(s) %s: the corpus only "
                         "shows -data_info with an input file (and -singleton, %s:%d); "
                         "analysis flags alongside are undocumented."
                         % (" ".join("-" + o for o in others), MIRROR_LABEL,
                            CITE["datainfosync"][1]))
    apply_rules(ctx, known.core_only)

    parts = [known.python_exe, known.program]
    if util:
        u = util[0]
        parts.append("-" + u)
        if ctx.values[u] is not True:
            parts.extend(ctx.values[u])
    if inp:
        parts.append(inp)
    for name in ctx.ordered:
        if name in util:
            continue
        parts.append("-" + name)
        if ctx.values[name] is not True:
            parts.extend(ctx.values[name])
    line = " ".join(parts)

    return {
        "rc": 2 if ctx.errors else 0,
        "json": known.json,
        "command_line": line,
        "errors": ctx.errors, "warnings": ctx.warnings, "notes": ctx.notes,
        "parse_warnings": [arity_notes[n] for n in ctx.ordered if n in arity_notes],
        "mode": mode, "python_exe": known.python_exe, "program": known.program,
        "input": inp,
        "d_table": (ctx.raw("d") or [None])[0],
        "mirror": known.mirror, "commands_in_mirror": len(order),
        "dry_run": known.dry_run, "core_only": known.core_only,
        "checked": ctx.ordered,
    }


def render(res):
    out = list(res.get("parse_warnings", []))
    for kind in ("errors", "warnings", "notes"):
        out.extend(res.get(kind, []))
    if res.get("rc") == 0:
        if res.get("dry_run"):
            out.append("Dry-run report: nothing executed; line validated against %s "
                       "(%d commands parsed; mode: %s)."
                       % (res["mirror"], res["commands_in_mirror"], res["mode"]))
            out.append("Checked commands: %s"
                       % (", ".join("-" + c for c in res["checked"]) or "(none)"))
        out.append("COMMAND: %s" % res["command_line"])
        if not res.get("dry_run"):
            out.append("(assembled line only — nothing executed)")
    return "\n".join(out)


# ---------------------------------------------------------------- self test

def _mirror_text(rel_path):
    if rel_path == MIRROR_LABEL:
        path = os.path.join(SKILL_DIR, rel_path)
    else:
        path = os.path.join(SUITE_DIR, rel_path.split("../", 1)[1])
    try:
        with open(path, encoding="utf-8") as fh:
            return path, fh.read().splitlines()
    except (IOError, OSError):
        return path, None


# ------------------------------------------------------------- corpus replay
# Every `python [path/]PyRate.py ...` line inside a fenced code block of any
# SKILL.md or references/*.md in the suite must assemble through build().
LAUNCH_RE = re.compile(r"^\s*python3?\s+\S*\bPyRate\.py\b")
FLAG_RE = re.compile(r"-[A-Za-z][A-Za-z0-9_]*\Z")
COMMENT_RE = re.compile(r"\s+#\s.*\Z")   # trailing shell comment, ' #' after a space

# VISIBLE allow-list: candidate lines the replay skips, each with a reason.
# An entry that matches nothing is itself a self-test failure, so a skip can
# never rot into a silent one.
REPLAY_ALLOW = [
    {"path": r"pyrate/SKILL\.md", "line": 57,
     "reason": "general syntax pattern 'python PyRate.py <file> [commands]' transcribed "
               "verbatim from the corpus's own invocation syntax, whose input is itself a "
               "placeholder path and which carries the literal '[commands]' "
               "meta-placeholder, not a runnable command line"},
]


def corpus_command_lines(suite_dir):
    """Yield (relpath, start_line, joined_command_text) for fenced launch lines."""
    out = []
    try:
        children = sorted(os.listdir(suite_dir))
    except OSError:
        return out
    for sk in children:
        skill_dir = os.path.join(suite_dir, sk)
        if not os.path.isfile(os.path.join(skill_dir, "SKILL.md")):
            continue
        paths = [os.path.join(skill_dir, "SKILL.md")]
        rd = os.path.join(skill_dir, "references")
        if os.path.isdir(rd):
            paths += [os.path.join(rd, f) for f in sorted(os.listdir(rd))
                      if f.endswith(".md")]
        for p in paths:
            try:
                with open(p, encoding="utf-8") as fh:
                    lines = fh.read().splitlines()
            except (IOError, OSError):
                continue
            infence = False
            i = 0
            while i < len(lines):
                if lines[i].lstrip().startswith("```"):
                    infence = not infence
                    i += 1
                    continue
                if infence and LAUNCH_RE.search(lines[i]):
                    start = i + 1
                    buf = lines[i]
                    while buf.rstrip().endswith("\\") and i + 1 < len(lines):
                        i += 1
                        buf = buf.rstrip()[:-1] + " " + lines[i]
                    out.append((os.path.relpath(p, suite_dir), start, buf.strip()))
                i += 1
    return out


def corpus_replay(mirror_path):
    """Return (n_replayed, n_allowlisted, failure_messages)."""
    order, parsed = parse_mirror(mirror_path)
    accepted = set(order) | set(EXTENSIONS)
    failures, n, n_allow = [], 0, set()
    for rel, line, text in corpus_command_lines(SUITE_DIR):
        prog_tok = None
        for cand in shlex_pre_tokens(text):
            if cand.endswith("PyRate.py"):
                prog_tok = cand
                break
        if prog_tok is None:
            failures.append("%s:%d: no PyRate.py program token in %r" % (rel, line, text))
            continue
        stripped = COMMENT_RE.sub("", text)
        why = None
        try:
            toks = shlex.split(stripped)
        except ValueError as exc:
            toks = None
            why = "shlex cannot tokenise (%s)" % exc
        if toks is not None:
            # tokens after the program file
            tail = toks[toks.index(prog_tok) + 1:]
            refused = sorted({t[1:] for t in tail
                              if FLAG_RE.fullmatch(t) and t[1:] not in accepted})
            if refused:
                why = ("refused flag token(s): %s (not in the parsed command list or "
                       "the cited EXTENSIONS)" % ", ".join("-" + r for r in refused))
            else:
                res = build(["--mirror", mirror_path] + tail)
                if res["rc"] == 0:
                    n += 1
                    continue
                why = ("assembles to rc=%d: %s"
                       % (res["rc"], " | ".join(res.get("errors", []))[:300]))
        hit = [e for e in REPLAY_ALLOW
               if e["line"] == line and re.search(e["path"], rel.replace(os.sep, "/"))]
        if hit:
            n_allow.add(rel + ":" + str(line))
            continue
        failures.append("%s:%d: documented command line cannot be replayed — %s :: %r "
                        "(allow-list it in REPLAY_ALLOW with a reason only if the line "
                        "is genuinely not a PyRate.py command)" % (rel, line, why, text))
    unused = [e for e in REPLAY_ALLOW
              if not any(re.search(e["path"], f.rsplit(":", 1)[0])
                         and f.endswith(":" + str(e["line"])) for f in n_allow)]
    for e in unused:
        failures.append("REPLAY_ALLOW entry for %s line %d is unused (%s) — delete it "
                        "or fix the line number" % (e["path"], e["line"], e["reason"]))
    return n, len(n_allow), failures


def shlex_pre_tokens(text):
    try:
        return shlex.split(COMMENT_RE.sub("", text))
    except ValueError:
        return text.split()


def self_test(mirror_path=None):
    errors = []
    counters = {"checks": 0}

    def expect(cond, msg):
        counters["checks"] += 1
        if not cond:
            errors.append(msg)


    mp = mirror_path or DEFAULT_MIRROR

    # 1. CITATION AUDIT: every quote must actually sit at its file:line
    bad = []
    cache = {}
    for key, (rel, line, quote) in CITE.items():
        if rel not in cache:
            cache[rel] = _mirror_text(rel)
        path, lines = cache[rel]
        if lines is None:
            bad.append("%s: missing mirror file %s" % (key, path))
            continue
        window = norm(" ".join(lines[line - 1:line + 1]))  # quote may cross one newline
        if norm(quote) not in window:
            bad.append("%s: quote not at %s:%d — %r" % (key, rel, line, quote[:70]))
    expect(not bad, "citation audit failures:\n  " + "\n  ".join(bad))

    # 2. MIRROR PARSING reproduces the inventory and arities
    order, parsed = parse_mirror(mp)
    for must in ("A", "n", "s", "p", "b", "mHPP", "qShift", "mG", "ncat", "fixSE",
                 "mL", "mM", "mC", "mCov", "cauchy", "thread", "fU", "tC", "tQ",
                 "singleton", "d", "wd", "out", "j", "pL", "pM", "pP", "pS", "pC",
                 "r", "t", "sw", "k", "a", "M", "B", "T", "S", "multiR", "tT", "nT",
                 "tR", "tS", "fS", "fR", "fixShift", "trait", "trait_file", "logT", "N"):
        expect(must in parsed, "mirror parse lost command -%s" % must)
    arity_notes = {}
    arities = {n: resolve_arity(n, parsed[n], META.get(n), arity_notes) for n in order}
    expect(arities["mG"] == 0 and arities["mHPP"] == 0 and arities["mC"] == 0,
           "flags must parse to arity 0")
    expect(arities["pL"] == 2 and arities["cauchy"] == 2 and arities["thread"] == 2
           and arities["pP"] == 2 and arities["tQ"] == 2,
           "2-value commands parsed wrong: %r"
           % {k: arities[k] for k in ("pL", "cauchy", "thread", "pP", "tQ")})
    expect(arities["tC"] == 3 and arities["fU"] == 3,
           "3-value commands parsed wrong: %r"
           % {k: arities[k] for k in ("tC", "fU")})
    expect(arities["ncat"] == 1 and arities["j"] == 1 and arities["mCov"] == 1
           and arities["trait_file"] == 1 and arities["d"] == 1 and arities["A"] == 1,
           "1-value commands parsed wrong: %r"
           % {k: arities[k] for k in ("ncat", "j", "mCov", "trait_file", "d", "A")})
    expect(arities["pM"] == 2, "-pM must fall back to arity 2 (docs typo)")

    # 3. BEHAVIOUR SCENARIOS
    def run(args):
        return build(["--mirror", mp] + args)

    r = run(["in_PyRate.py", "-ncat", "4"])
    expect(r["rc"] == 2, "-ncat without -mG must fail")
    msg = " ".join(r["errors"])
    expect("This command is used only when running under a Gamma model of preservation "
           "(i.e. with -mG)" in msg and "command-list.md:101" in msg,
           "error must quote the mirror: %r" % r["errors"])
    r = run(["in_PyRate.py", "-mG", "-ncat", "4"])
    expect(r["rc"] == 0 and "-mG -ncat 4" in r["command_line"],
           "-mG -ncat 4 must pass: %r" % r)
    r = run(["in_PyRate.py", "-A", "0", "-r", "4", "-t", "0.03", "-sw", "100"])
    expect(r["rc"] == 0, "MC3 combo must pass: %r" % r["errors"])
    r = run(["in_PyRate.py", "-A", "2", "-r", "4"])
    expect(r["rc"] == 2 and "-A 0" in " ".join(r["errors"]),
           "-r with -A 2 must fail quoting -A 0")
    r = run(["in_PyRate.py", "-t", "0.03"])
    expect(r["rc"] == 2, "-t without -r>1 must fail")
    r = run(["in_PyRate.py", "-A", "1", "-k", "10", "-a", "0.3"])
    expect(r["rc"] == 0, "TI combo must pass")
    r = run(["in_PyRate.py", "-mM", "3", "-B", "10"])
    expect(r["rc"] == 0 and any("-B" in w for w in r["warnings"]),
           "-B without explicit -A 2 must warn: %r" % r)
    r = run(["in_PyRate.py", "-N", "24", "-pL", "1.1", "1.1"])
    expect(r["rc"] == 2 and "if used only if the number of extant taxa"
           in " ".join(r["errors"]), "-pL with -N 24 must fail quoting the doc")
    r = run(["in_PyRate.py", "-N", "-1", "-pL", "1.1", "1.1"])
    expect(r["rc"] == 0, "-pL with -N -1 must pass: %r" % r["errors"])
    r = run(["in_PyRate.py", "-mHPP", "-qShift", "epochs_q.txt"])
    expect(r["rc"] == 2, "mHPP+qShift must fail")
    r = run(["in_PyRate.py", "-nT", "0", "-qShift", "epochs_q.txt"])
    expect(r["rc"] == 2, "-nT 0 + -qShift must fail (HPP auto-set)")
    r = run(["-d", "ursidae_se.txt", "-fixSE", "null"])
    expect(r["rc"] == 2, "-d + -fixSE must fail")
    r = run(["-d", "ursidae_se.txt", "-n", "1000"])
    expect(r["rc"] == 0 and r["command_line"].startswith("python PyRate.py -d "
           "ursidae_se.txt"), "-d as sole input must pass: %r" % r["command_line"])
    r = run(["in_PyRate.py", "-d", "table.txt"])
    expect(r["rc"] == 2, "positional input + -d must fail")
    r = run(["in_PyRate.py", "-A", "9"])
    expect(r["rc"] == 2 and "documented set" in " ".join(r["errors"]), "-A 9 must fail")
    r = run(["in_PyRate.py", "-A", "4"])
    expect(r["rc"] == 0 and any("tutorial-1.md:174" in n for n in r["notes"]),
           "-A 4 must be accepted with the tutorial-1 citation note: %r" % r)
    r = build(["--mirror", mp, "--core-only", "in_PyRate.py", "-A", "4"])
    expect(r["rc"] == 2 and "core-only" in " ".join(r["errors"]),
           "--core-only must refuse -A 4")
    r = run(["in_PyRate.py", "-pC", "0", "-mCov", "5"])
    expect(r["rc"] == 0, "-pC 0 -mCov 5 must pass: %r" % r["errors"])
    r = run(["in_PyRate.py", "-pC", "0", "-mCov", "1"])
    expect(r["rc"] == 2, "-pC 0 -mCov 1 must fail (doc garbled, rule by inference)")
    r = run(["in_PyRate.py", "-mC", "-mL", "1"])
    expect(r["rc"] == 2, "-mC with -mL 1 must fail")
    r = run(["in_PyRate.py", "-mL", "2", "-mM", "2", "-mC"])
    expect(r["rc"] == 0, "-mL 2 -mM 2 -mC must pass")
    r = run(["in_PyRate.py", "-data_info"])
    expect(r["rc"] == 0 and r["command_line"] ==
           "python PyRate.py in_PyRate.py -data_info", "-data_info form wrong: %r"
           % r["command_line"])
    r = run(["-data_info"])
    expect(r["rc"] == 2, "-data_info without input must fail")
    r = run(["in_PyRate.py", "-mProb", "x_mcmc.log"])
    expect(r["rc"] == 2, "-mProb + positional input must fail")
    r = run(["-mProb", "x_mcmc.log", "-b", "200"])
    expect(r["rc"] == 0 and r["command_line"] ==
           "python PyRate.py -mProb x_mcmc.log -b 200",
           "utility assembly wrong: %r" % r["command_line"])
    r = run(["-plotQ", "x_mcmc.log", "-b", "100"])
    expect(r["rc"] == 2, "-plotQ without -qShift must fail")
    r = run(["-plotQ", "x_mcmc.log", "-qShift", "epochs_q.txt", "-b", "100"])
    expect(r["rc"] == 0, "documented -plotQ usage must pass: %r" % r["errors"])
    r = run(["-combLog", "dir", "-tag", "mcmc", "-b", "100"])
    expect(r["rc"] == 0, "-combLog -tag must pass")
    r = run(["in_PyRate.py", "-tag", "rhinos"])
    expect(r["rc"] == 2, "-tag alone must fail")
    r = run(["in_PyRate.py", "-A", "4", "-edgeShift", "inf", "0"])
    expect(r["rc"] == 0, "-edgeShift inf 0 with -A 4 must pass: %r" % r["errors"])
    r = run(["-d", "se.txt", "-ltt", "1", "-grid_plot", "0.1"])
    expect(r["rc"] == 0, "documented -ltt usage must pass: %r" % r["errors"])
    r = run(["in_PyRate.py", "-ltt", "1"])
    expect(r["rc"] == 2, "-ltt without -d must fail")
    r = run(["in_PyRate.py", "-qShift", "e_q.txt", "-mG", "-log_sp_q_rates"])
    expect(r["rc"] == 0, "TPP+Gamma+log_sp_q_rates must pass: %r" % r["errors"])
    r = run(["in_PyRate.py", "-log_sp_q_rates"])
    expect(r["rc"] == 2, "-log_sp_q_rates alone must fail")
    r = run(["in_PyRate.py", "-PPmodeltest"])
    expect(r["rc"] == 2, "-PPmodeltest without -qShift must fail")
    r = run(["in_PyRate.py", "-zzz"])
    expect(r["rc"] == 4, "unknown flag must give usage rc=4")
    r = run([])
    expect(r["rc"] == 2, "no input must fail")
    r = run(["in_PyRate.py", "-pL", "1.1"])
    expect(r["rc"] == 4, "wrong arity must be refused (nargs=2)")
    r = run(["in_PyRate.py", "-fixSE", "null"])
    expect(r["rc"] == 0, "-fixSE null must be accepted")
    r = run(["in_PyRate.py", "-j", "x"])
    expect(r["rc"] == 2 and "expected int" in " ".join(r["errors"]),
           "-j x must fail type check")
    r = run(["in_PyRate.py", "-mCov", "7"])
    expect(r["rc"] == 2, "-mCov 7 must be outside documented set")
    r = run(["in_PyRate.py", "-b", "0.1"])
    expect(r["rc"] == 0 and any("fraction of the total" in n for n in r["notes"]),
           "-b 0.1 fraction note missing: %r" % r["notes"])
    r = run(["-mProb", "x.log", "-mG"])
    expect(r["rc"] == 2, "utility+analysis mixing must fail")

    # 4. CORPUS REPLAY — every documented `python …PyRate.py …` command line
    n_replay, n_allow, rfails = corpus_replay(mp)
    expect(n_replay > 80, "corpus replay assembled only %d command lines — if the "
                          "scanner broke, a regression would slip through" % n_replay)
    for m in rfails:
        errors.append("corpus replay: " + m)

    # 5. BDNN / RJMCMC / ADE extension scenarios
    r = run(["in_PyRate.py", "-BDNNmodel", "1", "-trait_file", "t.txt",
             "-BDNNtimevar", "a.txt", "-mG", "-qShift", "s.txt", "-n", "200001"])
    expect(r["rc"] == 0, "documented BDNN run line must pass: %r" % r["errors"])
    r = run(["in_PyRate.py", "-BDNNmodel", "1", "-BDNNtimevar", "a.txt", "b.txt"])
    expect(r["rc"] == 0, "-BDNNtimevar with two time-series must pass (:205): %r"
           % r["errors"])
    r = run(["in_PyRate.py", "-BDNNtimevar", "a.txt"])
    expect(r["rc"] == 2 and "-BDNNmodel" in " ".join(r["errors"]),
           "-BDNNtimevar without -BDNNmodel must fail: %r" % r["errors"])
    r = run(["in_PyRate.py", "-BDNNmodel", "1", "-BDNNpath_taxon_time_tables",
             "p1", "p2", "-trait_file", "t.txt"])
    expect(r["rc"] == 2 and "No additional" in " ".join(r["errors"]),
           "-BDNNpath_taxon_time_tables + -trait_file must fail quoting :411")
    r = run(["-plotBDNN", "x_mcmc.log", "-b", "0.1"])
    expect(r["rc"] == 0 and r["command_line"] ==
           "python PyRate.py -plotBDNN x_mcmc.log -b 0.1",
           "-plotBDNN utility form wrong: %r" % r["command_line"])
    r = run(["-plotBDNN", "x_mcmc.log", "-min_age_plot", "2.6", "-root_plot", "15.9",
             "-b", "0.5"])
    expect(r["rc"] == 0, "documented -plotBDNN truncation line must pass: %r"
           % r["errors"])
    r = run(["-combBDNN", "logs", "-b", "0.25"])
    expect(r["rc"] == 0, "-combBDNN must pass")
    r = run(["-combLogRJ", "logs", "-b", "1000", "-tag", "Canis", "-resample", "100"])
    expect(r["rc"] == 0, "-combLogRJ -tag -resample must pass: %r" % r["errors"])
    r = run(["-plotRJ", "logs", "-b", "200", "-root_plot", "23", "-min_age_plot", "5.3"])
    expect(r["rc"] == 0, "-plotRJ truncation line must pass: %r" % r["errors"])
    r = run(["in_PyRate.py", "-BDNNmodel", "1", "-BDNN_groups", '{"a": ["b"]}',
             "-BDNN_pred_importance_interaction"])
    expect(r["rc"] == 2 and "not in combination" in " ".join(r["errors"]),
           "-BDNN_groups + -BDNN_pred_importance_interaction must fail quoting :364")
    r = run(["-BDNN_pred_importance", "x_mcmc.log", "-BDNN_pred_importance_nperm", "23",
             "-BDNN_nsim_expected_cv", "7", "-resample", "10", "-b", "0.1"])
    expect(r["rc"] == 0, "documented -BDNN_pred_importance line must pass: %r"
           % r["errors"])
    r = run(["-BDNN_pred_importance", "x_mcmc.log", "-BDNN_nsim_expected_cv", "7"])
    expect(r["rc"] == 0, "-BDNN_nsim_expected_cv under -BDNN_pred_importance must pass")
    r = run(["in_PyRate.py", "-BDNN_nsim_expected_cv", "7"])
    expect(r["rc"] == 2, "-BDNN_nsim_expected_cv alone must fail")
    r = run(["-BDNN_interaction", "x_mcmc.log", "-BDNN_interaction_fix", "-resample",
             "3", "-b", "0.5"])
    expect(r["rc"] == 0, "-BDNN_interaction_fix line must pass: %r" % r["errors"])
    r = run(["in_PyRate.py", "-BDNN_interaction_fix"])
    expect(r["rc"] == 2, "-BDNN_interaction_fix alone must fail")
    r = run(["in_PyRate.py", "-BDNNmodel", "1", "-BDNNnodes", "16", "8"])
    expect(r["rc"] == 0, "-BDNNnodes 16 8 must pass")
    r = run(["in_PyRate.py", "-BDNNmodel", "1", "-BDNNnodes", "30", "20", "10"])
    expect(r["rc"] == 0, "-BDNNnodes 30 20 10 must pass (:381 three layers)")
    r = run(["in_PyRate.py", "-BDNNmodel", "1", "-BDNNnodes", "8"])
    expect(r["rc"] == 2 and "documents 2-3 values" in " ".join(r["errors"]),
           "-BDNNnodes with one value must fail with the documented range")
    r = run(["in_PyRate.py", "-qFilter", "0", "-qShift", "e.txt", "-mG"])
    expect(r["rc"] == 2 and "-BDNNmodel" in " ".join(r["errors"]),
           "-qFilter is a BDNN inference flag: must fail without -BDNNmodel")
    r = run(["-d", "se.txt", "-A", "4", "-min_dt", "0.5"])
    expect(r["rc"] == 0, "-min_dt line must pass: %r" % r["errors"])
    r = build(["--mirror", mp, "--core-only", "in_PyRate.py", "-min_dt", "0.5"])
    expect(r["rc"] == 4, "--core-only must refuse -min_dt")
    r = run(["in_PyRate.py", "-ADE", "1", "-qShift", "epochs.txt", "-filter", "23.03",
             "5.3"])
    expect(r["rc"] == 0, "documented ADE line must pass: %r" % r["errors"])
    r = run(["in_PyRate.py", "-ADE", "1", "-mG", "-qShift", "epochs.txt"])
    expect(r["rc"] == 2 and "HPP" in " ".join(r["errors"]),
           "-ADE with -mG must fail quoting :143")
    r = run(["in_PyRate.py", "-filter", "23.03", "5.3"])
    expect(r["rc"] == 2, "-filter without -ADE must fail")
    r = run(["in_PyRate.py", "-tree", "f.tre", "-bdc", "-eqr"])
    expect(r["rc"] == 0, "BDC line must pass: %r" % r["errors"])
    r = run(["in_PyRate.py", "-restore_mcmc", "x_mcmc.log", "-BDNNmodel", "1"])
    expect(r["rc"] == 0, "-restore_mcmc line must pass: %r" % r["errors"])
    r = run(["-v"])
    expect(r["rc"] == 0 and r["command_line"] == "python PyRate.py -v",
           "-v probe must assemble: %r" % r)
    r = run(["in_PyRate.py", "-fast_burnin", "0", "-A", "0"])
    expect(r["rc"] == 0, "-fast_burnin must pass: %r" % r["errors"])
    r = run(["-plot", "logs", "-tag", "rhinos", "-root_age", "23"])
    expect(r["rc"] == 0, "-root_age with -plot/-tag must pass: %r" % r["errors"])
    r = run(["in_PyRate.py", "-var", "folder"])
    expect(r["rc"] == 0 and any("PyRateMBD.py" in note for note in r["notes"]),
           "-var must assemble with the PyRateMBD.py note: %r" % r)
    r = run(["in_PyRate.py", "-BDNNmodel", "1", "-plotBDNN_transf_features", "b.txt"])
    expect(r["rc"] == 2 and "-plotBDNN_effects" in " ".join(r["errors"]),
           "-plotBDNN_transf_features needs a post-processing host")
    r = run(["in_PyRate.py", "-resample", "100"])
    expect(r["rc"] == 2, "-resample without a host must fail")
    r = run(["in_PyRate.py", "-BDNNmodel", "5"])
    expect(r["rc"] == 0 and any("beyond the documented examples" in w
                                for w in r["warnings"]),
           "-BDNNmodel 5 must warn: only -BDNNmodel 1 is documented: %r" % r["warnings"])

    # 6. GRAMMAR SCOPE — --program renames nothing, because it cannot switch
    #    grammars: only the program whose page this tool parses is accepted.
    expect("GRAMMAR SCOPE" in __doc__ and "--program" in __doc__
           and "--python-exe" in __doc__,
           "--help must document its own options and state the grammar scope; the "
           "docstring lacks one of GRAMMAR SCOPE / --program / --python-exe")
    r = build(["--mirror", mp, "in_PyRate.py", "-mG"])
    expect(r["rc"] == 0 and r["command_line"].startswith("python %s " % SUPPORTED_PROGRAM),
           "the default program must be %s: %r" % (SUPPORTED_PROGRAM, r))
    for form in ("PyRate.py", "./PyRate.py", "../PyRate-3.0.0/PyRate.py"):
        rr = build(["--mirror", mp, "--program", form, "in_PyRate.py", "-mG"])
        expect(rr["rc"] == 0 and rr["command_line"].startswith("python %s " % form),
               "--program %s (a path to %s) must still be accepted: %r"
               % (form, SUPPORTED_PROGRAM, rr))
    rr = build(["--mirror", mp, "--python-exe", "python2", "in_PyRate.py", "-mG"])
    expect(rr["rc"] == 0 and rr["command_line"] == "python2 PyRate.py in_PyRate.py -mG",
           "--python-exe must rename the launcher token only: %r" % rr)
    for prog, doc in PROGRAM_DOCS:
        rr = build(["--mirror", mp, "--program", prog, "in_PyRate.py", "-A", "2"])
        expect(rr["rc"] == 4,
               "--program %s must exit 4 (this tool does not carry its grammar), got "
               "%d :: %r" % (prog, rr["rc"], rr.get("command_line")))
        expect("command_line" not in rr,
               "a refused --program must not print a COMMAND line: %s -> %r"
               % (prog, rr.get("command_line")))
        text = " ".join(rr["errors"])
        expect(SUPPORTED_PROGRAM in text,
               "the refusal of %s must name the one supported program: %r"
               % (prog, rr["errors"]))
        expect(doc in text,
               "the refusal of %s must point at the page documenting its options (%s): %r"
               % (prog, doc, rr["errors"]))
        path, lines = _mirror_text(doc)
        expect(lines is not None,
               "PROGRAM_DOCS points at an unreadable page for %s: %s" % (prog, path))
        if lines is not None:
            expect(any(prog in ln for ln in lines),
                   "%s never mentions %s, so the refusal message names the wrong page"
                   % (doc, prog))
    rr = build(["--mirror", mp, "--program", "PyRateContinuous.py",
                "-d", "x.txt", "-m", "1", "-c", "temp.txt"])
    expect(rr["rc"] == 4 and any("GRAMMAR SCOPE" in e or "grammar" in e
                                 for e in rr["errors"]),
           "the reported --program repro must be refused with the scope explained: %r"
           % rr)
    txt = render(build(["--mirror", mp, "--program", "PyRateDES.py", "-d", "x.txt"]))
    expect("COMMAND" not in txt and txt.startswith("[ERROR]"),
           "render() must print the refusal and no command line: %r" % txt[:160])
    own = set(order) | set(EXTENSIONS)
    for f in FOREIGN_FLAGS:
        expect(f not in own,
               "-%s is documented for another program yet accepted here: the grammar "
               "scope statement is out of date" % f)
        rr = build(["--mirror", mp, "in_PyRate.py", "-" + f, "1"])
        expect(rr["rc"] == 4, "-%s must be refused by the %s grammar, got rc %d"
               % (f, SUPPORTED_PROGRAM, rr["rc"]))
    rr = build(["--mirror", mp, "--core-only", "--program", "PyRateMBD.py",
                "in_PyRate.py", "-mG"])
    expect(rr["rc"] == 4, "--core-only must not widen the accepted programs: %r" % rr)

    # 6b. --json emits the documented single object on every report path
    import contextlib
    import io

    def cli(args):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = main(["--mirror", mp] + args)
        return rc, buf.getvalue()

    rc, out = cli(["--json", "in_PyRate.py", "-mG"])
    obj = None
    try:
        obj = json.loads(out)
    except ValueError as exc:
        expect(False, "--json must print exactly one JSON object, got %r (%s)"
               % (out[:160], exc))
    expect(rc == 0 and obj and obj.get("command_line")
           == "python PyRate.py in_PyRate.py -mG"
           and obj.get("program") == SUPPORTED_PROGRAM,
           "--json payload wrong: rc=%d %r" % (rc, out[:160]))
    rc, out = cli(["--json", "in_PyRate.py", "-ncat", "4"])
    expect(rc == 2 and json.loads(out)["errors"],
           "--json must carry the rejection too: rc=%d %r" % (rc, out[:160]))
    rc, out = cli(["--json", "--program", "PyRateContinuous.py", "in_PyRate.py", "-mG"])
    obj = json.loads(out)
    expect(rc == 4 and obj["rc"] == 4 and "PyRateContinuous.py" in " ".join(obj["errors"]),
           "--json must report a refused --program: rc=%d %r" % (rc, out[:200]))
    rc, out = cli(["--list"])
    first = out.splitlines()[0] if out.splitlines() else ""
    expect(rc == 0 and first.startswith("Commands parsed from ")
           and "Grammar: the options of %s only" % SUPPORTED_PROGRAM in out
           and "PyRateDES.py" in out,
           "--list must open with its banner and close with the scope it refuses: %r"
           % out[-200:])
    expect(not any(p in first for p, _d in PROGRAM_DOCS),
           "the --list banner must name only the page it parses, not the refused "
           "programs: %r" % first)

    # json serializability of every report shape
    for a in (["in_PyRate.py", "-mG"], ["in_PyRate.py", "-ncat", "4"]):
        rr = run(a)
        json.dumps({k: v for k, v in rr.items()})
    txt = render(run(["in_PyRate.py", "-mG"]))
    expect("COMMAND: python PyRate.py in_PyRate.py -mG" in txt,
           "render format wrong: %r" % txt)
    r = run(["in_PyRate.py", "-pC", "0", "-mHPP", "-qShift", "e_q.txt", "-ncat", "4",
             "-A", "1", "-B", "2", "-tag", "x", "-j", "-3"])
    expect(len(render(r).splitlines()) < 45, "output not bounded: %r" % render(r))

    if errors:
        for e in errors:
            print("SELF-TEST FAIL: %s" % e)
        return 1
    print("build_command.py self-test: OK (%d checks; citation audit of %d quotes "
          "across %d mirrors; %d commands parsed from the command list + %d cited "
          "extensions; corpus replay: %d documented command lines assembled, %d "
          "allow-listed)"
          % (counters["checks"], len(CITE), len(cache), len(order), len(EXTENSIONS),
             n_replay, n_allow))
    return 0


def main(argv=None):
    try:
        res = build(argv if argv is not None else sys.argv[1:])
    except (IOError, OSError):
        print("error: I/O problem while reading mirrors", file=sys.stderr)
        return 3
    if res.get("help"):
        print(__doc__)
        return 0
    if res.get("selftest"):
        return res["rc"]
    if res.get("json"):
        # the documented machine-readable form of the same report, one object
        print(json.dumps(res, indent=2, sort_keys=True))
        return res["rc"]
    if res.get("list"):
        print("Commands parsed from %s (%d core):" % (res["mirror"], res["count_core"]))
        for row in res["list"]:
            print("  " + row)
        print("Grammar: %s" % res["grammar"])
        return 0
    print(render(res))
    return res["rc"]


if __name__ == "__main__":
    sys.exit(main())
