from nonebot.adapters.cqhttp import Bot
from nonebot import get_bots
from nonebot.adapters.cqhttp import MessageSegment as msg

import sqlite3
import os
import feedparser
import asyncio
import time
import requests

from .model import Rss,Item

def check_rss(rss_url:str)->str:
    try:
        r=requests.get(rss_url)
        r=feedparser.parse(r.text)
        if('entries' in r.keys()):
            return r['feed']['subtitle']
        else:
            return ''
    except Exception:
        return ''

async def update_rss(rss:Rss,mode='init'):
    try:
        connect = sqlite3.connect('./db/rss.db')
        cursor=connect.cursor()
        if(mode=='init'):
            results=cursor.execute('SELECT * FROM rss WHERE rss_url="{rss_url}"'.format(rss_url=rss.url))
            results=[result for result in results]
            rss.id=results[0][0]
        
        r=requests.get(rss.url)
        r=feedparser.parse(r.text)
        new_items=[Item(rss_id=rss.id,
                        title=item['title'],
                        link=item['link']
                        )
                        for item in r['entries']]

        # 与存储在数据库中的item进行比较，查看是否有更新
        sql='SELECT * FROM items WHERE rss_id={rss_id}'.format(rss_id=rss.id)
        results=cursor.execute(sql)
        old_items=[Item(rss_id=item[0],
                        id=item[1],
                        title=item[2],
                        link=item[3]) 
                        for item in results]

        update_items=[]
        for new_item in new_items:
            is_update=True
            for old_item in old_items:
                if(old_item.title==new_item.title and old_item.link==new_item.link):
                    is_update=False
                    break
            if(is_update):
                update_items.append(new_item)
        
        if(len(update_items)>=1):
            for item in update_items:
                sql='INSERT INTO items (rss_id,title,link) VALUES({rss_id},"{title}","{link}");'.format(
                    rss_id=item.rss_id,
                    title=item.title.replace('"','""'),
                    link=item.link
                )
                cursor.execute(sql)
            connect.commit()
            if(mode=='update'):
                bots = get_bots()
                bot=None
                for id in bots.keys():
                    bot=bots[id]
                subscribres=cursor.execute('SELECT * FROM subscribe WHERE rss_id={rss_id}'.format(rss_id=rss.id))
                for update in update_items:
                    for subscribre in subscribres:
                        reply=msg.at(user_id=subscribre[1])
                        reply=reply+'您所订阅的{rss_name}更新了\r\ntitle:{title}\r\nurl:{url}'.format(
                            rss_name=subscribre[5],
                            title= update.title,
                            url=update.link
                        )
                        await bot.send_group_msg(group_id=subscribre[2],message=reply)
    except Exception as e:
        print('rss {name}更新失败!'.format(name=rss.name))
        raise Exception(e.args[0])
    finally:
        cursor.close()
        connect.close()


def get_all_rss():
    try:
        connect = sqlite3.connect('./db/rss.db')
        cursor=connect.cursor()

        sql='SELECT * FROM rss'
        rss_results=cursor.execute(sql)
        rss_results=[result for result in rss_results]
        rss_list=[]
        for rss in rss_results:
            if(rss[3]):#如果是激活的rss
                rss_info=cursor.execute('SELECT * FROM subscribe WHERE rss_id={id}'.format(id=rss[0]))
                rss_info=[info for info in rss_info][0]
                rss=Rss(id=rss[0],url=rss[1],describe=rss[2],activate=rss[3],name=rss_info[5])
                rss_list.append(rss)
        return rss_list
    finally:
        cursor.close()
        connect.close()

def rss_server():
    print('rss进程开启！')
    loop=asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    time.sleep(10)
    while True:
        time.sleep(1)
        rss_list=get_all_rss()
        if(len(rss_list)>=1):
            try:
                tasks=[]
                for rss in rss_list:
                    if(rss.activate):
                        tasks.append(update_rss(rss=rss,mode='update'))
                if(len(tasks)>0):
                    loop.run_until_complete(asyncio.gather(*tasks))
                    print('成功更新rss')
                    time.sleep(10)
            except Exception as e:
                print('更新rss错误!info:%s'%e.args[0])
                time.sleep(1)

