---
name: pyrate-rjmcmc
description: "Reversible jump MCMC rate-shift analyses in PyRate (`-A 4`): setting them up for occurrence data (`-A 4 -mHPP -mG`) and for fixed origination/extinction times (`-d Canidae_1_G_se_est.txt -A 4`); the uniform shift-time prior and `-min_dt`; the four RJMCMC outputs (sum.txt, mcmc.log with k_birth/k_death/root_age/tot_length/q_rate/alpha/PP_lik/BD_lik, sp_rates.log, ex_rates.log) and the variable column count; reading the number of shifts with `-mProb` and `-b` burnin; plotting rates through time and shift histograms with `-plotRJ`, `-tag`, `-grid_plot`, `-root_plot`, `-min_age_plot`, `-logT`, `-log_marginal_rates`; merging replicates with `-combLogRJ`, `-resample`, `-combLog`, `-col_tag`; large datasets with `-se_gibbs`, `-fU`, `-fQ`, `-tQ`; bounding origination/extinction times with `-bound_se`."
---

# Reversible jump MCMC (`-A 4`): number and placement of rate shifts

## Overview

PyRate estimates how many speciation/extinction rate shifts a fossil record supports and where they fall in
time. Tutorial #3 presents **RJMCMC (`-A 4`)** as the newer route: it "uses RJMCMC (Green 1995) instead of
BDMCMC", the latter being "available through the command `-A 2`", and "simulations show that it is more
accurate than BDMCMC" (`references/tutorial-3.md:30`; the Chinese twin `references/tutorial-3-cn.md:31` says
the same). "An analysis with RJMCMC is set up using the command `-A 4`" (`references/tutorial-3.md:32`), for
occurrence data (`references/tutorial-3.md:35`) and equally for data whose origination/extinction times are
already fixed and passed with `-d` (`references/tutorial-3.md:39`). Under `-A 4` both the **number** and the
**placement** of shifts are sampled; the alternatives fix one of them — `-A 0` runs "an MCMC for parameter
estimation, i.e. with fixed number of shifts in the birth-death model" (`references/command-list.md:47`) with
the counts set by `-mL`/`-mM` (`references/command-list.md:111-117`) or their ages set by `-fixShift`
(`references/command-list.md:123-125`). That the RJMCMC estimates the "number and temporal placement of
shifts" is stated on tutorial #1 (`../pyrate-bd-analysis/references/tutorial-1.md:167`).

The single riskiest assumption in this skill: **that you know which algorithm your log file came from.** The
corpus contradicts itself about the default. `references/command-list.md:52` binds `(default)` to `-A 2`
(also in Chinese, `references/command-list-cn.md:53`), while
`../pyrate-bd-analysis/references/tutorial-1.md:167` calls "the RJMCMC algorithm (default)" and line 174 of
the same page says "using `-A 4` (or omitting the flag) will set the algorithm to RJMCMC". Both output sets
differ (`sp_rates.log`/`ex_rates.log` vs `marginal_rates.log`), so always pass `-A 4` explicitly and confirm
against `*_sum.txt`, the "Text file providing the complete list of settings used in the analysis"
(`references/tutorial-3.md:52-53`).

## The eight things that break a run

| # | What happens | Consequence | Wiki wording (`references/…`) |
| --- | --- | --- | --- |
| 1 | `-A` omitted, hoping for RJMCMC | The command list calls `-A 2` (BDMCMC) the default, tutorial #1 calls RJMCMC the default; the two answers produce different log files, and the pages further disagree on whether the `k_birth`/`k_death` shift-count columns are logged at all under RJMCMC (see the conflict note below). What neither page attaches to any `-A` value is a default *preservation* model — that statement lives in the preservation section, not in `-A` | `references/command-list.md:52` "Example: `-A 2`  (default)" vs `../pyrate-bd-analysis/references/tutorial-1.md:174` "(or omitting the flag) will set the algorithm to RJMCMC"; `references/command-list.md:88` "Note that the NHPP is  used unless differently specified." |
| 2 | `-plotRJ` given the log *files* | The function takes a directory; a file argument is not what the page documents | `references/tutorial-3.md:77` "**this command requires the path to the log files (i.e. not the files themselves)**" |
| 3 | `-plotRJ` on a run set up with `-log_marginal_rates 1` | No shift-placement histogram at all — the old format is for `-plot` only | `references/tutorial-3.md:60` "it cannot be analyzed using the command `plotRJ`, to assess the temporal placement of significant rate shifts" (the mirror drops the leading `-` in `plotRJ`) |
| 4 | `-min_dt` changed for the run but not for the plot — or set very small | The plot is computed under a prior the analysis did not use; small values destabilise the run | `references/tutorial-3.md:89` "If the **prior on the minimum duration between time bins**  was changed from its default in the analysis, this hsould be also specified when plotting the results"; `references/tutorial-3.md:48` "setting this parameter to small values can lead to instable results, especially for small datasets" |
| 5 | Counting `-b` in the wrong unit | `references/tutorial-3.md:67` counts samples ("the first 200 samples will be removed (i.e. the first 200,000 iterations, if the sampling frequency was set to 1,000)"), `references/command-list.md:69` says "number of iterations to be discarded", and `references/command-list.md:72` counts samples again — so state the unit next to every `-b` you write | see left; identical inconsistency in `references/command-list-cn.md:70-73` |
| 6 | Reaching for `-M`, `-B`, `-T`, `-S` to make RJMCMC explore more shifts | Each of the four is scoped "used only when running BDMCMC analysis for parameter estimation (i.e. with `-A 2`)"; the corpus documents no RJMCMC counterpart | `references/command-list.md:214,218,222,226` |
| 7 | `-se_gibbs` with no preservation flag — the undeclared default is NHPP, not one of the two models the section admits — or expecting sharp shifts | The Gibbs option is restricted, and with RJMCMC it can blur exactly the signal you came for | `references/tutorial-3.md:122` "This model only works for preservation models based on homogenous or time-variable Poisson processes (HPP or TPP)."; `references/command-list.md:88` "Note that the NHPP is  used unless differently specified." (double space in the source) and `../pyrate-bd-analysis/references/tutorial-1.md:122` "By default, PyRate assumes an NHPP model"; `references/tutorial-3.md:123` "This model combined with RJMCMC might lead to \"smoothed\" speciation and extinction rates through time." (straight quotes in the mirror) |
| 8 | `-bound_se` table built with `min` before `max` | The bounds apply to the wrong side of each time; by the printed header, column 2 is the `max_ts` bound | `references/tutorial-3.md:129` gives the prose column order (earliest/latest origination, earliest/latest extinction) without ever using the tokens; the header `references/tutorial-3.md:134` prints `max_ts` before `min_ts`; the `max_ts`/`min_ts`/`min_te` tokens appear in prose only at `references/tutorial-3.md:131` |

