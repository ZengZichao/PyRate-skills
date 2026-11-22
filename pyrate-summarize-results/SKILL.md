---
name: pyrate-summarize-results
description: "PyRate output reading and post-processing: *_sum.txt, *_mcmc.log, *_marginal_rates.log, *_marginal_likelihood.txt, *_RTTplot.r, *_RTTplot.pdf, *_se_est.txt and pyrate_mcmc_logs folder; all mcmc-log columns (PP_lik, BD_lik, q_rate, alpha, cov_sp, cov_ex, cov_q, k_birth, k_death, beta, root_age, lambda_0.., mu_0.., shift_sp_1.., shift_ex_1.., tot_length, *_TS, *_TE) and which analysis logs each (-A 0/-A 1 fixed shifts vs BDMCMC vs TI); commands -data_info, -plot/-plotRJ, -plot2, -tag, -root_plot/-root_age, -mProb, -BF, -ginput, -resample, -ltt 1/2/3, -grid_plot, -d, -mL, -combLog; -b burnin (samples vs 0-1 fraction, defaults disagree across pages); RTT rates-through-time plots need an Rscript shell call; Tracer convergence check before summarising; RJMCMC -A 4 set, marginal_rates.log opt-in via -log_marginal_rates 1; three RJMCMC-tutorial pre-flight checks (opt-in flag if the rates log is missing, re-specify -min_dt when plotting, grep your mcmc-log header before -mProb); output-stem collisions and -out tags."
---

# PyRate output files and post-processing (`-plot`, `-plot2`, `-mProb`, `-BF`, `-data_info`, `-ginput`, `-ltt`)

## Overview

This skill governs everything that happens **after** a PyRate run: what files the run leaves behind and what each
column of them holds (`references/summarize-results.md`:12-30), and the post-processing commands that turn those logs
into figures, model probabilities, Bayes factors and the origination/extinction tables that feed the next program
(`references/summarize-results.md`:33-69, `references/tutorial-2.md`:22-88). The wiki page is the authority on file
contents; tutorial #2 is the authority on the `-ginput`/`-d -ltt` route. The page states "A typical PyRate analysis produces
three output files" (`references/summarize-results.md`:13): `_sum.txt` (settings), `_mcmc.log` (posterior samples) and
`_marginal_rates.log` (marginal rates in 1 time-unit bins) — with `_marginal_likelihood.txt` replacing the rates file
under TI (`:27`), and the tutorial adding that these are "saved in a folder named *pyrate\_mcmc\_logs* in the same directory as the input file"
(`../pyrate-bd-analysis/references/tutorial-1.md`:194).

**The riskiest assumption this skill removes:** that the log you are summarising is (a) the file your algorithm actually
wrote and (b) free of burn-in. `-plot` reads `*_marginal_rates.log`, but the two NOTE lines on this very page point
elsewhere: "NOTE that the default output for PyRate analysis using `-A 4`" — the RJMCMC set, whose `marginal_rates.log` is
opt-in ("can be obtained instead, using the command `-log_marginal_rates 1`", `../pyrate-rjmcmc/references/tutorial-3.md`:60,
which contradicts that page counting it as default output "4)", `:51`/`:59` — see hazard 3); and the page's own answer to burn-in is procedural, not automatic:
"We recommend to inspect the ‘*_marginal_rates.log’ file in Tracer to define the appropriate proportion of burnin"
(`references/summarize-results.md`:40). A plot or an `-mProb` table computed over an unconverged or un-trimmed chain is
wrong in a way no output field reveals.

## The 9 things that break a run

| # | What happens | Consequence | Wiki wording (`references/…`) |
| --- | --- | --- | --- |
| 1 | Summarising a chain that has not converged | RTT credible intervals and `-mProb` model frequencies reflect the burn-in phase; no output field reports it | "the file can be opened in the program" Tracer "to check the efficiency and mixing of the MCMC and the proportion of burnin" — `summarize-results.md`:20; `tutorial-1.md`:205 (ESS) → see `pyrate-mcmc-tuning` |
| 2 | `-plot` pointed at a directory with no `-tag` — or with a `-tag` narrower than you meant | Without a tag, "the function takes each ‘*_marginal_rates.log’ in the specified directory and summarizes it in a plot": other clades/replicates get figures too, and same-stem outputs collide. With a tag, the mirror image of the same sentence applies — "whereas other files are ignored" — so every log whose name lacks the substring is silently left out of the plot and no count of the files used is printed | "the function takes each ‘*_marginal_rates.log’ in the specified directory and summarizes it in a plot" — `summarize-results.md`:40; "combine all ‘*_marginal_rates.log’ files containing the word ‘rhinos’ in a single plot, whereas other files are ignored" — `summarize-results.md`:56 |
| 3 | Running `-plot` on an `-A 4` (RJMCMC) run | the file it reads is opt-in, not automatic: use `-plotRJ` on `sp_rates.log`/`ex_rates.log`, or re-run with `-log_marginal_rates 1` | "NOTE that the default output for PyRate analysis using `-A 4`" — `summarize-results.md`:25, `:36`; `tutorial-3.md`:51, `:57`, `:60` → `pyrate-rjmcmc`. Note the conflict: `tutorial-3.md` numbers `marginal_rates.log` as output "4)" of the four "by default" (`:51`, `:59`) yet says it "can be obtained instead, using the command `-log_marginal_rates 1`" (`:60`) — treat it as absent unless the flag was set; when the file is simply not in the directory, run check 1 of "Three pre-flight checks" before believing the run failed |
| 4 | Forgetting `-b` when summarising | burn-in samples are averaged into the plot; and the page's two stated defaults disagree with the global default | `-plot`: "(by default set to 1)" `summarize-results.md`:40 vs `-mProb`: "(by default set to 0)" `:64` vs "`-b 0`  (default; all samples are logged)" `../pyrate-command-reference/references/command-list.md`:71 |
| 5 | Treating `-b` as an iteration count | `-b 200` removes 200 **samples**, i.e. 200,000 iterations at `-s 1000`; over- or under-trimming by 3 orders of magnitude | "the flag `-b 200` indicates that the first 200 samples will be removed (i.e. the first 200,000 iterations, if the sampling frequency was set to 1,000)" — `tutorial-1.md`:213; `-b 0.10` = fraction, `command-list.md`:69, `:73` — but the `-b` definition itself says "Set the number of iterations to be discarded", `:69`; see Burn-in |
| 6 | Plotting a TI (`-A 1`) run | there is nothing to plot: the rates file "is replaced by" `_marginal_likelihood.txt`; `-b` must instead be right for the marginal likelihood | `summarize-results.md`:27-30; `-A 1` "computes the marginal likelihood of a birth-death model" — `command-list.md`:49; "Must be set to a reasonable number when estimating marginal likelihood through TI" — `command-list.md`:69; "It is important to **specify an appropriate burnin** using the flag `-b`)" — `tutorial-2.md`:153 |
| 7 | No R on the machine / not on `PATH` | `-plot` writes the `.r` script and, by inference from the two sentences below (the docs never print the failure), no PDF, because the script "is automatically executed by PyRate using the shell command `RScript`" | "generates a rates-through-time plot (RTT) using the scripting language R" — `summarize-results.md`:40; "If you are using Windows, please make sure that the path to Rscript.exe is included in the PATH environment variables (default in Mac/Linux)" — `../pyrate/references/home.md`:84 → `pyrate-installation` |
| 8 | Writing `-root_age 23` because the example says so, under a heading that says `-root_plot` | the page's own example uses a token its heading does not name; neither token appears in the global command list, and the RJMCMC tutorial uses the other spelling | heading `##### `-root_plot`` vs example "`-plot path_to_pyrate_results -tag rhinos -root_age 23`" — `summarize-results.md`:58-61; `../pyrate-rjmcmc/references/tutorial-3.md`:84 (`-root_plot 23`); `grep -n "root_age\|root_plot" ../pyrate-command-reference/references/command-list.md` → no hit |
| 9 | Two runs of the same input in one directory | outputs are overwritten: the stem comes from the input file and only `-out` adds a distinguishing tag | "Add tag to default stem name of output files. This command is useful to avoid overwriting output files when running several instances of the same analysis." — `command-list.md`:33-35 |

