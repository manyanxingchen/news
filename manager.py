#导入扩展程序
from new import create_app,db,models  #导入models是让整个程序知道有models存在
from flask_migrate import Migrate,MigrateCommand
from flask_script import Manager
#调用方法获取app
app = create_app('develop')
#创建manager对象，管理app
manager = Manager(app)
#使用Migrate关联app,db
Migrate(app,db)
#给manager添加一条管理命令
manager.add_command('db',MigrateCommand)
#运行程序
if __name__ =='__main__':
    app.run()