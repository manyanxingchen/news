#导入扩展程序
from datetime import datetime,timedelta
from random import randint

from flask import current_app

from new import create_app,db,models  #导入models是让整个程序知道有models存在
from flask_migrate import Migrate,MigrateCommand
from flask_script import Manager
#调用方法获取app
from new.models import User

app = create_app('develop')
#创建manager对象，管理app
manager = Manager(app)
#使用Migrate关联app,db
Migrate(app,db)
#给manager添加一条管理命令
manager.add_command('db',MigrateCommand)
#为了使得创建管理员用户的保密，只有创建人可知需要在终端中调用方法，传递相应参数
@manager.option('-u', '--username', dest='username')
@manager.option('-p', '--password', dest='password')
#创建管理员用户--使用终端创建管理员用户  python manager.py create_superuser -u username -p password
def create_superuser(username,password):
    #1.创建管理员用户
    admin = User()
    #2.给管理员用户赋值属性
    admin.nick_name = username
    admin.mobile = username
    admin.password = password
    admin.is_admin = True
    #3.添加到数据库
    try:
        db.session.add(admin)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return '创建失败'
    return '创建成功'
#为了图表好看批量创建用户
@manager.option('-t', '--test', dest='test')
def test(test):
    #批量添加用户
    user_list = []
    for i in range(0,1000):
        user = User()
        user.nick_name = '张三%s'%i
        user.mobile = '139%08d'%i
        user.password_hash = 'pbkdf2:sha256:150000$AWOXUM5P$8cfe321f09633bee119f904d15a1a7372824257b8236874fe6907e4086f2d3d2'
        user.last_login = datetime.now() - timedelta(seconds=randint(0,3600*24*31))
        user_list.append(user)
    #批量添加到数据库
    try:
        db.session.add_all(user_list)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return '添加测试用户失败'
    return '添加测试用户成功'
#运行程序
if __name__ =='__main__':
    manager.run()