## Why RJMCMC, and what the alternatives fix in place

| Command | What is estimated / fixed | Citation |
| --- | --- | --- |
| `-A 4` | number of shifts, shift times, speciation/extinction rates between shifts — "An analysis with RJMCMC is set up using the command `-A 4`" | `references/tutorial-3.md:32`; estimation target per `../pyrate-bd-analysis/references/tutorial-1.md:167` and the `-A 2` entry (`references/command-list.md:51`) that RJMCMC replaces (`references/tutorial-3.md:30`) |
| `-A 2` | same target, older algorithm — "run a BDMCMC analysis" that estimates "the number of rate shifts in the birth-death process, their temporal placement and the speciation and extinction rates between" shifts | `references/command-list.md:51` |
| `-A 0` | "MCMC for parameter estimation, i.e. with fixed number of shifts"; shift count comes from `-mL`/`-mM` (e.g. `-mL 2` = "set 2 speciation rates and 1 rate shift") | `references/command-list.md:47,111-117` |
| `-A 1` | thermodynamic integration for a marginal likelihood ("*_marginal_likelihood.txt"), i.e. model comparison across a *given* number of shifts, not shift search | `references/command-list.md:49` |
| `-A 3` | "Dirichlet Process Prior on the speciation and extinction rates within fixed time bins. Warning: this function is currently still being tested." | `references/command-list.md:54` |
| `-fixShift` | "the number and temporal placement of the rate shifts is fixed and set identical for both speciation and extinction"; also switches the rate priors to half-Cauchy | `references/command-list.md:124` |

Coverage note worth repeating: **`-A 4` is not in the command list at all.** `grep -n -- '-A 4'
references/command-list.md references/command-list-cn.md` returns nothing — the `-A` entry stops at `-A 3`
(`references/command-list.md:46-54`). The same holds for `-plotRJ`, `-combLogRJ`, `-combLog`, `-col_tag`, `-resample`, `-min_dt`, `-se_gibbs`,
`-bound_se`, `-grid_plot`, `-root_plot`, `-min_age_plot` and
`-log_marginal_rates`: zero hits in
`references/command-list.md` and in `references/command-list-cn.md`. `-mProb` occurs there once only, as a
hyperlink inside the `-b` entry (`references/command-list.md:69`), never as an entry of its own. Outside the
command list, tutorial #3 is the *sole* page of this corpus carrying `-plotRJ`, `-combLogRJ`, `-col_tag`,
`-min_dt`, `-se_gibbs`, `-bound_se` and `-log_marginal_rates` (verified: `grep -rlF` each flag over
`../pyrate-*/references/*.md` matches only `tutorial-3.md` and `tutorial-3-cn.md`); the rest have sibling
appearances — `-A 4` also occurs in tutorial #1 (`../pyrate-bd-analysis/references/tutorial-1.md:174,265-276`),
summarize-results (`../pyrate-summarize-results/references/summarize-results.md:25,36`) and the BDNN tutorial
(`../pyrate-bdnn/references/tutorial-bdnn.md:472`); `-combLog` in tutorial #1
(`../pyrate-bd-analysis/references/tutorial-1.md:227`); `-resample` with `-ginput` in tutorial #2
(`../pyrate-summarize-results/references/tutorial-2.md:51-61`); `-grid_plot`, `-root_plot` and `-min_age_plot`
in the `-plot` sections of tutorials #1/#2 and the summarize-results page.

## The rate-shift prior (`-min_dt`)

"By default the RJMCMC assumes a uniform prior on the time of rate shifts, with the constraint that a time
bin cannot be smaller than 1 time unit (e.g. 1 myr)" (`references/tutorial-3.md:44`, CN
`references/tutorial-3-cn.md:45`). The one knob is `-min_dt`:

| Command | Effect | Citation |
| --- | --- | --- |
| `python PyRate.py -d Canidae_1_G_se_est.txt -A 4 -min_dt 0.5` | "allowes rate shifts to be separated by at least 0.5 myr" | `references/tutorial-3.md:46,48` |
| `-min_dt 0.5` repeated on `-plotRJ` | keeps the plotted prior equal to the analysed one | `references/tutorial-3.md:89-91` |

