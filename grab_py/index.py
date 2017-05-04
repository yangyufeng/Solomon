#!/usr/bin python
# -*-coding:utf-8 -*-
#index.py

import MySQLdb
import requests
from lxml import etree
import sys
reload(sys)
sys.setdefaultencoding('utf8')

#加载tencentVideo
from getTencentVideo import getTencentVideo

#接库
conn= MySQLdb.connect(
					host='localhost',
					port = 3306,
					user='root',
					passwd='123',
					db ='company',
					charset='utf8',
					)
cur = conn.cursor()

#tencentVideo默认参数
TVdes = "no_date"
TVori = "tencent_video"

if __name__ == '__main__':

	def setup_logger(name):
		import logging
		from logging.handlers import RotatingFileHandler

		formatter = logging.Formatter(fmt='[%(asctime)s][%(levelname)s][%(name)s] => %(message)s')

		handler = RotatingFileHandler('log_%s.log' % name, maxBytes=50000000, backupCount=2)
		handler.setFormatter(formatter)

		logger = logging.getLogger(name)
		logger.setLevel(getattr(logging, "DEBUG"))
		logger.addHandler(handler)


	setup_logger("TencentVideo")

	getTencentVideo(cur,TVdes,TVori)

cur.close()
conn.commit()
conn.close()