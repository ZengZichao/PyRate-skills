---
title: Preparing input file
source_url: https://github.com/dsilvestro/PyRate/wiki/1.-Preparing-input-file
language: Simplified Chinese
mirrored_from: PyRate-doc/PyRate-wiki/1.-Preparing-input-file-cn.md
headings: 4
translated_from: preparing-input-file.md
mirror: local Simplified-Chinese translation of the PyRate documentation
---
PyRate 程序对输入数据的格式有特定要求，请务必按照以下步骤仔细操作。以包含化石产出记录数据的表格为起点，可以使用脚本 ‘pyrate_utilities.r’ 中提供的 R 函数来生成格式正确的输入文件。 


***

所有化石产出记录都需要以表格（制表符分隔的文本文件）的形式提供，其列包括物种名称、该物种的状态（"extant" 或 "extinct"）以及最小年龄和最大年龄。最小年龄和最大年龄通常对应于某一特定化石被归入的阶（stage）的时间界限，一般可以从数据库中获取。目前 PyRate 无法处理这四列中的缺失信息，因此请事先删除这些条目。如果能够获得性状值，可以再添加一列来提供该值，并将其用于出生-死亡分析（注意，此处允许存在缺失数据，应记为 NA）。典型的输入文件如下所示：

`Species				Status	MinT	 MaxT    Trait`  
`Ursus_etruscus			extinct	 1.9	  2.6		 90  `  
`Ursus_etruscus			extinct	 1.2	  1.8		 90  `  
`Ursus_etruscus			extinct	 2.6	  3.4		 90  `  
`Agriotherium_insigne		extinct	 4.2	  5.3		285  `  
`Ursavus_brevirhinus		extinct	 8.2	  9.0		 80  `  
`Ursavus_brevirhinus		extinct	11.2	 15.2		 80  `  
`Agriotherium_intermedium	extinct	 3.4	  4.2		 NA  `  
`...					...		 ...	  ...		...	`  

随后即可使用随 PyRate 包提供的 R 工具脚本中的 R 函数 `extract.ages` 来处理该文件。若要加载 `extract.ages` 函数，请打开 R 控制台并输入：

`> source(file = "/path_to_file/pyrate_utilities.r")`

### `extract.ages`
`extract.ages` 函数需要传入包含原始数据的文件路径，此外还可以指定若干选项。

##### `replicates`  
该选项允许用户在单个输入文件中生成数据集的多个重复，每次都从以 MinT 和 MaxT 为边界的均匀分布中随机取样，重新确定各产出记录的年龄。这些重复可以在不同的运行中分别加以分析（参见 PyRate 命令 -j），将这些重复的结果合并起来，是考虑化石产出记录真实年龄不确定性的一种方法（另见 Silvestro et al. 2014）。
示例：  
`replicates=1`  （默认，生成 1 个数据集）  
`replicates=10`  （生成数据集的 10 个随机重复）
	
##### `cutoff` 
指定一个阈值，用于排除时间不确定性较高的化石产出记录，即 MinT 与 MaxT 之间时间范围过宽的记录。示例：  
`cutoff=NULL`（默认；所有产出记录都保留在数据集中）  
`cutoff=5`（时间范围达到或超过 5 Myr 的所有产出记录都从数据集中剔除）

##### `random`  
指定是为每条产出记录随机取样得到一个年龄（在 MinT 与 MaxT 之间），还是使用中点年龄。注意，当生成多个重复时（即 replicates > 1），该选项默认取值为 `TRUE`。示例：  
`random = TRUE`  （默认）  
`random = FALSE`  （使用中点年龄）

---
可以在 R 控制台中按如下方式调用 extract.ages 函数：

`> extract.ages(file = "/path_to_file/Ursidae.txt", replicates=10, cutoff=5, random=TRUE)` 

该命令会在各自对应的时间范围内对化石产出记录的年龄随机重新取样 10 次，并生成一个 Python 文件（此处名为 'Ursidae_PyRate.py'），该文件现在可以导入 PyRate 中进行分化（多样性增加）速率分析。 
