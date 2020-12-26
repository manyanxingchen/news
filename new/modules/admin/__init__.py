#1，导入烂熟扩展
from flask import Blueprint, request, session, redirect

#2.创建揽入对象
admin_blue = Blueprint('admin',__name__,url_prefix='/admin1')
#3.导入views装饰视图函数
from . import views

#4.注册管理员蓝图
#在项目new文件__init__.py中

#5.捕获admin1装饰的路路径添加请求钩子
@admin_blue.before_request
def before_request():
    """
    if request.url.endswith('/admin1/login'):
        pass
    else:
        if session.get('is_admin'):
            pass
        else:
            return redirect('/')
    """
    if not request.url.endswith('/admin1/login'):
        if not session.get('is_admin'):
            return redirect('/')