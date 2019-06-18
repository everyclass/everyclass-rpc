from everyclass.rpc.consts import Error

# 4XX 开头为用户发出请求错误
# 注册相关
E_EMPTY_USERNAME = Error(4001, "Empty username")  # 用户名为空
E_EMPTY_PASSWORD = Error(4002, "Empty password")  # 密码空
E_INVALID_CAPTCHA = Error(4003, "Invalid captcha")  # 验证码验证未通过
E_STUDENT_UNEXIST = Error(4004, "Student not exist")  # 学号不存在
E_STUDENT_NOT_REGISTERED = Error(4005, "Student not registered")  # 此学生未注册
E_WRONG_PASSWORD = Error(4006, "Wrong password")  # 密码错误
E_ALREADY_REGISTERED = Error(4007, "Already registered")  # 已经注册过了，不要重复注册
E_EMPTY_TOKEN = Error(4008, "Empty token")  # 邮件 token 验证没有传递 token
E_INVALID_TOKEN = Error(4009, "Invalid token")  # 邮件 token 无效
E_WEAK_PASSWORD = Error(4010, "Weak password")  # 密码强度过弱
E_EMPTY_REQUEST_ID = Error(4011, "Empty request ID")  # 请求 ID 为空

# 用户面板相关
E_INVALID_REQUEST = Error(4100, "Invalid request")  # 无效请求
E_INVALID_PRIVACY_LEVEL = Error(4101, "Invalid preference value")  # 无效的隐私等级
E_LOGIN_REQUIRED = Error(4102, "Login required")  # 需要登录

E_PWD_VER_SUCCESS = Error(4200, "Success")  # 密码验证：成功
E_PWD_VER_NEXT = Error(4201, "Next time")  # 密码验证：下次查询
E_PWD_VER_WRONG = Error(4202, "Wrong password")  # 密码验证：密码错误


# 5XX 开头为服务器内部错误
E_BE_INTERNAL = Error(4501, "Backend internal error")  # 上游服务错误
