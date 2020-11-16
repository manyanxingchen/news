#导入扩展程序
from new import create_app
#调用方法获取app
app = create_app('product')
#定义路由
@app.route('/',methods=['GET','POST'])
#定义视图函数
def index():
    # redis_store.set("name","zhangsan")
    # print(redis_store.get("name"))
    #测试session获取
    # session['name'] = 'lisi'
    # print(session.get('name'))
    return 'hello world'
#运行程序
if __name__ =='__main__':
    app.run()