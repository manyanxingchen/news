#导入蓝图
from flask import request, current_app, make_response

from new import redis_store, constants
from new.modules.passport import passport_blue
#创建蓝图视图函数
from new.utils.captcha.captcha import captcha

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