Two things the page never settles: (a) it describes `-min_dt` both as a minimum **bin duration**
(`references/tutorial-3.md:44`) and as a minimum **separation between shifts**
(`references/tutorial-3.md:48`) — the Chinese twin carries the same double wording
(`references/tutorial-3-cn.md:45` "时间分箱允许的最小时长" vs `references/tutorial-3-cn.md:49` "各速率转变
之间至少相隔 0.5 myr"), so this is an upstream ambiguity, not a translation artefact; (b) "1 time unit" is
illustrated as "1 myr" (`references/tutorial-3.md:44`) but no page defines the unit of the input ages here.

## The exact setup tutorial #3 prints

Every command line the page prints, in page order, with the numbers it uses. The same sequence, verbatim and
annotated, is in `../assets/files/rjmcmc-commands.sh`.

| Line | Command (verbatim) | What the page says it is for |
| --- | --- | --- |
| `references/tutorial-3.md:35` | `python PyRate.py .../Canis_pbdb_data_PyRate.py -A 4 -mHPP -mG` | RJMCMC "available both for occurrence data" |
| `references/tutorial-3.md:37,39` | `python PyRate.py -d Canidae_1_G_se_est.txt -A 4` | "for data sets with fixed times of origination and extinction" (`:37`, which also cross-references tutorial #2); command at `:39` |
| `references/tutorial-3.md:46` | `python PyRate.py -d Canidae_1_G_se_est.txt -A 4 -min_dt 0.5` | change the shift-time prior |
| `references/tutorial-3.md:65` | `python PyRate.py -mProb .../Canis_pbdb_data_mcmc.log -b 200` | model probabilities by shift number; `-b 200` = first 200 samples = "the first 200,000 iterations, if the sampling frequency was set to 1,000" (`:67`) |
| `references/tutorial-3.md:73` | `python PyRate.py -plotRJ .../path_to_log_files/ -b 200` | RTT + shift-time plots from a directory |
| `references/tutorial-3.md:84` | `python PyRate.py -plotRJ .../path_to_log_files/ -b 200 -root_plot 23 -min_age_plot 5.3` | truncation to the 5.3-23 time window; the page calls the result "a plot spanning only the Miocene" (`references/tutorial-3.md:86`) |
| `references/tutorial-3.md:91` | `python PyRate.py -plotRJ .../path_to_log_files/ -b 200 -min_dt 0.5` | restate the prior when plotting |
| `references/tutorial-3.md:99` | `python PyRate.py -combLogRJ /pyrate_mcmc_logs -b 1000 -tag Canis` | merge replicates; `-b 1000` — "specifies that the first 1,000 samples should be removed as burn-in" (`:101`) |
| `references/tutorial-3.md:105` | `python PyRate.py -combLogRJ .../pyrate_mcmc_logs -b 1000 -tag Canis -resample 100` | "100 random samples should be taken from each replicate" (`references/tutorial-3.md:107`) |
| `references/tutorial-3.md:115` | `python PyRate.py .../Rhinocerotidae_PyRate.py -qShift .../epochs_q.txt -se_gibbs -fU 0.35 0.6 0` | Gibbs sampling of origination/extinction times for large datasets |
| `references/tutorial-3.md:119` | `-fQ 0.1 -tQ 1.05 1.05` | printed as a fragment at `:119`; the lead-in "Typically these settings will help" is at `:117` |
| `references/tutorial-3.md:142` | `python ./PyRate.py ./example_files/Ammonoidea.py -bound_se ./example_files/Ammonoidea_bound_se.txt` | bound origination/extinction times |
| `references/tutorial-3.md:146` | `python ./PyRate.py ./example_files/Ammonoidea.py -bound_se ./example_files/Ammonoidea_bound_se.txt -qShift ./example_files/epochs_q.txt -se_gibbs -fU 0.35 0.6 0` | the same bounds "in combination with Gibbs sampler" (`references/tutorial-3.md:144`) |

The `-d` route matters more than it looks. `references/command-list.md:18` states that `-d`
"automatically sets `-fixSE = null`" — the doc's own redundant parenthetical "(see PyRate command list)" sits
between the two quoted spans below — and that this means "the estimation of preservation rates and times of
speciation/extinction are switched off, and the MCMC only samples the birth-death parameters based on the
given times of origin and extinction of each species" (all `references/command-list.md:18`). So a `-d … -A 4`
run never touches the preservation process, and its `Canidae_1_G_se_est.txt` must come from an earlier
analysis (the `-ginput` route, owned by
`../pyrate-summarize-results/references/tutorial-2.md:22-64`, which names the output
"Canidae\_1\_G\_se\_est.txt" at `:33` — note that the same section twice calls the combined output
"...se_ext.txt" at `:45` and `:48`, an upstream naming discrepancy the page never resolves). `-fixSE null`
itself means "first and last appearances are  used as fixed times of speciation and extinction"
(`references/command-list.md:105`, double space in the source).

## RJMCMC output: four files, and how shifts are recorded

"RJMCMC analyses by default produce 4 output files" (`references/tutorial-3.md:51`):

| File | Documented content | Read it for | Citation |
| --- | --- | --- | --- |
| `sum.txt` | "the complete list of settings used in the analysis" | the settings that actually ran — which `-A`, which prior, which preservation model (inference: the page calls it the complete list but its exact layout is documented nowhere) | `references/tutorial-3.md:52-53` |
| `mcmc.log` | tab-separated posterior samples: posterior, prior, `PP_lik`, `BD_lik`, `q_rate`, `alpha`, "the number of sampled rate shifts (*k_birth*, *k_death*)", `root_age`, `tot_length`, "and the times of speciation and extinction of all taxa in the data set" — rendered in the mirror with escaped asterisks and "if estimated"; under TPP the preservation rates between shifts are "*q_0, q_1, ... q_n* (from older to younger)" | the shift counts per sample, i.e. the input to `-mProb` | `references/tutorial-3.md:55` |
| `sp_rates.log`, `ex_rates.log` | "sampled rates and times of rate shifts"; "because the number of shifts is likely to change throughout the RJMCMC, the number of columns in the text file is not fixed" | the input to `-plotRJ`; shift placement | `references/tutorial-3.md:57` |
| `marginal_rates.log` (old format) | obtained "instead" with `-log_marginal_rates 1`; works with `-plot`, "but it cannot be analyzed using the command `plotRJ`" | legacy RTT plots only | `references/tutorial-3.md:60` |

Reading the number of shifts therefore has **two documented routes**: the per-sample counts `k_birth` /
`k_death` in `mcmc.log` (`references/tutorial-3.md:55`), summarised by `-mProb`; and the *marginal*
placement of shifts in the `-plotRJ` histograms (`references/tutorial-3.md:75`). The variable-width
`sp_rates.log` / `ex_rates.log` files carry the shift times themselves, and because the column count is not
fixed you cannot paste them into a spreadsheet as a rectangular table without deciding a maximum shift
number first — the page prints no such rule.

**Conflict to check on your own data.** `../pyrate-summarize-results/references/summarize-results.md:20`
describes the same columns as
"the number of sampled rate shifts (`k_birth`, `k_death`; only logged in BDMCMC analyses)",
and line 64 of that page scopes `-mProb` to "the posterior samples logged in a BDMCMC analysis".
Tutorial #3 does the opposite: it lists `k_birth`/`k_death` among the RJMCMC `mcmc.log` columns
(`references/tutorial-3.md:55`) and applies `-mProb` to an RJMCMC log (`references/tutorial-3.md:63-65`).
Both statements are in this corpus; neither is qualified. Do not assume — grep your own log for the headers
(`rjmcmc-mcmc-log-column-names.txt` lists every name either page mentions).

## Summarising model probabilities (`-mProb`) and burnin

```sh
python PyRate.py -mProb .../Canis_pbdb_data_mcmc.log -b 200    # references/tutorial-3.md:65
```

The **mcmc.log** file "can be used to calculate the sampling frequencies of birth-death models with different
number of rate shifts" and the command "will provide a table (printed on screen) with the relative
probabilities of birth-death models with different number of rate shifts"
(`references/tutorial-3.md:63,67`). It takes the log *file* (unlike `-plotRJ`, which takes the *directory*),
and no output file name is documented — the table is screen output only.

Burnin selection feeds in through `-b`, whose documented meaning is the strictest thing in this chain:

| Form | Documented reading | Citation |
| --- | --- | --- |
| `-b 200` with `-mProb` | "the first 200 samples will be removed (i.e. the first 200,000 iterations, if the sampling frequency was set to 1,000)" | `references/tutorial-3.md:67` |
| `-b 1000` with `-combLogRJ` | "specifies that the first 1,000 samples should be removed as burn-in" | `references/tutorial-3.md:101` |
| `-b 0` | "(default; all samples are logged)" | `references/command-list.md:71` |
| `-b 0.10` | "the first 10% of the samples are discarded"; "When set to a number between 0 and 1, it is interpreted as a fraction of the total number of MCMC generations" | `references/command-list.md:69,73` |

Cross-check the number against `-s` (sampling frequency, `-s 1000` default, `references/command-list.md:60-62`)
and against `-n` ("Number of MCMC or BDMCMC generations", `-n 10000000` default,
`references/command-list.md:56-58`): 200 samples at `s = 1000` is 200,000 of 10,000,000 generations. The
sister page recommends inspecting the log in Tracer to set the burnin
(`../pyrate-summarize-results/references/summarize-results.md:20`) — that advice is written for the general
`mcmc.log`, not specifically for `-A 4`.

## Plotting rates through time and rate shifts (`-plotRJ`)

`-plotRJ` consumes `sp_rates.log` and `ex_rates.log` (`references/tutorial-3.md:71`): "This will generate an
R script and a PDF file with the RTT plots showing speciation and extinction rates through time. It will also
show histograms with the inferred times of rate shifts and calculate Bayes Factors to help determining the
time when a rate shift is supported by significant posterior probability."
(`references/tutorial-3.md:75`).

| Option | Documented behaviour | Citation |
| --- | --- | --- |
| `path_to_log_files/` | **a directory**, not files; "If multiple compatible files are found in the directory, they will be plotted individually. All individual plots are however combined in a single R script and PDF file." | `references/tutorial-3.md:77` |
| `-tag Canis_pbdb` | restricts plotting to log files whose *name* contains the string | `references/tutorial-3.md:77` |
| `-b 200` | burnin removal before plotting | `references/tutorial-3.md:73` |
| `-grid_plot 0` | default; "sets the bin size to obtain 100 bins across the dataset's time window" | `references/tutorial-3.md:79` |
| `-grid_plot 0.1` | "sets the bin size to 0.1 Myr"; any "arbitrarily small positive value" is allowed | `references/tutorial-3.md:80` |
| `-root_plot 10` | "truncate the plot to a given maximum age"; "will only show marginal rates in the most recent 10 time units" | `references/tutorial-3.md:82` |
| `-min_age_plot 5.3` | "truncate the rates-through-time plot at a given minimum age" | `references/tutorial-3.md:82` |
| `-logT 1` | "can be added to plot log10-transformed rates-through-time" | `references/tutorial-3.md:88` |
| `-min_dt 0.5` | restate the shift prior when it was changed for the analysis | `references/tutorial-3.md:89-91` |

Evidence thresholds printed for the shift histograms (`references/tutorial-3.md:75`, CN
`references/tutorial-3-cn.md:76`): "two horizontal dashed lines showing the thresholds for positive evidence
of a rate shift (bottom line: logBF = 2) and for strong evidence of a rate shift (top line: logBF = 6). Thus,
any point in the histogram showing sampling frequencies for a rate shift exceeding the thresholds indicate a
time of significant rate change." Example figure: the mirror embeds the image with a relative path
written from inside `references/`, at `references/tutorial-3.md:93`; the same file as seen from this skill
folder is `../assets/images/RTT_plot_RJMCMC.png`.

`-plotRJ` writes and runs R code: the page says it "will generate an R script and a PDF file"
(`references/tutorial-3.md:75`). The only documented R dependency in this corpus is for `-plot` — "The script
is automatically executed by PyRate using the shell command `RScript`"
(`../pyrate-installation/references/home.md:84`) — so by inference `-plotRJ` needs `Rscript` on `PATH` too,
but no page says so for `-plotRJ` by name.

**`-logT` conflict.** In this plotting context the tutorial means log10 (`references/tutorial-3.md:88`), but
the command list binds the same flag to *trait* transformation, where `-logT 1` is "trait is log_e
transformed" and `-logT 2` is "trait is log10 transformed (default)"
(`references/command-list.md:150-155`; identical in `references/command-list-cn.md:150-155`). Two readings of
one flag; do not treat one page's value list as valid for the other.

## Combining log files from multiple replicates

"PyRate includes a utility function to combine output files from different runs into one file. Assuming that
all output files form the previous analyses are in the same pyrate mcmc logs directory"
(`references/tutorial-3.md:97`; 'form' is the source's typo for 'from' — the Chinese twin carries the same
sentence at `references/tutorial-3-cn.md:98`, but the typo is English-only and untranslatable, so the CN page
neither preserves nor resolves it).

```sh
python PyRate.py -combLogRJ /pyrate_mcmc_logs -b 1000 -tag Canis                        # :99
python PyRate.py -combLogRJ .../pyrate_mcmc_logs -b 1000 -tag Canis -resample 100       # :105
```

| Piece | Documented meaning | Citation |
| --- | --- | --- |
| `-combLogRJ <path>` | "provides the full path to the log files" | `references/tutorial-3.md:101` |
| `-b 1000` | "the first 1,000 samples should be removed as burn-in" | `references/tutorial-3.md:101` |
| `-tag Canis` | "specifies that all and only files containing `x` (the word _Canis_ in the example above) in the file name should be combined" | `references/tutorial-3.md:101` |
| outputs | "generates three output files" named `combined_[n]_mcmc.log`, `combined_[n]_sp_rates.log`, `combined_[n]_ex_rates.log`, "where [n] is the number of combined replicates" (the mirror escapes the underscores inside these names) | `references/tutorial-3.md:101` |
| `-resample 100` | "100 random samples should be taken from each replicate and saved into the combined log files", "To avoid producing too large combined files" | `references/tutorial-3.md:103,107` |
| `-combLog` + `-col_tag posterior root_age death_age` | for the `mcmc.log` only, "will combine only the three columns with headers `posterior`,`root_age`, and `death_age` (while ignoring all other parameters)" — the same trim drops `k_birth`/`k_death`, so this recipe cannot feed `-mProb` (inference from `references/tutorial-3.md:55,63`; see Pitfalls) | `references/tutorial-3.md:110` |

Why it matters: replicate analyses exist because the input file carries randomised fossil ages, and
"**Ideally, we should analyze multiple randomized replicates and combine the results to incorporate dating
uncertainties** in our rate estimates"
(`../pyrate-bd-analysis/references/tutorial-1.md:178`). The replicate selector is `-j`
(`references/command-list.md:27-30`) and `-out run_2`, which “adds ‘run_2’ to the name of all output files” so the
runs do not overwrite each other (`references/command-list.md:32-35`) — which is what makes a
`-tag`-selectable directory of logs.

Two documented oddities: the name `death_age` — used at `references/tutorial-3.md:110` as required by `-plotRJ` —
is otherwise absent from the corpus (`grep -rn death_age */references/*.md` matches only
`references/tutorial-3.md:110` and its CN twin at line 111), and it is *not* among the `mcmc.log` columns
listed at `references/tutorial-3.md:55`. And `references/tutorial-3.md:110` says `-plotRJ` needs only
`root_age` and `death_age`, while `references/tutorial-3.md:71` says `-plotRJ` uses `sp_rates.log` and
`ex_rates.log`; the two sentences are never reconciled on the page.

## Running PyRate on large datasets

What the section names, in full (`references/tutorial-3.md:112-123`): the Gibbs route of Moharrek et al.
2022 Palaeontology — "an approximate Gibbs sampler can be used to sample more efficiently the times of
origination and extinction" (`references/tutorial-3.md:113`) — switched on with `-se_gibbs`, combined with
`-qShift .../epochs_q.txt` and
"modify the update frequencies to set most of the updates (> 90%) to focus on speciation, extinction, and
preservation rates" (`references/tutorial-3.md:113`), i.e. `-fU 0.35 0.6 0`
(`references/tutorial-3.md:115`); plus, for many preservation shifts, `-fQ 0.1 -tQ 1.05 1.05`
(`references/tutorial-3.md:117-119`).

| Lever | Value used by the tutorial | Documented semantics | Citation |
| --- | --- | --- | --- |
| `-se_gibbs` | on, and never alone: both printed commands pair it with `-qShift` | no definition anywhere in this corpus beyond this section. What the section *does* settle is the model it may be paired with: a bare `-se_gibbs` leaves the preservation model undeclared, and undeclared means NHPP — "Note that the NHPP is  used unless differently specified." (`references/command-list.md:88`), "By default, PyRate assumes an NHPP model" (`../pyrate-bd-analysis/references/tutorial-1.md:122`) — which is not one of the two the note admits (`references/tutorial-3.md:122`) | `references/tutorial-3.md:113,115,122,146` |
| `-fU 0.35 0.6 0` | preservation 0.35, birth-death 0.6, Covar 0 | "Update frequencies for preservation rate, birth-death parameters, and correlation parameters under the Covar model, respectively. What is left is used for updating speciation and extinction times." → by arithmetic 5% of updates go to SE times, and 95% ≥ the "> 90%" the page asks for | `references/command-list.md:263-265` |
| `-fQ 0.1` | 0.1 | **not defined anywhere in this corpus** (the command list has `-fU`, `-fS`, `-fR` but no `-fQ`) — the only context the page gives is "tune the proposal frequency and window sizes for the preservation parameters" | `references/tutorial-3.md:117-119` |
| `-tQ 1.05 1.05` | window sizes 1.05 / 1.05 | "Window sizes of the preservation rate (q) and of the shape parameter of the gamma distributed rate heterogeneity (alpha), respectively (multiplier proposals)" — the documented default is `-tQ 1.2 1.2` | `references/command-list.md:243-245` |
| `-qShift .../epochs_q.txt` | in both printed `-se_gibbs` commands | sets TPP preservation (`references/command-list.md:91-93`), and that is load-bearing rather than cosmetic: the section admits only "HPP or TPP" (`references/tutorial-3.md:122`) while the undeclared default is NHPP (`references/command-list.md:88`), so a preservation flag has to be named — the page never says this in words, it only ever runs the flag with `-qShift` (`references/tutorial-3.md:115,146`; inference) | `references/tutorial-3.md:115,122,146` |

The two documented caveats. (i) HPP/TPP only — "This model only works for preservation models based on
homogenous or time-variable Poisson processes (HPP or TPP)." (`references/tutorial-3.md:122`, note the
source's spelling "homogenous") — which excludes the *default* rather than some exotic choice, because with
no preservation flag PyRate runs NHPP: "Note that the NHPP is  used unless differently specified."
(`references/command-list.md:88`) and "By default, PyRate assumes an NHPP model"
(`../pyrate-bd-analysis/references/tutorial-1.md:122`). A bare `-se_gibbs` is therefore outside the set the
page admits, and both of its own `-se_gibbs` commands pass `-qShift` (`references/tutorial-3.md:115,146`).
(ii) Smoothing — the page's two remedies are "One option to avoid that is to set predefined
times of rate shifts using `-fixShift`" and "Another option is to run the analysis (with `-fixShift`),
extract the times of origination and extinction", "and then run the RJMCMC algorithm with fixed times of
origination and extinction using the `-d` command" (`references/tutorial-3.md:123`).

**Threading, burnin and sampling are *not* part of this section.** `references/tutorial-3.md:112-123` prints
no `-thread`, `-n`, `-s` or `-b` advice; if you need those levers they come from the command list —
`-thread 0 0` "(default; sequential likelihood calculation)" and `-thread 1 3` "use 1 thread for
birth-death, 3 threads for NHPP likelihood" (`references/command-list.md:75-79`), `-n`
(`references/command-list.md:56-58`), `-s` (`references/command-list.md:60-62`), `-b`
(`references/command-list.md:68-73`) — and attributing them to this tutorial would be inventing
a source.

## Constraining origination and extinction times (`-bound_se`)

"Inferred origination and extinction times can be constrained to occur no earlier or later than a specified age"
(`references/tutorial-3.md:127`). The input is
"a tab or comma separated text file. The first column gives the name of the taxon, the second its earliest origination time, the third the latest originaton time, the fourth the earliest extinction time, and the fifth column the latest extinction time. When an origination or extinction time should not be constrained, the respecive cell should contain _NA_. Taxa without any of the two bounds do not need to be included in the text file"
(`references/tutorial-3.md:129`; the typos "originaton" and "respecive" are in the source, and the Chinese twin translates the same column order, `references/tutorial-3-cn.md:130`).

The flag itself is never explained in prose: `-bound_se` appears in this corpus only inside the two
example command lines (`references/tutorial-3.md:142,146`; `grep -rn 'bound_se' */references/*.md` from the
suite root adds nothing but their CN twins at `references/tutorial-3-cn.md:143,147`).

Reconciling the prose with the printed header (`references/tutorial-3.md:134`) is arithmetic, not
documentation: ages grow backwards, so `max_ts` **is** the "earliest origination time" and `min_ts` the
"latest", giving the order `taxon, max_ts, min_ts, max_te, min_te`. The example's numbers support that
reading — `Acanthoscaphites` carries `min_te = 66.0` and `Sabaliceras` `min_te = 251.902`, the two mass
extinctions the rationale sentence names: "we know for certain that taxa went extinct during a mass
extinction event (setting min_te) or originated after a given moment in time (setting max_ts). Setting a
minimum age of orignation (min_ts) can be usefull if we only have records younger than a certain age but we
know the taxon originated much earlier" (`references/tutorial-3.md:131`).

| taxon | max_ts | min_ts | max_te | min_te |
| --- | --- | --- | --- | --- |
| Anolcites | 251.902 | NA | NA | 201.4 |
| Acanthoscaphites | NA | NA | NA | 66.0 |
| Glatziella | 372.15 | NA | NA | NA |
| Sabaliceras | NA | 276.1 | NA | 251.902 |

Table reproduced from `references/tutorial-3.md:134-139` verbatim in
`../assets/files/rjmcmc-bound_se-table-EXCERPT.md`; the tab-separated rendering is
`../assets/files/rjmcmc-bound_se.txt`.

```sh
python ./PyRate.py ./example_files/Ammonoidea.py -bound_se ./example_files/Ammonoidea_bound_se.txt   # :142
python ./PyRate.py ./example_files/Ammonoidea.py -bound_se ./example_files/Ammonoidea_bound_se.txt \
     -qShift ./example_files/epochs_q.txt -se_gibbs -fU 0.35 0.6 0                                   # :146
```

Relation to `-d` / `-fixSE`: `-bound_se` constrains times that are **estimated**, and both printed examples
take the occurrence-data `.py` input (`references/tutorial-3.md:142,146`). `-d` and `-fixSE` are the opposite
case — the times are given and their estimation is "switched off" (`references/command-list.md:18,105`), so
there is nothing left for a bound to act on. `-bound_se` and `-d` never appear together anywhere in this
corpus (verified: `grep -rn 'bound_se' */references/*.md` hits only `references/tutorial-3.md` lines 142, 146
and the CN twin at 143, 147), and no page states whether the two flags are combinable.

## Worked example

Placeholders only where the tutorial itself uses them; PyRate runs under Python 2.6-2.7
(`../pyrate-installation/references/home.md:69`). Each PyRate line below reproduces one the mirrors print
(flags and numbers verbatim); only the file paths are adapted to this suite's layout, and the `bash`/`grep`/
`head`/`ls`/`column` lines are plain shell. No line names a particular machine: the block opens in this skill
directory and the `python` lines are run from your own PyRate checkout, as step 1 says.

```sh
cd ../pyrate-rjmcmc    # this skill directory, wherever the suite is installed: from the suite root this
                       # enters it, from inside it is a no-op; the ../assets paths below need that cwd

# 0. see the whole tutorial #3 command set, with a references/tutorial-3.md line ref per command
bash ../assets/files/rjmcmc-commands.sh                 # dry run (default); RUN=1 executes
head -12 ../assets/files/rjmcmc-mcmc-log-column-names.txt   # mcmc.log names the docs spell out (references/tutorial-3.md:55 + ../pyrate-summarize-results/references/summarize-results.md:20; ../pyrate-bd-analysis/references/tutorial-1.md:199 repeats the same list)

# 1. the run (tutorial-3.md:35 with your own occurrence input; -A 4 from tutorial-3.md:32)
#    the `python` lines below run from your PyRate checkout — tutorial #3 prints no `cd` line of its own, so
#    copy the anchor the corpus uses elsewhere: cd /your/path/to/PyRate-master (../pyrate-bdnn/references/tutorial-bdnn.md:48)
python PyRate.py Canis_pbdb_data_PyRate.py -A 4 -mHPP -mG          # -mHPP/-mG: references/command-list.md:87,95
python PyRate.py -d Canidae_1_G_se_est.txt -A 4 -min_dt 0.5        # tutorial-3.md:46

# 2. confirm what actually ran, then read the shift counts (tutorial-3.md:52-53, 65)
grep -n -i 'min_dt' Canis_pbdb_data_sum.txt                        # sum.txt lists the settings (:52-53);
# its exact layout is not documented anywhere, so treat a no-match as unknown, not as proof
python PyRate.py -mProb Canis_pbdb_data_mcmc.log -b 200            # table printed on screen (:63-67)

# 3. plot RTT + shift histograms from the DIRECTORY (tutorial-3.md:73, 77, 91)
python PyRate.py -plotRJ .../path_to_log_files/ -b 200 -min_dt 0.5  # the .../ placeholder is the tutorial's own; compare against logBF 2 / 6 (:75)

# 4. many replicates -> one merged log set (tutorial-3.md:99,105; -j/-out: command-list.md:27-35)
python PyRate.py -combLogRJ .../pyrate_mcmc_logs -b 1000 -tag Canis -resample 100
ls .../pyrate_mcmc_logs/combined_*_mcmc.log                         # names per tutorial-3.md:101

# 5. bound origination/extinction times with the fixture table (tutorial-3.md:142)
#    `<suite>` = the folder holding these skills; spelled out because this line runs from the PyRate
#    checkout, where a path relative to this skill directory would not reach the fixture; the fixture's
#    `#` provenance lines are not documented input, so strip them before handing the file to PyRate
python ./PyRate.py ./example_files/Ammonoidea.py -bound_se <suite>/assets/files/rjmcmc-bound_se.txt
column -t ../assets/files/rjmcmc-bound_se.txt                       # check max-before-min column order first
```

The `./example_files/Ammonoidea.py` occurrence file is not part of this suite — its format is owned by
`../pyrate-input-file/`.

## Pitfalls

- **Do not compare `-A 4` and `-A 2` logs file-by-file.** `-A 2` output is described in the general output
  section as `marginal_rates.log`-based (`../pyrate-bd-analysis/references/tutorial-1.md:192,200`), RJMCMC
  defaults to `sp_rates.log`/`ex_rates.log`, and the `-plot`/`-plotRJ` functions are not interchangeable
  (`references/tutorial-3.md:60`).
- **`-plotRJ` writes one R script and one PDF for a whole directory**: "All individual plots are however
  combined in a single R script and PDF file" (`references/tutorial-3.md:77`). Re-running it on a directory
  whose file set changed does not obviously invalidate the earlier PDF; the page prints no overwrite rule.
- **`-grid_plot 0` is a real bin size, not a null setting**: it means "100 bins across the dataset's time window"
  (`references/tutorial-3.md:79`), so a plot's resolution silently depends on the clade's age range.
- **Histogram peaks are not the same quantity as `k_birth`/`k_death`.** The histograms show marginal sampling
  frequencies per time bin judged against logBF thresholds (`references/tutorial-3.md:75`); the per-sample
  shift counts come from `mcmc.log` (`references/tutorial-3.md:55`). Quote them separately.
- **Screen-only results get lost.** `-mProb` output is "a table (printed on screen)"
  (`references/tutorial-3.md:67`) with no documented file name — redirect it yourself (`> mProb.txt` is a
  shell action, not a documented PyRate option).
- **`-col_tag posterior root_age death_age` — the page's own example — silently un-feeds `-mProb`.** Its
  own recipe for the `mcmc.log` (`references/tutorial-3.md:110`) keeps three columns and nothing else —
  "only the three columns with headers `posterior`,`root_age`, and `death_age`"
  and "while ignoring all other parameters". The shift count is not among the three: it lives in
  `k_birth`/`k_death`, "the number of sampled rate shifts (*k_birth*, *k_death*)" (`references/tutorial-3.md:55`).
  The summary is computed from that same log, which
  "can be used to calculate the sampling frequencies of birth-death models with different number of rate shifts"
  (`references/tutorial-3.md:63`) and yields
  "the relative probabilities of birth-death models with different number of rate shifts" (`references/tutorial-3.md:67`).
  The page justifies it for plotting alone: "only `root_age`, and `death_age` are needed to run the" `-plotRJ`
  function (`references/tutorial-3.md:110`). **No line anywhere connects `-col_tag` to `-mProb`**, so the dead summary is *inferred* from the quotes above, as is the absence of any documented
  warning for it. Keep an un-trimmed `mcmc.log`, or add `k_birth k_death` to `-col_tag`, whenever you still
  want the shift-number posterior.
- **Source typos are load-bearing here**: the page writes `plotRJ` without the leading `-`
  (`references/tutorial-3.md:60`) and "defined" for "defines" (`references/tutorial-3.md:79`); the actual
  flag is `-plotRJ` (`references/tutorial-3.md:71`).

## Not documented in this wiki

| Unanswered question | Why you must not fill it in |
| --- | --- |
| Whether omitting `-A` gives `-A 2` or `-A 4` | `references/command-list.md:52` and `../pyrate-bd-analysis/references/tutorial-1.md:167,174` give opposite answers and no third page arbitrates; the difference changes the output files and the shift-count columns |
| Whether `-mProb` is valid on an `-A 4` log | `references/tutorial-3.md:63-65` applies it to an RJMCMC run while `../pyrate-summarize-results/references/summarize-results.md:20,64` restricts `k_birth`/`k_death` and `-mProb` to BDMCMC |
| A prior on the *number* of shifts under `-A 4` | BDMCMC has one ("a Poisson distributed prior on the number of speciation/extinction rates", `-B`, `references/command-list.md:218`); no page gives `-A 4` an equivalent, and `-B`'s own text is scoped to `-A 2` |
| Whether `-mL`/`-mM`/`-mC` do anything under `-A 4` | `-mL`/`-mM` name only `-A 0`, `-A 1` and `-A 2` (`references/command-list.md:112,116`) and `-mC` names no `-A` value at all (`references/command-list.md:120`); "In BDMCMC analyses (`-A 2`) this command is only used to set the number of starting rates" is not extended to RJMCMC |
| Any maximum number of shifts, and the definition of the 'time unit' a shift bin must fill | `references/tutorial-3.md:44` illustrates '(e.g. 1 myr)' and nothing more |
| The exact header line / column order of `mcmc.log`, `sp_rates.log`, `ex_rates.log`, `combined_[n]_*` | no log file is printed anywhere in this corpus; only the names in `references/tutorial-3.md:55` are given, and `death_age` (`references/tutorial-3.md:110`) is not among them |
| Whether `-bound_se` needs its header row, whether `NA` is case-sensitive, whether bounds are hard truncations or priors, and whether they may contradict the record (e.g. `min_ts` older than the oldest occurrence) | `references/tutorial-3.md:127-131` states the layout and the motivation only |
| `-bound_se` together with `-d`, or with `-A 2` | the two printed commands pair it with the occurrence input and with `-se_gibbs` (`references/tutorial-3.md:142,146`) — nothing else |
| `-fQ`: full name, valid range, and what else it controls | appears once, as a fragment (`references/tutorial-3.md:119`), and is absent from `references/command-list.md` |
| Whether a bare `-se_gibbs` (no preservation flag) is refused, warned about, or silently run under the default NHPP — and how `-mG` combines with it | `references/tutorial-3.md:122` names only "HPP or TPP", and `references/command-list.md:88` ("Note that the NHPP is  used unless differently specified.") plus `../pyrate-bd-analysis/references/tutorial-1.md:122` establish that NHPP is what you get when you name nothing — so the gap is the *default* invocation, not an exotic one; but no page states what PyRate does about it, and `-mG` is described as applicable to "the NHPP, HPP, and TPP preservation models" (`references/command-list.md:97`) without reference to the Gibbs sampler |
| Convergence criteria specific to `-A 4`, and how long to run | `references/tutorial-3.md:113` says large datasets "may require long computing time for the MCMC to reach convergence" and then only gives the Gibbs/frequency advice; the Tracer recommendation belongs to another page (`../pyrate-summarize-results/references/summarize-results.md:20`) |
| What `-combLogRJ` does without `-tag`, whether replicates may differ in length, and whether earlier `combined_*` files get re-merged | `references/tutorial-3.md:101` describes only what `-tag x` selects ("all and only files containing `x`") |
| How `-plotRJ` treats `sp_rates.log` and `ex_rates.log` with different numbers of shifts | `references/tutorial-3.md:57` states only that the column count "is not fixed" |
| Whether `Rscript` is required for `-plotRJ` | `references/tutorial-3.md:75` promises "an R script and a PDF file"; the `RScript` statement is made about `-plot` in `../pyrate-installation/references/home.md:84` |

## Related skills

- `pyrate-command-reference` — owns the same `references/command-list.md`: the `-A 0`-`-A 3` entries, `-d`, `-fixSE`, `-j`, `-out`, `-b`, `-n`, `-s`, `-thread`, `-fU`, `-tQ`, `-fS`, `-tS`, `-multiR`.
- `pyrate-bd-analysis` — tutorial #1: the base BD run, `-A 2`, `marginal_rates.log` + `-plot`, `-fixShift` with `epochs.txt`, `-j` replicates, and `-edgeShift 18 2` — a documented `-A 4` combination of its own (with further `-A 4` occurrences at `../pyrate-bd-analysis/references/tutorial-1.md:174` and in other skills' pages, see the coverage note above) (`../pyrate-bd-analysis/references/tutorial-1.md:265-276`).
- `pyrate-preservation-models` — `-mHPP`, `-mG`, `-qShift`/`epochs_q.txt`: exactly the models the `-se_gibbs` restriction is about (`references/tutorial-3.md:122`).
- `pyrate-summarize-results` — own entries for `-mProb`, `-plot`, `-plot2`, `-tag`, `-root_plot`, `-BF` and the general output-file descriptions (including the conflicting "only logged in BDMCMC analyses"); it also notes `-b` is "by default set to 0" when summarizing (`../pyrate-summarize-results/references/summarize-results.md:64`). The `-b` definition itself lives with `pyrate-command-reference`.
- `pyrate-continuous-covariates` / `pyrate-summarize-results` — `-ginput`, which produces the `..._se_est.txt` tables that this skill's `-d … -A 4` runs consume (`../pyrate-summarize-results/references/tutorial-2.md:22-64`).
- `pyrate-input-file` — the occurrence `.py` input, the `-d` 4-column table, `epochs_q.txt`.
- `pyrate-mcmc-tuning` — tutorial #6 for tuning/mixing questions; this skill only covers the frequency changes the RJMCMC page prints.
- `pyrate-trait-age-models`, `pyrate-diversity-dependence` — MCDD use of the `-d` clade column (`references/command-list.md:18`) and trait-age models, which are `-A 0`/`-A 1` territory.
- `pyrate-des` — a separate program, `PyRateDES.py` (`../pyrate/references/home.md:53`); no `-A 4` appears
  in the DES pages. `pyrate-bdnn` is **not** a separate program: BDNN is a model of `PyRate.py` switched on
  with "`-BDNNmodel 1`" (`../pyrate-bdnn/references/tutorial-bdnn.md:223`), the home page's program list
  names only `PyRate.py`, `PyRateContinuous.py`, `PyRateMCDD.py`, `PyRateDES.py` and `pyrate_lib`
  (`../pyrate/references/home.md:28,39,46,53,60`) and contains no BDNN entry at all
  (`grep -c -i bdnn ../pyrate/references/home.md` = 0), and the token `PyRateBDNN` appears nowhere in this
  corpus — do not write it as a command name. The BDNN tutorial does print one `-A 4` command
  (`../pyrate-bdnn/references/tutorial-bdnn.md:472`) — that workflow is owned there.
- `pyrate-installation` — Python 2.6-2.7, `numpy`/`scipy`/`argparse`, `Rscript`.
- `pyrate` — the suite index and tutorial list.

## Resources

| File | What's in it | Load when |
| --- | --- | --- |
| `references/tutorial-3.md` | The whole RJMCMC tutorial: `-A 4` setup for occurrence and `-d` data, the `-min_dt` prior, the 4 output files, `-mProb`, `-plotRJ` and its plot options, `-combLogRJ`/`-combLog`, `-se_gibbs` for large datasets, `-bound_se` and its example table | Any question in this skill's scope — it is the only page that documents the RJMCMC workflow itself (`-plotRJ`, `-combLogRJ`, `-col_tag`, `-min_dt`, `-se_gibbs`, `-bound_se`, `-log_marginal_rates` all appear nowhere else in the corpus) |
| `references/tutorial-3-cn.md` | Full Simplified-Chinese twin (frontmatter is 9 lines vs the English 8, so every body line of the English mirror sits at CN line = EN line +1) | When an English sentence is ambiguous: it states the `-grid_plot` binning outright (`:80`, "共获得 100 个分箱"), repeats the `-combLogRJ` output names (`:102`) and the `-bound_se` column order (`:130`) — but it reproduces, and so cannot resolve, the `-min_dt` and `-logT` ambiguities |
| `references/command-list.md` | The `-A 0`-`-A 3` definitions (no `-A 4`), `-d`, `-fixSE`, `-j`, `-out`, `-b`, `-n`, `-s`, `-thread`, `-mL`/`-mM`/`-mC`/`-fixShift`, `-M`/`-B`/`-T`/`-S`, the tuning block (`-multiR`, `-tT`, `-nT`, `-tQ`, `-tR`, `-tS`, `-fS`, `-tC`, `-fU`, `-fR` — no `-fQ`), `-logT` as a trait transform | Deciding what a flag means outside tutorial #3, or proving an option is undocumented |
| `references/command-list-cn.md` | Chinese twin of the above. Line offsets vs the English mirror: +1 through `-mG` (EN `:95` = CN `:96`), identical for EN `:98-176`, then −1 from EN `:177` on (`-pP` EN `:178` = CN `:177`) | Checking whether a default or restriction in English is a translation artefact — e.g. `-A 2 (默认值)` at `:53` confirms the default conflict is upstream |

## grep recipes

```sh
# run these from this skill directory; every recipe was executed and the real result is annotated
# on its own line. The two "|| echo ..." lines name corpus absences and fall back to their marker.
grep -n -- '-A 4' references/tutorial-3.md | head -6   # the `-A 4` command lines at :32, :35, :39, :46
grep -n -- '-A 4' references/command-list.md || echo 'ABSENT: -A 4 is not in the command list'
grep -n 'time bin cannot be smaller\|separated by at least' references/tutorial-3.md
grep -n 'logBF\|number of columns in the text file' references/tutorial-3.md
grep -n 'first 200 samples\|first 1,000 samples' references/tutorial-3.md
grep -rn death_age ../pyrate-*/references/*.md | grep -v tutorial-3 || echo 'prints nothing: outside tutorial-3 no mirror names death_age'
grep -rn -- '-fQ' references/command-list.md || echo 'ABSENT: -fQ appears only as a fragment in tutorial-3.md:119'
grep -n 'only logged in BDMCMC' ../pyrate-summarize-results/references/summarize-results.md
```

## Runnable fixtures (`../assets/files/`)

All four are about this skill's own page; nothing here invents data. The table in
`rjmcmc-bound_se-table-EXCERPT.md`, the 12 verbatim command lines plus the `-fQ 0.1 -tQ 1.05 1.05` fragment
in `rjmcmc-commands.sh` (its 13th `cmd` line is the one marked COMPOSED) were each re-checked byte-for-byte
against the mirror, English and Chinese (the two agree on every one).

| File | Provenance | What it makes concrete |
| --- | --- | --- |
| `../assets/files/rjmcmc-commands.sh` | `derived` — assembled from `references/tutorial-3.md` lines 35, 39, 46, 65, 73, 84, 91, 99, 105, 110, 115, 119, 142, 146; every command verbatim except the `-combLog`/`-col_tag` line, which the file itself marks COMPOSED | the complete tutorial #3 command sequence, dry-run printable (`bash rjmcmc-commands.sh`) and executable with `RUN=1` |
| `../assets/files/rjmcmc-bound_se.txt` | `derived` from `references/tutorial-3.md:134-139` — markdown table re-laid out as tab-separated text, values and column order unchanged; it opens with `#` provenance comment lines, and nothing in the corpus says a `-bound_se` reader accepts comments (`references/tutorial-3.md:129` describes only "a tab or comma separated text file" of five columns), so strip them before a real run | a `-bound_se` table, including the `NA` convention and the `max_ts` before `min_ts` ordering |
| `../assets/files/rjmcmc-bound_se-table-EXCERPT.md` | `verbatim` copy of `references/tutorial-3.md:134-139` (identical to `references/tutorial-3-cn.md:135-140`) with a provenance header | the table exactly as the wiki prints it, pipes and alignment included |
| `../assets/files/rjmcmc-mcmc-log-column-names.txt` | `derived` — vocabulary extracted from `references/tutorial-3.md:55,110` plus `../pyrate-summarize-results/references/summarize-results.md:20`; explicitly not a header line | which `mcmc.log` column names are actually documented (for `-col_tag`, `-mProb`, Tracer checks) and which the docs dispute |
