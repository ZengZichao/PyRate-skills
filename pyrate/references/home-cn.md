---
title: PyRate 手册
source_url: https://github.com/dsilvestro/PyRate/wiki/Home
language: Simplified Chinese
mirrored_from: PyRate-doc/PyRate-wiki/Home-cn.md
headings: 8
translated_from: home.md
mirror: local Simplified-Chinese translation of the PyRate documentation
---
<img src="../../assets/images/PyRate_logo1024.png" align="left" width="80">  
  

# PyRate 手册  

### 请参阅[教程（TUTORIALS）](https://github.com/dsilvestro/PyRate/tree/master/tutorials#pyrate-tutorials---index)以获取更新的文档。


**PyRate 是一个用于在贝叶斯框架（Bayesian framework）下从化石产出记录数据（fossil occurrence data）估计宏观演化速率的 Python 程序。** 它包含多种方法，可用于推断**物种形成（speciation）、灭绝（extinction）与扩散（dispersal）速率**、这些速率如何随时间变化，以及它们是否与**性状（trait）**（例如体型）相关，或是否对**连续变量（continuous variable）**（例如气候替代指标）或**竞争效应（competitive effects）**（通过多样性依赖）作出响应。宏观演化速率与**保存率（preservation rate）**联合估计，后者刻画生物体的化石化、取样与鉴定过程。 

