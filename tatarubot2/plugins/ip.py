"""
获取服务端公网IP
仅超级用户私聊使用
"""

import requests
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, GroupMessageEvent
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.rule import to_me

this_command = "ip"
ip = on_command(this_command, rule=to_me(), permission=SUPERUSER, priority=5)


@ip.handle()
async def handle_group(event: GroupMessageEvent):
    await ip.finish("群聊不支持此指令")


@ip.handle()
async def handle_private(event: PrivateMessageEvent, args: Message = CommandArg()):
    ip_type = args.extract_plain_text()
    result = await pub_ip(ip_type)
    await ip.finish(result)


# 取消代理
proxies = {"https": ""}


async def pub_ip(ip_type):
    try:
        if ip_type == "4":
            with requests.get('https://4.ident.me', proxies=proxies) as myip:
                return myip.text
        elif ip_type == "6":
            with requests.get('https://6.ident.me', proxies=proxies) as myip:
                return myip.text
        else:
            with requests.get('https://4.ident.me', proxies=proxies) as myip4:
                with requests.get('https://6.ident.me', proxies=proxies) as myip6:
                    return myip4.text + "\n" + myip6.text
    except:
        with requests.get('https://api64.ipify.org', proxies=proxies) as myip:
            return myip.text
