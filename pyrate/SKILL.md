---
name: pyrate
description: "PyRate suite router: Bayesian macroevolutionary rate estimation from fossil occurrences. What it estimates: speciation, extinction, dispersal, preservation rates, Covar trait correlations, time-continuous correlates, diversity dependence. Programs: PyRate.py, PyRateContinuous.py (-ginput -DD -c -m), PyRateMCDD.py, PyRateDES.py (-fossil -recent -bin_size), BDNN via PyRate.py (-BDNNmodel -plotBDNN), pyrate_lib beside the program, R pyrate_utilities.r (extract.ages, extract.ages.pbdb, fit.prior). Three steps: occurrence table Species/Status/MinT/MaxT/Trait -> *_PyRate.py -> -A 0/1/2/4 -n -s -p -b -j -d -out -singleton -mHPP -mG -qShift -ncat -fixSE -mCov -trait_file -> -plot -plot2 -tag -root_plot -mProb -BF on *_mcmc.log, *_marginal_rates.log, *_sum.txt. Failure modes: Python 2.6-2.7 vs 3.10+ doc conflict, missing pyrate_lib, argparse/numpy/scipy, Rscript for plots, commands missing from the wiki list (-A 4, -edgeShift, -min_dt, -fast_burnin), AGPLv3, pyrate.help@gmail.com; routes to 13 sibling skills."
---

# PyRate: what the suite covers, which program, which skill

## Overview

PyRate is, in Home's own words, "a Python program to estimate macroevolutionary rates from fossil
occurrence data using a Bayesian framework", inferring "speciation, extinction, and dispersal rates",
how they vary through time, and whether they correlate with traits "(e.g. body size)" or respond to
continuous variables "(e.g. climate proxies)" or competitive effects "(through diversity dependence)";
macroevolutionary rates are jointly estimated with preservation rates, "describing processes of
fossilization, sampling and identification of organisms" (`references/home.md` 17). The package holds
several programs, one per model family (`references/home.md` 22): `PyRate.py`, `PyRateContinuous.py`,
`PyRateMCDD.py`, `PyRateDES.py`, the `pyrate_lib` library and the R script `pyrate_utilities.r`
(`references/home.md` 28-61, 86). This skill is the router: it identifies the program a request needs
and hands the run to the sibling skill that owns the documentation for it.

The riskiest assumption this router removes: **the two "official" compatibility statements in this
corpus contradict each other, and the option catalogue most agents reach for is incomplete.** Home
says "Please note that Python 3.x is currently not supported" (`references/home.md` 69, tested with
"Python 2.6 – 2.7") while tutorial 0 says to make sure "Python (v.3.10 or higher)" is installed
(`../pyrate-installation/references/virtual-environment.md` 13) — and Home itself opens with "Please
refer to the TUTORIALS for updated documentation" (`references/home.md` 14), which is the corpus's own
tie-breaker. Separately, the wiki command list (`2.-PyRate:-command-list.md`) covers `PyRate.py` only
and contains **zero** occurrences of `-A 4`, `-edgeShift`, `-min_dt`, `-ginput`, `-DD`, `-fast_burnin`,
`-BDNNmodel`, `-plotBDNN`, `-fossil`, `-recent`, `-bin_size`, `-restore_mcmc` — all of which the
tutorials print. Never infer that a command does not exist because the command list omits it, and
never invent one because a sibling model seems to need it.

## Pre-run gate: three things this index must hand you before any command

