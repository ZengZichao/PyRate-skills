#!/usr/bin/env python3
"""Completeness gate for the PyRate skills suite.

Mirroring every page into references/ proves nothing about *use*: a suite can ship
perfect mirrors and still leave most documented behaviour unmentioned. This script
therefore derives the inventory from the corpus itself (nothing is hand-listed, so
the check cannot be talked into passing) and then proves each item is actually named
by some SKILL.md.

Axes, all harvested from the documentation corpus (default: `../PyRate-doc` relative to the suite root, override with `--corpus`):

  tier 1  commands the corpus *heads*: every `##### <name>` heading
  tier 2  commands the corpus documents *only by usage*: `-flag` tokens appearing in
          code contexts (fenced blocks / inline spans) of the tutorial and wiki pages
          that never head their options. Harvested from code contexts only, which
          excludes prose hyphenation.
  tier 3  other documented surfaces: non-base-R functions the docs tell you to call,
          output artefacts a run writes, and model/algorithm names.
  sections every level 1-3 heading of every page (traceability, not verbatim).

Commands (tier 1 + tier 2) are HARD: a documented option no SKILL.md names is a hole
in the suite. Sections, functions, artefacts and model names are SOFT by default and
become hard under --strict.

    python3 scripts/audit_coverage.py [--corpus PATH] [--strict] [--dump-inventory F]
                                       [--self-test]

--self-test asserts the harvester's own invariants on synthetic strings, with no corpus
and no suite file read, so a rule that goes blunt is caught here rather than silently
dropping documented commands from the inventory.
"""
import argparse
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SUITE = os.path.dirname(HERE)
DEFAULT_CORPUS = os.path.join(os.path.dirname(SUITE), "PyRate-doc")

W = "PyRate-wiki"
T = "PyRate-tutorials/tutorials"

PAGES = [
    f"{W}/Home.md",
    f"{W}/1.-Preparing-input-file.md",
    f"{W}/2.-PyRate:-command-list.md",
    f"{W}/3.-Summarize-PyRate-results.md",
    f"{W}/4.-PyRateContinuous.md",
    f"{W}/5.-Dispersal-Extinction-Sampling-model.md",
    f"{T}/README.md",
    f"{T}/pyrate_tutorial_0.md",
    f"{T}/pyrate_tutorial_1.md",
    f"{T}/pyrate_tutorial_2.md",
    f"{T}/pyrate_tutorial_3.md",
    f"{T}/pyrate_tutorial_4.md",
    f"{T}/pyrate_tutorial_5.md",
    f"{T}/pyrate_tutorial_6.md",
    f"{T}/pyrate_tutorial_bdnn.md",
]

# One skill owns each page; several pages are subdivided by heading keyword below.
PAGE_SKILL = {
    f"{W}/Home.md": "pyrate",
    f"{W}/1.-Preparing-input-file.md": "pyrate-input-file",
    f"{W}/2.-PyRate:-command-list.md": "pyrate-command-reference",
    f"{W}/3.-Summarize-PyRate-results.md": "pyrate-summarize-results",
    f"{W}/4.-PyRateContinuous.md": "pyrate-continuous-covariates",
    f"{W}/5.-Dispersal-Extinction-Sampling-model.md": "pyrate-des",
    f"{T}/README.md": "pyrate",
    f"{T}/pyrate_tutorial_0.md": "pyrate-installation",
    f"{T}/pyrate_tutorial_1.md": "pyrate-bd-analysis",
    f"{T}/pyrate_tutorial_2.md": "pyrate-summarize-results",
    f"{T}/pyrate_tutorial_3.md": "pyrate-rjmcmc",
    f"{T}/pyrate_tutorial_4.md": "pyrate-diversity-dependence",
    f"{T}/pyrate_tutorial_5.md": "pyrate-des",
    f"{T}/pyrate_tutorial_6.md": "pyrate-mcmc-tuning",
    f"{T}/pyrate_tutorial_bdnn.md": "pyrate-bdnn",
}

