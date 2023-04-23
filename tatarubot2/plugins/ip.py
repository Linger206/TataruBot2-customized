"""
获取公网IP, 用于ddns
仅超级用户私聊使用
"""

import requests
from nonebot import on_command
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, GroupMessageEvent
from nonebot.permission import SUPERUSER
from nonebot.rule import to_me

this_command = "ip"
ip = on_command(this_command, rule=to_me(), permission=SUPERUSER, priority=5)
# 取消代理
proxies = {"https": ""}


@ip.handle()
async def handle_first_receive(event: GroupMessageEvent):
    await ip.finish("群聊不支持此指令")


@ip.handle()
async def handle_first_receive(event: PrivateMessageEvent):
    args = str(event.get_message()).strip()
    if args == this_command:
        return_str = await pub_ipv4()
        await ip.finish(return_str)
    else:
        return


async def pub_ipv4():
    try:
        with requests.get('https://4.ident.me', proxies=proxies) as myip:
            return myip.text
    except:
        with requests.get('https://api.ipify.org', proxies=proxies) as myip:
            return myip.text
