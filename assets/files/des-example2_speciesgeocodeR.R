# source: PyRate-doc/PyRate-tutorials/tutorials/pyrate_tutorial_5.md lines 97-126 (= fenced block at references/tutorial-5.md:105-134) | verbatim
# shows: route 2 - classifying fossil/recent coordinates into areas with speciesgeocodeR (>= v 1.0-6), then writing plain foss.txt / pres.txt tables
# note: this tutorial version does NOT call DESin()/write.DES.in(); the DES input files come from PyRateDES.py -fossil/-recent (tutorial-5.md:143)
# note: paths are literally "..."-abbreviated in the doc, and "DES_examples/DES_input_dataExample_2_recent_coordinates.txt" on tutorial-5.md:119 is missing a slash - both kept as printed
library(speciesgeocodeR)

occ.thresh <- 0.1 #at least 10% occurrence in an area required

#Assign the fossil coordinates to operational areas
fos <- read.table(".../PyRate/example_files/DES_examples/DES_input_data/Example_2_coordinates.txt", sep = "\t", header = TRUE)
fos.class <- SpGeoCod(".../PyRate/example_files/DES_examples/DES_input_data/Example_2_coordinates.txt",
                      ".../PyRate/example_files/DES_examples/DES_input_data/Example_regions.shp", areanames = "Region")
foss <- data.frame(fos, higherGeography = fos.class$sample_table$homepolygon)
foss <- foss[complete.cases(foss),]

#Assign the recent coordinates to operational areas, using the occurrence threshold
rec <- read.table("Example_data/Example_2_recent_coordinates.txt", sep = "\t", header = TRUE)

rec.class <- SpGeoCod(".../PyRate/example_files/DES_examples/DES_input_dataExample_2_recent_coordinates.txt",
                      ".../PyRate/example_files/DES_examples/DES_input_data/Example_regions.shp", 
                      areanames = "Region")

pres <- round(rec.class$spec_table[, 2:3] / rowSums(rec.class$spec_table[, 2:3]), 2)
pres[which(pres[, 1] >= occ.thresh ), 1] <- names(pres)[1] 
pres[which(pres[, 2] >= occ.thresh ), 2] <- names(pres)[2] 
pres <- data.frame(scientificName = rep(rec.class$spec_table[, 1], 2),
                   higherGeography = c(pres[, 1], pres[, 2]))
pres <- pres[pres$higherGeography %in% names(rec.class$spec_table), ]

# Write tables 
write.table(foss, ".../PyRate/example_files/DES_examples/DES_input_data/foss.txt",
            sep = "\t", col.names = TRUE, row.names = FALSE, quote = FALSE)
write.table(pres, ".../PyRate/example_files/DES_examples/DES_input_data/pres.txt",
            sep = "\t", col.names = TRUE, row.names = FALSE, quote = FALSE)
