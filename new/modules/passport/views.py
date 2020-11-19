#导入蓝图

from flask import request, current_app, make_response, jsonify
from new import redis_store, constants
from new.modules.passport import passport_blue
import json
import re
from new.libs.yuntongxun.sms import CCP
#创建蓝图视图函数
from new.utils.captcha.captcha import captcha
# 获取短信验证码
# 请求路径  passport/sms_code
# 请求方式  post
# 请求参数  电话号码   图片验证码   随机编码
# 返回值  errno errmsg
@passport_blue.route('/sms_code',methods=['POST'])
def sms_code():
    #取出参数
    json_data = request.data
    dict_data = json.loads(json_data)
    mobile = dict_data.get('mobile')
    image_code = dict_data.get('image_code')
    image_code_id = dict_data.get('image_code_id')
    # 校验参数，图片验证码
    #依据图片验证码的随机编码取出redis中的image_code图片验证码
    redis_image_code = redis_store.get('image_code:%s'%image_code_id)
    if image_code !=redis_image_code:
        return jsonify(errno = 10000,errmsg ='图片验证码错误')
    #依据正则表达式校验电话号码的格式
    if not re.match('1[3-9]\d{9}',mobile):
        return jsonify(errno = 20000,errmsg = '电话号码格式错误')
    #发送短信，调用封装好的app
    ccp = CCP()
    result = ccp.send_template_sms('19852058578', ['888888', 5], 1)
    if result == -1:
        return jsonify(errno = 30000,errmsg = '短信发送失败')
    #返回发送的状态
    return jsonify(errno = 40000,errmsg = '短信发送成功')
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