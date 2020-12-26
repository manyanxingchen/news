#导入蓝图
from datetime import datetime

from flask import render_template, request, current_app, session, redirect, g
import time
from . import admin_blue
from ...models import User
from ...utils.commons import user_login_data
from datetime import datetime,timedelta
@admin_blue.route('/user_count')
def user_count():
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error
        return render_template('admin1/user_count.html',errmsg = '总人数查询失败')
    try:
        #1.先获取本月1日0点的日期时间
        localtime = time.localtime()
        #2.获取本月日期字符串
        month_start_time_str = '%s-%s-01'%(localtime.tm_year,localtime.tm_mon)
        #3.将字符串转换为日期类型
        month_start_time_date = datetime.strptime(month_start_time_str,'%Y-%m-%d')

        month_count = User.query.filter(User.last_login>=month_start_time_date,User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error
        return render_template('admin1/user_count.html',errmsg = '获取月活人数失败')
    try:
        #1.先获取本月1日0点的日期时间
        day_start_time_str = '%s-%s-%s'%(localtime.tm_year,localtime.tm_mon,localtime.tm_mday)
        day_start_time_date = datetime.strptime(day_start_time_str,'%Y-%m-%d')
        day_count = User.query.filter(User.last_login>=day_start_time_date,User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error
        return render_template('admin1/user_count.html',errmsg = '获取日活人数失败')
    #获取活跃时间段内，对应的活跃人数
    active_date = []  #获取活跃日期
    active_count = []  #获取活跃人数
    for i in range(0,31):
        #当前开始时间A
        begin_date = day_start_time_date - timedelta(days=i)
        #当天开始时间的后一天B
        end_date = day_start_time_date - timedelta(days=i-1)
        #添加当天开始时间字符串到，活跃日期中
        active_date.append(begin_date.strftime('%m-%d'))
        #查询时间A到B这一天的注册人数
        every_active_count = User.query.filter(User.is_admin==False,User.last_login>=begin_date,User.last_login<=end_date).count()
        #添加当天注册人数到，获取数量中
        active_count.append(every_active_count)
    #为了图表显示方便
    active_date.reverse()
    active_count.reverse()
    data = {
        'total_count':total_count,
        'month_count':month_count,
        'day_count':day_count,
        'active_count':active_count,
        'active_date':active_date
    }
    return render_template('admin1/user_count.html',data = data)
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