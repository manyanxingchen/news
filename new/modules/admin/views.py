#导入蓝图
from flask import render_template

from . import admin_blue

@admin_blue.route('/login')
def admin_login():
    return render_template('/admin1/login.html')