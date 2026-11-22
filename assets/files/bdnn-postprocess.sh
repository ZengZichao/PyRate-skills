#!/usr/bin/env bash
# source: PyRate-doc/PyRate-tutorials/tutorials/pyrate_tutorial_bdnn.md | derived
# shows: every BDNN output-postprocessing command the tutorial prints: -plotBDNN (marginal RTT, time-truncated, per group of taxa), -plotBDNN_effects partial dependence plots (escaped-quote and single-quote -BDNN_groups forms), -BDNN_interaction for more than two predictors, -BDNN_interaction_fix for species-specific rates, -BDNN_pred_importance
# every `python .../PyRate.py ...` line below is byte-identical to pyrate-bdnn/references/tutorial-bdnn.md; the line numbers in each comment
#   cite the prose that motivates the command, NOT the command's own mirror line; only the comment lines were added by this fixture.
# usage: needs a PyRate source checkout (https://github.com/dsilvestro/PyRate) with example_files/BDNN_examples/Carnivora/
#        and Python 2.6-2.7 on PATH as `python` (Python 3 is explicitly NOT supported).
#        Dry-run the quoting without PyRate:  bash -n bdnn-postprocess.sh

# Log-file names: lines 261/271/283/316/331/336/347 read ..._G_BDS_BDNN_16_8TVc_mcmc.log while the impatient
# example reads ..._G_BD1-1_BDNN_16_8TVc_mcmc.log (line 61). No file in this corpus explains the name encoding -
# always take the name of the *_mcmc.log actually written by your run (see the skill's hazard table).

# 1. Marginal rates through time (mirror lines 258-261); -b 0.1 is the burnin proportion and the command reads
#    _sp_rates.log / _ex_rates.log from pyrate_mcmc_logs, writing a PDF plus an editable R script (line 264).
#    Add -logT 2 for a log scale, -root_plot / -min_age_plot to truncate. NOTE: -logT means something else in
#    Covar runs (trait transformation, command-list.md lines 150-155).
python ./PyRate.py -plotBDNN ./example_files/BDNN_examples/Carnivora/pyrate_mcmc_logs/Carnivora_occs_1_G_BDS_BDNN_16_8TVc_mcmc.log -b 0.1

# 2. The same plot truncated at the -edgeShift boundaries (mirror lines 400-402).
python ./PyRate.py -plotBDNN ./example_files/BDNN_examples/Carnivora/pyrate_mcmc_logs/Carnivora_occs_1_edge_G_BD1-1_BDNN_16_8TVc_mcmc.log -min_age_plot 2.6 -root_plot 15.9 -b 0.5

# 3. RTT for subsets of taxa defined in a tab-separated taxon/group file (mirror lines 268-271).
#    The doc names RTT_groups.csv but never prints its contents; figure:
#    ../../assets/images/Carnivora_BDNN_RTT_Borophagus.png
python ./PyRate.py -plotBDNN ./example_files/BDNN_examples/Carnivora/pyrate_mcmc_logs/Carnivora_occs_1_G_BDS_BDNN_16_8TVc_mcmc.log -b 0.1 -plotBDNN_groups ./example_files/BDNN_examples/Carnivora/Advanced_examples/RTT_groups.csv

# 4. Partial dependence plots: single predictors + all two-way interactions (mirror lines 280-283).
#    -resample 100 because 'the log file may contain thousands of samples. However, 100 should be sufficient' (line 286).
#    Net diversification is not a parameter: subtract the extinction PDP from the speciation PDP (line 280).
python ./PyRate.py -plotBDNN_effects ./example_files/BDNN_examples/Carnivora/pyrate_mcmc_logs/Carnivora_occs_1_G_BDS_BDNN_16_8TVc_mcmc.log -plotBDNN_transf_features ./example_files/BDNN_examples/Carnivora/Backscale.txt -BDNN_groups "{\"geography\": [\"Eurasia\", \"NAmerica\"], \"taxon\": [\"Amphicyonidae\", \"Canidae\", \"Felidae\", \"FeliformiaOther\", \"Hyaenidae\", \"Musteloidea\", \"Ursidae\", \"Viverridae\"]}" -b 0.1 -resample 100

