# -*- coding: utf-8 -*-
from fuzzywuzzy import fuzz
from nonebot import on_command, get_driver
from nonebot.adapters import Bot, Event, Message
from nonebot.rule import to_me
from nonebot.params import CommandArg

from tatarubot2.plugins.ff_weibo import ff_weibo_help
from tatarubot2.plugins.house import house_help
from tatarubot2.plugins.item import item_help
from tatarubot2.plugins.item_new import item_new_help
from tatarubot2.plugins.logs_dps import logs_dps_help
from tatarubot2.plugins.lottery import lottery_help
from tatarubot2.plugins.market import market_help
from tatarubot2.plugins.market_new import market_new_help
from tatarubot2.plugins.nuannuan import nuannuan_help
from tatarubot2.plugins.precious import precious_help
from tatarubot2.plugins.bili import bili_help
from tatarubot2.plugins.quest import quest_help

this_command = "/help"
bot_help = on_command(this_command, rule=to_me(), priority=5)
(bot_name,) = get_driver().config.nickname


async def create_help():
    return_list = []
    return_list.append(await nuannuan_help())
    return_list.append(await precious_help())
    return_list.append(await lottery_help())
    return_list.append(await ff_weibo_help())
    return_list.append(await item_help())
    return_list.append(await item_new_help())
    return_list.append(await market_help())
    return_list.append(await market_new_help())
    return_list.append(await house_help())
    return_list.append(await logs_dps_help())
    return_list.append(await bili_help())
    return_list.append(await quest_help())
    return return_list


async def find_best_match(strings, keyword):
    best_match = None
    max_ratio = -1

    for string in strings:
        if keyword == string.split(" ", 1)[0]:
            return string
        ratio = fuzz.ratio(string.lower(), keyword.lower())
        if ratio > max_ratio:
            max_ratio = ratio
            best_match = string

    return best_match


@bot_help.handle()
async def handle_first_receive(event: Event, keyword: Message = CommandArg()):
    help_list = await create_help()
    if not keyword:
        return_str = f"【{bot_name}现有的功能】\n注：以(*)开头的命令需私聊或群里@机器人才有效\n\n" + \
                     "\n\n".join(help_list)
    else:
        return_str = await find_best_match(help_list, keyword.extract_plain_text())
    await bot_help.finish(return_str)
