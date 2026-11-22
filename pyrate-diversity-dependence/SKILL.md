---
name: pyrate-diversity-dependence
description: "Reference for PyRate multiple-clade diversity dependence: `PyRateMCDD.py` (`-d`, `-n`, `-s`, `-c` clade flag) and the multivariate birth-death model `PyRateMBD.py` (`-d`, `-var` predictor folder, `-m 0` exponential / `-m 1` linear, `-out`, `-rmDD 1`, `-minT`, `-maxT`, `-hsp 0`, `-n`, `-s`, `-plot`). Covers the MCDD 4-column tab-separated input (clade, species id, times of origin and extinction, plus replicate columns), the predictor file format, running MBD on clade diversity trajectories from `-ltt`, Horseshoe vs Gamma hyper-priors, shrinkage weights Wl/Wm and correlation parameters Gl/Gm, Ferns_MBD_short_run.png, the PNAS 2015 canid citation, and that the PyRateMCDD wiki page is under construction. Failure modes: clade column not filled with 0s outside MCDD, 1-based clade numbering, `-c` meaning a clade index here but a correlate file in PyRateContinuous, `-var` given a file not a folder, `-plot` without `-d`/`-var`/`-m`, missing `pyrate_lib`, Python 3 unsupported."
---

# MCDD and MBD: multiple-clade diversity dependence and multivariate birth-death rates

## Overview

Two programs answer the same question — do origination and extinction rates respond to how many lineages coexist — when a single clade is not enough. `PyRateMCDD.py` fits the **multiple-clade diversity-dependent (MCDD)** model, where the birth-death process of each clade runs "with diversity dependencies from its own diversity and the diversity of all other clades" (`references/tutorial-4.md`:36; the Chinese twin is unambiguous here: 在考虑来自其自身多样性以及所有其他演化支多样性的依赖作用下, `references/tutorial-4-cn.md`:37) and the wiki words the same thing as "diversity dependence effects within and between clades" (`../pyrate/references/home.md`:47). `PyRateMBD.py` fits the **multivariate birth-death (MBD)** model, which allows "the estimation of speciation and extinction rates as a function of multiple time-continuous variables" (`references/tutorial-4.md`:46) and which the tutorial explicitly recommends re-using for multiple-clade diversity dependence by feeding the clades' diversity trajectories in as predictors (`references/tutorial-4.md`:73-74). MCDD is Silvestro, Antonelli, Salamin & Quental (2015), *The role of clade competition in the diversification of North American canids*, PNAS 112:8684-8689 — cited in the tutorial as a bare URL (`references/tutorial-4.md`:24, <https://www.pnas.org/content/112/28/8684>) and printed in full only at `../pyrate/references/home.md`:49. MBD is cited only as "(Lehtonen, Silvestro et al. 2017)" with <https://www.nature.com/articles/s41598-017-05263-7> (`references/tutorial-4.md`:46); no full reference for it exists anywhere in this corpus.

The riskiest assumption this skill removes is a **documentation** one. Neither program has a command list: the wiki states "Wiki page for PyRateMCDD is under construction" (`../pyrate-command-reference/references/command-list.md`:18, repeated verbatim at `../pyrate-continuous-covariates/references/pyratecontinuous.md`:11) and Home adds "A detailed command list is in preparation" for `PyRateMCDD.py` (`../pyrate/references/home.md`:47); `PyRateMBD.py` is not even in the wiki program list (`../pyrate/references/home.md`:28-60 lists `PyRate.py`, `PyRateContinuous.py`, `PyRateMCDD.py`, `PyRateDES.py`, `pyrate_lib` only) and `grep -rl "PyRateMBD" ../*/references/` returns exactly four files - `tutorial-4.md` and `tutorial-4-cn.md` as carried here and as carried by `pyrate-trait-age-models` (same mirror, two homes). Consequence: the only MCDD/MBD statements outside `references/tutorial-4.md`:23-94 are Home's one-line model description (`../pyrate/references/home.md`:47) and three near-copies of the origin-extinction table sentence (`../pyrate-command-reference/references/command-list.md`:18 and `../pyrate-continuous-covariates/references/pyratecontinuous.md`:11 word it identically; `../pyrate-continuous-covariates/references/tutorial-2.md`:24 paraphrases it) - none of which is a command list. So the output file names, the complete option sets, the defaults of `-n`/`-s` for these two programs and the replicate-selection behaviour are **undocumented**. Do not import `PyRate.py` behaviour into an MCDD/MBD command line; anything not in the tables below is unknown, not default.

## The 8 things that break a run

