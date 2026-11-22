# source: PyRate-doc/PyRate-tutorials/tutorials/pyrate_tutorial_4.md lines 114-159 (the five command lines are source lines 116, 133, 139, 150, 159) | verbatim
# shows: every command line the tutorial prints for the three PyRate.py model families this skill owns - Covar (trait-correlated), ADE (age-dependent extinction) and BDC / BDC-skyline (birth-death chronospecies)
# note: the -logT 10 in the Covar line is exactly as printed by the docs, although both docs only define -logT 0, 1 and 2 (mirror tutorial-4.md:106-108, command-list.md:153-155); see the skill's "Not documented in this wiki" table
# usage: bash covar-model-commands.sh runs nothing by itself - the lines need the upstream example files (Ursidae_example_PyRate.py, Ursidae_bm.txt, epochs.txt, example_files/BDC_model/Feliformia.py, Feliformia.tre) and PyRate.py on Python 2.7; replace <your_dataset> with your own *_PyRate.py input

# --- Covar: trait-correlated speciation, extinction and preservation (tutorial-4.md:124) ---
./PyRate.py Ursidae_example_PyRate.py -trait_file Ursidae_bm.txt -mCov 5 -logT 10 -pC 0

# --- ADE: age-dependent extinction with a TPP preservation model (tutorial-4.md:141) ---
python PyRate.py <your_dataset> -ADE 1 -qShift epochs.txt

# --- ADE restricted to a time window of roughly constant rates (tutorial-4.md:147) ---
python PyRate.py <your_dataset> -ADE 1 -qShift epochs.txt -filter 23.03 5.3

# --- BDC: joint analysis of fossil occurrences and a tree file (NEXUS format) (tutorial-4.md:156, 158) ---
python PyRate.py example_files/BDC_model/Feliformia.py -tree example_files/BDC_model/Feliformia.tre

# --- BDC-skyline: rate shifts fixed at epoch boundaries under the BDC compatible model (tutorial-4.md:167) ---
python PyRate.py example_files/BDC_model/Feliformia.py -tree example_files/BDC_model/Feliformia.tre -fixShift example_files/epochs.txt -bdc
