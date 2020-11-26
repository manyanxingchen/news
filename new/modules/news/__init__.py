from flask import Blueprint
#创建新闻蓝图
news_blue = Blueprint('news',__name__,url_prefix='/news')
#使用视图对象，装饰视图函数
from new.modules.news import views
