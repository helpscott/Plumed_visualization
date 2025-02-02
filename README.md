# Plumed_visualization
基于python的PLUMED的可视化界面开发

Plumed Visualization and Setup Tool（测试版 0.1.0）是一款为分子动力学模拟中加速采样而设计的linux平台下的可视化辅助工具，旨在降低新学者对加速采样方法的入门门槛。工具对外完全免费开放，采用图形化界面，用户通过鼠标点击即可完成安装与使用，无需繁琐的命令行配置。此软件可快速实现 Plumed 文件的可视化与生成，一站式完成从加速采样方法选择到关键参数设定的过程，极大地简化了新手对加速采样的学习曲线。

本工具支持以下安装方式：
直接下载源码包project.zip，解压后，在根目录运行python -m src.main。

主要功能
可视化与参数设置：
提供直观的图形界面，用于快速配置 Plumed 中的各类加速采样方法，包括常规偏置（Metad、Walls 等）与输出文件定义等。鼠标放在参数上时，会显示详细的说明。
一键生成plumed文件：
自动整合用户配置的多种偏置方法、CV（Collective Variables）定义及输出文件配置，轻松完成 Plumed 驱动文件的生成。
命令行工具集成：
简化了 Plumed 命令行的调用，对常见操作（如 driver、sum_hills 等）提供了便利入口，帮助新手快速上手。
支持5种原子群组COM、CENTER、GHOST、GROUP和FIXEDATOM的定义。
支持20多种CV的定义，并根据不同种类的划分供用户选择。
支持6种加速采样方法的定义。
支持6种命令行工具的使用。

我们计划在后续版本中持续更新并完善以下功能：

将multi 类型的 CV以及多种文献中使用较多的非官方 CV 合并集成，并提供可视化配置入口。
增加数据分析模块，包括 Plumed 重加权等系列分析功能，集成更多后处理和可视化能力。
整合plumed本身支持的额外模块整合，如部分机器学习功能。
对一些文献中的算法、方法进行实现并整合以及可视化界面的实现（如同平均力积分、快速单质相变模拟等）。
后续引入力场模块，可以让用户针对体系使用现有的主流力场。

软件完全免费完全开放，可能有不足之处，请大家及时进行交流。

谢谢大家的意见与反馈~

邮箱：245780622@qq.com
