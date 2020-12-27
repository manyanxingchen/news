#导入蓝图
from datetime import datetime

from flask import render_template, request, current_app, session, redirect, g, jsonify
import time
from . import admin_blue
from ... import db, constants
from ...models import User, News, Category
from ...utils.commons import user_login_data
from datetime import datetime,timedelta

from ...utils.image_storage import image_storage
from ...utils.response_code import RET
#1.请求路径   /admin1/add_category
#2.请求方式   post
#3.请求参数  post name id
#4.返回响应
@admin_blue.route('/add_category',methods=['POST'])
def add_news():
    #1.获取参数
    name = request.json.get('name')
    id = request.json.get('id')
    #2.参数为空校验
    if not name:
        return jsonify(errno = RET.PARAMERR,errmsg = '分类名不能为空')
    #3.判断是否存在新闻id  是则为修改分类名
    if id:
        #查询分类
        try:
            category = Category.query.get(id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno = RET.DBERR,errmsg ='分类查询失败')
        #判断分类是否存在
        if not category:
            return jsonify(errno = RET.NODATA,errmsg = '分类不存在')
        #修改分类名
        category.name = name
        return jsonify(errno = RET.OK,errmsg = '分类名修改成功')
    #不存在分类id  则为添加分类
    category = Category()
    category.name = name
    db.session.add(category)
    db.session.commit()
    return jsonify(errno = RET.OK,errmsg = '分类添加成功')
#1.请求路径   /admin1/news_edit_detail
#2.请求方式 get
#3.请求参数  get news_id post title  digest  index_image_url  content   category
#4.返回响应
@admin_blue.route('/news_type',methods = ['GET','POST'])
def news_type():
    #1.判断请求方式 如果为get   携带数据渲染页面
    if request.method =='GET':
        try:
            #查询新闻分类
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return render_template('/admin1/news_type.html',errmsg='分类查询失败')
        #判断新闻分类是否存在
        # if not categories:
        #     return render_template('/amdin1/news_type.html',errmsg = '分类查询错误')
        # #将新闻分类对象转换成字典
        # category_list =[]
        # for category in categories:
        #     category_list.append(category.to_dict())
        #category  因为不要对其内的数据进行其他条件操作，因此不需要转换成字典
        return render_template('/admin1/news_type.html',category_list = categories)
#1.请求路径   /admin1/news_edit_detail
#2.请求方式 get post
#3.请求参数  get news_id  post title  digest  index_image_url  content   category
#4.返回响应
@admin_blue.route('/news_edit_detail',methods = ['GET','POST'])
def news_edit_detail():
    #1.判断请求方式 get请求  获取新闻编号
    if request.method == 'GET':
        news_id = request.args.get('news_id')
        #2.参数为空校验
        if not news_id:
            return render_template('/admin1/news_edit_detail.html',errmsg = '新闻编号获取失败')
        #3.查询新闻内容
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return render_template('/admin1/news_edit_detail.html',errmsg = '新闻查询失败')
        #4判断新闻是否存在
        if not news:
            return render_template('/admin1/news_edit_detail.html',errmsg = '新闻不存在')
        # 5查询所有分类
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return render_template('/admin1/news_edit_detail.html', errmsg='新闻分类查询失败')
        #6新闻分类转换成字典
        category_list = []
        for category in categories:
            category_list.append(category.to_dict())
        data = {
            # 将新闻对象转换成字典
            'news':news.to_dict(),
            'category_list':category_list
        }
        return render_template('/admin1/news_edit_detail.html', data=data)
    else:
        #1.获取参数
        news_id = request.form.get('news_id')
        digest = request.form.get('digest')
        title = request.form.get('title')
        content = request.form.get('content')
        index_image = request.files.get('index_image')
        category_id = request.form.get('category_id')
        #校验参数  为空
        if not all([title,digest,content,news_id,category_id]):
            return jsonify(errno = RET.PARAMERR,errmsg = '参数不能为空')
        #2.查询新闻
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno = RET.DBERR,errmsg = '新闻查询失败')
        if not news:
            return jsonify(errno = RET.NODATA,errmsg = '新闻不存在')
        #2.上传图片
        if index_image:
            try:
                index_image_url = image_storage(index_image.read())
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno = RET.THIRDERR,errmsg = '七牛云错误')
            if not index_image_url:
                return jsonify(errno = RET.NODATA,errmsg = '图片上传失败')
            news.index_image_url = constants.QINIU_DOMIN_PREFIX + index_image_url
        #3.更改新闻属性
        news.title = title
        news.digest =digest
        news.category_id = category_id
        news.content = content
        #4.返回响应
        return jsonify(errno = RET.OK,errmsg = '编辑成功')
#1.请求路径   /admin1/edit
#2.请求方式 get
#3.请求参数  get p
#4.返回响应

