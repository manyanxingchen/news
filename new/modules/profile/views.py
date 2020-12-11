#导入蓝图
from flask import render_template, redirect, g, request, jsonify

from . import profile_blue
from ...utils.commons import user_login_data


from ...utils.response_code import RET
#对用户基本资料页面进行渲染
# 请求方式  post、get
# 请求路径  /user/base_info.html
# 请求参数  post请求参数  signature  nick_name  gender
# 请求响应  errno errmsg
@profile_blue.route('/base_info',methods = ['GET','POST'])
@user_login_data
def base_info():
    #1.判断请求类型
    if request.method == 'GET':
        #2.如果是get请求携带数据渲染页面
        return render_template('new1/user_base_info.html',user_info = g.user.to_dict())
    #3.如果是post请求进行获取参数
    signature = request.json.get('signature')
    nick_name = request.json.get('nick_name')
    gender = request.json.get('gender')
    #4.参数为空校验
    if not all([signature,nick_name,gender]):
        return jsonify(errno = RET.NODATA,errmsg = '参数不能为空')
    #5.性别判断
    if not gender in ['WOMAN','MAN']:
        return jsonify(errno = RET.PARAMERR,errmsg = '性别参数错误')
    #5.数据库内容修改
    g.user.nick_name = nick_name
    g.user.signature = signature
    g.user.gender = gender
    #6.返回响应
    return jsonify(errno = RET.OK,errmsg = '基本资料修改成功')
#对用户基本资料页面进行渲染
# 请求方式  post、get
# 请求路径  /user/base_info.html
# 请求参数  post请求参数  signature  nick_name  gender
# 请求响应  errno errmsg
@profile_blue.route('/pic_info',methods = ['GET','POST'])
@user_login_data
def pic_info():
    #1.判断请求方式
    if request.method =='GET':
        #2.get请求携带用户信息渲染页面
        return render_template('new1/user_pic_info.html',user_info = g.user.to_dict())
    #3.post请求 获取参数
    #4.校验参数
    #5.修改数据库
    #6.返回响应
    return
@profile_blue.route('/user_index')
@user_login_data
def user_index():
    if not g.user:
        return redirect('/')
    data = {
        'user_info' : g.user.to_dict()
    }
    return render_template('new1/user.html',data = data)