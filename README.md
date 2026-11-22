# PyRate 技能包（`PyRate-skills`）

面向 LLM Agent 的 **PyRate** 技能集：把 PyRate 的官方文档（GitHub wiki + `tutorials/`）整理成可单独加载的
Agent Skills，让 AI 编程助手在写命令、读输出、排错时**有据可查、不臆造参数**。每个技能是一个含 `SKILL.md`
的目录：`SKILL.md`（英文，给 Agent 读）给出该主题的危险项、参数表、可跑示例与 Pitfalls，`references/`
里是该主题对应的官方页面本地镜像，按需加载。本 README 是给人看的仓库导览。

**内容来源**：本工作区同级目录 `../PyRate-doc/` 的 PyRate 文档语料，它由两个 git 检出组成——

| 语料 | 上游 | 检出 HEAD | 页数 |
| --- | --- | --- | --- |
| `PyRate-doc/PyRate-wiki/` | <https://github.com/dsilvestro/PyRate.wiki.git>（wiki，页面即 <https://github.com/dsilvestro/PyRate/wiki/Home> 等 6 页） | `abebf92` (2024-09-02) | 6 个主题 × 英文/中文 |
| `PyRate-doc/PyRate-tutorials/tutorials/` | <https://github.com/dsilvestro/PyRate.git> 的 `tutorials/` 目录 | `6b804ab` (2026-11-11) | 9 个文件 × 英文/中文 |

被镜像的 6 个 wiki 页面：`Home`、`1. Preparing input file`、`2. PyRate: command list`、
`3. Summarize PyRate results`、`4. PyRateContinuous`、`5. Dispersal Extinction Sampling model`；
9 个 tutorial 文件：`README.md`、`pyrate_tutorial_0.md` … `pyrate_tutorial_6.md`、`pyrate_tutorial_bdnn.md`。
PyRate 程序本身（<https://github.com/dsilvestro/PyRate>，AGPLv3）**不在**本仓库内，本仓库也不运行它。

**溯源纪律**（这套东西的全部可信度都建立在这三条上，违反任何一条都会被闸门打回）：

1. **镜像逐字**：`references/*.md` 是语料页面的完整副本，只加 frontmatter、只把图片路径改指到
   `../../assets/images/`，一个字母都不重排（上游的拼写错误原样保留）。由 `audit_sources.py` 与
   `audit_corpus.py` 的 A/K/S 项逐字节比对语料。
2. **引用落地**：正文里每一个 `references/<file>.md:LINE` 都必须指向该镜像真实存在、且内容与引用相符的
   行；跨技能引用写全 `<owning-skill>/references/<file>.md:LINE`。由 `audit_corpus.py` T 项与
   `audit_citations.py` 复核（当前 T：729 处引用全部落地）。
3. **样例诚实**：`assets/files/` 里凡不是语料原文的都必须在文件头声明是自己造的，并在
   `assets/files/README.md` 的索引里逐行写明偏离了什么。由 `audit_corpus.py` 的 Q/W 项复核。

| 规模 | 数量 |
| --- | --- |
| 技能（`*/SKILL.md`） | 14 个，合计 4920 行 |
| 文档镜像（`*/references/*.md`） | 52 份 = 50 份语料逐字镜像（25 英文 + 25 中文对照；有些页面被多个技能各自留一份，故文件数 > 页面数）+ 2 份本套件自撰的分析页（页内以 `**This file is not a mirror.**` 自我声明，并在 `scripts/audit_corpus.py` 的 `PLANNED_AUTHORED` 里逐一点名） |
| 语料覆盖率 | **30 / 30 = 100%**（`scripts/audit_corpus.py` 的 A 项检查） |
| 可直接使用的样例输入（`assets/files/`） | 77 个（逐字或改写自文档代码块的格式样例，另有 `README.md` 溯源索引，见 `assets/files/README.md`） |
| 文档原图（`assets/images/`） | 14 张 PNG，与语料中的图片逐字节一致（O 项检查） |
| 技能自带的辅助脚本 | 5 个工具（`pyrate-command-reference/scripts/` 4 个 + `pyrate-input-file/scripts/` 1 个），另有 11 个自检闸门脚本在顶层 `scripts/` |
| `SKILL.md` 里的 `grep` 复验配方 | 143 条（`scripts/audit_recipes.py` 本轮真的执行了 108 条以 `grep`/管道形式书写的配方，另 13 条同行带可核对的数字或「应为空」断言；其余形式书写的配方行见第六节） |

---

## 一、为什么需要它

PyRate 的坑不在「参数太多」，而在**文档各处散落着会静默改变结果的约定**，以及文档自己前后不一致的地方。
这套技能把这些逐条钉在镜像行号上，例如：

1. **Python 版本：语料里有两个互相矛盾的答案。** wiki 首页写
   "Please note that Python 3.x is currently not supported"（`pyrate-installation/references/home.md:69`），
   而虚拟环境教程要求 "First, make sure **Python (v.3.10 or higher)** is installed"
   （`pyrate-installation/references/virtual-environment.md:13`）。技能不替你选边，而是教你先用
   `check_env.py` / `venv-preflight.sh` 在**你手上那份 PyRate** 上实测（见 `pyrate-installation/SKILL.md`
   "Which Python? the corpus answers twice"）。
