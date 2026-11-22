#!/usr/bin/env bash
# source: PyRate-doc/PyRate-tutorials/tutorials/pyrate_tutorial_bdnn.md | derived
# shows: every BDNN inference / dataset-setup command the tutorial prints: two time-series files, the default long run, custom time bins with -fixShift, edge shifts, custom taxon x time predictor tables, exporting those tables, -restore_mcmc, replicates with -j, -combBDNN across replicates, and BDNN on previously estimated origination/extinction times
# every `python .../PyRate.py ...` line below is byte-identical to pyrate-bdnn/references/tutorial-bdnn.md; the line numbers in each comment
#   cite the prose that motivates the command, NOT the command's own mirror line; only the comment lines were added by this fixture.
# usage: needs a PyRate source checkout (https://github.com/dsilvestro/PyRate) with example_files/BDNN_examples/Carnivora/
#        and Python 2.6-2.7 on PATH as `python` (Python 3 is explicitly NOT supported).
#        Dry-run the quoting without PyRate:  bash -n bdnn-run-analysis.sh

# A. Different time-series for speciation and extinction: two paths after -BDNNtimevar, and 'These files should
#    have the same column names though' (mirror line 205); -fixShift gives the bin boundaries used by both.
python ./PyRate.py ./example_files/BDNN_examples/Carnivora/Carnivora_occs.py -BDNNmodel 1 -trait_file ./example_files/BDNN_examples/Carnivora/Traits.txt -BDNNtimevar ./example_files/BDNN_examples/Carnivora/Advanced_examples/Paleotemperature_nohumans.txt ./example_files/BDNN_examples/Carnivora/Advanced_examples/Paleotemperature_humans.txt -fixShift ./example_files/BDNN_examples/Carnivora/Advanced_examples/Time_windows.txt -mG -qShift ./example_files/BDNN_examples/Carnivora/Stages.txt -out _different_timevar -n 200001 -p 20000 -s 5000

# B. The reference run of section 'Running a BDNN inference' (mirror lines 228-231). -s sampling frequency,
#    -n total generations, -p print frequency (line 232). 'An analysis with the settings above will last
#    approximately half a day' (line 234).
python ./PyRate.py ./example_files/BDNN_examples/Carnivora/Carnivora_occs.py -BDNNmodel 1 -BDNNtimevar ./example_files/BDNN_examples/Carnivora/Paleotemperature.txt -trait_file ./example_files/BDNN_examples/Carnivora/Traits.txt -qShift ./example_files/BDNN_examples/Carnivora/Stages.txt -mG -n 20000001 -s 20000 -p 10000

# C. Unequal / custom time bins: -fixShift file holding bin boundaries, 'no header, just ages' (mirror line 238),
#    and -out _time_windows to keep the output files of different runs apart (line 252).
#    Fixture for the -fixShift file: bdnn-Time_windows.txt
python ./PyRate.py ./example_files/BDNN_examples/Carnivora/Carnivora_occs.py -BDNNmodel 1 -BDNNtimevar ./example_files/BDNN_examples/Carnivora/Paleotemperature.txt -trait_file ./example_files/BDNN_examples/Carnivora/Traits.txt -fixShift ./example_files/BDNN_examples/Carnivora/Advanced_examples/Time_windows.txt -qShift ./example_files/BDNN_examples/Carnivora/Stages.txt -mG -out _time_windows -n 20000001 -s 20000 -p 10000

# D. Edge shifts (mirror lines 392-397): -edgeShift 15.97 2.5 fixes shifts at the boundaries while PyRate still
#    searches for rate variation between them; -qFilter 0 'allows for shifts in sampling rates at the boundaries' (line 394).
python ./PyRate.py ./example_files/BDNN_examples/Carnivora/Carnivora_occs.py -BDNNmodel 1 -trait_file ./example_files/BDNN_examples/Carnivora/Traits.txt -BDNNtimevar ./example_files/BDNN_examples/Carnivora/Paleotemperature.txt -mG -qShift ./example_files/BDNN_examples/Carnivora/Stages.txt -qFilter 0 -edgeShift 15.97 2.5 -out _edge -n 200001 -p 20000 -s 5000

