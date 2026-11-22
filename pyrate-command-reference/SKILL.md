---
name: pyrate-command-reference
description: "All 50 PyRate.py options and the `<input file>` argument, verbatim from wiki page '2. PyRate: command list', with EN/CN lines, arity, value forms, documented defaults: -d origin/extinction table (auto-sets -fixSE null), -wd, -j, -out, -singleton 1/2/-1, -A 0/1/2/3 (fixed-shift MCMC, TI marginal likelihood, BDMCMC default, Dirichlet Process Prior), -n, -s, -p, -b (iterations or 0-1 fraction), -thread, -mHPP, -qShift file, -mG+-ncat, -fixSE, -mL, -mM, -mC, -fixShift epochs.txt, -trait_file, -mCov 1-5, -trait, -logT 0/1/2, -N -1, -pL, -pM, -pP, -pS, -pC, -cauchy, -r/-t/-sw MC3, -k/-a TI, -M/-B/-T/-S BDMCMC, -multiR, -tT, -nT, -tQ, -tR, -tS, -tC, -fU, -fS, -fR; NHPP vs HPP vs TPP vs Gamma preservation, interlocks, options ignored outside their -A mode, Python 2.7-only runtime, pyrate_lib scope (not stated for PyRate.py), -plot needing Rscript, stems *_sum.txt, *_mcmc.log, *_marginal_rates.log, *_marginal_likelihood.txt, -A 4 RJMCMC, EN-CN drift; scripts check_env/build_command(PyRate.py only)/parse_results.py."
---

# PyRate.py command reference - every option on the command-list page

## Overview

`PyRate.py` takes one positional argument (the `*_PyRate.py` occurrence file,
`references/command-list.md:12-15`) and then any number of the **50 option blocks** the page prints in
8 `###` sections (`references/command-list.md:9, 45, 85, 110, 129, 161, 192, 230`): input/working
directory, main analysis settings, preservation model, constrained shifts, Covar settings,
(hyper)priors, advanced (BD)MCMC, tuning. This skill is the index of those blocks: for each command the
master table below gives the EN and CN mirror line, the arity the page's own example line shows, the
value forms, and the documented default verbatim - or the words *not stated*, because the page prints a
`(default)` marker on 31 lines covering **30 options**, one more default (`-cauchy -1 -1`) exists only in
prose (`references/command-list.md:175`), and **18 of the 50 options have no default anywhere on the
page**. The deterministic front door is `scripts/`: `check_env.py` reports the runtime
the docs require and the documented defaults it can read back; `build_command.py` assembles a command
line for `PyRate.py` - the one grammar it carries, so `--program` refuses the other programs of the
family - and refuses combinations the page forbids (it never executes anything); `parse_results.py` reads
the output stems and says which analysis mode actually ran.

