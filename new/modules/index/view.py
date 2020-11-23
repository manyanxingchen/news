#from new.modules.index import index_blue
from sqlalchemy import text

from . import index_blue  #点表示的是当前的路径下
from flask import current_app, render_template, session, jsonify, request

#定义蓝图路由
from ...models import User, News, Category
from ...utils.response_code import RET
#首页分页显示新闻列表
# 请求路径  /newlist
# 请求方式  get
# 请求参数  分类   第几页   每一页显示的对象
# 返回值  errno errmsg
@index_blue.route('/newslist',methods=['GET'])
def newlist():
    #1.获取参数
    cid = request.args.get('cid','1')
    page = request.args.get('page','1')
    per_page = request.args.get('per_page','10')
    #2.转换参数格式（获取的参数类型为字符型，分页查询中的函数需要整型参数）
    try:
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        page = 1
        per_page = 10

    #3.分页查询
    try:
        if cid == '1':
            paginate = News.query.filter().order_by(News.create_time.desc()).paginate(page,per_page,False)
        else:
            paginate = News.query.filter(News.category_id==cid).order_by(News.create_time.desc()).paginate(page,per_page,False)
        # """
        #方式2.
        # filters = text(" ")
        # if cid != "1":
        #     filters = (News.category_id == cid)
        # paginate = News.query.filter(filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
        # 方式3.
        # filters = []
        # if cid != "1":
        #     filters.append(News.category_id == cid)
        # paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR,errmsg = '分页新闻获取失败')
    #4.获取到分页对象的属性:当前页，总页数，当前页的对象列表
    total_pages = paginate.pages
    current_page = paginate.page
    items = paginate.items
    #5.将对象列表转换为字典列表
    news_list = []
    for item in items:
        news_list.append(item.to_dict())
    #6.携带数据，返回响应
    return jsonify(errno = RET.OK,errmsg = '分页信息获取成功',totalPage=total_pages,currentPage=current_page,newsList=news_list)
@index_blue.route('/',methods=['GET','POST'])
#定义视图函数
def index():
    #分类列表显示
    #1.查询分类列表
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR,errmsg = '获取分类列表失败')
    #将数据转换为列表数据
    category_list = []
    for category in categories:
        category_list.append(category.to_dict())

    # 热门新闻显示
    # 1.查询10条热门新闻
    try:
        news = News.query.order_by(News.clicks.desc()).limit(10).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg='热门新闻查询失败')
    # 将news新闻的格式转换为列表
    news_list = []
    for new in news:
        news_list.append(new.to_dict())
    #1.获取到用户登录信息
    user_id = session.get('user_id')
    #2.依据用户id查询用户信息
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    #3.拼接用户数据，渲染页面
    data = {
            #如果有值返回左边，否则返回右边
        'user_info':user.to_dict() if user else '',
        'news_list':news_list,
        'category_list':category_list
    }
    return render_template('new1/index.html',data =data)
    # redis_store.set("name","zhangsan")
    # print(redis_store.get("name"))
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

#处理网站logo
@index_blue.route('/favicon.ico')
def get_web_logo():
    return current_app.send_static_file('news/favicon.ico')