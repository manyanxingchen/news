#from new.modules.index import index_blue
from . import index_blue  #点表示的是当前的路径下
#定义路由
@index_blue.route('/',methods=['GET','POST'])
#定义视图函数
def index():
    # redis_store.set("name","zhangsan")
    # print(redis_store.get("name"))
    #测试session获取
    # session['name'] = 'lisi'
    # print(session.get('name'))
    return 'hello world'