
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
from database import redisdb
import traceback
import gl
import hashlib  # 导入md5加密模块
import time  # 导入时间模块
import sys
import re
import requests
class AdminHandler(pyrestful.rest.RestHandler):
    """
        this is admin handler api.

        this object provides some method to query and controll system

        :param None:

        """
    def _right(self):
        return False
        hq_cookie = self.get_cookie('xr_cookie')  # 获取浏览器cookie
        session = gl.gl_session.get(hq_cookie, None)  # 将获取到的cookie值作为下标，在数据字典里找到对应的用户信息字典
        if not session:  # 判断用户信息不存在
            return False
        else:
            if session.get('is_login', None) == True:  # 否则判断用户信息字典里的下标is_login是否等于True
                return True
            else:
                return False

    @get(_path="/admin")
    def get_index(self):
        self.redirect("admin/index")


    @get(_path="/admin/index")
    def get_page(self):
        if self._right():  # 否则判断用户信息字典里的下标is_login是否等于True
            self.render("admin/index.html")
        else:
            self.redirect("/admin/login")

    @get(_path="/admin/login")
    def get_login(self):
        self.render("admin/login.html",err='')

    @get(_path="/admin/statistics_number")
    def statistics_visitor(self):
        try:
            data = self.get_argument("data")
            data_list = data.split("|")

            num_list = [re.sub(r'\D', "", item) for item in data_list]

            if len(num_list) != 6:
                raise Exception("格式不对")
            ip = num_list[1]
            pv = num_list[2]

            lip = num_list[3]
            lpv = num_list[4]

            if not ip.isdigit() or not pv.isdigit() or not lip.isdigit() or not lpv.isdigit():
                return

            time = datetime.datetime.now().strftime("%Y-%m-%d")
            sql = '''
                insert into t_statistics  values('%s','%s','%s','%s','%s')
                on DUPLICATE key update 
                f_time=values(f_time),f_ip=values(f_ip),f_pv=values(f_pv),f_lip=values(f_lip),f_lpv=values(f_lpv);
                ''' % (time, ip, pv, lip, lpv)
            gl.log(sql)
            ret = self.application.db.execute_sql(sql)
        except Exception as e:
            logging.warning("浏览统计存在问题！")
            logging.warning(e)

    @tornado.web.asynchronous
    @tornado.gen.engine
    @get(_path="/admin/statistics_numbers")
    def get_statistics_numbers(self):
        sql = """
            select sum(ipn) as ipnums from (
                (select sum(f_lip)  as ipn from t_statistics as st)
                union
                (select  f_ip as ipn from t_statistics order by f_time desc LIMIT 0,1)
            ) as ips
        """
        sdb = self.application.db
        # data = yield tornado.gen.Task(sdb.execute, sql)
        data = yield sdb.execute(sql)
        ret = data
        result = {
            "ret": "1",
            "msg": "",
            "data": ret
        }
        self.finish(result)


    @post(_path="/admin/login",_produces=mediatypes.APPLICATION_JSON)
    def post_login(self):
        user = self.get_body_argument("username",None)
        pwd = self.get_body_argument("password",None)
        gl.log(user,pwd)
        if user == 'admin' and pwd == 'admin':  # 判断用户的密码和账号
            obj = hashlib.md5()  # 创建md5加密对象
            obj.update(bytes(str(time.time()), encoding="utf-8"))  # 获取系统当前时间，传入到md5加密对象里加密
            key = obj.hexdigest()  # 获取加密后的密串
            # rd = self.application.redis

            gl.gl_session[key] = {}  # 将密串作为下标到container字典里，创建一个新空字典
            gl.gl_session[key]['username'] = user  # 字典里的键为yhm，值为用户名
            gl.gl_session[key]['password'] = pwd  # 字典里的键为mim，值为用户密码
            gl.gl_session[key]['is_login'] = True  # 字典里的键为is_login，值为True
            self.set_cookie('xr_cookie', key, expires_days=1)  # 将密串作为cookie值写入浏览器
            self.render('admin/index.html',username=user)
        else:
            self.render('admin/login.html',err="用户名或密码不正确！")



    @get(_path="/admin/restart")
    def restart(self):
        """
        - 功能:    重启系统.
        - URL:     /admin/restart
        - HTTP:    GET
        - 参数:    无
        - 返回值:
                   * 正确,{"rel": 1,"msg": "" }
                   * 错误:{ "rel":0,"msg":"err！" }
        """
        os.system("python3 restart.py")

    @get(_path="/admin/get_day_word")
    def get_day_word(self):
        """
        - 功能:    获取金山每日一句
        - URL:     /admin/get_day_word
        - HTTP:    GET
        - 参数:    无
        - 返回值:
                   * 正确,{"rel": 1,"msg": "" }
                   * 错误:{ "rel":0,"msg":"err！" }
        """


        url = "http://open.iciba.com/dsapi/"
        r = requests.get(url)
        self.write(r.json())

    @get(_path="/admin/get_weather")
    def Query_weather_info(self):
        """
             - 功能:    #8 查询天气情况
             - URL:     /admin/get_weather
             - HTTP:    GET
             - 参数:
                        * 字段名          类型            内容         举例
                        * city_id      int                城市ID       101100201 （山西大同）
             - 返回值:
                        * 正确返回:{"result":"0","msg":"","payload":{'city': '城市', 'cityid': '城市ID', 'weather': '天气情况', 'SD': '湿度', 'temp': '温度', 'FX': '风向', 'FL': '风力'}}
                        * 错误:{"result":"-1","msg":"错误消息内容"}

        """

        try:
            city_id = self.get_argument('city_id',None)
        except:
            traceback.print_exc()

        if not city_id or city_id == '':
            self.finish({
                "rel": 0,
                "msg": "city_id不能为空！"
            })
            return

        # 国家气象局接口
        # 接口参见：https://www.cnblogs.com/wangjingblogs/p/3192953.html
        # 转发接口地址
        # 1 http://www.weather.com.cn/data/cityinfo/101010100.html  北京
        # 2 http://www.weather.com.cn/data/sk/101010100.html

        try:
            url = 'http://www.weather.com.cn/data/sk/%s.html' % city_id
            rel = requests.get(url, timeout=1)
            url2 = 'http://www.weather.com.cn/data/cityinfo/%s.html' % city_id
            rel2 = requests.get(url2, timeout=1)
        except:
            self.finish({
                "rel": 0,
                "msg": "连接接口失败！"
            })
            return

        try:
            data = json.loads(rel.content.decode('utf-8'))["weatherinfo"]
            data2 = json.loads(rel2.content.decode('utf-8'))["weatherinfo"]

            ret = {
                "city": data["city"],
                "cityid": data["cityid"],
                "weather": data2["weather"],
                "SD": data["SD"],
                "temp": data["temp"],
                "FX": data["WD"],
                "FL": data["WS"]
            }
        except:
            self.finish({
                "rel": 0,
                "msg": "city_id编码不正确！"
            })

        self.finish({"result": "0", "msg": "", "payload": ret})

    @get(_path="/admin/ip_test", _produces=mediatypes.APPLICATION_JSON)
    def ip_test(self):
        ip = self.request.remote_ip
        self.finish({"ip":ip})