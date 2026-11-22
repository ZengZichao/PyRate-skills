#!/bin/sh
# source: PyRate-doc/PyRate-tutorials/tutorials/pyrate_tutorial_2.md lines 102,106,122,132,140,149,155 | verbatim (command text byte-identical to the mirror; markdown backticks and trailing spaces removed)
# shows: every PyRateContinuous.py command line the docs print - diversity dependence (-DD), correlation with a time-continuous variable (-c), correlation model (-m -1/0/1), rates-through-time plotting (-plot), thermodynamic-integration model testing (-A 1) and marginal-likelihood calculation (-mL)
# reference-only: the paths are the docs' own placeholders (.../); substitute real files before running. Needs Python 2.6-2.7 and the folder pyrate_lib in the same directory as PyRateContinuous.py (../pyrate/references/home.md:39,61)
# these seven lines are the COMPLETE set of PyRateContinuous.py examples in this corpus; -plot is documented on ../pyrate-summarize-results/references/summarize-results.md:39-40 for PyRate's *_marginal_rates.log, not for a PyRateContinuous log

# references/tutorial-2.md:102  # -DD alone; -m is absent, so the documented default applies: -m 0 exponential (references/pyratecontinuous.md:37)
python PyRateContinuous.py -d .../Canidae_1_G_se_est.txt -DD

# references/tutorial-2.md:106  # -DD -m 0 exponential; the other settings are -m 1 linear and -m -1 constant-rate null model for model testing (tutorial-2.md:104,108; pyratecontinuous.md:36-38)
python PyRateContinuous.py -d .../Canidae_1_G_se_est.txt -DD -m 0

# references/tutorial-2.md:122  # RTT plot of a DD run: -plot takes the log file and -b 200 sets the plotting burnin (tutorial-2.md:124). NOTE this doc line carries -b TWICE (-b 100 and -b 200); which one wins is not documented
python PyRateContinuous.py -d .../Canidae_1_G_se_est.txt -DD -m 0 -b 100 -plot .../Canidae_1_G_se_est_DD_0_exp.log -b 200

# references/tutorial-2.md:132  # correlation with an external variable: -c temperature.txt, a 2-column tab-separated time/value table (references/pyratecontinuous.md:32)
python PyRateContinuous.py -d .../Canidae_1_G_se_est.txt -m 0 -c temperature.txt

# references/tutorial-2.md:140  # RTT plot of a -c run
python PyRateContinuous.py -d .../Canidae_1_G_se_est.txt -m 0 -c temperature.txt -plot .../my_logfile.log -b 100

# references/tutorial-2.md:149  # -A 1: thermodynamic integration for the marginal likelihood; 10 scaling categories by default and -n counts per category (tutorial-2.md:151)
python PyRateContinuous.py -d .../Canidae_1_G_se_est.txt -m 0 -c temperature.txt -A 1

# references/tutorial-2.md:155  # -mL on a directory: marginal likelihood of every file with extension .log there; an appropriate -b must be given (tutorial-2.md:153)
python PyRateContinuous.py -mL .../path_to_my_logfiles -b 100
