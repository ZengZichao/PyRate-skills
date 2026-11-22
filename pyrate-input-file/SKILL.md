---
name: pyrate-input-file
description: "Build, read and check the input a PyRate run needs: the tab-delimited fossil occurrence table (header row, one row per occurrence; the four mandatory columns species name/Status extinct-or-extant/MinT/MaxT; optional Trait column, missing data NA; optional Site column, coeval occurrences sharing one randomised age), the R generators extract.ages and extract.ages.pbdb in pyrate_utilities.r with their replicates, cutoff, random, extant_species options, the PBDB download settings (Show accepted names only, uncheck Include metadata), the two generated files *_PyRate.py (Numpy arrays, one per replicate) and *_SpeciesList.txt, the -j replicate selector, and the pre-flight commands -data_info and -check_names (Genus_species format, ranks 0-3, no synonym check). Covers the all-occurrences rule, the missing-data hard stop, cutoff as silent row deletion, the header-name and cutoff-boundary conflicts. Fixtures ../assets/files/occ-*; checker ../pyrate-input-file/scripts/validate_input.py --expect trait|site|none."
---

# From fossil occurrences to a PyRate-runnable input file

## Overview

PyRate estimates speciation, extinction and preservation rates from fossil occurrences, and it never reads a
raw occurrence table: the table is converted first, by `extract.ages` or `extract.ages.pbdb` in the R script
`pyrate_utilities.r`, into a Python input file (`references/preparing-input-file.md` 9, 26, 31;
`references/tutorial-1.md` 37, 68). The whole chain this skill owns is:

```
occurrence table (.txt, tab-delimited)  ──extract.ages()──────────┐
PBDB .csv download ──extract.ages.pbdb()──► *_PyRate.py  ──► python PyRate.py <file> -data_info
                                          └► *_SpeciesList.txt ──► python PyRate.py -check_names <file>
```

