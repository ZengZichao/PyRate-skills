---
title: PyRate: command list
source_url: https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list
language: Simplified Chinese
mirrored_from: PyRate-doc/PyRate-wiki/2.-PyRate:-command-list-cn.md
headings: 57
translated_from: command-list.md
mirror: local Simplified-Chinese translation of the PyRate documentation
---
### 输入文件、工作目录
你可以在[这里](https://github.com/dsilvestro/PyRate/tree/master/example_files)找到多种示例文件。关于准备输入文件的更多细节请见[这里](https://github.com/dsilvestro/PyRate/wiki/1.-Preparing-input-file)。

##### `<input file>`
设置输入文件，包括路径与文件名。该文件是一个 Python 文件，其中包含化石产出记录数据（以 Numpy 数组列表的形式），并可选地包含一个或多个连续性状（continuous trait）。利用 R 脚本 `pyrate_utilities.R`（见上文）可以生成格式正确的输入文件。
示例：
`python PyRate.py path_to_input_file/Ursidae_PyRate.py`

##### `-d`
除包含产出记录数据的 python 输入文件外，用户也可以提供一张表格，给出每个物种的起源时间与灭绝时间。该选项会自动设置 `-fixSE = null`（见 PyRate 命令列表），即关闭保存率以及物种形成/灭绝时间的估算，马尔可夫链蒙特卡洛（MCMC）仅基于所给的每个物种起源与灭绝时间对出生-死亡（birth-death）模型参数进行抽样。当起源时间与灭绝时间已知、或已经通过其他 PyRate 分析估算得到时，该选项十分有用。该表格应制作为以制表符分隔的文本文件，第一行为列标题，随后每个物种占一行。每行包含 4 列：第一列指明物种所属的演化支（clade），这只在 MCDD 分析中有用（PyRateMCDD 的 Wiki 页面正在建设中），在其他所有分析中均应填 0。第二列指明物种的数字标识符（该数值是任意的，仅用于参考）。第三列和第四列则分别包含每个物种的起源时间与灭绝时间。若这些数值存在多个估算结果（例如来自先前的重复 PyRate 分析），则可作为额外的列提供（例如第 5 列为起源时间的第二个估算值，第 6 列为灭绝时间的第二个估算值）。与标准 PyRate 分析一样，重复编号通过命令 `-j` 选择（见下文）。
示例：
`python PyRate.py -d path_to_input_file/Ursidae_SE.txt`

#####`-wd`
定义工作目录（working directory），所有输出文件将保存在该目录中。若未指定，输出文件将保存在与输入文件相同的目录中。
示例：
`-wd path_to_target_directory`

#####`-j`
如果输入文件包含多个数据集（例如为考虑化石年代的不确定性而使用 R 脚本 `pyrate_utilities.R` 生成的数据集），该命令用于指定将要分析哪一个数据集。
示例：
`-j 1`  （默认值；分析输入文件中的第一个数据集）

##### `-out`
在输出文件默认基本名（stem name）上添加标签。当同一分析运行多个实例时，该命令有助于避免输出文件被覆盖。
示例：
`-out run_2`  （将 ‘run_2’ 添加到所有输出文件的名称中）

##### `-singleton`
该命令可用于在排除某些分类单元（taxa，例如单记录分类单元 singleton）之后运行任何分析。若设为 1，则在运行分析之前去除所有仅有 1 次产出记录的分类单元（更多示例见下文）。被排除的分类单元数目与剩余的分类单元数目会打印到屏幕上。当与命令 [`-data_info`](https://github.com/dsilvestro/PyRate/wiki/3.-Summarize-PyRate-results#-data_info) 一起使用时，该信息同样可用。
示例：  
`-singleton  1`  （排除仅有 1 次已取样产出记录的分类单元）  
`-singleton  2`  （排除已取样产出记录不超过 2 次的分类单元）  
`-singleton  -1`  （排除现生分类单元）

***
### 主要分析设置
##### `-A`	
`-A 0` 运行用于参数估算的 MCMC，即出生-死亡模型中速率转变（rate shift）的数目固定（见“出生-死亡模型——约束速率转变”一节）。该分析生成的输出文件包含参数的后验（posterior）抽样，例如物种形成/灭绝/保存率以及速率转变的时间（更多细节见“输出文件说明”一节）。 

`-A 1` 运行带有热力学积分（thermodynamic integration，[(TI; Lartillot & Philippe 2006)](http://sysbio.oxfordjournals.org/content/55/2/195.full)）的 MCMC，以估算出生-死亡模型的拟合度。该分析计算出生-死亡模型的边际似然（marginal likelihood，保存于 ‘*_marginal_likelihood.txt’ 文件），可用于比较备选模型，例如速率转变数目或性状相关性不同的模型。

`-A 2` 运行 BDMCMC 分析 [(Stephens 2000)](http://www.jstor.org/stable/2673981?seq=1#page_scan_tab_contents)，联合估算出生-死亡过程中速率转变的数目、转变的时间位置，以及各转变之间的物种形成率与灭绝率。该分析生成的输出文件包含参数的后验抽样，例如保存率以及随时间变化的物种形成/灭绝率（见“输出文件说明”一节）。
示例：`-A 2`  （默认值）

`-A 3` 运行一个 MCMC 分析，对固定时间箱（time bins）内的物种形成率与灭绝率施加 Dirichlet 过程先验（Dirichlet Process Prior）。警告：该功能目前仍处于测试阶段。

##### `-n`
MCMC 或 BDMCMC 的代数。
示例：`-n 10000000`  （默认值）

##### `-s`	
MCMC 抽样频率。
示例： `-s 1000`  （默认值）

##### `-p`	
MCMC 屏幕打印频率。
示例： `-p 1000`

##### `-b`
设置分析中被丢弃（即不记录）的迭代数目，作为烧录期（burn-in）。通过 TI 估算边际似然时（见命令 `-A`），必须将该值设为合理的数目。在汇总 MCMC 结果（例如 [`-mProb`](https://github.com/dsilvestro/PyRate/wiki/3.-Summarize-PyRate-results#-mprob)、[`-plot`](https://github.com/dsilvestro/PyRate/wiki/3.-Summarize-PyRate-results#-plot) 功能）时，该命令也用于排除烧录期抽样。当设为 0 到 1 之间的数值时，其被解释为 MCMC 总代数的比例。
示例：
`-b 0`  （默认值；记录所有抽样） 
`-b 1000`  （丢弃前 1,000 个抽样） 
`-b 0.10`  （丢弃前 10% 的抽样） 

##### -thread 
设置分别用于计算出生-死亡过程似然与 NHPP 似然的线程数目。当两个值均设为 0 时，PyRate 将对似然采用顺序计算（因而会使分析速度略有下降），并且不会使用 python 的 multiprocessing 库。  
示例： 
`-thread 0 0` （默认值；顺序似然计算）  
`-thread 1 3` （出生-死亡过程使用 1 个线程，NHPP 似然使用 3 个线程）
 

注：更多命令见“高级 (BD)MCMC 设置”一节。

***
### 保存（化石化）模型

##### `-mHPP` 
对保存率使用齐次泊松过程（homogeneous Poisson process，HPP），而非采用保存率呈“帽形”（hat-shaped，即 PERT）分布的非齐次泊松过程（non-homogeneous Poisson process，NHPP）[(Liow et al. 2010)](http://paleobiol.geoscienceworld.org/content/36/2/224.abstract)。请注意：除非另有指定，否则使用的是 NHPP。
示例：`-mHPP`  

##### `-qShift` 
对保存率使用时变泊松过程（time-variable Poisson process，TPP），即保存率在预定义的时间段内恒定，但可跨时间段变化（例如不同的地质世，geological epochs）。使用该模型需要提供一个文件，其中给出划分各世的时间（示例见[这里](https://github.com/dsilvestro/PyRate/blob/master/example_files/epochs_q.txt)）。 
示例：`-qShift epochs_q.txt`  

##### `-mG` 
设定 Gamma 模型，允许数据集中各分类单元的平均保存率存在异质性。在 Gamma 模型下，保存率被假定服从形状参数（_alpha_）由数据估算的 gamma 分布。在大多数实证数据集上，Gamma 模型显著优于“保存率恒定”这一备选假定；已有研究表明，跨分类单元的速率异质性在一定程度上可解释保存率随时间的变化 [(Silvestro et al.  2014)](http://sysbio.oxfordjournals.org/content/63/3/349.long)。该选项可应用于 NHPP、HPP 和 TPP 保存模型。
示例：`-mG`

##### `-ncat` 
设置在 Gamma 模型下用于获取 gamma 分布保存率的类别数目。增大该数值可使速率跨分类单元的变异更大，而对分析速度的影响相对较小。该命令仅在使用 Gamma 保存模型（即配合 `-mG`）时使用。
示例：-ncat 4  （默认值）

##### `-fixSE` 
基于先前的分析，固定所有分类单元的物种形成时间与灭绝时间。该命令可用于载入一个 ‘mcmc.log’ 文件，由此计算所有分类单元物种形成与灭绝时间的后验均值。随后 PyRate 将使用这些值运行分析，即不再估算这些时间，也不再计算保存过程（NHPP 或 HPP）的似然，而仅对出生-死亡模型的参数进行抽样。若设为 `-fixSE null`，则使用首次出现与末次出现时间作为固定的物种形成时间与灭绝时间。 
示例：`-fixSE /path_to_file/Ursidae.mcmc.log`


***
### 出生-死亡模型——约束速率转变
##### `-mL` 
设置 MCMC 中使用的随时间变化的物种形成速率数目（配合 `-A 0` 或 `-A 1`）。在 BDMCMC 分析（`-A 2`）中，该命令仅用于设置起始速率的数目。
示例：`-mL 2`（设置 2 个物种形成速率与 1 次速率转变）

##### `-mM` 
设置 MCMC 中使用的随时间变化的灭绝速率数目（配合 -A 0 或 -A 1）。在 BDMCMC 分析（-A 2）中，该命令仅用于设置起始速率的数目。
示例：`-mM 3`（设置 3 个灭绝速率与 2 次速率转变）

##### `-mC` 
将物种形成率与灭绝率的时间段约束为相等。该命令仅用于至少包含一次速率转变的出生-死亡模型中（例如配合 `-mL 2` 与 `-mM 2`），且
示例：`-mC`

##### `-fixShift` 
依据文本文件中给出的年龄，固定速率转变的数目与时间。该文件只需是一个文本文件，其中列出应被固定的速率转变年龄（见 PyRate 示例文件中的 ‘epochs.txt’）。使用该命令时，速率转变的数目与时间位置被固定，并且对物种形成与灭绝设为相同。这会自动将物种形成率与灭绝率的先验（prior）切换为半柯西分布（half-Cauchy distribution）[(Silvestro et al. 2015)](http://onlinelibrary.wiley.com/doi/10.1111/nph.13247/abstract)，另见函数 [-cauchy](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#cauchy)。 
示例：`-fixShift path_to_file/epochs.txt`


***
### 性状相关性速率设置（Covar 模型）
PyRate 实现了这样的出生-死亡模型：其中物种形成率与灭绝率随谱系（lineage）以特异的方式变化，其变化是与某个连续性状之间相关性的函数。该模型的描述见[这里](http://onlinelibrary.wiley.com/doi/10.1111/2041-210X.12263/abstract)。如果 PyRate [输入文件](https://github.com/dsilvestro/PyRate/wiki/1.-Preparing-input-file)中包含某个性状，则在使用命令 [`-mCov`](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#settings-for-trait-correlated-rates-covar-models) 时会直接从 python 文件中读取性状值。或者，可使用命令 `-trait_file`（见下文）以单独文件的形式提供包含性状数据的表格。相关性参数的默认先验是以 0 为中心、标准差 = 1 的正态分布。标准差可通过命令 [`-pC`](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-pc) 修改。

##### `-trait_file`
利用该命令可提供一张表格（制表符分隔的文本文件），给出化石数据集中各物种的性状值。表格的第一列应包含物种名称（与 PyRate 文件中使用的名称完全一致），第二列提供性状值（[见示例文件](https://github.com/dsilvestro/PyRate/blob/master/example_files/Ursidae_bm.txt)）。缺少性状数据的物种可以从表格中省略。或者，也可以将其保留在表格中并将性状值设为 `NA`。这些物种仍会被纳入分析，但其性状值将由 MCMC 进行插补。
示例：  
`-trait_file path_to_file/Ursidae_SE.txt` 与性状相关的物种形成速率  

##### `-mCov`
设置 Covar 模型，其中出生-死亡速率（以及保存率）跨谱系变化，这是与某一连续性状的相关性所导致的结果；该性状作为观测变量提供，而相关性则由估算得到的参数（cov_sp, cov_ex, cov_q）刻画。
示例：  
`-mCov 1` 与性状相关的物种形成速率  
`-mCov 2` 与性状相关的灭绝速率  
`-mCov 3` 与性状相关的物种形成与灭绝速率  
`-mCov 4` 与性状相关的保存率  
`-mCov 5` 与性状相关的物种形成、灭绝与保存率  

##### `-trait` 
如果输入文件包含多个性状，该命令用于指定将要分析哪个性状。
示例：`-trait 1`（默认值；取第一个性状）

##### `-logT` 
定义性状值的变换方式。
示例：  
`-logT 0` 不对性状作变换  
`-logT 1` 对性状作 log_e 变换  
`-logT 2` 对性状作 log10 变换（默认值） 




***
### （超）先验设置
##### `-N` 
设置现生（extant）物种的数目（无论它们是否被纳入化石产出记录数据）。该值用于计算物种形成率与灭绝率的超先验（hyperprior），即以当前已知的多样性为条件（[Kubo and Iwasa 1995](http://www.jstor.org/stable/2410323?seq=1#page_scan_tab_contents)；Silvestro et al. 2014 中的公式 12–15）。若设为 `-N -1` 或未加指定，则改用 gamma 先验，其形状参数与尺度参数由选项 `-pL` 和 `-pM` 定义（见下文）。后一种选项可能适用于已经灭绝的演化支，或当前多样性尚不确定的情形。 
示例：`-N 24`

##### `-pL` 
物种形成率的 gamma 分布先验的形状参数与尺度参数，该速率估算每个谱系每 Myr 的期望化石产出记录数。仅当未指出现生分类单元数目（即 `-N -1`）时才使用该命令。
示例：`-pL 1.1 1.1`(默认值)

##### `-pM` 
灭绝率的 gamma 分布先验的形状参数与尺度参数，该速率估算每个谱系每 Myr 的期望化石产出记录数。仅当未指出现生分类单元数目（即 `-N -1`）时才使用该命令。
示例：`-pL 1.1 1.1` （默认值）

##### `-cauchy` 
该命令将半柯西分布（half-Cauchy distribution）设为物种形成率与灭绝率的超先验 [(Silvestro et al. 2015)](http://onlinelibrary.wiley.com/doi/10.1111/nph.13247/abstract)。当使用其他先验（例如 Gamma）时，应用默认设置 `-cauchy -1 -1`。在 `-cauchy 0 0`（使用 [`-fixShift`](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-fixshift) 时的默认设置）下，尺度参数将由数据推断。在 `-cauchy x y`（其中 x, y >0）下，尺度参数将被设为 x（针对物种形成率）与 y（针对灭绝率）。

##### `-pP` 
保存率的 gamma 分布先验的形状参数与尺度参数，该速率估算每个谱系每 Myr 的期望化石产出记录数。
示例：`-pP 1.5 1` （默认值）

##### `-pS` 
关于各时间段长度相对于数据集总时间跨度的 Dirichlet 先验的形状参数。若设为 `-pS 1`，该先验为均匀分布；而较大的取值会倾向于等长的时间段。
示例：`-pS 2.5` （默认值）

##### `-pC` 
在 [Covar 模型](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#settings-for-trait-correlated-rates-covar-models)下，相关性参数的正态先验的标准差。正态先验以 0 为中心。若设为 0，则标准差被赋予 Gamma 超先验 G(2,2) 并由数据估算。该选项仅应在估算至少 2 个相关性参数时使用，即使用 [`-mCov 2` 或 `-mCov`](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-mcov)。
示例：`-pC 1` （默认值）


***
### 高级 (BD)MCMC 设置
##### `-r` 
设置为耦合马尔可夫链 MCMC（Metropolis Coupled MCMC，MC3）分析而提供的并行“加热”链（heated chain）数目。若有可用处理器，每条链将使用一个不同的处理器。该数目包含“冷”链（cold chain）。该命令仅在为参数估算运行 MCMC 分析时使用（即配合 `-A 0`）。
示例：`-r 4`（即 1 条冷链与 3 条加热链）

##### `-t` 
设置 MC3 加热链的“温度”（temperature）参数。该命令仅在运行 MC3 分析时使用（即 `-r >1`）。
示例：`-t 0.03` （默认值）

##### `-sw` 
MC3 分析中尝试链间交换的频率。该命令仅在运行 MC3 分析时使用（即 `-r >1`）。
示例：`-sw 100` （默认值）

##### `-k` 
TI 中用于边际似然估算的缩放因子（scaling factor）数目。缩放因子数目越多，估算得到的边际似然越准确，但需要更长的计算时间。该命令仅在运行 TI 分析时使用（即配合 `-A 1`）。
示例：`-k 10` （默认值）

##### `-a` 
TI 分析中服从 beta 分布的缩放因子的形状参数 [(cf. Xie et al. 2011)](http://sysbio.oxfordjournals.org/content/60/2/150.long)。该命令仅在运行 TI 分析时使用（即配合 `-A 1`）。 
示例：`-a 0.3` （默认值）

##### `-M` 
BDMCMC 分析中模型更新的频率。该参数决定探索新出生-死亡模型的频繁程度。减小该数值可以改善对出生-死亡速率中转变数目的抽样。该命令仅在为参数估算运行 BDMCMC 分析时使用（即配合 `-A 2`）。
示例：`-M 25` （默认值）

##### `-B` 
设置 BDMCMC 算法在模型中提出新速率转变时所使用的出生率（birth-rate）。该值也对应于模型中物种形成/灭绝速率数目的一个 Poisson 分布先验的形状参数。该命令仅在为参数估算运行 BDMCMC 分析时使用（即配合 `-A 2`）。
示例：`-B 1` （默认值）

##### `-T` 
设置 BDMCMC 分析中用于更新模型的时间。增大该参数的效果与增大出生率（命令 `-B`）类似。该命令仅在为参数估算运行 BDMCMC 分析时使用（即配合 `-A 2`）。
示例：`-T 1` （默认值）

##### `-S`
设置经过多少代之后 BDMCMC 算法开始更新模型（例如在烧录期之后）。该命令仅在为参数估算运行 BDMCMC 分析时使用（即配合 `-A 2`）。
示例：`-S 1000` 

***
### 调参（tuning）参数
##### `-multiR` 
设置物种形成率与灭绝率更新的提议机制。当 `-multiR 0` 时，更新通过滑动窗口（sliding window）进行；而 `-multiR 1` 设置乘子提议（multiplier proposals）。窗口大小可用 [`-tR`](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-tr) 调整。
示例：`-multiR 1` （默认值）

##### `-tT` 
物种形成/灭绝时间更新的窗口大小（均匀滑动窗口）。
示例：`-tT 1` （默认值）

##### `-nT` 
一次更新中物种形成/灭绝时间的最大数目。若设为 0，则物种形成/灭绝时间被设为等于首次/末次出现时间，并且保存模型自动设为 HPP。
示例：`-nT 5` （默认值）

##### `-tQ` 
保存率（q）与 gamma 分布速率异质性的形状参数（alpha）更新的窗口大小（乘子提议），二者分别给出。
示例：`-tQ 1.2 1.2` （默认值）

##### `-tR` 
物种形成/灭绝速率更新的窗口大小（默认为乘子提议，另见 [`-multiR`](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-multir)）。
示例：`-tR 0.05` （默认值）

##### `-tS` 
物种形成/灭绝速率的转变时间更新的窗口大小（均匀滑动窗口）。
示例：`-tS 1` （默认值）

##### `-fS`
在更新出生-死亡参数时更新转变时间的频率（否则更新速率）。当不对速率转变进行抽样，或转变时间已被固定（使用命令 [`-fixSE`](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-fixse)）时，该值将被自动设为 0。
示例：`-fS 0.7` （默认值）

##### `-tC` 
在使用速率与某性状共变的模型时，相关性参数更新的窗口大小。各窗口大小分别针对与物种形成率、灭绝率和保存率的共变给出。这些参数是否被更新取决于所选的 Covar 模型（见命令 [`-mCov`](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-mcov)）。
示例：`-tC 0.025 0.025 0.1` （默认值）

##### `-fU` 
分别为保存率、出生-死亡参数以及 Covar 模型下相关性参数的更新频率。剩余部分用于更新物种形成与灭绝时间。
示例：` -fU 0.02 0.18 0.08` （Covar 模型下的默认值；以 2% 的频率更新保存参数、以 18% 的频率更新出生-死亡参数、以 8% 的频率更新 Covar 参数、以 72% 的频率更新物种形成与灭绝时间）

##### `-fR` 
一次更新中所更新的出生-死亡速率比例（更新频率由命令 `-fU` 定义）。该命令用于减小被更新的速率参数比例，尤其是在运行包含多次速率转变的出生-死亡模型时（例如由命令 [`-fixShift`](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-fixshift) 定义），以改善 MCMC 的混合（mixing）效果。
示例：`-fR 1` （默认值）
