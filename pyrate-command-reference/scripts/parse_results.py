#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""parse_results.py — compact, citating digest of the files a PyRate run left behind.

Part of the PyRate-skills suite (skill: pyrate-command-reference).
Python 3 standard library only. Deterministic, offline, read-only: it never runs
PyRate, never writes to the inspected directory, and never executes a .py/.r file
it is pointed at (a `*_PyRate.py` or `*_RTTplot.r` argument is treated as text).

WHY THE CITATIONS
  Which columns a `*_mcmc.log` carries is the only in-file evidence of which
  analysis mode actually ran, and the corpus states those rules literally
  ("only logged in BDMCMC analyses", "only logged under fixed number of shifts,
  i.e. with `-A 0` or `-A 1`"). Every rule this tool applies is quoted with its
  mirror file:line; every number it prints is labelled "arithmetic" because it is
  computed here, not documented. No mirror of this corpus prints a real header
  row or data row of any output file, so where the physical layout is unknown
  the tool prints the literal words `format not documented` instead of guessing.

USAGE
  python3 scripts/parse_results.py PATH [PATH ...]        # file or directory
  python3 scripts/parse_results.py run/pyrate_mcmc_logs    # digest every match
  python3 scripts/parse_results.py x_mcmc.log --b 0.1      # + effect of a burn-in
  python3 scripts/parse_results.py --stems                 # documented name stems
  python3 scripts/parse_results.py x_mcmc.log --json       # machine-readable
  python3 scripts/parse_results.py --self-test             # temp fixtures + asserts

FLAGS
  PATH                    file or directory; directories are walked (sorted, depth
                          first, symlinks not followed) and matched by stem
  --b N                   extra burn-in to report for logs: N>=1 = samples,
                          0<N<1 = fraction (references/command-list.md:69)
  --stems                 print the documented output-name stems and exit 0
  --json                  one JSON object instead of the text report
  --max-rows N            how many per-column statistics / names to print (1-200,
                          default 8); everything else is summarised as "+N more"
  --max-lines N           read at most N lines of any file (default 400000)
  --self-test             build its own temp fixtures and assert behaviour

EXIT CODES
  0 at least one documented file was digested
  1 nothing matched a documented stem, or every target was unreadable
  2 bad usage (e.g. --b without a number, --max-rows out of range)

WHAT IT PRINTS (text mode; bounded by --max-rows, so a *_mcmc.log block stays under
about 40 lines no matter how many columns the file has)
  One block per recognised file: stem + what the docs say it holds, sample/column
  counts, the columns this corpus names, the columns it does not (labelled
  "format not documented"), the mode evidence in the column set, shift-count
  histograms from k_birth/k_death, mean/median/min/max of the documented parameters,
  the marginal likelihood when a *_marginal_likelihood.txt is present, and the
  positional check of a *_se_est.txt / *_se_ext.txt table.
"""

import argparse
import json
import os
import re
import sys

# --- mirrors, as cited from this skill folder (paths must resolve for the reader) --
PAGE = "references/command-list.md"                                     # this skill
SUM = "../pyrate-summarize-results/references/summarize-results.md"
T1 = "../pyrate-bd-analysis/references/tutorial-1.md"
T3 = "../pyrate-rjmcmc/references/tutorial-3.md"
T2 = "../pyrate-summarize-results/references/tutorial-2.md"

UNDOCUMENTED = "format not documented"

# stem glob -> (documented wording, citation, reader)
STEMS = [
    ("_mcmc.log", "Tab-separated table with the MCMC samples of the posterior, prior, "
                  "likelihoods of the preservation process and of the birth-death "
                  "(indicated by PP_lik and BD_lik, respectively), the preservation rate "
                  "(q_rate) ... and the times of speciation and extinction of all taxa in "
                  "the data set (*_TS and *_TE, respectively).", SUM + ":18-20"),
    ("_sum.txt", "Text file providing the complete list of settings used in the analysis.",
     SUM + ":15-16"),
    ("_marginal_rates.log", "Tab-separated table with the posterior samples of the marginal "
                            "rates of speciation, extinction, and net diversification, "
                            "calculated within 1 time unit (typically Myr).", SUM + ":22-23"),
    ("_marginal_likelihood.txt", "Text file providing the marginal likelihood of a "
                                 "birth-death model estimated by TI; under -A 1 it replaces "
                                 "*_marginal_rates.log.", SUM + ":27-30"),
    ("_sp_rates.log", "sampled rates and times of rate shifts (RJMCMC, -A 4)", T3 + ":56-57"),
    ("_ex_rates.log", "sampled rates and times of rate shifts (RJMCMC, -A 4)", T3 + ":56-57"),
    ("_se_est.txt", "estimated times of origination and extinction written by -ginput and "
                    "read back by -d", T2 + ":31-33"),
    ("_se_ext.txt", "combined ...se_ext.txt written by -ginput with -tag", T2 + ":45-49"),
    ("_RTTplot.r", "the R script -plot generates (text; never executed by this tool)",
     SUM + ":40"),
    ("_RTTplot.pdf", "the pdf -plot generates", SUM + ":40"),
]

# documented mcmc.log column names, verbatim from the sentence at SUM:19-20 (+T1:257)
COLUMN_RULES = [
    ("posterior", "MCMC samples of the posterior", SUM + ":19"),
    ("prior", "MCMC samples of the prior", SUM + ":19"),
    ("PP_lik", "likelihood of the preservation process", SUM + ":19-20"),
    ("BD_lik", "likelihood of the birth-death process", SUM + ":20"),
    ("q_rate", "the preservation rate", SUM + ":20"),
    ("alpha", "shape parameter of its gamma distributed heterogeneity", SUM + ":20"),
    ("cov_sp", "the parameters of the Covar model", SUM + ":20"),
    ("cov_ex", "the parameters of the Covar model", SUM + ":20"),
    ("cov_q", "the parameters of the Covar model", SUM + ":20"),
    ("k_birth", "the number of sampled rate shifts (only logged in BDMCMC analyses)",
     SUM + ":20"),
    ("k_death", "the number of sampled rate shifts (only logged in BDMCMC analyses)",
     SUM + ":20"),
    ("beta", "the value of scaling factor used in TI analyses", SUM + ":20"),
    ("root_age", "the time of origin of the oldest lineage", SUM + ":20"),
    ("tot_length", "the total branch length", SUM + ":20"),
    ("hypL", "estimated scale parameter of the half-Cauchy prior on speciation rates",
     T1 + ":257"),
    ("hypM", "estimated scale parameter of the half-Cauchy prior on extinction rates",
     T1 + ":257"),
]
DOCUMENTED_EXACT = set(name for name, _w, _c in COLUMN_RULES)

PATTERNS = [
    (re.compile(r"^lambda_(\d+)$"), "speciation rate between shifts (lambda_0, lambda_1, "
     "...; only logged under fixed number of shifts, i.e. with -A 0 or -A 1)", SUM + ":20"),
    (re.compile(r"^mu_(\d+)$"), "extinction rate between shifts (mu_0, mu_1, ...; only "
     "logged under fixed number of shifts, i.e. with -A 0 or -A 1)", SUM + ":20"),
    (re.compile(r"^shift_sp_(\d+)$"), "time of a speciation-rate shift (only logged with "
     "-A 0 or -A 1)", SUM + ":20"),
    (re.compile(r"^shift_ex_(\d+)$"), "time of an extinction-rate shift (only logged with "
     "-A 0 or -A 1)", SUM + ":20"),
    (re.compile(r"^q_(\d+)$"), "preservation rate within one time frame under the TPP model "
     "(q_0, q_1, ... q_n, from older to younger)", T1 + ":199"),
    (re.compile(r"^.+_TS$"), "time of speciation of one taxon (*_TS)", SUM + ":20"),
    (re.compile(r"^.+_TE$"), "time of extinction of one taxon (*_TE)", SUM + ":20"),
]


# --------------------------------------------------------------------- small helpers
def is_float(tok):
    try:
        float(tok)
        return True
    except (TypeError, ValueError):
        return False


def fnum(x):
    if x is None:
        return "-"
    return "%.6g" % x


def clip(items, n):
    """Bounded, human-readable rendering of a list."""
    items = list(items)
    if not items:
        return "(none)"
    if len(items) <= n:
        return ", ".join(str(i) for i in items)
    return ", ".join(str(i) for i in items[:n]) + " ... (+%d more)" % (len(items) - n)


def quantile(sorted_vals, q):
    """Nearest-rank quantile; arithmetic, not a documented estimator (95% HPD is
    what -plot draws, SUM:40, and computing it needs the file's own convention)."""
    if not sorted_vals:
        return None
    idx = min(len(sorted_vals) - 1, max(0, int(round(q * (len(sorted_vals) - 1)))))
    return sorted_vals[idx]


def classify(path):
    """Return (stem, documented wording, citation) for a recognised output file."""
    base = os.path.basename(path)
    for stem, wording, cite in STEMS:
        if base.endswith(stem):
            return stem, wording, cite
    if re.match(r"^combined_\d+_mcmc\.log$", base):
        return "_mcmc.log", "combined log across replicates (-combLogRJ): " \
                            "combined_[n]_mcmc.log", T3 + ":101"
    for stem, wording, cite in STEMS:
        if stem.startswith("_") and base.endswith(stem.lstrip("_")):
            return stem, wording, cite
    return None, None, None


def read_lines(path, limit=None):
    """Read text with no traceback on binary/oversized input; returns (lines, note)."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.read().split("\n")
    except OSError as exc:
        return None, "unreadable: %s" % (exc.strerror or exc)
    if limit is not None and len(lines) > limit:
        return lines[:limit], "truncated at %d line(s) by this tool" % limit
    return lines, None


def table_rows(lines):
    """Split tab-separated rows, skipping blanks and '#' comment lines."""
    rows = []
    for ln in lines:
        text = ln.rstrip("\r")
        if not text.strip() or text.lstrip().startswith("#"):
            continue
        rows.append([c.strip() for c in text.split("\t")])
    return rows


def column_values(rows, index):
    """Numeric values of one column, by position; non-numeric cells are skipped."""
    vals = []
    for r in rows:
        if index < len(r) and is_float(r[index]):
            vals.append(float(r[index]))
    return vals


# ------------------------------------------------------------------------ summarisers
def summarise_columns(header, rows, max_rows):
    """Column inventory: names this corpus defines, names it does not, and per-column
    arithmetic. Returns (report_lines, data_for_json)."""
    named, groups, unknown = [], {}, []
    exact = dict((n, (w, c)) for n, w, c in COLUMN_RULES)
    for i, col in enumerate(header):
        if col in DOCUMENTED_EXACT:
            wording, cite = exact[col]
            named.append((col, i, wording, cite))
            continue
        for rx, wording, cite in PATTERNS:
            if rx.match(col):
                grp = groups.setdefault(rx.pattern, {"wording": wording, "cite": cite,
                                                     "cols": []})
                grp["cols"].append((col, i))
                break
        else:
            unknown.append((col, i))

    stats = {}
    for col, i, _w, _c in named:
        stats[col] = column_values(rows, i)
    for _pat, grp in groups.items():
        for col, i in grp["cols"][:max_rows]:
            stats[col] = column_values(rows, i)

    lines = []
    lines.append("  columns defined by this corpus: %s"
                 % clip([c[0] for c in named], max_rows))
    for pat, wording, cite, cols in _group_order(groups):
        lines.append("  %s: %d column(s) %s" % (wording.split(" (")[0], len(cols),
                                                clip(cols, 4)))
        lines.append("     %s [%s]" % (wording, cite))
    if unknown:
        lines.append("  columns this corpus never names: %s -> their meaning: %s"
                     % (clip([c[0] for c in unknown], max_rows), UNDOCUMENTED))
    return lines, stats, named, groups, unknown


def _group_order(groups):
    """Deterministic iteration over the pattern groups, in PATTERNS order."""
    rank = dict((rx.pattern, i) for i, (rx, _w, _c) in enumerate(PATTERNS))
    out = []
    for pat in sorted(groups, key=lambda p: rank.get(p, 99)):
        grp = groups[pat]
        out.append((pat, grp["wording"], grp["cite"], [c for c, _i in grp["cols"]]))
    return out


def stat_line(name, vals):
    if not vals:
        return "  %s: no numeric values parsed" % name
    s = sorted(vals)
    return ("  %s: n=%d mean=%s median=%s min=%s max=%s"
            % (name, len(s), fnum(sum(s) / len(s)), fnum(quantile(s, 0.5)),
               fnum(s[0]), fnum(s[-1])))


def histogram(vals, keep=8):
    out = {}
    for v in vals:
        key = int(v) if v == int(v) else v
        out[key] = out.get(key, 0) + 1
    pairs = sorted(out.items(), key=lambda kv: (-kv[1], str(kv[0])))
    return pairs[:keep], len(pairs) - keep


def mode_evidence(header):
    """Statements the corpus really makes about which columns mean which -A mode."""
    cols = set(header)
    ev = []
    if {"k_birth", "k_death"} & cols:
        ev.append(("k_birth/k_death present", "\"only logged in BDMCMC analyses\" [%s:20]"
                   % SUM, "-A 2 per %s:51-52" % PAGE))
    if ({"lambda_0", "mu_0"} & cols) or any(re.match(r"^shift_(sp|ex)_\d+$", c) for c in cols):
        ev.append(("lambda_*/mu_*/shift_* present",
                   "\"only logged under fixed number of shifts, i.e. with `-A 0` or "
                   "`-A 1`\" [%s:20]" % SUM, "-A 0 / -A 1 per %s:47, 49" % PAGE))
    if "beta" in cols:
        ev.append(("beta present", "\"the value of scaling factor used in TI analyses\" "
                   "[%s:20]" % SUM, "-A 1 per %s:49" % PAGE))
    if {"cov_sp", "cov_ex", "cov_q"} & cols:
        ev.append(("cov_* present", "\"the parameters of the Covar model\" [%s:20]" % SUM,
                   "-mCov per %s:138" % PAGE))
    if any(re.match(r"^q_\d+$", c) for c in cols):
        ev.append(("q_0, q_1, ... present", "\"When using the TPP model of preservation, "
                   "the preservation rates between shifts are indicated as q_0, q_1, "
                   "... q_n\" [%s:199]" % T1, "-qShift per %s:91-92" % PAGE))
    if "alpha" in cols:
        ev.append(("alpha present", "\"the shape parameter of its gamma distributed "
                   "heterogeneity\" [%s:20]" % SUM, "-mG per %s:95-96" % PAGE))
    if "hypL" in cols or "hypM" in cols:
        ev.append(("hypL/hypM present", "\"the estimated scale parameters of the "
                   "half-Cauchy prior distributions assigned to speciation and extinction "
                   "rates, indicated by hypL and hypM\" [%s:257]" % T1,
                   "-fixShift per %s:124" % PAGE))
    return ev


def digest_mcmc_log(path, lines, res, args):
    rows = table_rows(lines)
    if not rows:
        res["lines"].append("  empty after comment/blank filtering")
        return
    has_header = not all(is_float(c) for c in rows[0])
    header = rows[0] if has_header else []
    data = rows[1:] if has_header else rows
    res["lines"].append("  samples=%d  columns=%s  (arithmetic on the file; no mirror "
                        "prints a header or a data row, so the physical column order is "
                        "%s)" % (len(data), len(header) or "unknown", UNDOCUMENTED))
    if not has_header:
        res["lines"].append("  no header line found: columns cannot be named — %s; the "
                            "docs assume a named, tab-separated table [%s:18-20]"
                            % (UNDOCUMENTED, SUM))
        res["data"]["samples"] = len(data)
        res["data"]["columns"] = None
        res["data"]["header"] = None
        return
    res["data"]["samples"] = len(data)
    res["data"]["columns"] = len(header)
    res["data"]["header"] = header

    idx = dict((c, i) for i, c in enumerate(header))
    col_lines, stats, _named, _groups, unknown = summarise_columns(header, data,
                                                                  args.max_rows)
    res["lines"].extend(col_lines)
    res["data"]["unnamed_columns"] = [c for c, _i in unknown]
    res["data"]["column_values"] = dict((k, v) for k, v in stats.items()
                                        if k in DOCUMENTED_EXACT)

    ev = mode_evidence(header)
    if ev:
        res["lines"].append("  mode evidence in the column set:")
        for what, quote, mode in ev:
            res["lines"].append("    %s -> %s => %s" % (what, quote, mode))
    res["data"]["mode_evidence"] = [[a, b, c] for a, b, c in ev]

    for shift in ("k_birth", "k_death"):
        vals = stats.get(shift) or []
        if vals:
            pairs, extra = histogram(vals)
            res["lines"].append("  shift counts (%s): %s%s" % (
                shift, ", ".join("%s sample(s) at %s" % (n, v) for v, n in pairs),
                " ... (+%d value(s) not shown)" % extra if extra > 0 else ""))
            res["data"].setdefault("shift_counts", {})[shift] = \
                {"values": [[v, n] for v, n in pairs]}

    if not any(c in DOCUMENTED_EXACT for c in header):
        res["lines"].append("  none of the column names the corpus defines is present; "
                            "reading this file against the docs is %s" % UNDOCUMENTED)

    order = [c for c in ("posterior", "prior", "PP_lik", "BD_lik", "q_rate", "alpha",
                         "root_age", "tot_length") if c in idx]
    if order:
        res["lines"].append("  documented parameters (arithmetic on the logged samples):")
        for name in order:
            res["lines"].append("    " + stat_line(name, stats.get(name, []))[2:])
    ts = [c for c in header if c.endswith("_TS")]
    te = [c for c in header if c.endswith("_TE")]
    res["data"]["taxon_time_columns"] = {"TS": len(ts), "TE": len(te)}
    if ts or te:
        res["lines"].append("  per-taxon times: %d *_TS and %d *_TE column(s) -> %s; "
                            "showing the first %d (arithmetic):"
                            % (len(ts), len(te),
                               clip(ts[:2] + te[:2], 4), args.max_rows))
        for col in (ts + te)[:args.max_rows]:
            res["lines"].append("    %s" % stat_line(col, stats.get(col, []))[2:])
        if len(ts) + len(te) > args.max_rows:
            res["lines"].append("    ... (+%d column(s) not shown)"
                                % (len(ts) + len(te) - args.max_rows))
        res["lines"].append("    these are the values a later -fixSE or -d table is built "
                            "from [%s:105; %s:18]" % (PAGE, PAGE))
    elif data:
        res["lines"].append("  no *_TS/*_TE columns. The docs list them as part of the file "
                            "[%s:20] but never say they disappear under fixed times "
                            "(-d / -fixSE / -nT 0, %s:18, 105, 240), so treat this "
                            "reading as %s and confirm in *_sum.txt"
                            % (SUM, PAGE, UNDOCUMENTED))
    burn = args.b
    if burn is not None:
        if 0 < burn < 1:
            kept = int(round(len(data) * (1.0 - burn)))
            res["lines"].append("  --b %g as a fraction: %d of %d sample(s) kept "
                                "(arithmetic; %s:69 defines the fraction against the "
                                "MCMC generations, not against this file)"
                                % (burn, kept, len(data), PAGE))
        else:
            kept = max(len(data) - int(burn), 0)
            res["lines"].append("  --b %g: %d of %d sample(s) kept (arithmetic)"
                                % (burn, kept, len(data)))
        res["data"]["burnin_kept"] = kept


def digest_marginal_rates(path, lines, res, _args):
    rows = table_rows(lines)
    if not rows:
        res["lines"].append("  empty after comment/blank filtering")
        return
    first = rows[0]
    has_header = not all(is_float(c) for c in first)
    data = rows[1:] if has_header else rows
    res["lines"].append("  rows=%d  columns=%d (arithmetic)" % (len(data), len(first)))
    res["data"]["rows"] = len(data)
    res["data"]["columns"] = len(first)
    res["lines"].append("  column layout: %s — the corpus describes the content "
                        "(\"the marginal rates of speciation, extinction, and net "
                        "diversification, calculated within 1 time unit (typically Myr)\") "
                        "but prints no header [%s:22-23]" % (UNDOCUMENTED, SUM))
    if has_header:
        res["lines"].append("  header as found in the file: %s" % clip(first, 8))
        res["data"]["header"] = first
    named = [c for c in first if c in DOCUMENTED_EXACT]
    if named:
        res["lines"].append("  names that also occur in the mcmc.log sentence: %s"
                            % clip(named, 8))
    for i in range(min(3, len(first))):
        vals = column_values(data, i)
        if vals:
            s = sorted(vals)
            res["lines"].append("  column %d (unlabelled by the docs): n=%d min=%s "
                                "max=%s (arithmetic only)"
                                % (i + 1, len(s), fnum(s[0]), fnum(s[-1])))


def digest_likelihood(path, lines, res, _args):
    body = [l.strip() for l in lines if l.strip()]
    res["lines"].append("  %d non-empty line(s)" % len(body))
    for l in body[:3]:
        res["lines"].append("  | %s" % l[:140])
    vals = [l for l in body if is_float(l.split()[-1] if l.split() else "")]
    if vals:
        res["lines"].append("  marginal likelihood value(s) present: %s (read from the "
                            "file)" % clip([v.split()[-1] for v in vals], 4))
        res["data"]["values"] = [float(v.split()[-1]) for v in vals]
    else:
        res["lines"].append("  no bare numeric line found; file layout: %s" % UNDOCUMENTED)
    res["lines"].append("  feeds -BF, which \"Takes the marginal likelihoods calculated "
                        "under two birth-death models (from '*_marginal_likelihood.txt' "
                        "files) to calculate Bayes Factors\" [%s:68]" % SUM)


def documented_options():
    """Option names declared by the command-list mirror (parsed, never hardcoded)."""
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, os.pardir, "references", "command-list.md")
    names = []
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                m = re.match(r"^#{5}[ \t]*`?(-[A-Za-z][A-Za-z0-9_]*)`?[ \t]*$", line)
                if m:
                    names.append(m.group(1))
    except OSError:
        return []
    return names


def digest_sum(path, lines, res, _args):
    body = [l.rstrip("\r") for l in lines if l.strip()]
    res["lines"].append("  %d non-empty line(s) — \"Text file providing the complete list "
                        "of settings used in the analysis.\" [%s:15-16]"
                        % (len(body), SUM))
    res["lines"].append("  field layout: %s (no mirror prints this file)" % UNDOCUMENTED)
    text = "\n".join(body)
    opts = [o for o in documented_options()
            if re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(o), text)]
    if opts:
        res["lines"].append("  command-list options named in the text (keyword scan, not a "
                            "parser): %s" % clip(opts, 14))
    for l in body[:6]:
        res["lines"].append("  | %s" % l[:140])
    if len(body) > 6:
        res["lines"].append("  | ... +%d line(s) not shown" % (len(body) - 6))
    res["data"]["lines"] = len(body)


def digest_rates_or_plot(path, lines, res, stem):
    if stem.endswith(".r"):
        res["lines"].append("  R script written by -plot; treated as text and never "
                            "executed [%s:40]" % SUM)
        body = [l for l in lines if l.strip()][:4]
        for l in body:
            res["lines"].append("  | %s" % l[:140])
        return
    if stem.endswith(".pdf"):
        res["lines"].append("  binary plot output; nothing to digest [%s:40]" % SUM)
        return
    rows = table_rows(lines)
    res["lines"].append("  rows=%d  columns=%s" % (len(rows),
                                                   len(rows[0]) if rows else 0))
    res["lines"].append("  column layout: %s — \"because the number of shifts is likely to "
                        "change throughout the RJMCMC, the number of columns in the text "
                        "file is not fixed\" [%s:57]; read it with -plotRJ [%s:71-73]"
                        % (UNDOCUMENTED, T3, T3))


def digest_se_table(path, lines, res, _args):
    rows = table_rows(lines)
    if not rows:
        res["lines"].append("  empty after comment/blank filtering")
        return
    first = rows[0]
    has_header = not all(is_float(c) for c in first)
    data = rows[1:] if has_header else rows
    res["lines"].append("  rows=%d  columns=%d (arithmetic)%s"
                        % (len(data), len(first),
                           "; header in file: " + clip(first, 6) if has_header else ""))
    res["lines"].append("  documented column meanings are positional: \"the first column "
                        "indicates the clade assignment ... The second column indicates a "
                        "species numeric identifier ... the third and fourth column "
                        "contain the time of origin and extinction of each species\" and "
                        "further pairs may follow [%s:18; %s:24]. The literal header "
                        "labels: %s" % (PAGE, T2, UNDOCUMENTED))
    bad = [i + 1 for i, r in enumerate(data)
           if len(r) < 4 or not is_float(r[2]) or not is_float(r[3])]
    if bad:
        res["lines"].append("  rows that do not fit the documented 4-column shape: %s"
                            % clip(bad, 6))
    else:
        res["lines"].append("  every row has >= 4 fields with numeric columns 3-4 "
                            "(checked, not documented behaviour)")
    if len(first) % 2 == 1 and len(first) > 4:
        res["lines"].append("  column count %d is not 4 + an even number of estimate "
                            "pairs — the docs describe pairs [%s:18]" % (len(first), PAGE))


DIGESTERS = {
    "_mcmc.log": digest_mcmc_log,
    "_marginal_rates.log": digest_marginal_rates,
    "_marginal_likelihood.txt": digest_likelihood,
    "_sum.txt": digest_sum,
    "_sp_rates.log": digest_rates_or_plot,
    "_ex_rates.log": digest_rates_or_plot,
    "_RTTplot.r": digest_rates_or_plot,
    "_RTTplot.pdf": digest_rates_or_plot,
    "_se_est.txt": digest_se_table,
    "_se_ext.txt": digest_se_table,
}


# ---------------------------------------------------------------------------- walking
def expand(target):
    """Files under `target` (or `target` itself); bounded and deterministic."""
    if os.path.isfile(target):
        return [target], []
    if not os.path.isdir(target):
        return [], ["not found: %s" % target]
    notes = []
    found = []
    for root, dirs, files in os.walk(target, followlinks=False):
        dirs.sort()
        for name in sorted(files):
            found.append(os.path.join(root, name))
            if len(found) >= 2000:
                notes.append("stopped scanning after 2000 files (output bound)")
                return found, notes
    return found, notes


def parse_targets(targets, args):
    report, problems, skipped = [], [], []
    for target in targets:
        files, notes = expand(target)
        problems.extend(notes)
        matched = 0
        for path in files:
            stem, wording, cite = classify(path)
            if stem is None:
                if os.path.isfile(target):
                    problems.append("not a documented PyRate output name: %s "
                                    "(recognised stems: %s)"
                                    % (path, ", ".join(s for s, _w, _c in STEMS)))
                else:
                    skipped.append(path)
                continue
            matched += 1
            entry = {"path": path, "stem": stem, "citation": cite,
                     "documented_as": wording, "lines": [], "data": {}}
            lines, note = read_lines(path, limit=args.max_lines)
            if lines is None:
                entry["lines"].append("  %s" % note)
                entry["data"]["error"] = note
            else:
                if note:
                    entry["lines"].append("  (%s)" % note)
                digester = DIGESTERS[stem]
                try:
                    if stem in ("_sp_rates.log", "_ex_rates.log", "_RTTplot.r",
                                "_RTTplot.pdf"):
                        digest_rates_or_plot(path, lines, entry, stem)
                    else:
                        digester(path, lines, entry, args)
                except Exception as exc:          # never leak a traceback
                    entry["lines"].append("  could not be digested: %s: %s"
                                          % (type(exc).__name__, exc))
                    entry["data"]["error"] = str(exc)
            report.append(entry)
        if not matched and os.path.isdir(target):
            problems.append("no file with a documented stem inside %s" % target)
    return report, problems, skipped


def cross_checks(report):
    """Consistency readings that need more than one file; each one quoted, none invented."""
    by_stem = {}
    for e in report:
        by_stem.setdefault(e["stem"], []).append(e)
    cols = set()
    for e in by_stem.get("_mcmc.log", []):
        cols.update(e["data"].get("header") or [])
    out = []
    has_k = bool({"k_birth", "k_death"} & cols)
    has_fixed = ({"lambda_0", "mu_0"} & cols) or any(
        re.match(r"^shift_(sp|ex)_\d+$", c) for c in cols)
    if has_k and has_fixed:
        out.append("*_mcmc.log carries both k_birth/k_death and lambda_*/shift_* columns. "
                   "The pages make these exclusive: \"only logged in BDMCMC analyses\" vs "
                   "\"only logged under fixed number of shifts, i.e. with `-A 0` or `-A 1`\" "
                   "[%s:20] - so either two runs were combined here or the corpus does not "
                   "describe this file" % SUM)
    ml = by_stem.get("_marginal_likelihood.txt", [])
    if ml and has_k:
        out.append("a *_marginal_likelihood.txt sits next to a log whose k_birth/k_death "
                   "say BDMCMC. The marginal likelihood is computed \"by TI (option -A 1)\" "
                   "[%s:27] and BDMCMC is `-A 2` [%s:51] - these do not come from one run "
                   "unless the files were pooled" % (SUM, PAGE))
    if ml and by_stem.get("_marginal_rates.log") and len(ml) == 1:
        out.append("*_marginal_rates.log and *_marginal_likelihood.txt are both present: "
                   "under -A 1 the first \"is replaced by the following\" [%s:27], so at "
                   "least one of them is from another analysis" % SUM)
    if len(ml) >= 2:
        out.append("%d *_marginal_likelihood.txt files: this is the input of -BF, which "
                   "\"Takes the marginal likelihoods calculated under two birth-death "
                   "models (from '*_marginal_likelihood.txt' files) to calculate Bayes "
                   "Factors\" [%s:68]" % (len(ml), SUM))
    elif len(ml) == 1:
        out.append("only one *_marginal_likelihood.txt here; -BF compares two, so a single "
                   "file cannot yield a Bayes Factor [%s:68]" % SUM)
    return out


def render_text(report, problems, skipped, args):
    out = ["PyRate results digest — %d file(s) recognised, %d other file(s) ignored"
           % (len(report), len(skipped))]
    for entry in report:
        out.append("")
        out.append("FILE %s" % entry["path"])
        out.append("  stem %s  [%s]" % (entry["stem"], entry["citation"]))
        out.append("  documented as: %s" % entry["documented_as"])
        out.extend(entry["lines"])
    cross = cross_checks(report)
    if cross:
        out.append("")
        out.append("CROSS-CHECKS (readings that combine several files)")
        for c in cross:
            text = "  - %s" % c
            out.append(text if len(text) <= 400 else text[:397] + "...")
    if problems:
        out.append("")
        out.append("PROBLEMS")
        out.extend("  - %s" % p for p in problems[:20])
        if len(problems) > 20:
            out.append("  ... +%d more" % (len(problems) - 20))
    if not report:
        out.append("")
        out.append("nothing to digest; documented stems:")
        out.extend(print_stems(lines=True))
    return "\n".join(out)


def print_stems(lines=False):
    out = []
    for stem, wording, cite in STEMS:
        out.append("  %-29s %s [%s]" % ("*" + stem, (wording[:70] + "...")
                                        if len(wording) > 73 else wording, cite))
    out.append("  -out adds a tag to every stem name: \"`-out run_2`  (adds 'run_2' to "
               "the name of all output files)\" [%s:32-35]" % PAGE)
    out.append("  -wd moves them elsewhere: \"If not specified, output files will be "
               "saved in the same directory as the input file\" [%s:22-23]" % PAGE)
    out.append("  MCMC/BDMCMC logs land in a folder \"named pyrate_mcmc_logs in the same "
               "directory as the input file\" [%s:194]" % T1)
    if lines:
        return out
    print("\n".join(out))
    return []


# -------------------------------------------------------------------------- self-test
def _write(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def self_test():
    import shutil
    import tempfile
    fails = []
    checks = [0]

    def expect(cond, msg):
        checks[0] += 1
        if not cond:
            fails.append(msg)

    tmp = tempfile.mkdtemp(prefix="parse_results_selftest_")
    try:
        bdmcmc = ["posterior\tprior\tPP_lik\tBD_lik\tq_rate\talpha\tk_birth\tk_death\t"
                  "root_age\ttot_length\tCanis_ferox_TS\tCanis_ferox_TE"]
        for i in range(10):
            bdmcmc.append("%d\t%d\t%d\t%d\t0.5\t1.2\t%d\t%d\t10.5\t100\t%s\t0.0"
                          % (100 + i, 10 + i, 5 * i, 2 * i, i % 3, (i + 1) % 4,
                             9.0 + i * 0.1))
        bd_path = os.path.join(tmp, "canis_mcmc.log")
        _write(bd_path, "\n".join(bdmcmc) + "\n")

        fixed = ["posterior\tPP_lik\tBD_lik\tq_rate\tbeta\tlambda_0\tlambda_1\tmu_0\t"
                 "mu_1\tshift_sp_1\tshift_ex_1\thypL\thypM"]
        for i in range(6):
            fixed.append("9%d\t3%d\t1%d\t0.4\t0.5\t0.1\t0.2\t0.05\t0.06\t7.5\t6.1\t1.0\t2.0"
                         % (i, i, i))
        fx_path = os.path.join(tmp, "fixed_mcmc.log")
        _write(fx_path, "\n".join(fixed) + "\n")

        mr_path = os.path.join(tmp, "canis_marginal_rates.log")
        _write(mr_path, "\n".join("1.%d\t0.%d\t0.%d" % (i, i, i) for i in range(5)) + "\n")
        ml_path = os.path.join(tmp, "canis_marginal_likelihood.txt")
        _write(ml_path, "-123.456\n")
        sum_path = os.path.join(tmp, "canis_sum.txt")
        _write(sum_path, "Input file: canis_PyRate.py\nNumber of MCMC generations: 10000\n"
                         "Preservation model: -mG\nNumber of categories: -ncat 4\n")
        sp_path = os.path.join(tmp, "canis_sp_rates.log")
        _write(sp_path, "some\tunlabelled\tcolumns\n1\t2\t3\n")
        se_path = os.path.join(tmp, "canis_se_est.txt")
        _write(se_path, "# provenance comment line, must be skipped\n"
                        "clade\tid\torigin\textinction\n0\t1\t9.9\t0.0\n0\t2\t5.0\t2.0\n")
        odd_path = os.path.join(tmp, "readme.md")
        _write(odd_path, "not a PyRate output\n")
        bad_path = os.path.join(tmp, "broken_mcmc.log")
        _write(bad_path, "posterior\tPP_lik\nnot-a-number\tx\n")
        nohdr = os.path.join(tmp, "nohdr_mcmc.log")
        _write(nohdr, "1\t2\t3\n4\t5\t6\n")

        ns = argparse.Namespace(b=None, max_rows=8, max_lines=400000)

        def run(paths, **kw):
            for k, v in kw.items():
                setattr(ns, k, v)
            rep, probs, skipped = parse_targets(paths, ns)
            return rep, probs, skipped

        rep, _p, _s = run([bd_path])
        text = "\n".join(rep[0]["lines"])
        expect("samples=10" in text, "bd case: sample count missing: %r" % text)
        expect("k_birth" in text and "shift counts" in text,
               "bd case: shift histogram missing: %r" % text)
        expect("BDMCMC" in text, "bd case: mode evidence missing: %r" % text)
        expect("Canis_ferox_TS" in text and "per-taxon times" in text,
               "bd case: TS/TE block missing: %r" % text)
        expect(text.count("format not documented") >= 1,
               "bd case: expected an honest %r note" % UNDOCUMENTED)
        expect(len(rep[0]["lines"]) < 60,
               "a 17-column mcmc.log block must stay bounded, got %d lines"
               % len(rep[0]["lines"]))

        rep, _p, _s = run([fx_path])
        text = "\n".join(rep[0]["lines"])
        expect("-A 0" in text and "-A 1" in text,
               "fixed case: lambda/shift evidence missing: %r" % text)
        expect("hypL" in text, "fixed case: hypL/hypM (T1:257) missing: %r" % text)

        rep, _p, _s = run([mr_path])
        text = "\n".join(rep[0]["lines"])
        expect("column layout: format not documented" in text,
               "marginal_rates must say %r: %r" % (UNDOCUMENTED, text))

        rep, _p, _s = run([ml_path])
        expect("-123.456" in " ".join(rep[0]["lines"]), "marginal likelihood value missing")
        expect("-BF" in " ".join(rep[0]["lines"]), "the -BF follow-up line is missing")

        rep, _p, _s = run([sum_path])
        text = "\n".join(rep[0]["lines"])
        expect("-ncat" in text and "-mG" in text,
               "sum keyword scan lost the options: %r" % text)
        expect("field layout: format not documented" in text,
               "sum must label its layout %r" % UNDOCUMENTED)

        rep, _p, _s = run([sp_path])
        expect("format not documented" in " ".join(rep[0]["lines"]),
               "sp_rates must refuse to guess the layout")

        rep, _p, _s = run([se_path])
        text = "\n".join(rep[0]["lines"])
        expect("rows=2" in text and "clade assignment" in text,
               "se_est digest wrong: %r" % text)

        rep, probs, skipped = run([tmp])
        stems = set(e["stem"] for e in rep)
        expect("_mcmc.log" in stems and "_sum.txt" in stems and "_se_est.txt" in stems,
               "directory walk missed stems: %r" % stems)
        expect(odd_path in skipped, "directory walk should skip readme.md, not warn")
        expect(rep, "directory walk found nothing")

        rep, probs, _s = run([odd_path])
        expect(not rep and any("not a documented PyRate output name" in p for p in probs),
               "unknown single file must be reported: %r" % probs)

        rep, _p, _s = run([bad_path])
        text = "\n".join(rep[0]["lines"])
        expect("posterior: n=0" in text or "no numeric values parsed" in text,
               "non-numeric rows must degrade, not crash: %r" % text)

        rep, _p, _s = run([nohdr])
        expect(UNDOCUMENTED in " ".join(rep[0]["lines"]),
               "header-less log must be labelled %r" % UNDOCUMENTED)

        rep, _p, _s = run([bd_path], b=0.5)
        expect("kept" in " ".join(rep[0]["lines"]), "--b fraction note missing")
        rep, _p, _s = run([bd_path], b=3)
        expect("7 of 10" in " ".join(rep[0]["lines"]),
               "--b count arithmetic wrong: %r" % " ".join(rep[0]["lines"]))
        rep, _p, _s = run([bd_path], max_rows=2)
        text = "\n".join(rep[0]["lines"])
        expect("more" in text and len(rep[0]["lines"]) < 40,
               "output is not bounded by --max-rows: %d lines" % len(rep[0]["lines"]))

        _p, probs, _s = run([os.path.join(tmp, "does_not_exist_mcmc.log")])
        expect(any("not a documented" in p or "not found" in p for p in probs),
               "missing file must produce a message: %r" % probs)

        payload = {"files": [{k: v for k, v in e.items() if k != "lines"} for e in rep],
                   "problems": probs}
        json.dumps(payload)
        expect(json.loads(json.dumps(payload))["files"], "json payload is empty")

        out = render_text(rep, probs, [], ns).splitlines()
        expect(len(out) < 120, "self-test output unbounded: %d lines" % len(out))
        stem_lines = print_stems(lines=True)
        expect(any("_marginal_likelihood.txt" in l for l in stem_lines),
               "--stems must list the TI file")
        expect(documented_options().count("-ncat") == 1,
               "command-list mirror could not be re-parsed for the keyword scan")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        for f in fails:
            print("SELF-TEST FAIL: %s" % f)
        print("parse_results.py self-test: FAILED (%d/%d assertions)"
              % (len(fails), checks[0]))
        return 1
    print("parse_results.py self-test: OK (%d assertions on 11 temp fixtures: BDMCMC / "
          "fixed-shift / header-less mcmc.log, marginal_rates, marginal_likelihood, "
          "sum.txt, sp_rates, se_est, unknown names, --b, --max-rows, --json payload)"
          % checks[0])
    return 0


# ------------------------------------------------------------------------------ main
def build_parser():
    ap = argparse.ArgumentParser(prog="parse_results.py", add_help=True,
                                 description="Digest PyRate output files with citations "
                                             "(read-only, stdlib-only).",
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__.split("USAGE")[0])
    ap.add_argument("paths", nargs="*", metavar="PATH")
    ap.add_argument("--b", type=float, default=None, metavar="N",
                    help="report the effect of discarding N samples (0<N<1 = fraction)")
    ap.add_argument("--stems", action="store_true",
                    help="print the documented output-file stems and exit")
    ap.add_argument("--json", action="store_true", help="emit one JSON object")
    ap.add_argument("--max-rows", type=int, default=8, metavar="N",
                    help="per-column statistics to print, 1-200 (default 8)")
    ap.add_argument("--max-lines", type=int, default=400000, metavar="N",
                    help="read at most N lines per file (default 400000)")
    ap.add_argument("--self-test", action="store_true",
                    help="build temp fixtures and assert behaviour")
    return ap


def main(argv=None):
    ap = build_parser()
    try:
        args = ap.parse_args(argv)
    except SystemExit as exc:                     # argparse already printed usage
        return int(exc.code) if exc.code else 0
    if args.self_test:
        return self_test()
    if args.stems:
        print_stems()
        return 0
    if not args.paths:
        print(__doc__)
        print("\ndocumented stems:")
        print_stems()
        return 2
    if args.max_rows < 1 or args.max_rows > 200:
        print("error: --max-rows must be in 1-200", file=sys.stderr)
        return 2
    if args.b is not None and args.b < 0:
        print("error: --b must be >= 0 (0 keeps every sample)", file=sys.stderr)
        return 2
    report, problems, skipped = parse_targets(args.paths, args)
    if args.json:
        print(json.dumps({
            "ok": bool(report),
            "targets": args.paths,
            "recognised": len(report),
            "ignored": skipped,
            "problems": problems,
            "undocumented_layout_wording": UNDOCUMENTED,
            "files": [{"path": e["path"], "stem": e["stem"], "citation": e["citation"],
                       "documented_as": e["documented_as"],
                       "text": e["lines"], "data": e["data"]} for e in report],
        }, ensure_ascii=False, indent=1))
        return 0 if report else 1
    print(render_text(report, problems, skipped, args))
    return 0 if report else 1


if __name__ == "__main__":
    sys.exit(main())
