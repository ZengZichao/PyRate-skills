---
title: PyRate 教程 \#1
source_url: https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_1.md
language: Simplified Chinese
mirrored_from: PyRate-doc/PyRate-tutorials/tutorials/pyrate_tutorial_1-cn.md
headings: 21
translated_from: tutorial-1.md
mirror: local Simplified-Chinese translation of the PyRate documentation
---
<img src="../../assets/images/PyRate_logo1024.png" align="left" width="80">  

# PyRate 教程 \#1


***
#### 目录
* [生成 PyRate 输入文件（方案 1）](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_1.md#generate-pyrate-input-file-option-1)  
* [生成 PyRate 输入文件（方案 2）](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_1.md#generate-pyrate-input-file-option-2)  
* [物种形成与灭绝速率随时间的估计](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_1.md#estimation-of-speciation-and-extinction-rates-through-time)    

* [返回索引](https://github.com/dsilvestro/PyRate/tree/master/tutorials#pyrate-tutorials---index) 
***



# 生成 PyRate 输入文件（方案 1）
1. **下载化石产出记录**：从 [Paleobiology Database（古生物数据库）](https://paleobiodb.org/classic/displayDownloadGenerator) 获取某个演化支的数据。例如，搜索犬属 *Canis* 并将其保存为 csv 文件，文件名可使用 *Canis_pbdb_data.csv*。下载该文件之前，请在“按分类单元选择（Select by taxonomy）”部分勾选“仅显示接受名（Show accepted names only）”，并在“选择输出选项（Choose output options）”部分取消勾选“在输出开头包含元数据（Include metadata at the beginning of the output）”。

2. **启动 R**：打开一个终端窗口并输入 `R`，然后按回车键。在 Mac 或 Windows 上也可以使用 R GUI 应用程序或 RStudio。 

3. **加载 *pyrate_utilities.r* 文件**，例如输入：  
  `source(".../PyRate-master/pyrate_utilities.r")`。请注意，为简便起见，此处用 `.../` 表示文件的完整路径。在大多数操作系统中，可以直接将 *pyrate_utilities.r* 文件拖放到 R 控制台中以粘贴完整路径。 

4. **确认哪些物种现今仍然存活**（如果有的话），因为运行分化（多样性增加）速率分析时必须提供这一信息。除非另有说明，所有物种都将被视为已灭绝。在 R 中输入以下内容以定义现存物种向量：   
  `extant_dogs = c("Canis rufus","Canis lupus","Canis aureus","Canis latrans","Canis mesomelas","Canis anthus","Pseudalopex gymnocercus","Canis adustus","Canis familiaris")`

5. **解析原始数据并生成 PyRate 输入文件**。这里将使用一个自动化函数，从 PBDB 原始表格中提取化石产出记录数据，并将其保存为与 PyRate 兼容的输入文件。在 R 中输入：   
  `extract.ages.pbdb(file= ".../Canis_pbdb_data.csv",extant_species=extant_dogs)`  
  **重要提示：**该函数不会检查同物异名、拼写错误等。此外还可以指定两个选项。选项 `replicates`（默认值设为 1）会在各自的时间范围内对每条化石产出记录的年龄进行重新抽样。如果使用 `replicates=10`，则会将十个重复数据集保存在单个 PyRate 输入文件中。这些重复数据集随后可（分别）进行分析，合并后的结果能够将化石记录中的年龄不确定性纳入考虑。选项 `cutoff` 可用于删除年龄范围大于给定时间范围的产出记录。例如，使用 `cutoff=10` 将删除最大年龄与最小年龄之差大于 10 Myr 的所有产出记录。 

6. **检查 PyRate 输入文件。**上一步生成了两个文件：一个文本文件（\*\_SpeciesList.txt），其中包含数据集里所有物种的列表；一个 python 文件（\*\_PyRate.py），其中所有产出记录都已按 PyRate 分析所需的格式整理好。可以直接在 PyRate 中检查该 python 文件，以获得若干汇总统计量：  
  a. 打开一个终端窗口
  b. 进入 Pyrate 文件夹，例如：  
    `cd ".../PyRate-master"`
  c. 使用以下参数启动 PyRate：  
  `python PyRate.py '.../Canis_pbdb_data_PyRate.py' -data_info`  
***

# 生成 PyRate 输入文件（方案 2）
1. **准备化石产出记录表。**可以使用文本编辑器或电子表格编辑器准备一张包含化石产出记录数据的表格。表格必须包含 4 列，分别为 1) 分类单元名称，2) 状态（指明该分类单元是 "extinct"（已灭绝）还是 "extant"（现存）），3) 最小年龄，以及 4) 最大年龄。表格应有表头（第一行），并且**每条化石产出记录占一行**（见下方示例）。最小年龄和最大年龄表示每条化石产出记录的年龄范围，通常依据地层界线确定。表中还可以增加一列，用于给出可在 PyRate 分析中使用的性状值（例如估算的体重）。  


| Taxon\_name   | Status  | MinAge | MaxAge |
| ------------- |:-------------:| -----:| -----:|
Canis\_ferox | extinct | 4.9    | 10.3
Canis\_lepophagus | extinct | 4.9 | 10.3  
Canis\_ferox | extinct | 4.9 | 10.3  
Canis\_ferox | extinct | 4.9 | 10.3  
Canis\_ferox | extinct | 4.9 | 10.3  
Canis\_edwardii | extinct | 0.3 | 4.9  
Canis\_armbrusteri | extinct | 0.3 | 4.9  
Canis\_latrans | extant | 0.3 | 4.9  
Canis\_latrans | extant | 1.8 | 4.9  
Canis\_thooides | extinct | 1.8 | 4.9  

2. **启动 R**，方法同上。  
3. **加载 *pyrate_utilities.r* 文件**，方法同上。  
4. **解析原始数据并生成 PyRate 输入文件**。在 R 中输入：   
  `extract.ages(file="…/PyRate/example_files/Ursidae.txt", replicates=10)` 该函数包含的 `replicates` 与 `cutoff` 选项与上文（方案 1）中所述 `extract.ages.pbdb()` 函数相同。 

### 考虑同一产地多条产出记录的年龄相关性
如果某个化石动物群或产地包含多条产出记录，即使在各自的时间范围内随机化其年龄，也应将这些记录视为同时代的。 
这可以通过在输入数据中指定一个 "Site" 列来实现，该列用一个数字标明每条产出记录所属动物群（产地）的 ID。例如下方示例中，前三条产出记录发现于同一产地，因此它们的随机年龄将完全相同。


| Taxon\_name   | Status  | MinAge | MaxAge | Site
| ------------- |:-------------:| -----:| -----:| -----:|
Canis\_ferox | extinct | 4.9    | 10.3 | 1
Canis\_lepophagus | extinct | 4.9 | 10.3  | 1
Canis\_ferox | extinct | 4.9 | 10.3  | 2
Canis\_ferox | extinct | 4.9 | 5.3  | 3
Canis\_edwardii | extinct | 0.3 | 4.9  | 4
Canis\_armbrusteri | extinct | 0.3 | 4.9 | 4 
Canis\_latrans | extant | 0.3 | 4.9  | 4 
Canis\_latrans | extant | 1.8 | 4.9  | 5
Canis\_thooides | extinct | 1.8 | 4.9  | 5

*pyrate_utilities.r*（`extract.ages()`）在输入表中包含名为 "Site" 的列时，会自动按产地对化石年龄进行重新抽样。感谢 Peter Wagner 和 Juan Cantalapiedra 就此提出的建议！


***

# 检查物种名称中的拼写错误与拼写不一致

PyRate 实现了一种用于检查物种名称拼写不一致（预期格式为 *Genus\_species*）的算法，因为这类问题在大型数据集中经常出现，并会影响分析的准确性。该功能由 `-check_names` 函数实现，它需要一个每行包含一个物种名称的文本文件。该函数可直接使用按上述步骤准备 PyRate 输入文件时生成的文本文件（\*\_SpeciesList.txt）。

该函数的调用方式如下：

 `python PyRate.py  -check_names .../PBDB_dataset_TaxonList.txt` 
 
该命令会返回一张保存在文本文件中的表格，其中列出可能是拼写错误的情况。等级 0 和 1 表示最可能属于拼写错误的情况，而等级 2 和 3 则最可能是真正不同的名称。 
**注意：该算法并不检查同物异名！**

输出的表格可能如下所示： 

| taxon1 | taxon2 | rank |
| ------------- |-------------| :-----:| 
Adocus_parvus | Adocus_pravus | 0
Testudo_annae | Testudo_nanus | 0
Trionyx_pliocaenicus | Trionyx_pliocenicus | 0
Testudo_aralensis | Testudo_tarakliensis | 1
Cyclanorbis_turkanensis | Cyclanorbis_urahensis | 2
Geochelone_eocaenica | Neochelys_eocaenica | 2
Megalochelys_sivalensis | Melanochelys_sivalensis | 2

需要研究者自行复核这些可能存在的不一致之处，并相应地修正其数据集中的名称。 


***
# 物种形成与灭绝速率随时间的估计

## 定义保存率模型
**保存的非齐次泊松过程（NHPP）**。默认情况下，PyRate 采用 NHPP 模型，即保存率在每个谱系的存续期间内按照钟形分布发生变化（Silvestro et al. 2014 Syst Biol）。 

**齐次泊松过程（HPP）**。或者，也可以使用保存率不随时间变化的 HPP 模型，命令为 `-mHPP`：

`python PyRate.py .../Canis_pbdb_data_PyRate.py -mHPP`

**随时间变化的泊松过程（TPP）**。另一种保存模型假定保存率在某一个预先定义的时间段内保持恒定，但可以在不同时间段之间变化（例如各个地质世）。如果我们预期速率异质性主要出现在时间维度上、而非谱系之间，那么该模型尤其有用。

我们可以建立一个在每个地质世内独立估计保存率的模型，方法是使用命令 `-qShift` 并提供一个包含各地质世分界时间的文件（示例文件 _PyRate-master/example\_files/epochs\_q.txt_ 中已给出）：  

`python PyRate.py .../Canis_pbdb_data_PyRate.py -qShift .../epochs_q.txt`  

保存率向量的默认先验是一个形状参数 = 1.5、速率参数 = 1.5 的伽马分布。这些参数值可以使用命令 `-pP` 修改，例如 `-pP 2 0.1` 会将形状参数改为 2、速率参数改为 0.1。
或者，先验的速率参数可以由数据本身估计，从而减少主观选择的影响，并使先验更好地适应数据。将该速率参数设为 0 即可启用此选项，例如： 

`python PyRate.py .../Canis_pbdb_data_PyRate.py -qShift .../epochs_q.txt -pP 1.5 0`

当速率参数设为零时，PyRate 会给该速率指定一个信息量很弱的指数超先验，并与其他所有模型参数一起对其抽样。当估计多个保存率时，推荐采用这种做法。


**速率异质性的伽马模型**。NHPP、HPP 与 TPP 模型都可以与速率异质性的伽马模型耦合，这使我们能够考虑保存率在各谱系之间的异质性。要设置伽马模型，我们在命令中添加标志 `-mG`：

`python PyRate.py .../Canis_pbdb_data_PyRate.py -mG` [NHPP 模型]  
`python PyRate.py .../Canis_pbdb_data_PyRate.py -mHPP -mG` [HPP 模型]
`python PyRate.py .../Canis_pbdb_data_PyRate.py -qShift .../epochs_q.txt -mG`  


**保存各谱系的相对保存率**。将 TPP 模型与伽马模型组合使用时，可以把估计得到的每个谱系的相对保存率记录到文件中。这通过在命令中添加标志 `-log_sp_q_rates` 实现，将额外保存一个日志文件，其中为数据集中的每个谱系列出一列，给出估计的相对保存率（注意实际速率取决于平均保存率及其随时间的变化）。 

`python PyRate.py .../Canis_pbdb_data_PyRate.py -qShift .../epochs_q.txt -mG -log_sp_q_rates` 

### 不同保存模型之间的模型检验
可采用最大似然检验（方法描述见[此处](https://www.cambridge.org/core/journals/paleobiology/article/improved-estimation-of-macroevolutionary-rates-from-fossil-data-using-a-bayesian-framework/334F08A74A6C92F1FEAD91A71FE59A1C)）来评估 NHPP、HPP 与 TPP 之中哪一个最受数据支持。运行该检验时，需要提供输入文件、为 TPP 模型提供速率转变时间的文件，并添加标志 `-PPmodeltest`

``python PyRate.py .../Canis_pbdb_data_PyRate.py -qShift .../epochs_q.txt -PPmodeltest``

请注意，这里并不检验伽马模型，但我们建议在模型检验所选出的 NHPP、HPP 或 TPP 最佳模型之上再加入伽马模型。 

## 分析设置
这里我们介绍使用 PyRate 对化石产出记录数据进行标准分析的主要设置。该分析将估计：

1. **各谱系的起源与灭绝时间**  
2. **保存率**及其**异质性**水平  
3. 随时间变化的**物种形成与灭绝速率**。 

速率随时间的变化由速率转变引入。速率转变的数目与时间位置由数据估计，可使用 RJMCMC 算法（默认）或 BDMCMC 算法。**专门针对 RJMCMC 的教程见[此处](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_3.md#pyrate-tutorial-3)。** BDMCMC 与 RJMCMC 都能估计带速率转变的出生-死亡模型，但**推荐使用 RJMCMC 算法，因为它通常能提供更准确的结果（开放获取论文见[此处](https://www.cambridge.org/core/journals/paleobiology/article/improved-estimation-of-macroevolutionary-rates-from-fossil-data-using-a-bayesian-framework/334F08A74A6C92F1FEAD91A71FE59A1C)）**。


该分析需要一个由上述 R 函数生成的 **PyRate 输入文件**。我们需要提供的第一个参数就是输入文件：

`python PyRate.py .../Canis_pbdb_data_PyRate.py -A 2`

在大多数操作系统（包括 Mac OS、Windows 和 Ubuntu）中，可以直接将输入文件拖放到终端窗口中，以粘贴完整路径和文件名。附加命令 `-A 2` 用于运行 BDMCMC 算法，而使用 `-A 4`（或省略该标志）会将算法设置为 RJMCMC。 

除输入文件外，PyRate 为所有参数都提供了默认设置。虽然有些参数只有在遇到收敛问题时才需要修改，但有少数几个参数非常重要，因为它们会改变基本的模型假设或分析的长度——见下文。

由于前面步骤生成的输入文件包含 10 个经过随机化的化石年龄重复数据集，因此我们可以指定要分析哪一个重复。**理想情况下，应当分析多个随机化重复并合并结果，以便把定年不确定性纳入**我们的速率估计之中。为指定要分析的重复，我们使用标志 `-j` 并在其后给出重复编号。例如使用：

`python PyRate.py .../Canis_pbdb_data_PyRate.py -A 2 -mHPP -mG -j 1`

即可设置分析使用第一个重复。

我们可以（某些情况下也应当）修改 MCMC 迭代次数和抽样频率。默认情况下，PyRate 将运行 10,000,000 次迭代，并每 1,000 次迭代抽样一次参数。根据数据集的大小，可能需要**增加迭代次数以达到收敛**（此时最好降低对链的抽样频率，以减小输出文件的体积）。这通过命令 `-n` 和 `-s` 实现：

`python PyRate.py .../Canis_pbdb_data_PyRate.py -mG -n 20000000 -s 5000`

在这些设置下，PyRate 将运行 2,000 万次迭代，每 5,000 次迭代抽样一次。因此生成的日志文件（见下文）将包含 4,000 个后验样本。  


## 输出文件
**请注意，RJMCMC 分析的默认输出与此不同，相关说明见[此处](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_3.md#rjmcmc-output)。**

上述 PyRate 分析会产生三个输出文件，保存在与输入文件同一目录下名为 *pyrate\_mcmc\_logs* 的文件夹中：

#### 1) sum.txt  
   以文本文件形式提供分析中所用全部设置的完整列表。  
#### 2) mcmc.log   
制表符分隔的表格，包含后验与先验的 MCMC 样本、保存过程的似然与出生-死亡的似然（分别以 *PP_lik* 和 *BD_lik* 表示）、保存率（*q_rate*）、其伽马分布异质性的形状参数（*alpha*）、抽到的速率转变数目（*k_birth*、*k_death*）、最古老谱系的起源时间（*root_age*）、总分支长度（*tot_length*），以及数据集中所有分类单元的物种形成与灭绝时间（分别以 *\*_TS* 和 *\*_TE* 表示）。当使用 TPP 保存模型时，各速率转变之间的保存率表示为 *q_0, q_1, ... q_n*（由老到新）。
#### 3) marginal_rates.log 
制表符分隔的表格，包含物种形成、灭绝以及净分化（多样性增加）边际速率的后验样本，这些速率在 1 个时间单位（通常为 Myr）内计算。 


## 汇总结果
这些日志文件可以在 [**Tracer**](https://github.com/beast-dev/tracer/releases/tag/v1.7.1) 程序中打开，以检查 MCMC 是否收敛，例如查看有效样本量（ESS），并确定烧录期（burn-in）所占的比例。 
当运行多个重复时，ESS 值应当分别从每个重复的日志文件中计算（即不要从[合并后的日志文件](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_1.md#combine-log-files-across-replicates)中计算），因为每个重复都基于不同的随机化数据集，因而可能收敛到略有差异的解。
不过，这些差异可以用来纳入化石产出记录定年方面的不确定性。

**mcmc.log** 文件可用于计算具有不同速率转变数目的出生-死亡模型的抽样频率。这通过使用 PyRate 命令 `-mProb` 并在其后给出日志文件来完成：

`python PyRate.py -mProb .../Canis_pbdb_data_mcmc.log -b 200`

其中标志 `-b 200` 表示将删除前 200 个样本（即前 200,000 次迭代，如果抽样频率设为 1,000 的话）。该命令会输出一张表格，给出具有不同速率转变数目的出生-死亡模型的相对概率。 


可以使用函数 `-plot` 基于 **marginal_rates.log** 文件生成速率随时间变化（RTT）图：

`python PyRate.py -plot .../Canis_pbdb_data_marginal_rates.log -b 200`

这将生成一个 R 脚本和一个 PDF 文件，其中的 RTT 图展示物种形成、灭绝以及净分化速率随时间的变化。使用标志 `-plot2` 代替 `-plot` 可以得到风格略有不同的 RTT 图。 



#### 合并各重复的日志文件
若要将来自不同重复的日志文件合并为一个，可以使用命令：

`PyRate.py -combLog path_to_your_log_files -tag mcmc -b 100`

其中 `path_to_your_log_files` 指定日志文件所在的目录；`-tag mcmc` 使 PyRate 合并所有文件名中包含 _mcmc.log_ 的文件（如果该目录中包含 PyRate 生成的多个输出文件，例如 _mcmc.log_ 和 _marginal\_rates.log_，则应使用相应的标签）；`-b 100` 表示将每个日志文件的前 100 个样本作为烧录期样本予以排除——应剔除多少烧录期样本，需要在检查日志文件之后确定，例如使用 Tracer。

若要生成合并了所有重复的速率随时间变化图，可以使用命令：

`PyRate.py -plot path_to_your_log_files -tag Canis_pbdb -b 100`

这将合并文件名中包含 `Canis_pbdb` 的所有 _marginal\_rates.log_ 文件，并把结果汇总到一张图中。​ 可以使用不同的标签来确定要合并哪些文件。    


#### 绘制保存率随时间变化图
使用命令 `-plotQ` 并在其后给出 `mcmc.log` 文件（包含文件路径），即可汇总并绘制用 TPP 模型估计的保存率：

`PyRate.py -plotQ .../Canis_pbdb_data_mcmc.log -qShift epochs.txt -b 100`

请注意，同样需要提供速率转变时间文件（例如 `PyRate-master/example_files/epochs_q.txt`）。


***
## 固定时间箱内的物种形成与灭绝速率
#### 分析设置
PyRate 还可以拟合**速率转变的数目与时间位置事先固定**的出生-死亡模型，例如依据地质世来固定。在这种情况下，必须使用命令 `-fixShift` 提供一个包含预定义速率转变时间的文件。该文件的格式非常简单，示例见：`.../PyRate-master/example_files/epochs.txt`。该模型对各速率转变之间的物种形成与灭绝速率采用半柯西（half-Cauchy）先验分布，并对各自的尺度参数设置超先验，以降低过度参数化的风险。 
为强制执行固定的速率转变时间，我们使用以下命令：

`python PyRate.py .../Canis_pbdb_data_PyRate.py -fixShift .../epochs.txt`

上文介绍的用于设置保存模型、MCMC 长度和抽样频率的其他选项在此情形下同样可用。

#### 汇总结果
以固定速率转变时间运行 PyRate 会产生与前述分析相同的 3 个输出文件。主要差别在于 *mcmc.log* 文件：由于速率转变数目已经固定，其中不再有速率转变数目的估计值（*k_birth*、*k_death*）。不过，该日志文件现在包含各速率转变之间的物种形成/灭绝速率（分别命名为 *lambda_0, lambda_1,* ... 和  *mu_0, mu_1, ...*），以及赋予物种形成与灭绝速率的半柯西先验分布的尺度参数估计值，分别以 *hypL* 和 *hypM* 表示。

RTT 图的生成方式与前述分析相同，即在命令 `-plot`（或 `-plot2`）后给出 *marginal_rates.log* 文件的路径，并设置作为烧录期丢弃的样本数（例如 `-b 100`）。



## 在边界处设置固定速率转变，同时在其间搜索速率转变

有时化石数据集会被最大和最小边界所截断（例如因为只有某个时间窗口内的产出记录可用）。这可能在时间范围的边缘造成表观上的速率转变，而其反映的其实是取样偏差。在这种情况下，可以根据数据集已知的时间边界，事先（_a priori_）固定速率转变的时间，并只估计该时间窗口内的速率，忽略边界之外发生的情况。  该功能可以与 [RJMCMC 算法](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_3.md#pyrate-tutorial-3)（`-A 4`）结合使用，以推断允许的时间窗口内的速率转变：

`python PyRate.py <data_set> -A 4 -edgeShift 18 2`

其中 -A 4 设置使用 RJMCMC 算法（该算法会搜索速率转变），而 `-edgeShift 18 2` 在时间 18 和 2 处设置固定的速率转变时间。采用这些设置时，算法只在该时间范围内搜索速率转变。
也可以用下面的命令只设置一个最大年龄边界处的速率转变：

`python PyRate.py <data_set> -A 4 -edgeShift 18 0`

或者设置一个最小年龄边界处的速率转变：

`python PyRate.py <data_set> -A 4 -edgeShift inf 0`

在汇总结果时，只应考虑该时间窗口内估计的速率，例如使用 [`plotRJ` 命令](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_3.md#plot-rates-through-time-and-rate-shifts)并配合标志 `-root_plot` 和 `-min_age_plot`。
