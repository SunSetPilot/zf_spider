import requests
import zfspider
from time import sleep
import time

user = "" #学号
passwd = "" #密码
url = "https://jwxt2.ahu.edu.cn" #学校教务系统地址
stu=zfspider.stu_info(user,passwd)
jw=zfspider.jwxt(stu,url)

NumOfScore = 0

while True:
    status = jw.login()
    while status == False:
        sleep(3)
        status = jw.login()
    score = jw.get_score()
    GPA = jw.get_GPA()
    if len(score)!=NumOfScore:
        NumOfScore = len(score)
        desp = "更新时间："+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"\n\nGPA："+GPA+"\n\n课程名    学分    成绩    绩点\n\n"
        for list in score:
            desp= desp+list[3]+"    "+list[6]+"    "+list[8]+"    "+list[7]+"\n\n"
        data={
            "text":"成绩已更新 ",
            "desp":desp
        }
        requests.post("https://sc.ftqq.com/*.send",data=data) #微信消息接口 https://sc.ftqq.com
    sleep(1800)
