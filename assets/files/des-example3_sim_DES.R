# source: PyRate-doc/PyRate-tutorials/tutorials/pyrate_tutorial_5.md lines 144-161 (= fenced block at references/tutorial-5.md:152-169) | verbatim
# shows: route 3 - simulating DES input files with the R package simDES (github.com/thauffe/simDES): sim_DES() call + write.table of Sim[[1]] to sim.txt
# note: only the FIRST element Sim[[1]] is written; what the other elements hold is not documented in this corpus
# Install the packages
library(devtools)
install_github("thauffe/simDES")
library(simDES)

# Check the documentation of the main function sim_DES
?sim_DES

# E.g. simulating 100 lineages over 25 million years with a rate shift 5.3 million years ago and sampling heterogeneity
Sim <- sim_DES(Time = 25, Step = 0.01, BinSize = 0.25, Nspecies = 100,
               SimD = c(0.2, 0.1, 0.3, 0.15),
               SimE = c(0.1, 0.1, 0.05, 0.15),
               SimQ = c(0.5, 0.4, 0.7, 0.8),
               Qtimes = 5.3, Ncat = Inf, alpha = 1)

# Write input table
write.table(Sim[[1]], ".../PyRate/example_files/DES_examples/DES_input_data/sim.txt",
            sep = "\t", row.names = FALSE, quote = FALSE, na = "NaN")
