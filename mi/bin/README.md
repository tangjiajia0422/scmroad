# Scripts in use

* [tjj-common_func](#tjj-common_func)
* [tjj-confliter](#tjj-confliter)
* [tjj-merge](#tjj-merge)

### <span id="tjj-common_func">tjj-common_func</span>

通用方法列表
```bash
print_error "Error msg"                       //echo封装红色，错误提示信息
print_info "Info msg"                         //echo封装绿色，普通提示信息
contains_element "strA" "strB"                //判断strB中是否包含strA
find_conflicts “conflict filelist file”       //找出具体的冲突发生的行，显示出来
echo_array "${a[*]}"                          //输出数组每个元素
```

### <span id="tjj-confliter">tjj-confliter</span>

> 需要tjj-common_func和tjj-xlwt2xls.py

如何使用该脚本?
* 该脚本是用来列出给定列表文件中各文件类型
* 在git merge发生冲突时尤其有用，.git/MERGE_MSG是默认文件
* 提供关键字功能
* 将冲突部分输出到文本文件和xls文件中

真实示例:
* non-hlos需要从MSM8996.LA.2.0.1.c4 升级到 MSM8996.LA.2.0.1.c4-01012
* 在只需要过滤出modem_proc目录下发生冲突的各文件类型，就可以这样使用:
```bash
#默认冲突文件就是.git/MERGE_MSG，因此-f可以省
$0 -f '.git/MERGE_MSG' -k 'modem_proc'

#如果需要将冲突输出到文件，则需要加上-d(detail)选项，默认输出文件是conflicts.xls
$0 -f '.git/MERGE_MSG' -k 'modem_proc' -d 
```
### <span id="tjj-merge">tjj-merge</span>

> 需要tjj-common_func

如何使用该脚本?
* 该脚本是用来处理通用仓库在merge出现冲突后，也可以把当前目录下某些子文件夹回复成ours
* 该脚本会首先做git merge的操作，根据需求是否回退某些子目录

真实示例:
* non-hlos需要从MSM8996.LA.2.0.1.c4 升级到 MSM8996.LA.2.0.1.c4-01012
* 但只需要升级modem_proc这个目录，而其他目录还保留为MSM8996.LA.2.0.1.c4
* 因此可以这样使用该脚本: 
```bash
#branch_ours和branch_theirs都需要存在的branch，请检查branch前是否有remote前缀
$0 -k 'modem_proc' -s 'branch_ours' -t 'branch_theirs'
#-k省去，则所有目录都会回退到merge前的状态
#-s省去，则使用HEAD。不省则会先执行 git checkout -f "branch_ours"(暂不支持，请保持当前仓库clean)
#-t不可省，这是需要merge的分支！
```



