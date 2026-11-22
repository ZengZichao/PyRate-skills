---
name: pyrate-bdnn
description: "PyRate BDNN (birth-death neural network, tutorial 7): per-lineage, through-time speciation/extinction rates driven by 1-myr time bins, 0-1/one-hot/integer and continuous traits and time-series predictors, jointly with times and preservation. Run: -BDNNmodel 1 -trait_file -BDNNtimevar -BDNNtimetrait -BDNNtimeres -fixShift -edgeShift -qFilter -out -n -s -p -j -restore_mcmc -combBDNN -BDNNpath_taxon_time_tables -BDNNexport_taxon_time_tables -d -ginput. Plots: -plotBDNN(_groups/_effects/_transf_features) -BDNN_groups -BDNN_interaction(_fix) -BDNN_pred_importance(_nperm/_interaction/_window_size) -BDNN_nsim_expected_cv -BDNN_mean_shap_per_group -resample -logT -root_plot -min_age_plot -thread. NN: -BDNNnodes -BDNNactfun -BDNNoutputfun -BDNNreg -BDNNprecision. Files: *_mcmc.log _sp_rates.log _pdp.csv _predictor_influence.csv _coefficient_of_rate_variation.csv combined_[n].pkl Backscale.txt. Breaks: no z-transform, missing trait states, bad -BDNN_groups quoting, table count, unconverged chain, log-name mismatch."
---

# BDNN: birth-death neural network rates in PyRate

## Overview

BDNN (`PyRate.py ... -BDNNmodel 1`) "modulates speciation and extinction rates per lineage and through time as a function of" (1) **time**, (2) "one or multiple **categorical and/or continuous traits** (e.g. diet, body mass, geographic range)", (3) "one or more **time-dependent variables** (e.g. paleotemperature)" and (4) "**phylogenetic relatedness** (e.g. classification into higher taxa or phylogenetic eigenvectors)" — `references/tutorial-bdnn.md`:29-34. Because the rate function "is based on a fully connected feed-forward neural network, it is not based on *a priori* assumptions about its shape": it allows "non-linear and non-monotonic responses of the rates to variation in the predictors" and "any interactions among the predictors" (line 36-37). The network parameters are "estimated jointly with the origination and extinction times of all taxa and the preservation rates" (line 39), and the output serves to "estimate rate variation through time, across species, and to identify the most important predictors of such variation and their individual or combined effects" (line 40). Everything runs through `PyRate.py`; no program named `PyRateBDNN` exists anywhere in this corpus (`../pyrate/references/home.md`:28-60 lists only `PyRate.py`, `PyRateContinuous.py`, `PyRateMCDD.py`, `PyRateDES.py`, `pyrate_lib`).

The single riskiest assumption this skill inherits: **BDNN is documented by exactly one page** — `grep -rli bdnn` over the corpus returns only the tutorial (both languages) plus its one-line entry in the tutorials index. It is the largest page in the corpus (475 body lines; the next longest printed page is tutorial 5 at 376), the mirror is 483 lines with frontmatter at 1-8, and none of its 25 `-BDNN*`/`-plotBDNN*`/`-combBDNN` commands appears in the PyRate command list (`grep -c -i bdnn ../pyrate-command-reference/references/command-list.md` = 0), so any value not printed in that page has no documented meaning — and every run described takes 'ca. 45 minutes' at best (line 44) and "approximately half a day" for the full-length settings (line 234), so a wrong flag costs hours. Python 2.6-2.7 only (`../pyrate/references/home.md`:69 also states "Python 3.x is currently not supported"), `numpy`/`scipy` required (`../pyrate/references/home.md`:69-71).

## BDNN vs the Covar / PyRateContinuous / MBD routes

| Route | How it is launched | Shape of the rate function | Predictors it accepts | Preservation + origination/extinction times | Use it when |
| --- | --- | --- | --- | --- | --- |
| **BDNN** (this skill) | `python ./PyRate.py <occs.py> -BDNNmodel 1 ...` (bdnn:55) | feed-forward NN, non-linear, non-monotonic, all two-way (and more) interactions, no *a priori* shape (bdnn:36-37) | time (1-myr bins by default, bdnn:223) + many continuous and categorical traits via `-trait_file` + time-series via `-BDNNtimevar` (both bdnn:223) | inferred jointly with the network (bdnn:39); all preservation-model commands still apply (`-mG`, `-qShift`, bdnn:225-226) | heterogeneous predictor sets incl. one-hot multi-state traits; you refuse to assume linear/exponential; you want SHAP-style importance ranking |
| **Covar** | `PyRate.py ... -mCov 1-5` (+ `-trait_file` / `-trait`) | "speciation and extinction rates change in a lineage-specific fashion as a function of an estimated correlation with a continuous trait" (`../pyrate-command-reference/references/command-list.md`:130) | **one continuous trait** (correlation parameters `cov_sp`, `cov_ex`, `cov_q`: same:138) | jointly, as in standard PyRate | a single quantitative trait whose effect you are willing to assume monotone; the `-mCov` values, the normal(0,1) prior and `-pC` (all `command-list.md`:130-188) are owned by `../pyrate-command-reference` and `../pyrate-trait-age-models` |
| **PyRateContinuous** | `PyRateContinuous.py -d <se_est.txt> [-DD \| -c <var.txt>] -m` | "linear or exponential correlations with a time continuous variable" (`../pyrate/references/home.md`:39-40) | **one** time-continuous variable (`-c`) or the clade's own diversity (`-DD`): `../pyrate-continuous-covariates/references/pyratecontinuous.md`:28-32 | **not modelled**: "The program does not model preservation and assumes that the times of origination and extinction of each lineage are known" (same file:10) | times already estimated, one driver at a time; the `-m` value list, its default and `-A 1` model testing are owned by `../pyrate-continuous-covariates` (same file:34-38, 26) |
| **MBD** (multivariate birth-death) | `./PyRateMBD.py -d <SE.txt> -var <folder> -m 1` (`../pyrate-trait-age-models/references/tutorial-4.md`:68) | "linear or exponential functions linking the temporal variation of birth-death rates with changes in one or more variables"; one correlation parameter per variable (same file:46-47) | multiple time-continuous variables, each a tab-separated `time / predictor` file in one folder (same:53-56,71) | fixed: needs the "table with estimated speciation and extinction times" (same:53), i.e. the `-ginput` output (`../pyrate-summarize-results/references/tutorial-2.md`:41-43) | many time-continuous drivers at once on given times; the horseshoe vs gamma hyper-prior choice (same file:49-51) is owned by `../pyrate-trait-age-models` |

BDNN is the only one of the four that keeps the neural-network shape *and* re-estimates times and preservation — note the last section of the tutorial (bdnn:465-483) shows BDNN run on **fixed** times with `-d`, i.e. deliberately reduced to the Continuous/MBD input style.

## The 10 things that break a run

