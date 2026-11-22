---
name: pyrate-preservation-models
description: "Choosing, running and testing the fossilization (preservation) model in PyRate: the default non-homogeneous Poisson process NHPP with hat-shaped PERT-distributed lineage rates, the homogeneous Poisson process (-mHPP), the time-variable Poisson process TPP (-qShift with an epochs_q.txt file of epoch-boundary ages, logged as q_0 q_1 ... q_n), and the across-taxon Gamma rate-heterogeneity model (-mG, -ncat, shape parameter alpha) which can be applied to NHPP, HPP and TPP. Covers the preservation hyperprior -pP, tuning -tQ -fU -fS -nT -thread, -fixSE (and -d) switching off the preservation likelihood, the -PPmodeltest maximum-likelihood test across NHPP/HPP/TPP (Gamma not tested), -log_sp_q_rates per-lineage relative rates, -plotQ through-time plots, and marginal-likelihood model comparison with -A 1 thermodynamic integration, -k, -a, -b burnin and *_marginal_likelihood.txt."
---

# PyRate preservation (fossilization) models: NHPP, HPP, TPP and the Gamma model

## Overview

PyRate jointly estimates the birth-death process with **preservation rates**, "describing processes of fossilization, sampling and identification of organisms" (`../pyrate/references/home.md:17`), and the analysis explicitly targets "**preservation rate** and its level of **heterogeneity**" alongside lineage ages and diversification rates (`references/tutorial-1.md:161-165`). Four processes are selectable in `PyRate.py`: **NHPP** (no flag — it is the default, hat-shaped/PERT-distributed through each lineage's lifespan, `references/command-list.md:88`, `references/tutorial-1.md:122`), **HPP** (`-mHPP`, constant through time), **TPP** (`-qShift <epochs file>`, constant within each predefined time frame, varying across them), and the **Gamma model** (`-mG`, plus `-ncat` categories) which adds across-taxon heterogeneity of the mean preservation rate on top of any of the other three (`references/command-list.md:95-102`, `references/tutorial-1.md:142-146`).

The single riskiest assumption this skill governs: **doing nothing is a model choice.** "Note that the NHPP is  used unless differently specified." (`references/command-list.md:88`) — a run that omits `-mHPP`/`-qShift` is already assuming hat-shaped, lineage-specific preservation, and every downstream speciation/extinction estimate is conditioned on it. The docs' own advice on which model to prefer is strong enough to quote exactly: "On most empirical data sets the Gamma model strongly outperforms the  alternative assumption of constant rates" (`references/command-list.md:97`, attributed there to Silvestro et al. 2014, <http://sysbio.oxfordjournals.org/content/63/3/349.long>).

## The 8 things that break a preservation run

| # | What happens | Consequence | Wiki wording (`references/…`) |
| --- | --- | --- | --- |
| 1 | You assume *no flag = no model* | NHPP runs anyway, with lineage-specific hat-shaped rates you did not choose — omitting a flag is a model choice, not an absence of one; the docs state NHPP as the default rather than warning you | "Note that the NHPP is  used unless differently specified." `references/command-list.md:88`; "By default, PyRate assumes an NHPP model" `references/tutorial-1.md:122` |
| 2 | `-qShift` given, epoch file missing/wrong | TPP is not usable without it: "To use this model you need to provide a file containing the times that delimit the different epochs"; the docs print no fallback and no error message (see the section Not documented in this wiki below) | `references/command-list.md:92`; example form `-qShift epochs_q.txt` `references/command-list.md:93` |
| 3 | `-ncat` set without `-mG` | The docs restrict it to Gamma runs: "This command is used only when  running under a Gamma model of preservation (i.e. with `-mG`)" — they never say what PyRate does if you pass it alone | `references/command-list.md:101` |
| 4 | `-fixSE` (or `-d`) is used | The run proceeds "without calculating the likelihood of the  preservation process (NHPP or HPP), but only sampling the parameters  of the birth-death"; `-fixSE null` = first/last appearances. *By inference* the `PP_lik`/`q_rate` columns of such a log are then not an estimated preservation likelihood — no mirror says what is written there | `references/command-list.md:105-106`; `-d` "automatically sets `-fixSE = null`", which switches off "the estimation of preservation rates" `references/command-list.md:18` |
| 5 | `-nT 0` is passed while tuning | Your preservation model is overridden: "speciation/extinction times are set equal to first/last appearances and the preservation model is automatically set to HPP" | `references/command-list.md:240` (default is `-nT 5`, `:241`) |
| 6 | `-A 1` (TI) run with the default `-b 0` | Marginal likelihoods become unusable: "Must be set to a reasonable number when estimating marginal likelihood through TI (see command `-A`)", while the default is `-b 0` (all samples logged) | `references/command-list.md:69`, `:71` |
| 7 | `-pP` left at the fixed prior when several `q` are estimated | The tutorial's own reason to change it is "to reduce the subjectivity of the choice and allow the prior to better adapt to the data"; its remedy is to set the second `-pP` value to `0`, because "PyRate assigns a vague exponential hyper-prior to the rate and samples the rate along with all other model parameters. This approach is recommended whenever multiple preservation rates are estimated" | `references/tutorial-1.md:135`; command `-pP 1.5 0` `references/tutorial-1.md:137`; prose `references/tutorial-1.md:139` |
| 8 | `-PPmodeltest` is read as having tested *your* preservation model | The Gamma model is *not* part of that test: "Note that the Gamma model is not tested here, but we recommend to add it to the best model among NHPP, HPP, or TPP as selected by the model testing." | `references/tutorial-1.md:158` |

## The four processes

| Model | Assumption about the preservation rate `q` | Command the docs print | Source |
| --- | --- | --- | --- |
| **NHPP** (default) | non-homogeneous Poisson process, rates "‘hat-shaped’ (PERT)  distributed" through each lineage's lifespan; the tutorial words it as rates that "change during the lifespan of each lineage following a bell-shaped distribution" | no flag exists — omitting the others selects it | `references/command-list.md:88`; `references/tutorial-1.md:122` |
| **HPP** | "homogeneous Poisson process for preservation rates", i.e. "the preservation rate is constant through time" | `python PyRate.py .../Canis_pbdb_data_PyRate.py -mHPP` | `references/command-list.md:88-89`; `references/tutorial-1.md:124-126` |
| **TPP** | "time-variable Poisson process" where "preservation rates are constant within a predefined time frame, but can vary across time frames (e.g. geological epochs)"; "particularly useful if we expect rate heterogeneity to occur mostly through time, rather than among lineages" | `python PyRate.py .../Canis_pbdb_data_PyRate.py -qShift .../epochs_q.txt` | `references/command-list.md:92-93`; `references/tutorial-1.md:128-132` |
| **Gamma** | "heterogeneity of the mean preservation  rate across the taxa in a data set"; rates "assumed to be distributed according to a gamma  distribution with shape parameter (_alpha_) estimated from the data" | `python PyRate.py .../Canis_pbdb_data_PyRate.py -mG` | `references/command-list.md:96-98`; `references/tutorial-1.md:142-144` |

The three documented Gamma combinations (`references/tutorial-1.md:144-146`, all reproduced in `../assets/files/pres-models_commands.sh`):

```sh
python PyRate.py .../Canis_pbdb_data_PyRate.py -mG                              # [NHPP model]
python PyRate.py .../Canis_pbdb_data_PyRate.py -mHPP -mG                        # [HPP model]
python PyRate.py .../Canis_pbdb_data_PyRate.py -qShift .../epochs_q.txt -mG     # [TPP model]
```

`references/command-list.md:97` states the same rule in prose: "This option can be applied to the NHPP, HPP, and TPP preservation models."

### What the Gamma claim actually says (and how garbled the English is)

The load-bearing sentence, byte-for-byte from `references/command-list.md:97`:

> "On most empirical data sets the Gamma model strongly outperforms the  alternative assumption of constant rates, and across-taxa rate  heterogeneity has been shown to Gamma model accounts to some  extent for temporal changes of the preservation rates [(Silvestro et al.  2014)](http://sysbio.oxfordjournals.org/content/63/3/349.long)."

The clause "has been shown to Gamma model accounts to some  extent" (`references/command-list.md:97`) is not grammatical English — the upstream wiki text is broken there. The Chinese twin resolves the intent: "已有研究表明，跨分类单元的速率异质性在一定程度上可解释保存率随时间的变化" (`references/command-list-cn.md:97`) — i.e. taxon-to-taxon heterogeneity has been shown to account **to some extent** for *temporal* change in preservation. Use the claim as: (a) Gamma usually beats constant-rate preservation on empirical data (attributed to Silvestro et al. 2014, not measured in this wiki), and (b) it partially absorbs time-varying preservation, which is why `-mG` and `-qShift` are alternatives as well as complements. The tutorial's phrasing of (b) is different again — it only says the TPP is for heterogeneity "mostly through time, rather than among lineages" (`references/tutorial-1.md:128`).

## Options reference

Every flag that touches preservation, with the defaults exactly as the mirrors print them. Where the
mirrors print no default at all the cell says so — absence of a documented default is not a default.

| Option | Documented behaviour | Documented default | Source |
| --- | --- | --- | --- |
| `-mHPP` | switch NHPP → HPP | not applied unless specified — "Note that the NHPP is  used unless differently specified." | `references/command-list.md:87-89` |
| `-qShift <file>` | switch to TPP; file holds "the times that delimit the different epochs" | opt-in flag; no default printed | `references/command-list.md:91-93` |
| `-mG` | add Gamma across-taxon heterogeneity to NHPP/HPP/TPP ("To set the Gamma model we add the flag `-mG`") | opt-in flag; no default printed | `references/command-list.md:95-98`; `references/tutorial-1.md:142` |
| `-ncat N` | number of Gamma categories; more = "more variability of the rates across taxa, with comparatively little  effect on the speed of the analysis" | `-ncat 4  (default)` | `references/command-list.md:100-102` |
| `-fixSE <file\|null>` | fix SE times from a previous `mcmc.log` (posterior means) or from first/last appearances (`null`); the preservation likelihood is then not calculated | opt-in flag; no default printed | `references/command-list.md:104-106` |
| `-d <table>` | input route that supplies origin/extinction times; "automatically sets `-fixSE = null`", switching off "the estimation of preservation rates" | alternative to the `*_PyRate.py` input; no default printed | `references/command-list.md:17-18` |
| `-pP shape scale` | wiki: "Shape and scale parameters of the gamma distributed prior on the preservation rate"; tutorial calls the second argument a **rate**, not a scale (see Pitfalls) | `-pP 1.5 1` annotated "(default)" at `references/command-list.md:180` — **but** `references/tutorial-1.md:134` says shape = 1.5 and **rate** = 1.5 | `references/command-list.md:178-180`; `references/tutorial-1.md:134` |
| `-tQ w1 w2` | "Window sizes of the preservation rate (q) and of the shape parameter of the gamma distributed rate heterogeneity (alpha), respectively (multiplier proposals)" | `-tQ 1.2 1.2` (default) | `references/command-list.md:243-245` |
| `-fU a b c` | "Update frequencies for preservation rate, birth-death parameters, and correlation parameters" — "What is left is used for updating speciation and extinction times" — the first number is the preservation update frequency | `-fU 0.02 0.18 0.08` stated only "default under Covar model" | `references/command-list.md:263-265` |
| `-fS f` | frequency of updating BD shift times when BD parameters are updated; "The value will be automatically set to 0 when no rate shifts are being sampled or if the times of shifts are fixed (with command `-fixSE`)" — the `-fixSE` link is why it matters here | `-fS 0.7` (default) | `references/command-list.md:255-257` |
| `-nT N` | max number of SE times updated per iteration; `0` forces first/last appearances **and HPP** | `-nT 5` (default) | `references/command-list.md:239-241` |
| `-thread BD NHPP` | the **second** number threads "the NHPP likelihood" | `-thread 0 0` (default; sequential likelihood calculation) | `references/command-list.md:75-79` |
| `-log_sp_q_rates` | with TPP **and** Gamma: log "the estimated relative preservation rate for each lineage", "one column for each lineage" | opt-in flag; no default printed | `references/tutorial-1.md:149-151` |
| `-PPmodeltest` | maximum-likelihood test of NHPP vs HPP vs TPP; needs the input file plus the TPP shift-time file | opt-in flag; no default printed | `references/tutorial-1.md:154-156` |
| `-plotQ <mcmc.log>` | summarise/plot TPP preservation rates; the epoch file must be passed again — "should be provided as well" | post-run command, no default printed | `references/tutorial-1.md:239-243` |
| `-out <tag>` | tag output-file stems, so parallel preservation-model runs do not overwrite each other | "default stem name" exists; the tag itself is opt-in | `references/command-list.md:32-35` |
| `-A 1` | MCMC with thermodynamic integration writing `*_marginal_likelihood.txt` | `-A 2` printed as the default (`:52`) — contested, see Pitfalls | `references/command-list.md:46-52` |
| `-k N` / `-a x` | TI scaling-factor count and beta shape of those factors; more factors = "improve the accuracy of the estimated marginal likelihood, but require longer computational time" | `-k 10` (default), `-a 0.3` (default) | `references/command-list.md:205-211` |
| `-b n` | burnin discarded; for TI the docs say "Must be set to a reasonable number when estimating marginal likelihood through TI". Unit conflict inside the corpus: "Set the number of **iterations** to be discarded" (`:69`) vs its own example "first 1,000 **samples** are discarded" (`:72`) and the tutorial's "the first 200 samples will be removed (i.e. the first 200,000 iterations, if the sampling frequency was set to 1,000)" (`references/tutorial-1.md:213`). Values between 0 and 1 are "a fraction of the total number of MCMC generations" (`references/command-list.md:69`) | `-b 0` (default; all samples are logged) | `references/command-list.md:68-73`; `references/tutorial-1.md:213` |

Not preservation options, even though they sit in the same blocks: `-pL`, `-pM`, `-N`, `-cauchy`, `-pS` are the birth-death/shift hyperpriors (owned by `../pyrate-bd-analysis/` and `../pyrate-command-reference/`), and `-pC`/`-tC`/`-mCov` are the trait-correlated ones — including `cov_q`, the Covar correlation with **preservation rate** (`references/command-list.md:138-144`), whose tuning window is the **third** `-tC` value ("Window sizes are given for covariation with speciation, extinction, and preservation rates respectively", `references/command-list.md:260`); all of that is `../pyrate-trait-age-models/` territory.

## Hyperpriors belonging to preservation

| Quantity | Prior as documented | Where |
| --- | --- | --- |
| Mean preservation rate `q` | gamma, shape and scale set by `-pP`; "which estimates the expected number of fossil occurrences per lineage per Myr" | `references/command-list.md:179-180` |
| `q` under TPP | "The default prior on the vector of preservation rates is a single gamma distribution with shape = 1.5 and rate = 1.5" — a *single* gamma shared by the vector; change with `-pP 2 0.1` | `references/tutorial-1.md:134` |
| `q` rate estimated from data | set the second `-pP` argument to `0`: "PyRate assigns a vague exponential hyper-prior to the rate and samples the rate along with all other model parameters. This approach is recommended whenever multiple preservation rates are estimated" | `references/tutorial-1.md:137-139` |
| Gamma heterogeneity shape `alpha` | "distributed according to a gamma  distribution with shape parameter (_alpha_) estimated from the data"; tuned through `-tQ`'s **second** window size | `references/command-list.md:96`, `:244` |
| Per-lineage relative rates (TPP+Gamma) | logged only on request with `-log_sp_q_rates`; "the actual rate will depend on the mean preservation rate and it variation through time" (`it` is the doc's typo) | `references/tutorial-1.md:149` |

## Testing between preservation models

Two distinct machineries exist and they are not interchangeable:

**1. `-PPmodeltest` — the documented preservation-model test.** The sentence is broken English again (it reads "A maximum likelihood test across" and then jumps into an inline link), but its content is clear: the test "is available to assess which of NHPP, HPP, or TPP is best supported by the data", and "To run the test you need to provide the input file and the file providing the times of rate shift for the TPP model and add the flag `-PPmodeltest`" (`references/tutorial-1.md:154`, command at `:156`). It is the only preservation-model test the corpus names, it does **not** test `-mG` (`references/tutorial-1.md:158`), and no output file, statistic or decision rule is documented anywhere in these mirrors (see the section Not documented in this wiki below).

**2. TI marginal likelihoods (`-A 1`).** "`-A 1` run an MCMC with thermodynamic integration" — "This analysis computes the marginal likelihood of a birth-death model" and saves it to a `*_marginal_likelihood.txt` file, "that can be use to compare alternative models, e.g. with different number of rate shifts or trait correlations." (`references/command-list.md:49`, including the docs' ungrammatical "can be use"). Every comparison target the docs name is a process/diversification one — different number of shifts, fixed shift ages, trait correlations (`../pyrate-summarize-results/references/summarize-results.md:30`), and in the continuous-covariate tutorial "diversity-dependent models with linear vs exponential correlation" against "temperature-dependent models" (`../pyrate-summarize-results/references/tutorial-2.md:147`) — **preservation models are not named among them anywhere**, and no mirror prints an `-A 1` command carrying a preservation flag. So using TI to rank NHPP/HPP/TPP is by inference from the fact that the preservation process is part of the model whose marginal likelihood is computed. Two hard requirements: `-b` must be non-zero and sensible (`references/command-list.md:69`), and accuracy is driven by `-k` with shape `-a` (`references/command-list.md:205-211`). To compare two runs, take the two `*_marginal_likelihood.txt` files to `-BF`: "The Bayes factor is calculated as twice the difference of log marginal likelihood and the degree of support divided into four categories: negligible, positive, strong, very strong," — that command is owned by `../pyrate-summarize-results/references/summarize-results.md:67-69`.

A practical ordering that stays inside what is documented: `-PPmodeltest` to pick NHPP/HPP/TPP, then add `-mG` to the winner (`references/tutorial-1.md:158`), then use `-A 1` + `-BF` for whatever model comparison you report (`../pyrate-summarize-results/references/summarize-results.md:30`).

## Reading preservation output

Only the preservation-carrying columns and files are in scope here; the log's full column inventory, `*_marginal_likelihood.txt` semantics and post-processing belong to `../pyrate-summarize-results/` (fixture `../assets/files/sum-mcmc-log-columns.txt`), and chain length/ESS/Tracer procedure to `../pyrate-mcmc-tuning/`.

- `mcmc.log` — "Tab-separated table with the MCMC samples of the posterior, prior, likelihoods of the preservation process and of the birth-death (indicated by *PP_lik* and *BD_lik*, respectively), the preservation rate (*q_rate*), the shape parameter of its gamma-distributed heterogeneity (*alpha*)" (`references/tutorial-1.md:199`); the rest of that sentence is BD columns.
- Under TPP, "the preservation rates between shifts are indicated as *q_0, q_1, ... q_n* (from older to younger)" (`references/tutorial-1.md:199`). The epoch file the docs link runs youngest-to-oldest (`../assets/files/pres-epochs_q.txt`), so **how a file line maps onto a `q_i` index is stated nowhere** — check the direction on your own log instead of assuming it.
- `*_sum.txt` — "Text file providing the complete list of settings used in the analysis" (`references/tutorial-1.md:197`, named `*_sum.txt` at `../pyrate-summarize-results/references/summarize-results.md:15`); this is where you confirm which preservation model a log actually came from, which matters because of the `-nT 0` and `-A` surprises above.

## Constraints from elsewhere in the corpus (cross-references)

- `-se_gibbs` (large-dataset Gibbs sampler): "This model only works for preservation models based on homogenous or time-variable Poisson processes (HPP or TPP)" — so **not** NHPP: `../pyrate-rjmcmc/references/tutorial-3.md:122`, with the tuning line `-fQ 0.1 -tQ 1.05 1.05` at `:119` (`-fQ` is never in the wiki command list).
- Age-dependent extinction `-ADE 1`: "Note that only homogeneous Poisson process (HPP) and time-variable Poisson process can be used with the ADE model." — `../pyrate-trait-age-models/references/tutorial-4.md:143`.
- RJMCMC analyses do combine these flags: `python PyRate.py .../Canis_pbdb_data_PyRate.py -A 4 -mHPP -mG` — `../pyrate-rjmcmc/references/tutorial-3.md:35`.
- DES has its own `-mG` wording ("the mean sampling rate across all taxa equals q and the heterogeneity is given by a discretized Gamma distribution with *n* categories", default four usually sufficient, "should therefore be always included in DES models") — `../pyrate-des/references/tutorial-5.md:213`. That is `PyRateDES.py`, not `PyRate.py`: owned by `../pyrate-des/`.
- BDNN: "All standard commands to define the preservation model can be used in combination with the BDNN model" and the tutorial's own runs combine them — `... -qShift ./example_files/BDNN_examples/Carnivora/Stages.txt -mG ...` — `../pyrate-bdnn/references/tutorial-bdnn.md:225-226` (prose) and `:230`, `:472` (commands). Owned by `../pyrate-bdnn/`.

## Worked example

Run from this skill directory, with `PyRate.py` reachable (the docs call `python PyRate.py …` from the PyRate folder — see `../pyrate-installation/`). `$OCC` is any `*_PyRate.py` occurrence file (see `../pyrate-input-file/`); the epoch file is the real fixture this skill owns. Every flag set below is one the mirrors print (only the paths are parameterised, and `-out` tags are added because `references/command-list.md:32-35` exists for exactly that); sources are `references/tutorial-1.md:126,132,137,144-146,151,156,180,186,241` and `references/command-list.md:49,106`. Note that the tutorial's own preservation lines carry no `-A` except `:180` (`-A 2 -mHPP -mG -j 1`) and `:172` (`-A 2` alone) — reproduced as printed below, and per the Pitfalls entry you should pass `-A` explicitly in a real run.

```sh
OCC=/path/to/Canis_pbdb_data_PyRate.py        # your *_PyRate.py input file
EPOCHS=../assets/files/pres-epochs_q.txt      # the delimiter file this skill owns

# 1. The four processes, side by side
python PyRate.py "$OCC" -mG -n 20000000 -s 5000 -out NHPP_G          # NHPP + Gamma (references/tutorial-1.md:186)
python PyRate.py "$OCC" -mHPP -mG -j 1 -out HPP_G                    # HPP  + Gamma (references/tutorial-1.md:180)
python PyRate.py "$OCC" -qShift "$EPOCHS" -mG -out TPP_G             # TPP  + Gamma (references/tutorial-1.md:146)
python PyRate.py "$OCC" -mHPP -out HPP                               # plain HPP    (references/tutorial-1.md:126)

# 2. Or let the documented test choose among NHPP / HPP / TPP for you
python PyRate.py "$OCC" -qShift "$EPOCHS" -PPmodeltest               # references/tutorial-1.md:156

# 3. For TPP, give the shared q prior a data-estimated rate, and log per-lineage relative rates
python PyRate.py "$OCC" -qShift "$EPOCHS" -pP 1.5 0 -out TPP          # references/tutorial-1.md:137
python PyRate.py "$OCC" -qShift "$EPOCHS" -mG -log_sp_q_rates -out TPP_G   # references/tutorial-1.md:151

# 4. Marginal likelihoods (TI). -b "Must be set to a reasonable number when estimating marginal
#    likelihood through TI" (references/command-list.md:69); the fraction form -b 0.10 is printed at :73 and
#    sidesteps the iterations-vs-samples unit conflict (:69 vs :72). -k 10 is the printed default,
#    raise it for accuracy at more time (references/command-list.md:206,207). By inference: the corpus never
#    prints an -A 1 line that carries a preservation flag.
python PyRate.py "$OCC" -A 1 -mHPP -b 0.10 -out HPP_TI                # references/command-list.md:49,69,73
python PyRate.py "$OCC" -A 1 -mHPP -mG -b 0.10 -k 20 -out HPP_G_TI    # -k 20 is illustrative, not a doc value

# 5. Fixing SE times instead of estimating them - no preservation likelihood is computed
python PyRate.py "$OCC" -fixSE /path/to/Ursidae.mcmc.log              # references/command-list.md:106
python PyRate.py "$OCC" -fixSE null                                   # references/command-list.md:105

# 6. What actually ran, then comparison, then the TPP rates through time
head -50 pyrate_mcmc_logs/*HPP_TI_*_sum.txt                            # references/tutorial-1.md:196-197
python PyRate.py -BF pyrate_mcmc_logs/*HPP_TI_*_marginal_likelihood.txt \
                  pyrate_mcmc_logs/*HPP_G_TI_*_marginal_likelihood.txt  # ../pyrate-summarize-results/references/summarize-results.md:69
python PyRate.py -plotQ pyrate_mcmc_logs/*TPP_G_mcmc.log -qShift "$EPOCHS" -b 100   # references/tutorial-1.md:241
```

Step 6's `-plotQ` re-supplies the epoch file because "the file with the times of rate shift (e.g. `PyRate-master/example_files/epochs_q.txt`) should be provided as well" (`references/tutorial-1.md:243`) — although the docs' own `-plotQ` line two lines above it passes `-qShift epochs.txt`, i.e. the *other* example file (`references/tutorial-1.md:241`); see Pitfalls. Step 4's TI-for-preservation comparison is **by inference** (see the section above): the corpus never prints an `-A 1` line carrying a preservation flag.

## Pitfalls

- **`-pP` is documented twice, with a different default *and* a different unit for the second argument.** `references/command-list.md:179-180` says "Shape and **scale** parameters of the gamma distributed prior on the preservation rate" and prints "`-pP 1.5 1` (default)", while `references/tutorial-1.md:134` says the prior is "a single gamma distribution with shape = 1.5 and **rate** = 1.5" and `-pP 2 0.1` "changes the shape to 2 and the rate to 0.1" (`references/tutorial-1.md:134`). For a Gamma distribution scale = 1/rate, so these are not two spellings of one prior — and only the *rate* reading makes `-pP 1.5 0` ("setting the rate parameter to 0", `references/tutorial-1.md:135-137`) meaningful at all. The Chinese mirrors repeat the same disagreement (`references/command-list-cn.md:177-179` vs `references/tutorial-1-cn.md:135`), so it is not a translation artefact. Set `-pP` explicitly whenever the prior matters, record the exact two numbers, and do not assume either default.
- **The `-plotQ` example names the wrong epoch file.** The command line is `PyRate.py -plotQ .../Canis_pbdb_data_mcmc.log -qShift epochs.txt -b 100` (`references/tutorial-1.md:241`) — `epochs.txt` is the *birth-death* shift file (`-fixShift`, `references/command-list.md:124`) — while the note directly below says the rate-shift file "e.g. `PyRate-master/example_files/epochs_q.txt`" "should be provided as well" (`references/tutorial-1.md:243`). Pass the `-qShift` file your run actually used (this skill's `../assets/files/pres-epochs_q.txt`) and check the plot's epoch bounds.
- **The Gamma sentence you may want to cite is broken English** in both the wiki and this mirror (`references/command-list.md:97`); quote the first clause only, and use `references/command-list-cn.md:97` for the second clause's meaning.
- **`-mG` is not an alternative to NHPP/HPP/TPP** — it is an add-on ("NHPP, HPP, and TPP models can all be coupled with a Gamma model of rate heterogeneity", `references/tutorial-1.md:142`); `-ncat` is documented as usable "only when  running under a Gamma model of preservation" (`references/command-list.md:101`, i.e. it does nothing on its own — the exact behaviour of passing it alone is not described), and `-PPmodeltest` will not tell you whether you needed it (`references/tutorial-1.md:158`).
- **`-fixSE`/`-d` runs are not preservation analyses.** They switch the preservation process off: `-fixSE` runs "without calculating the likelihood of the  preservation process (NHPP or HPP)" (`references/command-list.md:105`) and `-d` "automatically sets `-fixSE = null`" (`references/command-list.md:18`). *By inference* — no mirror says what is written to the log — do not mix a `-fixSE` log with ordinary runs when comparing `q_rate` or `PP_lik`.
- **The default NHPP is described two different ways**: its rates are "‘hat-shaped’ (PERT)  distributed" (`references/command-list.md:88`) but they also "change during the lifespan of each lineage following a bell-shaped distribution" (`references/tutorial-1.md:122`). Neither mirror gives the PERT parameters, so do not reconstruct the distribution from the shape word alone.
- **`-nT 0` silently rewrites your model to HPP** (`references/command-list.md:240`); what happens to a `-mG` request in the same run is not stated anywhere (see Not documented).
- **Update-frequency starvation:** the first `-fU` value is the preservation-rate update frequency and "What is left is used for updating speciation and extinction times" (`references/command-list.md:264`); the sibling tuning note `-fQ 0.1 -tQ 1.05 1.05` for many preservation shifts is at `../pyrate-rjmcmc/references/tutorial-3.md:117-119`.
- **The Python version is contested inside this corpus.** The wiki still says "using Python 2.6 – 2.7" and "Please note that Python 3.x is currently not supported" (`../pyrate/references/home.md:69`), while the tutorial mirror says "First, make sure **Python (v.3.10 or higher)** is installed on your computer." (`../pyrate-installation/references/virtual-environment.md:13`, with `python3` noted at `:26`). `../pyrate-installation/` owns that conflict — resolve it there before a long preservation run, and check `*_sum.txt` output for a clean start either way. Separately, `-plot` is documented as generating "an R script that is used to produce a graphic output", "automatically executed by PyRate using the shell command `RScript`" (`../pyrate/references/home.md:84`) — no mirror says the same about `-plotQ`, so a *`-plotQ` produced no figure* failure is first an environment question and second an undocumented one.
- Long runs: `-A 2` (BDMCMC) and RJMCMC estimate the number of BD shifts, `-A 0`/`-A 1` work with a fixed number set by `-mL`/`-mM` (`references/command-list.md:47,51,112,116`; `-A 4` = RJMCMC is documented only in the tutorials, `references/tutorial-1.md:174`, not in the wiki command list). The only place the corpus states that preservation options survive another analysis choice is `references/tutorial-1.md:254` ("The other options described above to set preservation model, length of the MCMC, and sampling frequency are also available in this case", for the `-fixShift` analysis); extending that to every `-A` mode is *by inference*, and note the one documented counter-example below it — `-nT 0` does rewrite the preservation model (`references/command-list.md:240`). Algorithm choice is `../pyrate-rjmcmc/` and `../pyrate-bd-analysis/`'s.
- **Which `-A` is the default is itself contested**, and it matters for TI: `references/command-list.md:52` prints "`-A 2`  (default)" while `references/tutorial-1.md:174` says "using `-A 4` (or omitting the flag) will set the algorithm to RJMCMC". Never rely on omission — pass `-A` explicitly in every preservation run, and check `*_sum.txt` (`references/tutorial-1.md:196-197`) to see what actually ran.

## Not documented in this wiki

| Unanswered question | Why you must not fill it in |
| --- | --- |
| The exact layout the `-qShift` file must have (header? one column? must ages be sorted? how many boundaries are sensible?) | `references/command-list.md:92` only says it contains "the times that delimit the different epochs" and links an example file; **no mirror prints the file's contents**. The bundled `../assets/files/pres-epochs_q.txt` is that linked upstream file (verified byte-identical to it: 32 ages, one per line, no header, no trailing newline) — an observation about one example, not a documented grammar |
| What PyRate does if the `-qShift` file is missing, empty, unsorted, or holds an age outside the data range | the docs state only the requirement (`references/command-list.md:92`) and give the example form (`:93`); no error message, no validation rule, no partial-degradation behaviour appears in any mirror |
| What `-PPmodeltest` writes, what statistic it uses, its degrees of freedom, and how to read its result | only the invocation is printed (`references/tutorial-1.md:154-156`); `grep -rn modeltest references/` returns exactly those two English lines and their CN twins (`references/tutorial-1-cn.md:155,157`), the wiki command list never defines `-PPmodeltest`, and no output file, statistic or threshold is named anywhere |
| Whether TI (`-A 1`) marginal likelihoods are valid for comparing *preservation* models | `references/command-list.md:49` names "different number of rate shifts or trait correlations", `../pyrate-summarize-results/references/summarize-results.md:30` names "different number of shifts, fixed shift ages, trait-correlated rates using the Covar model", and `../pyrate-summarize-results/references/tutorial-2.md:147` (PyRateContinuous) names diversity-dependent vs temperature-dependent models — a preservation-model comparison is never listed as a TI use case, and no `-A 1` command line in the corpus carries a preservation flag |
| Which `-qShift` file `-plotQ` actually wants | the example command passes `-qShift epochs.txt` (`references/tutorial-1.md:241`) while the note below it names `epochs_q.txt` (`:243`); the two files drive different models (BD shift ages vs preservation epochs) — a genuine doc-internal conflict, not a question with a documented answer |
| What `-pP`'s second argument is and what its default is | `references/command-list.md:179-180` calls it a **scale** with default `-pP 1.5 1`; `references/tutorial-1.md:134` calls it a **rate** with value 1.5 (`references/command-list-cn.md:177-179` and `references/tutorial-1-cn.md:135` repeat the split, so it is not a translation artefact). scale = 1/rate means the two readings give different priors; do not pick one silently |
| Whether `-mG`/`alpha` survive `-nT 0` (which forces HPP) | `references/command-list.md:240` states the switch to HPP and nothing else |
| Whether `-mHPP` and `-qShift` may be combined, and which wins | no precedence rule exists in either mirror; `references/command-list.md:88,92` describe them as separate model switches |
| Can `-mG` be used together with `-fixSE` (is `alpha` still sampled once the preservation likelihood is off)? | `references/command-list.md:105` says the preservation likelihood is not computed but says nothing about the Gamma part |
| The name and format of the `-log_sp_q_rates` output file | `references/tutorial-1.md:149` promises "one additional log file containing one column for each lineage" and stops there |
| How `-ncat` discretises the Gamma distribution, and its allowed range | `references/command-list.md:101` gives only the qualitative effect "more variability of the rates across taxa, with comparatively little  effect on the speed of the analysis" |
| The default `-fU` for a non-Covar analysis | `references/command-list.md:265` labels its numbers "default under Covar model" only |
| Whether `-qShift` epochs interact with `-fixShift` epochs (both take an epoch file) | `references/command-list.md:124` (`-fixShift`) and `:92` (`-qShift`) are documented independently, never jointly |
| `-tQ`'s behaviour when `-mG` is off (does the second window size do anything?) | `references/command-list.md:244` names both windows but binds neither to a model |
| Whether a `-b` value counts iterations or logged samples — critical for the `-b` you pass to a TI preservation comparison | the wiki's own sentence says "Set the number of iterations to be discarded" (`references/command-list.md:69`) while its example three lines below, at the end of the same block, says "first 1,000 samples are discarded" (`:72`), while `references/tutorial-1.md:213` says samples and converts to iterations via `-s`; no mirror resolves which reading PyRate implements, so state the units you assumed next to any marginal-likelihood comparison |

## Related skills

- `../pyrate-command-reference/` — owns the full option list (`-A`, `-n`, `-s`, `-b`, `-r`, `-M`, `-B`, …) and the same `command-list.md` mirror; go there for anything outside the Preservation (fossilization) model block at `references/command-list.md:85-106`.
- `../pyrate-input-file/` — the `*_PyRate.py` occurrence file every command above needs, `extract.ages()`/`extract.ages.pbdb()`, the `Site` column, and `-d` origin/extinction tables.
- `../pyrate-bd-analysis/` — the birth-death side of the same tutorial: `-mL`/`-mM`/`-mC`/`-fixShift`, `-N`/`-pL`/`-pM`/`-cauchy`/`-pS` hyperpriors, and the analysis setup.
- `../pyrate-rjmcmc/` — `-A 4`, `-se_gibbs` (HPP/TPP only), `-bound_se`, `-plotRJ`; the algorithm choice your preservation model has to survive.
- `../pyrate-summarize-results/` — owns the wiki "Description of the output files" page (`../pyrate-summarize-results/references/summarize-results.md:12`; `*_sum.txt`, `*_mcmc.log`, `*_marginal_likelihood.txt`) and `-data_info`, `-mProb`, `-plot`, `-plot2`, `-tag`, `-BF`; `-plotQ` and `-combLog` are documented on the tutorial pages this skill mirrors (`references/tutorial-1.md:225-243`), which is where the syntax comes from.
- `../pyrate-mcmc-tuning/` — proposal tuning (`-tT`, `-tR`, `-tS`, `-multiR`, `-fR`) that surrounds `-tQ`/`-fU`.
- `../pyrate-trait-age-models/` — `cov_q` / `-mCov 4` (trait-correlated **preservation** rate) and `-ADE 1`, which also restricts you to HPP/TPP.
- `../pyrate-des/` and `../pyrate-continuous-covariates/` — `PyRateDES.py`'s own `-mG`/`-qtimes` sampling model and `PyRateContinuous.py`'s environmental model: different programs, different defaults.
- `../pyrate-bdnn/` — BDNN inference, whose standard preservation switches stay available (`../pyrate-bdnn/references/tutorial-bdnn.md:225`); its main worked runs pair `-qShift .../Stages.txt` with `-mG` (`:230`, `:472`), though not every BDNN command line in that tutorial carries them.
- `../pyrate-installation/` and `../pyrate/` — the interpreter question (that skill owns the 2.6-2.7 vs 3.10+ conflict flagged under Pitfalls), virtual environments, `numpy`/`scipy`, `Rscript` on `PATH`, and the program map.

## Resources

| File | What's in it | Load when |
| --- | --- | --- |
| `references/command-list.md` | The wiki command list: the "Preservation (fossilization) model" block (`-mHPP`, `-qShift`, `-mG`, `-ncat`, `-fixSE`, lines 85-106), `-A`/`-n`/`-s`/`-b`/`-thread`, `-d`, the (hyper)prior block incl. `-pP`, and the tuning block incl. `-tQ`, `-nT`, `-fU`, `-fS` | Any question about an option name, its documented default, or which block it lives in |
| `references/command-list-cn.md` | Same page in Simplified Chinese. **Do not assume line numbers carry over from the English**: the `-mG` entry merges English `96-97` into a single Chinese line `97`, while `-cauchy` merges English `175-176` into `175`, so the offset changes down the page (Preservation heading is EN `85` / CN `86`, `-ncat` is EN `100` / CN `100`, `-pP` is EN `178-180` / CN `177-179`) | When an English sentence is garbled — it is the only witness for the meaning of the broken `-mG` clause (`:97`) |
| `references/tutorial-1.md` | "Defining the preservation model" (`references/tutorial-1.md:121-158`): the four models with runnable lines, the `-pP` prior prose (`:134-139`), `-log_sp_q_rates`, "Model testing across preservation models" (`references/tutorial-1.md:153`) with `-PPmodeltest`, output files and `mcmc.log` columns (`:194-199`), `-plotQ` (`:238-243`) | Choosing or running a preservation model, or reading its log; anything the command list states too briefly |
| `references/tutorial-1-cn.md` | The same tutorial translated; the `-pP`/`-PPmodeltest`/`-plotQ` passages at `:135`, `:155`, `:240-244` | Checking whether the 1.5/1.5 prior statement is a translation artefact (it is not — both languages say 1.5 and 1.5) |

## grep recipes

```sh
# run these from this skill directory - all eight verified to return hits
grep -n 'NHPP is  used unless differently specified' references/command-list.md
grep -n -A 3 '^##### `-mG`' references/command-list.md
grep -n 'preservation model is automatically set to HPP' references/command-list.md
grep -rn 'shape = 1.5\|-pP 1.5' references/
grep -n 'Gamma model is not tested' references/tutorial-1.md
grep -n 'q_0, q_1, ... q_n' references/tutorial-1.md
grep -n -- "-fS\|-fixSE null" references/command-list.md
grep -n '保存率随时间的变化' references/command-list-cn.md
```

## Runnable fixtures (`../assets/files/`)

| File | Run it? | Provenance / what it makes concrete |
| --- | --- | --- |
| `../assets/files/pres-epochs_q.txt` | yes — as `-qShift` input | `# source: the upstream example_files/epochs_q.txt that this skill links at references/command-list.md:92 (and references/command-list-cn.md:93) \| verbatim`, kept **byte-clean** (no comment header) because PyRate parses it: 32 epoch-boundary ages, one per line, youngest (0.0117) first, oldest (541.0) last, no header row and no terminating newline on the last line. Verified byte-identical to `https://raw.githubusercontent.com/dsilvestro/PyRate/master/example_files/epochs_q.txt` (185 bytes) — the file the docs link, **not** a file the corpus prints, so its layout stays an observation about one example rather than a documented format — it is listed under Not documented in this wiki. The sister fixture `../assets/files/cmdref-epochs_q.txt` (owned by `../pyrate-command-reference/`) holds the same 32 ages, in the same order, behind a 9-line comment header — that header declares the values *synthetic* and says no author of this suite had access to upstream's file, while the sibling's own SKILL.md presents the same file as a verbatim copy of it (and counts 31 ages, not 32); nothing here documents which of those is right, so only this fixture's identity with upstream has been checked. Nothing in the wiki documents whether the parser tolerates comment lines, so pass **this** file to `-qShift`. |
| `../assets/files/pres-models_commands.sh` | yes — run it **from the PyRate directory** (the commands call `PyRate.py`, not `path/to/PyRate.py`): `bash ../assets/files/pres-models_commands.sh /path/to/Dataset_PyRate.py ../assets/files/pres-epochs_q.txt` (needs a real input file and the Python build your `../pyrate-installation/` setup provides — see the Python conflict under Pitfalls) | `# source: PyRate-doc/PyRate-tutorials/tutorials/pyrate_tutorial_1.md lines 113-150 and PyRate-doc/PyRate-wiki/2.-PyRate:-command-list.md lines 77-98 \| derived` — the flags are the docs', the paths are parameterised (`$OCC`, `$EPOCHS`, `$PY`) and a few runs add flags the docs print as *defaults* (`-A 2`, `-n`, `-s`, `-j`, `-out`, `-b`, `-k`) rather than inventing values. Contents: one command per preservation model (default NHPP, HPP, TPP, TPP+`-pP 1.5 0`, `-mG` on each of the three, `-ncat 4`, `-log_sp_q_rates`), the `-PPmodeltest` line, three `-A 1` TI runs, two `-fixSE` runs, and `-plotQ`; every step cites its mirror `file:line` in the comment above it. `bash -n` clean |