安装与环境要求见[此处](https://github.com/dsilvestro/PyRate/wiki#compatibility-and-installation)。如有问题、建议或缺陷报告，请**[联系我们](mailto:pyrate.help@gmail.com)**！


**PyRate 软件包包含多个实现不同模型的程序。演示最重要功能的简明教程可在[此处](https://github.com/dsilvestro/PyRate/tree/master/tutorials)获取**

PyRate 遵循 [AGPLv3 许可证](https://tldrlegal.com/license/gnu-affero-general-public-license-v3-(agpl-3.0)#summary)。

***

#### `PyRate.py` 
PyRate.py 实现了推断随时间变化的物种形成与灭绝速率以及保存率的主要功能（命令与选项详见[此处](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list)）。它还包括一个用于推断[性状依赖的物种形成与灭绝](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#settings-for-trait-correlated-rates-covar-models)的模型。 
一次标准的 PyRate 分析需要三个步骤：(1) 准备[输入文件](https://github.com/dsilvestro/PyRate/wiki/1.-Preparing-input-file)；(2) 提供[输入文件](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#input-files-working-directory)与[分析设置](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#main-analysis-settings)并启动 PyRate；(3)[汇总](https://github.com/dsilvestro/PyRate/wiki/3.-Summarize-PyRate-results)结果并生成[速率随时间变化图](https://github.com/dsilvestro/PyRate/wiki/3.-Summarize-PyRate-results#plotsummarize-results)。**教程可在[此处](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_1.md#pyrate-tutorial-1)获取。**  
该程序所实现的主要方法描述见于下列文献：

Silvestro, D., Schnitzler, J., Liow, L.H., Antonelli, A. & Salamin, N. (2014) _Bayesian Estimation of Speciation and Extinction from Incomplete Fossil Occurrence Data_. Systematic Biology, 63, 349–367.

Silvestro, D., Salamin, N., Schnitzler, J. (2014) _PyRate: A new program to estimate speciation and extinction rates from incomplete fossil record_. Methods in Ecology and Evolution, 5, 1126–1131

---  

#### `PyRateContinuous.py` [需要依赖库 [pyrate_lib](https://github.com/dsilvestro/PyRate/wiki#pyrate_lib)]
该程序实现了一个出生-死亡模型（birth-death model），其中速率通过与一个时间连续变量之间的线性或指数相关而随时间变化。[详细的命令列表正在编写中](https://github.com/dsilvestro/PyRate/wiki/4.-PyRateContinuous)。此处实现的模型描述见于：

Silvestro D., Antonelli A., Salamin N., Quental T. B. (2015) The role of clade competition in the diversification of North American canids. PNAS, 112, 8684-8689.

---

#### `PyRateMCDD.py` [需要依赖库 [pyrate_lib](https://github.com/dsilvestro/PyRate/wiki#pyrate_lib)]
该程序实现了一个多演化支多样性依赖模型（Multiple Clade Diversity Dependence，MCDD），其中物种形成与灭绝速率可因演化支内部以及演化支之间的多样性依赖效应而随时间变化。详细的命令列表正在编写中。MCDD 模型描述见于：

Silvestro D., Antonelli A., Salamin N., Quental T. B. (2015) The role of clade competition in the diversification of North American canids. PNAS, 112, 8684-8689.

---

#### `PyRateDES.py` [需要依赖库 [pyrate_lib](https://github.com/dsilvestro/PyRate/wiki#pyrate_lib)]
该程序实现了一个扩散-灭绝-取样模型（Dispersal Extinction Sampling，DES），该模型利用两个离散区域的化石产出记录来估计区域之间的扩散速率与区域内的局部灭绝速率，同时纳入取样偏差。格式正确的输入文件可使用脚本 `DES_input_preparation.R` 生成，方法见[此处](https://github.com/dsilvestro/PyRate/wiki/5.-Dispersal-Extinction-Sampling-model)。详细的命令列表正在编写中。MCDD 模型描述见于：

Silvestro, D., Zizka A., Bacon C. D., Cascales-Minana B. and Salamin, N., Antonelli, A. (2016) Fossil Biogeography: A new model to infer dispersal, extinction and sampling from paleontological data. Phil Trans Roy Soc B, doi: 10.1098/rstb.2015.0225.

---

#### `pyrate_lib` 
依赖库 [pyrate_lib](https://github.com/dsilvestro/PyRate/tree/master/pyrate_lib)] 包含若干被多个 PyRate 程序使用的函数。该库无需任何安装。只需注意：**当你运行需要 `pyrate_lib` 的程序时（例如 [`PyRateContinuous`](https://github.com/dsilvestro/PyRate/wiki#pyratecontinuouspy-requires-library-pyrate_lib)），`pyrate_lib` 文件夹必须与该程序位于同一目录中**。 

***




## 兼容性与安装
PyRate 已在 Unix 操作系统（Mac OS 10.6 或更高版本与 Cent OS 6）以及 Windows（XP 与 7）上使用 Python 2.6 – 2.7 通过测试。该程序需要 argparse 库，在 Python 2.6 下该库需要手动安装（可在此处获取：https://code.google.com/p/argparse/ ），而在 Python 2.7 中它属于默认安装的一部分。**请注意，目前不支持 Python 3.x，Python 2.7.x 可在此处获取：https://www.python.org/downloads/。**

需要 numpy 与 scipy 库。源文件与安装程序可在此处获取：http://sourceforge.net/projects/numpy/files/ 与 http://sourceforge.net/projects/scipy/files/ 。或者，你可以下载 requirements.txt [文件](https://github.com/dsilvestro/PyRate/blob/master/requirements.txt)，并在终端（UNIX 系统）中使用 `pip install -r requirements.txt` 进行安装。在 UNIX 系统下，PyRate 将使用 multiprocessing 库与 thread（若可用），并对似然（likelihoods）进行并行计算（参见命令 -thread）。 


要在 UNIX 上启动一次 PyRate 分析，请通过终端（Terminal）进入 PyRate 目录并输入：
`./PyRate.py path_to_input_file/file_name.py [commands]`
或 
`python PyRate.py path_to_input_file/file_name.py [commands]`

要在 Windows 上启动 PyRate，请通过命令提示符（Command prompt）进入 PyRate 目录并输入：
`python PyRate.py path_to_input_file/file_name.py [commands]`

如果你使用的是 Windows，请确保 python.exe 的路径已包含在 PATH 环境变量中。为此，请编辑 PATH 环境变量并添加安装 Python 2.x 的文件夹（例如 ‘C:\python27’）。关于如何操作的简明教程，例如可在 Java 网站上找到：https://www.java.com/en/download/help/path.xml 

[`-plot`](https://github.com/dsilvestro/PyRate/wiki/3.-Summarize-PyRate-results) 函数会生成一个 R 脚本，用于产出图形输出。该脚本由 PyRate 使用 shell 命令 `RScript` 自动执行。如果你使用的是 Windows，请确保 Rscript.exe 的路径已包含在 PATH 环境变量中（在 Mac/Linux 下为默认设置）。为此，请编辑 PATH 环境变量并添加 R 安装目录的 \bin\ 文件夹（例如 ‘C:\Program Files\R\R-2.14.0\bin\i386’）。关于如何操作的简明教程，例如可在 Java 网站上找到：https://www.java.com/en/download/help/path.xml 

R 脚本 pyrate_utilities.r 已在 R 版本 2.x 与 3.x 下通过测试。`fit.prior` 函数需要 fitdistrplus 包。