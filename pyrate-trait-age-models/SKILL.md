---
name: pyrate-trait-age-models
description: "Covar trait-correlated diversification, age-dependent extinction (ADE) and the birth-death chronospecies (BDC) model in PyRate.py: the `-trait_file` table (species name + trait value, tab-separated, missing data as `NA` and imputed by the MCMC), the trait column of the `*_PyRate.py` input, `-mCov 1` to `-mCov 5` (cov_sp, cov_ex, cov_q), `-trait`, `-logT 0/1/2`, `-pC` (Normal prior centred in 0 with sd = 1; Gamma(2,2) hyper-prior at `-pC 0`), Covar tuning `-tC` and `-fU`; `-A 1` thermodynamic integration, `*_marginal_likelihood.txt` and `-BF` Bayes factors for comparing a Covar model against a plain BD model, the contested unit of `-b` in that burnin, and reading `cov_*` by 95% HPD against the prior centre 0 (a criterion transferred from `pyrate-continuous-covariates`); `-ADE 1` restricted to HPP/TPP preservation, `-filter` time windows, Weibull shape and scale; BDC with `-tree` (NEXUS), `-bdc`, `-eqr`, `-fixShift` skyline, Dendropy; and the five commands the wiki command list never documents."
---

# Trait-dependent, age-dependent and chronospecies models in PyRate (`-mCov`, `-ADE`, BDC)

## Overview

All three model families live in the same program, `PyRate.py`: **Covar** makes speciation, extinction and/or preservation vary lineage-specifically as a function of a continuous trait through estimated correlation parameters `cov_sp`, `cov_ex`, `cov_q` (`references/command-list.md` 138; `references/tutorial-4.md` 112); **ADE** makes extinction a function of *species age* instead of a constant, and reports the shape and scale of a Weibull distribution (`references/tutorial-4.md` 145, 149); **BDC** jointly analyses fossil occurrences and a tree file in NEXUS format under a birth-death chronospecies process (`references/tutorial-4.md` 152-169; the docs never say the tree must be time-calibrated, however obvious that is for a chronospecies model). Covar is the only one of the three that has a section on the wiki command list ("Settings for trait correlated rates (Covar models)", `references/command-list.md` 129-155); `-ADE`, `-filter`, `-tree`, `-bdc` and `-eqr` appear *nowhere* on that page — they are documented only by the tutorial's prose and command lines (verified: `grep` finds no entry; see the recipes).

The single riskiest thing here is the trait table, not the model: `-trait_file` requires species names "identical to those used in the PyRate file" (`references/command-list.md` 133) and treats a species as missing-data if you write `NA`, while leaving it out of the table altogether is described in the same breath as an equivalent option ("Species for which trait data are not available can be omitted from the table. Alternatively, they can be included in the table with trait value `NA`", `references/command-list.md` 133) — yet the sentence "These species will be still included in the analysis, but their trait value will be imputed by the MCMC" grammatically covers only the `NA` rows. Neither the English nor the Chinese mirror says what happens to omitted species, so a Covar run silently analysed a taxon subset rather than an imputed trait is a real, undetectable-from-the-docs failure mode (see the section titled 'Not documented in this wiki' below).

## The nine things that break a run

