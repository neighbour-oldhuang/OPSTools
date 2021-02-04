#!/usr/bin/env bash
## author: huange heaoyytcw@foxmail.com
#. /etc/profile
##INIT BEGIN #designed by huange@hujiang.com
#runUser="gs"
#[[ $(whoami) != "${runUser}" ]] && echo "请使用${runUser}账户运行!" && exit 1
myname="$(basename $0)"
runLogFile="/tmp/${myname}-run.log"
echo "run "$0" at $(date)" >> ${runLogFile}
#set -e
#set -x
[ -f /tmp/${myname}.pid ] && echo "process may already running as $(cat /tmp/${myname}.pid)" && exit 8
echo "$$" > /tmp/${myname}.pid
trap 'echo "exitxxx";exit 8' 2
trap "rm -f  /tmp/${myname}.pid" EXIT
alias grep='egrep -v "$$|grep"|grep'
alias egrep='egrep -v "$$|grep"|egrep'
mklog(){
    if [ "$#" -gt 0 ];then
        echo "$(date) $*" >> ${runLogFile}
    else
        while read line;do
            echo "$(date) $line" >> ${runLogFile}
        done
    fi
}
homeDir="$(dirname $(readlink -f $0))"
#INIT END
