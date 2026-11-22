---
title: 为 PyRate 设置虚拟环境
source_url: https://github.com/dsilvestro/PyRate/blob/master/tutorials/pyrate_tutorial_0.md
language: Simplified Chinese
mirrored_from: PyRate-doc/PyRate-tutorials/tutorials/pyrate_tutorial_0-cn.md
headings: 1
translated_from: virtual-environment.md
mirror: local Simplified-Chinese translation of the PyRate documentation
---
# 为 PyRate 设置虚拟环境

***
 
首先，请确认你的计算机上已安装 **Python（v.3.10 或更高版本）**。如需安装或升级 Python，请访问：[python.org](https://www.python.org/downloads/)。    
按照以下步骤，你可以在虚拟环境（virtual environment）中运行 PyRate，从而确保包含所有兼容的依赖包，同时不会影响你系统中已安装的 Python。

1) **创建虚拟环境**，在终端控制台（Windows 上为*命令提示符*）中输入： 

```
python -m venv desired_path_to_env/pyrate_env
```  
或在 Windows 上：

```
py -m venv desired_path_to_env/pyrate_env
```  
请注意，根据你计算机上默认的 Python 版本，你可能需要输入 `python3`。 

2) **激活虚拟环境**，在 MacOS/UNIX 上使用： 

```
source desired_path_to_env/pyrate_env/bin/activate
```
或在 Windows 上：

```
.\desired_path_to_env\pyrate_env\Scripts\activate
```  

3) **安装 PyRate 依赖包**到虚拟环境中（在 Windows 上请使用 `py` 代替 `python`），并先将 `your_path` 替换为指向 `PyRate-master` 目录的正确路径：

```
python -m ensurepip --upgrade
python -m pip install --upgrade pip
python -m pip install -r your_path/PyRate-master/requirements.txt
```

你可以使用以下命令确认 PyRate 现在已能在你的虚拟环境中运行：
```
python your_path/PyRate-master/PyRate.py -v
```

注意：如果出现 `Module FastPyRateC was not found.` 这一提示信息，程序仍然可以运行，但其中某些函数会改用速度较慢的实现方式。你可以按照这些[说明](https://github.com/dsilvestro/PyRate/blob/master/pyrate_lib/fastPyRateC/README.md)来安装 fastPyRateC 库。  

4) **如果你使用的是 Windows**，请确保 python.exe 的路径已被包含在 PATH 环境变量之中。为此，请编辑 PATH 环境变量，添加 Python 3.x 的安装文件夹（例如 `'C:\...\Python\Python312'`）以及存放 Python 脚本的文件夹（例如 `'C:\...\Python\Python312\Scripts'`）。例如可以在 [Java 网站](https://www.java.com/en/download/help/path.xml) 上找到一篇简单的操作教程。 
函数 -plot 会生成一个用于产生图形输出的 R 脚本。该脚本由 PyRate 通过 shell 命令 `RScript` 自动执行。如果你使用的是 Windows，请确保 `Rscript.exe` 的路径已被包含在 PATH 环境变量之中（在 Mac/Linux 上为默认设置）。为此，请编辑 PATH 环境变量，添加 R 安装目录下的 \bin 文件夹（例如 `'C:\Program Files\R\R-4.4.1\bin'`）。例如可以在 [Java 网站](https://www.java.com/en/download/help/path.xml) 上找到一篇简单的操作教程。

