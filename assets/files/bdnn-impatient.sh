#!/usr/bin/env bash
# source: PyRate-doc/PyRate-tutorials/tutorials/pyrate_tutorial_bdnn.md | derived
# shows: the complete 'Complete example for the impatient' section (mirror lines 43-115): BDNN inference with -BDNNmodel 1, -plotBDNN rates-through-time, -plotBDNN_effects partial dependence plots, -BDNN_pred_importance predictor importance
# every `python .../PyRate.py ...` line below is byte-identical to pyrate-bdnn/references/tutorial-bdnn.md; the line numbers in each comment
#   cite the prose that motivates the command, NOT the command's own mirror line; only the comment lines were added by this fixture.
# usage: needs a PyRate source checkout (https://github.com/dsilvestro/PyRate) with example_files/BDNN_examples/Carnivora/
#        and Python 2.6-2.7 on PATH as `python` (Python 3 is explicitly NOT supported).
#        Dry-run the quoting without PyRate:  bash -n bdnn-impatient.sh

# The doc gives no shell options; add 'set -e' yourself if you want to stop at the first failing step.

# step 1 (mirror lines 46-48) 'Move to your PyRate folder' - the path below is the doc's own literal placeholder, edit it.
cd /your/path/to/PyRate-master

# step 2 (mirror lines 53-55) 'Run a BDNN inference'. The whole section is advertised as taking 'ca. 45 minutes' (line 44),
# which is why -n is only 200001 here; the full-length run in bdnn-run-analysis.sh uses -n 20000001.
python ./PyRate.py ./example_files/BDNN_examples/Carnivora/Carnivora_occs.py -BDNNmodel 1 -trait_file ./example_files/BDNN_examples/Carnivora/Traits.txt -BDNNtimevar ./example_files/BDNN_examples/Carnivora/Paleotemperature.txt -mG -qShift ./example_files/BDNN_examples/Carnivora/Stages.txt -n 200001 -p 20000 -s 5000

# step 3 (mirror lines 58-61) '-plotBDNN' -> 'a PDF file with the marginal rates through time (RTT)' (line 59).
# -b 0.5 'discards 50% of the MCMC samples as burnin' (line 64). Output figure: ../../assets/images/Carnivora_BDNN_RTT.png.
python ./PyRate.py -plotBDNN ./example_files/BDNN_examples/Carnivora/pyrate_mcmc_logs/Carnivora_occs_1_G_BD1-1_BDNN_16_8TVc_mcmc.log -b 0.5

# step 4 (mirror lines 70-73) partial dependence plots. -plotBDNN_transf_features rescales z-transformed predictors
# back to their original scale; -BDNN_groups bundles one-hot states of a categorical predictor into one figure (line 76).
# Output figures: ../../assets/images/Carnivora_BDNN_family_speciation.png, Carnivora_BDNN_temp_extinction.png.
python ./PyRate.py -plotBDNN_effects ./example_files/BDNN_examples/Carnivora/pyrate_mcmc_logs/Carnivora_occs_1_G_BD1-1_BDNN_16_8TVc_mcmc.log -plotBDNN_transf_features ./example_files/BDNN_examples/Carnivora/Backscale.txt -BDNN_groups "{\"geography\": [\"Eurasia\", \"NAmerica\"], \"taxon\": [\"Amphicyonidae\", \"Canidae\", \"Felidae\", \"FeliformiaOther\", \"Hyaenidae\", \"Musteloidea\", \"Ursidae\", \"Viverridae\"]}" -b 0.5

# step 5 (mirror lines 88-91) predictor importance + coefficient of rate variation; seven files are written to the log folder (line 96).
# -BDNN_nsim_expected_cv 10 instead of the default 100 is set 'to safe some time for the impatient' [sic, line 94].
# The seven output files include _coefficient_of_rate_variation.csv, _sp_predictor_influence.csv and
# _ex_predictor_influence.csv (lines 96, 104); shapes in fixtures bdnn-cv_rate_variation-EXCERPT.txt and
# bdnn-predictor_influence-EXCERPT.txt.
python ./PyRate.py -BDNN_pred_importance ./example_files/BDNN_examples/Carnivora/pyrate_mcmc_logs/Carnivora_occs_1_G_BD1-1_BDNN_16_8TVc_mcmc.log -plotBDNN_transf_features ./example_files/BDNN_examples/Carnivora/Backscale.txt -BDNN_groups "{\"geography\": [\"Eurasia\", \"NAmerica\"], \"taxon\": [\"Amphicyonidae\", \"Canidae\", \"Felidae\", \"FeliformiaOther\", \"Hyaenidae\", \"Musteloidea\", \"Ursidae\", \"Viverridae\"]}" -b 0.5 -BDNN_nsim_expected_cv 10
