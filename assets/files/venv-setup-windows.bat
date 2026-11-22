@echo off
rem derived: runnable variant of the Windows branches of
rem   pyrate-installation/references/virtual-environment.md lines 24, 36, 39, 42-44, 49, 54-55
rem   pyrate-installation/references/home.md lines 82, 84
rem shows: the Windows-only install sequence (py launcher, Scripts\activate, PATH fixes for
rem        python.exe and Rscript.exe) as one file, with the doc's own lines as rem comments
rem
rem Usage (Command prompt):
rem   venv-setup-windows.bat create  C:\path\to\PyRate-master   [env dir, default .\pyrate_env]
rem   venv-setup-windows.bat install C:\path\to\PyRate-master   (run AFTER activating the env)
rem   venv-setup-windows.bat path                              (print the two PATH fixes)
rem Not executed on the Linux box this suite was authored on; the commands are those the docs print.

setlocal enabledelayedexpansion
set PHASE=%~1
set REPO=%~2
set ENVDIR=%~3
if "%ENVDIR%"=="" set ENVDIR=.\pyrate_env

if "%PHASE%"=="create"  goto create
if "%PHASE%"=="install" goto install
if "%PHASE%"=="path"    goto pathfix
echo Usage: venv-setup-windows.bat create^|install^|path C:\path\to\PyRate-master [env dir]
exit /b 2

:create
rem doc: "py -m venv desired_path_to_env/pyrate_env"            (virtual-environment.md line 24)
rem doc: "Note that depending on the default version of Python on your machine you may have to
rem       type python3."                                       (virtual-environment.md line 26)
if "%REPO%"=="" (echo Give the path to PyRate-master as the second argument. & exit /b 2)
py -m venv %ENVDIR%
if errorlevel 1 (echo "py" failed - the docs also print python3 / python as alternatives. & exit /b 1)
echo.
echo 2) Activate it, in the SAME console you will run PyRate from:
rem doc line 36: .\desired_path_to_env\pyrate_env\Scripts\activate
echo      %ENVDIR%\Scripts\activate
echo    then run:  venv-setup-windows.bat install %REPO%
exit /b 0

:install
rem doc: "Install PyRate dependencies in the virtual environment (on Windows use `py` instead of
rem       `python`)"                                           (virtual-environment.md line 39)
rem doc: python -m ensurepip --upgrade                          (virtual-environment.md line 42)
rem doc: python -m pip install --upgrade pip                    (virtual-environment.md line 43)
rem doc: python -m pip install -r your_path/PyRate-master/requirements.txt   (line 44)
if "%REPO%"=="" (echo Give the path to PyRate-master as the second argument. & exit /b 2)
py -m ensurepip --upgrade
py -m pip install --upgrade pip
py -m pip install -r %REPO%\requirements.txt
if errorlevel 1 (echo requirements.txt not found or install failed. & exit /b 1)
echo.
echo 4) Check that PyRate runs in the environment:
echo      python %REPO%\PyRate.py -v                            (virtual-environment.md line 49)
python %REPO%\PyRate.py -v
echo If the output contains "Module FastPyRateC was not found." the run is still valid, only slower
echo for some functions (virtual-environment.md line 52).
exit /b 0

:pathfix
rem doc: "make sure that the path to python.exe is included in the PATH environment variables ...
rem       add the folder in which Python 3.x is installed (e.g. 'C:\...\Python\Python312') and the
rem       folder with the Python scripts (e.g. 'C:\...\Python\Python312\Scripts')"  (line 54)
rem doc: "make sure that the path to Rscript.exe is included in the PATH environment variables
rem       (default in Mac/Linux) ... add the \bin folder of the R installation
rem       (e.g. 'C:\Program Files\R\R-4.4.1\bin')"              (line 55)
echo Check what this console actually resolves:
where python.exe
where Rscript.exe
if errorlevel 1 echo Rscript.exe not on PATH - the docs require it, because the -plot function
if errorlevel 1 echo executes the generated R script with the shell command Rscript
if errorlevel 1 echo (home.md line 84, virtual-environment.md line 55). What PyRate prints when it
if errorlevel 1 echo is missing is not documented on either page.
echo The wiki Home page prints the Python 2.x example 'C:\python27' and the R example
echo 'C:\Program Files\R\R-2.14.0\bin\i386' (home.md lines 82, 84); the install tutorial prints
echo Python312 / R-4.4.1 examples instead (virtual-environment.md lines 54, 55). Neither page says
echo which set supersedes the other - use the folder of the versions actually installed.
exit /b 0
