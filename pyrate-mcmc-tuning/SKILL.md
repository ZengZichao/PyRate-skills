---
name: pyrate-mcmc-tuning
description: "Tune and debug the PyRate (BD)MCMC engine: -fast_burnin (approximate Gibbs sampler on origination/extinction times, default 0); the ten Tuning parameters -multiR (0 sliding window versus 1 multiplier), -tR (0.05), -tT (1), -nT (5; -nT 0 is a model change, not a tuning one), -tQ (q and gamma shape alpha, 1.2 1.2), -tS (1), -fS (0.7), -tC (0.025 0.025 0.1), -fU (0.02 0.18 0.08), -fR (1); the Advanced (BD)MCMC settings -r, -t, -sw (MC3 heated chains), -k, -a (TI scaling points), -M, -B, -T, -S (BDMCMC model updates); and -n, -s, -p, -b, -thread. Gated by Tutorial 1's triage rule: change the -t and -f knobs only when experiencing convergence issues - never instead of settling the settings that change the basic model assumptions or the length of the analyses (-A, -n, -s, -b, -j). Covers burnin feeding -mProb and -plot, why -A 1 TI needs a non-default -b, silent no-op knobs, the -fixSE/-fixShift slip inside -fS, and what these four mirrors never document (no ESS, Rhat, autocorrelation or Tracer)."
---

# PyRate MCMC tuning, burnin and proposal knobs

## Overview

PyRate's (BD)MCMC is steered by three families of flags that the mirrors keep in three separate
sections: the main run settings (`-n`, `-s`, `-p`, `-b`, `-thread`), the nine Advanced (BD)MCMC
settings (`-r`, `-t`, `-sw`, `-k`, `-a`, `-M`, `-B`, `-T`, `-S`), and the ten Tuning parameters
(`-multiR`, `-tR`, `-tT`, `-nT`, `-tQ`, `-tS`, `-fS`, `-tC`, `-fU`, `-fR`) that decide what each
iteration proposes, plus `-fast_burnin`. This skill records, knob by knob, what the docs say it
does, its printed default, which other command gates it, and which ones silently do nothing unless
the matching model is on. It also marks the gap these four mirrors never close: they name a symptom
for one knob only (`-fR` and "mixing"), and they contain no convergence diagnostic at all (§9). That
is a statement about four pages, not about PyRate — the convergence guidance this corpus does have
is a triage rule on Tutorial 1 that says when you are allowed to touch any knob here at all, and it
comes before every step in §8 (§8.0).

Evidence base: four local mirrors — `references/tutorial-6.md` + `references/tutorial-6-cn.md` (the
page titled `# PyRate - Advanced settings`, tutorial-6.md:9) and `references/command-list.md` +
`references/command-list-cn.md` (the command list). Line numbers are of the MIRRORS, frontmatter
included. `[CN: file:line ...]` marks a claim additionally checked against the Chinese twin. Lines
marked **[inference]** are my reading, not the docs'.

## 0. The docs' own vocabulary

- **Three sections, not one.** `-n`, `-s`, `-p`, `-b`, `-thread` sit under `### Main analysis
  settings` [command-list.md:45]; `-r`, `-t`, `-sw`, `-k`, `-a`, `-M`, `-B`, `-T`, `-S` under
  `### Advanced (BD)MCMC settings` [command-list.md:192] `[CN: command-list-cn.md:191
  「高级 (BD)MCMC 设置」]`; the ten proposal knobs under `### Tuning parameters`
  [command-list.md:230; tutorial-6.md:17]. That header occurs exactly twice inside these four mirrors
  — but the command-list page is mirrored in six sibling skills too, so a suite-wide
  `grep -rn "^### Tuning parameters" .. --include="*.md"` returns 7. My evidence base is the two EN
  pages plus their twins: `grep -n "Tuning parameters" references/command-list.md
  references/tutorial-6.md`.
- **The only named symptom in the whole vocabulary is "mixing", and it names one knob.**
  `grep -rn "mixing" references/` returns four hits — the same `-fR` sentence on both pages plus its
  two CN twins [command-list.md:268; tutorial-6.md:54], glossed 「混合（mixing）」 in Chinese. No
  window or frequency knob is given a symptom.
- **The only occurrence of "convergence"** in all four mirrors is inside `-fast_burnin`
  [references/tutorial-6.md:14] (`grep -rni "converg" references/` returns that one line), CN 「以加快收敛」
  [references/tutorial-6-cn.md:15] `[CN]`. Nothing **in these four mirrors** tells you how to observe
  it — which is not the same as nothing in the corpus: Tutorial 1 tells you to open the logs in Tracer
  and read the ESS [../pyrate-bd-analysis/references/tutorial-1.md:205], and the summarise page
  recommends the same before choosing a burnin
  [../pyrate-summarize-results/references/summarize-results.md:64]. See the Tracer/ESS rows of §9 —
  the → rows are the pointers to those two mirrors — and §8.0 for the triage rule that every knob in
  this skill sits under.
- **`-fast_burnin` lives on one page only.** It is defined at tutorial-6.md:13-14 and appears zero
  times in the command list (counting recipe, §11).
- **Burnin has three different Chinese renderings**: the section heading 「快速烧录期（Fast burnin）」
  [tutorial-6-cn.md:13], `-b`'s 「烧录期（burn-in）」 [command-list-cn.md:70], and `-S`'s
  「在烧录期之后」 [command-list-cn.md:225] `[CN]`. Grep 「烧」 before trusting a translated term.

## 1. Fast burnin

| Command | Documented text | Default |
|---|---|---|
| `-fast_burnin <int>` | "Specify number of MCMC iterations using approximate Gibbs sampler for times of origination and extinction for faster convergence" [tutorial-6.md:14] | "(default: `-fast_burnin 0`)" [tutorial-6.md:14] |

- The value is a **number of iterations**, not a flag: the heading types it `-fast_burnin <int>`
  [tutorial-6.md:13], the only place its type is written down; `-multiR <boolean>` and `-tT <float>`
  are likewise typed only on this page [tutorial-6.md:18,21]; the command list prints those two bare
  [command-list.md:231,235] and never names `-fast_burnin` at all (§7 hazard 1).
- `0` — the documented default — means no Gibbs phase at all: the plain (BD)MCMC runs from the first
  generation [tutorial-6.md:14].
- What the phase does is named and nothing else: an "approximate Gibbs sampler" for "times of
  origination and extinction" [tutorial-6.md:14]. No mirror says which parameters it touches, what it
  costs per iteration, how long it should be, or how you would notice it worked (§9).
- `-fast_burnin` carries **no** "used only when" clause, unlike all nine advanced settings
  [command-list.md:194-226, per-command lines in §3] and unlike `-ncat` [command-list.md:101].
  **[inference]** Which `-A` analyses accept `-fast_burnin` is therefore unstated; do not promise it
  works with `-A 1` or `-A 3`.

### 1.1 `-fast_burnin` in the run-length accounting (it is counted in iterations; the ledger around it mixes units)

