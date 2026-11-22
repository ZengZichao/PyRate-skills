# source: PyRate-doc/PyRate-wiki/5.-Dispersal-Extinction-Sampling-model.md lines 12-25 (= fenced block at references/des-model.md:20-33) | verbatim
# shows: the R route to DES input files - source(DES_input_preparation.R), DESin(), summary(), plot(), write.DES.in() from the wiki page
#load utility functions
source(DES_input_preparation.R)

#load input files and convert into DES format
exp1 <- DESin("Example_data/Example_1_minimum_data.txt", "Example_data/Example_1_recent_distributions.txt", 
              bin.size = 2, reps = 3)
 
#explore the data for potential biases
summary(exp1)
par(ask = T)
plot(exp1)

#write DES input files to the working directory
write.DES.in(exp1, file = "Example_data/Example1_DES_in")