2. **`-d` 会悄悄关掉一半估计。** 给出起源/灭绝时间表时，"This option automatically sets `-fixSE = null`
   (see PyRate command list), meaning that the estimation of preservation rates and times of
   speciation/extinction are switched off, and the MCMC only samples the birth-death parameters"
   （`pyrate-command-reference/references/command-list.md:18`）。以为自己在估保存速率、实际是在给定年龄上跑
   BD，是这条路最常见的错。
3. **`-check_names` 不查同物异名，而且它压根不在官方命令表里。** 原文是
   "**NOTE that this algorithm does NOT check for synonyms!**"（`pyrate-input-file/references/tutorial-1.md:101`），
   而 wiki 的 command list 全页搜不到 `-check_names` 这个命令（`grep -c -- "-check_names"` 在
   `pyrate-command-reference/references/command-list.md` 上返回 0）——它只被 tutorial 记录。
   把「拼写审计通过」当成「命名表干净」是危险的（`pyrate-input-file/SKILL.md` 的 `-check_names` 一节）。
4. **出现记录表的缺失数据规则：四个必填列一个都不能空。**
   "At present, PyRate can not deal with missing information in these four columns, so make sure that you
   remove these entries beforehand."（`pyrate-input-file/references/preparing-input-file.md:14`）——只有可选的
   第 5 列 Trait 允许 `NA`（同一行后半句）。而列名本身**在语料的两个页面里就有两种拼法**：wiki 用
   `Species Status MinT MaxT Trait`（`preparing-input-file.md:16`），tutorial 用
   `Taxon_name Status MinAge MaxAge`（`tutorial-1.md:52`）；技能把这条冲突原样列出而不裁决
   （`pyrate-input-file/SKILL.md` "Which column names are correct?"）。第三种拼法
   `Species Status min_age max_age trait` 只在**本套件自己合成的**样例
   `assets/files/occ-ursidae-upstream.txt:13` 的表头里出现，语料 30 页里搜不到它——见第八节。
5. **Gamma 保存模型的「明显更优」是文档断言，且那句话本身是坏的。**
   "On most empirical data sets the Gamma model strongly outperforms the  alternative assumption of constant
   rates, and across-taxa rate  heterogeneity has been shown to Gamma model accounts to some  extent for
   temporal changes of the preservation rates"（`pyrate-preservation-models/references/command-list.md:97`，
   句子在上游就断了，空格也照原样留着）——没有对照数字、没有适用条件；而 `-ncat` 又 "used only when  running
   under a Gamma model of preservation (i.e. with `-mG`)"（同页 101 行）。技能据此把 `-mG` 的收益标为「文档主张」
   而非「已验证事实」。

此外还有：`Site` 列会让同 site 的共存记录共享一个随机年龄（正文与它印出的表在编号上自相矛盾，
`pyrate-input-file/references/tutorial-1.md:72` vs 75-85 行）、`-A 3` 被页面自己标注
"still being tested"（`pyrate-command-reference/references/command-list.md:54`）、生成速率图的最后一步
"This requires that R is installed on your PC to execute the shell command Rscript"
（`pyrate-des/references/tutorial-5.md:354`）等等，都写在各自的 "things that break a run" 表里。

## 二、技能列表（14 个）

「参考镜像数」是该技能 `references/` 目录里的实际文件数（含中文对照）。「自带脚本」指该技能目录下的
`scripts/*.py`；其余技能没有自带脚本，可执行样例放在共享的 `assets/files/` 里。

