# bash FAQ和坑

1. **坑!** 看如下代码
```bash
#!/bin/bash
funca(){
  for (( i=0; i<2; i++ ))
  do
    echo $i
  done
}

funcb(){
  for (( i=10; i<12; i++ ))
  do
    funca
  done
}

funcb
```
哈哈哈，屏幕在一直打印0 1 0 1，试试把funcb中的i换成j试试!!
(个人理解是因为bash中的方法是没有栈的概念，所以i变量并不会因为在funca中的循环弹栈，而是在这个bash中i是一个全局变量)

2. 从一个字符串中删除匹配的子串
```bash
$ before="abcdefghij defaf"
$ filter_out_str="def"
$ result=${before//"${filter_out_str}"/}
$ echo ${result}
```
