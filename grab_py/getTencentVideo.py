#!/usr/bin python
# -*-coding:utf-8 -*-
#getTencentVideo.py

import MySQLdb
import requests
from lxml import etree
import time
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from logging import getLogger
import re


#拿取人名
def getCMnameList(cur):
	count = cur.execute('select name,id from chairmansName')
	#重置游标位置，0,为偏移量，mode＝absolute | relative,默认为relative,
	cur.scroll(0,mode='absolute')
	#获取所有结果
	results = cur.fetchall()
	return results

#搜索这个人名的最新视频
def searchChairmansNews(keyword):
	p = {'tabid':'0','duration':'0','pubfilter':'0','filter':'sort=1','stag':'4','q':keyword}
	#https://v.qq.com/x/search/?q=马云&filter=sort=1&pubfilter=0&duration=0&tabid=0
	res = requests.get("http://v.qq.com/x/search/",params = p)
	#print res.url
	res.encoding = 'utf-8'
	return res.text

#搜索这个url在库中的是否存在,不存在返回0，存在返回id数字
def urlexist(cur,url):
	sql = "select * from chairmansNews where url = '%s'"%(url)
	count = cur.execute(sql)
	return count

#入库返回None成功，返回抛错失败
def insertChairmansNews(cur,keyword,title,description,url,origin,pubtime):
	sql = "insert into chairmansNews (keyword,title,description,url,origin,pubtime) values ('%s','%s','%s','%s','%s','%s')"%(keyword,title,description,url,origin,pubtime)
	count = cur.execute(sql)
	return count

#抓取入库完成后，记录完成时间
def saveTime(cur,origin):
	sql = "insert into chairmansSaveTime (origin) values('%s')"%(origin)
	count = cur.execute(sql)
	return count

#检查关键词是否完全匹配标题中的关键词
def filterCompleteTitle(title,keyword):
	res = len(re.findall(ur'(.)*%s'%(keyword), u'%s'%(title)))
	return res
	

def getTencentVideo(cur,description,origin):
	logger = getLogger("TencentVideo")
	#搜索入库
	resName = getCMnameList(cur)

	for rName in resName:

		keyword = rName[0].encode("utf8")
		Cid = rName[1]

		data = searchChairmansNews(keyword)
		html = etree.HTML(data)
		
		resNews = html[0].xpath('//div[@class="result_item result_item_h"]')

		for rNews in resNews:
			#整理数据
			dataA = rNews.find('.//a[@_stat="video:poster_h_title"]')
			dataTitle = dataA.xpath('string(.)').strip()
			dataUrl = dataA.xpath('@href')[0]
			dataTime = rNews.find('.//span[@class="content"]').xpath('string(.)').strip()
			#排重
			conf = urlexist(cur,dataUrl)
			if conf == 0:
				resFilter = filterCompleteTitle(dataTitle,keyword)
				if resFilter >= 1:					
					logger.info("不重复，且通过过滤。插入数据。keyword:%s"%(keyword))
					resinsert = insertChairmansNews(cur,keyword,dataTitle,description,dataUrl,origin,dataTime)
					if resinsert == 1:
						logger.info("插入数据成功。keyword:%s"%(keyword))
					else:
						logger.info("插入失败。keyword:%s"%(keyword))
				else:
					logger.info("未能通过过滤。keyword:%s"%(keyword))
			else:		
				logger.info("数据重复。keyword:%s"%(keyword))

	time.sleep(3)
	resSaveTime = saveTime(cur,origin)
	if resSaveTime == 1:
		logger.info("抓取完毕。")



