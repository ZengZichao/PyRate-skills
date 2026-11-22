---
name: pyrate-installation
description: "Build and verify a working PyRate runtime and tell when you do not have one. Covers the virtual-environment tutorial (python -m venv, py -m venv, source pyrate_env/bin/activate, pyrate_env Scripts activate, ensurepip --upgrade, pip install --upgrade pip, pip install -r PyRate-master/requirements.txt, PyRate.py -v) and the wiki Compatibility and installation page (Python 2.6-2.7 vs 3.10+, python3, argparse on 2.6, numpy, scipy, multiprocessing, thread, -thread 0 0 sequential vs parallel likelihood). Owns pyrate_lib adjacency for PyRateContinuous.py, PyRateMCDD.py, PyRateDES.py; the R side (pyrate_utilities.r, extract.ages(.pbdb), fit.prior needing fitdistrplus, DES_input_preparation.R, R 2.x/3.x, the RScript shell command behind -plot and -plot_raw); Windows PATH for python.exe, Python312 Scripts, Rscript.exe; UNIX ./PyRate.py vs python PyRate.py; example_files; Module FastPyRateC was not found.; plus a pre-flight check (python -V, numpy/scipy importable, Rscript on PATH, pyrate_lib adjacent, check_env.py)."
---

# PyRate installation: getting a working runtime, and proving you have one

## Overview

PyRate is "a Python program to estimate macroevolutionary rates from fossil occurrence data using a Bayesian framework" (`references/home.md`:17), shipped as a source tree (`PyRate-master/`) whose programs are launched by hand: `python PyRate.py path_to_input_file/file_name.py [commands]` (`references/home.md`:77,80). Neither install page prints an installer, a package-manager name for PyRate itself (`conda`, `pip install PyRate` — absent from both mirrors, and from every mirror in this corpus), or a build step: the documented install story is (a) one tutorial page, `references/virtual-environment.md` (upstream `tutorials/pyrate_tutorial_0.md`), which builds a virtual environment and installs `requirements.txt` into it, and (b) one wiki section, "Compatibility and installation" at `references/home.md`:68-86. Almost every other runtime fact this skill uses — `pyrate_lib` placement, the `RScript` shell command behind `-plot`, Windows `PATH` — sits inside those two blocks. The three exceptions are cited from the sibling mirrors that print them: `-plot_raw` also needs R (`../pyrate-des/references/tutorial-5.md`:95), `-plot` outputs (`../pyrate-summarize-results/references/summarize-results.md`:40), and how to load `pyrate_utilities.r` (`../pyrate-input-file/references/tutorial-1.md`:31).

The single riskiest assumption this skill exists to remove: **the interpreter you type is not necessarily the interpreter PyRate runs on, and the corpus gives two mutually exclusive answers about which one is correct.** `references/home.md`:69 states "**Please note that Python 3.x is currently not supported, Python 2.7.x can be found here: https://www.python.org/downloads/.**" while `references/virtual-environment.md`:13 states the opposite requirement ("First, make sure **Python (v.3.10 or higher)** is installed on your computer"). Both statements are reproduced faithfully by the Chinese twins (`references/home-cn.md`:70, `references/virtual-environment-cn.md`:14), so translation cannot arbitrate; see "Which Python?" below for the documented tie-breaker and the pre-flight checklist for detecting which runtime you actually have.

## The nine things that break a run

| # | What happens | Consequence | Wiki wording (mirror:line) |
| --- | --- | --- | --- |
| 1 | You follow one install page and ignore the other | A 2.7 interpreter (Home) or a 3.x interpreter (tutorial) — the two pages each deem the other's runtime unusable, and neither names a version that both accept | `references/home.md`:69 "Python 3.x is currently not supported" vs `references/virtual-environment.md`:13 "Python (v.3.10 or higher)" |
| 2 | Steps 3-4 are run before step 2, i.e. the venv was never activated | `ensurepip`/`pip install` mutate your system environment, and `python` still resolves outside `pyrate_env`; PyRate then runs on whatever the shell finds | the tutorial's own reason for the venv: "to make sure all the compatible dependencies are included without affecting your system Python installation" (`references/virtual-environment.md`:14) |
| 3 | The doc placeholders are copied literally (`desired_path_to_env`, `your_path`) | `python -m pip install -r your_path/PyRate-master/requirements.txt` cannot resolve, so nothing gets installed and every later step fails on a missing module — the docs require you to edit them ("after replacing `your_path` with the correct path to the `PyRate-master` directory", `references/virtual-environment.md`:39) | `references/virtual-environment.md`:19,31,36,39,44 |
| 4 | `python -m ensurepip --upgrade` is skipped | `pip` is then absent from the new environment, so the `requirements.txt` step cannot run at all — *consequence by inference*: the tutorial prints the three commands in one fenced block, in that order, and never explains what `ensurepip` does (`references/virtual-environment.md`:42-44) | `references/virtual-environment.md`:42-44 (three commands printed in one block, in order) |
| 5 | numpy and/or scipy are not importable in that interpreter | The library requirement named by the wiki is unmet; the page calls both required and prints no error text for their absence | "The libraries numpy and scipy are required." (`references/home.md`:71) |
| 6 | Under Python 2.6, `argparse` is missing | The requirement stands until you install it by hand; 2.6 does not bundle it, 2.7 does. The docs never say *what* argparse does — calling it "the command-line parser" is your own knowledge, not the wiki's | "The program requires the library argparse, which needs to be installed manually under Python 2.6 (it can be found here: https://code.google.com/p/argparse/), whereas it is part of the default installation in Python 2.7." (`references/home.md`:69) |
| 7 | `pyrate_lib` is not next to the program you launch | `PyRateContinuous.py`, `PyRateMCDD.py`, `PyRateDES.py` — the three programs whose `home.md` headings carry the pyrate_lib requirement (`:39`,`:46`,`:53`) — are run without a library they state they need. *The docs print no error message for this case*, so a traceback naming a missing local module is the evidence, not a quoted string; and "The library does not require any installation." means placement is the entire install step | `references/home.md`:61 — "the folder `pyrate_lib` needs to be in the same directory as the program" (headings at `:39`,`:46`,`:53`) |
| 8 | `-plot` produces no graphic on Windows | The plot step is a shell-out, not a Python code path: PyRate writes an R script and executes it through the shell command the docs print as `RScript`, so `R`'s bin folder must be reachable — *what happens when it is not is not printed anywhere*; only the requirement is documented | "The function -plot generates an R script that is used to produce a graphic output. The script is automatically executed by PyRate using the shell command `RScript`." (`references/virtual-environment.md`:55; `references/home.md`:84 prints the same sentence with `-plot` as a hyperlink) |
| 9 | `Module FastPyRateC was not found.` is read as a failed install | Wrong triage: the run is valid, only slower; the fast C library is optional and installed separately | "In case the message `Module FastPyRateC was not found.` appears the program will still run but use a slower implementation for some of the functions." (`references/virtual-environment.md`:52) |

