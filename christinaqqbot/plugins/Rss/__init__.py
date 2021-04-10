from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters.cqhttp import Bot,Event
from nonebot.adapters.cqhttp import MessageSegment as msg
from nonebot.log import logger

from .util import check_rss,update_rss,rss_db_init,rss_server,add_rss,query_user_rss,remove_rss
from .model import Rss

from christinaqqbot.utils.rule import _gruop_white_list

import threading

rss_db_init()
threading.Thread(target=rss_server).start()


RSS=on_command('rss',rule=to_me()&_gruop_white_list)
@RSS.handle()
async def _handle(bot: Bot, event: Event, state: dict):
    args_list = str(event.message).strip().split()
    error_reply='\
所输入命令有误！现在支持的命令如下：\r\n\
add:添加一个rss源。/rss add 源名称 源地址\r\n\
list:查看自己所添加的所有源 /rss list \r\n\
remove:移除所添加的一个源。/rss remove 订阅源的id'
    if(len(args_list)>=1):
        if(args_list[0]=='add' and len(args_list)>=3):
            rss_name,rss_url=args_list[1],args_list[2]
            rss=Rss(name=rss_name,url=rss_url,user_id=event.user_id,group_id=event.group_id,type='group')
            des=check_rss(rss.url)
            if(des==''):
                await RSS.finish(msg.reply(id_=event.message_id)+'你所输入的rss源有误！')
            else:
                rss.describe=des
                add_result = add_rss(rss)
                if(add_result=='repeat'):
                    await RSS.finish(msg.reply(id_=event.message_id)+'你已添加过该源，请勿重复添加！')
                await update_rss(rss,mode='init')
                await RSS.finish(msg.reply(id_=event.message_id)+'RSS {rss_name} 添加成功\r\nrss简介：{describe}'.format(rss_name=rss_name,describe=des))
        elif(args_list[0]=='list'):
            results=query_user_rss(user_id=event.user_id)
            reply='您的订阅:\r\n' if len(results)>0 else '您还没有订阅rss'
            for result in results:
                reply+='id:{rss_id} {rss_name}\r\n{rss_url}\r\n'.format(
                    rss_id=result[0],
                    rss_name=result[5],
                    rss_url=result[-1]
                )
            await RSS.finish(msg.reply(id_=event.message_id)+reply)
        elif(args_list[0]=='remove' and len(args_list)>=2):
            remove_result=remove_rss(user_id=event.user_id,subscibe_id=int(args_list[1]))
            if(remove_result=='none'):
                await RSS.finish(msg.reply(id_=event.message_id)+'没有该rss记录，请使用正确的id')
            elif(remove_result=='no_permission'):
                await RSS.finish(msg.reply(id_=event.message_id)+'你没有该rss记录的权限')
            elif(remove_result=='success'):
                await RSS.finish(msg.reply(id_=event.message_id)+'删除成功')
            elif(remove_result=='error'):
                await RSS.finish(msg.reply(id_=event.message_id)+'删除错误!')
        else:
            await RSS.finish(msg.reply(id_=event.message_id)+error_reply)
    else:
        await RSS.finish(msg.reply(id_=event.message_id)+error_reply)
