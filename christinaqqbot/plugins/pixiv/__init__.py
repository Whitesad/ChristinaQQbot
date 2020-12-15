from nonebot import on_message
from nonebot import on_command
from nonebot import on_notice
from nonebot.rule import to_me
from nonebot.adapters.cqhttp import Bot,Event
from nonebot.adapters.cqhttp import MessageSegment as msg

import requests
import json
import random
import os
import asyncio
import threading
import time

from christinaqqbot.utils.reply import *
from christinaqqbot.utils.rule import  _gruop_white_list

emoji_image='34a6d4bbd65b0c8903c9fed1f12e9792.image'
emoji_image2='3674633fb2a753be08cf09d3b2045d71.image'

api_url='https://api.imjad.cn/pixiv/v2/'


setu_tags=['萝莉','黑丝','白丝','魅魔','吸血鬼','白毛','FGO','arknights','原神','碧蓝航线','百合','红瞳','舰队Collection','JK']
api_url='https://pix.ipv4.host/illustrations'
def get_setu(tag='random')->dict:
    page=random.randint(1,6)
    if(tag=='random'):
        tag=get_random_reply(setu_tags)
        page=random.randint(1,21)
    para={
        'keyword':tag,
        'pageSize':'20',
        'searchType':'origin',
        'illustType':'illust',
        'page':str(page)
    }
    try:
        r=requests.get(url=api_url,params=para)
    except Exception:
        raise Exception
    
    result_dict=json.loads(r.text)
    if('data' in result_dict.keys()):
        result=result_dict['data'][random.randint(0,20)]
        return {
            'title':result['title'],
            'id':result['id'],
            'artistId':result['artistId'],
            'urls':result['imageUrls'][0]
        }
    else:
        return None


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


def save_pic(pic_url):
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

def setu_thread(bot:Bot,event:Event,args:dict):
    # if(key_word=='random'):
    #     # reply=msg.reply(id_=event.id)+'正在随机生成图片中，请等待...\r\n生成时间越久图片质量越高'
    #     # asyncio.run(bot.send_msg(group_id=event.group_id,message=reply))
    #     pass
    # else:
    #     reply=msg.reply(id_=event.id)+'正在依据关键词：'+key_word+' 生成图片中，请等待...\r\n生成时间越久图片质量越高'
    #     asyncio.run(bot.send_msg(group_id=event.group_id,message=reply))
    try:
        setu=get_setu(tag=args['key_word'])
        if(setu==None):
            None_reply=msg.reply(id_=event.id)+'淦哦老兄，你的xp真**怪！建议重新搜或者换个xp！'
            asyncio.run(bot.send_msg(group_id=event.group_id,message=None_reply))
            return
        pic_name=save_pic(setu['urls']['original'])
        try:
            pic_file=os.getcwd()+'\pic\\'+pic_name

            pic_id="P站id:"+str(setu['id'])
            pic_tag="关键词"+args['key_word']
            if(args['mode']=='xml'):
                setu_reply='[CQ:cardimage,file='+'file:///'+pic_file+',source='+pic_id+' '+pic_tag+']'
                asyncio.run(bot.send_msg(group_id=event.group_id,message=setu_reply))
            elif(args['mode']=='pic'):
                setu_reply=msg.reply(id_=event.id)+msg.image(file='file:///'+pic_file)+pic_id+'\r\n'+pic_tag
                asyncio.run(bot.send_msg(group_id=event.group_id,message=setu_reply))
        finally:
            os.remove(pic_file)
    except Exception:
        error_reply=msg.reply(id_=event.id)+'你的涩图炸了，你可以尝试再来一张。'
        asyncio.run(bot.send_msg(group_id=event.group_id,message=error_reply))

pixiv=on_command('setu',rule=to_me()&_gruop_white_list)
@pixiv.handle()
async def handle_setu(bot: Bot, event: Event, state: dict):
    args_list = str(event.message).strip().split()
    opt=['-s','-m','--help']
    args={
        'key_word':'random',
        'mode':'xml'
    }
    for arg in args_list:
        if(arg[:1]=='-'and arg not in opt):
            await pixiv.finish(msg.reply(id_=event.id)+'你输入的{}有误，请输入--help获得命令帮助'.format(arg))
    if('--help'in args_list):
        await  pixiv.finish(msg.reply(id_=event.id)+'-m:设置回复模式，xml/pic\r\n-s:搜索关键词，置空则为随机')

    if('-s'in args_list):
        if(args_list.index('-s')!=len(args_list)-1):
            if(args_list[args_list.index('-s')+1]not in opt):
                args['key_word']=args_list[args_list.index('-s')+1]
            else:
                await  pixiv.finish(msg.reply(id_=event.id)+'你所输入的-s搜索参数有误！搜索参数应该为不带空格的单词，语言不定。')
        else:
            await  pixiv.finish(msg.reply(id_=event.id)+'你所输入的-s搜索参数有误！搜索参数应该为不带空格的单词，语言不定。')
    if('-m'in args_list):
        if(args_list.index('-m')!=len(args_list)-1):
            if(args_list[args_list.index('-m')+1] in ['xml','pic']):
                args['mode']=args_list[args_list.index('-m')+1]            
            else:
                await pixiv.finish(msg.reply(id_=event.id)+"你所输入的-m显示参数有误！\r\nxml:以xml大图发送，默认选项\r\npic:以小图形式发送")
        else:
            await pixiv.finish(msg.reply(id_=event.id)+"你所输入的-m显示参数有误！\r\nxml:以xml大图发送，默认选项\r\npic:以小图形式发送")
    
    await pixiv.send(msg.reply(id_=event.id)+"你的涩图正在处理，依据关键词{}".format(args['key_word']))
    threading.Thread(target=setu_thread,args=(bot,event,args)).start()

