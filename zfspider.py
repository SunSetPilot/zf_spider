import requests
from lxml import etree
import urllib
from checkcode import verify
class stu_info:
    def __init__(self, user,passwd):
        self.user = user
        self.passwd = passwd

class jwxt:
    def __init__(self,student,jwurl):
        self.student = student
        self.jwurl = jwurl
        # 使用session自动管理会话
        self.session = requests.session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0'

    def login(self):
        loginpage_content = self.session.get(self.jwurl+'/default2.aspx').content
        selector = etree.HTML(loginpage_content)
        # 获得验证码请求url
        code_src = selector.xpath('//*[@id="icode"]/@src')[0]
        code_img = self.session.get(self.jwurl+code_src, stream=True).content
        with open('code.jpg','wb') as f:
            f.write(code_img)
        __VIEWSTATE = selector.xpath('//*[@id="__VIEWSTATE"]')[0]
        __VIEWSTATEGENERATOR = selector.xpath('//*[@id="__VIEWSTATEGENERATOR"]')[0]
        code=verify('code.jpg')
        data = {
            "__LASTFOCUS": "",
            "__VIEWSTATE": __VIEWSTATE,
            "__VIEWSTATEGENERATOR": __VIEWSTATEGENERATOR,
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "txtUserName": self.student.user,
            "TextBox2": self.student.passwd,
            "txtSecretCode": code,
            "RadioButtonList1": u"学生",
            "Button1": u"登录",
        }
        loginres = self.session.post(self.jwurl, data=data, allow_redirects=True)
        selector = etree.HTML(loginres.content.decode())
        if len(selector.xpath('//*[@id="Label3"]/text()')):
            # 提取学生姓名
            name=selector.xpath('//*[@id="xhxm"]/text()')[0]
            self.stu_name_url=urllib.parse.quote(str(name[0:len(name)-2]).encode('utf-8'))
            return True
        else:
            return False

    def get_score(self):
        self.session.headers['Referer'] = self.jwurl + "/xs_main.aspx?xh=" + self.student.user
        scoreurl = self.jwurl + "/xscj_gc2.aspx?xh=" +self.student.user + "&xm=" + self.stu_name_url + "&gnmkdm=N121605"
        scorepage= self.session.get(scoreurl)
        selector = etree.HTML(scorepage.content.decode())
        __VIEWSTATE= selector.xpath('//*[@id="__VIEWSTATE"]/@value')[0]
        __VIEWSTATEGENERATOR = selector.xpath('//*[@id="__VIEWSTATEGENERATOR"]/@value')[0]
        self.session.headers['Referer']=scoreurl
        data ={
            "__VIEWSTATE": __VIEWSTATE,
            "__VIEWSTATEGENERATOR":__VIEWSTATEGENERATOR,
            "ddlXN":"",
            "ddlXQ":"",
            "Button2":u"在校学习成绩查询",
        }
        scorepage=self.session.post(scoreurl,data=data)
        selector = etree.HTML(scorepage.content.decode())
        score=[]
        for row in selector.xpath('//*[@id="Datagrid1"]//tr[td]'):
            score.append([i for i in row.itertext()][1:14])
        score=score[1:]
        self.GPA=selector.xpath('//*[@id="pjxfjd"]/text()')[0][7:]
        return score

    def get_course(self):
        self.session.headers['Referer'] = self.jwurl + "/xs_main.aspx?xh=" + self.student.user
        course_url =self.jwurl + "/xsxkqk.aspx?xh=" + self.student.user + "&xm=" + self.stu_name_url + "&gnmkdm=N121605"
        course_page = self.session.get(course_url)
        selector = etree.HTML(course_page.content.decode())
        course = []
        for row in selector.xpath('//*[@id="DBGrid"]//tr[td]'):
            course.append([i for i in row.itertext()][2:13])
        course = course[1:]
        return course

if __name__ == "__main__":
    url = "https://jwxt1.ahu.edu.cn"
    user = ""
    passwd = ""
    stu=stu_info(user,passwd)
    jw=jwxt(stu,url)
    while True:
        if jw.login():
            print("success")
            break
    print(jw.get_score())
    print(jw.GPA)