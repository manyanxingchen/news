#导入蓝图
from flask import current_app, jsonify, abort, render_template, session

from . import news_blue
from ...models import News, User
from ...utils.response_code import RET


@news_blue.route('/<int:news_id>')
def news_detail(news_id):
    #从session中获取用户id
    user_id  = session.get('user_id')
    user = None
    #从数据库中搜索用户
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(error = RET.DBERR,errmsg = '用户获取失败')
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
    #将新闻转换为字典类型
    data = {
        'news_info':news.to_dict(),
        #返回用户数据
        'user_info':user.to_dict() if user else '',
        'news_list':click_news_list
    }
    return render_template('new1/detail.html',data = data)