`-fast_burnin` takes a bare integer, so the only way to size it is against the commands that also
count. This table is the whole ledger these four mirrors allow; every row's unit is the mirror's own
wording.

| Command | Unit the mirror states | Source | What it does for `-fast_burnin` |
|---|---|---|---|
| `-fast_burnin <int>` | "Specify number of MCMC iterations using approximate Gibbs sampler for times of origination and extinction for faster convergence" | [references/tutorial-6.md:13-14] | the currency is **iterations**, and no non-zero example exists (§9) |
| `-n` | "Number of MCMC or BDMCMC generations." | [references/command-list.md:57] | the same currency, so **[inference]** `-fast_burnin` must be read as a prefix of the `-n` budget — no mirror says whether the Gibbs phase runs inside `-n` or on top of it, nor whether the `-s` clock starts before or after it |
| `-s` | "MCMC sampling frequency." with printed `-s 1000` | [references/command-list.md:61-62] | whether a sample taken during the Gibbs phase reaches the log is **not documented**; Tutorial 1 states the arithmetic only for a plain run ("the resulting log files (see below) will include 4,000 posterior samples", ../pyrate-bd-analysis/references/tutorial-1.md:188) |
| `-b` | "Set the number of iterations to be discarded (i.e. not logged)" — but its own example line says "(first 1,000 samples are discarded)" | [references/command-list.md:69; :72] | `-b` is written in both currencies at once (hazard 5), so no arithmetic between `-fast_burnin` and `-b` is safe; budget them separately |
| `-S` | "the number of generations after which the BDMCMC algorithm will start updating the model (e.g. after a burn-in phase)" | [references/command-list.md:226] | a second, `-A 2`-only phase boundary expressed in generations; **no mirror orders `-fast_burnin` and `-S` against each other** |
| `-p` | "MCMC print-on-screen frequency." | [references/command-list.md:65] | the only per-iteration signal it produces goes to the screen, not to a file (§5 item 5) |

The sibling RJMCMC page documents the other approximate-Gibbs route and does state what it costs and
where it applies: `-se_gibbs` is offered when very large runs "may require long computing
time for the MCMC to reach convergence"
[../pyrate-rjmcmc/references/tutorial-3.md:113], and it "only works for preservation models based on
homogenous or time-variable Poisson processes (HPP or TPP)" [../pyrate-rjmcmc/references/tutorial-3.md:122].
No such gate or caveat is printed for `-fast_burnin` anywhere in my four mirrors — so treat its scope
as unknown, not as inherited from `-se_gibbs`.

## 2. The ten Tuning parameters — what each one actually moves

