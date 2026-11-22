---
title: Dispersal Extinction Sampling model
source_url: https://github.com/dsilvestro/PyRate/wiki/5.-Dispersal-Extinction-Sampling-model
language: Simplified Chinese
mirrored_from: PyRate-doc/PyRate-wiki/5.-Dispersal-Extinction-Sampling-model-cn.md
headings: 0
translated_from: des-model.md
mirror: local Simplified-Chinese translation of the PyRate documentation
---

##输入数据准备
DES 模型需要一组重复的输入文件，其中各分类单元的产出记录已按时间分箱（time-bin）和区域归类。利用 PyRate 主目录中提供的 R 工具，或利用 R 包 [speciesgeocodeR](https://github.com/azizka/speciesgeocodeR)，可以很方便地从两个制表符分隔的文本文件生成这些输入文件。所需的数据为：1) 一张化石产出记录数据表；2) 一张包含所有分类单元现代分布的数据表。分布数据的提供形式既可以是离散区域分类（示例 1），也可以是产出记录坐标（示例 2）。重复（replication）来自对化石年龄估计值的均匀重抽样，即在每个化石的 earliestAge 与 latestAge 之间进行抽样。

####示例 1 - 离散区域分类输入

在第一个示例中，分类单元的分布已经以 DES 分析所关注的区域（"neartic" 和 "paleoartic"）的形式给出。示例输入文件与输出文件可在[此处](https://github.com/dsilvestro/PyRate/tree/master/example_files/DES_input_data)找到。输入数据的格式遵循 DarwinCore 标准。[Example_1_minimum_data.txt](https://github.com/dsilvestro/PyRate/blob/master/example_files/DES_input_data/Example_1_minimum_data.txt) 给出了化石产出记录的最小输入数据，[Example_1_recent_distributions.txt](https://github.com/dsilvestro/PyRate/blob/master/example_files/DES_input_data/Example_1_recent_distributions.txt) 给出了现代分布。请注意，如果某一分类单元在现代时期同时出现于两个区域，则每个区域都需要单独占一行。加载 R 工具文件 "pyrate_DES_utilities.R" 之后，运行下列代码即可生成 DES 输入文件（示例见此处）。该代码亦可在[此处](https://github.com/dsilvestro/PyRate/blob/master/pyrate_DES_input_example_script.R)获取。

`DESin function` 用于将输入数据转换为 DES 格式。`bin.size` 定义时间分箱的大小（如果化石年龄以百万年为单位，则此处也以百万年为单位）。分箱大小应在所期望的分辨率与数据可用性之间折中选取。`reps` 是所需的重复数目。重复来自化石的年代不确定性，化石通常只能给出一个最小年龄和一个最大年龄。对每一个重复，化石的年龄从最小年龄与最大年龄之间的均匀分布中抽样。

```{r, warning = F, echo = F}
#load utility functions
source(DES_input_preparation.R)

#load input files and convert into DES format
exp1 <- DESin("Example_data/Example_1_minimum_data.txt", "Example_data/Example_1_recent_distributions.txt", 
              bin.size = 2, reps = 3)
 
#explore the data for potential biases
summary(exp1)
par(ask = T)
plot(exp1)

#write DES input files to the working directory
write.DES.in(exp1, file = "Example_data/Example1_DES_in")

```


####示例 2 - 以坐标形式提供的物种分布

物种分布常常以坐标而非离散区域的形式获得。使用下列基于 speciesgeocodeR（>= v 1.0-6）的脚本，即可为 DES 输入准备化石数据与现代数据的坐标。但请务必注意，DES 假定现代数据是完整的，因此只有在样本量充分且经过良好整编的情况下，才应使用产出记录来表示现代数据。此外，通常应当使用分类单元的原生分布范围（以避免人为因素的影响，因为人为因素会夸大、有时也会缩小许多分类单元的现代分布范围）。

```{r, warning = F, echo = F}
library(speciesgeocodeR)
source(DES_input_preparation.R)

occ.thresh <- 0.1 #at least 10% occurrence in an area required

#Assign the fossil coordinates to operational areas
fos <- read.table("Example_data/Example_2_coordinates.txt", sep = "\t", header = T)
fos.class <- SpGeoCod("Example_data/Example_2_coordinates.txt", "Example_data/Example_regions.shp", areanames = "Region")
foss <- data.frame(fos, higherGeography = fos.class$sample_table$homepolygon)
foss <- foss[complete.cases(foss),]

#Assign the recent coordinates to operational areas, using the occurrence threshold
rec <- read.table("Example_data/Example_2_recent_coordinates.txt", sep = "\t", header = T)

rec.class <- SpGeoCod("Example_data/Example_2_recent_coordinates.txt", "Example_data/Example_regions.shp", 
                      areanames = "Region")

pres <- round(rec.class$spec_table[, 2:3] / rowSums(rec.class$spec_table[, 2:3]), 2)
pres[which(pres[, 1] >= occ.thresh ), 1] <- names(pres)[1] 
pres[which(pres[, 2] >= occ.thresh ), 2] <- names(pres)[2] 
pres <- data.frame(scientificName = rep(rec.class$spec_table[, 1], 2),
                   higherGeography = c(pres[, 1], pres[, 2]))
pres <- pres[pres$higherGeography %in% names(rec.class$spec_table), ]

#create DESin files
exp2 <- DESin(foss, pres, bin.size = 2, reps = 3)
write.DES.in(exp2, "Example2_out")

#explore data
summary(exp2)

par(ask = T)
plot(exp2)

```