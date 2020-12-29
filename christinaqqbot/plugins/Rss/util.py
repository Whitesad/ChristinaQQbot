
import sqlite3
import os

class Rss:
    def __init__(self,
            name,
            url:str,
            user_id:int,
            type:str,
            group_id:int
    ):
        self.name=name
        self.url=url
        self.user_id=user_id
        self.type=type
        self.group_id=group_id


def add_rss(rss:Rss):
    connect=sqlite3.connect('./db/rss.db')
    cursor=connect.cursor()

    sql='INSERT INTO subscribe (rss_name,rss_url,subscriber,subscriber_group_id,subscribe_type) \
        VALUES ("{rss_name}","{rss_url}",{subscriber},{subscriber_group_id},"{subscribe_type}");'.format(
            rss_name=rss.name,
            rss_url=rss.url,
            subscriber=rss.user_id,
            subscriber_group_id=rss.group_id,
            subscribe_type=rss.type
        )
    print(sql)
    cursor.execute(sql)
    connect.commit()

    cursor.close()
    connect.close()

def rss_db_init():
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