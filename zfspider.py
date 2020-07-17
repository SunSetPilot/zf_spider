import requests
from checkcode import verify
from lxml import etree
from imp import reload
import sys
import urllib

class stu_info:
    def __init__(self, user,passwd):
        self.user = user
        self.passwd = passwd

class jwxt:
    def __init__(self,student,jwurl):
        reload(sys)
        self.student = student
        self.jwurl = jwurl
        self.session = requests.session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0'

    def login(self):
        loginpage_content = self.session.get(self.jwurl+'/default2.aspx').content;
        code_img = self.session.get(self.jwurl+'/CheckCode.aspx', stream=True).content
        with open('code.jpg','wb') as f:
            f.write(code_img)
        selector = etree.HTML(loginpage_content)
        __VIEWSTATE = selector.xpath('//form[@id="form1"]//input[@name="__VIEWSTATE"]/@value')[0]
        __VIEWSTATEGENERATOR = selector.xpath('//form[@id="form1"]//input[@name="__VIEWSTATEGENERATOR"]/@value')[0]
        RadioButtonList1 = u"学生"
        Button1 = u"登录"
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
            "RadioButtonList1": RadioButtonList1,
            "Button1": Button1,
        }
        loginres = self.session.post(self.jwurl, data=data, allow_redirects=True)
        selector = etree.HTML(loginres.content.decode())
        if len(selector.xpath('//*[@id="Label3"]/text()')):
            self.session.headers['Referer'] = self.jwurl + "/xs_main.aspx?xh=" + self.student.user
            stu_info_url =  self.jwurl + "/xsgrxx.aspx?xh=" + self.student.user
            stu_info_page = self.session.get(stu_info_url)
            selector = etree.HTML(stu_info_page.content.decode())
            self.stu_name=selector.xpath('//*[@id="xm"]/text()')[0]
            self.stu_name_url=urllib.parse.quote(str(self.stu_name).encode('utf-8'))
            return True
        else:
            return False

    def get_score(self):
        self.session.headers['Referer'] = self.jwurl + "/xs_main.aspx?xh=" + self.student.user
        scoreurl = self.jwurl + "/xscjcx.aspx?xh=" +self.student.user + "&xm=" + self.stu_name_url + "&gnmkdm=N121605"
        scorepage= self.session.get(scoreurl)
        selector = etree.HTML(scorepage.content.decode())
        __VIEWSTATE= selector.xpath('//*[@id="__VIEWSTATE"]/@value')[0]
        __VIEWSTATEGENERATOR = selector.xpath('//*[@id="__VIEWSTATEGENERATOR"]/@value')[0]
        self.session.headers['Referer']=scoreurl
        data ={
            "_EVENTTARGET":"",
            "__EVENTARGUMENT":"",
            "__VIEWSTATE": __VIEWSTATE,
            "__VIEWSTATEGENERATOR":__VIEWSTATEGENERATOR,
            "ddlXN":"",
            "ddlXQ":"",
            "ddl_kcxz":"",
            "btn_zcj":u"历年成绩",
            "hidLanguage":""
        }
        scorepage=self.session.post(scoreurl,data=data)
        selector = etree.HTML(scorepage.content.decode())
        score=[]
        for row in selector.xpath('//*[@id="Datagrid1"]//tr[td]'):
            score.append([i for i in row.itertext()][1:14])
        score=score[1:]
        return score

    def get_GPA(self):
        self.session.headers['Referer'] = self.jwurl + "/xs_main.aspx?xh=" + self.student.user
        scoreurl = self.jwurl + "/xscjcx.aspx?xh=" + self.student.user + "&xm=" + self.stu_name_url + "&gnmkdm=N121605"
        scorepage = self.session.get(scoreurl)
        selector = etree.HTML(scorepage.content.decode())
        __VIEWSTATE = selector.xpath('//*[@id="__VIEWSTATE"]/@value')[0]
        __VIEWSTATEGENERATOR = selector.xpath('//*[@id="__VIEWSTATEGENERATOR"]/@value')[0]
        self.session.headers['Referer'] = scoreurl
        data = {
            "_EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": __VIEWSTATE,
            "__VIEWSTATEGENERATOR": __VIEWSTATEGENERATOR,
            "ddlXN": "",
            "ddlXQ": "",
            "ddl_kcxz": "",
            "Button1": u"成绩统计",
            "hidLanguage": ""
        }
        scorepage = self.session.post(scoreurl, data=data)
        selector = etree.HTML(scorepage.content.decode())
        GPA =  selector.xpath('//*[@id="pjxfjd"]/text()')[0][11:]
        return GPA

if __name__ == "__main__":
    url = "https://jwxt0.ahu.edu.cn"
    user = "Y01814243"
    passwd = "ahu2018wzj813"
    stu=stu_info(user,passwd)
    jw=jwxt(stu,url)
    jw.login()
    jw.get_GPA()