| 技能 | 一句话用途 | 自带脚本 | 参考镜像数 |
| --- | --- | --- | --- |
| `pyrate` | 入口/路由技能：包内各程序总览、标准三步分析、按用户目标路由到其余技能、教程索引、引用与许可 | — | 4 |
| `pyrate-installation` | 建好并验证运行时：venv 建立与激活、`ensurepip`/`requirements.txt`、`numpy`/`scipy`/`argparse`、R 与 `Rscript`、`pyrate_lib` 必须同目录、Python 版本冲突的实测预检 | — | 4 |
| `pyrate-input-file` | 输入数据这一层：制表符分隔的出现记录表（4 必填列 + 可选 `Trait`/`Site`）、缺失数据规则、`extract.ages(.pbdb)`、生成的 `*_PyRate.py`/`*_TaxonList.txt`、`-check_names`、`-data_info` | `validate_input.py` | 5 |
| `pyrate-command-reference` | wiki「2. PyRate: command list」逐项参考：全部命令与 `<input file>`、8 个小节、词元数、取值形态、文档默认值、命令之间的互锁、只在他处出现的命令、EN/CN 漂移 | `build_command.py`、`check_env.py`、`parse_results.py`、`pyrate_commands.py` | 2 |
| `pyrate-preservation-models` | 保存（化石化）模型的选择与检验：默认 NHPP + PERT 钟形谱系速率、`-mHPP`、`-qShift` + `epochs_q.txt`（TPP）、`-mG`/`-ncat` 跨类群 Gamma 异质性、超先验、`-PPmodeltest`、`-A 1` 比模型 | — | 4 |
| `pyrate-bd-analysis` | 跑一次出生-死亡分析并读懂它：`-A 0/1/2/3` 四种模式、运行几何（`-n`/`-s`/`-p`/`-b`/`-thread`/`-wd`/`-out`/`-j`）、`-A 2` BDMCMC 端到端、三种「速率突变」分析的区别、先验表、`-combLog` | — | 4 |
| `pyrate-rjmcmc` | 可逆跳跃 MCMC（`-A 4`）：两种输入 setup、突变时间均匀先验与 `-min_dt`、四个输出文件与列对应、`-mProb`、`-plotRJ`、`-combLogRJ`、`-se_gibbs`、`-bound_se` | — | 4 |
| `pyrate-summarize-results` | 输出解读与后处理：`*_sum.txt`/`*_mcmc.log`/`*_marginal_rates.log`/`*_marginal_likelihood.txt`/`*_RTTplot.r`/`pyrate_mcmc_logs/`，每一列的含义与在何种分析下才记录，`-plot`/`-combLog`/`-b`/`-ginput` | — | 4 |
| `pyrate-continuous-covariates` | `PyRateContinuous.py`：速率随时间连续变化（`-m 0` 指数为文档默认 / `-m 1` 线性）、`-DD` 用自身多样性、`-c` 外接时间-数值表、`-ginput` 生成 `*_se_est.txt`、`-A 1` 检验，以及 `-ginput` 归属的两处冲突 | — | 4 |
| `pyrate-diversity-dependence` | 多类群多样性依赖：`PyRateMCDD.py` 的 4 列 / 6 列输入与 0 起始类群编号、`-d`/`-n`/`-s`/`-c`；`PyRateMBD.py` 多变量出生-死亡（`-var`、`-m 0/1`、`-rmDD`、`-minT`/`-maxT`、`-hsp`） | — | 2 |
| `pyrate-trait-age-models` | 性状与年龄依赖模型：Covar（`-trait_file`、`-mCov 1`–`5`、`-trait`、`-logT`、`-pC`、`-tC`/`-fU`）、ADE 年龄依赖灭绝（`-ADE 1`、`-filter`、只允许 HPP/TPP）、BDC 出生-死亡年代种（`-bdc`、`-eqr`、需 Dendropy 树文件） | — | 4 |
| `pyrate-des` | 扩散-灭绝-取样（DES）：`PyRateDES.py` 全部选项、DarwinCore 化石/现生两张表、生成输入的 `-fossil`/`-recent`/`-bin_size`/`-rep`/`-trim_age`/`-translate`/`-site`、`-d` 分析与协变量扩展、三条数据准备路线、路线二区域编码的取值陷阱 | — | 5 |
| `pyrate-bdnn` | BDNN（出生-死亡神经网络，tutorial 7）：`-BDNNmodel 1` 与默认 1-Myr 时间 bin、性状编码（0-1 / one-hot / 整数）、`-fixShift`+`-edgeShift`+`-qFilter`、`-plotBDNN*` 家族、七个 CSV 输出、`-combBDNN`/`-restore_mcmc` | — | 2 |
| `pyrate-mcmc-tuning` | 调优与链排错：`-fast_burnin`（默认 0）、十个 Tuning 参数 `-multiR`/`-tT`/`-nT`/`-tQ`/`-tR`/`-tS`/`-fS`/`-tC`/`-fU`/`-fR`、九个高级 (BD)MCMC 设置、运行长度与抽样频率、烧入与 `-b`/TI 的相互影响 | — | 4 |

`pyrate` 是推荐入口：它的 "Routing table" 一节按用户目标把任务路由到其余技能。

## 三、目录结构

```
PyRate-skills/
├── README.md                    本文件
├── LICENSE                      原创层 MIT（明确不覆盖镜像层与图片）
├── LICENSE.md                   上游出处、git HEAD、无担保声明（provenance 记录）
├── pyrate/                      14 个技能目录，每个都是独立技能
│   ├── SKILL.md                 技能主体（YAML frontmatter: name + description，英文正文）
│   └── references/              该技能的镜像：EN 逐字副本 + CN 中文对照
├── pyrate-bd-analysis/ … pyrate-trait-age-models/     其余技能，结构相同
├── pyrate-command-reference/
│   ├── references/{command-list.md,command-list-cn.md}
│   └── scripts/                 build_command.py / check_env.py / parse_results.py / pyrate_commands.py
├── pyrate-input-file/
│   ├── references/              preparing-input-file(.md/-cn.md) + tutorial-1(.md/-cn.md)
│   └── scripts/validate_input.py
├── pyrate-des/
│   └── references/              5 份：des-model + tutorial-5（各含 CN 对照）
│                                + route2-area-coding-hazards.md（本套件自撰：路线 2 面积编码陷阱的
│                                逐行追踪，页首自我声明 `**This file is not a mirror.**`）
│                                （技能目录里没有 DES_demo/：那是 worked example 在 PyRate 仓库根
│                                `mkdir -p` 的产物，不属于本套件）
├── assets/
│   ├── files/                   77 个样例（56 txt / 12 sh / 5 R / 1 bat / 1 py / 1 tsv / 1 md）
│   │   └── README.md            全部 77 个样例的逐条溯源索引
│   └── images/                  14 张文档原图（被镜像以 ../../assets/images/ 引用）
└── scripts/                     11 个机器闸门（见第六节）
```

## 四、安装与使用

* **整仓安装（推荐）**：技能之间用 `../<sibling>/references/<file>.md` 互相引用，样例一律写成
  `../assets/files/<fixture>`，共享图片写成 `../../assets/images/<png>`——这些路径都是**相对技能目录的上一层**
  算的。把 14 个技能目录和 `assets/` 一起放进技能根目录即可让全部链接落地：

