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
import platform
import feedparser
import re
from bs4 import BeautifulSoup
import urllib.request

from christinaqqbot.utils.reply import *
from christinaqqbot.utils.rule import  _gruop_white_list

# 计算平台
sys = platform.system()

api_url='https://api.imjad.cn/pixiv/v2/'


setu_tags=['萝莉','黑丝','白丝','魅魔','吸血鬼','白毛','FGO','arknights','原神','碧蓝航线','百合','红瞳','舰队Collection','JK']
api_url='https://pix.ipv4.host/illustrations'

def get_2_setu(tag='random'):
    if(tag=='random'):
        tag=get_random_reply(setu_tags)
    try:
        api_url='http://www.rsshub.whitesad.xyz/pixiv/search/{tag}/popular/0'.format(tag=tag)
        r=requests.get(url=api_url)
        r=feedparser.parse(r.text)
    except Exception:
        raise Exception("setu api访问错误！\r\n你的涩图炸了，你可以尝试再来一张。")
    
    if(len(r['entries'])>0):
        result=r['entries'][random.randint(0,len(r['entries'])-1)]
        image_url=re.findall(r'["](.*?)["]',result['summary'])[0]
        return {
            'title':result['title'],
            'id':result['id'].split('/')[-1], #取ID
            'author':result['author'],
            'url':image_url
        }
    else:
        return None

def get_3_setu():
    api_url='http://www.rsshub.whitesad.xyz/95mm/tab/%E7%83%AD%E9%97%A8'
    r=requests.get(url=api_url)
    r=feedparser.parse(r.text)
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
    return {
        'url':pic_url
        }

def get_setu(tag='random',type=2)->dict:
    if(type==2):
        return get_2_setu(tag=tag)
    elif(type==3):
        return get_3_setu()


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
    return pic_name

def send_2_setu(bot:Bot,event:Event,args:dict,setu:dict):
    if(setu==None):
        None_reply=msg.reply(id_=event.id)+'淦哦老兄，你的xp真**怪！建议重新搜或者换个xp！'
        try:
            asyncio.run(bot.send_msg(group_id=event.group_id,message=None_reply))
        except Exception:
            raise Exception('发送回复消息失败！')
    else:
        # 储存setu到本地
        pic_name=save_setu(setu['url'])

        try:
            
            pic_file=''
            if sys == "Windows":
                pic_file=os.getcwd()+'\pic\\'+pic_name
            elif sys == "Linux":
                pic_file=os.getcwd()+'/pic/'+pic_name
            
            pic_id="P站id:"+str(setu['id'])
            pic_tag="关键词"+args['key_word']
            
            if(args['mode']=='xml'):
                setu_reply='[CQ:cardimage,file='+'file:///'+pic_file+',source='+pic_id+' '+pic_tag+']'
                try:
                    asyncio.run(bot.send_msg(group_id=event.group_id,message=setu_reply))
                except Exception:
                    raise Exception('发送xml涩图消息失败！')
            elif(args['mode']=='pic'):
                setu_reply=msg.reply(id_=event.id)+msg.image(file='file:///'+pic_file)+pic_id+'\r\n'+pic_tag
                try:
                    asyncio.run(bot.send_msg(group_id=event.group_id,message=setu_reply))
                except Exception:
                    raise Exception('发送pic涩图消息失败！')
        finally:
            os.remove(pic_file)

def send_3_setu(bot:Bot,event:Event,args:dict,setu:dict):
    # 储存setu到本地
    pic_name=save_setu(setu['url'])

    try:
        if sys == "Windows":
            pic_file=os.getcwd()+'\pic\\'+pic_name
        elif sys == "Linux":
            pic_file=os.getcwd()+'/pic/'+pic_name
        
        if(args['mode']=='xml'):
            setu_reply='[CQ:cardimage,file='+'file:///'+pic_file+']'
            try:
                asyncio.run(bot.send_msg(group_id=event.group_id,message=setu_reply))
            except Exception:
                raise Exception('发送xml涩图消息失败！')
        elif(args['mode']=='pic'):
            setu_reply=msg.reply(id_=event.id)+msg.image(file='file:///'+pic_file)
            try:
                asyncio.run(bot.send_msg(group_id=event.group_id,message=setu_reply))
            except Exception:
                raise Exception('发送pic涩图消息失败！')
    finally:
        os.remove(pic_file)

def send_setu(bot:Bot,event:Event,args:dict,setu:dict,type:int):
    if(type==2):
        send_2_setu(bot,event,args,setu)
    elif(type==3):
        send_3_setu(bot,event,args,setu)

def setu_thread(bot:Bot,event:Event,args:dict):
    try:
        # 获取setu url
        setu=get_setu(tag=args['key_word'],type=args['type'])
        send_setu(bot,event,args,setu,args['type'])
    except Exception as e:
        error_reply=msg.reply(id_=event.id)+'info:{}'.format(e.args[0])
        asyncio.run(bot.send_msg(group_id=event.group_id,message=error_reply))

pixiv=on_command('setu',rule=to_me()&_gruop_white_list)
@pixiv.handle()
async def handle_setu(bot: Bot, event: Event, state: dict):
    args_list = str(event.message).strip().split()
    opt=['-s','-m','-3','-2','--help','--debug']
    args={
        'key_word':'random',
        'mode':'pic',
        'type':2,
        'debug':False
    }
    for arg in args_list:
        if(arg[:1]=='-'and arg not in opt):
            await pixiv.finish(msg.reply(id_=event.id)+'你输入的{}有误，请输入--help获得命令帮助'.format(arg))
    if('--debug'in args_list):
        args['debug']=True
    if('--help'in args_list):
        await  pixiv.finish(msg.reply(id_=event.id)+'-m:设置回复模式，xml/pic\r\n-s:搜索关键词，置空则为随机\r\n--debug:开启debug模式，打印更多信息')

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
            if(args_list[args_list.index('-m')+1] in ['xml','pic','3']):
                args['mode']=args_list[args_list.index('-m')+1]            
            else:
                await pixiv.finish(msg.reply(id_=event.id)+"你所输入的-m显示参数有误！\r\nxml:以xml大图发送\r\npic:以小图形式发送，默认选项\r\n")
        else:
            await pixiv.finish(msg.reply(id_=event.id)+"你所输入的-m显示参数有误！\r\nxml:以xml大图发送\r\npic:以小图形式发送，默认选项")
    if('-3' in args_list):
        args['type']=3

    await pixiv.send(msg.reply(id_=event.id)+"你的涩图正在处理，依据关键词{}".format(args['key_word']))
    threading.Thread(target=setu_thread,args=(bot,event,args)).start()

