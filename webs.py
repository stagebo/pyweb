import os
import tornado.httpserver
import tornado.ioloop
import pyrestful.rest
import logging
import pymysql
import configparser
import sys
import datetime
import json
import platform
import re
import traceback
from pyrestful import mediatypes
from pyrestful.rest import get, post, put, delete
from handler_jieba import JiebaHandler
from handler_ybs import DoctorHandler
from handler_admin import AdminHandler
from handler_chatbot import ChatbotHandler
from handler_foru import ForuHandler
from handler_message import  MessageHandler
from handler_game import PuzzleHandler
from handler_jsonp import JsonpHandler
from tornado.log import access_log, app_log, gen_log
from tornado.options import define,options
sys.path.append("..")
from database import dbHelper,redisdb,syncdb
import gl

from tornado import ioloop, gen
from tornado_mysql import pools





class Application(pyrestful.rest.RestService):
    def __init__(self):
        self.cf = configparser.ConfigParser()
        self.read_config()
        # 内存数据库
        self.redis = redisdb.RedisDb()

        logging.info("tornado is tring to init...")
        settings= dict(
            #cookie_secret="SBwKSjz3SCWo04t68f/FOY7fPKZI20JYje1IYPBrxaM=",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,
            debug = False,
            login_url = "admin/login",
            log_function = self.mylog
        )
        handlers=[
            MainHadler,
            JiebaHandler,
            DoctorHandler,
            AdminHandler,
            ChatbotHandler,
            ForuHandler,
            MessageHandler,
            PuzzleHandler,
            JsonpHandler,
        ]
        super(Application, self).__init__(handlers, **settings)
        #  取消原始数据库连接工具
        # dbHelper.database=dbHelper.DbHelper(self.mysql_host,self.mysql_uid,self.mysql_pwd,self.mysql_port,self.mysql_db)

        self.db = syncdb.SyncDb(self.mysql_host, self.mysql_port, self.mysql_uid, self.mysql_pwd, self.mysql_db)
        logging.info("tornado is inited.")

    def read_config(self):

        try:
            self.cf.read("web.conf")
        except:
            logging.error("not find a config file named webrest.conf")
            sys.exit(1)
        self.mysql_host = self.cf.get("mysql", "host")
        self.mysql_uid = self.cf.get("mysql", "uid")
        self.mysql_pwd = self.cf.get("mysql", "pwd")
        self.mysql_db = self.cf.get("mysql", "db")
        self.mysql_port = self.cf.getint("mysql", "port")
        self.web_port = self.cf.getint("web", "port")
        self.webs_port = self.cf.getint("web", "port_ssl")

    def mylog(self,handler):
        if handler.get_status() < 400:
            log_method = access_log.info
        elif handler.get_status() < 500:
            log_method = access_log.warning
        else:
            log_method = access_log.error

        request_time = 1000.0 * handler.request.request_time()
        log_method("%d %s %.2fms", handler.get_status(),
                   handler._request_summary(), request_time)

#
class MainHadler(pyrestful.rest.RestHandler):
    @get(_path="/")
    def index(self):
        self.render("base.html")

    @get(_path="/main")
    def main_page(self):
        self.render("main.html")

    @get(_path="/doc")
    def main_doc(self):
        self.render("doc/html/index.html")

    @get(_path="/about")
    def about_page(self):
        self.render("about.html")

    @get(_path="/love/nexttime",_produces=mediatypes.APPLICATION_JSON)
    def get_time(self):
        now = datetime.datetime.now()
        tar = datetime.datetime(2018, 2, 13, 1, 20, 0)
        d = tar - now
        return {"days":d.days,"seconds":d.seconds}



    @get(_path="/admin/redis", _produces=mediatypes.APPLICATION_JSON)
    def redis_test(self):
        try:
            rd = self.application.redis
            rd.set("time",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            d = rd.get("time")

            return {
                'time':d
            }
        except:
            traceback.print_exc()



def copy_log():
    logpath = os.path.join("..", "log")
    logfile =os.path.join(logpath,"pyweb.log") # "..\log\pyweb.log"
    logbak = os.path.join(logpath,"%s.log"%datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    cmd = ""
    print("init log file.")
    print("platform info:%s" % platform.platform())
    print( os.path.exists(logfile))
    if not os.path.exists(logfile):
        print("create log files.")
        os.makedirs(logpath)
        open(logfile, "w")
    elif "Windows" in platform.platform():
        try:
            cmd = "copy %s %s" % (logfile,logbak)
        except:
            traceback.print_exc()
    elif "Linux" in platform.platform():
        cmd = "cp %s %s" % (logfile,logbak)
    if cmd != "":
        p = os.popen(cmd)
        print(cmd)
        print(p)
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=logfile,
                        filemode='w')

def main():
    copy_log()
    try:
        print("Start the service")
        app = Application()
        server =  tornado.httpserver.HTTPServer(app, ssl_options={
           "certfile": os.path.join('keys', "server.pem"),
           "keyfile": os.path.join('keys', "server.key"),
        })
        server.listen(app.webs_port)
        print("access port %s" % app.webs_port)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print("\nStop the service")

if __name__ == '__main__':
    main()
