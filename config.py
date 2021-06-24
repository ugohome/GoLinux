# -*- coding:utf-8 -*-

'''
Session, Cookies以及一些第三方扩展都会用到SECRET_KEY值,否则报错,应该生成随机值,简单方法如下:
import os
os.urandom(24)
'''
SECRET_KEY = '\xd5\x00\xad\xdc\x0fP\xaeT\xec\xd7\x17J\xb5?\xfd\xcc\xa4?0\xcc\xbde\x0f\xdc'
#使用本地的Bootstrap资源,解决Flask-Bootstrap CDN访问http://cdnjs.cloudflare.com资源速度很慢问题.
BOOTSTRAP_SERVE_LOCAL = True

#flask_dropzone配置
DROPZONE_DEFAULT_MESSAGE = '请将更新包拖放到这里上传!'
#要先允许用户自定义文件类型,下一条才能进行文件类型定义,否则报错.
DROPZONE_ALLOWED_FILE_CUSTOM = True
DROPZONE_ALLOWED_FILE_TYPE = '.gz, .sh, .zip, .sql, .dat'
DROPZONE_INVALID_FILE_TYPE = '该类型文件不允许上传!'
DROPZONE_BROWSER_UNSUPPORTED = '当前浏览器不支持,请使用谷歌或火狐内核浏览器.'
DROPZONE_MAX_FILE_SIZE = 2048
DROPZONE_FILE_TOO_BIG = '文件{{filesize}}M,超出限制: {{maxFilesize}}M.'
DROPZONE_TIMEOUT = 1200000       #连接超时,默认30000毫秒 (30 秒)
DROPZONE_CANCEL_UPLOAD = '取消上传'
DROPZONE_REMOVE_FILE = '删除'
DROPZONE_CANCEL_CONFIRMATION = '确定取消!'
DROPZONE_UPLOAD_CANCELED = '确定取消!'
#以下配置造成无法正常上传,问题待查
#DROPZONE_UPLOAD_MULTIPLE = True  #是否允许一次请求发送多个文件,默认False,允许同时上传2个文件
#DROPZONE_PARALLEL_UPLOADS = 5    #DROPZONE_UPLOAD_MULTIPLE = True时,可更改一次同时上传数量.