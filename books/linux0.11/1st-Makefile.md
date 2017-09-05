###### <span id="top">top</span>
# Linux内核体系结构</span>

1. [操作系统组成](#os-components)
2. [Linux内核模式](#kernel-mode)
3. [Linux内核系统体系结构](#kernel-structure)
4. [Linux内核源码目录结构](#kernel-src-structure)
 - [引导启动程序boot](#src-boot)
 - [文件系统fs](#src-fs)
 - [头文件include](#src-include)
 - [内核初始化程序init](#src-init)
 - [内核程序主目录](#src-kernel)
  - [块设备驱动程序kernel/blk_dev](#src-kernel-blkdev)
  - [字符设备驱动程序kernel/chr_dev](#src-kernel-chrdev)
  - [数学仿真操作kernel/math](#src-kernel-math)
5. [内核库函数lib](#src-lib)
6. [内存管理mm](#src-mm)
7. [内核编译工具tools](#src-tools)
8. [Makefile整体编译结构](#makefile-structure)
 - [Makefile注解](#makefile-comments)
9. [as86,ld86](#asld86)
10. [System.map](#systemmap)
11. [总结](#summarize)


###### <span id="os-components">os-components</span>

## 操作系统组成

* 用户应用程序: 字处理、浏览器或者用户自编程的各种应用程序
* 操作系统服务: 向用户所提供的服务被看作是操作系统的部分功能的程序，如shell命令解释等
* 操作系统内核: 对硬件资源的抽象和访问调度
* 硬件系统

**Linux kernel 主要用途就是为了与硬件进行交互，实现对硬件部件的编程控制和接口操作，调度对硬件资源的访问，并为计算机上的用户程序提供一个高级的执行环境和对硬件的虚拟接口**

[->TOP](#top)

###### <span id="kernel-mode">kernel-mode</span>
## Linux内核模式

* 整体式的单内核模式
* 层次式的微内核模式

Linux0.11内核是单内核模式，其有点是代码结构紧凑、执行速度快，不足主要是层次结构不强
> 在单内核模式系统中，操作系统所提供的服务流程：应用主程序使用指定的参数执行系统调用指令，使CPU从用户态切换到内核态，然后操作系统更具具体的参数调用特定的系统调用程序。在完成应用程序所要求的服务后，操作系统从内核态又切换回用户态，返回到应用程序中继续执行后面的指令

**单内核可以粗略的分为三个层次**
* 调用服务的主程序;
* 执行系统调用的服务层;
* 系统调用的底层函数.

[->TOP](#top)

###### <span id="kernel-structure">kernel-structure</span>
## Linux内核系统体系结构

* 进程调度
 - 控制进程对CPU资源的使用
* 内存管理 
 - 确保所有进程可以安全地共享机器主存区
 - 支持虚拟内存管理，使得Linux支持进程使用比实际内存空间更多;
 - 利用文件系统把暂时不用的内存数据块交换到外部存储设备中，需要时再换回来
* 文件系统
 - 支持对外部设备的驱动和存储
 - 虚拟文件系统通过向所有的外部存储设备提供一个通用的文件接口，隐藏了各种硬件设备的不同细节，从而提供并支持多种文件系统格式
* 进程间通信
 - 多进程间的信息交换
* 网络接口
 - 提供对多种网络通信标准的访问并支持多中网络硬件

**所有模块都与进程调度有依赖关系，因为他们都需要依靠进程调度程序来挂起或者重新运行他们的进程**

除了依赖关系外，所有模块都依赖于内核通用资源：包括所有子系统都会调用的内存分配和回收函数、打印信息或出错函数，以及一些系统调试函数等

[->TOP](#top)

###### <span id="kernel-src-structure">kernel-src-structure</span>
## Linux内核源码目录结构

单内核模式，各程序紧密联系，依赖和调用关系也非常密切

目录结构：
* boot        系统引导汇编程序
* fs          文件系统
* include     头文件(\*.h)
 - asm        与CPU体系结构相关的部分
 - linux      Linux内核专用部分
 - sys        系统数据结构部分
* init        内核初始化程序
* kernel      内核进程调度、信号处理、系统调用等程序
 - blk_drv    块设备驱动程序
 - chr_drv    字符设备驱动程序
 - math       数学协处理器仿真处理程序
* lib         内核库函数
* mm          内存管理程序
* tools       生成内核Image文件的工具程序
* Makefile    嵌套调用子目录makefile

[->TOP](#top)

###### <span id='src-boot'>src-boot</span>
### 引导启动程序boot

boot目录包含3个汇编文件，是内核中最先被编译的程序

主要功能：
* 计算机加电时引导内核启动
* 将内核代码加载到内存中
* 做一些进入32位保护模式前的系统初始化工作

文件：
* bootsect.s 
> 磁盘引导块程序，编译后会驻留在磁盘的第一个扇区(引导扇区，0磁道，0磁头，第一扇区)。在PC加电ROM BIOS自检后，将被BIOS加载到内存0x7C00处进行执行
* setup.s
> 用于读取机器的硬件配置参数，并把内核模块system移动到适当的内存位置处
* head.s
> 会被编译链接在system模块的最前部分，主要进行硬件设备的探测设置和内存管理页面的初始设置工作

[->TOP](#top)

###### <span id='src-fs'>src-fs</span>
### 文件系统fs

fs是文件系统实现程序的目录，包含17各C程序
* file_table.c   仅定义了一个文件句柄(描述符)结构数组
* ioctl.c        引用kernel/chr_dev/tty.c中函数，实现字符设备的io控制功能
* exec.c         主要包含一个执行程序函数do_execve()，他是所有exec函数簇中的主要函数
* fcntl.c        用于实现文件IO控制的系统调用函数
* read_write.c   用于实现文件读/写和定位三个系统调用函数
* stat.c         实现了两个获取文件状态的系统调用函数
* open.c         实现修改文件属性和创建与关闭文件的系统调用函数
* char_dev.c     包含字符设备读写函数rw_char()
* pipe.c         包含管道读写函数和创建管道的系统调用
* file_dev.c     包含基于i节点和描述符结构的文件读写函数
* namei.c        包括文件系统中目录名和文件名的操作函数和系统调用
* block_dev.c    包含块数据读写函数
* inode.c        包含针对文件系统i节点操作的函数
* truncate.c     程序用于在删除文件时释放文件所占用的设备数据空间
* bitmap.c       用于处理文件系统中i节点和逻辑数据块的位图
* super.c        包含对文件系统超级块的处理函数
* buffer.c       用于对内存高速缓冲区进行处理
>> ll_rw_block   是块设备的底层读函数，它不再fs目录中，而是kernel/blk_dev/ll_rw_block.c中块设备读写驱动函数
**文件系统对于块设备中数据读写，都需要通过高速缓冲区与块设备的驱动程序(ll_rw_block)来操作，文件系统程序集本身并不直接与块设备的驱动程序打交道**

<pre>
   .------------.   .-------.        .-------.        .-------.
   | file_table |   | ioctl |        | exec  |\       | fcntl |
   '------------'   '-------'        '-|-----' \      '-------'
           .------------.              |        \         |
          /| read_write |\             |         \        |
         / '------------' \            |          \    .--v---.
        /      |   |       \           | .------.  \   | open |
       /       |   |        \          | | stat |\  \  '------'
   .--v-------.| .-v----. .--v-------. | '------' \  \    |
   | char_dev || | pipe | | file_dev | |    /      \ .v---v--.
   '----------'| '------' '----------'.--------------| namei |--->|
               |               |    | ||  /          '-------'    |
          .----v------.        |    v vv v               |        |
          | block_dev |        |  .-------.        .-----v----.   |
          '-----------'        |  | inode |------->| truncate |   |
                \              |  '-------'        '----------'   |
                 \             |   |   \            |/            |
                  \            |   |    \           |             |
                   \           |   |     \         /|             |
                    \          |   |      \       / |             |
                     \         |   |       \     /  |             |
                      \        |   |     .--v---v-. |             |
                       \       |   |     | bitmap | |             |
                        \      |   |     '--------' |             |
                         \     |   |             \  |             |
                          \    |   | .------------\-v             |
                           \   |   | |             \              |
                            v  v   v v              \             |
                           .--------.              .-v-----.      |
                           | buffer |              | super |<-----'
                           '--------'              '-------'
                               |
                         .-----v-------.
                         | ll_rw_block |
                         '-------------'
</pre>

[->TOP](#top)

###### <span id="src-include">src-include</span>
### 头文件主目录include

一共32个头文件，其中主目录下有13个，asm下有4个，linux下有10个，sys有5个
* a.out.h        a.out头文件，定义了a.out执行文件格式和一些宏
* const.h        常数符号头文件，目前仅定义了i节点中i_mode字段的各标志位
* ctype.h        字符类型头文件。定义了一些有关字符类型判断和转换的宏
* errno.h        错误号头文件。包括系统中各种出错号
* fcntl.h        文件控制头文件。用于文件及描述符的操作控制常数符号的定义
* signal.h       信号头文件。定义信号符号常量，信号结构及信号操作函数原型
* stdarg.h       标准参数头文件。以宏的形式定义变量参数列表。主要说明了一个类型 (va_list)和三个宏(va_start,va_arg和va_end)，用于vsprintf、vprintf、vfprintf函数
* stddef.h       标准定义头文件。定义了NULL，offsetof(TYPE, MEMBER)
* string.h       字符串头文件。主要定义了一些有关字符串操作的嵌入函数
* termios.h      终端输入输出的函数头文件。主要定义控制异步通信接口的终端接口
* time.h         时间类型头文件。其中最主要定义了tm结构和一些有关时间的函数原型
* unistd.h       Linux标准头文件。定义了各种符号常数和类型，并声明了各种函数。如定义了\_\_LIBARAY\_\_，还包括系统调用号和内嵌汇编\_syscall0()等
* utime.h        用户时间头文件。定义了访问和修改时间结构及utime()原型

include/asm下主要定义了一些与CPU体系相关的数据结构、宏等
* asm/io.h       io头文件。以宏的嵌入汇编程序形式定义对io端口操作的函数
* asm/memory.h   内存拷贝头文件。含有memcpy()嵌入式汇编宏函数
* asm/segment.h  段操作头文件。定义了有关段寄存器操作的嵌入式汇编函数
* asm/system.h   系统头文件。定义了设置或修改描述符/中断门等的嵌入式汇编宏

include/linux内核专用头文件

* linux/config.h 内核配置头文件。定义键盘语言和硬盘类型(HD_TYPE)可选项
* linux/fdreg.h  软驱头文件。含有软盘控制器参数的一些定义
* linux/fs.h     文件系统头文件。定义文件表结构(file, buffer_head, m_inode等)
* linux/hdreg.h  硬盘参数头文件。定义访问磁盘寄存器端口，状态码，分区表等信息
* linux/head.h   head头文件，定义了段描述符的简单结构和几个选择符常量
* linux/kernel.h 内核头文件。包含一些内核常用函数的原型定义。
* linux/mm.h     内存管理头文件。包含页面大小定义和一些页面释放函数原型
* linux/sched.h  调度程序头文件。定义了结构体task_struct、初始任务0的数据。
* linux/sys.h    系统调用头文件。包含72个系统调用C函数处理程序，以sys\_开头
* linux/tty.h    tty头文件，定义了有关tty_io，串行通信方面的参数、常数

include/sys系统专用数据结构

* sys/stat.h     文件状态头文件。包含文件或文件系统状态结构stat()和常量
* sys/times.h    定义了进程中运行时间结构tms以及times()函数原型
* sys/types.h    类型头文件。定义了基本的系统数据类型
* sys/utsname.h  系统名称结构头文件
* sys/wait.h     等待调用头文件。定义系统调用wait()和waitpid()及相关常数符号

[->TOP](#top)

###### <span id="src-init">src-init<span>
### 内核初始化程序目录init

只有一个main.c。用于执行内核所有的初始化工作，然后移到用户模式创建新进程，并在控制台设备上运行shell程序
> 1. 根据内存大小对缓冲区内存容量进行分配，如果还设置了要使用虚拟盘，则在缓冲区内存后面也为它留下空间
> 2. 所有硬件初始化工作，包括人工创建的第一个任务(task 0)，并设置了中断允许标志
> 3. 在执行从内核态移到用户态后，系统第一次调用创建进程函数fork()，创建出一个用于运行init()的进程，在该子进程中，系统将设置控制台环境，并且再生成一个子进程用来运行shell程序

[->TOP](#top)

###### <span id="src-kernel">src-kernel</span>
### 内核程序主目录kernel

linux/kernel目录中共包含12个代码和一个Makefile，调用关系复杂，因此就对大致功能进行分类

通用程序                  | 硬件中断程序 |  系统调用程序                | |调
schedule.c      |         | asm.s        |  system_call.s               | |用
panic.c         | mktime  |              |                              | |关
printk,vsprintf |         | traps.c      |  fork.c,sys.c,exit.c,signal.c| v系

* asm.s     用于处理系统硬件异常所引起的中断，对各硬件异常的实际处理程序则是在traps.c文件中，在各个中断处理过程中，将分别调用traps.c中相应的C函数
* exit.c    主要包括用于处理进程终止的系统调用。包括进程释放、会话终止和程序退出处理函数以及杀死进程、终止进程、挂起进程等系统调用函数
* fork.c    提供了sys_fork()系统调用中使用的find_empty_process()和copy_process()两个函数
* mktime.c  包含一个内核使用的时间函数mktime()，用于计算从1970/1/1起到开机当日的秒数，仅在init/main.c中被调用一次
* panic.c   包含一个显示内核出错信息显示函数printk()
* printk.c  包含内核专用信息显示函数printk()
* sched.c   包括有关调度的基本函数(sleep_on, wakeup, schedule等)以及一些简单的系统调用函数。
* signal.c  包括了有关信号处理的4个系统调用以及一个在对应的中断处理程序中处理信号的函数do_signal()
* sys.c     包括很多系统调用函数，其中还有不少没实现呢
* system_call.s  实现了linux系统调用(int 0x80)的接口处理过程，实际的处理过程则包含在各系统调用相应的C语言处理函数中，这些处理函数分布在整个linux内核代码中
* vsprintf.c  实现了现在已经归入标准库函数中的字符串格式化函数

[->TOP](#top)

###### <span id="src-kernel-blkdev">src-kernel-blkdev</span>
#### 块设备驱动程序子目录kernel/blk_dev

包含4个C和一个h文件，blk.h是为块设备程序专门使用的，所以与C文件放在一起

<pre>
  .-------.   .-------------.
  | blk.h |   | ll_rw_blk.c |
  '-------'   '-------------'
                  /   |
                 /    |
           .----v-. .-v--------.
           | hd.c | | floppy.c |
           '------' '----------'
</pre>

* blk.h    定义了3个C程序中共用的块设备结构和数据块请求结构
* hd.c     主要实现对硬盘数据块进行读写的底层驱动函数，主要是do_hd_request()
* floppy.c 主要实现了对软盘数据块的读写驱动函数，主要是do_fd_request()
* ll_rw_blk.c  实现了底层块设备数据读写函数ll_rw_block()，内核中所有其他程序都是通过调用该函数对块设备进行数据读写操作。该函数在 许多访问块设备数据的地方被调用，尤其是在高速缓冲区处理文件fs/buffer.c中

[->TOP](#top)

###### <span id="src-kernel-chrdev">src-kernel-chrdev</span>
#### 字符设备驱动程序子目录kernel/chr_dev

包含4个C和2各汇编文件。这些文件实现了对串口rs-232, tty, 键盘,和终端控制台设备的驱动

<pre>
                   .----------.   .-------------.
                  /| tty_io.c |\  | tty_ioctl.c |
                 / '----------' \ '-------------'
                /    |     |     \
               /     |     |      \
              /      |     |       \
             /       |     |        \
            /        |     |         \
 .---------v..-------v-..--v--------..v-----------.
 | serial.c || rs_io.s || console.c || keyboard.S |
 '----------''---------''-----------''------------'
</pre>

* tty_io.c    包含对tty字符设备读函数tty_read()和写函数tty_write()，另外还包括在串行中断处理过程中调用的C函数do_tty_interrupt()，该函数会在中断类型为读字符的处理中被调用
* console.c   主要包括控制台初始化程序和控制台写函数con_write()，用于被tty设备调用，还包括对显示器和键盘中断的初始化设置程序con_init()
* rs_io.s     用于实现两个串行接口的中断处理程序。该中断处理程序会根据从中断标识寄存器(端口0x3fa或者0x2fa)中取的的4种中断类型分别进行处理，并在处理中断类型为读字符的代码中调用do_tty_interrupt()
* serial.c    用于对异步串行通信芯片UART进行初始化操作，并设置两个通信端口的中断向量。另外还包括tty用于向串口输出的rs_write()函数
* tty_ioctl.c 实现了tty的io控制接口函数tty_ioctl()以及对termio(s)终端io结构的读写函数，并会在实现系统调用sys_ioctl()的fs/ioctl.c程序中被调用
* keyboard.S  主要实现了键盘中断处理过程keyboard_interrupt

[->TOP](#top)

###### <span id="src-kernel-math">src-kernel-math</span>
#### 数学协处理器仿真和操作程序子目录kernel/math

只有一个C程序math_emulate.c。其中math_emulate()函数是中断int7的中断处理程序调用C函数。当机器中没有数学协处理器，而CPU又执行了协处理器的指令时，就会引发该中断。因此该中断就是用软件来仿真协处理器功能

[->TOP](#top)

###### <span id="src-lib">src-lib</span>
## 内核库函数lib

内核库函数主要用于用户编程调用，是编译系统标准库的接口函数之一。共12个C文件。除了malloc.c较长外，其他程序都很短。
* exit()     退出函数
* close(fd)  关闭文件函数
* dup()      复制文件描述符
* open()     文件打开
* write()    写文件函数
* execve()   执行程序函数
* malloc()   内存分配韩式
* wait()     等待子进程状态函数
* sedid()    创建会话系统
* include/string.h  字符串操作函数

[->TOP](#top)

###### <span id="src-mm">src-mm</span>
## 内存管理mm

* page.s   包括内存页面异常中断(int14)处理程序，主要用于处理程序由于缺页而引起的页异常中断和访问非法地址而引起的页保护机制
* memory.c 包括对内存进行初始化的函数mem_int()，由page.s的内存处理中断过程调用的do_no_page()和do_wp_page()函数。在创建新进程而执行复制进程操作时，即是哟呢该文件中的内存处理函数来分配管理内存空间

[->TOP](#top)

###### <span id="src-tools">src-tools</span>
## 编译内核工具tools

build.c程序用于将Linux各个目录中被分别编译生成的目标代码连接合并称一个可运行的内核映象文件image

[->TOP](#top)

###### <span id="makefile-structure">makefile-structure</span>
## Makefile整体编译结构

<pre>
                   .------..----..----..--------.
                   | head || fs || mm || kernel |
                   '----\-''-|--''|---'/--------'
                         \   |    |   / | main |
                          \  |    |  /  '------'
.----------.   .-------.  .v-v----v./    .-----.
| bootsect |   | setup |  | system <-----| lib |
'--------\-'   '--|----'  '/-------'     '-----'
          \       |       /
           \      |      /
           .v-----v-----v-.
           | kernel Image |
           '--------------'
         kernel build structure
</pre>

[->TOP](#top)

###### <span id="makefile-comments">makefile-comments</span>
### Makefile注解

<pre>
#
# if you want the ram-disk device, define this to be the
# size in blocks.
# 如果要使用RAM盘设备的话，就定义块的大小
RAMDISK = #-DRAMDISK=512

# 8086汇编编译器和连接器
# -0生成8086目标程序;-a生成与gas和gld部分兼容的代码
AS86	=as86 -0 -a
LD86	=ld86 -0 

# 这是GNU的汇编和连接器
AS	=gas
LD	=gld

# gld用到的选项
# -s输出文件中省略所有的符号信息
# -x删除所有局部符号
# -M需要在标准输出设备(显示器)上打印链接映象
LDFLAGS	=-s -x -M

# gcc是GNU C的程序编译器
CC	=gcc $(RAMDISK)

# gcc选项 -Wall打印所有警告信息; -O对代码进行优化;
# -fstrength-reduce优化所有警告信息; -smstring-insns是Linus自己写的选项(可选)
CFLAGS	=-Wall -O -fstrength-reduce -fomit-frame-pointer \
-fcombine-regs -mstring-insns

# cpp是gcc的预处理程序
# -nostdinc -Iinclude表示不要搜索标准的头文件目录，而使用-I指定的目录或是当前目录下搜索头文件
CPP	=cpp -nostdinc -Iinclude

#
# ROOT_DEV specifies the default root-device when making the image.
# This can be either FLOPPY, /dev/xxxx or empty, in which case the
# default of /dev/hd6 is used by 'build'.
# ROOT_DEV是在创建内核映像image文件时所使用的默认根文件系统所在的设备。如果不定义在build程序(tools)下就默认使用/dev/hd6
ROOT_DEV=/dev/hd6

# kernel、mm、fs目录所产生的目标代码文件
ARCHIVES=kernel/kernel.o mm/mm.o fs/fs.o

# 块和字符设备库文件。.a是静态库，包含多个可执行二进制代码子程序集合
DRIVERS =kernel/blk_drv/blk_drv.a kernel/chr_drv/chr_drv.a

# 数学运算库文件
MATH	=kernel/math/math.a

# 由libs目录中文件所编译生成的通用库文件
LIBS	=lib/lib.a

# make老式的隐藏后缀规则。(现在这种规则已经不用了，而是用更清晰的匹配规则)。如下是一种双后缀规则--用一对后缀定义的:源后缀和目标后缀
# 利用如下命令将所有.c文件编译成.s文件
# -nostdinc -Iinclude和上面一样，表示不使用标准头文件目录，而使用-I指定的
# -S表示把.c编译成.s后就停止，不继续进行汇编了
# -o表示其输出文件的形式
.c.s:
	$(CC) $(CFLAGS) \
	-nostdinc -Iinclude -S -o $*.s $<

# 使用gas将所有.s编译成.o目标文件，-c表示只编译或汇编，但不进行链接操作
.s.o:
	$(AS) -c -o $*.o $<

# 使用gcc将C文件编译成目标文件但不链接
.c.o:
	$(CC) $(CFLAGS) \
	-nostdinc -Iinclude -c -o $*.o $<

# all表示Makefile所知的顶层目标，image文件
all:	Image

# Image依赖这4各文件，然后执行命令--用tools/build命令将bootsect、setup、system文件以ROOT_DEV为根文件系统设备组装称内核文件Image
# sync命令是迫使缓冲块数据立即写盘并更新超级块
Image: boot/bootsect boot/setup tools/system tools/build
	tools/build boot/bootsect boot/setup tools/system $(ROOT_DEV) > Image
	sync

# disk目标依赖Image
# dd是Unix标准命令：复制一个文件，并根据选项进行转换和格式化
# bs=一次读写的字节数; if=输入的文件; of=输出的文件，这里的/dev/PS0指第一个软盘驱动器
disk: Image
	dd bs=8192 if=Image of=/dev/PS0

# 生成tools/build可执行文件
tools/build: tools/build.c
	$(CC) $(CFLAGS) \
	-o tools/build tools/build.c

# 利用上面给的.s.o规则生成head.o目标文件
boot/head.o: boot/head.s

# tools/system的依赖
# 生成system命令，并且gld把链接映像重定向放在System.map文件中
tools/system:	boot/head.o init/main.o \
		$(ARCHIVES) $(DRIVERS) $(MATH) $(LIBS)
	$(LD) $(LDFLAGS) boot/head.o init/main.o \
	$(ARCHIVES) \
	$(DRIVERS) \
	$(MATH) \
	$(LIBS) \
	-o tools/system > System.map

# 数学协处理函数
kernel/math/math.a:
	(cd kernel/math; make)

# 块设备函数blk_drv.a
kernel/blk_drv/blk_drv.a:
	(cd kernel/blk_drv; make)

# 字符设备函数chr_drv.a
kernel/chr_drv/chr_drv.a:
	(cd kernel/chr_drv; make)

# 内核目标kernel.o
kernel/kernel.o:
	(cd kernel; make)

# 内存管理模块mm.o
mm/mm.o:
	(cd mm; make)

# 文件系统模块fs.o
fs/fs.o:
	(cd fs; make)

# 库函数lib.a
lib/lib.a:
	(cd lib; make)

# 使用8086汇编和链接器对setup.s文件进行编译生成setup文件
# -s表示要去除目标文件中的符号信息
boot/setup: boot/setup.s
	$(AS86) -o boot/setup.o boot/setup.s
	$(LD86) -s -o boot/setup boot/setup.o

# 同样使用8086汇编和连接器生成bootsect.o磁盘引导块
boot/bootsect:	boot/bootsect.s
	$(AS86) -o boot/bootsect.o boot/bootsect.s
	$(LD86) -s -o boot/bootsect boot/bootsect.o

# 在bootsect.s程序开头添加一行有关system文件长度信息
# (实际长度 + 15) / 16 用于获得用'节'表示的长度信息。1节 = 16字节
tmp.s:	boot/bootsect.s tools/system
	(echo -n "SYSSIZE = (";ls -l tools/system | grep system \
		| cut -c25-31 | tr '\012' ' '; echo "+ 15 ) / 16") > tmp.s
	cat boot/bootsect.s >> tmp.s

# 清除编译结果
clean:
	rm -f Image System.map tmp_make core boot/bootsect boot/setup
	rm -f init/*.o tools/system tools/build boot/*.o
	(cd mm;make clean)
	(cd fs;make clean)
	(cd kernel;make clean)
	(cd lib;make clean)

# 先执行clean规则，然后对liunx进行打包压缩。sync迫使缓冲数据立即写盘并更新磁盘超级块
backup: clean
	(cd .. ; tar cf - linux | compress - > backup.Z)
	sync

dep:
	sed '/\#\#\# Dependencies/q' < Makefile > tmp_make
	(for i in init/*.c;do echo -n "init/";$(CPP) -M $$i;done) >> tmp_make
	cp tmp_make Makefile
	(cd fs; make dep)
	(cd kernel; make dep)
	(cd mm; make dep)

### Dependencies:
init/main.o : init/main.c include/unistd.h include/sys/stat.h \
  include/sys/types.h include/sys/times.h include/sys/utsname.h \
  include/utime.h include/time.h include/linux/tty.h include/termios.h \
  include/linux/sched.h include/linux/head.h include/linux/fs.h \
  include/linux/mm.h include/signal.h include/asm/system.h include/asm/io.h \
  include/stddef.h include/stdarg.h include/fcntl.h 

</pre>

[->TOP](#top)

###### <span id="asld86">asld86</span>
## as86, ld86简介

as86和ld86是Intel8086的汇编和链接程序，它完全是一个8086的汇编编译器，却可以为386处理器编制32位的代码。Linux使用它仅仅是为了创建16位的启动扇区bootsector代码和setup二进制执行代码。该编译器的语法和GUN的汇编编译器语法是不兼容的

[->TOP](#top)

###### <span id="systemmap">systemmap</span>
## System.map文件

System.map文件用于存放内核符号表信息。符号表是所有符号及其对应地址的一个列表。每次编译产生的System.map都是全新的。当内核运行出错时，就可以通过System.map文件中的符号表解析，就可以查到一个地址值对应的变量名，反之亦可。

符号表样例：

<pre>
c03441a0 B dmi_broken
c03441a4 B is_sony_vaio_laptop
c03441c0 b dmi_ident
c0344200 b pci_bios_present
c0344204 b pirq_table
</pre>

可以看到名为dmi_broken的变量位于内核地址c03441a0处

System.map位于使用它的软件(内核日志记录后台程序klogd)能够寻找的地方。在系统启动时，如果没有以一个参数形式为klogd给出System.map的位置，则klogd将会在三个地方搜寻System.map
* /boot/System.map
* /System.map
* /usr/src/linux/System.map

尽管内核本身实际上不使用Syetem.map，但其他程序，象klogd，lsof，ps，dosemu都需要一个正确的Syetem.map文件。利用该文件，这些程序可以根据已知的内存地址查找出对应的内核变量名，便于对内核的调试工作。

[->TOP](#top)

###### <span id="summarize">summarize</span>
## 本章总结

主要讲述了早期linux操作系统的内核模式和体系结构，并对编译文件makefile做了注释

[->TOP](#top)
