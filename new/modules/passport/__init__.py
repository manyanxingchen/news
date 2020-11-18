#导入蓝图扩展
from flask import Blueprint

#创建蓝图对象

passport_blue = Blueprint('passport',__name__,url_prefix='/passport')   #url_prefix='/passport'加入访问路径前缀

#导入包含蓝图视图函数的文件views

from new.modules.passport import views

