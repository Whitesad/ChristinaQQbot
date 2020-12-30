
import sqlite3
import os
import feedparser
import asyncio
import time

from .util import Rss,Item

def check_rss(rss:Rss)->bool:
    r=feedparser.parse(rss.url)
    new_items=[Item(rss_name=rss.name,
                    rss_id=rss.id,
                    title=item['title'],
                    link=item['link']) 
                    for item in r['entries']]

    # 与存储在数据库中的item进行比较，查看是否有更新
    coonect = sqlite3.connect('./db/rss.db')
    cursor=coonect.cursor()
    sql='SELECT * FROM items WHERE rss_id={rss_id}'.format(rss_id=rss.id)
    results=cursor.execute(sql)
    old_items=[Item(id=item[0],
                    rss_id=item[1],
                    rss_name=item[2],
                    title=item[3],
                    link=item[4]) 
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
    

    cursor.close()
    coonect.close()

    return True

def get_all_rss():
    coonect = sqlite3.connect('./db/rss.db')
    cursor=coonect.cursor()

    sql='SELECT * FROM subscribe'
    rss_results=cursor.execute(sql)
    rss_list=[]
    for rss in rss_results:
        rss=Rss(id=rss[0],name=rss[1],url=rss[2],user_id=rss[3],group_id=rss[4],type=rss[5])
        rss_list.append(rss)

    cursor.close()
    coonect.close()
    return rss_list


def rss_server():
    rss_list=get_all_rss()
    loop=asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        loop.run_until_complete(asyncio.gather([check_rss(rss) for rss in rss_list]))
        time.sleep(30)


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
                    rss_name=rss.name
                )
            cursor.execute(sql)
            connect.commit()
            return 'exist'

    # 该源还未被添加，则添加该源
    sql='INSERT INTO rss (rss_url,activate) VALUES ("{rss_url}",{activate});'.format(
        rss_url=rss.url,
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
            rss_name=rss.name
        )
    cursor.execute(sql)
    connect.commit()

    cursor.close()
    connect.close()
    return 'new'

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
            rss_name TEXT NOT NULL,
            title TEXT NOT NULL,
            link TEXT NOT NULL
            );
        ''')
        print('建立items表')
        connect.commit()

    cursor.close()
    connect.close()

    if(not os.path.exists('./db')):
        os.mkdir('./db')
    # 建立数据库
    connect=sqlite3.connect('./db/rss.db')
    cursor=connect.cursor()

    tables=cursor.execute('SELECT name FROM sqlite_master WHERE type="table" ORDER BY name;')
    exist_subscribe,exist_items=False,False
    for table in tables:
        if(table[0]=='subscribe'):
            exist_subscribe=True
        elif(table[0]=='items'):
            exist_items=True
    if(not exist_subscribe):
        # 建立订阅信息表
        # rss_name：rss的名称，rss_url：订阅链接,subscriber：订阅者，subscriber_group_id：在哪个群里订阅
        cursor.execute('''
        CREATE TABLE subscribe(
            ID INT PRIMARY KEY NOT NULL,
            rss_name TEXT NOT NULL,
            rss_url TEXT NOT NULL,
            subscriber INT NOT NULL,
            subscriber_group_id INT NOT NULL
            );
        ''')
    if(not exist_items):
        # 建立订阅信息items表
        # rss_name：订阅名称,items：rss的item
        cursor.execute('''
        CREATE TABLE items(
            ID INT PRIMARY KEY NOT NULL,
            rss_name TEXT NOT NULL,
            items TEXT NOT NULL
            );
        ''')

    cursor.close()
    connect.close()