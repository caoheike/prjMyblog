'''
    用户配置页
'''

# web登录和会话配置信息
user = 'weizai'
pwd = 'a929171a502b9127c2552e1d650b7980' # 明文密码 tdragon6 的md5

# jwt加密盐
global_salt = 'weizai' # 必须修改，不然可以伪造jwt token直接登录

# 会话保持时间，单位：小时
expire = 48


# 共享远控shell的共享密码
share_pwd = 'a929171a502b9127c2552e1d650b7980' # 明文密码 tdragon6 的md5

# 共享shell会话保持时间，单位：小时
share_expire = 24