```bash
# 方式 A：个人全局可用
mkdir -p ~/.qoder/skills
cp -r PyRate-skills/pyrate PyRate-skills/pyrate-* PyRate-skills/assets ~/.qoder/skills/

# 方式 B：只对某个项目可用
mkdir -p <project>/.qoder/skills
cp -r PyRate-skills/pyrate PyRate-skills/pyrate-* PyRate-skills/assets <project>/.qoder/skills/
```

  装完后 `~/.qoder/skills/pyrate-input-file/` 里的 `../assets/files/occ-canis-table.txt` 解析为
  `~/.qoder/skills/assets/files/occ-canis-table.txt`，`../pyrate-command-reference/references/command-list.md`
  解析为同级的兄弟技能——两者都在。顶层 `scripts/` 不必安装：`audit_corpus.py` 要在**仓库内**跑（它按脚本自身
  位置反推套件根，并且需要同级目录存在语料 `../PyRate-doc/`）。

* **只装单个技能（会断链，务必补 `assets/`）**：例如
  `cp -r PyRate-skills/pyrate-des ~/.qoder/skills/`。这时 `~/.qoder/skills/pyrate-des/SKILL.md` 里的
  `../assets/files/des-CarnivoraFossils.txt` 会解析到 `~/.qoder/skills/assets/…`，`../pyrate-input-file/references/…`
  会解析到 `~/.qoder/skills/pyrate-input-file/references/…`——那里通常既没有 `assets/` 也没有兄弟技能，
  **这些链接会全部失效**。补救：把 `assets/` 一并复制到技能目录的上层，并把它引用的那几个兄弟技能一起复制；
  或者保留整仓目录结构（`cp -r PyRate-skills ~/.qoder/skills/PyRate-skills/`，让加载器递归扫子目录）。
  想知道某个技能到底依赖哪些兄弟，在套件根目录跑：

```bash
grep -oh '\.\./[A-Za-z0-9_-]*/' pyrate-des/SKILL.md | sort -u   # 它锚定的顶层目录
```

* **加载进会话**：复制完即可由技能加载器按 `SKILL.md` 的 `description` 命中；会话已在跑的话用
  `/skills reload` 让它重新扫描目录，不必重启。
* **按需加载**：`references/` 是整页镜像，不要整页塞进上下文。每个 `SKILL.md` 的 Resources 表列出该技能全部
  镜像文件与「何时加载」，末尾的 `grep recipes` 给出可执行、已在镜像上验证过的精确抽取命令（第六节的
  `audit_recipes.py` 会真的逐条执行它们）。
* **不确定该用哪个技能**：先读 `pyrate/SKILL.md` 的路由表。

## 五、附带的脚本

五个脚本都只用 Python 3 标准库，**离线、只读、绝不执行 PyRate**；`--self-test` 会自建临时样例并断言行为。
下面每条命令与括号里的结果都是本机实际打印的（`audit_corpus.py` 的 H 项就是逐个跑 `--self-test` 来把关）。

```bash
cd PyRate-skills

# 1) 组装并校验一条 PyRate.py 命令行（真值来源是镜像本身：命令集在运行时从
#    pyrate-command-reference/references/command-list.md 解析，镜像改了它就跟著改）
python3 pyrate-command-reference/scripts/build_command.py --self-test
#   → self-test: OK (136 checks; citation audit of 142 quotes across 9 mirrors;
#      50 commands parsed from the command list + 59 cited extensions;
#      corpus replay: 118 documented command lines assembled, 1 allow-listed)
python3 pyrate-command-reference/scripts/build_command.py Ursidae_PyRate.py -A 2 -mG -j 1
#   → COMMAND: python PyRate.py Ursidae_PyRate.py -j 1 -A 2 -mG   （只组装，不执行）
python3 pyrate-command-reference/scripts/build_command.py canis_PyRate.py \
    -qShift assets/files/cmdref-epochs_q.txt -mG -ncat 4 --dry-run
```

`build_command.py` 接受的自有选项（其余一切 `-X` 都按镜像声明的词元数转发给 PyRate 命令）：
`--mirror PATH`、`--json`、`--dry-run`、`--self-test`、`--list`（打印它当前接受的 109 个命令）、`--core-only`、
`--python-exe EXE`、`--program NAME`、`--help`；退出码 0 有效 / 2 校验失败 / 3 镜像缺失或不可解析 / 4 用法错误。
注意：`--list` 的命令集仍**不含** `PyRateContinuous.py`/`PyRateMCDD.py`/`PyRateMBD.py`/`PyRateDES.py` 的
一部分专属命令，第六节的 `audit_command_lines.py` 因此还是红的。

```bash
# 2) 探测本机是否真的有一个可用的 PyRate 运行时
python3 pyrate-command-reference/scripts/check_env.py --self-test
#   → self-test: OK (20 assertions on temp interpreter shims, no real interpreters required)
python3 pyrate-command-reference/scripts/check_env.py --pyrate-dir /path/to/PyRate-master
```

`check_env.py` 的选项：`--pyrate-dir PATH`（可重复，也会搜 `$PYRATE_DIR` 与当前目录）、`--python2 PATH`、
`--python3 PATH`、`--timeout SECONDS`（0<t≤120，默认 20）、`--json`、`--self-test`、`-h`。
注意它对 Python 2.6–2.7 与 3.10+ 的冲突**同时报告两条**，不替你选。

