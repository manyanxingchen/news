from qiniu import Auth, put_file, etag, put_data
import qiniu.config

#需要填写你的 Access Key 和 Secret Key
access_key = 'W8zBe5cmcooljjl2Q96h_w9k1qc_YCyiphfri9js'
secret_key = 'OaTvFnefba7ZDmveldccvjfL5OMj7FPUhhdWhpji'
#为了方便使用将其封装成一个对象以便调用
def image_storage(image_data):
    #构建鉴权对象
    q = Auth(access_key, secret_key)

    #要上传的空间
    bucket_name = 'manyanxingchen'

    #上传后保存的文件名
    # key = 'flower.png'
    #一般不设置名字
    key = None
    #生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)

    #要上传文件的本地路径
    # localfile = './test.jpg'

    ret, info = put_data(token, key, image_data)
    #判断上传成功返回信息
    if info.status_code == 200:
        return ret.get("key")
    # assert ret['key'] == key
    # assert ret['hash'] == etag(localfile)
    else:
        return None
#测试调用
if __name__ == '__main__':
    #将图片转换成二进制码进行存储
    with open('./test.jpg','rb') as f:
        image_storage(f.read())