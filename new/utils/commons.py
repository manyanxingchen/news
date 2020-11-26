#创建热门新闻的过滤器
from flask import session, current_app, g
from functools import wraps

def hot_news_filter(index):
    if index == 1:
        return 'first'
    elif index == 2:
        return 'second'
    elif index == 3:
        return 'third'
    else:
        return ''

#自定义登录窗口装饰函数
def user_login_data(view_func):
    @wraps(view_func)
    def wrapper(*args,**kwargs):
        # 1.获取到用户登录信息
        user_id = session.get('user_id')
        # 2.依据用户id查询用户信息
        user = None
        if user_id:
            try:
                from new.models import User
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        #3.将user数据封装到g对象
        g.user = user
        return view_func(*args,**kwargs)
    return wrapper