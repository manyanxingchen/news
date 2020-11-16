#导入扩展程序
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#创建flask实例化程序
app = Flask(__name__)

db = SQLAlchemy(app)

#创建配置型系类
class Config(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:3306?news'
    SQLALCHEMY_TRACK_MODEFICATIONS = False
#把配置信息加载到app中
app.config.from_object(Config)
#定义路由
@app.route('/')
#定义视图函数
def index():
    return 'hello world'
#运行程序
if __name__ =='__main__':
    app.run()