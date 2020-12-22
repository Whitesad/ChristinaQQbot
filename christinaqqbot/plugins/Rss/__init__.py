from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters.cqhttp import Bot,Event,MessageSegment
from nonebot import require
from nonebot.log import logger


import asyncio
import threading
import datetime as dt

from christinaqqbot.utils.rule import _gruop_white_list



test=on_command('test',rule=to_me()&_gruop_white_list)

def send(bot:Bot,event:Event,message:str):
    asyncio.run(bot.send_group_msg(group_id=event.group_id,message=message))

async def run(bot:Bot,event:Event):
    await bot.send_group_msg(group_id=event.group_id,message="async 第一条信息 "+dt.datetime.now().strftime('%F %T'))
    await bot.send_group_msg(group_id=event.group_id,message="async 第二条信息 "+dt.datetime.now().strftime('%F %T'))
    await bot.send_group_msg(group_id=event.group_id,message="aynnc 第三条信息 "+dt.datetime.now().strftime('%F %T'))

async def test_thread(bot:Bot,event:Event):
    asyncio.create_task(bot.send_group_msg(group_id=event.group_id,message="task 第一条信息 "+dt.datetime.now().strftime('%F %T')))
    asyncio.create_task(bot.send_group_msg(group_id=event.group_id,message="task 第二条信息 "+dt.datetime.now().strftime('%F %T')))
    asyncio.create_task(bot.send_group_msg(group_id=event.group_id,message="task 第三条信息 "+dt.datetime.now().strftime('%F %T')))

@test.handle()
async def _(bot:Bot,event:Event,dic:dict):
    asyncio.create_task(test_thread(bot,event))
    logger.info('回复成功！')