REROUTE = [
    (("input file", "generate pyrate input", "species name", "typo", "spelling", "site"), "pyrate-input-file"),
    (("preservation", "fossilization", "mhpp", "qshift", "mg", "ncat", "model testing across preservation"), "pyrate-preservation-models"),
    (("install", "virtual environment", "compatibility", "requirements", "path"), "pyrate-installation"),
    (("output file", "summar", "plot", "extract estimated", "range-through", "lineage through time", "diversity trajectory"), "pyrate-summarize-results"),
    (("rjmcmc", "reversible jump", "rate shift", "large dataset", "constrain"), "pyrate-rjmcmc"),
    (("pyratecontinuous", "time-continuous", "time continuous", "thermodynamic integration", "diversity dependent", "diversity-dependent"), "pyrate-continuous-covariates"),
    (("mcdd", "multiple-clade", "multiple clade", "multivariate", "mbd"), "pyrate-diversity-dependence"),
    (("trait", "covar", "age dependent", "age-dependent", "chronospecies", "ade", "bdc"), "pyrate-trait-age-models"),
    (("dispersal", "des", "area", "biogeograph"), "pyrate-des"),
    (("bdnn", "neural network", "predictor", "partial dependence"), "pyrate-bdnn"),
    (("burnin", "burn-in", "tuning", "mcmc", "convergen", "chain"), "pyrate-mcmc-tuning"),
]

EXPECTED_SKILLS = [
    "pyrate", "pyrate-input-file", "pyrate-command-reference", "pyrate-installation",
    "pyrate-bd-analysis", "pyrate-preservation-models", "pyrate-rjmcmc",
    "pyrate-summarize-results", "pyrate-continuous-covariates",
    "pyrate-diversity-dependence", "pyrate-trait-age-models", "pyrate-des",
    "pyrate-bdnn", "pyrate-mcmc-tuning",
]

# `#####` heads a documented command; the `\s*` matters: the corpus writes
# `#####`-wd`` with no space, and requiring whitespace silently drops two commands.
HEAD_CMD = re.compile(r"^#####\s*(.+?)\s*$")
HEAD_SEC = re.compile(r"^(#{1,3})\s+(.+?)\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")
INLINE = re.compile(r"`([^`\n]+)`")
FLAG = re.compile(r"(?<![\w-])-([A-Za-z_][A-Za-z0-9_]*)")
CALL = re.compile(r"\b([A-Za-z][A-Za-z0-9._]{2,})\s*\(")
ARTEFACT = re.compile(r"([\w.*\-]*\.(?:log|txt|pdf|png|rdata|csv|tre|summary|R|r|py|html))\b", re.I)
MODEL = re.compile(r"\b(NHPP|HPP|TPP|BDMCMC|RJMCMC|MCMC|MCDD|MBD|BDNN|ADE|BDC|DES|Covar|Skyline|Gamma|PERT|TI)\b")

# pip/venv/shell switches and single letters that are never PyRate options
DENY = {"h", "y", "o", "m", "t", "e", "p", "a", "b", "i", "l", "v", "u", "g", "w", "x", "z",
        "f", "q", "k", "r", "upgrade", "index", "bash", "sh", "rf", "R", "lm", "dev", "tools",
        "add", "c", "E", "V"}
DENY -= {"v"}  # `-v` IS documented (pyrate_tutorial_0.md:41, print the version)

BASE_R = set("""c list data.frame read.table write.table read.csv source library require
install.packages setwd getwd print paste paste0 sapply lapply apply t names head tail str
summary plot hist seq rep length dim which unique sort order cbind rbind is.na na.omit
identical format round max min mean colSums rowSums file.path dir.create sessionInfo dev.off
pdf png as.data.frame as.matrix matrix numeric character function return if for while system
file.exists unlist do.call grep gsub subset merge levels factor sample set.seed par lines
points abline legend axis box text title""".split())


def clean(text):
    text = text.strip().strip("`").strip()
    text = re.sub(r"<[^>]+>", "", text)
    return text.replace("\\#", "#").strip()


def reroute(heading, default):
    low = heading.lower()
    for keys, skill in REROUTE:
        if any(k in low for k in keys):
            return skill
    return default


def code_lines(lines):
    """(lineno, text) for every line living in a code context."""
    out, inside = [], False
    for i, raw in enumerate(lines, start=1):
        if FENCE.match(raw):
            inside = not inside
            continue
        if inside:
            out.append((i, raw))
        else:
            out.extend((i, s) for s in INLINE.findall(raw))
    return out


