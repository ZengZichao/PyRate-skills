---
name: pyrate-des
description: "Runs & debugs PyRate Dispersal-Extinction-Sampling (DES) analysis of fossil occurrences from two predefined areas with `PyRateDES.py`. In: -fossil,-recent,-wd,-filename,-bin_size,-rep,-trim_age,-translate,-timeline,-site,-data_in_area,-plot_raw,-taxon,-area,-age1,-age2 on DarwinCore tables (scientificName/earliestAge/latestAge/higherGeography) or R routes DESin(), write.DES.in(), DES_input_preparation.R, speciesgeocodeR SpGeoCod(), simDES sim_DES(). M: -mG,-ncat,-qtimes,-TdD,-TdE,-symd,-syme,-symq,-constr,-varD,-varE,-r,-symCovD,-symCovE,-constrCovD_0,-constrCovE_0,-DivdD,-DivdE,-DdE,-symDivdD,-symDivdE,-constrDivdD_0,-constrDivdE_0,-traitD,-traitE,-logTraitD,-logTraitE,-catD,-catE. Output: -A 0 (Bayesian) or -A 3 (ML, needs nlopt), -n,-s,-p,-out,-sum,-b,-plot,-plotCI, marginal_rates.log. Failure mode: route-2 area-coding silently deletes rows, missing nlopt or Rscript, stray PyRateDES2.py, -qtime vs -qtimes, a -data_in_area example missing its flag, -translate needing an empty -recent."
---

# `PyRateDES.py`: dispersal, local extinction and sampling in two areas

## Overview

DES ("Dispersal Extinction Sampling") takes fossil occurrences already classified into time bins and **two discrete, predefined areas** and, by default in a Bayesian framework (`references/tutorial-5.md` line 191: "The default settings specify Bayesian inference"), estimates dispersal between the areas, local extinction within each area, and the sampling rate of each area (`../pyrate/references/home.md` line 54: "uses fossil occurrences in two discrete areas to estimate rates of dispersal between areas and rates of local extinction within areas, while incorporating sampling biases"). Model and program are cited in this corpus only by `../pyrate/references/home.md` line 56: "Silvestro, D., Zizka A., Bacon C. D., Cascales-Minana B. and Salamin, N., Antonelli, A. (2016) Fossil Biogeography: A new model to infer dispersal, extinction and sampling from paleontological data. Phil Trans Roy Soc B, doi: 10.1098/rstb.2015.0225." Note that neither of this skill's own four mirrors prints that citation, and `home.md` line 54 introduces it with the wrong model name — "The MCDD model is described here:" (carried into `home-cn.md` line 55) — a copy-paste artifact of the wiki, not a claim that DES = MCDD.

The program is invoked the same way as the rest of PyRate: `cd /path/to/PyRate`, then `python ./PyRateDES.py ...` (`references/tutorial-5.md` lines 57-59, 179-181); it "requires library" `pyrate_lib` (`../pyrate/references/home.md` line 53) and so runs under the same interpreter as the other programs — the Python-version rule and the virtual environment are owned by `pyrate-installation`, not repeated here. Data-dependent replication is the model's core device: "Replication arises from a uniform resampling of the fossil age estimates between the *earliestAge* and *latestAge* of each fossil" (`references/tutorial-5.md` line 25), so one dataset becomes `-rep` files and the analysis commands all point at **one replicate** (`Carnivora_1.txt`).

**Citation shorthand used below:** a bare `:NNN` means `references/tutorial-5.md` line NNN (the tutorial is the source of nearly every rule here) **unless the same sentence has just named another mirror**, in which case it continues in that one; every other file is named in full at least once. All line numbers were produced with `grep -n` / `sed -n` on the mirrors in this folder, frontmatter included.

