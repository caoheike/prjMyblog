---
title: hack路由测试
date: 2021-08-20 18:07:21
tags: Hack
categories: Hack
---

### hack路由测试

apt update -y && apt upgrade -y
apt-get install -y git curl wget gcc libpcap-dev screen dstat cmake gengetopt byacc flex git zmap iptraf nano vnstat tcpdump python libpcap-dev autoconf automake libtool make g++ unzip protobuf-compiler qttools5-dev-tools qt5-default libprotobuf-dev protobuf-compiler autoconf automake libssl-dev
wget https://www.caida.org/projects/spoofer/downloads/spoofer-1.4.5.tar.gz
tar xvf spoofer-1.4.5.tar.gz
cd spoofer-1.4.5
./configure
make
cd prober
./spoofer-prober

no 回车
no 回车

流量监控
https://blog.csdn.net/weixin_39813200/article/details/110603277 
vnstat -l -i eth0

layerCN2 不限量 120
https://ipraft.com  刚认识送的渠道 香港vps
https://t.me/primebotnet   老外api
https://www.estoxy.com/dedicated-servers-nl-10g   分享的10g机器
枣庄      应该是个游戏服务器 打了玩家会掉
https://spoofer.caida.org/report.php?sessionkey=pr442f5zb7vi79 伪造api
https://www.seflow.net/dedicated 机器买了-但是量不够大
https://account.megalayer.net/cart.php?gid=3 不稳定 可能伪造不了
https://t.me/ME_MOON987  推荐的便宜机器
http://www.daidc.com 国内扫描