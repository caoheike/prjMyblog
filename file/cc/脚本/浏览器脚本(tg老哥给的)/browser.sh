#!/bin/bash

ulimit -n 999999
fileName="browser.js"

if [ ! -f "./$fileName" ]; then
echo -e "\033[33m脚本 [ $fileName ] 不存在！\033[0m"
exit
fi

if [ ! -n "$3" ];then
echo -e "\033[31m错误：命令格式不正确！\033[0m"
echo -e "\033[33m$0 目标(URL) 时间 列表文件\033[0m"
exit
fi

screen -dms 1 timeout $2 node $fileName $1 $2 $3 &
sleep "$2"s
pkill -f optls