#导入蓝图
from flask import render_template, request, current_app, session, redirect, g

from . import admin_blue
from ...models import User
from ...utils.commons import user_login_data


@admin_blue.route('/index')
@user_login_data
def index():
    data = {
        'user_info':g.user.to_dict() if g.user else ''
    }
    return render_template('admin1/index.html',data = data)
# @admin_blue.route('/login')
# def admin_login():
#     return render_template('/admin1/login.html')

#1.请求路径  /user/login
#2.请求方式  get  post
#3.请求参数  post  username password
#4.返回响应  errno errmsg
@admin_blue.route('/login',methods = ['GET','POST'])
def admin_login():
    #1.判断请求方式
    if request.method == 'GET':
        #判断用户是否登录
        if session.get('is_admin'):
            return redirect('/admin1/index')
        # 2.get请求直接渲染页面
        return render_template('admin1/login.html')
    #3.post请求 获取参数
    if request.method =='POST':
        username = request.form.get('username')
        password = request.form.get('password')
    #4.参数为空校验
    if not all([username,password]):
        return render_template('admin1/login.html',errmsg = '参数不能为空')
    #5.依据用户名取出管理员用户，判断管理员用户shifoucunzsai
    try:
        admin = User.query.filter(User.mobile == username,User.is_admin==True).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin1/login.html',errmsg= '管理员查询失败')
    if not admin:
        return render_template('admin1/login.html',errmsg = '管理员用户不存在')
    #6.判断密码是否正确
    if not admin.check_password(password):
        return render_template('admin1/login.html',errmsg = '密码错误')
    #7.管理员的session信息
    session['user_id'] = admin.id
    session['is_admin'] = True
    #8.重定向到首页
    return redirect('/admin1/index')