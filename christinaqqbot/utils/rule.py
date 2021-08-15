import nonebot
from nonebot.rule import Rule
from nonebot.adapters.cqhttp import Bot,Event


gruop_white_list=nonebot.get_driver().config.whitelist

async def _gruop_white_list(bot: Bot, event: Event, state: dict) -> bool:
    if(event.group_id in gruop_white_list.values()):
        return True
    else:
        return False