"The PyRate program requires a specific format for the input data, so please follow the next steps
carefully" (`references/preparing-input-file.md` 9). The riskiest assumption this skill removes by checking
it instead of trusting it: **the four mandatory columns tolerate no gaps at all** — "At present, PyRate can
not deal with missing information in these four columns, so make sure that you remove these entries
beforehand" (`references/preparing-input-file.md` 14) — while the *optional* trait column is the only place
where "missing data are allowed, and should be given as  NA" (same line, the double space is the doc's). The
second-largest assumption an agent gets wrong here is the column naming: the two pages this skill is built
from print **different header rows** for the same table (see the conflict section below), so a fix on
`MinT`/`MaxT` is not evidence about `MinAge`/`MaxAge`.
**Underneath both is the page's scope demand, stated once and never re-enforced downstream:** "All fossil occurrences need to be provided in a table (a tab-delimited text file)" — completeness of the *occurrence set*, not just of the four cells (`references/preparing-input-file.md` 14).
The cascade that demand starts, and the re-count that closes it: `references/cutoff-and-completeness.md` §1-§4.

Runtime context (owned by other skills, needed to run anything below): PyRate is invoked as
`python PyRate.py path_to_input_file/file_name.py [commands]` (`../pyrate/references/home.md` 75-80) under
Python 2.6-2.7, "Please note that Python 3.x is currently not supported"
(`../pyrate/references/home.md` 69); `../pyrate-installation/references/virtual-environment.md` 54 gives
Python 3.x PATH advice, which contradicts it — that conflict is documented in `pyrate-installation`.

## The eight things that break a run

| # | What happens | Consequence | Wiki wording (mirror line) |
| --- | --- | --- | --- |
| 1 | A blank/NA in species name, Status, MinT or MaxT | Nothing to convert: the four columns "can not" carry missing information; entries must be removed before the R step | `preparing-input-file.md` 14 |
| 2 | One row per species instead of one row per occurrence, or no header row | The table is defined as "The table should have a header (first row) and **one row for each fossil occurrence**" — collapsing occurrences changes the data the model sees | `tutorial-1.md` 49 |
| 3 | Status spelled other than `extinct` / `extant`, **or the same species given `extant` in one row and `extinct` in another** | Those two strings are the documented vocabulary ("their status (\"extant\" or \"extinct\")"); **no page says what another spelling does** — see §Verified (upstream accepts it and silently treats anything that is not `extant` as extinct). The mixed-status case is the opposite failure and it comes early and loudly: the R conversion hard-stops with `at least one species is listed as both extinct and extant` (§Verified, the row headed `one species both extant and extinct`) — a **not documented** behaviour, so expect no guidance page to mention the message; then cross-check the mark you actually shipped against `-data_info`, which prints `number of extant taxa` (`../pyrate-summarize-results/references/summarize-results.md` 10; `references/tutorial-1.md` 45) | `preparing-input-file.md` 14; `tutorial-1.md` 49 |
| 4 | Trusting one reading of `cutoff` | The wiki excludes a range "of 5 Myr or higher", the tutorial "remove occurrences with an age range greater than" the threshold — an occurrence exactly at the cutoff is excluded on one page and kept on the other | `preparing-input-file.md` 42 vs `tutorial-1.md` 38 |
| 5 | PBDB download left with metadata rows or non-accepted names, then fed to `extract.ages.pbdb` | The function "does not check for synonyms, typos, etc." — bad names go straight into the input file | `tutorial-1.md` 26, 38 |
| 6 | Trait column filled with blanks instead of `NA` | Only `NA` is the documented missing-value marker for that column | `preparing-input-file.md` 14 |
| 7 | Inconsistent spellings of the same species across occurrences | A species split over two names is two lineages; `-check_names` finds spelling variants but "**NOTE that this algorithm does NOT check for synonyms!**" and the rest is manual | `tutorial-1.md` 94, 100, 101, 115 |
| 8 | A `cutoff` (or the no-missing-data rule) applied without re-counting | Both are deletions performed *before* PyRate exists: occurrences are "excluded from the data set" and entries are removed "beforehand", so a species that loses all its occurrences leaves the data set, the species list and the analysis, and diversity plus every rate then move with the threshold — no page states that consequence (`references/cutoff-and-completeness.md` §1, §3) | `preparing-input-file.md` 14, 40-42; `tutorial-1.md` 38, 40 |

## The mandatory occurrence table

A tab-delimited text file, header row first, one row per fossil occurrence (`preparing-input-file.md` 14;
`tutorial-1.md` 49). The corpus prints two header rows for this same table — both are reproduced here
because which one you meet depends on which page you landed on:

| # | Wiki page header | Tutorial 1 header | Content | Missing allowed? |
| --- | --- | --- | --- | --- |
| 1 | `Species` (`preparing-input-file.md` 16) | `Taxon\_name` (`tutorial-1.md` 52); prose: "1) Taxon name" (`tutorial-1.md` 49) | species/binomial of the occurrence, expected `Genus_species` for `-check_names` (`tutorial-1.md` 94) | no |
| 2 | `Status` (`preparing-input-file.md` 16) | `Status` (`tutorial-1.md` 52) | `"extant"` or `"extinct"` (`preparing-input-file.md` 14; `tutorial-1.md` 49) | no |
| 3 | `MinT` (`preparing-input-file.md` 16) | `MinAge` (`tutorial-1.md` 52) | minimum age of the occurrence | no |
| 4 | `MaxT` (`preparing-input-file.md` 16) | `MaxAge` (`tutorial-1.md` 52) | maximum age of the occurrence | no |
| 5 | `Trait` (`preparing-input-file.md` 16) | not named; "One additional column can be included in the table indicating a trait value (e.g. estimated body mass) that can be used PyRate analyses." (`tutorial-1.md` 49, the missing "in" is the doc's) | one trait value per occurrence | **yes — `NA`** (`preparing-input-file.md` 14) |
| 6 / 5 | — (absent from the wiki page) | `Site` (`tutorial-1.md` 75) | "a number specifying the ID of the assemblage for each occurrence" (`tutorial-1.md` 72) | not stated |

The exact example tables the docs print (they are the only format spec in the corpus). The first block is
character-for-character the mirror text except that the mirror ends every one of those rows with the docs'
two-space markdown line break, trimmed here; the second block is the tutorial's two tables set out side by
side (row content unchanged, the markdown separator rows of mirror 53 and 76 dropped):

```text
# references/preparing-input-file.md 16-24 (the wiki's "A typical input file may look like this:")
`Species				Status	MinT	 MaxT    Trait`
`Ursus_etruscus			extinct	 1.9	  2.6		 90  `
`Ursus_etruscus			extinct	 1.2	  1.8		 90  `
`Ursus_etruscus			extinct	 2.6	  3.4		 90  `
`Agriotherium_insigne		extinct	 4.2	  5.3		285  `
`Ursavus_brevirhinus		extinct	 8.2	  9.0		 80  `
`Ursavus_brevirhinus		extinct	11.2	 15.2		 80  `
`Agriotherium_intermedium	extinct	 3.4	  4.2		 NA  `
`...					...		 ...	  ...		...	`
```

```text
# references/tutorial-1.md 52-63 (option 2 step 1) and 75-85 (the Site variant)
| Taxon\_name   | Status  | MinAge | MaxAge |        | Taxon\_name   | Status  | MinAge | MaxAge | Site
Canis\_ferox | extinct | 4.9    | 10.3             Canis\_ferox | extinct | 4.9    | 10.3 | 1
Canis\_lepophagus | extinct | 4.9 | 10.3           Canis\_lepophagus | extinct | 4.9 | 10.3  | 1
Canis\_ferox | extinct | 4.9 | 10.3               Canis\_ferox | extinct | 4.9 | 10.3  | 2
Canis\_ferox | extinct | 4.9 | 10.3               Canis\_ferox | extinct | 4.9 | 5.3  | 3
Canis\_ferox | extinct | 4.9 | 10.3               Canis\_edwardii | extinct | 0.3 | 4.9  | 4
Canis\_edwardii | extinct | 0.3 | 4.9             Canis\_armbrusteri | extinct | 0.3 | 4.9 | 4
Canis\_armbrusteri | extinct | 0.3 | 4.9          Canis\_latrans | extant | 0.3 | 4.9  | 4
Canis\_latrans | extant | 0.3 | 4.9               Canis\_latrans | extant | 1.8 | 4.9  | 5
Canis\_latrans | extant | 1.8 | 4.9               Canis\_thooides | extinct | 1.8 | 4.9  | 5
Canis\_thooides | extinct | 1.8 | 4.9
```

Tab-delimited, tab-padded, one row per occurrence; `Agriotherium_intermedium` carries `NA` in the trait
column and nothing else does; `Canis_latrans` appears twice, once with `0.3` and once with `1.8`, both
`extant`. The `...` row (`preparing-input-file.md` 24) is the doc's own truncation marker — the wiki prints
7 of the occurrences of an Ursidae data set, not a complete file.

## Which column names are correct? (unresolved conflict in the corpus)

Both readings, stated as printed — do not normalise them silently:

- **Wiki reading** — `Species … Status MinT MaxT Trait`, and the prose names the same pair.
  `preparing-input-file.md` 14 gives "minimum and maximum ages as the columns".
  `preparing-input-file.md` 34 gives "re-drawing the ages of the occurrences at random from uniform distributions with boundaries MinT and MaxT".
  `preparing-input-file.md` 40 gives "with a wide temporal range between MinT and MaxT".
  CN twin identical, including the English header row: `preparing-input-file-cn.md` 15, 17, 35, 41.
- **Tutorial reading** — "The table must include 4 columns including 1) Taxon name, 2) Status specifying
  whether the taxon is \"extinct\" or \"extant\", 3) Minimum age, and 4) Maximum age." with the table header
  `Taxon\_name | Status | MinAge | MaxAge` (`tutorial-1.md` 49, 52, 75). CN twin identical, table
  untranslated: `tutorial-1-cn.md` 50, 53, 76.
- **What the header text is worth**: the only column name the corpus says is *significant* is `"Site"` —
  `extract.ages()` "will automatically resample fossil ages by site when a column named \"Site\" is included
  in the input table" (`tutorial-1.md` 87). Neither page says the other header strings are read at all; the
  wiki's `extract.ages` example points at `Ursidae.txt` without naming its header
  (`preparing-input-file.md` 52). Nothing in this corpus states that the four mandatory columns may be
  renamed, nor that they may not — see `Not documented in this wiki`.

Practical consequence: when you must guess nothing, keep a header row, keep the four columns in the printed
order (name, status, min, max), spell the optional 5th `Trait` **or** `Site` exactly as printed, and never
supply both (the corpus only ever describes a *single* additional column:
`preparing-input-file.md` 14 vs `tutorial-1.md` 72 — see §Verified outside this corpus for what the R
function actually does with six columns).

## What MinT / MaxT mean, and what `extract.ages` does with them

`preparing-input-file.md` 14: "The minimum and maximum ages commonly correspond to the temporal boundaries of the stage a particular fossil is assigned to and are generally available from the databases".
`tutorial-1.md` 49: "Min and max ages represent the age ranges of each fossil occurrence, typically based on stratigraphic boundaries". Neither page states the **unit** of those ages: the only unit appearing next to them
anywhere is Myr, and only inside the `cutoff` examples (`preparing-input-file.md` 42; `tutorial-1.md` 38),
while `marginal_rates.log` is described as rates "calculated within 1 time unit (typically Myr)"
(`tutorial-1.md` 201) — so Myr is the docs' working unit rather than a documented requirement (inference from
those three lines).

`extract.ages` collapses each `[MinT, MaxT]` interval to **one** age per occurrence and writes only ages to
the Python file: a draw "at random from uniform distributions with boundaries MinT and MaxT"
(`preparing-input-file.md` 34) when `random=TRUE`, or "the midpoint age" when `random=FALSE`
(`preparing-input-file.md` 45, 47). With a `Site` column the draw is made per site instead, so occurrences
from one assemblage stay coeval (`tutorial-1.md` 71-72, 87) — but read the example with care: the prose says
"the first three occurrences were found in the same site" while the table printed on the next lines gives those
three rows Site `1`, `1`, `2` (`tutorial-1.md` 72 vs 77-79, repeated in the CN twin at
`tutorial-1-cn.md` 73 vs 78-80), so the *rule* is documented and the *example* is self-inconsistent; do not
infer anything about site grouping from that row triple. Extant taxa: the input table marks them with
`extant` in Status (`preparing-input-file.md` 14) — how that mark becomes model input is documented only as
"this information must be provided when running a diversification rate analysis" (`tutorial-1.md` 33); the
separate `-N` flag (number of extant species regardless of occurrence data) lives in
`../pyrate-command-reference/references/command-list.md` 162-163.

## `extract.ages`: options, defaults, replicates

Load it first — `> source(file = "/path_to_file/pyrate_utilities.r")` (`preparing-input-file.md` 28; the
tutorial's variant is `source(".../PyRate-master/pyrate_utilities.r")`, `tutorial-1.md` 31, where `.../`
"here indicated as `.../` for simplicity", same line). The function "needs the path to the file containing
the raw data and has a few options that can be specified" (`preparing-input-file.md` 31).

| Option | Documented default | Documented effect | Citation |
| --- | --- | --- | --- |
| `file` | — (required) | "the path to the file containing the raw data" | `preparing-input-file.md` 31 |
| `replicates` | `replicates=1` "(default, generates 1 data set)" | several replicates of the data set in a single input file, each re-drawing ages | `preparing-input-file.md` 34-37; `tutorial-1.md` 38 ("by default set to 1") |
| `cutoff` | `cutoff=NULL` "(default; all occurrences are kept in the data set)" | threshold excluding occurrences with a wide MinT-MaxT range; `cutoff=5` → "all occurrences with a temporal range of 5 Myr or higher are excluded" — a **deletion from the data set**, made before PyRate exists, not a flag on the row; no page states what it costs (hazard 8, `references/cutoff-and-completeness.md` §3) | `preparing-input-file.md` 39-42; CN `preparing-input-file-cn.md` 41-43 ("达到或超过 5 Myr") |
| `random` | `random = TRUE` "(default)"; `random = FALSE` "(use midpoint ages)" | random age in `[MinT, MaxT]` vs midpoint; "Note that this option defaults to `TRUE` if several replicates are generated (i.e. replicates > 1)" | `preparing-input-file.md` 44-47; CN `preparing-input-file-cn.md` 46 |

The `replicates > 1` → random interaction is stated by both language versions (`preparing-input-file.md` 45;
`preparing-input-file-cn.md` 46 carries the same sentence in Chinese — it is a local translation, so the wording
is not "verbatim"). Read strictly, the doc only says `random` *defaults* to `TRUE` in that case and never says
an explicit `random=FALSE` is refused; the corpus leaves it there. The upstream script ignores an explicit
`random=FALSE` whenever `replicates > 1` (§Verified, reproduced here), so plan on midpoint + replicates being
unavailable. The tutorial's `cutoff` wording disagrees with the wiki's at the boundary (`tutorial-1.md` 38: "remove
occurrences with an age range greater than a given temporal range", then "will remove all occurrences in
which the difference between max age and min age is larwger than 10 Myr" — `larwger` is the doc's typo, kept
here; CN `tutorial-1-cn.md` 39 "大于 10 Myr").
Treat the boundary as unresolved and avoid data sitting exactly on the threshold.

One asymmetry worth knowing before you grep: the two pages name different option sets for the *same* function.
Tutorial 1 says only that `extract.ages` "includes `replicates` and `cutoff` options as the
`extract.ages.pbdb()` function described above (option 1)" (`tutorial-1.md` 68) — `random` is documented
exclusively on the wiki page (`preparing-input-file.md` 44-47), and `extant_species` exclusively in the
tutorial (`tutorial-1.md` 37). Neither page claims its list is exhaustive, so treat the union of the two as the
documented option set and nothing beyond it.

The two calls the docs print, transcribed exactly (the `#` tail of each line is this file's citation, not the
docs'):

```r
> extract.ages(file = "/path_to_file/Ursidae.txt", replicates=10, cutoff=5, random=TRUE)   # preparing-input-file.md 52
extract.ages(file="…/PyRate/example_files/Ursidae.txt", replicates=10)                     # tutorial-1.md 68
```

"This resamples 10 times the age of fossil occurrences randomly within the respective temporal ranges and
generates a Python file (here called 'Ursidae_PyRate.py')" (`preparing-input-file.md` 54). Note the second
line's path separator is U+2026 `…`, not three ASCII dots (same in the CN twin, `tutorial-1-cn.md` 69) — a
copy-paste trap.

### Replicates, `-j`, and why any of this is done

Replicates exist to carry age uncertainty into the rates. `preparing-input-file.md` 34: "combining the results of these replicates is a way to account for the uncertainty of the true ages of the fossil occurrences (see also Silvestro et al. 2014)".
`tutorial-1.md` 38: "These replicates can then be analyzed (individually) and the combined results will account for age uncertainties in the fossil record".
You pick one with `-j`: "**Ideally, we should analyze multiple randomized replicates and combine the results to
incorporate dating uncertainties** in our rate estimates. To specify the which replicate we want to analyze,
we use the flag `-j` followed by the replicate number" (`tutorial-1.md` 178 — the doubled "the which" is the
doc's), e.g. `python PyRate.py .../Canis_pbdb_data_PyRate.py -A 2 -mHPP -mG -j 1` (`tutorial-1.md` 180). `-j`
semantics, default and examples are owned by `pyrate-command-reference`
(`../pyrate-command-reference/references/command-list.md` 27-30); combining and ESS rules are owned by
`pyrate-summarize-results` (`../pyrate-summarize-results/references/summarize-results.md`, and
`references/tutorial-1.md` 206 for "the ESS values should be computed from the log files of each replicate").

## `extract.ages.pbdb`: the PBDB route (Tutorial 1, option 1)

| Step | What the doc demands | Citation |
| --- | --- | --- |
| 1 download | PBDB download generator `https://paleobiodb.org/classic/displayDownloadGenerator`, e.g. genus *Canis*, "save it as a cvs file" (the `cvs` typo is the doc's), e.g. *Canis_pbdb_data.csv*; **"check the box \"Show accepted names only\" in the \"Select by taxonomy\" section, and uncheck the box \"Include metadata at the beginning of the output\" in the \"Choose output options\" section"** | `tutorial-1.md` 26; CN `tutorial-1-cn.md` 27 |
| 2 R | open a terminal, type `R`, Enter (or R GUI / RStudio) | `tutorial-1.md` 28 |
| 3 load | `source(".../PyRate-master/pyrate_utilities.r")` | `tutorial-1.md` 31 |
| 4 extant vector | "**Check which species are extant today** (if any), as this information must be provided when running a diversification rate analysis. All species unless otherwise specified will be considered as extinct." → `extant_dogs = c("Canis rufus","Canis lupus","Canis aureus","Canis latrans","Canis mesomelas","Canis anthus","Pseudalopex gymnocercus","Canis adustus","Canis familiaris")` | `tutorial-1.md` 33-34; CN `tutorial-1-cn.md` 34-35 |
| 5 generate | `extract.ages.pbdb(file= ".../Canis_pbdb_data.csv",extant_species=extant_dogs)`; "**IMPORTANT NOTE:** this function does not check for synonyms, typos, etc."; then "You can specify two additional options": `replicates` (default 1) and `cutoff` | `tutorial-1.md` 36-38; CN `tutorial-1-cn.md` 38-39 |
| 6 check | see next section (`-data_info`) | `tutorial-1.md` 40-45 |

Two hazards unique to this route. (a) The `extant_species` vector is written with **spaces**
(`"Canis rufus"`, `tutorial-1.md` 34) while the occurrence tables and the `-check_names` format use the
underscored `Genus_species` form (`tutorial-1.md` 52-63, 94); nowhere do the two pages state which form must
match, nor what happens to a name that does not match — §Verified has the answer from the script itself: the
match is made against PBDB's `accepted_name` column **before** underscores are inserted, and a name that fails
to match is silently recorded as `extinct`. (b) `random` is documented for `extract.ages` but never offered for
`extract.ages.pbdb` — the tutorial says "You can specify two additional options"
(`tutorial-1.md` 38; CN `tutorial-1-cn.md` 39 "此外还可以指定两个选项"), and `random` is absent, so its behaviour
there is undocumented; §Verified records that the upstream function does take a `random` argument and passes it
straight to `extract.ages`, i.e. the doc under-states the interface.

## The two generated files, and what the `.py` really is

"The previous step generated two files: a text file (\*\_SpeciesList.txt) containing the list of all species
included in the dataset and a python file (\*\_PyRate.py) with all occurrences formatted for a PyRate
analysis" (`tutorial-1.md` 40; CN `tutorial-1-cn.md` 41).

| File | Documented content | What is *not* documented | Citation |
| --- | --- | --- | --- |
| `*_PyRate.py` | "all occurrences formatted for a PyRate analysis"; a Python file "with the fossil occurrence data (as list of Numpy arrays) and, optionally, one or more continuous traits" | the variable names, array shapes, how many arrays per replicate, how `replicates=10` appears inside the file | `tutorial-1.md` 40; `../pyrate-command-reference/references/command-list.md` 13 |
| `*_SpeciesList.txt` | "the list of all species included in the dataset"; usable directly as the `-check_names` input, which "requires a text file containing one species name for each row" | whether it has a header, one row per species or per occurrence, whether it repeats names | `tutorial-1.md` 40, 94 |

The name of the second file is not stable even inside one page: the `-check_names` example command reads
`.../PBDB_dataset_TaxonList.txt` (`tutorial-1.md` 98) — `_TaxonList`, not `_SpeciesList`. See
§Verified outside this corpus for the file the function actually writes (it is `<base>_TaxonList.txt`, which
matches the tutorial's *command* example and not its *prose*), and for the real layout of the `*_PyRate.py`
body, which no page prints.

Pre-flight inspection of the input, as the tutorial prescribes ("We can check the python file directly in
PyRate to get a few summary statistics", `tutorial-1.md` 40):

```sh
cd ".../PyRate-master"                                        # tutorial-1.md 43
python PyRate.py '.../Canis_pbdb_data_PyRate.py' -data_info    # tutorial-1.md 45
```

`-data_info` "will plot on screen a few summary statistics about a fossil data set (PyRate input file):
number of species, number of species excluded as singletons" plus "number of extant taxa, number of
occurrences, observed time span of the data set"
(`../pyrate-summarize-results/references/summarize-results.md` 9-10); the singleton exclusion itself is
`../pyrate-command-reference/references/command-list.md` 37-42 (`pyrate-command-reference`).

## `-check_names`: spelling audit of the taxon list

| Item | Documented value | Citation |
| --- | --- | --- |
| Purpose | "an algorithm to check for inconsistent spelling in species names (expected format: *Genus\_species*) as these can occur frequently especially in large datasets and hamper the accuracy of the analysis" | `tutorial-1.md` 94 |
| Input | "requires a text file containing one species name for each row"; can use the generated `*_SpeciesList.txt` directly | `tutorial-1.md` 94 |
| Command | `python PyRate.py  -check_names .../PBDB_dataset_TaxonList.txt` (flag **before** the file — unlike `-data_info`, where the file comes first) | `tutorial-1.md` 98 |
| Output | "a table saved in a text file with plausible typos", three columns `taxon1`, `taxon2`, `rank` | `tutorial-1.md` 100, 105-113 |
| Rank semantics | "Ranks 0 and 1 indicate the most likely cases of misspellings, whereas ranks 2 and 3 are most likely truly different names." | `tutorial-1.md` 100; CN `tutorial-1-cn.md` 101 |
| Limits | "**NOTE that this algorithm does NOT check for synonyms!**" and "It is up to the researcher to double check these possible inconsistencies and fix the names in their dataset accordingly." | `tutorial-1.md` 101, 115 |

The example output the doc prints (all rows it shows; note that **no rank 3 row appears** even though rank 3
is defined at `tutorial-1.md` 100): `Adocus_parvus/Adocus_pravus/0`, `Testudo_annae/Testudo_nanus/0`,
`Trionyx_pliocaenicus/Trionyx_pliocenicus/0`, `Testudo_aralensis/Testudo_tarakliensis/1`,
`Cyclanorbis_turkanensis/Cyclanorbis_urahensis/2`, `Geochelone_eocaenica/Neochelys_eocaenica/2`,
`Megalochelys_sivalensis/Melanochelys_sivalensis/2` (`tutorial-1.md` 107-113). Fixture
`../assets/files/occ-check-names-output-EXAMPLE.txt` is that table as tab-delimited text. The corpus stops at
rank 3 in prose and at rank 2 in its example; §Verified notes that the upstream example scores file
(`example_species_list_scores.txt`, which pairs with the species list excerpted as a fixture below) carries
ranks up to 6, so treat 0-3 as the documented range rather than as a ceiling.

Typo note (kept because greps for the corrected spelling miss the sentence): the English page opens "PyRte
implements an algorithm" and ends the same paragraph "while preparing yRate's input files"
(`tutorial-1.md` 94); the CN twin renders both as PyRate (`tutorial-1-cn.md` 95), so the CN page is *not* a
typo-faithful guide.

## Worked example

The occurrence-table and R-call lines below are the docs' own commands with the paths pointed at the local
fixtures; the `python PyRate.py …` lines need a PyRate installation (not part of this workspace) and are
quoted from `references/tutorial-1.md`. `extract.ages` lives in `pyrate_utilities.r`, which ships with the
PyRate package — the corpus names it but does not contain it, so set `<utils>` to your own copy.

```sh
# 0. look at the two documented table shapes (fixtures, see the table below). Every command below is pasted FROM
#    THE SUITE ROOT: there the checker is pyrate-input-file/scripts/validate_input.py and the fixtures are
#    assets/files/ — a bare scripts/validate_input.py from the root names no file (this file's tables, by
#    contrast, use the skill-directory view: scripts/validate_input.py and ../assets/files/).
grep -v '^#' assets/files/occ-ursidae-table-EXCERPT.txt | column -t -s$'\t'   # wiki header: Species Status MinT MaxT Trait
grep -v '^#' assets/files/occ-canis-table-with-Site.txt | column -t -s$'\t'   # tutorial header + Site

# 1. build a strict copy of the table (the fixtures carry '#' provenance lines - strip them)
mkdir -p /tmp/occ_run && grep -v '^#' assets/files/occ-ursidae-table-EXCERPT.txt > /tmp/occ_run/Ursidae.txt

# 1b. pre-flight this skill's own checker on the exact file you will hand to R (prints PASS, exit 0). It does
#     skip '#' provenance lines, but it warns that a real run may not - so checking the stripped copy is the
#     honest order of operations.
python3 pyrate-input-file/scripts/validate_input.py /tmp/occ_run/Ursidae.txt --expect trait

# 2. the documented R step: references/preparing-input-file.md line 52
Rscript -e 'source("<utils>/pyrate_utilities.r")
            extract.ages(file = "/tmp/occ_run/Ursidae.txt", replicates=10, cutoff=5, random=TRUE)'
#   -> "two files": the .py plus the taxon list beside it (tutorial-1.md 40 says two files; the exact
#      names _PyRate.py / _TaxonList.txt and the "same directory" part are §Verified, not documented)

# 3. confirm the replicate count and the Numpy-array structure before launching anything
grep -c '^data_' /tmp/occ_run/Ursidae_PyRate.py            # 10 -> replicates=10 worked (§Verified layout)
head -5 /tmp/occ_run/Ursidae_PyRate.py                     # compare ../assets/files/occ-pyrate-input-structure-EXCERPT.py

# 4. the documented pre-flight and audit calls (need a PyRate installation)
python PyRate.py '/tmp/occ_run/Ursidae_PyRate.py' -data_info            # tutorial-1.md 45
python PyRate.py  -check_names /tmp/occ_run/Ursidae_TaxonList.txt       # tutorial-1.md 98 (the doc's own
#     example reads .../PBDB_dataset_TaxonList.txt; the _TaxonList name for this data set is from §Verified)

# 5. a first real run picking replicate 1 (tutorial-1.md 180; -j owned by pyrate-command-reference)
python PyRate.py /tmp/occ_run/Ursidae_PyRate.py -A 2 -mHPP -mG -j 1
```

Step 2 was executed twice for this skill family with R 4.1.2 on the wiki's own 7-row table (the author, then
re-run by the auditor): both times it wrote a `Ursidae_PyRate.py` with `data_1` … `data_10`, one array per
species and 4 arrays in the first replicate (4 species from 7 occurrences), e.g.
`data_1=[array([4.388551]), array([3.801561]), array([8.405514,14.697734]), array([2.353374,1.50151,3.240746])]`.
The ages are drawn without a seed, **so your numbers will differ — compare structure, never values.** The run
also printed `Excluded  0 % occurrences` (two spaces after "Excluded") and left an `Rplots.pdf` behind; both
come from the script, not from the docs (§Verified), and the zero is expected here because the widest range in
that table is 4.0 Myr, below `cutoff=5`.

## Pitfalls

- **The `-j` numbering runs over the replicates in the file, not over your runs**: with `replicates=10` the
  input holds ten data sets (`preparing-input-file.md` 34-37; `tutorial-1.md` 38, 178), so `-j 11` asks for a
  data set that is not there. The docs never state the valid range or the failure message.
- **`random=FALSE` is only reachable with `replicates=1` in practice.** The doc says `random` "defaults to
  `TRUE` if several replicates are generated (i.e. replicates > 1)" (`preparing-input-file.md` 45) and never
  says what an explicit `random=FALSE` does in that case; the upstream script overwrites it unconditionally
  (§Verified, reproduced), so a midpoints-plus-replicates design is not expressible.
- **Do not "clean" the header conflict by picking one page**: `MinT`/`MaxT` and `MinAge`/`MaxAge` are both in
  print (`preparing-input-file.md` 16 vs `tutorial-1.md` 52) and no page lists accepted header strings.
- **Trait is per occurrence in the table, per species in the analysis**: the table gives a value on each row
  (`preparing-input-file.md` 16-23) while the model uses lineage trait values; the corpus's only statement
  connecting the two is that a trait "can be used in the birth-death analysis"
  (`preparing-input-file.md` 14) — the *how* is nowhere stated (inference). §Verified records that the upstream
  script writes one value per species, the mean of that species' occurrence values, `nan` where they were `NA`.
  The `-trait_file` alternative and trait handling are owned by
  `pyrate-trait-age-models` (`../pyrate-trait-age-models/references/command-list.md` 130-135).
- **`cutoff` is a data-deletion switch, not a warning**: both pages say occurrences are "excluded from the data
  set" / "removed" (`preparing-input-file.md` 39-42; `tutorial-1.md` 38); neither page says anything is reported
  back. The upstream script prints `Excluded  N % occurrences` and opens a histogram device (§Verified) — quote
  the number in your own notes rather than assuming a later reader sees it. **What it deletes for you**
  (inferred; no page states it): a species whose every occurrence is excluded leaves the list "containing the
  list of all species included in the dataset" (`tutorial-1.md` 40), the input file and the analysis — so
  richness, the observed time span and every rate estimated afterwards describe a smaller biota. **Re-count
  instead of assuming**: build the table twice (`cutoff=NULL`, `cutoff=5`), diff the two species lists and
  compare both `-data_info` prints (`tutorial-1.md` 45; `../pyrate-summarize-results/references/summarize-results.md` 10); commands in `references/cutoff-and-completeness.md` §4.
- **The docs' paths are placeholders**: `.../`, `/path_to_file/`, `…/` (`tutorial-1.md` 31;
  `preparing-input-file.md` 28, 52; `tutorial-1.md` 68) — substitute real paths before running.
  Two conveniences *are* documented, both in Tutorial 1 and absent from the wiki page: drag and drop `pyrate_utilities.r` onto the R console (`tutorial-1.md` 31; CN 32) or the input file onto the terminal window (`tutorial-1.md` 174; CN 175). The fix-the-source-then-regenerate loop is **not** stated anywhere: `tutorial-1.md` 115 stops at repairing the table, so re-calling `extract.ages` after a fix is an inference from `preparing-input-file.md` 26 (`references/cutoff-and-completeness.md` §5).
- **Argument order is not uniform**: `-data_info` follows the input file (`tutorial-1.md` 45) while
  `-check_names` precedes a taxon list (`tutorial-1.md` 98) — the file after `-check_names` is *not* a
  `*_PyRate.py` input.

## Not documented in this wiki

| Unanswered question | Why you must not fill it in |
| --- | --- |
| How to **choose** the `cutoff` threshold, and what a given value costs the data set | the pages print a default (`cutoff=NULL`, "all occurrences are kept in the data set") and one worked value each — `5` Myr (`preparing-input-file.md` 41-42; CN 42-43) and `10` Myr (`tutorial-1.md` 38; CN 39) — plus no criterion, no sensitivity protocol, and no statement of what exclusion does to species richness or to the estimates; the trace and the re-count commands are in `references/cutoff-and-completeness.md` §3, §4, §6 |
| Are the four mandatory header strings checked at all, and what happens if you rename them (`MinAge` vs `MinT`)? | neither page states a header-name requirement except for `"Site"` (`tutorial-1.md` 87); the wiki names its example file `Ursidae.txt` without printing that file (`preparing-input-file.md` 52) and prints the example table without naming the file (`preparing-input-file.md` 16-24), so the two are never tied together |
| Can one table carry **both** a trait column and a `Site` column? | the wiki documents "One additional column" (`preparing-input-file.md` 14) and the tutorial documents a 5th column `Site` (`tutorial-1.md` 75) — a 6-column table is described nowhere |
| What are the units PyRate demands, and may MinT exceed MaxT for a normal occurrence? | "Myr" appears only inside the `cutoff` examples (`preparing-input-file.md` 42; `tutorial-1.md` 38) and as "typically Myr" for the output table (`tutorial-1.md` 201); no rule about reversed/inverted age pairs exists in either page |
| Which `Site` IDs are valid, must they be contiguous, may a site hold one occurrence? | `tutorial-1.md` 72 says only "a number specifying the ID of the assemblage" |
| Does `-check_names` accept a header line, duplicates, or the 2-3 column `*_SpeciesList.txt` shape? | `tutorial-1.md` 94 demands "one species name for each row" and simultaneously points at the generated list file; the generated file's shape is never printed (upstream writes a header — §Verified) |
| Are **genus-level (single-rank) names** — `Mammuthus`, `Canis sp.`, an unresolved OTU label — accepted or rejected, anywhere in the chain? | the corpus states one format only, the two-rank *Genus\_species*, and states it as what `-check_names` **expects** (`references/tutorial-1.md` 94; CN `references/tutorial-1-cn.md` 95); no page names a rank above species, no page says a one-word name is an error, and every printed table holds binomials only (`references/tutorial-1.md` 49, 52-63) — so a genus-level OTU that converts without complaint is **not documented** as valid, and neither is it documented as rejected; report such names as unvalidated rather than as accepted. This skill's checker `WARN`s on any name that is not exactly two underscore-separated tokens (`scripts/validate_input.py`:627-633) — the tool's reading of that same sentence, not a corpus rule |
| What ranks does `-check_names` actually emit beyond the documented 0-3, and what is the output file's name? | `tutorial-1.md` 100 defines 0-3 only; 105-113 shows 0-2; the output file name is never given ("a table saved in a text file"); §Verified reports an upstream example file with ranks up to 6 and a `<input>_scores.txt` naming pattern, neither of which is documented |
| Does `extract.ages.pbdb` accept `random`? | `tutorial-1.md` 38 limits it to "two additional options"; `preparing-input-file.md` 44-47 documents `random` for `extract.ages` only (§Verified: the upstream function does take it) |
| Which PBDB columns does `extract.ages.pbdb` read, and what if "Include metadata" was left on? | `tutorial-1.md` 26 names two checkboxes and nothing else about the CSV shape |
| How is the `extant` mark used, and what happens when a species is `extant` in one row and `extinct` in another? | the corpus only says the status must be provided (`tutorial-1.md` 33) and defines the two strings; no consistency rule is stated |
| Is there a minimum number of occurrences/species for a usable input? | nothing in either page; `-singleton` (a *runtime* exclusion, `../pyrate-command-reference/references/command-list.md` 37-42) is not an input requirement |
| What is the exact on-screen format of `-data_info` output? | the only description is the summary-statistics sentence in `../pyrate-summarize-results/references/summarize-results.md` 9-10 |

## Verified outside this corpus

These checks were run against the **upstream** `pyrate_utilities.r` and `example_files/` (the files the corpus
names at `preparing-input-file.md` 28, 52 and `tutorial-1.md` 68 but does not contain): local copies fetched
during authoring, md5-recorded where a fixture points at them, and R 4.1.2 is the interpreter used. Rows marked
**[re-run]** were reproduced independently by the auditor on 2026-11-20 against those same copies. They are
*not* wiki documentation and can drift from it; treat them as engineering facts, cite the docs for anything you
report as "documented". Conflicts between this block and the docs are listed in the skill's report.

| Check (R 4.1.2, `extract.ages`) | Result |
| --- | --- |
| `cutoff=q` boundary | excludes range **≥ q** (a row with MaxT-MinT = 4.0 is dropped at `cutoff=4`, one with 3.999 is kept) → the wiki's "or higher" (`preparing-input-file.md` 42) is what the code does, the tutorial's "greater than" (`tutorial-1.md` 38) is not |
| header row required? | yes — `read.table(header=T)`: with no header the **first occurrence is silently eaten** as column names; header *strings* are ignored (parsing is positional for columns 1-4), so both `MinT/MaxT` and `MinAge/MaxAge` work |
| blank in a mandatory column | hard stop: `the input file contains missing data in species names, status or ages)` |
| one species both `extant` and `extinct` | hard stop: `at least one species is listed as both extinct and extant` |
| `Status` spelled neither `extant` nor `extinct` **[re-run]** | no check, no warning: a row typed `extint` is written like any extinct one; only the exact string `extant` (compared case-insensitively) triggers the extant treatment, so a typo silently changes the data |
| `MinT` > `MaxT` **[re-run]** | accepted silently — the random draw uses the element-wise min/max of the two columns, so a reversed pair yields the same interval as the correct order (the upstream warning for it exists only as commented-out code) |
| `random=FALSE` with `replicates>1` **[re-run]** | ignored: replicate 1 and replicate 2 gave different non-midpoint ages, i.e. the script sets randomization on for `replicates > 1` whatever you asked for — the doc's "defaults to `TRUE`" (`preparing-input-file.md` 45) is weaker than the code |
| the taxon-list file actually written | `<base>_TaxonList.txt`, tab-delimited with a header `Species Status` (plus a third column `Trait` when the table had a trait column) — one row per **species**, not "one species name for each row" as `-check_names` demands (`tutorial-1.md` 94) |
| `*_PyRate.py` body | `#!/usr/bin/env python`; `from numpy import *`; `data_1=[array([...]), …]` (one array per species, sorted by name, holding that species' randomised ages; extant species get a trailing `0`), `data_2` … per replicate, then `d=[ data_1, …]`, `names=[ 'Ursidae_1', …]`, `get_data(i)`, `get_out_name(i)`, `taxa_names=[…]`, and `trait1=array([... nan …])` / `traits=[trait1]` / `get_continuous(i)` when a trait exists — consistent with "list of Numpy arrays" (`../pyrate-command-reference/references/command-list.md` 13) but never printed in the corpus; see `../assets/files/occ-pyrate-input-structure-EXCERPT.py`. Verified two ways: read off the upstream example file (75 arrays per `data_N`, 6 taxa ending in `,0`) and by generating a file here **[re-run]** |
| six-column table (trait + `Site`) | both are lost: the 5th column is only renamed `trait`/`site` when the table has exactly 5 columns, so a 6-column table gets per-occurrence ages (site ignored) and no trait block |
| 5th column named anything else | treated as the trait column (the name only matters when it is `Site`, matched case-insensitively) |
| trait values in the `.py` | one entry per species = the **mean** of that species' per-occurrence trait values (`NA` → `nan`), i.e. the per-occurrence column is collapsed at conversion time, not at analysis time |
| `extract.ages.pbdb` interface | `function(file, sep=",", extant_species=c(), replicates=1, cutoff=NULL, random=TRUE)` — so `random` **is** accepted despite "two additional options" (`tutorial-1.md` 38); it reads the PBDB columns `accepted_name`, `min_ma`, `max_ma` by name, matches `extant_species` against `accepted_name` **before** spaces become underscores (a non-matching name is silently `extinct`), writes an intermediate tab-delimited `<base>.txt` and then calls `extract.ages()` on it. Leaving "Include metadata" on was tested **[re-run]**: a ragged preamble makes R die inside `read.table` (`line 1 did not have 4 elements`) and a missing `accepted_name` column dies later with `argument is of length zero` — neither message mentions the checkboxes, and a preamble whose rows carry exactly as many fields as the data would instead be eaten as the header (not tested, by inference) |
| undocumented `extract.ages` arguments | `outname="_PyRate"`, `save_tax_list=T` (and `sep=","` for `extract.ages.pbdb`) exist in the script; the corpus documents `file`, `replicates`, `cutoff`, `random` only |
| side effects | with `cutoff` set, an `Rplots.pdf` histogram appears in the working directory **[re-run]** and `Excluded  N % occurrences` (two spaces) is printed; `extract.ages.pbdb` prints `This function is currently being tested - caution with the results!` (a string from the shipped R script: no such caution appears in any mirror) |
| upstream `example_files/Ursidae.txt` (the file `preparing-input-file.md` 52 names) | 965 occurrence rows + header `Species Status min_age max_age trait`, **CR-only line endings**, 75 species (261 `extant` rows), trait values in grams-ish magnitudes (e.g. `285000` where the wiki prints `285`) — the wiki's `MinT/MaxT/Trait` header and its trait numbers do not match this file |
| upstream `-check_names` companion output | the fetched `example_species_list_scores.txt` (the file whose name pairs with `example_species_list.txt`, header `taxon1 taxon2 rank` as `tutorial-1.md` 105 describes) holds **ranks 0-6**, i.e. well past the documented 0-3, and the name pattern implies the output is `<input>_scores.txt`. Both are inferences from a shipped example: no copy of `PyRate.py` was available here to read the code |

## Related skills

- `pyrate-command-reference` — owns every flag: `<input file>`, `-j` (default 1), `-data_info` link, `-singleton`, `-N`, `-trait_file`, `-d` (the alternative origin/extinction table input, which bypasses `extract.ages`).
- `pyrate-summarize-results` — owns `-data_info`'s description and all output files (`sum.txt`, `mcmc.log`, `marginal_rates.log`), log combination across replicates.
- `pyrate-preservation-models` — NHPP/HPP/TPP, `-mHPP`, `-qShift` + `epochs_q.txt`, `-mG`, `-pP`.
- `pyrate-bd-analysis` — the analysis itself: `-A 2`/`-A 4`, `-n`, `-s`, `-fixShift`, `-edgeShift`, output files.
- `pyrate-installation` — the Python 2.6-2.7 environment (and the wiki's Python 3 PATH contradiction), `numpy`/`scipy`.
- `pyrate` — the router: program list, invocation form, citations, three-step workflow.
- `pyrate-trait-age-models` — what the trait column is for downstream (`-mCov`, `-trait_file`, `NA` imputation by the MCMC).
- `pyrate-des` — a different input pipeline entirely (`DES_input_preparation.R`, `DESin()`), not `extract.ages`.
- `scripts/validate_input.py` — the pre-flight checker for this skill's raw occurrence tables and for a generated `*_PyRate.py`. The path is written from this skill's own directory, the anchor a skill loader resolves; from a sibling skill's folder it is one level up and back down into this folder. **Which spelling runs depends on where you type it**: a bare `scripts/validate_input.py` at the suite root names a file that does not exist (the failure seen in blind testing), so there prepend this skill's folder name to it — the spelling every runnable command in this file uses — while inside this skill directory the path above is complete as written (and the fixtures are `../assets/files/`, which is the view this file's tables take). Note that the script's own `--help` USAGE block prints only the skill-directory-relative form, `scripts/validate_input.py`:54-60, so `--help` is not a safe source for the path.
  **Owned by the tooling agent and still changing**: read `python3 scripts/validate_input.py --help` and `--rules` (typed in this skill's directory) rather than trusting this bullet. Interface observed at re-check time:
  `validate_input.py [PATH ...] [--expect trait|site|none] [--pyrate-dir DIR] [--json] [--rules] [--max-findings N] [--quiet] [--self-test]`, where `ERROR` = a rule the docs state, `WARN` = a pattern the docs only exhibit or the tool inferred, and exit 0/1/2 = no ERROR / at least one ERROR / usage-IO. The flag set and its values are read off `scripts/validate_input.py`:62-70 and `:1293` —
  **`--expect` takes exactly `trait`, `site` or `none`** (line 64); omit it to check a table without asserting which optional 5th column it must carry (the mismatch ERROR at `:563-572` only fires when the flag was given).
  Three behaviours worth knowing, each re-run against the current file: it skips the fixtures' `#` provenance lines and says so in a `NOTE`; it reports the tutorial's `Taxon_name Status MinAge MaxAge` header as a `WARN` that quotes *both* mirrors (wiki 16 vs tutorial 52)
  instead of demanding one spelling, which matches §Which column names are correct; and it treats `MinT` > `MaxT` as a `WARN` explicitly labelled INFERRED, matching §Verified (the corpus never states the ordering, and upstream accepts
  it silently). `--self-test` did **not** pass at audit time (4 of 49 assertions, `--self-test --quiet`), and two of them are the checker reading `../assets/files/occ-pyrate-input-structure-EXCERPT.py` — a deliberate three-window excerpt of a 793-line upstream file — as though it were a complete input, so `d=[…]` names `data_2`-`data_10` that
  the excerpt elides (those two assertions are at lines 1119-1120 of the current file). Do not "repair" the excerpt by padding it out: that would destroy the byte-identity the file exists to demonstrate, so the mismatch is the checker's to resolve. It inspects tables and the `.py` shape; it does not run `extract.ages` or PyRate.

## Resources

| File | What's in it | Load when |
| --- | --- | --- |
| `references/preparing-input-file.md` | The wiki's input-format page: the mandatory four columns and the no-missing-data rule, the trait column and `NA`, the Ursidae example table, `source()` of `pyrate_utilities.r`, `extract.ages` with `replicates` / `cutoff` / `random` and their defaults, the full example call and the generated `Ursidae_PyRate.py` | Any question about table format or the R options |
| `references/preparing-input-file-cn.md` | Full CN twin (lines are +1 vs the English file); same tables, same defaults; renders `replicates > 1` → `TRUE` and `cutoff` "达到或超过" exactly | When an English sentence about defaults or the cutoff boundary is ambiguous |
| `references/tutorial-1.md` | Tutorial 1: the PBDB route (checkboxes, `extant_dogs`, `extract.ages.pbdb`, the no-synonyms note), the manual route with the `Taxon_name/Status/MinAge/MaxAge` and `Site` tables, `-data_info`, `-check_names` and its rank table — plus the preservation-model/analysis/output sections that belong to the sibling skills | Building an input from PBDB, or the name/rank questions |
| `references/tutorial-1-cn.md` | Full CN twin (lines +1 vs English); identical tables and commands; corrects the English `PyRte`/`yRate's` typos to PyRate and keeps the `cutoff` "大于" wording | Cross-checking a quoted sentence, and to see which typos are English-only |
| `../pyrate-command-reference/references/command-list.md` | `../pyrate-command-reference/references/command-list.md` 13 ("list of Numpy arrays"), 15 (`python PyRate.py path_to_input_file/Ursidae_PyRate.py`), 27-30 (`-j`), 19-20 (`-d` alternative input), 37-42 (`-singleton`), 162-163 (`-N`) | Anything a flag does with the file you produced |
| `../pyrate-summarize-results/references/summarize-results.md` | 9-10: the `-data_info` statistics list | Interpreting the pre-flight output |
| `../pyrate-trait-age-models/references/command-list.md` | 130-135: traits read from the python file with `-mCov`, or supplied separately via `-trait_file` (NA imputed by the MCMC) | When a trait column is involved |
| `../pyrate/references/home.md` | 69-71 (Python 2.6-2.7, `numpy`/`scipy`), 75-80 (invocation form), 86 (`pyrate_utilities.r` tested under R 2.x/3.x) | Before running the R or Python steps |
| `scripts/validate_input.py` | This skill's pre-flight checker for occurrence tables and for a generated `*_PyRate.py`; **run it from this skill's directory with this path** (at the suite root, prepend this skill's folder name to it — see Related skills), with `--expect trait|site|none` (owned by the tooling agent; see Related skills for its current flags, its three re-checked behaviours and its failing self-test) | Before handing a table to `extract.ages`, and after generating the `.py` |

## grep recipes

```sh
# run these from this skill directory (all 8 verified to match on 2026-11-20)
grep -n "can not deal with missing information" references/preparing-input-file.md
grep -n "or higher\|larwger\|达到或超过\|大于 10" references/*.md
grep -n "MinT\|MinAge" references/preparing-input-file.md references/tutorial-1.md
grep -n "first three occurrences\|前三条" references/tutorial-1.md references/tutorial-1-cn.md
grep -n "SpeciesList\|TaxonList\|check_names" references/tutorial-1.md
grep -n "Show accepted names only\|extant_species\|considered as extinct" references/tutorial-1.md
grep -n "uniform distributions\|midpoint\|replicates=1\|cutoff=NULL" references/preparing-input-file.md
grep -n "Ranks 0 and 1\|does NOT check for synonyms" references/tutorial-1.md
```

## Runnable fixtures (`../assets/files/`)

The `#` lines at the top of the first five fixtures are provenance comments, not data — strip them with `grep -v '^#' <file>` for a strict reader (`extract.ages` skips them: R's `read.table` default treats `#` as a
comment character, verified outside the corpus; `python3 scripts/validate_input.py` — run in this skill's directory, prepend this skill's folder name at the suite root — also skips them, but emits a `NOTE`
warning that a real run may not, which is the reason every command here strips first). The four upstream-derived files (`occ-pyrate-input-structure-EXCERPT.py`,
`occ-ursidae-upstream.txt`, `occ-taxonlist-upstream-EXAMPLE.txt`,
`occ-check-names-input-upstream-EXCERPT.txt`) come from the upstream `example_files/` the corpus names but does
not contain: only the `.py` excerpt carries its own provenance header, the other three are kept byte-clean so a
reader parses exactly what upstream ships, and their provenance (with md5s) is recorded in the table below.

| File | Run it? | Provenance | What it makes concrete |
| --- | --- | --- | --- |
| `../assets/files/occ-ursidae-table-EXCERPT.txt` | yes (input to `extract.ages`) | `PyRate-doc/PyRate-wiki/1.-Preparing-input-file.md` lines 8-15 (= mirror 16-23) — derived (backticks/padding normalised to single tabs; the doc's literal `...` row at mirror line 24 dropped) | the wiki's 5-column table, `NA` in the trait column, repeated species names, one row per occurrence |
| `../assets/files/occ-canis-table.txt` | yes | `PyRate-doc/PyRate-tutorials/tutorials/pyrate_tutorial_1.md` lines 44-55 (= mirror 52-63) — derived (markdown pipes → tabs) | the tutorial's 4-column header `Taxon_name Status MinAge MaxAge` and the `extant`/`extinct` vocabulary |
| `../assets/files/occ-canis-table-with-Site.txt` | yes | same source, lines 67-77 (= mirror 75-85) — derived | the `Site` column: rows 1-2 share Site 1, rows 5-7 Site 4, rows 8-9 Site 5 → coeval randomisation; its header also records the doc's own prose/table contradiction (`tutorial-1.md` 72 vs 77-79) |
| `../assets/files/occ-check-names-output-EXAMPLE.txt` | no (output sample) | same source, lines 97-105 (= mirror 105-113) — derived | the three columns `-check_names` writes and the rank values it prints (0-2; rank 3 is defined at line 100 but never shown) |
| `../assets/files/occ-extract-ages-calls.R` | no (reference lines) | wiki 20, 44 (= mirror 28, 52) + tutorial 23, 26, 29, 60 (= mirror 31, 34, 37, 68) — derived (the docs wrap each call in backticks and add trailing prose on three of the six lines; dropped here, R text byte-identical) | every documented `source()` / `extract.ages` / `extract.ages.pbdb` / `extant_dogs` line in one place, including the U+2026 path |
| `../assets/files/occ-pyrate-input-structure-EXCERPT.py` | parseable, not runnable as data | **upstream** `example_files/Ursidae_PyRate.py` (referenced by `preparing-input-file.md` 54) lines 1-10, 78-80, 784-793 — EXCERPT | the real shape behind "list of Numpy arrays": `data_1=[array([...]), …]` … `data_10`, `d=[…]`, `names=[…]`, `taxa_names=[…]`, `trait1=array([ … nan …])`; extant species end in a trailing `0` |
| `../assets/files/occ-ursidae-upstream.txt` | yes (input to `extract.ages`) | **upstream** `example_files/Ursidae.txt`, byte-verbatim (md5 `cbea033159a13ea4d5311b7a8372def3`), CR line endings — kept byte-clean, no provenance header on purpose | the 965-occurrence table the docs' own example call names, with header `Species Status min_age max_age trait`: a **third** column spelling, and trait values `285000` where the wiki prints `285` |
| `../assets/files/occ-taxonlist-upstream-EXAMPLE.txt` | no (sample of a generated file) | **upstream** `example_files/Ursidae_TaxonList.txt`, byte-verbatim (md5 `c74c06df65cbfa9b4efbc6d14c29b4b2`) | what `extract.ages` really writes beside the `.py`: 75 species rows with header `Species Status Trait` — the file the tutorial calls `*_SpeciesList.txt` and `-check_names` calls `*_TaxonList.txt` |
| `../assets/files/occ-check-names-input-upstream-EXCERPT.txt` | yes (input to `-check_names`) | **upstream** `example_files/example_species_list.txt` lines 1-21 — EXCERPT | a real one-species-name-per-row list with a `species` header row and duplicated misspellings inside it, i.e. the shape `-check_names` demands |
