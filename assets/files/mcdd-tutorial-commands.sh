# source: PyRate-doc/PyRate-tutorials/tutorials/pyrate_tutorial_4.md lines 26, 30, 60, 82 | verbatim
# shows: the whole MCDD + MBD command sequence tutorial 4 prints, in printed order (mirror references/tutorial-4.md lines 34, 38, 68, 90)
# paths and ./ prefixes are reproduced exactly as the docs write them; the docs print no other MCDD/MBD command line
# NOTE: not runnable as-is - substitute your own input files. See SKILL.md "Worked example".

# --- MCDD, all clades analysed at once (mirror tutorial-4.md line 34) ---
PyRateMCDD.py -d /example_files/Carnivores_MCDD.txt -n 10000000 -s 10000

# --- MCDD, one clade at a time; -c 0 targets the first clade (mirror tutorial-4.md line 38) ---
PyRateMCDD.py -d /example_files/Carnivores_MCDD.txt -n 10000000 -s 10000 -c 0

# --- MBD, launch an analysis; -var points to a folder of predictor files (mirror tutorial-4.md line 68) ---
./PyRateMBD.py -d /example_files/Ferns_SE.txt -var /example_files/predictors_MBDmodel -m 1

# --- MBD, summarizing the results with -plot (mirror tutorial-4.md line 90) ---
./PyRateMBD.py -d /example_files/Ferns_SE.txt -var /example_files/predictors_MBDmodel -m 1 -plot Ferns_SE_0_lin_MBD.log
