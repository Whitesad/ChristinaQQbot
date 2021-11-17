import nonebot
from nonebot.adapters.cqhttp import Bot,Event
from nonebot import on_message
from nonebot.adapters.cqhttp import MessageSegment as msg


from nonebot.rule import to_me

from christinaqqbot.utils.rule import _gruop_white_list

function_manager=on_message(rule=to_me(),priority=10)

@function_manager.handle()
async def handle_error_command(bot:Bot,event:Event,state:dict):
    error_reply='您输入的命令有误！现在支持的命令如下：\r\n'\
        +'/setu：搜索一张涩图\r\n'\
        +'/waifu：随机得到一张GAN生成的美少女头像\r\n'\
        +'/rss：rss订阅功能\r\n'\
        +'/mcping：判断该群绑定的mc服务器是否正常运行\r\n'\
        +'戳一戳：随机发送一条语音'
    await function_manager.finish(msg.reply(id_=event.message_id)+error_reply)