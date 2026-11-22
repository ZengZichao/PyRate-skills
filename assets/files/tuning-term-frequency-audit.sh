#!/bin/sh
# tuning-term-frequency-audit.sh
# Provenance: written by the pyrate-mcmc-tuning skill author (plain shell, no external tools).
# Lives in assets/files; resolves this skill's references/ from its own location, so it runs from
# anywhere:  sh /abs/path/assets/files/tuning-term-frequency-audit.sh
# Prints how often the PyRate tuning vocabulary actually occurs on each mirrored page, and proves
# which knobs live on one page only. Everything it prints is observable fact from the mirrors; the
# absence checks are the point - they back the "not documented" table in SKILL.md.

set -u
ROOT="${0%/*}/*/*"
ROOT=$(cd "${0%/*}/../.." && pwd)
REF="$ROOT/pyrate-mcmc-tuning/references"
[ -d "$REF" ] || { echo "cannot find $REF (run the script from assets/files/)" >&2; exit 1; }
cd "$REF" || exit 1

echo "## pages scanned (wc -l -c)"
for f in tutorial-6.md tutorial-6-cn.md command-list.md command-list-cn.md; do
  printf '%-22s %s\n' "$f" "$(wc -l -c < "$f" | tr -s ' ')"
done

echo
echo "## tuning knobs: occurrences of each literal command name"
for k in fast_burnin multiR tT nT tQ tR tS fS tC fU fR r sw k a M B T; do
  printf -- '-%-11s t6=%-2s t6-cn=%-2s cl=%-2s cl-cn=%s\n' "$k" \
    "$(grep -o -- "-$k" tutorial-6.md      | wc -l)" \
    "$(grep -o -- "-$k" tutorial-6-cn.md   | wc -l)" \
    "$(grep -o -- "-$k" command-list.md    | wc -l)" \
    "$(grep -o -- "-$k" command-list-cn.md | wc -l)"
done

echo
echo "## which page defines each knob HEADING (1 = defined there, 0 = absent)"
for k in fast_burnin multiR tT nT tQ tR tS fS tC fU fR; do
  printf -- '-%-11s tutorial-6.md=%s  command-list.md=%s\n' "$k" \
    "$(grep -c "^##### \`-$k" tutorial-6.md)" \
    "$(grep -c "^##### \`-$k" command-list.md)"
done

echo
echo "## directional statements about tuning knobs (grep -c per phrase)"
for p in "Reducing this number can improve" "Higher number of scaling factors will improve" \
         "Increasing this parameter has a similar effect" "improve the MCMC mixing" \
         "automatically set to HPP" "automatically set to 0"; do
  printf '%-46s t6=%s cl=%s\n' "$p" \
    "$(grep -cF "$p" tutorial-6.md)" "$(grep -cF "$p" command-list.md)"
done

echo
echo "## convergence-diagnostic vocabulary (all four mirrors) - expect 0 for every line"
for p in effective\ sample ESS Rhat R-hat Gelman autocorrelation acceptance stationar tracer; do
  printf '%-20s %s\n' "$p" "$(grep -cow -- "$p" *.md | awk -F: '{s+=$NF} END {print s+0}')"
done
printf 'convergence      %s (only ever inside -fast_burnin)\n' \
  "$(grep -c convergence *.md | awk -F: '{s+=$NF} END {print s+0}')"
printf 'mixing           %s (only ever inside -fR)\n' "$(grep -c mixing *.md | awk -F: '{s+=$NF} END {print s+0}')"

echo
echo "## the one documented fast-burnin default, verbatim"
grep -n fast_burnin tutorial-6.md
