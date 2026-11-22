---
title: PyRate - 高级设置
source_url: https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_6.md
language: Simplified Chinese
mirrored_from: PyRate-doc/PyRate-tutorials/tutorials/pyrate_tutorial_6-cn.md
headings: 14
translated_from: tutorial-6.md
mirror: local Simplified-Chinese translation of the PyRate documentation
---
# PyRate - 高级设置


### 快速烧录期（Fast burnin） 
##### `-fast_burnin <int>` 
指定使用近似 Gibbs 采样器更新起源与灭绝时间的马尔可夫链蒙特卡洛（MCMC）迭代次数，以加快收敛（默认值：`-fast_burnin 0`）


### 调优参数
##### `-multiR <boolean>` 
设置物种形成速率与灭绝速率更新的建议机制（proposal mechanism）。当 `-multiR 0` 时，使用滑动窗口进行更新；而 `-multiR 1` 则使用乘子建议（默认）。窗口大小可通过 `-tR` 调整。

##### `-tT <float>` 
物种形成/灭绝时间更新的窗口大小（均匀滑动窗口）。
示例：`-tT 1`（默认）

##### `-nT` 
一次更新的物种形成/灭绝时间的最大数目。若设为 0，则物种形成/灭绝时间将被直接设为首次/末次出现时间，且保存模型会自动设为 HPP。
示例：`-nT 5`（默认）

##### `-tQ` 
保存率（q）与呈 gamma 分布的速率异质性的形状参数（alpha）更新时各自的窗口大小（乘子建议）。
示例：`-tQ 1.2 1.2`（默认）

##### `-tR` 
物种形成/灭绝速率更新的窗口大小（默认使用乘子建议，另见 [`-multiR`](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-multir)）。
示例：`-tR 0.05`（默认）

##### `-tS` 
物种形成/灭绝速率转变时间（rate shift time）更新的窗口大小（均匀滑动窗口）。
示例：`-tS 1`（默认）

##### `-fS`
在更新出生-死亡参数时，更新速率转变时间的频率（否则更新的是速率参数）。当不对任何速率转变进行取样，或速率转变时间已被固定（使用命令 [`-fixSE`](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-fixse)）时，该值将被自动设为 0。
示例：`-fS 0.7`（默认）

##### `-tC` 
当使用速率与性状协变的模型时，相关性参数更新的窗口大小。各窗口大小分别对应与物种形成速率、灭绝速率和保存率的协变。这些参数是否被更新取决于所选的 Covar 模型（参见命令 [`-mCov`](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-mcov)）。
示例：`-tC 0.025 0.025 0.1`（默认）

##### `-fU` 
分别对应保存率、出生-死亡参数以及 Covar 模型下相关性参数的更新频率。剩余的部分用于更新物种形成时间与灭绝时间。
示例：` -fU 0.02 0.18 0.08`（Covar 模型下的默认值；以 2% 的频率更新保存参数，以 18% 的频率更新出生-死亡参数，以 8% 的频率更新 Covar 参数，以 72% 的频率更新物种形成与灭绝时间）

##### `-fR` 
一次更新的出生-死亡速率所占的比例（更新频率由命令 `-fU` 定义）。应使用该命令来减少被更新的速率参数比例，尤其在运行含有大量速率转变的出生-死亡模型时（例如由命令 [`-fixShift`](https://github.com/dsilvestro/PyRate/wiki/2.-PyRate:-command-list#-fixshift) 定义的速率转变），以改善 MCMC 的混合（mixing）效果。
示例：`-fR 1`（默认）
