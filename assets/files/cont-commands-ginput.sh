#!/bin/sh
# source: PyRate-doc/PyRate-tutorials/tutorials/pyrate_tutorial_2.md lines 29,41,47,55,60,68,74,79,86 and PyRate-doc/PyRate-wiki/4.-PyRateContinuous.md lines 16-18 | verbatim (command text byte-identical to the mirrors; markdown backticks and trailing spaces removed, the docs' own trailing "# ..." comments kept)
# shows: every command line the docs print for extracting origination/extinction times (-ginput, -b, -tag, -resample) and for plotting range-through diversity (-ltt, -grid_plot) - and the fact that the two docs name DIFFERENT programs for -ginput
# reference-only: the paths are the docs' own placeholders (.../, path_to_log_file/); substitute real files before running. Needs Python 2.6-2.7 (Python 3.x "is currently not supported", ../pyrate/references/home.md:69) and the folder pyrate_lib next to the program (../pyrate/references/home.md:61)
# DOC CONFLICT: the tutorial runs -ginput through PyRate.py (tutorial-2.md:29,41,47,55,60); the wiki page runs it through PyRateContinuous.py (pyratecontinuous.md:16,18) and drops the -ginput flag altogether on pyratecontinuous.md:17

# --- extracting the estimated times, references/tutorial-2.md "Mean times of origination and extinction" ---
# references/tutorial-2.md:29  # -> 3 output files: Canidae_1_G_se_est.txt, a lineage-through-time PDF and the R script (tutorial-2.md:31-35)
python PyRate.py -ginput .../Canidae_1_G_mcmc.log -b 100

# references/tutorial-2.md:41  # a directory: each file with extension *_mcmc.log processed separately (tutorial-2.md:43)
python PyRate.py -ginput .../path_to_log_files -b 100

# references/tutorial-2.md:47  # -tag combines replicates into one ...se_ext.txt, one column pair per replicate (tutorial-2.md:49)
python PyRate.py -ginput .../path_to_log_files -tag Canidae -b 100

# references/tutorial-2.md:55  # -resample 10: draws 10 posterior samples instead of the mean, stored as additional columns (tutorial-2.md:57)
python PyRate.py -ginput .../Canidae_1_G_mcmc.log -b 100 -resample 10

# references/tutorial-2.md:60  # -tag + -resample: ten values from each file concatenated into one table (tutorial-2.md:62)
python PyRate.py -ginput .../path_to_log_files -tag Canidae -b 100 -resample 10

# references/tutorial-2.md:68  # -ltt 1: mean diversity through time, min/max range from replicates shown shaded (tutorial-2.md:70)
python PyRate.py -d Canidae_1_G_se_est.txt -ltt 1

# references/tutorial-2.md:74  # -ltt 2: same plot with log10-transformed diversity (tutorial-2.md:76)
python PyRate.py -d Canidae_1_G_se_est.txt -ltt 2

# references/tutorial-2.md:79  # -ltt 3: LTT plot of each replicate as individual lines (tutorial-2.md:81)
python PyRate.py -d Canidae_1_G_se_est.txt -ltt 3

# references/tutorial-2.md:86  # -grid_plot 0.1: counts in 0.1 Myr bins instead of the default bin size of 1 time unit (tutorial-2.md:83,88)
python PyRate.py -d Canidae_1_G_se_est.txt -ltt 1 -grid_plot 0.1

# --- the same task, as printed on the PyRateContinuous wiki page (PyRateContinuous.py form) ---
# references/pyratecontinuous.md:16  # the wiki form: PyRateContinuous.py -ginput -> Ursidae_1_se_est.txt
python PyRateContinuous.py -ginput path_to_log_file/Ursidae_1_mcmc.log -b 100   # generates a file named `Ursidae_1_se_est.txt` with the estimated times of origination and extinction for each species, after excluding the first 100 samples as burnin.

# references/pyratecontinuous.md:17  # the wiki's directory form AS PRINTED - no -ginput flag on this line
python PyRateContinuous.py path_to_log_file/ -b 100   # generates as many files as the number of `*mcmc.log` files found in the directory.

# references/pyratecontinuous.md:18  # wiki -tag form: the log files are replicates of one analysis; pick one replicate later with -j
python PyRateContinuous.py path_to_log_file/ -b 100 -tag Ursidae   # generates a single file with the estimated times of origination and extinction for each species combining all log files containing the "Ursidae" in their file names. The different log files are treated as replicates of the same analysis . The individual replicates can be analyzed in subsequent analyses in PyRate and PyRateContinuous using the [command `-j`](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-j).
