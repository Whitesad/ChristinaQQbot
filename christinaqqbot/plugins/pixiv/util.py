from asyncio import tasks
import asyncio
from bs4 import BeautifulSoup
import urllib.request
import feedparser
import re
import random
import requests
import platform
import os
import time,datetime


import nonebot
from nonebot.adapters.cqhttp import Bot,Event
from nonebot.adapters.cqhttp import MessageSegment as msg
from nonebot.matcher import Matcher
from nonebot import get_bots

from christinaqqbot.utils.reply import get_random_reply
from christinaqqbot.utils.time import get_beijing_time
from .model import setu


setu_tags=['萝莉','黑丝','白丝','魅魔','吸血鬼','白毛','arknights','原神','碧蓝航线','百合','红瞳','舰队Collection','JK','巨乳']

setu_api=nonebot.get_driver().config.setu_api

def get_2_setu(tag='random')->setu:
    if(tag=='random'):
        tag=get_random_reply(setu_tags)
    try:
        api_url=setu_api+'/pixiv/search/{tag}/popular/0'.format(tag=tag)
        r=requests.get(url=api_url)
        r=feedparser.parse(r.text)
    except Exception:
        raise Exception("setu api访问错误！\r\n你的涩图炸了，你可以尝试再来一张。")
    
    if(len(r['entries'])>0):
        result=r['entries'][random.randint(0,len(r['entries'])-1)]
        image_url=re.findall(r'["](.*?)["]',result['summary'])[0]
        return setu(
            url=image_url,
            type=2,
            info={
                'title':result['title'],
                'id':result['id'].split('/')[-1], #取ID
                'author':result['author'],
                'tag':tag
            }
        )
    else:
        return None

def get_3_setu()->setu:
    try:
        api_url=setu_api+'/95mm/tab/%E7%83%AD%E9%97%A8'
        r=requests.get(url=api_url)
        r=feedparser.parse(r.text)
    except Exception:
        raise Exception("setu api访问错误！\r\n你的涩图炸了，你可以尝试再来一张。")
    
    try:
        pic=get_random_reply(r['entries'])
        
        opener=urllib.request.build_opener()
        opener.addheaders=[("User-Agent","Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE")]
        data=opener.open(pic['link'])

        soup=BeautifulSoup(data.read(),'lxml')
        # 找到标题，得到页数
        title=soup.find(class_='post-title h3').contents[0]
        page_num = int(re.findall("\d+", title)[-1])
        random_pic_url=pic['link']
        random_pic_url=random_pic_url.replace('.html','/'+str(random.randint(1,page_num))+'.html')

        data=opener.open(random_pic_url)
        soup=BeautifulSoup(data.read(),'lxml')
        pic_url=soup.find(class_='nc-light-gallery-item').contents[1].attrs['src']
    except Exception:
        raise Exception("涩图访问错误！\r\n你的涩图炸了，你可以尝试再来一张。")
    return setu(
        url=pic_url,
        type=3,
    )

def get_setu(tag='random',type=2)->dict:
    if(type==2):
        return get_2_setu(tag=tag)
    elif(type==3):
        return get_3_setu()

# 计算平台
sys = platform.system()
def save_setu(pic_url):
    try:
        opener=urllib.request.build_opener()
        opener.addheaders=[("User-Agent","Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE")]
        data=opener.open(pic_url)
    except Exception:
        raise Exception("服务器转存请求图片错误！\r\n你的涩图炸了，你可以尝试再来一张。")
    try:
        pic_name=pic_url.split('/')[-1]
        if(not os.path.exists('./pic')):
            os.mkdir('./pic')
        with open('./pic/'+pic_name,'wb')as f:
            f.write(data.read())
            f.close()
    except Exception:
        raise Exception("服务器转存储存图片错误！\r\n你的涩图炸了，你可以尝试再来一张。")
    if sys == "Windows":
        pic_file=os.getcwd()+'\pic\\'+pic_name
    elif sys == "Linux":
        pic_file=os.getcwd()+'/pic/'+pic_name
    return pic_file

async def send_daily_setu(group_id:int,bot:Bot,setu_list:list):
    # await bot.send_group_msg(group_id=group_id,message='test')
    tasks=[]
    for setu in setu_list:
        message='[CQ:image,file={file}]'.format(file='file:///'+setu.pic_file)
        tasks.append(bot.send_group_msg(group_id=group_id,message=message))
    await asyncio.gather(*tasks)
    time.sleep(2)
    await bot.send_group_msg(group_id=group_id,message='今日份涩图已准备好，美好的一天从看涩图开始！')
    return

