import os
from unittest import TestCase
from spider import spider_main
import wtf
from flask import Flask, render_template, request
import sqlite3
import jieba  # 分词
from wordcloud import WordCloud  # 词云
from matplotlib import pyplot as plt  # 绘图
from PIL import Image  # 图片处理
import numpy as np  # 矩阵运算

app = Flask(__name__)


# 路由解析，通过用户访问的路径，匹配相应的函数

@app.route('/')
def index():
    if os.path.exists(r'.\comment.db'):
        return render_template("index.html")
    else:
        spider_main()
    return render_template("index.html")


@app.route('/index')  # 首页
def home():
    return index()


@app.route('/comment')  # 热评展示页
def comment():
    datalist = []
    conn = sqlite3.connect("comment.db")
    cursor = conn.cursor()
    sql = "select id,username,vip,message,ctime,likenum from hotComment"
    data = cursor.execute(sql)
    for item in data:
        datalist.append(item)
    cursor.close()
    conn.close()
    return render_template("comment.html", comments=datalist, comments_num=len(datalist))


@app.route('/analysis')  # 用户分析页
def analysis():
    account = []  # 官方号名称
    num = []  # 官方号点赞数量
    users = []  # 热评用户名
    user_num = []  # 热评用户数
    comment_time = []  # 评论时间段
    comment_num = []  # 评论数量
    level_num = []  # 账号数量
    vip_num = []  # 会员数量
    conn = sqlite3.connect("comment.db")
    cursor = conn.cursor()
    # sql语句执行统计官方号的数量，按官方号名称分组并显示官方名称
    sql = """
    select username,likenum from hotComment where official_verify like '%官方账号' 
    group by official_verify order by likenum desc
    """
    # 选择用户名与点赞量，降序排列
    sql1 = """
        select username,likenum from hotComment order by likenum desc
    """
    # 统计出同一时间段（小时内）发表的评论数
    sql2 = """
        select substr(ctime,1,13),count(substr(ctime,1,13))from hotComment group by substr(ctime,1,13)
    """

    # 统计各等级账号人数
    sql3 = """
        select  levelinfo,count(username) from hotComment group by levelinfo
    """
    #统计各vip类型数量
    sql4 = """
        select vip,count(vip) from hotComment group by vip
    """

    official_data = cursor.execute(sql)

    for item in official_data:
        # print(type(item[0]))
        # print(item[0])
        account.append(item[0])
        num.append(item[1])

    cursor1 = conn.cursor()
    likenum_data = cursor1.execute(sql1)
    for item in likenum_data:
        users.append(item[0])
        user_num.append(item[1])
    # print(users)
    # print(account)

    cursor2 = conn.cursor()
    comment_data = cursor2.execute(sql2)
    for item in comment_data:
        comment_time.append(item[0])
        comment_num.append(item[1])
    print(comment_data)

    cursor3 = conn.cursor()
    level_data = cursor3.execute(sql3)
    for item in level_data:
        level_num.append(item[1])

    cursor4 = conn.cursor()
    vip_data = cursor.execute(sql4)
    for item in vip_data:
        vip_num.append(item[1])

    # 切片 划分出前十个传入后台
    account = account[1:11]
    num = num[1:11]
    users = users[1:11]
    user_num = user_num[1:11]

    comment_time = comment_time[1:24]
    comment_num = comment_num[1:24]

    cursor.close()
    conn.close()
    return render_template("analysis.html", account=account, num=num, users=users,
                           user_num=user_num, comment_time=comment_time, comment_num=comment_num,
                           level_num=level_num, vip_num=vip_num)


@app.route('/wordcloud')  # 词云页
def wordcloud():
    if os.path.exists(r'.\static\assets\img\word.png'):
        # 判断本地是否已存在 images 文件夹，有的话直接开始下载，没有创建一个
        print("当前目录下已存在词云图片....")
    else:
        conn = sqlite3.connect("comment.db")
        cursor = conn.cursor()
        sql = "select distinct message from hotComment"
        #distinct关键字可查找唯一的记录，过滤重复数据
        data = cursor.execute(sql)
        text = ""
        for item in data:
            text = text + item[0]
        print(text)
        cursor.close()
        conn.close()

        # 分词
        cut = jieba.cut(text)
        string = ' '.join(cut)
        print(len(string))

        img = Image.open(r'.\static\assets\img\wordbg.jpg')  # 打开遮罩图片
        img_array = np.array(img)
        word_cloud = WordCloud(background_color='white', mask=img_array, font_path="msyh.ttc")
        word_cloud.generate_from_text(string)

        # 绘制图片
        fig = plt.figure(1)
        plt.imshow(word_cloud)
        plt.axis("off")
        # plt.show()
        plt.savefig(r'.\static\assets\img\word.png', dpi=500)

    return render_template("wordcloud.html")


@app.route('/team')  # 团队介绍页
def team():
    return render_template("team.html")

if __name__ == '__main__':
    app.run()