| # | What happens | Consequence | Wiki wording (`references/tutorial-bdnn.md`, CN twin at line+1) |
| --- | --- | --- | --- |
| 1 | Continuous traits or time-series fed un-transformed | Poor convergence — the page's only statement about preparing predictors for convergence is a MUST: "to improve model convergence **continuous traits and time-series predictors should be z-transformed** (i.e. subtracting the mean and dividing by the standard deviation)" | line 126; repeated for `-BDNNtimevar` at line 178 |
| 2 | Trait table with gaps | Undefined: "Species-specific traits need to be complete, i.e. no missing states or measures. Taxa with missing traits should either be included or can potentially be imputed" (line 128). Conflicts with the Covar `-trait_file` rule, which explicitly allows `NA` rows that "will be imputed by the MCMC" (`../pyrate-command-reference/references/command-list.md`:133) | line 128 |
| 3 | `-BDNN_groups` mis-quoted | The JSON must reach PyRate as **one** argument. The doc uses escaped quotes `"{\"geography\": [...]"` and says the "declaration of the `-BDNN_groups` includes *escaped quotes (i.e. \")"; on "a Linux or Mac system, the expression can be simplified with single quotes for the outer quotes" | lines 290-292 |
| 4 | Pre-binned time-series whose bins do not match the network's | "This needs to match the time bins of the neural network, which are by default 1 myr" (line 212); bins come from `-BDNNtimeres` / `-fixShift` (line 238) | lines 212, 238 |
| 5 | Forgetting that `-fixShift` is overloaded | In a BDNN run `-fixShift` defines the NN's custom bins ("use the `-fixShift` command to provide the path to a file defining custom bins' boundaries", line 238) while the command list documents the same flag as fixing birth-death rate shifts and warns it "will automatically switch the priors on speciation and extinction rates into half-Cauchy distributions" (`../pyrate-command-reference/references/command-list.md`:124). No page states what that side effect means for a BDNN run | line 238 |
| 6 | Custom taxon x time tables: wrong count, wrong names, or extra flags | "one custom table per time-bin is needed" / "the number of tables need to equal the number of boundaries", files named *01.txt*, *02.txt*, ... "for the most recent one" and older; "No additional `-trait_file` and `-BDNNtimevar` should be invoked" | lines 409-411 |
| 7 | Copy-pasting a `*_mcmc.log` path from the docs | The tutorial uses two different log names for the same dataset — `Carnivora_occs_1_G_BD1-1_BDNN_16_8TVc_mcmc.log` (line 61) and `Carnivora_occs_1_G_BDS_BDNN_16_8TVc_mcmc.log` (line 261) — and never explains the encoding (`G`, `BD1-1` vs `BDS`, `16_8`, `TVc`, `Grj`) nor prints the name a run writes. Take the name from your own output directory | lines 61, 261, 477 |
| 8 | Chain still moving when `-n` ends | "BDNN inferrences may need more MCMC generations than expected to reach the stationarity distribution of the Markov chain and the selected number of generation `-n` might be to small" [sic] → continue with `-restore_mcmc <logfile>` and re-pass the model arguments (line 433-436) | line 433 |
| 9 | Post-processing cost blows up | `-BDNN_interaction` "can last a while to compute and may use a lot of memory, especially for continuous predictors because for three continuous predictors we need to calculate 100 x 100 x 100 rates" (line 312); `-BDNN_pred_importance_interaction` "will be much slower" (line 360); the permutation correction "takes very long if the shortest bin is very small (e.g. the Holocene)" (line 362) | lines 312, 360, 362 |
| 10 | Several BDNN runs in one folder without `-out` | "`-out` arguments allow us to add a suffix to the output files" (line 252); the command list calls it out as the way "to avoid overwriting output files when running several instances of the same analysis" (`../pyrate-command-reference/references/command-list.md`:33-35); with combined/replicated files the suffix is also the `-tag` selector (line 460) | lines 252, 460 |

## Complete example for the impatient (verbatim, mirror lines 43-115)

The whole section, every line and number as the tutorial prints it. "This will take you ca. 45 minutes and assumes some familiarity with PyRate" (line 44). Fixture: `../assets/files/bdnn-impatient.sh`.

```sh
cd /your/path/to/PyRate-master

python ./PyRate.py ./example_files/BDNN_examples/Carnivora/Carnivora_occs.py -BDNNmodel 1 -trait_file ./example_files/BDNN_examples/Carnivora/Traits.txt -BDNNtimevar ./example_files/BDNN_examples/Carnivora/Paleotemperature.txt -mG -qShift ./example_files/BDNN_examples/Carnivora/Stages.txt -n 200001 -p 20000 -s 5000

python ./PyRate.py -plotBDNN ./example_files/BDNN_examples/Carnivora/pyrate_mcmc_logs/Carnivora_occs_1_G_BD1-1_BDNN_16_8TVc_mcmc.log -b 0.5

python ./PyRate.py -plotBDNN_effects ./example_files/BDNN_examples/Carnivora/pyrate_mcmc_logs/Carnivora_occs_1_G_BD1-1_BDNN_16_8TVc_mcmc.log -plotBDNN_transf_features ./example_files/BDNN_examples/Carnivora/Backscale.txt -BDNN_groups "{\"geography\": [\"Eurasia\", \"NAmerica\"], \"taxon\": [\"Amphicyonidae\", \"Canidae\", \"Felidae\", \"FeliformiaOther\", \"Hyaenidae\", \"Musteloidea\", \"Ursidae\", \"Viverridae\"]}" -b 0.5

python ./PyRate.py -BDNN_pred_importance ./example_files/BDNN_examples/Carnivora/pyrate_mcmc_logs/Carnivora_occs_1_G_BD1-1_BDNN_16_8TVc_mcmc.log -plotBDNN_transf_features ./example_files/BDNN_examples/Carnivora/Backscale.txt -BDNN_groups "{\"geography\": [\"Eurasia\", \"NAmerica\"], \"taxon\": [\"Amphicyonidae\", \"Canidae\", \"Felidae\", \"FeliformiaOther\", \"Hyaenidae\", \"Musteloidea\", \"Ursidae\", \"Viverridae\"]}" -b 0.5 -BDNN_nsim_expected_cv 10
```

Reading the four steps: `-plotBDNN` "will create a PDF file with the marginal rates through time (RTT)" (line 59); `-b 0.5` "discards 50% of the MCMC samples as burnin" (line 64); `-plotBDNN_transf_features` "rescales z-transformed continuous traits and time-series predictors to their original scale" and `-BDNN_groups` "used to display categorical predictors with multiple unordered states, for instance, the family to which each taxon belongs in the same figure" (line 76); `-BDNN_nsim_expected_cv 10` is set "(instead of the default 100) to safe some time for the impatient" [sic] (line 94). The dataset is "genus-level occurrence data of northern hemisphere Cenozoic carnivores, a table with a paleotemperature time series, and a table with lineage-specific traits: log-transformed body mass, taxonomic information (family-level classification), and continent of occurrence" from "Hauffe et al 2022 MEE" (line 124).

## Setting up a BDNN dataset

Occurrences stay in the standard PyRate input file (line 120, format owned by `../pyrate-input-file`); the extras are two plain tables: "A tab-separated text file with species-specific trait data can be loaded in the analysis using the `-trait_table` command, while a table with time-series predictors can be loaded using the `-BDNNtimevar` command" (line 122) — **note the flag name printed there is `-trait_table`, which appears nowhere else in the corpus; the page otherwise uses `-trait_file` in all nine command lines (55, 208, 230, 249, 397, 427, 436, 447, 482) and in four prose mentions (223, 408, 409, 411) — 13 in total (`grep -c -- "-trait_file" references/tutorial-bdnn.md`) — and `-trait_table` is not in the command list either**. Treat line 122 as a typo and use `-trait_file`. "The tables are simple tab-separated text files with a header" (line 124).

