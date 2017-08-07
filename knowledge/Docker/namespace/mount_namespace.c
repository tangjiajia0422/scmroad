#define _GNU_SOURCE
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/mount.h>
#include <stdio.h>
#include <errno.h>
#include <sched.h>
#include <signal.h>
#include <unistd.h>

/*定义一个给clone用的栈，大小1M */
#define STACK_SIZE (1024 * 1024)
static char container_stack[STACK_SIZE];

char* const container_args[] = {"/bin/bash", "-l", NULL};

int container_main(void* arg)
{
  printf("Container - inside the container!\n");
  printf("Container [%5d] - inside the container!\n", getpid());
  sethostname("container", 10); //设置容器中的hostname

  //remount '/proc' 来欺骗"top"和"ps"等靠读取/proc目录下信息的命令
  if (mount("proc", "rootfs/proc", "proc", 0, NULL) !=0 ){
    perror("proc");
  }

  if (mount("sysfs", "rootfs/sys", "sysfs", 0, NULL) !=0 ){
    perror("sys");
  }

  if (mount("none", "rootfs/tmp", "tmpfs", 0, NULL) !=0 ){
    perror("tmp");
  }

  if (mount("devpts", "rootfs/dev/pts", "devpts", 0, NULL) !=0 ){
    perror("dev/pts");
  }

  if (mount("shm", "rootfs/dev/shm", "tmpfs", 0, NULL) !=0 ){
    perror("dev/shm");
  }

  if (mount("tmpfs", "rootfs/run", "tmpfs", 0, NULL) !=0 ){
    perror("run");
  }

  /*
   * 模仿Docker的从外向容器里mount相关文件
   * 可以查看 /var/lib/docker/containers/<container_id>目录，会看到docker的这些文件
   */
  // 在执行mount操作的时候，rootfs_etc/hosts和rootfs/etc/hosts这两文件都需要存在，不存在先touch为空文件
  if (mount("rootfs_etc/hosts", "rootfs/etc/hosts", "none", MS_BIND, NULL) !=0 || 
      mount("rootfs_etc/hostname", "rootfs/etc/hostname", "none", MS_BIND, NULL) !=0 ||
      mount("rootfs_etc/resolv.conf", "rootfs/etc/resolv.conf", "none", MS_BIND, NULL) !=0 ){
    perror("rootfs_etc");
  }

  // 模仿docker run命令中的-v, --volume=[]参数的行为
  if (mount("/tmp/t1", "rootfs/mnt", "none", MS_BIND, NULL) !=0 ){
    perror("mnt");
  }

  // chroo隔离目录
  if (chdir("./rootfs") !=0 || chroot("./") !=0 ){
    perror("chdir/chroot");
  }

  /* 直接执行一个shell，以便我们观察这个进程空间里的资源是否被隔离了 */
  execv(container_args[0], container_args);
  printf("Something's worng!\n");
  return 1;
}

int main()
{
  printf("Parent - start a container!\n");
  /* 调用clone函数，其中传出一个函数，还有一个栈空间(为什么传尾指针，因为栈是反着的) */
  int container_pid = clone(container_main, container_stack+STACK_SIZE, 
                            CLONE_NEWUTS | CLONE_NEWIPC | CLONE_NEWPID | CLONE_NEWNS | SIGCHLD, NULL);
  /* 在父进程结束前，等待子进程结束 */
  while (waitpid(container_pid, NULL, 0) < 0 && errno == EINTR)
  {
    continue;
  }
  //waitpid(container_pid, NULL, 0);
  printf("Parent - container stopped!\n");
  return 0;
}
