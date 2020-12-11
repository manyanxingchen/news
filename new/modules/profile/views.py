#导入蓝图
from flask import render_template, redirect, g

from . import profile_blue
from ...utils.commons import user_login_data


@profile_blue.route('/user_index')
@user_login_data
def user_index():
    if not g.user:
        return redirect('/')
    data = {
        'user_info' : g.user.to_dict()
    }
    return render_template('new1/user.html',data = data)