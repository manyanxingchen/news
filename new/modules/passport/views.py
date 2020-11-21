#导入蓝图
import random
from datetime import datetime

from flask import request, current_app, make_response, jsonify, session
from new import redis_store, constants, db
from new.models import User
from new.modules.passport import passport_blue
import json
import re
from new.libs.yuntongxun.sms import CCP
from new.utils.captcha.captcha import captcha
from new.utils.response_code import RET
#创建蓝图视图函数
@passport_blue.route('/logout',methods=['POST'])
def logout():
    #1.清空session
    session.pop('user_id',None)
    #2.返回响应
    return jsonify(errno = RET.OK,errmsg = '退出成功')
#登录验证
#创建蓝图视图函数
# 获取注册信息
# 请求路径  passport/login
# 请求方式  post
# 请求参数  电话号码    密码
# 返回值  errno errmsg
@passport_blue.route('/login',methods=['POST'])
def login():

#1.获取参数
    mobile = request.json.get('mobile')
    password = request.json.get('password')
#2.判断参数是否为空
    if not all([mobile,password]):
        return jsonify(errno = RET.NODATA,errmsg = '参数为空')
#3.依据手机号在数据库中查询
    try:
        user = User.query.filter(User.mobile ==mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR,errmsg = '获取用户失败')
#4.判断用户是否存在
    if not user:
        return jsonify(errno = RET.NODATA,errmsg = '该用户还未注册')
#5.判断密码是否正确
    if not user.check_password(password):
        return jsonify(errno = RET.PARAMERR,errmsg = '密码错误')
#6.将用户信息存放到session中
    session['user_id'] = user.id
#6.1记录用户最后登录时间
    user.last_login = datetime.now()
    # try:
    #     db.session.commit()
    # except Exception as e:
    #     current_app.logger.error(e)
#7.返回信息
    return jsonify(errno = RET.OK,errmsg = '登陆成功')
@passport_blue.route('/register',methods=['POST'])
def register():
#创建蓝图视图函数
# 获取注册信息
# 请求路径  passport/register
# 请求方式  post
# 请求参数  电话号码   短信验证码   密码
# 返回值  errno errmsg
#注册验证流程
#1.获取前端传送参数
    # json_data = request.data
    # #将json数据转换为字典
    # dict_data = json.laods(json_data)
    dict_data = request.get_json()
    mobile = dict_data.get('mobile')
    sms_code = dict_data.get('sms_code')
    password = dict_data.get('password')
#2.校验参数是否为空
    if not all([mobile,sms_code,password]):
        return jsonify(errno = RET.PARAMERR,errmsg = '参数为空')
#3.取出redis短信验证码
    try:
        redis_sms_code = redis_store.get('sms_code:%s'%mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DATAERR,errmsg = 'redis短信验证码获取失败')
#4.判断短信验证码是否过期
    if not redis_sms_code:
        return jsonify(errno = RET.NODATA,errmsg = '短信验证码已过期')
#5.判断验证码是否正确
    if redis_sms_code!=sms_code:
        return jsonify(errno = RET.DATAERR,errmsg = '验证码错误')
#6.删除redis中的短信验证码
    try:
        redis_store.delete('sms_code:%s'%mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR,errmsg = '删除短信验证码失败')
#7.创建用户
    user = User()

#8.设置用户对象属性
    user.nick_name = mobile
    user.password= password
    user.mobile = mobile
    user.signature = '这个用户很懒，没有签名'
#9.保存用户到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR,errmsg = '用户注册失败')
#10.返回注册成功
    return jsonify(errno =RET.OK,errmsg = '注册成功')
