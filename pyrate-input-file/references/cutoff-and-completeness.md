# What the input page demands of the occurrence set, and what `cutoff` takes away

**This file is not a mirror.** It is suite-authored analysis and the detail layer for four rows of
`SKILL.md` — hazard 1 and 8 of *The eight things that break a run*, the `cutoff` row of the
`extract.ages` options table, the `cutoff` and placeholder-path bullets of *Pitfalls*, and the two
threshold rows of *Not documented in this wiki*. Every claim below carries a citation of the form
`references/<file>.md:LINE` into the mirrors this skill carries, every double-quoted span is
byte-identical to the mirror at that line, and everything the corpus does not say is marked
**inferred** (a reading of the printed pages) or **undocumented** (the corpus is silent). Line
numbers are of the local mirrors, frontmatter included; the `-cn` twins sit one line lower than the
English on both pages used here, and each CN line is given so the trace can be re-checked in either
language. `references/preparing-input-file.md` is 54 lines long, so its last citable line is 54.

## 1. Two demands in one sentence

The page that defines the input table opens with a scope demand and a completeness demand printed in
the same breath (`references/preparing-input-file.md`:14, CN `references/preparing-input-file-cn.md`:15):

> All fossil occurrences need to be provided in a table (a tab-delimited text file), with species
> names, their status ("extant" or "extinct"), and minimum and maximum ages as the columns.

