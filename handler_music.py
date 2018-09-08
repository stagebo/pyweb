
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
import requests

class MusicHandler(pyrestful.rest.RestHandler):
    @get(_path="/music")
    def get_index(self):
        self.render("music/index.html")

    @get(_path="/music/list",_produces=mediatypes.APPLICATION_JSON)
    def get_musics(self):
        word = self.get_argument('name',"最后我们没在一起")
        res1 = requests.get(
            'https://c.y.qq.com/soso/fcgi-bin/client_search_cp?&t=0&aggr=1&cr=1&catZhida=1&lossless=0&flag_qc=0&p=1&n=20&w=' + word)
        jm1 = json.loads(res1.text.strip('callback()[]'))
        jm1 = jm1['data']['song']['list']
        mids = []
        songmids = []
        srcs = []
        songnames = []
        singers = []
        ret = []
        for j in jm1:
            try:
                mid = j['media_mid']
                smid = j['songmid']
                sname = j['songname']
                sgname = j['singer'][0]['name']
                mids.append(j['media_mid'])
                songmids.append(j['songmid'])
                songnames.append(j['songname'])
                singers.append(j['singer'][0]['name'])

                res2 = requests.get(
                    'https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg?&jsonpCallback=MusicJsonCallback&cid=205361747&songmid=' +
                    smid + '&filename=C400' + mid + '.m4a&guid=6612300644')
                jm2 = json.loads(res2.text)
                vkey = jm2['data']['items'][0]['vkey']
                src = 'http://dl.stream.qqmusic.qq.com/C400' + mid + '.m4a?vkey=' + vkey + '&guid=6612300644&uin=0&fromtag=66'
                ret.append({
                    'mid':mid,
                    'smid':smid,
                    "songname":sname,
                    "singer":sgname,
                    "link":src
                })
            except:
                print('wrong')
        return ret


