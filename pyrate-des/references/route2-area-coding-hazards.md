# Route 2 (coordinates / area-coding): where the documented script drops rows

**This file is not a mirror.** It is suite-authored analysis, and it is the detail layer for the
route-2 hazard rows in `SKILL.md` (sections *Input data preparation*, *Pitfalls*, *Not documented
in this wiki*). Every claim below carries a citation of the form `references/<file>.md:LINE` into
the four mirrors this skill carries, every double-quoted span is byte-identical to the mirror at
that line, and everything the corpus does not say is marked **inferred** (a reading of the printed
code) or **undocumented** (the corpus is silent). Line numbers are of the local mirrors, frontmatter
included; the `-cn` twins are one line lower than the English everywhere on these pages, and each
CN line number is given so the trace can be re-checked in either language.

Route 2 is the coordinate route: `references/tutorial-5.md`:105-134 (R) then `:143` (`PyRateDES.py
-fossil/-recent`), and the wiki page's variant at `references/des-model.md`:43-75, which ends in R
`DESin()`/`write.DES.in()` instead. Both print the same area-coding block, and it is the only place
in this corpus where DES input rows are produced by code that can silently remove them.

## 1. The two area-coding rules, side by side

| Side | What the printed code does | Threshold applied | Lines (EN wiki / EN tutorial / CN twins) |
| --- | --- | --- | --- |
| Fossils | every occurrence row gets exactly one area: the value of `fos.class$sample_table$homepolygon`, pasted into a new `higherGeography` column of the fossil table | **none** | `references/des-model.md`:51 / `references/tutorial-5.md`:113 / `references/des-model-cn.md`:52 / `references/tutorial-5-cn.md`:114 |
| Fossils | the joined table is then subset to its complete cases: `foss <- foss[complete.cases(foss),]` | n/a (this *is* the filter) | `references/des-model.md`:52 / `references/tutorial-5.md`:114 / `references/des-model-cn.md`:53 / `references/tutorial-5-cn.md`:115 |
| Recent | proportional occupancy per area is computed, then a cell is turned into an area name **only** if it clears `occ.thresh`, and finally only rows whose `higherGeography` is an area name are kept | **0.1**, and only here | `references/des-model.md`:60-65 / `references/tutorial-5.md`:123-128 / `references/des-model-cn.md`:61-66 / `references/tutorial-5-cn.md`:124-129 |

The threshold and its comment are one line, and the comment is the corpus's only prose about it:

```r
occ.thresh <- 0.1 #at least 10% occurrence in an area required
```

`references/des-model.md`:46 (CN `references/des-model-cn.md`:47) and `references/tutorial-5.md`:107
(CN `references/tutorial-5-cn.md`:108). The name says "recent" and so does the next comment in both
mirrors — `#Assign the recent coordinates to operational areas, using the occurrence threshold`
(`references/des-model.md`:54, `references/tutorial-5.md`:116) — so `occ.thresh` governs the recent
table alone; the word never appears again in either file.

## 2. Fossil side, line by line: what survives

```r
fos <- read.table("Example_data/Example_2_coordinates.txt", sep = "\t", header = T)
fos.class <- SpGeoCod("Example_data/Example_2_coordinates.txt", "Example_data/Example_regions.shp", areanames = "Region")
foss <- data.frame(fos, higherGeography = fos.class$sample_table$homepolygon)
foss <- foss[complete.cases(foss),]
```

