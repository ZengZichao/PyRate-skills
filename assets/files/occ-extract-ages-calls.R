# source: PyRate-doc/PyRate-wiki/1.-Preparing-input-file.md lines 20, 44 and PyRate-doc/PyRate-tutorials/tutorials/pyrate_tutorial_1.md lines 23, 26, 29, 60 | derived (in the docs each call sits inside markdown backticks and three of the six lines carry trailing prose after the closing backtick; the backticks and that prose are dropped here, the R text itself is unchanged - including the wiki's '> ' console prompts, the tutorial's two-space list indentation and its U+2026 path character)
# shows: every R line the two input-preparation pages print - loading pyrate_utilities.r, the extant-species vector, extract.ages.pbdb(), extract.ages() with replicates/cutoff/random
# the leading "> " marks the R console prompt as printed by the wiki page - drop it before running; these lines are the docs' placeholders (".../", "/path_to_file/"), not real paths

# references/preparing-input-file.md:28 (wiki page)
> source(file = "/path_to_file/pyrate_utilities.r")

# references/preparing-input-file.md:52 (wiki page: 10 replicates, cutoff 5, random ages)
> extract.ages(file = "/path_to_file/Ursidae.txt", replicates=10, cutoff=5, random=TRUE)

# references/tutorial-1.md:31 (tutorial, option 1 step 3)
  source(".../PyRate-master/pyrate_utilities.r")

# references/tutorial-1.md:34 (tutorial, option 1 step 4 - names here use SPACES, cf. the underscored Genus_species names used in the tables)
  extant_dogs = c("Canis rufus","Canis lupus","Canis aureus","Canis latrans","Canis mesomelas","Canis anthus","Pseudalopex gymnocercus","Canis adustus","Canis familiaris")

# references/tutorial-1.md:37 (tutorial, option 1 step 5)
  extract.ages.pbdb(file= ".../Canis_pbdb_data.csv",extant_species=extant_dogs)

# references/tutorial-1.md:68 (tutorial, option 2 step 4) - as printed, including the U+2026 character instead of three dots in the path
  extract.ages(file="…/PyRate/example_files/Ursidae.txt", replicates=10)