## Output files, file by file

Bare `:NN` in the two tables below means `references/summarize-results.md` line N (the page this skill mirrors); any other
file is named in full.

| File (`<stem>` = input-file stem, plus any `-out` tag) | Written by | What is in it | Next thing you do with it |
| --- | --- | --- | --- |
| `<stem>_sum.txt` | every analysis | "Text file providing the complete list of settings used in the analysis." (`:16`) | the audit trail for a figure; the only documented record of the settings actually used |
| `<stem>_mcmc.log` | MCMC / BDMCMC / RJMCMC / TI | "Tab-separated table with the MCMC samples of the posterior, prior, likelihoods of the preservation process and of the birth-death" plus every parameter (`:19-20`) — column table below | `-mProb` (model frequencies), `-ginput` (origination/extinction times), Tracer (mixing, burn-in) |
| `<stem>_marginal_rates.log` | the file this page treats as the standard output; the page states only the exceptions — **not** the `-A 4` default (`:25`, `:36`) and replaced under `-A 1` (`:27`); `command-list.md`:47, `:51` send `-A 0`/`-A 2` runs to this section | "Tab-separated table with the posterior samples of the marginal rates of speciation, extinction, and net diversification, calculated within 1 time unit (typically Myr)." (`:23`) | `-plot` / `-plot2` → RTT figure |
| `<stem>_marginal_likelihood.txt` | `-A 1` (TI) — the rates file "is replaced by the following" (`:27`) | "Text file providing the marginal likelihood of a birth-death model estimated by TI." (`:30`) | `-BF` with a second such file (`:67-69`) |
| `<stem>_RTTplot.r` + `<stem>_RTTplot.pdf` | `-plot` (`:40`); for `-plot2` by inference only, since `:46` declares `-plot2` equivalent to `-plot` | the R source and the graphic; "by default these files will be save in the same directory as the input file" (doc's typo `save` kept, `:40`) | the figure itself; edit the `.r` to restyle |
| `<stem>_se_est.txt` | `-ginput` (`tutorial-2.md`:31-35) | mean posterior times of origination and extinction, one row per species (`tutorial-2.md`:24) | `-d` input for PyRate / PyRateContinuous, `-ltt` plots, MCDD, BDNN |
| `sp_rates.log`, `ex_rates.log` | `-A 4` default (`../pyrate-rjmcmc/references/tutorial-3.md`:57) | "Tab-separated text files providing sampled rates and times of rate shifts"; "the number of columns in the text file is not fixed" (same line) | `-plotRJ`, `-combLogRJ` → owned by `pyrate-rjmcmc` |

Location rules that are documented: `-wd` sets the working directory and "If not specified, output files will be saved in
the same directory as the input file" (`../pyrate-command-reference/references/command-list.md`:23); tutorial #1 states
the three files are "saved in a folder named *pyrate\_mcmc\_logs* in the same directory as the input file"
(`../pyrate-bd-analysis/references/tutorial-1.md`:194).

## What each column of `*_mcmc.log` means

Verbatim inventory of `references/summarize-results.md`:19-20, in the order the wiki lists them (the order is *not*
stated to be the physical column order — no mirror prints a header row; see `../assets/files/sum-mcmc-log-columns.txt`).
In the "Logged when" column, bare `:NN` is `references/summarize-results.md` line N; "always" means the page names no
condition on the token (it does not promise the token appears in every analysis either).

| Column token | Meaning (doc wording) | Logged when |
| --- | --- | --- |
| posterior, prior | "the MCMC samples of the posterior, prior" | always (`:19`) |
| `PP_lik`, `BD_lik` | "likelihoods of the preservation process and of the birth-death" | always (spans `:19-20`) |
| `q_rate` | "the preservation rate" | always (`:20`) |
| `alpha` | "the shape parameter of its gamma distributed heterogeneity" | `:20` (heterogeneity model; not stated on this page) |
| `cov_sp`, `cov_ex`, `cov_q` | "the parameters of the Covar model" | `:20` (Covar analyses; see `pyrate-trait-age-models`) |
| `k_birth`, `k_death` | "the number of sampled rate shifts" | "only logged in BDMCMC analyses" (`:20`) — but the RJMCMC log description lists them too (`../pyrate-rjmcmc/references/tutorial-3.md`:55): unresolved, see Pitfalls |
| `beta` | "the value of scaling factor used in TI analyses" | `-A 1` (`:20`) |
| `root_age` | "the time of origin of the oldest lineage" | always (`:20`); the "minimum root age across all log files" that `-root_plot 0` uses (`:59`) is presumably this column — the page never connects the two by name |
| `lambda_0, lambda_1, ...` / `mu_0, mu_1, ...` | "the speciation/ extinction rates between shifts" | "only logged under fixed number of shifts, i.e. with `-A 0` or `-A 1`" (`:20`) |
| `shift_sp_1, ...` / `shift_ex_1, ...` | "the times of rate shifts in speciation and extinction" | "only logged with `-A 0` or `-A 1`" (`:20`) |
| `tot_length` | "the total branch length" | always (`:20`) |
| `*_TS`, `*_TE` | "the times of speciation and extinction of all taxa in the data set" | always on this page; "if estimated" only in `../pyrate-rjmcmc/references/tutorial-3.md`:55 |
| `q_0, q_1, ... q_n` | "When using the TPP model of preservation, the preservation rates between shifts are indicated as" them, "from older to younger" | TPP preservation model — **not on this page**: `../pyrate-bd-analysis/references/tutorial-1.md`:199 → `pyrate-preservation-models` |

## Post-processing commands on this page (and the two tutorial pages)

| Command | Reads | Writes | Documented detail | Source |
| --- | --- | --- | --- | --- |
| `-data_info` | a PyRate input file | screen only — "plot on screen a few summary statistics": species, singletons excluded, extant taxa, occurrences, observed time span. The page names **no** output file for it | pairs with `-singleton` | `summarize-results.md`:9-10; used as `python PyRate.py '.../Canis_pbdb_data_PyRate.py' -data_info` in `../pyrate-bd-analysis/references/tutorial-1.md`:45 |
| `-plot` | one `*_marginal_rates.log` **or a directory of them** | `_RTTplot.r` + `_RTTplot.pdf` | "plotted in 1 Myr time bins with the respective 95% HPDs"; burn-in via `-b`, "(by default set to 1)"; needs R | `summarize-results.md`:39-43 |
| `-plot2` | same | same | "produces RTT plots with fading credible intervals as shown in" Silvestro et al. (2015 PNAS) "(Fig. 2)" — the LandPlants_RTT.png figure on the page is a `-plot2` output | `summarize-results.md`:45-51 |
| `-tag` | filename substring | (modifies `-plot`, `-plot2`, `-ginput`) | "Specify which files should be combined in the RTT plot. When this argument is not used each marginal rate file will be plotted separately." — and the other half of the same entry: the example combines the files "containing the word ‘rhinos’ in a single plot, whereas other files are ignored", so a `-tag` silently *drops* every log whose name does not contain it (`summarize-results.md`:54, `:56`). No page says what happens when the tag matches no file at all | `summarize-results.md`:53-56 |
| `-root_plot` (example prints `-root_age`) | combined logs | (modifies the plot's x-axis) | "sets the maximum age in the plot. If set to 0, the age will be determined as the minimum root age across all log files. If `root_plot n`, where `n>0`, then the marginal rates will be plotted only up to an age of `n`." | `summarize-results.md`:58-61 |
| `-mProb` | a BDMCMC `*_mcmc.log` | table on screen: "sampling frequencies of birth-death models with different number of rate shifts" | proportion of burnin via `-b`, "(by default set to 0)"; example `-mProb file_name_mcmc.log` | `summarize-results.md`:63-65; `../pyrate-rjmcmc/references/tutorial-3.md`:67 ("printed on screen") |
| `-BF` | two `*_marginal_likelihood.txt` files | Bayes factor + category | "calculated as twice the difference of log marginal likelihood and the degree of support divided into four categories: negligible, positive, strong, very strong", after Kass and Raftery (1995) | `summarize-results.md`:67-69 |
| `-ginput` | a `*_mcmc.log` or a directory of them | 3 files: the `_se_est.txt` times table, a PDF (lineage durations + diversity trajectory), the R script that made it | "the command `-b 100` indicates that the first 100 samples should be discarded as burnin"; with a directory, "each file with extension `*_mcmc.log` will be processed separately" | `tutorial-2.md`:26-43 |
| `-ginput … -tag X` | several logs | one combined times table, "with columns with the origin and extinction of each species given for each replicate" | the replicate-combining route | `tutorial-2.md`:45-49 |
| `-ginput … -resample N` | logs | same table, N posterior samples "as additional columns" | multiple samples instead of means | `tutorial-2.md`:51-62 |
| `-d <times table> -ltt 1` | `_se_est.txt` | "1) a **pdf file** with the LTT plot, 2) a **table with the estimated diversity trajectory**, and 3) the **R script**" | "the mean diversity through time, with the min and max range inferred from the replicates and shown as shaded area" | `tutorial-2.md`:65-70 |
| `-ltt 2` / `-ltt 3` | same | same three files | `2` = "log10-transformed diversity"; `3` = "LTT plots from each replicate are shown as individual lines" | `tutorial-2.md`:74-81 |
| `-grid_plot n` | (modifies `-ltt`, `-plotRJ`) | — | LTT default is "time bins the size of 1 time unit"; `-grid_plot 0.1` → 0.1 Myr bins. (`-plotRJ` has a different default: `-grid_plot 0` = 100 bins) | `tutorial-2.md`:83-88; `../pyrate-rjmcmc/references/tutorial-3.md`:79-80 |
| `-plot` / `-mL` on **PyRateContinuous** | a PyRateContinuous `.log` (`-plot`), a directory of TI logs (`-mL`: "will calculate the marginal likelihood for each file in the directory with extension" `.log`) | R script + RTT PDF; or one text file of marginal likelihoods + new logs holding only the "cold" part of the MCMC states | Owned by `pyrate-continuous-covariates` (it mirrors the same tutorial); listed here only for the two summarising traps: tutorial-2 prints `-plot` twice with two different `-b` values (`:122` vs `:140`) and `-mL` collides with an unrelated option in the command list (see Pitfalls). "It is important to **specify an appropriate burnin** using the flag `-b`)" (doc's stray `)` kept) | `tutorial-2.md`:120-124, `:140`, `:153-157` |

## Three pre-flight checks the docs place on another page

Each of these is documented, but none of them sits on the `-plot`/`-mProb` section of the summarise page: two are in the
RJMCMC tutorial, the third is a conflict this page creates against itself. Do them **before** typing the command, because
all three fail silently — a missing file, a plot drawn under a prior the chain never sampled, a table of nothing.

| Trigger | The check, and the wording that mandates it |
| --- | --- |
| `-plot`/`-plot2`/`-plotRJ`: the `*_marginal_rates.log` you are about to point at is **not there** | **First recall whether the run carried `-log_marginal_rates 1`** — for an `-A 4` (RJMCMC) run the rates log is opt-in, so its absence is the expected result and not a failed analysis: "RJMCMC analyses by default produce 4 output files" (`../pyrate-rjmcmc/references/tutorial-3.md`:51), and the fourth entry of that list, `marginal_rates.log`, is headlined ‘(old format)’ at `:59` and "can be obtained instead, using the command `-log_marginal_rates 1` when setting up the analysis" (`../pyrate-rjmcmc/references/tutorial-3.md`:60). If the flag was not set, either plot `sp_rates.log`/`ex_rates.log` with `-plotRJ` (`:57`, `:71`) or re-run with the flag. The two are not interchangeable: the opt-in log "can be processed using the command `-plot`" but "cannot be analyzed using the command `plotRJ`" (`../pyrate-rjmcmc/references/tutorial-3.md`:60), which is the only command documented to give shift placement and its Bayes-factor thresholds (`:75`). No mirror prints the message `-plot` gives on a missing or unmatched file — **not documented** — so confirm with `ls` before diagnosing anything else (hazard 2, hazard 3) |
| Plotting a run whose `-min_dt` differed from the default | **Repeat the analysis' prior on the plotting command**: "If the prior on the minimum duration between time bins was changed from its default in the analysis, this hsould be also specified when plotting the results" (`../pyrate-rjmcmc/references/tutorial-3.md`:89, doc's typo `hsould` kept), on the page's own example `python PyRate.py -plotRJ .../path_to_log_files -b 200 -min_dt 0.5` (`:91`). That matters because "the RJMCMC assumes a uniform prior on the time of rate shifts, with the constraint that a time bin cannot be smaller than 1 time unit" by default (`../pyrate-rjmcmc/references/tutorial-3.md`:44) while the tutorial's run is `python PyRate.py -d Canidae_1_G_se_est.txt -A 4 -min_dt 0.5` (`:46`): plot such a run without `-min_dt` and you are plotting the wrong prior. The rule is stated for no specific command and the example the page gives is a `-plotRJ` line: **not documented** whether it also binds `-plot`/`-plot2` on the old-format log. **Inferred, not stated anywhere on the page:** that the figure then mislabels its own bins — so record the `-min_dt` you plotted with, and check it against `<stem>_sum.txt`, "Text file providing the complete list of settings used in the analysis" (`references/summarize-results.md`:16) |
| `-mProb`, on any log | **Look at your own log's header first** — e.g. `head -1 file_mcmc.log \| tr '\t' '\n' \| grep -n k_` (an `inferred` procedure: no mirror prints a header row of `*_mcmc.log` — see the table Not documented in this wiki below). The corpus contradicts itself about whether the shift-count columns exist outside BDMCMC: `references/summarize-results.md`:20 logs `k_birth`/`k_death` "only logged in BDMCMC analyses", the command entry on the same page reads "Takes the posterior samples logged in a BDMCMC analysis" (`references/summarize-results.md`:64), and yet `../pyrate-rjmcmc/references/tutorial-3.md`:63-65 applies `-mProb` to the RJMCMC `mcmc.log` whose own column list does include the two columns (`:55`). Unresolved (see Pitfalls), so the column check is the only tie-breaker available to you: no `k_*` column in your log means the command has nothing to count |

## Burn-in when summarising (`-b`)

Three rules, from three pages, that must be applied together:

1. **`-b` counts samples, not generations**: "`-b 1000`  (first 1,000 samples are discarded)" (`command-list.md`:72) and,
   at `-s 1000`, "the flag `-b 200` indicates that the first 200 samples will be removed (i.e. the first 200,000 iterations,
   if the sampling frequency was set to 1,000)" (`../pyrate-bd-analysis/references/tutorial-1.md`:213, repeated verbatim at
   `../pyrate-rjmcmc/references/tutorial-3.md`:67).