Naming rule, stated off this page: a trait table's first column is its taxon list, and the command list — which documents the very flag every BDNN command above passes — requires "The first column of the table should include the species names (identical to those used in the PyRate file)" (`../pyrate-command-reference/references/command-list.md:133`). The BDNN page never repeats the requirement and never says what happens when a name does not match (undocumented); its four printed trait tables are consistent with it, each headed `scientificName` (`references/tutorial-bdnn.md:135,143,152,161`), and the custom taxon x time tables deliberately drop that column ("but no column with taxon names", `references/tutorial-bdnn.md:409`). Only the naming clause transfers: the same command-list sentence goes on to let you omit taxa or give them `NA`, which the BDNN page forbids — "Species-specific traits need to be complete, i.e. no missing states or measures" (`references/tutorial-bdnn.md:128`, hazard 2 above).

### Trait encodings (line 131-175)

| Trait type | Rule (verbatim key words) | Example printed | Fixture |
| --- | --- | --- | --- |
| Binary, one of two states | "should be 0-1 encoded" (line 133) | `scientificName / Aquatic`: `Orcinus 1`, `Cavia 0` (135-138) | `../assets/files/bdnn-trait-binary-EXCERPT.txt` |
| Unordered, >2 states | "should be one-hot encoded" (line 141) | family columns `Felidae Musteloidea Ursidae` for *Acinonyx / Actiocyon / Agriotherium* (143-147) | `../assets/files/bdnn-trait-onehot-unordered-EXCERPT.txt` |
| Unordered, taxon may hold several states | "should also be one-hot encoded" (line 150) | geography `Eurasia NAmerica`, `Agriotherium 1 1` (152-156) | `../assets/files/bdnn-trait-onehot-multistate-EXCERPT.txt` |
| Ordered, >2 states | "should be encoded with integers", best centered on zero "i.e. subtracting the real-numbered value closest to the median of the states" (line 159); six states 0, 0, 1, 2, 3, 4 become -2, -2, -1, 0, 1, 2 because "the median is 1.5" (line 159) — note that 1.5 is *named* as the median while 2 is what the page subtracts and what it then prints in the Backscale row; see the contradiction spelled out in the Backscale subsection below | `Ordered_trait` column (161-168) | `../assets/files/bdnn-trait-ordered-centered-EXCERPT.txt` |

### Backscale / `-plotBDNN_transf_features` file

"The original mean and standard deviation can be stored in a tab-separated text file" (`references/tutorial-bdnn.md:126`), the example being `Backscale.txt`, and the file is laid out with "the mean in the first row and the standard deviation in the second row" (`references/tutorial-bdnn.md:190`). **For a centered ordered trait the page contradicts itself, and this suite does not pick a side.** The prose at `references/tutorial-bdnn.md:159` asks for "the value in the first row equal to the median and the value in the second row set to 1", yet in the same sentence, for the states 0, 0, 1, 2, 3, 4 it says "we subtract 2 from each state because the median is 1.5" — and the column it then prints for that very trait (`references/tutorial-bdnn.md:172-175`, `Ordered_trait` over `2` over `1`) holds 2, i.e. the offset that was subtracted, not the 1.5 the prose names as the median. So either the first row is the median and the printed file is wrong, or the first row is the offset actually subtracted and the prose misuses the word median; `references/tutorial-bdnn.md:170` states the purpose ("To have labels for the partial dependence plots beginning with zero") and, on the codes printed at `references/tutorial-bdnn.md:161-168`, the label starts at zero only for the second reading (the smallest code is -2) — **that resolution is inferred: no line of this corpus says which of its two values belongs in the row, and a file written from the prose alone (1.5) would not reproduce the file the page prints.** Adding temperature gives `Ordered_trait Temperature` with rows `2 16.02` and `1 2.20` (`references/tutorial-bdnn.md:192-195`), where the sentence at `references/tutorial-bdnn.md:190` calls that same first row a *mean*. The file itself "is optional and does not change anything in the BDNN model inference. The effect plot using the `-plotBDNN_effects` command will be more meaningful though" (`references/tutorial-bdnn.md:198`). Fixtures: `../assets/files/bdnn-Backscale-ordered-only-EXCERPT.txt`, `../assets/files/bdnn-Backscale-EXCERPT.txt`.

### Time-series predictors (`-BDNNtimevar`)

"need to include **time** as the first column and the actual time-series variable in the following columns. These variables should be z-transformed to improve model convergence" (line 178) — shape in `../assets/files/bdnn-BDNNtimevar-ztransformed-EXCERPT.txt` (`Time Temperature Prey`, 7 rows from 0.00 to 7.35 Ma, lines 180-188). Two file paths give different series to speciation and extinction, but "These files should have the same column names though" (line 205); the run using it is at line 208 (`-out _different_timevar`). Already-binned series are accepted: the `Time` value is the bin start, "Mean value from 0.0-0.9999 Ma" etc. (lines 214-218, fixture `../assets/files/bdnn-BDNNtimevar-binned-EXCERPT.txt`), and "This needs to match the time bins of the neural network, which are by default 1 myr" (line 212).

### Custom time bins

"While origination and extinction times of the taxa are inferred in continuous time, the time effect of the BDNN and time-series are by default binned into 1-myr bins" (line 238). Uniform alternative: `-BDNNtimeres 0.5` "to set all bins to 0.5 million years" (line 238). Unequal bins: a `-fixShift` file that "should have the same format as the one for the `-qShift` of the preservation model (i.e. no header, just ages)" (line 238) — the printed example is `0.0117 / 0.126 / 0.781 / 1.8` (lines 240-245, fixture `../assets/files/bdnn-Time_windows.txt`). Motivation: "capture the higher temperature variability in the Pleistocene", and "larger bins could be useful for periods with few fossil occurrences and will result in faster BDNN runs" (line 238). Run: line 249.

## Running a BDNN inference

"To run a BDNN analysis we need to provide the occurrence file and use the command `-BDNNmodel 1`. By default the BDNN model will only use time as predictor, discretized in 1-myr bins" (line 223); "Time as a predictor can be omitted by including the setting `-BDNNtimetrait 0`, but this should be justified" (line 223). All "standard commands to" define the preservation model "can be used in combination with the BDNN model" (line 225) — the page names none of them except the two it uses, so the menu itself lives in `../pyrate-preservation-models` / `../pyrate-command-reference/references/command-list.md`:85-106 (`-mHPP`, `-qShift`, `-mG`, `-ncat`, `-fixSE`); the tutorial pairs `-qShift` (time-variable preservation) with `-mG` (variation in sampling among species) (line 226).

| Flag on the reference run (line 230) | Meaning as printed (line 232-234) | Default elsewhere |
| --- | --- | --- |
| `-n 20000001` | "total of MCMC iterations" | `-n 10000000` (`../pyrate-command-reference/references/command-list.md`:58) |
| `-s 20000` | "sampling frequency" | `-s 1000` (same:62) |
| `-p 10000` | "frequency of prints on your screen" | example `-p 1000`, no default stated (same:66) |
| `-j 2` | "the different replicates can be selected with the `-j` argument (e.g. `-j 2` for the second replicate)" (line 234, 444-447) | `-j 1` (same:30) |
| `-out _time_windows` | "add a suffix to the output files" (line 252, 418) | no default printed; `command-list.md`:32-35 only says it will "Add tag to default stem name of output files" |
| `-mG`, `-qShift <file>` | preservation: Gamma across-taxa heterogeneity / TPP bins | `command-list.md`:91-99 |
| `-edgeShift 15.97 2.5` | "we can fix shifts at boundaries, while searching for rate variation between them" (line 394) | see `../pyrate-bd-analysis/references/tutorial-1.md`:267-276 |
| `-qFilter 0` | "Adding `-qFilter` allows for shifts in sampling rates at the boundaries" (line 394) | value list documented nowhere in this corpus |
| `-fixShift <file>` | custom NN bins (line 238) | see hazard 5 |
| `-restore_mcmc <log>` | "restore the MCMC chain from the last sample" (line 433) | n/a |
| `-d <se_est.txt>` | BDNN on given times; `-d` "automatically sets `-fixSE = null`" / "the MCMC only samples the birth-death parameters" (`command-list.md`:18) | n/a |