| Demand | What the page then allows | Citation |
| --- | --- | --- |
| **Provide every occurrence** — "All fossil occurrences need to be provided" | nothing to trim by: the table is the whole occurrence set of the study group | `references/preparing-input-file.md`:14 / CN :15 |
| **Fill the four columns** — "At present, PyRate can not deal with missing information in these four columns, so make sure that you remove these entries beforehand." | the remedy the page itself prescribes is **deleting the row**, before any R option exists | same line |
| One extra column of trait values, where "missing data are allowed, and should be given as  NA" (the double space is the doc's) | `NA` is the only documented missing marker, and only in that column | same line |

Read together, the two demands are in tension and the page resolves it by deletion: an occurrence
that is real but has an unfilled stage boundary must be **removed** to satisfy the column rule, which
breaks the "all occurrences" rule. Neither page states which demand wins, and neither asks for a
record of what was dropped — the second sentence is the corpus's only appearance of the word
"beforehand" in this context (`references/preparing-input-file.md`:14, CN :15). **Undocumented**: any
accounting for removed entries. The practical consequence is that the row count of your source table
is the only audit trail, and it lives outside PyRate.

Nothing in the corpus says an incomplete occurrence set is detected anywhere in the chain. The only
input-stage reporting the pages describe is `-data_info`, which "will plot on screen a few summary
statistics about a fossil data set (PyRate input file): number of species, number of species excluded
as singletons" and "number of extant taxa, number of occurrences, observed time span of the data set"
(`../pyrate-summarize-results/references/summarize-results.md`:10) — statistics **of what the file
contains**, never a comparison against what the source table left out. **Inferred** from those lines:
a silently short table is indistinguishable from a short data set.

## 2. `cutoff`, in both pages and both languages

| Wording | Text | Citation |
| --- | --- | --- |
| Wiki, the option | "Specify a threshold to exclude fossil occurrences with a high temporal uncertainty, i.e. with a wide temporal range between MinT and MaxT." | `references/preparing-input-file.md`:40 / CN :41 |
| Wiki, default | "`cutoff=NULL` (default; all occurrences are kept in the data set)" | `references/preparing-input-file.md`:41 / CN :42 |
| Wiki, worked value | "`cutoff=5` (all occurrences with a temporal range of 5 Myr or higher are excluded from the data set)" | `references/preparing-input-file.md`:42 / CN :43 ("达到或超过 5 Myr … 都从数据集中剔除") |
| Wiki, in the example call | `extract.ages(file = "/path_to_file/Ursidae.txt", replicates=10, cutoff=5, random=TRUE)` | `references/preparing-input-file.md`:52 |
| Tutorial, the option | "The option `cutoff` can be used to remove occurrences with an age range greater than a given temporal range." then "will remove all occurrences in which the difference between max age and min age is larwger than 10 Myr" (`larwger` is the doc's typo) | `references/tutorial-1.md`:38 / CN :39 ("删除年龄范围大于给定时间范围的产出记录") |

Both pages use deletion verbs — "excluded from the data set", "remove" — and neither describes a
preview, a log, or a way back. The boundary itself is contested (wiki "or higher" vs tutorial
"greater than"): `SKILL.md` §Verified records the R script excluding ranges **≥ q**, i.e. the wiki
wording, which is an engineering fact about the shipped script and not a corpus claim.

## 3. The deletion cascade, claim by claim

1. **Documented.** `cutoff` removes rows from the data set before it is written
   (`references/preparing-input-file.md`:40-42). The operation is applied to the occurrence table's
   own `MaxT - MinT` spread, so it is independent of the replicate machinery that re-draws ages
   "at random from uniform distributions with boundaries MinT and MaxT"
   (`references/preparing-input-file.md`:34).
2. **Documented, indirectly.** What reaches PyRate is only what survives: the generated file holds
   "all occurrences formatted for a PyRate analysis" and the species list is defined as the file
   "containing the list of all species included in the dataset" (`references/tutorial-1.md`:40, CN :41).
   The list is *of the data set*, so it is a record of the survivors, not of your intentions.
3. **Inferred (the corpus never states it).** A species all of whose occurrences are excluded has no
   row left, so it is no longer "included in the dataset": it leaves the species list, leaves the
   input file, and leaves the analysis. From that point the run estimates diversity and rates for a
   smaller biota than the one you downloaded. This step is the whole reason `cutoff` is a modelling
   decision rather than a cleaning switch, and no page says it.
4. **Inferred.** Because the threshold is an absolute Myr span, its severity depends on the duration
   of the stages a data set is binned to (`references/preparing-input-file.md`:14 says the ages
   "commonly correspond to the temporal boundaries of the stage a particular fossil is assigned to"),
   so the same value can be harmless for one formation and destructive for another. The corpus gives
   no scale-free rule.
5. **Undocumented.** Whether the exclusion is evaluated once on the raw table or per replicate;
   whether anything at all is printed (the upstream script prints `Excluded  N % occurrences` and
   opens an `Rplots.pdf` histogram — `SKILL.md` §Verified, an engineering fact, not a doc claim);
   and what happens when `cutoff` removes every occurrence of the **oldest or youngest** species,
   which shortens "observed time span of the data set"
   (`../pyrate-summarize-results/references/summarize-results.md`:10) at its ends.

## 4. Re-count after setting the threshold

The corpus's own verification habit is the two-file check at `references/tutorial-1.md`:40-45 (step 6,
"Check PyRate input files", ending in `python PyRate.py '.../Canis_pbdb_data_PyRate.py' -data_info`).
Applied to a threshold, that becomes four commands and one comparison. Paths follow the worked example
in `SKILL.md`; run the R step twice, once without the threshold:

```sh
mkdir -p /tmp/occ_run/nocut /tmp/occ_run/cut5
#   generate both inputs from the same table: cutoff=NULL and cutoff=5
  wc -l < /tmp/occ_run/Ursidae.txt                       # rows you supplied
  wc -l < /tmp/occ_run/nocut/Ursidae_TaxonList.txt       # species with no threshold
  wc -l < /tmp/occ_run/cut5/Ursidae_TaxonList.txt        # species after the deletion
  diff /tmp/occ_run/nocut/Ursidae_TaxonList.txt /tmp/occ_run/cut5/Ursidae_TaxonList.txt
python PyRate.py /tmp/occ_run/nocut/Ursidae_PyRate.py -data_info    # tutorial-1.md:45
python PyRate.py /tmp/occ_run/cut5/Ursidae_PyRate.py  -data_info    # compare both count lines
```

Report the deltas — rows supplied, species lost, occurrences and time span per `-data_info` — in your
notes and in anything you hand on, because none of it is written to a file by either program
(§3 point 5). The `_TaxonList` name used above is the one `SKILL.md` §Verified records the script
actually writes; the corpus prose calls it `*_SpeciesList.txt` (`references/tutorial-1.md`:40) while
its own command example reads `.../PBDB_dataset_TaxonList.txt` (`references/tutorial-1.md`:98).

## 5. Two documented path conveniences, and one loop that is not documented

**Stated, in Tutorial 1 only** — both sentences carry their CN twin:

| Convenience | Text | Citation |
| --- | --- | --- |
| the R script's path | "In most operating systems you can drag and drop the *pyrate_utilities.r* file onto the R console to paste the full path." | `references/tutorial-1.md`:31 / CN :32 |
| the input file's path | "In most operating systems (including Mac OS, Windows, and Ubuntu) you can drag and drop the input file onto the terminal window to paste the full path and file name." | `references/tutorial-1.md`:174 / CN :175 |

Neither appears on the wiki input page: `references/preparing-input-file.md` offers only the
placeholders `source(file = "/path_to_file/pyrate_utilities.r")` (:28) and
`extract.ages(file = "/path_to_file/Ursidae.txt", …)` (:52), and the word does not occur on that page
in either language — so a reader who works only from the wiki page is entitled to know the trick is
*documented corpus material*, just on the other page this skill mirrors.

**Not stated anywhere: the fix-then-regenerate loop.** The page that tells you to repair names ends at
"It is up to the researcher to double check these possible inconsistencies and fix the names in their
dataset accordingly." (`references/tutorial-1.md`:115, CN :116) and then moves straight to the
analysis section (`references/tutorial-1.md`:119-121). No page says to call `extract.ages` or
`extract.ages.pbdb` again afterwards, no page says the already-generated `.py` is stale, and no page
says which artifacts must be discarded. **Inferred**, from `references/preparing-input-file.md`:26
(the `.py` is produced *from* the table by that function): an edit to the table changes nothing that
has already been generated, so the loop is table → function → `-data_info` → run, and every command in
`SKILL.md` §Worked example is written in that order for this reason. Treat "regenerate, then re-check"
as the skill's recommendation, never as a wiki instruction.

## 6. Picking the threshold: everything the corpus offers

| What you would want | What exists | Citation |
| --- | --- | --- |
| A default | "`cutoff=NULL` (default; all occurrences are kept in the data set)" | `references/preparing-input-file.md`:41 / CN :42 |
| A worked value | `5` (wiki, twice: the option's own example and the full call) and `10` (tutorial illustration) | `references/preparing-input-file.md`:42, :52 / `references/tutorial-1.md`:38 |
| A unit for the number | "Myr" appears **only inside these two examples**; no page states a unit requirement for the input ages at all | `references/preparing-input-file.md`:42 / `references/tutorial-1.md`:38 |
| A criterion for choosing it — a distribution to inspect, a fraction of occurrences one may afford to lose, a sensitivity protocol | nothing; the sentences stop at what the option does | **undocumented** |
| A report of what it removed | nothing on either page; the script's `Excluded  N % occurrences` line and histogram are `SKILL.md` §Verified (engineering fact about the shipped R code, not a corpus claim) | **undocumented** |

So the two values in print are illustrations, not recommendations, and they are not comparable to each
other (different data sets, different stage durations). **Inferred**, from §3 points 3-4: a threshold
is a statement about which occurrences you distrust, it changes the biota being modelled, and the only
honest procedure is the one in §4 — run the threshold, diff the species lists, report both counts, and
say which value you used. **Undocumented**: any PyRate-side record of the choice; `*_sum.txt` is
described as "the complete list of settings used in the analysis"
(`../pyrate-summarize-results/references/summarize-results.md`:16), which is an *analysis* settings
file, and `extract.ages` runs before any analysis exists.

