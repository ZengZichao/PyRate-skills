---
title: PyRate 教程 \#2
source_url: https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_2.md
language: Simplified Chinese
mirrored_from: PyRate-doc/PyRate-tutorials/tutorials/pyrate_tutorial_2-cn.md
headings: 13
translated_from: tutorial-2.md
mirror: local Simplified-Chinese translation of the PyRate documentation
---
<img src="../../assets/images/PyRate_logo1024.png" align="left" width="80">  

# PyRate 教程 \#2

***  
#### 目录
* [具有时间连续相关变量的出生-死亡模型](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_2.md#birth-death-models-with-time-continuous-correlates)  
* [模型检验](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_2.md#model-testing-using-thermodynamic-integration-ti)

* [返回目录](https://github.com/dsilvestro/PyRate/tree/master/tutorials#pyrate-tutorials---index) 
***


# 提取起源与灭绝时间的估计值
起源与灭绝时间的估计值将作为 PyRateContinuous 以及 PyRate 软件包中其他分析的输入文件。 
该表格以制表符分隔的文本文件形式保存，第一行为列标题，随后每个物种占一行。每一行包含 4 列：第一列标示物种所属演化支（clade）的归属，这一列仅在使用 [MCDD 模型](https://github.com/dsilvestro/PyRate/wiki#pyratemcddpy-requires-library-pyrate_lib) 时才有用，在其他所有分析中都应填 0。第二列标示物种的数字标识符（这些取值是任意的，仅作参考）。最后两列则给出每个物种或分类单元的起源时间与灭绝时间。  

### 起源与灭绝时间的平均值
PyRateContinuous 的输入文件可以使用 `-ginput` 命令，从此前某次 PyRate 分析产生的 _mcmc.log 文件中生成。例如，若在先前使用 PyRate 进行的分析中生成了名为 "Canidae_1_G_mcmc.log" 的输出文件，则可用该文件来提取每个物种起源与灭绝时间的估计值：  

`python PyRate.py -ginput .../Canidae_1_G_mcmc.log -b 100`  

其中命令 `-b 100` 表示应将前 100 个样本作为烧录期（burn-in）样本舍弃。该命令生成 3 个输出文件，保存在与 "Canidae_1_G_mcmc.log" 文件相同的目录中：  
  
1. 一个文本文件，包含**起源与灭绝时间的估计值**，将作为 PyRateContinuous 的输入文件使用（例如 "Canidae\_1\_G\_se\_est.txt"）
2. 一个 PDF 文件，绘制每条谱系的持续时间以及该演化支的多样性轨迹（**穿越时间谱系图**，lineage through time plot，另见下文的选项说明）
3. 生成上述 PDF 文件所用的 R 脚本。


**附加选项。**
你也可以在 `-ginput` 命令后给出一个包含各 log 文件的目录路径：

`python PyRate.py -ginput .../path_to_log_files -b 100`

此时，每个扩展名为 `*_mcmc.log` 的文件都会被分别处理。

你可以使用附加标志 `-tag` 来识别应当合并进同一个 `...se_ext.txt` 文件的文件，例如由重复分析所得的文件。例如，使用如下命令 	

`python PyRate.py -ginput .../path_to_log_files -tag Canidae -b 100`  

所有文件名中包含 `Canidae` 且扩展名为 `*_mcmc.log` 的 log 文件将被合并为一个 `...se_ext.txt` 文件，其中每个物种的起源与灭绝时间按各次重复分别成列给出。

### 起源与灭绝时间的多个样本
若要从后验中抽取起源与灭绝时间的多个样本而非平均值，可将上述命令与附加标志 `-resample` 结合使用，并指定需要抽取的样本数目。
例如： 

`python PyRate.py -ginput .../Canidae_1_G_mcmc.log -b 100 -resample 10`  

将抽取十组起源与灭绝时间，并将其作为附加列存入所生成的文本文件中。 
同样，命令： 

`python PyRate.py -ginput .../path_to_log_files -tag Canidae -b 100 -resample 10`  

将从每个文件中抽取十个取值，并将它们拼接为一张表格。 


# 绘制区间贯穿的多样性轨迹（穿越时间谱系图）
`...se_ext.txt` 文件可用于生成基于区间贯穿（range-through）多样性的穿越时间谱系（lineage through time，LTT）图。为此，我们需要提供 `...se_ext.txt` 文件（通过 `-d` 命令），并在 `-ltt ` 标志后跟一个数字，以在不同选项之间进行选择：

`python PyRate.py -d Canidae_1_G_se_est.txt -ltt 1`

该选项绘制穿越时间的平均多样性，并由各次重复推断出最小与最大范围，以阴影区域显示。该命令生成 3 个输出文件：1) 一个包含 LTT 图的 **pdf 文件**；2) 一个**给出多样性轨迹估计值的表格**；3) 用于生成该图的 **R 脚本**。

当使用

`python PyRate.py -d Canidae_1_G_se_est.txt -ltt 2`

你会得到一幅相似的图，只是多样性经过 log10 变换。
最后，使用 

`python PyRate.py -d Canidae_1_G_se_est.txt -ltt 3`

各次重复的 LTT 图将以单独的曲线显示。

默认情况下，LTT 图基于大小为 1 个时间单位的时间片（time bin）内的多样性计数。若要绘制基于更精细时间分辨率的计数图，可使用命令 `-grid_plot`，它定义时间片的大小。
例如，使用：

`python PyRate.py -d Canidae_1_G_se_est.txt -ltt 1 -grid_plot 0.1`

多样性轨迹将以 0.1 Myr 的时间片进行计算。


# 具有时间连续相关变量的出生-死亡模型
本教程介绍如何在出生-死亡模型（birth-death model）下分析数据，其中的速率通过与某个时间连续变量呈线性或指数相关的方式随时间变化。时间连续变量可以包括演化支自身的多样性（多样性依赖，diversity dependence），也可以是古环境变量，例如温度或海平面。具有时间连续相关变量的出生-死亡模型在程序 "PyRateContinuous.py" 中实现。 

## 为 PyRateContinuous 生成输入文件
该程序不对保存率（preservation rate）进行建模，而是假定每条谱系的起源与灭绝时间已知或已被估计（通常是在此前的 PyRate 分析中估计得到）。因此，PyRateContinuous.py 的输入文件只是一张简单的表格，列出每条谱系的起源时间与灭绝时间。该表格的生成方法如[此处](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_2.md#extract-estimated-times-of-origination-and-extinction)所述



## 多样性依赖的出生-死亡模型
在多样性依赖模型中，起源与灭绝速率可能与演化支自身被取样的（区间贯穿）多样性呈线性或指数相关。要运行多样性依赖的出生-死亡模型分析，可启动 PyRateContinuous，提供输入数据（`-d` 标志）并添加 `-DD` 标志：  

`python PyRateContinuous.py -d .../Canidae_1_G_se_est.txt -DD`

该程序实现了两种由 `-m` 标志定义的多样性依赖模型：**指数模型**（`-m 0`），其中物种形成与灭绝速率是演化支多样性的指数函数；以及**线性模型**（`-m 1`），其中物种形成与灭绝速率与多样性呈线性相关。  

`python PyRateContinuous.py -d .../Canidae_1_G_se_est.txt -DD -m 0`

为便于模型检验，你还可以设置 `-m -1`，它运行一个空模型，其中物种形成与灭绝速率为常数且不依赖于多样性。  

与标准的 PyRate 分析一样，MCMC 迭代次数与取样频率可分别通过 `-n` 和 `-s` 标志设置。  

请注意，PyRateContinuous 不估计起源与灭绝时间，也不估计保存率。这意味着需要估计的参数数量远少于标准 PyRate 分析。因此，将 MCMC 迭代次数设为 100,000 到 100 万之间，对大多数数据集而言就足够了。

#### 输出文件
PyRateContinuous 生成单个输出文件，其中包含所有参数的后验样本。估计得到的**多样性依赖参数**在输出 log 文件中分别以 *Gl* 和 *Gm* 记录，对应物种形成与灭绝。当这些参数显著不同于 0（依据其 95% HPD）时，我们即认为该相关性显著为正或显著为负（取决于 *G* >> 0 还是 *G* << 0）。**基线物种形成与灭绝速率**（在 log 文件中标作 *L0* 和 *M0*）表示在现今时刻的物种形成与灭绝速率估计值。  

该 log 文件可在 Tracer 中打开，以检查是否达到收敛，并查看所关心参数的均值与 95% HPD。 

#### 绘制物种形成与灭绝速率随时间的变化
PyRateContinuous 可根据估计得到的基线速率与多样性依赖参数，绘制边际的物种形成与灭绝速率随时间变化图。要生成 RTT 图，可输入：

`python PyRateContinuous.py -d .../Canidae_1_G_se_est.txt -DD -m 0 -b 100 -plot .../Canidae_1_G_se_est_DD_0_exp.log -b 200`
 
这将生成一个 R 脚本和一个 PDF 文件，其中的 RTT 图显示物种形成速率与灭绝速率随时间的变化。命令 `-b 200` 指定将前 200 个样本作为烧录期（burn-in）样本舍弃。 


## 与时间连续变量的相关性
你可以拟合这样的出生-死亡模型：物种形成与灭绝速率随时间变化，且二者是某个时间连续变量（例如古温度的代理指标）的线性或指数函数。该变量的取值应在一个简单的、以制表符分隔并带有标题行（第一行）的文本文件中提供，包含两列，分别给出时间与变量值（示例见 `PyRate-master/example_files/temperature.txt`）。   

要运行温度依赖的物种形成与灭绝速率分析，应使用命令 `-c` 提供包含该变量的文本文件：
 
`python PyRateContinuous.py -d .../Canidae_1_G_se_est.txt -m 0 -c temperature.txt`

与多样性依赖模型相同（见上文），`-m` 标志用于在默认的**指数模型**（`-m 0`，其中物种形成与灭绝速率是时间连续变量的指数函数）与**线性模型**（`-m 1`，假定二者呈线性相关）之间进行切换。  

时间连续变量默认会被重新标定，使其取值范围等于 1；此外还整体平移，使其在现今时刻等于 0。估计得到的**相关参数**在输出 log 文件中分别以 *Gl* 和 *Gm* 保存，对应物种形成与灭绝；而**基线物种形成与灭绝速率**（在 log 文件中标作 *L0* 和 *M0*）表示在现今时刻的物种形成与灭绝速率估计值。时间连续变量的重新标定方式可通过 `-r` 标志更改。 

速率随时间变化图可使用命令 `-plot` 生成，如上面对 DD 模型所示，例如

`python PyRateContinuous.py -d .../Canidae_1_G_se_est.txt -m 0 -c temperature.txt -plot .../my_logfile.log -b 100`



***
## 使用热力学积分（TI）进行模型检验

你可以使用 TI 算法计算模型的边际似然，从而**比较备选模型的拟合优度**。例如，你可以比较多样性依赖模型中线性相关与指数相关的拟合效果，或者比较多样性依赖模型与温度依赖模型的拟合效果。分析设置与模型定义都与上文所述相同，TI 算法通过 `-A 1` 标志启用：

`python PyRateContinuous.py -d .../Canidae_1_G_se_est.txt -m 0 -c temperature.txt -A 1`

PyRateContinuous 默认使用 10 个缩放类别运行 TI，而迭代次数（由 `-n` 标志指定）对应于每个类别的 MCMC 迭代次数。   

运行 TI 会产生单个 log 文件作为输出，边际似然即由该文件计算得到。当你在一组备选模型下运行完 TI 分析后，可以使用命令 `-mL` 计算所有模型的边际似然。该命令接受 log 文件所在的路径，并为目录中扩展名为 ".log" 的每个文件计算边际似然。重要的是使用 `-b` 标志**指定合适的烧录期（burn-in）**，例如：  

`python PyRateContinuous.py -mL .../path_to_my_logfiles -b 100`

该命令将生成单个文本文件，其中包含所有模型的边际似然。它还会生成新的 log 文件，仅包含由 TI 算法采样的 MCMC 状态中“冷”的部分。这些 log 文件的内容可在 Tracer 中查看，并用于参数估计。 