Timing to quote to a user: the 200001-generation impatient run "will take you ca. 45 minutes" (line 44); the 20000001-generation run "will last approximately half a day" (line 234). Long-run outputs are shipped in the repo's `Advanced_examples/Example_output` (lines 234, 252, 418).

### Network hyper-parameters (`Other options`, lines 377-389)

| Option | Values / default as printed | Line |
| --- | --- | --- |
| `-BDNNnodes 16 8` | "Defines the number of layers and nodes in each layer (default: two layers of 18 and 8 nodes); 30 20 10 would specify three layers with 30, 20, and 10 nodes" — the flag occurs exactly once in the page (`grep -c -- "-BDNNnodes" references/tutorial-bdnn.md` = 1) and there it is `16 8`, while the stated default is 18 and 8 and every log name printed says `BDNN_16_8`; no resolution in this corpus | 381 |
| `-BDNNoutputfun` | "Activation function of the output layer: 0) abs, 1) softPlus, 2) exp, 3) relu 4) sigmoid 5) sigmoid_rate (default=5)" | 383 |
| `-BDNNactfun` | "Activation function of the hidden layer(s): 0) tanh, 1) relu, 2) leaky_relu, 3) swish, 4) sigmoid (default=0)" | 385 |
| `-BDNNreg` | "whether the regularization layer should be omitted by setting it to -1.0. The default value of 1.0 for the truncated exponential prior assigns the highest probability of no effect on the BDNN predictors. Higher positive values increase this weight." Same `t_reg` for both rates by default; make them independent with `-BDNNreg 1.0 1.0`; `-BDNNreg 1.0 -1.0` = "regularization for speciation but not extinction" | 387 |
| `-BDNNprecision` | "Sets the floating point precision of the neural network nodes and influences the BDNN speed. Default value of 1 refers to 32bit single precision i.e. 7 decimal digits." Then the same sentence contradicts it: "Use this double precision (i.e. 16 decimal digits) with `-BDNNprecision 1` if your per_species_rates.log shows extremely small values of e.g. 0.000001 (Better: `-rescale` your occurrence data)." — the flag value selecting double precision is undocumented (`-rescale` occurs nowhere in the corpus except in this same sentence) | 389 |

Line 232 announces "Additional Hyper-parameters specifying the network structure and prior settings", pointing at *Other options* — that block (377-389) contains exactly `-BDNNnodes`, `-BDNNoutputfun`, `-BDNNactfun`, `-BDNNreg`, `-BDNNprecision`; `-BDNNmodel` itself is the model switch of line 223 and is *not* listed there.

## Output post-processing

The post-processing commands all take a `*mcmc.log` file (or, for `-combBDNN`, the log folder) and write their output into `pyrate_mcmc_logs/`. In the two BDNN option lists `-b` is "Burnin fraction (default 0.1)" (lines 297, 352) — that differs from the core `-b 0` default in `../pyrate-command-reference/references/command-list.md`:71, and `-b` "When set to a number between 0 and 1, it is interpreted as a fraction of the total number of MCMC generations" (same:69).

### Marginal rates through time — `-plotBDNN` (lines 257-275)

`python ./PyRate.py -plotBDNN <log> -b 0.1` (line 261): "This uses the `_sp_rates.log` and `_ex_rates.log` files from the `pyrate_mcmc_logs` directory. The command will generate a PDF file and an R script with the rates-through-time plots, which will be saved in the `pyrate_mcmc_logs` directory. Rates can be visualized on a log scale by adding `-logT 2` and truncated with `-root_plot` and `-min_age_plot`. The R script file can be edited to customize the plot" (line 264). `-logT` here means *plot* log-scaling; for Covar models the same flag means trait transformation (`command-list.md`:150-155) — do not carry one meaning into the other. Subsets of taxa: `-plotBDNN_groups <tab-separated taxon/group file>` (line 271), e.g. families Amphicyonidae / Canidae / Musteloidea, Eurasia, "weighing less than 10 kg, or just for the gluttonous eater (_Borophagus_)" (line 268); the file's columns are never printed. After an `-edgeShift` run, "We can then truncate the rates through time plot at the boundaries with the `-min_age_plot` and `-root_plot` arguments" (line 400) — line 402 does it with `-min_age_plot 2.6 -root_plot 15.9 -b 0.5`, on a log whose name carries an extra `edge` element (see hazard 7 before reusing it).

### Partial dependence plots — `-plotBDNN_effects` (lines 279-307)

PDPs "marginalize over the remaining predictors, i.e. cancelling out their effect and displaying only the effect attributed to the respective predictor(s)"; "Although net diversification rate is not an inferred model parameter itself, we can display the effect on it by subtracting the extinction PDP from the speciation PDP" (line 280). Command at line 283. Options (lines 295-307): `-b` (default 0.1), `-resample` "Number of post burnin MCMC samples (using all by default)" — use ~100 because "the log file may contain thousands of samples. However, 100 should be sufficient" (lines 286, 299), `-plotBDNN_transf_features`, `-BDNN_groups`, `-root_plot`/`-min_age_plot` ("Considers only taxa originating or going extinct in this time window"), `-thread 2 0` ("Number of CPU cores to be used for parallel calculation of importance metrics"; two values = BD and NHPP likelihoods, `command-list.md`:75-79). Output: "generate a PDF file and an R script" saved in the `pyrate_mcmc_logs` directory (line 288). The Linux/Mac spelling of the groups argument is line 292.

### More than two predictors — `-BDNN_interaction` (lines 310-337)

PDP figures cover single predictors and two-way interactions only; "you can obtain a text file with the partial dependence rates for any set of predictors with the `-BDNN_interaction` command" (line 312), predictors listed via `-BDNN_groups`, which "can contain a mixture of continuous and categorical predictors (while this flag is usually reserved for one-hot encoded categorical traits)" (line 329). Commands: line 316 (BodyMass + Temperature + time), line 331 (with `taxon`), line 336 (adds `-BDNN_interaction_fix`). It "will create four text files in the *pyrate_mcmc_logs* folder (two for speciation and two for extinction)" (line 319): the `*_pdp.csv` files whose first columns "are named according to the `-BDNN_groups`" and whose last three columns are mean and "upper and lower 95% credible interval" (line 320), plus a file of "the predictor's values of the taxa at their inferred time of origination or extinction", useful "to truncate the *_pdp.csv* file to the observed range of predictors" (line 327). `-BDNN_interaction` "can be also used to get species-specific speciation and extinction rates", which "basically asks: *What would be the speciation (or extinction) rate of a taxon at the time of its origination (or extinction) if its family and its geographic distribution would not matter?*" (line 334); the example that adds `-BDNN_interaction_fix` to do so is at line 336. The printed `_pdp.csv` example has a 6-column header (line 322) and a 7-field first row (line 324) — the doc's own error, reproduced identically in the CN twin (lines 323 and 325); fixture `../assets/files/bdnn-pdp-EXCERPT.txt`.

