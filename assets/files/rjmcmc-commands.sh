#!/usr/bin/env bash
# source: PyRate-doc/PyRate-tutorials/tutorials/pyrate_tutorial_3.md lines 35,39,46,65,73,84,91,99,105,110,115,119,142,146 | derived
# shows: every command line Tutorial #3 (RJMCMC) prints, in tutorial order - setup, -mProb, -plotRJ, -combLogRJ, -se_gibbs, -bound_se; all verbatim except the -combLog/-col_tag line, which is marked COMPOSED below
#
# Dry run by default (prints the sequence). To actually execute:
#   RUN=1 bash rjmcmc-commands.sh
# The inputs are printed by the tutorial as placeholders (".../Canis_pbdb_data_PyRate.py",
# ".../path_to_log_files/"), so a "file not found" from a RUN=1 pass is expected until you
# substitute your own paths; nothing here fabricates data the docs do not print.
# Line numbers refer to the MIRROR: references/tutorial-3.md (frontmatter occupies lines 1-8).
set -u

RUN="${RUN:-0}"
cmd() { # cmd <tutorial-3.md line> <verbatim command>
    printf '\n# references/tutorial-3.md:%s\n%s\n' "$1" "$2"
    if [ "$RUN" = "1" ]; then eval "$2"; fi
}

printf '=== A. Setting up an analysis using RJMCMC (tutorial-3.md:29-48)\n'
cmd 35 'python PyRate.py .../Canis_pbdb_data_PyRate.py -A 4 -mHPP -mG'
cmd 39 'python PyRate.py -d Canidae_1_G_se_est.txt -A 4'
# tutorial-3.md:44 default shift-time prior = uniform, "a time bin cannot be smaller than 1 time unit"
cmd 46 'python PyRate.py -d Canidae_1_G_se_est.txt -A 4 -min_dt 0.5'

printf '\n=== B. RJMCMC output (tutorial-3.md:50-60): sum.txt, mcmc.log, sp_rates.log, ex_rates.log\n'
printf '# plus the old format, requested at run time: -log_marginal_rates 1 (tutorial-3.md:60)\n'
printf '# that file works with -plot but NOT with -plotRJ (tutorial-3.md:60)\n'

printf '\n=== C. Summarize model probabilities (tutorial-3.md:62-67)\n'
cmd 65 'python PyRate.py -mProb .../Canis_pbdb_data_mcmc.log -b 200'
# -b 200 = the first 200 SAMPLES, "i.e. the first 200,000 iterations, if the sampling
# frequency was set to 1,000" (tutorial-3.md:67)

printf '\n=== D. Plot rates through time and rate shifts (tutorial-3.md:70-93)\n'
cmd 73 'python PyRate.py -plotRJ .../path_to_log_files/ -b 200'
printf '# -plotRJ takes the DIRECTORY, "not the files themselves" (tutorial-3.md:77);\n'
printf '# restrict the files with -tag Canis_pbdb (tutorial-3.md:77); grid default is\n'
printf '# -grid_plot 0 = 100 bins across the window (tutorial-3.md:79)\n'
cmd 84 'python PyRate.py -plotRJ .../path_to_log_files/ -b 200 -root_plot 23 -min_age_plot 5.3'
cmd 91 'python PyRate.py -plotRJ .../path_to_log_files/ -b 200 -min_dt 0.5'

printf '\n=== E. Combine log files from multiple replicates (tutorial-3.md:96-110)\n'
cmd 99 'python PyRate.py -combLogRJ /pyrate_mcmc_logs -b 1000 -tag Canis'
cmd 105 'python PyRate.py -combLogRJ .../pyrate_mcmc_logs -b 1000 -tag Canis -resample 100'
printf '# mcmc.log only: -combLog plus the column selector printed at tutorial-3.md:110.\n'
printf '# COMPOSED, not verbatim: tutorial-3.md:110 prints only the fragments `-combLog` and\n'
printf '# `-col_tag posterior root_age death_age`; the only full -combLog command line in this\n'
printf '# corpus is tutorial-1.md:227 (`PyRate.py -combLog path_to_your_log_files -tag mcmc -b 100`),\n'
printf '# which selects FILES by -tag; the line below pairs that shape with the -col_tag columns.\n'
cmd '110 (COMPOSED)' 'python PyRate.py -combLog .../pyrate_mcmc_logs -col_tag posterior root_age death_age'
printf '# combined outputs are named combined_[n]_mcmc.log / combined_[n]_sp_rates.log /\n'
printf '# combined_[n]_ex_rates.log, [n] = number of replicates (tutorial-3.md:101)\n'

printf '\n=== F. Running PyRate on large datasets (tutorial-3.md:112-124)\n'
cmd 115 'python PyRate.py .../Rhinocerotidae_PyRate.py -qShift .../epochs_q.txt -se_gibbs -fU 0.35 0.6 0'
printf '# printed as a FRAGMENT to add when there are many preservation shifts (tutorial-3.md:119):\n'
printf '#   -fQ 0.1 -tQ 1.05 1.05\n'
printf '# HPP/TPP preservation only; can smooth rates -> use -fixShift, or extract SE times\n'
printf '# and rerun with -d (tutorial-3.md:122-123)\n'

printf '\n=== G. Constraining origination and extinction times (tutorial-3.md:126-146)\n'
printf '# table format: taxon, max_ts, min_ts, max_te, min_te; NA = unbounded (tutorial-3.md:129-140)\n'
cmd 142 'python ./PyRate.py ./example_files/Ammonoidea.py -bound_se ./example_files/Ammonoidea_bound_se.txt'
cmd 146 'python ./PyRate.py ./example_files/Ammonoidea.py -bound_se ./example_files/Ammonoidea_bound_se.txt -qShift ./example_files/epochs_q.txt -se_gibbs -fU 0.35 0.6 0'

printf '\n# done. RUN=%s (set RUN=1 to execute); every command is verbatim from the tutorial except\n# the -combLog/-col_tag line, which the comment above marks COMPOSED.\n' "$RUN"
