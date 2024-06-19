TG直链和系统代理

```
wget -N --no-check-certificate https://raw.githubusercontent.com/ToyoDAdoubiBackup/doubi/master/mtproxy.sh && chmod +x mtproxy.sh && bash mtproxy.sh
```

# 使用一键脚本搭建shadowsocks服务

21 3 月, 2019 3378点热度 0人点赞 0条评论

手动搭建shadowsocks服务无论是对程序员还是我这样的非专业小白来说，可能都是一件很麻烦的事情，好在有秋水大大的 shadowsocks一键搭建脚本。
秋水大大的shaowsocks脚本我推荐使用4合一脚本，安装的时候再选择ss版本。
秋水大大的脚本支持CentOS 6+，Debian 7+，Ubuntu 12+等常见的Linux发行版。
个人比较推荐选择shadowsocks的libev版本，尤其是当你的vps配置比较低的时候，libev轻量级的优势就凸显出来了，还支持simple-obfs。

该脚本在centos8上会报错：[Error] Failed to install python ，建议使用CentOS 7或手动安装shadowsocks。

使用的VPS 是[搬瓦工 49.9刀/年套餐](https://jimubiedao.com/go/bandwagon-cn2-49-99)，流量足够，CN2网络，速度也比较快。

2021年更新：Shadowsocks 代理协议目前容易被墙，更推荐使用 Trojan或Vless协议。

如果是为了更好的支持udp协议，建议在vps上搭建[v2-ui面板](https://jimubiedao.com/1166)，同样支持shadowsocks。
运行shadowsocks一键脚本之前，先安装bbr脚本，以优化网速。

## bbr一键脚本：

```
wget --no-check-certificate https://github.com/teddysun/across/raw/master/bbr.sh
chmod +x bbr.sh
./bbr.sh
```

安装完成后，脚本会提示需要重启 VPS ，输入 y 并回车后重启。

如果没什么问题，接着运行ss一键脚本。

## Shadowsocks 四合一脚本：

```
wget --no-check-certificate -O shadowsocks-all.sh https://raw.githubusercontent.com/teddysun/shadowsocks_install/master/shadowsocks-all.sh
chmod +x shadowsocks-all.sh
./shadowsocks-all.sh 2>&1 | tee shadowsocks-all.log
```

如果运行后你的终端有如下提示

```
wget: command not found
```

可能是因为你的vps是最小化安装，那么，只需要自己安装wget就好

**CentOS系统：**

```
yum -y install wget
```

 

**Ubuntu和Debian系统：**

```
apt-get install wget
```

再复制一键脚本运行就好了。

推荐安装libev版本，选择AEAD 加密，开启simple-obfs，然后等待脚本安装完毕即可。

如需手动修改请修改完配置文件后重启对应的 Shadowsocks 服务：

Shadowsocks-libev 配置文件：

```
vi /etc/shadowsocks-libev/config.json
```

Shadowsocks-libev 开启、停止、重启和查看状态命令：

```
/etc/init.d/shadowsocks-libev start | stop | restart | status
```

