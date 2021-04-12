from bs4 import BeautifulSoup
import urllib.request
import feedparser
import re
import random
import requests
import platform
import os

from nonebot.adapters.cqhttp import Bot,Event
from nonebot.adapters.cqhttp import MessageSegment as msg
from nonebot.matcher import Matcher

from christinaqqbot.utils.reply import get_random_reply
from .model import setu


setu_tags=['萝莉','黑丝','白丝','魅魔','吸血鬼','白毛','arknights','原神','碧蓝航线','百合','红瞳','舰队Collection','JK','巨乳']
def get_2_setu(tag='random')->setu:
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
        api_url='http://www.rsshub.whitesad.xyz/95mm/tab/%E7%83%AD%E9%97%A8'
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