2. **`-b` between 0 and 1 is a fraction**: "When set to a number between 0 and 1, it is interpreted as a fraction of the
   total number of MCMC generations" (`command-list.md`:69), e.g. `-b 0.10` "the first 10% of the samples are discarded"
   (`:73`) and the BDNN tutorial's `-ginput ... -b 0.25` (`../pyrate-bdnn/references/tutorial-bdnn.md`:477).
3. **The default is per-command and inconsistent across the docs** — `-plot` "by default set to 1"
   (`summarize-results.md`:40), `-mProb` "by default set to 0" (`:64`), while the global option list says
   "`-b 0`  (default; all samples are logged)" (`command-list.md`:71). Treat any summarising run without an explicit
   `-b` as un-trimmed, and set `-b` from the Tracer ESS/burn-in inspection rather than from the default
   (`summarize-results.md`:40, `:64`). Convergence, tuning, ESS targets and chain length are owned by
   **`pyrate-mcmc-tuning`**; this skill only governs the `-b` you hand to the summarising commands.

**Corpus conflict, unresolved (`-b` units):** the `-b` definition itself opens "Set the number of iterations to be
discarded (i.e. not logged) from the analysis as burnin" (`command-list.md`:69), while its own examples and both tutorials
count *samples* (`:71-73`; `tutorial-1.md`:213). The sample reading is the only one the docs spell out arithmetically, so
this skill uses it — but state which unit you assumed when reporting a burn-in, because the page that defines the flag does
not use it.

