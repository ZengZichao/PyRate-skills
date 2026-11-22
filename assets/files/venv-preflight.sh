#!/usr/bin/env bash
# derived: PyRate-skills | probes are built only from commands/options the PyRate docs print
# shows: a pre-flight check of the PyRate runtime (interpreter, numpy/scipy/argparse, Rscript,
#        pyrate_lib adjacency) - run this before any analysis
#
# Usage:  ./venv-preflight.sh [path_to_PyRate_directory] [--run-verify]
# Exit:   0 = every documented requirement satisfied, 1 = at least one FAIL
#
# Rule sources (line numbers in the local mirrors of this suite):
#   interpreter 3.10+      pyrate-installation/references/virtual-environment.md:13
#   interpreter 2.6-2.7    pyrate-installation/references/home.md:69   ("Python 3.x is currently not supported")
#   argparse               pyrate-installation/references/home.md:69
#   numpy / scipy          pyrate-installation/references/home.md:71
#   multiprocessing/thread pyrate-installation/references/home.md:71
#   Rscript for -plot      pyrate-installation/references/home.md:84, virtual-environment.md:55
#   pyrate_utilities.r     pyrate-installation/references/home.md:86
#   pyrate_lib adjacency   pyrate-installation/references/home.md:61
#   PyRate.py -v           pyrate-installation/references/virtual-environment.md:49

PY="${PYTHON:-python}"
command -v "$PY" >/dev/null 2>&1 || PY=python3
PYDIR=""
RUN_VERIFY=0
for a in "$@"; do
  case "$a" in
    --run-verify) RUN_VERIFY=1 ;;
    *) PYDIR="$a" ;;
  esac
done

fails=0; warns=0
ok()   { printf 'PASS  %-30s %s\n' "$1" "$2"; }
bad()  { printf 'FAIL  %-30s %s\n' "$1" "$2"; fails=$((fails+1)); }
warn() { printf 'WARN  %-30s %s\n' "$1" "$2"; warns=$((warns+1)); }
info() { printf 'INFO  %-30s %s\n' "$1" "$2"; }

echo "== PyRate pre-flight (interpreter: $PY) =="

# 1. interpreter exists
if "$PY" -V >/dev/null 2>&1; then
  ver=$("$PY" -c 'import sys;print("%d.%d.%d"%sys.version_info[:3])' 2>/dev/null)
  ok "python runs" "$("$PY" -V 2>&1)"
  major=${ver%%.*}
  if "$PY" -c 'import sys;sys.exit(0 if sys.version_info[:2]>=(3,10) else 1)' 2>/dev/null; then
    ok "virtual-env tutorial" "Python $ver satisfies 'Python (v.3.10 or higher)' (virtual-environment.md:13)"
  elif [ "$major" = "2" ]; then
    warn "virtual-env tutorial" "Python $ver is 2.x: matches the wiki Home line 'using Python 2.6 – 2.7' (home.md:69) but NOT the tutorial's 'Python (v.3.10 or higher)' (virtual-environment.md:13)"
  else
    warn "virtual-env tutorial" "Python $ver is 3.x but older than 3.10 - below the tutorial floor 'Python (v.3.10 or higher)' (virtual-environment.md:13); Home (home.md:69) says instead 'Please note that Python 3.x is currently not supported'"
  fi
else
  bad "python runs" "'$PY' not found - on Windows the docs use 'py' (virtual-environment.md:24,39); or set PYTHON=/path/to/python"
fi

# 2. pip usable through the interpreter (docs never call a bare pip: virtual-environment.md:42-44)
if "$PY" -m pip --version >/dev/null 2>&1; then
  ok "python -m pip" "$("$PY" -m pip --version 2>&1 | cut -d' ' -f1-3)"
else
  bad "python -m pip" "not usable - run '$PY -m ensurepip --upgrade' (virtual-environment.md:42)"
fi

# 3. required libraries (home.md:71)
for lib in numpy scipy; do
  if v=$("$PY" -c "import $lib;print($lib.__version__)" 2>/dev/null); then
    ok "$lib importable" "$v"
  else
    bad "$lib importable" "no $lib - Home prints 'pip install -r requirements.txt' (home.md:71); the install tutorial prints 'python -m pip install -r your_path/PyRate-master/requirements.txt' (virtual-environment.md:44)"
  fi
done

# 4. argparse (home.md:69: manual install under 2.6, bundled with 2.7; still importable on 3.x)
if "$PY" -c "import argparse" 2>/dev/null; then
  ok "argparse importable" "command-line parser named as a program requirement (home.md:69)"
else
  bad "argparse importable" "missing - home.md:69 lists argparse as required (manual install under Python 2.6)"
fi