| # | What happens | Consequence | Wiki wording |
| --- | --- | --- | --- |
| 1 | Running `-ADE 1` while leaving the preservation model at its default | ADE cannot be used with the default preservation model: "Note that the NHPP is  used unless differently specified." (`references/command-list.md` 88, note the doc's double space) while ADE allows only two models | "Note that only homogeneous Poisson process (HPP) and time-variable Poisson process can be used with the ADE model." (`references/tutorial-4.md` 143) |
| 2 | Trait-table species names differing from the PyRate input names (spacing, synonyms, `_` vs space) | **No consequence is documented**: the corpus prints no name-check, no error and no warning message for a mismatch, so assume silent misbehaviour (inference from the absence, not from any doc statement) | "The first column of the table should include the species names (identical to those used in the PyRate file)" (`references/command-list.md` 133; `references/tutorial-4.md` 103) |
| 3 | Dropping a taxon from the trait table instead of writing `NA` | Undocumented whether the taxon is dropped from the analysis or imputed; the two readings differ in the number of taxa modelled | "Species for which trait data are not available can be omitted from the table." (`references/command-list.md` 133) |
| 4 | Copying the tutorial's `-logT 10`, or pre-transforming the trait yourself | `10` is outside the documented value set `{0,1,2}` and no page says what PyRate does with an undefined value; and `-logT 2` (log10) is already the command-list default, so a hand-log-transformed table plus the default transformation double-transforms (inference from the documented default, not a documented warning) | "`-logT 2` trait is log10 transformed (default)" (`references/command-list.md` 155) vs `-logT 10` (`references/tutorial-4.md` 124) |
| 5 | `-pC 0` on a single-parameter Covar model (`-mCov 1`, `2` or `4` — by inference: each of those estimates exactly one of `cov_sp`, `cov_ex`, `cov_q`, `references/command-list.md` 140-144) | Both pages state the *same* rule ('at least 2' = 'more than one'), but the command list's own enumeration is broken text: it ends "i.e. using [`-mCov 2` or `-mCov`]" with the second value's number missing, so the page literally names a one-parameter model while its rule forbids it | "This option should only be used if at least 2 correlation parameters are being estimated, i.e. using [`-mCov 2` or `-mCov`]" (`references/command-list.md` 187) vs "this option is generally preferred when more than one correlation parameters are estimated (i.e. with `-mCov 3` or `-mCov 5`)" (`references/tutorial-4.md` 120) |
| 6 | Comparing a Covar and a plain BD model by TI (`-A 1`) with the default burnin | Marginal likelihoods come from a chain that logged its whole burnin, and the docs make a non-zero `-b` a requirement for TI. The *unit* of `-b` is contested even inside one page — iterations in the definition, samples in the very next examples — so the count you type is not the cut you get (step 2 of the worked example therefore passes a fraction) | "Must be set to a reasonable number when estimating marginal likelihood through TI (see command `-A`)" (`references/command-list.md` 69); `-b 0` is the default (`references/command-list.md` 71); "`-b 1000`  (first 1,000 samples are discarded)" (`references/command-list.md` 72) vs "Set the number of iterations to be discarded" (`references/command-list.md` 69) |
| 7 | BDC without the Dendropy library in the interpreter PyRate actually runs on — and the corpus does not settle which that is: Home pins 2.6-2.7 (`../pyrate/references/home.md` 69) while the install tutorial requires 3.10+ (`../pyrate-installation/references/virtual-environment.md` 13); `pyrate-installation` owns that conflict | The `-tree` analysis cannot run (inference from the word 'requires'; the docs print no import error or message), and the version you must install Dendropy into is precisely the disputed part | "Note that this function requires the [Dendropy library](https://dendropy.org)." (`references/tutorial-4.md` 160) |
| 8 | Believing a BDC run models one shared birth-death process | By default fossil and phylogenetic data get **independent** rate parameters; `-bdc`/`-eqr` are what couple them | "By default the analysis assumes a constant rate birth-death model with independent rate parameters between fossil and phylogenetic data." (`references/tutorial-4.md` 162) |
| 9 | Running the Covar model and its plain-BD comparator in the same output directory | Output files (including `*_marginal_likelihood.txt`) overwrite each other, so the Bayes factor compares two runs you can no longer tell apart | "This command is useful to avoid overwriting output files when running several instances of the same analysis." (`-out`, `references/command-list.md` 33) |

## Covar: trait-correlated diversification

"PyRate implements birth-death models in which speciation and extinction rates change in a lineage-specific fashion as a function of an estimated correlation with a continuous trait (Covar models)" (`references/tutorial-4.md` 99; the command-list section opens with the same sentence minus the `(Covar models)` parenthetical, `references/command-list.md` 130). Both pages cite the model with nothing but a bare link — "The model is described [here]" to `http://onlinelibrary.wiley.com/doi/10.1111/2041-210X.12263/abstract` — so the paper is never named in prose anywhere in this corpus: no author, no year, no title, no journal. The only identifier the docs print is the DOI fragment embedded in that URL, which resolves outside the wiki; do not cite a citation the corpus does not contain.

### Two routes to the trait values

| Route | How PyRate gets the trait | Source |
| --- | --- | --- |
| Inside the input file | The `*_PyRate.py` file may hold "one or more continuous traits"; then "the trait values will be read directly from the python file when using the command" `-mCov` | `references/command-list.md` 13, 130 |
| Separate table | `-trait_file path/to/table.txt`, a "tab-separated text file": column 1 = species names identical to the PyRate file, column 2 = trait values | `references/command-list.md` 132-133, `references/tutorial-4.md` 103 |

Which trait is used when the input file carries several: `-trait` (default `1`, "it takes first trait", `references/command-list.md` 146-148). The two trait sources are introduced as alternatives ("Alternatively, a table with the trait data can be provided as a separate file using the command `-trait_file`", `references/command-list.md` 130), but that word is not a precedence rule: nothing in either mirror says which source wins if both an in-file trait and a `-trait_file` table are present.

Missing data: `NA` in the trait column keeps the species in the analysis with its trait value imputed by the MCMC (`references/command-list.md` 133). The input-file page owns the parallel rule for the trait column of the occurrence table — "note that here, missing data are allowed, and should be given as  NA" (double space as printed) — `../pyrate-input-file/references/preparing-input-file.md` 14, with a worked `NA` row at line 23 of that mirror; the four core columns (`Species`, `Status`, `MinT`, `MaxT`) do *not* tolerate missing data ("PyRate can not deal with missing information in these four columns"), same line. Restated here only because the fixture `../assets/files/covar-trait-column-EXCERPT.txt` shows that `NA` row; the rule itself belongs to `pyrate-input-file`.

Transformation: "Trait values can (often should) be log-transformed. This can be deon using the command `logT`:" — `references/tutorial-4.md` 105, quoted with the source's two typos (`deon`; `logT` without the leading `-`). The values themselves are only ever printed as `-logT 0` (no transformation), `-logT 1` (log_e), `-logT 2` (log10) (`references/tutorial-4.md` 106-108; `references/command-list.md` 153-155, which adds `(default)` to `-logT 2` at line 155 and prints no default in the tutorial).

Why that line matters here: the only trait values the wiki prints are small and dimensionless (90, 285, 80; `../pyrate-input-file/references/preparing-input-file.md` 17-23), while the `Ursidae_bm.txt` that both Covar pages link — a 75-species table downloaded by the `pyrate-command-reference` skill as `../assets/files/cmdref-trait-table.txt` — gives 90000 for *Ursus_etruscus* (line 71) and 285000 for *Agriotherium_insigne* (line 7), i.e. the same species three orders of magnitude larger, and that file also has a `Species`/`Trait` header line (line 4). Treat those as upstream-repository evidence, not as wiki documentation: neither mirror says anything about units, magnitudes or headers.

### Every Covar command on the command list, with its documented default

The "Settings for trait correlated rates (Covar models)" section is `references/command-list.md` 129-155 (CN twin `references/command-list-cn.md` 129-155, same line numbers).

| Command | Documented values / semantics | Documented default | Lines |
| --- | --- | --- | --- |
| `-trait_file` | Path to the tab-separated trait table (`NA` allowed). The section's own example line is garbled: it points at `Ursidae_SE.txt` — the `-d` origination/extinction table name (`references/command-list.md` 20) — and labels it "correlated speciation rate", a `-mCov 1` description | none stated | 132-135 |
| `-mCov` | `1` correlated speciation rate; `2` correlated extinction rate; `3` correlated speciation and extinction rates; `4` correlated preservation rate; `5` correlated speciation, extinction, preservation rates. Correlation parameters: `cov_sp`, `cov_ex`, `cov_q` | **none printed anywhere** — the page never says whether Covar is off by default (by inference from the model list, `-mCov` is opt-in; not stated) | 137-144; the five example lines 140-144 are byte-identical at `references/tutorial-4.md` 114-118 (there the description at 112 merely prefixes "Use the command `-mCov` to") |
| `-trait` | Which trait to analyse if the input file holds several | `-trait 1` "(default; it takes first trait)" | 146-148 |
| `-logT` | `0` not transformed; `1` log_e; `2` log10 | `-logT 2` "(default)" | 150-155 |
| `-pC` | "Standard deviation of the Normal prior on the correlation parameters … The Normal priors are centered in 0. If set to 0, the standard deviation is assigned a Gamma hyper-prior G(2,2) and estimated from the data." | `-pC 1` "(default)" | 186-188 (hyperprior section) |
| `-tC` | "Window sizes of updates of correlation parameters … for covariation with speciation, extinction, and preservation rates respectively"; which entries are used depends on `-mCov` | `-tC 0.025 0.025 0.1` "(default)" | 259-261 (tuning section) |
| `-fU` | "Update frequencies for preservation rate, birth-death parameters, and correlation parameters under the Covar model, respectively. What is left is used for updating speciation and extinction times." | `-fU 0.02 0.18 0.08` "(default under Covar model; … 72%)" | 263-265 (tuning section) |

Tuning detail beyond these lines belongs to `pyrate-mcmc-tuning`; the same two commands reappear in that skill's mirror at `../pyrate-mcmc-tuning/references/tutorial-6.md` 46 (`-tC`) and 50-51 (`-fU`).

### How the tutorial's typical invocation uses them

`./PyRate.py Ursidae_example_PyRate.py -trait_file Ursidae_bm.txt -mCov 5 -logT 10 -pC 0` (`references/tutorial-4.md` 124, printed as "A typical analysis is launched with the following command:", line 122). Reading it option by option: a separate trait table (`Ursidae_bm.txt`; no mirror says what `bm` stands for, and only the input-file page's "(e.g. estimated body mass)" — `../pyrate-input-file/references/tutorial-1.md` 49 — makes that reading plausible, by inference), all three correlation parameters at once (`-mCov 5`), the hyper-prior on their standard deviation (`-pC 0`), which the tutorial explicitly recommends here — "**Note** that this option is generally preferred when more than one correlation parameters are estimated (i.e. with `-mCov 3` or `-mCov 5`)" (`references/tutorial-4.md` 120) — and `-logT 10`, a value no mirror defines. Both twins print `10` (`references/tutorial-4-cn.md` 125), so it is upstream, not a transcription error of this workspace. The example files are named but never printed (`references/tutorial-4.md` 126).

### Model comparison: a Covar model against a plain BD model

`-A` selects what the run computes (`references/command-list.md` 46-54): `-A 0` parameter estimation with a fixed number of shifts, `-A 1` "run an MCMC with thermodynamic integration" … "to estimate the fit of a birth-death model. This analysis computes the marginal likelihood of a birth-death model" … "file) that can be use to compare alternative models, e.g. with different number of rate shifts or trait correlations." (line 49; the file name sits inside that elision — the doc prints it as ‘*_marginal_likelihood.txt’ in curly quotes with a stray tab before it, and the ungrammatical 'can be use' is upstream, not a transcription error of this workspace), `-A 2` BDMCMC, printed as the default (line 52) — and `-A 3` Dirichlet-process MCMC, flagged "Warning: this function is currently still being tested." (line 54). So the documented Covar-vs-BD comparison is: run both models with `-A 1`, discard burnin with `-b` (line 69 — and see hazard 6 for what that number counts), and feed the two marginal-likelihood files to `-BF`. The scaling-factor count `-k` (default `10`, lines 206-207) and the beta shape parameter `-a` (default `0.3`, lines 210-211) are documented on the same page; the Bayes-factor arithmetic ("twice the difference of log marginal likelihood", categories negligible/positive/strong/very strong) is in `../pyrate-summarize-results/references/summarize-results.md` 67-69, and that page's `*_marginal_likelihood.txt` entry (line 30) names "trait-correlated rates using the Covar model" as a comparison use case. The posterior samples of `cov_sp`, `cov_ex`, `cov_q` are logged in `*_mcmc.log` per that mirror's line 20.

### Reading `cov_sp` / `cov_ex` / `cov_q`: what counts as an effect

`-mCov` estimates "correlation parameters (cov_sp, cov_ex, cov_q)" (`references/tutorial-4.md` 112), one per rate the model couples to the trait (`references/command-list.md` 140-144), and every one of them is prior-centred on no effect: "The default prior on the correlation parameters is a normal distribution centered in 0 and with standard deviation = 1" (`references/tutorial-4.md` 120), which the command list words as "The Normal priors are centered in 0" (`references/command-list.md` 187). The quantity to beat is therefore **0**, and `-BF`/`-A 1` answers a *different* question (which model fits better) — it does not tell you the direction or the significance of a trait correlation, so a comparison alone leaves the `cov_*` unread.

The only decision rule this corpus states for exactly that situation belongs to the sibling program: "When these parameters are significantly different from 0 (based on their 95% HPD) we consider the correlation as significantly positive or negative" (`../pyrate-continuous-covariates/references/tutorial-2.md` 115), printed there for that program's correlation parameters *Gl*/*Gm*. **Label: transferred by inference, not a Covar doc rule** — the string HPD occurs in none of `references/tutorial-4.md`, `references/command-list.md` or their CN twins, and the sole Covar statement is that the columns exist (`../pyrate-summarize-results/references/summarize-results.md` 20); use the criterion, but say you transferred it. Neither may you carry a threshold across your own models: ADE reads its Weibull shape against 1, "If the shape parameter is not significantly different from 1, then there is no evidence of age dependent extinction rates" (`references/tutorial-4.md` 149), so 0 belongs to `cov_*` and 1 to ADE — and neither belongs to `cov_q`'s preservation scale (Pitfalls, 'Preservation-coupled Covar is a different animal'). Read the HPD off `*_mcmc.log` in Tracer, the inspection route the same source page gives (`../pyrate-continuous-covariates/references/tutorial-2.md` 117; `../pyrate-summarize-results/references/summarize-results.md` 20).

## ADE: age-dependent extinction

Motivation, verbatim: "Testing for age dependent extinction is more complicated than fitting a Weibull distribution to the estimated longevities of species because that would not account for the unobserved species, which are likely the short lived ones" (Hagen et al. 2017, `references/tutorial-4.md` 137). The ADE model is "implemented in its own function in PyRate" (`references/tutorial-4.md` 138; the subsection it is described in is titled "Bayesian implementation of the ADE model", line 133) and takes the ordinary occurrence-based input: that line's link points to tutorial 1's "Generate PyRate input file (option 1)" section (`../pyrate-input-file/references/tutorial-1.md` 25), i.e. a `*_PyRate.py` file of occurrences, not a `-d` origination/extinction table (`references/command-list.md` 17-20).

| Piece | Documented content | Lines |
| --- | --- | --- |
| Switch | `-ADE 1` "specifies that you want to run the ADE model"; no default printed | `references/tutorial-4.md` 141-143 |
| Preservation | `-qShift` sets "a preservation model with rate shifts" (TPP); only HPP and TPP are allowed with ADE → use `-mHPP` (`references/command-list.md` 87-89) or `-qShift` (91-93) | `references/tutorial-4.md` 143 |
| Assumption | "The ADE model assumes that extinction rates are only a function of species age and the mean rate does not change through time. Thus, ADE models should be tested within time windows with roughly constant speciation and extinction rates." | `references/tutorial-4.md` 145 |
| Time window | `-filter` "to drop all taxa outside a specified time range"; example `-filter 23.03 5.3` "will only analyze taxa with all occurrences in the Miocene" — i.e. older bound first, and only taxa entirely inside the window are kept (both read off the example, not stated as a rule) | `references/tutorial-4.md` 145-149 |
| Output | "The output file from an ADE analysis includes the estimated shape and scale parameters of the Weibull distribution." — the file itself is never named | `references/tutorial-4.md` 149 |
| Interpretation | shape not significantly different from 1 → no evidence of ADE; shape < 1 → extinction highest at the start of a species' life and decreasing with age; shape > 1 → extinction increases with time since origination | `references/tutorial-4.md` 149 |
| Alternative | ADE-NN, a deep-neural-network implementation, "the code implementing it is available [here]" in the repo's `ADE-NN/` directory; no PyRate command for it exists in this corpus | `references/tutorial-4.md` 134 |

The `-qShift` argument in the tutorial's ADE lines is `epochs.txt`, while the command list's `-qShift` example file is `epochs_q.txt` (`references/command-list.md` 93) and `epochs.txt` is the `-fixShift` example file (`references/command-list.md` 124-125) — a filename collision between pages; both are just paths to a list of epoch-boundary ages, so pass the file the command list names for the option you use.

## BDC: birth-death chronospecies

"Fossil and phylogenetic data can be jointly analyzed under the BDC model" and "This analysis requires two input files: a standard PyRate input dataset" (`references/tutorial-4.md` 154, where the model is attributed only to a linked author-year string, "Silvestro, Warnock, Gavryushkina & Stadler 2018" — no journal, title or DOI text is printed) plus "a tree file (NEXUS format)" (`references/tutorial-4.md` 156), needs Dendropy (`references/tutorial-4.md` 160). The CN twin renders `-bdc` as "强制**在 BDC 模型下采用相容的物种形成率与灭绝率**" (`references/tutorial-4-cn.md` 164) — "相容" (compatible) is exactly as undefined as the English word, so it does not resolve the term.

| Setting | What it does (documented wording) | Lines |
| --- | --- | --- |
| (nothing extra) | "By default the analysis assumes a constant rate birth-death model with independent rate parameters between fossil and phylogenetic data." | `references/tutorial-4.md` 162 |
| `-bdc` | "enforces **compatible speciation and extinction rates under the BDC model**" — read, by inference from the default stated on line 162, as relaxing the split between fossil and phylogenetic rate parameters. What "compatible" means mathematically is not defined anywhere in this corpus. | `references/tutorial-4.md` 163 |
| `-eqr` | "sets the **rates to be equal**" | `references/tutorial-4.md` 163 |
| `-fixShift` | Run under the **BDC skyline model** with rate shifts fixed at epoch boundaries: "This command sets up an analysis with rate shifts at the epochs boundaries under the BDC compatible model." | `references/tutorial-4.md` 165-169; option semantics `references/command-list.md` 123-125 (it also auto-switches the rate priors to half-Cauchy) |
| Plotting | "Plotting functions in R to plot the results of the BDC and BDC-skyline models are available [here]" → `plot_functions_BDC_model.R` in the repo; the script itself is not part of this corpus | `references/tutorial-4.md` 171 |

The two printed BDC command lines (plain BDC, BDC-skyline) plus the two ADE lines and the one Covar line — five lines in all — are collected in `../assets/files/covar-model-commands.sh`.

## Worked example

Uses only the three fixtures this skill owns and options that the mirrors print. The interpreter is **disputed, not settled** — the command lines below work on either reading, but you cannot claim compliance with both pages: Home states "Python 2.6 – 2.7" and "Python 3.x is currently not supported" (`../pyrate/references/home.md` 69), while the install tutorial states the opposite requirement, "First, make sure **Python (v.3.10 or higher)** is installed on your computer" (`../pyrate-installation/references/virtual-environment.md` 13); no mirror arbitrates and `pyrate-installation` owns that conflict, so record which interpreter you ran. Substitute your own `*_PyRate.py` input for `<your_dataset>`, and note that the `-logT 10` of the tutorial line is replaced by the documented `-logT 2` because `10` is undefined in either mirror.

```sh
# steps 0-1 and 5 need nothing but coreutils and run from THIS skill directory,
# so that ../assets/files/ resolves; steps 2-4 need PyRate.py + pyrate_lib in the working
# directory on the interpreter PyRate runs there - 2.6-2.7 per ../pyrate/references/home.md:69
# but 3.10+ per ../pyrate-installation/references/virtual-environment.md:13 (the corpus
# contradicts itself; ../pyrate-installation owns that conflict)
cd pyrate-trait-age-models

# 0) LOOK at the two documented trait-table shapes
column -t -s "$(printf '\t')" ../assets/files/covar-trait-column-EXCERPT.txt   # Species Status MinT MaxT Trait, NA allowed
cat ../assets/files/covar-trait-file-DERIVED.txt                               # -trait_file shape: name<TAB>value

# 1) NAME CHECK before any Covar run (inference from references/command-list.md:133, "identical to those used in the PyRate file";
#    the *_SpeciesList.txt file is documented at ../pyrate-input-file/references/tutorial-1.md:40)
cut -f1 ../assets/files/covar-trait-file-DERIVED.txt | sort > /tmp/trait_names.txt
# compare with your input's species list, e.g.: sort <path>/<dataset>_SpeciesList.txt > /tmp/inp_names.txt; comm -3 /tmp/{trait,inp}_names.txt

# 2) COVAR vs plain BD, compared by TI (options: references/command-list.md 46-52, 56-73, 132-155, 186-188)
#    WHY -b IS WRITTEN AS A FRACTION: references/command-list.md:69 measures -b in iterations, its own
#    examples two lines later measure it in samples (references/command-list.md:72,73), and the sibling
#    program's page measures it in samples outright (../pyrate-continuous-covariates/references/pyratecontinuous.md:14).
#    This chain logs 10000 samples - arithmetic on the documented -n 10000000
#    and -s 1000 (references/command-list.md:58,62), which no page performs - so a sample-count burn-in
#    above 10000 discards the entire run on one reading, while a count of a few hundred discards nearly
#    nothing on the other. A fraction is the one value that survives both (inference: -s is constant, so
#    a tenth of the generations is a tenth of the logged samples). The size is still yours to justify:
#    ../pyrate-bd-analysis/references/tutorial-1.md:205 makes it a matter of inspecting the chain.
python PyRate.py <your_dataset> -trait_file ../assets/files/covar-trait-file-DERIVED.txt -mCov 3 \
    -logT 2 -pC 0 -A 1 -n 10000000 -s 1000 -b 0.10 -out covar3   # -mCov 3 + -pC 0: references/tutorial-4.md:120; -b 0.10 is the docs' own fraction example, references/command-list.md:73
python PyRate.py <your_dataset> -A 1 -n 10000000 -s 1000 -b 0.10 -out bd0   # same burn-in both runs, since -b "Must be set to a reasonable number when estimating marginal likelihood through TI", references/command-list.md:69
# each -A 1 run writes a *_marginal_likelihood.txt (command-list.md:49); -out will "Add tag to default stem name of output files"
# (command-list.md:33) but no page prints the resulting file NAME pattern -> glob for it, do not assume:
ls *marginal_likelihood.txt
python PyRate.py -BF covar3_marginal_likelihood.txt bd0_marginal_likelihood.txt  # -BF as printed, ../pyrate-summarize-results/references/summarize-results.md:69

# 3) ADE inside a roughly constant-rate window, on TPP preservation (tutorial-4.md:147, verbatim)
#    -qShift gives the TPP model, one of the only two allowed with ADE (tutorial-4.md:143);
#    the other allowed choice is -mHPP (command-list.md:87-89) instead of -qShift epochs.txt
python PyRate.py <your_dataset> -ADE 1 -qShift epochs.txt -filter 23.03 5.3    # exactly tutorial-4.md:147

# 4) BDC, then the BDC-skyline variant (tutorial-4.md:158 and 167; Dendropy required, tutorial-4.md:160)
python PyRate.py example_files/BDC_model/Feliformia.py -tree example_files/BDC_model/Feliformia.tre
python PyRate.py example_files/BDC_model/Feliformia.py -tree example_files/BDC_model/Feliformia.tre \
    -fixShift example_files/epochs.txt -bdc

# 5) CHECK any line you reconstructed against the five lines the tutorial actually prints
grep -v '^#' ../assets/files/covar-model-commands.sh
```

Step 2's `-BF` line is written as the sibling mirror prints it (`../pyrate-summarize-results/references/summarize-results.md` 69 shows the option and its two file arguments only); whether an input dataset must precede it is not stated. Steps 3-4 use the upstream example paths (`example_files/BDC_model/…`, `references/tutorial-4.md` 158) which are *not* fixtures here — nothing in this corpus prints their contents.

## Pitfalls

- **`-mCov` without a trait anywhere.** The trait must come from the input file or `-trait_file` (`references/command-list.md` 130); neither mirror documents an error message, a fallback, or a default when no trait exists. Prepare the trait column before adding `-mCov`.
- **`-pC 0` is not free**: it replaces the fixed sd with an estimated one through a Gamma(2,2) hyper-prior (`references/command-list.md` 187), and both pages restrict it to models estimating more than one correlation parameter — but read hazard 5 before trusting the command list's enumeration of which `-mCov` values those are (its own list is broken text; the tutorial's `-mCov 3` / `-mCov 5` gloss is the usable one). With a single correlation parameter, set `-pC` to a positive number (default `1`, `references/command-list.md` 188).
- **Preservation-coupled Covar is a different animal.** `-mCov 4`/`-mCov 5` put the trait correlation on the preservation rate `q` too (`references/command-list.md` 143-144), which changes the fossilization model this suite documents in `pyrate-preservation-models`; do not interpret a `-mCov 5` `cov_q` with preservation-model logic from `-mHPP`/`-mG` runs.
- **A Bayes factor does not read your `cov_*`.** `-A 1` + `-BF` answers which model fits better (`references/command-list.md` 46-54); the direction and significance of a trait correlation come only from the posterior samples of `cov_sp`, `cov_ex`, `cov_q` (`references/tutorial-4.md` 112) measured against the prior centre of 0 (`references/tutorial-4.md` 120; `references/command-list.md` 187). The 95%-HPD-excludes-0 criterion used to do that here is **transferred** from `../pyrate-continuous-covariates/references/tutorial-2.md` 115 — no mirror of this skill states any decision rule for `cov_*` — so quote it as a transfer, not as Covar documentation (see the section 'Reading cov_sp / cov_ex / cov_q').
- **ADE answers a different question than rate-shift models.** Its assumption is a time-constant mean rate (`references/tutorial-4.md` 145); running it on a data set you already know has strong rate shifts (a `-mL`/`-mM`/`-fixShift` finding, `references/command-list.md` 111-125) tests age dependence in the wrong window.
- **Do not mix `-A` values across a comparison.** `-A 1` is the only mode *documented* to write `*_marginal_likelihood.txt` (`references/command-list.md` 49) and `-A 2` is the default (`references/command-list.md` 52), so — by inference from those two lines, no page states it as a rule — a Covar run launched without `-A` produces no marginal likelihood to compare, and cannot be scored against a `-A 1` BD run by `-BF`.
- **BDC `-bdc` vs `-eqr` are not interchangeable** ("compatible" vs "equal", `references/tutorial-4.md` 163) and neither is the default (`references/tutorial-4.md` 162): record which of the three you ran, because the corpus gives no further definition to reconstruct it from.
- **Tutorial-4's own Contents block omits the section you are reading — and its one dead anchor is evidence of an unfinished page.** The Contents list covers only MBD, Covar and ADE (`references/tutorial-4.md` 16-18): MCDD (heading at line 23) and BDC (heading at line 152) are absent from it entirely. The MBD entry (line 16) links the anchor `#multivariate-birth-death-models-this-tutorial-is-work-in-progress`, which no heading on the page produces (the heading as printed at line 44 is "The Multivariate Birth-Death model (MBD)"), so the link is dead and the "work in progress" notice it points at is stale — the page body carries no such warning for Covar, ADE or BDC. Read that as: this tutorial is upstream-flagged as incomplete, and the silence about your model is not a guarantee.

## Not documented in this wiki

| Unanswered question | Why you must not fill it in |
| --- | --- |
| Whether a species omitted from the `-trait_file` table is dropped from the analysis or imputed like an `NA` species | the two options are stated in one breath and the imputation sentence names only the `NA` rows (`references/command-list.md` 133, `references/tutorial-4.md` 103); the CN twins restate the same ambiguity (`references/command-list-cn.md` 133, `references/tutorial-4-cn.md` 104) without resolving it |
| What `-logT 10` does | only `0`, `1`, `2` are defined anywhere in this corpus (`references/command-list.md` 153-155; `references/tutorial-4.md` 106-108); `10` appears solely in the tutorial's example line (`references/tutorial-4.md` 124 and its CN twin `references/tutorial-4-cn.md` 125), so it is upstream, not a workspace transcription error |
| The default of `-mCov`, `-trait_file`, `-ADE`, `-filter`, `-tree`, `-bdc`, `-eqr` | none of the five BDC/ADE commands appears on the command-list page at all, and the Covar section prints defaults only for `-trait` and `-logT` |
| Whether `-filter` may be used without `-ADE` | it is only ever shown inside an ADE command line (`references/tutorial-4.md` 145-149); the corpus gives it no entry of its own |
| Whether `-tree` matches tree tips to occurrence species by name, and what happens on mismatch | `references/tutorial-4.md` 154-160 states the two input files and the Dendropy dependency and nothing else about names |
| The mathematical content of "compatible" rates under `-bdc` | the word is the entire definition (`references/tutorial-4.md` 163); the 2018 paper is linked but not reproduced anywhere in this corpus |
| Which `-A` modes Covar/ADE/BDC support | the Covar section never mentions `-A`; `-tC`/`-fU` are described only under 'Tuning parameters' (`references/command-list.md` 259-265); `-A 3` carries its own 'still being tested' warning (line 54) and `-A 4` (RJMCMC) is not on this page at all — it is documented only at `../pyrate-rjmcmc/references/tutorial-3.md` 32 |
| What PyRate does when `-ADE 1` is run with the preservation model left at its NHPP default | the restriction exists ("only homogeneous Poisson process (HPP) and time-variable Poisson process can be used with the ADE model", `references/tutorial-4.md` 143) but no page prints an error, a warning or an automatic switch; both tutorial ADE lines pass `-qShift` (141, 147) and never discuss the alternative |
| Whether `-mCov` combines with `-mG` gamma rate heterogeneity, or with `-qShift`/`-fixShift` at the same time | no combination is documented; the only explicit compatibility statement for any of these three models is the ADE HPP/TPP restriction (`references/tutorial-4.md` 143) |
| The name/format of the ADE output file holding the Weibull shape and scale | "The output file from an ADE analysis includes…" (`references/tutorial-4.md` 149) never names it; the output-file inventory lives in `../pyrate-summarize-results/references/summarize-results.md` and lists no ADE file |
| The exact file name `-A 1` writes when `-out <tag>` is also given | the docs only ever write the stem as ‘*_marginal_likelihood.txt’ (`references/command-list.md` 49) and describe `-out` as "Add tag to default stem name of output files" (`references/command-list.md` 33) without printing one real combined name anywhere; glob for the file instead of guessing its name |
| Whether a trait table needs a header row | `-trait_file` is described only as a "tab-separated text file" whose first column is names and second is values, with no word on a header (`references/command-list.md` 133), whereas the `-d` table explicitly requires one ("the first line containing column headers", `references/command-list.md` 18); the upstream `Ursidae_bm.txt` copy in `../assets/files/cmdref-trait-table.txt` does start with a `Species`/`Trait` header (line 4), but that is repo evidence outside this wiki and cannot be cited as a rule |
| The internal layout of a `*_PyRate.py` file that carries a trait | no page in this corpus prints the generated python file at all (run from the suite root, `grep -rn 'DataTypes\|np.array' */references/*.md` finds nothing); `references/command-list.md` 13 and 130 only say it may hold "one or more continuous traits" — and the same line calls the generator `pyrate_utilities.R` where the input-file page writes `pyrate_utilities.r` (`../pyrate-input-file/references/preparing-input-file.md` 9, 28), so even the tool name's case is unsettled |
| How many traits a single Covar run can take, and whether multivariate Covar exists | `-trait` implies several may be stored but only "which trait will be analyzed" is documented (`references/command-list.md` 146-148) |
| What `-filter` does to a taxon whose occurrences straddle the window boundary | "drop all taxa outside a specified time range" plus "taxa with all occurrences in the Miocene" (`references/tutorial-4.md` 145, 149) are the only statements; boundary handling is not specified |
| Burnin/monitoring requirements specific to Covar chains (`cov_sp` etc.), and any decision rule stated *for* `cov_*` | the burnin rules that exist are generic (`references/command-list.md` 68-73); Tracer inspection of `cov_*` is only implied by the sibling output-file page (`../pyrate-summarize-results/references/summarize-results.md` 20); the 95%-HPD-against-0 criterion used in the section 'Reading cov_sp / cov_ex / cov_q' above is **transferred** from `../pyrate-continuous-covariates/references/tutorial-2.md` 115 and is labelled there as the other program's rule — the word HPD occurs in none of this skill's four mirrors (last grep recipe below), so report it as a transfer and never as a Covar doc rule |

## Related skills

- `pyrate-input-file` — the occurrence table (`Species Status MinT MaxT [Trait]`), the `NA` rule for the trait column, `extract.ages`, the `*_PyRate.py` and `*_SpeciesList.txt` outputs; `../pyrate-input-file/references/preparing-input-file.md` 14-24.
- `pyrate-preservation-models` — `-mHPP`, `-qShift` + `epochs_q.txt`, `-mG`, `-ncat`: everything ADE's restriction and Covar's `cov_q` refer to; `../pyrate-preservation-models/references/command-list.md` 85-106.
- `pyrate-bd-analysis` — the plain birth-death run and `-mL`/`-mM`/`-mC`/`-fixShift` (the comparator in the Covar-vs-BD comparison); `../pyrate-bd-analysis/references/command-list.md` 110-125.
- `pyrate-rjmcmc` — `-A 4` / RJMCMC shift searching (a mode this page's `-A` block does not document).
- `pyrate-summarize-results` — `*_mcmc.log` columns incl. `cov_sp`/`cov_ex`/`cov_q`, `*_marginal_likelihood.txt`, `-BF`, `-mProb`, `-plot`.
- `pyrate-mcmc-tuning` — `-tC`, `-fU`, `-tT`, `-nT` and the mixing advice behind them; `../pyrate-mcmc-tuning/references/tutorial-6.md` 46-51.
- `pyrate-diversity-dependence` — the MCDD and MBD halves of the same tutorial page, and **the owner of MBD**: MBD is a separate program, `PyRateMBD.py` (`references/tutorial-4.md` 53), with its own options (`-var` folder of predictors, `references/tutorial-4.md` 68, 71; `-rmDD 1` 78; `-minT`/`-maxT` 79, 80; `-hsp 0` 81), so none of them is available on the `PyRate.py` command lines this skill documents. Same for MCDD (`PyRateMCDD.py`, `references/tutorial-4.md` 24, 34, 38). The grep recipe ending in `# 6 hits` below prints all six lines; note the router `../pyrate/SKILL.md` contradicts itself here — its routing table sends MBD to `pyrate-diversity-dependence` and marks this skill as *not* MBD, while its own related-skills list still appends MBD to this skill's entry, so treat the table (and this bullet) as the correct version and re-run that grep if it matters to you.
- `pyrate-continuous-covariates` — `PyRateContinuous.py`, where environment variables drive rates through time; do not confuse with the per-lineage trait Covar model.
- `pyrate-des` — `PyRateDES.py` dispersal/extinction/sampling models.
- `pyrate-command-reference` — the whole command list in one place, including the sections quoted here.
- `pyrate-installation` — owner of the Python-version conflict this skill cannot settle (Home's 2.6-2.7 + ban on 3.x, `../pyrate/references/home.md` 69, vs the install tutorial's "Python (v.3.10 or higher)", `../pyrate-installation/references/virtual-environment.md` 13) and of the venv recipe. Note what that recipe does **not** pin: `../assets/files/venv-setup.sh` is a derived wrapper of `../pyrate-installation/references/virtual-environment.md` 16-50 that builds the environment from whichever interpreter you hand it and installs `requirements.txt`, whose contents no mirror prints (`../pyrate-installation/references/virtual-environment.md` 44). Install Dendropy into the environment you actually settle on, before BDC.
- `pyrate` — router: `../pyrate/references/home.md` 29 documents `PyRate.py` as implementing "the main functions to infer speciation and extinction rates through time and preservation rates" plus "a model to infer" trait-dependent rates (section link text: trait dependent speciation and extinction).

## Resources

| File | What's in it | Load when |
| --- | --- | --- |
| `references/tutorial-4.md` | Tutorial 4 in full: MCDD (23-42), MBD (44-94), **Trait correlated diversification (98-126)**, **ADE (131-149)**, **BDC (152-171)**, incl. every command line the three models have | Setting up or debugging a `-mCov`, `-ADE` or BDC run; reading the tutorial's `-logT 10` line; finding the `-filter`/`-bdc`/`-eqr`/`-tree` usage |
| `references/tutorial-4-cn.md` | Chinese twin of the same page (its frontmatter is 9 lines against the English 8, so the Chinese body runs one line below the English throughout: sections at 99-127, 132-150, 153-172) | When an English sentence is ambiguous — it preserves the `-logT 10` (125) and the `logT` typo (106), so it settles nothing about `-logT`; but where English 143 garbles the ADE line ("where -ADE 1 specifies … and -qShift is the  sets a preservation model with rate shifts"), the Chinese (144) reads cleanly, so use the CN wording for `-qShift` |
| `references/command-list.md` | The wiki command list: `<input file>`/`-d`/`-j`/`-out`/`-singleton` (12-42), `-A`/`-n`/`-s`/`-b`/`-thread` (46-82), preservation (87-106), constrained shifts (111-125), **Covar section (129-155)**, hyperpriors incl. `-pC` (161-188), advanced (192-227), tuning incl. `-tC`/`-fU`/`-fR` (230-268) | Any option's documented default; the Covar command table; TI/`-A` mechanics for model comparison |
| `references/command-list-cn.md` | Chinese twin (same layout; Covar section 129-155, `-pC` 185-187, `-tC`/`-fU` 258-264) | Checking a default's wording; note the CN text carries the same broken "`-mCov 2` 或 `-mCov`" phrase at 186, so that defect is upstream |

## grep recipes

All ten were run from this skill directory. Two of them print a fallback line instead of a match (the `|| echo` guards): those are the checks that establish what this skill cannot document — the five model commands that are absent from the command list, and the absence of any HPD wording in its own mirrors.

```sh
# run these from this skill directory
grep -n "^##### \`-trait\|^##### \`-mCov\|^##### \`-logT\|^##### \`-pC\|^##### \`-tC\|^##### \`-fU\|^### Settings for trait" references/command-list.md
grep -n "identical to those used in the PyRate file\|imputed by the MCMC" references/command-list.md references/tutorial-4.md
grep -n "G(2,2)\|standard deviation = 1\|at least 2 correlation" references/command-list.md references/tutorial-4.md
grep -n -- "-logT 10\|deon\|-mCov 3\` or \`-mCov 5" references/tutorial-4.md references/tutorial-4-cn.md
grep -n "homogeneous Poisson process (HPP) and time-variable\|only a function of species age\|significantly different from 1" references/tutorial-4.md
grep -n "independent rate parameters between fossil\|compatible speciation and extinction rates\|Dendropy" references/tutorial-4.md
grep -n "can be use to compare alternative models\|Must be set to a reasonable number" references/command-list.md
grep -n "PyRateMBD.py\|PyRateMCDD.py" references/tutorial-4.md  # 6 hits - MCDD at 24/34/38, MBD at 53/68/90: both are other programs on this page, neither is a PyRate.py model documented here
grep -n -e '-ADE' -e '-bdc' -e '-eqr' -e '-tree' -e '-filter' references/command-list.md || echo 'NO MATCH: none of the five commands is on the command-list page'
grep -rn -i hpd references/ || echo 'NO MATCH: no mirror of this skill states an HPD rule, so the cov_* criterion above is a transfer from pyrate-continuous-covariates'
```

## Runnable fixtures (`../assets/files/`)

| File | Run it? | Provenance / what it makes concrete |
| --- | --- | --- |
| `../assets/files/covar-trait-column-EXCERPT.txt` | no (input data) | verbatim rows / derived wrapping: `PyRate-doc/PyRate-wiki/1.-Preparing-input-file.md` lines 8-16, mirrored at `../pyrate-input-file/references/preparing-input-file.md` 16-24; only the markdown backticks and the trailing two-space hard breaks were removed, every row's inner whitespace is byte-identical to the mirror. Shows the `Species Status MinT MaxT Trait` table, one row per occurrence, repeated names with a constant trait value, and `NA` for *Agriotherium_intermedium*. Its last line is the doc's own literal `...` row (mirror line 24), kept because the copy is verbatim — skip it when parsing. Complements `../assets/files/occ-ursidae-table-EXCERPT.txt` (same table, separators normalised to single tabs and the `...` row dropped); this one keeps the ragged printed spacing (multiple tabs plus padding spaces inside each row), so read it with a whitespace-tolerant split or use the normalised sibling instead |
| `../assets/files/covar-trait-file-DERIVED.txt` | no (input data) | derived: the four unique species and trait values of the file above, re-laid out as the two-column `-trait_file` table the spec requires (`references/command-list.md` 133: name, value, tab-separated, `NA` allowed; the docs never say whether a header line belongs there, so this fixture has none). The corpus links `Ursidae_bm.txt` (`references/tutorial-4.md` 103) but never prints it, so this is the shape, not the upstream data — for the real 75-species file use `../assets/files/cmdref-trait-table.txt` (owned by `pyrate-command-reference`, values 1000x the wiki illustration) |
| `../assets/files/covar-model-commands.sh` | needs PyRate + upstream `example_files/` | verbatim: the five command lines the tutorial prints for the three models (mirror `references/tutorial-4.md` 124, 141, 147, 158, 167 = source lines 116, 133, 139, 150, 159) with a `#` provenance header naming the `-logT 10` anomaly. Grep/diff it to confirm a reconstructed invocation matches the docs |
