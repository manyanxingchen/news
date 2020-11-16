#导入扩展程序
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from datetime import timedelta
#创建flask实例化程序
app = Flask(__name__)
#创建配置型系类
class Config(object):
    DEBUG = True
    #session加密配置
    SECRET_KEY = 'JALSJDFLKAJSLK'
    #数据库配置信息
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:3306/news'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #redis配置信息
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = '6379'
    #session配置信息
    SESSION_TYPE = 'redis'  #设定session的存储类型
    SESSION_REDIS = StrictRedis(host=REDIS_HOST,port=REDIS_PORT)  #指定session存储的redis服务器
    SESSION_USE_SIGNER = True  #设置签名存储
    PERMANENT_SESSION_LIFETIME = timedelta(days=2)  #设置session有效期  秒使用seconds
#把配置信息加载到app中
app.config.from_object(Config)
#创建数据库应用实例化程序
db = SQLAlchemy(app)
#创建redis实例化程序
redis_store = StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT,decode_responses=True)
#创建session实例化程序，读取app中的session配置信息
Session(app)
#定义路由
@app.route('/')
#定义视图函数
def index():
    redis_store.set("name","zhangsan")
    print(redis_store.get("name"))
    #测试session获取
    session['name'] = 'lisi'
    print(session.get('name'))
    return 'hello world'
#运行程序
if __name__ =='__main__':
    app.run()