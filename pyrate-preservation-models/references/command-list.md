---
title: PyRate: command list
source_url: https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list
language: English
mirrored_from: PyRate-doc/PyRate-wiki/2.-PyRate:-command-list.md
headings: 57
mirror: verbatim local mirror of the PyRate documentation
---
### Input files, working directory
You can find various example files [here](https://github.com/dsilvestro/PyRate/tree/master/example_files). More details about preparing an input file are given [here](https://github.com/dsilvestro/PyRate/wiki/1.-Preparing-input-file).

##### `<input file>`
Set input file including path and file name. The file is a Python file 	with the fossil occurrence data (as list of Numpy arrays) and, optionally, one or more continuous traits. Input files with correct formatting can be generated using the R script `pyrate_utilities.R` (see above).
Example:
`python PyRate.py path_to_input_file/Ursidae_PyRate.py`

##### `-d`
Alternatively to the python input file with occurrence data, users can provide a table with the times of origin and extinction of each species. This option automatically sets `-fixSE = null` (see PyRate command list), meaning that the estimation of preservation rates and times of speciation/extinction are switched off, and the MCMC only samples the birth-death parameters based on the given times of origin and extinction of each species. This option is useful when origination and extinction times are known or have been estimated previously through another PyRate analysis. The table should be formatted as tab-separated text file with the first line containing column headers followed by one row for each species. Each row contains 4 columns: the first column indicates the clade assignment of species, this is only useful in MCDD analyses (Wiki page for PyRateMCDD is under construction) and should be filled with 0s for all other analyses. The second column indicates a species numeric identifier (this values are arbitrary and only used for reference). Finally the third and fourth column contain the time of origin and extinction of each species, respectively. If multiple estimates for these values are available, for instance deriving from previous replicated PyRate analyses, these can be provided as additional columns (e.g. 5th column for a second estimate of origination times, 6th column for a second estimate of extinction times). As in standard PyRate analyses, the replicate number is selected through the command `-j` (see below).
Example:
`python PyRate.py -d path_to_input_file/Ursidae_SE.txt`

#####`-wd`
Define working directory where all output files will be saved. If not specified, output files will be saved in the same directory as the input file.
Example:
`-wd path_to_target_directory`

#####`-j`
If the input file includes several data sets, e.g. generated using the R script `pyrate_utilities.R` to account for uncertainties of fossil ages, this command defines which data set will be analyzed.
Example:
`-j 1`  (default; the first data set from the input file is analyzed)

##### `-out`
Add tag to default stem name of output files. This command is useful to avoid overwriting output files when running several instances of the same analysis.
Example:
`-out run_2`  (adds ‘run_2’ to the name of all output files)

##### `-singleton`
This command can be used to run any analysis after excluding some taxa, such as singletons. If set to 1 it will remove all taxa sampled in a single occurrence prior to running the analysis (see below for more examples). The number of excluded taxa and the number of remaining taxa is printed on screen. This information is also available when using it together with the command [`-data_info`](https://github.com/dsilvestro/PyRate/wiki/3.-Summarize-PyRate-results#-data_info).
Examples:  
`-singleton  1`  (excludes taxa with only 1 sampled occurrence)  
`-singleton  2`  (excludes taxa with 2 or less sampled occurrences)  
`-singleton  -1`  (excludes extant taxa)

***
### Main analysis settings
##### `-A`	
`-A 0` run an MCMC for parameter estimation, i.e. with fixed number of shifts in the birth-death model (see section ‘Birth-death model – constrained shifts’). This analysis generates output files with posterior samples of the parameters, e.g. speciation/extinction/preservation rates and times of rate shifts (see section ‘Description of the output files’ for more details). 

`-A 1` run an MCMC with thermodynamic integration [(TI; Lartillot & Philippe 2006)](http://sysbio.oxfordjournals.org/content/55/2/195.full) to estimate the fit of a birth-death model. This analysis computes the marginal likelihood of a birth-death model (save to a 	‘*_marginal_likelihood.txt’ file) that can be use to compare alternative models, e.g. with different number of rate shifts or trait correlations.

`-A 2` run a BDMCMC analysis [(Stephens 2000)](http://www.jstor.org/stable/2673981?seq=1#page_scan_tab_contents) to jointly estimate the number of rate shifts in the birth-death process, their temporal placement and the speciation and extinction rates between 	shifts. This analysis generates output files with posterior samples of the parameters e.g. preservation rates and speciation/extinction rates through time (see section ‘Description of the output files’).
Example: `-A 2`  (default)

`-A 3` run a MCMC analysis with Dirichlet Process Prior on the speciation and extinction rates within fixed time bins. Warning: this function is currently still being tested.

##### `-n`
Number of MCMC or BDMCMC generations.
Example:`-n 10000000`  (default)

##### `-s`	
MCMC sampling frequency.
Example: `-s 1000`  (default)

##### `-p`	
MCMC print-on-screen frequency.
Example: `-p 1000`

##### `-b`
Set the number of iterations to be discarded (i.e. not logged) from the analysis as burnin. Must be set to a reasonable number when estimating marginal likelihood through TI (see command `-A`). This command is also used to exclude burnin samples when summarizing MCMC results (e.g. [`-mProb`](https://github.com/dsilvestro/PyRate/wiki/3.-Summarize-PyRate-results#-mprob), [`-plot`](https://github.com/dsilvestro/PyRate/wiki/3.-Summarize-PyRate-results#-plot) functions). When set to a number between 0 and 1, it is interpreted as a fraction of the total number of MCMC generations.
Examples:
`-b 0`  (default; all samples are logged) 
`-b 1000`  (first 1,000 samples are discarded) 
`-b 0.10`  (the first 10% of the samples are discarded) 

##### -thread 
Set the number of threads used for calculating the likelihood of the birth-death process and the NHPP likelihood respectively. When both values are set to 0, PyRate will use sequential computation of the likelihood (thus slowing down a bit the analysis) and will not use the multiprocessing python library.  
Examples: 
`-thread 0 0` (default; sequential likelihood calculation)  
`-thread 1 3` (use 1 thread for birth-death, 3 threads for NHPP likelihood)
 

NOTE: Additional commands are provided in the section  ‘Advanced (BD)MCMC settings’.

***
### Preservation (fossilization) model

##### `-mHPP` 
Use homogeneous Poisson process for preservation rates instead of  non-homogeneous Poisson process (NHPP) with ‘hat-shaped’ (PERT)  distributed preservation rates [(Liow et al. 2010)](http://paleobiol.geoscienceworld.org/content/36/2/224.abstract). Note that the NHPP is  used unless differently specified.
Example: `-mHPP`  

##### `-qShift` 
Use time-variable Poisson process for preservation rates (TPP) where preservation rates are constant within a predefined time frame, but can vary across time frames (e.g. geological epochs). To use this model you need to provide a file containing the times that delimit the different epochs (an example is provided [here](https://github.com/dsilvestro/PyRate/blob/master/example_files/epochs_q.txt)). 
Example: `-qShift epochs_q.txt`  

##### `-mG` 
Set the Gamma model, allowing heterogeneity of the mean preservation  rate across the taxa in a data set. Preservation rates under the Gamma  model will be assumed to be distributed according to a gamma  distribution with shape parameter (_alpha_) estimated from the data.
 On most empirical data sets the Gamma model strongly outperforms the  alternative assumption of constant rates, and across-taxa rate  heterogeneity has been shown to Gamma model accounts to some  extent for temporal changes of the preservation rates [(Silvestro et al.  2014)](http://sysbio.oxfordjournals.org/content/63/3/349.long). This option can be applied to the NHPP, HPP, and TPP preservation models.
Example: `-mG`

##### `-ncat` 
Set the number of categories used to obtained the gamma distributed  preservation rates under the Gamma model. Increasing this number will  allow for more variability of the rates across taxa, with comparatively little  effect on the speed of the analysis. This command is used only when  running under a Gamma model of preservation (i.e. with `-mG`).
Example: -ncat 4  (default)

##### `-fixSE` 
Fix the times of speciation and extinction of all taxa based on a previous  analysis. This command can be used to load a ‘mcmc.log’ from which  posterior mean times of speciation and extinction are calculated for all  taxa. PyRate will then run the analysis using these values, i.e. without  estimating them and without calculating the likelihood of the  preservation process (NHPP or HPP), but only sampling the parameters  of the birth-death. If set to `-fixSE null` first and last appearances are  used as fixed times of speciation and extinction. 
Example: `-fixSE /path_to_file/Ursidae.mcmc.log`


***
### Birth-death model – constrained shifts
##### `-mL` 
Set the number of speciation rates through time used in the MCMC (with `-A 0` or `-A 1`). In BDMCMC analyses (`-A 2`) this command is only used to set the number of starting rates.
Example: `-mL 2` (set 2 speciation rates and 1 rate shift)

##### `-mM` 
Set the number of extinction rates through time used in the MCMC (with -A 0 or -A 1). In BDMCMC analyses (-A 2) this command is only used to set the number of starting rates.
Example: `-mM 3` (set 3 extinction rates and 2 rate shifts)

##### `-mC` 
Constrain the time frames of speciation and extinction rates to be equal. This command is only used in birth-death models with at least one rate shift (e.g. with `-mL 2` and `-mM 2`) and
Example: `-mC`

##### `-fixShift` 
Fix number and time based on ages provided in a text file. This should be simply a text file with the ages at which the rate shifts should be fixed (see file ‘epochs.txt’ in PyRate’s example files). When this command is used, the number and temporal placement of the rate shifts is fixed and set identical for both speciation and extinction. This will automatically switch the priors on speciation and extinction rates into half-Cauchy distributions [(Silvestro et al. 2015)](http://onlinelibrary.wiley.com/doi/10.1111/nph.13247/abstract) see also function [-cauchy](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#cauchy). 
Example: `-fixShift path_to_file/epochs.txt`


***
### Settings for trait correlated rates (Covar models)
PyRate implements birth-death models in which speciation and extinction rates change in a lineage-specific fashion as a function of an estimated correlation with a continuous trait. The model is described [here](http://onlinelibrary.wiley.com/doi/10.1111/2041-210X.12263/abstract). If a trait is included in the PyRate [input file](https://github.com/dsilvestro/PyRate/wiki/1.-Preparing-input-file) the trait values will be read directly from the python file when using the command [`-mCov`](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#settings-for-trait-correlated-rates-covar-models). Alternatively, a table with the trait data can be provided as a separate file using the command `-trait_file` (see below). The default prior on the correlation parameters is a normal distribution centered in 0 and with standard deviation = 1. The standard deviation can be modified using the command [`-pC`](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-pc).

##### `-trait_file`
With this command you can provide a table (tab-separated text file) providing trait values for the species in your fossil data set. The first column of the table should include the species names (identical to those used in the PyRate file), the second column provides the trait values ([see example file](https://github.com/dsilvestro/PyRate/blob/master/example_files/Ursidae_bm.txt)). Species for which trait data are not available can be omitted from the table. Alternatively, they can be included in the table with trait value `NA`. These species will be still included in the analysis, but their trait value will be imputed by the MCMC.
Examples:  
`-trait_file path_to_file/Ursidae_SE.txt` correlated speciation rate  

##### `-mCov`
Set Covar models in which the birth-death rates (and preservation rate) vary across lineages as the result of a correlation with a continuous trait, provided as an observed variable, based on estimated correlation parameters (cov_sp, cov_ex, cov_q).
Examples:  
`-mCov 1` correlated speciation rate  
`-mCov 2` correlated extinction rate  
`-mCov 3` correlated speciation and extinction rates  
`-mCov 4` correlated preservation rate  
`-mCov 5` correlated speciation, extinction, preservation rates  

##### `-trait` 
If the input file includes several traits, this command defines which trait will be analyzed.
Example: `-trait 1` (default; it takes first trait)

##### `-logT` 
Define trait value transformation.
Examples:  
`-logT 0` trait is not transformed  
`-logT 1` trait is log_e transformed  
`-logT 2` trait is log10 transformed (default) 




***
### (Hyper)prior settings
##### `-N` 
Set the number of extant species (regardless of whether or not they are included in the fossil occurrence data). This is used to calculate the hyperprior on the speciation and extinction rates, i.e. conditioning on the present known diversity ([Kubo and Iwasa 1995](http://www.jstor.org/stable/2410323?seq=1#page_scan_tab_contents); Equations 12–15 in Silvestro et al. 2014). If set to `-N -1` or if not specified, a gamma prior will be used instead with shape and scale parameters defined by the flags `-pL` and `-pM` (see below). The latter option might be appropriate for clades that have gone extinct or when the current diversity is doubtful. 
Example: `-N 24`

##### `-pL` 
Shape and scale parameters of the gamma distributed prior on the speciation rate, which estimates the expected number of fossil occurrences per lineage per Myr. This command if used only if the number of extant taxa is not specified (i.e. `-N -1`).
Example: `-pL 1.1 1.1`(default)

##### `-pM` 
Shape and scale parameters of the gamma distributed prior on the extinction rate, which estimates the expected number of fossil occurrences per lineage per Myr. This command if used only if the number of extant taxa is not specified (i.e. `-N -1`).
Example: `-pL 1.1 1.1` (default)

##### `-cauchy` 
This command sets half-Cauchy distributions as hyper priors on speciation and extinction rates [(Silvestro et al. 2015)](http://onlinelibrary.wiley.com/doi/10.1111/nph.13247/abstract). Default `-cauchy -1 -1` is applied when different priors are used (e.g. Gamma). Under `-cauchy 0 0` (which is default when using [`-fixShift`](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-fixshift)) the scale parameters will
be inferred form the data. Under `-cauchy x y` (where x, y >0), scale parameters will be set to x (for speciation rates) and y (for extinction rates).

##### `-pP` 
Shape and scale parameters of the gamma distributed prior on the preservation rate, which estimates the expected number of fossil occurrences per lineage per Myr.
Example: `-pP 1.5 1` (default)

##### `-pS` 
Shape parameter of the Dirichlet prior on the length of the time frames relative to the total time span of the data set. If set to `-pS 1` the prior is a uniform distribution, whereas big values will favor equal sized time frames.
Example: `-pS 2.5` (default)

##### `-pC` 
Standard deviation of the Normal prior on the correlation parameters under the [Covar model](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#settings-for-trait-correlated-rates-covar-models). The Normal priors are centered in 0. If set to 0, the standard deviation is assigned a Gamma hyper-prior G(2,2) and estimated from the data. This option should only be used if at least 2 correlation parameters are being estimated, i.e. using [`-mCov 2` or `-mCov`](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-mcov).
Example: `-pC 1` (default)


***
### Advanced (BD)MCMC settings
##### `-r` 
Set the number of parallel ‘heated’ chains for Metropolis Coupled MCMC (MC3) analysis. Each chain will use a different processor if available. The number includes the ‘cold’ chain. This command is used only when running MCMC analysis for parameter estimation (i.e. with `-A 0`).
Example: `-r 4` (for 1 cold and 3 heated chains)

##### `-t` 
Set the ‘temperature’ parameter for the MC3 heated chains. This command is used only when running MC3 analysis (i.e. with `-r >1`).
Example: `-t 0.03` (default)

##### `-sw` 
Frequency of attempted swaps between chains in MC3 analysis. This command is used only when running MC3 analysis (i.e. with `-r >1`).
Example: `-sw 100` (default)

##### `-k` 
Number of scaling factors used for marginal likelihood estimation in TI. Higher number of scaling factors will improve the accuracy of the estimated marginal likelihood, but require longer computational time. This command is used only when running TI analysis (i.e. with `-A 1`).
Example: `-k 10` (default)

##### `-a` 
Shape parameter of the beta distributed scaling factors in TI analyses [(cf. Xie et al. 2011)](http://sysbio.oxfordjournals.org/content/60/2/150.long). This command is used only when running TI analysis (i.e. with `-A 1`). 
Example: `-a 0.3` (default)

##### `-M` 
Frequency of model update in BDMCMC analysis. This parameter determines how frequently new birth-death models will be explored. Reducing this number can improve the sampling of the number of shifts in birth-death rates. This command is used only when running BDMCMC analysis for parameter estimation (i.e. with `-A 2`).
Example: `-M 25` (default)

##### `-B` 
Set the birth-rate at which the BDMCMC algorithm will propose new rate shifts in the model. This also corresponds to the shape parameter a Poisson distributed prior on the number of speciation/extinction rates in the model. This command is used only when running BDMCMC analysis for parameter estimation (i.e. with `-A 2`).
Example: `-B 1` (default)

##### `-T` 
Set the time spent in updating the model in BDMCMC analysis. Increasing this parameter has a similar effect to increasing the birth-rate (command `-B`). This command is used only when running BDMCMC analysis for parameter estimation (i.e. with `-A 2`).
Example: `-T 1` (default)

##### `-S`
Set the number of generations after which the BDMCMC algorithm will start updating the model (e.g. after a burn-in phase). This command is used only when running BDMCMC analysis for parameter estimation (i.e. with `-A 2`).
Example: `-S 1000` 

***
### Tuning parameters
##### `-multiR` 
Set proposal mechanism for updates of speciation and extinction rates. When `-multiR 0` updates are done using sliding window, whereas `-multiR 1` sets multiplier proposals. Window sizes can be adjusted using [`-tR`](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-tr).
Example: `-multiR 1` (default)

##### `-tT` 
Window size of updates of speciation/extinction times (uniform sliding window).
Example: `-tT 1` (default)

##### `-nT` 
Maximum number of speciation/extinction times updated at a time. If set to 0, speciation/extinction times are set equal to first/last appearances and the preservation model is automatically set to HPP.
Example: `-nT 5` (default)

##### `-tQ` 
Window sizes of the preservation rate (q) and of the shape parameter of the gamma distributed rate heterogeneity (alpha), respectively (multiplier proposals).
Example: `-tQ 1.2 1.2` (default)

##### `-tR` 
Window size of updates of speciation/extinction rates (by default multiplier proposals, see also [`-multiR`](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-multir)).
Example: `-tR 0.05` (default)

##### `-tS` 
Window size of updates of shift times for speciation/extinction rates (uniform sliding window).
Example: `-tS 1` (default)

##### `-fS`
Frequency of updating shift times, when updating birth-death parameters (else rates are updated). The value will be automatically set to 0 when no rate shifts are being sampled or if the times of shifts are fixed (with command [`-fixSE`](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-fixse)).
Example: `-fS 0.7` (default)

##### `-tC` 
Window sizes of updates of correlation parameters, when using models with rates covarying with a trait. Window sizes are given for covariation with speciation, extinction, and preservation rates respectively. The parameters will be updated (or not) depending on the Covar model selected (see command [`-mCov`](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-mcov)).
Example: `-tC 0.025 0.025 0.1` (default)

##### `-fU` 
Update frequencies for preservation rate, birth-death parameters, and correlation parameters under the Covar model, respectively. What is left is used for updating speciation and extinction times.
Example:` -fU 0.02 0.18 0.08` (default under Covar model; updates preservation parameters with frequency 2%, birth-death parameters with frequency 18%, Covar parameters with frequency 8%, times of speciation and extinction with frequency 72%)

##### `-fR` 
Fraction of birth-death rates updated at a time (with frequency defined by the command `-fU`). This command should be used to reduce the fraction of updated rate parameters especially when running birth-death models with many shifts, e.g. defined by the command [`-fixShift`](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-fixshift), to improve the MCMC mixing.
Example: `-fR 1` (default)