## Extracting times of origination and extinction (`-ginput`)

"Estimated times of origination and extinction are used as input files for PyRateContinuous and other analyses in the
PyRate package" (`tutorial-2.md`:23). Both routes start from a `*_mcmc.log`; both use `-b` for burn-in
(`tutorial-2.md`:27-31).

| Route | Command shape (printed by the docs) | Output table | Use it when |
| --- | --- | --- | --- |
| Mean times | `python PyRate.py -ginput .../Canidae_1_G_mcmc.log -b 100` (`tutorial-2.md`:29) | one row per species, 4 columns: clade (0 unless MCDD), arbitrary numeric species id, time of origin, time of extinction (`tutorial-2.md`:24) | a single point estimate per lineage is enough |
| Mean times, whole directory | `python PyRate.py -ginput .../path_to_log_files -b 100` → "each file with extension `*_mcmc.log` will be processed separately" (`tutorial-2.md`:41-43) | one table per log | you want per-replicate tables |
| Replicates combined | `python PyRate.py -ginput .../path_to_log_files -tag Canidae -b 100` (`tutorial-2.md`:47) | one table, "columns with the origin and extinction of each species given for each replicate" (`tutorial-2.md`:49) | downstream replicate selection with `-j`, LTT shading from the replicate spread |
| Multiple posterior samples | `python PyRate.py -ginput .../Canidae_1_G_mcmc.log -b 100 -resample 10` (`tutorial-2.md`:55) | "will sample ten times of origination and extinction and store them in the resulting text file as additional columns" (`tutorial-2.md`:57) | propagating dating/topology uncertainty into a downstream analysis instead of the mean |
| Replicates + samples | `python PyRate.py -ginput .../path_to_log_files -tag Canidae -b 100 -resample 10` → "will sample ten values from each file and concatenate them in one table" (`tutorial-2.md`:60-62) | concatenated columns | many replicates × many draws |

