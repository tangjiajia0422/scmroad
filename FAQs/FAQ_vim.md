# vim FAQs

https://coolshell.cn/articles/11312.html

### 置顶更新

* 2017-9-4 

**在命令行模式下，可以使用 :15vs或者15vsplit就可以将vi按照屏幕宽度15%-85%的比例分成两份**
**在命令行模式下，可以使用 :15split就可以将vi按照屏幕宽度15%-85%的比例分成两份**

### 浏览目录模式

* 浏览文件
> :E    (在所有的normal模式都可以使用)
>> 在分屏时，如果使用 :wq 这样命令，就会退出当前的屏，使用:E就可以返回当前文件所在的目录继续浏览
* :E下支持的命令
> - 到上一级目录
> D 删除文件
> R 改文件名
> s 对文件排序
> x 执行文件

### 窗口分屏

* 在shell时，vim直接参数即可分屏
> vim -O{n} file1 file2 (大写的O表示垂直分屏, n一般和文件数相同)
> vim -o{n} file1 file2 (消协的o表示水平分屏)
* 把当前窗口上下分屏，并在下面进行目录浏览
> :He 全称是Hexplore (在下边分屏浏览目录)
> :He! (在上边分屏浏览目录)
> :split (命令也可以创建分屏, vsplit 则创建垂直分屏)
* 把当前窗口左右分屏，则可以：
> :Ve 全称是Vexplore (在左边分屏浏览目录，在右边则是:Ve!)
* 分屏见的跳转和切换是：先按 Ctrl+w，然后再按方向键 "h< j\_ k^ l>"
* 关闭分屏
> Ctrl+W c   (关闭当前窗口)
> Ctrl+W q   (关闭当前窗口，如果只剩最后一个，则退出vim)
* 上下分割当前打开的文件
> Ctrl+W s
* 左右分割当前打开的文件
> Ctrl+W v

### Tab页

分屏也可能不爽，更喜欢的是Chrome这样的分页浏览
> :Te 全称是Texplorer  (新建一个tab页)
在多个Tab页中切换，使用如下按键(没有冒号！)
> gt 下一页
> gT 前一页
> {i} gt i是数字，到指定页，比如 5 gt 就是到第5页

在shell使用 vim 的 -p 参数可以以tab页的方式打开多个文件
vim -p a1.cpp a2.cpp a3.cpp

### 常用技巧

* 字符相关
> guu  (把一行文字变成全小写，Vu也可以)
> gUU  (把一行文字变全大写，VU也可以)
> v 进入选择模式，移动光标选择文本，按 u 转成小写，按 U 转成大写
> \* 或者 \# 号在当前文件中搜索当前光标的单词
* 缩进相关
> \>\>向右缩进当前行， << 向左缩进当前行
> = 缩进当前行，对齐缩进
* 复制粘贴相关
> v 进入选择模式，移动光标选择文本，按 y 进行复制，按 p 在当前位置后粘贴，P 在当前位置前粘贴
> 2dd 剪切2行，p 粘贴
> 2yy 复制2行，p 粘贴
* 其他常用
> o 小写O 在当前行后插入一个新行
> O 大写O 在当前行前插入一个新行
> 0 数字零 到行头
> ^ 到本行第一个不是blank的字符(blank 字符就是空格，tab，\n，回车等)
> $ 到行尾
> u 撤销
* 自动补齐
> 在insert模式下，输入一个词的开头，然后按下 Ctrl+p 或者 Ctrl+n 自动补齐功能就出现了


