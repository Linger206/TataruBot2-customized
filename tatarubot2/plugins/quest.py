import json
import os
import urllib
from difflib import SequenceMatcher
from queue import Queue

import requests
from nonebot import on_command
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText
from nonebot.rule import to_me

this_dir = os.path.split(os.path.realpath(__file__))[0]
json_path = os.path.join(this_dir, "../data/plot_quest.json")
plot_quest_list = json.loads(open(json_path, "r", encoding="utf-8").read())


def bfs_quest(quest):
    q = Queue()
    q.put(quest)
    now_main_scenario = "Endwalker主线任务(6.0)"
    # back search
    back_cnt = 0
    visited = set()
    while not q.empty() and back_cnt < 10000:
        a_quest = q.get(False)
        if a_quest['pk'] in visited:
            continue
        back_cnt += 1
        visited.add(a_quest['pk'])
        if a_quest['fields']['endpoint']:
            break
        for pre_quest_id in a_quest['fields']['pre_quests']:
            for pre_q in plot_quest_list:
                if pre_q['pk'] == pre_quest_id:
                    q.put(pre_q)
    # forward search
    forward_cnt = 0
    visited.clear()
    q.put(quest)
    while not q.empty() and forward_cnt < 10000:
        a_quest = q.get(False)
        if a_quest['pk'] in visited:
            continue
        forward_cnt += 1
        visited.add(a_quest['pk'])
        if a_quest['fields']['endpoint']:
            now_main_scenario = a_quest['fields']['endpoint_desc']
            break
        for suf_quest_id in a_quest['fields']['suf_quests']:
            for suf_q in plot_quest_list:
                if suf_q['pk'] == suf_quest_id:
                    q.put(suf_q)
    back_cnt -= 1
    forward_cnt -= 1
    return {
        "back_cnt": back_cnt,
        "now_main_scenario": now_main_scenario,
        "forward_cnt": forward_cnt,
    }


def get_banner(quest_id):
    API_URL = "https://cafemaker.wakingsands.com"
    INTL_API_URL = "https://xivapi.com"
    api_base = API_URL
    banner_url = ""
    r = requests.get("{}/quest/{}".format(api_base, quest_id), timeout=5)
    if r.status_code != 200:
        api_base = INTL_API_URL
        r = requests.get("{}/quest/{}".format(api_base, quest_id), timeout=5)
        if r.status_code != 200:
            return ""
    quest_data = r.json()
    if "Banner" in quest_data and quest_data["Banner"] != "":
        banner_url = "{}{}".format(api_base, quest_data["Banner"])
    return banner_url


async def search_quest(quest_name: str):
    quests = [e for e in plot_quest_list if quest_name in e["fields"]['name']]
    if len(quests) == 0:
        quests = [e for e in plot_quest_list if quest_name in e["fields"]['language_names']]
    if not quests:
        msg = f'找不到任务"{quest_name}"，请检查任务名'
    else:
        quest = max(quests, key=lambda x: SequenceMatcher(None, str(x), quest_name).ratio())
        # main scenario
        if quest['fields']['quest_type'] == 3:
            quest_img_url = (
                "https://huiji-public.huijistatic.com/ff14/uploads/4/4a/061432.png"
            )
            bfs_res = bfs_quest(quest)
            # fmt: off
            percent = (bfs_res["back_cnt"] + 1) * 100 / (bfs_res["back_cnt"] + 1 + bfs_res["forward_cnt"])
            # fmt: on
            content = "{}进度已达到{:.2f}%，剩余{}个任务".format(
                bfs_res["now_main_scenario"], percent, bfs_res["forward_cnt"]
            )
        # special
        elif quest['fields']['quest_type'] == 8:
            quest_img_url = (
                "https://huiji-public.huijistatic.com/ff14/uploads/4/4c/061439.png"
            )
            content = "特殊支线任务"
        else:
            quest_img_url = (
                "https://huiji-public.huijistatic.com/ff14/uploads/6/61/061431.png"
            )
            content = "支线任务"

        url = "https://ff14.huijiwiki.com/wiki/{}".format(
            urllib.parse.quote("任务:" + str(quest['fields']['name']))
        ) if "cn" in quest['fields']['language_names'] else (
            "https://www.garlandtools.org/db/#quest/{}".format(quest['pk']))
        try:
            banner_url = get_banner(quest['pk'])
        except Exception:
            banner_url = ""
        msg = {
                "url": url,
                "title": f"{quest['fields']['name']}",
                "content": content,
                "image": quest_img_url,
                "banner": banner_url
            }

    return msg


quest_matcher = on_command("quest", aliases={"任务"}, rule=to_me(), priority=5)


async def quest_help():
    return "(*)" + "quest/任务 任务名/关键字 查询任务进度"


@quest_matcher.handle()
async def handle(event: Event, matcher: Matcher):
    key_words = event.get_message().extract_plain_text().strip().split(" ", 1)
    if len(key_words) >= 2:
        matcher.set_arg("key_word", Message(key_words[1]))


@quest_matcher.got("key_word", prompt="请输入任务名:")
async def handle_key_word(key_word: str = ArgPlainText()):
    key_word = key_word.strip()
    if not key_word:
        await quest_matcher.finish("任务名为空")
    try:
        result = await search_quest(key_word)
        if type(result) != dict:
            raise Exception(result)
    except Exception as e:
        await quest_matcher.finish(e.args if e.args else "查询失败")
        return

    msg = "任务名: {}\n" \
          "任务类型: {}\n" \
          "wiki地址: {}\n".format(result['title'], result['content'], result['url'])
    await quest_matcher.finish(msg)
