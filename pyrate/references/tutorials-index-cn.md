---
title: PyRate 教程 - 索引
source_url: https://github.com/dsilvestro/PyRate/blob/master/tutorials/README.md
language: Simplified Chinese
mirrored_from: PyRate-doc/PyRate-tutorials/tutorials/README-cn.md
headings: 8
translated_from: tutorials-index.md
mirror: local Simplified-Chinese translation of the PyRate documentation
---
<img src="../../assets/images/PyRate_logo1024.png" align="left" width="80">  

# PyRate 教程 - 索引
  
  
---
### 安装 PyRate

* [在虚拟环境中安装 PyRate 及其依赖包](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_0.md)。

---


### 准备输入文件
* [生成 PyRate 输入文件（选项 1）](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_1.md#generate-pyrate-input-file-option-1)  
* [生成 PyRate 输入文件（选项 2）](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_1.md#generate-pyrate-input-file-option-2)  
* [检查物种列表中的拼写不一致与笔误](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_1.md#check-species-names-for-typos-and-inconsistent-spelling)  

---
### 估算物种形成率与灭绝率随时间的变化
* [设置保存模型](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_1.md#defining-the-preservation-model)
* [使用 RJMCMC 估算含速率转变的出生-死亡模型（推荐算法）](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_3.md#estimate-rate-variation-using-reversible-jump-mcmc)
* [使用 BDMCMC 估算含速率转变的出生-死亡模型](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_1.md#estimation-of-speciation-and-extinction-rates-through-time)
* [固定时间分箱的出生-死亡模型](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_1.md#speciation-and-extinction-rates-within-fixed-time-bins)
* [在大型数据集上运行 PyRate](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_3.md#running-pyrate-on-large-datasets)
* [约束起源时间与灭绝时间](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_3.md#constraining-origination-and-extinction-times)


### 输出的绘图与汇总
* [绘制边缘速率（RJMCMC）](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_3.md#plot-rates-through-time-and-rate-shifts)
* [BDMCMC 输出的绘图与汇总](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_1.md#summarize-the-results)
* [绘制保存率随时间的变化曲线](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_1.md#plot-preservation-rates-through-time)
* [绘制 range-through 多样性轨迹](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_2.md#plot-range-through-diversity-trajectory-lineage-through-time-plot)

---
### 具有时间连续相关变量的出生-死亡模型
* [为 PyRateContinuous 生成输入文件](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_2.md#generate-input-file-for-pyratecontinuous)
* [多样性依赖的出生-死亡模型](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_2.md#diversity-dependent-birth-death-models)
* [与时间连续变量的相关性](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_2.md#correlation-with-a-time-continuous-variable)
* [利用边缘似然进行模型检验](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_2.md#model-testing-using-thermodynamic-integration-ti)
* [多演化支多样性依赖模型](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_4.md#the-multiple-clade-diversity-dependent-model-mcdd)
* [多元出生-死亡模型（多个时间连续相关变量）](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_4.md#the-multivariate-birth-death-model-mbd)

### 其他出生-死亡模型
* [性状依赖的出生-死亡模型](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_4.md#trait-correlated-diversification)
* [年龄依赖的灭绝模型](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_4.md#age-dependent-extinction-ade-model)
* [出生-死亡时间种（chronospecies）模型](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_4.md#the-birth-death-chronospecies-bdc-model)
* [出生-死亡神经网络（BDNN）模型](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_bdnn.md)

---
### 扩散-灭绝-取样（Dispersal Extinction Sampling）模型
* [为 DES 分析准备输入数据](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_5.md#input-data-preparation)
* [运行 DES 分析](https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_5.md#running-a-des-analysis)

---








