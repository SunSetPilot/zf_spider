# zf_spider
python实现正方教务系统成绩爬虫，当有新成绩时自动推送通知

checkcode.py 验证码识别模块，采用CNN训练的模型
zfspider.py 爬虫模块，登录教务系统，爬取成绩和GPA
main.py 每隔半小时自动登录正方教务系统查询是否有成绩更新，若有，则发送微信通知


使用方法：
在main.py中填写学号，密码和教务系统网址
https://sc.ftqq.com 申请接口，将申请到的key填入

基于python3.6编写，需要的运行库
tensorflow==1.7.0rc1
Keras==2.1.5
Pillow==5.0.0
h5py==2.8.0
requests

v2.0更新日志
1.将用户数据保存在配置文件中
2.将爬取到的数据保存到数据库中
3.增加定时提醒上课功能