# 5. parallel likelihood libraries (home.md:71 "multiprocessing and thread (if available)")
if "$PY" -c "import multiprocessing" 2>/dev/null; then
  ok "multiprocessing" "available - enables -thread parallel likelihood (home.md:71)"
else
  warn "multiprocessing" "unavailable - likelihoods fall back to sequential; see -thread (home.md:71, command-list.md:75)"
fi
if "$PY" -c "import thread" 2>/dev/null; then
  ok "thread" "Python-2 module present (home.md:71)"
else
  info "thread" "'thread' not importable - expected on Python 3 (renamed _thread); home.md:71 qualifies it with '(if available)'"
fi

# 6. R / Rscript, needed by -plot (home.md:84, virtual-environment.md:55)
if command -v Rscript >/dev/null 2>&1; then
  ok "Rscript on PATH" "$(command -v Rscript)"
else
  if command -v Rscript.exe >/dev/null 2>&1; then
    ok "Rscript on PATH" "$(command -v Rscript.exe)"
  else
    bad "Rscript on PATH" "not found - '-plot' shells out to it (home.md:84); on Windows add R's bin folder to PATH (virtual-environment.md:55)"
  fi
fi
# the docs print the shell command as `RScript`; on a case-sensitive filesystem only Rscript exists
if [ -x "$(dirname "$(command -v Rscript 2>/dev/null || echo /nonexistent/x)")/RScript" ]; then
  info "RScript spelling" "a name 'RScript' also resolves here"
else
  info "RScript spelling" "docs print the shell command as \`RScript\` (home.md:84, virtual-environment.md:55); the executable is normally 'Rscript' - case matters on Unix"
fi

# 7. fitdistrplus, needed by fit.prior in pyrate_utilities.r (home.md:86)
if command -v Rscript >/dev/null 2>&1; then
  if Rscript -e 'library(fitdistrplus)' >/dev/null 2>&1; then
    ok "R fitdistrplus" "loads - required by fit.prior (home.md:86)"
  else
    warn "R fitdistrplus" "not installed - 'The function fit.prior requires the package fitdistrplus' (home.md:86)"
  fi
fi

# 8. the PyRate tree itself
if [ -n "$PYDIR" ]; then
  [ -d "$PYDIR" ] || { bad "PyRate directory" "'$PYDIR' does not exist"; }
  for f in PyRate.py requirements.txt pyrate_utilities.r; do
    if [ -e "$PYDIR/$f" ]; then ok "$f" "$PYDIR/$f"; else bad "$f" "not in $PYDIR"; fi
  done
  for prog in PyRateContinuous.py PyRateMCDD.py PyRateDES.py; do
    if [ -e "$PYDIR/$prog" ]; then
      if [ -d "$PYDIR/pyrate_lib" ]; then
        ok "$prog + pyrate_lib" "pyrate_lib is in the same directory (required, home.md:61)"
      else
        bad "$prog pyrate_lib" "'the folder pyrate_lib needs to be in the same directory as the program' (home.md:61)"
      fi
    else
      info "$prog" "not present in $PYDIR (only needed for that model family)"
    fi
  done
  if [ -d "$PYDIR/example_files" ]; then
    ok "example_files" "$PYDIR/example_files - tutorial paths are written relative to the PyRate root"
  else
    warn "example_files" "no example_files/ under $PYDIR - docs link them at github.com/dsilvestro/PyRate/tree/master/example_files (command-list.md:10)"
  fi
  if [ "$RUN_VERIFY" = "1" ] && [ -e "$PYDIR/PyRate.py" ]; then
    echo "== python $PYDIR/PyRate.py -v (virtual-environment.md:49) =="
    out=$("$PY" "$PYDIR/PyRate.py" -v 2>&1)
    rc=$?
    printf '%s\n' "$out"
    if printf '%s' "$out" | grep -q "Module FastPyRateC was not found"; then
      info "FastPyRateC" "absent - 'the program will still run but use a slower implementation for some of the functions' (virtual-environment.md:52)"
    fi
    [ "$rc" = "0" ] && ok "PyRate.py -v" "exit 0" || bad "PyRate.py -v" "exit $rc - see the traceback above"
  else
    info "PyRate.py -v" "not executed (pass --run-verify to run the tutorial's own check, virtual-environment.md:49)"
  fi
else
  info "PyRate tree" "no directory given - pass the PyRate root to also check pyrate_lib adjacency and example_files (home.md:61)"
fi

echo "--"
if [ "$fails" = "0" ]; then
  echo "RESULT: all documented runtime requirements checked OK ($warns warning(s))"
  exit 0
fi
echo "RESULT: $fails check(s) FAILED, $warns warning(s) - do not start an analysis on this interpreter"
exit 1