```bash
# 3) 摘要 PyRate 跑完之后留下的输出文件（只读；*.py / *.r 一律当文本，绝不执行）
python3 pyrate-command-reference/scripts/parse_results.py --self-test
#   → self-test: OK (29 assertions on 11 temp fixtures: BDMCMC / fixed-shift / header-less
#      mcmc.log, marginal_rates, marginal_likelihood, sum.txt, sp_rates, se_est,
#      unknown names, --b, --max-rows, --json payload)
python3 pyrate-command-reference/scripts/parse_results.py --stems      # 文档印过的输出名
python3 pyrate-command-reference/scripts/parse_results.py run_1_mcmc.log run_1_sum.txt --b 0.25
```

`parse_results.py` 的选项：位置参数 `PATH …`、`--b N`（按丢弃 N 个样本报告影响，0<N<1 视为比例）、
`--stems`、`--json`、`--max-rows N`（每列统计的行数，1–200，默认 8）、`--max-lines N`（每文件最多读取行数，默认 400000）、
`--self-test`、`-h`。它只认文档印过的文件名，喂样例输入会得到
`not a documented PyRate output name`；物理布局文档没写处它打印字面的 `format not documented` 而不猜。

```bash
# 4) 命令索引查询（第 5 个工具，也是 build_command.py 的 EXTENSIONS 表数据来源）
python3 pyrate-command-reference/scripts/pyrate_commands.py --self-test
#   → self-test: OK (570 checks: 51 command rows verified against command-list.md and its CN twin,
#      56 off-page citations verified)
python3 pyrate-command-reference/scripts/pyrate_commands.py -- mG -d   # 查命令（-d 必须放在 -- 之后）
python3 pyrate-command-reference/scripts/pyrate_commands.py --modes     # 各 -A 模式允许/禁止哪些命令
python3 pyrate-command-reference/scripts/pyrate_commands.py --elsewhere # 只在别的页面出现的命令
```

`pyrate_commands.py` 的选项：位置参数 `commands …`、`--elsewhere`、`--modes`、`--json`、`--self-test`、`-h`。
因为它自己也用 argparse，**带前导 `-` 的命令名要写在 `--` 之后**，否则会被当成它自己的选项而报错。

```bash
# 5) 跑分析之前校验输入表 / 生成的 *_PyRate.py
python3 pyrate-input-file/scripts/validate_input.py --self-test
#   → self-test: OK (54 assertions; 26 cited rules re-verified against the mirrors;
#      tables + generated *_PyRate.py inputs; a hostile input was confirmed not to execute)
python3 pyrate-input-file/scripts/validate_input.py assets/files/occ-canis-table.txt
#   → RESULT occ-canis-table.txt: PASS (0 errors, 1 warning)
#     （那 1 个 WARN 是列名冲突本身，不是数据错）
python3 pyrate-input-file/scripts/validate_input.py 你的表.txt --expect trait --pyrate-dir /path/to/PyRate-master
python3 pyrate-input-file/scripts/validate_input.py --rules       # 它实现了哪些规则、原文引在哪一行
```

`validate_input.py` 的选项：位置参数 `PATH …`、`--expect {trait,site,none}`（断言第 5 列必须是什么）、
`--pyrate-dir DIR`、`--json`、`--rules`、`--max-findings N`（默认 40，上限 500）、`--quiet`、`--self-test`、`-h`；
退出码 0 = 无 ERROR，1 = 至少一个 ERROR，2 = 用法/IO 问题。文档只示范而未明说的模式只给 WARN，不会让跑失败。

样例本身怎么读：`assets/files/README.md` 是全部 77 个样例的溯源索引（哪一个逐字来自哪一页、哪一行，
哪一个是我们合成的、能不能直接跑）。**先读它**：本套件不含上游 `example_files/` 数据，凡文档未印出数值的
样例都标了 `synthesized`，只能当格式样板。

## 六、机器闸门：怎么跑、证明什么、今天的真实结果

11 个闸门都不联网、都不往套件里写文件；其中两个会动盘：`audit_install.py` 把整套复制到临时目录再跑一遍，
`audit_tutorial_runs.py` 会在临时工作目录里**真的执行**语料教程里的命令（它需要一份 PyRate 上游源码树，
所以是唯一一条要依赖环境才能跑的闸门）。其余都在套件根目录下以 `python3 scripts/<gate>.py` 运行，
退出码 0 = 干净、1 = 有 FAIL（每条 FAIL 都带 `file:line`）。`audit_corpus.py` 默认在同级目录找
`../PyRate-doc`，可用 `--corpus PATH` 指定。每个闸门都有 `--self-test`（用注入的缺陷证明它真的会咬人；
条数随闸门而异，`audit_corpus.py` 一百多项）。所有闸门都支持 `--help`（`audit_recipes.py` 的 shebang 已补，
`./scripts/audit_recipes.py` 可直接执行）。

下表是 **2026-11-22 在本机实际跑出的结果**（最后一行原样粘贴，`exit` 是进程真实退出码）。全部绿的。

