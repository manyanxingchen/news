#导入扩展程序
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from config import Config

app = Flask(__name__)
#创建配置型系类

#把配置信息加载到app中
app.config.from_object(Config)
#创建数据库应用实例化程序
db = SQLAlchemy(app)
#创建redis实例化程序
redis_store = StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT,decode_responses=True)
#创建session实例化程序，读取app中的session配置信息
Session(app)
#使用CSRFProtect保护app    ['POST', 'PUT', 'PATCH', 'DELETE']  保护这四种请求方式
CSRFProtect(app)
#定义路由
@app.route('/',methods=['GET','POST'])
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