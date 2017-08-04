#define _GNU_SOURCE
#include <sys/mount.h>
#include <stdio.h>
#include <errno.h>

/*
 * mount函数的出错的分析
 */
int main()
{
  int rlt = mount("conf/hosts", "rootfs/etc/hosts", "none", MS_BIND, NULL);
  if (errno == EACCES){ printf("权能不足");}
  if (errno == EBUSY){ printf("源文件系统已被挂上。或者不可以以只读的方式重新挂载，因为它还拥有以写方式打开的文件; 目标处于忙状态");}
  if (errno == ENOENT){ printf("路径名部分内容表示的目录不存在");}
  if (errno == ENOTDIR){printf("路径名的部分内容不是目录");}
  if (errno == EPERM){printf("调用者权能不足");}
  if (errno == ENOTBLK){printf("source不是块设备");}
  if (errno == ELOOP){printf("路径解析的过程中存在太多的符号连接");}
 
  printf("tangjiajia %d", rlt);
  
  return 0;
}
