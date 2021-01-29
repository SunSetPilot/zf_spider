#coding=utf-8
import json
import os
import requests
import zfspider
import time
from datetime import datetime
from datetime import timedelta
import pymysql
import re
from apscheduler.schedulers.background import BackgroundScheduler

# 判断配置文件是否存在
if os.path.exists('spider_data.dat'):
    # 载入配置
    with open('spider_data.dat','r') as file:
        data = json.load(file)
    user = data['user']
    passwd = data['passwd']
    url = data['url']
    num_socres = data['num_scores']
    num_course = data['num_course']
    start_week = data['start_week']
else:
    # 如果不存在则根据用户的输入初始化爬虫
    user = input("请输入教务系统用户名：")
    passwd = input("请输入教务系统密码：")
    start_week = (input("请输入第1周起始日期(YYYY-MM-DD):"))
    data = {}
    data['user'] = user
    data['passwd'] = passwd
    url = "https://jwxt1.ahu.edu.cn"
    data['url'] = url
    num_socres = 0
    data['num_scores'] = num_socres
    num_course = 0
    data['num_course'] = num_course
    data['start_week'] = start_week
    with open('spider_data.dat','w') as file:
        json.dump(data,file)

# 初始化爬虫
stu=zfspider.stu_info(user,passwd)
jw=zfspider.jwxt(stu,url)

def send_notice(Name,Teacher,Place,Time):
    # 数据库返回的是timedelta类型
    # 需要根据当前年月日+数据库返回时间+20分钟计算得正确上课时间
    _time = Time + datetime(int(time.strftime("%Y", time.localtime())),
                            int(time.strftime("%m", time.localtime())),
                            int(time.strftime("%d", time.localtime())),0,0,0) + timedelta(minutes=20)
    content = "课程名:"+Name+"\n\n授课教师:"+Teacher+"\n\n上课地点:"+Place+"\n\n上课时间:"+str(_time)
    course_data = {
        "text": "上课啦！",
        "desp":content
    }
    requests.post("https://sc.ftqq.com/****.send", data=course_data)

