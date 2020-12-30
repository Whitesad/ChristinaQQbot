from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters.cqhttp import Bot,Event,MessageSegment
from nonebot.log import logger

from .util import check_rss,update_rss,rss_db_init,rss_server,add_rss
from .model import Rss

from christinaqqbot.utils.rule import _gruop_white_list

import threading

rss_db_init()
threading.Thread(target=rss_server).start()


RSS=on_command('rss',rule=to_me()&_gruop_white_list)
@RSS.handle()
async def _handle(bot: Bot, event: Event, state: dict):
    args_list = str(event.message).strip().split()
    if(len(args_list)>=2):
        rss_name,rss_url=args_list[0],args_list[1]
        rss=Rss(name=rss_name,url=rss_url,user_id=event.user_id,group_id=event.group_id,type='group')
        des=check_rss(rss.url)
        if(des==''):
            await RSS.finish('你所输入的rss源有误！')
        else:
            rss.describe=des
            add_rss(rss)
            await update_rss(rss,mode='init')
            await  RSS.finish('RSS添加成功')