| # | What happens | Consequence | Wording + citation |
| --- | --- | --- | --- |
| 1 | The first column of the `-d`/MCDD table is not 0-based, or is not filled with 0s in non-MCDD analyses | Clade identity (hence every between-clade diversity term) shifts by one, or a non-MCDD run is silently told there are several clades | "starting from 0, 1, 2, etc." (`references/tutorial-4.md`:26); "the first column indicates the clade assignment of species, this is only useful in MCDD analyses (Wiki page for PyRateMCDD is under construction) and should be filled with 0s for all other analyses" (`../pyrate-command-reference/references/command-list.md`:18) |
| 2 | Origination/extinction times are hand-made rather than taken from a previous PyRate run | The model assumes those times as given: MCDD input columns 3-4 are "the times of origination and extinction of the species as inferred in a previous PyRate analysis" (`references/tutorial-4.md`:28), and the same table type "does not model preservation" (`../pyrate-continuous-covariates/references/pyratecontinuous.md`:10) | see left; generate them with `-ginput` (`references/tutorial-4.md`:28; `../pyrate-continuous-covariates/references/tutorial-2.md`:27-35) |
| 3 | Replicate columns are appended but no replicate selector is passed | You do not know which replicate pair the run used. Replicates "can be added to the MCDD input file" (`references/tutorial-4.md`:30); "the replicate number is selected through the command `-j`" (`../pyrate-command-reference/references/command-list.md`:18) — but `-j` is documented only for `PyRate.py`, default `-j 1` (`../pyrate-command-reference/references/command-list.md`:27-30) and never shown with `PyRateMCDD.py`. How the extra columns get built *is* documented for the upstream run: `-tag` combines replicated log files into one table "with columns with the origin and extinction of each species given for each replicate" and `-resample N` stores N posterior samples "as additional columns" (`../pyrate-continuous-covariates/references/tutorial-2.md`:45-49, 52-57) | documented / undocumented split — see the `Not documented in this wiki` table |
| 4 | `-c` is used with a PyRateContinuous habit | In MCDD `-c 0` is a **clade index** ("you can also analyze a single clade at time", "using the flag `-c`", `references/tutorial-4.md`:36); in `PyRateContinuous.py` `-c` is the path to a **correlate table** (`../pyrate-continuous-covariates/references/pyratecontinuous.md`:31-32). Same letter, different programs, different meaning; no doc warns about it | see the `-c` row of the MBD vs `PyRateContinuous` comparison table |
| 5 | `-var` points at a single file, or a predictor file lacks its header line | MBD needs "a set of predictors provided as separate files in a single directory" and "The flag `-var` is used to specify the path to a folder containing all predictors" (`references/tutorial-4.md`:53, 71); "Each predictor should be provided as a tab-separated table with a header and two columns for time before present and predictor values" (`references/tutorial-4.md`:54) | `references/tutorial-4.md`:53-54, 66, 71 |
| 6 | `-plot` is run bare, or with a `-m` that differs from the run | "the input data, the directory containing all predictors, and the correlation model (linear or exponential) must be specified" (`references/tutorial-4.md`:88) | `references/tutorial-4.md`:88, 90 |
| 7 | The wrong prior is used for the number of correlates | Horseshoe is on by default; gamma hyper-priors "should be preferred when testing only few variables (e.g. 2-4 correlates)" (`references/tutorial-4.md`:51), switched on with `-hsp 0` (`references/tutorial-4.md`:81, 85) | `references/tutorial-4.md`:49-51, 81, 85 |
| 8 | Environment: Python 3, or `pyrate_lib` not beside the program | "**Please note that Python 3.x is currently not supported", tested with "Python 2.6 – 2.7" (`../pyrate/references/home.md`:69); `PyRateMCDD.py` is listed as "requires library" `pyrate_lib` and "the folder `pyrate_lib` needs to be in the same directory as the program" (`../pyrate/references/home.md`:46, 61) | `../pyrate/references/home.md`:46, 61, 69 |

## MCDD: what varies within versus between clades

| Item | Documented value | Citation |
| --- | --- | --- |
| Program | `PyRateMCDD.py` | `references/tutorial-4.md`:24 |
| Model | multiple-clade diversity dependence (MCDD); rates change through time "as the result of diversity dependence effects within and between clades" | `../pyrate/references/home.md`:47 |
| Within-clade component | the focal clade's own diversity | `references/tutorial-4.md`:36 |
| Between-clade component | the diversity of all other clades in the table — included even when only one clade is analysed (`-c`) | `references/tutorial-4.md`:36, 40 |
| Number of clades analysed | all at once by default; `-c N` restricts the *analysed* birth-death process to clade `N` | `references/tutorial-4.md`:36, 38 |
| Variable selection | "a Bayesian variable selection algorithm that can switch on and off the diversity dependent parameters depending on how important they are to explain rate variation using indicators that can take a value of 0 or 1" | `references/tutorial-4.md`:42 |
| Reference | PNAS 2015 canid paper (bare URL in the tutorial; full citation in Home) | `references/tutorial-4.md`:24; `../pyrate/references/home.md`:49 |
| Command list | none: "A detailed command list is in preparation" | `../pyrate/references/home.md`:47 |

Which method to trust: the tutorial names MBD as "An alternative method that can be used to infer multiple-clade diversity dependence", says MBD "uses the horseshoe prior algorithm to perform variable selection", and reports that the two were compared in <http://www.evolutionary-ecology.com/abstracts/v18/3010.html>, "suggesting that the latter might be preferable" (`references/tutorial-4.md`:42; CN: 结果表明后一种方法可能更为可取, `references/tutorial-4-cn.md`:43). "The latter" = MBD.

## The MCDD input table and the clade-assignment column

One file, tab-separated, one row per species: "a tab-separated table with 4 columns (or more if you have multiple replicates) and one row per species" (`references/tutorial-4.md`:24). This is the same table the `-d` command of PyRate accepts, so the cross-reference is `../pyrate-command-reference/references/command-list.md`:17-18 (the `-d` entry).

| Column | Content (tutorial wording) | Content (command-list wording) | Citation |
| --- | --- | --- | --- |
| 1 | "identifies the clade the species belongs to, starting from 0, 1, 2, etc." | "the first column indicates the clade assignment of species, this is only useful in MCDD analyses (Wiki page for PyRateMCDD is under construction) and should be filled with 0s for all other analyses" | `references/tutorial-4.md`:26 / `../pyrate-command-reference/references/command-list.md`:18 |
| 2 | "a species identifier" | "a species numeric identifier (this values are arbitrary and only used for reference)" | `references/tutorial-4.md`:27 / `../pyrate-command-reference/references/command-list.md`:18 |
| 3 | time of origination "as inferred in a previous PyRate analysis", generated with `-ginput` | time of origin | `references/tutorial-4.md`:28 / `../pyrate-command-reference/references/command-list.md`:18 |
| 4 | time of extinction, same provenance | time of extinction | `references/tutorial-4.md`:28 / `../pyrate-command-reference/references/command-list.md`:18 |
| 5, 6, ... | "If you have multiple replicates of the initial PyRate analysis, these can be added to the MCDD input file" | "5th column for a second estimate of origination times, 6th column for a second estimate of extinction times" | `references/tutorial-4.md`:30 / `../pyrate-command-reference/references/command-list.md`:18 |

Where the extra columns come from - the upstream `-ginput` run makes them: `-tag` combines replicated log files into one table "with columns with the origin and extinction of each species given for each replicate", and `-resample N` stores N posterior samples "as additional columns" (`../pyrate-continuous-covariates/references/tutorial-2.md`:45-49, 52-57). Neither statement says what `PyRateMCDD.py` then does with those columns.

Three pages state this table and they are not identical. `../pyrate-command-reference/references/command-list.md`:18 and `../pyrate-continuous-covariates/references/pyratecontinuous.md`:11 contain the same sentence word for word (verified by substring match); `../pyrate-continuous-covariates/references/tutorial-2.md`:24 paraphrases it - "this is only useful when using" (then a hyperlink whose anchor text is "MCDD models") "and should be filled with 0s for all other analyses" - and, unlike the other two, leaves the time columns unnumbered: "Finally the following columns contain the time of origin and extinction of each species or taxon" (so tutorial 2 allows taxon rows; the other two say "species").

