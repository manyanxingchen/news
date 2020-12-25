#导入蓝图
from flask import current_app, jsonify, abort, render_template, session, g, request

from . import news_blue
from ... import db
from ...models import News, User, Comment, CommentLike
from ...utils.commons import user_login_data
from ...utils.response_code import RET
#用户点赞、取消点赞
# 1.请求路径：/news/comment_like
# 2.请求方式  post/get
# 3.请求参数  comment_id ,action,g.user
# 4.返回值 errno errmsg
@news_blue.route('/comment_like',methods = ['POST'])
@user_login_data
def comment_like():
    #1.判断用户是否登录
    if not g.user:
        return jsonify(errno = RET.NODATA,errmsg = '用户还未登录')
    #2.获取参数
    comment_id = request.json.get('comment_id')
    action = request.json.get('action')
    #3.判断参数是否为空
    if not all([comment_id,action]):
        return jsonify(errno = RET.PARAMERR,errmsg = '参数不能为空')
    #4.点赞参数类型校验
    if not action in ['add','remove']:
        return jsonify(errno = RET.DATAERR,errmsg = '参数错误')
    #5.依据评论编号查询评论对象，判断评论是否存在
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR,errmsg = '评论获取失败')
    #5.判断评论是否存在
    if not comment: return jsonify(errno = RET.NODATA,errmsg = '该评论不存在')
    #6.判断用户操作类型：点赞、取消点赞
    try:
        if action=='add':
        # 判断是否点过赞
            comment_like = CommentLike.query.filter(CommentLike.comment_id == comment_id,CommentLike.user_id == g.user.id).first()
            if not comment_like:
                #创建点赞对象
                comment_like = CommentLike()
                comment_like.comment_id = comment_id
                comment_like.user_id = g.user.id
                #添加到数据库
                db.session.add(comment_like)
                comment.like_count +=1
                db.session.commit()
            else:
                return jsonify(errno=RET.PARAMERR, errmsg='该评论您已点过赞')
        else:
                # 判断是否点过赞
            comment_like = CommentLike.query.filter(CommentLike.comment_id == comment_id,
                                                        CommentLike.user_id == g.user.id).first()
            if comment_like:
                    #取消点赞
                db.session.delete(comment_like)
                if comment.like_count > 0:
                    comment.like_count -= 1
                db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR,errmsg = '操作失败')
    #7.返回响应
    return jsonify(errno = RET.OK,errmsg = '操作成功')
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
#关注或者取消关注
#1.请求路径  news/news_followed
#2.请求方式   post
#3.请求参数   操作方式  作者
#4.返回响应    errno errmsg
@news_blue.route('/followed_user',methods = ['POST'])
@user_login_data
def followed_user():
    #校验是否登录
    if not g.user:
        return jsonify(errno = RET.SESSIONERR,errmsg = '用户未登录')
    #1.获取参数
    author_id = request.json.get('user_id')
    action = request.json.get('action')
    #2.参数校验为空
    if not all([action,author_id]):
        return jsonify(errno = RET.NODATA,errmsg = '参数不能为空')
    #3.判断参数是否正确
    if not action in ['follow','unfollow']:
        return jsonify(errno = RET.DATAERR,errmsg = '参数错误')
    #4.判断作者是否存在
    try:
        author = User.query.get(author_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR,errmsg = '作者查询失败')
    if not author:
        return jsonify(errno = RET.NODATA,errmsg = '作者不存在')
    #5.如果是关注：判断用户是否在作者粉丝中
    try:
        if action == 'follow':
            if not g.user in author.followers:
                author.followers.append(g.user)
        #6.如果是取消关注
        else:
            author.followers.remove(g.user)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR,errmsg = '操作失败')
    #7.返回响应
    return jsonify(errno = RET.OK, errmsg = '操作成功')
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
    is_collected = False
    if g.user:
        if news in g.user.collection_news:
            is_collected =True
    #将新闻转换为字典类型
    #显示评论数据
    #获取用户点赞信息
    #判断用户是否登录
    commnent_likes = []
    try:
        if g.user:
            #依据用户id取出与用户id相关的信息
            commnent_likes = CommentLike.query.filter(g.user.id == CommentLike.user_id).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR,errmsg = '点赞获取失败')
    #取出点赞的新闻id列表
    user_comment_likes_list = []
    for comment_like in commnent_likes:
        user_comment_likes_list.append(comment_like.comment_id)
    #1.查询评论数据
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR,errmsg = '新闻评论数据获取失败')
    comments_list= []
    for comment in comments:
        comms_dict =  comment.to_dict()
        # 判断用户是否对评论点过赞
        comms_dict['is_like'] = False
        if g.user and comment.id in user_comment_likes_list:
            comms_dict['is_like'] = True
        comments_list.append(comms_dict)
    is_followers = False
    #用户关注
    if g.user and news.user:
        if g.user in news.user.followers:
            is_followers = True
    data = {
        'news_info':news.to_dict(),
        #返回用户数据
        'user_info':g.user.to_dict() if g.user else '',
        #返回详情页热点新闻
        'news_list':click_news_list,
        'comments':comments_list,
        'is_followers':is_followers,
        'is_collected':is_collected
    }
    return render_template('new1/detail.html',data = data)

