---
title: PyRate Manual
source_url: https://github.com/dsilvestro/PyRate/wiki/Home
language: English
mirrored_from: PyRate-doc/PyRate-wiki/Home.md
headings: 8
mirror: verbatim local mirror of the PyRate documentation
---
<img src="../../assets/images/PyRate_logo1024.png" align="left" width="80">  
  

# PyRate Manual  

### Please refer to the [TUTORIALS](https://github.com/dsilvestro/PyRate/tree/master/tutorials#pyrate-tutorials---index) for updated documentation.


**PyRate is a Python program to estimate macroevolutionary rates from fossil occurrence data using a Bayesian framework.** It includes several methods to infer **speciation, extinction, and dispersal rates**, how they vary through time and whether they correlate with **traits** (e.g. body size) or respond to **continuous variables** (e.g. climate proxies) or **competitive effects** (through diversity dependence). Macroevolutionary rates are jointly estimated with **preservation rates**, describing processes of fossilization, sampling and identification of organisms. 

Installation and requirements are described [here](https://github.com/dsilvestro/PyRate/wiki#compatibility-and-installation). For questions, suggestions or bugs **[contact us](mailto:pyrate.help@gmail.com)**!


**The PyRate package includes several programs implementing different models. Simple tutorials demonstrating the most important features are available [here](https://github.com/dsilvestro/PyRate/tree/master/tutorials)**

PyRate is licensed under a [AGPLv3 License](https://tldrlegal.com/license/gnu-affero-general-public-license-v3-(agpl-3.0)#summary).

***

#### `PyRate.py` 
PyRate.py implements the main functions to infer speciation and extinction rates through time and preservation rates (commands and options are detailed [here](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list)). It also includes a model to infer [trait dependent speciation and extinction](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#settings-for-trait-correlated-rates-covar-models). 
A standard PyRate analysis requires three steps: (1) Prepare an [input file](https://github.com/dsilvestro/PyRate/wiki/1.-Preparing-input-file); (2) launch PyRate providing an [input file](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#input-files-working-directory) and [analysis settings](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#main-analysis-settings); and (3) [Summarize](https://github.com/dsilvestro/PyRate/wiki/3.-Summarize-PyRate-results) the results and generate [rates-through-time plots](https://github.com/dsilvestro/PyRate/wiki/3.-Summarize-PyRate-results#plotsummarize-results). **A tutorial is available [here](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_1.md#pyrate-tutorial-1).**  
The main methods implemented in and the program are described here:

Silvestro, D., Schnitzler, J., Liow, L.H., Antonelli, A. & Salamin, N. (2014) _Bayesian Estimation of Speciation and Extinction from Incomplete Fossil Occurrence Data_. Systematic Biology, 63, 349–367.

Silvestro, D., Salamin, N., Schnitzler, J. (2014) _PyRate: A new program to estimate speciation and extinction rates from incomplete fossil record_. Methods in Ecology and Evolution, 5, 1126–1131

---  

#### `PyRateContinuous.py` [requires library [pyrate_lib](https://github.com/dsilvestro/PyRate/wiki#pyrate_lib)]
This program implements a birth-death model in which rates vary through time through linear or exponential correlations with a time continuous variable. A [detailed command list is in preparation](https://github.com/dsilvestro/PyRate/wiki/4.-PyRateContinuous). The model implemented here is described in:

Silvestro D., Antonelli A., Salamin N., Quental T. B. (2015) The role of clade competition in the diversification of North American canids. PNAS, 112, 8684-8689.

---

#### `PyRateMCDD.py` [requires library [pyrate_lib](https://github.com/dsilvestro/PyRate/wiki#pyrate_lib)]
This program implements a Multiple Clade Diversity Dependence model (MCDD) in which speciation and extinction rates may change through time as the result of diversity dependence effects within and between clades. A detailed command list is in preparation. The MCDD model is described here:

Silvestro D., Antonelli A., Salamin N., Quental T. B. (2015) The role of clade competition in the diversification of North American canids. PNAS, 112, 8684-8689.

---

#### `PyRateDES.py` [requires library [pyrate_lib](https://github.com/dsilvestro/PyRate/wiki#pyrate_lib)]
This program implements a Dispersal Extinction Sampling model (DES), which uses fossil occurrences in two discrete areas to estimate rates of dispersal between areas and rates of local extinction within areas, while incorporating sampling biases. Correctly formatted input files can be generated using the script `DES_input_preparation.R` as described [here](https://github.com/dsilvestro/PyRate/wiki/5.-Dispersal-Extinction-Sampling-model). A detailed command list is in preparation. The MCDD model is described here:

Silvestro, D., Zizka A., Bacon C. D., Cascales-Minana B. and Salamin, N., Antonelli, A. (2016) Fossil Biogeography: A new model to infer dispersal, extinction and sampling from paleontological data. Phil Trans Roy Soc B, doi: 10.1098/rstb.2015.0225.

---

#### `pyrate_lib` 
The library [pyrate_lib](https://github.com/dsilvestro/PyRate/tree/master/pyrate_lib)] contains various functions that are used by several PyRate programs. The library does not require any installation. Simply, **when you run a program requiring `pyrate_lib` (e.g. [`PyRateContinuous`](https://github.com/dsilvestro/PyRate/wiki#pyratecontinuouspy-requires-library-pyrate_lib)), the folder `pyrate_lib` needs to be in the same directory as the program**. 

***




## Compatibility and installation
PyRate has been tested under Unix operating systems (Mac OS 10.6 or higher and Cent OS 6) and under Windows (XP and 7) using Python 2.6 – 2.7. The program requires the library argparse, which needs to be installed manually under Python 2.6 (it can be found here: https://code.google.com/p/argparse/), whereas it is part of the default installation in Python 2.7. **Please note that Python 3.x is currently not supported, Python 2.7.x can be found here: https://www.python.org/downloads/.**

The libraries numpy and scipy are required. Source files and installers are available here: http://sourceforge.net/projects/numpy/files/ and http://sourceforge.net/projects/scipy/files/. Alternatively, you can download the requirements.txt [file](https://github.com/dsilvestro/PyRate/blob/master/requirements.txt) and use `pip install -r requirements.txt` to install them from Terminal (UNIX systems). Under UNIX systems, PyRate will use the library multiprocessing and thread (if available) and implement parallel computation of the likelihoods (see command -thread). 


To launch a PyRate analysis on UNIX browse via Terminal to the PyRate directory and type:
`./PyRate.py path_to_input_file/file_name.py [commands]`
or 
`python PyRate.py path_to_input_file/file_name.py [commands]`

To start PyRate on Windows, browse via Command prompt to the PyRate directory and type:
`python PyRate.py path_to_input_file/file_name.py [commands]`

If you are using Windows, please make sure that the path to python.exe is included in the PATH environment variables. To do so, edit the PATH environment variable and add the folder in which Python 2.x is installed (e.g. ‘C:\python27’). An easy tutorial how to do that can be found for example on the Java website: https://www.java.com/en/download/help/path.xml 

The function [`-plot`](https://github.com/dsilvestro/PyRate/wiki/3.-Summarize-PyRate-results) generates an R script that is used to produce a graphic output. The script is automatically executed by PyRate using the shell command `RScript`. If you are using Windows, please make sure that the path to Rscript.exe is included in the PATH environment variables (default in Mac/Linux). To do so, edit the PATH environment variable and add the \bin\ folder of the R installation (e.g. ‘C:\Program Files\R\R-2.14.0\bin\i386’). An easy tutorial how to do that can be found for example on the Java website: https://www.java.com/en/download/help/path.xml 

The R script pyrate_utilities.r was tested under R version 2.x and 3.x. The function `fit.prior` requires the package fitdistrplus.