Downstream readers of that table: `-d` for PyRateContinuous (`tutorial-2.md`:102), `-d … -ltt` for the range-through
trajectory (`tutorial-2.md`:68), `-d` for a new PyRate/RJMCMC run
(`../pyrate-rjmcmc/references/tutorial-3.md`:39), MCDD input (`../pyrate-diversity-dependence/references/tutorial-4.md`:24-28)
and BDNN (`../pyrate-bdnn/references/tutorial-bdnn.md`:477-482). Note what `-d` does to the model:
"This option automatically sets `-fixSE = null` (see PyRate command list), meaning that the estimation of preservation rates and times of speciation/extinction are switched off"
(`../pyrate-command-reference/references/command-list.md`:18) — a re-run from a times table is a different model, not a
continuation of the first one. See `../assets/files/sum-se_est-FORMAT.txt` for the column layout; the corpus never prints
a data row or the header labels of this file. Two fixtures elsewhere in the suite show what the *repo* (not these docs)
uses — `../assets/files/cmdref-SE-table.txt`, extracted verbatim from upstream `example_files/Ursidae_SE.txt`, heads its
four columns `clade species ts te`, while `../assets/files/cont-se-est.txt` heads them `clade id origination extinction`
and carries no provenance line. Treat both as shapes, not as documentation: no page states the header labels.

## Range-through diversity trajectory (lineage-through-time plot)

`python PyRate.py -d Canidae_1_G_se_est.txt -ltt 1` (`tutorial-2.md`:68) → mean diversity through time with the
min–max range across replicates shaded, plus the diversity-trajectory table and the R script (`tutorial-2.md`:70).
`-ltt 2` log10-transforms diversity (`:74-76`); `-ltt 3` draws each replicate as its own line (`:79-81`); `-grid_plot 0.1`
refines bins from the default 1 time unit (`:83-88`). What the docs say about the output is only this: it is a plot of
"range-through diversity" (`:66`) built from the times table, i.e. counts of lineages whose estimated origin–extinction
intervals span each bin. **Inference, not stated anywhere on the page:** that those counts therefore inherit the preservation
model of the upstream run (the `*_TS`/`*_TE` columns come from it, `summarize-results.md`:20) — no mirror discusses how
preservation modelling affects an LTT curve, and no bias correction is documented.

## Combining replicates

On the summarise page, replicate combination is a **plotting** operation: `-tag` "Specify which files should be combined
in the RTT plot" (`summarize-results.md`:54), e.g. `-plot path_to_pyrate_results -tag rhinos` (`:56`), optionally capped
by `-root_plot`/`-root_age` (`:58-61`). In tutorial #2 the same flag combines replicates **in the times table**
(`-ginput … -tag Canidae`, `tutorial-2.md`:45-49). Combining the logs themselves is not on this page: `-combLog`
(`../pyrate-bd-analysis/references/tutorial-1.md`:227) and `-combLogRJ` with `-col_tag`
(`../pyrate-rjmcmc/references/tutorial-3.md`:96-110) are owned by `pyrate-bd-analysis` and `pyrate-rjmcmc` — though the Related-skills bullet of `../pyrate-bd-analysis/SKILL.md` routes `-combLog` and `-plotQ` back *here*, so the
suite currently disagrees about who owns them; the commands are printed only in tutorial #1 (`:227`, `-plotQ` at `:239-241`),
never on the summarise page. Compute ESS
per replicate, not from a combined log (`../pyrate-bd-analysis/references/tutorial-1.md`:205-206).

