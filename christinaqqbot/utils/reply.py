import random
from nonebot.adapters.cqhttp import Bot,Event
from nonebot.adapters.cqhttp import MessageSegment,Message
from typing import Union

def get_random_reply(random_list):
    random_sample =random.sample(range(0,len(random_list)),len(random_list))
    random_int=random_sample[random.randint(0,len(random_sample)-1)]
    return random_list[random_int]

async def bot_reply(bot:Bot,event:Event,message:Union[str, Message]):
    reply=MessageSegment.reply(id_=event.id)+message
    await  bot.send_group_msg(group_id=event.group_id,message=message)