@admin_blue.route('/news_edit')
def news_edit():
    #1.获取参数
    p = request.args.get('p',1)
    keywords = request.args.get('keywords')
    #2.参数类型转换
    try:
        p = int(p)
    except Exception  as e:
        current_app.logger.error(e)
        return render_template('/admin1/news_edit.html',errmsg = '参数类型转换失败')
    #3.分页查询
    filter = []
    try:
        if keywords:
            filter = [News.title.contains(keywords)]
        news = News.query.filter(*filter).paginate(p,10,False)
    except Exception as e:
        current_app.logger.error(e)
        return render_template('/admin1/news_edit.html',errmsg = '新闻查询失败')
    #4.获取分页查询内容
    totalPage = news.pages
    currentPage = news.page
    items = news.items
    #5.将新闻内容转换成字典
    news_list = []
    for news in  items:
        news_list.append(news.to_dict())
    data = {
        'totalPage':totalPage,
        'currentPage':currentPage,
        'news_list':news_list
    }
    return render_template('/admin1/news_edit.html',data = data)
#1.请求路径   /admin1/news_review_detail
#2.请求方式 get   post
#3.请求参数  get id
#4.返回响应
@admin_blue.route('/news_review_detail',methods = ['GET','POST'])
def news_review_detail():
    #判断请求方式
    if request.method =='GET':
        #1.获取参数
        news_id = request.args.get('news_id')
        #2.参数为空校验
        if not news_id:
            return render_template('/admin1/news_review_detail.html',errmsg='新闻id参数不能为空')
        #3.参数类型转换
        try:
            news_id = int(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return render_template('/amdin1/news_review_detail.html',errmsg = '参数类型转换失败')
        #4.查询新闻
        try:
            # news = News.query.filter(News.id==news_id).first()
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return render_template('/admin1/news_review_detail.html',errmsg= '新闻查询失败')
        #判断新闻是否存在
        if not news:
            return render_template('/admin1/news_review_detail.html',errmsg = '新闻不存在')
        return render_template('/admin1/news_review_detail.html',news = news.to_dict())
    else:
        #1.获取参数
        news_id = request.json.get('news_id')
        action = request.json.get('action')
        #2.参数为空校验
        if not all([news_id,action]):
            return jsonify(errno = RET.PARAMERR,errmsg = '参数不能为空')
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno = RET.DBERR,errmsg = '新闻查询失败')
        #判断新闻是否存在
        if not news:
            return jsonify(errno = RET.NODATA,errmsg = '新闻不存在')
        #判断操作方式是否正确
        if not action in ['accept','reject']:
            return jsonify(errno = RET.PARAMERR,errmsg = '操作类型有误')
        #如果操作方式为通过
        if action == 'accept':
            #将新闻审核状态赋值为0  即通过
            try:
                news.status = 0
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno = RET.DBERR,errmsg = '数据库修改失败')
        #如果操作方式为未通过
        else:
            try:
                #将新闻状态赋值为-1  即未通过
                news.status = -1
                news.reason = request.json.get('reason','')
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno = RET.DBERR,errmsg = '数据库修改失败')
        #返回响应
        return jsonify(errno = RET.OK,errmsg = '操作成功')
#1.请求路径   /admin1/news_review
#2.请求方式 get   post
#3.请求参数  post  p
#4.返回响应
@admin_blue.route('/news_review',methods=['GET','POST'])
def news_review():
    #1.获取参数
    p = request.args.get('p','1')
    keywords = request.args.get('keywords')
    #2.参数类型转换
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        return render_template('/admin1/news_review.html',errmsg = '参数类型转换失败')
    #3.分页查询
    try:
        #定义筛选列表
        filter = [News.status!=0]
        #判断keywords是否有值
        if keywords:
            filter.append(News.title.contains(keywords))
        paginate = News.query.filter(*filter).order_by(News.create_time.desc()).paginate(p,9,False)
    except Exception as e:
        current_app.logger.error(e)
        return render_template('/admin1/news_review.html',errmsg = '分页查询失败')
    if not paginate:
        return render_template('/admin1/news_review.html',errmsg = '分页查询为空')
    #4.获取分页查询内容
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items
    #5.将分页对象转换成字典
    news_list = []
    for news in items:
        news_list.append(news.to_review_dict())
    data = {
        'totalPage':totalPage,
        'currentPage':currentPage,
        'news_list':news_list
    }
    return render_template('/admin1/news_review.html',data = data)
#1.请求路径 /admimn1/user_list
#2.请求方式  get  post
#3.请求参数   post p
#4.返回响应   errno errmsg
@admin_blue.route('/user_list',methods=['GET','POST'])
def user_list():
    #1.获取参数
    p = request.args.get('p','1')
    #2.参数类型转换
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        return render_template('/admin1/uer_list.html',errsg = '参数类型转换失败')
    #4.如果是，进行分页查询
    try:
        paginate = User.query.filter(User.is_admin ==False).paginate(p,9,False)
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin1/user_list.html',errmsg = '分页查询失败')
    #5.判断分页内容是否存在
    if not paginate:
        return render_template('admin1/user_list.html',errmsg='分页查询内容为空')
    #6.获取分页查询对象
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items
    #7.将查询出来的用户转换为字典对象
    user_list = []
    for user in items:
        user_list.append(user.to_admin_dict())
    data = {
        'totalPage':totalPage,
        'currentPage':currentPage,
        'user_list':user_list
    }
    return render_template('admin1/user_list.html',data = data)
@admin_blue.route('/user_count')
def user_count():
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)
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