### Predictor importance — `-BDNN_pred_importance` (lines 340-374)

Three metrics: "1) the marginal posterior probability of an effect, 2) the effect size of the predictor on the rates (SHAP values), and 3) the effect of the predictor on model fit (feature permutation)" (line 342); command at line 347 (printed as `python PyRate.py`, without the `./` used everywhere else). Options: `-b`, `-resample`, `-BDNN_nsim_expected_cv` (default 100; "The postprocessing step of getting the expected rate variation is ommitted when set to 0"), `-BDNN_pred_importance_nperm` (default 100), `-BDNN_pred_importance_interaction` (also rank two-way interactions; "this will be much slower"), `-BDNN_pred_importance_window_size 0.1`, `-BDNN_groups` ("Works, however, also for groups of continuous traits (but not in combination with `-BDNN_pred_importance_interaction`)"), `-BDNN_mean_shap_per_group`, `-root_plot`/`-min_age_plot`, `-thread` (lines 350-370). It "creates seven files in the log files' folder" (line 96): named in the docs are `_coefficient_of_rate_variation.csv` (line 96), `_sp_predictor_influence.csv` and `_ex_predictor_influence.csv` (line 104) — which are the "two tab-separated tables with the estimated importance and ranking of each predictor" of line 373 — plus "a PDF file and an R script with the lineage-specific speciation and extinction rates" (line 373). That is 5 named files against "seven" (96) and against "the remaining four output files" (line 115): the page's own arithmetic does not close (5 + 4 = 9 != 7), so never quote a file count to a user — list what your run actually wrote.

Interpreting the two tables (line 113): `feature1` = predictor; `feature1_state` = "the pairwise comparison for categorical predictors"; `posterior_probability` "quantifies the consistency of the direction of the predictors' effect (e.g. the proportion of the 10 sub-sampled MCMC generations genera of which the family Amphicyonidae had an higher extinction rate than Canidae)" [sic]; `shap` "measures the effect size of the predictor"; `delta_lik` "is the decrease in model likelihood when permuting the predictor"; `rank` = "the consensus among the individual importance ranking of these three metrics". The CV file compares empirical rate variation with "the upper 95% quantile of rate variation under a constant diversification process with the same root age and a similar number of taxa ± 25% as the analysed dataset. An output with higher empirical rate variation than expected permits to dig into which predictors are mainly causing this variation" (line 96) — the printed Carnivora result: speciation 0.55 vs 0.29, extinction 0.82 vs 0.34 (lines 98-101; fixtures `../assets/files/bdnn-cv_rate_variation-EXCERPT.txt`, `../assets/files/bdnn-predictor_influence-EXCERPT.txt`).

### Custom predictors, restart, replicates, fixed times

* **Custom taxon x time tables** (lines 406-428). Needed because a regular run "assumes that species traits do not change over time and that all species experience the same environmental conditions over time" (line 408). For species-specific / time-specific values (e.g. continent-specific temperature, humans affecting only extinction): tables "have a similar format as the standard `-trait_file` (i.e., species in rows and traits, including paleoenvironment, in columns, but no column with taxon names)"; file names *01.txt*, *02.txt* ...; loaded with `-BDNNpath_taxon_time_tables`, which "takes the path to a folder containing the custom tables" — one path = both rates, "the first one is for the predictors of speciation rates and the second for extinction rates"; no `-trait_file`/`-BDNNtimevar` alongside (lines 409-411); run at line 415 (`-out _taxon_time_tables`, output suffix named at line 418). `-BDNNexport_taxon_time_tables` (line 427) writes the tables a normal run builds, "To help setting-up the correct number of custom tables and get their format right" (line 425); those exports "could then be modified using a text editor or spreadsheet software" (line 425).
* **Re-starting** (lines 431-437): `-restore_mcmc <log>` plus the original model arguments (the example at line 436 re-passes `-BDNNmodel 1`, `-trait_file`, `-BDNNtimevar`, `-mG`, `-qShift`, `-n`, `-p`, `-s`).
* **Combining replicates** (lines 440-462): replicates exist "To account for age uncertainty in fossil occurrences, you should create multiple replicates with randomly sampled ages" (line 442); the BDNN model "can be inferred for these replicates independently and their output files can be combined to obtain e.g. a single rate through time plot for all replicates or obtain the predictor importance across replicates" (line 442). Run each replicate with `-j n` (line 447; "the Carnivora example dataset contains three replicates", line 444), then `python ./PyRate.py -combBDNN <log_folder> -b 0.25` (line 453) — line 456 calls the positional argument `path_to_your_log_files` and says it "specifies the directory where the log files are (e.g., pyrate_mcmc_logs)". It "generates five output files" (line 457): `combined_[n]_mcmc.log`, `combined_[n]_per_species_rates.log`, `combined_[n]_sp_rates.log`, `combined_[n]_ex_rates.log`, `combined_[n].pkl` — "[n] is the number of combined replicates" (line 457, which quotes only the first name with typographic marks and the last with none); `-b 0.25` "specifies that the first 25% of all MCMC samples from each file should be excluded as burnin" and the right burnin "should be determined after inspecting the mcmc.log files, e.g. using Tracer" (line 458); `-resample` "To avoid producing too large combined files you can sub-sample each log file" (line 458, "A value of 100 sub-samples is typically enough"); `-tag taxon_time_tables` selects which analyses to combine when several share the folder (line 460); afterwards "we do not need to specify these parameters in post-processing steps like `-plotBDNN_effects` or `-BDNN_pred_importance`" (line 462). The equivalent non-BDNN commands are `-combLog` (`../pyrate-bd-analysis/references/tutorial-1.md`:227-229) and `-combLogRJ`, which "generates three output files" (`../pyrate-rjmcmc/references/tutorial-3.md`:101).
* **Fixed origination/extinction times** (lines 465-483): "the input file is a simple table with the times of origination and extinction of each lineage" (line 467). Infer times with `-A 4 -qShift ... -mG -n 1000001 -p 100000 -s 10000` (line 472) → `-ginput <log> -b 0.25` produces `..._se_est.txt` (line 477, documented in `../pyrate-continuous-covariates/references/pyratecontinuous.md`:13-18 and `../pyrate-summarize-results/references/tutorial-2.md`:94-95) → `python ./PyRate.py -d <se_est.txt> -BDNNmodel 1 -trait_file <Traits.txt> -n 500001 -p 20000 -s 5000` (line 482); note this last command passes no `-BDNNtimevar`, `-mG` or `-qShift`. `-A 4` = the RJMCMC algorithm (`../pyrate-bd-analysis/references/tutorial-1.md`:269) although `-A`'s own list stops at `-A 3` with `-A 2` default (`command-list.md`:46-54).

### Files a BDNN run and its post-processing produce

