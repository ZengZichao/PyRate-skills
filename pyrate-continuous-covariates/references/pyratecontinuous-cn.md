---
title: PyRateContinuous
source_url: https://github.com/dsilvestro/PyRate/wiki/4.-PyRateContinuous
language: Simplified Chinese
mirrored_from: PyRate-doc/PyRate-wiki/4.-PyRateContinuous-cn.md
headings: 8
translated_from: pyratecontinuous.md
mirror: local Simplified-Chinese translation of the PyRate documentation
---
### 生成输入文件
PyRateContinuous 实现的是出生-死亡模型（birth-death model），其中物种形成（speciation，即起源）速率与灭绝（extinction）速率会随时间发生变化，且这种变化是某个连续时间变量（continuous variable）作用的结果，例如演化支（clade）自身的多样性，或古温度等外部因素。该程序不对保存率（preservation rate）进行建模，并假定各谱系（lineage）的起源时间与灭绝时间已知或已被估计出来，通常是在[先前的 PyRate 分析](https://github.com/dsilvestro/PyRate/wiki/3.-Summarize-PyRate-results#_mcmclog)中完成的。
因此，`PyRateContinuous.py` 的输入文件是一个简单的表格，列出每个物种的起源时间与灭绝时间。该表格采用制表符分隔的文本文件格式，第一行为列标题，之后每个物种占一行。每行包含 4 列：第一列指明物种所属的演化支，这仅在 MCDD 分析中才有用（PyRateMCDD 的 Wiki 页面正在建设中），其他所有分析中该列应全部填 0。第二列给出物种的数字标识符（这些数值是任意的，仅用于引用参考）。最后，第三列和第四列分别给出每个物种的起源时间和灭绝时间。**PyRateContinuous 的输入文件可以使用以下命令从 PyRate 的 *_mcmc.log 文件生成：**

##### `-ginput`  
该命令分析一个或多个由 PyRate 生成的[日志文件](https://github.com/dsilvestro/PyRate/wiki/3.-Summarize-PyRate-results#_mcmclog)，产出一个文件，该文件可在后续 [PyRateContinuous](https://github.com/dsilvestro/PyRate/wiki#pyratecontinuouspy-requires-library-pyrate_lib) 或 [PyRate](https://github.com/dsilvestro/PyRate/wiki#pyratepy) 的分析中通过 `-d` 标志作为输入使用。该命令的参数可以是一个日志文件，也可以是包含日志文件的目录。在排除烧录期（burn-in）样本之后，根据每个日志文件计算起源时间和灭绝时间的后验均值（被排除的样本数由 `-b` 命令设定）。  
示例：  
`python PyRateContinuous.py -ginput path_to_log_file/Ursidae_1_mcmc.log -b 100` # 生成一个名为 `Ursidae_1_se_est.txt` 的文件，其中包含每个物种起源时间与灭绝时间的估计结果（估计前已将前 100 个样本作为烧录期排除）。  
`python PyRateContinuous.py path_to_log_file/ -b 100` # 生成的文件数目与目录中找到的 `*mcmc.log` 文件数目相同。  
`python PyRateContinuous.py path_to_log_file/ -b 100 -tag Ursidae` # 生成单一文件，其中包含每个物种起源时间与灭绝时间的估计结果（由所有文件名中含有“Ursidae”的日志文件合并计算得到）。不同的日志文件被视为同一分析的重复。各个重复可在 PyRate 与 PyRateContinuous 的后续分析中使用[命令 `-j`](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-j) 进行分析。

***
### 设置分析
##### `-d`
通过该命令提供输入文件。更多细节见[此处](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-d)及上文。

##### `-A`
设定 MCMC（马尔可夫链蒙特卡洛）算法：使用 `-A 0` 进行参数估计，使用 `-A 1` 估计模型的边缘似然以进行模型检验（[更多细节见此](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-a)）。

##### `-DD`  
使用 `-DD` 命令运行**多样性依赖（diversity dependence）模型**，在该模型中起源速率与灭绝速率可能与演化支自身的多样性呈[线性或指数](https://github.com/dsilvestro/PyRate/wiki/PyRateContinuous#-m)相关。所估计的多样性依赖参数在输出中以 `Gl` 和 `Gm` 记录，分别对应物种形成和灭绝。

##### `-c`  
作为多样性依赖模型的替代方案，用户可以提供一个表格，报告某个**变量（例如古气候替代指标）的取值及其变化时间**。该表格是制表符分隔的文本文件，含标题行以及两列，分别指示变量的变化时间和取值。[示例文件见此](https://github.com/dsilvestro/PyRate/blob/master/example_files/temperature.txt)。可以假定该变量与起源速率和灭绝速率之间存在线性或指数相关关系（[使用命令 `-m`](https://github.com/dsilvestro/PyRate/wiki/PyRateContinuous#-m)）。所估计的相关参数在输出中以 `Gl` 和 `Gm` 记录，分别对应物种形成和灭绝。

##### `-m`
设定相关模型。共有三个可用选项：  
`-m -1` 无相关。该选项拟合恒定速率的出生-死亡模型，主要用于使用边缘似然进行模型比较。  
`-m 0` 指数相关（默认值；见 [Silvestro et al. 2015 PNAS](http://www.pnas.org/content/suppl/2015/06/23/1502803112.DCSupplemental/pnas.1502803112.sapp.pdf) 中的公式 7）  
`-m 1` 线性相关。  