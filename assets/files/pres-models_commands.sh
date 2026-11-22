#!/usr/bin/env bash
# source: PyRate-doc/PyRate-tutorials/tutorials/pyrate_tutorial_1.md lines 113-150 and
#         PyRate-doc/PyRate-wiki/2.-PyRate:-command-list.md lines 77-98 (plus 24, 38, 60, 67, 170,
#         231, 235, 255) | derived
# shows: one runnable command line for each of the four PyRate preservation (fossilization) models
#        (NHPP, HPP, TPP, Gamma-heterogeneous), plus the preservation-model test, the -fixSE shortcut,
#        the TI marginal-likelihood runs and the TPP post-run plot - exactly as the mirrors print them.
#
# The flags below are the docs' own; the input/epochs paths and the interpreter are parameterised
# (the docs write the input as `.../Canis_pbdb_data_PyRate.py`), `-out` tags are added because
# references/command-list.md:32-35 exists for exactly that, and every numeric value used here is one
# the docs print (defaults -n 10000000, -s 1000, -j 1, -k 10, -ncat 4, -b 0.10). Citations point at
# the mirrors:
#   references/tutorial-1.md  = PyRate wiki/tutorials mirror, English
#   references/command-list.md
# Python version is contested INSIDE this corpus: ../pyrate/references/home.md:69 says the program was
# tested "using Python 2.6 – 2.7" and "Please note that Python 3.x is currently not supported", while
# ../pyrate-installation/references/virtual-environment.md:13 says "First, make sure **Python (v.3.10
# or higher)** is installed on your computer" (and notes `python3` at :26). Set PY to whichever your
# installation skill resolves that conflict with.
#
# usage: run from the PyRate directory (the docs call `python PyRate.py`, not a full path):
#   bash /path/to/pres-models_commands.sh /path/to/Dataset_PyRate.py /path/to/epochs_q.txt
#   (or set the 2nd argument to this skill's assets/files/pres-epochs_q.txt)
set -euo pipefail

OCC=${1:?give the *_PyRate.py input file as first argument}
EPOCHS=${2:-pres-epochs_q.txt}     # the delimiter file this skill owns; see its table in SKILL.md
PY=${PY:-python}                   # interpreter per the note above (2.7 vs 3.10+ is contested)

echo "== 1. NHPP - the DEFAULT, no flag exists for it (references/command-list.md:88, references/tutorial-1.md:122) =="
# "Note that the NHPP is  used unless differently specified." (references/command-list.md:88)
"$PY" PyRate.py "$OCC" -A 2 -n 10000000 -s 1000
#  ^ tutorial prints bare `python PyRate.py .../Canis_pbdb_data_PyRate.py -mG -n 20000000 -s 5000`
#    style lines; -n/-s defaults are references/command-list.md:58 and :62.

echo "== 2. HPP - homogeneous Poisson process, constant q through time (references/tutorial-1.md:126) =="
"$PY" PyRate.py "$OCC" -mHPP

echo "== 3. TPP - time-variable Poisson process, q constant within each epoch (references/tutorial-1.md:132) =="
"$PY" PyRate.py "$OCC" -qShift "$EPOCHS"

echo "== 3b. TPP with the prior rate estimated from the data (recommended when several q are estimated;
     references/tutorial-1.md:137 and :139) =="
"$PY" PyRate.py "$OCC" -qShift "$EPOCHS" -pP 1.5 0

echo "== 4. Gamma across-taxon heterogeneity, on top of NHPP / HPP / TPP (references/tutorial-1.md:144-146) =="
"$PY" PyRate.py "$OCC" -mG                                  # [NHPP model]
"$PY" PyRate.py "$OCC" -mHPP -mG                            # [HPP model]
"$PY" PyRate.py "$OCC" -qShift "$EPOCHS" -mG                # [TPP model]
"$PY" PyRate.py "$OCC" -qShift "$EPOCHS" -mG -ncat 4          # -ncat 4 is the only value the docs print (references/command-list.md:102)
"$PY" PyRate.py "$OCC" -qShift "$EPOCHS" -mG -log_sp_q_rates   # per-lineage relative q (tutorial-1.md:151)

echo "== 5. Which of NHPP / HPP / TPP does the data support? ML test over preservation processes =="
# The docs do NOT test the Gamma model here: "Note that the Gamma model is not tested here, but we
# recommend to add it to the best model among NHPP, HPP, or TPP as selected by the model testing."
# (references/tutorial-1.md:158); the command is printed at references/tutorial-1.md:156.
"$PY" PyRate.py "$OCC" -qShift "$EPOCHS" -PPmodeltest

echo "== 6. Marginal likelihoods by TI, one run per preservation model (references/command-list.md:49) =="
# -b "Must be set to a reasonable number when estimating marginal likelihood through TI"
# (references/command-list.md:69); the default is -b 0 (all samples logged, :71) and the fraction
# form "-b 0.10" is printed at :73 - use it, because :69 calls -b ITERATIONS while :72 and
# references/tutorial-1.md:213 call it SAMPLES (unresolved corpus conflict).
"$PY" PyRate.py "$OCC" -A 1 -mHPP -b 0.10 -out HPP
"$PY" PyRate.py "$OCC" -A 1 -qShift "$EPOCHS" -b 0.10 -out TPP
"$PY" PyRate.py "$OCC" -A 1 -mHPP -mG -b 0.10 -k 10 -out HPP_G   # -k 10 default (references/command-list.md:207)
# each run writes a '*_marginal_likelihood.txt' file (references/command-list.md:49); compare two of
# them with -BF (../pyrate-summarize-results/references/summarize-results.md:67-69).
# by inference only: the corpus never prints an `-A 1` line combined with a preservation flag, and it
# never lists preservation models among the documented TI comparison targets - see "Not documented".

echo "== 7. Fix speciation/extinction times -> the preservation likelihood is no longer computed =="
# references/command-list.md:104-106; '-fixSE null' = first/last appearances.
# -A 0 = fixed number of BD shifts (references/command-list.md:47); -mL 2 / -mM 2 are the doc's own
# examples (references/command-list.md:113, :117).
"$PY" PyRate.py "$OCC" -fixSE null -A 0 -mL 2 -mM 3
"$PY" PyRate.py "$OCC" -fixSE path_to_file/Ursidae.mcmc.log -A 0 -mL 2 -mM 3

echo "== 8. Post-run: preservation rate through time under TPP (references/tutorial-1.md:241) =="
# The tutorial passes the epoch file again at plot time; note it writes the file name as `epochs.txt`
# in the command but says the *_q_ file should be provided (references/tutorial-1.md:243) - a conflict.
"$PY" PyRate.py -plotQ path_to_logs/Dataset_mcmc.log -qShift "$EPOCHS" -b 100

# Not run here, but related flags documented for preservation: -pP 1.5 1 (default,
# references/command-list.md:180 - the tutorial prints 1.5/1.5, references/tutorial-1.md:134),
# -tQ 1.2 1.2 (q and alpha tuning windows, references/command-list.md:245),
# -fU 0.02 0.18 0.08 (update frequencies, first value = preservation, :265),
# -nT 0 (forces HPP! references/command-list.md:240), -thread 1 3 (2nd value = NHPP likelihood, :79).
