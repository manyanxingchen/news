from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from config import config_dict


#定义全局变量redis_store
redis_store = None
#定义工厂方法
def create_app(config_name):
    app = Flask(__name__)
    #根据传入的配置类名称取出对应的类
    config = config_dict.get(config_name)
    #把配置信息加载到app中
    app.config.from_object(config)
    #创建数据库应用实例化程序
    db = SQLAlchemy(app)
    #创建redis实例化程序
    redis_store = StrictRedis(host=config.REDIS_HOST,port=config.REDIS_PORT,decode_responses=True)
    #创建session实例化程序，读取app中的session配置信息
    Session(app)
    #使用CSRFProtect保护app    ['POST', 'PUT', 'PATCH', 'DELETE']  保护这四种请求方式
    CSRFProtect(app)
    #注册蓝图
    from new.modules.index import index_blue
    app.register_blueprint(index_blue)
    return app