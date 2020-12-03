#导入蓝图
from flask import current_app, jsonify, abort, render_template, session, g, request

from . import news_blue
from ... import db
from ...models import News, User, Comment
from ...utils.commons import user_login_data
from ...utils.response_code import RET
#用户评论
#1.请求路径：/news/comment
#2.请求方式：post
#3.请求参数  news_id  parent_id  user_id   content
#4.返回值   errno errmsg 评论的字典需要在前端显示
@news_blue.route('/news_comment',methods = ['POST'])
@user_login_data
def comment():
    #1.判断用户是否登录
    if not g.user:
        return jsonify(errno = RET.NODATA,errmsg = '用户没有登录')
    #2.获取参数
    news_id = request.json.get('news_id')
    content = request.json.get('comment')
    parent_id = request.json.get('parent_id')
    #3.参数为空校验
    if not all([news_id,content]):
        return jsonify(errno = RET.NODATA,errmsg = '评论请求数据获取失败')
    #4.依据参数取出新闻，判断新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.NODATA,errmsg ='新闻获取失败')
    if not news: return jsonify(errno = RET.NODATA,errmsg = '该新闻不存在')
    #5.创建评论对象
    comment = Comment()
    #6.给评论对象赋值
    comment.user_id = g.user.id
    comment.news_id = news_id
    comment.content = content
    if parent_id:
        comment.parent_id = parent_id
    #7.保存到数据库
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR,errmsg = '新闻评论失败')
    #8.返回响应
    return jsonify(errno = RET.OK,errmsg = '评论成功',data = comment.to_dict())
#用户收藏、取消收藏
# 1.请求路径：/news/news_collect
# 2.请求方式  post/get
# 3.请求参数  news_id ,action,g.user
# 4.返回值 errno errmsg
@news_blue.route('/news_collect',methods=['GET','POST'])
@user_login_data
def news_collect():
    #1.判断用户是否登录
    if not g.user:
        return jsonify(errno = RET.LOGINERR,errmsg = '用户还没有登录')
    #2.获取参数
    news_id = request.json.get('news_id')
    action = request.json.get('action')
    #3.参数为空校验
    if not all([news_id,action]):
        return jsonify(errno = RET.PARAMERR,errmsg = '参数传递错误，参数不能为空')
    #4.action参数校验，是否在[collect,cancel_collect]
    if not action in ['collect','cancel_collect']:
        return jsonify(errno = RET.PARAMERR,errmsg = '收藏参数传递错误')
    #5.依据新闻id取出新闻
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR,errmsg = '获取新闻数据失败')
    #6.判断新闻是否在用户收藏列表
    try:
        if action == 'collect':
            if not news in g.user.collection_news:
                g.user.collection_news.append(news)
        else:
            g.user.collection_news.remove(news)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR,errmsg = '惭怍失败')
    #7.返回响应
    return jsonify(errno = RET.OK,errmsg = '操作成功')
@news_blue.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    #从session中获取用户id
    #使用g对象
    # user_id  = session.get('user_id')
    # user = None
    # #从数据库中搜索用户
    # if user_id:
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)
    #         return jsonify(error = RET.DBERR,errmsg = '用户获取失败')
    #依据前台传送的id获取新闻
    try:
        news =  News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error =RET.DBERR,errmsg = '获取新闻失败')
    #判断news是否为空
    if not news:
        abort(404)
    #  新闻详情页的热门新闻
    try:
        click_news = News.query.order_by(News.clicks.desc()).limit(6).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR,errmsg = '新闻详情页热门新闻获取失败')
    #将获取的新闻字符串类型转换为列表类型
    click_news_list = []
    for new in click_news:
        click_news_list.append(new.to_dict())
    #判断新闻是否被用户收藏
    # is_collected = False
    # if g.user:
    #     if news in g.user.collection_news:
    #         is_collected =True
    #将新闻转换为字典类型
    #显示评论数据
    #1.查询评论数据
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR,errmsg = '新闻评论数据获取失败')
    comments_list= []
    for comment in comments:
        comments_list.append(comment.to_dict())
    data = {
        'news_info':news.to_dict(),
        #返回用户数据
        'user_info':g.user.to_dict() if g.user else '',
        #返回详情页热点新闻
        'news_list':click_news_list,
        'comments':comments_list
    }
    return render_template('new1/detail.html',data = data)

