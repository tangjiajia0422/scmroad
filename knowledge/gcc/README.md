# gcc

## gcc编译基本流程

1. c(.c)和c++(.cc, .cpp, .cxx)的源文件
> gcc -E a.c -o a.i
> // 如果不加-o参数，gcc会把处理过的源文件放到标准输出中
2. 预处理后的源文件。c源文件预处理后后缀为.i, c++为.ii 。
> gcc -S a.i
> //会在当前文件夹下生成a.s
3. 编译后生成的汇编源代码。后缀为.s,.S。
> gcc -c a.s
> //只进行汇编生成目标文件,.o结尾的目标文件可以用
> //(ar crv libabc.a a.o b.o c.o )打包成形如lib×××.a的静态库
4. 目标文件与库文件进行链接，生成可执行文件。
> gcc a.o //在当前文件夹下生成a.out
> 其中任何一种状态，用 gcc 如果不加 -c，-E，-S 选项都会直接生成可执行文件，如果加上了选项，可以由之前任一状态生成所需要的文件（如gcc -S a.c可以直接生成a.s，gcc -c a.i可以直接生成a.o ）。如果是c++直接换用g++命令就行。
5. gcc -v可以输出编译过程的配置和版本信息。

## gcc警告提示

* -fsyntax-only     检查程序中的语法错误，不产生输出信息
* -w                禁止所有警告信息
* -Wunused          声明了木有用
* -Wmain            main函数定义不常规
* -Wall             提供所有警告
* -pedantic-errors  允许ansi c标准列出的全部信息

## gcc常用选项

* -g 加入调试信息，gdb调试的时候要用。
* -On [优化选项](./gcc-optimize-options.md)。这里的n可以用0-3来替代。数字越大优化效果越好，-O0表示不进行优化。优化可能针对硬件进行优化，也可能针对代码优化（删除公共表达式，循环优化，删除无用信息）。优化可能大大增加编译时间和内存，他通常会将循环或函数展开，使他们以内联的方式进行，不是通过函数调用，这样可以显著提高性能，不过调试最好不要用优化选项。
* -l 指定要用到的库，注意这里之后要加的是库的名字，如果是多线程，可能要用到pthread库，那么此时就要加上 -lpthread ，这样gcc就会到库目录中找名为libpthread.so（lib×××.so）的文件，如果是静态库的话是libpthread.a( lib×××.a)（貌似gcc先找动态库，再找静态库？）。
* -L 指定所需要的库所在的文件夹。系统先寻找标准位置，再寻找指定位置（标准库一般在/lib或/usr/lib）。
* -I 指定头文件的寻找路径。先找标准的，后找指定的（标准的一般在/usr/include）。
* -static 只用静态库,再拿上面那个例子，如果加上-static，系统就会只寻找libpthread.a文件。
* -shared 生成动态库（共享库）文件，形如 libxxx.so （gcc -shared dang.o -o libdang.so）