| 闸门 | 它证明什么 | 今天的结果（原样输出 + 退出码） |
| --- | --- | --- |
| `scripts/audit_corpus.py` | 总闸（A–W 二十多项）：语料逐页落地、镜像逐字节、链接与图片解析、引用落地、样例前缀与溯源、SKILL.md 结构、本 README 的数字 | `audit_corpus.py: 0 failure(s), 3 warning(s); exit 0 == clean`<br>`suite=…  corpus=…  skills planned=14  mirrors planned=50`，exit 0 |
| `scripts/audit_structure.py` | 每个 `SKILL.md` 的 frontmatter 合法（`name` 与目录同名、`description` 单行 ≤1024 字符）、必备小节齐全、资源表成形 | `14 skills checked, 0 structural defects`<br>`RESULT: PASS`，exit 0 |
| `scripts/audit_sources.py` | 语料 30 页 vs 镜像 50 份：无未镜像页、无被改写的正文、无重复伪造 | `RESULT: PASS - every corpus page is mirrored, verbatim`，exit 0（30 页 / 50 镜像 / 被多技能重复 10） |
| `scripts/audit_coverage.py` | 技能集合是否覆盖了语料里的命令、Python/R 函数、模型名、输出产物名 | `RESULT: PASS  (hard command misses: 0, skills: 14, soft gaps: 0)`，exit 0（另打印 15 条 `GAP` 产物名，见第七节） |
| `scripts/audit_citations.py` | `SKILL.md` 的引用与引文：文件存在、行号在范围内、引文在镜像里逐字存在 | `FABRICATED: 0`<br>`FILE-MISSING: 0   LINE-OOB: 0`<br>`RESULT: PASS`，exit 0（citations 1825 / quotations 721） |
| `scripts/audit_script_citations.py` | 5 个自带脚本里内嵌的镜像引用与引文是否落地 | `TOTAL: 101 citation sites in 5 scripts; 17 embedded quotes verbatim-at-line, 0 stale, 0 absent; 56 sites line-verified only`<br>`RESULT: PASS`，exit 0 |
| `scripts/audit_recipes.py` | 把每个 `SKILL.md` 结尾的 grep/sh 配方**真的执行**在镜像上，核对同一行声明的数字或「为空」断言 | `98 recipe(s) executed from 14 skill(s); 11 carried an exactly checkable same-line claim (count or asserted emptiness); 0 anomaly(ies), 4 INFO`<br>`RESULT: PASS`，exit 0 |
| `scripts/audit_command_lines.py` | 独立扫描 64 个文件里的 817 条 PyRate 命令行，把 1644 个命令词元对照 `build_command.py --list` 的接受集 | `RESULT: PASS`，exit 0 |
| `scripts/audit_flag_values.py` | 示例命令里的取值是否有文档依据（重点是 `-b` 的样本数/迭代次数之争） | `RESULT: PASS`，exit 0 |
| `scripts/audit_install.py` | 把套件复制到别处再跑一遍：制作机绝对路径泄漏、只在安装后才断的链接、从副本跑自检 | `15 self-testing script(s) run from the copy, 0 failure(s)`<br>`RESULT: PASS`，exit 0 |

`audit_corpus.py` 自己那三条 WARN 都是关于它本身的：3 行占位图名、3 行规则文本按行号豁免。

一键跑完（前 10 个不需要任何外部条件）：

```bash
cd PyRate-skills
for g in audit_corpus audit_structure audit_sources audit_coverage audit_citations \
         audit_script_citations audit_recipes audit_command_lines audit_flag_values audit_install; do
    python3 scripts/$g.py > /tmp/$g.log 2>&1; printf '%-24s exit=%s\n' "$g" "$?"
done
```

第 11 个要一份 PyRate 上游源码树（`github.com/dsilvestro/PyRate` 的 master 即可）和一个装了依赖的 Python：

```bash
python3 scripts/audit_tutorial_runs.py --tree /path/to/PyRate-master \
        --env /path/to/venv/bin/python > /tmp/audit_tutorial_runs.log 2>&1; echo "exit=$?"
```

它自带 240 s 的单条命令墙钟上限（`--max-seconds` 可调）与有界复跑，全量在 1-3 小时量级（教程里的 MCMC 是真跑的）；不给 `--tree`/`--env`
时它照常跑完但**一条也不执行**，那种绿不证明任何东西，读它的输出时先看「执行序列」那一列。

## 七、红闸门如何结的案，以及还开着什么

本轮之前有三个红闸门，外加 `audit_corpus.py` 里一大摞待办。逐条结案；结案方式全部是**改内容**或**改闸门的取证
方式**，没有一条是靠放宽判定、扩大豁免面或删检查做到的：

* **`audit_command_lines.py`：FAIL (213) → PASS。** 那 213 个词元逐条查下来分三类。其一，`build_command.py` 的
  接受集只从 `PyRate.py` 的命令页解析，缺 `PyRateDES.py` / `PyRateContinuous.py` / `PyRateMCDD.py` / `PyRateMBD.py`
  / `PyRateMCMC.py` 与 R 侧 `rPYRATE*.R` 的专属命令——已按语料原样补进 `--program` 段与目录表（自检原样输出：
  `196 checks; all defects detected; 0 undetected; 1 false rejection; corpus replay: 122 documented command lines
  assembled, 1 allow-listed`）。其二，技能自己写的命令用了文档里从没出现过的旗标（`-out`、`-wd` 之类），已改回
  文档印过的形态：28 处编造 `-wd` 清零、`-out` 只剩 `pyrate-bdnn` 里四处真实文档命令、`PyRateContinuous` 的 TI
  循环改为「每个模型跑进自己的目录再收拢日志」。其三，`cd` 与相对路径不匹配，已补 `cd`。整条链上只剩**一处按行号
  点名**的豁免：`pyrate/SKILL.md:57` 的 `PyRate.py -help | grep -i ...` 是管道，闸门只该看第一段。