# E. Custom taxon x time predictor tables (mirror lines 406-415): two folder paths after
#    -BDNNpath_taxon_time_tables = speciation predictors then extinction predictors (line 410); 'No additional
#    -trait_file and -BDNNtimevar should be invoked' (line 411). One table per time bin, named 01.txt, 02.txt, ...
python ./PyRate.py ./example_files/BDNN_examples/Carnivora/Carnivora_occs.py -BDNNmodel 1 -BDNNpath_taxon_time_tables ./example_files/BDNN_examples/Carnivora/Advanced_examples/load_predictors/speciation ./example_files/BDNN_examples/Carnivora/Advanced_examples/load_predictors/extinction -fixShift ./example_files/BDNN_examples/Carnivora/Advanced_examples/Time_windows.txt -qShift ./example_files/BDNN_examples/Carnivora/Stages.txt -mG -out _taxon_time_tables -n 20000001 -s 20000 -p 10000

# F. Export the predictor tables of a normal run to get the right number/format before editing them (mirror lines 425-427).
python ./PyRate.py ./example_files/BDNN_examples/Carnivora/Carnivora_occs.py -BDNNmodel 1 -BDNNtimevar ./example_files/BDNN_examples/Carnivora/Paleotemperature.txt -trait_file ./example_files/BDNN_examples/Carnivora/Traits.txt -fixShift ./example_files/BDNN_examples/Carnivora/Advanced_examples/Time_windows.txt -BDNNexport_taxon_time_tables

# G. Restart a chain that had not converged: 'restore the MCMC chain from the last sample using the -restore_mcmc
#    argument' (mirror lines 433-436). Repeat the original model arguments - the log alone is not enough.
python ./PyRate.py ./example_files/BDNN_examples/Carnivora/Carnivora_occs.py -restore_mcmc ./example_files/BDNN_examples/Carnivora/pyrate_mcmc_logs/Carnivora_occs_1_G_BDS_BDNN_16_8TVc_mcmc.log -BDNNmodel 1 -trait_file ./example_files/BDNN_examples/Carnivora/Traits.txt -BDNNtimevar ./example_files/BDNN_examples/Carnivora/Paleotemperature.txt -mG -qShift ./example_files/BDNN_examples/Carnivora/Stages.txt -n 200001 -p 20000 -s 5000

# H. The 2nd age-uncertainty replicate ('the Carnivora example dataset contains three replicates', mirror line 444).
python ./PyRate.py ./example_files/BDNN_examples/Carnivora/Carnivora_occs.py -j 2 -BDNNmodel 1 -trait_file ./example_files/BDNN_examples/Carnivora/Traits.txt -BDNNtimevar ./example_files/BDNN_examples/Carnivora/Paleotemperature.txt -mG -qShift ./example_files/BDNN_examples/Carnivora/Stages.txt -n 200001 -p 20000 -s 5000

# I. Combine the replicate log files of one folder: -b 0.25 excludes the first 25% of each file as burnin;
#    optionally add -resample 100 and -tag <suffix> (mirror lines 450-460). Writes combined_[n]_mcmc.log,
#    combined_[n]_per_species_rates.log, combined_[n]_sp_rates.log, combined_[n]_ex_rates.log, combined_[n].pkl (line 457).
python ./PyRate.py -combBDNN ./example_files/BDNN_examples/Carnivora/pyrate_mcmc_logs -b 0.25

# J. BDNN on times of origination and extinction taken from an earlier analysis (mirror lines 465-483):
# J1. infer the times with the RJMCMC algorithm (-A 4; mirror line 472). -A 4 is NOT in the -A list of
#     ../pyrate-command-reference/references/command-list.md lines 46-54 (only -A 0..3, default -A 2).
python ./PyRate.py ./example_files/BDNN_examples/Carnivora/Carnivora_occs.py -A 4 -qShift ./example_files/BDNN_examples/Carnivora/Stages.txt -mG -n 1000001 -p 100000 -s 10000
# J2. mean posterior times -> Carnivora_occs_1_Grj_se_est.txt (-ginput, -b 0.25; mirror lines 475-477)
python ./PyRate.py -ginput ./example_files/BDNN_examples/Carnivora/pyrate_mcmc_logs/Carnivora_occs_1_Grj_mcmc.log -b 0.25
# J3. BDNN fed with -d <se_est.txt> (mirror lines 480-482). Per ../pyrate-command-reference/references/command-list.md
#     line 18, -d 'automatically sets -fixSE = null', i.e. preservation rates and times are no longer estimated.
python ./PyRate.py -d ./example_files/BDNN_examples/Carnivora/pyrate_mcmc_logs/Carnivora_occs_1_Grj_se_est.txt -BDNNmodel 1 -trait_file ./example_files/BDNN_examples/Carnivora/Traits.txt -n 500001 -p 20000 -s 5000
