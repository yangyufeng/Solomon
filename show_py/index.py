
#!/usr/bin python
# -*-coding:utf-8 -*-
#index.py
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from datetime import *
from json import dumps

import MySQLdb
import requests
from lxml import etree

from flask import Flask


app = Flask(__name__)

app.config.update(
	DEBUG = False,
)

#路径例子
@app.route('/user/<username>')
def show_user_profile(username): 
	# show the user profile for that user 
	return 'User %s' % username

#data operation
def getSaveTime(cur,origin):
	#select * from chairmansSaveTime where origin = 'tencent_video' order by id desc limit 2;
	sql = "select inserttime from chairmansSaveTime where origin = '%s' order by id desc limit 2"%(origin)
	count = cur.execute(sql)
	cur.scroll(0,mode='absolute')
	#获取所有结果
	results = cur.fetchall()
	return results

def getNewsByTime(cur,origin,time1,time2):
	#print time2
	#print time1
	sql = "select keyword,title,description,url,origin,pubtime from chairmansNews where datatime between '%s' and '%s' and origin = '%s'"%(time2,time1,origin)
	count = cur.execute(sql)
	cur.scroll(0,mode='absolute')
	#获取所有结果
	results = cur.fetchall()
	return results	

#mysql中datetime在python中字符串化
def json_date(obj):
	"""JSON serializer for objects not serializable by default json code"""
	if isinstance(obj, date):
		serial = obj.isoformat()
		return serial
	raise TypeError ("Type not serializable")

@app.route('/showVideos/<origin>')
def showTencentVideo(origin):
	#接库
	conn= MySQLdb.connect(
						host='localhost',
						port = 3306,
						user='root',
						passwd='1',
						db ='company',
						charset='utf8',
						)
	cur = conn.cursor()

	#获取最新两条时间
	arrTime = []
	resSaveTime = getSaveTime(cur,origin)

	for rSaveName in resSaveTime:
		arrTime.append(rSaveName[0]) 

	time1 = arrTime[0]
	time2 = arrTime[1]

	#分类拿取两个时间点中的数据
	resNews = getNewsByTime(cur,origin,time1,time2)

	ArrNews = []
	arrNews = {'keyword': '','title': '','description': '','url':'','origin':'','pubtime':''}

	for rNews in resNews:
		rk = rNews[0]
		rt = rNews[1]
		rd = rNews[2]
		ru = rNews[3]
		ro = rNews[4]
		rp = dumps(rNews[5], default=json_date)
		arrNews = {'keyword': rk,'title': rt,'description': rd,'url':ru,'origin':ro,'pubtime':rp}#
		ArrNews.append(arrNews)		

	#Json化同时设置UTF8编码
	encodedjson = dumps(ArrNews, ensure_ascii=False).encode('utf-8') 

	cur.close()
	conn.commit()
	conn.close()	
	return encodedjson

if __name__ == "__main__":
	app.run(host='0.0.0.0')