# 获取短信验证码
# 请求路径  passport/sms_code
# 请求方式  post
# 请求参数  电话号码   图片验证码   随机编码
# 返回值  errno errmsg
@passport_blue.route('/sms_code',methods=['POST'])
def sms_code():
    #1.获取参数
    # json_data = request.data
    # dict_data = json.loads(json_data)
    #上两行代码可以转换为
    #dict_data = request.json  #或者是
    dict_data = request.get_json()
    print(222222)
    mobile = dict_data.get('mobile')
    image_code = dict_data.get('image_code')
    image_code_id = dict_data.get('image_code_id')
    #2.参数的为空校验
    if not all([mobile,image_code,image_code_id]):
        return jsonify(errno = RET.PARAMERR ,errmsg='参数为空')
    #3.检验手机格式
    if not re.match('1[3-9]\d{9}',mobile):
        return jsonify(errno = RET.DATAERR,errmsg = '电话号码格式错误')
    #4.依据图片验证码编号获取图片验证码
    try:
        redis_image_code = redis_store.get('image_code:%s'%image_code_id)
    except Exception as e:
        current_app.logger.error(e)
    #5.判断图片验证码是否过期
    if not redis_image_code:
        return jsonify(errno = RET.NODATA,errmsg = '图片验证码已过期')
    #6.校验图片验证码
    if image_code.upper() !=redis_image_code.upper():
        return jsonify(errno = RET.DATAERR,errmsg = '图片验证码错误')
    #7.删除redis中的图片验证码
    try:
        redis_store.delete('image_code:%s'%image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR,errmsg = '删除redis失败')
    #8.生成一个短信验证码，调用ccp
    sms_code = '%06d'%random.randint(0,999999)
    ccp = CCP()
    result =  ccp.send_template_sms(mobile,[sms_code,constants.SMS_CODE_REDIS_EXPIRES/60],1)
    if result == -1:
        return jsonify(errno = RET.DATAERR,errmsg = '短信发送失败')
    #9.将短信验证码保存到redis中
    try:
        redis_store.set('sms_code:%s'%mobile,sms_code,constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR,errmsg = '短信验证码存储失败')
    #10.返回发送成功
    return jsonify(errno = RET.OK,errmsg = '短信验证码发送成功')
    # #取出参数
    # json_data = request.data
    # dict_data = json.loads(json_data)
    # mobile = dict_data.get('mobile')
    # image_code = dict_data.get('image_code')
    # image_code_id = dict_data.get('image_code_id')
    # # 校验参数，图片验证码
    # #依据图片验证码的随机编码取出redis中的image_code图片验证码
    # redis_image_code = redis_store.get('image_code:%s'%image_code_id)
    # if image_code !=redis_image_code:
    #     return jsonify(errno = 10000,errmsg ='图片验证码错误')
    # #依据正则表达式校验电话号码的格式
    # if not re.match('1[3-9]\d{9}',mobile):
    #     return jsonify(errno = 20000,errmsg = '电话号码格式错误')
    # #发送短信，调用封装好的app
    # ccp = CCP()
    # result = ccp.send_template_sms('19852058578', ['888888', 5], 1)
    # if result == -1:
    #     return jsonify(errno = 30000,errmsg = '短信发送失败')
    # #返回发送的状态
    # return jsonify(errno = 40000,errmsg = '短信发送成功')
#定义验证图片试图函数
@passport_blue.route('/image_code')
def image_code():
    # 1.获取从前端传送过来的图片验证码参数    args获取查询参数
    cur_id = request.args.get('cur_id')
    pre_id = request.args.get('pre_id')
    #2.调用generate_captcha()获取图片验证码的编号、值、图片
    name,text,image_data=captcha.generate_captcha()
    # 3.将图片验证码参数存储到redis
    #1.参数1：key   参数2：value    参数3：有效期
    try:   #做异常处理
        redis_store.set('image_code:%s'%cur_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
        if pre_id:
            redis_store.delete('image_code:%s'%pre_id)
    except Exception as e:
        current_app.logger.error(e)
        return '图片验证码操作失败'
    #4.返回图片
    response = make_response(image_data)
    response.headers['Content-Type'] = 'image/png'
    return response