* **`audit_flag_values.py`：FAIL (8) → PASS。** 争点只在 `-b`：`4.-PyRateContinuous.md:7` 说它是样本数，
  `command-list.md:69` 说它是迭代次数。技能里 9 个示例取值换成文档真印过的（0、0.1、0.10、0.25、0.5、100、200、
  1000、100000），两种读法连同两条镜像行号一起写进 `pyrate-command-reference/SKILL.md` 与
  `pyrate-continuous-covariates/SKILL.md`，不裁决。
* **`audit_install.py`：FAIL (7) → PASS。** 其中 6 条是 worked example 里写死的制作机绝对路径（照抄会 `cd` 到不
  存在的地方），已改成相对路径或 `<PyRate 目录>` 占位；第 7 条是 `audit_sources.py --self-test` 在**没有语料的安装
  副本**里必然失败。修法不是豁免它，而是让那个自检**自带**一份临时语料——`scripts/audit_sources.py:333`、
  `:359` 用 `tempfile.mkdtemp` 造自己的 fixture——于是在任何机器上都成立，也仍然真的会咬。
* **`audit_coverage.py`：15 条 `GAP` → 0。** 语料提到而技能没展开的产物名（BDNN 的七个 CSV、
  `_sp_predictor_influence.csv`、`Time_windows.txt`、`DiatomFossils.txt` 之类）各自写进了对应 SKILL.md 并逐条引
  镜像行号；该闸门的「软缺口」现在与它打印的清单一样是空的，不再是「闸门绿但清单不为空」。
* **引用类：103 + 147 处 stale pointer → 0。** `SKILL.md` 与自带脚本里的行号曾大量漂移（引文逐字存在于镜像，但不
  在它声称的那一行）。现在 `audit_citations.py` 与 `audit_script_citations.py` 双双报 `0 stale pointer(s)`，脚本侧
  覆盖面同时从 5 个脚本 101 处扩到 9 个脚本 99 处（`validate_input.py` 与四个 `audit_*` 不在扫描范围，脚本头部明写）。
* **镜像与结构。** 19 处镜像正文偏离、9 处未解决链接、9 处缺目录、326 处「正文里的 `#` 被当成 `headings` 目录项」，
  分别由重建镜像、修链接、补目录、把 `headings` 提为 YAML 顶层键解决；13 份英文镜像重建为逐字节一致，现在
  `references/` 下是 50 份逐字镜像（25 英文 + 25 中文）+ 2 份自写页。
* **`assets/files/` 与它的假溯源。** `pyrate-input-file/SKILL.md` 曾把三个**由本套件合成**的文件说成上游
  `example_files/` 的逐字节副本、给出两个编造的 md5，还断言其中一个是 CR-only 行尾（实测 0 个 CR 字节）。三句全
  删，改为直说「合成样例，按 `command-list.md` / `1.-Preparing-input-file.md` 的列定义构造」，并保留「语料只给出这
  三个文件的文件名与用途、没有任何字节」这一事实。同时 `audit_corpus.py` 的 Q 项不再用「整文件不在镜像里 = 编造」：
  77 个样例现在逐条对照自己 frontmatter 声明的镜像行区间，**71/77 逐字命中**，其余 6 个按**文件名**点名（不是按目
  录、不是按模式，漏一个或豁免多了都会 FAIL）并逐字复现其数据体；`extreme-ages.txt` 的镜像断言已删除，只保留
  `3.-Summarize-PyRate.md:192` 这个格式出处。
* **编造引文清零。** 六条「读起来像文档、文档里没有」的引文（`-ifTC` 的默认值、`-ss` 只支持两个模型、`-out` 是全局
  输出前缀、`-fixThRaw` 的含义、R 侧的解压路径、`-pC`/`-out` 的默认取值）改成「镜像逐字引 + 明确标为自己的推论」，
  或整句删除。同类清理还包括 `pyrate-continuous-covariates/SKILL.md` 里那句文档中 0 命中的 `TI_%M` glob 断言、
  `pyrate-des/SKILL.md` 里三处（`-dsd` 先验形状不是「1,1」、`-out` 不控制 DES 生成产物前缀、`-plotBD` 的图名来自
  本套件的 `parse_results.py` 而非 PyRate）。
* **本 README 自己的数字**重推了一遍（总行数、页数、镜像数、配方数、闸门数、每技能 references 数），
  `audit_corpus.py` 的 R 项现在从磁盘重新推导、只跟本文比对，不再信文中写着的数。

还开着的：

* **`audit_citations.py` 的 FABRICATED 启发式会误报**：它贪婪重配对引号，一行里「长引文 + 短引文」混排时，中间那句
  没被引的散文会被当成引文。所以 `RESULT: PASS` 只说明「它抽出来的那些引文逐字存在」，不说明每一处引用都被抽出来
  验过。
