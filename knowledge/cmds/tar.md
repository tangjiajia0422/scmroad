# 压缩解压 tar

tar 这个命令的参数之多，让我很绝望，于是我发明了一个简单的记忆方法。
使用 tar 命令只要记得参数是『必选+自选+f』即可，我们先来看看『必选！五选一』:
```bash
-c 意为 create，表示创建压缩包
-x 意为 extract，表示解压
-t 表示查看内容
-r 给压缩包追加文件
-u 意为 update，更新压缩包中的文件
```
注意了，上面是**一定要五选一的，不能一个都不选，也不能同时选俩**。但是自选的部分就可以按照需要挑选了，比如：
```bash
-z 使用 gzip 属性
-j 使用 bz2 属性
-Z 使用 compress 属性
-v 意为 verbose，显示详细的操作过程
-O 将文件输出到标准输出
```
然后最后一个一定要是 f 后面跟压缩包名（无论是要解压还是要压缩，都是指压缩包的名字）。接下来我们看看具体实例，就很容易理解具体的用法了。

1. 假设我们有很多 .md 文件需要打包，那么可以使用
```bash
tar -cf posts.tar *.md        //c 是创建压缩包，也就是压缩，然后是 f，给出压缩包名，最后是要压缩的文件
```
2. 然后我们发现还有一些 .txt 文件也需要打包进去，那么可以使用
```bash
tar -rf posts.tar *.txt       //r 是追加文件
```
3. 然后我们发现 hello.md 弄错了，修正后需要更新到压缩包中，可以使用
```bash
tar -uf post.tar hello.md     //u 是更新
```
4. 压缩好了，我们来看看压缩包的内容，可以使用
```bash
tar -tf posts.tar             //t 是列出文件内容
```
5. 把压缩包发送到其他位置之后，需要解压，可以使用
```bash
tar -xf posts.tar             //x 是解压
```
6. 加入自选参数后的用法（要不要加 v 可以看个人喜好）

## tar.gz 相关

```bash
tar -czf posts.tar.gz *.md   // 压缩
tar -xzf posts.tar.gz        // 解压
```
## tar.bz2 相关

```bash
tar -cjf posts.tar.bz2 *.md  // 压缩
tar -xjf posts.tar.bz2       // 解压
```

## tar.Z 相关
```bash
tar -cZf posts.tar.Z *.md    // 压缩
tar -xZf posts.tar.Z         // 解压
```

## 总结一波，遇到不同类型的文件，请用不同的套路来应对：

```bash
*.tar     -> tar -xf
*.tar.gz  -> tar -xzf
*.tar.bz2 -> tar -xjf
*.tar.Z   -> tar -xZf
*.gz      -> gzip -d
*.rar     -> unrar e
*.zip     -> unzip
```
