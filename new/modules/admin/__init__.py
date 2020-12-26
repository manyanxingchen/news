#1，导入烂熟扩展
from flask import Blueprint
#2.创建揽入对象
admin_blue = Blueprint('admin',__name__,url_prefix='/admin1')
#3.导入views装饰视图函数
from . import views

#4.注册管理员蓝图