# 5. The same -BDNN_groups argument in the Linux/Mac form (mirror lines 290-293): single quotes outside,
#    double quotes inside, no backslash escaping. Kept commented because it is a fragment, not a command.
# -BDNN_groups '{"geography": ["Eurasia", "NAmerica"], "taxon": ["Amphicyonidae", "Canidae", "Felidae", "FeliformiaOther", "Hyaenidae", "Musteloidea", "Ursidae", "Viverridae"]}'

# 6. Partial dependence rates for three predictors, as text files instead of plots (mirror lines 312-316).
#    'This can last a while to compute and may use a lot of memory, especially for continuous predictors
#    because for three continuous predictors we need to calculate 100 x 100 x 100 rates' (line 312).
#    Writes four files (*_pdp.csv + one file of observed predictor values, for speciation and for extinction).
python ./PyRate.py -BDNN_interaction ./example_files/BDNN_examples/Carnivora/pyrate_mcmc_logs/Carnivora_occs_1_G_BDS_BDNN_16_8TVc_mcmc.log -plotBDNN_transf_features ./example_files/BDNN_examples/Carnivora/Backscale.txt -BDNN_groups "{\"BodyMass\": [\"BodyMass\"], \"Temperature\": [\"Temperature\"], \"time\": [\"time\"]}" -b 0.5 -resample 3

# 7. -BDNN_groups mixing continuous and categorical predictors (mirror lines 329-331) - normally reserved
#    for one-hot encoded traits, but allowed here.
python ./PyRate.py -BDNN_interaction ./example_files/BDNN_examples/Carnivora/pyrate_mcmc_logs/Carnivora_occs_1_G_BDS_BDNN_16_8TVc_mcmc.log -plotBDNN_transf_features ./example_files/BDNN_examples/Carnivora/Backscale.txt -BDNN_groups "{\"BodyMass\": [\"BodyMass\"], \"Temperature\": [\"Temperature\"], \"taxon\": [\"Amphicyonidae\", \"Canidae\", \"Felidae\", \"FeliformiaOther\", \"Hyaenidae\", \"Musteloidea\", \"Ursidae\", \"Viverridae\"]}" -b 0.5 -resample 3

# 8. Species-time-specific rates at each taxon's inferred origination/extinction, marginalizing over
#    family and geography: same as 6 plus -BDNN_interaction_fix (mirror lines 334-336).
python ./PyRate.py -BDNN_interaction ./example_files/BDNN_examples/Carnivora/pyrate_mcmc_logs/Carnivora_occs_1_G_BDS_BDNN_16_8TVc_mcmc.log -BDNN_interaction_fix -plotBDNN_transf_features ./example_files/BDNN_examples/Carnivora/Backscale.txt -BDNN_groups "{\"BodyMass\": [\"BodyMass\"], \"Temperature\": [\"Temperature\"], \"time\": [\"time\"]}" -b 0.5 -resample 3

# 9. Predictor importance from three XAI metrics (mirror lines 344-347). The doc prints 'python PyRate.py' here,
#    without the ./ it uses on every other command line. Options used: -b, -resample,
#    -BDNN_nsim_expected_cv 7, -BDNN_pred_importance_nperm 23.
python PyRate.py -BDNN_pred_importance ./example_files/BDNN_examples/Carnivora/pyrate_mcmc_logs/Carnivora_occs_1_G_BDS_BDNN_16_8TVc_mcmc.log -BDNN_groups "{\"geography\": [\"Eurasia\", \"NAmerica\"], \"taxon\": [\"Amphicyonidae\", \"Canidae\", \"Felidae\", \"FeliformiaOther\", \"Hyaenidae\", \"Musteloidea\", \"Ursidae\", \"Viverridae\"]}" -b 0.1 -resample 10 -BDNN_nsim_expected_cv 7 -BDNN_pred_importance_nperm 23
