sandisk(){
  my_sandisk=$(df | grep '21D1-FA99' | awk '{print $1}')
  echo "sudo mount ${my_sandisk} /mnt/sandisk"
  sudo mount "${my_sandisk}" /mnt/sandisk
}
#alias adb='/home/mi/workspace/android-sdk-linux/platform-tools/adb'
#alias fastboot='/home/mi/workspace/android-sdk-linux/platform-tools/fastboot'
alias repo='/home/mi/bin/repo/repo'
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../../'
bincp(){
  if [ -e "/mnt/sandisk/Mi/bin" ]; then
    cp -vu ~/bin/tjj-* /mnt/sandisk/Mi/bin
    cp -vf ~/bin/*.md /mnt/sandisk/Mi/bin
    cp -vu ~/bin/tjj-* /mnt/sandisk/mi/scmroad/mi/bin
    cp -vf ~/bin/*.md /mnt/sandisk/mi/scmroad/mi/bin
  else
    echo "Target not exist, please exec '\$sandisk' first"
  fi
}

tjjgithub(){
  git status
  if [ $? = 0 ]; then
    sed -i 's#tangjiajia@xiaomi.com#tang_jiajia@163.com#g' ~/.gitconfig
    cur_remote=$(git remote -v | grep "push" | awk '{$1=$NF="";print $0}')
    remote_nickname=$(git remote -v | grep -E '\(push\)$' | awk '{print $1}')
    git add -A
    # wait inputs for 60 seconds
    read -t 60 -p "Commit message:" commitmsg
    if [ -n "${commitmsg}" ]; then
      echo "git commit -m ${commitmsg}"
      git commit -m "${commitmsg}"
    else
      echo "Manually eval: \$ git commit -m 'xxx'"
    fi
    read -t 20 -p "Push to github?(y/n)" is_push
    if [ "x${is_push}x" = "xyx" ]; then
      echo "git push ${cur_remote} HEAD:master -f"
      #在~/.ssh/config中配置了github的提交key，待验证
      #Host github.com
      #  HostName github.com
      #  User git
      #  IdentityFile /home/mi/.ssh/id_rsa.pub
      #  IdentitiesOnly yes
      git push "${remote_nickname}" HEAD:master -f
    else
      echo "Manually eval: \$ git push "${cur_remote}" HEAD:master -f"
    fi
    sed -i 's#tang_jiajia@163.com#tangjiajia@xiaomi.com#g' ~/.gitconfig
  else
    echo "Error: not a git repository!"
  fi
}