All ten are defined twice. I diffed the two blocks (tutorial-6.md:17-55 vs command-list.md:230-269):
the prose is identical except that (i) tutorial-6.md:19 puts `-multiR`'s "(default)" inside the
sentence, where command-list.md:233 puts it on an Example line, (ii) tutorial-6.md:19 names `-tR`
bare where command-list.md:232 links it, and (iii) only tutorial-6 types three headings —
`-fast_burnin <int>`, `-multiR <boolean>`, `-tT <float>` (§1); `-nT` and the seven other knobs are
untyped on both pages. In the table below, anything in **quotation marks is the mirror's own
wording**; anything in **(parentheses is my gloss**. The phrase "proposal type" is mine — the
mirrors never use it.

| Command | Rate / parameter it updates | Proposal type (documented) | Documented default | Source |
|---|---|---|---|---|
| `-multiR` | speciation and extinction rates | (0 = sliding window, 1 = multiplier) | `-multiR 1` | tutorial-6.md:18-19; command-list.md:231-233 |
| `-tR` | speciation/extinction **rate** window | "by default multiplier proposals" (the mirror then links `-multiR`) | `-tR 0.05` | tutorial-6.md:33-35; command-list.md:247-249 |
| `-tT` | speciation/extinction **times** | "uniform sliding window" | `-tT 1` | tutorial-6.md:21-23; command-list.md:235-237 |
| `-nT` | how MANY times are proposed at once | (a count, not a window) | `-nT 5` | tutorial-6.md:25-27; command-list.md:239-241 |
| `-tQ` | preservation rate `q` AND gamma shape `alpha`, "respectively" | "multiplier proposals" | `-tQ 1.2 1.2` | tutorial-6.md:29-31; command-list.md:243-245 |
| `-tS` | **shift times** of speciation/extinction rates | "uniform sliding window" | `-tS 1` | tutorial-6.md:37-39; command-list.md:251-253 |
| `-fS` | how often shift times vs rates are tried | (frequency) | `-fS 0.7` | tutorial-6.md:41-43; command-list.md:255-257 |
| `-tC` | Covar correlation parameters (speciation, extinction, preservation, "respectively") | (window) | `-tC 0.025 0.025 0.1` | tutorial-6.md:45-47; command-list.md:259-261 |
| `-fU` | update frequencies: preservation, birth-death, Covar | (three frequencies) | `-fU 0.02 0.18 0.08`, "default under Covar model" | tutorial-6.md:49-51; command-list.md:263-265 |
| `-fR` | fraction of birth-death rates updated at a time | (fraction) | `-fR 1` | tutorial-6.md:53-55; command-list.md:267-269 |

Semantics worth quoting exactly, because the wording is the rule:

- "When `-multiR 0` updates are done using sliding window, whereas `-multiR 1` sets multiplier
  proposals (default). Window sizes can be adjusted using `-tR`." [tutorial-6.md:19] So `-tR` serves
  **both** mechanisms — so reading `-multiR` as multiplier-only is wrong. `[CN: the same
  phrase is 乘子建议 at tutorial-6-cn.md:20 but 乘子提议 at command-list-cn.md:231, and the section is
  调优参数 there versus 调参（tuning）参数 here]`.
- `-nT` is a model switch disguised as a knob: "If set to 0, speciation/extinction times are set
  equal to first/last appearances and the preservation model is automatically set to HPP."
  [tutorial-6.md:26] `[CN: tutorial-6-cn.md:27 「保存模型会自动设为 HPP」]`.
- `-fS` is silently overridden: "The value will be automatically set to 0 when no rate shifts are
  being sampled or if the times of shifts are fixed" [references/tutorial-6.md:42] — and the flag this
  sentence then points at is the wrong one; see §7 hazard 10 before repeating it.
- `-fU` leaves the remainder for the times. Its definition says
  "What is left is used for updating speciation and extinction times." [tutorial-6.md:50]
  The printed default spells that arithmetic out:
  "updates preservation parameters with frequency 2%, birth-death parameters with frequency 18%, Covar parameters with frequency 8%, times of speciation and extinction with frequency 72%"
  [tutorial-6.md:51].
- `-fR` is the only knob with a purpose clause: "This command should be used to reduce the fraction
  of updated rate parameters especially when running birth-death models with many shifts, e.g.
  defined by the command `-fixShift` ... to improve the MCMC mixing." [tutorial-6.md:54]
  `[CN: tutorial-6-cn.md:55]`
- `-tQ`'s second value is `alpha`, "the shape parameter of the gamma distributed rate heterogeneity"
  [tutorial-6.md:30], which the command list introduces only as a property of the Gamma preservation
  model [command-list.md:95-97]; the sibling `-ncat` is explicitly gated: it "is used only when  running
  under a Gamma model of preservation (i.e. with `-mG`)" [command-list.md:101, double space verbatim].
  **[inference]** Outside `-mG` there is nothing documented for `-tQ`'s second value to act on.
- `-tC` windows "are given for covariation with speciation, extinction, and preservation rates
  respectively. The parameters will be updated (or not) depending on the Covar model selected (see
  command `-mCov`)" [tutorial-6.md:46].

## 3. The advanced (BD)MCMC settings — all nine, with gates and defaults

| Command | Controls | Gate (documented) | Default | Source |
|---|---|---|---|---|
| `-r` | number of parallel ‘heated’ chains for MC3; "The number includes the ‘cold’ chain" | "used only when running MCMC analysis for parameter estimation (i.e. with `-A 0`)" | **no "(default)" printed**; the printed "Example: `-r 4`" is annotated "(for 1 cold and 3 heated chains)" | command-list.md:193-195 `[CN: 192-194]` |
| `-t` | "the ‘temperature’ parameter for the MC3 heated chains" | "used only when running MC3 analysis (i.e. with `-r >1`)" | `-t 0.03` | command-list.md:197-199 `[CN: 196-198]` |
| `-sw` | "Frequency of attempted swaps between chains in MC3 analysis" | `-r >1` | `-sw 100` | command-list.md:201-203 `[CN: 200-202]` |
| `-k` | "Number of scaling factors used for marginal likelihood estimation in TI" | "used only when running TI analysis (i.e. with `-A 1`)" | `-k 10` | command-list.md:205-207 `[CN: 204-206]` |
| `-a` | "Shape parameter of the beta distributed scaling factors in TI analyses" | `-A 1` | `-a 0.3` | command-list.md:209-211 `[CN: 208-210]` |
| `-M` | "Frequency of model update in BDMCMC analysis" | "used only when running BDMCMC analysis for parameter estimation (i.e. with `-A 2`)" | `-M 25` | command-list.md:213-215 `[CN: 212-214]` |
| `-B` | "the birth-rate at which the BDMCMC algorithm will propose new rate shifts"; it "also corresponds to the shape parameter a Poisson distributed prior on the number of speciation/extinction rates" | `-A 2` | `-B 1` | command-list.md:217-219 `[CN: 216-218]` |
| `-T` | "the time spent in updating the model in BDMCMC analysis" | `-A 2` | `-T 1` | command-list.md:221-223 `[CN: 220-222]` |
| `-S` | "the number of generations after which the BDMCMC algorithm will start updating the model (e.g. after a burn-in phase)" | `-A 2` | **no `(default)` printed** — "Example: `-S 1000` " | command-list.md:225-227 `[CN: 224-226]` |

`grep -nE "used only when" references/command-list.md` enumerates every gate in one pass (it also
returns the `-ncat` gate, §2). Case-distinct letters are separate commands, not aliases — §7 hazard 6.

## 4. Run size, sampling and print frequency

| Command | Documented text | Default | Source |
|---|---|---|---|
| `-n` | "Number of MCMC or BDMCMC generations." | `-n 10000000` | command-list.md:56-58 `[CN: 57-59]` |
| `-s` | "MCMC sampling frequency." | `-s 1000` | command-list.md:60-62 `[CN: 61-63]` |
| `-p` | "MCMC print-on-screen frequency." | no `(default)` printed — "Example: `-p 1000`" | command-list.md:64-66 `[CN: 65-67]` |
| `-b` | "Set the number of iterations to be discarded (i.e. not logged) from the analysis as burnin." | `-b 0` "(default; all samples are logged)" | command-list.md:68-73 `[CN: 69-74]` |
| `-thread` | "the number of threads used for calculating the likelihood of the birth-death process and the NHPP likelihood respectively" | `-thread 0 0` "(default; sequential likelihood calculation)" | command-list.md:75-79 `[CN: 76-80]` |
| `-j` | with several data sets in the input file (e.g. from `pyrate_utilities.R`, for age uncertainty) "this command defines which data set will be analyzed" | `-j 1` "(default; the first data set from the input file is analyzed)" | command-list.md:27-30 `[CN: 28-31]` |
| `-out` | "Add tag to default stem name of output files. This command is useful to avoid overwriting output files when running several instances of the same analysis." | untagged | command-list.md:32-35 `[CN: 33-36]` |

`-thread 0 0` costs speed, not correctness: with both values zero "PyRate will use sequential
computation of the likelihood (thus slowing down a bit the analysis) and will not use the
multiprocessing python library" [command-list.md:76].

- The parallel half of that pair is documented off my pages and platform-conditional: "Under UNIX
  systems, PyRate will use the library multiprocessing and thread (if available) and implement
  parallel computation of the likelihoods (see command -thread)"
  [../pyrate-installation/references/home.md:71], CN twin at [../pyrate-installation/references/home-cn.md:72]. So `-thread 1 3`, "use 1
  thread for birth-death, 3 threads for NHPP likelihood" [command-list.md:79], is documented as
  likelihood parallelism only: it neither lengthens the chain nor changes what is logged.
  **[inference]** Treat a non-default `-thread` as wall-clock relief (step 8 of §8), never as a
  convergence lever; whether any non-UNIX build parallelises at all is not documented.

## 5. How burnin and sampling interact with summarisation and with TI

The complete set of documented interactions:

1. **`-b` is a logging decision, not a post-hoc filter.** The iterations it names are "discarded
   (i.e. not logged)" [command-list.md:69]. **[inference]** What it drops cannot be recovered by a
   later summary command: a summary of that log is a summary of what remains.
2. **`-b` is honoured by the summariser too, and its unit is contested.** The same line:
   "This command is also used to exclude burnin samples when summarizing MCMC results", naming
   `-mProb` and `-plot` (there as links to the summarise page) [command-list.md:69]; and "When set to
   a number between 0 and 1, it is interpreted as a fraction of the total number of MCMC
   generations", with printed examples `-b 0`, `-b 1000`, `-b 0.10` [command-list.md:69-73]. One value
   One value therefore means two different things at run time and summary
   time depending only on magnitude, and the two pages disagree about the unit:
   Tutorial 1 counts samples ("the first 200 samples will be removed",
   ../pyrate-bd-analysis/references/tutorial-1.md:213) while the command list
   defines the flag in iterations [command-list.md:69]. That conflict is recorded, with all four
   witnesses, as hazard 2 of `pyrate-bd-analysis`; do not resolve it here.
3. **TI is the one place the docs make a demand of you.** "Must be set to a reasonable number when
   estimating marginal likelihood through TI (see command `-A`)" [command-list.md:69] — and the
   default is `-b 0` [command-list.md:71]. `-A 1` is the analysis that "computes the marginal
   likelihood of a birth-death model", saved to a ‘*_marginal_likelihood.txt’ file
   [command-list.md:49]. Its accuracy knob is `-k`: "Higher number of scaling factors will improve
   the accuracy of the estimated marginal likelihood, but require longer computational time"
   [command-list.md:206] `[CN: command-list-cn.md:205 「缩放因子数目越多，估算得到的边际似然越准确，
   但需要更长的计算时间」]`. How large `-b` must be, and whether TI burnin is dropped inside the
   marginal-likelihood integral or only at summarisation: not documented (§9).
4. **`-S` is a second, BDMCMC-only burnin gate.** It sets "the number of generations after which the
   BDMCMC algorithm will start updating the model (e.g. after a burn-in phase)"
   [command-list.md:226] — a window in which the model itself (number and placement of shifts) is
   frozen, while pre-`-S` samples are still logged unless `-b` discards them. **[inference]** Reading
   a `-A 2` log that includes pre-`-S` generations means reading a chain that could not yet change
   shift number or placement; no mirror tells you to exclude them.
5. **`-p` reaches no file.** It is the "print-on-screen frequency" [command-list.md:65]; nothing ties
   it to a logged quantity.

## 6. Every directional statement these mirrors make about tuning

The complete inventory. Before repeating any tuning advice as fact, `grep -c` its phrase.

| Knob | The docs' only directional statement | Source |
|---|---|---|
| `-M` | "Reducing this number can improve the sampling of the number of shifts in birth-death rates." | command-list.md:214 `[CN: 213]` |
| `-T` | "Increasing this parameter has a similar effect to increasing the birth-rate (command `-B`)." | command-list.md:222 `[CN: 221]` |
| `-k` | "Higher number of scaling factors will improve the accuracy of the estimated marginal likelihood, but require longer computational time." | command-list.md:206 `[CN: 205]` |
| `-fR` | reduce it "especially when running birth-death models with many shifts" (the mirror links `-fixShift` here) "to improve the MCMC mixing" | tutorial-6.md:54 = command-list.md:268 |
| `-nT` | `0` collapses the model: times = first/last appearances, preservation forced to HPP | tutorial-6.md:26 |
| `-fS` | forced to `0` when no shifts are sampled or shift times are fixed | tutorial-6.md:42 |
| `-ncat` | "Increasing this number will  allow for more variability of the rates across taxa, with comparatively little  effect on the speed of the analysis." (spacing verbatim) | command-list.md:101 |
| `-thread` | `0 0` gives "sequential computation of the likelihood (thus slowing down a bit the analysis)" | command-list.md:76 |
| `-fast_burnin` | a non-zero count gives "faster convergence" — no magnitude, no diagnostic | tutorial-6.md:14 |
| `-tR`, `-tT`, `-tS`, `-tQ`, `-tC`, `-fU`, `-multiR`, `-r`, `-t`, `-sw`, `-a`, `-B`, `-S`, `-b`, `-s`, `-n` | **no directional statement exists** — no sign, size, step, effect or failure symptom is documented for any of them | — |

Scope of that last row: it audits **my four mirrors**, and the corpus's one numeric tuning prescription
for `-fU` lives on a sibling, under the heading "Running PyRate on large datasets" [../pyrate-rjmcmc/references/tutorial-3.md:112].
Its diagnosis [../pyrate-rjmcmc/references/tutorial-3.md:113] is that very large datasets "may require long computing time for the MCMC to reach convergence".
The answer on that same line is the approximate Gibbs sampler flag `-se_gibbs` — spelled with the
underscores in the corpus, never as one word — together with the retuning instruction quoted verbatim
from [../pyrate-rjmcmc/references/tutorial-3.md:113]: "modify the update frequencies to set most of the updates (> 90%) to focus on speciation, extinction, and preservation rates".
It is worked out as `-fU 0.35 0.6 0` [../pyrate-rjmcmc/references/tutorial-3.md:115] and, when the analysis has
numerous preservation shifts, `-fQ 0.1 -tQ 1.05 1.05` [../pyrate-rjmcmc/references/tutorial-3.md:119]; the HPP/TPP-only
gate on that route is at [../pyrate-rjmcmc/references/tutorial-3.md:122], and it says nothing about `-fast_burnin`.
`grep -rn "large dataset" references/` still prints nothing here — quote the sibling with its prefix or
say nothing (§8.0, step 8 note below).

## 7. The 10 things that break a run

| # | Hazard | Source |
|---|---|---|
| 1 | **`-fast_burnin` is invisible from the command list.** No command-list mirror names it — not this skill's `references/command-list.md` and `command-list-cn.md`, nor the five sibling skills' copies of those same two pages (`grep -rl fast_burnin .. --include="command-list*.md"` run from this skill directory prints nothing, exit 1; over all of `../*/references/` only tutorial-6.md and its CN twin match) — yet it is a real switch documented with a default of 0. An agent that reads only the "complete" command page never learns it exists (counting recipe, §11). | tutorial-6.md:12-14; command-list.md (absent) |
| 2 | **Advanced settings do nothing under the wrong `-A`.** `-r` needs `-A 0` [command-list.md:194]; `-t`/`-sw` need `-r >1` [command-list.md:198,202]; `-k`/`-a` need `-A 1` [command-list.md:206,210]; `-M`/`-B`/`-T`/`-S` need `-A 2` [command-list.md:214,218,222,226]. Since `-A 2` is the **default analysis** [command-list.md:52], a bare `-r 4` is inert. No mirror says whether such a command errors, warns or is silently ignored. **Self-check that the switch did take effect** **[inference]** — nothing documents an echo of the settings, so make it observable: run the same command twice, the knob at its documented default and at the candidate value, tag the runs apart with `-out` ("Add tag to default stem name of output files." [command-list.md:33]), hold `-s` fixed [command-list.md:62], and compare the logs — identical columns is the only evidence these pages support for "the knob did nothing" (§5 item 5: `-p` is a print-on-screen frequency and reaches no file). No mirror documents a warning line or a settings dump, so a run that "worked" is not a run that worked; for `-r` the processor remark "Each chain will use a different processor if available" [command-list.md:194] is a wall-clock hint under `-A 0` only, not proof (§9, MC3 row). | command-list.md:193-227; :52 |
| 3 | **`-fS` is silently zeroed.** Any expectation that shift times move is void in either of the two situations the mirror names: "when no rate shifts are being sampled or if the times of shifts are fixed" [tutorial-6.md:42] — the first disjunct is a model with no shifts to sample (e.g. one rate via `-mL 1 -mM 1`, command-list.md:112,116), the second is fixed shift times, which the same sentence mis-links to `-fixSE` while the command that fixes them is `-fixShift` [command-list.md:123-125]; read the mechanism, not the flag the sentence points at (hazard 10). | tutorial-6.md:41-43; command-list.md:123-125 |
| 4 | **`-nT 0` is a model change, not a speed change.** Times become first/last appearances and preservation is forced to HPP [tutorial-6.md:26], so the run answers a different question than the `-nT 5` default [tutorial-6.md:27]. | tutorial-6.md:25-27 |
| 5 | **`-b 0` is the default and `-b` is unit-overloaded.** `-b 0` logs everything [71]; `0 < -b < 1` is a fraction of `-n` while `-b 1000` is a count [69-73]. The same fraction reused with a different `-n` discards a different number of iterations. **Documented antidote for the run-length half of this hazard:** write `-b` as a fraction — "When set to a number between 0 and 1, it is interpreted as a fraction of the total number of MCMC generations" [command-list.md:69], the mirror's own example being `-b 0.10` "(the first 10% of the samples are discarded)" [command-list.md:73] — so one value tracks the run when you change `-n`. **[inference]** It does not settle the samples-vs-iterations dispute of §5 item 2 (hazard 2 of `pyrate-bd-analysis`): the fraction's own example line counts "samples" [command-list.md:73], and no mirror says whether the fraction is taken over generations or over logged samples. | command-list.md:68-73 |
| 6 | **Case-distinct single letters are different commands.** `-t` MC3 temperature [197] vs `-T` BDMCMC model-update time [221]; `-s` sampling frequency [60] vs `-S` BDMCMC start generation [225]; `-p` print frequency [64]; `-M` model-update frequency [213] vs the model switches `-mL`/`-mM`/`-mC`/`-mG`/`-mCov` [111,115,119,95,137]. | command-list.md §3, §4, §6 |
| 7 | **`-fU`'s documented default belongs to one model only.** It is labelled "default under Covar model" [tutorial-6.md:51]; the 2/18/8/72 split sums to 100%, and no line says what `-fU` does in a run without `-mCov` — nor what `-tQ`'s second value does without `-mG` (§2, **[inference]**). | tutorial-6.md:49-51; command-list.md:95-102 |
| 8 | **Two documentation defects that will mislead you.** Under the `-pM` heading the printed example line is "Example: `-pL 1.1 1.1` (default)" [172] — `-pL`'s own example [168] repeated under the wrong flag (the two lines differ only by a space before "(default)"), so no `-pM` default is literally printed anywhere (the CN mirror duplicates the same slip [command-list-cn.md:172] `[CN]`). And the `-cauchy` paragraph breaks mid-sentence at "the scale parameters will" [175] and resumes "be inferred form the data." [176] (typo `form`), so which setting applies when can only be read across the break — the CN twin renders it as one sentence [command-list-cn.md:175] `[CN]`. | command-list.md:166-176 |
| 9 | **One analysis mode is advertised as unfinished.** "`-A 3` run a MCMC analysis with Dirichlet Process Prior on the speciation and extinction rates within fixed time bins. Warning: this function is currently still being tested." [command-list.md:54] — and no tuning or advanced command is documented as applying to `-A 3`. | command-list.md:54 `[CN: 55]` |
| 10 | **The `-fS` sentence names the wrong command.** All four mirrors zero `-fS` "if the times of shifts are fixed" and then, in the closing parenthesis, link to `-fixSE` [references/command-list.md:256; references/tutorial-6.md:42] — but `-fixSE` fixes "the times of speciation and extinction of all taxa", i.e. the node ages, from a previous log [references/command-list.md:104-106]; the command that fixes shift *times* is `-fixShift` ("Fix number and time based on ages provided in a text file." [references/command-list.md:123-125]). The identical link appears in both Chinese twins [references/command-list-cn.md:255; references/tutorial-6-cn.md:43], so this is the source page's slip, not a translation artefact — it cannot be resolved by reading the CN mirror. **[inference]** Act on the mechanism the sentence states, not on the flag it names: `-fS` is inert whenever shift times are not being sampled (no shifts in the model, or shifts fixed by `-fixShift`, or by `-edgeShift` per ../pyrate-bd-analysis/references/tutorial-1.md:269). Do **not** conclude from this sentence that `-fixSE` switches shift sampling off — nothing documents that. | command-list.md:256, 104-106, 123-125; tutorial-6.md:42 |

## 8. Decision procedure when a chain looks wrong

### 8.0 First: the corpus's own precondition on tuning

The nine steps below are for a run you have already decided to tune. Tutorial 1 is the one page in
this corpus that says which parameters may be changed when, and it splits them into two classes
before listing any of them — this mirror line is corpus line 168 of Tutorial 1, offset documented in
`pyrate-bd-analysis`:

> "While several parameters should be changed only when experiencing convergence issues, there are a few that are very important as they change the basic model assumptions or the length of the analyses - see below." [../pyrate-bd-analysis/references/tutorial-1.md:176]

So the whole tuning surface of this skill is **conditional on an observed convergence problem**, and
turning one of these knobs is not a substitute for settling the settings in the table first. Settle
these, in this order, and re-check the chain before touching a single `-t` or `-f`:

| Settled first | Why it is model or run length, not sampling | Source |
|---|---|---|
| the input file | "PyRate includes default settings for all parameters except for the input file." | ../pyrate-bd-analysis/references/tutorial-1.md:176 |
| `-A` (0/1/2/3, and `-A 4` RJMCMC) | it picks the algorithm and what is estimated at all: "The additional command `-A 2` is used to run the BDMCMC algorithm, whereas using `-A 4` (or omitting the flag) will set the algorithm to RJMCMC." | ../pyrate-bd-analysis/references/tutorial-1.md:174; references/command-list.md:46-54 |
| preservation model `-mHPP` / `-mG` / `-qShift` / `-pP` | they change what the process assumes about the record; `-pP` changes a prior's shape and rate | ../pyrate-bd-analysis/references/tutorial-1.md:124, :142, :130, :134 |
| `-n` and `-s` | the length of the analyses: "you may have to **increase the number iterations to reach convergence**" — the doc's first lever against non-convergence is more iterations, not a new proposal | ../pyrate-bd-analysis/references/tutorial-1.md:184; references/command-list.md:56-62 |
| `-b` | it decides which samples exist ("discarded (i.e. not logged)"), so it is upstream of every diagnostic | references/command-list.md:69 |
| `-j` | which age replicate is analysed, and the page says to run several | ../pyrate-bd-analysis/references/tutorial-1.md:178-180 |
| `-mL` / `-mM` / `-fixShift` | number and placement of rate shifts are the model | references/command-list.md:112, :116, :123-125 |
| `-nT` — **only** at `0` | it looks like a tuning knob and is a model switch: "the preservation model is automatically set to HPP" | references/tutorial-6.md:26 (hazard 4) |
| `-B` under `-A 2` | it "also corresponds to the shape parameter a Poisson distributed prior on the number of speciation/extinction rates" — a prior, so changing it changes the question | references/command-list.md:218 (step 7 note) |

Everything else this skill owns belongs to the deferred class: `-multiR`, `-tR`, `-tT`, `-tQ`,
`-tS`, `-fS`, `-tC`, `-fU`, `-fR`, `-fast_burnin`, and the MC3/TI settings `-r`, `-t`, `-sw`, `-k`,
`-a`, `-M`, `-T`, `-S`. **[inference]** Tutorial 1 never names the members of either class (it says
"several parameters" and "a few"), so this partition is my reading from each command's own
definition — a window, a frequency, a fraction, or a chain count belongs to the deferred class;
anything that fixes a prior, a model structure, or the iteration budget does not. The two
counter-examples in the table above are the traps: `-nT` and `-B` look like knobs and are not.

What applying the rule looks like on the one page that applies it: the RJMCMC page's section
"Running PyRate on large datasets" [../pyrate-rjmcmc/references/tutorial-3.md:112] diagnoses
"long computing time for the MCMC to reach convergence"
[../pyrate-rjmcmc/references/tutorial-3.md:113] and answers by retuning frequencies and window
sizes — "you might want to tune the proposal frequency and window sizes for the preservation
parameters to improve and speed up convergence"
[../pyrate-rjmcmc/references/tutorial-3.md:117] — with `-fU 0.35 0.6 0`
[../pyrate-rjmcmc/references/tutorial-3.md:115] and `-fQ 0.1 -tQ 1.05 1.05`
[../pyrate-rjmcmc/references/tutorial-3.md:119]. That is exactly the deferred class, entered
*because* convergence was the observed problem. Note `-fQ` is not one of my commands: it appears only
on that sibling page (§9, last row).

### The nine steps

Steps in order. The last column separates what the mirrors state **[D]** from my reading **[I]**; the
"observable" column is the honest limit of what these pages let you check. Steps 1-3 are §8.0's table
in operational form; steps 4-9 are the deferred class, so they require the evidence §8.0 names (a log
opened in Tracer, with the ESS read per replicate —
../pyrate-bd-analysis/references/tutorial-1.md:205-206), not merely a slow-looking run.

| Step | Turn this | Why (documented) | Observable that it worked | [D]/[I] |
|---|---|---|---|---|
| 1 | Confirm the analysis type: `-A 0`, `-A 1`, `-A 2` (default), `-A 3` [command-list.md:46-54] | every advanced knob is gated on it (§7 hazard 2) | `-A 0`/`-A 2` produce files with "posterior samples of the parameters"; `-A 1` produces the ‘*_marginal_likelihood.txt’ file [47,49,51] | [D] |
| 2 | Check `-b` and `-s` before touching any proposal knob [68-73, 60-62] | `-b` decides what is logged at all; `-s` decides how often | the log holds roughly `(n - discarded)/s` rows (10M generations at `-s 1000` gives 10,000 rows) — no documented minimum exists | [D] for the flags, [I] for the arithmetic |
| 3 | Running TI (`-A 1`)? Set `-b` "to a reasonable number", then consider `-k` | the only imperative about convergence in these mirrors [69]; `-k` trades accuracy for time [206] | a marginal-likelihood file exists [49]; **no acceptance criterion for its value is documented** | [D] + [I] |
| 4 | Time parameters moving slowly → `-tT` (window) and `-nT` (how many per update); rate parameters → `-tR`, after checking which mechanism `-multiR` selected | that is exactly what each knob updates [tutorial-6.md:18-35] | **no symptom-to-knob mapping is documented**; only the parameter each knob owns | [D] for the assignment, [I] for this triage order |
| 5 | Rate shifts not moving → `-tS` (window), then `-fS` (how often shift times are tried instead of rates) | [tutorial-6.md:37-43] | first rule out hazard 3's **first** disjunct — the model may contain no rate shifts to sample, which on its own sets `-fS` to 0 [tutorial-6.md:42], so "nothing moves" can be documented behaviour rather than a failure; do not attribute the zeroing to `-fixSE` (hazard 10) | [D] |
| 6 | Many rate shifts and a reluctant chain → `-fR` (and, with a fixed-shift file, `-fixShift`) | the only knob the docs tie to a named symptom, "to improve the MCMC mixing" [tutorial-6.md:54; command-list.md:123-125] | the docs give no way to observe mixing; a between-run comparison is all this corpus supports | [D] for the advice, [I] for anything else |
| 7 | BDMCMC not exploring shift numbers → `-M`, then `-B` / `-T`, and check `-S` | "Reducing this number can improve the sampling of the number of shifts" [214]; `-B` "also corresponds to the shape parameter a Poisson distributed prior on the number of speciation/extinction rates" [218]; `-T` "has a similar effect to increasing the birth-rate (command `-B`)" [222]; `-S` freezes the model until generation `-S` [226] | the sampled number of shifts differs between runs. **[inference]** because `-B` is a prior shape, changing it changes the model being compared, not only the sampler | [D] + [I] flagged |
| 8 | Chain fine but the run is slow → `-fast_burnin`, and `-thread` | a Gibbs-updated burnin phase is offered "for faster convergence" [tutorial-6.md:14]; `-thread 0 0` is "sequential computation of the likelihood (thus slowing down a bit the analysis)" [76] | nothing observable is documented — which is exactly the gap in §9 | [D] |
| 9 | Covar run misbehaving → `-tC` (which correlations, in which order) and `-fU` (how often each block is tried) | [tutorial-6.md:45-51] | nothing documented beyond the parameters each knob owns | [D] |

Step 8 when the data are large rather than the model slow: the corpus documents a distinct route, not
in my four mirrors — `-se_gibbs` for a "very large dataset (e.g. hundreds or thousands of lineages)"
[../pyrate-rjmcmc/references/tutorial-3.md:113], gated to "preservation models based on homogenous or
time-variable Poisson processes (HPP or TPP)" [../pyrate-rjmcmc/references/tutorial-3.md:122] and warned
against "smoothed" rates when combined with RJMCMC [../pyrate-rjmcmc/references/tutorial-3.md:123].
**[inference]** `-fast_burnin` carries no such gate, cost statement or caveat anywhere in my mirrors (§1,
§9), so do not import the sibling's conditions onto it — and do not report the sibling's prescription as
one of my four pages' (§6 scope note).

## 9. Not documented in this wiki (these four mirrors; rows marked → are answered by a sibling)

Every row was checked by the command in column 3, and that command reads **only this skill's
`references/`** — so "nothing" means zero hits across my four files, not zero hits in the corpus. The
→ rows say where the answer actually lives; do not report one of them as a corpus-wide gap.

| Question | Status | How I verified |
|---|---|---|
| What counts as converged? Any numeric target for `-b`, `-n`, `-s`? | **absent from these four mirrors** — no threshold is named anywhere in them; `-b` gets "reasonable number" [command-list.md:69] with no definition | `grep -rni "converg" references/` → the single `-fast_burnin` line |
| → Then how do I know when to stop? The corpus's own answer | **not here, documented twice elsewhere** — open the log in Tracer: "The log files can be opened in the program" Tracer "to check if the MCMC has converged, for example looking the the Effective Sample Sizes (ESS), and determine the proportion of burnin" [../pyrate-bd-analysis/references/tutorial-1.md:205], ESS per replicate not from a combined file [../pyrate-bd-analysis/references/tutorial-1.md:206], and the summarise page recommends inspecting the log in Tracer to set the burnin proportion [../pyrate-summarize-results/references/summarize-results.md:64]; no numeric target is given by any of those either | `grep -rn "Tracer" references/` → nothing (rc 1), while the sibling mirrors above carry the word |
| → ESS / Tracer: is there any per-knob diagnostic? | **absent here; the sibling pages give a procedure, not a diagnostic** — no mirror anywhere states a numeric ESS target for a PyRate run; what is documented is `-n`/`-s` as the response to non-convergence [../pyrate-bd-analysis/references/tutorial-1.md:184] and `-fQ`/`-tQ` retuned for it [../pyrate-rjmcmc/references/tutorial-3.md:117-119] | `grep -inw -e ESS references/command-list.md` → nothing (rc 1) — and do not fall back on a substring search here: `grep -in ess references/command-list.md` returns 9 lines of *process*, *less*, *expresses* |
| ESS / effective sample size, autocorrelation time, potential scale reduction (Rhat), Gelman-Rubin, Heidelberger, acceptance rate, stationarity, trace plots, Tracer | **absent from these four mirrors** — zero hits for every one of these terms (the → row above names the two sibling mirrors that do use Tracer and the ESS) | `grep -inw -e ESS -e Rhat -e Gelman -e Rubin -e autocorrelation -e acceptance -e stationar -e tracer references/*.md` and `grep -in -e "effective sample" -e "R-hat" -e "potential scale" -e heidelberg references/*.md` → both print nothing, exit 1 |
| What should `-tR` / `-tT` / `-tS` / `-tQ` / `-tC` be set to, and in what steps? | **absent** — only each knob's single printed default (0.05 / 1 / 1 / 1.2 1.2 / 0.025 0.025 0.1); no range, no direction, no rule | `grep -n "^Example" references/tutorial-6.md` → one line per knob |
| How do I detect a window that is too large or too small? | **absent** — no symptom is named for any of the ten knobs; §6 is the whole inventory | `grep -rn "mixing" references/` → the `-fR` sentence only |
| Does `-fast_burnin` cost anything or bias the chain? How long should it run? | **absent** — no non-zero example, no duration guidance | `grep -rn -- "-fast_burnin" references/` → 4 lines (heading + text, in two language mirrors) |
| Which `-A` analyses accept `-fast_burnin`? | **absent** — it is the only tuning command carrying no "used only when" clause | `grep -nE "used only when" references/command-list.md` |
| Do the `-r` heated chains exchange samples, and how do you read MC3 output? | **absent** — `-r` only says "Each chain will use a different processor if available" [command-list.md:194] | `grep -n "MC3" references/command-list.md` |
| Is `-b` burnin excluded from the TI marginal-likelihood integral itself, or only from summaries? | **absent** — the requirement is stated, the mechanism is not | `grep -n -B1 -A1 "computes the marginal likelihood" references/command-list.md` |
| Do `-mProb` / `-plot` warn when `-b` exceeds the samples in the log? | **absent here** — both names occur only as link text inside the `-b` line [command-list.md:69]; their syntax and behaviour belong to the summarise page, where `-mProb` is printed as `-mProb file_name_mcmc.log` and its `-b` defaults to 0 on that same line [../pyrate-summarize-results/references/summarize-results.md:64-65]. Whether either warns on an over-large `-b`: not documented there either | `grep -n "mProb" references/*.md` → 2 hits, EN and CN twins of that one `-b` sentence; no syntax printed anywhere |
| What happens if I set a knob outside its gate (e.g. `-k` with `-A 2`)? | **absent** — "used only when" is the entire documentation of every gate | `grep -nE "used only when" references/command-list.md` |
| How do replicate runs combine, and what do I do with several logs (`-j`, `-out`)? | **partial** — `-j` selects a data set [27-30], `-out` tags output stems so parallel runs do not overwrite [32-35]; nothing on combining chains | `grep -n -A3 -e "defines which data set will be analyzed" -e "Add tag to default stem name" references/command-list.md` |
| Recommended settings per data size or model complexity | **absent from these four mirrors** — they print defaults, never prescriptions. The one size-conditioned prescription in the corpus is a sibling's: large data sets get `-se_gibbs` plus retuned `-fU`/`-fQ`/`-tQ` [../pyrate-rjmcmc/references/tutorial-3.md:113-119] (§8.0) | `grep -rn "large dataset" references/` → nothing |
| The flags `-se_gibbs` and `-fQ`, seen next to `-fU 0.35 0.6 0` and `-tQ 1.05 1.05` in the suite's RJMCMC page | **not in these mirrors** — they belong to a sibling's evidence base (`../pyrate-rjmcmc/references/tutorial-3.md:113-119`), so I cannot document them here; they are the worked example of the triage rule (§8.0), and see Related skills | `grep -rn "se_gibbs" references/` → nothing |

## 10. Worked example — flags and values are the docs', the assembly is mine

These mirrors print two complete invocations — `python PyRate.py
path_to_input_file/Ursidae_PyRate.py` [command-list.md:15] and `python PyRate.py -d
path_to_input_file/Ursidae_SE.txt` [command-list.md:20] — and one bare flag example per command, but
no finished tuning command line. The block below therefore composes documented flags with
documented values. `path_to_input_file/Ursidae_PyRate.py` is the path printed at command-list.md:15
(Ursidae is also the `-fixSE` example file, :106); treat it as the docs' naming convention, not a
guaranteed path. **[inference]** The ordering of flags on one line is mine.

```bash
# 1 - parameter estimation with two speciation and two extinction rates.
#   -A 0 [command-list.md:47] ; -mL 2 / -mM 2 (values paired verbatim at :120; semantics :112,:116)
#   ; -n 10000000 [:58] ; -s 1000 [:62]
#   -b 1000 "first 1,000 samples are discarded" [:72] ; -p 1000 [:66] ; -out run_1 [:32-35]
#   -multiR 1 [tutorial-6.md:18-19] ; -tR 0.05, -tT 1, -tS 1, -fS 0.7 [tutorial-6.md:33-43]
#   -fast_burnin 0 - the documented default [tutorial-6.md:13-14]
python PyRate.py path_to_input_file/Ursidae_PyRate.py -A 0 -mL 2 -mM 2 -n 10000000 -s 1000 -b 1000 \
    -multiR 1 -tR 0.05 -tT 1 -tS 1 -fS 0.7 -fast_burnin 0 -p 1000 -out run_1

# 2 - let BDMCMC estimate the number and placement of shifts (-A 2 is the DEFAULT analysis,
#   command-list.md:51-52) with its documented model-update settings:
#   -M 25 [:215] ; -B 1 [:219] ; -T 1 [:223] ; -S 1000 [:227 - an example, NOT a documented default]
python PyRate.py path_to_input_file/Ursidae_PyRate.py -A 2 -n 10000000 -s 1000 -b 1000 \
    -M 25 -B 1 -T 1 -S 1000 -out run_2

# 3 - the TI comparison of model 1: -b is required "to a reasonable number" (command-list.md:69),
#   -k 10 / -a 0.3 are the documented TI settings [:207, :211];
#   output: a ‘*_marginal_likelihood.txt’ file [command-list.md:49]
python PyRate.py path_to_input_file/Ursidae_PyRate.py -A 1 -mL 2 -mM 2 -n 10000000 -s 1000 -b 1000 \
    -k 10 -a 0.3 -out run_3
```

What these mirrors let you check afterwards, and no more: `-A 1` writes the marginal-likelihood file
[command-list.md:49]; `-fixSE` reads back a `mcmc.log` from a previous analysis
[command-list.md:104-106]; `-mProb` and `-plot` are named as the summarisers that honour `-b`
[command-list.md:69]. No numeric criterion is documented for any of them, so this skill must not
promise one (§9, the Tracer/ESS rows). Legitimate tuning evidence in this corpus is
**between-run**: change one knob, re-run, compare summaries — see `pyrate-summarize-results`.

## 11. grep recipes (run from this skill directory; every one executed and passing)

```bash
# fast_burnin: defined on the Advanced-settings page, absent from the command list
grep -rn -- "-fast_burnin" references/
grep -c fast_burnin references/command-list.md
# and across the whole suite, no command-list mirror of any skill names it (prints nothing, exit 1)
grep -rl fast_burnin .. --include="command-list*.md"

# every tuning knob with its printed value / default marker
grep -nE "Example|\(default" references/tutorial-6.md

# the two pages carrying the tuning section, and every gate condition
grep -n "Tuning parameters" references/command-list.md references/tutorial-6.md
grep -nE "used only when" references/command-list.md

# the -multiR mechanism sentence, plus the CN terminology split (提议 vs 建议, 调优 vs 调参)
grep -n "multiR" references/tutorial-6.md references/command-list.md
grep -n "提议\|建议\|调优\|调参" references/command-list-cn.md references/tutorial-6-cn.md

# prove the absence of convergence diagnostics (prints nothing, then exit=1)
grep -inw -e ESS -e Rhat -e Gelman -e Rubin -e autocorrelation -e acceptance -e stationar -e tracer references/*.md
echo "exit=$?"

# the only knob with a documented symptom; the only mention of convergence
grep -rn "mixing" references/
grep -rni "converg" references/

# -S and -p carry no "(default)" tag, unlike their neighbours
grep -n -B2 -e 'Example: `-S 1000`' -e 'Example: `-p 1000`' references/command-list.md
```

## Resources

| File | Load when |
|---|---|
| `references/tutorial-6.md` | You need the knob definitions as prose: `-fast_burnin` (its only source, :13-14) and the ten Tuning parameters (:17-55), including the `-fast_burnin <int>` / `-tT <float>` / `-multiR <boolean>` type annotations. |
| `references/tutorial-6-cn.md` | A Chinese term is ambiguous: 快速烧录期 (:13), 调优参数 (:18), 乘子建议 (:20), 均匀滑动窗口 (:23), 混合（mixing） (:55). |
| `references/command-list.md` | Anything outside the ten knobs: `-A`/`-n`/`-s`/`-p`/`-b`/`-thread` (:45-82), the nine Advanced (BD)MCMC settings (:192-227), and the commands that gate them (`-mG` :95-98, `-ncat` :100-102, `-fixSE` :104-106, `-mL`/`-mM`/`-mC`/`-fixShift` :111-125, `-mCov` :137-144, `-N`/`-pL`/`-pM`/`-cauchy`/`-pP`/`-pS`/`-pC` :162-188). |
| `references/command-list-cn.md` | The Chinese twin of the same page: 高级 (BD)MCMC 设置 (:191), 调参（tuning）参数 (:229), 乘子提议 (:231) — note that both the section title and 提议/建议 differ from tutorial-6-cn.md. |
| `../assets/files/tuning-knobs-command-lines.txt` | You want one representative command line per knob, each tied to its source line. |
| `../assets/files/tuning-defaults-table.txt` | You want every knob's documented default plus the line it comes from, on one screen. |
| `../assets/files/tuning-term-frequency-audit.sh` (+ captured output `tuning-term-frequency-audit.txt`) | You want the raw vocabulary counts behind §0, §6 and §9; the script resolves its paths from its own location, so `sh ../assets/files/tuning-term-frequency-audit.sh` run from this skill directory works, as does the absolute path the script's own header shows. |
| `../pyrate-bd-analysis/references/tutorial-1.md` — a sibling's mirror, not part of my evidence base | You need what my four pages omit: the two-class triage rule (:176), `-n`/`-s` as the documented response to non-convergence (:184-188), Tracer and the ESS as the actual check (:205-206), `-b` counted in samples at summary time (:213, :229), `-A 4` and `-edgeShift` (:174, :269). Cite it with a sibling prefix, as everywhere in §8.0 — a bare name never resolves to another skill's folder. |
| `../pyrate-summarize-results/references/summarize-results.md` | You need the `-mProb` / `-plot` syntax and the Tracer-based instruction that decides `-b` after the run (:63-65). |
| `../pyrate-installation/references/home.md` — a sibling's mirror, not part of my evidence base | You need the only sentence in the corpus that says when PyRate parallelises at all: the UNIX `multiprocessing`/`thread` note behind `-thread` ([../pyrate-installation/references/home.md:71]; the CN twin of that same sentence is [../pyrate-installation/references/home-cn.md:72]). Cite it with a sibling prefix (§4). |
| `../pyrate-rjmcmc/references/tutorial-3.md` | You want the single worked example of the deferred class being entered on purpose: `-se_gibbs`, `-fU 0.35 0.6 0`, `-fQ 0.1 -tQ 1.05 1.05` (:112-119) — and the HPP/TPP-only gate that my `-fast_burnin` has no equivalent of (:122). |

## Related skills

- `pyrate-command-reference` owns the full command list — every command named here outside my two
  sections (`-mHPP`, `-mG`, `-mCov`, `-pS`, `-singleton`, `-d`, `-trait_file`).
- `pyrate-bd-analysis` owns the choice of `-A 0` / `-A 1` / `-A 2` and the marginal-likelihood
  comparison itself; I own only the knobs that change how those chains move. It also carries the
  Tutorial 1 mirror whose two-class triage rule gates every step in my §8 (§8.0), and the `-b`
  currency conflict I deliberately do not resolve (§5 item 2).
- `pyrate-summarize-results` owns `-b` and `-s` as consumed by `-mProb`, `-plot` and `-combLog`, and
  the Tracer/ESS procedure that these four mirrors cannot answer (§9 Tracer/ESS rows).
- `pyrate-rjmcmc` owns the BDMCMC model semantics behind `-A 2` and `-fixShift`, and is the skill
  whose page documents `-se_gibbs` and `-fQ` — the other approximate-Gibbs route my mirrors never
  mention (§9, last row). Its "large datasets" section is the only place in the suite that actually
  walks through the deferred class of §8.0 (:112-119).
- `pyrate-preservation-models` owns `-mHPP` / `-mG` / `-qShift` / `-ncat` — what `-tQ`'s two values
  act on, and what `-nT 0` forces ("automatically set to HPP", tutorial-6.md:26).
- `pyrate-continuous-covariates` owns the Covar models that give `-tC` and `-fU` their meaning, and
  the `-pC` prior on the correlations.
- `pyrate-diversity-dependence` and `pyrate-des` own `-mC`, `-fixShift` and `-pS`, i.e. the shift
  structures whose times and frequencies `-tS` and `-fS` move.
- `pyrate-input-file` owns the input `.py` file, `-singleton`, and `-j` replicate selection — the
  reason `-out` tagging matters when one dataset is run several times.
