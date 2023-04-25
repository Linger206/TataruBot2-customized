"""
B站视频搜索
"""
import requests
from bs4 import SoupStrainer, BeautifulSoup
from nonebot import on_command, get_driver
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText
from nonebot.rule import to_me

this_command = "bili"
bili = on_command(this_command, aliases={"攻略"}, rule=to_me(), priority=5)
(bot_name,) = get_driver().config.nickname


@bili.handle()
async def handle(event: Event, matcher: Matcher):
    key_words = event.get_message().extract_plain_text().strip().split(" ", 1)
    if len(key_words) >= 2:
        matcher.set_arg("key_word", Message(key_words[1]))


@bili.got("key_word", prompt="请输入关键词:")
async def handle_key_word(key_word: str = ArgPlainText()):
    key_word = key_word.strip().replace(" ", "+")
    if not key_word:
        await bili.finish("关键词为空")
    result = await search_bili(key_word)
    await bili.finish(result[0] + ": " + result[1] + "\n" + result[2])


headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/54.0.2840.99 Safari/537.36"}


# 搜索B站视频 抓取视频标题和url
async def search_bili(keyword: str):
    bili_url = f"https://search.bilibili.com/all?keyword={keyword}"
    try:
        with requests.get(bili_url, headers=headers, timeout=3) as bili_res:
            bili_res.encoding = 'utf-8'
            only_li_tags = SoupStrainer("li", "video-item matrix")
            bs = BeautifulSoup(bili_res.text, "html.parser", parse_only=only_li_tags)
            up_name = bs.find("a", "up-name").text
            title = bs.find("a", "img-anchor")['title']
            url = bs.find("a", "img-anchor")['href'].replace("//", "https://").replace("?from=search", "")
            return up_name, title, url
    except:
        return "", f"点击看{bot_name}热舞", "https://www.bilibili.com/video/BV1GJ411x7h7"
