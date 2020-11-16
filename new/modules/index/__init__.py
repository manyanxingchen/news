#创建蓝图三步骤
#1.导入扩展   创建蓝图实例对象

from flask import Blueprint
index_blue = Blueprint("index",__name__)
#2.导入views装饰视图函数
#from new.modules.index import view
from . import view
#3.注册蓝图
#这一步在初始化文件中返回app时就会返回注册蓝图