def add_rss(rss:Rss)->str:
    connect=sqlite3.connect('./db/rss.db')
    cursor=connect.cursor()

    rss_rows=cursor.execute('SELECT * FROM rss WHERE rss_url="{rss_url}"'.format(rss_url=rss.url))
    rss_rows=[row for row in rss_rows]
    # 如果查询结果存在，则说明已经存在该rss源
    if(len(rss_rows)>=1):
        # 依据查询出来的rss_id来确定该用户是否已经订阅过该源
        subscibe_rows=cursor.execute('SELECT * FROM subscribe WHERE rss_id={rss_id} AND subscriber={subscriber}'.format(
                                    rss_id=rss_rows[0][0],
                                    subscriber=rss.user_id))
        subscibe_rows=[row for row in subscibe_rows]
        if(len(subscibe_rows)>=1):
            return 'repeat'
        # 该用户没订阅该源，则使用该源
        else:
            sql='INSERT INTO subscribe (subscriber,subscriber_group_id,subscribe_type,rss_id,rss_name) \
                VALUES ({subscriber},{subscriber_group_id},"{subscribe_type}",{rss_id},"{rss_name}");'.format(
                    subscriber=rss.user_id,
                    subscriber_group_id=rss.group_id,
                    subscribe_type=rss.type,
                    rss_id=rss_rows[0][0],
                    rss_name=rss.name.replace('"','""')
                )
            cursor.execute(sql)
            connect.commit()
            # 标记该rss激活
            sql='UPDATE rss SET activate = 1 WHERE rss_id={rss_id}'.format(rss_id=rss_rows[0][0])
            cursor.execute(sql)
            connect.commit()
            return 'exist'

    # 该源还未被添加，则添加该源
    sql='INSERT INTO rss (rss_url,describe,activate) VALUES ("{rss_url}","{describe}",{activate});'.format(
        rss_url=rss.url,
        describe=rss.describe.replace('"','""'),
        activate=1
    )
    cursor.execute(sql)
    connect.commit()
    rows=cursor.execute('SELECT * FROM rss WHERE rss_url="{rss_url}"'.format(rss_url=rss.url))
    rows=[row for row in rows]
    sql='INSERT INTO subscribe (subscriber,subscriber_group_id,subscribe_type,rss_id,rss_name) \
        VALUES ({subscriber},{subscriber_group_id},"{subscribe_type}",{rss_id},"{rss_name}");'.format(
            subscriber=rss.user_id,
            subscriber_group_id=rss.group_id,
            subscribe_type=rss.type,
            rss_id=rows[0][0],
            rss_name=rss.name.replace('"','""')
        )
    cursor.execute(sql)
    connect.commit()

    cursor.close()
    connect.close()
    return 'new'

def query_user_rss(user_id:int)->[]:
    try:
        connect = sqlite3.connect('./db/rss.db')
        cursor=connect.cursor()

        sql='SELECT * FROM subscribe WHERE subscriber={subscriber}'.format(
            subscriber=user_id
        )
        results=cursor.execute(sql)
        results=[result for result in results]
        for i in range(len(results)):
            sql='SELECT * FROM rss WHERE rss_id={rss_id};'.format(rss_id=results[i][4])
            rss=cursor.execute(sql)
            rss=[r for r in rss]
            result=results[i]
            result=[r for r in result]
            result.append(rss[0][1])
            results[i]=result

        return results
    finally:
            cursor.close()
            connect.close()

def remove_rss(subscibe_id,user_id):
    try:
        connect = sqlite3.connect('./db/rss.db')
        cursor=connect.cursor()
        sql='SELECT * FROM subscribe WHERE ID={id}'.format(
            id=subscibe_id
        )
        results=cursor.execute(sql)
        results=[result for result in results]
        rss_id=results[0][4]
        if(len(results)<=0):
            return 'none'
        elif(results[0][1]!=user_id):
            return 'no_permission'
        else:
            sql='DELETE FROM subscribe WHERE ID={id}'.format(id=subscibe_id)
            cursor.execute(sql)
            connect.commit()
            results=cursor.execute('SELECT * FROM subscribe WHERE rss_id={rss_id}'.format(rss_id=rss_id))
            results=[result for result in results]
            # 如果删除该条记录使得此rss无用户使用，则将其标为不激活状态
            if(len(results)<=0):
                cursor.execute('UPDATE rss SET activate=0 WHERE rss_id={rss_id}'.format(rss_id=rss_id))
                connect.commit()
            return 'success'
    except Exception:
        return 'error'
    finally:
        cursor.close()
        connect.close()

def rss_db_init():
    if(not os.path.exists('./db')):
        os.mkdir('./db')
    # 建立数据库
    connect=sqlite3.connect('./db/rss.db')
    cursor=connect.cursor()

    tables=cursor.execute('SELECT name FROM sqlite_master WHERE type="table" ORDER BY name;')
    exist_subscribe,exist_items,exist_rss=False,False,False
    for table in tables:
        if(table[0]=='subscribe'):
            exist_subscribe=True
        elif(table[0]=='items'):
            exist_items=True
        elif(table[0]=='rss'):
            exist_rss=True
    if(not exist_subscribe):
        # 建立订阅信息表
        # rss_name：rss的名称，rss_url：订阅链接,subscriber：订阅者，subscriber_group_id：在哪个群里订阅
        cursor.execute('''
        CREATE TABLE subscribe(
            ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,
            subscriber INT NOT NULL,
            subscriber_group_id INT NOT NULL,
            subscribe_type VARCHAR(32) NOT NULL,
            rss_id INT NOT NULL,
            rss_name TEXT NOT NULL
            );
        ''')
        print('建立subscribe表')
        connect.commit()
    if(not exist_rss):
        # 建立订阅信息表
        # rss_name：rss的名称，rss_url：订阅链接,subscriber：订阅者，subscriber_group_id：在哪个群里订阅
        cursor.execute('''
        CREATE TABLE rss(
            rss_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,
            rss_url TEXT NOT NULL,
            describe TEXT NOT NULL,
            activate BOOLEAN DEFAULT 1
            );
        ''')
        print('建立rss表')
        connect.commit()
    if(not exist_items):
        # 建立订阅信息items表
        # rss_name：订阅名称,items：rss的item
        cursor.execute('''
        CREATE TABLE items(
            item_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            rss_id INT NOT NULL,
            title TEXT NOT NULL,
            link TEXT NOT NULL
            );
        ''')
        print('建立items表')
        connect.commit()

    cursor.close()
    connect.close()