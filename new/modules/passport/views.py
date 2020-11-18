#导入蓝图
from new.modules.passport import passport_blue
#创建蓝图视图函数
from new.utils.captcha.captcha import captcha

#定义验证图片试图函数
@passport_blue.route('/image_code')
def image_code():
    #调用generate_captcha()获取图片验证码的编号、值、图片
    name,text,image_data=captcha.generate_captcha()
    return image_data