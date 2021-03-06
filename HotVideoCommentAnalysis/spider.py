import requests
import urllib.request
from bs4 import BeautifulSoup
import re
import xlwt
import sqlite3
import json
import time

baseURL = "https://api.bilibili.com/x/v2/reply?callback=jQueryjsonp=jsonp&pn=1&type=1&oid=541189458&sort=2&_=1594691657406"


def spider_main():
    datalist = []
    datalist = askURL(baseURL)  # 获取网页数据

    dbpath = "comment.db"
    saveData2DB(datalist, dbpath)
    print(len(datalist))

# 访问链接
def askURL(url):
    data = ""
    datalist = []
    dataset = set()
    head = {  # 模拟浏览器头部信息
        "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.61"
    }
    try:
        for i in range(1, 550):
            r = requests.get(url.replace("pn=1", "pn=%d" % i))
            data = json.loads(r.text)

            replies = data['data']

            for reply in replies.get('replies'):
                print(reply)
                datalist.append(reply)
                # print(data['data']['replies'])
        # for item in datalist:
        #     print(item)


    except Exception as e:
        print(e)
    return datalist



# 保存数据到数据库
def saveData2DB(datalist, dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()

    for data in datalist:
        uid = '"' + data['member']['mid'] + '"'
        username = '"' + data['member']['uname'] + '"'
        gender = '"' + data['member']['sex'] + '"'
        sign = '"' + (data['member']['sign']).replace('"', "") + '"'
        official_verify = '"' + data['member']['official_verify']['desc'] + '"'
        levelinfo = '"' + str(data['member']['level_info']['current_level']) + '"'
        vip = '"' + data['member']['vip']['label']['text'] + '"'
        ctime = '"' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data['ctime'])) + '"'
        message = '"' + data['content']['message'] + '"'
        likenum = '"' + str(data['like']) + '"'
        # print(uid, username, gender, sign, levelinfo, vip, message, likenum, end=" ")

        sql = """
            insert into hotComment(uid,username,gender,sign,official_verify,levelinfo,vip,ctime,message,likenum)
            values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""" % (
        uid, username, gender, sign, official_verify, levelinfo, vip, ctime, message, likenum)
        print(sql)
        try:
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            print(e)
    sql2 = """
        delete from hotComment where message in (select * from hotComment group by message having count (message) > 1)
        and id not in (select min(id) from people group by message having count(message)>1)
    """
    #查找并删除重复数据
    try:
        cursor.excute(sql2)
        conn.commit()
    except Exception as e:
        print(e)
    cursor.close()
    conn.close()


def init_db(dbpath):
    sql = """
        create table hotComment 
        (
        id INTEGER primary key autoincrement,
        uid INTEGER,
        username varchar,
        gender varchar,
        sign varchar,
        official_verify varchar,
        levelinfo varchar,
        vip varchar,
        ctime text,
        message text,
        likenum numeric 
        )
    """
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    spider_main()
    print("爬取完毕")
