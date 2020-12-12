from nonebot import on_message
from nonebot import on_command
from nonebot import on_notice
from nonebot.rule import to_me
from nonebot.adapters.cqhttp import Bot,Event,MessageSegment


import requests
import json
import random
import os
import asyncio
import threading
import time

from christinaqqbot.utils.reply import *


emoji_image='34a6d4bbd65b0c8903c9fed1f12e9792.image'
emoji_image2='3674633fb2a753be08cf09d3b2045d71.image'

api_url='https://api.imjad.cn/pixiv/v2/'

gruop_white_list={
    '男酮之家':822022036,
    'MC上流':983204066,
    'test bot':965768002,
    'BIT-fellow':1070578282
    # 'gal':196452038
}



setu_tags=['萝莉','黑丝','白丝','巨乳','魅魔','吸血鬼','白毛','FGO','arknights','原神','碧蓝航线','百合','FATE','红瞳']
search_tags=[' 50users入り',' 100users入り',' 500users入り',' 1000users入り',' 5000users入り']
def get_random_setu(key_word):
    setu_tag=get_random_reply(setu_tags)
    search_tag=get_random_reply(search_tags)
    if(key_word!='random'):
        setu_tag=key_word
    random_pages=random.sample(range(1,11),10)
    front_page=999999
    url_dict={}
    for page in random_pages:
        if(page>front_page):
            continue
        params={
            'type':'search',
            'word':setu_tag+search_tag,
            'mode':'partial_match_for_tags',
            'order':'date_desc',
            'page':str(page)
        }
        # params={
        #         'type':'rank',
        #         'mode':'day_male',
        #         'page':str(page)
        # }
        # ConnectionError
        try:
            r=requests.get(url=api_url,params=params)
        except Exception:
            raise Exception

        url_dict=json.loads(r.text)
        if('error' in url_dict.keys()):
            front_page=page
            continue
        elif(len(url_dict['illusts'])<=0):
            front_page=page
            continue
        else:
            break

    if('error' in url_dict.keys()):
        return None
    url_list=url_dict['illusts']
    if(len(url_list)==0):
        return None
    no_r18_list=[]
    limit_tag=['R-18G','R-18']
    for url in url_list:
        is_r18=False
        for tag in url['tags']:
            if(tag['name']in limit_tag):
                is_r18=True
                break
        if(not is_r18):
            no_r18_list.append(url)
    if(len(no_r18_list)<=0):
        return None
    random_setu_list=random.sample(range(0,len(no_r18_list)),len(no_r18_list))
    random_setu=no_r18_list[random_setu_list[random.randint(0,len(random_setu_list)-1)]]
    return random_setu


def save_pic(pic):
    pic_url=pic['image_urls']['medium']
    # data={'type':'rank','content':'male','mode':'daily','per_page':'10','page':1}
    headers = {
        'Referer': 'https://app-api.pixiv.net/'
    }
    pic_name=pic_url.split('/')[-1]
    try:
        r=requests.get(url=pic_url,headers=headers)
    except Exception:
        raise Exception
    with open('./pic/'+pic_name,'wb')as f:
        f.write(r.content)
        f.close()
    return pic_name


setu_msg=[
    '[CQ:image,file=3674633fb2a753be08cf09d3b2045d71.image]',
    '色图',
    '涩图',
    'setu'
    ]

def setu_thread(bot:Bot,event:Event,key_word):
    if(key_word=='random'):
        reply=MessageSegment.reply(id_=event.id)+'正在随机生成图片中，请等待...\r\n生成时间越久图片质量越高'
        asyncio.run(bot.send_msg(group_id=event.group_id,message=reply))
    else :
        reply=MessageSegment.reply(id_=event.id)+'正在依据关键词：'+key_word+' 生成图片中，请等待...\r\n生成时间越久图片质量越高'
        asyncio.run(bot.send_msg(group_id=event.group_id,message=reply))

    start=time.time()
    try:
        setu=get_random_setu(key_word=key_word)
        if(setu==None):
            None_reply=MessageSegment.reply(id_=event.id)+'淦哦老兄，你的xp真**怪！建议重新搜或者换个xp！'
            asyncio.run(bot.send_msg(group_id=event.group_id,message=None_reply))
            return
        pic_name=save_pic(setu)
        try:
            pic_file=os.getcwd()+'\pic\\'+pic_name

            pic_id="P站id:"+str(setu['id'])
            pic_time="time:"+"%.1f"%(time.time()-start)+'s'
            setu_reply=MessageSegment.reply(id_=event.id)+MessageSegment.image(file='file:///'+pic_file)+pic_id+'\r\n'+pic_time
            asyncio.run(bot.send_msg(group_id=event.group_id,message=setu_reply))
        finally:
            os.remove(pic_file)
    except Exception:
        error_reply=MessageSegment.reply(id_=event.id)+'你的涩图炸了，你可以尝试再来一张。'
        asyncio.run(bot.send_msg(group_id=event.group_id,message=error_reply))

pixiv=on_message(rule=to_me())
@pixiv.handle()
async def handle_setu(bot: Bot, event: Event, state: dict):
    if event.detail_type=='group':
        is_setu=False
        for key_msg in setu_msg:
            if(key_msg in event.raw_message):
                is_setu=True
                break
        key_word='random'
        if(is_setu):
            msg_list=event.raw_message.split()
            if(msg_list[-1]in setu_msg and len(msg_list)==3):
                key_word=msg_list[-2]

        if(event.group_id in gruop_white_list.values() and is_setu):
            threading.Thread(target=setu_thread,args=(bot,event,key_word)).start()

