# Python FAQ

1. 判断对象是否是一个file对象
```python
f = open('a.txt', 'r')
if isinstance(f, file):
    print 'is a file'
```

2. 把管道结果作为python的输入
```python
$ cat python_iterate_stdin.py
import sys

for line in sys.stdin:
    sys.stdout.write(line)

$ echo -e "first line\nsecond line" | python python_iterate_stdin.py
//注意: 这里用管道执行python脚本，不能带参数，并且文件内不能定义函数然后再调用函数
//不能有argparse，也不能 __name__ == '__main__': main() 这样。只能当成纯脚本执行
```

3. list和string互换
```python
''.join(listA)  #list转string
list(stringA)   #string转list
```
