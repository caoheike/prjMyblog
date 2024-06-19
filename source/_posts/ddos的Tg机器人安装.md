---
title: ddos的Tg机器人安装
date: 2024-06-05 20:27:42
tags:
---
### TG的ddos机器人安装

1、首先推荐的肯定是ubantu环境本人用的ubantu20

```
yum install python3 -y
```

2、以下是需要的依赖环境

```py
pip3 or pip install python-telegram-bot==12.8
```

3、tg加这个机器人创建bot

https://t.me/BotFather 创建机器人 获取id

4、根据token获取chatid

获取个人id

https://api.telegram.org/bot{token}/getUpdates

https://api.telegram.org/bot7433057629:AAGos0BhjbHnlE67WhcVX9RS25WMxOm2umY/getUpdates

5、获取群聊的chatid

拉入群聊继续获取id

6、将源码的频道以及token进行一个替换即可运行

