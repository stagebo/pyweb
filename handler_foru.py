
import tornado.web
import pyrestful.rest
import json
import jieba
import sys
import os
import datetime
sys.path.append("..")
from database import dbHelper
import logging
from pyrestful.rest import get, post, put, delete
from pyrestful import mediatypes
import traceback
import gl
import hashlib  # 导入md5加密模块
import time  # 导入时间模块
import sys

class ForuHandler(pyrestful.rest.RestHandler):
    @get(_path="/foru")
    def get_index(self):
        gl.log("foru")
        self.render("foru/index.html")

    @get(_path="/foru/loveyqy")
    def get_time_page(self):
        self.render("foru/love_time.html")

    @get(_path="/foru/lineforu",_produces=mediatypes.APPLICATION_JSON)
    def get_days(self):
        tar = datetime.datetime(2017, 6, 6, 21, 0, 0)
        brake = datetime.datetime(2018, 9, 2, 21, 7, 0)
        now = datetime.datetime.now()
        now = brake
        timedel = now - tar

        result = {
            "days":timedel.days,
            "seconds":timedel.seconds,
            "allseconds":timedel.days*24*60*60+timedel.seconds
        }
        return result;

    @get(_path="/foru/lifemonths", _produces=mediatypes.APPLICATION_JSON)
    def get_months(self):
        brithday = self.get_argument("bri",None)
        bri = datetime.datetime(1994,3,23,0,0,0)
        if bri:
            try:
                bri = datetime.datetime.strptime(brithday,"%Y-%m-%d")
            except:
                pass
        tar = datetime.datetime(2017,6,6,21,0,0)
        brake = datetime.datetime(2018, 9, 2, 21, 7, 0)
        now = datetime.datetime.now()

        m1 = self.month_differ(tar,bri)
        m2 = self.month_differ(brake,tar)
        m3 = self.month_differ(now,brake)
        return {
            "n1":m1,
            "n2":m1+m2,
            "n3":m1+m2+m3,
            "start":str(bri),
            "tar":str(tar),
            "now":str(now)
        }
    def month_differ(self,x, y):
        """暂不考虑day, 只根据month和year计算相差月份
        Parameters
        ----------
        x, y: 两个datetime.datetime类型的变量

        Return
        ------
        differ: x, y相差的月份
        """
        month_differ = abs((x.year - y.year) * 12 + (x.month - y.month) * 1)
        return month_differ
