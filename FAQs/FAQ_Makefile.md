# Makefile FAQ

## 1. 错误: prerequisites cannot be defined in recipes
复现：在目标的构建命令中使用foreach eval call某一个函数
> [Makefile.error](../knowledge/Docker/namespace/Makefile.error)

解决方法：使用makefile的提供的self-remaking features
> [Makefile](../knowledge/Docker/namespace/Makefile)

Android源码中有使用foreach来eval call函数的例子(不是放在目标的构建命令中，只是普通的执行)：
[build/core/dex_preopt.mk](http://androidxref.com/7.1.1_r6/xref/build/core/dex_preopt.mk#74)

> foreach函数：
> ```bash
> $(foreach val,<list>,<text>)
> ```
> 把参数<list>中的单词逐一取出放到参数所指定的变量中，然后再执行<text>所包含的表达式。每一次<text>会返回一个字符串赋值给val，循环过程中，<text>的所返回的每个字符串会以空格分隔，最后当整个循环结束时，<text>所返回的每个字符串所组成的整个字符串（以空格分隔）将会是foreach函数的返回值。所以，最好是一个变量名，<list>可以是一个表达式，而<text>中一般会使用这个参数来依次枚举<list>中的单词。
> ```bash
> names := a b c d
> files := $(foreach n,$(names),$(n).o)
> #files := a.o b.o c.o d.o
> ```