(`references/des-model.md`:49-52, verbatim; the tutorial's equivalent is `references/tutorial-5.md`:110-114.)

* **One area per occurrence, no threshold.** `data.frame(fos, higherGeography = ...)` attaches a
  single value per row (`references/des-model.md`:51), so a fossil occurrence that straddles two
  areas, or whose record cannot be matched one-to-one to `sample_table` rows, is not given two rows
  and is not asked what fraction of it lies where. **inferred:** that a point outside every polygon
  yields an empty `homepolygon` value is R/`speciesgeocodeR` semantics, not a corpus statement; the
  corpus never prints `sample_table`, never defines `homepolygon` and never describes what
  `SpGeoCod()` returns for an unmatched point.
* **The subset drops rows, silently.** `complete.cases(foss)` is called on the **whole joined
  frame**, not on the new column (`references/des-model.md`:52), so a row is dropped for an empty
  value in *any* column of `fos` too — a missing `latestAge` loses the row even if the occurrence
  sits inside a polygon. **inferred:** R's `data.frame()` also removes an entirely empty `higherGeography`
  column before `complete.cases` ever sees it, in which case the subset removes nothing and the
  output table has no area column at all. Which of the two happens depends on `SpGeoCod()`'s return,
  which nothing in this corpus documents.
* **No count is printed.** Nothing between `read.table` (`references/des-model.md`:49) and
  `write.table`/`DESin()` (`references/des-model.md`:52 → `:68`) reports how many rows the subset
  removed, in either mirror.

## 3. Recent side, line by line: what survives

```r
pres <- round(rec.class$spec_table[, 2:3] / rowSums(rec.class$spec_table[, 2:3]), 2)
pres[which(pres[, 1] >= occ.thresh ), 1] <- names(pres)[1] 
pres[which(pres[, 2] >= occ.thresh ), 2] <- names(pres)[2] 
pres <- data.frame(scientificName = rep(rec.class$spec_table[, 1], 2),
                   higherGeography = c(pres[, 1], pres[, 2]))
pres <- pres[pres$higherGeography %in% names(rec.class$spec_table), ]
```

(`references/des-model.md`:60-65 verbatim; tutorial equivalent `references/tutorial-5.md`:123-128.)

* Each cell that **passes** is overwritten with the area name taken from the column header
  (`names(pres)[1]`, `names(pres)[2]`); a cell that **fails** keeps its rounded proportion
  (`references/des-model.md`:61-62`).
* The last line keeps only cells that are area names
  (`references/des-model.md`:65`pres <- pres[pres$higherGeography %in% names(rec.class$spec_table), ]`),
  i.e. it throws away every failing cell's residue. So a taxon whose largest occupancy is below 0.1
  ends up with **zero recent rows**; a taxon at 0.55/0.45 keeps one row, not two.
* The test is `>=`, so exactly 0.10 passes — that is visible in the operators printed at
  `references/des-model.md`:61-62, but the corpus nowhere states that this boundary was chosen
  deliberately (**undocumented**).
* The recent table is required to cover *every* taxon: "The two text files needed are: 1) a table
  with the fossil occurrences 2) a table with the recent distribution of all taxa"
  (`references/tutorial-5.md`:25; the wiki page words it "The data needed are: 1) a table with the
  fossil occurrences 2) a table with the recent distribution of all taxa",
  `references/des-model.md`:11). Route 2's own subsetting can leave that requirement unmet without
  anyone noticing.

## 4. What each side of the asymmetry costs you

| Loss the code produces | Downstream consequence | Status of the consequence |
| --- | --- | --- |
| A fossil row whose point fell outside every polygon (or whose other columns were empty) disappears from `foss` | that occurrence contributes to no time bin, so a taxon's range shortens or its first/last appearance moves | **inferred** from `references/des-model.md`:52 — the corpus never says what PyRateDES does with the rows it is handed |
| A taxon whose *every* fossil row is dropped | it is absent from the `-fossil` table at all (`references/tutorial-5.md`:143 passes `foss.txt` to `-fossil`), i.e. it silently leaves the analysis | **inferred** |
| A taxon whose recent occupancy is under 0.1 in both areas | it gets no recent row, so its present range in both areas is empty; and a present range is what distinguishes a living representative from an extinct one — "PyRateDES works for groups of taxa without any living representative. In this case the file with the recent distribution should contain only the header of scientificName and higherGeography" (`references/tutorial-5.md`:55) | the `:55` sentence is verbatim corpus; the step "therefore a taxon missing from `-recent` is coded as not extant" is **inferred** — no mirror states the rule, and nothing documents what `PyRateDES.py` does when a name is in the fossil table but not in the recent table (**undocumented**) |
| More absent-present codings than the data supports | local extinction is estimated from present-range absence; DES estimates "rates of local extinction within areas" (`../pyrate/references/home.md`:54) | the model's aim is corpus text; "this inflates local extinction" is the critic's claim and this suite cannot source it — treat as **inferred, unverified** |
| A taxon whose recent rows were cut to one area while its fossils are in the other | its only area record is fossil-side, which is what `-data_in_area 1` is for — "`-data_in_area 1` is an argument to code fossil occurrences for a DES analysis where lineages are only known from a single area" (`references/tutorial-5.md`:93) | the flag exists for hand-built single-area data; whether it is a remedy for rows route 2 deleted is **undocumented** |

Two further asymmetries in the same block, both visible in the printed code:

* `pres <- round(rec.class$spec_table[, 2:3] / ...)` takes **columns 2 and 3** — the block assumes
  `spec_table` is exactly `name + two areas` (`references/des-model.md`:60), i.e. exactly the two
  areas DES is specified for (`references/tutorial-5.md`:23 "classified into time-bins and two
  discrete and predefined areas"). A third area silently contributes nothing rather than failing.
* The `scientificName` column is rebuilt as `rep(rec.class$spec_table[, 1], 2)`
  (`references/des-model.md`:63), i.e. the name list is duplicated to match the two candidate-row
  blocks. If `spec_table`'s row order does not match the order `sample_table` was built in, the
  fossil side (matched through `fos` by `data.frame` position, `references/des-model.md`:51) and the
  recent side (matched through `spec_table` position) are keyed differently — nothing in the corpus
  documents that `SpGeoCod()` keeps row order (**undocumented**).

## 5. The sanity check the wiki page runs, and what to add to it

Both wiki examples end by looking at the object before writing it, under a comment that names the
purpose:

```r
#explore the data for potential biases
summary(exp1)
par(ask = T)
plot(exp1)
```

(`references/des-model.md`:27-30; the example-2 twin is `#explore data` + `summary(exp2)` +
`plot(exp2)` at `references/des-model.md`:71-75; CN twins `references/des-model-cn.md`:28-31 and
`:72-76`.) So the documentation's own R route contains a bias check on the generated object, and it
is the only pre-run check anywhere on these two pages: the tutorial's route 2 prints **no**
`summary()`/`plot()` at all (its block ends at `write.table` of `foss.txt`/`pres.txt`,
`references/tutorial-5.md`:131-134) and its only look at the data is the post-generation
`-plot_raw` figure of "the observed diversity trajectories and their 95% credible interval in the
two area" (`references/tutorial-5.md`:95).

Because `summary()`/`plot()` are called on the *post-subset* object, they show you the reconstruction
after the deletions, not the deletions themselves. Add the two comparisons the printed script omits
(`derived:` this is this suite's own addition, not documentation):

```r
# count what each subsetting step removed
nrow(fos); nrow(foss)                                  # rows lost to complete.cases()
setdiff(unique(fos$scientificName), unique(foss$scientificName))   # taxa with no surviving fossil row
table(foss$higherGeography, useNA = "ifany")            # which area the survivors sit in
setdiff(unique(as.character(rec.class$spec_table[, 1])),
        unique(as.character(pres$scientificName)))      # taxa that fell under occ.thresh
```

If any of those four lines is non-trivial, route 2 has just cost you data; fix the polygons, lower
`occ.thresh` deliberately, or code the areas yourself and use route 1
(`references/tutorial-5.md`:63), which applies no filter you cannot see.

## 6. Paths: the directory the printed R code uses is not the directory the page links

Every file the wiki page's code opens lives in a directory named **nowhere else in the corpus**:

* `Example_data/` appears 9 times on 6 lines of `references/des-model.md` (`:24` twice, `:33`, `:49`,
  `:50` twice, `:55`, `:57`), e.g.
  `references/des-model.md`:24 `exp1 <- DESin("Example_data/Example_1_minimum_data.txt", "Example_data/Example_1_recent_distributions.txt", `
  and `references/des-model.md`:33 `write.DES.in(exp1, file = "Example_data/Example1_DES_in")`.
* The same page's prose links those exact files under a different directory:
  `https://github.com/dsilvestro/PyRate/blob/master/example_files/DES_input_data/Example_1_minimum_data.txt`
  and `https://github.com/dsilvestro/PyRate/tree/master/example_files/DES_input_data`, both printed on
  `references/des-model.md`:15, together with "Example input and output files can be found [here]" in
  the same sentence.
* So as printed, all six example calls on that page open a path no reader has. **inferred:** that
  `Example_data/` should read `example_files/DES_input_data/` is a reading of the page's own links;
  the page never says it, and no corpus file lists an `Example_data` directory.
* The tutorial's route 2 was corrected to real paths **except** for one line, which still carries the
  wiki's literal: `references/tutorial-5.md`:117
  `rec <- read.table("Example_data/Example_2_recent_coordinates.txt", sep = "\t", header = TRUE)`
  (CN `references/tutorial-5-cn.md`:118) while the two lines above it use
  `".../PyRate/example_files/DES_examples/DES_input_data/..."` (`references/tutorial-5.md`:110-112`).
  The recent-coordinate file is therefore opened from a different place than the shapefile it is
  classified against, and written output goes to `.../DES_examples/DES_input_data/pres.txt`
  (`references/tutorial-5.md`:133).
* The tutorial's own directory names, for the record: route 1 input and output
  `./example_files/DES_examples/Carnivora` (`references/tutorial-5.md`:29 links, `:63` runs), route 2
  in- and output `./example_files/DES_examples/DES_input_data` (`:110-112`, `:131`, `:133`, and `-wd
  ./example_files/DES_examples` at `:143`), route 3 `.../DES_examples/DES_input_data/sim.txt`
  (`:168`). **Not one of them is ever printed as a plain, unquoted directory path**: the R calls wrap
  them in quotes and the `-d` examples pass the *generated* replicate file
  (`./example_files/DES_examples/Carnivora/Carnivora_1.txt`, `references/tutorial-5.md`:186), so a
  reader cannot recover the layout from any `ls` the docs print.
* `references/tutorial-5.md`:119 has a second, worse path bug:
  `rec.class <- SpGeoCod(".../PyRate/example_files/DES_examples/DES_input_dataExample_2_recent_coordinates.txt",`
  — the `/` between the directory and the file name is missing, so the path names a file called
  `DES_input_dataExample_2_recent_coordinates.txt` inside `DES_input_data`. The `-cn` twin prints the
  same string at `references/tutorial-5-cn.md`:120, i.e. it is upstream, not a translation artifact.
* This suite mirrors the two **pages**, not the data: `../assets/files/` holds 13 `des-` fixtures and
  no `Example_2_coordinates.txt`, `Example_2_recent_coordinates.txt`,
  `Example_1_minimum_data.txt` or `Example_regions.shp`. Check from this skill directory:
  `ls ../assets/files | grep -ci "Example_"` → `0`.

## 7. Numbers the corpus never pins down for `PyRateDES.py` (`-p`, `-b`, chain lengths)

The sentence that introduces the three chain options spells two roles, not three:

> "We can (and in the cases of more complex models with time-variable rates we should) change the
> number of MCMC iterations and the sampling frequency. By default PyRateDES will run 100,000
> iterations and sample and print the parameters every 100 iterations. Depending on the size of the
> data set you may have to increase the number iterations to reach convergence (in which case it
> might be a good idea to sample the chain less frequently to reduce the size of the output files).
> This is done using the commands `-n`, `-s`, and `-p`"

(`references/tutorial-5.md`:191, CN `references/tutorial-5-cn.md`:192.) The same sentence is the only
place `-p` occurs in the English mirror; it names three flags for two quantities, and never says which
flag sets what. Everything the corpus actually prints for these four options:

| Option | Values printed, with lines | What the docs state about it |
| --- | --- | --- |
| `-n` | `500000` (`:194`), `1000001` (`:226`, `:361`, `:382`) | the page gives no default *value* for `-n`, only the sentence "will run 100,000 iterations" (`:191`). The core program's list puts `-n 10000000` "(default)" (`../pyrate-command-reference/references/command-list.md`:56-58) — a different program; do not paste it into a DES command as a DES default |
| `-s` | `1000` (`:194`, `:226`, `:361`, `:382`), `10000` (`:194`) | "sample and print the parameters every 100 iterations" by default (`:191`) — **inferred** that `-s` is that 100, from "sample ... every 100 iterations" plus "This is done using the commands `-n`, `-s`, and `-p`" |
| `-p` | `10000` (`:194`), `1000` (`:226`, `:361`, `:382`) | **no role is stated for this program.** The only two `-p` explanations anywhere in the suite's mirrors are for other programs: "MCMC print-on-screen frequency." with "Example: `-p 1000`" for `PyRate.py` (`../pyrate-command-reference/references/command-list.md`:64-66) and, for a `PyRate.py` BDNN run, "while `-p` sets the frequency of prints on your screen" (`../pyrate-bdnn/references/tutorial-bdnn.md`:232). Neither mirror says PyRateDES behaves the same |
| `-b` | `1000` (`:341`, with `-sum`), `200` (`:349` and `:368`, with `-plot`) | unit stated **only** in the `-sum` paragraph, in generations: "the flag `-b` specifies the burnin (default 0; e.g. 1000 for the first 1000 MCMC generations)" (`:338`). The `-plot` lines (`:349`, `:368`) carry `-b 200` and the text that introduces `-plot` (`:346`) says nothing about `-b` |

Practical rules that follow, none of which needs a guess:

* Do not write "`-p` = print frequency" as documentation for `PyRateDES.py`. The DES page never says
  what `-p` does; the reading comes from `command-list.md`:64-66 (`PyRate.py`) and
  `tutorial-bdnn.md`:232 (also `PyRate.py`). Quote it as a cross-program inference or not at all.
* Neither `-p` value DES prints is a default: `10000` sits on `-n 500000` (`:194`) and `1000` sits on
  `-n 1000001` (`:226`, `:361`, `:382`), and the only default the page states for the chain is 100,000
  iterations sampled every 100 (`:191`).
* Do not reuse `-b 200` (a `-plot` line, `:349` and `:368`) as a summary burn-in, and do not call
  `-b 1000` (`:341`) a default — the printed DES default is 0 (`:338`).
* `-b`'s unit is **contested across this corpus**, and DES only settles one half of it. DES's `-sum`
  sentence counts generations ("e.g. 1000 for the first 1000 MCMC generations", `:338`), while the
  core command list defines the same option both ways in one entry — "Set the number of iterations to
  be discarded (i.e. not logged) from the analysis as burnin" (`../pyrate-command-reference/references/command-list.md`:69)
  and then "first 1,000 samples are discarded" / "the first 10% of the samples are discarded"
  (`:71-73`, so `-b` also accepts a fraction there, which no DES line does) — and the sibling route's
  **plot** sentence, the exact analogue of DES's `-plot ... -b 200`, counts samples: "The command
  `-b 200` specifies that the first 200 samples are discarded as burnin"
  (`../pyrate-continuous-covariates/references/tutorial-2.md`:124). So the unit of `-b 200` on a DES
  `-plot` line is **undocumented**: on the generations reading it discards 200 of a chain logged every
  1000 iterations (`:191`, `:349`), i.e. effectively nothing, and on the samples reading it discards
  200 of the logged samples. Say which you mean instead of assuming.
* `-ncat` is the one rate-model number DES does pin down: "The default of four categories (`-ncat 4`)
  is usually sufficient to account for heterogeneity across lineages" (`:213`).

## 8. One-line summary for the SKILL.md hazard table

Route 2 pins each fossil occurrence to one area with no threshold and then keeps only complete cases
(`references/des-model.md`:51-52), while it keeps a recent cell only above `occ.thresh` = 0.1
(`references/des-model.md`:46, `:61-62`, `:65`); both deletions are silent, and neither page prints a
count before and after. The wiki page's own `summary()`/`plot()` (`references/des-model.md`:27-30`)
run after the deletions, so they cannot show you what was lost.
