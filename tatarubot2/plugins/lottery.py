# -*- coding: utf-8 -*-
"""
仙人仙彩
"""

import random

from nonebot import on_command, get_driver
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State

this_command = "仙人彩"
lottery = on_command(this_command, priority=5)
(bot_name,) = get_driver().config.nickname


async def lottery_help():
    return this_command + "：帮你选每周仙人仙彩数字"


async def random_lottery():
    last_num_list = []
    lottery_list = []
    for _ in range(3):
        while True:
            last_num = random.randint(0, 9)
            if last_num not in last_num_list:
                last_num_list.append(last_num)
                break
        lottery_list.append(str(random.randint(0, 9)) + " " +
                            str(random.randint(0, 9)) + " " +
                            str(random.randint(0, 9)) + " " +
                            str(last_num))
    return "\n".join(lottery_list)


@lottery.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()
    if args == this_command:
        lottery_num_str = await random_lottery()
        await lottery.finish(f"{bot_name}觉得这个可以！\n" + lottery_num_str)
    else:
        return