def build_inventory(corpus):
    pages, sections, commands = [], [], []
    for rel in PAGES:
        full = os.path.join(corpus, rel)
        if not os.path.exists(full):
            raise SystemExit("corpus page missing: %s" % full)
        lines = open(full, encoding="utf-8").read().splitlines()
        pages.append({"page": rel, "owner": PAGE_SKILL[rel], "lines": len(lines)})
        cur = None
        for i, raw in enumerate(lines, start=1):
            mc, ms = HEAD_CMD.match(raw), HEAD_SEC.match(raw)
            if mc:
                name = clean(mc.group(1))
                if name:
                    commands.append({"command": name, "page": rel, "line": i, "tier": 1,
                                     "kind": "output-file" if re.match(r"^_?\*", name) else "command",
                                     "section": cur, "owner": reroute(name, PAGE_SKILL[rel])})
            elif ms:
                title = clean(ms.group(2))
                if not title or title.lower().startswith("pyrate tutorial"):
                    continue
                cur = title
                sections.append({"title": title, "depth": len(ms.group(1)), "page": rel,
                                 "line": i, "owner": reroute(title, PAGE_SKILL[rel])})

    headed = {c["command"].strip("_").lstrip("-").lower() for c in commands}
    by_usage, seen = [], set()
    funcs, artefacts = {}, {}
    models = collections.defaultdict(list)
    for rel in PAGES:
        lines = open(os.path.join(corpus, rel), encoding="utf-8").read().splitlines()
        owner = PAGE_SKILL[rel]
        for lineno, text in code_lines(lines):
            for m in FLAG.finditer(text):
                tok = m.group(1)
                if tok in DENY or tok.lower() in headed or (rel, tok) in seen:
                    continue
                if not (re.search(r"[A-Z]", tok) or "_" in tok or len(tok) <= 3):
                    continue
                seen.add((rel, tok))
                by_usage.append({"command": "-" + tok, "page": rel, "line": lineno, "tier": 2,
                                 "kind": "command-by-usage", "owner": owner})
            for m in CALL.finditer(text):
                n = m.group(1)
                if n in BASE_R or n.lower() in BASE_R:
                    continue
                if "." not in n and "_" not in n and not n[0].isupper() and len(n) < 5:
                    continue
                funcs.setdefault(n, (rel, lineno))
            for m in ARTEFACT.finditer(text):
                artefacts.setdefault(m.group(1), (rel, lineno))
        for lineno, raw in enumerate(lines, start=1):
            for m in MODEL.finditer(raw):
                models[m.group(1)].append("%s:%d" % (rel, lineno))

    return {
        "corpus": corpus, "pages": pages, "sections": sections, "commands": commands,
        "commands_by_usage": by_usage,
        "r_functions": [{"name": k, "page": v[0], "line": v[1]} for k, v in sorted(funcs.items())],
        "artefacts": [{"name": k, "page": v[0], "line": v[1]} for k, v in sorted(artefacts.items())],
        "models": [{"name": k, "count": len(v), "first": v[0]} for k, v in sorted(models.items())],
    }


def skill_bodies():
    out = {}
    for name in sorted(os.listdir(SUITE)):
        p = os.path.join(SUITE, name, "SKILL.md")
        if os.path.isfile(p):
            out[name] = open(p, encoding="utf-8").read()
    return out


def tok_re(tok):
    esc = re.escape(tok.strip("_").replace("*", "\x00"))
    return re.compile(r"(?<![A-Za-z0-9_-])" + esc.replace("\x00", ".*") + r"(?![A-Za-z0-9_-])", re.I)