## Worked example

The `.../` paths are the docs' own placeholders — substitute the files your run wrote. Every command line below is printed
verbatim by a mirror *except* the two marked `assembled` (they combine flags the docs print separately). Step 0 is real from
this skill directory; steps 1-7 are the documented sequence for one analysis.

```sh
# 0) what the docs print, with the mirror line each command came from
grep -n '' ../assets/files/sum-postprocess-commands.txt               # every documented command + its mirror line
grep -v '^#' ../assets/files/sum-output-files-index.txt | column -t -s'|'   # the files a run should have left

# 1) the data set itself (prints on screen; summarize-results.md:10) - line verbatim from ../pyrate-bd-analysis/references/tutorial-1.md:45
python PyRate.py '.../Canis_pbdb_data_PyRate.py' -data_info

# 2) after the run, list what appeared and check mixing in Tracer BEFORE summarising
ls .../pyrate_mcmc_logs                                                 # ../pyrate-bd-analysis/references/tutorial-1.md:194 (the folder the run writes)
#    no *_marginal_rates.log in that listing, and the run was -A 4? The file is opt-in there: it is only written when the
#    analysis carried -log_marginal_rates 1 (../pyrate-rjmcmc/references/tutorial-3.md:51, :60) - see check 1 above;
#    otherwise plot sp_rates.log / ex_rates.log with -plotRJ (:57, :71)

# 3) model probabilities from a BDMCMC (-A 2) log; -b counts SAMPLES (../pyrate-bd-analysis/references/tutorial-1.md:213) - verbatim from ../pyrate-bd-analysis/references/tutorial-1.md:211
python PyRate.py -mProb .../Canis_pbdb_data_mcmc.log -b 200

# 4) rates-through-time: one file (../pyrate-bd-analysis/references/tutorial-1.md:218, path completed with the logs folder), then
#    a tagged set capped to the Neogene - ASSEMBLED from summarize-results.md:61 (-tag/-root_age) + ../pyrate-command-reference/references/command-list.md:73 (-b fraction)
python PyRate.py -plot .../pyrate_mcmc_logs/Canis_pbdb_data_marginal_rates.log -b 200
python PyRate.py -plot .../pyrate_mcmc_logs -tag Canis_pbdb -b 0.1 -root_age 23

# 5) origination/extinction times for the next program - all three verbatim from tutorial-2.md:29, :47, :60
python PyRate.py -ginput .../Canidae_1_G_mcmc.log -b 100
python PyRate.py -ginput .../path_to_log_files -tag Canidae -b 100
python PyRate.py -ginput .../path_to_log_files -tag Canidae -b 100 -resample 10

# 6) range-through diversity trajectory from that table - verbatim from tutorial-2.md:68 and :86
python PyRate.py -d Canidae_1_G_se_est.txt -ltt 1
python PyRate.py -d Canidae_1_G_se_est.txt -ltt 1 -grid_plot 0.1

# 7) model comparison from two TI runs - the file names are summarize-results.md:69's own placeholders
python PyRate.py -BF .../file_1_marginal_likelihood.txt .../file_2_marginal_likelihood.txt
```

Expected artefacts: `_RTTplot.r`/`_RTTplot.pdf` for steps 4 (needs `RScript` on `PATH`, `../pyrate/references/home.md`:84),
`_se_est.txt` + LTT PDF + R script for step 5, and the LTT PDF + diversity table + R script for step 6
(`summarize-results.md`:40; `tutorial-2.md`:31-35, `:70`).

## Pitfalls

- **`-mProb` is described for BDMCMC but used on RJMCMC logs.** This page: "Takes the posterior samples logged in a
  BDMCMC analysis"; `../pyrate-rjmcmc/references/tutorial-3.md`:63 applies it to the RJMCMC `mcmc.log` and `:55` lists
  `k_birth`/`k_death` in that log, contradicting "only logged in BDMCMC analyses" here (`:20`). Report which page you
  followed; the corpus does not settle it. Until it is settled, resolve it on your own data: check the header of *your*
  `mcmc.log` for the two `k_` columns before running `-mProb` (check 3 of Three pre-flight checks) — the command counts
  sampled shift numbers, so with no such column in the file there is nothing for it to report.
- **`-root_plot` vs `-root_age`**: the section is `-root_plot`, its own example and this skill's Worked example use
  `-root_age` (`:61`), while `../pyrate-rjmcmc/references/tutorial-3.md`:84 uses `-root_plot 23 -min_age_plot 5.3`.
  Nothing reconciles them.
- **`se_est.txt` vs `se_ext.txt`**: `tutorial-2.md`:33 names the output `Canidae_1_G_se_est.txt`; `:45` and `:49` name the
  replicate-combined output `...se_ext.txt` and `:66` hands that same `...se_ext.txt` name to `-d`; every other page in the
  corpus uses `_se_est.txt`
  (`../pyrate-continuous-covariates/references/pyratecontinuous.md`:16, `../pyrate-bdnn/references/tutorial-bdnn.md`:482).
  Use the file your run actually wrote (`ls`), not the name from the prose.
- **Which program runs `-ginput`**: `tutorial-2.md`:29,`:41`,`:47`,`:55`,`:60` all invoke `python PyRate.py -ginput …`,
  while `pyratecontinuous.md`:16-18 invoke `python PyRateContinuous.py -ginput …` (and `:17` drops the `-ginput` flag
  entirely). Both programs are shown; the tutorial form is what this skill's examples use.
- **A duplicated `-b`**: `tutorial-2.md`:122 prints `-b 100 -plot ...log -b 200`. The docs never say which one the plot
  uses ("The command `-b 200` specifies that the first 200 samples are discarded as burnin", `:124`). Pass `-b` once.