**Riskiest assumption, stated up front:** that omitting `-A` gives you BDMCMC. The page marks `-A 2` as "(default)"
(`references/command-list.md:52`), but the first tutorial says using
`-A 4` "(or omitting the flag) will set the algorithm to RJMCMC"
(`../pyrate-bd-analysis/references/tutorial-1.md:174`). This skill follows the command-list page (the
contract's authoritative source for commands) and flags the contradiction everywhere it matters;
`build_command.py` warns whenever `-A` is omitted rather than guessing.

## The 14 things that break a run

| # | what you do | consequence | the docs' words + citation |
| --- | --- | --- | --- |
| 1 | run under Python 3 | program does not start | "Python 3.x is currently not supported" `../pyrate-installation/references/home.md:69` - but the venv tutorial demands "Python (v.3.10 or higher)" `../pyrate-installation/references/virtual-environment.md:13` (unresolved corpus conflict) |
| 2 | run `PyRateContinuous.py` / `PyRateMCDD.py` / `PyRateDES.py` with the `pyrate_lib` folder not beside the program | the library is not where the page says it must be | "when you run a program requiring `pyrate_lib` (e.g. `PyRateContinuous`), the folder `pyrate_lib` needs to be in the same directory as the program" `../pyrate-installation/references/home.md:61`, which also calls it a library "used by several PyRate programs" (same line); the `[requires library pyrate_lib]` tag sits on those three headings only (`:39`, `:46`, `:53`) - **no page states the requirement for `PyRate.py`, and no page states what failing it prints** |
| 3 | omit `-A` | you may get RJMCMC, not the documented default | `references/command-list.md:52` vs `../pyrate-bd-analysis/references/tutorial-1.md:174` |
| 4 | pass `-r`, `-t`, `-sw`, `-k`, `-a`, `-M`, `-B`, `-T`, `-S` outside their mode | option silently unused | each block carries "This command is used only when running" plus the mode: `-r` "(i.e. with `-A 0`)" `references/command-list.md:194`, `-k` "(i.e. with `-A 1`)" `:206`, `-M` "(i.e. with `-A 2`)" `:214` |
| 5 | switch to `-d` | preservation and SE-time estimation are switched off, results are conditional on your ages | "This option automatically sets `-fixSE = null`" `references/command-list.md:18` |
| 6 | set `-nT 0` | SE times become first/last appearances **and** the preservation model is forced to HPP | "the preservation model is automatically set to HPP" `references/command-list.md:240` |
| 7 | set `-fixShift` | the rate priors change underneath you | "This will automatically switch the priors on speciation and extinction rates into half-Cauchy distributions" `references/command-list.md:124`; `-cauchy 0 0` then becomes the default (`:175`) |
| 8 | set `-ncat` without `-mG` (or `-pL`/`-pM` with `-N` given) | ignored | `-ncat` "used only when running under a Gamma model" `references/command-list.md:101` (the source has a double space: "used only when  running"); `-pL` "used only if the number of extant taxa is not specified (i.e. `-N -1`)" `:167` |
| 9 | pass `-b 0.5` expecting half-a-sample | it means half of `-n` | "When set to a number between 0 and 1, it is interpreted as a fraction of the total number of MCMC generations" `references/command-list.md:69` |
| 10 | feed `-plot`/`-mProb` a run with `-b 0` | burn-in not excluded, and the summarising page claims a different default | `-b 0` "(default; all samples are logged)" `references/command-list.md:71` vs "(by default set to 1)" `../pyrate-summarize-results/references/summarize-results.md:40` |
| 11 | `-qShift` without an epoch file / with a bad one | TPP cannot be set up | "you need to provide a file containing the times that delimit the different epochs" `references/command-list.md:92`; shape shown by `../assets/files/cmdref-epochs_q.txt` |
| 12 | `-trait_file` with names that differ from the input file | trait table does not match the data set | "The first column of the table should include the species names (identical to those used in the PyRate file)" `references/command-list.md:133`; example file shape in `../assets/files/cmdref-trait-table.txt` |
| 13 | `-pC 0` in a single-correlation Covar model | hyper-prior route not applicable | "This option should only be used if at least 2 correlation parameters are being estimated" `references/command-list.md:187` - the sentence then truncates inside its own `-mCov` links (see EN vs CN drift) |
| 14 | expect `-plot` to work without R | no RTT plot | `-plot` "generates an R script that is used to produce a graphic" output via Rscript `../pyrate-installation/references/home.md:84` |

## How to read the index: arity, value forms, evidence

* **arity** is the number of values the page's own `Example:` line shows. `-thread 1 3` takes two
  integers (`references/command-list.md:75-79`), `-tC 0.025 0.025 0.1` three
  (`references/command-list.md:261`), `-mG` none (`references/command-list.md:98`) - **one
  exception**: the `-cauchy` block prints no `Example:` line at all, so its two values come from the
  prose forms `-cauchy 0 0` / `-cauchy x y` (`references/command-list.md:175-176`).
* **enumerated domains** printed as example lines, never as prose ranges: `-singleton 1 / 2 / -1`
  (`:40-42`), `-mCov 1-5` (`:140-144`), `-logT 0 / 1 / 2` (`:153-155`), `-multiR 0 / 1` (`:232`),
  `-A 0 / 1 / 2 / 3` (`:47-54`).
* **`-b` is dual-typed** (int = iterations discarded, or `0 < x < 1` = fraction of `-n`)
  `references/command-list.md:69-73` - and the page's own gloss on the int form counts *samples*
  ("first 1,000 samples are discarded" `references/command-list.md:72`), exactly as
  `../pyrate-continuous-covariates/references/pyratecontinuous.md:14` does ("the number of samples
  excluded is set with the command `-b`"). So on the samples reading an `-n`/`-s` chain logs
  `-n`/`-s` samples and a larger `-b` voids the run: keep `-b` below that quotient and check it.
* **paths** are the value of `-d`, `-wd`, `-qShift`, `-fixSE`, `-fixShift`, `-trait_file`, `-out`
  takes a tag string, not a path `:32-35`.
* *not stated* in the default column means the page prints no default - not that there is none. Those
  questions go to the *Not documented in this wiki* table below.

## Master index - every command the page prints

### `input files / working directory` - page section "Input files, working directory" (EN 9 / CN 10), 6 blocks

| command | EN@ / CN@ | values | documented default | what the page states |
| --- | --- | --- | --- | --- |
| `<input file>` | 12 / 13 | path to the *_PyRate.py occurrence file | *not stated* | the input file itself: occurrence data as a list of Numpy arrays |
| `-d` | 17 / 18 | path to a tab-separated origin/extinction table | *not stated* | alternative input: given times of origin/extinction per species; auto-sets -fixSE = null |
| `-wd` | 22 / 23 | path_to_target_directory | *not stated* | working directory for all output files (else the input-file directory) |
| `-j` | 27 / 28 | int (replicate / data-set number) | `1` | which data set of a multi-data-set input file is analysed |
| `-out` | 32 / 33 | tag string | *not stated* | tag appended to the default stem name of output files |
| `-singleton` | 37 / 38 | 1 / 2 / -1 | *not stated* | 1 excludes taxa with 1 occurrence, 2 excludes taxa with <= 2, -1 excludes extant taxa |

### `main analysis settings` - page section "Main analysis settings" (EN 45 / CN 46), 6 blocks

| command | EN@ / CN@ | values | documented default | what the page states |
| --- | --- | --- | --- | --- |
| `-A` | 46 / 47 | 0 / 1 / 2 / 3 | `2` | 0 MCMC fixed shifts, 1 MCMC + TI marginal likelihood, 2 BDMCMC (default), 3 MCMC with Dirichlet Process Prior (still being tested) |
| `-n` | 56 / 57 | int (generations) | `10000000` | number of MCMC or BDMCMC generations |
| `-s` | 60 / 61 | int | `1000` | MCMC sampling frequency |
| `-p` | 64 / 65 | int | *not stated* | MCMC print-on-screen frequency |
| `-b` | 68 / 69 | int >= 1 (iterations) OR 0 < x < 1 (fraction of -n) | `0` | burn-in discarded (not logged); must be sensible whenever the marginal likelihood is estimated through TI (`-A 1` or `-A 3`) |
| `-thread` | 75 / 76 | int int (birth-death, NHPP) | `0 0` | threads for the BD likelihood and the NHPP likelihood; 0 0 = sequential |

### `preservation model` - page section "Preservation (fossilization) model" (EN 85 / CN 86), 5 blocks

| command | EN@ / CN@ | values | documented default | what the page states |
| --- | --- | --- | --- | --- |
| `-mHPP` | 87 / 88 | (switch) | *not stated* | homogeneous Poisson process instead of the default NHPP |
| `-qShift` | 91 / 92 | path to a file of epoch-boundary times | *not stated* | time-variable Poisson process (TPP): preservation constant within epochs |
| `-mG` | 95 / 96 | (switch) | *not stated* | Gamma model of across-taxon preservation heterogeneity (alpha estimated) |
| `-ncat` | 100 / 100 | int | `4` | number of gamma categories; only used with -mG |
| `-fixSE` | 104 / 104 | path to a *_mcmc.log file, or the literal word null | *not stated* | fix times of speciation/extinction from a previous analysis (or from first/last appearances when set to null) |

### `birth-death constrained shifts` - page section "Birth-death model – constrained shifts" (EN 110 / CN 110), 4 blocks

| command | EN@ / CN@ | values | documented default | what the page states |
| --- | --- | --- | --- | --- |
| `-mL` | 111 / 111 | int | *not stated* | number of speciation rates through time (shifts = values - 1) |
| `-mM` | 115 / 115 | int | *not stated* | number of extinction rates through time (shifts = values - 1) |
| `-mC` | 119 / 119 | (switch) | *not stated* | constrain the time frames of speciation and extinction rates to be equal |
| `-fixShift` | 123 / 123 | path to a text file of shift ages | *not stated* | fix number and ages of shifts, identical for speciation and extinction; switches the BD priors to half-Cauchy |

### `trait-correlated rates (Covar)` - page section "Settings for trait correlated rates (Covar models)" (EN 129 / CN 129), 4 blocks

| command | EN@ / CN@ | values | documented default | what the page states |
| --- | --- | --- | --- | --- |
| `-trait_file` | 132 / 132 | path to a tab-separated Species/Trait table (NA allowed) | *not stated* | trait values supplied as a separate file instead of the input file |
| `-mCov` | 137 / 137 | 1 / 2 / 3 / 4 / 5 | *not stated* | 1 sp, 2 ex, 3 sp+ex, 4 preservation, 5 sp+ex+preservation rate correlated with the trait |
| `-trait` | 146 / 146 | int (trait number) | `1` | which trait of a multi-trait input file is analysed |
| `-logT` | 150 / 150 | 0 / 1 / 2 | `2` | 0 no transformation, 1 log_e, 2 log10 |

### `(hyper)prior settings` - page section "(Hyper)prior settings" (EN 161 / CN 161), 7 blocks

| command | EN@ / CN@ | values | documented default | what the page states |
| --- | --- | --- | --- | --- |
| `-N` | 162 / 162 | int >= 0, or -1 | `-1 (gamma prior route)` | number of extant species; conditions the BD hyperprior on present diversity |
| `-pL` | 166 / 166 | float float (shape scale) | `1.1 1.1` | gamma prior on the speciation rate; only when -N -1 / not specified; its trailing clause is `-pM`'s and `-pP`'s wording verbatim (see EN vs CN drift) |
| `-pM` | 170 / 170 | float float (shape scale) | *not stated* | gamma prior on the extinction rate; the page's example line for -pM misprints '-pL 1.1 1.1'; its trailing clause is `-pL`'s and `-pP`'s wording verbatim |
| `-cauchy` | 174 / 174 | float float; `0 0` or `x y > 0` is what the block describes as setting half-Cauchy scales, `-1 -1` is the value it applies to other priors | `-1 -1` (prose only, no `Example:` line) | "Default `-cauchy -1 -1` is applied when different priors are used (e.g. Gamma)" (`references/command-list.md:175`); under `0 0` - default with `-fixShift` - "the scale parameters will be inferred form the data" (`:175-176`); under `x y > 0` they are "set to x (for speciation rates) and y (for extinction rates)" (`:176`) |
| `-pP` | 178 / 177 | float float (shape scale) | `1.5 1` | gamma prior on the preservation rate |
| `-pS` | 182 / 181 | float | `2.5` | shape of the Dirichlet prior on the relative length of the time frames |
| `-pC` | 186 / 185 | float >= 0 | `1` | sd of the Normal(0, sd) prior on the correlation parameters; 0 estimates the sd from the data with a G(2,2) hyper-prior |

### `advanced (BD)MCMC settings` - page section "Advanced (BD)MCMC settings" (EN 192 / CN 191), 9 blocks

| command | EN@ / CN@ | values | documented default | what the page states |
| --- | --- | --- | --- | --- |
| `-r` | 193 / 192 | int (chains, cold chain included) | *not stated* | number of heated chains for MC3; only with -A 0 |
| `-t` | 197 / 196 | float | `0.03` | temperature of the MC3 heated chains; only with -r > 1 |
| `-sw` | 201 / 200 | int | `100` | frequency of attempted chain swaps in MC3; only with -r > 1 |
| `-k` | 205 / 204 | int | `10` | number of scaling factors for TI marginal-likelihood estimation; only with -A 1 |
| `-a` | 209 / 208 | float | `0.3` | shape of the beta-distributed scaling factors in TI; only with -A 1 |
| `-M` | 213 / 212 | int | `25` | frequency of model update in BDMCMC; only with -A 2 |
| `-B` | 217 / 216 | float | `1` | birth-rate at which BDMCMC proposes new shifts = shape of the Poisson prior on the number of rates; only with -A 2 |
| `-T` | 221 / 220 | float | `1` | time spent updating the model in BDMCMC; only with -A 2 |
| `-S` | 225 / 224 | int | *not stated* | generation after which BDMCMC starts updating the model; only with -A 2 |

### `tuning parameters` - page section "Tuning parameters" (EN 230 / CN 229), 10 blocks

| command | EN@ / CN@ | values | documented default | what the page states |
| --- | --- | --- | --- | --- |
| `-multiR` | 231 / 230 | 0 / 1 | `1` | 0 sliding-window, 1 multiplier proposals for speciation/extinction rates |
| `-tT` | 235 / 234 | float | `1` | window size of speciation/extinction time updates |
| `-nT` | 239 / 238 | int >= 0 | `5` | max number of SE times updated at a time; 0 sets SE times to first/last appearances AND forces the preservation model to HPP |
| `-tQ` | 243 / 242 | float float (q, alpha) | `1.2 1.2` | window sizes of the preservation rate and of the gamma heterogeneity alpha |
| `-tR` | 247 / 246 | float | `0.05` | window size of speciation/extinction rate updates |
| `-tS` | 251 / 250 | float | `1` | window size of shift-time updates |
| `-fS` | 255 / 254 | float | `0.7` | frequency of updating shift times while updating BD parameters; auto-set to 0 when no shifts are sampled or shift times are fixed |
| `-tC` | 259 / 258 | float float float (sp, ex, q) | `0.025 0.025 0.1` | window sizes of the correlation-parameter updates |
| `-fU` | 263 / 262 | float float float (preservation, BD, Covar) | `0.02 0.18 0.08 under the Covar model` | update frequencies; the remainder updates speciation/extinction times |
| `-fR` | 267 / 266 | float <= 1 | `1` | fraction of BD rates updated at a time; lower it to improve mixing in models with many shifts |

## Analysis modes, and who owns which command

| `-A` | what the page says | commands this page restricts to it | cite |
| --- | --- | --- | --- |
| `0` | "run an MCMC for parameter estimation, i.e. with fixed number of shifts" | `-r` (hence `-t`, `-sw`); `-mL`/`-mM`/`-mC` set the shift structure; the `lambda_0, lambda_1, ...` / `mu_0, mu_1, ...` / `shift_sp_1, ...` log columns exist "only logged under fixed number of shifts, i.e. with `-A 0` or `-A 1`" | `references/command-list.md:47, 112, 116, 194`; `../pyrate-summarize-results/references/summarize-results.md:20` |
| `1` | "run an MCMC with thermodynamic integration" plus "to estimate the fit of a birth-death model"; writes `*_marginal_likelihood.txt` | `-k`, `-a`; `-b` "Must be set to a reasonable number when estimating marginal likelihood through TI" — the goal, which both `-A 1` and `-A 3` serve | `references/command-list.md:49, 54, 206, 210, 69` |
| `2` | "run a BDMCMC analysis" to "jointly estimate the number of rate shifts in the birth-death process"; the example line reads 'Example: `-A 2`' followed by '(default)' | `-M`, `-B`, `-T`, `-S`; in this mode `-mL`/`-mM` "is only used to set the number of starting rates" | `references/command-list.md:51-52, 112, 214-226` |
| `3` | "MCMC analysis with Dirichlet Process Prior on the speciation and extinction rates within fixed time bins. Warning: this function is currently still being tested." | none documented | `references/command-list.md:54` |
| `4` | **not on this page at all** (`grep -n -- '-A 4' references/command-list.md` = 0 hits), yet used by the tutorials as RJMCMC | `-edgeShift`, `-min_dt`, `-plotRJ`, `-combLogRJ`, `-bound_se` are RJMCMC-side commands documented elsewhere | `../pyrate-bd-analysis/references/tutorial-1.md:174`; `../pyrate-rjmcmc/references/tutorial-3.md` |

## Interlocks: what each command silently changes

| command | interlock, in the page's words | cite |
| --- | --- | --- |
| `-d` | "automatically sets `-fixSE = null`" - and so "the estimation of preservation rates and times of speciation/extinction are switched off" | `references/command-list.md:18` |
| `-fixSE` | PyRate runs "without estimating them and without calculating the likelihood of the preservation process (NHPP or HPP)"; `-fixSE null` uses first/last appearances | `references/command-list.md:105` |
| `-nT 0` | "speciation/extinction times are set equal to first/last appearances and the preservation model is automatically set to HPP" | `references/command-list.md:240` |
| `-fixShift` | number and placement of shifts "fixed and set identical for both speciation and extinction" + priors switch to half-Cauchy | `references/command-list.md:124` |
| `-cauchy` | "Default `-cauchy -1 -1` is applied when different priors are used (e.g. Gamma)"; `0 0` = scales inferred from data; `x y > 0` = fixed scales | `references/command-list.md:175-176` |
| `-N` / `-pL` / `-pM` | with `-N -1` "or if not specified, a gamma prior will be used instead with shape and scale parameters defined by the flags `-pL` and `-pM`" | `references/command-list.md:163, 167, 171` |
| `-mHPP` vs `-qShift` | HPP "instead of non-homogeneous Poisson process (NHPP)"; `-qShift` selects TPP - both replace the same default. "Note that the NHPP is used unless differently specified." | `references/command-list.md:88, 92` |
| `-mG` + `-ncat` | Gamma heterogeneity "can be applied to the NHPP, HPP, and TPP preservation models"; `-ncat` counts the categories, Gamma model only | `references/command-list.md:97, 101` |
| `-mL`/`-mM` + `-mC` | `-mC` "is only used in birth-death models with at least one rate shift (e.g. with `-mL 2` and `-mM 2`) and" (sentence truncated on the page) | `references/command-list.md:120` |
| `-mCov` + `-trait` / `-trait_file` / `-tC` / `-pC` / `-fU` | trait read from the input file unless `-trait_file` given; `-tC` window sizes "depending on the Covar model selected"; `-fU` default quoted only "under Covar model" | `references/command-list.md:130, 133, 260-261, 265, 187` |
| `-fS` | "The value will be automatically set to 0 when no rate shifts are being sampled or if the times of shifts are fixed" - the page then names `-fixSE` where `-fixShift` seems meant | `references/command-list.md:256` |
| `-j` | also selects which replicate of a multi-column `-d` table is analysed | `references/command-list.md:28, 19` |
| `-r` | "Each chain will use a different processor if available. The number includes the 'cold' chain." | `references/command-list.md:194` |
| `-thread` | `-thread 0 0` = "sequential likelihood calculation" and "will not use the multiprocessing python library" | `references/command-list.md:76-78` |

## Commands this page never documents (known only from other pages)

These are real PyRate.py flags in the corpus with **no block on the command-list page**; the citations
point at the sibling mirror that prints them. `example-only` = the only place the flag is *named* is a
copy-paste command line, so its value semantics are not documented anywhere.

| flag | evidence | cite |
| --- | --- | --- |
| `-A 4` (RJMCMC) | prose, contradicts the page's default | `../pyrate-bd-analysis/references/tutorial-1.md:174` |
| `-BF` | documented block | `../pyrate-summarize-results/references/summarize-results.md:67-69` |
| `-mProb` | documented block | `../pyrate-summarize-results/references/summarize-results.md:63-65` |
| `-plot`, `-plot2`, `-tag`, `-root_plot`, `-data_info` | documented blocks | `../pyrate-summarize-results/references/summarize-results.md:39, 45, 53, 58, 9` |
| `-combLog` | **example-only**: introduced by "you can use the command:" then a command line | `../pyrate-input-file/references/tutorial-1.md:225-227` |
| `-PPmodeltest` | **example-only**; the prose above it is itself truncated, breaking off at "A maximum likelihood test across" | `../pyrate-input-file/references/tutorial-1.md:154-156` |
| `-fQ` | **example-only**: bare line `-fQ 0.1 -tQ 1.05 1.05`; the prose never names it | `../pyrate-rjmcmc/references/tutorial-3.md:117-119` |
| `-bound_se` | **example-only** (file argument in two command lines) | `../pyrate-rjmcmc/references/tutorial-3.md:142, 146` |
| `-col_tag` | named in prose, values never enumerated | `../pyrate-rjmcmc/references/tutorial-3.md:110` |
| `-log_marginal_rates` | named in prose inside an example invocation | `../pyrate-rjmcmc/references/tutorial-3.md:60` |
| `-check_names`, `-log_sp_q_rates`, `-edgeShift`, `-plotQ`, `-min_age_plot`, `-min_dt`, `-ltt`, `-grid_plot`, `-resample`, `-se_gibbs`, `-plotRJ`, `-combLogRJ` | described in tutorial prose, no block on this page | `../pyrate-input-file/references/tutorial-1.md:94, 149, 267, 239`; `../pyrate-rjmcmc/references/tutorial-3.md:46, 73, 99`; `../pyrate-continuous-covariates/references/tutorial-2.md:68, 86`; `../pyrate-mcmc-tuning/references/tutorial-6.md:13` (`-fast_burnin` has its own block there) |

## EN vs CN drift between the two mirrors

The CN twin (`references/command-list-cn.md`) is a local translation, not an upstream page; where the
English is ambiguous the CN wording is the translator's reading, so both are reported.

* **Line offsets are not constant.** Measured heading-by-heading: **CN = EN + 1** from `-A` to `-mG`
  (`-A` EN 46 / CN 47, `-n` EN 56 / CN 57, `-mG` EN 95 / CN 96), **CN = EN** from `-ncat` to `-cauchy`
  (EN 100 / CN 100, EN 174 / CN 174) and **CN = EN − 1** from `-pP` on (`-pP` EN 178 / CN 177,
  `-multiR` EN 231 / CN 230, `-fR` EN 267 / CN 266) - the EN `-cauchy` prose is split across two lines
  (175-176) where CN fits it into one (174). Never reuse an EN line number as a CN line number.
* **Truncations are upstream, not translation loss.** `-mC` ends "(e.g. with `-mL 2` and `-mM 2`) and"
  in EN `references/command-list.md:120` and "（例如配合 `-mL 2` 与 `-mM 2`），且" in CN
  `references/command-list-cn.md:120` - both stop mid-sentence.
* **The garbled `-mG` sentence is resolved differently.** EN 97 reads "across-taxa rate heterogeneity
  has been shown to Gamma model accounts to some extent for temporal changes of the preservation
  rates" (ungrammatical, words missing); CN 97 states a clean reading. Quote EN verbatim and do not
  treat the CN as authoritative for wording.
* **Misprints are mirrored, not corrected.** `-pM`'s example prints `-pL 1.1 1.1` in EN
  (`references/command-list.md:172`, identical at `:168`) and the `-trait_file` example points at
  `Ursidae_SE.txt` with the trailing gloss "correlated speciation rate" in both languages
  (`references/command-list.md:135`, `references/command-list-cn.md:135`); the linked example file is
  `Ursidae_bm.txt` (`:133`).
* **One clause is printed in three different blocks.** "which estimates the expected number of fossil
  occurrences per lineage per Myr" is verbatim in the `-pL` (`references/command-list.md:167`), `-pM`
  (`:171`) and `-pP` (`:179`) blocks - attached to the speciation, the extinction *and* the
  preservation rate alike - and the CN twin repeats it at the same three places
  (`references/command-list-cn.md:167, 171, 178`); the corpus uses the phrase nowhere else. What each
  prior is placed on is stated by the first half of the sentence ("the gamma distributed prior on the
  speciation rate" `references/command-list.md:167`); treating the trailing clause as a definition of
  the `-pL`/`-pM` priors is unsupported (inferred: duplicated upstream wording, not a third meaning).
* **Whitespace/typos to keep when grepping:** "used only when  running" (double space, `-ncat` EN 101);
  "inferred form the data" (`-cauchy` EN 176); "This command if used only if" (`-pL`/`-pM` EN 167, 171);
  tabs inside sentences at EN 13 and EN 49. CN 101 and CN 175 are clean, so an EN-only grep is the
  safer audit.
* **No terminology drift that changes a rule.** The interlock sentences agree: EN prose 88 / 105 / 124 /
  163 / 187 / 240 / 256 / 264 correspond to CN prose 89 / 105 / 124 / 163 / 186 / 239 / 255 / 263, and
  each mirror marks a default on exactly 31 lines
  (`grep -c -- '(default' references/command-list.md` = `grep -c '默认值' references/command-list-cn.md` = 31).

## Worked example

Assemble first, run second - `build_command.py` carries the **PyRate.py grammar only** (its accepted
flags are parsed from `references/command-list.md`, so `--program` refuses any other program of the
family), never executes anything and prints only rules it can cite (exit 0 = assemblable,
2 = forbidden combination, 4 = unknown flag / wrong arity / a `--program` it cannot validate).

```bash
# this skill directory, addressed from the suite root wherever the bundle is installed;
# if your shell is already inside it, skip this step
cd pyrate-command-reference

# 1. can this machine even host the documented runtime? (exit 1 = blockers; here it finds no python2)
python3 scripts/check_env.py            # add --json for machine-readable output

# 2. assemble a TI model-testing run (-A 1) from the fixtures this skill owns:
#    -d table  -> cmdref-SE-table.txt, epoch file -> cmdref-epochs_q.txt,
#    trait table -> cmdref-trait-table.txt
#    All three carry our '#' provenance header, which no document tells PyRate to skip and which
#    displaces the column-header row that both tables require - so strip first, then point at the copies.
mkdir -p /tmp/cmdref_run
for f in cmdref-SE-table cmdref-epochs_q cmdref-trait-table; do
    grep -v '^#' "../assets/files/$f.txt" > "/tmp/cmdref_run/$f.txt"; done
python3 scripts/build_command.py \
    -d /tmp/cmdref_run/cmdref-SE-table.txt \
    -A 1 -n 10000000 -s 1000 -b 1000 -k 32 -a 0.3 \
    -qShift /tmp/cmdref_run/cmdref-epochs_q.txt -mG -ncat 4 \
    -trait_file /tmp/cmdref_run/cmdref-trait-table.txt -mCov 3 -logT 0 -pC 0 \
    -N -1 -pL 1.1 1.1 -pP 1.5 1 -cauchy 0 0 \
    -tT 1 -nT 5 -fR 0.2 -out demo -wd ./out
# COMMAND: python PyRate.py -d /tmp/cmdref_run/cmdref-SE-table.txt -wd ./out -out demo -A 1 -n
#   10000000 -s 1000 -b 1000 -qShift /tmp/cmdref_run/cmdref-epochs_q.txt -mG -ncat 4 -trait_file
#   /tmp/cmdref_run/cmdref-trait-table.txt -mCov 3 -logT 0 -N -1 -pL 1.1 1.1 -cauchy 0 0 -pP 1.5 1 -pC
#   0 -k 32 -a 0.3 -tT 1 -nT 5 -fR 0.2
# (assembled line only - nothing executed)          EXIT=0
# the tool reorders tokens into the page's section order and keeps -d in front of the -wd/-out tags.
# every number here is one the page prints: -n 10000000 `references/command-list.md:58`,
# -s 1000 `references/command-list.md:62`, -b 1000 `references/command-list.md:72`; the chain logs
# 10000000/1000 = 10,000 samples, and -b 1000 stays below that under either unit the corpus gives
# -b - iterations (`references/command-list.md:69`) or samples
# (`../pyrate-continuous-covariates/references/pyratecontinuous.md:14`). A -b above 10,000 would
# discard the whole chain on the samples reading, which is why none is used here.

# 3. the same tool rejecting a forbidden combination (mode interlocks + value domain), verbatim output:
python3 scripts/build_command.py in.py -A 1 -ncat 4 -r 4 -b 0.1 -logT 10
# [ERROR] -logT: value 10 is outside the documented set [0, 1, 2] ("-logT 2 trait is log10 transformed
#         (default)" (references/command-list.md:155)).
# [ERROR] -ncat without -mG: "This command is used only when running under a Gamma model of
#         preservation (i.e. with -mG)." (references/command-list.md:101) Fix: add -mG or drop -ncat.
# [ERROR] -r with -A 1: "This command is used only when running MCMC analysis for parameter estimation
#         (i.e. with -A 0)." (references/command-list.md:194)
# [NOTE] -b 0.1: "When set to a number between 0 and 1, it is interpreted as a fraction of the total
#         number of MCMC generations." (references/command-list.md:69)   ->  exit code 2

# 4. launch it for real (invocation form, references/command-list.md:15) - on the stripped copies again,
#    because command-list.md documents no '#' tolerance for -d, -qShift or -trait_file:
python2 PyRate.py -d /tmp/cmdref_run/cmdref-SE-table.txt -A 1 -n 10000000 -s 1000 -b 1000 \
    -k 32 -a 0.3 -qShift /tmp/cmdref_run/cmdref-epochs_q.txt -mG -ncat 4 \
    -trait_file /tmp/cmdref_run/cmdref-trait-table.txt -mCov 3 -logT 0 -pC 0 \
    -N -1 -pL 1.1 1.1 -pP 1.5 1 -cauchy 0 0 -tT 1 -nT 5 -fR 0.2 -out demo -wd ./out

# 5. read the run back: which stems appeared, and which -A actually ran
python3 scripts/parse_results.py --stems
python3 scripts/parse_results.py ./out
```

Step 3 is the useful one: three of the four flags are individually valid PyRate commands, and the page
is what makes the combination illegal.

## Pitfalls

* **Reading `-pM`'s default off the page.** Its `Example:` line is a misprint of `-pL`
  (`references/command-list.md:170-172`); `-pM` therefore has *no documented default*, although
  `:163` implies it shares `-pL`'s gamma-prior route. `../pyrate-input-file/references/tutorial-1.md`
  does not repair it either.
* **Passing `-cauchy -1 -1` to switch the half-Cauchy hyper priors *on*.** The page applies `-1 -1`
  "when different priors are used (e.g. Gamma)" (`references/command-list.md:175`) - i.e. alongside
  the gamma route of `-N -1` with `-pL`/`-pM` (`references/command-list.md:163`). The half-Cauchy
  settings the block describes are `0 0` ("the scale parameters will be inferred form the data", and
  the default under `-fixShift`) and `x y > 0` (`references/command-list.md:175-176`). The block prints
  no `Example:` line, so no `-cauchy` pair anywhere on the page is offered as an example to copy.
* **Assuming every command has a default.** `-S` (`:227`) and `-p` (`:66`) print example values
  *without* "(default)"; so do `-d`, `-wd`, `-out`, `-singleton`, `-mHPP`, `-qShift`, `-mG`, `-fixSE`,
  `-mL`, `-mM`, `-mC`, `-fixShift`, `-trait_file`, `-mCov`, `-pM`, `-r` - 18 blocks in all. `-N` is a
  special case: `:163` says what happens "if not specified" (the gamma-prior route via `-pL`/`-pM`) but
  never names a value for `-N` itself.
* **Believing `-b 0` carries over to plotting.** `-b 0` is the analysis default
  (`references/command-list.md:71`); the plotting page asserts of `-b` "(by default set to 1)"
  (`../pyrate-summarize-results/references/summarize-results.md:40`).
* **Treating `-logT 10` as legal.** Tutorial 4 runs `-mCov 5 -logT 10 -pC 0`
  (`../pyrate-diversity-dependence/references/tutorial-4.md:124`, mirrored in CN at
  `../pyrate-diversity-dependence/references/tutorial-4-cn.md:125`), while this page enumerates only
  `0`, `1`, `2` (`references/command-list.md:152-155`). And `-logT 1` means `log_e` on this page
  (`:154`) while the RJMCMC tutorial states "The command `-logT 1` can be added to plot
  log10-transformed rates-through-time" (`../pyrate-rjmcmc/references/tutorial-3.md:88`).
* **Confusing scale with rate for `-pP`.** This page says "Shape and scale parameters of the gamma
  distributed prior on the preservation rate" and prints "Example: `-pP 1.5 1` (default)"
  (`references/command-list.md:179-180`); tutorial 1 says "The default prior on the vector of
  preservation rates is a single gamma distribution with shape = 1.5 and rate = 1.5" and then treats
  "-pP 2 0.1" as a shape/rate pair (`../pyrate-bd-analysis/references/tutorial-1.md:134`). Two
  parameterisations, unreconciled - pass explicit values and read them back from `*_sum.txt`.
* **Forgetting `-A 3` is experimental.** "Warning: this function is currently still being tested."
  (`references/command-list.md:54`), and no time-bin-setting command is documented on the page.
* **Passing the clade column junk in a `-d` table.** Column 1 is the clade assignment, "only useful in
  MCDD analyses … and should be filled with 0s for all other analyses"
  (`references/command-list.md:18`); see `../assets/files/cmdref-SE-table.txt`.
* **Losing a replicate.** Extra `-d` columns (5th/6th = second origin/extinction estimates) are selected
  by `-j`, whose default is `1` (`references/command-list.md:19, 30`);
  `../assets/files/cmdref-SE-table-multi-replicate-EXCERPT.txt` shows the shape.
* **Grep-ability.** Several option blocks are written without a space after the heading marker
  (``#####`-wd``` at `:22`, ``##### -thread`` at `:75`), so use `grep -n '^#####'`, not
  `grep -n '^##### '`, when counting blocks (51 = 50 options + `<input file>`).
* **`-d` and the input file are alternatives, not a pair.** `Example: `python PyRate.py -d
  path_to_input_file/Ursidae_SE.txt`` (`references/command-list.md:20`) shows `-d` replacing the
  positional `*_PyRate.py` argument; combining both is not documented.

## Not documented in this wiki

| question you may be tempted to answer | why you must not fill it in |
| --- | --- |
| What runs if `-A` is omitted? | `:52` says `-A 2` (default); `../pyrate-bd-analysis/references/tutorial-1.md:174` says RJMCMC. No third source decides. |
| What are the defaults of the other 18 commands? | The page prints `(default)` on 31 lines covering 30 options, plus prose defaults for `-cauchy` (`:175`) and the `-N` "if not specified" route (`:163`); nothing for the rest. Absence of a stated default is not evidence of no default. |
| Which column headers must a `-d` table carry? | `:18` requires "the first line containing column headers" but never names them; the four words in `cmdref-SE-table.txt` (`clade species ts te`) are labels this suite invented for the fixture, not a documented rule and not an upstream convention (contrast `../assets/files/cont-se-est.txt`, which heads the same shape `clade id origination extinction`). |
| Are more than two replicate columns in `-d` allowed? | `:19` says only "these can be provided as additional columns" and exemplifies a 5th and a 6th; nothing about a 7th. |
| Can `-logT` take values above 2? | Only `0/1/2` are enumerated (`:152-155`); `-logT 10` in tutorial 4 is unexplained. |
| What completes the truncated `-mC` sentence? | Both language mirrors stop at "and" / "，且" (`:120`); any completion is invention. |
| Which `-mCov` values make `-pC 0` valid? | `:187` truncates inside its own `-mCov` links, so the intended set is unreadable; `../pyrate-diversity-dependence/references/tutorial-4.md:120` instead recommends it "with `-mCov 3` or `-mCov 5`". |
| Is `-pP`'s second parameter a scale or a rate? | Contradicted between `:179` and `../pyrate-bd-analysis/references/tutorial-1.md:134`. |
| Does `-thread` cap at the physical core count, and what happens if you over-request? | `:76-77` states only what `0 0` means. |
| Does `-singleton -1` require the data set to be non-extant-safe? | `:42` gives the effect ("excludes extant taxa") and `:39` promises on-screen counts, nothing more. |
| What columns appear in `*_mcmc.log`, and in which order? | The summarising page lists column *names* (`../pyrate-summarize-results/references/summarize-results.md:18-20`) but the corpus prints no complete output file; `parse_results.py` reports what is present, never what "should" be. |
| Is there a `-A 4` block, and which options does it accept? | The flag is absent from this page (`grep -n -- '-A 4' references/command-list.md` = 0). |
| Does `-fS` mean `-fixShift` at `:256`? | The page names `-fixSE`; both readings are consequences, so the tool warns instead of choosing. |

## Related skills

* `../pyrate/` - what PyRate is, the program family, the tutorials index.
* `../pyrate-installation/` - Python/`numpy`/`scipy`/`argparse`/`multiprocessing` requirements, `pyrate_lib` adjacency, virtualenv recipe (the page that conflicts with `home.md` on Python 3).
* `../pyrate-input-file/` - the `*_PyRate.py` occurrence file, `pyrate_utilities.R`, `-check_names`, the PBDB workflow, `-PPmodeltest`.
* `../pyrate-preservation-models/` - NHPP/HPP/TPP/Gamma choice in tutorial context (`-mHPP`, `-qShift`, `-mG`, `-ncat`, `-log_sp_q_rates`).
* `../pyrate-bd-analysis/` - the end-to-end `-A 2` BDMCMC tutorial and its output files.
* `../pyrate-rjmcmc/` - `-A 4`, `-plotRJ`, `-combLogRJ`, `-min_dt`, `-bound_se`, `-se_gibbs`, `-col_tag`, `-fQ`.
* `../pyrate-summarize-results/` - `*_sum.txt`/`*_mcmc.log`/`*_marginal_rates.log` column meanings, `-plot`, `-plot2`, `-tag`, `-root_plot`, `-mProb`, `-BF`, `-data_info`.
* `../pyrate-continuous-covariates/` - `PyRateContinuous.py`, `-ginput`, `_se_est.txt`, `-ltt`, `-grid_plot`, `-resample`.
* `../pyrate-diversity-dependence/` - `PyRateMCDD`, `-mCov`/`-pC`/`-logT` in the MCDD tutorial, the clade column of `-d`.
* `../pyrate-trait-age-models/` - Covar model maths and trait-correlated rate interpretation (`-mCov`, `-trait`, `-tC`).
* `../pyrate-des/` - DES model pages and their own option set (`-sym*`, `-constr*`, `-age1/2`, `-bin_size`).
* `../pyrate-bdnn/` - the `-BDNN*` option family, none of which exists on this page.
* `../pyrate-mcmc-tuning/` - `tutorial-6.md` tuning narrative (`-fast_burnin` has its block there, not here).
* `../assets/files/` - the fixtures listed at the end of this file.

## Resources

| file | what's in it | load when |
| --- | --- | --- |
| `references/command-list.md` | verbatim EN mirror of the page whose corpus file is `PyRate-doc/PyRate-wiki/2.-PyRate:-command-list.md` (frontmatter `title: PyRate: command list`) - 51 `#####` blocks in 8 `###` sections, 268 lines (`wc -l`), last line without trailing newline. Every bare line number in this SKILL.md refers to it. | you need the exact wording of a rule, a default, or a value list; before writing any option into a command line |
| `references/command-list-cn.md` | local Simplified-Chinese twin (`translated_from: command-list.md`), same 51 blocks; 268 lines ending with a newline, body starting at line 10 because its frontmatter is 9 lines | the English is truncated, ungrammatical or ambiguous (`-mC` `:120`, `-mG` `:97`, `-pC 0` `:187`) - read CN, then report both |
| `scripts/pyrate_commands.py` | the data table behind the index: 51 rows with section, EN line, CN line, arity, values, default, semantics, `requires`/`conflicts`, plus `KNOWN_ELSEWHERE` (flags documented on other pages) and `ANALYSIS_MODES` | you want the machine-readable form of the master table, or to extend a rule without editing the mirrors |
| `scripts/check_env.py` | prints one line per check: python2 vs python3 on PATH, `numpy`/`scipy`/`argparse`/`multiprocessing`/`thread` import tests, `PyRate.py` + `pyrate_lib` adjacency, `Rscript`, the four documented defaults with their `command-list.md` lines, a blocker list and a VERDICT; `--json`; exit 1 when blocked. Read its `pyrate_lib` line as a layout hint, not as a requirement stated for `PyRate.py` - the corpus scopes it to "when you run a program requiring `pyrate_lib` (e.g. `PyRateContinuous`)" (`../pyrate-installation/references/home.md:61`) | before any run, and whenever a run dies before printing its settings |
| `scripts/build_command.py` | validates a command line against the page: unknown flags, arity, value domains, mode interlocks, `-d`/`-qShift`/`-fixShift`/`-trait_file` file shapes, utility-vs-analysis mixing; prints the canonical `python PyRate.py …` line plus the citing reason for every note/warning/error; `--list`, `--json`, `--dry-run`, `--self-test` (re-verifies all 142 of its own quotations and replays every documented `python …PyRate.py …` line of the suite). **It carries the `PyRate.py` grammar only**: `--program` accepts `PyRate.py` in any path form and refuses every other program of the family with exit 4, naming the supported program and the page that documents the refused one's own options - `PyRateContinuous.py` documents `-c` (`../pyrate-continuous-covariates/references/pyratecontinuous.md:31`), `-m` (`:34`) and `-DD` (`:28`), none of which the builder accepts, and its `-A` is offered only as `-A 0`/`-A 1` (`:26`) where `PyRate.py`'s page carries `-A 2 (default)` (`references/command-list.md:52`); `--help` prints the same scope | you are about to type PyRate options, or you need the exact doc sentence that forbids a combination |
| `scripts/parse_results.py` | reads `*_mcmc.log`, `*_marginal_rates.log`, `*_marginal_likelihood.txt`, `*_sum.txt`; reports columns, which `-A` mode they evidence (`k_birth`/`k_death` ⇒ BDMCMC, `lambda_*`/`shift_*` ⇒ `-A 0`/`-A 1`, `beta` ⇒ TI), arithmetic summaries, `--b` burn-in effect, `--stems` | a run finished (or half-finished) and you must know what it actually did |

## grep recipes

Run from this skill directory; all patterns were executed and match.

```bash
grep -n '^#####' references/command-list.md | wc -l          # 51 blocks = 50 options + <input file>
grep -n '^### ' references/command-list.md                   # the 8 sections and their line numbers
grep -n -- '(default' references/command-list.md | wc -l     # 31; 'grep -n 默认值' on CN also 31
grep -n -- '-A 4' references/command-list.md                 # 0 hits -> -A 4 is not on this page
grep -n -- '-fixSE = null' references/command-list.md        # line 18: the -d interlock, full sentence
grep -n -- 'only when\|only used\|only be used' references/command-list.md   # 15 interlock statements
grep -n -- '-pL 1.1 1.1' references/command-list.md          # 168 AND 172 -> the -pM example misprint
grep -n 'Ursidae_SE' references/command-list.md references/command-list-cn.md # 135: -trait_file misprint in both
grep -n 'and$' references/command-list.md; grep -n '，且$' references/command-list-cn.md   # -mC truncated in both
```

## Runnable fixtures (`../assets/files/`)

| fixture | provenance (first lines of the file) | what it shows |
| --- | --- | --- |
| `cmdref-SE-table.txt` | `# note: SYNTHETIC - every number below was invented for this fixture, and the header labels … are invented too` (9 `#` lines; the header retracts an earlier verbatim/md5 claim) | the `-d` table shape as this suite built it: tab-separated, our own header `clade species ts te`, 75 data rows (`grep -vcE '^\s*#'` = 76 counting that header), clade `0`, arbitrary numeric ids, Myr ages. Measured against the fresh upstream checkout at ../PyRate-master/example_files/Ursidae_SE.txt (not part of this suite; the path is informational, not a suite-relative link): its 76 lines hash to `6d9d04ec…` and so do these 76 payload lines — i.e. the values here are that file's, while the fixture's own header still calls them invented and the corpus itself never prints them. Strip the `#` lines before passing to `-d` |
| `cmdref-SE-table-multi-replicate-EXCERPT.txt` | `# source: derived from … line 18 (extra-column rule) on top of example_files/Ursidae_SE.txt rows 1-4 | derived` | the 5th/6th-column replicate rule (`ts2`, `te2`) selected by `-j`; the ts2/te2 numbers are illustrative additions (not upstream data), the first four columns are verbatim rows 2-5 |
| `cmdref-epochs_q.txt` | `# source: dsilvestro/PyRate example_files/epochs_q.txt (linked from … line 92, the -qShift example) | verbatim` | the `-qShift` file: 31 epoch-boundary ages, one per line, no header, youngest first (0.0117) to oldest (541.0) |
| `cmdref-epochs.txt` | `# source: dsilvestro/PyRate example_files/epochs.txt (named by -fixShift at … line 124) | verbatim` | the `-fixShift` file ("see file 'epochs.txt' in PyRate's example files"): 30 fixed shift ages, one per line |
| `cmdref-trait-table.txt` | `# source: dsilvestro/PyRate example_files/Ursidae_bm.txt (linked from … line 133, the -trait_file rule) | verbatim` | the `-trait_file` table: header `Species<TAB>Trait`, names matching the input file, `NA` rows that the MCMC imputes |
| `cmdref-command-index.tsv` | `# source: … command-list.md lines 9-269 | derived` | the machine-readable master index: command, section, EN line, CN line, arity, documented default, values printed by the page; regenerate with `python3 scripts/build_command.py --list` |
| `cmdref-output-stems.txt` | `# source: … command-list.md lines 22-23, 32-35, 49 | … 3.-Summarize-PyRate-results.md lines 12-29, 40 | derived` | every output name the docs print (`*_sum.txt`, `*_mcmc.log`, `*_marginal_rates.log`, `*_marginal_likelihood.txt`, `sp_rates.log`/`ex_rates.log`, `*_se_est.txt`, `*_RTTplot.r`/`.pdf`, `pyrate_mcmc_logs/`) with the line that names it and how `-out`/`-wd` move them |
