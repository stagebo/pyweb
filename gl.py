
from chatterbot import ChatBot
import ip2region.ip2Region


import requests
import http.cookiejar


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36',
           # "Referer": "https://www.baidu.com/",
           }
# 建立一个会话，可以把同一用户的不同请求联系起来；直到会话结束都会自动处理cookies
session = requests.Session()
# 建立LWPCookieJar实例，可以存Set-Cookie3类型的文件。
# 而MozillaCookieJar类是存为'/.txt'格式的文件
session.cookies = http.cookiejar.LWPCookieJar("cookie")
# 若本地有cookie则不用再post数据了

gl_session={}

gl_rd = None
gl_chatbot = ChatBot(
    'Ron Obvious',
    trainer='chatterbot.trainers.ChatterBotCorpusTrainer'
)

dbFile = 'ip2region/data/ip2region.db'
gl_ip_searcher = ip2region.ip2Region.Ip2Region(dbFile)
# Train based on the english corpus
#gl_chatbot.train("chatterbot.corpus.english")

# gl_session = session

def get_err_params(title="错误",msg="发生了错误！",href="",href_text="跳转"):
    err = {
        "title":title,
        "msg":msg,
        "href":href,
        "href_text":href_text
    }

    return err
import logging
def log(*msg, sp=' ',end=''):
    st = ""
    for m in msg:
        st += str(m)+sp
    st += end
    logging.info(st)
    print(st)