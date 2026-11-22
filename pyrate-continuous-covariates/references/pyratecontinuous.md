---
title: PyRateContinuous
source_url: https://github.com/dsilvestro/PyRate/wiki/4.-PyRateContinuous
language: English
mirrored_from: PyRate-doc/PyRate-wiki/4.-PyRateContinuous.md
headings: 8
mirror: verbatim local mirror of the PyRate documentation
---
### Generating input files
PyRateContinuous implements birth-death models in which speciation (origination) and extinction rates change through time as the result of a time continuous variable, e.g. the clade's own diversity or an external factor such as paleo-temperature. The program does not model preservation and assumes that the times of origination and extinction of each lineage are known or have been estimated, typically in a [previous PyRate analysis](https://github.com/dsilvestro/PyRate/wiki/3.-Summarize-PyRate-results#_mcmclog).
Thus, the input file for `PyRateContinuous.py` is a simple table with the times of origin and extinction of each species. The table is formatted as tab-separated text file with the first line containing column headers followed by one row for each species. Each row contains 4 columns: the first column indicates the clade assignment of species, this is only useful in MCDD analyses (Wiki page for PyRateMCDD is under construction) and should be filled with 0s for all other analyses. The second column indicates a species numeric identifier (this values are arbitrary and only used for reference). Finally the third and fourth column contain the time of origin and extinction of each species, respectively. **The input files for PyRateContinuous can be generated from PyRate *_mcmc.log files using the following command:**

##### `-ginput`  
This command analyzes one or multiple PyRate-generated [log files](https://github.com/dsilvestro/PyRate/wiki/3.-Summarize-PyRate-results#_mcmclog) to produce a file that can be used in subsequent analyses in [PyRateContinuous](https://github.com/dsilvestro/PyRate/wiki#pyratecontinuouspy-requires-library-pyrate_lib) or [PyRate](https://github.com/dsilvestro/PyRate/wiki#pyratepy), using the flag `-d`. This command takes as argument either a log file or a directory containing log files. Mean posterior times of origination and extinction are calculated from each log file after excluding burnin (the number of samples excluded is set with the command `-b`).  
Examples:  
`python PyRateContinuous.py -ginput path_to_log_file/Ursidae_1_mcmc.log -b 100` # generates a file named `Ursidae_1_se_est.txt` with the estimated times of origination and extinction for each species, after excluding the first 100 samples as burnin.  
`python PyRateContinuous.py path_to_log_file/ -b 100` # generates as many files as the number of `*mcmc.log` files found in the directory.  
`python PyRateContinuous.py path_to_log_file/ -b 100 -tag Ursidae` # generates a single file with the estimated times of origination and extinction for each species combining all log files containing the "Ursidae" in their file names. The different log files are treated as replicates of the same analysis . The individual replicates can be analyzed in subsequent analyses in PyRate and PyRateContinuous using the [command `-j`](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-j).

***
### Setting up an analysis
##### `-d`
Input files are provided using this command. More details can be found [here](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-d) and above.

##### `-A`
Set the MCMC algorithm: Use `-A 0` for parameter estimation and `-A 1` to estimate model marginal likelihood for model testing ([More details here](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-a)).

##### `-DD`  
Use the `-DD` command to run **diversity dependence models**, in which origination and extinction rates may correlate [linearly or exponentially](https://github.com/dsilvestro/PyRate/wiki/PyRateContinuous#-m) to the clade own diversity. The estimated diversity dependent parameters are logged to the output as `Gl` and `Gm` for speciation and extinction, respectively.

##### `-c`  
In alternative to the diversity dependent model, the user can provide a table reporting the values of a **variable (e.g. a paleoclimate proxy) and its times of change**. The table is a tab-separated text file with header and two columns indicating the time of change and the value of the variable. An [example file is provided here](https://github.com/dsilvestro/PyRate/blob/master/example_files/temperature.txt). Linear or exponential correlations between the variable and origination and extinction rates can be assumed [using the command `-m`](https://github.com/dsilvestro/PyRate/wiki/PyRateContinuous#-m). The estimated correlation parameters are logged to the output as `Gl` and `Gm` for speciation and extinction, respectively.

##### `-m`
Set the correlation model. There are three available options:  
`-m -1` no correlation. This option fits a constant rate birth-death model and is mostly useful for model comparisons using marginal likelihoods .  
`-m 0` exponential correlation (default; see Equation 7 in [Silvestro et al. 2015 PNAS](http://www.pnas.org/content/suppl/2015/06/23/1502803112.DCSupplemental/pnas.1502803112.sapp.pdf))  
`-m 1` linear correlation.  