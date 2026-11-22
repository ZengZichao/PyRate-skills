# source: PyRate-doc/PyRate-wiki/5.-Dispersal-Extinction-Sampling-model.md lines 35-67 (= fenced block at references/des-model.md:43-75) | verbatim
# shows: the WIKI version of route 2 - same SpGeoCod classification but it then calls DESin()/summary()/plot()/write.DES.in() in R
# conflict: this wiki block generates the DES files with R (source(DES_input_preparation.R)); the tutorial generates them with PyRateDES.py -fossil/-recent
library(speciesgeocodeR)
source(DES_input_preparation.R)

occ.thresh <- 0.1 #at least 10% occurrence in an area required

#Assign the fossil coordinates to operational areas
fos <- read.table("Example_data/Example_2_coordinates.txt", sep = "\t", header = T)
fos.class <- SpGeoCod("Example_data/Example_2_coordinates.txt", "Example_data/Example_regions.shp", areanames = "Region")
foss <- data.frame(fos, higherGeography = fos.class$sample_table$homepolygon)
foss <- foss[complete.cases(foss),]

#Assign the recent coordinates to operational areas, using the occurrence threshold
rec <- read.table("Example_data/Example_2_recent_coordinates.txt", sep = "\t", header = T)

rec.class <- SpGeoCod("Example_data/Example_2_recent_coordinates.txt", "Example_data/Example_regions.shp", 
                      areanames = "Region")

pres <- round(rec.class$spec_table[, 2:3] / rowSums(rec.class$spec_table[, 2:3]), 2)
pres[which(pres[, 1] >= occ.thresh ), 1] <- names(pres)[1] 
pres[which(pres[, 2] >= occ.thresh ), 2] <- names(pres)[2] 
pres <- data.frame(scientificName = rep(rec.class$spec_table[, 1], 2),
                   higherGeography = c(pres[, 1], pres[, 2]))
pres <- pres[pres$higherGeography %in% names(rec.class$spec_table), ]

#create DESin files
exp2 <- DESin(foss, pres, bin.size = 2, reps = 3)
write.DES.in(exp2, "Example2_out")

#explore data
summary(exp2)

par(ask = T)
plot(exp2)

