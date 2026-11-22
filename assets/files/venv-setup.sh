#!/usr/bin/env bash
# derived: runnable variant of pyrate-installation/references/virtual-environment.md:16-50
# shows: the four steps of "Setting up a virtual environment for PyRate" with the placeholders
#        (desired_path_to_env/pyrate_env, your_path) replaced by arguments instead of by hand
#
# Usage:  ./venv-setup.sh /path/to/PyRate-master [/where/to/put/pyrate_env]
#         PY=py  ./venv-setup.sh ...     # the docs say "on Windows use `py` instead of `python`"
#
# The doc's own lines, verbatim, are printed as "# doc:" comments next to each command.
set -u

REPO="${1:-}"
ENVDIR="${2:-./pyrate_env}"
PY="${PY:-python}"          # doc: "on Windows use `py` instead of `python`" (virtual-environment.md:39)
                           # doc: "you may have to type `python3`"          (virtual-environment.md:26)
command -v "$PY" >/dev/null 2>&1 || { echo "error: '$PY' not found (try python3, or PY=/path/to/python)"; exit 1; }
[ -n "$REPO" ] || { echo "error: give the path to the PyRate-master directory (the doc calls it your_path)"; exit 1; }
[ -f "$REPO/requirements.txt" ] || echo "warning: $REPO/requirements.txt not found - step 3 needs it (virtual-environment.md:44)"

echo "== 1) Create a virtual environment =="
# doc: python -m venv desired_path_to_env/pyrate_env            (virtual-environment.md:19)
# doc: py -m venv desired_path_to_env/pyrate_env                (virtual-environment.md:24, Windows)
"$PY" -m venv "$ENVDIR" || exit 1

echo "== 2) Activate the virtual environment =="
if [ "$(uname -s 2>/dev/null)" = "Windows_NT" ] || [ -d "$ENVDIR/Scripts" ]; then
  # doc: .\desired_path_to_env\pyrate_env\Scripts\activate      (virtual-environment.md:36)
  echo "Run in the *same* console before continuing:"
  echo "  source $ENVDIR/Scripts/activate     # Git-Bash/MSYS"
  echo "  .\\${ENVDIR}/Scripts\\activate          # Windows command prompt (virtual-environment.md:36)"
  exit 0
fi
# doc: source desired_path_to_env/pyrate_env/bin/activate       (virtual-environment.md:31)
# 'source' cannot persist into the caller from a script, so the activation line is printed for
# the user's own shell; the steps below use the environment's interpreter by absolute path.
BIN="$ENVDIR/bin"
[ -x "$BIN/python" ] || { echo "error: $BIN/python missing - activation or creation failed"; exit 1; }
echo "In your own shell, run:  source $ENVDIR/bin/activate      (virtual-environment.md:31)"

echo "== 3) Install PyRate dependencies =="
# doc: python -m ensurepip --upgrade                                       (virtual-environment.md:42)
# doc: python -m pip install --upgrade pip                                 (virtual-environment.md:43)
# doc: python -m pip install -r your_path/PyRate-master/requirements.txt   (virtual-environment.md:44)
"$BIN/python" -m ensurepip --upgrade &&
"$BIN/python" -m pip install --upgrade pip &&
"$BIN/python" -m pip install -r "$REPO/requirements.txt" || { echo "error: dependency install failed"; exit 1; }

echo "== 4) Check that PyRate runs in the environment =="
# doc: python your_path/PyRate-master/PyRate.py -v                         (virtual-environment.md:49)
echo "  $BIN/python $REPO/PyRate.py -v"
"$BIN/python" "$REPO/PyRate.py" -v
rc=$?
echo "exit code: $rc"
echo "If the output contains 'Module FastPyRateC was not found.' the install is still usable:"
echo "'the program will still run but use a slower implementation for some of the functions' (virtual-environment.md:52)"
exit $rc
