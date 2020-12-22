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

from christinaqqbot.utils.reply import *
from christinaqqbot.utils.rule import  _gruop_white_list

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
        raise Exception("setu api访问错误！\r\n你的涩图炸了，你可以尝试再来一张。")
    
    result_dict=json.loads(r.text)
    if('data' in result_dict.keys()):
        result=result_dict['data'][random.randint(0,len(result_dict['data']))]
        return {
            'title':result['title'],
            'id':result['id'],
            'artistId':result['artistId'],
            'urls':result['imageUrls'][0]
        }
    else:
        return None


def save_setu(id):
    pic_url='https://pixiv.cat/%s.jpg'%id
    try:
        r=requests.get(url=pic_url)
        if(r.status_code==404):
            if('需要指定'in r.text):
                pic_url='https://pixiv.cat/%s-1.jpg'%id
                r=requests.get(url=pic_url)
            else:
                raise Exception("服务器转存遇到无法转存的图片！\r\n你的涩图炸了，你可以尝试再来一张。")
    except Exception:
        raise Exception("服务器转存请求图片错误！\r\n你的涩图炸了，你可以尝试再来一张。")
    try:
        pic_name=pic_url.split('/')[-1]
        if(not os.path.exists('./pic')):
            os.mkdir('./pic')
        with open('./pic/'+pic_name,'wb')as f:
            f.write(r.content)
            f.close()
    except Exception:
        raise Exception("服务器转存储存图片错误！\r\n你的涩图炸了，你可以尝试再来一张。")
    return pic_name


def setu_thread(bot:Bot,event:Event,args:dict):
    try:
        # 三个debug模式下用来计时的变量
        setu_time=time.time()
        save_time=time.time()
        send_time=time.time()

        # 获取setu url
        setu=get_setu(tag=args['key_word'])
        setu_time=time.time()-setu_time

        if(setu==None):
            None_reply=msg.reply(id_=event.id)+'淦哦老兄，你的xp真**怪！建议重新搜或者换个xp！'
            try:
                asyncio.run(bot.send_msg(group_id=event.group_id,message=None_reply))
            except Exception:
                raise Exception('发送回复消息失败！')
        else:
            # 储存setu到本地
            save_time=time.time()
            pic_name=save_setu(setu['id'])
            save_time=time.time()-save_time

            try:
                sys = platform.system()
                pic_file=''
                if sys == "Windows":
                    pic_file=os.getcwd()+'\pic\\'+pic_name
                elif sys == "Linux":
                    pic_file=os.getcwd()+'/pic/'+pic_name
                
                pic_id="P站id:"+str(setu['id'])
                pic_tag="关键词"+args['key_word']
                send_time=time.time()
                
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
                

                send_time=time.time()-send_time
            finally:
                os.remove(pic_file)
        if(args['debug']):
            try:
                reply=msg.reply(id_=event.id)+"api request时间:{:.2f}s\r\npic request时间:{:.2f}s\r\nsend message时间{:.2f}s".format(setu_time,save_time,send_time)
                asyncio.run(bot.send_msg(group_id=event.group_id,message=reply))
            except Exception:
                raise Exception('发送debug消息失败！')

    except Exception as e:
        error_reply=msg.reply(id_=event.id)+'info:{}'.format(e.args[0])
        asyncio.run(bot.send_msg(group_id=event.group_id,message=error_reply))

pixiv=on_command('setu',rule=to_me()&_gruop_white_list)
@pixiv.handle()
async def handle_setu(bot: Bot, event: Event, state: dict):
    args_list = str(event.message).strip().split()
    opt=['-s','-m','--help','--debug']
    args={
        'key_word':'random',
        'mode':'pic',
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
            if(args_list[args_list.index('-m')+1] in ['xml','pic']):
                args['mode']=args_list[args_list.index('-m')+1]            
            else:
                await pixiv.finish(msg.reply(id_=event.id)+"你所输入的-m显示参数有误！\r\nxml:以xml大图发送\r\npic:以小图形式发送，默认选项\r\n")
        else:
            await pixiv.finish(msg.reply(id_=event.id)+"你所输入的-m显示参数有误！\r\nxml:以xml大图发送\r\npic:以小图形式发送，默认选项")
    
    await pixiv.send(msg.reply(id_=event.id)+"你的涩图正在处理，依据关键词{}".format(args['key_word']))
    threading.Thread(target=setu_thread,args=(bot,event,args)).start()

