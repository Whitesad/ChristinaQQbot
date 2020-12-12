from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters.cqhttp import Bot,Event,MessageSegment
import requests
import lxml
from  bs4 import BeautifulSoup
import json

def parse_dmzj(html:str)->[]:
    start=html.find('{',0)
    if(start==-1):
        return None
    end=html.find('}',start)
    dic=json.loads(html[start:end+1])
    return {
        'src':'动漫之家',
        'picurl':dic['cover'],
        'comic_author':dic['comic_author'],
        'comic_newPage':dic['last_update_chapter_name'],
        'comic_name':dic['comic_name'],
        'comic_url':dic['comic_url'][2:],
    }

def parse_manhuadui(li)->{}:
    if(len(li)<=0):
        return None
    # 索引0是为了只要第一个结果
    all_a=li[0].findAll('a')
    pic_url=all_a[0].next.attrs['src']
    comic_url=all_a[1].attrs['href']
    comic_title=all_a[1].attrs['title']
    comic_author=li[0].find(class_='auth').contents[0]
    comic_newPage=li[0].find(class_='newPage').contents[0]
    return {
        'src':'漫画堆',
        'picurl':pic_url,
        'comic_author':comic_author,
        'comic_newPage':comic_newPage,
        'comic_name':comic_title,
        'comic_url':comic_url,
    }


def search_comic(comic_name:str)->None:
    dmzj_url='https://sacg.dmzj.com/comicsum/search.php'
    manhuadui_url='https://www.manhuadai.com/search/'

    dmzj_r=requests.get(url=dmzj_url,params={'s':comic_name})
    dmzj_result=parse_dmzj(dmzj_r.text)

    manhuadui_r=requests.get(url=manhuadui_url,params={'keywords':comic_name})
    manhuadui_soup=BeautifulSoup(manhuadui_r.text,'lxml')
    manhuadui_result=parse_manhuadui(manhuadui_soup.find_all(class_='list-comic')) 
    
    return [dmzj_result,manhuadui_result]


rss=on_command('search',rule=to_me())

@rss.handle()
async def _(bot: Bot, event: Event, state: dict)->None:
    args = str(event.message).strip()
    results=search_comic(args)
    reply=MessageSegment.reply(id_=event.id)
    for result in results:
        if(result==None):
            continue
        reply+=MessageSegment.image(file=result['picurl'])+"\r\n"
        reply=reply+result['comic_name']+"\r\n"+result['comic_url']+"\r\n"
        reply=reply+"作者:"+result['comic_author']+"\r\n"
        reply=reply+"最新话："+result['comic_newPage']+"\r\n"
        reply=reply+"搜索来源:"+result['src']
    await bot.send_msg(group_id=event.group_id,message=reply)