## Which Python? the corpus answers twice

| Statement | Where | Scope as printed |
| --- | --- | --- |
| "PyRate has been tested under Unix operating systems (Mac OS 10.6 or higher and Cent OS 6) and under Windows (XP and 7) using Python 2.6 – 2.7." + "Please note that Python 3.x is currently not supported, Python 2.7.x can be found here: https://www.python.org/downloads/." | `references/home.md`:69 (CN `references/home-cn.md`:70) | wiki Home, section "Compatibility and installation"; the only place that bans 3.x |
| "First, make sure **Python (v.3.10 or higher)** is installed on your computer." | `references/virtual-environment.md`:13 (CN `:14`) | tutorial `pyrate_tutorial_0.md`, the install page the tutorials index lists first |
| "Note that depending on the default version of Python on your machine you may have to type `python3`." | `references/virtual-environment.md`:26 (CN `:27`) | the tutorial's only nod to interpreter naming |
| Windows PATH examples: "the folder in which Python 2.x is installed (e.g. ‘C:\python27’)" vs "the folder in which Python 3.x is installed (e.g. `'C:\...\Python\Python312'`)" | `references/home.md`:82 vs `references/virtual-environment.md`:54 | the two pages even print different install-dir examples |

How to reconcile what the corpus itself says, and nothing more:
- **Documented tie-breaker:** the wiki Home page points away from itself for current information — "### Please refer to the [TUTORIALS](https://github.com/dsilvestro/PyRate/tree/master/tutorials#pyrate-tutorials---index) for updated documentation." (`references/home.md`:14, CN `:15`), and the install tutorial is that index's first entry (`../pyrate/references/tutorials-index.md`:17, "Install PyRate and dependencies in a virtual environment"). By that pointer the 3.10+ requirement is the current instruction and `home.md`:69's 2.x text is the older wiki page that the same page admits is superseded. **Label: this ordering is inferred** from `home.md`:14; no mirror anywhere states that the Python 2.x requirement was dropped, in which release, or on what date.
- **What is not resolved:** no mirror states a Python version that satisfies both pages, no mirror gives a PyRate release number attached to either requirement, and no mirror prints the contents of `requirements.txt` (which is what would actually settle which interpreter can install the dependencies). Treat the version question as an environment observation, not as doc exegesis: run `python -V` and `python PyRate.py -v` and record what the program says (see the pre-flight below). If a 3.x interpreter cannot run the tree you were given, that is `home.md`:69's claim being exercised, and it belongs in your report, not in a guess.

## The install sequence exactly as the tutorial prints it

| Step | Command (verbatim) | Platform | Line of `references/virtual-environment.md` |
| --- | --- | --- | --- |
| 0 | prerequisite sentence: "First, make sure **Python (v.3.10 or higher)** is installed on your computer." | all | `:13` |
| 1 | `python -m venv desired_path_to_env/pyrate_env` | terminal console | `:19` |
| 1b | `py -m venv desired_path_to_env/pyrate_env` | "or on Windows" | `:24` |
| 2 | `source desired_path_to_env/pyrate_env/bin/activate` | "using on MacOS/UNIX" | `:31` |
| 2b | `.\desired_path_to_env\pyrate_env\Scripts\activate` | "or on Windows" | `:36` |
| 3 | `python -m ensurepip --upgrade` | all ("on Windows use `py` instead of `python`", `:39`) | `:42` |
| 3 | `python -m pip install --upgrade pip` | all | `:43` |
| 3 | `python -m pip install -r your_path/PyRate-master/requirements.txt` | all | `:44` |
| 4 | `python your_path/PyRate-master/PyRate.py -v` — "You can check that PyRate can now be run in your virtual environment using:" | all | `:47-49` |
| note | `Module FastPyRateC was not found.` → still runs, slower implementation; fastPyRateC installed from `pyrate_lib/fastPyRateC/README.md` (URL as printed) | all | `:52` |
| 4 | Windows `PATH`: add "the folder in which Python 3.x is installed (e.g. `'C:\...\Python\Python312'`)" **and** "the folder with the Python scripts (e.g. `'C:\...\Python\Python312\Scripts'`)" | Windows | `:54` |
| 4 | Windows `PATH`: add "the \bin folder of the R installation (e.g. `'C:\Program Files\R\R-4.4.1\bin'`)" for `Rscript.exe` | Windows | `:55` |

The wiki adds the older, non-venv route in the same breath as its requirements: "Alternatively, you can download the requirements.txt [file](https://github.com/dsilvestro/PyRate/blob/master/requirements.txt) and use `pip install -r requirements.txt` to install them from Terminal (UNIX systems)." (`references/home.md`:71) — note it is scoped "(UNIX systems)" there, while the tutorial applies the equivalent command on every platform inside a venv (`references/virtual-environment.md`:44).

## Dependencies