| File | Written by | Notes |
| --- | --- | --- |
| `<stem>_<j>_<...>_BDNN_<nodes>_<...>_mcmc.log` | inference | name never explained; see hazard 7 |
| `_sp_rates.log`, `_ex_rates.log` | inference | read by `-plotBDNN` (line 264) |
| `per_species_rates.log` | inference (by inference: the page only says "your per_species_rates.log", line 389, and never states which step writes it) | the file to watch for "extremely small values of e.g. 0.000001" (line 389) |
| PDF + R script (RTT) | `-plotBDNN` | in `pyrate_mcmc_logs` (line 264) |
| PDF + R script (PDPs) | `-plotBDNN_effects` | line 288 |
| four text files: `*_pdp.csv` + what line 327 calls "The other text file" | `-BDNN_interaction` | lines 319-327 (four files promised, only the *_pdp.csv pair actually named) |
| `_coefficient_of_rate_variation.csv`, `_sp_predictor_influence.csv`, `_ex_predictor_influence.csv`, PDF + R script, + 4 unnamed | `-BDNN_pred_importance` | lines 96, 104, 115, 373 |
| `combined_[n]_mcmc.log`, `combined_[n]_per_species_rates.log`, `combined_[n]_sp_rates.log`, `combined_[n]_ex_rates.log`, `combined_[n].pkl` | `-combBDNN` | line 457 |
| exported taxon x time tables | `-BDNNexport_taxon_time_tables` | line 425 (folder/name pattern not printed) |

## The six Carnivora_BDNN figures (`../assets/images/`)

| Figure | `<img>` line / caption line | What it shows (caption wording) |
| --- | --- | --- |
| `Carnivora_BDNN_RTT.png` | 66 / 67 | "Rates through time plot for the Carnivora BDNN analysis obtained with the command `-plotBDNN`" |
| `Carnivora_BDNN_family_speciation.png` | 78 / 79 | "Carnivora families have different speciation rates according to the partial dependence plots" |
| `Carnivora_BDNN_temp_extinction.png` | 83 / 84 | "Lower temperatures are related to higher extinction rates according to the partial dependence plots. Ticks along the x-axis display the observed values of the predictor at the inferred extinction times of the species" |
| `Carnivora_BDNN_backtransformation.png` | 200 / 201 | "Temperature effect on carnivore extinction rate with (right) and without (left) reversing the z-transformation of temperature with the `-plotBDNN_transf_features` argument when creating the effect plot from the same BDNN log file" |
| `Carnivora_BDNN_RTT_Borophagus.png` | 274 / 275 | "Species-specific rates through time plot for the gluttonous eater (<i>Borophagus</i>)" — the `-plotBDNN_groups` output of line 271 |
| `Carnivora_BDNN_humans.png` | 420 / 421 | PDP of the human / Carnivora spatial-temporal overlap on extinction; "The effect on extinction rate is higher in North America ... The effect of humans on Eurasian carnivores was permitted during the past 126,000 years. <i>Humans1.0</i> indicates spatial-temporal overlap" — the custom-predictor example of line 415 |

## Worked example

Offline checks on the fixtures (no PyRate needed), then the real run:

```sh
cd ../pyrate-bdnn                       # this skill directory

# 1. every command sequence parses, and every command line in the three scripts is
#    still byte-identical to a line of references/tutorial-bdnn.md (25 lines, silent on success)
for f in ../assets/files/bdnn-*.sh; do bash -n "$f" || echo "SYNTAX FAIL: $f"
  while IFS= read -r c; do grep -qF -- "$c" references/tutorial-bdnn.md \
      || echo "NOT VERBATIM in $f: $c"; done \
    < <(grep -v '^[[:space:]]*#' "$f" | grep -v '^[[:space:]]*$')
done

# 2. prove the escaped -BDNN_groups JSON survives the shell as ONE argument
#    (a stub named python shadows the interpreter, so nothing is executed)
python() { for a in "$@"; do case "$a" in '{"geography"'*)
    printf '%s\n' "$a" | python3 -c 'import json,sys; d=json.load(sys.stdin); print("  groups OK:", list(d), "->", d["taxon"][:3])';; esac; done; }
export -f python
sed '/^cd /d' ../assets/files/bdnn-impatient.sh | bash

# 3. look at the table shapes the tutorial describes
column -t -s "$(printf '\t')" ../assets/files/bdnn-trait-onehot-multistate-EXCERPT.txt
column -t -s "$(printf '\t')" ../assets/files/bdnn-Backscale-EXCERPT.txt
cat ../assets/files/bdnn-Time_windows.txt          # -fixShift custom bins: no header, just ages

# 4. the actual analysis (needs a PyRate checkout, Python 2.7, R; ~45 min at -n 200001)
#    cd /your/path/to/PyRate-master && bash <suite>/assets/files/bdnn-impatient.sh
#    then post-process:  bash <suite>/assets/files/bdnn-postprocess.sh
#    and the long variants (custom bins, edge shifts, custom tables, -combBDNN):
#    bash <suite>/assets/files/bdnn-run-analysis.sh
```

Step 2 prints two `groups OK: ['geography', 'taxon'] -> ['Amphicyonidae', 'Canidae', 'Felidae']` lines (one per command carrying `-BDNN_groups`); if your own shell mangles the argument, nothing is printed and the run would see several arguments instead of one.

## Pitfalls

- **Do not trust a `-b` default across commands.** The BDNN option lists say "Burnin fraction (default 0.1)" (lines 297, 352) while the core `-b` default is `-b 0` ("all samples are logged", `command-list.md`:71). Always pass `-b` explicitly, and remember `-combBDNN -b 0.25` burns 25% of *each* input file, not of the combined result (line 458).
- **After `-combBDNN`, drop `-b`/`-resample` from the post-processing calls** — "we do not need to specify these parameters in post-processing steps like `-plotBDNN_effects` or `-BDNN_pred_importance`" (line 462); repeating them silently burns the combined file a second time (by inference from lines 458-462).
- **The documented example numbers are tied to the `-resample` of that example.** The importance text explains `posterior_probability` as "the proportion of the 10 sub-sampled MCMC generations" (line 113), i.e. it is conditioned on the `-resample 10` of line 347; compare values only between runs sharing `-resample`.
- **`-BDNNprecision` cannot be set as the page instructs.** Line 389 names value `1` as 32-bit single precision *and* as the switch to 64-bit double precision; the CN twin (line 390) copies the contradiction rather than resolving it. If `per_species_rates.log` shows values like 0.000001, the page's own alternative — "Better: `-rescale` your occurrence data" (line 389) — names a flag whose only occurrence in the whole corpus is that one sentence (`grep -rn -- "-rescale" /path/to/PyRate-doc` hits the BDNN tutorial and its CN twin only); no page documents its values or even confirms it exists as a command.
- **Time-varying predictor effects need custom tables, not `-BDNNtimevar` twice.** The plain route assumes "species traits do not change over time and that all species experience the same environmental conditions over time" (line 408); `-BDNNtimevar a b` only splits speciation vs extinction (line 205).
- **`-BDNN_groups` is not only for one-hot traits** — with `-BDNN_interaction` you pass one-element groups for continuous predictors (`"{\"BodyMass\": [\"BodyMass\"], ... }"`, line 316) and mixtures (line 331); with `-BDNN_pred_importance` groups of continuous traits work "but not in combination with `-BDNN_pred_importance_interaction`" (line 364).
- **Expect the doc's own typos when grepping**: `-trait_table` (122), "to safe some time" (94), "specifiy" (238), "analyse" (252), "emergance" (205), "Tab-seperated" (301), "ommitted" (356), "inferrences ... might be to small" (433), "generations genera" (113) — and line 115 links `#predictor_importance` while the table of contents (line 20) and the heading (line 340) give `#predictor-importance`, so the "more details" link does not resolve.

## Not documented in this wiki