**The model precondition the corpus states exactly once**: "Note however, that DES assumes the present data to be complete, so a use of occurrence records for recent data is only for very well samples and curated data" — and native ranges should be used, since anthropogenic influence "will inflate, or sometimes decrease, the recent distribution of many taxa" (`references/tutorial-5.md`:102, `references/des-model.md`:40; the English "very well samples" is the docs' own typo for *sampled*, kept in both mirrors). **Check where that sentence sits before you quote it**: `grep -rn 'present data' references/` returns only those two lines, both inside the *Example 2 — species distributions as coordinates* section, so **no mirror restates it for route 1 discrete-area input, for `-recent` handling as such, or for the analysis phase** — whether it binds a hand-built present table is **not documented**. Treat it as a precondition of any present-range file you pass to `-recent` (`references/tutorial-5.md`:67) and label that as this skill's extension, not the docs' claim; it is a *completeness* assumption about the present data, distinct from the row loss documented in *Route 2 deletes rows* below. See also the Pitfalls bullet.

**The riskiest assumption this skill handles**: the DES tutorial is the *only* place in this corpus that documents any `PyRateDES.py` option — `../pyrate-command-reference/references/command-list.md` contains zero DES options (`grep -c -E '\-varD|\-DivdD|\-traitD|PyRateDES' ../pyrate-command-reference/references/command-list.md` returns `0`), and a corpus-wide `grep -rln -- '-DivdD\|-data_in_area\|-varE'` over the source docs returns only `pyrate_tutorial_5.md` and its `-cn` twin (checked: `grep -rln PyRateDES` over the corpus additionally hits only `Home.md` / `Home-cn.md`, which name no option) — while `../pyrate/references/home.md` line 54 states "A detailed command list is in preparation." So **any option not listed below is undocumented, not available-by-default**; and the wiki page `references/des-model.md` prints no date and describes a *different* input-generation route (R `DESin()` instead of `PyRateDES.py -fossil/-recent`) — calling it the older of the two is by inference from that R-only vocabulary, since the tutorial is dated `#### January 2022` (`references/tutorial-5.md` line 10) and the wiki page is undated. See the conflict rows in the hazard table.

## The 12 things that break a run

| # | What happens | Consequence | Wording + mirror line |
| --- | --- | --- | --- |
| 1 | More than two areas, or areas not predefined | DES is specified for exactly two areas; nothing in this corpus documents >2 | `references/tutorial-5.md`:23 "classified into time-bins and two discrete and predefined areas" — but `references/des-model.md`:11 drops "two" and says only "time-bins and areas" |
| 2 | `-recent` supplied with data rows for a wholly extinct group | wrong present-range coding; for `-translate` it breaks the documented precondition (what PyRateDES then does is not stated anywhere) | `references/tutorial-5.md`:55 "the file with the recent distribution should contain only the header of scientificName and higherGeography"; :79 "This requires the `-recent` file to be empty" |
| 3 | Column names are not the DarwinCore defaults | the table is not parsed as taxon/area/age | `references/tutorial-5.md`:81-87 (`-taxon`, `-area`, `-age1`, `-age2` exist "in case it is not *scientificName*" etc.); `references/des-model.md`:15 "The format of the input data follows the DarwinCore standard" |
| 4 | A taxon spanning both areas on one row | the recent range is wrong (dispersal is estimated from ranges) | `references/tutorial-5.md`:45 "if a taxon occurs in both areas in recent time, it needs a separate row for each area" (`references/des-model.md`:15 same sentence) |
| 5 | A column named `site` present but unwanted | age randomization gets linked to the assemblage (by inference from 'is assumed'); which file the column sits in is itself disputed — see Pitfalls | `references/tutorial-5.md`:91 "By default a column named `site` is assumed (but not required). If there is a column `site`, but the randomization of ages should not be linked to the site, use" `-site ""` — but :43 puts the `site` column in the *fossil* table |
| 6 | `-timeline` used together with `-bin_size` | the bin size you set is not the bin size used | `references/tutorial-5.md`:89 "allowing time bins of different duration by specifying the boundaries between bins. In this case, `-bin_size` is ignored" |
| 7 | Default chain length on a skyline/covariate model | under-converged rates: default is only 100,000 iterations, sampled and printed every 100 | `references/tutorial-5.md`:191 "By default PyRateDES will run 100,000 iterations and sample and print the parameters every 100 iterations"; the doc's own complex runs use `-n 1000001 -s 1000 -p 1000` (:226, :361, :382) |
| 8 | `-A 3` (maximum likelihood) without `nlopt` | the ML fit cannot run; and `-A 3` yields no uncertainty even when it works | `references/tutorial-5.md`:175 "PyRateDES requires the Python library *nlopt* for fitting models with Maximum likelihood. It can be installed with `pip install nlopt`"; :197 "typically faster than Bayesian inference but does not quantify the uncertainty of the model parameters" |
| 9 | `-plot` / `-plot_raw` with R not on `PATH` | the documented precondition for the plotting step fails; the exact failure (error text vs silent no-show) is not printed anywhere in this corpus | `references/tutorial-5.md`:354 and :95 "This requires that R is installed on your PC to execute the shell command Rscript. If you are using Windows, please make sure that the path to Rscript.exe is included in the PATH environment variables (default in Mac/Linux)" |
| 10 | `-translate` output analysed with a covariate model, or `-qtimes` ages left uncorrected | the first is ruled out in the docs; the second puts the rate shifts at the wrong ages (consequence by inference — the docs only give the subtraction rule) | `references/tutorial-5.md`:79 "Datasets generated using `-translate` should only be analyzed with the skyline model but not with covariate dependent dispersal and extinction models. Time of `-translate` will need to be subtracted from other ages of `-qtime`" |
| 11 | Covariates put next to the data instead of in their own directory | breaks the documented layout; the corpus prints no error message for it, so check the paths yourself | `references/tutorial-5.md`:238 "The predictors should be tab-separated text files located in a seperate directory"; :248 "Several covariates could influence dispersal and/or extinction rates and should be located in the same directory" |
| 12 | Copy-pasting three commands the tutorial prints broken | the run does not do what the text says | `references/tutorial-5.md`:314 has the covariate directory with **no flag in front of it**; :274 attributes `-DivdD`/`-DivdE` to "`PyRateDES2.py`" while :277 runs `PyRateDES.py`; :93's `-data_in_area 1` example command omits `-data_in_area 1` |

## Input data preparation: the three documented routes

Routes 1, 1b and 2 all converge on the same artifact — a set of replicated DES input files, written into `-wd` by routes 1 and 2 and into the R working directory by route 1b (`write.DES.in(exp1, file = "Example_data/Example1_DES_in")`, `references/des-model.md`:33) — which you then feed to `-d`. Route 3 is different: its `write.table(Sim[[1]], .../DES_input_data/sim.txt, ...)` (`references/tutorial-5.md`:168) is a plain R write, with no `-wd` and no `-rep`, and no command line anywhere in this corpus feeds a simulated file to `-d`. Only route 1's product is ever analysed: every command at `:186`-`:382` reads `Carnivora_1.txt`; route 2's Python step ends at `:143` with `-filename Example2 -bin_size 2 -rep 5` (the generated names, by inference `Example2_1.txt` … `Example2_5.txt`, are never printed) and route 3 stops after writing `sim.txt` (`:168`).

| Route | What you supply | Generator | Documented generator command |
| --- | --- | --- | --- |
| 1. discrete area classification | fossil table + recent table, both already area-coded (`Eurasia`, `NAmerica`; the wiki's older example uses `"neartic"` and `"paleoartic"`, `references/des-model.md`:15) | `PyRateDES.py` itself | `references/tutorial-5.md`:63 |
| 1b. same, R route (wiki page) | the same two tables (`Example_1_minimum_data.txt`, `Example_1_recent_distributions.txt`) | R: `source(DES_input_preparation.R)`, `DESin()`, `write.DES.in()` — and the page then sanity-checks its own output with `summary()` / `plot()` (`references/des-model.md`:27-30) | `references/des-model.md`:21-33 |
| 2. coordinates | `Example_2_coordinates.txt`, `Example_2_recent_coordinates.txt`, `Example_regions.shp` | R `speciesgeocodeR` `SpGeoCod()` → `foss.txt` / `pres.txt`, then `PyRateDES.py` — **this route subsets the data twice, with two different rules, and prints no count: see *Route 2 deletes rows* below** | `references/tutorial-5.md`:105-134 (R) then :143 (Python); the wiki variant instead calls `DESin(foss, pres, bin.size = 2, reps = 3)` (`references/des-model.md`:68-69) |
| 3. simulated | nothing (scenario parameters) | R `simDES::sim_DES()` → `sim.txt` | `references/tutorial-5.md`:152-169 |

The shapes exactly as the mirrors print them (tab-delimited: `references/tutorial-5.md`:25 "two tab-delimited text files"; `references/des-model.md`:11 prints "two tab-delimited text", which `references/des-model-cn.md`:12 confirms as "两个制表符分隔的文本文件" — two tab-delimited text **files**). Rows marked **never printed** are coverage holes, not formats you may invent:

| Table | Columns (as printed) | Fixture |
| --- | --- | --- |
| fossil occurrences (`CarnivoraFossils.txt`) | `scientificName`, `earliestAge`, `latestAge`, `higherGeography` — and optionally `site` (`references/tutorial-5.md`:43) | `../assets/files/des-CarnivoraFossils.txt`, `../assets/files/des-CarnivoraFossilsSite-EXCERPT.txt` |
| recent distribution (`CarnivoraRecent.txt`) | `scientificName`, `higherGeography`; header-only when the group has no extant members | `../assets/files/des-CarnivoraRecent.txt`, `../assets/files/des-CarnivoraRecent-HEADERONLY.txt` |
| covariate series (`sealevel.txt`) | `age`, `<covariate>` — one file per predictor, in its own directory | `../assets/files/des-sealevel-EXCERPT.txt` |
| continuous trait (`Body_mass_1.txt`) | `scientificName`, `BodyMass` (kg, untransformed) | `../assets/files/des-Body_mass_1-EXCERPT.txt` |
| categorical trait (`FamilyGenera.txt`) | `scientificName`, `Family` (numerically coded) | `../assets/files/des-FamilyGenera-EXCERPT.txt` |
| route-2 coordinate input (`Example_2_coordinates.txt`, `Example_2_recent_coordinates.txt`, `Example_regions.shp`) | **never printed** — the R code only shows they are read with `sep = "\t", header = TRUE` and that the areas come from the shapefile column `areanames = "Region"` (`references/tutorial-5.md`:110-112); no fixture exists because there is nothing to copy | none (see *Not documented in this wiki*) |
| route-2 R output (`foss.txt`, `pres.txt`) | **never printed** — by inference from `references/tutorial-5.md`:113 `foss.txt` is the fossil table plus a `higherGeography` column taken from `fos.class$sample_table$homepolygon`, and by :126-128 `pres.txt` is `scientificName` + `higherGeography`, i.e. the route-1 shapes above | none |
| route-1b wiki input (`Example_1_minimum_data.txt`, `Example_1_recent_distributions.txt`) | **never printed**; the wiki says only `references/des-model.md`:15 "The format of the input data follows the DarwinCore standard" | none (the R call itself is in `../assets/files/des-wiki-example1_DESin.R`) |
| simulated input (`sim.txt`) | never printed — only the `write.table(Sim[[1]], ...)` call is | `../assets/files/des-example3_sim_DES.R` |

R packages and functions the R code blocks in these mirrors actually print: `speciesgeocodeR` (">= v 1.0-6", `references/tutorial-5.md`:102) with `SpGeoCod()`,
`read.table(..., sep = "\t", header = TRUE)`, `complete.cases()`, `rowSums()`, `write.table()`, and the threshold object `occ.thresh <- 0.1` (`:107`, "at least 10% occurrence in an area required"); `simDES` installed by `library(devtools)` + `install_github("thauffe/simDES")`
(`:153-154`), `library(simDES)` (`:155`), help page called with `?sim_DES` (`:158`), main call at `:161-165`; and, on the wiki page only, `source(DES_input_preparation.R)`, `DESin()`, `summary()`, `par(ask = T)`, `plot()`, `write.DES.in()` (`references/des-model.md`:21-33 and 43-75).

### Route 2 deletes rows: the two area-coding rules are asymmetric

Route 2 (coordinates → areas) is the one documented generator that can lose data without saying so.
The corpus shows the mechanism and never comments on it, so read the code, not the prose.

* **Fossils get exactly one area, no threshold.** `foss <- data.frame(fos, higherGeography = fos.class$sample_table$homepolygon)`
  (`references/des-model.md`:51, `references/tutorial-5.md`:113) pins every occurrence row to the single
  polygon `SpGeoCod()` returned for it; the string `occ.thresh` does not appear anywhere in that
  half of the block.
* **Then a `complete.cases` subset drops rows.** `foss <- foss[complete.cases(foss),]`
  (`references/des-model.md`:52, `references/tutorial-5.md`:114) is called on the whole joined frame, so
  an occurrence that produced no usable area value — or that was already incomplete in another column —
  leaves the table. **(inferred:** that no area value means the point fell outside every polygon is
  `speciesgeocodeR` behavior the corpus never documents**.)**
* **Recent presences follow the opposite rule.** Only cells clearing `occ.thresh <- 0.1` — "at least
  10% occurrence in an area required" (`references/des-model.md`:46, `references/tutorial-5.md`:107) —
  are converted to area names (`references/des-model.md`:61-62), and the last subset keeps just those
  (`references/des-model.md`:65).
* **Read the asymmetry in the right direction: the threshold is recent-only, and it is the only recent
  filter.** `grep -n occ.thresh references/des-model.md` returns exactly three lines — `:46` (the
  definition), `:61` and `:62` (both in the recent half) — and nothing in the fossil half
  (`references/des-model.md`:48-52); the tutorial's twin of the block gives `:107`, `:124`, `:125` with
  the same empty fossil half (`references/tutorial-5.md`:110-114). So occupancy proportions are never
  computed on the fossil side at all (`references/des-model.md`:60 divides only `rec.class$spec_table`):
  a **fossil** row is dropped only for being incomplete (`references/des-model.md`:52), never for low
  occupancy, while a **recent** presence is dropped at under 10% even when its area resolved perfectly.
  Do not paraphrase this as `a 10% area-occupancy filter is applied to the occurrences` — that wording is
  wrong for half the data (`references/des-model.md`:51 pins each fossil row to `homepolygon` with no
  threshold).
* **Consequences, each labelled.** A taxon can lose *all* its fossil rows and vanish from `foss.txt`; it
  can lose recent rows in one or both areas; and with no recent row at all it is handed to
  `PyRateDES.py -recent` (`references/tutorial-5.md`:143) with an empty present range — absence from that
  file is how the docs encode "no living representative" (`references/tutorial-5.md`:55). **(inferred;**
  the corpus never states what PyRateDES does with such a taxon**.)** That a resulting bias runs toward
  *inflated local extinction* is the critic's claim and this suite cannot source it: DES estimates "rates
  of local extinction within areas" (`../pyrate/references/home.md`:54) and no mirror says what a missing
  recent row does to that estimate **(inferred, unverified)**.
* **The sanity check the page itself runs comes too late.** Both wiki examples look at the reconstruction
  under the comment "#explore the data for potential biases" with `summary(exp1)` and `plot(exp1)`
  (`references/des-model.md`:27-30, CN `references/des-model-cn.md`:28-31; the example-2 pair at
  `references/des-model.md`:71-75) — but on the *post-subset* object, so they display the damaged table and
  never what was dropped. Tutorial route 2 prints no `summary()`/`plot()` at all, and `-plot_raw` (`:95`) is
  likewise after generation. Add the four counting commands in `references/route2-area-coding-hazards.md` §5 before you
  hand `foss.txt`/`pres.txt` to `PyRateDES.py`.
* **Paths in that block are broken in three different ways** — see the Pitfalls bullet and §6 of
  `references/route2-area-coding-hazards.md`.

## The complete documented `PyRateDES.py` option list

Everything below is what exists in this corpus — **55 distinct documented option names**, every one of them verified to occur literally in `references/tutorial-5.md` (a `grep -q -- "-<name>"` loop over the 55 names finds 55/55; spot-check `grep -o -- '-ncat\|-data_in_area\|-logTraitD' references/tutorial-5.md`). A 56th string, `-qtime` (twice on `:79`), is by inference a typo variant of `-qtimes` — the docs never flag it. Anything beyond this list (preservation models other than `-mG`, prior options, `-A` values other than `0`/`3`, the values of `-r`) is **not documented here**; `home.md`:54 says the DES command list is still in preparation, so treat *absent from this list* as *absent from the documentation*, never as *unsupported*.

Input generation (with `-fossil`/`-recent`), `references/tutorial-5.md`:65-95 — `-fossil` :65, `-recent` :67, `-wd` :69, `-filename` :71, `-bin_size` :73, `-rep` :75, `-trim_age` :77, `-translate` :79, `-taxon` :81, `-area` :83, `-age1` :85, `-age2` :87, `-timeline` :89, `-site` :91, `-data_in_area 1` :93, `-plot_raw` :95.

Analysis, summary, plotting — `-d` :186 (the replicated input file), `-out` :189, `-n` :191, `-s` :191, `-p` :191 (that one sentence names three flags for two quantities: what `-p` does is **not documented for this program**, and neither value it carries is a default — see *Not documented in this wiki*), `-A` :197 (`-A 0` default Bayesian, `-A 3` ML — which "requires the Python library *nlopt*", :175), `-sum` :206 and :341 (the prose that introduces them is at :203 and :338 but never spells the flag), `-b` :338 (burn-in, "default 0"; its unit is stated for the `-sum` route only, never for the `-plot` lines that pass `-b 200` at :349 and :368), `-plot` :349 (introduced without the flag at :346), `-plotCI` :356.

Preservation, rates-through-time, constraints — `-mG` :213, `-ncat` :213 (default 4 — the only tunable in this group whose default the docs pin as a value: `grep -rn -- '-ncat' references/*.md` hits one sentence at :213, its CN twin `references/tutorial-5-cn.md`:214 and `route2-area-coding-hazards.md` §7), `-qtimes` :223, `-TdD` :223, `-TdE` :223, `-symd`/`-syme`/`-symq` :231, `-constr` :233.

Covariate-dependent — `-varD`/`-varE` :251-257 (introduced in prose at :238-248), `-r` :261, `-symCovD`/`-symCovE` :267, `-constrCovD_0`/`-constrCovE_0` :269.

Diversity-dependent — `-DivdD`/`-DivdE` :274, `-DdE` :280, `-symDivdD`/`-symDivdE` :284, `-constrDivdD_0`/`-constrDivdE_0` :286.

Trait-dependent — `-traitD`/`-traitE` :307, `-logTraitD`/`-logTraitE` :309, `-catD`/`-catE` :331.

The `-constr` index set is the only one fully enumerated (`references/tutorial-5.md`:233): `1` dispersal A→B, `2` dispersal B→A, `3` extinction in A, `4` extinction in B, `5` sampling in A, `6` sampling in B; "Several constraints can be combined e.g. `-constr 3 5 `". For the covariate and diversity index sets the tutorial gives only single examples (`-symCovD 1`, `-constrCovD_0 1 4`, `-constrDivdD_0 2`, `-constrDivdE_0 1`) — and those indices are *not* the `-constr` ones: `-constr 1` fixes "the dispersal rate from area A to B" (`:233`), while `-constrCovD_0 1 4` "removes through index 1 the effect of the first covariate on the dispersal rate from area A to B" (`:269`), i.e. the covariate index counts covariate × direction and its full space is nowhere enumerated.

## Running a DES analysis

Every subsection is the tutorial's own heading and its own command lines; `../assets/files/des-analysis_commands.txt` holds all 17 analysis/summary/plot command lines verbatim with line numbers.

### Basic analysis with constant rates (`### Basic DES analysis with constant rates`, :177)

Rates "constant through time but differ between both areas" (:183); the default algorithm is Bayesian (`-A 0`).
The ML alternative has an extra dependency the corpus states once, outside this section: "PyRateDES requires the Python library *nlopt* for fitting models with Maximum likelihood. It can be installed with `pip install nlopt`" (`references/tutorial-5.md`:175 — `grep -rn nlopt references/*.md` hits only that line and its CN twin `references/tutorial-5-cn.md`:176, so nothing documents an ML fallback if `nlopt` is missing), and an `-A 3` result carries no parameter uncertainty (:197).

```
python ./PyRateDES.py -d ./example_files/DES_examples/Carnivora/Carnivora_1.txt
python ./PyRateDES.py -d ./example_files/DES_examples/Carnivora/Carnivora_1.txt -n 500000 -s 1000 -p 10000
python ./PyRateDES.py -d ./example_files/DES_examples/Carnivora/Carnivora_1.txt -A 3
python ./PyRateDES.py -d ./example_files/DES_examples/Carnivora/Carnivora_1.txt -sum ./example_files/DES_examples/Carnivora/Carnivora_1_0.log
```
(:186, :194, :200, :206 — output file "will be named *Carnivora_1_0.log* and is saved where the input data was", :189.)

### Heterogeneity in preservation across taxa (`### DES analysis with heterogeneity...`, :211)

`-mG` makes the mean sampling rate equal `q` with heterogeneity from "a discretized Gamma distribution with *n* categories" (`references/tutorial-5.md`:213); `-ncat` sets `n`, and its default is the one tunable quantity of this model the corpus pins down twice over, both value and why: "The default of four categories (`-ncat 4`) is usually sufficient to account for heterogeneity across lineages and a higher number increases computation time" (:213) — no other rate-model option in this section has a printed default (`grep -rn -- '-ncat' references/*.md` returns only `:213`, its CN twin `references/tutorial-5-cn.md`:214 and `references/route2-area-coding-hazards.md` §7). The tutorial also prices the benefit twice: "Incorporating sampling heterogeneity improves the rate estimation" and heterogeneity "is computationally inexpensive to infer as it only adds a single free parameter to the model", hence its unconditional recommendation that heterogeneity "should therefore be always included in DES models" (:213).

```
python ./PyRateDES.py -d ./example_files/DES_examples/Carnivora/Carnivora_1.txt -mG
```
(:216.)

### Time-variable skyline with rate shifts (`### Time variable model with rate shifts (Skyline model)`, :221)

Shifts are given with `-qtimes`; add `-TdD` and `-TdE` to let dispersal and extinction vary through time (:223). Constraints: `-symd`, `-syme`, `-symq` force equality between areas (rates still differ among time strata), `-constr` freezes selected rates across strata (:231-233).

```
python ./PyRateDES.py -d ./example_files/DES_examples/Carnivora/Carnivora_1.txt -TdD -TdE -mG -qtimes 20.43 15.97 13.65 11.63 7.25 5.33 2.58 -n 1000001 -s 1000 -p 1000
```
(:226 — the same seven shift ages are printed **ascending** at :349 and :361, and ascending is in fact the majority order (one descending command at :226 against four ascending at :349, :361, :368, :382), so do not read either order as required; see the *Not documented in this wiki* table.)

### Covariate-dependent dispersal and extinction (`### Covariate dependent dispersal and extinction models`, :236)

"an upgraded version of the original DES model" (:238): model dispersal and/or extinction as a function of a time-variable predictor (sea level, temperature). Same or different predictors for the two rate types; several covariates go in one directory (:248). Covariates are "scaled to the range [0,1]" by default, changed with `-r` (:261 — the values of `-r` are not printed). Composable with `-qtimes`, `-TdD`/`-TdE` and `-mG` (:263).

```
python ./PyRateDES.py -d ./example_files/DES_examples/Carnivora/Carnivora_1.txt -varD ./example_files/DES_examples/Carnivora/covariate_dispersal -varE ./example_files/DES_examples/Carnivora/covariate_extinction
python ./PyRateDES.py -d ./example_files/DES_examples/Carnivora/Carnivora_1.txt -varE ./example_files/DES_examples/Carnivora/covariate_eurasia ./example_files/DES_examples/Carnivora/covariate_northamerica
```
(:251, :257 — the second form passes **two** directories to `-varE`: "The path to the first folder are the time-series for area 1 and the second path for area 2", :254.) Constraints `-symCovD`/`-symCovE` (symmetric effect in both areas) and `-constrCovD_0`/`-constrCovE_0` (effect set to zero) take indices (:267, :269).

### Diversity-dependent dispersal and extinction (`### Diversity dependent dispersal and extinction models`, :272)

"Dispersal rate into an area could decline with the increase in diversity of the respective area and extinction rate may increase with the area's diversity" (:274); `-DdE` adds the invasion effect where "immigrating taxa drive resident taxa to extinction" (:280). Composable with `-qtimes` and `-mG` (:280).

```
python ./PyRateDES.py -d ./example_files/DES_examples/Carnivora/Carnivora_1.txt -DivdD -DivdE
```
(:277. The prose names the program `PyRateDES2.py`; the command names `PyRateDES.py`. Both are kept verbatim in `references/tutorial-5-cn.md`:275 and :278, so the discrepancy is upstream, not a translation artifact.) Constraints: `-symDivdD`/`-symDivdE`, `-constrDivdD_0`/`-constrDivdE_0` (:284, :286).

### Trait-dependent dispersal and extinction (`### Trait dependent dispersal and extinction models`, :289)

Continuous traits (`Body_mass_1.txt`) with `-traitD`/`-traitE`; "By default, all traits are internally log-transformed", turned off with `-logTraitD 0` / `-logTraitE 0` (:309). Categorical traits (`FamilyGenera.txt`) "needs to be numerical coded", with `-catD`/`-catE`, and "Additional column can be used to reflect the hierarchical taxonomy of the taxon" (:317, :331).

```
python ./PyRateDES.py -d ./example_files/DES_examples/Carnivora/Carnivora_1.txt -traitD ./example_files/DES_examples/Carnivora/Body_mass_1.txt
python ./PyRateDES.py -d ./example_files/DES_examples/Carnivora/Carnivora_1.txt -catD ./example_files/DES_examples/Carnivora/FamilyGenera.txt
python ./PyRateDES.py -d .../example_files/DES_examples/Carnivora/Carnivora_1.txt ./example_files/DES_examples/Carnivora/covariate_extinction -traitD .../example_files/DES_examples/Carnivora/Body_mass_1.txt
```
(:304, :328, :314 — the third line is exactly as printed and is missing the flag that `covariate_extinction` belongs to; by inference from :251 it should read `-varE ./example_files/.../covariate_extinction`. Label the fix as your own edit, not the docs'.)

## Summarising and plotting DES output

The tutorial's own section is `## Summarizing and plotting the DES output` (:334) with two subsections, `### Summarize model probabilities` (:336) and `### Plotting model output` (:344).

* **Parameter summaries.** `-sum <output>.log` gives "the mean and 95% credible interval of all model parameters of a Bayesian analysis" (:203); the file is described as the "**mcmc.log** file" and `-b` sets the burn-in, "default 0; e.g. 1000 for the first 1000 MCMC generations" (:338). Command at :341.
* **Model probabilities — a documented gap.** The section heading is `### Summarize model probabilities` (:336) but the body prints only the `-sum`/`-b` command; **no DES command for marginal likelihoods, Bayes factors or model probabilities appears anywhere in this corpus.** `-mProb` and `-BF` exist only for PyRate.py's BDMCMC output (`../pyrate-summarize-results/references/summarize-results.md` lines 63-67), and no mirror says they read a DES log. Do not DES-model-select with them by assumption.
* **Rates through time.** From the "**marginal_rates.log** file" — "the trajectory of the area-specific dispersal and extinction rates through time" (:346):

```
python ./PyRateDES.py -d ./example_files/DES_examples/Carnivora/Carnivora_1.txt -TdD -TdE -qtimes 2.58 5.33 7.25 11.63 13.65 15.97 20.43 -mG -plot ./example_files/DES_examples/Carnivora/Carnivora_1_0_q_2.58_5.33_7.25_11.63_13.65_15.97_20.43_TdD_TdE_marginal_rates.log -b 200 -plotCI 0.75 0.95
```
(:349; `-plotCI` "allows to specify the width of the credible intervals to be plotted. Default is only one interval of 0.95" :356; the run that produced that log is reprinted at :361. By inference from :349/:368, `-plot` needs the model flags restated on the same command line — the tutorial never says so in prose.)
* **Covariate / diversity / trait effects** (`:365`, command `:368`) → figure of body mass vs dispersal and temperature vs extinction; the run that produced it is `:382` (it adds `-constr 1 2`, i.e. both dispersals constant across strata, which the plotted log name `..._TdD_Eexp_constr_0_1_TraitD_CatD_G.log` renders as `constr_0_1`; `Eexp` and the `_G` suffix are nowhere explained).
* **Observed diversity before modelling**: `-plot_raw` writes "a plot in PDF format in `-wd` of the observed diversity trajectories and their 95% credible interval in the two area" (:95).

The four figures in `../assets/images/`, with the tutorial line that embeds each:

| Image | Shows | Attached to |
| --- | --- | --- |
| `../assets/images/DES_observed_diversity.png` | observed diversity trajectories + 95% CI in the two areas | `-plot_raw`, `references/tutorial-5.md`:97 |
| `../assets/images/DES_rate_shifts_through_time.png` | area-specific dispersal/extinction rates through time, skyline shifts | the `-plot ... -plotCI 0.75 0.95` command, `:352` |
| `../assets/images/DES_bodymass_dispersal.png` | `:373`: "how body mass (in kg) influences dispersal rate and how this effect varies among families (labeled 1-16)" | `:371` |
| `../assets/images/DES_temperature_extinction.png` | `:377`: "the impact of paleotemperature on extinction rate is stronger in area 1 (Eurasia) than in area 2 (North America)" | `:375` |

## Worked example

Run from the PyRate repo root after `cd /path/to/PyRate` (`references/tutorial-5.md`:57-59). `FIX` is this suite's `../assets/files/` directory (give it the absolute path). The tutorial's own paths (`./example_files/DES_examples/Carnivora/`) are rewritten to a local `./DES_demo/` because the corpus must not be written into; every flag and value below is the tutorial's. Strip the fixture `#` provenance header first, because **no mirror says whether PyRateDES skips comment lines in the input tables**.

```sh
FIX=/path/to/PyRate-skills/assets/files            # this suite; use the real path in your checkout
cd /path/to/PyRate                                 # tutorial-5.md:59
mkdir -p DES_demo
for f in des-CarnivoraFossils des-CarnivoraRecent; do
    grep -v '^# ' "$FIX/$f.txt" > "DES_demo/${f#des-}.txt"   # -> CarnivoraFossils.txt, CarnivoraRecent.txt
done
head -3 DES_demo/CarnivoraFossils.txt | cat -A     # confirm a header row and 4 tab-separated columns

# 1. generate the replicated input files - tutorial-5.md:63, path rewritten to ./DES_demo
#    If this one step exits 1 with `ValueError: The truth value of an empty array is ambiguous`, you are
#    on numpy 2.x and the runtime is not usable for DES: this generation step is the place in the tutorial
#    where a passing `python -c 'import numpy, scipy'` proves nothing, because the raise comes from
#    `if trim_age > 0:` in `pyrate_lib/lib_utilities.py` rather than from an import. The A/B measurement
#    and the pin that clears it: ../pyrate-installation/SKILL.md, its subsection headed
#    *numpy 2.x: every documented check passes and `PyRateDES.py` still dies*. That subsection is an
#    observation on one machine, not a
#    claim of the corpus - no page of this wiki states a numpy version bound at all.
python ./PyRateDES.py -fossil ./DES_demo/CarnivoraFossils.txt -recent ./DES_demo/CarnivoraRecent.txt -wd ./DES_demo -filename Carnivora -bin_size 0.5 -rep 10

# 2. constant rates (:186) and heterogeneous preservation (:216)
python ./PyRateDES.py -d ./DES_demo/Carnivora_1.txt
python ./PyRateDES.py -d ./DES_demo/Carnivora_1.txt -mG

# 3. skyline with the shifts the tutorial uses (:226) - it already carries -n 1000001 -s 1000 -p 1000,
#    because the documented default is only 100,000 iterations sampled every 100 (:191; longer-chain example :194)
python ./PyRateDES.py -d ./DES_demo/Carnivora_1.txt -TdD -TdE -mG -qtimes 20.43 15.97 13.65 11.63 7.25 5.33 2.58 -n 1000001 -s 1000 -p 1000

# 4. summarise (:341) and plot (:349) - note :349 lists the same -qtimes ages in reverse order
#    (step 3 above keeps :226's descending order; the docs print both - 1 descending vs 4 ascending -
#    and never state a required sort, so each line here copies its source line: see "Not documented")
python ./PyRateDES.py -d ./DES_demo/Carnivora_1.txt -sum ./DES_demo/Carnivora_1_0.log -b 1000
python ./PyRateDES.py -d ./DES_demo/Carnivora_1.txt -TdD -TdE -qtimes 2.58 5.33 7.25 11.63 13.65 15.97 20.43 -mG -plot ./DES_demo/Carnivora_1_0_q_2.58_5.33_7.25_11.63_13.65_15.97_20.43_TdD_TdE_marginal_rates.log -b 200 -plotCI 0.75 0.95
```
Steps 2-4 are single-line commands exactly as the tutorial prints them (`:216`, `:226`, `:341`, `:349`); only the file paths differ. The loop, the `head -3 | cat -A` check and the path rewrites were executed against the fixtures in this suite (output: a `scientificName earliestAge latestAge higherGeography` header plus tab-separated rows); the `python ./PyRateDES.py ...` lines are executed by this suite's own end-to-end gate, `../scripts/audit_tutorial_runs.py`, which runs the tutorial mirrors' command sequences against upstream `PyRate` master in a throwaway workdir. Three things no page of this corpus states are now measured there; each is a machine observation (one machine, numpy 1.26.4 + scipy 1.13.1, see `../pyrate-installation/SKILL.md`), not a claim of the docs: (1) step 1 writes `<filename>_<replicate>.txt` for replicate **1..`-rep`** into the `-wd` directory — `-rep 2` produced exactly `Carnivora_1.txt` and `Carnivora_2.txt`, and there is **no** `_0` input file; (2) the analysis really does name its log `<stem>_0.log`, as `:189` says — step 2 at the documented default of "100,000 iterations" (`:191`) does not fit the gate's per-command budget, and the bounded re-run that proves the line starts correctly writes `Carnivora_1_0.log` plus `Carnivora_1_0_marginal_rates.log`; (3) `-out` is **not** part of the generation step: appended there it is accepted but changes nothing (identical product names, rc 0), and `:189` attaches `-out` to the `-d` analysis output only.
The nine-row fossil table here is *not* the full Carnivora dataset, so `-bin_size 0.5` over ~31 Myr produces far more bins than taxa — the tutorial's own advice is "Bin size should be chosen as a compromise between the desired resolution and data availability" (`references/tutorial-5.md`:73, repeated at `references/des-model.md`:17). Step 1's output filename pattern `Carnivora_<replicate>.txt` is by inference from `-filename Carnivora -rep 10` (:63) plus `-d ./example_files/DES_examples/Carnivora/Carnivora_1.txt` (:186); no mirror ever prints a directory listing of the generated files.

## Pitfalls

- **Two documents, two generators.** `references/des-model.md`:21-33 makes the input files with R (`source(DES_input_preparation.R)` → `DESin()` → `write.DES.in()`); `references/tutorial-5.md`:63 makes them with `PyRateDES.py -fossil/-recent`, and the tutorial's own route-2 script (`:105-134`) deliberately *stops* at writing `foss.txt`/`pres.txt` and never calls `DESin()`. The wiki page also links a different example set (`example_files/DES_input_data/Example_1_minimum_data.txt`, `references/des-model.md`:15) than the tutorial (`example_files/DES_examples/Carnivora/CarnivoraFossils.txt`, `references/tutorial-5.md`:29). Pick one route and say which; do not mix `write.DES.in()` output with the tutorial's analysis commands.
- **`DES_input_preparation.R` vs `pyrate_DES_utilities.R`.** `references/des-model.md`:15 tells you to load the R utilities file named `pyrate_DES_utilities.R`, but the code block that follows sources `DES_input_preparation.R` (`:21`), which is also the name `../pyrate/references/home.md`:54 gives. The CN twin reproduces both names (`references/des-model-cn.md`:16 and :22), so the wiki page is internally inconsistent; nothing in this corpus prints either file's contents.
- **The `-translate` arithmetic.** With `-translate 66.0`, "a Cretaceous rate shift would need to be specified with 79.0 instead of 145.0" (`references/tutorial-5.md`:79) — subtract the shift from every `-qtimes` age. Note that the bullet calls the option `-qtime`: that string occurs twice on `references/tutorial-5.md`:79 and twice more on `references/tutorial-5-cn.md`:80 (source page `pyrate_tutorial_5.md`:71 / `pyrate_tutorial_5-cn.md`:71), i.e. four times corpus-wide and never anywhere else; every command line in these mirrors uses `-qtimes`, and the CN twin reproduces the same two `-qtime` strings rather than normalizing them, so the typo is upstream. It also requires a rate shift at `bin_size/2` and "all rates after this shift should be ignored".
- **Which file holds the `site` column? The tutorial contradicts itself.** `references/tutorial-5.md`:43 puts it in the fossil table — it says a coeval assemblage is handled by 'specifying a "site" column in the input data' (the doc prints `site` in straight double quotes there) and links `CarnivoraFossilsSite.txt`, a fossil file. But `:91` describes `-site` as "specifying the name of the column in the `-recent` text file with the ID of the assemblage for each occurrence" — yet the recent table printed at `:47-53` has only `scientificName` and `higherGeography`, and the randomization being controlled is that of fossil ages (`:25`). `references/tutorial-5-cn.md`:92 translates the `-recent` wording faithfully, so the conflict is upstream, not a translation artifact. Do not resolve it by guessing: use `../assets/files/des-CarnivoraFossilsSite-EXCERPT.txt` (fossil-side, per `:43`) and say so.
- **Ages are in million years**, and `-bin_size` inherits that unit (`references/tutorial-5.md`:73); mixing calendar ages (negative) with Myr is uncaught.
- **The present-day table is an assumption, not data, when route 2 is used**: "DES assumes the present data to be complete, so a use of occurrence records for recent data is only for very well samples and curated data" and native ranges should be used, since anthropogenic influence "will inflate, or sometimes decrease, the recent distribution of many taxa" (`references/tutorial-5.md`:102, `references/des-model.md`:40; the English "very well samples" is the docs' own typo for *sampled*, kept in both mirrors).
- **Route 2 also silently deletes rows before you ever get a file to check** — the fossil side is pinned to one area with no threshold and then subset to complete cases (`references/des-model.md`:51-52, `references/tutorial-5.md`:113-114), while the recent side keeps only cells at or above `occ.thresh` = 0.1 (`references/des-model.md`:46, `:61-62`, `:65`). A taxon can therefore lose every fossil row, or its present range, or both, with no count printed anywhere on either page. Line-by-line trace, the `inferred`/`undocumented` split and a four-command check: `references/route2-area-coding-hazards.md` §2-§5.
- **The route-2 script's paths do not resolve, in three separate ways.** (i) The wiki page opens every example file from `Example_data/` (nine occurrences on six lines of `references/des-model.md`:24, 33, 49, 50, 55, 57) while the same page's own links put those files under `example_files/DES_input_data/` (`references/des-model.md`:15) — no corpus page ever names an `Example_data` directory, so that mapping is inference from the links. (ii) The tutorial's route-2 block was corrected to `.../PyRate/example_files/DES_examples/DES_input_data/` everywhere **except** one line, which still carries the wiki's literal (`references/tutorial-5.md`:117, CN `references/tutorial-5-cn.md`:118). (iii) `references/tutorial-5.md`:119 is missing a `/` — it prints `DES_input_dataExample_2_recent_coordinates.txt` — and the CN twin reproduces it at `:120`, so it is upstream. Neither directory is ever printed as a plain unquoted path (route 1 uses `./example_files/DES_examples/Carnivora`, `:29` and `:63`), and this suite mirrors the pages, not the data: `ls ../assets/files | grep -ci "Example_"` prints 0.
- **No `DES_demo/` ships with this skill.** The docs have you work from the PyRate checkout — `cd /path/to/PyRate` (`references/tutorial-5.md`:57-59) — and produce the DES input files there with `PyRateDES.py -fossil/-recent` (`:61-63`); the `mkdir -p DES_demo` in *Worked example* is this suite's own step, so that directory lands wherever you run the loop, never here (`ls -d DES_demo` inside this skill folder prints nothing). A `DES_demo/` found here would be a leftover from running the loop in the wrong place; the real inputs are what the `grep -v '^# '` loop writes from `../assets/files/`, and `-fossil`/`-recent` should point at those.
- **`-mG` is recommended always** (`references/tutorial-5.md`:213), so a plain `-d file.txt` run is a baseline, not a reportable model — and remember `-A 3` runs give no credible intervals (`:197`).
- **Replicates are separate files and separate runs.** The `-d` examples always take `Carnivora_1.txt`, replicate 1 of `-rep 10`; this corpus never documents how to combine results across replicates (see *Not documented in this wiki* below). Do not average logs by invention — state the choice.
- **Fixtures carry `#` headers.** `.txt` DES tables in `../assets/files/` begin with provenance comment lines (contract §6); strip them (`grep -v '^# '`) before passing a fixture to `PyRateDES.py -fossil`.

## Not documented in this wiki

| Unanswered question | Why you must not fill it in |
| --- | --- |
| What is inside a generated DES input file (`Carnivora_1.txt`)? Columns, bin encoding, how the two areas are represented | no mirror prints the file or its structure; `-d` is shown only as a path (`references/tutorial-5.md`:186). The core-PyRate `-d` origin/extinction table documented in `../pyrate-input-file/references/preparing-input-file.md` is a *different* format and must not be assumed here |
| How to pool or compare results across the `-rep` replicates | the tutorial analyses one replicate (`:186`-`:382`) and never mentions the other 9 |
| What the `_0` in `Carnivora_1_0.log` means, and the general output-naming rule | `references/tutorial-5.md`:189 names that one file and adds only that `-out` "allows to add a user-defined name to the output". The `_0` string is never glossed anywhere: `grep -c 'Carnivora_1_0' references/tutorial-5.md` prints 5 — the prose at :189, the two `-sum` arguments at :206 and :341, and the two `-plot` arguments at :349 and :368 — and `references/tutorial-5-cn.md` reproduces all five without explaining them (same count there); the two `-plot` names extend it to `Carnivora_1_0_q_<shifts>_<flags>_marginal_rates.log`, whose trailing `_G` is likewise unexplained (:368). Whether `_0` is the `-A` algorithm index (`:197` defaults to `-A 0`), a run counter, or something else is **not documented** — the coincidence with the default algorithm is a hypothesis, not corpus text — so quote a DES output filename only by copying a printed example, never by rebuilding the pattern |
| Must `-qtimes` ages be ascending or descending? | the corpus prints **both** orders and never comments on sorting: exactly **one** descending command (`references/tutorial-5.md`:226, `20.43 … 2.58`) against **four** ascending ones (:349, :361, :368, :382, `2.58 … 20.43`) — `grep -c -- '-qtimes 20.43 15.97' references/tutorial-5.md` prints 1 and `grep -c -- '-qtimes 2.58 5.33' references/tutorial-5.md` prints 4. So the majority order is *ascending* while the order this skill quotes for the skyline run is *descending* — each command below keeps the order of the line it copies (`:226` in *Worked example* step 3, `:349` in *Rates through time*), which is a documentation-fidelity choice, **not** evidence that either order is required or ignored. If you reorder, say so; nothing in this corpus tells you whether the shift set is sorted internally |
| The legal values of `-r` (covariate scaling) | `:261` states the default ([0,1]) and that `-r` changes it, printing no example |
| What `-p` does for `PyRateDES.py`, and which of its two printed values is a default | `references/tutorial-5.md`:191 names `-n`, `-s` and `-p` for "the number of MCMC iterations and the sampling frequency" (two quantities, three flags) and never says which flag sets what. The only roles ever stated belong to `PyRate.py`: `../pyrate-command-reference/references/command-list.md`:65 "MCMC print-on-screen frequency." (its example, `-p 1000`, is the next line) and `../pyrate-bdnn/references/tutorial-bdnn.md`:232 "while `-p` sets the frequency of prints on your screen", about a `python ./PyRate.py` run two lines earlier. DES's own two values, 10000 at `references/tutorial-5.md`:194 and 1000 at `:226`, `:361`, `:382`, sit on different `-n`s, so neither is a default. Do not guess; `references/route2-area-coding-hazards.md` §7 tabulates every occurrence |
| The unit of `-b` on a DES `-plot` command | `references/tutorial-5.md`:338 states it for the `-sum` route only — "e.g. 1000 for the first 1000 MCMC generations" — while `:349` and `:368` pass `-b 200` to `-plot` and the sentence introducing `-plot` (`:346`) never mentions `-b`. The nearest analogue, for another program, counts samples: `../pyrate-continuous-covariates/references/tutorial-2.md`:124 "The command `-b 200` specifies that the first 200 samples are discarded as burnin"; and the core list states the option both ways inside one entry — `../pyrate-command-reference/references/command-list.md`:69 "Set the number of iterations to be discarded (i.e. not logged) from the analysis as burnin" then, at line 72, first 1,000 samples discarded. So name your unit instead of inheriting one |
| What `PyRateDES.py` does with a taxon that is in `-fossil` but has no row in `-recent` — the state route 2's `occ.thresh` filter can create (`references/des-model.md`:65) | the corpus describes only the whole-file case, "PyRateDES works for groups of taxa without any living representative. In this case the file with the recent distribution should contain only the header of scientificName and higherGeography" (`references/tutorial-5.md`:55), and requires the recent table to hold "the recent distribution of all taxa" (`references/tutorial-5.md`:25); whether `-data_in_area 1` (`:93`) or `-trim_age` (`:77`) changes the per-taxon outcome is stated nowhere |
| The index spaces of `-constrCovD_0`, `-constrCovE_0`, `-constrDivdD_0`, `-constrDivdE_0` beyond the four printed examples | `:269` and `:286` give one example each; unlike `-constr` (`:233`, all six indices named) no enumeration exists, so `-constrCovD_0 3` is uninterpretable |
| How to compute DES model probabilities / compare DES models | `### Summarize model probabilities` (`:336`) documents `-sum`/`-b` only; no `-A 1` thermodynamic-integration, marginal-likelihood or Bayes-factor route is given for DES (`../pyrate-command-reference/references/command-list.md` has none either) |
| Which priors DES uses, and any option to set them | the word `prior` does not occur in any of this skill's four mirrors (`grep -ci -- 'prior' references/*.md` returns `0` everywhere); only `:213` speaks of "a single free parameter", about `-mG` |
| Convergence criteria / ESS targets for DES chains | `:191` says only "you may have to increase the number iterations to reach convergence"; the diagnostics workflow lives in `../pyrate-mcmc-tuning/references/tutorial-6.md` for `PyRate.py` |
| Whether a DES analysis can handle more than two areas | `:23` says two, `references/des-model.md`:11 says "areas"; `-data_in_area 1` (`:93`) is about lineages known from a single area, not about adding areas |
| Does `PyRateDES2.py` exist as a shipped program? | one stray mention, `references/tutorial-5.md`:274; `../pyrate/references/home.md`:53 names only `PyRateDES.py` in the program list |
| Whether `#` comment lines are tolerated in DES input tables | never stated; that is why the Worked example strips them |
| What `Sim[[1]]` is, and what `sim_DES`'s other return elements hold; the meaning of `Ncat = Inf, alpha = 1` in the printed call | `:161-169` prints the call and writes only `Sim[[1]]`; the docs point to `?sim_DES` in the external package instead of describing the arguments |
| The PDF/filename produced by `-plot_raw` and by `-plot` | `:95` says "a plot in PDF format in `-wd`", `:354` says "an R script and a PDF file"; no names are printed |
| The columns of the route-2 coordinate tables (`Example_2_coordinates.txt`, `Example_2_recent_coordinates.txt`) and of the shapefile | `references/tutorial-5.md`:110-121 shows only that they are read with `sep = "\t", header = TRUE` and that area names come from the `Region` attribute; no mirror prints a single row, so latitude/longitude column names are unrecorded |
| The shape of the R route's output (`write.DES.in()` files, `Example1_DES_in*`) | `references/des-model.md`:33 shows the call only; the wiki page never opens the resulting file, and it is not stated to be the same artifact `PyRateDES.py -fossil/-recent` writes |

## Related skills

- `pyrate` — `../pyrate/references/home.md` owns the program list, the `pyrate_lib` requirement (`../pyrate/references/home.md`:53), "A detailed command list is in preparation" for DES (`../pyrate/references/home.md`:54) and the only DES citation in the corpus (`../pyrate/references/home.md`:56).
- `pyrate-command-reference` — owns `command-list.md` and `../pyrate-command-reference/scripts/pyrate_commands.py`, both for `PyRate.py` only; neither documents a single DES option, which is why this skill enumerates its own list above.
- `pyrate-input-file` — the core occurrence table `Species Status MinT MaxT [Trait]`, `epochs_q.txt` and the `*_PyRate.py` structure. Different format from every DES table above; do not swap them.
- `pyrate-installation` — the virtual environment `PyRateDES.py` runs in; the interpreter rule itself is stated in the page that skill mirrors, `../pyrate-installation/references/home.md`:69 ("Python 3.x is currently not supported", tested with "Python 2.6 – 2.7"), and `pip install nlopt` for `-A 3` is at `references/tutorial-5.md`:175.
- `pyrate-preservation-models` / `pyrate-bd-analysis` — the `PyRate.py` preservation models (`-mHPP`, `-mG` with `-ncat`) and birth-death analyses; DES has its own `-mG` semantics (`references/tutorial-5.md`:213) and no documented equivalent of the core model catalogue.
- `pyrate-continuous-covariates` — `PyRateContinuous.py`'s covariate models; unrelated to DES `-varD`/`-varE`.
- `pyrate-diversity-dependence` — `PyRateMCDD.py` multi-clade diversity dependence; DES diversity dependence is `-DivdD`/`-DivdE`/`-DdE` and lives here.
- `pyrate-trait-age-models` — the `PyRate.py` Covar trait-correlation models (`-mCov`, `-pC`); DES trait effects are `-traitD`/`-traitE`/`-catD`/`-catE` and live here.
- `pyrate-rjmcmc` — RJMCMC rate-shift model search for `PyRate.py`; DES shift models are fixed by `-qtimes`, with no search option documented.
- `pyrate-summarize-results` — the `-plot`, `-plot2`, `-mProb`, `-BF` functions and the `*_sum.txt` / `*_mcmc.log` / `*_marginal_rates.log` descriptions for `PyRate.py` (that mirror never names the program implementing them — no `PyRate_summarize.py` string exists anywhere in the corpus); whether they accept DES logs is undocumented.
- `pyrate-mcmc-tuning` — `tutorial-6.md` MCMC tuning/diagnostics for `PyRate.py`; DES only has `-n`/`-s`/`-p`/`-b`.
- `pyrate-bdnn` — `tutorial-bdnn.md` uses the same Carnivora data with family, log body mass and continent (Eurasia / North America) as neural-network inputs; that is a different model of the same biological tables, not a DES option.

## Resources

| File | What's in it | Load when |
| --- | --- | --- |
| `references/tutorial-5.md` | The whole January 2022 DES tutorial: the three input routes, all 55 documented options, all 17 command lines, defaults (`-A 0`, 100,000 iterations, `-ncat 4`, `-b 0`, covariate scaling [0,1]), the four figures | Any question about running, modelling, summarising or plotting DES — it is the only source of DES command syntax in this corpus |
| `references/tutorial-5-cn.md` | Full Simplified-Chinese twin (every line = the English line +1, because its frontmatter is 9 lines vs 8) | When an English bullet is ambiguous; it reproduces the `-site`-is-in-`-recent` wording (`:92`), `PyRateDES2.py` (`:275`) and the malformed `:315` command, so all three are upstream, not translation |
| `references/des-model.md` | The wiki page: R-based preparation, `DESin()`/`write.DES.in()`/`SpGeoCod()` blocks, DarwinCore note, `Example_1_minimum_data.txt` / `Example_2_coordinates.txt` / `Example_regions.shp`, the "neartic"/"paleoartic" example | Only for the **R** preparation route and its function names — the page prints no `PyRateDES.py` command line at all, so nothing about running or plotting comes from here |
| `references/des-model-cn.md` | Chinese twin of the wiki page (`:12` restores "两个制表符分隔的文本文件", i.e. two tab-delimited text *files*) | Resolving the wiki's clipped English sentences |
| `references/route2-area-coding-hazards.md` | Suite-authored detail layer (**not a mirror**, and it quotes no corpus prose): the two asymmetric area-coding rules traced line by line (`references/des-model.md`:51-52 against `:46`, `:61-62`, `:65`), what each deletion can cost and how much of that is only **inferred**, the `summary()`/`plot()` bias check the wiki runs *after* the subsets (`:27-30`, `:71-75`) plus four counting commands, the three ways the block's printed paths fail (`Example_data/`, the stale literal at `references/tutorial-5.md`:117, the missing slash at `:119`), and every `-n`/`-s`/`-p`/`-b` value the docs print next to what they actually state about it | Before running route 2; before quoting a `-p` or `-b` number as a default; when a DES run reports more local extinctions than the data seems to support and route 2 produced the input (the causal claim is **unverified** — what this file establishes is the silent row loss) |
| `../pyrate/references/home.md` | DES at `../pyrate/references/home.md`:53 (program heading + the `pyrate_lib` requirement), :54 "A detailed command list is in preparation." (the same sentence supplies the "two discrete areas" framing and points at `DES_input_preparation.R`), :56 the Phil Trans R Soc B 2016 citation | Citing DES, or justifying why the option list here is exhaustive-by-necessity |
| `../pyrate-summarize-results/references/summarize-results.md` | `-plot`/`-plot2`/`-mProb`/`-BF` and the `*_sum.txt`, `*_mcmc.log`, `*_marginal_rates.log`, `*_marginal_likelihood.txt` descriptions for `PyRate.py` (lines 33-67) | Only to confirm those tools are documented for PyRate, not for DES |

```sh
# run these from this skill directory
grep -n "two discrete and predefined areas" references/tutorial-5.md
grep -n "should therefore be always included in DES models" references/tutorial-5.md
grep -n '^\* `-' references/tutorial-5.md | wc -l                          # 26 = the option-definition bullets
grep -n "inpute\|seperate\|very well samples\|PyRateDES2" references/tutorial-5.md
grep -n "DES_input_preparation.R\|pyrate_DES_utilities.R" references/des-model.md
grep -c "^python ./PyRateDES.py" references/tutorial-5.md                  # 17 = the 17 in ../assets/files/des-analysis_commands.txt
grep -c -E "\-varD|\-DivdD|\-traitD|PyRateDES" ../pyrate-command-reference/references/command-list.md   # prints 0: DES is absent from the wiki command list
grep -n "Phil Trans\|command list is in preparation" ../pyrate/references/home.md
```

## Runnable fixtures (`../assets/files/`)

All are extracted from the fenced blocks and printed tables of this skill's mirrors; provenance (corpus source lines *and* the equivalent mirror lines) is in each file's header. **None contains data invented to contradict the docs**; every `.R` and command fixture was byte-diffed against its mirror block and the four files marked EXCERPT carry the truncated tables exactly as printed. `des-CarnivoraFossilsSite-EXCERPT.txt` is the only one whose extra column *values* are illustrative (the docs print a `site` column but no numbers for it).

| File | Run it? | What it makes concrete |
| --- | --- | --- |
| `../assets/files/des-CarnivoraFossils.txt` | yes, after `grep -v '^# '` | route 1 fossil table: `scientificName`/`earliestAge`/`latestAge`/`higherGeography`, 9 rows of `tutorial-5.md`:31-41 as tab-delimited text |
| `../assets/files/des-CarnivoraRecent.txt` | yes, same | route 1 recent table; `Canis` on two rows because it occurs in both areas (`tutorial-5.md`:45) |
| `../assets/files/des-CarnivoraRecent-HEADERONLY.txt` | yes, same | the header-only recent file for a group with no extant members (`:55`) — also what `-translate` requires (`:79`) |
| `../assets/files/des-CarnivoraFossilsSite-EXCERPT.txt` | yes, same, but read the header | `derived:` the same 9 rows plus a `site` column; the real `CarnivoraFossilsSite.txt` is linked (`:43`) but its contents are printed nowhere |
| `../assets/files/des-sealevel-EXCERPT.txt` | as `-varD`/`-varE` directory content | covariate time series `age`/`sealevel` (`:240-246`); 0.008 Myr is missing from the printed rows, hence EXCERPT |
| `../assets/files/des-Body_mass_1-EXCERPT.txt` | as `-traitD`/`-traitE` file | continuous trait table in kg, pre-log-transform (`:293-299`) |
| `../assets/files/des-FamilyGenera-EXCERPT.txt` | as `-catD`/`-catE` file | numerically coded categorical trait (`:319-325`) |
| `../assets/files/des-input_generation_commands.txt` | yes, from the PyRate root | all 4 documented `-fossil`/`-recent` commands (`:63`, `:89`, `:93`, `:143`) with line numbers; includes the `-data_in_area` example that omits its own flag |
| `../assets/files/des-analysis_commands.txt` | yes, from the PyRate root | all 17 documented `-d` analysis/`-sum`/`-plot` commands, byte-identical to `:186`-`:382` — the complete DES command surface |
| `../assets/files/des-example2_speciesgeocodeR.R` | no as-is: `...`-elided paths in the source | route 2 classification with `SpGeoCod()`, `occ.thresh <- 0.1`, `write.table` of `foss.txt`/`pres.txt` (`:105-134`) |
| `../assets/files/des-wiki-example2_DESin.R` | no as-is (same elided paths) | the *wiki's* version of route 2, which instead calls `DESin()`/`write.DES.in()` (`des-model.md`:43-75) — keep beside the tutorial version to see the route conflict |
| `../assets/files/des-wiki-example1_DESin.R` | no: needs `DES_input_preparation.R` from the PyRate home directory | route 1b in R: `source(DES_input_preparation.R)`, `DESin(bin.size = 2, reps = 3)`, `summary()`, `plot()`, `write.DES.in()` (`des-model.md`:20-33) |
| `../assets/files/des-example3_sim_DES.R` | yes once `devtools` + `thauffe/simDES` are installed | route 3: `sim_DES(Time = 25, Step = 0.01, BinSize = 0.25, Nspecies = 100, SimD = c(0.2, 0.1, 0.3, 0.15), SimE = c(0.1, 0.1, 0.05, 0.15), SimQ = c(0.5, 0.4, 0.7, 0.8), Qtimes = 5.3, Ncat = Inf, alpha = 1)` and `write.table(Sim[[1]], .../sim.txt, na = "NaN")` (`:152-169`) |
