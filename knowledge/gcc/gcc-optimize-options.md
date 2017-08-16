# gcc -On(n=0-3)

> [gcc优化文档](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html)

一般来说，如果不指定优化标识的话，gcc就会产生可调试代码，每条指令之间将是独立的：可以在指令之间设置断点，使用gdb中的 p命令查看变量的值，改变变量的值等。并且把获取最快的编译速度作为它的目标。

当优化标识被启用之后，gcc编译器将会试图改变程序的结构（当然会在保证变换之后的程序与源程序语义等价的前提之下），以满足某些目标。
如：代码大小最小或运行速度更快（只不过通常来说，这两个目标是矛盾的，二者不可兼得）。在不同的gcc配置和目标平台下，同一个标识所采用的优化种类也是不一样的，这可以使用-Q --help=optimizers来获取每个优化标识所启用的优化选项。

下面每个-fx-x优化标识都可以在上述链接中找到解释

1. -O，-O1：这两个命令的效果是一样的，目的都是在不影响编译速度的前提下，尽量采用一些优化算法降低代码大小和可执行代码的运行速度。并开启如下的优化选项：
```bash
-fauto-inc-dec 
-fbranch-count-reg 
-fcombine-stack-adjustments 
-fcompare-elim 
-fcprop-registers 
-fdce 
-fdefer-pop 
-fdelayed-branch 
-fdse 
-fforward-propagate 
-fguess-branch-probability 
-fif-conversion2 
-fif-conversion 
-finline-functions-called-once 
-fipa-pure-const 
-fipa-profile 
-fipa-reference 
-fmerge-constants 
-fmove-loop-invariants 
-freorder-blocks 
-fshrink-wrap 
-fshrink-wrap-separate 
-fsplit-wide-types 
-fssa-backprop 
-fssa-phiopt 
-fstore-merging 
-ftree-bit-ccp 
-ftree-ccp 
-ftree-ch 
-ftree-coalesce-vars 
-ftree-copy-prop 
-ftree-dce 
-ftree-dominator-opts 
-ftree-dse 
-ftree-forwprop 
-ftree-fre 
-ftree-phiprop 
-ftree-sink 
-ftree-slsr 
-ftree-sra 
-ftree-pta 
-ftree-ter 
-funit-at-a-time
```

2. -O2该优化选项会牺牲部分编译速度，除了执行-O1所执行的所有优化之外，还会采用几乎所有的目标配置支持的优化算法，用以提高目标代码的运行速度。**默认推荐的优化级别，除非系统有特殊的需求。使用-O2优化，编译器会尝试优化代码性能并且在大小上也不做妥协，同时也不用花费过长的编译时间**
```bash
-fthread-jumps 
-falign-functions  -falign-jumps 
-falign-loops  -falign-labels 
-fcaller-saves 
-fcrossjumping 
-fcse-follow-jumps  -fcse-skip-blocks 
-fdelete-null-pointer-checks 
-fdevirtualize -fdevirtualize-speculatively 
-fexpensive-optimizations 
-fgcse  -fgcse-lm  
-fhoist-adjacent-loads 
-finline-small-functions 
-findirect-inlining 
-fipa-cp 
-fipa-cp-alignment 
-fipa-bit-cp 
-fipa-sra 
-fipa-icf 
-fisolate-erroneous-paths-dereference 
-flra-remat 
-foptimize-sibling-calls 
-foptimize-strlen 
-fpartial-inlining 
-fpeephole2 
-freorder-blocks-algorithm=stc 
-freorder-blocks-and-partition -freorder-functions 
-frerun-cse-after-loop  
-fsched-interblock  -fsched-spec 
-fschedule-insns  -fschedule-insns2 
-fstrict-aliasing -fstrict-overflow 
-ftree-builtin-call-dce 
-ftree-switch-conversion -ftree-tail-merge 
-fcode-hoisting 
-ftree-pre 
-ftree-vrp 
-fipa-ra
```

3. -O3该选项除了执行-O2所有的优化选项之外，一般都是采取很多向量化算法，提高代码的并行执行程度，利用现代CPU中的流水线，Cache等。
```bash
-finline-functions      // 采用一些启发式算法对函数进行内联
-funswitch-loops        // 执行循环unswitch变换
-fpredictive-commoning  // 
-fgcse-after-reload     //执行全局的共同子表达式消除
-ftree-loop-vectorize　  // 
-ftree-loop-distribute-patterns
-fsplit-paths 
-ftree-slp-vectorize
-fvect-cost-model
-ftree-partial-pre
-fpeel-loops 
-fipa-cp-clone options
```

这个选项会提高执行代码的大小，当然会降低目标代码的执行时间。**其实-O3并不是一个让人放心的优化级别，更多的时候会占据更多的内存和执行文件大小，从而拖慢系统**

4. -Os这个优化标识和-O3有异曲同工之妙，当然两者的目标不一样，-O3的目标是宁愿增加目标代码的大小，也要拼命的提高运行速度，但是这个选项是在-O2的基础之上，尽量的降低目标代码的大小，这对于存储容量很小的设备来说非常重要。为了降低目标代码大小，会禁用下列优化选项，一般就是压缩内存中的对齐空白(alignment padding)
```bash
-falign-functions  
-falign-jumps  
-falign-loops 
-falign-labels
-freorder-blocks  
-freorder-blocks-algorithm=stc 
-freorder-blocks-and-partition  
-fprefetch-loop-arrays
```

5. -Ofast: GCC4.7引入。该选项将不会严格遵循语言标准，除了启用所有的-O3优化选项之外，也会针对某些语言启用部分优化。如：-ffast-math ，对于Fortran语言，还会启用下列选项：
```bash
-fno-protect-parens 
-fstack-arrays
```

6. -Og: GCC4.8 引入。该标识会精心挑选部分与-g选项不冲突的优化选项，当然就能提供合理的优化水平，同时产生较好的可调试信息和对语言标准的遵循程度。