| Requirement | Stated by | How the docs say to get it | When its absence bites |
| --- | --- | --- | --- |
| Python 3.10+ **or** 2.6-2.7 (contradicted) | `virtual-environment.md`:13 / `home.md`:69 | download from python.org (both pages print the same URL, `https://www.python.org/downloads/`) | before anything else |
| pip | `virtual-environment.md`:42-43 | `python -m ensurepip --upgrade`, then `python -m pip install --upgrade pip` | step 3 cannot run |
| `requirements.txt` | `virtual-environment.md`:44; `home.md`:71 | `python -m pip install -r your_path/PyRate-master/requirements.txt` (tutorial) or `pip install -r requirements.txt` (wiki) — the file sits at the root of `PyRate-master` | the doc's one-line way to get "all the compatible dependencies" (`virtual-environment.md`:14) |
| numpy | `home.md`:71 | source files/installers at `http://sourceforge.net/projects/numpy/files/`, or `requirements.txt` | import failure at launch; also the input format depends on it — the input file is "a Python file" holding "the fossil occurrence data (as list of Numpy arrays)" (`../pyrate-command-reference/references/command-list.md`:13) |
| scipy | `home.md`:71 | `http://sourceforge.net/projects/scipy/files/`, or `requirements.txt` | import failure at launch |
| argparse | `home.md`:69 | "needs to be installed manually under Python 2.6 (it can be found here: https://code.google.com/p/argparse/)"; "part of the default installation in Python 2.7" | only relevant on the 2.x reading |
| multiprocessing, thread | `home.md`:71 | no install step is documented for either; the wiki only says PyRate "will use the library multiprocessing and thread (if available)" | graceful, by inference: with no threads the likelihood is computed sequentially (see `-thread`); no mirror prints an error for their absence |
| fastPyRateC | `virtual-environment.md`:52 | optional; instructions URL `https://github.com/dsilvestro/PyRate/blob/master/pyrate_lib/fastPyRateC/README.md` | performance only |
| `pyrate_lib` | `home.md`:60-61 | "The library does not require any installation." — placement, not installation | see the programs table below |
| R + `Rscript` | `home.md`:84; `virtual-environment.md`:55 | install R; on Windows add its `\bin` to `PATH` | `-plot` / `-plot_raw` produce no graphic |
| R package fitdistrplus | `home.md`:86 | not stated | "The function `fit.prior` requires the package fitdistrplus." |
| `pyrate_utilities.r` | `home.md`:86; `../pyrate-input-file/references/tutorial-1.md`:31 | shipped with the package — "the R utilities script provided with PyRate package" (`../pyrate-input-file/references/preparing-input-file.md`:26); loaded with `source(".../PyRate-master/pyrate_utilities.r")` | input-file generation and `fit.prior` |
| `DES_input_preparation.R` | `home.md`:54; `../pyrate-des/references/des-model.md`:21 (`source(DES_input_preparation.R)`) | **not documented** — `home.md`:54 only says input files "can be generated using the script `DES_input_preparation.R`", and no mirror says where the script comes from | DES input-file preparation |
| `nlopt` (Python) | `../pyrate-des/references/tutorial-5.md`:175 (CN twin same line: "PyRateDES 需要 Python 库 *nlopt* 来以最大似然（Maximum likelihood）拟合模型") | the one spelling and the one install command the corpus gives: "PyRateDES requires the Python library *nlopt* for fitting models with Maximum likelihood. It can be installed with `pip install nlopt`." — **no version is stated anywhere**, and it is not part of `requirements.txt` in any page | DES maximum-likelihood fitting, which tutorial 5 reaches with `-A 3`: "The same DES model can be fitted with Maximum likelihood by setting the algorithm to `-A 3` instead of using the default `-A 0`" (`../pyrate-des/references/tutorial-5.md`:197). Two gaps to report rather than paper over: no page says nlopt is needed for the default `-A 0` Bayesian route, and no page says whether `requirements.txt` already carries it (the file's contents are never printed — see *Not documented*), so `python -c "import nlopt"` is the only honest test |
| `Dendropy` (Python; spelled `Dendropy` by the docs, project name DendroPy) | `../pyrate-trait-age-models/references/tutorial-4.md`:160 (CN `../pyrate-trait-age-models/references/tutorial-4-cn.md`:161) | only a hyperlink, no command and no version: "Note that this function requires the [Dendropy library](https://dendropy.org)." | the BDC joint analysis of fossils + a tree, i.e. `-tree`: the sentence sits directly under `python PyRate.py example_files/BDC_model/Feliformia.py -tree example_files/BDC_model/Feliformia.tre` (`../pyrate-trait-age-models/references/tutorial-4.md`:158). "this function" is defined by adjacency only — no page names the flag in the requirement sentence, and no page lists Dendropy as a `PyRate.py` dependency for any other command, so do not install-broaden it beyond a `-tree`/`-bdc` run |

### numpy 2.x: every documented check passes and `PyRateDES.py` still dies

`home.md`:71 makes numpy a hard requirement ("The libraries numpy and scipy are required.") and `virtual-environment.md`:44 gets it for you with `python -m pip install -r your_path/PyRate-master/requirements.txt`. No page prints that file's contents and no page states a version bound (see *Not documented*), so which numpy you end up with is a property of your checkout rather than of the docs — and a current one is incompatible with the DES code path.

Observed on this machine (2026-11-20) against the upstream `dsilvestro/PyRate` master tree the wiki links — a machine fact, not a statement of the corpus:

| environment | `PyRate.py` | the command `../pyrate-des/references/tutorial-5.md`:63 prints |
| --- | --- | --- |
| `pip install -r requirements.txt` as written (numpy 2.5.5, scipy 1.18.1) | works — `-j 1` runs and prints MCMC lines | fails, exit code 1, `ValueError: The truth value of an empty array is ambiguous`, raised by `if trim_age > 0:` at `pyrate_lib/lib_utilities.py`:585 inside `des_in` (that line tests `np.array(trim_age)`, which is empty when no trim value was passed); **0** of the `-rep 10` input files get written |
| the same tree with numpy pinned to 1.26.4 and scipy to 1.13.1 | works | exit code 0, all 10 replicate files written |

Two consequences for how you verify a runtime. First, pre-flight row 5 (`python -c "import numpy, scipy"`) passing is *not* evidence of a working PyRate: the import succeeds and the failure only surfaces when the DES generator runs, so a DES job needs the generator itself as the smoke test. Second, the empty output directory is the symptom of this crash, not a path or `-wd` problem — do not go debugging `Carnivora_1.txt` into the input tables; the fix is the numpy version. When you report it, say it is an observation on your machine: the corpus never mentions a numpy upper bound, so it neither recommends nor forbids the pin.

## The R side

| Fact | Wording / value | Where |
| --- | --- | --- |
| `-plot` is a shell-out, not a Python routine | "The function -plot generates an R script that is used to produce a graphic output. The script is automatically executed by PyRate using the shell command `RScript`." | `virtual-environment.md`:55; `home.md`:84 prints the same sentence with `-plot` turned into a wiki hyperlink, so the byte-exact quote above is the tutorial's version |
| The executable's name | the sentence above prints the shell command as `RScript`, while the same two sentences require "the path to Rscript.exe" in `PATH` — keep both spellings as printed; on a case-sensitive Unix filesystem the binary is `Rscript` (by inference from the two spellings in `home.md`:84; no mirror discusses case) | `home.md`:84, `virtual-environment.md`:55 |
| Mac/Linux need nothing | "(default in Mac/Linux)" for the `Rscript` path | `home.md`:84, `virtual-environment.md`:55 |
| Windows `PATH` value | `home.md`:84 "add the \bin\ folder of the R installation (e.g. ‘C:\Program Files\R\R-2.14.0\bin\i386’)" vs `virtual-environment.md`:55 "add the \bin folder of the R installation (e.g. `'C:\Program Files\R\R-4.4.1\bin'`)" — same rule, two different example R versions, and only the wiki's example carries `\i386` | both cited |
| R versions the utilities were validated on | "The R script pyrate_utilities.r was tested under R version 2.x and 3.x." — no mirror tests R 4.x, yet the newer tutorial's PATH example is an R 4.4.1 directory; the two are not reconciled anywhere in this corpus | `home.md`:86 vs `virtual-environment.md`:55 |
| R functions PyRate relies on | `extract.ages` — heading at `../pyrate-input-file/references/preparing-input-file.md`:30, example call at `:52`; `extract.ages.pbdb` — `../pyrate-input-file/references/tutorial-1.md`:37 (the pbdb variant is **not** documented on the preparing-input-file page); `fit.prior` needs fitdistrplus — `home.md`:86 | siblings |
| Other plot commands needing R | `-plot_raw`: "This requires that R is installed on your PC to execute the shell command Rscript." | `../pyrate-des/references/tutorial-5.md`:95, `:354` |
| What `-plot` writes once R is reachable | an R script `*_RTTplot.r` and a pdf `*_RTTplot.pdf` | `../pyrate-summarize-results/references/summarize-results.md`:40 (semantics owned by `pyrate-summarize-results`) |

## Programs, and where `pyrate_lib` must sit

| Program | Tag on the wiki | `pyrate_lib` | Notes printed by the docs |
| --- | --- | --- | --- |
| `PyRate.py` | `home.md`:28 — its heading carries no pyrate_lib requirement | not stated for this program (by inference from the tag's absence; no mirror says PyRate.py does not need it) | "commands and options are detailed [here]" → command list; launched as `python PyRate.py <input.py> [commands]` (`home.md`:77,80) |
| `PyRateContinuous.py` | `home.md`:39 heading, with the pyrate_lib requirement | **required, adjacent** | linear/exponential correlation of rates with a continuous variable (`home.md`:40) |
| `PyRateMCDD.py` | `home.md`:46 heading, with the pyrate_lib requirement | **required, adjacent** | Multiple Clade Diversity Dependence (`home.md`:47) |
| `PyRateDES.py` | `home.md`:53 heading, with the pyrate_lib requirement | **required, adjacent** | Dispersal Extinction Sampling; inputs via `DES_input_preparation.R` (`home.md`:54) |
| `pyrate_lib` | `home.md`:60-61 | — | "The library does not require any installation." and then the placement rule itself: "the folder `pyrate_lib` needs to be in the same directory as the program" |
| `pyrate_utilities.r` | `home.md`:86 | — | R utilities, tested under R 2.x/3.x; `fit.prior` → fitdistrplus |

The placement rule names *the program's* directory, not the current working directory — so a copy of `PyRateDES.py` moved elsewhere without `pyrate_lib` beside it breaks a requirement the wiki states in as many words, even though it prints no error message for the case; and launching a program through a relative path from some other working directory (e.g. `python <parent>/PyRate-master/PyRateDES.py`) is addressed by no mirror at all (see "Not documented").

## Launching, working directory, example_files

| Form | Printed as | Where |
| --- | --- | --- |
| UNIX, direct | `./PyRate.py path_to_input_file/file_name.py [commands]` — "To launch a PyRate analysis on UNIX browse via Terminal to the PyRate directory and type:" | `home.md`:74-75 (CN `:75-76`) |
| UNIX, via interpreter | `python PyRate.py path_to_input_file/file_name.py [commands]` | `home.md`:77 |
| Windows | `python PyRate.py path_to_input_file/file_name.py [commands]` — "browse via Command prompt to the PyRate directory" | `home.md`:79-80 |
| venv check | `python your_path/PyRate-master/PyRate.py -v` | `virtual-environment.md`:49 |
| other programs | `python PyRateContinuous.py …` (`../pyrate-continuous-covariates/references/pyratecontinuous.md`:16), `PyRateMCDD.py -d …` (`../pyrate-diversity-dependence/references/tutorial-4.md`:34 — printed **without** a `python` prefix), `python ./PyRateDES.py …` (`../pyrate-des/references/tutorial-5.md`:63) | siblings |

- Both UNIX forms appear in the same paragraph; the docs print no difference in behaviour between them and never mention a file-permission requirement for the `./PyRate.py path_to_input_file/file_name.py` form.
- Input paths are written relative to the PyRate root in the tutorials (`./example_files/…`, `.../PyRate-master/example_files/…`) and with an explicit `-wd` for outputs: "Define working directory where all output files will be saved. If not specified, output files will be saved in the same directory as the input file." (`../pyrate-command-reference/references/command-list.md`:23).
- Example data: "You can find various example files [here](https://github.com/dsilvestro/PyRate/tree/master/example_files)" (`../pyrate-command-reference/references/command-list.md`:10); the specific files the corpus links are `example_files/epochs_q.txt` (`:92`), `example_files/Ursidae_bm.txt` (`:133`), `example_files/temperature.txt` (`../pyrate-continuous-covariates/references/pyratecontinuous.md`:32), `example_files/Carnivores_MCDD.txt` (`../pyrate-diversity-dependence/references/tutorial-4.md`:24), `example_files/DES_examples/…` (`../pyrate-des/references/tutorial-5.md`:63), `example_files/BDNN_examples/…` (`../pyrate-bdnn/references/tutorial-bdnn.md`:55).

## Parallel likelihood: multiprocessing, thread, `-thread`

| Item | Value / wording | Where |
| --- | --- | --- |
| Capability | "Under UNIX systems, PyRate will use the library multiprocessing and thread (if available) and implement parallel computation of the likelihoods (see command -thread)." | `home.md`:71 (CN `:72`) |
| What the command takes | `-thread` sets "the number of threads used for calculating the likelihood of the birth-death process and the NHPP likelihood respectively" — two integers; the page prints `-thread 0 0` "(default; sequential likelihood calculation)" and `-thread 1 3` "(use 1 thread for birth-death, 3 threads for NHPP likelihood)" | `../pyrate-command-reference/references/command-list.md`:76,`:78-79` |
| Install-side meaning of `0 0` | "When both values are set to 0, PyRate will use sequential computation of the likelihood (thus slowing down a bit the analysis) and will not use the multiprocessing python library." — so an interpreter without `multiprocessing` still gives a working, *sequential* run. That reading is **by inference** from the two quoted sentences: no mirror prints an error for a missing `multiprocessing`, and no mirror says which thread counts are sensible | `../pyrate-command-reference/references/command-list.md`:76 |
| Non-UNIX | no mirror states the behaviour on Windows for `-thread`; the multiprocessing sentence above is scoped "Under UNIX systems" | `home.md`:71 |

Everything beyond these four facts — the option's place in the command list, its interaction with the other analysis settings — is owned by `pyrate-command-reference`; route there rather than restating it.

## Pre-flight checklist — run this before any analysis

Order matters: the first rows decide whether the later ones mean anything. The suite also ships a runtime checker, `../pyrate-command-reference/scripts/check_env.py` (owned by `pyrate-command-reference`); run it alongside this table. Per its own header it is a Python-3 stdlib-only, offline probe that prints one PASS/FAIL/WARN/SKIP line per check — a python2 and a python3 interpreter, importability of numpy/scipy/argparse on each usable interpreter, `Rscript` on `PATH`, the four program files, and an adjacent `pyrate_lib` — and it takes `--pyrate-dir PATH` (repeatable), `--json`, `--timeout SECONDS`, `--python2 PATH`, `--python3 PATH`, `--self-test`. It therefore covers rows 1, 5, 6-argparse, 8 and 9 below; it does **not** cover the virtual-environment steps (rows 3-4), the tutorial's own `PyRate.py -v` run (row 7) or the R package `fitdistrplus` (row 10), which is why the table is still worth walking. Invoke it with `python3`, never with the interpreter you are testing: inside a PyRate 2.7 environment (the `home.md`:69 reading) a bare `python` is Python 2 and cannot run a Python-3 script.

| # | Check | Command (documented or plain probing) | Pass | How to read a failure |
| --- | --- | --- | --- | --- |
| 1 | which interpreter answers | `python -V` (and `python3 -V`, `py -V`) | one of them exists and you know which one your `PATH` gives | nothing found → Windows `PATH` lacks the Python folder and its `Scripts` subfolder (`virtual-environment.md`:54, `home.md`:82); inside a venv also check you ran step 2 (`:31`/`:36`) |
| 2 | which runtime rule does it satisfy | compare `python -V` to `virtual-environment.md`:13 (3.10+) and `home.md`:69 (2.6-2.7) | the version satisfies the page you are following | the two pages disagree by construction (`home.md`:69 vs `virtual-environment.md`:13): record the interpreter version and which page you used, never silently average them |
| 3 | pip usable through that interpreter | `python -m ensurepip --upgrade` then `python -m pip install --upgrade pip` (`virtual-environment.md`:42-43) | `python -m pip --version` prints a version inside the env | no pip → the first line of the tutorial's install block was skipped, so `requirements.txt` was never installed into this environment (`:42`) |
| 4 | dependency install | `python -m pip install -r your_path/PyRate-master/requirements.txt` (`virtual-environment.md`:44) | completes without pip reporting that the file does not exist | file not found → the docs' `your_path` stand-in was not replaced, or you are pointing at the parent of `PyRate-master` (`:39`) |
| 5 | numpy and scipy importable | `python -c "import numpy, scipy"` | both import | `home.md`:71 lists both as required; an ImportError here means dependencies went to a *different* interpreter (check 2 and hazard 2) |
| 6 | parallel-likelihood libraries | `python -c "import multiprocessing"` | importable → `-thread n m` can be used | not importable → PyRate "will not use the multiprocessing python library" (`../pyrate-command-reference/references/command-list.md`:76); keep `-thread 0 0` and expect a slower run; `import thread` failing on a 3.x interpreter is expected, since `home.md`:71 qualifies it "(if available)" and `home.md`:69 assumed 2.x |
| 7 | the program actually runs | `python your_path/PyRate-master/PyRate.py -v` (`virtual-environment.md`:49) | exit status 0 — no mirror documents what a successful `-v` prints, so the status is the only criterion the corpus supports | `Module FastPyRateC was not found.` → not fatal, "the program will still run but use a slower implementation for some of the functions" (`:52`); any other traceback is a real runtime failure |
| 8 | `pyrate_lib` adjacency | `ls <PyRate dir>/pyrate_lib` before `PyRateContinuous.py` / `PyRateMCDD.py` / `PyRateDES.py` | directory sits **next to** the program | `home.md`:61 — placement, nothing to install; hazard 7 |
| 9 | R and `Rscript` on `PATH` | `Rscript --version` (Windows: `where Rscript.exe`) | resolves | the documented requirement behind `-plot`/`-plot_raw` is unmet; the corpus never prints the resulting failure, so expect no graphic but report it as inference, not as a documented message (`home.md`:84, `virtual-environment.md`:55, `../pyrate-des/references/tutorial-5.md`:95) |
| 10 | R package for `fit.prior` | `Rscript -e 'library(fitdistrplus)'` | loads | `home.md`:86 — "The function `fit.prior` requires the package fitdistrplus."; input-file preparation still works without it |
| 11 | suite runtime checker | `python3 ../pyrate-command-reference/scripts/check_env.py --pyrate-dir <PyRate dir>` (add `--json` to parse it) | `VERDICT:` line says a usable runtime was detected (exit 0) | its `Remediation:` lines name the single most useful fix; it deliberately reports the python2 and python3 readings separately because of the contradiction in row 2 — see the paragraph above for what it cannot see. It probes only `numpy`, `scipy` and `argparse`, so rows 12-13 below are **not** covered by it and stay yours |
| 12 | `nlopt`, for a DES maximum-likelihood run only | `python -c 'import nlopt'` — install the way the page says: `pip install nlopt` | importable | needed because "PyRateDES requires the Python library *nlopt* for fitting models with Maximum likelihood" (`../pyrate-des/references/tutorial-5.md`:175), which tutorial 5 runs as `-A 3` (`:197`); no version is documented and no page says whether `requirements.txt` provides it, so treat a pass here as only 'the library the doc names is present', and read a failure as blocking an `-A 3` route rather than the whole install |
| 13 | `Dendropy`, for a `-tree` / BDC joint run only | `python -c 'import dendropy'` | importable | "Note that this function requires the [Dendropy library](https://dendropy.org)." (`../pyrate-trait-age-models/references/tutorial-4.md`:160, attached to the `-tree` call at `:158`). The corpus gives no install command and no version for it — `pip install nlopt` is spelled out for nlopt and nothing equivalent is printed for Dendropy, so the command above is inferred from the library name, and the import spelling (`dendropy`, lowercase) is inferred too |

`bash ../assets/files/venv-preflight.sh [PyRate-directory] [--run-verify]` automates rows 1-3 and 5-10 and the file-presence half of row 4 (it never installs anything, so row 4's actual install and row 11's checker stay yours to run); it re-prints both Python rules instead of choosing one, and exits 0 only when every check it can make passes (verified on this machine: exit 1 on a tree without `pyrate_lib`, exit 0 when it is present).

## Worked example

The commands below are the tutorial's own steps with its stand-in paths resolved, plus this skill's pre-flight fixture. `PYRATE` is the `PyRate-master` directory `virtual-environment.md`:39 calls `your_path/PyRate-master`.

```sh
cd pyrate-installation    # this skill directory, addressed from the suite root wherever it is installed
PYRATE=/path/to/PyRate-master

# Steps 1-4 of references/virtual-environment.md in one file (derived wrapper: python -m venv,
# ensurepip, pip install --upgrade pip, pip install -r requirements.txt, PyRate.py -v)
bash ../assets/files/venv-setup.sh "$PYRATE" ~/venvs/pyrate_env

# The wrapper cannot activate into your shell, so run the tutorial's own line 31 yourself, then re-check:
source ~/venvs/pyrate_env/bin/activate
python "$PYRATE/PyRate.py" -v                  # virtual-environment.md:49

# Pre-flight (this skill's fixture), then the suite checker owned by pyrate-command-reference
bash ../assets/files/venv-preflight.sh "$PYRATE" --run-verify
python3 ../pyrate-command-reference/scripts/check_env.py --pyrate-dir "$PYRATE"
```

Actual output of the pre-flight, re-captured byte-for-byte on this machine (2026-11) against a stub tree containing `PyRate.py`, `requirements.txt`, `pyrate_utilities.r`, `PyRateContinuous.py`, `example_files/` and **no** `pyrate_lib`:

```text
== PyRate pre-flight (interpreter: python) ==
PASS  python runs                    Python 3.12.7
PASS  virtual-env tutorial           Python 3.12.7 satisfies 'Python (v.3.10 or higher)' (virtual-environment.md:13)
PASS  python -m pip                  pip 24.2 from
PASS  numpy importable               1.26.4
PASS  scipy importable               1.13.1
PASS  argparse importable            command-line parser named as a program requirement (home.md:69)
PASS  multiprocessing                available - enables -thread parallel likelihood (home.md:71)
INFO  thread                         'thread' not importable - expected on Python 3 (renamed _thread); home.md:71 qualifies it with '(if available)'
PASS  Rscript on PATH                /usr/bin/Rscript
INFO  RScript spelling               docs print the shell command as `RScript` (home.md:84, virtual-environment.md:55); the executable is normally 'Rscript' - case matters on Unix
WARN  R fitdistrplus                 not installed - 'The function fit.prior requires the package fitdistrplus' (home.md:86)
PASS  PyRate.py                      /tmp/venv-audit/PyRate-master/PyRate.py
PASS  requirements.txt               /tmp/venv-audit/PyRate-master/requirements.txt
PASS  pyrate_utilities.r             /tmp/venv-audit/PyRate-master/pyrate_utilities.r
FAIL  PyRateContinuous.py pyrate_lib 'the folder pyrate_lib needs to be in the same directory as the program' (home.md:61)
INFO  PyRateMCDD.py                  not present in /tmp/venv-audit/PyRate-master (only needed for that model family)
INFO  PyRateDES.py                   not present in /tmp/venv-audit/PyRate-master (only needed for that model family)
PASS  example_files                  /tmp/venv-audit/PyRate-master/example_files - tutorial paths are written relative to the PyRate root
== python /tmp/venv-audit/PyRate-master/PyRate.py -v (virtual-environment.md:49) ==

PASS  PyRate.py -v                   exit 0
--
RESULT: 1 check(s) FAILED, 1 warning(s) - do not start an analysis on this interpreter
exit=1
```

`PyRate.py -v` printed nothing above because the tree is a stub file, not the real program — and no mirror states what a successful `-v` prints (see "Not documented"), so the fixture treats exit status 0 as the only checkable criterion. Re-running the same command after `mkdir /tmp/venv-audit/PyRate-master/pyrate_lib` ends with `RESULT: all documented runtime requirements checked OK (1 warning(s))` and exit 0.

Reading it: the interpreter fails `home.md`:69's rule and satisfies `virtual-environment.md`:13's — a documented contradiction, reported rather than resolved (hazard 1). The `FAIL` is the fixture's own wording of a documented requirement, not a message the docs print: `PyRateMCDD.py`/`PyRateDES.py` were not in the tree at all (so nothing to conclude about them), while `PyRateContinuous.py` was present without `pyrate_lib` beside it — precisely what `home.md`:61 forbids. `WARN` on fitdistrplus costs only `fit.prior` (`home.md`:86). Fix the placement, re-run, and only then start an analysis.

## Pitfalls

- **Do not "fix" the Python contradiction by inventing a compromise.** The corpus contains exactly two version *requirements* (`home.md`:69, `virtual-environment.md`:13); the only other version strings are two Windows `PATH` examples naming a 2.x and a 3.x install folder (`home.md`:82, `virtual-environment.md`:54). There is no third source, no release number, no changelog. Report both requirements with citations, plus the interpreter you observed.
- **`python`, `python3` and `py` are three different documented names for the interpreter you are about to use** (`virtual-environment.md`:19,`:24`,`:26`,`:39`); picking one silently changes which environment gets the dependencies (hazard 2).
- **An environment check passed is not an install check passed.** `Rscript --version` proves nothing about `pyrate_lib`, and `PyRate.py -v` proves nothing about `PyRateDES.py`, which is a different program, and `home.md`:53 gives its heading the pyrate_lib requirement.
- **The docs' stand-in text is not a path.** `desired_path_to_env`, `your_path`, `.../` and `/path_to_file/` appear in the printed commands; the tutorials explicitly use `.../` "for simplicity" (`../pyrate-input-file/references/tutorial-1.md`:31).
- **`pyrate_utilities.r` vs `pyrate_utilities.R`:** `home.md`:86 and `../pyrate-input-file/references/preparing-input-file.md`:28 print the lowercase `.r`, while `../pyrate-command-reference/references/command-list.md`:13,`:28` print "the R script `pyrate_utilities.R`". On a case-sensitive filesystem only one resolves; use whatever `ls` shows and cite both spellings.
- **Keep the docs' typos when quoting.** `home.md`:54 says "The MCDD model is described here" inside the `PyRateDES.py` section, and `RScript`/`Rscript` alternate as above — do not silently correct either in a report of what the wiki says.
- **`-v` is an install check, not an analysis option.** The string `PyRate.py -v` occurs exactly twice in this entire suite's mirrors — `virtual-environment.md`:49 and its CN twin `virtual-environment-cn.md`:50 — and never in the command list, so do not describe it as a supported analysis option; grep recipe 9 below prints every occurrence.

## Not documented in this wiki

| Unanswered question | Why you must not fill it in |
| --- | --- |
| The contents of `requirements.txt` (which packages, which versions) | both pages link the file (`home.md`:71, `virtual-environment.md`:44) and neither prints a single line of it, so any package list would be invented — including whether the two per-program libraries named elsewhere, `nlopt` (`../pyrate-des/references/tutorial-5.md`:175) and Dendropy (`../pyrate-trait-age-models/references/tutorial-4.md`:160), are inside it; neither is named on either install page, so both are checked by import (rows 12-13), not assumed installed |
| Which Python version a given PyRate release requires, or when the wiki's 2.x statement was superseded | no mirror carries a version number, date or changelog for either install page |
| What `PyRate.py -v` prints on success | the tutorial gives the command (`virtual-environment.md`:49) and no output; it does not even say in words that anything is printed |
| Whether `./PyRate.py path_to_input_file/file_name.py` (home.md:75) needs the executable bit or a shebang line | the page prints the form without any `chmod` or `#!` mention; the `python PyRate.py` alternative on the next line is offered with no stated reason |
| Whether `pyrate_lib` must also sit next to `PyRate.py` | `home.md`:28-29 carries no pyrate_lib requirement in its heading, but absence of that marker is not a statement about the program's imports — and note that `pyrate-bd-analysis`'s own worked example asserts the opposite, which this wiki does not support |
| Whether the programs resolve `pyrate_lib` relative to the script or to the working directory | `home.md`:61 says only "in the same directory as the program"; no mirror discusses `cd`, `-wd` or symlinks in this connection |
| `-thread` behaviour on Windows, and how many threads are sensible | `home.md`:71 scopes multiprocessing to "Under UNIX systems"; `../pyrate-command-reference/references/command-list.md`:76-79 documents the arguments but no platform |
| Minimum/maximum R version for `-plot` | `home.md`:86 tests `pyrate_utilities.r` under "R version 2.x and 3.x" (an R-script claim), while `virtual-environment.md`:55 merely shows an R 4.4.1 path example; nothing states which R versions `-plot` output works on |
| Whether fastPyRateC is required for any specific model | `virtual-environment.md`:52 says only that some functions get "a slower implementation"; the instructions link points outside this corpus |
| Installing PyRate on macOS Silicon/conda/Docker, or any package manager other than pip | the two install pages print only python.org installers, sourceforge for numpy/scipy, and pip |
| Whether the venv name must be `pyrate_env` | it is the tutorial's example string (`virtual-environment.md`:19,`:31`,`:36`), never called a requirement |

## Related skills

- `pyrate` — the router and tutorials index; `../pyrate/references/tutorials-index.md`:17 is the entry that labels this tutorial "Install PyRate and dependencies in a virtual environment", and `../pyrate/references/home.md` carries the same Home mirror for program/citation questions.
- `pyrate-command-reference` — owns the command list (`-thread`, `-wd`, `-d`, `-j`, `-b`) and the input-file option semantics, and ships `../pyrate-command-reference/scripts/check_env.py`: a Python-3, stdlib-only, offline **runtime** checker (python2/python3 interpreters, numpy/scipy/argparse imports, `Rscript` on `PATH`, the four program files, `pyrate_lib` adjacency) — pre-flight row 11 runs it and says what it cannot see.
- `pyrate-input-file` — owns `pyrate_utilities.r` as an R API (`extract.ages`, `extract.ages.pbdb`, `replicates`, `cutoff`, the `Site` column); this skill covers only the fact that loading it is an R step needing no Python install.
- `pyrate-summarize-results` — owns `-plot`, `-plot2`, `-tag` and the `*_RTTplot.r` / `*_RTTplot.pdf` outputs; this skill covers only their `Rscript`/`PATH` dependency.
- `pyrate-continuous-covariates`, `pyrate-diversity-dependence`, `pyrate-des` — own `PyRateContinuous.py`, `PyRateMCDD.py`, `PyRateDES.py` usage and their input tables; this skill owns the `pyrate_lib` placement rule that gates all three.
- `pyrate-bdnn` — owns the BDNN tutorial's model setup and its `example_files/BDNN_examples/…` paths.
- `pyrate-bd-analysis`, `pyrate-preservation-models`, `pyrate-rjmcmc`, `pyrate-trait-age-models`, `pyrate-mcmc-tuning` — analysis-layer skills; none of them restates install facts.

## Resources

| File | What's in it | Load when |
| --- | --- | --- |
| `references/virtual-environment.md` | The whole install tutorial (`pyrate_tutorial_0.md`): Python 3.10+ sentence, the 4 numbered steps with every command line, `python3`/`py` notes, `PyRate.py -v`, the FastPyRateC message, Windows `PATH` for `Python312`, `Python312\Scripts`, `R-4.4.1\bin`, the `RScript` sentence | Any install/venv/`pip`/`PATH` question; the `-v` check; whether a missing FastPyRateC module is fatal (it is not — `:52`) |
| `references/virtual-environment-cn.md` | Simplified-Chinese twin (frontmatter 9 lines, so body lines are +1). Confirms `-plot` is a function name ("函数 -plot 会生成一个用于产生图形输出的 R 脚本", `:56`) and that `python3`/`py` are interpreter names, not new commands (`:27`,`:40`) | When the English at `virtual-environment.md`:39 ("on Windows use `py` instead of `python`") or the `RScript` sentence reads ambiguously — it does not resolve the Python-version contradiction, which the CN reproduces verbatim (`:14`) |
| `references/home.md` | Program catalogue whose `:39`, `:46`, `:53` headings carry the pyrate_lib requirement, the `pyrate_lib` placement rule (`:61`), "Compatibility and installation" (`:68`-`:86`): Python 2.6-2.7 + "Python 3.x is currently not supported", argparse-on-2.6, numpy/scipy, `requirements.txt` + `pip install -r`, multiprocessing/thread, both UNIX launch forms, the Windows launch form, `PATH` for `python.exe`/`Rscript.exe`, `pyrate_utilities.r` R 2.x/3.x + fitdistrplus, and the `TUTORIALS` "for updated documentation" pointer (`:14`) | Every non-tutorial install fact; the version contradiction; which program needs what |
| `references/home-cn.md` | Simplified-Chinese twin of the same page (`:70` = the 2.6-2.7 / "目前不支持 Python 3.x" sentence, `:72` = multiprocessing/thread, `:76` = the `./PyRate.py path_to_input_file/file_name.py` line, `:85` = `RScript`, `:87` = fitdistrplus) | Cross-checking an ambiguous English sentence in Home — the two agree on every claim used above, including the ban on 3.x, so the contradiction with the tutorial is original, not a translation artefact |

```sh
# run these from this skill directory; every recipe is a plain read-only grep that matches
grep -n -e "Python (v.3.10 or higher)" -e "Python 3.x is currently not supported" -e "Python 2.6" references/virtual-environment.md references/home.md
grep -n -e "python -m venv" -e "py -m venv" -e "bin/activate" -e "Scripts" -e "ensurepip" -e "requirements.txt" -e "PyRate.py -v" references/virtual-environment.md
grep -n -e "FastPyRateC" -e "slower implementation" references/virtual-environment.md references/virtual-environment-cn.md
grep -n -e "argparse" -e "numpy and scipy are required" -e "multiprocessing" -e "fitdistrplus" -e "pyrate_utilities" references/home.md
grep -n -e "in the same directory as the program" -e "requires library" references/home.md
grep -n -e "PATH environment variables" -e "RScript" -e "Rscript.exe" references/home.md references/virtual-environment.md
grep -rn -e "pyrate_utilities" ../pyrate-input-file/references ../pyrate-command-reference/references
grep -rn -e "PyRate.py -v" references ../pyrate-command-reference/references
grep -rn -e "nlopt" -e "Dendropy" ../pyrate-des/references/tutorial-5.md ../pyrate-trait-age-models/references/tutorial-4.md   # the two per-program Python libraries: named only in tutorial mirrors, never on either install page
```

## Runnable fixtures (`../assets/files/`)

| File | Run it? | Provenance / what it makes concrete |
| --- | --- | --- |
| `../assets/files/venv-setup.sh` | yes — `bash venv-setup.sh /path/to/PyRate-master [env dir]`; re-run on this machine and it completed end to end with exit 0 against a stub tree (it creates a real venv, runs `ensurepip`, upgrades `pip`, installs `requirements.txt`, then runs `PyRate.py -v`) | `derived:` the tutorial's steps 1-4 (`virtual-environment.md`:19,31,42,43,44,49) with its stand-in paths taken as arguments; it prints the doc line beside each command, and prints (not runs) step 2's `source … bin/activate`, because a script cannot activate into the caller's shell |
| `../assets/files/venv-preflight.sh` | yes — `bash venv-preflight.sh [PyRate dir] [--run-verify]`; verified in both directions: exit 1 when `pyrate_lib` is absent from a tree holding `PyRateContinuous.py`, exit 0 when it is present (warnings alone never fail it) | `derived:` the pre-flight table above; probes only what `home.md`:61,69,71,84,86 and `virtual-environment.md`:13,42,44,49,52,55 document, and reports the two Python rules separately instead of choosing one |
| `../assets/files/venv-setup-windows.bat` | Windows `cmd.exe` only — **not executed** on the Linux box this suite was authored on | `derived:` the Windows branches the tutorial prints: `py -m venv` (`:24`), `Scripts\activate` (`:36`), `py` for `python` (`:39`), the three install commands (`:42-44`), `PyRate.py -v` (`:49`), and the `PATH` fixes for `python.exe` / `Python312\Scripts` / `Rscript.exe` (`:54-55`) |
| `../assets/files/venv-launch-forms.txt` | no (reference sheet) | `derived:` an annotated index — each command, message or `PATH` string is copied verbatim from the doc line named in its `[file:line]` tag (every tag re-checked against the mirrors), while the tags, the section headings, the entry labels and the parenthesised notes are the fixture's own additions and the wiki's curly quotes are normalised to straight ones; covers every install command, launch form and example `PATH` string the two install pages print, plus the per-program launch lines carried by sibling mirrors (`-thread 0 0`, `PyRateDES.py`, `PyRateMCDD.py`, `PyRateContinuous.py`); the one `PATH` instruction outside that coverage is named in the fixture header (`../pyrate-des/references/tutorial-5.md`:354 prints no example path) |
