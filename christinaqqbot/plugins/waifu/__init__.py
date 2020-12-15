from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters.cqhttp import Bot,Event,MessageSegment

import random
import requests
import lxml
from  bs4 import BeautifulSoup
import json
import os
import platform

from christinaqqbot.utils.rule import _gruop_white_list

waifu=on_command('waifu',rule=to_me()&_gruop_white_list)

def save_pic(pic_url):
    pic_name=pic_url.split('/')[-1]
    try:
        r=requests.get(url=pic_url)
    except Exception:
        raise Exception
    with open('./pic/'+pic_name,'wb')as f:
        f.write(r.content)
        f.close()
    return pic_name

@waifu.handle()
async def _(bot: Bot, event: Event, state: dict)->None:
    waifu_url='https://www.thiswaifudoesnotexist.net/example-'+str(random.randint(0,100000))+'.jpg'
    reply=MessageSegment.reply(id_=event.id)
    try:
        pic_name=save_pic(waifu_url)
        try:
            sys = platform.system()
            pic_file=''
            if sys == "Windows":
                pic_file=os.getcwd()+'\pic\\'+pic_name
            elif sys == "Linux":
                pic_file=os.getcwd()+'/pic/'+pic_name
            reply+=MessageSegment.image(file='file:///'+pic_file)
            await bot.send_group_msg(group_id=event.group_id,message=reply)
        finally:
            os.remove(pic_file)
    except Exception:
        reply=reply+"waifu生成错误！请再次尝试！"
        await bot.send_group_msg(group_id=event.group_id,message=reply)

    