#!/usr/bin python
# -*-coding:utf-8 -*-
#sendMessage.py

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import requests
from datetime import *
from json import dumps
import json
import MySQLdb
from logging import getLogger

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
	#print sql
	count = cur.execute(sql)
	if count != 0:
		cur.scroll(0,mode='absolute')
		#获取所有结果
		results = cur.fetchall()
		return results
	else:
		return count

#mysql中datetime在python中字符串化
def json_date(obj):
	"""JSON serializer for objects not serializable by default json code"""
	if isinstance(obj, date):
		serial = obj.isoformat()
		return serial
	raise TypeError ("Type not serializable")


def sendMessage(cur,origin):
	logger = getLogger("sendMessage")
	#获取最新两条时间
	arrTime = []
	resSaveTime = getSaveTime(cur,origin)

	for rSaveName in resSaveTime:
		arrTime.append(rSaveName[0]) 

	time1 = arrTime[0]
	time2 = arrTime[1]

	#分类拿取两个时间点中的数据
	resNews = getNewsByTime(cur,origin,time1,time2)
	if resNews != 0:
		logger.info("此时间段有取数据！")
	else:
		logger.info("此时间段无抓取数据！")
		exit()

	str = ''

	for rNews in resNews:

		rk = rNews[0]
		rt = rNews[1]
		rd = rNews[2]
		ru = rNews[3]
		ro = rNews[4]
		rp = dumps(rNews[5], default=json_date)

		rstr = '来源：' + ro + ' 人物：' + rk + '\n' + '标题：' + rt + '\n' + '地址：' + ru + '\n' + '发布时间：' + rp + '\n\n' 
		str += rstr 

	res = requests.post("http://120.26.99.59:8087/baoer/wscn2_send_message/", json={"msg_to": "videoTest", "msg_body": str})
	#print res.url
	res.encoding = 'utf-8'
	resArr = json.loads(res.text)
	if resArr['is_success'] == True:
			logger.info("推送成功！")
	return res

