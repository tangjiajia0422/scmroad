# LINUX NAMESPACE

## 简介
> Linux Namespace是Linux提供的一种内核级别环境隔离的方法。
> chroot(通过修改根目录把用户劫持到一个特定目录下)，chroot提供了一种简单的隔离模式：
>> chroot内部的文件系统无法访问外部的内容。
> Linux Namespace在此基础上，提供了对UTS、IPC、mount、PID、network、User等隔离机制

>> Linux下超级父进程的PID是1,所以和chroot一样，如果我们可以把用户进程空间劫持到某个进程分支下，
>> 并像chroot那样让其下面的进程看到的哪个超级父进程的PID是1,于是就达到资源隔离的效果了。

## Linux Namespace种类
|分类                |系统调用参数      |内核版本        |
| ------------------ |:----------------:| --------------:|
| Mount namespaces   | CLONE_NEWNS      | Linux 2.4.19   |
| UTS namespaces     | CLONE_NEWUTS     | Linux 2.6.19   |
| IPC namespaces     | CLONE_NEWIPC     | Linux 2.6.19   |
| PID namespaces     | CLONE_NEWPID     | Linux 2.6.24   |
| Network namespaces | CLONE_NEWNET     | Linux 2.6.29   |
| User namespaces    | CLONE_NEWUSER    | Linux 3.8      |

涉及三个系统调用:
* clone() --- 实现线程的系统调用，用来创建一个新的进程，并可以通过设计上述参数达到隔离
* unshare() - 使某进程脱离某个namespace
* setns() --- 把某个进程加入到某个namespace

## clone()系统调用
[clone_simple1.c](clone_simple1.c)

## UTS Namespace
UTS用来设置子进程的hostname

[uts_namespace.c](uts_namespace.c)

```bash
tangjiajia@localhost:$ sudo ./uts_namespace 
root@container:# uname -n
```

## IPC Namespace
[ipc_namespace.c](ipc_namespace.c)

> IPC(inter-process communication)是Linux下进程通信的一种方式。一般有共享内存、信号量、消息队列等方法。
所以为了隔离，也需要把IPC隔离出来，这样，只有在同一个namespace下的进程才能互相通信。
熟悉IPC原理的就知道，IPC需要一个全局的ID，因此我们的namespace就需要对这个ID隔离，不能让别的namespace的进程看到。

1. 创建一个IPC的Queue(全局的Queue ID是0)
```bash
tangjiajia@localhost:$ ipcmk -Q
  消息队列 id：0
tangjiajia@localhost:$ ipcs -q
  --------- 消息队列 -----------
  键        msqid      拥有者  权限     已用字节数 消息      
  0x9e105c59 0          tangjiajia 644        0            0
```
2. 当我们运行加上了CLONE_NEWIPC的程序后，就会有如下的结果
```bash
tangjiajia@localhost:$ sudo ./ipc_namespace 
  [sudo] tangjiajia 的密码： 
  Parent - start a container!
  Container - inside the container!
root@container:# ipcs -q
  --------- 消息队列 -----------
  键        msqid      拥有者  权限     已用字节数 消息      

```
3. 可以看到在2中是空的，看不到这个全局的IPC消息队列

## PID Namespace
[pid_namespace.c](pid_namespace.c)

> PID为1有什么用？
在Linux中，PID为1的进程是init，地位及其特殊。作为所有进程的父进程，有很多的特权(比如屏蔽信号啥的)。
init进程还会检查所有进程状态: 比如某个子进程脱离了父进程(父进程没有wait它)，那么init进程就会负责回收资源并结束这个子进程。
因此要做到进程空间隔离，首先要创建PID为1的进程，最好像chroot那样，把子进程的PID在容器内变成1.

> 为啥在这个容器内使用ps,top等命令，还是看到所有进程呢？
这说明还是没有__完全隔离啊!__。因为ps和top这样的命令是去度/proc下的文件系统。而此时父进程和clone出来的子进程在访问/proc是一样的。
所以隔离还需要对文件系统进行隔离

## Mount Namespace

