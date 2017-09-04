# Linux 0.11源码注解学习(赵囧博士)

**分析过程主要是按照计算机启动过程进行的。因此分析的连贯性到初始化结束内核开始调用shell程序为止**

* 第一章[Makefile](1st-Makefile.md)
* 第二章[boot/](2nd-boot.md)
* 第三章[init/](3rd-init.md)
* 第四章[kernel/](4th-kernel.md)
* 第五章[fs/](5th-fs.md)
* 第六章[mm/](6th-mm.md)
* 第七章[include/](7th-include.md)
* 第八章[lib/](8th-lib.md)
* 第九章[tools/](9th-tools.md)

## 1. Linux的诞生和发展

linux的内核版本号的第二个数字为奇数表示其是正在开发的版本，偶数则表示稳定版
> 2.5.52 就是开发版; 2.6.13就是稳定版

## POSIX标准

POSIX(Portable Operating System Interface for Computing System)是由ISO/IEC开发的一簇标准。该标准是基于现有UNIX实践和经验，描述了操作系统的调用服务接口，用于保证应用程序可以在源码一级上在多种操作系统上移植和运行。
> POSIX.1标准是在1988年9月被批准的，全称是IEEE 1003.1-1988

## Linux内核的诞生

1991年10月5日，Linus在comp.os.minix新闻组上发布消息，正式宣布Linux内核系统的诞生(Free minix-like kernel sources for 386-AT)。因此10月5日对于Linux社区是一个特殊的日子，许多的Linux新版本的发布也都选择了这个日子。

## Linix操作系统版本的升迁

* 0.00  两个进程分别显示AAA BBB
* 0.01 第一个正式向外公布的Linux内核版本
* 0.10 由Ted Ts' o发布的Linux内核版本
* 0.11 基本可以可以正常运行的内核版本
* 0.12 加入对数学协处理器的软件模拟程序; 开始加入虚拟文件系统思想的内核版本

## 综述

Linix-0.11版本是在1991年12月8日发布，发布时还包括了以下文件：
> * bootimage.Z       具有美国键盘代码的压缩启动映像文件
> * rootimage.Z       以1200kB压缩的根文件系统映像文件
> * linux-0.11.tar.Z  内核源代码文件
> * as86.tar.Z        16位的汇编程序和装入程序
> * INSTALL-0.11      更新过的安装信息文件