* **`audit_corpus.py` 的 N 项跳过引号无法成对的行**，跨行引文根本不被验证；那一部分是人工核对的。
* **语料内部三处前后不一致没有裁决**，只在 `pyrate-command-reference/SKILL.md` 的漂移表里两行并列：`-b` 的单位、
  `-prD`/`-spD` 的作用对象（`command-list.md:65` 英文 = 「prior on the speciation and extinction rates」，`:121`
  中文 = 「diversification rates 的先验」，已用 `parse_results.py:42` 的合并列名如实记录）、`-pP` 的第二参数是尺度
  还是速率。
* **上游的 `example_files/` 不随套件分发**：语料只是引用它们，本机也没有。所有需要真实输入数据的例子都写明「先取得
  PyRate 源码树」，`pyrate-des/DES_demo/` 这类制作期产物已从套件删除。
* **`scripts/__pycache__/` 已在 `.gitignore` 中忽略**，不会进入版本控制；本地跑闸门时仍会生成，可随时删。

两条以前只能靠文档、现在是跑出来的事实：

* **教程命令真的执行过。** `audit_tutorial_runs.py` 把各 `references/tutorial*.md` 里的命令序列在一份真实的上游源码
  树（`github.com/dsilvestro/PyRate` master）里逐条执行，按 rc 与产物分类为「执行通过 / CRASH / ENV / LONGRUN」。
  CRASH 计入 FAIL；ENV（缺依赖）与 LONGRUN（撞墙钟上限）单列、必须打印，且 LONGRUN 要成立必须附一份「按该页自己
  文档化的迭代旗标缩小规模后能跑通、且真的产出文件」的复跑证明，否则降级为 CRASH。命令行上本来没有可缩短的迭代
  字面量时（`tutorial-5.md`:186 那种「跑默认 10 万次」的命令），允许**追加**一个旗标，但它必须同时满足两条取证：
  同一镜像里有把它文档化为迭代次数的句子、且同一镜像（或 `build_command.py --list` 对 `PyRate.py`）见过该程序以整数
  取值用它；两条证据的行号都打进判定行，取值由闸门选定并明写「非文档印过的组合，仅用于证明可运行性」。真失败
  （rc!=0）永远进不了这条路径。原样结果在第六节的表里。
* **numpy 2.x 下 `PyRateDES.py` 的 DES 生成步骤会死，而文档里每一条检查都是绿的。** 语料 `home.md:71` 只说
  「The libraries numpy and scipy are required.」，`virtual-environment.md:44` 让人 `pip install -r requirements.txt`
  而不钉版本；今天这样装会拿到 numpy 2.5.5，实测生成步骤 rc=1，
  `ValueError: The truth value of an empty array is ambiguous`，抛点是 `pyrate_lib/lib_utilities.py:585` 的
  `if trim_age > 0:`，`-rep 10` 该写的 10 个文件一个都没写。钉到 numpy 1.26.4 + scipy 1.13.1 后同一命令 rc=0、10 个
  文件齐。这是**本机实测事实、不是文档的说法**，已写进 `pyrate-installation/SKILL.md`（自检表之后的一节）并在
  `pyrate-des/SKILL.md` 的 worked example 里指过去。

## 八、数据来源与许可

* **`references/` 是上游文档的逐字镜像。** 25 份英文镜像是 PyRate wiki 页面与 `tutorials/` 文件的完整本地副本，
  只做两处改动：加一段 YAML frontmatter（记录 `source_url`、`mirrored_from`、`headings`），以及把图片路径
  从 `assets/…` 改指到 `../../assets/images/…`。一个字母都没重排，文档里的拼写错误
  （`PyRte`、`yRate's`、`larwger`）原样保留。上游是 **PyRate，AGPLv3**，<https://github.com/dsilvestro/PyRate>
  （wiki 检出 <https://github.com/dsilvestro/PyRate.wiki.git>）；`assets/images/` 下的 14 张图同样来自上游。
  **这两类文件不由本仓库的 MIT 许可重新授权**，`LICENSE` 里有明确的除外条款；详细出处与 git HEAD 记在 `LICENSE.md`。
  因为镜像层是 AGPLv3，整个派生套件按 `LICENSE.md` 的声明一并以 AGPLv3 分发。
* **`-cn` 文件不是上游页面。** 25 份 `*-cn.md` 是**本工作区内制作的简体中文对照译文**（语料的两个 git 检出里
  `git ls-files` 匹配不到任何 `*cn.md`，15 个中文页面全部是未跟踪的本地新增），它们的 frontmatter 用
  `mirror: local Simplified-Chinese translation of the PyRate documentation` 与 `translated_from:` 表明这一点，
  `source_url` 指向被翻译的英文页。请勿把它们当成上游中文文档引用。
* **MIT（本仓库原创部分）**：14 份 `SKILL.md`、顶层 `scripts/` 与两个技能目录下的 5 个脚本、
  `README.md`、`assets/files/README.md` 溯源索引、`assets/files/` 里由我们合成的样例，以及仓库组织，见 `LICENSE`。
* **无担保**：语料自身存在矛盾（最典型的就是 Python 版本，还有 `-b` 的单位、`-ginput` 归属、列名拼法），
  这套技能的原则是**记录冲突而不裁决**；它是文档的忠实索引，不是凌驾文档的权威。
* 引用 PyRate 请用文档列出的文献（Silvestro et al. 2014 *Syst Biol* 63:349 与 2014 *MEE* 5:2442，
  以及各模型对应的追加文献），见 `pyrate/SKILL.md` 的 "Literature, licence, support" 一节。
