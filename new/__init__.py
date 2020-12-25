from flask import Flask, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_wtf.csrf import CSRFProtect,generate_csrf
from config import config_dict
import logging
from logging.handlers import RotatingFileHandler

#定义redis_store
from new.utils.commons import hot_news_filter

redis_store = None
#定义数据库变量
db = SQLAlchemy()
#定义工厂方法
def create_app(config_name):

    app = Flask(__name__)
    #根据传入的配置类名称取出对应的类
    config = config_dict.get(config_name)
    # 调用日志方法，并从config文件中传入相应的等级参数
    log_file(config.LEVEL_NAME)
    #把配置信息加载到app中
    app.config.from_object(config)
    #创建数据库应用实例化程序
    db.init_app(app)
    #创建redis实例化程序
    #将局部变量redis_store声明为全局变量
    global redis_store
    redis_store = StrictRedis(host=config.REDIS_HOST,port=config.REDIS_PORT,decode_responses=True)
    #创建session实例化程序，读取app中的session配置信息
    Session(app)
    #使用CSRFProtect保护app    ['POST', 'PUT', 'PATCH', 'DELETE']  保护这四种请求方式
    CSRFProtect(app)
    #注册首页蓝图
    from new.modules.index import index_blue
    app.register_blueprint(index_blue)
    #注册图片验证码蓝图
    from new.modules.passport import passport_blue
    app.register_blueprint(passport_blue)
    #注册新闻验证码蓝图
    from new.modules.news import news_blue
    app.register_blueprint(news_blue)
    #用户信息显示蓝图
    from new.modules.profile import profile_blue
    app.register_blueprint(profile_blue)
    #管理员蓝图
    from new.modules.admin import admin_blue
    app.register_blueprint(admin_blue)
    #使用请求钩子拦截所有的请求
    @app.after_request
    def after_request(resp):
        csrf_token  = generate_csrf()
        resp.set_cookie('csrf_token',csrf_token)
        return resp
    #捕捉异常404错误渲染页面
    @app.errorhandler(404)
    def page_not_found(e):
        #多重路径无法返回时，可以使用重定向对业务面进行渲染
        return redirect('/404')
        # return render_template('admin1/404.html')
    #强自定义的过滤器加载到系统默认的过滤器中
    app.add_template_filter(hot_news_filter,'my_filter')
    print(app.url_map)
    return app
def log_file(LEVEL_NAME):
    #设置日志记录的等级   ERROR = 40 > WARNIG = 30 > INFO = 20 > DEBUG = 10
    logging.basicConfig(level=LEVEL_NAME)  #调试debug级 一旦设置该级别大于等于该级别的信息都会输出
    #创建日志记录器1，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上线
    file_log_handler = RotatingFileHandler("logs/log",maxBytes=1024*1024*100,backupCount=10,encoding='utf8')
    #创建日志记录的格式，日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    #为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    #为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)