Two things the corpus does not settle, and you must not paper over: (i) column 2 is "a species identifier" in tutorial 4 but "a species numeric identifier" in all three other statements (`../pyrate-command-reference/references/command-list.md`:18, `../pyrate-continuous-covariates/references/pyratecontinuous.md`:11, `../pyrate-continuous-covariates/references/tutorial-2.md`:24) — the wiki says a number, the tutorial says an identifier, and no example row is printed anywhere to break the tie; (ii) supplying `-d` "automatically sets `-fixSE = null`", "meaning that the estimation of preservation rates and times of speciation/extinction are switched off" (`../pyrate-command-reference/references/command-list.md`:18) — that sentence is written for `PyRate.py`; whether the same automatic switch happens inside `PyRateMCDD.py` is not stated anywhere.

Example file named by the docs: `Carnivores_MCDD.txt` (<https://github.com/dsilvestro/PyRate/blob/master/example_files/Carnivores_MCDD.txt>, `references/tutorial-4.md`:24). The tutorial prints **no rows** of it — see the `STRUCTURE` fixtures below.

## The MCDD command sequence the tutorial prints, in order

| # | Command line (verbatim) | What it does | Flags |
| --- | --- | --- | --- |
| 1 | `PyRateMCDD.py -d /example_files/Carnivores_MCDD.txt -n 10000000 -s 10000` | "you can run an analysis using" this — all clades at once (`references/tutorial-4.md`:32-36) | `-d` input table; `-n` = "the number of MCMC iterations"; `-s` = "the sampling frequency" (`references/tutorial-4.md`:36) |
| 2 | `PyRateMCDD.py -d /example_files/Carnivores_MCDD.txt -n 10000000 -s 10000 -c 0` | "will estimates the diversity dependent effects from all clades affecting the speciation and extinction of the first clade" (`references/tutorial-4.md`:40, sic) | `-c 0` = analyse clade 0 only, other clades still contribute diversity |

Both lines are at `references/tutorial-4.md`:34 and :38 (CN `references/tutorial-4-cn.md`:35, :39). They are the only two `PyRateMCDD.py` command lines in the corpus. Note the invocation form: the tutorial prints `PyRateMCDD.py` with neither `python` nor `./`, while Home's general pattern is `python PyRate.py path_to_input_file/file_name.py [commands]` (`../pyrate/references/home.md`:77) and the MBD lines are printed with `./`. The corpus never documents the correct form for `PyRateMCDD.py`.

About the numbers: `-n 10000000` and `-s 1000` are documented as the `PyRate.py` values/default (`../pyrate-command-reference/references/command-list.md`:56-58, :60-62 "Example: `-s 1000`  (default)"). The MCDD line passes `-s 10000` and the MBD option block lists `-s 5000` (`references/tutorial-4.md`:83). No default sampling frequency is documented for either program; do not call any of these three 'the default'. And `-n 10000000` here contradicts the sibling page's advice for the analogous no-preservation model (`../pyrate-continuous-covariates/references/tutorial-2.md`:112, "100,000 and 1 million") - see the last table of `Not documented in this wiki`.

## MBD: the multivariate birth-death model

**This skill carries MBD.** Some routing rows in this suite index the multivariate birth-death model under
`pyrate-trait-age-models`, and that skill's own text sends MCDD and MBD back here; whichever way you
arrived, every MBD command this corpus documents is listed below with the line it is printed on, so you
do not have to follow the routing to find it. MBD lives in one page only — `# The Multivariate Birth-Death
model (MBD)`, `references/tutorial-4.md`:44, mirrored here — and `grep -rl "PyRateMBD" ../*/references/`
hits only that one page, in its two homes (here and in `pyrate-trait-age-models`), i.e. four files (see
the overview), so this table is the whole
documented MBD command surface, and anything not in it is undocumented, not defaulted.

| What you run | Command / option exactly as printed | Citation |
| --- | --- | --- |
| the program | `PyRateMBD.py` ("The MBD model is implemented in the program `PyRateMBD.py`") | `references/tutorial-4.md`:53 |
| an MBD analysis | `./PyRateMBD.py -d /example_files/Ferns_SE.txt -var /example_files/predictors_MBDmodel -m 1` | `references/tutorial-4.md`:68 (CN `references/tutorial-4-cn.md`:69) |
| its results plotted | `./PyRateMBD.py -d /example_files/Ferns_SE.txt -var /example_files/predictors_MBDmodel -m 1 -plot Ferns_SE_0_lin_MBD.log` | `references/tutorial-4.md`:90 (CN `:91`) |
| the correlation model | `-m 0` exponential (default), `-m 1` linear | `references/tutorial-4.md`:70 |
| the predictors | `-var` "the path to a folder containing all predictors" | `references/tutorial-4.md`:71 (format at `:54`) |
| the plot input | `-plot <logfile>` | `references/tutorial-4.md`:88 |
| the seven "Additional options" | `-out outname`, `-rmDD 1`, `-minT 2.58`, `-maxT 23`, `-hsp 0`, `-n 10000000`, `-s 5000` | `references/tutorial-4.md`:77-83 (`-hsp` explained at `:85`) |
| MCDD, the other model here | `PyRateMCDD.py -d /example_files/Carnivores_MCDD.txt -n 10000000 -s 10000`, and the same with `-c 0` | `references/tutorial-4.md`:34 and `:38` |

`-b`, `-j`, `-A`, `-r` and `-tag` are **not** MBD options in this corpus: none of the five occurs anywhere
in `references/tutorial-4.md` (see the option-block note below and *Not documented in this wiki*).

| Item | Documented value | Citation |
| --- | --- | --- |
| Program | `PyRateMBD.py` | `references/tutorial-4.md`:53 |
| Rates | speciation and extinction as a function of multiple time-continuous variables; "The model assumes linear or exponential functions linking the temporal variation of birth-death rates with changes in one or more variables" | `references/tutorial-4.md`:46 |
| Parameters | "a correlation parameter is estimated for each variable (for speciation and extinction)" — the CN resolves the ambiguity: 会为每个变量各估计一个相关参数（物种形成与灭绝分别对应一个）, i.e. one per variable **per rate type** | `references/tutorial-4.md`:47; `references/tutorial-4-cn.md`:48 |
| Main input | the table of estimated origination/extinction times produced by `-ginput` (the docs link to tutorial 2 under the words "table with estimated speciation and extinction times") | `references/tutorial-4.md`:53 |
| Predictors | "It additionally requires a set of predictors provided as separate files in a single directory", each "a tab-separated table with a header and two columns for time before present and predictor values" | `references/tutorial-4.md`:53-54 |
| Shrinkage | a "**Horseshoe prior algorithm**" is "used to shrink around zero the correlation parameters, thus reducing the risk of over-parameterization and the need for explicit model testing" | `references/tutorial-4.md`:49 |
| Alternative prior | "**Alternatively, gamma hyper-priors** can be used to constrain the correlation parameters and prevent over-parameterization"; "This option should be preferred when testing only few variables (e.g. 2-4 correlates)." | `references/tutorial-4.md`:51 |
| Reference | (Lehtonen, Silvestro et al. 2017), <https://www.nature.com/articles/s41598-017-05263-7> | `references/tutorial-4.md`:46, 49 |
| Example predictors | <https://github.com/dsilvestro/PyRate/tree/master/example_files/predictors_MBDmodel> | `references/tutorial-4.md`:64 |

EN-vs-CN nuance worth knowing before you tell a user that MBD needs no model testing: the English sentence attaches *reducing* to both nouns ("thus reducing the risk of over-parameterization and the need for explicit model testing", `references/tutorial-4.md`:49), i.e. it reduces the need; the Chinese renders it as two coordinate results, 降低过度参数化的风险，同时也无需进行显式的模型检验 = *reduces the risk of over-parameterization and at the same time there is no need for explicit model testing* (`references/tutorial-4-cn.md`:50). The English is the upstream text; the stronger claim is the translation's reading, not the docs'.

### How MBD differs from single-correlate `PyRateContinuous.py`

| Question | `PyRateContinuous.py` | `PyRateMBD.py` (MBD) |
| --- | --- | --- |
| Number of time-continuous variables | one correlate at a time, or the clade's own diversity | "multiple time-continuous variables" (`references/tutorial-4.md`:46) |
| How the variable is supplied | `-c` with a single table of the variable and its times of change (`../pyrate-continuous-covariates/references/pyratecontinuous.md`:31-32; e.g. `-c temperature.txt`, `../pyrate-continuous-covariates/references/tutorial-2.md`:132) | `-var` with a **folder** of predictor files (`references/tutorial-4.md`:71) |
| Diversity dependence | switched on with `-DD`, "Use the `-DD` command to run **diversity dependence models**", where rates correlate linearly or exponentially "to the clade own diversity" (`../pyrate-continuous-covariates/references/pyratecontinuous.md`:29) | self-diversity dependence is on by default and removed with `-rmDD 1` (`references/tutorial-4.md`:78) |
| Correlation model flag | `-m -1` (no correlation, for marginal-likelihood comparisons), `-m 0` exponential (default), `-m 1` linear (`../pyrate-continuous-covariates/references/pyratecontinuous.md`:35-38) | `-m 0` exponential (default) and `-m 1` linear only (`references/tutorial-4.md`:70); no `-m -1` is documented for MBD |
| Priors on the correlation parameters | **not documented** in `pyratecontinuous.md` (`grep -n prior` on that mirror returns nothing); the only correlation-prior statements in this corpus are for the Covar model of `PyRate.py`: "The default prior on the correlation parameters is a normal distribution centered in 0 and with standard deviation = 1", changed with `-pC` (`../pyrate-trait-age-models/references/tutorial-4.md`:120) and the `-pC` entry "The Normal priors are centered in 0" with "Example: `-pC 1` (default)" (`../pyrate-command-reference/references/command-list.md`:187-188) — do not assume either applies to `PyRateContinuous.py` or to a single-correlate run | Horseshoe by default, or gamma hyper-priors with `-hsp 0` (`references/tutorial-4.md`:49, 85) |
| Model testing | marginal likelihoods via `-A 1` (`../pyrate-continuous-covariates/references/pyratecontinuous.md`:25-26) | horseshoe shrinkage, "thus reducing the risk of over-parameterization and the need for explicit model testing" (`references/tutorial-4.md`:49) |
| Wiki page | yes: `4.-PyRateContinuous` | none; `PyRateMBD.py` absent from the program list (`../pyrate/references/home.md`:28-60) |

### MBD options exactly as the "Additional options" block lists them

The block is the heading at `references/tutorial-4.md`:76 plus the seven option lines :77-83, with the `-hsp` explanation at :85 (CN: heading :77, options :78-84, explanation :86). Verbatim, in the printed order:

| Option | Doc wording (verbatim) | Notes |
| --- | --- | --- |
| `-out outname` | "add a string to output file names" | the `PyRate.py` equivalent: "Add tag to default stem name of output files" (`../pyrate-command-reference/references/command-list.md`:32-33) |
| `-rmDD 1` | "remove self-diversity dependence (by default included in the analysis)" | so self-diversity dependence is included by default; how MBD identifies the "self" predictor among the files in `-var` is not stated |
| `-minT 2.58` | "truncate at min time (e.g. at 2.58 Ma)" | unit Ma by the example only; no default documented |
| `-maxT 23` | "truncate at max time (e.g. at 23 Ma)" | as above |
| `-hsp 0` | "use Gamma hyper-priors instead of the Horseshoe prior" | expanded at `references/tutorial-4.md`:85: "this can be replaced with gamma hyper-priors on the precision parameters (1/variance) of the Gaussian priors on the correlation parameters. This is done adding the flag: `-hsp 0`" |
| `-n 10000000` | "MCMC iterations" | |
| `-s 5000` | "sampling frequency" | |

Plus the options that appear outside that block: the `-d` flag is printed only inside the two MBD command lines (`references/tutorial-4.md`:68, 90) - the prose at :53 and :66 describes "the input file and the path to all predictor files" without printing the flag letters; `-var` is printed in those same two lines and named in prose at :71; `-m` at :70; `-plot <logfile>` at :88. That is the **complete** documented MBD option set — `-b`, `-j`, `-A`, `-r` and `-tag` are documented for other programs only (none of the five occurs anywhere in `references/tutorial-4.md`).

The two MBD command lines the tutorial prints, in order:

```text
./PyRateMBD.py -d /example_files/Ferns_SE.txt -var /example_files/predictors_MBDmodel -m 1
./PyRateMBD.py -d /example_files/Ferns_SE.txt -var /example_files/predictors_MBDmodel -m 1 -plot Ferns_SE_0_lin_MBD.log
```

(`references/tutorial-4.md`:68 and :90; CN :69 and :91.) `-m 1` is explained as "specifies the type of correlation model, the options being `-m 0` for exponential correlations (default) and `-m 1` for linear correlations" (`references/tutorial-4.md`:70).

## Using MBD to run a multiple-clade diversity-dependent analysis

The sub-section is `references/tutorial-4.md`:73-74 (heading "### Using the MBD model to run multiple-clade diversity dependent analysis"; CN `references/tutorial-4-cn.md`:74-75). Its entire content is two sentences: "To use the MBD model in a multiple-clade diversity dependence analysis you should provide the diversity trajectories of all clades as predictors." and "Diversity trajectories files in the correct format can be generated using PyRate's `-ltt`" - the word "command" that follows is a hyperlink to tutorial 2, not part of the sentence's plain text (`references/tutorial-4.md`:74).

So the documented route is: previous PyRate run → `-ginput` table per clade → `-ltt` → the diversity-trajectory table becomes one predictor file per clade → all of them in one folder → `-var`. The `-ltt` machinery lives in `../pyrate-continuous-covariates/references/tutorial-2.md`:65-88: `python PyRate.py -d Canidae_1_G_se_est.txt -ltt 1` (line 68) "generates 3 output files: 1) a **pdf file** with the LTT plot, 2) a **table with the estimated diversity trajectory**, and 3) the **R script** used to generate the plot" (line 70), and `-grid_plot 0.1` sets the bin size of the counts (lines 83-86). What the corpus does **not** document: which `-ltt` value gives the format MBD wants (tutorial 2 prints `-ltt 1`, `-ltt 2` - "you obtain a similar plot but with log10-transformed diversity" - and `-ltt 3` - "LTT plots from each replicate are shown as individual lines", lines 68-81, and attaches the trajectory table to the `-ltt 1` call, but never says which of the three is the MBD predictor format), the column layout of that trajectory table, how to rename/split the tables into one file per clade, or whether the MCDD clade column must be present in the MBD `-d` table for MBD to know the clades. None of it is stated anywhere in this corpus — see the `Not documented in this wiki` table.

## Summarizing the results

`references/tutorial-4.md`:87-92 (CN :88-93). Documented facts:

| Item | Wording | Citation |
| --- | --- | --- |
| What `-plot` produces | "the marginal speciation and extinction rates through time" plotted "as predicted by the MBD model" (the docs print two spaces between those spans) | `references/tutorial-4.md`:88 |
| What you must re-supply | "the input data, the directory containing all predictors, and the correlation model (linear or exponential) must be specified" | `references/tutorial-4.md`:88 |
| Extra output under Horseshoe | "the `plot` function also computes the shrinkage weights (_Wl_ and _Wm_ for speciation and extinction, respectively) for all predictors. The shrinkage weights quantify the statistical support for each correlation factor." | `references/tutorial-4.md`:92 |
| Parameter names in the logs | "The correlation parameters are indicated by _Gl_ and _Gm_ in the log files and their posterior estimate is also indicated in the plots produced by the `-plot` command" | `references/tutorial-4.md`:92 |
| Reading the logs directly | "they can also easily be obtained by opening the _mcmc.log_ file in" Tracer (<http://tree.bio.ed.ac.uk/software/tracer/>) | `references/tutorial-4.md`:92 |

Interpretation of `Gl`/`Gm` is **not** given in this tutorial. The rule lives in the sibling page: "When these parameters are significantly different from 0 (based on their 95% HPD) we consider the correlation as significantly positive or negative (depending on whether *G* >> 0 or *G* << 0)" (`../pyrate-continuous-covariates/references/tutorial-2.md`:115) — stated for `PyRateContinuous`, so applying it to MBD logs is by inference from the identical parameter naming, not a documented statement.

## The `Ferns_MBD_short_run.png` figure

`references/tutorial-4.md`:94 embeds it as an image link whose target is written relative to `references/`, so from this skill directory the file is `../assets/images/Ferns_MBD_short_run.png` (the CN mirror embeds the same file at `references/tutorial-4-cn.md`:95) - it is the last element of the MBD section, between the shrinkage paragraph (:92) and the Covar heading (:98). The corpus gives **no caption and no interpretation**: the only doc statement about it is that `-plot` gives "the marginal speciation and extinction rates through time" "as predicted by the MBD model" (`references/tutorial-4.md`:88). Everything below is my reading of that PNG, labelled as such:

- two panels, `Speciation rates – Combined effects` (blue) and `Extinction rates – Combined effects` (red), each subtitled `Exponential correlations`; x-axis Time (Ma) from about -410 to 0, y-axis rates 0.00 to 0.15 plus.
- each panel draws a swarm of thin pale individual-sample lines, a heavy coloured line (the posterior summary) and a wide pale credible band around it; the band is much wider in the deep-time half than near the present, and there is a sharp extinction peak at about 250 Ma that reaches ~0.12 while the band extends past the top of the axis.
- what the *short run* in the file name demonstrates, by inference: an MBD analysis run well below the `-n 10000000` of `references/tutorial-4.md`:82, whose visible result is exactly the broad, ragged uncertainty bands — i.e. a short MBD run still produces the full two-panel marginal-RTT output, but with wide intervals. The docs never say this, and never say which file the figure was plotted from.

Two inconsistencies to carry forward rather than resolve: the figure is titled `Exponential correlations` while both printed MBD command lines use `-m 1` (linear) (`references/tutorial-4.md`:68, 90); and the printed log name `Ferns_SE_0_lin_MBD.log` pairs `_0_` with `lin`, whereas the sibling tutorial's log `Canidae_1_G_se_est_DD_0_exp.log` pairs `_0_` with `exp` under `-m 0` (`../pyrate-continuous-covariates/references/tutorial-2.md`:122). Do not derive your own output-file name from either example; use `-out` (`references/tutorial-4.md`:77).

## Worked example

```sh
# <suite> = the PyRate-skills/ root. Run in a scratch directory.
# Interpreter: Python 2.6-2.7 only ("Python 3.x is currently not supported", ../pyrate/references/home.md:69)
# pyrate_lib must sit in the same directory as the program (../pyrate/references/home.md:61)
mkdir -p mcdd_run/predictors && cd mcdd_run

# 1. MCDD input table: 4 tab-separated columns, clade numbering from 0 (references/tutorial-4.md:24-30).
#    The fixture is a STRUCTURE placeholder - the tutorial prints the columns but no rows.
#    Its leading '#' lines are provenance only; strip them before handing the file to a program.
cp <suite>/assets/files/mcdd-input-table-STRUCTURE.txt Carnivores_MCDD.txt
grep -v '^#' Carnivores_MCDD.txt > Carnivores_MCDD_data.txt                # the table the program would read
column -t Carnivores_MCDD_data.txt                                         # clade | species | time_of_origin | time_of_extinction

# 2. the two MCDD command lines the tutorial prints, in order (references/tutorial-4.md:34, 38)
#    (illustrative only: the placeholder times are invented, so no result means anything)
PyRateMCDD.py -d Carnivores_MCDD_data.txt -n 10000000 -s 10000
PyRateMCDD.py -d Carnivores_MCDD_data.txt -n 10000000 -s 10000 -c 0        # clade 0 only, other clades still count

#    with replicates: the 5th/6th columns are the second origination/extinction estimates
#    (../pyrate-command-reference/references/command-list.md:18; built upstream by -tag/-resample,
#    ../pyrate-continuous-covariates/references/tutorial-2.md:45-57); how MCDD picks one is undocumented
cp <suite>/assets/files/mcdd-input-table-replicates-STRUCTURE.txt Carnivores_MCDD_rep2.txt

# 3. MBD predictors: one tab-separated file per predictor, all in ONE directory
#    (references/tutorial-4.md:53-54, 71). The fixture is the 5-row example the docs print at :56-62
#    and is byte-clean (no '#' lines), so it can be dropped straight into the -var folder.
cp <suite>/assets/files/mcdd-predictor-table-EXCERPT.txt predictors/clade0_diversity.txt
cp <suite>/assets/files/mcdd-predictor-table-EXCERPT.txt predictors/clade1_diversity.txt  # copied twice only to show the folder layout
head -2 predictors/clade0_diversity.txt                                                   # time<TAB>predictor header row

# 4. MBD main input = the estimated origination/extinction table (-ginput output; references/tutorial-4.md:53)
grep -v '^#' <suite>/assets/files/mcdd-input-table-STRUCTURE.txt > Ferns_SE.txt   # placeholder with the documented layout

# 5. the two MBD command lines the tutorial prints, in order (references/tutorial-4.md:68, 90)
./PyRateMBD.py -d Ferns_SE.txt -var predictors -m 1
./PyRateMBD.py -d Ferns_SE.txt -var predictors -m 1 -plot Ferns_SE_0_lin_MBD.log
#    replace the .log name with the file your run actually wrote - the naming convention is not documented
```

## Pitfalls

- **The typos in this section are in the source and are load-bearing if you grep for them.** `references/tutorial-4.md`:32 "One the input file is ready" (for 'Once'), :36 "a single clade at time" (missing 'a'), :40 'will estimates', :42 the paragraph begins with a lowercase "the MCDD model implements", :46 'The MBD model allow'. They are prose, not syntax, so they never affect a run - but they must be kept verbatim when quoting, and they break naive greps for 'Once the input file'.
- **`-c 0` is neither *the first predictor* nor *no clade*.** It selects clade 0 and the run still includes every other clade's diversity (`references/tutorial-4.md`:36, 40). Looping `-c` over clade indices gives one analysis per focal clade; the docs never say the results are comparable across those runs.
- **Do not mix the two programs' flag sets.** `-rmDD`, `-hsp`, `-minT`, `-maxT` are documented only inside the "Additional options" block (`references/tutorial-4.md`:76-85) and `-var` only in the MBD run/plot lines and the sentence at :71 (`references/tutorial-4.md`:68, 71, 90); corpus-wide, `-rmDD`/`-hsp`/`-minT`/`-maxT` appear nowhere outside tutorial 4. There is no evidence they exist in `PyRateMCDD.py`. Conversely `-c <clade>` is documented only for MCDD.
- **The MCDD/MBD input tables are not occurrence tables.** They carry estimated origination/extinction times (`references/tutorial-4.md`:28, 53), so the preservation model, `-b` burn-in choice and the quality of the upstream run all propagate into the rate estimates; `-ltt`/`-ginput` provenance is covered by `pyrate-continuous-covariates` and `pyrate-summarize-results`.
- **Predictor rescaling is undocumented for MBD.** `PyRateContinuous` states "The time-continuous variable is by default rescaled so that its range of values equals 1. It is additionally shifted to equal 0 at the present." and "The rescaling of the time-continuous variable can be changed using the flag `-r`" (`../pyrate-continuous-covariates/references/tutorial-2.md`:136). Nothing in `references/tutorial-4.md` says MBD does the same, so never assume `Gl`/`Gm` from an MBD log are on the same scale as a `PyRateContinuous` one.
- **A `-var` folder is not a place to keep unrelated files.** "The flag `-var` is used to specify the path to a folder containing all predictors" (`references/tutorial-4.md`:71) and no exclusion option is documented, so anything else in that folder is unaccounted for.
- **The tutorial's own paths are illustrative.** `/example_files/Carnivores_MCDD.txt` and `/example_files/predictors_MBDmodel` start with `/` as printed (`references/tutorial-4.md`:34, 38, 68, 90); they are not valid paths on your machine.
- **Grepping the corpus for "MCDD" throws a false positive.** Home's `PyRateDES.py` paragraph ends "The MCDD model is described here:" (`../pyrate/references/home.md`:54) while the reference printed under it is the DES paper (`../pyrate/references/home.md`:56) - a source typo for "The DES model". It is not MCDD documentation; the MCDD entry is `../pyrate/references/home.md`:46-49.

## Not documented in this wiki

The PyRateMCDD wiki page is under construction (`../pyrate-command-reference/references/command-list.md`:18; `../pyrate-continuous-covariates/references/pyratecontinuous.md`:11) and Home's command list is "in preparation" (`../pyrate/references/home.md`:47). That means **this skill plus `references/tutorial-4.md`:23-94 is the entire *method and command* documentation of MCDD in the corpus** — 72 lines of prose, two command lines, and one table description. Everything else the corpus says about MCDD is Home's one-sentence model description (`../pyrate/references/home.md`:47) and three copies of the input-table sentence (`../pyrate-command-reference/references/command-list.md`:18, `../pyrate-continuous-covariates/references/pyratecontinuous.md`:11, `../pyrate-continuous-covariates/references/tutorial-2.md`:24), none of which lists an option. The practical implication for anyone relying on it: you cannot verify an MCDD command line against a reference, only against the two lines printed in this skill's MCDD section; an option you have not seen printed in tutorial 4 must be treated as unsupported, and any MCDD result you report has to carry the tutorial section as its method citation because there is no wiki page to cite. Anyone relying on MCDD is relying on a tutorial section whose own table of contents does not even list it (`references/tutorial-4.md`:16-18 lists Multivariate Birth-Death models, Trait-dependent diversification, Age dependent extinction; the anchor at :16 still reads `#multivariate-birth-death-models-this-tutorial-is-work-in-progress`). The questions below are answered nowhere in this corpus; do not fill them in from `PyRate.py` habits.

| Unanswered question | Why you must not fill it in |
| --- | --- |
| How does `PyRateMCDD.py` choose among replicate columns — does it accept `-j`? | building the columns is documented (`-tag`/`-resample`, `../pyrate-continuous-covariates/references/tutorial-2.md`:45-57) and `-j` is the documented selector for PyRate (`../pyrate-command-reference/references/command-list.md`:18, :27-30), but no MCDD command line shows `-j` and tutorial 4 never mentions a selector (`references/tutorial-4.md`:30); guessing it may silently analyse replicate 1 |
| What files does `PyRateMCDD.py` / `PyRateMBD.py` write, and what are they named? | neither page lists outputs; the only printed log name, `Ferns_SE_0_lin_MBD.log`, is internally inconsistent with `-m 1` (see the figure section) |
| The full option list and defaults of both programs (`-b`? `-A`? `-thread`? `-p`?) | "A detailed command list is in preparation" (`../pyrate/references/home.md`:47); `PyRateMBD.py` is absent from the wiki program list entirely (`../pyrate/references/home.md`:28-60) |
| Is `-rmDD` available in `PyRateMCDD.py`, and how does MBD know which predictor is the focal clade's own diversity? | `-rmDD 1` appears only in the MBD options block (`references/tutorial-4.md`:78); the self-diversity term is never tied to a file name, a column, or `-c` |
| Can MBD run a constant-rate / no-correlation model for comparison (`-m -1`)? | `references/tutorial-4.md`:70 documents only `-m 0` and `-m 1`; `-m -1` exists only for `PyRateContinuous` (`../pyrate-continuous-covariates/references/pyratecontinuous.md`:36, used for model comparisons at `../pyrate-continuous-covariates/references/tutorial-2.md`:108) |
| Does the MCDD clade column have to be filled in the MBD `-d` table too? | the clade column is described for MCDD and `-d` generally (`references/tutorial-4.md`:26; `../pyrate-command-reference/references/command-list.md`:18); the MBD section never mentions clades except via predictors (`references/tutorial-4.md`:74) |
| Column 2 of the table: species name or number? | "a species identifier" (`references/tutorial-4.md`:27) vs "a species numeric identifier" (`../pyrate-command-reference/references/command-list.md`:18, `../pyrate-continuous-covariates/references/pyratecontinuous.md`:11, `../pyrate-continuous-covariates/references/tutorial-2.md`:24) |
| Units/behaviour of `-minT` and `-maxT`, their interaction, and what happens to lineages crossing the cut | one line each in `references/tutorial-4.md`:79-80 with "e.g." values only |
| Which `-ltt` option produces the diversity-trajectory table, and its exact layout, for use as MBD predictors | `references/tutorial-4.md`:74 points at `-ltt`; the layout is only described as "a **table with the estimated diversity trajectory**" (`../pyrate-continuous-covariates/references/tutorial-2.md`:70) |
| How many predictors MBD can take, and whether predictor time axes must match each other and the data | `references/tutorial-4.md`:51 mentions "2-4 correlates" only as prior advice; no limit or alignment rule is stated |
| Convergence criteria specific to MCDD/MBD (ESS, burn-in, run length) | `references/tutorial-4.md` gives `-n`/`-s` numbers only; the tuning guidance in this corpus belongs to `PyRate.py` (`../pyrate-mcmc-tuning/references/tutorial-6.md`). The nearest documented statement is for `PyRateContinuous` - "setting the number of MCMC iterations between 100,000 and 1 million, will be sufficient for most data sets" (`../pyrate-continuous-covariates/references/tutorial-2.md`:112) - and it is flatly at odds with the `-n 10000000` printed in both MCDD and MBD blocks (`references/tutorial-4.md`:34, 38, 82). Do not transfer the 100k-1M advice to MCDD/MBD, and do not treat 10M as validated either |
| The full bibliographic entry for the MBD paper | only "(Lehtonen, Silvestro et al. 2017)" + URL (`references/tutorial-4.md`:46); the comparison paper for MCDD-vs-MBD performance is an abstract link (`references/tutorial-4.md`:42) |

## Related skills

- `pyrate-continuous-covariates` — owns `PyRateContinuous.py`: the single-correlate diversity-dependence model `-DD`, the `-c` correlate-table flag, `-m -1/0/1`, `-ginput` including the `-tag`/`-resample` ways of building replicate columns, and tutorial 2 including the `-ltt` plots that produce MBD predictors. Start here for anything about one correlate.
- `pyrate-command-reference` — owns `command-list.md`: the `-d` table format (including the clade-assignment column and replicate columns), `-j`, `-n`, `-s`, `-b`, `-out`, `-pC`, `-fixSE`.
- `pyrate-trait-age-models` — owns the rest of tutorial 4: Covar trait-dependent models (`-trait_file`, `-mCov`, `-logT`, `-pC`), ADE (`-ADE`, `-filter`) and the BDC model. Do not duplicate those here.
- `pyrate-summarize-results` — owns `_mcmc.log` contents, Tracer inspection, `-plot`/`-mProb`/`-tag` for `PyRate.py` results.
- `pyrate-bd-analysis` — the upstream PyRate birth-death analysis whose output log feeds `-ginput` and hence every MCDD/MBD input table.
- `pyrate-input-file` — occurrence tables (`Species Status MinT MaxT [Trait]`, `../pyrate-input-file/references/preparing-input-file.md`:16), the `*_PyRate.py` structure; a different format from the MCDD table.
- `pyrate-mcmc-tuning` — owns tutorial 6, the advanced `PyRate.py` tuning settings (`-fast_burnin`, `-multiR`, `-tT`, `-nT`, `-tQ`, `-tR`, `-tS`, `-fS`, `-tC`, `-fU`, `-fR`), and carries a copy of `command-list.md` for `-n`, `-s`, `-b`, `-thread`. Nothing there is documented for MCDD/MBD.
- `pyrate-installation` — Python 2.6-2.7 requirement, virtual environment, `pyrate_lib` placement.
- `pyrate-des` — the DES model, the other documented route to an externally driven process: area-specific covariates such as temperature time-series per area (`../pyrate-des/references/tutorial-5.md`:254).
- `pyrate-bdnn` — the neural-network rate models, the other route to flexible rate-through-time functions.
- `pyrate` — router: Home program list and the tutorials index (which files MCDD/MBD under tutorial 4, `../pyrate/references/tutorials-index.md`:49-50).

## Resources

| File | What's in it | Load when |
| --- | --- | --- |
| `references/tutorial-4.md` | The whole tutorial 4: MCDD (lines 23-42), MBD (44-71), MBD-for-multiple-clades (73-74), Additional options (76-85), Summarizing the results (87-94), then Covar/ADE/BDC (98-171) | Any MCDD or MBD question — it is the only method-and-command documentation that exists anywhere in the corpus |
| `references/tutorial-4-cn.md` | Line-for-line Simplified-Chinese translation (offset +1 line: MCDD 24-43, MBD 45-72, options 77-84, results 88-95) | Whenever the English is ambiguous: it settles the per-variable-per-rate correlation count (:48) and the within/between-clade wording (:37), but states the model-testing point more strongly (:50) |
| `../pyrate-command-reference/references/command-list.md` | The `-d` table format with the clade-assignment column and the "Wiki page for PyRateMCDD is under construction" note (line 18), `-j` (27-30), `-out` (32-35), `-n` (56-58), `-s` (60-62), `-pC` (186-188) | Building or debugging the MCDD/MBD input table; replicate selection |
| `../pyrate-continuous-covariates/references/pyratecontinuous.md` | `PyRateContinuous` options: `-ginput` (13-18), `-d` (22), `-A` (25-26), `-DD` (28-29), `-c` (31-32), `-m -1/0/1` (34-38); the same input-table sentence including the under-construction note (11) | Comparing MBD against the single-correlate program; flag-collision checks |
| `../pyrate-continuous-covariates/references/tutorial-2.md` | The third variant of the origin/extinction table sentence (24), `-ginput` workflow (27-35), `-tag` and `-resample` replicate columns (45-57), `-ltt` diversity-trajectory outputs (65-88), `-DD` runs (100-106), `Gl`/`Gm` significance rule (115), predictor rescaling and `-r` (136) | Producing the MCDD/MBD input table and the per-clade predictor files |
| `../pyrate/references/home.md` | Program list: `PyRateMCDD.py` and "A detailed command list is in preparation" (46-47), the full PNAS 2015 citation (49), the DES paragraph that mislabels itself "The MCDD model is described here" (54), `pyrate_lib` placement (60-61), Python version rule (69), invocation pattern (77) | Anything about how to invoke the programs, and what is *not* documented |
| `../pyrate/references/tutorials-index.md` | Index entries routing multiple-clade diversity dependence and the multivariate BD model to tutorial 4 (49-50) and single-clade diversity dependence to tutorial 2 (46) | Deciding which tutorial owns a question |
| `../assets/images/Ferns_MBD_short_run.png` | The MBD short-run two-panel marginal RTT figure embedded at `references/tutorial-4.md`:94 | Checking what a short MBD run looks like |

```sh
# run these from this skill directory (all verified to match)
grep -n "PyRateMCDD.py -d" references/tutorial-4.md
grep -n -- "-rmDD\|-hsp 0\|-var" references/tutorial-4.md
grep -n "the latter might be preferable" references/tutorial-4.md
grep -n "diversity trajectories" references/tutorial-4.md
grep -n "shrinkage weights" references/tutorial-4.md
grep -rn "clade assignment of species" ../*/references/   # the clade column, as stated on all three pages that describe it
grep -rln "under construction" ../*/references/
grep -rl "PyRateMBD" ../*/references/
```

## Runnable fixtures (`../assets/files/`)

| File | Run it? | What it makes concrete |
| --- | --- | --- |
| `../assets/files/mcdd-tutorial-commands.sh` | no — reference only | all four MCDD/MBD command lines tutorial 4 prints, in printed order, with the command text reproduced exactly (including the `/example_files/` paths and the `./` prefixes); only the docs' enclosing backticks and the trailing space after the `-c 0` line are dropped, so it is a runnable shell file rather than a byte-for-byte copy of the markdown lines; provenance header inside (source `pyrate_tutorial_4.md` lines 26, 30, 60, 82 = mirror lines 34, 38, 68, 90) |
| `../assets/files/mcdd-input-table-STRUCTURE.txt` | yes, after `grep -v '^#'` (5 provenance comment lines) | the 4-column tab-separated MCDD/`-d` table: `clade`, species id, time of origin, time of extinction, clade numbering 0/1/2. `derived:` — the docs describe the columns (`references/tutorial-4.md`:24-30) but print no rows, so the values are illustrative placeholders and the header text is invented (only "the first line containing column headers" is documented, `../pyrate-command-reference/references/command-list.md`:18) |
| `../assets/files/mcdd-input-table-replicates-STRUCTURE.txt` | yes, after `grep -v '^#'` (4 provenance comment lines) | the same table extended to 6 columns, 5th = second origination estimate, 6th = second extinction estimate (`references/tutorial-4.md`:30; `../pyrate-command-reference/references/command-list.md`:18). `derived:` placeholders as above |
| `../assets/files/mcdd-predictor-table-EXCERPT.txt` | yes (drop into a `-var` folder) | the predictor file format, byte-clean (no comment header, because a `#` line would break the tab-separated reader): header `time	predictor` plus the five rows the docs print at `references/tutorial-4.md`:56-62 (`0 0.06`, `1 0.0665`, `2 0.073`, `3 0.0795`, `4 0.086`). `derived:` only in that the doc shows it as a Markdown table; the values are verbatim and the file is truncated to what the docs print, hence `EXCERPT` |
