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
> [clone_simple1.c](clone_simple1.c)

