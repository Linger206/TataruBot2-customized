"""
获取服务端公网IP
仅超级用户私聊使用
"""

import requests
from nonebot import on_fullmatch
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, GroupMessageEvent
from nonebot.permission import SUPERUSER
from nonebot.rule import to_me

this_command = "ip"
ip = on_fullmatch(this_command, rule=to_me(), permission=SUPERUSER, priority=5)


@ip.handle()
async def handle_first_receive(event: GroupMessageEvent):
    await ip.finish("群聊不支持此指令")


@ip.handle()
async def handle_first_receive(event: PrivateMessageEvent):
    return_str = await pub_ipv4()
    await ip.finish(return_str)


# 取消代理
proxies = {"https": ""}


async def pub_ipv4():
    try:
        with requests.get('https://4.ident.me', proxies=proxies) as myip4:
            with requests.get('https://6.ident.me', proxies=proxies) as myip6:
                return myip4.text + "\n" + myip6.text
    except:
        with requests.get('https://api64.ipify.org', proxies=proxies) as myip:
            return myip.text