- **`-mL` is two different options.** On this tutorial it computes marginal likelihoods in PyRateContinuous
  (`tutorial-2.md`:153-157); in the option list `-mL` sets "the number of speciation rates through time"
  (`../pyrate-command-reference/references/command-list.md`:111-113). Never assume from the token alone.
- **Default algorithm**: this page carries two NOTEs about "the default output for PyRate analysis using `-A 4`" (`:25`,
  `:36`) — i.e. it assumes an `-A 4` run may be what you summarise — but the option list labels `-A 2` "(default)" (`command-list.md`:52) while `../pyrate-bd-analysis/references/tutorial-1.md`:174 says "using `-A 4` (or omitting the flag) will set the algorithm to RJMCMC". Since the algorithm decides which files exist, record
  `-A` explicitly in every run.
- **`-data_info` "plots" but names no output file**: it is described as a screen dump of five statistics (`:10`); the page
  never says whether anything is also written to disk. If you need it in the paper's supplement, capture stdout with `>`
  (the redirect is arithmetic on your shell, not a documented option).
- **The interpreter you launch these commands with is unsettled**: `../pyrate/references/home.md`:69 says PyRate was tested "using Python 2.6 – 2.7" while the tutorial-0 setup says to add the folder "in which Python 3.x is installed" to `PATH` (`../pyrate-installation/references/virtual-environment.md`:54). This skill prints the docs' own `python PyRate.py …` form; resolve the environment in `pyrate-installation` before blaming a summarising command for a `SyntaxError`.
- **Quoted wording drift**: the CN twin `references/summarize-results-cn.md`:41 renders the `-plot` burn-in default
  identically ("默认设为 1"), so it does not resolve the `1` vs `0` conflict in hazard 4 — both languages carry it.

## Not documented in this wiki

| Unanswered question | Why you must not fill it in |
| --- | --- |
| The literal header row (and thus parse-by-position) of `*_mcmc.log` and `*_marginal_rates.log` | no mirror prints a data row of either file; only prose (`:19-20`, `:23`) and three header names via `-col_tag posterior root_age death_age` (`../pyrate-rjmcmc/references/tutorial-3.md`:110) — `death_age` is defined nowhere |
| The numeric cut-offs for the four `-BF` support categories | `:68` names the categories and cites Kass and Raftery (1995) but gives no thresholds; the logBF = 2 / logBF = 6 dashed lines in `../pyrate-rjmcmc/references/tutorial-3.md`:75 belong to `-plotRJ` shift histograms, not to `-BF` |
| The file names of the `-ltt` and `-ginput` PDF/R-script outputs | `tutorial-2.md`:35 and `:70` say only "a **pdf file**", "the **R script**", "a **table with the estimated diversity trajectory**" |
| Whether `-plot` accepts `-resample`, and what `-root_plot` defaults to when combining files | `-resample` is documented for `-ginput` (`tutorial-2.md`:52) and `-combLogRJ`/BDNN only; `:59` describes `0` and `n>0` but never a default |
| Which `-b` wins when it appears twice (`tutorial-2.md`:122) | the page glosses only the second one; no precedence rule exists anywhere in the corpus |
| Whether `-mProb` is valid on an RJMCMC log, and what it prints exactly | `:64` restricts it to BDMCMC, `../pyrate-rjmcmc/references/tutorial-3.md`:63 uses it on one; the printed table's columns are never shown |
| What `-plot` does when the directory holds logs with different bin sizes or time spans | `:40` defines only per-file and `-tag` behaviour |
| Behaviour when `-b` exceeds the number of samples in the log | no error text appears anywhere in this corpus |
| Whether `_sum.txt` records the `-b`/`-out` values used for a post-processing run | `:16` says "settings used in the analysis", not used in the summarising command |
| Whether the summarize-page commands accept PyRateDES/PyRateMBD logs | PyRateDES has its own summariser (its `-sum` command line is at `../pyrate-des/references/tutorial-5.md`:206) and is a different program |

## Related skills

- `pyrate-mcmc-tuning` — convergence, ESS, chain length, `-n`/`-s`/`-p`, tuning parameters, `-fast_burnin`: everything about *whether* a log may be summarised.
- `pyrate-rjmcmc` — the `-A 4` default output set (`sum.txt`, `mcmc.log`, `sp_rates.log`, `ex_rates.log`), `-log_marginal_rates 1`, `-plotRJ`, `-combLogRJ`, `-min_age_plot`, `-min_dt` when plotting.
- `pyrate-command-reference` — the authoritative option list: `-b` (count/fraction/default), `-out`, `-wd`, `-j`, `-d`, `-A`, `-n`, `-s`, `-p`, `-singleton`.
- `pyrate-bd-analysis` — the tutorial-1 run-then-summarise workflow, `-data_info` on a real input, `-combLog`, `-plotQ` (preservation rates), the `pyrate_mcmc_logs` folder.
- `pyrate-continuous-covariates` — the wiki-side `-ginput` page, PyRateContinuous `-plot`, `-mL`, and the `Gl`/`Gm`/`L0`/`M0` log columns.
- `pyrate-input-file` — building the `*_PyRate.py` occurrence input that `-data_info` reads; the `-d` times table as an alternative input.
- `pyrate-preservation-models` — `q_rate`, `alpha`, and the TPP `q_0…q_n` columns of the log.
- `pyrate-trait-age-models` — `cov_sp`, `cov_ex`, `cov_q` (Covar) and age-dependent extinction.
- `pyrate-diversity-dependence` / `pyrate-bdnn` — downstream consumers of the `_se_est.txt` table (MCDD clade column; BDNN back-transformation).
- `pyrate-des` — PyRateDES's own output naming and `-sum`.
- `pyrate-installation` — Python 2.7 and `RScript` on `PATH`, without which `-plot` writes a script and no figure.

## Resources

