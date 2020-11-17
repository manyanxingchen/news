import logging
from datetime import timedelta
from redis import StrictRedis
from datetime import timedelta
class Config(object):
    #flask应用程序调试
    DEBUG = True
    #session加密配置
    SECRET_KEY = 'JALSJDFLKAJSLK'
    #数据库配置信息
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:3306/news'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #redis配置信息
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = '6379'
    #session配置信息
    SESSION_TYPE = 'redis'  #设定session的存储类型
    SESSION_REDIS = StrictRedis(host=REDIS_HOST,port=REDIS_PORT)  #指定session存储的redis服务器
    SESSION_USE_SIGNER = True  #设置签名存储
    PERMANENT_SESSION_LIFETIME = timedelta(days=2)  #设置session有效期  秒使用seconds
    LEVEL_NAME =logging.DEBUG
#开发环境配置信息
class DevelopConfig(Config):
    pass

#生产（线上）环境配置信息
class ProductConfig(Config):
    LEVEL_NAME = logging.ERROR
#测试环境配置信息
class TestConfig(Config):
    pass

#给外界提供一个统一的访问接口
config_dict={
    'develop':DevelopConfig,
    'product':ProductConfig,
    'test':TestConfig
}