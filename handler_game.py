import tornado.web
import pyrestful.rest
import json,uuid,random
from PIL import Image
import jieba
import sys
import datetime
from database import dbHelper
import logging
from pyrestful.rest import get, post, put, delete
from pyrestful import mediatypes
import traceback
import ip2region.ip2Region
import gl
from tornado import gen
class PuzzleHandler(pyrestful.rest.RestHandler):
    @get(_path="/game")
    def index(self):
        self.render("game/puzzle.html")

    @get(_path="/game/puzzle")
    def puzzle(self):
        self.render("game/puzzle.html")

    @tornado.web.asynchronous
    @tornado.gen.engine
    @get(_path="/game/get_image")
    def get_image(self):
        sql = "select * from t_game_image"
        data = yield self.application.db.execute(sql)
        result = []
        for row in data:
            url = row['f_url']
            url1 = {'url': row['f_url1'], 'idx': 1}
            url2 = {'url': row['f_url2'], 'idx': 2}
            url3 = {'url': row['f_url3'], 'idx': 3}
            url4 = {'url': row['f_url4'], 'idx': 4}
            url5 = {'url': row['f_url5'], 'idx': 5}
            url6 = {'url': row['f_url6'], 'idx': 6}
            url7 = {'url': row['f_url7'], 'idx': 7}
            url8 = {'url': row['f_url8'], 'idx': 8}
            url9 = {'url': row['f_url9'], 'idx': 9}
            list = [url2,url3,url4,url5,url6,url7,url8,url9]
            random.shuffle(list)
            item = {'total':url,'part':list}
            result.append(item)

        self.finish({
            'ret': 1,
            'msg': '',
            'data': result
        })

    @tornado.web.asynchronous
    @tornado.gen.engine
    @get(_path="/game/test")
    def game_test(self):
        self.finish("game test")
    @tornado.web.asynchronous
    @tornado.gen.engine
    @get(_path="/game/create_image")
    def create_image(self):
        '''
        1   2   3
        4(0,1)   5   6
        7   8   9

        :return:
        '''
        im = Image.open('static/image/yqy20170529SQ.jpg')  # 读取和代码处于同一目录下的 lena.png
        w, h = im.size
        a = min(w, h)
        d = a // 3
        value_list = []
        uid_str = str(uuid.uuid1())
        filename = 'static/game_image/image_split_%s.png' % (uid_str)
        value_list.append("'" + filename + "'")
        im.save(filename)
        for key in range(9):
            filename = 'static/game_image/image_split_%s_%s_%s.png' % (key,uid_str, key)
            value_list.append("'" + filename + "'")
            j = key//3
            i = key%3
            gl.log(i,j)
            region = im.crop((i * d, j * d, i * d + d, j * d + d))
            region.save(filename)
        gl.log(a, d)
        sql = """
           insert into t_game_image (f_url,f_url1,f_url2,f_url3,f_url4,f_url5,f_url6,f_url7,f_url8,f_url9)
           values (%s)
           """ % ','.join(value_list)
        self.application.db.execute_sql(sql)
        self.finish("success")
