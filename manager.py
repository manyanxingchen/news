#导入扩展程序
from new import create_app
#调用方法获取app
app = create_app('product')


#运行程序
if __name__ =='__main__':
    app.run()