| # | Check | Why it belongs here | Wording + citation |
| --- | --- | --- | --- |
| 1 | **Settle the interpreter before copying a single command: route to `pyrate-installation`, do not decide it from Home.** Home states "Please note that Python 3.x is currently not supported" and reports testing only "using Python 2.6 – 2.7"; the tutorial every run actually follows says to "make sure **Python (v.3.10 or higher)** is installed", builds the venv with `python -m venv desired_path_to_env/pyrate_env` and warns "you may have to type `python3`". Create/activate that environment first and run *every* command of this suite through its interpreter. | the two statements are mutually exclusive, and choosing wrong (e.g. a bare `python3 PyRate.py ...` on a checkout that only imports under 2.7, or a 2.7 venv against the tutorial's `pip` step) stops the task before step 1 of the analysis; which side a given checkout is on is an observation on the machine, not a citation — the corpus never demonstrates a concrete failure (see the 'The 10 things that break a run' table, item 1) | `references/home.md` 69; `../pyrate-installation/references/virtual-environment.md` 13, 19, 26; tie-break `references/home.md` 14 |
| 2 | **Two executable checkers ship in this suite — name them with their skill folder, never bare.** Each checker lives *inside* a skill directory, so both the document anchors and the command lines below are resolved from this file's directory (the `..`-prefix form): run from `pyrate/`, `python3 ../pyrate-command-reference/scripts/check_env.py` probes a python2 *and* a python3 candidate, the importability of numpy/scipy/argparse on each usable interpreter, `Rscript` on `PATH`, the four PyRate program files and an adjacent `pyrate_lib` (`../pyrate-command-reference/scripts/check_env.py:36-41`; options `--pyrate-dir PATH`, `--json`, `--self-test`, `--timeout`, `--python2`, `--python3`, `:32-33`). `python3 ../pyrate-command-reference/scripts/build_command.py Ursidae_PyRate.py -A 2 -mG -j 1` assembles and validates one whole `python PyRate.py <input> [commands]` line — the flags, the arity taken from the mirror's own documented usage lines, and the mirror's conditional-combination rules such as `-ncat`: "This command is used only when running under a Gamma model of preservation (i.e. with `-mG`)" — against the command list parsed at runtime from that mirror (`../pyrate-command-reference/references/command-list.md` 100-102; `../pyrate-command-reference/scripts/build_command.py:3-14, 37-40, 43-49`; also `--list`, `--self-test`, `--core-only`, `--dry-run`, `--program`). | suite code, not documentation. The paths above are skill-folder paths, resolved from this file's own directory; the suite-root spelling (skill name first, no leading `..`) works only inside this repository checkout and dangles once the skills are installed side by side. No input checker ships under `pyrate-command-reference` — that one is `../pyrate-input-file/scripts/validate_input.py` — and the audit gates, the only scripts sitting at the suite root itself, are a third location again: none of them is named `validate_input.py`. `ls */scripts/` before naming any path. The rules `check_env.py` enforces come from the mirrors cited in the next column | rules it probes: `references/home.md` 61 (`pyrate_lib` adjacency), 69 (argparse, Python 2.6 – 2.7), 71 (numpy/scipy, multiprocessing/`-thread`); `../pyrate-installation/references/virtual-environment.md` 13 (the interpreter conflict it reports instead of resolving); grammar source `../pyrate-command-reference/references/command-list.md` 9-268 |
| 3 | **Nothing is parallel by default — `-thread` is the first switch to move on a big dataset**, whose documented default is "`-thread 0 0` (default; sequential likelihood calculation)". For very large runs the tutorials pull a different lever: "an approximate Gibbs sampler can be used to sample more efficiently the times of origination and extinction", i.e. `-se_gibbs` plus retuned update frequencies (`../pyrate-rjmcmc/references/tutorial-3.md` 112-115, example call at 115) | `-thread` sets the thread count for the birth-death and the NHPP likelihoods *respectively*; at 0/0 PyRate "will not use the multiprocessing python library", and Home makes the parallel path platform-conditional: "Under UNIX systems, PyRate will use the library multiprocessing and thread (if available)". The `-se_gibbs` route is gated: "This model only works for preservation models based on homogenous or time-variable Poisson processes (HPP or TPP)" | `../pyrate-command-reference/references/command-list.md` 76-78; `references/home.md` 71; `../pyrate-rjmcmc/references/tutorial-3.md` 113, 115, 122 |

## The programs in the package

| Program | Model it implements (Home's wording) | Home line | Reference literature Home prints | Command list status |
| --- | --- | --- | --- | --- |
| `PyRate.py` | main functions for speciation/extinction through time plus preservation; also "trait dependent speciation and extinction" (Covar models) | 28-29 | Silvestro et al. 2014 *Systematic Biology* 63:349-367 (line 33); Silvestro, Salamin & Schnitzler 2014 *Methods in Ecology and Evolution* 5:1126-1131 (line 35) | the only complete list: 8 option groups, `../pyrate-command-reference/references/command-list.md` 9-268 — yet it still omits PyRate.py commands the tutorials print (`-A 4`, `-edgeShift`, `-min_dt`, `-restore_mcmc`) |
| `PyRateContinuous.py` (requires `pyrate_lib`, line 39) | birth-death with rates varying "through time through linear or exponential correlations with a time continuous variable" | 39-40 | Silvestro et al. 2015 *PNAS* 112:8684-8689 (line 42) | "A detailed command list is in preparation" (line 40, linked) — but six commands are documented in `../pyrate-continuous-covariates/references/pyratecontinuous.md` 13-38 |
| `PyRateMCDD.py` (requires `pyrate_lib`, line 46) | Multiple Clade Diversity Dependence: rates "may change through time as the result of diversity dependence effects within and between clades" | 46-47 | Silvestro et al. 2015 *PNAS* 112:8684-8689 (line 49) | "A detailed command list is in preparation." (line 47, no link) + "Wiki page for PyRateMCDD is under construction" (`../pyrate-command-reference/references/command-list.md` 18) |
| `PyRateDES.py` (requires `pyrate_lib`, line 53) | Dispersal Extinction Sampling: "uses fossil occurrences in two discrete areas to estimate rates of dispersal between areas and rates of local extinction within areas, while incorporating sampling biases" | 53-54 | Silvestro et al. 2016 *Phil Trans Roy Soc B*, doi 10.1098/rstb.2015.0225 (line 56) | "A detailed command list is in preparation." (line 54); Home names the helper script `DES_input_preparation.R` (line 54). Note Home's line 54 mislabels the citation lead-in as "The MCDD model is described here" — the paper below it is the DES paper |
| BDNN (no separate executable is named anywhere in this corpus) | birth-death neural network modulating rates by time, "categorical and/or continuous traits", "time-dependent variables" and "phylogenetic relatedness" (wording from `../pyrate-bdnn/references/tutorial-bdnn.md` 29-34, not Home) | not on Home | not on Home (Home's program list, lines 28-61, has no BDNN entry; the corpus prints no page dates) | run through `PyRate.py` with `-BDNNmodel 1` (`../pyrate-bdnn/references/tutorial-bdnn.md` 223, 55) |
| `pyrate_lib` | library used by several programs; "does not require any installation" | 60-61 | — | rule: "the folder pyrate_lib needs to be in the same directory as the program" (line 61) |
| `pyrate_utilities.r` | R utilities; Home names only `fit.prior` — `extract.ages` is documented in `../pyrate-input-file/references/preparing-input-file.md` 26-52 and `extract.ages.pbdb` in `../pyrate-input-file/references/tutorial-1.md` 37 | 86 | — | "The R script pyrate_utilities.r was tested under R version 2.x and 3.x. The function fit.prior requires the package fitdistrplus." (line 86) |

Invocation, both forms Home prints (`references/home.md` 75-80):

```
./PyRate.py path_to_input_file/file_name.py [commands]
python PyRate.py path_to_input_file/file_name.py [commands]
```

## The standard three-step analysis and who owns each step

Home: "A standard PyRate analysis requires three steps" (`references/home.md` 30).

| Step | What the docs say | Owning skill | Anchor |
| --- | --- | --- | --- |
| 1. Prepare an input file | occurrence table -> `*_PyRate.py` (or a `-d` origin/extinction table) | `pyrate-input-file` | `../pyrate-input-file/references/preparing-input-file.md` 14 (column rules), 28 (`source(...)`), 52 (`extract.ages(...)`), 54 (writes `Ursidae_PyRate.py`) |
| 2. Launch with input file + analysis settings | every setting is optional except the input file: "PyRate includes default settings for all parameters except for the input file." | `pyrate-bd-analysis` (the run), `pyrate-command-reference` (the options), `pyrate-preservation-models` (`-mHPP`/`-mG`/`-qShift`) | `../pyrate-bd-analysis/references/tutorial-1.md` 176; `../pyrate-command-reference/references/command-list.md` 45-83 |
| 3. Summarise and plot rates through time | three output files, then `-plot`/`-plot2`/`-tag`/`-mProb`/`-BF` — with one prerequisite to check first: under RJMCMC `*_marginal_rates.log` exists only if `-log_marginal_rates 1` was passed **at run time** | `pyrate-summarize-results` | `../pyrate-summarize-results/references/summarize-results.md` 12-13, 33-69; RJMCMC output set and the opt-in flag: `../pyrate-rjmcmc/references/tutorial-3.md` 51, 59-60 |

## Routing table (all 13 sibling skills)

| User goal | Skill folder | The file:line that answers it |
| --- | --- | --- |
| install PyRate, virtual environment, `Module FastPyRateC was not found`, check the install | `pyrate-installation` | `../pyrate-installation/references/virtual-environment.md` 13 (Python v.3.10 or higher), 19/24 (venv), 31/36 (activate), 42-44 (pip + requirements.txt), 49 (`PyRate.py -v`), 52 (fastPyRateC optional), 54-55 (Windows PATH, `-plot`/Rscript); Home's (undated) statements: `references/home.md` 69-71 |
| build or repair an occurrence input file; which columns are mandatory; typos in species names | `pyrate-input-file` | `../pyrate-input-file/references/preparing-input-file.md` 14 (`Species Status MinT MaxT [Trait]`, tab-delimited, no missing values); `../pyrate-input-file/references/tutorial-1.md` 25 (option 1, PBDB), 48 (option 2), 70 (age dependence / same-site occurrences), 92 (spelling check) |
| What does command `-x` do? / full option catalogue of `PyRate.py` | `pyrate-command-reference` | `../pyrate-command-reference/references/command-list.md` 9 (input/working dir), 22 (`-wd`), 27 (`-j`), 32 (`-out`), 37 (`-singleton`), 45 (main settings), 85 (preservation), 110 (constrained shifts), 129 (Covar), 161 (hyperpriors), 192 (advanced MCMC), 230 (tuning) |
| choose/parameterise the preservation (fossilization) model | `pyrate-preservation-models` | `../pyrate-preservation-models/references/command-list.md` 87 (`-mHPP`), 91 (`-qShift`), 95 (`-mG`), 100 (`-ncat`), 104 (`-fixSE`); walkthrough `../pyrate-preservation-models/references/tutorial-1.md` 121, 153 (model testing across preservation models), 238 (plot preservation rates) |
| first speciation/extinction-through-time analysis, defaults, output files, fixed time bins | `pyrate-bd-analysis` | `../pyrate-bd-analysis/references/tutorial-1.md` 119, 160 (analysis setup), 191-202 (`sum.txt`, `mcmc.log`, `marginal_rates.log`), 204, 224 (combine replicates), 247 (fixed bins), 263 (edge shifts) |
| rate shifts by RJMCMC, large datasets, constrained origination/extinction times | `pyrate-rjmcmc` | `../pyrate-rjmcmc/references/tutorial-3.md` 27, 32 (`-A 4`), 50 (outputs), 62 (model probabilities), 70 (RTT + rate-shift plots), 96 (combine replicates), 112 (large datasets), 126 (constraints) |
| summarise, plot, model probabilities, Bayes factors, range-through diversity | `pyrate-summarize-results` | `../pyrate-summarize-results/references/summarize-results.md` 9 (`-data_info`), 12-13 (three output files), 15/18/22/29 (each file), 33 (Plot/summarize), 39 (`-plot`), 45 (`-plot2`), 53 (`-tag`), 58 (`-root_plot`), 63 (`-mProb`), 67 (`-BF`); `../pyrate-summarize-results/references/tutorial-2.md` 22 (extract origination/extinction times), 65 (range-through/LTT plot) |
| rates as a function of a continuous variable; `-DD`, `-ginput`, `-c`, `-m` | `pyrate-continuous-covariates` | `../pyrate-continuous-covariates/references/pyratecontinuous.md` 9 (input = origin/extinction table), 13 (`-ginput`), 21 (setup), 28 (`-DD`), 31 (`-c`), 34 (`-m -1/0/1`); `../pyrate-continuous-covariates/references/tutorial-2.md` 94, 99, 127, 145 (Thermodynamic Integration) |
| multiple-clade diversity dependence (MCDD) **and** the multivariate birth-death model (MBD, `PyRateMBD.py`) | `pyrate-diversity-dependence` | `../pyrate-diversity-dependence/references/tutorial-4.md` 23 (MCDD), 24 ("implemented in the program `PyRateMCDD.py` and requires a single input file", 4 columns — or more with replicates — tab-separated, one row per species), 34/38 (example calls); MBD: 44 (heading), 53 (`PyRateMBD.py`), 68 (example call), 71 (`-var`), 73-74 (MBD run on clade diversity trajectories), 76 (additional options), 87 (`-plot`) |
| trait-correlated (Covar), age-dependent extinction (ADE), Birth-Death Chronospecies (BDC) — **not MBD**, which is routed above | `pyrate-trait-age-models` | `../pyrate-trait-age-models/references/command-list.md` 129, 132 (`-trait_file`), 137 (`-mCov` 1-5 at 140-144), 146 (`-trait`), 150 (`-logT`); `../pyrate-trait-age-models/references/tutorial-4.md` 98 (Covar), 102, 111, 131 (ADE), 152 (BDC). That skill disclaims MBD itself: its Related-skills entry sends `PyRateMBD.py`, `-hsp` and `-var` to `pyrate-diversity-dependence` and places them outside that skill's models (`../pyrate-trait-age-models/SKILL.md` 184) |
| dispersal between two areas, local extinction, sampling (`PyRateDES.py`) | `pyrate-des` | `../pyrate-des/references/des-model.md` 10-17 (the `DESin` function and `bin.size`), 24/33 (the R calls `DESin(...)` and `write.DES.in(...)`); `../pyrate-des/references/tutorial-5.md` 21 (input prep), 27, 100, 147, 173 (running), 177, 211, 221, 236, 272, 289 (model variants), 334 (summarize/plot), 63/143/186 (`PyRateDES.py` calls) |
| BDNN: neural-network rates, effect plots, predictor importance | `pyrate-bdnn` | `../pyrate-bdnn/references/tutorial-bdnn.md` 27 (model), 43 (quick example), 55 (run), 119 (dataset), 126 (z-transform predictors), 222 (running), 255 (postprocessing), 279 (partial dependence), 340 (predictor importance), 431 (restart), 440 (replicates), 465-482 (fixed origination/extinction times) |
| MCMC not converging, burnin, proposal tuning | `pyrate-mcmc-tuning` | `../pyrate-mcmc-tuning/references/tutorial-6.md` 12 (Fast burnin), 13-14 (`-fast_burnin <int>`, default 0), 17 (Tuning parameters), 18 (`-multiR`), 21 (`-tT`), 25 (`-nT`), 29 (`-tQ`), 33 (`-tR`), 37 (`-tS`), 41 (`-fS`), 45 (`-tC`), 49 (`-fU`), 53 (`-fR`); the `-multiR`/`-t*`/`-f*` blocks also stand in `../pyrate-mcmc-tuning/references/command-list.md` 230-268, but `-fast_burnin` has 0 hits there |

## Tutorials index -> skill map (all 26 bullets)

Every bullet of `references/tutorials-index.md` (7 `###` sections, lines 15-61; CN twin
`references/tutorials-index-cn.md` 16-62) routes as follows. The CN mirror has the same 26 bullets and
the same target anchors.

| Index line | Bullet (abbreviated) | Skill | Target |
| --- | --- | --- | --- |
| 17 | Install PyRate in a virtual environment | `pyrate-installation` | `../pyrate-installation/references/virtual-environment.md` 9 |
| 23 | Generate PyRate input file (option 1) | `pyrate-input-file` | `../pyrate-input-file/references/tutorial-1.md` 25 |
| 24 | Generate PyRate input file (option 2) | `pyrate-input-file` | `../pyrate-input-file/references/tutorial-1.md` 48 |
| 25 | Check species list for spelling/typos | `pyrate-input-file` | `../pyrate-input-file/references/tutorial-1.md` 92 |
| 29 | Setting up a preservation model | `pyrate-preservation-models` | `../pyrate-preservation-models/references/tutorial-1.md` 121 |
| 30 | Birth-death with rate shifts using RJMCMC "(recommended algorithm)" | `pyrate-rjmcmc` | `../pyrate-rjmcmc/references/tutorial-3.md` 27 |
| 31 | Birth-death with rate shifts using BDMCMC | `pyrate-bd-analysis` | `../pyrate-bd-analysis/references/tutorial-1.md` 119 |
| 32 | Birth-death with fixed time bins | `pyrate-bd-analysis` | `../pyrate-bd-analysis/references/tutorial-1.md` 247 |
| 33 | Running PyRate on large datasets | `pyrate-rjmcmc` | `../pyrate-rjmcmc/references/tutorial-3.md` 112 |
| 34 | Constraining origination and extinction times | `pyrate-rjmcmc` | `../pyrate-rjmcmc/references/tutorial-3.md` 126 |
| 38 | Plotting marginal rates (RJMCMC) | `pyrate-rjmcmc` | `../pyrate-rjmcmc/references/tutorial-3.md` 70 |
| 39 | Plotting and summarizing BDMCMC output | `pyrate-summarize-results` (commands) / `pyrate-bd-analysis` (walkthrough) | `../pyrate-summarize-results/references/summarize-results.md` 33 / `../pyrate-bd-analysis/references/tutorial-1.md` 204 |
| 40 | Plotting preservation rates through time | `pyrate-preservation-models` | `../pyrate-preservation-models/references/tutorial-1.md` 238 |
| 41 | Plotting range-through diversity trajectories | `pyrate-summarize-results` | `../pyrate-summarize-results/references/tutorial-2.md` 65 |
| 45 | Generating input file for PyRateContinuous | `pyrate-continuous-covariates` | `../pyrate-continuous-covariates/references/tutorial-2.md` 94; `../pyrate-continuous-covariates/references/pyratecontinuous.md` 13 |
| 46 | Diversity dependent birth-death models | `pyrate-continuous-covariates` | `../pyrate-continuous-covariates/references/tutorial-2.md` 99 (`-DD`, `../pyrate-continuous-covariates/references/pyratecontinuous.md` 28) |
| 47 | Correlation with a time-continuous variable | `pyrate-continuous-covariates` | `../pyrate-continuous-covariates/references/tutorial-2.md` 127 |
| 48 | Model testing using marginal likelihoods | `pyrate-continuous-covariates` | `../pyrate-continuous-covariates/references/tutorial-2.md` 145; command `-A 1` in `../pyrate-command-reference/references/command-list.md` 49 |
| 49 | Multiple-clade diversity dependent model | `pyrate-diversity-dependence` | `../pyrate-diversity-dependence/references/tutorial-4.md` 23 |
| 50 | Multivariate birth-death model (MBD) | `pyrate-diversity-dependence` | `../pyrate-diversity-dependence/references/tutorial-4.md` 44 |
| 53 | Trait dependent birth-death models | `pyrate-trait-age-models` | `../pyrate-trait-age-models/references/tutorial-4.md` 98; `../pyrate-trait-age-models/references/command-list.md` 129 |
| 54 | Age dependent extinction model | `pyrate-trait-age-models` | `../pyrate-trait-age-models/references/tutorial-4.md` 131 |
| 55 | Birth-death Chronospecies model | `pyrate-trait-age-models` | `../pyrate-trait-age-models/references/tutorial-4.md` 152 |
| 56 | Birth-death neural network (BDNN) | `pyrate-bdnn` | `../pyrate-bdnn/references/tutorial-bdnn.md` 27 |
| 60 | Preparing input data for DES analysis | `pyrate-des` | `../pyrate-des/references/tutorial-5.md` 21 |
| 61 | Running a DES analysis | `pyrate-des` | `../pyrate-des/references/tutorial-5.md` 173 |

**Two routes the index does not carry** (the router supplies them, from Home): `pyrate_tutorial_6.md`
(MCMC tuning / advanced settings) has **no bullet** in the index -> `pyrate-mcmc-tuning`; and the five
wiki pages (`1.-Preparing-input-file`, `2.-PyRate:-command-list`, `3.-Summarize-PyRate-results`,
`4.-PyRateContinuous`, `5.-Dispersal-Extinction-Sampling-model`) are reachable only from Home
(links at `references/home.md` 29, 30, 40, 54, and 84 for the summarize page), not from the index.

**One index anchor is dead, upstream (corpus defect — recorded, not patched).** The ADE bullet at
`references/tutorials-index.md` 54 points at `pyrate_tutorial_4.md#age-dependent-extinction-ade-model`
(singular `model`), but the section heading it must reach is `# Age dependent extinction (ADE) models`
(`../pyrate-diversity-dependence/references/tutorial-4.md` 131), whose GitHub anchor ends `-ade-models`
(plural) — the form tutorial 4's own Contents bullet does use (`../pyrate-diversity-dependence/references/tutorial-4.md` 18).
The CN twin carries the same singular anchor (`references/tutorials-index-cn.md` 55), so this is upstream and
not a translation slip. Both files here are verbatim mirrors, so neither side is edited in this suite: fix the
link in `dsilvestro/PyRate/tutorials/README.md`, and route from the heading line (131) rather than the index
anchor. The MBD bullet at `references/tutorials-index.md` 50 was checked the same way and does match its heading
(`../pyrate-diversity-dependence/references/tutorial-4.md` 44).

## The 10 things that break a run

| # | What happens | Consequence | Wording + citation |
| --- | --- | --- | --- |
| 1 | You trust Home's "Python 3.x is currently not supported" | you install a 2.7 interpreter the tutorials no longer use (or vice versa); the corpus records the contradiction but never demonstrates a concrete failure symptom — treat any import/syntax-break claim as inference | `references/home.md` 69 vs `../pyrate-installation/references/virtual-environment.md` 13; tie-break `references/home.md` 14 ("for updated documentation") |
| 2 | You run the wrong program for the model | `PyRateContinuous.py` "does not model preservation and assumes that the times of origination and extinction of each lineage are known"; `PyRate.py` is the one that estimates them ("typically in a previous PyRate analysis") | `../pyrate-continuous-covariates/references/tutorial-2.md` 95; `references/home.md` 29, 40 |
| 3 | `pyrate_lib` is not beside the program | every program whose Home heading carries the pyrate_lib requirement tag (`references/home.md` 39, 46, 53) loses the functions it imports | "the folder pyrate_lib needs to be in the same directory as the program" (`references/home.md` 61) |
| 4 | Blank/NAs in the four occurrence columns | the input file is invalid; only the optional Trait column may be missing | "At present, PyRate can not deal with missing information in these four columns, so make sure that you remove these entries beforehand." (`../pyrate-input-file/references/preparing-input-file.md` 14) |
| 5 | You conclude an option does not exist because the wiki command list omits it, or invent one for a program whose list is 'in preparation' | silently wrong model, or a command line that never existed | `references/home.md` 40, 47, 54 ("A detailed command list is in preparation"); `../pyrate-command-reference/references/command-list.md` 18 ("Wiki page for PyRateMCDD is under construction"); `-A 4`, `-edgeShift`, `-ginput`, `-DD`, `-BDNNmodel`, `-fossil` have 0 hits in that command list |
| 6 | `-d` (origin/extinction table) is treated as just another input switch | it "automatically sets `-fixSE = null`", and "the estimation of preservation rates and times of speciation/extinction are switched off" | `../pyrate-command-reference/references/command-list.md` 18 |
| 7 | You leave the default algorithm while the tutorials recommend another | `-A 2` (BDMCMC) is the documented default; the index labels RJMCMC "(recommended algorithm)" and tutorial 3 uses `-A 4`; a `-A 2` run is not the recommended analysis | `../pyrate-command-reference/references/command-list.md` 52; `references/tutorials-index.md` 30; `../pyrate-rjmcmc/references/tutorial-3.md` 32 |
| 8 | `-b` stays at 0 while estimating marginal likelihoods by TI | marginal likelihoods (`-A 1`, feeding `-BF`) computed from unbuilt/undisciplined chains | `../pyrate-command-reference/references/command-list.md` 69 ("Must be set to a reasonable number when estimating marginal likelihood through TI"), 71 (`-b 0` default) |
| 9 | Several runs share one output directory | files are overwritten; `-out` exists precisely for this | `../pyrate-command-reference/references/command-list.md` 33 |
| 10 | `-plot` runs without R reachable, or you match the docs' shell-command spelling literally | no graphic output; Home prints `RScript`, tutorial 5 prints `Rscript` | `references/home.md` 84; `../pyrate-des/references/tutorial-5.md` 95 ("This requires that R is installed on your PC to execute the shell command Rscript"), 354 |

Honourable mentions: `-A 3` carries "Warning: this function is currently still being tested."
(`../pyrate-command-reference/references/command-list.md` 54); `argparse` must be installed by hand
under Python 2.6 (`references/home.md` 69); `numpy`/`scipy` are required (`references/home.md` 71);
if `Module FastPyRateC was not found.` appears "the program will still run but use a slower
implementation for some of the functions" (`../pyrate-installation/references/virtual-environment.md` 52).

## Compatibility and installation headline facts

Tested "under Unix operating systems (Mac OS 10.6 or higher and Cent OS 6) and under Windows (XP and
7) using Python 2.6 – 2.7", with "Python 3.x is currently not supported" bolded on Home
(`references/home.md` 69); `numpy` and `scipy` required, installable via `pip install -r
requirements.txt`; on UNIX PyRate "will use the library multiprocessing and thread (if available) and
implement parallel computation of the likelihoods (see command -thread)" (`references/home.md` 71);
Windows needs `python.exe` on `PATH` (`references/home.md` 82) and `Rscript.exe` on `PATH` for `-plot`
(`references/home.md` 84); `pyrate_utilities.r` tested under R 2.x and 3.x, and `fit.prior` needs
`fitdistrplus` (`references/home.md` 86). All of this is the *wiki's* statement; the actual install
procedure an agent should follow is owned by `pyrate-installation` and says Python 3.10+
(`../pyrate-installation/references/virtual-environment.md` 13).

## Literature, licence, support

- `PyRate.py`: Silvestro et al. 2014 *Systematic Biology* 63:349-367 (`references/home.md` 33) and
  Silvestro, Salamin & Schnitzler 2014 *MEE* 5:1126-1131 (`references/home.md` 35).
- `PyRateContinuous.py` and `PyRateMCDD.py`: Silvestro et al. 2015 *PNAS* 112:8684-8689
  (`references/home.md` 42 and 49 — the same paper for both).
- `PyRateDES.py`: Silvestro et al. 2016 *Phil Trans Roy Soc B*, doi: 10.1098/rstb.2015.0225
  (`references/home.md` 56), introduced by a line that mislabels it "The MCDD model is described here"
  (`references/home.md` 54).
- Licence: Home states PyRate is licensed under what it links as "AGPLv3 License" (`references/home.md` 24).
- Support: "For questions, suggestions or bugs" one should "contact us" at `pyrate.help@gmail.com`
  (`references/home.md` 19). Home defers documentation currency to the tutorials
  (`references/home.md` 14) and points at the tutorial set again at `references/home.md` 22.

## EN vs CN: where the twins differ, and where they agree on an error

- `references/home.md` 31 reads "The main methods implemented in and the program are described here:"
  — a broken relative clause. `references/home-cn.md` 32 ("该程序所实现的主要方法描述见于下列文献：")
  reads as a clean statement that the main methods implemented in the program are described in the two papers below; use the CN reading, the EN is garbled.
- `references/home.md` 54 attaches "The MCDD model is described here" to the **DES** paper;
  `references/home-cn.md` 55 repeats it verbatim ("MCDD 模型描述见于"), so this is an upstream error,
  not a translation slip. The paper at line 56 is the DES paper.
- The Python 3.x prohibition is identical in both languages (`references/home.md` 69 =
  `references/home-cn.md` 70), as is "Python（v.3.10 或更高版本）"
  (`../pyrate-installation/references/virtual-environment-cn.md` 14) — the contradiction lives in the
  corpus itself, not in the translation.
- The "(recommended algorithm)" label on RJMCMC is present in both index twins
  (`references/tutorials-index.md` 30 = `references/tutorials-index-cn.md` 31 推荐算法) but appears
  nowhere in `../pyrate-rjmcmc/references/tutorial-3.md`, which only says "We have recently implemented
  a new algorithm in PyRate that uses RJMCMC (Green 1995) instead of BDMCMC" (line 30, which also
  contains the typo "The method is is described").
- "in preparation" is a *link* only for `PyRateContinuous.py` (`references/home.md` 40) and plain text
  for MCDD (47) and DES (54); CN mirrors this asymmetry exactly (`references/home-cn.md` 41, 48, 55).
- Script casing is unstable across pages: `pyrate_utilities.r` (`references/home.md` 86,
  `../pyrate-input-file/references/preparing-input-file.md` 9, 28) vs `pyrate_utilities.R`
  (`../pyrate-command-reference/references/command-list.md` 13, 28). Unix file names are
  case-sensitive; resolve against the checkout you have rather than either doc.

## Worked example

Route a request end to end. Every line below is copied from a mirror (path shown); no fixture is used
because this skill owns none.

```sh
cd pyrate        # this skill directory, addressed from the suite root wherever it is installed

# 1. Which program does the model need? Home is the authority for the four executables:
grep -n '^#### ' references/home.md                       # -> lines 28, 39, 46, 53, 60

# 2. Interpreter check (Home vs tutorial 0 disagree; Home defers to the tutorials):
grep -n "not supported" references/home.md                # home.md:69
grep -n "v.3.10" ../pyrate-installation/references/virtual-environment.md   # :13

# 3. From your PyRate checkout, confirm the library rule (home.md:61) and smoke-test the install
#    exactly as tutorial 0 prints it (../pyrate-installation/references/virtual-environment.md:49):
ls PyRate.py PyRateContinuous.py PyRateMCDD.py PyRateDES.py pyrate_lib
python your_path/PyRate-master/PyRate.py -v
#    (or run the suite's own probe if it is present: bash ../assets/files/venv-preflight.sh /path/to/PyRate)

# 4. Step 1 of the analysis - build the input file (../pyrate-input-file/references/preparing-input-file.md:28, 52), in an R console:
#      > source(file = "/path_to_file/pyrate_utilities.r")
#      > extract.ages(file = "/path_to_file/Ursidae.txt", replicates=10, cutoff=5, random=TRUE)
#    -> writes Ursidae_PyRate.py (../pyrate-input-file/references/preparing-input-file.md:54)

# 5. Step 2 - launch (../pyrate-bd-analysis/references/command-list.md:15; add -j to pick a replicate, -out to avoid overwriting):
python PyRate.py path_to_input_file/Ursidae_PyRate.py

# 6. Step 3 - summarise (../pyrate-bd-analysis/references/tutorial-1.md:218; -tag/-root_plot/-mProb/-BF: ../pyrate-summarize-results/references/summarize-results.md:53-67):
python PyRate.py -plot .../Canis_pbdb_data_marginal_rates.log -b 200
```

## Pitfalls

- Do not treat `PyRateDES.py`'s, `PyRateMCDD.py`'s or `PyRateContinuous.py`'s commands as a superset of
  `PyRate.py`'s: `-A` exists in both `PyRate.py` and `PyRateContinuous.py`
  (`../pyrate-command-reference/references/command-list.md` 46;
  `../pyrate-continuous-covariates/references/pyratecontinuous.md` 25) but `-d` also means different
  things in the two lists (`../pyrate-command-reference/references/command-list.md` 17 = origin/extinction table;
  `../pyrate-continuous-covariates/references/pyratecontinuous.md` 22 =
  the same kind of file), and `PyRateMCDD.py` takes no occurrence file at all
  (`../pyrate-diversity-dependence/references/tutorial-4.md` 24).
- Home's program list has no BDNN entry, so the claim that BDNN ships with PyRate must be sourced from the tutorials
  (`../pyrate-bdnn/references/tutorial-bdnn.md` 27, 223), not from Home. The corpus never names a
  `PyRateBDNN.py` executable — do not write one.
- BDNN changes the input contract: "continuous traits and time-series predictors should be z-transformed"
  (`../pyrate-bdnn/references/tutorial-bdnn.md` 126) — a raw body-mass column is a documented no-go.
- DES input is a *set of replicated* tables, not one file: "The DES model needs a set of replicated
  input files with the taxon occurrences classified into time-bins and areas"
  (`../pyrate-des/references/des-model.md` 11).
- For `-A 1`/TI runs the file `_marginal_rates.log` is replaced by `_marginal_likelihood.txt`
  (`../pyrate-summarize-results/references/summarize-results.md` 27, 29), so a plot script pointed at
  the usual name finds nothing.
- A plot/summarise route has a prerequisite only the *run* can satisfy: under RJMCMC `*_marginal_rates.log` is not a default product — "RJMCMC analyses by default produce 4 output files" (`../pyrate-rjmcmc/references/tutorial-3.md` 51),
  and the marginal-rates file is the optional old-format alternative obtained "using the command `-log_marginal_rates 1`" (`../pyrate-rjmcmc/references/tutorial-3.md` 59-60; the page's own enumeration is loose — heading 3 names two
  files, `sp_rates.log` and `ex_rates.log`, while heading 4 is this opt-in one). Pass it at step 2: no plot command can recover a file that was never written. The trade-off on the same line is that the opt-in file
  "can be processed using the command `-plot`" but "it cannot be analyzed using the command `plotRJ`" (`../pyrate-rjmcmc/references/tutorial-3.md` 60), whereas `-plotRJ` is documented for the default rate files
  ("This file can be analyzed using the command `-plotRJ`", `../pyrate-rjmcmc/references/tutorial-3.md` 57). `-log_marginal_rates` has exactly 1 hit across the English mirrors (line 60) and 0 in
  `../pyrate-command-reference/references/command-list.md` — a tutorial-only flag the command list cannot confirm, so absence from that list proves nothing (item 5 of 'The 10 things that break a run').
- When several replicates exist, the replicate is chosen by `-j` (`../pyrate-command-reference/references/command-list.md` 27) — and for
  `-d` inputs too (`../pyrate-command-reference/references/command-list.md` 18). ESS must be computed per replicate, not from a combined log
  (`../pyrate-bd-analysis/references/tutorial-1.md` 206).

## Not documented in this wiki

| Unanswered question | Why you must not fill it in |
| --- | --- |
| Which Python version each program requires (BDNN, DES, MCDD specifically) | the corpus states a version twice and contradictorily (`references/home.md` 69 vs `../pyrate-installation/references/virtual-environment.md` 13) and never per program; there is no evidence to generalise |
| What `python PyRate.py -v` prints, and whether `-v` still exists in the command set | only occurrence in the corpus is `../pyrate-installation/references/virtual-environment.md` 49; `-v` appears nowhere as a command in the wiki command list (its only substring hit, line 92, is the hyphen of "time-variable") |
| The full command sets of `PyRateContinuous.py`, `PyRateMCDD.py`, `PyRateDES.py` | Home: "A detailed command list is in preparation" (`references/home.md` 40, 47, 54); MCDD's wiki page is "under construction" (`../pyrate-command-reference/references/command-list.md` 18). Only the commands the tutorials print are evidenced |
| Whether `-plot` must be called with `PyRate.py` or with a dedicated program | `../pyrate-summarize-results/references/summarize-results.md` 42-43 gives bare `-plot path` examples; only `../pyrate-bd-analysis/references/tutorial-1.md` 218 shows the full `python PyRate.py -plot ...` form (233 prints a program-named `PyRate.py -plot ...` form without `python`); `PyRateDES.py` summarises with its own `-sum` call instead (`../pyrate-des/references/tutorial-5.md` 206) |
| Default value of `-p` (print frequency) and of `-thread` upper limit | `../pyrate-command-reference/references/command-list.md` 64-67 shows `Example: -p 1000` with **no** "(default)" marker, unlike `-n` (58), `-s` (62), `-b` (71); absence of a marker is not a default |
| Whether `-A 3` (Dirichlet Process) is safe for production | the only statement is "Warning: this function is currently still being tested." (`../pyrate-command-reference/references/command-list.md` 54) |
| Whether `fit.prior`, `extract.ages`, `extract.ages.pbdb` ship in one file or several | `references/home.md` 86 names `pyrate_utilities.r` and `fit.prior`; `../pyrate-input-file/references/preparing-input-file.md` 26-52 documents `extract.ages` only; `extract.ages.pbdb` is named only at `../pyrate-input-file/references/tutorial-1.md` 37-38, whose IMPORTANT NOTE documents `replicates` and `cutoff` in prose (and states the function "does not check for synonyms, typos, etc.") but prints no parameter table; line 40 names its two outputs (`*_SpeciesList.txt`, `*_PyRate.py`) without giving their layout |
| Which reference to cite for BDNN, MBD, ADE, BDC | Home's literature list (`references/home.md` 33-56) stops at 2016 and covers only four programs; `../pyrate-bdnn/references/tutorial-bdnn.md` 124 points at an example dataset from Hauffe et al. 2022 MEE, which is a data citation, not a model citation |
| Whether the `-singleton` exclusions change the reported number of species in `-data_info` output beyond "printed on screen" | `../pyrate-command-reference/references/command-list.md` 37-41 states the counts are printed and cross-references `-data_info`; no output layout is given |
| The exact status/validity of `PyRateBDNN` as a program name | the string `PyRateBDNN` occurs nowhere in this corpus (grep over all mirrors); BDNN is documented only as commands passed to `PyRate.py` |

## Related skills

- `pyrate-installation` — venv creation/activation, `requirements.txt`, `PyRate.py -v`, fastPyRateC, Windows `PATH`.
- `pyrate-input-file` — the occurrence table, `extract.ages`/`extract.ages.pbdb`, replicates/cutoff/random, species-name typo checking, same-site age dependence.
- `pyrate-command-reference` — the whole `PyRate.py` option catalogue in 8 groups with defaults and examples.
- `pyrate-preservation-models` — NHPP/HPP/TPP/Gamma choices, `-mHPP`, `-qShift`, `-mG`, `-ncat`, `-fixSE`, preservation-rate plots.
- `pyrate-bd-analysis` — the BDMCMC/`-A` analysis walkthrough, defaults, the three output files, fixed time bins, edge shifts.
- `pyrate-rjmcmc` — `-A 4` RJMCMC rate shifts, model-probability summaries, large datasets, constrained times.
- `pyrate-summarize-results` — output-file semantics, `-plot`/`-plot2`/`-tag`/`-root_plot`/`-mProb`/`-BF`, `-data_info`, range-through diversity plots.
- `pyrate-continuous-covariates` — `PyRateContinuous.py`: `-ginput`, `-DD`, `-c`, `-m`, single-clade diversity dependence, TI model testing.
- `pyrate-diversity-dependence` — `PyRateMCDD.py` multiple-clade diversity dependence and its 4-column input.
- `pyrate-trait-age-models` — Covar trait-correlated models (`-mCov`, `-trait_file`, `-trait`, `-logT`), ADE, BDC, MBD.
- `pyrate-des` — `PyRateDES.py`, `DES_input_preparation.R`, `-fossil`/`-recent`/`-bin_size`/`-plot_raw`, DES model variants.
- `pyrate-bdnn` — `-BDNNmodel`, `-plotBDNN`, partial-dependence effect plots, predictor importance, custom time bins.
- `pyrate-mcmc-tuning` — `-fast_burnin` and the `-multiR`/`-t*`/`-f*` proposal tuners.

## Resources

| File | What's in it | Load when |
| --- | --- | --- |
| `references/home.md` | The whole wiki Home page: PyRate's scope (line 17), the four programs with their pyrate_lib requirements and per-program literature (28-56), `pyrate_lib` directory rule (60-61), Compatibility and installation (68-86), AGPLv3 (24), contact (19), the three-step analysis (30) | Always first: it is the only page that states what PyRate is and which program implements which model |
| `references/home-cn.md` | Simplified-Chinese twin of Home (9-line frontmatter, so body lines are +1: scope 18, programs 29-57, library 62, compatibility 69-87) | Whenever an English sentence on Home is ambiguous — see "EN vs CN" for the two places where the CN settles or confirms an upstream error |
| `references/tutorials-index.md` | The tutorials README: 7 sections, 26 bullets, each linking to a `pyrate_tutorial_N.md#anchor` (17-61) | To decide which tutorial — and therefore which sibling skill — answers a request; the map above reproduces all 26 |
| `references/tutorials-index-cn.md` | Simplified-Chinese twin, same 26 bullets and same anchors (18-62) | To confirm a bullet's meaning (e.g. 推荐算法 at line 31) without guessing from the English title |

## grep recipes

```sh
# run these from this skill directory (all 8 patterns verified to match; recipe 7 verifies an absence)
grep -n "not supported\|in preparation\|under construction" references/home.md
grep -n "pyrate_lib" references/home.md
grep -n '^#### ' references/home.md
grep -n "recommended" references/tutorials-index.md
grep -n '^### ' references/tutorials-index.md
grep -c '^\* ' references/tutorials-index.md references/tutorials-index-cn.md
grep -rn "tutorial_6" references/ || echo "no hit - the index carries no bullet for tutorial 6"
grep -n "v.3.10" ../pyrate-installation/references/virtual-environment.md
```

## Runnable fixtures (`../assets/files/`)

This skill owns **no fixtures**: the coverage map assigns the `pyrate` router the prefix `—` (none),
because every example file in the corpus belongs to a page owned by a sibling. Nothing in the Worked
example above needs one. Fixtures you may want live next door, named with their owner's prefix —
`venv-` (pyrate-installation), `occ-` (pyrate-input-file), `cmdref-` (pyrate-command-reference),
`pres-` (pyrate-preservation-models), `bd-` (pyrate-bd-analysis), `rjmcmc-` (pyrate-rjmcmc), `sum-`
(pyrate-summarize-results), `cont-` (pyrate-continuous-covariates), `mcdd-`
(pyrate-diversity-dependence), `covar-` (pyrate-trait-age-models), `des-` (pyrate-des), `bdnn-`
(pyrate-bdnn), `tuning-` (pyrate-mcmc-tuning). This is suite convention, not documentation; list what
actually exists before citing a path. As of writing, `../assets/files/venv-preflight.sh` (owned by
`pyrate-installation`) probes precisely the headline requirements of this page — interpreter, numpy/scipy/argparse,
Rscript for `-plot`, `pyrate_lib` adjacency — and is the cheapest way to settle the Python conflict on a
real machine:

```sh
ls ../assets/files/                      # what is really there
ls ../assets/files/ | cut -d- -f1 | sort | uniq -c   # which owners have contributed
```