def daily_setu():
    time.sleep(5)
    prepare_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '6:50', '%Y-%m-%d%H:%M')
    send_time=datetime.datetime.strptime(str(datetime.datetime.now().date()) + '21:36', '%Y-%m-%d%H:%M')

    while True:
        try:
            now_time=get_beijing_time()
            # 达到时间，开始准备涩图
            if(prepare_time<now_time<send_time):
                try:
                    setu_list=get_daily_setu()
                    if(len(setu_list)==0):
                        # 出现任何异常则跳过准备时间的十分钟
                        time.sleep(660)
                        raise Exception('今日排行版没有符合条件的涩图')
                        # 访问涩图排行版正确，但是没有符合条件的涩图
                    for setu in setu_list:
                        setu.pic_file=save_setu(setu.url)

                    bots = get_bots()
                    bot=None
                    for id in bots.keys():
                        bot=bots[id]

                    # 获得开启日常涩图功能的群号
                    daily_setu_group=nonebot.get_driver().config.daily_setu
                    while True:
                        try:
                            now_time=get_beijing_time()
                            # 达到发送时间，发送
                            if(now_time>send_time):
                                for group in daily_setu_group.keys():
                                    asyncio.run(send_daily_setu(daily_setu_group[group],bot,setu_list))
                                break
                            time.sleep(1)
                        except Exception as e:
                            pass
                        
                except Exception as e:
                    pass
                finally:
                    for setu in setu_list:
                        os.remove(setu.pic_file)
                # delete pic
        except Exception as e:
            print(str(e.args))
        
        time.sleep(1)

    

def get_daily_setu():
    setu_list=[]
    try:
        api_url=setu_api+'/pixiv/ranking/day_male/'
        r=requests.get(url=api_url)
        r=feedparser.parse(r.text)
        results=[]
        for entry in r['entries']:
            rank=int(entry['title'].split()[0][1:])
            results.append([rank,entry])
        results=sorted(results,key=lambda result: result[0])
        if(len(results)>0):
            for result in results:
                image_url=re.findall(r'["](.*?)["]',result[1]['summary'])[0]
                if(image_url[-6:-5]=='-'):
                    continue
                image_url=image_url.replace('.cat','.re')
                setu_list.append(
                    setu(
                    url=image_url,
                    type=2,
                    info={
                        'title':result[1]['title'],
                        'id':result[1]['id'].split('/')[-1], #取ID
                        'author':result[1]['author'],
                        'tag':'daily rank'
                })
                )
    except Exception:
        raise Exception('获取当日涩图排行榜错误！')
    finally:
        return setu_list[:10]

async def parse_args(pixiv:Matcher, event: Event,message:str)->dict:
    args_list = message.strip().split()
    opt=['-s','-m','-3','-2','--help','--debug']
    args={
        'key_word':'random',
        'mode':'pic',
        'type':2,
        'debug':False
    }
    for arg in args_list:
        if(arg[:1]=='-'and arg not in opt):
            await pixiv.finish(msg.reply(id_=event.message_id)+'你输入的{}有误，请输入--help获得命令帮助'.format(arg))
    if('--debug'in args_list):
        args['debug']=True
    if('--help'in args_list):
        await  pixiv.finish(msg.reply(id_=event.message_id)+'-m:设置回复模式，xml/pic\r\n-s:搜索关键词，置空则为随机\r\n--debug:开启debug模式，打印更多信息\r\n-2/-3::搜索2次元涩图或者三次元涩图')

    if('-s'in args_list):
        if(args_list.index('-s')!=len(args_list)-1):
            if(args_list[args_list.index('-s')+1]not in opt):
                args['key_word']=args_list[args_list.index('-s')+1]
            else:
                await  pixiv.finish(msg.reply(id_=event.message_id)+'你所输入的-s搜索参数有误！搜索参数应该为不带空格的单词，语言不定。')
        else:
            await  pixiv.finish(msg.reply(id_=event.message_id)+'你所输入的-s搜索参数有误！搜索参数应该为不带空格的单词，语言不定。')
    if('-m'in args_list):
        if(args_list.index('-m')!=len(args_list)-1):
            if(args_list[args_list.index('-m')+1] in ['xml','pic','3']):
                args['mode']=args_list[args_list.index('-m')+1]            
            else:
                await pixiv.finish(msg.reply(id_=event.message_id)+"你所输入的-m显示参数有误！\r\nxml:以xml大图发送\r\npic:以小图形式发送，默认选项\r\n")
        else:
            await pixiv.finish(msg.reply(id_=event.message_id)+"你所输入的-m显示参数有误！\r\nxml:以xml大图发送\r\npic:以小图形式发送，默认选项")
    if('-3' in args_list):
        args['type']=3
    return args