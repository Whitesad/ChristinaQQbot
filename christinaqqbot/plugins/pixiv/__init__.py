from nonebot import on_message
from nonebot import on_command
from nonebot import on_notice
from nonebot.rule import to_me
from nonebot.adapters.cqhttp import Bot,Event
from nonebot.adapters.cqhttp import MessageSegment as msg

import os
import threading

from christinaqqbot.utils.reply import *
from christinaqqbot.utils.rule import  _gruop_white_list

from .model import setu
from .util import daily_setu, get_setu
from .util import parse_args
from .util import save_setu

pixiv=on_command('setu',rule=to_me()&_gruop_white_list)

threading.Thread(target=daily_setu).start()

@pixiv.handle()
async def handle_setu(bot: Bot, event: Event, state: dict):
    # 处理参数
    args= await parse_args(pixiv,event,str(event.message))
    await pixiv.send(msg.reply(id_=event.message_id)+"你的涩图正在处理，依据关键词{}".format(args['key_word']))

    # 得到涩图url
    try:
        setu=get_setu(tag=args['key_word'],type=args['type'])
    except Exception as e:
        await pixiv.finish(msg.reply(id_=event.message_id)+'info:{}'.format(e.args[0]))
    
    # 储存涩图
    try:
        pic_file=save_setu(setu.url)
    except Exception as e:
        await pixiv.finish(msg.reply(id_=event.message_id)+'info:{}'.format(e.args[0]))

    # 构造涩图形式
    # 以cardimage形式发送
    if(args['mode']=='xml'):
        if(setu.type==2):
            setu_reply='[CQ:cardimage,file='+'file:///'+pic_file+',source=id:{pic_id} tag:{pic_tag}]'.format(
                pic_id=setu.info['id'],
                pic_tag=setu.info['tag']
            )
        elif(setu.type==3):
            setu_reply='[CQ:cardimage,file='+'file:///'+pic_file+']'
    # 以普通图片形式发送
    elif(args['mode']=='pic'):
        if(setu.type==2):
            setu_reply='pixiv id:{id}\r\nauthor:{author}\r\ntitle={title}\r\ntag={tag}\r\n[CQ:image,file={file}]'.format(
                id=setu.info['id'],
                author=setu.info['author'],
                title=setu.info['title'],
                tag=setu.info['tag'],
                file='file:///'+pic_file
                )
        elif(setu.type==3):
            setu_reply='[CQ:image,file={file}]'.format(
                file='file:///'+pic_file
                )
    
    login_info=await bot.call_api("get_login_info")
    msgs=[
            {
                "type": "node",
                "data": {
                    "name": login_info['nickname'],
                    "uin": str(login_info['user_id']),
                    "content": setu_reply
                }
            }
        ]
    try:
        await bot.call_api("send_group_forward_msg",group_id=event.group_id,messages=msgs)
    except Exception:
        await pixiv.finish(msg.reply(id_=event.message_id)+'info:{}'.format('涩图发送失败！'))
    finally:
        os.remove(pic_file)