# AUFS

AUFS是一种Union FileSystem，所谓的UnionFS就是把不同物理位置的目录合并mount到同一个目录中。
AUFS(Advance UnionFS)，其实到现在还没有进Linux主干，可能是Linus就是不喜欢AUFS吧～～

## AUFS感性认识

1. 我们创建了两个目录fruits,vegetables，还分别建了两个文件
```bash
$ tree
.
├── fruits
│   ├── apple
│   └── tomato
└── vegetables
    ├── carrots
    └── tomato
```
2. 执行以下操作
```bash
# 创建一个mnt目录
$ mkdir mnt

# 把睡过目录和蔬菜目录union mount到./mnt目录中
$ sudo mount -t aufs -o dirs=./fruits:./vegetables none ./mnt

# 查看./mnt目录
$ tree ./mnt
./mnt
├── apple
├── carrots
└── tomato
```
./mnt目录下有三个文件：apple，carrots，tomato。水果和蔬菜的目录被union到了./mnt目录下了。

修改其中的文件内容
```bash
$ echo mnt > ./mnt/apple
$ cat ./mnt/apple
mnt
$ cat ./fruits/apple
mnt
```
可见：我们修改./mnt/apple后，./fruits/apple的内容也被修改了
```bash
$ echo mnt_carrots > ./mnt/carrots
$ cat ./vegetables/carrots

$ cat ./fruits/carrots
mnt_carrots
```
可见：我们修改了./mnt/carrots的内容，./vegetables/carrots并没有变化，而./fruits/carrots的目录下出现了carrots文件，其内容是我们在./mnt/carrots里的内容。

在mount aufs命令中，在没有指定 vegetables和fruits目录权限的情况下，默认命令行第一个(最左边)的目录是可读可写的，后面的全部是只读。

所以如下命令是指定权限的方式：
```bash
$ sudo mount -t aufs -o dirs=./fruits=rw:./vegetables=rw none ./mnt
````
都设置了读写权限，那么修改./mnt/tomato这个文件究竟哪个文件会被修改呢？
```bash
$ echo "mnt_tomato" > ./mnt/tomato
$ cat ./fruits/tomato
mnt_tomato
$ cat ./vegetables/tomato
I am a vegetable
```
可见：如果文件名重复，在mount命令行中，越往前优先级就越高

## AUFS想象力

直接把CD/DVD上的image运行在一个可写的存储设备上(U盘)--把CD/DVD文件系统和USB这个可写的系统联合mount起来，这样，对于DVD上的任何修改都会被应用在U盘上，而不会损坏DVD上的原始数据;
再发挥下想象力，也可以把一个目录，比如源代码，作为一个只读的模板，和另一个工作区联合mount在一起，这样做的任何修改都不会破坏源代码

是不是可以想象Docker可以利用UnionFS来做出分层的镜像了？

## 运行docker后

在Docker执行起来后(docker run -it ubuntu /bin/bash)，可以从/sys/fs/aufs/si\_**id**目录下查看aufso 的mount情况
只有顶层(branch)是rw权限，其他都是ro+wh权限只读

## AUFS的特性

AUFS有所有UnionFS的特性，把多个目录合并成同一个目录，并可以为每个需要合并的目录制定相应的权限，实时添加、删除、修改已经被mount的目录。而且还可以在多个可写的branch/dir之间进行负载均衡。

其实上面的例子，已经展示了AUFS的mount，下面我们再来关心下被union的目录(分支)的相关权限：
* rw表示可写可读read-write
* ro表示read-only，如果不指定权限，那么除了第一个外ro是默认值，对于ro分支，其永远不回收到写操作，也不会收到查找whiteout的操作
* rr表示real-read-only，与readonly不同，rr标记的是天生就是只读的分支，这样，AUFS可以提高性能，比如不再设置inotify来检查文件变动通知。
> **什么是whiteout?**
> 一般来说ro的分支都会有wh的属性，比如"[dir]=ro+wh"。所谓的whiteout的意思，如果在union中删除某个文件，实际上是位于一个readonly的分支(目录)上，那么在mount的union这个目录中将看不到这个文件，但是readonly这个层上我们无法做任何修改，所以我们就需要对这个readonly的目录里文件做whiteout。AUFS的whiteout的实现是通过在上层的可写的目录下建立对应的whiteout隐藏文件来实现的
示例：
```bash
$ tree
.
├── fruits
│   ├── apple
│   └── tomato
├── test
└── vegetables
    ├── carrots
    └── tomato
$ mount -t aufs -o dirs=./test=rw:./fruits=ro:./vegetables=ro none ./mnt1
$ ls ./mnt1
# 在权限为rw的test目录下新建一个whiteout的隐藏文件.wh.apple就会发现./mnt1/apple这个文件消失了
$ touch ./test/.wh.apple //这个操作和rm ./mnt1/apple是一样的
$ ls ./mnt1
carrots  tomato
```

## 术语

**Branch** - 就是各个要被union起来的目录(就是上面使用的dirs的命令行参数)
* Branch根据被union的顺序形成一个stack，一版来说最上面是可写的，下面都是只读的
* Branch的stack可以在被mount后进行修改，比如修改吮吸，加入新的branch，或者删除其中的branch，亦或者直接修改branch的权限

**Whiteout** 和 **Opaque**
* 如果UnionFS中的某个目录被删除了，那么就应该不可见了，就算是在底层的branch中还有这个目录，那也应该不可见了。
* Whiteout就是某个上层目录覆盖了下层的相同名字的目录。用于隐藏低层分支的文件，也用于阻止readdir进入低层分支。
* Opaque的意思就是不允许任何下层的某个目录显示出来 
* 在隐藏低层档的情况下，whiteout的名字是'.wh.<filename>'
* 在阻止readdir情况下，名字是'.wh..wh..opq'或者'.wh.__dir_opaque'

