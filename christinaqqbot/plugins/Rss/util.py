
import sqlite3
import os


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