| Unanswered question | Why you must not fill it in |
| --- | --- |
| Which `-BDNNprecision` value gives double precision (line 389 names `1` for both) | the only two statements of the value-to-precision mapping contradict each other; the CN twin (390) repeats them verbatim |
| The default of `-BDNNnodes`: "two layers of 18 and 8 nodes" vs the page's only `-BDNNnodes 16 8` (381) and all 12 printed log names carrying `BDNN_16_8` | nothing else in the corpus states a network size; guessing 16/8 or 18/8 changes the model |
| What `G`, `BD1-1`, `BDS`, `16_8`, `TVc`, `Grj` mean in the log names | `grep -n "BDS\|BD1-1\|TVc\|Grj"` matches only inside this tutorial (14 lines); no naming rule is printed anywhere |
| The identity of the "remaining four output files" of `-BDNN_pred_importance` (line 115) | the page names five files across lines 96, 104 and 373 yet says it "creates seven files" (96) and refers to "the remaining four output files" (115); 5 + 4 != 7, so the set cannot be reconstructed from the doc |
| What a BDNN run does when a name in the trait table is not in the occurrence file (or the reverse) | the requirement itself is stated only for `-trait_file` on the command list, "identical to those used in the PyRate file" (`../pyrate-command-reference/references/command-list.md:133`); `references/tutorial-bdnn.md` never repeats it and prints no failure mode, so treat a mismatch as unexplored behaviour, not as a documented error |
| Which number belongs in the first row of an ordered trait's `Backscale.txt` column — the 1.5 that `references/tutorial-bdnn.md:159` calls the median, or the 2 the same page prints at `references/tutorial-bdnn.md:172-175` (and calls a *mean* at `references/tutorial-bdnn.md:190`) | the two statements are one sentence apart and nothing reconciles them; the codes at `references/tutorial-bdnn.md:161-168` plus the zero-label purpose at `references/tutorial-bdnn.md:170` point to 2, but no line of this corpus says so |
| The columns of `-plotBDNN_groups` files (`RTT_groups.csv`) | line 268 describes the subsets but never prints the table; the `-trait_file` shape at line 135 does not tell you whether a header is required |
| The contents of the Carnivora `Traits.txt`, `Paleotemperature.txt`, `Stages.txt`, `Backscale.txt`, `Carnivora_occs.py` | the page links the repo files but prints only hypothetical tables; do not present your reconstruction as the dataset |
| The `-qFilter` value list (line 394, `grep -rn -- '-qFilter'` matches only this tutorial in both languages) | the sentence says only "allows for shifts in sampling rates at the boundaries"; the meaning of `0` is not given |
| Whether `-restore_mcmc` appends to the same log, and which arguments must be repeated | line 433 gives the argument and one example that re-passes everything; no rule is stated |
| Whether `-plotBDNN*` commands call R automatically (and need `Rscript` on PATH) | lines 264/288/373 say a PDF and an R script are generated; only `../pyrate/references/home.md`:84 documents auto-execution "using the shell command `RScript`" and it is written about `-plot`, not `-plotBDNN` |
| Interaction of `-fixShift` with the half-Cauchy prior switch documented for it (`command-list.md`:124) | the BDNN page reuses the flag for NN bins (238) and says nothing about priors |
| Any default for `-BDNNtimeres`, `-BDNNtimetrait`, `-combBDNN`, or the `-BDNNexport_taxon_time_tables` output layout | `-BDNNtimeres` and `-BDNNtimetrait` appear exactly once each (238, 223), `-combBDNN` once (453), `-BDNNexport_taxon_time_tables` twice (425, 427) — `grep -c -- "-BDNNtimeres" references/tutorial-bdnn.md` = 1 — with no value list or default anywhere |
| Where the ± 25% taxon-count window and the "same root age" of the expected-CV simulation come from when times are uncertain | line 96 states the comparison but not which replicate/log supplies root age and taxon count |
| A citation for the BDNN model itself | the tutorial cites only the dataset paper "Hauffe et al 2022 MEE" (line 124); MBD gets Lehtonen et al. 2017 (`../pyrate-trait-age-models/references/tutorial-4.md`:46) and Covar gets its own paper (`command-list.md`:130) — do not attribute BDNN to either |
| Whether `-BDNNmodel` accepts values other than 1 | all 11 lines naming it in `references/tutorial-bdnn.md` (`grep -c -- "-BDNNmodel" references/tutorial-bdnn.md` = 11) are `-BDNNmodel 1`; no other value is printed anywhere in the corpus |

## Related skills

- `../pyrate-input-file` — the standard occurrence input file that BDNN requires (bdnn:120; its `Species / Status / MinT / MaxT` columns are documented there, `../pyrate-input-file/references/preparing-input-file.md`:16) and the R extraction utilities; BDNN never re-describes it.
- `../pyrate-preservation-models` — `-mG`, `-qShift`, `-mHPP`, `epochs_q.txt`-style bins; BDNN only says these "can be used in combination with the BDNN model" (bdnn:225-226).
- `../pyrate-bd-analysis` — the `-qShift`/`Stages.txt` workflow, `-out`, `-edgeShift` (`tutorial-1.md`:265-278), `-combLog` for replicates (`tutorial-1.md`:227-229), and `-A`/algorithm choice.
- `../pyrate-rjmcmc` — `-A 4` (the step that produces the times BDNN can consume via `-d`), `-root_plot`/`-min_age_plot` semantics (`tutorial-3.md`:82-84), `-combLogRJ` comparison.
- `../pyrate-summarize-results` — `-ginput`/`_se_est.txt` generation with `-b`, `-tag`, `-resample` (`tutorial-2.md`:45-60) and the `*mcmc.log` column layout.
- `../pyrate-continuous-covariates` — the `-d` table format and `-ginput` rule set (`pyratecontinuous.md`:11-18) plus the linear/exponential alternative to BDNN.
- `../pyrate-trait-age-models` — Covar (`-mCov`, `-trait`, `-pC`), ADE, and MBD (multi-predictor linear/exponential with horseshoe priors): the routes you compare BDNN against.
- `../pyrate-mcmc-tuning` — proposal-ratio tuning if the chain mixes poorly (the BDNN page offers only running more MCMC generations and `-restore_mcmc`, bdnn:433).
- `../pyrate-command-reference` — every shared flag's documented default (`-n`, `-s`, `-p`, `-b`, `-j`, `-out`, `-thread`, `-fixShift`, `-trait_file`, `-d`, `-logT`); it contains **no** `-BDNN*` entry.
- `../pyrate-installation` — Python 2.6-2.7 virtualenv, `numpy`/`scipy`, R for plotting.
- `../pyrate` — router: program list, tutorials index (BDNN is entry 7, `tutorials-index.md`:56), citations.

## Resources

