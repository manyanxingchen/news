#from new.modules.index import index_blue
from . import index_blue  #点表示的是当前的路径下
from ... import redis_store
import logging
from flask import current_app,render_template
#定义蓝图路由
@index_blue.route('/',methods=['GET','POST'])
#定义视图函数
def index():
    redis_store.set("name","zhangsan")
    print(redis_store.get("name"))
    #测试session获取
    # session['name'] = 'lisi'
    # print(session.get('name'))

    #使用日志记录方法logging进行输出控制
    # logging.debug('输入调试信息')
    # logging.info('输入详细信息')
    # logging.warning('输入警告信息')
    # logging.error('输入错误信息')
    #使用current_app来输出日志信息
    # current_app.logger.debug('输入调试信息2')
    # current_app.logger.info('输入详细信息2')
    # current_app.logger.warning('输入警告信息2')
    # current_app.logger.error('输入错误信息2')
    return render_template('new1/index.html')