def self_test():
    """Assert this harvester's own invariants on strings it carries -- no corpus read.

    The coverage gate is only meaningful if the inventory it derives from the corpus is
    the inventory the docs actually print. Every rule below is the reason one documented
    command would otherwise be missed (a `#####` heading written with no space, an option
    harvested out of a code context only, a pip switch that is not a PyRate option), so
    each is pinned here on synthetic input that needs nothing but the standard library.
    """
    run, bad = [0], []

    def ok(cond, msg):
        run[0] += 1
        if not cond:
            bad.append(msg)

    # the plan: every page has exactly one owning skill, and every owner is a real skill
    ok(len(EXPECTED_SKILLS) == 14, "the plan names %d skills, not 14" % len(EXPECTED_SKILLS))
    ok(len(set(EXPECTED_SKILLS)) == len(EXPECTED_SKILLS), "EXPECTED_SKILLS has a duplicate")
    ok(len(PAGES) == len(set(PAGES)) == 15, "PAGES must be 15 distinct corpus pages")
    ok(set(PAGE_SKILL) == set(PAGES), "PAGE_SKILL and PAGES disagree: %s"
       % sorted(set(PAGE_SKILL) ^ set(PAGES)))
    ok(all(v in EXPECTED_SKILLS for v in PAGE_SKILL.values()),
       "a page is owned by a skill outside the plan")
    ok(all(skill in EXPECTED_SKILLS for _, skill in REROUTE),
       "REROUTE sends work to a skill outside the plan")

    # tier 1: a `#####` command heading, with or without the space the corpus omits; the
    # angle-bracket placeholder is markup, so clean() takes it off the option name
    ok(clean(HEAD_CMD.match("##### `-n <int>`").group(1)) == "-n",
       "a spaced command heading is harvested (%r)"
       % clean(HEAD_CMD.match("##### `-n <int>`").group(1)))
    ok(clean(HEAD_CMD.match("#####`-wd <str>`").group(1)) == "-wd",
       "the no-space spelling the corpus uses is harvested too (%r)"
       % clean(HEAD_CMD.match("#####`-wd <str>`").group(1)))
    ok(HEAD_SEC.match("##### `-n <int>`") is None,
       "a command heading must not also be counted as a section")
    ok(HEAD_SEC.match("### 2. Output files").groups() == ("###", "2. Output files"),
       "a section heading keeps its depth and title")
    ok(clean("plotRJ \\# with an escaped hash") == "plotRJ # with an escaped hash",
       "clean() unescapes the markdown hash")

    # code contexts: fenced lines and inline spans are harvested, fences themselves are not
    got = code_lines(["prose with `inline_flag -qtime` here", "```",
                      "python PyRate.py -ginput", "```", "after `x -y`"])
    ok(got == [(1, "inline_flag -qtime"), (3, "python PyRate.py -ginput"), (5, "x -y")],
       "code_lines returns %s" % got)

    # tier 2: options are read out of code contexts only, and pip switches are not options
    ok(FLAG.findall("python PyRate.py -ginput -n 10 -rf tmp --index-url http")
       == ["ginput", "n", "rf"], "FLAG overharounds prose hyphens and long options")
    ok(FLAG.findall("the time-continuous model, -v, then 2 - 3") == ["v"],
       "a hyphenated word or a minus sign is not an option")
    ok("v" not in DENY, "-v is documented (print the version) and must stay in the inventory")
    ok({"rf", "upgrade", "index", "c", "E"} <= DENY, "pip/shell switches must stay denied")
    ok(not (DENY & {"ginput", "BDNNmodel", "fixShift"}), "no documented PyRate option is denied")

    # the soft axes
    ok(sorted(CALL.findall("check_names(SpeciesList) and data.frame(a)")) ==
       sorted(["check_names", "data.frame"]), "a documented call is harvested")
    ok("read.table" in BASE_R and "check_names" not in BASE_R,
       "BASE_R filters base R and nothing else")
    ok(ARTEFACT.findall("writes *_mcmc.log and combined_summary.txt now") ==
       ["*_mcmc.log", "combined_summary.txt"], "output artefacts are harvested")
    ok(MODEL.findall("under NHPP with BDMCMC and MCDD but not mcmc") ==
       ["NHPP", "BDMCMC", "MCDD"], "model names are harvested case-sensitively")

    # ownership: a heading is routed to the skill that must document it
    ok(reroute("Generating the PyRate input file", "pyrate") == "pyrate-input-file",
       "an input-file heading stays with the input skill")
    ok(reroute("Plot the rates", "pyrate") == "pyrate-summarize-results",
       "a plot heading is rerouted to the summarising skill")
    ok(reroute("Something with no keyword at all", "pyrate-des") == "pyrate-des",
       "an unrouted heading keeps the page owner")
    ok(all(reroute(t, "pyrate") in EXPECTED_SKILLS for t in
           ("MCMC tuning parameters", "BDNN predictor influence", "DES areas",
            "Preservation models", "Rate shifts", "Output files")),
       "rerouting never invents a skill")

    # matching a SKILL.md: token boundaries, so -n cannot be covered by -name
    ok(tok_re("-n").search("run `-n 100` here") and not tok_re("-n").search("use -name x"),
       "an option token must match whole, not as a prefix")
    ok(tok_re("*_mcmc.log").search("combined_1_mcmc.log written"),
       "the artefact wildcard matches a real file name")

    print("audit_coverage.py self-test: %s (%d checks, %d failure(s))"
          % ("OK" if not bad else "FAILED", run[0], len(bad)))
    for b in bad:
        print("  SELF-TEST FAIL: %s" % b)
    return 0 if not bad else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default=DEFAULT_CORPUS)
    ap.add_argument("--strict", action="store_true", help="soft axes become fatal too")
    ap.add_argument("--dump-inventory", metavar="FILE")
    ap.add_argument("--self-test", action="store_true",
                    help="assert this harvester's own invariants on synthetic input")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    x = build_inventory(a.corpus)
    if a.dump_inventory:
        json.dump(x, open(a.dump_inventory, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("inventory written: %s" % a.dump_inventory)

    bodies = skill_bodies()
    all_text = "\n".join(bodies.values())
    print("corpus pages: %d (%d lines)   skills with SKILL.md: %d"
          % (len(x["pages"]), sum(p["lines"] for p in x["pages"]), len(bodies)))

    inventory = x["commands"] + x["commands_by_usage"]
    missing, covered, per_owner = [], 0, {}
    for c in inventory:
        name = c["command"].strip("_")
        own = per_owner.setdefault(c["owner"], [0, 0, []])
        own[1] += 1
        if tok_re(name).search(all_text):
            covered += 1
            own[0] += 1
        else:
            missing.append(c)
            own[2].append(name)

    print("\nCOMMAND SURFACE (hard): %d/%d  [%d headed + %d documented only by usage]"
          % (covered, len(inventory), len(x["commands"]), len(x["commands_by_usage"])))
    for own in sorted(per_owner):
        got, tot, miss = per_owner[own]
        print("  %s %-32s %3d/%-3d%s" % ("OK " if got == tot else "GAP", own, got, tot,
                                         ("   missing: " + " ".join(miss[:14]) +
                                          (" ..." if len(miss) > 14 else "")) if miss else ""))
    if missing:
        print("\nHARD MISSES - documented commands no SKILL.md names:")
        for c in missing:
            print("  %-28s %s:%d  (owner %s)" % (c["command"], c["page"], c["line"], c["owner"]))

    low = all_text.lower()
    sec_miss = []
    for s in x["sections"]:
        t = s["title"]
        if len(t) < 4:
            continue
        if t.lower() in low:
            continue
        words = [w for w in re.split(r"[^A-Za-z0-9]+", t) if len(w) > 4]
        if words and sum(1 for w in words if w.lower() in low) >= max(1, len(words) - 1):
            continue
        sec_miss.append(s)
    print("\nSECTION TRACEABILITY (soft): %d/%d" % (len(x["sections"]) - len(sec_miss), len(x["sections"])))
    for s in sec_miss[:40]:
        print("  GAP %-58s %s:%d" % (s["title"][:58], s["page"].split("/")[-1], s["line"]))

    for key, label in (("r_functions", "R/PYTHON FUNCTIONS"), ("models", "MODEL NAMES")):
        items = x[key]
        hit = [i for i in items if tok_re(i["name"]).search(all_text)]
        print("\n%s (soft): %d/%d" % (label, len(hit), len(items)))
        for i in items:
            if i not in hit:
                print("  GAP %s  (%s:%s)" % (i["name"], i["page"].split("/")[-1], i["line"]))

    art = x["artefacts"]
    ahit = [i for i in art if tok_re(i["name"].replace("*", "*")).search(all_text)]
    print("\nOUTPUT ARTEFACTS (soft): %d/%d" % (len(ahit), len(art)))
    for i in art:
        if i not in ahit:
            print("  GAP %s  (%s:%d)" % (i["name"], i["page"].split("/")[-1], i["line"]))

    absent = [s for s in EXPECTED_SKILLS if s not in bodies]
    if absent:
        print("\nSKILLS MISSING SKILL.md: " + ", ".join(absent))
    extra = [s for s in bodies if s not in EXPECTED_SKILLS]
    if extra:
        print("SKILLS NOT IN THE PLAN: " + ", ".join(extra))

    soft_fail = bool(sec_miss) or len(hit) < len(x["models"])
    rc = 1 if (missing or absent or extra or (a.strict and soft_fail)) else 0
    print("\nRESULT: %s  (hard command misses: %d, skills: %d, soft gaps: %d%s)"
          % ("PASS" if rc == 0 else "FAIL", len(missing), len(bodies),
             len(sec_miss), ", --strict" if a.strict else ""))
    return rc


if __name__ == "__main__":
    sys.exit(main())
