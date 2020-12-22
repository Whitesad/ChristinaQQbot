from nonebot.rule import Rule
from nonebot.adapters.cqhttp import Bot,Event


gruop_white_list={
    '男酮之家':822022036,
    'MC上流':983204066,
    'test bot':965768002,
    '执指之手':815659169,
    # 'BIT-fellow':1070578282
    # 'gal':196452038
}

async def _gruop_white_list(bot: Bot, event: Event, state: dict) -> bool:
    if(event.group_id in gruop_white_list.values()):
        return True
    else:
        return False