| File | What's in it | Load when |
| --- | --- | --- |
| `references/tutorial-bdnn.md` | The whole tutorial 7 (483 lines; frontmatter 1-8, body 9-483; 29 headings): model description, the impatient example, dataset setup and trait encodings, the inference command and its hyper-parameters, `-plotBDNN` / `-plotBDNN_effects` / `-BDNN_interaction` / `-BDNN_pred_importance`, custom predictors, restart, `-combBDNN`, `-d` pipeline, the six Carnivora figures | Always — it is the only BDNN documentation in existence here |
| `references/tutorial-bdnn-cn.md` | Simplified-Chinese twin (484 lines; frontmatter 1-9, body 10-484, so body line = EN line + 1). All 26 fenced command blocks are byte-identical to the EN and every flag/number matches; it does **not** resolve the `-BDNNprecision` or `-BDNNnodes` contradictions | Reading a sentence you doubt; it never adds an option the EN lacks |
| `../pyrate-command-reference/references/command-list.md` | The shared flags a BDNN command line borrows, with their documented defaults: `-d` (17-20), `-j` (27-30), `-out` (32-35), `-A` (46-54), `-n`/`-s`/`-p`/`-b` (56-73), `-thread` (75-79), preservation models `-mHPP`/`-qShift`/`-mG`/`-ncat`/`-fixSE` (85-106), `-fixShift` (123-125), the Covar block incl. `-trait_file`, `-mCov`, `-trait`, `-logT` (129-155). Zero BDNN entries | Any flag that is not `-BDNN*`; checking a default |
| `../pyrate-continuous-covariates/references/pyratecontinuous.md` | `-ginput` (lines 13-18), the `-d` table columns (11), `-A`, `-DD`, `-c`, `-m` | Building the fixed-times BDNN input, or choosing the linear/exponential alternative |
| `../pyrate-trait-age-models/references/tutorial-4.md` | MBD: shape, predictors, `-var`, `-m`, horseshoe vs gamma priors (lines 44-91); Covar/ADE commands | Writing the justification for BDNN over MBD/Covar |
| `../pyrate-bd-analysis/references/tutorial-1.md` | `-qShift`/`-mG` usage, `-A 4` + `-edgeShift` (265-278), `-combLog` + `-tag` + `-b` (227-229) | Replicate handling and the preservation-model half of a BDNN command line |
| `../pyrate-rjmcmc/references/tutorial-3.md` | `-root_plot 23 -min_age_plot 5.3` semantics (82-84), `-combLogRJ` "generates three output files" (101) | Truncating BDNN RTT plots; comparing combine commands |
| `../pyrate-summarize-results/references/tutorial-2.md` | `-ginput ... -resample 10`, `-tag`, and "Generate input file for PyRateContinuous" (45-60, 94-95) | The `-d` step of the fixed-times pipeline |
| `../pyrate/references/home.md` | Program list (28-60), Python 2.6-2.7 / argparse / numpy / scipy (69-71), the `RScript` plotting note (84) — and no BDNN entry at all | Environment failures; documenting that BDNN lives inside `PyRate.py` |
| `../pyrate/references/tutorials-index.md` | The unnumbered bullet "Birth-death neural network (BDNN) model" (line 56) under "Other birth-death models"; the page itself is titled `PyRate Tutorial \#7` (bdnn:11) | Locating the tutorial upstream |

```sh
# run these from this skill directory
grep -n "^#\{1,4\} " references/tutorial-bdnn.md                       # 29 headings = the section map
grep -o -- "-[A-Za-z_]*BDNN[A-Za-z_]*" references/tutorial-bdnn.md | sort -u   # the 25 BDNN commands/options
grep -n "default" references/tutorial-bdnn.md | grep -i "bdnn\|burnin\|resample"   # every stated default (16 lines)
grep -n "Carnivora_BDNN" references/tutorial-bdnn.md                    # the six figures
grep -n -- "-trait_file\|-trait_table" references/tutorial-bdnn.md       # the -trait_table typo vs the 13 uses of -trait_file
grep -n "BDS\|BD1-1\|TVc\|Grj" references/tutorial-bdnn.md               # the unexplained log-name encoding
grep -n "_rates.log\|\.pkl\|_pdp.csv\|_influence.csv\|_coefficient_of_rate_variation.csv" references/tutorial-bdnn.md
grep -n -- '`-logT' ../pyrate-command-reference/references/command-list.md   # -logT means trait transformation there
```

## Runnable fixtures (`../assets/files/`)

The `.sh` fixtures carry a `# source:` header; the tab-separated tables are kept byte-clean (a header line would change what they demonstrate), so their provenance is this table — "EN" means `references/tutorial-bdnn.md` and "CN" means `references/tutorial-bdnn-cn.md`. Every command line in the three scripts was verified to occur verbatim in `references/tutorial-bdnn.md` — Worked example step 1 re-runs that check. Every table fixture is a markdown-table-to-TSV conversion of the lines named, values unchanged.

| Fixture | Provenance | What it makes concrete |
| --- | --- | --- |
| `../assets/files/bdnn-impatient.sh` | derived (commands verbatim; comments added) | the complete "Complete example for the impatient" sequence, lines 48-91 |
| `../assets/files/bdnn-run-analysis.sh` | derived (commands verbatim) | 12 inference variants: two time-series (208), reference run (230), custom bins (249), edge shifts (397), custom tables (415), export (427), `-restore_mcmc` (436), `-j 2` (447), `-combBDNN` (453), `-A 4`/`-ginput`/`-d` pipeline (472-482) |
| `../assets/files/bdnn-postprocess.sh` | derived (commands verbatim) | 8 post-processing commands (mirror lines 261-402) plus the single-quote `-BDNN_groups` fragment of line 292, kept as a comment because it is an argument, not a command |
| `../assets/files/bdnn-trait-binary-EXCERPT.txt` | derived from EN 135-138 (CN 136-139) | 0-1 encoded binary trait table: header + the 2 data rows the doc prints |
| `../assets/files/bdnn-trait-onehot-unordered-EXCERPT.txt` | derived from EN 143-147 | one-hot family columns, unordered single-state trait |
| `../assets/files/bdnn-trait-onehot-multistate-EXCERPT.txt` | derived from EN 152-156 | one-hot geography, taxon allowed in both areas (`Agriotherium 1 1`) |
| `../assets/files/bdnn-trait-ordered-centered-EXCERPT.txt` | derived from EN 161-168 | integer-coded ordered trait centered on zero |
| `../assets/files/bdnn-Backscale-ordered-only-EXCERPT.txt` | derived from EN 172-175 | `-plotBDNN_transf_features` column for an ordered trait, reproduced exactly as printed: 2 then 1. The fixture carries the page's numbers, not a verdict on them — EN 159 names 1.5 as the median while EN 174 prints 2 in the row EN 159 says holds the median (see the Backscale section) |
| `../assets/files/bdnn-Backscale-EXCERPT.txt` | derived from EN 192-195 | mean row then SD row, two predictor columns |
| `../assets/files/bdnn-BDNNtimevar-ztransformed-EXCERPT.txt` | derived from EN 180-188 | `-BDNNtimevar`: `Time` first, then z-transformed series |
| `../assets/files/bdnn-BDNNtimevar-binned-EXCERPT.txt` | derived from EN 214-218 | pre-binned series; the doc prints prose placeholders, not values |
| `../assets/files/bdnn-Time_windows.txt` | derived from EN 240-245 | `-fixShift` custom NN bins: no header, ages 0.0117 / 0.126 / 0.781 / 1.8 |
| `../assets/files/bdnn-cv_rate_variation-EXCERPT.txt` | derived from EN 98-101 | `_coefficient_of_rate_variation.csv` shape with the Carnivora numbers |
| `../assets/files/bdnn-predictor_influence-EXCERPT.txt` | derived from EN 106-111 | `_sp/_ex_predictor_influence.csv` columns `feature1` to `rank` |
| `../assets/files/bdnn-pdp-EXCERPT.txt` | derived from EN 322-325 (CN 323-326), doc's own defect kept | `*_pdp.csv` columns; the first data row has 7 fields under 6 headers in EN and CN alike |