# 设置定时任务，每天0点设置当天的提醒
def set_notice():
    # 获得当前日期
    today = time.strftime("%Y-%m-%d", time.localtime())
    # 获得当前星期
    day_of_week = datetime.now().isoweekday()
    # 计算时间差：讲两个时间转化为秒数相减，再将结果转化为星期差
    curr_week = int((time.mktime(time.strptime(today,'%Y-%m-%d'))-time.mktime(time.strptime(start_week,'%Y-%m-%d')))/(24*60*60)//7+1)
    if curr_week % 2 != 0:
        single_week = True
    else:
        single_week = False
    db = pymysql.connect("localhost", "****", "****", "spider", autocommit=True)
    c = db.cursor()
    if single_week:
        # 如果是单周，从数据库中查询符合当前星期，且当前周在起始周与结束周范围内，且是单周或每周上课的课程
        sql = "SELECT Name,Teacher,Place,Time From course WHERE Day=%s AND Begin<=%s AND End>=%s AND (Week=1 OR Week=0);"
    else:
        # 如果是双周，从数据库中查询符合当前星期，且当前周在起始周与结束周范围内，且是双周或每周上课的课程
        sql = "SELECT Name,Teacher,Place,Time From course WHERE Day=%s AND Begin<=%s AND End>=%s AND (Week=2 OR Week=0);"
    c.execute(sql,(str(day_of_week),str(curr_week),str(curr_week)))
    results = c.fetchall()
    # 设置一次性任务
    s = BackgroundScheduler()
    for row in results:
        run_time = datetime(int(time.strftime("%Y", time.localtime())),
                            int(time.strftime("%m", time.localtime())),
                            int(time.strftime("%d", time.localtime())),0,0,0)+row[3]
        # 触发器类型为date，即一次性任务
        s.add_job(func=send_notice,args=(row[0],row[1],row[2],row[3]),trigger='date',next_run_time=run_time)
    s.start()

#设置每日定时任务
scheduler = BackgroundScheduler()
scheduler.add_job(func=set_notice, trigger='cron', hour=0,minute=1)
scheduler.start()

#循环获取教务系统成绩与课表信息
login_times = 0
while True:
    if login_times>10:
        requests.get("https://sc.ftqq.com/****.send?text=登录失败次数过多，请注意！")
    #开始登录
    try:
        status = jw.login()
    except Exception as e:
        print(e)
        login_times +=1
        time.sleep(3)
        continue
    if not status:
        print("login failed!")
        login_times += 1
        time.sleep(3)
        continue
    else:
        login_times = 0
        print("login success!")

    #更新数据库课程信息
    try:
        course = jw.get_course()
    except Exception as e:
        print(e)
        requests.get("https://sc.ftqq.com/****.send?text=登录成功但获取课程失败，请注意！")
        time.sleep(120)
        continue
    print("get course success!")
    if len(course) != num_course:
        num_course = len(course)
        data['num_course'] = num_course
        # 如果数据有更新，则更新配置文件
        with open('spider_data.dat', 'w') as file:
            json.dump(data, file)
        db = pymysql.connect("localhost", "****", "****", "spider",autocommit=True)
        c = db.cursor()
        c.execute("TRUNCATE TABLE course;")
        # 逐行解析爬虫返回的数据
        for row in course:
            course_id = row[0]
            course_name = row[1]
            course_teacher = row[4]
            # 有时会存在一门课有多个上课时间的情况，但中间的分隔符都是分号，所以可以用split隔开多个时间段
            # 数据库里存放的是每一门课最小的时间单位
            course_time = row[8].split(';')
            course_place = row[10].split(';')
            # 因为每一个上课时间段和上课地点都是对应的，两个列表长度相等，所以可以同时遍历两个列表
            for (i, j) in zip(course_time, course_place):
                # 汉字转换数字
                hz_to_di = {
                    '一': '1', '二': '2', '三': '3', '四': '4', '五': '5', '六': '6', '日': '7',
                }
                course_day = hz_to_di[re.findall("周(.)第", i)[0]]
                # 根据节次选择对应的上课时间
                # 存入数据库中的时间比正常时间提前了20分钟，方便设置定时器
                di_to_time = {
                    '1': '08:00:00', '2': '08:55:00', '3': '10:00:00', '4': '10:55:00', '5': '13:40:00',
                    '6': '14:35:00', '7': '15:30:00', '8': '16:25:00', '9': '18:40:00', '10': '19:35:00',
                    '11': '20:30:00'
                }
                course_time_2 = di_to_time[re.findall("第(.).*节", i)[0]]
                course_begin = re.findall("{第(.*)-", i)[0]
                # 加split的原因是如果后面跟了 |单周 或者是 |双周 这样的话，会往后多匹配两个字符
                course_end = re.findall("-(.*)周}", i)[0].split('周')[0]
                if "单周" in i:
                    course_week = '1'
                elif "双周" in i:
                    course_week = '2'
                else:
                    course_week = '0'
                sql = "INSERT INTO course VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);"
                c.execute(sql, (course_id, course_name, course_teacher, j, course_day, course_begin, course_end, course_week,course_time_2))
        c.close()
        db.close()

    #获取成绩
    try:
        score = jw.get_score()
    except Exception as e:
        print(e)
        requests.get("https://sc.ftqq.com/****.send?text=登录成功但获取成绩失败，请注意！")
        time.sleep(120)
        continue
    print("get score success!")

    #推送成绩信息到微信
    if len(score)!=num_socres:
        num_socres = len(score)
        data['num_scores'] = num_socres
        with open('spider_data.dat', 'w') as file:
            json.dump(data, file)
        desp = "更新时间："+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"\n\nGPA："+jw.GPA+"\n\n课程名    学分    成绩    绩点\n\n"
        for list in score:
            desp += list[3]+"    "+list[6]+"    "+list[8]+"    "+list[7]+"\n\n"
        score_data={
            "text":"成绩已更新 ",
            "desp":desp
        }
        requests.post("https://sc.ftqq.com/****.send",data=score_data)
    # 每隔1小时更新一次
    time.sleep(3600)