| File | What's in it | Load when |
| --- | --- | --- |
| `references/summarize-results.md` | The whole wiki page: `-data_info`; the output-file descriptions (`_sum.txt`, `_mcmc.log` column list, `_marginal_rates.log`, `_marginal_likelihood.txt`); `-plot`, `-plot2`, `-tag`, `-root_plot`, `-mProb`, `-BF` with every example line | Any question about what a PyRate file contains or what a summarising command writes |
| `references/summarize-results-cn.md` | Full Simplified-Chinese translation of the same page: every `#####` file/command heading, every command line and every `-b` default kept as in the English; prose and `###` section titles translated | When an English sentence about a default or a bin size is ambiguous — it does **not** resolve the `-b` default conflict (`:41` "默认设为 1" vs `:65` "默认设为 0") |
| `references/tutorial-2.md` | Tutorial #2: extracting origination/extinction times (`-ginput`, `-tag`, `-resample`), range-through diversity/LTT (`-d`, `-ltt 1/2/3`, `-grid_plot`), PyRateContinuous run/plot/`-mL`/TI | The times-table route, LTT plots, or any PyRateContinuous post-processing command |
| `references/tutorial-2-cn.md` | Chinese twin of tutorial #2: same 13 headings by structure (text translated), same command lines byte-for-byte | Cross-checking the meaning of `-resample`, `-ltt 2/3` and the replicate wording |
| `../pyrate-command-reference/references/command-list.md` | `-d`, `-wd`, `-j`, `-out`, `-singleton`, `-A`, `-n`, `-s`, `-p`, `-b` definitions | Any option's default, unit or side effect |
| `../pyrate-bd-analysis/references/tutorial-1.md` | Output folder, `-data_info` on a real file, Tracer/ESS guidance, `-mProb`, `-plot`, `-combLog`, `-plotQ` | The full run → summarise workflow around a real analysis |
| `../pyrate-rjmcmc/references/tutorial-3.md` | RJMCMC's "4 output files" list (including the `marginal_rates.log` contradiction), `-log_marginal_rates 1`, the `-min_dt` bin-duration prior (`:44`, `:46`) that must be repeated when plotting (`../pyrate-rjmcmc/references/tutorial-3.md`:89-91), `-mProb` on an RJMCMC log, `-plotRJ`, `-root_plot`/`-min_age_plot`, `-combLogRJ`, `-col_tag` | Your `-A 4` run left (or did not leave) a `marginal_rates.log` and you need to know which, or you are plotting a `-min_dt` run |
| `../pyrate-continuous-covariates/references/pyratecontinuous.md` | The wiki's `-ginput` section and the times-table format spec | Deciding which program hosts `-ginput`, or naming of `_se_est.txt` |
| `../pyrate/references/home.md` | Invocation form and the `RScript` PATH requirement for `-plot` (R 2.x/3.x note for `pyrate_utilities.r`) | `-plot` produced an `.r` file and no `.pdf` |

```sh
# run these from this skill directory
grep -n "produces three output files\|is replaced by the following" references/summarize-results.md
grep -n "by default set to 1\|by default set to 0\|minimum root age across all log files" references/summarize-results.md
grep -n "k_birth\|tot_length\|shift_sp_1" references/summarize-results.md
grep -n "^##### \`-" references/summarize-results.md
grep -n "discarded as burnin\|as additional columns\|individual lines\|0.1 Myr time bins" references/tutorial-2.md
grep -n "se_ext.txt\|se_est.txt\|se\\\\_est.txt" references/tutorial-2.md
grep -n "烧录期比例\|默认设为 1" references/summarize-results-cn.md
grep -n "默认设为 0\|缩放因子" references/summarize-results-cn.md
# the three pre-flight checks, each at its mirror line (51/59/60 opt-in rates log; 44/46/89/91 -min_dt; 63-65 -mProb)
grep -n "produce 4 output files\|log_marginal_rates\|minimum duration between time bins\|min_dt\|mProb" ../pyrate-rjmcmc/references/tutorial-3.md
grep -n "only logged in BDMCMC analyses\|^-mProb\|mProb" references/summarize-results.md
head -1 .../your_run_mcmc.log | tr '\t' '\n' | grep -n k_     # do you actually have k_birth/k_death? (inferred check)
```

## Runnable fixtures (`../assets/files/`)

All four are documentation extracts, not analysis data. **No mirror in this corpus prints a single body row or header line of
`*_mcmc.log`, `*_marginal_rates.log` or the `-ginput` times table** (the only column names anywhere are the prose of
`summarize-results.md`:19-20 / `tutorial-3.md`:55 and the `-col_tag` example), so the format sheets below are positional
layouts, each with its own `# source:` / `# shows:` header and a `# WARNING`/`# NOTE` marking what is inferred. Other tables
of the corpus *do* print real rows (occurrence tables in `../pyrate-input-file/references/preparing-input-file.md`, the
PyRateMBD predictor table in `../pyrate-diversity-dependence/references/tutorial-4.md`:54-60) — those are other skills'
fixtures, not evidence about these three files.

| File | Run it? | What it makes concrete |
| --- | --- | --- |
| `../assets/files/sum-postprocess-commands.txt` | as a command catalogue (`grep -n ''` on it) | every summarising/post-processing command line printed by the two English mirrors, verbatim, each tagged with its mirror line — `derived` (backticks, the leading `Example:` and the docs' trailing double-spaces removed) |
| `../assets/files/sum-mcmc-log-columns.txt` | no — reference sheet | the 20-odd columns the docs say `*_mcmc.log` holds, with whatever condition the page attaches to each (analysis type, `-A` value, or none) — `derived` from `summarize-results.md`:19-20 |
| `../assets/files/sum-se_est-FORMAT.txt` | no — layout sheet, do not feed to PyRate | the 4-column + replicate/resample-column layout of the `-ginput` output read by `-d`, and the two conflicting file names the docs use for it — `derived` |
| `../assets/files/sum-output-files-index.txt` | yes, as an `ls` checklist after a run | every documented output file name, which analysis writes it and which command reads it, including the `-out`/`-wd` naming rules — `derived` |
