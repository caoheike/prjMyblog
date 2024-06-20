#!/bin/bash
pkill -f "python3 freebot.py"
sleep 1
nohup python3 freebot.py > bot.log 2>&1 &