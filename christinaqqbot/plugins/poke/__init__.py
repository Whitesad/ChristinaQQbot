from nonebot import on_notice
from nonebot.rule import to_me
from nonebot.adapters.cqhttp import Bot,Event,MessageSegment

from christinaqqbot.utils.reply import *

# 戳 一 戳
pokehah = on_notice()

poke_reply=[
        "lsp你再戳？","连个bot都要戳的肥宅真恶心啊。",
        "你再戳！", "？再戳试试？", "别戳了别戳了再戳就坏了555", "我爪巴爪巴，球球别再戳了", "你戳你🐎呢？！",
        "那...那里...那里不能戳...绝对...", "(。´・ω・)ん?", "有事恁叫我，别天天一个劲戳戳戳！", "欸很烦欸！你戳🔨呢",
        "?","再戳一下试试？","???","正在关闭对您的所有服务...关闭成功","啊呜，刚刚竟然睡着了。什么事？","正在定位您的真实地址。。。\r\n定位成功。轰炸机已起飞"
]

reply=[
    '时间会随着人的感觉而变长或变短，相对论真是既浪漫又伤感的东西呢。',
    '我经常会想，对于冈部来说真由理是一个多么不可或缺的存在\r\n一个人原来可以对另一个人如此珍视',
    '结果我和你的区别可能就是，你是A priori的存在，而我是A posteriori的存在吧。',
    '就算不能总想起来也好，就算100次里只有1次也罢，希望你能想起我，因为那里有着我，1％的墙壁的对面，我一定存在着！冈部…冈部…冈部…',
    'El Psy Congroo',
    '这一切都是命运石之门的选择！',
    '被过去囚禁，对未来叹息。',
    '不要想一味的改变现在，这只会让过去变得面目全非罢了。',
    '过去在远离，未来是否意味着正在靠近。',
    '呐，冈部....',
    '谁要吃变态的香蕉啊！',
    '我不是助手',
    '说了多少遍了,我不是助手！！',
    '眼睛…快闭上…',
    '才不是克里斯蒂娜！',
    '你这个hentai绅士',
    '才不是关心你呢！',
    '不要加蒂娜!!!',
    '白痴吗你，想死吗你?',
    '抱抱…',
    '在百分之一的墙的对面，我一定存在着.',
    '在无数条世界线中，说不定会存在其他的「我」，无数的「我」心意相通，其中说不定就包含着我。',
    '就算思念能超越世界线，现实的收束依旧无情',
    '就算不能总想起来也好，就算100次里只有1次也罢，希望你能想起我，因为那里有着我，1％的墙壁的对面，我一定存在着！冈部…冈部…冈部…',
]

@pokehah.handle()
async def _poke(bot: Bot, event: Event, state: dict) -> None:
    if(event.detail_type=='notify'and event.raw_event['target_id']==event.raw_event['self_id']):
        msg = get_random_reply(reply)

        await bot.send_msg(group_id=event.group_id,message=msg)